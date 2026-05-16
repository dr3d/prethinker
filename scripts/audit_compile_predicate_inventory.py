#!/usr/bin/env python3
"""Summarize candidate and admitted predicates across compile JSON artifacts."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


PREDICATE_RE = re.compile(r"^\s*(?P<name>[a-z][A-Za-z0-9_]*)\s*\((?P<args>.*)\)\s*\.?\s*$")


def iter_compile_jsons(paths: list[str]) -> list[Path]:
    out: list[Path] = []
    for raw in paths:
        path = Path(raw)
        if path.is_file() and path.suffix.lower() == ".json":
            out.append(path)
        elif path.is_dir():
            out.extend(sorted(path.rglob("domain_bootstrap_file*.json")))
    return sorted(dict.fromkeys(out))


def signature_from_clause(clause: str) -> str:
    text = str(clause or "").strip()
    if ":-" in text:
        text = text.split(":-", 1)[0].strip()
    match = PREDICATE_RE.match(text)
    if not match:
        return ""
    args = match.group("args").strip()
    if not args:
        arity = 0
    else:
        arity = 1
        depth = 0
        for char in args:
            if char == "(":
                depth += 1
            elif char == ")":
                depth = max(0, depth - 1)
            elif char == "," and depth == 0:
                arity += 1
    return f"{match.group('name')}/{arity}"


def normalize_candidate(value: Any) -> str:
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return ""
        if "/" in text and "(" not in text:
            return text
        sig = signature_from_clause(text)
        if sig:
            return sig
        match = re.match(r"^\s*([a-z][A-Za-z0-9_]*)\s*/\s*(\d+)\s*$", text)
        if match:
            return f"{match.group(1)}/{match.group(2)}"
        return text
    if isinstance(value, dict):
        signature = str(value.get("signature") or "").strip()
        if signature:
            return normalize_candidate(signature)
        name = str(value.get("name") or value.get("predicate") or "").strip()
        arity = value.get("arity")
        if name and arity is not None:
            return f"{name}/{arity}"
        if name:
            return name
    return ""


def fixture_name(path: Path, payload: dict[str, Any]) -> str:
    text_file = str(payload.get("text_file") or "")
    if text_file:
        parent = Path(text_file).parent.name
        if parent:
            return parent
    if path.parent.name:
        return path.parent.name
    return path.stem


def summarize(paths: list[str]) -> dict[str, Any]:
    compile_paths = iter_compile_jsons(paths)
    candidate_counter: Counter[str] = Counter()
    admitted_counter: Counter[str] = Counter()
    fixture_candidate_sets: dict[str, set[str]] = {}
    fixture_admitted_sets: dict[str, set[str]] = {}
    fixture_rows: list[dict[str, Any]] = []
    parse_failures: list[str] = []

    for path in compile_paths:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            parse_failures.append(str(path))
            continue
        fixture = fixture_name(path, payload)
        parsed = payload.get("parsed") if isinstance(payload.get("parsed"), dict) else {}
        source_compile = payload.get("source_compile") if isinstance(payload.get("source_compile"), dict) else {}
        candidates = [
            sig
            for raw in parsed.get("candidate_predicates", []) or []
            if (sig := normalize_candidate(raw))
        ]
        facts = source_compile.get("facts", []) if isinstance(source_compile.get("facts"), list) else []
        rules = source_compile.get("rules", []) if isinstance(source_compile.get("rules"), list) else []
        queries = source_compile.get("queries", []) if isinstance(source_compile.get("queries"), list) else []
        admitted = [sig for clause in [*facts, *rules, *queries] if (sig := signature_from_clause(str(clause)))]

        candidate_counter.update(candidates)
        admitted_counter.update(admitted)
        fixture_candidate_sets[fixture] = set(candidates)
        fixture_admitted_sets[fixture] = set(admitted)
        fixture_rows.append(
            {
                "fixture": fixture,
                "path": str(path),
                "parsed_ok": bool(payload.get("parsed_ok")),
                "candidate_predicate_count": len(candidates),
                "unique_candidate_predicate_count": len(set(candidates)),
                "admitted_clause_predicate_count": len(admitted),
                "unique_admitted_predicate_count": len(set(admitted)),
                "admitted_count": source_compile.get("admitted_count"),
                "skipped_count": source_compile.get("skipped_count"),
                "rough_score": (payload.get("score") or {}).get("rough_score") if isinstance(payload.get("score"), dict) else None,
            }
        )

    candidate_fixture_counts: Counter[str] = Counter()
    admitted_fixture_counts: Counter[str] = Counter()
    for sigs in fixture_candidate_sets.values():
        candidate_fixture_counts.update(sigs)
    for sigs in fixture_admitted_sets.values():
        admitted_fixture_counts.update(sigs)

    def top_rows(counter: Counter[str], fixture_counter: Counter[str], limit: int) -> list[dict[str, Any]]:
        return [
            {"predicate": pred, "occurrences": count, "fixtures": fixture_counter.get(pred, 0)}
            for pred, count in counter.most_common(limit)
        ]

    unique_candidate = set(candidate_counter)
    unique_admitted = set(admitted_counter)
    return {
        "artifact_count": len(compile_paths),
        "parsed_artifact_count": len(fixture_rows),
        "parse_failures": parse_failures,
        "totals": {
            "candidate_predicate_mentions": sum(candidate_counter.values()),
            "unique_candidate_predicates": len(unique_candidate),
            "admitted_clause_predicate_mentions": sum(admitted_counter.values()),
            "unique_admitted_predicates": len(unique_admitted),
            "candidate_not_admitted_unique": len(unique_candidate - unique_admitted),
            "admitted_not_candidate_unique": len(unique_admitted - unique_candidate),
        },
        "fixtures": sorted(fixture_rows, key=lambda row: row["fixture"]),
        "candidate_predicates": top_rows(candidate_counter, candidate_fixture_counts, len(candidate_counter)),
        "admitted_predicates": top_rows(admitted_counter, admitted_fixture_counts, len(admitted_counter)),
        "top_candidate_predicates": top_rows(candidate_counter, candidate_fixture_counts, 80),
        "top_admitted_predicates": top_rows(admitted_counter, admitted_fixture_counts, 120),
        "candidate_not_admitted": sorted(unique_candidate - unique_admitted),
        "admitted_not_candidate": sorted(unique_admitted - unique_candidate),
    }


def render_markdown(payload: dict[str, Any]) -> str:
    totals = payload["totals"]
    lines = [
        "# Compile Predicate Inventory",
        "",
        f"- Compile artifacts scanned: `{payload['artifact_count']}`",
        f"- Parsed artifacts: `{payload['parsed_artifact_count']}`",
        f"- Candidate predicate mentions: `{totals['candidate_predicate_mentions']}`",
        f"- Unique candidate predicates: `{totals['unique_candidate_predicates']}`",
        f"- Admitted predicate mentions: `{totals['admitted_clause_predicate_mentions']}`",
        f"- Unique admitted predicates: `{totals['unique_admitted_predicates']}`",
        f"- Candidate predicates not admitted anywhere: `{totals['candidate_not_admitted_unique']}`",
        f"- Admitted predicates not listed as candidates anywhere: `{totals['admitted_not_candidate_unique']}`",
        "",
        "## Top Admitted Predicates",
        "",
        "| Predicate | Clause mentions | Fixtures |",
        "| --- | ---: | ---: |",
    ]
    for row in payload["top_admitted_predicates"][:40]:
        lines.append(f"| `{row['predicate']}` | {row['occurrences']} | {row['fixtures']} |")
    lines.extend(["", "## Top Candidate Predicates", "", "| Predicate | Mentions | Fixtures |", "| --- | ---: | ---: |"])
    for row in payload["top_candidate_predicates"][:40]:
        lines.append(f"| `{row['predicate']}` | {row['occurrences']} | {row['fixtures']} |")
    lines.extend(["", "## Fixtures", "", "| Fixture | Candidates | Unique candidates | Admitted mentions | Unique admitted | Skipped | Rough score |", "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"])
    for row in payload["fixtures"]:
        rough = row.get("rough_score")
        rough_text = "" if rough is None else str(rough)
        lines.append(
            f"| `{row['fixture']}` | {row['candidate_predicate_count']} | {row['unique_candidate_predicate_count']} | "
            f"{row['admitted_clause_predicate_count']} | {row['unique_admitted_predicate_count']} | "
            f"{row.get('skipped_count') if row.get('skipped_count') is not None else ''} | {rough_text} |"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+")
    parser.add_argument("--out-json", required=True)
    parser.add_argument("--out-md", required=True)
    args = parser.parse_args()

    payload = summarize(args.paths)
    out_json = Path(args.out_json)
    out_md = Path(args.out_md)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    out_md.write_text(render_markdown(payload), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
