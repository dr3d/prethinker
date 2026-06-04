#!/usr/bin/env python3
"""Audit retained reference-judge null-control reports.

This is the cheap governance check for judged-QA score confidence. It does not
rerun the LLM judge. It verifies that claim-bearing judged-QA references point
at retained null-control reports whose own summaries passed.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = Path("datasets/domain_pack_measurements/current_reference_judge_null_controls.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    parser.add_argument("--exit-zero", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = audit_manifest(args.manifest)
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


def audit_manifest(manifest_path: Path) -> dict[str, Any]:
    manifest_abs = _resolve_path(manifest_path)
    payload = _load_json(manifest_abs)
    reports = payload.get("reports")
    if not isinstance(reports, list) or not reports:
        raise SystemExit(f"Manifest must contain a non-empty reports array: {manifest_abs}")

    report_rows = [_audit_report(item, index=index + 1) for index, item in enumerate(reports)]
    blockers = [reason for row in report_rows for reason in row["blocking_reasons"]]
    return {
        "schema": "prethinker.reference_judge_null_control_report_audit.v1",
        "created_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "manifest_path": str(manifest_abs),
        "manifest_schema": payload.get("schema", ""),
        "summary": {
            "report_count": len(report_rows),
            "blocking_reasons": blockers,
            "status": "pass" if not blockers else "fail",
        },
        "reports": report_rows,
    }


def _audit_report(item: dict[str, Any], *, index: int) -> dict[str, Any]:
    report_id = str(item.get("id") or f"report_{index}").strip()
    report_path = _resolve_path(Path(str(item.get("report_json") or "")))
    expect = item.get("expect") if isinstance(item.get("expect"), dict) else {}
    blockers: list[str] = []

    payload: dict[str, Any] = {}
    if not report_path.is_file():
        blockers.append(f"{report_id}:report_json_missing:{report_path}")
    elif _is_under_repo_tmp(report_path):
        blockers.append(f"{report_id}:claim_bearing_null_control_report_under_repo_tmp:{report_path}")
    else:
        payload = _load_json(report_path)

    summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else {}
    status = str(summary.get("status") or "").strip()
    if status != "pass":
        blockers.append(f"{report_id}:report_status:{status or 'missing'}")
    if int(summary.get("exact_null_verdicts") or 0) != int(expect.get("exact_null_verdicts", 0)):
        blockers.append(
            f"{report_id}:exact_null_verdicts:{summary.get('exact_null_verdicts')}:"
            f"expected:{expect.get('exact_null_verdicts', 0)}"
        )
    unclassified = summary.get("unclassified_redaction_fields")
    if isinstance(unclassified, list):
        unclassified_count = len(unclassified)
    else:
        unclassified_count = int(unclassified or 0)
    if unclassified_count != int(expect.get("unclassified_redaction_fields", 0)):
        blockers.append(
            f"{report_id}:unclassified_redaction_fields:{unclassified_count}:"
            f"expected:{expect.get('unclassified_redaction_fields', 0)}"
        )
    if int(payload.get("sample_per_fixture") or 0) < int(expect.get("sample_per_fixture") or 1):
        blockers.append(f"{report_id}:sample_per_fixture_lt_expected:{payload.get('sample_per_fixture')}")
    if int(summary.get("sampled_product_exact_rows") or 0) < int(expect.get("sampled_product_exact_rows_min") or 1):
        blockers.append(f"{report_id}:sampled_product_exact_rows_lt_expected:{summary.get('sampled_product_exact_rows')}")
    if int(summary.get("control_judgments") or 0) < int(expect.get("control_judgments_min") or 1):
        blockers.append(f"{report_id}:control_judgments_lt_expected:{summary.get('control_judgments')}")

    return {
        "id": report_id,
        "description": str(item.get("description", "")),
        "report_json": str(report_path),
        "report_schema": payload.get("schema_version", ""),
        "sample_per_fixture": int(payload.get("sample_per_fixture") or 0),
        "sampled_product_exact_rows": int(summary.get("sampled_product_exact_rows") or 0),
        "control_judgments": int(summary.get("control_judgments") or 0),
        "exact_null_verdicts": int(summary.get("exact_null_verdicts") or 0),
        "unclassified_redaction_fields": unclassified_count if "unclassified_count" in locals() else 0,
        "blocking_reasons": blockers,
    }


def report_md(report: dict[str, Any]) -> str:
    lines = [
        "# Reference Judge Null-Control Report Audit",
        "",
        f"Status: `{report['summary']['status']}`",
        f"Reports: `{report['summary']['report_count']}`",
        "",
        "| Report | Status | Sampled exact rows | Controls | Exact nulls |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for row in report["reports"]:
        status = "pass" if not row["blocking_reasons"] else "fail"
        lines.append(
            f"| `{row['id']}` | `{status}` | `{row['sampled_product_exact_rows']}` | "
            f"`{row['control_judgments']}` | `{row['exact_null_verdicts']}` |"
        )
    if report["summary"]["blocking_reasons"]:
        lines.extend(["", "## Blocking Reasons", ""])
        lines.extend(f"- `{reason}`" for reason in report["summary"]["blocking_reasons"])
    lines.append("")
    return "\n".join(lines)


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
