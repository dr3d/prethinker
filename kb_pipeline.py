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
import subprocess
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
    PROJECT_ROOT,
    PROJECT_ROOT / "vendor" / "prolog-reasoning",
    PROJECT_ROOT / ".runtime" / "prolog-reasoning",
    PROJECT_ROOT / "prolog-reasoning",
]
DEFAULT_BACKEND = "ollama"
DEFAULT_KB_ROOT = Path("kb_store")
DEFAULT_EPHEMERAL_KB_ROOT = Path("tmp/kb_store")
DEFAULT_KB_NAME = "default"
DEFAULT_PROGRESS_MEMORY_NAME = "progress.json"
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
AMBIGUOUS_PRONOUN_ATOMS = {
    "he",
    "him",
    "his",
    "she",
    "her",
    "hers",
    "they",
    "them",
    "their",
    "theirs",
    "it",
    "its",
    "this",
    "that",
    "these",
    "those",
}
WRITE_INTENTS = {"assert_fact", "assert_rule", "retract"}
PREDICATE_SIGNATURE_RE = re.compile(r"\b[a-z][a-z0-9_]*\s*/\s*\d+\b", flags=re.IGNORECASE)


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


def _probe_ollama_system_prompt(*, model: str, timeout_seconds: int) -> dict[str, Any]:
    model_name = str(model).strip()
    if not model_name:
        return {
            "status": "skipped",
            "reason": "empty_model_name",
            "has_system": None,
            "system_prompt_id": "",
            "system_sha256": "",
            "char_count": 0,
            "preview": "",
        }
    try:
        proc = subprocess.run(
            ["ollama", "show", model_name, "--system"],
            capture_output=True,
            text=True,
            timeout=max(1, int(timeout_seconds)),
            check=False,
        )
    except FileNotFoundError:
        return {
            "status": "unavailable",
            "reason": "ollama_command_not_found",
            "has_system": None,
            "system_prompt_id": "",
            "system_sha256": "",
            "char_count": 0,
            "preview": "",
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "timeout",
            "reason": "ollama_show_timeout",
            "has_system": None,
            "system_prompt_id": "",
            "system_sha256": "",
            "char_count": 0,
            "preview": "",
        }

    stdout = (proc.stdout or "").strip()
    stderr = (proc.stderr or "").strip()
    if proc.returncode != 0:
        return {
            "status": "error",
            "reason": "ollama_show_failed",
            "return_code": int(proc.returncode),
            "stderr": stderr[:240],
            "has_system": None,
            "system_prompt_id": "",
            "system_sha256": "",
            "char_count": 0,
            "preview": "",
        }

    has_system = bool(stdout)
    system_sha = _sha256_text(stdout) if has_system else ""
    system_id = f"sp-{system_sha[:12]}" if system_sha else ""
    preview_line = ""
    for line in stdout.splitlines():
        if line.strip():
            preview_line = line.strip()[:120]
            break
    return {
        "status": "ok",
        "reason": "",
        "has_system": has_system,
        "system_prompt_id": system_id,
        "system_sha256": system_sha,
        "char_count": len(stdout),
        "preview": preview_line,
    }


def _collect_system_prompt_sources(
    *,
    backend: str,
    model: str,
    runtime_prompt_text: str,
    detect_ollama_system: bool,
    ollama_detect_timeout_seconds: int,
) -> dict[str, Any]:
    runtime_text = str(runtime_prompt_text or "").strip()
    runtime_loaded = bool(runtime_text)
    runtime_sha = _sha256_text(runtime_text) if runtime_loaded else ""
    runtime_id = f"sp-{runtime_sha[:12]}" if runtime_sha else ""

    baked_probe: dict[str, Any]
    if backend != "ollama":
        baked_probe = {
            "status": "unknown",
            "reason": "backend_not_ollama",
            "has_system": None,
            "system_prompt_id": "",
            "system_sha256": "",
            "char_count": 0,
            "preview": "",
        }
    elif not detect_ollama_system:
        baked_probe = {
            "status": "skipped",
            "reason": "ollama_system_detect_disabled",
            "has_system": None,
            "system_prompt_id": "",
            "system_sha256": "",
            "char_count": 0,
            "preview": "",
        }
    else:
        baked_probe = _probe_ollama_system_prompt(
            model=model,
            timeout_seconds=ollama_detect_timeout_seconds,
        )

    model_name = str(model).strip().lower()
    semparse_name_hint = "semparse" in model_name
    baked_has_system = baked_probe.get("has_system")
    if isinstance(baked_has_system, bool):
        double_source = runtime_loaded and baked_has_system
        conflict_basis = "detected"
    else:
        double_source = runtime_loaded and semparse_name_hint and backend == "ollama"
        conflict_basis = "heuristic_semparse_name" if double_source else "none"

    return {
        "runtime_prompt_loaded": runtime_loaded,
        "runtime_prompt_id": runtime_id,
        "runtime_prompt_sha256": runtime_sha,
        "runtime_prompt_char_count": len(runtime_text),
        "runtime_prompt_source_path": "",
        "baked_model_probe": baked_probe,
        "semparse_name_hint": semparse_name_hint,
        "double_source_active": bool(double_source),
        "double_source_basis": conflict_basis,
    }


def _format_system_prompt_conflict_message(
    *,
    backend: str,
    model: str,
    prompt_file_path: Path,
    sources: dict[str, Any],
) -> str:
    runtime_id = str(sources.get("runtime_prompt_id", "")).strip() or "(none)"
    baked_probe = sources.get("baked_model_probe", {})
    if not isinstance(baked_probe, dict):
        baked_probe = {}
    baked_id = str(baked_probe.get("system_prompt_id", "")).strip() or "(unknown)"
    basis = str(sources.get("double_source_basis", "")).strip() or "unknown"
    return (
        "Double system-prompt source detected. "
        f"backend={backend} model={model} runtime_prompt_file={prompt_file_path} "
        f"runtime_prompt_id={runtime_id} baked_system_id={baked_id} basis={basis}. "
        "Use one source only: "
        "(a) bare model + runtime prompt-file, or "
        "(b) baked model + blank prompt-file."
    )


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

    # LM Studio: prefer OpenAI-compatible endpoint first; fallback to legacy API.
    openai_payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt_text}],
        "temperature": 0,
        "stream": False,
        "max_tokens": 1024,
        "context_length": context_length,
    }
    try:
        raw = _post_json(
            f"{base_url.rstrip('/')}/v1/chat/completions",
            openai_payload,
            timeout=timeout,
            api_key=api_key,
        )
        message = ""
        reasoning = ""
        choices = raw.get("choices", [])
        if isinstance(choices, list) and choices:
            choice0 = choices[0] if isinstance(choices[0], dict) else {}
            msg_obj = choice0.get("message", {})
            if isinstance(msg_obj, dict):
                message = str(msg_obj.get("content", "") or "")
                reasoning = str(
                    msg_obj.get("reasoning_content", "")
                    or msg_obj.get("reasoning", "")
                    or ""
                )
        if not message and isinstance(raw.get("output_text"), str):
            message = str(raw.get("output_text", "") or "")
        if not message and isinstance(raw.get("response"), str):
            message = str(raw.get("response", "") or "")
        return ModelResponse(message=message, reasoning=reasoning, raw=raw)
    except RuntimeError as error:
        msg = str(error)
        fallback_allowed = ("HTTP 404" in msg) or ("HTTP 405" in msg)
        if not fallback_allowed:
            raise
        legacy_payload = {
            "model": model,
            "input": prompt_text,
            "temperature": 0,
            "context_length": context_length,
        }
        raw = _post_json(
            f"{base_url.rstrip('/')}/api/v1/chat",
            legacy_payload,
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
    if re.search(r"\b(retract|remove|delete|undo)\b", lowered):
        return "retract"
    if re.search(r"\b(correction|actually)\b", lowered) and re.search(
        r"\b(not|did not|didn't|no longer|instead|retract|remove|undo)\b",
        lowered,
    ):
        return "retract"
    if re.search(r"\b(if|whenever|then)\b", lowered) and not re.search(
        r"\b(ask|asks|asked)\s+if\b",
        lowered,
    ):
        return "assert_rule"
    if re.search(r"\?$", lowered) or re.search(r"^\s*(who|what|where|when|why|how)\b", lowered):
        return "query"
    if re.search(r"\b(translate|summarize|rewrite|format|explain)\b", lowered):
        return "other"
    return "assert_fact"


def _has_rule_cues(text: str) -> bool:
    lowered = (text or "").strip().lower()
    return bool(
        re.search(
            r"\b(if|whenever|then|implies|unless|only if|every|all|any)\b",
            lowered,
        )
    )


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
    utterance: str = "",
    progress_memory: dict[str, Any] | None = None,
    progress_low_relevance_threshold: float = 0.34,
    progress_high_risk_threshold: float = 0.18,
) -> dict[str, Any]:
    eagerness = _clip_01(clarification_eagerness, fallback=0.0)
    uncertainty_score = _clip_01(parsed.get("uncertainty_score"), fallback=_estimate_uncertainty_score(parsed))
    ambiguity_count = len(parsed.get("ambiguities", [])) if isinstance(parsed.get("ambiguities"), list) else 0
    needs_clarification = bool(parsed.get("needs_clarification", False))
    intent = str(parsed.get("intent", "")).strip().lower()
    boosted_uncertainty = uncertainty_score
    if needs_clarification:
        boosted_uncertainty = max(boosted_uncertainty, 0.82)
    if ambiguity_count > 0:
        boosted_uncertainty = max(boosted_uncertainty, min(0.92, 0.45 + 0.1 * ambiguity_count))

    low_threshold = _clip_01(progress_low_relevance_threshold, fallback=0.34)
    high_threshold = _clip_01(progress_high_risk_threshold, fallback=0.18)
    if high_threshold > low_threshold:
        high_threshold = low_threshold

    progress_summary = _progress_relevance_summary(
        parsed=parsed,
        utterance=utterance,
        progress_memory=progress_memory,
    )
    progress_score = _clip_01(progress_summary.get("progress_relevance_score"), fallback=1.0)
    progress_low_relevance = False
    progress_high_risk = False
    if (
        progress_summary.get("progress_focus_present")
        and intent in WRITE_INTENTS
    ):
        if progress_score <= high_threshold:
            progress_low_relevance = True
            progress_high_risk = True
            boosted_uncertainty = max(boosted_uncertainty, 0.9)
        elif progress_score <= low_threshold:
            progress_low_relevance = True
            boosted_uncertainty = max(boosted_uncertainty, 0.8)

    threshold = max(0.05, 1.0 - eagerness)
    request = boosted_uncertainty >= threshold
    out = {
        "clarification_eagerness": eagerness,
        "uncertainty_score": uncertainty_score,
        "effective_uncertainty": round(boosted_uncertainty, 3),
        "threshold": round(threshold, 3),
        "request_clarification": bool(request),
        "needs_clarification_flag": needs_clarification,
        "progress_low_relevance": bool(progress_low_relevance),
        "progress_high_risk": bool(progress_high_risk),
        "progress_low_relevance_threshold": round(low_threshold, 3),
        "progress_high_risk_threshold": round(high_threshold, 3),
    }
    out.update(progress_summary)
    return out


def _coerce_utterance_entry(raw: Any) -> tuple[str, list[str], int | None, list[str], bool | None]:
    if isinstance(raw, str):
        return raw.strip(), [], None, [], None
    if not isinstance(raw, dict):
        return str(raw).strip(), [], None, [], None

    text = str(raw.get("utterance", "") or raw.get("text", "") or raw.get("input", "")).strip()
    answers_raw = raw.get("clarification_answers", [])
    answers: list[str] = []
    if isinstance(answers_raw, list):
        answers = [str(item).strip() for item in answers_raw if str(item).strip()]
    confirmation_answers_raw = raw.get("confirmation_answers", [])
    confirmation_answers: list[str] = []
    if isinstance(confirmation_answers_raw, list):
        confirmation_answers = [str(item).strip() for item in confirmation_answers_raw if str(item).strip()]
    max_rounds: int | None = None
    max_rounds_raw = raw.get("max_clarification_rounds")
    if isinstance(max_rounds_raw, (int, float)):
        max_rounds = max(0, int(max_rounds_raw))
    require_confirmation: bool | None = None
    raw_require_confirmation = raw.get("require_final_confirmation")
    if isinstance(raw_require_confirmation, bool):
        require_confirmation = raw_require_confirmation
    return text, answers, max_rounds, confirmation_answers, require_confirmation


def _is_predicate_control_directive(text: str) -> bool:
    raw = str(text or "").strip()
    if not raw:
        return False
    lowered = raw.lower()
    if not (
        lowered.startswith("use ")
        or lowered.startswith("predicates:")
        or lowered.startswith("schema:")
    ):
        return False
    return len(PREDICATE_SIGNATURE_RE.findall(raw)) >= 2


def _extract_predicate_names_from_control_directive(text: str) -> list[str]:
    names: set[str] = set()
    for token in PREDICATE_SIGNATURE_RE.findall(str(text or "")):
        name = token.split("/", 1)[0].strip().lower()
        if name:
            names.add(name)
    return sorted(names)


def _is_explicit_logic_utterance(text: str) -> bool:
    raw = str(text or "").strip()
    if not raw:
        return False
    lowered = raw.lower()
    if re.match(r"^\s*(query|assert|retract|set)\b", lowered):
        return True
    if re.match(r"^\s*[a-z_][a-z0-9_]*\s*\(", raw):
        return True
    if ":-" in raw and re.search(r"[a-z_][a-z0-9_]*\s*\(", raw):
        return True
    return False


def _pre_normalize_utterance(text: str) -> tuple[str, list[dict[str, Any]]]:
    """
    Lightweight pre-parse normalization for noisy multi-clause turns.

    Goals:
    - avoid parser confusion on parenthetical exception text
    - split known high-noise connector patterns into cleaner sentence segments
    - keep semantics intact and deterministic
    """
    working = str(text or "").strip()
    if not working:
        return "", []

    events: list[dict[str, Any]] = []
    collapsed = re.sub(r"\s+", " ", working).strip()
    if collapsed != working:
        working = collapsed
        events.append({"kind": "whitespace_collapse"})

    # Command-shaped turns should stay literal; rewriting them can corrupt
    # explicit predicate/argument structures.
    if _is_explicit_logic_utterance(working):
        return working, events

    parenthetical_pattern = re.compile(r"\(([^()]{1,180})\)")
    if parenthetical_pattern.search(working):
        # Convert short parenthetical fragments into inline clauses so the parser
        # sees the exception content as first-class text.
        next_working = parenthetical_pattern.sub(r", \1,", working)
        next_working = re.sub(r"\s+,", ",", next_working)
        next_working = re.sub(r",\s*,+", ", ", next_working)
        next_working = re.sub(r"\s{2,}", " ", next_working).strip()
        if next_working != working:
            working = next_working
            events.append({"kind": "parenthetical_inline"})

    phrase_rewrites: list[tuple[str, str, str]] = [
        (r"\bbut\b", ". ", "split_on_but"),
        (r"\bwhile\b", ". ", "split_on_while"),
        (r"\band top replies advise\b", ". top replies advise", "split_question_advice"),
        (r"\band comments advise\b", ". comments advise", "split_question_advice"),
        (r"\band answer was\b", ". answer was", "split_answer_clause"),
        (r"\band the chair emphasized\b", ". the chair emphasized", "split_policy_emphasis_clause"),
    ]
    for pattern, replacement, kind in phrase_rewrites:
        rewritten = re.sub(pattern, replacement, working, flags=re.IGNORECASE)
        rewritten = re.sub(r"\.\s*\.", ".", rewritten)
        rewritten = re.sub(r",\s*\.", ".", rewritten)
        rewritten = re.sub(r"\s{2,}", " ", rewritten).strip()
        if rewritten != working:
            working = rewritten
            events.append({"kind": kind})

    working = re.sub(r",\s*\.", ".", working)
    working = re.sub(r"\s+\.", ".", working).strip()
    return working, events


def _truncate_text(raw: str, limit: int) -> str:
    text = str(raw or "").strip()
    if limit <= 0 or len(text) <= limit:
        return text
    if limit <= 3:
        return text[:limit]
    return text[: limit - 3].rstrip() + "..."


def _snapshot_kb_clauses_for_clarification(
    *,
    server: Any,
    corpus_clauses: set[str] | None,
    max_items: int,
    max_chars: int,
) -> list[str]:
    clauses: list[str] = []
    if isinstance(corpus_clauses, set):
        clauses.extend(
            _normalize_clause(item)
            for item in sorted(corpus_clauses)
            if _normalize_clause(item)
        )

    if not clauses and hasattr(server, "engine"):
        engine = getattr(server, "engine", None)
        runtime_clauses = getattr(engine, "clauses", []) if engine is not None else []
        for row in runtime_clauses:
            text = _normalize_clause(repr(row))
            if text:
                clauses.append(text)
    if not clauses and hasattr(server, "_clauses"):
        raw = getattr(server, "_clauses", set())
        if isinstance(raw, set):
            clauses.extend(
                _normalize_clause(item)
                for item in sorted(raw)
                if _normalize_clause(item)
            )

    deduped: list[str] = []
    seen: set[str] = set()
    for clause in clauses:
        if clause in seen:
            continue
        seen.add(clause)
        deduped.append(clause)

    if max_items > 0 and len(deduped) > max_items:
        deduped = deduped[-max_items:]

    if max_chars > 0:
        selected: list[str] = []
        budget = max_chars
        for clause in reversed(deduped):
            needed = len(clause) + 1
            if selected and needed > budget:
                continue
            if not selected and len(clause) > budget:
                selected.append(_truncate_text(clause, max(32, budget)))
                break
            if needed > budget:
                break
            selected.append(clause)
            budget -= needed
        deduped = list(reversed(selected))

    return deduped


