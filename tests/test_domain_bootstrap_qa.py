from pathlib import Path

from scripts.run_domain_bootstrap_qa import (
    POST_INGESTION_QA_QUERY_STRATEGY,
    _assessment_revenue_companion,
    _assessment_transfer_policy_companion,
    _classification_deferral_effect_companion,
    _conversion_assessment_delta_companion,
    _clinic_device_recall_companion,
    _industrial_sensor_companion,
    _negative_join_with_previous,
    _placeholder_repaired_query,
    _relaxed_constant_query,
    _temporal_join_with_previous,
    _vacancy_voting_eligibility_companion,
    cache_key_for_question,
    clause_signature,
    compiled_kb_inventory,
    hash_text,
    is_cacheable_row,
    parse_markdown_answer_key,
    parse_numbered_markdown_questions,
    read_cached_row,
    run_query_plan,
    score_oracle,
    summarize,
    summarize_helper_classes,
    write_cached_row,
)
from kb_pipeline import CorePrologRuntime


def test_parse_numbered_markdown_questions_keeps_phase_labels() -> None:
    text = """# Phase 1 - Straight Queries

1. Which items were explicitly declared recalled?
2. Who is the authority accused of wrongdoing?

# Phase 2 - Ambiguity

16. Who is K. Lume?

## Answers 1-16

1. Batch P-44.
16. Unknown unless resolved.
"""

    rows = parse_numbered_markdown_questions(text)

    assert [row["id"] for row in rows] == ["q001", "q002", "q016"]
    assert rows[0]["phase"] == "Phase 1 - Straight Queries"
    assert rows[2]["phase"] == "Phase 2 - Ambiguity"
    assert rows[2]["utterance"] == "Who is K. Lume?"


def test_parse_markdown_answer_key_reads_answer_section_only() -> None:
    text = """# Questions

1. Which items were recalled?
2. Who signed?

## Answers 1-2

1. Batch P-44 and the welcome loaf.
2. Unknown until K. Lume is resolved.
"""

    answers = parse_markdown_answer_key(text)

    assert answers == {
        "q001": "Batch P-44 and the welcome loaf.",
        "q002": "Unknown until K. Lume is resolved.",
    }


def test_reference_answers_are_not_structured_oracle_expectations() -> None:
    row = {"projected_decision": "answer", "queries": [], "query_results": []}

    assert score_oracle(row=row, oracle={"reference_answer": "Unknown."}) is None


def test_qa_cache_key_changes_when_question_changes() -> None:
    context = {
        "schema_version": "domain_bootstrap_qa_cache_v1",
        "script_hash": hash_text("script"),
        "run_hash": hash_text("run"),
        "qa_hash": hash_text("qa"),
        "config": {"model": "model"},
    }
    oracle = {"reference_answer": "A"}
    first = cache_key_for_question(
        context=context,
        item={"id": "q001", "utterance": "Who signed?"},
        oracle=oracle,
    )
    second = cache_key_for_question(
        context=context,
        item={"id": "q001", "utterance": "Who signed it?"},
        oracle=oracle,
    )

    assert first != second


def test_qa_cache_row_round_trips(tmp_path) -> None:
    row = {"id": "q001", "ok": True, "queries": ["p(X)."], "reference_judge": {"verdict": "exact"}}

    assert is_cacheable_row(row) is True
    write_cached_row(cache_dir=tmp_path, cache_key="abc", row=row)

    assert read_cached_row(cache_dir=tmp_path, cache_key="abc") == row


def test_compiled_kb_inventory_uses_clause_surfaces_not_english() -> None:
    facts = [
        "affected_item(grievance_1, batch_p_44).",
        "claimed_label(grievance_1, plain_oat_ration).",
    ]
    rules = ["can_depart(Batch) :- affected_item(G, Batch), claimed_label(G, plain_oat_ration)."]

    inventory = compiled_kb_inventory(facts=facts, rules=rules)

    assert clause_signature(rules[0]) == "can_depart/1"
    assert inventory["signatures"] == ["affected_item/2", "can_depart/1", "claimed_label/2"]
    assert inventory["examples"]["affected_item/2"] == ["affected_item(grievance_1, batch_p_44)."]
    assert "affected_item(X, Y)." in inventory["query_templates"]
    assert "can_depart(X)." in inventory["query_templates"]


def test_post_ingestion_qa_strategy_prefers_compiled_kb_surface() -> None:
    strategy = POST_INGESTION_QA_QUERY_STRATEGY

    assert strategy["name"] == "post_ingestion_qa_query_strategy_v1"
    assert "compiled_predicate_inventory.signatures" in " ".join(strategy["predicate_surface_policy"])
    assert "relevant_clauses" in " ".join(strategy["predicate_surface_policy"])
    assert any("full compiled predicate arity" in item for item in strategy["arity_and_variable_policy"])
    assert any("Do not pre-fill an answer slot" in item for item in strategy["arity_and_variable_policy"])
    assert any("Do not over-constrain descriptive label slots" in item for item in strategy["arity_and_variable_policy"])
    assert any("record id too early" in item for item in strategy["arity_and_variable_policy"])
    assert any("source-owned record predicates" in item for item in strategy["arity_and_variable_policy"])
    assert any("institution, ledger, record, or source questions" in item for item in strategy["arity_and_variable_policy"])
    assert any("who-reported or reporter questions" in item for item in strategy["arity_and_variable_policy"])
    assert any("longer normalized atom" in item for item in strategy["arity_and_variable_policy"])
    assert any("grievance(Grievance, Label)" in item for item in strategy["arity_and_variable_policy"])
    assert any("source-attributed claims" in item for item in strategy["epistemic_policy"])
    assert any("policy_requirement/3" in item for item in strategy["epistemic_policy"])
    assert "elapsed_days" in " ".join(strategy["epistemic_policy"])
    assert any("alternate atom order" in item for item in strategy["arity_and_variable_policy"])
    assert any("federal_agency_authority" in item for item in strategy["epistemic_policy"])
    assert any("conflict_policy" in item for item in strategy["epistemic_policy"])
    assert any("witness_statement(Speaker, Language" in item for item in strategy["epistemic_policy"])
    assert any("extension_reason" in item for item in strategy["epistemic_policy"])
    assert any("subgrant_amount" in item for item in strategy["epistemic_policy"])
    assert any("prior_complaint/4" in item for item in strategy["epistemic_policy"])


def test_reference_judge_policy_treats_normalized_purpose_atoms_as_answer_bearing() -> None:
    source = Path("scripts/run_domain_bootstrap_qa.py").read_text(encoding="utf-8")

    assert "Purpose/action atom policy" in source
    assert "fetching_fog_leaves" in source


def test_score_oracle_can_match_decision_predicate_and_answer_text() -> None:
    row = {
        "projected_decision": "answer",
        "queries": ["declares_recalled(flour_moon_seven, X)."],
        "query_results": [{"result": {"rows": [{"X": "batch_p_44"}]}}],
    }
    oracle = {
        "expected_decision": "answer",
        "expected_query_predicates": ["declares_recalled"],
        "expected_answer_contains": ["batch_p_44"],
    }

    assert score_oracle(row=row, oracle=oracle) is True


def test_summarize_counts_reference_judge_verdicts() -> None:
    rows = [
        {"ok": True, "queries": ["p(X)."], "reference_answer": "A", "reference_judge": {"verdict": "exact"}},
        {"ok": True, "queries": ["q(X)."], "reference_answer": "B", "reference_judge": {"verdict": "partial"}},
        {"ok": True, "queries": [], "reference_answer": "C", "reference_judge": {"verdict": "miss"}},
    ]

    summary = summarize(rows=rows, load_errors=[], elapsed_ms=12)

    assert summary["judge_rows"] == 3
    assert summary["judge_exact"] == 1
    assert summary["judge_partial"] == 1
    assert summary["judge_miss"] == 1


