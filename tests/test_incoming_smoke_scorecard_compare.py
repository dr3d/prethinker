from scripts.compare_incoming_smoke_scorecards import build_comparison, render_markdown


def _scorecard(
    *,
    exact: int,
    partial: int,
    miss: int,
    failed: int = 0,
    writes: int = 0,
    non_exact_rows: list[dict] | None = None,
) -> dict:
    qa_rows = exact + partial + miss
    return {
        "summary": {
            "fixture_count": 1,
            "compiled_count": 1 - failed,
            "compile_failed_count": failed,
            "qa_rows": qa_rows,
            "exact_rows": exact,
            "partial_rows": partial,
            "miss_rows": miss,
            "exact_rate": round(exact / qa_rows, 4) if qa_rows else None,
            "failure_surface_counts": {"compile_surface_gap": partial + miss},
            "semantic_progress_risk_counts": {"low": 1 - failed, "medium": failed},
            "write_proposal_rows": writes,
        },
        "fixtures": [
            {
                "fixture": "alpha",
                "compile_status": "compiled" if not failed else "compile_parse_failed",
                "compile_health": "healthy",
                "semantic_progress_risk": "low" if not failed else "medium",
                "profile_fallback": "",
                "judge_counts": {"exact": exact, "partial": partial, "miss": miss},
                "non_exact_rows": non_exact_rows or [],
            }
        ],
    }


def test_scorecard_compare_promotes_exact_gain_without_miss_growth() -> None:
    report = build_comparison(_scorecard(exact=8, partial=2, miss=0), _scorecard(exact=9, partial=1, miss=0))

    assert report["summary"]["delta"]["exact_rows"] == 1
    assert report["summary"]["delta"]["miss_rows"] == 0
    assert report["summary"]["promotion_recommendation"] == "promote_candidate"
    assert report["fixtures"][0]["delta"] == {"exact": 1, "partial": -1, "miss": 0}


def test_scorecard_compare_rejects_miss_growth_even_with_exact_gain() -> None:
    report = build_comparison(_scorecard(exact=8, partial=2, miss=0), _scorecard(exact=9, partial=0, miss=1))

    assert report["summary"]["promotion_recommendation"] == "reject_candidate"
    assert report["summary"]["delta"]["failure_surface_counts"] == {"compile_surface_gap": -1}


def test_scorecard_compare_rejects_compile_or_write_regression() -> None:
    compile_report = build_comparison(_scorecard(exact=8, partial=2, miss=0), _scorecard(exact=9, partial=1, miss=0, failed=1))
    write_report = build_comparison(_scorecard(exact=8, partial=2, miss=0), _scorecard(exact=9, partial=1, miss=0, writes=1))

    assert compile_report["summary"]["promotion_recommendation"] == "reject_candidate"
    assert write_report["summary"]["promotion_recommendation"] == "reject_candidate"


def test_scorecard_compare_marks_neutral_candidate_as_mixed() -> None:
    report = build_comparison(_scorecard(exact=8, partial=2, miss=0), _scorecard(exact=8, partial=2, miss=0))
    markdown = render_markdown(report)

    assert report["summary"]["promotion_recommendation"] == "mixed_candidate"
    assert "Failure-surface deltas" in markdown
    assert "`alpha`" in markdown


def test_scorecard_compare_requires_row_gate_for_baseline_exact_regression() -> None:
    baseline = _scorecard(exact=8, partial=2, miss=0, non_exact_rows=[{"id": "q001", "verdict": "partial"}])
    candidate = _scorecard(
        exact=9,
        partial=1,
        miss=0,
        non_exact_rows=[{"id": "q010", "verdict": "partial", "question": "Regressed row?"}],
    )

    report = build_comparison(baseline, candidate)
    markdown = render_markdown(report)

    assert report["summary"]["delta"]["baseline_exact_regression_rows"] == 1
    assert report["summary"]["promotion_recommendation"] == "row_level_gate_required"
    assert report["baseline_exact_regressions"][0]["id"] == "q010"
    assert "Baseline-Exact Regressions" in markdown
