from scripts.plan_incoming_fixture_runs import build_plan, render_markdown


def test_incoming_fixture_run_plan_uses_staged_questions_and_oracle() -> None:
    manifest = {
        "fixtures": [
            {
                "fixture": "meridian_permit_board",
                "status": "staged",
                "source": "tmp/incoming_staged/meridian_permit_board/source.md",
                "qa_file": "tmp/incoming_staged/meridian_permit_board/qa.md",
                "oracle_jsonl": "tmp/incoming_staged/meridian_permit_board/oracle.jsonl",
                "categories": {"direct_fact": 15, "rule_derived": 15, "conflict_exception": 10},
            }
        ]
    }

    plan = build_plan(
        manifest=manifest,
        model="test-model",
        base_url="http://127.0.0.1:1234",
        compile_out_root=__import__("pathlib").Path("tmp/compile"),
        qa_out_root=__import__("pathlib").Path("tmp/qa"),
        qa_limit=5,
        max_plan_passes=4,
    )

    fixture = plan["fixtures"][0]
    assert plan["summary"]["fixture_count"] == 1
    assert "municipal permit rules" in fixture["domain_hint"]
    assert "--compile-flat-plus-plan-passes" in fixture["compile_command"]
    assert "--focused-pass-ops-schema" in fixture["compile_command"]
    assert "--qa-file tmp\\incoming_staged\\meridian_permit_board\\qa.md" in fixture["qa_command_template"]
    assert "--oracle-jsonl tmp\\incoming_staged\\meridian_permit_board\\oracle.jsonl" in fixture["qa_command_template"]
    assert "--limit 5" in fixture["qa_command_template"]


def test_incoming_fixture_run_plan_markdown_lists_commands() -> None:
    plan = {
        "generated_at": "now",
        "summary": {"fixture_count": 1, "qa_limit": 5, "max_plan_passes": 4, "category_counts": {}},
        "fixtures": [
            {
                "fixture": "demo",
                "domain_hint": "demo hint",
                "challenge_categories": {"direct": 1},
                "compile_command": "python compile",
                "qa_command_template": "python qa",
            }
        ],
    }

    markdown = render_markdown(plan)

    assert "# Incoming Fixture Cold Run Plan" in markdown
    assert "python compile" in markdown
    assert "python qa" in markdown
