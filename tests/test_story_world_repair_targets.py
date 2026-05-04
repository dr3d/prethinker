from scripts.plan_story_world_repair_targets import build_repair_plan, render_markdown


def test_story_world_repair_plan_uses_query_predicates_for_lenses() -> None:
    scorecard = {
        "fixtures": [
            {
                "fixture": "larkspur",
                "non_exact_rows": [
                    {
                        "id": "q011",
                        "question": "What state?",
                        "verdict": "miss",
                        "failure_surface": "compile_surface_gap",
                        "queries": ["initial_state(pearlescent_loom, X)."],
                    },
                    {
                        "id": "q034",
                        "question": "When?",
                        "verdict": "partial",
                        "failure_surface": "hybrid_join_gap",
                        "queries": ["rule_threshold(lr_7_3, reply_deadline_from_response, Z, CalendarDays)."],
                    },
                ],
            }
        ]
    }

    report = build_repair_plan(scorecard)

    assert report["summary"]["target_count"] == 2
    assert report["summary"]["acquisition_lens_counts"] == {
        "object_state_transition_surface": 1,
        "rule_threshold_surface": 1,
    }
    assert report["targets"][0]["acquisition_lens"] == "object_state_transition_surface"
    assert report["targets"][0]["repair_lane"] == "scoped_source_surface_repair"
    assert report["targets"][1]["repair_lane"] == "helper_or_query_join_repair"


def test_story_world_repair_plan_can_filter_fixture() -> None:
    scorecard = {
        "fixtures": [
            {
                "fixture": "alpha",
                "non_exact_rows": [{"id": "q001", "verdict": "miss", "queries": ["person_role(X, Y)."]}],
            },
            {
                "fixture": "beta",
                "non_exact_rows": [{"id": "q002", "verdict": "miss", "queries": ["deadline(X, Y, Z, active)."]}],
            },
        ]
    }

    report = build_repair_plan(scorecard, fixture_filter={"beta"})

    assert report["summary"]["fixture_counts"] == {"beta": 1}
    assert report["targets"][0]["acquisition_lens"] == "temporal_deadline_surface"


def test_story_world_repair_markdown_lists_lens_counts() -> None:
    report = build_repair_plan(
        {
            "fixtures": [
                {
                    "fixture": "alpha",
                    "non_exact_rows": [
                        {
                            "id": "q001",
                            "question": "Who?",
                            "verdict": "partial",
                            "failure_surface": "compile_surface_gap",
                            "queries": ["person_role(X, reviewer)."],
                        }
                    ],
                }
            ]
        }
    )

    markdown = render_markdown(report)

    assert "# Story-World Repair Targets" in markdown
    assert "`identity_role_roster_surface`" in markdown
    assert "Predicate Hints" in markdown
