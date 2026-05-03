from scripts.run_rule_acquisition_pass import _drop_backbone_duplicate_rules


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
