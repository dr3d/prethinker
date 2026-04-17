#!/usr/bin/env python3
"""
Build a frozen baseline scorecard from latest story-pack summaries.

Outputs:
1) machine summary json in tmp/
2) human markdown report in docs/reports/
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


DEFAULT_PACKS = [
    "mid_pack",
    "upper_mid_pack",
    "mid_noisy_pack",
    "upper_mid_noisy_pack",
    "mid_multilingual_pack",
    "upper_mid_multilingual_pack",
    "mid_structured_pack",
]

STRUCTURED_PACKS = {
    "mid_pack",
    "upper_mid_pack",
    "mid_noisy_pack",
    "upper_mid_noisy_pack",
}

WILD_PACKS = {
    "mid_multilingual_pack",
    "upper_mid_multilingual_pack",
    "mid_structured_pack",
}


def _utc_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _pack_row(pack_name: str) -> dict[str, Any]:
    stress_path = ROOT / "tmp" / f"{pack_name}_stress.summary.json"
    progressive_path = ROOT / "tmp" / f"{pack_name}_progressive.summary.json"
    stress = _load_json(stress_path)
    progressive = _load_json(progressive_path)

    run_count = int(stress.get("run_count", 0) or 0)
    pipeline_pass = int(stress.get("pipeline_pass_count", 0) or 0)
    stages = progressive.get("stages", [])
    gate_total = len(stages) if isinstance(stages, list) else 0
    gate_pass = 0
    if isinstance(stages, list):
        for stage in stages:
            if not isinstance(stage, dict):
                continue
            if bool(stage.get("hard_gate_pass", False)) or bool(stage.get("gate_passed", False)):
                gate_pass += 1

    return {
        "pack_name": pack_name,
        "stress_summary_path": str(stress_path),
        "progressive_summary_path": str(progressive_path),
        "stress_present": bool(stress),
        "progressive_present": bool(progressive),
        "stress_run_count": run_count,
        "stress_pipeline_pass_count": pipeline_pass,
        "stress_pipeline_pass_rate": (float(pipeline_pass) / float(run_count)) if run_count else 0.0,
        "stress_avg_coverage": float(stress.get("avg_coverage", 0.0) or 0.0),
        "stress_avg_precision": float(stress.get("avg_precision", 0.0) or 0.0),
        "stress_avg_exam_pass_rate": float(stress.get("avg_exam_pass_rate", 0.0) or 0.0),
        "progressive_gate_pass_count": gate_pass,
        "progressive_gate_total": gate_total,
        "progressive_gate_pass_rate": (float(gate_pass) / float(gate_total)) if gate_total else 0.0,
        "progressive_avg_coverage": float(progressive.get("avg_coverage", 0.0) or 0.0),
        "progressive_avg_precision": float(progressive.get("avg_precision", 0.0) or 0.0),
        "progressive_avg_exam_pass_rate": float(progressive.get("avg_exam_pass_rate", 0.0) or 0.0),
        "stress_generated_at_utc": stress.get("generated_at_utc", ""),
        "progressive_generated_at_utc": progressive.get("generated_at_utc", ""),
    }


def _aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {
            "pack_count": 0,
            "avg_stress_pipeline_pass_rate": 0.0,
            "avg_stress_coverage": 0.0,
            "avg_stress_precision": 0.0,
            "avg_stress_exam": 0.0,
            "avg_progressive_gate_pass_rate": 0.0,
            "avg_progressive_coverage": 0.0,
            "avg_progressive_precision": 0.0,
            "avg_progressive_exam": 0.0,
        }

    def _avg(key: str) -> float:
        return sum(float(r.get(key, 0.0) or 0.0) for r in rows) / float(len(rows))

    return {
        "pack_count": len(rows),
        "avg_stress_pipeline_pass_rate": round(_avg("stress_pipeline_pass_rate"), 6),
        "avg_stress_coverage": round(_avg("stress_avg_coverage"), 6),
        "avg_stress_precision": round(_avg("stress_avg_precision"), 6),
        "avg_stress_exam": round(_avg("stress_avg_exam_pass_rate"), 6),
        "avg_progressive_gate_pass_rate": round(_avg("progressive_gate_pass_rate"), 6),
        "avg_progressive_coverage": round(_avg("progressive_avg_coverage"), 6),
        "avg_progressive_precision": round(_avg("progressive_avg_precision"), 6),
        "avg_progressive_exam": round(_avg("progressive_avg_exam_pass_rate"), 6),
    }


def _render_markdown(summary: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Baseline Reset (Frozen)")
    lines.append("")
    lines.append(f"- Generated UTC: `{summary.get('generated_at_utc', '')}`")
    lines.append(f"- Model baseline: `{summary.get('settings', {}).get('model', '')}`")
    lines.append(f"- Source: latest `tmp/*_stress.summary.json` + `tmp/*_progressive.summary.json`")
    lines.append("")
    lines.append("## Lane Aggregates")
    lines.append("")
    for lane_key, lane_title in [
        ("structured_lane", "Structured Lane"),
        ("wild_lane", "Wild/Bridge Lane"),
        ("overall", "Overall"),
    ]:
        lane = summary.get(lane_key, {})
        if not isinstance(lane, dict):
            continue
        lines.append(f"### {lane_title}")
        lines.append("")
        lines.append(f"- Pack count: `{lane.get('pack_count', 0)}`")
        lines.append(f"- Stress pipeline pass rate (avg): `{lane.get('avg_stress_pipeline_pass_rate', 0.0):.3f}`")
        lines.append(f"- Stress coverage (avg): `{lane.get('avg_stress_coverage', 0.0):.3f}`")
        lines.append(f"- Stress precision (avg): `{lane.get('avg_stress_precision', 0.0):.3f}`")
        lines.append(f"- Stress exam pass (avg): `{lane.get('avg_stress_exam', 0.0):.3f}`")
        lines.append(f"- Progressive gate pass (avg): `{lane.get('avg_progressive_gate_pass_rate', 0.0):.3f}`")
        lines.append(f"- Progressive coverage (avg): `{lane.get('avg_progressive_coverage', 0.0):.3f}`")
        lines.append(f"- Progressive precision (avg): `{lane.get('avg_progressive_precision', 0.0):.3f}`")
        lines.append(f"- Progressive exam pass (avg): `{lane.get('avg_progressive_exam', 0.0):.3f}`")
        lines.append("")

    lines.append("## Pack Scorecard")
    lines.append("")
    lines.append("| Pack | Stress Pass | Stress Cov | Stress Prec | Stress Exam | Progressive Gates | Progressive Cov | Progressive Prec | Progressive Exam |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for row in summary.get("packs", []):
        if not isinstance(row, dict):
            continue
        lines.append(
            "| "
            f"`{row.get('pack_name','')}` | "
            f"{float(row.get('stress_pipeline_pass_rate', 0.0)):.3f} | "
            f"{float(row.get('stress_avg_coverage', 0.0)):.3f} | "
            f"{float(row.get('stress_avg_precision', 0.0)):.3f} | "
            f"{float(row.get('stress_avg_exam_pass_rate', 0.0)):.3f} | "
            f"{int(row.get('progressive_gate_pass_count', 0))}/{int(row.get('progressive_gate_total', 0))} | "
            f"{float(row.get('progressive_avg_coverage', 0.0)):.3f} | "
            f"{float(row.get('progressive_avg_precision', 0.0)):.3f} | "
            f"{float(row.get('progressive_avg_exam_pass_rate', 0.0)):.3f} |"
        )
    lines.append("")
    lines.append("## Guardrail Policy")
    lines.append("")
    lines.append("- New experiments must not reduce structured-lane stress pipeline pass rate.")
    lines.append("- New experiments must not reduce structured-lane progressive gate pass rate.")
    lines.append("- Wild-lane changes are allowed to iterate if structured lane stays stable.")
    lines.append("- Any non-net-positive branch is parked with a report, not merged silently.")
    lines.append("")
    return "\n".join(lines).strip() + "\n"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build frozen baseline scorecard from latest summary artifacts.")
    p.add_argument("--packs", default=",".join(DEFAULT_PACKS))
    p.add_argument("--model", default="qwen3.5:9b")
    p.add_argument("--summary-json", default="tmp/baseline_reset_2026-04-16.summary.json")
    p.add_argument("--report-md", default="docs/reports/BASELINE_RESET_2026-04-16.md")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    pack_names = [x.strip() for x in str(args.packs).split(",") if x.strip()]
    rows = [_pack_row(name) for name in pack_names]
    structured_rows = [r for r in rows if str(r.get("pack_name")) in STRUCTURED_PACKS]
    wild_rows = [r for r in rows if str(r.get("pack_name")) in WILD_PACKS]

    summary = {
        "generated_at_utc": _utc_iso(),
        "settings": {
            "model": str(args.model),
            "pack_names": pack_names,
        },
        "packs": rows,
        "structured_lane": _aggregate(structured_rows),
        "wild_lane": _aggregate(wild_rows),
        "overall": _aggregate(rows),
    }

    summary_json = Path(str(args.summary_json))
    if not summary_json.is_absolute():
        summary_json = (ROOT / summary_json).resolve()
    summary_json.parent.mkdir(parents=True, exist_ok=True)
    summary_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report_md = Path(str(args.report_md))
    if not report_md.is_absolute():
        report_md = (ROOT / report_md).resolve()
    report_md.parent.mkdir(parents=True, exist_ok=True)
    report_md.write_text(_render_markdown(summary), encoding="utf-8")

    print(f"[baseline-reset] summary_json={summary_json}")
    print(f"[baseline-reset] report_md={report_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

