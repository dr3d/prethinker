import json
from pathlib import Path

from scripts.audit_compile_surface_stability import audit_paths, render_markdown


def _write_compile(
    path: Path,
    facts: list[str],
    candidate_predicates: list[str] | None = None,
    profile_delivery_findings: list[dict[str, object]] | None = None,
) -> Path:
    path.parent.mkdir(parents=True)
    path.write_text(
        json.dumps(
            {
                "parsed_ok": True,
                "parsed": {
                    "candidate_predicates": [
                        {"signature": signature} for signature in (candidate_predicates or [])
                    ]
                },
                "source_compile": {
                    "facts": facts,
                    "profile_delivery": {
                        "findings": profile_delivery_findings or [],
                    },
                },
            }
        ),
        encoding="utf-8",
    )
    return path


def test_compile_surface_stability_detects_parallel_assignment_drift(tmp_path: Path) -> None:
    draw1 = _write_compile(
        tmp_path / "draw1" / "fixture_a" / "domain_bootstrap_file_a.json",
            [
                "task_assigned_to(task_alpha, person_one, 2026_01_01).",
                "task_description(task_alpha, first_task).",
                "task_description(task_beta, second_task).",
                "source_record_text_atom(src_0, person_one_was_assigned_to_first_task).",
                "source_record_text_atom(src_1, person_two_was_assigned_to_second_task).",
            ],
    )
    draw2 = _write_compile(
        tmp_path / "draw2" / "fixture_a" / "domain_bootstrap_file_b.json",
        [
                "task_assigned_to(task_alpha, person_one, 2026_01_01).",
                "task_assigned_to(task_beta, person_two, 2026_01_02).",
                "task_description(task_alpha, first_task).",
                "task_description(task_beta, second_task).",
                "source_record_text_atom(src_0, person_one_was_assigned_to_first_task).",
                "source_record_text_atom(src_1, person_two_was_assigned_to_second_task).",
            ],
    )

    report = audit_paths([draw1, draw2])

    fixture = report["fixtures"][0]
    assert fixture["stable"] is False
    assert fixture["unstable_fact_count"] == 1
    assert fixture["predicate_drift"] == [
        {"predicate": "task_assigned_to", "counts": [1, 2], "min": 1, "max": 2, "delta": 1}
    ]
    assert fixture["signature_delivery_drift"] == [
        {"signature": "task_assigned_to/3", "counts": [1, 2], "min": 1, "max": 2, "delta": 1}
    ]
    surface_drift = {row["surface"]: row for row in fixture["surface_drift"]}
    assert surface_drift["assignment_binding_surface"] == {
        "surface": "assignment_binding_surface",
        "counts": [1, 2],
        "min": 1,
        "max": 2,
        "delta": 1,
    }
    first_contracts = {row["contract"]: row for row in fixture["draws"][0]["contracts"]}
    second_contracts = {row["contract"]: row for row in fixture["draws"][1]["contracts"]}
    assert first_contracts["parallel_assignment_event_preservation"]["status"] == "partial"
    assert second_contracts["parallel_assignment_event_preservation"]["status"] == "pass"
    assert report["summary"]["unstable_fixture_count"] == 1
    assert report["summary"]["signature_delivery_drift_count"] == 1


def test_compile_surface_stability_reports_candidate_palette_drift(tmp_path: Path) -> None:
    draw1 = _write_compile(
        tmp_path / "draw1" / "fixture_palette" / "domain_bootstrap_file_a.json",
        ["entity_assignment(entity_001, version_a, cohort_a)."],
        candidate_predicates=["entity_assignment/3", "attribute_exception/3"],
    )
    draw2 = _write_compile(
        tmp_path / "draw2" / "fixture_palette" / "domain_bootstrap_file_b.json",
        ["entity_assignment(entity_001, version_a, cohort_a)."],
        candidate_predicates=["entity_assignment/3", "attribute_exception/4", "source_capture/4"],
    )

    report = audit_paths([draw1, draw2])

    fixture = report["fixtures"][0]
    assert fixture["stable"] is True
    assert fixture["palette_stable"] is False
    assert fixture["palette_common_count"] == 1
    assert fixture["palette_union_count"] == 4
    assert fixture["palette_unstable_count"] == 3
    assert fixture["predicate_arity_drift"] == [{"predicate": "attribute_exception", "arities": [3, 4]}]
    assert report["summary"]["palette_unstable_fixture_count"] == 1


