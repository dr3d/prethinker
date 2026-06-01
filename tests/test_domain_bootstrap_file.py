from scripts.run_domain_bootstrap_file import (
    COMPETITION_ROLE_ALIAS_CONTEXT_V1,
    COMPILE_SURFACE_INVARIANT_CONTEXT_V1,
    FINANCIAL_REPORT_SOURCE_COMPILER_CONTEXT_V1,
    FICTION_REFERENCE_CONTAINMENT_CONTEXT_V1,
    NARRATIVE_SOURCE_COMPILER_CONTEXT_V1,
    OPERATIONAL_RECORD_STATUS_CONTEXT_V1,
    PROBATE_PROPERTY_STATUS_CONTEXT_V1,
    PROFILE_SIGNATURE_ROSTER_JSON_SCHEMA,
    RULE_INGESTION_SOURCE_COMPILER_CONTEXT_V1,
    SOURCE_AUTHORITY_AUDIT_CONTEXT_V1,
    SOURCE_ENTITY_LEDGER_SCHEMA,
    SOURCE_PASS_OPS_JSON_SCHEMA,
    _append_entity_id_closure_facts,
    _append_source_field_id_facts,
    _append_source_record_ledger_facts,
    _call_lmstudio_json_schema,
    _compile_health_summary,
    _compile_source_pass_ops,
    _compile_source_with_plan_passes,
    _ensure_appeal_filing_predicate,
    _ensure_document_checkbox_provision_predicate,
    _ensure_document_identifier_occurrence_predicate,
    _ensure_document_metadata_predicates,
    _ensure_entity_location_predicate,
    _ensure_legal_citation_detail_predicate,
    _ensure_list_range_inventory_predicates,
    _ensure_rating_scale_option_predicate,
    _ensure_monetary_payment_predicate,
    _ensure_obligation_detail_predicate,
    _ensure_procedural_rule_detail_predicate,
    _ensure_event_date_predicate,
    _ensure_quantity_event_predicate,
    _ensure_quorum_status_predicate,
    _ensure_repeated_structure_predicates,
    _ensure_role_detail_predicate,
    _ensure_scheduled_event_predicate,
    _ensure_source_attributed_claim_predicate,
    _ensure_source_authority_predicate,
    _ensure_source_detail_predicate,
    _ensure_status_state_predicate,
    _ensure_vote_tally_predicate,
    _source_pass_predicate_contract_guidance,
    _profile_admission_report,
    _profile_admission_retry_context,
    _attach_profile_admission_report,
    _flat_plus_surface_contribution,
    _profile_bootstrap_admission_context,
    _chat_headers,
    _default_openrouter_title,
    _invalid_profile_retry_context,
    _profile_schema_contract_retry_context,
    _profile_schema_contract_retry_needed,
    _profile_list_range_inventory_repair_context_lines,
    _profile_list_range_inventory_repair_offered_carriers,
    _profile_list_range_inventory_offered_omission_rows,
    _profile_list_range_inventory_omission_context,
    _profile_rating_scale_repair_context_lines,
    _profile_rating_scale_repair_offered_carriers,
    _document_date_repair_context_lines,
    _profile_document_date_repair_offered_carriers,
    _profile_governed_subject_discovery_context_lines,
    _profile_governed_subject_discovery_offered_carriers,
    _facts_from_governed_subject_atom_rows,
    _facts_from_governed_subject_manifest,
    _replace_governed_subject_atom_row_facts,
    _profile_legal_citation_repair_context_lines,
    _profile_legal_citation_repair_offered_carriers,
    _profile_monetary_payment_repair_context_lines,
    _profile_monetary_payment_repair_offered_carriers,
    _review_outcome_repair_context_lines,
    _profile_review_outcome_repair_offered_carriers,
    _registered_carrier_omission_context_lines,
    _legal_citation_repair_preferred_subject_ids,
    _enforce_legal_citation_repair_subject_contract,
    _enforce_additive_pass_allowed_signatures,
    _reconcile_profile_carrier_contracts,
    _enforce_list_range_inventory_fact_contract,
    _apply_document_subject_atom_convergence,
    _apply_governed_claim_ground_atom_reduction,
    _apply_governed_obligation_detail_atom_reduction,
    _apply_governed_reference_citation_atom_reduction,
    _apply_governed_review_atom_fact_reduction,
    _attach_governed_companion_subject_health,
    _attach_registered_carrier_delivery_report,
    _lmstudio_chat_completions_url,
    _pass_surface_contribution,
    _profile_from_signature_roster,
    _profile_registry_for_lens,
    _profile_registry_palette_report,
    _profile_registry_palette_prior_context,
    _profile_registry_accountability_context,
    _profile_registry_completion_context_lines,
    _apply_profile_registry_completion_followup_pass,
    _profile_registry_accountability_followup_context_lines,
    _apply_profile_registry_accountability_followup_pass,
    _apply_domain_omission_carrier_signature_reduction,
    _apply_fda_warning_letter_subject_convergence,
    _apply_fda_date_atom_reduction,
    _apply_fda_facility_subject_convergence,
    _apply_fda_lot_identifier_atom_reduction,
    _apply_fda_facility_identity_atom_reduction,
    _apply_fda_consultant_citation_scope_reduction,
    _apply_fda_office_atom_reduction,
    _apply_fda_violation_detail_subject_integrity,
    _apply_fda_violation_number_atom_reduction,
    _enforce_fda_correspondence_party_placeholder_contract,
    _unsafe_profile_registry_palette_prior_reason,
    _should_build_source_entity_ledger,
    _source_compiler_context,
    _source_entity_ledger_context,
    _source_pass_profile_delivery_target_context,
    _source_pass_ops_to_semantic_ir,
    _source_pass_self_check_missing_slots,
    _list_range_inventory_existing_fact_context,
)
import scripts.run_domain_bootstrap_file as domain_bootstrap_file
import json
from pathlib import Path


def test_narrative_context_guards_attributes_and_official_duties() -> None:
    context = "\n".join(NARRATIVE_SOURCE_COMPILER_CONTEXT_V1)

    assert "numeric ages" in context
    assert "not encode numeric ages or duties as names or aliases" in context
    assert "official inspects, certifies, authorizes, investigates, or decides" in context
    assert "preserve each named resident separately" in context
    assert "errand/distraction" in context
    assert "choice-by-contrast" in context
    assert "comic-consequence" in context
    assert "explicit-moral" in context


def test_financial_report_context_preserves_named_contributions() -> None:
    context = "\n".join(FINANCIAL_REPORT_SOURCE_COMPILER_CONTEXT_V1)

    assert "financial_report_source_compiler_strategy_v1" in context
    assert "named affiliate, associate, investee, subsidiary, segment" in context
    assert "metric, value, and unit" in context
    assert "financial_result/5" in context
    assert "five-slot maximum" in context
    assert "Do not invent /6 financial predicates" in context
    assert "source-contained ratios" in context


def test_source_detail_profile_extension_is_additive_fallback_only() -> None:
    profile = {
        "candidate_predicates": [
            {
                "signature": "item_id/1",
                "args": ["item_id"],
                "description": "Item identifier.",
                "why": "Keeps item ids queryable.",
                "admission_notes": [],
            }
        ],
        "provenance_sensitive_predicates": [],
        "self_check": {"notes": []},
    }

    metadata = _ensure_source_detail_predicate(profile)

    assert metadata["added"] is True
    assert any(item["signature"] == "source_detail/4" for item in profile["candidate_predicates"])
    assert "source_detail/4" in profile["provenance_sensitive_predicates"]


def test_source_detail_profile_extension_respects_specific_detail_carrier() -> None:
    profile = {
        "candidate_predicates": [
            {
                "signature": "device_attribute/3",
                "args": ["device_id", "attribute_kind", "attribute_value"],
                "description": "Device attribute.",
                "why": "Keeps device attributes queryable.",
                "admission_notes": [],
            }
        ],
    }

    metadata = _ensure_source_detail_predicate(profile)

    assert metadata == {
        "schema_version": "profile_source_detail_extension_v1",
        "added": False,
        "reason": "specific_detail_carrier_present",
    }


def test_role_detail_profile_extension_adds_carrier_for_shallow_roles() -> None:
    profile = {
        "candidate_predicates": [
            {
                "signature": "party_role/3",
                "args": ["person", "role", "organization"],
            }
        ],
        "provenance_sensitive_predicates": [],
        "self_check": {"notes": []},
    }

    metadata = _ensure_role_detail_predicate(profile)

    assert metadata["added"] is True
    assert metadata["signature"] == "person_role_detail/5"
    carrier = next(item for item in profile["candidate_predicates"] if item["signature"] == "person_role_detail/5")
    assert carrier["args"] == [
        "person_id",
        "role_or_title",
        "organization_or_office",
        "represented_party_or_scope",
        "location_or_context",
    ]
    assert "person_role_detail/5" in profile["provenance_sensitive_predicates"]


def test_role_detail_profile_extension_respects_rich_role_carrier() -> None:
    profile = {
        "candidate_predicates": [
            {"signature": "counsel_for/5", "args": ["proceeding", "person", "office", "party", "location"]},
            {"signature": "party_role/3", "args": ["person", "role", "organization"]},
        ]
    }

    assert _ensure_role_detail_predicate(profile) == {
        "schema_version": "profile_role_detail_extension_v1",
        "added": False,
        "reason": "rich_role_carrier_present",
    }


def test_document_metadata_profile_extension_adds_general_carriers() -> None:
    profile = {
        "candidate_predicates": [
            {"signature": "decision_date/2", "args": ["case", "date"]},
        ],
        "provenance_sensitive_predicates": [],
        "self_check": {"notes": []},
    }

    metadata = _ensure_document_metadata_predicates(profile)

    assert metadata["added"] is True
    assert metadata["signatures"] == [
        "document_title/2",
        "document_publisher/2",
        "document_date/3",
        "document_date_range/3",
        "registrant_identity/2",
        "registrant_name/2",
    ]
    signatures = {item["signature"] for item in profile["candidate_predicates"]}
    assert "document_title/2" in signatures
    assert "document_publisher/2" in signatures
    assert "document_date/3" in signatures
    assert "document_date_range/3" in signatures
    assert "registrant_identity/2" in signatures
    assert "registrant_name/2" in signatures
    registrant = next(item for item in profile["candidate_predicates"] if item["signature"] == "registrant_identity/2")
    assert registrant["args"] == ["registrant_entity", "incorporation_or_organization_jurisdiction"]
    assert "not a current status" in " ".join(registrant["admission_notes"])
    name = next(item for item in profile["candidate_predicates"] if item["signature"] == "registrant_name/2")
    assert name["args"] == ["registrant_entity", "legal_name"]
    assert "not a ticker" in " ".join(name["admission_notes"])
    assert "document_title/2" in profile["provenance_sensitive_predicates"]


def test_document_metadata_profile_extension_is_idempotent() -> None:
    profile = {
        "candidate_predicates": [
            {"signature": "document_title/2", "args": ["document_id", "title"]},
            {"signature": "document_publisher/2", "args": ["document_id", "publisher_or_issuing_body"]},
            {"signature": "document_date/3", "args": ["document_or_subject_id", "date_kind_or_role", "date_value"]},
            {"signature": "document_date_range/3", "args": ["document_id", "start_date", "end_date"]},
            {
                "signature": "registrant_identity/2",
                "args": ["registrant_entity", "incorporation_or_organization_jurisdiction"],
            },
            {"signature": "registrant_name/2", "args": ["registrant_entity", "legal_name"]},
        ],
    }

    metadata = _ensure_document_metadata_predicates(profile)

    assert metadata["added"] is False
    assert metadata["signatures"] == []
    assert len(profile["candidate_predicates"]) == 6


def test_legal_citation_detail_profile_extension_adds_exact_citation_carrier() -> None:
    profile = {
        "candidate_predicates": [
            {"signature": "obligation_statute/2", "args": ["obligation", "statute"]},
        ],
        "provenance_sensitive_predicates": [],
        "self_check": {"notes": []},
    }

    metadata = _ensure_legal_citation_detail_predicate(profile)

    assert metadata["added"] is True
    assert metadata["signature"] == "legal_citation_detail/4"
    carrier = next(item for item in profile["candidate_predicates"] if item["signature"] == "legal_citation_detail/4")
    assert carrier["args"] == ["subject_id", "citation", "citation_role_or_purpose", "source_or_scope"]
    assert "Named procedural rule sets" in " ".join(carrier["admission_notes"])
    assert "legal_citation_detail/4" in profile["provenance_sensitive_predicates"]


def test_legal_citation_detail_profile_extension_is_idempotent() -> None:
    profile = {
        "candidate_predicates": [
            {
                "signature": "legal_citation_detail/4",
                "args": ["subject_id", "citation", "citation_role_or_purpose", "source_or_scope"],
            }
        ],
    }

    assert _ensure_legal_citation_detail_predicate(profile) == {
        "schema_version": "profile_legal_citation_detail_extension_v1",
        "added": False,
        "reason": "legal_citation_detail_already_present",
    }


def test_monetary_payment_profile_extension_adds_exact_amount_carrier() -> None:
    profile = {
        "candidate_predicates": [],
        "provenance_sensitive_predicates": [],
        "self_check": {"notes": []},
    }

    metadata = _ensure_monetary_payment_predicate(profile)

    assert metadata["added"] is True
    assert metadata["signature"] == "monetary_payment/5"
    carrier = next(item for item in profile["candidate_predicates"] if item["signature"] == "monetary_payment/5")
    assert carrier["args"] == ["subject_id", "amount", "authority_or_basis", "purpose_or_use", "source_or_scope"]
    assert "Use compact amount atoms such as usd_725000" in " ".join(carrier["admission_notes"])
    assert "monetary_payment/5" in profile["provenance_sensitive_predicates"]


def test_obligation_detail_profile_extension_adds_compact_term_carrier() -> None:
    profile = {
        "candidate_predicates": [
            {"signature": "settlement_obligation/3", "args": ["obligation_id", "type", "description"]},
        ],
        "provenance_sensitive_predicates": [],
        "self_check": {"notes": []},
    }

    metadata = _ensure_obligation_detail_predicate(profile)

    assert metadata["added"] is True
    assert metadata["signature"] == "obligation_detail/5"
    assert metadata["source_pressure"] is True
    assert metadata["accountability_required"] is True
    carrier = next(item for item in profile["candidate_predicates"] if item["signature"] == "obligation_detail/5")
    assert carrier["args"] == ["obligation_id", "detail_kind", "detail_value", "role_or_purpose", "source_or_scope"]
    assert "Use one obligation_detail/5 row per atomic" in " ".join(carrier["admission_notes"])
    assert "obligation_detail/5" in profile["provenance_sensitive_predicates"]
    assert any("obligation_detail/5" in note for note in profile["self_check"]["notes"])


def test_procedural_rule_detail_profile_extension_adds_compact_rule_carrier() -> None:
    profile = {
        "candidate_predicates": [
            {
                "signature": "review_deadline/3",
                "args": ["deadline_id", "review_or_rehearing_request", "period"],
            }
        ],
        "provenance_sensitive_predicates": [],
        "self_check": {"notes": []},
    }

    metadata = _ensure_procedural_rule_detail_predicate(profile)

    assert metadata["added"] is True
    assert metadata["signature"] == "procedural_rule_detail/5"
    assert metadata["source_pressure"] is True
    assert metadata["accountability_required"] is True
    carrier = next(item for item in profile["candidate_predicates"] if item["signature"] == "procedural_rule_detail/5")
    assert carrier["args"] == ["rule_id", "detail_kind", "detail_value", "rule_context_or_action", "source_or_scope"]
    assert "Use one procedural_rule_detail/5 row per atomic" in " ".join(carrier["admission_notes"])
    assert "procedural_rule_detail/5" in profile["provenance_sensitive_predicates"]


def test_registered_carrier_delivery_flags_extension_carrier_without_rows() -> None:
    source_compile = {
        "unique_fact_count": 1,
        "facts": ["settlement_obligation(obligation_1, data_reporting, broad_summary)."],
        "compile_health": {
            "schema_version": "compile_lens_health_v1",
            "verdict": "healthy",
            "recommendation": "qa_run_reasonable",
            "pass_count": 1,
            "unhealthy_pass_count": 0,
            "unhealthy_passes": [],
            "flag_counts": {},
            "unique_contribution_total": 1,
            "duplicate_total": 0,
            "semantic_progress": {"zombie_risk": "low", "recommended_action": "continue"},
        },
    }
    profile = {
        "candidate_predicates": [
            {
                "signature": "obligation_detail/5",
                "args": ["obligation_id", "detail_kind", "detail_value", "role_or_purpose", "source_or_scope"],
            }
        ]
    }

    report = _attach_registered_carrier_delivery_report(
        source_compile=source_compile,
        parsed_profile=profile,
        profile_extension_metadata={
            "extensions": [
                {"added": True, "signature": "obligation_detail/5", "source_pressure": True},
            ]
        },
    )

    assert report["not_source_interpretation"] is True
    assert report["offered_signatures"] == ["obligation_detail/5"]
    assert report["accountable_signatures"] == ["obligation_detail/5"]
    assert report["findings"] == [
        {
            "class": "registered_carrier_offered_but_undelivered",
            "signature": "obligation_detail/5",
            "delivered_carrier_row_count": 0,
            "reason": (
                "registered carrier signature was offered by profile extension metadata but no typed rows "
                "were emitted"
            ),
        }
    ]
    assert source_compile["compile_health"]["flag_counts"]["registered_carrier_offered_but_undelivered"] == 1
    assert "registered_carrier_delivery" in source_compile["compile_health"]["unhealthy_passes"]


def test_registered_carrier_delivery_accepts_extension_carrier_rows() -> None:
    source_compile = {
        "facts": [
            "obligation_detail(obligation_1, tariff_schedule, schedule_9, data_reporting, source_line_13).",
            "obligation_detail(obligation_1, duration, one_year, data_reporting, source_line_13).",
        ],
        "compile_health": {
            "schema_version": "compile_lens_health_v1",
            "verdict": "healthy",
            "recommendation": "qa_run_reasonable",
            "pass_count": 1,
            "unhealthy_pass_count": 0,
            "unhealthy_passes": [],
            "flag_counts": {},
            "unique_contribution_total": 2,
            "duplicate_total": 0,
            "semantic_progress": {"zombie_risk": "low", "recommended_action": "continue"},
        },
    }
    profile = {
        "candidate_predicates": [
            {
                "signature": "obligation_detail/5",
                "args": ["obligation_id", "detail_kind", "detail_value", "role_or_purpose", "source_or_scope"],
            }
        ]
    }

    report = _attach_registered_carrier_delivery_report(
        source_compile=source_compile,
        parsed_profile=profile,
        profile_extension_metadata={
            "extensions": [
                {"added": True, "signature": "obligation_detail/5", "source_pressure": True},
            ]
        },
    )

    assert report["delivered_row_counts"]["obligation_detail/5"] == 2
    assert report["findings"] == []
    assert source_compile["compile_health"]["verdict"] == "healthy"


def test_registered_carrier_delivery_keeps_non_accountable_extensions_report_only() -> None:
    source_compile = {
        "facts": [],
        "compile_health": {
            "schema_version": "compile_lens_health_v1",
            "verdict": "healthy",
            "recommendation": "qa_run_reasonable",
            "pass_count": 1,
            "unhealthy_pass_count": 0,
            "unhealthy_passes": [],
            "flag_counts": {},
            "unique_contribution_total": 0,
            "duplicate_total": 0,
            "semantic_progress": {"zombie_risk": "low", "recommended_action": "continue"},
        },
    }
    profile = {
        "candidate_predicates": [
            {
                "signature": "document_checkbox_provision/5",
                "args": ["document_id", "provision_label", "checkbox_state", "rule_label", "citation"],
            }
        ]
    }

    report = _attach_registered_carrier_delivery_report(
        source_compile=source_compile,
        parsed_profile=profile,
        profile_extension_metadata={
            "extensions": [
                {"added": True, "signature": "document_checkbox_provision/5"},
            ]
        },
    )

    assert report["offered_signatures"] == ["document_checkbox_provision/5"]
    assert report["accountable_signatures"] == []
    assert report["findings"] == []
    assert source_compile["compile_health"]["verdict"] == "healthy"


def test_registered_carrier_omission_context_uses_contract_registry() -> None:
    lines = _registered_carrier_omission_context_lines(
        {
            "findings": [
                {
                    "class": "registered_carrier_offered_but_undelivered",
                    "signature": "obligation_detail/5",
                }
            ]
        }
    )

    joined = "\n".join(lines)
    assert "REGISTERED CARRIER OMISSION FOLLOWUP" in joined
    assert "obligation_detail/5" in joined
    assert "Emit one row per atomic detail" in joined
    assert "do not emit prose excerpts" in joined


def test_registered_carrier_omission_followup_merges_allowed_rows(monkeypatch) -> None:
    source_compile = {
        "admitted_count": 1,
        "skipped_count": 0,
        "effective_admitted_count": 1,
        "effective_skipped_count": 0,
        "facts": ["document_title(doc_1, title_atom)."],
        "rules": [],
        "queries": [],
        "surface_contribution": [],
        "compile_health": {
            "schema_version": "compile_lens_health_v1",
            "verdict": "healthy",
            "recommendation": "qa_run_reasonable",
            "pass_count": 0,
            "unhealthy_pass_count": 0,
            "unhealthy_passes": [],
            "flag_counts": {},
            "unique_contribution_total": 1,
            "duplicate_total": 0,
            "semantic_progress": {"zombie_risk": "low", "recommended_action": "continue"},
        },
    }
    profile = {
        "candidate_predicates": [
            {
                "signature": "obligation_detail/5",
                "args": ["obligation_id", "detail_kind", "detail_value", "role_or_purpose", "source_or_scope"],
            }
        ]
    }
    metadata = {"extensions": [{"added": True, "signature": "obligation_detail/5", "source_pressure": True}]}
    initial = domain_bootstrap_file._attach_registered_carrier_delivery_report(
        source_compile=source_compile,
        parsed_profile=profile,
        profile_extension_metadata=metadata,
        mark_health=False,
    )

    def fake_compile_source_pass_ops(**kwargs):
        assert kwargs["pass_id"] == "profile_registered_carrier_omission_followup"
        assert kwargs["predicates"] == "obligation_detail/5"
        return {
            "ok": True,
            "admitted_count": 2,
            "skipped_count": 1,
            "facts": [
                "obligation_detail(obligation_1, tariff_schedule, schedule_9, data_reporting, source_line_13).",
                "unregistered_escape(obligation_1, source_sentence).",
            ],
            "rules": [],
            "queries": [],
        }

    monkeypatch.setattr(domain_bootstrap_file, "_compile_source_pass_ops", fake_compile_source_pass_ops)

    result = domain_bootstrap_file._apply_profile_registered_carrier_omission_followup_pass(
        source_compile=source_compile,
        parsed_profile=profile,
        source_text="RMP agreed to provide data under Schedule 9.",
        intake_plan={},
        args=type("Args", (), {"focused_pass_operation_target": 8})(),
        profile_extension_metadata=metadata,
        registered_delivery_report=initial,
    )

    assert result["attempted"] is True
    assert result["new_fact_count"] == 1
    assert result["signature_contract"]["rejected_count"] == 1
    assert source_compile["facts"] == [
        "document_title(doc_1, title_atom).",
        "obligation_detail(obligation_1, tariff_schedule, schedule_9, data_reporting, source_line_13).",
    ]
    assert source_compile["registered_carrier_delivery"]["findings"] == []


def test_monetary_payment_repair_context_uses_typed_payment_and_citation_facts() -> None:
    profile = {
        "candidate_predicates": [
            {
                "signature": "monetary_payment/5",
                "args": ["subject_id", "amount", "authority_or_basis", "purpose_or_use", "source_or_scope"],
            },
            {"signature": "payment_amount/2", "args": ["obligation_id", "amount"]},
        ]
    }
    source_compile = {
        "facts": [
            "obligation(obligation_payment, payment_of_725_000_to_the_state_of_new_york).",
            "payment_amount(obligation_payment, 725000_usd).",
            "obligation_enforces(obligation_payment, gbl_349_d).",
            "legal_citation_detail(eq_ny_ag_24_102_monetary_relief, gbl_349_d, statutory_ground, direct).",
            "source_record_text(row_15, 'pay $725,000 pursuant to GBL').",
        ]
    }

    assert _profile_monetary_payment_repair_offered_carriers(profile) == ["monetary_payment/5"]
    lines = _profile_monetary_payment_repair_context_lines(
        parsed_profile=profile,
        source_compile=source_compile,
    )
    context = "\n".join(lines)

    assert "PROFILE MONETARY PAYMENT REPAIR PASS" in context
    assert "monetary_payment/5" in context
    assert "EXISTING MONETARY FACT: payment_amount(obligation_payment, 725000_usd)." in context
    assert "EXISTING MONETARY FACT: obligation_enforces(obligation_payment, gbl_349_d)." in context
    assert "source_record_text" not in context
    assert "subject_id, amount, authority_or_basis, purpose_or_use, source_or_scope" in context


def test_document_checkbox_profile_extension_adds_general_carrier() -> None:
    profile = {
        "candidate_predicates": [
            {"signature": "document_identifier/3", "args": ["document_id", "identifier_kind", "value"]},
        ],
        "provenance_sensitive_predicates": [],
        "self_check": {"notes": []},
    }

    metadata = _ensure_document_checkbox_provision_predicate(profile)

    assert metadata["added"] is True
    assert metadata["signature"] == "document_checkbox_provision/5"
    carrier = next(item for item in profile["candidate_predicates"] if item["signature"] == "document_checkbox_provision/5")
    assert carrier["args"] == ["document_id", "provision_label_or_text", "checkbox_mark", "rule_or_provision", "citation"]
    assert "one row per checkbox/list provision" in " ".join(carrier["admission_notes"])
    assert "document_checkbox_provision/5" in profile["provenance_sensitive_predicates"]


def test_document_checkbox_profile_extension_is_idempotent() -> None:
    profile = {
        "candidate_predicates": [
            {
                "signature": "document_checkbox_provision/5",
                "args": ["document_id", "provision_label_or_text", "checkbox_mark", "rule_or_provision", "citation"],
            }
        ],
    }

    assert _ensure_document_checkbox_provision_predicate(profile) == {
        "schema_version": "profile_document_checkbox_provision_extension_v1",
        "added": False,
        "reason": "document_checkbox_provision_already_present",
    }


def test_document_identifier_occurrence_profile_extension_adds_general_carrier() -> None:
    profile = {
        "candidate_predicates": [
            {"signature": "document_identifier/3", "args": ["document_id", "identifier_kind", "value"]},
        ],
        "provenance_sensitive_predicates": [],
        "self_check": {"notes": []},
    }

    metadata = _ensure_document_identifier_occurrence_predicate(profile)

    assert metadata["added"] is True
    assert metadata["signature"] == "document_identifier_occurrence/5"
    carrier = next(item for item in profile["candidate_predicates"] if item["signature"] == "document_identifier_occurrence/5")
    assert carrier["args"] == [
        "document_id",
        "identifier_kind",
        "identifier_value",
        "occurrence_scope_or_label",
        "source_order",
    ]
    assert "Do not collapse distinct values" in " ".join(carrier["admission_notes"])
    assert "document_identifier_occurrence/5" in profile["provenance_sensitive_predicates"]


def test_document_identifier_occurrence_profile_extension_is_idempotent() -> None:
    profile = {
        "candidate_predicates": [
            {
                "signature": "document_identifier_occurrence/5",
                "args": [
                    "document_id",
                    "identifier_kind",
                    "identifier_value",
                    "occurrence_scope_or_label",
                    "source_order",
                ],
            }
        ],
    }

    assert _ensure_document_identifier_occurrence_predicate(profile) == {
        "schema_version": "profile_document_identifier_occurrence_extension_v1",
        "added": False,
        "reason": "document_identifier_occurrence_already_present",
    }


def test_list_range_inventory_profile_extension_adds_general_carriers() -> None:
    profile = {
        "candidate_predicates": [
            {"signature": "claim_outcome/3", "args": ["claim_set_id", "ground", "outcome"]},
        ],
        "provenance_sensitive_predicates": [],
        "self_check": {"notes": []},
    }

    metadata = _ensure_list_range_inventory_predicates(profile)

    assert metadata["added"] is True
    assert metadata["signatures"] == ["list_member/4", "claim_range/4", "item_range/4", "claim_ground/4", "review_outcome/4"]
    signatures = {item["signature"] for item in profile["candidate_predicates"]}
    assert "list_member/4" in signatures
    assert "claim_range/4" in signatures
    assert "item_range/4" in signatures
    assert "claim_ground/4" in signatures
    assert "review_outcome/4" in signatures
    claim_range = next(item for item in profile["candidate_predicates"] if item["signature"] == "claim_range/4")
    assert claim_range["args"] == ["claim_set_id", "start_claim", "end_claim", "source_or_scope"]
    assert "source-stated segment" in " ".join(claim_range["admission_notes"])
    list_member = next(item for item in profile["candidate_predicates"] if item["signature"] == "list_member/4")
    list_member_notes = " ".join(list_member["admission_notes"])
    assert "Do not use source_or_scope to encode a legal ground" in list_member_notes
    assert "companion typed relation" in list_member_notes
    assert "claim_range/4" in profile["provenance_sensitive_predicates"]
    assert "claim_ground/4" in profile["provenance_sensitive_predicates"]
    assert "review_outcome/4" in profile["provenance_sensitive_predicates"]


def test_list_range_inventory_profile_extension_is_idempotent() -> None:
    profile = {
        "candidate_predicates": [
            {"signature": "list_member/4", "args": ["list_or_set_id", "member_value", "member_kind_or_role", "source_or_scope"]},
            {"signature": "claim_range/4", "args": ["claim_set_id", "start_claim", "end_claim", "source_or_scope"]},
            {"signature": "item_range/4", "args": ["item_set_id", "start_item", "end_item", "source_or_scope"]},
        ],
    }

    metadata = _ensure_list_range_inventory_predicates(profile)

    assert metadata["added"] is False
    assert metadata["signatures"] == []
    assert len(profile["candidate_predicates"]) == 3


def test_list_range_inventory_profile_extension_does_not_add_claim_ground_without_ground_signal() -> None:
    profile = {
        "candidate_predicates": [
            {"signature": "item_range/4", "args": ["item_set_id", "start_item", "end_item", "source_or_scope"]},
        ],
        "provenance_sensitive_predicates": [],
    }

    metadata = _ensure_list_range_inventory_predicates(profile)

    assert "claim_ground/4" not in metadata["signatures"]
    assert not any(item["signature"] == "claim_ground/4" for item in profile["candidate_predicates"])


def test_rating_scale_profile_extension_adds_option_carrier_from_rating_profile_signal() -> None:
    profile = {
        "candidate_predicates": [
            {
                "signature": "assigned_rating/3",
                "args": ["offeror_name", "factor_name", "rating"],
                "description": "Adjectival rating assigned to an offeror for a factor.",
                "why": "Captures assigned ratings.",
                "admission_notes": ["Use for specific ratings assigned to offerors."],
            }
        ],
        "provenance_sensitive_predicates": [],
        "self_check": {"notes": []},
    }

    metadata = _ensure_rating_scale_option_predicate(profile)

    assert metadata == {
        "schema_version": "profile_rating_scale_extension_v1",
        "added": True,
        "signatures": ["rating_scale_option/4"],
        "authority": "vocabulary_extension_only",
        "fact_extraction": False,
    }
    assert profile["candidate_predicates"][-1]["signature"] == "rating_scale_option/4"
    assert "rating_scale_option/4" in profile["provenance_sensitive_predicates"]


def test_rating_scale_profile_extension_requires_rating_signal() -> None:
    profile = {"candidate_predicates": [{"signature": "document_date/3", "args": []}]}

    assert _ensure_rating_scale_option_predicate(profile) == {
        "schema_version": "profile_rating_scale_extension_v1",
        "added": False,
        "reason": "no_rating_scale_signal",
    }


def test_rating_scale_repair_context_targets_only_rating_scale_carrier() -> None:
    profile = {
        "candidate_predicates": [
            {"signature": "rating_scale_option/4", "args": ["scale", "rating", "rank", "source"]},
            {"signature": "assigned_rating/3", "args": ["entity", "factor", "rating"]},
        ]
    }

    assert _profile_rating_scale_repair_offered_carriers(profile) == ["rating_scale_option/4"]
    text = "\n".join(_profile_rating_scale_repair_context_lines(profile))
    assert "distinguish allowed scale options from ratings assigned" in text
    assert "rating_scale_option/4" in text
    assert "compatible signatures to consider: rating_scale_option/4" in text
    assert "do not emit source_record_* rows" in text


def test_profile_carrier_contract_reconciliation_restores_registered_roles() -> None:
    profile = {
        "candidate_predicates": [
            {
                "signature": "claim_range/4",
                "args": ["proceeding_id", "claim_start", "claim_end", "claim_label"],
            },
            {
                "signature": "list_member/4",
                "args": ["set_id", "member_id", "set_label", "member_label"],
            },
        ],
        "provenance_sensitive_predicates": [],
    }

    metadata = _reconcile_profile_carrier_contracts(profile)

    assert metadata["changed_count"] == 2
    claim_range = next(item for item in profile["candidate_predicates"] if item["signature"] == "claim_range/4")
    list_member = next(item for item in profile["candidate_predicates"] if item["signature"] == "list_member/4")
    assert claim_range["args"] == ["claim_set_id", "start_claim", "end_claim", "source_or_scope"]
    assert list_member["args"] == ["list_or_set_id", "member_value", "member_kind_or_role", "source_or_scope"]
    assert "claim_range/4" in profile["provenance_sensitive_predicates"]
    assert "list_member/4" in profile["provenance_sensitive_predicates"]
    assert metadata["authority"] == "registered_carrier_contract_only"


def test_profile_schema_retry_does_not_fire_for_governed_carrier_roles_only() -> None:
    assert _profile_schema_contract_retry_needed(
        {
            "governed_carrier_arg_role_mismatch_refs": [
                "claim_range/4:args=proceeding_id,claim_start,claim_end,claim_label "
                "expected=claim_set_id,start_claim,end_claim,source_or_scope"
            ],
            "candidate_signature_arg_mismatch_refs": [],
            "candidate_duplicate_name_arity_refs": [],
            "provenance_prose_arg_role_refs": [],
            "repeated_structure_role_mismatch_refs": [],
            "list_range_inventory_slot_loss_refs": [],
        }
    ) is False


