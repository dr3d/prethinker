#!/usr/bin/env python3
"""Add failure-surface labels to an existing domain-bootstrap QA artifact.

This is a post-run diagnostic. It does not rerun source compilation, does not
rerun QA query planning, and does not read the original source prose. It only
classifies non-exact QA rows using the compiled KB surface, emitted queries,
query results, and benchmark reference answers already present in the artifact.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = REPO_ROOT / "tmp" / "domain_bootstrap_qa"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.run_domain_bootstrap_qa import (  # noqa: E402
    SemanticIRCallConfig,
    classify_failure_surface,
    compiled_kb_inventory,
    summarize,
    write_summary,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qa-json", type=Path, required=True)
    parser.add_argument("--run-json", type=Path, default=None, help="Optional compile run JSON override.")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--backend", choices=["lmstudio"], default="lmstudio")
    parser.add_argument("--model", default="qwen/qwen3.6-35b-a3b")
    parser.add_argument("--base-url", default="http://127.0.0.1:1234")
    parser.add_argument("--timeout", type=int, default=420)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--top-p", type=float, default=0.82)
    parser.add_argument("--top-k", type=int, default=20)
    parser.add_argument("--num-ctx", type=int, default=32768)
    parser.add_argument("--max-tokens", type=int, default=6000)
    parser.add_argument("--force", action="store_true", help="Reclassify rows that already have failure_surface.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    qa_path = args.qa_json if args.qa_json.is_absolute() else (REPO_ROOT / args.qa_json).resolve()
    record = json.loads(qa_path.read_text(encoding="utf-8-sig"))
    run_path = args.run_json
    if run_path is None:
        run_value = str(record.get("run_json", "")).strip()
        if not run_value:
            raise SystemExit("QA artifact has no run_json; pass --run-json")
        run_path = Path(run_value)
    run_path = run_path if run_path.is_absolute() else (REPO_ROOT / run_path).resolve()
    run_record = json.loads(run_path.read_text(encoding="utf-8-sig"))
    compile_record = run_record.get("source_compile") if isinstance(run_record.get("source_compile"), dict) else {}
    facts = [str(item).strip() for item in compile_record.get("facts", []) if str(item).strip()]
    rules = [str(item).strip() for item in compile_record.get("rules", []) if str(item).strip()]
    kb_inventory = compiled_kb_inventory(facts=facts, rules=rules)
    config = SemanticIRCallConfig(
        backend=str(args.backend),
        base_url=str(args.base_url),
        model=str(args.model),
        context_length=int(args.num_ctx),
        timeout=int(args.timeout),
        temperature=float(args.temperature),
        top_p=float(args.top_p),
        top_k=int(args.top_k),
        max_tokens=int(args.max_tokens),
        think_enabled=False,
        reasoning_effort="none",
    )

    classified = 0
    skipped = 0
    rows = record.get("rows", [])
    for row in rows if isinstance(rows, list) else []:
        if not isinstance(row, dict):
            continue
        judge = row.get("reference_judge") if isinstance(row.get("reference_judge"), dict) else {}
        if str(judge.get("verdict", "")).strip() == "exact":
            skipped += 1
            continue
        if isinstance(row.get("failure_surface"), dict) and not bool(args.force):
            skipped += 1
            continue
        row["failure_surface"] = classify_failure_surface(
            row=row,
            kb_inventory=kb_inventory,
            facts=facts,
            rules=rules,
            config=config,
        )
        classified += 1

    summary = summarize(
        rows=[row for row in rows if isinstance(row, dict)] if isinstance(rows, list) else [],
        load_errors=record.get("runtime_load_errors", []) if isinstance(record.get("runtime_load_errors"), list) else [],
        elapsed_ms=int((record.get("summary") or {}).get("elapsed_ms", 0) or 0),
    )
    prior_summary = record.get("summary") if isinstance(record.get("summary"), dict) else {}
    summary.update(
        {
            "cache_enabled": prior_summary.get("cache_enabled", False),
            "cache_hits": prior_summary.get("cache_hits", 0),
            "cache_misses": prior_summary.get("cache_misses", 0),
            "failure_surface_classified": classified,
            "failure_surface_skipped": skipped,
        }
    )
    record["summary"] = summary
    record["failure_surface_classification"] = {
        "schema_version": "qa_failure_surface_classification_run_v1",
        "classified_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "qa_json": str(qa_path),
        "run_json": str(run_path),
        "classified_rows": classified,
        "skipped_rows": skipped,
        "policy": [
            "No source prose was read.",
            "No QA query planning was rerun.",
            "Only non-exact judged rows were classified unless --force was supplied.",
        ],
    }

    out_dir = args.out_dir if args.out_dir.is_absolute() else (REPO_ROOT / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    out_path = out_dir / f"{qa_path.stem}_failure_surface_{stamp}.json"
    md_path = out_path.with_suffix(".md")
    out_path.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    write_summary(record, md_path)
    print(f"Wrote {out_path}")
    print(f"Wrote {md_path}")
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