def test_summarize_counts_helper_class_rows_by_companion() -> None:
    rows = [
        {
            "ok": True,
            "query_results": [
                {
                    "result": {
                        "predicate": "industrial_sensor_support",
                        "rows": [
                            {"SupportKind": "raw_event_count", "HelperClass": "clean-helper"},
                            {"SupportKind": "sensor_vendor_model", "HelperClass": "candidate-helper"},
                        ],
                    }
                },
                {
                    "result": {
                        "predicate": "legacy_support",
                        "rows": [{"SupportKind": "legacy"}],
                    }
                },
            ],
        }
    ]

    helper_summary = summarize_helper_classes(rows)

    assert helper_summary["row_count"] == 3
    assert helper_summary["helper_class_counts"] == {
        "candidate-helper": 1,
        "clean-helper": 1,
        "unlabeled": 1,
    }
    assert helper_summary["companion_helper_class_counts"]["industrial_sensor_support"] == {
        "candidate-helper": 1,
        "clean-helper": 1,
    }


def test_score_oracle_returns_none_without_answer_key() -> None:
    assert score_oracle(row={"queries": []}, oracle={}) is None


def test_temporal_join_builds_dependency_closure_for_derived_threshold() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "facility_status(eastgate_treatment_facility, offline, 2026_03_04t08_00).",
        "eastgate_offline_threshold_hours(6).",
        "boil_water_notice(millbrook, 2026_03_04t14_45, diane_cheng).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    joined = _temporal_join_with_previous(
        runtime,
        previous_queries=[
            "facility_status(eastgate_treatment_facility, offline, Starttime).",
            "eastgate_offline_threshold_hours(Thresholdhours).",
            "add_hours(Starttime, Thresholdhours, Thresholdtime).",
            "boil_water_notice(Zone, Noticetime, Issuer).",
        ],
        query="elapsed_minutes(Thresholdtime, Noticetime, Minutes).",
    )

    assert joined is not None
    result = joined["result"]
    assert result["status"] == "success"
    assert any(str(row.get("Minutes")) == "45" for row in result["rows"])
    assert "facility_status(eastgate_treatment_facility, offline, Starttime)" in joined["query"]
    assert "eastgate_offline_threshold_hours(Thresholdhours)" in joined["query"]


def test_temporal_join_synthesizes_missing_threshold_bridge() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "facility_status(eastgate_treatment_facility, offline, 2026_03_04t08_00).",
        "eastgate_offline_threshold_hours(6).",
        "boil_water_notice(millbrook, 2026_03_04t14_45, diane_cheng).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    joined = _temporal_join_with_previous(
        runtime,
        previous_queries=[
            "facility_status(eastgate_treatment_facility, offline, Starttime).",
            "eastgate_offline_threshold_hours(Thresholdhours).",
            "boil_water_notice(Zone, Noticetime, Issuer).",
        ],
        query="elapsed_minutes(Thresholdtime, Noticetime, Minutes).",
    )

    assert joined is not None
    assert joined["result"]["status"] == "success"
    assert any(str(row.get("Minutes")) == "45" for row in joined["result"]["rows"])
    assert "add_hours(Starttime, Thresholdhours, Thresholdtime)" in joined["query"]


def test_hoa_assessment_revenue_companion_uses_current_counts_and_rates() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "unit_count(single_family, 84).",
        "unit_count(single_family, 96).",
        "unit_count(townhome, 36).",
        "unit_count(townhome, 42).",
        "unit_count(condominium, 24).",
        "unit_count(condominium, 18).",
        "assessment_rate(single_family, 3600).",
        "assessment_rate(townhome, 3600).",
        "assessment_rate(condominium, 2700).",
        "conversion_effective_date(unit_c13, condominium, townhome).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    companion = _assessment_revenue_companion(runtime, predicate="unit_count", query="unit_count(Type, Count).")

    assert companion is not None
    rows = companion["result"]["rows"]
    assert any(row.get("RowKind") == "total" and row.get("TotalRevenue") == "545400" for row in rows)


def test_industrial_sensor_companion_derives_event_and_sensor_support() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    facts = [
        "source_record_field(src_line_0067, event_id, ev_01).",
        "source_record_field(src_line_0067, system, sys_a).",
        "source_record_field(src_line_0067, recorded_time_raw, v_2026_04_22_14_02_13).",
        "source_record_field(src_line_0074, event_id, ev_08).",
        "source_record_field(src_line_0074, system, sys_b).",
        "source_record_field(src_line_0074, recorded_time_raw, v_2026_04_22_15_09_33).",
        "source_record_field(src_line_0075, event_id, ev_09).",
        "source_record_field(src_line_0075, system, sys_a).",
        "source_record_field(src_line_0075, recorded_time_raw, v_2026_04_22_15_14_50).",
        "source_record_field(src_line_0074, description, batch_b_2026_0422_3_flagged_off_spec_by_qis_opt_12).",
        "source_record_field(src_line_0079, event_id, ev_13).",
        "source_record_field(src_line_0079, system, sys_c).",
        "source_record_field(src_line_0079, recorded_time_raw, v_2026_04_22_15_30_00).",
        "source_record_field(src_line_0079, description, maintenance_window_opened_for_sensor_diagnostics_mms_t_2026_0422_1).",
        "source_record_field(src_line_0088, event_id, ev_01).",
        "source_record_field(src_line_0088, wall_clock_time_utc_corrected, v_2026_04_22_14_01_26).",
        "source_record_field(src_line_0095, event_id, ev_08).",
        "source_record_field(src_line_0095, wall_clock_time_utc_corrected, v_2026_04_22_15_11_51).",
        "source_record_field(src_line_0096, event_id, ev_09).",
        "source_record_field(src_line_0096, wall_clock_time_utc_corrected, v_2026_04_22_15_14_03).",
        "source_record_line(src_line_0095, 95).",
        "source_record_section(src_line_0095, section_4_corrected_timeline).",
        "source_record_text_atom(src_line_0160, of_ev_08_or_ev_12_those_originated_from_qis_opt_12_automatic_flagging).",
        "sensor_id(hum_d_04).",
        "sensor_id(qis_opt_12).",
        "source_record_line(src_line_0118, 118).",
        "source_record_label(src_line_0118, qis_opt_12).",
        "source_record_section(src_line_0118, v_5_1_qis_opt_12_calibration_2026_04_15).",
        "source_record_line(src_line_0120, 120).",
        "source_record_label(src_line_0120, mms_t_2026_0414_3).",
        "source_record_section(src_line_0120, v_5_1_qis_opt_12_calibration_2026_04_15).",
        "source_record_text_atom(src_line_0120, calibration_ticket_mms_t_2026_0414_3_the_line_continued_to_operate).",
        "source_record_line(src_line_0219, 219).",
        "source_record_label(src_line_0219, hum_d_04).",
        "source_record_section(src_line_0219, section_9_sensor_register_excerpts).",
        "source_record_text_atom(src_line_0219, hum_d_04_vendor_sentec_model_sentec_rh_220_plus_location).",
        "source_record_line(src_line_0223, 223).",
        "source_record_label(src_line_0223, next_calibration_due_2026_07_12).",
        "source_record_section(src_line_0223, section_9_sensor_register_excerpts).",
        "source_record_text_atom(src_line_0223, next_calibration_due_2026_07_12).",
        "source_record_text_atom(src_line_0255, v_2026_04_25_buffer_overflow_on_dry_dl_04_confirmed_by_maintenance_team_no_recovery).",
        "source_record_text_atom(src_line_0264, compliance_packet_id_mpp_comp_2026_0427_the_two_packets_cover_the).",
    ]
    for fact in facts:
        assert runtime.assert_fact(fact).get("status") == "success"

    companion = _industrial_sensor_companion(
        runtime,
        predicate="source_record_field",
        args=[],
        query="source_record_field(SourceRow, Header, Value).",
    )

    assert companion is not None
    rows = companion["result"]["rows"]
    details = " ".join(str(row.get("Detail", "")) for row in rows)
    assert any(
        row.get("SupportKind") == "raw_event_count"
        and row.get("Value") == "4"
        and row.get("HelperClass") == "clean-helper"
        for row in rows
    )
    assert any(
        row.get("SupportKind") == "corrected_event_time"
        and row.get("Subject") == "EV-08"
        and row.get("HelperClass") == "clean-helper"
        for row in rows
    )
    assert any(
        row.get("SupportKind") == "sensor_vendor_model"
        and row.get("Subject") == "HUM-D-04"
        and row.get("HelperClass") == "clean-helper"
        for row in rows
    )
    assert any(
        row.get("SupportKind") == "sensor_register_section"
        and row.get("Subject") == "HUM-D-04"
        and row.get("HelperClass") == "clean-helper"
        for row in rows
    )
    assert any(
        row.get("SupportKind") == "regulatory_packet_identifier"
        and row.get("HelperClass") == "candidate-helper"
        for row in rows
    )
    assert any(
        row.get("SupportKind") == "sensor_next_calibration"
        and row.get("Subject") == "HUM-D-04"
        and row.get("HelperClass") == "clean-helper"
        for row in rows
    )
    assert any(
        row.get("SupportKind") == "sensor_calibration_ticket"
        and row.get("Subject") == "QIS-OPT-12"
        and row.get("HelperClass") == "clean-helper"
        for row in rows
    )
    assert any(
        row.get("SupportKind") == "event_batch_identifier"
        and row.get("Subject") == "EV-08"
        and row.get("HelperClass") == "clean-helper"
        for row in rows
    )
    assert any(
        row.get("SupportKind") == "event_maintenance_ticket"
        and row.get("Subject") == "EV-13"
        and row.get("HelperClass") == "clean-helper"
        for row in rows
    )
    assert "2 minutes 12 seconds" in details
    assert "Vendor Sentec; model Sentec RH-220-Plus." in details
    assert "Next calibration due 2026-07-12." in details
    assert "MPP-COMP-2026-0427" in details
    assert "R. Kim did not originate EV-08 or EV-12" in details


