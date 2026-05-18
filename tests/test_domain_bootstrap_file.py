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
    _ensure_quantity_event_predicate,
    _ensure_repeated_structure_predicates,
    _ensure_source_authority_predicate,
    _ensure_source_detail_predicate,
    _profile_admission_report,
    _profile_admission_retry_context,
    _attach_profile_admission_report,
    _flat_plus_surface_contribution,
    _profile_bootstrap_admission_context,
    _default_openrouter_title,
    _invalid_profile_retry_context,
    _lmstudio_chat_completions_url,
    _pass_surface_contribution,
    _profile_from_signature_roster,
    _profile_registry_palette_report,
    _profile_registry_palette_prior_context,
    _should_build_source_entity_ledger,
    _source_compiler_context,
    _source_entity_ledger_context,
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
