from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_JSON = REPO_ROOT / "tmp" / "cross_fixture_repair_slices.json"
DEFAULT_OUT_MD = REPO_ROOT / "tmp" / "cross_fixture_repair_slices.md"


@dataclass(frozen=True)
class RepairTheme:
    theme: str
    purpose: str
    keywords: tuple[str, ...]
    predicate_keywords: tuple[str, ...] = ()
    acquisition_lenses: tuple[str, ...] = ()


THEMES: tuple[RepairTheme, ...] = (
    RepairTheme(
        theme="temporal_status_deadline",
        purpose="Repair status-at-date, deadline, expiration, grace-period, and interval arithmetic rows.",
        keywords=("deadline", "expiration", "status on", "status at", "before", "after", "business day", "grace"),
        predicate_keywords=("deadline", "expires", "status_at", "business_days", "motion_filed", "motion_resolved"),
        acquisition_lenses=("temporal_deadline_surface",),
    ),
    RepairTheme(
        theme="rule_interpretation_application",
        purpose="Acquire or apply rule text, conditions, interpretations, eligibility, approval, and compliance surfaces.",
        keywords=("rule", "interpretation", "eligib", "approval", "approve", "comply", "compliance", "apply", "matching percentage"),
        predicate_keywords=("rule_", "rule", "interpretation", "eligibility", "approval", "compliance", "overlay", "parking_requirement"),
        acquisition_lenses=("rule_interpretation_surface",),
    ),
    RepairTheme(
        theme="authority_document_control",
        purpose="Acquire controlling-document, issuing-authority, notification, parameter, inspection, and priority surfaces.",
        keywords=("authority", "agreement", "resolution", "controls", "inspect", "require", "approve", "customers"),
        predicate_keywords=("priority_rule", "notification_requirement", "specifies_parameter", "document_type", "issued_by", "recommends_action"),
        acquisition_lenses=("authority_document_surface",),
    ),
    RepairTheme(
        theme="rationale_claim_uncertainty",
        purpose="Acquire explicit reasons, source-note rationale, corrections, unresolved questions, claim status, and evidentiary posture.",
        keywords=("why", "reason", "unresolved", "evidentiary", "source report", "suspect", "deliberate", "correction", "current position"),
        predicate_keywords=("reason", "note", "source", "explicit_non_finding", "suspected", "corrected", "concern", "panel_decision"),
        acquisition_lenses=("claim_truth_status_surface", "permission_rationale_surface"),
    ),
    RepairTheme(
        theme="entity_role_identity",
        purpose="Acquire identity, person-role, roster, role-holder, and named-actor surfaces.",
        keywords=("who ", "which exhibitor", "review panel", "facilities director"),
        predicate_keywords=("person_role", "registered_as", "role", "director", "flagged_by"),
        acquisition_lenses=("identity_role_roster_surface",),
    ),
    RepairTheme(
        theme="object_state_custody",
        purpose="Acquire object current-state, condition, location, custody, ownership, award, and device transition surfaces.",
        keywords=("current condition", "currently in", "where is", "custody", "ownership", "device", "loom", "lantern", "split to vault"),
        predicate_keywords=("initial_state", "current_state", "event_location", "owns", "device_name", "awarded", "vault", "lot_status"),
        acquisition_lenses=("object_state_transition_surface", "object_location_custody_surface", "outcome_award_status_surface"),
    ),
    RepairTheme(
        theme="quantity_arithmetic_capacity",
        purpose="Repair numeric capacity, cost, percentage, threshold, fund-balance, and quantity arithmetic rows.",
        keywords=("how many", "afford", "percentage", "threshold", "adjusted", "maximum allowable", "amount"),
        predicate_keywords=("cost", "fund_balance", "loan_term", "threshold", "amount", "percentage", "footprint", "lot_area", "dimension"),
        acquisition_lenses=("fiscal_capacity_surface", "spatial_dimension_surface"),
    ),
    RepairTheme(
        theme="answer_restraint_surface",
        purpose="Repair rows whose evidence exists but the answer needs better uncertainty, current-position, or evidentiary wording.",
        keywords=("evidentiary status", "current position"),
        predicate_keywords=(),
        acquisition_lenses=("answer_surface_repair",),
    ),
)


def load_targets(paths: list[Path]) -> list[dict[str, Any]]:
    targets: list[dict[str, Any]] = []
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        for target in payload.get("targets", []) or []:
            if not isinstance(target, dict):
                continue
            targets.append({**target, "source_artifact": str(path)})
    return targets


def classify_theme(target: dict[str, Any]) -> str:
    lens = str(target.get("acquisition_lens") or target.get("repair_lane") or "").casefold()
    question = str(target.get("question") or "").casefold()
    queries = " ".join(str(query) for query in target.get("queries", []) or []).casefold()
    for theme in THEMES:
        if any(item.casefold() == lens for item in theme.acquisition_lenses):
            return theme.theme
    for theme in THEMES:
        if any(keyword.casefold() in queries for keyword in theme.predicate_keywords):
            return theme.theme
    for theme in THEMES:
        if any(keyword.casefold() in question for keyword in theme.keywords):
            return theme.theme
    return "classify_before_repair"


