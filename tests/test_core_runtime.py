import unittest

from kb_pipeline import CorePrologRuntime, _apply_to_kb


class CoreRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.runtime = CorePrologRuntime()

    def test_assert_fact_and_query(self) -> None:
        add = self.runtime.assert_fact("parent(alice, bob).")
        self.assertEqual(add.get("status"), "success")

        query = self.runtime.query_rows("parent(alice, X).")
        self.assertEqual(query.get("status"), "success")
        rows = query.get("rows", [])
        self.assertTrue(any(row.get("X") == "bob" for row in rows))

    def test_rule_inference_works(self) -> None:
        self.assertEqual(self.runtime.assert_fact("parent(alice, bob).").get("status"), "success")
        self.assertEqual(self.runtime.assert_fact("parent(bob, carol).").get("status"), "success")
        self.assertEqual(
            self.runtime.assert_rule("ancestor(X, Y) :- parent(X, Y).").get("status"),
            "success",
        )
        self.assertEqual(
            self.runtime.assert_rule("ancestor(X, Z) :- parent(X, Y), ancestor(Y, Z).").get("status"),
            "success",
        )

        query = self.runtime.query_rows("ancestor(alice, Z).")
        self.assertEqual(query.get("status"), "success")
        values = {row.get("Z") for row in query.get("rows", [])}
        self.assertIn("bob", values)
        self.assertIn("carol", values)

    def test_conjunctive_query_shares_variable_bindings(self) -> None:
        self.assertEqual(self.runtime.assert_fact("parent(alice, bob).").get("status"), "success")
        self.assertEqual(self.runtime.assert_fact("parent(alice, dana).").get("status"), "success")
        self.assertEqual(self.runtime.assert_fact("likes(bob, chess).").get("status"), "success")

        query = self.runtime.query_rows("parent(alice, X), likes(X, chess).")

        self.assertEqual(query.get("status"), "success")
        self.assertEqual(query.get("rows"), [{"X": "bob"}])

    def test_temporal_before_compares_bound_timestamp_atoms(self) -> None:
        self.assertEqual(
            self.runtime.assert_fact("boil_water_notice(millbrook, 2026_03_04t14_45, diane_cheng).").get("status"),
            "success",
        )

        query = self.runtime.query_rows("boil_water_notice(Zone, Time, Issuer), before(Time, 2026_03_04t15_00).")

        self.assertEqual(query.get("status"), "success")
        self.assertEqual(
            query.get("rows"),
            [{"Zone": "millbrook", "Time": "2026_03_04t14_45", "Issuer": "diane_cheng"}],
        )

    def test_temporal_after_compares_bound_timestamp_atoms(self) -> None:
        self.assertEqual(
            self.runtime.assert_fact("notice_lifted(2026_03_05t20_30, diane_cheng).").get("status"),
            "success",
        )

        query = self.runtime.query_rows("notice_lifted(Time, Actor), after(Time, 2026_03_05t16_00).")

        self.assertEqual(query.get("status"), "success")
        self.assertEqual(query.get("rows"), [{"Time": "2026_03_05t20_30", "Actor": "diane_cheng"}])

    def test_retract_fact(self) -> None:
        self.assertEqual(self.runtime.assert_fact("parent(alice, bob).").get("status"), "success")
        remove = self.runtime.retract_fact("parent(alice, bob).")
        self.assertEqual(remove.get("status"), "success")

        query = self.runtime.query_rows("parent(alice, X).")
        self.assertEqual(query.get("status"), "no_results")

    def test_reject_non_ground_fact(self) -> None:
        add = self.runtime.assert_fact("parent(X, bob).")
        self.assertEqual(add.get("status"), "validation_error")

    def test_apply_blocks_unknown_predicate_when_registry_strict(self) -> None:
        parsed = {
            "intent": "assert_fact",
            "logic_string": "mother(ann, me).",
            "facts": ["mother(ann, me)."],
            "rules": [],
            "queries": [],
        }
        result = _apply_to_kb(
            self.runtime,
            parsed,
            registry_signatures={"parent/2"},
            strict_registry=True,
            type_schema={"entities": {}, "predicates": {}},
            strict_types=False,
        )
        self.assertEqual(result.get("result", {}).get("status"), "constraint_error")

    def test_apply_blocks_type_mismatch_when_types_enabled(self) -> None:
        parsed = {
            "intent": "assert_fact",
            "logic_string": "parent(alice, flu).",
            "facts": ["parent(alice, flu)."],
            "rules": [],
            "queries": [],
        }
        type_schema = {
            "entities": {
                "alice": "person",
                "flu": "disease",
            },
            "predicates": {
                "parent/2": ["person", "person"],
            },
        }
        result = _apply_to_kb(
            self.runtime,
            parsed,
            registry_signatures={"parent/2"},
            strict_registry=True,
            type_schema=type_schema,
            strict_types=True,
        )
        self.assertEqual(result.get("result", {}).get("status"), "constraint_error")

    def test_apply_dual_writes_temporal_fact_without_changing_base_behavior(self) -> None:
        parsed = {
            "intent": "assert_fact",
            "logic_string": "parent(alice, bob).",
            "facts": ["parent(alice, bob)."],
            "rules": [],
            "queries": [],
        }
        result = _apply_to_kb(
            self.runtime,
            parsed,
            registry_signatures={"parent/2", "at_step/2"},
            strict_registry=True,
            type_schema={"entities": {}, "predicates": {}},
            strict_types=False,
            turn_index=7,
            temporal_dual_write=True,
            temporal_predicate="at_step",
        )
        self.assertEqual(result.get("result", {}).get("status"), "success")
        timeline = result.get("result", {}).get("timeline", {})
        self.assertEqual(timeline.get("status"), "success")

        base_query = self.runtime.query_rows("parent(alice, X).")
        self.assertEqual(base_query.get("status"), "success")
        self.assertTrue(any(row.get("X") == "bob" for row in base_query.get("rows", [])))

        temporal_query = self.runtime.query_rows("at_step(7, parent(alice, bob)).")
        self.assertEqual(temporal_query.get("status"), "success")
        self.assertEqual(int(temporal_query.get("num_rows", 0)), 1)

    def test_apply_dual_write_skips_temporal_when_registry_disallows_predicate(self) -> None:
        parsed = {
            "intent": "assert_fact",
            "logic_string": "parent(alice, bob).",
            "facts": ["parent(alice, bob)."],
            "rules": [],
            "queries": [],
        }
        result = _apply_to_kb(
            self.runtime,
            parsed,
            registry_signatures={"parent/2"},
            strict_registry=True,
            type_schema={"entities": {}, "predicates": {}},
            strict_types=False,
            turn_index=3,
            temporal_dual_write=True,
            temporal_predicate="at_step",
        )
        self.assertEqual(result.get("result", {}).get("status"), "success")
        timeline = result.get("result", {}).get("timeline", {})
        self.assertEqual(timeline.get("status"), "skipped")
        self.assertIn("strict registry", str(timeline.get("reason", "")).lower())

        base_query = self.runtime.query_rows("parent(alice, X).")
        self.assertEqual(base_query.get("status"), "success")
        self.assertTrue(any(row.get("X") == "bob" for row in base_query.get("rows", [])))

        temporal_query = self.runtime.query_rows("at_step(3, parent(alice, bob)).")
        self.assertEqual(temporal_query.get("status"), "no_results")

    def test_apply_dual_write_allows_temporal_when_registry_strict_but_empty(self) -> None:
        parsed = {
            "intent": "assert_fact",
            "logic_string": "parent(alice, bob).",
            "facts": ["parent(alice, bob)."],
            "rules": [],
            "queries": [],
        }
        result = _apply_to_kb(
            self.runtime,
            parsed,
            registry_signatures=set(),
            strict_registry=True,
            type_schema={"entities": {}, "predicates": {}},
            strict_types=False,
            turn_index=5,
            temporal_dual_write=True,
            temporal_predicate="at_step",
        )
        self.assertEqual(result.get("result", {}).get("status"), "success")
        timeline = result.get("result", {}).get("timeline", {})
        self.assertEqual(timeline.get("status"), "success")

        temporal_query = self.runtime.query_rows("at_step(5, parent(alice, bob)).")
        self.assertEqual(temporal_query.get("status"), "success")
        self.assertEqual(int(temporal_query.get("num_rows", 0)), 1)


if __name__ == "__main__":
    unittest.main()
