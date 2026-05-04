from scripts.summarize_rule_activation_transfer import build_report, render_markdown


def test_rule_activation_transfer_summarizes_rescues_and_best_labels() -> None:
    comparison = {
        "label": "toy",
        "path": "toy.json",
        "record": {
            "groups": [
                {
                    "name": "toy_fixture",
                    "baseline_label": "baseline",
                    "labels": ["baseline", "rule"],
                    "row_count": 2,
                    "baseline_rescue_count": 1,
                    "baseline_regression_count": 1,
                    "mode_counts": {
                        "baseline": {"exact": 1, "miss": 1},
                        "rule": {"exact": 1, "miss": 1},
                    },
                    "perfect_selector_counts": {"exact": 2},
                    "rows": [
                        {
                            "id": "q1",
                            "question": "Q1?",
                            "baseline_rescued": True,
                            "baseline_regressed": False,
                            "volatile": True,
                            "best_verdict": "exact",
                            "best_labels": ["rule"],
                            "verdicts": {"baseline": "miss", "rule": "exact"},
                        },
                        {
                            "id": "q2",
                            "question": "Q2?",
                            "baseline_rescued": False,
                            "baseline_regressed": True,
                            "volatile": True,
                            "best_verdict": "exact",
                            "best_labels": ["baseline"],
                            "verdicts": {"baseline": "exact", "rule": "miss"},
                        },
                    ],
                }
            ]
        },
    }

    selector = {
        "label": "toy_selector",
        "path": "selector.json",
        "record": {
            "group": {"name": "toy_fixture"},
            "rows": [
                {"id": "q1", "selected_mode": "rule", "selected_verdict": "exact"},
                {"id": "q2", "selected_mode": "rule", "selected_verdict": "miss"},
            ],
        },
    }

    report = build_report(comparisons=[comparison], selectors=[selector], label="toy_transfer")

    assert report["aggregate"]["row_count"] == 2
    assert report["aggregate"]["baseline_rescue_count"] == 1
    assert report["aggregate"]["baseline_regression_count"] == 1
    assert report["aggregate"]["best_label_counts"] == {"rule": 1, "baseline": 1}
    assert report["aggregate"]["activation_governor_counts"] == {
        "activate_nonbaseline_rescue": 1,
        "protect_baseline_exact": 1,
    }
    assert report["aggregate"]["selector_governor_compliance_counts"] == {
        "activate_nonbaseline_rescue_pass": 1,
        "protect_baseline_exact_fail": 1,
    }
    assert report["aggregate"]["semantic_progress"]["recommended_action"] == "continue_only_with_named_expected_contribution"
    assert len(report["frontier_rows"]) == 2
    assert report["frontier_rows"][0]["signals"] == ["baseline_rescued", "volatile"]
    assert report["frontier_rows"][0]["activation_governor_target"]["target"] == "activate_nonbaseline_rescue"
    assert report["frontier_rows"][1]["activation_governor_target"]["target"] == "protect_baseline_exact"
    assert report["frontier_rows"][1]["selector_governor_compliance"]["compliant"] is False


def test_rule_activation_transfer_markdown_states_policy() -> None:
    report = build_report(comparisons=[], label="empty")

    markdown = render_markdown(report)

    assert "# Rule Activation Transfer Summary" in markdown
    assert "does not read source prose" in markdown
    assert "Activation governor targets" in markdown
    assert "Selector governor compliance" in markdown
    assert "## Frontier Rows" in markdown

    report_with_miss = {
        "fixtures": [
            {
                "name": "toy",
                "selector_governor_audit": {
                    "misses": [
                        {
                            "id": "q1",
                            "target": "protect_baseline_exact",
                            "selected_mode": "rule",
                            "selected_verdict": "miss",
                            "best_labels": ["baseline"],
                        }
                    ]
                },
            }
        ],
        "aggregate": {},
        "frontier_rows": [],
    }

    markdown = render_markdown(report_with_miss)

    assert "## Selector Governor Misses" in markdown
    assert "protect_baseline_exact" in markdown


def test_rule_activation_transfer_marks_stable_rows_as_any_mode() -> None:
    comparison = {
        "label": "toy",
        "path": "toy.json",
        "record": {
            "groups": [
                {
                    "name": "toy_fixture",
                    "baseline_label": "baseline",
                    "labels": ["baseline", "rule"],
                    "row_count": 1,
                    "baseline_rescue_count": 0,
                    "baseline_regression_count": 0,
                    "rows": [
                        {
                            "id": "q1",
                            "best_labels": ["baseline", "rule"],
                            "verdicts": {"baseline": "partial", "rule": "partial"},
                            "volatile": False,
                        }
                    ],
                }
            ]
        },
    }

    report = build_report(comparisons=[comparison], label="toy_transfer")

    assert report["fixtures"][0]["activation_governor_counts"] == {"stable_any_mode": 1}
