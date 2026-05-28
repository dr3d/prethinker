import json
from pathlib import Path

from scripts.score_source_support_adjudication import build_report, render_markdown


def _row(row_id: str, verdict: str) -> dict:
    return {
        "id": row_id,
        "reference_judge": {"verdict": verdict},
        "response_envelope": {"status": "established" if verdict == "exact" else "partially_established"},
    }


def test_score_source_support_adjudication_keeps_raw_and_provisional_scores(tmp_path: Path) -> None:
    fixture = "sample_fixture_001"
    qa_path = tmp_path / "qa" / fixture / "domain_bootstrap_qa_20260528.json"
    qa_path.parent.mkdir(parents=True)
    qa_path.write_text(
        json.dumps(
            {
                "qa_file": str(Path("datasets") / fixture / "qa.md"),
                "rows": [
                    _row("q001", "exact"),
                    _row("q002", "miss"),
                    _row("q003", "partial"),
                ],
            }
        ),
        encoding="utf-8",
    )
    decisions_path = tmp_path / "source_support.json"
    decisions_path.write_text(
        json.dumps(
            {
                "schema_version": "source_support_adjudication_v1",
                "rows": [
                    {
                        "fixture": fixture,
                        "row_id": "q002",
                        "decision": "oracle_overreach",
                        "score_policy": "exclude_from_source_contained_score",
                        "recommended_action": "revise_oracle",
                        "rationale": "Reference requires evidence outside the source package.",
                    },
                    {
                        "fixture": fixture,
                        "row_id": "q003",
                        "decision": "source_contained",
                        "score_policy": "keep_scored",
                        "recommended_action": "keep_as_instrument_signal",
                        "rationale": "Source package contains the requested evidence.",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    report = build_report(qa_roots=(tmp_path / "qa",), adjudication_json=decisions_path)

    assert report["summary"]["raw_counts"] == {"exact": 1, "miss": 1, "partial": 1}
    assert report["summary"]["provisional_source_contained_counts"] == {"exact": 1, "partial": 1}
    assert report["summary"]["excluded_from_source_contained_count"] == 1
    assert report["summary"]["decision_counts"] == {"oracle_overreach": 1, "source_contained": 1}

    markdown = render_markdown(report)
    assert "# Source-Support Adjudication Score" in markdown
    assert "`oracle_overreach`" in markdown


def test_score_source_support_adjudication_reports_missing_decisions(tmp_path: Path) -> None:
    fixture = "sample_fixture_001"
    qa_path = tmp_path / "qa" / fixture / "domain_bootstrap_qa_20260528.json"
    qa_path.parent.mkdir(parents=True)
    qa_path.write_text(
        json.dumps({"qa_file": str(Path("datasets") / fixture / "qa.md"), "rows": [_row("q001", "exact")]}),
        encoding="utf-8",
    )
    decisions_path = tmp_path / "source_support.json"
    decisions_path.write_text(
        json.dumps(
            {
                "schema_version": "source_support_adjudication_v1",
                "rows": [
                    {
                        "fixture": fixture,
                        "row_id": "q099",
                        "decision": "oracle_overreach",
                        "score_policy": "exclude_from_source_contained_score",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    report = build_report(qa_roots=(tmp_path / "qa",), adjudication_json=decisions_path)

    assert report["summary"]["missing_decision_count"] == 1
    assert report["missing_decisions"][0]["row_id"] == "q099"
