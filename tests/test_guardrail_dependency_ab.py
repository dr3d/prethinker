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
    HARBOR_FRONTIER_SCENARIO_IDS,
    POLICY_DEMO_SCENARIO_IDS,
    RULE_MUTATION_SCENARIO_IDS,
    SILVERTON_NOISY_SCENARIO_IDS,
    SILVERTON_SCENARIO_IDS,
    SOURCE_FIDELITY_SCENARIO_IDS,
    WILD_SCENARIOS,
    _slug_component as _bakeoff_slug_component,
    score_admission,
    score_record,
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

    def test_admission_score_checks_truth_maintenance_evidence(self) -> None:
        mapped = {
            "admission_diagnostics": {
                "clauses": {
                    "facts": ["requested_by(reimbursement_1, maya)."],
                    "queries": ["violation(reimbursement_1, reimbursement_policy)."],
                },
                "clause_supports": {
                    "facts": [
                        {
                            "clause": "requested_by(reimbursement_1, maya).",
                            "support_ref": "R1 requested by Maya",
                        }
                    ]
                },
                "truth_maintenance": {
                    "support_links": [
                        {
                            "operation_index": 0,
                            "support_kind": "direct_utterance",
                            "support_ref": "R1 requested by Maya",
                            "role": "grounds",
                        }
                    ],
                    "conflicts": [
                        {
                            "new_operation_index": 1,
                            "conflict_kind": "claim_vs_observation",
                            "why": "claim conflicts with observation",
                        }
                    ],
                    "derived_consequences": [
                        {
                            "statement": "R1 violates reimbursement policy",
                            "commit_policy": "query_only",
                        }
                    ],
                },
                "operations": [],
            }
        }
        scenario = {
            "expect": {
                "admission": {
                    "must_admit_fact": [["requested_by(r1", "requested_by(reimbursement_1"]],
                    "must_admit_query": ["violation("],
                    "must_support_ref": ["direct_utterance", "R1 requested"],
                    "must_conflict": ["claim_vs_observation"],
                    "must_derived_consequence": [["violation", "violates"], "query_only"],
                }
            }
        }
        score = score_admission(mapped, scenario)
        self.assertTrue(score["ok"], score)
        self.assertEqual(score["check_count"], score["check_total"])

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

    def test_harbor_frontier_pack_is_registered(self) -> None:
        by_id = {str(row.get("id", "")): row for row in WILD_SCENARIOS}
        self.assertEqual(len(HARBOR_FRONTIER_SCENARIO_IDS), 14)
        domains = set()
        for scenario_id in HARBOR_FRONTIER_SCENARIO_IDS:
            self.assertIn(scenario_id, by_id)
            scenario = by_id[scenario_id]
            domains.add(str(scenario.get("domain", "")))
            self.assertTrue(str(scenario_id).startswith("harbor_"))
            self.assertIn(str(scenario.get("expect", {}).get("decision", "")), {
                "answer",
                "clarify",
                "commit",
                "mixed",
                "quarantine",
                "reject",
            })
            self.assertTrue(scenario.get("allowed_predicates"))
            text = " ".join(
                [
                    str(scenario.get("utterance", "")),
                    " ".join(str(item) for item in scenario.get("context", [])),
                    " ".join(str(item) for item in scenario.get("expect", {}).get("must", [])),
                    " ".join(str(item) for item in scenario.get("expect", {}).get("avoid", [])),
                ]
            ).lower()
            self.assertTrue(
                any(
                    token in text
                    for token in [
                        "existing",
                        "claim",
                        "correction",
                        "unless",
                        "before",
                        "after",
                        "effective",
                        "witness",
                        "allergy",
                        "query",
                        "except",
                        "role",
                        "trustee",
                    ]
                )
            )
        self.assertTrue({"harbor_house_legal", "harbor_house_temporal"}.issubset(domains))

    def test_policy_demo_pack_is_registered(self) -> None:
        by_id = {str(row.get("id", "")): row for row in WILD_SCENARIOS}
        self.assertEqual(len(POLICY_DEMO_SCENARIO_IDS), 7)
        domains = set()
        for scenario_id in POLICY_DEMO_SCENARIO_IDS:
            self.assertIn(scenario_id, by_id)
            scenario = by_id[scenario_id]
            domains.add(str(scenario.get("domain", "")))
            self.assertTrue(scenario.get("predicate_contracts"))
            self.assertTrue(scenario.get("allowed_predicates"))
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
                    " ".join(str(item) for item in scenario.get("expect", {}).get("avoid", [])),
                ]
            ).lower()
            self.assertTrue(
                any(
                    token in text
                    for token in [
                        "policy",
                        "rule",
                        "violate",
                        "depends",
                        "blocked",
                        "query",
                        "commitment",
                        "claim",
                    ]
                )
            )
            admission = scenario.get("expect", {}).get("admission", {})
            self.assertTrue(
                any(
                    key in admission
                    for key in ["must_support_ref", "must_conflict", "must_derived_consequence"]
                )
            )
        self.assertTrue({"policy_stress_test", "meeting_commitment", "story_world"}.issubset(domains))

    def test_source_fidelity_pack_is_registered(self) -> None:
        by_id = {str(row.get("id", "")): row for row in WILD_SCENARIOS}
        self.assertEqual(SOURCE_FIDELITY_SCENARIO_IDS, ["story_source_fidelity_otter_names"])
        scenario = by_id[SOURCE_FIDELITY_SCENARIO_IDS[0]]
        self.assertEqual(scenario.get("domain"), "story_source_fidelity")
        self.assertIn("member_of/2", scenario.get("allowed_predicates", []))
        self.assertIn("gathered/2", scenario.get("allowed_predicates", []))
        self.assertTrue(scenario.get("predicate_contracts"))
        expected_text = " ".join(
            [
                " ".join(str(item) for item in scenario.get("expect", {}).get("must", [])),
                " ".join(str(item) for item in scenario.get("expect", {}).get("avoid", [])),
            ]
        ).lower()
        self.assertIn("little slip of an otter", expected_text)
        self.assertIn("baby_bear", expected_text)
        self.assertIn("gave(", expected_text)

    def test_source_fidelity_score_catches_prior_leakage_and_bad_relation(self) -> None:
        by_id = {str(row.get("id", "")): row for row in WILD_SCENARIOS}
        scenario = by_id["story_source_fidelity_otter_names"]
        parsed = {
            "schema_version": "semantic_ir_v1",
            "decision": "commit",
            "turn_type": "state_update",
            "entities": [
                {"id": "e1", "surface": "Little Slip of an Otter", "normalized": "little_otter", "type": "person", "confidence": 0.82},
                {"id": "e2", "surface": "Baby Bear", "normalized": "baby_bear", "type": "person", "confidence": 0.77},
            ],
            "referents": [],
            "assertions": [],
            "unsafe_implications": [],
            "candidate_operations": [
                {
                    "operation": "assert",
                    "predicate": "gave",
                    "args": ["group_of_otters", "little_mint_sprig", "little_otter"],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                    "confidence": 0.86,
                },
                {
                    "operation": "assert",
                    "predicate": "is_a",
                    "args": ["little_otter", "three_otters"],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                    "confidence": 0.83,
                },
            ],
            "clarification_questions": [],
            "truth_maintenance": {},
            "self_check": {"bad_commit_risk": "low", "notes": []},
        }
        score = score_record(parsed, scenario)
        self.assertLess(score["avoid_count"], score["avoid_total"], score)
        self.assertLess(score["must_count"], score["must_total"], score)

    def test_source_fidelity_admission_contract_catches_bad_writes(self) -> None:
        by_id = {str(row.get("id", "")): row for row in WILD_SCENARIOS}
        scenario = by_id["story_source_fidelity_otter_names"]
        mapped = {
            "admission_diagnostics": {
                "clauses": {
                    "facts": [
                        "gave(group_of_otters, little_mint_sprig, little_otter).",
                        "is_a(little_otter, three_otters).",
                        "owns(baby_bear, baby_bear_bowl).",
                    ]
                },
                "operations": [
                    {
                        "admitted": True,
                        "effect": "fact",
                        "operation": "assert",
                        "predicate": "gave",
                        "args": ["group_of_otters", "little_mint_sprig", "little_otter"],
                    }
                ],
            }
        }
        score = score_admission(mapped, scenario)
        self.assertFalse(score["ok"], score)
        self.assertTrue(any("must_not_admit_fact" in miss for miss in score["misses"]))


if __name__ == "__main__":
    unittest.main()
