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


SEMANTIC_IR_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "schema_version",
        "decision",
        "turn_type",
        "entities",
        "referents",
        "assertions",
        "unsafe_implications",
        "candidate_operations",
        "clarification_questions",
        "self_check",
    ],
    "properties": {
        "schema_version": {"type": "string", "const": "semantic_ir_v1"},
        "decision": {
            "type": "string",
            "enum": ["commit", "clarify", "quarantine", "reject", "answer", "mixed"],
        },
        "turn_type": {
            "type": "string",
            "enum": ["state_update", "query", "correction", "rule_update", "mixed", "unknown"],
        },
        "entities": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["id", "surface", "normalized", "type", "confidence"],
                "properties": {
                    "id": {"type": "string"},
                    "surface": {"type": "string"},
                    "normalized": {"type": "string"},
                    "type": {
                        "type": "string",
                        "enum": [
                            "person",
                            "object",
                            "medication",
                            "lab_test",
                            "condition",
                            "symptom",
                            "place",
                            "time",
                            "unknown",
                        ],
                    },
                    "confidence": {"type": "number"},
                },
            },
        },
        "referents": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["surface", "status", "candidates", "chosen"],
                "properties": {
                    "surface": {"type": "string"},
                    "status": {"type": "string", "enum": ["resolved", "ambiguous", "unresolved"]},
                    "candidates": {"type": "array", "items": {"type": "string"}},
                    "chosen": {"anyOf": [{"type": "string"}, {"type": "null"}]},
                },
            },
        },
        "assertions": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["kind", "subject", "relation_concept", "object", "polarity", "certainty"],
                "properties": {
                    "kind": {"type": "string", "enum": ["direct", "question", "claim", "correction", "rule"]},
                    "subject": {"type": "string"},
                    "relation_concept": {"type": "string"},
                    "object": {"type": "string"},
                    "polarity": {"type": "string", "enum": ["positive", "negative"]},
                    "certainty": {"type": "number"},
                },
            },
        },
        "unsafe_implications": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["candidate", "why_unsafe", "commit_policy"],
                "properties": {
                    "candidate": {"type": "string"},
                    "why_unsafe": {"type": "string"},
                    "commit_policy": {"type": "string", "enum": ["clarify", "quarantine", "reject"]},
                },
            },
        },
        "candidate_operations": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["operation", "predicate", "args", "polarity", "source", "safety"],
                "properties": {
                    "operation": {"type": "string", "enum": ["assert", "retract", "rule", "query", "none"]},
                    "predicate": {"type": "string"},
                    "args": {"type": "array", "items": {"type": "string"}},
                    "polarity": {"type": "string", "enum": ["positive", "negative"]},
                    "source": {"type": "string", "enum": ["direct", "inferred", "context"]},
                    "safety": {"type": "string", "enum": ["safe", "unsafe", "needs_clarification"]},
                },
            },
        },
        "clarification_questions": {"type": "array", "items": {"type": "string"}},
        "self_check": {
            "type": "object",
            "additionalProperties": False,
            "required": ["bad_commit_risk", "missing_slots", "notes"],
            "properties": {
                "bad_commit_risk": {"type": "string", "enum": ["low", "medium", "high"]},
                "missing_slots": {"type": "array", "items": {"type": "string"}},
                "notes": {"type": "array", "items": {"type": "string"}},
            },
        },
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
    "- mixed: same turn contains both safe writes and a query/rule/unsafe implication. If unsafe_implications is non-empty and safe operations are also present, decision MUST be mixed, not commit.\n"
    "- commit: direct state update or correction has a clear target and safe predicate mapping.\n"
    "Special guards:\n"
    "- Context entries are already-known state/rules, not new user assertions. Do not create candidate_operations that merely restate context.\n"
    "- Use context to resolve referents and answer queries; only the current utterance may introduce a new write candidate.\n"
    "- If the current utterance contains policy/rule language such as all/every/unless/must/before and also direct facts, choose mixed. Commit the direct facts and represent rule/policy material in assertions or unsafe_implications if no safe rule clause is available.\n"
    "- Do not turn a claim into a fact. 'Bob says he has it' is a claim, not possession.\n"
    "- Do not infer diagnosis or staging from a single lab value request. Quarantine or clarify.\n"
    "- Do not infer allergy from nausea/vomiting alone. Clarify allergy vs side effect/intolerance when the user only reports symptoms.\n"
    "- If the user explicitly says 'not allergic' and gives a side-effect/intolerance explanation such as nausea, the correction is clear: propose retracting the allergy and recording the side effect; do not ask for allergy-vs-intolerance clarification.\n"
    "- A clear correction like 'not Mara, Fred has it' may propose retract/assert.\n"
    "- Retraction is a governance operation, not a predicate. You may propose operation='retract' even when 'retract/1' is not in allowed_predicates.\n"
    "- A correction like 'it should be quarantined instead' with context containing the old fact is enough to retract the old fact and assert the replacement fact; do not ask for authority/provenance unless the predicate itself requires it.\n"
    "- Do not invent required governance slots that are not in the predicate schema. Source document, authority, or reason fields are optional provenance unless the allowed predicate explicitly requires them.\n"
    "- A direct correction like 'remove X allergy; stomach upset only' is explicit enough to retract the allergy and record side effect/intolerance when the old allergy fact is in context.\n"
    "- Medical comparative labs can still be direct facts: 'lower than last week but still above the upper bound' means lab_result_high remains safe; do not require the numeric value unless the predicate requires a value slot.\n"
    "- 'Do not call it normal' is explicit negative classification; do not treat it as an ambiguous referent when the preceding lab test is clear.\n"
    "- Do not assert a fact about a quantified group atom such as submitted_form(residents) for 'all residents except Kai'. Use individual known members only when context enumerates them; otherwise mark the class-level write unsafe.\n"
    "- Pure hypothetical questions with 'if ... would ...?' are queries, not writes and not clarification requests when the hypothetical nature is clear. Mark the query operation safe; do not ask whether the user wants a hypothetical answer. Do not assert the hypothetical premise or any derived consequence as a fact.\n"
    "- Denial predicates are speech/event facts. 'Omar denied signing the waiver' may assert denied(...); it must not assert signed(...) false.\n"
    "- Legal findings are scoped speech/finding facts. 'The court did not find that Pavel paid' must not become negative paid(Pavel, ...). It is an absence of finding; use mixed/quarantine or a finding predicate if available.\n"
    "- 'Only after X did Y become effective; X happened Wednesday' is enough to commit Y's effective date as Wednesday when an effective_on predicate is allowed. Do not mark the effective date unsafe merely because it follows from the stated condition.\n"
    "- Do not include draft thoughts, reversals, or self-debate in unsafe_implications. If the final candidate_operations mark an operation safe, do not also list the same operation as unsafe.\n"
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
    reasoning_effort: str = "none"
    max_tokens: int = 4096


