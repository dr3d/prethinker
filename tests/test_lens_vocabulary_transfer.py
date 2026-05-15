import json
from pathlib import Path

from scripts.audit_lens_vocabulary_transfer import (
    EVIDENCE_PROVENANCE_TERMS,
    RULE_COMPOSITION_TERMS,
    audit_compile,
    summarize_reports,
)


def _write_compile(path: Path, facts: list[str]) -> Path:
    path.write_text(
        json.dumps(
            {
                "parsed_ok": True,
                "source_compile": {"facts": facts},
            }
        ),
        encoding="utf-8",
    )
    return path


def test_lens_vocabulary_audit_classifies_structural_and_source_only_terms(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_1, report_commissioned_and_later_revised).",
            "report_commissioned_by(report_a, board, 2026_04_02).",
            "report_date(report_a, 2026_04_02).",
        ],
    )

    report = audit_compile(compile_json, lens="evidence_provenance", terms=EVIDENCE_PROVENANCE_TERMS)

    rows = {row["term"]: row["status"] for row in report["terms"]}
    assert rows["commissioned"] == "structural"
    assert rows["dated"] == "structural"
    assert rows["corrected"] == "source_only"


def test_lens_vocabulary_audit_marks_shallow_structural_when_slots_are_missing(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_1, summary_presented_by_mina_to_circle).",
            "presented_to(summary_a, circle).",
        ],
    )

    report = audit_compile(compile_json, lens="evidence_provenance", terms=EVIDENCE_PROVENANCE_TERMS)

    rows = {row["term"]: row["status"] for row in report["terms"]}
    assert rows["presented"] == "shallow_structural"


def test_lens_vocabulary_audit_accepts_equivalent_preparation_predicates(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_1, rowan_wrote_the_safety_note_on_2026_04_06).",
            "created_by(safety_note, rowan_hale, 2026_04_06).",
        ],
    )

    report = audit_compile(compile_json, lens="evidence_provenance", terms=EVIDENCE_PROVENANCE_TERMS)

    rows = {row["term"]: row["status"] for row in report["terms"]}
    assert rows["prepared"] == "structural"


def test_lens_vocabulary_audit_requires_presentation_slots(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_1, laila_read_the_safety_note_aloud_at_closing_huddle).",
            "read_aloud(laila_chen, safety_note, closing_huddle).",
        ],
    )

    report = audit_compile(compile_json, lens="evidence_provenance", terms=EVIDENCE_PROVENANCE_TERMS)

    rows = {row["term"]: row["status"] for row in report["terms"]}
    assert rows["presented"] == "structural"


def test_lens_vocabulary_summary_counts_terms(tmp_path: Path) -> None:
    first = audit_compile(
        _write_compile(
            tmp_path / "first.json",
            [
                "source_record_text_atom(src_1, report_prepared_by_clerk).",
                "report_prepared_by(report_a, clerk).",
            ],
        ),
        lens="evidence_provenance",
        terms=EVIDENCE_PROVENANCE_TERMS,
    )
    second = audit_compile(
        _write_compile(
            tmp_path / "second.json",
            ["source_record_text_atom(src_1, report_prepared_by_clerk)."],
        ),
        lens="evidence_provenance",
        terms=EVIDENCE_PROVENANCE_TERMS,
    )

    summary = summarize_reports([first, second], EVIDENCE_PROVENANCE_TERMS)

    assert summary["term_status_counts"]["prepared"]["structural"] == 1
    assert summary["term_status_counts"]["prepared"]["source_only"] == 1


def test_rule_composition_audit_accepts_shared_anchor_contracts(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_1, exception_applies_unless_supervisor_signs_the_waiver).",
            "exception_condition(after_hours_access_waiver, supervisor_signature).",
            "exception_effect(after_hours_access_waiver, permit_after_hours_access).",
        ],
    )

    report = audit_compile(compile_json, lens="rule_composition", terms=RULE_COMPOSITION_TERMS)

    rows = {row["term"]: row["status"] for row in report["terms"]}
    assert rows["exception"] == "structural"


def test_rule_composition_audit_marks_partial_contracts_shallow(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_1, exception_applies_unless_supervisor_signs_the_waiver).",
            "exception_condition(after_hours_access_waiver, supervisor_signature).",
        ],
    )

    report = audit_compile(compile_json, lens="rule_composition", terms=RULE_COMPOSITION_TERMS)

    rows = {row["term"]: row["status"] for row in report["terms"]}
    assert rows["exception"] == "shallow_structural"


def test_rule_composition_audit_requires_relational_threshold_slots(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_1, the_threshold_is_three_consecutive_clean_logs).",
            "threshold_value(clean_log_rule, three_consecutive_clean_logs).",
            "threshold_measure(clean_log_rule, inspection_logs).",
        ],
    )

    report = audit_compile(compile_json, lens="rule_composition", terms=RULE_COMPOSITION_TERMS)

    rows = {row["term"]: row["status"] for row in report["terms"]}
    assert rows["threshold"] == "structural"


def test_rule_composition_audit_accepts_condition_action_activation_contract(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_1, the_rule_activates_when_a_weekend_request_is_made).",
            "rule_condition(weekend_access_rule, weekend_reservation_request).",
            "rule_action(weekend_access_rule, allow_reservation_after_training).",
        ],
    )

    report = audit_compile(compile_json, lens="rule_composition", terms=RULE_COMPOSITION_TERMS)

    rows = {row["term"]: row["status"] for row in report["terms"]}
    assert rows["activation_condition"] == "structural"
    assert rows["base_rule"] == "structural"


def test_rule_composition_audit_accepts_rule_precedence_as_override_contract(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_1, emergency_closure_overrides_the_normal_booking_rule).",
            "rule_precedence(emergency_closure_rule, normal_booking_rule, conflict).",
        ],
    )

    report = audit_compile(compile_json, lens="rule_composition", terms=RULE_COMPOSITION_TERMS)

    rows = {row["term"]: row["status"] for row in report["terms"]}
    assert rows["override"] == "structural"
    assert rows["precedence"] == "structural"
