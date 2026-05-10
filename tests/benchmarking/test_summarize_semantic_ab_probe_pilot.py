from __future__ import annotations

from scripts.benchmarking.summarize_semantic_ab_probe_pilot import check_row, summarize


def test_check_row_detects_absence_status_variants() -> None:
    unresolved = check_row(_row("absence_negative_evidence_vs_unresolved__unresolved_absence", "q004", "Unresolved and pending confirmation."))
    negative = check_row(_row("absence_negative_evidence_vs_unresolved__negative_absence_distractor", "q004", "Disqualifying; the exception is unavailable."))
    denied = check_row(_row("absence_negative_evidence_vs_unresolved__negative_absence", "q005", "The exception is denied."))

    assert unresolved["passed"] is True
    assert negative["passed"] is True
    assert denied["passed"] is True


def test_check_row_detects_absence_near_collision_entity_confusion() -> None:
    confused = check_row(
        _row("absence_negative_evidence_vs_unresolved__unresolved_absence_hard", "q003", "No, North Pine Glass has no confirmed relocation file.")
    )

    assert confused["passed"] is False
    assert confused["reason"] == "expects target applicant, not near-collision applicant"


def test_check_row_detects_condition_clock_variants() -> None:
    condition = check_row(_row("condition_time_vs_certification_time__condition_clock_distractor", "q003", "2026-05-01 17:00."))
    certification = check_row(_row("condition_time_vs_certification_time__certification_clock", "q003", "2026-05-01 17:30."))

    assert condition["passed"] is True
    assert certification["passed"] is True


def test_summarize_counts_checked_failures() -> None:
    summary = summarize(
        [
            _row("condition_time_vs_certification_time__condition_clock", "q003", "2026-05-01 17:30."),
            _row("condition_time_vs_certification_time__certification_clock", "q003", "2026-05-01 17:30."),
        ]
    )

    assert summary["checked_rows"] == 2
    assert summary["failed_rows"] == 1


def _row(fixture: str, question_id: str, answer: str) -> dict[str, object]:
    return {
        "fixture": fixture,
        "question_id": question_id,
        "answer": answer,
    }
