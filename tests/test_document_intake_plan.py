import json
import unittest

from src.document_intake_plan import (
    INTAKE_PLAN_JSON_SCHEMA,
    build_intake_plan_messages,
    intake_plan_context,
    parse_intake_plan_json,
)


class DocumentIntakePlanTests(unittest.TestCase):
    def test_build_messages_puts_raw_source_under_llm_control(self) -> None:
        messages = build_intake_plan_messages(
            source_text="We declare the harbor independent and list grievances.",
            source_name="declaration.md",
            domain_hint="declaration_style_document",
        )

        self.assertEqual(messages[0]["role"], "system")
        self.assertIn("intake planner", messages[0]["content"])
        self.assertIn("do not emit Prolog", messages[0]["content"])
        self.assertEqual(messages[1]["role"], "user")
        self.assertIn("INPUT_JSON", messages[1]["content"])
        self.assertIn("raw_source_text", messages[1]["content"])
        self.assertIn("declaration_style_document", messages[1]["content"])
        self.assertIn("required_top_level_json_shape", messages[1]["content"])
        self.assertIn("Do not put a long list", messages[1]["content"])
        self.assertIn("source-record and reporting acts", messages[1]["content"])

    def test_schema_is_strict_control_plane_object(self) -> None:
        self.assertEqual(INTAKE_PLAN_JSON_SCHEMA["type"], "object")
        self.assertFalse(INTAKE_PLAN_JSON_SCHEMA["additionalProperties"])
        self.assertIn("source_boundary", INTAKE_PLAN_JSON_SCHEMA["required"])
        self.assertIn("predicate_family_strategy", INTAKE_PLAN_JSON_SCHEMA["required"])
        self.assertIn("pass_plan", INTAKE_PLAN_JSON_SCHEMA["required"])
        family_schema = INTAKE_PLAN_JSON_SCHEMA["properties"]["predicate_family_strategy"]["items"]
        self.assertFalse(family_schema["additionalProperties"])
        pass_schema = INTAKE_PLAN_JSON_SCHEMA["properties"]["pass_plan"]["items"]
        self.assertFalse(pass_schema["additionalProperties"])

    def test_parse_and_project_context(self) -> None:
        parsed, error = parse_intake_plan_json(
            json.dumps(
                {
                    "schema_version": "intake_plan_v1",
                    "source_boundary": {
                        "source_id_hint": "thalos_declaration",
                        "source_type": "declaration",
                        "epistemic_stance": "source_claims_not_external_facts",
                        "why": "The document speaks in accusations and declarations.",
                    },
                    "symbolic_strategy": [
                        "Preserve source boundary before repeated grievances.",
                        "Represent accusations as source-attributed grievances.",
                    ],
                    "entity_strategy": ["Promote recurring institutions and groups to entities."],
                    "predicate_family_strategy": [
                        {
                            "family": "grievance",
                            "purpose": "Uniform query surface for repeated accusations.",
                            "recommended_predicates": ["grievance/2", "grievance_actor/2"],
                            "epistemic_status": "claim_by_source",
                        }
                    ],
                    "pass_plan": [
                        {
                            "pass_id": "pass_1",
                            "purpose": "source boundary",
                            "focus": "document identity and speaker",
                            "operation_budget": "small",
                            "recommended_predicates": ["document/1", "document_type/2"],
                            "completion_policy": "always include",
                        }
                    ],
                    "risk_policy": ["Do not collapse grievances into verified facts."],
                    "self_check": {"plan_authority": "proposal_only", "notes": ["Use as guidance only."]},
                }
            )
        )

        self.assertEqual(error, "")
        self.assertIsNotNone(parsed)
        context = intake_plan_context(parsed)
        self.assertTrue(any("source_claims_not_external_facts" in row for row in context))
        self.assertTrue(any("grievance/2" in row for row in context))
        self.assertTrue(any("pass_1" in row for row in context))
        self.assertTrue(any("Do not collapse" in row for row in context))


if __name__ == "__main__":
    unittest.main()
