#!/usr/bin/env python3
"""Summarize scored direct-frontier pilot outputs.

The summary keeps both micro row-weighted rates and macro fixture-averaged
rates. That prevents 25-row surgical fixtures from disappearing inside 40-row
fixtures while still preserving the true row denominator.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCORED_DIR = REPO_ROOT / "tmp" / "public_benchmark" / "frontier_direct_scored"
DEFAULT_OUT_JSON = REPO_ROOT / "tmp" / "public_benchmark" / "frontier_direct_rollup.json"
DEFAULT_OUT_MD = REPO_ROOT / "tmp" / "public_benchmark" / "frontier_direct_rollup.md"
DEFAULT_OUT_CSV = REPO_ROOT / "tmp" / "public_benchmark" / "frontier_direct_rollup_rows.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scored-jsonl", action="append", default=[])
    parser.add_argument("--scored-dir", type=Path, default=DEFAULT_SCORED_DIR)
    parser.add_argument("--out-json", type=Path, default=DEFAULT_OUT_JSON)
    parser.add_argument("--out-md", type=Path, default=DEFAULT_OUT_MD)
    parser.add_argument("--out-csv", type=Path, default=DEFAULT_OUT_CSV)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    paths = [_resolve(Path(item)) for item in args.scored_jsonl]
    if not paths:
        scored_dir = _resolve(args.scored_dir)
        paths = sorted(scored_dir.glob("*_scored.jsonl"))
    rows: list[dict[str, Any]] = []
    for path in paths:
        rows.extend(_load_rows(path))
    summary = summarize(rows, source_paths=[str(path) for path in paths])
    out_json = _resolve(args.out_json)
    out_md = _resolve(args.out_md)
    out_csv = _resolve(args.out_csv)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(render_markdown(summary), encoding="utf-8")
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    _write_question_csv(summary, out_csv)
    print(json.dumps({"rows": len(rows), "json": str(out_json), "markdown": str(out_md), "csv": str(out_csv)}, indent=2))
    return 0


def summarize(rows: list[dict[str, Any]], *, source_paths: list[str] | None = None) -> dict[str, Any]:
    model_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        model_rows[str(row.get("model", ""))].append(row)
    models = [summarize_model(model, items) for model, items in sorted(model_rows.items())]
    return {
        "schema_version": "frontier_direct_pilot_rollup_v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source_paths": source_paths or [],
        "row_count": len(rows),
        "models": models,
    }


def summarize_model(model: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_fixture = _group(rows, "fixture")
    by_bucket = _group(rows, "bucket")
    by_category = _group(rows, "category", default="uncategorized")
    fixture_summaries = [_summarize_group(name, items) for name, items in sorted(by_fixture.items())]
    bucket_summaries = [_summarize_group(name, items) for name, items in sorted(by_bucket.items())]
    category_summaries = [_summarize_group(name, items) for name, items in sorted(by_category.items())]
    question_summaries = _summarize_questions(rows)
    macro_exact_all = mean([item["exact_rate_all"] for item in fixture_summaries]) if fixture_summaries else 0.0
    macro_exact_judged = mean([item["exact_rate_judged"] for item in fixture_summaries]) if fixture_summaries else 0.0
    return {
        "model": model,
        "micro": _summarize_group("all", rows),
        "macro_fixture_exact_rate_all": round(macro_exact_all, 4),
        "macro_fixture_exact_rate_judged": round(macro_exact_judged, 4),
        "fixtures": fixture_summaries,
        "buckets": bucket_summaries,
        "categories": category_summaries,
        "question_variance": _question_variance(question_summaries),
        "questions": question_summaries,
    }


def _summarize_group(name: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    counts: Counter[str] = Counter(_verdict(row) for row in rows)
    total = len(rows)
    judged = total - int(counts.get("not_judged", 0))
    exact = int(counts.get("exact", 0))
    exact_partial = exact + int(counts.get("partial", 0))
    return {
        "name": name,
        "rows": total,
        "judged_rows": judged,
        "verdict_counts": dict(sorted(counts.items())),
        "exact_rate_all": round(exact / total, 4) if total else 0.0,
        "exact_rate_judged": round(exact / judged, 4) if judged else 0.0,
        "exact_plus_partial_rate_all": round(exact_partial / total, 4) if total else 0.0,
        "exact_plus_partial_rate_judged": round(exact_partial / judged, 4) if judged else 0.0,
    }


def _summarize_questions(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row.get("fixture", "")), str(row.get("question_id", "")))].append(row)
    summaries: list[dict[str, Any]] = []
    for (fixture, question_id), items in sorted(grouped.items()):
        counts: Counter[str] = Counter(_verdict(row) for row in items)
        exact = int(counts.get("exact", 0))
        judged = len(items) - int(counts.get("not_judged", 0))
        summaries.append(
            {
                "fixture": fixture,
                "question_id": question_id,
                "bucket": str(items[0].get("bucket", "")) if items else "",
                "category": str(items[0].get("category", "") or "uncategorized") if items else "",
                "runs": len(items),
                "judged_runs": judged,
                "verdict_counts": dict(sorted(counts.items())),
                "exact_run_rate_all": round(exact / len(items), 4) if items else 0.0,
                "exact_run_rate_judged": round(exact / judged, 4) if judged else 0.0,
            }
        )
    return summaries


def _question_variance(question_summaries: list[dict[str, Any]]) -> dict[str, Any]:
    exact_rates = [float(item.get("exact_run_rate_judged", 0.0) or 0.0) for item in question_summaries]
    stable_exact = sum(1 for item in question_summaries if float(item.get("exact_run_rate_judged", 0.0) or 0.0) == 1.0)
    stable_non_exact = sum(1 for item in question_summaries if float(item.get("exact_run_rate_judged", 0.0) or 0.0) == 0.0)
    mixed = len(question_summaries) - stable_exact - stable_non_exact
    return {
        "questions": len(question_summaries),
        "stable_exact_questions": stable_exact,
        "stable_non_exact_questions": stable_non_exact,
        "mixed_verdict_questions": mixed,
        "mean_question_exact_rate_judged": round(mean(exact_rates), 4) if exact_rates else 0.0,
    }


def _group(rows: list[dict[str, Any]], key: str, *, default: str = "") -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        value = str(row.get(key, "") or default)
        grouped[value].append(row)
    return grouped


def _verdict(row: dict[str, Any]) -> str:
    judge = row.get("reference_judge") if isinstance(row.get("reference_judge"), dict) else {}
    return str(judge.get("verdict") or "not_judged")


def render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Frontier Direct Pilot Rollup",
        "",
        f"- Generated UTC: `{summary.get('generated_utc', '')}`",
        f"- Scored run rows: `{summary.get('row_count', 0)}`",
        "",
        "## Model Summary",
        "",
        "| Model | Rows | Judged | Exact All | Exact Judged | Exact+Partial Judged | Macro Fixture Exact | Mixed Questions |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for model in summary.get("models", []):
        micro = model.get("micro", {})
        variance = model.get("question_variance", {})
        lines.append(
            "| `{model}` | {rows} | {judged} | {exact_all:.4f} | {exact_judged:.4f} | {ep_judged:.4f} | {macro:.4f} | {mixed} |".format(
                model=model.get("model", ""),
                rows=micro.get("rows", 0),
                judged=micro.get("judged_rows", 0),
                exact_all=float(micro.get("exact_rate_all", 0.0) or 0.0),
                exact_judged=float(micro.get("exact_rate_judged", 0.0) or 0.0),
                ep_judged=float(micro.get("exact_plus_partial_rate_judged", 0.0) or 0.0),
                macro=float(model.get("macro_fixture_exact_rate_judged", 0.0) or 0.0),
                mixed=variance.get("mixed_verdict_questions", 0),
            )
        )
    lines.append("")
    for model in summary.get("models", []):
        lines.extend(_render_model_sections(model))
    return "\n".join(lines)


def _render_model_sections(model: dict[str, Any]) -> list[str]:
    lines = [
        f"## {model.get('model', '')}",
        "",
        "### Fixtures",
        "",
        "| Fixture | Rows | Exact Judged | Exact+Partial Judged | Counts |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for item in model.get("fixtures", []):
        lines.append(
            f"| `{item.get('name', '')}` | {item.get('rows', 0)} | "
            f"{float(item.get('exact_rate_judged', 0.0) or 0.0):.4f} | "
            f"{float(item.get('exact_plus_partial_rate_judged', 0.0) or 0.0):.4f} | "
            f"`{item.get('verdict_counts', {})}` |"
        )
    lines.extend(
        [
            "",
            "### Buckets",
            "",
            "| Bucket | Rows | Exact Judged | Exact+Partial Judged | Counts |",
            "| --- | ---: | ---: | ---: | --- |",
        ]
    )
    for item in model.get("buckets", []):
        lines.append(
            f"| `{item.get('name', '')}` | {item.get('rows', 0)} | "
            f"{float(item.get('exact_rate_judged', 0.0) or 0.0):.4f} | "
            f"{float(item.get('exact_plus_partial_rate_judged', 0.0) or 0.0):.4f} | "
            f"`{item.get('verdict_counts', {})}` |"
        )
    lines.append("")
    return lines


def _write_question_csv(summary: dict[str, Any], path: Path) -> None:
    fieldnames = [
        "model",
        "fixture",
        "bucket",
        "category",
        "question_id",
        "runs",
        "judged_runs",
        "exact_run_rate_all",
        "exact_run_rate_judged",
        "verdict_counts",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for model in summary.get("models", []):
            for question in model.get("questions", []):
                writer.writerow(
                    {
                        "model": model.get("model", ""),
                        **{key: question.get(key, "") for key in fieldnames if key != "model"},
                        "verdict_counts": json.dumps(question.get("verdict_counts", {}), sort_keys=True),
                    }
                )


def _load_rows(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else (REPO_ROOT / path).resolve()


if __name__ == "__main__":
    raise SystemExit(main())
