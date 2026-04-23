from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "run_medical_prompt_probe.py"
SPEC = importlib.util.spec_from_file_location("run_medical_prompt_probe", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_score_parse_rewards_expected_logic_and_blocks_forbidden_logic():
    case = {
        "expected_route": "assert_fact",
        "expect_needs_clarification": False,
        "expected_logic_contains": ["taking(lena, warfarin)."],
        "forbidden_logic_contains": ["taking_coumadin("],
    }
    parsed = {
        "intent": "assert_fact",
        "needs_clarification": False,
        "logic_string": "pregnant(lena).\ntaking(lena, warfarin).",
    }
    scored = MODULE._score_parse(case, parsed)
    assert scored["score"] == scored["score_max"]


def test_render_concept_hints_includes_seed_and_aliases():
    text = MODULE._render_concept_hints(
        [
            {
                "seed_id": "warfarin",
                "preferred_name": "warfarin",
                "semantic_types": [{"sty": "Pharmacologic Substance"}],
                "aliases": [{"text": "Coumadin"}, {"text": "warfarin"}],
            }
        ]
    )
    assert "warfarin" in text
    assert "Coumadin" in text
    assert "Pharmacologic Substance" in text


def test_build_medical_guide_includes_clarification_first_instruction():
    guide = MODULE._build_medical_guide("BASE", "SUPPLEMENT", [])
    assert "keep logic_string empty" in guide
    assert "Do not invent a patient identity" in guide
