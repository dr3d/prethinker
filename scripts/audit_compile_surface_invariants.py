"""Audit compile artifacts for direct answer-bearing surface invariants.

This is a pre-QA readiness check. It reads domain-bootstrap compile JSON and
asks whether generic surface families visible in the source-record ledger also
appear as admitted non-source-record facts. The goal is to catch compile
sparsity before spending QA/judge cycles or falling back to legacy helpers.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


FACT_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\((.*)\)\.\s*$")
TOKEN_RE = re.compile(r"[a-z0-9]+")
NUMBER_WORDS = {
    "zero",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "ten",
    "eleven",
    "twelve",
    "thirteen",
    "fourteen",
    "fifteen",
    "sixteen",
    "seventeen",
    "eighteen",
    "nineteen",
    "twenty",
}
PROMOTABLE_SOURCE_RECORD_MARKERS = {
    "abandoned",
    "access",
    "assigned",
    "available",
    "calibration",
    "coach",
    "contested",
    "correction",
    "date",
    "device",
    "discovered",
    "due",
    "errata",
    "group",
    "identifier",
    "manager",
    "motion",
    "next",
    "not",
    "overruled",
    "registrar",
    "role",
    "scanner",
    "scheduled",
    "status",
    "ticket",
}
SOURCE_RECORD_STOP_TOKENS = {
    "a",
    "an",
    "and",
    "as",
    "by",
    "for",
    "in",
    "line",
    "of",
    "on",
    "or",
    "per",
    "record",
    "row",
    "section",
    "source",
    "src",
    "the",
    "to",
    "v",
}


@dataclass(frozen=True)
class InvariantSpec:
    family: str
    description: str
    groups: dict[str, tuple[str, ...]]


@dataclass(frozen=True)
class RelationContractSpec:
    contract: str
    description: str
    required_predicate: str
    companion_predicate: str
    required_key_indexes: tuple[int, ...]
    companion_key_indexes: tuple[int, ...]


INVARIANTS: tuple[InvariantSpec, ...] = (
    InvariantSpec(
        family="identity_role_surface",
        description="named people or organizations with answer-bearing roles",
        groups={
            "registrar_or_recorder": ("registrar", "compiler", "compiled", "recorder", "recorded"),
            "operator_or_attendant": ("operator", "attendant", "console"),
            "custodian_or_holder": ("custodian", "custody", "holder", "held"),
            "clinical_or_safety_role": ("nurse", "medical", "safety", "reviewer", "observer"),
            "legal_or_claim_role": ("counsel", "claimant", "appellant", "respondent"),
            "supervisor_or_authority": ("supervisor", "authorized", "authority", "approver", "approved"),
        },
    ),
    InvariantSpec(
        family="source_addressability_surface",
        description="named sections, titles, register parts, and source coordinates",
        groups={
            "section_coordinate": ("section", "subsection", "part", "appendix"),
            "title_or_heading": ("title", "heading", "caption"),
            "chronology_coordinate": ("chronology", "timeline", "sequence"),
            "negative_inference_coordinate": ("inference", "available", "unavailable", "not", "absence"),
            "basis_coordinate": ("basis", "reason", "ground", "corroborated"),
        },
    ),
    InvariantSpec(
        family="source_authority_surface",
        description="source documents, authority/evidence roles, source actors or dates, and governed subjects",
        groups={
            "source_document_or_correspondence": (
                "document",
                "correspondence",
                "letter",
                "report",
                "catalog",
                "register",
                "policy",
                "order",
                "source",
            ),
            "authority_or_evidence_role": (
                "authority",
                "authorized",
                "governs",
                "governed",
                "evidence",
                "finding",
                "basis",
            ),
            "source_actor_or_date": (
                "actor",
                "author",
                "dated",
                "date",
                "registrar",
                "court",
                "reporter",
                "prepared",
            ),
            "governed_subject_or_item": (
                "subject",
                "item",
                "object",
                "claim",
                "access",
                "status",
                "finding",
                "action",
            ),
        },
    ),
    InvariantSpec(
        family="answer_detail_surface",
        description="source-stated answer details, rationales, availability/scope, commitments, and exclusions",
        groups={
            "detail_or_explanation": (
                "detail",
                "explanation",
                "reason",
                "rationale",
                "basis",
                "because",
            ),
            "availability_or_scope": (
                "available",
                "availability",
                "scope",
                "separate",
                "agreement",
                "outside",
            ),
            "commitment_or_future_action": (
                "promise",
                "promised",
                "acknowledgment",
                "commitment",
                "will",
                "pending",
            ),
            "negative_or_exclusion_detail": (
                "not",
                "excluded",
                "denied",
                "rejected",
                "without",
                "unresolved",
            ),
        },
    ),
    InvariantSpec(
        family="status_state_surface",
        description="point-in-time status/state, current condition, transitions, and scoped population state",
        groups={
            "subject_or_population": (
                "application",
                "case",
                "document",
                "item",
                "lot",
                "permit",
                "population",
                "record",
                "request",
                "sample",
                "subject",
            ),
            "state_or_status_value": (
                "active",
                "approved",
                "available",
                "cleared",
                "condition",
                "current",
                "denied",
                "failed",
                "hold",
                "pending",
                "resolved",
                "state",
                "status",
                "suspect",
            ),
            "temporal_or_source_scope": (
                "as",
                "at",
                "current",
                "date",
                "dated",
                "effective",
                "final",
                "initial",
                "on",
                "source",
                "time",
            ),
            "transition_or_resolution": (
                "after",
                "before",
                "changed",
                "from",
                "not",
                "reclassified",
                "replaced",
                "superseded",
                "to",
                "voided",
            ),
        },
    ),
    InvariantSpec(
        family="participant_statement_surface",
        description="speaker/actor statements, advice, estimates, comments, clarifications, content, context, and binding status",
        groups={
            "speaker_or_actor": (
                "speaker",
                "actor",
                "author",
                "commenter",
                "participant",
                "staff",
                "member",
                "official",
            ),
            "speech_act_or_record_type": (
                "statement",
                "comment",
                "advice",
                "opinion",
                "estimate",
                "certification",
                "clarification",
                "caveat",
                "observation",
                "said",
                "stated",
                "suggested",
                "asked",
            ),
            "content_or_position": (
                "content",
                "proposition",
                "position",
                "concern",
                "support",
                "supported",
                "oppose",
                "opposed",
                "agree",
                "question",
                "reason",
            ),
            "context_or_source_event": (
                "hearing",
                "meeting",
                "discussion",
                "memo",
                "record",
                "source",
                "date",
                "translation",
            ),
            "binding_or_epistemic_status": (
                "binding",
                "advisory",
                "nonbinding",
                "non",
                "not",
                "informational",
                "observation",
                "opinion",
            ),
        },
    ),
    InvariantSpec(
        family="rule_policy_surface",
        description="rules, policies, procedure identifiers, clauses, ratios, and governing sections",
        groups={
            "policy_or_rule_id": ("policy", "rule", "procedure", "manual", "clause", "section"),
            "ratio_or_requirement": ("ratio", "minimum", "required", "requirement", "qualifying"),
            "exception_or_exclusion": ("exception", "excluding", "exclusion", "unless", "not"),
        },
    ),
    InvariantSpec(
        family="object_device_surface",
        description="objects, devices, systems, vendor/model identifiers, and inventory ids",
        groups={
            "device_or_system": ("device", "sensor", "system", "instrument", "console"),
            "vendor_or_model": ("vendor", "model", "manufacturer", "make", "sensor_info", "system_info", "device_info"),
            "object_or_item_id": ("object", "item", "inventory", "specimen", "sample", "id", "item_id", "item_description"),
        },
    ),
    InvariantSpec(
        family="temporal_event_surface",
        description="events, raw/corrected timestamps, effective dates, and transitions",
        groups={
            "event_or_action": ("event", "action", "incident", "change", "transition"),
            "timestamp_or_date": ("timestamp", "time", "date", "dated"),
            "correction_or_supersession": ("corrected", "correction", "raw", "original", "superseded"),
            "interval_or_window": ("interval", "window", "start", "end", "deadline"),
        },
    ),
    InvariantSpec(
        family="event_backbone_unit_surface",
        description="event rows whose identity, temporal anchor, participant, governed subject, and outcome remain joinable",
        groups={
            "event_identity": ("event", "entry", "record", "incident", "log"),
            "temporal_anchor": ("timestamp", "time", "date", "dated", "chronological", "order"),
            "participant_or_system": ("actor", "operator", "system", "party", "participant", "originated"),
            "subject_or_object": ("subject", "object", "item", "sample", "request", "proposal", "debt"),
            "outcome_or_state": ("status", "outcome", "result", "state", "settled", "void", "issued"),
        },
    ),
    InvariantSpec(
        family="measure_count_surface",
        description="explicit counts, thresholds, durations, percentages, and computed requirements",
        groups={
            "count_or_total": ("count", "total", "number", "manifest"),
            "threshold_or_limit": ("threshold", "limit", "minimum", "maximum"),
            "duration_or_hours": ("hour", "hours", "day", "days", "duration"),
            "ratio_or_formula": ("ratio", "per", "computed", "formula", "ceil", "ceiling"),
            "measurement_value": ("percent", "rh", "kg", "minute", "second", "value"),
        },
    ),
    InvariantSpec(
        family="financial_baseline_surface",
        description="financial or numeric-state baselines, adjustments, scenarios, resulting values, and thresholds",
        groups={
            "baseline_value": ("baseline", "starting", "initial", "current", "balance", "reserve"),
            "adjustment_value": ("adjustment", "debit", "credit", "subtraction", "addition", "minus", "expenditure", "appropriation"),
            "scenario_or_actuality": ("actual", "hypothetical", "counterfactual", "would", "if", "after", "before"),
            "resulting_value": ("result", "resulting", "remaining", "new", "final", "post"),
            "constraint_or_threshold": ("minimum", "maximum", "threshold", "limit", "policy", "breach"),
        },
    ),
    InvariantSpec(
        family="custody_control_surface",
        description="custody, access, ownership, recall/return, and control state",
        groups={
            "custody_or_possession": ("custody", "possession", "possessor", "holder", "held"),
            "ownership_or_title": ("owner", "ownership", "title"),
            "access_or_location": ("access", "location", "storage", "room"),
            "recall_or_return": ("recall", "return", "loan", "retrieve"),
        },
    ),
)


RELATION_CONTRACTS: tuple[RelationContractSpec, ...] = (
    RelationContractSpec(
        contract="access_authority_source_pair",
        description="authorized access item/party pairs should expose the source or authority companion row",
        required_predicate="access_authorized_to",
        companion_predicate="access_source",
        required_key_indexes=(0, 1),
        companion_key_indexes=(0, 1),
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--compile-json",
        action="append",
        type=Path,
        default=[],
        help="Compile JSON file or directory containing domain_bootstrap_file_*.json. Repeatable.",
    )
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    paths = _expand_compile_paths(args.compile_json)
    if not paths:
        raise SystemExit("No compile JSON files found.")
    reports = [audit_compile(path) for path in paths]
    payload = {
        "schema_version": "compile_surface_invariant_audit_v1",
        "compile_count": len(reports),
        "summary": summarize_reports(reports),
        "reports": reports,
    }
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(render_markdown(payload), encoding="utf-8")
    if not args.out_json and not args.out_md:
        print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def _expand_compile_paths(inputs: list[Path]) -> list[Path]:
    out: list[Path] = []
    for item in inputs:
        if item.is_dir():
            matches = sorted(item.glob("domain_bootstrap_file_*.json"))
            if matches:
                out.append(matches[-1])
                continue
            for fixture_dir in sorted(path for path in item.iterdir() if path.is_dir()):
                fixture_matches = sorted(fixture_dir.glob("domain_bootstrap_file_*.json"))
                if fixture_matches:
                    out.append(fixture_matches[-1])
        elif item.is_file():
            out.append(item)
    return sorted(dict.fromkeys(path.resolve() for path in out))


def audit_compile(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    facts = _facts_from_compile(data)
    source_facts = [fact for fact in facts if _predicate_name(fact).startswith("source_record")]
    direct_facts = [fact for fact in facts if not _predicate_name(fact).startswith("source_record")]
    direct_rows = _fact_rows(direct_facts)
    source_tokens = _tokens_for_facts(source_facts)
    direct_tokens = _tokens_for_facts(direct_facts)
    source_record_tokens = _tokens_for_facts(source_facts)
    direct_predicates = sorted({_predicate_name(fact) for fact in direct_facts if _predicate_name(fact)})
    candidate_predicates = _candidate_predicates(data)
    source_record_promotion = _audit_source_record_promotion(source_facts, direct_facts)

    families = [
        _audit_family(
            spec=spec,
            source_tokens=source_tokens,
            direct_tokens=direct_tokens,
            source_record_tokens=source_record_tokens,
            direct_predicates=direct_predicates,
            candidate_predicates=candidate_predicates,
        )
        for spec in INVARIANTS
    ]
    return {
        "compile_json": str(path),
        "run": path.parent.parent.name if path.parent.parent != path.parent else "",
        "fixture": path.parent.name,
        "parsed_ok": bool(data.get("parsed_ok")),
        "direct_fact_count": len(direct_facts),
        "source_record_fact_count": len(source_facts),
        "candidate_predicate_count": len(candidate_predicates),
        "direct_predicates": direct_predicates,
        "source_record_promotion_telemetry": source_record_promotion,
        "families": families,
        "relation_contracts": [
            *[_audit_relation_contract(spec, direct_rows) for spec in RELATION_CONTRACTS],
            _audit_financial_baseline_derivation_contract(source_facts, direct_rows),
            _audit_quantity_value_delivery_contract(source_facts, direct_rows, candidate_predicates),
            _audit_source_attributed_claim_contract(source_facts, direct_rows),
            _audit_participant_statement_status_contract(source_facts, direct_rows),
            _audit_status_state_scope_contract(source_facts, direct_rows),
            _audit_vague_wrapper_backbone_contract(source_facts, direct_rows, families),
            _audit_repeated_record_detail_delivery_contract(source_facts, direct_rows),
        ],
        "summary": _summarize_families(families),
    }


def _facts_from_compile(data: dict[str, Any]) -> list[str]:
    source_compile = data.get("source_compile") if isinstance(data.get("source_compile"), dict) else {}
    facts = source_compile.get("facts")
    if isinstance(facts, list):
        return [str(fact).strip() for fact in facts if str(fact).strip()]
    parsed = data.get("parsed") if isinstance(data.get("parsed"), dict) else {}
    parsed_facts = parsed.get("facts")
    if isinstance(parsed_facts, list):
        return [str(fact).strip() for fact in parsed_facts if str(fact).strip()]
    return []


def _audit_source_record_promotion(source_facts: list[str], direct_facts: list[str]) -> dict[str, Any]:
    direct_text = "\n".join(direct_facts).casefold()
    direct_tokens = _tokens_for_facts(direct_facts)
    candidates: list[dict[str, Any]] = []
    for fact in source_facts:
        row = _source_record_candidate_from_fact(fact)
        if row is None:
            continue
        tokens = _promotable_tokens(row["value"])
        if not tokens:
            continue
        marker_hits = sorted(tokens & PROMOTABLE_SOURCE_RECORD_MARKERS)
        looks_like_identifier = _looks_like_identifier_tokens(tokens)
        looks_like_list = len([token for token in tokens if token.isdigit()]) >= 3
        if not marker_hits and not looks_like_identifier and not looks_like_list:
            continue
        covered = sorted(tokens & direct_tokens)
        coverage_ratio = round(len(covered) / len(tokens), 4) if tokens else 0.0
        value_in_direct = str(row["value"]).casefold() in direct_text
        stranded = not value_in_direct and coverage_ratio < 0.5
        candidates.append(
            {
                **row,
                "marker_hits": marker_hits,
                "token_count": len(tokens),
                "covered_token_count": len(covered),
                "coverage_ratio": coverage_ratio,
                "value_in_direct": value_in_direct,
                "stranded": stranded,
            }
        )
    stranded_rows = [row for row in candidates if row["stranded"]]
    return {
        "schema_version": "source_record_promotion_telemetry_v1",
        "candidate_count": len(candidates),
        "stranded_count": len(stranded_rows),
        "top_stranded": stranded_rows[:20],
    }


def _source_record_candidate_from_fact(fact: str) -> dict[str, Any] | None:
    predicate = _predicate_name(fact)
    args = _split_fact_args(FACT_RE.match(fact).group(2)) if FACT_RE.match(fact) else []
    if predicate == "source_record_label" and len(args) >= 2:
        return {"predicate": predicate, "source_ref": args[0], "value": _clean_source_record_value(args[1])}
    if predicate in {"source_record_field", "source_record_inline_field"} and len(args) >= 3:
        value = f"{_clean_source_record_value(args[1])}_{_clean_source_record_value(args[2])}"
        return {"predicate": predicate, "source_ref": args[0], "value": value}
    if predicate == "source_record_cell" and len(args) >= 3:
        return {"predicate": predicate, "source_ref": args[0], "value": _clean_source_record_value(args[2])}
    return None


def _clean_source_record_value(value: str) -> str:
    return str(value).strip().strip("'\"")


def _promotable_tokens(value: str) -> set[str]:
    return {
        token
        for token in TOKEN_RE.findall(str(value).casefold())
        if token not in SOURCE_RECORD_STOP_TOKENS
    }


def _looks_like_identifier_tokens(tokens: set[str]) -> bool:
    if not tokens:
        return False
    has_alpha = any(re.search(r"[a-z]", token) for token in tokens)
    has_digit = any(re.search(r"\d", token) for token in tokens)
    return has_alpha and has_digit


def _candidate_predicates(data: dict[str, Any]) -> list[str]:
    parsed = data.get("parsed") if isinstance(data.get("parsed"), dict) else {}
    rows = parsed.get("candidate_predicates")
    out: list[str] = []
    if not isinstance(rows, list):
        return out
    for row in rows:
        if isinstance(row, dict):
            name = str(row.get("name") or row.get("predicate") or row.get("signature") or "").strip()
        else:
            name = str(row).strip()
        if name:
            out.append(name)
    return sorted(set(out))


def _audit_family(
    *,
    spec: InvariantSpec,
    source_tokens: set[str],
    direct_tokens: set[str],
    source_record_tokens: set[str],
    direct_predicates: list[str],
    candidate_predicates: list[str],
) -> dict[str, Any]:
    triggered: dict[str, list[str]] = {}
    covered: dict[str, list[str]] = {}
    ledger_only: dict[str, list[str]] = {}
    candidate_only: dict[str, list[str]] = {}
    predicate_token_text = " ".join(direct_predicates).lower()
    candidate_token_text = " ".join(candidate_predicates).lower()
    for group, terms in spec.groups.items():
        trigger_hits = [term for term in terms if term in source_tokens]
        if not trigger_hits:
            continue
        triggered[group] = trigger_hits
        direct_hits = [term for term in terms if term in direct_tokens or term in predicate_token_text]
        if direct_hits:
            covered[group] = direct_hits
            continue
        candidate_hits = [term for term in terms if term in candidate_token_text]
        if candidate_hits:
            candidate_only[group] = candidate_hits
            continue
        ledger_hits = [term for term in terms if term in source_record_tokens]
        if ledger_hits:
            ledger_only[group] = ledger_hits
    missing = sorted(set(triggered) - set(covered))
    if not triggered:
        status = "not_applicable"
    elif not missing:
        status = "pass"
    elif covered:
        status = "partial"
    elif candidate_only:
        status = "candidate_only"
    elif ledger_only:
        status = "ledger_only"
    else:
        status = "fail"
    return {
        "family": spec.family,
        "description": spec.description,
        "status": status,
        "triggered_groups": triggered,
        "covered_groups": covered,
        "candidate_only_groups": candidate_only,
        "ledger_only_groups": ledger_only,
        "missing_groups": missing,
    }


def summarize_reports(reports: list[dict[str, Any]]) -> dict[str, Any]:
    status_counts: dict[str, int] = {}
    family_status_counts: dict[str, dict[str, int]] = {}
    promotion_candidate_count = 0
    promotion_stranded_count = 0
    for report in reports:
        telemetry = report.get("source_record_promotion_telemetry")
        if isinstance(telemetry, dict):
            promotion_candidate_count += int(telemetry.get("candidate_count") or 0)
            promotion_stranded_count += int(telemetry.get("stranded_count") or 0)
        for family in report["families"]:
            status = str(family["status"])
            status_counts[status] = status_counts.get(status, 0) + 1
            bucket = family_status_counts.setdefault(str(family["family"]), {})
            bucket[status] = bucket.get(status, 0) + 1
    return {
        "status_counts": dict(sorted(status_counts.items())),
        "family_status_counts": {key: dict(sorted(value.items())) for key, value in sorted(family_status_counts.items())},
        "source_record_promotion_candidate_count": promotion_candidate_count,
        "source_record_promotion_stranded_count": promotion_stranded_count,
    }


def _summarize_families(families: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for family in families:
        status = str(family["status"])
        counts[status] = counts.get(status, 0) + 1
    return dict(sorted(counts.items()))


def _predicate_name(fact: str) -> str:
    match = FACT_RE.match(str(fact))
    return match.group(1) if match else ""


def _fact_rows(facts: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for fact in facts:
        match = FACT_RE.match(fact)
        if not match:
            continue
        rows.append({"predicate": match.group(1), "args": _split_fact_args(match.group(2))})
    return rows


def _split_fact_args(raw_args: str) -> list[str]:
    args: list[str] = []
    current: list[str] = []
    in_quote = False
    escape = False
    depth = 0
    for char in raw_args:
        if escape:
            current.append(char)
            escape = False
            continue
        if char == "\\":
            current.append(char)
            escape = True
            continue
        if char == '"':
            current.append(char)
            in_quote = not in_quote
            continue
        if not in_quote and char == "(":
            depth += 1
        elif not in_quote and char == ")" and depth:
            depth -= 1
        if char == "," and not in_quote and depth == 0:
            args.append("".join(current).strip())
            current = []
            continue
        current.append(char)
    if current or raw_args.strip():
        args.append("".join(current).strip())
    return args


def _audit_relation_contract(spec: RelationContractSpec, rows: list[dict[str, Any]]) -> dict[str, Any]:
    required_keys = {
        _key_for_indexes(row["args"], spec.required_key_indexes)
        for row in rows
        if row["predicate"] == spec.required_predicate and _has_indexes(row["args"], spec.required_key_indexes)
    }
    companion_keys = {
        _key_for_indexes(row["args"], spec.companion_key_indexes)
        for row in rows
        if row["predicate"] == spec.companion_predicate and _has_indexes(row["args"], spec.companion_key_indexes)
    }
    required_keys.discard(())
    companion_keys.discard(())
    missing_keys = sorted(required_keys - companion_keys)
    if not required_keys and not companion_keys:
        status = "not_applicable"
    elif not required_keys:
        status = "companion_only"
    elif not missing_keys:
        status = "pass"
    elif companion_keys:
        status = "partial"
    else:
        status = "missing_companion"
    return {
        "contract": spec.contract,
        "description": spec.description,
        "status": status,
        "required_predicate": spec.required_predicate,
        "companion_predicate": spec.companion_predicate,
        "required_key_count": len(required_keys),
        "companion_key_count": len(companion_keys),
        "missing_keys": missing_keys,
    }


def _audit_financial_baseline_derivation_contract(
    source_facts: list[str],
    direct_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    """Check that arithmetic state changes are slot-bound, not just mentioned.

    The token family can tell us that balance, adjustment, result, and policy
    words all appeared somewhere. This contract asks whether the admitted
    structural rows keep a derivation surface with a baseline/previous value,
    adjustment, resulting value, scenario or basis, and constraint.
    """

    source_tokens = _tokens_for_facts(source_facts)
    trigger_groups = {
        "financial_state": {"balance", "reserve", "fund", "value"},
        "adjustment": {"adjustment", "debit", "credit", "expenditure", "appropriation", "subtraction", "addition"},
        "result": {"result", "resulting", "remaining", "new", "final", "post", "reduce", "reduced"},
    }
    triggered = {
        name: sorted(tokens & source_tokens)
        for name, tokens in trigger_groups.items()
        if tokens & source_tokens
    }
    if set(triggered) != set(trigger_groups):
        return {
            "contract": "financial_baseline_derivation_contract",
            "description": "numeric-state changes should bind baseline, adjustment, result, scenario or basis, and constraint in structural rows",
            "status": "not_applicable",
            "required_key_count": 0,
            "companion_key_count": 0,
            "missing_keys": [],
            "triggered_groups": triggered,
            "covered_slots": {},
        }

    structural_rows = [
        row
        for row in direct_rows
        if _is_financial_structural_row(row) and row["predicate"] not in {"source_recorded_assertion"}
    ]
    structural_parts: list[str] = []
    for row in structural_rows:
        structural_parts.append(str(row["predicate"]))
        structural_parts.extend(str(arg) for arg in row["args"])
    structural_text = " ".join(structural_parts).lower()
    structural_tokens = set(TOKEN_RE.findall(structural_text))

    covered_slots: dict[str, list[str]] = {}
    slot_terms = {
        "baseline_or_previous_value": ("baseline", "starting", "initial", "current", "previous", "prior", "balance"),
        "adjustment_value": ("adjustment", "adjustments", "debit", "credit", "expenditure", "appropriation", "subtraction", "addition"),
        "resulting_value": ("result", "resulting", "remaining", "new", "final", "post", "balance"),
        "scenario_or_basis": ("actual", "hypothetical", "counterfactual", "scenario", "assumption", "if", "would", "basis", "after", "before"),
        "constraint_or_threshold": ("constraint", "threshold", "minimum", "maximum", "limit", "policy", "requirement"),
    }
    for slot, terms in slot_terms.items():
        hits = [term for term in terms if term in structural_tokens]
        if hits:
            covered_slots[slot] = hits

    missing_slots = sorted(set(slot_terms) - set(covered_slots))
    if not structural_rows:
        status = "missing_structural_surface"
    elif not missing_slots:
        status = "pass"
    elif covered_slots:
        status = "partial"
    else:
        status = "fail"
    return {
        "contract": "financial_baseline_derivation_contract",
        "description": "numeric-state changes should bind baseline, adjustment, result, scenario or basis, and constraint in structural rows",
        "status": status,
        "required_key_count": len(slot_terms),
        "companion_key_count": len(covered_slots),
        "missing_keys": missing_slots,
        "triggered_groups": triggered,
        "covered_slots": covered_slots,
        "structural_row_count": len(structural_rows),
        "structural_predicates": sorted({str(row["predicate"]) for row in structural_rows}),
    }


def _is_financial_structural_row(row: dict[str, Any]) -> bool:
    text = " ".join([str(row["predicate"]), *[str(arg) for arg in row["args"]]]).lower()
    tokens = set(TOKEN_RE.findall(text))
    financial_terms = {"fund", "balance", "reserve", "financial", "fiscal", "amount", "value"}
    arithmetic_terms = {
        "derivation",
        "transaction",
        "adjustment",
        "expenditure",
        "appropriation",
        "threshold",
        "constraint",
        "minimum",
        "maximum",
        "policy",
        "scenario",
        "assumption",
    }
    predicate = str(row["predicate"])
    return bool((financial_terms & tokens) or (arithmetic_terms & tokens) or "balance" in predicate)


def _audit_quantity_value_delivery_contract(
    source_facts: list[str],
    direct_rows: list[dict[str, Any]],
    candidate_predicates: list[str],
) -> dict[str, Any]:
    """Detect stranded numeric value surfaces in source-record text.

    The profile-admission audit can tell us whether the proposed predicate
    palette has a suitable quantity-bearing shape. This compile-side contract
    asks the next question: did any admitted non-source row actually bind the
    stated value to a subject and measure/unit, or did the value remain only in
    source-record text or broad prose wrappers?
    """

    source_rows = _source_record_text_rows(source_facts)
    source_mentions = _quantity_value_source_mentions(source_rows)
    complete_rows = [row for row in direct_rows if _is_direct_quantity_value_row(row)]
    candidate_carriers = sorted(
        signature for signature in candidate_predicates if _candidate_signature_can_carry_quantity_value(signature)
    )
    wrapper_rows = [row for row in direct_rows if _is_vague_wrapper_row(row)]
    direct_predicates = sorted({str(row["predicate"]) for row in complete_rows})
    wrapper_predicates = sorted({str(row["predicate"]) for row in wrapper_rows})

    if not source_mentions:
        status = "not_applicable"
    elif complete_rows:
        status = "pass"
    elif candidate_carriers:
        status = "quantity_palette_offered_but_undelivered"
    elif wrapper_rows:
        status = "shallow_quantity_value_delivery"
    else:
        status = "missing_quantity_value_delivery"

    missing = [] if complete_rows else [row["excerpt"] for row in source_mentions[:12]]
    return {
        "contract": "quantity_value_delivery_contract",
        "description": "source-stated counts, quantities, rates, durations, thresholds, or monetary values should be admitted as direct value rows with subject and measure/unit slots",
        "status": status,
        "required_key_count": len(source_mentions),
        "companion_key_count": len(complete_rows),
        "missing_keys": missing,
        "source_signal_count": len(source_mentions),
        "complete_quantity_row_count": len(complete_rows),
        "candidate_quantity_carriers": candidate_carriers,
        "wrapper_row_count": len(wrapper_rows),
        "direct_predicates": direct_predicates,
        "wrapper_predicates": wrapper_predicates,
        "triggered_groups": {
            "source_signals": [row["groups"] for row in source_mentions[:12]],
        },
    }


def _quantity_value_source_mentions(source_rows: list[str]) -> list[dict[str, Any]]:
    mentions: list[dict[str, Any]] = []
    group_terms = {
        "count_or_total": {
            "count",
            "counts",
            "total",
            "totals",
            "manifest",
            "quantity",
            "quantities",
        },
        "rate_or_amount": {
            "amount",
            "amounts",
            "rate",
            "rates",
            "cost",
            "costs",
            "price",
            "prices",
            "balance",
            "reserve",
            "fund",
            "dollar",
            "dollars",
        },
        "duration_or_threshold": {
            "duration",
            "hour",
            "hours",
            "days",
            "second",
            "seconds",
            "deadline",
            "threshold",
            "limit",
            "minimum",
            "maximum",
        },
        "measurement_or_percent": {
            "measurement",
            "measure",
            "metric",
            "reading",
            "readings",
            "score",
            "percent",
            "percentage",
            "kg",
            "cm",
            "mm",
            "meters",
            "seconds",
        },
    }
    for row in source_rows:
        payload = _strip_source_record_coordinate_prefix(_source_record_payload_text(row)).lower()
        tokens = set(TOKEN_RE.findall(payload))
        groups: dict[str, list[str]] = {}
        for group, terms in group_terms.items():
            hits = sorted(tokens & terms)
            if hits:
                groups[group] = hits
        if groups and _text_has_numeric_value(payload):
            mentions.append(
                {
                    "excerpt": payload[:180],
                    "groups": groups,
                }
            )
    return mentions


def _strip_source_record_coordinate_prefix(text: str) -> str:
    stripped = str(text or "").strip()
    return re.sub(
        r"^(?:heading|labeled_line|anchored_line|paragraph_line|continuation_line|list_row|table_row)\s+\d+[a-z]?\s+",
        "",
        stripped,
        count=1,
        flags=re.IGNORECASE,
    )


def _candidate_signature_can_carry_quantity_value(signature: str) -> bool:
    name, _, arity_text = str(signature or "").strip().lower().partition("/")
    try:
        arity = int(arity_text)
    except ValueError:
        arity = 0
    known = {"event_measurement", "event_quantity", "reading_value", "measurement_value", "metric_observation"}
    if name in known:
        return arity >= 3
    quantity_terms = {
        "amount",
        "balance",
        "count",
        "cost",
        "duration",
        "limit",
        "measure",
        "measurement",
        "metric",
        "minimum",
        "maximum",
        "percent",
        "quantity",
        "rate",
        "reading",
        "score",
        "threshold",
        "total",
        "value",
    }
    tokens = set(TOKEN_RE.findall(name))
    return arity >= 2 and bool(tokens & quantity_terms or any(term in name for term in quantity_terms))


def _is_direct_quantity_value_row(row: dict[str, Any]) -> bool:
    predicate = str(row.get("predicate") or "").lower()
    if predicate.startswith("source_record") or _is_vague_wrapper_row(row):
        return False
    args = [str(arg) for arg in row.get("args", [])]
    if len(args) < 2 or not _row_has_numeric_value(row):
        return False
    tokens = _tokens_for_row(row)
    quantity_terms = {
        "amount",
        "balance",
        "count",
        "cost",
        "duration",
        "limit",
        "measure",
        "measurement",
        "metric",
        "minimum",
        "maximum",
        "percent",
        "quantity",
        "rate",
        "reading",
        "score",
        "threshold",
        "total",
        "value",
    }
    known_quantity_predicates = {
        "event_measurement",
        "event_quantity",
        "reading_value",
        "measurement_value",
        "metric_observation",
    }
    if predicate in known_quantity_predicates and len(args) >= 3:
        return True
    predicate_tokens = set(TOKEN_RE.findall(predicate))
    if not (predicate_tokens & quantity_terms or any(term in predicate for term in quantity_terms)):
        return False
    non_value_args = [arg for arg in args if not _text_has_numeric_value(arg)]
    if len(args) == 2 and (predicate_tokens & quantity_terms or any(term in predicate for term in quantity_terms)):
        return len(non_value_args) >= 1
    return len(non_value_args) >= 2


def _row_has_numeric_value(row: dict[str, Any]) -> bool:
    return any(_arg_has_quantity_numeric_value(str(arg)) for arg in row.get("args", []))


def _arg_has_quantity_numeric_value(arg: str) -> bool:
    norm = _normalize_arg(arg)
    if not norm:
        return False
    if norm.startswith(("src_", "source_", "source_line_", "line_")):
        return False
    if re.fullmatch(r"(?:19|20)\d{2}(?:_[01]\d(?:_[0-3]\d(?:_[0-2]\d(?:_[0-5]\d)?)?)?)?", norm):
        return False
    if re.fullmatch(r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*_(?:19|20)\d{2}", norm):
        return False
    return _text_has_numeric_value(norm)


def _text_has_numeric_value(text: str) -> bool:
    lowered = str(text or "").lower()
    tokens = set(TOKEN_RE.findall(lowered))
    return bool(
        re.search(r"\b\d+(?:[._]\d+)?\b", lowered)
        or re.search(
            r"(?:amount|balance|count|cost|duration|hour|hours|days|second|seconds|limit|measure|measurement|metric|minimum|maximum|percent|quantity|rate|reading|score|threshold|total|value|kg|cm|mm|meters)_[0-9]",
            lowered,
        )
        or re.search(
            r"[0-9]_(?:amount|count|cost|hours|days|seconds|kg|cm|mm|meters|percent|score|value)",
            lowered,
        )
        or tokens & NUMBER_WORDS
    )


def _audit_source_attributed_claim_contract(
    source_facts: list[str],
    direct_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    source_rows = _source_record_text_rows(source_facts)
    source_mentions = _source_attribution_mentions(source_rows)
    structural_rows = [row for row in direct_rows if _is_source_attributed_claim_row(row)]
    wrapper_rows = [
        row
        for row in direct_rows
        if str(row.get("predicate") or "").lower() in {"source_recorded_assertion", "source_detail", "answer_detail"}
    ]
    if not source_mentions:
        status = "not_applicable"
    elif structural_rows:
        status = "pass"
    elif wrapper_rows:
        status = "source_reference_wrapper_only"
    else:
        status = "missing_source_reference_surface"
    return {
        "contract": "source_attributed_claim_contract",
        "description": "source-attributed claims should preserve source actor/document, content, and source/scope as direct rows rather than only source-record prose",
        "status": status,
        "required_key_count": len(source_mentions),
        "companion_key_count": len(structural_rows),
        "missing_keys": [] if structural_rows else [row["excerpt"] for row in source_mentions[:12]],
        "source_signal_count": len(source_mentions),
        "structural_row_count": len(structural_rows),
        "structural_predicates": sorted({str(row["predicate"]) for row in structural_rows}),
        "wrapper_predicates": sorted({str(row["predicate"]) for row in wrapper_rows}),
        "triggered_groups": {
            "source_signals": [row["groups"] for row in source_mentions[:12]],
        },
    }


def _source_attribution_mentions(source_rows: list[str]) -> list[dict[str, Any]]:
    mentions: list[dict[str, Any]] = []
    source_terms = {
        "according",
        "attested",
        "claim",
        "claimed",
        "email",
        "letter",
        "memo",
        "memorandum",
        "note",
        "opinion",
        "per",
        "report",
        "reported",
        "says",
        "source",
        "statement",
        "states",
        "stated",
        "testimony",
    }
    content_terms = {
        "active",
        "authority",
        "available",
        "binding",
        "confirmed",
        "determined",
        "finding",
        "not",
        "open",
        "pending",
        "resolved",
        "status",
        "supports",
        "unresolved",
    }
    for row in source_rows:
        payload = _strip_source_record_coordinate_prefix(_source_record_payload_text(row)).lower()
        tokens = set(TOKEN_RE.findall(payload))
        source_hits = sorted(tokens & source_terms)
        content_hits = sorted(tokens & content_terms)
        if source_hits and content_hits:
            mentions.append(
                {
                    "excerpt": payload[:180],
                    "groups": {
                        "source_or_speech_cue": source_hits,
                        "claim_content_cue": content_hits,
                    },
                }
            )
    return mentions


def _is_source_attributed_claim_row(row: dict[str, Any]) -> bool:
    predicate = str(row.get("predicate") or "").lower()
    args = [str(arg) for arg in row.get("args", [])]
    if predicate.startswith("source_record") or len(args) < 3:
        return False
    if predicate in {
        "participant_statement",
        "witness_statement",
        "legal_opinion",
        "source_authority",
        "source_attributed_claim",
        "source_detail",
        "statement_detail",
    }:
        return True
    tokens = _tokens_for_row(row)
    predicate_tokens = set(TOKEN_RE.findall(predicate))
    source_tokens = {
        "claim",
        "email",
        "letter",
        "memo",
        "memorandum",
        "note",
        "opinion",
        "report",
        "source",
        "statement",
        "testimony",
        "witness",
    }
    content_tokens = {"authority", "content", "detail", "finding", "status", "support", "topic"}
    return bool(predicate_tokens & source_tokens and (tokens & content_tokens or len(args) >= 4))


def _audit_participant_statement_status_contract(
    source_facts: list[str],
    direct_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    source_tokens = _tokens_for_facts(source_facts)
    speech_tokens = {
        "statement",
        "comment",
        "advice",
        "opinion",
        "estimate",
        "certification",
        "clarification",
        "caveat",
        "observation",
        "said",
        "stated",
        "suggested",
        "asked",
    }
    status_tokens = {"binding", "advisory", "nonbinding", "informational", "opinion", "not", "false", "true"}
    triggered = {
        "speech_surface": sorted(speech_tokens & source_tokens),
        "binding_status": sorted(status_tokens & source_tokens),
    }
    if not triggered["speech_surface"] or not triggered["binding_status"]:
        return {
            "contract": "participant_statement_status_contract",
            "description": "statement/advice/comment/estimate rows should expose binding or advisory status on the row or a same-anchor companion",
            "status": "not_applicable",
            "required_key_count": 0,
            "companion_key_count": 0,
            "missing_keys": [],
            "triggered_groups": triggered,
            "covered_keys": [],
        }

    statement_rows = [row for row in direct_rows if _is_statement_structural_row(row)]
    status_rows = [row for row in direct_rows if _is_statement_status_row(row)]
    status_anchors = {
        _normalize_arg(arg)
        for row in status_rows
        for arg in row["args"][:2]
        if str(arg).strip()
    }
    missing: list[str] = []
    covered: list[str] = []
    for index, row in enumerate(statement_rows, start=1):
        row_tokens = _tokens_for_row(row)
        anchors = {_normalize_arg(arg) for arg in row["args"][:2] if str(arg).strip()}
        key = f"{row['predicate']}[{index}]"
        if row_tokens & status_tokens:
            covered.append(key)
            continue
        if anchors & status_anchors:
            covered.append(key)
            continue
        missing.append(key)

    if not statement_rows:
        status = "missing_structural_surface"
    elif not missing:
        status = "pass"
    elif covered:
        status = "partial"
    else:
        status = "missing_status_companion"
    return {
        "contract": "participant_statement_status_contract",
        "description": "statement/advice/comment/estimate rows should expose binding or advisory status on the row or a same-anchor companion",
        "status": status,
        "required_key_count": len(statement_rows),
        "companion_key_count": len(covered),
        "missing_keys": missing,
        "triggered_groups": triggered,
        "covered_keys": covered,
        "statement_predicates": sorted({str(row["predicate"]) for row in statement_rows}),
        "status_predicates": sorted({str(row["predicate"]) for row in status_rows}),
    }


def _audit_status_state_scope_contract(
    source_facts: list[str],
    direct_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    """Require status/state rows to keep subject, value, and scope together.

    Status words alone are too cheap: the native pressure rows ask for state at
    a date, current condition, pending resolution, supersession, or scoped
    subset state. This contract watches for source rows with those signals and
    checks whether direct status-like rows preserve a queryable subject, state
    value, and temporal/source/current scope on the same row or stable anchor.
    """

    source_rows = _source_record_text_rows(source_facts)
    status_source_rows = [row for row in source_rows if _is_status_state_source_row(row)]
    triggered_groups = _status_state_trigger_groups(status_source_rows)
    if not status_source_rows or not triggered_groups.get("state_or_status_value"):
        return {
            "contract": "status_state_scope_contract",
            "description": "status/state surfaces should bind subject, state value, and temporal/source/current scope",
            "status": "not_applicable",
            "required_key_count": 0,
            "companion_key_count": 0,
            "missing_keys": [],
            "triggered_groups": triggered_groups,
            "status_row_count": 0,
            "complete_status_row_count": 0,
            "status_predicates": [],
        }

    status_rows = [row for row in direct_rows if _is_status_state_structural_row(row)]
    complete: list[str] = []
    shallow: list[str] = []
    for index, row in enumerate(status_rows, start=1):
        slots = _status_state_slots(row)
        key = f"{row['predicate']}[{index}]"
        if {"subject", "state_value", "temporal_or_source_scope"} <= slots:
            complete.append(key)
        else:
            missing = sorted({"subject", "state_value", "temporal_or_source_scope"} - slots)
            shallow.append(f"{key}:{','.join(missing)}")

    source_row_count = len(status_source_rows)
    complete_ratio = len(complete) / source_row_count if source_row_count else 0.0
    if complete and not shallow:
        status = "pass"
    elif complete:
        status = "partial"
    elif status_rows:
        status = "shallow_status_state_surface"
    else:
        status = "missing_status_state_surface"
    return {
        "contract": "status_state_scope_contract",
        "description": "status/state surfaces should bind subject, state value, and temporal/source/current scope",
        "status": status,
        "required_key_count": source_row_count,
        "companion_key_count": len(complete),
        "missing_keys": shallow[:20],
        "triggered_groups": triggered_groups,
        "status_row_count": len(status_rows),
        "complete_status_row_count": len(complete),
        "complete_status_row_ratio": round(complete_ratio, 4),
        "status_predicates": sorted({str(row["predicate"]) for row in status_rows}),
    }


def _audit_vague_wrapper_backbone_contract(
    source_facts: list[str],
    direct_rows: list[dict[str, Any]],
    families: list[dict[str, Any]],
) -> dict[str, Any]:
    """Flag generic detail/event wrappers when event backbone slots are thin.

    This is a quality gate, not an extraction repair. Generic wrappers may be
    useful as additive residue, but they should not be the only surface when the
    source has event identity, time, participant/system, subject, and outcome
    coordinates.
    """

    source_tokens = _tokens_for_facts(source_facts)
    trigger_terms = {
        "event_identity": {"event", "entry", "record", "incident", "log"},
        "temporal_anchor": {"timestamp", "time", "date", "dated", "chronological", "order"},
        "participant_or_system": {"actor", "operator", "system", "party", "participant", "originated"},
        "subject_or_object": {"subject", "object", "item", "sample", "request", "proposal", "debt"},
        "outcome_or_state": {"status", "outcome", "result", "state", "settled", "void", "issued"},
    }
    triggered_groups = {
        name: sorted(tokens & source_tokens)
        for name, tokens in trigger_terms.items()
        if tokens & source_tokens
    }
    backbone = next((row for row in families if row.get("family") == "event_backbone_unit_surface"), {})
    backbone_status = str(backbone.get("status") or "")
    wrapper_rows = [row for row in direct_rows if _is_vague_wrapper_row(row)]
    wrapper_predicates = sorted({str(row["predicate"]) for row in wrapper_rows})

    if len(triggered_groups) < 3:
        status = "not_applicable"
    elif backbone_status == "pass":
        status = "pass"
    elif wrapper_rows:
        status = "vague_wrapper_without_backbone"
    else:
        status = "missing_backbone_surface"

    return {
        "contract": "vague_wrapper_backbone_contract",
        "description": "generic detail/event wrappers must not substitute for event identity, temporal, participant/system, subject, and outcome backbone rows",
        "status": status,
        "required_key_count": len(trigger_terms) if len(triggered_groups) >= 3 else 0,
        "companion_key_count": len(triggered_groups),
        "missing_keys": list(backbone.get("missing_groups") or []),
        "triggered_groups": triggered_groups,
        "event_backbone_status": backbone_status,
        "wrapper_row_count": len(wrapper_rows),
        "wrapper_predicates": wrapper_predicates,
    }


def _audit_repeated_record_detail_delivery_contract(
    source_facts: list[str],
    direct_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    """Check that repeated record ledgers keep anchor-level detail rows.

    This is the fixture-free version of the Dulse pressure: if the source has
    repeated source-owned records and those records mention actions, transfers,
    status, consequences, or required returns, the compile should not preserve
    only the rule/status wrapper. Each record anchor should remain joinable to
    the participants, item/value detail, and outcome/consequence rows that make
    later questions answerable without rereading prose.
    """

    source_rows = _source_record_text_rows(source_facts)
    source_anchor_signals = _source_record_anchor_signals(source_rows)
    source_anchors = set(source_anchor_signals)
    source_tokens = _tokens_for_facts(source_facts)
    transfer_signal = source_tokens & {
        "trade",
        "traded",
        "transfer",
        "transferred",
        "provided",
        "return",
        "returned",
        "received",
        "sold",
        "bought",
        "paid",
        "issued",
    }
    outcome_signal = source_tokens & {
        "void",
        "invalid",
        "violation",
        "violated",
        "status",
        "flagged",
        "disputed",
        "unresolved",
        "settled",
        "consequence",
        "penalty",
        "must",
        "owed",
    }
    triggered_groups = {
        "record_anchors": sorted(source_anchors)[:20],
        "transfer_or_action_terms": sorted(transfer_signal),
        "outcome_or_consequence_terms": sorted(outcome_signal),
    }
    actionable_anchors = set(source_anchors)
    if len(actionable_anchors) < 3 or not (transfer_signal or outcome_signal):
        return {
            "contract": "repeated_record_detail_delivery_contract",
            "description": "repeated source-owned records should preserve per-record participant, item/value, and status/consequence detail surfaces",
            "status": "not_applicable",
            "required_key_count": 0,
            "companion_key_count": 0,
            "missing_keys": [],
            "triggered_groups": triggered_groups,
            "record_anchor_count": len(actionable_anchors),
            "complete_anchor_count": 0,
            "partial_anchor_count": 0,
            "direct_anchor_count": 0,
            "direct_predicates": [],
        }

    direct_anchors = _direct_anchor_slots(direct_rows)
    complete: list[str] = []
    partial: list[str] = []
    missing: list[str] = []
    for anchor in sorted(actionable_anchors):
        slots = direct_anchors.get(anchor, set())
        required_slots = {"record_identity"}
        if transfer_signal:
            required_slots.add("participant")
            required_slots.add("item_or_value")
        elif outcome_signal:
            required_slots.add("status_or_consequence")
        if required_slots <= slots:
            complete.append(anchor)
        elif slots:
            partial.append(f"{anchor}:{','.join(sorted(required_slots - slots))}")
        else:
            missing.append(anchor)

    complete_ratio = (len(complete) / len(actionable_anchors)) if actionable_anchors else 0.0
    if complete and (not partial and not missing):
        status = "pass"
    elif complete_ratio >= 0.65:
        status = "pass_sparse_tail"
    elif complete:
        status = "partial"
    elif partial:
        status = "shallow_record_detail_delivery"
    else:
        status = "missing_record_detail_delivery"

    return {
        "contract": "repeated_record_detail_delivery_contract",
        "description": "repeated source-owned records should preserve per-record participant, item/value, and status/consequence detail surfaces",
        "status": status,
        "required_key_count": len(actionable_anchors),
        "companion_key_count": len(complete),
        "missing_keys": [*partial[:20], *missing[:20]],
        "triggered_groups": triggered_groups,
        "record_anchor_count": len(actionable_anchors),
        "complete_anchor_count": len(complete),
        "partial_anchor_count": len(partial),
        "complete_anchor_ratio": round(complete_ratio, 4),
        "direct_anchor_count": len(direct_anchors),
        "direct_predicates": sorted({str(row["predicate"]) for row in direct_rows if _row_record_anchors(row)}),
    }


def _source_record_text_rows(source_facts: list[str]) -> list[str]:
    rows: list[str] = []
    for fact in source_facts:
        predicate = _predicate_name(fact)
        if predicate not in {"source_record_text_atom", "source_record_label", "source_record_row"}:
            continue
        rows.append(str(fact).lower())
    return rows


def _source_record_anchors(source_rows: list[str]) -> set[str]:
    anchors: set[str] = set()
    for row in source_rows:
        for match in re.finditer(
            r"(?:^|[^a-z0-9])(?P<prefix>entry|record|case|item|filing|transaction|trade|event)[_\s-]+(?P<id>[0-9]+[a-z]?)",
            row,
        ):
            anchors.add(f"{match.group('prefix')}_{match.group('id')}")
    return anchors


def _source_record_anchor_signals(source_rows: list[str]) -> dict[str, set[str]]:
    signals: dict[str, set[str]] = {}
    for row in source_rows:
        row_anchors = _source_record_anchors([row])
        if not row_anchors:
            continue
        row_tokens = set(TOKEN_RE.findall(row.lower()))
        for anchor in row_anchors:
            signals.setdefault(anchor, set()).update(row_tokens)
    return signals


def _direct_anchor_slots(direct_rows: list[dict[str, Any]]) -> dict[str, set[str]]:
    anchors: dict[str, set[str]] = {}
    for row in direct_rows:
        row_anchors = _row_record_anchors(row)
        if not row_anchors:
            continue
        slots = _record_detail_slots(row)
        for anchor in row_anchors:
            anchors.setdefault(anchor, set()).update(slots)
    return anchors


def _row_record_anchors(row: dict[str, Any]) -> set[str]:
    anchors: set[str] = set()
    for raw in row.get("args", []):
        value = _normalize_arg(str(raw))
        if re.match(r"^(entry|record|case|item|filing|transaction|trade|event)_[a-z0-9_-]*[0-9][a-z0-9_-]*$", value):
            anchors.add(value)
    return anchors


def _record_detail_slots(row: dict[str, Any]) -> set[str]:
    predicate = str(row.get("predicate") or "").lower()
    tokens = _tokens_for_row(row)
    slots: set[str] = set()
    if tokens & {"entry", "record", "ledger", "log", "register", "transaction", "trade"} or any(
        marker in predicate for marker in ("entry", "record", "ledger", "transaction", "trade")
    ):
        slots.add("record_identity")
    if tokens & {"participant", "party", "actor", "seller", "buyer", "trader", "witness", "from", "to", "recipient", "giver"} or any(
        marker in predicate for marker in ("participant", "party", "actor", "seller", "buyer", "trader", "witness")
    ):
        slots.add("participant")
    if tokens & {"item", "good", "goods", "amount", "quantity", "unit", "value", "measure", "measures", "bars", "count"} or any(
        marker in predicate for marker in ("item", "good", "amount", "quantity", "value")
    ):
        slots.add("item_or_value")
    if tokens & {
        "status",
        "void",
        "invalid",
        "violation",
        "flagged",
        "disputed",
        "unresolved",
        "settled",
        "consequence",
        "penalty",
        "return",
        "returned",
        "obligation",
    } or any(marker in predicate for marker in ("status", "consequence", "penalty", "violation", "void", "return")):
        slots.add("status_or_consequence")
    return slots


def _is_vague_wrapper_row(row: dict[str, Any]) -> bool:
    predicate = str(row.get("predicate") or "").lower()
    if predicate in {
        "answer_detail",
        "detail",
        "event",
        "event_description",
        "event_detail",
        "record_detail",
        "source_detail",
        "source_recorded_assertion",
    }:
        return True
    return False


def _is_statement_structural_row(row: dict[str, Any]) -> bool:
    if _is_statement_status_row(row):
        return False
    tokens = _tokens_for_row(row)
    predicate = str(row["predicate"]).lower()
    if predicate.startswith(("rule_", "policy_", "charter_")):
        return False
    if any(marker in predicate for marker in ("translation", "language", "original_text", "statement_original")):
        return False
    return bool(
        tokens
        & {
            "statement",
            "comment",
            "opinion",
            "estimate",
            "certification",
            "clarification",
            "caveat",
            "observation",
            "advice",
        }
        or any(marker in predicate for marker in ("comment", "opinion", "estimate", "certification", "statement"))
    )


def _is_statement_status_row(row: dict[str, Any]) -> bool:
    predicate = str(row["predicate"]).lower()
    tokens = _tokens_for_row(row)
    return bool(
        "binding" in predicate
        or "status" in predicate
        or "epistemic" in predicate
        or ({"binding", "advisory", "nonbinding", "informational"} & tokens)
    )


def _status_state_trigger_groups(source_rows: list[str]) -> dict[str, list[str]]:
    groups: dict[str, set[str]] = {}
    for row in source_rows:
        tokens = set(TOKEN_RE.findall(_source_record_payload_text(row).lower()))
        for group, terms in {
            "subject_or_population": {
                "application",
                "case",
                "document",
                "item",
                "lot",
                "permit",
                "population",
                "record",
                "request",
                "sample",
                "subject",
            },
            "state_or_status_value": {
                "active",
                "approved",
                "available",
                "cleared",
                "condition",
                "current",
                "denied",
                "failed",
                "hold",
                "pending",
                "resolved",
                "state",
                "status",
                "suspect",
            },
            "temporal_or_source_scope": {
                "as",
                "at",
                "current",
                "date",
                "dated",
                "effective",
                "final",
                "initial",
                "on",
                "source",
                "time",
            },
            "transition_or_resolution": {
                "after",
                "before",
                "changed",
                "from",
                "not",
                "reclassified",
                "replaced",
                "superseded",
                "to",
                "voided",
            },
        }.items():
            hits = tokens & terms
            if hits:
                groups.setdefault(group, set()).update(hits)
    return {group: sorted(values) for group, values in sorted(groups.items())}


def _status_state_source_tokens(source_row: str) -> set[str]:
    groups = _status_state_trigger_groups([source_row])
    return set(groups)


def _is_status_state_source_row(source_row: str) -> bool:
    groups = _status_state_source_tokens(source_row)
    if "state_or_status_value" not in groups:
        return False
    if "subject_or_population" not in groups:
        return False
    return bool(groups & {"temporal_or_source_scope", "transition_or_resolution"})


def _is_status_state_structural_row(row: dict[str, Any]) -> bool:
    predicate = str(row.get("predicate") or "").lower()
    predicate_tokens = set(TOKEN_RE.findall(predicate))
    if predicate.startswith("source_record"):
        return False
    if _is_statement_status_row(row) and not any(
        marker in predicate for marker in ("record", "case", "application", "item", "lot", "sample", "permit", "status_at")
    ):
        return False
    predicate_markers = {
        "active",
        "approved",
        "available",
        "availability",
        "cleared",
        "current",
        "denied",
        "failed",
        "hold",
        "pending",
        "phase",
        "resolved",
        "state",
        "status",
        "suspect",
        "suspended",
        "unresolved",
        "voided",
    }
    condition_context = "condition" in predicate_tokens and bool(predicate_tokens & {"current", "state", "status"})
    return bool(
        predicate.endswith(("_status_at", "_state_at", "_condition_at", "_status_on", "_state_on"))
        or bool(predicate_tokens & predicate_markers)
        or condition_context
    )


def _status_state_slots(row: dict[str, Any]) -> set[str]:
    predicate = str(row.get("predicate") or "").lower()
    args = [str(arg) for arg in row.get("args", [])]
    tokens = _tokens_for_row(row)
    slots: set[str] = set()
    state_terms = {
        "active",
        "approved",
        "available",
        "cleared",
        "closed",
        "condition",
        "current",
        "denied",
        "failed",
        "hold",
        "pending",
        "resolved",
        "settled",
        "state",
        "status",
        "suspect",
        "suspended",
        "unresolved",
        "void",
        "voided",
    }
    if args:
        slots.add("subject")
    if tokens & state_terms or any(marker in predicate for marker in ("status", "state", "condition", "phase")):
        slots.add("state_value")
    if (
        predicate.endswith(("_status_at", "_state_at", "_condition_at", "_status_on", "_state_on"))
        or len(args) >= 3
        or any(_looks_temporal_or_source_scope(arg) for arg in args)
        or tokens & {"as", "at", "current", "date", "dated", "effective", "final", "initial", "source", "time"}
    ):
        slots.add("temporal_or_source_scope")
    if tokens & {"after", "before", "changed", "from", "reclassified", "replaced", "superseded", "to", "voided"}:
        slots.add("transition")
    return slots


def _looks_temporal_or_source_scope(value: str) -> bool:
    norm = _normalize_arg(value)
    return bool(
        re.search(r"(?:^|_)(?:20\d{2}|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|current|final|initial|source|src|line)(?:_|$)", norm)
    )


def _source_record_payload_text(fact: str) -> str:
    match = FACT_RE.match(str(fact))
    if not match:
        return str(fact)
    args = _split_fact_args(match.group(2))
    if len(args) <= 1:
        return " ".join(args)
    return " ".join(args[1:])


def _tokens_for_row(row: dict[str, Any]) -> set[str]:
    return set(TOKEN_RE.findall(" ".join([str(row["predicate"]), *[str(arg) for arg in row["args"]]]).lower()))


def _has_indexes(args: list[str], indexes: tuple[int, ...]) -> bool:
    return all(index < len(args) for index in indexes)


def _key_for_indexes(args: list[str], indexes: tuple[int, ...]) -> tuple[str, ...]:
    if not _has_indexes(args, indexes):
        return ()
    return tuple(_normalize_arg(args[index]) for index in indexes)


def _normalize_arg(value: str) -> str:
    return value.strip().strip('"').strip("'").lower()


def _tokens_for_facts(facts: list[str]) -> set[str]:
    return set(TOKEN_RE.findall(" ".join(facts).lower()))


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Compile Surface Invariant Audit",
        "",
        f"- Schema: `{payload['schema_version']}`",
        f"- Compiles: `{payload['compile_count']}`",
        f"- Status counts: `{payload['summary']['status_counts']}`",
        f"- Source-record promotion candidates: `{payload['summary'].get('source_record_promotion_candidate_count', 0)}`",
        f"- Source-record promotion stranded candidates: `{payload['summary'].get('source_record_promotion_stranded_count', 0)}`",
        "",
        "## Fixture Summary",
        "",
        "| Run | Fixture | Direct facts | Source-record facts | Pass | Partial | Candidate-only | Ledger-only | Fail | N/A |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for report in payload["reports"]:
        summary = report["summary"]
        lines.append(
            "| {run} | {fixture} | {direct} | {source} | {pass_} | {partial} | {candidate} | {ledger} | {fail} | {na} |".format(
                run=f"`{report['run']}`",
                fixture=f"`{report['fixture']}`",
                direct=report["direct_fact_count"],
                source=report["source_record_fact_count"],
                pass_=summary.get("pass", 0),
                partial=summary.get("partial", 0),
                candidate=summary.get("candidate_only", 0),
                ledger=summary.get("ledger_only", 0),
                fail=summary.get("fail", 0),
                na=summary.get("not_applicable", 0),
            )
        )
    lines.extend(["", "## Missing Or Weak Families", ""])
    for report in payload["reports"]:
        weak = [row for row in report["families"] if row["status"] not in {"pass", "not_applicable"}]
        weak_contracts = [
            row for row in report.get("relation_contracts", []) if row["status"] not in {"pass", "not_applicable"}
        ]
        if not weak and not weak_contracts:
            continue
        lines.append(f"### `{report['run']}` / `{report['fixture']}`")
        lines.append("")
        for family in weak:
            lines.append(
                f"- `{family['family']}`: `{family['status']}`; missing `{family['missing_groups']}`"
            )
        for contract in weak_contracts:
            lines.append(
                f"- `{contract['contract']}`: `{contract['status']}`; missing keys `{contract['missing_keys']}`"
            )
        telemetry = report.get("source_record_promotion_telemetry")
        if isinstance(telemetry, dict) and int(telemetry.get("stranded_count") or 0):
            lines.append(
                f"- `source_record_promotion_telemetry`: `stranded`; candidates `{telemetry.get('candidate_count', 0)}`, stranded `{telemetry.get('stranded_count', 0)}`"
            )
        lines.append("")
    stranded = [
        (report, row)
        for report in payload["reports"]
        for row in (
            report.get("source_record_promotion_telemetry", {}).get("top_stranded", [])
            if isinstance(report.get("source_record_promotion_telemetry"), dict)
            else []
        )
    ]
    if stranded:
        lines.extend(
            [
                "## Source-Record Promotion Telemetry",
                "",
                "| Run | Fixture | Predicate | Source Ref | Coverage | Value |",
                "| --- | --- | --- | --- | ---: | --- |",
            ]
        )
        for report, row in stranded[:40]:
            value = str(row.get("value") or "").replace("|", "\\|")
            if len(value) > 120:
                value = value[:117] + "..."
            lines.append(
                f"| `{report['run']}` | `{report['fixture']}` | `{row.get('predicate', '')}` | `{row.get('source_ref', '')}` | {row.get('coverage_ratio', 0)} | `{value}` |"
            )
    return "\n".join(lines).rstrip() + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
