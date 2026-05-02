#!/usr/bin/env python3
"""Union mapper-admitted domain bootstrap compile surfaces.

This utility combines already-admitted facts/rules from one or more
domain-bootstrap source compile JSON artifacts. It deliberately does not read
the original source prose and does not infer new clauses. It only deduplicates
safe mapper outputs and optionally validates that the merged clauses load in
the local Prolog runtime.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = REPO_ROOT / "tmp" / "domain_bootstrap_file"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from kb_pipeline import CorePrologRuntime  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-json", action="append", type=Path, required=True, help="Compile run JSON to merge.")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--label", default="union", help="Short label used in the output filename.")
    parser.add_argument("--domain-hint", default="", help="Optional domain hint override.")
    parser.add_argument(
        "--no-runtime-validation",
        action="store_true",
        help="Do not validate merged clauses in the local Prolog runtime before writing.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_paths = [path if path.is_absolute() else (REPO_ROOT / path).resolve() for path in args.run_json]
    records = [json.loads(path.read_text(encoding="utf-8-sig")) for path in run_paths]
    if not records:
        raise SystemExit("no records supplied")

    facts = _ordered_unique(_source_compile_items(records, "facts"))
    rules = _ordered_unique(_source_compile_items(records, "rules"))
    queries = _ordered_unique(_source_compile_items(records, "queries"))
    load_errors: list[str] = []
    if not bool(args.no_runtime_validation):
        facts, rules, load_errors = _runtime_validated(facts=facts, rules=rules)

    first = dict(records[0])
    first_compile = first.get("source_compile") if isinstance(first.get("source_compile"), dict) else {}
    domain_hint = str(args.domain_hint or first.get("domain_hint") or "")
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    source_counts = [
        {
            "run_json": str(path),
            "facts": len(_compile_items(record, "facts")),
            "rules": len(_compile_items(record, "rules")),
            "queries": len(_compile_items(record, "queries")),
        }
        for path, record in zip(run_paths, records)
    ]

    first.update(
        {
            "ts": now,
            "mode": "deterministic_compile_union",
            "domain_hint": domain_hint,
            "source_compile": {
                "ok": not bool(load_errors),
                "mode": "deterministic_compile_union",
                "facts": facts,
                "rules": rules,
                "queries": queries,
                "admitted_count": len(facts) + len(rules),
                "skipped_count": 0,
                "unique_fact_count": len(facts),
                "unique_rule_count": len(rules),
                "unique_query_count": len(queries),
                "source_admitted_counts": source_counts,
                "runtime_load_errors": load_errors,
            },
            "union_source_compile": {
                "schema_version": "domain_bootstrap_compile_union_v1",
                "created_at": now,
                "source_runs": [str(path) for path in run_paths],
                "source_counts": source_counts,
                "runtime_validated": not bool(args.no_runtime_validation),
                "runtime_load_errors": load_errors,
                "policy": [
                    "No source prose was read.",
                    "No new facts or rules were inferred.",
                    "Only mapper-admitted compile outputs were deduplicated.",
                ],
            },
        }
    )
    if isinstance(first_compile, dict):
        first["union_source_compile"]["first_compile_mode"] = first_compile.get("mode", "")

    out_dir = args.out_dir if args.out_dir.is_absolute() else (REPO_ROOT / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = _slug(str(args.label or "union"))
    model_slug = _slug(str(first.get("model") or "model"))
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    out_path = out_dir / f"domain_bootstrap_file_{stamp}_{slug}_{model_slug}.json"
    out_path.write_text(json.dumps(first, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(str(out_path))
    print(
        json.dumps(
            {
                "facts": len(facts),
                "rules": len(rules),
                "queries": len(queries),
                "runtime_load_errors": len(load_errors),
                "source_runs": len(run_paths),
            },
            sort_keys=True,
        )
    )
    return 0


def _compile_items(record: dict[str, Any], key: str) -> list[str]:
    source_compile = record.get("source_compile") if isinstance(record.get("source_compile"), dict) else {}
    return [str(item).strip() for item in source_compile.get(key, []) if str(item).strip()]


def _source_compile_items(records: list[dict[str, Any]], key: str) -> list[str]:
    out: list[str] = []
    for record in records:
        out.extend(_compile_items(record, key))
    return out


def _ordered_unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out


def _runtime_validated(*, facts: list[str], rules: list[str]) -> tuple[list[str], list[str], list[str]]:
    runtime = CorePrologRuntime(max_depth=500)
    good_facts: list[str] = []
    good_rules: list[str] = []
    errors: list[str] = []
    for fact in facts:
        result = runtime.assert_fact(fact)
        if str(result.get("status", "")) == "success":
            good_facts.append(fact)
        else:
            errors.append(f"fact {fact}: {result.get('message', result)}")
    for rule in rules:
        result = runtime.assert_rule(rule)
        if str(result.get("status", "")) == "success":
            good_rules.append(rule)
        else:
            errors.append(f"rule {rule}: {result.get('message', result)}")
    return good_facts, good_rules, errors


def _slug(value: str) -> str:
    out = "".join(ch.lower() if ch.isalnum() else "-" for ch in str(value or "").strip())
    out = "-".join(part for part in out.split("-") if part)
    return out[:80] or "union"


if __name__ == "__main__":
    raise SystemExit(main())
