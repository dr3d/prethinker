from scripts.autolab_queue_wildbench_pilot import build_job_markdown


def test_wildbench_pilot_job_has_bounded_contract() -> None:
    markdown = build_job_markdown(job_id="wild_demo", candidate_count=2, qa_rows=12)

    assert "job_id: wild_demo" in markdown
    assert "Do not edit tracked repo files" in markdown
    assert "Do not run Prethinker heavy compiles" in markdown
    assert "Do not call the desktop heavy LM Studio endpoint" in markdown
    assert "python scripts/validate_autolab_candidate_artifacts.py" in markdown
    assert "wildbench_pilot_summary.md" in markdown


def test_wildbench_pilot_job_uses_candidate_and_qa_schema_names() -> None:
    markdown = build_job_markdown(job_id="wild_demo", candidate_count=3, qa_rows=15)

    assert "autolab_source_candidate_v1" in markdown
    assert "autolab_candidate_qa_v1" in markdown
    assert "Write exactly 15 QA rows per candidate" in markdown
    assert "candidate_001" in markdown
    assert "candidate_002" in markdown
    assert "source_candidate.json" in markdown
    assert "qa_candidate.json" in markdown


def test_wildbench_source_only_job_omits_qa_work() -> None:
    markdown = build_job_markdown(job_id="wild_demo", candidate_count=1, qa_rows=10, source_only=True)

    assert "role: autolab_source_hunter" in markdown
    assert "candidate_001" in markdown
    assert "candidate_002" not in markdown
    assert "source_candidate.json" in markdown
    assert "qa_candidate.json" not in markdown
    assert "should not draft QA yet" in markdown
