import unittest
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
UI_GATEWAY_ROOT = REPO_ROOT / "ui_gateway"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(UI_GATEWAY_ROOT) not in sys.path:
    sys.path.insert(0, str(UI_GATEWAY_ROOT))

from gateway.phases import process_turn
from gateway.session_store import SessionState


class _FakeRuntime:
    def __init__(self) -> None:
        self.answer_execution = None
        self.answer_route = None

    def process_utterance(self, *, utterance, config, session, clarification_answer=None, prethink_id=None):
        return {
            "status": "clarification_required",
            "front_door": {
                "route": "query",
                "compiler_intent": "query",
                "looks_like_query": True,
                "looks_like_write": False,
                "ambiguity_score": 0.85,
                "needs_clarification": True,
                "reasons": ["User request lacks specific constraints for recommendation."],
                "clarification_question": "What cuisine or location do you prefer for dinner tonight?",
                "prethink_id": "pt-123",
            },
            "execution": None,
            "compiler_trace": {"summary": {"overall": "prethink=primary; raw routing packet accepted"}},
        }

    def should_handoff_instead_of_clarify(self, *, route, config):
        return True

    def answer(self, *, utterance, route, execution, clarification, config):
        self.answer_execution = execution
        self.answer_route = route
        return {
            "speaker": "served-llm",
            "text": "Try a good local spot for dinner.",
            "mode": "served_llm_handoff",
        }


class _FailingClarificationRuntime:
    def process_utterance(self, *, utterance, config, session, clarification_answer=None, prethink_id=None):
        if clarification_answer:
            return {
                "status": "ok",
                "front_door": {
                    "route": "write",
                    "compiler_intent": "assert_fact",
                    "needs_clarification": False,
                    "reasons": ["clarification_resolved"],
                    "clarification_question": "",
                    "prethink_id": prethink_id or "pt-123",
                },
                "execution": {
                    "status": "error",
                    "intent": "assert_fact",
                    "writes_applied": 0,
                    "operations": [],
                    "query_result": None,
                    "parse": {},
                    "errors": ["assert_fact requires facts[0]"],
                },
                "compiler_trace": {"summary": {"overall": "parse failed"}},
            }
        return {
            "status": "clarification_required",
            "front_door": {
                "route": "write",
                "compiler_intent": "assert_fact",
                "looks_like_query": False,
                "looks_like_write": True,
                "ambiguity_score": 0.9,
                "needs_clarification": True,
                "reasons": ["needs_clarification"],
                "clarification_question": "Which exact fact should be stored?",
                "prethink_id": "pt-123",
            },
            "execution": None,
            "compiler_trace": {"summary": {"overall": "hold"}},
        }

    def should_handoff_instead_of_clarify(self, *, route, config):
        return False

    def answer(self, *, utterance, route, execution, clarification, config):
        return {
            "speaker": "prethink-gateway",
            "text": "Execution blocked.",
            "mode": "answer",
        }


class _MedicalClarificationRuntime:
    def process_utterance(self, *, utterance, config, session, clarification_answer=None, prethink_id=None):
        if clarification_answer:
            return {
                "status": "ok",
                "front_door": {
                    "route": "write",
                    "compiler_intent": "assert_fact",
                    "needs_clarification": False,
                    "reasons": ["medical_clarification_resolved"],
                    "clarification_question": "",
                    "prethink_id": prethink_id or "pt-medical",
                },
                "execution": {
                    "status": "success",
                    "intent": "assert_fact",
                    "writes_applied": 1,
                    "operations": [
                        {
                            "tool": "assert_fact",
                            "status": "success",
                            "clause": "lab_result_high(mara, blood_pressure_measurement).",
                        }
                    ],
                    "query_result": None,
                    "parse": {
                        "intent": "assert_fact",
                        "facts": ["lab_result_high(mara, blood_pressure_measurement)."],
                    },
                    "errors": [],
                },
                "compiler_trace": {"summary": {"overall": "medical clarification rescued"}},
            }
        return {
            "status": "clarification_required",
            "front_door": {
                "route": "query",
                "compiler_intent": "query",
                "looks_like_query": True,
                "looks_like_write": False,
                "ambiguity_score": 0.9,
                "needs_clarification": True,
                "reasons": ["vague_medical_surface"],
                "clarification_question": "Which specific blood pressure measurement is bad for Mara?",
                "prethink_id": "pt-medical",
            },
            "execution": None,
            "compiler_trace": {"summary": {"overall": "hold"}},
        }

    def should_handoff_instead_of_clarify(self, *, route, config):
        return False

    def answer(self, *, utterance, route, execution, clarification, config):
        return {
            "speaker": "prethink-gateway",
            "text": "Stored: Mara had a high blood pressure result.",
            "mode": "answer",
        }


