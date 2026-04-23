from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "run_medical_clarification_probe.py"
SPEC = importlib.util.spec_from_file_location("run_medical_clarification_probe", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_effective_utterance_embeds_question_and_answer():
    case = {
        "utterance": "Mara's pressure has been high lately.",
        "clarification_question": "Do you mean a blood pressure reading or a diagnosis?",
        "clarification_answer": "I mean blood pressure readings.",
    }
    effective = MODULE._effective_utterance(case)
    assert "Clarification question:" in effective
    assert "Clarification answer:" in effective


def test_score_initial_rewards_clarification_with_empty_logic():
    case = {"initial_expect_needs_clarification": True}
    parsed = {"needs_clarification": True, "logic_string": ""}
    scored = MODULE._score_initial(case, parsed)
    assert scored["score"] == scored["score_max"]


def test_score_final_rewards_expected_logic_and_blocks_forbidden_logic():
    case = {
        "final_expect_needs_clarification": False,
        "final_expected_logic_contains": ["lab_result_high(mara, blood_pressure_measurement)."],
        "final_forbidden_logic_contains": ["hypertension"],
    }
    parsed = {
        "needs_clarification": False,
        "logic_string": "lab_result_high(mara, blood_pressure_measurement).",
    }
    scored = MODULE._score_final(case, parsed)
    assert scored["score"] == scored["score_max"]
