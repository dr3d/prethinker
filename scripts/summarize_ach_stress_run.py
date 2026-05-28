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
    top_support = _top_support_rows(report)
    pivotal_support = next(
        (item for item in top_support if item.get("evidence_id") == expected_pivotal),
        {},
    )
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
        "expected_pivotal_support_rank": int(pivotal_support.get("support_rank", 0) or 0),
        "expected_pivotal_support_share": float(pivotal_support.get("support_share", 0.0) or 0.0),
        "expected_pivotal_evidence_role": str(pivotal_support.get("role", "")),
        "top_support_evidence_ids": [
            str(item.get("evidence_id") or "")
            for item in top_support
            if int(item.get("support_weight", 0) or 0) > 0
        ][:5],
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


def _top_support_rows(report: dict[str, Any]) -> list[dict[str, Any]]:
    ach_report = report.get("ach_report") if isinstance(report.get("ach_report"), dict) else {}
    rows = ach_report.get("top_support_contributions") if isinstance(ach_report.get("top_support_contributions"), list) else []
    if rows:
        return _ranked_support_rows(rows)

    summary = report.get("summary") if isinstance(report.get("summary"), dict) else {}
    top = summary.get("top_hypotheses")
    if not isinstance(top, list) or len(top) != 1:
        return []
    top_id = str(top[0])
    scorer_payload = report.get("scorer_payload") if isinstance(report.get("scorer_payload"), dict) else {}
    judgments = scorer_payload.get("judgments") if isinstance(scorer_payload.get("judgments"), list) else []
    labels = {
        str(item.get("id") or ""): str(item.get("label") or item.get("id") or "")
        for item in scorer_payload.get("evidence", []) or []
        if isinstance(item, dict)
    }
    roles = {
        str(item.get("id") or ""): str(item.get("role") or "")
        for item in scorer_payload.get("evidence", []) or []
        if isinstance(item, dict)
    }
    support_rows: list[dict[str, Any]] = []
    total_support = 0
    for item in judgments:
        if not isinstance(item, dict):
            continue
        if str(item.get("hypothesis_id") or "") != top_id:
            continue
        evidence_id = str(item.get("evidence_id") or "")
        assessment = str(item.get("assessment") or "")
        weight = int(item.get("weight", 0) or 0)
        support_weight = weight if assessment == "consistent" else 0
        total_support += support_weight
        support_rows.append(
            {
                "evidence_id": evidence_id,
                "label": labels.get(evidence_id, evidence_id),
                "role": roles.get(evidence_id, ""),
                "top_hypothesis_id": top_id,
                "assessment": assessment,
                "weight": weight,
                "support_weight": support_weight,
                "support_share": 0.0,
            }
        )
    for item in support_rows:
        item["support_share"] = round(int(item["support_weight"]) / total_support, 4) if total_support > 0 else 0.0
    return _ranked_support_rows(support_rows)


def _ranked_support_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = [
        {
            "evidence_id": str(item.get("evidence_id") or ""),
            "label": str(item.get("label") or item.get("evidence_id") or ""),
            "role": str(item.get("role") or ""),
            "top_hypothesis_id": str(item.get("top_hypothesis_id") or ""),
            "assessment": str(item.get("assessment") or ""),
            "weight": int(item.get("weight", 0) or 0),
            "support_weight": int(item.get("support_weight", 0) or 0),
            "support_share": float(item.get("support_share", 0.0) or 0.0),
        }
        for item in rows
        if isinstance(item, dict)
    ]
    out.sort(key=lambda item: (-item["support_weight"], item["evidence_id"]))
    for index, item in enumerate(out, start=1):
        item["support_rank"] = index
    return out


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
        "| Fixture | Target | Top | Sensitivity | Pivotal Support | Pivotal Role | Alignment | Contract |",
        "| --- | --- | --- | --- | ---: | --- | --- | ---: |",
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
                    f"`{row.get('expected_pivotal_support_rank', 0)} / {row.get('expected_pivotal_support_share', 0.0)}`",
                    f"`{row.get('expected_pivotal_evidence_role', '')}`",
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
