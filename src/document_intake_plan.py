from __future__ import annotations

import json
import re
from typing import Any


INTAKE_PLAN_CONTRACT: dict[str, Any] = {
    "schema_version": "intake_plan_v1",
    "source_boundary": {
        "source_id_hint": "",
        "source_type": "",
        "epistemic_stance": "",
        "why": "",
    },
    "symbolic_strategy": [""],
    "entity_strategy": [""],
    "predicate_family_strategy": [
        {
            "family": "",
            "purpose": "",
            "recommended_predicates": ["predicate_name/2"],
            "epistemic_status": "",
        }
    ],
    "pass_plan": [
        {
            "pass_id": "pass_1",
            "purpose": "",
            "focus": "",
            "operation_budget": "",
            "recommended_predicates": ["predicate_name/2"],
            "coverage_goals": [""],
            "completion_policy": "",
        }
    ],
    "risk_policy": [""],
    "self_check": {
        "plan_authority": "proposal_only",
        "notes": [""],
    },
}


INTAKE_PLAN_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "schema_version",
        "source_boundary",
        "symbolic_strategy",
        "entity_strategy",
        "predicate_family_strategy",
        "pass_plan",
        "risk_policy",
        "self_check",
    ],
    "properties": {
        "schema_version": {"type": "string", "const": "intake_plan_v1"},
        "source_boundary": {
            "type": "object",
            "additionalProperties": False,
            "required": ["source_id_hint", "source_type", "epistemic_stance", "why"],
            "properties": {
                "source_id_hint": {"type": "string"},
                "source_type": {"type": "string"},
                "epistemic_stance": {"type": "string"},
                "why": {"type": "string"},
            },
        },
        "symbolic_strategy": {"type": "array", "maxItems": 12, "items": {"type": "string"}},
        "entity_strategy": {"type": "array", "maxItems": 12, "items": {"type": "string"}},
        "predicate_family_strategy": {
            "type": "array",
            "maxItems": 12,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["family", "purpose", "recommended_predicates", "epistemic_status"],
                "properties": {
                    "family": {"type": "string"},
                    "purpose": {"type": "string"},
                    "recommended_predicates": {"type": "array", "maxItems": 32, "items": {"type": "string"}},
                    "epistemic_status": {"type": "string"},
                },
            },
        },
        "pass_plan": {
            "type": "array",
            "maxItems": 12,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "pass_id",
                    "purpose",
                    "focus",
                    "operation_budget",
                    "recommended_predicates",
                    "coverage_goals",
                    "completion_policy",
                ],
                "properties": {
                    "pass_id": {"type": "string"},
                    "purpose": {"type": "string"},
                    "focus": {"type": "string"},
                    "operation_budget": {"type": "string"},
                    "recommended_predicates": {"type": "array", "maxItems": 32, "items": {"type": "string"}},
                    "coverage_goals": {"type": "array", "maxItems": 10, "items": {"type": "string"}},
                    "completion_policy": {"type": "string"},
                },
            },
        },
        "risk_policy": {"type": "array", "maxItems": 12, "items": {"type": "string"}},
        "self_check": {
            "type": "object",
            "additionalProperties": False,
            "required": ["plan_authority", "notes"],
            "properties": {
                "plan_authority": {"type": "string", "const": "proposal_only"},
                "notes": {"type": "array", "maxItems": 12, "items": {"type": "string"}},
            },
        },
    },
}


INTAKE_PLAN_SYSTEM = (
    "You are an intake planner for a governed symbolic compiler. "
    "You do not emit Prolog, semantic_ir_v1, durable facts, or KB writes. "
    "Your job is to do the high-level document-to-logic strategy a skilled logic engineer would do before compiling: "
    "source boundary, epistemic stance, predicate-family plan, entity strategy, and pass plan."
)


