import unittest

from src.mcp_server import PrologMCPServer


class LocalMcpServerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.server = PrologMCPServer()

    def test_tools_list_contains_core_surface(self) -> None:
        result = self.server.tools_list()
        self.assertEqual(result.get("status"), "success")
        names = {tool.get("name") for tool in result.get("tools", [])}
        self.assertIn("pre_think", names)
        self.assertIn("set_pre_think_session", names)
        self.assertIn("show_pre_think_state", names)
        self.assertIn("record_clarification_answer", names)
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


if __name__ == "__main__":
    unittest.main()
