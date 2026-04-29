import json
import tempfile
import unittest
from pathlib import Path

from scripts.run_profile_bootstrap import _load_jsonl
from src.profile_bootstrap import (
    PROFILE_BOOTSTRAP_JSON_SCHEMA,
    build_profile_bootstrap_messages,
    parse_profile_bootstrap_json,
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
        self.assertEqual(score["frontier_unknown_positive_predicate_refs"], [])
        self.assertGreater(score["rough_score"], 0.4)

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
