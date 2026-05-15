"""Audit whether lens vocabulary terms surface on unlike compile artifacts.

This is a compile-artifact audit, not a QA score. It compares a vocabulary of
structural lens terms against admitted direct facts and source-record facts. A
term is "structural" when it appears in direct predicates or arguments, "source
only" when it appears only in source-record ledger text, and "absent" when the
source itself did not expose that term family.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


FACT_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\((.*)\)\.\s*$")
TOKEN_RE = re.compile(r"[a-z0-9]+")


@dataclass(frozen=True)
class LensTerm:
    term: str
    tokens: tuple[str, ...]


EVIDENCE_PROVENANCE_TERMS: tuple[LensTerm, ...] = (
    LensTerm("prepared", ("prepared", "preparer", "drafted", "wrote", "written")),
    LensTerm("presented", ("presented", "submitted", "filed", "introduced")),
    LensTerm("dated", ("dated", "date")),
    LensTerm("admitted", ("admitted", "entered")),
    LensTerm("relied_on", ("relied", "relies", "basis", "cited")),
    LensTerm("commissioned", ("commissioned", "requested", "ordered")),
    LensTerm("corrected", ("corrected", "correction", "revised", "amended")),
    LensTerm("located", ("located", "found", "stored", "held")),
)

LENS_TERMS: dict[str, tuple[LensTerm, ...]] = {
    "evidence_provenance": EVIDENCE_PROVENANCE_TERMS,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lens", choices=sorted(LENS_TERMS), required=True)
    parser.add_argument(
        "--compile-json",
        action="append",
        type=Path,
        default=[],
        help="Compile JSON file or directory containing domain_bootstrap_file_*.json. Repeatable.",
    )
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    paths = _expand_compile_paths(args.compile_json)
    if not paths:
        raise SystemExit("No compile JSON files found.")
    terms = LENS_TERMS[args.lens]
    reports = [audit_compile(path, lens=args.lens, terms=terms) for path in paths]
    payload = {
        "schema": "lens_vocabulary_transfer_audit_v1",
        "lens": args.lens,
        "compile_count": len(reports),
        "summary": summarize_reports(reports, terms),
        "reports": reports,
    }
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(render_markdown(payload), encoding="utf-8")
    if not args.out_json and not args.out_md:
        print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def _expand_compile_paths(inputs: list[Path]) -> list[Path]:
    out: list[Path] = []
    for item in inputs:
        if item.is_dir():
            matches = sorted(item.glob("domain_bootstrap_file_*.json"))
            if matches:
                out.append(matches[-1])
                continue
            out.extend(sorted(item.glob("*/domain_bootstrap_file_*.json")))
        elif item.is_file():
            out.append(item)
    return sorted(dict.fromkeys(path.resolve() for path in out))


def audit_compile(path: Path, *, lens: str, terms: tuple[LensTerm, ...]) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    facts = _facts_from_compile(data)
    source_facts = [fact for fact in facts if _predicate_name(fact).startswith("source_record")]
    direct_facts = [fact for fact in facts if not _predicate_name(fact).startswith("source_record")]
    source_tokens = _tokens_for_facts(source_facts)
    direct_tokens = _tokens_for_facts(direct_facts)
    term_rows = [_audit_term(term, source_tokens=source_tokens, direct_tokens=direct_tokens) for term in terms]
    return {
        "lens": lens,
        "compile_json": str(path),
        "run": path.parent.parent.name if path.parent.parent != path.parent else "",
        "fixture": path.parent.name,
        "parsed_ok": bool(data.get("parsed_ok")),
        "direct_fact_count": len(direct_facts),
        "source_record_fact_count": len(source_facts),
        "terms": term_rows,
        "summary": _summarize_terms(term_rows),
    }


def _audit_term(term: LensTerm, *, source_tokens: set[str], direct_tokens: set[str]) -> dict[str, Any]:
    source_hits = [token for token in term.tokens if token in source_tokens]
    direct_hits = [token for token in term.tokens if token in direct_tokens]
    if direct_hits:
        status = "structural"
    elif source_hits:
        status = "source_only"
    else:
        status = "not_applicable"
    return {
        "term": term.term,
        "status": status,
        "source_hits": source_hits,
        "direct_hits": direct_hits,
    }


def _facts_from_compile(data: dict[str, Any]) -> list[str]:
    source_compile = data.get("source_compile") if isinstance(data.get("source_compile"), dict) else {}
    facts = source_compile.get("facts")
    if isinstance(facts, list):
        return [str(fact).strip() for fact in facts if str(fact).strip()]
    parsed = data.get("parsed") if isinstance(data.get("parsed"), dict) else {}
    parsed_facts = parsed.get("facts")
    if isinstance(parsed_facts, list):
        return [str(fact).strip() for fact in parsed_facts if str(fact).strip()]
    return []


def _predicate_name(fact: str) -> str:
    match = FACT_RE.match(str(fact))
    return match.group(1) if match else ""


def _tokens_for_facts(facts: list[str]) -> set[str]:
    return set(TOKEN_RE.findall(" ".join(facts).lower()))


def _summarize_terms(term_rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in term_rows:
        status = str(row["status"])
        counts[status] = counts.get(status, 0) + 1
    return dict(sorted(counts.items()))


def summarize_reports(reports: list[dict[str, Any]], terms: tuple[LensTerm, ...]) -> dict[str, Any]:
    by_status: dict[str, int] = {}
    by_term: dict[str, dict[str, int]] = {term.term: {} for term in terms}
    for report in reports:
        for row in report["terms"]:
            status = str(row["status"])
            by_status[status] = by_status.get(status, 0) + 1
            bucket = by_term.setdefault(str(row["term"]), {})
            bucket[status] = bucket.get(status, 0) + 1
    return {
        "status_counts": dict(sorted(by_status.items())),
        "term_status_counts": {key: dict(sorted(value.items())) for key, value in sorted(by_term.items())},
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Lens Vocabulary Transfer Audit",
        "",
        f"- Schema: `{payload['schema']}`",
        f"- Lens: `{payload['lens']}`",
        f"- Compiles: `{payload['compile_count']}`",
        f"- Status counts: `{payload['summary']['status_counts']}`",
        "",
        "## Term Summary",
        "",
        "| Term | Structural | Source-only | N/A |",
        "| --- | ---: | ---: | ---: |",
    ]
    for term, counts in payload["summary"]["term_status_counts"].items():
        lines.append(
            f"| `{term}` | {counts.get('structural', 0)} | {counts.get('source_only', 0)} | {counts.get('not_applicable', 0)} |"
        )
    lines.extend(
        [
            "",
            "## Fixture Summary",
            "",
            "| Run | Fixture | Direct facts | Source-record facts | Structural | Source-only | N/A |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for report in payload["reports"]:
        summary = report["summary"]
        lines.append(
            "| {run} | {fixture} | {direct} | {source} | {structural} | {source_only} | {na} |".format(
                run=f"`{report['run']}`",
                fixture=f"`{report['fixture']}`",
                direct=report["direct_fact_count"],
                source=report["source_record_fact_count"],
                structural=summary.get("structural", 0),
                source_only=summary.get("source_only", 0),
                na=summary.get("not_applicable", 0),
            )
        )
    lines.extend(["", "## Source-Only Terms", ""])
    for report in payload["reports"]:
        source_only = [row["term"] for row in report["terms"] if row["status"] == "source_only"]
        if source_only:
            lines.append(f"- `{report['fixture']}`: {', '.join(f'`{term}`' for term in source_only)}")
    return "\n".join(lines).rstrip() + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
