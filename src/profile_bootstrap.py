from __future__ import annotations

import json
import re
from typing import Any


PROFILE_BOOTSTRAP_CONTRACT: dict[str, Any] = {
    "schema_version": "profile_bootstrap_v1",
    "domain_guess": "",
    "domain_scope": "",
    "confidence": 0.0,
    "source_summary": [""],
    "entity_types": [
        {
            "name": "",
            "description": "",
            "examples": [""],
        }
    ],
    "candidate_predicates": [
        {
            "signature": "predicate_name/2",
            "args": ["arg_role_1", "arg_role_2"],
            "description": "",
            "why": "",
            "admission_notes": [""],
        }
    ],
    "likely_functional_predicates": [""],
    "provenance_sensitive_predicates": [""],
    "admission_risks": [""],
    "clarification_policy": [""],
    "unsafe_transformations": [""],
    "starter_frontier_cases": [
        {
            "utterance": "",
            "expected_boundary": "",
            "must_not_write": [""],
        }
    ],
    "self_check": {
        "profile_authority": "proposal_only",
        "notes": [""],
    },
}


PROFILE_BOOTSTRAP_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "schema_version",
        "domain_guess",
        "domain_scope",
        "confidence",
        "source_summary",
        "entity_types",
        "candidate_predicates",
        "likely_functional_predicates",
        "provenance_sensitive_predicates",
        "admission_risks",
        "clarification_policy",
        "unsafe_transformations",
        "starter_frontier_cases",
        "self_check",
    ],
    "properties": {
        "schema_version": {"type": "string", "const": "profile_bootstrap_v1"},
        "domain_guess": {"type": "string"},
        "domain_scope": {"type": "string"},
        "confidence": {"type": "number"},
        "source_summary": {"type": "array", "items": {"type": "string"}},
        "entity_types": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["name", "description", "examples"],
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "examples": {"type": "array", "items": {"type": "string"}},
                },
            },
        },
        "candidate_predicates": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["signature", "args", "description", "why", "admission_notes"],
                "properties": {
                    "signature": {"type": "string"},
                    "args": {"type": "array", "items": {"type": "string"}},
                    "description": {"type": "string"},
                    "why": {"type": "string"},
                    "admission_notes": {"type": "array", "items": {"type": "string"}},
                },
            },
        },
        "likely_functional_predicates": {"type": "array", "items": {"type": "string"}},
        "provenance_sensitive_predicates": {"type": "array", "items": {"type": "string"}},
        "admission_risks": {"type": "array", "items": {"type": "string"}},
        "clarification_policy": {"type": "array", "items": {"type": "string"}},
        "unsafe_transformations": {"type": "array", "items": {"type": "string"}},
        "starter_frontier_cases": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["utterance", "expected_boundary", "must_not_write"],
                "properties": {
                    "utterance": {"type": "string"},
                    "expected_boundary": {"type": "string"},
                    "must_not_write": {"type": "array", "items": {"type": "string"}},
                },
            },
        },
        "self_check": {
            "type": "object",
            "additionalProperties": False,
            "required": ["profile_authority", "notes"],
            "properties": {
                "profile_authority": {"type": "string", "const": "proposal_only"},
                "notes": {"type": "array", "items": {"type": "string"}},
            },
        },
    },
}


PROFILE_BOOTSTRAP_SYSTEM = (
    "You propose profile_bootstrap_v1 JSON for Prethinker domain-profile design. "
    "You are not extracting durable facts and you are not authorizing KB writes. "
    "Infer a compact predicate/entity surface from representative text, preserving "
    "claim/fact, obligation/fact, condition/event, provenance, and ambiguity boundaries."
)