def build_semantic_ir_messages(
    *,
    utterance: str,
    context: list[str] | None = None,
    allowed_predicates: list[str] | None = None,
    domain: str = "runtime",
    include_schema_contract: bool = True,
) -> list[dict[str, str]]:
    payload = {
        "task": "Analyze the utterance and emit semantic_ir_v1 JSON only.",
        "output_instruction": "Return exactly one semantic_ir_v1 JSON object.",
        "domain": domain,
        "utterance": utterance,
        "context": context or [],
        "allowed_predicates": allowed_predicates or [],
        "authority_boundary": "The runtime validates and commits; you only propose semantic structure.",
        "variant_guidance": BEST_GUARDED_V2_GUIDANCE,
    }
    if include_schema_contract:
        payload["required_top_level_json_shape"] = SCHEMA_CONTRACT
        payload["output_instruction"] = (
            "Return exactly one JSON object using required_top_level_json_shape as the root shape. "
            "Do not copy the key name required_top_level_json_shape into your response."
        )
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
    backend = str(config.backend or "ollama").strip().lower()
    messages = build_semantic_ir_messages(
        utterance=utterance,
        context=context,
        allowed_predicates=allowed_predicates,
        domain=domain,
        include_schema_contract=backend != "lmstudio",
    )
    if backend == "lmstudio":
        return _call_lmstudio_semantic_ir(config=config, messages=messages)
    if backend != "ollama":
        raise RuntimeError(f"semantic_ir_v1 backend not supported: {backend}")
    return _call_ollama_semantic_ir(config=config, messages=messages)


