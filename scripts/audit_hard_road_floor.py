#!/usr/bin/env python3
"""Compute a conservative sign-clean floor from existing QA artifacts.

The hard-road metric is intentionally narrow:

    product exact
    AND typed-plan replay succeeds over non-source-record compile atoms
    AND redaction replay survives with the deterministic proxy
    AND returned evidence values do not match atom-shape blockers

This is not a product score. It is a quick "are we still on any road?" floor
that avoids new LLM calls and refuses rows that may be carried by prose-shaped
typed atoms.
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

from scripts.audit_kb_atom_inventory import build_report as build_atom_inventory_report  # noqa: E402
from scripts.audit_redaction_replay import _iter_qa_files, build_report as build_redaction_report  # noqa: E402
from scripts.audit_typed_plan_replay import build_report as build_typed_plan_report  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path, help="QA JSON files or directories containing QA JSON files.")
    parser.add_argument(
        "--compile-root",
        type=Path,
        required=True,
        help="Compile artifact root with one directory per fixture.",
    )
    parser.add_argument(
        "--redaction-report",
        type=Path,
        default=None,
        help="Optional redaction_replay_audit_v1 JSON to use instead of deterministic proxy.",
    )
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    parser.add_argument("--max-shape-examples", type=int, default=100000)
    parser.add_argument(
        "--exit-zero",
        action="store_true",
        help="Report without failing when hard-clean exact rows are zero.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    qa_files = sorted({file.resolve() for path in args.paths for file in _iter_qa_files(path)})
    report = build_report(
        qa_files=qa_files,
        compile_root=args.compile_root,
        redaction_report_path=args.redaction_report,
        max_shape_examples=max(1, int(args.max_shape_examples)),
    )
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(render_markdown(report), encoding="utf-8")
    if not args.out_json and not args.out_md:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if args.exit_zero or report["summary"]["hard_clean_exact"] > 0 else 1


def build_report(
    *,
    qa_files: list[Path],
    compile_root: Path,
    redaction_report_path: Path | None = None,
    max_shape_examples: int = 100000,
) -> dict[str, Any]:
    typed_report = build_typed_plan_report(qa_files=qa_files, compile_root=compile_root, compile_json=None)
    redaction_report = (
        json.loads(redaction_report_path.read_text(encoding="utf-8"))
        if redaction_report_path
        else build_redaction_report(qa_files=qa_files, config=None)
    )
    atom_report = build_atom_inventory_report(
        compile_root=compile_root,
        fixtures=None,
        include_source_record=False,
        include_prose_like=False,
        max_examples=max_shape_examples,
    )

    typed_by_key = {_row_key(row): row for row in typed_report.get("rows", [])}
    redaction_by_key = {_row_key(row): row for row in redaction_report.get("rows", [])}
    shape_values_by_fixture, shape_predicates_by_fixture = _shape_blockers_by_fixture(atom_report)

    rows: list[dict[str, Any]] = []
    counts: Counter[str] = Counter()
    by_fixture: dict[str, Counter[str]] = defaultdict(Counter)
    for qa_file in qa_files:
        data = json.loads(qa_file.read_text(encoding="utf-8"))
        fixture = _qa_fixture_name(qa_file=qa_file, data=data)
        for row in data.get("rows", []) or []:
            if not isinstance(row, dict):
                continue
            row_id = str(row.get("id", "")).strip()
            verdict = str((row.get("reference_judge") or {}).get("verdict", "")).strip() or "unjudged"
            key = (fixture, row_id)
            typed_row = typed_by_key.get(key, {})
            redaction_row = redaction_by_key.get(key, {})
            typed_status = str(typed_row.get("status", "")).strip()
            redaction_status = str(redaction_row.get("thesis_verdict", "")).strip()
            shape_hits = _row_shape_hits(
                row,
                shape_values=shape_values_by_fixture.get(fixture, set()),
                shape_predicates=shape_predicates_by_fixture.get(fixture, set()),
            )
            product_exact = verdict == "exact"
            typed_full = typed_status == "all_queries_success"
            redaction_survived = redaction_status == "survived"
            atom_shape_clean = not shape_hits
            hard_clean = product_exact and typed_full and redaction_survived and atom_shape_clean

            counts["row_count"] += 1
            counts[f"verdict_{verdict}"] += 1
            if product_exact:
                counts["product_exact"] += 1
            if product_exact and typed_full:
                counts["typed_plan_exact"] += 1
            if product_exact and redaction_survived:
                counts["redaction_survived_exact"] += 1
            if product_exact and atom_shape_clean:
                counts["atom_shape_clean_product_exact"] += 1
            if hard_clean:
                counts["hard_clean_exact"] += 1

            by_fixture[fixture]["row_count"] += 1
            by_fixture[fixture][f"verdict_{verdict}"] += 1
            if product_exact:
                by_fixture[fixture]["product_exact"] += 1
            if product_exact and typed_full:
                by_fixture[fixture]["typed_plan_exact"] += 1
            if product_exact and redaction_survived:
                by_fixture[fixture]["redaction_survived_exact"] += 1
            if product_exact and atom_shape_clean:
                by_fixture[fixture]["atom_shape_clean_product_exact"] += 1
            if hard_clean:
                by_fixture[fixture]["hard_clean_exact"] += 1

            rows.append(
                {
                    "fixture": fixture,
                    "id": row_id,
                    "product_verdict": verdict,
                    "typed_plan_status": typed_status or "not_product_exact",
                    "redaction_thesis_verdict": redaction_status or "not_product_exact",
                    "atom_shape_clean": atom_shape_clean,
                    "atom_shape_hits": shape_hits[:10],
                    "hard_clean": hard_clean,
                    "reference_answer": row.get("reference_answer", ""),
                }
            )

    summary = {
        "row_count": counts["row_count"],
        "product_exact": counts["product_exact"],
        "product_exact_rate": _share(counts["product_exact"], counts["row_count"]),
        "typed_plan_exact": counts["typed_plan_exact"],
        "typed_plan_exact_rate": _share(counts["typed_plan_exact"], counts["row_count"]),
        "redaction_survived_exact": counts["redaction_survived_exact"],
        "redaction_survived_exact_rate": _share(counts["redaction_survived_exact"], counts["row_count"]),
        "atom_shape_clean_product_exact": counts["atom_shape_clean_product_exact"],
        "atom_shape_clean_product_exact_rate": _share(
            counts["atom_shape_clean_product_exact"],
            counts["row_count"],
        ),
        "hard_clean_exact": counts["hard_clean_exact"],
        "hard_clean_exact_rate": _share(counts["hard_clean_exact"], counts["row_count"]),
        "verdict_counts": {
            key.removeprefix("verdict_"): value
            for key, value in sorted(counts.items())
            if key.startswith("verdict_")
        },
        "atom_shape_blockers": atom_report.get("atom_shape", {}).get("blocker_count", 0),
        "atom_shape_issue_type_counts": atom_report.get("atom_shape", {}).get("issue_type_counts", {}),
    }
    return {
        "schema_version": "hard_road_floor_audit_v1",
        "qa_file_count": len(qa_files),
        "compile_root": str(compile_root),
        "redaction_report": str(redaction_report_path) if redaction_report_path else "deterministic_proxy",
        "summary": summary,
        "by_fixture": {
            fixture: _fixture_summary(counter)
            for fixture, counter in sorted(by_fixture.items())
        },
        "rows": rows,
        "component_summaries": {
            "typed_plan_replay": typed_report.get("summary", {}),
            "redaction_replay": redaction_report.get("summary", {}),
            "atom_shape": atom_report.get("atom_shape", {}),
        },
    }


def _fixture_summary(counter: Counter[str]) -> dict[str, Any]:
    row_count = counter["row_count"]
    return {
        "row_count": row_count,
        "product_exact": counter["product_exact"],
        "product_exact_rate": _share(counter["product_exact"], row_count),
        "typed_plan_exact": counter["typed_plan_exact"],
        "typed_plan_exact_rate": _share(counter["typed_plan_exact"], row_count),
        "redaction_survived_exact": counter["redaction_survived_exact"],
        "redaction_survived_exact_rate": _share(counter["redaction_survived_exact"], row_count),
        "atom_shape_clean_product_exact": counter["atom_shape_clean_product_exact"],
        "atom_shape_clean_product_exact_rate": _share(counter["atom_shape_clean_product_exact"], row_count),
        "hard_clean_exact": counter["hard_clean_exact"],
        "hard_clean_exact_rate": _share(counter["hard_clean_exact"], row_count),
        "verdict_counts": {
            key.removeprefix("verdict_"): value
            for key, value in sorted(counter.items())
            if key.startswith("verdict_")
        },
    }


def _row_key(row: dict[str, Any]) -> tuple[str, str]:
    return (str(row.get("fixture", "")).strip(), str(row.get("id", "")).strip())


def _qa_fixture_name(*, qa_file: Path, data: dict[str, Any]) -> str:
    run_json = str(data.get("run_json") or "").strip()
    if run_json:
        parent = Path(run_json).parent.name
        if parent:
            return parent
    return qa_file.parent.name


def _shape_blockers_by_fixture(atom_report: dict[str, Any]) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    values: dict[str, set[str]] = defaultdict(set)
    predicates: dict[str, set[str]] = defaultdict(set)
    for issue in atom_report.get("atom_shape", {}).get("examples", []) or []:
        if not isinstance(issue, dict) or issue.get("severity") != "blocker":
            continue
        fixture = str(issue.get("fixture", "")).strip()
        if not fixture:
            continue
        value = str(issue.get("value", "")).strip()
        if value:
            values[fixture].add(value)
        signature = str(issue.get("signature", "")).strip()
        predicate = signature.split("/", 1)[0].strip()
        if predicate and str(issue.get("field", "")) == "predicate":
            predicates[fixture].add(predicate)
    return values, predicates


def _row_shape_hits(
    row: dict[str, Any],
    *,
    shape_values: set[str],
    shape_predicates: set[str],
) -> list[dict[str, str]]:
    if not shape_values and not shape_predicates:
        return []
    hits: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for query_result in row.get("query_results", []) or []:
        result = query_result.get("result") if isinstance(query_result, dict) else None
        if not isinstance(result, dict):
            continue
        predicate = str(result.get("predicate", "")).strip()
        if predicate in shape_predicates:
            key = (predicate, "predicate", predicate)
            if key not in seen:
                seen.add(key)
                hits.append({"predicate": predicate, "field": "predicate", "value": predicate})
        for result_row in result.get("rows") or []:
            if not isinstance(result_row, dict):
                continue
            for field, value in result_row.items():
                text = str(value).strip()
                if text and text in shape_values:
                    key = (predicate, str(field), text)
                    if key in seen:
                        continue
                    seen.add(key)
                    hits.append({"predicate": predicate, "field": str(field), "value": text})
    return hits


def _share(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 6) if denominator else 0.0


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Hard-Road Floor Audit",
        "",
        f"- Schema: `{report['schema_version']}`",
        f"- QA files: `{report['qa_file_count']}`",
        f"- Compile root: `{report['compile_root']}`",
        f"- Redaction report: `{report['redaction_report']}`",
        "",
        "## Summary",
        "",
        f"- Rows: `{summary['row_count']}`",
        f"- Product exact: `{summary['product_exact']}` / `{summary['row_count']}` = `{summary['product_exact_rate']:.2%}`",
        f"- Typed-plan exact: `{summary['typed_plan_exact']}` / `{summary['row_count']}` = `{summary['typed_plan_exact_rate']:.2%}`",
        f"- Redaction-survived exact: `{summary['redaction_survived_exact']}` / `{summary['row_count']}` = `{summary['redaction_survived_exact_rate']:.2%}`",
        f"- Atom-shape-clean product exact: `{summary['atom_shape_clean_product_exact']}` / `{summary['row_count']}` = `{summary['atom_shape_clean_product_exact_rate']:.2%}`",
        f"- Hard-clean exact: `{summary['hard_clean_exact']}` / `{summary['row_count']}` = `{summary['hard_clean_exact_rate']:.2%}`",
        f"- Atom-shape blockers in compile artifacts: `{summary['atom_shape_blockers']}`",
        "",
        "## By Fixture",
        "",
        "| Fixture | Product | Typed | Redacted | Atom-clean | Hard-clean |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for fixture, item in report["by_fixture"].items():
        row_count = item["row_count"]
        lines.append(
            "| `{}` | {}/{} | {}/{} | {}/{} | {}/{} | {}/{} |".format(
                fixture,
                item["product_exact"],
                row_count,
                item["typed_plan_exact"],
                row_count,
                item["redaction_survived_exact"],
                row_count,
                item["atom_shape_clean_product_exact"],
                row_count,
                item["hard_clean_exact"],
                row_count,
            )
        )
    lines.extend(
        [
            "",
            "## Product-Exact Rows Failing Hard-Clean",
            "",
            "| Fixture | Row | Typed | Redaction | Atom hits |",
            "| --- | --- | --- | --- | ---: |",
        ]
    )
    for row in report["rows"]:
        if row["product_verdict"] != "exact" or row["hard_clean"]:
            continue
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | {} |".format(
                row["fixture"],
                row["id"],
                row["typed_plan_status"],
                row["redaction_thesis_verdict"],
                len(row.get("atom_shape_hits", [])),
            )
        )
    lines.extend(
        [
            "",
            "## Note",
            "",
            (
                "This is a conservative floor computed from existing artifacts. It treats prose-shaped "
                "typed atoms as blockers. Redaction status comes from the report named above; when that "
                "field is `deterministic_proxy`, no model calls were used."
            ),
        ]
    )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
