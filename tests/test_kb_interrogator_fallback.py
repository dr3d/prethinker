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


def test_normalize_question_payload_drops_rule_queries_and_repairs_boolean_checks():
    payload = {
        "questions": [
            {
                "id": "bad1",
                "question": "Who directed the commons?",
                "query": "directed(X, commons) :- at_step(1, X).",
                "expect_status": "success",
                "min_rows": 1,
                "reasoning_type": "temporal",
                "temporal": True,
                "rationale": "bad rule query",
            },
            {
                "id": "ok1",
                "question": "Did Mateo slip?",
                "query": "slipped(mateo, footbridge_stairs).",
                "expect_status": "success",
                "min_rows": 2,
                "max_rows": 2,
                "contains_row": {"true": True},
                "reasoning_type": "retrieval",
                "temporal": False,
                "rationale": "boolean fact check",
            },
        ]
    }
    rows, notes = _normalize_question_payload(
        payload,
        fallback_signatures=["slipped/2", "at_step/2"],
        fallback_clauses=["slipped(mateo, footbridge_stairs).", "at_step(1, slipped(mateo, footbridge_stairs))."],
        question_count=2,
        min_temporal_questions=0,
    )
    assert any("rule_query_dropped" in note for note in notes)
    assert any("contains_row_ignored" in note for note in notes)
    assert any("row_bounds_repaired" in note for note in notes)
    assert rows[0]["query"] == "slipped(mateo, footbridge_stairs)."
    assert rows[0]["contains_row"] is None
    assert rows[0]["min_rows"] == 1
    assert rows[0]["max_rows"] == 1
