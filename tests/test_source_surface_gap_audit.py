from __future__ import annotations

from kb_pipeline import CorePrologRuntime
from scripts.audit_source_surface_gaps import audit_scorecard
from scripts.run_domain_bootstrap_qa import (
    compiled_kb_inventory,
    _source_record_citation_list_companion,
    _source_record_compile_surface_hint_queries,
    _source_record_identifier_set_companion,
    _source_field_question_key_hint_queries,
    _source_label_question_key_hint_queries,
    _source_section_question_key_hint_queries,
    _source_text_question_token_hint_queries,
    run_query_plan,
)


def test_source_text_question_token_hints_use_question_tokens_only() -> None:
    queries = _source_text_question_token_hint_queries(
        utterance="What is the label and material for case QR-17?",
        kb_inventory={"signatures": ["source_record_text_atom/2"]},
    )

    assert 'source_record_text_atom(SourceRow, TextAtom), memberchk("qr_17", TextAtom).' in queries
    assert all("ceramic" not in query for query in queries)


def test_source_text_question_token_hints_prioritize_initial_surname() -> None:
    queries = _source_text_question_token_hint_queries(
        utterance="What events did R. Kim not originate?",
        kb_inventory={"signatures": ["source_record_text_atom/2"]},
    )

    assert queries[0] == 'source_record_text_atom(SourceRow, TextAtom), memberchk("r_kim", TextAtom).'


def test_source_text_question_token_hints_include_quantity_questions() -> None:
    queries = _source_text_question_token_hint_queries(
        utterance="How many books were damaged in the pipe burst?",
        kb_inventory={"signatures": ["source_record_text_atom/2"]},
    )

    assert 'source_record_text_atom(SourceRow, TextAtom), memberchk("the_pipe_burst", TextAtom).' in queries
    assert 'source_record_text_atom(SourceRow, TextAtom), memberchk("books", TextAtom).' in queries


def test_source_surface_hint_queries_use_exact_surface_mentions_for_variant_questions() -> None:
    queries = _source_record_compile_surface_hint_queries(
        utterance="List every distinct spelling/casing variation that appears in the source.",
        kb_inventory={"signatures": ["source_record_surface_mention/3", "source_record_text_atom/2"]},
    )

    assert "source_record_surface_mention(SourceRow, SurfaceAtom, SurfaceText)." in queries
    assert all("Meter" not in query and "Lydium" not in query for query in queries)


def test_source_surface_hint_queries_use_surface_mentions_for_printed_parenthetical_ids() -> None:
    queries = _source_record_compile_surface_hint_queries(
        utterance="What is the full release number printed at the bottom of this document, including any parenthetical?",
        kb_inventory={"signatures": ["source_record_surface_mention/3", "source_record_text_atom/2"]},
    )

    assert "source_record_surface_mention(SourceRow, SurfaceAtom, SurfaceText)." in queries
    assert all("25-1508" not in query and "ATL" not in query for query in queries)


def test_source_surface_hint_queries_use_first_date_occurrence_for_first_mention_questions() -> None:
    queries = _source_record_compile_surface_hint_queries(
        utterance="In which named subsection is the date March 4, 2026 first introduced?",
        kb_inventory={"signatures": ["source_record_first_date_occurrence/4", "source_record_date_alias/3"]},
    )

    assert "source_record_first_date_occurrence(CanonicalDate, SourceRow, Line, SurfaceText)." in queries


def test_source_field_question_key_hints_use_existing_source_field_headers() -> None:
    queries = _source_field_question_key_hint_queries(
        utterance="What is the vendor and model number for device QR-17?",
        kb_inventory={
            "signatures": ["source_record_field/3"],
            "examples": {
                "source_record_field/3": [
                    "source_record_field(src_line_1, vendor, northstar).",
                    "source_record_field(src_line_1, model, nx_4).",
                    "source_record_field(src_line_1, location, bay_3).",
                ]
            },
        },
    )

    assert "source_record_field(SourceRow, vendor, Value)." in queries
    assert "source_record_field(SourceRow, model, Value)." in queries
    assert "source_record_field(SourceRow, location, Value)." not in queries