def test_list_range_inventory_repair_context_targets_only_range_carriers() -> None:
    profile = {
        "candidate_predicates": [
            {"signature": "list_member/4", "args": ["list_or_set_id", "member_value", "member_kind_or_role", "source_or_scope"]},
            {"signature": "claim_range/4", "args": ["claim_set_id", "start_claim", "end_claim", "source_or_scope"]},
            {"signature": "claim_treatment/5", "args": ["claim_set_id", "ground", "prior_art", "basis", "source"]},
            {"signature": "document_identifier/3", "args": ["document_id", "identifier_kind", "value"]},
        ]
    }

    assert _profile_list_range_inventory_repair_offered_carriers(profile) == [
        "list_member/4",
        "claim_range/4",
        "claim_treatment/5",
    ]
    text = "\n".join(_profile_list_range_inventory_repair_context_lines(profile))
    assert "source-stated singleton" in text
    assert "source-stated range segment" in text
    assert "source-stated category, class, type, option, or heading inventories" in text
    assert "period, impact, statement, effect, account, or narrative-detail predicates" in text
    assert "not satisfied by expanding" in text
    assert "set-to-relation row" in text
    assert "do not hide a legal ground" in text
    assert "CARRIER CONTRACT claim_range/4" in text
    assert "must not encode the legal ground" in text
    assert "do not emit source_record_* rows" in text
    assert "claim_range/4" in text
    assert "claim_treatment/5" in text
    assert "document_identifier/3" not in text


def test_source_pass_self_check_missing_slots_reads_nested_payload() -> None:
    assert _source_pass_self_check_missing_slots(
        {"source_pass_ops": {"self_check": {"missing_slots": [" claim_range rows ", "", "review rows"]}}}
    ) == ["claim_range rows", "review rows"]


def test_list_range_inventory_existing_fact_context_filters_typed_companions_only() -> None:
    lines = _list_range_inventory_existing_fact_context(
        {
            "facts": [
                "source_record_text_display(src1, prose).",
                "claim_range(contested_claims, 6, 9, direct).",
                "rejection_ground(contested_claims, song_525, 35_u_s_c_102_a_1, anticipated).",
                "document_identifier(no_2025_1705, docket, 2025_1705).",
            ]
        }
    )

    text = "\n".join(lines)
    assert "EXISTING LIST/RANGE FACT: claim_range(contested_claims, 6, 9, direct)." in text
    assert (
        "EXISTING LIST/RANGE FACT: rejection_ground(contested_claims, song_525, 35_u_s_c_102_a_1, anticipated)."
        in text
    )
    assert "source_record_text_display" not in text
    assert "document_identifier" not in text


def test_list_range_inventory_omission_context_uses_governed_health_rows() -> None:
    source_compile = {
        "facts": [
            "claim_ground(claims_28_37, obviousness, song_525, rejected).",
            "source_record_text_display(src1, claims_28_37_were_rejected_as_obvious).",
        ],
        "governed_companion_subject_health": {
            "governed_companion_omission_ledger": [
                {
                    "subject": "claims_28_37",
                    "signature": "claim_range/4",
                    "status": "missing_unaccounted",
                    "observed_predicates": ["claim_ground", "legal_citation_detail"],
                    "reason": "typed subject has companion families but no range",
                },
                {
                    "subject": "claims_28_37",
                    "signature": "review_outcome/4",
                    "status": "missing_unaccounted",
                    "observed_predicates": ["claim_ground"],
                },
            ]
        },
    }

    rows = _profile_list_range_inventory_offered_omission_rows(source_compile)
    assert rows == [
        {
            "subject": "claims_28_37",
            "signature": "claim_range/4",
            "observed_predicates": ["claim_ground", "legal_citation_detail"],
            "reason": "typed subject has companion families but no range",
        }
    ]
    text = "\n".join(_profile_list_range_inventory_omission_context(source_compile))
    assert "OMISSION_LEDGER_ROW subject=claims_28_37 signature=claim_range/4" in text
    assert "EXISTING LIST/RANGE FACT: claim_ground(claims_28_37, obviousness, song_525, rejected)." in text
    assert "source_record_text_display" not in text


def test_list_range_inventory_contract_rejects_same_source_range_expansion() -> None:
    source_compile = {
        "facts": [
            "list_member(count_set_1, 2, count, src_line_0003).",
            "list_member(count_set_1, 4, count, src_line_0003).",
            "list_member(count_set_1, 5, count, src_line_0003).",
            "list_member(count_set_1, 6, count, src_line_0003).",
            "list_member(count_set_1, 9, count, src_line_0003).",
            "item_range(count_set_1, 4, 6, src_line_0003).",
            "list_member(count_set_1, 4, count, src_line_0099).",
        ]
    }

    report = _enforce_list_range_inventory_fact_contract(source_compile)

    assert report["rejected_count"] == 3
    assert source_compile["facts"] == [
        "list_member(count_set_1, 2, count, src_line_0003).",
        "list_member(count_set_1, 9, count, src_line_0003).",
        "item_range(count_set_1, 4, 6, src_line_0003).",
        "list_member(count_set_1, 4, count, src_line_0099).",
    ]
    assert source_compile["deterministic_list_range_contract_policy"]["not_source_interpretation"] is True


def test_list_range_inventory_contract_rejects_cross_set_source_line_range_expansion() -> None:
    source_compile = {
        "facts": [
            "list_member(claim_set_expanded, 1, claim, source_line_0003).",
            "list_member(claim_set_expanded, 3, claim, source_line_0003).",
            "list_member(claim_set_expanded, 4, claim, source_line_0003).",
            "list_member(claim_set_expanded, 5, claim, source_line_0003).",
            "list_member(claim_set_expanded, 8, claim, source_line_0003).",
            "claim_range(claim_set_segment, 3, 5, src_line_0003).",
        ]
    }

    report = _enforce_list_range_inventory_fact_contract(source_compile)

    assert report["rejected_count"] == 3
    assert source_compile["facts"] == [
        "list_member(claim_set_expanded, 1, claim, source_line_0003).",
        "list_member(claim_set_expanded, 8, claim, source_line_0003).",
        "claim_range(claim_set_segment, 3, 5, src_line_0003).",
    ]
    assert report["rejected_facts"] == [
        "list_member(claim_set_expanded, 3, claim, source_line_0003).",
        "list_member(claim_set_expanded, 4, claim, source_line_0003).",
        "list_member(claim_set_expanded, 5, claim, source_line_0003).",
    ]


def test_list_range_inventory_contract_rejects_overcompressed_range_when_finer_segments_exist() -> None:
    source_compile = {
        "facts": [
            "claim_range(claim_set_broad, 1, 8, source_line_0003).",
            "claim_range(claim_set_exact, 1, 1, src_line_0003).",
            "claim_range(claim_set_exact, 3, 5, src_line_0003).",
            "claim_range(claim_set_exact, 8, 8, src_line_0003).",
            "list_member(claim_set_expanded, 3, claim, source_line_0003).",
            "list_member(claim_set_expanded, 8, claim, source_line_0003).",
        ]
    }

    report = _enforce_list_range_inventory_fact_contract(source_compile)

    assert report["rejected_count"] == 2
    assert report["rejected_facts"] == [
        "claim_range(claim_set_broad, 1, 8, source_line_0003).",
        "list_member(claim_set_expanded, 3, claim, source_line_0003).",
    ]
    assert source_compile["facts"] == [
        "claim_range(claim_set_exact, 1, 1, src_line_0003).",
        "claim_range(claim_set_exact, 3, 5, src_line_0003).",
        "claim_range(claim_set_exact, 8, 8, src_line_0003).",
        "list_member(claim_set_expanded, 8, claim, source_line_0003).",
    ]


def test_list_range_inventory_contract_rejects_malformed_claim_range_boundaries() -> None:
    source_compile = {
        "facts": [
            "claim_range(contested_claims_set, 6_9, claim, source_src_line_0028).",
            "claim_range(contested_claims_set, 6, 9, src_line_0028).",
            "list_member(contested_claims_set, 1, claim, src_line_0028).",
        ]
    }

    report = _enforce_list_range_inventory_fact_contract(source_compile)

    assert report["rejected_count"] == 1
    assert report["rejected_facts"] == [
        "claim_range(contested_claims_set, 6_9, claim, source_src_line_0028).",
    ]
    assert source_compile["facts"] == [
        "claim_range(contested_claims_set, 6, 9, src_line_0028).",
        "list_member(contested_claims_set, 1, claim, src_line_0028).",
        "claim_range(contested_claims_set, 6, 9, source_src_line_0028).",
    ]
    assert source_compile["deterministic_list_range_atom_reduction_facts"] == [
        "claim_range(contested_claims_set, 6, 9, source_src_line_0028).",
    ]
    assert source_compile["deterministic_list_range_atom_reduction_policy"]["not_source_interpretation"] is True


def test_source_pass_predicate_contract_guidance_names_optional_carriers() -> None:
    guidance = _source_pass_predicate_contract_guidance(
        [
            {"signature": "document_identifier_occurrence/5"},
            {"signature": "document_checkbox_provision/5"},
            {"signature": "claim_range/4"},
            {"signature": "claim_ground/4"},
            {"signature": "legal_citation_detail/4"},
            {"signature": "review_outcome/4"},
            {"signature": "procedural_rule_detail/5"},
            {"signature": "domain_omission/5"},
        ]
    )

    text = "\n".join(guidance)
    assert "CARRIER CONTRACT document_identifier_occurrence/5" in text
    assert "identifier_value is the source-stated value" in text
    assert "CARRIER CONTRACT document_checkbox_provision/5" in text
    assert "checkbox_state is the source-stated mark" in text
    assert "document_identifier_occurrence/5" in text
    assert "one candidate operation per occurrence" in text
    assert "document_checkbox_provision/5" in text
    assert "one candidate operation per source-stated row" in text
    assert "list/range inventory carriers" in text
    assert "source-stated singleton or source-stated range segment" in text
    assert "do not emit 1-9" in text
    assert "claim set anchor convergence" in text
    assert "Do not emit claim_range/4 with only numeric boundaries" in text
    assert "reuse one shared subject id" in text
    assert "broad inventory rows do not satisfy subset-specific ground" in text
    assert "Do not distribute a broad wrapper phrase" in text
    assert "Do not use bare claim numbers as claim_ground/4 subject ids" in text
    assert "emit claim_ground/4 on that same set id" in text
    assert "Contract delivery note for domain_omission/5" in text
    assert "explicit absence statements are source facts" in text
    assert "self_check alone does not satisfy omission accountability" in text
    assert "reuse the full prior set inventory" in text
    assert "same subject id as claim_ground/4" in text
    assert "statutory_ground rather than private variants" in text
    assert "review_outcome/4" in text
    assert "Do not invent private affirmed_by/2" in text
    assert "one review_outcome/4 row per governed subject id" in text
    assert "rather than a role label such as board_role" in text
    assert "procedural_rule_detail/5" in text
    assert "default consequence" in text
    assert "one procedural_rule_detail/5 row per atomic part" in text


def test_legal_citation_repair_context_reuses_governed_subject_ids() -> None:
    profile = {
        "candidate_predicates": [
            {"signature": "legal_citation_detail/4", "args": ["subject_id", "citation", "role", "source_or_scope"]},
            {"signature": "claim_ground/4", "args": ["subject_id", "ground", "reference", "status"]},
        ]
    }
    source_compile = {
        "facts": [
            "claim_ground(claim_set_alpha, anticipation, reference_alpha, rejected).",
            "claim_range(claim_set_alpha, 1, 1, src_line_0002).",
            "source_record_text_atom(src_line_0002, section_102_a_1).",
        ]
    }

    carriers = _profile_legal_citation_repair_offered_carriers(profile)
    text = "\n".join(
        _profile_legal_citation_repair_context_lines(
            parsed_profile=profile,
            source_compile=source_compile,
        )
    )

    assert carriers == ["legal_citation_detail/4"]
    assert "reuse that exact subject id" in text
    assert "preserve that purpose in legal_citation_detail/4's role slot" in text
    assert "preserve exact subsection markers in paragraph- or section-scoped rows" in text
    assert "investigation was commenced" in text
    assert "future_amendments_to_foregoing_laws_regulations_and_rules" in text
    assert "emit every enumerated citation on that same paragraph/obligation scope anchor" in text
    assert "EXISTING GOVERNED FACT: claim_ground(claim_set_alpha, anticipation, reference_alpha, rejected)." in text
    assert "source_record_text_atom" not in text


def test_governed_subject_discovery_context_uses_only_governed_carriers() -> None:
    profile = {
        "candidate_predicates": [
            {"signature": "claim_range/4", "args": ["claim_set_id", "start_claim", "end_claim", "source_or_scope"]},
            {"signature": "claim_ground/4", "args": ["claim_or_set_id", "ground", "reference", "status"]},
            {"signature": "legal_citation_detail/4", "args": ["subject_id", "citation", "role", "source_or_scope"]},
            {"signature": "review_outcome/4", "args": ["subject_id", "reviewer", "outcome", "source_or_scope"]},
            {"signature": "source_record_surface_mention/3"},
        ]
    }
    source_compile = {
        "facts": [
            "claim_range(claim_set_alpha, 1, 1, src_line_0002).",
            "claim_ground(claim_set_alpha, anticipation, reference_alpha, rejected).",
            "source_record_surface_mention(src_line_0002, claim_set_alpha, display).",
        ]
    }

    carriers = _profile_governed_subject_discovery_offered_carriers(profile)
    text = "\n".join(
        _profile_governed_subject_discovery_context_lines(
            parsed_profile=profile,
            source_compile=source_compile,
        )
    )

    assert carriers == ["claim_range/4", "claim_ground/4", "legal_citation_detail/4", "review_outcome/4"]
    assert "source-owned subject discovery" in text
    assert "one stable subject id per distinct source-stated subset" in text
    assert "do not emit source_record_* rows" in text
    assert "claim_range/4" in text
    assert "review_outcome/4" in text
    assert "EXISTING GOVERNED FACT: claim_ground(claim_set_alpha, anticipation, reference_alpha, rejected)." in text
    assert "source_record_surface_mention" not in text


def test_governed_subject_manifest_maps_typed_slots_to_governed_facts() -> None:
    manifest = {
        "schema_version": "governed_subject_manifest_v1",
        "subjects": [
            {
                "subject_id": "Set Alpha",
                "kind": "claim rejection",
                "ranges": [{"start": "1", "end": "1", "source_or_scope": "Line 0002"}],
                "ground": {
                    "present": True,
                    "theory": "anticipated",
                    "reference": "ref_alpha",
                    "status": "rejected",
                    "source_or_scope": "Line 0002",
                },
                "legal_citations": [{"citation": "102(a)(1)", "role": "statutory_basis", "source_or_scope": "Line 0002"}],
                "review_outcomes": [{"reviewer": "actor_board", "outcome": "affirmation_outcome", "source_or_scope": "Line 0005"}],
                "omitted_companions": [],
            }
        ],
        "subject_accounts": [
            {
                "subject_id": "Set Alpha",
                "companion_statuses": [
                    {"signature": "claim_range/4", "status": "instances", "reason": "range stated"},
                    {"signature": "claim_ground/4", "status": "instances", "reason": "ground stated"},
                    {"signature": "review_outcome/4", "status": "uncertain", "reason": "later sentence unclear"},
                    {"signature": "source_record_surface_mention/3", "status": "instances", "reason": "not allowed"},
                ],
            }
        ],
        "subject_accounts": [
            {
                "subject_id": "Set Alpha",
                "companion_statuses": [
                    {"signature": "claim_range/4", "status": "instances", "reason": "range stated"},
                    {"signature": "claim_ground/4", "status": "instances", "reason": "ground stated"},
                    {"signature": "review_outcome/4", "status": "uncertain", "reason": "later sentence unclear"},
                    {"signature": "source_record_surface_mention/3", "status": "instances", "reason": "not allowed"},
                ],
            }
        ],
        "self_check": {"missing_subjects": [], "notes": []},
    }

    report = _facts_from_governed_subject_manifest(
        manifest,
        allowed_signatures={"claim_range/4", "claim_ground/4", "legal_citation_detail/4", "review_outcome/4"},
    )

    assert report["facts"] == [
        "claim_range(set_alpha, 1, 1, line_0002).",
        "claim_ground(set_alpha, anticipation, reference_alpha, rejected).",
        "legal_citation_detail(set_alpha, section_102_a_1, statutory_ground, line_0002).",
        "review_outcome(set_alpha, review_board, affirmed, line_0005).",
    ]
    assert report["skipped"] == []


def test_governed_subject_atom_rows_maps_flat_rows_to_governed_facts() -> None:
    payload = {
        "schema_version": "governed_subject_atom_rows_v1",
        "rows": [
            {
                "signature": "claim_range/4",
                "args": ["Set Alpha", "1", "1", "Line 0002"],
                "source_or_scope": "Line 0002",
            },
            {
                "signature": "claim_ground/4",
                "args": ["Set Alpha", "anticipated", "ref_alpha", "rejected"],
                "source_or_scope": "Line 0002",
            },
            {
                "signature": "legal_citation_detail/4",
                "args": ["Set Alpha", "102(a)(1)", "statutory_basis", "Line 0002"],
                "source_or_scope": "Line 0002",
            },
            {
                "signature": "review_outcome/4",
                "args": ["Set Alpha", "actor_board", "affirmation_outcome", "Line 0005"],
                "source_or_scope": "Line 0005",
            },
            {
                "signature": "source_record_surface_mention/3",
                "args": ["Set Alpha", "display", "Line 0002", "extra"],
                "source_or_scope": "Line 0002",
            },
        ],
        "subject_accounts": [
            {
                "subject_id": "Set Alpha",
                "companion_statuses": [
                    {"signature": "claim_range/4", "status": "instances", "reason": "range stated"},
                    {"signature": "claim_ground/4", "status": "instances", "reason": "ground stated"},
                    {"signature": "review_outcome/4", "status": "uncertain", "reason": "later sentence unclear"},
                    {"signature": "source_record_surface_mention/3", "status": "instances", "reason": "not allowed"},
                ],
            }
        ],
        "self_check": {"missing_subjects": [], "notes": []},
    }

    report = _facts_from_governed_subject_atom_rows(
        payload,
        allowed_signatures={"claim_range/4", "claim_ground/4", "legal_citation_detail/4", "review_outcome/4"},
    )

    assert report["facts"] == [
        "claim_range(set_alpha, 1, 1, line_0002).",
        "claim_ground(set_alpha, anticipation, reference_alpha, rejected).",
        "legal_citation_detail(set_alpha, section_102_a_1, statutory_ground, line_0002).",
        "review_outcome(set_alpha, review_board, affirmed, line_0005).",
    ]
    assert report["skipped"] == [{"reason": "signature_not_allowed", "value": "source_record_surface_mention/3"}]
    assert report["subject_accounts"] == [
        {"subject": "set_alpha", "signature": "claim_range/4", "status": "instances", "reason": "range stated"},
        {"subject": "set_alpha", "signature": "claim_ground/4", "status": "instances", "reason": "ground stated"},
        {
            "subject": "set_alpha",
            "signature": "review_outcome/4",
            "status": "uncertain",
            "reason": "later sentence unclear",
        },
    ]
    assert report["account_skipped"] == [
        {"reason": "companion_status_signature_not_allowed", "value": "source_record_surface_mention/3"}
    ]

    alternate_report = _facts_from_governed_subject_atom_rows(
        {
            "governed_subject_atom_rows_v1": [
                {"claim_range": ["Set Alpha", 1, 1, "Line 0002"]},
                {"predicate": "claim_ground", "args": ["Set Alpha", "anticipated", "ref_alpha", "rejected"]},
                {"sig": "legal_citation_detail/4", "args": ["Set Alpha", "102(a)(1)", "statutory_basis", "Line 0002"]},
            ]
        },
        allowed_signatures={"claim_range/4", "claim_ground/4", "legal_citation_detail/4"},
    )

    assert alternate_report["facts"] == [
        "claim_range(set_alpha, 1, 1, line_0002).",
        "claim_ground(set_alpha, anticipation, reference_alpha, rejected).",
        "legal_citation_detail(set_alpha, section_102_a_1, statutory_ground, line_0002).",
    ]
    assert alternate_report["skipped"] == []


def test_governed_subject_atom_rows_replace_prior_supported_carriers_only() -> None:
    report = _replace_governed_subject_atom_row_facts(
        existing_facts=[
            "claim_range(stale_subject, 1, 9, old_source).",
            "claim_ground(stale_subject, section_102, reference_alpha, rejected).",
            "claim_ground(clean_subject, section_103, reference_beta, rejected).",
            "source_record_surface_mention(src1, stale_subject, display).",
        ],
        replacement_facts=[
            "claim_range(clean_subject, 1, 1, line_1).",
            "claim_ground(clean_subject, anticipation, reference_alpha, rejected).",
        ],
    )

    assert report["facts"] == [
        "claim_range(stale_subject, 1, 9, old_source).",
        "claim_ground(stale_subject, section_102, reference_alpha, rejected).",
        "source_record_surface_mention(src1, stale_subject, display).",
        "claim_range(clean_subject, 1, 1, line_1).",
        "claim_ground(clean_subject, anticipation, reference_alpha, rejected).",
    ]
    assert report["replaced_facts"] == [
        "claim_ground(clean_subject, section_103, reference_beta, rejected).",
    ]
    assert report["appended_facts"] == [
        "claim_range(clean_subject, 1, 1, line_1).",
        "claim_ground(clean_subject, anticipation, reference_alpha, rejected).",
    ]


def test_legal_citation_repair_context_prefers_canonical_claim_set_ids() -> None:
    profile = {
        "candidate_predicates": [
            {"signature": "legal_citation_detail/4", "args": ["subject_id", "citation", "role", "source_or_scope"]},
            {"signature": "claim_ground/4", "args": ["subject_id", "ground", "reference", "status"]},
        ]
    }
    source_compile = {
        "facts": [
            "claim_ground(claim_set_alpha, 102_a_1, reference_alpha, anticipated).",
            "claim_range(claim_set_alpha, 1, 1, src_line_0002).",
            "claim_ground(claim_set_alpha_102, anticipation, reference_alpha, rejected).",
            "claim_range(claim_set_alpha_102, 1, 1, src_line_0002).",
            "review_outcome(claim_set_alpha_102, review_board, affirmed, src_line_0005).",
        ]
    }

    preferred = _legal_citation_repair_preferred_subject_ids(source_compile)
    text = "\n".join(
        _profile_legal_citation_repair_context_lines(
            parsed_profile=profile,
            source_compile=source_compile,
        )
    )

    assert preferred == ["claim_set_alpha_102"]
    assert "preferred governed subject ids for legal citations: claim_set_alpha_102" in text
    assert "EXISTING GOVERNED FACT: claim_ground(claim_set_alpha_102, anticipation, reference_alpha, rejected)." in text
    assert "EXISTING GOVERNED FACT: claim_ground(claim_set_alpha, 102_a_1, reference_alpha, anticipated)." not in text


def test_legal_citation_subject_contract_rejects_new_duplicate_subject_citations() -> None:
    source_compile = {
        "facts": [
            "claim_ground(claim_set_alpha_102, anticipation, reference_alpha, rejected).",
            "legal_citation_detail(claim_set_alpha_102, section_102_a_1, statutory_ground, direct).",
            "legal_citation_detail(claim_set_alpha, section_102_a_1, statutory_ground, src_line_0005).",
            "legal_citation_detail(document_order, section_102_a_1, statutory_ground, src_line_0005).",
        ]
    }

    report = _enforce_legal_citation_repair_subject_contract(
        source_compile,
        preferred_subjects={"claim_set_alpha_102"},
        prior_facts={
            "claim_ground(claim_set_alpha_102, anticipation, reference_alpha, rejected).",
            "legal_citation_detail(document_order, section_102_a_1, statutory_ground, src_line_0005).",
        },
    )

    assert report["rejected_facts"] == [
        "legal_citation_detail(claim_set_alpha, section_102_a_1, statutory_ground, src_line_0005)."
    ]
    assert "legal_citation_detail(claim_set_alpha_102, section_102_a_1, statutory_ground, direct)." in source_compile["facts"]
    assert "legal_citation_detail(document_order, section_102_a_1, statutory_ground, src_line_0005)." in source_compile["facts"]


def test_review_outcome_repair_context_targets_governed_subject_ids() -> None:
    profile = {
        "candidate_predicates": [
            {"signature": "review_outcome/4", "args": ["reviewed_subject_id", "reviewing_body", "outcome", "source_or_scope"]},
            {"signature": "claim_ground/4", "args": ["subject_id", "ground", "reference", "status"]},
        ]
    }
    source_compile = {
        "facts": [
            "claim_ground(claim_set_alpha, anticipation, reference_alpha, rejected).",
            "claim_range(claim_set_alpha, 1, 1, src_line_0003).",
            "legal_citation_detail(claim_set_alpha, section_102_a_1, statutory_ground, src_line_0005).",
            "review_outcome(reviewed_rejections, review_board, affirmed, src_line_0011).",
            "source_record_text_atom(src_line_0011, board_affirmed).",
        ]
    }

    carriers = _profile_review_outcome_repair_offered_carriers(profile)
    text = "\n".join(
        _review_outcome_repair_context_lines(
            parsed_profile=profile,
            source_compile=source_compile,
        )
    )

    assert carriers == ["review_outcome/4"]
    assert "preferred governed subject ids for review outcomes: claim_set_alpha" in text
    assert "EXISTING GOVERNED FACT: claim_ground(claim_set_alpha, anticipation, reference_alpha, rejected)." in text
    assert "reviewed-rejections ids" in text
    assert "source_record_text_atom" not in text


def test_review_outcome_repair_context_allows_document_level_final_disposition_subjects() -> None:
    profile = {
        "candidate_predicates": [
            {
                "signature": "review_outcome/4",
                "args": ["reviewed_subject_id", "reviewing_body", "outcome", "source_or_scope"],
            }
        ]
    }
    source_compile = {
        "facts": [
            "document_identifier_occurrence(fed_cir_2025_1705_song, appeal_no, 2025_1705, header, 1).",
            "document_date(fed_cir_2025_1705_song, decision_date, february_18_2026).",
            "affirmed(2025_1705, affirmed).",
            "claim_ground(song_18199940_rejection_1, anticipation, song_656, rejected).",
            "review_outcome(song_18199940_rejection_1, federal_circuit, affirmed, final_disposition).",
        ]
    }

    text = "\n".join(
        _review_outcome_repair_context_lines(
            parsed_profile=profile,
            source_compile=source_compile,
        )
    )

    assert "document-level or case-level final disposition" in text
    assert "available document/case subject ids for document-level final dispositions: fed_cir_2025_1705_song" in text
    assert "EXISTING GOVERNED FACT: document_date(fed_cir_2025_1705_song, decision_date, february_18_2026)." in text
    assert "EXISTING GOVERNED FACT: affirmed(2025_1705, affirmed)." in text
    assert "EXISTING GOVERNED FACT: source_record" not in text


def test_additive_pass_signature_contract_rejects_offered_carrier_escape() -> None:
    source_compile = {
        "facts": [
            "claim_id(1).",
            "claim_range(claim_set_alpha, 1, 1, src_line_0003).",
            "anticipated_by_reference(1, reference_alpha).",
        ]
    }
    pass_record = {
        "facts": [
            "claim_range(claim_set_alpha, 1, 1, src_line_0003).",
            "anticipated_by_reference(1, reference_alpha).",
        ],
        "_profile_list_range_inventory_repair_new_facts": [
            "claim_range(claim_set_alpha, 1, 1, src_line_0003).",
            "anticipated_by_reference(1, reference_alpha).",
        ],
    }

    report = _enforce_additive_pass_allowed_signatures(
        source_compile,
        prior_facts={"claim_id(1)."},
        allowed_signatures={"claim_range/4", "claim_ground/4"},
        metadata_prefix="profile_list_range_inventory_repair",
        pass_record=pass_record,
    )

    assert report["rejected_facts"] == ["anticipated_by_reference(1, reference_alpha)."]
    assert source_compile["facts"] == [
        "claim_id(1).",
        "claim_range(claim_set_alpha, 1, 1, src_line_0003).",
    ]
    assert pass_record["facts"] == ["claim_range(claim_set_alpha, 1, 1, src_line_0003)."]
    assert pass_record["_profile_list_range_inventory_repair_new_facts"] == [
        "claim_range(claim_set_alpha, 1, 1, src_line_0003)."
    ]
    assert source_compile["profile_list_range_inventory_repair_signature_contract_rejected_count"] == 1


def test_vote_tally_profile_extension_adds_direct_carrier_for_explicit_tallies() -> None:
    profile = {
        "candidate_predicates": [
            {
                "signature": "hearing_note/3",
                "args": ["hearing_id", "topic", "text"],
                "description": "Broad hearing note.",
                "why": "Keeps hearing text.",
                "admission_notes": [],
            }
        ],
        "provenance_sensitive_predicates": [],
        "self_check": {"notes": []},
    }

    metadata = _ensure_vote_tally_predicate(
        profile,
        source_text=(
            "The board voted 3-2 to proceed without a new survey.\n"
            "The final vote was approved 3-1."
        ),
    )

    assert metadata["added"] is True
    assert metadata["signature"] == "vote_tally/5"
    assert any(item["signature"] == "vote_tally/5" for item in profile["candidate_predicates"])
    assert "vote_tally/5" in profile["provenance_sensitive_predicates"]


def test_event_date_profile_extension_adds_direct_carrier_for_dated_events() -> None:
    profile = {
        "candidate_predicates": [
            {
                "signature": "hearing_status/2",
                "args": ["hearing_id", "status"],
                "description": "Hearing status.",
                "why": "Keeps hearing status.",
                "admission_notes": [],
            }
        ],
        "provenance_sensitive_predicates": [],
        "self_check": {"notes": []},
    }

    metadata = _ensure_event_date_predicate(
        profile,
        source_text="Hearing date April 24, 2026. Koss filed an appeal on 2026-05-08.",
    )

    assert metadata["added"] is True
    assert metadata["signature"] == "event_date/2"
    assert any(item["signature"] == "event_date/2" for item in profile["candidate_predicates"])
    assert "event_date/2" in profile["provenance_sensitive_predicates"]


def test_event_date_profile_extension_adds_direct_carrier_for_timed_events() -> None:
    profile = {
        "candidate_predicates": [
            {
                "signature": "event_status/2",
                "args": ["event_id", "status"],
                "description": "Event status.",
                "why": "Keeps event status.",
                "admission_notes": [],
            }
        ],
        "provenance_sensitive_predicates": [],
        "self_check": {"notes": []},
    }

    metadata = _ensure_event_date_predicate(
        profile,
        source_text="About 1415 the guard arm released and the status changed to open.",
    )

    assert metadata["added"] is True
    assert metadata["signature"] == "event_time/2"
    assert any(item["signature"] == "event_time/2" for item in profile["candidate_predicates"])
    assert "event_time/2" in profile["provenance_sensitive_predicates"]


def test_event_date_profile_extension_respects_existing_temporal_carrier() -> None:
    profile = {
        "candidate_predicates": [
            {
                "signature": "hearing_date/2",
                "args": ["hearing_id", "date"],
            }
        ],
    }

    metadata = _ensure_event_date_predicate(
        profile,
        source_text="Hearing date April 24, 2026.",
    )

    assert metadata == {
        "schema_version": "profile_event_date_extension_v1",
        "added": False,
        "reason": "event_date_carrier_present",
    }


def test_quorum_status_profile_extension_adds_direct_carrier_for_quorum_checks() -> None:
    profile = {
        "candidate_predicates": [
            {
                "signature": "hearing_note/3",
                "args": ["hearing_id", "topic", "text"],
            }
        ],
        "provenance_sensitive_predicates": [],
        "self_check": {"notes": []},
    }

    metadata = _ensure_quorum_status_predicate(
        profile,
        source_text="Quorum check: 4 of 5 members present; quorum met, 3 required.",
    )

    assert metadata["added"] is True
    assert metadata["signature"] == "quorum_status/3"
    assert any(item["signature"] == "quorum_status/3" for item in profile["candidate_predicates"])
    assert "quorum_status/3" in profile["provenance_sensitive_predicates"]


def test_quorum_status_profile_extension_respects_existing_carrier() -> None:
    profile = {
        "candidate_predicates": [
            {"signature": "meeting_quorum/3", "args": ["meeting_id", "status", "count"]},
        ],
    }

    metadata = _ensure_quorum_status_predicate(
        profile,
        source_text="Quorum check: 4 of 5 members present; quorum met, 3 required.",
    )

    assert metadata == {
        "schema_version": "profile_quorum_status_extension_v1",
        "added": False,
        "reason": "quorum_status_carrier_present",
    }


def test_appeal_filing_profile_extension_adds_direct_carrier_for_appeals() -> None:
    profile = {
        "candidate_predicates": [
            {"signature": "post_hearing_note/2", "args": ["note_id", "text"]},
        ],
        "provenance_sensitive_predicates": [],
        "self_check": {"notes": []},
    }

    metadata = _ensure_appeal_filing_predicate(
        profile,
        source_text="Koss files a formal appeal of the variance approval on May 8, 2026 within the 30-day appeal window.",
    )

    assert metadata["added"] is True
    assert metadata["signature"] == "appeal_filed/3"
    assert any(item["signature"] == "appeal_filed/3" for item in profile["candidate_predicates"])
    assert "appeal_filed/3" in profile["provenance_sensitive_predicates"]


def test_appeal_filing_profile_extension_ignores_appeal_window_notice() -> None:
    profile = {
        "candidate_predicates": [
            {"signature": "post_hearing_note/2", "args": ["note_id", "text"]},
        ],
        "provenance_sensitive_predicates": [],
        "self_check": {"notes": []},
    }

    metadata = _ensure_appeal_filing_predicate(
        profile,
        source_text=(
            "Any party desiring to appeal this order must do so in the appropriate court "
            "within 30 days after issuance and notify the commission."
        ),
    )

    assert metadata == {
        "schema_version": "profile_appeal_filing_extension_v1",
        "added": False,
        "reason": "no_explicit_appeal_filing_signal",
    }
    assert not any(item["signature"] == "appeal_filed/3" for item in profile["candidate_predicates"])
    assert "appeal_filed/3" not in profile["provenance_sensitive_predicates"]


