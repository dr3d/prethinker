import json
from pathlib import Path

from scripts.summarize_current_compile_fact_qa_status import (
    apply_markdown_freshness_check,
    build_report,
    render_markdown,
)


def test_summarize_current_compile_fact_qa_status_aggregates_manifest_run(tmp_path: Path) -> None:
    manifest_run = _write_manifest_run(tmp_path)
    source_audit = _write_source_audit(tmp_path)

    report = build_report(manifest_run_path=manifest_run, source_audit_path=source_audit)
    md = render_markdown(report)

    assert report["summary"]["status"] == "pass"
    assert report["summary"]["cell_count"] == 2
    assert report["summary"]["reference_count"] == 4
    assert report["summary"]["exact_support_ge_2"] == 3
    assert report["summary"]["per_run_rows"] == 12
    assert report["summary"]["per_run_exact"] == 8
    assert report["summary"]["unexpected_same_signature_ge_2"] == 1
    assert report["cells"][0]["unexpected_same_signature_support_ge_2"] == [
        {
            "fact": "sec_exhibit(sec_8k_material_event_001, exhibit_10_1, agreement, incorporated_by_reference, exhibit_table_row_10_1).",
            "support": 3,
        }
    ]
    assert report["summary"]["source_warning_count"] == 1
    assert "Support>=2: `3 / 4`" in md
    assert "Unexpected same-signature facts support>=2: `1`" in md
    assert "Unexpected Same-Signature Support>=2" in md
    assert "incorporated_by_reference" in md
    assert "`sec_form_8k_skeleton_seed`" in md
    assert "artifact atom pass/pass; value pass/pass" in md
    assert "lens compiles `12`" in md
    assert "missing_bundle_manifest_recovered_from_compile_json" in md


def test_summarize_current_compile_fact_qa_status_blocks_failed_source_audit(tmp_path: Path) -> None:
    manifest_run = _write_manifest_run(tmp_path)
    source_audit = _write_source_audit(tmp_path, source_status="fail")

    report = build_report(manifest_run_path=manifest_run, source_audit_path=source_audit)

    assert report["summary"]["status"] == "fail"
    assert "source_audit_status_not_pass" in report["summary"]["blocking_reasons"]


def test_summarize_current_compile_fact_qa_status_blocks_prose_dependent_rows(tmp_path: Path) -> None:
    manifest_run = _write_manifest_run(tmp_path, prose_dependent_exact=1)
    source_audit = _write_source_audit(tmp_path)

    report = build_report(manifest_run_path=manifest_run, source_audit_path=source_audit)

    assert report["summary"]["status"] == "fail"
    assert any("prose_dependent_exact" in reason for reason in report["summary"]["blocking_reasons"])


def test_compile_fact_status_markdown_freshness_check_passes_matching_doc(tmp_path: Path) -> None:
    manifest_run = _write_manifest_run(tmp_path)
    source_audit = _write_source_audit(tmp_path)
    report = build_report(manifest_run_path=manifest_run, source_audit_path=source_audit)
    rendered = render_markdown(report)
    expected = tmp_path / "CURRENT_COMPILE_FACT_QA_STATUS.md"
    expected.write_text(rendered, encoding="utf-8")

    apply_markdown_freshness_check(report=report, expected_path=expected, rendered_md=rendered)

    assert report["summary"]["status"] == "pass"
    assert not report["summary"]["blocking_reasons"]


def test_compile_fact_status_markdown_freshness_check_blocks_stale_doc(tmp_path: Path) -> None:
    manifest_run = _write_manifest_run(tmp_path)
    source_audit = _write_source_audit(tmp_path)
    report = build_report(manifest_run_path=manifest_run, source_audit_path=source_audit)
    expected = tmp_path / "CURRENT_COMPILE_FACT_QA_STATUS.md"
    expected.write_text("# old\n", encoding="utf-8")

    apply_markdown_freshness_check(
        report=report,
        expected_path=expected,
        rendered_md=render_markdown(report),
    )

    assert report["summary"]["status"] == "fail"
    assert any("expected_markdown_stale" in reason for reason in report["summary"]["blocking_reasons"])


