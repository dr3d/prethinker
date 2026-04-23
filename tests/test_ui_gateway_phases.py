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


if __name__ == "__main__":
    unittest.main()
