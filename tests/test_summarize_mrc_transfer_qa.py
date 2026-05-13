from __future__ import annotations

import json

from scripts.summarize_mrc_transfer_qa import (
    PROPOSITION_TYPE_OPERATIONAL_RULES,
    classify_proposition_type,
    classify_transfer_coordinate,
    summarize_run,
)


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


def test_classify_how_far_coordinate_as_comparative() -> None:
    row = {
        "utterance": "How far was it from the meeting point to the hotel?",
        "reference_answer": "B. Three miles.",
        "failure_surface": {"surface": "hybrid_join_gap", "rationale": "The route distance must be assembled."},
    }

    assert classify_transfer_coordinate(row) == "comparative_or_temporal_resolution"


def test_classify_feeling_after_event_coordinate_as_implicit() -> None:
    row = {
        "utterance": "How did the captain feel after the all-clear announcement?",
        "reference_answer": "The captain felt relieved.",
        "failure_surface": {"surface": "compile_surface_gap", "rationale": "The emotional state is inferred from reaction."},
    }

    assert classify_transfer_coordinate(row) == "implicit_attitude_or_consequence"


def test_post_event_action_is_not_temporal_coordinate_by_default() -> None:
    row = {
        "utterance": "What did the volunteers do after the bottle tipped over?",
        "reference_answer": "They wiped the table.",
        "failure_surface": {"surface": "compile_surface_gap", "rationale": "The action detail was not compiled."},
    }

    assert classify_transfer_coordinate(row) == "direct_compile_surface_gap"


def test_classify_title_coordinate() -> None:
    row = {
        "utterance": "What is the best title for this passage?",
        "reference_answer": "A. A Useful Habit",
        "failure_surface": {"surface": "answer_surface_gap", "rationale": "The facts support the theme."},
    }

    assert classify_transfer_coordinate(row) == "title_theme_or_summary_answer"


def test_document_name_is_not_title_theme_coordinate() -> None:
    row = {
        "utterance": 'What contract text relates to "Document Name"? Details: The name of the contract',
        "reference_answer": "DISTRIBUTOR AGREEMENT",
        "failure_surface": {
            "surface": "query_surface_gap",
            "rationale": "A source row contains a title-like token, but the question asks for an explicit document field.",
        },
    }

    assert classify_transfer_coordinate(row) == "query_surface_resolution"
    assert classify_proposition_type(row) == "factual"


def test_classifier_transport_error_is_not_false_option_coordinate() -> None:
    row = {
        "utterance": 'What contract text relates to "Effective Date"?',
        "reference_answer": "February 21, 2011",
        "failure_surface": {
            "surface": "judge_uncertain",
            "rationale": "classifier error: invalid_json_schema is_byok false",
        },
    }

    assert classify_transfer_coordinate(row) == "judge_transport_uncertain"


def test_summarize_uses_latest_qa_artifact_per_fixture(tmp_path) -> None:
    fixture_dir = tmp_path / "fixture_a"
    fixture_dir.mkdir()
    old_payload = {
        "rows": [
            {
                "id": "q001",
                "ok": False,
                "utterance": "Where?",
                "reference_answer": "north hall",
                "failure_surface": {"surface": "compile_surface_gap", "rationale": "old"},
                "reference_judge": {"verdict": "miss"},
            }
        ]
    }
    new_payload = {
        "rows": [
            {
                "id": "q001",
                "ok": True,
                "utterance": "Where?",
                "reference_answer": "north hall",
                "reference_judge": {"verdict": "exact"},
            }
        ]
    }
    old_path = fixture_dir / "domain_bootstrap_qa_20260101T000000000000Z_qa_model.json"
    new_path = fixture_dir / "domain_bootstrap_qa_20260101T000001000000Z_qa_model.json"
    old_path.write_text(json.dumps(old_payload), encoding="utf-8")
    new_path.write_text(json.dumps(new_payload), encoding="utf-8")

    summary = summarize_run(tmp_path)

    assert summary["totals"]["question_count"] == 1
    assert summary["totals"]["exact"] == 1


def test_summarize_can_mark_intake_alignment_noise(tmp_path) -> None:
    fixture_dir = tmp_path / "fixture_a"
    fixture_dir.mkdir()
    payload = {
        "rows": [
            {
                "id": "q001",
                "ok": False,
                "utterance": "Does it collect GPS location?",
                "reference_answer": "It collects payment data.",
                "failure_surface": {"surface": "compile_surface_gap", "rationale": "No GPS fact was compiled."},
                "reference_judge": {"verdict": "miss"},
            }
        ]
    }
    qa_path = fixture_dir / "domain_bootstrap_qa_20260101T000001000000Z_qa_model.json"
    qa_path.write_text(json.dumps(payload), encoding="utf-8")
    audit_path = tmp_path / "transfer_intake_audit.json"
    audit_path.write_text(
        json.dumps(
            {
                "rows": [
                    {
                        "fixture": "fixture_a",
                        "id": "q001",
                        "status": "likely_reference_mismatch",
                        "flags": ["low_question_evidence_overlap"],
                        "missing_question_terms": ["gps", "location"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    summary = summarize_run(tmp_path, intake_audit=audit_path)

    assert summary["failure_surface_counts"] == {"intake_quality_gap": 1}
    assert summary["transfer_coordinate_counts"] == {"dataset_answer_alignment_noise": 1}
    assert "alignment noise" in summary["non_exact_rows"][0]["rationale"]


def test_proposition_taxonomy_declares_operational_precedence() -> None:
    rules = "\n".join(PROPOSITION_TYPE_OPERATIONAL_RULES)

    assert "Apply precedence" in rules
    assert "synthesis, comparative, categorical, inference, factual" in rules
    assert "Remove multiple-choice options" in rules


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


def test_short_for_question_is_categorical_not_inference() -> None:
    row = {
        "utterance": "What is AFC short for?",
        "reference_answer": "American Football Conference",
        "failure_surface": {
            "surface": "compile_surface_gap",
            "rationale": "The failure rationale may mention missing inference, but the proposition is an acronym expansion.",
        },
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


def test_contract_date_extraction_is_factual_not_comparative() -> None:
    row = {
        "utterance": 'What contract text relates to "Agreement Date"? Details: The date of the contract',
        "reference_answer": "October 30, 2017",
        "failure_surface": {"surface": "compile_surface_gap", "rationale": "The date is directly stated."},
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