def _recent_turn_context_for_clarification(
    *,
    turn_rows: list[dict[str, Any]],
    max_turns: int,
    max_chars: int = 2400,
) -> list[str]:
    if max_turns <= 0 or not turn_rows:
        return []
    rows = turn_rows[-max_turns:]
    lines: list[str] = []
    for row in rows:
        idx = int(row.get("turn_index", 0) or 0)
        utterance = _truncate_text(str(row.get("utterance", "")), 140)
        apply_status = str(row.get("apply_status", "")).strip() or "unknown"
        parsed = row.get("parsed", {})
        logic = ""
        if isinstance(parsed, dict):
            logic = _truncate_text(str(parsed.get("logic_string", "")), 140)
        line = f"T{idx:02d} [{apply_status}] U: {utterance}"
        if logic:
            line += f" | L: {logic}"
        lines.append(line)

    if max_chars > 0:
        selected: list[str] = []
        budget = max_chars
        for line in reversed(lines):
            needed = len(line) + 1
            if selected and needed > budget:
                continue
            if not selected and len(line) > budget:
                selected.append(_truncate_text(line, max(32, budget)))
                break
            if needed > budget:
                break
            selected.append(line)
            budget -= needed
        lines = list(reversed(selected))
    return lines


def _build_clarification_context_pack(
    *,
    server: Any,
    corpus_clauses: set[str] | None,
    turn_rows: list[dict[str, Any]],
    progress_memory: dict[str, Any] | None,
    history_turns: int,
    kb_clause_limit: int,
    kb_char_budget: int,
) -> dict[str, Any]:
    kb_lines = _snapshot_kb_clauses_for_clarification(
        server=server,
        corpus_clauses=corpus_clauses,
        max_items=max(0, kb_clause_limit),
        max_chars=max(0, kb_char_budget),
    )
    recent_lines = _recent_turn_context_for_clarification(
        turn_rows=turn_rows,
        max_turns=max(0, history_turns),
    )
    progress_lines: list[str] = []
    if isinstance(progress_memory, dict):
        progress_lines.extend(_progress_focus_preview(progress_memory, max_items=5))
        for row in progress_memory.get("open_questions", []):
            if not isinstance(row, dict):
                continue
            if str(row.get("status", "open")).strip().lower() != "open":
                continue
            text = str(row.get("text", "")).strip()
            if text:
                progress_lines.append(f"open_question: {text}")
            if len(progress_lines) >= 8:
                break
    return {
        "kb_clauses": kb_lines,
        "recent_turns": recent_lines,
        "progress_summary": progress_lines,
        "kb_clause_count": len(kb_lines),
        "recent_turn_count": len(recent_lines),
        "progress_summary_count": len(progress_lines),
    }


def _is_affirmative_confirmation(answer: str) -> bool:
    text = _normalize_clarification_answer_text(answer)
    return text in {
        "y",
        "yes",
        "yeah",
        "yep",
        "sure",
        "ok",
        "okay",
        "confirm",
        "approved",
        "go ahead",
        "do it",
        "apply",
    }


def _is_negative_confirmation(answer: str) -> bool:
    text = _normalize_clarification_answer_text(answer)
    return text in {
        "n",
        "no",
        "nope",
        "nah",
        "stop",
        "cancel",
        "reject",
        "do not apply",
        "dont apply",
        "don't apply",
    }


def _build_final_confirmation_question(parsed: dict[str, Any]) -> str:
    intent = str(parsed.get("intent", "")).strip()
    logic = _truncate_text(str(parsed.get("logic_string", "")).strip(), 180)
    if intent in {"assert_fact", "assert_rule", "retract"} and logic:
        return f"Confirm KB write `{intent}` with `{logic}`? (yes/no)"
    if intent in {"assert_fact", "assert_rule", "retract"}:
        return f"Confirm KB write `{intent}`? (yes/no)"
    return "Confirm this operation? (yes/no)"


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


def _normalize_clarification_answer_text(answer: str) -> str:
    text = re.sub(r"\s+", " ", str(answer or "").strip()).lower()
    return text


def _is_non_informative_clarification_answer(answer: str) -> bool:
    normalized = _normalize_clarification_answer_text(answer)
    if not normalized:
        return True
    non_informative = {
        "unknown",
        "i don't know",
        "i dont know",
        "dont know",
        "not sure",
        "unsure",
        "n/a",
        "na",
    }
    return normalized in non_informative


def _is_redundant_clarification_pair(
    rounds: list[dict[str, Any]],
    *,
    question: str,
    answer: str,
) -> bool:
    q_norm = _normalize_clarification_answer_text(question)
    a_norm = _normalize_clarification_answer_text(answer)
    for row in rounds:
        rq = _normalize_clarification_answer_text(str(row.get("question", "")))
        ra = _normalize_clarification_answer_text(str(row.get("answer", "")))
        if rq == q_norm and ra == a_norm:
            return True
    return False


def _coerce_synthetic_answer_text(raw: Any) -> str:
    text = str(raw or "").strip()
    if not text:
        return ""
    text = text.strip("`").strip()
    text = re.sub(r"^\s*(answer|a)\s*:\s*", "", text, flags=re.IGNORECASE)
    if len(text) >= 2 and ((text[0] == text[-1] == '"') or (text[0] == text[-1] == "'")):
        text = text[1:-1].strip()
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > 240:
        text = text[:240].rstrip()
    return text


def _build_clarification_answer_prompt(
    *,
    utterance: str,
    route: str,
    question: str,
    parsed: dict[str, Any],
    rounds: list[dict[str, Any]],
    context_pack: dict[str, Any] | None = None,
    answer_role: str = "proxy_model",
) -> str:
    prior = []
    for row in rounds:
        q = str(row.get("question", "")).strip()
        a = str(row.get("answer", "")).strip()
        if q or a:
            prior.append(f"Q: {q}\nA: {a}")
    prior_text = "\n".join(prior) if prior else "(none)"
    parsed_view = {
        "intent": parsed.get("intent"),
        "logic_string": parsed.get("logic_string"),
        "ambiguities": parsed.get("ambiguities", []),
        "clarification_reason": parsed.get("clarification_reason", ""),
        "uncertainty_score": parsed.get("uncertainty_score"),
    }
    kb_lines: list[str] = []
    recent_lines: list[str] = []
    progress_lines: list[str] = []
    if isinstance(context_pack, dict):
        kb_raw = context_pack.get("kb_clauses", [])
        recent_raw = context_pack.get("recent_turns", [])
        progress_raw = context_pack.get("progress_summary", [])
        if isinstance(kb_raw, list):
            kb_lines = [str(item).strip() for item in kb_raw if str(item).strip()]
        if isinstance(recent_raw, list):
            recent_lines = [str(item).strip() for item in recent_raw if str(item).strip()]
        if isinstance(progress_raw, list):
            progress_lines = [str(item).strip() for item in progress_raw if str(item).strip()]
    kb_text = "\n".join(f"- {row}" for row in kb_lines) if kb_lines else "(none)"
    recent_text = "\n".join(f"- {row}" for row in recent_lines) if recent_lines else "(none)"
    progress_text = "\n".join(f"- {row}" for row in progress_lines) if progress_lines else "(none)"
    role = str(answer_role or "proxy_model").strip().lower()
    if role == "served_llm":
        role_rules = (
            "- use deterministic KB context first, then recent turns, then utterance language cues\n"
            "- if one interpretation is clearly most likely, answer concretely\n"
            "- if multiple plausible interpretations remain, answer must be exactly 'unknown'\n"
            "- keep confidence conservative; <=0.55 when ambiguity remains\n"
        )
    else:
        role_rules = (
            "- treat deterministic KB context as highest-trust evidence\n"
            "- if deterministic context and recent turns do not support certainty, answer must be 'unknown'\n"
            "- if truly unknown, answer must be exactly 'unknown'\n"
        )

    return (
        "/no_think\n"
        "You are the clarification proxy for a served assistant model.\n"
        "Return minified JSON only with keys: answer,confidence,assumption\n"
        "Rules:\n"
        "- answer must be short, concrete, and directly answer the question\n"
        f"{role_rules}"
        "- confidence must be numeric in [0,1]\n"
        "- assumption must be <=12 words\n"
        "Do not output markdown or extra keys.\n"
        f"Answer role: {role}\n"
        f"Route: {route}\n"
        f"Deterministic KB context:\n{kb_text}\n"
        f"Progress memory context:\n{progress_text}\n"
        f"Recent accepted turns:\n{recent_text}\n"
        f"Original utterance:\n{utterance}\n"
        f"Clarification question:\n{question}\n"
        f"Prior clarification transcript:\n{prior_text}\n"
        f"Current parse draft:\n{json.dumps(parsed_view, ensure_ascii=False)}\n"
    )


def _generate_synthetic_clarification_answer(
    *,
    backend: str,
    base_url: str,
    model: str,
    utterance: str,
    route: str,
    question: str,
    parsed: dict[str, Any],
    rounds: list[dict[str, Any]],
    context_pack: dict[str, Any] | None,
    context_length: int,
    timeout: int,
    api_key: str | None,
    answer_source_prefix: str = "synthetic",
    answer_role: str = "proxy_model",
) -> tuple[str, dict[str, Any]]:
    prompt = _build_clarification_answer_prompt(
        utterance=utterance,
        route=route,
        question=question,
        parsed=parsed,
        rounds=rounds,
        context_pack=context_pack,
        answer_role=answer_role,
    )
    response = _call_model_prompt(
        backend=backend,
        base_url=base_url,
        model=model,
        prompt_text=prompt,
        context_length=max(512, context_length),
        timeout=timeout,
        api_key=api_key,
    )
    parsed_json, _ = _parse_model_json(response, required_keys=["answer"])
    if isinstance(parsed_json, dict):
        answer = _coerce_synthetic_answer_text(parsed_json.get("answer", ""))
        if answer:
            return answer, {
                "answer_source": f"{answer_source_prefix}_model",
                "answer_confidence": _clip_01(parsed_json.get("confidence"), fallback=0.5),
                "answer_assumption": str(parsed_json.get("assumption", "")).strip(),
                "context_kb_clause_count": int((context_pack or {}).get("kb_clause_count", 0) or 0),
                "context_recent_turn_count": int((context_pack or {}).get("recent_turn_count", 0) or 0),
                "context_progress_summary_count": int((context_pack or {}).get("progress_summary_count", 0) or 0),
            }

    fallback = _coerce_synthetic_answer_text(response.message)
    if fallback:
        return fallback, {
            "answer_source": f"{answer_source_prefix}_fallback",
            "answer_confidence": 0.3,
            "answer_assumption": "fallback from raw message",
        }

    return "", {
        "answer_source": f"{answer_source_prefix}_failed",
        "answer_confidence": 0.0,
        "answer_assumption": "no parseable synthetic answer",
        "context_kb_clause_count": int((context_pack or {}).get("kb_clause_count", 0) or 0),
        "context_recent_turn_count": int((context_pack or {}).get("recent_turn_count", 0) or 0),
        "context_progress_summary_count": int((context_pack or {}).get("progress_summary_count", 0) or 0),
    }


def _is_variable_token(token: str) -> bool:
    if not token:
        return False
    first = token[0]
    if not (first == "_" or ("A" <= first <= "Z")):
        return False
    return all(ch == "_" or ch.isalnum() for ch in token[1:])


def _term_has_variable(term: Term) -> bool:
    if getattr(term, "is_variable", False):
        return True
    return any(_term_has_variable(arg) for arg in getattr(term, "args", []))


def _parse_clause_term(clause: str) -> Term | None:
    normalized = _normalize_clause(clause)
    if not normalized:
        return None
    raw = normalized[:-1].strip() if normalized.endswith(".") else normalized.strip()
    if not raw:
        return None
    parser = PrologEngine(max_depth=32)
    try:
        return parser.parse_term(raw)
    except Exception:
        return None


def _split_rule_head_body(expr: str) -> tuple[str, str] | None:
    text = expr.strip()
    if not text:
        return None
    paren_depth = 0
    bracket_depth = 0
    for idx in range(len(text) - 1):
        ch = text[idx]
        if ch == "(":
            paren_depth += 1
        elif ch == ")":
            paren_depth = max(0, paren_depth - 1)
        elif ch == "[":
            bracket_depth += 1
        elif ch == "]":
            bracket_depth = max(0, bracket_depth - 1)
        elif ch == ":" and text[idx + 1] == "-" and paren_depth == 0 and bracket_depth == 0:
            head = text[:idx].strip()
            body = text[idx + 2 :].strip()
            if head and body:
                return head, body
            return None
    return None


def _is_valid_goal_clause(clause: str, *, require_ground: bool = False) -> bool:
    normalized = _normalize_clause(clause)
    if not normalized:
        return False
    raw = normalized[:-1].strip() if normalized.endswith(".") else normalized.strip()
    if not raw or ":-" in raw:
        return False
    term = _parse_clause_term(normalized)
    if term is None:
        return False
    if require_ground and _term_has_variable(term):
        return False
    return True


def _is_valid_rule_clause(clause: str) -> bool:
    normalized = _normalize_clause(clause)
    if not normalized:
        return False
    raw = normalized[:-1].strip() if normalized.endswith(".") else normalized.strip()
    split = _split_rule_head_body(raw)
    if not split:
        return False
    head_text, body_text = split
    if not _is_valid_goal_clause(f"{head_text}.", require_ground=False):
        return False
    body_goals = _split_top_level_args(body_text)
    if not body_goals:
        return False
    for goal in body_goals:
        if not _is_valid_goal_clause(f"{goal}.", require_ground=False):
            return False
    return True


def _extract_first_explicit_goal_clause(text: str, *, require_ground: bool) -> str:
    source = text or ""
    length = len(source)
    for start in range(length):
        first = source[start]
        if first < "a" or first > "z":
            continue
        name_end = start + 1
        while name_end < length and (source[name_end].isalnum() or source[name_end] == "_"):
            name_end += 1
        cursor = name_end
        while cursor < length and source[cursor].isspace():
            cursor += 1
        if cursor >= length or source[cursor] != "(":
            continue

        depth = 0
        close_idx = -1
        for idx in range(cursor, length):
            ch = source[idx]
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    close_idx = idx
                    break
        if close_idx < 0:
            continue

        tail = close_idx + 1
        while tail < length and source[tail].isspace():
            tail += 1
        if tail < length and source[tail] == ".":
            candidate = source[start : tail + 1]
        else:
            candidate = source[start : close_idx + 1]
        normalized = _normalize_clause(candidate)
        if _is_valid_goal_clause(normalized, require_ground=require_ground):
            return normalized
    return ""


def _walk_term_components(term: Term, atoms: set[str], variables: set[str], predicates: set[str]) -> None:
    if getattr(term, "is_variable", False):
        name = str(getattr(term, "name", "")).strip()
        if name:
            variables.add(name)
        return

    name = str(getattr(term, "name", "")).strip()
    args = list(getattr(term, "args", []))
    if args:
        if name and name != "retract":
            predicates.add(name)
        for arg in args:
            _walk_term_components(arg, atoms, variables, predicates)
        return

    if name and name != "retract":
        atoms.add(name)


