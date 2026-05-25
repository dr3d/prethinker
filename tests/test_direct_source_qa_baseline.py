import json
import sys
from pathlib import Path

from scripts.run_direct_source_qa_baseline import (
    cache_key_for_job,
    load_jobs,
    parse_args,
    summarize,
)


def test_load_jobs_uses_source_questions_and_oracle(tmp_path: Path) -> None:
    fixture = tmp_path / "fixture_a"
    fixture.mkdir()
    (fixture / "source.md").write_text("Source body.", encoding="utf-8")
    (fixture / "qa.md").write_text("# QA\n\n1. What is named?\n2. What is missing?\n", encoding="utf-8")
    (fixture / "oracle.jsonl").write_text(
        "\n".join(
            [
                json.dumps({"id": "q001", "reference_answer": "Alpha"}),
                json.dumps({"id": "q002", "reference_answer": "Not stated"}),
            ]
        ),
        encoding="utf-8",
    )

    jobs = load_jobs(tmp_path, [], set(), 0)

    assert [job["id"] for job in jobs] == ["q001", "q002"]
    assert jobs[0]["fixture"] == "fixture_a"
    assert jobs[0]["source_text"] == "Source body."
    assert jobs[1]["reference_answer"] == "Not stated"


def test_cache_key_changes_when_reference_or_prompt_version_changes() -> None:
    job = {
        "fixture": "fixture_a",
        "source_hash": "abc",
        "id": "q001",
        "utterance": "What is named?",
        "reference_answer": "Alpha",
    }

    first = cache_key_for_job(
        job,
        model="model-a",
        base_url="https://openrouter.ai/api/v1",
        answer_prompt_version="answer-v1",
        judge_prompt_version="judge-v1",
    )
    second = cache_key_for_job(
        {**job, "reference_answer": "Beta"},
        model="model-a",
        base_url="https://openrouter.ai/api/v1",
        answer_prompt_version="answer-v1",
        judge_prompt_version="judge-v1",
    )
    third = cache_key_for_job(
        job,
        model="model-a",
        base_url="https://openrouter.ai/api/v1",
        answer_prompt_version="answer-v2",
        judge_prompt_version="judge-v1",
    )

    assert first != second
    assert first != third


def test_parse_args_defaults_to_local_lmstudio(monkeypatch) -> None:
    monkeypatch.delenv("PRETHINKER_BASE_URL", raising=False)
    monkeypatch.setattr(sys, "argv", ["run_direct_source_qa_baseline.py"])

    args = parse_args()

    assert args.base_url == "http://127.0.0.1:1234"


def test_summarize_counts_fixture_verdicts() -> None:
    rows = [
        {"fixture": "a", "ok": True, "reference_judge": {"verdict": "exact"}},
        {"fixture": "a", "ok": True, "reference_judge": {"verdict": "partial"}},
        {"fixture": "b", "ok": False, "error": "boom", "reference_judge": {"verdict": "miss"}},
    ]

    summary = summarize(rows, elapsed_ms=123)

    assert summary["question_count"] == 3
    assert summary["ok_rows"] == 2
    assert summary["error_rows"] == 1
    assert summary["judge_exact"] == 1
    assert summary["judge_partial"] == 1
    assert summary["judge_miss"] == 1
    assert summary["by_fixture"]["a"]["question_count"] == 2
    assert summary["by_fixture"]["b"]["errors"] == 1
