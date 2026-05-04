import json
from pathlib import Path

from scripts.stage_incoming_fixtures import stage_fixtures


def _write_fixture(path: Path) -> None:
    path.mkdir(parents=True)
    (path / "source.md").write_text("source text\n", encoding="utf-8")
    (path / "fixture_notes.md").write_text("notes\n", encoding="utf-8")
    rows = [
        json.dumps(
            {
                "id": f"AB-{index:03d}",
                "category": "direct" if index <= 20 else "derived",
                "question": f"Question {index}?",
                "answer": f"Answer {index}.",
            },
            sort_keys=True,
        )
        for index in range(1, 41)
    ]
    (path / "qa.jsonl").write_text("\n".join(rows) + "\n", encoding="utf-8")


def test_stage_incoming_fixtures_splits_questions_and_oracle(tmp_path: Path) -> None:
    fixture = tmp_path / "meridian_permit_board"
    out_root = tmp_path / "staged"
    _write_fixture(fixture)

    report = stage_fixtures(fixture_dirs=[fixture], out_root=out_root)

    staged = out_root / "meridian_permit_board"
    assert report["summary"]["staged_fixture_count"] == 1
    assert (staged / "source.md").exists()
    assert (staged / "qa_authored_with_answers.jsonl").exists()
    qa_md = (staged / "qa.md").read_text(encoding="utf-8")
    oracle = [json.loads(line) for line in (staged / "oracle.jsonl").read_text(encoding="utf-8").splitlines()]
    questions = [json.loads(line) for line in (staged / "qa_questions.jsonl").read_text(encoding="utf-8").splitlines()]

    assert "Answer 1" not in qa_md
    assert "Question 1?" in qa_md
    assert oracle[0]["id"] == "q001"
    assert oracle[0]["source_id"] == "AB-001"
    assert oracle[0]["reference_answer"] == "Answer 1."
    assert "answer" not in questions[0]
    assert questions[0]["question"] == "Question 1?"


def test_stage_incoming_fixtures_fails_without_answers(tmp_path: Path) -> None:
    fixture = tmp_path / "bad_fixture"
    out_root = tmp_path / "staged"
    _write_fixture(fixture)
    rows = [json.loads(line) for line in (fixture / "qa.jsonl").read_text(encoding="utf-8").splitlines()]
    rows[0].pop("answer")
    (fixture / "qa.jsonl").write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")

    report = stage_fixtures(fixture_dirs=[fixture], out_root=out_root)

    assert report["summary"]["failed_fixture_count"] == 1
    assert "qa_rows_missing_answer:AB-001" in report["fixtures"][0]["errors"]


def test_stage_incoming_fixtures_promotes_isolated_markdown_oracle_shape(tmp_path: Path) -> None:
    fixture = tmp_path / "veridia_intake"
    out_root = tmp_path / "story_worlds"
    fixture.mkdir(parents=True)
    (fixture / "turns.md").write_text("# Turns\n\n### Turn 01\nMara spoke.\n", encoding="utf-8")
    (fixture / "qa.md").write_text("q001: Who spoke?\nq002: What format is this?\n", encoding="utf-8")
    (fixture / "oracle.jsonl").write_text(
        "\n".join(
            [
                json.dumps({"id": "q001", "answer": "Mara", "behavior": "commit"}),
                json.dumps({"id": "q002", "answer": "A turnstream", "behavior": "commit"}),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    report = stage_fixtures(fixture_dirs=[fixture], out_root=out_root)

    staged = out_root / "veridia_intake"
    qa_md = (staged / "qa.md").read_text(encoding="utf-8")
    questions = [json.loads(line) for line in (staged / "qa_questions.jsonl").read_text(encoding="utf-8").splitlines()]
    oracle = [json.loads(line) for line in (staged / "oracle.jsonl").read_text(encoding="utf-8").splitlines()]
    metrics = [json.loads(line) for line in (staged / "progress_metrics.jsonl").read_text(encoding="utf-8").splitlines()]

    assert report["summary"]["staged_fixture_count"] == 1
    assert (staged / "source.md").read_text(encoding="utf-8") == (fixture / "turns.md").read_text(encoding="utf-8")
    assert (staged / "story.md").exists()
    assert (staged / "turns.md").exists()
    assert "1. Who spoke?" in qa_md
    assert "Mara" not in qa_md
    assert questions[0]["id"] == "q001"
    assert oracle[1]["reference_answer"] == "A turnstream"
    assert metrics[0]["run_id"] == "VI-000"
    assert metrics[0]["qa_rows"] == 2
