from __future__ import annotations

from scripts.run_semantic_router_agility import (
    _admitted_predicates_from_clauses,
    _anti_coupling_diagnostics,
    _compiler_context_from_router,
    _evaluate_router,
    _known_profile_or_general,
    _profile_predicate_index,
    _router_diagnostics,
    _router_case_from_lava,
    _router_requests_bootstrap,
)
from scripts.run_semantic_ir_lava_sweep import LavaCase
from scripts.run_multilingual_semantic_ir_probe import MULTILINGUAL_CASES
from src.domain_profiles import load_domain_profile_catalog, thin_profile_roster
from src.semantic_router import (
    GUIDANCE_MODULES,
    ROUTER_SCHEMA_CONTRACT,
    build_semantic_router_input_payload,
    build_semantic_router_messages,
    parse_semantic_router_json,
)


def test_semantic_router_payload_exposes_roster_and_modules():
    catalog = load_domain_profile_catalog()
    roster = thin_profile_roster(catalog)
    payload = build_semantic_router_input_payload(
        utterance="Priya's creatinine came back high.",
        context=["Known patient: Priya."],
        available_domain_profiles=roster,
    )

    assert payload["utterance"] == "Priya's creatinine came back high."
    assert payload["available_domain_profiles"]
    profiles = {row["profile_id"]: row for row in payload["available_domain_profiles"]}
    assert "medical@v0" in profiles
    assert profiles["medical@v0"]["context_available"] is True
    assert profiles["logistics@v0"]["context_available"] is False
    assert payload["available_guidance_modules"] == GUIDANCE_MODULES
    assert payload["required_top_level_json_shape"] == ROUTER_SCHEMA_CONTRACT
    assert "context_audit" in payload["required_top_level_json_shape"]
    policy = "\n".join(payload["routing_policy"])
    assert "Do not invent recent context" in policy
    assert "Routing policy text is not evidence" in policy
    assert "story-world scene memory" in policy
    assert "new, ad hoc, specialized" in policy
    assert "waived notice" in policy
    assert "Fill context_audit" in policy


def test_semantic_router_messages_use_dedicated_router_system_prompt():
    messages = build_semantic_router_messages(
        utterance="In Doe v. Acme, the complaint alleged breach.",
        context=[],
        available_domain_profiles=[],
    )

    assert messages[0]["role"] == "system"
    assert "semantic_router_v1" in messages[0]["content"]
    assert "semantic_ir_v1" in messages[1]["content"]


def test_parse_semantic_router_json_accepts_router_shape():
    parsed = parse_semantic_router_json(
        """
        {
          "schema_version": "semantic_router_v1",
          "selected_profile_id": "legal_courtlistener@v0",
          "candidate_profile_ids": ["legal_courtlistener@v0"],
          "routing_confidence": 0.91,
          "turn_shape": "state_update",
          "should_segment": false,
          "segments": [],
          "guidance_modules": ["claim_vs_fact"],
          "retrieval_hints": {"entity_terms": ["acme"], "predicate_terms": [], "context_needs": []},
          "risk_flags": ["claim_not_finding"],
          "context_audit": {
            "why_this_profile": "legal source language",
            "selected_context_sources": ["legal_courtlistener@v0"],
            "secondary_profiles_considered": [],
            "why_not_secondary": []
          },
          "bootstrap_request": {"needed": false, "proposed_domain_name": "", "why": "", "candidate_predicate_concepts": []},
          "notes": []
        }
        """
    )

    assert parsed
    assert parsed["selected_profile_id"] == "legal_courtlistener@v0"


def test_router_profile_validation_rejects_future_or_unknown_profiles():
    catalog = load_domain_profile_catalog()

    assert _known_profile_or_general("medical@v0", catalog) == "medical@v0"
    assert _known_profile_or_general("logistics@v0", catalog) == "general"
    assert _known_profile_or_general("totally_new@v0", catalog) == "general"
    assert _known_profile_or_general("bootstrap", catalog) == "general"


def test_router_context_summary_is_structural_context_not_authority():
    context = _compiler_context_from_router(
        {
            "selected_profile_id": "sec_contracts@v0",
            "candidate_profile_ids": ["sec_contracts@v0"],
            "turn_shape": "rule_update",
            "should_segment": False,
            "guidance_modules": ["contract_obligation_semantics"],
            "retrieval_hints": {"entity_terms": ["borrower"], "predicate_terms": ["obligation"], "context_needs": []},
            "risk_flags": ["rule_not_fact"],
            "bootstrap_request": {"needed": False},
            "segments": [],
        },
        ["Known contract: loan_1."],
    )

    assert context[0] == "Known contract: loan_1."
    assert context[1].startswith("semantic_router_v1 authority:")
    assert context[2].startswith("semantic_router_v1 decision:")
    assert "sec_contracts@v0" in context[2]
    assert "context_audit" in context[2]


