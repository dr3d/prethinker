#!/usr/bin/env python3
"""
Run named scenario tracks from kb_scenarios/tracks.json.

This keeps ladder gating separate from examples/demos while still making
non-ladder packs easy to run in repeatable grunt-work loops.
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
DEFAULT_MANIFEST = ROOT / "kb_scenarios" / "tracks.json"
DEFAULT_SCENARIOS_DIR = ROOT / "kb_scenarios"
DEFAULT_OUT_DIR = ROOT / "tmp" / "runs" / "tracks"
PIPELINE = ROOT / "kb_pipeline.py"


def _load_manifest(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("tracks"), list):
        raise ValueError(f"Invalid tracks manifest shape: {path}")
    return payload


def _find_track(payload: dict[str, Any], track_id: str) -> dict[str, Any]:
    for track in payload.get("tracks", []):
        if isinstance(track, dict) and track.get("id") == track_id:
            return track
    raise ValueError(f"Track not found: {track_id}")


def _slug(text: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in text).strip("_")


def _scenario_path(name: str, scenarios_dir: Path) -> Path:
    if name.endswith(".json"):
        return scenarios_dir / name
    return scenarios_dir / f"{name}.json"


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run a named scenario track.")
    p.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    p.add_argument("--list-tracks", action="store_true")
    p.add_argument("--track", default="")
    p.add_argument("--scenarios-dir", default=str(DEFAULT_SCENARIOS_DIR))
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    p.add_argument("--summary-out", default="")
    p.add_argument("--backend", default="ollama")
    p.add_argument("--base-url", default="http://127.0.0.1:11434")
    p.add_argument(
        "--model",
        default="qwen3.5:9b",
        help=(
            "Parser model id. Default is bare qwen3.5:9b so runtime --prompt-file "
            "remains the single system-prompt source."
        ),
    )
    p.add_argument("--runtime", default="core")
    p.add_argument("--kb-root", default="")
    p.add_argument("--prompt-file", default="")
    p.add_argument("--kb-name-prefix", default="")
    p.add_argument("--context-length", type=int, default=0)
    p.add_argument("--clarification-eagerness", type=float, default=-1.0)
    p.add_argument("--max-clarification-rounds", type=int, default=-1)
    p.add_argument("--require-final-confirmation", action="store_true")
    p.add_argument("--clarification-answer-model", default="")
    p.add_argument("--clarification-answer-backend", default="")
    p.add_argument("--clarification-answer-base-url", default="")
    p.add_argument("--clarification-answer-context-length", type=int, default=0)
    p.add_argument("--clarification-answer-min-confidence", type=float, default=-1.0)
    p.add_argument("--clarification-answer-history-turns", type=int, default=-1)
    p.add_argument("--clarification-answer-kb-clause-limit", type=int, default=-1)
    p.add_argument("--clarification-answer-kb-char-budget", type=int, default=-1)
    p.add_argument("--served-llm-model", default="")
    p.add_argument("--served-llm-backend", default="")
    p.add_argument("--served-llm-base-url", default="")
    p.add_argument("--served-llm-context-length", type=int, default=0)
    p.add_argument("--fail-on-under", action="store_true", help="Exit non-zero when pass rate is below track required_pass_rate.")
    return p.parse_args()


def _print_tracks(payload: dict[str, Any]) -> None:
    for track in payload.get("tracks", []):
        tid = str(track.get("id", "")).strip()
        desc = str(track.get("description", "")).strip()
        scenarios = track.get("scenarios", [])
        target = track.get("required_pass_rate")
        print(f"- {tid} ({len(scenarios)} scenarios, target={target})")
        if desc:
            print(f"  {desc}")


def main() -> int:
    args = _parse_args()
    manifest_path = Path(args.manifest).resolve()
    scenarios_dir = Path(args.scenarios_dir).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    payload = _load_manifest(manifest_path)
    if args.list_tracks:
        _print_tracks(payload)
        return 0

    if not args.track:
        raise SystemExit("--track is required unless --list-tracks is used.")

    track = _find_track(payload, args.track)
    scenarios = track.get("scenarios", [])
    if not isinstance(scenarios, list) or not scenarios:
        raise SystemExit(f"Track has no scenarios: {args.track}")

    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d_%H%M%S")
    records: list[dict[str, Any]] = []
    passed_runs = 0

    for idx, scenario_name in enumerate(scenarios, start=1):
        scenario_name = str(scenario_name).strip()
        scenario_path = _scenario_path(scenario_name, scenarios_dir)
        if not scenario_path.exists():
            records.append(
                {
                    "scenario": scenario_name,
                    "scenario_path": str(scenario_path),
                    "status": "missing_scenario",
                    "overall_status": "failed",
                }
            )
            print(f"[{idx:02d}/{len(scenarios)}] missing scenario: {scenario_path}")
            continue

        kb_name = f"{_slug(args.kb_name_prefix)}_{_slug(scenario_name)}" if args.kb_name_prefix else _slug(scenario_name)
        run_out = out_dir / f"{_slug(scenario_name)}_{_slug(args.track)}_{stamp}.json"

        cmd = [
            sys.executable,
            str(PIPELINE),
            "--backend",
            args.backend,
            "--base-url",
            args.base_url,
            "--model",
            args.model,
            "--runtime",
            args.runtime,
            "--scenario",
            str(scenario_path),
            "--kb-name",
            kb_name,
            "--out",
            str(run_out),
        ]
        if args.prompt_file:
            cmd.extend(["--prompt-file", args.prompt_file])
        if args.kb_root:
            cmd.extend(["--kb-root", args.kb_root])
        if args.context_length > 0:
            cmd.extend(["--context-length", str(args.context_length)])
        if args.clarification_eagerness >= 0.0:
            cmd.extend(["--clarification-eagerness", str(args.clarification_eagerness)])
        if args.max_clarification_rounds >= 0:
            cmd.extend(["--max-clarification-rounds", str(args.max_clarification_rounds)])
        if args.require_final_confirmation:
            cmd.append("--require-final-confirmation")
        if args.clarification_answer_model:
            cmd.extend(["--clarification-answer-model", args.clarification_answer_model])
        if args.clarification_answer_backend:
            cmd.extend(["--clarification-answer-backend", args.clarification_answer_backend])
        if args.clarification_answer_base_url:
            cmd.extend(["--clarification-answer-base-url", args.clarification_answer_base_url])
        if args.clarification_answer_context_length > 0:
            cmd.extend(["--clarification-answer-context-length", str(args.clarification_answer_context_length)])
        if args.clarification_answer_min_confidence >= 0.0:
            cmd.extend(["--clarification-answer-min-confidence", str(args.clarification_answer_min_confidence)])
        if args.clarification_answer_history_turns >= 0:
            cmd.extend(["--clarification-answer-history-turns", str(args.clarification_answer_history_turns)])
        if args.clarification_answer_kb_clause_limit >= 0:
            cmd.extend(["--clarification-answer-kb-clause-limit", str(args.clarification_answer_kb_clause_limit)])
        if args.clarification_answer_kb_char_budget >= 0:
            cmd.extend(["--clarification-answer-kb-char-budget", str(args.clarification_answer_kb_char_budget)])
        if args.served_llm_model:
            cmd.extend(["--served-llm-model", args.served_llm_model])
        if args.served_llm_backend:
            cmd.extend(["--served-llm-backend", args.served_llm_backend])
        if args.served_llm_base_url:
            cmd.extend(["--served-llm-base-url", args.served_llm_base_url])
        if args.served_llm_context_length > 0:
            cmd.extend(["--served-llm-context-length", str(args.served_llm_context_length)])

        print(f"[{idx:02d}/{len(scenarios)}] running {scenario_name}")
        proc = subprocess.run(cmd, cwd=str(ROOT), check=False)

        if not run_out.exists():
            records.append(
                {
                    "scenario": scenario_name,
                    "scenario_path": str(scenario_path),
                    "status": "run_missing_output",
                    "exit_code": proc.returncode,
                    "overall_status": "failed",
                }
            )
            continue

        report = json.loads(run_out.read_text(encoding="utf-8"))
        overall_status = str(report.get("overall_status", "failed"))
        passed = overall_status == "passed"
        if passed:
            passed_runs += 1
        records.append(
            {
                "scenario": scenario_name,
                "scenario_path": str(scenario_path),
                "run_output": str(run_out),
                "overall_status": overall_status,
                "validation_passed": int(report.get("validation_passed", 0)),
                "validation_total": int(report.get("validation_total", 0)),
                "turns_total": int(report.get("turns_total", 0)),
                "turn_apply_failures": int(report.get("turn_apply_failures", 0)),
                "turn_parse_failures": int(report.get("turn_parse_failures", 0)),
                "exit_code": proc.returncode,
            }
        )

    total = len(scenarios)
    pass_rate = (passed_runs / total) if total else 0.0
    required = float(track.get("required_pass_rate", 1.0))
    meets_target = pass_rate >= required

    summary = {
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "manifest_path": str(manifest_path),
        "track_id": args.track,
        "track_description": track.get("description", ""),
        "required_pass_rate": required,
        "runs_total": total,
        "runs_passed": passed_runs,
        "run_pass_rate": round(pass_rate, 4),
        "meets_target": meets_target,
        "settings": {
            "backend": args.backend,
            "base_url": args.base_url,
            "model": args.model,
            "runtime": args.runtime,
            "kb_root": args.kb_root,
            "prompt_file": args.prompt_file,
            "context_length": args.context_length,
            "clarification_eagerness": args.clarification_eagerness,
            "max_clarification_rounds": args.max_clarification_rounds,
            "require_final_confirmation": bool(args.require_final_confirmation),
            "clarification_answer_model": args.clarification_answer_model,
            "clarification_answer_backend": args.clarification_answer_backend,
            "clarification_answer_base_url": args.clarification_answer_base_url,
            "clarification_answer_context_length": args.clarification_answer_context_length,
            "clarification_answer_min_confidence": args.clarification_answer_min_confidence,
            "clarification_answer_history_turns": args.clarification_answer_history_turns,
            "clarification_answer_kb_clause_limit": args.clarification_answer_kb_clause_limit,
            "clarification_answer_kb_char_budget": args.clarification_answer_kb_char_budget,
            "served_llm_model": args.served_llm_model,
            "served_llm_backend": args.served_llm_backend,
            "served_llm_base_url": args.served_llm_base_url,
            "served_llm_context_length": args.served_llm_context_length,
        },
        "records": records,
    }

    summary_out = Path(args.summary_out).resolve() if args.summary_out else (out_dir / f"track_{_slug(args.track)}_summary_{stamp}.json")
    summary_out.parent.mkdir(parents=True, exist_ok=True)
    summary_out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(
        f"Track {args.track}: passed={passed_runs}/{total} "
        f"({pass_rate*100:.1f}%) target={required*100:.1f}% "
        f"meets_target={meets_target}"
    )
    print(f"Summary: {summary_out}")

    if args.fail_on_under and not meets_target:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