def test_source_field_question_key_hints_use_all_inventory_headers_beyond_examples() -> None:
    facts = [
        f"source_record_field(src_line_{index:04d}, filler_{index}, value_{index})."
        for index in range(12)
    ]
    facts.append("source_record_field(src_line_9999, vendor, northstar).")
    inventory = compiled_kb_inventory(facts=facts, rules=[])

    queries = _source_field_question_key_hint_queries(
        utterance="Which vendor is listed for device QR-17?",
        kb_inventory=inventory,
    )

    assert "source_record_field(SourceRow, vendor, Value)." in queries


def test_source_section_question_key_hints_use_all_inventory_headers_beyond_examples() -> None:
    facts = [
        f"source_record_section(src_line_{index:04d}, filler_{index})."
        for index in range(12)
    ]
    facts.append("source_record_section(src_line_9999, flight_time).")
    facts.append("source_record_text_atom(src_line_9999, total_this_make_and_model_22_hours).")
    inventory = compiled_kb_inventory(facts=facts, rules=[])

    queries = _source_section_question_key_hint_queries(
        utterance="How much total flight time did the pilot have in this specific aircraft type?",
        kb_inventory=inventory,
    )

    assert "source_record_section(SourceRow, flight_time), source_record_text_atom(SourceRow, TextAtom)." in queries


def test_source_label_question_key_hints_use_all_inventory_headers_beyond_examples() -> None:
    facts = [
        f"source_record_label(src_line_{index:04d}, filler_{index})."
        for index in range(12)
    ]
    facts.append("source_record_label(src_line_9999, additional_participating_persons).")
    facts.append(
        "source_record_text_atom(src_line_9999, additional_participating_persons_brook_stewart_federal_aviation_administration_sacramento_ca)."
    )
    inventory = compiled_kb_inventory(facts=facts, rules=[])

    queries = _source_label_question_key_hint_queries(
        utterance="Name the FAA participating person listed in the investigation.",
        kb_inventory=inventory,
    )

    assert (
        "source_record_label(SourceRow, additional_participating_persons), "
        "source_record_text_atom(SourceRow, TextAtom)."
    ) in queries


def test_source_label_question_key_hints_keep_date_time_label_tokens() -> None:
    inventory = compiled_kb_inventory(
        facts=[
            "source_record_label(src_line_0007, date_time).",
            "source_record_text_atom(src_line_0007, date_time_august_30_2024_07_05_local).",
        ],
        rules=[],
    )

    queries = _source_label_question_key_hint_queries(
        utterance="On what date and at what local time did the accident occur?",
        kb_inventory=inventory,
    )

    assert "source_record_label(SourceRow, date_time), source_record_text_atom(SourceRow, TextAtom)." in queries


def test_run_query_plan_filters_source_text_memberchk_queries() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    runtime.assert_fact("source_record_text_atom(src_line_1, case_qr_17_material_ceramic_blue).")
    runtime.assert_fact("source_record_text_atom(src_line_2, unrelated_record_summary).")

    rows = run_query_plan(
        runtime,
        ['source_record_text_atom(SourceRow, TextAtom), memberchk("qr_17", TextAtom).'],
        helper_companions_enabled=False,
    )

    assert rows[0]["result"]["status"] == "success"
    assert rows[0]["result"]["num_rows"] == 1
    assert rows[0]["result"]["rows"][0]["SourceRow"] == "src_line_1"
    assert rows[0]["result"]["reasoning_basis"]["validation"] == "source_text_contains_filter_repaired"


