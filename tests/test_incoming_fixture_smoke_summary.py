from pathlib import Path

from scripts.summarize_incoming_fixture_smoke import build_report, render_markdown


def test_incoming_fixture_smoke_summary_merges_qa_rows_and_failures(tmp_path: Path) -> None:
    compile_record = {
        "source_compile": {
            "admitted_count": 12,
            "skipped_count": 3,
            "compile_health": {
                "verdict": "warning",
                "semantic_progress": {
                    "zombie_risk": "medium",
                    "recommended_action": "continue_only_with_named_expected_contribution",
                },
            },
            "surface_contribution": [
                {"pass_id": "flat", "unique_contribution_count": 10, "duplicate_count": 0, "health_flags": []}
            ],
        }
    }
    qa_base = {
        "rows": [
            {
                "id": "q001",
                "utterance": "Question 1?",
                "reference_answer": "Answer 1",
                "reference_judge": {"verdict": "exact"},
                "failure_surface": {"surface": "not_applicable"},
            },
            {
                "id": "q002",
                "utterance": "Question 2?",
                "reference_answer": "Answer 2",
                "reference_judge": {"verdict": "miss"},
                "queries": ["fact(X)."],
            },
        ]
    }
    qa_failure = {
        "rows": [
            {
                "id": "q002",
                "failure_surface": {"surface": "compile_surface_gap"},
            }
        ]
    }

    report = build_report(
        fixture="demo",
        compile_record=compile_record,
        qa_records=[qa_base, qa_failure],
        compile_path=tmp_path / "compile.json",
        qa_paths=[tmp_path / "qa.json", tmp_path / "failure.json"],
    )

    assert report["summary"]["compile_admitted"] == 12
    assert report["summary"]["compile_status"] == "compiled"
    assert report["summary"]["profile_fallback"] == ""
    assert report["summary"]["compile_parsed_ok"] is True
    assert report["summary"]["judge_counts"] == {"exact": 1, "miss": 1}
    assert report["summary"]["failure_surface_counts"] == {"compile_surface_gap": 1}
    assert report["non_exact_rows"][0]["id"] == "q002"
    assert report["non_exact_rows"][0]["failure_surface"] == "compile_surface_gap"


def test_incoming_fixture_smoke_summary_markdown_lists_non_exact_rows() -> None:
    report = {
        "fixture": "demo",
        "generated_at": "now",
        "summary": {
            "compile_admitted": 1,
            "compile_skipped": 0,
            "compile_health": "healthy",
            "semantic_progress_risk": "low",
            "semantic_progress_action": "continue",
            "qa_rows": 1,
            "judge_counts": {"partial": 1},
            "failure_surface_counts": {"hybrid_join_gap": 1},
            "write_proposal_rows": 0,
        },
        "surface_contribution": [],
        "non_exact_rows": [{"id": "q001", "verdict": "partial", "failure_surface": "hybrid_join_gap", "question": "Q?"}],
    }

    markdown = render_markdown(report)

    assert "# Incoming Fixture Smoke Summary: demo" in markdown
    assert "hybrid_join_gap" in markdown
    assert "q001" in markdown


def test_incoming_fixture_smoke_summary_counts_unclassified_non_exacts() -> None:
    report = build_report(
        fixture="demo",
        compile_record={"source_compile": {"admitted_count": 1}},
        qa_records=[
            {
                "rows": [
                    {
                        "id": "q001",
                        "utterance": "Question?",
                        "reference_judge": {"verdict": "partial"},
                    }
                ]
            }
        ],
    )

    assert report["summary"]["failure_surface_counts"] == {"unclassified": 1}
    assert report["non_exact_rows"][0]["failure_surface"] == "unclassified"


def test_incoming_fixture_smoke_summary_allows_compile_only_failure() -> None:
    report = build_report(
        fixture="failed",
        compile_record={"parsed_ok": False, "parse_error": "bad json"},
        qa_records=[],
    )

    assert report["summary"]["compile_parsed_ok"] is False
    assert report["summary"]["compile_status"] == "compile_parse_failed"
    assert report["summary"]["compile_parse_error"] == "bad json"
    assert report["summary"]["qa_rows"] == 0
    assert report["summary"]["judge_counts"] == {}


def test_incoming_fixture_smoke_summary_reports_signature_roster_fallback() -> None:
    report = build_report(
        fixture="fallback",
        compile_record={
            "profile_signature_roster_retry": {"parsed_ok": True},
            "source_compile": {"admitted_count": 1, "skipped_count": 0},
        },
        qa_records=[],
    )

    assert report["summary"]["profile_fallback"] == "signature_roster"
