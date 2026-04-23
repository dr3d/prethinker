import unittest
from types import SimpleNamespace
from unittest.mock import patch

from ui_gateway.gateway.runtime_hooks import RuntimeHooks
from src.mcp_server import PrologMCPServer


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

    def test_canonicalize_subject_suffixed_predicate_uses_registry_form(self) -> None:
        hooks = RuntimeHooks()
        parsed = {
            "intent": "assert_fact",
            "logic_string": "runs_scott(bakery).",
            "facts": [
                "runs_scott(bakery).",
            ],
            "rules": [],
            "queries": [],
            "components": {
                "atoms": ["bakery"],
                "variables": [],
                "predicates": ["runs_scott"],
            },
            "ambiguities": [],
            "rationale": "Temporary parser rationale.",
        }

        out = hooks._canonicalize_subject_prefixed_predicates(parsed)

        self.assertEqual(
            out.get("facts"),
            ["runs(scott, bakery)."],
        )
        self.assertEqual(
            out.get("logic_string"),
            "runs(scott, bakery).",
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

    def test_apply_parsed_executes_mixed_rule_fact_and_query_bundle(self) -> None:
        hooks = RuntimeHooks()
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

        execution = hooks._apply_parsed(parsed=parsed, prethink_id=prethink_id, server=server)

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

    def test_should_handoff_instead_of_clarify_when_served_mode_is_always_and_not_strict(self) -> None:
        hooks = RuntimeHooks()

        should_handoff = hooks.should_handoff_instead_of_clarify(
            route="query",
            config={"served_handoff_mode": "always", "strict_mode": False},
        )

        self.assertTrue(should_handoff)

    def test_should_not_handoff_instead_of_clarify_when_strict_mode_is_on(self) -> None:
        hooks = RuntimeHooks()

        should_handoff = hooks.should_handoff_instead_of_clarify(
            route="query",
            config={"served_handoff_mode": "always", "strict_mode": True},
        )

        self.assertFalse(should_handoff)

    def test_build_served_prompt_for_other_turn_requests_plain_text_chat(self) -> None:
        hooks = RuntimeHooks()

        prompt = hooks._build_served_prompt(
            utterance="my feet were hurting this morning so i skipped my walk. hows your day been?",
            route="other",
            execution={
                "intent": "other",
                "writes_applied": 0,
                "query_result": None,
                "parse": {},
            },
        )

        self.assertIn("Reply naturally in plain text", prompt)
        self.assertIn("Do not return JSON", prompt)
        self.assertNotIn("DETERMINISTIC_SUMMARY_JSON", prompt)

    def test_served_handoff_response_uses_text_mode_and_unwraps_json_response(self) -> None:
        hooks = RuntimeHooks()

        with patch("ui_gateway.gateway.runtime_hooks._get_api_key", return_value=None), patch(
            "ui_gateway.gateway.runtime_hooks._call_model_prompt",
            return_value=SimpleNamespace(message='{"response":"Hello there."}', reasoning="", raw={}),
        ) as mocked:
            answer = hooks._served_handoff_response(
                utterance="my feet were hurting this morning so i skipped my walk. hows your day been?",
                route="other",
                execution={
                    "intent": "other",
                    "writes_applied": 0,
                    "query_result": None,
                    "parse": {},
                },
                config={
                    "served_llm_provider": "ollama",
                    "served_llm_model": "gpt-oss:20b",
                    "served_llm_base_url": "http://127.0.0.1:11434",
                    "served_llm_context_length": 32768,
                    "served_llm_timeout": 60,
                    "served_handoff_mode": "always",
                },
            )

        self.assertEqual(answer.get("text"), "Hello there.")
        self.assertEqual(mocked.call_args.kwargs["response_format"], "text")
        self.assertIn("served_llm", answer)
        self.assertIn("prompt_text", answer["served_llm"])
        self.assertIn("USER_UTTERANCE:", str(answer["served_llm"]["prompt_text"]))


if __name__ == "__main__":
    unittest.main()
