#!/usr/bin/env python3
"""Score story-world QA support coverage against a compiled KB.

This is intentionally post-ingestion. The support map is an evaluation artifact:
it is never fed into profile discovery or source compilation.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = REPO_ROOT / "tmp" / "story_world_support"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from kb_pipeline import CorePrologRuntime  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Score QA support bundles against a compiled story-world KB.")
    parser.add_argument("--run-json", type=Path, required=True, help="domain_bootstrap_file_*.json with source_compile.")
    parser.add_argument("--support-map", type=Path, required=True, help="JSONL support map with required_support_any bundles.")
    parser.add_argument("--qa-json", type=Path, default=None, help="Optional domain_bootstrap_qa_*.json for root-cause labeling.")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_path = _resolve(args.run_json)
    support_path = _resolve(args.support_map)
    qa_path = _resolve(args.qa_json) if args.qa_json else None

    run_record = json.loads(run_path.read_text(encoding="utf-8-sig"))
    compile_record = run_record.get("source_compile") if isinstance(run_record.get("source_compile"), dict) else {}
    facts = [str(item).strip() for item in compile_record.get("facts", []) if str(item).strip()]
    rules = [str(item).strip() for item in compile_record.get("rules", []) if str(item).strip()]
    runtime, load_errors = _load_runtime(facts=facts, rules=rules)
    support_rows = _load_jsonl(support_path)
    qa_rows = _load_qa_rows(qa_path) if qa_path else {}

    rows = [
        _score_support_row(row, runtime=runtime, qa_row=qa_rows.get(str(row.get("id", "")).strip(), {}))
        for row in support_rows
    ]
    summary = _summary(rows, load_errors=load_errors)
    record = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "run_json": str(run_path),
        "support_map": str(support_path),
        "qa_json": str(qa_path) if qa_path else "",
        "source_fact_count": len(facts),
        "source_rule_count": len(rules),
        "runtime_load_errors": load_errors,
        "summary": summary,
        "rows": rows,
    }

    out_dir = _resolve(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}_{run_path.stem}_support"
    json_path = out_dir / f"{slug}.json"
    md_path = json_path.with_suffix(".md")
    json_path.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    _write_markdown(record, md_path)
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else (REPO_ROOT / path).resolve()


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        row = json.loads(line)
        if isinstance(row, dict):
            rows.append(row)
    return rows


def _load_qa_rows(path: Path | None) -> dict[str, dict[str, Any]]:
    if path is None:
        return {}
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    rows = data.get("rows", []) if isinstance(data, dict) else []
    out: dict[str, dict[str, Any]] = {}
    for row in rows if isinstance(rows, list) else []:
        if isinstance(row, dict) and str(row.get("id", "")).strip():
            out[str(row["id"]).strip()] = row
    return out


def _load_runtime(*, facts: list[str], rules: list[str]) -> tuple[CorePrologRuntime, list[str]]:
    runtime = CorePrologRuntime(max_depth=500)
    errors: list[str] = []
    for fact in facts:
        result = runtime.assert_fact(fact)
        if str(result.get("status", "")) != "success":
            errors.append(f"fact {fact}: {result.get('message', result)}")
    for rule in rules:
        result = runtime.assert_rule(rule)
        if str(result.get("status", "")) != "success":
            errors.append(f"rule {rule}: {result.get('message', result)}")
    return runtime, errors


def _score_support_row(row: dict[str, Any], *, runtime: CorePrologRuntime, qa_row: dict[str, Any]) -> dict[str, Any]:
    bundles = row.get("required_support_any", [])
    scored_bundles: list[dict[str, Any]] = []
    support_present = False
    first_satisfied = ""
    for bundle in bundles if isinstance(bundles, list) else []:
        if not isinstance(bundle, dict):
            continue
        queries = [str(item).strip() for item in bundle.get("queries", []) if str(item).strip()]
        query_rows = []
        bundle_ok = bool(queries)
        for query in queries:
            result = runtime.query_rows(query)
            ok = str(result.get("status", "")) == "success" and int(result.get("num_rows", 0) or 0) > 0
            if not ok:
                bundle_ok = False
            query_rows.append(
                {
                    "query": query,
                    "ok": ok,
                    "status": result.get("status", ""),
                    "num_rows": result.get("num_rows", 0),
                    "rows": result.get("rows", [])[:5] if isinstance(result.get("rows"), list) else [],
                }
            )
        if bundle_ok and not support_present:
            support_present = True
            first_satisfied = str(bundle.get("label", "")).strip()
        scored_bundles.append(
            {
                "label": str(bundle.get("label", "")).strip(),
                "ok": bundle_ok,
                "queries": query_rows,
            }
        )

    verdict = ""
    if isinstance(qa_row, dict):
        judge = qa_row.get("reference_judge") if isinstance(qa_row.get("reference_judge"), dict) else {}
        verdict = str(judge.get("verdict", "")).strip()
    qa_query_had_rows = _qa_query_had_rows(qa_row)
    root_cause = _root_cause(
        support_present=support_present,
        qa_verdict=verdict,
        qa_query_had_rows=qa_query_had_rows,
    )
    return {
        "id": str(row.get("id", "")).strip(),
        "phase": str(row.get("phase", "")).strip(),
        "question": str(row.get("question", "")).strip(),
        "support_present": support_present,
        "satisfied_bundle": first_satisfied,
        "qa_verdict": verdict,
        "qa_query_had_rows": qa_query_had_rows,
        "root_cause": root_cause,
        "failure_classes": row.get("failure_classes", []),
        "bundles": scored_bundles,
    }


def _qa_query_had_rows(qa_row: dict[str, Any]) -> bool:
    if not isinstance(qa_row, dict):
        return False
    for item in qa_row.get("query_results", []) if isinstance(qa_row.get("query_results"), list) else []:
        result = item.get("result") if isinstance(item, dict) else {}
        if isinstance(result, dict) and str(result.get("status", "")) == "success" and int(result.get("num_rows", 0) or 0) > 0:
            return True
    return False


def _root_cause(*, support_present: bool, qa_verdict: str, qa_query_had_rows: bool) -> str:
    verdict = str(qa_verdict or "").strip().lower()
    if not support_present:
        return "compile_missing_required_support"
    if verdict in {"exact", "not_judged", ""}:
        return "support_available"
    if not qa_query_had_rows:
        return "query_planner_missed_available_support"
    return "answer_synthesis_or_query_specificity_gap"


def _summary(rows: list[dict[str, Any]], *, load_errors: list[str]) -> dict[str, Any]:
    total = len(rows)
    support = sum(1 for row in rows if row.get("support_present"))
    exact_with_support = sum(1 for row in rows if row.get("support_present") and row.get("qa_verdict") == "exact")
    causes: dict[str, int] = {}
    for row in rows:
        cause = str(row.get("root_cause", "")).strip() or "unknown"
        causes[cause] = causes.get(cause, 0) + 1
    return {
        "questions": total,
        "support_present": support,
        "support_missing": total - support,
        "support_rate": round(support / max(1, total), 3),
        "exact_with_support": exact_with_support,
        "runtime_load_error_count": len(load_errors),
        "root_causes": dict(sorted(causes.items())),
    }


def _write_markdown(record: dict[str, Any], path: Path) -> None:
    summary = record.get("summary", {}) if isinstance(record.get("summary"), dict) else {}
    lines = [
        "# Story-World QA Support Score",
        "",
        f"- Run: `{record.get('run_json', '')}`",
        f"- Support map: `{record.get('support_map', '')}`",
        f"- QA run: `{record.get('qa_json', '')}`",
        f"- Support: `{summary.get('support_present', 0)}/{summary.get('questions', 0)}` (`{summary.get('support_rate', 0)}`)",
        f"- Runtime load errors: `{summary.get('runtime_load_error_count', 0)}`",
        "",
        "## Root Causes",
        "",
    ]
    causes = summary.get("root_causes", {}) if isinstance(summary.get("root_causes"), dict) else {}
    lines.extend([f"- `{key}`: {value}" for key, value in causes.items()] or ["- none"])
    lines.extend(["", "## Rows", ""])
    lines.append("| id | support | qa | root cause | satisfied bundle | question |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for row in record.get("rows", []) if isinstance(record.get("rows"), list) else []:
        lines.append(
            "| {id} | {support} | {qa} | {cause} | {bundle} | {question} |".format(
                id=row.get("id", ""),
                support="yes" if row.get("support_present") else "no",
                qa=row.get("qa_verdict", ""),
                cause=row.get("root_cause", ""),
                bundle=row.get("satisfied_bundle", ""),
                question=str(row.get("question", "")).replace("|", "\\|"),
            )
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
