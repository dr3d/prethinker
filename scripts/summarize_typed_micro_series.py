#!/usr/bin/env python3
"""Summarize typed micro-fixture support across repeated compile artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.validate_typed_micro_fixtures import (  # noqa: E402
    DEFAULT_ROOT,
    _facts_from_compile_json,
    _load_fact_lines,
    _match_expected_facts,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", required=True, help="Micro-fixture id under datasets/compile_micro_fixtures.")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--compile-json", action="append", default=[], type=Path, required=True)
    parser.add_argument("--support-threshold", type=int, default=2)
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    parser.add_argument("--exit-zero", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(
        fixture_id=str(args.fixture),
        root=args.root,
        compile_paths=[path.resolve() for path in args.compile_json],
        support_threshold=int(args.support_threshold),
    )
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(render_markdown(report), encoding="utf-8")
    if not args.out_json and not args.out_md:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if args.exit_zero or report["summary"]["compile_count"] else 1


def build_report(
    *,
    fixture_id: str,
    root: Path = DEFAULT_ROOT,
    compile_paths: list[Path],
    support_threshold: int = 2,
) -> dict[str, Any]:
    fixture_dir = root / fixture_id
    expected_path = fixture_dir / "expected_facts.pl"
    expected_facts = _load_fact_lines(expected_path)
    runs: list[dict[str, Any]] = []
    support: dict[str, list[str]] = {fact: [] for fact in expected_facts}
    for index, path in enumerate(compile_paths, start=1):
        run_id = path.parent.name or f"run_{index}"
        compile_facts = _facts_from_compile_json(path)
        match_report = _match_expected_facts(expected_facts, compile_facts)
        missing = set(match_report["missing_expected_facts"])
        matched = [fact for fact in expected_facts if fact not in missing]
        for fact in matched:
            support.setdefault(fact, []).append(run_id)
        runs.append(
            {
                "run_id": run_id,
                "compile_json": str(path),
                "matched_fact_count": len(matched),
                "expected_fact_count": len(expected_facts),
                "missing_fact_count": len(missing),
            }
        )
    rows = [
        {
            "expected_fact": fact,
            "support_count": len(run_ids),
            "support_runs": run_ids,
            "meets_threshold": len(run_ids) >= support_threshold,
        }
        for fact, run_ids in support.items()
    ]
    rows.sort(key=lambda item: (not bool(item["meets_threshold"]), -int(item["support_count"]), item["expected_fact"]))
    supported = [row for row in rows if row["meets_threshold"]]
    return {
        "schema_version": "typed_micro_series_summary_v1",
        "fixture_id": fixture_id,
        "expected_facts": str(expected_path),
        "support_threshold": support_threshold,
        "summary": {
            "compile_count": len(compile_paths),
            "expected_fact_count": len(expected_facts),
            "supported_fact_count": len(supported),
            "unsupported_fact_count": len(rows) - len(supported),
        },
        "runs": runs,
        "rows": rows,
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Typed Micro-Series Summary",
        "",
        f"- Fixture: `{report['fixture_id']}`",
        f"- Compiles: `{summary['compile_count']}`",
        f"- Expected facts: `{summary['expected_fact_count']}`",
        f"- Support threshold: `{report['support_threshold']}`",
        f"- Supported facts: `{summary['supported_fact_count']}`",
        f"- Unsupported facts: `{summary['unsupported_fact_count']}`",
        "",
        "| Support | Meets | Expected fact |",
        "| ---: | --- | --- |",
    ]
    for row in report.get("rows", []):
        meets = "yes" if row.get("meets_threshold") else "no"
        lines.append(
            "| {} | {} | `{}` |".format(
                row.get("support_count", 0),
                meets,
                str(row.get("expected_fact", "")).replace("|", "/"),
            )
        )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
