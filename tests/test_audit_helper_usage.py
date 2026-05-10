import json

from scripts.audit_helper_usage import audit_roots, render_markdown


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