def test_source_record_identifier_set_collects_reference_numbers() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    runtime.assert_fact(
        "source_record_text_atom(src_line_0003, "
        "medical_products_laboratories_inc_marcs_cms_721916_april_09_2026)."
    )
    runtime.assert_fact("source_record_numeric_token(src_line_0003, v_721916).")
    runtime.assert_fact("source_record_text_atom(src_line_0026, warning_letter_320_26_61).")
    runtime.assert_fact("source_record_numeric_token(src_line_0026, v_320_26_61).")

    companion = _source_record_identifier_set_companion(
        runtime,
        utterance="What are the two reference numbers FDA uses for this warning letter?",
        query_intents=[
            {
                "intent_type": "list",
                "target_terms": ["reference numbers", "warning letter"],
                "answer_constraints": [],
                "uncertainty_policy": "answer",
                "language": "en",
                "source": "semantic_ir",
            }
        ],
    )

    assert companion is not None
    displays = {row["IdentifierDisplay"] for row in companion["result"]["rows"]}
    assert "MARCS-CMS 721916" in displays
    assert "Warning Letter 320-26-61" in displays


def test_source_record_identifier_set_ignores_utterance_without_structured_intent() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    runtime.assert_fact("source_record_text_atom(src_line_0003, warning_letter_320_26_61).")
    runtime.assert_fact("source_record_numeric_token(src_line_0003, v_320_26_61).")

    companion = _source_record_identifier_set_companion(
        runtime,
        utterance="What reference number does this warning letter use?",
    )

    assert companion is None


def test_source_record_identifier_set_collects_inspection_related_identifiers() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    runtime.assert_fact("source_record_field(src_line_0045, inspection_nr, v_1814187_015).")
    runtime.assert_fact("source_record_field(src_line_0046, report_id, v_0112600).")
    runtime.assert_fact("source_record_field(src_line_0075, activity_nr, v_2277281).")
    runtime.assert_fact("source_record_field(src_line_0099, investigation_nr, v_180500_015).")

    companion = _source_record_identifier_set_companion(
        runtime,
        utterance="How many distinct inspection-related identifiers does this record contain?",
        query_intents=[
            {
                "intent_type": "count",
                "target_terms": ["inspection identifiers", "report id", "activity nr", "investigation nr"],
                "answer_constraints": [],
                "uncertainty_policy": "answer",
                "language": "en",
                "source": "semantic_ir",
            }
        ],
    )

    assert companion is not None
    displays = {row["IdentifierDisplay"] for row in companion["result"]["rows"]}
    assert "Inspection Nr 1814187.015" in displays
    assert "Report ID 0112600" in displays
    assert "Activity Nr 2277281" in displays
    assert "Investigation Nr 180500.015" in displays


def test_source_record_citation_list_collects_ordered_cfr_sections() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    runtime.assert_fact(
        "source_record_text_atom(src_line_0046, "
        "v_1_your_firm_failed_to_establish_procedures_under_21_cfr_211_113_a)."
    )
    runtime.assert_fact(
        "source_record_text_atom(src_line_0078, "
        "v_2_production_control_violation_under_21_cfr_211_100_a)."
    )
    runtime.assert_fact("source_record_text_atom(src_line_0098, v_3_batch_failure_investigation_21_cfr_211_192).")
    runtime.assert_fact("source_record_text_atom(src_line_0133, v_4_stability_testing_program_21_cfr_211_166_a).")

    companion = _source_record_citation_list_companion(
        runtime,
        utterance="Which four CFR sections are cited as the four CGMP violations?",
    )

    assert companion is not None
    rows = companion["result"]["rows"]
    displays = [row["CitationDisplay"] for row in rows if row["CitationOrder"] != "summary"]
    assert displays == [
        "21 CFR 211.113(a)",
        "21 CFR 211.100(a)",
        "21 CFR 211.192",
        "21 CFR 211.166(a)",
    ]
    assert rows[-1]["CitationCount"] == "4"


def test_source_record_citation_list_collects_cfr_part_subpart() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    runtime.assert_fact("source_record_text_atom(src_line_0010, violation_under_21_cfr_111_70_e).")
    runtime.assert_fact("source_record_text_atom(src_line_0011, violation_under_21_cfr_111_205_a).")
    runtime.assert_fact("source_record_text_atom(src_line_0012, violation_under_21_cfr_111_255_a).")
    runtime.assert_fact("source_record_text_atom(src_line_0013, label_review_under_21_cfr_part_111_subpart_n).")

    companion = _source_record_citation_list_companion(
        runtime,
        utterance="What are the four CFR citations listed under the CGMP violations?",
    )

    assert companion is not None
    displays = [row["CitationDisplay"] for row in companion["result"]["rows"] if row["CitationOrder"] != "summary"]
    assert displays == [
        "21 CFR 111.70(e)",
        "21 CFR 111.205(a)",
        "21 CFR 111.255(a)",
        "21 CFR Part 111, Subpart N",
    ]


