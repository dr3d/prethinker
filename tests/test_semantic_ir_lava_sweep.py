from __future__ import annotations

from scripts.run_semantic_ir_lava_sweep import apply_mapped_directly, filter_lava_cases, score_expectation, select_base_cases
from scripts.run_semantic_ir_lava_sweep import load_frontier_pack_cases
from scripts.run_semantic_ir_lava_sweep import LavaCase
from src.mcp_server import PrologMCPServer


def test_lava_direct_apply_records_but_skips_queries_by_default():
    server = PrologMCPServer()
    mapped = {
        "intent": "query",
        "admission_diagnostics": {
            "clauses": {
                "facts": ["parent(noel, rhea)."],
                "rules": ["ancestor(X, Y) :- parent(X, Y)."],
                "queries": ["ancestor(noel, rhea)."],
                "retracts": [],
            }
        },
    }

    result = apply_mapped_directly(server, mapped)

    assert result["status"] == "success"
    assert result["writes_applied"] == 2
    assert result["errors"] == []
    assert result["operations"][-1]["tool"] == "query_rows"
    assert result["operations"][-1]["result"]["status"] == "skipped"
    assert server.query_rows("ancestor(noel, rhea).")["status"] == "success"


def test_lava_balanced_sampling_spreads_source_families():
    cases = [
        LavaCase(id=f"rung_{i}", source="kb_scenario:rung_many", utterance=f"rung {i}")
        for i in range(12)
    ]
    cases.extend(
        [
            LavaCase(id="medical", source="medical", utterance="Mara's pressure is high."),
            LavaCase(id="legal", source="dataset:legal_seed", utterance="Court held X."),
            LavaCase(id="story", source="goldilocks", utterance="Goldilocks found porridge."),
        ]
    )

    import random

    selected = select_base_cases(cases, limit=4, mode="balanced", rng=random.Random(7))
    sources = {case.source.split(":", 1)[0] for case in selected}

    assert len(selected) == 4
    assert {"medical", "dataset", "goldilocks"} <= sources


def test_lava_pack_v2_loads_with_expected_profile_coverage():
    from pathlib import Path

    cases = [
        case
        for case in load_frontier_pack_cases(Path("docs/data/frontier_packs"))
        if case.source.endswith("semantic_ir_lava_pack_v2")
    ]
    profiles = {case.expected_profile for case in cases}

    assert len(cases) == 36
    assert {
        "medical@v0",
        "legal_courtlistener@v0",
        "sec_contracts@v0",
        "story_world@v0",
        "probate@v0",
    } <= profiles
    assert all(case.expect and case.expect.get("must") for case in cases)


def test_lava_pack_v3_records_calibration_status_with_bootstrap_pressure():
    import json
    from pathlib import Path

    path = Path("docs/data/frontier_packs/semantic_ir_lava_pack_v3.json")
    metadata = json.loads(path.read_text(encoding="utf-8"))
    cases = [
        case
        for case in load_frontier_pack_cases(Path("docs/data/frontier_packs"))
        if case.source.endswith("semantic_ir_lava_pack_v3")
    ]
    profiles = {case.expected_profile for case in cases}

    assert metadata["status"] == "calibration_after_first_held_out_run"
    assert "First held-out result" in metadata["validation_note"]
    assert len(cases) >= 16
    assert {
        "medical@v0",
        "legal_courtlistener@v0",
        "sec_contracts@v0",
        "story_world@v0",
        "probate@v0",
        "bootstrap",
    } <= profiles
    assert all(case.expect and case.expect.get("avoid") for case in cases)


def test_lava_pack_v4_targets_next_architecture_hazards():
    import json
    from pathlib import Path

    path = Path("docs/data/frontier_packs/semantic_ir_lava_pack_v4.json")
    metadata = json.loads(path.read_text(encoding="utf-8"))
    cases = [
        case
        for case in load_frontier_pack_cases(Path("docs/data/frontier_packs"))
        if case.source.endswith("semantic_ir_lava_pack_v4")
    ]
    profiles = {case.expected_profile for case in cases}
    hazards = {row.get("hazard") for row in metadata["cases"]}

    assert metadata["status"] == "fresh_held_out_candidate"
    assert len(cases) == 25
    assert hazards == {
        "truth_maintenance_explosion",
        "predicate_canonicalization_drift",
        "claim_fact_observation_epistemology",
        "segmentation_semantics",
        "multilingual_ontology_pressure",
    }
    assert {
        "medical@v0",
        "legal_courtlistener@v0",
        "sec_contracts@v0",
        "story_world@v0",
        "probate@v0",
    } <= profiles
    assert all(case.expect and case.expect.get("must") and case.expect.get("avoid") for case in cases)


