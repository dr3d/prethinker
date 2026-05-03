from scripts.run_rule_acquisition_pass import (
    _drop_backbone_duplicate_rules,
    _runtime_trial,
    _unsupported_body_fragments,
)
from scripts.union_domain_bootstrap_compiles import _promotion_ready_rules_from_trial


def test_drop_backbone_duplicate_rules_ignores_whitespace_and_periods() -> None:
    rules = [
        "derived_status(X, failed, council_vote) :- derived_condition(X, support_threshold_met, council_vote).",
        "derived_status(copper_rails_proposal, failed, council_budget_veto) :- proposal(copper_rails_proposal).",
    ]
    backbone_rules = [
        "derived_status(copper_rails_proposal, failed, council_budget_veto) :-   proposal(copper_rails_proposal)"
    ]

    kept, duplicates = _drop_backbone_duplicate_rules(rules, backbone_rules)

    assert kept == [
        "derived_status(X, failed, council_vote) :- derived_condition(X, support_threshold_met, council_vote)."
    ]
    assert duplicates == [
        "derived_status(copper_rails_proposal, failed, council_budget_veto) :- proposal(copper_rails_proposal)."
    ]


def test_runtime_trial_marks_dependency_composed_rules_ready() -> None:
    trial = _runtime_trial(
        facts=[
            "base_fact(alpha).",
            "ok(alpha).",
        ],
        backbone_rules=[],
        rule_lens_rules=[
            "derived_condition(Item, ready, demo_scope) :- base_fact(Item).",
            "derived_status(Item, final, demo_scope) :- derived_condition(Item, ready, demo_scope), ok(Item).",
        ],
        positive_queries=["derived_status(alpha, final, demo_scope)."],
        negative_queries=["derived_status(beta, final, demo_scope)."],
    )

    isolated = {item["rule"]: item for item in trial["derived_head_queries"]}
    composed = {item["rule"]: item for item in trial["composition_head_queries"]}
    final_rule = "derived_status(Item, final, demo_scope) :- derived_condition(Item, ready, demo_scope), ok(Item)."

    assert trial["promotion_ready_rule_count"] == 1
    assert trial["composition_ready_rule_count"] == 2
    assert trial["composition_rescued_rule_count"] == 1
    assert isolated[final_rule]["num_rows"] == 0
    assert composed[final_rule]["num_rows"] == 1
    assert composed[final_rule]["dependency_rule_count"] == 1
    assert trial["positive_probe_pass_count"] == 1
    assert trial["negative_probe_pass_count"] == 1


def test_union_promotion_filter_keeps_composition_ready_rules() -> None:
    final_rule = "derived_status(Item, final, demo_scope) :- derived_condition(Item, ready, demo_scope), ok(Item)."
    runtime_trial = {
        "derived_head_queries": [{"rule": final_rule, "status": "no_results", "num_rows": 0}],
        "composition_head_queries": [
            {
                "rule": final_rule,
                "status": "success",
                "num_rows": 1,
                "unsupported_body_signatures": [],
                "unsupported_body_goals": [],
                "unsupported_body_fragments": [],
            }
        ],
    }

    assert _promotion_ready_rules_from_trial(runtime_trial) == {final_rule}


def test_value_helpers_reject_measure_variables_and_computed_thresholds() -> None:
    fragments = _unsupported_body_fragments(
        "derived_status(Applicant, ineligible_matching, rule_5) :- "
        "requested_amount(Applicant, Amount), "
        "value_greater_than(Amount, 25000), "
        "matching_fund_commitment(Applicant, Match, Source), "
        "value_at_most(Match, 0.3 * Amount)."
    )

    assert any("value_greater_than(Amount, 25000) uses numeric measure variable" in item for item in fragments)
    assert any("value_at_most(Match, 0.3 * Amount) uses numeric measure variable" in item for item in fragments)
    assert any("value_at_most(Match, 0.3 * Amount) uses computed or variable threshold" in item for item in fragments)
