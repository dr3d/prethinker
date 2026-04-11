#!/usr/bin/env python3
"""
Run ladder scenarios in a selectable range with smart skip behavior.

Primary goals:
1) avoid unnecessary reruns when scenario+prompt+settings already passed
2) allow start/end rung parameters for focused sweeps
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import re
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCENARIOS_DIR = ROOT / "kb_scenarios"
DEFAULT_RUNS_DIR = ROOT / "kb_runs"
DEFAULT_OUT_DIR = ROOT / "tmp" / "runs" / "ladder"
DEFAULT_SUMMARY_DIR = ROOT / "tmp" / "runs"


@dataclass(frozen=True)
class ScenarioRow:
    index: int
    path: Path
    stem: str
    family: str
    rung_num: int


def _resolve(path_text: str) -> Path:
    p = Path(path_text)
    if p.is_absolute():
        return p
    return (Path.cwd() / p).resolve()


def _utc_now_compact() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        obj = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return None
    return obj if isinstance(obj, dict) else None


def _prompt_sha256(path: Path) -> str:
    # Match kb_pipeline prompt provenance hashing: sha256(prompt_text.strip().encode("utf-8"))
    text = path.read_text(encoding="utf-8-sig").strip()
    if not text:
        return ""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _parse_family_and_rung(stem: str) -> tuple[str, int]:
    m = re.match(r"^(stage|acid)_(\d+)_", stem)
    if m:
        return m.group(1), int(m.group(2))
    if stem.startswith("story_"):
        return "story", 0
    return "misc", 0


def _sort_key(path: Path) -> tuple[int, int, str]:
    family, rung_num = _parse_family_and_rung(path.stem)
    family_order = {"stage": 0, "acid": 1, "story": 2, "misc": 3}.get(family, 99)
    return (family_order, rung_num, path.stem)


def _collect_scenarios(scenarios_dir: Path, include_misc: bool) -> list[ScenarioRow]:
    rows: list[Path] = []
    for p in scenarios_dir.glob("*.json"):
        if not p.is_file():
            continue
        stem = p.stem
        if stem.startswith(("stage_", "acid_", "story_")):
            rows.append(p)
            continue
        if include_misc:
            rows.append(p)
    rows.sort(key=_sort_key)
    out: list[ScenarioRow] = []
    for i, p in enumerate(rows, start=1):
        family, rung_num = _parse_family_and_rung(p.stem)
        out.append(ScenarioRow(index=i, path=p.resolve(), stem=p.stem, family=family, rung_num=rung_num))
    return out


def _parse_bound(raw: str, all_rows: list[ScenarioRow], *, default_index: int) -> int:
    token = raw.strip()
    if not token:
        return default_index
    if token.isdigit():
        idx = int(token)
        if 1 <= idx <= len(all_rows):
            return idx
        raise ValueError(f"Bound index out of range: {idx}")
    norm = token.removesuffix(".json")
    for row in all_rows:
        if row.stem == norm:
            return row.index
    raise ValueError(f"Unknown rung bound: {token}")


def _parse_dt(raw: str) -> datetime | None:
    txt = str(raw).strip()
    if not txt:
        return None
    txt = txt.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(txt)
    except ValueError:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _argv_flag_value(argv: list[str], flag: str) -> str:
    for i, token in enumerate(argv):
        if token == flag and i + 1 < len(argv):
            return str(argv[i + 1]).strip()
    return ""


def _extract_report_signature(report: dict[str, Any]) -> dict[str, Any]:
    ms = report.get("model_settings", {})
    if not isinstance(ms, dict):
        ms = {}
    inv = report.get("invocation", {})
    argv = inv.get("argv", []) if isinstance(inv, dict) else []
    if not isinstance(argv, list):
        argv = []
    argv_set = {str(x) for x in argv}
    prompt = report.get("prompt_provenance", {})
    if not isinstance(prompt, dict):
        prompt = {}

    return {
        "backend": str(report.get("backend", "")).strip(),
        "base_url": str(report.get("base_url", "")).strip(),
        "model": str(report.get("model", "")).strip(),
        "runtime": str(report.get("runtime", "")).strip(),
        "context_length": int(ms.get("context_length", 0) or 0),
        "two_pass": bool(report.get("two_pass", ms.get("two_pass", True))),
        "split_extraction": bool(report.get("split_extraction", ms.get("split_extraction", True))),
        "strict_registry": bool(ms.get("strict_registry", False)),
        "strict_types": bool(ms.get("strict_types", False)),
        "clarification_eagerness": round(float(ms.get("clarification_eagerness", 0.0) or 0.0), 6),
        "max_clarification_rounds": int(ms.get("max_clarification_rounds", 0) or 0),
        "clarification_answer_model": str(ms.get("clarification_answer_model", "")).strip(),
        "clarification_answer_backend": str(ms.get("clarification_answer_backend", "")).strip(),
        "clarification_answer_base_url": str(ms.get("clarification_answer_base_url", "")).strip(),
        "clarification_answer_context_length": int(ms.get("clarification_answer_context_length", 0) or 0),
        "prompt_sha256": str(prompt.get("prompt_sha256", "")).strip(),
        "force_empty_kb": "--force-empty-kb" in argv_set,
        "kb_root": _argv_flag_value(argv, "--kb-root"),
        "kb_name": _argv_flag_value(argv, "--kb-name"),
        "corpus_path": _argv_flag_value(argv, "--corpus-path"),
        "seed_from_kb_path": "--seed-from-kb-path" in argv_set,
    }


def _build_target_signature(args: argparse.Namespace, prompt_sha256: str) -> dict[str, Any]:
    answer_model = str(args.clarification_answer_model).strip()
    answer_backend = str(args.clarification_answer_backend).strip() if answer_model else ""
    answer_base_url = str(args.clarification_answer_base_url).strip() if answer_model else ""
    answer_ctx = int(args.clarification_answer_context_length) if answer_model else 0
    return {
        "backend": str(args.backend).strip(),
        "base_url": str(args.base_url).strip(),
        "model": str(args.model).strip(),
        "runtime": str(args.runtime).strip(),
        "context_length": int(args.context_length),
        "two_pass": not bool(args.no_two_pass),
        "split_extraction": not bool(args.no_split_extraction),
        "strict_registry": bool(args.strict_registry),
        "strict_types": bool(args.strict_types),
        "clarification_eagerness": round(float(args.clarification_eagerness), 6),
        "max_clarification_rounds": int(args.max_clarification_rounds),
        "clarification_answer_model": answer_model,
        "clarification_answer_backend": answer_backend,
        "clarification_answer_base_url": answer_base_url,
        "clarification_answer_context_length": answer_ctx,
        "prompt_sha256": str(prompt_sha256).strip(),
        "force_empty_kb": bool(args.force_empty_kb),
        "kb_root": str(args.kb_root).strip(),
        "kb_name": str(args.kb_name).strip(),
        "corpus_path": str(args.corpus_path).strip(),
        "seed_from_kb_path": bool(args.seed_from_kb_path),
    }


def _is_report_passed(report: dict[str, Any]) -> bool:
    status = str(report.get("overall_status", "")).strip().lower()
    if status == "passed":
        return True
    try:
        total = int(report.get("validation_total", 0) or 0)
        passed = int(report.get("validation_passed", 0) or 0)
    except (TypeError, ValueError):
        return False
    return total > 0 and total == passed


def _is_report_fresh_for_scenario(report: dict[str, Any], scenario_path: Path) -> bool:
    finished = _parse_dt(str(report.get("run_finished_utc", "")))
    if finished is None:
        return False
    mtime_utc = datetime.fromtimestamp(scenario_path.stat().st_mtime, tz=timezone.utc)
    return finished >= mtime_utc


def _collect_latest_reports(runs_dirs: list[Path]) -> dict[str, list[tuple[Path, dict[str, Any], datetime]]]:
    out: dict[str, list[tuple[Path, dict[str, Any], datetime]]] = {}
    seen_paths: set[Path] = set()
    for runs_dir in runs_dirs:
        if not runs_dir.exists():
            continue
        for p in runs_dir.rglob("*.json"):
            rp = p.resolve()
            if rp in seen_paths:
                continue
            seen_paths.add(rp)
            report = _read_json(rp)
            if not isinstance(report, dict):
                continue
            scenario = str(report.get("scenario", "")).strip()
            if not scenario:
                continue
            finished = _parse_dt(str(report.get("run_finished_utc", "")))
            if finished is None:
                finished = datetime.fromtimestamp(rp.stat().st_mtime, tz=timezone.utc)
            out.setdefault(scenario, []).append((rp, report, finished))
    for key in list(out.keys()):
        out[key].sort(key=lambda row: row[2], reverse=True)
    return out


def _find_reusable_pass(
    *,
    scenario_stem: str,
    scenario_path: Path,
    target_sig: dict[str, Any],
    reports_by_scenario: dict[str, list[tuple[Path, dict[str, Any], datetime]]],
) -> tuple[Path, dict[str, Any]] | None:
    candidates = reports_by_scenario.get(scenario_stem, [])
    for path, report, _ in candidates:
        if not _is_report_passed(report):
            continue
        if not _is_report_fresh_for_scenario(report, scenario_path):
            continue
        if _extract_report_signature(report) == target_sig:
            return path, report
    return None


def _run_one(args: argparse.Namespace, scenario: ScenarioRow, out_path: Path) -> int:
    cmd: list[str] = [
        sys.executable,
        str(ROOT / "kb_pipeline.py"),
        "--scenario",
        str(scenario.path),
        "--backend",
        str(args.backend),
        "--base-url",
        str(args.base_url),
        "--model",
        str(args.model),
        "--runtime",
        str(args.runtime),
        "--kb-root",
        str(args.kb_root),
        "--prompt-file",
        str(args.prompt_file),
        "--prompt-history-dir",
        str(args.prompt_history_dir),
        "--context-length",
        str(args.context_length),
        "--timeout-seconds",
        str(args.timeout_seconds),
        "--clarification-eagerness",
        str(args.clarification_eagerness),
        "--max-clarification-rounds",
        str(args.max_clarification_rounds),
        "--clarification-answer-context-length",
        str(args.clarification_answer_context_length),
        "--out",
        str(out_path),
    ]
    if args.corpus_path:
        cmd.extend(["--corpus-path", str(args.corpus_path)])
    if args.kb_name:
        cmd.extend(["--kb-name", str(args.kb_name)])
    if args.force_empty_kb:
        cmd.append("--force-empty-kb")
    if args.seed_from_kb_path:
        cmd.append("--seed-from-kb-path")
    if args.strict_registry:
        cmd.extend(["--predicate-registry", str(args.predicate_registry), "--strict-registry"])
    if args.type_schema:
        cmd.extend(["--type-schema", str(args.type_schema)])
    if args.strict_types:
        cmd.append("--strict-types")
    if args.no_two_pass:
        cmd.append("--no-two-pass")
    if args.no_split_extraction:
        cmd.append("--no-split-extraction")
    if args.clarification_answer_model:
        cmd.extend(["--clarification-answer-model", str(args.clarification_answer_model)])
    if args.clarification_answer_backend:
        cmd.extend(["--clarification-answer-backend", str(args.clarification_answer_backend)])
    if args.clarification_answer_base_url:
        cmd.extend(["--clarification-answer-base-url", str(args.clarification_answer_base_url)])
    if args.env_file:
        cmd.extend(["--env-file", str(args.env_file)])

    proc = subprocess.run(cmd, cwd=ROOT)
    return int(proc.returncode)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run ladder scenarios with smart skip and range selection.")
    p.add_argument("--scenarios-dir", default=str(DEFAULT_SCENARIOS_DIR))
    p.add_argument("--runs-dir", default=str(DEFAULT_RUNS_DIR))
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    p.add_argument("--summary-out", default="")
    p.add_argument("--include-misc", action="store_true", help="Include non stage/acid/story scenario JSON files.")
    p.add_argument("--start-rung", default="", help="Rung index (1-based) or scenario name (stem/json).")
    p.add_argument("--end-rung", default="", help="Rung index (1-based) or scenario name (stem/json).")
    p.add_argument("--backend", default="ollama")
    p.add_argument("--base-url", default="http://127.0.0.1:11434")
    p.add_argument("--model", default="qwen3.5:9b")
    p.add_argument("--runtime", choices=["core", "none", "mcp"], default="core")
    p.add_argument("--prompt-file", default="modelfiles/semantic_parser_system_prompt.md")
    p.add_argument("--prompt-history-dir", default="tmp/prompt_history")
    p.add_argument("--env-file", default="")
    p.add_argument("--kb-root", default="tmp/kb_store")
    p.add_argument("--kb-name", default="")
    p.add_argument("--corpus-path", default="")
    p.add_argument("--context-length", type=int, default=8192)
    p.add_argument("--timeout-seconds", type=int, default=120)
    p.add_argument("--clarification-eagerness", type=float, default=0.35)
    p.add_argument("--max-clarification-rounds", type=int, default=2)
    p.add_argument("--clarification-answer-model", default="")
    p.add_argument("--clarification-answer-backend", default="")
    p.add_argument("--clarification-answer-base-url", default="")
    p.add_argument("--clarification-answer-context-length", type=int, default=16384)
    p.add_argument("--predicate-registry", default="modelfiles/predicate_registry.json")
    p.add_argument("--strict-registry", action="store_true")
    p.add_argument("--type-schema", default="")
    p.add_argument("--strict-types", action="store_true")
    p.add_argument("--no-two-pass", action="store_true")
    p.add_argument("--no-split-extraction", action="store_true")
    p.add_argument("--force-empty-kb", action="store_true")
    p.add_argument("--seed-from-kb-path", action="store_true")
    p.add_argument("--label", default="smart_latest", help="Suffix used in output report filenames.")
    p.add_argument("--skip-passed-fresh", action="store_true", default=True)
    p.add_argument("--no-skip-passed-fresh", action="store_true", help="Disable skip optimization.")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--stop-on-fail", action="store_true", default=True)
    p.add_argument("--no-stop-on-fail", action="store_true")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if args.no_skip_passed_fresh:
        args.skip_passed_fresh = False
    if args.no_stop_on_fail:
        args.stop_on_fail = False

    scenarios_dir = _resolve(args.scenarios_dir)
    runs_dir = _resolve(args.runs_dir)
    out_dir = _resolve(args.out_dir)
    prompt_file = _resolve(args.prompt_file)
    prompt_history_dir = _resolve(args.prompt_history_dir)
    if not prompt_file.exists():
        print(f"Prompt file not found: {prompt_file}")
        return 2
    if not scenarios_dir.exists():
        print(f"Scenarios dir not found: {scenarios_dir}")
        return 2

    all_rows = _collect_scenarios(scenarios_dir, include_misc=bool(args.include_misc))
    if not all_rows:
        print(f"No scenarios found in: {scenarios_dir}")
        return 2

    try:
        start_idx = _parse_bound(args.start_rung, all_rows, default_index=1)
        end_idx = _parse_bound(args.end_rung, all_rows, default_index=len(all_rows))
        if start_idx > end_idx:
            raise ValueError(f"start-rung ({start_idx}) must be <= end-rung ({end_idx})")
    except ValueError as exc:
        print(f"Invalid rung range: {exc}")
        return 2
    selected = [row for row in all_rows if start_idx <= row.index <= end_idx]

    prompt_sha = _prompt_sha256(prompt_file)
    target_sig = _build_target_signature(args, prompt_sha256=prompt_sha)
    report_dirs = [runs_dir]
    if out_dir not in report_dirs:
        report_dirs.append(out_dir)
    reports_by_scenario = _collect_latest_reports(report_dirs) if args.skip_passed_fresh else {}

    out_dir.mkdir(parents=True, exist_ok=True)
    prompt_history_dir.mkdir(parents=True, exist_ok=True)
    stamp = _utc_now_compact()
    summary_out = (
        _resolve(args.summary_out)
        if str(args.summary_out).strip()
        else (DEFAULT_SUMMARY_DIR / f"ladder_summary_{stamp}.json").resolve()
    )
    summary_out.parent.mkdir(parents=True, exist_ok=True)

    print(f"Ladder range: {start_idx}..{end_idx} ({len(selected)} scenarios)")
    for row in selected:
        print(f"  {row.index:02d}. {row.stem}")

    run_rows: list[dict[str, Any]] = []
    executed = 0
    skipped = 0
    failed = 0

    for row in selected:
        cached = None
        if args.skip_passed_fresh:
            cached = _find_reusable_pass(
                scenario_stem=row.stem,
                scenario_path=row.path,
                target_sig=target_sig,
                reports_by_scenario=reports_by_scenario,
            )
        if cached is not None:
            skipped += 1
            cached_path, cached_report = cached
            print(f"[SKIP] {row.stem} -> {cached_path}")
            run_rows.append(
                {
                    "scenario": row.stem,
                    "action": "skipped_cached_pass",
                    "cached_report": str(cached_path),
                    "overall_status": str(cached_report.get("overall_status", "")),
                    "validation_passed": int(cached_report.get("validation_passed", 0) or 0),
                    "validation_total": int(cached_report.get("validation_total", 0) or 0),
                }
            )
            continue

        out_path = (out_dir / f"{row.stem}_{args.label}.json").resolve()
        print(f"[RUN ] {row.stem} -> {out_path}")
        if args.dry_run:
            run_rows.append({"scenario": row.stem, "action": "dry_run"})
            continue

        rc = _run_one(args, row, out_path=out_path)
        executed += 1
        report = _read_json(out_path) if out_path.exists() else None
        if rc != 0 or not isinstance(report, dict):
            failed += 1
            run_rows.append({"scenario": row.stem, "action": "executed", "return_code": rc, "overall_status": "error"})
            print(f"[FAIL] {row.stem} (return code {rc})")
            if args.stop_on_fail:
                break
            continue

        status = str(report.get("overall_status", ""))
        v_pass = int(report.get("validation_passed", 0) or 0)
        v_total = int(report.get("validation_total", 0) or 0)
        ok = status.lower() == "passed" or (v_total > 0 and v_pass == v_total)
        if not ok:
            failed += 1
            print(f"[FAIL] {row.stem} ({v_pass}/{v_total}, status={status})")
        else:
            print(f"[PASS] {row.stem} ({v_pass}/{v_total})")
        run_rows.append(
            {
                "scenario": row.stem,
                "action": "executed",
                "report": str(out_path),
                "overall_status": status,
                "validation_passed": v_pass,
                "validation_total": v_total,
                "return_code": rc,
            }
        )
        if not ok and args.stop_on_fail:
            break

    summary = {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "selected_count": len(selected),
        "executed_count": executed,
        "skipped_count": skipped,
        "failed_count": failed,
        "start_rung": args.start_rung,
        "end_rung": args.end_rung,
        "label": args.label,
        "target_signature": target_sig,
        "rows": run_rows,
    }
    summary_out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Summary: {summary_out}")

    return 1 if failed > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
