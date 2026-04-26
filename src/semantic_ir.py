from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


SCHEMA_CONTRACT: dict[str, Any] = {
    "schema_version": "semantic_ir_v1",
    "decision": "commit|clarify|quarantine|reject|answer|mixed",
    "turn_type": "state_update|query|correction|rule_update|mixed|unknown",
    "entities": [
        {
            "id": "e1",
            "surface": "",
            "normalized": "",
            "type": "person|object|medication|lab_test|condition|symptom|place|time|unknown",
            "confidence": 0.0,
        }
    ],
    "referents": [
        {
            "surface": "it|her|his|that",
            "status": "resolved|ambiguous|unresolved",
            "candidates": ["e1"],
            "chosen": None,
        }
    ],
    "assertions": [
        {
            "kind": "direct|question|claim|correction|rule",
            "subject": "e1",
            "relation_concept": "",
            "object": "e2",
            "polarity": "positive|negative",
            "certainty": 0.0,
        }
    ],
    "unsafe_implications": [
        {
            "candidate": "",
            "why_unsafe": "",
            "commit_policy": "clarify|quarantine|reject",
        }
    ],
    "candidate_operations": [
        {
            "operation": "assert|retract|rule|query|none",
            "predicate": "",
            "args": [],
            "polarity": "positive|negative",
            "source": "direct|inferred|context",
            "safety": "safe|unsafe|needs_clarification",
        }
    ],
    "clarification_questions": [""],
    "self_check": {
        "bad_commit_risk": "low|medium|high",
        "missing_slots": [],
        "notes": [],
    },
}


BEST_GUARDED_V2_SYSTEM = (
    "You are a semantic IR compiler for a governed symbolic memory system. "
    "The root object must be semantic_ir_v1 itself, with schema_version and decision as top-level keys. "
    "Do not wrap the answer under schema_contract, result, output, or semantic_ir. "
    "You do not answer the user and you do not commit durable truth. "
    "Use direct language understanding aggressively, but mark unsafe commitments explicitly."
)


BEST_GUARDED_V2_GUIDANCE = (
    "Decision policy:\n"
    "- reject: user asks for treatment, dose, medication stop/hold/start, or clinical recommendation. You may still include clarification questions, but the decision remains reject.\n"
    "- quarantine: direct facts conflict with a claim, a claim would overwrite observed state, or a candidate fact is plausible but unsafe.\n"
    "- clarify: missing referent, measurement direction, patient identity, object of 'it/that', or allergy-vs-intolerance distinction blocks a write.\n"
    "- mixed: same turn contains both safe writes and a query/rule/unsafe implication.\n"
    "- commit: direct state update or correction has a clear target and safe predicate mapping.\n"
    "Special guards:\n"
    "- Do not turn a claim into a fact. 'Bob says he has it' is a claim, not possession.\n"
    "- Do not infer diagnosis or staging from a single lab value request. Quarantine or clarify.\n"
    "- Do not infer allergy from nausea/vomiting alone. Clarify allergy vs side effect/intolerance.\n"
    "- A clear correction like 'not Mara, Fred has it' may propose retract/assert.\n"
    "- If context supplies exactly one active patient and one active lab test, a direct 'it came back high' may propose a safe lab_result_high write.\n"
    "- For rule-plus-fact or fact-plus-query turns, use mixed and keep unsafe query targets out of committed facts.\n"
    "- Preserve negation in candidate_operations with polarity='negative'. Do not turn 'never saw X' into a positive saw/2 fact."
)


@dataclass(frozen=True)
class SemanticIRCallConfig:
    backend: str = "ollama"
    base_url: str = "http://127.0.0.1:11434"
    model: str = "qwen3.6:35b"
    context_length: int = 16384
    timeout: int = 120
    temperature: float = 0.0
    top_p: float = 0.82
    top_k: int = 20
    think_enabled: bool = False


def build_semantic_ir_messages(
    *,
    utterance: str,
    context: list[str] | None = None,
    allowed_predicates: list[str] | None = None,
    domain: str = "runtime",
) -> list[dict[str, str]]:
    payload = {
        "required_top_level_json_shape": SCHEMA_CONTRACT,
        "task": "Analyze the utterance and emit semantic_ir_v1 JSON only.",
        "output_instruction": (
            "Return exactly one JSON object using required_top_level_json_shape as the root shape. "
            "Do not copy the key name required_top_level_json_shape into your response."
        ),
        "domain": domain,
        "utterance": utterance,
        "context": context or [],
        "allowed_predicates": allowed_predicates or [],
        "authority_boundary": "The runtime validates and commits; you only propose semantic structure.",
        "variant_guidance": BEST_GUARDED_V2_GUIDANCE,
    }
    return [
        {"role": "system", "content": BEST_GUARDED_V2_SYSTEM},
        {"role": "user", "content": "INPUT_JSON:\n" + json.dumps(payload, ensure_ascii=False, indent=2)},
    ]


