from __future__ import annotations

import json
from pathlib import Path

from scripts.sample_mrc_transfer_fixtures import _coerce_race_records, write_race_fixtures
from scripts.stage_incoming_fixtures import stage_fixture


def test_write_race_fixtures_isolates_answer_key(tmp_path: Path) -> None:
    record = {
        "article": "A passage describes a planner, a reviewer, and a final note.",
        "questions": ["Who reviewed the plan?", "Which note was final?"],
        "options": [["The planner", "The reviewer"], ["Draft note", "Final note"]],
        "answers": ["B", "Final note"],
        "example_id": "transfer-demo-001",
    }

    written = write_race_fixtures(
        records=[record],
        out_root=tmp_path / "incoming",
        dataset_name="ehovy/race",
        config_name="high",
        split="validation",
        limit=1,
    )

    fixture = written[0]
    qa_md = (fixture / "qa.md").read_text(encoding="utf-8")
    oracle = [
        json.loads(line)
        for line in (fixture / "oracle.jsonl").read_text(encoding="utf-8").splitlines()
    ]

    assert "Who reviewed the plan?" in qa_md
    assert "B. The reviewer" in qa_md
    assert "correct" not in qa_md.casefold()
    assert "reference_answer" not in qa_md
    assert oracle[0]["id"] == "q001"
    assert oracle[0]["reference_answer"] == "B. The reviewer"
    assert oracle[1]["reference_answer"] == "B. Final note"


def test_sampled_fixture_can_be_staged(tmp_path: Path) -> None:
    record = {
        "article": "The report states one current total and one pending addition.",
        "questions": ["Which total is current?", "Which addition is pending?"],
        "options": [["10", "12"], ["Two units", "Five units"]],
        "answers": ["A", "B"],
        "example_id": "transfer-demo-002",
    }
    incoming = tmp_path / "incoming"
    staged = tmp_path / "staged"
    [fixture] = write_race_fixtures(
        records=[record],
        out_root=incoming,
        dataset_name="ehovy/race",
        config_name="high",
        split="validation",
        limit=1,
    )

    result = stage_fixture(fixture, out_root=staged)

    assert result["qa_rows"] == 2
    qa_md = (staged / fixture.name / "qa.md").read_text(encoding="utf-8")
    oracle = [
        json.loads(line)
        for line in (staged / fixture.name / "oracle.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert "Which total is current?" in qa_md
    assert oracle[0]["reference_answer"] == "A. 10"


def test_coerce_race_question_rows_groups_by_passage() -> None:
    rows = [
        {
            "article": "Shared passage.",
            "question": "First?",
            "options": ["A1", "A2"],
            "answer": "A",
            "example_id": "same-passage",
        },
        {
            "article": "Shared passage.",
            "question": "Second?",
            "options": ["B1", "B2"],
            "answer": "B",
            "example_id": "same-passage",
        },
    ]

    [record] = _coerce_race_records(rows)

    assert record["questions"] == ["First?", "Second?"]
    assert record["answers"] == ["A", "B"]
