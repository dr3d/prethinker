from src.semantic_struggle import assess_semantic_progress


def test_semantic_progress_assessment_continues_when_surface_is_fresh() -> None:
    assessment = assess_semantic_progress(
        surface_contribution=[
            {"pass_id": "p1", "unique_contribution_count": 12, "duplicate_count": 1, "health_flags": []},
            {"pass_id": "p2", "unique_contribution_count": 5, "duplicate_count": 0, "health_flags": []},
        ]
    )

    assert assessment["zombie_risk"] == "low"
    assert assessment["recommended_action"] == "continue"
    assert assessment["semantic_progress_delta"]["unique_contribution_total"] == 17
    assert assessment["semantic_progress_delta"]["stale_tail_count"] == 0


def test_semantic_progress_assessment_stops_on_repeated_stale_tail() -> None:
    assessment = assess_semantic_progress(
        surface_contribution=[
            {"pass_id": "p1", "unique_contribution_count": 8, "duplicate_count": 0, "health_flags": []},
            {"pass_id": "p2", "unique_contribution_count": 0, "duplicate_count": 4, "health_flags": ["no_unique_surface"]},
            {"pass_id": "p3", "unique_contribution_count": 0, "duplicate_count": 0, "health_flags": ["zero_yield"]},
        ]
    )

    assert assessment["zombie_risk"] == "high"
    assert assessment["recommended_action"] == "stop_and_report_struggle"
    assert "repeated_stale_pass_tail" in assessment["stop_reasons"]
    assert assessment["semantic_progress_delta"]["recent_unique_contribution_count"] == 0


def test_semantic_progress_assessment_requires_named_contribution_on_caution() -> None:
    assessment = assess_semantic_progress(
        surface_contribution=[
            {"pass_id": "p1", "unique_contribution_count": 2, "duplicate_count": 7, "health_flags": ["thin_surface"]},
            {"pass_id": "p2", "unique_contribution_count": 2, "duplicate_count": 7, "health_flags": ["thin_surface"]},
        ],
        selector_governor_counts={"protect_baseline_exact_pass": 3, "protect_baseline_exact_fail": 1},
    )

    assert assessment["zombie_risk"] == "medium"
    assert assessment["recommended_action"] == "continue_only_with_named_expected_contribution"
    assert "high_duplicate_surface_ratio" in assessment["caution_reasons"]
    assert "thin_surface" in assessment["caution_reasons"]
    assert "selector_governor_failures_present" in assessment["caution_reasons"]
    assert assessment["selector_governor"]["fail_count"] == 1


def test_semantic_progress_assessment_treats_single_skip_heavy_as_caution() -> None:
    assessment = assess_semantic_progress(
        surface_contribution=[
            {"pass_id": "p1", "unique_contribution_count": 20, "duplicate_count": 0, "health_flags": []},
            {"pass_id": "p2", "unique_contribution_count": 6, "duplicate_count": 1, "health_flags": ["skip_heavy"]},
        ]
    )

    assert assessment["zombie_risk"] == "medium"
    assert assessment["recommended_action"] == "continue_only_with_named_expected_contribution"
    assert "skip_heavy_pass_present" in assessment["caution_reasons"]
    assert assessment["stop_reasons"] == []
