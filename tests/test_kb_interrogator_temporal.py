from kb_pipeline import CorePrologRuntime, _normalize_clause
from scripts import kb_interrogator as ki


def _runtime_with_clauses(clauses: list[str]) -> CorePrologRuntime:
    runtime = CorePrologRuntime()
    for clause in clauses:
        normalized = _normalize_clause(clause)
        result = runtime.assert_rule(normalized) if ":-" in normalized else runtime.assert_fact(normalized)
        assert result.get("status") == "success", result
    return runtime


def test_relax_shared_step_temporal_query_rewrites_shared_step_variable() -> None:
    query = "at_step(T, incident(breach)), at_step(T, at(Unit, airlock))."
    repaired = ki._relax_shared_step_temporal_query(query)
    assert repaired == "at_step(Step1, incident(breach)), at_step(Step2, at(Unit, airlock))."


def test_evaluate_questions_repairs_shared_step_temporal_query_when_relaxed_variant_passes() -> None:
    runtime = _runtime_with_clauses(
        [
            "at_step(21, at(unit_alpha, airlock)).",
            "at_step(22, incident(breach)).",
        ]
    )

    questions = [
        {
            "id": "q1",
            "question": "Which unit reported the breach?",
            "query": "at_step(T, incident(breach)), at_step(T, at(Unit, airlock)).",
            "expect_status": "success",
            "min_rows": 1,
            "max_rows": 1,
            "contains_row": {"Unit": "unit_alpha"},
            "reasoning_type": "temporal",
            "temporal": True,
            "rationale": "test",
        }
    ]

    evaluated = ki._evaluate_questions(runtime, questions)
    row = evaluated["questions"][0]

    assert row["passed"] is True
    assert row["effective_query"] == "at_step(Step1, incident(breach)), at_step(Step2, at(Unit, airlock))."
    assert row["repair_applied"] == {
        "kind": "shared_step_relaxed",
        "original_query": "at_step(T, incident(breach)), at_step(T, at(Unit, airlock)).",
        "effective_query": "at_step(Step1, incident(breach)), at_step(Step2, at(Unit, airlock)).",
    }
    assert row["result"]["rows"] == [{"Step1": "22", "Step2": "21", "Unit": "unit_alpha"}]


def test_fallback_question_candidates_prioritize_temporal_clauses() -> None:
    signatures = ["plain_fact/1", "at_step/2"]
    clauses = [
        "plain_fact(a).",
        "plain_fact(b).",
        "at_step(3, plain_fact(c)).",
    ]

    rows = ki._fallback_question_candidates(signatures, clauses=clauses, question_count=3, temporal_first=True)

    assert len(rows) == 3
    assert any(row["temporal"] for row in rows)
    assert rows[0]["temporal"] is True
