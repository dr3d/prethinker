from __future__ import annotations

from scripts.benchmarking.extract_mutation_drift_triage import extract_rows


def test_extract_rows_selects_mutation_and_question_controls() -> None:
    summary = {
        "drift_rows": [
            _row("international_dates", "q001"),
            _row("strip_headings", "q025"),
            _row("strip_headings", "q040"),
        ]
    }

    rows = extract_rows(summary, mutations={"international_dates"}, question_ids={"q025"})

    assert [(row["mutation_id"], row["question_id"]) for row in rows] == [
        ("international_dates", "q001"),
        ("strip_headings", "q025"),
    ]
    assert rows[0]["triage_label"] == ""
    assert "reference_answer" in rows[0]


def _row(mutation_id: str, question_id: str) -> dict[str, object]:
    return {
        "model": "model",
        "source_fixture": "fixture",
        "mutation_id": mutation_id,
        "question_id": question_id,
        "category": "lookup",
        "similarity": 0.5,
        "control_answer": "A",
        "mutated_answer": "B",
    }
