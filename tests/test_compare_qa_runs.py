from scripts.compare_qa_runs import compare_qa_runs


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