def test_source_surface_gap_audit_separates_stranded_source_from_direct_rows(tmp_path) -> None:
    compile_json = tmp_path / "compile.json"
    compile_json.write_text(
        """
        {
          "source_compile": {
            "facts": [
              "item_id(case_qr_17).",
              "source_record_text_atom(src_line_1, case_qr_17_material_ceramic_blue)."
            ],
            "rules": []
          }
        }
        """,
        encoding="utf-8",
    )
    qa_json = tmp_path / "qa.json"
    qa_json.write_text(
        """
        {
          "rows": [
            {
              "id": "q001",
              "utterance": "What material is case QR-17?",
              "reference_answer": "Ceramic blue."
            }
          ]
        }
        """,
        encoding="utf-8",
    )
    scorecard = {
        "artifacts": [
            {
                "label": "unlike_fixture",
                "path": str(qa_json),
                "run_json": str(compile_json),
                "non_exact_rows": [
                    {
                        "id": "q001",
                        "verdict": "miss",
                        "failure_surface": "compile_surface_gap",
                        "question": "What material is case QR-17?",
                        "queries": ["item_material(case_qr_17, Material)."],
                    }
                ],
            }
        ]
    }

    report = audit_scorecard(scorecard)

    assert report["summary"]["evidence_class_counts"] == {"answer_stranded_in_source_record": 1}
    assert report["summary"]["coordinate_class_counts"] == {"other_answer_bearing_detail": 1}
    assert report["rows"][0]["coordinate_class"] == "other_answer_bearing_detail"


def test_source_surface_gap_audit_classifies_coordinate_shapes(tmp_path) -> None:
    compile_json = tmp_path / "compile.json"
    compile_json.write_text(
        """
        {
          "source_compile": {
            "facts": [
              "source_record_text_atom(src_line_1, case_status_active_pleadings_on_2026_03_20).",
              "source_record_text_atom(src_line_2, maintenance_ticket_mt_404_for_camera_firmware_update).",
              "source_record_text_atom(src_line_3, quality_director_lee_chen)."
            ],
            "rules": []
          }
        }
        """,
        encoding="utf-8",
    )
    qa_json = tmp_path / "qa.json"
    qa_json.write_text(
        """
        {
          "rows": [
            {"id": "q001", "utterance": "What was the case status on March 20?", "reference_answer": "Active pleadings."},
            {"id": "q002", "utterance": "What is the maintenance ticket for the firmware update?", "reference_answer": "MT-404."},
            {"id": "q003", "utterance": "Who is the Quality Director?", "reference_answer": "Lee Chen."}
          ]
        }
        """,
        encoding="utf-8",
    )
    scorecard = {
        "artifacts": [
            {
                "label": "unlike_fixture",
                "path": str(qa_json),
                "run_json": str(compile_json),
                "non_exact_rows": [
                    {"id": "q001", "verdict": "miss", "failure_surface": "compile_surface_gap", "question": "What was the case status on March 20?", "queries": []},
                    {"id": "q002", "verdict": "miss", "failure_surface": "compile_surface_gap", "question": "What is the maintenance ticket for the firmware update?", "queries": []},
                    {"id": "q003", "verdict": "miss", "failure_surface": "compile_surface_gap", "question": "Who is the Quality Director?", "queries": []},
                ],
            }
        ]
    }

    report = audit_scorecard(scorecard)

    assert report["summary"]["coordinate_class_counts"] == {
        "identity_or_role": 1,
        "other_answer_bearing_detail": 1,
        "status_or_state": 1,
    }
    assert report["summary"]["coordinate_detail_class_counts"] == {
        "compact_identifier_detail": 1,
        "official_or_staff_role_identity": 1,
        "point_in_time_status": 1,
    }