INTAKE_PLAN_GUIDANCE = (
    "Read the raw source as a whole and plan how it should be compiled later.\n"
    "Model the source's epistemic structure, not just grammar.\n"
    "Ask: What kind of source is this? Who is speaking? Which statements are claims, observations, rules, declarations, "
    "policies, measurements, identity ambiguities, or test scaffolds? Which repeated structures need stable ids? "
    "Which details need their own predicates because people will query them later?\n"
    "Do not enumerate all facts. Do not produce final Prolog. Design the compilation strategy.\n"
    "Prefer a multi-pass plan for dense documents: source metadata, entity taxonomy, principles/rules, repeated records, "
    "observations/evidence, final declarations/policies, pledges, and test/admission rules when relevant.\n"
    "Do not put a long list of unrelated incidents into one broad pass. If a source has many grievances/incidents, "
    "split the repeated-record work into focused passes such as labeling/custody, ledgers/source records, reporters/"
    "witnesses/complainants, temperature/measurement evidence, identity ambiguity, remedies/declarations, and final "
    "pledges. The later compiler has an operation budget per pass, so overly broad passes silently lose details.\n"
    "When later questions are likely to ask who recorded, reported, witnessed, complained, certified, measured, or "
    "which ledger/log/source contains a statement, make those source-record and reporting acts an explicit pass focus.\n"
    "When the source is full of grievances, allegations, complaints, claims, or other source-owned records, make "
    "epistemic status a first-class predicate-family concern. Later QA should be able to ask whether those records "
    "are source-bound accusations, observations, externally confirmed facts, or unresolved claims.\n"
    "When a rule has a condition, threshold, deadline, interval, exception, or completion requirement, make the "
    "condition a pass focus so the compiler preserves it as a queryable slot instead of a unary rule label.\n"
    "When the source is an insurance, reinsurance, contract-coverage, maritime-loss, warranty, salvage, or "
    "claims-adjustment dispute, plan for scoped contract surfaces and competing accounts rather than a simple event "
    "summary. Include focused passes for parties/roles by contract, insured asset and policy terms, incident timeline, "
    "notifications/deadlines, expert or survey reports, disputed measurements and costs, financial calculation chains, "
    "coverage positions and defenses, reinsurance or retrocession layers, salvage/security status, regulatory positions, "
    "legal citations, corrections, and witness statements when present. Treat source attribution as part of the fact "
    "identity for expert reports and party positions.\n"
    "For insurance dispute sources, dual-role entities require explicit role/context goals. A pass should make clear "
    "which rows distinguish one entity acting under two contracts, two coverages, or two legal capacities. Financial "
    "passes should preserve gross, deductible, net, share, attachment, limit, and difference values with source/basis "
    "rather than only storing one total.\n"
    "When the source is narrative, fictional, fable-like, or story-world material, plan for a story spine rather than "
    "a bag of facts. Include passes for stable cast/entity taxonomy, static possessions/locations, event sequence, "
    "speech acts, subjective evaluations, causal consequences, remediation or repairs, and final states when the "
    "source contains them.\n"
    "For narrative sources, explicitly recommend event/order/causal/final-state predicate families when later QA may "
    "ask what happened first, why something happened, what changed, what remained true after repair, or who knew/said "
    "a claim. If the story has whimsical source-local names, note that source-local naming must be preserved and "
    "famous-story priors must not be imported.\n"
    "For narrative sources, prefer a canonical story-world shape when it fits: event records, story-time order, "
    "before/after links, cause/consequence links, speech acts, subjective judgments, ownership/design relations, "
    "locations before/after events, and final-state facts. Do not encourage multiple near-synonym predicates for the "
    "same slot.\n"
    "When the source is a procedural investigation, misconduct case, disciplinary proceeding, appeal record, or "
    "administrative case file, plan a procedural backbone rather than a summary. Include focused passes for roles and "
    "organizational hierarchy, committee rosters and replacements, proceeding events, deadline requirements/outcomes, "
    "findings and sanctions, witness/source claims, corrections/clarifications, advisory non-determinations, unresolved "
    "questions, federal/external notices, financial dependencies, and temporal order when the source contains them.\n"
    "For procedural sources, explicitly separate findings from sanctions, witness claims from findings, advisory "
    "opinions from determinations, unresolved questions from answered policy questions, and corrected-away values from "
    "current facts. These distinctions are usually what later QA will test.\n"
    "Every pass should say what it focuses on, list explicit coverage_goals, and say what should be omitted or "
    "deferred when operation budget is limited. A coverage goal is a row-class target such as: emit person_role rows "
    "for every named case role; emit committee_member rows for each current roster member; emit deadline_requirement "
    "and deadline_met pairs for each stated deadline; emit finding rows separately from sanction rows; emit "
    "correction rows plus corrected-current facts.\n"
    "Python will only carry this plan forward; deterministic admission still owns writes."
)