def call_semantic_ir(
    *,
    utterance: str,
    config: SemanticIRCallConfig,
    context: list[str] | None = None,
    allowed_predicates: list[str] | None = None,
    domain: str = "runtime",
) -> dict[str, Any]:
    if str(config.backend or "ollama").strip().lower() != "ollama":
        raise RuntimeError("semantic_ir_v1 currently supports ollama backend only")
    messages = build_semantic_ir_messages(
        utterance=utterance,
        context=context,
        allowed_predicates=allowed_predicates,
        domain=domain,
    )
    payload = {
        "model": config.model,
        "stream": False,
        "format": "json",
        "think": bool(config.think_enabled),
        "messages": messages,
        "options": {
            "temperature": float(config.temperature),
            "top_p": float(config.top_p),
            "top_k": int(config.top_k),
            "num_ctx": int(config.context_length),
        },
    }
    req = urllib.request.Request(
        f"{config.base_url.rstrip('/')}/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=int(config.timeout)) as response:
            raw = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(str(exc)) from exc

    message = raw.get("message", {}) if isinstance(raw, dict) else {}
    content = str(message.get("content", "") if isinstance(message, dict) else "").strip()
    parsed = parse_semantic_ir_json(content)
    return {
        "latency_ms": int((time.perf_counter() - started) * 1000),
        "raw": raw,
        "content": content,
        "parsed": parsed,
    }


def parse_semantic_ir_json(text: str) -> dict[str, Any] | None:
    raw = str(text or "").strip()
    if not raw:
        return None
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(parsed, dict):
        return None
    if "semantic_ir" in parsed and isinstance(parsed.get("semantic_ir"), dict):
        parsed = parsed["semantic_ir"]
    if str(parsed.get("schema_version", "")).strip() != "semantic_ir_v1":
        return None
    if not str(parsed.get("decision", "")).strip():
        return None
    return parsed


def semantic_ir_to_prethink_payload(ir: dict[str, Any]) -> dict[str, Any]:
    decision = _normalize_decision(ir.get("decision"))
    intent = _intent_from_ir(ir)
    questions = _string_list(ir.get("clarification_questions"))
    risk = _bad_commit_risk(ir)
    needs_clarification = decision == "clarify" or bool(_missing_slots(ir))
    if decision in {"reject", "quarantine"}:
        intent = "other"
        needs_clarification = False
    uncertainty = {
        "low": 0.12,
        "medium": 0.48,
        "high": 0.86,
    }.get(risk, 0.48)
    if needs_clarification:
        uncertainty = max(uncertainty, 0.82)
    return {
        "intent": intent,
        "logic_string": "",
        "components": {"atoms": [], "variables": [], "predicates": []},
        "facts": [],
        "rules": [],
        "queries": [],
        "confidence": _confidence_object(round(1.0 - min(max(uncertainty, 0.0), 1.0), 2)),
        "ambiguities": _semantic_ir_ambiguities(ir),
        "needs_clarification": needs_clarification,
        "uncertainty_score": round(uncertainty, 2),
        "uncertainty_label": "high" if uncertainty >= 0.67 else ("medium" if uncertainty >= 0.34 else "low"),
        "clarification_question": questions[0] if needs_clarification and questions else "",
        "clarification_reason": _semantic_ir_reason(ir, decision),
        "rationale": f"semantic_ir_v1 decision={decision}; risk={risk}",
    }


def semantic_ir_to_legacy_parse(ir: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    decision = _normalize_decision(ir.get("decision"))
    warnings: list[str] = []
    facts: list[str] = []
    rules: list[str] = []
    queries: list[str] = []
    retracts: list[str] = []
    entity_names = _entity_name_map(ir)

    for op in _candidate_operations(ir):
        operation = str(op.get("operation", "")).strip().lower()
        safety = str(op.get("safety", "")).strip().lower()
        source = str(op.get("source", "")).strip().lower()
        polarity = str(op.get("polarity", "positive") or "positive").strip().lower()
        if safety != "safe":
            continue
        if source == "inferred":
            warnings.append("skipped inferred safe operation pending policy")
            continue
        if polarity == "negative" and operation == "assert":
            warnings.append("skipped negative assertion pending explicit negation policy")
            continue
        predicate = _predicate_name(op.get("predicate"))
        if not predicate:
            continue
        args = _operation_args(op.get("args"), entity_names=entity_names, for_query=operation == "query")
        if operation == "assert":
            facts.append(_clause(predicate, args))
        elif operation == "query":
            queries.append(_clause(predicate, args))
        elif operation == "retract":
            retracts.append(_clause(predicate, args))
        elif operation == "rule":
            clause = str(op.get("clause") or op.get("logic") or "").strip()
            if clause:
                rules.append(_ensure_period(clause))
            else:
                warnings.append("skipped rule operation without explicit clause")

    if decision in {"reject", "quarantine", "clarify"}:
        facts = []
        rules = []
        queries = [] if decision != "clarify" else queries
        retracts = []

    intent = _legacy_intent(facts=facts, rules=rules, queries=queries, retracts=retracts, decision=decision)
    logic_parts = retracts + facts + rules + queries
    payload = {
        "intent": intent,
        "logic_string": " ".join(logic_parts),
        "components": _components_from_clauses(logic_parts),
        "facts": facts,
        "rules": rules,
        "queries": queries,
        "confidence": _confidence_object(0.9 if decision in {"commit", "answer", "mixed"} else 0.25),
        "ambiguities": _semantic_ir_ambiguities(ir),
        "needs_clarification": decision == "clarify",
        "uncertainty_score": 0.85 if decision == "clarify" else (0.65 if decision in {"quarantine", "reject"} else 0.2),
        "uncertainty_label": "high" if decision == "clarify" else ("medium" if decision in {"quarantine", "reject"} else "low"),
        "clarification_question": _first_question(ir) if decision == "clarify" else "",
        "clarification_reason": _semantic_ir_reason(ir, decision) if decision == "clarify" else "",
        "rationale": f"Mapped from semantic_ir_v1 decision={decision}; skipped={len(warnings)}",
    }
    if retracts:
        payload["correction_retract_clauses"] = retracts
    return payload, warnings


def _candidate_operations(ir: dict[str, Any]) -> list[dict[str, Any]]:
    raw = ir.get("candidate_operations", [])
    if not isinstance(raw, list):
        return []
    return [item for item in raw if isinstance(item, dict)]


def _normalize_decision(value: Any) -> str:
    decision = str(value or "").strip().lower()
    if decision not in {"commit", "clarify", "quarantine", "reject", "answer", "mixed"}:
        return "quarantine"
    return decision


def _intent_from_ir(ir: dict[str, Any]) -> str:
    safe_ops: list[str] = []
    for op in _candidate_operations(ir):
        if str(op.get("safety", "")).strip().lower() != "safe":
            continue
        operation = str(op.get("operation", "")).strip().lower()
        source = str(op.get("source", "")).strip().lower()
        polarity = str(op.get("polarity", "positive") or "positive").strip().lower()
        if source == "inferred":
            continue
        if polarity == "negative" and operation == "assert":
            continue
        safe_ops.append(operation)
    if "assert" in safe_ops:
        return "assert_fact"
    if "rule" in safe_ops:
        return "assert_rule"
    if "retract" in safe_ops:
        return "retract"
    if "query" in safe_ops or _normalize_decision(ir.get("decision")) == "answer":
        return "query"
    return "other"


def _legacy_intent(
    *,
    facts: list[str],
    rules: list[str],
    queries: list[str],
    retracts: list[str],
    decision: str,
) -> str:
    if facts:
        return "assert_fact"
    if rules:
        return "assert_rule"
    if retracts:
        return "retract"
    if queries:
        return "query"
    if decision == "answer":
        return "query"
    return "other"


def _entity_name_map(ir: dict[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    raw = ir.get("entities", [])
    if not isinstance(raw, list):
        return out
    for item in raw:
        if not isinstance(item, dict):
            continue
        entity_id = str(item.get("id", "")).strip()
        if not entity_id:
            continue
        name = str(item.get("normalized") or item.get("surface") or "").strip()
        if name:
            out[entity_id] = name
    return out


def _operation_args(raw_args: Any, *, entity_names: dict[str, str], for_query: bool) -> list[str]:
    if not isinstance(raw_args, list):
        return []
    return [_term_from_arg(item, entity_names=entity_names, for_query=for_query) for item in raw_args]


def _term_from_arg(value: Any, *, entity_names: dict[str, str], for_query: bool) -> str:
    if isinstance(value, dict):
        for key in ("id", "entity", "value", "normalized", "surface"):
            if key in value:
                return _term_from_arg(value.get(key), entity_names=entity_names, for_query=for_query)
        return "unknown"
    raw = str(value or "").strip()
    if raw in entity_names:
        raw = entity_names[raw]
    if for_query and raw in {"?", "X", "Y", "Z", "Who", "What", "Where", "When"}:
        return raw if raw in {"X", "Y", "Z"} else "X"
    if for_query and raw.startswith("?"):
        return _variable_name(raw[1:] or "X")
    if re.fullmatch(r"-?\d+(\.\d+)?", raw):
        return raw
    if raw.startswith("'") and raw.endswith("'"):
        raw = raw[1:-1]
    return _atomize(raw)


def _variable_name(raw: str) -> str:
    name = re.sub(r"[^A-Za-z0-9_]+", "_", str(raw or "X")).strip("_") or "X"
    if not name[0].isalpha() or not name[0].isupper():
        name = "X" + name[:1].upper() + name[1:]
    return name


def _predicate_name(value: Any) -> str:
    raw = str(value or "").strip()
    if "/" in raw:
        raw = raw.split("/", 1)[0]
    raw = _atomize(raw)
    if not re.fullmatch(r"[a-z_][a-z0-9_]*", raw):
        return ""
    return raw


def _atomize(raw: str) -> str:
    value = str(raw or "").strip().lower()
    value = value.replace("%", " percent ")
    value = re.sub(r"[^a-z0-9_]+", "_", value).strip("_")
    return value or "unknown"


def _clause(predicate: str, args: list[str]) -> str:
    return _ensure_period(f"{predicate}({', '.join(args)})")


def _ensure_period(clause: str) -> str:
    text = str(clause or "").strip()
    return text if text.endswith(".") else f"{text}."


def _components_from_clauses(clauses: list[str]) -> dict[str, list[str]]:
    atoms: set[str] = set()
    variables: set[str] = set()
    predicates: set[str] = set()
    for clause in clauses:
        match = re.match(r"\s*([a-z_][a-z0-9_]*)\s*\(", clause)
        if match:
            predicates.add(match.group(1))
        for token in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", clause):
            if token[:1].isupper() or token.startswith("_"):
                variables.add(token)
            else:
                atoms.add(token)
    return {"atoms": sorted(atoms), "variables": sorted(variables), "predicates": sorted(predicates)}


def _confidence_object(value: float) -> dict[str, float]:
    clipped = max(0.0, min(1.0, float(value)))
    return {"overall": clipped, "intent": clipped, "logic": clipped}


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _bad_commit_risk(ir: dict[str, Any]) -> str:
    self_check = ir.get("self_check", {})
    risk = ""
    if isinstance(self_check, dict):
        risk = str(self_check.get("bad_commit_risk", "")).strip().lower()
    return risk if risk in {"low", "medium", "high"} else "medium"


def _missing_slots(ir: dict[str, Any]) -> list[str]:
    self_check = ir.get("self_check", {})
    if not isinstance(self_check, dict):
        return []
    return _string_list(self_check.get("missing_slots", []))


def _semantic_ir_ambiguities(ir: dict[str, Any]) -> list[str]:
    out: list[str] = []
    for item in _missing_slots(ir):
        out.append(f"missing slot: {item}")
    for ref in ir.get("referents", []) if isinstance(ir.get("referents"), list) else []:
        if not isinstance(ref, dict):
            continue
        status = str(ref.get("status", "")).strip().lower()
        if status in {"ambiguous", "unresolved"}:
            surface = str(ref.get("surface", "referent")).strip() or "referent"
            out.append(f"{surface} referent {status}")
    return out


def _semantic_ir_reason(ir: dict[str, Any], decision: str) -> str:
    missing = _missing_slots(ir)
    if missing:
        return f"Missing {missing[0]}"[:80]
    if decision == "reject":
        return "Rejected by semantic IR policy"
    if decision == "quarantine":
        return "Unsafe implication or claim"
    if decision == "clarify":
        return "Clarification needed"
    return "semantic_ir_v1"


def _first_question(ir: dict[str, Any]) -> str:
    questions = _string_list(ir.get("clarification_questions"))
    return questions[0] if questions else "Please clarify the missing semantic slot?"
