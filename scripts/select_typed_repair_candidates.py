#!/usr/bin/env python3
"""Select repair slices by joining QA verdicts to typed-recall diagnostics.

This is a measurement helper, not a query router. It does not inspect source
documents and does not map natural-language questions to predicates. It only
cross-tabs existing QA verdicts with typed-artifact recall classes so the next
repair starts from a visible ceiling:

    current QA row + answer type + typed_strict + typed_registered

Rows where strict typed material is likely available and registered atoms are
available are query/join candidates. Rows where strict typed material is missing
are compile-recall pressure. The script makes that split repeatable.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


QUERY_JOIN_REGISTERED_CLASSES = {"likely_available", "partial_available"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qa-root", type=Path, required=True)
    parser.add_argument("--typed-recall-json", type=Path, required=True)
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    parser.add_argument("--max-rows", type=int, default=80)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(
        qa_root=args.qa_root,
        typed_recall_json=args.typed_recall_json,
        max_rows=args.max_rows,
    )
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(render_markdown(report), encoding="utf-8")
    if not args.out_json and not args.out_md:
        print(render_markdown(report))
    return 0


def build_report(*, qa_root: Path, typed_recall_json: Path, max_rows: int = 80) -> dict[str, Any]:
    recall = json.loads(typed_recall_json.read_text(encoding="utf-8"))
    recall_rows = {
        (row.get("fixture"), row.get("id")): row
        for row in recall.get("rows", [])
        if row.get("fixture") and row.get("id")
    }
    rows = []
    for qa_path in sorted(qa_root.glob("*/*.json")):
        payload = json.loads(qa_path.read_text(encoding="utf-8"))
        fixture = qa_path.parent.name
        for qa_row in payload.get("rows", []):
            row_id = qa_row.get("id")
            recall_row = recall_rows.get((fixture, row_id), {})
            verdict = _qa_verdict(qa_row)
            failure_surface = _failure_surface(qa_row)
            row = {
                "fixture": fixture,
                "id": row_id,
                "answer_type": recall_row.get("answer_type", "unknown"),
                "verdict": verdict,
                "failure_surface": failure_surface,
                "question": qa_row.get("utterance", ""),
                "reference_answer": qa_row.get("reference_answer", ""),
                "typed_strict": _recall_class(recall_row, "typed_strict"),
                "typed_registered": _recall_class(recall_row, "typed_registered"),
            }
            rows.append(row)

    query_join_candidates = [
        row
        for row in rows
        if row["verdict"] != "exact"
        and row["typed_strict"]["class"] == "likely_available"
        and row["typed_registered"]["class"] in QUERY_JOIN_REGISTERED_CLASSES
    ]
    second_tier_candidates = [
        row
        for row in rows
        if row["verdict"] != "exact"
        and row["typed_strict"]["class"] == "partial_available"
        and row["typed_registered"]["class"] in QUERY_JOIN_REGISTERED_CLASSES
    ]
    compile_recall_pressure = [
        row
        for row in rows
        if row["verdict"] != "exact"
        and (
            row["typed_strict"]["class"] == "not_available"
            or row["typed_registered"]["class"] == "not_available"
        )
    ]

    return {
        "schema_version": "typed_repair_candidate_selection_v1",
        "qa_root": str(qa_root),
        "typed_recall_json": str(typed_recall_json),
        "summary": _summary(rows),
        "non_exact_by_answer_type_and_strict_class": _counter_table(
            (row["answer_type"], row["typed_strict"]["class"])
            for row in rows
            if row["verdict"] != "exact"
        ),
        "non_exact_by_answer_type_and_registered_class": _counter_table(
            (row["answer_type"], row["typed_registered"]["class"])
            for row in rows
            if row["verdict"] != "exact"
        ),
        "query_join_candidate_count": len(query_join_candidates),
        "query_join_candidates": _sort_rows(query_join_candidates)[:max_rows],
        "second_tier_candidate_count": len(second_tier_candidates),
        "second_tier_candidates": _sort_rows(second_tier_candidates)[:max_rows],
        "compile_recall_pressure_count": len(compile_recall_pressure),
        "compile_recall_pressure": _sort_rows(compile_recall_pressure)[:max_rows],
    }


def _qa_verdict(row: dict[str, Any]) -> str:
    judge = row.get("reference_judge") if isinstance(row.get("reference_judge"), dict) else {}
    envelope = row.get("response_envelope") if isinstance(row.get("response_envelope"), dict) else {}
    return str(judge.get("verdict") or envelope.get("reference_support") or "unknown")


def _failure_surface(row: dict[str, Any]) -> str:
    surface = row.get("failure_surface") if isinstance(row.get("failure_surface"), dict) else {}
    envelope = row.get("response_envelope") if isinstance(row.get("response_envelope"), dict) else {}
    return str(surface.get("surface") or envelope.get("failure_surface") or "unknown")


def _recall_class(row: dict[str, Any], key: str) -> dict[str, Any]:
    payload = row.get(key) if isinstance(row.get(key), dict) else {}
    return {
        "class": payload.get("class", "unknown"),
        "token_coverage": payload.get("token_coverage"),
        "number_coverage": payload.get("number_coverage"),
        "missing_tokens": payload.get("missing_tokens", []),
    }


def _summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    verdicts = Counter(row["verdict"] for row in rows)
    return {
        "row_count": len(rows),
        "exact": verdicts.get("exact", 0),
        "partial": verdicts.get("partial", 0),
        "miss": verdicts.get("miss", 0),
        "unknown": verdicts.get("unknown", 0),
        "non_exact": len([row for row in rows if row["verdict"] != "exact"]),
    }


def _counter_table(items: Any) -> list[dict[str, Any]]:
    counts = Counter(items)
    return [
        {"answer_type": answer_type, "class": class_name, "count": count}
        for (answer_type, class_name), count in sorted(counts.items())
    ]


def _sort_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(rows, key=lambda row: (row["answer_type"], row["fixture"], row["id"] or ""))


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Typed Repair Candidate Selection",
        "",
        f"- qa root: `{report['qa_root']}`",
        f"- typed recall: `{report['typed_recall_json']}`",
        f"- rows: {summary['row_count']}",
        f"- verdicts: {summary['exact']} exact / {summary['partial']} partial / {summary['miss']} miss",
        f"- non-exact rows: {summary['non_exact']}",
        f"- query/join candidates: {report['query_join_candidate_count']}",
        f"- second-tier candidates: {report['second_tier_candidate_count']}",
        f"- compile-recall pressure rows: {report['compile_recall_pressure_count']}",
        "",
        "## Non-Exact By Strict Typed Class",
        "",
        "| answer type | typed strict class | rows |",
        "| --- | --- | ---: |",
    ]
    for item in report["non_exact_by_answer_type_and_strict_class"]:
        lines.append(f"| {item['answer_type']} | {item['class']} | {item['count']} |")
    lines.extend(
        [
            "",
            "## Non-Exact By Registered Typed Class",
            "",
            "| answer type | typed registered class | rows |",
            "| --- | --- | ---: |",
        ]
    )
    for item in report["non_exact_by_answer_type_and_registered_class"]:
        lines.append(f"| {item['answer_type']} | {item['class']} | {item['count']} |")
    lines.extend(
        [
            "",
            "## Query/Join Candidates",
            "",
            "Non-exact rows where strict typed recall is likely and registered typed atoms are likely or partial.",
            "",
        ]
    )
    lines.extend(_render_rows(report["query_join_candidates"]))
    lines.extend(
        [
            "",
            "## Second-Tier Candidates",
            "",
            "Non-exact rows where strict typed recall is partial and registered typed atoms are likely or partial.",
            "",
        ]
    )
    lines.extend(_render_rows(report["second_tier_candidates"]))
    lines.extend(
        [
            "",
            "## Compile-Recall Pressure",
            "",
            "Non-exact rows where strict typed material or registered typed material is not available.",
            "",
        ]
    )
    lines.extend(_render_rows(report["compile_recall_pressure"]))
    return "\n".join(lines).rstrip() + "\n"


def _render_rows(rows: list[dict[str, Any]]) -> list[str]:
    if not rows:
        return ["No rows."]
    lines = [
        "| fixture | id | verdict | surface | answer type | strict | registered | reference |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        reference = _table_cell(str(row.get("reference_answer", ""))[:140])
        strict = _class_cell(row["typed_strict"])
        registered = _class_cell(row["typed_registered"])
        lines.append(
            f"| {row['fixture']} | {row['id']} | {row['verdict']} | "
            f"{row['failure_surface']} | {row['answer_type']} | {strict} | {registered} | {reference} |"
        )
    return lines


def _class_cell(payload: dict[str, Any]) -> str:
    token_cov = payload.get("token_coverage")
    if token_cov is None:
        return str(payload.get("class"))
    return f"{payload.get('class')} ({token_cov})"


def _table_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
