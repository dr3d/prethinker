from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_medical_predicate_registry_has_nine_canonical_predicates():
    payload = _load_json(ROOT / "modelfiles" / "predicate_registry.medical.json")
    predicates = payload.get("canonical_predicates", [])
    signatures = {
        (str(row.get("name", "")).strip(), int(row.get("arity", 0) or 0))
        for row in predicates
    }
    assert len(signatures) == 9
    assert ("taking", 2) in signatures
    assert ("pregnant", 1) in signatures
    assert ("has_condition", 2) in signatures
    assert ("has_symptom", 2) in signatures
    assert ("has_allergy", 2) in signatures
    assert ("underwent_lab_test", 2) in signatures
    assert ("lab_result_high", 2) in signatures
    assert ("lab_result_rising", 2) in signatures
    assert ("lab_result_abnormal", 2) in signatures


def test_medical_profile_manifest_points_to_existing_assets():
    manifest = _load_json(ROOT / "modelfiles" / "profile.medical.v0.json")
    assert manifest.get("profile_id") == "medical@v0"
    for key in (
        "predicate_registry",
        "type_schema_example",
        "prompt_supplement",
        "ontology_prospector_prompt",
    ):
        rel = str(manifest.get(key, "")).strip()
        assert rel
        assert (ROOT / rel).exists()
    assert str(manifest.get("umls_slice_dir", "")).strip()
    assert str(manifest.get("umls_bridge_facts", "")).strip().endswith("umls_bridge_facts.pl")
    settings = manifest.get("recommended_settings", {})
    assert settings.get("strict_registry") is True
    assert settings.get("strict_types") is False


def test_medical_type_schema_example_covers_core_predicates():
    schema = _load_json(ROOT / "modelfiles" / "type_schema.medical.example.json")
    predicates = schema.get("predicates", {})
    assert predicates.get("taking/2") == ["person", "medication"]
    assert predicates.get("has_condition/2") == ["person", "condition"]
    assert predicates.get("has_symptom/2") == ["person", "symptom"]
    assert predicates.get("has_allergy/2") == ["person", "allergy_or_substance"]
    assert predicates.get("pregnant/1") == ["person"]