def test_clinic_recall_companion_derives_official_source_record_support() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    facts = [
        "source_record_text_atom(src_line_0021, high_viscosity_infusates_failure_rate_observed_in_field_returns_0_7_per).",
        "source_record_text_atom(src_line_0027, manufacturer_contact_k_halberg_regional_liaison_eastern_network).",
        "source_record_text_atom(src_line_0075, epa_eastfield_pediatric_associates).",
        "source_record_text_atom(src_line_0116, procedure_mv_vp_04_a).",
        "source_record_text_atom(src_line_0196, been_sealed_with_tamper_evident_tape_seal_numbers_seal_nbfh_04_001).",
        "source_record_text_atom(src_line_0197, through_seal_nbfh_04_003_one_seal_per_shelf_i_will_retain_the_keys).",
        "source_record_text_atom(src_line_0230, issue_the_formal_release_for_verified_devices_at_the_network_level_once).",
        "source_record_field(src_line_0063, device_id, mp_009).",
        "source_record_field(src_line_0063, serial, v_4501_aa_100158).",
        "source_record_section(src_line_0230, v_8_3_network_medical_director_reply).",
        "source_record_line(src_line_0230, 230).",
    ]
    for fact in facts:
        assert runtime.assert_fact(fact).get("status") == "success"

    companion = _clinic_device_recall_companion(
        runtime,
        predicate="source_record_text_atom",
        args=[],
        query="source_record_text_atom(SourceRow, TextAtom).",
    )

    assert companion is not None
    rows = companion["result"]["rows"]
    details = " ".join(str(row.get("Detail", "")) for row in rows)
    assert any(
        row.get("SupportKind") == "device_serial_lookup"
        and row.get("Subject") == "MP-009"
        and row.get("HelperClass") == "clean-helper"
        for row in rows
    )
    assert any(
        row.get("SupportKind") == "manufacturer_liaison"
        and row.get("Value") == "K. Halberg"
        and row.get("HelperClass") == "candidate-helper"
        for row in rows
    )
    assert any(
        row.get("SupportKind") == "quarantine_seal_range"
        and row.get("HelperClass") == "candidate-helper"
        for row in rows
    )
    assert "K. Halberg" in details
    assert "0.7 per 1,000 hours of use" in details
    assert "EPA = Eastfield Pediatric Associates" in details
    assert "MV-VP-04-A" in details
    assert "SEAL-NBFH-04-001 through SEAL-NBFH-04-003" in details
    assert "MP-009 has serial 4501-AA-100158" in details


def test_hoa_conversion_assessment_delta_companion_derives_rate_increase() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "unit_count(townhome, 36).",
        "unit_count(townhome, 42).",
        "unit_count(condominium, 24).",
        "unit_count(condominium, 18).",
        "assessment_rate(townhome, 3600).",
        "assessment_rate(condominium, 2700).",
        "conversion_effective_date(unit_c13, condominium, townhome).",
        "conversion_effective_date(unit_c14, condominium, townhome).",
        "conversion_effective_date(unit_c15, condominium, townhome).",
        "conversion_effective_date(unit_c16, condominium, townhome).",
        "conversion_effective_date(unit_c17, condominium, townhome).",
        "conversion_effective_date(unit_c18, condominium, townhome).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    companion = _conversion_assessment_delta_companion(
        runtime,
        predicate="conversion_effective_date",
        query="conversion_effective_date(Unit, condominium, townhome).",
    )

    assert companion is not None
    assert companion["result"]["rows"][0]["RateDelta"] == "900"
    assert companion["result"]["rows"][0]["RevenueDelta"] == "5400"


def test_hoa_classification_deferral_companion_exposes_current_effect() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "unit_count(total, 156).",
        "classification_deferred(lot_52, pending_review).",
        "conditional_outcome(lot_52_reclassification, reclassified, count_157_revenue_549000).",
        "conditional_outcome(lot_52_reclassification, count_becomes_157, revenue_increase_3600).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    companion = _classification_deferral_effect_companion(
        runtime,
        predicate="classification_deferred",
        query="classification_deferred(lot_52, Status).",
    )

    assert companion is not None
    row = companion["result"]["rows"][0]
    assert row["CurrentAssessments"] == "1"
    assert row["AdditionalUnitsIfReclassified"] == "1"


def test_vacancy_voting_eligibility_companion_preserves_all_units_vote_surface() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "voting_eligibility(all_units, eligible).",
        "occupancy_status(lot_91, vacant).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    companion = _vacancy_voting_eligibility_companion(
        runtime,
        predicate="voting_eligibility",
        query="voting_eligibility(X, Y).",
    )

    assert companion is not None
    assert companion["result"]["rows"][0]["VacancyAffectsEligibility"] == "no"
    assert companion["result"]["rows"][0]["VacantUnitsCarryVotes"] == "yes"


def test_assessment_transfer_policy_companion_detects_seller_buyer_boundary() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "assessment_responsibility(lot_47, eriksen_family, 2025_01_01, 2025_01_22).",
        "assessment_responsibility(lot_47, chao_family, 2025_01_23, 2025_03_01).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    companion = _assessment_transfer_policy_companion(
        runtime,
        predicate="assessment_responsibility",
        query="assessment_responsibility(Unit, Party, StartDate, EndDate).",
    )

    assert companion is not None
    row = companion["result"]["rows"][0]
    assert row["SellerResponsibleThrough"] == "2025_01_22"
    assert row["BuyerResponsibleFrom"] == "2025_01_23"
    assert row["PolicyPattern"] == "seller_through_closing_buyer_from_day_after"


def test_temporal_join_adds_minute_precision_for_elapsed_hours() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "facility_status(eastgate_treatment_facility, offline, 2026_03_04t08_00).",
        "eastgate_offline_threshold_hours(6).",
        "boil_water_notice(millbrook, 2026_03_04t14_45, diane_cheng).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    joined = _temporal_join_with_previous(
        runtime,
        previous_queries=[
            "facility_status(eastgate_treatment_facility, offline, Starttime).",
            "eastgate_offline_threshold_hours(Thresholdhours).",
            "boil_water_notice(Zone, Noticetime, Issuer).",
        ],
        query="elapsed_hours(Thresholdtime, Noticetime, Elapsedhours).",
    )

    assert joined is not None
    assert "elapsed_minutes(Thresholdtime, Noticetime, Minutes)" in joined["query"]
    assert any(
        str(row.get("Elapsedhours")) == "0" and str(row.get("Minutes")) == "45"
        for row in joined["result"]["rows"]
    )