def test_compile_surface_stability_reports_candidate_zero_yield_signatures(tmp_path: Path) -> None:
    draw = _write_compile(
        tmp_path / "draw1" / "fixture_zero_yield" / "domain_bootstrap_file_a.json",
        ["entity_assignment(entity_001, version_a, cohort_a)."],
        candidate_predicates=["entity_assignment/3", "source_capture/4"],
    )

    report = audit_paths([draw])

    fixture = report["fixtures"][0]
    assert fixture["candidate_zero_yield_signatures"] == ["source_capture/4"]
    assert fixture["candidate_zero_yield_signature_count"] == 1
    assert fixture["draws"][0]["candidate_zero_yield_signatures"] == ["source_capture/4"]
    assert report["summary"]["candidate_zero_yield_signature_count"] == 1


def test_compile_surface_stability_reports_palette_delivery_contracts(tmp_path: Path) -> None:
    draw1 = _write_compile(
        tmp_path / "draw1" / "fixture_contract" / "domain_bootstrap_file_a.json",
        [
            "entity_assignment(entity_001, version_a, cohort_a).",
            "entity_assignment(entity_002, version_a, cohort_b).",
            "entity_assignment(entity_003, version_a, cohort_c).",
            "entity_assignment(entity_004, version_a, cohort_d).",
        ],
        candidate_predicates=["entity_assignment/3", "status_phase/2"],
    )
    draw2 = _write_compile(
        tmp_path / "draw2" / "fixture_contract" / "domain_bootstrap_file_b.json",
        [],
        candidate_predicates=["entity_assignment/3", "entity_assignment/4"],
    )

    report = audit_paths([draw1, draw2])

    fixture = report["fixtures"][0]
    assert report["summary"]["palette_delivery_contract_count"] == 1
    contract = fixture["palette_delivery_contracts"][0]
    assert contract["signature"] == "entity_assignment/3"
    assert contract["max_row_count"] == 4
    assert contract["classification_counts"] == {"arity_drift": 1, "healthy": 1}
    assert contract["draws"][0]["status"] == "healthy"
    assert contract["draws"][1]["status"] == "arity_drift"


def test_compile_surface_stability_reports_quantity_event_delivery_telemetry(tmp_path: Path) -> None:
    draw1 = _write_compile(
        tmp_path / "draw1" / "fixture_quantity" / "domain_bootstrap_file_a.json",
        [
            "event_description(ev_1, feed_rate_increased_to_18_4_kg_min).",
            "event_measurement(ev_1, feed_rate, 18.4, kg_min).",
        ],
        candidate_predicates=["event_description/2", "event_measurement/4"],
    )
    draw2 = _write_compile(
        tmp_path / "draw2" / "fixture_quantity" / "domain_bootstrap_file_b.json",
        ["event_description(ev_1, feed_rate_increased_to_18_4_kg_min)."],
        candidate_predicates=["event_description/2", "event_measurement/4"],
    )
    draw3 = _write_compile(
        tmp_path / "draw3" / "fixture_quantity" / "domain_bootstrap_file_c.json",
        ["event_description(ev_1, feed_rate_increased_to_18_4_kg_min)."],
        candidate_predicates=["event_description/2"],
    )

    report = audit_paths([draw1, draw2, draw3])

    fixture = report["fixtures"][0]
    telemetry = fixture["delivery_telemetry"][0]
    assert telemetry["kind"] == "quantity_event_delivery"
    assert telemetry["status"] == "offered_not_delivered"
    assert telemetry["status_counts"] == {
        "delivered": 1,
        "not_offered": 1,
        "offered_not_delivered": 1,
    }
    assert telemetry["carrier_row_counts"] == [1, 0, 0]
    assert telemetry["stranded_numeric_wrapper_counts"] == [0, 1, 1]
    assert report["summary"]["quantity_event_delivery_issue_count"] == 1
    markdown = render_markdown(report)
    assert "Quantity-event delivery issues" in markdown