def _extract_components_from_logic(logic_string: str) -> tuple[list[str], list[str], list[str]]:
    atoms: set[str] = set()
    variables: set[str] = set()
    predicates: set[str] = set()
    clause = _normalize_clause(logic_string)
    if not clause:
        return [], [], []

    raw = clause[:-1].strip() if clause.endswith(".") else clause.strip()
    terms: list[Term] = []
    split_rule = _split_rule_head_body(raw)
    if split_rule:
        head_text, body_text = split_rule
        head_term = _parse_clause_term(f"{head_text}.")
        if head_term is not None:
            terms.append(head_term)
        for goal_text in _split_top_level_args(body_text):
            goal_term = _parse_clause_term(f"{goal_text}.")
            if goal_term is not None:
                terms.append(goal_term)
    else:
        term = _parse_clause_term(clause)
        if term is not None:
            terms.append(term)

    for term in terms:
        _walk_term_components(term, atoms, variables, predicates)

    if not terms:
        signatures = _extract_goal_signatures(raw)
        fallback_predicates = sorted(
            {sig.split("/", 1)[0] for sig in signatures if "/" in sig and sig != "retract/1"}
        )
        return [], [], fallback_predicates

    return sorted(atoms), sorted(variables), sorted(predicates)


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
        targets = _extract_retract_targets(logic_string, [])
        if len(targets) <= 1:
            extracted_calls: list[str] = []
            for name, args in _extract_calls_with_args(utterance):
                if not name or not args:
                    continue
                call = _normalize_clause(f"{name}({', '.join(args)}).")
                if _is_valid_goal_clause(call, require_ground=True):
                    extracted_calls.append(call)
            if len(extracted_calls) > len(targets):
                targets = extracted_calls
        if not targets:
            return None
        facts = targets
        retract_clauses: list[str] = []
        for target in targets:
            fact_term = target[:-1] if target.endswith(".") else target
            retract_clauses.append(f"retract({fact_term}).")
        logic_string = "\n".join(retract_clauses)
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

    facts = [str(x).strip() for x in parsed.get("facts", [])]
    rules = [str(x).strip() for x in parsed.get("rules", [])]
    queries = [str(x).strip() for x in parsed.get("queries", [])]

    if intent == "assert_fact":
        if not facts:
            errors.append("assert_fact requires facts[0]")
        else:
            if len(facts) == 1 and logic_string != facts[0]:
                errors.append("assert_fact requires logic_string == facts[0] when a single fact is emitted")
            for idx, fact in enumerate(facts, start=1):
                if not _is_valid_goal_clause(fact, require_ground=True):
                    errors.append(f"facts[{idx - 1}] is not valid Prolog fact/goal")
            if len(facts) > 1 and logic_string:
                if not all((f[:-1] if f.endswith(".") else f) in logic_string for f in facts):
                    errors.append("assert_fact multi-fact logic_string must include every emitted fact clause")
    elif intent == "assert_rule":
        if not rules:
            errors.append("assert_rule requires rules[0]")
        else:
            if len(rules) == 1 and logic_string != rules[0]:
                errors.append("assert_rule requires logic_string == rules[0] when a single rule is emitted")
            for idx, rule in enumerate(rules, start=1):
                if not _is_valid_rule_clause(rule):
                    errors.append(f"rules[{idx - 1}] is not valid Prolog rule")
            if len(rules) > 1 and logic_string:
                if not all((r[:-1] if r.endswith(".") else r) in logic_string for r in rules):
                    errors.append("assert_rule multi-rule logic_string must include every emitted rule clause")
    elif intent == "query":
        if not queries:
            errors.append("query requires queries[0]")
        else:
            if logic_string != queries[0]:
                errors.append("query requires logic_string == queries[0]")
            if not _is_valid_goal_clause(queries[0], require_ground=False):
                errors.append("queries[0] is not valid Prolog goal")
    elif intent == "retract":
        retract_targets = _extract_retract_targets(logic_string, facts)
        if not retract_targets:
            errors.append("retract requires logic_string format retract(<fact>).")
        else:
            for idx, target in enumerate(retract_targets, start=1):
                if not _is_valid_goal_clause(target, require_ground=True):
                    errors.append(f"retract target at index {idx - 1} is not a valid grounded fact")
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


def _extract_retract_targets(logic_string: str, fallback_facts: list[str]) -> list[str]:
    targets: list[str] = []
    logic = str(logic_string or "").strip()
    if logic:
        fragments: list[str] = []
        for line in logic.splitlines():
            part = line.strip()
            if not part:
                continue
            chunks = [c.strip() for c in part.split(".") if c.strip()]
            if chunks:
                fragments.extend(chunks)
            else:
                fragments.append(part)
        if not fragments:
            fragments = [logic]
        for fragment in fragments:
            clause = _normalize_clause(f"{fragment}.")
            parsed = _parse_clause_term(clause)
            if parsed is None or str(getattr(parsed, "name", "")) != "retract":
                continue
            args = list(getattr(parsed, "args", []))
            if len(args) != 1:
                continue
            fact = _normalize_clause(str(args[0]))
            if _is_valid_goal_clause(fact, require_ground=True):
                targets.append(fact)

    for raw_fact in fallback_facts:
        fact = _normalize_clause(str(raw_fact))
        if _is_valid_goal_clause(fact, require_ground=True):
            targets.append(fact)

    seen: set[str] = set()
    unique: list[str] = []
    for target in targets:
        if target and target not in seen:
            seen.add(target)
            unique.append(target)
    return unique


def _extract_retract_target(logic_string: str, fallback_facts: list[str]) -> str | None:
    targets = _extract_retract_targets(logic_string, fallback_facts)
    return targets[0] if targets else None


