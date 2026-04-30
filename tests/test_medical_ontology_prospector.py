from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "run_medical_ontology_prospector.py"
SPEC = importlib.util.spec_from_file_location("run_medical_ontology_prospector", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_render_case_includes_clarification_answer_when_present():
    text = MODULE._render_case(
        {
            "case_id": "pressure_clarified_measurement",
            "source": "medical_profile_seed_clarified",
            "utterance": "Mara's pressure has been high lately.",
            "clarification_answer": "I mean her blood pressure readings have been high.",
        }
    )
    assert "CASE_ID: pressure_clarified_measurement" in text
    assert "CLARIFICATION_ANSWER: I mean her blood pressure readings have been high." in text


def test_normalize_candidate_atomizes_name_and_arguments():
    normalized = MODULE._normalize_candidate(
        {
            "name": "Taking",
            "arity": 2,
            "arguments": ["Person", "Medication"],
            "semantic_types": ["Person", "Clinical Drug"],
            "surface_forms": ["takes", "is taking"],
            "example_case_ids": ["pregnancy_warfarin"],
            "decision": "keep_existing",
            "confidence": 0.95,
            "rationale": "Recurring medication relation.",
        }
    )
    assert normalized is not None
    assert normalized["name"] == "taking"
    assert normalized["arguments"] == ["person", "medication"]
    assert normalized["surface_forms"] == ["takes", "is taking"]


def test_aggregate_batches_merges_support_and_rejections():
    aggregate = MODULE._aggregate_batches(
        [
            {
                "parsed": {
                    "candidate_predicates": [
                        {
                            "name": "taking",
                            "arity": 2,
                            "arguments": ["person", "medication"],
                            "semantic_types": ["Person", "Clinical Drug"],
                            "surface_forms": ["takes"],
                            "example_case_ids": ["ibuprofen_brand"],
                            "decision": "keep_existing",
                            "confidence": 0.9,
                            "rationale": "Medication relation.",
                        }
                    ],
                    "rejected_patterns": [
                        {
                            "pattern": "taking_warfarin/1",
                            "reason": "Lexicalized medication predicate.",
                        }
                    ],
                    "coverage_notes": ["Medication utterances converge well."],
                }
            },
            {
                "parsed": {
                    "candidate_predicates": [
                        {
                            "name": "taking",
                            "arity": 2,
                            "arguments": ["person", "medication"],
                            "semantic_types": ["Person", "Clinical Drug"],
                            "surface_forms": ["taking"],
                            "example_case_ids": ["pregnancy_warfarin"],
                            "decision": "keep_existing",
                            "confidence": 0.95,
                            "rationale": "Stable person/drug relation.",
                        }
                    ],
                    "rejected_patterns": [],
                    "coverage_notes": [],
                }
            },
        ],
        total_cases=2,
    )
    candidate = aggregate["candidate_predicates"][0]
    assert candidate["signature"] == "taking/2"
    assert candidate["support_count"] == 2
    assert "takes" in candidate["surface_forms"]
    assert "taking" in candidate["surface_forms"]
    assert aggregate["rejected_patterns"][0]["pattern"] == "taking_warfarin/1"
    assert aggregate["convergence"]["existing_palette_hits"] >= 1