def _write_manifest_run(tmp_path: Path, *, prose_dependent_exact: int = 0) -> Path:
    path = tmp_path / "manifest_run.json"
    path.write_text(
        json.dumps(
            {
                "summary": {"status": "pass"},
                "cells": [
                    _cell(
                        cell_id="sec_form_8k_skeleton_seed",
                        fixture_id="sec_form_8k_skeleton_v1",
                        reference_count=2,
                        exact_support_ge_2=2,
                        verdict_summary={
                            "run1.json": {"exact": 2},
                            "run2.json": {"exact": 1, "partial": 1},
                            "run3.json": {"exact": 2},
                        },
                        prose_dependent_exact=prose_dependent_exact,
                        unexpected_same_signature_ge_2=1,
                    ),
                    _cell(
                        cell_id="osha_incident_transfer_001",
                        fixture_id="osha_incident_transfer_001",
                        reference_count=2,
                        exact_support_ge_2=1,
                        verdict_summary={
                            "run1.json": {"exact": 1, "miss": 1},
                            "run2.json": {"exact": 1, "miss": 1},
                            "run3.json": {"exact": 1, "miss": 1},
                        },
                        prose_dependent_exact=0,
                        unexpected_same_signature_ge_2=0,
                    ),
                ],
            }
        ),
        encoding="utf-8",
    )
    return path


def _write_source_audit(tmp_path: Path, *, source_status: str = "pass") -> Path:
    path = tmp_path / "source_audit.json"
    path.write_text(
        json.dumps(
            {
                "summary": {"status": source_status},
                "cells": [
                    _source_cell(
                        "sec_form_8k_skeleton_seed",
                        warning="sec_form_8k_skeleton_seed:missing_bundle_manifest_recovered_from_compile_json",
                    ),
                    _source_cell("osha_incident_transfer_001"),
                ],
            }
        ),
        encoding="utf-8",
    )
    return path


def _cell(
    *,
    cell_id: str,
    fixture_id: str,
    reference_count: int,
    exact_support_ge_2: int,
    verdict_summary: dict,
    prose_dependent_exact: int,
    unexpected_same_signature_ge_2: int,
) -> dict:
    row_count = sum(sum(counts.values()) for counts in verdict_summary.values())
    exact = sum(int(counts.get("exact") or 0) for counts in verdict_summary.values())
    return {
        "id": cell_id,
        "fixture_id": fixture_id,
        "description": "test cell",
        "support_summary_by_fixture": {
            fixture_id: {
                "reference_count": reference_count,
                "exact_support_ge_2": exact_support_ge_2,
                "runs_seen": 3,
            }
        },
        "unexpected_same_signature_summary_by_fixture": {
            fixture_id: {
                "runs_seen": 3,
                "unexpected_same_signature_ge_1": unexpected_same_signature_ge_2,
                "unexpected_same_signature_ge_2": unexpected_same_signature_ge_2,
            }
        },
        "unexpected_same_signature_emissions_by_file": _unexpected_emissions(
            unexpected_same_signature_ge_2
        ),
        "redaction_summary": {
            "status": "pass",
            "row_count": row_count,
            "product_exact": exact,
            "prose_dependent_exact": prose_dependent_exact,
        },
        "typed_plan_summary": {
            "status": "pass",
            "registered_typed_plan_replayed_exact": exact,
            "unregistered_plan_exact_rows": 0,
        },
        "verdict_summary_by_file": verdict_summary,
    }


def _unexpected_emissions(unexpected_same_signature_ge_2: int) -> dict:
    if not unexpected_same_signature_ge_2:
        return {}
    fact = "sec_exhibit(sec_8k_material_event_001, exhibit_10_1, agreement, incorporated_by_reference, exhibit_table_row_10_1)."
    return {
        "run1.json": [fact],
        "run2.json": [fact],
        "run3.json": [fact],
    }


def _source_cell(cell_id: str, *, warning: str = "") -> dict:
    warnings = [warning] if warning else []
    return {
        "id": cell_id,
        "source_root": "C:\\prethinker_tmp_archive\\example",
        "bundle_manifest_status": "present",
        "run_count": 3,
        "lens_compile_count": 12,
        "warnings": warnings,
        "artifact_gate_summaries": {
            "lens_atom_inventory": {"status": "pass"},
            "union_atom_inventory": {"status": "pass"},
            "lens_value_domains": {"status": "pass"},
            "union_value_domains": {"status": "pass"},
        },
        "effective_settings": {
            "backend": "lmstudio",
            "model": "qwen/qwen3.6-35b-a3b",
            "temperature": 0.0,
            "top_p": 1.0,
            "num_ctx": 65536,
            "support_threshold": 2,
            "matcher": "constant_slot",
            "quantization": "Q4_K_M",
        },
    }
