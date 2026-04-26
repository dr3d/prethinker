import unittest

from scripts.run_guardrail_dependency_ab import (
    _avoid_probe,
    _classify_rescues,
    _score_runtime_result,
    _semantic_ir_decision,
)


class GuardrailDependencyABTests(unittest.TestCase):
    def test_rescue_taxonomy_marks_semantic_rescue_english(self) -> None:
        self.assertEqual(
            _classify_rescues(
                [
                    "semantic_ir_mapper",
                    "semantic_ir_prethink_projection",
                    "fallback_classifier",
                    "possessive_family_bundle_normalization",
                    "registry_fact_salvage_guard",
                ]
            ),
            {
                "authority_admission": 1,
                "legacy_route_fallback": 1,
                "semantic_rescue_english": 1,
                "structural_mapper": 2,
            },
        )

    def test_avoid_probe_strips_current_fact_suffix(self) -> None:
        self.assertEqual(
            _avoid_probe("owns_lease(oslo, dock7_lease) as current"),
            "owns_lease(oslo, dock7_lease)",
        )

    def test_runtime_score_uses_semantic_ir_decision_when_available(self) -> None:
        result = {
            "status": "success",
            "front_door": {"compiler_intent": "assert_fact"},
            "execution": {"intent": "assert_fact", "writes_applied": 1, "operations": []},
            "compiler_trace": {
                "prethink": {
                    "semantic_ir": {
                        "parsed": {
                            "schema_version": "semantic_ir_v1",
                            "decision": "mixed",
                        }
                    }
                }
            },
        }
        self.assertEqual(_semantic_ir_decision(result), "mixed")
        score = _score_runtime_result(
            result,
            {"expect": {"decision": "mixed", "must": [], "avoid": []}},
            final_kb=[],
        )
        self.assertTrue(score["decision_ok"])
        self.assertEqual(score["decision"], "mixed")

    def test_runtime_score_checks_avoid_against_final_kb(self) -> None:
        scenario = {
            "expect": {
                "decision": "commit",
                "must": ["Oskar", "Oslo"],
                "avoid": ["owns_lease(oslo, dock7_lease) as current"],
            }
        }
        result = {
            "status": "success",
            "front_door": {"compiler_intent": "assert_fact"},
            "execution": {
                "intent": "assert_fact",
                "writes_applied": 2,
                "operations": [
                    {"tool": "retract_fact", "clause": "owns_lease(oslo, dock7_lease)."},
                    {"tool": "assert_fact", "clause": "owns_lease(oskar, dock7_lease)."},
                ],
            },
        }
        score = _score_runtime_result(
            result,
            scenario,
            final_kb=["owns_lease(oskar, dock7_lease)."],
        )
        self.assertTrue(score["decision_ok"])
        self.assertEqual(score["avoid_count"], 1)


if __name__ == "__main__":
    unittest.main()
