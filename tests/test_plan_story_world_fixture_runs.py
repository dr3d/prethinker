from pathlib import Path

from scripts.plan_story_world_fixture_runs import build_plan, render_markdown


def _write_story_fixture(path: Path, *, oracle: bool = True) -> None:
    path.mkdir(parents=True)
    (path / "source.md").write_text("Source text for the compiler.\n", encoding="utf-8")
    (path / "qa.md").write_text("1. What happened?\n\n## Answer Key\n\n1. It happened.\n", encoding="utf-8")
    if oracle:
        (path / "oracle.jsonl").write_text('{"id":"q001","answer":"It happened."}\n', encoding="utf-8")


def test_story_world_run_plan_reads_promoted_fixture_shape(tmp_path: Path) -> None:
    dataset_root = tmp_path / "story_worlds"
    _write_story_fixture(dataset_root / "meridian_permit_board")
    _write_story_fixture(dataset_root / "scratch_without_qa")
    (dataset_root / "scratch_without_qa" / "qa.md").unlink()

    plan = build_plan(
        dataset_root=dataset_root,
        fixture_names=["meridian_permit_board"],
        model="test-model",
        base_url="http://127.0.0.1:1234",
        compile_out_root=tmp_path / "compile",
        qa_out_root=tmp_path / "qa",
        qa_limit=12,
        max_plan_passes=5,
    )

    fixture = plan["fixtures"][0]
    assert plan["summary"]["fixture_count"] == 1
    assert plan["summary"]["missing_requested_fixtures"] == []
    assert "municipal permit rules" in fixture["domain_hint"]
    assert "--compile-flat-plus-plan-passes" in fixture["compile_command"]
    assert "--focused-pass-ops-schema" in fixture["compile_command"]
    assert "--qa-file" in fixture["qa_command_template"]
    assert "--oracle-jsonl" in fixture["qa_command_template"]
    assert "--judge-reference-answers" in fixture["qa_command_template"]
    assert "--evidence-bundle-context-filter" in fixture["qa_command_template"]
    assert "--limit 12" in fixture["qa_command_template"]


def test_story_world_run_plan_can_omit_oracle_and_evidence_bundle(tmp_path: Path) -> None:
    dataset_root = tmp_path / "story_worlds"
    _write_story_fixture(dataset_root / "story_only_fixture", oracle=False)

    plan = build_plan(
        dataset_root=dataset_root,
        fixture_names=[],
        model="test-model",
        base_url="http://127.0.0.1:1234",
        compile_out_root=tmp_path / "compile",
        qa_out_root=tmp_path / "qa",
        qa_limit=3,
        max_plan_passes=2,
        include_evidence_bundle=False,
    )

    fixture = plan["fixtures"][0]
    assert fixture["oracle_jsonl"] is None
    assert "--oracle-jsonl" not in fixture["qa_command_template"]
    assert "--judge-reference-answers" not in fixture["qa_command_template"]
    assert "--evidence-bundle-plan" not in fixture["qa_command_template"]


def test_story_world_run_plan_markdown_lists_commands() -> None:
    markdown = render_markdown(
        {
            "generated_at": "now",
            "summary": {
                "fixture_count": 1,
                "missing_requested_fixtures": [],
                "qa_limit": 5,
                "max_plan_passes": 4,
                "include_evidence_bundle": True,
            },
            "fixtures": [
                {
                    "fixture": "demo",
                    "domain_hint": "demo hint",
                    "source": "datasets/story_worlds/demo/source.md",
                    "qa_file": "datasets/story_worlds/demo/qa.md",
                    "oracle_jsonl": None,
                    "compile_command": "python compile",
                    "qa_command_template": "python qa",
                }
            ],
        }
    )

    assert "# Story-World Fixture Cold Run Plan" in markdown
    assert "python compile" in markdown
    assert "python qa" in markdown
