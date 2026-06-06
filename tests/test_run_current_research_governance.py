from pathlib import Path

from scripts.run_current_research_governance import governance_commands, report_md


def test_governance_commands_include_current_claim_checks(tmp_path: Path) -> None:
    commands = governance_commands(out_root=tmp_path / "out", include_pytest=False)

    assert [command["id"] for command in commands] == [
        "sign_clean",
        "research_artifact_paths",
        "historical_score_claims",
        "domain_predicate_schema",
        "domain_pack_status",
        "domain_pack_variance_status",
        "domain_accountability_status",
        "fixture_bank_domain_inventory",
        "domain_predicate_proposal_status",
        "pending_external_work_orders",
        "query_micro_fixture_contracts",
        "query_grounding_status",
        "candidate_oracle_reviews",
        "source_oracle_reviews",
        "sec_value_axis_integrity",
        "fda_violation_alignment",
        "domain_omission_accountability_audit",
        "compile_fact_qa_exclusions",
        "compile_fact_qa_manifest_sources",
        "reference_judge_null_control_reports",
        "compile_fact_qa_manifest",
        "current_compile_fact_qa_status",
    ]
    pending_command = next(command for command in commands if command["id"] == "pending_external_work_orders")
    assert "--expect-md" in pending_command["command"]
    assert "--include-tmp-zips" not in pending_command["command"]
    assert "docs/PENDING_EXTERNAL_WORK_ORDERS.md" in pending_command["command"]
    query_contract_command = next(command for command in commands if command["id"] == "query_micro_fixture_contracts")
    assert "--expect-md" in query_contract_command["command"]
    assert "docs/QUERY_MICRO_FIXTURE_CONTRACT_STATUS.md" in query_contract_command["command"]
    query_status_command = next(command for command in commands if command["id"] == "query_grounding_status")
    assert "--expect-md" in query_status_command["command"]
    assert "docs/QUERY_GROUNDING_STATUS.md" in query_status_command["command"]
    review_command = next(command for command in commands if command["id"] == "candidate_oracle_reviews")
    assert "--expect-md" in review_command["command"]
    assert "docs/CANDIDATE_ORACLE_REVIEW_STATUS.md" in review_command["command"]
    source_review_command = next(command for command in commands if command["id"] == "source_oracle_reviews")
    assert "--expect-md" in source_review_command["command"]
    assert "docs/SOURCE_ORACLE_REVIEW_STATUS.md" in source_review_command["command"]
    fda_alignment_command = next(command for command in commands if command["id"] == "fda_violation_alignment")
    assert "--expect-md" in fda_alignment_command["command"]
    assert "docs/FDA_VIOLATION_ALIGNMENT_STATUS.md" in fda_alignment_command["command"]
    omission_command = next(command for command in commands if command["id"] == "domain_omission_accountability_audit")
    assert "audit_domain_omission_accountability.py" in omission_command["command"][1]
    assert "--compile-json" in omission_command["command"]
    status_command = next(command for command in commands if command["id"] == "current_compile_fact_qa_status")
    assert "--exclusion-audit" in status_command["command"]
    assert any("compile_fact_qa_exclusions.json" in item for item in status_command["command"])


def test_governance_commands_can_include_pytest(tmp_path: Path) -> None:
    commands = governance_commands(out_root=tmp_path / "out", include_pytest=True)

    assert commands[-1]["id"] == "pytest"
    assert commands[-1]["command"][-4:] == ["-m", "pytest", "-q", "tests"]


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
