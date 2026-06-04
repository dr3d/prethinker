#!/usr/bin/env python3
"""Audit why domain fixtures are excluded from the standing compile-fact QA manifest.

This is an anti-cherry-pick governance check. It does not read source prose,
QA questions, or judge outputs. It compares domain-associated typed fixtures
against the current claim-bearing compile-fact QA manifest and requires every
unmeasured associated fixture to have an explicit retained reason.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.summarize_domain_pack_status import build_report as build_domain_status_report  # noqa: E402


DEFAULT_MEASUREMENT_MANIFEST = Path("datasets/domain_pack_measurements/current_compile_fact_qa_manifest.json")
DEFAULT_EXCLUSION_MANIFEST = Path("datasets/domain_pack_measurements/current_compile_fact_qa_exclusions.json")

REASON_CODES = {
    "accountability_control_micro_fixture",
    "component_lane_fixture",
    "diagnostic_boundary_probe",
    "diagnostic_lane_not_promoted",
    "external_judged_qa_package",
    "seed_or_component_micro_fixture",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--measurement-manifest", type=Path, default=DEFAULT_MEASUREMENT_MANIFEST)
    parser.add_argument("--exclusion-manifest", type=Path, default=DEFAULT_EXCLUSION_MANIFEST)
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    parser.add_argument("--exit-zero", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = audit_manifests(
        measurement_manifest=args.measurement_manifest,
        exclusion_manifest=args.exclusion_manifest,
    )
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(report_md(report), encoding="utf-8")
    if not args.out_json and not args.out_md:
        print(json.dumps(report, indent=2, sort_keys=True))
    blocked = bool(report["summary"]["blocking_reasons"])
    return 0 if args.exit_zero or not blocked else 1


def audit_manifests(
    *,
    measurement_manifest: Path,
    exclusion_manifest: Path,
    domain_status_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    measurement_abs = _resolve_path(measurement_manifest)
    exclusion_abs = _resolve_path(exclusion_manifest)
    measurement = _load_json(measurement_abs)
    exclusions_payload = _load_json(exclusion_abs)
    if domain_status_report is None:
        domain_status_report = build_domain_status_report()

    associated = _associated_fixture_map(domain_status_report)
    measured_ids = _measured_fixture_ids(measurement)
    exclusions = _exclusion_rows(exclusions_payload)
    excluded_ids = {row["fixture_id"] for row in exclusions}

    blockers: list[str] = []
    missing_exclusions = sorted(set(associated) - measured_ids - excluded_ids)
    for fixture_id in missing_exclusions:
        blockers.append(f"{fixture_id}:associated_fixture_missing_from_manifest_and_exclusion_ledger")

    duplicate_exclusions = _duplicates([row["fixture_id"] for row in exclusions])
    for fixture_id in duplicate_exclusions:
        blockers.append(f"{fixture_id}:duplicate_exclusion_entry")

    for row in exclusions:
        fixture_id = row["fixture_id"]
        if fixture_id not in associated:
            blockers.append(f"{fixture_id}:excluded_fixture_not_domain_associated")
        if fixture_id in measured_ids:
            blockers.append(f"{fixture_id}:excluded_fixture_also_in_measurement_manifest")
        if row["reason_code"] not in REASON_CODES:
            blockers.append(f"{fixture_id}:unknown_reason_code:{row['reason_code']}")
        if not row["note"]:
            blockers.append(f"{fixture_id}:missing_note")
        if not row["status"]:
            blockers.append(f"{fixture_id}:missing_status")
        evidence_roots = row["evidence_roots"]
        if not evidence_roots:
            blockers.append(f"{fixture_id}:missing_evidence_root")
        for evidence_root in evidence_roots:
            evidence_path = _resolve_path(Path(evidence_root))
            if not evidence_path.exists():
                blockers.append(f"{fixture_id}:evidence_root_missing:{evidence_path}")
            if _is_under_repo_tmp(evidence_path):
                blockers.append(f"{fixture_id}:evidence_root_under_repo_tmp:{evidence_path}")

    reason_counts = Counter(row["reason_code"] for row in exclusions)
    return {
        "schema": "prethinker.compile_fact_qa_exclusion_audit.v1",
        "created_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "measurement_manifest": str(measurement_abs),
        "exclusion_manifest": str(exclusion_abs),
        "allowed_reason_codes": sorted(REASON_CODES),
        "summary": {
            "associated_fixture_count": len(associated),
            "measured_fixture_count": len(measured_ids),
            "excluded_fixture_count": len(excluded_ids),
            "missing_exclusion_count": len(missing_exclusions),
            "reason_counts": dict(sorted(reason_counts.items())),
            "blocking_reasons": blockers,
            "status": "pass" if not blockers else "fail",
        },
        "measured_fixtures": sorted(measured_ids),
        "excluded_fixtures": exclusions,
        "missing_exclusions": missing_exclusions,
    }


def report_md(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Compile-Fact QA Exclusion Audit",
        "",
        f"Status: `{summary['status']}`",
        f"Associated fixtures: `{summary['associated_fixture_count']}`",
        f"Measured fixtures: `{summary['measured_fixture_count']}`",
        f"Excluded fixtures: `{summary['excluded_fixture_count']}`",
        f"Missing exclusions: `{summary['missing_exclusion_count']}`",
        "",
        "## Exclusion Reasons",
        "",
        "| Reason | Count |",
        "| --- | ---: |",
    ]
    for reason, count in summary["reason_counts"].items():
        lines.append(f"| `{reason}` | {count} |")
    lines.extend(["", "## Excluded Fixtures", "", "| Fixture | Reason | Status |", "| --- | --- | --- |"])
    for row in report["excluded_fixtures"]:
        lines.append(f"| `{row['fixture_id']}` | `{row['reason_code']}` | `{row['status']}` |")
    if report["summary"]["blocking_reasons"]:
        lines.extend(["", "## Blocking Reasons", ""])
        lines.extend(f"- `{reason}`" for reason in report["summary"]["blocking_reasons"])
    lines.append("")
    return "\n".join(lines)


def _associated_fixture_map(report: dict[str, Any]) -> dict[str, str]:
    rows: dict[str, str] = {}
    for domain in report.get("domains", []):
        domain_id = str(domain.get("profile_id") or "")
        for fixture in domain.get("fixtures", []):
            fixture_id = str(fixture.get("fixture_id") or "").strip()
            if fixture_id:
                rows[fixture_id] = domain_id
    return rows


def _measured_fixture_ids(manifest: dict[str, Any]) -> set[str]:
    cells = manifest.get("cells")
    if not isinstance(cells, list) or not cells:
        raise SystemExit("Measurement manifest must contain a non-empty cells array")
    return {
        str(cell.get("fixture_id") or "").strip()
        for cell in cells
        if str(cell.get("fixture_id") or "").strip()
    }


def _exclusion_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = payload.get("exclusions")
    if not isinstance(rows, list):
        raise SystemExit("Exclusion manifest must contain an exclusions array")
    normalized: list[dict[str, Any]] = []
    for index, item in enumerate(rows, start=1):
        if not isinstance(item, dict):
            raise SystemExit(f"Exclusion entry {index} must be an object")
        evidence = item.get("evidence_roots")
        normalized.append(
            {
                "fixture_id": str(item.get("fixture_id") or "").strip(),
                "reason_code": str(item.get("reason_code") or "").strip(),
                "status": str(item.get("status") or "").strip(),
                "note": str(item.get("note") or "").strip(),
                "evidence_roots": [str(path).strip() for path in evidence] if isinstance(evidence, list) else [],
            }
        )
    return normalized


def _duplicates(values: list[str]) -> list[str]:
    counts = Counter(values)
    return sorted(value for value, count in counts.items() if value and count > 1)


def _resolve_path(path: Path) -> Path:
    if path.is_absolute():
        return path.resolve()
    return (REPO_ROOT / path).resolve()


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        raise SystemExit(f"Could not read JSON {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"Expected JSON object in {path}")
    return payload


def _is_under_repo_tmp(path: Path) -> bool:
    try:
        relative = path.resolve().relative_to(REPO_ROOT / "tmp")
    except ValueError:
        return False
    return bool(relative.parts)


if __name__ == "__main__":
    raise SystemExit(main())
