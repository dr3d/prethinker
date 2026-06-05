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
        _cell_row(
            cell=cell,
            source=source_by_id.get(str(cell.get("id") or ""), {}),
            manifest_root=manifest_run_path.parent,
        )
        for cell in manifest_run.get("cells", [])
        if isinstance(cell, dict)
    ]
    families = _family_rows(cells)
    unsupported_by_carrier = _unsupported_by_carrier_rows(cells)
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
            "unexpected_same_signature_ge_2": sum(
                int(cell["unexpected_same_signature_ge_2"]) for cell in cells
            ),
            "forbidden_emissions_ge_1": sum(int(cell["forbidden_emissions_ge_1"]) for cell in cells),
            "forbidden_emissions_ge_2": sum(int(cell["forbidden_emissions_ge_2"]) for cell in cells),
            "prose_dependent_exact": sum(int(cell["prose_dependent_exact"]) for cell in cells),
            "unregistered_plan_exact_rows": sum(
                int(cell["unregistered_plan_exact_rows"]) for cell in cells
            ),
            "source_warning_count": sum(int(cell["source_warning_count"]) for cell in cells),
            "unsupported_expected_fact_count": sum(
                len(cell.get("unsupported_expected_facts") or []) for cell in cells
            ),
            "unsupported_support_0_count": sum(
                1
                for cell in cells
                for row in cell.get("unsupported_expected_facts") or []
                if int(row.get("exact_support") or 0) <= 0
            ),
            "unsupported_support_1_count": sum(
                1
                for cell in cells
                for row in cell.get("unsupported_expected_facts") or []
                if int(row.get("exact_support") or 0) == 1
            ),
        },
        "families": families,
        "unsupported_by_carrier": unsupported_by_carrier,
        "cells": cells,
    }


def _cell_row(*, cell: dict[str, Any], source: dict[str, Any], manifest_root: Path) -> dict[str, Any]:
    cell_id = str(cell.get("id") or "")
    fixture_id = str(cell.get("fixture_id") or "")
    support = dict((cell.get("support_summary_by_fixture") or {}).get(fixture_id) or {})
    unexpected = dict(
        (cell.get("unexpected_same_signature_summary_by_fixture") or {}).get(fixture_id) or {}
    )
    unexpected_support = _unexpected_same_signature_support(
        cell.get("unexpected_same_signature_emissions_by_file") or {}
    )
    forbidden = dict((cell.get("forbidden_emissions_summary_by_fixture") or {}).get(fixture_id) or {})
    forbidden_support = _forbidden_emission_support(
        cell.get("forbidden_emissions_by_file") or {}
    )
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
        "unexpected_same_signature_ge_2": int(unexpected.get("unexpected_same_signature_ge_2") or 0),
        "unexpected_same_signature_ge_1": int(unexpected.get("unexpected_same_signature_ge_1") or 0),
        "unexpected_same_signature_support_ge_2": unexpected_support,
        "forbidden_emissions_ge_1": int(forbidden.get("forbidden_emissions_ge_1") or 0),
        "forbidden_emissions_ge_2": int(forbidden.get("forbidden_emissions_ge_2") or 0),
        "forbidden_emissions_support_ge_1": forbidden_support,
        "redaction_status": str(redaction.get("status") or ""),
        "prose_dependent_exact": int(redaction.get("prose_dependent_exact") or 0),
        "typed_plan_status": str(typed_plan.get("status") or ""),
        "registered_typed_plan_replayed_exact": int(
            typed_plan.get("registered_typed_plan_replayed_exact") or 0
        ),
        "unregistered_plan_exact_rows": int(typed_plan.get("unregistered_plan_exact_rows") or 0),
        "source_root": str(source.get("source_root") or ""),
        "bundle_manifest_status": str(source.get("bundle_manifest_status") or ""),
        "lens_compile_count": int(source.get("lens_compile_count") or 0),
        "artifact_gate_status": _artifact_gate_status(source.get("artifact_gate_summaries") or {}),
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
        "unsupported_expected_facts": _unsupported_expected_facts(
            manifest_root=manifest_root,
            cell_id=cell_id,
        ),
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


def _unexpected_same_signature_support(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, dict):
        return []
    counts: dict[str, int] = {}
    for emissions in value.values():
        if not isinstance(emissions, list):
            continue
        for fact in {str(item).strip() for item in emissions if str(item).strip()}:
            counts[fact] = counts.get(fact, 0) + 1
    rows = [
        {"fact": fact, "support": support}
        for fact, support in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
        if support >= 2
    ]
    return rows


