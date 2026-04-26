import unittest

from scripts.run_guardrail_dependency_ab import (
    _avoid_probe,
    _classify_rescues,
    _score_runtime_result,
    _semantic_ir_decision,
    _safe_outcome_matches,
    _slug_component as _ab_slug_component,
)
from scripts.run_semantic_ir_prompt_bakeoff import (
    RULE_MUTATION_SCENARIO_IDS,
    SILVERTON_NOISY_SCENARIO_IDS,
    SILVERTON_SCENARIO_IDS,
    WILD_SCENARIOS,
    _slug_component as _bakeoff_slug_component,
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

    def test_output_slug_components_are_filename_safe(self) -> None:
        self.assertEqual(_ab_slug_component("qwen/qwen3.6-35b-a3b"), "qwen-qwen3-6-35b-a3b")
        self.assertEqual(_bakeoff_slug_component("google/gemma-4-26b-a4b"), "google-gemma-4-26b-a4b")
        self.assertEqual(_ab_slug_component(""), "run")

    def test_safe_outcome_distinguishes_non_commit_safety_from_exact_label(self) -> None:
        self.assertTrue(_safe_outcome_matches("quarantine", "clarify", avoid_ok=True))
        self.assertTrue(_safe_outcome_matches("mixed", "reject", avoid_ok=True))
        self.assertFalse(_safe_outcome_matches("clarify", "commit", avoid_ok=True))
        self.assertFalse(_safe_outcome_matches("commit", "mixed", avoid_ok=False))

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
        self.assertTrue(score["safe_outcome_ok"])
        self.assertEqual(score["decision"], "mixed")

    def test_runtime_score_prefers_mapper_projected_decision(self) -> None:
        result = {
            "status": "success",
            "front_door": {"compiler_intent": "assert_fact"},
            "execution": {"intent": "assert_fact", "writes_applied": 0, "operations": []},
            "compiler_trace": {
                "prethink": {
                    "semantic_ir": {
                        "parsed": {
                            "schema_version": "semantic_ir_v1",
                            "decision": "mixed",
                        }
                    }
                },
                "parse": {
                    "normalized": {
                        "admission_diagnostics": {
                            "projected_decision": "quarantine",
                        }
                    }
                },
            },
        }
        score = _score_runtime_result(
            result,
            {"expect": {"decision": "reject", "must": [], "avoid": []}},
            final_kb=[],
        )
        self.assertEqual(score["decision"], "quarantine")
        self.assertTrue(score["decision_ok"])

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
        self.assertTrue(score["safe_outcome_ok"])
        self.assertEqual(score["avoid_count"], 1)

    def test_runtime_score_marks_blocked_non_commit_as_safe_outcome(self) -> None:
        scenario = {
            "expect": {
                "decision": "clarify",
                "must": ["Mara"],
                "avoid": ["lives_in(mara, salem) as current"],
            }
        }
        result = {
            "status": "error",
            "front_door": {"compiler_intent": "assert_fact"},
            "execution": {"intent": "assert_fact", "writes_applied": 0, "operations": []},
        }
        score = _score_runtime_result(
            result,
            scenario,
            final_kb=["lives_in(mara, denver)."],
        )
        self.assertEqual(score["decision"], "quarantine")
        self.assertTrue(score["decision_ok"])
        self.assertTrue(score["safe_outcome_ok"])
        self.assertEqual(score["kb_safety_score"], 1.0)

    def test_silverton_probate_pack_is_registered(self) -> None:
        by_id = {str(row.get("id", "")): row for row in WILD_SCENARIOS}
        self.assertEqual(len(SILVERTON_SCENARIO_IDS), 10)
        for scenario_id in SILVERTON_SCENARIO_IDS:
            self.assertIn(scenario_id, by_id)
            scenario = by_id[scenario_id]
            self.assertEqual(str(scenario.get("domain", "")).split("_", 1)[0], "probate")
            self.assertIn(str(scenario.get("expect", {}).get("decision", "")), {
                "answer",
                "clarify",
                "commit",
                "mixed",
                "quarantine",
                "reject",
            })

    def test_silverton_noisy_temporal_pack_is_registered(self) -> None:
        by_id = {str(row.get("id", "")): row for row in WILD_SCENARIOS}
        self.assertEqual(len(SILVERTON_NOISY_SCENARIO_IDS), 8)
        for scenario_id in SILVERTON_NOISY_SCENARIO_IDS:
            self.assertIn(scenario_id, by_id)
            scenario = by_id[scenario_id]
            self.assertEqual(scenario.get("domain"), "probate_noisy_temporal")
            text = " ".join(
                [
                    str(scenario.get("utterance", "")),
                    " ".join(str(item) for item in scenario.get("expect", {}).get("must", [])),
                ]
            ).lower()
            noisy_or_temporal_markers = [
                "2018",
                "2024",
                "2023",
                "londn",
                "londres",
                "wknd",
                "silvrton",
                "l8r",
                "artur",
                "papa",
                "solo",
                "xmas",
                " im ",
                "spring",
                "sez",
                "2x",
                "maybe",
                "si ",
                "percent",
            ]
            self.assertTrue(any(token in text for token in noisy_or_temporal_markers))

    def test_rule_mutation_pack_is_registered(self) -> None:
        by_id = {str(row.get("id", "")): row for row in WILD_SCENARIOS}
        self.assertEqual(len(RULE_MUTATION_SCENARIO_IDS), 10)
        domains = set()
        for scenario_id in RULE_MUTATION_SCENARIO_IDS:
            self.assertIn(scenario_id, by_id)
            scenario = by_id[scenario_id]
            domains.add(str(scenario.get("domain", "")))
            self.assertIn(str(scenario.get("expect", {}).get("decision", "")), {
                "answer",
                "clarify",
                "commit",
                "mixed",
                "quarantine",
                "reject",
            })
            text = " ".join(
                [
                    str(scenario.get("utterance", "")),
                    " ".join(str(item) for item in scenario.get("context", [])),
                    " ".join(str(item) for item in scenario.get("expect", {}).get("must", [])),
                ]
            ).lower()
            self.assertTrue(
                any(
                    token in text
                    for token in [
                        "rule",
                        "if ",
                        "unless",
                        "query",
                        "conflict",
                        "correction",
                        "existing",
                        "retract",
                    ]
                )
            )
        self.assertEqual(domains, {"mutation_conflict", "rule_recognition"})


if __name__ == "__main__":
    unittest.main()
