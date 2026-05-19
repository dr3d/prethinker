import json
from pathlib import Path

from scripts.audit_compile_surface_invariants import audit_compile, summarize_reports
from scripts.audit_compile_surface_invariants import _expand_compile_paths


def _write_compile(path: Path, facts: list[str], candidate_predicates: list[str] | None = None) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "parsed_ok": True,
                "parsed": {"candidate_predicates": candidate_predicates or []},
                "source_compile": {"facts": facts},
            }
        ),
        encoding="utf-8",
    )
    return path


def test_audit_compile_surface_invariants_passes_direct_surfaces(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_line_001, section_8_2_inferences_not_available).",
            "source_record_text_atom(src_line_002, vendor_sentec_model_rh_220_plus_operator_r_kim).",
            "source_record_text_atom(src_line_003, procedure_qhp_04_requires_72_hours).",
            "source_record_text_atom(src_line_004, registrar_report_dated_2026_04_02_is_authority_for_item_access_status).",
            "section_title(section_8_2, inferences_not_available).",
            "sensor_info(hum_d_04, sentec, rh_220_plus).",
            "operator_note(r_kim, 2026_04_22_15_15, line_stopped).",
            "policy_rule(qhp_04, off_spec_material, held_for_72_hours).",
            "source_authority(report_2026_04_02, registrar, item_7, access_status).",
        ],
    )

    report = audit_compile(compile_json)

    statuses = {row["family"]: row["status"] for row in report["families"]}
    assert statuses["source_addressability_surface"] == "pass"
    assert statuses["object_device_surface"] == "pass"
    assert statuses["identity_role_surface"] == "pass"
    assert statuses["source_authority_surface"] == "pass"
    assert statuses["rule_policy_surface"] == "pass"


def test_audit_compile_surface_invariants_detects_candidate_only_surface(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        ["source_record_text_atom(src_line_001, registrar_beatrice_caulfield_compiled_register)."],
        candidate_predicates=["registrar_identity/2"],
    )

    report = audit_compile(compile_json)

    identity = next(row for row in report["families"] if row["family"] == "identity_role_surface")
    assert identity["status"] == "candidate_only"
    assert "registrar_or_recorder" in identity["missing_groups"]


def test_audit_compile_surface_invariants_detects_source_authority_ledger_only(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_line_001, court_order_document_dated_2026_04_02_is_authority_for_item_access_status).",
            "access_authorized_to(item_7, requester).",
        ],
    )

    report = audit_compile(compile_json)

    source_authority = next(row for row in report["families"] if row["family"] == "source_authority_surface")
    assert source_authority["status"] == "partial"
    assert "source_document_or_correspondence" in source_authority["missing_groups"]
    assert "authority_or_evidence_role" in source_authority["covered_groups"]


def test_audit_compile_surface_invariants_detects_answer_detail_ledger_only(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_line_001, application_pending_because_commitment_not_available_outside_scope).",
            "application_status(app_1, pending).",
        ],
    )

    report = audit_compile(compile_json)

    detail = next(row for row in report["families"] if row["family"] == "answer_detail_surface")
    assert detail["status"] == "partial"
    assert "detail_or_explanation" in detail["missing_groups"]
    assert "availability_or_scope" in detail["missing_groups"]
    assert "negative_or_exclusion_detail" in detail["missing_groups"]
    assert "commitment_or_future_action" in detail["covered_groups"]


def test_audit_compile_surface_invariants_reports_stranded_source_record_promotions(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_label(src_line_001, next_calibration_due_2026_07_12).",
            "source_record_field(src_line_002, device_id, dev_scan_07).",
            "device_id(dev_scan_07).",
        ],
    )

    report = audit_compile(compile_json)

    telemetry = report["source_record_promotion_telemetry"]
    assert telemetry["candidate_count"] == 2
    assert telemetry["stranded_count"] == 1
    assert telemetry["top_stranded"][0]["value"] == "next_calibration_due_2026_07_12"


def test_expand_compile_paths_uses_latest_per_fixture_directory(tmp_path: Path) -> None:
    first = _write_compile(tmp_path / "root" / "fixture_a" / "domain_bootstrap_file_001.json", [])
    latest = _write_compile(tmp_path / "root" / "fixture_a" / "domain_bootstrap_file_002.json", [])
    other = _write_compile(tmp_path / "root" / "fixture_b" / "domain_bootstrap_file_001.json", [])

    paths = _expand_compile_paths([tmp_path / "root"])

    assert paths == sorted([latest.resolve(), other.resolve()])
    assert first.resolve() not in paths