def _forbidden_emission_support(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, dict):
        return []
    counts: dict[str, int] = {}
    compiled: dict[str, set[str]] = {}
    for emissions in value.values():
        if not isinstance(emissions, list):
            continue
        run_facts: dict[str, set[str]] = {}
        for item in emissions:
            if not isinstance(item, dict):
                continue
            forbidden_fact = str(item.get("forbidden_fact") or "").strip()
            compiled_fact = str(item.get("compiled_fact") or "").strip()
            if not forbidden_fact:
                continue
            run_facts.setdefault(forbidden_fact, set())
            if compiled_fact:
                run_facts[forbidden_fact].add(compiled_fact)
        for forbidden_fact, compiled_facts in run_facts.items():
            counts[forbidden_fact] = counts.get(forbidden_fact, 0) + 1
            compiled.setdefault(forbidden_fact, set()).update(compiled_facts)
    return [
        {
            "forbidden_fact": forbidden_fact,
            "support": support,
            "compiled_facts": sorted(compiled.get(forbidden_fact, set())),
        }
        for forbidden_fact, support in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    ]


def _unsupported_expected_facts(*, manifest_root: Path, cell_id: str) -> list[dict[str, Any]]:
    judged_dir = manifest_root / cell_id / "judged_qa"
    if not judged_dir.exists():
        return []
    by_reference: dict[str, dict[str, Any]] = {}
    for path in sorted(judged_dir.glob("*__run*__judged_qa.json")):
        payload = _load_json(path)
        run_id = str(payload.get("run_id") or path.stem)
        for row in payload.get("rows") or []:
            if not isinstance(row, dict):
                continue
            reference = str(row.get("reference_answer") or "").strip()
            if not reference:
                continue
            item = by_reference.setdefault(
                reference,
                {
                    "reference_answer": reference,
                    "carrier": str(row.get("reference_answer_carrier") or ""),
                    "exact_support": 0,
                    "verdicts": [],
                    "non_exact_answers": [],
                },
            )
            verdict = str((row.get("reference_judge") or {}).get("verdict") or "")
            item["verdicts"].append({"run": run_id, "verdict": verdict})
            if verdict == "exact":
                item["exact_support"] += 1
            else:
                answer = str(row.get("answer") or "").strip()
                if answer:
                    item["non_exact_answers"].append(answer)
    unsupported = [
        {
            "reference_answer": item["reference_answer"],
            "carrier": item["carrier"],
            "exact_support": item["exact_support"],
            "verdicts": item["verdicts"],
            "non_exact_answers": sorted(set(item["non_exact_answers"]))[:3],
        }
        for item in by_reference.values()
        if int(item["exact_support"]) < 2
    ]
    return sorted(
        unsupported,
        key=lambda item: (
            int(item["exact_support"]),
            str(item.get("carrier") or ""),
            str(item.get("reference_answer") or ""),
        ),
    )


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
                "unexpected_same_signature_ge_2": 0,
                "forbidden_emissions_ge_1": 0,
                "forbidden_emissions_ge_2": 0,
                "prose_dependent_exact": 0,
                "unregistered_plan_exact_rows": 0,
            },
        )
        row["cell_count"] += 1
        row["reference_count"] += int(cell["reference_count"])
        row["exact_support_ge_2"] += int(cell["exact_support_ge_2"])
        row["per_run_rows"] += int(cell["per_run_rows"])
        row["per_run_exact"] += int(cell["per_run_exact"])
        row["unexpected_same_signature_ge_2"] += int(cell["unexpected_same_signature_ge_2"])
        row["forbidden_emissions_ge_1"] += int(cell["forbidden_emissions_ge_1"])
        row["forbidden_emissions_ge_2"] += int(cell["forbidden_emissions_ge_2"])
        row["prose_dependent_exact"] += int(cell["prose_dependent_exact"])
        row["unregistered_plan_exact_rows"] += int(cell["unregistered_plan_exact_rows"])
    return [families[key] for key in sorted(families)]


