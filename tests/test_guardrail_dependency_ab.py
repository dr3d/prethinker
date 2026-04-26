import unittest

from scripts.run_guardrail_dependency_ab import _avoid_probe, _score_runtime_result


class GuardrailDependencyABTests(unittest.TestCase):
    def test_avoid_probe_strips_current_fact_suffix(self) -> None:
        self.assertEqual(
            _avoid_probe("owns_lease(oslo, dock7_lease) as current"),
            "owns_lease(oslo, dock7_lease)",
        )

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
