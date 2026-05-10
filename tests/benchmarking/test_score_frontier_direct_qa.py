from __future__ import annotations

import json
from pathlib import Path

from scripts.benchmarking.score_frontier_direct_qa import (
    _extract_first_json_object,
    _load_oracle_for_row,
    _normalize_judge_json,
    _summarize,
    build_judge_payload,
    score_row,
)


def test_build_judge_payload_compares_model_answer_to_reference() -> None:
    payload = build_judge_payload(
        row={
            "fixture": "fixture",
            "question_id": "q001",
            "category": "lookup",
            "question": "What is current?",
            "answer": "It is active.",
        },
        oracle={"reference_answer": "It is active.", "category": "lookup"},
    )

    assert payload["model_answer"] == "It is active."
    assert payload["reference_answer"] == "It is active."
    assert any("unsupported completion" in item for item in payload["verdict_policy"])


def test_load_oracle_for_row_uses_source_parent_oracle(tmp_path: Path) -> None:
    fixture = tmp_path / "fixture"
    fixture.mkdir()
    source = fixture / "source.md"
    source.write_text("Source.", encoding="utf-8")
    (fixture / "oracle.jsonl").write_text(
        '{"id":"q001","reference_answer":"Answer one.","category":"lookup"}\n',
        encoding="utf-8",
    )

    oracle = _load_oracle_for_row({"source_file": str(source), "question_id": "q001"})

    assert oracle["reference_answer"] == "Answer one."


def test_score_row_dry_run_attaches_judge_payload(tmp_path: Path) -> None:
    fixture = tmp_path / "fixture"
    fixture.mkdir()
    source = fixture / "source.md"
    source.write_text("Source.", encoding="utf-8")
    (fixture / "oracle.jsonl").write_text(
        json.dumps({"id": "q001", "reference_answer": "Answer one.", "category": "lookup"}) + "\n",
        encoding="utf-8",
    )

    row = score_row(
        {
            "fixture": "fixture",
            "question_id": "q001",
            "question": "Question?",
            "answer": "Answer one.",
            "source_file": str(source),
        },
        judge_model="judge/model",
        judge_base_url="http://127.0.0.1:1234/v1",
        judge_api_key="",
        timeout=1,
        max_tokens=100,
        dry_run=True,
    )

    assert row["reference_answer"] == "Answer one."
    assert row["reference_judge"]["verdict"] == "not_judged"
    assert row["reference_judge"]["judge_payload"]["model_answer"] == "Answer one."


def test_summarize_counts_verdicts() -> None:
    summary = _summarize(
        [
            {"reference_judge": {"verdict": "exact"}},
            {"reference_judge": {"verdict": "partial"}},
            {"reference_judge": {"verdict": "miss"}},
        ]
    )

    assert summary["rows"] == 3
    assert summary["verdict_counts"] == {"exact": 1, "miss": 1, "partial": 1}
    assert summary["exact_rate"] == 0.3333


def test_extract_first_json_object_accepts_fenced_json_with_trailing_text() -> None:
    parsed = _extract_first_json_object('```json\n{"verdict":"exact"}\n```\nextra')

    assert parsed == {"verdict": "exact"}


def test_normalize_judge_json_clamps_bad_verdict() -> None:
    judge = _normalize_judge_json({"verdict": "maybe", "issues": ["x"]})

    assert judge["schema_version"] == "direct_qa_judge_v1"
    assert judge["verdict"] == "not_judged"
    assert judge["issues"] == ["x"]
