#!/usr/bin/env python3
"""
Run a controlled bare-vs-baked system-prompt parity check.

Lane A (runtime SP): bare model + prompt-file
Lane B (baked SP): baked model + blank prompt-file
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
DEFAULT_OUT_DIR = ROOT / "tmp" / "runs" / "sp_parity"
DEFAULT_KB_ROOT = ROOT / "tmp" / "kb_store"
DEFAULT_PROMPT_FILE = ROOT / "modelfiles" / "semantic_parser_system_prompt.md"
DEFAULT_BLANK_PROMPT_FILE = ROOT / "modelfiles" / "blank_prompt.md"
DEFAULT_SCENARIOS = [
    "kb_scenarios/stage_01_facts_only.json",
    "kb_scenarios/stage_02_rule_ingest.json",
]


def _slug(text: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in text).strip("_")


def _resolve(path_text: str) -> Path:
    p = Path(path_text)
    if p.is_absolute():
        return p
    return (ROOT / p).resolve()


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run bare-vs-baked SP parity checks.")
    p.add_argument(
        "--scenario",
        action="append",
        default=[],
        help="Scenario path (repeat for multiple). Defaults to stage_01 + stage_02 smoke pair.",
    )
    p.add_argument("--backend", default="ollama")
    p.add_argument("--base-url", default="http://127.0.0.1:11434")
    p.add_argument("--runtime", default="core")
    p.add_argument("--context-length", type=int, default=8192)
    p.add_argument("--bare-model", default="qwen3.5:9b")
    p.add_argument("--baked-model", default="qwen35-semparse:9b")
    p.add_argument("--prompt-file", default=str(DEFAULT_PROMPT_FILE))
    p.add_argument("--blank-prompt-file", default=str(DEFAULT_BLANK_PROMPT_FILE))
    p.add_argument("--kb-root", default=str(DEFAULT_KB_ROOT))
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    p.add_argument("--summary-out", default="")
    p.add_argument("--sp-conflict-policy", choices=["error", "warn", "off"], default="error")
    p.add_argument("--fail-on-drift", action="store_true")
    return p.parse_args()


def _resolve_scenarios(raw: list[str]) -> list[Path]:
    if not raw:
        raw = list(DEFAULT_SCENARIOS)
    out: list[Path] = []
    for item in raw:
        p = _resolve(item)
        if not p.exists():
            raise SystemExit(f"Scenario not found: {p}")
        out.append(p)
    return out


def _ensure_blank_prompt(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text("", encoding="utf-8")
        return
    if path.is_dir():
        raise SystemExit(f"blank prompt path is a directory: {path}")
    text = path.read_text(encoding="utf-8-sig")
    if text.strip():
        path.write_text("", encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _run_lane(
    *,
    lane_name: str,
    scenario_path: Path,
    backend: str,
    base_url: str,
    runtime: str,
    context_length: int,
    model: str,
    prompt_file: Path,
    kb_root: Path,
    out_dir: Path,
    stamp: str,
    sp_conflict_policy: str,
) -> dict[str, Any]:
    scenario_slug = _slug(scenario_path.stem)
    lane_slug = _slug(lane_name)
    out_path = out_dir / f"{scenario_slug}_{lane_slug}_{stamp}.json"
    kb_name = f"parity_{lane_slug}_{scenario_slug}"
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
        runtime,
        "--context-length",
        str(max(512, int(context_length))),
        "--scenario",
        str(scenario_path),
        "--kb-name",
        kb_name,
        "--kb-root",
        str(kb_root),
        "--prompt-file",
        str(prompt_file),
        "--sp-conflict-policy",
        sp_conflict_policy,
        "--out",
        str(out_path),
    ]
    proc = subprocess.run(cmd, cwd=str(ROOT), check=False)
    record: dict[str, Any] = {
        "lane": lane_name,
        "command": cmd,
        "exit_code": int(proc.returncode),
        "run_output": str(out_path),
        "scenario": str(scenario_path),
        "model": model,
        "prompt_file": str(prompt_file),
    }
    if not out_path.exists():
        record["status"] = "missing_output"
        return record
    report = _read_json(out_path)
    prompt_prov = report.get("prompt_provenance", {})
    if not isinstance(prompt_prov, dict):
        prompt_prov = {}
    sp_sources = report.get("system_prompt_sources", {})
    if not isinstance(sp_sources, dict):
        sp_sources = {}
    record.update(
        {
            "status": "ok",
            "overall_status": str(report.get("overall_status", "unknown")),
            "validation_passed": int(report.get("validation_passed", 0) or 0),
            "validation_total": int(report.get("validation_total", 0) or 0),
            "turn_parse_failures": int(report.get("turn_parse_failures", 0) or 0),
            "turn_apply_failures": int(report.get("turn_apply_failures", 0) or 0),
            "prompt_id": str(prompt_prov.get("prompt_id", "")),
            "prompt_sha256": str(prompt_prov.get("prompt_sha256", "")),
            "double_source_active": bool(sp_sources.get("double_source_active")),
            "double_source_basis": str(sp_sources.get("double_source_basis", "")),
        }
    )
    return record


def main() -> int:
    args = _parse_args()
    scenario_paths = _resolve_scenarios(args.scenario)
    prompt_file = _resolve(args.prompt_file)
    blank_prompt_file = _resolve(args.blank_prompt_file)
    kb_root = _resolve(args.kb_root)
    out_dir = _resolve(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    kb_root.mkdir(parents=True, exist_ok=True)
    if not prompt_file.exists():
        raise SystemExit(f"Prompt file not found: {prompt_file}")
    _ensure_blank_prompt(blank_prompt_file)

    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d_%H%M%S")
    per_scenario: list[dict[str, Any]] = []
    drift_count = 0

    for idx, scenario_path in enumerate(scenario_paths, start=1):
        print(f"[{idx:02d}/{len(scenario_paths)}] parity check {scenario_path.name}")
        bare = _run_lane(
            lane_name="runtime_prompt_lane",
            scenario_path=scenario_path,
            backend=args.backend,
            base_url=args.base_url,
            runtime=args.runtime,
            context_length=args.context_length,
            model=args.bare_model,
            prompt_file=prompt_file,
            kb_root=kb_root,
            out_dir=out_dir,
            stamp=stamp,
            sp_conflict_policy=args.sp_conflict_policy,
        )
        baked = _run_lane(
            lane_name="baked_prompt_lane",
            scenario_path=scenario_path,
            backend=args.backend,
            base_url=args.base_url,
            runtime=args.runtime,
            context_length=args.context_length,
            model=args.baked_model,
            prompt_file=blank_prompt_file,
            kb_root=kb_root,
            out_dir=out_dir,
            stamp=stamp,
            sp_conflict_policy=args.sp_conflict_policy,
        )

        parity_equal = (
            bare.get("status") == "ok"
            and baked.get("status") == "ok"
            and bare.get("overall_status") == baked.get("overall_status")
            and int(bare.get("validation_passed", -1)) == int(baked.get("validation_passed", -2))
            and int(bare.get("validation_total", -1)) == int(baked.get("validation_total", -2))
            and int(bare.get("turn_parse_failures", -1)) == int(baked.get("turn_parse_failures", -2))
            and int(bare.get("turn_apply_failures", -1)) == int(baked.get("turn_apply_failures", -2))
        )
        if not parity_equal:
            drift_count += 1

        per_scenario.append(
            {
                "scenario": str(scenario_path),
                "runtime_prompt_lane": bare,
                "baked_prompt_lane": baked,
                "parity_equal": parity_equal,
            }
        )

    summary = {
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "settings": {
            "backend": args.backend,
            "base_url": args.base_url,
            "runtime": args.runtime,
            "context_length": int(args.context_length),
            "bare_model": args.bare_model,
            "baked_model": args.baked_model,
            "prompt_file": str(prompt_file),
            "blank_prompt_file": str(blank_prompt_file),
            "kb_root": str(kb_root),
            "sp_conflict_policy": args.sp_conflict_policy,
        },
        "scenarios_total": len(scenario_paths),
        "parity_mismatches": drift_count,
        "all_parity_equal": drift_count == 0,
        "rows": per_scenario,
    }

    if args.summary_out:
        summary_path = _resolve(args.summary_out)
    else:
        summary_path = out_dir / f"sp_parity_summary_{stamp}.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("")
    print(f"Scenarios: {len(scenario_paths)}")
    print(f"Parity mismatches: {drift_count}")
    print(f"All parity equal: {summary.get('all_parity_equal')}")
    print(f"Summary: {summary_path}")

    if args.fail_on_drift and drift_count > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
