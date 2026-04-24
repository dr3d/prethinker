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
    bridge = {
        "loaded": True,
        "concepts": {
            "metformin": {
                "semantic_groups": ["medication"],
                "aliases": ["metformin", "glucophage"],
            }
        },
    }
    guide = medical_profile.build_medical_profile_guide(
        shared_prompt="BASE",
        supplement="SUPPLEMENT",
        concepts=[],
        umls_bridge=bridge,
        known_predicates=["taking/2", "pregnant/1"],
    )
    assert "taking/2" in guide
    assert "pregnant/1" in guide
    assert "Do not invent a patient identity from unresolved pronouns." in guide
    assert "only sources of patient identity" in guide
    assert "not discourse context" in guide
    assert "MEDICAL_UMLS_BRIDGE_HINTS" in guide
    assert "metformin" in guide
    assert "Do not create new predicates from UMLS concept names" in guide


def test_load_umls_bridge_facts_indexes_concepts_aliases_and_groups(tmp_path):
    bridge_path = tmp_path / "umls_bridge_facts.pl"
    bridge_path.write_text(
        "\n".join(
            [
                "umls_concept(metformin, 'C0025598').",
                "umls_preferred_atom(metformin, metformin).",
                "umls_semantic_group(metformin, medication).",
                "umls_alias_norm(metformin, glucophage).",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    bridge = medical_profile.load_umls_bridge_facts(bridge_path)
    assert bridge["loaded"] is True
    assert bridge["concepts"]["metformin"]["cui"] == "C0025598"
    assert bridge["concepts"]["metformin"]["semantic_groups"] == ["medication"]
    assert bridge["aliases"]["glucophage"] == "metformin"


def test_bridge_admission_guidance_matches_aliases_and_vague_terms(tmp_path):
    bridge_path = tmp_path / "umls_bridge_facts.pl"
    bridge_path.write_text(
        "umls_concept(metformin, 'C0025598').\n"
        "umls_semantic_group(metformin, medication).\n"
        "umls_alias_norm(metformin, glucophage).\n",
        encoding="utf-8",
    )
    bridge = medical_profile.load_umls_bridge_facts(bridge_path)
    guided = medical_profile.bridge_admission_guidance("Mara takes Glucophage.", bridge)
    assert guided["mentions"][0]["seed_id"] == "metformin"
    assert guided["mentions"][0]["semantic_groups"] == ["medication"]
    vague = medical_profile.bridge_admission_guidance("Mara's pressure is bad.", bridge)
    assert vague["needs_clarification"] is True
    assert vague["vague_surfaces"][0]["surface"] == "pressure"


def test_sanitize_medical_parse_for_bridge_clears_incompatible_fact(tmp_path):
    bridge_path = tmp_path / "umls_bridge_facts.pl"
    bridge_path.write_text(
        "umls_concept(blood_pressure_measurement, 'C0005824').\n"
        "umls_semantic_group(blood_pressure_measurement, lab_or_procedure).\n"
        "umls_alias_norm(blood_pressure_measurement, blood_pressure).\n",
        encoding="utf-8",
    )
    bridge = medical_profile.load_umls_bridge_facts(bridge_path)
    parsed = {
        "intent": "assert_fact",
        "needs_clarification": False,
        "logic_string": "has_condition(mara, blood_pressure_measurement).",
        "facts": ["has_condition(mara, blood_pressure_measurement)."],
        "rules": [],
        "queries": [],
        "ambiguities": [],
        "clarification_question": "",
        "clarification_reason": "",
        "rationale": "Mapped pressure to a condition.",
        "uncertainty_score": 0.1,
        "uncertainty_label": "low",
    }
    sanitized = medical_profile.sanitize_medical_parse_for_bridge(
        parsed,
        utterance="Mara's blood pressure has been high.",
        bridge=bridge,
    )
    assert sanitized is not None
    assert sanitized["needs_clarification"] is True
    assert sanitized["logic_string"] == ""
    assert sanitized["facts"] == []
    assert "UMLS bridge type steering" in sanitized["clarification_reason"]


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
