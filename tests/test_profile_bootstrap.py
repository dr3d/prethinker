import json
import tempfile
import unittest
from pathlib import Path

from scripts.run_profile_bootstrap import _load_jsonl
from src.profile_bootstrap import (
    PROFILE_BOOTSTRAP_JSON_SCHEMA,
    PROFILE_BOOTSTRAP_GUIDANCE,
    PROFILE_BOOTSTRAP_REVIEW_JSON_SCHEMA,
    PROFILE_BOOTSTRAP_REVIEW_GUIDANCE,
    build_profile_bootstrap_messages,
    build_profile_bootstrap_review_messages,
    parse_profile_bootstrap_json,
    parse_profile_bootstrap_review_json,
    profile_bootstrap_allowed_predicates,
    profile_bootstrap_domain_context,
    profile_bootstrap_frontier_cases,
    profile_bootstrap_predicate_contracts,
    profile_bootstrap_score,
)


class ProfileBootstrapTests(unittest.TestCase):
    def test_build_messages_include_samples_and_boundary(self) -> None:
        messages = build_profile_bootstrap_messages(
            domain_hint="contracts_compliance",
            samples=[
                {
                    "id": "s1",
                    "text": "The borrower shall deliver audited statements within 90 days.",
                    "context": ["Obligation language is not completion evidence."],
                }
            ],
        )

        self.assertEqual(messages[0]["role"], "system")
        self.assertIn("profile_bootstrap_v1", messages[0]["content"])
        self.assertIn("INPUT_JSON", messages[1]["content"])
        self.assertIn("contracts_compliance", messages[1]["content"])
        self.assertIn("required_top_level_json_shape", messages[1]["content"])
        self.assertIn("not authorizing KB writes", messages[0]["content"])

    def test_bootstrap_guidance_preserves_source_records_reporters_and_conditions(self) -> None:
        self.assertIn("source-record predicate", PROFILE_BOOTSTRAP_GUIDANCE)
        self.assertIn("reporting/source actor", PROFILE_BOOTSTRAP_GUIDANCE)
        self.assertIn("epistemic-status/provenance predicate", PROFILE_BOOTSTRAP_GUIDANCE)
        self.assertIn("avoid unary relation-like forms", PROFILE_BOOTSTRAP_GUIDANCE)
        self.assertIn("declaration, proclamation, manifesto", PROFILE_BOOTSTRAP_GUIDANCE)
        self.assertIn("source metadata predicates", PROFILE_BOOTSTRAP_GUIDANCE)
        self.assertIn("research-misconduct", PROFILE_BOOTSTRAP_GUIDANCE)
        self.assertIn("proceeding_event/4", PROFILE_BOOTSTRAP_GUIDANCE)
        self.assertIn("source-record loss", PROFILE_BOOTSTRAP_REVIEW_GUIDANCE)
        self.assertIn("reporter loss", PROFILE_BOOTSTRAP_REVIEW_GUIDANCE)
        self.assertIn("conditional-rule loss", PROFILE_BOOTSTRAP_REVIEW_GUIDANCE)
        self.assertIn("candidate_predicates[].args must be short schema role labels only", PROFILE_BOOTSTRAP_GUIDANCE)
        self.assertIn("entity_type_N counters", PROFILE_BOOTSTRAP_GUIDANCE)
        self.assertIn("Explicit negative surfaces need their own queryable predicate", PROFILE_BOOTSTRAP_GUIDANCE)
        self.assertIn("Do not rely on a positive predicate", PROFILE_BOOTSTRAP_GUIDANCE)
        self.assertIn("printed relative intervals are first-class query surfaces", PROFILE_BOOTSTRAP_GUIDANCE)
        self.assertIn("not only a boolean before/after predicate", PROFILE_BOOTSTRAP_GUIDANCE)
        self.assertIn("Flag negative-surface loss", PROFILE_BOOTSTRAP_REVIEW_GUIDANCE)
        self.assertIn("Flag temporal-distance loss", PROFILE_BOOTSTRAP_REVIEW_GUIDANCE)
        self.assertIn("source-coordinate provenance", PROFILE_BOOTSTRAP_GUIDANCE)
        self.assertIn("semantic assertion and the source coordinate", PROFILE_BOOTSTRAP_GUIDANCE)
        self.assertIn("Avoid requiring an invented claim id", PROFILE_BOOTSTRAP_GUIDANCE)
        self.assertIn("Flag source-coordinate provenance loss", PROFILE_BOOTSTRAP_REVIEW_GUIDANCE)
        self.assertIn("governed semantic subject/assertion and the source coordinate", PROFILE_BOOTSTRAP_REVIEW_GUIDANCE)
        self.assertIn("source-stated values", PROFILE_BOOTSTRAP_REVIEW_GUIDANCE)
        self.assertIn("named-scope contributions", PROFILE_BOOTSTRAP_GUIDANCE)
        self.assertIn("profile_bootstrap_v1 supports at most five argument", PROFILE_BOOTSTRAP_GUIDANCE)
        self.assertIn("Do not use /6 or higher", PROFILE_BOOTSTRAP_GUIDANCE)
        self.assertIn("Flag financial contribution loss", PROFILE_BOOTSTRAP_REVIEW_GUIDANCE)
        self.assertIn("separate provenance/source-coordinate carrier", PROFILE_BOOTSTRAP_REVIEW_GUIDANCE)
        self.assertIn("Do not list global lookup predicates", PROFILE_BOOTSTRAP_GUIDANCE)
        self.assertIn("record-keyed link predicate", PROFILE_BOOTSTRAP_GUIDANCE)
        self.assertIn("recipient/addressee body when stated", PROFILE_BOOTSTRAP_GUIDANCE)
        self.assertIn("captioned duty names and inline", PROFILE_BOOTSTRAP_GUIDANCE)
        self.assertIn("one-time fixed deadlines and recurring", PROFILE_BOOTSTRAP_GUIDANCE)
        self.assertIn("later notice, correction, amendment, update, extension", PROFILE_BOOTSTRAP_GUIDANCE)
        self.assertIn("direct document-update surface", PROFILE_BOOTSTRAP_GUIDANCE)
        self.assertIn("current decision's disposition separately from procedural history", PROFILE_BOOTSTRAP_GUIDANCE)
        self.assertIn("whether the matter is remanded/transferred or finally/directly resolved", PROFILE_BOOTSTRAP_GUIDANCE)
        self.assertIn("Flag recommendation-chain slot loss", PROFILE_BOOTSTRAP_REVIEW_GUIDANCE)
        self.assertIn("violation or deficiency categories separate from action type", PROFILE_BOOTSTRAP_GUIDANCE)
        self.assertIn("separate category rows for each stated area", PROFILE_BOOTSTRAP_GUIDANCE)
        self.assertIn("Flag violation-category loss", PROFILE_BOOTSTRAP_REVIEW_GUIDANCE)

    def test_document_intake_registries_are_narrow_and_fact_free(self) -> None:
        fixture_dir = Path("datasets/profile_bootstrap/samples/document_intake")
        for registry_name, required in [
            (
                "declaration_ontology_registry.json",
                {"document/1", "claim_made/3", "grievance/2", "method/2", "declares_status/3"},
            ),
            (
                "proclamation_ontology_registry.json",
                {"document/1", "principle/2", "grievance/2", "ledger_entry/2", "candidate_identity/2"},
            ),
        ]:
            registry = json.loads((fixture_dir / registry_name).read_text(encoding="utf-8"))
            self.assertEqual(registry["schema"], "candidate_profile_registry_v1")
            self.assertIn("vocabulary only", registry["source"])
            signatures = {item["signature"] for item in registry["predicates"]}
            self.assertGreaterEqual(len(signatures), 40)
            self.assertLessEqual(len(signatures), 130)
            self.assertTrue(required.issubset(signatures))
            self.assertFalse(any("fact" in item for item in registry["predicates"]))

    def test_profile_bootstrap_schema_is_strict_root_object(self) -> None:
        self.assertEqual(PROFILE_BOOTSTRAP_JSON_SCHEMA["type"], "object")
        self.assertFalse(PROFILE_BOOTSTRAP_JSON_SCHEMA["additionalProperties"])
        self.assertIn("candidate_predicates", PROFILE_BOOTSTRAP_JSON_SCHEMA["required"])
        self.assertIn("repeated_structures", PROFILE_BOOTSTRAP_JSON_SCHEMA["required"])
        candidate_schema = PROFILE_BOOTSTRAP_JSON_SCHEMA["properties"]["candidate_predicates"]["items"]
        self.assertFalse(candidate_schema["additionalProperties"])
        self.assertIn("admission_notes", candidate_schema["required"])
        repeated_schema = PROFILE_BOOTSTRAP_JSON_SCHEMA["properties"]["repeated_structures"]["items"]
        self.assertFalse(repeated_schema["additionalProperties"])
        self.assertIn("property_predicates", repeated_schema["required"])

    def test_profile_review_schema_and_messages_are_control_plane_only(self) -> None:
        self.assertEqual(PROFILE_BOOTSTRAP_REVIEW_JSON_SCHEMA["type"], "object")
        self.assertFalse(PROFILE_BOOTSTRAP_REVIEW_JSON_SCHEMA["additionalProperties"])
        self.assertIn("missing_capabilities", PROFILE_BOOTSTRAP_REVIEW_JSON_SCHEMA["required"])
        missing_schema = PROFILE_BOOTSTRAP_REVIEW_JSON_SCHEMA["properties"]["missing_capabilities"]["items"]
        self.assertFalse(missing_schema["additionalProperties"])

        messages = build_profile_bootstrap_review_messages(
            source_text="The infirmary ledger recorded blue sneezing.",
            source_name="proclamation.md",
            domain_hint="source_fidelity",
            intake_plan={"schema_version": "intake_plan_v1"},
            proposed_profile={"schema_version": "profile_bootstrap_v1", "candidate_predicates": []},
        )

        self.assertEqual(messages[0]["role"], "system")
        self.assertIn("review a proposed", messages[0]["content"].casefold())
        self.assertIn("INPUT_JSON", messages[1]["content"])
        self.assertIn("raw_source_text", messages[1]["content"])
        self.assertIn("proposed_profile_bootstrap_v1", messages[1]["content"])
        self.assertIn("never authorizes writes", messages[1]["content"])

    def test_parse_profile_review_json(self) -> None:
        parsed, error = parse_profile_bootstrap_review_json(
            json.dumps(
                {
                    "schema_version": "profile_bootstrap_review_v1",
                    "verdict": "retry_recommended",
                    "coverage_ok": False,
                    "confidence": 0.86,
                    "missing_capabilities": [
                        {
                            "capability": "ledger records",
                            "why_it_matters": "Later questions ask which ledger recorded which observation.",
                            "suggested_signatures": ["ledger_entry/2"],
                        }
                    ],
                    "risky_predicates": [],
                    "retry_guidance": ["Add a source-record predicate family."],
                    "self_check": {"review_authority": "proposal_only", "notes": ["control-plane only"]},
                }
            )
        )

        self.assertEqual(error, "")
        self.assertIsNotNone(parsed)
        self.assertFalse(parsed["coverage_ok"])

    def test_parse_and_score_profile_bootstrap(self) -> None:
        parsed, error = parse_profile_bootstrap_json(
            json.dumps(
                {
                    "schema_version": "profile_bootstrap_v1",
                    "domain_guess": "contracts_compliance",
                    "domain_scope": "Contract and compliance policy intake.",
                    "confidence": 0.9,
                    "source_summary": ["The samples contain obligations and exception policies."],
                    "entity_types": [
                        {"name": "party", "description": "Contract or policy actor.", "examples": ["borrower"]},
                        {"name": "obligation", "description": "Future duty.", "examples": ["deliver_statements"]},
                    ],
                    "candidate_predicates": [
                        {
                            "signature": "obligation/3",
                            "args": ["party", "duty", "source"],
                            "description": "Records a duty stated by a source.",
                            "why": "Shall language appears repeatedly.",
                            "admission_notes": ["Do not treat as completed action."],
                        }
                    ],
                    "likely_functional_predicates": ["current_status/2"],
                    "provenance_sensitive_predicates": ["obligation/3"],
                    "admission_risks": ["Obligation/fact collapse."],
                    "clarification_policy": ["Clarify whether a condition was met."],
                    "unsafe_transformations": ["Do not write delivered(...) from shall deliver."],
                    "starter_frontier_cases": [
                        {
                            "utterance": "Borrower shall deliver reports.",
                            "expected_boundary": "obligation not completed delivery",
                            "must_not_write": ["delivered(borrower, reports)"],
                        }
                    ],
                    "self_check": {"profile_authority": "proposal_only", "notes": ["Review required."]},
                }
            )
        )

        self.assertEqual(error, "")
        score = profile_bootstrap_score(parsed)
        self.assertTrue(score["schema_ok"])
        self.assertEqual(score["predicate_count"], 1)
        self.assertEqual(score["generic_predicate_count"], 0)
        self.assertEqual(score["candidate_signature_arg_mismatch_refs"], [])
        self.assertEqual(score["frontier_unknown_positive_predicate_refs"], [])
        self.assertGreater(score["rough_score"], 0.4)

    def test_parse_normalizes_invalid_argument_role_labels(self) -> None:
        parsed, error = parse_profile_bootstrap_json(
            json.dumps(
                {
                    "schema_version": "profile_bootstrap_v1",
                    "domain_guess": "municipal_budget",
                    "domain_scope": "Budget votes and thresholds.",
                    "confidence": 0.8,
                    "source_summary": ["sample"],
                    "entity_types": [{"name": "vote", "description": "Vote.", "examples": ["v1"]}],
                    "candidate_predicates": [
                        {
                            "signature": "council_vote/6",
                            "args": [
                                "vote_id",
                                "proposal_id",
                                "date",
                                "yes_votes",
                                "votes_for_or_against_or_absent_and_every_possible_value",
                            ],
                            "description": "Vote record.",
                            "why": "Votes matter.",
                            "admission_notes": ["Role labels are not value slots."],
                        }
                    ],
                    "likely_functional_predicates": [],
                    "provenance_sensitive_predicates": [],
                    "admission_risks": [],
                    "clarification_policy": [],
                    "unsafe_transformations": [],
                    "starter_frontier_cases": [],
                    "self_check": {"profile_authority": "proposal_only", "notes": []},
                }
            )
        )

        self.assertEqual(error, "")
        self.assertIsNotNone(parsed)
        self.assertEqual(
            parsed["candidate_predicates"][0]["args"],
            ["vote_id", "proposal_id", "date", "yes_votes", "arg_5"],
        )

    def test_profile_bootstrap_projects_to_draft_semantic_ir_profile(self) -> None:
        parsed = {
            "schema_version": "profile_bootstrap_v1",
            "domain_guess": "contracts_compliance",
            "domain_scope": "Contract and compliance policy intake.",
            "confidence": 0.9,
            "source_summary": ["sample"],
            "entity_types": [{"name": "approval", "description": "Approval.", "examples": ["r1"]}],
            "candidate_predicates": [
                {
                    "signature": "approved_by/2",
                    "args": ["item", "approver"],
                    "description": "Specific approval relation.",
                    "why": "Directly matches the domain relation.",
                    "admission_notes": ["Requires source support."],
                }
            ],
            "likely_functional_predicates": [],
            "provenance_sensitive_predicates": ["approved_by/2"],
            "admission_risks": ["event/fact collapse"],
            "clarification_policy": ["clarify missing actor"],
            "unsafe_transformations": ["do not infer approval"],
            "starter_frontier_cases": [
                {
                    "utterance": "R1 was approved by Ilya.",
                    "expected_boundary": "approved_by(r1, ilya)",
                    "must_not_write": ["event_occurred(approval, r1)"],
                }
            ],
            "self_check": {"profile_authority": "proposal_only", "notes": []},
        }

        self.assertEqual(profile_bootstrap_allowed_predicates(parsed), ["approved_by/2"])
        self.assertEqual(
            profile_bootstrap_predicate_contracts(parsed),
            [
                {
                    "signature": "approved_by/2",
                    "arguments": ["item", "approver"],
                    "notes": (
                        "Specific approval relation. Directly matches the domain relation. "
                        "Requires source support."
                    ),
                }
            ],
        )
        self.assertTrue(any("Contract and compliance" in row for row in profile_bootstrap_domain_context(parsed)))
        self.assertEqual(profile_bootstrap_frontier_cases(parsed)[0]["id"], "bootstrap_case_01")

    def test_profile_projection_deduplicates_predicate_signatures(self) -> None:
        parsed = {
            "candidate_predicates": [
                {
                    "signature": "approved_by/2",
                    "args": ["item", "approver"],
                    "description": "First copy.",
                    "why": "Model may repeat signatures under structured output pressure.",
                    "admission_notes": ["Requires direct support."],
                },
                {
                    "signature": "approved_by/2",
                    "args": ["item", "approver"],
                    "description": "Duplicate copy.",
                    "why": "Should not duplicate downstream allowed palettes.",
                    "admission_notes": ["Duplicate."],
                },
            ]
        }

        self.assertEqual(profile_bootstrap_allowed_predicates(parsed), ["approved_by/2"])
        self.assertEqual(len(profile_bootstrap_predicate_contracts(parsed)), 1)

    def test_score_penalizes_generic_predicate_surface(self) -> None:
        base = {
            "schema_version": "profile_bootstrap_v1",
            "domain_guess": "contracts_compliance",
            "domain_scope": "Contract and compliance policy intake.",
            "confidence": 0.9,
            "source_summary": ["sample"],
            "entity_types": [{"name": "event", "description": "Event.", "examples": ["approval"]}],
            "candidate_predicates": [
                {
                    "signature": "event_occurred/2",
                    "args": ["event_type", "details"],
                    "description": "Generic event wrapper.",
                    "why": "Too broad.",
                    "admission_notes": ["Prefer specific predicates when possible."],
                },
                {
                    "signature": "approved_by/2",
                    "args": ["item", "approver"],
                    "description": "Specific approval relation.",
                    "why": "Directly matches the domain relation.",
                    "admission_notes": ["Requires source support."],
                },
            ],
            "likely_functional_predicates": [],
            "provenance_sensitive_predicates": ["approved_by/2"],
            "admission_risks": ["event/fact collapse"],
            "clarification_policy": ["clarify missing actor"],
            "unsafe_transformations": ["do not infer approval"],
            "starter_frontier_cases": [
                {"utterance": "R1 was approved by Ilya.", "expected_boundary": "approval event", "must_not_write": []}
            ],
            "self_check": {"profile_authority": "proposal_only", "notes": []},
        }

        score = profile_bootstrap_score(base)

        self.assertEqual(score["generic_predicate_count"], 1)
        self.assertLess(score["rough_score"], 0.8)

    def test_score_catches_candidate_signature_arg_role_mismatch(self) -> None:
        parsed = {
            "schema_version": "profile_bootstrap_v1",
            "domain_guess": "operations_record",
            "domain_scope": "Operational source records with repeated actions.",
            "confidence": 0.9,
            "source_summary": ["sample"],
            "entity_types": [{"name": "action", "description": "Action record.", "examples": ["a1"]}],
            "candidate_predicates": [
                {
                    "signature": "record_action/4",
                    "args": ["record_id", "actor", "action"],
                    "description": "Action record with role labels.",
                    "why": "The source records repeated actions.",
                    "admission_notes": ["Keep roles as schema slots."],
                }
            ],
            "repeated_structures": [],
            "likely_functional_predicates": [],
            "provenance_sensitive_predicates": ["record_action/4"],
            "admission_risks": ["action/status collapse"],
            "clarification_policy": ["clarify actor"],
            "unsafe_transformations": ["do not infer completion"],
            "starter_frontier_cases": [
                {
                    "utterance": "A record stated an action.",
                    "expected_boundary": "record_action(r1, actor_a, action_a, src_1).",
                    "must_not_write": [],
                }
            ],
            "self_check": {"profile_authority": "proposal_only", "notes": []},
        }

        score = profile_bootstrap_score(parsed)

        self.assertEqual(score["candidate_signature_arg_mismatch_count"], 1)
        self.assertEqual(score["candidate_signature_arg_mismatch_refs"], ["record_action/4:args=3"])
        self.assertLess(score["rough_score"], 0.8)

    def test_score_surfaces_recommendation_chain_without_recipient_slot(self) -> None:
        parsed = {
            "schema_version": "profile_bootstrap_v1",
            "domain_guess": "regulatory_record",
            "domain_scope": "Regulatory source records with authority referrals.",
            "confidence": 0.9,
            "source_summary": ["sample"],
            "entity_types": [{"name": "action", "description": "Regulatory action.", "examples": ["a1"]}],
            "candidate_predicates": [
                {
                    "signature": "recommended_action/3",
                    "args": ["recommending_body", "target_entity", "action_type"],
                    "description": "Records a recommended action.",
                    "why": "One body recommended action against a target.",
                    "admission_notes": ["Must preserve the full chain."],
                },
                {
                    "signature": "regulatory_action/5",
                    "args": ["action_id", "action_type", "target_entity", "issuing_body", "legal_basis"],
                    "description": "Records the action later taken.",
                    "why": "The issuing body and action are source-stated.",
                    "admission_notes": ["Issuer is not automatically the recommendation recipient."],
                },
            ],
            "repeated_structures": [],
            "likely_functional_predicates": [],
            "provenance_sensitive_predicates": ["recommended_action/3"],
            "admission_risks": ["recommendation/action collapse"],
            "clarification_policy": ["clarify recipient when source omits it"],
            "unsafe_transformations": ["do not infer recipient from issuer"],
            "starter_frontier_cases": [
                {
                    "utterance": "The review body recommended administrative action.",
                    "expected_boundary": "recommended_action(r1, target_a, action_a).",
                    "must_not_write": [],
                }
            ],
            "self_check": {"profile_authority": "proposal_only", "notes": []},
        }

        score = profile_bootstrap_score(parsed)

        self.assertEqual(score["recommendation_chain_slot_loss_count"], 1)
        self.assertEqual(score["recommendation_chain_slot_loss_refs"], ["recommended_action/3"])

    def test_score_accepts_recommendation_chain_with_explicit_recipient_slot(self) -> None:
        parsed = {
            "schema_version": "profile_bootstrap_v1",
            "domain_guess": "regulatory_record",
            "domain_scope": "Regulatory source records with authority referrals.",
            "confidence": 0.9,
            "source_summary": ["sample"],
            "entity_types": [{"name": "action", "description": "Regulatory action.", "examples": ["a1"]}],
            "candidate_predicates": [
                {
                    "signature": "authority_recommendation/5",
                    "args": ["source_body", "recipient_body", "target_entity", "action_type", "source_ref"],
                    "description": "Records a recommendation chain.",
                    "why": "The source states who recommended action to whom.",
                    "admission_notes": ["Recipient remains separately queryable."],
                }
            ],
            "repeated_structures": [],
            "likely_functional_predicates": [],
            "provenance_sensitive_predicates": ["authority_recommendation/5"],
            "admission_risks": ["recommendation/action collapse"],
            "clarification_policy": ["clarify missing recipient"],
            "unsafe_transformations": ["do not infer final action scope"],
            "starter_frontier_cases": [
                {
                    "utterance": "The review body recommended action to the regulator.",
                    "expected_boundary": "authority_recommendation(body_a, regulator_b, target_c, action_d, src_1).",
                    "must_not_write": [],
                }
            ],
            "self_check": {"profile_authority": "proposal_only", "notes": []},
        }

        score = profile_bootstrap_score(parsed)

        self.assertEqual(score["recommendation_chain_slot_loss_count"], 0)
        self.assertEqual(score["recommendation_chain_slot_loss_refs"], [])

    def test_score_does_not_treat_direct_report_request_as_recommendation_chain(self) -> None:
        parsed = {
            "schema_version": "profile_bootstrap_v1",
            "domain_guess": "regulatory_record",
            "domain_scope": "Regulatory source records with direct report requests.",
            "confidence": 0.9,
            "source_summary": ["sample"],
            "entity_types": [{"name": "action", "description": "Regulatory action.", "examples": ["a1"]}],
            "candidate_predicates": [
                {
                    "signature": "requests_report/3",
                    "args": ["regulator", "target_entity", "request_type"],
                    "description": "Captures a direct request for a report.",
                    "why": "The source states a regulator requested a report from the target.",
                    "admission_notes": ["Direct request action, not a recommendation chain."],
                }
            ],
            "repeated_structures": [],
            "likely_functional_predicates": [],
            "provenance_sensitive_predicates": ["requests_report/3"],
            "admission_risks": ["request/action collapse"],
            "clarification_policy": ["clarify target when omitted"],
            "unsafe_transformations": ["do not infer a recommendation"],
            "starter_frontier_cases": [
                {
                    "utterance": "The regulator requested a report from the target.",
                    "expected_boundary": "requests_report(regulator_a, target_b, report_type_c).",
                    "must_not_write": [],
                }
            ],
            "self_check": {"profile_authority": "proposal_only", "notes": []},
        }

        score = profile_bootstrap_score(parsed)

        self.assertEqual(score["recommendation_chain_slot_loss_count"], 0)
        self.assertEqual(score["recommendation_chain_slot_loss_refs"], [])

    def test_score_surfaces_regulatory_violation_without_category_carrier(self) -> None:
        parsed = {
            "schema_version": "profile_bootstrap_v1",
            "domain_guess": "regulatory_enforcement",
            "domain_scope": "Regulatory enforcement records with compliance violations and failures.",
            "confidence": 0.9,
            "source_summary": ["sample"],
            "entity_types": [{"name": "action", "description": "Regulatory action.", "examples": ["a1"]}],
            "candidate_predicates": [
                {
                    "signature": "regulatory_order/4",
                    "args": ["order_id", "target_entity", "order_type", "legal_basis"],
                    "description": "Records an intervention.",
                    "why": "The source states the order.",
                    "admission_notes": ["Order type is not violation type."],
                },
                {
                    "signature": "admitted_failure/2",
                    "args": ["entity", "failure_description"],
                    "description": "Records a failure description.",
                    "why": "The source states failures.",
                    "admission_notes": ["Description alone leaves categories hard to query."],
                },
            ],
            "repeated_structures": [],
            "likely_functional_predicates": [],
            "provenance_sensitive_predicates": ["admitted_failure/2"],
            "admission_risks": ["violation category/action collapse"],
            "clarification_policy": ["clarify category when source omits it"],
            "unsafe_transformations": ["do not infer legal guilt"],
            "starter_frontier_cases": [
                {
                    "utterance": "The record listed violation categories.",
                    "expected_boundary": "admitted_failure(entity_a, failure_a).",
                    "must_not_write": [],
                }
            ],
            "self_check": {"profile_authority": "proposal_only", "notes": []},
        }

        score = profile_bootstrap_score(parsed)

        self.assertGreaterEqual(score["violation_category_slot_loss_count"], 1)
        self.assertIn("admitted_failure/2", score["violation_category_slot_loss_refs"])

    def test_score_accepts_regulatory_violation_category_carrier(self) -> None:
        parsed = {
            "schema_version": "profile_bootstrap_v1",
            "domain_guess": "regulatory_enforcement",
            "domain_scope": "Regulatory enforcement records with compliance violations and deficiencies.",
            "confidence": 0.9,
            "source_summary": ["sample"],
            "entity_types": [{"name": "finding", "description": "Regulatory finding.", "examples": ["f1"]}],
            "candidate_predicates": [
                {
                    "signature": "deficiency_identification/3",
                    "args": ["entity", "business_context", "deficiency_description"],
                    "description": "Records a deficiency with context and detail.",
                    "why": "The source states deficiency categories.",
                    "admission_notes": ["Business context remains queryable."],
                },
                {
                    "signature": "legal_basis/2",
                    "args": ["finding_id", "statute_reference"],
                    "description": "Records cited law.",
                    "why": "The source states statutes.",
                    "admission_notes": ["Legal basis is separate from deficiency category."],
                },
            ],
            "repeated_structures": [],
            "likely_functional_predicates": [],
            "provenance_sensitive_predicates": ["deficiency_identification/3"],
            "admission_risks": ["legal basis/category collapse"],
            "clarification_policy": ["clarify category when source omits it"],
            "unsafe_transformations": ["do not infer legal guilt"],
            "starter_frontier_cases": [
                {
                    "utterance": "The record listed deficiency categories.",
                    "expected_boundary": "deficiency_identification(entity_a, control_area_a, detail_a).",
                    "must_not_write": [],
                }
            ],
            "self_check": {"profile_authority": "proposal_only", "notes": []},
        }

        score = profile_bootstrap_score(parsed)

        self.assertEqual(score["violation_category_slot_loss_count"], 0)
        self.assertEqual(score["violation_category_slot_loss_refs"], [])

    def test_score_catches_frontier_cases_using_unproposed_positive_predicates(self) -> None:
        parsed = {
            "schema_version": "profile_bootstrap_v1",
            "domain_guess": "contracts_compliance",
            "domain_scope": "Contract and compliance policy intake.",
            "confidence": 0.9,
            "source_summary": ["sample"],
            "entity_types": [{"name": "approval", "description": "Approval.", "examples": ["r1"]}],
            "candidate_predicates": [
                {
                    "signature": "approved_by/2",
                    "args": ["item", "approver"],
                    "description": "Specific approval relation.",
                    "why": "Directly matches the domain relation.",
                    "admission_notes": ["Requires source support."],
                }
            ],
            "likely_functional_predicates": [],
            "provenance_sensitive_predicates": ["approved_by/2"],
            "admission_risks": ["event/fact collapse"],
            "clarification_policy": ["clarify missing actor"],
            "unsafe_transformations": ["do not infer approval"],
            "starter_frontier_cases": [
                {
                    "utterance": "R1 was approved by Ilya.",
                    "expected_boundary": "approved_by/2(r1, ilya) AND policy_rule/2(x, y). Do not write event_occurred/2(approval).",
                    "must_not_write": ["event_occurred/2"],
                }
            ],
            "self_check": {"profile_authority": "proposal_only", "notes": []},
        }

        score = profile_bootstrap_score(parsed)

        self.assertEqual(score["frontier_unknown_positive_predicate_count"], 1)
        self.assertEqual(score["frontier_unknown_positive_predicate_refs"], ["policy_rule/2"])

    def test_score_catches_unproposed_positive_predicate_calls_and_arity_drift(self) -> None:
        parsed = {
            "schema_version": "profile_bootstrap_v1",
            "domain_guess": "contracts_compliance",
            "domain_scope": "Contract and compliance policy intake.",
            "confidence": 0.9,
            "source_summary": ["sample"],
            "entity_types": [{"name": "approval", "description": "Approval.", "examples": ["r1"]}],
            "candidate_predicates": [
                {
                    "signature": "approved_by/2",
                    "args": ["item", "approver"],
                    "description": "Specific approval relation.",
                    "why": "Directly matches the domain relation.",
                    "admission_notes": ["Requires source support."],
                }
            ],
            "likely_functional_predicates": [],
            "provenance_sensitive_predicates": ["approved_by/2"],
            "admission_risks": ["event/fact collapse"],
            "clarification_policy": ["clarify missing actor"],
            "unsafe_transformations": ["do not infer approval"],
            "starter_frontier_cases": [
                {
                    "utterance": "R1 was approved by Ilya.",
                    "expected_boundary": (
                        "approved_by(r1, ilya, source=march_report); "
                        "policy_constraint(approver, approve_reimbursement). "
                        "Do not write event_occurred(approval, r1)."
                    ),
                    "must_not_write": ["event_occurred/2"],
                }
            ],
            "self_check": {"profile_authority": "proposal_only", "notes": []},
        }

        score = profile_bootstrap_score(parsed)

        self.assertEqual(score["frontier_unknown_positive_predicate_count"], 2)
        self.assertEqual(
            score["frontier_unknown_positive_predicate_refs"],
            ["approved_by/3", "policy_constraint/2"],
        )

    def test_score_ignores_commas_and_parentheses_inside_quoted_values(self) -> None:
        parsed = {
            "schema_version": "profile_bootstrap_v1",
            "domain_guess": "legal_case_summary",
            "domain_scope": "Board and court decision summaries.",
            "confidence": 0.9,
            "source_summary": ["sample"],
            "entity_types": [{"name": "case", "description": "Case record.", "examples": ["case_001"]}],
            "candidate_predicates": [
                {
                    "signature": "case_location/2",
                    "args": ["case_id", "location"],
                    "description": "Case location.",
                    "why": "Location is stated in the source.",
                    "admission_notes": ["Keep the source location as a value."],
                },
                {
                    "signature": "party_role/3",
                    "args": ["case_id", "party_id", "role"],
                    "description": "Party role in the case.",
                    "why": "Parties and roles are queryable.",
                    "admission_notes": ["Party names may contain punctuation."],
                },
                {
                    "signature": "legal_finding/4",
                    "args": ["case_id", "section", "actor", "stance"],
                    "description": "Legal finding.",
                    "why": "Findings need actor and stance.",
                    "admission_notes": ["Legal sections may contain parenthesized citations."],
                },
            ],
            "repeated_structures": [],
            "likely_functional_predicates": [],
            "provenance_sensitive_predicates": ["legal_finding/4"],
            "admission_risks": ["case/finding collapse"],
            "clarification_policy": ["clarify actor"],
            "unsafe_transformations": ["do not infer findings"],
            "starter_frontier_cases": [
                {
                    "utterance": "The board issued a finding in River City, AA.",
                    "expected_boundary": (
                        "case_location('case_001', 'River City, AA'). "
                        "party_role('case_001', 'Sample Industries, Inc.', 'Respondent'). "
                        "legal_finding('case_001', 'Section 8(a)(5) and (1)', 'Board', 'held')."
                    ),
                    "must_not_write": [],
                }
            ],
            "self_check": {"profile_authority": "proposal_only", "notes": []},
        }

        score = profile_bootstrap_score(parsed)

        self.assertEqual(score["frontier_unknown_positive_predicate_refs"], [])

    def test_score_catches_repeated_structure_refs_outside_palette(self) -> None:
        parsed = {
            "schema_version": "profile_bootstrap_v1",
            "domain_guess": "founding_document",
            "domain_scope": "Declaration-style source documents.",
            "confidence": 0.9,
            "source_summary": ["sample"],
            "entity_types": [{"name": "grievance", "description": "Source accusation record.", "examples": ["g1"]}],
            "candidate_predicates": [
                {
                    "signature": "grievance/2",
                    "args": ["grievance_id", "grievance_type"],
                    "description": "A recurring source grievance record.",
                    "why": "The source contains a repeated accusation list.",
                    "admission_notes": ["Keep as source claim, not objective fact."],
                }
            ],
            "repeated_structures": [
                {
                    "name": "grievance list",
                    "why": "Repeated accusation records need stable ids and properties.",
                    "id_strategy": "g1, g2, ...",
                    "record_predicate": "grievance/2",
                    "property_predicates": ["grievance_actor/2"],
                    "example_records": ["grievance(g1, withheld_assent)."],
                    "admission_notes": ["Actor predicate must be in the palette before use."],
                }
            ],
            "likely_functional_predicates": [],
            "provenance_sensitive_predicates": ["grievance/2"],
            "admission_risks": ["Claim/fact collapse"],
            "clarification_policy": ["Clarify ambiguous authority labels"],
            "unsafe_transformations": ["Do not assert accusations as verified facts"],
            "starter_frontier_cases": [
                {"utterance": "It withheld assent.", "expected_boundary": "grievance(g1, withheld_assent)", "must_not_write": []}
            ],
            "self_check": {"profile_authority": "proposal_only", "notes": []},
        }

        score = profile_bootstrap_score(parsed)

        self.assertEqual(score["repeated_structure_count"], 1)
        self.assertEqual(score["repeated_structure_unknown_predicate_refs"], ["grievance_actor/2"])

    def test_score_treats_repeated_structure_lookup_properties_as_diagnostic_only(self) -> None:
        parsed = {
            "schema_version": "profile_bootstrap_v1",
            "domain_guess": "public_record",
            "domain_scope": "Source records with repeated findings and provenance links.",
            "confidence": 0.9,
            "source_summary": ["sample"],
            "entity_types": [{"name": "finding", "description": "Repeated source finding.", "examples": ["f1"]}],
            "candidate_predicates": [
                {
                    "signature": "finding/2",
                    "args": ["finding_id", "label"],
                    "description": "A repeated source finding.",
                    "why": "The source has multiple findings.",
                    "admission_notes": ["Keep finding id stable."],
                },
                {
                    "signature": "source_supports/4",
                    "args": ["predicate_name", "subject_key", "source_ref", "support_type"],
                    "description": "Provenance support for a proposed predicate.",
                    "why": "Source references support semantic rows.",
                    "admission_notes": ["This is provenance, not a per-finding property."],
                },
                {
                    "signature": "instrument_obligation/3",
                    "args": ["instrument_name", "obligation_type", "description"],
                    "description": "Lookup row for obligations defined by a source instrument.",
                    "why": "Some obligations attach to source instruments.",
                    "admission_notes": ["Do not treat as a repeated finding property."],
                },
                {
                    "signature": "instrument_amount/2",
                    "args": ["instrument_id", "amount"],
                    "description": "Record-keyed property for a specific instrument row.",
                    "why": "The first role is already a stable id.",
                    "admission_notes": ["This should not be reported as a lookup-property ref."],
                },
            ],
            "repeated_structures": [
                {
                    "name": "finding list",
                    "why": "Findings need stable ids.",
                    "id_strategy": "f1, f2, ...",
                    "record_predicate": "finding/2",
                    "property_predicates": ["source_supports/4", "instrument_obligation/3", "instrument_amount/2"],
                    "example_records": ["finding(f1, missing_notice)."],
                    "admission_notes": ["Global lookup rows are diagnostic only for this gate."],
                }
            ],
            "likely_functional_predicates": [],
            "provenance_sensitive_predicates": ["finding/2", "source_supports/4"],
            "admission_risks": ["Finding/support collapse"],
            "clarification_policy": ["Clarify source support"],
            "unsafe_transformations": ["Do not assert support rows as objective findings"],
            "starter_frontier_cases": [
                {"utterance": "Which finding is supported?", "expected_boundary": "finding(f1, missing_notice)", "must_not_write": []}
            ],
            "self_check": {"profile_authority": "proposal_only", "notes": []},
        }

        score = profile_bootstrap_score(parsed)

        self.assertEqual(
            score["repeated_structure_lookup_property_refs"],
            ["instrument_obligation/3", "source_supports/4"],
        )
        self.assertEqual(score["repeated_structure_role_mismatch_refs"], [])

    def test_score_still_flags_repeated_structure_property_role_mismatch(self) -> None:
        parsed = {
            "schema_version": "profile_bootstrap_v1",
            "domain_guess": "public_record",
            "domain_scope": "Source records with repeated findings.",
            "confidence": 0.9,
            "source_summary": ["sample"],
            "entity_types": [{"name": "finding", "description": "Repeated source finding.", "examples": ["f1"]}],
            "candidate_predicates": [
                {
                    "signature": "finding/2",
                    "args": ["finding_id", "label"],
                    "description": "A repeated source finding.",
                    "why": "The source has multiple findings.",
                    "admission_notes": ["Keep finding id stable."],
                },
                {
                    "signature": "status_bucket/2",
                    "args": ["status", "value"],
                    "description": "A status/value property.",
                    "why": "Status values appear in the source.",
                    "admission_notes": ["Must be keyed before it can describe a repeated finding."],
                },
            ],
            "repeated_structures": [
                {
                    "name": "finding list",
                    "why": "Findings need stable ids.",
                    "id_strategy": "f1, f2, ...",
                    "record_predicate": "finding/2",
                    "property_predicates": ["status_bucket/2"],
                    "example_records": ["finding(f1, missing_notice)."],
                    "admission_notes": ["Property rows need a record id or subject first."],
                }
            ],
            "likely_functional_predicates": [],
            "provenance_sensitive_predicates": ["finding/2"],
            "admission_risks": ["Finding/status collapse"],
            "clarification_policy": ["Clarify status holder"],
            "unsafe_transformations": ["Do not detach status from its finding"],
            "starter_frontier_cases": [
                {"utterance": "Which finding has a status?", "expected_boundary": "finding(f1, missing_notice)", "must_not_write": []}
            ],
            "self_check": {"profile_authority": "proposal_only", "notes": []},
        }

        score = profile_bootstrap_score(parsed)

        self.assertEqual(score["repeated_structure_lookup_property_refs"], [])
        self.assertEqual(score["repeated_structure_role_mismatch_refs"], ["status_bucket/2"])

    def test_score_accepts_record_noun_as_repeated_structure_property_key(self) -> None:
        parsed = {
            "schema_version": "profile_bootstrap_v1",
            "domain_guess": "regulatory_sanctions",
            "domain_scope": "Repeated sanction records with typed properties.",
            "confidence": 0.9,
            "source_summary": ["sample"],
            "entity_types": [{"name": "sanction", "description": "Repeated sanction.", "examples": ["s1"]}],
            "candidate_predicates": [
                {
                    "signature": "sanction_record/2",
                    "args": ["sanction", "label"],
                    "description": "Repeated sanction record.",
                    "why": "The source lists sanctions.",
                    "admission_notes": ["The first arg is the sanction key."],
                },
                {
                    "signature": "sanction_type/2",
                    "args": ["sanction", "type"],
                    "description": "Type for a sanction.",
                    "why": "The source states sanction types.",
                    "admission_notes": ["First arg uses the record noun, not the word id."],
                },
                {
                    "signature": "observed_conduct/3",
                    "args": ["entity", "conduct", "service"],
                    "description": "Observed conduct.",
                    "why": "The source states conduct.",
                    "admission_notes": ["Entity is not the sanction record key."],
                },
            ],
            "repeated_structures": [
                {
                    "name": "sanction list",
                    "why": "Sanctions have properties.",
                    "id_strategy": "s1, s2",
                    "record_predicate": "sanction_record/2",
                    "property_predicates": ["sanction_type/2", "observed_conduct/3"],
                    "example_records": ["sanction_record(s1, fine)."],
                    "admission_notes": ["Properties should be keyed by sanction."],
                }
            ],
            "likely_functional_predicates": [],
            "provenance_sensitive_predicates": ["sanction_record/2"],
            "admission_risks": ["sanction/property collapse"],
            "clarification_policy": ["clarify sanction holder"],
            "unsafe_transformations": ["do not detach properties"],
            "starter_frontier_cases": [
                {
                    "utterance": "The sanction was a fine.",
                    "expected_boundary": "sanction_record(s1, fine). sanction_type(s1, fine).",
                    "must_not_write": [],
                }
            ],
            "self_check": {"profile_authority": "proposal_only", "notes": []},
        }

        score = profile_bootstrap_score(parsed)

        self.assertEqual(score["repeated_structure_lookup_property_refs"], [])
        self.assertEqual(score["repeated_structure_role_mismatch_refs"], ["observed_conduct/3"])

    def test_load_jsonl_accepts_harness_rows_as_samples(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "samples.jsonl"
            path.write_text(
                json.dumps(
                    {
                        "id": "case_1",
                        "domain": "sec_contracts",
                        "utterance": "Borrower shall repay the loan.",
                        "context": ["Obligation not fact."],
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            rows = _load_jsonl(path, limit=10)

        self.assertEqual(rows[0]["id"], "case_1")
        self.assertEqual(rows[0]["domain_hint"], "sec_contracts")
        self.assertEqual(rows[0]["text"], "Borrower shall repay the loan.")
        self.assertEqual(rows[0]["context"], ["Obligation not fact."])


if __name__ == "__main__":
    unittest.main()
