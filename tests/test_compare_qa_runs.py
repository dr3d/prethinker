from scripts.compare_qa_runs import compare_qa_runs, render_markdown


def _batch(fixture: str, exact: int, partial: int, miss: int) -> dict:
    return {
        "results": [
            {
                "fixture": fixture,
                "summary": {
                    "judge_exact": exact,
                    "judge_partial": partial,
                    "judge_miss": miss,
                },
            }
        ]
    }


def _multi_batch(rows: list[tuple[str, int, int, int]]) -> dict:
    return {
        "results": [
            {
                "fixture": fixture,
                "summary": {
                    "judge_exact": exact,
                    "judge_partial": partial,
                    "judge_miss": miss,
                },
            }
            for fixture, exact, partial, miss in rows
        ]
    }


def _run_rows(fixture: str, rows: list[tuple[str, str, str, list[str]]]) -> dict:
    return {
        "fixture": fixture,
        "summary": {
            "judge_exact": sum(1 for _, verdict, _, _ in rows if verdict == "exact"),
            "judge_partial": sum(1 for _, verdict, _, _ in rows if verdict == "partial"),
            "judge_miss": sum(1 for _, verdict, _, _ in rows if verdict == "miss"),
        },
        "rows": [
            {
                "id": row_id,
                "utterance": f"Question {row_id}?",
                "reference_answer": "Reference",
                "reference_judge": {"verdict": verdict, "concise_answer": "note"},
                "failure_surface": {"surface": surface},
                "query_results": [
                    {"result": {"predicate": predicate, "rows": [{"x": "y"}]}}
                    for predicate in predicates
                ],
            }
            for row_id, verdict, surface, predicates in rows
        ],
    }


def test_compare_qa_runs_marks_promotable_when_exact_holds_and_miss_drops() -> None:
    payload = compare_qa_runs(_batch("fixture_a", 24, 4, 12), _batch("fixture_a", 27, 5, 8))

    row = payload["comparisons"][0]
    assert row["promotion_status"] == "promotable"
    assert row["delta"] == {"exact": 3, "partial": 1, "miss": -4}


def test_compare_qa_runs_marks_regression_when_exact_drops_or_miss_rises() -> None:
    payload = compare_qa_runs(_batch("fixture_a", 34, 2, 3), _batch("fixture_a", 33, 3, 4))

    row = payload["comparisons"][0]
    assert row["promotion_status"] == "regression"
    assert row["delta"] == {"exact": -1, "partial": 1, "miss": 1}


def test_compare_qa_runs_reports_aggregate_delta() -> None:
    baseline = _multi_batch(
        [
            ("fixture_a", 10, 1, 4),
            ("fixture_b", 8, 2, 5),
        ]
    )
    candidate = _multi_batch(
        [
            ("fixture_a", 12, 0, 3),
            ("fixture_b", 7, 4, 4),
        ]
    )

    payload = compare_qa_runs(baseline, candidate)

    assert payload["aggregate"] == {
        "baseline": {"exact": 18, "partial": 3, "miss": 9},
        "candidate": {"exact": 19, "partial": 4, "miss": 7},
        "delta": {"exact": 1, "partial": 1, "miss": -2},
        "promotion_status": "promotable",
    }
    assert payload["summary"]["aggregate_promotion_status"] == "promotable"
    assert payload["summary"]["aggregate_delta"] == {"exact": 1, "partial": 1, "miss": -2}


def test_compare_qa_runs_reports_row_level_churn_and_added_support_surfaces() -> None:
    baseline = _run_rows(
        "fixture_a",
        [
            ("q001", "exact", "not_applicable", ["direct_fact"]),
            ("q002", "miss", "compile_surface_gap", ["direct_fact"]),
            ("q003", "partial", "query_surface_gap", ["source_record_old_support"]),
        ],
    )
    candidate = _run_rows(
        "fixture_a",
        [
            ("q001", "miss", "query_surface_gap", ["direct_fact", "source_record_new_support"]),
            ("q002", "exact", "not_applicable", ["direct_fact", "source_record_new_support"]),
            ("q003", "partial", "query_surface_gap", ["source_record_old_support"]),
        ],
    )

    payload = compare_qa_runs(baseline, candidate)

    assert payload["summary"]["row_change_count"] == 2
    assert payload["summary"]["row_improvement_count"] == 1
    assert payload["summary"]["row_regression_count"] == 1
    assert payload["summary"]["baseline_exact_regression_count"] == 1
    assert payload["summary"]["baseline_exact_to_miss_count"] == 1
    assert payload["regression_guard"] == {
        "schema_version": "qa_regression_guard_v1",
        "status": "fail",
        "rule": "Previously exact rows must remain exact before a candidate run is promoted.",
        "baseline_exact_regression_count": 1,
        "baseline_exact_to_miss_count": 1,
    }
    assert payload["row_changes"]["summary"]["regression_with_added_support_count"] == 1
    assert payload["row_changes"]["summary"]["regression_with_added_helper_count"] == 1
    regression = [
        row
        for row in payload["row_changes"]["changes"]
        if row["id"] == "q001"
    ][0]
    assert regression["movement"] == "regressed"
    assert regression["added_support_predicates"] == ["source_record_new_support"]
    assert regression["added_support_surface_classes"] == {
        "source_record_new_support": "current_source_record_summary"
    }
    assert regression["added_helper_predicates"] == ["source_record_new_support"]


def test_compare_qa_runs_regression_guard_passes_when_exact_rows_hold() -> None:
    baseline = _run_rows(
        "fixture_a",
        [
            ("q001", "exact", "not_applicable", ["direct_fact"]),
            ("q002", "miss", "compile_surface_gap", ["direct_fact"]),
        ],
    )
    candidate = _run_rows(
        "fixture_a",
        [
            ("q001", "exact", "not_applicable", ["direct_fact"]),
            ("q002", "exact", "not_applicable", ["direct_fact", "source_record_new_support"]),
        ],
    )

    payload = compare_qa_runs(baseline, candidate)

    assert payload["regression_guard"]["status"] == "pass"
    assert payload["regression_guard"]["baseline_exact_regression_count"] == 0


def test_compare_qa_runs_markdown_uses_support_surface_language() -> None:
    baseline = _run_rows("fixture_a", [("q001", "exact", "not_applicable", ["direct_fact"])])
    candidate = _run_rows(
        "fixture_a",
        [("q001", "miss", "query_surface_gap", ["direct_fact", "source_record_new_support"])],
    )

    markdown = render_markdown(compare_qa_runs(baseline, candidate))

    assert "Added Support Surfaces" in markdown
    assert "helper" not in markdown.casefold()
