#!/usr/bin/env python3
"""Run a direct Autolab artifact drill without Hermes, WSL, or a mailbox.

This is a deterministic local cycle: materialize small source-hunter artifacts,
validate them with the existing candidate validator, summarize them with the
existing batch summarizer, and stop.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.summarize_autolab_candidate_batch import build_report as build_summary_report
from scripts.summarize_autolab_candidate_batch import render_markdown as render_summary_markdown
from scripts.validate_autolab_candidate_artifacts import build_report as build_validation_report
from scripts.validate_autolab_candidate_artifacts import render_text as render_validation_text


DEFAULT_OUT_DIR = REPO_ROOT / "tmp" / "autolab_direct_cycles" / "artifact_drill"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--include-blocked", action="store_true")
    parser.add_argument("--include-source", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = _resolve(args.out_dir)
    include_blocked = bool(args.include_blocked)
    include_source = bool(args.include_source)
    if not include_blocked and not include_source:
        include_blocked = True
        include_source = True
    report = run_cycle(out_dir=out_dir, include_blocked=include_blocked, include_source=include_source)
    print(render_validation_text(report["validation_report"]))
    print(f"Wrote {out_dir}")
    return 0 if report["validation_report"]["summary"]["failed_artifact_count"] == 0 else 1


def run_cycle(*, out_dir: Path, include_blocked: bool = True, include_source: bool = True) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    source_paths: list[Path] = []
    blocked_paths: list[Path] = []
    if include_blocked:
        blocked_paths.append(_write_blocked_report(out_dir))
    if include_source:
        source_paths.append(_write_source_candidate(out_dir))

    validation = build_validation_report(source_paths=source_paths, qa_paths=[], blocked_paths=blocked_paths)
    validation_path = out_dir / "candidate_validation.json"
    validation_path.write_text(json.dumps(validation, indent=2, sort_keys=True), encoding="utf-8")

    summary = build_summary_report(root=out_dir)
    summary_json = out_dir / "candidate_summary.json"
    summary_md = out_dir / "candidate_summary.md"
    summary_json.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    summary_md.write_text(render_summary_markdown(summary), encoding="utf-8")

    manifest = {
        "schema_version": "autolab_direct_artifact_drill_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "out_dir": _display_path(out_dir),
        "policy": [
            "No Hermes, WSL, mailbox, remote agent, source prose interpretation, compile, query, judge, or promotion.",
            "Materializes deterministic artifacts and runs the same validators/summarizers used by Autolab review.",
        ],
        "validation_path": _display_path(validation_path),
        "summary_json_path": _display_path(summary_json),
        "summary_md_path": _display_path(summary_md),
        "validation_summary": validation["summary"],
        "candidate_summary": summary["summary"],
    }
    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return {"manifest": manifest, "validation_report": validation, "summary_report": summary}


def _write_blocked_report(out_dir: Path) -> Path:
    path = out_dir / "source_hunt_blocked.json"
    payload = {
        "schema_version": "autolab_source_hunt_blocked_v1",
        "job_id": "direct_blocked_report_drill",
        "attempted_urls": [
            {"url": "https://example.invalid/static-minutes.pdf", "failure_mode": "network_blocked"},
            {"url": "https://example.invalid/archive-index.html", "failure_mode": "no_results"},
        ],
        "candidate_count": 0,
        "recommendation": "retry_domain",
        "notes": "Direct deterministic drill; no remote source hunting attempted.",
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def _write_source_candidate(out_dir: Path) -> Path:
    candidate_dir = out_dir / "candidate_001"
    candidate_dir.mkdir(parents=True, exist_ok=True)
    source_path = candidate_dir / "source.md"
    source_path.write_text(
        "\n".join(
            [
                "# Static Drill Source",
                "",
                "Provenance URL: https://example.org/static-drill-source",
                "",
                "The Board adopted Resolution 12 on March 3, 2026. The resolution requires a follow-up inspection before the permit becomes active. The clerk noted that the inspection date was not yet scheduled.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    candidate_path = candidate_dir / "source_candidate.json"
    payload = {
        "schema_version": "autolab_source_candidate_v1",
        "candidate_id": "static_drill_source_001",
        "source_url": "https://example.org/static-drill-source",
        "domain_label": "governance",
        "why_it_is_hard": ["temporal_status", "authority_chain"],
        "expected_sparse_score": "medium",
        "provenance_notes": "Direct deterministic drill source with pending activation state.",
        "source_text_path": _display_path(source_path),
        "do_not_use_reason": "",
    }
    candidate_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return candidate_path


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