def test_compile_surface_stability_reports_profile_delivery_telemetry(tmp_path: Path) -> None:
    draw1 = _write_compile(
        tmp_path / "draw1" / "fixture_profile_delivery" / "domain_bootstrap_file_a.json",
        ["source_record_text_atom(src_line_1, policy_authorized_access_for_item_a_party_reader_one)."],
        candidate_predicates=["source_authority/3"],
        profile_delivery_findings=[
            {
                "class": "source_authority_carrier_offered_but_undelivered",
                "source_signal_count": 3,
                "offered_carriers": ["source_authority/3"],
            }
        ],
    )
    draw2 = _write_compile(
        tmp_path / "draw2" / "fixture_profile_delivery" / "domain_bootstrap_file_b.json",
        [
            "source_record_text_atom(src_line_1, policy_authorized_access_for_item_a_party_reader_one).",
            "source_authority(item_a, reader_one, policy_a).",
        ],
        candidate_predicates=["source_authority/3"],
    )

    report = audit_paths([draw1, draw2])

    fixture = report["fixtures"][0]
    assert report["summary"]["profile_delivery_issue_count"] == 1
    assert fixture["profile_delivery_telemetry"] == [
        {
            "kind": "profile_delivery",
            "class": "source_authority_carrier_offered_but_undelivered",
            "affected_draw_count": 1,
            "draw_count": 2,
            "source_signal_counts": [3],
            "offered_carriers": ["source_authority/3"],
            "carrier_delivery": [
                {
                    "carrier": "source_authority/3",
                    "row_counts": [0, 1],
                    "max": 1,
                    "min": 0,
                    "draws_with_rows": 1,
                }
            ],
            "response_hint": "multi_draw_preservation_candidate",
            "draws": [
                {
                    "run": "draw1",
                    "compile_json": str(draw1),
                    "source_signal_count": 3,
                    "offered_carriers": ["source_authority/3"],
                }
            ],
        }
    ]
    assert fixture["draws"][0]["profile_delivery_findings"][0]["class"] == (
        "source_authority_carrier_offered_but_undelivered"
    )
    markdown = render_markdown(report)
    assert "Profile delivery issue rows" in markdown
    assert "source_authority_carrier_offered_but_undelivered" in markdown
    assert "multi_draw_preservation_candidate" in markdown


def test_quantity_event_telemetry_ignores_source_line_locators(tmp_path: Path) -> None:
    draw = _write_compile(
        tmp_path / "draw1" / "fixture_story" / "domain_bootstrap_file_a.json",
        [
            "source_detail(person_a, errand, buy_brown_twine_and_vinegar, src_line_0013).",
            "source_detail(person_a, physical_trait, very_near_sighted, src_line_0007).",
        ],
        candidate_predicates=["source_detail/4"],
    )

    report = audit_paths([draw])

    fixture = report["fixtures"][0]
    telemetry = fixture["delivery_telemetry"][0]
    assert telemetry["status"] == "not_applicable"
    assert telemetry["numeric_wrapper_counts"] == [0]
    assert report["summary"]["quantity_event_delivery_issue_count"] == 0


def test_quantity_event_telemetry_allows_event_log_source_detail(tmp_path: Path) -> None:
    draw = _write_compile(
        tmp_path / "draw1" / "fixture_log" / "domain_bootstrap_file_a.json",
        ["source_detail(event_a, event_log_reading, pressure_value_18_4_kpa, src_line_0013)."],
        candidate_predicates=["source_detail/4"],
    )

    report = audit_paths([draw])

    fixture = report["fixtures"][0]
    telemetry = fixture["delivery_telemetry"][0]
    assert telemetry["status"] == "not_offered"
    assert telemetry["numeric_wrapper_counts"] == [1]
    assert report["summary"]["quantity_event_delivery_issue_count"] == 1


def test_quantity_event_telemetry_ignores_date_only_event_source_detail(tmp_path: Path) -> None:
    draw = _write_compile(
        tmp_path / "draw1" / "fixture_date" / "domain_bootstrap_file_a.json",
        ["source_detail(event_a, release_date, november_2007, src_line_0013)."],
        candidate_predicates=["source_detail/4"],
    )

    report = audit_paths([draw])

    fixture = report["fixtures"][0]
    telemetry = fixture["delivery_telemetry"][0]
    assert telemetry["status"] == "not_applicable"
    assert telemetry["numeric_wrapper_counts"] == [0]
    assert report["summary"]["quantity_event_delivery_issue_count"] == 0


