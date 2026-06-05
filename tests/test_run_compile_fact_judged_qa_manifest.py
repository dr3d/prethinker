import json
from pathlib import Path

from scripts.run_compile_fact_judged_qa_manifest import run_manifest, write_summary


def test_run_compile_fact_judged_qa_manifest_end_to_end(tmp_path: Path) -> None:
    fixture_root = tmp_path / "fixtures"
    fixture_dir = fixture_root / "fixture_a"
    fixture_dir.mkdir(parents=True)
    (fixture_dir / "expected_facts.pl").write_text(
        "fda_warning_letter(Letter, cder, apothecary_pharma_llc, v_2025_12_01, SrcLetter).\n",
        encoding="utf-8",
    )

    bundle_root = tmp_path / "bundle"
    for run_id in ["run1", "run2"]:
        run_dir = bundle_root / "unions" / run_id
        run_dir.mkdir(parents=True)
        (run_dir / "compile.json").write_text(
            json.dumps(
                {
                    "source_compile": {
                        "facts": [
                            "fda_warning_letter(wl_717972, cder, apothecary_pharma_llc, v_2025_12_01, source_url)."
                        ]
                    }
                }
            ),
            encoding="utf-8",
        )

    manifest = {
        "schema": "prethinker.compile_fact_qa_manifest.v1",
        "cells": [
            {
                "id": "cell_a",
                "fixture_id": "fixture_a",
                "domain_lens_bundle": str(bundle_root),
                "expect": {
                    "support.reference_count": 1,
                    "support.runs_seen": 2,
                    "support.exact_support_ge_2": 1,
                    "redaction.prose_dependent_exact": 0,
                    "typed_plan.unregistered_plan_exact_rows": 0,
                },
            }
        ],
    }

    out_root = tmp_path / "out"
    summary = run_manifest(
        manifest=manifest,
        manifest_path=tmp_path / "manifest.json",
        fixture_root=fixture_root,
        out_root=out_root,
        created_utc="2026-06-04T00:00:00Z",
    )
    write_summary(summary=summary, out_root=out_root)

    assert summary["summary"]["status"] == "pass"
    assert summary["cells"][0]["support_summary_by_fixture"]["fixture_a"]["exact_support_ge_2"] == 1
    assert summary["cells"][0]["unexpected_same_signature_summary_by_fixture"]["fixture_a"] == {
        "runs_seen": 2,
        "unexpected_same_signature_ge_1": 0,
        "unexpected_same_signature_ge_2": 0,
    }
    assert summary["cells"][0]["redaction_summary"]["prose_dependent_exact"] == 0
    assert summary["cells"][0]["typed_plan_summary"]["unregistered_plan_exact_rows"] == 0
    assert (out_root / "summary.json").exists()
    assert (out_root / "SUMMARY.md").exists()


def test_run_compile_fact_judged_qa_manifest_blocks_forbidden_emissions(tmp_path: Path) -> None:
    fixture_root = tmp_path / "fixtures"
    fixture_dir = fixture_root / "fixture_a"
    fixture_dir.mkdir(parents=True)
    (fixture_dir / "expected_facts.pl").write_text(
        "fda_warning_letter(Letter, cder, apothecary_pharma_llc, v_2025_12_01, SrcLetter).\n",
        encoding="utf-8",
    )
    (fixture_dir / "forbidden_facts.pl").write_text(
        "fda_warning_letter(Letter, cber, apothecary_pharma_llc, v_2025_12_01, SrcLetter).\n",
        encoding="utf-8",
    )

    bundle_root = tmp_path / "bundle"
    for run_id in ["run1", "run2"]:
        run_dir = bundle_root / "unions" / run_id
        run_dir.mkdir(parents=True)
        (run_dir / "compile.json").write_text(
            json.dumps(
                {
                    "source_compile": {
                        "facts": [
                            "fda_warning_letter(wl_717972, cder, apothecary_pharma_llc, v_2025_12_01, source_url).",
                            "fda_warning_letter(wl_717972, cber, apothecary_pharma_llc, v_2025_12_01, source_url).",
                        ]
                    }
                }
            ),
            encoding="utf-8",
        )

    manifest = {
        "schema": "prethinker.compile_fact_qa_manifest.v1",
        "cells": [
            {
                "id": "cell_a",
                "fixture_id": "fixture_a",
                "domain_lens_bundle": str(bundle_root),
                "expect": {
                    "support.reference_count": 1,
                    "support.exact_support_ge_2": 1,
                    "redaction.prose_dependent_exact": 0,
                    "typed_plan.unregistered_plan_exact_rows": 0,
                },
            }
        ],
    }

    summary = run_manifest(
        manifest=manifest,
        manifest_path=tmp_path / "manifest.json",
        fixture_root=fixture_root,
        out_root=tmp_path / "out",
        created_utc="2026-06-04T00:00:00Z",
    )

    assert summary["summary"]["status"] == "fail"
    assert summary["cells"][0]["forbidden_emissions_summary_by_fixture"]["fixture_a"] == {
        "runs_seen": 2,
        "forbidden_emissions_ge_1": 1,
        "forbidden_emissions_ge_2": 1,
    }
    assert summary["summary"]["blocking_reasons"] == ["cell_a:forbidden_emissions_ge_1:1"]


def test_run_compile_fact_judged_qa_manifest_reports_expectation_mismatch() -> None:
    result = {
        "id": "cell_a",
        "fixture_id": "fixture_a",
        "support_summary_by_fixture": {"fixture_a": {"exact_support_ge_2": 1}},
        "forbidden_emissions_summary_by_fixture": {"fixture_a": {"forbidden_emissions_ge_1": 0}},
        "unexpected_same_signature_summary_by_fixture": {
            "fixture_a": {"unexpected_same_signature_ge_2": 0}
        },
        "redaction_summary": {"status": "pass", "blocking_reasons": [], "prose_dependent_exact": 0},
        "typed_plan_summary": {"status": "pass", "blocking_reasons": [], "unregistered_plan_exact_rows": 0},
        "expect": {"support.exact_support_ge_2": 2},
    }

    from scripts.run_compile_fact_judged_qa_manifest import _blocking_reasons

    assert _blocking_reasons(result) == [
        "cell_a:expectation_mismatch:support.exact_support_ge_2:expected=2:actual=1"
    ]


def test_run_compile_fact_judged_qa_manifest_checks_unexpected_expectations() -> None:
    result = {
        "id": "cell_a",
        "fixture_id": "fixture_a",
        "support_summary_by_fixture": {"fixture_a": {"exact_support_ge_2": 1}},
        "forbidden_emissions_summary_by_fixture": {"fixture_a": {"forbidden_emissions_ge_1": 0}},
        "unexpected_same_signature_summary_by_fixture": {
            "fixture_a": {"unexpected_same_signature_ge_2": 1}
        },
        "redaction_summary": {"status": "pass", "blocking_reasons": [], "prose_dependent_exact": 0},
        "typed_plan_summary": {"status": "pass", "blocking_reasons": [], "unregistered_plan_exact_rows": 0},
        "expect": {"unexpected.unexpected_same_signature_ge_2": 0},
    }

    from scripts.run_compile_fact_judged_qa_manifest import _blocking_reasons

    assert _blocking_reasons(result) == [
        "cell_a:expectation_mismatch:unexpected.unexpected_same_signature_ge_2:expected=0:actual=1"
    ]
