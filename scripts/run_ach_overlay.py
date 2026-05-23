#!/usr/bin/env python3
"""Run a deterministic ACH overlay payload and write harness-style artifacts."""

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

from src.ach_overlay import analyze_ach_overlay  # noqa: E402


DEFAULT_OUT_DIR = REPO_ROOT / "tmp" / "ach_overlay_runs"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--payload", type=Path, required=True, help="ACH overlay payload JSON.")
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
    out_json = _resolve(args.out_json) if args.out_json else out_dir / f"{slug}_ach_report.json"
    out_md = _resolve(args.out_md) if args.out_md else out_dir / f"{slug}_ach_report.md"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    out_md.write_text(render_markdown(report), encoding="utf-8")
    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")
    print(json.dumps(report["summary"], sort_keys=True))
    return 0


def build_report(*, payload: dict[str, Any], payload_path: Path | None = None) -> dict[str, Any]:
    ach_report = analyze_ach_overlay(payload)
    top = [
        item["hypothesis_id"]
        for item in ach_report.get("hypothesis_scores", [])
        if isinstance(item, dict) and item.get("rank") == 1
    ]
    warnings = ach_report.get("warnings", []) if isinstance(ach_report.get("warnings"), list) else []
    return {
        "schema_version": "ach_overlay_run_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "payload_path": _display_path(payload_path) if payload_path else "",
        "policy": [
            "Runs only the deterministic ACH scorer over a populated matrix payload.",
            "Does not compile documents, query an LLM, mutate KB state, or write durable facts.",
            "Ranks hypotheses by least disconfirming evidence, not by largest support pile.",
        ],
        "summary": {
            "matrix_complete": bool(ach_report.get("matrix_complete")),
            "hypothesis_count": int(ach_report.get("hypothesis_count", 0) or 0),
            "evidence_count": int(ach_report.get("evidence_count", 0) or 0),
            "judgment_count": int(ach_report.get("judgment_count", 0) or 0),
            "warning_count": len(warnings),
            "top_hypotheses": top,
            "surviving_hypothesis_count": len(ach_report.get("surviving_hypotheses", []) or []),
            "sensitivity_count": len(ach_report.get("sensitivity", []) or []),
        },
        "ach_report": ach_report,
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report.get("summary", {}) if isinstance(report.get("summary"), dict) else {}
    ach_report = report.get("ach_report", {}) if isinstance(report.get("ach_report"), dict) else {}
    lines = [
        "# ACH Overlay Report",
        "",
        f"Generated: {report.get('generated_at', '')}",
        f"Payload: `{report.get('payload_path', '')}`",
        "",
        "## Summary",
        "",
        f"- Matrix complete: `{summary.get('matrix_complete', False)}`",
        f"- Hypotheses: `{summary.get('hypothesis_count', 0)}`",
        f"- Evidence rows: `{summary.get('evidence_count', 0)}`",
        f"- Judgments: `{summary.get('judgment_count', 0)}`",
        f"- Warnings: `{summary.get('warning_count', 0)}`",
        f"- Top hypotheses: `{summary.get('top_hypotheses', [])}`",
        f"- Sensitivity rows: `{summary.get('sensitivity_count', 0)}`",
        "",
        "## Hypothesis Scores",
        "",
        "| Rank | Hypothesis | Inconsistency | Consistency | Missing |",
        "| ---: | --- | ---: | ---: | ---: |",
    ]
    for row in ach_report.get("hypothesis_scores", []) or []:
        if not isinstance(row, dict):
            continue
        label = str(row.get("label", row.get("hypothesis_id", ""))).replace("|", "/")
        lines.append(
            f"| {row.get('rank', '')} | `{row.get('hypothesis_id', '')}` {label} | "
            f"{row.get('inconsistency_weight', 0)} | {row.get('consistency_weight', 0)} | "
            f"{row.get('missing_judgment_count', 0)} |"
        )

    lines.extend(
        [
            "",
            "## Diagnostic Evidence",
            "",
            "| Evidence | Weight | Score | Spread |",
            "| --- | ---: | ---: | --- |",
        ]
    )
    for row in ach_report.get("diagnostic_evidence", []) or []:
        if not isinstance(row, dict):
            continue
        label = str(row.get("label", row.get("evidence_id", ""))).replace("|", "/")
        lines.append(
            f"| `{row.get('evidence_id', '')}` {label} | {row.get('weight', 0)} | "
            f"{row.get('diagnostic_score', 0)} | `{row.get('assessment_spread', [])}` |"
        )

    sensitivity = ach_report.get("sensitivity", []) if isinstance(ach_report.get("sensitivity"), list) else []
    if sensitivity:
        lines.extend(["", "## Sensitivity", "", "| Evidence | Baseline Top | Top Without Evidence |", "| --- | --- | --- |"])
        for row in sensitivity:
            if not isinstance(row, dict):
                continue
            label = str(row.get("label", row.get("evidence_id", ""))).replace("|", "/")
            lines.append(
                f"| `{row.get('evidence_id', '')}` {label} | `{row.get('baseline_top', [])}` | "
                f"`{row.get('top_without_evidence', [])}` |"
            )

    warnings = ach_report.get("warnings", []) if isinstance(ach_report.get("warnings"), list) else []
    if warnings:
        lines.extend(["", "## Warnings", ""])
        for warning in warnings:
            if isinstance(warning, dict):
                lines.append(f"- `{warning.get('kind', 'warning')}`")
            else:
                lines.append(f"- `{warning}`")

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
    return out or "ach-overlay"


if __name__ == "__main__":
    raise SystemExit(main())
