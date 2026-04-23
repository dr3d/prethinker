from __future__ import annotations

import importlib.util
from pathlib import Path

from src import umls_mvp


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "run_umls_mvp_clinical_probe.py"
SPEC = importlib.util.spec_from_file_location("run_umls_mvp_clinical_probe", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_fired_checks_returns_expected_rule_when_required_seeds_are_present():
    checks = [
        {
            "check_id": "pregnancy_warfarin_risk",
            "required_seed_ids": ["pregnancy", "warfarin"],
            "label": "Pregnancy plus warfarin exposure",
            "kind": "medication_risk",
        }
    ]
    fired = MODULE._fired_checks({"pregnancy", "warfarin"}, checks)
    assert [row["check_id"] for row in fired] == ["pregnancy_warfarin_risk"]


def test_case_outcome_warns_when_expected_check_is_missing():
    case = {
        "case_id": "pregnancy_case",
        "utterance": "She is pregnant and still taking Coumadin.",
        "expected_checks": ["pregnancy_warfarin_risk"],
    }
    checks = [
        {
            "check_id": "pregnancy_warfarin_risk",
            "required_seed_ids": ["pregnancy", "warfarin"],
            "label": "Pregnancy plus warfarin exposure",
            "kind": "medication_risk",
        }
    ]
    alias_records = [
        {"alias": "pregnant", "seed_id": "pregnancy", "preferred_name": "Pregnancy"},
    ]
    outcome = MODULE._case_outcome(case, checks, alias_records)
    assert outcome["verdict"] == "warn"
    assert outcome["missing_checks"] == ["pregnancy_warfarin_risk"]


def test_case_outcome_passes_when_expected_check_fires():
    case = {
        "case_id": "pregnancy_case",
        "utterance": "She is pregnant and still taking Coumadin.",
        "expected_checks": ["pregnancy_warfarin_risk"],
    }
    checks = [
        {
            "check_id": "pregnancy_warfarin_risk",
            "required_seed_ids": ["pregnancy", "warfarin"],
            "label": "Pregnancy plus warfarin exposure",
            "kind": "medication_risk",
        }
    ]
    alias_records = [
        {"alias": "pregnant", "seed_id": "pregnancy", "preferred_name": "Pregnancy"},
        {"alias": "coumadin", "seed_id": "warfarin", "preferred_name": "warfarin"},
    ]
    outcome = MODULE._case_outcome(case, checks, alias_records)
    assert outcome["verdict"] == "pass"
    assert outcome["missing_checks"] == []
