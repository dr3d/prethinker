#!/usr/bin/env python3
"""Stop-claim audit for Prethinker's sign-clean standard.

This is stricter than the active leakage tripwire. Passing that tripwire only
means no known fixture names or answer phrases leaked into active runtime code.
Sign-clean additionally requires:

- no raw utterance/question regex semantic routing;
- no Python semantic routing over free-text source/display fields;
- no high-risk fixture/corpus-shaped vocabulary in active code;
- no active fixture-name leaks;
- no narrow active leakage forbidden hits.

Until this audit passes, public accuracy/product claims are blocked.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import scripts.audit_active_instrument_leakage as audit_active_instrument_leakage
from scripts.audit_free_text_semantic_routing import build_report as build_free_text_report
from scripts.audit_fixture_vocabulary_leaks import TERM_POLICIES, scan_fixture_name_leaks, scan_term, summarize_hits
from scripts.audit_utterance_regex_governance import build_report as build_regex_report

DEFAULT_REGEX_PATHS = (
    REPO_ROOT / "scripts" / "run_domain_bootstrap_qa.py",
    REPO_ROOT / "src",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    parser.add_argument("--max-regex-rows", type=int, default=120)
    parser.add_argument(
        "--exit-zero",
        action="store_true",
        help="Write the report but return 0 even when sign-clean status is fail.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(max_regex_rows=max(1, int(args.max_regex_rows)))
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(render_markdown(report), encoding="utf-8")
    if not args.out_json and not args.out_md:
        print(json.dumps(report, indent=2, sort_keys=True))
    if args.exit_zero:
        return 0
    return 0 if report["summary"]["status"] == "pass" else 1


def build_report(*, max_regex_rows: int = 120) -> dict[str, Any]:
    active_report = audit_active_instrument_leakage.build_report(audit_active_instrument_leakage.DEFAULT_PATHS)
    regex_report = build_regex_report(DEFAULT_REGEX_PATHS, max_rows=max_regex_rows)
    free_text_report = build_free_text_report(DEFAULT_REGEX_PATHS, max_rows=max_regex_rows)
    regex_counts = regex_report.get("summary", {}).get("category_counts", {})
    semantic_trigger_count = int(regex_counts.get("semantic_trigger", 0) or 0)
    forbidden_regex_count = int(regex_counts.get("forbidden_or_needs_review", 0) or 0)
    free_text_summary = free_text_report.get("summary", {})
    free_text_semantic_count = int(free_text_summary.get("claim_path_hit_count", 0) or 0)
    free_text_forensic_or_structural_count = int(free_text_summary.get("forensic_or_structural_hit_count", 0) or 0)

    vocab_rows = _fixture_vocabulary_rows()
    high_risk_active = [
        row
        for row in vocab_rows
        if row.get("risk") == "high" and int(row.get("counts", {}).get("active_code", 0) or 0) > 0
    ]
    fixture_name_leaks = scan_fixture_name_leaks()
    active_forbidden = active_report.get("forbidden_hits", [])

    blockers = []
    if active_forbidden:
        blockers.append(
            {
                "class": "active_fixture_or_answer_leak",
                "count": len(active_forbidden),
                "why": "Known fixture names, probe names, or answer phrases appear in active runtime code.",
            }
        )
    if fixture_name_leaks:
        blockers.append(
            {
                "class": "fixture_name_leak",
                "count": len(fixture_name_leaks),
                "why": "Dataset fixture directory names appear in active code or current docs.",
            }
        )
    if high_risk_active:
        blockers.append(
            {
                "class": "high_risk_corpus_shaped_active_vocabulary",
                "count": len(high_risk_active),
                "why": "High-risk legacy/corpus-shaped terms still appear in active code.",
            }
        )
    if semantic_trigger_count:
        blockers.append(
            {
                "class": "raw_utterance_semantic_regex",
                "count": semantic_trigger_count,
                "why": "Python regex still routes on raw utterance/question semantics.",
            }
        )
    if free_text_semantic_count:
        blockers.append(
            {
                "class": "free_text_semantic_routing",
                "count": free_text_semantic_count,
                "why": "Python still pattern-matches or tokenizes prose-like source/display fields.",
            }
        )
    if forbidden_regex_count:
        blockers.append(
            {
                "class": "forbidden_or_needs_review_regex",
                "count": forbidden_regex_count,
                "why": "Regex audit found fixture/batch/probe vocabulary in query-adjacent patterns.",
            }
        )

    status = "fail" if blockers else "pass"
    return {
        "schema_version": "prethinker_sign_clean_audit_v1",
        "claim_status": "blocked" if status == "fail" else "allowed",
        "summary": {
            "status": status,
            "blocker_count": len(blockers),
            "active_forbidden_hit_count": len(active_forbidden),
            "fixture_name_leak_count": len(fixture_name_leaks),
            "high_risk_active_vocabulary_count": len(high_risk_active),
            "raw_utterance_semantic_regex_count": semantic_trigger_count,
            "free_text_semantic_routing_count": free_text_semantic_count,
            "free_text_forensic_or_structural_count": free_text_forensic_or_structural_count,
            "forbidden_or_needs_review_regex_count": forbidden_regex_count,
        },
        "blockers": blockers,
        "active_leakage": active_report.get("summary", {}),
        "regex_governance": regex_report.get("summary", {}),
        "free_text_semantic_routing": free_text_report.get("summary", {}),
        "high_risk_active_vocabulary": high_risk_active,
        "fixture_name_leaks": fixture_name_leaks,
        "regex_rows": regex_report.get("rows", []),
        "free_text_semantic_rows": free_text_report.get("rows", []),
    }


def _fixture_vocabulary_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for policy in TERM_POLICIES:
        hits = scan_term(policy.term)
        rows.append(
            {
                **asdict(policy),
                "counts": summarize_hits(hits),
                "hits": [
                    asdict(hit)
                    for hit in hits
                    if hit.area in {"active_code", "current_docs"}
                ],
            }
        )
    return rows


def render_markdown(report: dict[str, Any]) -> str:
    summary = report.get("summary", {})
    lines = [
        "# Sign-Clean Audit",
        "",
        f"- Schema: `{report.get('schema_version')}`",
        f"- Status: `{summary.get('status')}`",
        f"- Claim status: `{report.get('claim_status')}`",
        f"- Blockers: `{summary.get('blocker_count')}`",
        f"- Active forbidden hits: `{summary.get('active_forbidden_hit_count')}`",
        f"- Fixture-name leaks: `{summary.get('fixture_name_leak_count')}`",
        f"- High-risk active vocabulary terms: `{summary.get('high_risk_active_vocabulary_count')}`",
        f"- Raw utterance semantic regex hits: `{summary.get('raw_utterance_semantic_regex_count')}`",
        f"- Free-text semantic routing claim-path hits: `{summary.get('free_text_semantic_routing_count')}`",
        f"- Free-text forensic/structural hits retained: `{summary.get('free_text_forensic_or_structural_count')}`",
        f"- Forbidden/needs-review regex hits: `{summary.get('forbidden_or_needs_review_regex_count')}`",
        "",
        "## Meaning",
        "",
        "If this audit fails, Prethinker is not sign-clean and public accuracy/product claims are blocked.",
        "The system may still be useful for research, but score claims must be treated as provisional.",
    ]
    blockers = report.get("blockers", [])
    if blockers:
        lines.extend(["", "## Blockers", "", "| Class | Count | Why |", "| --- | ---: | --- |"])
        for blocker in blockers:
            lines.append(
                "| `{}` | {} | {} |".format(
                    blocker.get("class", ""),
                    blocker.get("count", 0),
                    _md_cell(str(blocker.get("why", ""))),
                )
            )
    high_risk = report.get("high_risk_active_vocabulary", [])
    if high_risk:
        lines.extend(["", "## High-Risk Active Vocabulary", "", "| Term | Active code hits | Replacement |", "| --- | ---: | --- |"])
        for row in high_risk:
            counts = row.get("counts", {})
            lines.append(
                "| `{}` | {} | {} |".format(
                    row.get("term", ""),
                    counts.get("active_code", 0),
                    _md_cell(str(row.get("replacement", ""))),
                )
            )
    regex_rows = [row for row in report.get("regex_rows", []) if row.get("category") == "semantic_trigger"]
    if regex_rows:
        lines.extend(["", "## Sample Raw-Utterance Semantic Regex Rows", "", "| File | Line | Function | Pattern |", "| --- | ---: | --- | --- |"])
        for row in regex_rows[:30]:
            lines.append(
                "| `{}` | {} | `{}` | `{}` |".format(
                    row.get("file", ""),
                    row.get("line", ""),
                    row.get("function", ""),
                    _md_cell(str(row.get("pattern", ""))[:100]),
                )
            )
    free_text_rows = report.get("free_text_semantic_rows", [])
    if free_text_rows:
        lines.extend(["", "## Sample Free-Text Semantic Routing Rows", "", "| File | Line | Function | Category | Subject |", "| --- | ---: | --- | --- | --- |"])
        for row in free_text_rows[:30]:
            lines.append(
                "| `{}` | {} | `{}` | `{}` | `{}` |".format(
                    row.get("file", ""),
                    row.get("line", ""),
                    row.get("function", ""),
                    row.get("category", ""),
                    _md_cell(str(row.get("subject", ""))[:120]),
                )
            )
    return "\n".join(lines).rstrip() + "\n"


def _md_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


if __name__ == "__main__":
    raise SystemExit(main())
