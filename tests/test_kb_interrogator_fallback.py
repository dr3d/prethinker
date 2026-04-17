from scripts.kb_interrogator import (
    _fallback_question_candidates,
    _normalize_question_payload,
)


def test_fallback_question_candidates_use_clause_grounding_and_fill_temporal():
    rows = _fallback_question_candidates(
        ["at/2", "at_step/2"],
        clauses=["at(site_alpha, canal).", "at_step(1, at(site_alpha, canal))."],
        question_count=12,
    )
    assert len(rows) == 12
    assert sum(1 for row in rows if row.get("temporal")) >= 4
    assert any(row.get("query") == "at(site_alpha, canal)." for row in rows)
    assert any(row.get("query") == "at_step(1, at(site_alpha, canal))." for row in rows)


def test_normalize_question_payload_enforces_temporal_floor():
    payload = {
        "questions": [
            {
                "id": "q1",
                "question": "Where is the site?",
                "query": "at(site_alpha, canal).",
                "expect_status": "success",
                "min_rows": 1,
                "reasoning_type": "retrieval",
                "temporal": False,
                "rationale": "direct",
            }
        ]
    }
    rows, notes = _normalize_question_payload(
        payload,
        fallback_signatures=["at/2", "at_step/2"],
        fallback_clauses=["at(site_alpha, canal).", "at_step(1, at(site_alpha, canal))."],
        question_count=6,
        min_temporal_questions=3,
    )
    assert len(rows) == 6
    assert sum(1 for row in rows if row.get("temporal")) >= 3
    assert any("temporal_floor" in note for note in notes)