def _unsupported_by_carrier_rows(cells: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str], dict[str, Any]] = {}
    for cell in cells:
        family = str(cell.get("family") or "other")
        for row in cell.get("unsupported_expected_facts") or []:
            carrier = str(row.get("carrier") or "unknown")
            key = (family, carrier)
            group = groups.setdefault(
                key,
                {
                    "family": family,
                    "carrier": carrier,
                    "unsupported_count": 0,
                    "support_0_count": 0,
                    "support_1_count": 0,
                    "cells": set(),
                },
            )
            support = int(row.get("exact_support") or 0)
            group["unsupported_count"] += 1
            if support <= 0:
                group["support_0_count"] += 1
            elif support == 1:
                group["support_1_count"] += 1
            group["cells"].add(str(cell.get("id") or ""))
    rows: list[dict[str, Any]] = []
    for group in groups.values():
        rows.append(
            {
                "family": group["family"],
                "carrier": group["carrier"],
                "unsupported_count": group["unsupported_count"],
                "support_0_count": group["support_0_count"],
                "support_1_count": group["support_1_count"],
                "cell_count": len(group["cells"]),
                "cells": sorted(group["cells"]),
            }
        )
    return sorted(
        rows,
        key=lambda row: (
            str(row["family"]),
            -int(row["unsupported_count"]),
            str(row["carrier"]),
        ),
    )


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
        if cell["forbidden_emissions_ge_1"]:
            blockers.append(f"{cell_id}:forbidden_emissions_ge_1:{cell['forbidden_emissions_ge_1']}")
    return blockers


def _artifact_gate_status(gate_summaries: dict[str, Any]) -> str:
    if not gate_summaries:
        return "not_available"
    atom_status = _paired_gate_status(
        gate_summaries,
        ("lens_atom_inventory", "union_atom_inventory"),
    )
    value_status = _paired_gate_status(
        gate_summaries,
        ("lens_value_domains", "union_value_domains"),
    )
    return f"artifact atom {atom_status}; value {value_status}"


