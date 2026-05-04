from scripts.plan_incoming_compile_variant_overlay import build_report, render_markdown


def _scorecard(exact: int, partial: int, miss: int, fixtures: list[dict]) -> dict:
    return {
        "summary": {
            "exact_rows": exact,
            "partial_rows": partial,
            "miss_rows": miss,
            "qa_rows": exact + partial + miss,
        },
        "fixtures": fixtures,
    }


def _fixture(name: str, rows: list[dict]) -> dict:
    verdict_counts = {"exact": 10 - len(rows)}
    for row in rows:
        verdict_counts[row["verdict"]] = verdict_counts.get(row["verdict"], 0) + 1
    return {"fixture": name, "judge_counts": verdict_counts, "non_exact_rows": rows, "qa_rows": 10}


def test_compile_variant_overlay_accepts_complementary_rows_and_protects_exact_rows() -> None:
    baseline = _scorecard(
        8,
        2,
        0,
        [
            _fixture(
                "alpha",
                [
                    {"id": "q001", "verdict": "partial", "question": "First?"},
                    {"id": "q002", "verdict": "partial", "question": "Second?"},
                ],
            )
        ],
    )
    candidate = _scorecard(
        8,
        2,
        0,
        [
            _fixture(
                "alpha",
                [
                    {"id": "q002", "verdict": "partial", "question": "Second?"},
                    {"id": "q003", "verdict": "partial", "question": "Third?"},
                ],
            )
        ],
    )

    report = build_report(baseline=baseline, candidates=[("candidate", candidate, None)])

    assert report["summary"]["overlay_counts"] == {"exact": 9, "partial": 1, "miss": 0}
    assert report["summary"]["delta_vs_baseline"] == {"exact": 1, "partial": -1, "miss": 0}
    assert report["summary"]["accepted_variant_row_count"] == 1
    assert report["summary"]["protected_baseline_exact_row_count"] == 1
    assert report["fixtures"][0]["accepted_variant_rows"][0]["id"] == "q001"
    assert report["fixtures"][0]["protected_baseline_exact_rows"][0]["id"] == "q003"


def test_compile_variant_overlay_markdown_labels_upper_bound() -> None:
    baseline = _scorecard(1, 1, 0, [_fixture("alpha", [{"id": "q001", "verdict": "partial", "question": "Rescue?"}])])
    candidate = _scorecard(2, 0, 0, [_fixture("alpha", [])])

    markdown = render_markdown(build_report(baseline=baseline, candidates=[("candidate", candidate, None)]))

    assert "judged-artifact diagnostic upper bound" in markdown
    assert "Rescue?" in markdown
    assert "candidate" in markdown