def test_appeal_filing_profile_extension_respects_existing_carrier() -> None:
    profile = {
        "candidate_predicates": [
            {"signature": "appeal_record/3", "args": ["appellant", "target", "grounds"]},
        ],
    }

    metadata = _ensure_appeal_filing_predicate(
        profile,
        source_text="Koss files a formal appeal of the variance approval on May 8, 2026.",
    )

    assert metadata == {
        "schema_version": "profile_appeal_filing_extension_v1",
        "added": False,
        "reason": "appeal_filing_carrier_present",
    }


def test_quantity_event_profile_extension_is_vocabulary_only() -> None:
    profile = {
        "candidate_predicates": [
            {"signature": "event_record/3", "args": ["event_id", "source", "timestamp"]},
            {"signature": "event_description/2", "args": ["event_id", "description"]},
        ],
        "provenance_sensitive_predicates": [],
        "self_check": {"notes": []},
    }

    metadata = _ensure_quantity_event_predicate(
        profile,
        source_text=(
            "EV-01 2026-04-22 feed rate increased to 18 kg min.\n"
            "EV-02 2026-04-22 setpoint changed from 480 k to 495 k."
        ),
    )

    assert metadata["added"] is True
    assert metadata["fact_extraction"] is False
    assert any(item["signature"] == "event_measurement/4" for item in profile["candidate_predicates"])
    assert "event_measurement/4" in profile["provenance_sensitive_predicates"]


def test_quantity_event_profile_extension_respects_existing_carrier() -> None:
    profile = {
        "candidate_predicates": [
            {
                "signature": "metric_observation/4",
                "args": ["event_id", "metric", "value", "unit"],
            }
        ],
    }

    metadata = _ensure_quantity_event_predicate(
        profile,
        source_text=(
            "EV-01 2026-04-22 feed rate increased to 18 kg min.\n"
            "EV-02 2026-04-22 setpoint changed from 480 k to 495 k."
        ),
    )

    assert metadata == {
        "schema_version": "profile_quantity_event_extension_v1",
        "added": False,
        "reason": "no_shallow_quantity_event_palette",
    }


def test_status_state_profile_extension_is_vocabulary_only() -> None:
    profile = {
        "candidate_predicates": [
            {"signature": "record_status/2", "args": ["record_id", "status"]},
            {"signature": "status_date/2", "args": ["record_id", "date"]},
        ],
        "provenance_sensitive_predicates": [],
        "self_check": {"notes": []},
    }

    metadata = _ensure_status_state_predicate(
        profile,
        source_text=(
            "On 2026-09-15 record alpha status was suspect.\n"
            "On 2026-09-20 record beta status was cleared."
        ),
    )

    assert metadata["added"] is True
    assert metadata["fact_extraction"] is False
    assert any(item["signature"] == "status_state_at/4" for item in profile["candidate_predicates"])
    assert "status_state_at/4" in profile["provenance_sensitive_predicates"]


def test_status_state_profile_extension_respects_existing_carrier() -> None:
    profile = {
        "candidate_predicates": [
            {"signature": "record_status_at/3", "args": ["record_id", "status", "date"]},
        ],
    }

    metadata = _ensure_status_state_predicate(
        profile,
        source_text=(
            "On 2026-09-15 record alpha status was suspect.\n"
            "On 2026-09-20 record beta status was cleared."
        ),
    )

    assert metadata == {
        "schema_version": "profile_status_state_extension_v1",
        "added": False,
        "reason": "no_shallow_status_state_palette",
    }


def test_source_attributed_claim_profile_extension_is_vocabulary_only() -> None:
    profile = {
        "candidate_predicates": [
            {"signature": "source_note/2", "args": ["source_id", "text"]},
            {"signature": "claim_status/2", "args": ["claim_id", "status"]},
        ],
        "provenance_sensitive_predicates": [],
        "self_check": {"notes": []},
    }

    metadata = _ensure_source_attributed_claim_predicate(
        profile,
        source_text=(
            "Rivera memo says device alpha status is active.\n"
            "Field report notes claim beta remains unresolved."
        ),
    )

    assert metadata["added"] is True
    assert metadata["fact_extraction"] is False
    assert any(item["signature"] == "source_attributed_claim/4" for item in profile["candidate_predicates"])
    assert "source_attributed_claim/4" in profile["provenance_sensitive_predicates"]


def test_source_attributed_claim_profile_extension_respects_existing_carrier() -> None:
    profile = {
        "candidate_predicates": [
            {
                "signature": "source_claim/4",
                "args": ["claim_id", "source_document", "content", "source_row"],
            }
        ],
    }

    metadata = _ensure_source_attributed_claim_predicate(
        profile,
        source_text=(
            "Rivera memo says device alpha status is active.\n"
            "Field report notes claim beta remains unresolved."
        ),
    )

    assert metadata == {
        "schema_version": "profile_source_attributed_claim_extension_v1",
        "added": False,
        "reason": "source_attributed_claim_carrier_present",
    }


def test_source_attributed_claim_profile_extension_rejects_status_change_as_claim_carrier() -> None:
    profile = {
        "candidate_predicates": [
            {
                "signature": "lot_status_change/4",
                "args": ["lot_id", "new_status", "date", "source"],
            }
        ],
        "provenance_sensitive_predicates": [],
    }

    metadata = _ensure_source_attributed_claim_predicate(
        profile,
        source_text=(
            "Lab report confirmed citrus canker in lot 3A.\n"
            "Solberg's note says no further action is recommended."
        ),
    )

    assert metadata["added"] is True
    assert any(item["signature"] == "source_attributed_claim/4" for item in profile["candidate_predicates"])
    assert "source_attributed_claim/4" in profile["provenance_sensitive_predicates"]


def test_source_attributed_claim_profile_extension_rejects_claim_source_without_content() -> None:
    profile = {
        "candidate_predicates": [
            {
                "signature": "claim_source/4",
                "args": ["claim_label", "subject", "source", "support_role"],
            }
        ],
    }

    metadata = _ensure_source_attributed_claim_predicate(
        profile,
        source_text="Navarro's letter of intent is under review; it is not a binding lease.",
    )

    assert metadata["added"] is True
    assert any(item["signature"] == "source_attributed_claim/4" for item in profile["candidate_predicates"])


def test_source_authority_profile_extension_adds_vocabulary_for_explicit_authority() -> None:
    profile = {
        "candidate_predicates": [
            {
                "signature": "rule_condition/3",
                "args": ["rule_id", "condition", "consequence"],
                "description": "Rule condition.",
                "why": "Captures condition/consequence pairs.",
                "admission_notes": [],
            }
        ],
        "provenance_sensitive_predicates": [],
        "self_check": {"notes": []},
    }

    metadata = _ensure_source_authority_predicate(
        profile,
        source_text="Only the judge may grant the extension; stipulations are insufficient without a court order.",
    )

    assert metadata["added"] is True
    assert metadata["fact_extraction"] is False
    assert any(item["signature"] == "source_authority/3" for item in profile["candidate_predicates"])
    assert "source_authority/3" in profile["provenance_sensitive_predicates"]


def test_source_authority_profile_extension_is_not_added_without_signal() -> None:
    profile = {"candidate_predicates": [], "provenance_sensitive_predicates": [], "self_check": {"notes": []}}

    metadata = _ensure_source_authority_predicate(profile, source_text="The note lists three dates and two amounts.")

    assert metadata == {
        "schema_version": "profile_source_authority_extension_v1",
        "added": False,
        "reason": "no_explicit_source_authority_signal",
    }
    assert profile["candidate_predicates"] == []


def test_source_authority_profile_extension_respects_existing_carrier() -> None:
    profile = {
        "candidate_predicates": [
            {
                "signature": "governing_source/3",
                "args": ["subject_id", "source_id", "scope"],
                "description": "Governing source.",
                "why": "Carries source authority.",
                "admission_notes": [],
            }
        ],
        "provenance_sensitive_predicates": [],
        "self_check": {"notes": []},
    }

    metadata = _ensure_source_authority_predicate(profile, source_text="The governing rule controls the action.")

    assert metadata == {
        "schema_version": "profile_source_authority_extension_v1",
        "added": False,
        "reason": "source_authority_carrier_present",
    }
    assert all(item["signature"] != "source_authority/3" for item in profile["candidate_predicates"])


def test_entity_location_profile_extension_is_vocabulary_only() -> None:
    profile = {
        "candidate_predicates": [
            {
                "signature": "sensor_id/1",
                "args": ["sensor_id"],
                "description": "Sensor identifier.",
            }
        ],
        "provenance_sensitive_predicates": [],
        "self_check": {"notes": []},
    }

    metadata = _ensure_entity_location_predicate(
        profile,
        source_text="HUM-D-04 — Location: Dryer Chamber 4 mid-bed.",
    )

    assert metadata["added"] is True
    assert metadata["fact_extraction"] is False
    assert any(item["signature"] == "entity_location/3" for item in profile["candidate_predicates"])
    assert "entity_location/3" in profile["provenance_sensitive_predicates"]


def test_entity_location_profile_extension_respects_existing_carrier() -> None:
    profile = {
        "candidate_predicates": [
            {
                "signature": "device_location/2",
                "args": ["device_id", "location"],
                "description": "Device location.",
            }
        ],
    }

    metadata = _ensure_entity_location_predicate(profile, source_text="Device alpha location: Room 4.")

    assert metadata == {
        "schema_version": "profile_entity_location_extension_v1",
        "added": False,
        "reason": "location_carrier_present",
    }


def test_scheduled_event_profile_extension_is_vocabulary_only() -> None:
    profile = {
        "candidate_predicates": [
            {
                "signature": "sensor_id/1",
                "args": ["sensor_id"],
                "description": "Sensor identifier.",
                "why": "Keeps devices queryable.",
                "admission_notes": [],
            }
        ],
        "provenance_sensitive_predicates": [],
        "self_check": {"notes": []},
    }

    metadata = _ensure_scheduled_event_predicate(
        profile,
        source_text="HUM-D-04 last calibration 2026-01-12. Next calibration due 2026-07-12.",
    )

    assert metadata["added"] is True
    assert metadata["fact_extraction"] is False
    assert any(item["signature"] == "scheduled_event/4" for item in profile["candidate_predicates"])
    assert "scheduled_event/4" in profile["provenance_sensitive_predicates"]


def test_scheduled_event_profile_extension_respects_existing_carrier() -> None:
    profile = {
        "candidate_predicates": [
            {
                "signature": "maintenance_due/2",
                "args": ["device_id", "due_date"],
                "description": "Maintenance due date.",
            }
        ],
    }

    metadata = _ensure_scheduled_event_predicate(
        profile,
        source_text="Next maintenance due 2026-07-12.",
    )

    assert metadata == {
        "schema_version": "profile_scheduled_event_extension_v1",
        "added": False,
        "reason": "scheduled_event_carrier_present",
    }


def test_repeated_structure_predicate_extension_admits_property_predicates() -> None:
    profile = {
        "candidate_predicates": [
            {
                "signature": "reconciliation_report/5",
                "args": ["report_id", "date", "subject", "status", "count"],
                "description": "Repeated reconciliation record.",
                "admission_notes": [],
            }
        ],
        "repeated_structures": [
            {
                "name": "reconciliation reports",
                "record_predicate": "reconciliation_report/5",
                "property_predicates": ["unit_count/3", "unaccounted_units/3"],
            }
        ],
        "self_check": {"notes": []},
    }

    metadata = _ensure_repeated_structure_predicates(profile)

    signatures = {item["signature"] for item in profile["candidate_predicates"]}
    assert metadata["added"] is True
    assert metadata["signatures"] == ["unit_count/3", "unaccounted_units/3"]
    assert {"reconciliation_report/5", "unit_count/3", "unaccounted_units/3"} <= signatures
    added = [item for item in profile["candidate_predicates"] if item["signature"] == "unit_count/3"][0]
    assert added["args"] == ["arg_1", "arg_2", "arg_3"]
    assert metadata["fact_extraction"] is False


def test_operational_record_context_guards_status_corrections_and_unresolved_items() -> None:
    context = "\n".join(OPERATIONAL_RECORD_STATUS_CONTEXT_V1)

    assert "status before/after" in context
    assert "original/superseded value" in context
    assert "pending, unresolved, referred, deferred" in context
    assert "Operational lifecycle canonical palette preference" in context
    assert "record_status_phase/4" in context
    assert "record_lifecycle_event/5" in context
    assert "Operational record slot contract" in context
    assert "Operational received/filing actor rule" in context
    assert "Operational withdrawn-request content rule" in context
    assert "repeated dated lifecycle/status list" in context
    assert "subject, lifecycle state/action, and date/turn remain queryable together" in context
    assert "A domain-specific status/result predicate is not stricter if it drops the date" in context
    assert "status before and after when stated" in context
    assert "record type or status word alone is shallow metadata" in context
    assert "Do not substitute the submitter/applicant/source actor" in context
    assert "requested action/content/line item or descriptive target" in context


def test_compile_surface_invariants_preserve_source_stated_update_notices() -> None:
    context = "\n".join(COMPILE_SURFACE_INVARIANT_CONTEXT_V1)

    assert "later notice, correction, amendment, update, extension" in context
    assert "original/source document id" in context
    assert "changed field, stated effect, and source row" in context
    assert "Do not leave a source-stated update only as an intake-plan risk" in context


def test_source_compiler_context_selects_operational_record_lens_from_domain_hint() -> None:
    context = "\n".join(
        _source_compiler_context(
            intake_plan=None,
            domain_hint="turnstream facilities intake corrections pending uncertainty budget authority",
        )
    )

    assert "operational_record_status_strategy_v1" in context
    assert "Operational join-readiness rule" in context
    assert "permit/license lifecycle" in context
    assert "quarantine/lot-status" in context


def test_source_compiler_context_selects_financial_report_lens_from_intake_plan() -> None:
    context = "\n".join(
        _source_compiler_context(
            domain_hint="",
            intake_plan={
                "source_boundary": {
                    "source_type": "Corporate earnings release",
                    "epistemic_stance": "Formal corporate disclosure with financial statements.",
                },
                "pass_plan": [
                    {
                        "purpose": "Capture financial performance.",
                        "focus": "Financial result totals, investee contribution, and segment performance.",
                    }
                ],
            },
        )
    )

    assert "financial_report_source_compiler_strategy_v1" in context
    assert "source-stated totals and named scope contributions" in context
    assert "period, named scope/entity, metric, value, and unit" in context


def test_greenhouse_and_school_records_get_scoped_contexts() -> None:
    greenhouse_context = "\n".join(
        _source_compiler_context(
            domain_hint="greenhouse quarantine lab result nursery lot status record",
            intake_plan=None,
        )
    )
    school_context = "\n".join(
        _source_compiler_context(
            domain_hint="school field trip attendance supervision chaperone station roster",
            intake_plan=None,
        )
    )

    assert "quarantine/lot-status" in greenhouse_context
    assert "sample count" in greenhouse_context
    assert "administrative_roster_timeline_strategy_v1" in school_context
    assert "Mixed-session assignments must not overwrite the standing group roster" in school_context


def test_probate_property_context_separates_ownership_possession_and_status() -> None:
    context = "\n".join(PROBATE_PROPERTY_STATUS_CONTEXT_V1)

    assert "ownership, possession, control, custody, maintenance" in context
    assert "disputed, provisional, deferred, potential" in context
    assert "gift cards, bills of sale, solicitor advice" in context
    assert "balances, payments, seasonal values, totals" in context
    assert "row for every named governed subject/action" in context

    selected = "\n".join(
        _source_compiler_context(
            domain_hint="probate inheritance estate will gift pledge possession ownership adverse possession",
            intake_plan=None,
        )
    )

    assert "probate_property_status_strategy_v1" in selected
    assert "source-stated purchases, sales, wills, gifts" in selected


def test_competition_role_alias_context_keeps_banners_roles_and_corrections() -> None:
    context = "\n".join(COMPETITION_ROLE_ALIAS_CONTEXT_V1)

    assert "banner/title aliases are time-scoped identities" in context
    assert "dual-role records" in context
    assert "original posted rank, corrected rank" in context
    assert "Do not transfer an old banner victory" in context

    selected = "\n".join(
        _source_compiler_context(
            domain_hint="tournament archery banner alias scoring ranking protest marshal range officer dual role",
            intake_plan=None,
        )
    )

    assert "competition_role_alias_strategy_v1" in selected
    assert "protests, rulings, holds, misfires" in selected


def test_source_authority_audit_context_keeps_claim_source_and_correction_status() -> None:
    context = "\n".join(SOURCE_AUTHORITY_AUDIT_CONTEXT_V1)

    assert "visible/public text, copied guide text" in context
    assert "copied text is not independent confirmation" in context
    assert "drafted, installed, rejected, queued" in context
    assert "Authority override" in context
    assert "source document id" in context
    assert "source actor/author" in context
    assert "governed subject/item/claim/action" in context
    assert "Evidence provenance slot contract" in context
    assert "Authority and custody slot contract" in context
    assert "Authority record-detail rule" in context
    assert "artifact/source id" in context
    assert "recipient, admitting body, relying body, or presentation context" in context
    assert "role-only, recipient-only, or context-only rows" in context
    assert "reason a source is noncontrolling" in context
    assert "draft recommendation, staff note, official record, and controlling finding" in context
    assert "Authority draft-recommendation rule" in context
    assert "proposed content/action/scope" in context
    assert "Authority noncontrolling-source rule" in context
    assert "omitted controlling source" in context
    assert "Type, author, date, and status alone are shallow record metadata" in context

    selected = "\n".join(
        _source_compiler_context(
            domain_hint="museum relabelling audit placard visitor guide catalog acquisition record curator correction status",
            intake_plan=None,
        )
    )

    assert "source_authority_audit_strategy_v1" in selected
    assert "numeric counts, publication years, date ranges" in selected


def test_compile_surface_invariants_keep_authority_custody_ladder_slots() -> None:
    context = "\n".join(COMPILE_SURFACE_INVARIANT_CONTEXT_V1)

    assert "authority or custody ladder" in context
    assert "court order with issuer, content/action, date, and scope" in context
    assert "governing rule with rule, jurisdiction/body, and applicable condition" in context
    assert "noncontrolling source with source, content, and reason noncontrolling" in context
    assert "custody/access control with holder or access actor" in context
    assert "authority/custody record metadata is not enough by itself" in context
    assert "same-anchor content/effect/scope/condition/decision/governed-subject/reason rows" in context


def test_compile_surface_invariants_keep_current_adjudication_disposition_separate_from_history() -> None:
    context = "\n".join(COMPILE_SURFACE_INVARIANT_CONTEXT_V1)

    assert "current disposition surfaces separate from procedural history" in context
    assert "current decision or case id" in context
    assert "remands/transfers" in context
    assert "resolves it directly/on the merits" in context
    assert "If no stricter profile predicate can carry the disposition mode or effect" in context
    assert "source_detail/4" in context
    assert "underlying action under review preserved separately from the reviewing outcome" in context
    assert "emit typed rows for both layers" in context
    assert "Reuse the same governed item/claim/issue/action atom" in context
    assert "Do not encode the underlying rejection or denial only as a final affirmed status" in context


def test_compile_surface_invariants_keep_violation_categories_separate_from_actions() -> None:
    context = "\n".join(COMPILE_SURFACE_INVARIANT_CONTEXT_V1)

    assert "captioned duty/category labels" in context
    assert "violation or deficiency categories as separate answer surfaces" in context
    assert "intervention/action type rows" in context
    assert "legal_basis alone" in context
    assert "emit separate category rows for the stated items" in context


def test_compile_surface_invariants_keep_operational_record_slots() -> None:
    context = "\n".join(COMPILE_SURFACE_INVARIANT_CONTEXT_V1)

    assert "chronological/event-list sources need complete event backbone units" in context
    assert "fixed one-time due date and a recurring cadence" in context
    assert "two bare day counts" in context
    assert "Compile surface preservation rule" in context
    assert "must not replace already-needed concrete typed rows" in context
    assert "dropping typed backbone predicate families is not acceptable" in context
    assert "event id or entry label, date/time/order, actor/party/system" in context
    assert "vague event wrapper" in context
    assert "financial or numeric-state calculations need baseline preservation" in context
    assert "financial reports often state a total metric and then a named contributor" in context
    assert "actual versus hypothetical scenario assumptions" in context
    assert "Derivation rows need a scenario or basis slot" in context
    assert "Do not overwrite an initial baseline with a later actual value" in context
    assert "event_measurement/4" in context
    assert "not replacements for the direct value surface" in context
    assert "participant statements need direct statement surfaces" in context
    assert "share a stable statement id or source anchor" in context
    assert "Do not preserve only formal public comments" in context
    assert "operational record/status events" in context
    assert "event or record id, governed subject/item/application" in context
    assert "status before and after when stated" in context
    assert "operational lifecycle compiles should prefer stable phase and event surfaces" in context
    assert "repeated lifecycle/status source lines require parallel preservation" in context
    assert "subject, lifecycle state/action, and date/turn joinable" in context
    assert "two-slot status/result predicates that omit the date/event join" in context
    assert "public notices, recalls, and registry pages" in context
    assert "state-by-retailer or region-by-location distribution tables" in context
    assert "retailer-specific product restriction or carve-out" in context
    assert "source_record_cell_item/3 and source_record_cell_item_qualifier/4" in context
    assert "distributed_in_state/2, sold_at_retailer/3, product_restriction/3" in context
    assert "Do not stop at product_identity/product_form rows" in context
    assert "reuse the same product/item atoms" in context
    assert "alias/equivalence row connects them" in context
    assert "not to a single representative row item" in context
    assert "multi-value summary fields" in context
    assert "do not truncate the field to the first" in context
    assert "record_superseded_by/4" in context
    assert "Received/filed/assigned/approved/denied/withdrawn/pending/corrected/superseded/reopened/closed/current-status/transition" in context
    assert "preserve the receiving or filing actor separately from the submitter/source actor" in context
    assert "preserve the requested action/content/line item or descriptive target" in context
    assert "deterministic source-record rows are provenance, not a substitute for semantic addressability" in context
    assert "identity, role, identifier, location, current status, permission, obligation, count" in context
    assert "Do not leave the only queryable copy of such a value inside source_record_text_atom/2 or source_record_field/3" in context
    assert "source-record promotion must preserve slots, not merely copy prose" in context


def test_rule_ingestion_context_keeps_rule_composition_slot_contracts() -> None:
    context = "\n".join(RULE_INGESTION_SOURCE_COMPILER_CONTEXT_V1)

    assert "Rule composition slot contract" in context
    assert "Exceptions need governed rule, condition, and effect/scope" in context
    assert "thresholds need measure, value/unit, and governed rule" in context
    assert "fallback rules need trigger and fallback action" in context
    assert "Activation-condition anchoring rule" in context
    assert "governed rule, trigger/context, and governed subject or action" in context
    assert "Pairwise rule-relation rule" in context
    assert "higher/overriding rule, lower/overridden rule" in context

    selected = "\n".join(
        _source_compiler_context(
            domain_hint="policy rule exception threshold override precedence fallback eligibility vote quorum",
            intake_plan=None,
        )
    )

    assert "rule_ingestion_source_compiler_strategy_v1" in selected
    assert "Rule composition slot contract" in selected


def test_profile_delivery_context_targets_dense_distribution_table_states() -> None:
    source_text = "\n".join(
        [
            "| State | Retailers |",
            "| --- | --- |",
            "| Connecticut | Walmart, Save-a-Lot |",
            "| Delaware | Walmart, Save-a-Lot |",
            "| Illinois | Walmart, Kroger |",
            "| Indiana | Walmart, Kroger |",
            "| Kentucky | Walmart, Kroger |",
            "| Maryland | Walmart, Save-a-Lot, Shop N Save |",
            "| Michigan | Walmart, Kroger, Save-a-Lot |",
            "| New Jersey | Walmart, Save-a-Lot |",
            "| Pennsylvania | Walmart; Foodland (cucumber only) |",
        ]
    )
    lines = _source_pass_profile_delivery_target_context(
        source_text=source_text,
        parsed_profile={
            "candidate_predicates": [
                {"signature": "product_retailer_in_state/3"},
                {"signature": "product_name/2"},
            ]
        },
    )

    joined = "\n".join(lines)
    assert "dense distribution/state table" in joined
    assert "ct, de, il, in, ky, md, mi, nj, pa" in joined
    assert "product_retailer_in_state/3" in joined
    assert "Do not stop at a prefix of the table" in joined
    assert "Late rows such as" in joined
    assert "pa" in joined


def test_fiction_reference_context_keeps_story_layer_boundaries() -> None:
    context = "\n".join(FICTION_REFERENCE_CONTAINMENT_CONTEXT_V1)

    assert "fictional events" in context
    assert "source layer" in context
    assert "Publication chronology" in context
    assert "Unresolved real-incident" in context

    selected = "\n".join(
        _source_compiler_context(
            domain_hint="library novel fiction story level reference containment fictional coincidence source layer",
            intake_plan=None,
        )
    )

    assert "fiction_reference_containment_strategy_v1" in selected
    assert "do not promote fictional events as real-world facts" in selected


def test_source_entity_ledger_schema_has_coverage_targets() -> None:
    assert "coverage_targets" in SOURCE_ENTITY_LEDGER_SCHEMA["required"]
    target_schema = SOURCE_ENTITY_LEDGER_SCHEMA["properties"]["coverage_targets"]["items"]
    assert target_schema["required"] == [
        "target_id",
        "lens",
        "anchor_atoms",
        "coverage_goal",
        "risk_note",
    ]
    assert "event_spine" in target_schema["properties"]["lens"]["enum"]
    assert "final_state" in target_schema["properties"]["lens"]["enum"]
    assert "causality" in target_schema["properties"]["lens"]["enum"]


def test_source_entity_ledger_is_scoped_to_narrative_lanes() -> None:
    assert _should_build_source_entity_ledger(
        intake_plan={"pass_plan": [{"purpose": "story event spine"}]},
        domain_hint="story_world",
    )
    assert _should_build_source_entity_ledger(
        intake_plan={"pass_plan": [{"purpose": "fable final state"}]},
        domain_hint="",
    )
    assert not _should_build_source_entity_ledger(
        intake_plan={"pass_plan": [{"purpose": "regulatory recall access deadlines"}]},
        domain_hint="regulatory recall ledger",
    )
    assert not _should_build_source_entity_ledger(
        intake_plan={"pass_plan": [{"purpose": "grant committee eligibility rules"}]},
        domain_hint="governance records",
    )


def test_source_entity_ledger_context_marks_partial_skeleton_as_ledger_backed() -> None:
    context = "\n".join(
        _source_entity_ledger_context(
            {
                "schema_version": "source_entity_ledger_v1",
                "canonical_atoms": [],
                "object_families": [],
                "coverage_targets": [
                    {
                        "target_id": "final_state",
                        "lens": "final_state",
                        "anchor_atoms": ["little_mole"],
                        "coverage_goal": "preserve ending state",
                        "risk_note": "palette may not express every row class",
                    }
                ],
                "alias_risks": [],
                "notes": [],
            }
        )
    )

    assert "ledger-backed narrative skeleton passes" in context
    assert "partial safe skeleton is better than rejecting the pass" in context
    assert "coverage_targets, treat them as powerless pass-coverage hints" in context


def test_append_source_record_ledger_facts_marks_deterministic_policy() -> None:
    compile_record = {"facts": ["existing_fact(alpha)."], "unique_fact_count": 1}
    ledger = {
        "rows": [
            {
                "row_id": "src_line_0007",
                "kind": "labeled_line",
                "line": 7,
                "section": "Evidence",
                "exact": "Memo LAB4C-MEM-2026-04-22 states a row.",
                "label": "LAB4C-MEM-2026-04-22",
            }
        ]
    }

    _append_source_record_ledger_facts(compile_record, ledger)

    assert "existing_fact(alpha)." in compile_record["facts"]
    assert "source_record_label(src_line_0007, lab4c_mem_2026_04_22)." in compile_record["facts"]
    assert compile_record["unique_fact_count"] == len(compile_record["facts"])
    assert compile_record["deterministic_source_record_fact_count"] > 0
    assert compile_record["deterministic_source_record_policy"]["not_semantic_truth"] is True


def test_append_entity_id_closure_facts_from_admitted_direct_rows() -> None:
    compile_record = {
        "facts": [
            "event_recorded(ev_11, sys_d, 2026_04_22_15_15, operator_note).",
            "event_type(ev_12, off_spec_flag).",
            "source_record_field(src_line_1, event_id, ev_13).",
            "system_time_source(sys_a, internal_rtc).",
            "event_id(ev_10).",
        ],
        "unique_fact_count": 5,
    }
    profile = {
        "candidate_predicates": [
            {"signature": "event_id/1"},
            {"signature": "system_id/1"},
        ]
    }

    _append_entity_id_closure_facts(compile_record, profile)

    assert "event_id(ev_11)." in compile_record["facts"]
    assert "event_id(ev_12)." in compile_record["facts"]
    assert "event_id(ev_13)." not in compile_record["facts"]
    assert "system_id(sys_a)." in compile_record["facts"]
    assert compile_record["facts"].count("event_id(ev_10).") == 1
    assert compile_record["deterministic_entity_id_closure_fact_count"] == 3
    assert compile_record["unique_fact_count"] == len(compile_record["facts"])


def test_append_source_field_id_facts_from_exact_allowed_id_header() -> None:
    compile_record = {
        "facts": [
            "source_record_field(src_line_1, event_id, ev_13).",
            "source_record_field(src_line_2, device_id, dev_scan_07).",
            "source_record_field(src_line_3, description, ev_14).",
            "source_record_field(src_line_4, event_id, v_2026_05_01).",
        ],
        "unique_fact_count": 4,
    }
    profile = {
        "candidate_predicates": [
            {"signature": "event_id/1"},
            {"signature": "device_id/1"},
        ]
    }

    _append_source_field_id_facts(compile_record, profile)

    assert "event_id(ev_13)." in compile_record["facts"]
    assert "device_id(dev_scan_07)." in compile_record["facts"]
    assert "event_id(ev_14)." not in compile_record["facts"]
    assert "event_id(v_2026_05_01)." not in compile_record["facts"]
    assert compile_record["deterministic_source_field_id_fact_count"] == 2
    assert compile_record["unique_fact_count"] == len(compile_record["facts"])


def test_openrouter_compile_title_uses_phase_and_fixture_only(monkeypatch) -> None:
    monkeypatch.delenv("PRETHINKER_OPENROUTER_TITLE", raising=False)
    monkeypatch.delenv("OPENROUTER_APP_TITLE", raising=False)
    monkeypatch.delenv("OPENROUTER_X_TITLE", raising=False)

    title = _default_openrouter_title(Path("tmp") / "compile_run_20260514" / "fixture_a")

    assert title == "compile:fixture_a"


def test_compile_chat_headers_do_not_send_openrouter_key_to_local_lmstudio(monkeypatch) -> None:
    monkeypatch.delenv("PRETHINKER_API_KEY", raising=False)
    monkeypatch.setenv("OPENROUTER_API_KEY", "or-secret")
    monkeypatch.setenv("PRETHINKER_OPENROUTER_TITLE", "Prethinker Hosted Lane")
    monkeypatch.setenv("PRETHINKER_OPENROUTER_REFERER", "https://example.test/prethinker")

    headers = _chat_headers(base_url="http://127.0.0.1:1234")

    assert "Authorization" not in headers
    assert "HTTP-Referer" not in headers
    assert "X-Title" not in headers
    assert "X-OpenRouter-Title" not in headers


def test_source_pass_ops_schema_is_operations_only() -> None:
    assert SOURCE_PASS_OPS_JSON_SCHEMA["required"] == [
        "schema_version",
        "pass_id",
        "decision",
        "candidate_operations",
        "self_check",
    ]
    assert "entities" not in SOURCE_PASS_OPS_JSON_SCHEMA["properties"]
    assert "propositions" not in SOURCE_PASS_OPS_JSON_SCHEMA["properties"]
    assert SOURCE_PASS_OPS_JSON_SCHEMA["properties"]["candidate_operations"]["maxItems"] == 64


def test_profile_signature_roster_schema_omits_arg_roles() -> None:
    item_schema = PROFILE_SIGNATURE_ROSTER_JSON_SCHEMA["properties"]["candidate_signatures"]["items"]

    assert "candidate_signatures" in PROFILE_SIGNATURE_ROSTER_JSON_SCHEMA["required"]
    assert "args" not in item_schema["properties"]
    assert item_schema["properties"]["signature"]["pattern"] == "^[a-z][a-z0-9_]*/[1-5]$"


def test_source_pass_ops_wraps_for_normal_mapper() -> None:
    ir = _source_pass_ops_to_semantic_ir(
        {
            "schema_version": "source_pass_ops_v1",
            "pass_id": "pass_1",
            "decision": "commit",
            "candidate_operations": [
                {
                    "operation": "assert",
                    "proposition_id": "",
                    "predicate": "person_role",
                    "args": ["elena_voss", "respondent"],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                }
            ],
            "self_check": {"bad_commit_risk": "low", "missing_slots": [], "notes": ["compact pass"]},
        }
    )

    assert ir["schema_version"] == "semantic_ir_v1"
    assert ir["entities"] == []
    assert ir["propositions"] == []
    assert ir["candidate_operations"][0]["predicate"] == "person_role"
    assert ir["truth_maintenance"]["support_links"] == []
    assert ir["self_check"]["notes"] == ["compact pass"]


