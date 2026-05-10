from __future__ import annotations

from scripts.benchmarking.summarize_mutation_lab_drift import answer_similarity, summarize


def test_answer_similarity_uses_token_f1() -> None:
    assert answer_similarity("Alice owns the red key.", "Alice owns red key.") > 0.8
    assert answer_similarity("Alice owns the red key.", "Bob filed a permit.") < 0.3
    assert answer_similarity("13", "Thirteen") == 1.0


def test_summarize_flags_mutation_drift_against_control() -> None:
    rows = [
        _row("fixture__control", "q001", "Alice owns the red key."),
        _row("fixture__strip_headings", "q001", "Alice owns the red key."),
        _row("fixture__reverse_questions", "q001", "Bob filed a permit."),
    ]
    recipes = {
        "recipes": [
            {
                "synthetic_fixture": "fixture__control",
                "source_fixture": "fixture",
                "mutation_id": "control",
                "mutation_class": "control",
            },
            {
                "synthetic_fixture": "fixture__strip_headings",
                "source_fixture": "fixture",
                "mutation_id": "strip_headings",
                "mutation_class": "source_layout_mangle",
            },
            {
                "synthetic_fixture": "fixture__reverse_questions",
                "source_fixture": "fixture",
                "mutation_id": "reverse_questions",
                "mutation_class": "question_battery_mangle",
            },
        ]
    }

    summary = summarize(rows, recipes=recipes, drift_threshold=0.8)
    model = summary["models"][0]

    assert model["rows"] == 2
    assert model["drift_rows"] == 1
    assert model["fixtures"][0]["name"] == "fixture"
    assert model["mutations"][0]["name"] == "reverse_questions"


def test_summarize_largest_drifts_keeps_zero_similarity() -> None:
    rows = [
        _row("fixture__control", "q001", "Alpha"),
        _row("fixture__control", "q002", "Alice owns the key."),
        _row("fixture__strip_headings", "q001", "Beta"),
        _row("fixture__strip_headings", "q002", "Bob owns the key."),
    ]
    recipes = {
        "recipes": [
            {
                "synthetic_fixture": "fixture__control",
                "source_fixture": "fixture",
                "mutation_id": "control",
                "mutation_class": "control",
            },
            {
                "synthetic_fixture": "fixture__strip_headings",
                "source_fixture": "fixture",
                "mutation_id": "strip_headings",
                "mutation_class": "source_layout_mangle",
            },
        ]
    }

    summary = summarize(rows, recipes=recipes, drift_threshold=0.8)

    assert summary["models"][0]["largest_drifts"][0]["question_id"] == "q001"
    assert summary["models"][0]["largest_drifts"][0]["similarity"] == 0.0


def _row(fixture: str, question_id: str, answer: str) -> dict[str, object]:
    return {
        "model": "model",
        "fixture": fixture,
        "question_id": question_id,
        "category": "lookup",
        "run_index": 1,
        "answer": answer,
    }
