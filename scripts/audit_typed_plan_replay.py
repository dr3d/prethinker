#!/usr/bin/env python3
"""Replay QA query plans against typed compile atoms only.

This is a thesis-discipline diagnostic. It asks a narrower question than the
normal QA judge:

    If source-record/prose atoms are removed, do the row's planned Prolog
    queries still execute against the typed KB?

The script does not interpret the user's question and does not read source
prose. It loads compile artifacts, keeps only typed non-source-record facts, and
re-executes the query plans already recorded in QA rows.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.audit_kb_atom_inventory import _latest_compile_json, _typed_facts  # noqa: E402
from scripts.audit_redaction_replay import _iter_qa_files, _normalize, _reference_answer_parts  # noqa: E402
from scripts.run_domain_bootstrap_qa import (  # noqa: E402
    load_runtime,
    parse_prolog_query_goals,
    _typed_claim_finding_range_composition_results,
    _typed_legal_citation_inventory_composition_results,
    _typed_list_range_inventory_composition_results,
)
from src.carrier_contract_registry import carrier_contract  # noqa: E402


SOURCE_RECORD_PREFIX = "source_record_"
DETERMINISTIC_DERIVED_QUERY_SIGNATURES = {
    "typed_claim_finding_range_composition": "typed_claim_finding_range_composition/3",
    "typed_legal_citation_inventory_composition": "typed_legal_citation_inventory_composition/4",
    "typed_list_range_inventory_composition": "typed_list_range_inventory_composition/2",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path, help="QA JSON files or directories containing QA JSON files.")
    parser.add_argument(
        "--compile-root",
        type=Path,
        default=None,
        help="Optional root with per-fixture compile artifact directories.",
    )
    parser.add_argument(
        "--compile-json",
        type=Path,
        default=None,
        help="Optional compile JSON to use for every row.",
    )
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    parser.add_argument("--exit-zero", action="store_true", help="Report without failing. Do not use for gates.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    qa_files = sorted({file.resolve() for path in args.paths for file in _iter_qa_files(path)})
    report = build_report(
        qa_files=qa_files,
        compile_root=args.compile_root,
        compile_json=args.compile_json,
    )
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(render_markdown(report), encoding="utf-8")
    if not args.out_json and not args.out_md:
        print(json.dumps(report, indent=2, sort_keys=True))
    blocked = bool(report["summary"]["blocking_reasons"])
    return 0 if args.exit_zero or not blocked else 1


def build_report(
    *,
    qa_files: list[Path],
    compile_root: Path | None = None,
    compile_json: Path | None = None,
) -> dict[str, Any]:
    runtime_cache: dict[Path, dict[str, Any]] = {}
    rows: list[dict[str, Any]] = []
    verdict_counts: Counter[str] = Counter()
    replay_counts: Counter[str] = Counter()
    by_fixture: dict[str, Counter[str]] = defaultdict(Counter)
    runtime_load_errors: dict[str, list[str]] = {}

    for qa_file in qa_files:
        data = json.loads(qa_file.read_text(encoding="utf-8"))
        fixture_hint = _fixture_hint(data=data, qa_file=qa_file)
        default_compile_json = _resolve_compile_json(
            data=data,
            fixture=fixture_hint,
            compile_root=compile_root,
            compile_json=compile_json,
        )
        for row in data.get("rows", []) or []:
            if not isinstance(row, dict):
                continue
            fixture = str(row.get("fixture") or row.get("fixture_name") or fixture_hint).strip() or fixture_hint
            verdict = str((row.get("reference_judge") or {}).get("verdict", "")).strip() or "unjudged"
            verdict_counts[verdict] += 1
            if verdict != "exact":
                continue
            row_compile_json = _resolve_compile_json(
                data=data,
                fixture=fixture,
                compile_root=compile_root,
                compile_json=compile_json or default_compile_json,
            )
            replay = _replay_row(row=row, compile_json=row_compile_json, runtime_cache=runtime_cache)
            if replay["runtime_load_errors"]:
                runtime_load_errors[str(row_compile_json)] = list(replay["runtime_load_errors"])
            status = str(replay["status"])
            replay_counts[status] += 1
            by_fixture[fixture][status] += 1
            rows.append(
                {
                    "fixture": fixture,
                    "id": row.get("id", ""),
                    "reference_answer": row.get("reference_answer", ""),
                    "product_verdict": verdict,
                    "compile_json": str(row_compile_json) if row_compile_json else "",
                    **replay,
                }
            )

    total_rows = sum(verdict_counts.values())
    product_exact = verdict_counts.get("exact", 0)
    typed_plan_replayed = replay_counts.get("all_queries_success", 0)
    registered_plan_replayed = sum(
        1
        for row in rows
        if row.get("status") == "all_queries_success" and int(row.get("unregistered_query_signature_count", 0) or 0) == 0
    )
    unregistered_plan_rows = sum(
        1 for row in rows if int(row.get("unregistered_query_signature_count", 0) or 0) > 0
    )
    blocking_reasons = _blocking_reasons(
        qa_file_count=len(qa_files),
        product_exact=product_exact,
        registered_plan_replayed=registered_plan_replayed,
        blocked_source_record_plan_rows=replay_counts.get("blocked_source_record_query", 0),
        unregistered_plan_exact_rows=unregistered_plan_rows,
        runtime_load_errors=runtime_load_errors,
    )
    summary = {
        "row_count": total_rows,
        "product_exact": product_exact,
        "product_exact_rate": _share(product_exact, total_rows),
        "typed_plan_replayed_exact": typed_plan_replayed,
        "typed_plan_replayed_exact_rate": _share(typed_plan_replayed, total_rows),
        "registered_typed_plan_replayed_exact": registered_plan_replayed,
        "registered_typed_plan_replayed_exact_rate": _share(registered_plan_replayed, total_rows),
        "product_exact_registered_plan_replay_rate": _share(registered_plan_replayed, product_exact),
        "unregistered_plan_exact_rows": unregistered_plan_rows,
        "note": (
            "typed_plan_replayed_exact is a legacy-compatible field name for product-exact rows whose "
            "recorded query plans all replay over typed atoms; it is not an independent answer judge."
        ),
        "product_exact_plan_replay_rate": _share(typed_plan_replayed, product_exact),
        "blocked_source_record_plan_rows": replay_counts.get("blocked_source_record_query", 0),
        "verdict_counts": dict(sorted(verdict_counts.items())),
        "replay_status_counts": dict(sorted(replay_counts.items())),
        "runtime_load_errors": runtime_load_errors,
        "blocking_reasons": blocking_reasons,
        "status": "blocked" if blocking_reasons else "pass",
    }
    return {
        "schema_version": "typed_plan_replay_audit_v1",
        "qa_file_count": len(qa_files),
        "settings": {
            "compile_root": str(compile_root) if compile_root else "",
            "compile_json": str(compile_json) if compile_json else "",
        },
        "summary": summary,
        "by_fixture": {fixture: dict(counts) for fixture, counts in sorted(by_fixture.items())},
        "rows": rows,
    }


def _blocking_reasons(
    *,
    qa_file_count: int,
    product_exact: int,
    registered_plan_replayed: int,
    blocked_source_record_plan_rows: int,
    unregistered_plan_exact_rows: int,
    runtime_load_errors: dict[str, list[str]],
) -> list[str]:
    reasons: list[str] = []
    if qa_file_count <= 0:
        reasons.append("no_qa_files")
    if product_exact <= 0:
        reasons.append("no_product_exact_rows")
    if blocked_source_record_plan_rows > 0:
        reasons.append("blocked_source_record_plan_rows")
    if unregistered_plan_exact_rows > 0:
        reasons.append("unregistered_plan_exact_rows")
    if registered_plan_replayed < product_exact:
        reasons.append("product_exact_without_registered_typed_plan_replay")
    if runtime_load_errors:
        reasons.append("runtime_load_errors")
    return reasons


def _fixture_hint(*, data: dict[str, Any], qa_file: Path) -> str:
    rows = data.get("rows", []) or []
    for row in rows:
        if isinstance(row, dict):
            fixture = str(row.get("fixture") or row.get("fixture_name") or "").strip()
            if fixture:
                return fixture
    run_json = str(data.get("run_json") or "").strip()
    if run_json:
        parent = Path(run_json).parent
        if parent.name:
            return parent.name
    return qa_file.parent.name


def _resolve_compile_json(
    *,
    data: dict[str, Any],
    fixture: str,
    compile_root: Path | None,
    compile_json: Path | None,
) -> Path | None:
    if compile_json:
        return compile_json
    if compile_root:
        fixture_dir = compile_root / fixture
        if fixture_dir.exists():
            return _latest_compile_json(fixture_dir)
    run_json = str(data.get("run_json") or "").strip()
    if run_json:
        path = Path(run_json)
        if path.exists():
            return path
    return None


def _replay_row(
    *,
    row: dict[str, Any],
    compile_json: Path | None,
    runtime_cache: dict[Path, dict[str, Any]],
) -> dict[str, Any]:
    queries = [str(query).strip() for query in row.get("queries", []) or [] if str(query).strip()]
    if not queries:
        return _row_result(status="no_queries", queries=queries)
    signature_stats = _query_signature_stats(queries)
    blocked = [query for query in queries if _query_uses_source_record(query)]
    if blocked:
        return _row_result(
            status="blocked_source_record_query",
            queries=queries,
            blocked_queries=blocked,
            query_signature_stats=signature_stats,
        )
    if compile_json is None:
        return _row_result(status="missing_compile_json", queries=queries, query_signature_stats=signature_stats)
    cached = _runtime_for_compile(compile_json, runtime_cache=runtime_cache)
    if cached["errors"]:
        return _row_result(
            status="runtime_load_error",
            queries=queries,
            runtime_load_errors=cached["errors"],
            query_signature_stats=signature_stats,
        )

    replay_results: list[dict[str, Any]] = []
    executed_results: list[dict[str, Any]] = []
    success_count = 0
    typed_values: set[str] = set()
    for query in queries:
        derived = _replay_deterministic_derived_query(query=query, previous_results=executed_results)
        if derived is not None:
            result = derived
            status = str(result.get("status", "")).strip() or "unknown"
            rows = result.get("rows", [])
            row_count = len(rows) if isinstance(rows, list) else 0
            if status == "success":
                success_count += 1
            typed_values.update(_collect_replay_scalars(rows))
            executed_results.append({"query": query, "result": result})
            replay_results.append({"query": query, "status": status, "row_count": row_count, "derived": True})
            continue
        parsed = parse_prolog_query_goals(query)
        if parsed is None:
            replay_results.append({"query": query, "status": "parse_error", "row_count": 0})
            continue
        result = cached["runtime"].query_rows(query)
        status = str(result.get("status", "")).strip() or "unknown"
        rows = result.get("rows", [])
        row_count = len(rows) if isinstance(rows, list) else 0
        if status == "success":
            success_count += 1
        typed_values.update(_collect_replay_scalars(rows))
        executed_results.append({"query": query, "result": result})
        replay_results.append({"query": query, "status": status, "row_count": row_count})

    if success_count == len(queries):
        status = "all_queries_success"
    elif success_count > 0:
        status = "partial_query_success"
    else:
        status = "no_query_success"
    answer_coverage = _answer_coverage(
        reference=str(row.get("reference_answer", "")),
        typed_values=typed_values,
    )
    return _row_result(
        status=status,
        queries=queries,
        replay_results=replay_results,
        successful_query_count=success_count,
        typed_fact_count=cached["typed_fact_count"],
        answer_coverage=answer_coverage,
        query_signature_stats=signature_stats,
    )


def _query_signature_stats(queries: list[str]) -> dict[str, Any]:
    registered: list[str] = []
    unregistered: list[str] = []
    derived: list[str] = []
    unparsable: list[str] = []
    for query in queries:
        normalized = str(query or "").strip().rstrip(".")
        predicate = normalized.split("(", 1)[0].strip()
        if predicate in DETERMINISTIC_DERIVED_QUERY_SIGNATURES:
            derived.append(DETERMINISTIC_DERIVED_QUERY_SIGNATURES[predicate])
            continue
        parsed = parse_prolog_query_goals(query)
        if parsed is None:
            unparsable.append(query)
            continue
        for goal_predicate, goal_args in parsed:
            signature = f"{goal_predicate}/{len(goal_args)}"
            if carrier_contract(signature) is not None:
                registered.append(signature)
            else:
                unregistered.append(signature)
    return {
        "registered_query_signatures": sorted(set(registered)),
        "unregistered_query_signatures": sorted(set(unregistered)),
        "derived_query_signatures": sorted(set(derived)),
        "unparsable_queries": unparsable,
        "registered_query_signature_count": len(set(registered)),
        "unregistered_query_signature_count": len(set(unregistered)),
        "derived_query_signature_count": len(set(derived)),
    }


def _replay_deterministic_derived_query(
    *,
    query: str,
    previous_results: list[dict[str, Any]],
) -> dict[str, Any] | None:
    normalized = str(query or "").strip().rstrip(".")
    if normalized.startswith("typed_list_range_inventory_composition("):
        candidates = _typed_list_range_inventory_composition_results(previous_results)
    elif normalized.startswith("typed_claim_finding_range_composition("):
        candidates = _typed_claim_finding_range_composition_results(previous_results)
    elif normalized.startswith("typed_legal_citation_inventory_composition("):
        candidates = _typed_legal_citation_inventory_composition_results(previous_results)
    else:
        return None
    for item in candidates:
        result = item.get("result") if isinstance(item, dict) else None
        if isinstance(result, dict):
            return result
    return {
        "status": "no_results",
        "result_type": "derived_table",
        "predicate": normalized.split("(", 1)[0],
        "prolog_query": query,
        "rows": [],
        "num_rows": 0,
    }


def _runtime_for_compile(compile_json: Path, *, runtime_cache: dict[Path, dict[str, Any]]) -> dict[str, Any]:
    resolved = compile_json.resolve()
    if resolved in runtime_cache:
        return runtime_cache[resolved]
    facts, rejected, _shape_issues = _typed_facts(
        resolved,
        include_source_record=False,
        include_prose_like=False,
    )
    runtime, errors = load_runtime(facts=[fact.clause for fact in facts], rules=[])
    payload = {
        "runtime": runtime,
        "errors": errors,
        "typed_fact_count": len(facts),
        "rejected_counts": dict(sorted(rejected.items())),
    }
    runtime_cache[resolved] = payload
    return payload


def _query_uses_source_record(query: str) -> bool:
    goals = parse_prolog_query_goals(query)
    if goals is None:
        return False
    return any(predicate.startswith(SOURCE_RECORD_PREFIX) for predicate, _args in goals)


def _collect_replay_scalars(rows: Any) -> set[str]:
    out: set[str] = set()
    if not isinstance(rows, list):
        return out
    for row in rows:
        out.update(_collect_scalars(row))
    return out


def _collect_scalars(value: Any) -> set[str]:
    out: set[str] = set()
    if isinstance(value, dict):
        for inner in value.values():
            out.update(_collect_scalars(inner))
    elif isinstance(value, list):
        for inner in value:
            out.update(_collect_scalars(inner))
    elif isinstance(value, (str, int, float, bool)):
        normalized = _normalize(value)
        if normalized:
            out.add(normalized)
    return out


def _answer_coverage(*, reference: str, typed_values: set[str]) -> dict[str, Any]:
    normalized_reference = _normalize(reference)
    parts = _reference_answer_parts(reference)
    covered_parts = sorted(part for part in parts if part in typed_values)
    token_parts = _reference_tokens(reference)
    covered_tokens = sorted(token for token in token_parts if token in typed_values or any(token in value for value in typed_values))
    return {
        "full_reference_present": bool(normalized_reference and normalized_reference in typed_values),
        "structured_parts_total": len(parts),
        "structured_parts_covered": len(covered_parts),
        "structured_parts": sorted(parts),
        "covered_structured_parts": covered_parts,
        "token_total": len(token_parts),
        "token_covered": len(covered_tokens),
        "token_coverage": _share(len(covered_tokens), len(token_parts)),
    }


def _reference_tokens(reference: str) -> set[str]:
    tokens = {
        token.casefold()
        for token in re.findall(r"[A-Za-z0-9][A-Za-z0-9_./#:-]*", str(reference or ""))
        if len(token) >= 3
    }
    return {token for token in tokens if token not in {"and", "the", "with", "filed", "published"}}


def _row_result(
    *,
    status: str,
    queries: list[str],
    blocked_queries: list[str] | None = None,
    replay_results: list[dict[str, Any]] | None = None,
    successful_query_count: int = 0,
    typed_fact_count: int = 0,
    runtime_load_errors: list[str] | None = None,
    answer_coverage: dict[str, Any] | None = None,
    query_signature_stats: dict[str, Any] | None = None,
) -> dict[str, Any]:
    signature_stats = query_signature_stats or _query_signature_stats(queries)
    return {
        "status": status,
        "queries": queries,
        "query_count": len(queries),
        "successful_query_count": successful_query_count,
        "blocked_queries": blocked_queries or [],
        "replay_results": replay_results or [],
        "typed_fact_count": typed_fact_count,
        "runtime_load_errors": runtime_load_errors or [],
        "answer_coverage": answer_coverage or {},
        **signature_stats,
    }


def _share(count: int, total: int) -> float:
    return round(count / total, 6) if total else 0.0


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Typed Plan Replay Audit",
        "",
        f"- Schema: `{report['schema_version']}`",
        f"- QA files: `{report['qa_file_count']}`",
        f"- Rows: `{summary['row_count']}`",
        f"- Product exact: `{summary['product_exact']}` / `{summary['row_count']}` = `{summary['product_exact_rate']:.2%}`",
        f"- Product-exact rows with full typed-plan replay: `{summary['typed_plan_replayed_exact']}` / `{summary['row_count']}` = `{summary['typed_plan_replayed_exact_rate']:.2%}`",
        f"- Product-exact rows with registered-carrier typed replay: `{summary['registered_typed_plan_replayed_exact']}` / `{summary['row_count']}` = `{summary['registered_typed_plan_replayed_exact_rate']:.2%}`",
        f"- Product-exact registered replay survival: `{summary['product_exact_registered_plan_replay_rate']:.2%}`",
        f"- Product-exact rows using unregistered typed query signatures: `{summary['unregistered_plan_exact_rows']}`",
        f"- Product-exact replay survival: `{summary['product_exact_plan_replay_rate']:.2%}`",
        f"- Blocked source-record plan rows: `{summary['blocked_source_record_plan_rows']}`",
        f"- Replay statuses: `{summary['replay_status_counts']}`",
        f"- Status: `{summary['status']}`",
    ]
    if summary["blocking_reasons"]:
        lines.extend(["", "## Blocking Reasons", ""])
        for reason in summary["blocking_reasons"]:
            lines.append(f"- `{reason}`")
    lines.extend(
        [
            "",
            "## By Fixture",
            "",
            "| Fixture | All queries success | Partial | None | Blocked source-record | Missing compile |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for fixture, counts in report["by_fixture"].items():
        lines.append(
            "| `{}` | {} | {} | {} | {} | {} |".format(
                fixture,
                counts.get("all_queries_success", 0),
                counts.get("partial_query_success", 0),
                counts.get("no_query_success", 0),
                counts.get("blocked_source_record_query", 0),
                counts.get("missing_compile_json", 0),
            )
        )
    rows = report["rows"][:80]
    if rows:
        lines.extend(
            [
                "",
                "## Product-Exact Rows",
                "",
                "| Fixture | Row | Status | Successful queries | Unregistered signatures | Token coverage |",
                "| --- | --- | --- | ---: | --- | ---: |",
            ]
        )
        for row in rows:
            coverage = row.get("answer_coverage", {})
            lines.append(
                "| `{}` | `{}` | `{}` | {} / {} | {} | {:.2%} |".format(
                    row.get("fixture", ""),
                    row.get("id", ""),
                    row.get("status", ""),
                    row.get("successful_query_count", 0),
                    row.get("query_count", 0),
                    ", ".join(f"`{item}`" for item in row.get("unregistered_query_signatures", []) or []) or "-",
                    float(coverage.get("token_coverage", 0.0) or 0.0),
                )
            )
    lines.extend(
        [
            "",
            "## Note",
            "",
            "This is a plan-replay diagnostic. It proves that recorded query plans still execute over typed compile atoms after source-record/prose atoms are removed; it does not ask Python to interpret the user question.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
