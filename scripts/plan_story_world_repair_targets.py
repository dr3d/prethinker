#!/usr/bin/env python3
"""Plan story-world repair targets from full-QA scorecard artifacts."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
PREDICATE_RE = re.compile(r"\b([a-z][A-Za-z0-9_]*)\s*\(")


LENS_RULES: tuple[tuple[str, set[str], str], ...] = (
    (
        "governance_authority_rationale_surface",
        {
            "application_status",
            "eligibility_determination",
            "interpretation_text",
            "member_recused",
            "prior_grant_history",
            "quorum_met",
            "rule_clarified",
            "rule_exception",
            "vote_result",
        },
        "governance authority, recusal, quorum, interpretation, and eligibility-rationale rows need source-surface coverage",
    ),
    (
        "narrative_event_detail_surface",
        {
            "causes",
            "event",
            "has_property",
            "judged",
            "precedes",
            "said",
        },
        "narrative event, speech, judgment, and concrete-detail predicates need source-surface coverage",
    ),
    (
        "object_state_transition_surface",
        {
            "initial_state",
            "final_state",
            "current_state",
            "state",
            "condition",
            "device_state",
            "object_state",
            "event_affects_person",
            "event_affects_object",
        },
        "object/device state predicates need transition and final-state coverage",
    ),
    (
        "object_location_custody_surface",
        {
            "device_name",
            "event_location",
            "owns",
            "custody",
            "custodian",
            "located_at",
            "location",
        },
        "object location, ownership, or custody predicates need final-holder coverage",
    ),
    (
        "permission_rationale_surface",
        {
            "permission_granted",
            "permission_denied",
            "authorized",
            "disqualified_from",
            "ruling_by",
            "ruled_by",
            "rule_applies_to",
            "official_action",
            "reason",
            "rationale",
            "cause",
            "caused_by",
        },
        "permission, authority, or rationale predicates need source-surface coverage",
    ),
    (
        "temporal_deadline_surface",
        {
            "deadline",
            "deadline_toll",
            "event_on",
            "event_date",
            "event_occurs",
            "before",
            "after",
            "motion_filed",
            "motion_resolved",
            "interval_start",
            "interval_end",
        },
        "deadline/date/event-time predicates need source-surface acquisition",
    ),
    (
        "rule_threshold_surface",
        {
            "rule_threshold",
            "support_threshold_met",
            "derived_condition",
            "required_condition",
            "requires_public_hearing",
            "amendment_introduced",
            "supported",
            "vote",
        },
        "rule, vote, threshold, or derived-condition predicates need rule/body support",
    ),
    (
        "rule_interpretation_surface",
        {
            "rule_text",
            "rule_condition",
            "board_objection",
            "board_question",
            "staff_analysis",
            "unresolved_interpretation",
            "grandfathering_trigger",
            "parking_requirement",
            "overlay_priority",
        },
        "rule interpretation predicates need condition/scope/consequence coverage",
    ),
    (
        "spatial_dimension_surface",
        {
            "lot_dimension",
            "lot_area",
            "overlay_applicability",
            "dimensional_compliance",
            "property_location",
            "structure_footprint",
            "structure_height",
            "structure_historic_status",
            "structure_construction_year",
        },
        "spatial/dimensional predicates need measurement and overlay-scope coverage",
    ),
    (
        "identity_role_roster_surface",
        {
            "person_role",
            "registered_as",
            "person_name",
            "name",
            "alias",
            "member_of",
            "panel_member",
            "participant",
            "applicant",
        },
        "identity, roster, or role predicates are missing answer-bearing rows",
    ),
    (
        "claim_truth_status_surface",
        {
            "source_claim",
            "witness_statement",
            "finding",
            "explicit_non_finding",
            "reported_event",
            "claim_status",
            "statement_detail",
            "suspected_of",
            "admits_to",
            "epistemic_status",
        },
        "claim/finding/non-finding predicates need epistemic-status coverage",
    ),
    (
        "authority_document_surface",
        {
            "resolution",
            "resolution_adopted",
            "document",
            "document_date",
            "policy",
            "board_action",
            "authority",
            "issued_by",
            "document_type",
            "priority_rule",
            "notification_requirement",
            "specifies_parameter",
            "penalty_condition",
            "recommends_action",
        },
        "document/authority predicates need cross-document source support",
    ),
    (
        "fiscal_capacity_surface",
        {
            "cost_estimate",
            "fund_balance",
            "loan_term",
        },
        "cost/fund/loan predicates need fiscal-capacity join coverage",
    ),
    (
        "outcome_award_status_surface",
        {
            "awarded",
            "proposed_change",
        },
        "award, exhibition, or proposed-outcome predicates need status and consequence coverage",
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scorecard-json", type=Path, required=True)
    parser.add_argument("--fixture", action="append", default=[])
    parser.add_argument("--out-json", type=Path)
    parser.add_argument("--out-md", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    scorecard_path = _resolve(args.scorecard_json)
    report = build_repair_plan(
        json.loads(scorecard_path.read_text(encoding="utf-8-sig")),
        scorecard_path=scorecard_path,
        fixture_filter=set(args.fixture or []),
    )
    out_json = _resolve(args.out_json) if args.out_json else scorecard_path.with_name("story_world_repair_targets.json")
    out_md = _resolve(args.out_md) if args.out_md else scorecard_path.with_name("story_world_repair_targets.md")
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    out_md.write_text(render_markdown(report), encoding="utf-8")
    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")
    print(json.dumps(report["summary"], sort_keys=True))
    return 0


def build_repair_plan(
    scorecard: dict[str, Any],
    *,
    scorecard_path: Path | None = None,
    fixture_filter: set[str] | None = None,
) -> dict[str, Any]:
    fixture_filter = fixture_filter or set()
    targets: list[dict[str, Any]] = []
    fixture_rows = _scorecard_fixture_rows(scorecard)
    for fixture in fixture_rows:
        if not isinstance(fixture, dict):
            continue
        fixture_name = str(fixture.get("fixture") or fixture.get("label") or "")
        if fixture_filter and fixture_name not in fixture_filter:
            continue
        for row in fixture.get("non_exact_rows", []) if isinstance(fixture.get("non_exact_rows"), list) else []:
            if isinstance(row, dict):
                targets.append(_target_row(fixture_name=fixture_name, row=row))

    targets.sort(key=lambda item: (-int(item["priority"]), item["fixture"], item["id"]))
    lane_counts = Counter(str(target.get("repair_lane", "")) for target in targets)
    lens_counts = Counter(str(target.get("acquisition_lens", "")) for target in targets)
    surface_counts = Counter(str(target.get("failure_surface", "")) for target in targets)
    fixture_counts = Counter(str(target.get("fixture", "")) for target in targets)
    return {
        "schema_version": "story_world_repair_targets_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "policy": [
            "Reads scorecard artifacts only.",
            "Does not inspect fixture source prose, gold KBs, or answer keys for classification.",
            "Classifies acquisition lenses from query predicate names and judged failure surfaces.",
        ],
        "artifacts": {"scorecard_json": _display_path(scorecard_path)},
        "summary": {
            "target_count": len(targets),
            "fixture_counts": dict(sorted(fixture_counts.items())),
            "failure_surface_counts": dict(sorted(surface_counts.items())),
            "repair_lane_counts": dict(sorted(lane_counts.items())),
            "acquisition_lens_counts": dict(sorted(lens_counts.items())),
            "top_fixture": fixture_counts.most_common(1)[0][0] if fixture_counts else "",
            "top_acquisition_lens": lens_counts.most_common(1)[0][0] if lens_counts else "",
        },
        "targets": targets,
    }


def _scorecard_fixture_rows(scorecard: dict[str, Any]) -> list[Any]:
    fixtures = scorecard.get("fixtures")
    if isinstance(fixtures, list):
        return fixtures
    artifacts = scorecard.get("artifacts")
    if isinstance(artifacts, list):
        return artifacts
    return []


def render_markdown(report: dict[str, Any]) -> str:
    summary = report.get("summary", {}) if isinstance(report.get("summary"), dict) else {}
    lines = [
        "# Story-World Repair Targets",
        "",
        f"Generated: {report.get('generated_at', '')}",
        "",
        "## Policy",
        "",
    ]
    for rule in report.get("policy", []):
        lines.append(f"- {rule}")
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Targets: `{summary.get('target_count', 0)}`",
            f"- Fixtures: `{summary.get('fixture_counts', {})}`",
            f"- Failure surfaces: `{summary.get('failure_surface_counts', {})}`",
            f"- Repair lanes: `{summary.get('repair_lane_counts', {})}`",
            f"- Acquisition lenses: `{summary.get('acquisition_lens_counts', {})}`",
            f"- Top fixture: `{summary.get('top_fixture', '')}`",
            f"- Top acquisition lens: `{summary.get('top_acquisition_lens', '')}`",
            "",
            "## Targets",
            "",
            "| Priority | Fixture | Row | Verdict | Surface | Repair Lane | Acquisition Lens | Predicate Hints | Question |",
            "| ---: | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for target in report.get("targets", []):
        if not isinstance(target, dict):
            continue
        question = str(target.get("question", "")).replace("|", "/")
        predicates = ", ".join(str(p) for p in target.get("predicate_hints", []))
        lines.append(
            f"| `{target.get('priority', '')}` | `{target.get('fixture', '')}` | `{target.get('id', '')}` | "
            f"`{target.get('verdict', '')}` | `{target.get('failure_surface', '')}` | "
            f"`{target.get('repair_lane', '')}` | `{target.get('acquisition_lens', '')}` | "
            f"`{predicates}` | {question} |"
        )
    lines.append("")
    return "\n".join(lines)


def _target_row(*, fixture_name: str, row: dict[str, Any]) -> dict[str, Any]:
    queries = row.get("queries", []) if isinstance(row.get("queries"), list) else []
    predicates = sorted({predicate for query in queries for predicate in _predicates(str(query))})
    lens, reason = _acquisition_lens(predicates)
    surface = str(row.get("failure_surface", "") or "unclassified")
    verdict = str(row.get("verdict", ""))
    return {
        "fixture": fixture_name,
        "id": str(row.get("id", "")),
        "question": str(row.get("question", "")),
        "verdict": verdict,
        "failure_surface": surface,
        "repair_lane": _repair_lane(surface=surface),
        "acquisition_lens": lens,
        "lens_reason": reason,
        "priority": _priority(surface=surface, verdict=verdict),
        "predicate_hints": predicates,
        "queries": queries,
    }


def _predicates(query: str) -> list[str]:
    return [match.group(1) for match in PREDICATE_RE.finditer(query)]


def _acquisition_lens(predicates: list[str]) -> tuple[str, str]:
    predicate_set = set(predicates)
    for lens, candidates, reason in LENS_RULES:
        if predicate_set & candidates:
            return lens, reason
    if predicates:
        return "answer_bearing_source_surface", "predicate hints are present but do not match a named lens yet"
    return "classify_before_repair", "no predicate hints were available in the scorecard row"


def _repair_lane(*, surface: str) -> str:
    if surface == "compile_surface_gap":
        return "scoped_source_surface_repair"
    if surface == "hybrid_join_gap":
        return "helper_or_query_join_repair"
    if surface == "query_surface_gap":
        return "query_planner_repair"
    if surface == "answer_surface_gap":
        return "answer_surface_repair"
    return "classify_before_repair"


def _priority(*, surface: str, verdict: str) -> int:
    score = 0
    if verdict == "miss":
        score += 30
    elif verdict == "partial":
        score += 20
    if surface == "compile_surface_gap":
        score += 10
    elif surface == "hybrid_join_gap":
        score += 6
    elif surface == "query_surface_gap":
        score += 4
    return score


def _resolve(path: Path | None) -> Path:
    if path is None:
        return REPO_ROOT
    return path if path.is_absolute() else REPO_ROOT / path


def _display_path(value: Path | str | None) -> str:
    if value is None:
        return ""
    path = value if isinstance(value, Path) else Path(str(value))
    try:
        return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
