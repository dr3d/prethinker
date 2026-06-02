import json
from pathlib import Path

from scripts.audit_kb_atom_inventory import build_report


def _write_compile(path: Path, facts: list[str], **metadata) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "source_compile": {
            "facts": facts,
        }
    }
    payload.update(metadata)
    path.write_text(
        json.dumps(payload),
        encoding="utf-8",
    )


def test_kb_atom_inventory_excludes_source_record_and_prose_like_atoms(tmp_path: Path) -> None:
    compile_root = tmp_path / "compile"
    _write_compile(
        compile_root / "fixture_a" / "run.json",
        [
            "document_date(doc_a, issue_date, v_2026_05_30).",
            "document_identifier(doc_a, commission_file_number, id_001_39898).",
            "party_role_context(case_a, union_one, petitioner, direct).",
            "source_record_text_display(src_line_0001, 'Commission file number 001-39898').",
            "source_detail(doc_a, note, 'This is a very long prose-like note with many words that should be rejected from the typed atom inventory because it is display text in disguise.').",
        ],
    )
    _write_compile(
        compile_root / "fixture_b" / "run.json",
        [
            "document_date(doc_b, issue_date, v_2026_05_31).",
            "party_role(person_a, signatory, company_b).",
        ],
    )

    report = build_report(
        compile_root=compile_root,
        fixtures=None,
        include_source_record=False,
        include_prose_like=False,
        max_examples=2,
    )

    assert report["summary"]["fixture_count"] == 2
    assert report["summary"]["typed_fact_count"] == 5
    assert report["summary"]["registered_fact_count"] == 3
    assert report["summary"]["registered_signature_count"] == 2
    assert report["summary"]["registered_fact_rate"] == 0.6
    assert report["summary"]["registered_signature_rate"] == 0.5
    assert report["summary"]["unregistered_fact_count"] == 2
    assert report["summary"]["unregistered_signature_count"] == 2
    assert report["summary"]["rejected_counts"] == {
        "prose_like": 1,
        "source_record": 1,
    }
    assert report["top_signatures"]["document_date/3"] == 2
    assert report["top_registered_signatures"]["document_date/3"] == 2
    assert report["top_unregistered_signatures"]["document_identifier/3"] == 1
    assert report["top_signatures"]["document_identifier/3"] == 1
    assert report["top_signatures"]["party_role/3"] == 1
    assert report["top_registered_signatures"]["party_role_context/4"] == 1
    assert all(not item["signature"].startswith("source_record_") for item in report["signatures"])
    assert next(item for item in report["signatures"] if item["signature"] == "document_date/3")[
        "registered"
    ]
    assert not next(
        item for item in report["signatures"] if item["signature"] == "document_identifier/3"
    )["registered"]
    assert not next(item for item in report["signatures"] if item["signature"] == "party_role/3")[
        "registered"
    ]


def test_kb_atom_inventory_reports_signature_overlap(tmp_path: Path) -> None:
    compile_root = tmp_path / "compile"
    _write_compile(
        compile_root / "fixture_a" / "run.json",
        [
            "document_date(doc_a, issue_date, v_2026_05_30).",
            "party_role(person_a, signatory, company_a).",
        ],
    )
    _write_compile(
        compile_root / "fixture_b" / "run.json",
        [
            "document_date(doc_b, issue_date, v_2026_05_31).",
            "document_identifier(doc_b, accession_number, acc_123).",
        ],
    )

    report = build_report(
        compile_root=compile_root,
        fixtures=None,
        include_source_record=False,
        include_prose_like=False,
        max_examples=1,
    )

    assert report["fixture_signature_overlap"] == [
        {
            "left": "fixture_a",
            "right": "fixture_b",
            "intersection": 1,
            "union": 3,
            "jaccard": 0.333333,
        }
    ]


