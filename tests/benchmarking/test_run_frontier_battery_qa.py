from __future__ import annotations

from pathlib import Path

from scripts.benchmarking.run_frontier_battery_qa import (
    _parse_answers,
    build_battery_jobs,
    build_battery_messages,
    expand_jobs_to_rows,
)


def test_battery_prompt_includes_source_once_and_all_questions() -> None:
    messages = build_battery_messages(
        source="Document body.",
        questions=[
            {"id": "q001", "question": "First?", "category": "lookup"},
            {"id": "q002", "question": "Second?", "category": "temporal"},
        ],
    )

    prompt = messages[1]["content"]

    assert prompt.count("Document body.") == 1
    assert "q001: First?" in prompt
    assert "q002: Second?" in prompt
    assert "Return JSON only" in prompt


def test_build_battery_jobs_creates_one_call_per_fixture_run(tmp_path: Path) -> None:
    fixture = tmp_path / "fixture"
    fixture.mkdir()
    (fixture / "source.md").write_text("Document body.", encoding="utf-8")
    (fixture / "qa_questions.jsonl").write_text(
        '{"id":"q001","question":"First?","category":"lookup"}\n'
        '{"id":"q002","question":"Second?","category":"temporal"}\n',
        encoding="utf-8",
    )
    plan = {
        "fixtures": [
            {
                "fixture": "fixture",
                "bucket": "test",
                "dataset_path": str(fixture),
                "source_file": "source.md",
                "question_file": "qa_questions.jsonl",
                "planned_rows": 2,
            }
        ]
    }

    jobs = build_battery_jobs(
        plan,
        model="provider/model",
        provider="provider",
        runs_per_model=3,
        fixture_names=set(),
        limit_fixtures=0,
        limit_questions=0,
        dry_run=True,
    )

    assert len(jobs) == 3
    assert [job["run_index"] for job in jobs] == [1, 2, 3]
    assert len(jobs[0]["questions"]) == 2


def test_build_battery_jobs_filters_by_fixture_name(tmp_path: Path) -> None:
    first = _make_fixture(tmp_path, "first")
    second = _make_fixture(tmp_path, "second")
    plan = {
        "fixtures": [
            {"fixture": "first", "dataset_path": str(first), "planned_rows": 1},
            {"fixture": "second", "dataset_path": str(second), "planned_rows": 1},
        ]
    }

    jobs = build_battery_jobs(
        plan,
        model="provider/model",
        provider="provider",
        runs_per_model=1,
        fixture_names={"second"},
        limit_fixtures=0,
        limit_questions=0,
        dry_run=True,
    )

    assert [job["fixture"] for job in jobs] == ["second"]


def test_parse_answers_accepts_json_object() -> None:
    answers = _parse_answers('{"answers":[{"question_id":"q001","answer":"A"},{"question_id":"q002","answer":"B"}]}')

    assert answers == {"q001": "A", "q002": "B"}


def test_expand_jobs_to_rows_preserves_question_shape() -> None:
    rows = expand_jobs_to_rows(
        [
            {
                "fixture": "fixture",
                "bucket": "bucket",
                "run_index": 1,
                "provider": "provider",
                "model": "model",
                "source_file": "source.md",
                "question_file": "qa_questions.jsonl",
                "questions": [{"id": "q001", "question": "First?", "category": "lookup"}],
                "answers": {"q001": "Answer."},
                "status": "ok",
            }
        ]
    )

    assert rows[0]["schema_version"] == "frontier_battery_qa_row_v1"
    assert rows[0]["question_id"] == "q001"
    assert rows[0]["answer"] == "Answer."
    assert rows[0]["status"] == "ok"


def _make_fixture(root: Path, name: str) -> Path:
    fixture = root / name
    fixture.mkdir()
    (fixture / "source.md").write_text("Document body.", encoding="utf-8")
    (fixture / "qa_questions.jsonl").write_text(
        '{"id":"q001","question":"First?","category":"lookup"}\n',
        encoding="utf-8",
    )
    return fixture
