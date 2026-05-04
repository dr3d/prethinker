#!/usr/bin/env python3
"""Compare two incoming fixture smoke scorecards."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]


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
    report = build_comparison(
        json.loads(baseline_path.read_text(encoding="utf-8-sig")),
        json.loads(candidate_path.read_text(encoding="utf-8-sig")),
        baseline_path=baseline_path,
        candidate_path=candidate_path,
    )
    out_json = _resolve(args.out_json) if args.out_json else candidate_path.with_name("scorecard_comparison.json")
    out_md = _resolve(args.out_md) if args.out_md else candidate_path.with_name("scorecard_comparison.md")
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    out_md.write_text(render_markdown(report), encoding="utf-8")
    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")
    print(json.dumps(report["summary"], sort_keys=True))
    return 0


def build_comparison(
    baseline: dict[str, Any],
    candidate: dict[str, Any],
    *,
    baseline_path: Path | None = None,
    candidate_path: Path | None = None,
) -> dict[str, Any]:
    baseline_summary = _summary(baseline)
    candidate_summary = _summary(candidate)
    fixture_rows = _fixture_rows(baseline, candidate)
    exact_regressions = _baseline_exact_regression_rows(baseline, candidate)
    delta = {
        "fixture_count": _int(candidate_summary, "fixture_count") - _int(baseline_summary, "fixture_count"),
        "compiled_count": _int(candidate_summary, "compiled_count") - _int(baseline_summary, "compiled_count"),
        "compile_failed_count": _int(candidate_summary, "compile_failed_count")
        - _int(baseline_summary, "compile_failed_count"),
        "qa_rows": _int(candidate_summary, "qa_rows") - _int(baseline_summary, "qa_rows"),
        "exact_rows": _int(candidate_summary, "exact_rows") - _int(baseline_summary, "exact_rows"),
        "partial_rows": _int(candidate_summary, "partial_rows") - _int(baseline_summary, "partial_rows"),
        "miss_rows": _int(candidate_summary, "miss_rows") - _int(baseline_summary, "miss_rows"),
        "write_proposal_rows": _int(candidate_summary, "write_proposal_rows")
        - _int(baseline_summary, "write_proposal_rows"),
        "exact_rate": _number(candidate_summary, "exact_rate") - _number(baseline_summary, "exact_rate"),
        "failure_surface_counts": _counter_delta(
            baseline_summary.get("failure_surface_counts"),
            candidate_summary.get("failure_surface_counts"),
        ),
        "semantic_progress_risk_counts": _counter_delta(
            baseline_summary.get("semantic_progress_risk_counts"),
            candidate_summary.get("semantic_progress_risk_counts"),
        ),
        "baseline_exact_regression_rows": len(exact_regressions),
    }
    return {
        "schema_version": "incoming_fixture_smoke_scorecard_comparison_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "policy": [
            "Compares scorecard artifacts only.",
            "Does not inspect fixture source prose or reinterpret answers.",
        ],
        "artifacts": {
            "baseline_json": _display_path(baseline_path),
            "candidate_json": _display_path(candidate_path),
        },
        "summary": {
            "baseline": baseline_summary,
            "candidate": candidate_summary,
            "delta": delta,
            "promotion_recommendation": _recommend(delta),
        },
        "fixtures": fixture_rows,
        "baseline_exact_regressions": exact_regressions,
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report.get("summary", {}) if isinstance(report.get("summary"), dict) else {}
    delta = summary.get("delta", {}) if isinstance(summary.get("delta"), dict) else {}
    lines = [
        "# Incoming Fixture Smoke Scorecard Comparison",
        "",
        f"Generated: {report.get('generated_at', '')}",
        "",
        "## Summary",
        "",
        f"- Recommendation: `{summary.get('promotion_recommendation', '')}`",
        f"- Exact delta: `{delta.get('exact_rows', 0)}`",
        f"- Exact-rate delta: `{delta.get('exact_rate', 0)}`",
        f"- Partial delta: `{delta.get('partial_rows', 0)}`",
        f"- Miss delta: `{delta.get('miss_rows', 0)}`",
        f"- Compile-failed delta: `{delta.get('compile_failed_count', 0)}`",
        f"- Write-proposal delta: `{delta.get('write_proposal_rows', 0)}`",
        f"- Baseline-exact regressions: `{delta.get('baseline_exact_regression_rows', 0)}`",
        f"- Failure-surface deltas: `{delta.get('failure_surface_counts', {})}`",
        f"- Semantic-risk deltas: `{delta.get('semantic_progress_risk_counts', {})}`",
        "",
        "## Fixture Deltas",
        "",
        "| Fixture | Exact | Partial | Miss | Baseline | Candidate |",
        "| --- | ---: | ---: | ---: | --- | --- |",
    ]
    for row in report.get("fixtures", []):
        if not isinstance(row, dict):
            continue
        delta_row = row.get("delta", {}) if isinstance(row.get("delta"), dict) else {}
        lines.append(
            f"| `{row.get('fixture', '')}` | {delta_row.get('exact', 0)} | {delta_row.get('partial', 0)} | "
            f"{delta_row.get('miss', 0)} | `{row.get('baseline_label', '')}` | `{row.get('candidate_label', '')}` |"
        )
    regressions = report.get("baseline_exact_regressions", [])
    if regressions:
        lines.extend(["", "## Baseline-Exact Regressions", "", "| Fixture | Row | Candidate Verdict | Question |", "| --- | --- | --- | --- |"])
        for row in regressions:
            if not isinstance(row, dict):
                continue
            question = str(row.get("question", "")).replace("|", "/")
            lines.append(
                f"| `{row.get('fixture', '')}` | `{row.get('id', '')}` | "
                f"`{row.get('candidate_verdict', '')}` | {question} |"
            )
    lines.append("")
    return "\n".join(lines)


def _fixture_rows(baseline: dict[str, Any], candidate: dict[str, Any]) -> list[dict[str, Any]]:
    base_by_fixture = {str(row.get("fixture", "")): row for row in baseline.get("fixtures", []) if isinstance(row, dict)}
    cand_by_fixture = {str(row.get("fixture", "")): row for row in candidate.get("fixtures", []) if isinstance(row, dict)}
    rows: list[dict[str, Any]] = []
    for fixture in sorted(set(base_by_fixture) | set(cand_by_fixture)):
        base = base_by_fixture.get(fixture, {})
        cand = cand_by_fixture.get(fixture, {})
        base_judge = base.get("judge_counts", {}) if isinstance(base.get("judge_counts"), dict) else {}
        cand_judge = cand.get("judge_counts", {}) if isinstance(cand.get("judge_counts"), dict) else {}
        rows.append(
            {
                "fixture": fixture,
                "baseline_label": _label(base),
                "candidate_label": _label(cand),
                "baseline_compile_status": str(base.get("compile_status", "")),
                "candidate_compile_status": str(cand.get("compile_status", "")),
                "baseline_compile_health": str(base.get("compile_health", "")),
                "candidate_compile_health": str(cand.get("compile_health", "")),
                "baseline_semantic_progress_risk": str(base.get("semantic_progress_risk", "")),
                "candidate_semantic_progress_risk": str(cand.get("semantic_progress_risk", "")),
                "baseline_profile_fallback": str(base.get("profile_fallback", "")),
                "candidate_profile_fallback": str(cand.get("profile_fallback", "")),
                "delta": {
                    "exact": int(cand_judge.get("exact", 0) or 0) - int(base_judge.get("exact", 0) or 0),
                    "partial": int(cand_judge.get("partial", 0) or 0) - int(base_judge.get("partial", 0) or 0),
                    "miss": int(cand_judge.get("miss", 0) or 0) - int(base_judge.get("miss", 0) or 0),
                },
            }
        )
    return rows


def _recommend(delta: dict[str, Any]) -> str:
    if (
        delta.get("compile_failed_count", 0) > 0
        or delta.get("write_proposal_rows", 0) > 0
        or delta.get("miss_rows", 0) > 0
    ):
        return "reject_candidate"
    if delta.get("exact_rows", 0) < 0:
        return "reject_candidate"
    if delta.get("baseline_exact_regression_rows", 0) > 0:
        return "row_level_gate_required"
    if delta.get("exact_rows", 0) > 0:
        return "promote_candidate"
    return "mixed_candidate"


def _baseline_exact_regression_rows(baseline: dict[str, Any], candidate: dict[str, Any]) -> list[dict[str, Any]]:
    base_by_fixture = {str(row.get("fixture", "")): row for row in baseline.get("fixtures", []) if isinstance(row, dict)}
    cand_by_fixture = {str(row.get("fixture", "")): row for row in candidate.get("fixtures", []) if isinstance(row, dict)}
    out: list[dict[str, Any]] = []
    for fixture in sorted(set(base_by_fixture) & set(cand_by_fixture)):
        base = base_by_fixture.get(fixture, {})
        cand = cand_by_fixture.get(fixture, {})
        if "non_exact_rows" not in base or "non_exact_rows" not in cand:
            continue
        base_non_exact = _non_exact_by_id(base)
        for row_id, row in _non_exact_by_id(cand).items():
            if row_id not in base_non_exact:
                out.append(
                    {
                        "fixture": fixture,
                        "id": row_id,
                        "candidate_verdict": str(row.get("verdict", "unknown") or "unknown"),
                        "question": str(row.get("question", "")),
                    }
                )
    return out


def _non_exact_by_id(fixture_row: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = fixture_row.get("non_exact_rows", []) if isinstance(fixture_row.get("non_exact_rows"), list) else []
    return {str(row.get("id", "")): row for row in rows if isinstance(row, dict) and row.get("id")}


def _summary(scorecard: dict[str, Any]) -> dict[str, Any]:
    summary = scorecard.get("summary", {}) if isinstance(scorecard.get("summary"), dict) else {}
    return {
        "fixture_count": _int(summary, "fixture_count"),
        "compiled_count": _int(summary, "compiled_count"),
        "compile_failed_count": _int(summary, "compile_failed_count"),
        "qa_rows": _int(summary, "qa_rows"),
        "exact_rows": _int(summary, "exact_rows"),
        "partial_rows": _int(summary, "partial_rows"),
        "miss_rows": _int(summary, "miss_rows"),
        "exact_rate": summary.get("exact_rate"),
        "failure_surface_counts": dict(summary.get("failure_surface_counts", {}))
        if isinstance(summary.get("failure_surface_counts"), dict)
        else {},
        "semantic_progress_risk_counts": dict(summary.get("semantic_progress_risk_counts", {}))
        if isinstance(summary.get("semantic_progress_risk_counts"), dict)
        else {},
        "write_proposal_rows": _int(summary, "write_proposal_rows"),
    }


def _label(row: dict[str, Any]) -> str:
    judge = row.get("judge_counts", {}) if isinstance(row.get("judge_counts"), dict) else {}
    return f"{judge.get('exact', 0)}/{judge.get('partial', 0)}/{judge.get('miss', 0)}"


def _int(value: dict[str, Any], key: str) -> int:
    return int(value.get(key, 0) or 0)


def _number(value: dict[str, Any], key: str) -> float:
    raw = value.get(key)
    if raw is None or raw == "":
        return 0.0
    return float(raw)


def _counter_delta(baseline: Any, candidate: Any) -> dict[str, int]:
    base = baseline if isinstance(baseline, dict) else {}
    cand = candidate if isinstance(candidate, dict) else {}
    out: dict[str, int] = {}
    for key in sorted(set(base) | set(cand)):
        out[str(key)] = int(cand.get(key, 0) or 0) - int(base.get(key, 0) or 0)
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
