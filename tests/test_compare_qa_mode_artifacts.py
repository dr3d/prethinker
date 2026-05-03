from scripts.compare_qa_mode_artifacts import build_report, render_markdown


def _record(verdicts: dict[str, str]) -> dict:
    return {
        "rows": [
            {
                "id": row_id,
                "utterance": f"Question {row_id}?",
                "reference_judge": {"verdict": verdict},
            }
            for row_id, verdict in verdicts.items()
        ]
    }


def test_compare_qa_modes_marks_rescues_and_regressions() -> None:
    report = build_report(
        [
            {
                "name": "toy",
                "artifacts": [
                    {"label": "baseline", "path": "baseline.json", "record": _record({"q1": "miss", "q2": "exact"})},
                    {"label": "narrow", "path": "narrow.json", "record": _record({"q1": "exact", "q2": "partial"})},
                    {"label": "broad", "path": "broad.json", "record": _record({"q1": "partial", "q2": "exact"})},
                ],
            }
        ]
    )

    group = report["groups"][0]
    rows = {row["id"]: row for row in group["rows"]}

    assert group["volatile_row_count"] == 2
    assert group["baseline_rescue_count"] == 1
    assert group["baseline_regression_count"] == 1
    assert group["perfect_selector_counts"]["exact"] == 2
    assert rows["q1"]["baseline_rescued"] is True
    assert rows["q2"]["baseline_regressed"] is True


def test_compare_qa_modes_markdown_names_policy() -> None:
    report = build_report(
        [
            {
                "name": "toy",
                "artifacts": [
                    {"label": "baseline", "path": "baseline.json", "record": _record({"q1": "miss"})},
                    {"label": "narrow", "path": "narrow.json", "record": _record({"q1": "exact"})},
                ],
            }
        ]
    )

    markdown = render_markdown(report)

    assert "# Query Surface Mode Comparison" in markdown
    assert "does not read source prose" in markdown
    assert "Diagnostic perfect-selector upper bound" in markdown
