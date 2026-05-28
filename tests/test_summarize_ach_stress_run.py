import json

from scripts.summarize_ach_stress_run import render_markdown, summarize_ach_stress_run


def test_summarize_ach_stress_run_scores_targets(tmp_path) -> None:
    dataset = tmp_path / "dataset"
    run_dir = tmp_path / "run"
    dataset.mkdir()
    run_dir.mkdir()

    _write_fixture(dataset, fixture_id="high_case", target="high", pivotal="e1")
    _write_fixture(dataset, fixture_id="low_case", target="low", pivotal=None)
    _write_report(run_dir, "high-case", top=["h1"], sensitivity=["e1"], contract_violations=0)
    _write_report(run_dir, "low-case", top=["h1"], sensitivity=[], contract_violations=1)

    summary = summarize_ach_stress_run(dataset_root=dataset, run_dir=run_dir)

    assert summary["aggregate"]["fixture_count"] == 2
    assert summary["aggregate"]["ranking_correct_count"] == 2
    assert summary["aggregate"]["high_pivotal_detected_count"] == 1
    assert summary["aggregate"]["low_clean_count"] == 1
    assert summary["aggregate"]["contract_residual_fixture_count"] == 1
    assert summary["fixtures"][0]["sensitivity_alignment"] == "pivotal_detected"
    assert "# ACH Stress Run Summary" in render_markdown(summary)


def test_summarize_ach_stress_run_flags_wrong_high_sensitivity(tmp_path) -> None:
    dataset = tmp_path / "dataset"
    run_dir = tmp_path / "run"
    dataset.mkdir()
    run_dir.mkdir()

    _write_fixture(dataset, fixture_id="high_case", target="high", pivotal="e1")
    _write_report(run_dir, "high-case", top=["h1"], sensitivity=["e2"], contract_violations=0)

    summary = summarize_ach_stress_run(dataset_root=dataset, run_dir=run_dir)

    assert summary["fixtures"][0]["sensitivity_alignment"] == "wrong_or_partial_sensitivity"
    assert summary["aggregate"]["high_pivotal_detected_count"] == 0


def test_summarize_ach_stress_run_reports_pivotal_support_share(tmp_path) -> None:
    dataset = tmp_path / "dataset"
    run_dir = tmp_path / "run"
    dataset.mkdir()
    run_dir.mkdir()

    _write_fixture(dataset, fixture_id="high_case", target="high", pivotal="e2")
    _write_report(
        run_dir,
        "high-case",
        top=["h1"],
        sensitivity=[],
        contract_violations=0,
        judgments=[
            {"evidence_id": "e1", "hypothesis_id": "h1", "assessment": "consistent", "weight": 3},
            {"evidence_id": "e2", "hypothesis_id": "h1", "assessment": "consistent", "weight": 1},
            {"evidence_id": "e1", "hypothesis_id": "h2", "assessment": "neutral", "weight": 1},
            {"evidence_id": "e2", "hypothesis_id": "h2", "assessment": "neutral", "weight": 1},
        ],
    )

    summary = summarize_ach_stress_run(dataset_root=dataset, run_dir=run_dir)

    assert summary["fixtures"][0]["top_support_evidence_ids"] == ["e1", "e2"]
    assert summary["fixtures"][0]["expected_pivotal_support_rank"] == 2
    assert summary["fixtures"][0]["expected_pivotal_support_share"] == 0.25
    assert summary["fixtures"][0]["expected_pivotal_evidence_role"] == ""


def _write_fixture(root, *, fixture_id: str, target: str, pivotal: str | None) -> None:
    fixture = root / fixture_id
    fixture.mkdir()
    (fixture / "metadata.json").write_text(
        json.dumps({"fixture_id": fixture_id, "sensitivity_target": target, "domain": "test"}),
        encoding="utf-8",
    )
    (fixture / "ach_payload.json").write_text(
        json.dumps(
            {
                "fixture_id": fixture_id,
                "ach_question": "Which hypothesis wins?",
                "hypotheses": [{"id": "h1"}, {"id": "h2"}],
                "evidence_rows": [{"id": "e1"}, {"id": "e2"}],
                "expected_read": {
                    "best_hypothesis": "h1",
                    "sensitivity_expectation": target,
                    "pivotal_evidence": pivotal,
                },
            }
        ),
        encoding="utf-8",
    )


def _write_report(
    run_dir,
    slug: str,
    *,
    top: list[str],
    sensitivity: list[str],
    contract_violations: int,
    judgments: list[dict] | None = None,
) -> None:
    (run_dir / f"{slug}_ach_payload_proposal.json").write_text(
        json.dumps(
            {
                "summary": {
                    "top_hypotheses": top,
                    "matrix_complete": True,
                    "warning_count": 0,
                    "sensitivity_evidence_ids": sensitivity,
                    "proposal_contract_violation_count": contract_violations,
                    "proposal_contract_retry_count": 2,
                    "question_axis": "cause",
                },
                "scorer_payload": {
                    "evidence": [{"id": "e1", "label": "One"}, {"id": "e2", "label": "Two"}],
                    "judgments": judgments or [],
                },
            }
        ),
        encoding="utf-8",
    )
