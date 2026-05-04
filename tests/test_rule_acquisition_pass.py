from scripts.run_rule_acquisition_pass import (
    _backbone_fact_signature_support,
    _drop_backbone_duplicate_rules,
    _rule_guidance_context,
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


def test_runtime_trial_follows_transitive_dependency_composition() -> None:
    trial = _runtime_trial(
        facts=[
            "base_fact(alpha).",
            "ok(alpha).",
        ],
        backbone_rules=[],
        rule_lens_rules=[
            "derived_condition(Item, ready, demo_scope) :- base_fact(Item).",
            "derived_permission(Item, proceed, demo_object, demo_scope) :- derived_condition(Item, ready, demo_scope).",
            "derived_status(Item, final, demo_scope) :- derived_permission(Item, proceed, demo_object, demo_scope), ok(Item).",
        ],
        positive_queries=["derived_status(alpha, final, demo_scope)."],
        negative_queries=[],
    )

    composed = {item["rule"]: item for item in trial["composition_head_queries"]}
    final_rule = "derived_status(Item, final, demo_scope) :- derived_permission(Item, proceed, demo_object, demo_scope), ok(Item)."

    assert trial["promotion_ready_rule_count"] == 1
    assert trial["composition_ready_rule_count"] == 3
    assert trial["composition_rescued_rule_count"] == 2
    assert composed[final_rule]["num_rows"] == 1
    assert composed[final_rule]["dependency_rule_count"] == 2
    assert composed[final_rule]["dependency_signatures"] == [
        "derived_permission/4",
    ]
    assert composed[final_rule]["transitive_dependency_signatures"] == [
        "derived_condition/3",
        "derived_permission/4",
    ]
    assert trial["positive_probe_pass_count"] == 1


def test_dependency_composition_excludes_same_head_sibling_rules_transitively() -> None:
    target_rule = "derived_status(Item, final, demo_scope) :- derived_condition(Item, ready, demo_scope)."
    sibling_same_head = "derived_status(Item, intermediate, demo_scope) :- ok(Item)."
    trial = _runtime_trial(
        facts=["ok(alpha)."],
        backbone_rules=[],
        rule_lens_rules=[
            target_rule,
            "derived_condition(Item, ready, demo_scope) :- derived_status(Item, intermediate, demo_scope).",
            sibling_same_head,
        ],
        positive_queries=[],
        negative_queries=[],
    )

    composed = {item["rule"]: item for item in trial["composition_head_queries"]}

    assert composed[target_rule]["num_rows"] == 0
    assert composed[target_rule]["dependency_rule_count"] == 1
    assert composed[target_rule]["transitive_dependency_signatures"] == ["derived_condition/3"]
    assert composed[target_rule]["same_head_sibling_rules_excluded"] == [sibling_same_head]


def test_runtime_trial_supports_any_of_probe_groups() -> None:
    trial = _runtime_trial(
        facts=["amendment_introduced(ba_2026_07, councilmember_okafor, 2026_03_04, 185000)."],
        backbone_rules=[],
        rule_lens_rules=[
            "derived_condition(Amendment, requires_public_hearing, budget_amendment) :- amendment_introduced(Amendment, _, _, Amount), number_greater_than(Amount, 50000).",
        ],
        positive_queries=[
            "derived_status(ba_2026_07, requires_public_hearing, Source) || derived_condition(ba_2026_07, requires_public_hearing, Source)"
        ],
        negative_queries=[
            "derived_status(ba_2026_07, no_hearing_required, Source) || derived_condition(ba_2026_07, no_hearing_required, Source)"
        ],
    )

    assert trial["positive_probe_pass_count"] == 1
    assert trial["negative_probe_pass_count"] == 1
    positive = trial["positive_probe_results"][0]
    assert positive["passed"] is True
    assert len(positive["alternatives"]) == 2
    assert positive["num_rows"] == 1


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


def test_runtime_trial_blocks_rules_with_unbound_head_variables() -> None:
    rule = "derived_condition(Amendment, fiscal_certification_required, charter_9_3) :- charter_rule(9_3, fiscal_neutrality_certification, source_text)."
    trial = _runtime_trial(
        facts=["charter_rule(9_3, fiscal_neutrality_certification, source_text)."],
        backbone_rules=[],
        rule_lens_rules=[rule],
        positive_queries=[],
        negative_queries=[],
    )

    item = trial["derived_head_queries"][0]
    assert trial["promotion_ready_rule_count"] == 0
    assert item["unbound_head_variables"] == ["Amendment"]
    assert any("head variable Amendment is not bound" in fragment for fragment in item["unsupported_body_fragments"])


def test_repeated_body_aliasing_requires_literal_anchors() -> None:
    fragments = _unsupported_body_fragments(
        "derived_status(Applicant, eligible, rule8) :- "
        "required_condition(Applicant, Condition), "
        "deadline_met(Applicant, Condition), "
        "required_condition(Applicant, Condition), "
        "deadline_met(Applicant, Condition)."
    )

    assert any("repeated required_condition/2 goals share multiple anchor variables" in item for item in fragments)
    assert any("distinct requirements may satisfy with the same row" in item for item in fragments)


def test_repeated_body_goals_with_distinct_literal_anchors_are_allowed() -> None:
    fragments = _unsupported_body_fragments(
        "derived_status(Applicant, eligible, rule8) :- "
        "required_condition(Applicant, submit_revised_budget), "
        "deadline_met(Applicant, submit_revised_budget), "
        "required_condition(Applicant, provide_matching_docs), "
        "deadline_met(Applicant, provide_matching_docs)."
    )

    assert not any("repeated required_condition/2 goals" in item for item in fragments)
    assert not any("repeated deadline_met/2 goals" in item for item in fragments)


def test_runtime_trial_blocks_repeated_body_aliasing_rule() -> None:
    rule = (
        "derived_status(Applicant, eligible, rule8) :- "
        "required_condition(Applicant, Condition), "
        "deadline_met(Applicant, Condition), "
        "required_condition(Applicant, Condition), "
        "deadline_met(Applicant, Condition)."
    )
    trial = _runtime_trial(
        facts=[
            "required_condition(anya_petrov, submit_revised_budget).",
            "deadline_met(anya_petrov, submit_revised_budget).",
        ],
        backbone_rules=[],
        rule_lens_rules=[rule],
        positive_queries=[],
        negative_queries=[],
    )

    item = trial["derived_head_queries"][0]
    assert item["num_rows"] == 1
    assert trial["promotion_ready_rule_count"] == 0
    assert any("repeated required_condition/2 goals" in fragment for fragment in item["unsupported_body_fragments"])


def test_compact_rule_guidance_keeps_binding_and_horn_shape_constraints() -> None:
    guidance = "\n".join(_rule_guidance_context(target=4, rule_class="threshold", compact=True))

    assert "Head :- Body" in guidance
    assert "Every head variable must be bound" in guidance
    assert "Do not use derived_* predicates in the body" in guidance
    assert "fact-shaped clause" in guidance


def test_aggregation_rule_guidance_blocks_sibling_scope_leakage() -> None:
    guidance = "\n".join(_rule_guidance_context(target=4, rule_class="aggregation", compact=True))

    assert "current raw_source_text rule span" in guidance
    assert "Do not emit sibling scopes" in guidance
    assert "support_threshold_met" in guidance
    assert "majority_support" in guidance


def test_dependency_composition_guidance_consumes_upstream_conditions() -> None:
    guidance = "\n".join(_rule_guidance_context(target=4, rule_class="dependency_composition", compact=True))

    assert "consume existing upstream derived_condition/3" in guidance
    assert "Do not re-emit an upstream intermediate condition" in guidance


def test_backbone_fact_signature_support_is_structural_index() -> None:
    support = _backbone_fact_signature_support(
        [
            "voting_threshold(amendment_adoption, 4, 7).",
            "voting_threshold(amendment_recall, 4, 7).",
            "charter_rule(9_1, amendment_adoption, threshold_4_of_7).",
        ],
        example_limit=1,
    )

    by_signature = {row["signature"]: row for row in support}
    assert by_signature["voting_threshold/3"]["count"] == 2
    assert by_signature["voting_threshold/3"]["examples"] == [
        "voting_threshold(amendment_adoption, 4, 7)."
    ]
    assert by_signature["charter_rule/3"]["count"] == 1


def test_number_helper_dormancy_is_not_missing_body_support() -> None:
    rule = (
        "derived_status(AmendmentId, no_hearing_required, budget_amendment) :- "
        "amendment_introduced(AmendmentId, _, _, Amount), "
        "number_at_most(Amount, 50000)."
    )
    trial = _runtime_trial(
        facts=["amendment_introduced(ba_2026_07, councilmember_okafor, 2026_03_04, 185000)."],
        backbone_rules=[],
        rule_lens_rules=[rule],
        positive_queries=[],
        negative_queries=[],
    )

    item = trial["derived_head_queries"][0]
    assert item["num_rows"] == 0
    assert item["unsupported_body_goals"] == []
    assert item["unsupported_body_fragments"] == []


def test_number_helper_requires_bound_numeric_variable() -> None:
    fragments = _unsupported_body_fragments(
        "derived_status(AmendmentId, no_hearing_required, budget_amendment) :- "
        "number_at_most(Amount, 50000)."
    )

    assert any("number_at_most(Amount, 50000) uses numeric value variable before it is bound" in item for item in fragments)


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
