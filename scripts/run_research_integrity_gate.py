#!/usr/bin/env python3
"""Run Prethinker's current research integrity gate.

This is a convenience wrapper around existing biting audits. It is meant to be
run before/after research interventions so score movement cannot quietly depend
on known leakage paths.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TESTS = [
    "tests/test_validate_typed_micro_fixtures.py",
    "tests/test_carrier_contract_registry.py",
    "tests/test_summarize_typed_micro_series.py",
    "tests/test_domain_bootstrap_file.py",
    "tests/test_validate_domain_predicate_schema.py",
    "tests/test_audit_carrier_value_domains.py",
    "tests/test_audit_domain_omission_accountability.py",
    "tests/test_audit_kb_atom_inventory.py",
    "tests/test_audit_typed_plan_replay.py",
    "tests/test_audit_redaction_replay.py",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compile-root", type=Path, default=None)
    parser.add_argument("--fixture", action="append", default=[])
    parser.add_argument("--out-dir", type=Path, default=None)
    parser.add_argument("--skip-tests", action="store_true")
    parser.add_argument("--exit-zero", action="store_true", help="Write reports but return 0 even if a gate fails.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = (
        args.out_dir
        or ROOT
        / "tmp"
        / ("research_integrity_gate_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    ).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    steps = build_steps(
        compile_root=args.compile_root.resolve() if args.compile_root else None,
        fixtures=[str(item).strip() for item in args.fixture if str(item).strip()],
        out_dir=out_dir,
        include_tests=not bool(args.skip_tests),
    )
    rows: list[dict[str, Any]] = []
    for step in steps:
        print("$ " + " ".join(step["cmd"]), flush=True)
        proc = subprocess.run(step["cmd"], cwd=ROOT)
        rows.append({**step, "returncode": int(proc.returncode), "status": "pass" if proc.returncode == 0 else "fail"})
    report = {
        "schema_version": "research_integrity_gate_v1",
        "out_dir": str(out_dir),
        "summary": {
            "step_count": len(rows),
            "failed_steps": sum(1 for row in rows if row["status"] != "pass"),
            "status": "fail" if any(row["status"] != "pass" for row in rows) else "pass",
        },
        "steps": rows,
    }
    (out_dir / "research_integrity_gate.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "research_integrity_gate.md").write_text(render_markdown(report), encoding="utf-8")
    print(render_markdown(report), flush=True)
    return 0 if args.exit_zero or report["summary"]["status"] == "pass" else 1


def build_steps(
    *,
    compile_root: Path | None,
    fixtures: list[str],
    out_dir: Path,
    include_tests: bool,
) -> list[dict[str, Any]]:
    steps: list[dict[str, Any]] = [
        {
            "name": "sign_clean_audit",
            "cmd": [
                sys.executable,
                "scripts/audit_sign_clean.py",
                "--out-json",
                str(out_dir / "sign_clean_audit.json"),
                "--out-md",
                str(out_dir / "sign_clean_audit.md"),
            ],
        }
    ]
    if compile_root is not None:
        fixture_args = _fixture_args(fixtures)
        steps.extend(
            [
                {
                    "name": "atom_shape_audit",
                    "cmd": [
                        sys.executable,
                        "scripts/audit_kb_atom_inventory.py",
                        "--compile-root",
                        str(compile_root),
                        *fixture_args,
                        "--enforce-atom-shape",
                        "--out-json",
                        str(out_dir / "atom_inventory.json"),
                        "--out-md",
                        str(out_dir / "atom_inventory.md"),
                    ],
                },
                {
                    "name": "carrier_value_domain_audit",
                    "cmd": [
                        sys.executable,
                        "scripts/audit_carrier_value_domains.py",
                        "--compile-root",
                        str(compile_root),
                        *fixture_args,
                        "--out-json",
                        str(out_dir / "carrier_value_domains.json"),
                        "--out-md",
                        str(out_dir / "carrier_value_domains.md"),
                    ],
                },
                {
                    "name": "domain_omission_accountability_audit",
                    "cmd": [
                        sys.executable,
                        "scripts/audit_domain_omission_accountability.py",
                        "--compile-root",
                        str(compile_root),
                        *fixture_args,
                        "--out-json",
                        str(out_dir / "domain_omission_accountability.json"),
                        "--out-md",
                        str(out_dir / "domain_omission_accountability.md"),
                    ],
                },
            ]
        )
    if include_tests:
        steps.append(
            {
                "name": "focused_governance_tests",
                "cmd": [sys.executable, "-m", "pytest", *DEFAULT_TESTS, "-q"],
            }
        )
    return steps


def _fixture_args(fixtures: list[str]) -> list[str]:
    args: list[str] = []
    for fixture in fixtures:
        args.extend(["--fixture", fixture])
    return args


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Research Integrity Gate",
        "",
        f"- Status: `{summary['status']}`",
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


if __name__ == "__main__":
    raise SystemExit(main())