def test_audit_compile_surface_invariants_detects_incomplete_event_backbone(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_line_001, event_entry_7_dated_2026_04_02_operator_system_a_sample_4_status_settled).",
            "event(event_7).",
            "event_date(event_7, 2026_04_02).",
        ],
    )

    report = audit_compile(compile_json)

    backbone = next(row for row in report["families"] if row["family"] == "event_backbone_unit_surface")
    assert backbone["status"] == "partial"
    assert "participant_or_system" in backbone["missing_groups"]
    assert "subject_or_object" in backbone["missing_groups"]
    assert "outcome_or_state" in backbone["missing_groups"]


def test_audit_compile_surface_invariants_passes_event_backbone_unit(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_line_001, event_entry_7_dated_2026_04_02_operator_system_a_sample_4_status_settled).",
            "event(event_7).",
            "event_date(event_7, 2026_04_02).",
            "event_actor(event_7, system_a).",
            "event_subject(event_7, sample_4).",
            "event_status(event_7, settled).",
        ],
    )

    report = audit_compile(compile_json)

    backbone = next(row for row in report["families"] if row["family"] == "event_backbone_unit_surface")
    assert backbone["status"] == "pass"


def test_audit_compile_surface_invariants_flags_vague_event_wrapper_without_backbone(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_line_001, event_entry_7_dated_2026_04_02_operator_system_a_sample_4_status_settled).",
            "event(event_7).",
            "event_detail(event_7, source_line_001).",
            "event_date(event_7, 2026_04_02).",
        ],
    )

    report = audit_compile(compile_json)

    contract = next(
        row for row in report["relation_contracts"] if row["contract"] == "vague_wrapper_backbone_contract"
    )
    assert contract["status"] == "vague_wrapper_without_backbone"
    assert contract["wrapper_predicates"] == ["event", "event_detail"]
    assert "participant_or_system" in contract["missing_keys"]


def test_audit_compile_surface_invariants_does_not_treat_specific_detail_predicates_as_vague(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_line_001, event_entry_7_dated_2026_04_02_operator_system_a_sample_4_status_settled_accommodation_detail_ref_17).",
            "accommodation_detail(student_7, ref_17).",
            "event_date(event_7, 2026_04_02).",
        ],
    )

    report = audit_compile(compile_json)

    contract = next(
        row for row in report["relation_contracts"] if row["contract"] == "vague_wrapper_backbone_contract"
    )
    assert contract["status"] == "missing_backbone_surface"
    assert contract["wrapper_predicates"] == []


def test_audit_compile_surface_invariants_allows_vague_event_wrapper_when_backbone_passes(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_line_001, event_entry_7_dated_2026_04_02_operator_system_a_sample_4_status_settled).",
            "event(event_7).",
            "event_detail(event_7, source_line_001).",
            "event_date(event_7, 2026_04_02).",
            "event_actor(event_7, system_a).",
            "event_subject(event_7, sample_4).",
            "event_status(event_7, settled).",
        ],
    )

    report = audit_compile(compile_json)

    contract = next(
        row for row in report["relation_contracts"] if row["contract"] == "vague_wrapper_backbone_contract"
    )
    assert contract["status"] == "pass"


def test_audit_compile_surface_invariants_detects_repeated_record_detail_gap(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_line_001, entry_1_lee_traded_4_boxes_to_mira_status_valid).",
            "source_record_text_atom(src_line_002, entry_2_omar_traded_5_crates_to_nia_status_void_must_return_goods).",
            "source_record_text_atom(src_line_003, entry_3_nia_returned_5_crates_to_omar_status_settled).",
            "ledger_entry(entry_1, 2026_01_01).",
            "record_status(entry_1, valid).",
            "ledger_entry(entry_2, 2026_01_02).",
            "record_status(entry_2, void).",
            "ledger_entry(entry_3, 2026_01_03).",
            "record_status(entry_3, settled).",
        ],
    )

    report = audit_compile(compile_json)

    contract = next(
        row for row in report["relation_contracts"] if row["contract"] == "repeated_record_detail_delivery_contract"
    )
    assert contract["status"] == "shallow_record_detail_delivery"
    assert contract["record_anchor_count"] == 3
    assert contract["complete_anchor_count"] == 0
    assert "entry_2:item_or_value,participant" in contract["missing_keys"]


