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
            out.extend(sorted(item.glob("*/domain_bootstrap_file_*.json")))
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
        "families": families,
        "relation_contracts": [_audit_relation_contract(spec, direct_rows) for spec in RELATION_CONTRACTS],
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
    for report in reports:
        for family in report["families"]:
            status = str(family["status"])
            status_counts[status] = status_counts.get(status, 0) + 1
            bucket = family_status_counts.setdefault(str(family["family"]), {})
            bucket[status] = bucket.get(status, 0) + 1
    return {
        "status_counts": dict(sorted(status_counts.items())),
        "family_status_counts": {key: dict(sorted(value.items())) for key, value in sorted(family_status_counts.items())},
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
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