def test_kb_atom_inventory_atom_shape_gate_flags_prose_shaped_typed_atoms(tmp_path: Path) -> None:
    compile_root = tmp_path / "compile"
    _write_compile(
        compile_root / "fixture_a" / "run.json",
        [
            "document_title(doc_a, if_the_psc_fails_to_grant_a_request_for_review_or_rehearing_within_thirty_days_after_filing_the_request_it_is_deemed_denied).",
            "predicate_name_that_reads_like_a_whole_sentence_about_the_source_document_and_should_not_exist(doc_a, compact_atom).",
            "source_record_text_display(src_line_0001, 'The source prose is already excluded by source-record policy.').",
        ],
    )

    report = build_report(
        compile_root=compile_root,
        fixtures=None,
        include_source_record=False,
        include_prose_like=False,
        max_examples=10,
    )

    assert report["atom_shape"]["status"] == "fail"
    assert report["summary"]["atom_shape_blocker_count"] >= 2
    issue_types = report["atom_shape"]["issue_type_counts"]
    assert issue_types["registered_carrier_prose_shaped_value"] >= 1
    assert issue_types["predicate_name_too_long"] >= 1
    assert all(not issue["signature"].startswith("source_record_") for issue in report["atom_shape"]["examples"])


def test_kb_atom_inventory_reports_active_lens_scope_violations(tmp_path: Path) -> None:
    compile_root = tmp_path / "compile"
    _write_compile(
        compile_root / "violation_lens" / "run.json",
        [
            "fda_violation(violation_1, letter_1, violation_1, contamination_control, source_1).",
            "fda_response_requirement(letter_1, written_response, fifteen_working_days, issuing_office, corrective_actions, source_2).",
        ],
        active_profile_registry_lens={
            "id": "violation",
            "allowed_signatures": ["fda_violation/5"],
        },
    )

    report = build_report(
        compile_root=compile_root,
        fixtures=None,
        include_source_record=False,
        include_prose_like=False,
        max_examples=5,
    )

    assert report["lens_scope"]["status"] == "fail"
    assert report["summary"]["lens_scope_blocker_count"] == 1
    assert report["lens_scope"]["examples"][0]["signature"] == "fda_response_requirement/6"
    assert report["fixtures_detail"][0]["lens_scope_blocker_count"] == 1


def test_kb_atom_inventory_lens_scope_ignores_artifacts_without_active_lens(tmp_path: Path) -> None:
    compile_root = tmp_path / "compile"
    _write_compile(
        compile_root / "all_lenses_union" / "run.json",
        [
            "fda_violation(violation_1, letter_1, violation_1, contamination_control, source_1).",
            "fda_response_requirement(letter_1, written_response, fifteen_working_days, issuing_office, corrective_actions, source_2).",
        ],
    )

    report = build_report(
        compile_root=compile_root,
        fixtures=None,
        include_source_record=False,
        include_prose_like=False,
        max_examples=5,
    )

    assert report["lens_scope"]["status"] == "pass"
    assert report["summary"]["lens_scope_blocker_count"] == 0


def test_kb_atom_inventory_lens_scope_ignores_deterministic_unions_with_stale_lens_metadata(
    tmp_path: Path,
) -> None:
    compile_root = tmp_path / "compile"
    _write_compile(
        compile_root / "all_lenses_union" / "run.json",
        [
            "fda_violation(violation_1, letter_1, violation_1, contamination_control, source_1).",
            "fda_response_requirement(letter_1, written_response, fifteen_working_days, issuing_office, corrective_actions, source_2).",
        ],
        mode="deterministic_compile_union",
        union_source_compile={"source_runs": ["wrapper.json", "violation.json"]},
        active_profile_registry_lens={
            "id": "wrapper",
            "allowed_signatures": ["fda_warning_letter/5"],
        },
    )

    report = build_report(
        compile_root=compile_root,
        fixtures=None,
        include_source_record=False,
        include_prose_like=False,
        max_examples=5,
    )

    assert report["lens_scope"]["status"] == "pass"
    assert report["summary"]["lens_scope_blocker_count"] == 0