def test_temporal_join_disambiguates_relaxed_source_slots_for_duration_helpers() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "notice_issued(bwn_2026_04_28_a, 2026_04_28_08_00, e_02).",
        "notice_lifted(bwn_2026_04_28_a, 2026_05_04_12_00, e_12).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    joined = _temporal_join_with_previous(
        runtime,
        previous_queries=[
            "notice_issued(Relaxed1, Issuedtime, Relaxed3).",
            "notice_lifted(Relaxed1, Lifttime, Relaxed3).",
        ],
        query="elapsed_hours(Issuedtime, Lifttime, Totalhours).",
    )

    assert joined is not None
    assert "Relaxed3Join1" in joined["query"]
    assert "Relaxed3Join2" in joined["query"]
    assert any(
        str(row.get("Totalhours")) == "148" and str(row.get("Minutes")) == "8880"
        for row in joined["result"]["rows"]
    )


def test_placeholder_repair_promotes_lowercase_temporal_helper_slots() -> None:
    repaired = _placeholder_repaired_query("elapsed_hours(issuedtimestamp, liftedtimestamp, totalhours).")

    assert repaired is not None
    assert repaired["query"] == "elapsed_hours(Issuedtimestamp, Liftedtimestamp, Totalhours)."


def test_run_query_plan_keeps_placeholder_repairs_before_relaxed_temporal_join() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "notice_issued(bwn_2026_04_28_a, 2026_04_28_08_00, e_02).",
        "notice_lifted(bwn_2026_04_28_a, 2026_05_04_12_00, e_12).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = run_query_plan(
        runtime,
        [
            "notice_issued(bwn_2026_04_28_a, issuedtimestamp, issuedevent).",
            "notice_lifted(bwn_2026_04_28_a, liftedtimestamp, liftedevent).",
            "elapsed_hours(issuedtimestamp, liftedtimestamp, Totalhours).",
        ],
    )

    joined = [item for item in results if "elapsed_minutes" in item.get("query", "")]
    assert joined
    assert any(str(row.get("Totalhours")) == "148" for row in joined[-1]["result"]["rows"])


def test_temporal_join_localizes_repeated_event_id_provenance_variables() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "notice_issued(bwn_2026_04_28_a, 2026_04_28_08_00, e_02).",
        "notice_lifted(bwn_2026_04_28_a, 2026_05_04_12_00, e_12).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    joined = _temporal_join_with_previous(
        runtime,
        previous_queries=[
            "notice_issued(bwn_2026_04_28_a, Issuedtimestamp, Eventid).",
            "notice_lifted(bwn_2026_04_28_a, Liftedtimestamp, Eventid).",
        ],
        query="elapsed_hours(Issuedtimestamp, Liftedtimestamp, Totalhours).",
    )

    assert joined is not None
    assert "EventidJoin1" in joined["query"]
    assert "EventidJoin2" in joined["query"]
    assert any(str(row.get("Totalhours")) == "148" for row in joined["result"]["rows"])


def test_clear_sample_clock_pause_companion_derives_counted_hours_during_pause() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "rule_exception(rule_6_2a, clock_pauses_on_sampler_offline).",
        "clear_sample_segment(cs_seg_1, 2026_04_30_15_00, 2026_05_01_09_00, 18).",
        "sampler_offline_interval(station_s_3, 2026_05_01_09_00, 2026_05_01_11_00, routine_sampler_maintenance).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = run_query_plan(
        runtime,
        [
            "clear_sample_segment(Segmentid, start, end, Nominalhours).",
            "sampler_offline_interval(station, start, end, cause).",
        ],
    )

    support = [item for item in results if item.get("result", {}).get("predicate") == "clear_sample_clock_pause_support"]
    assert support
    row = support[-1]["result"]["rows"][0]
    assert row["ClockState"] == "paused"
    assert row["Rule"] == "rule_6_2a"
    assert row["CountedHours"] == "18"
    assert row["PauseStart"] == "2026_05_01_09_00"


def test_authority_custody_companion_counts_grouped_physical_custody() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "physical_custody(notebook_b, pellico_society).",
        "physical_custody(letters_at_pellico_16, pellico_society).",
        "physical_custody(personal_letters, pellico_society).",
        "physical_custody(loose_photos_18, pellico_society).",
        "physical_custody(personal_letter_1903_04_11, stille_conservation_studio).",
        "physical_custody(notebook_a, stille_conservation_studio).",
        "physical_custody(letters_at_stille, stille_conservation_studio).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = run_query_plan(runtime, ["physical_custody(Item, pellico_society)."])

    support = [item for item in results if item.get("result", {}).get("predicate") == "archive_authority_custody_support"]
    assert support
    rows = support[-1]["result"]["rows"]
    pellico = next(row for row in rows if row.get("SupportKind") == "physical_custody_count" and row.get("Holder") == "pellico_society")
    assert pellico["Count"] == "35"
    assert "letters_at_pellico_16:16" in pellico["Components"]
    assert "loose_photos_18:18" in pellico["Components"]
    stille = next(row for row in rows if row.get("SupportKind") == "physical_custody_count" and row.get("Holder") == "stille_conservation_studio")
    assert stille["Count"] == "10"


def test_authority_custody_companion_surfaces_object_custody_status_rows() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "object_custody_status(crimson_notebooks, hartwell_college_special_collections, physical_possession, 2026_05_04, probate_packet).",
        "object_custody_status(crimson_notebooks, hartwell_college_special_collections, restricted_access, 2026_04_30, probate_packet).",
        "object_custody_status(crimson_notebooks, katherine_hennessy_brown, title_claim, 2026_03_04, probate_packet).",
        "object_custody_status(crimson_notebooks, hartwell_college_special_collections, disputed, 2026_05_04, probate_packet).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = run_query_plan(
        runtime,
        ["object_custody_status(crimson_notebooks, Holder, StatusKind, TimeOrDate, SourceDocument)."],
    )

    support = [item for item in results if item.get("result", {}).get("predicate") == "archive_authority_custody_support"]
    assert support
    rows = support[-1]["result"]["rows"]
    kinds = {row["SupportKind"] for row in rows}
    assert "physical_possession_at_time" in kinds
    assert "access_restriction_status" in kinds
    assert "legal_title_or_ownership_claim" in kinds
    assert "ownership_or_custody_dispute_status" in kinds


def test_authority_custody_companion_pairs_stille_access_with_pellico_authorization() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "physical_custody(letters_at_stille, stille_conservation_studio).",
        "access_log_entry(access_2026_03_11_01, 2026_03_11, dr_k_phenwick, letters_at_stille, stille_premises).",
        "access_authorized_by(access_2026_03_11_01, pellico_society_with_stille_coordination).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = run_query_plan(runtime, ["access_log_entry(Event, 2026_03_11, dr_k_phenwick, Item, Location)."])

    support = [item for item in results if item.get("result", {}).get("predicate") == "archive_authority_custody_support"]
    assert support
    row = next(row for row in support[-1]["result"]["rows"] if row.get("SupportKind") == "access_custody_authorization")
    assert row["Custodian"] == "stille_conservation_studio"
    assert row["AuthorizedBy"] == "pellico_society_with_stille_coordination"


def test_authority_custody_companion_derives_access_support_from_source_record_cells() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "physical_custody(letters_at_stille, stille_conservation_studio).",
        "source_record_cell(src_line_0112, 1, v_2026_03_11).",
        "source_record_cell(src_line_0112, 2, dr_k_phenwick).",
        "source_record_cell(src_line_0112, 3, stille_premises).",
        "source_record_cell(src_line_0112, 4, v_8_letters_under_conservation).",
        "source_record_cell(src_line_0112, 5, pellico_society_with_stille_coordination).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = run_query_plan(runtime, ["source_record_cell(src_line_0112, Column, Value)."])

    support = [item for item in results if item.get("result", {}).get("predicate") == "archive_authority_custody_support"]
    assert support
    row = next(row for row in support[-1]["result"]["rows"] if row.get("SupportKind") == "access_custody_authorization")
    assert row["Custodian"] == "stille_conservation_studio"
    assert row["AuthorizedBy"] == "pellico_society_with_stille_coordination"
    assert row["Item"] == "v_8_letters_under_conservation"


