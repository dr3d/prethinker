#!/usr/bin/env python3
"""Compare domain bootstrap compile artifacts without reading source prose."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


PREDICATE_RE = re.compile(r"^\s*([a-z][A-Za-z0-9_]*)\s*\(")


def _read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    return data if isinstance(data, dict) else {}


def _predicate_signature(row: Any) -> str:
    if isinstance(row, dict):
        return str(row.get("signature") or "").strip()
    return ""


def _repeated_structure_signature(row: Any) -> str:
    if not isinstance(row, dict):
        return ""
    record = str(row.get("record") or "").strip()
    properties = row.get("properties") if isinstance(row.get("properties"), list) else []
    props = ",".join(str(item).strip() for item in properties if str(item).strip())
    name = str(row.get("name") or row.get("structure_id") or row.get("id") or "").strip()
    return f"{name}|{record}|{props}"


def _predicate_name(fact: str) -> str:
    match = PREDICATE_RE.match(str(fact))
    return match.group(1) if match else ""


def summarize_compile(path: Path, focus_predicates: set[str]) -> dict[str, Any]:
    data = _read_json(path)
    parsed = data.get("parsed") if isinstance(data.get("parsed"), dict) else {}
    score = data.get("score") if isinstance(data.get("score"), dict) else {}
    source_compile = data.get("source_compile") if isinstance(data.get("source_compile"), dict) else {}
    health = source_compile.get("compile_health") if isinstance(source_compile.get("compile_health"), dict) else {}
    facts = source_compile.get("facts") if isinstance(source_compile.get("facts"), list) else []
    rules = source_compile.get("rules") if isinstance(source_compile.get("rules"), list) else []
    queries = source_compile.get("queries") if isinstance(source_compile.get("queries"), list) else []
    predicate_counts = Counter(_predicate_name(str(fact)) for fact in facts)
    predicate_counts.pop("", None)
    candidate_predicates = sorted(
        sig for sig in (_predicate_signature(row) for row in parsed.get("candidate_predicates", [])) if sig
    )
    repeated_structures = sorted(
        sig for sig in (_repeated_structure_signature(row) for row in parsed.get("repeated_structures", [])) if sig
    )
    surface_rows = source_compile.get("surface_contribution")
    if not isinstance(surface_rows, list):
        surface_rows = []
    focus_counts = {
        predicate: int(predicate_counts.get(predicate, 0))
        for predicate in sorted(focus_predicates)
    }
    return {
        "path": str(path),
        "model": data.get("model"),
        "domain_hint": data.get("domain_hint"),
        "parsed_ok": data.get("parsed_ok"),
        "rough_score": score.get("rough_score"),
        "candidate_predicate_count": len(candidate_predicates),
        "candidate_predicates": candidate_predicates,
        "repeated_structure_count": len(repeated_structures),
        "repeated_structures": repeated_structures,
        "compile_mode": source_compile.get("mode"),
        "compile_ok": source_compile.get("ok"),
        "admitted_count": source_compile.get("admitted_count"),
        "skipped_count": source_compile.get("skipped_count"),
        "unique_fact_count": source_compile.get("unique_fact_count"),
        "fact_count": len(facts),
        "rule_count": len(rules),
        "query_count": len(queries),
        "compile_health_verdict": health.get("verdict"),
        "compile_health_recommendation": health.get("recommendation"),
        "semantic_zombie_risk": ((health.get("semantic_progress") or {}) if isinstance(health.get("semantic_progress"), dict) else {}).get("zombie_risk"),
        "fact_predicate_counts": dict(sorted(predicate_counts.items())),
        "focus_predicate_counts": focus_counts,
        "surface_contribution": surface_rows,
    }


def summarize_qa(path: Path) -> dict[str, Any]:
    data = _read_json(path)
    summary = data.get("summary") if isinstance(data.get("summary"), dict) else {}
    labels: list[str] = []
    rows = data.get("rows") if isinstance(data.get("rows"), list) else []
    for row in rows:
        if isinstance(row, dict):
            judge = row.get("reference_judge") if isinstance(row.get("reference_judge"), dict) else {}
            labels.append(str(judge.get("verdict") or row.get("judge_label") or row.get("label") or ""))
    return {
        "path": str(path),
        "question_count": summary.get("question_count", data.get("question_count")),
        "judge_exact": summary.get("judge_exact", data.get("judge_exact")),
        "judge_partial": summary.get("judge_partial", data.get("judge_partial")),
        "judge_miss": summary.get("judge_miss", data.get("judge_miss")),
        "runtime_load_error_count": summary.get("runtime_load_error_count", data.get("runtime_load_error_count")),
        "write_proposal_rows": summary.get("write_proposal_rows", data.get("write_proposal_rows")),
        "failure_surface_counts": summary.get("failure_surface_counts", data.get("failure_surface_counts")),
        "row_labels": labels,
    }


def compare_to_baseline(summaries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not summaries:
        return []
    baseline = summaries[0]
    base_predicates = set(baseline["candidate_predicates"])
    base_fact_predicates = set(baseline["fact_predicate_counts"])
    comparisons: list[dict[str, Any]] = []
    for summary in summaries:
        predicates = set(summary["candidate_predicates"])
        fact_predicates = set(summary["fact_predicate_counts"])
        comparisons.append(
            {
                "path": summary["path"],
                "admitted_delta": _delta(summary.get("admitted_count"), baseline.get("admitted_count")),
                "skipped_delta": _delta(summary.get("skipped_count"), baseline.get("skipped_count")),
                "unique_fact_delta": _delta(summary.get("unique_fact_count"), baseline.get("unique_fact_count")),
                "candidate_predicates_added": sorted(predicates - base_predicates),
                "candidate_predicates_removed": sorted(base_predicates - predicates),
                "fact_predicates_added": sorted(fact_predicates - base_fact_predicates),
                "fact_predicates_removed": sorted(base_fact_predicates - fact_predicates),
                "focus_predicate_deltas": {
                    key: _delta(value, baseline["focus_predicate_counts"].get(key))
                    for key, value in summary["focus_predicate_counts"].items()
                },
            }
        )
    return comparisons


def _delta(value: Any, baseline: Any) -> int | None:
    if isinstance(value, int) and isinstance(baseline, int):
        return value - baseline
    return None


def render_markdown(payload: dict[str, Any]) -> str:
    lines: list[str] = ["# Domain Bootstrap Compile Comparison", ""]
    lines.append("## Compile Summary")
    lines.append("")
    lines.append("| Label | Admitted | Skipped | Unique Facts | Predicates | Repeated Structures | Health | Mode |")
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |")
    for item in payload["compiles"]:
        label = Path(str(item["path"])).name
        lines.append(
            f"| `{label}` | {_fmt(item.get('admitted_count'))} | {_fmt(item.get('skipped_count'))} | "
            f"{_fmt(item.get('unique_fact_count'))} | {_fmt(item.get('candidate_predicate_count'))} | "
            f"{_fmt(item.get('repeated_structure_count'))} | `{item.get('compile_health_verdict')}` | `{item.get('compile_mode')}` |"
        )
    if payload.get("focus_predicates"):
        lines.extend(["", "## Focus Predicate Counts", ""])
        headers = " | ".join(f"`{name}`" for name in payload["focus_predicates"])
        lines.append(f"| Label | {headers} |")
        lines.append("| --- | " + " | ".join("---:" for _ in payload["focus_predicates"]) + " |")
        for item in payload["compiles"]:
            label = Path(str(item["path"])).name
            counts = " | ".join(str(item["focus_predicate_counts"].get(name, 0)) for name in payload["focus_predicates"])
            lines.append(f"| `{label}` | {counts} |")
    lines.extend(["", "## Predicate Deltas Versus First Compile", ""])
    for delta in payload["comparisons"][1:]:
        lines.append(f"### `{Path(str(delta['path'])).name}`")
        lines.append("")
        lines.append(f"- admitted delta: `{delta['admitted_delta']}`")
        lines.append(f"- skipped delta: `{delta['skipped_delta']}`")
        lines.append(f"- unique fact delta: `{delta['unique_fact_delta']}`")
        lines.append(f"- candidate predicates added: `{len(delta['candidate_predicates_added'])}`")
        lines.append(f"- candidate predicates removed: `{len(delta['candidate_predicates_removed'])}`")
        lines.append(f"- fact predicates added: `{len(delta['fact_predicates_added'])}`")
        lines.append(f"- fact predicates removed: `{len(delta['fact_predicates_removed'])}`")
        if delta.get("focus_predicate_deltas"):
            parts = ", ".join(f"{key}: {value}" for key, value in delta["focus_predicate_deltas"].items())
            lines.append(f"- focus predicate deltas: `{parts}`")
        lines.append("")
    if payload.get("qa"):
        lines.extend(["## QA Summary", ""])
        lines.append("| Label | Exact | Partial | Miss | Runtime Errors | Write Rows |")
        lines.append("| --- | ---: | ---: | ---: | ---: | ---: |")
        for item in payload["qa"]:
            label = Path(str(item["path"])).name
            lines.append(
                f"| `{label}` | {_fmt(item.get('judge_exact'))} | {_fmt(item.get('judge_partial'))} | "
                f"{_fmt(item.get('judge_miss'))} | {_fmt(item.get('runtime_load_error_count'))} | "
                f"{_fmt(item.get('write_proposal_rows'))} |"
            )
    lines.append("")
    return "\n".join(lines)


def _fmt(value: Any) -> str:
    return "" if value is None else str(value)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compile-json", action="append", required=True, help="Domain bootstrap compile JSON. First one is baseline.")
    parser.add_argument("--qa-json", action="append", default=[], help="Optional QA JSON summaries to include.")
    parser.add_argument("--focus-predicate", action="append", default=[], help="Predicate name to count across compile facts.")
    parser.add_argument("--out-json", help="Write structured comparison JSON.")
    parser.add_argument("--out-md", help="Write markdown report.")
    args = parser.parse_args()

    focus = {str(item).strip() for item in args.focus_predicate if str(item).strip()}
    compiles = [summarize_compile(Path(path), focus) for path in args.compile_json]
    qa = [summarize_qa(Path(path)) for path in args.qa_json]
    payload = {
        "schema_version": "domain_bootstrap_compile_comparison_v1",
        "focus_predicates": sorted(focus),
        "compiles": compiles,
        "comparisons": compare_to_baseline(compiles),
        "qa": qa,
    }
    if args.out_json:
        Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out_json).write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    markdown = render_markdown(payload)
    if args.out_md:
        Path(args.out_md).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out_md).write_text(markdown, encoding="utf-8")
    else:
        print(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
