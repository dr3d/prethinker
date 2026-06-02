import json
from pathlib import Path
from types import SimpleNamespace

from scripts.run_domain_bootstrap_file_batch import (
    CompileJob,
    _build_command,
    _detail_wrapper_drift_flags,
    _extract_compile_summary,
    _merge_quality_retry_context_lines,
    _profile_delivery_flags,
    _quality_gate_result,
    _quality_gate_rank_tuple,
    _quality_retry_metadata,
    _quality_retry_context_lines,
    _render_md,
    _summarize_existing_job,
    _summarize,
)


def test_build_command_forwards_profile_delivery_repair_pass() -> None:
    args = SimpleNamespace(
        domain_hint="",
        profile_registry=None,
        use_profile_registry_direct=False,
        profile_registry_palette_prior=False,
        allow_global_first_profile_registry_palette_prior=False,
        compile_source=True,
        compile_plan_passes=False,
        compile_flat_plus_plan_passes=True,
        focused_pass_ops_schema=True,
        source_entity_ledger=False,
        archival_identifier_ledger=False,
        source_record_ledger=True,
        source_record_ledger_facts=True,
        profile_delivery_repair_pass=True,
        intake_registry_context=False,
        review_profile=False,
        profile_review_retry=False,
        max_plan_passes=6,
        extra_compile_context_line=[],
    )
    command = _build_command(
        CompileJob(
            fixture="fixture_a",
            text_file=Path("datasets/fixture_a/source.md"),
            out_dir=Path("tmp/out/fixture_a"),
        ),
        args=args,
        model="model-a",
        base_url="http://127.0.0.1:1234",
        timeout=1200,
    )

    assert "--profile-delivery-repair-pass" in command


def test_build_command_forwards_profile_registry_lens() -> None:
    args = SimpleNamespace(
        domain_hint="",
        profile_registry=Path("datasets/domain_profiles/fda_warning_letter_v1/ontology_registry.json"),
        profile_registry_lens="violation",
        use_profile_registry_direct=False,
        profile_registry_palette_prior=False,
        allow_global_first_profile_registry_palette_prior=False,
        compile_source=True,
        compile_plan_passes=False,
        compile_flat_plus_plan_passes=True,
        focused_pass_ops_schema=True,
        source_entity_ledger=False,
        archival_identifier_ledger=False,
        source_record_ledger=False,
        source_record_ledger_facts=False,
        profile_delivery_repair_pass=False,
        intake_registry_context=False,
        review_profile=False,
        profile_review_retry=False,
        max_plan_passes=6,
        extra_compile_context_line=[],
    )
    command = _build_command(
        CompileJob(
            fixture="fixture_a",
            text_file=Path("datasets/fixture_a/source.md"),
            out_dir=Path("tmp/out/fixture_a"),
        ),
        args=args,
        model="model-a",
        base_url="http://127.0.0.1:1234",
        timeout=1200,
    )

    assert command[command.index("--profile-registry-lens") + 1] == "violation"


def test_build_command_forwards_profile_registry_followups() -> None:
    args = SimpleNamespace(
        domain_hint="",
        profile_registry=Path("datasets/domain_profiles/fda_warning_letter_v1/ontology_registry.json"),
        profile_registry_lens="wrapper",
        use_profile_registry_direct=False,
        profile_registry_palette_prior=False,
        allow_global_first_profile_registry_palette_prior=False,
        compile_source=True,
        compile_plan_passes=False,
        compile_flat_plus_plan_passes=True,
        focused_pass_ops_schema=True,
        source_entity_ledger=False,
        archival_identifier_ledger=False,
        source_record_ledger=False,
        source_record_ledger_facts=False,
        profile_delivery_repair_pass=False,
        profile_registry_completion_followup=True,
        profile_registry_accountability_followup=True,
        fda_violation_detail_bundle_followup=True,
        intake_registry_context=False,
        review_profile=False,
        profile_review_retry=False,
        max_plan_passes=6,
        extra_compile_context_line=[],
    )
    command = _build_command(
        CompileJob(
            fixture="fixture_a",
            text_file=Path("datasets/fixture_a/source.md"),
            out_dir=Path("tmp/out/fixture_a"),
        ),
        args=args,
        model="model-a",
        base_url="http://127.0.0.1:1234",
        timeout=1200,
    )

    assert "--profile-registry-completion-followup" in command
    assert "--profile-registry-accountability-followup" in command
    assert "--fda-violation-detail-bundle-followup" in command


def test_build_command_forwards_profile_identifier_occurrence_repair_pass() -> None:
    args = SimpleNamespace(
        domain_hint="",
        profile_registry=None,
        use_profile_registry_direct=False,
        profile_registry_palette_prior=False,
        allow_global_first_profile_registry_palette_prior=False,
        compile_source=True,
        compile_plan_passes=False,
        compile_flat_plus_plan_passes=True,
        focused_pass_ops_schema=True,
        source_entity_ledger=False,
        archival_identifier_ledger=False,
        source_record_ledger=True,
        source_record_ledger_facts=True,
        profile_delivery_repair_pass=False,
        profile_identifier_occurrence_repair_pass=True,
        intake_registry_context=False,
        review_profile=False,
        profile_review_retry=False,
        max_plan_passes=6,
        extra_compile_context_line=[],
    )
    command = _build_command(
        CompileJob(
            fixture="fixture_a",
            text_file=Path("datasets/fixture_a/source.md"),
            out_dir=Path("tmp/out/fixture_a"),
        ),
        args=args,
        model="model-a",
        base_url="http://127.0.0.1:1234",
        timeout=1200,
    )

    assert "--profile-identifier-occurrence-repair-pass" in command


def test_build_command_forwards_governed_subject_repair_passes() -> None:
    args = SimpleNamespace(
        domain_hint="",
        profile_registry=None,
        use_profile_registry_direct=False,
        profile_registry_palette_prior=False,
        allow_global_first_profile_registry_palette_prior=False,
        compile_source=True,
        compile_plan_passes=False,
        compile_flat_plus_plan_passes=True,
        focused_pass_ops_schema=True,
        source_entity_ledger=False,
        archival_identifier_ledger=False,
        source_record_ledger=True,
        source_record_ledger_facts=False,
        profile_delivery_repair_pass=False,
        profile_identifier_occurrence_repair_pass=False,
        profile_list_range_inventory_repair_pass=False,
        profile_governed_subject_manifest_pass=True,
        profile_legal_citation_repair_pass=True,
        profile_review_outcome_repair_pass=True,
        legal_citation_profile_extension=True,
        list_range_inventory_profile_extension=True,
        intake_registry_context=False,
        review_profile=False,
        profile_review_retry=False,
        max_plan_passes=6,
        extra_compile_context_line=[],
    )
    command = _build_command(
        CompileJob(
            fixture="fixture_a",
            text_file=Path("datasets/fixture_a/source.md"),
            out_dir=Path("tmp/out/fixture_a"),
        ),
        args=args,
        model="model-a",
        base_url="http://127.0.0.1:1234",
        timeout=1200,
    )

    assert "--profile-governed-subject-manifest-pass" in command
    assert "--profile-legal-citation-repair-pass" in command
    assert "--profile-review-outcome-repair-pass" in command
    assert "--legal-citation-profile-extension" in command
    assert "--list-range-inventory-profile-extension" in command


def test_compile_batch_command_forwards_openrouter_provider_controls() -> None:
    args = SimpleNamespace(
        domain_hint="",
        profile_registry=None,
        use_profile_registry_direct=False,
        profile_registry_palette_prior=False,
        allow_global_first_profile_registry_palette_prior=False,
        compile_source=True,
        compile_plan_passes=False,
        compile_flat_plus_plan_passes=False,
        focused_pass_ops_schema=False,
        source_entity_ledger=False,
        archival_identifier_ledger=False,
        source_record_ledger=False,
        source_record_ledger_facts=False,
        profile_delivery_repair_pass=False,
        intake_registry_context=False,
        review_profile=False,
        profile_review_retry=False,
        max_plan_passes=6,
        extra_compile_context_line=[],
        openrouter_provider_order="provider-a,provider-b",
        openrouter_provider_only="provider-a",
        openrouter_provider_ignore="provider-c",
        openrouter_quantizations="fp16",
        openrouter_allow_fallbacks="false",
        openrouter_require_parameters="true",
    )
    command = _build_command(
        CompileJob(
            fixture="fixture_a",
            text_file=Path("datasets/fixture_a/source.md"),
            out_dir=Path("tmp/out/fixture_a"),
        ),
        args=args,
        model="model-a",
        base_url="https://openrouter.ai/api/v1",
        timeout=1200,
    )

    assert command[command.index("--openrouter-provider-order") + 1] == "provider-a,provider-b"
    assert command[command.index("--openrouter-provider-only") + 1] == "provider-a"
    assert command[command.index("--openrouter-provider-ignore") + 1] == "provider-c"
    assert command[command.index("--openrouter-quantizations") + 1] == "fp16"
    assert command[command.index("--openrouter-allow-fallbacks") + 1] == "false"
    assert command[command.index("--openrouter-require-parameters") + 1] == "true"


