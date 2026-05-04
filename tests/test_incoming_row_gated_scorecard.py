from scripts.plan_incoming_row_gated_scorecard import build_report, render_markdown


def _scorecard(exact: int, partial: int, miss: int) -> dict:
    return {"summary": {"exact_rows": exact, "partial_rows": partial, "miss_rows": miss, "qa_rows": exact + partial + miss}}


def _overlay(fixtures: list[dict]) -> dict:
    return {"fixtures": fixtures}


def test_row_gated_scorecard_applies_accepted_rows_and_rejects_regressions() -> None:
    report = build_report(
        baseline=_scorecard(44, 4, 2),
        candidate=_scorecard(45, 4, 1),
        overlay=_overlay(
            [
                {
                    "fixture": "alpha",
                    "recommended_policy": "row_level_selector_required",
                    "accepted_candidate_rows": [
                        {"id": "q001", "baseline_verdict": "miss", "candidate_verdict": "exact"},
                        {"id": "q002", "baseline_verdict": "partial", "candidate_verdict": "exact"},
                        {"id": "q003", "baseline_verdict": "miss", "candidate_verdict": "partial"},
                    ],
                    "rejected_candidate_rows": [
                        {"id": "q004", "baseline_verdict": "exact", "candidate_verdict": "miss"}
                    ],
                    "unchanged_non_exact_rows": [],
                }
            ]
        ),
    )

    assert report["summary"]["row_gated_counts"] == {"exact": 46, "miss": 0, "partial": 4}
    assert report["summary"]["delta_vs_baseline"] == {"exact": 2, "miss": -2, "partial": 0}
    assert report["summary"]["recommendation"] == "row_gated_overlay_required"


def test_row_gated_scorecard_promotes_clean_overlay_candidate() -> None:
    report = build_report(
        baseline=_scorecard(8, 1, 1),
        candidate=_scorecard(9, 1, 0),
        overlay=_overlay(
            [
                {
                    "fixture": "alpha",
                    "recommended_policy": "accept_candidate_row_overlays",
                    "accepted_candidate_rows": [{"id": "q001", "baseline_verdict": "miss", "candidate_verdict": "exact"}],
                    "rejected_candidate_rows": [],
                    "unchanged_non_exact_rows": [],
                }
            ]
        ),
    )

    assert report["summary"]["row_gated_counts"] == {"exact": 9, "miss": 0, "partial": 1}
    assert report["summary"]["recommendation"] == "row_gated_overlay_candidate"


def test_row_gated_scorecard_markdown_lists_accepted_and_rejected_rows() -> None:
    report = build_report(
        baseline=_scorecard(1, 0, 1),
        candidate=_scorecard(1, 0, 1),
        overlay=_overlay(
            [
                {
                    "fixture": "alpha",
                    "recommended_policy": "row_level_selector_required",
                    "accepted_candidate_rows": [
                        {
                            "id": "q001",
                            "baseline_verdict": "miss",
                            "candidate_verdict": "exact",
                            "question": "Rescue?",
                        }
                    ],
                    "rejected_candidate_rows": [
                        {
                            "id": "q002",
                            "baseline_verdict": "exact",
                            "candidate_verdict": "miss",
                            "question": "Regression?",
                        }
                    ],
                    "unchanged_non_exact_rows": [],
                }
            ]
        ),
    )
    markdown = render_markdown(report)

    assert "# Incoming Row-Gated Scorecard Plan" in markdown
    assert "Rescue?" in markdown
    assert "Regression?" in markdown