def test_authority_custody_companion_surfaces_recall_and_notice_clauses() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "reserved_right(amendment_2024, pellico_society, recall, right_to_recall_any_item_from_a_contractor_s_custody_on_demand).",
        "custody_recall(photograph_album, stille_conservation_studio, 2026_03_03).",
        "source_record_text_atom(src_line_0040, notice_consent_of_the_trust_shall_not_be_required_for_placement_of_items_into_contractor_custody_but_the_society_shall_notify_the_trust_within_thirty_days_of_any_such_placement_of_personal_correspondence).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = run_query_plan(runtime, ["reserved_right(Document, pellico_society, recall, Description)."])

    support = [item for item in results if item.get("result", {}).get("predicate") == "archive_authority_custody_support"]
    assert support
    rows = support[-1]["result"]["rows"]
    recall = next(row for row in rows if row.get("SupportKind") == "recall_clause_exercised")
    notice = next(row for row in rows if row.get("SupportKind") == "contractor_custody_consent_notice")
    assert recall["AnswerValue"] == "amendment_2024"
    assert recall["Item"] == "photograph_album"
    assert notice["ConsentRequired"] == "no"
    assert notice["NoticeRequired"] == "personal_correspondence_within_30_days"


def test_source_record_clock_sync_companion_derives_last_successful_ntp_sync_date() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "source_record_text_atom(src_line_0106, status_timeline_resolvable_the_building_engineering_office_confirmed_on_2026_04_28_that_pem_bas_7_s_clock_had_drifted_from_ntp_pem_bas_7_s_last_successful_ntp_sync_was_2026_03_19_engineering_s_audit_measured_drift).",
        "source_record_numeric_token(src_line_0106, v_2026_03_19).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = run_query_plan(runtime, ["event_occurred_at(pem_bas_7, ntp_sync, X)."])

    support = [item for item in results if item.get("result", {}).get("predicate") == "source_record_clock_sync_support"]
    assert support
    row = support[-1]["result"]["rows"][0]
    assert row["System"] == "pem_bas_7"
    assert row["SyncKind"] == "last_successful_ntp_sync"
    assert row["Date"] == "2026_03_19"
    assert row["SourceRow"] == "src_line_0106"


def test_temporal_join_supports_elapsed_days_for_inspection_windows() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "inspection(pier_7, luis_ferreira, 2026_02_01).",
        "bypass_authorization(pier_7, luis_ferreira, 2026_03_04t15_30).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    joined = _temporal_join_with_previous(
        runtime,
        previous_queries=[
            "inspection(Facility, Officer, Inspectiondate).",
            "bypass_authorization(Facility, Officer, Authtime).",
        ],
        query="elapsed_days(Inspectiondate, Authtime, Days).",
    )

    assert joined is not None
    assert joined["result"]["status"] == "success"
    assert any(str(row.get("Days")) == "31" for row in joined["result"]["rows"])


def test_temporal_elapsed_placeholder_repair_keeps_lowercase_outputs_queryable() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "extension_request(req_1, 2025_06_20).",
        "deadline_value(nov_1, response, 2025_07_02).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = run_query_plan(
        runtime,
        [
            "extension_request(Request, extensiondate).",
            "deadline_value(Nov, response, originaldeadline).",
            "elapsed_days(Extensiondate, originaldeadline, dayselapsed).",
        ],
    )

    assert any(
        "elapsed_days(Extensiondate, Originaldeadline, Dayselapsed)" in item.get("query", "")
        and any(str(row.get("Dayselapsed")) == "12" for row in item.get("result", {}).get("rows", []))
        for item in results
    )


def test_temporal_join_recovers_from_overconstrained_date_surface() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "proceeding_event(inquiry_committee_first_meeting, february_10_2026, inquiry_committee, first_meeting).",
        "deadline_met(inquiry_report, 2026_02_10, 2026_04_25, yes).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    joined = _temporal_join_with_previous(
        runtime,
        previous_queries=[
            "proceeding_event(inquiry_committee_first_meeting, Starttime, inquiry_committee, first_meeting).",
            "deadline_met(inquiry_report, Starttime, Endtime, Status).",
        ],
        query="elapsed_days(Starttime, Endtime, Elapseddays).",
    )

    assert joined is not None
    assert joined["result"]["status"] == "success"
    assert "over-constraining prior query" in joined["result"]["reasoning_basis"]["note"]
    assert any(str(row.get("Elapseddays")) == "74" for row in joined["result"]["rows"])


def test_negative_query_join_supports_set_difference() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "residential_zone(millbrook).",
        "residential_zone(old_harbor).",
        "boil_water_notice(millbrook, 2026_03_04t14_45, diane_cheng).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    joined = _negative_join_with_previous(
        runtime,
        previous_queries=["residential_zone(Zone)."],
        query="\\+(boil_water_notice(Zone, Time, Issuer)).",
    )

    assert joined is not None
    assert joined["result"]["status"] == "success"
    assert joined["result"]["rows"][0]["Zone"] == "old_harbor"


def test_relaxed_constant_query_recovers_over_bound_atom_drift() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    assert runtime.assert_fact("inspection(pier_7, luis_ferreira, 2026_02_01).").get("status") == "success"

    exact = runtime.query_rows("inspection(pier_7, ferreira_luis, Date).")
    assert exact["status"] == "no_results"

    relaxed = _relaxed_constant_query(runtime, query="inspection(pier_7, ferreira_luis, Date).")

    assert relaxed is not None
    assert relaxed["result"]["status"] == "success"
    assert relaxed["result"]["reasoning_basis"]["kind"] == "core-local"
    assert relaxed["result"]["reasoning_basis"]["original_query"] == "inspection(pier_7, ferreira_luis, Date)."
    assert relaxed["result"]["rows"] == [
        {
            "Relaxed1": "pier_7",
            "Relaxed2": "luis_ferreira",
            "Date": "2026_02_01",
        }
    ]


def test_run_query_plan_derives_recall_classification_at_date() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "recall_classification(recall_oxalis_2026, class_ii, 2026_01_22).",
        "recall_reclassification(recall_oxalis_2026, class_ii, class_i, 2026_02_03).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = run_query_plan(runtime, ["recall_classification(recall_oxalis_2026, Class, 2026_02_05)."])

    companion = next(
        item for item in results if item["result"].get("predicate") == "recall_classification_at_date_support"
    )
    assert companion["result"]["rows"][0]["Class"] == "class_i"
    assert companion["result"]["rows"][0]["EffectiveDate"] == "2026_02_03"


def test_run_query_plan_counts_admitted_lot_range_atoms() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    assert (
        runtime.assert_fact("unit_count(oxalis_recall_2026, 7200_2024_a_through_7200_2024_f, 2026_01_18).").get(
            "status"
        )
        == "success"
    )

    results = run_query_plan(runtime, ["unit_count(recall_oxalis_2026, lot, Date)."])

    companion = next(item for item in results if item["result"].get("predicate") == "unit_range_count_support")
    assert companion["result"]["rows"][0]["RangeCount"] == "6"
    assert companion["result"]["rows"][0]["Date"] == "2026_01_18"


def test_run_query_plan_derives_recall_accounted_units_from_latest_unaccounted() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "termination_request(recall_oxalis_2026, veridian, 2026_05_15).",
        "unit_count(recall_oxalis_2026, 4200, 2026_01_30).",
        "unit_status_change(recall_oxalis_2026, 2026_03_15, unaccounted, 353, veridian).",
        "unit_status_change(recall_oxalis_2026, 2026_05_10, unaccounted, 73, veridian).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = run_query_plan(runtime, ["termination_request(recall_oxalis_2026, veridian, 2026_05_15)."])

    companion = next(item for item in results if item["result"].get("predicate") == "recall_accounted_units_support")
    row = companion["result"]["rows"][0]
    assert row["AccountedUnits"] == "4127"
    assert row["TotalUnits"] == "4200"
    assert row["UnaccountedUnits"] == "73"
    assert row["AccountedPercent"] == "98.3"


def test_run_query_plan_keeps_recall_accounted_units_scoped_to_termination_questions() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "unit_count(recall_oxalis_2026, 4200, 2026_01_30).",
        "unit_status_change(recall_oxalis_2026, 2026_05_10, unaccounted, 73, veridian).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = run_query_plan(runtime, ["unit_status_change(recall_oxalis_2026, Date, accounted, Count, Actor)."])

    assert not any(item["result"].get("predicate") == "recall_accounted_units_support" for item in results)


