import json
from pathlib import Path

from scripts.audit_typed_micro_near_misses import build_report, render_markdown


def _write_json(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def test_near_miss_audit_labels_source_coordinate_only_with_registry(tmp_path: Path) -> None:
    registry = _write_json(
        tmp_path / "registry.json",
        {
            "predicates": [
                {
                    "signature": "state_ag_party/5",
                    "args": [
                        "instrument_id",
                        "party_id",
                        "party_role",
                        "party_name",
                        "source_or_scope",
                    ],
                }
            ]
        },
    )
    summary = _write_json(
        tmp_path / "summary.json",
        {
            "fixture_id": "state_ag_transfer_demo",
            "support_threshold": 2,
            "rows": [
                {
                    "expected_fact": "state_ag_party(instrument_1, respondent_1, respondent, alpha_llc, source_para_1).",
                    "meets_threshold": False,
                    "support_count": 0,
                    "same_predicate_variants": [
                        {
                            "fact": "state_ag_party(instrument_1, respondent_1, respondent, alpha_llc, source_para_2).",
                            "run_count": 2,
                            "runs": ["run1", "run2"],
                        }
                    ],
                }
            ],
        },
    )

    report = build_report(summary_paths=[summary], profile_registry_path=registry)

    row = report["rows"][0]
    assert row["source_coordinate_only"] is True
    assert row["diagnosis"] == "source_coordinate_only"
    assert row["same_primary_subject_stable"] is True
    assert row["best_stable_mismatch_slots"] == ["source_or_scope"]
    assert row["best_stable_mismatch_slot_classes"] == ["source_coordinate"]
    assert report["by_slot"] == [
        {"slot": "source_or_scope", "slot_class": "source_coordinate", "count": 1}
    ]
    assert "This diagnostic reads typed facts only" in render_markdown(report)


def test_near_miss_audit_reports_same_subject_value_drift(tmp_path: Path) -> None:
    registry = _write_json(
        tmp_path / "registry.json",
        {
            "predicates": [
                {
                    "signature": "state_ag_obligation/7",
                    "args": [
                        "instrument_id",
                        "obligated_party",
                        "obligation_id",
                        "obligation_kind",
                        "frequency_or_status",
                        "amount_or_scope",
                        "source_or_scope",
                    ],
                }
            ]
        },
    )
    summary = _write_json(
        tmp_path / "summary.json",
        {
            "fixture_id": "state_ag_transfer_demo",
            "support_threshold": 2,
            "rows": [
                {
                    "expected_fact": "state_ag_obligation(instrument_1, alpha_llc, obligation_1, restitution, one_time, amount_1, source_1).",
                    "meets_threshold": False,
                    "support_count": 0,
                    "same_predicate_variants": [
                        {
                            "fact": "state_ag_obligation(instrument_1, alpha_llc, obligation_1, injunctive_relief, one_time, amount_1, source_1).",
                            "run_count": 3,
                            "runs": ["run1", "run2", "run3"],
                        }
                    ],
                }
            ],
        },
    )

    report = build_report(summary_paths=[summary], profile_registry_path=registry)

    row = report["rows"][0]
    assert row["source_coordinate_only"] is False
    assert row["diagnosis"] == "same_subject_value_or_slot_drift"
    assert row["same_primary_subject_stable"] is True
    assert row["best_stable_mismatch_slots"] == ["obligation_kind"]
    assert report["by_predicate"][0]["signature"] == "state_ag_obligation/7"
    assert report["by_predicate"][0]["stable_variant_count"] == 1


def test_near_miss_audit_distinguishes_unstable_variants_and_ignores_variables(
    tmp_path: Path,
) -> None:
    summary = _write_json(
        tmp_path / "summary.json",
        {
            "fixture_id": "demo_fixture",
            "support_threshold": 2,
            "rows": [
                {
                    "expected_fact": "demo_fact(Entity, expected_value, source_1).",
                    "meets_threshold": False,
                    "support_count": 0,
                    "same_predicate_variants": [
                        {
                            "fact": "demo_fact(item_1, nearby_value, source_1).",
                            "run_count": 1,
                            "runs": ["run1"],
                        }
                    ],
                }
            ],
        },
    )

    report = build_report(summary_paths=[summary])

    row = report["rows"][0]
    assert row["stable_variant_count"] == 0
    assert row["diagnosis"] == "no_stable_same_predicate_variant"
    assert row["best_stable_mismatch_slots"] == []
    assert row["best_any_mismatch_slots"] == ["arg2"]
    assert report["summary"]["no_stable_variant_count"] == 1


def test_near_miss_audit_reports_parse_errors_as_blocking(tmp_path: Path) -> None:
    summary = _write_json(
        tmp_path / "summary.json",
        {
            "fixture_id": "bad_fixture",
            "support_threshold": 2,
            "rows": [
                {
                    "expected_fact": "not a fact",
                    "meets_threshold": False,
                    "support_count": 0,
                    "same_predicate_variants": [],
                }
            ],
        },
    )

    report = build_report(summary_paths=[summary])

    assert report["summary"]["status"] == "fail"
    assert report["summary"]["blocking_reasons"] == ["parse_errors_present"]
    assert report["summary"]["diagnosis_counts"] == {"parse_error": 1}
    assert "expected_fact_parse_error" in report["summary"]["errors"][0]
