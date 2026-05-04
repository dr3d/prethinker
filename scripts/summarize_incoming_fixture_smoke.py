#!/usr/bin/env python3
"""Summarize a staged incoming fixture compile + QA smoke run."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = REPO_ROOT / "tmp" / "incoming_smoke_summaries"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", required=True)
    parser.add_argument("--compile-json", type=Path, required=True)
    parser.add_argument("--qa-json", type=Path, action="append", default=[])
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    compile_path = _resolve(args.compile_json)
    qa_paths = [_resolve(path) for path in args.qa_json]
    report = build_report(
        fixture=str(args.fixture),
        compile_record=json.loads(compile_path.read_text(encoding="utf-8-sig")),
        qa_records=[json.loads(path.read_text(encoding="utf-8-sig")) for path in qa_paths],
        compile_path=compile_path,
        qa_paths=qa_paths,
    )
    out_dir = args.out_dir if args.out_dir.is_absolute() else REPO_ROOT / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = _slug(str(args.fixture))
    out_json = out_dir / f"{slug}_smoke_summary.json"
    out_md = out_dir / f"{slug}_smoke_summary.md"
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    out_md.write_text(render_markdown(report), encoding="utf-8")
    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")
    print(json.dumps(report["summary"], sort_keys=True))
    return 0


def build_report(
    *,
    fixture: str,
    compile_record: dict[str, Any],
    qa_records: list[dict[str, Any]],
    compile_path: Path | None = None,
    qa_paths: list[Path] | None = None,
) -> dict[str, Any]:
    source_compile = compile_record.get("source_compile", {}) if isinstance(compile_record.get("source_compile"), dict) else {}
    parsed_ok = bool(compile_record.get("parsed_ok", True))
    compile_status = _compile_status(compile_record, source_compile)
    qa_rows = _merged_qa_rows(qa_records)
    verdict_counts = Counter(str((row.get("reference_judge") or {}).get("verdict", "unknown")) for row in qa_rows)
    failure_counts = Counter(_failure_surface(row) for row in qa_rows if _is_non_exact(row))
    non_exact_rows = [
        {
            "id": str(row.get("id", "")),
            "question": str(row.get("utterance", "")),
            "verdict": str((row.get("reference_judge") or {}).get("verdict", "unknown")),
            "failure_surface": _failure_surface(row),
            "reference_answer": str(row.get("reference_answer", "")),
            "queries": row.get("queries", []) if isinstance(row.get("queries"), list) else [],
        }
        for row in qa_rows
        if _is_non_exact(row)
    ]
    compile_health = source_compile.get("compile_health", {}) if isinstance(source_compile.get("compile_health"), dict) else {}
    semantic_progress = compile_health.get("semantic_progress", {}) if isinstance(compile_health.get("semantic_progress"), dict) else {}
    return {
        "schema_version": "incoming_fixture_smoke_summary_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "fixture": fixture,
        "policy": [
            "Summarizes compile and QA artifacts only.",
            "Does not read source prose for meaning or rerun compilation, QA, judging, or classification.",
        ],
        "artifacts": {
            "compile_json": _display_path(compile_path) if compile_path else "",
            "qa_json": [_display_path(path) for path in qa_paths or []],
        },
        "summary": {
            "profile_fallback": _profile_fallback(compile_record),
            "compile_status": compile_status,
            "compile_parsed_ok": parsed_ok,
            "compile_parse_error": str(compile_record.get("parse_error", "")),
            "compile_admitted": int(source_compile.get("admitted_count", 0) or 0),
            "compile_skipped": int(source_compile.get("skipped_count", 0) or 0),
            "compile_health": str(compile_health.get("verdict", "")),
            "semantic_progress_risk": str(semantic_progress.get("zombie_risk", "")),
            "semantic_progress_action": str(semantic_progress.get("recommended_action", "")),
            "qa_rows": len(qa_rows),
            "judge_counts": dict(verdict_counts),
            "failure_surface_counts": dict(failure_counts),
            "write_proposal_rows": sum(1 for row in qa_rows if row.get("proposed_facts") or row.get("proposed_rules")),
        },
        "surface_contribution": source_compile.get("surface_contribution", [])
        if isinstance(source_compile.get("surface_contribution"), list)
        else [],
        "non_exact_rows": non_exact_rows,
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report.get("summary", {}) if isinstance(report.get("summary"), dict) else {}
    lines = [
        f"# Incoming Fixture Smoke Summary: {report.get('fixture', '')}",
        "",
        f"Generated: {report.get('generated_at', '')}",
        "",
        "## Summary",
        "",
        f"- Compile admitted/skipped: `{summary.get('compile_admitted', 0)}` / `{summary.get('compile_skipped', 0)}`",
        f"- Profile fallback: `{summary.get('profile_fallback', '')}`",
        f"- Compile status: `{summary.get('compile_status', '')}`",
        f"- Compile parsed OK: `{summary.get('compile_parsed_ok', True)}`",
        f"- Compile parse error: `{summary.get('compile_parse_error', '')}`",
        f"- Compile health: `{summary.get('compile_health', '')}`",
        f"- Semantic progress: `{summary.get('semantic_progress_risk', '')}` / `{summary.get('semantic_progress_action', '')}`",
        f"- QA rows: `{summary.get('qa_rows', 0)}`",
        f"- Judge counts: `{summary.get('judge_counts', {})}`",
        f"- Failure surfaces: `{summary.get('failure_surface_counts', {})}`",
        f"- Write proposal rows: `{summary.get('write_proposal_rows', 0)}`",
        "",
        "## Surface Contribution",
        "",
        "| Pass | Unique | Duplicates | Health | Purpose |",
        "| --- | ---: | ---: | --- | --- |",
    ]
    for row in report.get("surface_contribution", []):
        if not isinstance(row, dict):
            continue
        lines.append(
            f"| `{row.get('pass_id', '')}` | {row.get('unique_contribution_count', 0)} | "
            f"{row.get('duplicate_count', 0)} | `{','.join(row.get('health_flags', []) or ['ok'])}` | "
            f"{str(row.get('purpose', '')).replace('|', '/')[:100]} |"
        )
    lines.extend(["", "## Non-Exact Rows", "", "| Row | Verdict | Surface | Question |", "| --- | --- | --- | --- |"])
    for row in report.get("non_exact_rows", []):
        if not isinstance(row, dict):
            continue
        question = str(row.get("question", "")).replace("|", "/")
        lines.append(f"| `{row.get('id', '')}` | `{row.get('verdict', '')}` | `{row.get('failure_surface', '')}` | {question} |")
    lines.append("")
    return "\n".join(lines)


def _merged_qa_rows(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id: dict[str, dict[str, Any]] = {}
    order: list[str] = []
    for record in records:
        for row in record.get("rows", []) if isinstance(record.get("rows"), list) else []:
            if not isinstance(row, dict):
                continue
            row_id = str(row.get("id", ""))
            if not row_id:
                continue
            if row_id not in by_id:
                order.append(row_id)
                by_id[row_id] = {}
            by_id[row_id].update(row)
    return [by_id[row_id] for row_id in order]


def _compile_status(compile_record: dict[str, Any], source_compile: dict[str, Any]) -> str:
    if source_compile:
        return "compiled"
    if compile_record.get("parsed_ok") is False:
        return "compile_parse_failed"
    return "compile_missing"


def _profile_fallback(compile_record: dict[str, Any]) -> str:
    roster = compile_record.get("profile_signature_roster_retry")
    if isinstance(roster, dict) and roster.get("parsed_ok") is True:
        return "signature_roster"
    retry = compile_record.get("profile_retry")
    if isinstance(retry, dict) and retry.get("parsed_ok") is True:
        return "compact_profile_retry"
    return ""


def _is_non_exact(row: dict[str, Any]) -> bool:
    return str((row.get("reference_judge") or {}).get("verdict", "")) not in {"", "exact"}


def _failure_surface(row: dict[str, Any]) -> str:
    surface = row.get("failure_surface")
    if isinstance(surface, dict):
        label = str(surface.get("surface", "")).strip()
        if label:
            return label
    return "unclassified"


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


def _display_path(value: Path | str | None) -> str:
    if value is None:
        return ""
    path = value if isinstance(value, Path) else Path(str(value))
    try:
        return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)
    except ValueError:
        return str(path)


def _slug(value: str) -> str:
    out = "".join(ch.lower() if ch.isalnum() else "-" for ch in str(value or ""))
    out = "-".join(part for part in out.split("-") if part)
    return out or "incoming-fixture"


if __name__ == "__main__":
    raise SystemExit(main())
