#!/usr/bin/env python3
"""Audit whether direct-surface QA misses have answer evidence in source surfaces.

This is a diagnostic tool, not a repair. It reads QA scorecard artifacts and
their compile JSONs, then checks whether reference-answer tokens are present in
deterministic ``source_record_*`` rows and/or direct admitted predicates.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
FACT_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\((.*)\)\.\s*$")
WORD_RE = re.compile(r"[a-z0-9]+")
STOPWORDS = {
    "a",
    "about",
    "according",
    "all",
    "an",
    "and",
    "answer",
    "are",
    "as",
    "associated",
    "at",
    "be",
    "by",
    "did",
    "does",
    "during",
    "for",
    "from",
    "had",
    "has",
    "have",
    "how",
    "if",
    "in",
    "is",
    "it",
    "its",
    "list",
    "model",
    "number",
    "of",
    "on",
    "or",
    "per",
    "same",
    "section",
    "status",
    "that",
    "the",
    "this",
    "to",
    "under",
    "was",
    "were",
    "what",
    "when",
    "which",
    "who",
    "with",
    "would",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scorecard-json", type=Path, required=True)
    parser.add_argument("--out-json", type=Path)
    parser.add_argument("--out-md", type=Path)
    parser.add_argument(
        "--surface",
        action="append",
        default=[],
        help="Optional failure surface filter. Repeatable.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    scorecard_path = _resolve(args.scorecard_json)
    report = audit_scorecard(
        json.loads(scorecard_path.read_text(encoding="utf-8-sig")),
        scorecard_path=scorecard_path,
        surfaces=set(args.surface or []),
    )
    out_json = _resolve(args.out_json) if args.out_json else scorecard_path.with_name("source_surface_gap_audit.json")
    out_md = _resolve(args.out_md) if args.out_md else scorecard_path.with_name("source_surface_gap_audit.md")
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    out_md.write_text(render_markdown(report), encoding="utf-8")
    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")
    print(json.dumps(report["summary"], sort_keys=True))
    return 0


def audit_scorecard(
    scorecard: dict[str, Any],
    *,
    scorecard_path: Path | None = None,
    surfaces: set[str] | None = None,
) -> dict[str, Any]:
    surfaces = surfaces or set()
    rows: list[dict[str, Any]] = []
    fixture_rows = _scorecard_fixture_rows(scorecard)
    for artifact in fixture_rows:
        if not isinstance(artifact, dict):
            continue
        fixture = str(artifact.get("label") or artifact.get("fixture") or "")
        qa_path = _path_from_artifact(artifact.get("path"))
        run_path = _path_from_artifact(artifact.get("run_json"))
        if not qa_path or not qa_path.exists() or not run_path or not run_path.exists():
            continue
        qa = json.loads(qa_path.read_text(encoding="utf-8-sig"))
        qa_rows = {str(row.get("id", "")): row for row in qa.get("rows", []) if isinstance(row, dict)}
        compile_payload = json.loads(run_path.read_text(encoding="utf-8-sig"))
        compile_index = _compile_index(compile_payload)
        for row in artifact.get("non_exact_rows", []) if isinstance(artifact.get("non_exact_rows"), list) else []:
            if not isinstance(row, dict):
                continue
            surface = str(row.get("failure_surface", "") or "")
            if surfaces and surface not in surfaces:
                continue
            qa_row = qa_rows.get(str(row.get("id", "")), {})
            rows.append(
                _audit_row(
                    fixture=fixture,
                    scorecard_row=row,
                    qa_row=qa_row,
                    compile_index=compile_index,
                )
            )

    evidence_counts = Counter(str(row.get("evidence_class", "")) for row in rows)
    surface_counts = Counter(str(row.get("failure_surface", "")) for row in rows)
    return {
        "schema_version": "source_surface_gap_audit_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "policy": [
            "Diagnostic only: may inspect reference answers to classify misses, but does not change architecture.",
            "Treats source_record_* rows as source-addressability evidence, not semantic truth.",
            "Use results to choose generic compile-surface or query-planning repairs; do not promote fixture terms.",
        ],
        "artifacts": {"scorecard_json": _display_path(scorecard_path)},
        "summary": {
            "row_count": len(rows),
            "failure_surface_counts": dict(sorted(surface_counts.items())),
            "evidence_class_counts": dict(sorted(evidence_counts.items())),
            "answer_in_source_record_rows": sum(
                1 for row in rows if row["answer_evidence"]["source_record_strong_match_count"]
            ),
            "answer_in_direct_rows": sum(1 for row in rows if row["answer_evidence"]["direct_strong_match_count"]),
            "question_terms_in_source_record_rows": sum(
                1 for row in rows if row["question_evidence"]["source_record_match_count"]
            ),
        },
        "rows": rows,
    }


def _audit_row(
    *,
    fixture: str,
    scorecard_row: dict[str, Any],
    qa_row: dict[str, Any],
    compile_index: dict[str, Any],
) -> dict[str, Any]:
    question = str(scorecard_row.get("question") or qa_row.get("utterance") or "")
    answer = str(qa_row.get("reference_answer") or "")
    answer_tokens = _salient_tokens(answer)
    question_tokens = _salient_tokens(question)
    answer_evidence = _evidence(tokens=answer_tokens, compile_index=compile_index)
    question_evidence = _evidence(tokens=question_tokens, compile_index=compile_index, min_overlap=2)
    direct_predicates = sorted({predicate for query in scorecard_row.get("queries", []) for predicate in _query_predicates(query)})
    evidence_class = _evidence_class(answer_evidence=answer_evidence, question_evidence=question_evidence)
    return {
        "fixture": fixture,
        "id": str(scorecard_row.get("id", "")),
        "verdict": str(scorecard_row.get("verdict", "")),
        "failure_surface": str(scorecard_row.get("failure_surface", "")),
        "question": question,
        "reference_answer": answer,
        "predicate_hints": direct_predicates,
        "evidence_class": evidence_class,
        "answer_tokens": sorted(answer_tokens),
        "question_tokens": sorted(question_tokens),
        "answer_evidence": answer_evidence,
        "question_evidence": question_evidence,
    }


def _evidence(tokens: set[str], compile_index: dict[str, Any], *, min_overlap: int = 1) -> dict[str, Any]:
    if not tokens:
        return {
            "source_record_match_count": 0,
            "direct_match_count": 0,
            "source_record_strong_match_count": 0,
            "direct_strong_match_count": 0,
            "source_record_best_coverage": 0.0,
            "direct_best_coverage": 0.0,
            "source_record_matches": [],
            "direct_matches": [],
        }
    source_matches = _matching_rows(tokens, compile_index["source_rows"], min_overlap=min_overlap)
    direct_matches = _matching_rows(tokens, compile_index["direct_rows"], min_overlap=min_overlap)
    return {
        "source_record_match_count": len(source_matches),
        "direct_match_count": len(direct_matches),
        "source_record_strong_match_count": sum(1 for match in source_matches if _is_strong_match(match, tokens)),
        "direct_strong_match_count": sum(1 for match in direct_matches if _is_strong_match(match, tokens)),
        "source_record_best_coverage": _best_coverage(source_matches, tokens),
        "direct_best_coverage": _best_coverage(direct_matches, tokens),
        "source_record_matches": source_matches[:5],
        "direct_matches": direct_matches[:5],
    }


def _evidence_class(*, answer_evidence: dict[str, Any], question_evidence: dict[str, Any]) -> str:
    answer_source = int(answer_evidence.get("source_record_strong_match_count", 0) or 0)
    answer_direct = int(answer_evidence.get("direct_strong_match_count", 0) or 0)
    answer_source_weak = int(answer_evidence.get("source_record_match_count", 0) or 0)
    answer_direct_weak = int(answer_evidence.get("direct_match_count", 0) or 0)
    question_source = int(question_evidence.get("source_record_match_count", 0) or 0)
    if answer_source and not answer_direct:
        return "answer_stranded_in_source_record"
    if answer_source and answer_direct:
        return "answer_present_in_direct_and_source"
    if answer_direct:
        return "answer_present_in_direct_only"
    if answer_source_weak and not answer_direct_weak:
        return "weak_answer_trace_in_source_record"
    if answer_source_weak:
        return "weak_answer_trace_in_source_and_direct"
    if question_source:
        return "question_surface_present_without_answer_match"
    return "no_obvious_source_match"


def _compile_index(payload: dict[str, Any]) -> dict[str, Any]:
    facts = _facts_from_compile(payload)
    source_rows: list[dict[str, Any]] = []
    direct_rows: list[dict[str, Any]] = []
    for fact in facts:
        parsed = _parse_fact(fact)
        if not parsed:
            continue
        predicate, args = parsed
        row = {
            "fact": fact,
            "predicate": predicate,
            "args": args,
            "tokens": _salient_tokens(" ".join([predicate, *args])),
        }
        if predicate.startswith("source_record"):
            source_rows.append(row)
        else:
            direct_rows.append(row)
    return {"source_rows": source_rows, "direct_rows": direct_rows}


def _matching_rows(tokens: set[str], rows: list[dict[str, Any]], *, min_overlap: int) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    for row in rows:
        overlap = tokens & set(row["tokens"])
        if len(overlap) < min_overlap:
            continue
        matches.append(
            {
                "predicate": row["predicate"],
                "overlap": sorted(overlap),
                "coverage": round(len(overlap) / max(1, len(tokens)), 3),
                "fact": row["fact"],
            }
        )
    matches.sort(key=lambda item: (-float(item["coverage"]), -len(item["overlap"]), item["predicate"], item["fact"]))
    return matches


def _is_strong_match(match: dict[str, Any], tokens: set[str]) -> bool:
    overlap_count = len(match.get("overlap", []))
    coverage = float(match.get("coverage", 0.0) or 0.0)
    if len(tokens) <= 2:
        return overlap_count == len(tokens)
    if len(tokens) <= 4:
        return overlap_count >= len(tokens) - 1 and coverage >= 0.75
    return overlap_count >= 3 and coverage >= 0.6


def _best_coverage(matches: list[dict[str, Any]], tokens: set[str]) -> float:
    if not matches or not tokens:
        return 0.0
    return round(max(float(match.get("coverage", 0.0) or 0.0) for match in matches), 3)


def _facts_from_compile(payload: dict[str, Any]) -> list[str]:
    source_compile = payload.get("source_compile") if isinstance(payload.get("source_compile"), dict) else {}
    facts = source_compile.get("facts")
    if isinstance(facts, list):
        return [str(fact).strip() for fact in facts if str(fact).strip()]
    parsed = payload.get("parsed") if isinstance(payload.get("parsed"), dict) else {}
    parsed_facts = parsed.get("facts")
    if isinstance(parsed_facts, list):
        return [str(fact).strip() for fact in parsed_facts if str(fact).strip()]
    return []


def _parse_fact(fact: str) -> tuple[str, list[str]] | None:
    match = FACT_RE.match(str(fact).strip())
    if not match:
        return None
    return match.group(1), [part.strip().strip("'\"") for part in _split_args(match.group(2))]


def _split_args(raw: str) -> list[str]:
    # Current compiled facts use atom arguments; this small splitter avoids
    # corrupting quoted commas if future ledgers contain quoted values.
    args: list[str] = []
    current: list[str] = []
    quote = ""
    for char in raw:
        if quote:
            current.append(char)
            if char == quote:
                quote = ""
            continue
        if char in {"'", '"'}:
            quote = char
            current.append(char)
            continue
        if char == ",":
            args.append("".join(current).strip())
            current = []
            continue
        current.append(char)
    if current or raw:
        args.append("".join(current).strip())
    return args


def _query_predicates(query: Any) -> list[str]:
    return [match.group(1) for match in re.finditer(r"\b([a-z][A-Za-z0-9_]*)\s*\(", str(query))]


def _salient_tokens(text: str) -> set[str]:
    tokens = set()
    for token in WORD_RE.findall(str(text).lower().replace("_", " ")):
        if token in STOPWORDS:
            continue
        if len(token) == 1 and not token.isdigit():
            continue
        tokens.add(token)
    return tokens


def _scorecard_fixture_rows(scorecard: dict[str, Any]) -> list[Any]:
    fixtures = scorecard.get("fixtures")
    if isinstance(fixtures, list):
        return fixtures
    artifacts = scorecard.get("artifacts")
    if isinstance(artifacts, list):
        return artifacts
    return []


def render_markdown(report: dict[str, Any]) -> str:
    summary = report.get("summary", {}) if isinstance(report.get("summary"), dict) else {}
    lines = [
        "# Source-Surface Gap Audit",
        "",
        f"Generated: {report.get('generated_at', '')}",
        "",
        "## Policy",
        "",
    ]
    for rule in report.get("policy", []):
        lines.append(f"- {rule}")
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Rows audited: `{summary.get('row_count', 0)}`",
            f"- Failure surfaces: `{summary.get('failure_surface_counts', {})}`",
            f"- Evidence classes: `{summary.get('evidence_class_counts', {})}`",
            f"- Answer present in source_record rows: `{summary.get('answer_in_source_record_rows', 0)}`",
            f"- Answer present in direct rows: `{summary.get('answer_in_direct_rows', 0)}`",
            f"- Question terms present in source_record rows: `{summary.get('question_terms_in_source_record_rows', 0)}`",
            "",
            "## Rows",
            "",
            "| Fixture | Row | Verdict | Surface | Evidence Class | Source Answer Matches | Direct Answer Matches | Question |",
            "| --- | --- | --- | --- | --- | ---: | ---: | --- |",
        ]
    )
    for row in report.get("rows", []):
        answer = row.get("answer_evidence", {}) if isinstance(row.get("answer_evidence"), dict) else {}
        question = str(row.get("question", "")).replace("|", "/")
        lines.append(
            f"| `{row.get('fixture', '')}` | `{row.get('id', '')}` | `{row.get('verdict', '')}` | "
            f"`{row.get('failure_surface', '')}` | `{row.get('evidence_class', '')}` | "
            f"`{answer.get('source_record_strong_match_count', 0)}` | "
            f"`{answer.get('direct_strong_match_count', 0)}` | {question} |"
        )
    lines.append("")
    lines.extend(["## Top Stranded Examples", ""])
    stranded = [row for row in report.get("rows", []) if row.get("evidence_class") == "answer_stranded_in_source_record"]
    for row in stranded[:12]:
        matches = row.get("answer_evidence", {}).get("source_record_matches", [])
        lines.append(f"### `{row.get('fixture')}` `{row.get('id')}`")
        lines.append("")
        lines.append(f"- Question: {row.get('question', '')}")
        lines.append(f"- Reference answer: `{row.get('reference_answer', '')}`")
        for match in matches[:2]:
            fact = str(match.get("fact", "")).replace("|", "/")
            overlap = ", ".join(match.get("overlap", []))
            lines.append(f"- Source match ({overlap}): `{fact}`")
        lines.append("")
    return "\n".join(lines)


def _path_from_artifact(value: Any) -> Path | None:
    if not value:
        return None
    path = Path(str(value))
    return path if path.is_absolute() else REPO_ROOT / path


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


def _display_path(value: Path | str | None) -> str:
    if value is None:
        return ""
    path = value if isinstance(value, Path) else Path(str(value))
    try:
        return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
