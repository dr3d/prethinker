#!/usr/bin/env python3
"""Run domain-bootstrap source compiles with explicit lane control.

This is an operator wrapper around run_domain_bootstrap_file.py. It keeps the
expensive source-reading work parallel and bounded while preserving the normal
single-fixture artifact format under one output directory per fixture.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET_ROOT = REPO_ROOT / "datasets" / "story_worlds"
DEFAULT_OUT_ROOT = REPO_ROOT / "tmp" / "domain_bootstrap_compile_batch"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.semantic_ir import bootstrap_env_local  # noqa: E402

bootstrap_env_local()


@dataclass(frozen=True)
class CompileJob:
    fixture: str
    text_file: Path
    out_dir: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", type=Path, default=DEFAULT_DATASET_ROOT)
    parser.add_argument("--out-root", type=Path, default=DEFAULT_OUT_ROOT)
    parser.add_argument("--fixture", action="append", default=[], help="Fixture name. Repeat to include multiple.")
    parser.add_argument("--model", default=os.environ.get("PRETHINKER_MODEL", "qwen/qwen3.6-35b-a3b"))
    parser.add_argument("--base-url", default=os.environ.get("PRETHINKER_BASE_URL", "http://127.0.0.1:1234"))
    parser.add_argument("--timeout", type=int, default=900, help="Base per-call LM timeout passed to compile runner.")
    parser.add_argument("--lanes", type=int, default=1, help="Concurrent compile runner processes.")
    parser.add_argument(
        "--timeout-scale",
        type=float,
        default=0.0,
        help="Per-call timeout multiplier. Default 0 means max(1, lanes).",
    )
    parser.add_argument("--domain-hint", default="")
    parser.add_argument("--compile-source", action="store_true")
    parser.add_argument("--compile-plan-passes", action="store_true")
    parser.add_argument("--compile-flat-plus-plan-passes", action="store_true")
    parser.add_argument("--max-plan-passes", type=int, default=6)
    parser.add_argument("--focused-pass-ops-schema", action="store_true")
    parser.add_argument("--source-entity-ledger", action="store_true")
    parser.add_argument("--archival-identifier-ledger", action="store_true")
    parser.add_argument("--source-record-ledger", action="store_true")
    parser.add_argument("--source-record-ledger-facts", action="store_true")
    parser.add_argument("--intake-registry-context", action="store_true")
    parser.add_argument("--review-profile", action="store_true")
    parser.add_argument("--profile-review-retry", action="store_true")
    parser.add_argument("--summarize-existing", action="store_true", help="Summarize latest existing compile artifacts without running jobs.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    lanes = max(1, int(args.lanes))
    timeout_scale = float(args.timeout_scale) if float(args.timeout_scale) > 0 else float(lanes)
    effective_timeout = max(1, int(round(int(args.timeout) * timeout_scale)))
    dataset_root = _abs(args.dataset_root)
    out_root = _abs(args.out_root)
    fixtures = [str(item) for item in args.fixture] or _discover_fixtures(dataset_root)
    jobs = [_build_job(name, dataset_root=dataset_root, out_root=out_root) for name in fixtures]
    commands = [
        _build_command(
            job,
            args=args,
            model=str(args.model),
            base_url=str(args.base_url),
            timeout=effective_timeout,
        )
        for job in jobs
    ]

    if args.dry_run:
        for command in commands:
            print(" ".join(command))
        return 0

    out_root.mkdir(parents=True, exist_ok=True)
    if bool(args.summarize_existing):
        results = [_summarize_existing_job(job) for job in jobs]
        for result in results:
            print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    else:
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=lanes) as pool:
            future_map = {
                pool.submit(_run_job, job, command): job
                for job, command in zip(jobs, commands)
            }
            for future in concurrent.futures.as_completed(future_map):
                result = future.result()
                results.append(result)
                print(json.dumps(result, ensure_ascii=False, sort_keys=True))

    results.sort(key=lambda item: str(item.get("fixture", "")))
    summary = _summarize(results, lanes=lanes, base_timeout=int(args.timeout), effective_timeout=effective_timeout)
    out_json = _abs(args.out_json) if args.out_json else out_root / "compile_batch_summary.json"
    out_md = _abs(args.out_md) if args.out_md else out_root / "compile_batch_summary.md"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    out_md.write_text(_render_md(summary), encoding="utf-8")
    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")
    return 0 if all(int(item.get("returncode", 1)) == 0 for item in results) else 1


def _abs(path: Path | None) -> Path:
    if path is None:
        return REPO_ROOT
    return path if path.is_absolute() else REPO_ROOT / path


def _discover_fixtures(dataset_root: Path) -> list[str]:
    return sorted(path.name for path in dataset_root.iterdir() if (path / "source.md").exists())


def _build_job(name: str, *, dataset_root: Path, out_root: Path) -> CompileJob:
    fixture_root = dataset_root / name
    text_file = fixture_root / "source.md"
    if not text_file.exists():
        raise FileNotFoundError(f"Missing source file: {text_file}")
    return CompileJob(fixture=name, text_file=text_file, out_dir=out_root / name)


def _build_command(
    job: CompileJob,
    *,
    args: argparse.Namespace,
    model: str,
    base_url: str,
    timeout: int,
) -> list[str]:
    command = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "run_domain_bootstrap_file.py"),
        "--text-file",
        str(job.text_file),
        "--model",
        model,
        "--base-url",
        base_url,
        "--timeout",
        str(timeout),
        "--out-dir",
        str(job.out_dir),
    ]
    if str(args.domain_hint or "").strip():
        command.extend(["--domain-hint", str(args.domain_hint).strip()])
    for flag in (
        "compile_source",
        "compile_plan_passes",
        "compile_flat_plus_plan_passes",
        "focused_pass_ops_schema",
        "source_entity_ledger",
        "archival_identifier_ledger",
        "source_record_ledger",
        "source_record_ledger_facts",
        "intake_registry_context",
        "review_profile",
        "profile_review_retry",
    ):
        if bool(getattr(args, flag, False)):
            command.append("--" + flag.replace("_", "-"))
    if int(args.max_plan_passes) > 0:
        command.extend(["--max-plan-passes", str(int(args.max_plan_passes))])
    return command


def _run_job(job: CompileJob, command: list[str]) -> dict[str, Any]:
    job.out_dir.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc)
    proc = subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True)
    latest_json = _latest_compile_json(job.out_dir)
    summary: dict[str, Any] = {}
    if latest_json is not None:
        try:
            payload = json.loads(latest_json.read_text(encoding="utf-8"))
            summary = _extract_compile_summary(payload)
        except Exception as exc:  # pragma: no cover - operator diagnostic only.
            summary = {"summary_error": str(exc)}
    return {
        "fixture": job.fixture,
        "returncode": proc.returncode,
        "started": started.isoformat(),
        "finished": datetime.now(timezone.utc).isoformat(),
        "out_dir": str(job.out_dir),
        "compile_json": str(latest_json) if latest_json else "",
        "summary": summary,
        "stdout_tail": proc.stdout[-2000:],
        "stderr_tail": proc.stderr[-2000:],
    }


def _summarize_existing_job(job: CompileJob) -> dict[str, Any]:
    latest_json = _latest_compile_json(job.out_dir)
    summary: dict[str, Any] = {}
    returncode = 0
    if latest_json is None:
        returncode = 1
    else:
        try:
            payload = json.loads(latest_json.read_text(encoding="utf-8"))
            summary = _extract_compile_summary(payload)
        except Exception as exc:  # pragma: no cover - operator diagnostic only.
            returncode = 1
            summary = {"summary_error": str(exc)}
    return {
        "fixture": job.fixture,
        "returncode": returncode,
        "started": "",
        "finished": datetime.now(timezone.utc).isoformat(),
        "out_dir": str(job.out_dir),
        "compile_json": str(latest_json) if latest_json else "",
        "summary": summary,
        "stdout_tail": "",
        "stderr_tail": "",
    }


def _latest_compile_json(out_dir: Path) -> Path | None:
    paths = sorted(out_dir.glob("domain_bootstrap_file_*.json"), key=lambda path: path.stat().st_mtime)
    return paths[-1] if paths else None


def _extract_compile_summary(payload: dict[str, Any]) -> dict[str, Any]:
    source_compile = payload.get("source_compile", {})
    compile_payload = payload.get("compile", {})
    diagnostics = compile_payload.get("admission_diagnostics", {}) if isinstance(compile_payload, dict) else {}
    operations = diagnostics.get("operations", []) if isinstance(diagnostics, dict) else []
    compile_admitted = _optional_int(source_compile.get("admitted_count")) if isinstance(source_compile, dict) else None
    compile_skipped = _optional_int(source_compile.get("skipped_count")) if isinstance(source_compile, dict) else None
    if compile_admitted is None:
        compile_admitted = sum(1 for row in operations if isinstance(row, dict) and bool(row.get("admitted")))
    if compile_skipped is None:
        compile_skipped = sum(1 for row in operations if isinstance(row, dict) and not bool(row.get("admitted")))
    score = payload.get("score", {}) if isinstance(payload.get("score"), dict) else {}
    predicates = payload.get("candidate_predicates")
    if predicates is None and isinstance(payload.get("parsed"), dict):
        predicates = payload.get("parsed", {}).get("candidate_predicates")
    return {
        "parsed_ok": bool(payload.get("parsed_ok", False)),
        "candidate_predicates": len(predicates or []),
        "compile_admitted": compile_admitted,
        "compile_skipped": compile_skipped,
        "rough_score": score.get("rough_score"),
        "risk_count": score.get("risk_count"),
    }


def _optional_int(value: Any) -> int | None:
    try:
        if value is None:
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def _summarize(results: list[dict[str, Any]], *, lanes: int, base_timeout: int, effective_timeout: int) -> dict[str, Any]:
    totals = {
        "candidate_predicates": 0,
        "compile_admitted": 0,
        "compile_skipped": 0,
    }
    parsed_ok_count = 0
    for result in results:
        summary = result.get("summary", {})
        if not isinstance(summary, dict):
            continue
        parsed_ok_count += 1 if bool(summary.get("parsed_ok")) else 0
        for key in totals:
            totals[key] += int(summary.get(key, 0) or 0)
    return {
        "generated": datetime.now(timezone.utc).isoformat(),
        "lanes": lanes,
        "base_timeout": base_timeout,
        "effective_timeout": effective_timeout,
        "fixture_count": len(results),
        "parsed_ok_count": parsed_ok_count,
        "totals": totals,
        "results": results,
    }


def _render_md(summary: dict[str, Any]) -> str:
    totals = summary.get("totals", {})
    lines = [
        "# Domain Bootstrap Compile Batch Summary",
        "",
        f"Generated: {summary.get('generated')}",
        "",
        f"- Lanes: `{summary.get('lanes')}`",
        f"- Base timeout: `{summary.get('base_timeout')}`",
        f"- Effective per-call timeout: `{summary.get('effective_timeout')}`",
        f"- Fixtures: `{summary.get('fixture_count')}`",
        f"- Parsed OK: `{summary.get('parsed_ok_count')}`",
        f"- Candidate predicates: `{totals.get('candidate_predicates', 0)}`",
        f"- Compile admitted / skipped: `{totals.get('compile_admitted', 0)} / {totals.get('compile_skipped', 0)}`",
        "",
        "| Fixture | Return | Predicates | Admitted | Skipped | Rough | Compile JSON |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for result in summary.get("results", []):
        item = result.get("summary", {}) if isinstance(result, dict) else {}
        lines.append(
            "| `{fixture}` | `{returncode}` | {predicates} | {admitted} | {skipped} | {rough} | `{compile_json}` |".format(
                fixture=result.get("fixture", ""),
                returncode=result.get("returncode", ""),
                predicates=item.get("candidate_predicates", 0),
                admitted=item.get("compile_admitted", 0),
                skipped=item.get("compile_skipped", 0),
                rough=item.get("rough_score", ""),
                compile_json=result.get("compile_json", ""),
            )
        )
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
