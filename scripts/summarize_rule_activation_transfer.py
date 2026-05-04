#!/usr/bin/env python3
"""Summarize rule-activation transfer across story-world comparison packs.

This is an after-the-fact structured-artifact report. It reads mode comparison
JSONs produced by `run_rule_activation_mode_pack.py`; it does not read source
prose, gold KBs, strategy files, QA reference answers, or rerun selection.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = REPO_ROOT / "tmp" / "rule_activation_transfer"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.semantic_struggle import assess_semantic_progress  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--comparison",
        action="append",
        required=True,
        help="Comparison artifact in the form label=path/to/mode_comparison.json.",
    )
    parser.add_argument(
        "--selector",
        action="append",
        default=[],
        help="Optional selector artifact in the form label=path/to/selector.json for after-the-fact governor compliance scoring.",
    )
    parser.add_argument("--label", default="story_world_rule_activation_transfer")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    comparisons = [_load_comparison(spec) for spec in args.comparison]
    selectors = [_load_selector(spec) for spec in args.selector]
    report = build_report(
        comparisons=comparisons,
        selectors=selectors,
        label=str(args.label or "rule_activation_transfer"),
    )
    out_dir = args.out_dir if args.out_dir.is_absolute() else (REPO_ROOT / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = _slug(str(args.label or "rule_activation_transfer"))
    out_json = out_dir / f"{slug}.json"
    out_md = out_dir / f"{slug}.md"
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    out_md.write_text(render_markdown(report), encoding="utf-8")
    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")
    print(json.dumps(report["aggregate"], sort_keys=True))
    return 0


def build_report(
    *,
    comparisons: list[dict[str, Any]],
    label: str,
    selectors: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    fixture_summaries: list[dict[str, Any]] = []
    frontier_rows: list[dict[str, Any]] = []
    aggregate_best_counts: Counter[str] = Counter()
    aggregate_mode_best_counts: Counter[str] = Counter()
    aggregate_governor_counts: Counter[str] = Counter()
    aggregate_selector_compliance_counts: Counter[str] = Counter()
    totals = Counter()
    selector_index = _selector_index(selectors or [])

    for comparison in comparisons:
        record = comparison.get("record", {}) if isinstance(comparison.get("record"), dict) else {}
        groups = record.get("groups", []) if isinstance(record.get("groups"), list) else []
        for group in groups:
            if not isinstance(group, dict):
                continue
            fixture = _summarize_group(
                label=str(comparison.get("label", "")),
                path=str(comparison.get("path", "")),
                group=group,
                selector_rows=selector_index.get(str(group.get("name", comparison.get("label", ""))), {}),
            )
            fixture_summaries.append(fixture)
            totals["row_count"] += int(fixture.get("row_count", 0))
            totals["volatile_row_count"] += int(fixture.get("volatile_row_count", 0))
            totals["baseline_rescue_count"] += int(fixture.get("baseline_rescue_count", 0))
            totals["baseline_regression_count"] += int(fixture.get("baseline_regression_count", 0))
            for verdict, count in fixture.get("perfect_selector_counts", {}).items():
                aggregate_best_counts[str(verdict)] += int(count)
            for mode, count in fixture.get("best_label_counts", {}).items():
                aggregate_mode_best_counts[str(mode)] += int(count)
            for action, count in fixture.get("activation_governor_counts", {}).items():
                aggregate_governor_counts[str(action)] += int(count)
            selector_audit = fixture.get("selector_governor_audit", {})
            if isinstance(selector_audit, dict):
                for action, count in selector_audit.get("compliance_counts", {}).items():
                    aggregate_selector_compliance_counts[str(action)] += int(count)
            frontier_rows.extend(fixture.get("frontier_rows", []))

    aggregate = {
        "comparison_count": len(comparisons),
        "fixture_group_count": len(fixture_summaries),
        "row_count": int(totals["row_count"]),
        "volatile_row_count": int(totals["volatile_row_count"]),
        "baseline_rescue_count": int(totals["baseline_rescue_count"]),
        "baseline_regression_count": int(totals["baseline_regression_count"]),
        "perfect_selector_counts": dict(aggregate_best_counts),
        "best_label_counts": dict(aggregate_mode_best_counts),
        "activation_governor_counts": dict(aggregate_governor_counts),
        "selector_governor_compliance_counts": dict(aggregate_selector_compliance_counts),
    }
    aggregate["semantic_progress"] = assess_semantic_progress(
        selector_governor_counts=dict(aggregate_selector_compliance_counts)
    )
    return {
        "schema_version": "rule_activation_transfer_summary_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "label": label,
        "policy": [
            "Reads rule activation mode-comparison artifacts only.",
            "Does not read source prose, gold KBs, oracle strategy files, or QA reference answers.",
            "Does not rerun compilation, query planning, judging, failure classification, or selector calls.",
            "Python summarizes structured verdict deltas and row volatility only.",
        ],
        "aggregate": aggregate,
        "fixtures": fixture_summaries,
        "frontier_rows": frontier_rows,
    }


def render_markdown(report: dict[str, Any]) -> str:
    aggregate = report.get("aggregate", {}) if isinstance(report.get("aggregate"), dict) else {}
    lines = [
        "# Rule Activation Transfer Summary",
        "",
        f"Generated: {report.get('generated_at', '')}",
        "",
        "This report summarizes existing story-world rule-activation comparison artifacts.",
        "It does not read source prose, gold KBs, strategy files, or QA reference answers.",
        "",
        "## Aggregate",
        "",
        f"- Fixture groups: `{aggregate.get('fixture_group_count', 0)}`",
        f"- Rows: `{aggregate.get('row_count', 0)}`",
        f"- Volatile rows: `{aggregate.get('volatile_row_count', 0)}`",
        f"- Baseline rescues: `{aggregate.get('baseline_rescue_count', 0)}`",
        f"- Baseline regressions: `{aggregate.get('baseline_regression_count', 0)}`",
        f"- Perfect-selector counts: `{aggregate.get('perfect_selector_counts', {})}`",
        f"- Best-label counts: `{aggregate.get('best_label_counts', {})}`",
        f"- Activation governor targets: `{aggregate.get('activation_governor_counts', {})}`",
        f"- Selector governor compliance: `{aggregate.get('selector_governor_compliance_counts', {})}`",
        f"- Semantic progress risk: `{(aggregate.get('semantic_progress') or {}).get('zombie_risk', '')}`",
        f"- Semantic progress action: `{(aggregate.get('semantic_progress') or {}).get('recommended_action', '')}`",
        "",
        "## Fixture Groups",
        "",
        "| Fixture | Rows | Volatile | Rescues | Regressions | Governor Targets | Selector Compliance |",
        "| --- | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for fixture in report.get("fixtures", []):
        selector_audit = fixture.get("selector_governor_audit", {})
        compliance_counts = selector_audit.get("compliance_counts", {}) if isinstance(selector_audit, dict) else {}
        lines.append(
            f"| `{fixture.get('name', '')}` | {fixture.get('row_count', 0)} | "
            f"{fixture.get('volatile_row_count', 0)} | {fixture.get('baseline_rescue_count', 0)} | "
            f"{fixture.get('baseline_regression_count', 0)} | `{fixture.get('activation_governor_counts', {})}` | "
            f"`{compliance_counts}` |"
        )
    lines.extend(
        [
            "",
            "## Frontier Rows",
            "",
            "| Fixture | Row | Signal | Best Verdict | Best Labels | Verdicts |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in report.get("frontier_rows", []):
        lines.append(
            f"| `{row.get('fixture', '')}` | `{row.get('id', '')}` | `{','.join(row.get('signals', []))}` | "
            f"{row.get('best_verdict', '')} | `{','.join(row.get('best_labels', []))}` | "
            f"`{row.get('verdicts', {})}` |"
        )
    selector_misses = _report_selector_misses(report)
    if selector_misses:
        lines.extend(
            [
                "",
                "## Selector Governor Misses",
                "",
                "| Fixture | Row | Target | Selected | Selected Verdict | Best Labels |",
                "| --- | --- | --- | --- | --- | --- |",
            ]
        )
        for miss in selector_misses:
            lines.append(
                f"| `{miss.get('fixture', '')}` | `{miss.get('id', '')}` | `{miss.get('target', '')}` | "
                f"`{miss.get('selected_mode', '')}` | `{miss.get('selected_verdict', '')}` | "
                f"`{','.join(miss.get('best_labels', []))}` |"
            )
    lines.append("")
    return "\n".join(lines)


def _summarize_group(
    *,
    label: str,
    path: str,
    group: dict[str, Any],
    selector_rows: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    rows = group.get("rows", []) if isinstance(group.get("rows"), list) else []
    selector_rows = selector_rows or {}
    best_label_counts: Counter[str] = Counter()
    activation_governor_counts: Counter[str] = Counter()
    selector_compliance_counts: Counter[str] = Counter()
    selector_misses: list[dict[str, Any]] = []
    frontier_rows: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        for best_label in row.get("best_labels", []) if isinstance(row.get("best_labels"), list) else []:
            best_label_counts[str(best_label)] += 1
        signals = _row_signals(row)
        governor = _activation_governor_target(row=row, baseline_label=str(group.get("baseline_label", "")))
        activation_governor_counts[str(governor.get("target", "unknown"))] += 1
        selected_row = selector_rows.get(str(row.get("id", "")))
        if selected_row:
            compliance = _selector_governor_compliance(
                comparison_row=row,
                selector_row=selected_row,
                governor=governor,
                baseline_label=str(group.get("baseline_label", "")),
            )
            selector_compliance_counts[str(compliance.get("result", "unknown"))] += 1
            if not bool(compliance.get("compliant", False)):
                selector_misses.append(compliance)
        if signals:
            frontier_rows.append(
                {
                    "fixture": str(group.get("name", label)),
                    "id": str(row.get("id", "")),
                    "question": str(row.get("question", "")),
                    "signals": signals,
                    "best_verdict": str(row.get("best_verdict", "")),
                    "best_labels": [str(item) for item in row.get("best_labels", [])]
                    if isinstance(row.get("best_labels"), list)
                    else [],
                    "verdicts": row.get("verdicts", {}) if isinstance(row.get("verdicts"), dict) else {},
                    "activation_governor_target": governor,
                    "selector_governor_compliance": _selector_governor_compliance(
                        comparison_row=row,
                        selector_row=selected_row,
                        governor=governor,
                        baseline_label=str(group.get("baseline_label", "")),
                    )
                    if selected_row
                    else {},
                }
            )
    return {
        "label": label,
        "path": path,
        "name": str(group.get("name", label)),
        "baseline_label": str(group.get("baseline_label", "")),
        "labels": [str(item) for item in group.get("labels", [])] if isinstance(group.get("labels"), list) else [],
        "row_count": int(group.get("row_count", len(rows)) or 0),
        "volatile_row_count": sum(1 for row in rows if isinstance(row, dict) and bool(row.get("volatile"))),
        "baseline_rescue_count": int(group.get("baseline_rescue_count", 0) or 0),
        "baseline_regression_count": int(group.get("baseline_regression_count", 0) or 0),
        "mode_counts": group.get("mode_counts", {}) if isinstance(group.get("mode_counts"), dict) else {},
        "perfect_selector_counts": group.get("perfect_selector_counts", {})
        if isinstance(group.get("perfect_selector_counts"), dict)
        else {},
        "best_label_counts": dict(best_label_counts),
        "activation_governor_counts": dict(activation_governor_counts),
        "selector_governor_audit": {
            "selector_row_count": len(selector_rows),
            "scored_row_count": sum(selector_compliance_counts.values()),
            "compliance_counts": dict(selector_compliance_counts),
            "misses": selector_misses[:20],
        },
        "frontier_rows": frontier_rows,
    }


def _row_signals(row: dict[str, Any]) -> list[str]:
    signals: list[str] = []
    if bool(row.get("baseline_rescued")):
        signals.append("baseline_rescued")
    if bool(row.get("baseline_regressed")):
        signals.append("baseline_regressed")
    if bool(row.get("volatile")):
        signals.append("volatile")
    return signals


def _activation_governor_target(*, row: dict[str, Any], baseline_label: str) -> dict[str, Any]:
    verdicts = row.get("verdicts", {}) if isinstance(row.get("verdicts"), dict) else {}
    baseline_verdict = str(verdicts.get(baseline_label, "unknown"))
    best_labels = [str(item) for item in row.get("best_labels", [])] if isinstance(row.get("best_labels"), list) else []
    nonbaseline_best = [label for label in best_labels if label != baseline_label]
    present_verdicts = {str(label): str(verdict) for label, verdict in verdicts.items()}
    unique_verdicts = set(present_verdicts.values())

    if not present_verdicts:
        target = "missing_mode_evidence"
        reason = "No mode verdicts were present in the comparison row."
    elif len(unique_verdicts) == 1:
        target = "stable_any_mode"
        reason = "All compared modes have the same verdict."
    elif baseline_verdict == "exact" and bool(row.get("baseline_regressed")):
        target = "protect_baseline_exact"
        reason = "Baseline is exact and at least one activated mode is worse."
    elif bool(row.get("baseline_rescued")) and nonbaseline_best:
        target = "activate_nonbaseline_rescue"
        reason = "At least one non-baseline mode improves the baseline verdict."
    elif baseline_label in best_labels and bool(row.get("volatile")):
        target = "prefer_baseline_under_volatility"
        reason = "The row is volatile, and baseline remains one of the best modes."
    elif nonbaseline_best:
        target = "candidate_nonbaseline_activation"
        reason = "A non-baseline mode is among the best modes, but the row is not a clean rescue."
    else:
        target = "needs_manual_policy"
        reason = "The comparison row does not fit a simple activation-governor bucket."

    return {
        "target": target,
        "reason": reason,
        "baseline_label": baseline_label,
        "baseline_verdict": baseline_verdict,
        "best_labels": best_labels,
        "nonbaseline_best_labels": nonbaseline_best,
    }


def _selector_governor_compliance(
    *,
    comparison_row: dict[str, Any],
    selector_row: dict[str, Any],
    governor: dict[str, Any],
    baseline_label: str,
) -> dict[str, Any]:
    target = str(governor.get("target", "unknown"))
    selected_mode = str(selector_row.get("selected_mode", ""))
    verdicts = comparison_row.get("verdicts", {}) if isinstance(comparison_row.get("verdicts"), dict) else {}
    selected_verdict = str(verdicts.get(selected_mode, selector_row.get("selected_verdict", "unknown")))
    best_labels = [str(item) for item in comparison_row.get("best_labels", [])] if isinstance(comparison_row.get("best_labels"), list) else []
    nonbaseline_best = [label for label in best_labels if label != baseline_label]
    best_verdict = str(comparison_row.get("best_verdict", "unknown"))

    if target == "stable_any_mode":
        compliant = selected_mode in verdicts
        reason = "stable rows only require choosing a compared mode"
    elif target == "activate_nonbaseline_rescue":
        compliant = selected_mode in nonbaseline_best
        reason = "clean rescue rows should select a best nonbaseline mode"
    elif target == "protect_baseline_exact":
        compliant = selected_verdict == "exact"
        reason = "baseline-exact protection rows should not select a worse verdict"
    elif target == "prefer_baseline_under_volatility":
        compliant = selected_mode == baseline_label
        reason = "volatile rows where baseline is best should prefer baseline"
    elif target == "candidate_nonbaseline_activation":
        compliant = selected_mode in best_labels
        reason = "candidate activation rows should select one of the best modes"
    elif target == "needs_manual_policy":
        compliant = selected_mode in best_labels
        reason = "manual-policy rows are counted compliant only when selected mode is best"
    else:
        compliant = False
        reason = "no compliance rule is defined for this governor target"

    return {
        "id": str(comparison_row.get("id", "")),
        "target": target,
        "compliant": bool(compliant),
        "result": f"{target}_{'pass' if compliant else 'fail'}",
        "reason": reason,
        "selected_mode": selected_mode,
        "selected_verdict": selected_verdict,
        "best_verdict": best_verdict,
        "best_labels": best_labels,
    }


def _selector_index(selectors: list[dict[str, Any]]) -> dict[str, dict[str, dict[str, Any]]]:
    out: dict[str, dict[str, dict[str, Any]]] = {}
    for selector in selectors:
        record = selector.get("record", {}) if isinstance(selector.get("record"), dict) else {}
        group = record.get("group", {}) if isinstance(record.get("group"), dict) else {}
        fixture = str(group.get("name", selector.get("label", "")))
        rows = record.get("rows", []) if isinstance(record.get("rows"), list) else []
        out[fixture] = {
            str(row.get("id", "")): row
            for row in rows
            if isinstance(row, dict) and str(row.get("id", "")).strip()
        }
    return out


def _report_selector_misses(report: dict[str, Any]) -> list[dict[str, Any]]:
    misses: list[dict[str, Any]] = []
    for fixture in report.get("fixtures", []):
        if not isinstance(fixture, dict):
            continue
        fixture_name = str(fixture.get("name", ""))
        selector_audit = fixture.get("selector_governor_audit", {})
        if not isinstance(selector_audit, dict):
            continue
        for miss in selector_audit.get("misses", []):
            if not isinstance(miss, dict):
                continue
            item = dict(miss)
            item["fixture"] = fixture_name
            misses.append(item)
    return misses


def _load_comparison(spec: str) -> dict[str, Any]:
    label, sep, raw_path = str(spec).partition("=")
    if not sep or not label.strip() or not raw_path.strip():
        raise SystemExit(f"invalid --comparison {spec!r}")
    path = Path(raw_path.strip())
    path = path if path.is_absolute() else (REPO_ROOT / path).resolve()
    return {
        "label": label.strip(),
        "path": _display_path(path),
        "record": json.loads(path.read_text(encoding="utf-8-sig")),
    }


def _load_selector(spec: str) -> dict[str, Any]:
    label, sep, raw_path = str(spec).partition("=")
    if not sep or not label.strip() or not raw_path.strip():
        raise SystemExit(f"invalid --selector {spec!r}")
    path = Path(raw_path.strip())
    path = path if path.is_absolute() else (REPO_ROOT / path).resolve()
    return {
        "label": label.strip(),
        "path": _display_path(path),
        "record": json.loads(path.read_text(encoding="utf-8-sig")),
    }


def _display_path(value: Path | str) -> str:
    path = value if isinstance(value, Path) else Path(str(value))
    try:
        return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)
    except ValueError:
        return str(path)


def _slug(value: str) -> str:
    out = "".join(ch.lower() if ch.isalnum() else "-" for ch in str(value or "").strip())
    out = "-".join(part for part in out.split("-") if part)
    return out[:80] or "rule-activation-transfer"


if __name__ == "__main__":
    raise SystemExit(main())
