import unittest

from kb_pipeline import _validate_parsed
from src.mcp_server import PrologMCPServer
from src.semantic_ir import (
    semantic_ir_admission_diagnostics,
    semantic_ir_to_legacy_parse,
    semantic_ir_to_prethink_payload,
)


def _ir(**updates):
    payload = {
        "schema_version": "semantic_ir_v1",
        "decision": "commit",
        "turn_type": "state_update",
        "entities": [
            {"id": "e1", "surface": "Mara", "normalized": "Mara", "type": "person", "confidence": 0.99},
            {"id": "e2", "surface": "silver compass", "normalized": "silver compass", "type": "object", "confidence": 0.96},
        ],
        "referents": [],
        "assertions": [],
        "unsafe_implications": [],
        "candidate_operations": [
            {
                "operation": "assert",
                "predicate": "owns",
                "args": ["e1", "e2"],
                "polarity": "positive",
                "source": "direct",
                "safety": "safe",
            }
        ],
        "clarification_questions": [],
        "self_check": {"bad_commit_risk": "low", "missing_slots": [], "notes": []},
    }
    payload.update(updates)
    return payload


class SemanticIRRuntimeTests(unittest.TestCase):
    def test_mapper_emits_valid_legacy_parse_for_safe_assert(self) -> None:
        parsed, warnings = semantic_ir_to_legacy_parse(_ir())
        self.assertEqual(warnings, [])
        self.assertEqual(parsed["intent"], "assert_fact")
        self.assertEqual(parsed["facts"], ["owns(mara, silver_compass)."])
        ok, errors = _validate_parsed(parsed)
        self.assertTrue(ok, errors)

    def test_mapper_skips_negative_assertion_until_negation_policy_exists(self) -> None:
        ir = _ir(
            candidate_operations=[
                {
                    "operation": "assert",
                    "predicate": "party_to",
                    "args": ["Tomas", "Celia and Jonas marriage"],
                    "polarity": "negative",
                    "source": "direct",
                    "safety": "safe",
                }
            ]
        )
        parsed, warnings = semantic_ir_to_legacy_parse(ir)
        self.assertEqual(parsed["intent"], "other")
        self.assertEqual(parsed["facts"], [])
        self.assertTrue(any("negative assertion" in warning for warning in warnings))

    def test_mapper_allows_negative_polarity_retract_as_retraction(self) -> None:
        ir = _ir(
            candidate_operations=[
                {
                    "operation": "retract",
                    "predicate": "owns",
                    "args": ["e1", "e2"],
                    "polarity": "negative",
                    "source": "direct",
                    "safety": "safe",
                }
            ]
        )
        parsed, warnings = semantic_ir_to_legacy_parse(ir)
        self.assertEqual(warnings, [])
        self.assertEqual(parsed["intent"], "retract")
        self.assertEqual(parsed["logic_string"], "retract(owns(mara, silver_compass)).")
        self.assertEqual(parsed["correction_retract_clauses"], ["owns(mara, silver_compass)."])

    def test_mapper_adds_retract_alias_for_numbered_entity(self) -> None:
        ir = _ir(
            candidate_operations=[
                {
                    "operation": "retract",
                    "predicate": "cleared",
                    "args": ["crate_12"],
                    "polarity": "negative",
                    "source": "direct",
                    "safety": "safe",
                },
                {
                    "operation": "assert",
                    "predicate": "quarantined",
                    "args": ["crate_12"],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                },
            ]
        )
        parsed, warnings = semantic_ir_to_legacy_parse(ir)
        self.assertEqual(warnings, [])
        self.assertIn("cleared(crate_12).", parsed["correction_retract_clauses"])
        self.assertIn("cleared(crate12).", parsed["correction_retract_clauses"])

    def test_mapper_correction_retract_assert_validates_with_assert_logic_string(self) -> None:
        ir = _ir(
            candidate_operations=[
                {
                    "operation": "retract",
                    "predicate": "owns",
                    "args": ["e1", "e2"],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                },
                {
                    "operation": "assert",
                    "predicate": "owns",
                    "args": ["Oskar", "silver compass"],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                },
            ]
        )
        parsed, warnings = semantic_ir_to_legacy_parse(ir)
        self.assertEqual(warnings, [])
        self.assertEqual(parsed["intent"], "assert_fact")
        self.assertEqual(parsed["logic_string"], "owns(oskar, silver_compass).")
        self.assertEqual(parsed["correction_retract_clauses"], ["owns(mara, silver_compass)."])
        ok, errors = _validate_parsed(parsed)
        self.assertTrue(ok, errors)

    def test_mapper_allows_denial_event_with_negative_polarity(self) -> None:
        ir = _ir(
            candidate_operations=[
                {
                    "operation": "assert",
                    "predicate": "denied",
                    "args": ["Omar", "waiver", "signed"],
                    "polarity": "negative",
                    "source": "direct",
                    "safety": "safe",
                }
            ]
        )
        parsed, warnings = semantic_ir_to_legacy_parse(ir)
        self.assertEqual(warnings, [])
        self.assertEqual(parsed["intent"], "assert_fact")
        self.assertEqual(parsed["facts"], ["denied(omar, waiver, signed)."])

    def test_mapper_skips_quantified_group_assertion_without_expansion(self) -> None:
        ir = _ir(
            entities=[
                {
                    "id": "e1",
                    "surface": "All residents",
                    "normalized": "residents",
                    "type": "person",
                    "confidence": 0.9,
                },
                {"id": "e2", "surface": "Kai", "normalized": "Kai", "type": "person", "confidence": 0.95},
            ],
            candidate_operations=[
                {
                    "operation": "assert",
                    "predicate": "submitted_form",
                    "args": ["e1"],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                },
                {
                    "operation": "assert",
                    "predicate": "submitted_waiver",
                    "args": ["e2"],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                },
            ],
        )
        parsed, warnings = semantic_ir_to_legacy_parse(ir)
        self.assertEqual(parsed["facts"], ["submitted_waiver(kai)."])
        self.assertTrue(any("quantified set assertion" in warning for warning in warnings))

    def test_prethink_payload_treats_pure_hypothetical_as_query(self) -> None:
        ir = _ir(
            decision="clarify",
            turn_type="query",
            candidate_operations=[
                {
                    "operation": "query",
                    "predicate": "receives_hazard_pay",
                    "args": ["Felix"],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                }
            ],
            clarification_questions=["Are you asking hypothetically?"],
            self_check={
                "bad_commit_risk": "high",
                "missing_slots": [],
                "notes": ["This is a hypothetical would-question."],
            },
        )
        payload = semantic_ir_to_prethink_payload(ir)
        self.assertEqual(payload["intent"], "query")
        self.assertFalse(payload["needs_clarification"])

    def test_mapper_allows_inferred_query_for_pure_hypothetical(self) -> None:
        ir = _ir(
            decision="mixed",
            turn_type="query",
            unsafe_implications=[
                {
                    "candidate": "receives_hazard_pay(felix)",
                    "why_unsafe": "Hypothetical consequence is not a fact.",
                    "commit_policy": "reject",
                }
            ],
            candidate_operations=[
                {
                    "operation": "query",
                    "predicate": "receives_hazard_pay",
                    "args": ["Felix"],
                    "polarity": "positive",
                    "source": "inferred",
                    "safety": "safe",
                }
            ],
            self_check={
                "bad_commit_risk": "low",
                "missing_slots": [],
                "notes": ["hypothetical if/would query"],
            },
        )
        parsed, warnings = semantic_ir_to_legacy_parse(ir)
        self.assertEqual(warnings, [])
        self.assertEqual(parsed["intent"], "query")
        self.assertEqual(parsed["queries"], ["receives_hazard_pay(felix)."])

    def test_mapper_skips_context_sourced_asserts_as_existing_state(self) -> None:
        ir = _ir(
            candidate_operations=[
                {
                    "operation": "assert",
                    "predicate": "owns",
                    "args": ["Mara", "silver compass"],
                    "polarity": "positive",
                    "source": "context",
                    "safety": "safe",
                },
                {
                    "operation": "assert",
                    "predicate": "located_in",
                    "args": ["silver compass", "locker"],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                },
            ]
        )
        parsed, warnings = semantic_ir_to_legacy_parse(ir)
        self.assertEqual(parsed["facts"], ["located_in(silver_compass, locker)."])
        self.assertTrue(any("context-sourced write" in warning for warning in warnings))
        diagnostics = parsed["admission_diagnostics"]
        self.assertEqual(diagnostics["operation_count"], 2)
        self.assertEqual(diagnostics["admitted_count"], 1)
        self.assertEqual(diagnostics["skipped_count"], 1)
        skipped = [row for row in diagnostics["operations"] if not row["admitted"]]
        self.assertEqual(skipped[0]["skip_reason"], "context_write_not_admissible")
        self.assertIn("source_policy", skipped[0]["rationale_codes"])

    def test_admission_diagnostics_explain_projection_and_skips(self) -> None:
        ir = _ir(
            decision="commit",
            unsafe_implications=[
                {
                    "candidate": "possessed(bob, key)",
                    "why_unsafe": "Possession is implied, not directly observed.",
                    "commit_policy": "quarantine",
                }
            ],
            candidate_operations=[
                {
                    "operation": "assert",
                    "predicate": "returned",
                    "args": ["Bob", "Alice", "key"],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                },
                {
                    "operation": "assert",
                    "predicate": "possessed",
                    "args": ["Bob", "key"],
                    "polarity": "positive",
                    "source": "inferred",
                    "safety": "safe",
                },
            ],
        )
        diagnostics = semantic_ir_admission_diagnostics(ir)
        self.assertEqual(diagnostics["model_decision"], "commit")
        self.assertEqual(diagnostics["projected_decision"], "mixed")
        self.assertEqual(
            diagnostics["projection_reason"],
            "safe_write_with_unsafe_implications_projected_to_mixed",
        )
        self.assertEqual(diagnostics["admitted_count"], 1)
        self.assertEqual(diagnostics["skipped_count"], 1)
        skipped = [row for row in diagnostics["operations"] if not row["admitted"]]
        self.assertEqual(skipped[0]["skip_reason"], "inferred_write_not_admissible")
        self.assertEqual(diagnostics["clauses"]["facts"], ["returned(bob, alice, key)."])

    def test_low_risk_clarify_alternative_does_not_downgrade_safe_correction(self) -> None:
        ir = _ir(
            decision="commit",
            turn_type="correction",
            candidate_operations=[
                {
                    "operation": "retract",
                    "predicate": "has_allergy",
                    "args": ["Leo", "penicillin"],
                    "polarity": "negative",
                    "source": "context",
                    "safety": "safe",
                },
                {
                    "operation": "assert",
                    "predicate": "side_effect",
                    "args": ["Leo", "penicillin", "stomach upset"],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                },
            ],
            unsafe_implications=[
                {
                    "candidate": "has_symptom(leo, stomach_upset)",
                    "why_unsafe": "Alternative modeling choice, not an active symptom.",
                    "commit_policy": "clarify",
                }
            ],
            self_check={"bad_commit_risk": "low", "missing_slots": [], "notes": []},
        )
        parsed, warnings = semantic_ir_to_legacy_parse(ir)
        self.assertEqual(warnings, [])
        self.assertEqual(parsed["intent"], "assert_fact")
        self.assertIn("decision=commit", parsed["rationale"])
        self.assertEqual(parsed["admission_diagnostics"]["projected_decision"], "commit")

    def test_context_labeled_writes_with_unsafe_implications_project_to_mixed(self) -> None:
        ir = _ir(
            decision="commit",
            turn_type="state_update",
            candidate_operations=[
                {
                    "operation": "assert",
                    "predicate": "showed",
                    "args": ["camera", "Omar", "unlocking cabinet"],
                    "polarity": "positive",
                    "source": "context",
                    "safety": "safe",
                }
            ],
            unsafe_implications=[
                {
                    "candidate": "took(omar, key)",
                    "why_unsafe": "Usage does not prove acquisition.",
                    "commit_policy": "reject",
                }
            ],
            self_check={"bad_commit_risk": "low", "missing_slots": [], "notes": []},
        )
        parsed, warnings = semantic_ir_to_legacy_parse(ir)
        self.assertTrue(any("context-sourced write" in warning for warning in warnings))
        self.assertEqual(parsed["intent"], "other")
        diagnostics = parsed["admission_diagnostics"]
        self.assertEqual(diagnostics["projected_decision"], "mixed")
        self.assertEqual(
            diagnostics["projection_reason"],
            "context_writes_with_unsafe_implications_projected_to_mixed",
        )

    def test_ambiguous_pronouns_with_only_speech_wrapper_project_to_clarify(self) -> None:
        ir = _ir(
            decision="mixed",
            turn_type="mixed",
            referents=[
                {
                    "surface": "her sister",
                    "status": "ambiguous",
                    "candidates": ["mara_sister", "priya_sister"],
                    "chosen": "mara_sister",
                }
            ],
            candidate_operations=[
                {
                    "operation": "assert",
                    "predicate": "told",
                    "args": ["Mara", "Priya", "claim_content"],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                },
                {
                    "operation": "assert",
                    "predicate": "saw",
                    "args": ["mara_sister", "van"],
                    "polarity": "positive",
                    "source": "inferred",
                    "safety": "unsafe",
                },
            ],
            clarification_questions=["Whose sister saw the van?"],
            self_check={"bad_commit_risk": "high", "missing_slots": [], "notes": []},
        )
        parsed, warnings = semantic_ir_to_legacy_parse(ir)
        self.assertEqual(warnings, [])
        self.assertEqual(parsed["intent"], "other")
        self.assertEqual(parsed["facts"], [])
        self.assertTrue(parsed["needs_clarification"])
        diagnostics = parsed["admission_diagnostics"]
        self.assertEqual(diagnostics["projected_decision"], "clarify")
        self.assertEqual(
            diagnostics["projection_reason"],
            "ambiguous_referents_with_only_speech_wrapper_projected_to_clarify",
        )
        self.assertEqual(diagnostics["admitted_count"], 0)
        self.assertTrue(
            any(
                row["skip_reason"] == "projected_decision_clarify_blocks_write"
                for row in diagnostics["operations"]
            )
        )

    def test_prethink_payload_does_not_block_on_optional_provenance_slot(self) -> None:
        ir = _ir(
            decision="quarantine",
            turn_type="correction",
            candidate_operations=[
                {
                    "operation": "retract",
                    "predicate": "cleared",
                    "args": ["crate_12"],
                    "polarity": "negative",
                    "source": "direct",
                    "safety": "safe",
                }
            ],
            self_check={
                "bad_commit_risk": "high",
                "missing_slots": ["reason_for_quarantine"],
                "notes": ["The correction itself is clear; the missing slot is metadata."],
            },
        )
        payload = semantic_ir_to_prethink_payload(ir)
        self.assertEqual(payload["intent"], "retract")
        self.assertFalse(payload["needs_clarification"])
        self.assertLess(payload["uncertainty_score"], 0.25)

    def test_quarantined_correction_still_projects_safe_retract(self) -> None:
        ir = _ir(
            decision="quarantine",
            turn_type="correction",
            candidate_operations=[
                {
                    "operation": "retract",
                    "predicate": "cleared",
                    "args": ["crate_12"],
                    "polarity": "negative",
                    "source": "direct",
                    "safety": "safe",
                },
                {
                    "operation": "assert",
                    "predicate": "quarantined",
                    "args": ["crate_12"],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "needs_clarification",
                },
            ],
            self_check={
                "bad_commit_risk": "high",
                "missing_slots": [],
                "notes": ["The replacement assertion is unsafe, but the old clear fact is a safe retraction."],
            },
        )
        parsed, warnings = semantic_ir_to_legacy_parse(ir)
        self.assertEqual(warnings, [])
        self.assertEqual(parsed["intent"], "retract")
        self.assertIn("retract(cleared(crate12)).", parsed["logic_string"])

    def test_prethink_payload_uses_clarify_for_missing_slot(self) -> None:
        ir = _ir(
            decision="clarify",
            candidate_operations=[],
            clarification_questions=["Which patient does 'his' refer to?"],
            self_check={"bad_commit_risk": "high", "missing_slots": ["patient"], "notes": []},
        )
        payload = semantic_ir_to_prethink_payload(ir)
        self.assertTrue(payload["needs_clarification"])
        self.assertEqual(payload["clarification_question"], "Which patient does 'his' refer to?")
        self.assertGreaterEqual(payload["uncertainty_score"], 0.82)

    def test_prethink_payload_projects_commit_with_unsafe_implication_as_mixed(self) -> None:
        ir = _ir(
            decision="commit",
            unsafe_implications=[
                {
                    "candidate": "took(omar, key)",
                    "why_unsafe": "Reported denial is not evidence of taking.",
                    "commit_policy": "reject",
                }
            ],
        )
        payload = semantic_ir_to_prethink_payload(ir)
        self.assertIn("decision=mixed", payload["rationale"])
        self.assertFalse(payload["needs_clarification"])

    def test_prethink_payload_projects_claim_plus_direct_observation_as_mixed(self) -> None:
        ir = _ir(
            decision="commit",
            assertions=[
                {
                    "kind": "claim",
                    "subject": "Omar",
                    "relation_concept": "denied",
                    "object": "taking_key",
                    "polarity": "negative",
                    "certainty": 0.9,
                },
                {
                    "kind": "direct",
                    "subject": "camera",
                    "relation_concept": "showed",
                    "object": "unlocking",
                    "polarity": "positive",
                    "certainty": 0.9,
                },
            ],
        )
        payload = semantic_ir_to_prethink_payload(ir)
        self.assertIn("decision=mixed", payload["rationale"])

    def test_prethink_payload_ignores_duplicate_unsafe_implication_for_safe_operation(self) -> None:
        ir = _ir(
            decision="commit",
            turn_type="correction",
            candidate_operations=[
                {
                    "operation": "retract",
                    "predicate": "has_allergy",
                    "args": ["Leo", "penicillin"],
                    "polarity": "negative",
                    "source": "context",
                    "safety": "safe",
                }
            ],
            unsafe_implications=[
                {
                    "candidate": "retract(has_allergy(leo, penicillin))",
                    "why_unsafe": "Draft thought contradicted by final safe operation.",
                    "commit_policy": "clarify",
                }
            ],
        )
        payload = semantic_ir_to_prethink_payload(ir)
        self.assertIn("decision=commit", payload["rationale"])

    def test_server_semantic_ir_path_skips_legacy_rescue_chain(self) -> None:
        server = PrologMCPServer(
            compiler_prompt_enabled=False,
            semantic_ir_enabled=True,
            semantic_ir_model="qwen3.6:35b",
        )

        def fake_compile_semantic_ir(utterance: str):
            return _ir(), ""

        server._compile_semantic_ir = fake_compile_semantic_ir  # type: ignore[method-assign]
        result = server.process_utterance({"utterance": "Mara owns the silver compass."})
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["front_door"]["compiler"]["model"], "qwen3.6:35b")
        self.assertTrue(result["front_door"]["compiler"]["semantic_ir_enabled"])
        execution = result["execution"]
        self.assertEqual(execution["writes_applied"], 1)
        trace = result["compiler_trace"]["parse"]
        rescue_names = [row["name"] for row in trace["rescues"]]
        self.assertEqual(rescue_names, ["semantic_ir_mapper"])
        diagnostics = trace["rescues"][0]["admission_diagnostics"]
        self.assertEqual(diagnostics["admitted_count"], 1)
        self.assertEqual(diagnostics["operations"][0]["effect"], "fact")
        query = server.query_rows("owns(mara, X).")
        self.assertEqual(query["status"], "success")
        self.assertEqual(query["rows"], [{"X": "silver_compass"}])

    def test_server_retract_alias_no_result_does_not_poison_success(self) -> None:
        server = PrologMCPServer(
            compiler_prompt_enabled=False,
            semantic_ir_enabled=True,
            semantic_ir_model="qwen3.6:35b",
        )
        server.assert_fact("cleared(crate12).")

        def fake_compile_semantic_ir(utterance: str):
            return _ir(
                decision="quarantine",
                turn_type="correction",
                candidate_operations=[
                    {
                        "operation": "retract",
                        "predicate": "cleared",
                        "args": ["crate_12"],
                        "polarity": "negative",
                        "source": "direct",
                        "safety": "safe",
                    }
                ],
                self_check={"bad_commit_risk": "high", "missing_slots": [], "notes": []},
            ), ""

        server._compile_semantic_ir = fake_compile_semantic_ir  # type: ignore[method-assign]
        result = server.process_utterance({"utterance": "Actually crate12 should be quarantined instead."})
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["execution"]["writes_applied"], 1)
        self.assertEqual(server.query_rows("cleared(crate12).")["status"], "no_results")


if __name__ == "__main__":
    unittest.main()
