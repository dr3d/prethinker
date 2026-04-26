#!/usr/bin/env python3
"""Summarize local Semantic IR guardrail A/B JSONL runs into a model matrix."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_GLOB = REPO_ROOT / "tmp" / "guardrail_dependency_ab" / "*.jsonl"


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _scenario_group(scenario_id: str) -> str:
    value = str(scenario_id or "").strip()
    if value.startswith("weak_"):
        return "weak_edges"
    if value.startswith("edge_"):
        return "edge"
    if value.startswith("rule_") or value.startswith("mutation_"):
        return "rule_mutation"
    if value.startswith("silverton_noisy_"):
        return "silverton_noisy"
    if value.startswith("silverton_"):
        return "silverton"
    return "mixed"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if not text:
                continue
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                records.append(parsed)
    return records


def summarize_run(path: Path) -> dict[str, Any]:
    records = load_jsonl(path)
    if not records:
        return {
            "file": path.name,
            "model": "",
            "scenario_group": "empty",
            "runs": 0,
            "semantic_decision_ok": 0,
            "semantic_avg_score": 0.0,
            "legacy_decision_ok": 0,
            "legacy_avg_score": 0.0,
            "semantic_non_mapper_rescues": 0,
        }
    first = records[0]
    semantic_scores = [
        row.get("semantic_ir", {}).get("score", {})
        for row in records
        if isinstance(row.get("semantic_ir"), dict)
    ]
    legacy_scores = [
        row.get("legacy", {}).get("score", {})
        for row in records
        if isinstance(row.get("legacy"), dict)
    ]
    groups = sorted({_scenario_group(str(row.get("scenario_id", ""))) for row in records})
    semantic_rescues = 0
    for row in records:
        semantic = row.get("semantic_ir", {}) if isinstance(row.get("semantic_ir"), dict) else {}
        try:
            semantic_rescues += int(semantic.get("non_mapper_parse_rescue_count", 0) or 0)
        except Exception:
            pass
    return {
        "file": path.name,
        "model": str(first.get("semantic_model", "")).strip(),
        "scenario_group": groups[0] if len(groups) == 1 else "mixed",
        "runs": len(records),
        "semantic_decision_ok": sum(1 for score in semantic_scores if bool(score.get("decision_ok"))),
        "semantic_avg_score": round(
            sum(_safe_float(score.get("rough_score")) for score in semantic_scores)
            / max(1, len(semantic_scores)),
            3,
        ),
        "legacy_decision_ok": sum(1 for score in legacy_scores if bool(score.get("decision_ok"))),
        "legacy_avg_score": round(
            sum(_safe_float(score.get("rough_score")) for score in legacy_scores)
            / max(1, len(legacy_scores)),
            3,
        ),
        "semantic_non_mapper_rescues": semantic_rescues,
    }


def format_markdown(summaries: list[dict[str, Any]]) -> str:
    rows = sorted(
        summaries,
        key=lambda row: (
            str(row.get("scenario_group", "")),
            str(row.get("model", "")),
            str(row.get("file", "")),
        ),
    )
    lines = [
        "# Semantic IR Model Matrix Summary",
        "",
        "| Group | Model | Runs | Semantic OK | Semantic Avg | Legacy OK | Legacy Avg | Semantic Non-Mapper Rescues | File |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        runs = int(row.get("runs", 0) or 0)
        lines.append(
            "| {group} | `{model}` | {runs} | {semantic_ok}/{runs} | {semantic_avg:.3f} | "
            "{legacy_ok}/{runs} | {legacy_avg:.3f} | {rescues} | `{file}` |".format(
                group=row.get("scenario_group", ""),
                model=row.get("model", ""),
                runs=runs,
                semantic_ok=int(row.get("semantic_decision_ok", 0) or 0),
                semantic_avg=_safe_float(row.get("semantic_avg_score")),
                legacy_ok=int(row.get("legacy_decision_ok", 0) or 0),
                legacy_avg=_safe_float(row.get("legacy_avg_score")),
                rescues=int(row.get("semantic_non_mapper_rescues", 0) or 0),
                file=row.get("file", ""),
            )
        )
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="*", help="Guardrail A/B JSONL files. Defaults to tmp/guardrail_dependency_ab/*.jsonl")
    parser.add_argument("--out", default="", help="Optional markdown output path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    paths = [Path(item) for item in args.files]
    if not paths:
        paths = sorted(DEFAULT_INPUT_GLOB.parent.glob(DEFAULT_INPUT_GLOB.name))
    summaries = [summarize_run(path) for path in paths if path.exists()]
    markdown = format_markdown(summaries)
    out_path = Path(str(args.out).strip()) if str(args.out).strip() else None
    if out_path is not None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(markdown, encoding="utf-8")
    else:
        print(markdown, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
