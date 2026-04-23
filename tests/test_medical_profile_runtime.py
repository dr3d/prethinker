from __future__ import annotations

import importlib.util
from pathlib import Path

from src import medical_profile


ROOT = Path(__file__).resolve().parents[1]
SUITE_MODULE_PATH = ROOT / "scripts" / "run_medical_profile_suite.py"
SUITE_SPEC = importlib.util.spec_from_file_location("run_medical_profile_suite", SUITE_MODULE_PATH)
assert SUITE_SPEC and SUITE_SPEC.loader
SUITE_MODULE = importlib.util.module_from_spec(SUITE_SPEC)
SUITE_SPEC.loader.exec_module(SUITE_MODULE)


def test_canonical_predicate_signatures_follow_profile_manifest():
    manifest = medical_profile.load_profile_manifest()
    signatures = medical_profile.canonical_predicate_signatures(manifest)
    assert signatures == [
        "taking/2",
        "has_condition/2",
        "has_symptom/2",
        "has_allergy/2",
        "underwent_lab_test/2",
        "lab_result_high/2",
        "lab_result_rising/2",
        "lab_result_abnormal/2",
        "pregnant/1",
    ]


def test_build_medical_profile_guide_mentions_palette_and_pronoun_guard():
    guide = medical_profile.build_medical_profile_guide(
        shared_prompt="BASE",
        supplement="SUPPLEMENT",
        concepts=[],
        known_predicates=["taking/2", "pregnant/1"],
    )
    assert "taking/2" in guide
    assert "pregnant/1" in guide
    assert "Do not invent a patient identity from unresolved pronouns." in guide
    assert "only sources of patient identity" in guide
    assert "not discourse context" in guide


def test_medical_profile_suite_render_summary_mentions_profile_and_rollups():
    text = SUITE_MODULE._render_summary_md(
        {
            "generated_at_utc": "2026-04-23T00:00:00+00:00",
            "profile_id": "medical@v0",
            "model": "qwen3.5:9b",
            "profile_assets": {
                "profile_manifest": "modelfiles/profile.medical.v0.json",
                "predicate_registry": "modelfiles/predicate_registry.medical.json",
            },
            "counts": {
                "sharp_memory_cases": 12,
                "sharp_memory_pass": 10,
                "sharp_memory_warn": 2,
                "sharp_memory_fail": 0,
                "clinical_checks_cases": 7,
                "clinical_checks_pass": 5,
                "clinical_checks_warn": 2,
                "clinical_checks_fail": 0,
                "prompt_baseline_score": 58,
                "prompt_medical_score": 70,
                "prompt_score_max": 79,
                "clarification_baseline_score": 21,
                "clarification_medical_score": 33,
                "clarification_score_max": 38,
            },
        }
    )
    assert "medical@v0" in text
    assert "10/12" in text
    assert "33/38" in text


def test_sanitize_medical_parse_for_clarification_clears_logic_on_unresolved_patient():
    parsed = {
        "intent": "assert_fact",
        "needs_clarification": False,
        "logic_string": "underwent_lab_test(noah, serum_creatinine_measurement).",
        "facts": ["underwent_lab_test(noah, serum_creatinine_measurement)."],
        "rules": [],
        "queries": [],
        "ambiguities": ["Patient identity 'his' is unresolved; using canonical example patient."],
        "clarification_question": "",
        "clarification_reason": "",
        "rationale": "Used example patient to maintain schema compliance.",
        "uncertainty_score": 0.15,
        "uncertainty_label": "low",
    }
    sanitized = medical_profile.sanitize_medical_parse_for_clarification(
        parsed,
        utterance="His serum creatinine was repeated this afternoon.",
    )
    assert sanitized is not None
    assert sanitized["needs_clarification"] is True
    assert sanitized["logic_string"] == ""
    assert sanitized["facts"] == []
    assert sanitized["clarification_question"] == "Who does 'his' refer to?"