def test_compile_batch_summary_extracts_quality_gate_signals() -> None:
    summary = _extract_compile_summary(
        {
            "parsed_ok": True,
            "parsed": {"candidate_predicates": [{"signature": "record_status/2"}]},
            "source_compile": {"admitted_count": 9, "skipped_count": 1},
            "score": {
                "rough_score": 0.861,
                "risk_count": 3,
                "candidate_signature_arg_mismatch_count": 1,
                "candidate_signature_arg_mismatch_refs": ["record_status/3:args=2"],
                "repeated_structure_count": 1,
                "repeated_structure_id_only_record_refs": ["record_id/1"],
                "repeated_structure_role_mismatch_refs": ["record_status/2"],
                "frontier_unknown_positive_predicate_count": 0,
                "frontier_unknown_positive_predicate_refs": [],
                "generic_predicate_count": 0,
            },
        }
    )

    assert summary["rough_score"] == 0.861
    assert summary["risk_count"] == 3
    assert summary["candidate_signature_arg_mismatch_refs"] == ["record_status/3:args=2"]
    assert summary["profile_schema_contract_flags"] == [
        "candidate_signature_arg_mismatch:record_status/3:args=2",
        "repeated_structure_id_only_record:record_id/1",
        "repeated_structure_role_mismatch:record_status/2",
    ]
    assert summary["repeated_structure_id_only_record_refs"] == ["record_id/1"]
    assert summary["frontier_unknown_positive_predicate_count"] == 0
    assert summary["detail_wrapper_drift_flags"] == []


def test_compile_batch_summary_refreshes_profile_bootstrap_score() -> None:
    summary = _extract_compile_summary(
        {
            "parsed_ok": True,
            "parsed": {
                "schema_version": "profile_bootstrap_v1",
                "candidate_predicates": [
                    {
                        "signature": "case_location/2",
                        "args": ["case_id", "location"],
                        "description": "Case location.",
                        "why": "Location is stated.",
                        "admission_notes": [],
                    }
                ],
                "starter_frontier_cases": [
                    {
                        "expected_boundary": "case_location('case_001', 'River City, AA').",
                        "must_not_write": [],
                    }
                ],
                "entity_types": [{"name": "case"}],
                "admission_risks": ["risk"],
                "repeated_structures": [],
            },
            "source_compile": {"admitted_count": 1, "skipped_count": 0},
            "score": {
                "rough_score": 0.1,
                "risk_count": 0,
                "frontier_unknown_positive_predicate_count": 1,
                "frontier_unknown_positive_predicate_refs": ["case_location/3"],
            },
        }
    )

    assert summary["rough_score"] > 0.1
    assert summary["frontier_unknown_positive_predicate_count"] == 0
    assert summary["frontier_unknown_positive_predicate_refs"] == []


def test_compile_batch_summary_flags_regulatory_violation_category_loss() -> None:
    summary = _extract_compile_summary(
        {
            "parsed_ok": True,
            "parsed": {
                "schema_version": "profile_bootstrap_v1",
                "domain_guess": "regulatory_enforcement",
                "domain_scope": "Compliance enforcement records with violations and failures.",
                "candidate_predicates": [
                    {
                        "signature": "regulatory_order/4",
                        "args": ["order_id", "target_entity", "order_type", "legal_basis"],
                        "description": "Intervention row.",
                        "why": "Source states the order.",
                        "admission_notes": [],
                    },
                    {
                        "signature": "admitted_failure/2",
                        "args": ["entity", "failure_description"],
                        "description": "Failure row.",
                        "why": "Source states a failure.",
                        "admission_notes": [],
                    },
                ],
                "starter_frontier_cases": [],
                "entity_types": [{"name": "action"}],
                "admission_risks": ["violation category collapse"],
                "repeated_structures": [],
            },
            "source_compile": {"admitted_count": 1, "skipped_count": 0},
            "score": {"rough_score": 0.1, "risk_count": 0},
        }
    )

    assert "admitted_failure/2" in summary["violation_category_slot_loss_refs"]
    assert any(
        flag.startswith("violation_category_slot_loss:")
        for flag in summary["profile_schema_contract_flags"]
    )


def test_compile_batch_summary_refreshes_list_range_inventory_slot_loss() -> None:
    summary = _extract_compile_summary(
        {
            "parsed_ok": True,
            "parsed": {
                "schema_version": "profile_bootstrap_v1",
                "domain_guess": "adjudicative_review",
                "domain_scope": "Review records with numbered claim outcomes.",
                "candidate_predicates": [
                    {
                        "signature": "claim_outcome/3",
                        "args": ["claim_range", "ground", "outcome"],
                        "description": "Outcome row.",
                        "why": "Source states claim outcomes.",
                        "admission_notes": [],
                    },
                ],
                "starter_frontier_cases": [],
                "entity_types": [{"name": "claim"}],
                "admission_risks": ["range compression"],
                "repeated_structures": [],
            },
            "source_compile": {"admitted_count": 1, "skipped_count": 0},
            "score": {"rough_score": 0.1, "risk_count": 0},
        }
    )

    assert summary["list_range_inventory_slot_loss_refs"] == ["claim_outcome/3"]
    assert any(
        flag.startswith("list_range_inventory_slot_loss:")
        for flag in summary["profile_schema_contract_flags"]
    )


def test_compile_batch_summary_separates_rejected_flat_pass_diagnostic_skips() -> None:
    summary = _extract_compile_summary(
        {
            "parsed_ok": True,
            "parsed": {"candidate_predicates": [{"signature": "sensor_observation/4"}]},
            "source_compile": {
                "admitted_count": 98,
                "skipped_count": 68,
                "flat_pass": {
                    "projected_decision": "reject",
                    "admitted_count": 0,
                    "skipped_count": 64,
                },
                "focused_passes": {
                    "admitted_count": 98,
                    "skipped_count": 4,
                },
            },
            "score": {"rough_score": 0.889, "risk_count": 5},
        }
    )

    assert summary["compile_skipped"] == 68
    assert summary["compile_effective_skipped"] == 4
    assert summary["compile_diagnostic_rejected_skipped"] == 64

    gate = _quality_gate_result(
        {"fixture": "industrial", "returncode": 0, "compile_json": "compile.json", "summary": summary},
        min_rough_score=0.775,
        max_risk_count=5,
    )

    assert gate["passed"] is True
    assert gate["compile_raw_skipped_share"] == 0.4096
    assert gate["compile_skipped_share"] == 0.0392


def test_summarize_existing_quality_selects_best_compile_not_latest(tmp_path) -> None:
    older = tmp_path / "domain_bootstrap_file_20260520T000001Z_source_model.json"
    latest = tmp_path / "domain_bootstrap_file_20260520T000002Z_source_model.json"
    older.write_text(
        json.dumps(
            {
                "parsed_ok": True,
                "parsed": {"candidate_predicates": [{"signature": "event_measurement/4"}]},
                "source_compile": {"admitted_count": 9, "skipped_count": 1, "facts": []},
                "score": {"rough_score": 0.9, "risk_count": 2},
            }
        ),
        encoding="utf-8",
    )
    latest.write_text(
        json.dumps(
            {
                "parsed_ok": True,
                "parsed": {"candidate_predicates": [{"signature": "event_description/2"}]},
                "source_compile": {
                    "admitted_count": 9,
                    "skipped_count": 1,
                    "facts": [
                        "source_record_field(src_line_001, duration, line_stop_started).",
                        "event_description(ev_10, line_stop_started).",
                    ],
                },
                "score": {"rough_score": 0.9, "risk_count": 2},
            }
        ),
        encoding="utf-8",
    )
    job = CompileJob(fixture="industrial", text_file=tmp_path / "source.md", out_dir=tmp_path)

    plain = _summarize_existing_job(job)
    quality_selected = _summarize_existing_job(job, quality_select=True)

    assert plain["compile_json"] == str(latest)
    assert quality_selected["compile_json"] == str(older)


def test_compile_batch_summary_flags_detail_wrapper_without_backbone() -> None:
    summary = _extract_compile_summary(
        {
            "parsed_ok": True,
            "parsed": {"candidate_predicates": [{"signature": "context/2"}]},
            "source_compile": {
                "facts": [
                    "source_record_field(src_line_001, record_id, rec_07).",
                    "source_record_field(src_line_001, departure_time, v_06_30).",
                    "context(rec_07, departure_context).",
                ],
            },
            "score": {"rough_score": 0.9, "risk_count": 2},
        }
    )

    assert any(flag.startswith("identity_backbone_missing_with_wrapper:") for flag in summary["detail_wrapper_drift_flags"])
    assert any(flag.startswith("date_time_backbone_missing_with_wrapper:") for flag in summary["detail_wrapper_drift_flags"])


def test_compile_batch_summary_flags_ledger_only_surface_contract() -> None:
    summary = _extract_compile_summary(
        {
            "parsed_ok": True,
            "parsed": {"candidate_predicates": [{"signature": "status_at/2"}]},
            "source_compile": {
                "facts": [
                    "source_record_text_atom(src_line_1, on_2026_05_01_record_a_was_received_with_status_pending).",
                    "source_record_text_atom(src_line_2, on_2026_05_02_record_a_was_closed_as_approved).",
                    "status_at(record_a, pending).",
                ],
            },
            "score": {"rough_score": 0.9, "risk_count": 2},
        }
    )

    assert summary["compile_surface_contract_flags"] == [
        "operational_lifecycle_preservation:ledger_only:source=2:direct=0"
    ]


def test_compile_batch_summary_extracts_profile_delivery_flags() -> None:
    payload = {
        "parsed_ok": True,
        "parsed": {"candidate_predicates": [{"signature": "status_state_at/4"}]},
        "source_compile": {
            "admitted_count": 9,
            "skipped_count": 1,
            "profile_delivery": {
                "findings": [
                    {
                        "class": "status_state_carrier_offered_but_undelivered",
                        "source_signal_count": 2,
                        "offered_carriers": ["status_state_at/4"],
                    }
                ]
            },
        },
        "score": {"rough_score": 0.9, "risk_count": 2},
    }

    assert _profile_delivery_flags(payload) == [
        "status_state_carrier_offered_but_undelivered:source=2:offered=status_state_at/4"
    ]
    summary = _extract_compile_summary(payload)
    assert summary["profile_delivery_flags"] == [
        "status_state_carrier_offered_but_undelivered:source=2:offered=status_state_at/4"
    ]


