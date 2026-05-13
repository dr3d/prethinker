#!/usr/bin/env python3
"""Audit external MRC transfer fixtures for question/reference/source alignment.

This is an intake-quality tool, not architecture. It helps separate noisy
dataset rows from genuine compiler or selector boundaries before QA scores are
interpreted as substrate evidence.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]

STOPWORDS = {
    "about",
    "access",
    "according",
    "after",
    "again",
    "against",
    "allow",
    "also",
    "among",
    "answer",
    "any",
    "an",
    "app",
    "application",
    "are",
    "before",
    "being",
    "can",
    "collect",
    "collected",
    "collecting",
    "collection",
    "consider",
    "could",
    "data",
    "detail",
    "details",
    "did",
    "does",
    "do",
    "doing",
    "for",
    "from",
    "have",
    "how",
    "information",
    "info",
    "into",
    "is",
    "it",
    "its",
    "kind",
    "may",
    "me",
    "more",
    "my",
    "not",
    "of",
    "on",
    "our",
    "other",
    "others",
    "people",
    "personal",
    "policy",
    "privacy",
    "question",
    "reference",
    "service",
    "services",
    "should",
    "source",
    "that",
    "the",
    "their",
    "them",
    "there",
    "these",
    "third",
    "this",
    "those",
    "through",
    "to",
    "use",
    "using",
    "was",
    "were",
    "what",
    "when",
    "where",
    "which",
    "while",
    "who",
    "why",
    "will",
    "with",
    "would",
    "you",
    "your",
}

TERM_ALIASES = {
    "advertisement": "advertis",
    "advertisements": "advertis",
    "advertising": "advertis",
    "ads": "advertis",
    "encrypted": "encrypt",
    "encryption": "encrypt",
    "geolocation": "location",
    "locations": "location",
    "marketing": "market",
    "permissions": "permission",
    "protected": "protect",
    "protection": "protect",
    "sale": "sell",
    "shared": "share",
    "sharing": "share",
    "stored": "store",
    "storing": "store",
    "tracked": "track",
    "tracking": "track",
}

CRITICAL_ABSENT_TERMS = {
    "gps",
    "location",
    "market",
}


def main() -> int:
    args = _parse_args()
    root = _abs(args.root)
    summary = audit_root(
        root,
        min_question_terms=args.min_question_terms,
        min_question_evidence_overlap=args.min_question_evidence_overlap,
    )
    out_json = _abs(args.out_json) if args.out_json else root / "transfer_intake_audit.json"
    out_md = _abs(args.out_md) if args.out_md else root / "transfer_intake_audit.md"
    out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    out_md.write_text(_render_md(summary), encoding="utf-8")
    print(json.dumps(summary["totals"], sort_keys=True))
    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")
    return 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True, help="Incoming or staged fixture root to audit.")
    parser.add_argument("--out-json", type=Path)
    parser.add_argument("--out-md", type=Path)
    parser.add_argument(
        "--min-question-terms",
        type=int,
        default=1,
        help="Minimum non-generic question terms required before overlap can be judged.",
    )
    parser.add_argument(
        "--min-question-evidence-overlap",
        type=float,
        default=0.5,
        help="Minimum share of non-generic question terms that should appear in source/reference evidence.",
    )
    return parser.parse_args()


def audit_root(
    root: Path,
    *,
    min_question_terms: int = 1,
    min_question_evidence_overlap: float = 0.5,
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    counts: Counter[str] = Counter()
    for fixture_dir in sorted(path for path in root.iterdir() if path.is_dir()):
        source = _read_optional(fixture_dir / "source.md")
        questions = _read_questions(fixture_dir / "qa.md")
        oracle_rows = _read_oracle(fixture_dir / "oracle.jsonl")
        for index, oracle in enumerate(oracle_rows, start=1):
            question = questions[index - 1] if index - 1 < len(questions) else ""
            row = audit_row(
                fixture=fixture_dir.name,
                qid=str(oracle.get("id") or f"q{index:03d}"),
                question=question,
                reference_answer=str(oracle.get("reference_answer") or oracle.get("answer") or ""),
                source=source,
                min_question_terms=min_question_terms,
                min_question_evidence_overlap=min_question_evidence_overlap,
            )
            rows.append(row)
            counts[row["status"]] += 1
            for flag in row["flags"]:
                counts[f"flag:{flag}"] += 1
    total = len(rows)
    actionable = counts.get("likely_reference_mismatch", 0)
    return {
        "schema_version": "mrc_transfer_intake_audit_v1",
        "root": str(root),
        "thresholds": {
            "min_question_terms": min_question_terms,
            "min_question_evidence_overlap": min_question_evidence_overlap,
        },
        "totals": {
            "rows": total,
            "ok": counts.get("ok", 0),
            "review": counts.get("review", 0),
            "likely_reference_mismatch": actionable,
            "ok_rate": round(counts.get("ok", 0) / total, 4) if total else 0.0,
        },
        "flag_counts": {key.removeprefix("flag:"): value for key, value in counts.items() if key.startswith("flag:")},
        "rows": rows,
    }


def audit_row(
    *,
    fixture: str,
    qid: str,
    question: str,
    reference_answer: str,
    source: str,
    min_question_terms: int,
    min_question_evidence_overlap: float,
) -> dict[str, Any]:
    question_terms = _content_terms(question)
    evidence_terms = _tokens(" ".join([source, reference_answer]))
    covered_terms = sorted(term for term in question_terms if term in evidence_terms)
    missing_terms = sorted(term for term in question_terms if term not in evidence_terms)
    overlap = len(covered_terms) / len(question_terms) if question_terms else None
    reference_literal_in_source = _literal_contains(source, reference_answer)
    flags: list[str] = []
    if not reference_answer.strip():
        flags.append("missing_reference_answer")
    if not source.strip():
        flags.append("missing_source")
    if len(question_terms) < min_question_terms:
        flags.append("low_question_signal")
    if not reference_literal_in_source:
        flags.append("reference_not_literal_in_source")
    if overlap is not None and overlap < min_question_evidence_overlap:
        flags.append("low_question_evidence_overlap")

    status = "ok"
    if "missing_reference_answer" in flags or "missing_source" in flags:
        status = "review"
    elif _strong_question_mismatch(question_terms, covered_terms, missing_terms):
        status = "likely_reference_mismatch"
    elif "low_question_evidence_overlap" in flags or "reference_not_literal_in_source" in flags:
        status = "review"

    return {
        "fixture": fixture,
        "id": qid,
        "status": status,
        "flags": flags,
        "question": question,
        "reference_preview": _preview(reference_answer),
        "question_terms": sorted(question_terms),
        "covered_question_terms": covered_terms,
        "missing_question_terms": missing_terms,
        "question_evidence_overlap": round(overlap, 4) if overlap is not None else None,
        "reference_literal_in_source": reference_literal_in_source,
    }


def _content_terms(question: str) -> set[str]:
    stripped = re.sub(r'"[^"]+"', " ", question)
    stripped = stripped.split(" Options:", 1)[0]
    return {token for token in _tokens(stripped) if token not in STOPWORDS and not token.isdigit()}


def _tokens(text: str) -> set[str]:
    return {_normalize_term(token) for token in re.findall(r"[a-z][a-z0-9]+", text.casefold())}


def _normalize_term(token: str) -> str:
    token = TERM_ALIASES.get(token, token)
    if token.endswith("ies") and len(token) > 4:
        token = f"{token[:-3]}y"
    elif token.endswith("ing") and len(token) > 5:
        token = token[:-3]
    elif token.endswith("ed") and len(token) > 4:
        token = token[:-2]
    elif token.endswith("s") and len(token) > 4 and not token.endswith("ss"):
        token = token[:-1]
    return TERM_ALIASES.get(token, token)


def _strong_question_mismatch(question_terms: set[str], covered_terms: list[str], missing_terms: list[str]) -> bool:
    if not question_terms:
        return False
    missing = set(missing_terms)
    covered = set(covered_terms)
    if missing & CRITICAL_ABSENT_TERMS:
        return True
    if not covered and len(question_terms) >= 2:
        return True
    return False


def _literal_contains(source: str, reference_answer: str) -> bool:
    reference = _normalize_literal(reference_answer)
    if not reference:
        return False
    return reference in _normalize_literal(source)


def _normalize_literal(text: str) -> str:
    return re.sub(r"\s+", " ", text.casefold()).strip()


def _read_questions(path: Path) -> list[str]:
    if not path.exists():
        return []
    questions: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"\s*\d+\.\s+(.*\S)\s*$", line)
        if match:
            questions.append(match.group(1))
    return questions


def _read_oracle(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rows.append(json.loads(line))
    return rows


def _read_optional(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _preview(text: str, limit: int = 240) -> str:
    cleaned = re.sub(r"\s+", " ", text).strip()
    return cleaned[:limit]


def _render_md(summary: dict[str, Any]) -> str:
    totals = summary.get("totals", {})
    lines = [
        "# MRC Transfer Intake Audit",
        "",
        f"Root: `{summary.get('root', '')}`",
        "",
        "## Totals",
        "",
        f"- Rows: `{totals.get('rows', 0)}`",
        f"- OK / review / likely mismatch: `{totals.get('ok', 0)} / {totals.get('review', 0)} / {totals.get('likely_reference_mismatch', 0)}`",
        f"- OK rate: `{totals.get('ok_rate', 0.0)}`",
        "",
        "## Flag Counts",
        "",
    ]
    for key, value in sorted((summary.get("flag_counts") or {}).items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Rows Needing Review", ""])
    review_rows = [row for row in summary.get("rows", []) if row.get("status") != "ok"]
    if not review_rows:
        lines.append("No rows flagged.")
    for row in review_rows:
        lines.extend(
            [
                f"### {row.get('fixture', '')} {row.get('id', '')}",
                "",
                f"- Status: `{row.get('status', '')}`",
                f"- Flags: `{', '.join(row.get('flags') or [])}`",
                f"- Question overlap: `{row.get('question_evidence_overlap')}`",
                f"- Missing question terms: `{', '.join(row.get('missing_question_terms') or [])}`",
                f"- Question: {row.get('question', '')}",
                f"- Reference preview: {row.get('reference_preview', '')}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def _abs(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


if __name__ == "__main__":
    raise SystemExit(main())
