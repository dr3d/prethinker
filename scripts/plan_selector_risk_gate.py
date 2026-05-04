#!/usr/bin/env python3
"""Plan selector activation risk gates from existing selector artifacts.

This is a post-run harness utility. It reads selector JSON artifacts and
optional selector-policy comparison reports. It does not read source prose, gold
KBs, QA reference answers, strategy files, or failure labels, and it does not
rerun selection.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = REPO_ROOT / "tmp" / "selector_risk_gates"
VERDICT_SCORE = {"miss": 0, "partial": 1, "exact": 2, "unknown": -1, "": -1}
SCORE_VERDICT = {-1: "unknown", 0: "miss", 1: "partial", 2: "exact"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-run", required=True, help="Baseline selector run in the form label=path.")
    parser.add_argument("--candidate-run", required=True, help="Candidate selector run in the form label=path.")
    parser.add_argument(
        "--transfer-comparison",
        action="append",
        default=[],
        help="Optional selector-policy comparison JSON used to assess candidate transfer support.",
    )
    parser.add_argument("--label", default="selector_risk_gate")
    parser.add_argument("--out-json", type=Path)
    parser.add_argument("--out-md", type=Path)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    baseline = _load_selector_run(str(args.baseline_run))
    candidate = _load_selector_run(str(args.candidate_run))
    transfer_reports = [_load_json(_resolve(Path(path))) for path in args.transfer_comparison]
    report = build_report(
        baseline=baseline,
        candidate=candidate,
        transfer_reports=transfer_reports,
        label=str(args.label or "selector_risk_gate"),
    )
    out_dir = args.out_dir if args.out_dir.is_absolute() else (REPO_ROOT / args.out_dir).resolve()
    out_json = _resolve(args.out_json) if args.out_json else out_dir / f"{_slug(args.label)}.json"
    out_md = _resolve(args.out_md) if args.out_md else out_dir / f"{_slug(args.label)}.md"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    out_md.write_text(render_markdown(report), encoding="utf-8")
    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")
    print(json.dumps(report["summary"], sort_keys=True))
    return 0


def build_report(
    *,
    baseline: dict[str, Any],
    candidate: dict[str, Any],
    transfer_reports: list[dict[str, Any]] | None = None,
    label: str = "selector_risk_gate",
) -> dict[str, Any]:
    transfer = assess_transfer_support(
        transfer_reports or [],
        candidate_policy=str(candidate.get("selection_policy", "") or candidate.get("label", "")),
    )
    baseline_rows = _rows_by_id(baseline)
    candidate_rows = _rows_by_id(candidate)
    row_ids = sorted(set(baseline_rows) | set(candidate_rows))
    rows = [
        classify_row(
            row_id=row_id,
            baseline_row=baseline_rows.get(row_id, {}),
            candidate_row=candidate_rows.get(row_id, {}),
            transfer_status=str(transfer.get("status", "unmeasured")),
        )
        for row_id in row_ids
    ]
    category_counts = Counter(str(row.get("category", "")) for row in rows)
    baseline_exact_regressions = sum(
        1
        for row in rows
        if row.get("baseline_verdict") == "exact" and _score(str(row.get("candidate_verdict", ""))) < _score("exact")
    )
    summary = {
        "row_count": len(rows),
        "safe_activation_target_count": int(category_counts.get("safe_activation_target", 0)),
        "calibration_activation_target_count": int(category_counts.get("calibration_activation_target", 0)),
        "protect_baseline_target_count": int(category_counts.get("protect_baseline_target", 0)),
        "needs_compile_repair_count": int(category_counts.get("needs_compile_repair", 0)),
        "stable_row_count": int(category_counts.get("stable_no_action", 0)),
        "baseline_exact_regression_count": baseline_exact_regressions,
        "candidate_transfer_status": str(transfer.get("status", "unmeasured")),
        "global_recommendation": _global_recommendation(
            transfer_status=str(transfer.get("status", "unmeasured")),
            category_counts=category_counts,
            baseline_exact_regressions=baseline_exact_regressions,
        ),
    }
    return {
        "schema_version": "selector_risk_gate_plan_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "label": label,
        "policy": [
            "Reads selector-run and selector-policy-comparison artifacts only.",
            "Does not read source prose, gold KBs, oracle strategy files, QA reference answers, or failure labels.",
            "Does not rerun compilation, query planning, judging, failure classification, or selection.",
            "Safe activation requires both row-level rescue and measured transfer support.",
        ],
        "artifacts": {
            "baseline_run": baseline.get("path", ""),
            "candidate_run": candidate.get("path", ""),
            "transfer_comparisons": [report.get("path", "") for report in transfer.get("reports", [])],
        },
        "baseline": _run_header(baseline),
        "candidate": _run_header(candidate),
        "transfer_support": transfer,
        "summary": summary,
        "rows": rows,
    }


def classify_row(
    *,
    row_id: str,
    baseline_row: dict[str, Any],
    candidate_row: dict[str, Any],
    transfer_status: str,
) -> dict[str, Any]:
    baseline_verdict = _selected_verdict(baseline_row)
    candidate_verdict = _selected_verdict(candidate_row)
    best_verdict = _best_verdict(candidate_row, baseline_row)
    delta = _score(candidate_verdict) - _score(baseline_verdict)
    if delta > 0:
        category = "safe_activation_target" if transfer_status == "supported" else "calibration_activation_target"
    elif delta < 0:
        category = "protect_baseline_target"
    elif _score(best_verdict) < _score("exact"):
        category = "needs_compile_repair"
    else:
        category = "stable_no_action"
    return {
        "id": row_id,
        "question": str(candidate_row.get("question") or baseline_row.get("question") or ""),
        "category": category,
        "baseline_selected_mode": str(baseline_row.get("selected_mode", "")),
        "candidate_selected_mode": str(candidate_row.get("selected_mode", "")),
        "baseline_verdict": baseline_verdict,
        "candidate_verdict": candidate_verdict,
        "best_available_verdict": best_verdict,
        "best_available_modes": candidate_row.get("best_labels") or baseline_row.get("best_labels") or [],
        "selector_disagreement": _selector_disagreement(candidate_row),
        "selection_source": str(candidate_row.get("selection_source", "")),
        "structural_candidate": str(candidate_row.get("structural_candidate", "")),
        "risk_reason": _risk_reason(
            category=category,
            baseline_verdict=baseline_verdict,
            candidate_verdict=candidate_verdict,
            best_verdict=best_verdict,
            transfer_status=transfer_status,
            candidate_row=candidate_row,
        ),
    }


def assess_transfer_support(reports: list[dict[str, Any]], *, candidate_policy: str) -> dict[str, Any]:
    report_rows: list[dict[str, Any]] = []
    for report in reports:
        policies = report.get("policy_summaries", []) if isinstance(report.get("policy_summaries"), list) else []
        by_policy = {
            str(row.get("selection_policy", "")): row
            for row in policies
            if isinstance(row, dict) and str(row.get("selection_policy", ""))
        }
        candidate = by_policy.get(candidate_policy)
        if not candidate:
            report_rows.append(
                {
                    "path": str(report.get("_path", "")),
                    "label": str(report.get("label", "")),
                    "status": "missing_candidate_policy",
                    "candidate_policy": candidate_policy,
                }
            )
            continue
        alternatives = [row for policy, row in by_policy.items() if policy != candidate_policy]
        if not alternatives:
            report_rows.append(
                {
                    "path": str(report.get("_path", "")),
                    "label": str(report.get("label", "")),
                    "status": "no_alternatives",
                    "candidate_policy": candidate_policy,
                }
            )
            continue
        candidate_exact = int(candidate.get("selected_exact", 0) or 0)
        candidate_miss = int(candidate.get("selected_miss", 0) or 0)
        best_alt_exact = max(int(row.get("selected_exact", 0) or 0) for row in alternatives)
        best_alt_miss = min(int(row.get("selected_miss", 0) or 0) for row in alternatives)
        supported = candidate_exact >= best_alt_exact and candidate_miss <= best_alt_miss
        report_rows.append(
            {
                "path": str(report.get("_path", "")),
                "label": str(report.get("label", "")),
                "status": "supported" if supported else "weak",
                "candidate_policy": candidate_policy,
                "candidate_exact": candidate_exact,
                "candidate_miss": candidate_miss,
                "best_alternative_exact": best_alt_exact,
                "best_alternative_miss": best_alt_miss,
                "exact_delta_vs_best_alternative": candidate_exact - best_alt_exact,
                "miss_delta_vs_best_alternative": candidate_miss - best_alt_miss,
            }
        )
    measured = [row for row in report_rows if row.get("status") in {"supported", "weak"}]
    if not measured:
        status = "unmeasured"
    elif all(row.get("status") == "supported" for row in measured):
        status = "supported"
    elif any(row.get("status") == "supported" for row in measured):
        status = "mixed"
    else:
        status = "weak"
    return {
        "status": status,
        "candidate_policy": candidate_policy,
        "measured_report_count": len(measured),
        "reports": report_rows,
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report.get("summary", {}) if isinstance(report.get("summary"), dict) else {}
    transfer = report.get("transfer_support", {}) if isinstance(report.get("transfer_support"), dict) else {}
    lines = [
        "# Selector Risk-Gate Plan",
        "",
        f"Generated: {report.get('generated_at', '')}",
        "",
        "This report reads selector artifacts only. It does not read source prose,",
        "gold KBs, QA reference answers, strategy files, or failure labels.",
        "",
        "## Summary",
        "",
        f"- Recommendation: `{summary.get('global_recommendation', '')}`",
        f"- Candidate transfer: `{summary.get('candidate_transfer_status', '')}`",
        f"- Rows: `{summary.get('row_count', 0)}`",
        f"- Safe activation targets: `{summary.get('safe_activation_target_count', 0)}`",
        f"- Calibration activation targets: `{summary.get('calibration_activation_target_count', 0)}`",
        f"- Protect baseline targets: `{summary.get('protect_baseline_target_count', 0)}`",
        f"- Needs compile repair: `{summary.get('needs_compile_repair_count', 0)}`",
        f"- Baseline-exact regressions: `{summary.get('baseline_exact_regression_count', 0)}`",
        "",
        "## Transfer Support",
        "",
        f"- Candidate policy: `{transfer.get('candidate_policy', '')}`",
        f"- Status: `{transfer.get('status', '')}`",
        "",
        "| Report | Status | Exact Delta | Miss Delta |",
        "| --- | --- | ---: | ---: |",
    ]
    for row in transfer.get("reports", []):
        if not isinstance(row, dict):
            continue
        lines.append(
            f"| `{row.get('label') or row.get('path', '')}` | `{row.get('status', '')}` | "
            f"{row.get('exact_delta_vs_best_alternative', '')} | {row.get('miss_delta_vs_best_alternative', '')} |"
        )
    lines.extend(
        [
            "",
            "## Row Gates",
            "",
            "| Row | Category | Baseline | Candidate | Best | Disagreement | Reason |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in report.get("rows", []):
        if not isinstance(row, dict) or row.get("category") == "stable_no_action":
            continue
        reason = str(row.get("risk_reason", "")).replace("|", "/")
        lines.append(
            f"| `{row.get('id', '')}` | `{row.get('category', '')}` | "
            f"`{row.get('baseline_selected_mode', '')}:{row.get('baseline_verdict', '')}` | "
            f"`{row.get('candidate_selected_mode', '')}:{row.get('candidate_verdict', '')}` | "
            f"`{row.get('best_available_verdict', '')}` | `{row.get('selector_disagreement', '')}` | {reason} |"
        )
    lines.append("")
    return "\n".join(lines)


def _global_recommendation(
    *,
    transfer_status: str,
    category_counts: Counter[str],
    baseline_exact_regressions: int,
) -> str:
    if transfer_status in {"weak", "unmeasured"}:
        return "do_not_promote_candidate_policy"
    if baseline_exact_regressions or category_counts.get("protect_baseline_target", 0):
        return "row_gate_required"
    if category_counts.get("safe_activation_target", 0):
        return "candidate_policy_promotable_for_safe_targets"
    if category_counts.get("needs_compile_repair", 0):
        return "compile_repair_before_selector_promotion"
    return "no_selector_change_needed"


def _risk_reason(
    *,
    category: str,
    baseline_verdict: str,
    candidate_verdict: str,
    best_verdict: str,
    transfer_status: str,
    candidate_row: dict[str, Any],
) -> str:
    if category == "safe_activation_target":
        return f"candidate improves {baseline_verdict} to {candidate_verdict} with supported transfer"
    if category == "calibration_activation_target":
        return f"candidate improves {baseline_verdict} to {candidate_verdict}, but transfer is {transfer_status}"
    if category == "protect_baseline_target":
        return f"candidate regresses {baseline_verdict} to {candidate_verdict}"
    if category == "needs_compile_repair":
        return f"best available selector verdict is {best_verdict}; no exact mode is visible"
    disagreement = _selector_disagreement(candidate_row)
    return f"stable under candidate; selector disagreement={disagreement}"


def _selector_disagreement(row: dict[str, Any]) -> str:
    source = str(row.get("selection_source", ""))
    selected = str(row.get("selected_mode", ""))
    structural_candidate = str(row.get("structural_candidate", ""))
    if structural_candidate and selected and structural_candidate != selected:
        return "llm_overrode_structural"
    if source in {"hybrid_structural", "protected_structural", "structural"}:
        return "structural_kept"
    if source in {"hybrid_llm", "protected_llm", "llm"}:
        return "llm_selected_without_structural_disagreement"
    return source or "unknown"


def _run_header(run: dict[str, Any]) -> dict[str, Any]:
    return {
        "label": run.get("label", ""),
        "path": run.get("path", ""),
        "selection_policy": run.get("selection_policy", ""),
        "summary": run.get("summary", {}),
    }


def _load_selector_run(spec: str) -> dict[str, Any]:
    label, sep, raw_path = str(spec).partition("=")
    if not sep or not label.strip() or not raw_path.strip():
        raise SystemExit(f"invalid run spec {spec!r}")
    path = _resolve(Path(raw_path.strip()))
    payload = _load_json(path)
    return {
        "label": label.strip(),
        "path": _display_path(path),
        "selection_policy": str(payload.get("selection_policy", "") or label.strip()),
        "summary": payload.get("summary", {}) if isinstance(payload.get("summary"), dict) else {},
        "rows": payload.get("rows", []) if isinstance(payload.get("rows"), list) else [],
    }


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if isinstance(payload, dict):
        payload.setdefault("_path", _display_path(path))
        return payload
    raise SystemExit(f"expected JSON object: {path}")


def _rows_by_id(run: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(row.get("id", "")): row
        for row in run.get("rows", [])
        if isinstance(row, dict) and str(row.get("id", "")).strip()
    }


def _selected_verdict(row: dict[str, Any]) -> str:
    return str(row.get("selected_verdict", "") or "unknown")


def _best_verdict(*rows: dict[str, Any]) -> str:
    for row in rows:
        value = str(row.get("best_verdict", "") or "")
        if value:
            return value
        verdicts = row.get("mode_verdicts", {}) if isinstance(row.get("mode_verdicts"), dict) else {}
        if verdicts:
            score = max((_score(str(verdict)) for verdict in verdicts.values()), default=-1)
            return SCORE_VERDICT.get(score, "unknown")
    score = max((_score(_selected_verdict(row)) for row in rows if row), default=-1)
    return SCORE_VERDICT.get(score, "unknown")


def _score(verdict: str) -> int:
    return VERDICT_SCORE.get(str(verdict), -1)


def _resolve(path: Path | None) -> Path:
    if path is None:
        return REPO_ROOT
    return path if path.is_absolute() else (REPO_ROOT / path).resolve()


def _display_path(value: Path | str | None) -> str:
    if value is None:
        return ""
    path = value if isinstance(value, Path) else Path(str(value))
    try:
        return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)
    except ValueError:
        return str(path)


def _slug(value: str) -> str:
    out = "".join(ch.lower() if ch.isalnum() else "-" for ch in str(value or "").strip())
    out = "-".join(part for part in out.split("-") if part)
    return out[:80] or "selector-risk-gate"


if __name__ == "__main__":
    raise SystemExit(main())