def test_compile_batch_summary_flags_underpreserved_distribution_state_table() -> None:
    facts = [
        "source_record_row(src_line_001, table_row, 1, distribution, connecticut).",
        "source_record_cell(src_line_001, retailers, walmart_save_a_lot).",
        "source_record_row(src_line_002, table_row, 2, distribution, delaware).",
        "source_record_cell(src_line_002, retailers, walmart_save_a_lot).",
        "source_record_row(src_line_003, table_row, 3, distribution, illinois).",
        "source_record_cell(src_line_003, retailers, walmart_kroger).",
        "source_record_row(src_line_004, table_row, 4, distribution, indiana).",
        "source_record_cell(src_line_004, retailers, kroger).",
        "source_record_row(src_line_005, table_row, 5, distribution, kentucky).",
        "source_record_cell(src_line_005, retailers, aldi).",
        "source_record_row(src_line_006, table_row, 6, distribution, maryland).",
        "source_record_cell(src_line_006, retailers, walmart_shop_n_save).",
        "source_record_row(src_line_007, table_row, 7, distribution, michigan).",
        "source_record_cell(src_line_007, retailers, walmart).",
        "source_record_row(src_line_008, table_row, 8, distribution, new_jersey).",
        "source_record_cell(src_line_008, retailers, walmart).",
        "source_record_row(src_line_009, table_row, 9, distribution, new_york).",
        "source_record_cell(src_line_009, retailers, aldi_walmart).",
        "sold_in_state(product_bulk, ct).",
        "sold_in_state(product_bulk, de).",
        "sold_in_state(product_bulk, il).",
        "sold_at_store(product_bulk, walmart).",
    ]
    summary = _extract_compile_summary(
        {
            "parsed_ok": True,
            "parsed": {
                "candidate_predicates": [
                    {"signature": "sold_in_state/2"},
                    {"signature": "sold_at_store/2"},
                ]
            },
            "source_compile": {"admitted_count": len(facts), "skipped_count": 0, "facts": facts},
            "score": {"rough_score": 0.9, "risk_count": 2},
        }
    )

    assert summary["table_list_surface_flags"] == [
        "distribution_state_table_underpreserved:source_states=9:direct_states=3:missing=6"
        ":missing_states=in,ky,md,mi,nj,ny"
    ]

    gate = _quality_gate_result(
        {"fixture": "recall", "returncode": 0, "compile_json": "compile.json", "summary": summary},
        min_rough_score=0.775,
        max_risk_count=5,
    )

    assert gate["passed"] is False
    assert gate["reasons"] == [
        "table_list_surface:distribution_state_table_underpreserved:source_states=9:direct_states=3:missing=6"
        ":missing_states=in,ky,md,mi,nj,ny"
    ]


def test_compile_batch_summary_accepts_preserved_distribution_state_table() -> None:
    source_facts = [
        f"source_record_row(src_line_{index:03d}, table_row, {index}, distribution, {state})."
        for index, state in enumerate(
            [
                "connecticut",
                "delaware",
                "illinois",
                "indiana",
                "kentucky",
                "maryland",
                "michigan",
                "new_jersey",
            ],
            start=1,
        )
    ]
    source_facts.extend(
        f"source_record_cell(src_line_{index:03d}, retailers, walmart)."
        for index in range(1, 9)
    )
    direct_facts = [
        "sold_in_state(product_bulk, ct).",
        "sold_in_state(product_bulk, de).",
        "sold_in_state(product_bulk, il).",
        "sold_in_state(product_bulk, in).",
        "sold_in_state(product_bulk, ky).",
        "sold_in_state(product_bulk, md).",
        "sold_in_state(product_bulk, mi).",
        "sold_in_state(product_bulk, nj).",
    ]
    summary = _extract_compile_summary(
        {
            "parsed_ok": True,
            "parsed": {"candidate_predicates": [{"signature": "sold_in_state/2"}]},
            "source_compile": {
                "admitted_count": len(source_facts) + len(direct_facts),
                "skipped_count": 0,
                "facts": [*source_facts, *direct_facts],
            },
            "score": {"rough_score": 0.9, "risk_count": 2},
        }
    )

    assert summary["table_list_surface_flags"] == []


def test_compile_batch_summary_counts_distributed_predicate_as_distribution_surface() -> None:
    states = [
        "connecticut",
        "delaware",
        "illinois",
        "indiana",
        "kentucky",
        "maryland",
        "michigan",
        "new_jersey",
    ]
    source_facts = [
        f"source_record_row(src_line_{index:03d}, table_row, {index}, distribution, {state})."
        for index, state in enumerate(states, start=1)
    ]
    source_facts.extend(
        f"source_record_cell(src_line_{index:03d}, retailers, walmart)."
        for index in range(1, len(states) + 1)
    )
    direct_facts = [
        "bulk_item_distributed_to(product_bulk, retailer_walmart, state_ct).",
        "bulk_item_distributed_to(product_bulk, retailer_walmart, state_de).",
        "bulk_item_distributed_to(product_bulk, retailer_walmart, state_il).",
        "bulk_item_distributed_to(product_bulk, retailer_walmart, state_in).",
        "bulk_item_distributed_to(product_bulk, retailer_walmart, state_ky).",
        "bulk_item_distributed_to(product_bulk, retailer_walmart, state_md).",
        "bulk_item_distributed_to(product_bulk, retailer_walmart, state_mi).",
        "bulk_item_distributed_to(product_bulk, retailer_walmart, state_nj).",
    ]
    summary = _extract_compile_summary(
        {
            "parsed_ok": True,
            "parsed": {"candidate_predicates": [{"signature": "bulk_item_distributed_to/3"}]},
            "source_compile": {
                "admitted_count": len(source_facts) + len(direct_facts),
                "skipped_count": 0,
                "facts": [*source_facts, *direct_facts],
            },
            "score": {"rough_score": 0.9, "risk_count": 2},
        }
    )

    assert summary["table_list_surface_flags"] == []


def test_compile_batch_summary_flags_underpreserved_distribution_state_retailer_pairs() -> None:
    states = [
        "connecticut",
        "delaware",
        "illinois",
        "indiana",
        "kentucky",
        "maryland",
        "michigan",
        "new_jersey",
    ]
    source_facts: list[str] = []
    for index, state in enumerate(states, start=1):
        ref = f"src_line_{index:03d}"
        source_facts.extend(
            [
                f"source_record_row({ref}, table_row, {index}, distribution, {state}).",
                f"source_record_cell_item({ref}, 1, {state}).",
                f"source_record_cell_item({ref}, 2, walmart).",
                f"source_record_cell_item({ref}, 2, save_a_lot).",
            ]
        )
    direct_facts = [
        "product_retailer_in_state(product_bulk, retailer_walmart, state_ct).",
        "product_retailer_in_state(product_bulk, retailer_walmart, state_de).",
        "product_retailer_in_state(product_bulk, retailer_walmart, state_il).",
        "product_retailer_in_state(product_bulk, retailer_walmart, state_in).",
        "product_retailer_in_state(product_bulk, retailer_walmart, state_ky).",
        "product_retailer_in_state(product_bulk, retailer_walmart, state_md).",
        "product_retailer_in_state(product_bulk, retailer_walmart, state_mi).",
        "product_retailer_in_state(product_bulk, retailer_walmart, state_nj).",
    ]
    summary = _extract_compile_summary(
        {
            "parsed_ok": True,
            "parsed": {"candidate_predicates": [{"signature": "product_retailer_in_state/3"}]},
            "source_compile": {
                "admitted_count": len(source_facts) + len(direct_facts),
                "skipped_count": 0,
                "facts": [*source_facts, *direct_facts],
            },
            "score": {"rough_score": 0.9, "risk_count": 2},
        }
    )

    assert summary["table_list_surface_flags"] == [
        "distribution_state_retailer_pair_underpreserved:"
        "source_pairs=16:direct_pairs=8:missing=8:"
        "missing_pairs=ct:save_a_lot,de:save_a_lot,il:save_a_lot,in:save_a_lot,"
        "ky:save_a_lot,md:save_a_lot,mi:save_a_lot,nj:save_a_lot"
    ]


