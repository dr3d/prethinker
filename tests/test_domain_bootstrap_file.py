from scripts.run_domain_bootstrap_file import (
    COMPETITION_ROLE_ALIAS_CONTEXT_V1,
    COMPILE_SURFACE_INVARIANT_CONTEXT_V1,
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
    _ensure_entity_location_predicate,
    _ensure_event_date_predicate,
    _ensure_quantity_event_predicate,
    _ensure_quorum_status_predicate,
    _ensure_repeated_structure_predicates,
    _ensure_scheduled_event_predicate,
    _ensure_source_attributed_claim_predicate,
    _ensure_source_authority_predicate,
    _ensure_source_detail_predicate,
    _ensure_status_state_predicate,
    _ensure_vote_tally_predicate,
    _profile_admission_report,
    _profile_admission_retry_context,
    _attach_profile_admission_report,
    _flat_plus_surface_contribution,
    _profile_bootstrap_admission_context,
    _chat_headers,
    _default_openrouter_title,
    _invalid_profile_retry_context,
    _lmstudio_chat_completions_url,
    _pass_surface_contribution,
    _profile_from_signature_roster,
    _profile_registry_palette_report,
    _profile_registry_palette_prior_context,
    _unsafe_profile_registry_palette_prior_reason,
    _should_build_source_entity_ledger,
    _source_compiler_context,
    _source_entity_ledger_context,
    _source_pass_profile_delivery_target_context,
    _source_pass_ops_to_semantic_ir,
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


def test_compile_surface_invariants_keep_operational_record_slots() -> None:
    context = "\n".join(COMPILE_SURFACE_INVARIANT_CONTEXT_V1)

    assert "chronological/event-list sources need complete event backbone units" in context
    assert "Compile surface preservation rule" in context
    assert "must not replace already-needed concrete typed rows" in context
    assert "dropping typed backbone predicate families is not acceptable" in context
    assert "event id or entry label, date/time/order, actor/party/system" in context
    assert "vague event wrapper" in context
    assert "financial or numeric-state calculations need baseline preservation" in context
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
                {"signature": "event_date/2", "args": ["event_id", "date"]},
                {"signature": "event_time/2", "args": ["event_id", "time"]},
            ]
        },
    )

    joined = "\n".join(lines)
    assert "explicit event/hearing/filing dates or clock times" in joined
    assert "event_date/2" in joined
    assert "event_time/2" in joined
    assert "not a substitute for a joinable temporal row" in joined


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


def test_lmstudio_chat_url_accepts_root_or_v1_base_url() -> None:
    assert _lmstudio_chat_completions_url("http://127.0.0.1:1234") == "http://127.0.0.1:1234/v1/chat/completions"
    assert _lmstudio_chat_completions_url("http://127.0.0.1:1234/v1") == "http://127.0.0.1:1234/v1/chat/completions"