def test_router_eval_distinguishes_near_miss_from_strict_match():
    catalog = load_domain_profile_catalog()
    strict = _evaluate_router(
        {
            "selected_profile_id": "medical@v0",
            "candidate_profile_ids": ["medical@v0"],
            "routing_confidence": 0.95,
            "bootstrap_request": {"needed": False},
        },
        expected_profile="medical@v0",
        effective_profile="medical@v0",
        catalog=catalog,
    )
    near = _evaluate_router(
        {
            "selected_profile_id": "probate@v0",
            "candidate_profile_ids": ["probate@v0", "legal_courtlistener@v0"],
            "routing_confidence": 0.82,
            "bootstrap_request": {"needed": False},
        },
        expected_profile="legal_courtlistener@v0",
        effective_profile="probate@v0",
        catalog=catalog,
    )

    assert strict["strict_ok"] is True
    assert strict["score"] == 1.0
    assert near["strict_ok"] is False
    assert near["semantic_near_miss"] is True
    assert near["score"] == 0.75


def test_router_eval_scores_bootstrap_against_selected_or_request():
    catalog = load_domain_profile_catalog()

    selected = _evaluate_router(
        {
            "selected_profile_id": "bootstrap",
            "candidate_profile_ids": ["sec_contracts@v0"],
            "routing_confidence": 0.9,
            "bootstrap_request": {"needed": True},
        },
        expected_profile="bootstrap",
        effective_profile="general",
        catalog=catalog,
    )
    missed = _evaluate_router(
        {
            "selected_profile_id": "general",
            "candidate_profile_ids": ["medical@v0"],
            "routing_confidence": 0.9,
            "bootstrap_request": {"needed": False},
        },
        expected_profile="bootstrap",
        effective_profile="general",
        catalog=catalog,
    )

    assert selected["strict_ok"] is True
    assert missed["strict_ok"] is False


def test_multilingual_probe_covers_profiles_without_python_translation_layer():
    profiles = {str(row["expected_profile"]) for row in MULTILINGUAL_CASES}
    languages = {str(row["language"]) for row in MULTILINGUAL_CASES}

    assert {"medical@v0", "legal_courtlistener@v0", "sec_contracts@v0", "story_world@v0", "probate@v0"} <= profiles
    assert {"es", "fr", "de", "pt", "ja", "it", "mixed"} <= languages
    assert all("utterance" in row and row["utterance"] for row in MULTILINGUAL_CASES)


def test_router_agility_can_project_lava_case_shape():
    case = LavaCase(
        id="lava2_probe",
        source="frontier:semantic_ir_lava_pack_v2",
        utterance="Priya toma warfarina.",
        context=("Known patient: Priya.",),
        expected_profile="medical@v0",
    )

    row = _router_case_from_lava(case)

    assert row["id"] == "lava2_probe"
    assert row["source"] == "frontier:semantic_ir_lava_pack_v2"
    assert row["expected_profile"] == "medical@v0"
    assert row["context"] == ["Known patient: Priya."]


def test_anti_coupling_flags_semantic_near_miss_with_admissions():
    catalog = load_domain_profile_catalog()
    router = {
        "selected_profile_id": "story_world@v0",
        "candidate_profile_ids": ["story_world@v0", "sec_contracts@v0"],
        "routing_confidence": 0.92,
    }
    router_eval = _evaluate_router(
        router,
        expected_profile="sec_contracts@v0",
        effective_profile="story_world@v0",
        catalog=catalog,
    )

    diagnostics = _anti_coupling_diagnostics(
        router=router,
        router_eval=router_eval,
        effective_profile="story_world@v0",
        expected_profile="sec_contracts@v0",
        diagnostics={
            "projected_decision": "commit",
            "operation_count": 1,
            "admitted_count": 1,
            "skipped_count": 0,
            "warning_counts": {"skipped check_validity/3 outside allowed predicate palette": 1},
            "clauses": {"facts": ["obligation(acme, deliver_report, contract_7)."]},
            "operations": [
                {"admitted": True, "predicate": "obligation", "effect": "fact"},
            ],
        },
        predicate_index=_profile_predicate_index(catalog),
    )

    kinds = {row["kind"] for row in diagnostics["flags"]}
    assert "semantic_near_miss_with_admissions" in kinds
    assert "admitted_predicates_fit_other_profile_better" in kinds


def test_anti_coupling_flags_mapper_profile_context_skips():
    diagnostics = _anti_coupling_diagnostics(
        router={
            "selected_profile_id": "general",
            "candidate_profile_ids": ["legal_courtlistener@v0"],
            "routing_confidence": 0.61,
        },
        router_eval={"low_confidence": True, "semantic_near_miss": False, "unavailable_near_miss": False},
        effective_profile="general",
        expected_profile="legal_courtlistener@v0",
        diagnostics={
            "projected_decision": "mixed",
            "operation_count": 4,
            "admitted_count": 1,
            "skipped_count": 3,
            "warning_counts": {"skipped check_validity/3 outside allowed predicate palette": 1},
            "clauses": {"facts": ["claim_made(witness, priya, took_warfarin, deposition)."]},
            "operations": [
                {
                    "admitted": False,
                    "predicate": "finding",
                    "skip_reason": "predicate_not_in_allowed_palette",
                },
                {
                    "admitted": False,
                    "predicate": "docket_entry",
                    "skip_reason": "predicate_not_in_allowed_palette",
                },
                {
                    "admitted": False,
                    "predicate": "holding",
                    "skip_reason": "predicate_contract_role_mismatch",
                },
            ],
        },
        predicate_index={},
    )

    kinds = {row["kind"] for row in diagnostics["flags"]}
    assert "low_confidence_router_with_admissions" in kinds
    assert "general_effective_profile_with_domain_candidates" in kinds
    assert "mapper_skips_tied_to_profile_context" in kinds
    assert "high_mapper_skip_ratio" in kinds


