#!/usr/bin/env python3
"""Roll up judged domain-bootstrap QA JSON artifacts."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qa-json", action="append", required=True, help="Judged domain bootstrap QA JSON artifact.")
    parser.add_argument("--label", action="append", default=[], help="Optional label for the matching --qa-json.")
    parser.add_argument("--out-json", type=Path)
    parser.add_argument("--out-md", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    labels = [str(item) for item in args.label]
    rows = [
        summarize_qa_artifact(Path(path), label=labels[index] if index < len(labels) else "")
        for index, path in enumerate(args.qa_json)
    ]
    scorecard = build_scorecard(rows)
    if args.out_json:
        out_json = _resolve(args.out_json)
        out_json.parent.mkdir(parents=True, exist_ok=True)
        out_json.write_text(json.dumps(scorecard, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    markdown = render_markdown(scorecard)
    if args.out_md:
        out_md = _resolve(args.out_md)
        out_md.parent.mkdir(parents=True, exist_ok=True)
        out_md.write_text(markdown, encoding="utf-8")
    else:
        print(markdown)
    print(json.dumps(scorecard["summary"], sort_keys=True))
    return 0


def summarize_qa_artifact(path: Path, *, label: str = "") -> dict[str, Any]:
    data = _read_json(path)
    summary = data.get("summary") if isinstance(data.get("summary"), dict) else {}
    rows = data.get("rows") if isinstance(data.get("rows"), list) else []
    judge_counts: Counter[str] = Counter()
    failure_counts: Counter[str] = Counter()
    non_exact_rows: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        verdict = _judge_verdict(row)
        if verdict:
            judge_counts.update([verdict])
        failure = row.get("failure_surface") if isinstance(row.get("failure_surface"), dict) else {}
        surface = str(failure.get("surface") or "").strip()
        if surface:
            failure_counts.update([surface])
        if verdict and verdict != "exact":
            non_exact_rows.append(
                {
                    "id": row.get("id"),
                    "verdict": verdict,
                    "failure_surface": surface,
                    "question": row.get("utterance"),
                    "queries": row.get("queries") if isinstance(row.get("queries"), list) else [],
                }
            )
    if not judge_counts and isinstance(summary.get("judge_exact"), int):
        judge_counts = Counter(
            {
                "exact": int(summary.get("judge_exact", 0) or 0),
                "partial": int(summary.get("judge_partial", 0) or 0),
                "miss": int(summary.get("judge_miss", 0) or 0),
            }
        )
    if not failure_counts and isinstance(summary.get("failure_surface_counts"), dict):
        failure_counts = Counter(
            {str(key): int(value or 0) for key, value in summary["failure_surface_counts"].items()}
        )
    return {
        "label": label or _infer_label(path, data),
        "path": str(path),
        "run_json": data.get("run_json"),
        "qa_file": data.get("qa_file"),
        "model": data.get("model"),
        "question_count": int(summary.get("question_count", len(rows)) or 0),
        "judge_counts": dict(sorted(judge_counts.items())),
        "failure_surface_counts": dict(sorted(failure_counts.items())),
        "runtime_load_error_count": int(summary.get("runtime_load_error_count", 0) or 0),
        "write_proposal_rows": int(summary.get("write_proposal_rows", 0) or 0),
        "cache_hits": int(summary.get("cache_hits", 0) or 0),
        "cache_misses": int(summary.get("cache_misses", 0) or 0),
        "non_exact_rows": non_exact_rows,
    }


def build_scorecard(rows: list[dict[str, Any]]) -> dict[str, Any]:
    judge_counts: Counter[str] = Counter()
    failure_counts: Counter[str] = Counter()
    for row in rows:
        judge_counts.update(_counter_from_dict(row.get("judge_counts")))
        failure_counts.update(_counter_from_dict(row.get("failure_surface_counts")))
    question_count = sum(int(row.get("question_count", 0) or 0) for row in rows)
    exact = int(judge_counts.get("exact", 0))
    return {
        "schema_version": "domain_bootstrap_qa_scorecard_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "policy": [
            "Reads judged QA JSON artifacts only.",
            "Does not inspect source prose, answer keys, or compile source text.",
            "Non-exact rows are copied from structured QA fields for triage.",
        ],
        "summary": {
            "artifact_count": len(rows),
            "question_count": question_count,
            "exact_rows": exact,
            "partial_rows": int(judge_counts.get("partial", 0)),
            "miss_rows": int(judge_counts.get("miss", 0)),
            "exact_rate": round(exact / question_count, 4) if question_count else None,
            "judge_counts": dict(sorted(judge_counts.items())),
            "failure_surface_counts": dict(sorted(failure_counts.items())),
            "runtime_load_error_count": sum(int(row.get("runtime_load_error_count", 0) or 0) for row in rows),
            "write_proposal_rows": sum(int(row.get("write_proposal_rows", 0) or 0) for row in rows),
        },
        "artifacts": rows,
    }


def render_markdown(scorecard: dict[str, Any]) -> str:
    summary = scorecard["summary"]
    lines = [
        "# Domain Bootstrap QA Scorecard",
        "",
        f"Generated: {scorecard.get('generated_at', '')}",
        "",
        "## Summary",
        "",
        f"- Artifacts: `{summary['artifact_count']}`",
        f"- Questions: `{summary['question_count']}`",
        f"- Exact / partial / miss: `{summary['exact_rows']}` / `{summary['partial_rows']}` / `{summary['miss_rows']}`",
        f"- Exact rate: `{summary['exact_rate']}`",
        f"- Failure surfaces: `{summary['failure_surface_counts']}`",
        f"- Runtime load errors: `{summary['runtime_load_error_count']}`",
        f"- Write proposal rows: `{summary['write_proposal_rows']}`",
        "",
        "## Artifacts",
        "",
        "| Label | Questions | Exact | Partial | Miss | Failures |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in scorecard["artifacts"]:
        judge = row.get("judge_counts", {}) if isinstance(row.get("judge_counts"), dict) else {}
        failures = row.get("failure_surface_counts", {}) if isinstance(row.get("failure_surface_counts"), dict) else {}
        lines.append(
            f"| `{row.get('label', '')}` | {row.get('question_count', 0)} | "
            f"{judge.get('exact', 0)} | {judge.get('partial', 0)} | {judge.get('miss', 0)} | `{failures}` |"
        )
    lines.append("")
    return "\n".join(lines)


def _read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    return data if isinstance(data, dict) else {}


def _judge_verdict(row: dict[str, Any]) -> str:
    judge = row.get("reference_judge") if isinstance(row.get("reference_judge"), dict) else {}
    return str(judge.get("verdict") or "").strip()


def _infer_label(path: Path, data: dict[str, Any]) -> str:
    qa_file = str(data.get("qa_file") or "").replace("\\", "/")
    if "/datasets/story_worlds/" in qa_file:
        parts = qa_file.split("/datasets/story_worlds/", 1)[1].split("/")
        if parts:
            return parts[0]
    if qa_file.startswith("datasets/story_worlds/"):
        parts = qa_file.split("/")
        if len(parts) > 2:
            return parts[2]
    return path.parent.name or path.stem


def _counter_from_dict(value: Any) -> Counter[str]:
    if not isinstance(value, dict):
        return Counter()
    return Counter({str(key): int(count or 0) for key, count in value.items()})


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


if __name__ == "__main__":
    raise SystemExit(main())
