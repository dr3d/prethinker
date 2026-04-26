import unittest

from kb_pipeline import _validate_parsed
from src.mcp_server import PrologMCPServer
from src.semantic_ir import semantic_ir_to_legacy_parse, semantic_ir_to_prethink_payload


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
        self.assertEqual(parsed["correction_retract_clauses"], ["owns(mara, silver_compass)."])

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
        query = server.query_rows("owns(mara, X).")
        self.assertEqual(query["status"], "success")
        self.assertEqual(query["rows"], [{"X": "silver_compass"}])


if __name__ == "__main__":
    unittest.main()