def test_source_authority_contract_requires_shared_subject_and_recipient_slots(tmp_path: Path) -> None:
    draw1 = _write_compile(
        tmp_path / "draw1" / "fixture_b" / "domain_bootstrap_file_a.json",
        [
            "access_authorized_to(item_a, reader_one, physical).",
            "access_source(item_a, reader_two, policy_a).",
            "court_order(order_1, 2026_01_01).",
            "source_record_text_atom(src_1, policy_authorized_access_for_item_a_party_reader_one).",
        ],
    )
    draw2 = _write_compile(
        tmp_path / "draw2" / "fixture_b" / "domain_bootstrap_file_b.json",
        [
            "access_authorized_to(item_a, reader_one, physical).",
            "access_source(item_a, reader_one, policy_a).",
            "source_record_text_atom(src_1, policy_authorized_access_for_item_a_party_reader_one).",
        ],
    )

    report = audit_paths([draw1, draw2])

    fixture = report["fixtures"][0]
    first_contracts = {row["contract"]: row for row in fixture["draws"][0]["contracts"]}
    second_contracts = {row["contract"]: row for row in fixture["draws"][1]["contracts"]}
    assert first_contracts["source_authority_pair_preservation"]["status"] == "ledger_only"
    assert first_contracts["source_authority_pair_preservation"]["direct_complete_count"] == 0
    assert first_contracts["source_authority_pair_preservation"]["direct_partial_count"] == 2
    assert second_contracts["source_authority_pair_preservation"]["status"] == "pass"
    assert second_contracts["source_authority_pair_preservation"]["direct_complete_count"] == 1


def test_source_authority_contract_prefers_structured_source_field_units(tmp_path: Path) -> None:
    draw = _write_compile(
        tmp_path / "draw1" / "fixture_c" / "domain_bootstrap_file_a.json",
        [
            "source_record_field(src_line_1, item_id, item_a).",
            "source_record_field(src_line_1, authorized_parties_access, reader_one).",
            "source_record_field(src_line_1, authorizing_source, policy_a).",
            "source_record_text_atom(src_line_1, policy_authorized_access_for_item_a_party_reader_one).",
            "source_record_text_atom(src_line_2, broad_authority_intro).",
            "access_authorized_to(item_a, reader_one, physical).",
            "access_source(item_a, reader_one, policy_a).",
        ],
    )

    report = audit_paths([draw])

    contract = report["fixtures"][0]["draws"][0]["contracts"][1]
    assert contract["contract"] == "source_authority_pair_preservation"
    assert contract["status"] == "pass"
    assert contract["source_signal_count"] == 1
    assert contract["source_field_unit_count"] == 1
    assert contract["source_text_mention_count"] == 1


def test_source_authority_contract_accepts_authorized_access_source_pair(tmp_path: Path) -> None:
    draw = _write_compile(
        tmp_path / "draw1" / "fixture_access" / "domain_bootstrap_file_a.json",
        [
            "source_record_field(src_line_1, item_id, item_a).",
            "source_record_field(src_line_1, authorized_party, reader_one).",
            "source_record_field(src_line_1, authority_source, policy_a).",
            "authorized_access(item_a, reader_one, physical_inspection).",
            "access_authority_source(item_a, reader_one, policy_a).",
        ],
    )

    report = audit_paths([draw])

    contract = report["fixtures"][0]["draws"][0]["contracts"][1]
    assert contract["contract"] == "source_authority_pair_preservation"
    assert contract["status"] == "pass"
    assert contract["direct_complete_count"] == 1
    assert contract["direct_partial_count"] == 0


def test_source_authority_contract_counts_direct_custody_and_title_surfaces(tmp_path: Path) -> None:
    draw = _write_compile(
        tmp_path / "draw1" / "fixture_custody" / "domain_bootstrap_file_a.json",
        [
            "source_record_field(src_line_1, object, item_a).",
            "source_record_field(src_line_1, holder, custodian_one).",
            "source_record_field(src_line_1, authority, court_order_a).",
            "legal_title(item_a, owner_one).",
            "physical_custody(item_a, custodian_one, 2026_01_01_to_2026_01_31).",
            "publication_authority(item_a, archive_policy).",
            "access_authority(item_a, supervisor_one, reading_room).",
        ],
    )

    report = audit_paths([draw])

    contract = report["fixtures"][0]["draws"][0]["contracts"][1]
    assert contract["contract"] == "source_authority_pair_preservation"
    assert contract["status"] == "pass"
    assert contract["direct_complete_count"] == 4
    assert contract["direct_partial_count"] == 0


