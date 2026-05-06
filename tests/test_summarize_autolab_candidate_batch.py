import json
from pathlib import Path

from scripts.summarize_autolab_candidate_batch import build_report, render_markdown


def test_summarize_autolab_candidate_batch_reads_nested_artifacts(tmp_path: Path) -> None:
    candidate = tmp_path / "run" / "candidate_001"
    candidate.mkdir(parents=True)
    (candidate / "source_candidate.json").write_text(
        json.dumps(
            {
                "schema_version": "autolab_source_candidate_v1",
                "candidate_id": "sparse_minutes",
                "source_url": "https://example.test/minutes",
                "domain_label": "governance",
                "why_it_is_hard": ["temporal_status", "absence"],
                "expected_sparse_score": "medium",
                "source_text_path": "tmp/hermes_mailbox/runs/demo/candidate_001/source.md",
                "do_not_use_reason": "",
            }
        ),
        encoding="utf-8",
    )
    rows = [
        {
            "qid": "q001",
            "question": "What is established?",
            "surface_family": "absence",
            "expected_answer_mode": "not_established",
            "why_this_is_hard": "Sparse record.",
        }
    ]
    (candidate / "qa_candidate.json").write_text(
        json.dumps({"schema_version": "autolab_candidate_qa_v1", "source_candidate_id": "sparse_minutes", "rows": rows}),
        encoding="utf-8",
    )
    (tmp_path / "run" / "candidate_validation.json").write_text(
        json.dumps(
            {
                "schema_version": "autolab_candidate_artifact_validation_v1",
                "summary": {"passed_artifact_count": 2, "warning_artifact_count": 0, "failed_artifact_count": 0},
            }
        ),
        encoding="utf-8",
    )

    report = build_report(root=tmp_path / "run")
    markdown = render_markdown(report)

    assert report["summary"]["source_candidate_count"] == 1
    assert report["summary"]["qa_candidate_count"] == 1
    assert report["summary"]["validation_report_count"] == 1
    assert report["summary"]["hard_surface_counts"]["absence"] == 1
    assert "sparse_minutes" in markdown
    assert "https://example.test/minutes" in markdown