def test_run_query_plan_adds_story_choice_contrast_support() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "judged(mina_moonbutton, cart_great, pride, too_proud).",
        "judged(mina_moonbutton, cart_middle, officiality, too_official).",
        "has_property(cart_little, just_brisk_enough).",
        "event(evt_mina_enter_little_cart, mina_moonbutton, entered, cart_little, kettle_house).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = run_query_plan(runtime, ["has_property(cart, property)."])

    companion = next(item for item in results if item["result"].get("predicate") == "story_choice_contrast_support")
    row = companion["result"]["rows"][0]
    assert row["AcceptedCandidate"] == "cart_little"
    assert row["PositiveProperty"] == "just_brisk_enough"
    assert row["RejectedCandidates"] == "cart_great,cart_middle"


def test_run_query_plan_can_infer_story_choice_from_complete_family_contrast() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "event(evt_mina_ride_great_cart, mina_moonbutton, rode, great_cart, kettle_house).",
        "event(evt_mina_ride_middle_cart, mina_moonbutton, rode, middle_sized_cart, kettle_house).",
        "event(evt_mina_ride_little_cart, mina_moonbutton, rode, little_cart, kettle_house).",
        "said(mina_moonbutton, narrative, this_cart_is_too_proud).",
        "said(mina_moonbutton, narrative, this_cart_is_too_official).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = run_query_plan(runtime, ["event(Evt, mina_moonbutton, Action, cart, Location)."])

    companion = next(item for item in results if item["result"].get("predicate") == "story_choice_contrast_support")
    row = companion["result"]["rows"][0]
    assert row["AcceptedCandidate"] == "little_cart"
    assert row["PositiveProperty"] == "accepted_by_contrast"
    assert row["EvidenceStatus"] == "inferred_by_complete_family_contrast"


def test_run_query_plan_pairs_story_remediation_method_with_extraction() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "event(evt_winding, great_burrow_mole, wound, mina_moonbutton, kettle_house).",
        "event(evt_key_extraction, great_burrow_mole, extracted, seven_silver_beetle_keys, mina_moonbutton_mouth).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    results = run_query_plan(runtime, ["event(Event, great_burrow_mole, extracted, beetle_keys, Target)."])

    companion = next(item for item in results if item["result"].get("predicate") == "story_remediation_method_support")
    row = companion["result"]["rows"][0]
    assert row["MethodAction"] == "wound"
    assert row["Patient"] == "mina_moonbutton"
    assert row["OutcomeObject"] == "seven_silver_beetle_keys"


def test_run_query_plan_adds_roster_state_support_from_group_membership() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "group_membership(arden, red_group, 2025_10_07t09_15, 2025_10_07t16_00).",
        "group_membership(bettina, red_group, 2025_10_07t09_15, 2025_10_07t16_00).",
        "supervision_assignment(ms_strand, red_group, 2025_10_07t09_15, 2025_10_07t16_00).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["group_membership(Student, Group, Start, End)."])

    companion = next(item for item in rows if item["result"].get("predicate") == "roster_state_support")
    result_rows = companion["result"]["rows"]
    assert any(
        row.get("SupportKind") == "group_count"
        and row.get("Group") == "red_group"
        and row.get("Count") == "2"
        and row.get("Members") == "arden,bettina"
        for row in result_rows
    )
    assert any(
        row.get("SupportKind") == "supervision_assignment"
        and row.get("Supervisor") == "ms_strand"
        and row.get("Target") == "red_group"
        for row in result_rows
    )


def test_run_query_plan_adds_roster_role_hints_from_admitted_group_atoms() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "group_member(shore_team_recording, lotte, 2025_10_09t10_30_to_2025_10_09t13_00).",
        "group_member(station_b_watch, freya, 2025_10_08t10_15_to_2025_10_08t14_00).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["group_member(Group, lotte, Day)."])

    companion = next(item for item in rows if item["result"].get("predicate") == "roster_state_support")
    result_rows = companion["result"]["rows"]
    assert any(
        row.get("SupportKind") == "group_member"
        and row.get("Person") == "lotte"
        and row.get("Group") == "shore_team_recording"
        and row.get("RoleHint") == "recording,shore"
        for row in result_rows
    )
    assert any(
        row.get("SupportKind") == "group_member"
        and row.get("Person") == "freya"
        and row.get("Group") == "station_b_watch"
        and row.get("RoleHint") == "station_b"
        for row in result_rows
    )


def test_source_record_section_display_renders_normalized_section_atoms() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "source_record_section(src_line_0074, v_1_4_roster_v3_2026_04_15).",
        "source_record_line(src_line_0074, 74).",
        "source_record_section(src_line_0225, v_6_1_temporary_in_day_assignment).",
        "source_record_line(src_line_0225, 225).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["source_record_section(SourceRow, SectionAtom)."])

    companion = next(item for item in rows if item["result"].get("predicate") == "source_record_section_display")
    result_rows = companion["result"]["rows"]
    assert any(
        row.get("SourceRow") == "src_line_0074"
        and row.get("DisplaySection") == "Section 1.4"
        and row.get("SectionTitleHint") == "roster_v3_2026_04_15"
        for row in result_rows
    )
    assert any(
        row.get("SourceRow") == "src_line_0225"
        and row.get("DisplaySection") == "Section 6.1"
        and row.get("SectionTitleHint") == "temporary_in_day_assignment"
        for row in result_rows
    )


def test_source_record_packet_metadata_surfaces_identifiers_and_pending_items() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "source_record_label(src_line_0158, sco_ch_3).",
        "source_record_text_atom(src_line_0003, packet_id_chms_rso_2026_t07).",
        "source_record_text_atom(src_line_0158, sco_ch_3_chaperone_counting_rules_defines_who_counts_toward_the).",
        "source_record_text_atom(src_line_0198, a_handheld_scanner_dev_scan_07_records_badge_taps).",
        "source_record_text_atom(src_line_0102, v_2_1_bus_1_driver_v_lee_license_cdl_ma_44291).",
        "source_record_text_atom(src_line_0192, a_diaz_is_the_parent_of_s_014_and_is_permitted_to_observe_group_b).",
        "source_record_text_atom(src_line_0193, events_on_saturday_afternoon_only_2026_05_02_13_00_17_00_a_diaz).",
        "source_record_text_atom(src_line_0249, return_leg_attendance_scans_will_be_appended_after_the_trip_and).",
        "source_record_section(src_line_0104, v_2_1_bus_1_driver_v_lee_license_cdl_ma_44291).",
        "source_record_line(src_line_0104, 104).",
        "source_record_text_atom(src_line_0104, capacity_24_students_departure_2026_05_01_06_30_from_cedar_hollow).",
        "source_record_line(src_line_0149, 149).",
        "source_record_text_atom(src_line_0149, adult_lodging_t_mendez_202_j_phelps_204_k_rosario_208).",
        "source_record_line(src_line_0150, 150).",
        "source_record_text_atom(src_line_0150, m_okonkwo_210_n_park_206_medical_coverage_station).",
        "source_record_line(src_line_0262, 262).",
        "source_record_text_atom(src_line_0262, retained_in_the_audit_binder_location_activities_office_filing).",
        "source_record_line(src_line_0263, 263).",
        "source_record_text_atom(src_line_0263, cabinet_3_drawer_2_and_are_not_the_operational_document).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["roster_version_status(v1, Status)."])

    companion = next(
        item for item in rows if item["result"].get("predicate") == "source_record_packet_metadata_support"
    )
    result_rows = companion["result"]["rows"]
    assert any(
        row.get("Kind") == "policy_identifier"
        and row.get("Value") == "sco_ch_3"
        and row.get("DisplayValue") == "SCO-CH-3"
        and row.get("HelperClass") == "clean-helper"
        for row in result_rows
    )
    assert any(
        row.get("Kind") == "packet_identifier"
        and row.get("DisplayValue") == "CHMS-RSO-2026-T07"
        and row.get("HelperClass") == "clean-helper"
        for row in result_rows
    )
    assert any(
        row.get("Kind") == "policy_name"
        and row.get("DisplayValue") == "SCO-CH-3 (Chaperone Counting Rules)"
        and row.get("HelperClass") == "candidate-helper"
        for row in result_rows
    )
    assert any(
        row.get("Kind") == "device_identifier"
        and row.get("DisplayValue") == "DEV-SCAN-07"
        for row in result_rows
    )
    assert any(
        row.get("Kind") == "driver_license_identifier"
        and row.get("DisplayValue") == "CDL-MA-44291"
        for row in result_rows
    )
    assert any(
        row.get("Kind") == "observer_permission_scope"
        and row.get("HelperClass") == "candidate-helper"
        for row in result_rows
    )
    assert any(
        row.get("Kind") == "pending_packet_item"
        and row.get("HelperClass") == "candidate-helper"
        for row in result_rows
    )
    assert any(
        row.get("Kind") == "transport_departure"
        and "06:30" in row.get("DisplayValue", "")
        for row in result_rows
    )
    assert any(
        row.get("Kind") == "adult_lodging_location"
        and row.get("HelperClass") == "candidate-helper"
        for row in result_rows
    )
    assert any(
        row.get("Kind") == "physical_retention_location"
        and row.get("HelperClass") == "candidate-helper"
        for row in result_rows
    )


