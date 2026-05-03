#!/usr/bin/env python3
"""Compare post-ingestion QA mode artifacts row by row.

This is a post-run analysis utility. It reads existing QA artifacts and their
structured judge labels. It does not read source prose, gold KBs, or strategy
files, and it does not rerun compilation, query planning, judging, or failure
classification.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_MD = REPO_ROOT / "docs" / "QUERY_SURFACE_MODE_COMPARISON.md"
DEFAULT_OUT_JSON = REPO_ROOT / "tmp" / "query_surface_mode_comparison.json"
VERDICT_SCORE = {"miss": 0, "partial": 1, "exact": 2}
SCORE_VERDICT = {0: "miss", 1: "partial", 2: "exact"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--group",
        action="append",
        required=True,
        help=(
            "Comparison group in the form name:label=path,label=path. "
            "Example: veridia:baseline=tmp/a.json,narrow=tmp/b.json"
        ),
    )
    parser.add_argument("--out-md", type=Path, default=DEFAULT_OUT_MD)
    parser.add_argument("--out-json", type=Path, default=DEFAULT_OUT_JSON)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    groups = [load_group(spec) for spec in args.group]
    report = build_report(groups)
    out_json = args.out_json if args.out_json.is_absolute() else REPO_ROOT / args.out_json
    out_md = args.out_md if args.out_md.is_absolute() else REPO_ROOT / args.out_md
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    out_md.write_text(render_markdown(report), encoding="utf-8")
    print(f"Wrote {out_md}")
    print(f"Wrote {out_json}")
    return 0


def load_group(spec: str) -> dict[str, Any]:
    name, _, rest = str(spec).partition(":")
    if not name.strip() or not rest.strip():
        raise SystemExit(f"invalid --group {spec!r}")
    artifacts: list[dict[str, Any]] = []
    for part in rest.split(","):
        label, _, raw_path = part.partition("=")
        if not label.strip() or not raw_path.strip():
            raise SystemExit(f"invalid artifact spec {part!r}")
        path = Path(raw_path.strip())
        path = path if path.is_absolute() else REPO_ROOT / path
        artifacts.append({"label": label.strip(), "path": path, "record": read_qa_artifact(path)})
    return {"name": name.strip(), "artifacts": artifacts}


def read_qa_artifact(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict) or not isinstance(payload.get("rows"), list):
        raise SystemExit(f"not a QA artifact with rows: {path}")
    return payload


def build_report(groups: list[dict[str, Any]]) -> dict[str, Any]:
    out_groups = [summarize_group(group) for group in groups]
    aggregate = {
        "row_count": sum(int(group["row_count"]) for group in out_groups),
        "volatile_row_count": sum(int(group["volatile_row_count"]) for group in out_groups),
        "baseline_regression_count": sum(int(group["baseline_regression_count"]) for group in out_groups),
        "baseline_rescue_count": sum(int(group["baseline_rescue_count"]) for group in out_groups),
    }
    return {
        "schema_version": "qa_mode_comparison_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "policy": [
            "Reads existing QA artifacts and structured judge labels only.",
            "Does not read source prose, gold KBs, oracle strategy files, or answer-shaped profile material.",
            "Does not rerun compilation, query planning, judging, or failure classification.",
            "Perfect-selector rows are diagnostic only; they are not a runtime selection policy.",
        ],
        "aggregate": aggregate,
        "groups": out_groups,
    }


def summarize_group(group: dict[str, Any]) -> dict[str, Any]:
    artifacts = group["artifacts"]
    labels = [artifact["label"] for artifact in artifacts]
    rows_by_label = {artifact["label"]: rows_by_id(artifact["record"]) for artifact in artifacts}
    all_ids = sorted(set().union(*(set(rows) for rows in rows_by_label.values())))
    baseline_label = labels[0]
    mode_counts = {
        label: dict(Counter(row_verdict(row) for row in rows_by_label[label].values()))
        for label in labels
    }
    row_summaries: list[dict[str, Any]] = []
    best_counts: Counter[str] = Counter()
    for row_id in all_ids:
        verdicts = {
            label: row_verdict(rows_by_label[label].get(row_id, {}))
            for label in labels
        }
        scores = {label: VERDICT_SCORE.get(verdict, -1) for label, verdict in verdicts.items()}
        best_score = max(scores.values()) if scores else -1
        best_labels = [label for label, score in scores.items() if score == best_score]
        best_verdict = SCORE_VERDICT.get(best_score, "unknown")
        best_counts[best_verdict] += 1
        baseline_score = scores.get(baseline_label, -1)
        volatile = len(set(verdicts.values())) > 1
        baseline_regressed = baseline_score == 2 and any(score < 2 for label, score in scores.items() if label != baseline_label)
        baseline_rescued = baseline_score < 2 and any(score > baseline_score for label, score in scores.items() if label != baseline_label)
        row_summaries.append(
            {
                "id": row_id,
                "question": row_question(rows_by_label, row_id, labels),
                "verdicts": verdicts,
                "best_verdict": best_verdict,
                "best_labels": best_labels,
                "volatile": volatile,
                "baseline_rescued": baseline_rescued,
                "baseline_regressed": baseline_regressed,
            }
        )
    return {
        "name": group["name"],
        "labels": labels,
        "baseline_label": baseline_label,
        "row_count": len(all_ids),
        "mode_counts": mode_counts,
        "perfect_selector_counts": dict(best_counts),
        "volatile_row_count": sum(1 for row in row_summaries if row["volatile"]),
        "baseline_rescue_count": sum(1 for row in row_summaries if row["baseline_rescued"]),
        "baseline_regression_count": sum(1 for row in row_summaries if row["baseline_regressed"]),
        "artifacts": [
            {
                "label": artifact["label"],
                "path": display_path(artifact["path"]),
            }
            for artifact in artifacts
        ],
        "rows": row_summaries,
    }


def display_path(value: Any) -> str:
    path = value if isinstance(value, Path) else Path(str(value))
    try:
        return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)
    except ValueError:
        return str(path)


def rows_by_id(record: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(row.get("id", "")): row for row in record.get("rows", []) if isinstance(row, dict) and str(row.get("id", "")).strip()}


def row_verdict(row: dict[str, Any]) -> str:
    judge = row.get("reference_judge") if isinstance(row.get("reference_judge"), dict) else {}
    return str(judge.get("verdict", "")).strip() or "unknown"


def row_question(rows_by_label: dict[str, dict[str, dict[str, Any]]], row_id: str, labels: list[str]) -> str:
    for label in labels:
        row = rows_by_label[label].get(row_id, {})
        question = str(row.get("utterance", "")).strip()
        if question:
            return question
    return ""


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Query Surface Mode Comparison",
        "",
        f"Generated: {report.get('generated_at', '')}",
        "",
        "This report compares existing post-ingestion QA artifacts. It does not read source prose,",
        "gold KBs, or strategy files, and it does not rerun the compiler, query planner, judge,",
        "or failure classifier.",
        "",
        "## Current Lesson",
        "",
        "Evidence-bundle filtering is not a simple replacement for the baseline query",
        "path. It rescues rows that the baseline under-supports, but it can also perturb",
        "already-correct rows. The next runtime-safe direction is a non-oracle selector",
        "that protects baseline exact-like rows and only activates alternate query modes",
        "when pre-judge signals indicate near-miss risk.",
        "",
        "The diagnostic perfect-selector counts below use judge labels after the fact.",
        "They are an upper-bound research measurement, not a runtime policy.",
        "",
        "## Aggregate",
        "",
    ]
    aggregate = report.get("aggregate", {}) if isinstance(report.get("aggregate"), dict) else {}
    lines.extend(
        [
            f"- Rows compared: `{aggregate.get('row_count', 0)}`",
            f"- Volatile rows: `{aggregate.get('volatile_row_count', 0)}`",
            f"- Baseline rows rescued by an alternate mode: `{aggregate.get('baseline_rescue_count', 0)}`",
            f"- Baseline exact rows regressed by an alternate mode: `{aggregate.get('baseline_regression_count', 0)}`",
            "",
            "## Groups",
            "",
        ]
    )
    for group in report.get("groups", []):
        lines.extend(render_group(group))
    return "\n".join(lines).rstrip() + "\n"


def render_group(group: dict[str, Any]) -> list[str]:
    labels = [str(label) for label in group.get("labels", [])]
    lines = [
        f"### {group.get('name', '')}",
        "",
        f"- Baseline mode: `{group.get('baseline_label', '')}`",
        f"- Rows: `{group.get('row_count', 0)}`",
        f"- Volatile rows: `{group.get('volatile_row_count', 0)}`",
        f"- Baseline rescued rows: `{group.get('baseline_rescue_count', 0)}`",
        f"- Baseline exact regression rows: `{group.get('baseline_regression_count', 0)}`",
        "",
        "| Mode | Exact | Partial | Miss | Unknown |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    mode_counts = group.get("mode_counts", {}) if isinstance(group.get("mode_counts"), dict) else {}
    for label in labels:
        counts = mode_counts.get(label, {}) if isinstance(mode_counts.get(label), dict) else {}
        lines.append(
            f"| `{label}` | {int(counts.get('exact', 0) or 0)} | {int(counts.get('partial', 0) or 0)} | {int(counts.get('miss', 0) or 0)} | {int(counts.get('unknown', 0) or 0)} |"
        )
    best = group.get("perfect_selector_counts", {}) if isinstance(group.get("perfect_selector_counts"), dict) else {}
    lines.extend(
        [
            "",
            f"Diagnostic perfect-selector upper bound: `{int(best.get('exact', 0) or 0)} exact / {int(best.get('partial', 0) or 0)} partial / {int(best.get('miss', 0) or 0)} miss`.",
            "",
            "| Row | Baseline | Best | Mode Verdicts | Note |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    baseline = str(group.get("baseline_label", ""))
    for row in group.get("rows", []):
        if not isinstance(row, dict) or not row.get("volatile"):
            continue
        verdicts = row.get("verdicts", {}) if isinstance(row.get("verdicts"), dict) else {}
        verdict_text = ", ".join(f"{label}:{verdicts.get(label, '')}" for label in labels)
        notes: list[str] = []
        if row.get("baseline_rescued"):
            notes.append("rescued")
        if row.get("baseline_regressed"):
            notes.append("baseline-exact-regression")
        lines.append(
            f"| `{row.get('id', '')}` | {verdicts.get(baseline, '')} | {row.get('best_verdict', '')} via `{','.join(row.get('best_labels', []))}` | {verdict_text} | {', '.join(notes)} |"
        )
    lines.append("")
    return lines


if __name__ == "__main__":
    raise SystemExit(main())