class _SegmentRuntime:
    def __init__(self) -> None:
        self.calls = []
        self.contexts = []

    def process_utterance(self, *, utterance, config, session, clarification_answer=None, prethink_id=None, context=None):
        self.calls.append(utterance)
        self.contexts.append(list(context or []))
        atom = f"segment_{len(self.calls)}"
        return {
            "status": "ok",
            "front_door": {
                "route": "write",
                "compiler_intent": "assert_fact",
                "needs_clarification": False,
                "reasons": ["semantic_ir_v1"],
                "clarification_question": "",
                "prethink_id": f"pt-{len(self.calls)}",
            },
            "execution": {
                "status": "success",
                "intent": "assert_fact",
                "writes_applied": 1,
                "operations": [
                    {
                        "tool": "assert_fact",
                        "result": {"status": "success", "fact": f"observed({atom})."},
                    }
                ],
                "query_result": None,
                "parse": {"intent": "assert_fact", "facts": [f"observed({atom})."]},
                "errors": [],
            },
            "compiler_trace": {
                "parse": {
                    "semantic_ir": {
                        "model": "qwen/qwen3.6-35b-a3b",
                        "parsed": {"decision": "commit", "turn_type": "state_update"},
                    },
                    "normalized": {
                        "admission_diagnostics": {
                            "admitted_count": 1,
                            "skipped_count": 0,
                            "operations": [{"admitted": True}],
                        }
                    },
                },
                "summary": {"overall": "semantic_ir_v1"},
            },
        }

    def should_handoff_instead_of_clarify(self, *, route, config):
        return False

    def answer(self, *, utterance, route, execution, clarification, config):
        return {"speaker": "prethink-gateway", "text": "unused", "mode": "answer"}


class _QueryBoundarySegmentRuntime(_SegmentRuntime):
    def process_utterance(self, *, utterance, config, session, clarification_answer=None, prethink_id=None, context=None):
        self.calls.append(utterance)
        self.contexts.append(list(context or []))
        index = len(self.calls)
        if "?" in utterance:
            return {
                "status": "ok",
                "front_door": {
                    "route": "query",
                    "compiler_intent": "query",
                    "needs_clarification": False,
                    "reasons": ["semantic_ir_v1"],
                    "clarification_question": "",
                    "prethink_id": f"pt-{index}",
                },
                "execution": {
                    "status": "success",
                    "intent": "query",
                    "writes_applied": 0,
                    "operations": [
                        {
                            "tool": "query_rows",
                            "result": {"status": "success", "query": "owns(mara, X)."},
                        }
                    ],
                    "query_result": {"status": "success", "rows": [{"X": "lease"}]},
                    "parse": {"intent": "query", "queries": ["owns(mara, X)."]},
                    "errors": [],
                },
                "compiler_trace": {
                    "parse": {
                        "semantic_ir": {
                            "model": "qwen/qwen3.6-35b-a3b",
                            "parsed": {"decision": "answer", "turn_type": "query"},
                        },
                        "normalized": {
                            "admission_diagnostics": {
                                "admitted_count": 1,
                                "skipped_count": 0,
                                "operations": [{"admitted": True, "effect": "query"}],
                            }
                        },
                    },
                    "summary": {"overall": "semantic_ir_v1"},
                },
            }
        atom = f"fact_{index}"
        return {
            "status": "ok",
            "front_door": {
                "route": "write",
                "compiler_intent": "assert_fact",
                "needs_clarification": False,
                "reasons": ["semantic_ir_v1"],
                "clarification_question": "",
                "prethink_id": f"pt-{index}",
            },
            "execution": {
                "status": "success",
                "intent": "assert_fact",
                "writes_applied": 1,
                "operations": [
                    {
                        "tool": "assert_fact",
                        "result": {"status": "success", "fact": f"observed({atom})."},
                    }
                ],
                "query_result": None,
                "parse": {"intent": "assert_fact", "facts": [f"observed({atom})."]},
                "errors": [],
            },
            "compiler_trace": {
                "parse": {
                    "semantic_ir": {
                        "model": "qwen/qwen3.6-35b-a3b",
                        "parsed": {"decision": "commit", "turn_type": "state_update"},
                    },
                    "normalized": {
                        "admission_diagnostics": {
                            "admitted_count": 1,
                            "skipped_count": 0,
                            "operations": [{"admitted": True, "effect": "fact"}],
                        }
                    },
                },
                "summary": {"overall": "semantic_ir_v1"},
            },
        }


