#!/usr/bin/env python3
"""Run the claim-bearing gate for a domain transfer compile cell."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", required=True)
    parser.add_argument("--compile-root", type=Path, required=True)
    parser.add_argument("--compile-json", action="append", type=Path, required=True)
    parser.add_argument("--support-threshold", type=int, default=2)
    parser.add_argument("--matcher", choices=("unification", "constant_slot"), default="constant_slot")
    parser.add_argument("--out-dir", type=Path, default=None)
    parser.add_argument("--skip-tests", action="store_true")
    parser.add_argument("--exit-zero", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = (
        args.out_dir
        or ROOT
        / "tmp"
        / ("domain_transfer_gate_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    ).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    compile_root = _resolve(args.compile_root)
    compile_paths = [_resolve(path) for path in args.compile_json]
    steps = build_steps(
        fixture=str(args.fixture),
        compile_root=compile_root,
        compile_paths=compile_paths,
        support_threshold=max(1, int(args.support_threshold)),
        matcher=str(args.matcher),
        out_dir=out_dir,
        include_tests=not bool(args.skip_tests),
    )
    rows: list[dict[str, Any]] = []
    for step in steps:
        print("$ " + " ".join(step["cmd"]), flush=True)
        proc = subprocess.run(step["cmd"], cwd=ROOT)
        rows.append({**step, "returncode": int(proc.returncode), "status": "pass" if proc.returncode == 0 else "fail"})

    report = {
        "schema_version": "domain_transfer_gate_v1",
        "fixture": str(args.fixture),
        "compile_root": str(compile_root),
        "compile_jsons": [str(path) for path in compile_paths],
        "out_dir": str(out_dir),
        "summary": {
            "step_count": len(rows),
            "failed_steps": sum(1 for row in rows if row["status"] != "pass"),
            "status": "fail" if any(row["status"] != "pass" for row in rows) else "pass",
        },
        "steps": rows,
    }
    (out_dir / "domain_transfer_gate.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out_dir / "domain_transfer_gate.md").write_text(render_markdown(report), encoding="utf-8")
    print(render_markdown(report), flush=True)
    return 0 if args.exit_zero or report["summary"]["status"] == "pass" else 1


def build_steps(
    *,
    fixture: str,
    compile_root: Path,
    compile_paths: list[Path],
    support_threshold: int,
    matcher: str,
    out_dir: Path,
    include_tests: bool,
) -> list[dict[str, Any]]:
    summary_cmd = [
        sys.executable,
        "scripts/summarize_typed_micro_series.py",
        "--fixture",
        fixture,
        "--support-threshold",
        str(support_threshold),
        "--matcher",
        matcher,
        "--enforce-supported",
        "--enforce-no-forbidden",
        "--out-json",
        str(out_dir / "typed_micro_series.json"),
        "--out-md",
        str(out_dir / "typed_micro_series.md"),
    ]
    for path in compile_paths:
        summary_cmd.extend(["--compile-json", str(path)])

    integrity_cmd = [
        sys.executable,
        "scripts/run_research_integrity_gate.py",
        "--compile-root",
        str(compile_root),
        "--out-dir",
        str(out_dir / "research_integrity_gate"),
    ]
    if not include_tests:
        integrity_cmd.append("--skip-tests")

    return [
        {"name": "typed_micro_series_expected_forbidden", "cmd": summary_cmd},
        {"name": "research_integrity_gate", "cmd": integrity_cmd},
    ]


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Domain Transfer Gate",
        "",
        f"- Status: `{summary['status']}`",
        f"- Fixture: `{report['fixture']}`",
        f"- Steps: `{summary['step_count']}`",
        f"- Failed steps: `{summary['failed_steps']}`",
        f"- Output directory: `{report['out_dir']}`",
        "",
        "| Step | Status | Return code |",
        "| --- | --- | ---: |",
    ]
    for row in report.get("steps", []):
        lines.append(f"| `{row['name']}` | `{row['status']}` | {row['returncode']} |")
    return "\n".join(lines) + "\n"


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else (ROOT / path).resolve()


if __name__ == "__main__":
    raise SystemExit(main())
