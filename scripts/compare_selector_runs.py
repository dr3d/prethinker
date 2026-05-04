#!/usr/bin/env python3
"""Compare selector-run artifacts produced by QA mode selection harnesses.

This is a post-run analysis utility. It reads selector JSON artifacts and their
after-the-fact selected verdict metrics. It does not read source prose, gold
KBs, QA reference answers, or strategy files, and it does not rerun selection.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = REPO_ROOT / "tmp" / "selector_policy_comparisons"
VERDICT_SCORE = {"miss": 0, "partial": 1, "exact": 2, "unknown": -1}
SCORE_VERDICT = {0: "miss", 1: "partial", 2: "exact", -1: "unknown"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run",
        action="append",
        required=True,
        help="Selector run in the form label=path/to/selector.json.",
    )
    parser.add_argument("--label", default="selector_policy_comparison")
    parser.add_argument(
        "--row-scope",
        choices=["group", "id"],
        default="group",
        help="Use group-prefixed row ids for mixed-fixture comparisons, or bare ids for same-fixture policy comparisons.",
    )
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    runs = [_load_run(spec) for spec in args.run]
    report = build_report(runs=runs, label=str(args.label or "selector_policy_comparison"), row_scope=str(args.row_scope))
    out_dir = args.out_dir if args.out_dir.is_absolute() else (REPO_ROOT / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = _slug(str(args.label or "selector_policy_comparison"))
    out_json = out_dir / f"{slug}.json"
    out_md = out_dir / f"{slug}.md"
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    out_md.write_text(render_markdown(report), encoding="utf-8")
    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")
    print(json.dumps(report["aggregate"], sort_keys=True))
    return 0


def build_report(*, runs: list[dict[str, Any]], label: str, row_scope: str = "group") -> dict[str, Any]:
    rows_by_run = {
        run["label"]: {
            _row_key(run, row, row_scope=row_scope): row
            for row in run.get("rows", [])
            if isinstance(row, dict) and str(row.get("id", "")).strip()
        }
        for run in runs
    }
    all_ids = sorted(set().union(*(set(rows) for rows in rows_by_run.values()))) if rows_by_run else []
    row_summaries: list[dict[str, Any]] = []
    best_selector_counts: Counter[str] = Counter()
    for row_id in all_ids:
        verdicts = {
            run_label: str(rows[row_id].get("selected_verdict", "unknown"))
            for run_label, rows in rows_by_run.items()
            if row_id in rows
        }
        scores = {run_label: VERDICT_SCORE.get(verdict, -1) for run_label, verdict in verdicts.items()}
        best_score = max(scores.values()) if scores else -1
        best_labels = [run_label for run_label, score in scores.items() if score == best_score]
        best_verdict = SCORE_VERDICT.get(best_score, "unknown")
        best_selector_counts[best_verdict] += 1
        row_summaries.append(
            {
                "id": row_id,
                "question": _first_question(rows_by_run, row_id),
                "selected_verdicts": verdicts,
                "best_selector_verdict": best_verdict,
                "best_selector_labels": best_labels,
                "volatile": len(set(verdicts.values())) > 1,
            }
        )

    run_summaries = [_summarize_run(run) for run in runs]
    policy_summaries = _summarize_policies(runs)
    return {
        "schema_version": "selector_policy_comparison_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "label": label,
        "row_scope": row_scope,
        "policy": [
            "Reads selector-run JSON artifacts only.",
            "Does not read source prose, gold KBs, oracle strategy files, or QA reference answers.",
            "Does not rerun compilation, query planning, judging, failure classification, or selection.",
        ],
        "aggregate": {
            "run_count": len(runs),
            "policy_count": len(policy_summaries),
            "row_count": len(all_ids),
            "volatile_row_count": sum(1 for row in row_summaries if row["volatile"]),
            "best_selector_counts": dict(best_selector_counts),
        },
        "policy_summaries": policy_summaries,
        "runs": run_summaries,
        "rows": row_summaries,
    }


def render_markdown(report: dict[str, Any]) -> str:
    aggregate = report.get("aggregate", {}) if isinstance(report.get("aggregate"), dict) else {}
    lines = [
        "# Selector Policy Comparison",
        "",
        f"Generated: {report.get('generated_at', '')}",
        "",
        "This report compares existing selector-run artifacts. It does not read source prose,",
        "gold KBs, strategy files, or QA reference answers, and it does not rerun selection.",
        "",
        "## Aggregate",
        "",
        f"- Row scope: `{report.get('row_scope', '')}`",
        f"- Runs: `{aggregate.get('run_count', 0)}`",
        f"- Policies: `{aggregate.get('policy_count', 0)}`",
        f"- Rows: `{aggregate.get('row_count', 0)}`",
        f"- Volatile rows: `{aggregate.get('volatile_row_count', 0)}`",
        f"- Best selector verdict counts: `{aggregate.get('best_selector_counts', {})}`",
        "",
        "## Policy Totals",
        "",
        "| Policy | Runs | Rows | Best Rows | Exact | Partial | Miss | Errors |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for policy in report.get("policy_summaries", []):
        if not isinstance(policy, dict):
            continue
        lines.append(
            f"| `{policy.get('selection_policy', '')}` | {policy.get('run_count', 0)} | "
            f"{policy.get('row_count', 0)} | {policy.get('selected_best_count', 0)} | "
            f"{policy.get('selected_exact', 0)} | {policy.get('selected_partial', 0)} | "
            f"{policy.get('selected_miss', 0)} | {policy.get('selector_error_count', 0)} |"
        )
    lines.extend(
        [
            "",
        "## Runs",
        "",
        "| Run | Policy | Best Rows | Exact | Partial | Miss | Errors | Artifact |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for run in report.get("runs", []):
        summary = run.get("summary", {}) if isinstance(run.get("summary"), dict) else {}
        lines.append(
            f"| `{run.get('label', '')}` | `{run.get('selection_policy', '')}` | {summary.get('selected_best_count', 0)} | {summary.get('selected_exact', 0)} | {summary.get('selected_partial', 0)} | {summary.get('selected_miss', 0)} | {summary.get('selector_error_count', 0)} | `{run.get('path', '')}` |"
        )
    lines.extend(["", "## Volatile Rows", "", "| Row | Best Selector Verdict | Best Selector Runs | Selected Verdicts |", "| --- | --- | --- | --- |"])
    for row in report.get("rows", []):
        if not isinstance(row, dict) or not row.get("volatile"):
            continue
        verdicts = row.get("selected_verdicts", {}) if isinstance(row.get("selected_verdicts"), dict) else {}
        verdict_text = ", ".join(f"{label}:{verdict}" for label, verdict in verdicts.items())
        lines.append(
            f"| `{row.get('id', '')}` | {row.get('best_selector_verdict', '')} | `{','.join(row.get('best_selector_labels', []))}` | {verdict_text} |"
        )
    lines.append("")
    return "\n".join(lines)


def _load_run(spec: str) -> dict[str, Any]:
    label, sep, raw_path = str(spec).partition("=")
    if not sep or not label.strip() or not raw_path.strip():
        raise SystemExit(f"invalid --run {spec!r}")
    path = Path(raw_path.strip())
    path = path if path.is_absolute() else (REPO_ROOT / path).resolve()
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    return {
        "label": label.strip(),
        "path": _display_path(path),
        "record": payload,
        "rows": payload.get("rows", []) if isinstance(payload.get("rows"), list) else [],
        "summary": payload.get("summary", {}) if isinstance(payload.get("summary"), dict) else {},
        "selection_policy": payload.get("selection_policy", ""),
        "group_name": str((payload.get("group") or {}).get("name", "")) if isinstance(payload.get("group"), dict) else "",
    }


def _summarize_run(run: dict[str, Any]) -> dict[str, Any]:
    return {
        "label": run.get("label", ""),
        "path": run.get("path", ""),
        "selection_policy": run.get("selection_policy", ""),
        "summary": run.get("summary", {}),
    }


def _summarize_policies(runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for run in runs:
        policy = str(run.get("selection_policy", "") or run.get("label", "") or "unknown")
        grouped.setdefault(policy, []).append(run)
    out: list[dict[str, Any]] = []
    for policy in sorted(grouped):
        members = grouped[policy]
        summaries = [run.get("summary", {}) if isinstance(run.get("summary"), dict) else {} for run in members]
        out.append(
            {
                "selection_policy": policy,
                "run_count": len(members),
                "row_count": sum(int(summary.get("row_count", 0) or len(run.get("rows", []))) for run, summary in zip(members, summaries)),
                "selected_best_count": sum(int(summary.get("selected_best_count", 0) or 0) for summary in summaries),
                "selected_exact": sum(int(summary.get("selected_exact", 0) or 0) for summary in summaries),
                "selected_partial": sum(int(summary.get("selected_partial", 0) or 0) for summary in summaries),
                "selected_miss": sum(int(summary.get("selected_miss", 0) or 0) for summary in summaries),
                "selector_error_count": sum(int(summary.get("selector_error_count", 0) or 0) for summary in summaries),
            }
        )
    return out


def _first_question(rows_by_run: dict[str, dict[str, dict[str, Any]]], row_id: str) -> str:
    for rows in rows_by_run.values():
        question = str(rows.get(row_id, {}).get("question", "")).strip()
        if question:
            return question
    return ""


def _row_key(run: dict[str, Any], row: dict[str, Any], *, row_scope: str) -> str:
    row_id = str(row.get("id", "")).strip()
    if row_scope == "id":
        return row_id
    group_name = str(run.get("group_name", "")).strip()
    if group_name:
        return f"{group_name}:{row_id}"
    return row_id


def _display_path(value: Path | str) -> str:
    path = value if isinstance(value, Path) else Path(str(value))
    try:
        return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)
    except ValueError:
        return str(path)


def _slug(value: str) -> str:
    out = "".join(ch.lower() if ch.isalnum() else "-" for ch in str(value or "").strip())
    out = "-".join(part for part in out.split("-") if part)
    return out[:80] or "selector-policy-comparison"


if __name__ == "__main__":
    raise SystemExit(main())