def test_compile_batch_summary_accepts_scaffold_covered_distribution_pairs() -> None:
    states = [
        ("connecticut", "ct"),
        ("delaware", "de"),
        ("illinois", "il"),
        ("indiana", "in"),
        ("kentucky", "ky"),
        ("maryland", "md"),
        ("michigan", "mi"),
        ("new_jersey", "nj"),
    ]
    source_facts: list[str] = []
    for index, (state, _state_atom) in enumerate(states, start=1):
        ref = f"src_line_{index:03d}"
        source_facts.extend(
            [
                f"source_record_row({ref}, table_row, {index}, distribution, {state}).",
                f"source_record_cell_item({ref}, 1, {state}).",
                f"source_record_cell_item({ref}, 2, walmart).",
                f"source_record_cell_item({ref}, 2, save_a_lot).",
                f"source_record_cell_item_pair({ref}, 1, {state}, 2, walmart).",
                f"source_record_cell_item_pair({ref}, 1, {state}, 2, save_a_lot).",
            ]
        )
    direct_facts = [
        f"product_retailer_in_state(product_bulk, retailer_walmart, state_{state_atom})."
        for _state, state_atom in states
    ]
    summary = _extract_compile_summary(
        {
            "parsed_ok": True,
            "parsed": {"candidate_predicates": [{"signature": "product_retailer_in_state/3"}]},
            "source_compile": {
                "admitted_count": len(source_facts) + len(direct_facts),
                "skipped_count": 0,
                "facts": [*source_facts, *direct_facts],
            },
            "score": {"rough_score": 0.9, "risk_count": 2},
        }
    )

    assert summary["table_list_surface_flags"] == []
    assert summary["table_list_surface_coverage_flags"] == [
        "distribution_state_retailer_pair_scaffold_covered:"
        "source_pairs=16:direct_pairs=8:covered_pairs=8:missing_direct=8:"
        "sample=ct:save_a_lot,de:save_a_lot,il:save_a_lot,in:save_a_lot,"
        "ky:save_a_lot,md:save_a_lot,mi:save_a_lot,nj:save_a_lot"
    ]

    gate = _quality_gate_result(
        {"fixture": "recall", "returncode": 0, "compile_json": "compile.json", "summary": summary},
        min_rough_score=0.775,
        max_risk_count=5,
    )

    assert gate["passed"] is True
    assert gate["table_list_surface_coverage_flags"] == summary["table_list_surface_coverage_flags"]


def test_compile_batch_summary_accepts_fully_scaffolded_distribution_states() -> None:
    states = [
        ("connecticut", "ct"),
        ("delaware", "de"),
        ("illinois", "il"),
        ("indiana", "in"),
        ("kentucky", "ky"),
        ("maryland", "md"),
        ("michigan", "mi"),
        ("new_jersey", "nj"),
    ]
    source_facts: list[str] = []
    for index, (state, _state_atom) in enumerate(states, start=1):
        ref = f"src_line_{index:03d}"
        source_facts.extend(
            [
                f"source_record_row({ref}, table_row, {index}, distribution, {state}).",
                f"source_record_cell_item({ref}, 1, {state}).",
                f"source_record_cell_item({ref}, 2, walmart).",
                f"source_record_cell_item_pair({ref}, 1, {state}, 2, walmart).",
            ]
        )
    summary = _extract_compile_summary(
        {
            "parsed_ok": True,
            "parsed": {"candidate_predicates": [{"signature": "product_retailer_in_state/3"}]},
            "source_compile": {
                "admitted_count": len(source_facts) + 1,
                "skipped_count": 0,
                "facts": [*source_facts, "product_name(product_bulk, bulk_retail_items)."],
            },
            "score": {"rough_score": 0.9, "risk_count": 2},
        }
    )

    assert summary["table_list_surface_flags"] == []
    assert summary["table_list_surface_coverage_flags"] == [
        "distribution_state_retailer_pair_scaffold_covered:"
        "source_pairs=8:direct_pairs=0:covered_pairs=8:missing_direct=8:"
        "sample=ct:walmart,de:walmart,il:walmart,in:walmart,ky:walmart,md:walmart,mi:walmart,nj:walmart"
    ]


def test_compile_batch_summary_flags_distribution_subject_granularity_split() -> None:
    states = [
        "connecticut",
        "delaware",
        "illinois",
        "indiana",
        "kentucky",
        "maryland",
        "michigan",
        "new_jersey",
        "new_york",
    ]
    source_facts = [
        f"source_record_row(src_line_{index:03d}, table_row, {index}, distribution, {state})."
        for index, state in enumerate(states, start=1)
    ]
    source_facts.extend(
        f"source_record_cell(src_line_{index:03d}, retailers, walmart_kroger)."
        for index in range(1, len(states) + 1)
    )
    direct_facts = [
        "product_retailer_in_state(bulk_retail_items, walmart, ct).",
        "product_retailer_in_state(bulk_retail_items, walmart, de).",
        "product_retailer_in_state(bulk_retail_items, kroger, il).",
        "product_retailer_in_state(cucumber_whole, walmart, ct).",
        "product_retailer_in_state(cucumber_whole, walmart, de).",
        "product_retailer_in_state(cucumber_whole, kroger, il).",
        "product_retailer_in_state(cucumber_whole, kroger, in).",
        "product_retailer_in_state(cucumber_whole, aldi, ky).",
        "product_retailer_in_state(cucumber_whole, walmart, md).",
        "product_retailer_in_state(cucumber_whole, walmart, mi).",
        "product_retailer_in_state(cucumber_whole, walmart, nj).",
        "product_retailer_in_state(cucumber_whole, aldi, ny).",
    ]
    summary = _extract_compile_summary(
        {
            "parsed_ok": True,
            "parsed": {"candidate_predicates": [{"signature": "product_retailer_in_state/3"}]},
            "source_compile": {
                "admitted_count": len(source_facts) + len(direct_facts),
                "skipped_count": 0,
                "facts": [*source_facts, *direct_facts],
            },
            "score": {"rough_score": 0.9, "risk_count": 2},
        }
    )

    assert summary["table_list_surface_flags"] == [
        "distribution_subject_granularity_split:"
        "subjects=2:category=bulk_retail_items:category_states=3:max_subject_states=9:source_states=9"
    ]

    gate = _quality_gate_result(
        {"fixture": "recall", "returncode": 0, "compile_json": "compile.json", "summary": summary},
        min_rough_score=0.775,
        max_risk_count=5,
    )

    assert gate["passed"] is False
    assert gate["reasons"] == [
        "table_list_surface:distribution_subject_granularity_split:"
        "subjects=2:category=bulk_retail_items:category_states=3:max_subject_states=9:source_states=9"
    ]


def test_quality_retry_context_names_underpreserved_distribution_tables() -> None:
    lines = _quality_retry_context_lines(
        {
            "reasons": [
                "table_list_surface:distribution_state_table_underpreserved:"
                "source_states=9:direct_states=3:missing=6:missing_states=in,ky,md,mi,nj,ny"
            ]
        }
    )

    joined = "\n".join(lines)
    assert "state/retailer distribution table" in joined
    assert "each table row as joinable direct distribution facts" in joined
    assert "distributed_in_state/2" in joined
    assert "source_record_cell_item and source_record_cell_item_qualifier" in joined
    assert "trailing short rows and single-retailer rows" in joined
    assert "stable product/item atoms" in joined
    assert "explicit alias, equivalence, or governed-category row" in joined
    assert "source_record_cell/source_record_text_atom row is provenance only" in joined
    assert "in, ky, md, mi, nj, ny" in joined


def test_quality_retry_context_names_distribution_subject_granularity_split() -> None:
    lines = _quality_retry_context_lines(
        {
            "reasons": [
                "table_list_surface:distribution_subject_granularity_split:"
                "subjects=2:category=bulk_retail_items:category_states=3:max_subject_states=9:source_states=9"
            ]
        }
    )

    joined = "\n".join(lines)
    assert "multiple granularity subjects" in joined
    assert "one stable governed distribution subject" in joined
    assert "category-to-product/governed-product rows" in joined
    assert "disconnected answer surfaces" in joined


def test_quality_retry_context_names_distribution_state_retailer_pair_holds() -> None:
    lines = _quality_retry_context_lines(
        {
            "reasons": [
                "table_list_surface:distribution_state_retailer_pair_underpreserved:"
                "source_pairs=16:direct_pairs=8:missing=8"
            ]
        }
    )

    joined = "\n".join(lines)
    assert "paired state plus retailer coordinates" in joined
    assert "single-retailer rows" in joined
    assert "retailer-specific product restrictions" in joined
    assert "state-only row and a retailer-only row are not equivalent" in joined


def test_compile_batch_summary_flags_underpreserved_prior_recall_date(tmp_path) -> None:
    source = tmp_path / "source.md"
    source.write_text(
        "The firm is expanding its July 12, 2024 recall to include additional peppers. "
        "This announcement is dated July 22, 2024.\n",
        encoding="utf-8",
    )
    facts = [
        "recall_date(recall_expansion_2024_07_22, 2024_07_22).",
        "recall_date(recall_expansion_2024_07_22, july_12_2024).",
        "source_record_text_atom(src_line_0001, july_12_2024).",
    ]
    summary = _extract_compile_summary(
        {
            "parsed_ok": True,
            "text_file": str(source),
            "parsed": {"candidate_predicates": [{"signature": "recall_date/2"}]},
            "source_compile": {"admitted_count": len(facts), "skipped_count": 0, "facts": facts},
            "score": {"rough_score": 0.9, "risk_count": 2},
        }
    )

    assert summary["public_recall_surface_flags"] == [
        "prior_recall_date_underpreserved:source_dates=1:direct_dates=0:missing=2024_07_12"
    ]

    gate = _quality_gate_result(
        {"fixture": "recall", "returncode": 0, "compile_json": "compile.json", "summary": summary},
        min_rough_score=0.775,
        max_risk_count=5,
    )

    assert gate["passed"] is False
    assert gate["reasons"] == [
        "public_recall_surface:"
        "prior_recall_date_underpreserved:source_dates=1:direct_dates=0:missing=2024_07_12"
    ]


