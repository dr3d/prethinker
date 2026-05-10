from __future__ import annotations

import json
from pathlib import Path

from scripts.benchmarking.build_public_benchmark_manifest import _fixture_manifest, _render_markdown, _summarize


def test_fixture_manifest_marks_ready_scored_fixture(tmp_path: Path) -> None:
    fixture = tmp_path / "sample_fixture"
    fixture.mkdir()
    (fixture / "source.md").write_text("source text\n", encoding="utf-8")
    (fixture / "qa_questions.jsonl").write_text('{"id":"q001","question":"One?"}\n', encoding="utf-8")
    (fixture / "oracle.jsonl").write_text('{"id":"q001","answer":"A"}\n', encoding="utf-8")
    (fixture / "progress_metrics.jsonl").write_text(
        json.dumps(
            {
                "run_id": "SF-001",
                "mode": "cold_unseen",
                "compile": {"admitted_ops": 12, "signature_recall": 0.5},
                "qa_first20": {"judge_exact": 1, "judge_partial": 0, "judge_miss": 0},
            }
        )
        + "\n",
        encoding="utf-8",
    )

    row = _fixture_manifest(fixture)

    assert row["publication_status"] == "ready_with_scored_history"
    assert row["source_file"] == "source.md"
    assert row["question_count"] == 1
    assert row["oracle_count"] == 1
    assert row["latest_progress"]["run_id"] == "SF-001"
    assert row["latest_progress"]["qa_exact"] == 1


def test_fixture_manifest_reports_missing_oracle(tmp_path: Path) -> None:
    fixture = tmp_path / "missing_oracle"
    fixture.mkdir()
    (fixture / "story.md").write_text("story text\n", encoding="utf-8")
    (fixture / "qa.md").write_text("- What happened?\n", encoding="utf-8")

    row = _fixture_manifest(fixture)

    assert row["publication_status"] == "needs_scoring_oracle"
    assert row["source_file"] == "story.md"
    assert row["question_count"] == 1


def test_fixture_manifest_reads_flat_progress_counts(tmp_path: Path) -> None:
    fixture = tmp_path / "flat_progress"
    fixture.mkdir()
    (fixture / "source.md").write_text("source text\n", encoding="utf-8")
    (fixture / "qa_questions.jsonl").write_text('{"id":"q001","question":"One?"}\n', encoding="utf-8")
    (fixture / "oracle.jsonl").write_text('{"id":"q001","answer":"A"}\n', encoding="utf-8")
    (fixture / "progress_metrics.jsonl").write_text(
        json.dumps(
            {
                "lane": "registry_probe",
                "ts": "2026-05-09T00:00:00Z",
                "exact": 8,
                "partial": 1,
                "miss": 1,
            }
        )
        + "\n",
        encoding="utf-8",
    )

    row = _fixture_manifest(fixture)

    assert row["latest_progress"]["run_id"] == "registry_probe"
    assert row["latest_progress"]["qa_scope"] == "flat"
    assert row["latest_progress"]["qa_exact"] == 8
    assert row["latest_progress"]["qa_exact_rate"] == 0.8


def test_summary_and_markdown_include_status_counts() -> None:
    fixtures = [
        {
            "fixture": "ready",
            "publication_status": "ready_with_scored_history",
            "source_file": "source.md",
            "question_count": 2,
            "oracle_count": 2,
            "private_answer_count": 0,
            "progress_metric_rows": 1,
            "latest_progress": {"qa_exact": 1, "qa_partial": 1, "qa_miss": 0},
        },
        {
            "fixture": "needs",
            "publication_status": "needs_scoring_oracle",
            "source_file": "source.md",
            "question_count": 1,
            "oracle_count": 0,
            "private_answer_count": 0,
            "progress_metric_rows": 0,
            "latest_progress": {},
        },
    ]
    summary = _summarize(fixtures)
    markdown = _render_markdown(
        {
            "generated_utc": "2026-05-09T00:00:00+00:00",
            "dataset_root": "datasets/story_worlds",
            "fixture_count": 2,
            "summary": summary,
            "fixtures": fixtures,
        }
    )

    assert summary["total_question_rows"] == 3
    assert summary["publication_status_counts"]["ready_with_scored_history"] == 1
    assert "`1 / 1 / 0`" in markdown
    assert "`needs_scoring_oracle`: `1`" in markdown