def test_audit_compile_surface_invariants_passes_repeated_record_detail_contract(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_line_001, entry_1_lee_traded_4_boxes_to_mira_status_valid).",
            "source_record_text_atom(src_line_002, entry_2_omar_traded_5_crates_to_nia_status_void_must_return_goods).",
            "source_record_text_atom(src_line_003, entry_3_nia_returned_5_crates_to_omar_status_settled).",
            "ledger_entry(entry_1, 2026_01_01).",
            "record_participant(entry_1, lee, sender).",
            "record_item(entry_1, boxes, 4).",
            "record_status(entry_1, valid).",
            "ledger_entry(entry_2, 2026_01_02).",
            "record_participant(entry_2, omar, sender).",
            "record_item(entry_2, crates, 5).",
            "record_status(entry_2, void).",
            "ledger_entry(entry_3, 2026_01_03).",
            "record_participant(entry_3, nia, sender).",
            "record_item(entry_3, crates, 5).",
            "record_status(entry_3, settled).",
        ],
    )

    report = audit_compile(compile_json)

    contract = next(
        row for row in report["relation_contracts"] if row["contract"] == "repeated_record_detail_delivery_contract"
    )
    assert contract["status"] == "pass"
    assert contract["complete_anchor_count"] == 3


def test_audit_compile_surface_invariants_detects_financial_baseline_gap(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_line_001, starting_balance_420000_after_actual_expenditure_22000_resulting_balance_398000_minimum_policy_200000).",
            "fund_balance(fund_1, 398000).",
            "policy_threshold(fund_1, minimum, 200000).",
        ],
    )

    report = audit_compile(compile_json)

    finance = next(row for row in report["families"] if row["family"] == "financial_baseline_surface")
    assert finance["status"] == "partial"
    assert "adjustment_value" in finance["missing_groups"]
    assert "scenario_or_actuality" in finance["missing_groups"]
    contract = next(
        row for row in report["relation_contracts"] if row["contract"] == "financial_baseline_derivation_contract"
    )
    assert contract["status"] == "partial"
    assert "adjustment_value" in contract["missing_keys"]
    assert "scenario_or_basis" in contract["missing_keys"]


def test_audit_compile_surface_invariants_passes_financial_baseline_surface(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_line_001, starting_balance_420000_after_actual_expenditure_22000_resulting_balance_398000_minimum_policy_200000).",
            "baseline_balance(fund_1, starting, 420000).",
            "balance_adjustment(fund_1, actual_expenditure, 22000).",
            "scenario_assumption(actual, after_expenditure).",
            "resulting_balance(fund_1, actual_after_expenditure, 398000).",
            "policy_threshold(fund_1, minimum, 200000).",
        ],
    )

    report = audit_compile(compile_json)

    finance = next(row for row in report["families"] if row["family"] == "financial_baseline_surface")
    assert finance["status"] == "pass"
    contract = next(
        row for row in report["relation_contracts"] if row["contract"] == "financial_baseline_derivation_contract"
    )
    assert contract["status"] == "pass"


def test_audit_compile_surface_invariants_detects_quantity_value_delivery_gap(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_line_001, packet_alpha_total_applications_six_threshold_four).",
            "answer_detail(packet_alpha, count_summary).",
        ],
    )

    report = audit_compile(compile_json)

    contract = next(
        row for row in report["relation_contracts"] if row["contract"] == "quantity_value_delivery_contract"
    )
    assert contract["status"] == "shallow_quantity_value_delivery"
    assert contract["source_signal_count"] == 1
    assert contract["complete_quantity_row_count"] == 0
    assert contract["wrapper_predicates"] == ["answer_detail"]


def test_audit_compile_surface_invariants_detects_offered_quantity_carrier_not_delivered(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_line_001, ev_01_feed_rate_increased_to_18_kg_min).",
            "event_description(ev_01, feed_rate_increased_to_18_kg_min).",
        ],
        candidate_predicates=["event_description/2", "event_measurement/4"],
    )

    report = audit_compile(compile_json)

    contract = next(
        row for row in report["relation_contracts"] if row["contract"] == "quantity_value_delivery_contract"
    )
    assert contract["status"] == "quantity_palette_offered_but_undelivered"
    assert contract["candidate_quantity_carriers"] == ["event_measurement/4"]
    assert contract["wrapper_predicates"] == ["event_description"]


def test_audit_compile_surface_invariants_passes_quantity_value_delivery_surface(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_line_001, packet_alpha_total_applications_six_threshold_four).",
            "application_count(packet_alpha, total_applications, 6, source_line_001).",
            "review_threshold(packet_alpha, minimum_applications, 4, source_line_001).",
        ],
    )

    report = audit_compile(compile_json)

    contract = next(
        row for row in report["relation_contracts"] if row["contract"] == "quantity_value_delivery_contract"
    )
    assert contract["status"] == "pass"
    assert contract["source_signal_count"] == 1
    assert contract["complete_quantity_row_count"] == 2
    assert contract["direct_predicates"] == ["application_count", "review_threshold"]