def test_source_pass_ops_reduces_review_atoms_to_governed_carrier() -> None:
    ir = _source_pass_ops_to_semantic_ir(
        {
            "schema_version": "source_pass_ops_v1",
            "pass_id": "pass_1",
            "decision": "commit",
            "candidate_operations": [
                {
                    "operation": "assert",
                    "proposition_id": "prop_affirmed",
                    "predicate": "affirmed_by/2",
                    "args": ["claim_set_102_rejection", "Board"],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                }
            ],
            "self_check": {"bad_commit_risk": "low", "missing_slots": [], "notes": []},
        }
    )

    operations = ir["candidate_operations"]

    assert operations[0]["predicate"] == "affirmed_by/2"
    assert operations[1] == {
        "operation": "assert",
        "proposition_id": "prop_affirmed_review_outcome",
        "predicate": "review_outcome/4",
        "args": ["claim_set_102_rejection", "Board", "affirmed", "direct"],
        "polarity": "positive",
        "source": "direct",
        "safety": "safe",
    }


def test_source_pass_ops_reduces_three_slot_event_date_to_document_date_contract() -> None:
    ir = _source_pass_ops_to_semantic_ir(
        {
            "schema_version": "source_pass_ops_v1",
            "pass_id": "profile_document_date_repair",
            "decision": "commit",
            "candidate_operations": [
                {
                    "operation": "assert",
                    "proposition_id": "evt_date_hearing",
                    "predicate": "event_date/2",
                    "args": ["docket_24_035_04", "hearing_date", "2024_12_16"],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                }
            ],
            "self_check": {"bad_commit_risk": "low", "missing_slots": [], "notes": []},
        },
        predicate_contracts=[
            {
                "signature": "document_date/3",
                "args": ["document_or_subject_id", "date_kind_or_role", "date_value"],
            },
            {
                "signature": "event_date/2",
                "args": ["event_id", "date"],
            },
        ],
    )

    operations = ir["candidate_operations"]

    assert operations[0]["predicate"] == "event_date/2"
    assert operations[1] == {
        "operation": "assert",
        "proposition_id": "evt_date_hearing_document_date",
        "predicate": "document_date/3",
        "args": ["docket_24_035_04", "hearing_date", "2024_12_16"],
        "polarity": "positive",
        "source": "direct",
        "safety": "safe",
    }


def test_source_pass_ops_completes_governed_source_scope_slots() -> None:
    contracts = [
        {
            "signature": "claim_range/4",
            "args": ["claim_set_id", "start_claim", "end_claim", "source_or_scope"],
        },
        {
            "signature": "review_outcome/4",
            "args": ["reviewed_subject_id", "reviewing_body_or_actor", "review_outcome_or_action", "source_or_scope"],
        },
    ]
    ir = _source_pass_ops_to_semantic_ir(
        {
            "schema_version": "source_pass_ops_v1",
            "pass_id": "pass_1",
            "decision": "commit",
            "candidate_operations": [
                {
                    "operation": "assert",
                    "proposition_id": "prop_range",
                    "predicate": "claim_range/4",
                    "args": ["claim_set_1", "3", "5"],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                },
                {
                    "operation": "assert",
                    "proposition_id": "prop_review",
                    "predicate": "review_outcome/4",
                    "args": ["claim_set_1", "board", "affirmed", "rejection"],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                },
            ],
            "self_check": {"bad_commit_risk": "low", "missing_slots": [], "notes": []},
        },
        predicate_contracts=contracts,
    )

    assert ir["candidate_operations"][0]["args"] == ["claim_set_1", "3", "5", "direct"]
    assert ir["candidate_operations"][1]["args"] == ["claim_set_1", "board", "affirmed", "direct"]


def test_governed_review_atom_fact_reduction_adds_review_outcome_without_source_text() -> None:
    source_compile = {
        "facts": [
            "claim_ground(claim_set_102_rejection, anticipation, reference_alpha, rejected).",
            "affirmed_by(claim_set_102_rejection, board).",
        ]
    }

    report = _apply_governed_review_atom_fact_reduction(source_compile)

    assert report == {
        "added_count": 1,
        "added_facts": [
            "review_outcome(claim_set_102_rejection, board, affirmed, direct)."
        ],
    }
    assert source_compile["facts"] == [
        "claim_ground(claim_set_102_rejection, anticipation, reference_alpha, rejected).",
        "affirmed_by(claim_set_102_rejection, board).",
        "review_outcome(claim_set_102_rejection, board, affirmed, direct).",
    ]
    assert source_compile["deterministic_governed_atom_reduction_policy"]["not_source_interpretation"] is True


def test_governed_obligation_detail_atom_reduction_extracts_schedule_atoms_only_from_typed_rows() -> None:
    source_compile = {
        "facts": [
            "obligation_detail(settlement_24_035_04, recipient_scope, customers_receiving_service_under_schedule_9, data_reporting, src_line_0013).",
            "source_record_text_atom(src_1, customers_receiving_service_under_schedule_5).",
        ]
    }

    report = _apply_governed_obligation_detail_atom_reduction(source_compile)

    assert report == {
        "added_count": 1,
        "added_facts": [
            "obligation_detail(settlement_24_035_04, tariff_schedule, schedule_9, data_reporting, src_line_0013)."
        ],
    }
    assert source_compile["facts"] == [
        "obligation_detail(settlement_24_035_04, recipient_scope, customers_receiving_service_under_schedule_9, data_reporting, src_line_0013).",
        "source_record_text_atom(src_1, customers_receiving_service_under_schedule_5).",
        "obligation_detail(settlement_24_035_04, tariff_schedule, schedule_9, data_reporting, src_line_0013).",
    ]
    assert source_compile["deterministic_obligation_detail_atom_reduction_policy"]["not_source_interpretation"] is True
    assert source_compile["deterministic_obligation_detail_atom_reduction_policy"]["not_query_interpretation"] is True

    second_report = _apply_governed_obligation_detail_atom_reduction(source_compile)

    assert second_report == {"added_count": 0, "added_facts": []}
    assert source_compile["facts"].count(
        "obligation_detail(settlement_24_035_04, tariff_schedule, schedule_9, data_reporting, src_line_0013)."
    ) == 1


def test_document_subject_atom_convergence_clones_document_level_facts_by_typed_identifier() -> None:
    source_compile = {
        "facts": [
            "document_identifier_occurrence(fed_cir_2025_1705_song, docket_number, 2025_1705, header, 1).",
            "document_date(doc_fed_cir_2025_1705, decision_date, february_18_2026).",
            "review_outcome(doc_fed_cir_2025_1705, federal_circuit, affirmed, src_line_0054).",
            "source_record_text_atom(src_1, tempting_prose).",
        ]
    }

    report = _apply_document_subject_atom_convergence(source_compile)

    assert report == {
        "added_count": 2,
        "added_facts": [
            "document_date(fed_cir_2025_1705_song, decision_date, february_18_2026).",
            "review_outcome(fed_cir_2025_1705_song, federal_circuit, affirmed, src_line_0054).",
        ],
    }
    assert report["added_facts"][0] in source_compile["facts"]
    assert report["added_facts"][1] in source_compile["facts"]
    assert not any(fact.startswith("source_record") and fact != "source_record_text_atom(src_1, tempting_prose)." for fact in source_compile["facts"])
    assert source_compile["deterministic_document_subject_atom_convergence_policy"]["not_source_interpretation"] is True
    assert source_compile["deterministic_document_subject_atom_convergence_policy"]["not_query_interpretation"] is True


def test_document_subject_atom_convergence_does_not_use_related_or_single_number_identifiers() -> None:
    source_compile = {
        "facts": [
            "document_identifier_occurrence(fed_cir_2025_1705_song, related_case_number, 2025_1653, related_case, 1).",
            "document_identifier_occurrence(fed_cir_2025_1705_song, joint_appendix_docket_number, 24, footnote, 2).",
            "document_date(doc_fed_cir_2025_1705, decision_date, february_18_2026).",
        ]
    }

    report = _apply_document_subject_atom_convergence(source_compile)

    assert report == {"added_count": 0, "added_facts": []}
    assert "document_date(fed_cir_2025_1705_song, decision_date, february_18_2026)." not in source_compile["facts"]


def test_governed_claim_ground_atom_reduction_splits_statute_from_theory() -> None:
    source_compile = {
        "facts": [
            "claim_ground(claim_set_alpha, 102_a_1, reference_alpha, anticipated).",
            "claim_ground(claim_set_beta, 103, reference_beta, obvious).",
        ]
    }

    report = _apply_governed_claim_ground_atom_reduction(source_compile)

    assert report["added_count"] == 4
    assert "claim_ground(claim_set_alpha, anticipation, reference_alpha, rejected)." in source_compile["facts"]
    assert "legal_citation_detail(claim_set_alpha, section_102_a_1, statutory_ground, direct)." in source_compile["facts"]
    assert "claim_ground(claim_set_beta, obviousness, reference_beta, rejected)." in source_compile["facts"]
    assert "legal_citation_detail(claim_set_beta, section_103, statutory_ground, direct)." in source_compile["facts"]
    assert source_compile["deterministic_claim_ground_atom_reduction_policy"]["not_source_interpretation"] is True


def test_governed_reference_citation_atom_reduction_normalizes_abbreviations() -> None:
    source_compile = {
        "facts": [
            "claim_ground(claim_set_alpha, anticipation, ref_alpha, rejected).",
            "legal_citation_detail(claim_set_alpha, sec_102a1, statutory_ground, src_line_0005).",
            "legal_citation_detail(claim_set_beta, sec_103, statutory_ground, src_line_0009).",
            "legal_citation_detail(claim_set_gamma, sec_103, obviousness, src_line_0009).",
        ]
    }

    report = _apply_governed_reference_citation_atom_reduction(source_compile)

    assert report["added_count"] == 4
    assert "claim_ground(claim_set_alpha, anticipation, reference_alpha, rejected)." in source_compile["facts"]
    assert "legal_citation_detail(claim_set_alpha, section_102_a_1, statutory_ground, src_line_0005)." in source_compile["facts"]
    assert "legal_citation_detail(claim_set_beta, section_103, statutory_ground, src_line_0009)." in source_compile["facts"]
    assert "legal_citation_detail(claim_set_gamma, section_103, statutory_ground, src_line_0009)." in source_compile["facts"]
    assert source_compile["deterministic_reference_citation_atom_reduction_policy"]["not_query_interpretation"] is True


def test_governed_reference_citation_atom_reduction_normalizes_governed_atom_synonyms() -> None:
    source_compile = {
        "facts": [
            "claim_ground(set_alpha, anticipated, ref_alpha, rejected).",
            "claim_ground(set_beta, obvious, ref_beta, rejected).",
            "legal_citation_detail(set_alpha, 102_a_1, statutory_basis, contested_claims).",
            "review_outcome(set_alpha, actor_board, affirmation_outcome, src_line_0011).",
        ]
    }

    report = _apply_governed_reference_citation_atom_reduction(source_compile)

    assert report["added_count"] == 4
    assert "claim_ground(set_alpha, anticipation, reference_alpha, rejected)." in source_compile["facts"]
    assert "claim_ground(set_beta, obviousness, reference_beta, rejected)." in source_compile["facts"]
    assert "legal_citation_detail(set_alpha, section_102_a_1, statutory_ground, contested_claims)." in source_compile["facts"]
    assert "review_outcome(set_alpha, review_board, affirmed, src_line_0011)." in source_compile["facts"]
    assert source_compile["deterministic_reference_citation_atom_reduction_policy"]["not_source_interpretation"] is True


def test_governed_reference_citation_atom_reduction_normalizes_amendment_scope() -> None:
    source_compile = {
        "facts": [
            (
                "legal_citation_detail(aod_24_102, "
                "any_further_amendments_to_the_foregoing_laws_regulations_and_rules, "
                "scope_extension, src_line_0034)."
            ),
        ]
    }

    report = _apply_governed_reference_citation_atom_reduction(source_compile)

    assert report["added_count"] == 1
    assert (
        "legal_citation_detail(aod_24_102, future_amendments_to_foregoing_laws_regulations_and_rules, "
        "amendment_scope, src_line_0034)."
        in source_compile["facts"]
    )
    assert source_compile["deterministic_reference_citation_atom_reduction_policy"]["not_source_interpretation"] is True


def test_governed_companion_subject_health_flags_missing_typed_companions() -> None:
    source_compile = {
        "facts": [
            "claim_ground(set_alpha, anticipation, reference_alpha, rejected).",
            "legal_citation_detail(set_alpha, section_102_a_1, statutory_ground, src_line_0002).",
            "review_outcome(set_alpha, review_board, affirmed, src_line_0011).",
            "claim_range(set_beta, 1, 1, src_line_0003).",
            "claim_ground(set_beta, anticipation, reference_beta, rejected).",
            "legal_citation_detail(set_beta, section_102_a_1, statutory_ground, src_line_0003).",
            "review_outcome(set_beta, review_board, affirmed, src_line_0011).",
        ]
    }

    report = _attach_governed_companion_subject_health(source_compile)

    flagged = {row["subject"]: row["missing_companions"] for row in report["rows"] if row["missing_companions"]}
    assert flagged == {"set_alpha": ["claim_range/4"]}
    alpha = next(row for row in report["rows"] if row["subject"] == "set_alpha")
    assert alpha["family_statuses"]["claim_range/4"] == "missing_unaccounted"
    assert alpha["family_statuses"]["claim_ground/4"] == "present"
    assert report["flagged_subject_count"] == 1
    assert report["omission_ledger_count"] == 1
    assert report["governed_companion_omission_ledger"] == [
        {
            "subject": "set_alpha",
            "signature": "claim_range/4",
            "status": "missing_unaccounted",
            "observed_predicates": ["claim_ground", "legal_citation_detail", "review_outcome"],
            "reason": "typed subject has at least one governed companion family but this companion family is absent",
        }
    ]
    assert report["not_source_interpretation"] is True
    assert source_compile["governed_companion_subject_health"] == report


