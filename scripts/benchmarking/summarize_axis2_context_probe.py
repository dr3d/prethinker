#!/usr/bin/env python3
"""Summarize Axis-2 context probe scores as standalone-vs-stuffed deltas."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RECIPE_JSON = REPO_ROOT / "tmp" / "public_benchmark" / "axis2_probe" / "axis2_context_probe_recipes.json"
DEFAULT_OUT_JSON = REPO_ROOT / "tmp" / "public_benchmark" / "axis2_probe" / "axis2_context_probe_rollup.json"
DEFAULT_OUT_MD = REPO_ROOT / "tmp" / "public_benchmark" / "axis2_probe" / "axis2_context_probe_rollup.md"
DEFAULT_OUT_CSV = REPO_ROOT / "tmp" / "public_benchmark" / "axis2_probe" / "axis2_context_probe_rows.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scored-jsonl", action="append", default=[])
    parser.add_argument("--recipe-json", type=Path, default=DEFAULT_RECIPE_JSON)
    parser.add_argument("--out-json", type=Path, default=DEFAULT_OUT_JSON)
    parser.add_argument("--out-md", type=Path, default=DEFAULT_OUT_MD)
    parser.add_argument("--out-csv", type=Path, default=DEFAULT_OUT_CSV)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows: list[dict[str, Any]] = []
    paths = [_resolve(Path(item)) for item in args.scored_jsonl]
    for path in paths:
        rows.extend(_load_rows(path))
    recipes = _read_json(_resolve(args.recipe_json))
    summary = summarize(rows, recipes=recipes, source_paths=[str(path) for path in paths])
    out_json = _resolve(args.out_json)
    out_md = _resolve(args.out_md)
    out_csv = _resolve(args.out_csv)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    out_md.write_text(render_markdown(summary), encoding="utf-8")
    write_rows_csv(summary, out_csv)
    print(json.dumps({"rows": len(rows), "json": str(out_json), "markdown": str(out_md), "csv": str(out_csv)}, indent=2))
    return 0


def summarize(
    rows: list[dict[str, Any]],
    *,
    recipes: dict[str, Any],
    source_paths: list[str] | None = None,
) -> dict[str, Any]:
    recipe_map = {str(item.get("assembly_id", "")): item for item in recipes.get("recipes", []) if isinstance(item, dict)}
    enriched = [_enrich_row(row, recipe_map) for row in rows]
    model_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in enriched:
        model_rows[str(row.get("model", ""))].append(row)
    models = [summarize_model(model, items) for model, items in sorted(model_rows.items())]
    return {
        "schema_version": "axis2_context_probe_rollup_v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source_paths": source_paths or [],
        "target_fixture": recipes.get("target_fixture", ""),
        "row_count": len(enriched),
        "models": models,
    }


def summarize_model(model: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_condition = _group(rows, "axis2_condition")
    condition_summaries = [_summarize_group(name, items) for name, items in sorted(by_condition.items())]
    baseline = next((item for item in condition_summaries if item["name"] == "standalone"), None)
    baseline_rate = float((baseline or {}).get("exact_rate_judged", 0.0) or 0.0)
    deltas = [
        {
            **item,
            "delta_from_standalone_exact_judged": round(float(item.get("exact_rate_judged", 0.0) or 0.0) - baseline_rate, 4),
        }
        for item in condition_summaries
    ]
    categories = _summarize_condition_categories(rows, baseline_condition="standalone")
    flips = _summarize_flips(rows)
    return {
        "model": model,
        "micro": _summarize_group("all", rows),
        "conditions": deltas,
        "categories": categories,
        "question_flips": flips,
    }


def _enrich_row(row: dict[str, Any], recipe_map: dict[str, dict[str, Any]]) -> dict[str, Any]:
    recipe = recipe_map.get(str(row.get("fixture", "")), {})
    return {
        **row,
        "axis2_condition": recipe.get("condition", row.get("axis2_condition", "")),
        "axis2_target_position": recipe.get("target_position", ""),
        "axis2_ordered_fixtures": recipe.get("ordered_fixtures", []),
        "axis2_source_tokens": recipe.get("approx_prompt_tokens_source_only", ""),
    }


def _summarize_condition_categories(rows: list[dict[str, Any]], *, baseline_condition: str) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row.get("axis2_condition", "")), str(row.get("category", "") or "uncategorized"))].append(row)
    summaries = []
    baseline_rates = {
        category: _summarize_group(category, items)["exact_rate_judged"]
        for (condition, category), items in grouped.items()
        if condition == baseline_condition
    }
    for (condition, category), items in sorted(grouped.items()):
        item = _summarize_group(category, items)
        base = float(baseline_rates.get(category, 0.0) or 0.0)
        summaries.append(
            {
                "condition": condition,
                "category": category,
                **item,
                "delta_from_standalone_exact_judged": round(float(item.get("exact_rate_judged", 0.0) or 0.0) - base, 4),
            }
        )
    return summaries


def _summarize_flips(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get("question_id", ""))].append(row)
    flips: list[dict[str, Any]] = []
    for question_id, items in sorted(grouped.items()):
        by_condition = _group(items, "axis2_condition")
        standalone = by_condition.get("standalone", [])
        if not standalone:
            continue
        base_rate = _summarize_group("standalone", standalone)["exact_rate_judged"]
        for condition, condition_rows in sorted(by_condition.items()):
            if condition == "standalone":
                continue
            item = _summarize_group(condition, condition_rows)
            delta = round(float(item["exact_rate_judged"]) - float(base_rate), 4)
            if delta != 0:
                flips.append(
                    {
                        "question_id": question_id,
                        "category": str(items[0].get("category", "") or "uncategorized"),
                        "condition": condition,
                        "standalone_exact_rate_judged": base_rate,
                        "condition_exact_rate_judged": item["exact_rate_judged"],
                        "delta": delta,
                        "condition_counts": item["verdict_counts"],
                    }
                )
    return flips


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
        "exact_plus_partial_rate_judged": round(exact_partial / judged, 4) if judged else 0.0,
    }


def render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Axis-2 Context Probe Rollup",
        "",
        f"- Generated UTC: `{summary.get('generated_utc', '')}`",
        f"- Target fixture: `{summary.get('target_fixture', '')}`",
        f"- Scored run rows: `{summary.get('row_count', 0)}`",
        "",
    ]
    for model in summary.get("models", []):
        lines.extend(_render_model(model))
    return "\n".join(lines)


def _render_model(model: dict[str, Any]) -> list[str]:
    lines = [
        f"## {model.get('model', '')}",
        "",
        "| Condition | Rows | Judged | Exact Judged | Exact+Partial Judged | Delta vs Standalone | Counts |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for item in model.get("conditions", []):
        lines.append(
            f"| `{item.get('name', '')}` | {item.get('rows', 0)} | {item.get('judged_rows', 0)} | "
            f"{float(item.get('exact_rate_judged', 0.0) or 0.0):.4f} | "
            f"{float(item.get('exact_plus_partial_rate_judged', 0.0) or 0.0):.4f} | "
            f"{float(item.get('delta_from_standalone_exact_judged', 0.0) or 0.0):+.4f} | "
            f"`{item.get('verdict_counts', {})}` |"
        )
    flips = model.get("question_flips", [])
    lines.extend(["", f"- Questions with nonzero condition deltas: `{len(flips)}`", ""])
    if flips:
        lines.extend(
            [
                "### Largest Question Deltas",
                "",
                "| Question | Category | Condition | Standalone | Condition | Delta | Counts |",
                "| --- | --- | --- | ---: | ---: | ---: | --- |",
            ]
        )
        for flip in sorted(flips, key=lambda item: float(item.get("delta", 0.0)))[:20]:
            lines.append(
                f"| `{flip.get('question_id', '')}` | `{flip.get('category', '')}` | `{flip.get('condition', '')}` | "
                f"{float(flip.get('standalone_exact_rate_judged', 0.0) or 0.0):.4f} | "
                f"{float(flip.get('condition_exact_rate_judged', 0.0) or 0.0):.4f} | "
                f"{float(flip.get('delta', 0.0) or 0.0):+.4f} | `{flip.get('condition_counts', {})}` |"
            )
        lines.append("")
    return lines


def write_rows_csv(summary: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "model",
        "question_id",
        "category",
        "condition",
        "standalone_exact_rate_judged",
        "condition_exact_rate_judged",
        "delta",
        "condition_counts",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for model in summary.get("models", []):
            for flip in model.get("question_flips", []):
                writer.writerow(
                    {
                        "model": model.get("model", ""),
                        "condition_counts": json.dumps(flip.get("condition_counts", {}), sort_keys=True),
                        **{key: flip.get(key, "") for key in fieldnames if key not in {"model", "condition_counts"}},
                    }
                )


def _group(rows: list[dict[str, Any]], key: str) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get(key, ""))].append(row)
    return grouped


def _verdict(row: dict[str, Any]) -> str:
    judge = row.get("reference_judge") if isinstance(row.get("reference_judge"), dict) else {}
    return str(judge.get("verdict") or "not_judged")


def _load_rows(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else (REPO_ROOT / path).resolve()


if __name__ == "__main__":
    raise SystemExit(main())
