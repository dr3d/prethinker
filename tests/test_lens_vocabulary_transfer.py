import json
from pathlib import Path

from scripts.audit_lens_vocabulary_transfer import (
    AUTHORITY_CUSTODY_TERMS,
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


def test_rule_composition_audit_accepts_linked_exception_condition_action(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_1, the_exception_applies_when_a_sponsor_signs_and_waives_review).",
            "rule_exception(base_review_rule, sponsor_exception).",
            "rule_condition(sponsor_exception, sponsor_signature).",
            "rule_action(sponsor_exception, waive_staff_review).",
        ],
    )

    report = audit_compile(compile_json, lens="rule_composition", terms=RULE_COMPOSITION_TERMS)

    rows = {row["term"]: row["status"] for row in report["terms"]}
    assert rows["exception"] == "structural"


def test_rule_composition_audit_marks_unresolved_exception_link_shallow(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_1, the_exception_applies_when_a_sponsor_signs_and_waives_review).",
            "rule_exception(base_review_rule, sponsor_exception).",
            "rule_condition(sponsor_exception, sponsor_signature).",
        ],
    )

    report = audit_compile(compile_json, lens="rule_composition", terms=RULE_COMPOSITION_TERMS)

    rows = {row["term"]: row["status"] for row in report["terms"]}
    assert rows["exception"] == "shallow_structural"


def test_rule_composition_audit_accepts_scoped_two_slot_override_link(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_1, emergency_closure_overrides_the_normal_booking_rule_when_active).",
            "rule_precedence(emergency_closure_rule, normal_booking_rule).",
            "rule_condition(emergency_closure_rule, closure_notice_active).",
            "rule_action(emergency_closure_rule, suspend_room_bookings).",
        ],
    )

    report = audit_compile(compile_json, lens="rule_composition", terms=RULE_COMPOSITION_TERMS)

    rows = {row["term"]: row["status"] for row in report["terms"]}
    assert rows["override"] == "structural"


def test_rule_composition_audit_leaves_rank_only_override_link_shallow(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_1, emergency_closure_overrides_the_normal_booking_rule_when_active).",
            "rule_precedence(emergency_closure_rule, normal_booking_rule).",
        ],
    )

    report = audit_compile(compile_json, lens="rule_composition", terms=RULE_COMPOSITION_TERMS)

    rows = {row["term"]: row["status"] for row in report["terms"]}
    assert rows["override"] == "shallow_structural"


def test_rule_composition_audit_accepts_current_generic_rule_palette(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_1, base_rule_exception_threshold_and_vote_requirements).",
            "rule_condition(base_rule, eligibility, recipient_on_waitlist).",
            "rule_consequence(base_rule, action, allow_transfer).",
            "requires_count(hardship_rule, missed_shift, 2, calendar_month).",
            "requires_vote(hardship_rule, two_thirds, five_members_present).",
            "exception_for(hardship_exception, base_rule).",
            "exception_condition(hardship_exception, evidence, medical_note).",
            "rule_consequence(hardship_exception, action, allow_transfer_with_one_workday).",
        ],
    )

    report = audit_compile(compile_json, lens="rule_composition", terms=RULE_COMPOSITION_TERMS)

    rows = {row["term"]: row["status"] for row in report["terms"]}
    assert rows["base_rule"] == "structural"
    assert rows["threshold"] == "structural"
    assert rows["vote_requirement"] == "structural"


def test_authority_custody_audit_accepts_court_order_slots(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_1, court_order_c_14_issued_by_county_court_on_2026_04_06_for_device_release).",
            "court_order(order_c_14, county_court, device_release, 2026_04_06).",
        ],
    )

    report = audit_compile(compile_json, lens="authority_custody", terms=AUTHORITY_CUSTODY_TERMS)

    rows = {row["term"]: row["status"] for row in report["terms"]}
    assert rows["court_order"] == "structural"


def test_authority_custody_audit_requires_noncontrolling_reason(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_1, copied_notice_is_noncontrolling_because_later_vote_replaced_it).",
            "source_status(copied_notice, noncontrolling).",
        ],
    )

    report = audit_compile(compile_json, lens="authority_custody", terms=AUTHORITY_CUSTODY_TERMS)

    rows = {row["term"]: row["status"] for row in report["terms"]}
    assert rows["noncontrolling_source"] == "shallow_structural"


def test_authority_custody_audit_accepts_noncontrolling_reason_contract(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_1, copied_notice_is_noncontrolling_because_later_vote_replaced_it).",
            "source_status(copied_notice, noncontrolling).",
            "noncontrolling_reason(copied_notice, later_vote_replaced_it).",
        ],
    )

    report = audit_compile(compile_json, lens="authority_custody", terms=AUTHORITY_CUSTODY_TERMS)

    rows = {row["term"]: row["status"] for row in report["terms"]}
    assert rows["noncontrolling_source"] == "structural"


def test_authority_custody_audit_accepts_board_vote_and_custody_terms(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_1, board_voted_to_place_archive_box_with_records_steward).",
            "board_vote(records_board, assign_box_to_records_steward, 2026_04_08).",
            "custody_holder(archive_box, records_steward, active_after_vote).",
        ],
    )

    report = audit_compile(compile_json, lens="authority_custody", terms=AUTHORITY_CUSTODY_TERMS)

    rows = {row["term"]: row["status"] for row in report["terms"]}
    assert rows["board_vote"] == "structural"
    assert rows["custody_holder"] == "structural"


def test_authority_custody_audit_accepts_generic_record_entry_contract(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_1, order_permits_log_inspection_but_not_release).",
            "record_entry(ro_2, order, research_court, 2026_02_05).",
            "permits_access(ro_2, log_inspection).",
            "denies_access(ro_2, physical_release).",
        ],
    )

    report = audit_compile(compile_json, lens="authority_custody", terms=AUTHORITY_CUSTODY_TERMS)

    rows = {row["term"]: row["status"] for row in report["terms"]}
    assert rows["court_order"] == "structural"


def test_authority_custody_audit_leaves_record_label_without_slots_shallow(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_1, draft_recommendation_existed_but_no_content_was_emitted).",
            "document_type(dr_6, draft_recommendation).",
            "document_author(dr_6, nia_park).",
        ],
    )

    report = audit_compile(compile_json, lens="authority_custody", terms=AUTHORITY_CUSTODY_TERMS)

    rows = {row["term"]: row["status"] for row in report["terms"]}
    assert rows["draft_recommendation"] == "shallow_structural"


def test_authority_custody_audit_accepts_is_noncontrolling_with_reason_detail(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_1, copied_summary_is_noncontrolling_because_it_ignored_later_vote).",
            "is_noncontrolling(summary_3).",
            "record_detail(summary_3, reason_noncontrolling, ignored_later_vote).",
        ],
    )

    report = audit_compile(compile_json, lens="authority_custody", terms=AUTHORITY_CUSTODY_TERMS)

    rows = {row["term"]: row["status"] for row in report["terms"]}
    assert rows["noncontrolling_source"] == "structural"