def test_audit_compile_surface_invariants_accepts_specific_two_slot_quantity_predicate(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_line_001, lot_alpha_initial_count_40_plants).",
            "lot_initial_count(lot_alpha, 40).",
        ],
    )

    report = audit_compile(compile_json)

    contract = next(
        row for row in report["relation_contracts"] if row["contract"] == "quantity_value_delivery_contract"
    )
    assert contract["status"] == "pass"
    assert contract["direct_predicates"] == ["lot_initial_count"]


def test_audit_compile_surface_invariants_ignores_source_line_numbers_as_quantity_values(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_line_002, section_2_has_heading_overview).",
            "section_title(section_2, overview).",
        ],
    )

    report = audit_compile(compile_json)

    contract = next(
        row for row in report["relation_contracts"] if row["contract"] == "quantity_value_delivery_contract"
    )
    assert contract["status"] == "not_applicable"


def test_audit_compile_surface_invariants_ignores_record_heading_numbers_and_labels(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_line_001, heading 3 subject_after_hours_access_log).",
            "source_record_text_atom(src_line_002, labeled_line 5 compiled_by_registrar).",
            "source_record_text_atom(src_line_003, table_row 7 date).",
            "access_log(log_alpha).",
        ],
    )

    report = audit_compile(compile_json)

    contract = next(
        row for row in report["relation_contracts"] if row["contract"] == "quantity_value_delivery_contract"
    )
    assert contract["status"] == "not_applicable"


def test_audit_compile_surface_invariants_detects_missing_source_attributed_claim(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_line_001, according_to_rivera_memo_device_alpha_status_active).",
            "device_status(device_alpha, active).",
        ],
    )

    report = audit_compile(compile_json)

    contract = next(
        row for row in report["relation_contracts"] if row["contract"] == "source_attributed_claim_contract"
    )
    assert contract["status"] == "missing_source_reference_surface"
    assert contract["source_signal_count"] == 1
    assert contract["structural_row_count"] == 0


def test_audit_compile_surface_invariants_passes_source_attributed_claim_surface(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_line_001, according_to_rivera_memo_device_alpha_status_active).",
            "source_attributed_claim(claim_1, rivera_memo, device_alpha_status_active, src_line_001).",
        ],
    )

    report = audit_compile(compile_json)

    contract = next(
        row for row in report["relation_contracts"] if row["contract"] == "source_attributed_claim_contract"
    )
    assert contract["status"] == "pass"
    assert contract["structural_predicates"] == ["source_attributed_claim"]


def test_audit_compile_surface_invariants_ignores_unattributed_status_rows(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_line_001, device_alpha_status_active).",
            "device_status(device_alpha, active).",
        ],
    )

    report = audit_compile(compile_json)

    contract = next(
        row for row in report["relation_contracts"] if row["contract"] == "source_attributed_claim_contract"
    )
    assert contract["status"] == "not_applicable"


def test_audit_compile_surface_invariants_detects_participant_statement_gap(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_line_001, participant_lee_said_the_plan_is_too_costly_as_a_concern_during_the_meeting).",
            "meeting_event(meeting_1, 2026_01_03).",
        ],
    )

    report = audit_compile(compile_json)

    surface = next(row for row in report["families"] if row["family"] == "participant_statement_surface")
    assert surface["status"] == "partial"
    assert "speaker_or_actor" in surface["missing_groups"]
    assert "speech_act_or_record_type" in surface["missing_groups"]
    assert "content_or_position" in surface["missing_groups"]


def test_audit_compile_surface_invariants_passes_participant_statement_surface(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_line_001, participant_lee_said_the_plan_is_too_costly_as_a_concern_during_the_meeting).",
            "participant_statement(lee, meeting_1, opposed, plan_cost_too_high, informational).",
            "statement_context(meeting_1, 2026_01_03, translated).",
        ],
    )

    report = audit_compile(compile_json)

    surface = next(row for row in report["families"] if row["family"] == "participant_statement_surface")
    assert surface["status"] == "pass"


def test_audit_compile_surface_invariants_detects_shallow_status_state_surface(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_line_001, record_alpha_status_suspect_on_2026_09_15).",
            "source_record_text_atom(src_line_002, record_beta_status_cleared_on_2026_09_05).",
            "record_status(record_alpha, suspect).",
            "record_status(record_beta, cleared).",
        ],
    )

    report = audit_compile(compile_json)

    surface = next(row for row in report["families"] if row["family"] == "status_state_surface")
    assert surface["status"] == "pass"
    contract = next(row for row in report["relation_contracts"] if row["contract"] == "status_state_scope_contract")
    assert contract["status"] == "shallow_status_state_surface"
    assert contract["required_key_count"] == 2
    assert contract["complete_status_row_count"] == 0
    assert "record_status[1]:temporal_or_source_scope" in contract["missing_keys"]


