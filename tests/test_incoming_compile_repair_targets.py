from scripts.plan_incoming_compile_repair_targets import build_repair_plan, render_markdown


def test_compile_repair_plan_prioritizes_surfaces_and_selector_status() -> None:
    scorecard = {
        "fixtures": [
            {
                "fixture": "alpha",
                "non_exact_rows": [
                    {
                        "id": "q001",
                        "question": "Q1?",
                        "verdict": "partial",
                        "failure_surface": "compile_surface_gap",
                    },
                    {
                        "id": "q002",
                        "question": "Q2?",
                        "verdict": "miss",
                        "failure_surface": "hybrid_join_gap",
                    },
                ],
            }
        ]
    }
    overlay = {
        "fixtures": [
            {
                "fixture": "alpha",
                "accepted_candidate_rows": [{"id": "q001"}],
                "unchanged_non_exact_rows": [{"id": "q002"}],
            }
        ]
    }

    report = build_repair_plan(scorecard, row_overlay=overlay)

    assert report["summary"]["target_count"] == 2
    assert report["targets"][0]["selector_status"] == "candidate_rescue"
    assert report["targets"][0]["repair_lane"] == "row_selector_calibration"
    assert report["targets"][1]["repair_lane"] == "helper_or_query_join_repair"


def test_compile_repair_plan_markdown_lists_targets() -> None:
    report = build_repair_plan(
        {
            "fixtures": [
                {
                    "fixture": "alpha",
                    "non_exact_rows": [
                        {
                            "id": "q001",
                            "question": "Q?",
                            "verdict": "miss",
                            "failure_surface": "query_surface_gap",
                        }
                    ],
                }
            ]
        }
    )

    markdown = render_markdown(report)

    assert "# Incoming Compile Repair Targets" in markdown
    assert "`query_planner_repair`" in markdown
    assert "`alpha`" in markdown
