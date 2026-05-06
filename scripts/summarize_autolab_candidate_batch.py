#!/usr/bin/env python3
"""Summarize Autolab wildbench candidate artifacts for Codex review."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_SCHEMA = "autolab_source_candidate_v1"
QA_SCHEMA = "autolab_candidate_qa_v1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = _resolve(args.root)
    report = build_report(root=root)
    if args.out_json:
        out_json = _resolve(args.out_json)
        out_json.parent.mkdir(parents=True, exist_ok=True)
        out_json.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        print(f"Wrote {out_json}")
    if args.out_md:
        out_md = _resolve(args.out_md)
        out_md.parent.mkdir(parents=True, exist_ok=True)
        out_md.write_text(render_markdown(report), encoding="utf-8")
        print(f"Wrote {out_md}")
    print(render_text(report))
    return 0


def build_report(*, root: Path) -> dict[str, Any]:
    source_candidates: list[dict[str, Any]] = []
    qa_candidates: list[dict[str, Any]] = []
    validation_reports: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*.json")) if root.exists() else []:
        payload = _read_json(path)
        schema = str(payload.get("schema_version", "")).strip() if isinstance(payload, dict) else ""
        if schema == SOURCE_SCHEMA:
            source_candidates.append(_source_summary(path, payload))
        elif schema == QA_SCHEMA:
            qa_candidates.append(_qa_summary(path, payload))
        elif schema == "autolab_candidate_artifact_validation_v1":
            validation_reports.append(_validation_summary(path, payload))
    hard_surface_counts = Counter(
        surface
        for candidate in source_candidates
        for surface in candidate.get("why_it_is_hard", [])
        if str(surface).strip()
    )
    qa_surface_counts = Counter(
        surface for candidate in qa_candidates for surface, count in candidate.get("surface_counts", {}).items() for _ in range(count)
    )
    return {
        "schema_version": "autolab_candidate_batch_summary_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "root": _display_path(root),
        "policy": [
            "Summarizes structured candidate artifacts only.",
            "Does not interpret source prose, infer answers, compile, query, judge, harvest, or promote.",
        ],
        "summary": {
            "source_candidate_count": len(source_candidates),
            "qa_candidate_count": len(qa_candidates),
            "validation_report_count": len(validation_reports),
            "hard_surface_counts": dict(sorted(hard_surface_counts.items())),
            "qa_surface_counts": dict(sorted(qa_surface_counts.items())),
        },
        "source_candidates": source_candidates,
        "qa_candidates": qa_candidates,
        "validation_reports": validation_reports,
    }


def render_text(report: dict[str, Any]) -> str:
    summary = report.get("summary", {})
    return (
        "Autolab candidate batch summary\n"
        f"sources={summary.get('source_candidate_count', 0)} "
        f"qa={summary.get('qa_candidate_count', 0)} "
        f"validations={summary.get('validation_report_count', 0)}"
    )


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Autolab Candidate Batch Summary",
        "",
        f"- root: `{report.get('root', '')}`",
        f"- source candidates: `{report.get('summary', {}).get('source_candidate_count', 0)}`",
        f"- QA candidates: `{report.get('summary', {}).get('qa_candidate_count', 0)}`",
        f"- validation reports: `{report.get('summary', {}).get('validation_report_count', 0)}`",
        "",
        "## Source Candidates",
        "",
    ]
    for candidate in report.get("source_candidates", []):
        lines.extend(
            [
                f"### {candidate.get('candidate_id', '')}",
                "",
                f"- domain: `{candidate.get('domain_label', '')}`",
                f"- expected_sparse_score: `{candidate.get('expected_sparse_score', '')}`",
                f"- source_url: {candidate.get('source_url', '')}",
                f"- hard surfaces: `{', '.join(candidate.get('why_it_is_hard', []))}`",
                f"- source_text_path: `{candidate.get('source_text_path', '')}`",
                f"- artifact: `{candidate.get('path', '')}`",
                "",
            ]
        )
    if not report.get("source_candidates"):
        lines.extend(["No source candidates found.", ""])
    if report.get("qa_candidates"):
        lines.extend(["## QA Candidates", ""])
        for candidate in report.get("qa_candidates", []):
            lines.extend(
                [
                    f"### {candidate.get('source_candidate_id', '')}",
                    "",
                    f"- rows: `{candidate.get('row_count', 0)}`",
                    f"- modes: `{candidate.get('mode_counts', {})}`",
                    f"- surfaces: `{candidate.get('surface_counts', {})}`",
                    f"- artifact: `{candidate.get('path', '')}`",
                    "",
                ]
            )
    return "\n".join(lines)


def _source_summary(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "candidate_id": str(payload.get("candidate_id", "")).strip(),
        "path": _display_path(path),
        "source_url": str(payload.get("source_url", "")).strip(),
        "domain_label": str(payload.get("domain_label", "")).strip(),
        "why_it_is_hard": [str(item).strip() for item in payload.get("why_it_is_hard", []) if str(item).strip()],
        "expected_sparse_score": str(payload.get("expected_sparse_score", "")).strip(),
        "source_text_path": str(payload.get("source_text_path", "")).strip(),
        "do_not_use_reason": str(payload.get("do_not_use_reason", "")).strip(),
    }


def _qa_summary(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    rows = payload.get("rows", []) if isinstance(payload.get("rows", []), list) else []
    surface_counts = Counter(str(row.get("surface_family", "")).strip() for row in rows if isinstance(row, dict))
    mode_counts = Counter(str(row.get("expected_answer_mode", "")).strip() for row in rows if isinstance(row, dict))
    return {
        "source_candidate_id": str(payload.get("source_candidate_id", "")).strip(),
        "path": _display_path(path),
        "row_count": len(rows),
        "surface_counts": dict(sorted((key, value) for key, value in surface_counts.items() if key)),
        "mode_counts": dict(sorted((key, value) for key, value in mode_counts.items() if key)),
    }


def _validation_summary(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    summary = payload.get("summary", {}) if isinstance(payload.get("summary"), dict) else {}
    return {
        "path": _display_path(path),
        "passed_artifact_count": int(summary.get("passed_artifact_count", 0) or 0),
        "warning_artifact_count": int(summary.get("warning_artifact_count", 0) or 0),
        "failed_artifact_count": int(summary.get("failed_artifact_count", 0) or 0),
    }


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


def _display_path(value: Path | str) -> str:
    path = value if isinstance(value, Path) else Path(str(value))
    try:
        return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
