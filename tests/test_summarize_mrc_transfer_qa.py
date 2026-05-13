from __future__ import annotations

from scripts.summarize_mrc_transfer_qa import classify_proposition_type, classify_transfer_coordinate


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


def test_classify_factual_proposition_type() -> None:
    row = {
        "utterance": "Where did the committee meet?",
        "reference_answer": "B. The town hall.",
        "failure_surface": {"surface": "compile_surface_gap", "rationale": "The meeting location is explicit."},
    }

    assert classify_proposition_type(row) == "factual"


def test_classify_comparative_proposition_type() -> None:
    row = {
        "utterance": "Which group had the fewest completed forms?",
        "reference_answer": "C. The morning group.",
        "failure_surface": {"surface": "hybrid_join_gap", "rationale": "The counts need comparison."},
    }

    assert classify_proposition_type(row) == "comparative"


def test_classify_categorical_proposition_type() -> None:
    row = {
        "utterance": "What kind of document is the attachment?",
        "reference_answer": "A. A policy notice.",
        "failure_surface": {"surface": "answer_surface_gap", "rationale": "The source describes its role."},
    }

    assert classify_proposition_type(row) == "categorical"


def test_classify_synthesis_proposition_type() -> None:
    row = {
        "utterance": "What is the best title for this passage?",
        "reference_answer": "A. A Useful Habit",
        "failure_surface": {"surface": "answer_surface_gap", "rationale": "The facts support the theme."},
    }

    assert classify_proposition_type(row) == "synthesis"


def test_classify_inference_proposition_type() -> None:
    row = {
        "utterance": "Why did the speaker leave early?",
        "reference_answer": "D. Because she felt unwelcome.",
        "failure_surface": {"surface": "query_surface_gap", "rationale": "The source implies the attitude."},
    }

    assert classify_proposition_type(row) == "inference"


def test_temporal_anchor_does_not_make_event_question_comparative() -> None:
    row = {
        "utterance": "What did the students do after the announcement?",
        "reference_answer": "A. They packed their notebooks.",
        "failure_surface": {"surface": "compile_surface_gap", "rationale": "The later event is directly stated."},
    }

    assert classify_proposition_type(row) == "factual"


def test_numeric_answer_is_comparative_proposition_type() -> None:
    row = {
        "utterance": "In the text, there are _ people in the family.",
        "reference_answer": "C. five",
        "failure_surface": {"surface": "compile_surface_gap", "rationale": "The answer requires counting members."},
    }

    assert classify_proposition_type(row) == "comparative"


def test_how_feel_when_question_is_inference_not_comparative() -> None:
    row = {
        "utterance": "How did the father feel when he saw the letter?",
        "reference_answer": "B. Touched.",
        "failure_surface": {"surface": "compile_surface_gap", "rationale": "The state is inferred from a reaction."},
    }

    assert classify_proposition_type(row) == "inference"


def test_most_as_general_quantifier_is_not_comparative() -> None:
    row = {
        "utterance": "In most games, players need to _.",
        "reference_answer": "A. control a character",
        "failure_surface": {"surface": "compile_surface_gap", "rationale": "The source states the ordinary action."},
    }

    assert classify_proposition_type(row) == "factual"


def test_intended_audience_is_categorical() -> None:
    row = {
        "utterance": "This notice is intended for _.",
        "reference_answer": "A. parents",
        "failure_surface": {"surface": "compile_surface_gap", "rationale": "The recipient class is recoverable."},
    }

    assert classify_proposition_type(row) == "categorical"


def test_emotional_state_blank_is_inference() -> None:
    row = {
        "utterance": "After the announcement, the child was in a state of _.",
        "reference_answer": "B. relief",
        "failure_surface": {"surface": "compile_surface_gap", "rationale": "The passage implies the reaction."},
    }

    assert classify_proposition_type(row) == "inference"