def build_report(paths: list[Path], *, min_fixtures: int = 2, max_rows_per_slice: int = 8) -> dict[str, Any]:
    targets = load_targets(paths)
    records: list[dict[str, Any]] = []
    for target in targets:
        records.append(
            {
                "theme": classify_theme(target),
                "fixture": str(target.get("fixture") or ""),
                "id": str(target.get("id") or ""),
                "verdict": str(target.get("verdict") or ""),
                "failure_surface": str(target.get("failure_surface") or ""),
                "repair_lane": str(target.get("repair_lane") or ""),
                "acquisition_lens": str(target.get("acquisition_lens") or ""),
                "question": str(target.get("question") or ""),
                "source_artifact": str(target.get("source_artifact") or ""),
            }
        )
    by_theme: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_theme[record["theme"]].append(record)
    purpose = {theme.theme: theme.purpose for theme in THEMES}
    purpose["classify_before_repair"] = "Rows that need human or more specific artifact classification before harness work."
    slices: list[dict[str, Any]] = []
    for theme, items in by_theme.items():
        fixtures = sorted({item["fixture"] for item in items if item["fixture"]})
        surfaces = Counter(item["failure_surface"] for item in items if item["failure_surface"])
        lanes = Counter(item["repair_lane"] for item in items if item["repair_lane"])
        verdicts = Counter(item["verdict"] for item in items if item["verdict"])
        score = len(items) * 4 + len(fixtures) * 8 + verdicts.get("miss", 0) * 2 + surfaces.get("compile_surface_gap", 0)
        if len(fixtures) >= min_fixtures:
            slices.append(
                {
                    "theme": theme,
                    "purpose": purpose.get(theme, ""),
                    "target_count": len(items),
                    "fixture_count": len(fixtures),
                    "fixtures": fixtures,
                    "failure_surface_counts": dict(sorted(surfaces.items())),
                    "repair_lane_counts": dict(sorted(lanes.items())),
                    "verdict_counts": dict(sorted(verdicts.items())),
                    "priority_score": score,
                    "representative_rows": sorted(
                        items,
                        key=lambda item: (
                            0 if item["verdict"] == "miss" else 1,
                            item["fixture"],
                            item["id"],
                        ),
                    )[:max_rows_per_slice],
                }
            )
    slices.sort(key=lambda item: (-int(item["priority_score"]), -int(item["fixture_count"]), item["theme"]))
    return {
        "schema_version": "cross_fixture_repair_slices_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "policy": [
            "Reads repair-target artifacts only.",
            "Does not inspect fixture source prose, gold KBs, or answer keys.",
            "Recommends only themes with targets in multiple fixtures by default.",
        ],
        "artifacts": [str(path) for path in paths],
        "summary": {
            "target_count": len(records),
            "theme_counts": dict(sorted(Counter(record["theme"] for record in records).items())),
            "fixture_count": len({record["fixture"] for record in records if record["fixture"]}),
            "recommended_slice_count": len(slices),
            "top_theme": slices[0]["theme"] if slices else "",
        },
        "recommended_slices": slices,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Cross-Fixture Repair Slices",
        "",
        "This report merges repair-target artifacts and looks for repeated failure",
        "themes across fixtures. It is a planning tool, not a source interpreter.",
        "",
        "## Policy",
        "",
    ]
    lines.extend(f"- {item}" for item in report.get("policy", []))
    summary = report.get("summary", {})
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- targets: `{summary.get('target_count', 0)}`",
            f"- fixtures: `{summary.get('fixture_count', 0)}`",
            f"- recommended slices: `{summary.get('recommended_slice_count', 0)}`",
            f"- top theme: `{summary.get('top_theme', '')}`",
            f"- theme counts: `{summary.get('theme_counts', {})}`",
            "",
            "## Recommended Slices",
            "",
        ]
    )
    for slice_ in report.get("recommended_slices", []):
        lines.extend(
            [
                f"### `{slice_['theme']}`",
                "",
                f"- priority score: `{slice_['priority_score']}`",
                f"- targets: `{slice_['target_count']}`",
                f"- fixtures: `{slice_['fixture_count']}` - {', '.join(slice_['fixtures'])}",
                f"- surfaces: `{slice_['failure_surface_counts']}`",
                f"- lanes: `{slice_['repair_lane_counts']}`",
                f"- purpose: {slice_['purpose']}",
                "",
                "| Fixture | Row | Verdict | Surface | Question |",
                "| --- | --- | --- | --- | --- |",
            ]
        )
        for row in slice_.get("representative_rows", []):
            lines.append(
                f"| `{row['fixture']}` | `{row['id']}` | `{row['verdict']}` | "
                f"`{row['failure_surface']}` | {row['question']} |"
            )
        lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-json", action="append", type=Path, required=True)
    parser.add_argument("--min-fixtures", type=int, default=2)
    parser.add_argument("--max-rows-per-slice", type=int, default=8)
    parser.add_argument("--out-json", type=Path, default=DEFAULT_OUT_JSON)
    parser.add_argument("--out-md", type=Path, default=DEFAULT_OUT_MD)
    return parser.parse_args()


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else (REPO_ROOT / path).resolve()


def main() -> int:
    args = parse_args()
    paths = [_resolve(path) for path in args.target_json]
    report = build_report(paths, min_fixtures=args.min_fixtures, max_rows_per_slice=args.max_rows_per_slice)
    out_json = _resolve(args.out_json)
    out_md = _resolve(args.out_md)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    out_md.write_text(render_markdown(report), encoding="utf-8")
    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")
    print(json.dumps(report["summary"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