def test_compile_batch_summary_accepts_direct_prior_recall_date(tmp_path) -> None:
    source = tmp_path / "source.md"
    source.write_text(
        "The firm is expanding its July 12, 2024 recall to include additional peppers. "
        "This announcement is dated July 22, 2024.\n",
        encoding="utf-8",
    )
    facts = [
        "recall_date(prior_recall_2024_07_12, 2024_07_12).",
        "recall_date(recall_expansion_2024_07_22, 2024_07_22).",
    ]
    summary = _extract_compile_summary(
        {
            "parsed_ok": True,
            "text_file": str(source),
            "parsed": {"candidate_predicates": [{"signature": "recall_date/2"}]},
            "source_compile": {"admitted_count": len(facts), "skipped_count": 0, "facts": facts},
            "score": {"rough_score": 0.9, "risk_count": 2},
        }
    )

    assert summary["public_recall_surface_flags"] == []


def test_compile_batch_summary_accepts_source_record_prior_recall_date_surface(tmp_path) -> None:
    source = tmp_path / "source.md"
    source.write_text(
        "The firm is expanding its July 12, 2024 recall to include additional peppers. "
        "This announcement is dated July 22, 2024.\n",
        encoding="utf-8",
    )
    facts = [
        (
            "source_record_row_context(src_line_0001, recall_announcement, "
            "the_firm_is_expanding_its_july_12_2024_recall_to_include_additional_peppers, "
            "company_announcement)."
        ),
        "source_record_text_atom(src_line_0001, the_firm_is_expanding_its_july_12_2024_recall_to_include_additional_peppers).",
        "recall_date(recall_expansion_2024_07_22, 2024_07_22).",
    ]
    summary = _extract_compile_summary(
        {
            "parsed_ok": True,
            "text_file": str(source),
            "parsed": {"candidate_predicates": [{"signature": "recall_date/2"}]},
            "source_compile": {"admitted_count": len(facts), "skipped_count": 0, "facts": facts},
            "score": {"rough_score": 0.9, "risk_count": 2},
        }
    )

    assert summary["public_recall_surface_flags"] == []


def test_quality_retry_context_names_prior_recall_date_holds() -> None:
    lines = _quality_retry_context_lines(
        {
            "reasons": [
                "public_recall_surface:"
                "prior_recall_date_underpreserved:source_dates=1:direct_dates=1:missing=2024_07_12"
            ]
        }
    )

    joined = "\n".join(lines)
    assert "original, prior, previous, or earlier recall date" in joined
    assert "distinct prior/original recall event-date row" in joined
    assert "separate from the current expansion" in joined
    assert "source_record_text_atom" in joined


def test_quality_retry_context_defers_small_lanes_when_table_surface_is_high_cardinality() -> None:
    lines = _quality_retry_context_lines(
        {
            "reasons": [
                "public_recall_surface:"
                "prior_recall_date_underpreserved:source_dates=1:direct_dates=0:missing=2024_07_12",
                "table_list_surface:distribution_state_table_underpreserved:"
                "source_states=18:direct_states=13:missing=5:missing_states=me,mo,nc,ri,tn",
                "table_list_surface:distribution_state_retailer_pair_underpreserved:"
                "source_pairs=52:direct_pairs=13:missing=39",
                "identity_canonicality:duplicate_named_subjects_without_alias:groups=4",
            ]
        }
    )

    joined = "\n".join(lines)
    assert "state/retailer distribution table" in joined
    assert "paired state plus retailer coordinates" not in joined
    assert "prior/original recall event-date row" not in joined
    assert "same product/item/object name" not in joined


def test_quality_retry_context_skips_pair_only_high_cardinality_table_holds() -> None:
    lines = _quality_retry_context_lines(
        {
            "reasons": [
                "table_list_surface:distribution_state_retailer_pair_underpreserved:"
                "source_pairs=52:direct_pairs=18:missing=39",
            ]
        }
    )

    assert lines == []


def test_quality_retry_context_keeps_small_lanes_when_table_surface_is_low_cardinality() -> None:
    lines = _quality_retry_context_lines(
        {
            "reasons": [
                "public_recall_surface:"
                "prior_recall_date_underpreserved:source_dates=1:direct_dates=0:missing=2024_07_12",
                "table_list_surface:distribution_state_table_underpreserved:"
                "source_states=18:direct_states=17:missing=1:missing_states=tn",
            ]
        }
    )

    joined = "\n".join(lines)
    assert "state/retailer distribution table" in joined
    assert "prior/original recall event-date row" in joined


def test_compile_batch_summary_flags_duplicate_named_subjects_without_alias() -> None:
    facts = [
        "product_name(prod_bulk_anaheim_peppers, anaheim_peppers).",
        "product_name(prod_bulk_anaheim, anaheim_peppers).",
        "distributed_in_state(prod_bulk_anaheim_peppers, md).",
        "sold_at_retailer(prod_bulk_anaheim, retailer_walmart, md).",
    ]
    summary = _extract_compile_summary(
        {
            "parsed_ok": True,
            "parsed": {"candidate_predicates": [{"signature": "product_name/2"}]},
            "source_compile": {"admitted_count": len(facts), "skipped_count": 0, "facts": facts},
            "score": {"rough_score": 0.9, "risk_count": 2},
        }
    )

    assert summary["identity_canonicality_flags"] == [
        "duplicate_named_subjects_without_alias:groups=1:predicates=product_name=1:"
        "sample=product_name:anaheim_peppers:2"
    ]

    gate = _quality_gate_result(
        {"fixture": "recall", "returncode": 0, "compile_json": "compile.json", "summary": summary},
        min_rough_score=0.775,
        max_risk_count=5,
    )

    assert gate["passed"] is False
    assert gate["reasons"] == [
        "identity_canonicality:duplicate_named_subjects_without_alias:groups=1:predicates=product_name=1:"
        "sample=product_name:anaheim_peppers:2"
    ]


def test_quality_gate_tiers_blocking_and_diagnostic_reasons() -> None:
    gate = _quality_gate_result(
        {
            "fixture": "fixture",
            "returncode": 0,
            "compile_json": "compile.json",
            "summary": {
                "parsed_ok": True,
                "rough_score": 0.9,
                "risk_count": 2,
                "compile_admitted": 4,
                "compile_skipped": 0,
                "profile_delivery_flags": [
                    "source_claim_carrier_partially_delivered:source=1:offered=source_attributed_claim/4"
                ],
                "compile_surface_contract_flags": [
                    "source_authority_pair_preservation:ledger_only:source=1:direct=0"
                ],
                "compile_health_flags": ["zero_yield=1"],
            },
        },
        min_rough_score=0.775,
        max_risk_count=5,
    )

    assert gate["passed"] is False
    assert gate["blocking_passed"] is False
    assert gate["blocking_reasons"] == [
        "compile_surface_contract:source_authority_pair_preservation:ledger_only:source=1:direct=0"
    ]
    assert gate["diagnostic_reasons"] == [
        "profile_delivery:source_claim_carrier_partially_delivered:source=1:offered=source_attributed_claim/4",
        "compile_health:zero_yield=1",
    ]
    assert gate["advisory_reasons"] == []


def test_compile_batch_summary_counts_quality_gate_tiers() -> None:
    summary = _summarize(
        [
            {
                "fixture": "blocking",
                "returncode": 0,
                "compile_json": "blocking.json",
                "summary": {
                    "parsed_ok": True,
                    "rough_score": 0.9,
                    "risk_count": 2,
                    "compile_admitted": 4,
                    "compile_skipped": 0,
                    "identity_canonicality_flags": ["duplicate_named_subjects_without_alias:groups=1"],
                },
            },
            {
                "fixture": "diagnostic",
                "returncode": 0,
                "compile_json": "diagnostic.json",
                "summary": {
                    "parsed_ok": True,
                    "rough_score": 0.9,
                    "risk_count": 2,
                    "compile_admitted": 4,
                    "compile_skipped": 0,
                    "profile_delivery_flags": ["vote_tally_carrier_offered_but_undelivered:source=1"],
                },
            },
        ],
        lanes=1,
        base_timeout=1,
        effective_timeout=1,
        quality_gate=True,
    )

    gate = summary["quality_gate"]
    assert gate["passed"] is False
    assert gate["blocking_passed"] is False
    assert gate["hold_count"] == 2
    assert gate["blocking_hold_count"] == 1
    assert gate["diagnostic_hold_count"] == 1
    rendered = _render_md(summary)
    assert "Blocking / diagnostic / advisory holds: `1 / 1 / 0`" in rendered


def test_compile_batch_summary_accepts_duplicate_names_with_alias() -> None:
    facts = [
        "product_name(prod_bulk_anaheim_peppers, anaheim_peppers).",
        "product_name(prod_bulk_anaheim, anaheim_peppers).",
        "product_alias(prod_bulk_anaheim, prod_bulk_anaheim_peppers).",
        "distributed_in_state(prod_bulk_anaheim_peppers, md).",
        "sold_at_retailer(prod_bulk_anaheim, retailer_walmart, md).",
    ]
    summary = _extract_compile_summary(
        {
            "parsed_ok": True,
            "parsed": {"candidate_predicates": [{"signature": "product_name/2"}]},
            "source_compile": {"admitted_count": len(facts), "skipped_count": 0, "facts": facts},
            "score": {"rough_score": 0.9, "risk_count": 2},
        }
    )

    assert summary["identity_canonicality_flags"] == []


