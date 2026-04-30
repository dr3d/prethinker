#!/usr/bin/env python3
"""Summarize story-world benchmark progress JSONL into graph-friendly tables."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_METRICS = ROOT / "datasets" / "story_worlds" / "otters_clockwork_pie" / "progress_metrics.jsonl"
DEFAULT_OUT_DIR = ROOT / "tmp" / "story_world_progress"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize story-world progress metrics.")
    parser.add_argument("--metrics", type=Path, default=DEFAULT_METRICS)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--stem", default="otters_progress")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    metrics_path = args.metrics if args.metrics.is_absolute() else (ROOT / args.metrics).resolve()
    rows = _load_jsonl(metrics_path)
    out_dir = args.out_dir if args.out_dir.is_absolute() else (ROOT / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    flat_rows = [_flatten_row(row) for row in rows]
    csv_path = out_dir / f"{args.stem}.csv"
    md_path = out_dir / f"{args.stem}.md"
    _write_csv(flat_rows, csv_path)
    _write_markdown(flat_rows, md_path)
    print(json.dumps({"rows": len(rows), "csv": str(csv_path), "markdown": str(md_path)}, indent=2))
    return 0


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{index}: row is not a JSON object")
        rows.append(value)
    return rows


def _flatten_row(row: dict[str, Any]) -> dict[str, Any]:
    compile_row = row.get("compile") if isinstance(row.get("compile"), dict) else {}
    qa_row = row.get("qa_first20") if isinstance(row.get("qa_first20"), dict) else {}
    return {
        "run_id": row.get("run_id", ""),
        "timestamp": row.get("timestamp", ""),
        "mode": row.get("mode", ""),
        "profile_rough_score": compile_row.get("rough_score", ""),
        "candidate_predicates": compile_row.get("candidate_predicates", ""),
        "admitted_ops": compile_row.get("admitted_ops", ""),
        "unique_facts": compile_row.get("unique_facts", ""),
        "signature_recall": compile_row.get("signature_recall", 0.0),
        "signature_precision": compile_row.get("signature_precision", 0.0),
        "qa_exact": qa_row.get("judge_exact", ""),
        "qa_partial": qa_row.get("judge_partial", ""),
        "qa_miss": qa_row.get("judge_miss", ""),
        "qa_exact_rate": qa_row.get("exact_rate", ""),
        "qa_exact_plus_partial_rate": qa_row.get(
            "exact_plus_partial_rate",
            qa_row.get("exact_rate", ""),
        ),
    }


def _write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _write_markdown(rows: list[dict[str, Any]], path: Path) -> None:
    columns = [
        "run_id",
        "profile_rough_score",
        "signature_recall",
        "signature_precision",
        "qa_exact",
        "qa_partial",
        "qa_exact_plus_partial_rate",
        "admitted_ops",
    ]
    lines = [
        "# Story-World Progress Summary",
        "",
        f"- Source rows: `{len(rows)}`",
        "",
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(_format_cell(row.get(column, "")) for column in columns) + " |")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _format_cell(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


if __name__ == "__main__":
    raise SystemExit(main())