def _call_ollama_semantic_ir(*, config: SemanticIRCallConfig, messages: list[dict[str, str]]) -> dict[str, Any]:
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


def _call_lmstudio_semantic_ir(*, config: SemanticIRCallConfig, messages: list[dict[str, str]]) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": config.model,
        "messages": messages,
        "temperature": float(config.temperature),
        "top_p": float(config.top_p),
        "max_tokens": int(config.max_tokens),
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "semantic_ir_v1",
                "strict": True,
                "schema": SEMANTIC_IR_JSON_SCHEMA,
            },
        },
    }
    if str(config.reasoning_effort or "").strip():
        payload["reasoning_effort"] = str(config.reasoning_effort).strip()
    base_url = config.base_url.rstrip("/")
    endpoint = f"{base_url}/chat/completions" if base_url.endswith("/v1") else f"{base_url}/v1/chat/completions"
    req = urllib.request.Request(
        endpoint,
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

    choices = raw.get("choices", []) if isinstance(raw, dict) else []
    first = choices[0] if choices and isinstance(choices[0], dict) else {}
    message = first.get("message", {}) if isinstance(first, dict) else {}
    content = str(message.get("content", "") if isinstance(message, dict) else "").strip()
    if not content and isinstance(message, dict):
        content = str(message.get("reasoning_content", "") or "").strip()
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
    decision = _projected_decision(ir)
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
    if not needs_clarification and decision in {"commit", "mixed", "answer"} and _has_safe_direct_write(ir):
        uncertainty = min(uncertainty, 0.2)
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
    decision = _projected_decision(ir)
    warnings: list[str] = []
    facts: list[str] = []
    rules: list[str] = []
    queries: list[str] = []
    retracts: list[str] = []
    entity_names = _entity_name_map(ir)
    entity_meta = _entity_metadata_map(ir)

    for op in _candidate_operations(ir):
        operation = str(op.get("operation", "")).strip().lower()
        safety = str(op.get("safety", "")).strip().lower()
        source = str(op.get("source", "")).strip().lower()
        polarity = str(op.get("polarity", "positive") or "positive").strip().lower()
        if safety != "safe":
            continue
        if source == "inferred" and not (operation == "query" and _is_pure_hypothetical_query(ir)):
            warnings.append("skipped inferred safe operation pending policy")
            continue
        if source == "context" and operation in {"assert", "rule"}:
            warnings.append("skipped context-sourced write operation")
            continue
        predicate = _predicate_name(op.get("predicate"))
        if not predicate:
            continue
        if operation == "assert" and _operation_targets_quantified_set(op, entity_meta):
            warnings.append("skipped quantified set assertion without individual expansion")
            continue
        if polarity == "negative" and operation == "assert" and not _is_negative_event_predicate(predicate):
            warnings.append("skipped negative assertion pending explicit negation policy")
            continue
        args = _operation_args(op.get("args"), entity_names=entity_names, for_query=operation == "query")
        if operation == "assert":
            facts.append(_clause(predicate, args))
        elif operation == "query":
            queries.append(_clause(predicate, args))
        elif operation == "retract":
            retracts.extend(_retract_clause_variants(predicate, args))
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
    logic_parts = facts + rules + queries
    if not logic_parts and retracts:
        logic_parts = [_retract_command(clause) for clause in retracts]
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


def _projected_decision(ir: dict[str, Any]) -> str:
    decision = _normalize_decision(ir.get("decision"))
    if _is_pure_hypothetical_query(ir):
        return "answer"
    if decision == "commit" and _has_safe_direct_write(ir) and _has_unsafe_implications(ir):
        return "mixed"
    if decision == "commit" and _has_safe_direct_write(ir) and _has_claim_and_direct_assertions(ir):
        return "mixed"
    if (
        decision == "quarantine"
        and _raw_missing_slots(ir)
        and not _missing_slots(ir)
        and _has_safe_direct_write(ir)
    ):
        return "mixed"
    if decision == "quarantine" and str(ir.get("turn_type", "")).strip().lower() == "correction":
        if _has_safe_direct_retract(ir):
            return "mixed"
    return decision


def projected_semantic_ir_decision(ir: dict[str, Any]) -> str:
    return _projected_decision(ir)


def _intent_from_ir(ir: dict[str, Any]) -> str:
    safe_ops: list[str] = []
    if _is_pure_hypothetical_query(ir):
        return "query"
    for op in _candidate_operations(ir):
        if str(op.get("safety", "")).strip().lower() != "safe":
            continue
        operation = str(op.get("operation", "")).strip().lower()
        source = str(op.get("source", "")).strip().lower()
        polarity = str(op.get("polarity", "positive") or "positive").strip().lower()
        if source == "inferred":
            continue
        predicate = _predicate_name(op.get("predicate"))
        if polarity == "negative" and operation == "assert" and not _is_negative_event_predicate(predicate):
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


def _entity_metadata_map(ir: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    raw = ir.get("entities", [])
    if not isinstance(raw, list):
        return out
    for item in raw:
        if not isinstance(item, dict):
            continue
        entity_id = str(item.get("id", "")).strip()
        if entity_id:
            out[entity_id] = item
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


def _retract_command(clause: str) -> str:
    target = str(clause or "").strip()
    target = target[:-1] if target.endswith(".") else target
    return _ensure_period(f"retract({target})")


def _retract_clause_variants(predicate: str, args: list[str]) -> list[str]:
    variants: list[list[str]] = [[]]
    for arg in args:
        choices = _term_aliases_for_retract(arg)
        variants = [prefix + [choice] for prefix in variants for choice in choices]
    clauses: list[str] = []
    seen: set[str] = set()
    for variant_args in variants[:8]:
        clause = _clause(predicate, variant_args)
        if clause not in seen:
            seen.add(clause)
            clauses.append(clause)
    return clauses


def _term_aliases_for_retract(term: str) -> list[str]:
    raw = str(term or "").strip()
    if not raw:
        return ["unknown"]
    aliases = [raw]
    compact = re.sub(r"(?<=[a-zA-Z])_(?=\d)", "", raw)
    compact = re.sub(r"(?<=\d)_(?=[a-zA-Z])", "", compact)
    if compact and compact != raw:
        aliases.append(compact)
    split_number = re.sub(r"(?<=[a-zA-Z])(?=\d)", "_", compact)
    if split_number and split_number not in aliases:
        aliases.append(split_number)
    return aliases


def _is_negative_event_predicate(predicate: str) -> bool:
    return predicate in {
        "denied",
        "denies",
        "denial",
        "refuted",
        "disputed",
        "rejected_claim",
    }


def _has_safe_direct_write(ir: dict[str, Any]) -> bool:
    for op in _candidate_operations(ir):
        if str(op.get("safety", "")).strip().lower() != "safe":
            continue
        if str(op.get("source", "")).strip().lower() != "direct":
            continue
        if str(op.get("operation", "")).strip().lower() in {"assert", "retract", "rule"}:
            return True
    return False


def _has_unsafe_implications(ir: dict[str, Any]) -> bool:
    raw = ir.get("unsafe_implications", [])
    if not isinstance(raw, list):
        return False
    return any(
        isinstance(item, dict) and not _unsafe_implication_duplicates_safe_operation(item, ir)
        for item in raw
    )


def _unsafe_implication_duplicates_safe_operation(item: dict[str, Any], ir: dict[str, Any]) -> bool:
    candidate = str(item.get("candidate", "")).strip().lower()
    if not candidate:
        return False
    for op in _candidate_operations(ir):
        if str(op.get("safety", "")).strip().lower() != "safe":
            continue
        operation = str(op.get("operation", "")).strip().lower()
        predicate = _predicate_name(op.get("predicate"))
        args = _operation_args(op.get("args"), entity_names=_entity_name_map(ir), for_query=operation == "query")
        if operation and operation not in candidate:
            continue
        if predicate and predicate not in candidate:
            continue
        if all(str(arg).strip().lower() in candidate for arg in args):
            return True
    return False


def _has_claim_and_direct_assertions(ir: dict[str, Any]) -> bool:
    raw = ir.get("assertions", [])
    if not isinstance(raw, list):
        return False
    kinds = {
        str(item.get("kind", "")).strip().lower()
        for item in raw
        if isinstance(item, dict)
    }
    return "claim" in kinds and "direct" in kinds


def _has_safe_direct_retract(ir: dict[str, Any]) -> bool:
    for op in _candidate_operations(ir):
        if str(op.get("safety", "")).strip().lower() != "safe":
            continue
        if str(op.get("source", "")).strip().lower() != "direct":
            continue
        if str(op.get("operation", "")).strip().lower() == "retract":
            return True
    return False


def _operation_targets_quantified_set(op: dict[str, Any], entity_meta: dict[str, dict[str, Any]]) -> bool:
    raw_args = op.get("args", [])
    if not isinstance(raw_args, list):
        return False
    for arg in raw_args:
        entity_id = ""
        if isinstance(arg, dict):
            entity_id = str(arg.get("id") or arg.get("entity") or arg.get("value") or "").strip()
        else:
            entity_id = str(arg or "").strip()
        meta = entity_meta.get(entity_id)
        if not isinstance(meta, dict):
            continue
        surface = str(meta.get("surface") or "").strip().lower()
        normalized = str(meta.get("normalized") or "").strip().lower()
        if surface.startswith(("all ", "every ", "each ")):
            return True
        if normalized in {"all", "everyone", "everybody"}:
            return True
    return False


def _is_pure_hypothetical_query(ir: dict[str, Any]) -> bool:
    turn_type = str(ir.get("turn_type", "")).strip().lower()
    if turn_type not in {"query", "unknown"} and _normalize_decision(ir.get("decision")) != "answer":
        text = " ".join(
            [
                str(ir.get("decision", "")),
                json.dumps(ir.get("self_check", {}), ensure_ascii=False),
                json.dumps(ir.get("unsafe_implications", []), ensure_ascii=False),
            ]
        ).lower()
        if "hypothetical" not in text and "counterfactual" not in text:
            return False
    ops = _candidate_operations(ir)
    if not ops:
        return False
    safe_queries = [
        op
        for op in ops
        if str(op.get("operation", "")).strip().lower() == "query"
        and str(op.get("safety", "")).strip().lower() == "safe"
    ]
    if not safe_queries:
        return False
    unsafe_writes = [
        op
        for op in ops
        if str(op.get("operation", "")).strip().lower() in {"assert", "retract", "rule"}
        and str(op.get("source", "")).strip().lower() != "context"
    ]
    if unsafe_writes:
        return False
    text = flatten_semantic_text(ir)
    return "hypothetical" in text or "counterfactual" in text or "if " in text or "would" in text


def flatten_semantic_text(value: Any) -> str:
    if isinstance(value, str):
        return value.lower()
    if isinstance(value, dict):
        return " ".join(flatten_semantic_text(item) for item in value.values())
    if isinstance(value, list):
        return " ".join(flatten_semantic_text(item) for item in value)
    return str(value).lower()


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


OPTIONAL_METADATA_MISSING_SLOTS = {
    "source_document_id",
    "source_note_id",
    "source_encounter_id",
    "reason",
    "reason_for_quarantine",
    "quarantine_reason",
    "authority",
}


def _raw_missing_slots(ir: dict[str, Any]) -> list[str]:
    self_check = ir.get("self_check", {})
    if not isinstance(self_check, dict):
        return []
    return _string_list(self_check.get("missing_slots", []))


def _missing_slots(ir: dict[str, Any]) -> list[str]:
    slots = _raw_missing_slots(ir)
    if _has_safe_direct_write(ir):
        return [
            slot
            for slot in slots
            if slot.strip().lower() not in OPTIONAL_METADATA_MISSING_SLOTS
        ]
    return slots


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
