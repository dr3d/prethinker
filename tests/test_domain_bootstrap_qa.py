from scripts.run_domain_bootstrap_qa import (
    POST_INGESTION_QA_QUERY_STRATEGY,
    _negative_join_with_previous,
    _relaxed_constant_query,
    _temporal_join_with_previous,
    clause_signature,
    compiled_kb_inventory,
    parse_markdown_answer_key,
    parse_numbered_markdown_questions,
    score_oracle,
    summarize,
)
from kb_pipeline import CorePrologRuntime


def test_parse_numbered_markdown_questions_keeps_phase_labels() -> None:
    text = """# Phase 1 - Straight Queries

1. Which items were explicitly declared recalled?
2. Who is the authority accused of wrongdoing?

# Phase 2 - Ambiguity

16. Who is K. Lume?

## Answers 1-16

1. Batch P-44.
16. Unknown unless resolved.
"""

    rows = parse_numbered_markdown_questions(text)

    assert [row["id"] for row in rows] == ["q001", "q002", "q016"]
    assert rows[0]["phase"] == "Phase 1 - Straight Queries"
    assert rows[2]["phase"] == "Phase 2 - Ambiguity"
    assert rows[2]["utterance"] == "Who is K. Lume?"


def test_parse_markdown_answer_key_reads_answer_section_only() -> None:
    text = """# Questions

1. Which items were recalled?
2. Who signed?

## Answers 1-2

1. Batch P-44 and the welcome loaf.
2. Unknown until K. Lume is resolved.
"""

    answers = parse_markdown_answer_key(text)

    assert answers == {
        "q001": "Batch P-44 and the welcome loaf.",
        "q002": "Unknown until K. Lume is resolved.",
    }


def test_reference_answers_are_not_structured_oracle_expectations() -> None:
    row = {"projected_decision": "answer", "queries": [], "query_results": []}

    assert score_oracle(row=row, oracle={"reference_answer": "Unknown."}) is None


def test_compiled_kb_inventory_uses_clause_surfaces_not_english() -> None:
    facts = [
        "affected_item(grievance_1, batch_p_44).",
        "claimed_label(grievance_1, plain_oat_ration).",
    ]
    rules = ["can_depart(Batch) :- affected_item(G, Batch), claimed_label(G, plain_oat_ration)."]

    inventory = compiled_kb_inventory(facts=facts, rules=rules)

    assert clause_signature(rules[0]) == "can_depart/1"
    assert inventory["signatures"] == ["affected_item/2", "can_depart/1", "claimed_label/2"]
    assert inventory["examples"]["affected_item/2"] == ["affected_item(grievance_1, batch_p_44)."]
    assert "affected_item(X, Y)." in inventory["query_templates"]
    assert "can_depart(X)." in inventory["query_templates"]


def test_post_ingestion_qa_strategy_prefers_compiled_kb_surface() -> None:
    strategy = POST_INGESTION_QA_QUERY_STRATEGY

    assert strategy["name"] == "post_ingestion_qa_query_strategy_v1"
    assert "compiled_predicate_inventory.signatures" in " ".join(strategy["predicate_surface_policy"])
    assert "relevant_clauses" in " ".join(strategy["predicate_surface_policy"])
    assert any("full compiled predicate arity" in item for item in strategy["arity_and_variable_policy"])
    assert any("Do not pre-fill an answer slot" in item for item in strategy["arity_and_variable_policy"])
    assert any("Do not over-constrain descriptive label slots" in item for item in strategy["arity_and_variable_policy"])
    assert any("record id too early" in item for item in strategy["arity_and_variable_policy"])
    assert any("source-owned record predicates" in item for item in strategy["arity_and_variable_policy"])
    assert any("institution, ledger, record, or source questions" in item for item in strategy["arity_and_variable_policy"])
    assert any("who-reported or reporter questions" in item for item in strategy["arity_and_variable_policy"])
    assert any("longer normalized atom" in item for item in strategy["arity_and_variable_policy"])
    assert any("grievance(Grievance, Label)" in item for item in strategy["arity_and_variable_policy"])
    assert any("source-attributed claims" in item for item in strategy["epistemic_policy"])
    assert "elapsed_days" in " ".join(strategy["epistemic_policy"])
    assert any("alternate atom order" in item for item in strategy["arity_and_variable_policy"])


def test_score_oracle_can_match_decision_predicate_and_answer_text() -> None:
    row = {
        "projected_decision": "answer",
        "queries": ["declares_recalled(flour_moon_seven, X)."],
        "query_results": [{"result": {"rows": [{"X": "batch_p_44"}]}}],
    }
    oracle = {
        "expected_decision": "answer",
        "expected_query_predicates": ["declares_recalled"],
        "expected_answer_contains": ["batch_p_44"],
    }

    assert score_oracle(row=row, oracle=oracle) is True


def test_summarize_counts_reference_judge_verdicts() -> None:
    rows = [
        {"ok": True, "queries": ["p(X)."], "reference_answer": "A", "reference_judge": {"verdict": "exact"}},
        {"ok": True, "queries": ["q(X)."], "reference_answer": "B", "reference_judge": {"verdict": "partial"}},
        {"ok": True, "queries": [], "reference_answer": "C", "reference_judge": {"verdict": "miss"}},
    ]

    summary = summarize(rows=rows, load_errors=[], elapsed_ms=12)

    assert summary["judge_rows"] == 3
    assert summary["judge_exact"] == 1
    assert summary["judge_partial"] == 1
    assert summary["judge_miss"] == 1


