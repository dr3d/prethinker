#!/usr/bin/env python3
"""Score QA rows under an explicit source-support adjudication ledger.

This is a reporting tool, not an instrument component. It does not inspect
source prose, parse user utterances, call an LLM, mutate datasets, or change QA
verdicts. It keeps the raw score visible while also reporting a provisional
source-contained view after explicitly adjudicated oracle/source-scope rows are
excluded.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import sys
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.adjudicate_qa_residue import _compact_row_id, _load_qa_runs, _select_latest_rows, _verdict


EXCLUDE_POLICIES = {"exclude_from_source_contained_score", "review_before_scoring"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qa-root", action="append", default=[], type=Path, help="Directory containing QA JSON artifacts.")
    parser.add_argument("--qa-json", action="append", default=[], type=Path, help="Individual QA JSON artifact.")
    parser.add_argument("--adjudication-json", required=True, type=Path, help="Source-support adjudication ledger.")
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(
        qa_roots=tuple(args.qa_root),
        qa_jsons=tuple(args.qa_json),
        adjudication_json=args.adjudication_json,
    )
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(render_markdown(report), encoding="utf-8")
    if not args.out_json and not args.out_md:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


def build_report(
    *,
    qa_roots: tuple[Path, ...] = (),
    qa_jsons: tuple[Path, ...] = (),
    adjudication_json: Path,
) -> dict[str, Any]:
    runs = _load_qa_runs(qa_roots=qa_roots, qa_jsons=qa_jsons)
    selected_rows = _select_latest_rows(runs)
    decisions = _load_decisions(adjudication_json)
    raw_counts: Counter[str] = Counter()
    provisional_counts: Counter[str] = Counter()
    decision_counts: Counter[str] = Counter()
    policy_counts: Counter[str] = Counter()
    adjudicated_rows: list[dict[str, Any]] = []
    selected_keys: set[tuple[str, str]] = set()
    excluded_count = 0
    reviewed_count = 0

    for fixture, row_id, qa_path, row, _data in selected_rows:
        key = (fixture, row_id)
        selected_keys.add(key)
        verdict = _verdict(row)
        raw_counts[verdict] += 1
        decision = decisions.get(key)
        if decision:
            reviewed_count += 1
            decision_counts[str(decision.get("decision") or "unknown")] += 1
            policy = str(decision.get("score_policy") or "keep_scored")
            policy_counts[policy] += 1
            excluded = policy in EXCLUDE_POLICIES
            if excluded:
                excluded_count += 1
            else:
                provisional_counts[verdict] += 1
            adjudicated_rows.append(
                {
                    "fixture": fixture,
                    "row_id": row_id,
                    "verdict": verdict,
                    "decision": decision.get("decision", ""),
                    "score_policy": policy,
                    "recommended_action": decision.get("recommended_action", ""),
                    "rationale": decision.get("rationale", ""),
                    "qa_json": str(qa_path),
                }
            )
        else:
            provisional_counts[verdict] += 1

    missing_decisions = [
        {"fixture": fixture, "row_id": row_id, **decision}
        for (fixture, row_id), decision in sorted(decisions.items())
        if (fixture, row_id) not in selected_keys
    ]
    return {
        "schema_version": "source_support_adjudication_score_v1",
        "generated": datetime.now(timezone.utc).isoformat(),
        "adjudication_json": str(_absolute(adjudication_json)),
        "summary": {
            "question_count": sum(raw_counts.values()),
            "raw_counts": dict(sorted(raw_counts.items())),
            "raw_exact_rate": _exact_rate(raw_counts),
            "reviewed_row_count": reviewed_count,
            "excluded_from_source_contained_count": excluded_count,
            "provisional_source_contained_question_count": sum(provisional_counts.values()),
            "provisional_source_contained_counts": dict(sorted(provisional_counts.items())),
            "provisional_source_contained_exact_rate": _exact_rate(provisional_counts),
            "decision_counts": dict(sorted(decision_counts.items())),
            "score_policy_counts": dict(sorted(policy_counts.items())),
            "missing_decision_count": len(missing_decisions),
        },
        "adjudicated_rows": sorted(adjudicated_rows, key=lambda item: (item["fixture"], item["row_id"])),
        "missing_decisions": missing_decisions,
    }


def _load_decisions(path: Path) -> dict[tuple[str, str], dict[str, Any]]:
    data = json.loads(_absolute(path).read_text(encoding="utf-8"))
    decisions: dict[tuple[str, str], dict[str, Any]] = {}
    for row in data.get("rows", []) or []:
        if not isinstance(row, dict):
            continue
        fixture = str(row.get("fixture") or "").strip()
        row_id = _compact_row_id(fixture, row.get("row_id") or row.get("id") or "")
        if not fixture or not row_id:
            continue
        decisions[(fixture, row_id)] = row
    return decisions


def render_markdown(report: dict[str, Any]) -> str:
    summary = report.get("summary", {}) if isinstance(report.get("summary"), dict) else {}
    lines = [
        "# Source-Support Adjudication Score",
        "",
        f"- Generated: `{report.get('generated', '')}`",
        f"- Adjudication ledger: `{report.get('adjudication_json', '')}`",
        f"- Questions: `{summary.get('question_count', 0)}`",
        f"- Raw counts: `{_format_counts(summary.get('raw_counts', {}))}`",
        f"- Raw exact rate: `{summary.get('raw_exact_rate', 0.0)}`",
        f"- Reviewed rows: `{summary.get('reviewed_row_count', 0)}`",
        f"- Excluded from source-contained view: `{summary.get('excluded_from_source_contained_count', 0)}`",
        f"- Provisional source-contained questions: `{summary.get('provisional_source_contained_question_count', 0)}`",
        f"- Provisional source-contained counts: `{_format_counts(summary.get('provisional_source_contained_counts', {}))}`",
        f"- Provisional source-contained exact rate: `{summary.get('provisional_source_contained_exact_rate', 0.0)}`",
        f"- Decisions: `{_format_counts(summary.get('decision_counts', {}))}`",
        f"- Score policies: `{_format_counts(summary.get('score_policy_counts', {}))}`",
        "",
        "This report does not replace the raw score. It only shows what remains after explicitly reviewed source/oracle-scope rows are set aside.",
        "",
        "| Fixture | Row | Verdict | Decision | Score Policy | Recommended Action |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in report.get("adjudicated_rows", []) or []:
        lines.append(
            "| `{fixture}` | `{row_id}` | `{verdict}` | `{decision}` | `{policy}` | `{action}` |".format(
                fixture=row.get("fixture", ""),
                row_id=row.get("row_id", ""),
                verdict=row.get("verdict", ""),
                decision=row.get("decision", ""),
                policy=row.get("score_policy", ""),
                action=row.get("recommended_action", ""),
            )
        )
    if report.get("missing_decisions"):
        lines.extend(["", "## Missing Decisions", ""])
        for row in report.get("missing_decisions", []):
            lines.append(f"- `{row.get('fixture', '')}` `{row.get('row_id', '')}`")
    return "\n".join(lines).rstrip() + "\n"


def _format_counts(counts: Any) -> str:
    if not isinstance(counts, dict) or not counts:
        return "-"
    return ", ".join(f"{key}:{value}" for key, value in sorted(counts.items()))


def _exact_rate(counts: Counter[str]) -> float:
    total = sum(counts.values())
    if not total:
        return 0.0
    return round(counts.get("exact", 0) / total, 4)


def _absolute(path: Path) -> Path:
    return path if path.is_absolute() else Path.cwd() / path


if __name__ == "__main__":
    raise SystemExit(main())
