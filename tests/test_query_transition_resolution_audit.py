from scripts.audit_query_transition_resolution import classify_not_exact_row


def _row(utterance: str, queries: list[str], *, rationale: str = "", reference: str = "") -> dict:
    return {
        "utterance": utterance,
        "reference_answer": reference,
        "failure_surface": {"rationale": rationale, "surface": "hybrid_join_gap"},
        "reference_judge": {"verdict": "miss"},
        "evidence_bundle_plan_query_results": [
            {"query": query, "result": {"predicate": query.split("(", 1)[0]}} for query in queries
        ],
    }


def test_classifies_return_to_state_from_intervening_end_surface() -> None:
    row = _row(
        "When did the unit return to standby?",
        ["state_start(unit_1, standby, Time)."],
        rationale="The answer is derivable from state_end(unit_1, active, Time).",
    )

    assert classify_not_exact_row(row) == "return_to_state_requires_intervening_end"


def test_classifies_interval_scoped_flat_status_surface() -> None:
    row = _row(
        "What status applied during the active interval?",
        ["asset_status(asset_1, Status).", "valid_until(asset_1, End)."],
    )

    assert classify_not_exact_row(row) == "interval_scoped_status_flattened"


def test_classifies_assignment_scope_missing_from_three_slot_assignment() -> None:
    row = _row(
        "Who was assigned to review?",
        ["record_assigned_to(record_1, Assignee, Date)."],
    )

    assert classify_not_exact_row(row) == "assignment_scope_missing"


def test_classifies_initial_status_absence() -> None:
    row = _row(
        "What was the item's initial status?",
        ["item_status(item_1, FinalStatus)."],
    )

    assert classify_not_exact_row(row) == "initial_status_not_admitted"
