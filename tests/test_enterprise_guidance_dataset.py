import json
import re
from pathlib import Path

from kb_pipeline import CorePrologRuntime
from scripts.run_domain_bootstrap_qa import (
    compact_relevant_clauses_for_evidence_plan,
    parse_markdown_answer_key,
    parse_numbered_markdown_questions,
    run_evidence_bundle_plan_queries,
)


ROOT = Path(__file__).resolve().parents[1]
ANAPLAN = ROOT / "datasets" / "enterprise_guidance" / "anaplan_polaris_performance_rules"


def test_anaplan_polaris_bundle_is_complete() -> None:
    expected = {
        "README.md",
        "source.md",
        "gold_kb.pl",
        "ontology_registry.json",
        "failure_buckets.json",
        "qa.md",
        "qa_battery.jsonl",
        "progress_journal.md",
        "progress_metrics.jsonl",
    }

    assert expected.issubset({path.name for path in ANAPLAN.iterdir()})


def test_anaplan_polaris_qa_battery_is_harness_ready() -> None:
    records = [
        json.loads(line)
        for line in (ANAPLAN / "qa_battery.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(records) == 43
    assert records[0]["id"] == "q001"
    assert records[-1]["id"] == "q043"
    assert any(row["phase"] == "tradeoff" for row in records)
    assert any("priority" in row["phase"] for row in records)

    qa_text = (ANAPLAN / "qa.md").read_text(encoding="utf-8")
    questions = parse_numbered_markdown_questions(qa_text)
    answers = parse_markdown_answer_key(qa_text)
    assert len(questions) == 43
    assert len(answers) == 43
    assert questions[0]["id"] == "q001"
    assert "Calculation Effort" in answers["q001"]
    assert "Full clear-and-reload" in answers["q032"]


def test_anaplan_polaris_gold_kb_exercises_guidance_edges() -> None:
    kb = (ANAPLAN / "gold_kb.pl").read_text(encoding="utf-8")
    for clause in [
        "optimization_priority(high_calc_effort_high_complexity_high_gb, 1).",
        "does_not_directly_determine(gb, performance).",
        "tradeoff(split_nested_if_formula, greater_parallelization, may_force_more_cells_to_calculate).",
        "workspace_rule(max_polaris_models_per_workspace, 1).",
        "intraday_update_rule(reporting_model, avoid_full_clear_and_reload).",
        "incremental_filter(current_not_equal_previous).",
    ]:
        assert clause in kb
    assert len(re.findall(r"^computationally_intensive_function\(", kb, flags=re.MULTILINE)) == 5
    assert len(re.findall(r"^higher_effort_aggregation\(", kb, flags=re.MULTILINE)) == 6


def test_anaplan_polaris_metadata_is_graph_ready() -> None:
    buckets = json.loads((ANAPLAN / "failure_buckets.json").read_text(encoding="utf-8"))
    registry = json.loads((ANAPLAN / "ontology_registry.json").read_text(encoding="utf-8"))
    metrics = [
        json.loads(line)
        for line in (ANAPLAN / "progress_metrics.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert len(buckets["buckets"]) >= 8
    assert any(item["id"] == "F2_priority_order_loss" for item in buckets["buckets"])
    assert registry["source"] == "starter_profile_not_gold_kb"
    signatures = {item["signature"] for item in registry["predicates"]}
    for signature in [
        "optimization_priority/2",
        "tradeoff/3",
        "debugging_tactic/2",
        "intraday_update_rule/2",
        "workspace_rule/2",
    ]:
        assert signature in signatures
    assert [row["timestamp"] for row in metrics] == sorted(row["timestamp"] for row in metrics)


def test_anaplan_polaris_fixture_text_is_ascii_stable() -> None:
    mojibake_pattern = "\u00c3\u00a2|\u00e2\u201a\u00ac\u00e2\u201e\u00a2|\u00e2\u201a\u00ac\u00c5\u201c|\u00e2\u201a\u00ac"
    for path in ANAPLAN.iterdir():
        if path.suffix.lower() not in {".md", ".pl", ".json", ".jsonl"}:
            continue
        text = path.read_text(encoding="utf-8")
        assert all(ord(char) < 128 for char in text), path.name
        assert re.search(mojibake_pattern, text) is None


def test_evidence_bundle_context_filter_uses_plan_predicates_without_question_parsing() -> None:
    plan = {
        "schema_version": "evidence_bundle_plan_v1",
        "support_bundles": [
            {
                "bundle_id": "b1",
                "purpose": "subgrant support",
                "query_templates": ["subgrant_purpose(subgrant_schutz, Purpose)."],
                "missing_if_empty": "missing",
            }
        ],
        "question_focus": "subgrant",
        "warnings": [],
    }
    facts = [
        "unrelated(alpha).",
        "subgrant_purpose(subgrant_schutz, theoretical_calculations).",
        "subgrant_amount(subgrant_schutz, 45_000).",
    ]

    selected = compact_relevant_clauses_for_evidence_plan(
        evidence_plan=plan,
        facts=facts,
        rules=[],
        max_clauses=3,
        broad_floor=1,
    )

    assert selected[0] == "subgrant_purpose(subgrant_schutz, theoretical_calculations)."
    assert "unrelated(alpha)." in selected


def test_evidence_bundle_plan_queries_are_inventory_validated_and_query_only() -> None:
    runtime = CorePrologRuntime(max_depth=50)
    assert runtime.assert_fact("subgrant_purpose(subgrant_schutz, theoretical_calculations).")["status"] == "success"
    assert runtime.assert_fact("subgrant_amount(subgrant_schutz, 45_000).")["status"] == "success"
    plan = {
        "schema_version": "evidence_bundle_plan_v1",
        "support_bundles": [
            {
                "bundle_id": "b1",
                "purpose": "subgrant support",
                "query_templates": [
                    "subgrant_purpose(subgrant_schutz, Purpose).",
                    "invented_predicate(X).",
                ],
                "missing_if_empty": "missing",
            }
        ],
        "question_focus": "subgrant",
        "warnings": [],
    }

    results = run_evidence_bundle_plan_queries(
        runtime=runtime,
        evidence_plan=plan,
        kb_inventory={"signatures": ["subgrant_purpose/2"], "counts": {}, "examples": {}},
    )

    statuses = [item["result"]["status"] for item in results]
    assert "success" in statuses
    assert "error" in statuses
    assert any(
        item["result"].get("reasoning_basis", {}).get("validation") == "predicate_and_arity_checked"
        for item in results
    )


def test_domain_companion_queries_follow_structured_committee_and_fsrb_predicates() -> None:
    from scripts.run_domain_bootstrap_qa import run_query_plan

    runtime = CorePrologRuntime(max_depth=50)
    for fact in [
        "committee_member(investigation_committee, okonkwo, member).",
        "committee_member_replaced(investigation_committee, okonkwo, bergstrom, june_3).",
        "fsrb_may(overturn_provost_determination).",
        "deadline_requirement(fsrb_overturn_notice, 10, business_days, fsrb_decision_date).",
        "fsrb_decision_effect(fsrb_overturns, expunge_finding).",
    ]:
        assert runtime.assert_fact(fact)["status"] == "success"

    results = run_query_plan(
        runtime,
        [
            "committee_member(investigation_committee, Member, Role).",
            "fsrb_may(overturn_provost_determination).",
        ],
    )
    queries = [item["query"] for item in results]

    assert "committee_member_replaced(investigation_committee, OldMember, NewMember, ReplacementDate)." in queries
    assert "deadline_requirement(Deadline, Amount, Unit, fsrb_decision_date)." in queries
    assert "fsrb_decision_effect(Condition, Effect)." in queries