PROFILE_BOOTSTRAP_GUIDANCE = (
    "Task:\n"
    "- Analyze the sample texts as a possible domain profile seed.\n"
    "- Propose reusable entity types, candidate predicates, argument roles, admission risks, "
    "clarification policies, unsafe transformations, and starter frontier cases.\n"
    "- Prefer small, typed predicates over vague catch-all predicates.\n"
    "- Prefer admission-ready predicates that name the domain relation directly. For example, "
    "submitted_by/2, approved_by/2, sent_on/2, obligation/3, conditional_right/3, "
    "subject_to/2, source_priority/3, and waiver/2 are usually better than generic "
    "event_occurred/2, policy_constraint/2, candidate_relation/4, or related_to/2.\n"
    "- If you need a generic predicate, explain why a more specific predicate is not yet justified.\n"
    "- Mark predicates that likely need provenance or functional/current-state handling.\n"
    "- Provenance-sensitive is not the same as unsafe. If a source directly states submitted_by, "
    "approved_by, sent_on, authored_by, filed_on, etc., the starter case may include that predicate "
    "as a positive expected boundary. Put only overreach, missing-condition conclusions, inferred "
    "violations, or unsupported relations in must_not_write.\n"
    "- If an utterance directly states several safe relations, include the safe relations rather than "
    "silently dropping them. For example, a report that says an invoice was submitted by one person "
    "and approved by another may include both submitted_by and approved_by boundaries; the unsafe "
    "part is inferring conflict or management that the report does not state.\n"
    "- Starter frontier cases should exercise the candidate predicates you actually proposed. "
    "Do not describe expected positive writes using predicates absent from candidate_predicates; "
    "unproposed predicates are fine only inside must_not_write as examples of unsafe writes.\n"
    "- In starter_frontier_cases.expected_boundary, every positive predicate signature such as "
    "approved_by/2 or obligation/3, and every positive predicate call such as approved_by(x, y), "
    "must match a predicate and arity in candidate_predicates. Do not add informal named arguments "
    "such as source=... to a /2 predicate call; either propose a provenance-aware arity or explain "
    "provenance in prose. If you want to show a predicate that must be rejected, put it after "
    "'Do not write' or inside must_not_write.\n"
    "- Treat action and condition arguments as atomic normalized labels unless you explicitly propose "
    "the nested predicate. Prefer borrower_default, sponsored_by_manager, no_unpaid_invoice, and "
    "witnessed_by_two_non_beneficiaries over default(borrower), sponsored_by(...), not(...), or "
    "witnessed_by_two_non_beneficiaries(...).\n"
    "- Before finalizing, self-audit starter_frontier_cases: collect every positive predicate call "
    "in expected_boundary and confirm its exact name/arity appears in candidate_predicates. If any "
    "positive call is missing, either add that predicate with argument roles or rewrite the case to "
    "use an existing proposed predicate.\n"
    "- Include examples from the samples, but do not invent durable facts.\n"
    "Safety boundary:\n"
    "- This output is profile-design material only.\n"
    "- Do not claim the proposed profile is approved.\n"
    "- Do not emit semantic_ir_v1, Prolog clauses, or ordinary KB writes.\n"
)


def build_profile_bootstrap_payload(
    *,
    samples: list[dict[str, Any]],
    domain_hint: str = "",
    existing_profiles: list[dict[str, Any]] | None = None,
    include_schema_contract: bool = True,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "task": "Analyze representative texts and emit profile_bootstrap_v1 JSON only.",
        "domain_hint": domain_hint,
        "samples": samples,
        "existing_profile_roster": existing_profiles or [],
        "output_guidance": PROFILE_BOOTSTRAP_GUIDANCE,
        "authority_boundary": (
            "The model proposes a candidate domain vocabulary. Humans and deterministic "
            "review decide whether any profile becomes approved."
        ),
    }
    if include_schema_contract:
        payload["required_top_level_json_shape"] = PROFILE_BOOTSTRAP_CONTRACT
    return payload


def build_profile_bootstrap_messages(
    *,
    samples: list[dict[str, Any]],
    domain_hint: str = "",
    existing_profiles: list[dict[str, Any]] | None = None,
    include_schema_contract: bool = True,
) -> list[dict[str, str]]:
    payload = build_profile_bootstrap_payload(
        samples=samples,
        domain_hint=domain_hint,
        existing_profiles=existing_profiles,
        include_schema_contract=include_schema_contract,
    )
    return [
        {"role": "system", "content": PROFILE_BOOTSTRAP_SYSTEM},
        {"role": "user", "content": "INPUT_JSON:\n" + json.dumps(payload, ensure_ascii=False, indent=2)},
    ]


def parse_profile_bootstrap_json(text: str) -> tuple[dict[str, Any] | None, str]:
    raw = str(text or "").strip()
    if not raw:
        return None, "empty"
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, flags=re.S)
        if not match:
            return None, "not_json"
        try:
            parsed = json.loads(match.group(0))
        except json.JSONDecodeError as exc:
            return None, f"json_error:{exc}"
    if not isinstance(parsed, dict):
        return None, "json_not_object"
    if parsed.get("schema_version") != "profile_bootstrap_v1":
        return None, "wrong_schema_version"
    return parsed, ""