def _paired_gate_status(gate_summaries: dict[str, Any], summary_keys: tuple[str, str]) -> str:
    statuses: list[str] = []
    for summary_key in summary_keys:
        summary = gate_summaries.get(summary_key)
        if isinstance(summary, dict):
            statuses.append(str(summary.get("status") or "unknown"))
        else:
            statuses.append("missing")
    return "/".join(statuses)


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
        f"- Unexpected same-signature facts support>=2: `{summary['unexpected_same_signature_ge_2']}`",
        f"- Forbidden fact emissions support>=1 / support>=2: `{summary['forbidden_emissions_ge_1']} / {summary['forbidden_emissions_ge_2']}`",
        f"- Prose-dependent exact rows: `{summary['prose_dependent_exact']}`",
        f"- Unregistered exact typed plans: `{summary['unregistered_plan_exact_rows']}`",
        f"- Source/provenance warnings: `{summary['source_warning_count']}`",
        f"- Unsupported expected facts support<2: `{summary['unsupported_expected_fact_count']}`",
        f"- Unsupported split support 0 / support 1: `{summary['unsupported_support_0_count']} / {summary['unsupported_support_1_count']}`",
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
            "| Family | Cells | Support>=2 | Per-run exact | Unexpected>=2 | Forbidden | Prose-dependent | Unregistered plans |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for family in report["families"]:
        lines.append(
            "| `{}` | {} | {} / {} | {} / {} | {} | {} / {} | {} | {} |".format(
                family["family"],
                family["cell_count"],
                family["exact_support_ge_2"],
                family["reference_count"],
                family["per_run_exact"],
                family["per_run_rows"],
                family["unexpected_same_signature_ge_2"],
                family["forbidden_emissions_ge_1"],
                family["forbidden_emissions_ge_2"],
                family["prose_dependent_exact"],
                family["unregistered_plan_exact_rows"],
            )
        )
    lines.extend(
        [
            "",
            "## Cells",
            "",
            "| Cell | Fixture | Support>=2 | Per-run exact | Unexpected>=2 | Forbidden | Replay gates | Source metadata |",
            "| --- | --- | ---: | ---: | ---: | ---: | --- | --- |",
        ]
    )
    for cell in report["cells"]:
        replay = (
            f"redaction `{cell['redaction_status']}` / prose `{cell['prose_dependent_exact']}`; "
            f"typed-plan `{cell['typed_plan_status']}` / unregistered `{cell['unregistered_plan_exact_rows']}`; "
            f"{cell['artifact_gate_status']}"
        )
        source = (
            f"`{cell['backend']}` `{cell['model']}`; temp `{cell['temperature']}`; "
            f"top_p `{cell['top_p']}`; ctx `{cell['num_ctx']}`; matcher `{cell['matcher']}`; "
            f"lens compiles `{cell['lens_compile_count']}`; manifest `{cell['bundle_manifest_status']}`"
        )
        lines.append(
            "| `{}` | `{}` | {} / {} | {} / {} | {} | {} | {} | {} |".format(
                cell["id"],
                cell["fixture_id"],
                cell["exact_support_ge_2"],
                cell["reference_count"],
                cell["per_run_exact"],
                cell["per_run_rows"],
                cell["unexpected_same_signature_ge_2"],
                f"{cell['forbidden_emissions_ge_1']} / {cell['forbidden_emissions_ge_2']}",
                replay,
                source,
            )
        )
    unsupported_rows = [
        (cell, row)
        for cell in report["cells"]
        for row in cell.get("unsupported_expected_facts") or []
    ]
    if unsupported_rows:
        lines.extend(
            [
                "",
                "## Unsupported Expected Facts",
                "",
                "These rows are the current coverage boundary: expected typed facts",
                "with exact support below the claim threshold of 2. They are",
                "diagnostic planning data, not permission to repair rows one by one.",
                "",
            ]
        )
        carrier_rows = report.get("unsupported_by_carrier") or []
        if carrier_rows:
            lines.extend(
                [
                    "### By Carrier",
                    "",
                    "| Family | Carrier | Unsupported | Support 0 | Support 1 | Cells |",
                    "| --- | --- | ---: | ---: | ---: | --- |",
                ]
            )
            for row in carrier_rows:
                cells = ", ".join(f"`{cell}`" for cell in row.get("cells") or [])
                lines.append(
                    "| `{}` | `{}` | {} | {} | {} | {} |".format(
                        row.get("family") or "",
                        row.get("carrier") or "",
                        row.get("unsupported_count", 0),
                        row.get("support_0_count", 0),
                        row.get("support_1_count", 0),
                        cells,
                    )
                )
        lines.extend(
            [
                "",
                "### Rows",
                "",
                "| Cell | Fixture | Carrier | Support | Verdicts | Expected Fact | Non-Exact Emissions |",
                "| --- | --- | --- | ---: | --- | --- | --- |",
            ]
        )
        for cell, row in unsupported_rows:
            verdicts = ", ".join(
                f"{item.get('run')}: {item.get('verdict')}"
                for item in row.get("verdicts") or []
            ).replace("|", "\\|")
            expected = str(row.get("reference_answer") or "").replace("|", "\\|")
            answers = "; ".join(str(item) for item in row.get("non_exact_answers") or [])
            answers = answers.replace("|", "\\|")
            lines.append(
                "| `{}` | `{}` | `{}` | {} | {} | `{}` | `{}` |".format(
                    cell["id"],
                    cell["fixture_id"],
                    row.get("carrier") or "",
                    row.get("exact_support", 0),
                    verdicts,
                    expected,
                    answers,
                )
            )
    forbidden_rows = [
        (cell, row)
        for cell in report["cells"]
        for row in cell.get("forbidden_emissions_support_ge_1", [])
    ]
    if forbidden_rows:
        lines.extend(
            [
                "",
                "## Forbidden Fact Emissions",
                "",
                "These rows are source-rejected facts that the compiler still emitted.",
                "Any occurrence blocks claim-bearing status for the cell.",
                "",
                "| Cell | Fixture | Support | Forbidden Fact | Compiled Fact(s) |",
                "| --- | --- | ---: | --- | --- |",
            ]
        )
        for cell, row in forbidden_rows:
            forbidden_fact = str(row.get("forbidden_fact") or "").replace("|", "\\|")
            compiled_facts = "; ".join(str(item) for item in row.get("compiled_facts") or [])
            compiled_facts = compiled_facts.replace("|", "\\|")
            lines.append(
                "| `{}` | `{}` | {} | `{}` | `{}` |".format(
                    cell["id"],
                    cell["fixture_id"],
                    row.get("support", 0),
                    forbidden_fact,
                    compiled_facts,
                )
            )
    unexpected_rows = [
        (cell, row)
        for cell in report["cells"]
        for row in cell.get("unexpected_same_signature_support_ge_2", [])
    ]
    if unexpected_rows:
        lines.extend(
            [
                "",
                "## Unexpected Same-Signature Support>=2",
                "",
                "These rows are precision-pressure diagnostics only. They are not",
                "promoted expected facts unless an independent source-only oracle",
                "adds them to the fixture.",
                "",
                "| Cell | Fixture | Support | Fact |",
                "| --- | --- | ---: | --- |",
            ]
        )
        for cell, row in unexpected_rows:
            fact = str(row.get("fact") or "").replace("|", "\\|")
            lines.append(
                "| `{}` | `{}` | {} | `{}` |".format(
                    cell["id"],
                    cell["fixture_id"],
                    row.get("support", 0),
                    fact,
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
