#!/usr/bin/env python3
"""Queue a bounded Autolab wildbench hunter/QA pilot markdown job."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MAILBOX = Path(r"\\192.168.0.103\c\prethinker\tmp\hermes_mailbox")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mailbox", type=Path, default=DEFAULT_MAILBOX)
    parser.add_argument("--job-id", default="")
    parser.add_argument("--candidate-count", type=int, default=2)
    parser.add_argument("--qa-rows", type=int, default=12)
    parser.add_argument("--source-only", action="store_true", help="Queue only source-hunter artifacts.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--out-md", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    job_id = args.job_id.strip() or f"wildbench_pilot_{utcstamp()}"
    candidate_count = max(1, min(int(args.candidate_count), 4))
    qa_rows = max(10, min(int(args.qa_rows), 25))
    mailbox = _resolve_mailbox(args.mailbox)
    markdown = build_job_markdown(
        job_id=job_id,
        candidate_count=candidate_count,
        qa_rows=qa_rows,
        source_only=bool(args.source_only),
    )
    out_path = _resolve_out_path(args.out_md, mailbox=mailbox, job_id=job_id)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(markdown, encoding="utf-8")
    print(f"Wrote {out_path}")
    if args.dry_run:
        print("dry_run=true")
    return 0


def build_job_markdown(*, job_id: str, candidate_count: int, qa_rows: int, source_only: bool = False) -> str:
    run_dir = f"tmp/hermes_mailbox/runs/{job_id}"
    role = "autolab_source_hunter" if source_only else "autolab_source_hunter_and_qa_drafter"
    candidate_dirs = [f"`{run_dir}/candidate_{index:03d}/`" for index in range(1, candidate_count + 1)]
    lines = [
        f"job_id: {job_id}",
        "kind: markdown",
        "priority: exploratory",
        f"role: {role}",
        "local_lmstudio_base_url: http://127.0.0.1:1234/v1",
        "heavy_lmstudio_base_url: http://192.168.0.150:1234/v1",
        "",
        "# Autolab Wildbench Pilot",
        "",
        "You are Hermes acting as a bounded Prethinker Autolab researcher.",
        "Do not edit tracked repo files. Do not run Prethinker heavy compiles.",
        "Do not call the desktop heavy LM Studio endpoint for this job.",
        "Do not loop or wait for chat. Produce artifacts, validate them, summarize, and stop.",
        "",
        "## Goal",
        "",
        f"Find {candidate_count} real-world public source packets that could become sparse or messy Prethinker stress fixtures.",
        "Prefer material that may never deserve a 100% score because the evidence is thin, partial, cross-referenced, corrected, or unresolved.",
        "The point is to expose uncertainty, absence, clarification, and zombie-answer pressure.",
        "",
        "Good sources include public enforcement letters, committee minutes, procurement protests, grant amendments, recall/safety/audit reports, museum/archive records, and policy pages with exceptions or effective dates.",
        "",
        "If web/network access is unavailable, write a short blocked report to the run directory and stop successfully. Do not invent sources.",
        "",
        "## Required Run Directory",
        "",
        f"Create `{run_dir}`.",
        "",
        "For each candidate, create a subdirectory:",
        "",
        *candidate_dirs,
        "",
        "Use more candidate directories only if this job asked for more than two candidates.",
        "",
        "Each candidate directory must contain:",
        "",
        "- `source.md`: cleaned source text with provenance URL at the top.",
        "- `source_candidate.json`: one source-hunter artifact.",
    ]
    if not source_only:
        lines.extend(["- `qa_candidate.json`: one QA-drafter artifact.", ""])
    else:
        lines.extend(
            [
                "",
                "This source-only pilot should not draft QA yet. The next job will draft QA after Codex sees whether the source candidate is real and useful.",
                "",
            ]
        )
    lines.extend(
        [
            "Also write:",
            "",
            f"- `{run_dir}/wildbench_pilot_summary.md`",
            f"- `{run_dir}/wildbench_pilot_summary.json`",
            "",
            "## Source Candidate JSON",
            "",
            "Use exactly this schema shape:",
            "",
            "```json",
            "{",
            '  "schema_version": "autolab_source_candidate_v1",',
            '  "candidate_id": "short_safe_slug",',
            '  "source_url": "https://...",',
            '  "domain_label": "regulatory | governance | archive | safety | policy | other",',
            '  "why_it_is_hard": ["temporal_status", "authority_chain"],',
            '  "expected_sparse_score": "low | medium | high",',
            '  "provenance_notes": "short note",',
            f'  "source_text_path": "{run_dir}/candidate_001/source.md",',
            '  "do_not_use_reason": ""',
            "}",
            "```",
            "",
        ]
    )
    if not source_only:
        lines.extend(
            [
                "## QA Candidate JSON",
                "",
                f"Write exactly {qa_rows} QA rows per candidate. Do not include answer keys.",
                "At least one row should have `expected_answer_mode` of `uncertain`, `not_established`, or `clarification`.",
                "Cover at least three `surface_family` values.",
                "",
                "Use exactly this schema shape:",
                "",
                "```json",
                "{",
                '  "schema_version": "autolab_candidate_qa_v1",',
                '  "source_candidate_id": "short_safe_slug",',
                '  "rows": [',
                "    {",
                '      "qid": "q001",',
                '      "question": "What does the source establish about X?",',
                '      "surface_family": "temporal_status",',
                '      "expected_answer_mode": "exact | uncertain | not_established | clarification",',
                '      "source_anchor": "short section label or short quote",',
                '      "why_this_is_hard": "short reason"',
                "    }",
                "  ]",
                "}",
                "```",
                "",
            ]
        )
    lines.extend(
        [
            "## Validation",
            "",
            "After writing the artifacts, run:",
            "",
            "```bash",
            f"python scripts/validate_autolab_candidate_artifacts.py --root {run_dir} --out-json {run_dir}/candidate_validation.json",
            "```",
            "",
            "If the validator fails, fix your JSON artifacts once and rerun the validator. If it still fails, leave the failed validation report and explain the failure in the summary.",
            "",
            "## Summary",
            "",
            "Your final Hermes response should be short and include:",
            "",
            "- candidate count;",
            "- validation pass/fail counts;",
            "- source URLs;",
            "- the hardest surface each candidate appears to stress;",
            "- whether Codex should review, reject, or ask for a different hunter job.",
            "",
            "Then stop.",
            "",
        ]
    )
    return "\n".join(lines)


def utcstamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _resolve_mailbox(path: Path) -> Path:
    return path if path.is_absolute() or str(path).startswith("\\\\") else REPO_ROOT / path


def _resolve_out_path(out_md: Path | None, *, mailbox: Path, job_id: str) -> Path:
    if out_md is None:
        return mailbox / "inbox" / f"{job_id}.md"
    return out_md if out_md.is_absolute() else REPO_ROOT / out_md


if __name__ == "__main__":
    raise SystemExit(main())
