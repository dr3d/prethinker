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

    def test_compile_prethink_semantics_falls_back_to_compact_classifier_on_invalid_primary_output(self) -> None:
        strict_server = PrologMCPServer(compiler_mode="strict")
        responses = [
            ModelResponse(message='{"intent":"assert_fact"', reasoning="", raw={}),
            ModelResponse(
                message=json.dumps(
                    {
                        "route": "assert_fact",
                        "needs_clarification": False,
                        "ambiguity_risk": "low",
                        "reason": "Declarative composition statement.",
                    }
                ),
                reasoning="",
                raw={},
            ),
        ]

        with patch("src.mcp_server._call_model_prompt", side_effect=responses):
            compiled, error = strict_server._compile_prethink_semantics(
                "muffins are made with cranberries and raisins or walnuts"
            )

        self.assertEqual(error, "")
        self.assertIsInstance(compiled, dict)
        self.assertEqual(compiled.get("intent"), "assert_fact")
        self.assertFalse(compiled.get("needs_clarification"))
        self.assertEqual(compiled.get("clarification_question"), "")

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

    def test_process_utterance_uses_canonical_registry_form_for_subject_prefixed_predicate(self) -> None:
        strict_server = PrologMCPServer(compiler_mode="strict")
        compiled = {
            "intent": "assert_fact",
            "needs_clarification": False,
            "uncertainty_score": 0.05,
            "clarification_question": "",
            "clarification_reason": "",
            "rationale": "Write-like utterance.",
        }
        parsed = {
            "intent": "assert_fact",
            "logic_string": "hope_lives_in(hope, salem).",
            "components": {
                "atoms": ["hope", "salem"],
                "variables": [],
                "predicates": ["hope_lives_in"],
            },
            "facts": ["hope_lives_in(hope, salem)."],
            "rules": [],
            "queries": [],
            "confidence": {"overall": 0.95, "intent": 0.95, "logic": 0.95},
            "ambiguities": [],
            "needs_clarification": False,
            "uncertainty_score": 0.05,
            "uncertainty_label": "low",
            "clarification_question": "",
            "clarification_reason": "",
            "rationale": "Temporary parser rationale.",
        }

        with (
            patch.object(strict_server, "_compile_prethink_semantics", return_value=(compiled, "")),
            patch(
                "src.mcp_server._call_model_prompt",
                return_value=ModelResponse(message=json.dumps(parsed), reasoning="", raw={}),
            ),
        ):
            result = strict_server.process_utterance({"utterance": "hope lives in salem"})

        self.assertEqual(result.get("status"), "success")
        trace = result.get("compiler_trace", {})
        self.assertIsInstance(trace.get("prethink"), dict)
        self.assertIn(
            "subject_prefixed_predicate_canonicalization",
            trace.get("summary", {}).get("parse_rescues", []),
        )
        execution = result.get("execution", {})
        self.assertEqual(execution.get("status"), "success")
        self.assertEqual(
            execution.get("parse", {}).get("facts"),
            ["lives_in(hope, salem)."],
        )
        query = strict_server.query_rows("lives_in(hope, X).")
        self.assertEqual(query.get("status"), "success")
        self.assertTrue(any(row.get("X") == "salem" for row in query.get("rows", [])))

    def test_process_utterance_normalizes_family_bundle_in_canonical_path(self) -> None:
        strict_server = PrologMCPServer(compiler_mode="strict")
        compiled = {
            "intent": "assert_fact",
            "needs_clarification": False,
            "uncertainty_score": 0.05,
            "clarification_question": "",
            "clarification_reason": "",
            "rationale": "Write-like utterance.",
        }
        parsed = {
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
            "uncertainty_score": 0.05,
            "uncertainty_label": "low",
            "clarification_question": "",
            "clarification_reason": "",
            "rationale": "Temporary parser rationale.",
        }

        with (
            patch.object(strict_server, "_compile_prethink_semantics", return_value=(compiled, "")),
            patch(
                "src.mcp_server._call_model_prompt",
                return_value=ModelResponse(message=json.dumps(parsed), reasoning="", raw={}),
            ),
        ):
            result = strict_server.process_utterance({"utterance": "scotts mom and dad is ann and ian."})

        self.assertEqual(result.get("status"), "success")
        trace = result.get("compiler_trace", {})
        self.assertIn(
            "compound_family_augmentation",
            trace.get("summary", {}).get("parse_rescues", []),
        )
        execution = result.get("execution", {})
        self.assertEqual(
            execution.get("parse", {}).get("facts"),
            ["parent(ann, scott).", "parent(ian, scott)."],
        )
        query = strict_server.query_rows("parent(X, scott).")
        self.assertEqual(query.get("status"), "success")
        parents = {row.get("X") for row in query.get("rows", [])}
        self.assertEqual(parents, {"ann", "ian"})

    def test_process_utterance_normalizes_explicit_sibling_name_in_canonical_path(self) -> None:
        strict_server = PrologMCPServer(compiler_mode="strict")
        compiled = {
            "intent": "assert_fact",
            "needs_clarification": False,
            "uncertainty_score": 0.05,
            "clarification_question": "",
            "clarification_reason": "",
            "rationale": "Write-like utterance.",
        }
        parsed = {
            "intent": "assert_fact",
            "logic_string": "brother(scott, blake). brother(blake, scott).",
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
            "ambiguities": [],
            "needs_clarification": False,
            "uncertainty_score": 0.05,
            "uncertainty_label": "low",
            "clarification_question": "",
            "clarification_reason": "",
            "rationale": "Temporary parser rationale.",
        }

        with (
            patch.object(strict_server, "_compile_prethink_semantics", return_value=(compiled, "")),
            patch(
                "src.mcp_server._call_model_prompt",
                return_value=ModelResponse(message=json.dumps(parsed), reasoning="", raw={}),
            ),
        ):
            result = strict_server.process_utterance(
                {"utterance": "scott has a brother and his brothers name is blake"}
            )

        self.assertEqual(result.get("status"), "success")
        execution = result.get("execution", {})
        self.assertEqual(
            execution.get("parse", {}).get("facts"),
            ["brother(blake, scott)."],
        )
        query = strict_server.query_rows("brother(X, scott).")
        self.assertEqual(query.get("status"), "success")
        self.assertEqual({row.get("X") for row in query.get("rows", [])}, {"blake"})

    def test_process_utterance_maps_can_you_make_with_query_to_made_with_relation(self) -> None:
        strict_server = PrologMCPServer(compiler_mode="strict")
        compiled_write = {
            "intent": "assert_fact",
            "needs_clarification": False,
            "uncertainty_score": 0.05,
            "clarification_question": "",
            "clarification_reason": "",
            "rationale": "Write-like utterance.",
        }
        parsed_write = {
            "intent": "assert_fact",
            "logic_string": "made_with(muffins, cranberries). made_with(muffins, raisins). made_with(muffins, walnuts).",
            "components": {
                "atoms": ["muffins", "cranberries", "raisins", "walnuts"],
                "variables": [],
                "predicates": ["made_with"],
            },
            "facts": [
                "made_with(muffins, cranberries).",
                "made_with(muffins, raisins).",
                "made_with(muffins, walnuts).",
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
            "rationale": "Temporary parser rationale.",
        }
        compiled_query = {
            "intent": "query",
            "needs_clarification": False,
            "uncertainty_score": 0.05,
            "clarification_question": "",
            "clarification_reason": "",
            "rationale": "Query-like utterance.",
        }
        parsed_query = {
            "intent": "query",
            "logic_string": "can_make_muffins_with_walnuts(user).",
            "components": {
                "atoms": ["can_make_muffins_with_walnuts", "user"],
                "variables": [],
                "predicates": ["can_make_muffins_with_walnuts"],
            },
            "facts": [],
            "rules": [],
            "queries": ["can_make_muffins_with_walnuts(user)."],
            "confidence": {"overall": 0.95, "intent": 0.95, "logic": 0.95},
            "ambiguities": [],
            "needs_clarification": False,
            "uncertainty_score": 0.05,
            "uncertainty_label": "low",
            "clarification_question": "",
            "clarification_reason": "",
            "rationale": "Temporary parser rationale.",
        }

        with (
            patch.object(
                strict_server,
                "_compile_prethink_semantics",
                side_effect=[(compiled_write, ""), (compiled_query, "")],
            ),
            patch(
                "src.mcp_server._call_model_prompt",
                side_effect=[
                    ModelResponse(message=json.dumps(parsed_write), reasoning="", raw={}),
                    ModelResponse(message=json.dumps(parsed_query), reasoning="", raw={}),
                ],
            ),
        ):
            write_result = strict_server.process_utterance(
                {"utterance": "muffins are made with cranberries or raisins or walnuts"}
            )
            query_result = strict_server.process_utterance(
                {"utterance": "can you make muffins with walnuts?"}
            )

        self.assertEqual(write_result.get("status"), "success")
        self.assertEqual(query_result.get("status"), "success")
        trace = query_result.get("compiler_trace", {})
        self.assertIn(
            "make_with_query_canonicalization",
            trace.get("summary", {}).get("parse_rescues", []),
        )
        execution = query_result.get("execution", {})
        self.assertEqual(
            execution.get("parse", {}).get("queries"),
            ["made_with(muffins, walnuts)."],
        )
        query_payload = execution.get("query_result", {})
        self.assertEqual(query_payload.get("status"), "success")

    def test_process_utterance_traces_freethinker_as_off_by_default(self) -> None:
        strict_server = PrologMCPServer(compiler_mode="strict")
        compiled = {
            "intent": "assert_fact",
            "needs_clarification": True,
            "uncertainty_score": 0.8,
            "clarification_question": "Who does 'he' refer to?",
            "clarification_reason": "Unresolved pronoun.",
            "rationale": "Write-like utterance blocked on reference.",
        }

        with patch.object(strict_server, "_compile_prethink_semantics", return_value=(compiled, "")):
            result = strict_server.process_utterance({"utterance": "He lives in Salem."})

        self.assertEqual(result.get("status"), "clarification_required")
        trace = result.get("compiler_trace", {})
        freethinker = trace.get("freethinker", {})
        self.assertEqual(freethinker.get("policy"), "off")
        self.assertFalse(freethinker.get("used"))
        self.assertEqual(freethinker.get("action"), "skipped")
        self.assertEqual(trace.get("summary", {}).get("freethinker_policy"), "off")

    def test_process_utterance_records_queued_freethinker_when_policy_enabled(self) -> None:
        strict_server = PrologMCPServer(
            compiler_mode="strict",
            freethinker_resolution_policy="grounded_reference",
        )
        compiled = {
            "intent": "assert_fact",
            "needs_clarification": True,
            "uncertainty_score": 0.8,
            "clarification_question": "Who does 'he' refer to?",
            "clarification_reason": "Unresolved pronoun.",
            "rationale": "Write-like utterance blocked on reference.",
        }

        with patch.object(strict_server, "_compile_prethink_semantics", return_value=(compiled, "")):
            result = strict_server.process_utterance({"utterance": "He lives in Salem."})

        self.assertEqual(result.get("status"), "clarification_required")
        trace = result.get("compiler_trace", {})
        freethinker = trace.get("freethinker", {})
        self.assertEqual(freethinker.get("policy"), "grounded_reference")
        self.assertFalse(freethinker.get("used"))
        self.assertEqual(freethinker.get("action"), "queued")
        self.assertEqual(freethinker.get("reason"), "not_implemented_yet")


if __name__ == "__main__":
    unittest.main()
