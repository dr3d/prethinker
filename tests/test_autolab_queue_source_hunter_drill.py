import pytest

from scripts.autolab_queue_source_hunter_drill import build_job_markdown


def test_blocked_report_drill_requires_validation_report() -> None:
    markdown = build_job_markdown(job_id="blocked_drill", drill="blocked_report")

    assert "role: autolab_source_hunter_drill" in markdown
    assert "source_hunt_blocked.json" in markdown
    assert "autolab_source_hunt_blocked_v1" in markdown
    assert "required_validation_report: tmp/autolab_mailbox/runs/blocked_drill/candidate_validation.json" in markdown
    assert "Do not merely describe files in stdout" in markdown


def test_static_source_drill_writes_candidate_shape() -> None:
    markdown = build_job_markdown(job_id="static_drill", drill="static_source")

    assert "candidate_001/source.md" in markdown
    assert "source_candidate.json" in markdown
    assert "autolab_source_candidate_v1" in markdown
    assert "static_drill_source_001" in markdown
    assert "candidate_count` set to `1`" in markdown


def test_source_hunter_drill_rejects_unknown_drill() -> None:
    with pytest.raises(ValueError):
        build_job_markdown(job_id="bad_drill", drill="unknown")