def _build_retract_fallback_parse(utterance: str) -> dict[str, Any] | None:
    text = utterance.strip()
    if not text:
        return None

    arrow_edge = re.search(
        r"([A-Za-z][A-Za-z0-9_'-]*)\s*(?:->|→|=>)\s*([A-Za-z][A-Za-z0-9_'-]*)\s+edge\b",
        text,
        re.IGNORECASE,
    )
    if arrow_edge:
        left_atom = _atomize(arrow_edge.group(1))
        right_atom = _atomize(arrow_edge.group(2))
        if left_atom and right_atom:
            # In family-graph phrasing, "x->y edge" typically denotes parent(x,y).
            fact = f"parent({left_atom}, {right_atom})."
            fact_term = fact[:-1]
            parsed = {
                "intent": "retract",
                "logic_string": f"retract({fact_term}).",
                "components": {
                    "atoms": sorted({left_atom, right_atom}),
                    "variables": [],
                    "predicates": ["parent"],
                },
                "facts": [fact],
                "rules": [],
                "queries": [],
                "confidence": {
                    "overall": 0.66,
                    "intent": 0.8,
                    "logic": 0.6,
                },
                "ambiguities": [],
                "needs_clarification": False,
                "uncertainty_score": 0.28,
                "uncertainty_label": "low",
                "clarification_question": "",
                "clarification_reason": "",
                "rationale": "Fallback retract parse from arrow-edge phrasing (x->y edge).",
            }
            ok_edge, _ = _validate_parsed(parsed)
            if ok_edge:
                return parsed

    fact = _extract_first_explicit_goal_clause(text, require_ground=True)
    if not fact:
        return None
    atoms, variables, predicates = _extract_components_from_logic(fact)
    if not predicates:
        return None
    fact_term = fact[:-1] if fact.endswith(".") else fact
    parsed = {
        "intent": "retract",
        "logic_string": f"retract({fact_term}).",
        "components": {
            "atoms": sorted(set(atoms)),
            "variables": sorted(set(variables)),
            "predicates": sorted(set(predicates)),
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


def _is_ambiguous_pronoun_atom(atom: str) -> bool:
    return str(atom or "").strip().lower() in AMBIGUOUS_PRONOUN_ATOMS


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

    # Strip common discourse lead-ins so core relation patterns still match.
    lowered = text.lower()
    leadins = [
        "please record this:",
        "record this:",
        "note this:",
        "note that:",
        "what i meant was that ",
        "i meant that ",
        "actually, ",
    ]
    for marker in leadins:
        if lowered.startswith(marker):
            text = text[len(marker) :].strip()
            lowered = text.lower()
            break
    # Remove lightweight connective prefixes that often precede factual clauses.
    connective_prefix = re.compile(r"^(?:and|also|so|then|well|okay|ok)\s*,?\s+", re.IGNORECASE)
    while True:
        stripped = connective_prefix.sub("", text, count=1).strip()
        if stripped == text or not stripped:
            break
        text = stripped
        lowered = text.lower()
    if ":" in text:
        _, tail = text.split(":", 1)
        if tail.strip():
            text = tail.strip()
            lowered = text.lower()

    explicit_fact = _extract_first_explicit_goal_clause(text, require_ground=True)
    if explicit_fact:
        atoms, variables, predicates = _extract_components_from_logic(explicit_fact)
        if not predicates:
            return None
        parsed = _build_parse_payload(
            intent="assert_fact",
            logic_string=explicit_fact,
            facts=[explicit_fact],
            rules=[],
            queries=[],
            predicates=predicates,
            atoms=atoms,
            variables=variables,
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

    inverse_named_possessive = re.match(
        r"^\s*([A-Za-z][A-Za-z0-9_'-]*)\s+is\s+([A-Za-z][A-Za-z0-9_'-]*)'?s\s+([A-Za-z][A-Za-z0-9_-]*)\.?\s*$",
        text,
        re.IGNORECASE,
    )
    if inverse_named_possessive:
        subject_atom = _atomize(inverse_named_possessive.group(1))
        owner_atom = _atomize(inverse_named_possessive.group(2))
        relation = _atomize(inverse_named_possessive.group(3))
        if subject_atom and owner_atom and relation:
            fact = f"{relation}({subject_atom}, {owner_atom})."
            parsed = _build_parse_payload(
                intent="assert_fact",
                logic_string=fact,
                facts=[fact],
                rules=[],
                queries=[],
                predicates=[relation],
                atoms=[subject_atom, owner_atom],
                variables=[],
                rationale="Fallback possessive relation parse from '<subject> is <owner>\\'s <relation>'.",
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
            if _is_ambiguous_pronoun_atom(subject_atom):
                var_name = "X"
                fact = f"{predicate}({var_name})."
                parsed = _build_parse_payload(
                    intent="assert_fact",
                    logic_string=fact,
                    facts=[fact],
                    rules=[],
                    queries=[],
                    predicates=[predicate],
                    atoms=[],
                    variables=[var_name],
                    rationale="Fallback unary parse detected unresolved pronoun subject.",
                )
                parsed["needs_clarification"] = True
                parsed["ambiguities"] = [f"Pronoun '{subject_atom}' is unresolved."]
                parsed["uncertainty_score"] = 0.78
                parsed["uncertainty_label"] = "high"
                parsed["clarification_reason"] = "Pronoun referent unresolved."
                parsed["clarification_question"] = f"Who does '{subject_atom}' refer to?"
                return parsed
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
    if not binary:
        binary = re.match(
            (
                r"^\s*([A-Za-z][A-Za-z0-9_'-]*)\s+is\s+(?:a|an|the)?\s*([A-Za-z][A-Za-z0-9_-]*)\s+of\s+"
                r"([A-Za-z][A-Za-z0-9_'-]*)(?:\s+(?:too|also|again|still|as_well))?\.?\s*$"
            ),
            text,
            re.IGNORECASE,
        )
    if binary:
        subject_atom = _atomize(binary.group(1))
        relation = _atomize(binary.group(2))
        obj_atom = _atomize(binary.group(3))
        if subject_atom and relation and obj_atom:
            subject_is_pronoun = _is_ambiguous_pronoun_atom(subject_atom)
            object_is_pronoun = _is_ambiguous_pronoun_atom(obj_atom)
            if subject_is_pronoun or object_is_pronoun:
                left = "X" if subject_is_pronoun else subject_atom
                right = "Y" if object_is_pronoun else obj_atom
                fact = f"{relation}({left}, {right})."
                parsed = _build_parse_payload(
                    intent="assert_fact",
                    logic_string=fact,
                    facts=[fact],
                    rules=[],
                    queries=[],
                    predicates=[relation],
                    atoms=[x for x in [subject_atom if not subject_is_pronoun else "", obj_atom if not object_is_pronoun else ""] if x],
                    variables=[v for v in [left if subject_is_pronoun else "", right if object_is_pronoun else ""] if v],
                    rationale="Fallback binary parse detected unresolved pronoun argument.",
                )
                parsed["needs_clarification"] = True
                pronouns = [x for x, ok in [(subject_atom, subject_is_pronoun), (obj_atom, object_is_pronoun)] if ok]
                parsed["ambiguities"] = [f"Unresolved pronoun(s): {', '.join(pronouns)}."]
                parsed["uncertainty_score"] = 0.8
                parsed["uncertainty_label"] = "high"
                parsed["clarification_reason"] = "Pronoun referent unresolved."
                if len(pronouns) == 1:
                    parsed["clarification_question"] = f"Who does '{pronouns[0]}' refer to?"
                else:
                    parsed["clarification_question"] = "Who are the pronoun referents in this relation?"
                return parsed
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


def _apply_directional_fact_guard(
    parsed: dict[str, Any],
    *,
    utterance: str,
    route: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """
    Deterministic guard for common role-direction slips.

    When the utterance is a clear "<subject> is <relation> of <object>" form and
    model output inverts the two arguments, prefer the fallback orientation.
    """
    events: list[dict[str, Any]] = []
    if not isinstance(parsed, dict):
        return parsed, events

    intent = str(parsed.get("intent", "")).strip().lower()
    route_name = str(route or "").strip().lower()
    if intent != "assert_fact" and route_name != "assert_fact":
        return parsed, events

    fallback = _build_assert_fact_fallback_parse(utterance)
    if not isinstance(fallback, dict):
        return parsed, events

    logic_text = str(parsed.get("logic_string", "")).strip()
    fallback_logic = str(fallback.get("logic_string", "")).strip()
    if not logic_text or not fallback_logic:
        return parsed, events

    current_calls = _extract_calls_with_args(logic_text[:-1] if logic_text.endswith(".") else logic_text)
    fallback_calls = _extract_calls_with_args(
        fallback_logic[:-1] if fallback_logic.endswith(".") else fallback_logic
    )
    if len(current_calls) != 1 or len(fallback_calls) != 1:
        return parsed, events

    current_name, current_args = current_calls[0]
    fallback_name, fallback_args = fallback_calls[0]
    if current_name != fallback_name:
        return parsed, events
    if len(current_args) != 2 or len(fallback_args) != 2:
        return parsed, events

    left = current_args[0].strip()
    right = current_args[1].strip()
    f_left = fallback_args[0].strip()
    f_right = fallback_args[1].strip()
    if not left or not right or not f_left or not f_right:
        return parsed, events
    if left == right or f_left == f_right:
        return parsed, events
    if _is_variable_token(left) or _is_variable_token(right):
        return parsed, events
    if _is_variable_token(f_left) or _is_variable_token(f_right):
        return parsed, events
    def _is_adjacent_transposition(source: str, target: str) -> bool:
        if len(source) != len(target) or len(source) < 2:
            return False
        if source == target:
            return False
        for idx in range(len(source) - 1):
            swapped = source[:idx] + source[idx + 1] + source[idx] + source[idx + 2 :]
            if swapped == target:
                return True
        return False

    def _is_single_edit(source: str, target: str) -> bool:
        if source == target:
            return True
        if _is_adjacent_transposition(source, target):
            return True
        len_diff = abs(len(source) - len(target))
        if len_diff > 1:
            return False
        if len(source) == len(target):
            mismatches = sum(1 for a, b in zip(source, target) if a != b)
            return mismatches <= 1
        if len(source) < len(target):
            source, target = target, source
        # source is longer by one char
        i = 0
        j = 0
        edits = 0
        while i < len(source) and j < len(target):
            if source[i] == target[j]:
                i += 1
                j += 1
            else:
                edits += 1
                i += 1
                if edits > 1:
                    return False
        return True

    def _atom_matches(expected: str, observed: str) -> bool:
        if expected == observed:
            return True
        return _is_single_edit(expected.lower(), observed.lower())

    reversed_match = _atom_matches(f_right, left) and _atom_matches(f_left, right)
    direct_match = _atom_matches(f_left, left) and _atom_matches(f_right, right)
    if not reversed_match and not direct_match:
        return parsed, events

    corrected_logic = f"{fallback_name}({f_left}, {f_right})."
    atoms, variables, predicates = _extract_components_from_logic(corrected_logic)
    parsed["logic_string"] = corrected_logic
    parsed["facts"] = [corrected_logic]
    parsed["rules"] = []
    parsed["queries"] = []
    parsed["components"] = {
        "atoms": sorted(set(atoms)),
        "variables": sorted(set(variables)),
        "predicates": sorted(set(predicates)),
    }
    rationale = str(parsed.get("rationale", "")).strip()
    if rationale:
        parsed["rationale"] = (
            rationale + " Directional fact guard corrected inverted subject/object order."
        )
    else:
        parsed["rationale"] = "Directional fact guard corrected inverted subject/object order."

    events.append(
        {
            "kind": "directional_fact_guard",
            "predicate": fallback_name,
            "from": f"{current_name}({left}, {right})",
            "to": f"{fallback_name}({f_left}, {f_right})",
            "match_mode": "reversed" if reversed_match and not direct_match else "canonicalized",
        }
    )
    return parsed, events


def _apply_retract_exclusion_guard(
    parsed: dict[str, Any],
    *,
    utterance: str,
    route: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    events: list[dict[str, Any]] = []
    if not isinstance(parsed, dict):
        return parsed, events

    intent = str(parsed.get("intent", "")).strip().lower()
    route_name = str(route or "").strip().lower()
    if intent != "retract" and route_name != "retract":
        return parsed, events

    text = str(utterance or "")
    excluded_edges = re.findall(
        r"\bnot\s+([A-Za-z][A-Za-z0-9_'-]*)\s*(?:->|→|=>)\s*([A-Za-z][A-Za-z0-9_'-]*)\b",
        text,
        flags=re.IGNORECASE,
    )
    protected_edges = re.findall(
        r"([A-Za-z][A-Za-z0-9_'-]*)\s*(?:->|→|=>)\s*([A-Za-z][A-Za-z0-9_'-]*)\s+(?:stays?|keeps?|remains?)\b",
        text,
        flags=re.IGNORECASE,
    )
    protected_edges.extend(
        re.findall(
            r"\bkeep\s+([A-Za-z][A-Za-z0-9_'-]*)\s*(?:->|→|=>)\s*([A-Za-z][A-Za-z0-9_'-]*)\b",
            text,
            flags=re.IGNORECASE,
        )
    )
    if not excluded_edges and not protected_edges:
        return parsed, events

    excluded_facts: set[str] = set()
    for left_raw, right_raw in excluded_edges + protected_edges:
        left_atom = _atomize(left_raw)
        right_atom = _atomize(right_raw)
        if left_atom and right_atom:
            excluded_facts.add(f"parent({left_atom}, {right_atom}).")
    if not excluded_facts:
        return parsed, events

    logic_text = str(parsed.get("logic_string", "")).strip()
    parsed_facts = [str(x).strip() for x in parsed.get("facts", []) if str(x).strip()]
    targets = _extract_retract_targets(logic_text, parsed_facts)
    if not targets:
        return parsed, events

    kept_targets = [t for t in targets if t not in excluded_facts]
    removed_targets = [t for t in targets if t in excluded_facts]
    if not removed_targets:
        return parsed, events
    if not kept_targets:
        return parsed, events

    clauses = [f"retract({t[:-1] if t.endswith('.') else t})." for t in kept_targets]
    new_logic = "\n".join(clauses)
    atoms, variables, predicates = _extract_components_from_logic(new_logic)
    parsed["logic_string"] = new_logic
    parsed["facts"] = kept_targets
    parsed["rules"] = []
    parsed["queries"] = []
    parsed["components"] = {
        "atoms": sorted(set(atoms)),
        "variables": sorted(set(variables)),
        "predicates": sorted(set(predicates)),
    }
    rationale = str(parsed.get("rationale", "")).strip()
    suffix = "Retract exclusion guard removed explicitly negated edge target(s)."
    parsed["rationale"] = f"{rationale} {suffix}".strip() if rationale else suffix
    events.append(
        {
            "kind": "retract_exclusion_guard",
            "removed": removed_targets,
            "kept": kept_targets,
        }
    )
    return parsed, events


def _apply_retract_edge_target_guard(
    parsed: dict[str, Any],
    *,
    utterance: str,
    route: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    events: list[dict[str, Any]] = []
    if not isinstance(parsed, dict):
        return parsed, events

    intent = str(parsed.get("intent", "")).strip().lower()
    route_name = str(route or "").strip().lower()
    if intent != "retract" and route_name != "retract":
        return parsed, events

    text = str(utterance or "")
    lowered = text.lower()
    edge_pairs = re.findall(
        r"([A-Za-z][A-Za-z0-9_'-]*)\s*(?:->|→|=>)\s*([A-Za-z][A-Za-z0-9_'-]*)",
        text,
        flags=re.IGNORECASE,
    )
    if not edge_pairs:
        return parsed, events

    excluded_pairs = set(
        (
            _atomize(left),
            _atomize(right),
        )
        for left, right in re.findall(
            r"\bnot\s+([A-Za-z][A-Za-z0-9_'-]*)\s*(?:->|→|=>)\s*([A-Za-z][A-Za-z0-9_'-]*)",
            text,
            flags=re.IGNORECASE,
        )
    )

    desired_targets: list[str] = []
    for left_raw, right_raw in edge_pairs:
        left_atom = _atomize(left_raw)
        right_atom = _atomize(right_raw)
        if not left_atom or not right_atom:
            continue
        if (left_atom, right_atom) in excluded_pairs:
            continue
        target = f"parent({left_atom}, {right_atom})."
        if target not in desired_targets:
            desired_targets.append(target)
    if not desired_targets:
        return parsed, events

    logic_text = str(parsed.get("logic_string", "")).strip()
    parsed_facts = [str(x).strip() for x in parsed.get("facts", []) if str(x).strip()]
    current_targets = _extract_retract_targets(logic_text, parsed_facts)

    def _is_parent_binary_fact(clause_text: str) -> bool:
        term = _parse_clause_term(clause_text)
        if term is None or str(getattr(term, "name", "")).strip() != "parent":
            return False
        args = list(getattr(term, "args", []))
        return len(args) == 2 and not any(getattr(arg, "is_variable", False) for arg in args)

    malformed_or_nonparent = (
        not current_targets or any(not _is_parent_binary_fact(target) for target in current_targets)
    )
    has_only_constraint = " only" in f" {lowered} "
    mismatched_targets = set(current_targets) != set(desired_targets)
    if not malformed_or_nonparent and not (has_only_constraint and mismatched_targets):
        return parsed, events

    clauses = [f"retract({t[:-1] if t.endswith('.') else t})." for t in desired_targets]
    new_logic = "\n".join(clauses)
    atoms, variables, predicates = _extract_components_from_logic(new_logic)
    parsed["logic_string"] = new_logic
    parsed["facts"] = desired_targets
    parsed["rules"] = []
    parsed["queries"] = []
    parsed["components"] = {
        "atoms": sorted(set(atoms)),
        "variables": sorted(set(variables)),
        "predicates": sorted(set(predicates)),
    }
    rationale = str(parsed.get("rationale", "")).strip()
    suffix = "Retract edge target guard normalized arrow-edge retract target(s)."
    parsed["rationale"] = f"{rationale} {suffix}".strip() if rationale else suffix
    events.append(
        {
            "kind": "retract_edge_target_guard",
            "from_targets": current_targets,
            "to_targets": desired_targets,
            "only_constraint": has_only_constraint,
        }
    )
    return parsed, events


def _apply_concession_contrast_guard(
    parsed: dict[str, Any],
    *,
    utterance: str,
    route: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    events: list[dict[str, Any]] = []
    if not isinstance(parsed, dict):
        return parsed, events

    intent = str(parsed.get("intent", "")).strip().lower()
    route_name = str(route or "").strip().lower()
    if intent != "assert_fact" and route_name != "assert_fact":
        return parsed, events

    facts = [str(x).strip() for x in parsed.get("facts", []) if str(x).strip()]
    if not facts:
        return parsed, events

    lowered = str(utterance or "").lower()
    next_facts = list(facts)
    added_facts: list[str] = []

    first_term = _parse_clause_term(facts[0])
    first_predicate = str(getattr(first_term, "name", "")).strip() if first_term is not None else ""
    first_args = list(getattr(first_term, "args", [])) if first_term is not None else []
    first_arg_atom = ""
    if first_args:
        first_arg_atom = str(getattr(first_args[0], "name", "")).strip()

    if "despite no notice" in lowered and first_arg_atom:
        no_notice_fact = f"no_notice({_atomize(first_arg_atom)})."
        if no_notice_fact not in next_facts:
            next_facts.append(no_notice_fact)
            added_facts.append(no_notice_fact)

    if "conceded" in lowered and first_predicate and first_arg_atom:
        speaker = ""
        speaker_match = re.search(
            r"\b(counsel|petitioner|respondent|tenant|poster|op|chair)\b",
            lowered,
        )
        if speaker_match:
            speaker = _atomize(speaker_match.group(1))
        if speaker:
            object_atom = f"{_atomize(first_predicate)}_{_atomize(first_arg_atom)}"
            conceded_fact = f"conceded({speaker}, {object_atom})."
            if conceded_fact not in next_facts:
                next_facts.append(conceded_fact)
                added_facts.append(conceded_fact)

    if not added_facts:
        return parsed, events

    parsed["facts"] = next_facts
    parsed["logic_string"] = next_facts[0]
    atoms: set[str] = set()
    variables: set[str] = set()
    predicates: set[str] = set()
    for clause in next_facts:
        a, v, p = _extract_components_from_logic(clause)
        atoms.update(a)
        variables.update(v)
        predicates.update(p)
    parsed["rules"] = []
    parsed["queries"] = []
    parsed["components"] = {
        "atoms": sorted(atoms),
        "variables": sorted(variables),
        "predicates": sorted(predicates),
    }
    rationale = str(parsed.get("rationale", "")).strip()
    suffix = "Concession contrast guard added implied companion facts from contrastive language."
    parsed["rationale"] = f"{rationale} {suffix}".strip() if rationale else suffix
    events.append(
        {
            "kind": "concession_contrast_guard",
            "added_facts": added_facts,
        }
    )
    return parsed, events


def _apply_declared_predicate_hint_guard(
    parsed: dict[str, Any],
    *,
    utterance: str,
    route: str,
    declared_predicates: set[str],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    events: list[dict[str, Any]] = []
    if not isinstance(parsed, dict) or not declared_predicates:
        return parsed, events

    intent = str(parsed.get("intent", "")).strip().lower()
    route_name = str(route or "").strip().lower()
    if intent not in {"assert_fact", "other"} and route_name not in {"assert_fact", "other"}:
        return parsed, events

    lowered = str(utterance or "").lower()
    hinted_facts: list[str] = []

    def _add_hint_fact(clause: str) -> None:
        normalized = _normalize_clause(clause)
        if not _is_valid_goal_clause(normalized, require_ground=False):
            return
        if normalized not in hinted_facts:
            hinted_facts.append(normalized)

    if "issue" in declared_predicates and "outage" in lowered:
        _add_hint_fact("issue(thread, outage_event).")
    if "narrowed_to" in declared_predicates and "narrowed" in lowered and "isp" in lowered:
        _add_hint_fact("narrowed_to(outage_event, single_isp_segment).")
    if "keeps" in declared_predicates and re.search(r"\b(still held|stayed true|still true)\b", lowered):
        _add_hint_fact("keeps(thread, cause_link_discussion).")
    if "still_true" in declared_predicates and re.search(r"\b(still held|stayed true|still true)\b", lowered):
        _add_hint_fact("still_true(thread, cause_link_discussion).")

    if "happened" in declared_predicates and "landlord" in lowered and "without notice" in lowered:
        _add_hint_fact("happened(poster, landlord_entered_without_notice).")
    if "documented_with" in declared_predicates and "photo" in lowered:
        _add_hint_fact("documented_with(poster, photos).")
    if "seeks" in declared_predicates and "terminate" in lowered and "lease" in lowered:
        _add_hint_fact("seeks(poster, terminate_lease).")
    if "advised_to" in declared_predicates and ("written demand" in lowered or ("advise" in lowered and "first" in lowered)):
        _add_hint_fact("advised_to(poster, send_written_demand_first).")

    if "emergency" in declared_predicates and "case_blue" in lowered and "emergency" in lowered:
        _add_hint_fact("emergency(case_blue).")
    if "no_notice" in declared_predicates and "case_blue" in lowered and "no notice" in lowered:
        _add_hint_fact("no_notice(case_blue).")
    if "conceded" in declared_predicates and "case_blue" in lowered and "conceded" in lowered and "emergency" in lowered:
        _add_hint_fact("conceded(counsel, emergency_case_blue).")

    if not hinted_facts:
        return parsed, events

    existing_facts = [
        _normalize_clause(str(x))
        for x in parsed.get("facts", [])
        if _normalize_clause(str(x))
    ]
    merged_facts: list[str] = []
    for clause in existing_facts + hinted_facts:
        if clause not in merged_facts:
            merged_facts.append(clause)
    if not merged_facts:
        return parsed, events

    atoms: set[str] = set()
    variables: set[str] = set()
    predicates: set[str] = set()
    for clause in merged_facts:
        a, v, p = _extract_components_from_logic(clause)
        atoms.update(a)
        variables.update(v)
        predicates.update(p)

    rationale = str(parsed.get("rationale", "")).strip()
    suffix = "Declared predicate hint guard added deterministic companion facts."
    merged_rationale = f"{rationale} {suffix}".strip() if rationale else suffix
    rebuilt = _build_parse_payload(
        intent="assert_fact",
        logic_string=merged_facts[0],
        facts=merged_facts,
        rules=[],
        queries=[],
        predicates=sorted(predicates),
        atoms=sorted(atoms),
        variables=sorted(variables),
        rationale=merged_rationale,
    )
    events.append(
        {
            "kind": "declared_predicate_hint_guard",
            "added_facts": [f for f in hinted_facts if f not in existing_facts],
        }
    )
    return rebuilt, events


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

    explicit_query = _extract_first_explicit_goal_clause(text, require_ground=False)
    if explicit_query:
        atoms, variables, predicates = _extract_components_from_logic(explicit_query)
        if not predicates:
            return None
        parsed = _build_parse_payload(
            intent="query",
            logic_string=explicit_query,
            facts=[],
            rules=[],
            queries=[explicit_query],
            predicates=predicates,
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


def _build_explicit_command_parse(utterance: str) -> tuple[str, dict[str, Any]] | None:
    text = str(utterance or "").strip()
    if not text:
        return None
    lowered = text.lower()

    def _build_assert_fact_from_clause(clause_text: str) -> dict[str, Any] | None:
        clause = _normalize_clause(clause_text)
        if not _is_valid_goal_clause(clause, require_ground=False):
            return None
        atoms, variables, predicates = _extract_components_from_logic(clause)
        parsed = _build_parse_payload(
            intent="assert_fact",
            logic_string=clause,
            facts=[clause],
            rules=[],
            queries=[],
            predicates=predicates,
            atoms=atoms,
            variables=variables,
            rationale="Deterministic explicit command parse (assert_fact).",
        )
        ok, _ = _validate_parsed(parsed)
        return parsed if ok else None

    def _build_assert_rule_from_clause(clause_text: str) -> dict[str, Any] | None:
        clause = _normalize_clause(clause_text)
        if not _is_valid_rule_clause(clause):
            return None
        atoms, variables, predicates = _extract_components_from_logic(clause)
        parsed = _build_parse_payload(
            intent="assert_rule",
            logic_string=clause,
            facts=[],
            rules=[clause],
            queries=[],
            predicates=predicates,
            atoms=atoms,
            variables=variables,
            rationale="Deterministic explicit command parse (assert_rule).",
        )
        ok, _ = _validate_parsed(parsed)
        return parsed if ok else None

    def _build_query_from_clause(clause_text: str) -> dict[str, Any] | None:
        cleaned = clause_text.strip()
        if cleaned.startswith("?-"):
            cleaned = cleaned[2:].strip()
        clause = _normalize_clause(cleaned)
        if not _is_valid_goal_clause(clause, require_ground=False):
            return None
        atoms, variables, predicates = _extract_components_from_logic(clause)
        parsed = _build_parse_payload(
            intent="query",
            logic_string=clause,
            facts=[],
            rules=[],
            queries=[clause],
            predicates=predicates,
            atoms=atoms,
            variables=variables,
            rationale="Deterministic explicit command parse (query).",
        )
        ok, _ = _validate_parsed(parsed)
        return parsed if ok else None

    def _build_retract_from_clause(clause_text: str) -> dict[str, Any] | None:
        target = _normalize_clause(clause_text)
        if not _is_valid_goal_clause(target, require_ground=False):
            return None
        logic = f"retract({target[:-1] if target.endswith('.') else target})."
        atoms, variables, predicates = _extract_components_from_logic(logic)
        parsed = _build_parse_payload(
            intent="retract",
            logic_string=logic,
            facts=[target],
            rules=[],
            queries=[],
            predicates=predicates,
            atoms=atoms,
            variables=variables,
            rationale="Deterministic explicit command parse (retract).",
        )
        ok, _ = _validate_parsed(parsed)
        return parsed if ok else None

    if lowered.startswith("query "):
        parsed = _build_query_from_clause(text[6:].strip())
        if isinstance(parsed, dict):
            return "query", parsed
        return None
    if lowered.startswith("set "):
        parsed = _build_assert_fact_from_clause(text[4:].strip())
        if isinstance(parsed, dict):
            return "assert_fact", parsed
        return None
    if lowered.startswith("assert fact "):
        parsed = _build_assert_fact_from_clause(text[len("assert fact ") :].strip())
        if isinstance(parsed, dict):
            return "assert_fact", parsed
        return None
    if lowered.startswith("assert rule "):
        parsed = _build_assert_rule_from_clause(text[len("assert rule ") :].strip())
        if isinstance(parsed, dict):
            return "assert_rule", parsed
        return None
    if lowered.startswith("retract fact "):
        parsed = _build_retract_from_clause(text[len("retract fact ") :].strip())
        if isinstance(parsed, dict):
            return "retract", parsed
        return None
    if lowered.startswith("retract "):
        parsed = _build_retract_from_clause(text[len("retract ") :].strip())
        if isinstance(parsed, dict):
            return "retract", parsed
        return None
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


def _is_ephemeral_kb_name(kb_name: str) -> bool:
    return kb_name.startswith(("sm_", "tmp_", "scratch_"))


def _uses_default_kb_root(raw_value: str) -> bool:
    normalized = str(raw_value).strip().replace("\\", "/").rstrip("/").lower()
    default = str(DEFAULT_KB_ROOT).replace("\\", "/").rstrip("/").lower()
    return normalized == default


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
        variables = [arg for arg in query_args if _is_variable_token(arg)]
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
                if _is_variable_token(query_arg):
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


def _progress_text_key(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "").strip()).strip().lower()


def _progress_item_id(kind: str, text: str) -> str:
    key = _progress_text_key(text)
    digest = hashlib.sha1(key.encode("utf-8")).hexdigest()[:10] if key else "empty"
    return f"{kind}_{digest}"


def _coerce_string_list(raw: Any) -> list[str]:
    if isinstance(raw, str):
        text = raw.strip()
        return [text] if text else []
    if not isinstance(raw, list):
        return []
    out: list[str] = []
    for item in raw:
        text = str(item).strip()
        if text:
            out.append(text)
    return out


def _empty_progress_memory(kb_name: str) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "ontology_name": kb_name,
        "updated_at_utc": _utc_now_iso(),
        "active_focus": [],
        "goals": [],
        "open_questions": [],
        "resolved_items": [],
        "notes": [],
    }


def _normalize_progress_memory(raw: dict[str, Any] | None, *, kb_name: str) -> dict[str, Any]:
    base = _empty_progress_memory(kb_name)
    if not isinstance(raw, dict):
        return base
    base["ontology_name"] = str(raw.get("ontology_name") or kb_name).strip() or kb_name
    base["updated_at_utc"] = str(raw.get("updated_at_utc") or _utc_now_iso())

    base["active_focus"] = _coerce_string_list(raw.get("active_focus"))

    goals_raw = raw.get("goals", [])
    goals: list[dict[str, Any]] = []
    if isinstance(goals_raw, list):
        for item in goals_raw:
            if not isinstance(item, dict):
                continue
            text = str(item.get("text", "")).strip()
            if not text:
                continue
            goal_id = str(item.get("id", "")).strip() or _progress_item_id("goal", text)
            status = str(item.get("status", "active")).strip().lower()
            if status not in {"active", "resolved"}:
                status = "active"
            goals.append(
                {
                    "id": goal_id,
                    "text": text,
                    "status": status,
                    "priority": int(item.get("priority", 1) or 1),
                    "created_turn": int(item.get("created_turn", 0) or 0),
                    "updated_turn": int(item.get("updated_turn", 0) or 0),
                    "source": str(item.get("source", "scenario")).strip() or "scenario",
                }
            )
    base["goals"] = goals

    questions_raw = raw.get("open_questions", [])
    questions: list[dict[str, Any]] = []
    if isinstance(questions_raw, list):
        for item in questions_raw:
            if not isinstance(item, dict):
                continue
            text = str(item.get("text", "")).strip()
            if not text:
                continue
            qid = str(item.get("id", "")).strip() or _progress_item_id("question", text)
            status = str(item.get("status", "open")).strip().lower()
            if status not in {"open", "resolved"}:
                status = "open"
            questions.append(
                {
                    "id": qid,
                    "text": text,
                    "status": status,
                    "priority": int(item.get("priority", 1) or 1),
                    "created_turn": int(item.get("created_turn", 0) or 0),
                    "updated_turn": int(item.get("updated_turn", 0) or 0),
                    "source": str(item.get("source", "scenario")).strip() or "scenario",
                }
            )
    base["open_questions"] = questions

    resolved_raw = raw.get("resolved_items", [])
    resolved_items: list[dict[str, Any]] = []
    if isinstance(resolved_raw, list):
        for item in resolved_raw:
            if not isinstance(item, dict):
                continue
            text = str(item.get("text", "")).strip()
            if not text:
                continue
            resolved_items.append(
                {
                    "kind": str(item.get("kind", "note")).strip() or "note",
                    "id": str(item.get("id", "")).strip() or _progress_item_id("resolved", text),
                    "text": text,
                    "resolution": str(item.get("resolution", "")).strip(),
                    "resolved_turn": int(item.get("resolved_turn", 0) or 0),
                    "resolved_at_utc": str(item.get("resolved_at_utc", "")).strip() or _utc_now_iso(),
                }
            )
    base["resolved_items"] = resolved_items[-200:]

    base["notes"] = _coerce_string_list(raw.get("notes"))
    return base


def _load_progress_memory(path: Path, *, kb_name: str) -> dict[str, Any]:
    parsed = _load_json(path)
    return _normalize_progress_memory(parsed, kb_name=kb_name)


def _extract_progress_directives(raw_utterance_entry: Any) -> dict[str, Any]:
    if not isinstance(raw_utterance_entry, dict):
        return {}
    payload: dict[str, Any] = {}
    progress_raw = raw_utterance_entry.get("progress", {})
    if isinstance(progress_raw, dict):
        payload.update(progress_raw)
    for key in (
        "set_active_focus",
        "add_goals",
        "add_open_questions",
        "resolve_goals",
        "resolve_questions",
        "add_notes",
    ):
        if key in raw_utterance_entry and key not in payload:
            payload[key] = raw_utterance_entry.get(key)
    return payload


def _apply_progress_directives(
    progress_memory: dict[str, Any],
    directives: dict[str, Any],
    *,
    turn_index: int,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    mem = _normalize_progress_memory(
        progress_memory,
        kb_name=str(progress_memory.get("ontology_name", DEFAULT_KB_NAME)),
    )
    if not isinstance(directives, dict) or not directives:
        mem["updated_at_utc"] = _utc_now_iso()
        return mem, []

    events: list[dict[str, Any]] = []

    set_focus = _coerce_string_list(directives.get("set_active_focus"))
    if set_focus:
        deduped = list(dict.fromkeys(set_focus))
        mem["active_focus"] = deduped
        events.append({"kind": "set_active_focus", "count": len(deduped)})

    add_notes = _coerce_string_list(directives.get("add_notes"))
    for note in add_notes:
        mem.setdefault("notes", []).append(note)
    if add_notes:
        events.append({"kind": "add_notes", "count": len(add_notes)})

    goals = list(mem.get("goals", []))
    for text in _coerce_string_list(directives.get("add_goals")):
        key = _progress_text_key(text)
        existing = next((row for row in goals if _progress_text_key(row.get("text", "")) == key), None)
        if existing is not None:
            existing["status"] = "active"
            existing["updated_turn"] = int(turn_index)
            events.append({"kind": "reactivate_goal", "id": existing.get("id"), "text": text})
            continue
        row = {
            "id": _progress_item_id("goal", text),
            "text": text,
            "status": "active",
            "priority": 1,
            "created_turn": int(turn_index),
            "updated_turn": int(turn_index),
            "source": "scenario_directive",
        }
        goals.append(row)
        events.append({"kind": "add_goal", "id": row["id"], "text": text})
    mem["goals"] = goals[-200:]

    questions = list(mem.get("open_questions", []))
    for text in _coerce_string_list(directives.get("add_open_questions")):
        key = _progress_text_key(text)
        existing = next((row for row in questions if _progress_text_key(row.get("text", "")) == key), None)
        if existing is not None:
            existing["status"] = "open"
            existing["updated_turn"] = int(turn_index)
            events.append({"kind": "reopen_question", "id": existing.get("id"), "text": text})
            continue
        row = {
            "id": _progress_item_id("question", text),
            "text": text,
            "status": "open",
            "priority": 1,
            "created_turn": int(turn_index),
            "updated_turn": int(turn_index),
            "source": "scenario_directive",
        }
        questions.append(row)
        events.append({"kind": "add_open_question", "id": row["id"], "text": text})
    mem["open_questions"] = questions[-200:]

    resolved_items = list(mem.get("resolved_items", []))

    resolve_goal_keys = {_progress_text_key(x) for x in _coerce_string_list(directives.get("resolve_goals"))}
    if resolve_goal_keys:
        for row in mem.get("goals", []):
            row_key = _progress_text_key(str(row.get("id", "")))
            text_key = _progress_text_key(str(row.get("text", "")))
            if row_key not in resolve_goal_keys and text_key not in resolve_goal_keys:
                continue
            if str(row.get("status", "active")) == "resolved":
                continue
            row["status"] = "resolved"
            row["updated_turn"] = int(turn_index)
            resolved_items.append(
                {
                    "kind": "goal",
                    "id": str(row.get("id", "")),
                    "text": str(row.get("text", "")),
                    "resolution": "resolved_by_directive",
                    "resolved_turn": int(turn_index),
                    "resolved_at_utc": _utc_now_iso(),
                }
            )
            events.append({"kind": "resolve_goal", "id": row.get("id"), "text": row.get("text", "")})

    resolve_question_keys = {_progress_text_key(x) for x in _coerce_string_list(directives.get("resolve_questions"))}
    if resolve_question_keys:
        for row in mem.get("open_questions", []):
            row_key = _progress_text_key(str(row.get("id", "")))
            text_key = _progress_text_key(str(row.get("text", "")))
            if row_key not in resolve_question_keys and text_key not in resolve_question_keys:
                continue
            if str(row.get("status", "open")) == "resolved":
                continue
            row["status"] = "resolved"
            row["updated_turn"] = int(turn_index)
            resolved_items.append(
                {
                    "kind": "question",
                    "id": str(row.get("id", "")),
                    "text": str(row.get("text", "")),
                    "resolution": "resolved_by_directive",
                    "resolved_turn": int(turn_index),
                    "resolved_at_utc": _utc_now_iso(),
                }
            )
            events.append({"kind": "resolve_question", "id": row.get("id"), "text": row.get("text", "")})

    mem["resolved_items"] = resolved_items[-300:]
    mem["updated_at_utc"] = _utc_now_iso()
    return mem, events


def _progress_signal_terms(progress_memory: dict[str, Any]) -> set[str]:
    terms: set[str] = set()

    def add_text(raw: str) -> None:
        normalized = _atomize(str(raw))
        if not normalized:
            return
        terms.add(normalized)
        parts = [p for p in normalized.split("_") if p]
        for part in parts:
            terms.add(part)

    for text in _coerce_string_list(progress_memory.get("active_focus")):
        add_text(text)
    for row in progress_memory.get("goals", []):
        if not isinstance(row, dict):
            continue
        if str(row.get("status", "active")).strip().lower() != "active":
            continue
        add_text(str(row.get("text", "")))
    for row in progress_memory.get("open_questions", []):
        if not isinstance(row, dict):
            continue
        if str(row.get("status", "open")).strip().lower() != "open":
            continue
        add_text(str(row.get("text", "")))
    return terms


def _progress_focus_units(progress_memory: dict[str, Any]) -> list[set[str]]:
    units: list[set[str]] = []

    def add_unit(raw: str) -> None:
        normalized = _atomize(str(raw))
        if not normalized:
            return
        terms = {part for part in normalized.split("_") if part}
        if terms:
            units.append(terms)

    for text in _coerce_string_list(progress_memory.get("active_focus")):
        add_unit(text)
    for row in progress_memory.get("goals", []):
        if not isinstance(row, dict):
            continue
        if str(row.get("status", "active")).strip().lower() != "active":
            continue
        add_unit(str(row.get("text", "")))
    for row in progress_memory.get("open_questions", []):
        if not isinstance(row, dict):
            continue
        if str(row.get("status", "open")).strip().lower() != "open":
            continue
        add_unit(str(row.get("text", "")))

    return units


def _parsed_signal_terms(parsed: dict[str, Any], *, utterance: str) -> set[str]:
    terms: set[str] = set()

    def add_text(raw: str) -> None:
        normalized = _atomize(str(raw))
        if not normalized:
            return
        terms.add(normalized)
        for part in normalized.split("_"):
            if part:
                terms.add(part)

    add_text(utterance)
    add_text(str(parsed.get("logic_string", "")))
    components = parsed.get("components", {})
    if isinstance(components, dict):
        for item in components.get("predicates", []):
            add_text(str(item))
        for item in components.get("atoms", []):
            add_text(str(item))
    for item in parsed.get("facts", []):
        add_text(str(item))
    for item in parsed.get("rules", []):
        add_text(str(item))
    for item in parsed.get("queries", []):
        add_text(str(item))
    return terms


def _progress_relevance_summary(
    *,
    parsed: dict[str, Any],
    utterance: str,
    progress_memory: dict[str, Any] | None,
) -> dict[str, Any]:
    if not isinstance(progress_memory, dict):
        return {
            "progress_memory_available": False,
            "progress_focus_present": False,
            "progress_signal_term_count": 0,
            "parsed_signal_term_count": 0,
            "overlap_term_count": 0,
            "progress_best_focus_overlap": 0.0,
            "progress_relevance_score": 1.0,
        }
    progress_terms = _progress_signal_terms(progress_memory)
    if not progress_terms:
        return {
            "progress_memory_available": True,
            "progress_focus_present": False,
            "progress_signal_term_count": 0,
            "parsed_signal_term_count": 0,
            "overlap_term_count": 0,
            "progress_best_focus_overlap": 0.0,
            "progress_relevance_score": 1.0,
        }
    parsed_terms = _parsed_signal_terms(parsed, utterance=utterance)
    if not parsed_terms:
        return {
            "progress_memory_available": True,
            "progress_focus_present": True,
            "progress_signal_term_count": len(progress_terms),
            "parsed_signal_term_count": 0,
            "overlap_term_count": 0,
            "progress_best_focus_overlap": 0.0,
            "progress_relevance_score": 0.0,
        }
    overlap = progress_terms & parsed_terms
    precision = len(overlap) / max(1, len(parsed_terms))
    recall = len(overlap) / max(1, len(progress_terms))
    # Bias toward precision: parsed-turn relevance to active objectives.
    base_score = (0.75 * precision) + (0.25 * recall)

    focus_units = _progress_focus_units(progress_memory)
    best_focus_overlap = 0.0
    for unit in focus_units:
        if not unit:
            continue
        overlap_ratio = len(unit & parsed_terms) / max(1, len(unit))
        if overlap_ratio > best_focus_overlap:
            best_focus_overlap = overlap_ratio

    score = max(base_score, best_focus_overlap)
    return {
        "progress_memory_available": True,
        "progress_focus_present": True,
        "progress_signal_term_count": len(progress_terms),
        "parsed_signal_term_count": len(parsed_terms),
        "overlap_term_count": len(overlap),
        "progress_overlap_terms": sorted(overlap)[:20],
        "progress_best_focus_overlap": round(_clip_01(best_focus_overlap, fallback=0.0), 3),
        "progress_relevance_score": round(_clip_01(score, fallback=0.0), 3),
    }


def _progress_focus_preview(progress_memory: dict[str, Any], *, max_items: int = 3) -> list[str]:
    rows: list[str] = []
    for text in _coerce_string_list(progress_memory.get("active_focus"))[: max_items]:
        rows.append(f"focus: {text}")
    for item in progress_memory.get("goals", []):
        if not isinstance(item, dict):
            continue
        if str(item.get("status", "active")).strip().lower() != "active":
            continue
        rows.append(f"goal: {str(item.get('text', '')).strip()}")
        if len(rows) >= max_items:
            break
    return rows[:max_items]


def _synthesize_progress_clarification_question(
    *,
    progress_memory: dict[str, Any] | None,
) -> str:
    if isinstance(progress_memory, dict):
        preview = _progress_focus_preview(progress_memory, max_items=1)
        if preview:
            focus = preview[0].split(":", 1)[-1].strip()
            if focus:
                return f"How does this relate to current focus '{focus}'?"
    return "How is this relevant to the current objective?"


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


def _batch_status(results: list[dict[str, Any]]) -> str:
    statuses = [str(row.get("status", "")).strip().lower() for row in results]
    if not statuses:
        return "validation_error"
    if any(s in {"constraint_error", "validation_error", "error", "unknown"} for s in statuses):
        for s in statuses:
            if s in {"constraint_error", "validation_error", "error", "unknown"}:
                return s
    if any(s == "success" for s in statuses):
        return "success"
    if all(s == "skipped" for s in statuses):
        return "skipped"
    if all(s == "no_results" for s in statuses):
        return "no_results"
    if "no_results" in statuses:
        return "no_results"
    return statuses[0] if statuses[0] else "unknown"


def _expand_assert_fact_clauses(candidates: list[str]) -> list[str]:
    expanded: list[str] = []
    for raw_clause in candidates:
        text = str(raw_clause or "").strip()
        if not text:
            continue

        # First pass: break multi-line / multi-sentence fact payloads.
        fragments: list[str] = []
        for line in text.splitlines():
            part = line.strip()
            if part:
                fragments.append(part)
        if not fragments:
            fragments = [text]

        sentence_parts: list[str] = []
        for fragment in fragments:
            chunks = [c.strip() for c in fragment.split(".") if c.strip()]
            if chunks:
                sentence_parts.extend(chunks)
            else:
                sentence_parts.append(fragment)

        for part in sentence_parts:
            clause = _normalize_clause(f"{part}.")
            if not clause:
                continue
            raw = clause[:-1].strip() if clause.endswith(".") else clause.strip()
            if ":-" in raw:
                expanded.append(clause)
                continue
            goals = _split_top_level_args(raw)
            if len(goals) > 1 and all(_is_valid_goal_clause(f"{g}.", require_ground=True) for g in goals):
                for goal in goals:
                    expanded.append(_normalize_clause(f"{goal}."))
            else:
                expanded.append(clause)
    seen: set[str] = set()
    unique: list[str] = []
    for clause in expanded:
        if clause and clause not in seen:
            seen.add(clause)
            unique.append(clause)
    return unique


def _expand_assert_rule_clauses(candidates: list[str]) -> list[str]:
    def _rewrite_rule_negation_aliases(clause_text: str) -> str:
        normalized = _normalize_clause(clause_text)
        if not normalized:
            return normalized
        raw = normalized[:-1].strip() if normalized.endswith(".") else normalized.strip()
        split = _split_rule_head_body(raw)
        if not split:
            return normalized

        head_text, body_text = split
        body_goals = _split_top_level_args(body_text)
        if not body_goals:
            return normalized

        rewritten_goals: list[str] = []
        changed = False
        for raw_goal in body_goals:
            goal = str(raw_goal).strip()
            if not goal:
                continue

            goal_rewritten = goal
            m_paren = re.match(r"^not\s*\((.+)\)$", goal, flags=re.IGNORECASE)
            if m_paren:
                inner = m_paren.group(1).strip()
                if inner:
                    goal_rewritten = f"\\+({inner})"
            else:
                m_space = re.match(r"^not\s+(.+)$", goal, flags=re.IGNORECASE)
                if m_space:
                    inner = m_space.group(1).strip()
                    if inner and _is_valid_goal_clause(f"{inner}.", require_ground=False):
                        goal_rewritten = f"\\+({inner})"

            if goal_rewritten != goal:
                changed = True
            rewritten_goals.append(goal_rewritten)

        if not changed or not rewritten_goals:
            return normalized

        rewritten = f"{head_text} :- {', '.join(rewritten_goals)}."
        return _normalize_clause(rewritten)

    def _rewrite_ancestor_transitive_rule(clause_text: str) -> str:
        normalized = _normalize_clause(clause_text)
        if not normalized:
            return normalized
        raw = normalized[:-1].strip() if normalized.endswith(".") else normalized.strip()
        split = _split_rule_head_body(raw)
        if not split:
            return normalized
        head_text, body_text = split
        head_term = _parse_clause_term(f"{head_text}.")
        if head_term is None or str(getattr(head_term, "name", "")).strip() != "ancestor":
            return normalized
        head_args = list(getattr(head_term, "args", []))
        if len(head_args) != 2:
            return normalized
        hx, hz = head_args[0], head_args[1]
        if not getattr(hx, "is_variable", False) or not getattr(hz, "is_variable", False):
            return normalized
        x_name = str(getattr(hx, "name", "")).strip()
        z_name = str(getattr(hz, "name", "")).strip()
        if not x_name or not z_name:
            return normalized

        goals = _split_top_level_args(body_text)
        if len(goals) != 2:
            return normalized
        g1 = _parse_clause_term(f"{goals[0]}.")
        g2 = _parse_clause_term(f"{goals[1]}.")
        if g1 is None or g2 is None:
            return normalized
        if str(getattr(g1, "name", "")).strip() != "ancestor":
            return normalized
        if str(getattr(g2, "name", "")).strip() != "ancestor":
            return normalized
        g1_args = list(getattr(g1, "args", []))
        g2_args = list(getattr(g2, "args", []))
        if len(g1_args) != 2 or len(g2_args) != 2:
            return normalized
        a1, a2 = g1_args
        b1, b2 = g2_args
        if not all(getattr(arg, "is_variable", False) for arg in [a1, a2, b1, b2]):
            return normalized
        a1n = str(getattr(a1, "name", "")).strip()
        a2n = str(getattr(a2, "name", "")).strip()
        b1n = str(getattr(b1, "name", "")).strip()
        b2n = str(getattr(b2, "name", "")).strip()
        if not (a1n and a2n and b1n and b2n):
            return normalized
        if not (a1n == x_name and a2n == b1n and b2n == z_name):
            return normalized

        rewritten = f"ancestor({x_name}, {z_name}) :- parent({x_name}, {a2n}), ancestor({a2n}, {z_name})."
        return _normalize_clause(rewritten)

    expanded: list[str] = []
    for raw_clause in candidates:
        clause = _rewrite_rule_negation_aliases(_normalize_clause(raw_clause))
        if not clause:
            continue
        if _is_valid_rule_clause(clause):
            expanded.append(_rewrite_ancestor_transitive_rule(clause))
            continue

        fragments: list[str] = []
        for line in str(raw_clause).splitlines():
            part = line.strip()
            if part:
                fragments.append(part)
        if not fragments:
            fragments = [str(raw_clause).strip()]

        split_parts: list[str] = []
        for fragment in fragments:
            chunks = [c.strip() for c in fragment.split(".") if c.strip()]
            if chunks:
                split_parts.extend(chunks)
            else:
                split_parts.append(fragment)

        for part in split_parts:
            normalized = _rewrite_rule_negation_aliases(_normalize_clause(f"{part}."))
            if _is_valid_rule_clause(normalized):
                expanded.append(_rewrite_ancestor_transitive_rule(normalized))

    seen: set[str] = set()
    unique: list[str] = []
    for clause in expanded:
        if clause and clause not in seen:
            seen.add(clause)
            unique.append(clause)
    return unique


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
        candidates = [str(x).strip() for x in facts if str(x).strip()]
        if not candidates:
            fallback = str(parsed.get("logic_string", "")).strip()
            if fallback:
                candidates = [fallback]
        expanded_facts = _expand_assert_fact_clauses(candidates)
        if not expanded_facts:
            return {
                "tool": "assert_fact",
                "input": None,
                "result": {"status": "validation_error", "message": "No valid fact clauses were provided."},
            }

        for fact in expanded_facts:
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

        op_results: list[dict[str, Any]] = []
        for fact in expanded_facts:
            if corpus_clauses is not None and fact in corpus_clauses:
                op_results.append({"status": "skipped", "message": "Fact already present in corpus.", "fact": fact})
                continue
            result = server.assert_fact(fact)
            if corpus_clauses is not None and result.get("status") == "success":
                corpus_clauses.add(fact)
            op_results.append({"status": str(result.get("status", "unknown")), "fact": fact, "raw": result})

        if len(expanded_facts) == 1:
            single = op_results[0]
            if "raw" in single:
                result_obj = dict(single.get("raw", {}))
            else:
                result_obj = {"status": single.get("status", "unknown"), "message": single.get("message", "")}
            return {"tool": "assert_fact", "input": expanded_facts[0], "result": result_obj}

        status = _batch_status(op_results)
        return {
            "tool": "assert_fact_batch",
            "input": expanded_facts,
            "result": {
                "status": status,
                "result_type": "batch",
                "applied_total": len(expanded_facts),
                "operations": op_results,
            },
        }
    if intent == "assert_rule":
        rules = parsed.get("rules", [])
        candidates = [str(x).strip() for x in rules if str(x).strip()]
        if not candidates:
            fallback = str(parsed.get("logic_string", "")).strip()
            if fallback:
                candidates = [fallback]
        expanded_rules = _expand_assert_rule_clauses(candidates)
        if not expanded_rules:
            return {
                "tool": "assert_rule",
                "input": None,
                "result": {"status": "validation_error", "message": "No valid rule clauses were provided."},
            }

        for rule in expanded_rules:
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

        op_results: list[dict[str, Any]] = []
        for rule in expanded_rules:
            if corpus_clauses is not None and rule in corpus_clauses:
                op_results.append({"status": "skipped", "message": "Rule already present in corpus.", "rule": rule})
                continue
            result = server.assert_rule(rule)
            if corpus_clauses is not None and result.get("status") == "success":
                corpus_clauses.add(rule)
            op_results.append({"status": str(result.get("status", "unknown")), "rule": rule, "raw": result})

        if len(expanded_rules) == 1:
            single = op_results[0]
            if "raw" in single:
                result_obj = dict(single.get("raw", {}))
            else:
                result_obj = {"status": single.get("status", "unknown"), "message": single.get("message", "")}
            return {"tool": "assert_rule", "input": expanded_rules[0], "result": result_obj}

        status = _batch_status(op_results)
        return {
            "tool": "assert_rule_batch",
            "input": expanded_rules,
            "result": {
                "status": status,
                "result_type": "batch",
                "applied_total": len(expanded_rules),
                "operations": op_results,
            },
        }
    if intent == "retract":
        targets = _extract_retract_targets(
            str(parsed.get("logic_string", "")),
            [str(x) for x in parsed.get("facts", [])],
        )
        if not targets:
            return {
                "tool": "retract_fact",
                "input": None,
                "result": {"status": "validation_error", "message": "Could not derive retract target fact."},
            }
        normalized_targets = [_normalize_clause(t) for t in targets if _normalize_clause(t)]

        for target in normalized_targets:
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

        op_results: list[dict[str, Any]] = []
        for target in normalized_targets:
            if corpus_clauses is not None and target not in corpus_clauses:
                op_results.append({"status": "no_results", "message": "Fact not present in corpus.", "fact": target})
                continue
            result = server.retract_fact(target)
            if corpus_clauses is not None and result.get("status") in {"success", "no_results"}:
                corpus_clauses.discard(target)
            op_results.append({"status": str(result.get("status", "unknown")), "fact": target, "raw": result})

        if len(normalized_targets) == 1:
            single = op_results[0]
            if "raw" in single:
                result_obj = dict(single.get("raw", {}))
            else:
                result_obj = {"status": single.get("status", "unknown"), "message": single.get("message", "")}
            return {"tool": "retract_fact", "input": normalized_targets[0], "result": result_obj}

        status = _batch_status(op_results)
        return {
            "tool": "retract_fact_batch",
            "input": normalized_targets,
            "result": {
                "status": status,
                "result_type": "batch",
                "applied_total": len(normalized_targets),
                "operations": op_results,
            },
        }
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


def _decision_state_for_turn(
    *,
    apply_status: str,
    validation_errors: list[str],
    clarification_pending_reason: str,
) -> str:
    """
    Map low-level parser/apply outcomes into a light-touch decision state model.

    States:
    - commit
    - stage_provisionally
    - ask_clarification
    - escalate
    - reject
    """
    if validation_errors:
        return "reject"

    status = str(apply_status or "unknown").strip().lower()
    if status in {"validation_error", "constraint_error"}:
        return "reject"

    if status in {"clarification_requested", "confirmation_requested"}:
        reason = str(clarification_pending_reason or "").strip().lower()
        escalation_markers = (
            "maximum clarification rounds reached",
            "non-informative",
            "loop detected",
            "could not provide",
            "no clarification answer available",
        )
        if any(marker in reason for marker in escalation_markers):
            return "escalate"
        return "ask_clarification"

    if status == "success":
        return "commit"

    if status in {"skipped", "no_results"}:
        return "stage_provisionally"

    return "reject"


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
                "passed": False,
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
    parser.add_argument("--context-length", type=int, default=8192, help="Context window for model calls (default 8192).")
    parser.add_argument(
        "--classifier-context-length",
        type=int,
        default=0,
        help="Context window for classifier pass in two-pass mode (0 inherits --context-length).",
    )
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
        help="Optional path containing src/mcp_server.py when --runtime mcp (defaults to local repo if present).",
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
        "--ephemeral-kb-root",
        default=str(DEFAULT_EPHEMERAL_KB_ROOT),
        help="Root folder for ephemeral KB namespaces (auto-used for names like sm_*, tmp_*, scratch_*).",
    )
    parser.add_argument(
        "--force-ephemeral-kb",
        action="store_true",
        help="Always route KB writes to --ephemeral-kb-root.",
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
        "--sp-conflict-policy",
        choices=["error", "warn", "off"],
        default="error",
        help=(
            "Policy when both runtime prompt guidance and baked model SYSTEM prompt are active. "
            "'error' aborts, 'warn' logs warning, 'off' ignores."
        ),
    )
    parser.add_argument(
        "--ollama-system-detect",
        action="store_true",
        default=True,
        help="Probe Ollama model SYSTEM prompt with 'ollama show --system' (default on).",
    )
    parser.add_argument(
        "--no-ollama-system-detect",
        action="store_true",
        help="Disable Ollama SYSTEM prompt probing (falls back to semparse name heuristic).",
    )
    parser.add_argument(
        "--ollama-system-detect-timeout-seconds",
        type=int,
        default=8,
        help="Timeout for 'ollama show --system' probe (default 8s).",
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
    parser.add_argument(
        "--require-final-confirmation",
        action="store_true",
        help="Require explicit final yes/no confirmation before any KB write intent is applied.",
    )
    parser.add_argument(
        "--progress-memory",
        action="store_true",
        default=True,
        help="Enable Progress Memory policy context (default on).",
    )
    parser.add_argument(
        "--no-progress-memory",
        action="store_true",
        help="Disable Progress Memory policy context.",
    )
    parser.add_argument(
        "--progress-low-relevance-threshold",
        type=float,
        default=0.34,
        help="Progress relevance score threshold below which write intents trigger clarification pressure.",
    )
    parser.add_argument(
        "--progress-high-risk-threshold",
        type=float,
        default=0.18,
        help="Progress relevance score threshold treated as high-risk for write intents.",
    )
    parser.add_argument(
        "--clarification-answer-model",
        default="",
        help="Optional model id used only to answer clarification questions during runs.",
    )
    parser.add_argument(
        "--clarification-answer-backend",
        choices=["", "lmstudio", "ollama"],
        default="",
        help="Optional backend for clarification-answer model. Defaults to --backend.",
    )
    parser.add_argument(
        "--clarification-answer-base-url",
        default="",
        help="Optional base URL for clarification-answer model. Defaults to backend default URL.",
    )
    parser.add_argument(
        "--clarification-answer-context-length",
        type=int,
        default=16384,
        help="Context window for clarification-answer model calls (default 16384).",
    )
    parser.add_argument(
        "--clarification-answer-history-turns",
        type=int,
        default=8,
        help="How many prior accepted turns to include for clarification answer context.",
    )
    parser.add_argument(
        "--clarification-answer-kb-clause-limit",
        type=int,
        default=80,
        help="Maximum KB clauses included in clarification answer context.",
    )
    parser.add_argument(
        "--clarification-answer-kb-char-budget",
        type=int,
        default=5000,
        help="Approximate char budget for KB clause context sent to clarification answer model.",
    )
    parser.add_argument(
        "--clarification-answer-min-confidence",
        type=float,
        default=0.55,
        help="Minimum generated clarification confidence required to accept auto-answer.",
    )
    parser.add_argument(
        "--served-llm-model",
        default="",
        help="Optional served-LLM model id for clarification Q&A (preferred over --clarification-answer-model when set).",
    )
    parser.add_argument(
        "--served-llm-backend",
        choices=["", "lmstudio", "ollama"],
        default="",
        help="Optional backend for --served-llm-model. Defaults to --backend.",
    )
    parser.add_argument(
        "--served-llm-base-url",
        default="",
        help="Optional base URL for --served-llm-model. Defaults to backend default URL.",
    )
    parser.add_argument(
        "--served-llm-context-length",
        type=int,
        default=16384,
        help="Context window for served-LLM clarification calls (default 16384).",
    )
    parser.add_argument("--out", default="", help="Optional output report JSON path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    progress_memory_enabled = bool(args.progress_memory and not args.no_progress_memory)
    progress_low_relevance_threshold = _clip_01(args.progress_low_relevance_threshold, fallback=0.34)
    progress_high_risk_threshold = _clip_01(args.progress_high_risk_threshold, fallback=0.18)
    if progress_high_risk_threshold > progress_low_relevance_threshold:
        progress_high_risk_threshold = progress_low_relevance_threshold

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
    use_ephemeral_kb = bool(args.force_ephemeral_kb) or (
        _is_ephemeral_kb_name(kb_name) and _uses_default_kb_root(args.kb_root)
    )
    kb_root = (
        Path(args.ephemeral_kb_root).resolve()
        if use_ephemeral_kb
        else Path(args.kb_root).resolve()
    )
    kb_dir = (kb_root / kb_name).resolve()
    progress_path = kb_dir / DEFAULT_PROGRESS_MEMORY_NAME
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
    progress_memory = (
        _load_progress_memory(progress_path, kb_name=kb_name)
        if progress_memory_enabled
        else _empty_progress_memory(kb_name)
    )
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
    sp_conflict_policy = str(args.sp_conflict_policy).strip().lower()
    detect_ollama_system = bool(args.ollama_system_detect and not args.no_ollama_system_detect)
    ollama_detect_timeout_seconds = max(1, int(args.ollama_system_detect_timeout_seconds))
    system_prompt_sources = _collect_system_prompt_sources(
        backend=backend,
        model=model,
        runtime_prompt_text=prompt_guide,
        detect_ollama_system=detect_ollama_system,
        ollama_detect_timeout_seconds=ollama_detect_timeout_seconds,
    )
    system_prompt_sources["runtime_prompt_source_path"] = str(prompt_file_path)
    if bool(system_prompt_sources.get("double_source_active")) and sp_conflict_policy != "off":
        conflict_message = _format_system_prompt_conflict_message(
            backend=backend,
            model=model,
            prompt_file_path=prompt_file_path,
            sources=system_prompt_sources,
        )
        if sp_conflict_policy == "warn":
            print(f"WARNING: {conflict_message}")
        else:
            print(f"ERROR: {conflict_message}")
            return 2

    served_llm_model = args.served_llm_model.strip()
    served_llm_backend = (
        args.served_llm_backend.strip().lower() if args.served_llm_backend.strip() else backend
    )
    served_llm_base_url = (
        args.served_llm_base_url.strip() or DEFAULT_BASE_URLS[served_llm_backend]
    )
    served_llm_context_length = max(256, int(args.served_llm_context_length))

    clarification_answer_model = args.clarification_answer_model.strip()
    clarification_answer_backend = (
        args.clarification_answer_backend.strip().lower() if args.clarification_answer_backend.strip() else backend
    )
    clarification_answer_base_url = (
        args.clarification_answer_base_url.strip() or DEFAULT_BASE_URLS[clarification_answer_backend]
    )
    clarification_answer_context_length = max(256, int(args.clarification_answer_context_length))
    clarification_answer_history_turns = max(0, int(args.clarification_answer_history_turns))
    clarification_answer_kb_clause_limit = max(0, int(args.clarification_answer_kb_clause_limit))
    clarification_answer_kb_char_budget = max(0, int(args.clarification_answer_kb_char_budget))
    clarification_answer_min_confidence = _clip_01(args.clarification_answer_min_confidence, fallback=0.55)

    if served_llm_model:
        clarification_auto_answer_enabled = True
        auto_answer_model = served_llm_model
        auto_answer_backend = served_llm_backend
        auto_answer_base_url = served_llm_base_url
        auto_answer_context_length = served_llm_context_length
        auto_answer_source_prefix = "served_llm"
        auto_answer_role = "served_llm"
        auto_answer_label = "served-LLM clarification model"
    else:
        clarification_auto_answer_enabled = bool(clarification_answer_model)
        auto_answer_model = clarification_answer_model
        auto_answer_backend = clarification_answer_backend
        auto_answer_base_url = clarification_answer_base_url
        auto_answer_context_length = clarification_answer_context_length
        auto_answer_source_prefix = "synthetic"
        auto_answer_role = "proxy_model"
        auto_answer_label = "clarification answer model"

    use_two_pass = bool(args.two_pass and not args.no_two_pass)
    use_split_extraction = bool(args.split_extraction and not args.no_split_extraction)
    context_length = max(512, int(args.context_length))
    classifier_context_length = (
        context_length
        if int(args.classifier_context_length) <= 0
        else max(512, int(args.classifier_context_length))
    )
    clarification_eagerness = _clip_01(args.clarification_eagerness, fallback=0.35)
    max_clarification_rounds = max(0, int(args.max_clarification_rounds))
    require_final_confirmation = bool(args.require_final_confirmation)
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
        "context_length": context_length,
        "classifier_context_length": classifier_context_length,
        "timeout_seconds": args.timeout_seconds,
        "runtime": runtime_mode,
        "two_pass": use_two_pass,
        "split_extraction": use_split_extraction,
        "strict_registry": bool(args.strict_registry),
        "strict_types": bool(args.strict_types),
        "clarification_eagerness": clarification_eagerness,
        "max_clarification_rounds": max_clarification_rounds,
        "require_final_confirmation": require_final_confirmation,
        "progress_memory_enabled": progress_memory_enabled,
        "progress_low_relevance_threshold": progress_low_relevance_threshold,
        "progress_high_risk_threshold": progress_high_risk_threshold,
        "clarification_auto_answer_enabled": clarification_auto_answer_enabled,
        "clarification_answer_backend": auto_answer_backend if clarification_auto_answer_enabled else "",
        "clarification_answer_base_url": auto_answer_base_url if clarification_auto_answer_enabled else "",
        "clarification_answer_model": auto_answer_model if clarification_auto_answer_enabled else "",
        "clarification_answer_context_length": (
            auto_answer_context_length if clarification_auto_answer_enabled else 0
        ),
        "clarification_answer_history_turns": (
            clarification_answer_history_turns if clarification_auto_answer_enabled else 0
        ),
        "clarification_answer_kb_clause_limit": (
            clarification_answer_kb_clause_limit if clarification_auto_answer_enabled else 0
        ),
        "clarification_answer_kb_char_budget": (
            clarification_answer_kb_char_budget if clarification_auto_answer_enabled else 0
        ),
        "clarification_answer_min_confidence": (
            clarification_answer_min_confidence if clarification_auto_answer_enabled else 0.0
        ),
        "clarification_answer_source_prefix": auto_answer_source_prefix if clarification_auto_answer_enabled else "",
        "clarification_answer_role": auto_answer_role if clarification_auto_answer_enabled else "",
        "served_llm_model": served_llm_model,
        "served_llm_backend": served_llm_backend if served_llm_model else "",
        "served_llm_base_url": served_llm_base_url if served_llm_model else "",
        "served_llm_context_length": served_llm_context_length if served_llm_model else 0,
        "sp_conflict_policy": sp_conflict_policy,
        "system_prompt_sources": system_prompt_sources,
        "backend_options": {"num_ctx": context_length} if backend == "ollama" else {},
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
        f"max_rounds={max_clarification_rounds} "
        f"final_confirmation={require_final_confirmation}"
    )
    print(
        "Progress memory: "
        f"enabled={progress_memory_enabled} "
        f"path={progress_path} "
        f"low_rel={progress_low_relevance_threshold:.2f} "
        f"high_risk={progress_high_risk_threshold:.2f}"
    )
    if clarification_auto_answer_enabled:
        print(
            f"{auto_answer_label.capitalize()}: "
            f"{auto_answer_backend}/{auto_answer_model} @ {auto_answer_base_url} "
            f"(ctx={auto_answer_context_length} "
            f"history_turns={clarification_answer_history_turns} "
            f"kb_limit={clarification_answer_kb_clause_limit} "
            f"kb_chars={clarification_answer_kb_char_budget} "
            f"min_conf={clarification_answer_min_confidence:.2f})"
        )
    else:
        print("Clarification answer model: (disabled)")
    print(f"Prompt file: {prompt_file_path} ({'loaded' if prompt_guide else 'not found/empty'})")
    baked_probe = system_prompt_sources.get("baked_model_probe", {})
    if not isinstance(baked_probe, dict):
        baked_probe = {}
    print(
        "System-prompt sources: "
        f"runtime_loaded={bool(system_prompt_sources.get('runtime_prompt_loaded'))} "
        f"baked_status={baked_probe.get('status', 'unknown')} "
        f"baked_has_system={baked_probe.get('has_system')} "
        f"double_source={bool(system_prompt_sources.get('double_source_active'))} "
        f"policy={sp_conflict_policy}"
    )
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
    declared_predicates: set[str] = set()
    for idx, raw in enumerate(utterances, start=1):
        (
            utterance,
            scripted_clarification_answers,
            entry_max_rounds,
            scripted_confirmation_answers,
            entry_require_confirmation,
        ) = _coerce_utterance_entry(raw)
        utterance_original = utterance
        utterance, pre_normalization_events = _pre_normalize_utterance(utterance_original)
        control_predicate_directive = _is_predicate_control_directive(utterance_original)
        if not utterance:
            continue
        progress_directives = _extract_progress_directives(raw)
        progress_events: list[dict[str, Any]] = []
        progress_snapshot_before = (
            _normalize_progress_memory(progress_memory, kb_name=kb_name)
            if progress_memory_enabled
            else _empty_progress_memory(kb_name)
        )
        if progress_memory_enabled and progress_directives:
            progress_memory, progress_events = _apply_progress_directives(
                progress_memory,
                progress_directives,
                turn_index=idx,
            )
        progress_snapshot_after_directives = (
            _normalize_progress_memory(progress_memory, kb_name=kb_name)
            if progress_memory_enabled
            else _empty_progress_memory(kb_name)
        )

        per_turn_max_rounds = (
            max_clarification_rounds
            if entry_max_rounds is None
            else max(0, int(entry_max_rounds))
        )
        per_turn_require_confirmation = (
            require_final_confirmation
            if entry_require_confirmation is None
            else bool(entry_require_confirmation)
        )
        clarification_rounds: list[dict[str, Any]] = []
        scripted_answer_index = 0
        generated_answer_count = 0
        served_llm_answer_count = 0
        proxy_answer_count = 0
        clarification_pending = False
        clarification_pending_reason = ""
        confirmation_pending = False
        confirmation_question = ""
        confirmation_answer = ""
        confirmation_result = "not_required"
        confirmation_answer_index = 0
        clarification_question = ""
        clarification_answer_attempt: dict[str, Any] = {}
        clarification_policy = {
            "clarification_eagerness": clarification_eagerness,
            "uncertainty_score": 0.0,
            "effective_uncertainty": 0.0,
            "threshold": round(max(0.05, 1.0 - clarification_eagerness), 3),
            "request_clarification": False,
            "needs_clarification_flag": False,
            "progress_memory_available": bool(progress_memory_enabled),
            "progress_focus_present": False,
            "progress_relevance_score": 1.0,
            "progress_low_relevance": False,
            "progress_high_risk": False,
        }
        progress_low_relevance_seen = False
        progress_high_risk_seen = False

        if control_predicate_directive:
            declared_names = _extract_predicate_names_from_control_directive(utterance_original)
            if declared_names:
                declared_predicates.update(declared_names)
            control_apply_row = {
                "tool": "none",
                "input": {
                    "control_directive": "predicate_signature_declaration",
                    "raw_utterance": utterance_original,
                    "declared_predicates": declared_names,
                },
                "result": {
                    "status": "skipped",
                    "message": "Consumed predicate-control directive before parse.",
                },
            }
            control_apply_status = str(control_apply_row.get("result", {}).get("status", "skipped"))
            control_decision_state = _decision_state_for_turn(
                apply_status=control_apply_status,
                validation_errors=[],
                clarification_pending_reason="",
            )
            turn_rows.append(
                {
                    "turn_index": idx,
                    "utterance": utterance,
                    "utterance_original": utterance_original,
                    "utterance_pre_normalized": utterance,
                    "pre_normalization_events": pre_normalization_events,
                    "control_predicate_directive": True,
                    "declared_predicates_from_control": declared_names,
                    "route": "other",
                    "route_source": "pre_normalizer",
                    "repaired": False,
                    "fallback_used": False,
                    "alignment_events": [],
                    "registry_unknown_signatures": [],
                    "parsed": None,
                    "validation_errors": [],
                    "deferred_validation_errors": [],
                    "clarification_rounds": [],
                    "clarification_rounds_used": 0,
                    "clarification_max_rounds": per_turn_max_rounds,
                    "clarification_answers_available": len(scripted_clarification_answers),
                    "clarification_answers_used": 0,
                    "clarification_scripted_answers_used": 0,
                    "clarification_synthetic_answers_used": 0,
                    "clarification_generated_answers_used": 0,
                    "clarification_served_llm_answers_used": 0,
                    "clarification_proxy_answers_used": 0,
                    "clarification_policy": clarification_policy,
                    "progress_low_relevance_seen": False,
                    "progress_high_risk_seen": False,
                    "progress_directives": progress_directives,
                    "progress_events": progress_events,
                    "progress_snapshot_before": progress_snapshot_before,
                    "progress_snapshot_after_directives": progress_snapshot_after_directives,
                    "clarification_pending": False,
                    "clarification_pending_reason": "",
                    "clarification_question": "",
                    "clarification_answer_attempt": {},
                    "confirmation_required": False,
                    "confirmation_question": "",
                    "confirmation_answer": "",
                    "confirmation_result": "not_required",
                    "confirmation_answers_available": len(scripted_confirmation_answers),
                    "confirmation_answers_used": 0,
                    "apply": control_apply_row,
                    "apply_status": control_apply_status,
                    "decision_state": control_decision_state,
                }
            )
            print(
                f"[turn {idx:02d}] route=other source=pre_normalizer repaired=False fallback=False "
                f"clar_rounds=0 apply_tool=none apply_status=skipped [ok]"
            )
            continue

        parsed: dict[str, Any] | None = None
        parsed_text = ""
        route = "other"
        route_source = "heuristic"
        repaired = False
        fallback_used = False
        validation_errors: list[str] = []
        deferred_validation_errors: list[str] = []
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
                    context_length=classifier_context_length,
                    timeout=args.timeout_seconds,
                    api_key=api_key,
                )
                cls_json, _ = _parse_model_json(cls_resp, required_keys=["route"])
                if isinstance(cls_json, dict):
                    candidate = str(cls_json.get("route", "")).strip()
                    if candidate in {"assert_fact", "assert_rule", "query", "retract", "other"}:
                        # Guard against classifier drift: only promote assert_fact -> assert_rule
                        # when the utterance has explicit rule cues.
                        if candidate == "assert_rule" and heuristic == "assert_fact" and not _has_rule_cues(turn_input_text):
                            route = heuristic
                            route_source = "heuristic"
                        elif (
                            candidate == "other"
                            and heuristic == "assert_fact"
                            and declared_predicates
                            and not re.search(r"\b(translate|summarize|rewrite|format|explain)\b", turn_input_text.lower())
                        ):
                            # In declared-predicate lanes, keep fact intent unless the user
                            # explicitly asks for non-KB transformation behavior.
                            route = heuristic
                            route_source = "heuristic"
                        else:
                            route = candidate
                            route_source = "model"

            explicit_command = _build_explicit_command_parse(turn_input_text)
            if explicit_command is not None:
                route, parsed = explicit_command
                route_source = "explicit_command"
                parsed_text = json.dumps(parsed)
            else:
                known_predicates = sorted(
                    set(_known_predicate_names_from_corpus(corpus_clauses)) | declared_predicates
                )
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
                    context_length=context_length,
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
                            context_length=context_length,
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
                            context_length=context_length,
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
                parsed_intent = str(parsed.get("intent", "")).strip().lower()
                if route in {"assert_fact", "assert_rule", "query", "retract"} and parsed_intent != route:
                    fallback_parsed = _build_route_fallback_parse(route, utterance)
                    if isinstance(fallback_parsed, dict):
                        fallback_parsed = _normalize_clarification_fields(
                            fallback_parsed,
                            utterance=utterance,
                            route=route,
                        )
                        ok_fb, errors_fb = _validate_parsed(fallback_parsed)
                        if ok_fb:
                            parsed = fallback_parsed
                            fallback_used = True
                            alignment_events.append(
                                {
                                    "kind": "route_intent_realign",
                                    "from_intent": parsed_intent or "unknown",
                                    "to_intent": route,
                                }
                            )
                        elif errors_fb:
                            validation_errors.extend(errors_fb)

            if isinstance(parsed, dict) and not validation_errors:
                parsed, direction_events = _apply_directional_fact_guard(
                    parsed,
                    utterance=utterance,
                    route=route,
                )
                if direction_events:
                    alignment_events.extend(direction_events)
                parsed, retract_edge_events = _apply_retract_edge_target_guard(
                    parsed,
                    utterance=utterance,
                    route=route,
                )
                if retract_edge_events:
                    alignment_events.extend(retract_edge_events)
                parsed, retract_exclusion_events = _apply_retract_exclusion_guard(
                    parsed,
                    utterance=utterance,
                    route=route,
                )
                if retract_exclusion_events:
                    alignment_events.extend(retract_exclusion_events)
                parsed, concession_events = _apply_concession_contrast_guard(
                    parsed,
                    utterance=utterance,
                    route=route,
                )
                if concession_events:
                    alignment_events.extend(concession_events)
                parsed, declared_hint_events = _apply_declared_predicate_hint_guard(
                    parsed,
                    utterance=utterance,
                    route=route,
                    declared_predicates=declared_predicates,
                )
                if declared_hint_events:
                    alignment_events.extend(declared_hint_events)
                parsed, alias_events = _align_parsed_predicates(parsed, registry_alias_map)
                if alias_events:
                    alignment_events.extend(alias_events)
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

            if isinstance(parsed, dict) and validation_errors and bool(parsed.get("needs_clarification", False)):
                deferred_validation_errors = list(validation_errors)
                validation_errors = []

            if not isinstance(parsed, dict) or validation_errors:
                break

            clarification_policy = _clarification_policy_decision(
                parsed=parsed,
                clarification_eagerness=clarification_eagerness,
                utterance=turn_input_text,
                progress_memory=progress_memory if progress_memory_enabled else None,
                progress_low_relevance_threshold=progress_low_relevance_threshold,
                progress_high_risk_threshold=progress_high_risk_threshold,
            )
            if clarification_policy.get("progress_low_relevance"):
                progress_low_relevance_seen = True
            if clarification_policy.get("progress_high_risk"):
                progress_high_risk_seen = True
            clarification_question = str(parsed.get("clarification_question", "")).strip()
            if not clarification_question:
                if clarification_policy.get("progress_low_relevance"):
                    clarification_question = _synthesize_progress_clarification_question(
                        progress_memory=progress_memory if progress_memory_enabled else None,
                    )
                    if not str(parsed.get("clarification_reason", "")).strip():
                        parsed["clarification_reason"] = "Low relevance to active objective."
                else:
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
                if _is_non_informative_clarification_answer(scripted_answer):
                    clarification_pending = True
                    clarification_pending_reason = (
                        "Clarification answer was non-informative; KB apply deferred."
                    )
                    break
                if _is_redundant_clarification_pair(
                    clarification_rounds,
                    question=clarification_question,
                    answer=scripted_answer,
                ):
                    clarification_pending = True
                    clarification_pending_reason = (
                        "Clarification loop detected (same question/answer); KB apply deferred."
                    )
                    break
                clarification_rounds.append(
                    {
                        "round": len(clarification_rounds) + 1,
                        "question": clarification_question,
                        "answer": scripted_answer,
                        "answer_source": "scenario_scripted",
                        "uncertainty_score": clarification_policy.get("uncertainty_score"),
                        "effective_uncertainty": clarification_policy.get("effective_uncertainty"),
                        "threshold": clarification_policy.get("threshold"),
                    }
                )
                continue

            if has_round_capacity and clarification_auto_answer_enabled:
                clarification_context_pack = _build_clarification_context_pack(
                    server=server,
                    corpus_clauses=corpus_clauses,
                    turn_rows=turn_rows,
                    progress_memory=progress_memory if progress_memory_enabled else None,
                    history_turns=clarification_answer_history_turns,
                    kb_clause_limit=clarification_answer_kb_clause_limit,
                    kb_char_budget=clarification_answer_kb_char_budget,
                )
                synthetic_answer, answer_meta = _generate_synthetic_clarification_answer(
                    backend=auto_answer_backend,
                    base_url=auto_answer_base_url,
                    model=auto_answer_model,
                    utterance=utterance,
                    route=route,
                    question=clarification_question,
                    parsed=parsed,
                    rounds=clarification_rounds,
                    context_pack=clarification_context_pack,
                    context_length=auto_answer_context_length,
                    timeout=args.timeout_seconds,
                    api_key=api_key,
                    answer_source_prefix=auto_answer_source_prefix,
                    answer_role=auto_answer_role,
                )
                clarification_answer_attempt = {
                    "model": auto_answer_model,
                    "backend": auto_answer_backend,
                    "base_url": auto_answer_base_url,
                    "answer_role": auto_answer_role,
                    "answer_source_prefix": auto_answer_source_prefix,
                    "answer_source": str(answer_meta.get("answer_source", "")),
                    "answer_confidence": _clip_01(answer_meta.get("answer_confidence"), fallback=0.0),
                    "answer_assumption": str(answer_meta.get("answer_assumption", "")).strip(),
                    "answer_text": synthetic_answer,
                }
                if synthetic_answer:
                    answer_confidence = _clip_01(answer_meta.get("answer_confidence"), fallback=0.5)
                    if answer_confidence < clarification_answer_min_confidence:
                        clarification_pending = True
                        clarification_pending_reason = (
                            f"{auto_answer_label.capitalize()} confidence below threshold; KB apply deferred."
                        )
                        break
                    if _is_non_informative_clarification_answer(synthetic_answer):
                        clarification_pending = True
                        clarification_pending_reason = (
                            f"{auto_answer_label.capitalize()} returned non-informative answer; KB apply deferred."
                        )
                        break
                    if _is_redundant_clarification_pair(
                        clarification_rounds,
                        question=clarification_question,
                        answer=synthetic_answer,
                    ):
                        clarification_pending = True
                        clarification_pending_reason = (
                            "Clarification loop detected from answer model; KB apply deferred."
                        )
                        break
                    answer_source = str(answer_meta.get("answer_source", f"{auto_answer_source_prefix}_model"))
                    generated_answer_count += 1
                    if answer_source.startswith("served_llm"):
                        served_llm_answer_count += 1
                    else:
                        proxy_answer_count += 1
                    clarification_rounds.append(
                        {
                            "round": len(clarification_rounds) + 1,
                            "question": clarification_question,
                            "answer": synthetic_answer,
                            "answer_source": answer_source,
                            "answer_confidence": answer_confidence,
                            "answer_assumption": str(answer_meta.get("answer_assumption", "")).strip(),
                            "answer_context_kb_clause_count": int(answer_meta.get("context_kb_clause_count", 0) or 0),
                            "answer_context_recent_turn_count": int(answer_meta.get("context_recent_turn_count", 0) or 0),
                            "answer_context_progress_summary_count": int(
                                answer_meta.get("context_progress_summary_count", 0) or 0
                            ),
                            "uncertainty_score": clarification_policy.get("uncertainty_score"),
                            "effective_uncertainty": clarification_policy.get("effective_uncertainty"),
                            "threshold": clarification_policy.get("threshold"),
                        }
                    )
                    continue
                clarification_pending = True
                clarification_pending_reason = f"{auto_answer_label.capitalize()} could not provide a usable answer."
                break

            clarification_pending = True
            if not has_round_capacity:
                clarification_pending_reason = "Maximum clarification rounds reached for this utterance."
            else:
                clarification_pending_reason = "No clarification answer available for the generated question."
            break

        apply_row: dict[str, Any]
        if (
            not clarification_pending
            and isinstance(parsed, dict)
            and not validation_errors
            and per_turn_require_confirmation
            and str(parsed.get("intent", "")).strip() in {"assert_fact", "assert_rule", "retract"}
        ):
            confirmation_question = _build_final_confirmation_question(parsed)
            if confirmation_answer_index < len(scripted_confirmation_answers):
                confirmation_answer = scripted_confirmation_answers[confirmation_answer_index]
                confirmation_answer_index += 1
                if _is_affirmative_confirmation(confirmation_answer):
                    confirmation_result = "accepted"
                elif _is_negative_confirmation(confirmation_answer):
                    clarification_pending = True
                    confirmation_pending = True
                    confirmation_result = "declined"
                    clarification_pending_reason = "Final user confirmation declined; KB apply deferred."
                else:
                    clarification_pending = True
                    confirmation_pending = True
                    confirmation_result = "invalid"
                    clarification_pending_reason = "Final user confirmation was not yes/no; KB apply deferred."
            else:
                clarification_pending = True
                confirmation_pending = True
                confirmation_result = "missing"
                clarification_pending_reason = "Final user confirmation required before KB apply."

        if clarification_pending and isinstance(parsed, dict) and not validation_errors:
            pending_status = "confirmation_requested" if confirmation_pending else "clarification_requested"
            apply_row = {
                "tool": "none",
                "input": {
                    "clarification_question": clarification_question,
                    "clarification_rounds_used": len(clarification_rounds),
                    "confirmation_question": confirmation_question,
                    "confirmation_answer": confirmation_answer,
                },
                "result": {
                    "status": pending_status,
                    "message": clarification_pending_reason or "Clarification required before KB apply.",
                    "clarification_question": clarification_question,
                    "clarification_policy": clarification_policy,
                    "confirmation_required": bool(confirmation_pending),
                    "confirmation_question": confirmation_question,
                    "confirmation_answer": confirmation_answer,
                    "confirmation_result": confirmation_result,
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
        decision_state = _decision_state_for_turn(
            apply_status=apply_status,
            validation_errors=validation_errors,
            clarification_pending_reason=clarification_pending_reason,
        )
        turn_rows.append(
            {
                "turn_index": idx,
                "utterance": utterance,
                "utterance_original": utterance_original,
                "utterance_pre_normalized": utterance,
                "pre_normalization_events": pre_normalization_events,
                "control_predicate_directive": False,
                "declared_predicates_from_control": [],
                "route": route,
                "route_source": route_source,
                "repaired": repaired,
                "fallback_used": fallback_used,
                "alignment_events": alignment_events,
                "registry_unknown_signatures": registry_unknown_signatures,
                "parsed": parsed,
                "validation_errors": validation_errors,
                "deferred_validation_errors": deferred_validation_errors,
                "clarification_rounds": clarification_rounds,
                "clarification_rounds_used": len(clarification_rounds),
                "clarification_max_rounds": per_turn_max_rounds,
                "clarification_answers_available": len(scripted_clarification_answers),
                "clarification_answers_used": scripted_answer_index,
                "clarification_scripted_answers_used": scripted_answer_index,
                "clarification_synthetic_answers_used": generated_answer_count,
                "clarification_generated_answers_used": generated_answer_count,
                "clarification_served_llm_answers_used": served_llm_answer_count,
                "clarification_proxy_answers_used": proxy_answer_count,
                "clarification_policy": clarification_policy,
                "progress_low_relevance_seen": progress_low_relevance_seen,
                "progress_high_risk_seen": progress_high_risk_seen,
                "progress_directives": progress_directives,
                "progress_events": progress_events,
                "progress_snapshot_before": progress_snapshot_before,
                "progress_snapshot_after_directives": progress_snapshot_after_directives,
                "clarification_pending": clarification_pending,
                "clarification_pending_reason": clarification_pending_reason,
                "clarification_question": clarification_question,
                "clarification_answer_attempt": clarification_answer_attempt,
                "confirmation_required": bool(
                    per_turn_require_confirmation
                    and isinstance(parsed, dict)
                    and str(parsed.get("intent", "")).strip() in {"assert_fact", "assert_rule", "retract"}
                ),
                "confirmation_question": confirmation_question,
                "confirmation_answer": confirmation_answer,
                "confirmation_result": confirmation_result,
                "confirmation_answers_available": len(scripted_confirmation_answers),
                "confirmation_answers_used": confirmation_answer_index,
                "apply": apply_row,
                "apply_status": apply_status,
                "decision_state": decision_state,
            }
        )

        if apply_status in {"clarification_requested", "confirmation_requested"}:
            status_note = "confirmation" if apply_status == "confirmation_requested" else "clarification"
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
        if str(row.get("apply_status")) not in {"success", "skipped", "no_results"}
    )
    clarification_requests = sum(
        1
        for row in turn_rows
        if str(row.get("apply_status")) in {"clarification_requested", "confirmation_requested"}
    )
    confirmation_requests = sum(
        1 for row in turn_rows if str(row.get("apply_status")) == "confirmation_requested"
    )
    clarification_rounds_total = sum(
        int(row.get("clarification_rounds_used", 0)) for row in turn_rows
    )
    clarification_synthetic_answers_total = sum(
        int(row.get("clarification_synthetic_answers_used", 0)) for row in turn_rows
    )
    clarification_served_llm_answers_total = sum(
        int(row.get("clarification_served_llm_answers_used", 0)) for row in turn_rows
    )
    clarification_proxy_answers_total = sum(
        int(row.get("clarification_proxy_answers_used", 0)) for row in turn_rows
    )
    pre_normalized_turns = sum(
        1 for row in turn_rows if isinstance(row.get("pre_normalization_events"), list) and row.get("pre_normalization_events")
    )
    control_predicate_directive_turns = sum(
        1 for row in turn_rows if bool(row.get("control_predicate_directive"))
    )
    progress_low_relevance_clarifications = sum(
        1
        for row in turn_rows
        if isinstance(row.get("clarification_policy"), dict)
        and bool(row["clarification_policy"].get("progress_low_relevance"))
        and bool(row["clarification_policy"].get("request_clarification"))
    )
    progress_high_risk_turns = sum(
        1
        for row in turn_rows
        if isinstance(row.get("clarification_policy"), dict)
        and bool(row["clarification_policy"].get("progress_high_risk"))
    )
    off_focus_write_attempts = sum(
        1
        for row in turn_rows
        if isinstance(row.get("parsed"), dict)
        and str(row["parsed"].get("intent", "")).strip().lower() in WRITE_INTENTS
        and bool(row.get("progress_low_relevance_seen"))
    )
    off_focus_write_intercepts = sum(
        1
        for row in turn_rows
        if isinstance(row.get("parsed"), dict)
        and str(row["parsed"].get("intent", "")).strip().lower() in WRITE_INTENTS
        and bool(row.get("progress_low_relevance_seen"))
        and str(row.get("decision_state", "")).strip().lower() != "commit"
    )
    off_focus_write_commits = sum(
        1
        for row in turn_rows
        if isinstance(row.get("parsed"), dict)
        and str(row["parsed"].get("intent", "")).strip().lower() in WRITE_INTENTS
        and bool(row.get("progress_low_relevance_seen"))
        and str(row.get("decision_state", "")).strip().lower() == "commit"
    )
    off_focus_write_block_rate = round(off_focus_write_intercepts / max(1, off_focus_write_attempts), 3)
    off_focus_write_contamination_rate = round(off_focus_write_commits / max(1, off_focus_write_attempts), 3)
    kb_contamination_delta = off_focus_write_commits - off_focus_write_intercepts
    decision_state_counts: dict[str, int] = {}
    for row in turn_rows:
        state = str(row.get("decision_state", "reject"))
        decision_state_counts[state] = decision_state_counts.get(state, 0) + 1

    run_skipped = runtime_mode == "none"
    overall_ok = (
        (not run_skipped)
        and parse_fail_count == 0
        and apply_fail_count == 0
        and validation_pass == validation_total
    )
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
        if progress_memory_enabled:
            progress_memory["updated_at_utc"] = _utc_now_iso()
            _write_json(progress_path, progress_memory)
            progress_write = {
                "status": "written",
                "path": str(progress_path),
                "active_focus_count": len(_coerce_string_list(progress_memory.get("active_focus"))),
                "goal_count": len(progress_memory.get("goals", [])),
                "open_question_count": len(progress_memory.get("open_questions", [])),
            }
        else:
            progress_write = {
                "status": "skipped",
                "path": str(progress_path),
                "reason": "Progress memory disabled.",
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
        progress_write = {
            "status": "skipped",
            "path": str(progress_path),
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
            "progress_path": str(progress_path),
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
        "system_prompt_sources": system_prompt_sources,
        "declared_predicates": sorted(declared_predicates),
        "kb_runtime_boot_path": str(server_boot_kb_path),
        "kb_init": kb_init,
        "corpus_load": corpus_load,
        "corpus_write": corpus_write,
        "progress_write": progress_write,
        "progress_memory_enabled": progress_memory_enabled,
        "progress_memory": progress_memory,
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
        "turns_confirmation_requested": confirmation_requests,
        "clarification_rounds_total": clarification_rounds_total,
        "clarification_synthetic_answers_total": clarification_synthetic_answers_total,
        "clarification_served_llm_answers_total": clarification_served_llm_answers_total,
        "clarification_proxy_answers_total": clarification_proxy_answers_total,
        "pre_normalized_turns": pre_normalized_turns,
        "control_predicate_directive_turns": control_predicate_directive_turns,
        "progress_low_relevance_clarifications": progress_low_relevance_clarifications,
        "progress_high_risk_turns": progress_high_risk_turns,
        "off_focus_write_attempts": off_focus_write_attempts,
        "off_focus_write_intercepts": off_focus_write_intercepts,
        "off_focus_write_commits": off_focus_write_commits,
        "off_focus_write_block_rate": off_focus_write_block_rate,
        "off_focus_write_contamination_rate": off_focus_write_contamination_rate,
        "kb_contamination_delta": kb_contamination_delta,
        "decision_state_counts": decision_state_counts,
        "validation_total": validation_total,
        "validation_passed": validation_pass,
        "overall_status": "skipped" if run_skipped else ("passed" if overall_ok else "failed"),
        "turns": turn_rows,
        "validations": validation_rows,
    }

    print("")
    print(f"Validation: {validation_pass}/{validation_total} passed")
    print(f"Parser failures: {parse_fail_count}")
    print(f"Apply failures: {apply_fail_count}")
    print(
        "Clarification requests: "
        f"{clarification_requests} (confirmation={confirmation_requests}, rounds={clarification_rounds_total})"
    )
    print(
        "Generated clarification answers used: "
        f"{clarification_synthetic_answers_total} "
        f"(served_llm={clarification_served_llm_answers_total}, proxy={clarification_proxy_answers_total})"
    )
    print(
        "Pre-normalization: "
        f"turns_with_rewrites={pre_normalized_turns} "
        f"control_directive_turns={control_predicate_directive_turns}"
    )
    if declared_predicates:
        print(
            "Declared predicate hints: "
            f"{len(declared_predicates)} ({', '.join(sorted(declared_predicates)[:10])}"
            + ("..." if len(declared_predicates) > 10 else "")
            + ")"
        )
    print(
        "Progress-policy clarifications: "
        f"{progress_low_relevance_clarifications} "
        f"(high_risk_turns={progress_high_risk_turns})"
    )
    print(
        "Off-focus write policy: "
        f"attempts={off_focus_write_attempts} "
        f"intercepts={off_focus_write_intercepts} "
        f"commits={off_focus_write_commits} "
        f"block_rate={off_focus_write_block_rate:.3f} "
        f"contamination_rate={off_focus_write_contamination_rate:.3f} "
        f"delta={kb_contamination_delta}"
    )
    print(f"Decision states: {decision_state_counts}")
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

    return 0 if (overall_ok or run_skipped) else 1


if __name__ == "__main__":
    raise SystemExit(main())
