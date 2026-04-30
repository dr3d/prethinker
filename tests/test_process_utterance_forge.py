import importlib.util
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FORGE_PATH = ROOT / "scripts" / "run_process_utterance_forge.py"
SPEC = importlib.util.spec_from_file_location("process_utterance_forge", FORGE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_summarize_result_extracts_parse_and_trace_fields():
    result = {
        "status": "success",
        "result_type": "utterance_processed",
        "front_door": {
            "route": "write",
            "compiler_intent": "assert_fact",
            "needs_clarification": False,
            "clarification_question": "",
            "ambiguity_score": 0.12,
        },
        "execution": {
            "status": "success",
            "writes_applied": 1,
            "operations": [{"tool": "assert_fact"}],
            "query_result": None,
            "errors": [],
            "parse": {
                "intent": "assert_fact",
                "logic_string": "lives_in(hope, salem).",
            },
        },
        "compiler_trace": {
            "summary": {
                "overall": "parse adjusted via synthetic_guard",
                "parse_rescues": ["synthetic_guard"],
            }
        },
    }
    summary = MODULE._summarize_result(result)
    assert summary["status"] == "success"
    assert summary["route"] == "write"
    assert summary["parse_intent"] == "assert_fact"
    assert summary["logic_string"] == "lives_in(hope, salem)."
    assert summary["writes_applied"] == 1
    assert summary["trace_parse_rescues"] == ["synthetic_guard"]


def test_interestingness_score_weights_failures_above_passes():
    fail_score = MODULE._interestingness_score(
        {"verdict": "fail", "severity": 0.7},
        {"status": "error", "needs_clarification": False, "trace_parse_rescues": []},
    )
    pass_score = MODULE._interestingness_score(
        {"verdict": "pass", "severity": 0.2},
        {"status": "success", "needs_clarification": False, "trace_parse_rescues": []},
    )
    assert fail_score > pass_score


def test_should_keep_case_respects_pass_sample_rate_and_keep_flag():
    rng = random.Random(54)
    assert MODULE._should_keep_case(
        judgment={"verdict": "warn", "severity": 0.4, "keep_case": True},
        result_summary={"status": "success", "needs_clarification": False, "trace_parse_rescues": []},
        pass_sample_rate=0.0,
        rng=rng,
    )
    assert not MODULE._should_keep_case(
        judgment={"verdict": "pass", "severity": 0.1, "keep_case": False},
        result_summary={"status": "success", "needs_clarification": False, "trace_parse_rescues": []},
        pass_sample_rate=0.0,
        rng=rng,
    )
    assert MODULE._should_keep_case(
        judgment={"verdict": "pass", "severity": 0.1, "keep_case": False},
        result_summary={"status": "success", "needs_clarification": False, "trace_parse_rescues": []},
        pass_sample_rate=1.0,
        rng=rng,
    )


def test_meta_generator_artifact_guard_rejects_anchor_dump_shape():
    assert MODULE._looks_meta_generator_artifact(
        "I want you to list every single item from the anchor list in one sentence"
    )
    assert not MODULE._looks_meta_generator_artifact("Remember that Hope lives in Salem.")


def test_choose_lane_error_focus_biases_correction_and_pronoun_followups():
    rng = random.Random(54)
    counts = {}
    transcript = [{"turn_index": 1}]
    for _ in range(200):
        lane = MODULE._choose_lane(transcript, rng, "error_focus")
        counts[lane] = counts.get(lane, 0) + 1
    assert counts.get("correction", 0) > counts.get("compound_fact", 0)
    assert counts.get("pronoun_carryover", 0) > counts.get("relationship_bundle", 0)


def test_choose_lane_temporal_focus_biases_temporal_followups():
    rng = random.Random(54)
    counts = {}
    transcript = [{"turn_index": 1}]
    for _ in range(200):
        lane = MODULE._choose_lane(transcript, rng, "temporal_focus")
        counts[lane] = counts.get(lane, 0) + 1
    assert counts.get("temporal_state", 0) > counts.get("correction", 0)
    assert counts.get("temporal_state", 0) > counts.get("query_after_write", 0)
