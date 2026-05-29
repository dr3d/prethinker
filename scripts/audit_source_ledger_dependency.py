#!/usr/bin/env python3
"""Audit how much QA scoring depends on source-record ledger evidence.

Source ledgers preserve source text and source-row structure. That is useful
for provenance, but dangerous if it becomes a shadow semantic retrieval engine.
This audit does not declare source-ledger evidence forbidden. It separates:

- direct compiled predicate support;
- source-ledger-only support;
- mixed support.

Use it to keep score claims honest after sign-clean changes.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path, help="QA JSON file(s) or directories containing QA JSON files.")
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    parser.add_argument(
        "--fail-on-source-ledger-only-exact",
        action="store_true",
        help="Return non-zero if any exact row is supported only by source-record predicates.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(args.paths)
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(render_markdown(report), encoding="utf-8")
    if not args.out_json and not args.out_md:
        print(json.dumps(report, indent=2, sort_keys=True))
    if args.fail_on_source_ledger_only_exact and report["summary"]["source_ledger_only_exact"] > 0:
        return 1
    return 0


def build_report(paths: list[Path]) -> dict[str, Any]:
    qa_files = sorted({path.resolve() for path in paths for path in _iter_qa_files(path)})
    rows: list[dict[str, Any]] = []
    verdict_counts: Counter[str] = Counter()
    exact_support_counts: Counter[str] = Counter()
    source_predicates: Counter[str] = Counter()
    direct_predicates: Counter[str] = Counter()
    by_fixture: dict[str, Counter[str]] = defaultdict(Counter)
    source_only_examples: list[dict[str, Any]] = []

    for qa_file in qa_files:
        data = json.loads(qa_file.read_text(encoding="utf-8"))
        fixture = qa_file.parent.name
        for row in data.get("rows", []) or []:
            if not isinstance(row, dict):
                continue
            verdict = str((row.get("reference_judge") or {}).get("verdict", "")).strip() or "unjudged"
            verdict_counts[verdict] += 1
            source_preds, direct_preds = _row_support_predicates(row)
            for predicate in source_preds:
                source_predicates[predicate] += 1
            for predicate in direct_preds:
                direct_predicates[predicate] += 1
            support_class = _support_class(source_preds=source_preds, direct_preds=direct_preds)
            if verdict == "exact":
                exact_support_counts[support_class] += 1
                by_fixture[fixture][support_class] += 1
                if support_class == "source_ledger_only" and len(source_only_examples) < 50:
                    source_only_examples.append(
                        {
                            "fixture": fixture,
                            "id": row.get("id", ""),
                            "question": row.get("utterance", ""),
                            "source_predicates": sorted(source_preds),
                            "direct_predicates": sorted(direct_preds),
                        }
                    )
            rows.append(
                {
                    "fixture": fixture,
                    "id": row.get("id", ""),
                    "verdict": verdict,
                    "support_class": support_class,
                    "source_predicates": sorted(source_preds),
                    "direct_predicates": sorted(direct_preds),
                }
            )

    exact_total = sum(exact_support_counts.values())
    return {
        "schema_version": "source_ledger_dependency_audit_v1",
        "qa_file_count": len(qa_files),
        "summary": {
            "row_count": len(rows),
            "verdict_counts": dict(sorted(verdict_counts.items())),
            "exact_rows": exact_total,
            "direct_only_exact": exact_support_counts.get("direct_only", 0),
            "mixed_exact": exact_support_counts.get("mixed", 0),
            "source_ledger_only_exact": exact_support_counts.get("source_ledger_only", 0),
            "no_evidence_exact": exact_support_counts.get("no_evidence", 0),
            "source_ledger_only_exact_share": _share(exact_support_counts.get("source_ledger_only", 0), exact_total),
            "mixed_exact_share": _share(exact_support_counts.get("mixed", 0), exact_total),
        },
        "exact_support_counts": dict(sorted(exact_support_counts.items())),
        "source_predicate_counts": dict(source_predicates.most_common(40)),
        "direct_predicate_counts": dict(direct_predicates.most_common(40)),
        "by_fixture": {fixture: dict(counts) for fixture, counts in sorted(by_fixture.items())},
        "source_ledger_only_examples": source_only_examples,
        "rows": rows,
    }


def _iter_qa_files(path: Path) -> list[Path]:
    if path.is_file() and path.suffix.lower() == ".json":
        return [path]
    if not path.exists():
        return []
    files: list[Path] = []
    for candidate in path.rglob("*.json"):
        try:
            text = candidate.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if '"rows"' in text and '"reference_judge"' in text:
            files.append(candidate)
    return files


def _row_support_predicates(row: dict[str, Any]) -> tuple[set[str], set[str]]:
    source_preds: set[str] = set()
    direct_preds: set[str] = set()
    for query_result in row.get("query_results", []) or []:
        result = query_result.get("result") if isinstance(query_result, dict) else None
        if not isinstance(result, dict):
            continue
        result_rows = result.get("rows")
        if not isinstance(result_rows, list) or not result_rows:
            continue
        predicate = str(result.get("predicate", "")).strip()
        if not predicate:
            continue
        if _is_source_ledger_predicate(predicate):
            source_preds.add(predicate)
        else:
            direct_preds.add(predicate)
    return source_preds, direct_preds


def _is_source_ledger_predicate(predicate: str) -> bool:
    return predicate.startswith("source_record_")


def _support_class(*, source_preds: set[str], direct_preds: set[str]) -> str:
    if source_preds and direct_preds:
        return "mixed"
    if source_preds:
        return "source_ledger_only"
    if direct_preds:
        return "direct_only"
    return "no_evidence"


def _share(count: int, total: int) -> float:
    if not total:
        return 0.0
    return round(count / total, 6)


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Source Ledger Dependency Audit",
        "",
        f"- Schema: `{report['schema_version']}`",
        f"- QA files: `{report['qa_file_count']}`",
        f"- Rows: `{summary['row_count']}`",
        f"- Verdict counts: `{summary['verdict_counts']}`",
        f"- Exact rows: `{summary['exact_rows']}`",
        f"- Direct-only exact: `{summary['direct_only_exact']}`",
        f"- Mixed exact: `{summary['mixed_exact']}` share `{summary['mixed_exact_share']}`",
        f"- Source-ledger-only exact: `{summary['source_ledger_only_exact']}` share `{summary['source_ledger_only_exact_share']}`",
        f"- No-evidence exact: `{summary['no_evidence_exact']}`",
        "",
        "## Meaning",
        "",
        "Source-ledger-only exact rows are not automatically wrong, but they are not direct compiled-fact evidence.",
        "Use this count as a claim qualifier and as a warning against source-ledger search becoming a shadow semantic engine.",
    ]
    if report.get("by_fixture"):
        lines.extend(["", "## By Fixture", "", "| Fixture | Direct-only exact | Mixed exact | Source-ledger-only exact | No-evidence exact |", "| --- | ---: | ---: | ---: | ---: |"])
        for fixture, counts in report["by_fixture"].items():
            lines.append(
                "| `{}` | {} | {} | {} | {} |".format(
                    fixture,
                    counts.get("direct_only", 0),
                    counts.get("mixed", 0),
                    counts.get("source_ledger_only", 0),
                    counts.get("no_evidence", 0),
                )
            )
    examples = report.get("source_ledger_only_examples", [])
    if examples:
        lines.extend(["", "## Sample Source-Ledger-Only Exact Rows", "", "| Fixture | Row | Source predicates | Question |", "| --- | --- | --- | --- |"])
        for row in examples[:20]:
            lines.append(
                "| `{}` | `{}` | `{}` | {} |".format(
                    row.get("fixture", ""),
                    row.get("id", ""),
                    ", ".join(row.get("source_predicates", []))[:180],
                    _md_cell(str(row.get("question", ""))[:220]),
                )
            )
    return "\n".join(lines).rstrip() + "\n"


def _md_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


if __name__ == "__main__":
    raise SystemExit(main())
