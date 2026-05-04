from __future__ import annotations

import unittest

from scripts.run_gateway_turnset import _score_turn_expectations, _summarize


def _turn(*, route: str = "write", clarify: str = "skipped", commit: str = "applied", writes: int = 1) -> dict:
    return {
        "route": route,
        "phases": [
            {"phase": "clarify", "status": clarify, "data": {}},
            {"phase": "commit", "status": commit, "data": {"writes_applied": writes}},
            {"phase": "answer", "status": "ok", "data": {}},
        ],
    }


class GatewayTurnsetRunnerTests(unittest.TestCase):
    def test_scores_turn_expectations_from_structured_gateway_output(self) -> None:
        result = {
            "status": "ok",
            "pending_clarification": {"question": "Which approval?"},
            "turn": _turn(route="write", clarify="required", commit="blocked", writes=0),
        }
        row = {
            "utterance": "It was approved.",
            "expected_status": "ok",
            "expected_route": "write",
            "expected_clarify_status": "required",
            "expected_commit_status": "blocked",
            "expected_pending_before": False,
            "expected_pending_after": True,
            "expected_queue_max": 0,
            "expected_max_writes": 0,
        }

        self.assertEqual(
            _score_turn_expectations(row=row, result=result, pending_before=False),
            [],
        )

    def test_summarize_counts_stenographer_pending_and_delayed_commit(self) -> None:
        responses = [
            {
                "kind": "utterance",
                "pending_before": False,
                "pending_after": True,
                "queued_after": 0,
                "expectations_present": True,
                "expectation_mismatches": [],
                "turn": _turn(route="write", clarify="required", commit="blocked", writes=0),
            },
            {
                "kind": "clarification_answer",
                "pending_before": True,
                "pending_after": False,
                "queued_after": 2,
                "expectations_present": True,
                "expectation_mismatches": ["commit expected applied got failed"],
                "turn": _turn(route="write", clarify="resolved", commit="applied", writes=1),
            },
            {
                "kind": "utterance",
                "pending_before": False,
                "pending_after": False,
                "queued_after": 3,
                "expectations_present": False,
                "expectation_mismatches": [],
                "turn": _turn(route="write", clarify="queued", commit="blocked", writes=0),
            },
        ]

        summary = _summarize(responses)

        self.assertEqual(summary["pending_after_count"], 1)
        self.assertEqual(summary["pending_before_count"], 1)
        self.assertEqual(summary["queued_after_max"], 3)
        self.assertEqual(summary["queued_turns"], 2)
        self.assertEqual(summary["clarify_queued"], 1)
        self.assertEqual(summary["clarification_answer_turns"], 1)
        self.assertEqual(summary["delayed_commit_after_clarification"], 1)
        self.assertEqual(summary["expectation_pass"], 1)
        self.assertEqual(summary["expectation_fail"], 1)


if __name__ == "__main__":
    unittest.main()
