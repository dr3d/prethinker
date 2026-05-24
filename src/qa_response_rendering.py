"""Render product-facing answers from QA support envelopes.

The renderer consumes qa_response_envelope_v1 objects. It does not judge,
query, mutate KB state, or change QA scores.
"""

from __future__ import annotations

from typing import Any, Mapping


def render_qa_response(envelope: Mapping[str, Any]) -> dict[str, Any]:
    """Turn a QA support envelope into a user-facing response object."""

    status = str(envelope.get("status") or "ambiguous").strip() or "ambiguous"
    reference_answer = str(envelope.get("reference_answer") or "").strip()
    support_summary = str(envelope.get("support_summary") or "").strip()
    clarification_questions = _string_list(envelope.get("clarification_questions"))
    missing_slots = _string_list(envelope.get("missing_slots"))
    evidence_rows = envelope.get("evidence_rows")
    if not isinstance(evidence_rows, list):
        evidence_rows = []

    answer_text, next_action = _render_text(
        status=status,
        reference_answer=reference_answer,
        support_summary=support_summary,
        clarification_questions=clarification_questions,
        missing_slots=missing_slots,
    )

    return {
        "schema_version": "qa_rendered_response_v1",
        "source_schema_version": str(envelope.get("schema_version") or ""),
        "reading_type": str(envelope.get("reading_type") or ""),
        "status": status,
        "display_status": _display_status(status),
        "answer_text": answer_text,
        "next_action": next_action,
        "evidence_rows": evidence_rows[:16],
        "source_row_count": len(evidence_rows),
        "policy_note": (
            "Rendered from a QA response envelope. This layer presents the current "
            "support reading; it does not create new evidence or alter QA scoring."
        ),
    }


def _render_text(
    *,
    status: str,
    reference_answer: str,
    support_summary: str,
    clarification_questions: list[str],
    missing_slots: list[str],
) -> tuple[str, str]:
    if status == "established":
        body = support_summary or reference_answer or "The admitted evidence supports the answer."
        return body, "Use the cited evidence rows as support."
    if status == "partially_established":
        body = support_summary or reference_answer or "The admitted evidence only partially supports the answer."
        return f"Partially established: {body}", "Review the missing or qualified support before relying on this answer."
    if status == "clarification_required":
        if clarification_questions:
            question_text = clarification_questions[0]
        elif missing_slots:
            question_text = "Please clarify: " + ", ".join(missing_slots) + "."
        else:
            question_text = "Please clarify the question before I answer."
        return question_text, "Ask for clarification before answering."
    if status == "coverage_gap":
        return (
            "I do not have enough admitted evidence to establish the requested answer.",
            "Inspect compile coverage or source preservation for this row.",
        )
    if status == "not_established":
        return (
            "The admitted evidence does not establish the supplied answer.",
            "Do not rely on this answer without additional evidence.",
        )
    return (
        "The current evidence reading is ambiguous.",
        "Review the row manually or rerun the relevant measurement path.",
    )


def _display_status(status: str) -> str:
    return {
        "established": "Established",
        "partially_established": "Partially established",
        "not_established": "Not established",
        "clarification_required": "Clarification required",
        "coverage_gap": "Coverage gap",
        "ambiguous": "Ambiguous",
    }.get(status, "Ambiguous")


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    out: list[str] = []
    for item in value:
        text = str(item).strip()
        if text and text not in out:
            out.append(text)
    return out
