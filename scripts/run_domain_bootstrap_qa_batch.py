#!/usr/bin/env python3
"""Run domain-bootstrap QA artifacts with explicit GPU lane control.

This is an operator convenience wrapper around run_domain_bootstrap_qa.py. It
does not inspect source prose or scoring files beyond passing the normal QA and
oracle paths through to the underlying runner.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

DEFAULT_DATASET_ROOT = REPO_ROOT / "datasets" / "story_worlds"
DEFAULT_COMPILE_ROOT = REPO_ROOT / "tmp" / "incoming_6_cold_compile_20260508"
DEFAULT_OUT_ROOT = REPO_ROOT / "tmp" / "incoming_6_full40_qa_20260508"


@dataclass(frozen=True)
class QaJob:
    fixture: str
    run_json: Path
    qa_file: Path
    oracle_jsonl: Path | None
    judge_reference_answers: bool
    out_dir: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", type=Path, default=DEFAULT_DATASET_ROOT)
    parser.add_argument("--compile-root", type=Path, default=DEFAULT_COMPILE_ROOT)
    parser.add_argument("--out-root", type=Path, default=DEFAULT_OUT_ROOT)
    parser.add_argument("--fixture", action="append", default=[], help="Fixture name. Repeat to include multiple.")
    parser.add_argument("--model", default="qwen/qwen3.6-35b-a3b")
    parser.add_argument("--base-url", default="http://127.0.0.1:1234")
    parser.add_argument("--limit", type=int, default=40)
    parser.add_argument("--timeout", type=int, default=420, help="Base per-call LM timeout passed to QA runner.")
    parser.add_argument("--lanes", type=int, default=1, help="Concurrent QA runner processes.")
    parser.add_argument(
        "--timeout-scale",
        type=float,
        default=0.0,
        help="Per-call timeout multiplier. Default 0 means max(1, lanes).",
    )
    parser.add_argument("--no-evidence-bundle", action="store_true")
    parser.add_argument("--no-classify-failure-surfaces", action="store_true")
    parser.add_argument("--no-cache", action="store_true", help="Pass through to QA runner for fresh hosted calls.")
    parser.add_argument(
        "--compatibility-adapter-row-limit",
        type=int,
        default=0,
        dest="compatibility_adapter_row_limit",
        help=(
            "Question-level budget for retired query-only compatibility rows. "
            "Default 0 disables compatibility row assembly; use -1 for unbounded forensic delivery."
        ),
    )
    parser.add_argument(
        "--include-retired-native-compatibility-adapters",
        dest="include_retired_native_compatibility_adapters",
        action="store_true",
        help="Opt in to older native-corpus compatibility adapters for forensic replay.",
    )
    parser.add_argument(
        "--disable-current-source-record-summaries",
        action="store_true",
        help="Pass through to QA runner for source-record summary ablation.",
    )
    parser.add_argument(
        "--disable-support-predicate",
        action="append",
        default=[],
        help="Pass through to QA runner. Repeat to disable multiple support predicates.",
    )
    parser.add_argument("--summarize-existing", action="store_true", help="Summarize latest existing QA artifacts without running jobs.")
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
    compile_root = _abs(args.compile_root)
    out_root = _abs(args.out_root)
    fixtures = [str(item) for item in args.fixture] or _discover_fixtures(compile_root)
    jobs = [_build_job(name, dataset_root=dataset_root, compile_root=compile_root, out_root=out_root) for name in fixtures]

    commands = [
        _build_command(
            job,
            model=str(args.model),
            base_url=str(args.base_url),
            limit=int(args.limit),
            timeout=effective_timeout,
            evidence_bundle=not bool(args.no_evidence_bundle),
            classify_failure_surfaces=not bool(args.no_classify_failure_surfaces),
            cache=not bool(args.no_cache),
            compatibility_adapter_row_limit=args.compatibility_adapter_row_limit,
            include_retired_native_compatibility_adapters=bool(args.include_retired_native_compatibility_adapters),
            disable_current_source_record_summaries=bool(args.disable_current_source_record_summaries),
            disabled_support_predicates=tuple(str(item).strip() for item in args.disable_support_predicate if str(item).strip()),
        )
        for job in jobs
    ]
    if args.dry_run:
        for command in commands:
            print(" ".join(command))
        return 0

    out_root.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []
    if bool(args.summarize_existing):
        results = [_summarize_existing_job(job) for job in jobs]
        for result in results:
            print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    else:
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
    out_json = _abs(args.out_json) if args.out_json else out_root / "qa_batch_summary.json"
    out_md = _abs(args.out_md) if args.out_md else out_root / "qa_batch_summary.md"
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


def _discover_fixtures(compile_root: Path) -> list[str]:
    return sorted(path.name for path in compile_root.iterdir() if path.is_dir())


def _build_job(name: str, *, dataset_root: Path, compile_root: Path, out_root: Path) -> QaJob:
    fixture_root = dataset_root / name
    compile_dir = compile_root / name
    run_jsons = sorted(compile_dir.glob("domain_bootstrap_file_*.json"), key=lambda path: path.stat().st_mtime)
    if not run_jsons:
        raise FileNotFoundError(f"No compile JSON found under {compile_dir}")
    qa_file = fixture_root / "qa.md"
    oracle_jsonl = fixture_root / "oracle.jsonl"
    if not qa_file.exists():
        raise FileNotFoundError(f"Missing QA file: {qa_file}")
    has_markdown_answers = _qa_markdown_has_answer_key(qa_file)
    if not oracle_jsonl.exists() and not has_markdown_answers:
        raise FileNotFoundError(f"Missing oracle file or markdown answer key: {oracle_jsonl}")
    return QaJob(
        fixture=name,
        run_json=run_jsons[-1],
        qa_file=qa_file,
        oracle_jsonl=oracle_jsonl if oracle_jsonl.exists() else None,
        judge_reference_answers=oracle_jsonl.exists() or has_markdown_answers,
        out_dir=out_root / name,
    )


def _build_command(
    job: QaJob,
    *,
    model: str,
    base_url: str,
    limit: int,
    timeout: int,
    evidence_bundle: bool,
    classify_failure_surfaces: bool,
    cache: bool = True,
    compatibility_adapter_row_limit: int | None = 0,
    include_retired_native_compatibility_adapters: bool = False,
    disable_current_source_record_summaries: bool = False,
    disabled_support_predicates: tuple[str, ...] = (),
) -> list[str]:
    command = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "run_domain_bootstrap_qa.py"),
        "--run-json",
        str(job.run_json),
        "--qa-file",
        str(job.qa_file),
        "--limit",
        str(limit),
        "--timeout",
        str(timeout),
        "--model",
        model,
        "--base-url",
        base_url,
        "--out-dir",
        str(job.out_dir),
    ]
    if job.oracle_jsonl is not None:
        command.extend(["--oracle-jsonl", str(job.oracle_jsonl)])
    if job.judge_reference_answers:
        command.append("--judge-reference-answers")
    if classify_failure_surfaces:
        command.append("--classify-failure-surfaces")
    if not cache:
        command.append("--no-cache")
    if compatibility_adapter_row_limit is not None:
        command.extend(["--compatibility-adapter-row-limit", str(int(compatibility_adapter_row_limit))])
    if include_retired_native_compatibility_adapters:
        command.append("--include-retired-native-compatibility-adapters")
    if disable_current_source_record_summaries:
        command.append("--disable-current-source-record-summaries")
    for predicate in disabled_support_predicates:
        command.extend(["--disable-support-predicate", predicate])
    if evidence_bundle:
        command.extend(["--evidence-bundle-plan", "--execute-evidence-bundle-plan", "--evidence-bundle-context-filter"])
    return command


def _run_job(job: QaJob, command: list[str]) -> dict[str, Any]:
    job.out_dir.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc)
    proc = subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True)
    latest_json = _latest_qa_json(job.out_dir)
    summary: dict[str, Any] = {}
    if latest_json is not None:
        try:
            payload = json.loads(latest_json.read_text(encoding="utf-8"))
            summary = payload.get("summary", {}) if isinstance(payload, dict) else {}
        except Exception as exc:  # pragma: no cover - operator diagnostic only.
            summary = {"summary_error": str(exc)}
    return {
        "fixture": job.fixture,
        "returncode": proc.returncode,
        "started": started.isoformat(),
        "finished": datetime.now(timezone.utc).isoformat(),
        "out_dir": str(job.out_dir),
        "qa_json": str(latest_json) if latest_json else "",
        "summary": summary,
        "stdout_tail": proc.stdout[-2000:],
        "stderr_tail": proc.stderr[-2000:],
    }


def _summarize_existing_job(job: QaJob) -> dict[str, Any]:
    latest_json = _latest_qa_json(job.out_dir)
    summary: dict[str, Any] = {}
    returncode = 0
    if latest_json is None:
        returncode = 1
    else:
        try:
            payload = json.loads(latest_json.read_text(encoding="utf-8"))
            summary = payload.get("summary", {}) if isinstance(payload, dict) else {}
        except Exception as exc:  # pragma: no cover - operator diagnostic only.
            returncode = 1
            summary = {"summary_error": str(exc)}
    return {
        "fixture": job.fixture,
        "returncode": returncode,
        "started": "",
        "finished": datetime.now(timezone.utc).isoformat(),
        "out_dir": str(job.out_dir),
        "qa_json": str(latest_json) if latest_json else "",
        "summary": summary,
        "stdout_tail": "",
        "stderr_tail": "",
    }


def _latest_qa_json(out_dir: Path) -> Path | None:
    paths = sorted(out_dir.glob("domain_bootstrap_qa_*.json"), key=lambda path: path.stat().st_mtime)
    return paths[-1] if paths else None


def _qa_markdown_has_answer_key(path: Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError:
        return False
    return any(line.strip().lower() == "## answers" for line in text.splitlines())


def _summarize(results: list[dict[str, Any]], *, lanes: int, base_timeout: int, effective_timeout: int) -> dict[str, Any]:
    totals = {
        "question_count": 0,
        "judge_exact": 0,
        "judge_partial": 0,
        "judge_miss": 0,
        "runtime_load_error_count": 0,
        "write_proposal_rows": 0,
    }
    for result in results:
        summary = result.get("summary", {})
        if not isinstance(summary, dict):
            continue
        for key in totals:
            totals[key] += int(summary.get(key, 0) or 0)
    compatibility_pressure = _summarize_compatibility_pressure(results=results, totals=totals)
    exact_rate = (totals["judge_exact"] / totals["question_count"]) if totals["question_count"] else 0.0
    return {
        "generated": datetime.now(timezone.utc).isoformat(),
        "lanes": lanes,
        "base_timeout": base_timeout,
        "effective_timeout": effective_timeout,
        "totals": {**totals, "exact_rate": round(exact_rate, 4)},
        "compatibility_pressure_summary": compatibility_pressure,
        "results": results,
    }


def _summarize_compatibility_pressure(*, results: list[dict[str, Any]], totals: dict[str, int]) -> dict[str, Any]:
    row_class_counts: Counter[str] = Counter()
    companion_row_totals: Counter[str] = Counter()
    row_count = 0
    for result in results:
        summary = result.get("summary", {})
        if not isinstance(summary, dict):
            continue
        compatibility_summary = summary.get("compatibility_row_summary", {})
        if not isinstance(compatibility_summary, dict) or not compatibility_summary:
            continue
        row_count += int(compatibility_summary.get("row_count", 0) or 0)
        raw_class_counts = compatibility_summary.get("row_class_counts", {})
        if isinstance(raw_class_counts, dict):
            for key, value in raw_class_counts.items():
                row_class_counts[str(key)] += int(value or 0)
        raw_companion_totals = compatibility_summary.get("companion_row_totals", {})
        if isinstance(raw_companion_totals, dict):
            for key, value in raw_companion_totals.items():
                companion_row_totals[str(key)] += int(value or 0)
    answer_summary = {
        "question_count": int(totals.get("question_count", 0) or 0),
        "judge_rows": int(totals.get("judge_exact", 0) or 0)
        + int(totals.get("judge_partial", 0) or 0)
        + int(totals.get("judge_miss", 0) or 0),
        "judge_exact": int(totals.get("judge_exact", 0) or 0),
        "judge_partial": int(totals.get("judge_partial", 0) or 0),
        "judge_miss": int(totals.get("judge_miss", 0) or 0),
    }
    return dict(
        {
            "row_count": row_count,
            "row_class_counts": dict(sorted(row_class_counts.items())),
            "companion_row_totals": dict(sorted(companion_row_totals.items())),
            "answer_surface_summary": answer_summary,
        },
        **compatibility_pressure_metrics(
            row_count=row_count,
            row_class_counts=row_class_counts,
            answer_summary=answer_summary,
        ),
    )


def _render_md(summary: dict[str, Any]) -> str:
    totals = summary.get("totals", {})
    compatibility_pressure = summary.get("compatibility_pressure_summary", {})
    lines = [
        "# Domain Bootstrap QA Batch Summary",
        "",
        f"Generated: {summary.get('generated')}",
        "",
        f"- Lanes: `{summary.get('lanes')}`",
        f"- Base timeout: `{summary.get('base_timeout')}`",
        f"- Effective per-call timeout: `{summary.get('effective_timeout')}`",
        f"- Questions: `{totals.get('question_count', 0)}`",
        f"- Exact / partial / miss: `{totals.get('judge_exact', 0)} / {totals.get('judge_partial', 0)} / {totals.get('judge_miss', 0)}`",
        f"- Exact rate: `{totals.get('exact_rate', 0.0)}`",
        f"- Runtime load errors: `{totals.get('runtime_load_error_count', 0)}`",
        f"- Write proposal rows: `{totals.get('write_proposal_rows', 0)}`",
        f"- Compatibility rows: `{display_pressure_label(compatibility_pressure.get('pressure_label', 'unknown'))}` rows=`{compatibility_pressure.get('row_count', 0)}` rows/exact=`{compatibility_pressure.get('compatibility_rows_per_exact')}` tentative-share=`{compatibility_pressure.get('tentative_share', 0.0)}`",
        "",
        "| Fixture | Return | Exact | Partial | Miss | QA JSON |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for result in summary.get("results", []):
        item_summary = result.get("summary", {}) if isinstance(result, dict) else {}
        lines.append(
            "| `{fixture}` | `{returncode}` | {exact} | {partial} | {miss} | `{qa_json}` |".format(
                fixture=result.get("fixture", ""),
                returncode=result.get("returncode", ""),
                exact=item_summary.get("judge_exact", 0),
                partial=item_summary.get("judge_partial", 0),
                miss=item_summary.get("judge_miss", 0),
                qa_json=result.get("qa_json", ""),
            )
        )
    lines.append("")
    return "\n".join(lines)


def compatibility_pressure_metrics(
    *,
    row_count: int,
    row_class_counts: Counter[str],
    answer_summary: dict[str, int],
) -> dict[str, Any]:
    exact = int(answer_summary.get("judge_exact", 0) or 0)
    tentative_rows = int(row_class_counts.get("tentative", 0) or 0)
    direct_rows = int(row_class_counts.get("direct", 0) or 0)
    rows_per_exact = (row_count / exact) if exact else 0.0
    tentative_share = (tentative_rows / row_count) if row_count else 0.0
    return {
        "compatibility_rows_per_exact": round(rows_per_exact, 4),
        "tentative_share": round(tentative_share, 4),
        "direct_support_rows": direct_rows,
        "tentative_support_rows": tentative_rows,
        "pressure_label": compatibility_pressure_label(
            row_count=row_count,
            rows_per_exact=rows_per_exact,
            tentative_share=tentative_share,
        ),
    }


def compatibility_pressure_label(*, row_count: int, rows_per_exact: float, tentative_share: float) -> str:
    if row_count <= 0:
        return "no_compatibility_pressure"
    if rows_per_exact >= 25 or tentative_share >= 0.5:
        return "high_compatibility_pressure"
    if rows_per_exact >= 5:
        return "medium_compatibility_pressure"
    return "low_compatibility_pressure"


def display_pressure_label(value: str) -> str:
    return str(value or "unknown").replace("_", " ")


if __name__ == "__main__":
    raise SystemExit(main())
