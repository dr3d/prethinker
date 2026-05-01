from kb_pipeline import CorePrologRuntime
from scripts.score_story_world_support import (
    _available_signatures,
    _clause_signature,
    _score_support_row,
    _summary,
)


def test_clause_signature_handles_terms_strings_and_rules() -> None:
    assert _clause_signature("deadline_met(inquiry_report, 60_days, '2026-06-01', yes).") == "deadline_met/4"
    assert _clause_signature("before(E1, E2) :- story_time(E1, T1), story_time(E2, T2).") == "before/2"


def test_support_scorer_reports_loose_predicate_arity_gradient() -> None:
    runtime = CorePrologRuntime(max_depth=100)
    runtime.assert_fact("person_role(elena_voss, respondent).")
    signatures = _available_signatures(facts=["person_role(elena_voss, respondent)."], rules=[])
    row = {
        "id": "q001",
        "phase": "roles",
        "question": "Who was the respondent?",
        "required_support_any": [
            ["person_role(Who, respondent).", "committee_member(inquiry_committee, Who, role)."]
        ],
        "failure_classes": ["role_surface_gap"],
    }

    scored = _score_support_row(row, runtime=runtime, qa_row={}, available_signatures=signatures)

    assert scored["support_present"] is False
    assert scored["loose_support_present"] is False
    assert scored["bundles"][0]["label"] == "bundle_1"
    assert scored["loose_query_matches"] == 1
    assert scored["loose_query_total"] == 2
    assert scored["loose_query_match_rate"] == 0.5
    assert scored["root_cause"] == "compile_missing_required_support"

    loose_signatures = signatures | {"committee_member/3"}
    scored = _score_support_row(row, runtime=runtime, qa_row={}, available_signatures=loose_signatures)

    assert scored["support_present"] is False
    assert scored["loose_support_present"] is True
    assert scored["root_cause"] == "support_shape_incomplete_or_argument_drift"
    summary = _summary([scored], load_errors=[])
    assert summary["loose_support_present"] == 1
    assert summary["loose_query_signature_rate"] == 1.0
