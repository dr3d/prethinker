#!/usr/bin/env python3
"""Extract selected mutation-drift rows into a review table."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DRIFT_JSON = REPO_ROOT / "tmp" / "public_benchmark" / "mutation_lab" / "perception_power_pilot_drift.json"
DEFAULT_OUT_CSV = REPO_ROOT / "tmp" / "public_benchmark" / "mutation_lab" / "perception_power_pilot_triage.csv"
DEFAULT_OUT_MD = REPO_ROOT / "tmp" / "public_benchmark" / "mutation_lab" / "perception_power_pilot_triage.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--drift-json", type=Path, default=DEFAULT_DRIFT_JSON)
    parser.add_argument("--mutation", action="append", default=[])
    parser.add_argument("--question-id", action="append", default=[])
    parser.add_argument("--out-csv", type=Path, default=DEFAULT_OUT_CSV)
    parser.add_argument("--out-md", type=Path, default=DEFAULT_OUT_MD)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = _read_json(_resolve(args.drift_json))
    rows = extract_rows(
        summary,
        mutations=set(args.mutation or ["international_dates"]),
        question_ids=set(args.question_id or ["q025", "q030"]),
    )
    out_csv = _resolve(args.out_csv)
    out_md = _resolve(args.out_md)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    write_csv(rows, out_csv)
    out_md.write_text(render_markdown(rows), encoding="utf-8")
    print(json.dumps({"rows": len(rows), "csv": str(out_csv), "markdown": str(out_md)}, indent=2))
    return 0


def extract_rows(
    summary: dict[str, Any],
    *,
    mutations: set[str],
    question_ids: set[str],
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    oracle_cache: dict[str, dict[str, str]] = {}
    for row in summary.get("drift_rows", []):
        mutation = str(row.get("mutation_id", ""))
        qid = str(row.get("question_id", ""))
        if mutation not in mutations and qid not in question_ids:
            continue
        source_fixture = str(row.get("source_fixture", ""))
        oracle = oracle_cache.setdefault(source_fixture, _load_oracle_answers(source_fixture))
        selected.append(
            {
                "triage_label": "",
                "review_notes": "",
                "model": row.get("model", ""),
                "source_fixture": source_fixture,
                "mutation_id": mutation,
                "question_id": qid,
                "category": row.get("category", ""),
                "similarity": row.get("similarity", ""),
                "reference_answer": oracle.get(qid, ""),
                "control_answer": row.get("control_answer", ""),
                "mutated_answer": row.get("mutated_answer", ""),
            }
        )
    return sorted(selected, key=lambda item: (str(item["question_id"]), str(item["mutation_id"])))


def write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    fieldnames = [
        "triage_label",
        "review_notes",
        "model",
        "source_fixture",
        "mutation_id",
        "question_id",
        "category",
        "similarity",
        "reference_answer",
        "control_answer",
        "mutated_answer",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def render_markdown(rows: list[dict[str, Any]]) -> str:
    lines = [
        "# Perception Drift Triage Table",
        "",
        "Labels to use:",
        "",
        "- harmless answer-shape drift",
        "- semantically equivalent date formatting",
        "- source retrieval focus change",
        "- true correctness loss",
        "- scorer normalization defect",
        "",
        "| Label | Fixture | Question | Mutation | Category | Similarity | Oracle Answer | Control Answer | Mutated Answer | Notes |",
        "| --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "|  | `{source_fixture}` | `{question_id}` | `{mutation_id}` | `{category}` | {similarity} | {reference} | {control} | {mutated} |  |".format(
                source_fixture=row.get("source_fixture", ""),
                question_id=row.get("question_id", ""),
                mutation_id=row.get("mutation_id", ""),
                category=row.get("category", ""),
                similarity=row.get("similarity", ""),
                reference=_cell(row.get("reference_answer", "")),
                control=_cell(row.get("control_answer", "")),
                mutated=_cell(row.get("mutated_answer", "")),
            )
        )
    lines.append("")
    return "\n".join(lines)


def _cell(value: Any) -> str:
    return str(value or "").replace("\n", " ").replace("|", "/")[:260]


def _read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _load_oracle_answers(source_fixture: str) -> dict[str, str]:
    if not source_fixture:
        return {}
    oracle_path = REPO_ROOT / "datasets" / "story_worlds" / source_fixture / "oracle.jsonl"
    if not oracle_path.exists():
        return {}
    answers: dict[str, str] = {}
    with oracle_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            qid = str(row.get("id", ""))
            answer = str(row.get("reference_answer", ""))
            if qid:
                answers[qid] = answer
    return answers


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else (REPO_ROOT / path).resolve()


if __name__ == "__main__":
    raise SystemExit(main())