def test_lava_source_filter_matches_source_or_id():
    cases = [
        LavaCase(id="alpha_case", source="frontier:semantic_ir_lava_pack_v2", utterance="a"),
        LavaCase(id="beta_special", source="dataset:other", utterance="b"),
        LavaCase(id="gamma", source="dataset:other", utterance="c"),
    ]

    assert [case.id for case in filter_lava_cases(cases, source_filter="lava_pack_v2")] == ["alpha_case"]
    assert [case.id for case in filter_lava_cases(cases, source_filter="beta")] == ["beta_special"]


def test_lava_expectation_separates_diagnostic_mentions_from_admitted_unsafe_clauses():
    case = LavaCase(
        id="spanish_probate",
        source="frontier:test",
        utterance="x",
        expected_decision="mixed",
        expect={
            "decision": "mixed",
            "must": ["London, Ontario"],
            "avoid": ["london_uk"],
        },
    )
    ir = {
        "self_check": {
            "notes": [
                "The correction says this was London, Ontario, not london_uk.",
            ]
        }
    }
    record = {
        "projected_decision": "mixed",
        "clauses": {"facts": ["resided_in(beatriz, london_ontario, interval_1)."]},
        "mapper_warnings": [],
        "fuzzy_edge_kinds": [],
    }

    score = score_expectation(case, record, ir=ir)

    assert score["must_hits"] == 1
    assert score["missing_must"] == []
    assert score["avoid_hits"] == ["london_uk"]
    assert score["avoid_asserted_hits"] == []
    assert score["avoid_durable_hits"] == []
    assert score["avoid_admitted_hits"] == []
    assert score["semantic_clean"] is False
    assert score["admission_safe"] is True
    assert score["ok"] is True


def test_lava_expectation_does_not_treat_queries_as_durable_bad_writes():
    case = LavaCase(
        id="access_query",
        source="frontier:test",
        utterance="x",
        expected_decision="mixed",
        expect={
            "decision": "mixed",
            "must": ["Theo"],
            "avoid": ["access_grant(theo, production"],
        },
    )
    record = {
        "projected_decision": "mixed",
        "clauses": {
            "facts": ["expires_on(b_14, before_approval)."],
            "queries": ["access_grant(theo, production, sponsor_badge_b_14, current_state)."],
            "rules": [],
            "retracts": [],
        },
        "mapper_warnings": [],
        "fuzzy_edge_kinds": [],
    }

    score = score_expectation(case, record, ir={"note": "Theo access question"})

    assert score["missing_must"] == []
    assert score["avoid_asserted_hits"] == []
    assert score["avoid_query_hits"] == ["access_grant(theo, production"]
    assert score["avoid_durable_hits"] == []
    assert score["admission_safe"] is True
    assert score["ok"] is True


def test_lava_expectation_treats_forbidden_retracts_as_safe_admission():
    case = LavaCase(
        id="correct_bad_old_fact",
        source="frontier:test",
        utterance="x",
        expected_decision="mixed",
        expect={
            "decision": "mixed",
            "must": ["London, Ontario"],
            "avoid": ["london_uk"],
        },
    )
    record = {
        "projected_decision": "mixed",
        "clauses": {
            "facts": ["resided_in(beatriz, london_ontario, interval_1)."],
            "retracts": ["resided_outside_country(beatriz, london_uk, old_interval)."],
        },
        "mapper_warnings": [],
        "fuzzy_edge_kinds": [],
    }

    score = score_expectation(case, record, ir={"note": "Correction to London, Ontario from london_uk"})

    assert score["avoid_retract_hits"] == ["london_uk"]
    assert score["avoid_asserted_hits"] == []
    assert score["admission_safe"] is True
    assert score["ok"] is True