def test_compile_batch_summary_accepts_duplicate_names_with_same_metadata_shape() -> None:
    facts = [
        "product_name(wiers_farm_bagged_cubanelle, wiers_farm_bagged_cubanelle).",
        "product_upc(wiers_farm_bagged_cubanelle, 073064201836).",
        "product_brand(wiers_farm_bagged_cubanelle, wiers_farm).",
        "product_weight(wiers_farm_bagged_cubanelle, 16_oz).",
        "product_name(prod_wiers_cubanelle, wiers_farm_bagged_cubanelle).",
        "product_upc(prod_wiers_cubanelle, 073064201836).",
        "product_brand(prod_wiers_cubanelle, wiers_farm).",
        "product_weight(prod_wiers_cubanelle, 16_oz).",
    ]
    summary = _extract_compile_summary(
        {
            "parsed_ok": True,
            "parsed": {"candidate_predicates": [{"signature": "product_name/2"}]},
            "source_compile": {"admitted_count": len(facts), "skipped_count": 0, "facts": facts},
            "score": {"rough_score": 0.9, "risk_count": 2},
        }
    )

    assert summary["identity_canonicality_flags"] == []


def test_quality_retry_context_names_duplicate_identity_atoms() -> None:
    lines = _quality_retry_context_lines(
        {
            "reasons": [
                "identity_canonicality:duplicate_named_subjects_without_alias:"
                "groups=1:predicates=product_name=1:sample=product_name:anaheim_peppers:2"
            ]
        }
    )

    joined = "\n".join(lines)
    assert "same product/item/object name" in joined
    assert "reuse one stable subject atom" in joined
    assert "alias/equivalence or governed-category rows" in joined
    assert "Identity repair must preserve existing repeated-table coverage" in joined
    assert "do not drop direct state/retailer/restriction rows" in joined
    assert "source_record_cell_item_qualifier" in joined


def test_compile_batch_summary_refreshes_stale_profile_delivery_from_source_text(tmp_path) -> None:
    source = tmp_path / "source.md"
    source.write_text("Solicitor opinion says actual knowledge remains unresolved.\n", encoding="utf-8")
    summary = _extract_compile_summary(
        {
            "parsed_ok": True,
            "domain_hint": "source attributed claim report status",
            "text_file": str(source),
            "parsed": {
                "candidate_predicates": [
                    {"signature": "legal_opinion/3", "args": ["author", "principle", "conclusion"]},
                    {
                        "signature": "source_attributed_claim/4",
                        "args": ["claim_id", "source_or_speaker", "content_or_status", "source_row_or_scope"],
                    },
                ]
            },
            "source_compile": {
                "facts": [
                    "legal_opinion(brennan, permit_in_force_principle, actual_knowledge_unresolved).",
                ],
                "profile_delivery": {
                    "findings": [
                        {
                            "class": "source_claim_carrier_offered_but_undelivered",
                            "source_signal_count": 1,
                            "offered_carriers": ["source_attributed_claim/4"],
                        }
                    ]
                },
            },
            "score": {"rough_score": 0.9, "risk_count": 2},
        }
    )

    assert summary["profile_delivery_flags"] == []


def test_profile_delivery_flags_include_quantity_row_requirement() -> None:
    payload = {
        "source_compile": {
            "profile_delivery": {
                "findings": [
                    {
                        "class": "quantity_carrier_partially_delivered",
                        "source_signal_count": 3,
                        "required_carrier_row_count": 5,
                        "offered_carriers": ["event_measurement/4", "event_duration/3"],
                    }
                ]
            }
        }
    }

    assert _profile_delivery_flags(payload) == [
        "quantity_carrier_partially_delivered:source=3:required=5:offered=event_measurement/4,event_duration/3"
    ]


def test_profile_delivery_flags_include_quantity_missing_keys() -> None:
    payload = {
        "source_compile": {
            "profile_delivery": {
                "findings": [
                    {
                        "class": "quantity_carrier_partially_delivered",
                        "source_signal_count": 5,
                        "required_carrier_row_count": 6,
                        "offered_carriers": ["event_measurement/4"],
                        "missing_signal_keys": ["duration:line_stop"],
                    }
                ]
            }
        }
    }

    assert _profile_delivery_flags(payload) == [
        "quantity_carrier_partially_delivered:source=5:required=6:offered=event_measurement/4"
        ":missing=duration:line_stop"
    ]


def test_profile_delivery_flags_include_source_claim_missing_keys() -> None:
    payload = {
        "source_compile": {
            "profile_delivery": {
                "findings": [
                    {
                        "class": "source_claim_carrier_partially_delivered",
                        "source_signal_count": 2,
                        "offered_carriers": ["source_attributed_claim/4"],
                        "missing_signal_keys": [
                            "note:draft:no_effect",
                            "letter_of_intent:letter_of_intent:not_binding",
                        ],
                    }
                ]
            }
        }
    }

    assert _profile_delivery_flags(payload) == [
        "source_claim_carrier_partially_delivered:source=2:offered=source_attributed_claim/4"
        ":missing=note:draft:no_effect,letter_of_intent:letter_of_intent:not_binding"
    ]


def test_quality_retry_context_includes_partial_profile_delivery() -> None:
    lines = _quality_retry_context_lines(
        {
            "reasons": [
                "profile_delivery:source_authority_carrier_partially_delivered:"
                "source=3:offered=source_authority/3"
            ]
        }
    )

    assert any("fewer than the source-signal count" in line for line in lines)
    assert any("source-authority row for every distinct" in line for line in lines)


def test_quality_retry_context_names_source_claim_description_trap() -> None:
    lines = _quality_retry_context_lines(
        {
            "reasons": [
                "profile_delivery:source_claim_carrier_offered_but_undelivered:"
                "source=2:offered=source_attributed_claim/4"
            ]
        }
    )

    joined = "\n".join(lines)
    assert "Quoted notes, letters, opinions, and statements" in joined
    assert "description/source_detail" in joined
    assert "does not replace the source-to-claim carrier" in joined
    assert "source-attributed claim rows are additive evidence" in joined
    assert "vote rows, survey or measurement rows" in joined


def test_quality_retry_context_names_source_claim_missing_keys() -> None:
    lines = _quality_retry_context_lines(
        {
            "reasons": [
                "profile_delivery:source_claim_carrier_partially_delivered:"
                "source=2:offered=source_attributed_claim/4"
                ":missing=note:draft:no_effect,letter_of_intent:letter_of_intent:not_binding"
            ]
        }
    )

    joined = "\n".join(lines)
    assert "missing source-attributed claim kinds" in joined
    assert "note:draft:no_effect" in joined
    assert "do not satisfy these with unrelated quoted notes" in joined
    assert "source-attributed claim rows are additive evidence" in joined


def test_quality_retry_context_prefers_four_slot_speaker_claims() -> None:
    lines = _quality_retry_context_lines(
        {
            "reasons": [
                "profile_delivery:source_claim_carrier_partially_delivered:"
                "source=4:offered=source_claim/3,source_attributed_claim/4"
                ":missing=statement:claim:not_flagged,opinion:claim:not_legal_determination"
            ]
        }
    )

    joined = "\n".join(lines)
    assert "speaker/document-framed statements" in joined
    assert "source_attributed_claim/4" in joined
    assert "A shorter source_claim/3 row is additive" in joined


def test_quality_retry_context_names_objection_and_concern_claim_keys() -> None:
    lines = _quality_retry_context_lines(
        {
            "reasons": [
                "profile_delivery:source_claim_carrier_partially_delivered:"
                "source=2:offered=source_attributed_claim/4"
                ":missing=note:claim:objection,source:claim:concern"
            ]
        }
    )

    joined = "\n".join(lines).casefold()
    assert "note the objection" in joined
    assert "proceeds despite the objection" in joined
    assert "concerned about" in joined
    assert "speaker/source, concern content" in joined


def test_quality_retry_context_names_numeric_event_details() -> None:
    lines = _quality_retry_context_lines(
        {
            "reasons": [
                "profile_delivery:quantity_carrier_offered_but_undelivered:"
                "source=5:offered=event_measurement/4"
            ]
        }
    )

    joined = "\n".join(lines)
    assert "setpoint before/after values" in joined
    assert "feed rates" in joined
    assert "separate before and after carrier rows" in joined
    assert "do not replace the direct numeric value row" in joined


def test_quality_retry_context_names_scope_discrepancy_missing_issues() -> None:
    lines = _quality_retry_context_lines(
        {
            "reasons": [
                "profile_delivery:scope_discrepancy_carrier_partially_delivered:"
                "source=5:offered=scope_discrepancy/6:missing=reporting_frequency,fire_hydrants"
            ]
        }
    )

    joined = "\n".join(lines)
    assert "not the full source-stated discrepancy set" in joined
    assert "reporting_frequency" in joined
    assert "fire_hydrants" in joined
    assert "both sides and the source/basis joinable" in joined


def test_quality_retry_context_names_duration_total_for_partial_quantity_delivery() -> None:
    lines = _quality_retry_context_lines(
        {
            "reasons": [
                "profile_delivery:quantity_carrier_partially_delivered:"
                "source=3:required=5:offered=event_measurement/4,event_duration/3"
            ]
        }
    )

    joined = "\n".join(lines)
    assert "line-stop or response durations" in joined
    assert "event_duration/3" in joined
    assert "separate before and after carrier rows" in joined


def test_quality_retry_context_names_quantity_missing_keys() -> None:
    lines = _quality_retry_context_lines(
        {
            "reasons": [
                "profile_delivery:quantity_carrier_partially_delivered:"
                "source=5:required=6:offered=event_measurement/4:missing=duration:line_stop"
            ]
        }
    )

    joined = "\n".join(lines)
    assert "missing quantity/event kinds" in joined
    assert "duration:line_stop" in joined
    assert "include both the interval subject" in joined
    assert "exact stated elapsed total" in joined
    assert "state-transition rows" in joined


def test_quality_retry_context_names_date_bearing_event_identifier_hold() -> None:
    lines = _quality_retry_context_lines(
        {
            "reasons": [
                "profile_delivery:event_identifier_date_only:source=3:offered=none"
            ]
        }
    )

    joined = "\n".join(lines)
    assert "event identifiers that embed dates or timestamps" in joined
    assert "event_timestamp/2" in joined
    assert "joinable argument" in joined


