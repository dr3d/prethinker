"""Merge direct facts from a baseline compile and a candidate compile.

The merge is conservative: keep the candidate source-record ledger, preserve all
baseline direct facts, and append candidate direct facts that are not already
present. This supports direct-surface replay experiments where a candidate adds a
new surface but drops previously accepted backbone rows.
"""

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.audit_compile_surface_invariants import _facts_from_compile, _predicate_name


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-compile", type=Path, required=True)
    parser.add_argument("--candidate-compile", type=Path, required=True)
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-md", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = merge_compile_files(args.baseline_compile, args.candidate_compile)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload["compile"], indent=2, sort_keys=True), encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(render_markdown(payload), encoding="utf-8")
    return 0


def merge_compile_files(baseline_path: Path, candidate_path: Path) -> dict[str, Any]:
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    baseline_facts = _facts_from_compile(baseline)
    candidate_facts = _facts_from_compile(candidate)
    baseline_source, baseline_direct = _split_source_direct(baseline_facts)
    candidate_source, candidate_direct = _split_source_direct(candidate_facts)
    source_facts = candidate_source or baseline_source
    merged_direct = _dedupe([*baseline_direct, *candidate_direct])
    merged_facts = [*source_facts, *merged_direct]

    merged = deepcopy(candidate)
    source_compile = merged.setdefault("source_compile", {})
    source_compile["facts"] = merged_facts
    merged.setdefault("merge_metadata", {})
    merged["merge_metadata"].update(
        {
            "schema_version": "compile_fact_merge_v1",
            "baseline_compile": str(baseline_path),
            "candidate_compile": str(candidate_path),
            "baseline_direct_fact_count": len(baseline_direct),
            "candidate_direct_fact_count": len(candidate_direct),
            "merged_direct_fact_count": len(merged_direct),
            "source_record_fact_count": len(source_facts),
            "added_direct_fact_count": len(merged_direct) - len(baseline_direct),
            "baseline_direct_predicate_count": len(_predicate_set(baseline_direct)),
            "candidate_direct_predicate_count": len(_predicate_set(candidate_direct)),
            "merged_direct_predicate_count": len(_predicate_set(merged_direct)),
        }
    )
    _merge_candidate_predicates(merged, baseline, candidate)
    return {"compile": merged, "metadata": merged["merge_metadata"]}


def _split_source_direct(facts: list[str]) -> tuple[list[str], list[str]]:
    source: list[str] = []
    direct: list[str] = []
    for fact in facts:
        if _predicate_name(fact).startswith("source_record"):
            source.append(fact)
        else:
            direct.append(fact)
    return source, direct


def _dedupe(facts: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for fact in facts:
        key = fact.strip()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(key)
    return out


def _predicate_set(facts: list[str]) -> set[str]:
    return {name for fact in facts if (name := _predicate_name(fact))}


def _merge_candidate_predicates(merged: dict[str, Any], baseline: dict[str, Any], candidate: dict[str, Any]) -> None:
    merged_parsed = merged.setdefault("parsed", {})
    rows: list[Any] = []
    for data in (baseline, candidate):
        parsed = data.get("parsed") if isinstance(data.get("parsed"), dict) else {}
        candidate_rows = parsed.get("candidate_predicates")
        if isinstance(candidate_rows, list):
            rows.extend(candidate_rows)
    seen: set[str] = set()
    merged_rows: list[Any] = []
    for row in rows:
        key = json.dumps(row, sort_keys=True) if isinstance(row, dict) else str(row)
        if key in seen:
            continue
        seen.add(key)
        merged_rows.append(row)
    if merged_rows:
        merged_parsed["candidate_predicates"] = merged_rows


def render_markdown(payload: dict[str, Any]) -> str:
    meta = payload["metadata"]
    return "\n".join(
        [
            "# Compile Fact Merge",
            "",
            f"- Schema: `{meta['schema_version']}`",
            f"- Baseline compile: `{meta['baseline_compile']}`",
            f"- Candidate compile: `{meta['candidate_compile']}`",
            f"- Source-record facts: `{meta['source_record_fact_count']}`",
            f"- Direct facts: `{meta['baseline_direct_fact_count']}` + candidate additions -> `{meta['merged_direct_fact_count']}`",
            f"- Direct predicates: `{meta['baseline_direct_predicate_count']}` baseline, `{meta['candidate_direct_predicate_count']}` candidate, `{meta['merged_direct_predicate_count']}` merged",
            f"- Added direct facts: `{meta['added_direct_fact_count']}`",
            "",
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