def test_source_pass_ops_guidance_preserves_explicit_negative_surfaces(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_call(**kwargs):
        captured["messages"] = kwargs["messages"]
        return {
            "content": json.dumps(
                {
                    "schema_version": "source_pass_ops_v1",
                    "pass_id": "pass_1",
                    "decision": "commit",
                    "candidate_operations": [],
                    "self_check": {"bad_commit_risk": "low", "missing_slots": [], "notes": []},
                }
            )
        }

    monkeypatch.setattr(domain_bootstrap_file, "_call_lmstudio_json_schema", fake_call)
    args = type(
        "Args",
        (),
        {
            "base_url": "http://example.invalid/v1",
            "model": "test-model",
            "timeout": 30,
            "temperature": 0.0,
            "top_p": 1.0,
            "max_tokens": 4000,
            "domain_hint": "",
            "focused_pass_operation_target": 8,
            "focused_retry_operation_target": 4,
        },
    )()

    result = _compile_source_pass_ops(
        source_text="The review team is not allowed to approve the memo.",
        parsed_profile={
            "candidate_predicates": [
                {"signature": "is_not_allowed_to_approve/2", "args": ["agent", "document"]}
            ]
        },
        intake_plan={},
        args=args,
        pass_id="pass_1",
        purpose="negative authority",
        focus="explicit prohibitions",
        completion="preserve negative surfaces",
        predicates="is_not_allowed_to_approve/2",
        coverage_goals="not-allowed role rows",
    )

    assert result["ok"] is True
    user_message = next(item for item in captured["messages"] if item["role"] == "user")
    assert "Explicit negative-surface preservation rule" in user_message["content"]
    assert "positive assertion on a compatible prohibition/forbidden/exempt/outside-scope/lacks-authority predicate" in user_message["content"]
    assert "Target-anchor preservation rule" in user_message["content"]
    assert "Object-vs-actor attachment rule" in user_message["content"]


def test_source_pass_ops_guidance_includes_compile_surface_invariants(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_call(**kwargs):
        captured["messages"] = kwargs["messages"]
        return {
            "content": json.dumps(
                {
                    "schema_version": "source_pass_ops_v1",
                    "pass_id": "pass_1",
                    "decision": "commit",
                    "candidate_operations": [],
                    "self_check": {"bad_commit_risk": "low", "missing_slots": [], "notes": []},
                }
            )
        }

    monkeypatch.setattr(domain_bootstrap_file, "_call_lmstudio_json_schema", fake_call)
    args = type(
        "Args",
        (),
        {
            "base_url": "http://example.invalid/v1",
            "model": "test-model",
            "timeout": 30,
            "temperature": 0.0,
            "top_p": 1.0,
            "max_tokens": 4000,
            "domain_hint": "",
            "focused_pass_operation_target": 8,
            "focused_retry_operation_target": 4,
        },
    )()

    result = _compile_source_pass_ops(
        source_text="Section 4 says the recorder logged two corrected sensor readings.",
        parsed_profile={
            "candidate_predicates": [
                {"signature": "section_title/2", "args": ["section", "title"]},
                {"signature": "corrected_reading/4", "args": ["sensor", "time", "value", "recorder"]},
            ]
        },
        intake_plan={},
        args=args,
        pass_id="pass_1",
        purpose="surface invariant",
        focus="source addressability and corrected readings",
        completion="preserve direct surfaces",
        predicates="section_title/2, corrected_reading/4",
        coverage_goals="direct source coordinates and measurement correction rows",
    )

    assert result["ok"] is True
    assert "compile_surface_invariant_strategy_v1" in "\n".join(COMPILE_SURFACE_INVARIANT_CONTEXT_V1)
    user_message = next(item for item in captured["messages"] if item["role"] == "user")
    assert "compile_surface_invariant_strategy_v1" in user_message["content"]
    assert "source addressability as queryable rows" in user_message["content"]
    assert "relation between the subject id and the section/source coordinate" in user_message["content"]
    assert "authority/source relation separately from the party receiving permission" in user_message["content"]
    assert "source document id, source actor/author" in user_message["content"]
    assert "provenance slot contract directly" in user_message["content"]
    assert "preparer/presenter/submitter/filer/commissioner" in user_message["content"]
    assert "rule-composition slot contract directly" in user_message["content"]
    assert "Unanchored condition-only, priority-only, quorum-only" in user_message["content"]
    assert "preserve the activation anchor directly" in user_message["content"]
    assert "A rule label that merely contains the trigger words is not enough" in user_message["content"]
    assert "preserve the pairwise relation directly" in user_message["content"]
    assert "Rank-only priority labels are shallow" in user_message["content"]
    assert "state-by-retailer or region-by-location distribution tables" in user_message["content"]
    assert "source_record_cell_item/3 and source_record_cell_item_qualifier/4" in user_message["content"]
    assert "reuse the same product/item atoms" in user_message["content"]
    assert "Candidate predicate names are not enough" in user_message["content"]


def test_pass_surface_contribution_counts_unique_rows_in_order() -> None:
    rows = _pass_surface_contribution(
        [
            {
                "pass_id": "p1",
                "facts": ["a(1).", "b(2)."],
                "rules": ["r(X) :- a(X)."],
                "queries": [],
                "admitted_count": 3,
                "skipped_count": 0,
            },
            {
                "pass_id": "p2",
                "facts": ["b(2).", "c(3)."],
                "rules": ["r(X) :- a(X)."],
                "queries": ["c(X)."],
                "admitted_count": 4,
                "skipped_count": 1,
            },
        ]
    )

    assert rows[0]["unique_contribution_count"] == 3
    assert rows[0]["duplicate_count"] == 0
    assert rows[1]["unique_contribution_count"] == 2
    assert rows[1]["duplicate_count"] == 2
    assert rows[1]["unique_contribution_ratio"] == 0.5
    assert rows[1]["health_flags"] == ["thin_surface"]


def test_flat_plus_surface_contribution_treats_flat_pass_as_seen() -> None:
    rows = _flat_plus_surface_contribution(
        flat={"facts": ["a(1).", "b(2)."], "rules": [], "queries": [], "admitted_count": 2, "skipped_count": 0},
        focused={
            "passes": [
                {
                    "pass_id": "p1",
                    "facts": ["b(2).", "c(3)."],
                    "rules": [],
                    "queries": [],
                    "admitted_count": 2,
                    "skipped_count": 0,
                }
            ]
        },
    )

    assert rows[0]["pass_id"] == "flat_skeleton"
    assert rows[0]["unique_contribution_count"] == 2
    assert rows[1]["pass_id"] == "p1"
    assert rows[1]["unique_contribution_count"] == 1
    assert rows[1]["duplicate_count"] == 1
    assert "thin_surface" in rows[1]["health_flags"]


def test_flat_plus_surface_contribution_discounts_rejected_flat_diagnostic() -> None:
    rows = _flat_plus_surface_contribution(
        flat={
            "projected_decision": "reject",
            "facts": [],
            "rules": [],
            "queries": [],
            "admitted_count": 0,
            "skipped_count": 64,
        },
        focused={
            "admitted_count": 98,
            "skipped_count": 4,
            "passes": [
                {
                    "pass_id": "p1",
                    "facts": ["sensor_observation(ev_01, sensor_a, humidity, v_62)."],
                    "rules": [],
                    "queries": [],
                    "admitted_count": 98,
                    "skipped_count": 4,
                }
            ],
        },
    )

    assert rows[0]["pass_id"] == "flat_skeleton"
    assert rows[0]["skipped_count"] == 64
    assert rows[0]["effective_skipped_count"] == 0
    assert rows[0]["diagnostic_flags"] == ["rejected_projection_diagnostic"]
    assert rows[0]["health_flags"] == []


def test_pass_surface_contribution_flags_zero_and_skip_heavy_passes() -> None:
    rows = _pass_surface_contribution(
        [
            {"pass_id": "failed", "ok": False, "facts": [], "rules": [], "queries": []},
            {
                "pass_id": "skip_heavy",
                "ok": True,
                "facts": ["a(1)."],
                "rules": [],
                "queries": [],
                "admitted_count": 1,
                "skipped_count": 9,
            },
        ]
    )

    assert rows[0]["health_flags"] == ["pass_not_ok", "zero_yield"]
    assert "thin_surface" in rows[1]["health_flags"]
    assert "skip_heavy" in rows[1]["health_flags"]


def test_compile_health_summary_classifies_pass_surface() -> None:
    healthy = _compile_health_summary(
        [
            {
                "pass_id": "p1",
                "unique_contribution_count": 10,
                "duplicate_count": 1,
                "health_flags": [],
            }
        ]
    )
    warning = _compile_health_summary(
        [
            {
                "pass_id": "p1",
                "unique_contribution_count": 2,
                "duplicate_count": 0,
                "health_flags": ["thin_surface"],
            }
        ]
    )
    poor = _compile_health_summary(
        [
            {
                "pass_id": "p1",
                "unique_contribution_count": 0,
                "duplicate_count": 0,
                "health_flags": ["pass_not_ok", "zero_yield"],
            }
        ]
    )
    skip_warning = _compile_health_summary(
        [
            {
                "pass_id": "p1",
                "unique_contribution_count": 10,
                "duplicate_count": 1,
                "health_flags": [],
            },
            {
                "pass_id": "p2",
                "unique_contribution_count": 5,
                "duplicate_count": 2,
                "health_flags": ["skip_heavy"],
            },
        ]
    )

    assert healthy["verdict"] == "healthy"
    assert healthy["recommendation"] == "qa_run_reasonable"
    assert healthy["semantic_progress"]["zombie_risk"] == "low"
    assert warning["verdict"] == "warning"
    assert warning["recommendation"] == "run_qa_but_treat_thin_lens_results_as_diagnostic"
    assert warning["semantic_progress"]["recommended_action"] == "continue_only_with_named_expected_contribution"
    assert poor["verdict"] == "poor"
    assert poor["recommendation"] == "repair_compile_before_qa"
    assert poor["semantic_progress"]["recommended_action"] == "stop_and_report_struggle"
    assert poor["flag_counts"]["zero_yield"] == 1
    assert poor["unhealthy_passes"] == ["p1"]
    assert skip_warning["verdict"] == "warning"
    assert skip_warning["recommendation"] == "run_qa_but_treat_thin_lens_results_as_diagnostic"
    assert skip_warning["semantic_progress"]["zombie_risk"] == "medium"


def test_profile_admission_flags_shallow_operational_lifecycle_palette() -> None:
    report = _profile_admission_report(
        source_text=(
            "On 2026-03-01 record R-1 was filed with status pending.\n"
            "On 2026-03-04 record R-1 was closed as approved."
        ),
        parsed_profile={
            "candidate_predicates": [
                {"signature": "record_status/2", "args": ["record_id", "status"]},
                {"signature": "event_date/3", "args": ["record_id", "event_type", "date"]},
            ]
        },
    )

    assert report["source_signal_counts"]["operational_lifecycle"] == 2
    assert report["candidate_contract_counts"]["operational_lifecycle_capable"] == 0
    assert report["findings"][0]["class"] == "shallow_lifecycle_palette"


def test_profile_admission_flags_shallow_quantity_event_palette() -> None:
    report = _profile_admission_report(
        source_text=(
            "EV-01 2026-04-22 feed rate increased to 18 kg min.\n"
            "EV-02 2026-04-22 setpoint changed from 480 k to 495 k."
        ),
        parsed_profile={
            "candidate_predicates": [
                {"signature": "event_record/3", "args": ["event_id", "source", "timestamp"]},
                {"signature": "event_description/2", "args": ["event_id", "description"]},
            ]
        },
    )

    assert report["source_signal_counts"]["quantity_event"] == 2
    assert report["quantity_event_required_carrier_row_count"] == 3
    assert report["candidate_contract_counts"]["quantity_event_capable"] == 0
    assert report["findings"][0]["class"] == "shallow_quantity_event_palette"


def test_profile_bootstrap_admission_context_guides_operational_status_palettes() -> None:
    context = _profile_bootstrap_admission_context(
        intake_plan=None,
        domain_hint="grant queue proposal status lifecycle",
    )
    joined = "\n".join(context)

    assert "complete status-at-date or lifecycle-event shape" in joined
    assert "subject, state/action/result, and date/source together" in joined
    assert "status_changed_on/2" in joined


def test_profile_bootstrap_admission_context_guides_quantity_event_palettes() -> None:
    context = _profile_bootstrap_admission_context(
        intake_plan=None,
        domain_hint="sensor measurement rate threshold values",
    )
    joined = "\n".join(context)

    assert "direct quantity-bearing event/record shape" in joined
    assert "event_description/2" in joined
    assert "numeric event details" in joined


def test_profile_bootstrap_admission_context_guides_status_state_palettes() -> None:
    context = _profile_bootstrap_admission_context(
        intake_plan=None,
        domain_hint="current status point-in-time partial population state",
    )
    joined = "\n".join(context)

    assert "direct status/state surface" in joined
    assert "subject or subset, state/status value, and temporal/source scope" in joined
    assert "status/2" in joined


def test_profile_admission_retry_context_names_complete_status_shapes() -> None:
    context = _profile_admission_retry_context(
        {
            "findings": [
                {
                    "class": "shallow_lifecycle_palette",
                    "nearby_signatures": ["proposal_status/2", "status_changed_on/2"],
                }
            ]
        }
    )
    joined = "\n".join(context)

    assert "PROFILE ADMISSION RETRY" in joined
    assert "proposal_status_at/3" in joined
    assert "proposal_status/2" in joined


def test_profile_admission_retry_context_names_complete_status_state_shapes() -> None:
    context = _profile_admission_retry_context(
        {
            "findings": [
                {
                    "class": "shallow_status_state_palette",
                    "nearby_signatures": ["entity_status/2", "effective_date/2"],
                }
            ]
        }
    )
    joined = "\n".join(context)

    assert "shallow_status_state_palette" in joined
    assert "status_state_at/4" in joined
    assert "entity_status/2" in joined


def test_profile_admission_retry_context_names_complete_source_claim_shapes() -> None:
    context = _profile_admission_retry_context(
        {
            "findings": [
                {
                    "class": "shallow_source_attributed_claim_palette",
                    "nearby_signatures": ["source_note/2", "statement/2"],
                }
            ]
        }
    )
    joined = "\n".join(context)

    assert "shallow_source_attributed_claim_palette" in joined
    assert "source_attributed_claim/4" in joined
    assert "source_note/2" in joined


def test_profile_admission_retry_context_names_quantity_event_shapes() -> None:
    context = _profile_admission_retry_context(
        {
            "findings": [
                {
                    "class": "shallow_quantity_event_palette",
                    "nearby_signatures": ["event_description/2"],
                }
            ]
        }
    )
    joined = "\n".join(context)

    assert "event_measurement/4" in joined
    assert "event/record/reading id" in joined
    assert "event_description/2" in joined


def test_profile_admission_accepts_complete_operational_lifecycle_palette() -> None:
    report = _profile_admission_report(
        source_text=(
            "On 2026-03-01 permit P-1 status was pending.\n"
            "On 2026-03-04 permit P-1 status was approved."
        ),
        parsed_profile={
            "candidate_predicates": [
                {"signature": "permit_status_at/3", "args": ["permit_file", "date", "status"]},
            ]
        },
    )

    assert report["candidate_contract_counts"]["operational_lifecycle_capable"] == 1
    assert report["findings"] == []


def test_profile_admission_flags_shallow_status_state_palette() -> None:
    report = _profile_admission_report(
        source_text=(
            "On 2026-09-15 record alpha status was suspect.\n"
            "On 2026-09-20 record beta status was cleared."
        ),
        parsed_profile={
            "candidate_predicates": [
                {"signature": "record_status/2", "args": ["record_id", "status"]},
                {"signature": "status_date/2", "args": ["record_id", "date"]},
            ]
        },
    )

    assert report["source_signal_counts"]["status_state"] == 2
    assert report["candidate_contract_counts"]["status_state_capable"] == 0
    assert "shallow_status_state_palette" in {finding["class"] for finding in report["findings"]}


def test_profile_admission_flags_shallow_source_attributed_claim_palette() -> None:
    report = _profile_admission_report(
        source_text=(
            "Rivera memo says device alpha status is active.\n"
            "Field report notes claim beta remains unresolved."
        ),
        parsed_profile={
            "candidate_predicates": [
                {"signature": "source_note/2", "args": ["source_id", "text"]},
                {"signature": "claim_status/2", "args": ["claim_id", "status"]},
            ]
        },
    )

    assert report["source_signal_counts"]["source_attributed_claim"] == 2
    assert report["candidate_contract_counts"]["source_attributed_claim_capable"] == 0
    assert "shallow_source_attributed_claim_palette" in {finding["class"] for finding in report["findings"]}


def test_profile_admission_accepts_complete_source_attributed_claim_palette() -> None:
    report = _profile_admission_report(
        source_text=(
            "Rivera memo says device alpha status is active.\n"
            "Field report notes claim beta remains unresolved."
        ),
        parsed_profile={
            "candidate_predicates": [
                {
                    "signature": "source_attributed_claim/4",
                    "args": ["claim_id", "source_document", "content_status", "source_row"],
                },
            ]
        },
    )

    assert report["candidate_contract_counts"]["source_attributed_claim_capable"] == 1
    assert report["findings"] == []


def test_source_attributed_claim_does_not_satisfy_status_state_palette() -> None:
    report = _profile_admission_report(
        source_text=(
            "On 2026-09-15 record alpha status was suspect.\n"
            "On 2026-09-20 record beta status was cleared."
        ),
        parsed_profile={
            "candidate_predicates": [
                {
                    "signature": "source_attributed_claim/4",
                    "args": ["claim_id", "source_document", "content_status", "source_row"],
                },
            ]
        },
    )

    assert report["candidate_contract_counts"]["source_attributed_claim_capable"] == 1
    assert report["candidate_contract_counts"]["status_state_capable"] == 0
    assert "shallow_status_state_palette" in {finding["class"] for finding in report["findings"]}


def test_source_authority_does_not_satisfy_source_attributed_claim_palette() -> None:
    report = _profile_admission_report(
        source_text=(
            "Rivera memo says device alpha status is active.\n"
            "Field report notes claim beta remains unresolved."
        ),
        parsed_profile={
            "candidate_predicates": [
                {
                    "signature": "source_authority/3",
                    "args": ["subject_id", "authority_or_source", "scope_or_action"],
                },
            ]
        },
    )

    assert report["candidate_contract_counts"]["source_authority_capable"] == 1
    assert report["candidate_contract_counts"]["source_attributed_claim_capable"] == 0
    assert "shallow_source_attributed_claim_palette" in {finding["class"] for finding in report["findings"]}


def test_status_note_arg_does_not_make_source_claim_carrier() -> None:
    report = _profile_admission_report(
        parsed_profile={
            "candidate_predicates": [
                {
                    "signature": "voided_draft/3",
                    "args": ["lease_ref", "draft_id", "status_note"],
                }
            ]
        },
        source_text=(
            "Corr note says this draft status is voided and has no legal effect.\n"
            "Navarro letter of intent is under review and is not binding."
        ),
    )

    assert report["candidate_contract_counts"]["source_attributed_claim_capable"] == 0
    assert "shallow_source_attributed_claim_palette" in {finding["class"] for finding in report["findings"]}


def test_profile_admission_keys_source_claim_requirements() -> None:
    report = _profile_admission_report(
        parsed_profile={
            "candidate_predicates": [
                {
                    "signature": "source_attributed_claim/4",
                    "args": ["claim_id", "source_or_speaker", "content_or_status", "source_row_or_scope"],
                }
            ]
        },
        source_text=(
            "Corr note says this draft status is voided and has no legal effect.\n"
            "Navarro letter of intent is under review and is not binding."
        ),
    )

    assert report["source_attributed_claim_required_keys"] == [
        "note:draft:no_effect",
        "letter_of_intent:letter_of_intent:not_binding",
    ]


def test_profile_admission_keys_speaker_framed_source_claims() -> None:
    report = _profile_admission_report(
        parsed_profile={
            "candidate_predicates": [
                {
                    "signature": "source_attributed_claim/4",
                    "args": ["claim_id", "source_or_speaker", "content_or_status", "source_row_or_scope"],
                }
            ]
        },
        source_text=(
            'Margaux Duvall says: "The tin trade in Entry 8 should not be flagged."\n'
            '**Kowalski:** "That is not what the code says. It says void."\n'
            'Vasquez notes: "This is my professional opinion, not a legal determination."\n'
        ),
    )

    assert report["source_attributed_claim_required_keys"] == [
        "statement:claim:not_flagged",
        "statement:claim:voided",
        "opinion:claim:not_legal_determination",
    ]


def test_profile_admission_distinguishes_architect_documentation_claims_from_permit_records() -> None:
    source_text = (
        'Panel Member says: "I disagree. No documentation from the architect has been submitted."\n'
        "Staff note says no record of the separate permit has been issued."
    )
    report = _profile_admission_report(
        parsed_profile={
            "candidate_predicates": [
                {
                    "signature": "source_attributed_claim/4",
                    "args": ["claim_id", "source_or_speaker", "content_or_status", "source_row_or_scope"],
                }
            ]
        },
        source_text=source_text,
    )

    assert "statement:architect_documentation:no_documentation" in report["source_attributed_claim_required_keys"]

    source_compile = {
        "unique_fact_count": 1,
        "facts": [
            "source_attributed_claim(staff_note, staff, no_record_of_the_separate_permit_has_been_issued, section_a).",
        ],
    }
    delivery = domain_bootstrap_file._profile_delivery_report(
        source_compile=source_compile,
        parsed_profile={
            "candidate_predicates": [
                {
                    "signature": "source_attributed_claim/4",
                    "args": ["claim_id", "source_or_speaker", "content_or_status", "source_row_or_scope"],
                }
            ]
        },
        admission_report=report,
        source_text=source_text,
    )

    finding = delivery["findings"][0]
    assert finding["class"] == "source_claim_carrier_partially_delivered"
    assert "statement:architect_documentation:no_documentation" in finding["missing_signal_keys"]


def test_profile_admission_speaker_frames_do_not_promote_admin_headings() -> None:
    report = _profile_admission_report(
        parsed_profile={
            "candidate_predicates": [
                {
                    "signature": "source_attributed_claim/4",
                    "args": ["claim_id", "source_or_speaker", "content_or_status", "source_row_or_scope"],
                }
            ]
        },
        source_text=(
            "**Post-hearing development 4 (May 10, 2026):** Marchetti applies for a "
            "Home Occupation Permit under Chapter 18. The application is pending."
        ),
    )

    assert report["source_attributed_claim_required_keys"] == []


def test_profile_admission_does_not_treat_admin_draft_lifecycle_as_source_claim() -> None:
    report = _profile_admission_report(
        parsed_profile={
            "candidate_predicates": [
                {
                    "signature": "source_attributed_claim/4",
                    "args": ["claim_id", "source_or_speaker", "content_or_status", "source_row_or_scope"],
                },
                {
                    "signature": "record_status_at/3",
                    "args": ["record_id", "status", "date"],
                },
            ]
        },
        source_text=(
            "On April 11, 2026, the project manager prepared a draft amendment proposing a "
            "classification change while retaining the 22\" DBH measurement. The draft was withdrawn on April 14, 2026 when the certified "
            "report superseded the draft. Dr. Tahir's certified report remained the operative basis.\n"
            "\"The actual-knowledge question is not resolved on this record,\" the email said."
        ),
    )

    assert report["source_attributed_claim_required_keys"] == ["email:claim:unresolved"]


def test_profile_admission_ignores_federal_register_authority_metadata_as_source_claim() -> None:
    source_text = "\n".join(
        [
            "**A Rule by the Federal Labor Relations Authority on 03/26/2024**",
            "| Agency | Federal Labor Relations Authority |",
            "## Federal Labor Relations Authority",
            "1. The authority citation for part 2471 continues to read as follows:",
            "Authority: 5 U.S.C. 7119, 7134.",
            "Issuing organization: Federal Labor Relations Authority - Federal Service Impasses Panel",
        ]
    )
    report = _profile_admission_report(
        parsed_profile={
            "candidate_predicates": [
                {
                    "signature": "source_attributed_claim/4",
                    "args": ["claim_id", "source_or_speaker", "content_or_status", "source_row_or_scope"],
                },
                {
                    "signature": "statutory_authority/2",
                    "args": ["cfr_part", "statute"],
                },
            ]
        },
        source_text=source_text,
    )

    assert report["source_signal_counts"]["source_attributed_claim"] == 0
    assert report["source_attributed_claim_required_keys"] == []
    authority_mentions = domain_bootstrap_file._source_authority_mentions(source_text)
    assert "| Agency |" not in "\n".join(authority_mentions)
    assert "Issuing organization" not in "\n".join(authority_mentions)


def test_profile_delivery_accepts_statutory_authority_as_authority_carrier() -> None:
    source_compile = {
        "unique_fact_count": 2,
        "facts": [
            "statutory_authority(5_cfr_2471, 5_u_s_c_7119).",
            "statutory_authority(5_cfr_2472, 5_u_s_c_6131).",
        ],
        "compile_health": {
            "schema_version": "compile_lens_health_v1",
            "verdict": "healthy",
            "recommendation": "qa_run_reasonable",
            "pass_count": 1,
            "unhealthy_pass_count": 0,
            "unhealthy_passes": [],
            "flag_counts": {},
            "unique_contribution_total": 2,
            "duplicate_total": 0,
            "semantic_progress": {"zombie_risk": "low", "recommended_action": "continue"},
        },
    }

    parsed_profile = {
        "candidate_predicates": [
            {
                "signature": "statutory_authority/2",
                "args": ["cfr_part", "statute"],
            }
        ]
    }
    source_text = "\n".join(
        [
            "Authority: 5 U.S.C. 7119.",
            "Authority: 5 U.S.C. 6131.",
        ]
    )
    admission_report = _profile_admission_report(
        parsed_profile=parsed_profile,
        source_text=source_text,
    )
    delivery = domain_bootstrap_file._profile_delivery_report(
        source_text="\n".join(
            [
                "Authority: 5 U.S.C. 7119.",
                "Authority: 5 U.S.C. 6131.",
            ]
        ),
        parsed_profile=parsed_profile,
        admission_report=admission_report,
        source_compile=source_compile,
    )

    assert delivery["findings"] == []
    assert delivery["delivered_carriers"]["source_authority"] == ["statutory_authority"]


def test_source_authority_extension_recognizes_authorization_act_rules() -> None:
    profile = {"candidate_predicates": [], "provenance_sensitive_predicates": [], "self_check": {"notes": []}}

    metadata = _ensure_source_authority_predicate(
        profile,
        source_text=(
            "Under the Field Safety Authorization Act of 2010, regulated equipment "
            "safety examinations are required once every 5 years."
        ),
    )

    assert metadata["added"] is True
    assert any(item["signature"] == "source_authority/3" for item in profile["candidate_predicates"])


def test_profile_delivery_accepts_status_state_carrier() -> None:
    source_compile = {
        "unique_fact_count": 1,
        "facts": [
            "asset_state(asset_alpha, unattended, 2023_03_19_to_2023_03_21).",
        ],
        "compile_health": {
            "schema_version": "compile_lens_health_v1",
            "verdict": "healthy",
            "recommendation": "qa_run_reasonable",
            "pass_count": 1,
            "unhealthy_pass_count": 0,
            "unhealthy_passes": [],
            "flag_counts": {},
            "unique_contribution_total": 1,
            "duplicate_total": 0,
            "semantic_progress": {"zombie_risk": "low", "recommended_action": "continue"},
        },
    }

    parsed_profile = {
        "candidate_predicates": [
            {
                "signature": "asset_state/3",
                "args": ["asset_id", "state", "time_or_context"],
            }
        ]
    }
    source_text = "The asset remained unattended at the remote site until March 21, 2023."
    admission_report = _profile_admission_report(
        parsed_profile=parsed_profile,
        source_text=source_text,
    )
    delivery = domain_bootstrap_file._profile_delivery_report(
        source_text=source_text,
        parsed_profile=parsed_profile,
        admission_report=admission_report,
        source_compile=source_compile,
    )

    assert delivery["findings"] == []
    assert delivery["delivered_carriers"]["status_state"] == ["asset_state"]


def test_profile_admission_keeps_real_stated_status_claim_pressure() -> None:
    report = _profile_admission_report(
        parsed_profile={
            "candidate_predicates": [
                {
                    "signature": "source_attributed_claim/4",
                    "args": ["claim_id", "source_or_speaker", "content_or_status", "source_row_or_scope"],
                }
            ]
        },
        source_text=(
            "As the operator and assistant attempted to restart the equipment on March 16, "
            "a control fault prevented the equipment from moving. The equipment remained "
            "offline with no one remaining on site to monitor its status. The operator "
            "returned to the equipment on March 19. He stated that the equipment was in "
            "good condition at the time, with no damage noted before he departed again."
        ),
    )

    assert report["source_attributed_claim_required_keys"] == ["source:claim:status"]


def test_profile_admission_accepts_complete_status_state_palette() -> None:
    report = _profile_admission_report(
        source_text=(
            "On 2026-09-15 record alpha status was suspect.\n"
            "On 2026-09-20 record beta status was cleared."
        ),
        parsed_profile={
            "candidate_predicates": [
                {"signature": "record_status_at/3", "args": ["record_id", "status", "date"]},
            ]
        },
    )

    assert report["candidate_contract_counts"]["status_state_capable"] == 1
    assert report["findings"] == []


def test_profile_admission_accepts_complete_quantity_event_palette() -> None:
    report = _profile_admission_report(
        source_text=(
            "EV-01 2026-04-22 feed rate increased to 18 kg min.\n"
            "EV-02 2026-04-22 setpoint changed from 480 k to 495 k."
        ),
        parsed_profile={
            "candidate_predicates": [
                {
                    "signature": "event_measurement/4",
                    "args": ["event_id", "measure", "value", "unit"],
                },
            ]
        },
    )

    assert report["candidate_contract_counts"]["quantity_event_capable"] == 1
    assert report["findings"] == []


def test_profile_admission_warning_updates_compile_health() -> None:
    source_compile = {
        "unique_fact_count": 5,
        "compile_health": {
            "schema_version": "compile_lens_health_v1",
            "verdict": "healthy",
            "recommendation": "qa_run_reasonable",
            "pass_count": 1,
            "unhealthy_pass_count": 0,
            "unhealthy_passes": [],
            "flag_counts": {},
            "unique_contribution_total": 5,
            "duplicate_total": 0,
            "semantic_progress": {"zombie_risk": "low", "recommended_action": "continue"},
        },
    }

    _attach_profile_admission_report(
        source_compile=source_compile,
        domain_hint="operational record status lifecycle",
        source_text=(
            "On 2026-03-01 record R-1 status was pending.\n"
            "On 2026-03-04 record R-1 status was approved."
        ),
        parsed_profile={
            "candidate_predicates": [
                {"signature": "record_status/2", "args": ["record_id", "status"]},
                {"signature": "event_date/3", "args": ["record_id", "event_type", "date"]},
            ]
        },
    )

    health = source_compile["compile_health"]
    assert health["verdict"] == "warning"
    assert health["recommendation"] == "run_qa_but_treat_thin_lens_results_as_diagnostic"
    assert health["flag_counts"]["shallow_lifecycle_palette"] == 1
    assert "profile_admission" in health["unhealthy_passes"]


def test_profile_delivery_flags_offered_status_state_carrier_without_emitted_rows() -> None:
    source_compile = {
        "unique_fact_count": 2,
        "facts": [
            "record_status(record_alpha, suspect).",
            "record_status(record_beta, cleared).",
        ],
        "compile_health": {
            "schema_version": "compile_lens_health_v1",
            "verdict": "healthy",
            "recommendation": "qa_run_reasonable",
            "pass_count": 1,
            "unhealthy_pass_count": 0,
            "unhealthy_passes": [],
            "flag_counts": {},
            "unique_contribution_total": 2,
            "duplicate_total": 0,
            "semantic_progress": {"zombie_risk": "low", "recommended_action": "continue"},
        },
    }

    _attach_profile_admission_report(
        source_compile=source_compile,
        domain_hint="point-in-time status/state",
        source_text=(
            "On 2026-09-15 record alpha status was suspect.\n"
            "On 2026-09-20 record beta status was cleared."
        ),
        parsed_profile={
            "candidate_predicates": [
                {"signature": "record_status_at/3", "args": ["record_id", "status", "date"]},
            ]
        },
    )

    delivery = source_compile["profile_delivery"]
    assert delivery["findings"][0]["class"] == "status_state_carrier_offered_but_undelivered"
    assert delivery["offered_carriers"]["status_state"] == ["record_status_at/3"]
    assert delivery["delivered_carriers"]["status_state"] == []
    health = source_compile["compile_health"]
    assert health["flag_counts"]["status_state_carrier_offered_but_undelivered"] == 1
    assert "profile_delivery" in health["unhealthy_passes"]


def test_profile_delivery_flags_partial_scope_discrepancy_rows() -> None:
    source_compile = {
        "unique_fact_count": 1,
        "facts": [
            "scope_discrepancy(pipe_length, 3200_feet, record_a, 3400_feet, record_b, revised_survey).",
        ],
        "compile_health": {
            "schema_version": "compile_lens_health_v1",
            "verdict": "healthy",
            "recommendation": "qa_run_reasonable",
            "pass_count": 1,
            "unhealthy_pass_count": 0,
            "unhealthy_passes": [],
            "flag_counts": {},
            "unique_contribution_total": 1,
            "duplicate_total": 0,
            "semantic_progress": {"zombie_risk": "low", "recommended_action": "continue"},
        },
    }

    _attach_profile_admission_report(
        source_compile=source_compile,
        domain_hint="policy contract discrepancy conflict agreement resolution",
        source_text=(
            "1. Pipe length: Record A states 3,200 feet. Record B states 3,400 feet.\n"
            "2. Progress reports: Record A requires monthly reports. Record B requires quarterly reports.\n"
            "3. Fire hydrants: Record A does not mention hydrants. Record B requires twelve hydrants."
        ),
        parsed_profile={
            "candidate_predicates": [
                {
                    "signature": "scope_discrepancy/6",
                    "args": ["issue", "left_value", "left_record", "right_value", "right_record", "basis"],
                },
            ]
        },
    )

    delivery = source_compile["profile_delivery"]
    finding = delivery["findings"][0]
    assert finding["class"] == "scope_discrepancy_carrier_partially_delivered"
    assert finding["missing_signal_keys"] == ["reporting_frequency", "fire_hydrants"]
    assert delivery["delivered_carrier_row_counts"]["scope_discrepancy"] == 1
    assert source_compile["compile_health"]["flag_counts"]["scope_discrepancy_carrier_partially_delivered"] == 1


def test_profile_delivery_flags_offered_source_claim_carrier_without_emitted_rows() -> None:
    source_compile = {
        "unique_fact_count": 2,
        "facts": [
            "source_note(rivera_memo, device_alpha_status_active).",
            "claim_status(claim_beta, unresolved).",
        ],
        "compile_health": {
            "schema_version": "compile_lens_health_v1",
            "verdict": "healthy",
            "recommendation": "qa_run_reasonable",
            "pass_count": 1,
            "unhealthy_pass_count": 0,
            "unhealthy_passes": [],
            "flag_counts": {},
            "unique_contribution_total": 2,
            "duplicate_total": 0,
            "semantic_progress": {"zombie_risk": "low", "recommended_action": "continue"},
        },
    }

    _attach_profile_admission_report(
        source_compile=source_compile,
        domain_hint="source attributed claim report status",
        source_text=(
            "Rivera memo says device alpha status is active.\n"
            "Field report notes claim beta remains unresolved."
        ),
        parsed_profile={
            "candidate_predicates": [
                {
                    "signature": "source_attributed_claim/4",
                    "args": ["claim_id", "source_document", "content_status", "source_row"],
                },
            ]
        },
    )

    delivery = source_compile["profile_delivery"]
    assert delivery["findings"][0]["class"] == "source_claim_carrier_offered_but_undelivered"
    assert delivery["offered_carriers"]["source_attributed_claim"] == ["source_attributed_claim/4"]
    assert delivery["delivered_carriers"]["source_attributed_claim"] == []
    health = source_compile["compile_health"]
    assert health["flag_counts"]["source_claim_carrier_offered_but_undelivered"] == 1
    assert "profile_delivery" in health["unhealthy_passes"]


def test_profile_delivery_flags_offered_source_authority_carrier_without_emitted_rows() -> None:
    source_compile = {
        "unique_fact_count": 1,
        "facts": [
            "recipient_action(item_7, access_granted).",
        ],
        "compile_health": {
            "schema_version": "compile_lens_health_v1",
            "verdict": "healthy",
            "recommendation": "qa_run_reasonable",
            "pass_count": 1,
            "unhealthy_pass_count": 0,
            "unhealthy_passes": [],
            "flag_counts": {},
            "unique_contribution_total": 1,
            "duplicate_total": 0,
            "semantic_progress": {"zombie_risk": "low", "recommended_action": "continue"},
        },
    }

    _attach_profile_admission_report(
        source_compile=source_compile,
        domain_hint="source authority governing source",
        source_text="Court order approval is authority for item 7 access status.",
        parsed_profile={
            "candidate_predicates": [
                {
                    "signature": "source_authority/3",
                    "args": ["subject_id", "authority_or_source", "scope_or_action"],
                },
            ]
        },
    )

    delivery = source_compile["profile_delivery"]
    assert delivery["findings"][0]["class"] == "source_authority_carrier_offered_but_undelivered"
    assert delivery["offered_carriers"]["source_authority"] == ["source_authority/3"]
    assert delivery["delivered_carriers"]["source_authority"] == []
    assert source_compile["compile_health"]["flag_counts"]["source_authority_carrier_offered_but_undelivered"] == 1


def test_profile_delivery_accepts_emitted_source_authority_carrier_rows() -> None:
    source_compile = {
        "unique_fact_count": 1,
        "facts": [
            "source_authority(item_7, court_order, access_status).",
        ],
        "compile_health": {
            "schema_version": "compile_lens_health_v1",
            "verdict": "healthy",
            "recommendation": "qa_run_reasonable",
            "pass_count": 1,
            "unhealthy_pass_count": 0,
            "unhealthy_passes": [],
            "flag_counts": {},
            "unique_contribution_total": 1,
            "duplicate_total": 0,
            "semantic_progress": {"zombie_risk": "low", "recommended_action": "continue"},
        },
    }

    _attach_profile_admission_report(
        source_compile=source_compile,
        domain_hint="source authority governing source",
        source_text="Court order approval is authority for item 7 access status.",
        parsed_profile={
            "candidate_predicates": [
                {
                    "signature": "source_authority/3",
                    "args": ["subject_id", "authority_or_source", "scope_or_action"],
                },
            ]
        },
    )

    assert source_compile["profile_delivery"]["findings"] == []
    assert source_compile["profile_delivery"]["delivered_carriers"]["source_authority"] == ["source_authority"]
    assert source_compile["compile_health"]["verdict"] == "healthy"


def test_profile_delivery_flags_partial_source_authority_carrier_rows() -> None:
    source_compile = {
        "unique_fact_count": 1,
        "facts": [
            "source_authority(item_7, court_order, access_status).",
        ],
        "compile_health": {
            "schema_version": "compile_lens_health_v1",
            "verdict": "healthy",
            "recommendation": "qa_run_reasonable",
            "pass_count": 1,
            "unhealthy_pass_count": 0,
            "unhealthy_passes": [],
            "flag_counts": {},
            "unique_contribution_total": 1,
            "duplicate_total": 0,
            "semantic_progress": {"zombie_risk": "low", "recommended_action": "continue"},
        },
    }

    _attach_profile_admission_report(
        source_compile=source_compile,
        domain_hint="source authority governing source source authority",
        source_text=(
            "Court order approval is authority for item 7 access status.\n"
            "Board memo is authority for item 8 access status."
        ),
        parsed_profile={
            "candidate_predicates": [
                {
                    "signature": "source_authority/3",
                    "args": ["subject_id", "authority_or_source", "scope_or_action"],
                },
            ]
        },
    )

    finding = source_compile["profile_delivery"]["findings"][0]
    assert finding["class"] == "source_authority_carrier_partially_delivered"
    assert finding["source_signal_count"] == 2
    assert finding["delivered_carrier_row_count"] == 1
    assert finding["missing_signal_count"] == 1
    assert source_compile["profile_delivery"]["delivered_carrier_row_counts"]["source_authority"] == 1
    assert source_compile["compile_health"]["flag_counts"]["source_authority_carrier_partially_delivered"] == 1
    assert source_compile["compile_health"]["verdict"] == "warning"


def test_profile_delivery_accepts_emitted_source_claim_carrier_rows() -> None:
    source_compile = {
        "unique_fact_count": 2,
        "facts": [
            "source_attributed_claim(claim_1, rivera_memo, device_alpha_status_active, src_line_001).",
            "source_attributed_claim(claim_2, field_report, claim_beta_unresolved, src_line_002).",
        ],
        "compile_health": {
            "schema_version": "compile_lens_health_v1",
            "verdict": "healthy",
            "recommendation": "qa_run_reasonable",
            "pass_count": 1,
            "unhealthy_pass_count": 0,
            "unhealthy_passes": [],
            "flag_counts": {},
            "unique_contribution_total": 2,
            "duplicate_total": 0,
            "semantic_progress": {"zombie_risk": "low", "recommended_action": "continue"},
        },
    }

    _attach_profile_admission_report(
        source_compile=source_compile,
        domain_hint="source attributed claim report status",
        source_text=(
            "Rivera memo says device alpha status is active.\n"
            "Field report notes claim beta remains unresolved."
        ),
        parsed_profile={
            "candidate_predicates": [
                {
                    "signature": "source_attributed_claim/4",
                    "args": ["claim_id", "source_document", "content_status", "source_row"],
                },
            ]
        },
    )

    assert source_compile["profile_delivery"]["findings"] == []
    assert source_compile["profile_delivery"]["delivered_carriers"]["source_attributed_claim"] == ["source_attributed_claim"]
    assert source_compile["compile_health"]["verdict"] == "healthy"


def test_profile_delivery_keys_source_claim_rows_to_required_signals() -> None:
    source_compile = {
        "unique_fact_count": 2,
        "facts": [
            "source_attributed_claim(claim_pryce_note, david_pryce, nursery_retention_support, src_line_027).",
            "letter_of_intent(loi_2025_02_navarro, navarro_consulting, l_2022_015, under_review).",
        ],
        "compile_health": {
            "schema_version": "compile_lens_health_v1",
            "verdict": "healthy",
            "recommendation": "qa_run_reasonable",
            "pass_count": 1,
            "unhealthy_pass_count": 0,
            "unhealthy_passes": [],
            "flag_counts": {},
            "unique_contribution_total": 2,
            "duplicate_total": 0,
            "semantic_progress": {"zombie_risk": "low", "recommended_action": "continue"},
        },
    }

    _attach_profile_admission_report(
        source_compile=source_compile,
        domain_hint="source attributed claim report status",
        source_text=(
            "Corr note says this draft status is voided and has no legal effect.\n"
            "Navarro letter of intent is under review and is not binding."
        ),
        parsed_profile={
            "candidate_predicates": [
                {
                    "signature": "source_attributed_claim/4",
                    "args": ["claim_id", "source_or_speaker", "content_or_status", "source_row_or_scope"],
                }
            ]
        },
    )

    finding = source_compile["profile_delivery"]["findings"][0]
    assert finding["class"] == "source_claim_carrier_partially_delivered"
    assert finding["required_signal_keys"] == [
        "note:draft:no_effect",
        "letter_of_intent:letter_of_intent:not_binding",
    ]
    assert finding["delivered_signal_keys"] == ["note:claim:support"]
    assert finding["missing_signal_keys"] == [
        "note:draft:no_effect",
        "letter_of_intent:letter_of_intent:not_binding",
    ]


def test_profile_delivery_keys_source_claim_rows_through_source_refs() -> None:
    source_compile = {
        "unique_fact_count": 4,
        "facts": [
            "source_attributed_claim(claim_v1_no_effect, corr, no_legal_effect, src_line_0031).",
            "source_attributed_claim(claim_loi_not_binding, source_md, not_a_binding_lease, src_line_0057).",
            "source_record_text_atom(src_line_0031, corr_note_this_draft_was_never_signed_and_has_no_legal_effect).",
            "source_record_text_atom(src_line_0057, navarro_letter_of_intent_is_under_review_it_is_not_a_binding_lease).",
        ],
        "compile_health": {
            "schema_version": "compile_lens_health_v1",
            "verdict": "healthy",
            "recommendation": "qa_run_reasonable",
            "pass_count": 1,
            "unhealthy_pass_count": 0,
            "unhealthy_passes": [],
            "flag_counts": {},
            "unique_contribution_total": 4,
            "duplicate_total": 0,
            "semantic_progress": {"zombie_risk": "low", "recommended_action": "continue"},
        },
    }

    _attach_profile_admission_report(
        source_compile=source_compile,
        domain_hint="source attributed claim report status",
        source_text=(
            "Corr note says this draft status is voided and has no legal effect.\n"
            "Navarro letter of intent is under review and is not binding."
        ),
        parsed_profile={
            "candidate_predicates": [
                {
                    "signature": "source_attributed_claim/4",
                    "args": ["claim_id", "source_or_speaker", "content_or_status", "source_row_or_scope"],
                }
            ]
        },
    )

    assert source_compile["profile_delivery"]["findings"] == []
    assert source_compile["profile_delivery"]["delivered_carriers"]["source_attributed_claim"] == [
        "source_attributed_claim"
    ]


def test_profile_delivery_keys_source_claim_ignores_generic_source_ids() -> None:
    source_compile = {
        "unique_fact_count": 2,
        "facts": [
            "source_attributed_claim(claim_status, source_md, does_not_change_the_status_of_unmoved_plants, note_scope).",
            "source_record_text_atom(source_md, generic_source_document).",
        ],
        "compile_health": {
            "schema_version": "compile_lens_health_v1",
            "verdict": "healthy",
            "recommendation": "qa_run_reasonable",
            "pass_count": 1,
            "unhealthy_pass_count": 0,
            "unhealthy_passes": [],
            "flag_counts": {},
            "unique_contribution_total": 2,
            "duplicate_total": 0,
            "semantic_progress": {"zombie_risk": "low", "recommended_action": "continue"},
        },
    }

    _attach_profile_admission_report(
        source_compile=source_compile,
        domain_hint="source attributed claim report status",
        source_text='Solberg\'s note: "This does not change the status of the unmoved plants."',
        parsed_profile={
            "candidate_predicates": [
                {
                    "signature": "source_attributed_claim/4",
                    "args": ["claim_id", "source_or_speaker", "content_or_status", "source_row_or_scope"],
                }
            ]
        },
    )

    assert source_compile["profile_delivery"]["findings"] == []


def test_source_claim_key_treats_not_resolved_as_unresolved() -> None:
    assert (
        domain_bootstrap_file._source_attributed_claim_signal_key(
            "The April 28 email says the actual-knowledge question is not resolved on this record."
        )
        == "email:claim:unresolved"
    )


def test_source_claim_key_treats_concerned_as_concern() -> None:
    assert (
        domain_bootstrap_file._source_attributed_claim_signal_key(
            "Popov states that he is concerned about street parking and truck traffic."
        )
        == "source:claim:concern"
    )


def test_profile_delivery_accepts_concerned_source_claim_row() -> None:
    source_compile = {
        "unique_fact_count": 1,
        "facts": [
            "source_attributed_claim(claim_popov_concern, victor_popov, concerned_about_parking_and_truck_traffic, src_line_0333).",
            "source_record_text_atom(src_line_0333, popov_states_that_he_is_concerned_about_parking_and_truck_traffic).",
        ],
        "compile_health": {
            "schema_version": "compile_lens_health_v1",
            "verdict": "healthy",
            "recommendation": "qa_run_reasonable",
            "pass_count": 1,
            "unhealthy_pass_count": 0,
            "unhealthy_passes": [],
            "flag_counts": {},
            "unique_contribution_total": 1,
            "duplicate_total": 0,
            "semantic_progress": {"zombie_risk": "low", "recommended_action": "continue"},
        },
    }

    _attach_profile_admission_report(
        source_compile=source_compile,
        domain_hint="source claim source statement",
        source_text="Popov states that he is concerned about street parking and truck traffic.",
        parsed_profile={
            "candidate_predicates": [
                {
                    "signature": "source_attributed_claim/4",
                    "args": ["claim_id", "source_or_speaker", "content_or_status", "source_row_or_scope"],
                }
            ]
        },
    )

    assert source_compile["profile_delivery"]["findings"] == []


def test_profile_delivery_accepts_source_local_claim_carrier_rows() -> None:
    source_compile = {
        "unique_fact_count": 3,
        "facts": [
            "legal_opinion(brennan, permit_in_force_principle, actual_knowledge_unresolved).",
            "public_comment(comment_1, resident_lee, plan_supports_safe_crossing, 2026_03_25).",
            "staff_assessment(assessment_1, director_soto, cost_estimate_requires_supplemental_appropriation, 2026_03_12).",
        ],
        "compile_health": {
            "schema_version": "compile_lens_health_v1",
            "verdict": "healthy",
            "recommendation": "qa_run_reasonable",
            "pass_count": 1,
            "unhealthy_pass_count": 0,
            "unhealthy_passes": [],
            "flag_counts": {},
            "unique_contribution_total": 3,
            "duplicate_total": 0,
            "semantic_progress": {"zombie_risk": "low", "recommended_action": "continue"},
        },
    }

    _attach_profile_admission_report(
        source_compile=source_compile,
        domain_hint="source attributed claim report status",
        source_text=(
            "Solicitor opinion says actual knowledge remains unresolved.\n"
            "Public comment supports the crossing.\n"
            "Staff assessment says supplemental appropriation may be required."
        ),
        parsed_profile={
            "candidate_predicates": [
                {"signature": "legal_opinion/3", "args": ["author", "principle", "conclusion"]},
                {"signature": "public_comment/4", "args": ["comment_id", "speaker", "content", "date"]},
                {"signature": "staff_assessment/4", "args": ["assessment_id", "author", "content", "date"]},
                {
                    "signature": "source_attributed_claim/4",
                    "args": ["claim_id", "source_or_speaker", "content_or_status", "source_row_or_scope"],
                },
            ]
        },
    )

    assert source_compile["profile_delivery"]["findings"] == []
    assert source_compile["profile_delivery"]["delivered_carriers"]["source_attributed_claim"] == [
        "legal_opinion",
        "public_comment",
        "staff_assessment",
    ]


def test_profile_delivery_flags_source_claim_backbone_coexistence_missing() -> None:
    source_compile = {
        "unique_fact_count": 1,
        "facts": [
            "source_attributed_claim(claim_koss, koss, no_documentation, src_line_001).",
        ],
        "compile_health": {
            "schema_version": "compile_lens_health_v1",
            "verdict": "healthy",
            "recommendation": "qa_run_reasonable",
            "pass_count": 1,
            "unhealthy_pass_count": 0,
            "unhealthy_passes": [],
            "flag_counts": {},
            "unique_contribution_total": 1,
            "duplicate_total": 0,
            "semantic_progress": {"zombie_risk": "low", "recommended_action": "continue"},
        },
    }

    _attach_profile_admission_report(
        source_compile=source_compile,
        domain_hint="zoning hearing board source attributed claim",
        source_text=(
            "Koss says: no documentation supports the side-yard exemption.\n"
            "Board voted 3-2 to deny the variance.\n"
            "Survey shows 8 feet from the western boundary.\n"
            "Home occupation permit application status is pending.\n"
            "Notice of appeal filed May 3, 2026.\n"
            "Board finding concluded hardship was not proven.\n"
            "Quorum was present at the hearing."
        ),
        parsed_profile={
            "candidate_predicates": [
                {
                    "signature": "source_attributed_claim/4",
                    "args": ["claim_id", "source_or_speaker", "content_or_status", "source_row_or_scope"],
                },
                {"signature": "board_vote/3", "args": ["body", "result", "tally"]},
                {"signature": "survey_measurement/4", "args": ["parcel", "measure", "value", "unit"]},
                {"signature": "permit_status/2", "args": ["permit_id", "status"]},
                {"signature": "appeal_filing/3", "args": ["appeal_id", "status", "date"]},
                {"signature": "board_finding/3", "args": ["finding_id", "conclusion", "body"]},
                {"signature": "quorum_status/2", "args": ["hearing_id", "status"]},
            ]
        },
    )

    finding = next(
        item
        for item in source_compile["profile_delivery"]["findings"]
        if item["class"] == "source_claim_backbone_coexistence_missing"
    )
    assert finding["missing_signal_keys"] == [
        "appeal_filing",
        "board_finding",
        "hearing_quorum",
        "permit_application_status",
        "survey_measurement",
        "vote",
    ]
    assert source_compile["compile_health"]["flag_counts"]["source_claim_backbone_coexistence_missing"] == 1


def test_source_claim_backbone_ignores_vote_as_organization_name() -> None:
    groups = domain_bootstrap_file._source_claim_backbone_source_groups(
        "The Clean Energy Organizations and Vote Solar filed comments before the Commission."
    )

    assert "vote" not in groups
    assert "vote" in domain_bootstrap_file._source_claim_backbone_source_groups(
        "The Board voted 3-2 to deny the variance."
    )


def test_profile_delivery_accepts_source_claim_with_preserved_backbone_rows() -> None:
    source_compile = {
        "unique_fact_count": 7,
        "facts": [
            "source_attributed_claim(claim_koss, koss, no_documentation, src_line_001).",
            "board_vote(board, denied, tally_3_2).",
            "survey_measurement(parcel_7, setback, 8, feet).",
            "permit_status(home_occupation_permit, pending).",
            "appeal_filing(appeal_1, filed, 2026_05_03).",
            "board_finding(hardship, not_proven, board).",
            "quorum_status(hearing_1, quorum_present).",
        ],
        "compile_health": {
            "schema_version": "compile_lens_health_v1",
            "verdict": "healthy",
            "recommendation": "qa_run_reasonable",
            "pass_count": 1,
            "unhealthy_pass_count": 0,
            "unhealthy_passes": [],
            "flag_counts": {},
            "unique_contribution_total": 7,
            "duplicate_total": 0,
            "semantic_progress": {"zombie_risk": "low", "recommended_action": "continue"},
        },
    }

    _attach_profile_admission_report(
        source_compile=source_compile,
        domain_hint="zoning hearing board source attributed claim",
        source_text=(
            "Koss says: no documentation supports the side-yard exemption.\n"
            "Board voted 3-2 to deny the variance.\n"
            "Survey shows 8 feet from the western boundary.\n"
            "Home occupation permit application status is pending.\n"
            "Notice of appeal filed May 3, 2026.\n"
            "Board finding concluded hardship was not proven.\n"
            "Quorum was present at the hearing."
        ),
        parsed_profile={
            "candidate_predicates": [
                {
                    "signature": "source_attributed_claim/4",
                    "args": ["claim_id", "source_or_speaker", "content_or_status", "source_row_or_scope"],
                },
                {"signature": "board_vote/3", "args": ["body", "result", "tally"]},
                {"signature": "survey_measurement/4", "args": ["parcel", "measure", "value", "unit"]},
                {"signature": "permit_status/2", "args": ["permit_id", "status"]},
                {"signature": "appeal_filing/3", "args": ["appeal_id", "status", "date"]},
                {"signature": "board_finding/3", "args": ["finding_id", "conclusion", "body"]},
                {"signature": "quorum_status/2", "args": ["hearing_id", "status"]},
            ]
        },
    )

    classes = {item["class"] for item in source_compile["profile_delivery"]["findings"]}
    assert "source_claim_backbone_coexistence_missing" not in classes


def test_profile_delivery_flags_missing_vote_tally_keys() -> None:
    source_compile = {
        "unique_fact_count": 4,
        "facts": [
            "voting_record(hoffman, affirmative, variance_request).",
            "voting_record(yee, affirmative, variance_request).",
            "voting_record(castellano, affirmative, variance_request).",
            "voting_record(kowalski, negative, variance_request).",
        ],
        "compile_health": {
            "schema_version": "compile_lens_health_v1",
            "verdict": "healthy",
            "recommendation": "qa_run_reasonable",
            "pass_count": 1,
            "unhealthy_pass_count": 0,
            "unhealthy_passes": [],
            "flag_counts": {},
            "unique_contribution_total": 4,
            "duplicate_total": 0,
            "semantic_progress": {"zombie_risk": "low", "recommended_action": "continue"},
        },
    }

    _attach_profile_admission_report(
        source_compile=source_compile,
        domain_hint="source claim hearing vote tally correction",
        source_text=(
            "The ZBA votes 3-2 to proceed with the hearing using the recorded survey.\n"
            "Vote on variance: approved 3-1.\n"
            "The minutes initially recorded the vote as 4-1 and were corrected to 3-1."
        ),
        parsed_profile={
            "candidate_predicates": [
                {"signature": "vote_tally/5", "args": ["vote_id", "body", "subject", "result", "tally"]},
                {"signature": "voting_record/3", "args": ["member", "vote", "subject"]},
            ]
        },
    )

    finding = next(
        item
        for item in source_compile["profile_delivery"]["findings"]
        if item["class"] == "vote_tally_carrier_partially_delivered"
    )
    assert finding["missing_signal_keys"] == ["proceed:3_2", "approved:3_1", "correction:4_1_to_3_1"]
    assert source_compile["profile_delivery"]["carrier_row_requirements"]["vote_tally"] == 3


def test_profile_delivery_accepts_vote_tally_rows() -> None:
    source_compile = {
        "unique_fact_count": 3,
        "facts": [
            "vote_tally(vote_proceed_survey, zba, proceed_with_recorded_survey, approved, 3_2).",
            "vote_tally(vote_variance_final, zba, variance_request, approved, 3_1).",
            "vote_tally(minutes_correction, zba, variance_vote_minutes, corrected_from_4_1_to_3_1, 3_1).",
        ],
        "compile_health": {
            "schema_version": "compile_lens_health_v1",
            "verdict": "healthy",
            "recommendation": "qa_run_reasonable",
            "pass_count": 1,
            "unhealthy_pass_count": 0,
            "unhealthy_passes": [],
            "flag_counts": {},
            "unique_contribution_total": 3,
            "duplicate_total": 0,
            "semantic_progress": {"zombie_risk": "low", "recommended_action": "continue"},
        },
    }

    _attach_profile_admission_report(
        source_compile=source_compile,
        domain_hint="source claim hearing vote tally correction",
        source_text=(
            "The ZBA votes 3-2 to proceed with the hearing using the recorded survey.\n"
            "Vote on variance: approved 3-1.\n"
            "The minutes initially recorded the vote as 4-1 and were corrected to 3-1."
        ),
        parsed_profile={
            "candidate_predicates": [
                {"signature": "vote_tally/5", "args": ["vote_id", "body", "subject", "result", "tally"]},
            ]
        },
    )

    classes = {item["class"] for item in source_compile["profile_delivery"]["findings"]}
    assert "vote_tally_carrier_partially_delivered" not in classes
    assert "vote_tally_carrier_offered_but_undelivered" not in classes
    assert source_compile["profile_delivery"]["delivered_carriers"]["vote_tally"] == ["vote_tally"]


def test_profile_delivery_accepts_emitted_status_state_carrier_rows() -> None:
    source_compile = {
        "unique_fact_count": 2,
        "facts": [
            "record_status_at(record_alpha, suspect, 2026_09_15).",
            "record_status_at(record_beta, cleared, 2026_09_20).",
        ],
        "compile_health": {
            "schema_version": "compile_lens_health_v1",
            "verdict": "healthy",
            "recommendation": "qa_run_reasonable",
            "pass_count": 1,
            "unhealthy_pass_count": 0,
            "unhealthy_passes": [],
            "flag_counts": {},
            "unique_contribution_total": 2,
            "duplicate_total": 0,
            "semantic_progress": {"zombie_risk": "low", "recommended_action": "continue"},
        },
    }

    _attach_profile_admission_report(
        source_compile=source_compile,
        domain_hint="point-in-time status/state",
        source_text=(
            "On 2026-09-15 record alpha status was suspect.\n"
            "On 2026-09-20 record beta status was cleared."
        ),
        parsed_profile={
            "candidate_predicates": [
                {"signature": "record_status_at/3", "args": ["record_id", "status", "date"]},
            ]
        },
    )

    assert source_compile["profile_delivery"]["findings"] == []
    assert source_compile["profile_delivery"]["delivered_carriers"]["status_state"] == ["record_status_at"]
    assert source_compile["compile_health"]["verdict"] == "healthy"


def test_profile_delivery_accepts_lease_term_status_rows() -> None:
    source_compile = {
        "unique_fact_count": 1,
        "facts": [
            "lease_term(l_2022_015, 2022_01, 2025_01, terminated).",
        ],
        "compile_health": {
            "schema_version": "compile_lens_health_v1",
            "verdict": "healthy",
            "recommendation": "qa_run_reasonable",
            "pass_count": 1,
            "unhealthy_pass_count": 0,
            "unhealthy_passes": [],
            "flag_counts": {},
            "unique_contribution_total": 1,
            "duplicate_total": 0,
            "semantic_progress": {"zombie_risk": "low", "recommended_action": "continue"},
        },
    }

    _attach_profile_admission_report(
        source_compile=source_compile,
        domain_hint="operational record status lifecycle",
        source_text="The current state is vacant after Holbrook's lease terminated November 30, 2024.",
        parsed_profile={
            "candidate_predicates": [
                {"signature": "lease_term/4", "args": ["lease_id", "start_date", "end_date", "status"]},
            ]
        },
    )

    assert source_compile["profile_delivery"]["findings"] == []
    assert source_compile["profile_delivery"]["delivered_carriers"]["status_state"] == ["lease_term"]


def test_profile_delivery_accepts_status_bearing_source_local_rows() -> None:
    source_compile = {
        "unique_fact_count": 2,
        "facts": [
            "knowledge_assertion(kowalski, tree_19_status_unchanged, 2026_04_21, exhibit_k1).",
            "scheduled_event(mid_construction_inspection, inspection, 2026_05_05, deferred_pending_hearing).",
        ],
        "compile_health": {
            "schema_version": "compile_lens_health_v1",
            "verdict": "healthy",
            "recommendation": "qa_run_reasonable",
            "pass_count": 1,
            "unhealthy_pass_count": 0,
            "unhealthy_passes": [],
            "flag_counts": {},
            "unique_contribution_total": 2,
            "duplicate_total": 0,
            "semantic_progress": {"zombie_risk": "low", "recommended_action": "continue"},
        },
    }

    _attach_profile_admission_report(
        source_compile=source_compile,
        domain_hint="point-in-time status/state",
        source_text=(
            "On 2026-04-21 record tree 19 status was unchanged.\n"
            "On 2026-05-05 record inspection status is deferred pending hearing."
        ),
        parsed_profile={
            "candidate_predicates": [
                {"signature": "authorization_status/4", "args": ["tree_id", "permit_id", "status", "date_range"]},
                {"signature": "knowledge_assertion/4", "args": ["person", "fact", "date", "source"]},
                {"signature": "scheduled_event/4", "args": ["event_id", "event_type", "date", "status"]},
            ]
        },
    )

    assert source_compile["profile_delivery"]["findings"] == []
    assert source_compile["profile_delivery"]["delivered_carriers"]["status_state"] == [
        "knowledge_assertion",
        "scheduled_event",
    ]


def test_profile_delivery_accepts_municipal_status_carrier_rows() -> None:
    source_compile = {
        "unique_fact_count": 3,
        "facts": [
            "permit_status(tr_2026_014, issued).",
            "tree_protection_status(19, not_protected).",
            "pending_determination(violation_of_tree_19_removal, pending).",
        ],
        "compile_health": {
            "schema_version": "compile_lens_health_v1",
            "verdict": "healthy",
            "recommendation": "qa_run_reasonable",
            "pass_count": 1,
            "unhealthy_pass_count": 0,
            "unhealthy_passes": [],
            "flag_counts": {},
            "unique_contribution_total": 3,
            "duplicate_total": 0,
            "semantic_progress": {"zombie_risk": "low", "recommended_action": "continue"},
        },
    }

    _attach_profile_admission_report(
        source_compile=source_compile,
        domain_hint="point-in-time status/state",
        source_text=(
            "On 2026-04-02 record permit status was issued.\n"
            "On 2026-04-25 record tree 19 status was not protected.\n"
            "On 2026-05-04 record violation determination was pending."
        ),
        parsed_profile={
            "candidate_predicates": [
                {"signature": "permit_status/2", "args": ["permit_id", "status"]},
                {"signature": "tree_protection_status/2", "args": ["tree_id", "status"]},
                {"signature": "pending_determination/2", "args": ["determination_id", "status"]},
            ]
        },
    )

    assert source_compile["profile_delivery"]["findings"] == []
    assert source_compile["profile_delivery"]["delivered_carriers"]["status_state"] == [
        "pending_determination",
        "permit_status",
        "tree_protection_status",
    ]


def test_profile_delivery_does_not_count_status_free_assertions_as_status_delivery() -> None:
    source_compile = {
        "unique_fact_count": 1,
        "facts": [
            "knowledge_assertion(kowalski, tree_19_is_norway_maple_22_dbh, 2026_04_21, exhibit_k1).",
        ],
        "compile_health": {
            "schema_version": "compile_lens_health_v1",
            "verdict": "healthy",
            "recommendation": "qa_run_reasonable",
            "pass_count": 1,
            "unhealthy_pass_count": 0,
            "unhealthy_passes": [],
            "flag_counts": {},
            "unique_contribution_total": 1,
            "duplicate_total": 0,
            "semantic_progress": {"zombie_risk": "low", "recommended_action": "continue"},
        },
    }

    _attach_profile_admission_report(
        source_compile=source_compile,
        domain_hint="point-in-time status/state",
        source_text="On 2026-04-21 record tree 19 status was unchanged.",
        parsed_profile={
            "candidate_predicates": [
                {"signature": "knowledge_assertion/4", "args": ["person", "fact", "date", "source"]},
            ]
        },
    )

    finding = source_compile["profile_delivery"]["findings"][0]
    assert finding["class"] == "status_state_carrier_offered_but_undelivered"
    assert source_compile["profile_delivery"]["delivered_carriers"]["status_state"] == []


def test_profile_delivery_accepts_source_local_authority_rows() -> None:
    source_compile = {
        "unique_fact_count": 4,
        "facts": [
            "charter_section(charter_art_ix_9_1, amendment_authority, council_may_amend_budget).",
            "rule_threshold(charter_art_ix_9_4, mayoral_authority_limit, 25000).",
            "emergency_authorization(emerg_auth_22k, 22000, sandbagging, 2026_05_12).",
            "amendment_authorizer(a1, helen_corr).",
            "permit_authorization(permit_a, tree_19, remove).",
        ],
        "compile_health": {
            "schema_version": "compile_lens_health_v1",
            "verdict": "healthy",
            "recommendation": "qa_run_reasonable",
            "pass_count": 1,
            "unhealthy_pass_count": 0,
            "unhealthy_passes": [],
            "flag_counts": {},
            "unique_contribution_total": 4,
            "duplicate_total": 0,
            "semantic_progress": {"zombie_risk": "low", "recommended_action": "continue"},
        },
    }

    _attach_profile_admission_report(
        source_compile=source_compile,
        domain_hint="source authority governing source",
        source_text=(
            "Section 9.1 is the amendment authority.\n"
            "The $25,000 mayoral emergency authority applies.\n"
            "Authorized by Property Manager Helen Corr."
        ),
        parsed_profile={
            "candidate_predicates": [
                {"signature": "charter_section/3", "args": ["section", "condition", "effect"]},
                {"signature": "amendment_author/2", "args": ["amendment_id", "person_name"]},
                {"signature": "rule_threshold/3", "args": ["rule_id", "condition", "value"]},
                {"signature": "authorization_rule/3", "args": ["actor_role", "action_type", "threshold_or_scope"]},
                {"signature": "emergency_authorization/4", "args": ["authorization_id", "amount", "scope", "date"]},
                {"signature": "event_authorizer/2", "args": ["event_id", "actor_id"]},
                {"signature": "authorized_by_role/3", "args": ["event_id", "actor_id", "role"]},
                {"signature": "amendment_authorizer/2", "args": ["amendment_id", "authorizer"]},
                {"signature": "permit_authorization/3", "args": ["permit_id", "subject_id", "authorized_action"]},
                {"signature": "source_authority/3", "args": ["subject_id", "authority_or_source", "scope_or_action"]},
            ]
        },
    )

    assert source_compile["profile_delivery"]["findings"] == []
    assert source_compile["profile_delivery"]["delivered_carrier_row_counts"]["source_authority"] == 5
    assert domain_bootstrap_file._fact_row_can_deliver_source_authority(
        "authorization_rule",
        ["property_manager", "standard_amendments_corrections_operational_changes", "under_50_000_annually"],
    )
    assert domain_bootstrap_file._fact_row_can_deliver_source_authority(
        "amendment_event",
        ["l_2019_004", "a1", "2024_04", "helen_corr", "lease_extended"],
    )
    assert domain_bootstrap_file._fact_row_can_deliver_source_authority(
        "amendment_author",
        ["a1_l2019", "helen_corr"],
    )
    assert domain_bootstrap_file._fact_row_can_deliver_source_authority(
        "authorized_by_role",
        ["event_l2019_a1", "corr", "property_manager"],
    )
    assert domain_bootstrap_file._fact_row_can_deliver_source_authority(
        "permit_authorization",
        ["permit_a", "tree_19", "remove"],
    )
    assert domain_bootstrap_file._fact_row_can_deliver_source_authority(
        "charter_rule",
        ["charter_section_9_4", "mayor_may_authorize_emergency_expenditures_up_to_25_000", "emergency_appropriation"],
    )


def test_profile_delivery_flags_offered_quantity_carrier_without_emitted_rows() -> None:
    source_compile = {
        "unique_fact_count": 2,
        "facts": [
            "event_description(ev_01, feed_rate_increased_to_18_kg_min).",
            "event_description(ev_02, setpoint_changed_from_480_k_to_495_k).",
        ],
        "compile_health": {
            "schema_version": "compile_lens_health_v1",
            "verdict": "healthy",
            "recommendation": "qa_run_reasonable",
            "pass_count": 1,
            "unhealthy_pass_count": 0,
            "unhealthy_passes": [],
            "flag_counts": {},
            "unique_contribution_total": 2,
            "duplicate_total": 0,
            "semantic_progress": {"zombie_risk": "low", "recommended_action": "continue"},
        },
    }

    _attach_profile_admission_report(
        source_compile=source_compile,
        domain_hint="instrument readings and measurement events",
        source_text=(
            "EV-01 2026-04-22 feed rate increased to 18 kg min.\n"
            "EV-02 2026-04-22 setpoint changed from 480 k to 495 k."
        ),
        parsed_profile={
            "candidate_predicates": [
                {
                    "signature": "event_measurement/4",
                    "args": ["event_id", "measure", "value", "unit"],
                },
            ]
        },
    )

    delivery = source_compile["profile_delivery"]
    assert delivery["findings"][0]["class"] == "quantity_carrier_offered_but_undelivered"
    assert delivery["offered_carriers"]["quantity_event"] == ["event_measurement/4"]
    assert delivery["delivered_carriers"]["quantity_event"] == []
    health = source_compile["compile_health"]
    assert health["verdict"] == "warning"
    assert health["flag_counts"]["quantity_carrier_offered_but_undelivered"] == 1
    assert "profile_delivery" in health["unhealthy_passes"]
    assert "profile_admission" not in health["unhealthy_passes"]


def test_profile_delivery_does_not_treat_sensor_certification_as_quantity_carrier() -> None:
    source_compile = {
        "unique_fact_count": 1,
        "facts": [
            "sensor_certified_for(hum_d_04, relative_humidity_measurement).",
        ],
        "compile_health": {
            "schema_version": "compile_lens_health_v1",
            "verdict": "healthy",
            "recommendation": "qa_run_reasonable",
            "pass_count": 1,
            "unhealthy_pass_count": 0,
            "unhealthy_passes": [],
            "flag_counts": {},
            "unique_contribution_total": 1,
            "duplicate_total": 0,
            "semantic_progress": {"zombie_risk": "low", "recommended_action": "continue"},
        },
    }

    _attach_profile_admission_report(
        source_compile=source_compile,
        domain_hint="instrument readings and measurement events",
        source_text="EV-02 feed rate increased to 18.4 kg min.",
        parsed_profile={
            "candidate_predicates": [
                {
                    "signature": "sensor_certified_for/2",
                    "args": ["sensor_id", "measurement_type"],
                },
                {
                    "signature": "event_measurement/4",
                    "args": ["event_id", "measure", "value", "unit"],
                },
            ]
        },
    )

    delivery = source_compile["profile_delivery"]
    assert delivery["offered_carriers"]["quantity_event"] == ["event_measurement/4"]
    assert delivery["delivered_carriers"]["quantity_event"] == []
    assert delivery["findings"][0]["class"] == "quantity_carrier_offered_but_undelivered"


def test_source_pass_profile_delivery_target_context_names_quantity_keys() -> None:
    lines = domain_bootstrap_file._source_pass_profile_delivery_target_context(
        source_text=(
            "EV-01 setpoint changed from 480 k to 495 k.\n"
            "EV-02 feed rate increased to 18.4 kg min.\n"
            "The line-stop duration between EV-10 and EV-14 is 17 hours 45 minutes 52 seconds."
        ),
        parsed_profile={
            "candidate_predicates": [
                {
                    "signature": "sensor_certified_for/2",
                    "args": ["sensor_id", "measurement_type"],
                },
                {
                    "signature": "event_measurement/4",
                    "args": ["event_id", "measure", "value", "unit"],
                },
            ]
        },
    )

    joined = "\n".join(lines)
    assert "PROFILE DELIVERY TARGET" in joined
    assert "event:ev_01:setpointx2" in joined
    assert "event:ev_02:feed_ratex1" in joined
    assert "duration:line_stopx1" in joined
    assert "event_measurement/4" in joined
    assert "sensor_certified_for/2" not in joined
    assert "exact stated elapsed total" in joined


def test_source_pass_profile_delivery_target_context_names_source_claim_keys() -> None:
    lines = domain_bootstrap_file._source_pass_profile_delivery_target_context(
        source_text=(
            "Counsel opinion: the letter of intent is not binding and remains under review.\n"
            "The actual knowledge question is not resolved on this record."
        ),
        parsed_profile={
            "candidate_predicates": [
                {
                    "signature": "source_attributed_claim/4",
                    "args": ["claim_id", "source_or_speaker", "content_or_status", "source_row_or_scope"],
                },
            ]
        },
    )

    joined = "\n".join(lines)
    assert "PROFILE DELIVERY TARGET" in joined
    assert "letter_of_intent:letter_of_intent:not_binding" in joined
    assert "source_attributed_claim/4" in joined
    assert "source-to-claim carrier row" in joined
    assert "omit the required status" in joined
    assert "additive evidence" in joined
    assert "vote rows, survey or measurement rows" in joined


def test_source_pass_profile_delivery_target_prefers_four_slot_speaker_claims() -> None:
    lines = domain_bootstrap_file._source_pass_profile_delivery_target_context(
        source_text='**Kowalski:** "That is not what the code says. It says void."',
        parsed_profile={
            "candidate_predicates": [
                {"signature": "source_claim/3", "args": ["source", "subject", "claim"]},
                {
                    "signature": "source_attributed_claim/4",
                    "args": ["claim_id", "source_or_speaker", "content_or_status", "source_row_or_scope"],
                },
            ]
        },
    )

    joined = "\n".join(lines)
    assert "statement:claim:voided" in joined
    assert "source_attributed_claim/4 is available and is preferred" in joined
    assert "A shorter source_claim/3 row is additive" in joined


def test_source_pass_profile_delivery_target_names_objection_and_concern() -> None:
    lines = domain_bootstrap_file._source_pass_profile_delivery_target_context(
        source_text=(
            '**Hoffman:** "We will note the objection and proceed."\n'
            "Popov states that he is concerned about street parking and truck traffic."
        ),
        parsed_profile={
            "candidate_predicates": [
                {
                    "signature": "source_attributed_claim/4",
                    "args": ["claim_id", "source_or_speaker", "content_or_status", "source_row_or_scope"],
                },
            ]
        },
    )

    joined = "\n".join(lines)
    assert "objection-noting claim requirements" in joined
    assert "does not replace the objection row" in joined
    assert "concern-statement requirements" in joined
    assert "concern content" in joined


def test_source_pass_profile_delivery_target_names_event_date_carrier() -> None:
    lines = domain_bootstrap_file._source_pass_profile_delivery_target_context(
        source_text="Hearing date April 24, 2026. Appeal filed 2026-05-08. About 1415 the status changed to open.",
        parsed_profile={
            "candidate_predicates": [
                {"signature": "document_date/3", "args": ["document_or_subject_id", "date_kind_or_role", "date_value"]},
                {"signature": "event_date/2", "args": ["event_id", "date"]},
                {"signature": "event_time/2", "args": ["event_id", "time"]},
            ]
        },
    )

    joined = "\n".join(lines)
    assert "explicit event/hearing/filing dates or clock times" in joined
    assert "document_date/3" in joined
    assert "event_date/2" in joined
    assert "event_time/2" in joined
    assert "not a substitute for a joinable temporal row" in joined


def test_document_date_repair_context_targets_typed_date_carriers_only() -> None:
    profile = {
        "candidate_predicates": [
            {"signature": "document_date/3", "args": ["document_or_subject_id", "date_kind_or_role", "date_value"]},
            {"signature": "event_date/2", "args": ["event_id", "date"]},
            {"signature": "source_note/4", "args": ["note_id", "number", "content", "source"]},
        ]
    }
    source_compile = {
        "facts": [
            "document_identifier(case_2025_1705, appeal_no, 2025_1705).",
            "prior_art_reference(song_525, 2016_0243525, 2016_08_25).",
            "source_note(note_1, 1, prose_content, src_line_0025).",
        ]
    }

    assert _profile_document_date_repair_offered_carriers(profile) == ["document_date/3", "event_date/2"]

    lines = _document_date_repair_context_lines(parsed_profile=profile, source_compile=source_compile)
    joined = "\n".join(lines)

    assert "PROFILE DOCUMENT DATE REPAIR PASS" in joined
    assert "document_date/3" in joined
    assert "event_date/2" in joined
    assert "one typed date row per source-stated dated event" in joined
    assert "The main document issue date does not replace related filing" in joined
    assert "use document_date/3 for document-like subjects and event_date/2 for procedural event ids" in joined
    assert "source_note/4" not in joined
    assert "EXISTING DATE/IDENTIFIER FACT: prior_art_reference(song_525, 2016_0243525, 2016_08_25)." in joined


def test_source_pass_profile_delivery_target_names_prior_recall_date_carrier() -> None:
    lines = domain_bootstrap_file._source_pass_profile_delivery_target_context(
        source_text=(
            "The firm is expanding its July 12, 2024 recall to include additional peppers. "
            "This announcement was published July 22, 2024."
        ),
        parsed_profile={
            "candidate_predicates": [
                {"signature": "recall_date/2", "args": ["recall_event", "date"]},
                {"signature": "product_name/2", "args": ["product", "name"]},
            ]
        },
    )

    joined = "\n".join(lines)
    assert "prior or original recall date" in joined
    assert "July 12, 2024" in joined
    assert "recall_date/2" in joined
    assert "separate from the current expansion" in joined
    assert "source_record_text_atom" in joined


def test_source_pass_profile_delivery_target_names_quorum_carrier() -> None:
    lines = domain_bootstrap_file._source_pass_profile_delivery_target_context(
        source_text="Quorum check: 4 of 5 members present; quorum met, 3 required.",
        parsed_profile={
            "candidate_predicates": [
                {"signature": "quorum_status/3", "args": ["event_id", "status", "count_or_requirement"]},
            ]
        },
    )

    joined = "\n".join(lines)
    assert "explicit quorum facts" in joined
    assert "quorum_status/3" in joined
    assert "does not replace the direct quorum row" in joined


def test_source_pass_profile_delivery_target_names_appeal_filing_carrier() -> None:
    lines = domain_bootstrap_file._source_pass_profile_delivery_target_context(
        source_text="Koss files a formal appeal of the variance approval on May 8, 2026.",
        parsed_profile={
            "candidate_predicates": [
                {"signature": "appeal_filed/3", "args": ["appellant", "target_or_subject", "date_or_status"]},
            ]
        },
    )

    joined = "\n".join(lines)
    assert "explicit appeal-filing facts" in joined
    assert "appeal_filed/3" in joined
    assert "does not replace the direct appeal/filing row" in joined


def test_profile_delivery_repair_context_targets_carrier_findings() -> None:
    lines = domain_bootstrap_file._profile_delivery_repair_context_lines(
        {
            "findings": [
                {
                    "class": "source_claim_carrier_offered_but_undelivered",
                    "offered_carriers": ["source_attributed_claim/4"],
                    "missing_signal_keys": ["statement:claim:status"],
                },
                {
                    "class": "source_authority_carrier_partially_delivered",
                    "offered_carriers": ["source_authority/3"],
                },
                {
                    "class": "status_state_carrier_offered_but_undelivered",
                    "offered_carriers": ["appeal_filed/3"],
                },
            ]
        }
    )

    joined = "\n".join(lines)
    assert "PROFILE DELIVERY REPAIR PASS" in joined
    assert "proposal-only" in joined
    assert "source_attributed_claim/4" in joined
    assert "source_authority/3" in joined
    assert "appeal_filed/3" in joined
    assert "statement:claim:status" in joined
    assert "source-to-claim relation" in joined
    assert "governed subject or scope" in joined
    assert "joined state surface" in joined


def test_profile_delivery_repair_ignores_nonrepair_findings() -> None:
    lines = domain_bootstrap_file._profile_delivery_repair_context_lines(
        {
            "findings": [
                {
                    "class": "quantity_carrier_offered_but_undelivered",
                    "offered_carriers": ["event_measurement/4"],
                }
            ]
        }
    )

    assert lines == []


def test_profile_role_roster_repair_context_targets_typed_role_carriers() -> None:
    profile = {
        "candidate_predicates": [
            {"signature": "counsel_for/5", "args": ["proceeding", "person", "organization", "party", "location"]},
            {"signature": "person_role/3", "args": ["person", "role", "organization"]},
            {"signature": "case_status/2", "args": ["case", "status"]},
        ]
    }

    lines = domain_bootstrap_file._profile_role_roster_repair_context_lines(profile)
    joined = "\n".join(lines)

    assert "PROFILE ROLE ROSTER REPAIR PASS" in joined
    assert "proposal-only" in joined
    assert "counsel_for/5" in joined
    assert "person_role/3" in joined
    assert "case_status/2" not in joined
    assert "exact stated office/firm/organization" in joined
    assert "do not collapse an office" in joined
    assert "do not emit source_record_* rows" in joined


def test_profile_role_roster_repair_context_absent_without_role_carriers() -> None:
    profile = {
        "candidate_predicates": [
            {"signature": "case_status/2", "args": ["case", "status"]},
            {"signature": "event_date/2", "args": ["event", "date"]},
        ]
    }

    assert domain_bootstrap_file._profile_role_roster_repair_context_lines(profile) == []


def test_profile_identifier_occurrence_repair_context_targets_identifier_carriers() -> None:
    profile = {
        "candidate_predicates": [
            {
                "signature": "document_identifier_occurrence/5",
                "args": ["document_id", "identifier_kind", "identifier_value", "scope_label", "source_order"],
            },
            {"signature": "case_status/2", "args": ["case", "status"]},
            {"signature": "docket_number/2", "args": ["case", "docket_number"]},
        ]
    }

    lines = domain_bootstrap_file._profile_identifier_occurrence_repair_context_lines(profile)
    joined = "\n".join(lines)

    assert "PROFILE IDENTIFIER OCCURRENCE REPAIR PASS" in joined
    assert "proposal-only" in joined
    assert "document_identifier_occurrence/5" in joined
    assert "docket_number/2" in joined
    assert "case_status/2" not in joined
    assert "same identifier label appears more than once" in joined
    assert "prefix#123456" in joined
    assert "operation_assert" in joined
    assert "never place" in joined
    assert "CARRIER CONTRACT document_identifier_occurrence/5" in joined
    assert "Do not collapse distinct values" in joined
    assert "do not emit source_record_* rows" in joined


def test_profile_identifier_occurrence_repair_context_ignores_footnote_numbers() -> None:
    profile = {
        "candidate_predicates": [
            {"signature": "footnote_content/3", "args": ["document_id", "footnote_number", "content"]},
            {"signature": "procedural_forfeiture/2", "args": ["argument", "reason"]},
            {"signature": "forfeiture_text/2", "args": ["argument_identifier", "text"]},
        ]
    }

    assert domain_bootstrap_file._profile_identifier_occurrence_repair_context_lines(profile) == []


def test_profile_identifier_occurrence_repair_context_absent_without_identifier_carriers() -> None:
    profile = {
        "candidate_predicates": [
            {"signature": "case_status/2", "args": ["case", "status"]},
            {"signature": "event_date/2", "args": ["event", "date"]},
        ]
    }

    assert domain_bootstrap_file._profile_identifier_occurrence_repair_context_lines(profile) == []


def test_source_pass_ops_normalizes_operation_name_suffix_and_missing_source_order() -> None:
    ir = _source_pass_ops_to_semantic_ir(
        {
            "schema_version": "source_pass_ops_v1",
            "decision": "commit",
            "candidate_operations": [
                {
                    "operation": "assert",
                    "proposition_id": "doc_id_001",
                    "predicate": "document_identifier_occurrence/5",
                    "args": [
                        "FedCir_2025-1705_Song",
                        "docket_number",
                        "2025-1705",
                        "header",
                        "predicate_name",
                        "document_identifier_occurrence_5",
                    ],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                }
            ],
            "self_check": {"bad_commit_risk": "low", "missing_slots": [], "notes": []},
        },
        predicate_contracts=[
            {
                "signature": "document_identifier_occurrence/5",
                "args": [
                    "document_id",
                    "identifier_kind",
                    "identifier_value",
                    "occurrence_scope_or_label",
                    "source_order",
                ],
            }
        ],
    )

    assert ir["candidate_operations"][0]["args"] == [
        "FedCir_2025-1705_Song",
        "docket_number",
        "2025-1705",
        "header",
        "1",
    ]


def test_source_pass_ops_uses_contract_arity_when_model_omits_predicate_signature() -> None:
    ir = _source_pass_ops_to_semantic_ir(
        {
            "schema_version": "source_pass_ops_v1",
            "decision": "commit",
            "candidate_operations": [
                {
                    "operation": "assert",
                    "proposition_id": "doc_id_001",
                    "predicate": "document_identifier_occurrence",
                    "args": [
                        "fed_cir_2025_1705_song",
                        "docket_number",
                        "2025_1705",
                        "header",
                    ],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                }
            ],
            "self_check": {"bad_commit_risk": "low", "missing_slots": [], "notes": []},
        },
        predicate_contracts=[
            {
                "signature": "document_identifier_occurrence/5",
                "args": [
                    "document_id",
                    "identifier_kind",
                    "identifier_value",
                    "occurrence_scope_or_label",
                    "source_order",
                ],
            }
        ],
    )

    assert ir["candidate_operations"][0]["args"] == [
        "fed_cir_2025_1705_song",
        "docket_number",
        "2025_1705",
        "header",
        "1",
    ]


def test_source_pass_ops_reads_profile_contract_arguments_alias_for_completion() -> None:
    ir = _source_pass_ops_to_semantic_ir(
        {
            "schema_version": "source_pass_ops_v1",
            "decision": "commit",
            "candidate_operations": [
                {
                    "operation": "assert",
                    "proposition_id": "doc_id_001",
                    "predicate": "document_identifier_occurrence/5",
                    "args": [
                        "fed_cir_2025_1705_song",
                        "docket_number",
                        "2025-1705",
                        "header",
                        "predicate_name",
                        "document_identifier_occurrence/5",
                    ],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                }
            ],
            "self_check": {"bad_commit_risk": "low", "missing_slots": [], "notes": []},
        },
        predicate_contracts=[
            {
                "signature": "document_identifier_occurrence/5",
                "arguments": [
                    "document_id",
                    "identifier_kind",
                    "identifier_value",
                    "occurrence_scope_or_label",
                    "source_order",
                ],
            }
        ],
    )

    assert ir["candidate_operations"][0]["args"] == [
        "fed_cir_2025_1705_song",
        "docket_number",
        "2025-1705",
        "header",
        "1",
    ]


def test_source_pass_ops_replaces_bare_source_order_marker_with_operation_index() -> None:
    ir = _source_pass_ops_to_semantic_ir(
        {
            "schema_version": "source_pass_ops_v1",
            "decision": "commit",
            "candidate_operations": [
                {
                    "operation": "assert",
                    "proposition_id": "doc_id_001",
                    "predicate": "document_identifier_occurrence/5",
                    "args": [
                        "fed_cir_2025_1705_song",
                        "docket_number",
                        "2025-1705",
                        "header",
                        "operation_name",
                    ],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                }
            ],
            "self_check": {"bad_commit_risk": "low", "missing_slots": [], "notes": []},
        },
        predicate_contracts=[
            {
                "signature": "document_identifier_occurrence/5",
                "arguments": [
                    "document_id",
                    "identifier_kind",
                    "identifier_value",
                    "occurrence_scope_or_label",
                    "source_order",
                ],
            }
        ],
    )

    assert ir["candidate_operations"][0]["args"] == [
        "fed_cir_2025_1705_song",
        "docket_number",
        "2025-1705",
        "header",
        "1",
    ]


def test_source_claim_mentions_ignore_sole_source_support_purpose() -> None:
    mentions = domain_bootstrap_file._source_attributed_claim_mentions(
        "One company was solicited for this sole-source requirement pursuant to the authority "
        "set forth in 10 U.S. Code 3204(a)(1) in support of the aircraft platform."
    )

    assert mentions == []


def test_source_claim_mentions_ignore_generic_status_label() -> None:
    assert domain_bootstrap_file._source_attributed_claim_mentions("- **Status:** Ongoing") == []


def test_source_claim_mentions_ignore_document_availability_link() -> None:
    mentions = domain_bootstrap_file._source_attributed_claim_mentions(
        "The factual report is available here: https://example.invalid/report.pdf"
    )

    assert mentions == []
    assert domain_bootstrap_file._source_attributed_claim_mentions(
        "A factual report that may be admissible is available here."
    ) == []


def test_source_claim_key_ignores_available_as_timing_capacity() -> None:
    assert (
        domain_bootstrap_file._source_attributed_claim_signal_key(
            "The statute states the amount of time available to the commission for review."
        )
        == ""
    )


def test_source_claim_mentions_ignore_certification_condition_without_claim_frame() -> None:
    mentions = domain_bootstrap_file._source_attributed_claim_mentions(
        "Within sixty days of receipt of a signed certification on letterhead, the payment obligation begins."
    )

    assert mentions == []


def test_source_claim_mentions_keep_speaker_statement_frame() -> None:
    mentions = domain_bootstrap_file._source_attributed_claim_mentions(
        "**Kowalski:** The draft remains under review and is not binding."
    )

    assert mentions == ["**Kowalski:** The draft remains under review and is not binding."]


def test_source_claim_delivery_does_not_treat_fund_source_as_claim_carrier() -> None:
    candidate = {
        "signature": "fund_source_details/3",
        "args": ["fund_source_id", "fund_description", "expiration_status"],
    }

    assert not domain_bootstrap_file._candidate_can_carry_source_attributed_claim_delivery_unit(candidate)
    assert not domain_bootstrap_file._fact_row_can_deliver_source_attributed_claim(
        "fund_source_details",
        ["navy_working_capital_funds", "fiscal_2026_funds", "not_expiring"],
    )


def test_profile_delivery_accepts_solicitation_authority_rows() -> None:
    source_compile = {
        "unique_fact_count": 1,
        "facts": [
            "solicitation_authority(contract_1, 10_u_s_code_3204_a_1).",
        ],
        "compile_health": {
            "schema_version": "compile_lens_health_v1",
            "verdict": "healthy",
            "recommendation": "qa_run_reasonable",
            "pass_count": 1,
            "unhealthy_pass_count": 0,
            "unhealthy_passes": [],
            "flag_counts": {},
            "unique_contribution_total": 1,
            "duplicate_total": 0,
            "semantic_progress": {"zombie_risk": "low", "recommended_action": "continue"},
        },
    }

    _attach_profile_admission_report(
        source_compile=source_compile,
        domain_hint="source authority procurement contract",
        source_text=(
            "One company was solicited for this sole-source requirement pursuant to the authority "
            "set forth in 10 U.S. Code 3204(a)(1)."
        ),
        parsed_profile={
            "candidate_predicates": [
                {
                    "signature": "solicitation_authority/2",
                    "args": ["contract_id", "authority_code"],
                }
            ]
        },
    )

    assert source_compile["profile_delivery"]["findings"] == []
    assert source_compile["profile_delivery"]["delivered_carriers"]["source_authority"] == [
        "solicitation_authority"
    ]


def test_source_authority_delivery_accepts_legal_basis_rows() -> None:
    assert domain_bootstrap_file._fact_row_can_deliver_source_authority(
        "legal_basis",
        ["claim_a", "statute_1"],
    )


def test_status_state_mentions_ignore_state_as_government_party() -> None:
    mentions = domain_bootstrap_file._status_state_source_mentions(
        "The People of the State of New York brought this action against Defendants."
    )

    assert mentions == []


def test_status_state_mentions_keep_actual_status_value() -> None:
    mentions = domain_bootstrap_file._status_state_source_mentions(
        "The permit application status remained pending as of 2026-04-01."
    )

    assert mentions == ["The permit application status remained pending as of 2026-04-01."]


def test_merge_profile_delivery_repair_pass_adds_unique_rows_and_health() -> None:
    source_compile = {
        "admitted_count": 1,
        "skipped_count": 0,
        "effective_admitted_count": 1,
        "effective_skipped_count": 0,
        "facts": ["base_fact(alpha)."],
        "rules": [],
        "queries": [],
        "surface_contribution": [
            {
                "pass_index": 0,
                "pass_id": "flat_skeleton",
                "purpose": "broad skeleton",
                "focus": "source-wide structure",
                "ok": True,
                "admitted_count": 1,
                "skipped_count": 0,
                "effective_skipped_count": 0,
                "diagnostic_flags": [],
                "fact_count": 1,
                "rule_count": 0,
                "query_count": 0,
                "unique_fact_count": 1,
                "unique_rule_count": 0,
                "unique_query_count": 0,
                "duplicate_count": 0,
                "unique_contribution_count": 1,
                "unique_contribution_ratio": 1.0,
                "health_flags": [],
            }
        ],
    }
    repair_pass = {
        "ok": True,
        "pass_id": "profile_delivery_repair",
        "purpose": "repair direct carrier delivery",
        "focus": "missing carrier rows",
        "admitted_count": 2,
        "skipped_count": 1,
        "facts": [
            "base_fact(alpha).",
            "source_attributed_claim(claim_1, report, status_available, src_line_001).",
        ],
        "rules": [],
        "queries": ["source_attributed_claim(Source, Subject, Claim, Scope)."],
    }

    domain_bootstrap_file._merge_profile_delivery_repair_pass(source_compile, repair_pass)

    assert source_compile["facts"] == [
        "base_fact(alpha).",
        "source_attributed_claim(claim_1, report, status_available, src_line_001).",
    ]
    assert source_compile["unique_fact_count"] == 2
    assert source_compile["admitted_count"] == 3
    assert source_compile["skipped_count"] == 1
    assert source_compile["effective_admitted_count"] == 3
    assert source_compile["effective_skipped_count"] == 1
    assert source_compile["repair_passes"] == [repair_pass]
    assert repair_pass["_profile_delivery_repair_new_facts"] == [
        "source_attributed_claim(claim_1, report, status_available, src_line_001)."
    ]
    assert source_compile["surface_contribution"][-1]["pass_id"] == "profile_delivery_repair"
    assert source_compile["surface_contribution"][-1]["unique_fact_count"] == 1
    assert source_compile["compile_health"]["verdict"] in {"healthy", "warning"}


def test_merge_additive_source_pass_keeps_role_roster_metadata_separate() -> None:
    source_compile = {
        "admitted_count": 1,
        "skipped_count": 0,
        "effective_admitted_count": 1,
        "effective_skipped_count": 0,
        "facts": ["base_fact(alpha)."],
        "rules": [],
        "queries": [],
        "surface_contribution": [],
    }
    repair_pass = {
        "ok": True,
        "pass_id": "profile_role_roster_repair",
        "purpose": "repair typed role and roster delivery",
        "focus": "missing role rows",
        "admitted_count": 2,
        "skipped_count": 0,
        "facts": ["base_fact(alpha).", "person_role(travis_heim, field_technician, dish_network_l_l_c)."],
        "rules": [],
        "queries": [],
    }

    domain_bootstrap_file._merge_additive_source_pass(
        source_compile,
        repair_pass,
        metadata_prefix="profile_role_roster_repair",
    )

    assert repair_pass["_profile_role_roster_repair_new_facts"] == [
        "person_role(travis_heim, field_technician, dish_network_l_l_c)."
    ]
    assert "_profile_delivery_repair_new_facts" not in repair_pass
    assert source_compile["repair_passes"] == [repair_pass]
    assert source_compile["surface_contribution"][-1]["pass_id"] == "profile_role_roster_repair"


def test_source_claim_key_treats_justified_source_statement_as_finding() -> None:
    key = domain_bootstrap_file._source_attributed_claim_fact_key(
        "source_attributed_claim",
        [
            "claim_solberg_scope",
            "solberg",
            "scope_expansion_to_gh_5_is_based_on_the_undisclosed_movement_and_warrants_elevated_sampling",
            "src_line_0037",
        ],
    )

    assert key == "source:claim:finding"


def test_source_claim_delivery_accepts_dispute_subject_for_dispute_claim() -> None:
    assert domain_bootstrap_file._source_claim_key_is_delivered(
        "statement:claim:dispute",
        "statement:dispute:not_flagged",
    )


def test_source_claim_delivery_accepts_party_position_as_statement_claim() -> None:
    assert domain_bootstrap_file._fact_row_can_deliver_source_attributed_claim(
        "party_position",
        ["party_a", "settlement_schedule", "opposed_mandated_process", "initial_comment"],
    )
    assert domain_bootstrap_file._source_claim_key_is_delivered(
        "statement:claim:objection",
        domain_bootstrap_file._source_attributed_claim_fact_key(
            "party_position",
            ["party_a", "settlement_schedule", "opposed_mandated_process", "initial_comment"],
        ),
    )


def test_vote_tally_text_ignores_document_ids_near_vote_language() -> None:
    assert not domain_bootstrap_file._vote_tally_text(
        "Counsel Memorandum HFF-CC-2026-0416 dated April 16, 2026 says the award is available."
    )
    assert not domain_bootstrap_file._vote_tally_signal_key("Correction memo HFF-CC-2026-0415 was circulated.")
    assert domain_bootstrap_file._vote_tally_signal_key("Motion vote recorded 4-3 after abstention.") == "vote:4_3"


def test_vote_tally_key_uses_tally_argument_before_date_bearing_vote_id() -> None:
    assert (
        domain_bootstrap_file._vote_tally_fact_key(
            "vote_tally",
            [
                "vote_april_24_2026_variance",
                "org_zba",
                "variance_approval_42_osprey",
                "approved",
                "3_1_hoffman_yee_castellano_kowalski",
            ],
        )
        == "approved:3_1"
    )


def test_source_claim_delivery_accepts_counsel_opinion_rows() -> None:
    source_compile = {
        "unique_fact_count": 1,
        "facts": [
            "counsel_opinion(hff_cc_2026_0415, app_s26_003, eligible_under_3_07_b_78_percent_beneficiaries).",
        ],
        "compile_health": {
            "schema_version": "compile_lens_health_v1",
            "verdict": "healthy",
            "recommendation": "qa_run_reasonable",
            "pass_count": 1,
            "unhealthy_pass_count": 0,
            "unhealthy_passes": [],
            "flag_counts": {},
            "unique_contribution_total": 1,
            "duplicate_total": 0,
            "semantic_progress": {"zombie_risk": "low", "recommended_action": "continue"},
        },
    }

    _attach_profile_admission_report(
        source_compile=source_compile,
        domain_hint="grant counsel opinion eligibility",
        source_text="Counsel opinion says the applicant is eligible under section 3.07(b).",
        parsed_profile={
            "candidate_predicates": [
                {
                    "signature": "counsel_opinion/3",
                    "args": ["document", "subject", "opinion"],
                }
            ]
        },
    )

    assert source_compile["profile_delivery"]["findings"] == []
    assert source_compile["profile_delivery"]["delivered_carriers"]["source_attributed_claim"] == ["counsel_opinion"]


def test_source_claim_delivery_accepts_source_attributed_legal_fact_rows() -> None:
    source_compile = {
        "unique_fact_count": 1,
        "facts": [
            "source_attributed_legal_fact(opinion_1, finding_scope, legal_opinion_available, src_line_0010).",
        ],
        "compile_health": {
            "schema_version": "compile_lens_health_v1",
            "verdict": "healthy",
            "recommendation": "qa_run_reasonable",
            "pass_count": 1,
            "unhealthy_pass_count": 0,
            "unhealthy_passes": [],
            "flag_counts": {},
            "unique_contribution_total": 1,
            "duplicate_total": 0,
            "semantic_progress": {"zombie_risk": "low", "recommended_action": "continue"},
        },
    }

    _attach_profile_admission_report(
        source_compile=source_compile,
        domain_hint="source claim legal opinion source attribution",
        source_text="Source record preserves legal-opinion attribution.",
        parsed_profile={
            "candidate_predicates": [
                {
                    "signature": "source_attributed_legal_fact/4",
                    "args": ["source", "subject", "claim_or_finding", "scope"],
                }
            ]
        },
    )

    assert source_compile["profile_delivery"]["findings"] == []
    assert source_compile["profile_delivery"]["delivered_carriers"]["source_attributed_claim"] == [
        "source_attributed_legal_fact"
    ]


def test_status_state_delivery_accepts_direct_appeal_filing_rows() -> None:
    source_compile = {
        "unique_fact_count": 1,
        "facts": ["appeal_filed(party_a, order_17, 2026_01_20)."],
        "compile_health": {
            "schema_version": "compile_lens_health_v1",
            "verdict": "healthy",
            "recommendation": "qa_run_reasonable",
            "pass_count": 1,
            "unhealthy_pass_count": 0,
            "unhealthy_passes": [],
            "flag_counts": {},
            "unique_contribution_total": 1,
            "duplicate_total": 0,
            "semantic_progress": {"zombie_risk": "low", "recommended_action": "continue"},
        },
    }

    _attach_profile_admission_report(
        source_compile=source_compile,
        domain_hint="status/state appeal filing status",
        source_text="Party A filed a formal appeal of Order 17 on January 20, 2026.",
        parsed_profile={
            "candidate_predicates": [
                {
                    "signature": "appeal_filed/3",
                    "args": ["appellant", "target_or_subject", "date_or_status"],
                }
            ]
        },
    )

    assert source_compile["profile_delivery"]["findings"] == []
    assert source_compile["profile_delivery"]["delivered_carriers"]["status_state"] == ["appeal_filed"]


def test_status_state_delivery_accepts_conditional_rule_rows() -> None:
    assert domain_bootstrap_file._candidate_can_carry_status_state_delivery_unit(
        {
            "signature": "payment_reduction_rule/3",
            "args": ["obligation_id", "reduction_amount", "trigger_event"],
        }
    )
    assert domain_bootstrap_file._fact_row_can_deliver_status_state(
        "conditional_rule",
        ["rule_a", "condition_met", "payment_not_owed", "source_row_17"],
    )
    assert domain_bootstrap_file._fact_row_can_deliver_status_state(
        "reduction_rule",
        ["obligation_a", "item_removed", "750", "per_item", "source_row_18"],
    )
    assert domain_bootstrap_file._fact_row_can_deliver_status_state(
        "vehicle_action",
        ["item_a", "removed_from_commerce", "2026_01_01", "source_row_19"],
    )
    assert domain_bootstrap_file._fact_row_can_deliver_status_state(
        "mandate_utility",
        ["utility_a", "issue_notice", "2026_03_01", "rate_cases_filed_on_or_after_date"],
    )
    assert domain_bootstrap_file._fact_row_can_deliver_status_state(
        "payment_reduction_rule",
        ["suspended_payment", "750", "vehicle_receives_modification"],
    )


def test_profile_delivery_accepts_emitted_quantity_carrier_rows() -> None:
    source_compile = {
        "unique_fact_count": 3,
        "facts": [
            "event_measurement(ev_01, feed_rate, 18, kg_min).",
            "event_measurement(ev_02, setpoint_before, 480, k).",
            "event_measurement(ev_02, setpoint_after, 495, k).",
        ],
        "compile_health": {
            "schema_version": "compile_lens_health_v1",
            "verdict": "healthy",
            "recommendation": "qa_run_reasonable",
            "pass_count": 1,
            "unhealthy_pass_count": 0,
            "unhealthy_passes": [],
            "flag_counts": {},
            "unique_contribution_total": 2,
            "duplicate_total": 0,
            "semantic_progress": {"zombie_risk": "low", "recommended_action": "continue"},
        },
    }

    _attach_profile_admission_report(
        source_compile=source_compile,
        domain_hint="instrument readings and measurement events",
        source_text=(
            "EV-01 2026-04-22 feed rate increased to 18 kg min.\n"
            "EV-02 2026-04-22 setpoint changed from 480 k to 495 k."
        ),
        parsed_profile={
            "candidate_predicates": [
                {
                    "signature": "event_measurement/4",
                    "args": ["event_id", "measure", "value", "unit"],
                },
            ]
        },
    )

    assert source_compile["profile_delivery"]["findings"] == []
    assert source_compile["profile_delivery"]["delivered_carriers"]["quantity_event"] == ["event_measurement"]
    assert source_compile["compile_health"]["verdict"] == "healthy"


def test_profile_delivery_counts_before_after_quantity_rows() -> None:
    source_compile = {
        "unique_fact_count": 3,
        "facts": [
            "event_measurement(ev_01, setpoint_before, 480, k).",
            "event_measurement(ev_01, setpoint_after, 495, k).",
            "event_measurement(ev_02, feed_rate, 18.4, kg_min).",
        ],
        "compile_health": {
            "schema_version": "compile_lens_health_v1",
            "verdict": "healthy",
            "recommendation": "qa_run_reasonable",
            "pass_count": 1,
            "unhealthy_pass_count": 0,
            "unhealthy_passes": [],
            "flag_counts": {},
            "unique_contribution_total": 3,
            "duplicate_total": 0,
            "semantic_progress": {"zombie_risk": "low", "recommended_action": "continue"},
        },
    }

    _attach_profile_admission_report(
        source_compile=source_compile,
        domain_hint="instrument readings and measurement events",
        source_text=(
            "EV-01 2026-04-22 setpoint changed from 480 k to 495 k.\n"
            "EV-02 2026-04-22 feed rate increased to 18.4 kg min.\n"
            "EV-06 2026-04-22 setpoint reverted from 495 k to 480 k."
        ),
        parsed_profile={
            "candidate_predicates": [
                {
                    "signature": "event_measurement/4",
                    "args": ["event_id", "measure", "value", "unit"],
                },
            ]
        },
    )

    delivery = source_compile["profile_delivery"]
    assert delivery["source_signal_counts"]["quantity_event"] == 3
    assert delivery["carrier_row_requirements"]["quantity_event"] == 5
    finding = delivery["findings"][0]
    assert finding["class"] == "quantity_carrier_partially_delivered"
    assert finding["required_carrier_row_count"] == 5
    assert finding["missing_carrier_row_count"] == 2
    assert finding["missing_signal_keys"] == ["event:ev_06:setpoint"]
    assert finding["required_signal_key_counts"]["event:ev_01:setpoint"] == 2
    assert finding["delivered_signal_key_counts"]["event:ev_01:setpoint"] == 2


def test_profile_delivery_names_missing_line_stop_duration_quantity_key() -> None:
    source_compile = {
        "unique_fact_count": 5,
        "facts": [
            "event_measurement(ev_01, setpoint_before, 480, k).",
            "event_measurement(ev_01, setpoint_after, 495, k).",
            "event_measurement(ev_02, feed_rate, 18.4, kg_min).",
            "event_measurement(ev_06, setpoint_before, 495, k).",
            "event_measurement(ev_06, setpoint_after, 480, k).",
        ],
        "compile_health": {
            "schema_version": "compile_lens_health_v1",
            "verdict": "healthy",
            "recommendation": "qa_run_reasonable",
            "pass_count": 1,
            "unhealthy_pass_count": 0,
            "unhealthy_passes": [],
            "flag_counts": {},
            "unique_contribution_total": 5,
            "duplicate_total": 0,
            "semantic_progress": {"zombie_risk": "low", "recommended_action": "continue"},
        },
    }

    _attach_profile_admission_report(
        source_compile=source_compile,
        domain_hint="instrument readings and measurement events",
        source_text=(
            "EV-01 2026-04-22 setpoint changed from 480 k to 495 k.\n"
            "EV-02 2026-04-22 feed rate increased to 18.4 kg min.\n"
            "EV-06 2026-04-22 setpoint reverted from 495 k to 480 k.\n"
            "The line-stop duration between EV-10 and EV-14 is 17 hours 45 minutes 52 seconds."
        ),
        parsed_profile={
            "candidate_predicates": [
                {
                    "signature": "event_measurement/4",
                    "args": ["event_id", "measure", "value", "unit"],
                },
            ]
        },
    )

    finding = source_compile["profile_delivery"]["findings"][0]
    assert finding["missing_signal_keys"] == ["duration:line_stop"]


def test_profile_delivery_accepts_source_local_event_duration_carrier() -> None:
    source_compile = {
        "unique_fact_count": 1,
        "facts": [
            "event_duration(17_hours_45_minutes_52_seconds, ev_10, ev_14).",
        ],
        "compile_health": {
            "schema_version": "compile_lens_health_v1",
            "verdict": "healthy",
            "recommendation": "qa_run_reasonable",
            "pass_count": 1,
            "unhealthy_pass_count": 0,
            "unhealthy_passes": [],
            "flag_counts": {},
            "unique_contribution_total": 1,
            "duplicate_total": 0,
            "semantic_progress": {"zombie_risk": "low", "recommended_action": "continue"},
        },
    }

    _attach_profile_admission_report(
        source_compile=source_compile,
        domain_hint="instrument readings and measurement events",
        source_text="Line-stop duration between EV-10 and EV-14 is 17 hours 45 minutes 52 seconds.",
        parsed_profile={
            "candidate_predicates": [
                {
                    "signature": "event_duration/3",
                    "args": ["duration_value", "start_event_id", "end_event_id"],
                },
            ]
        },
    )

    assert source_compile["profile_delivery"]["findings"] == []
    assert source_compile["profile_delivery"]["delivered_carriers"]["quantity_event"] == ["event_duration"]
    assert source_compile["compile_health"]["verdict"] == "healthy"


def test_profile_delivery_dedupes_repeated_line_stop_duration_surface() -> None:
    source_compile = {
        "unique_fact_count": 6,
        "facts": [
            "event_measurement(ev_01, setpoint_before, 480, k).",
            "event_measurement(ev_01, setpoint_after, 495, k).",
            "event_measurement(ev_02, feed_rate, 18.4, kg_min).",
            "event_measurement(ev_06, setpoint_before, 495, k).",
            "event_measurement(ev_06, setpoint_after, 480, k).",
            "line_state(line_stop, ev_10, ev_14, 17_hours_45_minutes_52_seconds).",
        ],
        "compile_health": {
            "schema_version": "compile_lens_health_v1",
            "verdict": "healthy",
            "recommendation": "qa_run_reasonable",
            "pass_count": 1,
            "unhealthy_pass_count": 0,
            "unhealthy_passes": [],
            "flag_counts": {},
            "unique_contribution_total": 6,
            "duplicate_total": 0,
            "semantic_progress": {"zombie_risk": "low", "recommended_action": "continue"},
        },
    }

    _attach_profile_admission_report(
        source_compile=source_compile,
        domain_hint="instrument readings and measurement events",
        source_text=(
            "EV-01 2026-04-22 setpoint changed from 480 k to 495 k.\n"
            "EV-02 2026-04-22 feed rate increased to 18.4 kg min.\n"
            "EV-06 2026-04-22 setpoint reverted from 495 k to 480 k.\n"
            "duration: 17 hours 45 minutes 52 seconds. The line-stop interval is continuous.\n"
            "The line-stop duration between EV-10 and EV-14 is 17 hours 45 minutes 52 seconds."
        ),
        parsed_profile={
            "candidate_predicates": [
                {
                    "signature": "event_measurement/4",
                    "args": ["event_id", "measure", "value", "unit"],
                },
                {
                    "signature": "line_state/4",
                    "args": ["state", "start_event_id", "end_event_id", "duration"],
                },
            ]
        },
    )

    delivery = source_compile["profile_delivery"]
    assert delivery["source_signal_counts"]["quantity_event"] == 5
    assert delivery["carrier_row_requirements"]["quantity_event"] == 6
    assert delivery["delivered_carrier_row_counts"]["quantity_event"] == 6
    assert delivery["findings"] == []
    assert delivery["delivered_carriers"]["quantity_event"] == ["event_measurement", "line_state"]
    assert source_compile["compile_health"]["verdict"] == "healthy"


def test_profile_delivery_accepts_named_duration_carrier_with_thin_candidate_args() -> None:
    source_compile = {
        "unique_fact_count": 1,
        "facts": [
            "line_stop_duration(line_4, 17_hours_45_minutes_52_seconds).",
        ],
        "compile_health": {
            "schema_version": "compile_lens_health_v1",
            "verdict": "healthy",
            "recommendation": "qa_run_reasonable",
            "pass_count": 1,
            "unhealthy_pass_count": 0,
            "unhealthy_passes": [],
            "flag_counts": {},
            "unique_contribution_total": 1,
            "duplicate_total": 0,
            "semantic_progress": {"zombie_risk": "low", "recommended_action": "continue"},
        },
    }

    _attach_profile_admission_report(
        source_compile=source_compile,
        domain_hint="instrument readings and measurement events",
        source_text="The line-stop duration between EV-10 and EV-14 is 17 hours 45 minutes 52 seconds.",
        parsed_profile={
            "candidate_predicates": [
                {
                    "signature": "line_stop_duration/2",
                    "args": ["duration"],
                },
            ]
        },
    )

    assert source_compile["profile_delivery"]["findings"] == []
    assert source_compile["profile_delivery"]["delivered_carriers"]["quantity_event"] == ["line_stop_duration"]


def test_profile_delivery_flags_date_bearing_event_identifier_without_temporal_row() -> None:
    source_compile = {
        "unique_fact_count": 2,
        "facts": [
            "event_occurred(ev_emergency_declaration_2026_05_12, emergency_declaration).",
            "event_outcome(ev_ratification_2026_05_14, ratified).",
        ],
        "compile_health": {
            "schema_version": "compile_lens_health_v1",
            "verdict": "healthy",
            "recommendation": "qa_run_reasonable",
            "pass_count": 1,
            "unhealthy_pass_count": 0,
            "unhealthy_passes": [],
            "flag_counts": {},
            "unique_contribution_total": 2,
            "duplicate_total": 0,
            "semantic_progress": {"zombie_risk": "low", "recommended_action": "continue"},
        },
    }

    _attach_profile_admission_report(
        source_compile=source_compile,
        domain_hint="operational record status lifecycle",
        source_text=(
            "Emergency declaration occurred on 2026-05-12.\n"
            "Ratification occurred on 2026-05-14."
        ),
        parsed_profile={"candidate_predicates": []},
    )

    delivery = source_compile["profile_delivery"]
    assert delivery["temporal_backbone"]["missing_event_id_count"] == 2
    assert delivery["findings"][0]["class"] == "event_identifier_date_only"
    assert delivery["findings"][0]["missing_event_ids"] == [
        "ev_emergency_declaration_2026_05_12",
        "ev_ratification_2026_05_14",
    ]
    health = source_compile["compile_health"]
    assert health["flag_counts"]["event_identifier_date_only"] == 1
    assert "profile_delivery" in health["unhealthy_passes"]


def test_profile_delivery_accepts_date_bearing_event_identifier_with_temporal_row() -> None:
    source_compile = {
        "unique_fact_count": 4,
        "facts": [
            "event_occurred(ev_emergency_declaration_2026_05_12, emergency_declaration).",
            "event_date(ev_emergency_declaration_2026_05_12, 2026_05_12).",
            "event_outcome(ev_ratification_2026_05_14, ratified).",
            "event_date(ev_ratification_2026_05_14, 2026_05_14).",
        ],
        "compile_health": {
            "schema_version": "compile_lens_health_v1",
            "verdict": "healthy",
            "recommendation": "qa_run_reasonable",
            "pass_count": 1,
            "unhealthy_pass_count": 0,
            "unhealthy_passes": [],
            "flag_counts": {},
            "unique_contribution_total": 4,
            "duplicate_total": 0,
            "semantic_progress": {"zombie_risk": "low", "recommended_action": "continue"},
        },
    }

    _attach_profile_admission_report(
        source_compile=source_compile,
        domain_hint="operational record status lifecycle",
        source_text=(
            "Emergency declaration occurred on 2026-05-12.\n"
            "Ratification occurred on 2026-05-14."
        ),
        parsed_profile={"candidate_predicates": []},
    )

    delivery = source_compile["profile_delivery"]
    assert delivery["temporal_backbone"]["covered_event_id_count"] == 2
    assert delivery["temporal_backbone"]["missing_event_id_count"] == 0
    assert delivery["findings"] == []
    assert source_compile["compile_health"]["verdict"] == "healthy"


def test_profile_delivery_ignores_long_date_bearing_finding_labels_as_event_ids() -> None:
    source_compile = {
        "unique_fact_count": 1,
        "facts": [
            (
                "investigation_finding(cause_of_humidity_alarm_at_ev_03_is_unresolved_"
                "missing_feedstock_moisture_analysis_lab_2026_0422_s3_and_dryer_airflow_logs, unresolved)."
            ),
        ],
        "compile_health": {
            "schema_version": "compile_lens_health_v1",
            "verdict": "healthy",
            "recommendation": "qa_run_reasonable",
            "pass_count": 1,
            "unhealthy_pass_count": 0,
            "unhealthy_passes": [],
            "flag_counts": {},
            "unique_contribution_total": 1,
            "duplicate_total": 0,
            "semantic_progress": {"zombie_risk": "low", "recommended_action": "continue"},
        },
    }

    _attach_profile_admission_report(
        source_compile=source_compile,
        domain_hint="operational record status lifecycle",
        source_text="The cause of humidity alarm EV-03 is unresolved pending lab 2026-0422-S3.",
        parsed_profile={"candidate_predicates": []},
    )

    delivery = source_compile["profile_delivery"]
    assert delivery["temporal_backbone"]["missing_event_id_count"] == 0
    assert delivery["findings"] == []
    assert source_compile["compile_health"]["verdict"] == "healthy"


def test_profile_admission_warning_is_operational_context_bounded() -> None:
    source_compile = {
        "unique_fact_count": 5,
        "compile_health": {
            "schema_version": "compile_lens_health_v1",
            "verdict": "healthy",
            "recommendation": "qa_run_reasonable",
            "pass_count": 1,
            "unhealthy_pass_count": 0,
            "unhealthy_passes": [],
            "flag_counts": {},
            "unique_contribution_total": 5,
            "duplicate_total": 0,
            "semantic_progress": {"zombie_risk": "low", "recommended_action": "continue"},
        },
    }

    _attach_profile_admission_report(
        source_compile=source_compile,
        domain_hint="literary character status",
        source_text=(
            "On 2026-03-01 record R-1 status was pending.\n"
            "On 2026-03-04 record R-1 status was approved."
        ),
        parsed_profile={
            "candidate_predicates": [
                {"signature": "record_status/2", "args": ["record_id", "status"]},
                {"signature": "event_date/3", "args": ["record_id", "event_type", "date"]},
            ]
        },
    )

    assert "profile_admission" not in source_compile
    assert source_compile["compile_health"]["verdict"] == "healthy"


def test_invalid_profile_retry_context_blocks_arg_role_runaway() -> None:
    context = _invalid_profile_retry_context(
        parse_error="json_error:bad comma",
        raw_content='"args":["plaintiff_id_ref_entity_type_1_2_3_4_5"]',
        max_predicates=12,
    )

    joined = "\n".join(context)
    assert "at most 12 unique predicate signatures" in joined
    assert "candidate_predicates[].args are short structural role labels only" in joined
    assert "argument-role runaway" in joined
    assert "entity_type_N counters" in joined


def test_profile_schema_contract_retry_context_blocks_six_slot_drift() -> None:
    score = {
        "candidate_signature_arg_mismatch_refs": ["financial_result/6:args=5"],
    }
    context = _profile_schema_contract_retry_context(score)

    joined = "\n".join(context)
    assert _profile_schema_contract_retry_needed(score) is True
    assert "support /1 through /5 only" in joined
    assert "Do not propose /6 or higher" in joined
    assert "separate provenance/source-coordinate predicate" in joined
    assert "financial_result/6:args=5" in joined


def test_profile_schema_contract_retry_context_blocks_repeated_role_mismatch() -> None:
    score = {
        "repeated_structure_role_mismatch_refs": ["remand_to/2"],
    }
    context = _profile_schema_contract_retry_context(score)

    joined = "\n".join(context)
    assert _profile_schema_contract_retry_needed(score) is True
    assert "Repeated-structure guardrail" in joined
    assert "first argument role must be the repeated record id or governed subject" in joined
    assert "do not use the global case id as a substitute" in joined
    assert "remand_to/2" in joined


def test_profile_from_signature_roster_uses_generic_args() -> None:
    profile = _profile_from_signature_roster(
        {
            "schema_version": "profile_signature_roster_v1",
            "domain_guess": "legal_docket",
            "domain_scope": "Docket state and deadlines.",
            "confidence": 0.7,
            "source_summary": ["Compact profile."],
            "entity_types": [{"name": "case", "description": "Case record."}],
            "candidate_signatures": [
                {
                    "signature": "case_info/4",
                    "description": "Case metadata.",
                    "admission_notes": ["source-bound"],
                },
                {
                    "signature": "case_info/4",
                    "description": "duplicate",
                    "admission_notes": [],
                },
                {
                    "signature": "bad/9",
                    "description": "ignored",
                    "admission_notes": [],
                },
            ],
            "repeated_structures": [
                {
                    "name": "docket entries",
                    "record_predicate": "docket_event/4",
                    "property_predicates": ["event_date/2"],
                }
            ],
            "admission_risks": ["deadline/fact collapse"],
            "clarification_policy": [],
            "unsafe_transformations": [],
            "self_check": {"notes": ["fallback"]},
        }
    )

    assert profile is not None
    assert profile["schema_version"] == "profile_bootstrap_v1"
    assert profile["candidate_predicates"][0]["signature"] == "case_info/4"
    assert profile["candidate_predicates"][0]["args"] == ["arg_1", "arg_2", "arg_3", "arg_4"]
    assert len(profile["candidate_predicates"]) == 1
    assert profile["repeated_structures"][0]["record_predicate"] == "docket_event/4"
    assert "compact_signature_roster_fallback" in profile["self_check"]["notes"]


def test_profile_registry_palette_report_counts_signature_and_arity_drift() -> None:
    report = _profile_registry_palette_report(
        profile_registry={
            "predicates": [
                {"signature": "entity_assignment/3"},
                {"signature": "status_phase/2"},
            ]
        },
        parsed_profile={
            "candidate_predicates": [
                {"signature": "entity_assignment/4"},
                {"signature": "status_phase/2"},
                {"signature": "source_capture/4"},
            ]
        },
    )

    assert report["registry_signature_count"] == 2
    assert report["profile_signature_count"] == 3
    assert report["overlap_signatures"] == ["status_phase/2"]
    assert report["missing_registry_signatures"] == ["entity_assignment/3"]
    assert report["extra_profile_signatures"] == ["entity_assignment/4", "source_capture/4"]
    assert report["same_name_changed_arity"] == [
        {
            "predicate": "entity_assignment",
            "registry_arities": [3],
            "profile_arities": [4],
        }
    ]


def test_profile_registry_for_lens_filters_predicates_and_requirements() -> None:
    filtered = _profile_registry_for_lens(
        {
            "lenses": [
                {
                    "id": "wrapper",
                    "purpose": "Wrapper facts only.",
                    "allowed_signatures": [
                        "fda_warning_letter/5",
                        "fda_correspondence_party/5",
                        "domain_omission/5",
                    ],
                },
                {
                    "id": "violation",
                    "allowed_signatures": ["fda_violation_detail/5"],
                },
            ],
            "predicates": [
                {"signature": "fda_warning_letter/5"},
                {"signature": "fda_correspondence_party/5"},
                {"signature": "fda_violation_detail/5"},
                {"signature": "domain_omission/5"},
            ],
            "accountability_requirements": [
                {
                    "id": "missing_signatory_role",
                    "carrier_signature": "fda_correspondence_party/5",
                    "omission_kind": "role_missing",
                    "reason_code": "signatory_not_stated",
                },
                {
                    "id": "missing_violation_detail",
                    "carrier_signature": "fda_violation_detail/5",
                    "omission_kind": "detail_missing",
                    "reason_code": "not_found",
                },
            ],
        },
        "wrapper",
    )

    assert [item["signature"] for item in filtered["predicates"]] == [
        "fda_warning_letter/5",
        "fda_correspondence_party/5",
        "domain_omission/5",
    ]
    assert [item["id"] for item in filtered["accountability_requirements"]] == ["missing_signatory_role"]
    assert filtered["active_lens"]["id"] == "wrapper"
    assert filtered["active_lens"]["predicate_count"] == 3


def test_profile_registry_for_lens_requires_known_lens() -> None:
    try:
        _profile_registry_for_lens({"lenses": [{"id": "wrapper"}], "predicates": []}, "chronology")
    except ValueError as exc:
        assert "unknown profile registry lens" in str(exc)
        assert "wrapper" in str(exc)
    else:
        raise AssertionError("unknown lens did not fail")


def test_profile_registry_for_lens_strips_omission_without_requirement() -> None:
    filtered = _profile_registry_for_lens(
        {
            "lenses": [
                {
                    "id": "conclusion",
                    "allowed_signatures": ["fda_conclusion_scope/4", "domain_omission/5"],
                }
            ],
            "predicates": [
                {"signature": "fda_conclusion_scope/4"},
                {"signature": "domain_omission/5"},
            ],
            "accountability_requirements": [],
        },
        "conclusion",
    )

    assert [item["signature"] for item in filtered["predicates"]] == ["fda_conclusion_scope/4"]
    assert filtered["active_lens"]["declared_allowed_signatures"] == [
        "domain_omission/5",
        "fda_conclusion_scope/4",
    ]
    assert filtered["active_lens"]["allowed_signatures"] == ["fda_conclusion_scope/4"]
    assert filtered["active_lens"]["accountability_requirement_count"] == 0


def test_profile_registry_lens_limits_direct_profile_and_completion_context() -> None:
    registry = _profile_registry_for_lens(
        {
            "lenses": [
                {
                    "id": "chronology",
                    "allowed_signatures": [
                        "fda_inspection_event/6",
                        "fda_form483_response/4",
                        "domain_omission/5",
                    ],
                }
            ],
            "predicates": [
                {"signature": "fda_inspection_event/6", "category": "chronology"},
                {"signature": "fda_form483_response/4", "category": "chronology"},
                {"signature": "fda_violation_detail/5", "category": "violation"},
                {"signature": "domain_omission/5", "category": "compile_accountability"},
            ],
        },
        "chronology",
    )

    profile = domain_bootstrap_file._profile_from_registry(registry, domain_hint="fda")
    profile_signatures = [
        item["signature"]
        for item in profile["candidate_predicates"]
        if isinstance(item, dict)
    ]
    assert profile_signatures == [
        "fda_inspection_event/6",
        "fda_form483_response/4",
    ]

    context = _profile_registry_completion_context_lines(registry, {"facts": []})
    joined = "\n".join(context)
    assert "fda_inspection_event/6" in joined
    assert "fda_form483_response/4" in joined
    assert "domain_omission/5 in this pass" in joined
    assert "fda_violation_detail/5" not in joined


def test_profile_registry_palette_prior_context_is_vocabulary_only() -> None:
    context = _profile_registry_palette_prior_context(
        {
            "predicates": [
                {"signature": "entity_assignment/3", "args": ["entity", "scope", "target"]},
                {"signature": "bad/9", "args": ["ignored"]},
            ]
        }
    )

    joined = "\n".join(context)
    assert "vocabulary-only" in joined
    assert "does not supply facts" in joined
    assert "zero-yield" in joined
    assert "entity_assignment/3" in joined
    assert "bad/9" not in joined


def test_profile_registry_accountability_context_requires_typed_omission_rows() -> None:
    context = _profile_registry_accountability_context(
        {
            "accountability_requirements": [
                {
                    "carrier_signature": "fda_correspondence_party/5",
                    "omission_kind": "role_missing",
                    "reason_code": "signatory_not_stated",
                    "trigger": "source_explicitly_states_no_signatory_or_signature_block",
                }
            ]
        }
    )

    joined = "\n".join(context)
    assert "omission contracts, not facts" in joined
    assert "domain_omission(DomainOrSubjectId, 'fda_correspondence_party/5'" in joined
    assert "role_missing" in joined
    assert "signatory_not_stated" in joined
    assert "do not rewrite it as an underscore atom" in joined
    assert "Do not leave this only in self_check" in joined


def test_profile_registry_completion_context_is_closed_registry_only() -> None:
    context = _profile_registry_completion_context_lines(
        {
            "predicates": [
                {"signature": "fda_warning_letter/5", "category": "wrapper", "notes": "Wrapper note."},
                {"signature": "fda_violation_detail/5", "category": "detail", "notes": "Detail note."},
                {"signature": "domain_omission/5"},
                {"signature": "made_up/3"},
            ]
        },
        {
            "facts": [
                "fda_warning_letter(letter_1, fda, acme_inc, v_2026_01_01, src_line_1).",
                "domain_omission(letter_1, 'fda_correspondence_party/5', role_missing, signatory_not_stated, src_line_2).",
            ]
        },
    )

    joined = "\n".join(context)
    assert "closed predicate registry" in joined
    assert "do not emit source_record_* rows" in joined
    assert "fda_warning_letter/5" in joined
    assert "fda_violation_detail/5" in joined
    assert "domain_omission/5 in this pass" in joined
    assert "made_up/3" not in joined
    assert "existing_fact: fda_warning_letter" in joined
    assert "existing_fact: domain_omission" not in joined
    assert "SIGNATURE NOTE: fda_violation_detail/5: category=detail; notes=Detail note." in joined


def test_profile_registry_completion_followup_rejects_outside_registry(monkeypatch) -> None:
    source_compile = {
        "facts": ["fda_warning_letter(letter_1, fda, acme_inc, v_2026_01_01, src_line_1)."],
        "rules": [],
        "queries": [],
        "admitted_count": 1,
        "skipped_count": 0,
    }
    registry = {
        "predicates": [
            {"signature": "fda_warning_letter/5"},
            {"signature": "fda_violation_detail/5"},
            {"signature": "domain_omission/5"},
        ]
    }

    def fake_compile_source_pass_ops(**kwargs):
        assert kwargs["pass_id"] == "profile_registry_completion_followup"
        assert "domain_omission/5" not in kwargs["predicates"]
        assert all(
            str(item.get("signature", "")).strip() != "domain_omission/5"
            for item in kwargs["parsed_profile"]["candidate_predicates"]
            if isinstance(item, dict)
        )
        assert kwargs["operation_target"] == 12
        return {
            "ok": True,
            "admitted_count": 2,
            "skipped_count": 0,
            "facts": [
                "fda_violation_detail(violation_1, missing_record_type, batch_production_records, pre_release_quality_review, src_line_12).",
                "source_record_text(row_12, prose).",
            ],
            "rules": [],
            "queries": [],
        }

    monkeypatch.setattr(domain_bootstrap_file, "_compile_source_pass_ops", fake_compile_source_pass_ops)

    result = _apply_profile_registry_completion_followup_pass(
        source_compile=source_compile,
        parsed_profile={"candidate_predicates": []},
        profile_registry=registry,
        source_text="The quality unit failed to review batch production records.",
        intake_plan={},
        args=type("Args", (), {"focused_pass_operation_target": 12})(),
        extra_context=[],
    )

    assert result["attempted"] is True
    assert result["new_fact_count"] == 1
    assert result["signature_contract"]["rejected_count"] == 1
    assert source_compile["facts"] == [
        "fda_warning_letter(letter_1, fda, acme_inc, v_2026_01_01, src_line_1).",
        "fda_violation_detail(violation_1, missing_record_type, batch_production_records, pre_release_quality_review, src_line_12).",
    ]


def test_profile_registry_accountability_followup_context_is_domain_omission_only() -> None:
    context = _profile_registry_accountability_followup_context_lines(
        {
            "accountability_requirements": [
                {
                    "id": "missing_signatory_role",
                    "carrier_signature": "fda_correspondence_party/5",
                    "omission_kind": "role_missing",
                    "reason_code": "signatory_not_stated",
                    "trigger": "source_explicitly_states_no_signatory_or_signature_block",
                }
            ]
        }
    )

    joined = "\n".join(context)
    assert "domain_omission/5 rows only" in joined
    assert "It must not emit source_record_* rows" in joined
    assert "'fda_correspondence_party/5'" in joined
    assert "Do not rewrite slash signatures as underscore atoms" in joined
    assert "CARRIER CONTRACT domain_omission/5" in joined


def test_profile_registry_accountability_followup_rejects_non_omission_rows(monkeypatch) -> None:
    source_compile = {
        "facts": ["fda_warning_letter(letter_1, cder, acme_inc, v_2026_01_01, src_line_1)."],
        "rules": [],
        "queries": [],
        "admitted_count": 1,
        "skipped_count": 0,
    }
    profile = {
        "candidate_predicates": [
            {"signature": "domain_omission/5"},
            {"signature": "fda_correspondence_party/5"},
        ]
    }
    registry = {
        "accountability_requirements": [
            {
                "id": "missing_signatory_role",
                "carrier_signature": "fda_correspondence_party/5",
                "omission_kind": "role_missing",
                "reason_code": "signatory_not_stated",
                "trigger": "source_explicitly_states_no_signatory_or_signature_block",
            }
        ]
    }

    def fake_compile_source_pass_ops(**kwargs):
        assert kwargs["pass_id"] == "profile_registry_accountability_followup"
        assert kwargs["predicates"] == "domain_omission/5"
        assert kwargs["operation_target"] == 8
        assert "domain_omission/5 rows only" in "\n".join(kwargs["extra_context"])
        return {
            "ok": True,
            "admitted_count": 2,
            "skipped_count": 0,
            "facts": [
                "domain_omission(letter_1, 'fda_correspondence_party/5', role_missing, signatory_not_stated, src_line_9).",
                "fda_correspondence_party(letter_1, signatory_unknown, signatory, unknown, src_line_9).",
            ],
            "rules": [],
            "queries": [],
        }

    monkeypatch.setattr(domain_bootstrap_file, "_compile_source_pass_ops", fake_compile_source_pass_ops)

    result = _apply_profile_registry_accountability_followup_pass(
        source_compile=source_compile,
        parsed_profile=profile,
        profile_registry=registry,
        source_text="The downloaded source has no signature block.",
        intake_plan={},
        args=type("Args", (), {"focused_pass_operation_target": 8})(),
        extra_context=[],
    )

    assert result["attempted"] is True
    assert result["new_fact_count"] == 1
    assert result["signature_contract"]["rejected_count"] == 1
    assert source_compile["facts"] == [
        "fda_warning_letter(letter_1, cder, acme_inc, v_2026_01_01, src_line_1).",
        "domain_omission(letter_1, 'fda_correspondence_party/5', role_missing, signatory_not_stated, src_line_9).",
    ]


def test_profile_registry_accountability_followup_no_requirements_is_noop() -> None:
    source_compile = {"facts": ["document_title(doc_1, warning_letter)."], "rules": [], "queries": []}

    result = _apply_profile_registry_accountability_followup_pass(
        source_compile=source_compile,
        parsed_profile={},
        profile_registry={"accountability_requirements": []},
        source_text="No source call should run.",
        intake_plan={},
        args=type("Args", (), {"focused_pass_operation_target": 8})(),
        extra_context=[],
    )

    assert result["attempted"] is False
    assert result["reason"] == "no_profile_registry_accountability_requirements"
    assert source_compile["facts"] == ["document_title(doc_1, warning_letter)."]


def test_domain_omission_carrier_signature_reduction_canonicalizes_registered_references() -> None:
    source_compile = {
        "facts": [
            "domain_omission(letter_1, fda_correspondence_party_5, role_missing, signatory_not_stated, src_line_9).",
            "domain_omission(letter_2, 'fda_correspondence_party/5', role_missing, signatory_not_stated, src_line_10).",
            "domain_omission(letter_3, not_a_registered_signature_5, role_missing, signatory_not_stated, src_line_11).",
        ]
    }

    report = _apply_domain_omission_carrier_signature_reduction(source_compile)

    assert report["reduction_count"] == 1
    assert report["invalid_count"] == 1
    assert source_compile["facts"] == [
        "domain_omission(letter_1, 'fda_correspondence_party/5', role_missing, signatory_not_stated, src_line_9).",
        "domain_omission(letter_2, 'fda_correspondence_party/5', role_missing, signatory_not_stated, src_line_10).",
        "domain_omission(letter_3, not_a_registered_signature_5, role_missing, signatory_not_stated, src_line_11).",
    ]
    assert source_compile["deterministic_domain_omission_signature_invalid_count"] == 1
    assert source_compile["deterministic_domain_omission_signature_reduction_policy"]["not_source_interpretation"] is True


def test_fda_warning_letter_subject_convergence_uses_typed_wrapper_date() -> None:
    source_compile = {
        "facts": [
            "fda_warning_letter(letter_2025_05_14_marigold, office_of_pharmaceutical_quality_operations, marigold_sterile_products_inc, v_2025_05_14, src_line_1).",
            "fda_violation(violation_1, fda_warning_letter_2025_05_14, violation_1, quality_unit_failure, src_line_2).",
            "fda_violation_citation(fda_warning_letter_2025_05_14, cfr_21_211_34, consultant_qualification, src_line_3).",
            "fda_response_requirement(fda_warning_letter_2025_05_14, written_response, fifteen_working_days, fda, corrective_actions_and_documentation, src_line_4).",
            "fda_conclusion_scope(doc_fda_warning_letter_20250514, recurrence_prevention, responsibility_to_correct, src_line_5).",
        ]
    }

    report = _apply_fda_warning_letter_subject_convergence(source_compile)

    assert report["reduction_count"] == 4
    assert source_compile["facts"] == [
        "fda_warning_letter(letter_2025_05_14_marigold, office_of_pharmaceutical_quality_operations, marigold_sterile_products_inc, v_2025_05_14, src_line_1).",
        "fda_violation(violation_1, letter_2025_05_14_marigold, violation_1, quality_unit_failure, src_line_2).",
        "fda_violation_citation(letter_2025_05_14_marigold, cfr_21_211_34, consultant_qualification, src_line_3).",
        "fda_response_requirement(letter_2025_05_14_marigold, written_response, fifteen_working_days, fda, corrective_actions_and_documentation, src_line_4).",
        "fda_conclusion_scope(letter_2025_05_14_marigold, recurrence_prevention, responsibility_to_correct, src_line_5).",
    ]
    policy = source_compile["deterministic_fda_warning_letter_subject_convergence_policy"]
    assert policy["not_source_interpretation"] is True
    assert policy["not_query_interpretation"] is True


def test_fda_warning_letter_subject_convergence_ignores_ambiguous_dates() -> None:
    source_compile = {
        "facts": [
            "fda_warning_letter(letter_a, office, firm_a, v_2025_05_14, src_line_1).",
            "fda_warning_letter(letter_b, office, firm_b, v_2025_05_14, src_line_2).",
            "fda_violation(violation_1, fda_warning_letter_2025_05_14, violation_1, quality_unit_failure, src_line_3).",
        ]
    }

    report = _apply_fda_warning_letter_subject_convergence(source_compile)

    assert report["reduction_count"] == 0
    assert source_compile["facts"][2] == (
        "fda_violation(violation_1, fda_warning_letter_2025_05_14, violation_1, quality_unit_failure, src_line_3)."
    )


def test_fda_violation_detail_subject_integrity_drops_letter_level_details() -> None:
    source_compile = {
        "facts": [
            "fda_violation(violation_1, letter_1, violation_1, quality_unit_failure, src_line_1).",
            "fda_violation_detail(violation_1, affected_lot, lot_a_104, product_release_record_review, src_line_2).",
            "fda_violation_detail(letter_1, response_status, written_response_required, corrective_action_evaluation, src_line_3).",
        ]
    }

    report = _apply_fda_violation_detail_subject_integrity(source_compile)

    assert report["dropped_count"] == 1
    assert source_compile["facts"] == [
        "fda_violation(violation_1, letter_1, violation_1, quality_unit_failure, src_line_1).",
        "fda_violation_detail(violation_1, affected_lot, lot_a_104, product_release_record_review, src_line_2).",
    ]
    policy = source_compile["deterministic_fda_violation_detail_subject_integrity_policy"]
    assert policy["not_source_interpretation"] is True
    assert policy["not_query_interpretation"] is True


def test_fda_violation_number_atom_reduction_canonicalizes_numeric_numbers() -> None:
    source_compile = {
        "facts": [
            "fda_violation(violation_1, letter_1, 1, quality_unit_failure, src_line_1).",
            "fda_violation(violation_2, letter_1, violation_2, contamination_control, src_line_2).",
        ]
    }

    report = _apply_fda_violation_number_atom_reduction(source_compile)

    assert report["reduction_count"] == 1
    assert source_compile["facts"] == [
        "fda_violation(violation_1, letter_1, violation_1, quality_unit_failure, src_line_1).",
        "fda_violation(violation_2, letter_1, violation_2, contamination_control, src_line_2).",
    ]
    policy = source_compile["deterministic_fda_violation_number_atom_reduction_policy"]
    assert policy["not_source_interpretation"] is True
    assert policy["not_query_interpretation"] is True


def test_fda_date_atom_reduction_canonicalizes_registered_date_slots() -> None:
    source_compile = {
        "facts": [
            "fda_inspection_event(inspection_1, facility_1, 2025_02_03, 2025_02_07, fda, src_line_4).",
            "fda_form483_response(response_1, inspection_1, 2025_02_21, src_line_5).",
            "fda_regulatory_meeting(meeting_1, firm_1, v_2025_04_03, src_line_6).",
        ]
    }

    report = _apply_fda_date_atom_reduction(source_compile)

    assert report["reduction_count"] == 2
    assert source_compile["facts"] == [
        "fda_inspection_event(inspection_1, facility_1, v_2025_02_03, v_2025_02_07, fda, src_line_4).",
        "fda_form483_response(response_1, inspection_1, v_2025_02_21, src_line_5).",
        "fda_regulatory_meeting(meeting_1, firm_1, v_2025_04_03, src_line_6).",
    ]
    assert source_compile["deterministic_fda_date_atom_reduction_policy"]["not_source_interpretation"] is True


def test_fda_facility_subject_convergence_uses_typed_facility_identity() -> None:
    source_compile = {
        "facts": [
            "fda_facility_identity(camden_facility, marigold_sterile_products_inc, camden_new_jersey, fei_3012345678, src_line_1).",
            "fda_inspection_event(inspection_1, marigold_sterile_products_inc, v_2025_02_03, v_2025_02_07, fda, src_line_4).",
        ]
    }

    report = _apply_fda_facility_subject_convergence(source_compile)

    assert report["reduction_count"] == 1
    assert source_compile["facts"] == [
        "fda_facility_identity(camden_facility, marigold_sterile_products_inc, camden_new_jersey, fei_3012345678, src_line_1).",
        "fda_inspection_event(inspection_1, camden_facility, v_2025_02_03, v_2025_02_07, fda, src_line_4).",
    ]
    policy = source_compile["deterministic_fda_facility_subject_convergence_policy"]
    assert policy["not_source_interpretation"] is True
    assert policy["not_query_interpretation"] is True


def test_fda_facility_subject_convergence_ignores_ambiguous_names() -> None:
    source_compile = {
        "facts": [
            "fda_facility_identity(facility_a, same_name, place_a, fei_1, src_line_1).",
            "fda_facility_identity(facility_b, same_name, place_b, fei_2, src_line_2).",
            "fda_inspection_event(inspection_1, same_name, v_2025_02_03, v_2025_02_07, fda, src_line_4).",
        ]
    }

    report = _apply_fda_facility_subject_convergence(source_compile)

    assert report["reduction_count"] == 0
    assert source_compile["facts"][2] == (
        "fda_inspection_event(inspection_1, same_name, v_2025_02_03, v_2025_02_07, fda, src_line_4)."
    )


def test_fda_lot_identifier_atom_reduction_canonicalizes_affected_lot_values() -> None:
    source_compile = {
        "facts": [
            "fda_violation_detail(violation_1, affected_lot, lot_a104, product_release_record_review, src_line_12).",
            "fda_violation_detail(violation_1, affected_lot, batch_a_105, product_release_record_review, src_line_12).",
            "fda_violation_detail(violation_1, affected_lot, a106, product_release_record_review, src_line_12).",
            "fda_violation_detail(violation_2, affected_product, batch_a_106, sterile_drug_products, src_line_13).",
        ]
    }

    report = _apply_fda_lot_identifier_atom_reduction(source_compile)

    assert report["reduction_count"] == 3
    assert source_compile["facts"] == [
        "fda_violation_detail(violation_1, affected_lot, lot_a_104, product_release_record_review, src_line_12).",
        "fda_violation_detail(violation_1, affected_lot, lot_a_105, product_release_record_review, src_line_12).",
        "fda_violation_detail(violation_1, affected_lot, lot_a_106, product_release_record_review, src_line_12).",
        "fda_violation_detail(violation_2, affected_product, batch_a_106, sterile_drug_products, src_line_13).",
    ]
    assert source_compile["deterministic_fda_lot_identifier_atom_reduction_policy"]["not_source_interpretation"] is True


def test_fda_facility_identity_atom_reduction_canonicalizes_location_and_fei() -> None:
    source_compile = {
        "facts": [
            "fda_facility_identity(facility_1, marigold_sterile_products_inc, camden_new_jersey_08102, 3012345678, src_line_4).",
        ]
    }

    report = _apply_fda_facility_identity_atom_reduction(source_compile)

    assert report["reduction_count"] == 1
    assert source_compile["facts"] == [
        "fda_facility_identity(facility_1, marigold_sterile_products_inc, camden_new_jersey, fei_3012345678, src_line_4).",
    ]
    assert source_compile["deterministic_fda_facility_identity_atom_reduction_policy"]["not_source_interpretation"] is True


def test_fda_consultant_citation_scope_reduction_uses_typed_violation_letter() -> None:
    source_compile = {
        "facts": [
            "fda_violation(violation_1, letter_1, violation_1, quality_unit_failure, src_line_8).",
            "fda_violation_citation(violation_1, cfr_21_211_34, consultant_qualification, src_line_20).",
            "fda_violation_citation(violation_1, cfr_21_211_192, cgmps_requirement, src_line_8).",
        ]
    }

    report = _apply_fda_consultant_citation_scope_reduction(source_compile)

    assert report["reduction_count"] == 1
    assert source_compile["facts"] == [
        "fda_violation(violation_1, letter_1, violation_1, quality_unit_failure, src_line_8).",
        "fda_violation_citation(letter_1, cfr_21_211_34, consultant_qualification, src_line_20).",
        "fda_violation_citation(violation_1, cfr_21_211_192, cgmps_requirement, src_line_8).",
    ]
    assert source_compile["deterministic_fda_consultant_citation_scope_reduction_policy"]["not_source_interpretation"] is True


def test_fda_office_atom_reduction_canonicalizes_registered_office_slots() -> None:
    source_compile = {
        "facts": [
            "fda_warning_letter(letter_1, office_pharmaceutical_quality_operations, acme_inc, v_2026_01_01, src_line_1).",
            "fda_correspondence_party(letter_1, office_pharmaceutical_quality_operations, issuing_office, office_pharmaceutical_quality_operations, src_line_1).",
            "fda_facility_identity(facility_1, office_pharmaceutical_quality_operations, camden_new_jersey, fei_1, src_line_2).",
        ]
    }

    report = _apply_fda_office_atom_reduction(source_compile)

    assert report["reduction_count"] == 2
    assert source_compile["facts"] == [
        "fda_warning_letter(letter_1, office_of_pharmaceutical_quality_operations, acme_inc, v_2026_01_01, src_line_1).",
        "fda_correspondence_party(letter_1, office_of_pharmaceutical_quality_operations, issuing_office, office_of_pharmaceutical_quality_operations, src_line_1).",
        "fda_facility_identity(facility_1, office_pharmaceutical_quality_operations, camden_new_jersey, fei_1, src_line_2).",
    ]
    assert source_compile["deterministic_fda_office_atom_reduction_policy"]["not_source_interpretation"] is True


def test_fda_correspondence_party_placeholder_contract_rejects_omission_substitutes() -> None:
    source_compile = {
        "facts": [
            "fda_correspondence_party(letter_1, acme_inc, recipient, acme_inc, src_line_1).",
            "fda_correspondence_party(letter_1, not_stated, signatory, not_stated, src_line_2).",
            "domain_omission(letter_1, 'fda_correspondence_party/5', role_missing, signatory_not_stated, src_line_2).",
        ]
    }

    report = _enforce_fda_correspondence_party_placeholder_contract(source_compile)

    assert report["rejected_count"] == 1
    assert source_compile["facts"] == [
        "fda_correspondence_party(letter_1, acme_inc, recipient, acme_inc, src_line_1).",
        "domain_omission(letter_1, 'fda_correspondence_party/5', role_missing, signatory_not_stated, src_line_2).",
    ]
    assert source_compile["fda_correspondence_party_placeholder_contract_policy"]["not_source_interpretation"] is True


def test_global_first_profile_registry_palette_prior_is_unsafe() -> None:
    reason = _unsafe_profile_registry_palette_prior_reason(
        {
            "schema": "candidate_profile_registry_v1",
            "fixture": "",
            "selection": {"mode": "first", "draw_count": 86},
            "predicates": [{"signature": "source_detail/4"}],
        }
    )

    assert "global first-draw palette" in reason


def test_fixture_scoped_first_profile_registry_palette_prior_is_allowed() -> None:
    reason = _unsafe_profile_registry_palette_prior_reason(
        {
            "schema": "candidate_profile_registry_v1",
            "fixture": "amended_lease_register",
            "selection": {"mode": "first", "draw_count": 3},
            "predicates": [{"signature": "source_detail/4"}],
        }
    )

    assert reason == ""


def test_compile_source_with_plan_passes_reports_health(monkeypatch) -> None:
    def fake_compile(**kwargs):
        pass_id = ""
        for row in kwargs.get("extra_context", []):
            if str(row).startswith("current_intake_pass_id:"):
                pass_id = str(row).split(":", 1)[1].strip()
        if pass_id == "p1":
            return {"ok": True, "facts": ["a(1)."], "rules": [], "queries": [], "admitted_count": 1, "skipped_count": 0}
        return {"ok": True, "facts": ["a(1).", "b(2)."], "rules": [], "queries": [], "admitted_count": 2, "skipped_count": 0}

    monkeypatch.setattr(domain_bootstrap_file, "_compile_source_with_draft_profile", fake_compile)
    args = type(
        "Args",
        (),
        {
            "max_plan_passes": 2,
            "focused_pass_operation_target": 48,
            "focused_pass_ops_schema": False,
            "domain_hint": "test",
        },
    )()

    result = _compile_source_with_plan_passes(
        source_text="source",
        parsed_profile={"candidate_predicates": []},
        intake_plan={
            "pass_plan": [
                {"pass_id": "p1", "purpose": "first", "focus": "one"},
                {"pass_id": "p2", "purpose": "second", "focus": "two"},
            ]
        },
        args=args,
    )

    assert result["ok"] is True
    assert result["facts"] == ["a(1).", "b(2)."]
    assert result["surface_contribution"][0]["unique_contribution_count"] == 1
    assert result["surface_contribution"][1]["duplicate_count"] == 1
    assert result["compile_health"]["verdict"] in {"healthy", "warning"}


def test_lmstudio_json_schema_retries_empty_content(monkeypatch) -> None:
    calls = {"count": 0}

    class FakeResponse:
        def __init__(self, payload: dict):
            self.payload = payload

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self) -> bytes:
            return json.dumps(self.payload).encode("utf-8")

    def fake_urlopen(request, timeout):
        calls["count"] += 1
        if calls["count"] == 1:
            return FakeResponse({"choices": [{"message": {"content": ""}}]})
        return FakeResponse({"choices": [{"message": {"content": '{"ok": true}'}}]})

    monkeypatch.setattr(domain_bootstrap_file.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(domain_bootstrap_file.time, "sleep", lambda seconds: None)

    result = _call_lmstudio_json_schema(
        base_url="http://localhost:1234/v1",
        model="model",
        messages=[{"role": "user", "content": "hello"}],
        schema={"type": "object"},
        schema_name="test_schema",
        timeout=5,
        temperature=0,
        top_p=1,
        max_tokens=100,
    )

    assert result["content"] == '{"ok": true}'
    assert result["attempts"] == 2
    assert result["empty_response_retries"] == 1


def test_lmstudio_json_schema_adds_openrouter_provider_routing(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self) -> bytes:
            return b'{"choices":[{"message":{"content":"{\\"ok\\":true}"}}]}'

    def fake_urlopen(request, timeout):
        captured["payload"] = json.loads(request.data.decode("utf-8"))
        captured["headers"] = dict(request.headers)
        return FakeResponse()

    monkeypatch.setenv("PRETHINKER_OPENROUTER_PROVIDER_ORDER", "provider-a")
    monkeypatch.setenv("PRETHINKER_OPENROUTER_ALLOW_FALLBACKS", "false")
    monkeypatch.setenv("PRETHINKER_OPENROUTER_REQUIRE_PARAMETERS", "true")
    monkeypatch.setattr(domain_bootstrap_file.urllib.request, "urlopen", fake_urlopen)

    result = _call_lmstudio_json_schema(
        base_url="https://openrouter.ai/api/v1",
        model="model",
        messages=[{"role": "user", "content": "hello"}],
        schema={"type": "object"},
        schema_name="test_schema",
        timeout=5,
        temperature=0,
        top_p=1,
        max_tokens=100,
    )

    assert result["content"] == '{"ok":true}'
    assert captured["payload"]["provider"] == {
        "allow_fallbacks": False,
        "order": ["provider-a"],
        "require_parameters": True,
    }
    assert captured["headers"]["X-openrouter-experimental-metadata"] == "enabled"


def test_lmstudio_json_schema_portable_openrouter_payload_omits_nonportable_thinking_fields(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self) -> bytes:
            return b'{"choices":[{"message":{"content":"{\\"ok\\":true}"}}]}'

    def fake_urlopen(request, timeout):
        captured["payload"] = json.loads(request.data.decode("utf-8"))
        return FakeResponse()

    monkeypatch.setenv("PRETHINKER_OPENROUTER_PORTABLE_PAYLOAD", "true")
    monkeypatch.setenv("PRETHINKER_OPENROUTER_PROVIDER_ONLY", "provider-a")
    monkeypatch.setenv("PRETHINKER_OPENROUTER_REQUIRE_PARAMETERS", "true")
    monkeypatch.setattr(domain_bootstrap_file.urllib.request, "urlopen", fake_urlopen)

    result = _call_lmstudio_json_schema(
        base_url="https://openrouter.ai/api/v1",
        model="model",
        messages=[{"role": "user", "content": "hello"}],
        schema={"type": "object"},
        schema_name="test_schema",
        timeout=5,
        temperature=0,
        top_p=1,
        max_tokens=100,
        reasoning_effort="none",
    )

    payload = captured["payload"]
    assert result["content"] == '{"ok":true}'
    assert "think" not in payload
    assert "thinking" not in payload
    assert "reasoning" not in payload
    assert "include_reasoning" not in payload
    assert "reasoning_effort" not in payload
    assert payload["provider"] == {
        "only": ["provider-a"],
        "require_parameters": True,
    }


def test_lmstudio_chat_url_accepts_root_or_v1_base_url() -> None:
    assert _lmstudio_chat_completions_url("http://127.0.0.1:1234") == "http://127.0.0.1:1234/v1/chat/completions"
    assert _lmstudio_chat_completions_url("http://127.0.0.1:1234/v1") == "http://127.0.0.1:1234/v1/chat/completions"
