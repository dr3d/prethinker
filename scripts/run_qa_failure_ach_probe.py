#!/usr/bin/env python3
"""Run deterministic ACH-style triage over QA non-exact rows."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.qa_failure_ach import analyze_qa_failure_batch  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qa-summary", type=Path, required=True)
    parser.add_argument("--artifact-root", type=Path, default=None)
    parser.add_argument("--include-failure-label", action="store_true")
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary_path = _resolve(args.qa_summary)
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    report = analyze_qa_failure_batch(
        payload,
        artifact_root=_resolve(args.artifact_root) if args.artifact_root else None,
        include_failure_label=bool(args.include_failure_label),
    )
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "qa_summary": str(summary_path),
        "include_failure_label": bool(args.include_failure_label),
        **report,
    }
    if args.out_json:
        out_json = _resolve(args.out_json)
        out_json.parent.mkdir(parents=True, exist_ok=True)
        out_json.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    if args.out_md:
        out_md = _resolve(args.out_md)
        out_md.parent.mkdir(parents=True, exist_ok=True)
        out_md.write_text(render_markdown(report), encoding="utf-8")
    if not args.out_json and not args.out_md:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0


def render_markdown(report: dict[str, Any]) -> str:
    summary = report.get("summary", {}) if isinstance(report.get("summary"), dict) else {}
    lines = [
        "# QA Failure ACH Probe",
        "",
        f"Generated: {report.get('generated_at', '')}",
        f"QA summary: `{report.get('qa_summary', '')}`",
        f"Included existing failure label as evidence: `{report.get('include_failure_label', False)}`",
        "",
        "## Summary",
        "",
        f"- Rows: `{summary.get('row_count', 0)}`",
        f"- Top hypothesis counts: `{summary.get('top_hypothesis_counts', {})}`",
        f"- Failure-surface counts: `{summary.get('failure_surface_counts', {})}`",
        f"- Response-status counts: `{summary.get('response_status_counts', {})}`",
        f"- Classifier agreement: `{summary.get('classifier_agreement_counts', {})}`",
        "",
        "## Family Top Hypotheses",
        "",
        "| Family | Top Hypothesis Counts |",
        "| --- | --- |",
    ]
    for family, counts in (summary.get("family_top_hypothesis_counts", {}) or {}).items():
        lines.append(f"| `{family}` | `{counts}` |")

    lines.extend(
        [
            "",
            "## Rows",
            "",
            "| Row | Verdict | Surface | ACH Top | Agreement | Features |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in report.get("rows", []) or []:
        if not isinstance(row, dict):
            continue
        features = row.get("feature_summary", {}) if isinstance(row.get("feature_summary"), dict) else {}
        feature_text = (
            f"q={features.get('query_count', 0)} "
            f"nonempty={features.get('nonempty_query_count', 0)} "
            f"direct={features.get('direct_nonempty_count', 0)} "
            f"source_record={features.get('source_record_nonempty_count', 0)} "
            f"support={features.get('support_surface_count', 0)} "
            f"shapes={features.get('question_shapes', [])}"
        )
        lines.append(
            "| `{fixture}` `{qid}` | `{verdict}` | `{surface}` | `{top}` | `{agreement}` | {features} |".format(
                fixture=_clean(row.get("fixture", "")),
                qid=_clean(row.get("id", "")),
                verdict=_clean(row.get("verdict", "")),
                surface=_clean(row.get("failure_surface", "")),
                top=_clean(",".join(row.get("top_hypotheses", []) or [])),
                agreement=_clean(row.get("classifier_agreement", "")),
                features=_clean(feature_text),
            )
        )
    return "\n".join(lines).rstrip() + "\n"


def _resolve(path: Path | None) -> Path | None:
    if path is None:
        return None
    return path if path.is_absolute() else REPO_ROOT / path


def _clean(value: Any) -> str:
    return str(value).replace("|", "/").replace("\n", " ").strip()


if __name__ == "__main__":
    raise SystemExit(main())
