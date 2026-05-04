#!/usr/bin/env python3
"""Plan row-level QA mode overlays from incoming smoke scorecards."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
VERDICT_RANK = {"exact": 3, "partial": 2, "miss": 1, "not_judged": 0, "unknown": 0, "": 0}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-json", type=Path, required=True)
    parser.add_argument("--candidate-json", type=Path, required=True)
    parser.add_argument("--out-json", type=Path)
    parser.add_argument("--out-md", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    baseline_path = _resolve(args.baseline_json)
    candidate_path = _resolve(args.candidate_json)
    report = build_overlay_plan(
        json.loads(baseline_path.read_text(encoding="utf-8-sig")),
        json.loads(candidate_path.read_text(encoding="utf-8-sig")),
        baseline_path=baseline_path,
        candidate_path=candidate_path,
    )
    out_json = _resolve(args.out_json) if args.out_json else candidate_path.with_name("row_mode_overlay_plan.json")
    out_md = _resolve(args.out_md) if args.out_md else candidate_path.with_name("row_mode_overlay_plan.md")
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    out_md.write_text(render_markdown(report), encoding="utf-8")
    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")
    print(json.dumps(report["summary"], sort_keys=True))
    return 0


def build_overlay_plan(
    baseline: dict[str, Any],
    candidate: dict[str, Any],
    *,
    baseline_path: Path | None = None,
    candidate_path: Path | None = None,
) -> dict[str, Any]:
    fixture_rows = _fixture_rows(baseline, candidate)
    accepted = sum(len(row.get("accepted_candidate_rows", [])) for row in fixture_rows)
    rejected = sum(len(row.get("rejected_candidate_rows", [])) for row in fixture_rows)
    unchanged = sum(len(row.get("unchanged_non_exact_rows", [])) for row in fixture_rows)
    return {
        "schema_version": "incoming_row_mode_overlay_plan_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "policy": [
            "Compares scorecard non-exact row artifacts only.",
            "Does not inspect fixture source prose, gold KBs, or reinterpret answer meaning.",
            "A missing row in non_exact_rows is treated as exact only within the compared scorecard artifact.",
        ],
        "artifacts": {
            "baseline_json": _display_path(baseline_path),
            "candidate_json": _display_path(candidate_path),
        },
        "summary": {
            "fixture_count": len(fixture_rows),
            "accepted_candidate_row_count": accepted,
            "rejected_candidate_row_count": rejected,
            "unchanged_non_exact_row_count": unchanged,
            "recommended_policy": _recommended_policy(accepted=accepted, rejected=rejected),
        },
        "fixtures": fixture_rows,
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report.get("summary", {}) if isinstance(report.get("summary"), dict) else {}
    lines = [
        "# Incoming Row-Mode Overlay Plan",
        "",
        f"Generated: {report.get('generated_at', '')}",
        "",
        "## Summary",
        "",
        f"- Recommendation: `{summary.get('recommended_policy', '')}`",
        f"- Accepted candidate rows: `{summary.get('accepted_candidate_row_count', 0)}`",
        f"- Rejected candidate rows: `{summary.get('rejected_candidate_row_count', 0)}`",
        f"- Unchanged non-exact rows: `{summary.get('unchanged_non_exact_row_count', 0)}`",
        "",
        "## Fixture Rows",
        "",
        "| Fixture | Policy | Accept | Reject | Unchanged |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for row in report.get("fixtures", []):
        if not isinstance(row, dict):
            continue
        lines.append(
            f"| `{row.get('fixture', '')}` | `{row.get('recommended_policy', '')}` | "
            f"{len(row.get('accepted_candidate_rows', []))} | "
            f"{len(row.get('rejected_candidate_rows', []))} | "
            f"{len(row.get('unchanged_non_exact_rows', []))} |"
        )
    lines.extend(["", "## Row Decisions", ""])
    for row in report.get("fixtures", []):
        if not isinstance(row, dict):
            continue
        decisions = [
            ("accept", row.get("accepted_candidate_rows", [])),
            ("reject", row.get("rejected_candidate_rows", [])),
            ("unchanged", row.get("unchanged_non_exact_rows", [])),
        ]
        for label, items in decisions:
            if not isinstance(items, list):
                continue
            for item in items:
                if not isinstance(item, dict):
                    continue
                question = str(item.get("question", "")).replace("|", "/")
                lines.append(
                    f"- `{label}` `{row.get('fixture', '')}` `{item.get('id', '')}`: "
                    f"`{item.get('baseline_verdict', '')}` -> `{item.get('candidate_verdict', '')}`; {question}"
                )
    lines.append("")
    return "\n".join(lines)


def _fixture_rows(baseline: dict[str, Any], candidate: dict[str, Any]) -> list[dict[str, Any]]:
    base_by_fixture = {str(row.get("fixture", "")): row for row in baseline.get("fixtures", []) if isinstance(row, dict)}
    cand_by_fixture = {str(row.get("fixture", "")): row for row in candidate.get("fixtures", []) if isinstance(row, dict)}
    rows: list[dict[str, Any]] = []
    for fixture in sorted(set(base_by_fixture) | set(cand_by_fixture)):
        base_rows = _non_exact_by_id(base_by_fixture.get(fixture, {}))
        cand_rows = _non_exact_by_id(cand_by_fixture.get(fixture, {}))
        accepted: list[dict[str, Any]] = []
        rejected: list[dict[str, Any]] = []
        unchanged: list[dict[str, Any]] = []
        for row_id in sorted(set(base_rows) | set(cand_rows)):
            before = _row_verdict(base_rows.get(row_id))
            after = _row_verdict(cand_rows.get(row_id))
            comparison = _row_delta(row_id=row_id, baseline=base_rows.get(row_id), candidate=cand_rows.get(row_id))
            if _rank(after) > _rank(before):
                accepted.append(comparison)
            elif _rank(after) < _rank(before):
                rejected.append(comparison)
            else:
                unchanged.append(comparison)
        rows.append(
            {
                "fixture": fixture,
                "recommended_policy": _recommended_policy(accepted=len(accepted), rejected=len(rejected)),
                "accepted_candidate_rows": accepted,
                "rejected_candidate_rows": rejected,
                "unchanged_non_exact_rows": unchanged,
            }
        )
    return rows


def _row_delta(row_id: str, baseline: dict[str, Any] | None, candidate: dict[str, Any] | None) -> dict[str, Any]:
    base = baseline or {}
    cand = candidate or {}
    return {
        "id": row_id,
        "baseline_verdict": _row_verdict(baseline),
        "candidate_verdict": _row_verdict(candidate),
        "question": str(cand.get("question") or base.get("question") or ""),
        "baseline_failure_surface": str(base.get("failure_surface", "")),
        "candidate_failure_surface": str(cand.get("failure_surface", "")),
    }


def _non_exact_by_id(fixture_row: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = fixture_row.get("non_exact_rows", []) if isinstance(fixture_row.get("non_exact_rows"), list) else []
    return {str(row.get("id", "")): row for row in rows if isinstance(row, dict) and row.get("id")}


def _row_verdict(row: dict[str, Any] | None) -> str:
    if not row:
        return "exact"
    return str(row.get("verdict", "unknown") or "unknown")


def _rank(verdict: str) -> int:
    return VERDICT_RANK.get(str(verdict), 0)


def _recommended_policy(*, accepted: int, rejected: int) -> str:
    if accepted and rejected:
        return "row_level_selector_required"
    if accepted:
        return "accept_candidate_row_overlays"
    if rejected:
        return "keep_baseline_for_rejected_rows"
    return "no_row_delta"


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
