import json

from scripts.audit_helper_usage import audit_roots, candidate_transfer_signal, render_markdown


def write_qa_artifact(path, fixture: str, helper: str, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "qa_file": f"C:/prethinker/datasets/story_worlds/{fixture}/qa.md",
                "rows": [
                    {
                        "query_results": [
                            {
                                "result": {
                                    "predicate": helper,
                                    "rows": rows,
                                }
                            }
                        ]
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


def write_judged_qa_artifact(path, fixture: str, helper: str, helper_rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "qa_file": f"C:/prethinker/datasets/story_worlds/{fixture}/qa.md",
                "rows": [
                    {
                        "reference_judge": {"verdict": "exact"},
                        "query_results": [
                            {
                                "result": {
                                    "predicate": helper,
                                    "rows": helper_rows,
                                }
                            }
                        ],
                    },
                    {"reference_judge": {"verdict": "miss"}, "query_results": []},
                ],
            }
        ),
        encoding="utf-8",
    )


def test_helper_usage_audit_flags_low_transfer_helpers(tmp_path) -> None:
    write_qa_artifact(
        tmp_path / "a.json",
        "fixture_a",
        "one_fixture_support",
        [{"HelperClass": "candidate-helper"}],
    )
    write_qa_artifact(
        tmp_path / "b.json",
        "fixture_b",
        "shared_support",
        [{"HelperClass": "clean-helper"}],
    )
    write_qa_artifact(
        tmp_path / "c.json",
        "fixture_c",
        "shared_support",
        [{"HelperClass": "clean-helper"}],
    )

    payload = audit_roots([tmp_path], rare_threshold=1, implemented_helpers={"shared_support"})

    assert payload["helper_count"] == 2
    assert payload["helpers"]["one_fixture_support"]["suspicious_low_transfer"] is True
    assert payload["helpers"]["one_fixture_support"]["implemented"] is False
    assert payload["helpers"]["one_fixture_support"]["support_kind_counts"] == {"unknown": 1}
    assert payload["orphaned_artifact_helper_count"] == 1
    assert payload["helpers"]["shared_support"]["suspicious_low_transfer"] is False
    assert payload["helpers"]["shared_support"]["implemented"] is True
    assert payload["helpers"]["shared_support"]["fixture_count"] == 2
    assert payload["fixtures"]["fixture_a"]["helper_count"] == 1
    assert payload["fixtures"]["fixture_b"]["helpers"] == ["shared_support"]

    markdown = render_markdown(payload)
    assert "one_fixture_support" in markdown
    assert "shared_support" in markdown
    assert "fixture_a" in markdown


def test_helper_usage_audit_counts_unlabeled_helper_rows(tmp_path) -> None:
    write_qa_artifact(
        tmp_path / "unlabeled.json",
        "fixture_a",
        "unlabeled_support",
        [{"SupportKind": "legacy_row"}],
    )

    payload = audit_roots([tmp_path], rare_threshold=1, implemented_helpers={"unlabeled_support"})

    assert payload["helpers"]["unlabeled_support"]["helper_class_counts"] == {"unlabeled": 1}
    assert payload["helpers"]["unlabeled_support"]["support_kind_counts"] == {"legacy_row": 1}
    assert payload["fixtures"]["fixture_a"]["helper_class_counts"] == {"unlabeled": 1}


def test_helper_usage_audit_does_not_double_count_evidence_plan_provenance_copy(tmp_path) -> None:
    helper_result = {
        "result": {
            "predicate": "roster_state_support",
            "rows": [{"HelperClass": "candidate-helper", "SupportKind": "group_count"}],
        }
    }
    path = tmp_path / "duplicate.json"
    path.write_text(
        json.dumps(
            {
                "qa_file": "C:/prethinker/datasets/story_worlds/fixture_a/qa.md",
                "rows": [
                    {
                        "reference_judge": {"verdict": "exact"},
                        "query_results": [helper_result],
                        "evidence_bundle_plan_query_results": [helper_result],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    payload = audit_roots([tmp_path], rare_threshold=1, implemented_helpers={"roster_state_support"})

    assert payload["helpers"]["roster_state_support"]["row_count"] == 1
    assert payload["helpers"]["roster_state_support"]["unique_row_count"] == 1
    assert payload["candidate_pruning_targets"][0]["candidate_rows"] == 1


def test_helper_usage_audit_measures_helper_pressure_against_answer_surface(tmp_path) -> None:
    write_judged_qa_artifact(
        tmp_path / "pressure.json",
        "fixture_a",
        "roster_state_support",
        [{"HelperClass": "candidate-helper", "SupportKind": "group_count"} for _ in range(600)],
    )

    payload = audit_roots([tmp_path], rare_threshold=1, implemented_helpers={"roster_state_support"})
    fixture = payload["fixtures"]["fixture_a"]

    assert payload["schema_version"] == "helper_usage_audit_v2"
    assert payload["helper_pressure_summary"]["pressure_label"] == "high_compatibility_pressure"
    assert payload["helper_pressure_summary"]["helper_rows_per_exact"] == 600.0
    assert payload["helper_pressure_summary"]["unique_row_count"] == 1
    assert payload["helper_pressure_summary"]["exact_rate"] == 0.5
    assert payload["helpers"]["roster_state_support"]["helper_class_support_kind_counts"] == {
        "candidate-helper": {"group_count": 600}
    }
    assert payload["helpers"]["roster_state_support"]["unique_helper_class_support_kind_counts"] == {
        "candidate-helper": {"group_count": 1}
    }
    assert payload["candidate_pruning_targets"] == [
        {
            "helper": "roster_state_support",
            "support_kind": "group_count",
            "candidate_rows": 600,
            "unique_candidate_rows": 1,
            "helper_rows": 600,
            "unique_helper_rows": 1,
            "candidate_share_of_helper": 1.0,
            "unique_candidate_share_of_helper": 1.0,
            "fixture_count": 1,
            "transfer_signal": "single_fixture_pressure",
        }
    ]
    assert fixture["unique_row_count"] == 1
    assert fixture["candidate_helper_share"] == 1.0
    assert fixture["pressure_label"] == "high_compatibility_pressure"

    markdown = render_markdown(payload)
    assert "Compatibility Adapter Usage Audit" in markdown
    assert "Adapter Pruning Targets" in markdown
    assert "600 (1 unique)" in markdown
    assert "`group_count`" in markdown
    assert "`single_fixture_pressure`" in markdown
    assert "Rows/exact" in markdown
    assert "high_compatibility_pressure" in markdown


def test_candidate_transfer_signal_separates_single_fixture_debt_from_transfer_scars() -> None:
    assert candidate_transfer_signal(fixture_count=1, unique_candidate_rows=20) == "single_fixture_pressure"
    assert candidate_transfer_signal(fixture_count=2, unique_candidate_rows=1) == "narrow_transfer_scar"
    assert candidate_transfer_signal(fixture_count=4, unique_candidate_rows=12) == "transferred_candidate_pressure"
