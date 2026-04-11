#!/usr/bin/env python3
"""
Run a clarification-tuning cadence over selected scenarios.

Purpose:
- keep parser model fixed (e.g., qwen3.5:9b)
- keep clarification responder fixed (e.g., gpt-oss:20b)
- sweep CE and clarification confidence thresholds
- report which setting mix gives best pass + stable clarification behavior
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCENARIO_PACK = [
    "kb_scenarios/rung_140_ce_pronoun_typo_missing_qmark.json",
    "kb_scenarios/rung_150_ce_typo_uncertainty_chain.json",
    "kb_scenarios/rung_160_ce_soft_retract_noise.json",
    "kb_scenarios/rung_170_ce_pronoun_followup_no_qmark.json",
]


@dataclass(frozen=True)
class CadenceSetting:
    ce: float
    min_conf: float

    @property
    def key(self) -> str:
        return f"ce_{self.ce:.2f}__mc_{self.min_conf:.2f}"


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _parse_float_list(raw: str) -> list[float]:
    values: list[float] = []
    for piece in raw.split(","):
        text = piece.strip()
        if not text:
            continue
        values.append(float(text))
    return values


def _load_report(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _synthetic_rounds_used(report: dict[str, Any]) -> int:
    turns = report.get("turns", [])
    if not isinstance(turns, list):
        return 0
    count = 0
    for turn in turns:
        if not isinstance(turn, dict):
            continue
        rounds = turn.get("clarification_rounds", [])
        if not isinstance(rounds, list):
            continue
        for row in rounds:
            if not isinstance(row, dict):
                continue
            source = str(row.get("answer_source", "")).strip().lower()
            if source.startswith("synthetic"):
                count += 1
    return count


def _run_one(
    *,
    scenario: Path,
    setting: CadenceSetting,
    args: argparse.Namespace,
    out_path: Path,
) -> tuple[int, list[str]]:
    cmd = [
        sys.executable,
        str(ROOT / "kb_pipeline.py"),
        "--scenario",
        str(scenario),
        "--backend",
        args.backend,
        "--base-url",
        args.base_url,
        "--model",
        args.model,
        "--runtime",
        args.runtime,
        "--kb-root",
        args.kb_root,
        "--kb-name",
        f"{args.kb_name_prefix}_{scenario.stem}_{setting.key}",
        "--force-empty-kb",
        "--prompt-file",
        args.prompt_file,
        "--context-length",
        str(args.context_length),
        "--timeout-seconds",
        str(args.timeout_seconds),
        "--clarification-eagerness",
        f"{setting.ce:.4f}",
        "--max-clarification-rounds",
        str(args.max_clarification_rounds),
        "--clarification-answer-model",
        args.clarification_answer_model,
        "--clarification-answer-backend",
        args.clarification_answer_backend,
        "--clarification-answer-base-url",
        args.clarification_answer_base_url,
        "--clarification-answer-context-length",
        str(args.clarification_answer_context_length),
        "--clarification-answer-history-turns",
        str(args.clarification_answer_history_turns),
        "--clarification-answer-kb-clause-limit",
        str(args.clarification_answer_kb_clause_limit),
        "--clarification-answer-kb-char-budget",
        str(args.clarification_answer_kb_char_budget),
        "--clarification-answer-min-confidence",
        f"{setting.min_conf:.4f}",
        "--out",
        str(out_path),
    ]
    if args.env_file:
        cmd.extend(["--env-file", args.env_file])
    if args.require_final_confirmation:
        cmd.append("--require-final-confirmation")
    if args.strict_registry:
        cmd.extend(["--predicate-registry", args.predicate_registry, "--strict-registry"])
    if args.type_schema:
        cmd.extend(["--type-schema", args.type_schema])
    if args.strict_types:
        cmd.append("--strict-types")

    proc = subprocess.run(
        cmd,
        cwd=ROOT,
        timeout=max(30, int(args.scenario_timeout_seconds)),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    tail_lines = []
    stdout = proc.stdout or ""
    for line in stdout.strip().splitlines()[-8:]:
        tail_lines.append(line.rstrip())
    if proc.returncode != 0:
        stderr = (proc.stderr or "").strip()
        if stderr:
            tail_lines.append(f"stderr: {stderr.splitlines()[-1].strip()}")
    return int(proc.returncode), tail_lines


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Clarification cadence tuner for parser + responder orchestration.")
    p.add_argument("--scenarios", default=",".join(DEFAULT_SCENARIO_PACK))
    p.add_argument("--ce-values", default="0.55,0.75,0.90")
    p.add_argument("--min-confidence-values", default="0.45,0.55,0.65")
    p.add_argument("--backend", default="ollama")
    p.add_argument("--base-url", default="http://127.0.0.1:11434")
    p.add_argument("--model", default="qwen3.5:9b")
    p.add_argument("--runtime", choices=["core", "none", "mcp"], default="core")
    p.add_argument("--clarification-answer-model", default="gpt-oss:20b")
    p.add_argument("--clarification-answer-backend", default="ollama")
    p.add_argument("--clarification-answer-base-url", default="http://127.0.0.1:11434")
    p.add_argument("--context-length", type=int, default=8192)
    p.add_argument("--clarification-answer-context-length", type=int, default=16384)
    p.add_argument("--clarification-answer-history-turns", type=int, default=8)
    p.add_argument("--clarification-answer-kb-clause-limit", type=int, default=80)
    p.add_argument("--clarification-answer-kb-char-budget", type=int, default=5000)
    p.add_argument("--max-clarification-rounds", type=int, default=2)
    p.add_argument("--require-final-confirmation", action="store_true")
    p.add_argument("--timeout-seconds", type=int, default=120)
    p.add_argument("--scenario-timeout-seconds", type=int, default=720)
    p.add_argument("--prompt-file", default="modelfiles/semantic_parser_system_prompt.md")
    p.add_argument("--env-file", default="")
    p.add_argument("--kb-root", default="tmp/kb_store")
    p.add_argument("--kb-name-prefix", default="ce_cadence")
    p.add_argument("--strict-registry", action="store_true")
    p.add_argument("--predicate-registry", default="modelfiles/predicate_registry.json")
    p.add_argument("--type-schema", default="")
    p.add_argument("--strict-types", action="store_true")
    p.add_argument("--out-dir", default="tmp/runs/clarification_cadence")
    p.add_argument("--summary-out", default="")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    scenarios = [Path(x.strip()) for x in args.scenarios.split(",") if x.strip()]
    missing = [str(p) for p in scenarios if not p.exists()]
    if missing:
        print("Missing scenario file(s):")
        for row in missing:
            print(f"  - {row}")
        return 2

    ce_values = _parse_float_list(args.ce_values)
    mc_values = _parse_float_list(args.min_confidence_values)
    if not ce_values or not mc_values:
        print("Both --ce-values and --min-confidence-values must contain at least one value.")
        return 2

    settings = [CadenceSetting(ce=ce, min_conf=mc) for ce in ce_values for mc in mc_values]
    out_dir = (ROOT / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = _utc_stamp()
    summary_out = (
        Path(args.summary_out).resolve()
        if str(args.summary_out).strip()
        else (ROOT / "tmp" / "runs" / f"clarification_cadence_summary_{stamp}.json").resolve()
    )
    summary_out.parent.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    print(f"Cadence sweep: {len(settings)} settings x {len(scenarios)} scenarios")
    for setting in settings:
        print(f"\n[SETTING] {setting.key}")
        for scenario in scenarios:
            report_path = out_dir / f"{scenario.stem}__{setting.key}.json"
            rc, tail = _run_one(
                scenario=scenario.resolve(),
                setting=setting,
                args=args,
                out_path=report_path,
            )
            report = _load_report(report_path) if report_path.exists() else None
            if isinstance(report, dict):
                validation_passed = int(report.get("validation_passed", 0) or 0)
                validation_total = int(report.get("validation_total", 0) or 0)
                overall_status = str(report.get("overall_status", "")).strip()
                clar_rounds = int(report.get("clarification_rounds_total", 0) or 0)
                clar_req = int(report.get("turns_clarification_requested", 0) or 0)
                conf_req = int(report.get("turns_confirmation_requested", 0) or 0)
                synthetic_rounds = _synthetic_rounds_used(report)
                decision_counts = report.get("decision_state_counts", {})
            else:
                validation_passed = 0
                validation_total = 0
                overall_status = "missing_report"
                clar_rounds = 0
                clar_req = 0
                conf_req = 0
                synthetic_rounds = 0
                decision_counts = {}

            row = {
                "setting": {"ce": setting.ce, "min_confidence": setting.min_conf, "key": setting.key},
                "scenario": scenario.stem,
                "return_code": rc,
                "report_path": str(report_path),
                "overall_status": overall_status,
                "validation_passed": validation_passed,
                "validation_total": validation_total,
                "clarification_rounds_total": clar_rounds,
                "turns_clarification_requested": clar_req,
                "turns_confirmation_requested": conf_req,
                "synthetic_clarification_rounds": synthetic_rounds,
                "decision_state_counts": decision_counts,
                "stdout_tail": tail,
            }
            rows.append(row)
            label = f"{validation_passed}/{validation_total}" if validation_total > 0 else "n/a"
            print(
                f"  - {scenario.stem}: rc={rc} status={overall_status} "
                f"val={label} clar_rounds={clar_rounds} conf_requests={conf_req} synth_rounds={synthetic_rounds}"
            )

    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        key = str((row.get("setting") or {}).get("key", ""))
        grouped.setdefault(key, []).append(row)

    ranking: list[dict[str, Any]] = []
    for key, group_rows in grouped.items():
        total = len(group_rows)
        pass_count = sum(
            1
            for row in group_rows
            if int(row.get("validation_total", 0) or 0) > 0
            and int(row.get("validation_passed", 0) or 0) == int(row.get("validation_total", 0) or 0)
            and str(row.get("overall_status", "")).lower() == "passed"
        )
        avg_rounds = (
            sum(int(row.get("clarification_rounds_total", 0) or 0) for row in group_rows) / total
            if total > 0
            else 0.0
        )
        avg_synth = (
            sum(int(row.get("synthetic_clarification_rounds", 0) or 0) for row in group_rows) / total
            if total > 0
            else 0.0
        )
        pass_rate = (pass_count / total) if total > 0 else 0.0
        score = (pass_rate * 100.0) - (avg_rounds * 1.5) - (avg_synth * 0.5)
        first_setting = group_rows[0].get("setting", {})
        ranking.append(
            {
                "setting": first_setting,
                "scenario_count": total,
                "pass_count": pass_count,
                "pass_rate": round(pass_rate, 4),
                "avg_clarification_rounds": round(avg_rounds, 4),
                "avg_synthetic_rounds": round(avg_synth, 4),
                "score": round(score, 4),
            }
        )

    ranking.sort(key=lambda row: (float(row.get("score", 0.0)), float(row.get("pass_rate", 0.0))), reverse=True)
    summary = {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "parser_model": args.model,
        "clarification_answer_model": args.clarification_answer_model,
        "settings_count": len(settings),
        "scenarios_count": len(scenarios),
        "rows": rows,
        "ranking": ranking,
        "best_setting": ranking[0] if ranking else {},
    }
    summary_out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\nSummary written: {summary_out}")
    if ranking:
        best = ranking[0]
        st = best.get("setting", {})
        print(
            "Best setting: "
            f"{st.get('key')} | pass_rate={best.get('pass_rate')} "
            f"avg_clar_rounds={best.get('avg_clarification_rounds')} "
            f"avg_synth_rounds={best.get('avg_synthetic_rounds')}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
