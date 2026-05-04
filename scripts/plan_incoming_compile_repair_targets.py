#!/usr/bin/env python3
"""Plan compile/query repair targets from incoming scorecard artifacts."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scorecard-json", type=Path, required=True)
    parser.add_argument("--row-overlay-json", type=Path)
    parser.add_argument("--out-json", type=Path)
    parser.add_argument("--out-md", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    scorecard_path = _resolve(args.scorecard_json)
    overlay_path = _resolve(args.row_overlay_json) if args.row_overlay_json else None
    report = build_repair_plan(
        json.loads(scorecard_path.read_text(encoding="utf-8-sig")),
        row_overlay=json.loads(overlay_path.read_text(encoding="utf-8-sig")) if overlay_path else None,
        scorecard_path=scorecard_path,
        row_overlay_path=overlay_path,
    )
    out_json = _resolve(args.out_json) if args.out_json else scorecard_path.with_name("compile_repair_targets.json")
    out_md = _resolve(args.out_md) if args.out_md else scorecard_path.with_name("compile_repair_targets.md")
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
    row_overlay: dict[str, Any] | None = None,
    scorecard_path: Path | None = None,
    row_overlay_path: Path | None = None,
) -> dict[str, Any]:
    overlay_index = _overlay_index(row_overlay or {})
    targets: list[dict[str, Any]] = []
    for fixture in scorecard.get("fixtures", []) if isinstance(scorecard.get("fixtures"), list) else []:
        if not isinstance(fixture, dict):
            continue
        fixture_name = str(fixture.get("fixture", ""))
        for row in fixture.get("non_exact_rows", []) if isinstance(fixture.get("non_exact_rows"), list) else []:
            if not isinstance(row, dict):
                continue
            row_id = str(row.get("id", ""))
            overlay = overlay_index.get((fixture_name, row_id), {})
            targets.append(_target_row(fixture_name=fixture_name, row=row, overlay=overlay))
    lane_counts = Counter(str(target.get("repair_lane", "")) for target in targets)
    surface_counts = Counter(str(target.get("failure_surface", "")) for target in targets)
    selector_counts = Counter(str(target.get("selector_status", "")) for target in targets)
    return {
        "schema_version": "incoming_compile_repair_targets_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "policy": [
            "Reads scorecard and row-overlay artifacts only.",
            "Does not inspect fixture source prose or gold KBs.",
            "Uses after-the-fact judged rows only to prioritize the next harness diagnostic.",
        ],
        "artifacts": {
            "scorecard_json": _display_path(scorecard_path),
            "row_overlay_json": _display_path(row_overlay_path),
        },
        "summary": {
            "target_count": len(targets),
            "repair_lane_counts": dict(sorted(lane_counts.items())),
            "failure_surface_counts": dict(sorted(surface_counts.items())),
            "selector_status_counts": dict(sorted(selector_counts.items())),
        },
        "targets": targets,
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report.get("summary", {}) if isinstance(report.get("summary"), dict) else {}
    lines = [
        "# Incoming Compile Repair Targets",
        "",
        f"Generated: {report.get('generated_at', '')}",
        "",
        "## Summary",
        "",
        f"- Targets: `{summary.get('target_count', 0)}`",
        f"- Repair lanes: `{summary.get('repair_lane_counts', {})}`",
        f"- Failure surfaces: `{summary.get('failure_surface_counts', {})}`",
        f"- Selector status: `{summary.get('selector_status_counts', {})}`",
        "",
        "## Targets",
        "",
        "| Fixture | Row | Verdict | Surface | Selector | Repair Lane | Question |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for target in report.get("targets", []):
        if not isinstance(target, dict):
            continue
        question = str(target.get("question", "")).replace("|", "/")
        lines.append(
            f"| `{target.get('fixture', '')}` | `{target.get('id', '')}` | `{target.get('verdict', '')}` | "
            f"`{target.get('failure_surface', '')}` | `{target.get('selector_status', '')}` | "
            f"`{target.get('repair_lane', '')}` | {question} |"
        )
    lines.append("")
    return "\n".join(lines)


def _target_row(*, fixture_name: str, row: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    surface = str(row.get("failure_surface", "") or "unclassified")
    selector_status = str(overlay.get("selector_status", "unresolved"))
    return {
        "fixture": fixture_name,
        "id": str(row.get("id", "")),
        "question": str(row.get("question", "")),
        "verdict": str(row.get("verdict", "")),
        "failure_surface": surface,
        "selector_status": selector_status,
        "repair_lane": _repair_lane(surface=surface, selector_status=selector_status),
        "queries": row.get("queries", []) if isinstance(row.get("queries"), list) else [],
        "reference_answer": str(row.get("reference_answer", "")),
    }


def _repair_lane(*, surface: str, selector_status: str) -> str:
    if selector_status == "candidate_rescue":
        return "row_selector_calibration"
    if surface == "hybrid_join_gap":
        return "helper_or_query_join_repair"
    if surface == "compile_surface_gap":
        return "scoped_source_surface_repair"
    if surface == "query_surface_gap":
        return "query_planner_repair"
    if surface == "answer_surface_gap":
        return "answer_surface_repair"
    return "classify_before_repair"


def _overlay_index(row_overlay: dict[str, Any]) -> dict[tuple[str, str], dict[str, str]]:
    out: dict[tuple[str, str], dict[str, str]] = {}
    for fixture in row_overlay.get("fixtures", []) if isinstance(row_overlay.get("fixtures"), list) else []:
        if not isinstance(fixture, dict):
            continue
        fixture_name = str(fixture.get("fixture", ""))
        for key, status in [
            ("accepted_candidate_rows", "candidate_rescue"),
            ("rejected_candidate_rows", "candidate_regression"),
            ("unchanged_non_exact_rows", "unresolved"),
        ]:
            for row in fixture.get(key, []) if isinstance(fixture.get(key), list) else []:
                if isinstance(row, dict) and row.get("id"):
                    out[(fixture_name, str(row.get("id", "")))] = {"selector_status": status}
    return out


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
