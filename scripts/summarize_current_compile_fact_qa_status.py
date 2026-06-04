#!/usr/bin/env python3
"""Summarize the current compile-fact QA manifest run.

This report is intentionally downstream of two governed artifacts:

1. run_compile_fact_judged_qa_manifest.py output, which deterministically
   compares expected typed facts to emitted typed compile facts; and
2. audit_compile_fact_qa_manifest_sources.py output, which checks retained roots
   and effective inference settings.

It does not read source prose, call an LLM, or invoke a judge.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.report_freshness import apply_markdown_freshness_check


DEFAULT_MANIFEST_RUN = Path("tmp/compile_fact_qa_manifest_run/summary.json")
DEFAULT_SOURCE_AUDIT = Path("tmp/compile_fact_manifest_sources.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest-run", type=Path, default=DEFAULT_MANIFEST_RUN)
    parser.add_argument("--source-audit", type=Path, default=DEFAULT_SOURCE_AUDIT)
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    parser.add_argument(
        "--expect-md",
        type=Path,
        default=None,
        help="Fail if this markdown file differs from the freshly rendered report.",
    )
    parser.add_argument("--exit-zero", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(
        manifest_run_path=args.manifest_run,
        source_audit_path=args.source_audit,
    )
    rendered_md = render_markdown(report)
    if args.expect_md:
        apply_markdown_freshness_check(
            report=report,
            expected_path=args.expect_md,
            rendered_md=rendered_md,
        )
        rendered_md = render_markdown(report)
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(rendered_md, encoding="utf-8")
    if not args.out_json and not args.out_md:
        print(json.dumps(report, indent=2, sort_keys=True))
    blocked = report["summary"]["status"] != "pass"
    return 0 if args.exit_zero or not blocked else 1


def build_report(*, manifest_run_path: Path, source_audit_path: Path) -> dict[str, Any]:
    manifest_run = _load_json(manifest_run_path)
    source_audit = _load_json(source_audit_path)
    source_by_id = {
        str(cell.get("id") or ""): cell
        for cell in source_audit.get("cells", [])
        if isinstance(cell, dict)
    }
    cells = [
        _cell_row(cell=cell, source=source_by_id.get(str(cell.get("id") or ""), {}))
        for cell in manifest_run.get("cells", [])
        if isinstance(cell, dict)
    ]
    families = _family_rows(cells)
    blockers = _blocking_reasons(
        manifest_run=manifest_run,
        source_audit=source_audit,
        cells=cells,
    )
    return {
        "schema": "prethinker.current_compile_fact_qa_status.v1",
        "created_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "manifest_run_path": str(manifest_run_path),
        "source_audit_path": str(source_audit_path),
        "summary": {
            "status": "pass" if not blockers else "fail",
            "blocking_reasons": blockers,
            "cell_count": len(cells),
            "family_count": len(families),
            "reference_count": sum(int(cell["reference_count"]) for cell in cells),
            "exact_support_ge_2": sum(int(cell["exact_support_ge_2"]) for cell in cells),
            "per_run_rows": sum(int(cell["per_run_rows"]) for cell in cells),
            "per_run_exact": sum(int(cell["per_run_exact"]) for cell in cells),
            "prose_dependent_exact": sum(int(cell["prose_dependent_exact"]) for cell in cells),
            "unregistered_plan_exact_rows": sum(
                int(cell["unregistered_plan_exact_rows"]) for cell in cells
            ),
            "source_warning_count": sum(int(cell["source_warning_count"]) for cell in cells),
        },
        "families": families,
        "cells": cells,
    }


def _cell_row(*, cell: dict[str, Any], source: dict[str, Any]) -> dict[str, Any]:
    cell_id = str(cell.get("id") or "")
    fixture_id = str(cell.get("fixture_id") or "")
    support = dict((cell.get("support_summary_by_fixture") or {}).get(fixture_id) or {})
    redaction = dict(cell.get("redaction_summary") or {})
    typed_plan = dict(cell.get("typed_plan_summary") or {})
    per_run_counts = _per_run_counts(cell.get("verdict_summary_by_file") or {})
    settings = dict(source.get("effective_settings") or {})
    return {
        "id": cell_id,
        "family": _family_for_cell(cell_id=cell_id, fixture_id=fixture_id),
        "fixture_id": fixture_id,
        "description": str(cell.get("description") or ""),
        "reference_count": int(support.get("reference_count") or 0),
        "exact_support_ge_2": int(support.get("exact_support_ge_2") or 0),
        "runs_seen": int(support.get("runs_seen") or source.get("run_count") or 0),
        "per_run_rows": int(per_run_counts["rows"]),
        "per_run_exact": int(per_run_counts["exact"]),
        "per_run_partial": int(per_run_counts["partial"]),
        "per_run_miss": int(per_run_counts["miss"]),
        "redaction_status": str(redaction.get("status") or ""),
        "prose_dependent_exact": int(redaction.get("prose_dependent_exact") or 0),
        "typed_plan_status": str(typed_plan.get("status") or ""),
        "registered_typed_plan_replayed_exact": int(
            typed_plan.get("registered_typed_plan_replayed_exact") or 0
        ),
        "unregistered_plan_exact_rows": int(typed_plan.get("unregistered_plan_exact_rows") or 0),
        "source_root": str(source.get("source_root") or ""),
        "bundle_manifest_status": str(source.get("bundle_manifest_status") or ""),
        "source_warning_count": len(source.get("warnings") or []),
        "source_warnings": list(source.get("warnings") or []),
        "backend": str(settings.get("backend") or ""),
        "model": str(settings.get("model") or ""),
        "temperature": settings.get("temperature", ""),
        "top_p": settings.get("top_p", ""),
        "num_ctx": settings.get("num_ctx", ""),
        "support_threshold": settings.get("support_threshold", ""),
        "matcher": str(settings.get("matcher") or ""),
        "quantization": str(settings.get("quantization") or ""),
    }


def _per_run_counts(verdict_summary_by_file: dict[str, Any]) -> dict[str, int]:
    totals = {"rows": 0, "exact": 0, "partial": 0, "miss": 0}
    for counts in verdict_summary_by_file.values():
        if not isinstance(counts, dict):
            continue
        exact = int(counts.get("exact") or 0)
        partial = int(counts.get("partial") or 0)
        miss = int(counts.get("miss") or 0)
        other = sum(
            int(value or 0)
            for key, value in counts.items()
            if str(key) not in {"exact", "partial", "miss"}
        )
        totals["exact"] += exact
        totals["partial"] += partial
        totals["miss"] += miss
        totals["rows"] += exact + partial + miss + other
    return totals


def _family_rows(cells: list[dict[str, Any]]) -> list[dict[str, Any]]:
    families: dict[str, dict[str, Any]] = {}
    for cell in cells:
        family = cell["family"]
        row = families.setdefault(
            family,
            {
                "family": family,
                "cell_count": 0,
                "reference_count": 0,
                "exact_support_ge_2": 0,
                "per_run_rows": 0,
                "per_run_exact": 0,
                "prose_dependent_exact": 0,
                "unregistered_plan_exact_rows": 0,
            },
        )
        row["cell_count"] += 1
        row["reference_count"] += int(cell["reference_count"])
        row["exact_support_ge_2"] += int(cell["exact_support_ge_2"])
        row["per_run_rows"] += int(cell["per_run_rows"])
        row["per_run_exact"] += int(cell["per_run_exact"])
        row["prose_dependent_exact"] += int(cell["prose_dependent_exact"])
        row["unregistered_plan_exact_rows"] += int(cell["unregistered_plan_exact_rows"])
    return [families[key] for key in sorted(families)]


def _blocking_reasons(
    *,
    manifest_run: dict[str, Any],
    source_audit: dict[str, Any],
    cells: list[dict[str, Any]],
) -> list[str]:
    blockers: list[str] = []
    if (manifest_run.get("summary") or {}).get("status") != "pass":
        blockers.append("manifest_run_status_not_pass")
    if (source_audit.get("summary") or {}).get("status") != "pass":
        blockers.append("source_audit_status_not_pass")
    for cell in cells:
        cell_id = cell["id"]
        if cell["redaction_status"] != "pass":
            blockers.append(f"{cell_id}:redaction_status:{cell['redaction_status']}")
        if cell["typed_plan_status"] != "pass":
            blockers.append(f"{cell_id}:typed_plan_status:{cell['typed_plan_status']}")
        if cell["prose_dependent_exact"]:
            blockers.append(f"{cell_id}:prose_dependent_exact:{cell['prose_dependent_exact']}")
        if cell["unregistered_plan_exact_rows"]:
            blockers.append(
                f"{cell_id}:unregistered_plan_exact_rows:{cell['unregistered_plan_exact_rows']}"
            )
    return blockers


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Current Compile-Fact QA Status",
        "",
        "Generated from the current compile-fact QA manifest run and manifest source/settings audit.",
        "This page does not read source prose, call an LLM, or judge messy human questions.",
        "",
        "## Summary",
        "",
        f"- Status: `{summary['status']}`",
        f"- Cells: `{summary['cell_count']}` across `{summary['family_count']}` families",
        f"- Support>=2: `{summary['exact_support_ge_2']} / {summary['reference_count']}` expected typed facts",
        f"- Per-run exact: `{summary['per_run_exact']} / {summary['per_run_rows']}` deterministic fact rows",
        f"- Prose-dependent exact rows: `{summary['prose_dependent_exact']}`",
        f"- Unregistered exact typed plans: `{summary['unregistered_plan_exact_rows']}`",
        f"- Source/provenance warnings: `{summary['source_warning_count']}`",
        "",
    ]
    if summary["blocking_reasons"]:
        lines.extend(["## Blocking Reasons", ""])
        lines.extend(f"- `{reason}`" for reason in summary["blocking_reasons"])
        lines.append("")
    lines.extend(
        [
            "## By Family",
            "",
            "| Family | Cells | Support>=2 | Per-run exact | Prose-dependent | Unregistered plans |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for family in report["families"]:
        lines.append(
            "| `{}` | {} | {} / {} | {} / {} | {} | {} |".format(
                family["family"],
                family["cell_count"],
                family["exact_support_ge_2"],
                family["reference_count"],
                family["per_run_exact"],
                family["per_run_rows"],
                family["prose_dependent_exact"],
                family["unregistered_plan_exact_rows"],
            )
        )
    lines.extend(
        [
            "",
            "## Cells",
            "",
            "| Cell | Fixture | Support>=2 | Per-run exact | Replay gates | Source metadata |",
            "| --- | --- | ---: | ---: | --- | --- |",
        ]
    )
    for cell in report["cells"]:
        replay = (
            f"redaction `{cell['redaction_status']}` / prose `{cell['prose_dependent_exact']}`; "
            f"typed-plan `{cell['typed_plan_status']}` / unregistered `{cell['unregistered_plan_exact_rows']}`"
        )
        source = (
            f"`{cell['backend']}` `{cell['model']}`; temp `{cell['temperature']}`; "
            f"top_p `{cell['top_p']}`; ctx `{cell['num_ctx']}`; matcher `{cell['matcher']}`; "
            f"manifest `{cell['bundle_manifest_status']}`"
        )
        lines.append(
            "| `{}` | `{}` | {} / {} | {} / {} | {} | {} |".format(
                cell["id"],
                cell["fixture_id"],
                cell["exact_support_ge_2"],
                cell["reference_count"],
                cell["per_run_exact"],
                cell["per_run_rows"],
                replay,
                source,
            )
        )
    warnings = [warning for cell in report["cells"] for warning in cell.get("source_warnings", [])]
    if warnings:
        lines.extend(["", "## Source Warnings", ""])
        lines.extend(f"- `{warning}`" for warning in warnings)
        lines.append("")
    described_cells = [cell for cell in report["cells"] if cell.get("description")]
    if described_cells:
        lines.extend(
            [
                "",
                "## Cell Notes",
                "",
                "| Cell | Note |",
                "| --- | --- |",
            ]
        )
        for cell in described_cells:
            note = str(cell["description"]).replace("|", "\\|")
            lines.append(f"| `{cell['id']}` | {note} |")
        lines.append("")
    return "\n".join(lines) + "\n"


def _family_for_cell(*, cell_id: str, fixture_id: str) -> str:
    text = f"{cell_id} {fixture_id}".lower()
    for prefix, family in [
        ("sec_", "sec_form_8k"),
        ("fda_", "fda_warning_letter"),
        ("ntsb_", "ntsb_investigation"),
        ("osha_", "osha_incident"),
    ]:
        if prefix in text:
            return family
    return "other"


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise SystemExit(f"Cannot read JSON file {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Cannot parse JSON file {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"JSON file must contain an object: {path}")
    return payload


if __name__ == "__main__":
    raise SystemExit(main())