def test_source_authority_contract_does_not_count_shallow_presentation_row(tmp_path: Path) -> None:
    draw = _write_compile(
        tmp_path / "draw1" / "fixture_shallow" / "domain_bootstrap_file_a.json",
        [
            "source_record_field(src_line_1, item, item_a).",
            "source_record_field(src_line_1, authorized_party, reader_one).",
            "source_record_field(src_line_1, source, policy_a).",
            "presented_to(item_a, reader_one).",
        ],
    )

    report = audit_paths([draw])

    contract = report["fixtures"][0]["draws"][0]["contracts"][1]
    assert contract["contract"] == "source_authority_pair_preservation"
    assert contract["status"] == "ledger_only"
    assert contract["direct_complete_count"] == 0


def test_operational_lifecycle_contract_does_not_read_estate_as_state(tmp_path: Path) -> None:
    draw = _write_compile(
        tmp_path / "draw1" / "fixture_estate" / "domain_bootstrap_file_a.json",
        [
            "source_record_text_atom(src_line_1, estate_opened_on_2026_01_01).",
            "source_record_text_atom(src_line_2, estate_review_due_2026_02_01).",
        ],
    )

    report = audit_paths([draw])

    contract = report["fixtures"][0]["draws"][0]["contracts"][2]
    assert contract["contract"] == "operational_lifecycle_preservation"
    assert contract["status"] == "not_applicable"
    assert contract["source_text_mention_count"] == 0


def test_operational_lifecycle_contract_ignores_schedule_and_static_status_text(tmp_path: Path) -> None:
    draw = _write_compile(
        tmp_path / "draw1" / "fixture_schedule" / "domain_bootstrap_file_a.json",
        [
            "source_record_text_atom(src_line_1, filed_in_support_of_status_report_due_2026_05_15).",
            "source_record_text_atom(src_line_2, as_of_2026_04_30_status_of_item_a_recorded_as_contested).",
            "source_record_text_atom(src_line_3, hearing_is_now_set_for_2026_06_17_title_status).",
        ],
    )

    report = audit_paths([draw])

    contract = report["fixtures"][0]["draws"][0]["contracts"][2]
    assert contract["contract"] == "operational_lifecycle_preservation"
    assert contract["status"] == "not_applicable"
    assert contract["source_text_mention_count"] == 0


def test_operational_lifecycle_contract_scores_complete_status_surfaces(tmp_path: Path) -> None:
    draw1 = _write_compile(
        tmp_path / "draw1" / "fixture_d" / "domain_bootstrap_file_a.json",
        [
            "source_record_text_atom(src_line_1, on_2026_05_01_record_a_was_received_with_status_pending).",
            "source_record_text_atom(src_line_2, on_2026_05_02_record_a_was_closed_as_approved).",
            "status_at(record_a, pending).",
        ],
    )
    draw2 = _write_compile(
        tmp_path / "draw2" / "fixture_d" / "domain_bootstrap_file_b.json",
        [
            "source_record_text_atom(src_line_1, on_2026_05_01_record_a_was_received_with_status_pending).",
            "source_record_text_atom(src_line_2, on_2026_05_02_record_a_was_closed_as_approved).",
            "record_lifecycle_event(evt_1, record_a, received, 2026_05_01).",
            "record_status_phase(record_a, approved, 2026_05_02).",
        ],
    )

    report = audit_paths([draw1, draw2])

    fixture = report["fixtures"][0]
    first_contracts = {row["contract"]: row for row in fixture["draws"][0]["contracts"]}
    second_contracts = {row["contract"]: row for row in fixture["draws"][1]["contracts"]}
    assert first_contracts["operational_lifecycle_preservation"]["status"] == "ledger_only"
    assert first_contracts["operational_lifecycle_preservation"]["direct_partial_count"] == 1
    assert second_contracts["operational_lifecycle_preservation"]["status"] == "pass"
    assert second_contracts["operational_lifecycle_preservation"]["direct_complete_count"] == 2


def test_operational_lifecycle_contract_reports_split_surfaces_without_passing(tmp_path: Path) -> None:
    draw = _write_compile(
        tmp_path / "draw" / "fixture_d" / "domain_bootstrap_file_a.json",
        [
            "source_record_text_atom(src_line_1, on_2026_05_01_record_a_was_received_with_status_pending).",
            "source_record_text_atom(src_line_2, on_2026_05_02_record_a_was_closed_as_approved).",
            "record_status(record_a, pending).",
            "record_status_changed_on(record_a, 2026_05_01).",
        ],
    )

    report = audit_paths([draw])

    contract = report["fixtures"][0]["draws"][0]["contracts"][2]
    assert contract["contract"] == "operational_lifecycle_preservation"
    assert contract["status"] == "ledger_only"
    assert contract["direct_complete_count"] == 0
    assert contract["direct_split_count"] == 1


