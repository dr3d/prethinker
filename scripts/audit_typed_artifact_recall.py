#!/usr/bin/env python3
"""Estimate typed-artifact recall against oracle answers.

This is a ceiling/proxy diagnostic, not a QA score. It asks:

    Is the answer material present in typed compile artifacts at all,
    if source-record prose/display predicates are ignored?

Two views are reported:

- typed_any: all non-source_record_* compile facts.
- typed_strict: non-source_record_* compile facts excluding prose-like atoms
  and display/text/label predicates.

If typed_strict coverage is low, query/join work cannot honestly reach high
accuracy until compile recall improves.
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


STOP_TOKENS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "been",
    "being",
    "by",
    "did",
    "do",
    "does",
    "for",
    "from",
    "in",
    "is",
    "it",
    "its",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "under",
    "was",
    "were",
    "what",
    "which",
    "who",
    "with",
}

FREE_TEXT_PREDICATE_HINTS = (
    "text",
    "display",
    "label",
    "summary",
    "description",
    "narrative",
    "quote",
    "raw",
)

PROVENANCE_ARG_RE = re.compile(r"^src_(?:line|row)_\d+$|^source_", re.IGNORECASE)


@dataclass(frozen=True)
class ParsedFact:
    predicate: str
    args: tuple[str, ...]
    clause: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--compile-root", type=Path, required=True)
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    parser.add_argument("--coverage-threshold", type=float, default=0.85)
    parser.add_argument("--partial-threshold", type=float, default=0.55)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(
        dataset_root=args.dataset_root,
        compile_root=args.compile_root,
        coverage_threshold=float(args.coverage_threshold),
        partial_threshold=float(args.partial_threshold),
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


def build_report(
    *,
    dataset_root: Path,
    compile_root: Path,
    coverage_threshold: float,
    partial_threshold: float,
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    by_fixture: dict[str, Counter[str]] = defaultdict(Counter)
    predicate_counts: Counter[str] = Counter()
    strict_predicate_counts: Counter[str] = Counter()
    fact_counts: Counter[str] = Counter()

    for fixture_dir in sorted(path for path in dataset_root.iterdir() if path.is_dir()):
        fixture = fixture_dir.name
        oracle_rows = _read_oracle(fixture_dir / "oracle.jsonl")
        compile_json = _latest_compile_json(compile_root / fixture)
        typed_any_facts, typed_strict_facts, rejected = _typed_fact_sets(compile_json)
        fact_counts["typed_any"] += len(typed_any_facts)
        fact_counts["typed_strict"] += len(typed_strict_facts)
        fact_counts["rejected_source_record_or_prose"] += rejected
        for fact in typed_any_facts:
            predicate_counts[fact.predicate] += 1
        for fact in typed_strict_facts:
            strict_predicate_counts[fact.predicate] += 1
        typed_any_text = _facts_text(typed_any_facts)
        typed_strict_text = _facts_text(typed_strict_facts)
        for oracle in oracle_rows:
            reference = str(oracle.get("reference_answer", ""))
            any_metrics = _coverage_metrics(reference, typed_any_text)
            strict_metrics = _coverage_metrics(reference, typed_strict_text)
            any_class = _coverage_class(any_metrics, coverage_threshold, partial_threshold)
            strict_class = _coverage_class(strict_metrics, coverage_threshold, partial_threshold)
            by_fixture[fixture][f"typed_any_{any_class}"] += 1
            by_fixture[fixture][f"typed_strict_{strict_class}"] += 1
            rows.append(
                {
                    "fixture": fixture,
                    "id": oracle.get("id", ""),
                    "reference_answer": reference,
                    "typed_any": any_metrics | {"class": any_class},
                    "typed_strict": strict_metrics | {"class": strict_class},
                }
            )

    summary = _summarize_rows(rows)
    return {
        "schema_version": "typed_artifact_recall_audit_v1",
        "dataset_root": str(dataset_root),
        "compile_root": str(compile_root),
        "thresholds": {
            "coverage": coverage_threshold,
            "partial": partial_threshold,
        },
        "summary": summary,
        "fact_counts": dict(fact_counts),
        "top_typed_any_predicates": dict(predicate_counts.most_common(30)),
        "top_typed_strict_predicates": dict(strict_predicate_counts.most_common(30)),
        "by_fixture": {fixture: dict(counter) for fixture, counter in sorted(by_fixture.items())},
        "rows": rows,
    }


def _read_oracle(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def _latest_compile_json(path: Path) -> Path:
    candidates = sorted(path.glob("*.json"), key=lambda item: item.stat().st_mtime)
    if not candidates:
        raise FileNotFoundError(f"No compile JSON found under {path}")
    return candidates[-1]


def _typed_fact_sets(path: Path) -> tuple[list[ParsedFact], list[ParsedFact], int]:
    data = json.loads(path.read_text(encoding="utf-8"))
    facts = data.get("source_compile", {}).get("facts", [])
    typed_any: list[ParsedFact] = []
    typed_strict: list[ParsedFact] = []
    rejected = 0
    for clause in facts:
        fact = _parse_fact(str(clause))
        if fact is None:
            continue
        if fact.predicate.startswith("source_record_"):
            rejected += 1
            continue
        typed_any.append(fact)
        if _is_strict_typed_fact(fact):
            typed_strict.append(fact)
        else:
            rejected += 1
    return typed_any, typed_strict, rejected


def _parse_fact(clause: str) -> ParsedFact | None:
    text = clause.strip()
    if text.endswith("."):
        text = text[:-1]
    match = re.match(r"^(?P<predicate>[a-z][a-zA-Z0-9_]*)\((?P<args>.*)\)$", text)
    if not match:
        return None
    return ParsedFact(
        predicate=match.group("predicate"),
        args=tuple(_split_args(match.group("args"))),
        clause=clause.strip(),
    )


def _split_args(text: str) -> list[str]:
    args: list[str] = []
    current: list[str] = []
    quote = ""
    depth = 0
    index = 0
    while index < len(text):
        char = text[index]
        if quote:
            current.append(char)
            if char == "\\" and index + 1 < len(text):
                index += 1
                current.append(text[index])
            elif char == quote:
                quote = ""
        else:
            if char in {"'", '"'}:
                quote = char
                current.append(char)
            elif char == "(":
                depth += 1
                current.append(char)
            elif char == ")":
                depth = max(0, depth - 1)
                current.append(char)
            elif char == "," and depth == 0:
                args.append("".join(current).strip())
                current = []
            else:
                current.append(char)
        index += 1
    if current or text:
        args.append("".join(current).strip())
    return args


def _is_strict_typed_fact(fact: ParsedFact) -> bool:
    predicate = fact.predicate.casefold()
    if any(hint in predicate for hint in FREE_TEXT_PREDICATE_HINTS):
        return False
    for arg in fact.args:
        if PROVENANCE_ARG_RE.search(arg.strip("'\"")):
            continue
        if _arg_looks_prose_like(arg):
            return False
    return True


def _arg_looks_prose_like(arg: str) -> bool:
    value = _display_atom(arg)
    tokens = _raw_tokens(value)
    if len(value) > 90 and len(tokens) > 8:
        return True
    if len(tokens) > 14:
        return True
    return False


def _facts_text(facts: list[ParsedFact]) -> str:
    values: list[str] = []
    for fact in facts:
        for arg in fact.args:
            clean = arg.strip().strip("'\"")
            if PROVENANCE_ARG_RE.search(clean):
                continue
            values.append(_display_atom(clean))
    return "\n".join(values)


def _coverage_metrics(reference: str, typed_text: str) -> dict[str, Any]:
    ref_tokens = _content_tokens(reference)
    typed_tokens = set(_content_tokens(typed_text))
    token_hits = [token for token in ref_tokens if token in typed_tokens]
    ref_numbers = _numbers(reference)
    typed_raw = unicodedata.normalize("NFKC", typed_text)
    number_hits = [number for number in ref_numbers if number in typed_raw]
    token_coverage = len(token_hits) / len(ref_tokens) if ref_tokens else 0.0
    number_coverage = len(number_hits) / len(ref_numbers) if ref_numbers else None
    return {
        "reference_token_count": len(ref_tokens),
        "token_hit_count": len(token_hits),
        "token_coverage": round(token_coverage, 6),
        "reference_number_count": len(ref_numbers),
        "number_hit_count": len(number_hits),
        "number_coverage": None if number_coverage is None else round(number_coverage, 6),
        "missing_tokens": sorted(set(ref_tokens) - typed_tokens)[:40],
    }


def _coverage_class(metrics: dict[str, Any], coverage_threshold: float, partial_threshold: float) -> str:
    token_coverage = float(metrics.get("token_coverage") or 0)
    number_coverage = metrics.get("number_coverage")
    numbers_ok = number_coverage is None or float(number_coverage) >= 1.0
    if token_coverage >= coverage_threshold and numbers_ok:
        return "likely_available"
    if token_coverage >= partial_threshold or (number_coverage is not None and float(number_coverage) >= 0.8):
        return "partial_available"
    return "not_available"


def _summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {"row_count": len(rows)}
    for view in ("typed_any", "typed_strict"):
        counts = Counter(row[view]["class"] for row in rows)
        avg_token = sum(row[view]["token_coverage"] for row in rows) / len(rows) if rows else 0
        number_rows = [row for row in rows if row[view]["number_coverage"] is not None]
        full_numbers = sum(1 for row in number_rows if row[view]["number_coverage"] == 1.0)
        out[view] = {
            "class_counts": dict(sorted(counts.items())),
            "likely_available": counts.get("likely_available", 0),
            "partial_available": counts.get("partial_available", 0),
            "not_available": counts.get("not_available", 0),
            "likely_available_rate": round(counts.get("likely_available", 0) / len(rows), 6) if rows else 0.0,
            "partial_or_likely_rate": round(
                (counts.get("likely_available", 0) + counts.get("partial_available", 0)) / len(rows),
                6,
            )
            if rows
            else 0.0,
            "avg_token_coverage": round(avg_token, 6),
            "number_rows": len(number_rows),
            "full_number_coverage_rows": full_numbers,
        }
    return out


def _display_atom(value: str) -> str:
    text = str(value or "").strip().strip("'\"")
    text = text.replace("_", " ")
    text = re.sub(r"\bv (\d)", r"\1", text)
    return text


def _normalize(value: str) -> str:
    text = unicodedata.normalize("NFKC", str(value or "")).casefold()
    text = text.replace("§", " section ")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", text)).strip()


def _raw_tokens(value: str) -> list[str]:
    return [token for token in _normalize(value).split() if token]


def _content_tokens(value: str) -> list[str]:
    return [token for token in _raw_tokens(value) if len(token) > 1 and token not in STOP_TOKENS]


def _numbers(value: str) -> list[str]:
    return re.findall(r"\b\d+(?:\.\d+)?\b", unicodedata.normalize("NFKC", str(value or "")))


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Typed Artifact Recall Audit",
        "",
        f"- Schema: `{report['schema_version']}`",
        f"- Dataset: `{report['dataset_root']}`",
        f"- Compile root: `{report['compile_root']}`",
        f"- Rows: `{summary['row_count']}`",
        "",
        "## Summary",
        "",
        "| View | Likely available | Partial available | Not available | Likely rate | Partial+likely rate | Avg token coverage | Full number rows |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for view in ("typed_any", "typed_strict"):
        data = summary[view]
        lines.append(
            "| `{}` | {} | {} | {} | {} | {} | {} | {}/{} |".format(
                view,
                data["likely_available"],
                data["partial_available"],
                data["not_available"],
                data["likely_available_rate"],
                data["partial_or_likely_rate"],
                data["avg_token_coverage"],
                data["full_number_coverage_rows"],
                data["number_rows"],
            )
        )
    lines.extend(
        [
            "",
            "## Meaning",
            "",
            "`typed_any` excludes `source_record_*` but may still include prose-like normalized atoms.",
            "`typed_strict` also excludes prose-like atoms and display/text/label predicates.",
            "Predicate names are not counted as answer tokens; only typed argument values contribute coverage.",
            "This is a deterministic recall proxy, not proof that a query layer can derive the answer.",
            "",
            "## By Fixture",
            "",
            "| Fixture | Strict likely | Strict partial | Strict not available | Any likely | Any partial | Any not available |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for fixture, counts in report["by_fixture"].items():
        lines.append(
            "| `{}` | {} | {} | {} | {} | {} | {} |".format(
                fixture,
                counts.get("typed_strict_likely_available", 0),
                counts.get("typed_strict_partial_available", 0),
                counts.get("typed_strict_not_available", 0),
                counts.get("typed_any_likely_available", 0),
                counts.get("typed_any_partial_available", 0),
                counts.get("typed_any_not_available", 0),
            )
        )
    lines.extend(
        [
            "",
            "## Least Covered Rows",
            "",
            "| Row | Strict class | Strict token coverage | Any class | Any token coverage | Missing strict tokens |",
            "| --- | --- | ---: | --- | ---: | --- |",
        ]
    )
    sorted_rows = sorted(report["rows"], key=lambda row: (row["typed_strict"]["token_coverage"], row["fixture"], row["id"]))
    for row in sorted_rows[:40]:
        lines.append(
            "| `{} {}` | `{}` | {} | `{}` | {} | `{}` |".format(
                row["fixture"],
                row["id"],
                row["typed_strict"]["class"],
                row["typed_strict"]["token_coverage"],
                row["typed_any"]["class"],
                row["typed_any"]["token_coverage"],
                ", ".join(row["typed_strict"]["missing_tokens"][:12]),
            )
        )
    return "\n".join(lines).rstrip() + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