def test_quality_retry_metadata_preserves_legacy_first_attempt_fields() -> None:
    metadata = _quality_retry_metadata(
        attempts=[
            {
                "attempt": 1,
                "input_compile_json": "a.json",
                "reasons": ["rough_score<0.775"],
                "context_lines": ["retry line"],
                "output_compile_json": "b.json",
            },
            {
                "attempt": 2,
                "input_compile_json": "b.json",
                "reasons": ["profile_delivery:quantity_carrier_offered_but_undelivered:source=5:offered=event_measurement/4"],
                "context_lines": ["quantity line"],
                "output_compile_json": "c.json",
            },
        ],
        first_reasons=["rough_score<0.775"],
        first_compile_json="a.json",
        final_gate={"decision": "hold", "reasons": ["still_held"]},
        blocked_reason="max_attempts_exhausted",
    )

    assert metadata["attempted"] is True
    assert metadata["attempt_count"] == 2
    assert metadata["initial_reasons"] == ["rough_score<0.775"]
    assert metadata["context_lines"] == ["retry line"]
    assert metadata["initial_compile_json"] == "a.json"
    assert metadata["final_reasons"] == ["still_held"]
    assert metadata["reason"] == "max_attempts_exhausted"


def test_quality_retry_context_merge_carries_forward_prior_guidance() -> None:
    merged = _merge_quality_retry_context_lines(
        ["quantity guidance", "scheduled guidance"],
        ["scheduled guidance", "source claim guidance"],
    )

    assert merged == ["quantity guidance", "scheduled guidance", "source claim guidance"]


def test_quality_gate_rank_prefers_less_regressed_retry_attempt() -> None:
    narrow_hold = {
        "passed": False,
        "reasons": ["profile_delivery:quantity_carrier_partially_delivered:source=5"],
        "rough_score": 0.889,
        "risk_count": 5,
        "compile_skipped_share": 0.0417,
    }
    regressed_hold = {
        "passed": False,
        "reasons": [
            "detail_wrapper_drift:identity_backbone_missing_with_wrapper:event_record",
            "detail_wrapper_drift:quantity_backbone_missing_with_wrapper:event_record",
            "profile_delivery:quantity_carrier_offered_but_undelivered:source=5",
        ],
        "rough_score": 1.0,
        "risk_count": 5,
        "compile_skipped_share": 0.0341,
    }

    assert _quality_gate_rank_tuple(narrow_hold) < _quality_gate_rank_tuple(regressed_hold)


def test_quality_gate_rank_prefers_lower_table_missing_count() -> None:
    severe_hold = {
        "passed": False,
        "reasons": [
            "table_list_surface:distribution_state_table_underpreserved:source_states=18:direct_states=0:missing=18"
        ],
        "rough_score": 0.944,
        "risk_count": 4,
        "compile_skipped_share": 0.0046,
    }
    narrower_hold = {
        "passed": False,
        "reasons": [
            "table_list_surface:distribution_state_table_underpreserved:source_states=18:direct_states=13:missing=5"
        ],
        "rough_score": 0.889,
        "risk_count": 4,
        "compile_skipped_share": 0.02,
    }

    assert _quality_gate_rank_tuple(narrower_hold) < _quality_gate_rank_tuple(severe_hold)


def test_quality_gate_rank_does_not_prefer_fewer_reasons_with_larger_surface_regression() -> None:
    smaller_surface_hold = {
        "passed": False,
        "reasons": [
            "public_recall_surface:prior_recall_date_underpreserved:source_dates=1:direct_dates=0:missing=2024_07_12",
            "table_list_surface:distribution_state_table_underpreserved:source_states=18:direct_states=13:missing=5",
            "table_list_surface:distribution_state_retailer_pair_underpreserved:source_pairs=52:direct_pairs=13:missing=39",
            "identity_canonicality:duplicate_named_subjects_without_alias:groups=4",
        ],
        "rough_score": 0.889,
        "risk_count": 5,
        "compile_skipped_share": 0.0,
    }
    larger_surface_hold = {
        "passed": False,
        "reasons": [
            "table_list_surface:distribution_state_table_underpreserved:source_states=18:direct_states=15:missing=3",
            "table_list_surface:distribution_state_retailer_pair_underpreserved:source_pairs=52:direct_pairs=0:missing=52",
            "identity_canonicality:duplicate_named_subjects_without_alias:groups=4",
        ],
        "rough_score": 0.944,
        "risk_count": 4,
        "compile_skipped_share": 0.139,
    }

    assert _quality_gate_rank_tuple(smaller_surface_hold) < _quality_gate_rank_tuple(larger_surface_hold)


def test_compile_batch_summary_allows_detail_wrapper_with_backbone() -> None:
    summary = _extract_compile_summary(
        {
            "parsed_ok": True,
            "parsed": {"candidate_predicates": [{"signature": "context/2"}]},
            "source_compile": {
                "facts": [
                    "source_record_field(src_line_001, record_id, rec_07).",
                    "source_record_field(src_line_001, departure_time, v_06_30).",
                    "record_id(rec_07).",
                    "departure_time(rec_07, v_06_30).",
                    "context(rec_07, departure_context).",
                ],
            },
            "score": {"rough_score": 0.9, "risk_count": 2},
        }
    )

    assert summary["detail_wrapper_drift_flags"] == []


def test_detail_wrapper_drift_ignores_unlinked_source_row_groups() -> None:
    summary = _extract_compile_summary(
        {
            "parsed_ok": True,
            "parsed": {"candidate_predicates": [{"signature": "event_record/2"}]},
            "source_compile": {
                "facts": [
                    "source_record_field(src_line_001, location, dryer_chamber_4_plc_cabinet).",
                    "source_record_field(src_line_002, event_id, ev_01).",
                    "event_record(ev_01, drying_chamber_humidity_alarm).",
                ],
            },
            "score": {"rough_score": 0.9, "risk_count": 2},
        }
    )

    assert "location_backbone_missing_with_wrapper:event_record" not in summary["detail_wrapper_drift_flags"]


def test_compile_batch_summary_treats_date_atoms_as_date_time_backbone() -> None:
    summary = _extract_compile_summary(
        {
            "parsed_ok": True,
            "parsed": {"candidate_predicates": [{"signature": "source_detail/4"}]},
            "source_compile": {
                "facts": [
                    "source_record_field(src_line_001, hearing_date, v_2026_04_24).",
                    "hearing_event(hearing_1, 2026_04_24, held).",
                    "source_detail(hearing_1, note, held_as_scheduled, src_line_001).",
                ],
            },
            "score": {"rough_score": 0.9, "risk_count": 2},
        }
    )

    assert "date_time_backbone_missing_with_wrapper:source_detail" not in summary["detail_wrapper_drift_flags"]


def test_detail_wrapper_drift_counts_contested_state_values() -> None:
    payload = {
        "parsed": {"candidate_predicates": [{"signature": "source_detail/4"}]},
        "source_compile": {
            "facts": [
                "source_record_field(src_line_1, title_status, contested_by_party).",
                "register_entry(item_a, external_a, object_a, holder_a, owner_a, contested_by_party).",
                "source_detail(item_a, title_status, contested_by_party, src_line_1).",
            ]
        },
    }

    assert _detail_wrapper_drift_flags(payload) == []


def test_compile_quality_gate_passes_accepted_draw_shape() -> None:
    result = {
        "fixture": "fixture_a",
        "returncode": 0,
        "compile_json": "compile.json",
        "summary": {
            "parsed_ok": True,
            "rough_score": 0.833,
            "risk_count": 5,
            "candidate_predicates": 18,
            "compile_admitted": 86,
            "compile_skipped": 52,
        },
    }

    gate = _quality_gate_result(result, min_rough_score=0.775, max_risk_count=5)

    assert gate["passed"] is True
    assert gate["decision"] == "pass"
    assert gate["compile_skipped_share"] == 0.3768


def test_compile_quality_gate_holds_high_risk_draw() -> None:
    result = {
        "fixture": "fixture_b",
        "returncode": 0,
        "compile_json": "compile.json",
        "summary": {
            "parsed_ok": True,
            "rough_score": 0.778,
            "risk_count": 6,
            "candidate_predicates": 30,
            "compile_admitted": 176,
            "compile_skipped": 23,
        },
    }

    gate = _quality_gate_result(result, min_rough_score=0.775, max_risk_count=5)

    assert gate["passed"] is False
    assert gate["decision"] == "hold"
    assert gate["reasons"] == ["risk_count>5"]


def test_compile_quality_gate_holds_detail_wrapper_drift() -> None:
    result = {
        "fixture": "fixture_detail",
        "returncode": 0,
        "compile_json": "compile.json",
        "summary": {
            "parsed_ok": True,
            "rough_score": 0.9,
            "risk_count": 2,
            "candidate_predicates": 12,
            "compile_admitted": 30,
            "compile_skipped": 0,
            "detail_wrapper_drift_flags": ["identity_backbone_missing_with_wrapper:context"],
        },
    }

    gate = _quality_gate_result(result, min_rough_score=0.775, max_risk_count=5)

    assert gate["passed"] is False
    assert gate["decision"] == "hold"
    assert gate["reasons"] == ["detail_wrapper_drift:identity_backbone_missing_with_wrapper:context"]


