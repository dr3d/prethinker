import unittest

from kb_pipeline import (
    CorePrologRuntime,
    _apply_progress_directives,
    _apply_to_kb,
    _clarification_policy_decision,
    _empty_progress_memory,
    _extract_progress_directives,
)


class ProgressMemoryTests(unittest.TestCase):
    def test_extract_progress_directives_from_utterance_entry(self) -> None:
        raw = {
            "utterance": "Alice is Bob's parent.",
            "progress": {
                "set_active_focus": ["family lineage"],
                "add_goals": ["track parent links"],
            },
        }
        directives = _extract_progress_directives(raw)
        self.assertEqual(directives.get("set_active_focus"), ["family lineage"])
        self.assertEqual(directives.get("add_goals"), ["track parent links"])

    def test_progress_directives_add_and_resolve_items(self) -> None:
        memory = _empty_progress_memory("progress_test")
        memory, events = _apply_progress_directives(
            memory,
            {
                "set_active_focus": ["hospital oxygen supply"],
                "add_goals": ["stabilize oxygen chain"],
                "add_open_questions": ["which supplier is delayed"],
            },
            turn_index=1,
        )
        self.assertTrue(events)
        self.assertEqual(memory.get("active_focus"), ["hospital oxygen supply"])
        self.assertEqual(len(memory.get("goals", [])), 1)
        self.assertEqual(len(memory.get("open_questions", [])), 1)

        memory, events = _apply_progress_directives(
            memory,
            {
                "resolve_goals": ["stabilize oxygen chain"],
                "resolve_questions": ["which supplier is delayed"],
            },
            turn_index=2,
        )
        self.assertTrue(any(row.get("kind") == "resolve_goal" for row in events))
        self.assertTrue(any(row.get("kind") == "resolve_question" for row in events))
        self.assertEqual(memory["goals"][0]["status"], "resolved")
        self.assertEqual(memory["open_questions"][0]["status"], "resolved")
        self.assertGreaterEqual(len(memory.get("resolved_items", [])), 2)

    def test_policy_requests_clarification_for_low_relevance_write(self) -> None:
        parsed = {
            "intent": "assert_fact",
            "logic_string": "mother(ann, me).",
            "confidence": {"overall": 0.9, "intent": 0.95, "logic": 0.9},
            "ambiguities": [],
            "needs_clarification": False,
            "uncertainty_score": 0.1,
        }
        progress_memory = _empty_progress_memory("pm")
        progress_memory["active_focus"] = ["hospital oxygen supply incident"]
        progress_memory["goals"] = [
            {
                "id": "goal_x",
                "text": "restore oxygen inventory",
                "status": "active",
                "priority": 1,
                "created_turn": 1,
                "updated_turn": 1,
                "source": "test",
            }
        ]
        decision = _clarification_policy_decision(
            parsed=parsed,
            clarification_eagerness=0.35,
            utterance="My mother is Ann.",
            progress_memory=progress_memory,
            progress_low_relevance_threshold=0.34,
            progress_high_risk_threshold=0.18,
        )
        self.assertTrue(decision.get("progress_low_relevance"))
        self.assertTrue(decision.get("request_clarification"))
        self.assertGreaterEqual(float(decision.get("effective_uncertainty", 0.0)), 0.8)

    def test_policy_does_not_force_clarification_for_relevant_write(self) -> None:
        parsed = {
            "intent": "assert_fact",
            "logic_string": "parent(alice, bob).",
            "confidence": {"overall": 0.9, "intent": 0.95, "logic": 0.9},
            "ambiguities": [],
            "needs_clarification": False,
            "uncertainty_score": 0.1,
            "components": {
                "predicates": ["parent"],
                "atoms": ["alice", "bob"],
                "variables": [],
            },
            "facts": ["parent(alice, bob)."],
            "rules": [],
            "queries": [],
        }
        progress_memory = _empty_progress_memory("pm")
        progress_memory["active_focus"] = ["parent alice bob lineage"]
        decision = _clarification_policy_decision(
            parsed=parsed,
            clarification_eagerness=0.35,
            utterance="Alice is Bob's parent.",
            progress_memory=progress_memory,
            progress_low_relevance_threshold=0.34,
            progress_high_risk_threshold=0.18,
        )
        self.assertFalse(decision.get("progress_low_relevance"))
        self.assertFalse(decision.get("request_clarification"))

    def test_progress_memory_never_mutates_truth_without_apply(self) -> None:
        runtime = CorePrologRuntime()
        parsed = {
            "intent": "assert_fact",
            "logic_string": "parent(alice, bob).",
            "facts": ["parent(alice, bob)."],
            "rules": [],
            "queries": [],
        }
        result = _apply_to_kb(
            runtime,
            parsed,
            registry_signatures={"parent/2"},
            strict_registry=True,
            type_schema={"entities": {}, "predicates": {}},
            strict_types=False,
        )
        self.assertEqual(result.get("result", {}).get("status"), "success")
        query = runtime.query_rows("parent(alice, X).")
        self.assertEqual(query.get("status"), "success")
        self.assertTrue(any(row.get("X") == "bob" for row in query.get("rows", [])))


if __name__ == "__main__":
    unittest.main()
