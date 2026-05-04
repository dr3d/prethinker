from scripts.plan_incoming_row_mode_overlay import build_overlay_plan, render_markdown


def _scorecard(non_exact_rows: list[dict]) -> dict:
    return {
        "fixtures": [
            {
                "fixture": "alpha",
                "non_exact_rows": non_exact_rows,
            }
        ]
    }


def test_row_mode_overlay_accepts_candidate_exact_rescue() -> None:
    baseline = _scorecard([{"id": "q001", "verdict": "partial", "question": "Q?"}])
    candidate = _scorecard([])

    report = build_overlay_plan(baseline, candidate)

    assert report["summary"]["accepted_candidate_row_count"] == 1
    assert report["summary"]["rejected_candidate_row_count"] == 0
    assert report["summary"]["recommended_policy"] == "accept_candidate_row_overlays"
    assert report["fixtures"][0]["accepted_candidate_rows"][0]["candidate_verdict"] == "exact"


def test_row_mode_overlay_rejects_candidate_regression() -> None:
    baseline = _scorecard([])
    candidate = _scorecard([{"id": "q001", "verdict": "miss", "question": "Q?"}])

    report = build_overlay_plan(baseline, candidate)

    assert report["summary"]["accepted_candidate_row_count"] == 0
    assert report["summary"]["rejected_candidate_row_count"] == 1
    assert report["summary"]["recommended_policy"] == "keep_baseline_for_rejected_rows"


def test_row_mode_overlay_requires_selector_for_mixed_rows() -> None:
    baseline = _scorecard(
        [
            {"id": "q001", "verdict": "partial", "question": "Q1?"},
            {"id": "q002", "verdict": "partial", "question": "Q2?"},
        ]
    )
    candidate = _scorecard([{"id": "q002", "verdict": "miss", "question": "Q2?"}])

    report = build_overlay_plan(baseline, candidate)
    markdown = render_markdown(report)

    assert report["summary"]["accepted_candidate_row_count"] == 1
    assert report["summary"]["rejected_candidate_row_count"] == 1
    assert report["summary"]["recommended_policy"] == "row_level_selector_required"
    assert "`alpha`" in markdown
