#!/usr/bin/env python3
"""Compare typed atom inventories between two compile artifacts.

This is a compile-only diagnostic. It compares the typed predicate/fact library
emitted by two compile runs without reading source prose, QA questions, oracle
answers, or source-record text. Its purpose is to make ontology drift visible:

    Which signatures appeared or disappeared?
    Which signatures changed fact counts?
    How much fact-level agreement survived?

The report is not a query router and must not be used to map natural language to
predicates.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.audit_kb_atom_inventory import (
    FREE_TEXT_PREDICATE_HINTS,
    SOURCE_RECORD_PREFIX,
    ParsedFact,
    _arg_kind,
    _latest_compile_json,
    _parse_fact,
    _typed_facts,
)
from src.carrier_contract_registry import carrier_contract


PROSE_REDACTION_ATOM = "__PROSE_REDACTED__"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--left", type=Path, required=True, help="Left compile JSON or directory.")
    parser.add_argument("--right", type=Path, required=True, help="Right compile JSON or directory.")
    parser.add_argument("--left-label", default="left")
    parser.add_argument("--right-label", default="right")
    parser.add_argument(
        "--include-source-record",
        action="store_true",
        help="Include source_record_* atoms. Default excludes them from the typed inventory.",
    )
    parser.add_argument(
        "--include-prose-like",
        action="store_true",
        help="Include text/display/label/description-like predicates and long prose-like arguments.",
    )
    parser.add_argument("--max-examples", type=int, default=8)
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_comparison(
        left=args.left,
        right=args.right,
        left_label=str(args.left_label),
        right_label=str(args.right_label),
        include_source_record=bool(args.include_source_record),
        include_prose_like=bool(args.include_prose_like),
        max_examples=max(0, int(args.max_examples)),
    )
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(render_markdown(report), encoding="utf-8")
    if not args.out_json and not args.out_md:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0


def build_comparison(
    *,
    left: Path,
    right: Path,
    left_label: str = "left",
    right_label: str = "right",
    include_source_record: bool = False,
    include_prose_like: bool = False,
    max_examples: int = 8,
) -> dict[str, Any]:
    left_json = _resolve_compile_json(left)
    right_json = _resolve_compile_json(right)
    left_facts, left_rejected = _comparison_facts(
        left_json,
        include_source_record=include_source_record,
        include_prose_like=include_prose_like,
    )
    right_facts, right_rejected = _comparison_facts(
        right_json,
        include_source_record=include_source_record,
        include_prose_like=include_prose_like,
    )

    left_index = _index_facts(left_facts)
    right_index = _index_facts(right_facts)
    left_fact_set = set(left_index["facts"])
    right_fact_set = set(right_index["facts"])
    left_signatures = set(left_index["signature_counts"])
    right_signatures = set(right_index["signature_counts"])
    left_predicates = set(left_index["predicate_counts"])
    right_predicates = set(right_index["predicate_counts"])

    added_facts = sorted(right_fact_set - left_fact_set)
    removed_facts = sorted(left_fact_set - right_fact_set)
    common_facts = left_fact_set & right_fact_set
    signature_rows = _signature_delta_rows(left_index, right_index, max_examples=max_examples)
    predicate_rows = _predicate_delta_rows(left_index, right_index)

    return {
        "schema_version": "compile_atom_inventory_comparison_v1",
        "left": {
            "label": left_label,
            "path": str(left),
            "compile_json": str(left_json),
            "summary": _side_summary(left_index, left_rejected),
        },
        "right": {
            "label": right_label,
            "path": str(right),
            "compile_json": str(right_json),
            "summary": _side_summary(right_index, right_rejected),
        },
        "settings": {
            "include_source_record": include_source_record,
            "include_prose_like": include_prose_like,
            "redact_prose_arguments": not include_prose_like,
            "max_examples": max_examples,
        },
        "summary": {
            "left_fact_count": len(left_fact_set),
            "right_fact_count": len(right_fact_set),
            "common_fact_count": len(common_facts),
            "added_fact_count": len(added_facts),
            "removed_fact_count": len(removed_facts),
            "fact_jaccard": _jaccard(left_fact_set, right_fact_set),
            "left_signature_count": len(left_signatures),
            "right_signature_count": len(right_signatures),
            "common_signature_count": len(left_signatures & right_signatures),
            "added_signature_count": len(right_signatures - left_signatures),
            "removed_signature_count": len(left_signatures - right_signatures),
            "signature_jaccard": _jaccard(left_signatures, right_signatures),
            "left_predicate_count": len(left_predicates),
            "right_predicate_count": len(right_predicates),
            "common_predicate_count": len(left_predicates & right_predicates),
            "added_predicate_count": len(right_predicates - left_predicates),
            "removed_predicate_count": len(left_predicates - right_predicates),
            "predicate_jaccard": _jaccard(left_predicates, right_predicates),
            "left_registered_signature_count": _registered_signature_count(left_signatures),
            "right_registered_signature_count": _registered_signature_count(right_signatures),
            "common_registered_signature_count": _registered_signature_count(left_signatures & right_signatures),
            "added_registered_signature_count": _registered_signature_count(right_signatures - left_signatures),
            "removed_registered_signature_count": _registered_signature_count(left_signatures - right_signatures),
            "changed_common_signature_count": sum(
                1
                for row in signature_rows
                if row["left_count"] > 0 and row["right_count"] > 0 and row["delta"] != 0
            ),
        },
        "added_signatures": [
            row for row in signature_rows if row["left_count"] == 0 and row["right_count"] > 0
        ],
        "removed_signatures": [
            row for row in signature_rows if row["left_count"] > 0 and row["right_count"] == 0
        ],
        "changed_common_signatures": [
            row for row in signature_rows if row["left_count"] > 0 and row["right_count"] > 0 and row["delta"] != 0
        ],
        "unchanged_common_signatures": [
            row for row in signature_rows if row["left_count"] > 0 and row["right_count"] > 0 and row["delta"] == 0
        ],
        "predicate_deltas": predicate_rows,
        "added_fact_examples": added_facts[:max_examples],
        "removed_fact_examples": removed_facts[:max_examples],
    }


def _resolve_compile_json(path: Path) -> Path:
    if path.is_file():
        return path
    if not path.exists():
        raise FileNotFoundError(path)
    direct = sorted(path.glob("*.json"), key=lambda item: (item.stat().st_mtime, item.name))
    if direct:
        return direct[-1]
    return _latest_compile_json(path)


def _comparison_facts(
    path: Path,
    *,
    include_source_record: bool,
    include_prose_like: bool,
) -> tuple[list[ParsedFact], Counter[str]]:
    if include_prose_like:
        return _typed_facts(
            path,
            include_source_record=include_source_record,
            include_prose_like=True,
        )
    data = json.loads(path.read_text(encoding="utf-8"))
    raw_facts = data.get("source_compile", {}).get("facts", [])
    facts: list[ParsedFact] = []
    rejected: Counter[str] = Counter()
    for clause in raw_facts:
        fact = _parse_fact(str(clause))
        if fact is None:
            rejected["unparsed"] += 1
            continue
        if fact.predicate.startswith(SOURCE_RECORD_PREFIX) and not include_source_record:
            rejected["source_record"] += 1
            continue
        if _predicate_is_prose_like(fact.predicate):
            rejected["prose_like_predicate"] += 1
            continue
        redacted_args: list[str] = []
        redacted_count = 0
        for arg in fact.args:
            if _arg_kind(arg) == "long_text":
                redacted_args.append(PROSE_REDACTION_ATOM)
                redacted_count += 1
            else:
                redacted_args.append(arg)
        if redacted_count:
            rejected["prose_arg_redacted"] += redacted_count
        facts.append(
            ParsedFact(
                predicate=fact.predicate,
                args=tuple(redacted_args),
                clause=_canonical_fact(ParsedFact(fact.predicate, tuple(redacted_args), fact.clause)),
            )
        )
    return facts, rejected


def _predicate_is_prose_like(predicate: str) -> bool:
    value = predicate.casefold()
    return any(hint in value for hint in FREE_TEXT_PREDICATE_HINTS)


def _index_facts(facts: list[ParsedFact]) -> dict[str, Any]:
    fact_strings = [_canonical_fact(fact) for fact in facts]
    by_signature: dict[str, list[str]] = defaultdict(list)
    for fact, canonical in zip(facts, fact_strings):
        by_signature[fact.signature].append(canonical)
    return {
        "facts": fact_strings,
        "signature_counts": Counter(fact.signature for fact in facts),
        "predicate_counts": Counter(fact.predicate for fact in facts),
        "facts_by_signature": {signature: sorted(values) for signature, values in by_signature.items()},
    }


def _canonical_fact(fact: ParsedFact) -> str:
    return f"{fact.predicate}({', '.join(fact.args)})."


def _side_summary(index: dict[str, Any], rejected: Counter[str]) -> dict[str, Any]:
    return {
        "typed_fact_count": len(index["facts"]),
        "predicate_count": len(index["predicate_counts"]),
        "signature_count": len(index["signature_counts"]),
        "rejected_counts": dict(sorted(rejected.items())),
        "top_signatures": dict(index["signature_counts"].most_common(25)),
        "top_predicates": dict(index["predicate_counts"].most_common(25)),
    }


def _signature_delta_rows(
    left_index: dict[str, Any],
    right_index: dict[str, Any],
    *,
    max_examples: int,
) -> list[dict[str, Any]]:
    left_counts = left_index["signature_counts"]
    right_counts = right_index["signature_counts"]
    left_by_signature = left_index["facts_by_signature"]
    right_by_signature = right_index["facts_by_signature"]
    rows: list[dict[str, Any]] = []
    for signature in sorted(set(left_counts) | set(right_counts)):
        left_facts = set(left_by_signature.get(signature, []))
        right_facts = set(right_by_signature.get(signature, []))
        rows.append(
            {
                "signature": signature,
                "registered_contract": carrier_contract(signature) is not None,
                "left_count": int(left_counts.get(signature, 0)),
                "right_count": int(right_counts.get(signature, 0)),
                "delta": int(right_counts.get(signature, 0)) - int(left_counts.get(signature, 0)),
                "common_fact_count": len(left_facts & right_facts),
                "fact_jaccard": _jaccard(left_facts, right_facts),
                "added_examples": sorted(right_facts - left_facts)[:max_examples],
                "removed_examples": sorted(left_facts - right_facts)[:max_examples],
            }
        )
    return sorted(rows, key=lambda row: (abs(row["delta"]), row["signature"]), reverse=True)


def _predicate_delta_rows(left_index: dict[str, Any], right_index: dict[str, Any]) -> list[dict[str, Any]]:
    left_counts = left_index["predicate_counts"]
    right_counts = right_index["predicate_counts"]
    rows = []
    for predicate in sorted(set(left_counts) | set(right_counts)):
        rows.append(
            {
                "predicate": predicate,
                "left_count": int(left_counts.get(predicate, 0)),
                "right_count": int(right_counts.get(predicate, 0)),
                "delta": int(right_counts.get(predicate, 0)) - int(left_counts.get(predicate, 0)),
            }
        )
    return sorted(rows, key=lambda row: (abs(row["delta"]), row["predicate"]), reverse=True)


def _registered_signature_count(signatures: set[str]) -> int:
    return sum(1 for signature in signatures if carrier_contract(signature) is not None)


def _jaccard(left: set[Any], right: set[Any]) -> float:
    union = left | right
    if not union:
        return 0.0
    return round(len(left & right) / len(union), 6)


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    left = report["left"]
    right = report["right"]
    lines = [
        "# Compile Atom Inventory Comparison",
        "",
        f"- Schema: `{report['schema_version']}`",
        f"- Left: `{left['label']}`",
        f"- Left JSON: `{left['compile_json']}`",
        f"- Right: `{right['label']}`",
        f"- Right JSON: `{right['compile_json']}`",
        f"- Include source records: `{report['settings']['include_source_record']}`",
        f"- Include prose-like atoms: `{report['settings']['include_prose_like']}`",
        f"- Redact prose arguments: `{report['settings']['redact_prose_arguments']}`",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Left typed facts | {summary['left_fact_count']} |",
        f"| Right typed facts | {summary['right_fact_count']} |",
        f"| Common typed facts | {summary['common_fact_count']} |",
        f"| Added facts | {summary['added_fact_count']} |",
        f"| Removed facts | {summary['removed_fact_count']} |",
        f"| Fact Jaccard | {summary['fact_jaccard']} |",
        f"| Left signatures | {summary['left_signature_count']} |",
        f"| Right signatures | {summary['right_signature_count']} |",
        f"| Common signatures | {summary['common_signature_count']} |",
        f"| Added signatures | {summary['added_signature_count']} |",
        f"| Removed signatures | {summary['removed_signature_count']} |",
        f"| Signature Jaccard | {summary['signature_jaccard']} |",
        f"| Changed common signatures | {summary['changed_common_signature_count']} |",
        f"| Predicate Jaccard | {summary['predicate_jaccard']} |",
        f"| Left registered signatures | {summary['left_registered_signature_count']} |",
        f"| Right registered signatures | {summary['right_registered_signature_count']} |",
        f"| Common registered signatures | {summary['common_registered_signature_count']} |",
        f"| Added registered signatures | {summary['added_registered_signature_count']} |",
        f"| Removed registered signatures | {summary['removed_registered_signature_count']} |",
        "",
        "## Added Signatures",
        "",
        "| Signature | Registered | Left | Right | Fact Jaccard | Examples |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for row in report["added_signatures"][:25]:
        lines.append(_signature_row(row, added=True))
    lines.extend(
        [
            "",
            "## Removed Signatures",
            "",
            "| Signature | Registered | Left | Right | Fact Jaccard | Examples |",
            "| --- | --- | ---: | ---: | ---: | --- |",
        ]
    )
    for row in report["removed_signatures"][:25]:
        lines.append(_signature_row(row, added=False))
    lines.extend(
        [
            "",
            "## Changed Common Signatures",
            "",
            "| Signature | Registered | Left | Right | Delta | Fact Jaccard |",
            "| --- | --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in report["changed_common_signatures"][:40]:
        lines.append(
            "| `{}` | {} | {} | {} | {} | {} |".format(
                row["signature"],
                "yes" if row["registered_contract"] else "no",
                row["left_count"],
                row["right_count"],
                row["delta"],
                row["fact_jaccard"],
            )
        )
    lines.extend(
        [
            "",
            "## Predicate Deltas",
            "",
            "| Predicate | Left | Right | Delta |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for row in report["predicate_deltas"][:40]:
        if row["delta"] == 0:
            continue
        lines.append(
            "| `{}` | {} | {} | {} |".format(
                row["predicate"],
                row["left_count"],
                row["right_count"],
                row["delta"],
            )
        )
    lines.extend(
        [
            "",
            "## Note",
            "",
            "This report compares typed compile atoms only. It excludes source-record and prose-like atoms by default and is not a query router.",
        ]
    )
    return "\n".join(lines) + "\n"


def _signature_row(row: dict[str, Any], *, added: bool) -> str:
    examples = row["added_examples"] if added else row["removed_examples"]
    rendered_examples = "<br>".join(f"`{example}`" for example in examples[:3])
    return "| `{}` | {} | {} | {} | {} | {} |".format(
        row["signature"],
        "yes" if row["registered_contract"] else "no",
        row["left_count"],
        row["right_count"],
        row["fact_jaccard"],
        rendered_examples,
    )


if __name__ == "__main__":
    raise SystemExit(main())
