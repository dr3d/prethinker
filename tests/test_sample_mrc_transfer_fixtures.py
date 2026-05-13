from __future__ import annotations

import json
from pathlib import Path

from scripts.sample_mrc_transfer_fixtures import (
    _coerce_cuad_records,
    _coerce_maud_records,
    _coerce_privacyqa_records,
    _coerce_race_records,
    _coerce_squad_records,
    _filter_privacyqa_record_ids,
    _select_records,
    write_cuad_fixtures,
    write_maud_fixtures,
    write_privacyqa_fixtures,
    write_race_fixtures,
    write_squad_fixtures,
)
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
    assert "Options: A. The planner B. The reviewer" in qa_md
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
    assert "Which total is current? Options: A. 10 B. 12" in qa_md
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


def test_select_records_evenly_spreads_candidates() -> None:
    records = [{"example_id": f"sample-{index}"} for index in range(10)]

    selected = _select_records(records, limit=4, offset=0, strategy="even", seed=13)

    assert [row["example_id"] for row in selected] == [
        "sample-0",
        "sample-3",
        "sample-6",
        "sample-9",
    ]


def test_coerce_squad_rows_groups_by_context() -> None:
    rows = [
        {
            "id": "s1",
            "title": "Demo",
            "context": "A shared context names a winner and a location.",
            "question": "Who won?",
            "answers": {"text": ["Ari"], "answer_start": [0]},
        },
        {
            "id": "s2",
            "title": "Demo",
            "context": "A shared context names a winner and a location.",
            "question": "Where?",
            "answers": {"text": ["the hall"], "answer_start": [0]},
        },
    ]

    [record] = _coerce_squad_records(rows)

    assert record["questions"] == ["Who won?", "Where?"]
    assert record["answers"] == ["Ari", "the hall"]


