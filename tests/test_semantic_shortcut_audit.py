from scripts.run_semantic_shortcut_audit import audit_clauses, collect_json_clauses, parse_clause


def risks_for(clause: str) -> set[str]:
    return {finding.risk for finding in audit_clauses([clause])}


def test_audit_flags_unbound_head_variable() -> None:
    clause = "derived_authorization(Order, valid, harbor) :- authorized_action(repair_order_71, mara_vale, valid)."
    findings = risks_for(clause)
    assert "unbound_head_variable" in findings


def test_audit_flags_entity_helper_argument_misuse() -> None:
    clause = "derived_tax_status(Cargo, taxable, harbor) :- value_greater_than(150, 100)."
    findings = risks_for(clause)
    assert "helper_argument_misuse" in findings


def test_audit_flags_claim_to_fact_shortcut() -> None:
    clause = "derived_status(case_7, confirmed, review) :- witness_claim(w1, mara, saw_payment, hearing)."
    findings = risks_for(clause)
    assert "claim_to_fact_shortcut_risk" in findings


def test_audit_flags_aggregation_final_outcome_without_veto_check() -> None:
    clause = "derived_status(budget_4, approved, council_vote) :- support_count_at_least(budget_4, 3)."
    findings = risks_for(clause)
    assert "aggregation_final_outcome_overclaim" in findings


def test_audit_accepts_body_supported_role_join_shape() -> None:
    clause = (
        "derived_authorization(RepairOrder, valid, glass_tide_repair) :- "
        "holds_role(Warden, harbor_warden, active), "
        "holds_role(Engineer, chief_tide_engineer, active), "
        "authorized_action(RepairOrder, Warden, valid), "
        "authorized_action(RepairOrder, Engineer, valid)."
    )
    findings = risks_for(clause)
    assert "unbound_head_variable" not in findings
    assert "broad_class_fanout_risk" not in findings


def test_parse_clause_splits_body_goals_at_top_level_only() -> None:
    parsed = parse_clause(
        "derived_status(X, ok, scope) :- pair(X, tuple(a,b)), number_greater_than(N, 3)."
    )
    assert parsed.head is not None
    assert [goal.signature for goal in parsed.body] == ["pair/2", "number_greater_than/2"]


def test_collect_json_clauses_from_compile_artifact_shape() -> None:
    payload = {
        "source_compile": {
            "facts": ["person(mara).", "not a clause"],
            "rules": [
                "derived_status(X, ok, scope) :- person(X).",
                {"clause": "derived_condition(case_1, threshold_met, vote) :- support_count_at_least(case_1, 3)."},
            ],
        }
    }
    clauses = collect_json_clauses(payload)
    assert "person(mara)." in clauses
    assert "derived_status(X, ok, scope) :- person(X)." in clauses
    assert "derived_condition(case_1, threshold_met, vote) :- support_count_at_least(case_1, 3)." in clauses
    assert "not a clause" not in clauses
