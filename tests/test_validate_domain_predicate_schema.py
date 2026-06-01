import json
from pathlib import Path

from scripts.validate_domain_predicate_schema import build_report


def test_empty_domain_predicate_schema_input_still_checks_carrier_registry():
    report = build_report([])

    assert report["summary"]["registry_count"] == 0
    assert report["summary"]["blocking_errors"] == 0


def test_fda_domain_predicate_schema_registry_matches_contracts():
    report = build_report([Path("datasets/domain_profiles/fda_warning_letter_v1/ontology_registry.json")])

    assert report["summary"]["status"] == "pass"
    assert report["summary"]["registry_count"] == 1
    assert report["summary"]["predicate_count"] >= 10
    assert report["registries"][0]["errors"] == []


def test_domain_predicate_schema_validator_blocks_unregistered_signature(tmp_path):
    path = tmp_path / "ontology_registry.json"
    path.write_text(
        json.dumps(
            {
                "schema": "candidate_profile_registry_v1",
                "fixture": "bad_domain_v1",
                "predicates": [
                    {
                        "signature": "made_up_domain_fact/2",
                        "args": ["subject_id", "detail_value"],
                        "category": "bad",
                        "notes": "Not registered.",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    report = build_report([path])

    assert report["summary"]["status"] == "fail"
    assert "made_up_domain_fact/2:unregistered_signature" in report["registries"][0]["errors"]


def test_domain_predicate_schema_validator_blocks_argument_drift(tmp_path):
    path = tmp_path / "ontology_registry.json"
    path.write_text(
        json.dumps(
            {
                "schema": "candidate_profile_registry_v1",
                "fixture": "bad_fda_domain_v1",
                "predicates": [
                    {
                        "signature": "fda_warning_letter/5",
                        "args": ["letter_id", "issue_date", "recipient_entity", "issuing_office", "source_or_scope"],
                        "category": "fda_document_wrapper",
                        "notes": "Registered signature but wrong argument order.",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    report = build_report([path])

    assert report["summary"]["status"] == "fail"
    assert "fda_warning_letter/5:args_do_not_match_carrier_contract" in report["registries"][0]["errors"]
