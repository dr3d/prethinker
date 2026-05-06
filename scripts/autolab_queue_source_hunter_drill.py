#!/usr/bin/env python3
"""Queue tiny Hermes source-hunter skill drills.

These drills train artifact discipline before open-ended source hunting. They
ask Hermes to write a small, known artifact shape, run the validator, and stop.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MAILBOX = Path(r"\\192.168.0.103\c\prethinker\tmp\hermes_mailbox")
DEFAULT_WSL_MAILBOX = "/mnt/c/prethinker/tmp/hermes_mailbox"
DRILLS = {"blocked_report", "static_source"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mailbox", type=Path, default=DEFAULT_MAILBOX)
    parser.add_argument("--wsl-mailbox", default=DEFAULT_WSL_MAILBOX)
    parser.add_argument("--job-id", default="")
    parser.add_argument("--drill", choices=sorted(DRILLS), required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--out-md", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    job_id = args.job_id.strip() or f"source_hunter_{args.drill}_{utcstamp()}"
    mailbox = _resolve_mailbox(args.mailbox)
    markdown = build_job_markdown(
        job_id=job_id,
        drill=str(args.drill),
        wsl_mailbox=str(args.wsl_mailbox).rstrip("/"),
    )
    out_path = _resolve_out_path(args.out_md, mailbox=mailbox, job_id=job_id)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(markdown, encoding="utf-8")
    print(f"Wrote {out_path}")
    if args.dry_run:
        print("dry_run=true")
    return 0


def build_job_markdown(*, job_id: str, drill: str, wsl_mailbox: str = DEFAULT_WSL_MAILBOX) -> str:
    if drill not in DRILLS:
        raise ValueError(f"unknown drill: {drill}")
    run_dir = f"{wsl_mailbox.rstrip('/')}/runs/{job_id}"
    lines = [
        f"job_id: {job_id}",
        "kind: markdown",
        "priority: training",
        "role: autolab_source_hunter_drill",
        f"required_artifact: {run_dir}/wildbench_pilot_summary.md",
        f"required_artifact: {run_dir}/wildbench_pilot_summary.json",
        f"required_artifact: {run_dir}/candidate_validation.json",
        f"required_validation_report: {run_dir}/candidate_validation.json",
        "local_lmstudio_base_url: http://127.0.0.1:1234/v1",
        "heavy_lmstudio_base_url: http://192.168.0.150:1234/v1",
        "",
        "# Autolab Source-Hunter Drill",
        "",
        "You are Hermes doing a tiny Prethinker Autolab source-hunter skill drill.",
        "Do not search the web unless this packet explicitly says to.",
        "Do not edit tracked repo files. Do not run heavy compiles. Do not use the desktop LM Studio endpoint.",
        "Write the required files, run validation, update the summaries, and stop.",
        "Do not merely describe files in stdout. A file only counts if it exists on disk.",
        "",
        f"Create `{run_dir}`.",
        "",
    ]
    if drill == "blocked_report":
        lines.extend(_blocked_report_drill(run_dir=run_dir, job_id=job_id))
    else:
        lines.extend(_static_source_drill(run_dir=run_dir))
    lines.extend(
        [
            "## Validation",
            "",
            "Run exactly:",
            "",
            "```bash",
            f"python scripts/validate_autolab_candidate_artifacts.py --root {run_dir} --out-json {run_dir}/candidate_validation.json",
            "```",
            "",
            "After validation, verify the files exist:",
            "",
            "```bash",
            f"ls -la {run_dir}",
            "```",
            "",
            "Final response should be one short paragraph with artifact paths and validator pass/fail counts.",
            "",
        ]
    )
    return "\n".join(lines)


def _blocked_report_drill(*, run_dir: str, job_id: str) -> list[str]:
    return [
        "## Drill: Blocked Report",
        "",
        "Do not hunt for a source. This drill only proves you can write a valid blocked-hunt artifact.",
        "",
        f"Write `{run_dir}/source_hunt_blocked.json` with this exact schema family:",
        "",
        "```json",
        "{",
        '  "schema_version": "autolab_source_hunt_blocked_v1",',
        f'  "job_id": "{job_id}",',
        '  "attempted_urls": [',
        '    {"url": "https://example.invalid/static-minutes.pdf", "failure_mode": "network_blocked"},',
        '    {"url": "https://example.invalid/archive-index.html", "failure_mode": "no_results"}',
        "  ],",
        '  "candidate_count": 0,',
        '  "recommendation": "retry_domain",',
        '  "notes": "Training drill: blocked report artifact only."',
        "}",
        "```",
        "",
        f"Write `{run_dir}/wildbench_pilot_summary.md` saying this was a blocked-report drill with zero candidates.",
        f"Write `{run_dir}/wildbench_pilot_summary.json` with `status` set to `blocked_report_drill` and `candidate_count` set to `0`.",
        "",
    ]


def _static_source_drill(*, run_dir: str) -> list[str]:
    candidate_dir = f"{run_dir}/candidate_001"
    return [
        "## Drill: Static Source Candidate",
        "",
        "Do not hunt for a source. This drill only proves you can write a valid source candidate artifact.",
        "",
        f"Create `{candidate_dir}`.",
        f"Write `{candidate_dir}/source.md` with a short public-domain-style mock source packet:",
        "",
        "```markdown",
        "# Static Drill Source",
        "",
        "Provenance URL: https://example.org/static-drill-source",
        "",
        "The Board adopted Resolution 12 on March 3, 2026. The resolution requires a follow-up inspection before the permit becomes active. The clerk noted that the inspection date was not yet scheduled.",
        "```",
        "",
        f"Write `{candidate_dir}/source_candidate.json`:",
        "",
        "```json",
        "{",
        '  "schema_version": "autolab_source_candidate_v1",',
        '  "candidate_id": "static_drill_source_001",',
        '  "source_url": "https://example.org/static-drill-source",',
        '  "domain_label": "governance",',
        '  "why_it_is_hard": ["temporal_status", "authority_chain"],',
        '  "expected_sparse_score": "medium",',
        '  "provenance_notes": "Training drill source with pending activation state.",',
        f'  "source_text_path": "{candidate_dir}/source.md",',
        '  "do_not_use_reason": ""',
        "}",
        "```",
        "",
        f"Write `{run_dir}/wildbench_pilot_summary.md` saying this was a static source-candidate drill with one candidate.",
        f"Write `{run_dir}/wildbench_pilot_summary.json` with `status` set to `static_source_drill` and `candidate_count` set to `1`.",
        "",
    ]


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