def test_score_oracle_returns_none_without_answer_key() -> None:
    assert score_oracle(row={"queries": []}, oracle={}) is None


def test_temporal_join_builds_dependency_closure_for_derived_threshold() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "facility_status(eastgate_treatment_facility, offline, 2026_03_04t08_00).",
        "eastgate_offline_threshold_hours(6).",
        "boil_water_notice(millbrook, 2026_03_04t14_45, diane_cheng).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    joined = _temporal_join_with_previous(
        runtime,
        previous_queries=[
            "facility_status(eastgate_treatment_facility, offline, Starttime).",
            "eastgate_offline_threshold_hours(Thresholdhours).",
            "add_hours(Starttime, Thresholdhours, Thresholdtime).",
            "boil_water_notice(Zone, Noticetime, Issuer).",
        ],
        query="elapsed_minutes(Thresholdtime, Noticetime, Minutes).",
    )

    assert joined is not None
    result = joined["result"]
    assert result["status"] == "success"
    assert any(str(row.get("Minutes")) == "45" for row in result["rows"])
    assert "facility_status(eastgate_treatment_facility, offline, Starttime)" in joined["query"]
    assert "eastgate_offline_threshold_hours(Thresholdhours)" in joined["query"]


def test_temporal_join_synthesizes_missing_threshold_bridge() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "facility_status(eastgate_treatment_facility, offline, 2026_03_04t08_00).",
        "eastgate_offline_threshold_hours(6).",
        "boil_water_notice(millbrook, 2026_03_04t14_45, diane_cheng).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    joined = _temporal_join_with_previous(
        runtime,
        previous_queries=[
            "facility_status(eastgate_treatment_facility, offline, Starttime).",
            "eastgate_offline_threshold_hours(Thresholdhours).",
            "boil_water_notice(Zone, Noticetime, Issuer).",
        ],
        query="elapsed_minutes(Thresholdtime, Noticetime, Minutes).",
    )

    assert joined is not None
    assert joined["result"]["status"] == "success"
    assert any(str(row.get("Minutes")) == "45" for row in joined["result"]["rows"])
    assert "add_hours(Starttime, Thresholdhours, Thresholdtime)" in joined["query"]


def test_temporal_join_adds_minute_precision_for_elapsed_hours() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "facility_status(eastgate_treatment_facility, offline, 2026_03_04t08_00).",
        "eastgate_offline_threshold_hours(6).",
        "boil_water_notice(millbrook, 2026_03_04t14_45, diane_cheng).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    joined = _temporal_join_with_previous(
        runtime,
        previous_queries=[
            "facility_status(eastgate_treatment_facility, offline, Starttime).",
            "eastgate_offline_threshold_hours(Thresholdhours).",
            "boil_water_notice(Zone, Noticetime, Issuer).",
        ],
        query="elapsed_hours(Thresholdtime, Noticetime, Elapsedhours).",
    )

    assert joined is not None
    assert "elapsed_minutes(Thresholdtime, Noticetime, Minutes)" in joined["query"]
    assert any(
        str(row.get("Elapsedhours")) == "0" and str(row.get("Minutes")) == "45"
        for row in joined["result"]["rows"]
    )


def test_temporal_join_supports_elapsed_days_for_inspection_windows() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "inspection(pier_7, luis_ferreira, 2026_02_01).",
        "bypass_authorization(pier_7, luis_ferreira, 2026_03_04t15_30).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    joined = _temporal_join_with_previous(
        runtime,
        previous_queries=[
            "inspection(Facility, Officer, Inspectiondate).",
            "bypass_authorization(Facility, Officer, Authtime).",
        ],
        query="elapsed_days(Inspectiondate, Authtime, Days).",
    )

    assert joined is not None
    assert joined["result"]["status"] == "success"
    assert any(str(row.get("Days")) == "31" for row in joined["result"]["rows"])


def test_negative_query_join_supports_set_difference() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    for fact in [
        "residential_zone(millbrook).",
        "residential_zone(old_harbor).",
        "boil_water_notice(millbrook, 2026_03_04t14_45, diane_cheng).",
    ]:
        assert runtime.assert_fact(fact).get("status") == "success"

    joined = _negative_join_with_previous(
        runtime,
        previous_queries=["residential_zone(Zone)."],
        query="\\+(boil_water_notice(Zone, Time, Issuer)).",
    )

    assert joined is not None
    assert joined["result"]["status"] == "success"
    assert joined["result"]["rows"][0]["Zone"] == "old_harbor"


def test_relaxed_constant_query_recovers_over_bound_atom_drift() -> None:
    runtime = CorePrologRuntime(max_depth=200)
    assert runtime.assert_fact("inspection(pier_7, luis_ferreira, 2026_02_01).").get("status") == "success"

    exact = runtime.query_rows("inspection(pier_7, ferreira_luis, Date).")
    assert exact["status"] == "no_results"

    relaxed = _relaxed_constant_query(runtime, query="inspection(pier_7, ferreira_luis, Date).")

    assert relaxed is not None
    assert relaxed["result"]["status"] == "success"
    assert relaxed["result"]["reasoning_basis"]["kind"] == "core-local"
    assert relaxed["result"]["reasoning_basis"]["original_query"] == "inspection(pier_7, ferreira_luis, Date)."
    assert relaxed["result"]["rows"] == [
        {
            "Relaxed1": "pier_7",
            "Relaxed2": "luis_ferreira",
            "Date": "2026_02_01",
        }
    ]
