from __future__ import annotations

from pathlib import Path

from scripts.benchmarking.run_frontier_direct_qa import (
    _extract_answer,
    _load_questions,
    build_direct_rows,
    build_messages,
)


def test_build_messages_uses_identical_source_question_template() -> None:
    messages = build_messages(
        source="Alpha source.",
        question="What happened?",
        prompt_contract={
            "system": "Use only source.",
            "user_template": "SOURCE:\n{source}\nQUESTION:\n{question}",
        },
    )

    assert messages == [
        {"role": "system", "content": "Use only source."},
        {"role": "user", "content": "SOURCE:\nAlpha source.\nQUESTION:\nWhat happened?"},
    ]


def test_load_questions_from_jsonl_without_oracle_answers(tmp_path: Path) -> None:
    path = tmp_path / "qa_questions.jsonl"
    path.write_text(
        '{"id":"q001","question":"First?","category":"lookup","reference_answer":"secret"}\n',
        encoding="utf-8",
    )

    rows = _load_questions(path)

    assert rows == [{"id": "q001", "question": "First?", "category": "lookup"}]
    assert "reference_answer" not in rows[0]


def test_build_direct_rows_repeats_runs_and_keeps_oracle_out_of_prompt(tmp_path: Path) -> None:
    fixture = tmp_path / "fixture"
    fixture.mkdir()
    (fixture / "source.md").write_text("Document body.", encoding="utf-8")
    (fixture / "qa_questions.jsonl").write_text(
        '{"id":"q001","question":"Question one?","category":"lookup"}\n'
        '{"id":"q002","question":"Question two?","category":"temporal"}\n',
        encoding="utf-8",
    )
    (fixture / "oracle.jsonl").write_text('{"id":"q001","reference_answer":"Do not read me."}\n', encoding="utf-8")
    plan = {
        "prompt_contract": {
            "system": "Answer only from source.",
            "user_template": "SOURCE DOCUMENT:\n{source}\n\nQUESTION:\n{question}",
        },
        "fixtures": [
            {
                "fixture": "fixture",
                "bucket": "test",
                "dataset_path": str(fixture),
                "source_file": "source.md",
                "question_file": "qa_questions.jsonl",
                "planned_rows": 2,
            }
        ],
    }

    rows = build_direct_rows(
        plan,
        model="provider/model",
        provider="provider",
        runs_per_model=3,
        limit_fixtures=0,
        limit_rows=0,
        dry_run=True,
    )

    assert len(rows) == 6
    assert [row["run_index"] for row in rows[:3]] == [1, 2, 3]
    prompt_text = rows[0]["messages"][1]["content"]
    assert "Document body." in prompt_text
    assert "Question one?" in prompt_text
    assert "Do not read me" not in prompt_text


def test_extract_answer_returns_empty_for_missing_choices() -> None:
    assert _extract_answer({"error": {"message": "quota"}}) == ""
