#!/usr/bin/env python3
"""Run a deterministic timeline overlay payload and write harness artifacts."""

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

from src.timeline_overlay import analyze_timeline_overlay  # noqa: E402


DEFAULT_OUT_DIR = REPO_ROOT / "tmp" / "timeline_overlay_runs"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--payload", type=Path, required=True, help="Timeline overlay payload JSON.")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload_path = _resolve(args.payload)
    payload = json.loads(payload_path.read_text(encoding="utf-8-sig"))
    report = build_report(payload=payload, payload_path=payload_path)

    out_dir = _resolve(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = _slug(str(payload.get("id") or payload.get("name") or payload_path.stem))
    out_json = _resolve(args.out_json) if args.out_json else out_dir / f"{slug}_timeline_report.json"
    out_md = _resolve(args.out_md) if args.out_md else out_dir / f"{slug}_timeline_report.md"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    out_md.write_text(render_markdown(report), encoding="utf-8")
    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")
    print(json.dumps(report["summary"], sort_keys=True))
    return 0


def build_report(*, payload: dict[str, Any], payload_path: Path | None = None) -> dict[str, Any]:
    timeline_report = analyze_timeline_overlay(payload)
    warnings = timeline_report.get("warnings", []) if isinstance(timeline_report.get("warnings"), list) else []
    return {
        "schema_version": "timeline_overlay_run_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "payload_path": _display_path(payload_path) if payload_path else "",
        "policy": [
            "Runs only deterministic chronology ordering over explicit event rows.",
            "Does not compile documents, query an LLM, mutate KB state, or write durable facts.",
            "Missing or invalid dates are warnings, not guessed values.",
        ],
        "summary": {
            "event_count": int(timeline_report.get("event_count", 0) or 0),
            "dated_event_count": int(timeline_report.get("dated_event_count", 0) or 0),
            "undated_event_count": int(timeline_report.get("undated_event_count", 0) or 0),
            "warning_count": len(warnings),
            "same_date_group_count": len(timeline_report.get("same_date_groups", []) or []),
            "date_gap_count": len(timeline_report.get("date_gaps", []) or []),
        },
        "timeline_report": timeline_report,
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report.get("summary", {}) if isinstance(report.get("summary"), dict) else {}
    timeline = report.get("timeline_report", {}) if isinstance(report.get("timeline_report"), dict) else {}
    lines = [
        "# Timeline Overlay Report",
        "",
        f"Generated: `{report.get('generated_at', '')}`",
        f"Payload: `{report.get('payload_path', '')}`",
        "",
        "## Summary",
        "",
        f"- Events: `{summary.get('event_count', 0)}`",
        f"- Dated / undated: `{summary.get('dated_event_count', 0)} / {summary.get('undated_event_count', 0)}`",
        f"- Warnings: `{summary.get('warning_count', 0)}`",
        f"- Same-date groups: `{summary.get('same_date_group_count', 0)}`",
        f"- Date gaps: `{summary.get('date_gap_count', 0)}`",
        "",
        "## Ordered Events",
        "",
        "| Date | Precision | Event | Type | Source |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in timeline.get("ordered_events", []) or []:
        if not isinstance(row, dict):
            continue
        label = str(row.get("label", row.get("id", ""))).replace("|", "/")
        source = str(row.get("source_coords", "")).replace("|", "/")
        event_type = str(row.get("event_type", "")).replace("|", "/")
        lines.append(
            f"| `{row.get('date', '')}` | `{row.get('date_precision', '')}` | "
            f"`{row.get('id', '')}` {label} | {event_type} | `{source}` |"
        )

    undated = timeline.get("undated_events", []) if isinstance(timeline.get("undated_events"), list) else []
    if undated:
        lines.extend(["", "## Undated Events", ""])
        for row in undated:
            if isinstance(row, dict):
                lines.append(f"- `{row.get('id', '')}` {row.get('label', '')}")

    same_date_groups = timeline.get("same_date_groups", []) if isinstance(timeline.get("same_date_groups"), list) else []
    if same_date_groups:
        lines.extend(["", "## Same-Date Groups", ""])
        for row in same_date_groups:
            if isinstance(row, dict):
                lines.append(f"- `{row.get('date_key', '')}`: `{row.get('event_ids', [])}`")

    gaps = timeline.get("date_gaps", []) if isinstance(timeline.get("date_gaps"), list) else []
    if gaps:
        lines.extend(["", "## Date Gaps", ""])
        for row in gaps:
            if isinstance(row, dict):
                lines.append(
                    f"- `{row.get('from_event_id', '')}` -> `{row.get('to_event_id', '')}`: "
                    f"`{row.get('gap_days', 0)}` days"
                )

    warnings = timeline.get("warnings", []) if isinstance(timeline.get("warnings"), list) else []
    if warnings:
        lines.extend(["", "## Warnings", ""])
        for warning in warnings:
            if isinstance(warning, dict):
                lines.append(f"- `{warning.get('kind', 'warning')}` on `{warning.get('event_id', '')}`")

    lines.append("")
    return "\n".join(lines)


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
    return out or "timeline-overlay"


if __name__ == "__main__":
    raise SystemExit(main())