def build_intake_plan_messages(
    *,
    source_text: str,
    source_name: str = "",
    domain_hint: str = "",
    candidate_profile_registry: dict[str, Any] | None = None,
) -> list[dict[str, str]]:
    payload = {
        "task": "Analyze raw source and emit intake_plan_v1 JSON only.",
        "source_name": source_name,
        "domain_hint": domain_hint,
        "raw_source_text": source_text,
        "guidance": INTAKE_PLAN_GUIDANCE,
        "required_top_level_json_shape": INTAKE_PLAN_CONTRACT,
    }
    if isinstance(candidate_profile_registry, dict) and candidate_profile_registry:
        payload["candidate_profile_registry_v1"] = _compact_registry_for_intake(candidate_profile_registry)
        payload["registry_policy"] = (
            "The registry is vocabulary/context only, not facts and not authority. "
            "When recommending predicates or coverage goals, prefer exact registry signatures that fit the source. "
            "Do not invent alternate predicate names or arities when a registry signature already covers the row class."
        )
    return [
        {"role": "system", "content": INTAKE_PLAN_SYSTEM},
        {"role": "user", "content": "INPUT_JSON:\n" + json.dumps(payload, ensure_ascii=False, indent=2)},
    ]


def _compact_registry_for_intake(registry: dict[str, Any]) -> dict[str, Any]:
    predicates: list[dict[str, Any]] = []
    for item in registry.get("predicates", []) if isinstance(registry.get("predicates"), list) else []:
        if not isinstance(item, dict):
            continue
        signature = str(item.get("signature", "")).strip()
        if not signature:
            continue
        predicates.append(
            {
                "signature": signature,
                "args": item.get("args", []) if isinstance(item.get("args"), list) else [],
                "category": str(item.get("category", item.get("why", ""))).strip(),
            }
        )
    return {
        "fixture": str(registry.get("fixture", "")).strip(),
        "purpose": str(registry.get("purpose", "")).strip(),
        "predicates": predicates[:160],
    }


def parse_intake_plan_json(text: str) -> tuple[dict[str, Any] | None, str]:
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
    if parsed.get("schema_version") != "intake_plan_v1":
        return None, "wrong_schema_version"
    return parsed, ""


def intake_plan_context(plan: dict[str, Any] | None) -> list[str]:
    if not isinstance(plan, dict):
        return []
    context: list[str] = ["intake_plan_v1: LLM-owned document-to-logic strategy. Use as guidance, not authority."]
    boundary = plan.get("source_boundary") if isinstance(plan.get("source_boundary"), dict) else {}
    for key in ["source_id_hint", "source_type", "epistemic_stance", "why"]:
        value = str(boundary.get(key, "")).strip()
        if value:
            context.append(f"intake_source_{key}: {value}")
    for item in plan.get("symbolic_strategy", []) if isinstance(plan.get("symbolic_strategy"), list) else []:
        text = str(item).strip()
        if text:
            context.append(f"intake_symbolic_strategy: {text}")
    for item in plan.get("entity_strategy", []) if isinstance(plan.get("entity_strategy"), list) else []:
        text = str(item).strip()
        if text:
            context.append(f"intake_entity_strategy: {text}")
    for family in plan.get("predicate_family_strategy", []) if isinstance(plan.get("predicate_family_strategy"), list) else []:
        if not isinstance(family, dict):
            continue
        name = str(family.get("family", "")).strip()
        purpose = str(family.get("purpose", "")).strip()
        predicates = ", ".join(
            str(item).strip()
            for item in family.get("recommended_predicates", [])
            if str(item).strip()
        ) if isinstance(family.get("recommended_predicates"), list) else ""
        status = str(family.get("epistemic_status", "")).strip()
        context.append(f"intake_predicate_family: {name}; purpose={purpose}; status={status}; predicates={predicates}")
    for item in plan.get("pass_plan", []) if isinstance(plan.get("pass_plan"), list) else []:
        if not isinstance(item, dict):
            continue
        pass_id = str(item.get("pass_id", "")).strip()
        purpose = str(item.get("purpose", "")).strip()
        focus = str(item.get("focus", "")).strip()
        budget = str(item.get("operation_budget", "")).strip()
        policy = str(item.get("completion_policy", "")).strip()
        predicates = ", ".join(
            str(row).strip()
            for row in item.get("recommended_predicates", [])
            if str(row).strip()
        ) if isinstance(item.get("recommended_predicates"), list) else ""
        goals = " | ".join(
            str(row).strip()
            for row in item.get("coverage_goals", [])
            if str(row).strip()
        ) if isinstance(item.get("coverage_goals"), list) else ""
        context.append(
            f"intake_pass: {pass_id}; purpose={purpose}; focus={focus}; budget={budget}; "
            f"completion={policy}; predicates={predicates}; coverage_goals={goals}"
        )
    for item in plan.get("risk_policy", []) if isinstance(plan.get("risk_policy"), list) else []:
        text = str(item).strip()
        if text:
            context.append(f"intake_risk_policy: {text}")
    return context