def test_operational_lifecycle_contract_reports_event_date_split_surfaces(tmp_path: Path) -> None:
    draw = _write_compile(
        tmp_path / "draw" / "fixture_d" / "domain_bootstrap_file_a.json",
        [
            "source_record_text_atom(src_line_1, on_2026_05_01_record_a_status_was_pending).",
            "source_record_text_atom(src_line_2, on_2026_05_02_record_a_was_closed_as_approved).",
            "record_status(record_a, pending).",
            "event_date(record_a, logged, 2026_05_01).",
        ],
    )

    report = audit_paths([draw])

    contract = report["fixtures"][0]["draws"][0]["contracts"][2]
    assert contract["status"] == "ledger_only"
    assert contract["direct_complete_count"] == 0
    assert contract["direct_split_count"] == 1


def test_operational_lifecycle_contract_accepts_typed_event_date_palette(tmp_path: Path) -> None:
    draw = _write_compile(
        tmp_path / "draw" / "fixture_d" / "domain_bootstrap_file_a.json",
        [
            "source_record_text_atom(src_line_1, on_2026_05_01_record_a_status_was_pending).",
            "source_record_text_atom(src_line_2, on_2026_05_02_record_a_was_closed_as_approved).",
            "event_type(evt_1, received).",
            "event_timestamp(evt_1, 2026_05_01).",
            "event_type(evt_2, closed).",
            "event_timestamp(evt_2, 2026_05_02).",
        ],
    )

    report = audit_paths([draw])

    contract = report["fixtures"][0]["draws"][0]["contracts"][2]
    assert contract["status"] == "pass"
    assert contract["direct_complete_count"] == 2
    assert contract["direct_split_count"] == 0


def test_operational_lifecycle_contract_ignores_undated_lifecycle_words(tmp_path: Path) -> None:
    draw = _write_compile(
        tmp_path / "draw" / "fixture_d" / "domain_bootstrap_file_a.json",
        [
            "source_record_text_atom(src_line_1, packet_supersedes_prior_notice_where_conflicts_exist).",
            "source_record_text_atom(src_line_2, final_review_was_completed_before_release).",
            "record_note(packet_a, supersedes_prior_notice).",
        ],
    )

    report = audit_paths([draw])

    contract = report["fixtures"][0]["draws"][0]["contracts"][2]
    assert contract["status"] == "not_applicable"
    assert contract["source_signal_count"] == 0


def test_operational_lifecycle_contract_ignores_assignment_and_negative_receipt(tmp_path: Path) -> None:
    draw = _write_compile(
        tmp_path / "draw" / "fixture_d" / "domain_bootstrap_file_a.json",
        [
            "source_record_text_atom(src_line_1, june_14_2026_14_15_division_chief_is_assigned_as_observer).",
            "source_record_text_atom(src_line_2, june_15_2026_03_30_office_has_not_received_the_notice).",
            "person_assignment(person_a, observer, 2026_06_14).",
        ],
    )

    report = audit_paths([draw])

    contract = report["fixtures"][0]["draws"][0]["contracts"][2]
    assert contract["status"] == "not_applicable"
    assert contract["source_signal_count"] == 0


def test_operational_lifecycle_contract_ignores_temporal_correction_and_storage_phrases(tmp_path: Path) -> None:
    draw = _write_compile(
        tmp_path / "draw" / "fixture_d" / "domain_bootstrap_file_a.json",
        [
            "source_record_text_atom(src_line_1, src_03_visual_content_corrected_timestamp_post_cc_2026_04_22_lob).",
            "source_record_text_atom(src_line_2, cycle_window_applications_opened_2026_02_15_closed_2026_04_01).",
            "source_record_text_atom(src_line_3, rc_2026_04_20_k_originals_are_filed).",
            "source_record_text_atom(src_line_4, maintenance_window_completed_line_restart_authorized_at_2026_04_23).",
            "event_timestamp_corrected(evt_1, 2026_04_22).",
        ],
    )

    report = audit_paths([draw])

    contract = report["fixtures"][0]["draws"][0]["contracts"][2]
    assert contract["status"] == "not_applicable"
    assert contract["source_signal_count"] == 0
