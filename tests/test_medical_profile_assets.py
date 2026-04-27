from __future__ import annotations

import json
from pathlib import Path

from src import medical_profile


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


def test_medical_profile_contracts_align_registry_and_type_schema():
    manifest = _load_json(ROOT / "modelfiles" / "profile.medical.v0.json")
    registry = _load_json(ROOT / "modelfiles" / "predicate_registry.medical.json")
    schema = _load_json(ROOT / "modelfiles" / "type_schema.medical.example.json")
    registry_signatures = {
        f"{row['name']}/{row['arity']}"
        for row in registry.get("canonical_predicates", [])
    }
    schema_predicates = set(schema.get("predicates", {}))
    profile_signatures = set(medical_profile.canonical_predicate_signatures(manifest))
    assert profile_signatures == registry_signatures
    assert profile_signatures == schema_predicates

    group_contracts = medical_profile.predicate_argument_groups(manifest)
    assert group_contracts["taking"][1] == {"medication"}
    assert group_contracts["has_condition"][1] == {"condition"}
    assert group_contracts["has_symptom"][1] == {"symptom_or_finding"}
    assert group_contracts["lab_result_high"][1] == {"lab_or_procedure"}
    assert "pregnant" not in group_contracts

    semantic_ir_contracts = medical_profile.semantic_ir_predicate_contracts(manifest)
    taking_contract = next(row for row in semantic_ir_contracts if row["signature"] == "taking/2")
    assert taking_contract["arguments"] == ["person", "medication"]
    assert taking_contract["umls_argument_groups"] == {"1": ["medication"]}
    assert taking_contract["grounding"]["0"] == "patient_identity_required"


def test_medical_profile_semantic_ir_context_summarizes_umls_bridge():
    bridge = {
        "loaded": True,
        "concepts": {
            "warfarin": {
                "preferred_atom": "warfarin",
                "semantic_groups": ["medication"],
                "aliases": ["warfarin", "coumadin"],
            }
        },
    }
    context = medical_profile.semantic_ir_profile_context(
        manifest={"profile_id": "medical@v0"},
        concepts=[],
        umls_bridge=bridge,
    )
    joined = "\n".join(context)
    assert "bounded medical memory" in joined
    assert "explicit named patient/person" in joined
    assert "warfarin" in joined
    assert "coumadin" in joined
    assert "groups=medication" in joined
