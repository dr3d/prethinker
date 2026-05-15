import json
from pathlib import Path

from scripts.audit_lens_vocabulary_transfer import (
    AUTHORITY_CUSTODY_TERMS,
    ENTITY_ROLE_TERMS,
    EVIDENCE_PROVENANCE_TERMS,
    EPISTEMIC_UNCERTAINTY_TERMS,
    OPERATIONAL_RECORD_STATUS_TERMS,
    RULE_COMPOSITION_TERMS,
    TEMPORAL_STATUS_TERMS,
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


def test_authority_custody_audit_accepts_source_document_declares_contract(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_1, controlling_finding_declares_current_custody).",
            "source_document(cf_3, controlling_finding).",
            "source_declares(cf_3, custody_holder, team_remains_holder_until_replacement).",
        ],
    )

    report = audit_compile(compile_json, lens="authority_custody", terms=AUTHORITY_CUSTODY_TERMS)

    rows = {row["term"]: row["status"] for row in report["terms"]}
    assert rows["controlling_finding"] == "structural"


def test_authority_custody_audit_accepts_record_type_provision_contract(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_1, staff_note_recommended_supervised_access).",
            "record_type(sn_9, staff_note).",
            "record_provision(sn_9, recommendation, supervised_access).",
        ],
    )

    report = audit_compile(compile_json, lens="authority_custody", terms=AUTHORITY_CUSTODY_TERMS)

    rows = {row["term"]: row["status"] for row in report["terms"]}
    assert rows["staff_note"] == "structural"


def test_authority_custody_audit_accepts_event_type_outcome_contract(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_1, council_vote_allowed_temporary_checkout).",
            "event_type(event_council_vote, council_vote).",
            "event_outcome(event_council_vote, temporary_checkout_allowed_to_plot_captains).",
        ],
    )

    report = audit_compile(compile_json, lens="authority_custody", terms=AUTHORITY_CUSTODY_TERMS)

    rows = {row["term"]: row["status"] for row in report["terms"]}
    assert rows["board_vote"] == "structural"


def test_authority_custody_audit_accepts_draft_proposal_pending_contract(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_1, draft_recommendation_proposed_supervised_checkout).",
            "record_type(dr_2, draft_recommendation).",
            "proposed_action(dr_2, supervised_checkout).",
            "pending_approval(dr_2, director_vote).",
        ],
    )

    report = audit_compile(compile_json, lens="authority_custody", terms=AUTHORITY_CUSTODY_TERMS)

    rows = {row["term"]: row["status"] for row in report["terms"]}
    assert rows["draft_recommendation"] == "structural"


def test_authority_custody_audit_accepts_doc_alias_draft_content_contract(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_1, draft_recommendation_proposed_checkout).",
            "doc_type(dr_2, draft_recommendation).",
            "doc_status(dr_2, draft).",
            "doc_content(dr_2, proposed_supervised_checkout).",
        ],
    )

    report = audit_compile(compile_json, lens="authority_custody", terms=AUTHORITY_CUSTODY_TERMS)

    rows = {row["term"]: row["status"] for row in report["terms"]}
    assert rows["draft_recommendation"] == "structural"


def test_authority_custody_audit_accepts_noncontrolling_omitted_source_contract(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_1, copied_notice_omitted_controlling_vote).",
            "noncontrolling_source(notice_5, copied_notice).",
            "copied_from(notice_5, draft_recommendation).",
            "omitted_authority(notice_5, controlling_vote).",
        ],
    )

    report = audit_compile(compile_json, lens="authority_custody", terms=AUTHORITY_CUSTODY_TERMS)

    rows = {row["term"]: row["status"] for row in report["terms"]}
    assert rows["noncontrolling_source"] == "structural"


def test_authority_custody_audit_accepts_source_recorded_noncontrolling_reason(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_1, copied_notice_omitted_final_order).",
            "document_status(notice_5, noncontrolling).",
            "source_recorded(notice_5, noncontrolling_reason, copied_draft_and_omitted_final_order).",
        ],
    )

    report = audit_compile(compile_json, lens="authority_custody", terms=AUTHORITY_CUSTODY_TERMS)

    rows = {row["term"]: row["status"] for row in report["terms"]}
    assert rows["noncontrolling_source"] == "structural"