def test_source_surface_gap_audit_splits_quantity_detail_shapes(tmp_path) -> None:
    compile_json = tmp_path / "compile.json"
    compile_json.write_text(
        """
        {
          "source_compile": {
            "facts": [
              "source_record_text_atom(src_line_1, awarded_19_fellowships).",
              "source_record_text_atom(src_line_2, filing_was_40_hours_after_scan).",
              "source_record_text_atom(src_line_3, rate_is_75_percent_of_standard_assessment).",
              "source_record_text_atom(src_line_4, seal_numbers_seal_001_through_seal_003)."
            ],
            "rules": []
          }
        }
        """,
        encoding="utf-8",
    )
    qa_json = tmp_path / "qa.json"
    qa_json.write_text(
        """
        {
          "rows": [
            {"id": "q001", "utterance": "How many fellowships were awarded?", "reference_answer": "19 fellowships."},
            {"id": "q002", "utterance": "Was the filing timely within the deadline?", "reference_answer": "No, it was 40 hours after the scan."},
            {"id": "q003", "utterance": "What assessment rate applies?", "reference_answer": "75 percent of the standard assessment."},
            {"id": "q004", "utterance": "What seal numbers are recorded?", "reference_answer": "SEAL-001 through SEAL-003."}
          ]
        }
        """,
        encoding="utf-8",
    )
    scorecard = {
        "artifacts": [
            {
                "label": "unlike_fixture",
                "path": str(qa_json),
                "run_json": str(compile_json),
                "non_exact_rows": [
                    {"id": "q001", "verdict": "miss", "failure_surface": "compile_surface_gap", "question": "How many fellowships were awarded?", "queries": []},
                    {"id": "q002", "verdict": "miss", "failure_surface": "compile_surface_gap", "question": "Was the filing timely within the deadline?", "queries": []},
                    {"id": "q003", "verdict": "miss", "failure_surface": "compile_surface_gap", "question": "What assessment rate applies?", "queries": []},
                    {"id": "q004", "verdict": "miss", "failure_surface": "compile_surface_gap", "question": "What seal numbers are recorded?", "queries": []},
                ],
            }
        ]
    }

    report = audit_scorecard(scorecard)

    assert report["summary"]["coordinate_class_counts"] == {"quantity_or_duration": 4}
    assert report["summary"]["coordinate_detail_class_counts"] == {
        "count_or_total": 1,
        "deadline_or_duration_arithmetic": 1,
        "identifier_range_or_sequence": 1,
        "monetary_rate_or_amount": 1,
    }


def test_source_surface_gap_audit_splits_status_state_detail_shapes(tmp_path) -> None:
    compile_json = tmp_path / "compile.json"
    compile_json.write_text(
        """
        {
          "source_compile": {
            "facts": [
              "source_record_text_atom(src_line_1, record_alpha_status_suspect_on_september_15).",
              "source_record_text_atom(src_line_2, record_beta_reclassified_from_hold_to_failed).",
              "source_record_text_atom(src_line_3, all_protected_items_are_a_b_and_c).",
              "source_record_text_atom(src_line_4, request_pending_clarification)."
            ],
            "rules": []
          }
        }
        """,
        encoding="utf-8",
    )
    qa_json = tmp_path / "qa.json"
    qa_json.write_text(
        """
        {
          "rows": [
            {"id": "q001", "utterance": "What status applied to record alpha as of September 15?", "reference_answer": "Suspect."},
            {"id": "q002", "utterance": "What condition was record beta reclassified to?", "reference_answer": "Failed, reclassified from hold."},
            {"id": "q003", "utterance": "What is the current status of the protected item population after the update?", "reference_answer": "A, B, and C."},
            {"id": "q004", "utterance": "What is the pending status of the request?", "reference_answer": "It remains pending clarification."}
          ]
        }
        """,
        encoding="utf-8",
    )
    scorecard = {
        "artifacts": [
            {
                "label": "unlike_fixture",
                "path": str(qa_json),
                "run_json": str(compile_json),
                "non_exact_rows": [
                    {"id": "q001", "verdict": "miss", "failure_surface": "compile_surface_gap", "question": "What status applied to record alpha as of September 15?", "queries": []},
                    {"id": "q002", "verdict": "miss", "failure_surface": "compile_surface_gap", "question": "What condition was record beta reclassified to?", "queries": []},
                    {"id": "q003", "verdict": "miss", "failure_surface": "compile_surface_gap", "question": "What is the current status of the protected item population after the update?", "queries": []},
                    {"id": "q004", "verdict": "miss", "failure_surface": "compile_surface_gap", "question": "What is the pending status of the request?", "queries": []},
                ],
            }
        ]
    }

    report = audit_scorecard(scorecard)

    assert report["summary"]["coordinate_class_counts"] == {"status_or_state": 4}
    assert report["summary"]["coordinate_detail_class_counts"] == {
        "partial_population_state": 1,
        "pending_or_resolution_state": 1,
        "point_in_time_status": 1,
        "status_transition_or_supersession": 1,
    }