def profile_bootstrap_score(parsed: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(parsed, dict):
        return {
            "schema_ok": False,
            "entity_type_count": 0,
            "predicate_count": 0,
            "risk_count": 0,
            "frontier_case_count": 0,
            "frontier_unknown_positive_predicate_count": 0,
            "frontier_unknown_positive_predicate_refs": [],
            "rough_score": 0.0,
        }
    schema_ok = parsed.get("schema_version") == "profile_bootstrap_v1"
    entity_count = len([item for item in parsed.get("entity_types", []) if isinstance(item, dict)])
    predicates = [item for item in parsed.get("candidate_predicates", []) if isinstance(item, dict)]
    predicate_count = len(predicates)
    generic_names = {"event_occurred", "policy_constraint", "candidate_relation", "related_to", "has_relation"}
    generic_predicate_count = 0
    for item in predicates:
        signature = str(item.get("signature", ""))
        name = signature.split("/", 1)[0].strip().casefold()
        if name in generic_names:
            generic_predicate_count += 1
    proposed_signatures = {_signature_key(str(item.get("signature", ""))) for item in predicates}
    proposed_signatures.discard("")
    risk_count = len([item for item in parsed.get("admission_risks", []) if str(item).strip()])
    frontier_cases = [item for item in parsed.get("starter_frontier_cases", []) if isinstance(item, dict)]
    frontier_count = len(frontier_cases)
    unknown_frontier_refs: list[str] = []
    for item in frontier_cases:
        positive_text = _positive_boundary_text(str(item.get("expected_boundary", "")))
        for ref in _predicate_refs(positive_text):
            if ref not in proposed_signatures:
                unknown_frontier_refs.append(ref)
    unknown_frontier_refs = sorted(set(unknown_frontier_refs))
    specificity_score = 1.0 - min(generic_predicate_count, max(1, predicate_count)) / max(1, predicate_count)
    frontier_consistency = 1.0 if not unknown_frontier_refs else 0.0
    rough_score = (
        (1 if schema_ok else 0)
        + min(entity_count, 4) / 4
        + min(predicate_count, 6) / 6
        + min(risk_count, 4) / 4
        + min(frontier_count, 3) / 3
        + specificity_score
        + frontier_consistency
    ) / 7
    return {
        "schema_ok": schema_ok,
        "entity_type_count": entity_count,
        "predicate_count": predicate_count,
        "generic_predicate_count": generic_predicate_count,
        "frontier_unknown_positive_predicate_count": len(unknown_frontier_refs),
        "frontier_unknown_positive_predicate_refs": unknown_frontier_refs,
        "risk_count": risk_count,
        "frontier_case_count": frontier_count,
        "rough_score": round(float(rough_score), 3),
    }


def _signature_key(signature: str) -> str:
    match = re.fullmatch(r"\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*/\s*(\d+)\s*", signature)
    if not match:
        return ""
    return f"{match.group(1).casefold()}/{match.group(2)}"


def _predicate_refs(text: str) -> set[str]:
    refs: set[str] = set()
    for match in re.finditer(r"\b([a-zA-Z_][a-zA-Z0-9_]*)/(\d+)\b", str(text or "")):
        refs.add(f"{match.group(1).casefold()}/{match.group(2)}")
    refs.update(_predicate_call_refs(str(text or "")))
    return refs


def _predicate_call_refs(text: str) -> set[str]:
    refs: set[str] = set()
    raw = str(text or "")
    for match in re.finditer(r"\b([a-z][a-z0-9_]*)\s*\(", raw):
        name = match.group(1).casefold()
        close_index = _matching_paren(raw, match.end() - 1)
        if close_index is None:
            continue
        args_text = raw[match.end() : close_index]
        refs.add(f"{name}/{_arity(args_text)}")
    return refs


def _matching_paren(text: str, open_index: int) -> int | None:
    depth = 0
    for index in range(open_index, len(text)):
        char = text[index]
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return index
    return None


def _arity(args_text: str) -> int:
    text = str(args_text or "").strip()
    if not text:
        return 0
    depth = 0
    count = 1
    for char in text:
        if char == "(":
            depth += 1
        elif char == ")":
            depth = max(0, depth - 1)
        elif char == "," and depth == 0:
            count += 1
    return count


def _positive_boundary_text(text: str) -> str:
    match = re.search(r"\bdo\s+not\s+write\b", str(text or ""), flags=re.I)
    if not match:
        return str(text or "")
    return str(text or "")[: match.start()]