def test_write_squad_fixture_can_be_staged(tmp_path: Path) -> None:
    record = {
        "context": "The committee met in the north hall. Mara chaired the meeting.",
        "questions": ["Where did the committee meet?", "Who chaired the meeting?"],
        "answers": ["north hall", "Mara"],
        "question_ids": ["s1", "s2"],
        "title": "Committee",
        "example_id": "s1",
    }
    incoming = tmp_path / "incoming"
    staged = tmp_path / "staged"
    [fixture] = write_squad_fixtures(
        records=[record],
        out_root=incoming,
        dataset_name="squad",
        config_name="default",
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
    assert "Where did the committee meet?" in qa_md
    assert "north hall" not in qa_md
    assert oracle[0]["reference_answer"] == "north hall"


def test_coerce_cuad_records_keeps_answer_centered_excerpts() -> None:
    context = (
        "Intro text. "
        "The agreement is between Alpha LLC and Beta Inc. "
        "More neutral contract words follow for several clauses. "
        "The term ends on December 31, 2030 unless renewed."
    )
    payload = {
        "data": [
            {
                "title": "Demo Contract",
                "paragraphs": [
                    {
                        "context": context,
                        "qas": [
                            {
                                "id": "c1",
                                "question": 'Highlight the parts (if any) of this contract related to "Parties". Details: The parties to the contract',
                                "answers": [
                                    {
                                        "text": "Alpha LLC and Beta Inc.",
                                        "answer_start": context.index("Alpha LLC"),
                                    }
                                ],
                                "is_impossible": False,
                            },
                            {
                                "id": "c2",
                                "question": 'Highlight the parts (if any) of this contract related to "Expiration Date". Details: The date when the contract ends',
                                "answers": [
                                    {
                                        "text": "December 31, 2030",
                                        "answer_start": context.index("December"),
                                    }
                                ],
                                "is_impossible": False,
                            },
                        ],
                    }
                ],
            }
        ]
    }

    [record] = _coerce_cuad_records(
        payload,
        max_questions_per_record=2,
        answer_window=30,
        max_answer_chars=100,
    )

    assert record["title"] == "Demo Contract"
    assert 'What contract text relates to "Parties"?' in record["questions"][0]
    assert record["answers"] == ["Alpha LLC and Beta Inc.", "December 31, 2030"]
    assert "Alpha LLC and Beta Inc." in record["context"]
    assert "December 31, 2030" in record["context"]


def test_write_cuad_fixture_can_be_staged(tmp_path: Path) -> None:
    record = {
        "context": "Contract title: Demo\n\n## Excerpt 1\n\nThe agreement is between Alpha LLC and Beta Inc.",
        "questions": ['What contract text relates to "Parties"? Details: The parties to the contract'],
        "answers": ["Alpha LLC and Beta Inc."],
        "question_ids": ["cuad-1"],
        "categories": ["Parties"],
        "title": "Demo Contract",
        "example_id": "demo-contract",
        "source_span_count": 1,
    }
    incoming = tmp_path / "incoming"
    staged = tmp_path / "staged"
    [fixture] = write_cuad_fixtures(
        records=[record],
        out_root=incoming,
        dataset_name="theatticusproject/cuad",
        config_name="default",
        split="train",
        limit=1,
    )

    result = stage_fixture(fixture, out_root=staged)

    assert result["qa_rows"] == 1
    qa_md = (staged / fixture.name / "qa.md").read_text(encoding="utf-8")
    oracle = [
        json.loads(line)
        for line in (staged / fixture.name / "oracle.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert 'What contract text relates to "Parties"?' in qa_md
    assert "Alpha LLC and Beta Inc." not in qa_md
    assert oracle[0]["reference_answer"] == "Alpha LLC and Beta Inc."


def test_coerce_maud_records_groups_by_contract_and_isolates_answers() -> None:
    rows = [
        {
            "data_type": "main",
            "contract_name": "contract_1",
            "text": "At closing, each share converts into the right to receive â€œcashâ€.",
            "answer": "All Cash",
            "question": "Type of Consideration-Answer",
            "subquestion": "<NONE>",
            "text_type": "Type of Consideration",
            "id": "3",
            "category": "General Information",
        },
        {
            "data_type": "main",
            "contract_name": "contract_1",
            "text": "The agreement includes a matching right period of four business days.",
            "answer": "4 business days",
            "question": "Initial matching rights period (COR)-Answer",
            "subquestion": "<NONE>",
            "text_type": "Agreement provides for matching rights in connection with COR",
            "id": "44",
            "category": "Fiduciary Duties",
        },
    ]

    [record] = _coerce_maud_records(
        rows,
        max_questions_per_record=2,
        max_text_chars=200,
        max_answer_chars=100,
        data_type="main",
    )

    assert record["title"] == "contract_1"
    assert len(record["questions"]) == 2
    assert record["answers"] == ["All Cash", "4 business days"]
    assert '"cash"' in record["context"]
    assert "All Cash" not in record["context"]
    assert "four business days" in record["context"]


def test_write_maud_fixture_can_be_staged(tmp_path: Path) -> None:
    record = {
        "context": "Contract name: contract_1\n\n## Excerpt 1\n\nAt closing, each share converts into cash.",
        "questions": ["What is the answer for: Type of Consideration-Answer Text type: Type of Consideration"],
        "answers": ["All Cash"],
        "question_ids": ["3"],
        "categories": ["General Information"],
        "text_types": ["Type of Consideration"],
        "title": "contract_1",
        "example_id": "contract_1",
        "source_span_count": 1,
    }
    incoming = tmp_path / "incoming"
    staged = tmp_path / "staged"
    [fixture] = write_maud_fixtures(
        records=[record],
        out_root=incoming,
        dataset_name="theatticusproject/maud",
        config_name="default",
        split="dev",
        limit=1,
    )

    result = stage_fixture(fixture, out_root=staged)

    assert result["qa_rows"] == 1
    qa_md = (staged / fixture.name / "qa.md").read_text(encoding="utf-8")
    oracle = [
        json.loads(line)
        for line in (staged / fixture.name / "oracle.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert "Type of Consideration-Answer" in qa_md
    assert "All Cash" not in qa_md
    assert oracle[0]["reference_answer"] == "All Cash"


def test_coerce_privacyqa_records_uses_snippets() -> None:
    rows = [
        {
            "id": "privacy_qa_1",
            "query": "Will my profile be visible to other users?",
            "answer": "Your public profile is visible to other users.",
            "corpus_file": "privacy_qa/Demo.txt",
            "snippets": [
                {
                    "answer": "Your public profile is visible to other users.",
                    "file_path": "privacy_qa/Demo.txt",
                    "span": [10, 55],
                }
            ],
        }
    ]

    [record] = _coerce_privacyqa_records(rows, max_answer_chars=200, max_context_chars=1000)

    assert record["questions"] == ["Will my profile be visible to other users?"]
    assert record["answers"] == ["Your public profile is visible to other users."]
    assert "Your public profile is visible" in record["context"]
    assert "10-55" in record["context"]


def test_filter_privacyqa_record_ids_preserves_requested_order() -> None:
    records = [
        {"example_id": "privacy_qa_1", "questions": ["first"]},
        {"example_id": "privacy_qa_2", "questions": ["second"]},
    ]

    filtered = _filter_privacyqa_record_ids(records, "privacy_qa_2, privacy_qa_1")

    assert [record["example_id"] for record in filtered] == ["privacy_qa_2", "privacy_qa_1"]


def test_write_privacyqa_fixture_can_be_staged(tmp_path: Path) -> None:
    record = {
        "context": "Privacy policy file: Demo\n\n## Snippet 1\n\nYour profile is visible to other users.",
        "questions": ["Will my profile be visible?"],
        "answers": ["Your profile is visible to other users."],
        "question_ids": ["privacy_qa_1"],
        "title": "privacy_qa/Demo.txt",
        "example_id": "privacy_qa_1",
        "source_span_count": 1,
    }
    incoming = tmp_path / "incoming"
    staged = tmp_path / "staged"
    [fixture] = write_privacyqa_fixtures(
        records=[record],
        out_root=incoming,
        dataset_name="amentaphd/legalbench-qa-privacy_qa",
        config_name="default",
        split="train",
        limit=1,
    )

    result = stage_fixture(fixture, out_root=staged)

    assert result["qa_rows"] == 1
    qa_md = (staged / fixture.name / "qa.md").read_text(encoding="utf-8")
    oracle = [
        json.loads(line)
        for line in (staged / fixture.name / "oracle.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert "Will my profile be visible?" in qa_md
    assert "Your profile is visible" not in qa_md
    assert oracle[0]["reference_answer"] == "Your profile is visible to other users."