def test_compile_quality_gate_holds_surface_contract_flag() -> None:
    result = {
        "fixture": "fixture_contract",
        "returncode": 0,
        "compile_json": "compile.json",
        "summary": {
            "parsed_ok": True,
            "rough_score": 0.9,
            "risk_count": 2,
            "candidate_predicates": 12,
            "compile_admitted": 30,
            "compile_skipped": 0,
            "compile_surface_contract_flags": [
                "operational_lifecycle_preservation:ledger_only:source=2:direct=0"
            ],
        },
    }

    gate = _quality_gate_result(result, min_rough_score=0.775, max_risk_count=5)

    assert gate["passed"] is False
    assert gate["decision"] == "hold"
    assert gate["reasons"] == [
        "compile_surface_contract:operational_lifecycle_preservation:ledger_only:source=2:direct=0"
    ]


def test_compile_quality_gate_holds_profile_delivery_flag() -> None:
    result = {
        "fixture": "fixture_profile_delivery",
        "returncode": 0,
        "compile_json": "compile.json",
        "summary": {
            "parsed_ok": True,
            "rough_score": 0.9,
            "risk_count": 2,
            "candidate_predicates": 12,
            "compile_admitted": 30,
            "compile_skipped": 0,
            "profile_delivery_flags": [
                "status_state_carrier_offered_but_undelivered:source=2:offered=status_state_at/4"
            ],
        },
    }

    gate = _quality_gate_result(result, min_rough_score=0.775, max_risk_count=5)

    assert gate["passed"] is False
    assert gate["decision"] == "hold"
    assert gate["reasons"] == [
        "profile_delivery:status_state_carrier_offered_but_undelivered:source=2:offered=status_state_at/4"
    ]


def test_compile_quality_gate_holds_profile_schema_contract_flag() -> None:
    result = {
        "fixture": "fixture_profile_schema",
        "returncode": 0,
        "compile_json": "compile.json",
        "summary": {
            "parsed_ok": True,
            "rough_score": 0.9,
            "risk_count": 2,
            "candidate_predicates": 12,
            "compile_admitted": 30,
            "compile_skipped": 0,
            "profile_schema_contract_flags": [
                "candidate_signature_arg_mismatch:record_action/4:args=3"
            ],
        },
    }

    gate = _quality_gate_result(result, min_rough_score=0.775, max_risk_count=5)

    assert gate["passed"] is False
    assert gate["decision"] == "hold"
    assert gate["reasons"] == [
        "profile_schema_contract:candidate_signature_arg_mismatch:record_action/4:args=3"
    ]


def test_quality_retry_context_includes_profile_signature_arity_mismatch() -> None:
    lines = _quality_retry_context_lines(
        {
            "reasons": [
                "profile_schema_contract:candidate_signature_arg_mismatch:record_action/4:args=3"
            ]
        }
    )

    assert any("signature's arity equal its short schema role list" in line for line in lines)


def test_quality_retry_context_includes_repeated_structure_profile_defects() -> None:
    lines = _quality_retry_context_lines(
        {
            "reasons": [
                "profile_schema_contract:repeated_structure_id_only_record:record/1",
                "profile_schema_contract:repeated_structure_role_mismatch:record_status/2",
                "profile_schema_contract:frontier_unknown_positive_predicate:record_status/3",
            ]
        }
    )

    assert any("id-only repeated-structure record predicate" in line for line in lines)
    assert any("first argument was not a record id" in line for line in lines)
    assert any("global lookup predicates" in line for line in lines)
    assert any("expected_boundary used a positive" in line for line in lines)


def test_quality_retry_context_includes_violation_category_slot_loss() -> None:
    lines = _quality_retry_context_lines(
        {
            "reasons": [
                "profile_schema_contract:violation_category_slot_loss:admitted_failure/2",
            ]
        }
    )

    assert any("category-capable carrier" in line for line in lines)
    assert any("legal-basis rows, obligation rows, and violation/deficiency/finding" in line for line in lines)


def test_quality_retry_context_includes_list_range_inventory_slot_loss() -> None:
    lines = _quality_retry_context_lines(
        {
            "reasons": [
                "profile_schema_contract:list_range_inventory_slot_loss:claim_outcome/3",
            ]
        }
    )

    assert any("compressed range/list atom" in line for line in lines)
    assert any("Range/member boundaries must remain typed and queryable" in line for line in lines)


def test_compile_quality_gate_holds_zero_yield_compile_health() -> None:
    summary = _extract_compile_summary(
        {
            "parsed_ok": True,
            "parsed": {"candidate_predicates": [{"signature": "source_claim/3"}]},
            "source_compile": {
                "admitted_count": 30,
                "skipped_count": 0,
                "compile_health": {
                    "verdict": "poor",
                    "flag_counts": {"zero_yield": 1},
                },
                "surface_contribution": [
                    {
                        "pass_id": "pass_4",
                        "purpose": "Extract testimony and decision records.",
                        "health_flags": ["zero_yield"],
                    }
                ],
            },
            "score": {"rough_score": 1.0, "risk_count": 2},
        }
    )

    gate = _quality_gate_result(
        {"fixture": "fixture_zero_yield", "returncode": 0, "compile_json": "compile.json", "summary": summary},
        min_rough_score=0.775,
        max_risk_count=5,
    )
    lines = _quality_retry_context_lines(gate)

    assert gate["passed"] is False
    assert "compile_health:verdict=poor" in gate["reasons"]
    assert "compile_health:zero_yield=1" in gate["reasons"]
    assert any(reason.startswith("compile_health:zero_yield_pass:pass_4:") for reason in gate["reasons"])
    assert any("planned focused pass that emitted zero facts" in line for line in lines)
    assert any("testimony and decision records" in line for line in lines)


def test_quality_retry_context_lines_are_generic_for_wrapper_and_lifecycle_holds() -> None:
    lines = _quality_retry_context_lines(
        {
            "reasons": [
                "detail_wrapper_drift:location_backbone_missing_with_wrapper:source_detail",
                "compile_surface_contract:operational_lifecycle_preservation:ledger_only:source=2:direct=0",
                "compile_surface_contract:source_authority_pair_preservation:ledger_only:source=1:direct=0",
                "profile_delivery:status_state_carrier_offered_but_undelivered:source=2:offered=status_state_at/4",
            ]
        }
    )

    assert any("missing location backbone surface" in line for line in lines)
    assert any("complete direct lifecycle units" in line for line in lines)
    assert any("direct source-authority surface" in line for line in lines)
    assert any("direct status/state carrier" in line for line in lines)
    joined = "\n".join(lines).casefold()
    assert "fixture" not in joined
    assert "source_detail, event, context, note, or summary row is additive only" in joined
    assert "rule description, note, docket text, or source_record row is additive only" in joined
    assert "every distinct stated authority coordinate" in joined


def test_quality_retry_context_includes_scheduled_due_date_contract() -> None:
    lines = _quality_retry_context_lines(
        {
            "reasons": [
                "compile_surface_contract:scheduled_maintenance_due_date_preservation:ledger_only:source=1:direct=0"
            ]
        }
    )

    assert any("scheduled calibration" in line for line in lines)
    assert any("subject/device, event type, due date, and source/basis" in line for line in lines)
    joined = "\n".join(lines).casefold()
    assert "source_record row, sensor id, or ticket reference is additive only" in joined


def test_quality_retry_context_names_source_claim_backbone_coexistence() -> None:
    lines = _quality_retry_context_lines(
        {
            "reasons": [
                "profile_delivery:source_claim_backbone_coexistence_missing:source=6:offered=source_attributed_claim/4:missing=vote,survey_measurement,permit_application_status"
            ]
        }
    )

    joined = "\n".join(lines).casefold()
    assert "source-attributed claim rows while losing" in joined
    assert "vote, survey_measurement, permit_application_status" in joined
    assert "source_attributed_claim/4 rows additive" in joined
    assert "source_detail/note/context rows do not replace" in joined


def test_quality_retry_context_names_vote_tally_missing_keys() -> None:
    lines = _quality_retry_context_lines(
        {
            "reasons": [
                "profile_delivery:vote_tally_carrier_partially_delivered:source=3:offered=vote_tally/5:missing=proceed:3_2,approved:3_1,correction:4_1_to_3_1"
            ]
        }
    )

    joined = "\n".join(lines).casefold()
    assert "missed stated vote tallies" in joined
    assert "proceed:3_2, approved:3_1, correction:4_1_to_3_1" in joined
    assert "individual member vote rows" in joined


def test_compile_batch_quality_gate_renders_markdown() -> None:
    summary = _summarize(
        [
            {
                "fixture": "fixture_a",
                "returncode": 0,
                "compile_json": "a.json",
                "summary": {
                    "parsed_ok": True,
                    "rough_score": 0.9,
                    "risk_count": 2,
                    "candidate_predicates": 10,
                    "compile_admitted": 20,
                    "compile_skipped": 0,
                },
            },
            {
                "fixture": "fixture_b",
                "returncode": 0,
                "compile_json": "b.json",
                "summary": {
                    "parsed_ok": True,
                    "rough_score": 0.7,
                    "risk_count": 2,
                    "candidate_predicates": 10,
                    "compile_admitted": 20,
                    "compile_skipped": 0,
                },
            },
        ],
        lanes=2,
        base_timeout=900,
        effective_timeout=1800,
        quality_gate=True,
        quality_min_rough_score=0.775,
        quality_max_risk_count=5,
    )

    assert summary["quality_gate"]["passed"] is False
    assert summary["quality_gate"]["hold_count"] == 1
    markdown = _render_md(summary)
    assert "## Compile Quality Gate" in markdown
    assert "rough_score<0.775" in markdown