def test_source_record_packet_metadata_exposes_grant_packet_identifiers_and_rules() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "source_record_label(src_line_0003, cycle_id).",
        "source_record_text_atom(src_line_0003, cycle_id_bwcf_mg_2026_s).",
        "source_record_section(src_line_0095, v_5_1_score_correction_memo_sc_2026_04_22).",
        "source_record_text_atom(src_line_0101, paper_score_sheet_was_correct_the_correction_memo_sc_2026_04_22).",
        "source_record_field(src_line_0117, recusal_memo, rc_2026_04_20_v).",
        "source_record_text_atom(src_line_0122, items_and_does_not_automatically_decide_the_named_item_in_any_direction).",
        "source_record_text_atom(src_line_0179, v_2026_04_29_within_the_14_day_appeal_window_from_the_decision_letter).",
        "source_record_text_atom(src_line_0180, v_2026_04_27_the_appeal_is_logged_as_ap_2026_0429_a).",
        "source_record_text_atom(src_line_0189, on_2026_05_22_as_of_the_compilation_date_ap_2026_0429_a_is).",
        "source_record_line(src_line_0223, 223).",
        "source_record_text_atom(src_line_0223, cycle_procedure_manual_bwcf_cp_2025_defines_threshold_vote).",
        "source_record_line(src_line_0224, 224).",
        "source_record_text_atom(src_line_0224, requirement_for_borderline_scores_appeal_window_and_supplementary).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["source_record_text_atom(Line, Text)."])

    companion = next(
        item for item in rows if item["result"].get("predicate") == "source_record_packet_metadata_support"
    )
    result_rows = companion["result"]["rows"]
    assert any(row.get("Kind") == "cycle_identifier" and row.get("DisplayValue") == "BWCF-MG-2026-S" for row in result_rows)
    assert any(row.get("Kind") == "score_correction_memo_identifier" and row.get("DisplayValue") == "SC-2026-04-22" for row in result_rows)
    assert any(row.get("Kind") == "recusal_memo_identifier" and row.get("DisplayValue") == "RC-2026-04-20-V" for row in result_rows)
    assert any(row.get("Kind") == "appeal_identifier" and row.get("DisplayValue") == "AP-2026-0429-A" for row in result_rows)
    assert any(
        row.get("Kind") == "appeal_identifier"
        and row.get("DisplayValue") == "AP-2026-0429-A"
        and row.get("HelperClass") == "clean-helper"
        for row in result_rows
    )
    assert any(
        row.get("Kind") == "procedure_manual_scope"
        and "BWCF-CP-2025" in row.get("DisplayValue", "")
        and row.get("HelperClass") == "candidate-helper"
        for row in result_rows
    )
    assert any(
        row.get("Kind") == "appeal_window_rule"
        and row.get("DisplayValue") == "14 days from the decision letter"
        and row.get("HelperClass") == "candidate-helper"
        for row in result_rows
    )


def test_grant_award_support_derives_counts_caps_recusals_and_appeal_status() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "application_eligibility(a_01, er_1, pass).",
        "application_eligibility(a_01, er_2, pass).",
        "application_eligibility(a_02, er_1, pass).",
        "application_eligibility(a_02, er_2, pass).",
        "application_eligibility(a_05, er_1, pass).",
        "application_eligibility(a_05, er_2, fail).",
        "requested_amount(a_02, 24000).",
        "bonus_eligibility(a_02, rural).",
        "final_award(a_01, 20000, awarded).",
        "final_award(a_02, 25000, awarded).",
        "final_award(a_07, 0, pending).",
        "source_record_field(src_line_0146, app_id, a_02).",
        "source_record_field(src_line_0146, pre_cap_amount, v_26_400).",
        "source_record_field(src_line_0146, capped, yes_25_000).",
        "source_record_field(src_line_0146, final_award, v_25_000).",
        "source_record_field(src_line_0020, parameter, number_of_applications).",
        "source_record_field(src_line_0020, value, v_7).",
        "source_record_field(src_line_0117, recusal_memo, rc_2026_04_20_v).",
        "source_record_field(src_line_0117, member, j_vasquez).",
        "source_record_field(src_line_0117, item, a_04).",
        "source_record_field(src_line_0117, reason, j_vasquez_serves_on_the_board_of_westside_arts_collective).",
        "source_record_line(src_line_0179, 179).",
        "source_record_text_atom(src_line_0179, v_2026_04_29_within_the_14_day_appeal_window_from_the_decision_letter).",
        "source_record_line(src_line_0189, 189).",
        "source_record_text_atom(src_line_0189, on_2026_05_22_as_of_the_compilation_date_ap_2026_0429_a_is).",
        "source_record_line(src_line_0190, 190).",
        "source_record_text_atom(src_line_0190, pending_a_07_has_neither_been_awarded_nor_finally_declined).",
        "source_record_line(src_line_0126, 126).",
        "source_record_text_atom(src_line_0126, the_committee_has_7_voting_members_with_one_recusal_6_members_vote).",
        "source_record_line(src_line_0103, 103).",
        "source_record_text_atom(src_line_0103, composite_from_7_4_to_8_4_a_02_s_revised_composite_is_above_the).",
        "source_record_line(src_line_0106, 106).",
        "source_record_text_atom(src_line_0106, the_corrected_score_is_operational_as_of_2026_04_22_the_pre_correction).",
        "source_record_line(src_line_0107, 107).",
        "source_record_text_atom(src_line_0107, composite_7_4_is_retained_in_the_audit_binder_but_is_not_used_for).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["application_eligibility(App, Rule, Result)."])

    companion = next(item for item in rows if item["result"].get("predicate") == "grant_award_support")
    result_rows = companion["result"]["rows"]
    assert any(
        row.get("SupportKind") == "eligible_application_count"
        and row.get("Amount") == "2"
        and "a_05=er_2:fail" in row.get("Detail", "")
        and row.get("HelperClass") == "clean-helper"
        for row in result_rows
    )
    assert any(
        row.get("SupportKind") == "cap_applied_application_count"
        and row.get("Amount") == "1"
        and "a_02:$26,400->$25,000" in row.get("Detail", "")
        and row.get("HelperClass") == "clean-helper"
        for row in result_rows
    )
    assert any(
        row.get("SupportKind") == "final_award_total"
        and row.get("Amount") == "$45,000"
        for row in result_rows
    )
    assert any(
        row.get("SupportKind") == "recusal_record"
        and row.get("Status") == "RC-2026-04-20-V"
        and "J. Vasquez recused from a_04" in row.get("Detail", "")
        and row.get("HelperClass") == "clean-helper"
        for row in result_rows
    )
    assert any(
        row.get("SupportKind") == "appeal_pending_status"
        and row.get("App") == "a_07"
        and row.get("HelperClass") == "candidate-helper"
        for row in result_rows
    )
    assert any(
        row.get("SupportKind") == "total_application_count"
        and row.get("Amount") == "7"
        for row in result_rows
    )
    assert any(
        row.get("SupportKind") == "committee_recusal_vote_count"
        and row.get("Amount") == "6"
        and row.get("HelperClass") == "candidate-helper"
        for row in result_rows
    )
    assert any(
        row.get("SupportKind") == "score_correction_operational"
        and row.get("App") == "a_02"
        and row.get("Amount") == "8.4"
        and row.get("HelperClass") == "candidate-helper"
        for row in result_rows
    )


