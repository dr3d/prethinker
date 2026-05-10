#!/usr/bin/env python3
"""Run no-oracle QA mode selection for multiple fixtures with lane control."""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_ROOT = REPO_ROOT / "tmp" / "qa_mode_selector_batch"


@dataclass(frozen=True)
class SelectorJob:
    fixture: str
    group: str
    out_json: Path
    out_md: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--qa-root",
        action="append",
        required=True,
        help="Candidate QA root as label=path. Path must contain per-fixture QA artifact directories.",
    )
    parser.add_argument("--fixture", action="append", default=[], help="Fixture name. Repeat to include multiple.")
    parser.add_argument("--out-root", type=Path, default=DEFAULT_OUT_ROOT)
    parser.add_argument("--model", default="qwen/qwen3.6-35b-a3b")
    parser.add_argument("--base-url", default="http://127.0.0.1:1234")
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--lanes", type=int, default=1)
    parser.add_argument(
        "--selection-policy",
        default="structural",
        choices=["direct", "completeness", "relevance", "activation", "structural", "hybrid", "protected", "guarded_activation"],
    )
    parser.add_argument("--hybrid-llm-policy", default="activation", choices=["direct", "completeness", "relevance", "activation"])
    parser.add_argument("--hybrid-margin", type=float, default=0.16)
    parser.add_argument("--hybrid-min-score", type=float, default=0.45)
    parser.add_argument("--include-self-check", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    lanes = max(1, int(args.lanes))
    out_root = _abs(args.out_root)
    roots = _parse_roots(args.qa_root)
    fixtures = [str(item) for item in args.fixture] or _discover_fixtures(roots)
    jobs = [_build_job(fixture, roots=roots, out_root=out_root) for fixture in fixtures]
    commands = [_build_command(job, args=args) for job in jobs]

    if args.dry_run:
        for command in commands:
            print(" ".join(command))
        return 0

    out_root.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []
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
    summary = _summarize(results, lanes=lanes, policy=str(args.selection_policy))
    out_json = _abs(args.out_json) if args.out_json else out_root / "selector_batch_summary.json"
    out_md = _abs(args.out_md) if args.out_md else out_root / "selector_batch_summary.md"
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


def _parse_roots(items: list[str]) -> list[tuple[str, Path]]:
    roots: list[tuple[str, Path]] = []
    for item in items:
        if "=" not in item:
            raise ValueError(f"--qa-root must be label=path, got: {item}")
        label, raw_path = item.split("=", 1)
        label = label.strip()
        if not label:
            raise ValueError(f"Empty label in --qa-root: {item}")
        roots.append((label, _abs(Path(raw_path.strip()))))
    return roots


def _discover_fixtures(roots: list[tuple[str, Path]]) -> list[str]:
    common: set[str] | None = None
    for _label, root in roots:
        fixtures = {path.name for path in root.iterdir() if path.is_dir()}
        common = fixtures if common is None else common & fixtures
    return sorted(common or set())


def _build_job(fixture: str, *, roots: list[tuple[str, Path]], out_root: Path) -> SelectorJob:
    parts: list[str] = []
    for label, root in roots:
        qa_json = _latest_qa_json(root / fixture)
        if qa_json is None:
            raise FileNotFoundError(f"No QA JSON found under {root / fixture}")
        parts.append(f"{label}={qa_json}")
    return SelectorJob(
        fixture=fixture,
        group=f"{fixture}:" + ",".join(parts),
        out_json=out_root / fixture / "selector.json",
        out_md=out_root / fixture / "selector.md",
    )


def _latest_qa_json(out_dir: Path) -> Path | None:
    paths = sorted(out_dir.glob("domain_bootstrap_qa_*.json"), key=lambda path: path.stat().st_mtime)
    return paths[-1] if paths else None


def _build_command(job: SelectorJob, *, args: argparse.Namespace) -> list[str]:
    command = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "select_qa_mode_without_oracle.py"),
        "--group",
        job.group,
        "--selection-policy",
        str(args.selection_policy),
        "--model",
        str(args.model),
        "--base-url",
        str(args.base_url),
        "--timeout",
        str(int(args.timeout)),
        "--hybrid-llm-policy",
        str(args.hybrid_llm_policy),
        "--hybrid-margin",
        str(float(args.hybrid_margin)),
        "--hybrid-min-score",
        str(float(args.hybrid_min_score)),
        "--out-json",
        str(job.out_json),
        "--out-md",
        str(job.out_md),
    ]
    if bool(args.include_self_check):
        command.append("--include-self-check")
    return command


