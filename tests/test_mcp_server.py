import json
import unittest
from pathlib import Path
from unittest.mock import patch

from kb_pipeline import ModelResponse
from src.mcp_server import PrologMCPServer


class LocalMcpServerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.server = PrologMCPServer(compiler_mode="heuristic")

    def test_tools_list_contains_core_surface(self) -> None:
        result = self.server.tools_list()
        self.assertEqual(result.get("status"), "success")
        names = {tool.get("name") for tool in result.get("tools", [])}
        self.assertIn("pre_think", names)
        self.assertIn("set_pre_think_session", names)
        self.assertIn("show_pre_think_state", names)
        self.assertIn("record_clarification_answer", names)
        self.assertIn("process_utterance", names)
        self.assertIn("query_rows", names)
        self.assertIn("assert_fact", names)
        self.assertIn("assert_rule", names)
        self.assertIn("retract_fact", names)

    def test_session_toggle_roundtrip(self) -> None:
        update = self.server.tools_call(
            "set_pre_think_session",
            {
                "enabled": False,
                "all_turns_require_prethink": True,
                "clarification_eagerness": 0.9,
                "require_final_confirmation": False,
            },
        )
        self.assertEqual(update.get("status"), "success")
        state = update.get("state", {})
        self.assertFalse(state.get("enabled"))
        self.assertTrue(state.get("all_turns_require_prethink"))
        self.assertEqual(state.get("clarification_eagerness"), 0.9)
        self.assertFalse(state.get("require_final_confirmation"))

        shown = self.server.tools_call("show_pre_think_state", {})
        self.assertEqual(shown.get("status"), "success")
        self.assertFalse(shown.get("state", {}).get("enabled"))

    def test_runtime_dispatch_query_flow(self) -> None:
        add = self.server.assert_fact("parent(alice, bob).")
        self.assertEqual(add.get("status"), "success")

        query = self.server.tools_call("query_rows", {"query": "parent(alice, X)."})
        self.assertEqual(query.get("status"), "success")
        rows = query.get("rows", [])
        self.assertTrue(any(row.get("X") == "bob" for row in rows))

    def test_write_requires_prethink_and_confirmation(self) -> None:
        blocked = self.server.tools_call("assert_fact", {"clause": "parent(alice, bob)."})
        self.assertEqual(blocked.get("status"), "blocked")
        self.assertEqual(blocked.get("result_type"), "pre_think_required")

        packet = self.server.tools_call("pre_think", {"utterance": "Alice is Bob's parent"})
        self.assertEqual(packet.get("status"), "success")
        prethink_id = packet.get("packet", {}).get("prethink_id")
        self.assertTrue(prethink_id)

        blocked_confirm = self.server.tools_call(
            "assert_fact",
            {"clause": "parent(alice, bob).", "prethink_id": prethink_id},
        )
        self.assertEqual(blocked_confirm.get("status"), "blocked")
        self.assertEqual(blocked_confirm.get("result_type"), "confirmation_required")

        add = self.server.tools_call(
            "assert_fact",
            {"clause": "parent(alice, bob).", "prethink_id": prethink_id, "confirm": True},
        )
        self.assertEqual(add.get("status"), "success")

    def test_single_prethink_allows_multiple_write_facts(self) -> None:
        packet = self.server.tools_call(
            "pre_think",
            {"utterance": "Alice is Bob's parent and Carol's parent"},
        )
        self.assertEqual(packet.get("status"), "success")
        prethink_id = packet.get("packet", {}).get("prethink_id")
        self.assertTrue(prethink_id)

        first = self.server.tools_call(
            "assert_fact",
            {"clause": "parent(alice, bob).", "prethink_id": prethink_id, "confirm": True},
        )
        self.assertEqual(first.get("status"), "success")

        second = self.server.tools_call(
            "assert_fact",
            {"clause": "parent(alice, carol).", "prethink_id": prethink_id, "confirm": True},
        )
        self.assertEqual(second.get("status"), "success")

    def test_query_requires_prethink_when_all_turns_enabled(self) -> None:
        self.server.assert_fact("parent(alice, bob).")
        self.server.tools_call("set_pre_think_session", {"all_turns_require_prethink": True})

        blocked = self.server.tools_call("query_rows", {"query": "parent(alice, X)."})
        self.assertEqual(blocked.get("status"), "blocked")
        self.assertEqual(blocked.get("result_type"), "pre_think_required")

        packet = self.server.tools_call("pre_think", {"utterance": "Who is Alice's child?"})
        self.assertEqual(packet.get("status"), "success")
        prethink_id = packet.get("packet", {}).get("prethink_id")
        self.assertTrue(prethink_id)

        query = self.server.tools_call(
            "query_rows",
            {"query": "parent(alice, X).", "prethink_id": prethink_id},
        )
        self.assertEqual(query.get("status"), "success")
        rows = query.get("rows", [])
        self.assertTrue(any(row.get("X") == "bob" for row in rows))

    def test_single_prethink_supports_interleaved_ingest_and_query_sequence(self) -> None:
        self.server.tools_call("set_pre_think_session", {"all_turns_require_prethink": True})
        packet = self.server.tools_call(
            "pre_think",
            {"utterance": "Alice is Bob's parent. Who is Bob's parent? Also Alice is Carol's parent. Who is Carol's parent?"},
        )
        self.assertEqual(packet.get("status"), "success")
        prethink_id = packet.get("packet", {}).get("prethink_id")
        self.assertTrue(prethink_id)

        add_bob = self.server.tools_call(
            "assert_fact",
            {"clause": "parent(alice, bob).", "prethink_id": prethink_id, "confirm": True},
        )
        self.assertEqual(add_bob.get("status"), "success")

        query_bob = self.server.tools_call(
            "query_rows",
            {"query": "parent(X, bob).", "prethink_id": prethink_id},
        )
        self.assertEqual(query_bob.get("status"), "success")
        self.assertTrue(any(row.get("X") == "alice" for row in query_bob.get("rows", [])))

        add_carol = self.server.tools_call(
            "assert_fact",
            {"clause": "parent(alice, carol).", "prethink_id": prethink_id, "confirm": True},
        )
        self.assertEqual(add_carol.get("status"), "success")

        query_carol = self.server.tools_call(
            "query_rows",
            {"query": "parent(X, carol).", "prethink_id": prethink_id},
        )
        self.assertEqual(query_carol.get("status"), "success")
        self.assertTrue(any(row.get("X") == "alice" for row in query_carol.get("rows", [])))

    def test_pre_think_packet_shape(self) -> None:
        packet = self.server.tools_call("pre_think", {"utterance": "Who is Alice?"})
        self.assertEqual(packet.get("status"), "success")
        self.assertEqual(packet.get("result_type"), "pre_think_packet")
        inner = packet.get("packet", {})
        self.assertEqual(inner.get("mode"), "short_circuit")
        self.assertIn("signals", inner)
        self.assertIn("coreference", inner)

    def test_medical_profile_loads_compiler_guide_and_palette(self) -> None:
        server = PrologMCPServer(compiler_mode="heuristic", active_profile="medical@v0")
        self.assertEqual(server._active_profile, "medical@v0")
        self.assertIn("MEDICAL_CONCEPT_HINTS:", server._compiler_prompt_text)
        self.assertIn("taking/2", server._compiler_prompt_text)
        self.assertIn(
            "Do not invent a patient identity from unresolved pronouns.",
            server._compiler_prompt_text,
        )

    def test_semantic_ir_medical_profile_passes_contracts_and_umls_context(self) -> None:
        server = PrologMCPServer(
            compiler_prompt_enabled=False,
            semantic_ir_enabled=True,
            compiler_backend="lmstudio",
            active_profile="medical@v0",
        )
        server._profile_semantic_ir_context = [
            "profile_scope: bounded medical memory",
            "umls_concept: warfarin; groups=medication; aliases=warfarin, coumadin",
        ]
        parsed = {
            "schema_version": "semantic_ir_v1",
            "decision": "commit",
            "turn_type": "state_update",
            "entities": [],
            "referents": [],
            "assertions": [],
            "unsafe_implications": [],
            "candidate_operations": [],
            "clarification_questions": [],
            "self_check": {"bad_commit_risk": "low", "missing_slots": [], "notes": []},
        }

        with patch(
            "src.mcp_server.call_semantic_ir",
            return_value={"content": "{}", "parsed": parsed, "latency_ms": 1},
        ) as mocked:
            ir, error = server._compile_semantic_ir("Priya is taking Coumadin.")

        self.assertEqual(error, "")
        self.assertIs(ir, parsed)
        kwargs = mocked.call_args.kwargs
        roster = kwargs.get("available_domain_profiles") or []
        self.assertEqual([row.get("profile_id") for row in roster], ["medical@v0"])
        contracts = kwargs.get("predicate_contracts") or []
        self.assertTrue(any(row.get("signature") == "taking/2" for row in contracts))
        taking = next(row for row in contracts if row.get("signature") == "taking/2")
        self.assertEqual(taking.get("arguments"), ["person", "medication"])
        domain_context = "\n".join(kwargs.get("domain_context") or [])
        self.assertIn("bounded medical memory", domain_context)
        self.assertIn("umls_concept:", domain_context)
        trace_input = server._last_semantic_ir_trace.get("model_input", {})
        self.assertTrue(trace_input.get("available_domain_profiles"))
        self.assertEqual([row.get("profile_id") for row in trace_input.get("available_domain_profiles", [])], ["medical@v0"])
        self.assertTrue(trace_input.get("predicate_contracts"))
        self.assertTrue(trace_input.get("domain_context"))
        self.assertTrue(trace_input.get("kb_context_pack"))

    def test_semantic_ir_pinned_profile_skips_router_and_focuses_roster(self) -> None:
        server = PrologMCPServer(
            compiler_prompt_enabled=False,
            semantic_ir_enabled=True,
            compiler_backend="lmstudio",
            active_profile="sec_contracts@v0",
        )
        parsed = {
            "schema_version": "semantic_ir_v1",
            "decision": "commit",
            "turn_type": "state_update",
            "entities": [],
            "referents": [],
            "assertions": [],
            "unsafe_implications": [],
            "candidate_operations": [],
            "clarification_questions": [],
            "self_check": {"bad_commit_risk": "low", "missing_slots": [], "notes": []},
        }

        with patch("src.mcp_server.call_semantic_router") as router, patch(
            "src.mcp_server.call_semantic_ir",
            return_value={"content": "{}", "parsed": parsed, "latency_ms": 1},
        ) as compiler:
            ir, error = server._compile_semantic_ir("The borrower shall repay after maturity.")

        self.assertEqual(error, "")
        self.assertIs(ir, parsed)
        router.assert_not_called()
        selection = server._last_semantic_ir_trace.get("profile_selection", {})
        self.assertTrue(selection.get("semantic_router_skipped"))
        self.assertEqual(selection.get("speed_path"), "active_profile_pinned")
        roster = compiler.call_args.kwargs.get("available_domain_profiles") or []
        self.assertEqual([row.get("profile_id") for row in roster], ["sec_contracts@v0"])

    def test_semantic_ir_receives_compact_kb_context_pack(self) -> None:
        server = PrologMCPServer(
            compiler_prompt_enabled=False,
            semantic_ir_enabled=True,
            compiler_backend="lmstudio",
            active_profile="auto",
        )
        server.assert_fact("lives_in(mara, london).")
        server.assert_fact("has_condition(mara, asthma).")
        server.assert_fact("access_log_entry(jonas, lab_a, april_1).")
        parsed = {
            "schema_version": "semantic_ir_v1",
            "decision": "commit",
            "turn_type": "correction",
            "entities": [],
            "referents": [],
            "assertions": [],
            "unsafe_implications": [],
            "candidate_operations": [],
            "truth_maintenance": {
                "support_links": [],
                "conflicts": [],
                "retraction_plan": [],
                "derived_consequences": [],
            },
            "clarification_questions": [],
            "self_check": {"bad_commit_risk": "low", "missing_slots": [], "notes": []},
        }

        with patch(
            "src.mcp_server.call_semantic_router",
            return_value={
                "content": "{}",
                "parsed": {
                    "schema_version": "semantic_router_v1",
                    "selected_profile_id": "general",
                    "candidate_profile_ids": ["general"],
                    "routing_confidence": 0.9,
                    "turn_shape": "correction",
                    "should_segment": False,
                    "segments": [],
                    "guidance_modules": ["correction_retraction"],
                    "retrieval_hints": {"entity_terms": ["Mara"], "predicate_terms": ["lives_in"], "context_needs": []},
                    "risk_flags": [],
                    "context_audit": {
                        "why_this_profile": "generic correction over current KB state",
                        "selected_context_sources": ["kb_context_pack"],
                        "secondary_profiles_considered": [],
                        "why_not_secondary": [],
                    },
                    "bootstrap_request": {
                        "needed": False,
                        "proposed_domain_name": "",
                        "why": "",
                        "candidate_predicate_concepts": [],
                    },
                    "notes": [],
                },
                "latency_ms": 1,
            },
        ), patch(
            "src.mcp_server.call_semantic_ir",
            return_value={"content": "{}", "parsed": parsed, "latency_ms": 1},
        ) as mocked:
            ir, error = server._compile_semantic_ir("Actually, Mara lives in Paris now.")

        self.assertEqual(error, "")
        self.assertIs(ir, parsed)
        pack = mocked.call_args.kwargs.get("kb_context_pack")
        self.assertIsInstance(pack, dict)
        self.assertEqual(pack.get("version"), "semantic_ir_context_pack_v1")
        self.assertIn("lives_in(mara, london).", pack.get("relevant_clauses", []))
        self.assertIn("lives_in(mara, london).", pack.get("current_state_candidates", []))
        self.assertIn(
            {
                "entity": "mara",
                "role": "current_state_subject",
                "predicate": "lives_in/2",
                "source_clause": "lives_in(mara, london).",
            },
            pack.get("current_state_subject_candidates", []),
        )
        self.assertIn("mara", pack.get("entity_candidates", []))
        self.assertGreaterEqual(pack.get("manifest", {}).get("total_direct_fact_clauses", 0), 3)
        trace_pack = server._last_semantic_ir_trace.get("model_input", {}).get("kb_context_pack", {})
        self.assertEqual(trace_pack.get("version"), "semantic_ir_context_pack_v1")
        context_audit = server._last_semantic_ir_trace.get("context_audit", {})
        self.assertEqual(context_audit.get("version"), "context_audit_v1")
        self.assertEqual(context_audit.get("why_this_profile"), "generic correction over current KB state")
        payload = mocked.call_args.kwargs
        # The API call receives the pack directly; the prompt payload also carries
        # KB policy in src.semantic_ir.build_semantic_ir_input_payload.
        self.assertIn("lives_in(mara, london).", payload.get("kb_context_pack", {}).get("relevant_clauses", []))

    def test_semantic_ir_receives_router_action_context(self) -> None:
        server = PrologMCPServer(
            compiler_prompt_enabled=False,
            semantic_ir_enabled=True,
            compiler_backend="lmstudio",
            active_profile="auto",
        )
        parsed = {
            "schema_version": "semantic_ir_v1",
            "decision": "mixed",
            "turn_type": "mixed",
            "entities": [],
            "referents": [],
            "assertions": [],
            "unsafe_implications": [],
            "candidate_operations": [],
            "truth_maintenance": {
                "support_links": [],
                "conflicts": [],
                "retraction_plan": [],
                "derived_consequences": [],
            },
            "clarification_questions": [],
            "self_check": {"bad_commit_risk": "low", "missing_slots": [], "notes": []},
        }
        router_payload = {
            "schema_version": "semantic_router_v1",
            "selected_profile_id": "sec_contracts@v0",
            "candidate_profile_ids": ["sec_contracts@v0"],
            "routing_confidence": 0.94,
            "turn_shape": "mixed",
            "should_segment": True,
            "segments": [],
            "guidance_modules": ["rule_query_boundary", "temporal_scope"],
            "action_plan": {
                "actions": [
                    "compile_semantic_ir",
                    "extract_query_operations",
                    "include_kb_context",
                    "include_truth_maintenance_guidance",
                    "review_before_admission",
                ],
                "skip_heavy_steps": [],
                "review_triggers": ["mixed_write_query"],
                "why": "turn contains policy writes and a query over policy effects",
            },
            "retrieval_hints": {"entity_terms": [], "predicate_terms": [], "context_needs": []},
            "risk_flags": ["mixed_write_query"],
            "context_audit": {
                "why_this_profile": "contract/policy rule plus query",
                "selected_context_sources": ["sec_contracts@v0", "kb_context_pack"],
                "secondary_profiles_considered": [],
                "why_not_secondary": [],
            },
            "bootstrap_request": {
                "needed": False,
                "proposed_domain_name": "",
                "why": "",
                "candidate_predicate_concepts": [],
            },
            "notes": [],
        }

        with patch(
            "src.mcp_server.call_semantic_router",
            return_value={"content": "{}", "parsed": router_payload, "latency_ms": 1},
        ), patch(
            "src.mcp_server.call_semantic_ir",
            return_value={"content": "{}", "parsed": parsed, "latency_ms": 1},
        ) as mocked:
            ir, error = server._compile_semantic_ir(
                "Record the reimbursement rule, then ask which February claims violate it."
            )

        self.assertEqual(error, "")
        self.assertIs(ir, parsed)
        domain_context = "\n".join(mocked.call_args.kwargs.get("domain_context") or [])
        self.assertIn("router_action_policy:", domain_context)
        self.assertIn("extract_query_operations", domain_context)
        self.assertIn("top-level decision mixed", domain_context)
        self.assertIn("truth_maintenance", domain_context)
        trace_input = server._last_semantic_ir_trace.get("model_input", {})
        action_context = "\n".join(trace_input.get("router_action_context", []))
        self.assertIn("include_kb_context", action_context)
        context_audit = server._last_semantic_ir_trace.get("context_audit", {})
        self.assertEqual(
            context_audit.get("action_plan", {}).get("actions", [])[1],
            "extract_query_operations",
        )

    def test_semantic_router_exact_context_cache_reuses_auto_selection(self) -> None:
        server = PrologMCPServer(
            compiler_prompt_enabled=False,
            semantic_ir_enabled=True,
            compiler_backend="lmstudio",
            active_profile="auto",
        )
        router_payload = {
            "schema_version": "semantic_router_v1",
            "selected_profile_id": "story_world@v0",
            "candidate_profile_ids": ["story_world@v0"],
            "routing_confidence": 0.99,
            "turn_shape": "state_update",
            "should_segment": False,
            "segments": [],
            "guidance_modules": ["source_fidelity"],
            "retrieval_hints": {"entity_terms": [], "predicate_terms": [], "context_needs": []},
            "risk_flags": [],
            "context_audit": {
                "why_this_profile": "story setting",
                "selected_context_sources": [],
                "secondary_profiles_considered": [],
                "why_not_secondary": [],
            },
            "bootstrap_request": {
                "needed": False,
                "proposed_domain_name": "",
                "why": "",
                "candidate_predicate_concepts": [],
            },
            "notes": [],
        }

        with patch(
            "src.mcp_server.call_semantic_router",
            return_value={"content": "{}", "parsed": router_payload, "latency_ms": 123},
        ) as router:
            first = server._semantic_ir_selected_profile_for_utterance("Mara found the key.", context=["scene: archive"])
            second = server._semantic_ir_selected_profile_for_utterance("Mara found the key.", context=["scene: archive"])

        self.assertEqual(first, "story_world@v0")
        self.assertEqual(second, "story_world@v0")
        self.assertEqual(router.call_count, 1)
        self.assertTrue(server._last_semantic_ir_profile_selection.get("cache_hit"))
        self.assertEqual(server._last_semantic_ir_profile_selection.get("latency_ms"), 0)

    def test_semantic_ir_auto_profile_switches_context_across_domains(self) -> None:
        server = PrologMCPServer(
            compiler_prompt_enabled=False,
            semantic_ir_enabled=True,
            compiler_backend="lmstudio",
            active_profile="auto",
        )
        server._profile_semantic_ir_context = [
            "profile_scope: bounded medical memory",
            "umls_concept: warfarin; groups=medication; aliases=warfarin, coumadin",
        ]
        parsed = {
            "schema_version": "semantic_ir_v1",
            "decision": "commit",
            "turn_type": "state_update",
            "entities": [],
            "referents": [],
            "assertions": [],
            "unsafe_implications": [],
            "candidate_operations": [],
            "clarification_questions": [],
            "self_check": {"bad_commit_risk": "low", "missing_slots": [], "notes": []},
        }
        utterances = [
            ("Priya is taking Coumadin.", "medical@v0", "taking/2", "bounded medical memory"),
            (
                "In Doe v. Acme, the complaint alleged breach but the court found only timeliness.",
                "legal_courtlistener@v0",
                "claim_made/4",
                "claim_policy:",
            ),
            (
                "The borrower shall repay the loan after the maturity date unless default is waived.",
                "sec_contracts@v0",
                "obligation/3",
                "obligation_policy:",
            ),
            ("Mara's blood pressure reading was high.", "medical@v0", "lab_result_high/2", "bounded medical memory"),
        ]

        router_results = [
            {
                "content": "{}",
                "parsed": {
                    "schema_version": "semantic_router_v1",
                    "selected_profile_id": expected_profile,
                    "candidate_profile_ids": [expected_profile],
                    "routing_confidence": 0.95,
                    "turn_shape": "state_update",
                    "should_segment": False,
                    "segments": [],
                    "guidance_modules": [],
                    "retrieval_hints": {"entity_terms": [], "predicate_terms": [], "context_needs": []},
                    "risk_flags": [],
                    "bootstrap_request": {
                        "needed": False,
                        "proposed_domain_name": "",
                        "why": "",
                        "candidate_predicate_concepts": [],
                    },
                    "notes": [],
                },
                "latency_ms": 1,
            }
            for _utterance, expected_profile, _expected_signature, _expected_context in utterances
        ]

        with patch("src.mcp_server.call_semantic_router", side_effect=router_results), patch(
            "src.mcp_server.call_semantic_ir",
            return_value={"content": "{}", "parsed": parsed, "latency_ms": 1},
        ) as mocked:
            for utterance, expected_profile, expected_signature, expected_context in utterances:
                ir, error = server._compile_semantic_ir(utterance)
                self.assertEqual(error, "")
                self.assertIs(ir, parsed)
                kwargs = mocked.call_args.kwargs
                self.assertEqual(kwargs.get("domain"), expected_profile)
                signatures = set(kwargs.get("allowed_predicates") or [])
                self.assertIn(expected_signature, signatures)
                self.assertIn(expected_context, "\n".join(kwargs.get("domain_context") or []))
                trace = server._last_semantic_ir_trace
                self.assertEqual(trace.get("selected_profile"), expected_profile)
                self.assertEqual(trace.get("profile_selection", {}).get("profile_id"), expected_profile)

    def test_pre_think_they_coreference_group_with_exception(self) -> None:
        utterance = (
            "I am Scott. my brother is Blake. his wife is Jan. "
            "he has 2 sons Will and Pierce and they live in Morro Bay California "
            "- except Will he lives in San Francisco"
        )
        packet = self.server.tools_call("pre_think", {"utterance": utterance})
        self.assertEqual(packet.get("status"), "success")
        coref = packet.get("packet", {}).get("coreference", {})
        bindings = coref.get("pronoun_bindings", [])
        self.assertTrue(bindings)
        they_binding = bindings[0]
        resolved = {item.lower() for item in they_binding.get("resolved_entities", [])}
        effective = {item.lower() for item in they_binding.get("effective_entities", [])}
        excluded = {item.lower() for item in they_binding.get("excluded_entities", [])}
        self.assertTrue({"blake", "jan", "will", "pierce"}.issubset(resolved))
        self.assertIn("will", excluded)
        self.assertTrue({"blake", "jan", "pierce"}.issubset(effective))

    def test_query_blocked_until_clarification_recorded(self) -> None:
        self.server.tools_call("set_pre_think_session", {"all_turns_require_prethink": True})
        self.server.assert_fact("lives_in(jan, morro_bay_california).")

        packet = self.server.tools_call("pre_think", {"utterance": "They live in Morro Bay"})
        self.assertEqual(packet.get("status"), "success")
        prethink_id = packet.get("packet", {}).get("prethink_id")
        self.assertTrue(prethink_id)

        blocked = self.server.tools_call(
            "query_rows",
            {"query": "lives_in(jan, Place).", "prethink_id": prethink_id},
        )
        self.assertEqual(blocked.get("status"), "blocked")
        self.assertEqual(blocked.get("result_type"), "clarification_required_before_query")

        clarified = self.server.tools_call(
            "record_clarification_answer",
            {"prethink_id": prethink_id, "answer": "they means jan and blake", "confirmed": True},
        )
        self.assertEqual(clarified.get("status"), "success")
        self.assertEqual(clarified.get("result_type"), "clarification_recorded")

        query = self.server.tools_call(
            "query_rows",
            {"query": "lives_in(jan, Place).", "prethink_id": prethink_id},
        )
        self.assertEqual(query.get("status"), "success")
        self.assertTrue(any(row.get("Place") == "morro_bay_california" for row in query.get("rows", [])))

    def test_query_rows_auto_repairs_two_entity_where_live_shape(self) -> None:
        self.server.assert_fact("lives_in(jan, morro_bay_california).")
        self.server.assert_fact("lives_in(will, san_francisco).")

        packet = self.server.tools_call("pre_think", {"utterance": "where does jan and will live"})
        self.assertEqual(packet.get("status"), "success")
        prethink_id = packet.get("packet", {}).get("prethink_id")
        self.assertTrue(prethink_id)

        malformed = "lives_in(jan, X), lives_in(will, Y), write(X, Y)."
        repaired = self.server.tools_call(
            "query_rows",
            {"query": malformed, "prethink_id": prethink_id},
        )
        self.assertEqual(repaired.get("status"), "success")
        self.assertTrue(repaired.get("fallback_applied"))
        self.assertEqual(repaired.get("original_query"), malformed)
        rows = repaired.get("rows", [])
        self.assertTrue(rows)
        row = rows[0]
        self.assertEqual(row.get("JanPlace"), "morro_bay_california")
        self.assertEqual(row.get("WillPlace"), "san_francisco")

    def test_query_loop_guard_blocks_repeated_no_result_churn(self) -> None:
        packet = self.server.tools_call("pre_think", {"utterance": "Who is my?"})
        self.assertEqual(packet.get("status"), "success")
        prethink_id = packet.get("packet", {}).get("prethink_id")
        self.assertTrue(prethink_id)

        first = self.server.tools_call(
            "query_rows",
            {"query": "user_intent(X).", "prethink_id": prethink_id},
        )
        self.assertEqual(first.get("status"), "no_results")

        second = self.server.tools_call(
            "query_rows",
            {"query": "user_intent(X).", "prethink_id": prethink_id},
        )
        self.assertEqual(second.get("status"), "no_results")

        blocked = self.server.tools_call(
            "query_rows",
            {"query": "user_intent(X).", "prethink_id": prethink_id},
        )
        self.assertEqual(blocked.get("status"), "blocked")
        self.assertEqual(blocked.get("result_type"), "query_loop_guard")

    def test_unknown_tool_returns_not_found(self) -> None:
        result = self.server.tools_call("not_a_tool", {})
        self.assertEqual(result.get("status"), "not_found")

    def test_strict_compiler_mode_blocks_without_compiler_prompt(self) -> None:
        missing = Path("tmp") / "does_not_exist_semparse_prompt.md"
        strict_server = PrologMCPServer(
            compiler_mode="strict",
            compiler_prompt_file=str(missing),
        )
        packet = strict_server.tools_call("pre_think", {"utterance": "Alice is Bob's parent."})
        self.assertEqual(packet.get("status"), "blocked")
        self.assertEqual(packet.get("result_type"), "compiler_failed")
        trace = packet.get("trace", {})
        self.assertIsInstance(trace, dict)
        self.assertEqual(trace.get("summary", {}).get("source"), "failed")

    def test_sanitize_compiler_clarification_suppresses_family_drift_when_shadow_parse_is_clean(self) -> None:
        strict_server = PrologMCPServer(compiler_mode="strict")
        compiled = {
            "intent": "assert_fact",
            "needs_clarification": True,
            "uncertainty_score": 0.75,
            "clarification_question": "Who are the parents of Barney and Betty?",
            "clarification_reason": "Ambiguous live next door lacks explicit parent relation.",
            "rationale": "Compiler drifted toward a family interpretation.",
        }
        shadow_parse = {
            "intent": "assert_fact",
            "logic_string": (
                "next_door(barney, fred).\n"
                "next_door(barney, wilma).\n"
                "next_door(betty, fred).\n"
                "next_door(betty, wilma)."
            ),
            "components": {
                "atoms": ["barney", "betty", "fred", "wilma"],
                "variables": [],
                "predicates": ["next_door"],
            },
            "facts": [
                "next_door(barney, fred).",
                "next_door(barney, wilma).",
                "next_door(betty, fred).",
                "next_door(betty, wilma).",
            ],
            "rules": [],
            "queries": [],
            "confidence": {"overall": 0.95, "intent": 0.95, "logic": 0.95},
            "ambiguities": [],
            "needs_clarification": False,
            "uncertainty_score": 0.15,
            "uncertainty_label": "low",
            "clarification_question": "",
            "clarification_reason": "",
            "rationale": "Shadow parse recognized a neighbor relation cleanly.",
        }

        with patch.object(strict_server, "_compile_shadow_parse", return_value=(shadow_parse, "")):
            sanitized = strict_server._sanitize_compiler_clarification(
                utterance="barney and betty live next door to fred and wilma",
                compiled=compiled,
            )

        self.assertFalse(sanitized.get("needs_clarification"))
        self.assertEqual(sanitized.get("clarification_question"), "")
        self.assertEqual(sanitized.get("clarification_reason"), "")
        self.assertEqual(sanitized.get("uncertainty_score"), 0.15)

    def test_sanitize_compiler_clarification_suppresses_explicit_family_bundle_when_shadow_parse_is_clean(self) -> None:
        strict_server = PrologMCPServer(compiler_mode="strict")
        compiled = {
            "intent": "assert_fact",
            "needs_clarification": True,
            "uncertainty_score": 0.75,
            "clarification_question": (
                "Who are Scott's parents? Ann and Ian, or is one of them Scott's parent "
                "and the other someone else's?"
            ),
            "clarification_reason": "Ambiguous pronoun 'Scott's' and unclear if both are parents or one is",
            "rationale": "Compiler over-questioned an explicit family bundle.",
        }
        shadow_parse = {
            "intent": "assert_fact",
            "logic_string": "parent(ann, scott). parent(ian, scott).",
            "components": {
                "atoms": ["ann", "ian", "scott"],
                "variables": [],
                "predicates": ["parent"],
            },
            "facts": [
                "parent(ann, scott).",
                "parent(ian, scott).",
            ],
            "rules": [],
            "queries": [],
            "confidence": {"overall": 0.95, "intent": 0.95, "logic": 0.95},
            "ambiguities": [],
            "needs_clarification": False,
            "uncertainty_score": 0.05,
            "uncertainty_label": "low",
            "clarification_question": "",
            "clarification_reason": "",
            "rationale": "Shadow parse recognized the explicit parent bundle cleanly.",
        }

        with patch.object(strict_server, "_compile_shadow_parse", return_value=(shadow_parse, "")):
            sanitized = strict_server._sanitize_compiler_clarification(
                utterance="scotts mom and dad are ann and ian",
                compiled=compiled,
            )

        self.assertFalse(sanitized.get("needs_clarification"))
        self.assertEqual(sanitized.get("clarification_question"), "")
        self.assertEqual(sanitized.get("clarification_reason"), "")
        self.assertEqual(sanitized.get("uncertainty_score"), 0.05)

    def test_sanitize_compiler_clarification_suppresses_explicit_family_bundle_is_variant(self) -> None:
        strict_server = PrologMCPServer(compiler_mode="strict")
        compiled = {
            "intent": "assert_fact",
            "needs_clarification": True,
            "uncertainty_score": 0.75,
            "clarification_question": (
                "Who are Scott's parents? Is it Ann and Ian, or is one of them Scott's parent "
                "and the other someone else's parent?"
            ),
            "clarification_reason": "Ambiguous pronoun 'his' and unclear if both are parents of Scott or",
            "rationale": "Compiler over-questioned an explicit family bundle with singular agreement.",
        }
        shadow_parse = {
            "intent": "assert_fact",
            "logic_string": "parent(ann, scotts_mom). parent(ian, scotts_mom).",
            "components": {
                "atoms": ["ann", "ian", "scotts_mom"],
                "variables": [],
                "predicates": ["parent"],
            },
            "facts": [
                "parent(ann, scotts_mom).",
                "parent(ian, scotts_mom).",
            ],
            "rules": [],
            "queries": [],
            "confidence": {"overall": 0.95, "intent": 0.95, "logic": 0.95},
            "ambiguities": [],
            "needs_clarification": False,
            "uncertainty_score": 0.15,
            "uncertainty_label": "low",
            "clarification_question": "",
            "clarification_reason": "",
            "rationale": "Shadow parse can be rough here, but clarification should still be suppressed.",
        }

        with patch.object(strict_server, "_compile_shadow_parse", return_value=(shadow_parse, "")):
            sanitized = strict_server._sanitize_compiler_clarification(
                utterance="scotts mom and dad is ann and ian.",
                compiled=compiled,
            )

        self.assertFalse(sanitized.get("needs_clarification"))
        self.assertEqual(sanitized.get("clarification_question"), "")
        self.assertEqual(sanitized.get("clarification_reason"), "")
        self.assertEqual(sanitized.get("uncertainty_score"), 0.15)

    def test_sanitize_compiler_clarification_suppresses_internal_predicate_mapping_when_shadow_parse_is_clean(self) -> None:
        strict_server = PrologMCPServer(compiler_mode="strict")
        compiled = {
            "intent": "assert_fact",
            "needs_clarification": True,
            "uncertainty_score": 0.75,
            "clarification_question": (
                "What is the intended Prolog predicate for 'entered the pinky penny supermarket' "
                "and 'headed over to the turnips'?"
            ),
            "clarification_reason": "Ambiguous action verbs and location references require canonical predicate mapping.",
            "rationale": "Compiler asked for internal predicate mapping.",
        }
        shadow_parse = {
            "intent": "assert_fact",
            "logic_string": (
                "entered(fred, pinky_penny_supermarket, 9am, friday_morning).\n"
                "entered(wilma, pinky_penny_supermarket, 9am, friday_morning).\n"
                "heading_over(fred, turnips, pinky_penny_supermarket).\n"
                "heading_over(wilma, turnips, pinky_penny_supermarket)."
            ),
            "components": {
                "atoms": ["fred", "wilma", "pinky_penny_supermarket", "turnips", "9am", "friday_morning"],
                "variables": [],
                "predicates": ["entered", "heading_over"],
            },
            "facts": [
                "entered(fred, pinky_penny_supermarket, 9am, friday_morning).",
                "entered(wilma, pinky_penny_supermarket, 9am, friday_morning).",
                "heading_over(fred, turnips, pinky_penny_supermarket).",
                "heading_over(wilma, turnips, pinky_penny_supermarket).",
            ],
            "rules": [],
            "queries": [],
            "confidence": {"overall": 0.95, "intent": 0.95, "logic": 0.95},
            "ambiguities": ["Direction of 'heading over' (implicit movement towards turnips)."],
            "needs_clarification": False,
            "uncertainty_score": 0.15,
            "uncertainty_label": "low",
            "clarification_question": "",
            "clarification_reason": "",
            "rationale": "Shadow parse recognized a stable action/location interpretation.",
        }

        with patch.object(strict_server, "_compile_shadow_parse", return_value=(shadow_parse, "")):
            sanitized = strict_server._sanitize_compiler_clarification(
                utterance=(
                    "at 9am on friday morning fred and wilma entered the pinky penny supermarket "
                    "and headed over to the turnips"
                ),
                compiled=compiled,
            )

        self.assertFalse(sanitized.get("needs_clarification"))
        self.assertEqual(sanitized.get("clarification_question"), "")
        self.assertEqual(sanitized.get("clarification_reason"), "")
        self.assertEqual(sanitized.get("uncertainty_score"), 0.15)

    def test_sanitize_compiler_clarification_suppresses_generic_event_fact_request_when_shadow_parse_is_clean(self) -> None:
        strict_server = PrologMCPServer(compiler_mode="strict")
        compiled = {
            "intent": "assert_fact",
            "needs_clarification": True,
            "uncertainty_score": 0.75,
            "clarification_question": "What specific facts about Fred, Wilma, or the turnips should be asserted?",
            "clarification_reason": "Utterance describes an event but lacks explicit predicates or facts to assert.",
            "rationale": "Event description requires clarification on intended ontology predicates.",
        }
        shadow_parse = {
            "intent": "assert_fact",
            "logic_string": (
                "entered(fred, pinky_penny_supermarket, 9am, friday_morning).\n"
                "entered(wilma, pinky_penny_supermarket, 9am, friday_morning).\n"
                "headed_over(fred, turnips, pinky_penny_supermarket).\n"
                "headed_over(wilma, turnips, pinky_penny_supermarket)."
            ),
            "components": {
                "atoms": ["fred", "wilma", "pinky_penny_supermarket", "turnips", "9am", "friday_morning"],
                "variables": [],
                "predicates": ["entered", "headed_over"],
            },
            "facts": [
                "entered(fred, pinky_penny_supermarket, 9am, friday_morning).",
                "entered(wilma, pinky_penny_supermarket, 9am, friday_morning).",
                "headed_over(fred, turnips, pinky_penny_supermarket).",
                "headed_over(wilma, turnips, pinky_penny_supermarket).",
            ],
            "rules": [],
            "queries": [],
            "confidence": {"overall": 0.95, "intent": 0.95, "logic": 0.95},
            "ambiguities": ["Canonical predicate names for the event verbs are not yet fixed in the ontology."],
            "needs_clarification": False,
            "uncertainty_score": 0.15,
            "uncertainty_label": "low",
            "clarification_question": "",
            "clarification_reason": "",
            "rationale": "Shadow parse recognized a stable action/location interpretation.",
        }

        with patch.object(strict_server, "_compile_shadow_parse", return_value=(shadow_parse, "")):
            sanitized = strict_server._sanitize_compiler_clarification(
                utterance=(
                    "at 9am on friday morning fred and wilma entered the pinky penny supermarket "
                    "and headed over to the turnips"
                ),
                compiled=compiled,
            )

        self.assertFalse(sanitized.get("needs_clarification"))
        self.assertEqual(sanitized.get("clarification_question"), "")
        self.assertEqual(sanitized.get("clarification_reason"), "")
        self.assertEqual(sanitized.get("uncertainty_score"), 0.15)

    def test_sanitize_compiler_clarification_suppresses_explicit_sibling_naming_when_shadow_parse_is_clean(self) -> None:
        strict_server = PrologMCPServer(compiler_mode="strict")
        compiled = {
            "intent": "assert_fact",
            "needs_clarification": True,
            "uncertainty_score": 0.75,
            "clarification_question": "Who is 'his' referring to, and is 'brother' a sibling relationship or a specific role?",
            "clarification_reason": "Unresolved pronoun 'his' and ambiguous 'brother' role.",
            "rationale": "Compiler over-questioned an explicit sibling naming statement.",
        }
        shadow_parse = {
            "intent": "assert_fact",
            "logic_string": "brother(scott, blake).\nbrother(blake, scott).",
            "components": {
                "atoms": ["scott", "blake"],
                "variables": [],
                "predicates": ["brother"],
            },
            "facts": [
                "brother(scott, blake).",
                "brother(blake, scott).",
            ],
            "rules": [],
            "queries": [],
            "confidence": {"overall": 0.95, "intent": 0.95, "logic": 0.95},
            "ambiguities": ["Interpretation of 'brothers name' as a specific entity."],
            "needs_clarification": False,
            "uncertainty_score": 0.15,
            "uncertainty_label": "low",
            "clarification_question": "",
            "clarification_reason": "",
            "rationale": "Shadow parse recognized the explicit sibling naming statement cleanly.",
        }

        with patch.object(strict_server, "_compile_shadow_parse", return_value=(shadow_parse, "")):
            sanitized = strict_server._sanitize_compiler_clarification(
                utterance="scott has a brother and his brothers name is blake",
                compiled=compiled,
            )

        self.assertFalse(sanitized.get("needs_clarification"))
        self.assertEqual(sanitized.get("clarification_question"), "")
        self.assertEqual(sanitized.get("clarification_reason"), "")
        self.assertEqual(sanitized.get("uncertainty_score"), 0.15)

    def test_rescue_explicit_with_correction_reuses_positive_shadow_parses(self) -> None:
        strict_server = PrologMCPServer(compiler_mode="strict")
        parsed = {
            "intent": "assert_fact",
            "logic_string": "retract(cart_with_fred).",
            "components": {
                "atoms": ["cart_with_fred"],
                "variables": [],
                "predicates": ["retract"],
            },
            "facts": ["retract(cart_with_fred)."],
            "rules": [],
            "queries": [],
            "confidence": {"overall": 0.9, "intent": 0.9, "logic": 0.9},
            "ambiguities": [],
            "needs_clarification": False,
            "uncertainty_score": 0.35,
            "uncertainty_label": "medium",
            "clarification_question": "",
            "clarification_reason": "",
            "rationale": "Temporary parser rationale.",
        }
        new_parse = {
            "intent": "assert_fact",
            "logic_string": "cart_with(fred, cart).",
            "components": {
                "atoms": ["fred", "cart"],
                "variables": [],
                "predicates": ["cart_with"],
            },
            "facts": ["cart_with(fred, cart)."],
            "rules": [],
            "queries": [],
            "confidence": {"overall": 0.95, "intent": 0.95, "logic": 0.95},
            "ambiguities": [],
            "needs_clarification": False,
            "uncertainty_score": 0.05,
            "uncertainty_label": "low",
            "clarification_question": "",
            "clarification_reason": "",
            "rationale": "Positive assert parse for Fred.",
        }
        old_parse = {
            "intent": "assert_fact",
            "logic_string": "cart_with(mara, cart).",
            "components": {
                "atoms": ["mara", "cart"],
                "variables": [],
                "predicates": ["cart_with"],
            },
            "facts": ["cart_with(mara, cart)."],
            "rules": [],
            "queries": [],
            "confidence": {"overall": 0.95, "intent": 0.95, "logic": 0.95},
            "ambiguities": [],
            "needs_clarification": False,
            "uncertainty_score": 0.05,
            "uncertainty_label": "low",
            "clarification_question": "",
            "clarification_reason": "",
            "rationale": "Positive assert parse for Mara.",
        }

        with patch.object(
            strict_server,
            "_compile_shadow_parse",
            side_effect=[(new_parse, ""), (old_parse, "")],
        ):
            rescued = strict_server._rescue_explicit_with_correction(
                parsed=parsed,
                utterance="actually no, cart is with Fred not Mara",
                compiler_intent="assert_fact",
            )

        self.assertEqual(rescued.get("facts"), ["cart_with(fred, cart)."])
        self.assertEqual(
            rescued.get("correction_retract_clauses"),
            ["cart_with(mara, cart)."],
        )
        self.assertEqual(rescued.get("uncertainty_score"), 0.05)
        self.assertFalse(rescued.get("needs_clarification"))

    def test_sanitize_compiler_clarification_normalizes_explicit_with_correction(self) -> None:
        strict_server = PrologMCPServer(compiler_mode="strict")
        compiled = {
            "intent": "retract",
            "needs_clarification": True,
            "uncertainty_score": 0.85,
            "clarification_question": "Which fact should be retracted?",
            "clarification_reason": "Correction may refer to either entity.",
            "rationale": "Compiler treated the utterance as a retraction.",
        }

        sanitized = strict_server._sanitize_compiler_clarification(
            utterance="actually no, cart is with Fred not Mara",
            compiled=compiled,
        )

        self.assertEqual(sanitized.get("intent"), "assert_fact")
        self.assertFalse(sanitized.get("needs_clarification"))
        self.assertEqual(sanitized.get("clarification_question"), "")
        self.assertEqual(sanitized.get("clarification_reason"), "")
        self.assertEqual(sanitized.get("uncertainty_score"), 0.15)

    def test_sanitize_compiler_clarification_normalizes_explicit_step_sequence(self) -> None:
        strict_server = PrologMCPServer(compiler_mode="strict")
        compiled = {
            "intent": "assert_fact",
            "needs_clarification": True,
            "uncertainty_score": 0.85,
            "clarification_question": "What is the predicate name for 'was in' and 'moved to'?",
            "clarification_reason": "Missing canonical predicate names for location and movement events.",
            "rationale": "Utterance describes location change but lacks explicit predicate definitions.",
        }

        sanitized = strict_server._sanitize_compiler_clarification(
            utterance="at step 11 Fred was in Salem and later moved to Harbor City",
            compiled=compiled,
        )

        self.assertEqual(sanitized.get("intent"), "assert_fact")
        self.assertFalse(sanitized.get("needs_clarification"))
        self.assertEqual(sanitized.get("clarification_question"), "")
        self.assertEqual(sanitized.get("clarification_reason"), "")
        self.assertEqual(sanitized.get("uncertainty_score"), 0.15)

    def test_extract_explicit_step_sequence_accepts_digit_bearing_locations(self) -> None:
        strict_server = PrologMCPServer(compiler_mode="strict")

        extracted = strict_server._extract_explicit_step_sequence(
            "at step 6 Noor was in Bay 3 and later moved to Mudroom."
        )

        self.assertEqual(
            extracted,
            {
                "step": 6,
                "entity_atom": "noor",
                "origin_atom": "bay_3",
                "destination_atom": "mudroom",
            },
        )

    def test_rescue_explicit_step_sequence_rewrites_invalid_step_predicates(self) -> None:
        strict_server = PrologMCPServer(compiler_mode="strict")
        parsed = {
            "intent": "assert_fact",
            "logic_string": "at_step_11(Noor, Galley). at_step_12(Noor, Cedar_House).",
            "components": {
                "atoms": ["Noor", "Galley", "Cedar_House"],
                "variables": [],
                "predicates": ["at_step_11", "at_step_12"],
            },
            "facts": [
                "at_step_11(Noor, Galley).",
                "at_step_12(Noor, Cedar_House).",
            ],
            "rules": [],
            "queries": [],
            "confidence": {"overall": 0.95, "intent": 0.95, "logic": 0.95},
            "ambiguities": [],
            "needs_clarification": False,
            "uncertainty_score": 0.1,
            "uncertainty_label": "low",
            "clarification_question": "",
            "clarification_reason": "",
            "rationale": "Temporary parser rationale.",
        }

        rescued = strict_server._rescue_explicit_step_sequence(
            parsed=parsed,
            utterance="at step 11 Noor was in Galley and later moved to Cedar House.",
            compiler_intent="assert_fact",
        )

        self.assertEqual(
            rescued.get("facts"),
            [
                "at_step(11, at(noor, galley)).",
                "at_step(12, at(noor, cedar_house)).",
            ],
        )
        self.assertFalse(rescued.get("needs_clarification"))
        self.assertEqual(rescued.get("uncertainty_score"), 0.1)

    def test_apply_compiled_parse_handles_explicit_with_correction_as_state_replacement(self) -> None:
        server = PrologMCPServer(compiler_mode="heuristic")
        initial = server.assert_fact("cart_with(mara, cart).")
        self.assertEqual(initial.get("status"), "success")
        packet = server.tools_call("pre_think", {"utterance": "cart is with Fred"})
        self.assertEqual(packet.get("status"), "success")
        prethink_id = packet.get("packet", {}).get("prethink_id")
        self.assertTrue(prethink_id)

        parsed = {
            "intent": "assert_fact",
            "logic_string": "cart_with(fred, cart).",
            "components": {
                "atoms": ["fred", "cart", "mara"],
                "variables": [],
                "predicates": ["cart_with"],
            },
            "facts": ["cart_with(fred, cart)."],
            "rules": [],
            "queries": [],
            "confidence": {"overall": 0.95, "intent": 0.95, "logic": 0.95},
            "ambiguities": [],
            "needs_clarification": False,
            "uncertainty_score": 0.05,
            "uncertainty_label": "low",
            "clarification_question": "",
            "clarification_reason": "",
            "rationale": "Recovered explicit correction.",
            "correction_retract_clauses": ["cart_with(mara, cart)."],
        }

        execution = server._apply_compiled_parse(parsed=parsed, prethink_id=prethink_id)

        self.assertEqual(execution.get("status"), "success")
        operations = execution.get("operations", [])
        self.assertEqual([op.get("tool") for op in operations[:2]], ["retract_fact", "assert_fact"])
        query = server.query_rows("cart_with(X, cart).")
        self.assertEqual(query.get("status"), "success")
        rows = query.get("rows", [])
        self.assertEqual({row.get("X") for row in rows}, {"fred"})

    def test_apply_compiled_parse_executes_mixed_rule_fact_and_query_bundle(self) -> None:
        server = PrologMCPServer(compiler_mode="heuristic")
        packet = server.tools_call(
            "pre_think",
            {"utterance": "If Alice is a parent of Bob then Alice is an ancestor of Bob."},
        )
        self.assertEqual(packet.get("status"), "success")
        prethink_id = packet.get("packet", {}).get("prethink_id")
        self.assertTrue(prethink_id)

        parsed = {
            "intent": "assert_rule",
            "logic_string": "ancestor(X, Y) :- parent(X, Y).",
            "components": {
                "atoms": ["alice", "bob"],
                "variables": ["X", "Y"],
                "predicates": ["parent", "ancestor"],
            },
            "facts": ["parent(alice, bob)."],
            "rules": ["ancestor(X, Y) :- parent(X, Y)."],
            "queries": ["ancestor(alice, bob)."],
            "confidence": {"overall": 0.95, "intent": 0.95, "logic": 0.95},
            "ambiguities": [],
            "needs_clarification": False,
            "uncertainty_score": 0.05,
            "uncertainty_label": "low",
            "clarification_question": "",
            "clarification_reason": "",
            "rationale": "Parsed mixed write/query bundle.",
        }

        execution = server._apply_compiled_parse(parsed=parsed, prethink_id=prethink_id)

        self.assertEqual(execution.get("status"), "success")
        self.assertEqual(execution.get("writes_applied"), 2)
        operations = execution.get("operations", [])
        self.assertEqual(
            [op.get("tool") for op in operations],
            ["assert_fact", "assert_rule", "query_rows"],
        )
        query_result = execution.get("query_result", {})
        self.assertEqual(query_result.get("status"), "success")
        self.assertEqual(query_result.get("num_rows"), 1)

    def test_process_utterance_rescues_clarified_medical_lab_result_in_canonical_path(self) -> None:
        strict_server = PrologMCPServer(compiler_mode="strict", active_profile="medical@v0")
        strict_server._pending_prethink = {
            "prethink_id": "pt-medical",
            "utterance": "Mara's pressure is bad lately.",
            "compiler_intent": "query",
            "compiler_uncertainty_score": 0.85,
            "clarification_required_before_query": True,
            "clarification_question": "Which specific lab test is bad for Mara?",
            "clarification_reason": "vague_medical_surface",
            "compiler_trace": {},
        }
        parsed = {
            "intent": "query",
            "logic_string": "",
            "components": {"atoms": [], "variables": [], "predicates": []},
            "facts": [],
            "rules": [],
            "queries": [],
            "confidence": {"overall": 0.5, "intent": 0.5, "logic": 0.5},
            "ambiguities": [],
            "needs_clarification": False,
            "uncertainty_score": 0.5,
            "uncertainty_label": "medium",
            "clarification_question": "",
            "clarification_reason": "",
            "rationale": "Extractor left the clarified lab result empty.",
        }

        with patch(
            "src.mcp_server._call_model_prompt",
            return_value=ModelResponse(message=json.dumps(parsed), reasoning="", raw={}),
        ):
            result = strict_server.process_utterance(
                {
                    "utterance": "Mara's pressure is bad lately.",
                    "clarification_answer": "Mara's blood pressure reading was high.",
                    "prethink_id": "pt-medical",
                }
            )

        self.assertEqual(result.get("status"), "success")
        execution = result.get("execution") or {}
        self.assertEqual(execution.get("intent"), "assert_fact")
        self.assertEqual(execution.get("writes_applied"), 1)
        self.assertEqual(
            execution.get("parse", {}).get("facts"),
            ["lab_result_high(mara, blood_pressure_measurement)."],
        )
        operations = execution.get("operations") or []
        self.assertEqual(operations[0].get("clause"), "lab_result_high(mara, blood_pressure_measurement).")
        trace = result.get("compiler_trace", {})
        self.assertIn(
            "medical_clarified_lab_result_rescue",
            trace.get("summary", {}).get("parse_rescues", []),
        )

    def test_process_utterance_holds_vague_medical_surface_before_extraction(self) -> None:
        strict_server = PrologMCPServer(compiler_mode="strict", active_profile="medical@v0")
        compiled = {
            "intent": "query",
            "needs_clarification": False,
            "uncertainty_score": 0.1,
            "clarification_question": "",
            "clarification_reason": "",
            "rationale": "Model treated the statement as a query.",
        }

        with patch(
            "src.mcp_server._call_model_prompt",
            return_value=ModelResponse(message=json.dumps(compiled), reasoning="", raw={}),
        ) as call_model:
            result = strict_server.process_utterance(
                {"utterance": "Mara's pressure is bad lately."}
            )

        self.assertEqual(result.get("status"), "clarification_required")
        front_door = result.get("front_door") or {}
        self.assertEqual(front_door.get("route"), "write")
        self.assertEqual(front_door.get("compiler_intent"), "assert_fact")
        self.assertTrue(front_door.get("needs_clarification"))
        question = str(front_door.get("clarification_question", ""))
        self.assertIn("pressure", question)
        self.assertIn("Mara", question)
        self.assertIn("blood pressure", question)
        self.assertEqual(call_model.call_count, 1)


def test_normalize_clarification_answer_maps_possessive_owner_choice_to_owner_name():
    server = PrologMCPServer()

    normalized = server._normalize_clarification_answer(
        clarification_question="Do you mean Scott's brother or Priya's brother when you say 'his brother'?",
        clarification_answer="scotts",
    )

    assert normalized == "Scott"