def test_roster_state_support_derives_operational_roster_from_source_record_ledger() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "source_record_section(src_line_0058, v_1_2_roster_v2_2026_04_09).",
        "source_record_line(src_line_0058, 58).",
        "source_record_text_atom(src_line_0058, group_c_physics_engineering_13).",
        "source_record_section(src_line_0059, v_1_2_roster_v2_2026_04_09).",
        "source_record_line(src_line_0059, 59).",
        "source_record_text_atom(src_line_0059, s_022_s_025).",
        "source_record_section(src_line_0074, v_1_4_roster_v3_2026_04_15).",
        "source_record_line(src_line_0074, 74).",
        "source_record_text_atom(src_line_0074, v_1_4_roster_v3_2026_04_15).",
        "source_record_section(src_line_0078, v_1_4_roster_v3_2026_04_15).",
        "source_record_line(src_line_0078, 78).",
        "source_record_text_atom(src_line_0078, s_022_is_correctly_assigned_to_group_b_only_the_group_c_listing).",
        "source_record_section(src_line_0088, v_1_4_roster_v3_2026_04_15).",
        "source_record_line(src_line_0088, 88).",
        "source_record_text_atom(src_line_0088, group_b_life_science_10).",
        "source_record_section(src_line_0089, v_1_4_roster_v3_2026_04_15).",
        "source_record_line(src_line_0089, 89).",
        "source_record_text_atom(src_line_0089, s_013_s_014_s_015_s_016_s_017_s_020_s_021_s_022_s_023_s_024).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["student_group_assignment(Student, v3, group_b)."])

    companion = next(item for item in rows if item["result"].get("predicate") == "roster_state_support")
    result_rows = companion["result"]["rows"]
    assert any(
        row.get("SupportKind") == "source_record_student_group_assignment"
        and row.get("Person") == "s_022"
        and row.get("Group") == "group_b"
        and row.get("Version") == "v3"
        and row.get("SourceRow") == "src_line_0089"
        for row in result_rows
    )
    assert any(
        row.get("SupportKind") == "group_count"
        and row.get("Group") == "group_b"
        and row.get("Version") == "v3"
        and row.get("Count") == "10"
        for row in result_rows
    )
    assert not any(
        row.get("SupportKind") == "source_record_student_group_assignment"
        and row.get("Person") == "s_022"
        and row.get("Group") == "group_c"
        and row.get("Version") == "v3"
        for row in result_rows
    )


def test_roster_state_support_joins_adult_roles_to_ratio_scope() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "adult_role(t_mendez, lead_chaperone).",
        "adult_role(j_phelps, chaperone).",
        "adult_role(n_park, medical_staff).",
        "role_counts_towards_ratio(lead_chaperone, true).",
        "role_counts_towards_ratio(chaperone, true).",
        "role_counts_towards_ratio(medical_staff, false).",
        "adult_role(v_lee, bus_1_driver).",
        "role_counts_towards_ratio(bus_1_driver, false).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["role_counts_towards_ratio(Role, true)."])

    companion = next(item for item in rows if item["result"].get("predicate") == "roster_state_support")
    result_rows = companion["result"]["rows"]
    assert any(
        row.get("SupportKind") == "ratio_counted_adults"
        and row.get("Count") == "2"
        and row.get("Members") == "j_phelps,t_mendez"
        for row in result_rows
    )
    assert any(
        row.get("SupportKind") == "adult_role"
        and row.get("Person") == "n_park"
        and row.get("CountsTowardRatio") == "false"
        for row in result_rows
    )
    assert any(
        row.get("SupportKind") == "ratio_excluded_adults"
        and row.get("Count") == "2"
        and row.get("Members") == "n_park,v_lee"
        for row in result_rows
    )


def test_query_strategy_mentions_official_identity_duty_rows() -> None:
    policy = "\n".join(POST_INGESTION_QA_QUERY_STRATEGY["arity_and_variable_policy"])

    assert "who-is or what-is identity questions about a named official" in policy
    assert "Name plus role is often only partial support" in policy
    assert "ruling_by/3" in policy


def test_person_role_query_adds_official_action_companions() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "person_role(osric_thane, fair_warden).",
        "ruling_by(osric_thane, moth_lantern, disqualified_from_judging).",
        "permission_granted(osric_thane, tobias_wren_repair_request).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["person_role(osric_thane, Role)."])
    queries = [str(row.get("query", "")) for row in rows]

    assert "ruling_by(osric_thane, Subject, Outcome)." in queries
    assert "permission_granted(osric_thane, Request)." in queries


def test_deadline_calculated_query_adds_deadline_family_companion() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "deadline_calculated(deadline_answer_resumed, answer, march_18_2026, 14_calendar_days, april_1_2026).",
        "deadline_calculated(reply_deadline, reply, october_28_2026, 14_calendar_days, november_11_2026).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(
        runtime,
        ["deadline_calculated(deadline_answer_resumed, Answer, X, Y, Z)."],
    )
    companion = [
        row
        for row in rows
        if row.get("query") == "deadline_calculated(Deadline, Type, StartDate, Duration, EndDate)."
    ]

    assert companion
    result_rows = companion[0]["result"]["rows"]
    assert any(row.get("Deadline") == "reply_deadline" and row.get("Type") == "reply" for row in result_rows)
    assert "deadline-family questions" in companion[0]["result"]["reasoning_basis"]["note"]


def test_conversion_effect_query_adds_balanced_classification_count_companion() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "unit_count(condominium, 24).",
        "unit_count(condominium, 18).",
        "unit_count(townhome, 36).",
        "unit_count(townhome, 42).",
        "conversion_effective_date(unit_c13, condominium, townhome).",
        "conversion_effective_date(unit_c14, condominium, townhome).",
        "conversion_effective_date(unit_c15, condominium, townhome).",
        "conversion_effective_date(unit_c16, condominium, townhome).",
        "conversion_effective_date(unit_c17, condominium, townhome).",
        "conversion_effective_date(unit_c18, condominium, townhome).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(runtime, ["conversion_effective_date(Unit, FromType, ToType)."])
    companion = [
        row
        for row in rows
        if row["result"].get("predicate") == "classification_conversion_effect_support"
    ]

    assert companion
    result_row = companion[0]["result"]["rows"][0]
    assert result_row["FromType"] == "condominium"
    assert result_row["ToType"] == "townhome"
    assert result_row["ConvertedCount"] == "6"
    assert result_row["FromTypeDelta"] == "-6"
    assert result_row["ToTypeDelta"] == "6"
    assert result_row["TotalCountEffect"] == "no_change"


def test_case_status_at_date_query_derives_interval_support_from_transition_anchors() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "case_status_at_date(case_2026_cv_1847, 2026_03_31, active_discovery).",
        "case_status_at_date(case_2026cv1847, 2026_09_15, active_dispositive).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(
        runtime,
        ["case_status_at_date(case_2026_cv_1847, 2026_08_10, Status)."],
    )
    companion = [
        row
        for row in rows
        if row.get("query")
        == "case_status_at_date_interval_support(QueryCase, RequestedDate, Status, EffectiveFrom, EffectiveUntil)."
    ]

    assert companion
    result_row = companion[0]["result"]["rows"][0]
    assert result_row["Status"] == "active_discovery"
    assert result_row["EffectiveFrom"] == "2026_03_31"
    assert result_row["EffectiveUntil"] == "2026_09_15"
    assert "interval support" in companion[0]["result"]["reasoning_basis"]["note"]


def test_generic_status_query_derives_interval_support_from_transition_anchors() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "lot_status(lot_5b, precautionary_hold, 2025_08_28).",
        "lot_status(lot_5b, suspect, 2025_09_10).",
        "lot_status(lot_5b, cleared, 2025_09_22).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    rows = run_query_plan(
        runtime,
        ["lot_status(lot_5b, Status, 2025_09_15)."],
    )
    companion = [
        row
        for row in rows
        if row.get("query") == "lot_status_interval_support(QueryEntity, RequestedDate, Status, EffectiveFrom, EffectiveUntil)."
    ]

    assert companion
    result_row = companion[0]["result"]["rows"][0]
    assert result_row["Status"] == "suspect"
    assert result_row["EffectiveFrom"] == "2025_09_10"
    assert result_row["EffectiveUntil"] == "2025_09_22"
    assert result_row["ObservedEntity"] == "lot_5b"
