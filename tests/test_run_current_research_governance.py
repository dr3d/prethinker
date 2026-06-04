from pathlib import Path

from scripts.run_current_research_governance import governance_commands, report_md


def test_governance_commands_include_current_claim_checks(tmp_path: Path) -> None:
    commands = governance_commands(out_root=tmp_path / "out", include_pytest=False)

    assert [command["id"] for command in commands] == [
        "sign_clean",
        "research_artifact_paths",
        "historical_score_claims",
        "domain_predicate_schema",
        "compile_fact_qa_manifest",
    ]


def test_governance_commands_can_include_pytest(tmp_path: Path) -> None:
    commands = governance_commands(out_root=tmp_path / "out", include_pytest=True)

    assert commands[-1]["id"] == "pytest"
    assert commands[-1]["command"][-3:] == ["-m", "pytest", "-q"]


def test_report_md_marks_failures() -> None:
    md = report_md(
        {
            "summary": {"status": "fail", "command_count": 2, "failed_count": 1},
            "commands": [
                {"id": "a", "returncode": 0},
                {"id": "b", "returncode": 2},
            ],
        }
    )

    assert "Status: `fail`" in md
    assert "| `a` | `pass` |" in md
    assert "| `b` | `fail (2)` |" in md
