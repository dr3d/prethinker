#!/usr/bin/env python3
"""Summarize ACH stress-batch proposer reports against fixture expectations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = summarize_ach_stress_run(dataset_root=args.dataset_root, run_dir=args.run_dir)
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(render_markdown(summary), encoding="utf-8")
    print(json.dumps(summary["aggregate"], sort_keys=True))
    return 0 if not summary["aggregate"]["missing_report_count"] else 1


def summarize_ach_stress_run(*, dataset_root: Path, run_dir: Path) -> dict[str, Any]:
    dataset_root = dataset_root.resolve()
    run_dir = run_dir.resolve()
    fixtures = []
    for fixture_dir in sorted(path for path in dataset_root.iterdir() if path.is_dir()):
        payload_path = fixture_dir / "ach_payload.json"
        if not payload_path.exists():
            continue
        payload = json.loads(payload_path.read_text(encoding="utf-8-sig"))
        metadata = _read_json(fixture_dir / "metadata.json")
        report_path = _report_path(run_dir, str(payload.get("fixture_id") or fixture_dir.name))
        report = _read_json(report_path) if report_path else {}
        fixtures.append(_fixture_summary(fixture_dir=fixture_dir, payload=payload, metadata=metadata, report=report, report_path=report_path))

    aggregate = _aggregate(fixtures)
    return {
        "schema_version": "ach_stress_run_summary_v1",
        "dataset_root": _display_path(dataset_root),
        "run_dir": _display_path(run_dir),
        "aggregate": aggregate,
        "fixtures": fixtures,
    }


def _fixture_summary(
    *,
    fixture_dir: Path,
    payload: dict[str, Any],
    metadata: dict[str, Any],
    report: dict[str, Any],
    report_path: Path | None,
) -> dict[str, Any]:
    report_summary = report.get("summary") if isinstance(report.get("summary"), dict) else {}
    expected = payload.get("expected_read") if isinstance(payload.get("expected_read"), dict) else {}
    expected_best = str(expected.get("best_hypothesis") or "").strip()
    expected_pivotal = str(expected.get("pivotal_evidence") or "").strip()
    target = str(metadata.get("sensitivity_target") or expected.get("sensitivity_expectation") or "").strip().casefold()
    top = [str(item) for item in report_summary.get("top_hypotheses", [])] if isinstance(report_summary.get("top_hypotheses"), list) else []
    sensitivity_ids = [
        str(item)
        for item in report_summary.get("sensitivity_evidence_ids", [])
        if str(item)
    ] if isinstance(report_summary.get("sensitivity_evidence_ids"), list) else []
    sensitivity_alignment = _sensitivity_alignment(
        target=target,
        expected_pivotal=expected_pivotal,
        sensitivity_ids=sensitivity_ids,
    )
    return {
        "fixture_id": str(payload.get("fixture_id") or fixture_dir.name),
        "fixture_dir": _display_path(fixture_dir),
        "report_path": _display_path(report_path) if report_path else "",
        "domain": str(metadata.get("domain") or ""),
        "sensitivity_target": target,
        "expected_best_hypothesis": expected_best,
        "top_hypotheses": top,
        "best_matches_expected": bool(expected_best and top == [expected_best]),
        "expected_pivotal_evidence": expected_pivotal,
        "sensitivity_evidence_ids": sensitivity_ids,
        "sensitivity_count": len(sensitivity_ids),
        "sensitivity_alignment": sensitivity_alignment,
        "matrix_complete": bool(report_summary.get("matrix_complete")) if report else False,
        "warning_count": int(report_summary.get("warning_count", 0) or 0),
        "proposal_contract_retry_count": int(report_summary.get("proposal_contract_retry_count", 0) or 0),
        "proposal_contract_violation_count": int(report_summary.get("proposal_contract_violation_count", 0) or 0),
        "question_axis": str(report_summary.get("question_axis") or ""),
        "report_missing": not bool(report),
    }


def _sensitivity_alignment(*, target: str, expected_pivotal: str, sensitivity_ids: list[str]) -> str:
    if target == "low":
        return "clean" if not sensitivity_ids else "false_positive"
    if target == "high":
        if expected_pivotal and expected_pivotal in sensitivity_ids:
            return "pivotal_detected"
        if sensitivity_ids:
            return "wrong_or_partial_sensitivity"
        return "missed"
    if target == "medium":
        return "detected" if sensitivity_ids else "missed"
    return "unknown"


def _aggregate(fixtures: list[dict[str, Any]]) -> dict[str, Any]:
    target_counts: dict[str, int] = {}
    alignment_counts: dict[str, int] = {}
    for row in fixtures:
        target_counts[row["sensitivity_target"]] = target_counts.get(row["sensitivity_target"], 0) + 1
        alignment_counts[row["sensitivity_alignment"]] = alignment_counts.get(row["sensitivity_alignment"], 0) + 1
    return {
        "fixture_count": len(fixtures),
        "missing_report_count": sum(1 for row in fixtures if row["report_missing"]),
        "ranking_correct_count": sum(1 for row in fixtures if row["best_matches_expected"]),
        "matrix_complete_count": sum(1 for row in fixtures if row["matrix_complete"]),
        "warning_count": sum(int(row["warning_count"]) for row in fixtures),
        "contract_residual_fixture_count": sum(1 for row in fixtures if int(row["proposal_contract_violation_count"]) > 0),
        "high_pivotal_detected_count": sum(1 for row in fixtures if row["sensitivity_target"] == "high" and row["sensitivity_alignment"] == "pivotal_detected"),
        "medium_detected_count": sum(1 for row in fixtures if row["sensitivity_target"] == "medium" and row["sensitivity_alignment"] == "detected"),
        "low_clean_count": sum(1 for row in fixtures if row["sensitivity_target"] == "low" and row["sensitivity_alignment"] == "clean"),
        "target_counts": target_counts,
        "sensitivity_alignment_counts": alignment_counts,
    }


def render_markdown(summary: dict[str, Any]) -> str:
    aggregate = summary.get("aggregate", {})
    lines = [
        "# ACH Stress Run Summary",
        "",
        f"- Dataset: `{summary.get('dataset_root', '')}`",
        f"- Run: `{summary.get('run_dir', '')}`",
        f"- Fixtures: `{aggregate.get('fixture_count', 0)}`",
        f"- Ranking correct: `{aggregate.get('ranking_correct_count', 0)}`",
        f"- Matrix complete: `{aggregate.get('matrix_complete_count', 0)}`",
        f"- Warnings: `{aggregate.get('warning_count', 0)}`",
        f"- Contract residual fixtures: `{aggregate.get('contract_residual_fixture_count', 0)}`",
        f"- High pivotal detected: `{aggregate.get('high_pivotal_detected_count', 0)}`",
        f"- Medium detected: `{aggregate.get('medium_detected_count', 0)}`",
        f"- Low clean: `{aggregate.get('low_clean_count', 0)}`",
        "",
        "| Fixture | Target | Top | Sensitivity | Alignment | Contract |",
        "| --- | --- | --- | --- | --- | ---: |",
    ]
    for row in summary.get("fixtures", []):
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row.get('fixture_id', '')}`",
                    f"`{row.get('sensitivity_target', '')}`",
                    f"`{row.get('top_hypotheses', [])}`",
                    f"`{row.get('sensitivity_evidence_ids', [])}`",
                    f"`{row.get('sensitivity_alignment', '')}`",
                    f"`{row.get('proposal_contract_violation_count', 0)}`",
                ]
            )
            + " |"
        )
    lines.append("")
    return "\n".join(lines)


def _report_path(run_dir: Path, fixture_id: str) -> Path | None:
    slug = _slug(fixture_id)
    candidates = sorted(run_dir.glob(f"{slug}_ach_payload_proposal.json"))
    if candidates:
        return candidates[0]
    loose = sorted(run_dir.glob(f"*{slug}*ach_payload_proposal.json"))
    return loose[0] if loose else None


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", str(value).strip().casefold()).strip("-")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    parsed = json.loads(path.read_text(encoding="utf-8-sig"))
    return parsed if isinstance(parsed, dict) else {}


def _display_path(path: Path | None) -> str:
    if path is None:
        return ""
    try:
        return str(path.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        return str(path.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
