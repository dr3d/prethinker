import unittest

from ui_gateway.gateway.runtime_hooks import RuntimeHooks


class RuntimeHooksFamilyBundleTests(unittest.TestCase):
    def test_augment_compound_family_facts_handles_is_variant(self) -> None:
        hooks = RuntimeHooks()
        parsed = {
            "intent": "assert_fact",
            "logic_string": "parent(ann, scotts_mom). parent(ian, scotts_mom).",
            "facts": [
                "parent(ann, scotts_mom).",
                "parent(ian, scotts_mom).",
            ],
            "rules": [],
            "queries": [],
            "components": {
                "atoms": ["ann", "ian", "scotts_mom"],
                "variables": [],
                "predicates": ["parent"],
            },
            "rationale": "Temporary parser rationale.",
        }

        out = hooks._augment_compound_family_facts(
            parsed=parsed,
            utterance="scotts mom and dad is ann and ian.",
            clarification_answer="",
        )

        self.assertEqual(
            out.get("facts"),
            ["parent(ann, scott).", "parent(ian, scott)."],
        )
        self.assertEqual(
            out.get("logic_string"),
            "parent(ann, scott). parent(ian, scott).",
        )
        self.assertEqual(out.get("ambiguities"), [])
        self.assertIn("explicit family bundle", str(out.get("rationale", "")).lower())
        self.assertNotIn("scotts_mom", str(out.get("rationale", "")).lower())

    def test_augment_compound_family_facts_handles_inverse_possessive_relation(self) -> None:
        hooks = RuntimeHooks()
        parsed = {
            "intent": "assert_fact",
            "logic_string": "best_friend(freds, barny).",
            "facts": [
                "best_friend(freds, barny).",
            ],
            "rules": [],
            "queries": [],
            "components": {
                "atoms": ["freds", "barny"],
                "variables": [],
                "predicates": ["best_friend"],
            },
            "ambiguities": [],
            "rationale": "Temporary parser rationale.",
        }

        out = hooks._augment_compound_family_facts(
            parsed=parsed,
            utterance="barny is freds best friend",
            clarification_answer="",
        )

        self.assertEqual(
            out.get("facts"),
            ["best_friend(barny, fred)."],
        )
        self.assertEqual(
            out.get("logic_string"),
            "best_friend(barny, fred).",
        )
        self.assertEqual(out.get("ambiguities"), [])
        self.assertIn("inverse possessive relation", str(out.get("rationale", "")).lower())

    def test_canonicalize_subject_prefixed_predicate_uses_registry_form(self) -> None:
        hooks = RuntimeHooks()
        parsed = {
            "intent": "assert_fact",
            "logic_string": "hope_lives_in(hope, salem).",
            "facts": [
                "hope_lives_in(hope, salem).",
            ],
            "rules": [],
            "queries": [],
            "components": {
                "atoms": ["hope", "salem"],
                "variables": [],
                "predicates": ["hope_lives_in"],
            },
            "ambiguities": [],
            "rationale": "Temporary parser rationale.",
        }

        out = hooks._canonicalize_subject_prefixed_predicates(parsed)

        self.assertEqual(
            out.get("facts"),
            ["lives_in(hope, salem)."],
        )
        self.assertEqual(
            out.get("logic_string"),
            "lives_in(hope, salem).",
        )
        self.assertEqual(out.get("ambiguities"), [])
        self.assertIn("registry form", str(out.get("rationale", "")).lower())

    def test_answer_uses_yes_for_grounded_yes_no_query(self) -> None:
        hooks = RuntimeHooks()
        execution = {
            "status": "success",
            "intent": "query",
            "writes_applied": 0,
            "operations": [],
            "query_result": {
                "status": "success",
                "num_rows": 1,
                "rows": [{}],
                "variables": [],
                "prolog_query": "made_with(muffins, walnuts).",
            },
            "parse": {
                "intent": "query",
                "queries": ["made_with(muffins, walnuts)."],
            },
            "errors": [],
        }

        answer = hooks.answer(
            utterance="can you make muffins with walnuts?",
            route="query",
            execution=execution,
            clarification=None,
            config={"served_handoff_mode": "never"},
        )

        self.assertEqual(answer.get("text"), "Yes.")


if __name__ == "__main__":
    unittest.main()
