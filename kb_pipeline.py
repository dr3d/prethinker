#!/usr/bin/env python3
"""
Build and validate runtime KBs from natural-language utterances via:
1) local 9B semantic parsing (LM Studio or Ollama)
2) deterministic runtime apply tools (local core interpreter by default; optional parse-only or MCP mode)

Designed to run standalone in this repo without sibling-repo requirements.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from engine.core import Clause, PrologEngine, Term

PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_PROLOG_REPO_CANDIDATES = [
    PROJECT_ROOT / "vendor" / "prolog-reasoning",
    PROJECT_ROOT / ".runtime" / "prolog-reasoning",
    PROJECT_ROOT / "prolog-reasoning",
]
DEFAULT_BACKEND = "ollama"
DEFAULT_KB_ROOT = Path("kb_store")
DEFAULT_KB_NAME = "default"
DEFAULT_PREDICATE_REGISTRY = Path("modelfiles/predicate_registry.json")
DEFAULT_PROMPT_HISTORY_DIR = Path("modelfiles/history/prompts")
DEFAULT_BASE_URLS = {
    "lmstudio": "http://127.0.0.1:1234",
    "ollama": "http://127.0.0.1:11434",
}
DEFAULT_MODELS = {
    "lmstudio": "qwen/qwen3.5-9b",
    "ollama": "qwen3.5:9b",
}


@dataclass
class ModelResponse:
    message: str
    reasoning: str
    raw: dict[str, Any]


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key and key not in os.environ:
            os.environ[key] = value


def _resolve_prolog_repo(cli_value: str) -> Path | None:
    candidates: list[Path] = []
    raw = (cli_value or "").strip()
    if raw:
        p = Path(raw)
        candidates.append(p if p.is_absolute() else (Path.cwd() / p))

    env_value = os.environ.get("PRETHINKER_PROLOG_REPO", "").strip()
    if env_value:
        p = Path(env_value)
        candidates.append(p if p.is_absolute() else (Path.cwd() / p))

    candidates.extend(DEFAULT_PROLOG_REPO_CANDIDATES)
    seen: set[str] = set()
    for candidate in candidates:
        try:
            resolved = candidate.resolve()
        except OSError:
            continue
        key = str(resolved).lower()
        if key in seen:
            continue
        seen.add(key)
        if (resolved / "src" / "mcp_server.py").exists():
            return resolved
    return None


def _resolve_env_file(cli_value: str, prolog_repo: Path | None) -> Path | None:
    raw = (cli_value or "").strip()
    candidates: list[Path] = []
    if raw:
        p = Path(raw)
        candidates.append(p if p.is_absolute() else (Path.cwd() / p))
    else:
        candidates.append(PROJECT_ROOT / ".env.local")
        if prolog_repo is not None:
            candidates.append(prolog_repo / ".env.local")

    seen: set[str] = set()
    for candidate in candidates:
        try:
            resolved = candidate.resolve()
        except OSError:
            continue
        key = str(resolved).lower()
        if key in seen:
            continue
        seen.add(key)
        if resolved.exists():
            return resolved
    return None


def _load_prompt_guide(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8-sig").strip()


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _snapshot_prompt_version(
    *,
    prompt_file_path: Path,
    prompt_text: str,
    history_dir: Path,
) -> dict[str, Any]:
    normalized = prompt_text.strip()
    if not normalized:
        return {
            "status": "missing",
            "prompt_id": "",
            "prompt_sha256": "",
            "source_path": str(prompt_file_path),
            "snapshot_path": "",
            "snapshot_created": False,
            "char_count": 0,
            "line_count": 0,
            "preview": "",
        }

    prompt_sha = _sha256_text(normalized)
    prompt_id = f"sp-{prompt_sha[:12]}"
    history_dir.mkdir(parents=True, exist_ok=True)
    snapshot_path = (history_dir / f"{prompt_id}.md").resolve()
    snapshot_created = False
    if not snapshot_path.exists():
        captured_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        header = (
            f"<!-- prompt_id: {prompt_id} -->\n"
            f"<!-- prompt_sha256: {prompt_sha} -->\n"
            f"<!-- source_path: {prompt_file_path} -->\n"
            f"<!-- captured_at_utc: {captured_at} -->\n\n"
        )
        snapshot_path.write_text(header + normalized + "\n", encoding="utf-8")
        snapshot_created = True

    preview_lines = [line for line in normalized.splitlines() if line.strip()][:8]
    return {
        "status": "ok",
        "prompt_id": prompt_id,
        "prompt_sha256": prompt_sha,
        "source_path": str(prompt_file_path),
        "snapshot_path": str(snapshot_path),
        "snapshot_created": snapshot_created,
        "char_count": len(normalized),
        "line_count": len(normalized.splitlines()),
        "preview": "\n".join(preview_lines),
    }


def _load_predicate_registry(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"canonical_predicates": []}
    try:
        parsed = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError:
        return {"canonical_predicates": []}
    if isinstance(parsed, dict) and isinstance(parsed.get("canonical_predicates"), list):
        return parsed
    return {"canonical_predicates": []}


def _build_registry_alias_map(registry: dict[str, Any]) -> dict[tuple[str, int], str]:
    mapping: dict[tuple[str, int], str] = {}
    rows = registry.get("canonical_predicates", [])
    if not isinstance(rows, list):
        return mapping
    for row in rows:
        if not isinstance(row, dict):
            continue
        name = _atomize(str(row.get("name", "")))
        arity_raw = row.get("arity", 0)
        try:
            arity = int(arity_raw)
        except (TypeError, ValueError):
            continue
        if not name or arity < 0:
            continue
        mapping[(name, arity)] = name
        aliases = row.get("aliases", [])
        if isinstance(aliases, list):
            for alias in aliases:
                alias_name = _atomize(str(alias))
                if alias_name:
                    mapping[(alias_name, arity)] = name
    return mapping


def _align_clause_predicates(
    clause: str,
    alias_map: dict[tuple[str, int], str],
) -> tuple[str, list[dict[str, Any]]]:
    normalized = _normalize_clause(clause)
    aligned = normalized
    events: list[dict[str, Any]] = []

    for signature in _extract_goal_signatures(aligned[:-1] if aligned.endswith(".") else aligned):
        if "/" not in signature:
            continue
        name, arity_text = signature.split("/", 1)
        if name == "retract":
            continue
        try:
            arity = int(arity_text)
        except ValueError:
            continue
        canonical = alias_map.get((_atomize(name), arity))
        if not canonical or canonical == name:
            continue
        pattern = rf"\b{re.escape(name)}\s*\("
        replacement = f"{canonical}("
        next_aligned = re.sub(pattern, replacement, aligned)
        if next_aligned != aligned:
            aligned = next_aligned
            events.append(
                {
                    "from": name,
                    "to": canonical,
                    "arity": arity,
                }
            )
    return aligned, events


def _collect_predicate_names_from_parsed(parsed: dict[str, Any]) -> list[str]:
    names: set[str] = set()
    clauses: list[str] = []
    logic = str(parsed.get("logic_string", "")).strip()
    if logic:
        clauses.append(logic)
    for key in ("facts", "rules", "queries"):
        value = parsed.get(key, [])
        if isinstance(value, list):
            clauses.extend(str(item).strip() for item in value if str(item).strip())
    for clause in clauses:
        for signature in _extract_goal_signatures(clause[:-1] if clause.endswith(".") else clause):
            if "/" not in signature:
                continue
            name = signature.split("/", 1)[0]
            if name != "retract":
                names.add(name)
    return sorted(names)


def _align_parsed_predicates(
    parsed: dict[str, Any],
    alias_map: dict[tuple[str, int], str],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if not alias_map:
        return parsed, []
    aligned = json.loads(json.dumps(parsed))
    events: list[dict[str, Any]] = []

    logic_string = str(aligned.get("logic_string", "")).strip()
    if logic_string:
        aligned_logic, logic_events = _align_clause_predicates(logic_string, alias_map)
        aligned["logic_string"] = aligned_logic
        events.extend(logic_events)

    for key in ("facts", "rules", "queries"):
        source = aligned.get(key, [])
        if not isinstance(source, list):
            continue
        next_items: list[str] = []
        for raw in source:
            clause = str(raw).strip()
            aligned_clause, clause_events = _align_clause_predicates(clause, alias_map)
            next_items.append(aligned_clause)
            events.extend(clause_events)
        aligned[key] = next_items

    components = aligned.get("components")
    if isinstance(components, dict):
        components["predicates"] = _collect_predicate_names_from_parsed(aligned)

    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in events:
        key = json.dumps(row, sort_keys=True)
        if key not in seen:
            seen.add(key)
            deduped.append(row)
    return aligned, deduped


def _build_registry_signature_set(registry: dict[str, Any]) -> set[str]:
    signatures: set[str] = set()
    rows = registry.get("canonical_predicates", [])
    if not isinstance(rows, list):
        return signatures
    for row in rows:
        if not isinstance(row, dict):
            continue
        name = _atomize(str(row.get("name", "")))
        try:
            arity = int(row.get("arity", 0))
        except (TypeError, ValueError):
            continue
        if name and arity >= 0:
            signatures.add(f"{name}/{arity}")
    return signatures


def _collect_signatures_from_parsed(parsed: dict[str, Any]) -> set[str]:
    signatures: set[str] = set()
    clauses: list[str] = []
    for key in ("facts", "rules", "queries"):
        value = parsed.get(key, [])
        if isinstance(value, list):
            clauses.extend(str(item).strip() for item in value if str(item).strip())

    logic = str(parsed.get("logic_string", "")).strip()
    if logic:
        if logic.startswith("retract("):
            target = _extract_retract_target(logic, [str(x) for x in parsed.get("facts", []) if str(x).strip()])
            if target:
                clauses.append(target)
        else:
            clauses.append(logic)

    for clause in clauses:
        expr = clause[:-1] if clause.endswith(".") else clause
        for sig in _extract_goal_signatures(expr):
            if sig != "retract/1":
                signatures.add(sig)
    return signatures


def _validate_parsed_against_registry(
    parsed: dict[str, Any],
    *,
    allowed_signatures: set[str],
    strict_registry: bool,
) -> tuple[list[str], list[str]]:
    if not allowed_signatures:
        return [], []
    used = sorted(_collect_signatures_from_parsed(parsed))
    unknown = [sig for sig in used if sig not in allowed_signatures]
    errors: list[str] = []
    if strict_registry and unknown:
        errors.append(
            "Predicate(s) not in registry: " + ", ".join(unknown)
        )
    return errors, unknown


def _load_type_schema(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"entities": {}, "predicates": {}}
    try:
        parsed = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError:
        return {"entities": {}, "predicates": {}}
    if not isinstance(parsed, dict):
        return {"entities": {}, "predicates": {}}
    entities = parsed.get("entities", {})
    predicates = parsed.get("predicates", {})
    if not isinstance(entities, dict):
        entities = {}
    if not isinstance(predicates, dict):
        predicates = {}
    return {"entities": entities, "predicates": predicates}


def _normalize_entity_key(token: str) -> str:
    value = token.strip().strip("'").strip('"')
    return _atomize(value) if value else ""


def _split_top_level_args(args_text: str) -> list[str]:
    items: list[str] = []
    current: list[str] = []
    depth = 0
    for ch in args_text:
        if ch == "(":
            depth += 1
            current.append(ch)
            continue
        if ch == ")":
            if depth > 0:
                depth -= 1
            current.append(ch)
            continue
        if ch == "," and depth == 0:
            value = "".join(current).strip()
            if value:
                items.append(value)
            current = []
            continue
        current.append(ch)
    value = "".join(current).strip()
    if value:
        items.append(value)
    return items


def _extract_calls_with_args(expr: str) -> list[tuple[str, list[str]]]:
    calls: list[tuple[str, list[str]]] = []
    text = expr.strip()
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if not ch.isalpha() or not ch.islower():
            i += 1
            continue
        j = i + 1
        while j < n and (text[j].isalnum() or text[j] == "_"):
            j += 1
        name = text[i:j]
        k = j
        while k < n and text[k].isspace():
            k += 1
        if k >= n or text[k] != "(":
            i = j
            continue
        depth = 0
        p = k
        close_idx = -1
        while p < n:
            if text[p] == "(":
                depth += 1
            elif text[p] == ")":
                depth -= 1
                if depth == 0:
                    close_idx = p
                    break
            p += 1
        if close_idx < 0:
            i = j
            continue
        args = _split_top_level_args(text[k + 1 : close_idx])
        calls.append((name, args))
        i = close_idx + 1
    return calls


def _validate_parsed_types(
    parsed: dict[str, Any],
    *,
    type_schema: dict[str, Any],
    strict_types: bool,
) -> list[str]:
    predicates_raw = type_schema.get("predicates", {})
    entities_raw = type_schema.get("entities", {})
    if not isinstance(predicates_raw, dict) or not predicates_raw:
        return []
    if not isinstance(entities_raw, dict):
        entities_raw = {}

    entity_types: dict[str, set[str]] = {}
    for raw_entity, raw_type in entities_raw.items():
        entity_key = _normalize_entity_key(str(raw_entity))
        if not entity_key:
            continue
        if isinstance(raw_type, list):
            type_values = {_atomize(str(item)) for item in raw_type if _atomize(str(item))}
        else:
            single = _atomize(str(raw_type))
            type_values = {single} if single else set()
        if type_values:
            entity_types[entity_key] = type_values

    predicate_types: dict[str, list[str]] = {}
    for signature, type_list in predicates_raw.items():
        sig = str(signature).strip()
        if "/" not in sig or not isinstance(type_list, list):
            continue
        normalized_types = [_atomize(str(item)) for item in type_list]
        if normalized_types:
            predicate_types[sig] = normalized_types

    if not predicate_types:
        return []

    clauses: list[str] = []
    for key in ("facts", "queries"):
        value = parsed.get(key, [])
        if isinstance(value, list):
            clauses.extend(str(item).strip() for item in value if str(item).strip())
    logic = str(parsed.get("logic_string", "")).strip()
    if logic.startswith("retract("):
        target = _extract_retract_target(logic, [str(x) for x in parsed.get("facts", []) if str(x).strip()])
        if target:
            clauses.append(target)

    errors: list[str] = []
    for clause in clauses:
        expr = clause[:-1] if clause.endswith(".") else clause
        for name, args in _extract_calls_with_args(expr):
            sig = f"{name}/{len(args)}"
            expected_types = predicate_types.get(sig)
            if not expected_types:
                continue
            for idx, arg in enumerate(args):
                if idx >= len(expected_types):
                    continue
                token = arg.strip()
                if not token or re.match(r"^[A-Z_]", token):
                    continue
                expected = expected_types[idx]
                if not expected:
                    continue
                entity_key = _normalize_entity_key(token)
                actual_types = entity_types.get(entity_key)
                if actual_types is None:
                    if strict_types:
                        errors.append(
                            f"Unknown type for entity '{entity_key}' in {sig} arg{idx + 1}; expected {expected}."
                        )
                    continue
                if expected not in actual_types:
                    errors.append(
                        f"Type mismatch for entity '{entity_key}' in {sig} arg{idx + 1}; "
                        f"expected {expected}, got {sorted(actual_types)}."
                    )
    return errors


def _build_runtime_constraint_guide(
    *,
    registry_signatures: set[str],
    strict_registry: bool,
    type_schema: dict[str, Any],
    strict_types: bool,
) -> str:
    lines: list[str] = []
    if registry_signatures:
        lines.append(
            "Allowed predicate signatures: " + ", ".join(sorted(registry_signatures))
        )
        if strict_registry:
            lines.append(
                "You MUST use only allowed predicate signatures. Do not invent new predicates."
            )
    predicates_raw = type_schema.get("predicates", {})
    if isinstance(predicates_raw, dict) and predicates_raw:
        lines.append(
            "Type constraints (predicate arg types): " + json.dumps(predicates_raw, ensure_ascii=False)
        )
        if strict_types:
            lines.append(
                "You MUST keep constants compatible with provided type constraints."
            )
    return "\n".join(lines).strip()


def _get_api_key() -> str | None:
    for key in (
        "PRETHINKER_API_KEY",
        "LMSTUDIO_API_KEY",
        "LM_API_TOKEN",
        "OPENAI_API_KEY",
    ):
        value = os.environ.get(key, "").strip()
        if value:
            return value
    return None


def _post_json(
    url: str,
    payload: dict[str, Any],
    *,
    timeout: int,
    api_key: str | None = None,
) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url=url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    if api_key:
        req.add_header("Authorization", f"Bearer {api_key}")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        raw = err.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {err.code} from {url}: {raw}") from err
    except urllib.error.URLError as err:
        raise RuntimeError(f"Connection error for {url}: {err}") from err


def _extract_last_json_object(text: str, required_keys: list[str] | None = None) -> str | None:
    if not text:
        return None
    required = required_keys or []
    depth = 0
    start = -1
    best: str | None = None

    for i, ch in enumerate(text):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
            continue
        if ch == "}":
            if depth > 0:
                depth -= 1
            if depth == 0 and start >= 0:
                candidate = text[start : i + 1]
                try:
                    parsed = json.loads(candidate)
                except json.JSONDecodeError:
                    start = -1
                    continue
                if isinstance(parsed, dict) and all(k in parsed for k in required):
                    best = candidate
                start = -1
    return best


def _call_model_prompt(
    *,
    backend: str,
    base_url: str,
    model: str,
    prompt_text: str,
    context_length: int,
    timeout: int,
    api_key: str | None,
) -> ModelResponse:
    if backend == "ollama":
        payload = {
            "model": model,
            "stream": False,
            "think": False,
            "format": "json",
            "messages": [{"role": "user", "content": prompt_text}],
            "options": {"temperature": 0, "num_ctx": context_length},
        }
        raw = _post_json(
            f"{base_url.rstrip('/')}/api/chat",
            payload,
            timeout=timeout,
            api_key=None,
        )
        message = ""
        reasoning = ""
        message_obj = raw.get("message")
        if isinstance(message_obj, dict):
            message = str(message_obj.get("content", "") or "")
            reasoning = str(message_obj.get("thinking", "") or "")
        if not message and isinstance(raw.get("response"), str):
            message = str(raw["response"])
        if not reasoning and isinstance(raw.get("thinking"), str):
            reasoning = str(raw["thinking"])
        return ModelResponse(message=message, reasoning=reasoning, raw=raw)

    payload = {
        "model": model,
        "input": prompt_text,
        "temperature": 0,
        "context_length": context_length,
    }
    raw = _post_json(
        f"{base_url.rstrip('/')}/api/v1/chat",
        payload,
        timeout=timeout,
        api_key=api_key,
    )
    message = ""
    reasoning = ""
    output_items = raw.get("output", [])
    if isinstance(output_items, list):
        for item in output_items:
            if not isinstance(item, dict):
                continue
            typ = item.get("type")
            content = item.get("content")
            if typ == "message" and isinstance(content, str) and content.strip():
                message = content.strip()
            if typ == "reasoning" and isinstance(content, str) and content.strip():
                reasoning = content
    return ModelResponse(message=message, reasoning=reasoning, raw=raw)


def _heuristic_route(text: str) -> str:
    lowered = text.strip().lower()
    if re.search(r"\b(retract|remove|delete|undo|correction|actually)\b", lowered):
        return "retract"
    if re.search(r"\b(if|whenever|then)\b", lowered):
        return "assert_rule"
    if re.search(r"\?$", lowered) or re.search(r"^\s*(who|what|where|when|why|how)\b", lowered):
        return "query"
    if re.search(r"\b(translate|summarize|rewrite|format|explain)\b", lowered):
        return "other"
    return "assert_fact"


def _build_classifier_prompt(utterance: str, *, prompt_guide: str = "") -> str:
    guide = f"Additional guidance:\n{prompt_guide}\n" if prompt_guide else ""
    return (
        "/no_think\n"
        f"{guide}"
        "Return minified JSON only:\n"
        '{"route":"assert_fact|assert_rule|query|retract|other",'
        '"needs_clarification":true|false,"ambiguity_risk":"low|medium|high","reason":"<=12 words"}\n'
        f"Utterance:\n{utterance}"
    )


def _build_extractor_prompt(
    utterance: str,
    route: str,
    *,
    known_predicates: list[str] | None = None,
    prompt_guide: str = "",
) -> str:
    route_guidance = {
        "assert_fact": "Route lock: assert_fact. Extract one best factual predicate statement.",
        "assert_rule": "Route lock: assert_rule. Extract one best conditional rule using ':-' syntax.",
        "query": "Route lock: query. Convert to query goal without '?-' prefix.",
        "retract": "Route lock: retract. Use retract(<fact>). as logic_string.",
    }.get(route, "Route lock: other. Keep logic_string empty and set intent=other.")
    known = ", ".join(known_predicates or [])
    ontology_hint = (
        f"Known ontology predicates to reuse when semantically compatible: {known}\n"
        if known
        else "Known ontology predicates: (none yet)\n"
    )
    guide = f"Additional guidance:\n{prompt_guide}\n" if prompt_guide else ""

    return (
        "/no_think\n"
        f"{guide}"
        f"{route_guidance}\n"
        f"{ontology_hint}"
        "Return JSON only with exactly these keys:\n"
        "intent,logic_string,components,facts,rules,queries,confidence,ambiguities,needs_clarification,uncertainty_score,uncertainty_label,clarification_question,clarification_reason,rationale\n"
        "Rules:\n"
        "- intent in assert_fact|assert_rule|query|retract|other\n"
        "- components object with arrays: atoms,variables,predicates\n"
        "- facts/rules/queries arrays of Prolog strings ending with '.'\n"
        "- queries must not include '?-'\n"
        "- atoms lowercase snake_case, variables Uppercase\n"
        "- confidence object with overall,intent,logic floats in [0,1]\n"
        "- uncertainty_score float in [0,1] where 1 means very uncertain\n"
        "- uncertainty_label in low|medium|high, aligned to uncertainty_score\n"
        "- clarification_question is a targeted user question ending with '?' when uncertainty is medium/high\n"
        "- clarification_reason is <=12 words and concrete\n"
        "- logic_string must be Prolog syntax (or empty only for intent=other)\n"
        "- assert_fact => logic_string == facts[0]\n"
        "- assert_rule => logic_string == rules[0]\n"
        "- query => logic_string == queries[0]\n"
        "- retract => logic_string == retract(<fact>).\n"
        "- other => logic_string='' and facts/rules/queries empty\n"
        "- For '<subject> is <relation> of <object>', emit relation(subject, object).\n"
        "- Keep argument order faithful to utterance semantics (subject first, object second).\n"
        "- For transitive statements, emit explicit compositional rule with shared variable chain.\n"
        "- Reuse known ontology predicate names when they fit; avoid synonym drift.\n"
        "No markdown. No extra text.\n"
        f"Utterance:\n{utterance}"
    )


def _build_logic_only_extractor_prompt(
    utterance: str,
    route: str,
    *,
    known_predicates: list[str] | None = None,
    prompt_guide: str = "",
) -> str:
    route_guidance = {
        "assert_fact": "Route lock: assert_fact. Emit one factual Prolog clause.",
        "assert_rule": "Route lock: assert_rule. Emit one rule clause using ':-'.",
        "query": "Route lock: query. Emit one Prolog goal clause (no '?-').",
        "retract": "Route lock: retract. Emit retract(<fact>).",
    }.get(route, "Route lock: other. Leave logic_string empty.")
    known = ", ".join(known_predicates or [])
    ontology_hint = (
        f"Known ontology predicates to reuse when semantically compatible: {known}\n"
        if known
        else "Known ontology predicates: (none yet)\n"
    )
    guide = f"Additional guidance:\n{prompt_guide}\n" if prompt_guide else ""
    return (
        "/no_think\n"
        f"{guide}"
        f"{route_guidance}\n"
        f"{ontology_hint}"
        "Return JSON only with exactly these keys:\n"
        "intent,logic_string,confidence,ambiguities,needs_clarification,uncertainty_score,uncertainty_label,clarification_question,clarification_reason,rationale\n"
        "Rules:\n"
        "- intent in assert_fact|assert_rule|query|retract|other\n"
        "- logic_string must be Prolog (or empty only for intent=other)\n"
        "- query logic_string ends with '.' and excludes '?-'\n"
        "- confidence object keys: overall,intent,logic (0..1)\n"
        "- uncertainty_score float in [0,1] where 1 means very uncertain\n"
        "- uncertainty_label in low|medium|high\n"
        "- clarification_question ends with '?' when clarification is needed\n"
        "- no markdown, no extra keys\n"
        f"Utterance:\n{utterance}"
    )


def _build_repair_prompt(
    utterance: str,
    route: str,
    candidate_json: str,
    errors: list[str],
    *,
    prompt_guide: str = "",
) -> str:
    error_block = "\n".join(f"- {item}" for item in errors) if errors else "- unknown validation error"
    guide = f"Additional guidance:\n{prompt_guide}\n" if prompt_guide else ""
    return (
        "/no_think\n"
        f"{guide}"
        "You are a strict JSON repairer for semantic parsing output.\n"
        "Return corrected JSON only. No markdown.\n"
        f"Route lock: {route}\n"
        "Required keys: intent,logic_string,components,facts,rules,queries,confidence,ambiguities,needs_clarification,uncertainty_score,uncertainty_label,clarification_question,clarification_reason,rationale\n"
        "Hard constraints:\n"
        "- intent in assert_fact|assert_rule|query|retract|other\n"
        "- components={atoms:[],variables:[],predicates:[]}\n"
        "- confidence={overall:0..1,intent:0..1,logic:0..1}\n"
        "- uncertainty_score in [0,1]\n"
        "- uncertainty_label in low|medium|high\n"
        "- clarification_question is empty or ends with '?'\n"
        "- arrays: facts,rules,queries,ambiguities\n"
        "- query entries and logic strings must end with '.' and exclude '?-'\n"
        "- assert_fact => logic_string==facts[0]\n"
        "- assert_rule => logic_string==rules[0]\n"
        "- query => logic_string==queries[0]\n"
        "- retract => logic_string==retract(<fact>).\n"
        "- other => logic_string=='' and facts/rules/queries empty\n"
        f"Original utterance:\n{utterance}\n"
        f"Validation errors:\n{error_block}\n"
        f"Candidate JSON:\n{candidate_json}\n"
    )


def _coerce_confidence_object(raw: Any) -> dict[str, float]:
    def clip(value: Any) -> float:
        try:
            val = float(value)
        except (TypeError, ValueError):
            val = 0.5
        if val < 0:
            return 0.0
        if val > 1:
            return 1.0
        return val

    if isinstance(raw, dict):
        return {
            "overall": clip(raw.get("overall")),
            "intent": clip(raw.get("intent")),
            "logic": clip(raw.get("logic")),
        }
    fallback = clip(raw)
    return {"overall": fallback, "intent": fallback, "logic": fallback}


def _clip_01(value: Any, *, fallback: float) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = fallback
    if number < 0:
        return 0.0
    if number > 1:
        return 1.0
    return number


def _coerce_uncertainty_label(raw: Any, *, score: float) -> str:
    label = str(raw or "").strip().lower()
    if label in {"low", "medium", "high"}:
        return label
    if score >= 0.75:
        return "high"
    if score >= 0.45:
        return "medium"
    return "low"


def _synthesize_clarification_question(
    *,
    utterance: str,
    route: str,
    ambiguities: list[str],
    reason: str,
) -> str:
    primary = ""
    if ambiguities:
        primary = str(ambiguities[0]).strip().rstrip(".")
    if primary:
        return f"Can you clarify this detail: {primary}?"
    if reason:
        reason_clean = reason.strip().rstrip(".")
        return f"Can you clarify this point before I apply it: {reason_clean}?"
    if route == "assert_fact":
        return "Can you confirm the exact fact and entities you want stored?"
    if route == "assert_rule":
        return "Can you confirm the exact rule condition and conclusion?"
    if route == "query":
        return "Can you clarify the exact entity or relation you want queried?"
    if route == "retract":
        return "Can you confirm the exact fact you want retracted?"
    return f"Can you clarify what you mean by: '{utterance}'?"


def _estimate_uncertainty_score(parsed: dict[str, Any]) -> float:
    confidence = parsed.get("confidence", {})
    confidence_overall = 0.5
    if isinstance(confidence, dict):
        confidence_overall = _clip_01(confidence.get("overall"), fallback=0.5)
    base = 1.0 - confidence_overall
    ambiguities = parsed.get("ambiguities", [])
    ambiguity_count = len(ambiguities) if isinstance(ambiguities, list) else 0
    if ambiguity_count > 0:
        base = max(base, min(0.9, 0.45 + 0.12 * ambiguity_count))
    if bool(parsed.get("needs_clarification", False)):
        base = max(base, 0.78)
    return _clip_01(base, fallback=0.5)


def _normalize_clarification_fields(
    parsed: dict[str, Any],
    *,
    utterance: str,
    route: str,
) -> dict[str, Any]:
    normalized = dict(parsed)
    ambiguities_raw = normalized.get("ambiguities", [])
    ambiguities: list[str] = []
    if isinstance(ambiguities_raw, list):
        for item in ambiguities_raw:
            text = str(item).strip()
            if text:
                ambiguities.append(text)

    uncertainty_score = _clip_01(
        normalized.get("uncertainty_score"),
        fallback=_estimate_uncertainty_score(normalized),
    )
    uncertainty_label = _coerce_uncertainty_label(
        normalized.get("uncertainty_label"),
        score=uncertainty_score,
    )

    reason = str(normalized.get("clarification_reason", "")).strip()
    if not reason:
        reason = str(normalized.get("rationale", "")).strip()
    if len(reason.split()) > 12:
        reason = " ".join(reason.split()[:12])

    question = str(normalized.get("clarification_question", "")).strip()
    if bool(normalized.get("needs_clarification", False)) and not question:
        question = _synthesize_clarification_question(
            utterance=utterance,
            route=route,
            ambiguities=ambiguities,
            reason=reason,
        )
    if question and not question.endswith("?"):
        question = question.rstrip(".") + "?"

    normalized["ambiguities"] = ambiguities
    normalized["uncertainty_score"] = uncertainty_score
    normalized["uncertainty_label"] = uncertainty_label
    normalized["clarification_question"] = question
    normalized["clarification_reason"] = reason
    return normalized


def _clarification_policy_decision(
    *,
    parsed: dict[str, Any],
    clarification_eagerness: float,
) -> dict[str, Any]:
    eagerness = _clip_01(clarification_eagerness, fallback=0.0)
    uncertainty_score = _clip_01(parsed.get("uncertainty_score"), fallback=_estimate_uncertainty_score(parsed))
    ambiguity_count = len(parsed.get("ambiguities", [])) if isinstance(parsed.get("ambiguities"), list) else 0
    needs_clarification = bool(parsed.get("needs_clarification", False))
    boosted_uncertainty = uncertainty_score
    if needs_clarification:
        boosted_uncertainty = max(boosted_uncertainty, 0.82)
    if ambiguity_count > 0:
        boosted_uncertainty = max(boosted_uncertainty, min(0.92, 0.45 + 0.1 * ambiguity_count))
    threshold = max(0.05, 1.0 - eagerness)
    request = boosted_uncertainty >= threshold
    return {
        "clarification_eagerness": eagerness,
        "uncertainty_score": uncertainty_score,
        "effective_uncertainty": round(boosted_uncertainty, 3),
        "threshold": round(threshold, 3),
        "request_clarification": bool(request),
        "needs_clarification_flag": needs_clarification,
    }


def _coerce_utterance_entry(raw: Any) -> tuple[str, list[str], int | None]:
    if isinstance(raw, str):
        return raw.strip(), [], None
    if not isinstance(raw, dict):
        return str(raw).strip(), [], None

    text = str(raw.get("utterance", "") or raw.get("text", "") or raw.get("input", "")).strip()
    answers_raw = raw.get("clarification_answers", [])
    answers: list[str] = []
    if isinstance(answers_raw, list):
        answers = [str(item).strip() for item in answers_raw if str(item).strip()]
    max_rounds: int | None = None
    max_rounds_raw = raw.get("max_clarification_rounds")
    if isinstance(max_rounds_raw, (int, float)):
        max_rounds = max(0, int(max_rounds_raw))
    return text, answers, max_rounds


def _build_clarification_context_utterance(utterance: str, rounds: list[dict[str, Any]]) -> str:
    if not rounds:
        return utterance
    lines = [f"Original utterance:\n{utterance}", "", "Clarification transcript:"]
    for row in rounds:
        round_index = int(row.get("round", 0))
        question = str(row.get("question", "")).strip()
        answer = str(row.get("answer", "")).strip()
        lines.append(f"Q{round_index}: {question}")
        lines.append(f"A{round_index}: {answer}")
    lines.append("")
    lines.append("Use the latest clarification answers as authoritative for disambiguation.")
    return "\n".join(lines)


def _extract_components_from_logic(logic_string: str) -> tuple[list[str], list[str], list[str]]:
    signatures = _extract_goal_signatures(logic_string[:-1] if logic_string.endswith(".") else logic_string)
    predicate_names = sorted({sig.split("/", 1)[0] for sig in signatures if "/" in sig})
    variables = sorted(set(re.findall(r"\b[A-Z][A-Za-z0-9_]*\b", logic_string)))
    atoms_raw = re.findall(r"\b[a-z][a-z0-9_]*\b", logic_string)
    atoms = sorted({tok for tok in atoms_raw if tok not in predicate_names and tok != "retract"})
    return atoms, variables, predicate_names


def _refine_logic_only_payload(
    core_parsed: dict[str, Any],
    route: str,
    *,
    utterance: str,
) -> dict[str, Any] | None:
    intent = str(core_parsed.get("intent", route)).strip()
    if intent not in {"assert_fact", "assert_rule", "query", "retract", "other"}:
        intent = route if route in {"assert_fact", "assert_rule", "query", "retract", "other"} else "other"
    logic_string = str(core_parsed.get("logic_string", "")).strip()
    if logic_string:
        logic_string = _normalize_clause(logic_string)
    confidence = _coerce_confidence_object(core_parsed.get("confidence"))
    ambiguities = core_parsed.get("ambiguities")
    rationale = str(core_parsed.get("rationale", "Logic-only extraction refined to full schema.")).strip()
    needs_clarification = bool(core_parsed.get("needs_clarification", False))

    if not isinstance(ambiguities, list):
        ambiguities = []

    facts: list[str] = []
    rules: list[str] = []
    queries: list[str] = []

    if intent == "assert_fact":
        if not logic_string:
            return None
        facts = [logic_string]
    elif intent == "assert_rule":
        if not logic_string or ":-" not in logic_string:
            return None
        rules = [logic_string]
    elif intent == "query":
        if not logic_string:
            return None
        queries = [logic_string]
    elif intent == "retract":
        target = _extract_retract_target(logic_string, [])
        if not target:
            return None
        fact_term = target[:-1] if target.endswith(".") else target
        logic_string = f"retract({fact_term})."
        facts = [target]
    elif intent == "other":
        logic_string = ""

    atoms, variables, predicates = _extract_components_from_logic(logic_string if logic_string else "noop(dummy).")
    if intent == "other":
        atoms = []
        variables = []
        predicates = []

    refined = {
        "intent": intent,
        "logic_string": logic_string,
        "components": {
            "atoms": atoms,
            "variables": variables,
            "predicates": predicates,
        },
        "facts": facts,
        "rules": rules,
        "queries": queries,
        "confidence": confidence,
        "ambiguities": ambiguities,
        "needs_clarification": needs_clarification,
        "uncertainty_score": _clip_01(core_parsed.get("uncertainty_score"), fallback=_estimate_uncertainty_score(core_parsed)),
        "uncertainty_label": _coerce_uncertainty_label(
            core_parsed.get("uncertainty_label"),
            score=_clip_01(core_parsed.get("uncertainty_score"), fallback=_estimate_uncertainty_score(core_parsed)),
        ),
        "clarification_question": str(core_parsed.get("clarification_question", "")).strip(),
        "clarification_reason": str(core_parsed.get("clarification_reason", "")).strip(),
        "rationale": rationale or "Refined logic-only parse.",
    }
    refined = _normalize_clarification_fields(refined, utterance=utterance, route=route)
    ok, _ = _validate_parsed(refined)
    return refined if ok else None


def _validate_parsed(parsed: dict[str, Any]) -> tuple[bool, list[str]]:
    errors: list[str] = []
    required = [
        "intent",
        "logic_string",
        "components",
        "facts",
        "rules",
        "queries",
        "confidence",
        "ambiguities",
        "needs_clarification",
        "uncertainty_score",
        "uncertainty_label",
        "clarification_question",
        "clarification_reason",
        "rationale",
    ]
    for key in required:
        if key not in parsed:
            errors.append(f"Missing key: {key}")

    intent = str(parsed.get("intent", ""))
    allowed = {"assert_fact", "assert_rule", "query", "retract", "other"}
    if intent not in allowed:
        errors.append(f"Invalid intent: {intent}")

    components = parsed.get("components")
    if not isinstance(components, dict) or not all(
        isinstance(components.get(name), list) for name in ("atoms", "variables", "predicates")
    ):
        errors.append("components must be object with list fields atoms/variables/predicates")

    confidence = parsed.get("confidence")
    if not isinstance(confidence, dict):
        errors.append("confidence must be object")
    else:
        for key in ("overall", "intent", "logic"):
            value = confidence.get(key)
            try:
                number = float(value)
            except (TypeError, ValueError):
                errors.append(f"confidence.{key} must be numeric")
                continue
            if number < 0 or number > 1:
                errors.append(f"confidence.{key} out of range [0,1]")

    for key in ("facts", "rules", "queries", "ambiguities"):
        if not isinstance(parsed.get(key), list):
            errors.append(f"{key} must be list")

    if not isinstance(parsed.get("needs_clarification"), bool):
        errors.append("needs_clarification must be boolean")

    uncertainty_score = parsed.get("uncertainty_score")
    try:
        uncertainty_number = float(uncertainty_score)
    except (TypeError, ValueError):
        errors.append("uncertainty_score must be numeric")
        uncertainty_number = -1.0
    if uncertainty_number < 0 or uncertainty_number > 1:
        errors.append("uncertainty_score out of range [0,1]")

    uncertainty_label = str(parsed.get("uncertainty_label", "")).strip().lower()
    if uncertainty_label not in {"low", "medium", "high"}:
        errors.append("uncertainty_label must be one of low|medium|high")

    clarification_question = str(parsed.get("clarification_question", "")).strip()
    if clarification_question and not clarification_question.endswith("?"):
        errors.append("clarification_question must end with '?' when non-empty")

    clarification_reason = str(parsed.get("clarification_reason", "")).strip()
    if len(clarification_reason.split()) > 12:
        errors.append("clarification_reason must be 12 words or fewer")

    logic_string = str(parsed.get("logic_string", "")).strip()
    if logic_string and not logic_string.endswith("."):
        errors.append("logic_string must end with '.' when non-empty")

    query_prefix_bad = any(str(q).lstrip().startswith("?-") for q in parsed.get("queries", []))
    if query_prefix_bad:
        errors.append("queries must not include '?-' prefix")

    prolog_goal = re.compile(r"^[a-z][a-z0-9_]*\(([^()]*)\)\.$")
    prolog_rule = re.compile(r"^[a-z][a-z0-9_]*\(([^()]*)\)\s*:-\s*.+\.$")
    prolog_retract = re.compile(r"^retract\(\s*[a-z][a-z0-9_]*\(([^()]*)\)\s*\)\.$")

    facts = [str(x).strip() for x in parsed.get("facts", [])]
    rules = [str(x).strip() for x in parsed.get("rules", [])]
    queries = [str(x).strip() for x in parsed.get("queries", [])]

    if intent == "assert_fact":
        if not facts:
            errors.append("assert_fact requires facts[0]")
        else:
            if logic_string != facts[0]:
                errors.append("assert_fact requires logic_string == facts[0]")
            if not prolog_goal.match(facts[0]):
                errors.append("facts[0] is not valid Prolog fact/goal")
    elif intent == "assert_rule":
        if not rules:
            errors.append("assert_rule requires rules[0]")
        else:
            if logic_string != rules[0]:
                errors.append("assert_rule requires logic_string == rules[0]")
            if not prolog_rule.match(rules[0]):
                errors.append("rules[0] is not valid Prolog rule")
    elif intent == "query":
        if not queries:
            errors.append("query requires queries[0]")
        else:
            if logic_string != queries[0]:
                errors.append("query requires logic_string == queries[0]")
            if not prolog_goal.match(queries[0]):
                errors.append("queries[0] is not valid Prolog goal")
    elif intent == "retract":
        if not prolog_retract.match(logic_string):
            errors.append("retract requires logic_string format retract(<fact>).")
    elif intent == "other":
        if logic_string:
            errors.append("other requires empty logic_string")
        if facts or rules or queries:
            errors.append("other requires empty facts/rules/queries")

    return (len(errors) == 0, errors)


def _parse_model_json(response: ModelResponse, required_keys: list[str]) -> tuple[dict[str, Any] | None, str]:
    message = (response.message or "").strip()
    if message:
        candidate = _extract_last_json_object(message, required_keys) or message
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, dict):
                return parsed, candidate
        except json.JSONDecodeError:
            pass

    reasoning = response.reasoning or ""
    candidate = _extract_last_json_object(reasoning, required_keys)
    if candidate:
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, dict):
                return parsed, candidate
        except json.JSONDecodeError:
            pass

    return None, ""


def _extract_retract_target(logic_string: str, fallback_facts: list[str]) -> str | None:
    match = re.match(r"^retract\(\s*(.+?)\s*\)\.$", logic_string.strip())
    if match:
        fact = match.group(1).strip()
        if not fact.endswith("."):
            fact += "."
        return fact
    if fallback_facts:
        fact = str(fallback_facts[0]).strip()
        if not fact.endswith("."):
            fact += "."
        return fact
    return None


def _build_retract_fallback_parse(utterance: str) -> dict[str, Any] | None:
    text = utterance.strip()
    if not text:
        return None
    fact = ""
    match_with_dot = re.search(r"([a-z][a-z0-9_]*\([^()]*\)\.)", text)
    if match_with_dot:
        fact = match_with_dot.group(1).strip()
    else:
        match_no_dot = re.search(r"([a-z][a-z0-9_]*\([^()]*\))", text)
        if match_no_dot:
            fact = match_no_dot.group(1).strip() + "."
    fact = _normalize_clause(fact)
    if not fact:
        return None

    predicate_match = re.match(r"^([a-z][a-z0-9_]*)\(", fact)
    if not predicate_match:
        return None
    predicate = predicate_match.group(1)

    tokens = re.findall(r"\b[a-z][a-z0-9_]*\b", fact)
    atoms = [tok for idx, tok in enumerate(tokens) if not (idx == 0 and tok == predicate)]
    variables = re.findall(r"\b[A-Z][A-Za-z0-9_]*\b", fact)
    fact_term = fact[:-1] if fact.endswith(".") else fact
    parsed = {
        "intent": "retract",
        "logic_string": f"retract({fact_term}).",
        "components": {
            "atoms": sorted(set(atoms)),
            "variables": sorted(set(variables)),
            "predicates": [predicate],
        },
        "facts": [fact],
        "rules": [],
        "queries": [],
        "confidence": {
            "overall": 0.7,
            "intent": 0.85,
            "logic": 0.65,
        },
        "ambiguities": [],
        "needs_clarification": False,
        "uncertainty_score": 0.22,
        "uncertainty_label": "low",
        "clarification_question": "",
        "clarification_reason": "",
        "rationale": "Fallback retract parse from explicit Prolog-like fact in utterance.",
    }
    ok, _ = _validate_parsed(parsed)
    return parsed if ok else None


def _atomize(text: str) -> str:
    lowered = text.strip().lower()
    lowered = re.sub(r"'s\b", "", lowered)
    lowered = re.sub(r"[^a-z0-9]+", "_", lowered)
    lowered = re.sub(r"_+", "_", lowered).strip("_")
    return lowered


def _build_parse_payload(
    *,
    intent: str,
    logic_string: str,
    facts: list[str],
    rules: list[str],
    queries: list[str],
    predicates: list[str],
    atoms: list[str],
    variables: list[str],
    rationale: str,
) -> dict[str, Any]:
    return {
        "intent": intent,
        "logic_string": logic_string,
        "components": {
            "atoms": sorted(set(atoms)),
            "variables": sorted(set(variables)),
            "predicates": sorted(set(predicates)),
        },
        "facts": facts,
        "rules": rules,
        "queries": queries,
        "confidence": {
            "overall": 0.72,
            "intent": 0.82,
            "logic": 0.68,
        },
        "ambiguities": [],
        "needs_clarification": False,
        "uncertainty_score": 0.24,
        "uncertainty_label": "low",
        "clarification_question": "",
        "clarification_reason": "",
        "rationale": rationale,
    }


def _build_assert_fact_fallback_parse(utterance: str) -> dict[str, Any] | None:
    text = utterance.strip().rstrip("?")
    if not text:
        return None

    explicit = re.search(r"([a-z][a-z0-9_]*\([^()]*\)\.)", text)
    if explicit:
        fact = _normalize_clause(explicit.group(1))
        predicate_match = re.match(r"^([a-z][a-z0-9_]*)\(", fact)
        if not predicate_match:
            return None
        predicate = predicate_match.group(1)
        atoms = [tok for tok in re.findall(r"\b[a-z][a-z0-9_]*\b", fact) if tok != predicate]
        parsed = _build_parse_payload(
            intent="assert_fact",
            logic_string=fact,
            facts=[fact],
            rules=[],
            queries=[],
            predicates=[predicate],
            atoms=atoms,
            variables=[],
            rationale="Fallback fact parse from explicit Prolog fact in utterance.",
        )
        ok, _ = _validate_parsed(parsed)
        return parsed if ok else None

    my_possessive = re.match(
        r"^\s*my\s+([A-Za-z][A-Za-z0-9_-]*)\s+is\s+([A-Za-z][A-Za-z0-9_'-]*)\.?\s*$",
        text,
        re.IGNORECASE,
    )
    if my_possessive:
        relation = _atomize(my_possessive.group(1))
        value_atom = _atomize(my_possessive.group(2))
        owner_atom = "me"
        if relation and value_atom:
            fact = f"{relation}({value_atom}, {owner_atom})."
            parsed = _build_parse_payload(
                intent="assert_fact",
                logic_string=fact,
                facts=[fact],
                rules=[],
                queries=[],
                predicates=[relation],
                atoms=[value_atom, owner_atom],
                variables=[],
                rationale="Fallback possessive fact parse from 'my <relation> is <entity>'.",
            )
            ok, _ = _validate_parsed(parsed)
            return parsed if ok else None

    named_possessive = re.match(
        r"^\s*([A-Za-z][A-Za-z0-9_'-]*)'?s\s+([A-Za-z][A-Za-z0-9_-]*)\s+is\s+([A-Za-z][A-Za-z0-9_'-]*)\.?\s*$",
        text,
        re.IGNORECASE,
    )
    if named_possessive:
        owner_atom = _atomize(named_possessive.group(1))
        relation = _atomize(named_possessive.group(2))
        value_atom = _atomize(named_possessive.group(3))
        if owner_atom and relation and value_atom:
            fact = f"{relation}({value_atom}, {owner_atom})."
            parsed = _build_parse_payload(
                intent="assert_fact",
                logic_string=fact,
                facts=[fact],
                rules=[],
                queries=[],
                predicates=[relation],
                atoms=[value_atom, owner_atom],
                variables=[],
                rationale="Fallback possessive fact parse from '<owner>'s <relation> is <entity>'.",
            )
            ok, _ = _validate_parsed(parsed)
            return parsed if ok else None

    unary = re.match(r"^\s*([A-Za-z][A-Za-z0-9_'-]*)\s+is\s+(?:a|an)\s+([A-Za-z][A-Za-z0-9_-]*)\.?\s*$", text, re.IGNORECASE)
    if unary:
        subject_atom = _atomize(unary.group(1))
        predicate = _atomize(unary.group(2))
        if subject_atom and predicate:
            fact = f"{predicate}({subject_atom})."
            parsed = _build_parse_payload(
                intent="assert_fact",
                logic_string=fact,
                facts=[fact],
                rules=[],
                queries=[],
                predicates=[predicate],
                atoms=[subject_atom],
                variables=[],
                rationale="Fallback unary fact parse from '<subject> is a <class>'.",
            )
            ok, _ = _validate_parsed(parsed)
            return parsed if ok else None

    binary = re.match(
        r"^\s*([A-Za-z][A-Za-z0-9_'-]*)\s+is\s+(?:a|an|the)?\s*([A-Za-z][A-Za-z0-9_-]*)\s+of\s+([A-Za-z][A-Za-z0-9_'-]*)\.?\s*$",
        text,
        re.IGNORECASE,
    )
    if binary:
        subject_atom = _atomize(binary.group(1))
        relation = _atomize(binary.group(2))
        obj_atom = _atomize(binary.group(3))
        if subject_atom and relation and obj_atom:
            fact = f"{relation}({subject_atom}, {obj_atom})."
            parsed = _build_parse_payload(
                intent="assert_fact",
                logic_string=fact,
                facts=[fact],
                rules=[],
                queries=[],
                predicates=[relation],
                atoms=[subject_atom, obj_atom],
                variables=[],
                rationale="Fallback binary relation parse from '<subject> is <relation> of <object>'.",
            )
            ok, _ = _validate_parsed(parsed)
            return parsed if ok else None
    return None


def _build_assert_rule_fallback_parse(utterance: str) -> dict[str, Any] | None:
    text = utterance.strip().rstrip("?")
    if not text:
        return None

    unary = re.match(
        r"^\s*if\s+someone\s+is\s+(?:a|an)\s+([A-Za-z][A-Za-z0-9_-]*)\s+then\s+they\s+are\s+(?:a|an)?\s*([A-Za-z][A-Za-z0-9_-]*)\.?\s*$",
        text,
        re.IGNORECASE,
    )
    if unary:
        body = _atomize(unary.group(1))
        head = _atomize(unary.group(2))
        if body and head:
            rule = f"{head}(X) :- {body}(X)."
            parsed = _build_parse_payload(
                intent="assert_rule",
                logic_string=rule,
                facts=[],
                rules=[rule],
                queries=[],
                predicates=[head, body],
                atoms=[],
                variables=["X"],
                rationale="Fallback unary implication rule parse.",
            )
            ok, _ = _validate_parsed(parsed)
            return parsed if ok else None

    transitive = re.match(
        (
            r"^\s*if\s+([A-Za-z])\s+is\s+(?:a|an)?\s*([A-Za-z][A-Za-z0-9_-]*)\s+of\s+([A-Za-z])\s+"
            r"and\s+\3\s+is\s+(?:a|an)?\s*([A-Za-z][A-Za-z0-9_-]*)\s+of\s+([A-Za-z])\s+"
            r"then\s+\1\s+is\s+(?:a|an)?\s*([A-Za-z][A-Za-z0-9_-]*)\s+of\s+\5\.?\s*$"
        ),
        text,
        re.IGNORECASE,
    )
    if transitive:
        x = transitive.group(1).upper()
        rel1 = _atomize(transitive.group(2))
        y = transitive.group(3).upper()
        rel2 = _atomize(transitive.group(4))
        z = transitive.group(5).upper()
        rel_head = _atomize(transitive.group(6))
        if x and y and z and rel1 and rel2 and rel_head:
            rule = f"{rel_head}({x}, {z}) :- {rel1}({x}, {y}), {rel2}({y}, {z})."
            parsed = _build_parse_payload(
                intent="assert_rule",
                logic_string=rule,
                facts=[],
                rules=[rule],
                queries=[],
                predicates=[rel_head, rel1, rel2],
                atoms=[],
                variables=[x, y, z],
                rationale="Fallback transitive composition rule parse.",
            )
            ok, _ = _validate_parsed(parsed)
            return parsed if ok else None

    binary = re.match(
        (
            r"^\s*if\s+([A-Za-z])\s+is\s+(?:a|an)?\s*([A-Za-z][A-Za-z0-9_-]*)\s+of\s+([A-Za-z])\s+"
            r"then\s+\1\s+is\s+(?:a|an)?\s*([A-Za-z][A-Za-z0-9_-]*)\s+of\s+\3\.?\s*$"
        ),
        text,
        re.IGNORECASE,
    )
    if binary:
        x = binary.group(1).upper()
        rel_body = _atomize(binary.group(2))
        y = binary.group(3).upper()
        rel_head = _atomize(binary.group(4))
        if x and y and rel_body and rel_head:
            rule = f"{rel_head}({x}, {y}) :- {rel_body}({x}, {y})."
            parsed = _build_parse_payload(
                intent="assert_rule",
                logic_string=rule,
                facts=[],
                rules=[rule],
                queries=[],
                predicates=[rel_head, rel_body],
                atoms=[],
                variables=[x, y],
                rationale="Fallback binary implication rule parse.",
            )
            ok, _ = _validate_parsed(parsed)
            return parsed if ok else None
    return None


def _build_query_fallback_parse(utterance: str) -> dict[str, Any] | None:
    text = utterance.strip()
    if not text:
        return None

    explicit = re.search(r"([a-z][a-z0-9_]*\([^()]*\)\.)", text)
    if explicit:
        query = _normalize_clause(explicit.group(1))
        predicate_match = re.match(r"^([a-z][a-z0-9_]*)\(", query)
        if not predicate_match:
            return None
        predicate = predicate_match.group(1)
        variables = re.findall(r"\b[A-Z][A-Za-z0-9_]*\b", query)
        atoms = [tok for tok in re.findall(r"\b[a-z][a-z0-9_]*\b", query) if tok != predicate]
        parsed = _build_parse_payload(
            intent="query",
            logic_string=query,
            facts=[],
            rules=[],
            queries=[query],
            predicates=[predicate],
            atoms=atoms,
            variables=variables,
            rationale="Fallback query parse from explicit Prolog query form.",
        )
        ok, _ = _validate_parsed(parsed)
        return parsed if ok else None

    possessive = re.match(
        r"^\s*who\s+is\s+([A-Za-z][A-Za-z0-9_'-]*)'?s\s+([A-Za-z][A-Za-z0-9_-]*)\??\s*$",
        text,
        re.IGNORECASE,
    )
    if possessive:
        subject = _atomize(possessive.group(1))
        predicate = _atomize(possessive.group(2))
        if subject and predicate:
            query = f"{predicate}({subject}, X)."
            parsed = _build_parse_payload(
                intent="query",
                logic_string=query,
                facts=[],
                rules=[],
                queries=[query],
                predicates=[predicate],
                atoms=[subject],
                variables=["X"],
                rationale="Fallback query parse from possessive relation question.",
            )
            ok, _ = _validate_parsed(parsed)
            return parsed if ok else None
    return None


def _build_route_fallback_parse(route: str, utterance: str) -> dict[str, Any] | None:
    if route == "retract":
        return _build_retract_fallback_parse(utterance)
    if route == "assert_fact":
        return _build_assert_fact_fallback_parse(utterance)
    if route == "assert_rule":
        return _build_assert_rule_fallback_parse(utterance)
    if route == "query":
        return _build_query_fallback_parse(utterance)
    return None


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _normalize_kb_name(raw_name: str) -> str:
    cleaned = re.sub(r"[^a-z0-9_-]+", "_", raw_name.strip().lower())
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    return cleaned or DEFAULT_KB_NAME


def _normalize_clause(clause: str) -> str:
    normalized = clause.strip()
    if normalized and not normalized.endswith("."):
        normalized += "."
    return normalized


def _read_corpus_clauses(path: Path) -> list[str]:
    if not path.exists():
        return []
    clauses: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("%"):
            continue
        if line.startswith(":-"):
            continue
        if not line.endswith("."):
            continue
        clauses.append(line)
    return clauses


def _write_corpus_clauses(path: Path, clauses: set[str]) -> dict[str, Any]:
    normalized = sorted({_normalize_clause(c) for c in clauses if _normalize_clause(c)})
    body = "\n".join(normalized)
    header = (
        "% Auto-generated by kb_pipeline.py\n"
        f"% Updated UTC: {_utc_now_iso()}\n\n"
    )
    text = header + (body + "\n" if body else "")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return {"path": str(path), "clause_count": len(normalized), "status": "written"}


def _load_corpus_into_server(server: Any, clauses: list[str]) -> dict[str, Any]:
    summary = {
        "status": "success",
        "loaded_total": 0,
        "loaded_facts": 0,
        "loaded_rules": 0,
        "skipped_total": 0,
        "failed_total": 0,
        "errors": [],
    }
    for raw_clause in clauses:
        clause = _normalize_clause(raw_clause)
        if not clause:
            summary["skipped_total"] += 1
            continue
        if clause.startswith("retract("):
            summary["skipped_total"] += 1
            continue

        if ":-" in clause:
            tool = "assert_rule"
            result = server.assert_rule(clause)
        else:
            tool = "assert_fact"
            result = server.assert_fact(clause)

        if result.get("status") == "success":
            summary["loaded_total"] += 1
            if tool == "assert_rule":
                summary["loaded_rules"] += 1
            else:
                summary["loaded_facts"] += 1
            continue

        summary["failed_total"] += 1
        summary["errors"].append(
            {"tool": tool, "clause": clause, "result": result}
        )

    if summary["failed_total"] > 0:
        summary["status"] = "partial_failure"
    return summary


class CorePrologRuntime:
    """Local runtime backed by the vendored core Prolog interpreter."""

    def __init__(self, max_depth: int = 500) -> None:
        self.engine = PrologEngine(max_depth=max_depth)

    @staticmethod
    def _split_top_level(text: str, delimiter: str) -> list[str]:
        parts: list[str] = []
        current: list[str] = []
        paren_depth = 0
        bracket_depth = 0

        for ch in text:
            if ch == "(":
                paren_depth += 1
                current.append(ch)
                continue
            if ch == ")":
                paren_depth = max(0, paren_depth - 1)
                current.append(ch)
                continue
            if ch == "[":
                bracket_depth += 1
                current.append(ch)
                continue
            if ch == "]":
                bracket_depth = max(0, bracket_depth - 1)
                current.append(ch)
                continue
            if ch == delimiter and paren_depth == 0 and bracket_depth == 0:
                part = "".join(current).strip()
                if part:
                    parts.append(part)
                current = []
                continue
            current.append(ch)

        tail = "".join(current).strip()
        if tail:
            parts.append(tail)
        return parts

    @staticmethod
    def _contains_variable(term: Term) -> bool:
        if getattr(term, "is_variable", False):
            return True
        args = getattr(term, "args", [])
        return any(CorePrologRuntime._contains_variable(arg) for arg in args)

    def _parse_query_term(self, query: str) -> Term:
        normalized = (query or "").strip()
        if not normalized:
            raise ValueError("Empty query.")
        if normalized.endswith("."):
            normalized = normalized[:-1].strip()
        if not normalized:
            raise ValueError("Empty query.")
        return self.engine.parse_term(normalized)

    @staticmethod
    def _collect_query_variables(term: Term) -> list[str]:
        names: list[str] = []

        def walk(node: Term) -> None:
            if getattr(node, "is_variable", False):
                name = getattr(node, "name", "")
                if isinstance(name, str) and name not in names:
                    names.append(name)
            for arg in getattr(node, "args", []):
                walk(arg)

        walk(term)
        return names

    def empty_kb(self) -> dict[str, Any]:
        self.engine.clauses.clear()
        return {
            "status": "success",
            "result_type": "runtime_emptied",
            "message": "Core runtime KB cleared.",
        }

    def assert_fact(self, clause: str) -> dict[str, Any]:
        normalized = _normalize_clause(clause)
        if not normalized:
            return {"status": "validation_error", "message": "Empty fact clause."}
        if ":-" in normalized:
            return {"status": "validation_error", "message": "Fact clause contains rule operator."}
        try:
            fact_term = self._parse_query_term(normalized)
        except Exception as error:
            return {"status": "validation_error", "message": f"Fact parse failed: {error}"}

        if self._contains_variable(fact_term):
            return {"status": "validation_error", "message": "Fact must be ground (no variables)."}

        for existing in self.engine.clauses:
            if existing.head == fact_term and not existing.body:
                return {
                    "status": "success",
                    "result_type": "fact_asserted",
                    "fact": normalized,
                    "message": "Fact already present in core runtime.",
                }

        self.engine.add_clause(Clause(fact_term))
        return {"status": "success", "result_type": "fact_asserted", "fact": normalized}

    def assert_rule(self, clause: str) -> dict[str, Any]:
        normalized = _normalize_clause(clause)
        if not normalized:
            return {"status": "validation_error", "message": "Empty rule clause."}
        raw = normalized[:-1].strip() if normalized.endswith(".") else normalized
        if ":-" not in raw:
            return {"status": "validation_error", "message": "Rule clause missing ':-'."}

        try:
            head_text, body_text = raw.split(":-", 1)
            head_text = head_text.strip()
            body_text = body_text.strip()
            if not head_text or not body_text:
                return {"status": "validation_error", "message": "Rule must include non-empty head and body."}
            head_term = self._parse_query_term(head_text)
            body_terms = [self._parse_query_term(piece) for piece in self._split_top_level(body_text, ",")]
            if not body_terms:
                return {"status": "validation_error", "message": "Rule body is empty."}
        except Exception as error:
            return {"status": "validation_error", "message": f"Rule parse failed: {error}"}

        rule_clause = Clause(head_term, body_terms)
        for existing in self.engine.clauses:
            if existing.head == rule_clause.head and (existing.body or []) == rule_clause.body:
                return {
                    "status": "success",
                    "result_type": "rule_asserted",
                    "rule": normalized,
                    "message": "Rule already present in core runtime.",
                }

        self.engine.add_clause(rule_clause)
        return {"status": "success", "result_type": "rule_asserted", "rule": normalized}

    def retract_fact(self, clause: str) -> dict[str, Any]:
        normalized = _normalize_clause(clause)
        if not normalized:
            return {"status": "validation_error", "message": "Empty retract clause."}
        if ":-" in normalized:
            return {"status": "validation_error", "message": "Retract target cannot be a rule."}
        try:
            fact_term = self._parse_query_term(normalized)
        except Exception as error:
            return {"status": "validation_error", "message": f"Retract parse failed: {error}"}
        if self._contains_variable(fact_term):
            return {"status": "validation_error", "message": "Retract target must be ground (no variables)."}

        for index, existing in enumerate(self.engine.clauses):
            if existing.head == fact_term and not existing.body:
                del self.engine.clauses[index]
                return {"status": "success", "result_type": "fact_retracted", "fact": normalized}

        return {"status": "no_results", "result_type": "no_result", "fact": normalized}

    def query_rows(self, query: str) -> dict[str, Any]:
        normalized = _normalize_clause(query)
        try:
            query_term = self._parse_query_term(normalized)
            variable_names = self._collect_query_variables(query_term)
            solutions = self.engine.resolve(query_term)
        except Exception as error:
            return {
                "status": "error",
                "result_type": "execution_error",
                "predicate": "",
                "prolog_query": normalized,
                "message": str(error),
                "reasoning_basis": {"kind": "core-local"},
            }

        if not solutions:
            return {
                "status": "no_results",
                "result_type": "no_result",
                "predicate": query_term.name,
                "prolog_query": normalized,
                "variables": variable_names,
                "rows": [],
                "num_rows": 0,
                "reasoning_basis": {"kind": "core-local"},
            }

        rows: list[dict[str, str]] = []
        seen_rows: set[str] = set()
        if variable_names:
            for solution in solutions:
                row: dict[str, str] = {}
                for variable_name in variable_names:
                    bound = solution.apply(Term(variable_name, is_variable=True))
                    row[variable_name] = str(bound)
                key = json.dumps(row, sort_keys=True)
                if key in seen_rows:
                    continue
                seen_rows.add(key)
                rows.append(row)
        else:
            rows.append({})

        return {
            "status": "success",
            "result_type": "table",
            "predicate": query_term.name,
            "prolog_query": normalized,
            "variables": variable_names,
            "rows": rows,
            "num_rows": len(rows),
            "reasoning_basis": {"kind": "core-local"},
        }


class ParseOnlyRuntime:
    """Lightweight local runtime used when MCP is disabled.

    Supports deterministic fact/rule storage and direct fact query lookups.
    It does not perform full Prolog inference for rule-derived answers.
    """

    def __init__(self) -> None:
        self._clauses: set[str] = set()

    def empty_kb(self) -> dict[str, Any]:
        self._clauses.clear()
        return {
            "status": "success",
            "result_type": "runtime_cleared",
            "message": "Parse-only runtime cleared.",
        }

    def assert_fact(self, clause: str) -> dict[str, Any]:
        normalized = _normalize_clause(clause)
        if not normalized:
            return {"status": "validation_error", "message": "Empty fact clause."}
        if ":-" in normalized:
            return {"status": "validation_error", "message": "Fact clause contains rule operator."}
        self._clauses.add(normalized)
        return {"status": "success", "result_type": "fact_asserted", "fact": normalized}

    def assert_rule(self, clause: str) -> dict[str, Any]:
        normalized = _normalize_clause(clause)
        if not normalized:
            return {"status": "validation_error", "message": "Empty rule clause."}
        if ":-" not in normalized:
            return {"status": "validation_error", "message": "Rule clause missing ':-'."}
        self._clauses.add(normalized)
        return {"status": "success", "result_type": "rule_asserted", "rule": normalized}

    def retract_fact(self, clause: str) -> dict[str, Any]:
        normalized = _normalize_clause(clause)
        if normalized in self._clauses:
            self._clauses.remove(normalized)
            return {"status": "success", "result_type": "fact_retracted", "fact": normalized}
        return {"status": "no_results", "result_type": "no_result", "fact": normalized}

    def query_rows(self, query: str) -> dict[str, Any]:
        normalized = _normalize_clause(query)
        body = normalized[:-1] if normalized.endswith(".") else normalized
        calls = _extract_calls_with_args(body)
        if len(calls) != 1:
            return {
                "status": "no_results",
                "result_type": "no_result",
                "predicate": "",
                "prolog_query": normalized,
                "variables": [],
                "rows": [],
                "num_rows": 0,
                "reasoning_basis": {"kind": "parse-only", "note": "Only direct fact queries are supported in parse-only runtime."},
            }
        predicate, query_args = calls[0]
        variables = [arg for arg in query_args if re.match(r"^[A-Z_][A-Za-z0-9_]*$", arg)]
        rows: list[dict[str, Any]] = []
        for clause in self._clauses:
            if ":-" in clause:
                continue
            fact_calls = _extract_calls_with_args(clause[:-1] if clause.endswith(".") else clause)
            if len(fact_calls) != 1:
                continue
            fact_predicate, fact_args = fact_calls[0]
            if fact_predicate != predicate or len(fact_args) != len(query_args):
                continue
            bindings: dict[str, str] = {}
            matched = True
            for query_arg, fact_arg in zip(query_args, fact_args):
                if re.match(r"^[A-Z_][A-Za-z0-9_]*$", query_arg):
                    existing = bindings.get(query_arg)
                    if existing is not None and existing != fact_arg:
                        matched = False
                        break
                    bindings[query_arg] = fact_arg
                    continue
                if query_arg != fact_arg:
                    matched = False
                    break
            if matched:
                row = {name: bindings.get(name, "") for name in variables}
                rows.append(row)
        status = "success" if rows else "no_results"
        result_type = "table" if rows else "no_result"
        return {
            "status": status,
            "result_type": result_type,
            "predicate": predicate,
            "prolog_query": normalized,
            "variables": variables,
            "rows": rows,
            "num_rows": len(rows),
            "reasoning_basis": {
                "kind": "parse-only",
                "note": "Direct fact lookup only; no rule inference in parse-only runtime.",
            },
        }


def _count_top_level_args(args_text: str) -> int:
    if not args_text.strip():
        return 0
    depth = 0
    count = 1
    for ch in args_text:
        if ch == "(":
            depth += 1
        elif ch == ")":
            if depth > 0:
                depth -= 1
        elif ch == "," and depth == 0:
            count += 1
    return count


def _extract_goal_signatures(expr: str) -> list[str]:
    signatures: list[str] = []
    text = expr.strip()
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if not ch.isalpha() or not ch.islower():
            i += 1
            continue
        j = i + 1
        while j < n and (text[j].isalnum() or text[j] == "_"):
            j += 1
        name = text[i:j]
        k = j
        while k < n and text[k].isspace():
            k += 1
        if k >= n or text[k] != "(":
            i = j
            continue
        depth = 0
        p = k
        close_idx = -1
        while p < n:
            if text[p] == "(":
                depth += 1
            elif text[p] == ")":
                depth -= 1
                if depth == 0:
                    close_idx = p
                    break
            p += 1
        if close_idx < 0:
            i = j
            continue
        args = text[k + 1 : close_idx]
        arity = _count_top_level_args(args)
        signatures.append(f"{name}/{arity}")
        i = close_idx + 1
    return signatures


def _build_ontology_profile(kb_name: str, clauses: set[str]) -> dict[str, Any]:
    normalized_clauses = sorted({_normalize_clause(c) for c in clauses if _normalize_clause(c)})
    fact_predicates: set[str] = set()
    rule_head_predicates: set[str] = set()
    rule_body_predicates: set[str] = set()

    for clause in normalized_clauses:
        if ":-" in clause:
            head, body = clause[:-1].split(":-", 1)
            for sig in _extract_goal_signatures(head):
                rule_head_predicates.add(sig)
            for sig in _extract_goal_signatures(body):
                rule_body_predicates.add(sig)
        else:
            for sig in _extract_goal_signatures(clause[:-1]):
                fact_predicates.add(sig)

    predicate_signatures = sorted(fact_predicates | rule_head_predicates | rule_body_predicates)
    return {
        "ontology_name": kb_name,
        "generated_at_utc": _utc_now_iso(),
        "clause_count": len(normalized_clauses),
        "predicate_signatures": predicate_signatures,
        "fact_predicates": sorted(fact_predicates),
        "rule_head_predicates": sorted(rule_head_predicates),
        "rule_body_predicates": sorted(rule_body_predicates),
    }


def _known_predicate_names_from_corpus(clauses: set[str]) -> list[str]:
    profile = _build_ontology_profile("tmp", clauses)
    names = {
        str(signature).split("/", 1)[0]
        for signature in profile.get("predicate_signatures", [])
        if "/" in str(signature)
    }
    return sorted(names)


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if isinstance(parsed, dict):
        return parsed
    return None


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _compare_ontology_profiles(previous: dict[str, Any] | None, current: dict[str, Any]) -> dict[str, Any]:
    prev_set = set()
    if isinstance(previous, dict):
        prev_set = {str(x) for x in previous.get("predicate_signatures", [])}
    curr_set = {str(x) for x in current.get("predicate_signatures", [])}

    added = sorted(curr_set - prev_set)
    removed = sorted(prev_set - curr_set)
    union_size = len(curr_set | prev_set)
    overlap_size = len(curr_set & prev_set)
    similarity = 1.0 if union_size == 0 else overlap_size / union_size
    churn = 0.0 if len(prev_set) == 0 else (len(added) + len(removed)) / len(prev_set)

    if not previous:
        change_level = "new"
    elif not added and not removed:
        change_level = "none"
    elif removed or churn >= 0.5:
        change_level = "major"
    elif churn >= 0.2:
        change_level = "moderate"
    else:
        change_level = "minor"

    return {
        "change_level": change_level,
        "requires_confirmation": bool(change_level == "major" or len(removed) > 0),
        "similarity_to_previous": round(similarity, 4),
        "added_signatures": added,
        "removed_signatures": removed,
        "previous_signature_count": len(prev_set),
        "current_signature_count": len(curr_set),
    }


def _load_ontology_index(path: Path) -> dict[str, Any]:
    parsed = _load_json(path)
    if not isinstance(parsed, dict):
        return {"ontologies": {}}
    if not isinstance(parsed.get("ontologies"), dict):
        parsed["ontologies"] = {}
    return parsed


def _compute_known_ontology_matches(
    kb_name: str,
    current_profile: dict[str, Any],
    index_payload: dict[str, Any],
    *,
    max_matches: int,
) -> list[dict[str, Any]]:
    current = {str(x) for x in current_profile.get("predicate_signatures", [])}
    rows: list[dict[str, Any]] = []
    ontologies = index_payload.get("ontologies", {})
    if not isinstance(ontologies, dict):
        return rows

    for other_name, meta in ontologies.items():
        if str(other_name) == kb_name or not isinstance(meta, dict):
            continue
        other_set = {str(x) for x in meta.get("predicate_signatures", [])}
        union_size = len(current | other_set)
        overlap_size = len(current & other_set)
        similarity = 1.0 if union_size == 0 else overlap_size / union_size
        rows.append(
            {
                "ontology_name": str(other_name),
                "similarity": round(similarity, 4),
                "shared_signatures": sorted(current & other_set),
                "other_signature_count": len(other_set),
            }
        )

    rows.sort(key=lambda item: item["similarity"], reverse=True)
    return rows[:max_matches]


def _update_ontology_index(
    path: Path,
    kb_name: str,
    kb_dir: Path,
    profile: dict[str, Any],
) -> dict[str, Any]:
    payload = _load_ontology_index(path)
    ontologies = payload.setdefault("ontologies", {})
    ontologies[kb_name] = {
        "ontology_name": kb_name,
        "kb_dir": str(kb_dir),
        "updated_at_utc": _utc_now_iso(),
        "predicate_signatures": profile.get("predicate_signatures", []),
        "clause_count": profile.get("clause_count", 0),
    }
    _write_json(path, payload)
    return payload


def _constraint_error_result(
    *,
    message: str,
    errors: list[str],
    unknown_signatures: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "status": "constraint_error",
        "result_type": "constraint_error",
        "message": message,
        "errors": errors,
        "unknown_signatures": unknown_signatures or [],
    }


def _runtime_constraint_check(
    *,
    parsed_fragment: dict[str, Any],
    registry_signatures: set[str],
    strict_registry: bool,
    type_schema: dict[str, Any],
    strict_types: bool,
) -> dict[str, Any] | None:
    registry_errors, unknown_signatures = _validate_parsed_against_registry(
        parsed_fragment,
        allowed_signatures=registry_signatures,
        strict_registry=strict_registry,
    )
    type_errors = _validate_parsed_types(
        parsed_fragment,
        type_schema=type_schema,
        strict_types=strict_types,
    )
    errors = registry_errors + type_errors
    if not errors:
        return None
    return _constraint_error_result(
        message="Runtime constraint check failed for KB operation.",
        errors=errors,
        unknown_signatures=unknown_signatures,
    )


def _apply_to_kb(
    server: Any,
    parsed: dict[str, Any],
    *,
    corpus_clauses: set[str] | None = None,
    registry_signatures: set[str] | None = None,
    strict_registry: bool = False,
    type_schema: dict[str, Any] | None = None,
    strict_types: bool = False,
) -> dict[str, Any]:
    allowed_signatures = registry_signatures or set()
    schema = type_schema or {"entities": {}, "predicates": {}}
    intent = str(parsed.get("intent", "other"))
    if intent == "assert_fact":
        facts = parsed.get("facts", [])
        fact = _normalize_clause(str(facts[0]).strip() if facts else str(parsed.get("logic_string", "")).strip())
        constraint_issue = _runtime_constraint_check(
            parsed_fragment={
                "logic_string": fact,
                "facts": [fact],
                "rules": [],
                "queries": [],
            },
            registry_signatures=allowed_signatures,
            strict_registry=strict_registry,
            type_schema=schema,
            strict_types=strict_types,
        )
        if constraint_issue is not None:
            return {"tool": "assert_fact", "input": fact, "result": constraint_issue}
        if corpus_clauses is not None and fact in corpus_clauses:
            return {
                "tool": "assert_fact",
                "input": fact,
                "result": {"status": "skipped", "message": "Fact already present in corpus."},
            }
        result = server.assert_fact(fact)
        if corpus_clauses is not None and result.get("status") == "success":
            corpus_clauses.add(fact)
        return {"tool": "assert_fact", "input": fact, "result": result}
    if intent == "assert_rule":
        rules = parsed.get("rules", [])
        rule = _normalize_clause(str(rules[0]).strip() if rules else str(parsed.get("logic_string", "")).strip())
        constraint_issue = _runtime_constraint_check(
            parsed_fragment={
                "logic_string": rule,
                "facts": [],
                "rules": [rule],
                "queries": [],
            },
            registry_signatures=allowed_signatures,
            strict_registry=strict_registry,
            type_schema=schema,
            strict_types=strict_types,
        )
        if constraint_issue is not None:
            return {"tool": "assert_rule", "input": rule, "result": constraint_issue}
        if corpus_clauses is not None and rule in corpus_clauses:
            return {
                "tool": "assert_rule",
                "input": rule,
                "result": {"status": "skipped", "message": "Rule already present in corpus."},
            }
        result = server.assert_rule(rule)
        if corpus_clauses is not None and result.get("status") == "success":
            corpus_clauses.add(rule)
        return {"tool": "assert_rule", "input": rule, "result": result}
    if intent == "retract":
        target = _extract_retract_target(
            str(parsed.get("logic_string", "")),
            [str(x) for x in parsed.get("facts", [])],
        )
        if not target:
            return {
                "tool": "retract_fact",
                "input": None,
                "result": {"status": "validation_error", "message": "Could not derive retract target fact."},
            }
        target = _normalize_clause(target)
        retract_logic = f"retract({target[:-1] if target.endswith('.') else target})."
        constraint_issue = _runtime_constraint_check(
            parsed_fragment={
                "logic_string": retract_logic,
                "facts": [target],
                "rules": [],
                "queries": [],
            },
            registry_signatures=allowed_signatures,
            strict_registry=strict_registry,
            type_schema=schema,
            strict_types=strict_types,
        )
        if constraint_issue is not None:
            return {"tool": "retract_fact", "input": target, "result": constraint_issue}
        if corpus_clauses is not None and target not in corpus_clauses:
            return {
                "tool": "retract_fact",
                "input": target,
                "result": {"status": "no_results", "message": "Fact not present in corpus."},
            }
        result = server.retract_fact(target)
        if corpus_clauses is not None and result.get("status") in {"success", "no_results"}:
            corpus_clauses.discard(target)
        return {"tool": "retract_fact", "input": target, "result": result}
    if intent == "query":
        query = _normalize_clause(str(parsed.get("logic_string", "")).strip())
        constraint_issue = _runtime_constraint_check(
            parsed_fragment={
                "logic_string": query,
                "facts": [],
                "rules": [],
                "queries": [query],
            },
            registry_signatures=allowed_signatures,
            strict_registry=strict_registry,
            type_schema=schema,
            strict_types=strict_types,
        )
        if constraint_issue is not None:
            return {"tool": "query_rows", "input": query, "result": constraint_issue}
        return {"tool": "query_rows", "input": query, "result": server.query_rows(query)}
    return {
        "tool": "none",
        "input": None,
        "result": {"status": "skipped", "message": "Intent=other; no KB mutation/query applied."},
    }


def _run_validations(server: Any, validations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for idx, check in enumerate(validations, start=1):
        query = str(check.get("query", "")).strip()
        if not query:
            rows.append(
                {
                    "id": check.get("id", f"validation_{idx:02d}"),
                    "status": "validation_error",
                    "passed": False,
                    "message": "Missing query",
                }
            )
            continue
        result = server.query_rows(query)
        expected_status = str(check.get("expect_status", "success")).strip()
        min_rows = check.get("min_rows")
        max_rows = check.get("max_rows")
        contains_row = check.get("contains_row")

        passed = result.get("status") == expected_status
        reasons: list[str] = []
        if not passed:
            reasons.append(
                f"Expected status={expected_status}, observed={result.get('status')}"
            )

        num_rows = int(result.get("num_rows", 0) or 0)
        if min_rows is not None and num_rows < int(min_rows):
            passed = False
            reasons.append(f"num_rows {num_rows} < min_rows {int(min_rows)}")
        if max_rows is not None and num_rows > int(max_rows):
            passed = False
            reasons.append(f"num_rows {num_rows} > max_rows {int(max_rows)}")

        if isinstance(contains_row, dict):
            rows_data = result.get("rows", [])
            matched = False
            if isinstance(rows_data, list):
                for row in rows_data:
                    if not isinstance(row, dict):
                        continue
                    ok = True
                    for key, value in contains_row.items():
                        if str(row.get(key)) != str(value):
                            ok = False
                            break
                    if ok:
                        matched = True
                        break
            if not matched:
                passed = False
                reasons.append(f"Expected row not found: {contains_row}")

        rows.append(
            {
                "id": check.get("id", f"validation_{idx:02d}"),
                "query": query,
                "expected_status": expected_status,
                "result": result,
                "passed": passed,
                "reasons": reasons,
            }
        )
    return rows


def _skip_validations(validations: list[dict[str, Any]], reason: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for idx, check in enumerate(validations, start=1):
        rows.append(
            {
                "id": check.get("id", f"validation_{idx:02d}"),
                "query": str(check.get("query", "")).strip(),
                "expected_status": str(check.get("expect_status", "success")).strip(),
                "result": {
                    "status": "skipped",
                    "result_type": "skipped",
                    "reason": reason,
                    "num_rows": 0,
                    "rows": [],
                    "variables": [],
                },
                "passed": True,
                "reasons": [reason],
            }
        )
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build and validate a runtime KB from natural language using local 9B semantic parsing."
    )
    parser.add_argument(
        "--scenario",
        default="kb_scenarios/kb_positive.json",
        help="Scenario JSON path (utterances + validations).",
    )
    parser.add_argument(
        "--backend",
        choices=["lmstudio", "ollama"],
        default=DEFAULT_BACKEND,
        help="Model backend.",
    )
    parser.add_argument("--base-url", default="", help="Override backend base URL.")
    parser.add_argument("--model", default="", help="Override model id.")
    parser.add_argument("--context-length", type=int, default=4096, help="Context window for model calls.")
    parser.add_argument("--timeout-seconds", type=int, default=120, help="Network timeout per model call.")
    parser.add_argument(
        "--runtime",
        choices=["core", "none", "mcp"],
        default="core",
        help="Runtime apply mode. 'core' uses local vendored interpreter (default). 'none' is parse-only fallback. 'mcp' uses PrologMCPServer.",
    )
    parser.add_argument(
        "--prolog-repo",
        default="",
        help="Optional path containing src/mcp_server.py when --runtime mcp.",
    )
    parser.add_argument(
        "--kb-path",
        default="prolog/core.pl",
        help="KB path passed to PrologMCPServer when --runtime mcp (relative to --prolog-repo or absolute).",
    )
    parser.add_argument(
        "--kb-root",
        default=str(DEFAULT_KB_ROOT),
        help="Root folder where named ontology KBs are stored.",
    )
    parser.add_argument(
        "--kb-name",
        default="",
        help="Named ontology KB. Defaults to scenario ontology_name or scenario name.",
    )
    parser.add_argument(
        "--corpus-path",
        default="",
        help="Optional corpus .pl path. Relative paths resolve under the named KB directory.",
    )
    parser.add_argument(
        "--force-empty-kb",
        action="store_true",
        help="Force empty_kb() even for existing ontologies (danger: ignores retained runtime context).",
    )
    parser.add_argument(
        "--seed-from-kb-path",
        action="store_true",
        help="Use --kb-path as runtime bootstrap source (legacy mode). Default keeps bootstrap seedless.",
    )
    parser.add_argument(
        "--write-corpus-on-fail",
        action="store_true",
        help="Write corpus/profile even when validations fail.",
    )
    parser.add_argument(
        "--max-known-ontology-matches",
        type=int,
        default=5,
        help="How many known ontology similarity matches to include in report.",
    )
    parser.add_argument(
        "--predicate-registry",
        default=str(DEFAULT_PREDICATE_REGISTRY),
        help="Predicate registry JSON path (canonical names, arities, aliases).",
    )
    parser.add_argument(
        "--strict-registry",
        action="store_true",
        help="Reject parsed turns that use predicate signatures outside the registry.",
    )
    parser.add_argument(
        "--type-schema",
        default="",
        help="Optional type schema JSON path with entities + predicate arg type constraints.",
    )
    parser.add_argument(
        "--strict-types",
        action="store_true",
        help="Reject parsed turns when type constraints cannot be validated.",
    )
    parser.add_argument(
        "--prompt-file",
        default="modelfiles/semantic_parser_system_prompt.md",
        help="Optional markdown prompt guidance file to inject into classifier/extractor/repair prompts.",
    )
    parser.add_argument(
        "--prompt-history-dir",
        default=str(DEFAULT_PROMPT_HISTORY_DIR),
        help="Directory for immutable prompt snapshots used for run provenance.",
    )
    parser.add_argument(
        "--env-file",
        default="",
        help="Optional env file for API keys. Defaults to local .env.local when present.",
    )
    parser.add_argument(
        "--two-pass",
        action="store_true",
        default=True,
        help="Enable classifier+extractor two-pass parsing (default on).",
    )
    parser.add_argument(
        "--no-two-pass",
        action="store_true",
        help="Disable classifier pass and use heuristic route only.",
    )
    parser.add_argument(
        "--split-extraction",
        action="store_true",
        default=True,
        help="Use logic-only extraction then deterministic schema refinement (default on).",
    )
    parser.add_argument(
        "--no-split-extraction",
        action="store_true",
        help="Disable logic-only split extraction and use full-schema extraction directly.",
    )
    parser.add_argument(
        "--clarification-eagerness",
        type=float,
        default=0.35,
        help="Clarification eagerness in [0,1]. Higher asks clarification at lower uncertainty.",
    )
    parser.add_argument(
        "--max-clarification-rounds",
        type=int,
        default=2,
        help="Maximum clarification Q&A rounds per utterance before deferring KB apply.",
    )
    parser.add_argument("--out", default="", help="Optional output report JSON path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_started = datetime.now(timezone.utc).replace(microsecond=0)
    scenario_path = Path(args.scenario).resolve()
    if not scenario_path.exists():
        print(f"Scenario not found: {scenario_path}")
        return 2

    payload = json.loads(scenario_path.read_text(encoding="utf-8-sig"))
    utterances = payload.get("utterances", [])
    validations = payload.get("validations", [])
    if not isinstance(utterances, list) or not utterances:
        print("Scenario must include a non-empty 'utterances' list.")
        return 2
    if not isinstance(validations, list):
        validations = []

    kb_name_source = (
        args.kb_name.strip()
        or str(payload.get("ontology_name", "")).strip()
        or str(payload.get("name", scenario_path.stem)).strip()
    )
    kb_name = _normalize_kb_name(kb_name_source)
    kb_root = Path(args.kb_root).resolve()
    kb_dir = (kb_root / kb_name).resolve()
    profile_path = kb_dir / "ontology_profile.json"
    ontology_index_path = kb_root / "ontologies_index.json"
    if args.corpus_path.strip():
        raw_corpus = Path(args.corpus_path.strip())
        if not raw_corpus.is_absolute():
            raw_corpus = kb_dir / raw_corpus
        corpus_path = raw_corpus.resolve()
    else:
        corpus_path = (kb_dir / "kb.pl").resolve()

    existing_corpus_clauses = _read_corpus_clauses(corpus_path)
    existing_profile = _load_json(profile_path)
    corpus_exists = corpus_path.exists()
    is_brand_new_ontology = (not corpus_exists) and (not existing_profile)

    prompt_file_path = Path(args.prompt_file)
    if not prompt_file_path.is_absolute():
        prompt_file_path = (Path.cwd() / prompt_file_path).resolve()
    prompt_guide = _load_prompt_guide(prompt_file_path)

    predicate_registry_path = Path(args.predicate_registry)
    if not predicate_registry_path.is_absolute():
        predicate_registry_path = (Path.cwd() / predicate_registry_path).resolve()
    predicate_registry = _load_predicate_registry(predicate_registry_path)
    registry_alias_map = _build_registry_alias_map(predicate_registry)
    registry_signatures = _build_registry_signature_set(predicate_registry)

    type_schema_path: Path | None = None
    if args.type_schema.strip():
        type_schema_path = Path(args.type_schema.strip())
        if not type_schema_path.is_absolute():
            type_schema_path = (Path.cwd() / type_schema_path).resolve()
    type_schema = _load_type_schema(type_schema_path) if isinstance(type_schema_path, Path) else {"entities": {}, "predicates": {}}

    runtime_mode = str(args.runtime).strip().lower()
    prolog_repo: Path | None = None
    if runtime_mode == "mcp":
        prolog_repo = _resolve_prolog_repo(args.prolog_repo)
        if prolog_repo is None:
            print("runtime=mcp requested but no Prolog MCP repo was found.")
            print(
                "Provide --prolog-repo (containing src/mcp_server.py), "
                "set PRETHINKER_PROLOG_REPO, or run with --runtime core."
            )
            return 2

    env_file_path = _resolve_env_file(args.env_file, prolog_repo)
    if env_file_path is not None:
        _load_env_file(env_file_path)
    api_key = _get_api_key()

    backend = args.backend
    base_url = args.base_url.strip() or DEFAULT_BASE_URLS[backend]
    model = args.model.strip() or DEFAULT_MODELS[backend]
    use_two_pass = bool(args.two_pass and not args.no_two_pass)
    use_split_extraction = bool(args.split_extraction and not args.no_split_extraction)
    clarification_eagerness = _clip_01(args.clarification_eagerness, fallback=0.35)
    max_clarification_rounds = max(0, int(args.max_clarification_rounds))
    prompt_history_dir = Path(args.prompt_history_dir)
    if not prompt_history_dir.is_absolute():
        prompt_history_dir = (Path.cwd() / prompt_history_dir).resolve()
    prompt_provenance = _snapshot_prompt_version(
        prompt_file_path=prompt_file_path,
        prompt_text=prompt_guide,
        history_dir=prompt_history_dir,
    )
    scenario_slug = _atomize(str(payload.get("name", scenario_path.stem))) or "scenario"
    model_slug = _atomize(model) or "model"
    run_id = f"run-{run_started.strftime('%Y%m%dT%H%M%SZ')}-{scenario_slug[:24]}-{model_slug[:20]}-{os.getpid()}"
    model_settings = {
        "temperature": 0,
        "context_length": args.context_length,
        "classifier_context_length": 2048,
        "timeout_seconds": args.timeout_seconds,
        "runtime": runtime_mode,
        "two_pass": use_two_pass,
        "split_extraction": use_split_extraction,
        "strict_registry": bool(args.strict_registry),
        "strict_types": bool(args.strict_types),
        "clarification_eagerness": clarification_eagerness,
        "max_clarification_rounds": max_clarification_rounds,
        "backend_options": {"num_ctx": args.context_length} if backend == "ollama" else {},
    }

    server: Any
    if runtime_mode == "mcp":
        assert prolog_repo is not None
        src_path = prolog_repo / "src"
        if not src_path.exists():
            print(f"prolog-reasoning src not found: {src_path}")
            return 2
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))

        from mcp_server import PrologMCPServer  # pylint: disable=import-outside-toplevel

        base_kb_path = Path(args.kb_path)
        if not base_kb_path.is_absolute():
            base_kb_path = (prolog_repo / base_kb_path).resolve()

        if args.seed_from_kb_path:
            server_boot_kb_path = base_kb_path
        elif corpus_exists:
            server_boot_kb_path = corpus_path
        else:
            bootstrap_path = (kb_dir / "_bootstrap_empty.pl").resolve()
            if not bootstrap_path.exists():
                bootstrap_path.parent.mkdir(parents=True, exist_ok=True)
                bootstrap_path.write_text("% Seedless bootstrap KB for named ontology runtime.\n", encoding="utf-8")
            server_boot_kb_path = bootstrap_path

        server = PrologMCPServer(kb_path=str(server_boot_kb_path))
    elif runtime_mode == "core":
        if corpus_exists:
            server_boot_kb_path = corpus_path
        else:
            server_boot_kb_path = (kb_dir / "_bootstrap_core.pl").resolve()
        server = CorePrologRuntime()
    else:
        if corpus_exists:
            server_boot_kb_path = corpus_path
        else:
            server_boot_kb_path = (kb_dir / "_bootstrap_parse_only.pl").resolve()
        server = ParseOnlyRuntime()

    should_empty = bool(args.force_empty_kb or is_brand_new_ontology)
    if should_empty:
        kb_init = server.empty_kb()
        if kb_init.get("status") != "success":
            print("empty_kb() failed; aborting.")
            print(json.dumps(kb_init, indent=2))
            return 1
    else:
        kb_init = {
            "status": "skipped",
            "result_type": "not_called",
            "message": "Existing ontology retained; empty_kb() not invoked.",
            "knowledge_base_path": str(server_boot_kb_path),
        }

    corpus_clauses: set[str] = {
        _normalize_clause(item)
        for item in existing_corpus_clauses
        if _normalize_clause(item)
    }
    if corpus_clauses:
        corpus_load = _load_corpus_into_server(server, sorted(corpus_clauses))
    else:
        corpus_load = {
            "status": "skipped",
            "loaded_total": 0,
            "message": "No retained corpus to preload.",
        }

    print(f"Scenario: {payload.get('name', scenario_path.stem)}")
    print(f"Ontology KB: {kb_name}")
    print(f"KB dir: {kb_dir}")
    print(f"Corpus path: {corpus_path}")
    print(f"Backend: {backend} @ {base_url}")
    print(f"Model: {model}")
    print(f"Runtime: {runtime_mode}")
    print(f"Two-pass: {use_two_pass}")
    print(f"Split extraction: {use_split_extraction}")
    print(
        f"Clarification policy: eagerness={clarification_eagerness:.2f} "
        f"max_rounds={max_clarification_rounds}"
    )
    print(f"Prompt file: {prompt_file_path} ({'loaded' if prompt_guide else 'not found/empty'})")
    if env_file_path is not None:
        print(f"Env file: {env_file_path}")
    else:
        print("Env file: (none)")
    print(
        "Prompt provenance: "
        f"id={prompt_provenance.get('prompt_id') or '(none)'} "
        f"snapshot={prompt_provenance.get('snapshot_path') or '(none)'}"
    )
    print(
        f"Predicate registry: {predicate_registry_path} "
        f"(entries={len(registry_signatures)} strict={bool(args.strict_registry)})"
    )
    print(
        f"Type schema: "
        f"{(str(type_schema_path) if type_schema_path else '(none)')} "
        f"(predicates={len(type_schema.get('predicates', {}))} strict={bool(args.strict_types)})"
    )
    print(f"KB init: {kb_init.get('status')} ({kb_init.get('message', kb_init.get('result_type', ''))})")
    print(
        "Corpus preload: "
        f"{corpus_load.get('status')} (loaded_total={corpus_load.get('loaded_total', 0)})"
    )

    turn_rows: list[dict[str, Any]] = []
    for idx, raw in enumerate(utterances, start=1):
        utterance, scripted_clarification_answers, entry_max_rounds = _coerce_utterance_entry(raw)
        if not utterance:
            continue

        per_turn_max_rounds = (
            max_clarification_rounds
            if entry_max_rounds is None
            else max(0, int(entry_max_rounds))
        )
        clarification_rounds: list[dict[str, Any]] = []
        scripted_answer_index = 0
        clarification_pending = False
        clarification_pending_reason = ""
        clarification_question = ""
        clarification_policy = {
            "clarification_eagerness": clarification_eagerness,
            "uncertainty_score": 0.0,
            "effective_uncertainty": 0.0,
            "threshold": round(max(0.05, 1.0 - clarification_eagerness), 3),
            "request_clarification": False,
            "needs_clarification_flag": False,
        }

        parsed: dict[str, Any] | None = None
        parsed_text = ""
        route = "other"
        route_source = "heuristic"
        repaired = False
        fallback_used = False
        validation_errors: list[str] = []
        alignment_events: list[dict[str, Any]] = []
        registry_unknown_signatures: list[str] = []

        while True:
            turn_input_text = _build_clarification_context_utterance(utterance, clarification_rounds)
            heuristic = _heuristic_route(turn_input_text)
            route = heuristic
            route_source = "heuristic"
            repaired = False
            fallback_used = False
            validation_errors = []
            alignment_events = []
            registry_unknown_signatures = []

            runtime_constraint_guide = _build_runtime_constraint_guide(
                registry_signatures=registry_signatures,
                strict_registry=bool(args.strict_registry),
                type_schema=type_schema,
                strict_types=bool(args.strict_types),
            )
            turn_prompt_guide = (
                f"{prompt_guide}\n\n{runtime_constraint_guide}".strip()
                if runtime_constraint_guide
                else prompt_guide
            )

            if use_two_pass and heuristic == "assert_fact":
                cls_prompt = _build_classifier_prompt(turn_input_text, prompt_guide=turn_prompt_guide)
                cls_resp = _call_model_prompt(
                    backend=backend,
                    base_url=base_url,
                    model=model,
                    prompt_text=cls_prompt,
                    context_length=2048,
                    timeout=args.timeout_seconds,
                    api_key=api_key,
                )
                cls_json, _ = _parse_model_json(cls_resp, required_keys=["route"])
                if isinstance(cls_json, dict):
                    candidate = str(cls_json.get("route", "")).strip()
                    if candidate in {"assert_fact", "assert_rule", "query", "retract", "other"}:
                        route = candidate
                        route_source = "model"

            known_predicates = _known_predicate_names_from_corpus(corpus_clauses)
            if use_split_extraction:
                ext_prompt = _build_logic_only_extractor_prompt(
                    turn_input_text,
                    route,
                    known_predicates=known_predicates,
                    prompt_guide=turn_prompt_guide,
                )
                required_keys = ["intent", "logic_string", "confidence"]
            else:
                ext_prompt = _build_extractor_prompt(
                    turn_input_text,
                    route,
                    known_predicates=known_predicates,
                    prompt_guide=turn_prompt_guide,
                )
                required_keys = ["intent", "logic_string", "components", "confidence"]
            ext_resp = _call_model_prompt(
                backend=backend,
                base_url=base_url,
                model=model,
                prompt_text=ext_prompt,
                context_length=args.context_length,
                timeout=args.timeout_seconds,
                api_key=api_key,
            )
            parsed, parsed_text = _parse_model_json(ext_resp, required_keys=required_keys)
            if use_split_extraction and isinstance(parsed, dict):
                parsed = _normalize_clarification_fields(parsed, utterance=utterance, route=route)
                refined = _refine_logic_only_payload(
                    parsed,
                    route,
                    utterance=utterance,
                )
                if isinstance(refined, dict):
                    parsed = refined
                    parsed_text = json.dumps(refined)
                else:
                    parsed = None
                    parsed_text = ""

            if not isinstance(parsed, dict):
                if use_split_extraction:
                    # Second prompt: full-schema refiner fallback when logic-only pass is insufficient.
                    full_prompt = _build_extractor_prompt(
                        turn_input_text,
                        route,
                        known_predicates=known_predicates,
                        prompt_guide=turn_prompt_guide,
                    )
                    full_resp = _call_model_prompt(
                        backend=backend,
                        base_url=base_url,
                        model=model,
                        prompt_text=full_prompt,
                        context_length=args.context_length,
                        timeout=args.timeout_seconds,
                        api_key=api_key,
                    )
                    parsed, parsed_text = _parse_model_json(
                        full_resp,
                        required_keys=["intent", "logic_string", "components", "confidence"],
                    )
                    if isinstance(parsed, dict):
                        parsed = _normalize_clarification_fields(parsed, utterance=utterance, route=route)
                validation_errors = ["Model did not return parseable JSON payload."]
                if isinstance(parsed, dict):
                    parsed = _normalize_clarification_fields(parsed, utterance=utterance, route=route)
                    ok_full, errors_full = _validate_parsed(parsed)
                    if ok_full:
                        validation_errors = []
                    else:
                        validation_errors = errors_full
                if validation_errors:
                    fallback_parsed = _build_route_fallback_parse(route, utterance)
                    if isinstance(fallback_parsed, dict):
                        fallback_parsed = _normalize_clarification_fields(
                            fallback_parsed,
                            utterance=utterance,
                            route=route,
                        )
                        parsed = fallback_parsed
                        validation_errors = []
                        fallback_used = True
            else:
                parsed = _normalize_clarification_fields(parsed, utterance=utterance, route=route)
                ok, errors = _validate_parsed(parsed)
                validation_errors = errors
                if not ok:
                    repair_prompt = _build_repair_prompt(
                        turn_input_text,
                        route,
                        parsed_text or json.dumps(parsed),
                        errors,
                        prompt_guide=turn_prompt_guide,
                    )
                    repair_resp = _call_model_prompt(
                        backend=backend,
                        base_url=base_url,
                        model=model,
                        prompt_text=repair_prompt,
                        context_length=args.context_length,
                        timeout=args.timeout_seconds,
                        api_key=api_key,
                    )
                    repaired_json, repaired_text = _parse_model_json(
                        repair_resp,
                        required_keys=["intent", "logic_string", "components", "confidence"],
                    )
                    if isinstance(repaired_json, dict):
                        repaired_json = _normalize_clarification_fields(
                            repaired_json,
                            utterance=utterance,
                            route=route,
                        )
                        ok2, errors2 = _validate_parsed(repaired_json)
                        if ok2:
                            parsed = repaired_json
                            parsed_text = repaired_text
                            validation_errors = []
                            repaired = True
                        else:
                            validation_errors = errors2
                    if validation_errors:
                        fallback_parsed = _build_route_fallback_parse(route, utterance)
                        if isinstance(fallback_parsed, dict):
                            fallback_parsed = _normalize_clarification_fields(
                                fallback_parsed,
                                utterance=utterance,
                                route=route,
                            )
                            parsed = fallback_parsed
                            validation_errors = []
                            fallback_used = True

            if isinstance(parsed, dict) and not validation_errors:
                parsed, alignment_events = _align_parsed_predicates(parsed, registry_alias_map)
                parsed = _normalize_clarification_fields(parsed, utterance=utterance, route=route)
                registry_errors, unknown_signatures = _validate_parsed_against_registry(
                    parsed,
                    allowed_signatures=registry_signatures,
                    strict_registry=bool(args.strict_registry),
                )
                registry_unknown_signatures = unknown_signatures
                if registry_errors:
                    validation_errors.extend(registry_errors)
                type_errors = _validate_parsed_types(
                    parsed,
                    type_schema=type_schema,
                    strict_types=bool(args.strict_types),
                )
                if type_errors:
                    validation_errors.extend(type_errors)

            if not isinstance(parsed, dict) or validation_errors:
                break

            clarification_policy = _clarification_policy_decision(
                parsed=parsed,
                clarification_eagerness=clarification_eagerness,
            )
            clarification_question = str(parsed.get("clarification_question", "")).strip()
            if not clarification_question:
                clarification_question = _synthesize_clarification_question(
                    utterance=utterance,
                    route=route,
                    ambiguities=parsed.get("ambiguities", []) if isinstance(parsed.get("ambiguities"), list) else [],
                    reason=str(parsed.get("clarification_reason", "")).strip(),
                )
                parsed["clarification_question"] = clarification_question

            if not clarification_policy.get("request_clarification"):
                break

            has_round_capacity = len(clarification_rounds) < per_turn_max_rounds
            has_scripted_answer = scripted_answer_index < len(scripted_clarification_answers)
            if has_round_capacity and has_scripted_answer:
                scripted_answer = scripted_clarification_answers[scripted_answer_index]
                scripted_answer_index += 1
                clarification_rounds.append(
                    {
                        "round": len(clarification_rounds) + 1,
                        "question": clarification_question,
                        "answer": scripted_answer,
                        "uncertainty_score": clarification_policy.get("uncertainty_score"),
                        "effective_uncertainty": clarification_policy.get("effective_uncertainty"),
                        "threshold": clarification_policy.get("threshold"),
                    }
                )
                continue

            clarification_pending = True
            if not has_round_capacity:
                clarification_pending_reason = "Maximum clarification rounds reached for this utterance."
            else:
                clarification_pending_reason = "No clarification answer available for the generated question."
            break

        apply_row: dict[str, Any]
        if clarification_pending and isinstance(parsed, dict) and not validation_errors:
            apply_row = {
                "tool": "none",
                "input": {
                    "clarification_question": clarification_question,
                    "clarification_rounds_used": len(clarification_rounds),
                },
                "result": {
                    "status": "clarification_requested",
                    "message": clarification_pending_reason or "Clarification required before KB apply.",
                    "clarification_question": clarification_question,
                    "clarification_policy": clarification_policy,
                },
            }
        elif not isinstance(parsed, dict) or validation_errors:
            apply_row = {
                "tool": "none",
                "input": None,
                "result": {
                    "status": "validation_error",
                    "message": "Skipping KB apply due to parser validation failure.",
                },
            }
        else:
            apply_row = _apply_to_kb(
                server,
                parsed,
                corpus_clauses=corpus_clauses,
                registry_signatures=registry_signatures,
                strict_registry=bool(args.strict_registry),
                type_schema=type_schema,
                strict_types=bool(args.strict_types),
            )

        tool_result = apply_row.get("result", {})
        apply_status = str(tool_result.get("status", "unknown"))
        turn_rows.append(
            {
                "turn_index": idx,
                "utterance": utterance,
                "route": route,
                "route_source": route_source,
                "repaired": repaired,
                "fallback_used": fallback_used,
                "alignment_events": alignment_events,
                "registry_unknown_signatures": registry_unknown_signatures,
                "parsed": parsed,
                "validation_errors": validation_errors,
                "clarification_rounds": clarification_rounds,
                "clarification_rounds_used": len(clarification_rounds),
                "clarification_max_rounds": per_turn_max_rounds,
                "clarification_answers_available": len(scripted_clarification_answers),
                "clarification_answers_used": scripted_answer_index,
                "clarification_policy": clarification_policy,
                "clarification_pending": clarification_pending,
                "clarification_pending_reason": clarification_pending_reason,
                "clarification_question": clarification_question,
                "apply": apply_row,
                "apply_status": apply_status,
            }
        )

        if apply_status == "clarification_requested":
            status_note = "clarification"
        else:
            status_note = "ok" if not validation_errors and apply_status in {"success", "skipped", "no_results"} else "issue"
        print(
            f"[turn {idx:02d}] route={route} source={route_source} repaired={repaired} fallback={fallback_used} "
            f"clar_rounds={len(clarification_rounds)} apply_tool={apply_row.get('tool')} "
            f"apply_status={apply_status} [{status_note}]"
        )

    if runtime_mode in {"mcp", "core"}:
        validation_rows = _run_validations(server, validations)
    else:
        validation_rows = _skip_validations(
            validations,
            "Skipped: runtime=none (parse-only mode).",
        )
    validation_pass = sum(1 for row in validation_rows if row.get("passed"))
    validation_total = len(validation_rows)
    parse_fail_count = sum(1 for row in turn_rows if row.get("validation_errors"))
    apply_fail_count = sum(
        1
        for row in turn_rows
        if str(row.get("apply_status")) not in {"success", "skipped", "no_results", "clarification_requested"}
    )
    clarification_requests = sum(
        1 for row in turn_rows if str(row.get("apply_status")) == "clarification_requested"
    )
    clarification_rounds_total = sum(
        int(row.get("clarification_rounds_used", 0)) for row in turn_rows
    )

    overall_ok = parse_fail_count == 0 and apply_fail_count == 0 and validation_pass == validation_total
    current_profile = _build_ontology_profile(kb_name, corpus_clauses)
    ontology_diff = _compare_ontology_profiles(existing_profile, current_profile)
    known_index_before = _load_ontology_index(ontology_index_path)
    known_matches = _compute_known_ontology_matches(
        kb_name,
        current_profile,
        known_index_before,
        max_matches=max(1, int(args.max_known_ontology_matches)),
    )
    gear_change = {
        "change_level": ontology_diff.get("change_level"),
        "detected": ontology_diff.get("change_level") in {"major", "moderate"},
        "requires_confirmation": ontology_diff.get("requires_confirmation"),
    }

    should_write_artifacts = bool(overall_ok or args.write_corpus_on_fail)
    if should_write_artifacts:
        corpus_write = _write_corpus_clauses(corpus_path, corpus_clauses)
        _write_json(profile_path, current_profile)
        index_payload = _update_ontology_index(ontology_index_path, kb_name, kb_dir, current_profile)
        profile_write = {
            "status": "written",
            "path": str(profile_path),
            "predicate_signature_count": len(current_profile.get("predicate_signatures", [])),
        }
        index_write = {
            "status": "written",
            "path": str(ontology_index_path),
            "ontology_count": len(index_payload.get("ontologies", {})),
        }
    else:
        corpus_write = {
            "status": "skipped",
            "path": str(corpus_path),
            "reason": "Run failed. Use --write-corpus-on-fail to persist anyway.",
        }
        profile_write = {
            "status": "skipped",
            "path": str(profile_path),
            "reason": "Run failed. Use --write-corpus-on-fail to persist anyway.",
        }
        index_write = {
            "status": "skipped",
            "path": str(ontology_index_path),
            "reason": "Run failed. Use --write-corpus-on-fail to persist anyway.",
        }

    run_finished = datetime.now(timezone.utc).replace(microsecond=0)
    report = {
        "run_id": run_id,
        "run_started_utc": run_started.isoformat(),
        "run_finished_utc": run_finished.isoformat(),
        "invocation": {
            "argv": sys.argv,
            "cwd": str(Path.cwd()),
        },
        "scenario": payload.get("name", scenario_path.stem),
        "scenario_path": str(scenario_path),
        "ontology_kb_name": kb_name,
        "kb_namespace": {
            "kb_root": str(kb_root),
            "kb_dir": str(kb_dir),
            "corpus_path": str(corpus_path),
            "profile_path": str(profile_path),
            "ontology_index_path": str(ontology_index_path),
        },
        "backend": backend,
        "base_url": base_url,
        "model": model,
        "runtime": runtime_mode,
        "two_pass": use_two_pass,
        "split_extraction": use_split_extraction,
        "model_settings": model_settings,
        "prompt_file": str(prompt_file_path),
        "prompt_file_loaded": bool(prompt_guide),
        "env_file_loaded": str(env_file_path) if env_file_path is not None else "",
        "prompt_provenance": prompt_provenance,
        "system_prompt_text": prompt_guide,
        "kb_runtime_boot_path": str(server_boot_kb_path),
        "kb_init": kb_init,
        "corpus_load": corpus_load,
        "corpus_write": corpus_write,
        "profile_write": profile_write,
        "index_write": index_write,
        "ontology_profile": current_profile,
        "ontology_previous_profile": existing_profile,
        "ontology_diff": ontology_diff,
        "known_ontology_matches": known_matches,
        "gear_change": gear_change,
        "turns_total": len(turn_rows),
        "turn_parse_failures": parse_fail_count,
        "turn_apply_failures": apply_fail_count,
        "turns_clarification_requested": clarification_requests,
        "clarification_rounds_total": clarification_rounds_total,
        "validation_total": validation_total,
        "validation_passed": validation_pass,
        "overall_status": "passed" if overall_ok else "failed",
        "turns": turn_rows,
        "validations": validation_rows,
    }

    print("")
    print(f"Validation: {validation_pass}/{validation_total} passed")
    print(f"Parser failures: {parse_fail_count}")
    print(f"Apply failures: {apply_fail_count}")
    print(f"Clarification requests: {clarification_requests} (rounds={clarification_rounds_total})")
    print(
        "Ontology drift: "
        f"{ontology_diff.get('change_level')} "
        f"(requires_confirmation={ontology_diff.get('requires_confirmation')})"
    )
    print(f"Run id: {run_id}")
    print(f"Overall: {report['overall_status']}")
    if corpus_write.get("status") == "written":
        print(f"Corpus updated: {corpus_write.get('path')}")
    else:
        print(f"Corpus update skipped: {corpus_write.get('reason')}")

    if args.out:
        out_path = Path(args.out).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"Report written: {out_path}")

    return 0 if overall_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
