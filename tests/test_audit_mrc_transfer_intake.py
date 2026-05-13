from __future__ import annotations

import json

from scripts.audit_mrc_transfer_intake import audit_root, audit_row


def test_audit_row_accepts_answer_bearing_evidence() -> None:
    row = audit_row(
        fixture="fixture_a",
        qid="q001",
        question="Does the service collect GPS location?",
        reference_answer="The service collects GPS location when the user enables location services.",
        source="The service collects GPS location when the user enables location services.",
        min_question_terms=1,
        min_question_evidence_overlap=0.5,
    )

    assert row["status"] == "ok"
    assert "gps" in row["covered_question_terms"]
    assert row["reference_literal_in_source"] is True


def test_audit_row_flags_literal_answer_that_misses_question_terms() -> None:
    row = audit_row(
        fixture="fixture_a",
        qid="q001",
        question="Does the service collect GPS location?",
        reference_answer="The service collects payment card information for purchases.",
        source="The service collects payment card information for purchases.",
        min_question_terms=1,
        min_question_evidence_overlap=0.5,
    )

    assert row["status"] == "likely_reference_mismatch"
    assert "low_question_evidence_overlap" in row["flags"]
    assert "gps" in row["missing_question_terms"]
    assert "location" in row["missing_question_terms"]


def test_audit_root_summarizes_fixture_alignment(tmp_path) -> None:
    fixture = tmp_path / "fixture_a"
    fixture.mkdir()
    (fixture / "source.md").write_text("The service collects payment data.", encoding="utf-8")
    (fixture / "qa.md").write_text("# QA\n\n1. Does the service collect GPS location?\n", encoding="utf-8")
    (fixture / "oracle.jsonl").write_text(
        json.dumps(
            {
                "id": "q001",
                "reference_answer": "The service collects payment data.",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    summary = audit_root(tmp_path)

    assert summary["totals"]["rows"] == 1
    assert summary["totals"]["likely_reference_mismatch"] == 1
    assert summary["flag_counts"]["low_question_evidence_overlap"] == 1
