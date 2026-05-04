from scripts.rollup_incoming_smoke_scorecard import build_scorecard, render_markdown


def test_incoming_smoke_scorecard_rolls_up_fixture_counts() -> None:
    reports = [
        {
            "fixture": "alpha",
            "summary": {
                "compile_status": "compiled",
                "profile_fallback": "signature_roster",
                "compile_parsed_ok": True,
                "compile_admitted": 10,
                "compile_skipped": 2,
                "compile_health": "warning",
                "semantic_progress_risk": "low",
                "semantic_progress_action": "continue",
                "qa_rows": 3,
                "judge_counts": {"exact": 2, "partial": 1},
                "failure_surface_counts": {"compile_surface_gap": 1},
                "write_proposal_rows": 0,
            },
            "non_exact_rows": [{"id": "q003"}],
        },
        {
            "fixture": "beta",
            "summary": {
                "compile_status": "compile_parse_failed",
                "compile_parsed_ok": False,
                "compile_parse_error": "bad json",
                "qa_rows": 0,
                "judge_counts": {},
                "failure_surface_counts": {},
                "write_proposal_rows": 0,
            },
            "non_exact_rows": [],
        },
    ]

    scorecard = build_scorecard(reports)

    assert scorecard["summary"]["fixture_count"] == 2
    assert scorecard["summary"]["compiled_count"] == 1
    assert scorecard["summary"]["compile_failed_count"] == 1
    assert scorecard["summary"]["qa_rows"] == 3
    assert scorecard["summary"]["exact_rate"] == 0.6667
    assert scorecard["summary"]["failure_surface_counts"] == {"compile_surface_gap": 1}
    assert scorecard["fixtures"][0]["profile_fallback"] == "signature_roster"


def test_incoming_smoke_scorecard_markdown_lists_fixture_rows() -> None:
    scorecard = build_scorecard(
        [
            {
                "fixture": "alpha",
                "summary": {
                    "compile_status": "compiled",
                    "profile_fallback": "signature_roster",
                    "compile_health": "healthy",
                    "semantic_progress_risk": "low",
                    "qa_rows": 1,
                    "judge_counts": {"exact": 1},
                    "failure_surface_counts": {},
                    "write_proposal_rows": 0,
                },
            }
        ]
    )

    markdown = render_markdown(scorecard)

    assert "# Incoming Fixture Smoke Scorecard" in markdown
    assert "`alpha`" in markdown
    assert "signature_roster" in markdown
    assert "Exact / partial / miss" in markdown
