#!/usr/bin/env python3
"""Audit not-exact QA rows for query/transition resolution residue.

This is a diagnostic audit over QA artifacts. It does not change query
planning, compile guidance, compatibility-row delivery, or selector behavior.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


PREDICATE_RE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(")


def classify_not_exact_row(row: dict[str, Any]) -> str:
    text = " ".join(
        str(value or "")
        for value in (
            row.get("utterance"),
            row.get("reference_answer"),
            _nested(row, "evidence_bundle_plan", "question_focus"),
            _nested(row, "failure_surface", "rationale"),
            _nested(row, "failure_surface", "suggested_next_action"),
        )
    ).lower()
    queries = _row_queries(row)
    predicates = set(_row_predicates(row))

    if _has_any(text, ("return to", "returned to", "back to", "revert to", "reverted to")) and (
        _has_suffix(predicates, "_start") or _has_suffix(predicates, "_end") or any("_start(" in q or "_end(" in q for q in queries)
    ):
        return "return_to_state_requires_intervening_end"

    if _has_any(text, ("during", "interval", "active interval", "validity", "effective window")) and (
        _has_suffix(predicates, "_status") or any("_status(" in q for q in queries)
    ):
        return "interval_scoped_status_flattened"

    if _has_any(text, ("assigned", "assignment", "assigned to")) and any("assigned_to" in predicate for predicate in predicates):
        if any(_predicate_arity_from_query(query, "assigned_to") == 3 for query in queries):
            return "assignment_scope_missing"
        return "assignment_resolution_residue"

    if _has_any(text, ("initial status", "initial state", "starting status", "starting state")):
        return "initial_status_not_admitted"

    if _has_any(text, ("current status", "final status", "latest status")) and _has_suffix(predicates, "_status"):
        return "status_phase_projection_residue"

    return "unclassified_query_transition_residue"


def audit_files(paths: list[Path]) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        rows = payload.get("rows") or []
        for row in rows:
            verdict = _nested(row, "reference_judge", "verdict")
            if verdict == "exact":
                continue
            classification = classify_not_exact_row(row)
            results.append(
                {
                    "qa_json": str(path),
                    "utterance": row.get("utterance", ""),
                    "reference_answer": row.get("reference_answer", ""),
                    "verdict": verdict or "unknown",
                    "failure_surface": _nested(row, "failure_surface", "surface") or "unknown",
                    "classification": classification,
                    "query_count": len(_row_queries(row)),
                    "predicates": sorted(set(_row_predicates(row))),
                }
            )

    return {
        "file_count": len(paths),
        "not_exact_count": len(results),
        "classification_counts": _count_by(results, "classification"),
        "failure_surface_counts": _count_by(results, "failure_surface"),
        "rows": results,
    }


def _to_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Query/Transition Resolution Residue Audit",
        "",
        f"- Files: `{report['file_count']}`",
        f"- Not-exact rows: `{report['not_exact_count']}`",
        f"- Classification counts: `{report['classification_counts']}`",
        f"- Failure-surface counts: `{report['failure_surface_counts']}`",
        "",
        "| Classification | Failure surface | Verdict | Query count | Utterance | Predicates |",
        "| --- | --- | --- | ---: | --- | --- |",
    ]
    for row in report["rows"]:
        predicates = ", ".join(f"`{predicate}`" for predicate in row["predicates"])
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row['classification']}`",
                    f"`{row['failure_surface']}`",
                    f"`{row['verdict']}`",
                    str(row["query_count"]),
                    _escape_md(str(row["utterance"])),
                    predicates,
                ]
            )
            + " |"
        )
    lines.append("")
    return "\n".join(lines)


def _count_by(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        value = str(row.get(key) or "unknown")
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def _row_queries(row: dict[str, Any]) -> list[str]:
    queries: list[str] = []
    for item in row.get("evidence_bundle_plan_query_results") or []:
        query = item.get("query")
        if query:
            queries.append(str(query))
    return queries


def _row_predicates(row: dict[str, Any]) -> list[str]:
    predicates: list[str] = []
    for query in _row_queries(row):
        match = PREDICATE_RE.search(query)
        if match:
            predicates.append(match.group(1))
    for item in row.get("evidence_bundle_plan_query_results") or []:
        predicate = _nested(item, "result", "predicate")
        if predicate:
            predicates.append(str(predicate))
    return predicates


def _predicate_arity_from_query(query: str, suffix: str) -> int | None:
    match = PREDICATE_RE.search(query)
    if not match or not match.group(1).endswith(suffix):
        return None
    start = query.find("(", match.end(1))
    end = query.rfind(")")
    if start < 0 or end < start:
        return None
    args = query[start + 1 : end]
    if not args.strip():
        return 0
    return len([part for part in args.split(",")])


def _has_suffix(values: set[str], suffix: str) -> bool:
    return any(value.endswith(suffix) for value in values)


def _has_any(text: str, needles: tuple[str, ...]) -> bool:
    return any(needle in text for needle in needles)


def _nested(value: dict[str, Any], *keys: str) -> Any:
    current: Any = value
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _escape_md(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("qa_json", nargs="+", type=Path)
    parser.add_argument("--out-json", type=Path)
    parser.add_argument("--out-md", type=Path)
    args = parser.parse_args()

    report = audit_files(args.qa_json)
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(_to_markdown(report), encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("not_exact_count", "classification_counts")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
