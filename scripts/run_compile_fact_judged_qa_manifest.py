#!/usr/bin/env python3
"""Run deterministic compile-fact judged-QA cells from a manifest."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.build_compile_fact_judged_qa import (  # noqa: E402
    _parse_domain_lens_bundles,
    build_bundle,
    write_bundle,
)
from scripts.validate_typed_micro_fixtures import DEFAULT_ROOT  # noqa: E402


DEFAULT_MANIFEST = Path("datasets/domain_pack_measurements/current_compile_fact_qa_manifest.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--fixture-root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--out-root", type=Path, required=True)
    parser.add_argument(
        "--created-utc",
        default="",
        help="Optional timestamp for reproducible tests; default is current UTC.",
    )
    parser.add_argument("--exit-zero", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    created_utc = str(args.created_utc).strip() or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    manifest = load_manifest(args.manifest)
    summary = run_manifest(
        manifest=manifest,
        manifest_path=args.manifest,
        fixture_root=args.fixture_root,
        out_root=args.out_root,
        created_utc=created_utc,
    )
    write_summary(summary=summary, out_root=args.out_root)
    blocked = bool(summary["summary"]["blocking_reasons"])
    return 0 if args.exit_zero or not blocked else 1


def load_manifest(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    cells = payload.get("cells")
    if not isinstance(cells, list) or not cells:
        raise SystemExit(f"Manifest must contain a non-empty cells array: {path}")
    return payload


def run_manifest(
    *,
    manifest: dict[str, Any],
    manifest_path: Path,
    fixture_root: Path,
    out_root: Path,
    created_utc: str,
) -> dict[str, Any]:
    out_root.mkdir(parents=True, exist_ok=True)
    cell_results: list[dict[str, Any]] = []
    blocking_reasons: list[str] = []
    for cell in manifest["cells"]:
        result = run_cell(
            cell=cell,
            fixture_root=fixture_root,
            out_root=out_root,
            created_utc=created_utc,
        )
        cell_results.append(result)
        blocking_reasons.extend(result["blocking_reasons"])
    return {
        "schema": "prethinker.compile_fact_qa_manifest_run.v1",
        "created_utc": created_utc,
        "manifest_path": str(manifest_path),
        "manifest_schema": manifest.get("schema", ""),
        "summary": {
            "cell_count": len(cell_results),
            "blocking_reasons": blocking_reasons,
            "status": "pass" if not blocking_reasons else "fail",
        },
        "cells": cell_results,
    }


def run_cell(
    *,
    cell: dict[str, Any],
    fixture_root: Path,
    out_root: Path,
    created_utc: str,
) -> dict[str, Any]:
    cell_id = _required_text(cell, "id")
    fixture_id = _required_text(cell, "fixture_id")
    cell_root = out_root / cell_id
    bundle_dir = cell_root / "judged_qa"
    reports_dir = cell_root / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    run_specs = _cell_run_specs(cell)
    bundle = build_bundle(
        fixture_root=fixture_root,
        run_specs=run_specs,
        created_utc=created_utc,
    )
    write_bundle(bundle=bundle, out_dir=bundle_dir)

    redaction = _run_audit(
        script=REPO_ROOT / "scripts" / "audit_redaction_replay.py",
        bundle_dir=bundle_dir,
        out_json=reports_dir / "redaction_replay.json",
        out_md=reports_dir / "redaction_replay.md",
    )
    typed_plan = _run_audit(
        script=REPO_ROOT / "scripts" / "audit_typed_plan_replay.py",
        bundle_dir=bundle_dir,
        out_json=reports_dir / "typed_plan_replay.json",
        out_md=reports_dir / "typed_plan_replay.md",
    )
    result = {
        "id": cell_id,
        "fixture_id": fixture_id,
        "description": str(cell.get("description", "")),
        "bundle_dir": str(bundle_dir),
        "reports_dir": str(reports_dir),
        "verdict_summary_by_file": bundle["verdict_summary_by_file"],
        "support_summary_by_fixture": bundle["support_summary_by_fixture"],
        "unexpected_same_signature_summary_by_fixture": bundle.get(
            "unexpected_same_signature_summary_by_fixture",
            {},
        ),
        "unexpected_same_signature_emissions_by_file": bundle.get(
            "unexpected_same_signature_emissions_by_file",
            {},
        ),
        "forbidden_emissions_summary_by_fixture": bundle.get(
            "forbidden_emissions_summary_by_fixture",
            {},
        ),
        "forbidden_emissions_by_file": bundle.get(
            "forbidden_emissions_by_file",
            {},
        ),
        "redaction_summary": redaction.get("summary", {}),
        "typed_plan_summary": typed_plan.get("summary", {}),
        "expect": cell.get("expect", {}),
        "blocking_reasons": [],
    }
    result["blocking_reasons"] = _blocking_reasons(result)
    return result


def write_summary(*, summary: dict[str, Any], out_root: Path) -> None:
    out_root.mkdir(parents=True, exist_ok=True)
    (out_root / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out_root / "SUMMARY.md").write_text(_summary_md(summary), encoding="utf-8")


def _cell_run_specs(cell: dict[str, Any]) -> list[dict[str, Any]]:
    fixture_id = _required_text(cell, "fixture_id")
    if cell.get("domain_lens_bundle"):
        return _parse_domain_lens_bundles([f"{fixture_id}={cell['domain_lens_bundle']}"])
    fixture_runs = cell.get("fixture_runs")
    if isinstance(fixture_runs, list) and fixture_runs:
        out: list[dict[str, Any]] = []
        for item in fixture_runs:
            out.append(
                {
                    "fixture_id": fixture_id,
                    "run_id": _required_text(item, "run_id"),
                    "compile_json": _required_text(item, "compile_json"),
                }
            )
        return out
    raise SystemExit(f"Cell must define domain_lens_bundle or fixture_runs: {cell.get('id')}")


def _run_audit(*, script: Path, bundle_dir: Path, out_json: Path, out_md: Path) -> dict[str, Any]:
    command = [
        sys.executable,
        str(script),
        str(bundle_dir),
        "--out-json",
        str(out_json),
        "--out-md",
        str(out_md),
    ]
    completed = subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True)
    if completed.returncode != 0:
        raise SystemExit(
            f"Audit failed ({script.name}) for {bundle_dir}\n"
            f"stdout:\n{completed.stdout}\n"
            f"stderr:\n{completed.stderr}"
        )
    return json.loads(out_json.read_text(encoding="utf-8"))


def _blocking_reasons(result: dict[str, Any]) -> list[str]:
    out: list[str] = []
    cell_id = result["id"]
    fixture_id = result["fixture_id"]
    support = result["support_summary_by_fixture"].get(fixture_id)
    if support is None:
        out.append(f"{cell_id}:missing_support_summary:{fixture_id}")
        support = {}
    forbidden = result.get("forbidden_emissions_summary_by_fixture", {}).get(fixture_id, {})
    if int(forbidden.get("forbidden_emissions_ge_1") or 0):
        out.append(
            f"{cell_id}:forbidden_emissions_ge_1:"
            f"{forbidden.get('forbidden_emissions_ge_1')}"
        )
    for key, expected in dict(result.get("expect") or {}).items():
        actual = _expect_actual(
            key=key,
            support=support,
            forbidden=forbidden,
            redaction=result["redaction_summary"],
            typed_plan=result["typed_plan_summary"],
        )
        if actual != expected:
            out.append(f"{cell_id}:expectation_mismatch:{key}:expected={expected}:actual={actual}")
    for audit_name, audit_summary in [
        ("redaction", result["redaction_summary"]),
        ("typed_plan", result["typed_plan_summary"]),
    ]:
        if audit_summary.get("status") != "pass":
            out.append(f"{cell_id}:{audit_name}_status:{audit_summary.get('status')}")
        if audit_summary.get("blocking_reasons"):
            out.append(f"{cell_id}:{audit_name}_blockers:{audit_summary.get('blocking_reasons')}")
    return out


def _expect_actual(
    *,
    key: str,
    support: dict[str, Any],
    forbidden: dict[str, Any],
    redaction: dict[str, Any],
    typed_plan: dict[str, Any],
) -> Any:
    if key.startswith("support."):
        return support.get(key.split(".", 1)[1])
    if key.startswith("forbidden."):
        return forbidden.get(key.split(".", 1)[1])
    if key.startswith("redaction."):
        return redaction.get(key.split(".", 1)[1])
    if key.startswith("typed_plan."):
        return typed_plan.get(key.split(".", 1)[1])
    raise SystemExit(f"Unsupported expectation key: {key}")


def _required_text(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)
    text = str(value or "").strip()
    if not text:
        raise SystemExit(f"Missing required key {key}: {payload}")
    return text


def _summary_md(summary: dict[str, Any]) -> str:
    lines = [
        "# Compile-Fact Judged QA Manifest Run",
        "",
        f"Status: `{summary['summary']['status']}`",
        f"Cells: `{summary['summary']['cell_count']}`",
        "",
    ]
    blockers = summary["summary"]["blocking_reasons"]
    if blockers:
        lines.append("## Blocking Reasons")
        lines.append("")
        lines.extend(f"- `{reason}`" for reason in blockers)
        lines.append("")
    lines.append("## Cells")
    lines.append("")
    lines.append("| Cell | Support>=2 | Forbidden | Per-run exact | Redaction | Typed plan |")
    lines.append("| --- | ---: | ---: | ---: | --- | --- |")
    for cell in summary["cells"]:
        fixture_id = cell["fixture_id"]
        support = cell["support_summary_by_fixture"].get(fixture_id, {})
        forbidden = cell.get("forbidden_emissions_summary_by_fixture", {}).get(fixture_id, {})
        support_text = f"{support.get('exact_support_ge_2', 0)} / {support.get('reference_count', 0)}"
        redaction = cell["redaction_summary"]
        typed_plan = cell["typed_plan_summary"]
        lines.append(
            "| "
            f"`{cell['id']}` | "
            f"{support_text} | "
            f"{forbidden.get('forbidden_emissions_ge_1', 0)} / {forbidden.get('forbidden_emissions_ge_2', 0)} | "
            f"{redaction.get('product_exact', 0)} / {redaction.get('row_count', 0)} | "
            f"{redaction.get('status', '')}; prose-dependent {redaction.get('prose_dependent_exact', 0)} | "
            f"{typed_plan.get('status', '')}; registered {typed_plan.get('registered_typed_plan_replayed_exact', 0)} |"
        )
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
