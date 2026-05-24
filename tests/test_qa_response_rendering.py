from src.qa_response_rendering import render_qa_response


def test_render_qa_response_established_uses_support_summary() -> None:
    response = render_qa_response(
        {
            "schema_version": "qa_response_envelope_v1",
            "reading_type": "reference_answer_support",
            "status": "established",
            "reference_answer": "Dana Lee signed the report.",
            "support_summary": "The admitted row names Dana Lee as signer.",
            "evidence_rows": [{"source_row": "src_line_7"}],
        }
    )

    assert response["schema_version"] == "qa_rendered_response_v1"
    assert response["status"] == "established"
    assert response["display_status"] == "Established"
    assert response["answer_text"] == "The admitted row names Dana Lee as signer."
    assert response["source_row_count"] == 1


def test_render_qa_response_clarification_required_asks_first_question() -> None:
    response = render_qa_response(
        {
            "schema_version": "qa_response_envelope_v1",
            "status": "clarification_required",
            "clarification_questions": ["Which notice are you asking about?"],
            "missing_slots": ["notice_id"],
        }
    )

    assert response["answer_text"] == "Which notice are you asking about?"
    assert response["next_action"] == "Ask for clarification before answering."


def test_render_qa_response_coverage_gap_does_not_invent_answer() -> None:
    response = render_qa_response(
        {
            "schema_version": "qa_response_envelope_v1",
            "status": "coverage_gap",
            "reference_answer": "Three corrective actions were listed.",
        }
    )

    assert response["answer_text"] == "I do not have enough admitted evidence to establish the requested answer."
    assert "does not create new evidence" in response["policy_note"]


def test_render_qa_response_partial_and_not_established_are_distinct() -> None:
    partial = render_qa_response(
        {
            "schema_version": "qa_response_envelope_v1",
            "status": "partially_established",
            "support_summary": "Only one of the two requested dates was retrieved.",
        }
    )
    miss = render_qa_response(
        {
            "schema_version": "qa_response_envelope_v1",
            "status": "not_established",
            "reference_answer": "The source says X.",
        }
    )

    assert partial["answer_text"].startswith("Partially established:")
    assert miss["answer_text"] == "The admitted evidence does not establish the supplied answer."