def test_operational_record_audit_accepts_record_detail_status_contract(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_1, intake_record_was_received_and_assigned).",
            "record_entry(intake_9, intake_record, clerk, 2026_04_01).",
            "record_detail(intake_9, received_by, clerk).",
            "record_detail(intake_9, assigned_to, review_team).",
        ],
    )

    report = audit_compile(compile_json, lens="operational_record_status", terms=OPERATIONAL_RECORD_STATUS_TERMS)

    rows = {row["term"]: row["status"] for row in report["terms"]}
    assert rows["received"] == "structural"
    assert rows["assigned"] == "structural"


def test_operational_record_audit_accepts_current_status_surface(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_1, work_order_current_status_pending).",
            "current_status(work_order_7, pending).",
        ],
    )

    report = audit_compile(compile_json, lens="operational_record_status", terms=OPERATIONAL_RECORD_STATUS_TERMS)

    rows = {row["term"]: row["status"] for row in report["terms"]}
    assert rows["pending"] == "structural"
    assert rows["current_status"] == "structural"


def test_operational_record_audit_marks_label_only_record_shallow(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_1, record_entry_only_says_denial_record).",
            "record_entry(denial_4, denied_record, clerk, 2026_04_02).",
        ],
    )

    report = audit_compile(compile_json, lens="operational_record_status", terms=OPERATIONAL_RECORD_STATUS_TERMS)

    rows = {row["term"]: row["status"] for row in report["terms"]}
    assert rows["denied"] == "shallow_structural"


def test_operational_record_audit_accepts_status_transition_slots(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_1, item_status_changed_from_pending_to_approved).",
            "status_transition(case_2, pending, approved, 2026_04_03).",
        ],
    )

    report = audit_compile(compile_json, lens="operational_record_status", terms=OPERATIONAL_RECORD_STATUS_TERMS)

    rows = {row["term"]: row["status"] for row in report["terms"]}
    assert rows["status_transition"] == "structural"


def test_epistemic_uncertainty_audit_accepts_stance_rows(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_1, note_confirmed_measurement_but_retracted_old_claim).",
            "confirmed(measurement_m4, scale_log).",
            "retracted(old_claim, supervisor_note).",
            "pending_item(inspection_file, battery_check).",
            "resolved_negative(camera_log, visitor_entry).",
        ],
    )

    report = audit_compile(compile_json, lens="epistemic_uncertainty", terms=EPISTEMIC_UNCERTAINTY_TERMS)

    rows = {row["term"]: row["status"] for row in report["terms"]}
    assert rows["confirmed"] == "structural"
    assert rows["retracted"] == "structural"
    assert rows["pending"] == "structural"
    assert rows["resolved_negative"] == "structural"


def test_epistemic_uncertainty_audit_marks_bare_stance_shallow(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_1, statement_was_disputed_but_no_target_was_preserved).",
            "disputed(statement_4).",
        ],
    )

    report = audit_compile(compile_json, lens="epistemic_uncertainty", terms=EPISTEMIC_UNCERTAINTY_TERMS)

    rows = {row["term"]: row["status"] for row in report["terms"]}
    assert rows["disputed"] == "shallow_structural"


def test_epistemic_uncertainty_audit_accepts_source_recorded_stance(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_1, review_confirmed_the_delivery).",
            "source_recorded(review_4, delivery_to_bed_b9, confirmed).",
        ],
    )

    report = audit_compile(compile_json, lens="epistemic_uncertainty", terms=EPISTEMIC_UNCERTAINTY_TERMS)

    rows = {row["term"]: row["status"] for row in report["terms"]}
    assert rows["confirmed"] == "structural"


def test_epistemic_uncertainty_audit_accepts_status_with_evidence_contract(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_1, cash_claim_unsupported_without_receipt).",
            "epistemic_status(claim_cash, unsupported).",
            "evidence_for(claim_cash, no_deposit_receipt).",
        ],
    )

    report = audit_compile(compile_json, lens="epistemic_uncertainty", terms=EPISTEMIC_UNCERTAINTY_TERMS)

    rows = {row["term"]: row["status"] for row in report["terms"]}
    assert rows["unsupported"] == "structural"