def test_anti_coupling_does_not_treat_bootstrap_fallback_as_profile_miss():
    diagnostics = _anti_coupling_diagnostics(
        router={
            "selected_profile_id": "bootstrap",
            "candidate_profile_ids": ["bootstrap", "story_world@v0"],
            "routing_confidence": 0.74,
            "bootstrap_request": {"needed": True, "reason": "ad hoc game rules need a new palette"},
        },
        router_eval={
            "strict_ok": True,
            "low_confidence": False,
            "semantic_near_miss": False,
            "unavailable_near_miss": False,
            "bootstrap_requested": True,
        },
        effective_profile="general",
        expected_profile="bootstrap",
        diagnostics={
            "projected_decision": "mixed",
            "operation_count": 2,
            "admitted_count": 2,
            "skipped_count": 0,
            "warning_counts": {},
            "clauses": {"facts": ["has_token(train_7, coal_token)."], "queries": ["can_cross(train_7, red_bridge)."]},
            "operations": [
                {"admitted": True, "predicate": "has_token", "effect": "fact"},
                {"admitted": True, "predicate": "can_cross", "effect": "query"},
            ],
        },
        predicate_index={},
    )

    kinds = {row["kind"] for row in diagnostics["flags"]}
    assert "strict_profile_miss_with_admissions" not in kinds
    assert "general_effective_profile_with_domain_candidates" not in kinds


def test_anti_coupling_marks_bootstrap_skips_as_review_only_not_profile_failure():
    diagnostics = _anti_coupling_diagnostics(
        router={
            "selected_profile_id": "bootstrap",
            "candidate_profile_ids": ["bootstrap", "sec_contracts@v0"],
            "routing_confidence": 0.77,
            "bootstrap_request": {"needed": True, "reason": "new lab protocol vocabulary"},
        },
        router_eval={
            "strict_ok": True,
            "low_confidence": False,
            "semantic_near_miss": False,
            "unavailable_near_miss": False,
            "bootstrap_requested": True,
        },
        effective_profile="general",
        expected_profile="bootstrap",
        diagnostics={
            "projected_decision": "mixed",
            "operation_count": 2,
            "admitted_count": 0,
            "skipped_count": 2,
            "warning_counts": {"skipped check_validity/3 outside allowed predicate palette": 1},
            "clauses": {"facts": [], "queries": []},
            "operations": [
                {
                    "admitted": False,
                    "predicate": "blank_clarity",
                    "skip_reason": "predicate_not_in_allowed_palette",
                },
                {
                    "admitted": False,
                    "predicate": "check_validity",
                    "skip_reason": "predicate_not_in_allowed_palette",
                },
            ],
        },
        predicate_index={},
    )

    kinds = {row["kind"] for row in diagnostics["flags"]}
    assert "bootstrap_review_only_skips" in kinds
    assert "mapper_skips_tied_to_profile_context" not in kinds
    assert "out_of_palette_warning" not in kinds


def test_router_requests_bootstrap_from_selected_profile_or_request_flag():
    assert _router_requests_bootstrap({"selected_profile_id": "bootstrap", "bootstrap_request": {"needed": False}})
    assert _router_requests_bootstrap({"selected_profile_id": "general", "bootstrap_request": {"needed": True}})
    assert not _router_requests_bootstrap({"selected_profile_id": "general", "bootstrap_request": {"needed": False}})


def test_router_diagnostics_flags_compiler_profile_drift_without_reading_utterance():
    catalog = load_domain_profile_catalog()
    diagnostics = _router_diagnostics(
        router={
            "selected_profile_id": "medical@v0",
            "candidate_profile_ids": ["medical@v0", "legal_courtlistener@v0"],
        },
        effective_profile="medical@v0",
        diagnostics={
            "clauses": {"facts": ["claim_made(complaint, acme, breach, source)."]},
            "operations": [{"predicate": "claim_made", "admitted": True, "effect": "fact"}],
        },
        predicate_index=_profile_predicate_index(catalog),
    )

    kinds = {row["kind"] for row in diagnostics["flags"]}
    assert "compiler_emitted_predicates_outside_selected_profile" in kinds
    assert "compiler_predicates_fit_secondary_profile_better" in kinds


def test_admitted_predicates_from_clauses_includes_rule_predicates():
    predicates = _admitted_predicates_from_clauses(
        {
            "facts": ["approved_by(r17, maya)."],
            "queries": ["conflicted_approver(Who, Requester)."],
            "rules": ["conflicted_approver(A, R) :- approved_by(X, A), requested_by(X, R), A = R."],
        }
    )

    assert {"approved_by", "requested_by", "conflicted_approver"} <= predicates
