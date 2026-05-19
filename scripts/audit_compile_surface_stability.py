#!/usr/bin/env python3
"""Compare compile draws for direct-surface stability.

This audit is intentionally post-hoc. It does not merge facts or repair a
compile. It asks whether multiple draws of the same source preserve the same
direct predicate palette and direct fact rows.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


FACT_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\((.*)\)\.\s*$")
SURFACE_GROUPS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("assignment_binding_surface", ("assigned", "assignment")),
    ("task_scope_surface", ("task", "review", "inspection", "testing", "verification")),
    ("status_phase_surface", ("status", "phase", "pending", "closed", "complete")),
    ("identity_role_surface", ("person", "role", "name", "actor")),
    ("object_record_surface", ("record", "ticket", "docket", "file", "packet", "equipment", "sample")),
    ("completion_transition_surface", ("completed", "closed", "finished", "moved", "transition")),
)
PALETTE_DELIVERY_REPEATED_MIN = 3
PALETTE_DELIVERY_COLLAPSE_RATIO = 0.55
QUANTITY_EVENT_CARRIER_PREDICATES = {
    "event_measurement",
    "event_quantity",
    "measurement_value",
    "metric_observation",
    "reading_value",
}
QUANTITY_EVENT_WRAPPER_PREDICATES = {
    "event_description",
    "event_detail",
    "event_note",
    "source_detail",
}
NUMBER_RE = re.compile(r"(?:^|[_\W])\d+(?:[._]\d+)?(?:[_\W]|$)")
QUANTITY_TERM_RE = re.compile(
    r"(?:^|[_\W])(?:kg|min|minute|hour|day|days|k|kw|percent|ratio|rate|threshold|setpoint|value|duration|offset|score|reading|acre|acres|sq_ft|foot|feet|unit|units|count|amount|humidity|temperature)(?:[_\W]|$)",
    re.IGNORECASE,
)
SOURCE_LOCATOR_RE = re.compile(r"^(?:src|source)?_?line_?\d+$|^l\d+$|^line_?\d+$", re.IGNORECASE)
EVENT_WRAPPER_CONTEXT_RE = re.compile(
    r"(?:^|_)(?:event|events|log|logs|reading|readings|measurement|measurements|metric|metrics)(?:_|$)",
    re.IGNORECASE,
)
QUANTITY_FIELD_CONTEXT_RE = re.compile(
    r"(?:^|_)(?:quantity|measure|measurement|metric|reading|rate|setpoint|threshold|duration|offset|score|count|amount|value)(?:_|$)",
    re.IGNORECASE,
)
DATE_TIME_FIELD_RE = re.compile(r"(?:^|_)(?:date|time|timestamp|year|month|day)(?:_|$)", re.IGNORECASE)
QUANTITY_EVENT_ISSUE_STATUSES = {"not_offered", "offered_not_delivered", "partially_delivered"}


def audit_paths(paths: list[Path]) -> dict[str, Any]:
    expanded = _expand_compile_paths(paths)
    draws_by_fixture: dict[str, list[dict[str, Any]]] = {}
    for path in expanded:
        draw = _load_draw(path)
        draws_by_fixture.setdefault(draw["fixture"], []).append(draw)

    fixtures = []
    for fixture, draws in sorted(draws_by_fixture.items()):
        fixtures.append(_audit_fixture(fixture, draws))

    return {
        "schema_version": "compile_surface_stability_audit_v1",
        "compile_count": len(expanded),
        "fixture_count": len(fixtures),
        "summary": _summarize(fixtures),
        "fixtures": fixtures,
    }


def _expand_compile_paths(inputs: list[Path]) -> list[Path]:
    out: list[Path] = []
    for item in inputs:
        if item.is_file():
            out.append(item)
            continue
        if not item.is_dir():
            continue
        direct = sorted(item.glob("domain_bootstrap_file_*.json"))
        if direct:
            out.append(direct[-1])
            continue
        out.extend(sorted(item.glob("*/domain_bootstrap_file_*.json")))
    return sorted(dict.fromkeys(path.resolve() for path in out))


def _load_draw(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    parsed = payload.get("parsed") if isinstance(payload.get("parsed"), dict) else {}
    facts = _facts_from_compile(payload)
    direct_facts = sorted(fact for fact in facts if not _predicate_name(fact).startswith("source_record"))
    source_facts = sorted(fact for fact in facts if _predicate_name(fact).startswith("source_record"))
    direct_rows = _fact_rows(direct_facts)
    source_rows = _fact_rows(source_facts)
    source_texts = _source_text_atoms(source_facts)
    predicate_counts: dict[str, int] = {}
    for fact in direct_facts:
        predicate = _predicate_name(fact)
        if predicate:
            predicate_counts[predicate] = predicate_counts.get(predicate, 0) + 1
    signature_counts = _fact_signature_counts(direct_rows)
    candidate_signatures = _candidate_signatures(parsed)
    return {
        "compile_json": str(path),
        "fixture": path.parent.name,
        "run": path.parent.parent.name,
        "parsed_ok": bool(payload.get("parsed_ok")),
        "candidate_signatures": candidate_signatures,
        "direct_fact_count": len(direct_facts),
        "direct_predicate_count": len(predicate_counts),
        "direct_facts": direct_facts,
        "predicate_counts": dict(sorted(predicate_counts.items())),
        "signature_counts": signature_counts,
        "candidate_zero_yield_signatures": sorted(
            signature for signature in candidate_signatures if int(signature_counts.get(signature, 0)) == 0
        ),
        "surface_counts": _surface_counts(direct_facts),
        "delivery_telemetry": _delivery_telemetry(candidate_signatures=candidate_signatures, direct_rows=direct_rows),
        "profile_delivery_findings": _profile_delivery_findings(payload),
        "contracts": _contract_reports(source_texts=source_texts, source_rows=source_rows, direct_rows=direct_rows),
    }


def _facts_from_compile(payload: dict[str, Any]) -> list[str]:
    source_compile = payload.get("source_compile") if isinstance(payload.get("source_compile"), dict) else {}
    facts = source_compile.get("facts")
    if isinstance(facts, list):
        return [str(fact).strip() for fact in facts if str(fact).strip()]
    parsed = payload.get("parsed") if isinstance(payload.get("parsed"), dict) else {}
    parsed_facts = parsed.get("facts")
    if isinstance(parsed_facts, list):
        return [str(fact).strip() for fact in parsed_facts if str(fact).strip()]
    return []


def _audit_fixture(fixture: str, draws: list[dict[str, Any]]) -> dict[str, Any]:
    palette_sets = [set(draw["candidate_signatures"]) for draw in draws]
    palette_union = set().union(*palette_sets) if palette_sets else set()
    palette_common = set.intersection(*palette_sets) if palette_sets else set()
    palette_unstable = sorted(palette_union - palette_common)
    palette_churn_ratio = (len(palette_unstable) / len(palette_union)) if palette_union else 0.0
    predicate_arity_drift = _predicate_arity_drift(palette_union)
    signature_names = sorted({name for draw in draws for name in draw["signature_counts"]})
    signature_delivery_drift = []
    for signature in signature_names:
        counts = [int(draw["signature_counts"].get(signature, 0)) for draw in draws]
        if len(set(counts)) <= 1:
            continue
        signature_delivery_drift.append(
            {
                "signature": signature,
                "counts": counts,
                "min": min(counts),
                "max": max(counts),
                "delta": max(counts) - min(counts),
            }
        )
    candidate_zero_yield_union = sorted(
        {
            signature
            for draw in draws
            for signature in draw.get("candidate_zero_yield_signatures", [])
        }
    )
    palette_delivery_contracts = _palette_delivery_contracts(draws)
    delivery_telemetry = _fixture_delivery_telemetry(draws)
    profile_delivery_telemetry = _fixture_profile_delivery_telemetry(draws)
    fact_sets = [set(draw["direct_facts"]) for draw in draws]
    union_facts = set().union(*fact_sets) if fact_sets else set()
    common_facts = set.intersection(*fact_sets) if fact_sets else set()
    unstable_facts = sorted(union_facts - common_facts)
    predicate_names = sorted({name for draw in draws for name in draw["predicate_counts"]})
    predicate_drift = []
    for predicate in predicate_names:
        counts = [int(draw["predicate_counts"].get(predicate, 0)) for draw in draws]
        if len(set(counts)) <= 1:
            continue
        predicate_drift.append(
            {
                "predicate": predicate,
                "counts": counts,
                "min": min(counts),
                "max": max(counts),
                "delta": max(counts) - min(counts),
            }
        )
    surface_names = sorted({name for draw in draws for name in draw["surface_counts"]})
    surface_drift = []
    for surface in surface_names:
        counts = [int(draw["surface_counts"].get(surface, 0)) for draw in draws]
        if len(set(counts)) <= 1:
            continue
        surface_drift.append(
            {
                "surface": surface,
                "counts": counts,
                "min": min(counts),
                "max": max(counts),
                "delta": max(counts) - min(counts),
            }
        )
    missing_by_draw = []
    for draw, fact_set in zip(draws, fact_sets):
        missing = sorted(union_facts - fact_set)
        missing_by_draw.append(
            {
                "compile_json": draw["compile_json"],
                "run": draw["run"],
                "missing_union_fact_count": len(missing),
                "missing_union_facts": missing[:25],
            }
        )
    return {
        "fixture": fixture,
        "draw_count": len(draws),
        "palette_stable": not palette_unstable and not predicate_arity_drift,
        "palette_union_count": len(palette_union),
        "palette_common_count": len(palette_common),
        "palette_unstable_count": len(palette_unstable),
        "palette_churn_ratio": round(palette_churn_ratio, 4),
        "unstable_candidate_signatures": palette_unstable,
        "predicate_arity_drift": predicate_arity_drift,
        "signature_delivery_drift": signature_delivery_drift,
        "candidate_zero_yield_signature_count": len(candidate_zero_yield_union),
        "candidate_zero_yield_signatures": candidate_zero_yield_union,
        "palette_delivery_contracts": palette_delivery_contracts,
        "delivery_telemetry": delivery_telemetry,
        "profile_delivery_telemetry": profile_delivery_telemetry,
        "stable": not unstable_facts,
        "union_fact_count": len(union_facts),
        "common_fact_count": len(common_facts),
        "unstable_fact_count": len(unstable_facts),
        "predicate_drift": predicate_drift,
        "surface_drift": surface_drift,
        "draws": [
            {
                "compile_json": draw["compile_json"],
                "run": draw["run"],
                "parsed_ok": draw["parsed_ok"],
                "candidate_signature_count": len(draw["candidate_signatures"]),
                "candidate_signatures": draw["candidate_signatures"],
                "missing_palette_union_count": len(sorted(palette_union - set(draw["candidate_signatures"]))),
                "missing_palette_union_signatures": sorted(palette_union - set(draw["candidate_signatures"]))[:25],
                "candidate_zero_yield_signature_count": len(draw["candidate_zero_yield_signatures"]),
                "candidate_zero_yield_signatures": draw["candidate_zero_yield_signatures"][:25],
                "direct_fact_count": draw["direct_fact_count"],
                "direct_predicate_count": draw["direct_predicate_count"],
                "direct_signature_count": len(draw["signature_counts"]),
                "surface_counts": draw["surface_counts"],
                "delivery_telemetry": draw["delivery_telemetry"],
                "profile_delivery_findings": draw["profile_delivery_findings"],
                "contracts": draw["contracts"],
            }
            for draw in draws
        ],
        "missing_by_draw": missing_by_draw,
    }


def _summarize(fixtures: list[dict[str, Any]]) -> dict[str, Any]:
    unstable = [fixture for fixture in fixtures if not fixture["stable"]]
    palette_unstable = [fixture for fixture in fixtures if not fixture.get("palette_stable")]
    quantity_delivery = [
        row
        for fixture in fixtures
        for row in fixture.get("delivery_telemetry", [])
        if isinstance(row, dict) and row.get("kind") == "quantity_event_delivery"
    ]
    return {
        "stable_fixture_count": len(fixtures) - len(unstable),
        "unstable_fixture_count": len(unstable),
        "palette_stable_fixture_count": len(fixtures) - len(palette_unstable),
        "palette_unstable_fixture_count": len(palette_unstable),
        "palette_unstable_signature_count": sum(int(fixture.get("palette_unstable_count", 0)) for fixture in fixtures),
        "predicate_arity_drift_count": sum(len(fixture.get("predicate_arity_drift", [])) for fixture in fixtures),
        "signature_delivery_drift_count": sum(len(fixture.get("signature_delivery_drift", [])) for fixture in fixtures),
        "candidate_zero_yield_signature_count": sum(
            int(fixture.get("candidate_zero_yield_signature_count", 0)) for fixture in fixtures
        ),
        "palette_delivery_contract_count": sum(len(fixture.get("palette_delivery_contracts", [])) for fixture in fixtures),
        "profile_delivery_issue_count": sum(len(fixture.get("profile_delivery_telemetry", [])) for fixture in fixtures),
        "quantity_event_delivery_issue_count": sum(
            1 for row in quantity_delivery if row.get("status") in QUANTITY_EVENT_ISSUE_STATUSES
        ),
        "unstable_fact_count": sum(int(fixture["unstable_fact_count"]) for fixture in fixtures),
        "predicate_drift_count": sum(len(fixture["predicate_drift"]) for fixture in fixtures),
        "surface_drift_count": sum(len(fixture["surface_drift"]) for fixture in fixtures),
    }


def _candidate_signatures(parsed: dict[str, Any]) -> list[str]:
    rows = parsed.get("candidate_predicates")
    if not isinstance(rows, list):
        return []
    out: list[str] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        signature = str(row.get("signature") or "").strip()
        if not signature:
            name = str(row.get("name") or row.get("predicate") or "").strip()
            args = row.get("args", [])
            if name and isinstance(args, list):
                signature = f"{name}/{len(args)}"
        if signature:
            out.append(signature)
    return sorted(dict.fromkeys(out))


def _predicate_arity_drift(signatures: set[str]) -> list[dict[str, Any]]:
    by_name: dict[str, set[int]] = {}
    for signature in signatures:
        name, arity = _split_signature(signature)
        if not name or arity is None:
            continue
        by_name.setdefault(name, set()).add(arity)
    return [
        {"predicate": name, "arities": sorted(arities)}
        for name, arities in sorted(by_name.items())
        if len(arities) > 1
    ]


def _split_signature(signature: str) -> tuple[str, int | None]:
    raw = str(signature or "").strip()
    match = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_]*)/(\d+)", raw)
    if not match:
        return raw.split("/", 1)[0], None
    return match.group(1), int(match.group(2))


def _fact_signature_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        predicate = str(row.get("predicate", "")).strip()
        args = row.get("args", [])
        if not predicate or not isinstance(args, list):
            continue
        signature = f"{predicate}/{len(args)}"
        counts[signature] = counts.get(signature, 0) + 1
    return dict(sorted(counts.items()))


def _palette_delivery_contracts(draws: list[dict[str, Any]]) -> list[dict[str, Any]]:
    palette_union = sorted({signature for draw in draws for signature in draw["candidate_signatures"]})
    contracts: list[dict[str, Any]] = []
    for signature in palette_union:
        counts = [int(draw["signature_counts"].get(signature, 0)) for draw in draws]
        max_count = max(counts) if counts else 0
        if max_count < PALETTE_DELIVERY_REPEATED_MIN:
            continue
        name, _arity = _split_signature(signature)
        draw_rows = []
        statuses = []
        for draw, count in zip(draws, counts):
            candidate_set = set(draw["candidate_signatures"])
            same_name_alternates = sorted(
                candidate
                for candidate in candidate_set
                if candidate != signature and _split_signature(candidate)[0] == name
            )
            status = _palette_delivery_status(
                count=count,
                max_count=max_count,
                candidate_present=signature in candidate_set,
                same_name_alternates=same_name_alternates,
            )
            statuses.append(status)
            draw_rows.append(
                {
                    "run": draw["run"],
                    "compile_json": draw["compile_json"],
                    "candidate_present": signature in candidate_set,
                    "row_count": count,
                    "status": status,
                    "same_name_alternates": same_name_alternates,
                }
            )
        if all(status == "healthy" for status in statuses):
            continue
        contracts.append(
            {
                "signature": signature,
                "max_row_count": max_count,
                "classification_counts": _count_statuses(statuses),
                "draws": draw_rows,
            }
        )
    return contracts


def _palette_delivery_status(
    *,
    count: int,
    max_count: int,
    candidate_present: bool,
    same_name_alternates: list[str],
) -> str:
    if count > 0 and count >= max(1, int(max_count * PALETTE_DELIVERY_COLLAPSE_RATIO)):
        return "healthy"
    if same_name_alternates:
        return "arity_drift"
    if candidate_present and count == 0:
        return "zero_yield"
    return "delivery_collapse"


def _delivery_telemetry(*, candidate_signatures: list[str], direct_rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "quantity_event_delivery": _quantity_event_delivery_telemetry(
            candidate_signatures=candidate_signatures,
            direct_rows=direct_rows,
        )
    }


def _profile_delivery_findings(payload: dict[str, Any]) -> list[dict[str, Any]]:
    source_compile = payload.get("source_compile", {}) if isinstance(payload.get("source_compile"), dict) else {}
    delivery = source_compile.get("profile_delivery", {}) if isinstance(source_compile.get("profile_delivery"), dict) else {}
    findings = delivery.get("findings", []) if isinstance(delivery.get("findings"), list) else []
    out: list[dict[str, Any]] = []
    for finding in findings:
        if not isinstance(finding, dict):
            continue
        cls = str(finding.get("class") or "").strip()
        if not cls:
            continue
        offered = [
            str(item).strip()
            for item in finding.get("offered_carriers", [])
            if str(item).strip()
        ] if isinstance(finding.get("offered_carriers"), list) else []
        out.append(
            {
                "class": cls,
                "source_signal_count": int(finding.get("source_signal_count") or 0),
                "offered_carriers": offered,
            }
        )
    return out


def _fixture_profile_delivery_telemetry(draws: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_class: dict[str, list[dict[str, Any]]] = {}
    for draw in draws:
        findings = draw.get("profile_delivery_findings", [])
        if not isinstance(findings, list):
            continue
        for finding in findings:
            if not isinstance(finding, dict):
                continue
            cls = str(finding.get("class") or "").strip()
            if cls:
                by_class.setdefault(cls, []).append({"draw": draw, "finding": finding})
    rows: list[dict[str, Any]] = []
    for cls, items in sorted(by_class.items()):
        rows.append(
            {
                "kind": "profile_delivery",
                "class": cls,
                "affected_draw_count": len(items),
                "draw_count": len(draws),
                "source_signal_counts": [
                    int(item["finding"].get("source_signal_count") or 0)
                    for item in items
                ],
                "offered_carriers": sorted(
                    {
                        str(carrier)
                        for item in items
                        for carrier in item["finding"].get("offered_carriers", [])
                        if str(carrier).strip()
                    }
                ),
                "draws": [
                    {
                        "run": item["draw"]["run"],
                        "compile_json": item["draw"]["compile_json"],
                        "source_signal_count": int(item["finding"].get("source_signal_count") or 0),
                        "offered_carriers": item["finding"].get("offered_carriers", []),
                    }
                    for item in items
                ],
            }
        )
    return rows


def _fixture_delivery_telemetry(draws: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    quantity_rows = []
    for draw in draws:
        item = draw.get("delivery_telemetry", {}).get("quantity_event_delivery")
        if isinstance(item, dict):
            quantity_rows.append(item)
    if quantity_rows:
        statuses = [str(item.get("delivery_status", "")) for item in quantity_rows]
        rows.append(
            {
                "kind": "quantity_event_delivery",
                "status": _aggregate_quantity_delivery_status(statuses),
                "status_counts": _count_statuses(statuses),
                "carrier_offered_counts": [int(item.get("carrier_offered_count", 0) or 0) for item in quantity_rows],
                "carrier_row_counts": [int(item.get("carrier_row_count", 0) or 0) for item in quantity_rows],
                "numeric_wrapper_counts": [int(item.get("numeric_wrapper_count", 0) or 0) for item in quantity_rows],
                "stranded_numeric_wrapper_counts": [
                    int(item.get("stranded_numeric_wrapper_count", 0) or 0) for item in quantity_rows
                ],
                "draws": quantity_rows,
            }
        )
    return rows


def _aggregate_quantity_delivery_status(statuses: list[str]) -> str:
    meaningful = [status for status in statuses if status and status != "not_applicable"]
    if not meaningful:
        return "not_applicable"
    if all(status == "delivered" for status in meaningful):
        return "delivered"
    if any(status == "offered_not_delivered" for status in meaningful):
        return "offered_not_delivered"
    if any(status == "partially_delivered" for status in meaningful):
        return "partially_delivered"
    if any(status == "not_offered" for status in meaningful):
        return "not_offered"
    return "mixed"


def _quantity_event_delivery_telemetry(
    *,
    candidate_signatures: list[str],
    direct_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    carrier_signatures = [
        signature
        for signature in candidate_signatures
        if _split_signature(signature)[0] in QUANTITY_EVENT_CARRIER_PREDICATES
    ]
    carrier_rows = [
        row
        for row in direct_rows
        if str(row.get("predicate", "")).strip() in QUANTITY_EVENT_CARRIER_PREDICATES
    ]
    carrier_subjects = {
        str((row.get("args") or [""])[0]).strip()
        for row in carrier_rows
        if isinstance(row.get("args"), list) and row.get("args")
    }
    numeric_wrappers = [
        row
        for row in direct_rows
        if _is_numeric_event_wrapper(row)
    ]
    stranded_wrappers = [
        row
        for row in numeric_wrappers
        if not _wrapper_subject_has_quantity_carrier(row, carrier_subjects)
    ]
    if not numeric_wrappers:
        status = "not_applicable"
    elif not carrier_signatures:
        status = "not_offered"
    elif carrier_signatures and numeric_wrappers and not carrier_rows:
        status = "offered_not_delivered"
    elif stranded_wrappers:
        status = "partially_delivered"
    else:
        status = "delivered"
    return {
        "kind": "quantity_event_delivery",
        "delivery_status": status,
        "carrier_offered_count": len(carrier_signatures),
        "carrier_offered_signatures": carrier_signatures,
        "carrier_row_count": len(carrier_rows),
        "numeric_wrapper_count": len(numeric_wrappers),
        "stranded_numeric_wrapper_count": len(stranded_wrappers),
        "sample_numeric_wrappers": [_row_to_fact_like(row) for row in numeric_wrappers[:6]],
        "sample_stranded_numeric_wrappers": [_row_to_fact_like(row) for row in stranded_wrappers[:6]],
    }


def _is_numeric_event_wrapper(row: dict[str, Any]) -> bool:
    predicate = str(row.get("predicate", "")).strip()
    args = row.get("args") if isinstance(row.get("args"), list) else []
    if predicate not in QUANTITY_EVENT_WRAPPER_PREDICATES:
        return False
    text = " ".join(_quantity_content_args(predicate, args))
    if predicate == "source_detail":
        return bool(NUMBER_RE.search(text) and _source_detail_has_quantity_event_context(args, text))
    return bool(NUMBER_RE.search(text) and QUANTITY_TERM_RE.search(text))


def _source_detail_has_quantity_event_context(args: list[Any], text: str) -> bool:
    values = [str(arg).strip() for arg in args]
    if len(values) < 3:
        return False
    subject = values[0]
    field = values[1]
    if DATE_TIME_FIELD_RE.search(field):
        return False
    has_event_context = bool(EVENT_WRAPPER_CONTEXT_RE.search(subject) or EVENT_WRAPPER_CONTEXT_RE.search(field))
    has_quantity_context = bool(QUANTITY_FIELD_CONTEXT_RE.search(field) or QUANTITY_TERM_RE.search(text))
    return (has_event_context or has_quantity_context) and has_quantity_context


def _quantity_content_args(predicate: str, args: list[Any]) -> list[str]:
    values = [str(arg).strip() for arg in args]
    if predicate == "source_detail" and len(values) >= 3:
        values = values[2:]
    elif len(values) >= 2:
        values = values[1:]
    return [value for value in values if value and not SOURCE_LOCATOR_RE.fullmatch(value)]


def _wrapper_subject_has_quantity_carrier(row: dict[str, Any], carrier_subjects: set[str]) -> bool:
    args = row.get("args") if isinstance(row.get("args"), list) else []
    return bool(args and str(args[0]).strip() in carrier_subjects)


def _row_to_fact_like(row: dict[str, Any]) -> str:
    predicate = str(row.get("predicate", "")).strip()
    args = row.get("args") if isinstance(row.get("args"), list) else []
    return f"{predicate}({', '.join(str(arg) for arg in args)})."


def _count_statuses(statuses: list[str]) -> dict[str, int]:
    out: dict[str, int] = {}
    for status in statuses:
        out[status] = out.get(status, 0) + 1
    return dict(sorted(out.items()))


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
    depth = 0
    for char in raw_args:
        if char == "," and depth == 0:
            args.append("".join(current).strip())
            current = []
            continue
        if char in "([":
            depth += 1
        elif char in ")]" and depth > 0:
            depth -= 1
        current.append(char)
    if current:
        args.append("".join(current).strip())
    return args


def _source_text_atoms(source_facts: list[str]) -> list[str]:
    texts: list[str] = []
    for row in _fact_rows(source_facts):
        if row["predicate"] != "source_record_text_atom" or len(row["args"]) < 2:
            continue
        texts.append(str(row["args"][1]).strip().lower())
    return texts


def _contract_reports(
    *, source_texts: list[str], source_rows: list[dict[str, Any]], direct_rows: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    return [
        _parallel_assignment_contract(source_texts=source_texts, direct_rows=direct_rows),
        _source_authority_pair_contract(source_texts=source_texts, source_rows=source_rows, direct_rows=direct_rows),
        _operational_lifecycle_contract(source_texts=source_texts, direct_rows=direct_rows),
    ]


def _parallel_assignment_contract(*, source_texts: list[str], direct_rows: list[dict[str, Any]]) -> dict[str, Any]:
    source_mentions = [
        text
        for text in source_texts
        if ("assigned_to" in text or "was_assigned" in text or "assigned_" in text)
        and any(marker in text for marker in ("task", "review", "inspection", "testing", "verification", "scope"))
    ]
    direct_rows_found = [
        row
        for row in direct_rows
        if row["predicate"]
        in {
            "assigned_to",
            "record_assigned_to",
            "task_assigned",
            "task_assigned_to",
            "assignment_event",
            "assignment_scope",
        }
    ]
    return _contract_status(
        contract="parallel_assignment_event_preservation",
        source_signal_count=len(source_mentions),
        direct_surface_count=len(direct_rows_found),
        required_when_source_count_at_least=2,
    )


def _source_authority_pair_contract(
    *, source_texts: list[str], source_rows: list[dict[str, Any]], direct_rows: list[dict[str, Any]]
) -> dict[str, Any]:
    source_mentions = [
        text
        for text in source_texts
        if any(marker in text for marker in ("authority", "authorized", "authoriz", "court_order", "policy", "governing"))
        and any(marker in text for marker in ("access", "finding", "status", "action", "subject", "item", "party"))
    ]
    source_units = _source_authority_source_units(source_rows)
    complete_units, partial_units = _source_authority_direct_units(direct_rows)
    return _contract_status(
        contract="source_authority_pair_preservation",
        source_signal_count=len(source_units) or len(source_mentions),
        direct_surface_count=len(complete_units),
        required_when_source_count_at_least=1,
        extra={
            "source_field_unit_count": len(source_units),
            "source_text_mention_count": len(source_mentions),
            "direct_complete_count": len(complete_units),
            "direct_partial_count": len(partial_units),
        },
    )


def _source_authority_source_units(source_rows: list[dict[str, Any]]) -> set[tuple[str, str]]:
    fields_by_record: dict[str, dict[str, set[str]]] = {}
    for row in source_rows:
        if row["predicate"] != "source_record_field" or len(row["args"]) < 3:
            continue
        record, field, value = (str(row["args"][0]), str(row["args"][1]).lower(), str(row["args"][2]).lower())
        fields_by_record.setdefault(record, {}).setdefault(field, set()).add(value)

    source_units: set[tuple[str, str]] = set()
    for record, fields in fields_by_record.items():
        subject_values = _field_values(fields, ("subject", "item", "object", "record", "entity", "case", "file"))
        actor_values = _field_values(fields, ("authorized", "authorised", "party", "access", "recipient", "actor", "holder"))
        source_values = _field_values(fields, ("source", "authority", "authorizing", "authorising", "governing", "basis", "rule", "policy", "order"))
        if not subject_values or not actor_values or not source_values:
            continue
        if all(_negative_source_value(value) for value in actor_values | source_values):
            continue
        for subject in subject_values:
            source_units.add((record, subject))
    return source_units


def _field_values(fields: dict[str, set[str]], markers: tuple[str, ...]) -> set[str]:
    values: set[str] = set()
    for field, field_values in fields.items():
        if any(marker in field for marker in markers):
            values.update(value for value in field_values if value)
    return values


def _negative_source_value(value: str) -> bool:
    return any(marker in value for marker in ("no_", "none", "not_applicable", "n_a"))


def _source_authority_direct_units(direct_rows: list[dict[str, Any]]) -> tuple[set[tuple[str, ...]], set[tuple[str, ...]]]:
    by_predicate: dict[str, list[list[str]]] = {}
    for row in direct_rows:
        by_predicate.setdefault(str(row.get("predicate") or ""), []).append([str(arg).strip() for arg in row.get("args", [])])

    complete: set[tuple[str, ...]] = set()
    partial: set[tuple[str, ...]] = set()

    authorized_keys = {
        (args[0], args[1])
        for args in by_predicate.get("access_authorized_to", [])
        if len(args) >= 3 and args[0] and args[1] and args[2]
    }
    authorized_keys.update(
        (args[0], args[1])
        for args in by_predicate.get("authorized_access", [])
        if len(args) >= 3 and args[0] and args[1] and args[2]
    )
    source_keys = {
        (args[0], args[1])
        for args in by_predicate.get("access_source", [])
        if len(args) >= 3 and args[0] and args[1] and args[2]
    }
    source_keys.update(
        (args[0], args[1])
        for args in by_predicate.get("access_authority_source", [])
        if len(args) >= 3 and args[0] and args[1] and args[2]
    )
    for key in sorted(authorized_keys & source_keys):
        complete.add(("access_pair", *key))
    for key in sorted((authorized_keys | source_keys) - (authorized_keys & source_keys)):
        partial.add(("access_pair", *key))

    source_by_subject = {
        args[0]
        for args in by_predicate.get("access_authority_source", [])
        if len(args) == 2 and args[0] and args[1]
    }
    party_by_subject = {
        args[0]
        for args in by_predicate.get("authorized_party", [])
        if len(args) >= 2 and args[0] and args[1]
    }
    for subject in sorted(source_by_subject & party_by_subject):
        complete.add(("packed_access_authority", subject))
    for subject in sorted((source_by_subject | party_by_subject) - (source_by_subject & party_by_subject)):
        partial.add(("packed_access_authority", subject))

    for predicate in (
        "access_authority",
        "publication_authority",
        "legal_title",
        "legal_title_holder",
        "physical_custody",
        "physical_custodian",
        "negative_authority",
        "no_access_for",
    ):
        for args in by_predicate.get(predicate, []):
            if len(args) >= 2 and args[0] and args[1]:
                complete.add((predicate, args[0], args[1]))

    for predicate in (
        "source_authority",
        "authority_source",
        "authorized_by",
        "governing_source",
        "authority_for",
        "source_for_authority",
    ):
        for args in by_predicate.get(predicate, []):
            if len(args) >= 3 and args[0] and args[1] and args[2]:
                complete.add((predicate, args[0], args[1]))
            elif len(args) >= 2 and args[0] and args[1]:
                partial.add((predicate, args[0], args[1]))

    return complete, partial


def _operational_lifecycle_contract(*, source_texts: list[str], direct_rows: list[dict[str, Any]]) -> dict[str, Any]:
    source_mentions = [
        text
        for text in source_texts
        if _is_operational_lifecycle_source_text(text)
    ]
    complete_units, partial_units, split_units = _operational_lifecycle_direct_units(direct_rows)
    return _contract_status(
        contract="operational_lifecycle_preservation",
        source_signal_count=len(source_mentions),
        direct_surface_count=len(complete_units),
        required_when_source_count_at_least=2,
        extra={
            "source_text_mention_count": len(source_mentions),
            "direct_complete_count": len(complete_units),
            "direct_partial_count": len(partial_units),
            "direct_split_count": len(split_units),
        },
    )


def _operational_lifecycle_direct_units(
    direct_rows: list[dict[str, Any]],
) -> tuple[set[tuple[str, ...]], set[tuple[str, ...]], set[tuple[str, ...]]]:
    complete: set[tuple[str, ...]] = set()
    partial: set[tuple[str, ...]] = set()
    date_by_subject: dict[str, set[tuple[str, ...]]] = {}
    state_by_subject: dict[str, set[tuple[str, ...]]] = {}
    typed_event_by_subject: dict[str, set[tuple[str, ...]]] = {}
    for index, row in enumerate(direct_rows):
        predicate = str(row.get("predicate") or "").lower()
        args = [str(arg).strip().lower() for arg in row.get("args", [])]
        lifecycle_predicate = _has_lifecycle_marker(predicate)
        date_carrier_predicate = _has_temporal_carrier_marker(predicate)
        typed_event_predicate = _has_typed_event_marker(predicate)
        if not lifecycle_predicate and not date_carrier_predicate and not typed_event_predicate:
            continue
        key = (predicate, str(index), *(args[:3]))
        joined_args = " ".join(args)
        has_temporal = _has_temporal_marker(joined_args)
        has_state = (
            lifecycle_predicate
            and (_has_state_marker(joined_args) or _has_lifecycle_marker(joined_args))
        ) or (typed_event_predicate and len(args) >= 2 and bool(args[1]))
        if len(args) >= 2:
            subject = args[0]
            if subject:
                if has_temporal:
                    date_by_subject.setdefault(subject, set()).add(key)
                if has_state:
                    state_by_subject.setdefault(subject, set()).add(key)
                if typed_event_predicate and bool(args[1]):
                    typed_event_by_subject.setdefault(subject, set()).add(key)
        if lifecycle_predicate and len(args) >= 3 and (has_temporal or has_state):
            complete.add(key)
        elif len(args) >= 2:
            partial.add(key)
    split: set[tuple[str, ...]] = set()
    for subject in sorted(set(date_by_subject) & set(typed_event_by_subject)):
        complete.add(("joined_event_lifecycle_surface", subject))
    for subject in sorted(set(date_by_subject) & set(state_by_subject)):
        if subject not in typed_event_by_subject:
            split.add(("split_lifecycle_surface", subject))
    return complete, partial, split


def _has_lifecycle_marker(text: str) -> bool:
    return _has_token_marker(
        text,
        (
            "status",
            "state",
            "phase",
            "transition",
            "lifecycle",
            "received",
            "filed",
            "approved",
            "denied",
            "withdrawn",
            "closed",
            "reopened",
            "corrected",
            "completed",
        ),
    ) or bool(re.search(r"(?:^|[^a-z0-9])supersed[a-z]*(?:[^a-z0-9]|$)", text.lower()))


def _has_token_marker(text: str, markers: tuple[str, ...]) -> bool:
    normalized = str(text).lower().replace("-", "_")
    return any(
        re.search(rf"(?:^|[^a-z0-9]){re.escape(marker)}(?:[^a-z0-9]|$)", normalized)
        for marker in markers
    )


def _is_operational_lifecycle_source_text(text: str) -> bool:
    text = str(text).casefold()
    if not _has_lifecycle_marker(text) or not _has_temporal_marker(text) or _negated_lifecycle_source_text(text):
        return False
    if _is_temporal_or_metric_correction_text(text):
        return False
    if _is_storage_or_window_boundary_text(text):
        return False
    if _is_schedule_or_deadline_text(text):
        return False
    if _is_static_status_snapshot_text(text):
        return False
    return _has_status_or_record_subject_marker(text)


def _is_temporal_or_metric_correction_text(text: str) -> bool:
    if not any(marker in text for marker in ("corrected", "correction")):
        return False
    return any(
        marker in text
        for marker in (
            "timestamp",
            "wall_clock",
            "clock",
            "time_of",
            "score",
            "rank",
            "reading",
            "measurement",
            "value",
        )
    )


def _is_storage_or_window_boundary_text(text: str) -> bool:
    return any(
        marker in text
        for marker in (
            "originals_are_filed",
            "retained_for_audit",
            "cycle_window",
            "maintenance_window",
            "inspection_window",
            "review_window",
        )
    )


def _is_schedule_or_deadline_text(text: str) -> bool:
    return any(
        marker in text
        for marker in (
            "deadline",
            "due_",
            "_due",
            "hearing",
            "scheduled",
            "calendared",
            "rescheduled",
        )
    )


def _is_static_status_snapshot_text(text: str) -> bool:
    return "status" in text and any(marker in text for marker in ("as_of", "recorded_as", "title_status"))


def _has_status_or_record_subject_marker(text: str) -> bool:
    return any(
        marker in text
        for marker in (
            "status",
            "state",
            "phase",
            "record",
            "case",
            "application",
            "request",
            "permit",
            "proposal",
            "ticket",
            "issue",
            "notice",
            "claim",
            "appeal",
            "docket",
            "filing",
            "form",
            "document",
            "order",
            "finding",
        )
    )


def _negated_lifecycle_source_text(text: str) -> bool:
    return any(
        marker in text
        for marker in (
            "not_received",
            "has_not_received",
            "had_not_received",
            "not_approved",
            "not_completed",
            "not_closed",
        )
    )


def _has_temporal_marker(text: str) -> bool:
    return bool(re.search(r"(?:^|[^0-9])(?:v_)?\d{4}[-_]\d{2}[-_]\d{2}(?:[^0-9]|$)", text))


def _has_temporal_carrier_marker(text: str) -> bool:
    return any(marker in text for marker in ("date", "dated", "timestamp", "time", "turn"))


def _has_typed_event_marker(text: str) -> bool:
    return any(
        marker in text
        for marker in (
            "event_type",
            "event_action",
            "event_status",
            "transition_type",
            "transition_action",
            "lifecycle_action",
        )
    )


def _has_state_marker(text: str) -> bool:
    return any(
        marker in text
        for marker in (
            "pending",
            "approved",
            "denied",
            "withdrawn",
            "closed",
            "reopened",
            "completed",
            "supersed",
        )
    )


def _contract_status(
    *,
    contract: str,
    source_signal_count: int,
    direct_surface_count: int,
    required_when_source_count_at_least: int,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if source_signal_count < required_when_source_count_at_least:
        status = "not_applicable"
    elif direct_surface_count >= source_signal_count:
        status = "pass"
    elif direct_surface_count > 0:
        status = "partial"
    else:
        status = "ledger_only"
    report = {
        "contract": contract,
        "status": status,
        "source_signal_count": source_signal_count,
        "direct_surface_count": direct_surface_count,
    }
    if extra:
        report.update(extra)
    return report


def _surface_counts(facts: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for fact in facts:
        predicate = _predicate_name(fact)
        text = f"{predicate} {fact}".lower()
        for surface, markers in SURFACE_GROUPS:
            if any(marker in text for marker in markers):
                counts[surface] = counts.get(surface, 0) + 1
    return dict(sorted(counts.items()))


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Compile Surface Stability Audit",
        "",
        f"- Compiles: `{report['compile_count']}`",
        f"- Fixtures: `{report['fixture_count']}`",
        f"- Stable fixtures: `{report['summary']['stable_fixture_count']}`",
        f"- Unstable fixtures: `{report['summary']['unstable_fixture_count']}`",
        f"- Palette-stable fixtures: `{report['summary']['palette_stable_fixture_count']}`",
        f"- Palette-unstable fixtures: `{report['summary']['palette_unstable_fixture_count']}`",
        f"- Unstable palette signatures: `{report['summary']['palette_unstable_signature_count']}`",
        f"- Predicate arity drift rows: `{report['summary']['predicate_arity_drift_count']}`",
        f"- Signature delivery drift rows: `{report['summary']['signature_delivery_drift_count']}`",
        f"- Candidate zero-yield signatures: `{report['summary']['candidate_zero_yield_signature_count']}`",
        f"- Palette delivery contract rows: `{report['summary']['palette_delivery_contract_count']}`",
        f"- Profile delivery issue rows: `{report['summary']['profile_delivery_issue_count']}`",
        f"- Quantity-event delivery issues: `{report['summary']['quantity_event_delivery_issue_count']}`",
        f"- Unstable direct facts: `{report['summary']['unstable_fact_count']}`",
        f"- Predicate drift rows: `{report['summary']['predicate_drift_count']}`",
        f"- Surface drift rows: `{report['summary']['surface_drift_count']}`",
        "",
    ]
    for fixture in report["fixtures"]:
        lines.extend(
            [
                f"## `{fixture['fixture']}`",
                "",
                f"- Draws: `{fixture['draw_count']}`",
                f"- Stable: `{fixture['stable']}`",
                f"- Palette stable: `{fixture['palette_stable']}`",
                f"- Common / union palette signatures: `{fixture['palette_common_count']} / {fixture['palette_union_count']}`",
                f"- Unstable palette signatures: `{fixture['palette_unstable_count']}`",
                f"- Palette churn ratio: `{fixture['palette_churn_ratio']}`",
                f"- Signature delivery drift rows: `{len(fixture['signature_delivery_drift'])}`",
                f"- Candidate zero-yield signatures: `{fixture['candidate_zero_yield_signature_count']}`",
                f"- Palette delivery contract rows: `{len(fixture['palette_delivery_contracts'])}`",
                f"- Delivery telemetry rows: `{len(fixture.get('delivery_telemetry', []))}`",
                f"- Profile delivery telemetry rows: `{len(fixture.get('profile_delivery_telemetry', []))}`",
                f"- Common / union direct facts: `{fixture['common_fact_count']} / {fixture['union_fact_count']}`",
                f"- Unstable direct facts: `{fixture['unstable_fact_count']}`",
                "",
            ]
        )
        if not fixture["palette_stable"]:
            lines.append(f"- Unstable candidate signatures: `{fixture['unstable_candidate_signatures']}`")
            if fixture.get("predicate_arity_drift"):
                lines.append(f"- Predicate arity drift: `{fixture['predicate_arity_drift']}`")
            lines.append("")
            lines.extend(["| Draw | Candidate signatures | Missing palette-union signatures |", "| --- | ---: | --- |"])
            for draw in fixture["draws"]:
                draw_name = Path(draw["compile_json"]).parent.parent.name
                lines.append(
                    f"| `{draw_name}` | {draw['candidate_signature_count']} | `{draw['missing_palette_union_signatures']}` |"
                )
            lines.append("")
        if fixture.get("candidate_zero_yield_signatures"):
            lines.append(f"- Candidate zero-yield signatures: `{fixture['candidate_zero_yield_signatures']}`")
            lines.append("")
            lines.extend(["| Draw | Candidate zero-yield signatures |", "| --- | --- |"])
            for draw in fixture["draws"]:
                draw_name = Path(draw["compile_json"]).parent.parent.name
                lines.append(
                    f"| `{draw_name}` | `{draw['candidate_zero_yield_signatures']}` |"
                )
            lines.append("")
        if fixture.get("signature_delivery_drift"):
            lines.extend(["| Signature | Counts | Delta |", "| --- | --- | ---: |"])
            for row in fixture["signature_delivery_drift"]:
                lines.append(f"| `{row['signature']}` | `{row['counts']}` | {row['delta']} |")
            lines.append("")
        if fixture.get("palette_delivery_contracts"):
            lines.extend(["| Signature | Max rows | Status counts | Draw statuses |", "| --- | ---: | --- | --- |"])
            for row in fixture["palette_delivery_contracts"]:
                statuses = [
                    f"{Path(draw['compile_json']).parent.parent.name}:{draw['status']}:{draw['row_count']}"
                    for draw in row.get("draws", [])
                    if isinstance(draw, dict)
                ]
                lines.append(
                    f"| `{row['signature']}` | {row['max_row_count']} | `{row['classification_counts']}` | `{statuses}` |"
                )
            lines.append("")
        if fixture.get("delivery_telemetry"):
            lines.extend(
                [
                    "| Telemetry | Status | Status counts | Carrier rows | Numeric wrappers | Stranded wrappers |",
                    "| --- | --- | --- | --- | --- | --- |",
                ]
            )
            for row in fixture["delivery_telemetry"]:
                lines.append(
                    f"| `{row['kind']}` | `{row['status']}` | `{row['status_counts']}` | "
                    f"`{row.get('carrier_row_counts', [])}` | `{row.get('numeric_wrapper_counts', [])}` | "
                    f"`{row.get('stranded_numeric_wrapper_counts', [])}` |"
                )
            lines.append("")
        if fixture.get("profile_delivery_telemetry"):
            lines.extend(
                [
                    "| Profile delivery class | Affected draws | Source signals | Offered carriers |",
                    "| --- | ---: | --- | --- |",
                ]
            )
            for row in fixture["profile_delivery_telemetry"]:
                lines.append(
                    f"| `{row['class']}` | {row['affected_draw_count']} / {row['draw_count']} | "
                    f"`{row.get('source_signal_counts', [])}` | `{row.get('offered_carriers', [])}` |"
                )
            lines.append("")
        if fixture["predicate_drift"]:
            lines.extend(["| Predicate | Counts | Delta |", "| --- | --- | ---: |"])
            for row in fixture["predicate_drift"]:
                lines.append(f"| `{row['predicate']}` | `{row['counts']}` | {row['delta']} |")
            lines.append("")
        if fixture["surface_drift"]:
            lines.extend(["| Surface | Counts | Delta |", "| --- | --- | ---: |"])
            for row in fixture["surface_drift"]:
                lines.append(f"| `{row['surface']}` | `{row['counts']}` | {row['delta']} |")
            lines.append("")
        lines.extend(
            [
                "| Draw | Contract | Status | Source signals | Source fields | Source text | Direct surfaces | Complete | Partial | Split |",
                "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for draw in fixture["draws"]:
            draw_name = Path(draw["compile_json"]).parent.parent.name
            for contract in draw["contracts"]:
                lines.append(
                    "| "
                    + " | ".join(
                        [
                            f"`{draw_name}`",
                            f"`{contract['contract']}`",
                            f"`{contract['status']}`",
                            str(contract["source_signal_count"]),
                            str(contract.get("source_field_unit_count", "")),
                            str(contract.get("source_text_mention_count", "")),
                            str(contract["direct_surface_count"]),
                            str(contract.get("direct_complete_count", "")),
                            str(contract.get("direct_partial_count", "")),
                            str(contract.get("direct_split_count", "")),
                        ]
                    )
                    + " |"
                )
        lines.append("")
        for draw in fixture["missing_by_draw"]:
            if not draw["missing_union_fact_count"]:
                continue
            lines.append(f"### Missing From `{Path(draw['compile_json']).parent.parent.name}`")
            lines.append("")
            lines.append(f"- Missing union facts: `{draw['missing_union_fact_count']}`")
            for fact in draw["missing_union_facts"]:
                lines.append(f"- `{fact}`")
            lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compile-json", action="append", type=Path, default=[])
    parser.add_argument("--out-json", type=Path)
    parser.add_argument("--out-md", type=Path)
    args = parser.parse_args()
    report = audit_paths(args.compile_json)
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(render_markdown(report), encoding="utf-8")
    if not args.out_json and not args.out_md:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(json.dumps(report["summary"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
