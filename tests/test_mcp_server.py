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
        add = self.server.tools_call("assert_fact", {"clause": "parent(alice, bob)."})
        self.assertEqual(add.get("status"), "success")

        query = self.server.tools_call("query_rows", {"query": "parent(alice, X)."})
        self.assertEqual(query.get("status"), "success")
        rows = query.get("rows", [])
        self.assertTrue(any(row.get("X") == "bob" for row in rows))

    def test_pre_think_packet_shape(self) -> None:
        packet = self.server.tools_call("pre_think", {"utterance": "Who is Alice?"})
        self.assertEqual(packet.get("status"), "success")
        self.assertEqual(packet.get("result_type"), "pre_think_packet")
        inner = packet.get("packet", {})
        self.assertEqual(inner.get("mode"), "short_circuit")
        self.assertIn("signals", inner)

    def test_unknown_tool_returns_not_found(self) -> None:
        result = self.server.tools_call("not_a_tool", {})
        self.assertEqual(result.get("status"), "not_found")


if __name__ == "__main__":
    unittest.main()

