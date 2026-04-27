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
        "truth_maintenance": {
            "support_links": [],
            "conflicts": [],
            "retraction_plan": [],
            "derived_consequences": [],
        },
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

    def test_mapper_admits_minimal_temporal_fact_vocabulary(self) -> None:
        ir = _ir(
            candidate_operations=[
                {
                    "operation": "assert",
                    "predicate": "interval_start",
                    "args": ["silverton_a_london_interval", "2018_03"],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                },
                {
                    "operation": "assert",
                    "predicate": "interval_end",
                    "args": ["silverton_a_london_interval", "2024_04"],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                },
                {
                    "operation": "assert",
                    "predicate": "corrected_temporal_value",
                    "args": ["silverton_a_return_stamp", "return_date", "2024_04", "2023_04"],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                },
            ]
        )
        parsed, warnings = semantic_ir_to_legacy_parse(ir)
        self.assertEqual(warnings, [])
        self.assertEqual(parsed["intent"], "assert_fact")
        self.assertEqual(
            parsed["facts"],
            [
                "interval_start(silverton_a_london_interval, 2018_03).",
                "interval_end(silverton_a_london_interval, 2024_04).",
                "corrected_temporal_value(silverton_a_return_stamp, return_date, 2024_04, 2023_04).",
            ],
        )

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

    def test_mapper_skips_placeholder_argument_write(self) -> None:
        ir = _ir(
            candidate_operations=[
                {
                    "operation": "assert",
                    "predicate": "lab_result_high",
                    "args": ["patient", "blood_pressure_measurement"],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                }
            ]
        )
        parsed, warnings = semantic_ir_to_legacy_parse(ir)
        self.assertEqual(parsed["intent"], "other")
        self.assertEqual(parsed["facts"], [])
        self.assertTrue(any("unresolved placeholder" in warning for warning in warnings))
        skipped = [
            row
            for row in parsed["admission_diagnostics"]["operations"]
            if not row["admitted"]
        ]
        self.assertEqual(skipped[0]["skip_reason"], "ungrounded_argument_atom")

    def test_mapper_skips_placeholder_prefixed_argument_write(self) -> None:
        ir = _ir(
            candidate_operations=[
                {
                    "operation": "assert",
                    "predicate": "sat_in",
                    "args": ["unknown_agent", "middle sized bear chair"],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                }
            ]
        )
        parsed, warnings = semantic_ir_to_legacy_parse(
            ir,
            allowed_predicates=["sat_in/2"],
        )
        self.assertEqual(parsed["intent"], "other")
        self.assertEqual(parsed["facts"], [])
        self.assertTrue(any("unresolved placeholder" in warning for warning in warnings))
        skipped = [
            row
            for row in parsed["admission_diagnostics"]["operations"]
            if not row["admitted"]
        ]
        self.assertEqual(skipped[0]["skip_reason"], "ungrounded_argument_atom")

    def test_mapper_skips_null_and_generic_actor_placeholder_writes(self) -> None:
        ir = _ir(
            candidate_operations=[
                {
                    "operation": "assert",
                    "predicate": "docket_entry",
                    "args": ["Doe v Acme", "42", "null", "null"],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                },
                {
                    "operation": "assert",
                    "predicate": "entered",
                    "args": ["female_actor", "Sonic Zips"],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                },
            ]
        )
        parsed, warnings = semantic_ir_to_legacy_parse(
            ir,
            allowed_predicates=["docket_entry/4", "entered/2"],
        )
        self.assertEqual(parsed["facts"], [])
        self.assertEqual(parsed["intent"], "other")
        self.assertEqual(len(warnings), 2)
        skipped = [
            row
            for row in parsed["admission_diagnostics"]["operations"]
            if not row["admitted"]
        ]
        self.assertEqual([row["skip_reason"] for row in skipped], ["ungrounded_argument_atom", "ungrounded_argument_atom"])

    def test_mapper_collapses_duplicate_candidate_operations(self) -> None:
        ir = _ir(
            candidate_operations=[
                {
                    "operation": "assert",
                    "predicate": "document_states",
                    "args": ["Tomas", "condition_role_title"],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                },
                {
                    "operation": "assert",
                    "predicate": "document_states",
                    "args": ["Tomas", "condition_role_title"],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                },
            ]
        )
        parsed, warnings = semantic_ir_to_legacy_parse(
            ir,
            allowed_predicates=["document_states/2"],
        )
        self.assertEqual(parsed["facts"], ["document_states(tomas, condition_role_title)."])
        self.assertTrue(any("duplicate candidate operation" in warning for warning in warnings))
        diagnostics = parsed["admission_diagnostics"]
        self.assertEqual(diagnostics["admitted_count"], 1)
        self.assertEqual(diagnostics["skipped_count"], 1)
        skipped = [
            row
            for row in diagnostics["operations"]
            if not row["admitted"]
        ]
        self.assertEqual(skipped[0]["skip_reason"], "duplicate_candidate_operation")

    def test_mapper_blocks_clear_contract_role_mismatch(self) -> None:
        ir = _ir(
            candidate_operations=[
                {
                    "operation": "assert",
                    "predicate": "interval_start",
                    "args": ["e1", "2024-01-01"],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                }
            ]
        )
        parsed, warnings = semantic_ir_to_legacy_parse(
            ir,
            allowed_predicates=["interval_start/2"],
            predicate_contracts=[
                {"signature": "interval_start/2", "arguments": ["interval", "date"]},
            ],
        )
        self.assertEqual(parsed["facts"], [])
        self.assertEqual(parsed["intent"], "other")
        self.assertTrue(any("role interval" in warning for warning in warnings))
        diagnostics = parsed["admission_diagnostics"]
        self.assertEqual(diagnostics["projected_decision"], "quarantine")
        self.assertEqual(
            diagnostics["projection_reason"],
            "contract_role_mismatch_projected_to_quarantine",
        )
        skipped = [
            row
            for row in diagnostics["operations"]
            if not row["admitted"]
        ]
        self.assertEqual(skipped[0]["skip_reason"], "predicate_contract_role_mismatch")

    def test_mapper_admits_contract_role_shape_when_interval_is_grounded(self) -> None:
        ir = _ir(
            candidate_operations=[
                {
                    "operation": "assert",
                    "predicate": "outside_district_interval",
                    "args": ["e1", "district", "mira_absence_interval_1"],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                },
                {
                    "operation": "assert",
                    "predicate": "interval_start",
                    "args": ["mira_absence_interval_1", "2024-01-01"],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                },
            ]
        )
        parsed, warnings = semantic_ir_to_legacy_parse(
            ir,
            allowed_predicates=["outside_district_interval/3", "interval_start/2"],
            predicate_contracts=[
                {"signature": "outside_district_interval/3", "arguments": ["person", "district_or_scope", "interval"]},
                {"signature": "interval_start/2", "arguments": ["interval", "date"]},
            ],
        )
        self.assertEqual(warnings, [])
        self.assertEqual(
            parsed["facts"],
            [
                "outside_district_interval(mara, district, mira_absence_interval_1).",
                "interval_start(mira_absence_interval_1, 2024_01_01).",
            ],
        )
        diagnostics = parsed["admission_diagnostics"]
        self.assertEqual(diagnostics["features"]["predicate_contract_enabled"], True)
        self.assertEqual(diagnostics["features"]["has_contract_invalid_safe_write"], False)

    def test_mapper_records_clause_supports_for_admitted_operations(self) -> None:
        parsed, warnings = semantic_ir_to_legacy_parse(_ir())
        self.assertEqual(warnings, [])
        supports = parsed["clause_supports"]["facts"]
        self.assertEqual(len(supports), 1)
        self.assertEqual(supports[0]["clause"], "owns(mara, silver_compass).")
        self.assertEqual(supports[0]["operation_index"], 0)
        self.assertEqual(supports[0]["predicate"], "owns")
        self.assertEqual(supports[0]["source"], "direct")
        self.assertIn("safe_direct_fact", supports[0]["rationale_codes"])

    def test_mapper_surfaces_truth_maintenance_without_granting_authority(self) -> None:
        ir = _ir(
            decision="mixed",
            candidate_operations=[
                {
                    "operation": "assert",
                    "predicate": "lives_in",
                    "args": ["Mara", "Paris"],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                },
                {
                    "operation": "assert",
                    "predicate": "citizen_of",
                    "args": ["Mara", "France"],
                    "polarity": "positive",
                    "source": "inferred",
                    "safety": "safe",
                },
            ],
            truth_maintenance={
                "support_links": [
                    {
                        "operation_index": 0,
                        "support_kind": "direct_utterance",
                        "support_ref": "current turn",
                        "role": "grounds",
                        "confidence": 0.98,
                    }
                ],
                "conflicts": [
                    {
                        "new_operation_index": 0,
                        "existing_ref": "context:lives_in(mara,london)",
                        "conflict_kind": "functional_overwrite",
                        "recommended_policy": "clarify",
                        "why": "Residence behaves like current state without explicit correction.",
                    }
                ],
                "retraction_plan": [
                    {
                        "operation_index": 0,
                        "target_ref": "context:lives_in(mara,london)",
                        "reason": "superseded_current_state",
                    }
                ],
                "derived_consequences": [
                    {
                        "statement": "Mara may be in France.",
                        "basis": ["op:0"],
                        "commit_policy": "do_not_commit",
                    }
                ],
            },
        )

        parsed, warnings = semantic_ir_to_legacy_parse(ir, allowed_predicates=["lives_in/2", "citizen_of/2"])

        self.assertTrue(any("inferred safe operation" in warning for warning in warnings))
        self.assertEqual(parsed["facts"], ["lives_in(mara, paris)."])
        self.assertEqual(parsed["admission_diagnostics"]["admitted_count"], 1)
        truth = parsed["truth_maintenance"]
        self.assertEqual(truth["support_links"][0]["support_ref"], "current turn")
        self.assertEqual(truth["conflicts"][0]["conflict_kind"], "functional_overwrite")
        self.assertEqual(truth["retraction_plan"][0]["reason"], "superseded_current_state")
        self.assertEqual(truth["derived_consequences"][0]["commit_policy"], "do_not_commit")

    def test_mapper_applies_profile_contract_validator_without_language_patch(self) -> None:
        ir = _ir(
            decision="commit",
            entities=[
                {"id": "e1", "surface": "court", "normalized": "court", "type": "object", "confidence": 0.99},
                {"id": "e2", "surface": "Doe v Acme", "normalized": "Doe v Acme", "type": "object", "confidence": 0.99},
            ],
            candidate_operations=[
                {
                    "operation": "assert",
                    "predicate": "claim_made",
                    "args": ["complaint", "Acme", "breached lease", "Doe v Acme"],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                },
                {
                    "operation": "assert",
                    "predicate": "finding",
                    "args": ["e1", "e2", "complaint alleged breach", "opinion"],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                },
            ],
        )
        parsed, warnings = semantic_ir_to_legacy_parse(
            ir,
            allowed_predicates=["claim_made/4", "finding/4"],
            predicate_contracts=[
                {"signature": "claim_made/4", "arguments": ["speaker_or_document", "claim_subject", "claim_content", "source"]},
                {
                    "signature": "finding/4",
                    "arguments": ["court_or_judge", "case", "finding_content", "source"],
                    "validators": [
                        {
                            "kind": "argument_must_not_contain_terms",
                            "argument": "finding_content",
                            "terms": ["alleged", "complaint"],
                            "reason": "allegation_not_court_finding",
                        }
                    ],
                },
            ],
        )
        self.assertEqual(parsed["facts"], ["claim_made(complaint, acme, breached_lease, doe_v_acme)."])
        self.assertTrue(any("allegation_not_court_finding" in warning for warning in warnings))
        diagnostics = parsed["admission_diagnostics"]
        self.assertEqual(diagnostics["projected_decision"], "mixed")
        self.assertEqual(diagnostics["projection_reason"], "profile_contract_policy_projected_to_mixed")
        self.assertEqual(diagnostics["features"]["has_contract_policy_invalid_safe_write"], True)
        skipped = [row for row in diagnostics["operations"] if not row["admitted"]]
        self.assertEqual(skipped[0]["skip_reason"], "allegation_not_court_finding")

    def test_mapper_blocks_inverted_temporal_interval(self) -> None:
        ir = _ir(
            decision="commit",
            candidate_operations=[
                {
                    "operation": "assert",
                    "predicate": "interval_start",
                    "args": ["absence_interval_1", "2024-05-01"],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                },
                {
                    "operation": "assert",
                    "predicate": "interval_end",
                    "args": ["absence_interval_1", "2024-03-01"],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                },
            ],
        )
        parsed, warnings = semantic_ir_to_legacy_parse(
            ir,
            allowed_predicates=["interval_start/2", "interval_end/2"],
            predicate_contracts=[
                {"signature": "interval_start/2", "arguments": ["interval", "date"]},
                {"signature": "interval_end/2", "arguments": ["interval", "date"]},
            ],
        )
        self.assertEqual(parsed["facts"], [])
        self.assertEqual(parsed["admission_diagnostics"]["projected_decision"], "quarantine")
        self.assertEqual(
            parsed["admission_diagnostics"]["projection_reason"],
            "temporal_interval_order_projected_to_quarantine",
        )
        self.assertTrue(any("interval start is after interval end" in warning for warning in warnings))
        self.assertEqual(parsed["admission_diagnostics"]["features"]["has_temporal_interval_order_mismatch"], True)

    def test_mapper_admits_story_world_predicates_from_palette(self) -> None:
        ir = _ir(
            candidate_operations=[
                {
                    "operation": "assert",
                    "predicate": "sat_in",
                    "args": ["Goldilocks", "Baby Bear chair"],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                },
                {
                    "operation": "assert",
                    "predicate": "broke",
                    "args": ["Baby Bear chair"],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                },
                {
                    "operation": "assert",
                    "predicate": "was_tasted",
                    "args": ["Papa Bear porridge"],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                },
            ]
        )
        parsed, warnings = semantic_ir_to_legacy_parse(
            ir,
            allowed_predicates=["sat_in/2", "broke/1", "was_tasted/1"],
        )
        self.assertEqual(warnings, [])
        self.assertEqual(
            parsed["facts"],
            [
                "sat_in(goldilocks, baby_bear_chair).",
                "broke(baby_bear_chair).",
                "was_tasted(papa_bear_porridge).",
            ],
        )

    def test_projection_marks_positive_write_plus_unsupported_negative_assertion_mixed(self) -> None:
        ir = _ir(
            candidate_operations=[
                {
                    "operation": "assert",
                    "predicate": "authentic",
                    "args": ["flood transfer"],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                },
                {
                    "operation": "assert",
                    "predicate": "approved_before",
                    "args": ["Pavel", "flood transfer", "trustee bonuses"],
                    "polarity": "negative",
                    "source": "direct",
                    "safety": "safe",
                },
            ]
        )
        parsed, warnings = semantic_ir_to_legacy_parse(
            ir,
            allowed_predicates=["authentic/1", "approved_before/3"],
        )
        self.assertTrue(any("negative assertion" in warning for warning in warnings))
        diagnostics = parsed["admission_diagnostics"]
        self.assertEqual(diagnostics["projected_decision"], "mixed")
        self.assertEqual(
            diagnostics["projection_reason"],
            "positive_write_with_unsupported_negative_assertion_projected_to_mixed",
        )
        self.assertEqual(parsed["facts"], ["authentic(flood_transfer)."])
        skipped = [row for row in diagnostics["operations"] if not row["admitted"]]
        self.assertEqual(skipped[0]["skip_reason"], "negative_fact_semantics_not_supported")

    def test_projection_marks_partial_write_admission_pressure_mixed(self) -> None:
        ir = _ir(
            candidate_operations=[
                {
                    "operation": "assert",
                    "predicate": "signed_log",
                    "args": ["Omar", "medication log"],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                },
                {
                    "operation": "assert",
                    "predicate": "signed_affidavit",
                    "args": ["Lena", "storm affidavit"],
                    "polarity": "positive",
                    "source": "inferred",
                    "safety": "safe",
                },
            ]
        )
        parsed, warnings = semantic_ir_to_legacy_parse(
            ir,
            allowed_predicates=["signed_log/2", "signed_affidavit/2"],
        )
        self.assertTrue(any("inferred safe operation" in warning for warning in warnings))
        diagnostics = parsed["admission_diagnostics"]
        self.assertEqual(diagnostics["projected_decision"], "mixed")
        self.assertEqual(
            diagnostics["projection_reason"],
            "partial_write_admission_pressure_projected_to_mixed",
        )
        self.assertEqual(parsed["facts"], ["signed_log(omar, medication_log)."])

    def test_projection_marks_self_check_rule_conflict_mixed(self) -> None:
        ir = _ir(
            candidate_operations=[
                {
                    "operation": "assert",
                    "predicate": "approved_on",
                    "args": ["Ada", "H7", "June 4"],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                },
                {
                    "operation": "assert",
                    "predicate": "authority_revoked_on",
                    "args": ["Ada", "June 1"],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                },
            ],
            self_check={
                "bad_commit_risk": "low",
                "missing_slots": [],
                "notes": [
                    "Context rule requires active authority on approval date. "
                    "The approval might be invalid under the rule; runtime validity check is still needed."
                ],
            },
        )
        parsed, warnings = semantic_ir_to_legacy_parse(
            ir,
            allowed_predicates=["approved_on/3", "authority_revoked_on/2"],
        )
        self.assertEqual(warnings, [])
        diagnostics = parsed["admission_diagnostics"]
        self.assertEqual(diagnostics["projected_decision"], "mixed")
        self.assertEqual(
            diagnostics["projection_reason"],
            "self_check_rule_conflict_projected_to_mixed",
        )
        self.assertEqual(diagnostics["features"]["has_self_check_rule_conflict"], True)
        self.assertEqual(len(parsed["facts"]), 2)

    def test_projection_admits_safe_direct_writes_from_quarantine(self) -> None:
        ir = _ir(
            decision="quarantine",
            candidate_operations=[
                {
                    "operation": "assert",
                    "predicate": "clinic_shipment",
                    "args": ["H7"],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                },
                {
                    "operation": "assert",
                    "predicate": "release_allowed",
                    "args": ["H7"],
                    "polarity": "positive",
                    "source": "inferred",
                    "safety": "unsafe",
                },
            ],
            unsafe_implications=[
                {
                    "candidate": "release_allowed(h7)",
                    "why_unsafe": "direct fact conflicts with a context rule consequence",
                    "commit_policy": "quarantine",
                }
            ],
            self_check={"bad_commit_risk": "medium", "missing_slots": [], "notes": []},
        )
        parsed, warnings = semantic_ir_to_legacy_parse(
            ir,
            allowed_predicates=["clinic_shipment/1", "release_allowed/1"],
        )
        self.assertEqual(warnings, [])
        diagnostics = parsed["admission_diagnostics"]
        self.assertEqual(diagnostics["projected_decision"], "mixed")
        self.assertEqual(
            diagnostics["projection_reason"],
            "quarantine_with_safe_direct_write_projected_to_mixed",
        )
        self.assertEqual(parsed["facts"], ["clinic_shipment(h7)."])

    def test_mapper_admits_rule_operation_with_explicit_clause(self) -> None:
        ir = _ir(
            decision="commit",
            turn_type="rule_update",
            candidate_operations=[
                {
                    "operation": "rule",
                    "predicate": "ancestor",
                    "args": [],
                    "clause": "ancestor(X, Y) :- parent(X, Y).",
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                }
            ],
        )
        parsed, warnings = semantic_ir_to_legacy_parse(ir)
        self.assertEqual(warnings, [])
        self.assertEqual(parsed["intent"], "assert_rule")
        self.assertEqual(parsed["rules"], ["ancestor(X, Y) :- parent(X, Y)."])
        self.assertEqual(parsed["admission_diagnostics"]["admitted_count"], 1)

    def test_mapper_keeps_assert_logic_string_valid_when_mixed_with_query(self) -> None:
        ir = _ir(
            decision="mixed",
            turn_type="mixed",
            unsafe_implications=[
                {
                    "candidate": "may_ship(crate12)",
                    "why_unsafe": "Candidate conflicts with context-derived shipping permission.",
                    "commit_policy": "clarify",
                }
            ],
            candidate_operations=[
                {
                    "operation": "assert",
                    "predicate": "cannot_ship",
                    "args": ["crate12"],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                },
                {
                    "operation": "query",
                    "predicate": "may_ship",
                    "args": ["crate12"],
                    "polarity": "positive",
                    "source": "context",
                    "safety": "safe",
                },
            ],
        )
        parsed, warnings = semantic_ir_to_legacy_parse(ir)
        self.assertEqual(warnings, [])
        self.assertEqual(parsed["intent"], "assert_fact")
        self.assertEqual(parsed["logic_string"], "cannot_ship(crate12).")
        self.assertEqual(parsed["facts"], ["cannot_ship(crate12)."])
        self.assertEqual(parsed["queries"], ["may_ship(crate12)."])
        ok, errors = _validate_parsed(parsed)
        self.assertTrue(ok, errors)

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

    def test_mapper_allows_placeholder_argument_query(self) -> None:
        ir = _ir(
            decision="clarify",
            turn_type="query",
            candidate_operations=[
                {
                    "operation": "query",
                    "predicate": "lab_result_high",
                    "args": ["patient", "blood_pressure_measurement"],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                }
            ],
            clarification_questions=["Which patient?"],
            self_check={"bad_commit_risk": "medium", "missing_slots": ["patient"], "notes": []},
        )
        parsed, warnings = semantic_ir_to_legacy_parse(ir)
        self.assertEqual(warnings, [])
        self.assertEqual(parsed["intent"], "query")
        self.assertEqual(parsed["queries"], ["lab_result_high(patient, blood_pressure_measurement)."])

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

    def test_ambiguous_query_is_not_projected_to_answer_by_hypothetical_words(self) -> None:
        ir = _ir(
            decision="clarify",
            turn_type="query",
            referents=[
                {
                    "surface": "him",
                    "status": "ambiguous",
                    "candidates": ["arthur", "alfred"],
                    "chosen": None,
                }
            ],
            unsafe_implications=[
                {
                    "candidate": "saw(silas, unknown_male)",
                    "why_unsafe": "Unsafe if the male referent was neither listed candidate.",
                    "commit_policy": "clarify",
                }
            ],
            candidate_operations=[
                {
                    "operation": "query",
                    "predicate": "identity_of",
                    "args": ["him"],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                }
            ],
            clarification_questions=["Who does 'him' refer to?"],
            self_check={
                "bad_commit_risk": "high",
                "missing_slots": [],
                "notes": ["This is ambiguous even though the safety note contains if-language."],
            },
        )
        payload = semantic_ir_to_prethink_payload(ir)
        self.assertEqual(payload["intent"], "query")
        self.assertTrue(payload["needs_clarification"])
        self.assertIn("decision=clarify", payload["rationale"])

    def test_speculative_ambiguous_observation_projects_to_quarantine(self) -> None:
        ir = _ir(
            decision="clarify",
            turn_type="query",
            referents=[
                {
                    "surface": "him",
                    "status": "ambiguous",
                    "candidates": ["arthur", "alfred"],
                    "chosen": None,
                }
            ],
            assertions=[
                {
                    "kind": "question",
                    "subject": "Silas",
                    "relation_concept": "saw",
                    "object": "him",
                    "polarity": "positive",
                    "certainty": 0.5,
                }
            ],
            unsafe_implications=[
                {
                    "candidate": "resided_in(arthur, england, 2022)",
                    "why_unsafe": "Speculative ambiguous witness memory cannot ground residence.",
                    "commit_policy": "clarify",
                }
            ],
            candidate_operations=[
                {
                    "operation": "query",
                    "predicate": "saw",
                    "args": ["Silas", "unknown", "pond"],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "needs_clarification",
                }
            ],
            clarification_questions=["Who does 'him' refer to?"],
            self_check={"bad_commit_risk": "high", "missing_slots": [], "notes": []},
        )
        payload = semantic_ir_to_prethink_payload(ir)
        self.assertEqual(payload["intent"], "other")
        self.assertFalse(payload["needs_clarification"])
        self.assertIn("decision=quarantine", payload["rationale"])
        parsed, warnings = semantic_ir_to_legacy_parse(ir, allowed_predicates=["saw/3", "resided_in/3"])
        self.assertEqual(warnings, [])
        self.assertEqual(parsed["intent"], "other")
        diagnostics = parsed["admission_diagnostics"]
        self.assertEqual(diagnostics["projected_decision"], "quarantine")
        self.assertEqual(
            diagnostics["projection_reason"],
            "speculative_ambiguous_observation_projected_to_quarantine",
        )

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

    def test_mapper_skips_query_scoped_identity_premise(self) -> None:
        ir = _ir(
            decision="mixed",
            turn_type="mixed",
            entities=[
                {"id": "e1", "surface": "Silverton A.", "normalized": "Silverton A.", "type": "person", "confidence": 0.9},
                {"id": "e2", "surface": "Alfred", "normalized": "Alfred", "type": "person", "confidence": 0.9},
                {"id": "e3", "surface": "Arthur", "normalized": "Arthur", "type": "person", "confidence": 0.9},
            ],
            candidate_operations=[
                {
                    "operation": "assert",
                    "predicate": "candidate_identity",
                    "args": ["e1", "e2"],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                },
                {
                    "operation": "query",
                    "predicate": "forfeited_share_to",
                    "args": ["e3", "50"],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                },
            ],
            self_check={
                "bad_commit_risk": "medium",
                "missing_slots": [],
                "notes": ["The utterance asks a conditional question about whether Arthur still loses."],
            },
        )
        parsed, warnings = semantic_ir_to_legacy_parse(ir)
        self.assertEqual(parsed["intent"], "query")
        self.assertEqual(parsed["facts"], [])
        self.assertEqual(parsed["queries"], ["forfeited_share_to(arthur, 50)."])
        self.assertTrue(any("identity premise scoped to a query" in warning for warning in warnings))
        diagnostics = parsed["admission_diagnostics"]
        self.assertEqual(diagnostics["projected_decision"], "answer")
        skipped = [row for row in diagnostics["operations"] if not row["admitted"]]
        self.assertEqual(skipped[0]["skip_reason"], "query_scoped_identity_premise_not_admissible")

    def test_initialed_person_state_write_projects_to_mixed(self) -> None:
        ir = _ir(
            decision="commit",
            turn_type="correction",
            entities=[
                {"id": "e1", "surface": "A. Silverton", "normalized": "A. Silverton", "type": "person", "confidence": 0.95},
                {"id": "e2", "surface": "Apr 2023", "normalized": "2023-04", "type": "time", "confidence": 0.95},
            ],
            candidate_operations=[
                {
                    "operation": "assert",
                    "predicate": "returned_in",
                    "args": ["e1", "e2"],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                }
            ],
        )
        parsed, warnings = semantic_ir_to_legacy_parse(ir)
        self.assertEqual(warnings, [])
        self.assertEqual(parsed["facts"], ["returned_in(a_silverton, 2023_04)."])
        diagnostics = parsed["admission_diagnostics"]
        self.assertEqual(diagnostics["projected_decision"], "mixed")
        self.assertEqual(
            diagnostics["projection_reason"],
            "initialed_person_state_write_projected_to_mixed",
        )

    def test_only_claim_wrapper_with_unsafe_implication_projects_to_quarantine(self) -> None:
        ir = _ir(
            decision="mixed",
            turn_type="mixed",
            candidate_operations=[
                {
                    "operation": "assert",
                    "predicate": "claimed",
                    "args": ["Arthur", "Silas", "witness_reliability_issue"],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                }
            ],
            unsafe_implications=[
                {
                    "candidate": "witness_reliability_issue(silas, discredited)",
                    "why_unsafe": "The committed fact would turn a biased claim into a finding.",
                    "commit_policy": "quarantine",
                }
            ],
            self_check={"bad_commit_risk": "medium", "missing_slots": [], "notes": []},
        )
        parsed, warnings = semantic_ir_to_legacy_parse(ir)
        self.assertEqual(warnings, [])
        self.assertEqual(parsed["intent"], "other")
        self.assertEqual(parsed["facts"], [])
        diagnostics = parsed["admission_diagnostics"]
        self.assertEqual(diagnostics["projected_decision"], "quarantine")
        self.assertEqual(
            diagnostics["projection_reason"],
            "only_communication_writes_with_unsafe_implications_projected_to_quarantine",
        )
        self.assertTrue(
            any(
                row["skip_reason"] == "projected_decision_quarantine_blocks_write"
                for row in diagnostics["operations"]
            )
        )

    def test_mapper_skips_out_of_palette_candidate_operation(self) -> None:
        ir = _ir(
            decision="mixed",
            turn_type="mixed",
            candidate_operations=[
                {
                    "operation": "assert",
                    "predicate": "claimed",
                    "args": ["Arthur", "Father", "all mine now"],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                },
                {
                    "operation": "assert",
                    "predicate": "excluded",
                    "args": ["Arthur", "Beatrice"],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                },
            ],
            unsafe_implications=[
                {
                    "candidate": "valid_amendment(charter_change)",
                    "why_unsafe": "Two-witness rule is not satisfied.",
                    "commit_policy": "quarantine",
                }
            ],
            self_check={"bad_commit_risk": "medium", "missing_slots": [], "notes": []},
        )
        parsed, warnings = semantic_ir_to_legacy_parse(
            ir,
            allowed_predicates=["claimed/3", "valid_amendment/1", "invalid_amendment_reason/2"],
        )
        self.assertEqual(parsed["intent"], "other")
        self.assertEqual(parsed["facts"], [])
        self.assertTrue(any("excluded/2 outside allowed predicate palette" in warning for warning in warnings))
        diagnostics = parsed["admission_diagnostics"]
        self.assertEqual(diagnostics["projected_decision"], "quarantine")
        self.assertTrue(diagnostics["features"]["predicate_palette_enabled"])
        skipped = [row for row in diagnostics["operations"] if not row["admitted"]]
        self.assertTrue(
            any(row["skip_reason"] == "predicate_not_in_allowed_palette" for row in skipped)
        )

    def test_mapper_skips_rule_clause_outside_palette(self) -> None:
        ir = _ir(
            decision="commit",
            turn_type="rule_update",
            candidate_operations=[
                {
                    "operation": "rule",
                    "predicate": "ancestor",
                    "args": [],
                    "clause": "ancestor(X, Y) :- parent(X, Y), trusted_source(X).",
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                }
            ],
        )
        parsed, warnings = semantic_ir_to_legacy_parse(
            ir,
            allowed_predicates=["ancestor/2", "parent/2"],
        )
        self.assertEqual(parsed["intent"], "other")
        self.assertEqual(parsed["rules"], [])
        self.assertEqual(parsed["admission_diagnostics"]["projected_decision"], "quarantine")
        self.assertTrue(any("trusted_source/1" in warning for warning in warnings))

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
        assert_op = next(row for row in execution["operations"] if row.get("tool") == "assert_fact")
        self.assertEqual(assert_op["support"]["clause"], "owns(mara, silver_compass).")
        self.assertEqual(assert_op["support"]["operation_index"], 0)
        self.assertEqual(assert_op["support"]["predicate"], "owns")
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
        server._registry_signatures.add(("cleared", 1))
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

    def test_server_blocks_unannounced_functional_state_overwrite(self) -> None:
        server = PrologMCPServer(
            compiler_prompt_enabled=False,
            semantic_ir_enabled=True,
            semantic_ir_model="qwen3.6:35b",
        )
        server.assert_fact("lives_in(mara, denver).")

        def fake_compile_semantic_ir(utterance: str):
            return _ir(
                candidate_operations=[
                    {
                        "operation": "assert",
                        "predicate": "lives_in",
                        "args": ["Mara", "Salem"],
                        "polarity": "positive",
                        "source": "direct",
                        "safety": "safe",
                    }
                ]
            ), ""

        server._compile_semantic_ir = fake_compile_semantic_ir  # type: ignore[method-assign]
        result = server.process_utterance({"utterance": "Mara lives in Salem."})
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["execution"]["writes_applied"], 0)
        guard_ops = [
            op for op in result["execution"]["operations"] if op.get("tool") == "stored_logic_conflict_guard"
        ]
        self.assertEqual(len(guard_ops), 1)
        conflicts = guard_ops[0]["result"]["conflicts"]
        self.assertEqual(conflicts[0]["kind"], "functional_current_state_conflict")
        self.assertEqual(server.query_rows("lives_in(mara, denver).")["status"], "success")
        self.assertEqual(server.query_rows("lives_in(mara, salem).")["status"], "no_results")

    def test_server_allows_explicit_functional_state_correction(self) -> None:
        server = PrologMCPServer(
            compiler_prompt_enabled=False,
            semantic_ir_enabled=True,
            semantic_ir_model="qwen3.6:35b",
        )
        server.assert_fact("lives_in(mara, denver).")

        def fake_compile_semantic_ir(utterance: str):
            return _ir(
                decision="commit",
                turn_type="correction",
                candidate_operations=[
                    {
                        "operation": "retract",
                        "predicate": "lives_in",
                        "args": ["Mara", "Denver"],
                        "polarity": "positive",
                        "source": "direct",
                        "safety": "safe",
                    },
                    {
                        "operation": "assert",
                        "predicate": "lives_in",
                        "args": ["Mara", "Salem"],
                        "polarity": "positive",
                        "source": "direct",
                        "safety": "safe",
                    },
                ],
            ), ""

        server._compile_semantic_ir = fake_compile_semantic_ir  # type: ignore[method-assign]
        result = server.process_utterance({"utterance": "Correction: Mara lives in Salem, not Denver."})
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["execution"]["writes_applied"], 2)
        self.assertEqual(server.query_rows("lives_in(mara, denver).")["status"], "no_results")
        self.assertEqual(server.query_rows("lives_in(mara, salem).")["status"], "success")

    def test_server_allows_nonexclusive_additional_condition(self) -> None:
        server = PrologMCPServer(
            compiler_prompt_enabled=False,
            semantic_ir_enabled=True,
            semantic_ir_model="qwen3.6:35b",
        )
        server._registry_signatures.add(("has_condition", 2))
        server.assert_fact("has_condition(mara, asthma).")

        def fake_compile_semantic_ir(utterance: str):
            return _ir(
                candidate_operations=[
                    {
                        "operation": "assert",
                        "predicate": "has_condition",
                        "args": ["Mara", "hypertension"],
                        "polarity": "positive",
                        "source": "direct",
                        "safety": "safe",
                    }
                ]
            ), ""

        server._compile_semantic_ir = fake_compile_semantic_ir  # type: ignore[method-assign]
        result = server.process_utterance({"utterance": "Mara also has hypertension."})
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["execution"]["writes_applied"], 1)
        self.assertEqual(server.query_rows("has_condition(mara, asthma).")["status"], "success")
        self.assertEqual(server.query_rows("has_condition(mara, hypertension).")["status"], "success")

    def test_server_blocks_rule_derived_modal_conflict(self) -> None:
        server = PrologMCPServer(
            compiler_prompt_enabled=False,
            semantic_ir_enabled=True,
            semantic_ir_model="qwen3.6:35b",
        )
        server._registry_signatures.update({("cleared", 1), ("may_ship", 1), ("cannot_ship", 1)})
        server.assert_fact("cleared(crate12).")
        server.assert_rule("may_ship(X) :- cleared(X).")

        def fake_compile_semantic_ir(utterance: str):
            return _ir(
                candidate_operations=[
                    {
                        "operation": "assert",
                        "predicate": "cannot_ship",
                        "args": ["crate_12"],
                        "polarity": "positive",
                        "source": "direct",
                        "safety": "safe",
                    }
                ]
            ), ""

        server._compile_semantic_ir = fake_compile_semantic_ir  # type: ignore[method-assign]
        result = server.process_utterance({"utterance": "Crate 12 cannot ship."})
        self.assertEqual(result["status"], "error")
        guard_ops = [
            op for op in result["execution"]["operations"] if op.get("tool") == "stored_logic_conflict_guard"
        ]
        self.assertEqual(guard_ops[0]["result"]["conflicts"][0]["kind"], "rule_derived_modal_conflict")
        self.assertEqual(server.query_rows("cannot_ship(crate12).")["status"], "no_results")


if __name__ == "__main__":
    unittest.main()
