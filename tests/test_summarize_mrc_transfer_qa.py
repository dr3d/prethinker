from __future__ import annotations

from scripts.summarize_mrc_transfer_qa import classify_transfer_coordinate


def test_classify_false_option_coordinate() -> None:
    row = {
        "utterance": "Which statement is NOT true?",
        "reference_answer": "B. The report was filed late.",
        "failure_surface": {"surface": "compile_surface_gap", "rationale": "The KB refutes option B."},
    }

    assert classify_transfer_coordinate(row) == "false_or_exception_option_selection"


def test_classify_formula_coordinate() -> None:
    row = {
        "utterance": "How many minutes should a third grader spend?",
        "reference_answer": "C. No more than thirty minutes.",
        "failure_surface": {"surface": "hybrid_join_gap", "rationale": "The formula is present but not applied."},
    }

    assert classify_transfer_coordinate(row) == "formula_or_rule_application"


def test_classify_title_coordinate() -> None:
    row = {
        "utterance": "What is the best title for this passage?",
        "reference_answer": "A. A Useful Habit",
        "failure_surface": {"surface": "answer_surface_gap", "rationale": "The facts support the theme."},
    }

    assert classify_transfer_coordinate(row) == "title_theme_or_summary_answer"
