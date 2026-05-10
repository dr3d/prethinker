#!/usr/bin/env python3
"""Summarize deterministic answer drift in mutation-lab raw outputs.

This is a cheap local-factory scorer. It does not decide exact/partial/miss.
Instead, it compares each mutated answer with the same model's control answer
for the same source fixture and question. Large drift flags rows worth judging
or turning into A/B semantic perturbations.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RECIPE_JSON = REPO_ROOT / "tmp" / "public_benchmark" / "mutation_lab" / "fixture_mutation_lab_recipes.json"
DEFAULT_OUT_JSON = REPO_ROOT / "tmp" / "public_benchmark" / "mutation_lab" / "mutation_lab_drift_summary.json"
DEFAULT_OUT_MD = REPO_ROOT / "tmp" / "public_benchmark" / "mutation_lab" / "mutation_lab_drift_summary.md"
DEFAULT_OUT_CSV = REPO_ROOT / "tmp" / "public_benchmark" / "mutation_lab" / "mutation_lab_drift_rows.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-jsonl", action="append", default=[])
    parser.add_argument("--recipe-json", type=Path, default=DEFAULT_RECIPE_JSON)
    parser.add_argument("--drift-threshold", type=float, default=0.80)
    parser.add_argument("--out-json", type=Path, default=DEFAULT_OUT_JSON)
    parser.add_argument("--out-md", type=Path, default=DEFAULT_OUT_MD)
    parser.add_argument("--out-csv", type=Path, default=DEFAULT_OUT_CSV)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    paths = [_resolve(Path(item)) for item in args.raw_jsonl]
    rows: list[dict[str, Any]] = []
    for path in paths:
        rows.extend(_load_rows(path))
    recipes = _read_json(_resolve(args.recipe_json))
    summary = summarize(rows, recipes=recipes, drift_threshold=float(args.drift_threshold), source_paths=[str(path) for path in paths])
    out_json = _resolve(args.out_json)
    out_md = _resolve(args.out_md)
    out_csv = _resolve(args.out_csv)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    out_md.write_text(render_markdown(summary), encoding="utf-8")
    write_csv(summary, out_csv)
    print(json.dumps({"rows": len(rows), "json": str(out_json), "markdown": str(out_md), "csv": str(out_csv)}, indent=2))
    return 0


def summarize(
    rows: list[dict[str, Any]],
    *,
    recipes: dict[str, Any],
    drift_threshold: float,
    source_paths: list[str] | None = None,
) -> dict[str, Any]:
    recipe_map = {str(item.get("synthetic_fixture", "")): item for item in recipes.get("recipes", []) if isinstance(item, dict)}
    enriched = [_enrich(row, recipe_map) for row in rows]
    control: dict[tuple[str, str, str, int], dict[str, Any]] = {}
    for row in enriched:
        if row.get("mutation_id") == "control":
            key = (str(row.get("model", "")), str(row.get("source_fixture", "")), str(row.get("question_id", "")), int(row.get("run_index", 0) or 0))
            control[key] = row
    drift_rows: list[dict[str, Any]] = []
    for row in enriched:
        if row.get("mutation_id") == "control":
            continue
        key = (str(row.get("model", "")), str(row.get("source_fixture", "")), str(row.get("question_id", "")), int(row.get("run_index", 0) or 0))
        base = control.get(key)
        if not base:
            continue
        similarity = answer_similarity(str(base.get("answer", "")), str(row.get("answer", "")))
        drift_rows.append(
            {
                "model": row.get("model", ""),
                "source_fixture": row.get("source_fixture", ""),
                "synthetic_fixture": row.get("fixture", ""),
                "mutation_id": row.get("mutation_id", ""),
                "mutation_class": row.get("mutation_class", ""),
                "question_id": row.get("question_id", ""),
                "category": row.get("category", ""),
                "run_index": row.get("run_index", 0),
                "similarity": similarity,
                "drift": similarity < drift_threshold,
                "control_answer": base.get("answer", ""),
                "mutated_answer": row.get("answer", ""),
            }
        )
    return {
        "schema_version": "mutation_lab_drift_summary_v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source_paths": source_paths or [],
        "drift_threshold": drift_threshold,
        "row_count": len(drift_rows),
        "models": _summarize_models(drift_rows),
        "drift_rows": drift_rows,
    }


def answer_similarity(left: str, right: str) -> float:
    left_tokens = _tokens(left)
    right_tokens = _tokens(right)
    if not left_tokens and not right_tokens:
        return 1.0
    if not left_tokens or not right_tokens:
        return 0.0
    overlap = len(left_tokens & right_tokens)
    precision = overlap / len(right_tokens)
    recall = overlap / len(left_tokens)
    if precision + recall == 0:
        return 0.0
    return round((2 * precision * recall) / (precision + recall), 4)


def _summarize_models(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_model: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_model[str(row.get("model", ""))].append(row)
    return [_summarize_model(model, items) for model, items in sorted(by_model.items())]


def _summarize_model(model: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "model": model,
        "rows": len(rows),
        "drift_rows": sum(1 for row in rows if row.get("drift")),
        "mean_similarity": round(sum(float(row.get("similarity", 0.0) or 0.0) for row in rows) / len(rows), 4) if rows else 0.0,
        "fixtures": [_summarize_group(name, items) for name, items in sorted(_group(rows, "source_fixture").items())],
        "mutations": [_summarize_group(name, items) for name, items in sorted(_group(rows, "mutation_id").items())],
        "categories": [_summarize_group(name, items) for name, items in sorted(_group(rows, "category").items())],
        "largest_drifts": sorted(rows, key=_row_similarity)[:20],
    }


def _summarize_group(name: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "name": name,
        "rows": len(rows),
        "drift_rows": sum(1 for row in rows if row.get("drift")),
        "mean_similarity": round(sum(float(row.get("similarity", 0.0) or 0.0) for row in rows) / len(rows), 4) if rows else 0.0,
    }


def _row_similarity(row: dict[str, Any]) -> float:
    try:
        return float(row.get("similarity", 1.0))
    except (TypeError, ValueError):
        return 1.0


def render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Mutation Lab Drift Summary",
        "",
        f"- Generated UTC: `{summary.get('generated_utc', '')}`",
        f"- Drift threshold: `{summary.get('drift_threshold', '')}`",
        f"- Compared non-control rows: `{summary.get('row_count', 0)}`",
        "",
    ]
    for model in summary.get("models", []):
        lines.extend(_render_model(model))
    return "\n".join(lines)


def _render_model(model: dict[str, Any]) -> list[str]:
    lines = [
        f"## {model.get('model', '')}",
        "",
        f"- Rows: `{model.get('rows', 0)}`",
        f"- Drift rows: `{model.get('drift_rows', 0)}`",
        f"- Mean similarity: `{model.get('mean_similarity', 0.0)}`",
        "",
        "### Fixtures",
        "",
        "| Fixture | Rows | Drift Rows | Mean Similarity |",
        "| --- | ---: | ---: | ---: |",
    ]
    for item in model.get("fixtures", []):
        lines.append(
            f"| `{item.get('name', '')}` | {item.get('rows', 0)} | {item.get('drift_rows', 0)} | "
            f"{float(item.get('mean_similarity', 0.0) or 0.0):.4f} |"
        )
    lines.extend(
        [
            "",
            "### Mutations",
            "",
            "| Mutation | Rows | Drift Rows | Mean Similarity |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for item in model.get("mutations", []):
        lines.append(
            f"| `{item.get('name', '')}` | {item.get('rows', 0)} | {item.get('drift_rows', 0)} | "
            f"{float(item.get('mean_similarity', 0.0) or 0.0):.4f} |"
        )
    lines.extend(["", "### Largest Drifts", "", "| Fixture | Mutation | Question | Category | Similarity |", "| --- | --- | --- | --- | ---: |"])
    for row in model.get("largest_drifts", [])[:20]:
        lines.append(
            f"| `{row.get('source_fixture', '')}` | `{row.get('mutation_id', '')}` | "
            f"`{row.get('question_id', '')}` | `{row.get('category', '')}` | "
            f"{float(row.get('similarity', 0.0) or 0.0):.4f} |"
        )
    lines.append("")
    return lines


def write_csv(summary: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "model",
        "source_fixture",
        "synthetic_fixture",
        "mutation_id",
        "mutation_class",
        "question_id",
        "category",
        "run_index",
        "similarity",
        "drift",
        "control_answer",
        "mutated_answer",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in summary.get("drift_rows", []):
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def _enrich(row: dict[str, Any], recipe_map: dict[str, dict[str, Any]]) -> dict[str, Any]:
    recipe = recipe_map.get(str(row.get("fixture", "")), {})
    return {
        **row,
        "source_fixture": recipe.get("source_fixture", row.get("mutation_source_fixture", "")),
        "mutation_id": recipe.get("mutation_id", row.get("mutation_id", "")),
        "mutation_class": recipe.get("mutation_class", row.get("mutation_class", "")),
    }


def _tokens(text: str) -> set[str]:
    return {_normalize_token(token) for token in re.findall(r"[a-z0-9]+", str(text or "").casefold())}


def _normalize_token(token: str) -> str:
    number_words = {
        "zero": "0",
        "one": "1",
        "two": "2",
        "three": "3",
        "four": "4",
        "five": "5",
        "six": "6",
        "seven": "7",
        "eight": "8",
        "nine": "9",
        "ten": "10",
        "eleven": "11",
        "twelve": "12",
        "thirteen": "13",
        "fourteen": "14",
        "fifteen": "15",
        "sixteen": "16",
        "seventeen": "17",
        "eighteen": "18",
        "nineteen": "19",
        "twenty": "20",
    }
    return number_words.get(token, token)


def _group(rows: list[dict[str, Any]], key: str) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get(key, ""))].append(row)
    return grouped


def _load_rows(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else (REPO_ROOT / path).resolve()


if __name__ == "__main__":
    raise SystemExit(main())
