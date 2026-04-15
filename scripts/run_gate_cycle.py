#!/usr/bin/env python3
"""
Run focused gate cycles:
- run kb_pipeline on a curated scenario batch
- run kb_interrogator on resulting KBs
- emit consolidated metrics report

This is the single command path for the current focus plan.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PIPELINE = ROOT / "kb_pipeline.py"
INTERROGATOR = ROOT / "scripts" / "kb_interrogator.py"
TRACKS = ROOT / "kb_scenarios" / "tracks.json"


def _slug(text: str) -> str:
    out = "".join(ch.lower() if ch.isalnum() else "_" for ch in str(text or "")).strip("_")
    while "__" in out:
        out = out.replace("__", "_")
    return out or "item"


def _now_stamp() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d_%H%M%S")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_track_scenarios(track_id: str) -> list[str]:
    payload = _read_json(TRACKS)
    for row in payload.get("tracks", []):
        if isinstance(row, dict) and str(row.get("id", "")).strip() == track_id:
            scenarios = row.get("scenarios", [])
            if isinstance(scenarios, list):
                return [str(x).strip() for x in scenarios if str(x).strip()]
    raise ValueError(f"Track not found: {track_id}")


def _build_baseline_focus_batch() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    rows.append(
        {
            "id": "goldilocks_roundtrip",
            "scenario_path": ROOT / "kb_scenarios" / "story_goldilocks_roundtrip.json",
            "predicate_registry": ROOT / "modelfiles" / "predicate_registry.goldilocks.json",
            "type_schema": ROOT / "modelfiles" / "type_schema.goldilocks.json",
            "clarification_eagerness": 0.2,
            "max_clarification_rounds": 1,
            "exam_style": "general",
        }
    )
    for name in _load_track_scenarios("excursion_middle_hn_v1"):
        rows.append(
            {
                "id": f"hn_{name}",
                "scenario_path": ROOT / "kb_scenarios" / f"{name}.json",
                "predicate_registry": ROOT / "modelfiles" / "predicate_registry.json",
                "type_schema": None,
                "clarification_eagerness": 0.35,
                "max_clarification_rounds": 2,
                "exam_style": "detective",
            }
        )
    return rows


def _pipeline_cmd(
    *,
    scenario_path: Path,
    run_out: Path,
    kb_name: str,
    backend: str,
    base_url: str,
    model: str,
    prompt_file: Path,
    predicate_registry: Path,
    type_schema: Path | None,
    clarification_eagerness: float,
    max_clarification_rounds: int,
    context_length: int,
) -> list[str]:
    cmd = [
        sys.executable,
        str(PIPELINE),
        "--backend",
        backend,
        "--base-url",
        base_url,
        "--model",
        model,
        "--runtime",
        "core",
        "--scenario",
        str(scenario_path),
        "--kb-name",
        kb_name,
        "--out",
        str(run_out),
        "--prompt-file",
        str(prompt_file),
        "--predicate-registry",
        str(predicate_registry),
        "--strict-registry",
        "--context-length",
        str(int(context_length)),
        "--clarification-eagerness",
        str(float(clarification_eagerness)),
        "--max-clarification-rounds",
        str(int(max_clarification_rounds)),
        "--clarification-answer-model",
        model,
        "--clarification-answer-backend",
        backend,
        "--clarification-answer-base-url",
        base_url,
        "--clarification-answer-context-length",
        str(int(context_length)),
        "--clarification-answer-min-confidence",
        "0.55",
        "--frontend-proposal-mode",
        "off",
    ]
    if isinstance(type_schema, Path):
        cmd.extend(["--type-schema", str(type_schema)])
    return cmd


def _interrogator_cmd(
    *,
    scenario_path: Path,
    candidate_kb: Path,
    out_json: Path,
    out_md: Path,
    backend: str,
    base_url: str,
    model: str,
    exam_style: str,
    context_length: int,
) -> list[str]:
    return [
        sys.executable,
        str(INTERROGATOR),
        "--source-text-file",
        str(scenario_path),
        "--candidate-kb",
        str(candidate_kb),
        "--backend",
        backend,
        "--base-url",
        base_url,
        "--model",
        model,
        "--exam-style",
        exam_style,
        "--context-length",
        str(int(context_length)),
        "--exam-question-count",
        "10",
        "--exam-min-temporal-questions",
        "1",
        "--out-json",
        str(out_json),
        "--out-md",
        str(out_md),
    ]


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run focused pipeline+interrogator baseline cycles.")
    p.add_argument("--batch", choices=["baseline_focus"], default="baseline_focus")
    p.add_argument("--backend", default="ollama")
    p.add_argument("--base-url", default="http://127.0.0.1:11434")
    p.add_argument("--model", default="qwen3.5:9b")
    p.add_argument("--prompt-file", default=str(ROOT / "modelfiles" / "semantic_parser_system_prompt.md"))
    p.add_argument("--context-length", type=int, default=8192)
    p.add_argument("--out-dir", default=str(ROOT / "tmp" / "runs" / "focus_cycles"))
    p.add_argument("--name", default="")
    return p.parse_args()


def main() -> int:
    args = _parse_args()

    out_root = Path(args.out_dir).resolve()
    out_root.mkdir(parents=True, exist_ok=True)
    stamp = _now_stamp()
    run_name = _slug(args.name) if str(args.name).strip() else f"{args.batch}_{stamp}"
    run_dir = out_root / run_name
    run_dir.mkdir(parents=True, exist_ok=True)

    prompt_file = Path(args.prompt_file).resolve()
    if not prompt_file.exists():
        print(f"Prompt file not found: {prompt_file}")
        return 2

    if args.batch == "baseline_focus":
        scenarios = _build_baseline_focus_batch()
    else:
        print(f"Unsupported batch: {args.batch}")
        return 2

    rows: list[dict[str, Any]] = []

    for idx, item in enumerate(scenarios, start=1):
        scenario_path = Path(item["scenario_path"]).resolve()
        scenario_id = str(item.get("id") or scenario_path.stem)
        if not scenario_path.exists():
            rows.append(
                {
                    "scenario_id": scenario_id,
                    "scenario_path": str(scenario_path),
                    "status": "missing_scenario",
                }
            )
            print(f"[{idx:02d}/{len(scenarios)}] missing scenario: {scenario_path}")
            continue

        scenario_slug = _slug(scenario_path.stem)
        pipeline_out = run_dir / f"{scenario_slug}.pipeline.json"
        interrogator_out = run_dir / f"{scenario_slug}.interrogator.json"
        interrogator_md = run_dir / f"{scenario_slug}.interrogator.md"

        kb_name = f"{_slug(run_name)}_{scenario_slug}"
        cmd = _pipeline_cmd(
            scenario_path=scenario_path,
            run_out=pipeline_out,
            kb_name=kb_name,
            backend=args.backend,
            base_url=args.base_url,
            model=args.model,
            prompt_file=prompt_file,
            predicate_registry=Path(item["predicate_registry"]).resolve(),
            type_schema=Path(item["type_schema"]).resolve() if item.get("type_schema") else None,
            clarification_eagerness=float(item.get("clarification_eagerness", 0.35)),
            max_clarification_rounds=int(item.get("max_clarification_rounds", 2)),
            context_length=int(args.context_length),
        )
        print(f"[{idx:02d}/{len(scenarios)}] pipeline: {scenario_path.stem}")
        proc_pipe = subprocess.run(cmd, cwd=str(ROOT), check=False)

        row: dict[str, Any] = {
            "scenario_id": scenario_id,
            "scenario_path": str(scenario_path),
            "pipeline_output": str(pipeline_out),
            "pipeline_exit_code": int(proc_pipe.returncode),
        }

        if not pipeline_out.exists():
            row["status"] = "pipeline_output_missing"
            rows.append(row)
            continue

        pipe_report = _read_json(pipeline_out)
        row["pipeline_overall_status"] = str(pipe_report.get("overall_status", "failed"))
        row["validation_passed"] = int(pipe_report.get("validation_passed", 0) or 0)
        row["validation_total"] = int(pipe_report.get("validation_total", 0) or 0)
        row["turn_parse_failures"] = int(pipe_report.get("turn_parse_failures", 0) or 0)
        row["turn_apply_failures"] = int(pipe_report.get("turn_apply_failures", 0) or 0)

        kb_namespace = pipe_report.get("kb_namespace", {})
        candidate_kb = Path(str(kb_namespace.get("corpus_path", "")).strip()).resolve() if isinstance(kb_namespace, dict) else None
        if not candidate_kb or not candidate_kb.exists():
            row["status"] = "kb_missing_after_pipeline"
            rows.append(row)
            continue

        cmd_int = _interrogator_cmd(
            scenario_path=scenario_path,
            candidate_kb=candidate_kb,
            out_json=interrogator_out,
            out_md=interrogator_md,
            backend=args.backend,
            base_url=args.base_url,
            model=args.model,
            exam_style=str(item.get("exam_style", "general")),
            context_length=int(args.context_length),
        )
        print(f"[{idx:02d}/{len(scenarios)}] interrogator: {scenario_path.stem}")
        proc_int = subprocess.run(cmd_int, cwd=str(ROOT), check=False)

        row["interrogator_output"] = str(interrogator_out)
        row["interrogator_exit_code"] = int(proc_int.returncode)

        if interrogator_out.exists():
            int_report = _read_json(interrogator_out)
            fact_audit = int_report.get("fact_audit", {}) if isinstance(int_report, dict) else {}
            exam = int_report.get("exam", {}) if isinstance(int_report, dict) else {}
            row["audit_coverage_score"] = float(fact_audit.get("coverage_score", 0.0) or 0.0)
            row["audit_precision_score"] = float(fact_audit.get("precision_score", 0.0) or 0.0)
            row["exam_pass_rate"] = float(exam.get("pass_rate", 0.0) or 0.0)
            row["exam_temporal_pass_rate"] = float(exam.get("temporal_pass_rate", 0.0) or 0.0)
            row["status"] = "ok"
        else:
            row["status"] = "interrogator_output_missing"

        rows.append(row)

    ok_rows = [r for r in rows if r.get("status") == "ok"]
    pipeline_pass_rows = [r for r in rows if str(r.get("pipeline_overall_status", "")).lower() == "passed"]

    def _avg(key: str) -> float:
        vals = [float(r.get(key, 0.0) or 0.0) for r in ok_rows]
        return (sum(vals) / len(vals)) if vals else 0.0

    summary = {
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "batch": args.batch,
        "run_name": run_name,
        "settings": {
            "backend": args.backend,
            "base_url": args.base_url,
            "model": args.model,
            "prompt_file": str(prompt_file),
            "context_length": int(args.context_length),
        },
        "scenario_count": len(scenarios),
        "rows_count": len(rows),
        "pipeline_pass_count": len(pipeline_pass_rows),
        "pipeline_pass_rate": round((len(pipeline_pass_rows) / len(rows)) if rows else 0.0, 6),
        "interrogator_ok_count": len(ok_rows),
        "avg_audit_coverage": round(_avg("audit_coverage_score"), 6),
        "avg_audit_precision": round(_avg("audit_precision_score"), 6),
        "avg_exam_pass_rate": round(_avg("exam_pass_rate"), 6),
        "avg_exam_temporal_pass_rate": round(_avg("exam_temporal_pass_rate"), 6),
        "rows": rows,
    }

    summary_json = run_dir / "summary.json"
    summary_md = run_dir / "summary.md"
    summary_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    md_lines = [
        "# Focus Cycle Summary",
        "",
        f"- Batch: `{args.batch}`",
        f"- Run name: `{run_name}`",
        f"- Scenarios: `{len(scenarios)}`",
        f"- Pipeline pass rate: `{summary['pipeline_pass_rate']}`",
        f"- Interrogator OK: `{len(ok_rows)}`",
        f"- Avg coverage: `{summary['avg_audit_coverage']}`",
        f"- Avg precision: `{summary['avg_audit_precision']}`",
        f"- Avg exam pass: `{summary['avg_exam_pass_rate']}`",
        f"- Avg temporal exam pass: `{summary['avg_exam_temporal_pass_rate']}`",
        "",
        "| Scenario | Pipeline | Coverage | Precision | Exam Pass | Status |",
        "|---|---|---:|---:|---:|---|",
    ]
    for row in rows:
        md_lines.append(
            "| "
            + f"`{row.get('scenario_id', '')}` | "
            + f"`{row.get('pipeline_overall_status', row.get('pipeline_exit_code', 'n/a'))}` | "
            + f"{float(row.get('audit_coverage_score', 0.0) or 0.0):.3f} | "
            + f"{float(row.get('audit_precision_score', 0.0) or 0.0):.3f} | "
            + f"{float(row.get('exam_pass_rate', 0.0) or 0.0):.3f} | "
            + f"`{row.get('status', '')}` |"
        )
    summary_md.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    print(
        "Focus cycle summary: "
        f"pipeline_pass={summary['pipeline_pass_count']}/{len(rows)} "
        f"interrogator_ok={len(ok_rows)}/{len(rows)} "
        f"coverage={summary['avg_audit_coverage']:.3f} "
        f"precision={summary['avg_audit_precision']:.3f} "
        f"exam={summary['avg_exam_pass_rate']:.3f}"
    )
    print(f"Summary JSON: {summary_json}")
    print(f"Summary MD: {summary_md}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
