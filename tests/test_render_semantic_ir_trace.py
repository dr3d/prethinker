import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.render_semantic_ir_trace import main, render_html, render_markdown


class RenderSemanticIRTraceTests(unittest.TestCase):
    def test_renders_workspace_and_admission_layers(self) -> None:
        record = {
            "scenario_id": "demo_conflict",
            "domain": "demo",
            "utterance": "Mara is in Paris. Actually, not London.",
            "context": ["Existing current fact: lives_in(mara, london)."],
            "allowed_predicates": ["lives_in/2"],
            "router_profile": "medical@v0",
            "effective_profile": "medical@v0",
            "expected_profile": "medical@v0",
            "router": {
                "schema_version": "semantic_router_v1",
                "selected_profile_id": "medical@v0",
                "candidate_profile_ids": ["medical@v0"],
                "routing_confidence": 0.93,
                "turn_shape": "correction",
                "should_segment": False,
                "segments": [],
                "guidance_modules": ["correction_retraction"],
                "retrieval_hints": {
                    "entity_terms": ["Mara"],
                    "predicate_terms": ["lives_in"],
                    "context_needs": ["current residence"],
                },
                "risk_flags": ["current_state_correction"],
                "bootstrap_request": {
                    "needed": False,
                    "proposed_domain_name": "",
                    "why": "",
                    "candidate_predicate_concepts": [],
                },
                "notes": ["Use KB state only as context."],
            },
            "anti_coupling": {
                "version": "anti_coupling_diagnostics_v1",
                "flag_count": 1,
                "summary": {
                    "expected_profile": "medical@v0",
                    "effective_profile": "medical@v0",
                    "routing_confidence": 0.93,
                    "projected_decision": "commit",
                    "admitted_count": 2,
                    "skipped_count": 1,
                },
                "flags": [
                    {
                        "severity": "review",
                        "kind": "mapper_skips_tied_to_profile_context",
                        "detail": "Mapper skipped one out-of-palette proposal.",
                        "skip_reasons": {"predicate_not_in_allowed_palette": 1},
                    }
                ],
            },
            "model_input": {
                "input_payload": {
                    "domain": "demo",
                    "utterance": "Mara is in Paris. Actually, not London.",
                    "context": ["Existing current fact: lives_in(mara, london)."],
                    "allowed_predicates": ["lives_in/2"],
                },
                "messages": [
                    {"role": "system", "content": "system prompt"},
                    {"role": "user", "content": "INPUT_JSON: {...}"},
                ],
                "options": {"temperature": 0.0, "num_ctx": 16384},
            },
            "score": {"decision": "commit", "expected_decision": "commit", "rough_score": 1.0},
            "parsed": {
                "schema_version": "semantic_ir_v1",
                "decision": "commit",
                "turn_type": "correction",
                "entities": [
                    {
                        "id": "e1",
                        "surface": "Mara",
                        "normalized": "Mara",
                        "type": "person",
                        "confidence": 0.99,
                    },
                    {
                        "id": "e2",
                        "surface": "Paris",
                        "normalized": "Paris",
                        "type": "place",
                        "confidence": 0.98,
                    },
                ],
                "referents": [],
                "assertions": [
                    {
                        "kind": "correction",
                        "subject": "e1",
                        "relation_concept": "residence",
                        "object": "e2",
                        "polarity": "positive",
                        "certainty": 0.96,
                    }
                ],
                "unsafe_implications": [],
                "truth_maintenance": {
                    "support_links": [
                        {
                            "operation_index": 1,
                            "support_kind": "direct_utterance",
                            "support_ref": "current turn says Mara is in Paris",
                            "role": "grounds",
                            "confidence": 0.96,
                        }
                    ],
                    "conflicts": [
                        {
                            "new_operation_index": 1,
                            "existing_ref": "context:lives_in(mara,london)",
                            "conflict_kind": "functional_overwrite",
                            "recommended_policy": "commit",
                            "why": "Explicit correction retracts the old residence before asserting the new one.",
                        }
                    ],
                    "retraction_plan": [
                        {
                            "operation_index": 0,
                            "target_ref": "context:lives_in(mara,london)",
                            "reason": "explicit_correction",
                        }
                    ],
                    "derived_consequences": [],
                },
                "temporal_graph": {
                    "schema_version": "temporal_graph_v1",
                    "events": [
                        {
                            "id": "ev1",
                            "label": "Mara moved to Paris",
                            "participants": ["e1", "e2"],
                            "source_status": "direct_assertion",
                            "support_ref": "current turn",
                        }
                    ],
                    "time_anchors": [
                        {
                            "id": "t1",
                            "value": "now",
                            "precision": "relative",
                            "source_status": "direct_assertion",
                            "support_ref": "current turn",
                        }
                    ],
                    "intervals": [],
                    "edges": [],
                },
                "candidate_operations": [
                    {
                        "operation": "retract",
                        "predicate": "lives_in",
                        "args": ["Mara", "London"],
                        "polarity": "negative",
                        "source": "direct",
                        "safety": "safe",
                    },
                    {
                        "operation": "assert",
                        "predicate": "lives_in",
                        "args": ["Mara", "Paris"],
                        "polarity": "positive",
                        "source": "direct",
                        "safety": "safe",
                    },
                    {
                        "operation": "assert",
                        "predicate": "untracked_location",
                        "args": ["Mara", "France"],
                        "polarity": "positive",
                        "source": "direct",
                        "safety": "safe",
                    },
                ],
                "clarification_questions": [],
                "self_check": {"bad_commit_risk": "low", "missing_slots": [], "notes": ["clear correction"]},
            },
        }

        rendered = render_markdown(
            [record],
            source=__file__,
            raw_chars=0,
            side="root",
            limit=0,
        )

        self.assertIn("Layer 0 - Focused Model Input", rendered)
        self.assertIn("Layer 0a - Semantic Router / Context Plan", rendered)
        self.assertIn("Selected profile: `medical@v0`", rendered)
        self.assertIn("Confidence: `0.93`", rendered)
        self.assertIn("Recorded model input / request envelope", rendered)
        self.assertIn("Exact chat messages sent to model", rendered)
        self.assertIn("Layer 2 - Parsed `semantic_ir_v1` Workspace", rendered)
        self.assertIn("Layer 3 - Deterministic Mapper / Admission Gate", rendered)
        self.assertIn("Support / dependency links", rendered)
        self.assertIn("**Support / dependency links:**\n\n| op # | kind | role | support ref | confidence |", rendered)
        self.assertIn("context:lives_in(mara,london)", rendered)
        self.assertIn("explicit_correction", rendered)
        self.assertIn("**Conflict proposals:**\n\n| op # | existing/context ref | kind | policy | why |", rendered)
        self.assertIn("**Retraction plan:**\n\n| op # | target | reason |", rendered)
        self.assertIn("Temporal graph proposal", rendered)
        self.assertIn("Diagnostic only. Durable temporal facts still require admitted `candidate_operations`.", rendered)
        self.assertIn("Mara moved to Paris", rendered)
        self.assertIn("**Time anchors:**\n\n| id | value | precision | source | support ref |", rendered)
        self.assertIn("Layer 3c - Truth-Maintenance / Admission Delta", rendered)
        self.assertIn("Truth-maintenance/admission alignment", rendered)
        self.assertIn("admitted_operation_without_model_support_link", rendered)
        self.assertIn("Layer 3d - Router / Compiler Coupling Diagnostics", rendered)
        self.assertIn("mapper_skips_tied_to_profile_context", rendered)
        self.assertIn("Facts passivated for KB assertion", rendered)
        self.assertIn("**Facts passivated for KB assertion:**\n\n- `lives_in(mara, paris).`", rendered)
        self.assertIn("Retract targets / correction clauses", rendered)
        self.assertIn("**Retract targets / correction clauses:**\n\n- `lives_in(mara, london).`", rendered)
        self.assertIn("lives_in(mara, paris).", rendered)
        self.assertIn("lives_in(mara, london).", rendered)
        self.assertIn("predicate_palette_gate", rendered)
        self.assertIn('<details class="trace-record" markdown="1">', rendered)
        self.assertIn('<summary class="record-summary">', rendered)

        rendered_html = render_html(rendered, title="demo")
        self.assertIn('<details class="trace-record">', rendered_html)
        self.assertIn('<summary class="record-summary">', rendered_html)
        self.assertIn("<h3>Layer 0 - Focused Model Input</h3>", rendered_html)

    def test_renders_parse_error_without_crashing(self) -> None:
        record = {
            "scenario_id": "bad_json",
            "domain": "demo",
            "utterance": "broken",
            "content": "",
            "parsed": None,
            "parse_error": "timed out",
            "score": {"rough_score": 0.0},
        }

        rendered = render_markdown([record], source=__file__, raw_chars=100, side="root", limit=0)

        self.assertIn("Parse unavailable", rendered)
        self.assertIn("timed out", rendered)

    def test_html_renders_markdown_instead_of_source_pre(self) -> None:
        html = render_html(
            "# Semantic IR Trace\n\n## 1. `demo`\n\n```json\n{\"ok\": true}\n```\n",
            title="demo",
        )

        self.assertIn("<h1>Semantic IR Trace</h1>", html)
        self.assertIn("<h2>1. <code>demo</code></h2>", html)
        self.assertIn("max-height: 28rem", html)
        self.assertNotIn("<pre># Semantic IR Trace", html)

    def test_html_out_suffix_writes_rendered_html_not_markdown_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            jsonl = tmp_path / "run.jsonl"
            out = tmp_path / "trace.html"
            jsonl.write_text(
                json.dumps(
                    {
                        "scenario_id": "demo",
                        "domain": "demo",
                        "utterance": "Mara is in Paris.",
                        "parsed": None,
                        "parse_error": "not needed",
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            with patch.object(sys, "argv", ["render_semantic_ir_trace.py", str(jsonl), "--out", str(out)]):
                self.assertEqual(main(), 0)

            text = out.read_text(encoding="utf-8")
            self.assertTrue(text.lstrip().startswith("<!doctype html>"))
            self.assertIn("<h1>Semantic IR Trace</h1>", text)
            self.assertNotIn("# Semantic IR Trace", text[:200])


if __name__ == "__main__":
    unittest.main()