def test_audit_compile_surface_invariants_passes_status_state_scope_contract(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_line_001, record_alpha_status_suspect_on_2026_09_15).",
            "source_record_text_atom(src_line_002, record_beta_status_cleared_on_2026_09_05).",
            "record_status_at(record_alpha, suspect, 2026_09_15).",
            "record_status_at(record_beta, cleared, 2026_09_05).",
        ],
    )

    report = audit_compile(compile_json)

    surface = next(row for row in report["families"] if row["family"] == "status_state_surface")
    assert surface["status"] == "pass"
    contract = next(row for row in report["relation_contracts"] if row["contract"] == "status_state_scope_contract")
    assert contract["status"] == "pass"
    assert contract["complete_status_row_count"] == 2


def test_audit_compile_surface_invariants_detects_statement_status_gap(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_line_001, witness_statement_is_advisory_not_binding).",
            "participant_statement(statement_1, witness_1, hearing_1, content_value).",
        ],
    )

    report = audit_compile(compile_json)

    contract = next(
        row for row in report["relation_contracts"] if row["contract"] == "participant_statement_status_contract"
    )
    assert contract["status"] == "missing_status_companion"
    assert contract["missing_keys"] == ["participant_statement[1]"]


def test_audit_compile_surface_invariants_passes_statement_status_contract(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_line_001, witness_statement_is_advisory_not_binding).",
            "participant_statement(statement_1, witness_1, hearing_1, content_value).",
            "statement_epistemic_status(statement_1, advisory).",
        ],
    )

    report = audit_compile(compile_json)

    contract = next(
        row for row in report["relation_contracts"] if row["contract"] == "participant_statement_status_contract"
    )
    assert contract["status"] == "pass"


def test_audit_compile_surface_invariants_ignores_statement_language_components(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "source_record_text_atom(src_line_001, translated_statement_is_advisory_not_binding).",
            "statement_original(statement_1, raw_text).",
            "statement_translation(statement_1, translated_text).",
            "statement_language(statement_1, indonesian).",
            "participant_statement(statement_1, witness_1, hearing_1, translated_text).",
            "statement_epistemic_status(statement_1, advisory).",
        ],
    )

    report = audit_compile(compile_json)

    contract = next(
        row for row in report["relation_contracts"] if row["contract"] == "participant_statement_status_contract"
    )
    assert contract["status"] == "pass"
    assert contract["required_key_count"] == 1


def test_audit_compile_surface_invariants_detects_access_source_pair_gap(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "access_authorized_to(item_1, requester_a, physical).",
            "access_source(item_1, requester_a, order_7).",
            "access_authorized_to(item_2, requester_a, observation_only).",
        ],
    )

    report = audit_compile(compile_json)

    contract = next(row for row in report["relation_contracts"] if row["contract"] == "access_authority_source_pair")
    assert contract["status"] == "partial"
    assert contract["required_key_count"] == 2
    assert contract["companion_key_count"] == 1
    assert contract["missing_keys"] == [("item_2", "requester_a")]


def test_audit_compile_surface_invariants_passes_access_source_pair_contract(tmp_path: Path) -> None:
    compile_json = _write_compile(
        tmp_path / "compile.json",
        [
            "access_authorized_to(item_1, requester_a, physical).",
            "access_source(item_1, requester_a, order_7).",
        ],
    )

    report = audit_compile(compile_json)

    contract = next(row for row in report["relation_contracts"] if row["contract"] == "access_authority_source_pair")
    assert contract["status"] == "pass"


def test_summarize_reports_counts_family_statuses(tmp_path: Path) -> None:
    first = audit_compile(
        _write_compile(
            tmp_path / "first.json",
            [
                "source_record_text_atom(src_line_001, sensor_vendor_model).",
                "sensor_info(s1, vendor_a, model_b).",
            ],
        )
    )
    second = audit_compile(
        _write_compile(
            tmp_path / "second.json",
            ["source_record_text_atom(src_line_001, sensor_vendor_model)."],
        )
    )

    summary = summarize_reports([first, second])

    assert summary["family_status_counts"]["object_device_surface"]["pass"] == 1
    assert summary["family_status_counts"]["object_device_surface"]["ledger_only"] == 1
    assert summary["relation_contract_status_counts"]["quantity_value_delivery_contract"]["not_applicable"] == 2
    assert summary["relation_contract_status_counts"]["source_attributed_claim_contract"]["not_applicable"] == 2