class GatewayPhasesTests(unittest.TestCase):
    def test_process_turn_uses_served_handoff_when_clarification_is_suppressed(self) -> None:
        runtime = _FakeRuntime()
        session = SessionState(session_id="session-test")
        config = {
            "front_door_uri": "prethink://local/front-door",
            "served_handoff_mode": "always",
            "strict_mode": False,
        }

        result = process_turn(
            utterance="i think we are going out to eat tonight - wheres a good place?",
            session=session,
            config=config,
            runtime=runtime,
            config_store=None,
        )

        turn = result["turn"]
        self.assertEqual(turn["assistant"]["mode"], "served_llm_handoff")
        self.assertIsNone(result["pending_clarification"])
        self.assertEqual(runtime.answer_route, "query")
        self.assertIsNotNone(runtime.answer_execution)
        self.assertEqual(runtime.answer_execution["status"], "success")
        clarify_phase = next(phase for phase in turn["phases"] if phase["phase"] == "clarify")
        self.assertEqual(clarify_phase["status"], "skipped")
        self.assertEqual(
            clarify_phase["data"]["reason"],
            "served_handoff_instead_of_clarify",
        )

    def test_failed_clarification_resolution_keeps_pending_turn(self) -> None:
        runtime = _FailingClarificationRuntime()
        session = SessionState(session_id="session-test")
        config = {
            "front_door_uri": "prethink://local/front-door",
            "served_handoff_mode": "never",
            "strict_mode": True,
        }

        first = process_turn(
            utterance="Mara's pressure is bad lately.",
            session=session,
            config=config,
            runtime=runtime,
            config_store=None,
        )
        self.assertIsNotNone(first["pending_clarification"])

        second = process_turn(
            utterance="Mara's blood pressure reading was high.",
            session=session,
            config=config,
            runtime=runtime,
            config_store=None,
        )

        self.assertIsNotNone(second["pending_clarification"])
        self.assertEqual(
            second["pending_clarification"]["original_utterance"],
            "Mara's pressure is bad lately.",
        )

    def test_medical_clarification_followup_can_commit_original_staged_turn(self) -> None:
        runtime = _MedicalClarificationRuntime()
        session = SessionState(session_id="session-medical")
        config = {
            "front_door_uri": "prethink://local/front-door",
            "served_handoff_mode": "never",
            "strict_mode": True,
            "active_profile": "medical@v0",
        }

        first = process_turn(
            utterance="Mara's pressure is bad lately.",
            session=session,
            config=config,
            runtime=runtime,
            config_store=None,
        )
        self.assertIsNotNone(first["pending_clarification"])

        second = process_turn(
            utterance="Mara's blood pressure reading was high.",
            session=session,
            config=config,
            runtime=runtime,
            config_store=None,
        )

        self.assertIsNone(second["pending_clarification"])
        turn = second["turn"]
        self.assertEqual(turn["route"], "write")
        commit_phase = next(phase for phase in turn["phases"] if phase["phase"] == "commit")
        self.assertEqual(commit_phase["status"], "applied")
        self.assertEqual(commit_phase["data"]["writes_applied"], 1)
        self.assertEqual(
            commit_phase["data"]["operations"][0]["clause"],
            "lab_result_high(mara, blood_pressure_measurement).",
        )

    def test_long_story_uses_segmented_semantic_ir_ingestion(self) -> None:
        runtime = _SegmentRuntime()
        session = SessionState(session_id="session-story")
        config = {
            "front_door_uri": "prethink://local/front-door",
            "served_handoff_mode": "never",
            "strict_mode": True,
            "semantic_ir_enabled": True,
        }
        story = "\n".join(
            [
                "Goldilocks was a little girl.",
                "Goldilocks walked through the forest.",
                "Goldilocks found a small house in the forest.",
                "There were three bowls of porridge on the table.",
            ]
            * 8
        )

        result = process_turn(
            utterance=story,
            session=session,
            config=config,
            runtime=runtime,
            config_store=None,
        )

        turn = result["turn"]
        self.assertEqual(turn["route"], "write")
        self.assertEqual(len(runtime.calls), 32)
        self.assertEqual(len(runtime.contexts), 32)
        self.assertIn("processing segment 1/32", runtime.contexts[0][0])
        self.assertEqual(len(runtime.contexts[0]), 2)
        self.assertIn("processing segment 2/32", runtime.contexts[1][0])
        self.assertIn("prior_source_segment_1: Goldilocks was a little girl.", runtime.contexts[1])
        self.assertTrue(
            any("do not import outside story or world knowledge" in item for item in runtime.contexts[1])
        )
        self.assertEqual(turn["trace"]["segmented_story"]["segment_count"], 32)
        commit_phase = next(phase for phase in turn["phases"] if phase["phase"] == "commit")
        self.assertEqual(commit_phase["status"], "applied")
        self.assertEqual(commit_phase["data"]["writes_applied"], 32)

    def test_query_boundary_segmentation_keeps_queries_from_piling_into_writes(self) -> None:
        runtime = _QueryBoundarySegmentRuntime()
        session = SessionState(session_id="session-query-boundary")
        config = {
            "front_door_uri": "prethink://local/front-door",
            "served_handoff_mode": "never",
            "strict_mode": True,
            "semantic_ir_enabled": True,
        }
        utterance = (
            "Mara owns the lease. Oskar manages the unit. Who owns the lease? "
            "Also remember that Theo signed the addendum."
        )

        result = process_turn(
            utterance=utterance,
            session=session,
            config=config,
            runtime=runtime,
            config_store=None,
        )

        self.assertEqual(result["status"], "ok")
        self.assertEqual(
            runtime.calls,
            [
                "Mara owns the lease.",
                "Oskar manages the unit.",
                "Who owns the lease?",
                "Also remember that Theo signed the addendum.",
            ],
        )
        self.assertEqual(len(runtime.contexts), 4)
        self.assertIn("processing segment 3/4", runtime.contexts[2][0])
        self.assertIn("prior_source_segment_1: Mara owns the lease.", runtime.contexts[2])
        self.assertIn("prior_source_segment_2: Oskar manages the unit.", runtime.contexts[2])
        turn = result["turn"]
        self.assertEqual(turn["route"], "write")
        ingest = next(phase for phase in turn["phases"] if phase["phase"] == "ingest")
        self.assertEqual(ingest["data"]["strategy"], "query_boundary_semantic_ir_ingestion")
        workspace = next(phase for phase in turn["phases"] if phase["phase"] == "workspace")
        self.assertEqual(workspace["data"]["segment_count"], 4)
        self.assertEqual(workspace["data"]["query_count"], 1)
        commit = next(phase for phase in turn["phases"] if phase["phase"] == "commit")
        self.assertEqual(commit["data"]["writes_applied"], 3)
        self.assertEqual(commit["data"]["status"], "success")
        self.assertIn("segmented_query_boundaries", turn["trace"])
        self.assertEqual(turn["trace"]["segmented_query_boundaries"]["query_count"], 1)


if __name__ == "__main__":
    unittest.main()
