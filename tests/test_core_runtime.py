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


if __name__ == "__main__":
    unittest.main()