def test_epistemic_uncertainty_audit_accepts_missing_field_contract(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_1, owner_name_unstated_for_locker_l_22).",
            "attribute_missing(locker_l22, owner_name).",
            "field_unstated(locker_l22, assignment_end_date).",
        ],
    )

    report = audit_compile(compile_json, lens="epistemic_uncertainty", terms=EPISTEMIC_UNCERTAINTY_TERMS)

    rows = {row["term"]: row["status"] for row in report["terms"]}
    assert rows["unstated"] == "structural"


def test_entity_role_audit_accepts_alias_and_role_holder_slots(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_1, badge_name_is_an_alias_and_mara_served_as_dock_lead).",
            "alias_of(mara_chen, badge_m17).",
            "role_holder(dock_lead, mara_chen, 2026_04_01).",
        ],
    )

    report = audit_compile(compile_json, lens="entity_role", terms=ENTITY_ROLE_TERMS)

    rows = {row["term"]: row["status"] for row in report["terms"]}
    assert rows["alias"] == "structural"
    assert rows["role_holder"] == "structural"


def test_entity_role_audit_requires_role_transition_slots(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_1, old_dispatch_lead_was_replaced_but_successor_missing).",
            "role_transition(dispatch_lead, previous_holder).",
        ],
    )

    report = audit_compile(compile_json, lens="entity_role", terms=ENTITY_ROLE_TERMS)

    rows = {row["term"]: row["status"] for row in report["terms"]}
    assert rows["role_transition"] == "shallow_structural"


def test_entity_role_audit_accepts_membership_ownership_and_responsibility_slots(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_1, inventory_circle_member_owned_cabinet_and_supervised_repair).",
            "group_member(inventory_circle, jo_ren, active).",
            "owner_of(cabinet_c9, jo_ren, legal_title).",
            "responsible_for(jo_ren, repair_check, 2026_04_08).",
        ],
    )

    report = audit_compile(compile_json, lens="entity_role", terms=ENTITY_ROLE_TERMS)

    rows = {row["term"]: row["status"] for row in report["terms"]}
    assert rows["membership"] == "structural"
    assert rows["ownership"] == "structural"
    assert rows["responsibility"] == "structural"


def test_entity_role_audit_accepts_current_generic_palette(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_1, identity_alias_role_custody_family_and_responsibility_rows).",
            "is_same_person(badge_9, mira_sol).",
            "has_alias(mira_sol, night_lead, evening_shift).",
            "held_role(mira_sol, dock_lead, temporary, evening_shift).",
            "owns(tool_library, tablet_t_8).",
            "has_custody(mira_sol, tablet_t_8, evening_shift).",
            "responsible_for(rafi_sen, signout_table).",
            "is_family_member(nora_vale, iven_vale).",
        ],
    )

    report = audit_compile(compile_json, lens="entity_role", terms=ENTITY_ROLE_TERMS)

    rows = {row["term"]: row["status"] for row in report["terms"]}
    assert rows["identity_equivalence"] == "structural"
    assert rows["alias"] == "structural"
    assert rows["role_holder"] == "structural"
    assert rows["ownership"] == "structural"
    assert rows["custody"] == "structural"
    assert rows["responsibility"] == "structural"
    assert rows["family_relationship"] == "structural"


def test_temporal_status_audit_accepts_status_timeline_and_effective_date(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_1, status_changed_on_effective_date).",
            "transition_effective_date(change_7, 2026_04_12).",
            "permit_status(permit_4, pending, 2026_04_01).",
            "permit_status(permit_4, approved, 2026_04_12).",
        ],
    )

    report = audit_compile(compile_json, lens="temporal_status", terms=TEMPORAL_STATUS_TERMS)

    rows = {row["term"]: row["status"] for row in report["terms"]}
    assert rows["effective_date"] == "structural"
    assert rows["status_at"] == "structural"


def test_temporal_status_audit_marks_label_without_slots_shallow(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_1, a_deadline_was_mentioned_without_date).",
            "deadline(task_9).",
        ],
    )

    report = audit_compile(compile_json, lens="temporal_status", terms=TEMPORAL_STATUS_TERMS)

    rows = {row["term"]: row["status"] for row in report["terms"]}
    assert rows["deadline"] == "shallow_structural"
