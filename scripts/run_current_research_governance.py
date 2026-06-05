#!/usr/bin/env python3
"""Run the current claim-protection checks as one governance command."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]

SEC_VALUE_AXIS_FACT_FILES = [
    "datasets/compile_micro_fixtures/sec_form_8k_skeleton_v1/expected_facts.pl",
    "datasets/compile_micro_fixtures/sec_form_8k_skeleton_transfer_001/expected_facts.pl",
    "datasets/compile_micro_fixtures/sec_form_8k_skeleton_transfer_002/expected_facts.pl",
    "datasets/compile_micro_fixtures/sec_form_8k_skeleton_transfer_003/expected_facts.pl",
    "datasets/compile_micro_fixtures/sec_form_8k_skeleton_v1/forbidden_facts.pl",
    "datasets/compile_micro_fixtures/sec_form_8k_skeleton_transfer_001/forbidden_facts.pl",
    "datasets/compile_micro_fixtures/sec_form_8k_skeleton_transfer_002/forbidden_facts.pl",
    "datasets/compile_micro_fixtures/sec_form_8k_skeleton_transfer_003/forbidden_facts.pl",
]
COMPILE_FACT_QA_MANIFEST = Path("datasets/domain_pack_measurements/current_compile_fact_qa_manifest.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-root", type=Path, default=Path("tmp/current_research_governance"))
    parser.add_argument("--include-pytest", action="store_true")
    parser.add_argument("--exit-zero", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out_root = args.out_root
    out_root.mkdir(parents=True, exist_ok=True)
    commands = governance_commands(out_root=out_root, include_pytest=args.include_pytest)
    results = [run_command(spec) for spec in commands]
    summary = {
        "schema": "prethinker.current_research_governance_run.v1",
        "created_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "summary": {
            "command_count": len(results),
            "failed_count": sum(1 for result in results if result["returncode"] != 0),
            "status": "pass" if all(result["returncode"] == 0 for result in results) else "fail",
        },
        "commands": results,
    }
    (out_root / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out_root / "SUMMARY.md").write_text(report_md(summary), encoding="utf-8")
    failed = summary["summary"]["status"] != "pass"
    return 0 if args.exit_zero or not failed else 1


def governance_commands(*, out_root: Path, include_pytest: bool) -> list[dict[str, Any]]:
    python = sys.executable
    report_root = out_root / "reports"
    commands: list[dict[str, Any]] = [
        {
            "id": "sign_clean",
            "command": [
                python,
                "scripts/audit_sign_clean.py",
                "--out-json",
                str(report_root / "sign_clean.json"),
                "--out-md",
                str(report_root / "sign_clean.md"),
            ],
        },
        {
            "id": "research_artifact_paths",
            "command": [
                python,
                "scripts/audit_research_artifact_paths.py",
                "--out-json",
                str(report_root / "research_artifact_paths.json"),
                "--out-md",
                str(report_root / "research_artifact_paths.md"),
            ],
        },
        {
            "id": "historical_score_claims",
            "command": [
                python,
                "scripts/audit_historical_score_claims.py",
                "--out-json",
                str(report_root / "historical_score_claims.json"),
                "--out-md",
                str(report_root / "historical_score_claims.md"),
            ],
        },
        {
            "id": "domain_predicate_schema",
            "command": [
                python,
                "scripts/validate_domain_predicate_schema.py",
                "--root",
                "datasets/domain_profiles",
            ],
        },
        {
            "id": "domain_pack_status",
            "command": [
                python,
                "scripts/summarize_domain_pack_status.py",
                "--out-json",
                str(report_root / "domain_pack_status.json"),
                "--out-md",
                str(report_root / "domain_pack_status.md"),
                "--expect-md",
                "docs/DOMAIN_PACK_STATUS.md",
            ],
        },
        {
            "id": "domain_pack_variance_status",
            "command": [
                python,
                "scripts/summarize_domain_pack_variance_status.py",
                "--out-json",
                str(report_root / "domain_pack_variance_status.json"),
                "--out-md",
                str(report_root / "domain_pack_variance_status.md"),
                "--expect-md",
                "docs/DOMAIN_PACK_VARIANCE_STATUS.md",
            ],
        },
        {
            "id": "domain_accountability_status",
            "command": [
                python,
                "scripts/summarize_domain_accountability_status.py",
                "--out-json",
                str(report_root / "domain_accountability_status.json"),
                "--out-md",
                str(report_root / "domain_accountability_status.md"),
                "--expect-md",
                "docs/DOMAIN_ACCOUNTABILITY_STATUS.md",
            ],
        },
        {
            "id": "fixture_bank_domain_inventory",
            "command": [
                python,
                "scripts/summarize_fixture_bank_domains.py",
                "--out-json",
                str(report_root / "fixture_bank_domain_inventory.json"),
                "--out-md",
                str(report_root / "fixture_bank_domain_inventory.md"),
                "--expect-md",
                "docs/FIXTURE_BANK_DOMAIN_INVENTORY.md",
            ],
        },
        {
            "id": "domain_predicate_proposal_status",
            "command": [
                python,
                "scripts/validate_domain_predicate_proposals.py",
                "--out-json",
                str(report_root / "domain_predicate_proposal_status.json"),
                "--out-md",
                str(report_root / "domain_predicate_proposal_status.md"),
                "--expect-md",
                "docs/DOMAIN_PREDICATE_PROPOSAL_STATUS.md",
            ],
        },
        {
            "id": "pending_external_work_orders",
            "command": [
                python,
                "scripts/audit_pending_external_work_orders.py",
                "--out-json",
                str(report_root / "pending_external_work_orders.json"),
                "--out-md",
                str(report_root / "pending_external_work_orders.md"),
                "--expect-md",
                "docs/PENDING_EXTERNAL_WORK_ORDERS.md",
            ],
        },
        {
            "id": "query_micro_fixture_contracts",
            "command": [
                python,
                "scripts/audit_query_micro_fixture_contracts.py",
                "--out-json",
                str(report_root / "query_micro_fixture_contracts.json"),
                "--out-md",
                str(report_root / "query_micro_fixture_contracts.md"),
                "--expect-md",
                "docs/QUERY_MICRO_FIXTURE_CONTRACT_STATUS.md",
            ],
        },
        {
            "id": "query_grounding_status",
            "command": [
                python,
                "scripts/summarize_query_grounding_status.py",
                "--out-json",
                str(report_root / "query_grounding_status.json"),
                "--out-md",
                str(report_root / "query_grounding_status.md"),
                "--expect-md",
                "docs/QUERY_GROUNDING_STATUS.md",
            ],
        },
        {
            "id": "candidate_oracle_reviews",
            "command": [
                python,
                "scripts/audit_candidate_oracle_reviews.py",
                "--out-json",
                str(report_root / "candidate_oracle_reviews.json"),
                "--out-md",
                str(report_root / "candidate_oracle_reviews.md"),
                "--expect-md",
                "docs/CANDIDATE_ORACLE_REVIEW_STATUS.md",
            ],
        },
        {
            "id": "source_oracle_reviews",
            "command": [
                python,
                "scripts/audit_source_oracle_reviews.py",
                "--out-json",
                str(report_root / "source_oracle_reviews.json"),
                "--out-md",
                str(report_root / "source_oracle_reviews.md"),
                "--expect-md",
                "docs/SOURCE_ORACLE_REVIEW_STATUS.md",
            ],
        },
        {
            "id": "sec_value_axis_integrity",
            "command": [
                python,
                "scripts/audit_sec_value_axis_integrity.py",
                *_sec_value_axis_audit_inputs(),
                "--out-json",
                str(report_root / "sec_value_axis_integrity.json"),
                "--out-md",
                str(report_root / "sec_value_axis_integrity.md"),
                "--expect-md",
                "docs/SEC_VALUE_AXIS_INTEGRITY_STATUS.md",
            ],
        },
        {
            "id": "compile_fact_qa_exclusions",
            "command": [
                python,
                "scripts/audit_compile_fact_qa_exclusions.py",
                "--out-json",
                str(report_root / "compile_fact_qa_exclusions.json"),
                "--out-md",
                str(report_root / "compile_fact_qa_exclusions.md"),
            ],
        },
        {
            "id": "compile_fact_qa_manifest_sources",
            "command": [
                python,
                "scripts/audit_compile_fact_qa_manifest_sources.py",
                "--out-json",
                str(report_root / "compile_fact_qa_manifest_sources.json"),
                "--out-md",
                str(report_root / "compile_fact_qa_manifest_sources.md"),
            ],
        },
        {
            "id": "reference_judge_null_control_reports",
            "command": [
                python,
                "scripts/audit_reference_judge_null_control_reports.py",
                "--out-json",
                str(report_root / "reference_judge_null_control_reports.json"),
                "--out-md",
                str(report_root / "reference_judge_null_control_reports.md"),
            ],
        },
        {
            "id": "compile_fact_qa_manifest",
            "command": [
                python,
                "scripts/run_compile_fact_judged_qa_manifest.py",
                "--out-root",
                str(out_root / "compile_fact_qa_manifest"),
            ],
        },
        {
            "id": "current_compile_fact_qa_status",
            "command": [
                python,
                "scripts/summarize_current_compile_fact_qa_status.py",
                "--manifest-run",
                str(out_root / "compile_fact_qa_manifest" / "summary.json"),
                "--source-audit",
                str(report_root / "compile_fact_qa_manifest_sources.json"),
                "--variance-status",
                str(report_root / "domain_pack_variance_status.json"),
                "--exclusion-audit",
                str(report_root / "compile_fact_qa_exclusions.json"),
                "--out-json",
                str(report_root / "current_compile_fact_qa_status.json"),
                "--out-md",
                str(report_root / "current_compile_fact_qa_status.md"),
                "--expect-md",
                "docs/CURRENT_COMPILE_FACT_QA_STATUS.md",
            ],
        },
    ]
    if include_pytest:
        commands.append(
            {
                "id": "pytest",
                "command": [python, "-m", "pytest", "-q", "tests"],
            }
        )
    return commands


def _sec_value_axis_audit_inputs() -> list[str]:
    args: list[str] = []
    for fact_file in SEC_VALUE_AXIS_FACT_FILES:
        args.extend(["--fact-file", fact_file])
    for compile_json in _sec_value_axis_compile_jsons_from_manifest():
        args.extend(["--compile-json", str(compile_json)])
    return args


def _sec_value_axis_compile_jsons_from_manifest() -> list[Path]:
    manifest_path = REPO_ROOT / COMPILE_FACT_QA_MANIFEST
    if not manifest_path.exists():
        return []
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    cells = manifest.get("cells")
    if not isinstance(cells, list):
        return []
    compile_jsons: list[Path] = []
    for cell in cells:
        if not isinstance(cell, dict):
            continue
        cell_id = str(cell.get("id", ""))
        if not cell_id.startswith("sec_form_8k"):
            continue
        bundle = str(cell.get("domain_lens_bundle", "")).strip()
        if not bundle:
            continue
        bundle_root = Path(bundle)
        if not bundle_root.is_absolute():
            bundle_root = REPO_ROOT / bundle_root
        union_root = bundle_root / "unions"
        if not union_root.exists():
            continue
        compile_jsons.extend(sorted(union_root.rglob("domain_bootstrap_file_*.json")))
    return compile_jsons


def run_command(spec: dict[str, Any]) -> dict[str, Any]:
    completed = subprocess.run(
        spec["command"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    )
    return {
        "id": spec["id"],
        "command": spec["command"],
        "returncode": completed.returncode,
        "stdout": completed.stdout[-4000:],
        "stderr": completed.stderr[-4000:],
    }


def report_md(summary: dict[str, Any]) -> str:
    lines = [
        "# Current Research Governance Run",
        "",
        f"Status: `{summary['summary']['status']}`",
        f"Commands: `{summary['summary']['command_count']}`",
        f"Failures: `{summary['summary']['failed_count']}`",
        "",
        "| Check | Status |",
        "| --- | --- |",
    ]
    for result in summary["commands"]:
        status = "pass" if result["returncode"] == 0 else f"fail ({result['returncode']})"
        lines.append(f"| `{result['id']}` | `{status}` |")
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