def _run_job(job: SelectorJob, command: list[str]) -> dict[str, Any]:
    job.out_json.parent.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc)
    proc = subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True)
    summary: dict[str, Any] = {}
    if job.out_json.exists():
        try:
            payload = json.loads(job.out_json.read_text(encoding="utf-8"))
            summary = payload.get("summary", {}) if isinstance(payload, dict) else {}
        except Exception as exc:  # pragma: no cover - operator diagnostic only.
            summary = {"summary_error": str(exc)}
    return {
        "fixture": job.fixture,
        "returncode": proc.returncode,
        "started": started.isoformat(),
        "finished": datetime.now(timezone.utc).isoformat(),
        "out_json": str(job.out_json),
        "out_md": str(job.out_md),
        "summary": summary,
        "stdout_tail": proc.stdout[-2000:],
        "stderr_tail": proc.stderr[-2000:],
    }


def _summarize(results: list[dict[str, Any]], *, lanes: int, policy: str) -> dict[str, Any]:
    totals = {
        "row_count": 0,
        "selected_exact": 0,
        "selected_partial": 0,
        "selected_miss": 0,
        "perfect_exact": 0,
        "perfect_partial": 0,
        "perfect_miss": 0,
        "selected_best_count": 0,
        "selector_error_count": 0,
    }
    for result in results:
        summary = result.get("summary", {})
        if not isinstance(summary, dict):
            continue
        perfect = summary.get("perfect_selector_counts", {})
        totals["row_count"] += int(summary.get("row_count", 0) or 0)
        totals["selected_exact"] += int(summary.get("selected_exact", 0) or 0)
        totals["selected_partial"] += int(summary.get("selected_partial", 0) or 0)
        totals["selected_miss"] += int(summary.get("selected_miss", 0) or 0)
        totals["selected_best_count"] += int(summary.get("selected_best_count", 0) or 0)
        totals["selector_error_count"] += int(summary.get("selector_error_count", 0) or 0)
        if isinstance(perfect, dict):
            totals["perfect_exact"] += int(perfect.get("exact", 0) or 0)
            totals["perfect_partial"] += int(perfect.get("partial", 0) or 0)
            totals["perfect_miss"] += int(perfect.get("miss", 0) or 0)
    totals["selected_exact_rate"] = round(totals["selected_exact"] / totals["row_count"], 4) if totals["row_count"] else 0.0
    totals["perfect_exact_rate"] = round(totals["perfect_exact"] / totals["row_count"], 4) if totals["row_count"] else 0.0
    return {
        "generated": datetime.now(timezone.utc).isoformat(),
        "lanes": lanes,
        "selection_policy": policy,
        "totals": totals,
        "results": results,
    }


def _render_md(summary: dict[str, Any]) -> str:
    totals = summary.get("totals", {})
    lines = [
        "# QA Mode Selector Batch Summary",
        "",
        f"Generated: {summary.get('generated')}",
        "",
        f"- Lanes: `{summary.get('lanes')}`",
        f"- Policy: `{summary.get('selection_policy')}`",
        f"- Rows: `{totals.get('row_count', 0)}`",
        f"- Selected exact / partial / miss: `{totals.get('selected_exact', 0)} / {totals.get('selected_partial', 0)} / {totals.get('selected_miss', 0)}`",
        f"- Selected exact rate: `{totals.get('selected_exact_rate', 0.0)}`",
        f"- Perfect exact / partial / miss: `{totals.get('perfect_exact', 0)} / {totals.get('perfect_partial', 0)} / {totals.get('perfect_miss', 0)}`",
        f"- Perfect exact rate: `{totals.get('perfect_exact_rate', 0.0)}`",
        f"- Selected best rows: `{totals.get('selected_best_count', 0)}`",
        f"- Selector errors: `{totals.get('selector_error_count', 0)}`",
        "",
        "| Fixture | Return | Selected | Perfect | Best Rows | Selector JSON |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for result in summary.get("results", []):
        item = result.get("summary", {}) if isinstance(result, dict) else {}
        perfect = item.get("perfect_selector_counts", {}) if isinstance(item.get("perfect_selector_counts"), dict) else {}
        lines.append(
            "| `{fixture}` | `{returncode}` | {selected} | {perfect} | {best} | `{out_json}` |".format(
                fixture=result.get("fixture", ""),
                returncode=result.get("returncode", ""),
                selected=f"{item.get('selected_exact', 0)} / {item.get('selected_partial', 0)} / {item.get('selected_miss', 0)}",
                perfect=f"{perfect.get('exact', 0)} / {perfect.get('partial', 0)} / {perfect.get('miss', 0)}",
                best=item.get("selected_best_count", 0),
                out_json=result.get("out_json", ""),
            )
        )
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