def test_source_surface_gap_audit_splits_source_and_answer_detail_shapes(tmp_path) -> None:
    compile_json = tmp_path / "compile.json"
    compile_json.write_text(
        """
        {
          "source_compile": {
            "facts": [
              "source_record_text_atom(src_line_1, asset_tag_is_dev_12891).",
              "source_record_text_atom(src_line_2, source_within_packet_is_appendix_b).",
              "source_record_text_atom(src_line_3, applicant_statement_is_opinion_not_finding).",
              "source_record_text_atom(src_line_4, eligible_project_categories_are_repair_and_access).",
              "source_record_text_atom(src_line_5, rivera_suggested_replacing_the_filter)."
            ],
            "rules": []
          }
        }
        """,
        encoding="utf-8",
    )
    qa_json = tmp_path / "qa.json"
    qa_json.write_text(
        """
        {
          "rows": [
            {"id": "q001", "utterance": "What is the asset tag for the laptop?", "reference_answer": "DEV-12891."},
            {"id": "q002", "utterance": "What is the source within the packet for the statement?", "reference_answer": "Appendix B."},
            {"id": "q003", "utterance": "Which source claim is the applicant's opinion rather than a staff finding?", "reference_answer": "The applicant statement."},
            {"id": "q004", "utterance": "What are the eligible project categories?", "reference_answer": "Repair and access."},
            {"id": "q005", "utterance": "What did Rivera suggest during the inspection?", "reference_answer": "Replacing the filter."}
          ]
        }
        """,
        encoding="utf-8",
    )
    scorecard = {
        "artifacts": [
            {
                "label": "unlike_fixture",
                "path": str(qa_json),
                "run_json": str(compile_json),
                "non_exact_rows": [
                    {"id": "q001", "verdict": "miss", "failure_surface": "compile_surface_gap", "question": "What is the asset tag for the laptop?", "queries": []},
                    {"id": "q002", "verdict": "miss", "failure_surface": "compile_surface_gap", "question": "What is the source within the packet for the statement?", "queries": []},
                    {"id": "q003", "verdict": "miss", "failure_surface": "compile_surface_gap", "question": "Which source claim is the applicant's opinion rather than a staff finding?", "queries": []},
                    {"id": "q004", "verdict": "miss", "failure_surface": "compile_surface_gap", "question": "What are the eligible project categories?", "queries": []},
                    {"id": "q005", "verdict": "miss", "failure_surface": "compile_surface_gap", "question": "What did Rivera suggest during the inspection?", "queries": []},
                ],
            }
        ]
    }

    report = audit_scorecard(scorecard)

    assert report["summary"]["coordinate_class_counts"] == {
        "other_answer_bearing_detail": 3,
        "source_reference": 2,
    }
    assert report["summary"]["coordinate_detail_class_counts"] == {
        "claim_or_opinion_attribution": 1,
        "compact_identifier_detail": 1,
        "eligibility_scope_or_category": 1,
        "participant_statement_detail": 1,
        "source_location_or_section": 1,
    }
