import json
import sys

from scripts import select_qa_mode_without_oracle
from scripts.select_qa_mode_without_oracle import (
    call_selector,
    compile_guard_disable_regex,
    hybrid_selector,
    load_group,
    merge_qa_records,
    protected_selector,
    score_selection,
    selector_system_prompt,
    structural_baseline_answer_surface_guard_reason,
    structural_identity_completeness_trap_reason,
    structural_mode_scores,
    structural_operational_record_status_trap_reason,
    structural_rationale_contrast_trap_reason,
    structural_selector,
    structural_specialized_answer_surface_override,
    structural_volume_trap_reason,
)


def _mode_with_predicates(mode: str, predicates: list[str], *, rows: int = 1, relaxed: bool = False) -> dict:
    return {
        "mode": mode,
        "query_evidence": {
            "executed_results": [
                {
                    "status": "success",
                    "num_rows": rows,
                    "predicate": predicate,
                    "was_relaxed_fallback": relaxed,
                }
                for predicate in predicates
            ],
            "warnings": [],
            "parse_error": "",
        },
    }


def test_structural_selector_prefers_direct_rows_without_model_call() -> None:
    row = {
        "id": "q001",
        "modes": [
            {
                "mode": "plain",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "no_results",
                            "num_rows": 0,
                            "predicate": "answer_row",
                            "was_relaxed_fallback": False,
                        }
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "evidence",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 2,
                            "predicate": "answer_row",
                            "was_relaxed_fallback": False,
                        }
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = structural_selector(row=row, mode_labels=["plain", "evidence"])

    assert selected["selected_mode"] == "evidence"
    assert selected["evidence_quality_by_mode"][0]["mode"] == "evidence"


def test_structural_selector_downweights_relaxed_fallbacks() -> None:
    row = {
        "id": "q002",
        "modes": [
            {
                "mode": "plain",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "answer_row",
                            "was_relaxed_fallback": False,
                        }
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "evidence",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 2,
                            "predicate": "answer_row",
                            "was_relaxed_fallback": True,
                        }
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = structural_selector(row=row, mode_labels=["plain", "evidence"])

    assert selected["selected_mode"] == "plain"


def test_hybrid_selector_skips_model_when_structural_choice_is_confident() -> None:
    row = {
        "id": "q003",
        "modes": [
            {
                "mode": "plain",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "no_results",
                            "num_rows": 0,
                            "predicate": "answer_row",
                            "was_relaxed_fallback": False,
                        }
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "evidence",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 5,
                            "predicate": "answer_row",
                            "was_relaxed_fallback": False,
                        }
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }
    fallback_calls = 0

    def fallback_selector(**_kwargs):
        nonlocal fallback_calls
        fallback_calls += 1
        return {"selected_mode": "plain"}

    selected = hybrid_selector(
        row=row,
        mode_labels=["plain", "evidence"],
        margin=1.5,
        min_score=3.0,
        fallback_selector=fallback_selector,
    )

    assert fallback_calls == 0
    assert selected["selected_mode"] == "evidence"
    assert selected["selection_source"] == "hybrid_structural"


def test_hybrid_selector_calls_model_when_structural_choice_is_uncertain() -> None:
    row = {
        "id": "q004",
        "modes": [
            {
                "mode": "plain",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "answer_row",
                            "was_relaxed_fallback": False,
                        }
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "evidence",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "answer_row",
                            "was_relaxed_fallback": False,
                        }
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }
    fallback_calls = 0

    def fallback_selector(**_kwargs):
        nonlocal fallback_calls
        fallback_calls += 1
        return {"selected_mode": "evidence", "selection_confidence": 0.73}

    selected = hybrid_selector(
        row=row,
        mode_labels=["plain", "evidence"],
        margin=1.5,
        min_score=3.0,
        fallback_selector=fallback_selector,
    )

    assert fallback_calls == 1
    assert selected["selected_mode"] == "evidence"
    assert selected["selection_source"] == "hybrid_llm"


def test_hybrid_selector_calls_model_for_operational_status_competing_lens() -> None:
    row = {
        "id": "q004b",
        "question": "What is the current operational status of Segment 4?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 8,
                            "predicate": "investigation_status",
                            "was_relaxed_fallback": False,
                        }
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "operational_record",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 2,
                            "predicate": "has_state",
                            "was_relaxed_fallback": False,
                        }
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }
    fallback_calls = 0

    def fallback_selector(**_kwargs):
        nonlocal fallback_calls
        fallback_calls += 1
        return {"selected_mode": "operational_record"}

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "operational_record"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=fallback_selector,
    )

    assert fallback_calls == 1
    assert selected["selected_mode"] == "operational_record"
    assert selected["selection_source"] == "hybrid_llm"
    assert (
        "operational/status question has competing mode with specialized record-state evidence"
        in selected["structural_uncertainty_reasons"]
    )
    assert selected["structural_uncertainty_reasons"]


def test_specialized_guard_routes_valid_period_to_union_validity_surface() -> None:
    row = {
        "id": "q_valid_period",
        "question": "What is the valid period for the Ground Use Permit?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 4, "predicate": "valid_from", "was_relaxed_fallback": False},
                        {"status": "success", "num_rows": 4, "predicate": "valid_to", "was_relaxed_fallback": False},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "union",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 2, "predicate": "valid_from", "was_relaxed_fallback": False},
                        {"status": "success", "num_rows": 2, "predicate": "permit_validity", "was_relaxed_fallback": False},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }
    scored = structural_mode_scores(row=row, mode_labels=["baseline", "union"])

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=scored,
        mode_labels=["baseline", "union"],
        structural_choice="baseline",
    )

    assert override
    assert override[0] == "union"
    assert "valid-period" in override[1]


def test_specialized_guard_routes_reinspection_count_to_compact_aggregate_surface() -> None:
    row = {
        "id": "q_reinspection_count",
        "question": "How many vendors failed the October 15 reinspection?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 21, "predicate": "inspection_result", "was_relaxed_fallback": True},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "union",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 20, "predicate": "inspection_result", "was_relaxed_fallback": True},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "lifecycle",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 5, "predicate": "vendor_status", "was_relaxed_fallback": False},
                        {"status": "success", "num_rows": 1, "predicate": "inspection_record", "was_relaxed_fallback": False},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }
    scored = structural_mode_scores(row=row, mode_labels=["baseline", "union", "lifecycle"])

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=scored,
        mode_labels=["baseline", "union", "lifecycle"],
        structural_choice="lifecycle",
    )

    assert override
    assert override[0] == "union"
    assert "failed-reinspection" in override[1]


def test_specialized_guard_protects_unrestricted_active_count_baseline() -> None:
    row = {
        "id": "q_unrestricted_active",
        "question": "As of October 16, how many of the five permit types are fully active without restrictions?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 6, "predicate": "status_at", "was_relaxed_fallback": False},
                        {"status": "success", "num_rows": 2, "predicate": "restriction_applied", "was_relaxed_fallback": True},
                        {"status": "success", "num_rows": 2, "predicate": "suspension_period", "was_relaxed_fallback": True},
                        {"status": "success", "num_rows": 2, "predicate": "violation_occurred", "was_relaxed_fallback": True},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "union",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 10, "predicate": "status_at", "was_relaxed_fallback": False},
                        {"status": "success", "num_rows": 10, "predicate": "permit_validity", "was_relaxed_fallback": False},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }
    scored = structural_mode_scores(row=row, mode_labels=["baseline", "union"])

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=scored,
        mode_labels=["baseline", "union"],
        structural_choice="union",
    )

    assert override
    assert override[0] == "baseline"
    assert "unrestricted-active" in override[1]


def test_specialized_guard_keeps_source_belief_on_testimony_surface() -> None:
    row = {
        "id": "q_source_belief",
        "question": "What vessel does Strand believe the bell is from?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 2, "predicate": "testimony_by", "was_relaxed_fallback": False},
                        {"status": "success", "num_rows": 1, "predicate": "claim_asserted_by", "was_relaxed_fallback": False},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "union",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 4, "predicate": "testimony_by", "was_relaxed_fallback": False},
                        {"status": "success", "num_rows": 4, "predicate": "candidate_origin", "was_relaxed_fallback": False},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }
    scored = structural_mode_scores(row=row, mode_labels=["baseline", "union"])

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=scored,
        mode_labels=["baseline", "union"],
        structural_choice="union",
    )

    assert override
    assert override[0] == "baseline"
    assert "source-belief" in override[1]


def test_specialized_guard_routes_alternative_inscription_to_union_surface() -> None:
    row = {
        "id": "q_alt_inscription",
        "question": "What alternative vessel names could the inscription represent?",
        "modes": [
            {
                "mode": "candidate",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 4, "predicate": "candidate_origin", "was_relaxed_fallback": False},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "union",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 4, "predicate": "candidate_origin", "was_relaxed_fallback": True},
                        {"status": "success", "num_rows": 1, "predicate": "inscription_fragment", "was_relaxed_fallback": True},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }
    scored = structural_mode_scores(row=row, mode_labels=["candidate", "union"])

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=scored,
        mode_labels=["candidate", "union"],
        structural_choice="candidate",
    )

    assert override
    assert override[0] == "union"
    assert "alternative-inscription" in override[1]


def test_hybrid_selector_calls_model_when_relaxed_volume_dominates() -> None:
    row = {
        "id": "q004b",
        "modes": [
            {
                "mode": "broad",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "broad_row",
                            "was_relaxed_fallback": False,
                        },
                        {
                            "status": "success",
                            "num_rows": 8,
                            "predicate": "broad_row",
                            "was_relaxed_fallback": True,
                        },
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "focused",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "focused_row",
                            "was_relaxed_fallback": False,
                        }
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }
    fallback_calls = 0

    def fallback_selector(**_kwargs):
        nonlocal fallback_calls
        fallback_calls += 1
        return {"selected_mode": "focused", "selection_confidence": 0.7}

    selected = hybrid_selector(
        row=row,
        mode_labels=["broad", "focused"],
        margin=1.0,
        min_score=3.0,
        fallback_selector=fallback_selector,
    )

    assert fallback_calls == 1
    assert selected["selected_mode"] == "focused"
    assert "relaxed fallback volume" in selected["structural_uncertainty_reasons"][0]


def test_volume_trap_does_not_double_penalize_relaxed_only_baseline() -> None:
    row = {
        "id": "q004c",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 8,
                            "predicate": "fallback_row",
                            "was_relaxed_fallback": True,
                        }
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "variant",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "direct_row",
                            "was_relaxed_fallback": False,
                        }
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    scored = structural_mode_scores(row=row, mode_labels=["baseline", "variant"])

    assert structural_volume_trap_reason(scored) == ""


def test_structural_selector_demotes_source_record_facts_primary_surface() -> None:
    row = {
        "id": "q001",
        "question": "Who has legal title to Notebook A as of 2026-04-30?",
        "modes": [
            {
                "mode": "source_record_facts",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 20,
                            "predicate": "source_record_field_value",
                            "was_relaxed_fallback": False,
                        },
                        {
                            "status": "success",
                            "num_rows": 10,
                            "predicate": "source_record_text_key",
                            "was_relaxed_fallback": True,
                        },
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "entity",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 2,
                            "predicate": "legal_title_holder",
                            "was_relaxed_fallback": False,
                        }
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = structural_selector(row=row, mode_labels=["source_record_facts", "entity"])

    assert selected["selected_mode"] == "entity"
    assert selected["structural_candidate"] == "source_record_facts"
    assert "addressability scaffolding" in selected["source_record_facts_demotion_reason"]


def test_structural_selector_keeps_source_record_facts_without_semantic_alternative() -> None:
    row = {
        "id": "q017",
        "question": "How many active labels remain in the master inventory after withdrawals?",
        "modes": [
            {
                "mode": "source_record_facts",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "source_record_field_value",
                            "was_relaxed_fallback": False,
                        }
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "parallel",
                "query_evidence": {
                    "executed_results": [],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = structural_selector(row=row, mode_labels=["source_record_facts", "parallel"])

    assert selected["selected_mode"] == "source_record_facts"
    assert "source_record_facts_demotion_reason" not in selected


def test_structural_selector_demotes_memory_ledger_combo_to_focused_surface() -> None:
    row = {
        "id": "q003",
        "question": "What bonus percentage does section 3.2 award?",
        "modes": [
            {
                "mode": "memory_ledger_combo",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 5,
                            "predicate": "ledger_row",
                            "was_relaxed_fallback": False,
                        },
                        {
                            "status": "success",
                            "num_rows": 10,
                            "predicate": "source_record_field_value",
                            "was_relaxed_fallback": True,
                        },
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "source_record",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 2,
                            "predicate": "bonus_percentage",
                            "was_relaxed_fallback": False,
                        }
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = structural_selector(row=row, mode_labels=["memory_ledger_combo", "source_record"])

    assert selected["selected_mode"] == "source_record"
    assert selected["structural_candidate"] == "memory_ledger_combo"
    assert "memory-ledger combo" in selected["memory_ledger_combo_demotion_reason"]


def test_raw_timestamp_guard_prefers_raw_timestamp_surface() -> None:
    row = {
        "id": "q007",
        "question": "What is the raw (uncorrected) timestamp of BAS-002?",
        "modes": [
            _mode_with_predicates("cold", ["recorded_access_event", "clock_drift_applied"], rows=6),
            _mode_with_predicates("entity", ["raw_timestamp"], rows=2),
        ],
    }

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=["cold", "entity"]),
        mode_labels=["cold", "entity"],
        structural_choice="cold",
    )

    assert override == (
        "entity",
        "raw-timestamp question needs explicit raw_timestamp surface rather than corrected/event-correlation volume",
    )


def test_hybrid_guard_disable_regex_skips_matching_specialized_guard() -> None:
    row = {
        "id": "q007",
        "question": "What is the raw (uncorrected) timestamp of BAS-002?",
        "modes": [
            _mode_with_predicates("cold", ["recorded_access_event", "clock_drift_applied"], rows=6),
            _mode_with_predicates("entity", ["raw_timestamp"], rows=2),
        ],
    }

    def fallback_selector(*, row: dict, mode_labels: list[str]) -> dict:
        return {
            "schema_version": "qa_mode_selector_v1",
            "selected_mode": "cold",
            "selection_confidence": 0.5,
            "evidence_quality_by_mode": [],
            "rationale": "fallback after disabled guard",
            "risks": [],
        }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "entity"],
        margin=0,
        min_score=0,
        fallback_selector=fallback_selector,
        guard_disable_regex=compile_guard_disable_regex("raw-timestamp question"),
    )

    assert selected["selected_mode"] == "cold"
    assert "specialized_guard_reason" not in selected
    assert selected["disabled_guard_reasons"] == [
        "raw-timestamp question needs explicit raw_timestamp surface rather than corrected/event-correlation volume"
    ]


def test_hybrid_guard_disable_regex_leaves_nonmatching_specialized_guard_active() -> None:
    row = {
        "id": "q007",
        "question": "What is the raw (uncorrected) timestamp of BAS-002?",
        "modes": [
            _mode_with_predicates("cold", ["recorded_access_event", "clock_drift_applied"], rows=6),
            _mode_with_predicates("entity", ["raw_timestamp"], rows=2),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "entity"],
        margin=0,
        min_score=0,
        fallback_selector=lambda *, row, mode_labels: {},
        guard_disable_regex=compile_guard_disable_regex("sampler-offline"),
    )

    assert selected["selected_mode"] == "entity"
    assert "raw-timestamp question" in selected["specialized_guard_reason"]
    assert "disabled_guard_reasons" not in selected


def test_guard_disable_regex_reports_invalid_pattern() -> None:
    try:
        compile_guard_disable_regex("[")
    except ValueError as exc:
        assert "invalid --disable-guard-reason-regex" in str(exc)
    else:  # pragma: no cover - defensive
        raise AssertionError("invalid guard-disable regex should fail")


def test_snapshot_state_guard_prefers_sampler_status_surface() -> None:
    row = {
        "id": "q027",
        "question": "What was the operational state of sampler S-3 at 2026-04-30 12:00 according to the snapshot table?",
        "modes": [
            _mode_with_predicates("cold", ["event_description", "event_corrected_from"], rows=14),
            _mode_with_predicates("parallel", ["sampler_status"], rows=1),
            _mode_with_predicates("entity", ["sampler_state"], rows=4),
        ],
    }

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=["cold", "parallel", "entity"]),
        mode_labels=["cold", "parallel", "entity"],
        structural_choice="cold",
    )

    assert override == (
        "parallel",
        "snapshot-state question needs sampler status surface rather than broad event-description volume",
    )


def test_snapshot_state_guard_prefers_state_plus_cause_when_available() -> None:
    row = {
        "id": "q027",
        "question": "What was the operational state of sampler S-3 at 2026-04-29 04:30 according to the snapshot table?",
        "modes": [
            _mode_with_predicates("cold", ["event_description", "event_corrected_from"], rows=14),
            _mode_with_predicates("parallel", ["sampler_status"], rows=1),
            _mode_with_predicates("entity", ["sampler_state", "sampler_state_cause"], rows=4),
        ],
    }

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=["cold", "parallel", "entity"]),
        mode_labels=["cold", "parallel", "entity"],
        structural_choice="cold",
    )

    assert override == (
        "entity",
        "snapshot-state question needs sampler state-plus-cause surface when the snapshot row asks why that state held",
    )


def test_snapshot_state_guard_falls_back_to_sampler_state_surface() -> None:
    row = {
        "id": "q027b",
        "question": "What was the operational state of sampler S-3 at 2026-04-29 04:30 according to the snapshot table?",
        "modes": [
            _mode_with_predicates("cold", ["event_description", "event_corrected_from"], rows=14),
            _mode_with_predicates("entity", ["sampler_state"], rows=4),
        ],
    }

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=["cold", "entity"]),
        mode_labels=["cold", "entity"],
        structural_choice="cold",
    )

    assert override == (
        "entity",
        "snapshot-state question needs explicit sampler_state surface rather than broad event-description or status volume",
    )


def test_clear_sample_clock_snapshot_guard_prefers_elapsed_segment_helper_surface() -> None:
    row = {
        "id": "q029",
        "question": "What was the state of the clear-sample clock at 2026-05-01 10:00 according to the snapshot table, and how many hours had been counted?",
        "modes": [
            _mode_with_predicates("source_record_facts_v2", ["source_record_row", "source_record_cell"], rows=21),
            _mode_with_predicates("parallel", ["clear_sample_segment", "elapsed_hours", "elapsed_minutes"], rows=2),
        ],
    }

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=["source_record_facts_v2", "parallel"]),
        mode_labels=["source_record_facts_v2", "parallel"],
        structural_choice="source_record_facts_v2",
    )

    assert override == (
        "parallel",
        "clear-sample clock snapshot question needs segment-plus-elapsed-time helper surface rather than snapshot text alone",
    )


def test_badge_id_guard_prefers_unresolved_identity_badge_surface() -> None:
    row = {
        "id": "q003",
        "question": "What is T. Aldridge's badge ID?",
        "modes": [
            _mode_with_predicates("source_record", ["source_record", "source_reliability_scope"], rows=5),
            _mode_with_predicates("cold", ["badge_holder_unidentified", "identity_status", "recorded_access_event"], rows=12),
        ],
    }

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=["source_record", "cold"]),
        mode_labels=["source_record", "cold"],
        structural_choice="source_record",
    )

    assert override == (
        "cold",
        "badge-id question with unresolved holder needs identity-status badge surface rather than nearest source-record usage",
    )


def test_corrected_timestamp_guard_prefers_corrected_timestamp_surface() -> None:
    row = {
        "id": "q011",
        "question": "What is the corrected timestamp of event E-04 under §6.5?",
        "modes": [
            _mode_with_predicates("cold", ["event_corrected_from", "rule_description"], rows=1),
            _mode_with_predicates("entity", ["event_corrected_timestamp", "event_description"], rows=1),
        ],
    }

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=["cold", "entity"]),
        mode_labels=["cold", "entity"],
        structural_choice="cold",
    )

    assert override == (
        "entity",
        "corrected-timestamp question needs explicit corrected-timestamp surface rather than rule-description context",
    )


def test_corrected_duration_guard_prefers_paired_badge_timestamps() -> None:
    row = {
        "id": "q015",
        "question": "How long, on the corrected timeline, was the badge holder inside Lab 4-C?",
        "modes": [
            _mode_with_predicates("source_record", ["corrected_timestamp"], rows=18),
            _mode_with_predicates("parallel", ["badge_used", "raw_timestamp", "corrected_timestamp"], rows=1, relaxed=True),
        ],
    }

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=["source_record", "parallel"]),
        mode_labels=["source_record", "parallel"],
        structural_choice="source_record",
    )

    assert override == (
        "parallel",
        "corrected-duration question needs paired raw/corrected badge-event surface rather than corrected timestamp volume alone",
    )


def test_same_item_guard_prefers_current_identity_description_surface() -> None:
    row = {
        "id": "q015",
        "question": "Are EX-E-09 and EX-E-10 the same item? Briefly explain.",
        "modes": [
            _mode_with_predicates("source_record_facts", ["withdrawn_label", "current_label"], rows=6),
            _mode_with_predicates("source_record", ["has_current_label", "item_description", "label_withdrawn"], rows=1),
        ],
    }

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=["source_record_facts", "source_record"]),
        mode_labels=["source_record_facts", "source_record"],
        structural_choice="source_record_facts",
    )

    assert override == (
        "source_record",
        "same-item question needs current item identity/description surface rather than withdrawn-label evidence alone",
    )


def test_near_duplicate_bin_code_guard_prefers_collision_location_surface() -> None:
    row = {
        "id": "q020",
        "question": "Which two folder labels and which two bin codes form a near-duplicate pair, and which item belongs in each?",
        "modes": [
            _mode_with_predicates("source_record_facts", ["current_label", "current_location"], rows=12),
            _mode_with_predicates("entity", ["bin_location", "collision_risk", "item_description"], rows=55),
        ],
    }

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=["source_record_facts", "entity"]),
        mode_labels=["source_record_facts", "entity"],
        structural_choice="source_record_facts",
    )

    assert override == (
        "entity",
        "near-duplicate bin-code question needs collision-risk plus bin-location surface rather than generic current-label rows",
    )


def test_active_held_count_guard_prefers_current_label_status_filter_surface() -> None:
    row = {
        "id": "q040",
        "question": "Counting only currently active labels and excluding any item that has already been released from custody, how many items remain physically held in the evidence room?",
        "modes": [
            _mode_with_predicates("cold", ["current_exhibit_label", "item_status"], rows=27),
            _mode_with_predicates("source_record_facts", ["current_label", "current_status", "withdrawn_label"], rows=14),
        ],
    }

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=["cold", "source_record_facts"]),
        mode_labels=["cold", "source_record_facts"],
        structural_choice="cold",
    )

    assert override == (
        "source_record_facts",
        "active-held count question needs current-label/status plus withdrawn-label filter surface",
    )


def test_publication_authority_guard_prefers_publication_restriction_surface() -> None:
    row = {
        "id": "q004",
        "question": "Who has authority to publish facsimile reproductions of Notebook A's contents, and is that authority currently active?",
        "modes": [
            _mode_with_predicates("parallel", ["access_authorization", "publication_restriction"], rows=20),
            _mode_with_predicates("source_record_facts_v2", ["publication_authority", "policy_restriction", "source_record_row"], rows=9),
            _mode_with_predicates("source_record", ["publication_authority", "policy_restriction", "board_resolution"], rows=5),
        ],
    }

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=["parallel", "source_record_facts_v2", "source_record"]),
        mode_labels=["parallel", "source_record_facts_v2", "source_record"],
        structural_choice="parallel",
    )

    assert override == (
        "source_record",
        "publication-authority question needs publication holder plus active restriction surface rather than broad access-authority volume",
    )


def test_personal_letter_reading_access_guard_avoids_raw_source_rows() -> None:
    row = {
        "id": "q019",
        "question": "As of 2026-04-30, may a researcher read a personal letter at Pellico's reading room?",
        "modes": [
            _mode_with_predicates("source_record_facts_v2", ["access_authority", "source_record_row"], rows=12),
            _mode_with_predicates("source_record", ["access_authority", "board_resolution", "publication_authority"], rows=30),
            _mode_with_predicates("memory_ledger_combo", ["access_authorized_by", "board_resolution", "publication_authority"], rows=4),
        ],
    }

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=["source_record_facts_v2", "source_record", "memory_ledger_combo"]),
        mode_labels=["source_record_facts_v2", "source_record", "memory_ledger_combo"],
        structural_choice="source_record",
    )

    assert override == (
        "memory_ledger_combo",
        "personal-letter reading-access question needs semantic access authority plus publication-restriction boundary, not raw source rows alone",
    )


def test_physical_custody_item_count_guard_prefers_grouped_count_helper() -> None:
    row = {
        "id": "q022",
        "question": "How many items remain in Pellico's physical custody as of 2026-04-30?",
        "modes": [
            _mode_with_predicates("parallel", ["physical_custodian"], rows=3),
            _mode_with_predicates("authority_helper", ["archive_authority_custody_support", "physical_custody"], rows=7),
        ],
    }

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=["parallel", "authority_helper"]),
        mode_labels=["parallel", "authority_helper"],
        structural_choice="parallel",
    )

    assert override == (
        "authority_helper",
        "physical-custody item-count question needs grouped custody count helper rather than raw custodian row count",
    )


def test_governing_custody_document_guard_prefers_exact_source_row_text() -> None:
    row = {
        "id": "q026",
        "question": "Which 2024 document governs the conservator's right to physical custody, and what does it specify?",
        "modes": [
            _mode_with_predicates("parallel", ["agreement_clause"], rows=3),
            _mode_with_predicates("source_record_facts_v2", ["source_record_row", "source_record_text_atom", "source_record_cell"], rows=8),
        ],
    }

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=["parallel", "source_record_facts_v2"]),
        mode_labels=["parallel", "source_record_facts_v2"],
        structural_choice="parallel",
    )

    assert override == (
        "source_record_facts_v2",
        "governing-2024-custody-document question needs exact amendment source-row text with custody/notice clauses",
    )


def test_arbitrator_unresolved_question_guard_prefers_dispute_scope_surface() -> None:
    row = {
        "id": "q015",
        "question": "What is the second unresolved question that the arbitrator has authority to determine?",
        "modes": [
            _mode_with_predicates("source_record", ["dispute_status", "dispute_subject"], rows=4),
            _mode_with_predicates("entity", ["dispute_scope"], rows=2),
        ],
    }

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=["source_record", "entity"]),
        mode_labels=["source_record", "entity"],
        structural_choice="source_record",
    )

    assert override == (
        "entity",
        "arbitrator-unresolved-question row needs dispute-scope/topic surface rather than broad dispute-status volume",
    )


def test_notebook_location_pause_guard_prefers_custody_restriction_surface() -> None:
    row = {
        "id": "q033",
        "question": "Where is Notebook A located as of 2026-04-30, and is its publication paused?",
        "modes": [
            _mode_with_predicates("cold", ["physical_custodian", "policy_suspension"], rows=2),
            _mode_with_predicates("source_record", ["physical_custody", "policy_restriction", "publication_authority"], rows=8),
        ],
    }

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=["cold", "source_record"]),
        mode_labels=["cold", "source_record"],
        structural_choice="source_record",
    )

    assert override == (
        "source_record",
        "location-plus-publication-pause question needs custody plus publication restriction surface",
    )


def test_mou_scope_expansion_guard_prefers_agreement_addition_surface() -> None:
    row = {
        "id": "q035",
        "question": "Has any item beyond the original Notebook B been added to the Northbridge MOU scope since the MOU effective date?",
        "modes": [
            _mode_with_predicates("source_record", ["right_scope", "access_event"], rows=43),
            _mode_with_predicates("parallel", ["agreement_clause", "access_authorization", "access_event"], rows=3),
        ],
    }

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=["source_record", "parallel"]),
        mode_labels=["source_record", "parallel"],
        structural_choice="source_record",
    )

    assert override == (
        "parallel",
        "MOU-scope expansion question needs agreement-clause plus access/addition surface rather than static right-scope volume",
    )


def test_photograph_album_interval_guard_prefers_access_recall_surface() -> None:
    row = {
        "id": "q036",
        "question": "During what interval was the photograph album physically at Pellico's premises despite being on the conservation intake list at Stille?",
        "modes": [
            _mode_with_predicates("memory_ledger_combo", ["conservation_scope", "custody_recall"], rows=13),
            _mode_with_predicates("entity", ["access_log_entry", "physical_custodian", "recall_event"], rows=3),
        ],
    }

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=["memory_ledger_combo", "entity"]),
        mode_labels=["memory_ledger_combo", "entity"],
        structural_choice="memory_ledger_combo",
    )

    assert override == (
        "entity",
        "photograph-album interval question needs exact access-log custody surface rather than broad access-event volume",
    )


def test_photograph_album_interval_guard_prefers_exact_access_log_surface() -> None:
    row = {
        "id": "q036",
        "question": "During what interval was the photograph album physically at Pellico's premises despite being on the conservation intake list at Stille?",
        "modes": [
            _mode_with_predicates("parallel", ["access_event", "physical_custodian", "recall_event"], rows=5),
            _mode_with_predicates("entity", ["access_log_entry", "physical_custodian", "recall_event"], rows=3),
        ],
    }

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=["parallel", "entity"]),
        mode_labels=["parallel", "entity"],
        structural_choice="parallel",
    )

    assert override == (
        "entity",
        "photograph-album interval question needs exact access-log custody surface rather than broad access-event volume",
    )


def test_custody_release_guard_prefers_status_surface_over_scan_volume() -> None:
    row = {
        "id": "q035",
        "question": "When did the laptop EX-D-04 leave evidence custody, and to whom?",
        "modes": [
            _mode_with_predicates("source_record_facts", ["scan_record", "current_status"], rows=13),
            _mode_with_predicates("memory_ledger_combo", ["custody_status"], rows=3),
            _mode_with_predicates("source_record", ["custody_status"], rows=1),
        ],
    }

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=["source_record_facts", "memory_ledger_combo", "source_record"]),
        mode_labels=["source_record_facts", "memory_ledger_combo", "source_record"],
        structural_choice="source_record_facts",
    )

    assert override == (
        "source_record",
        "custody-release question needs custody/status surface rather than scan-record volume",
    )


def test_expected_order_guard_prefers_expected_order_surface() -> None:
    row = {
        "id": "q039",
        "question": "When is Judge Anwar's order on EX-C-01 expected?",
        "modes": [
            _mode_with_predicates("source_record", ["has_open_exception"], rows=5),
            _mode_with_predicates("parallel", ["expected_order_date"], rows=1),
        ],
    }

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=["source_record", "parallel"]),
        mode_labels=["source_record", "parallel"],
        structural_choice="source_record",
    )

    assert override == (
        "parallel",
        "expected-order question needs explicit expected-order surface rather than open-exception volume",
    )


def test_phone_ping_granularity_guard_prefers_device_ping_surface() -> None:
    row = {
        "id": "q028",
        "question": "What carrier sectors do Aldridge's phone pings cover, and at what approximate granularity?",
        "modes": [
            _mode_with_predicates("cold", ["evidence_source", "location_ping_at"], rows=5),
            _mode_with_predicates("entity", ["device_ping", "location_granularity"], rows=1, relaxed=True),
        ],
    }

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=["cold", "entity"]),
        mode_labels=["cold", "entity"],
        structural_choice="cold",
    )

    assert override == (
        "entity",
        "phone-ping granularity question needs device-ping granularity surface rather than evidence-source summary",
    )


def test_evidence_source_count_guard_prefers_source_catalog_surface() -> None:
    row = {
        "id": "q031",
        "question": "How many distinct evidence sources are cataloged in §2?",
        "modes": [
            _mode_with_predicates("source_record_facts", ["activity_unresolved"], rows=13),
            _mode_with_predicates("entity", ["source_id"], rows=12),
        ],
    }

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=["source_record_facts", "entity"]),
        mode_labels=["source_record_facts", "entity"],
        structural_choice="source_record_facts",
    )

    assert override == (
        "entity",
        "evidence-source count question needs source-id catalog surface rather than generic evidence-source rows",
    )


def test_evidence_source_count_guard_prefers_source_id_over_generic_source_rows() -> None:
    row = {
        "id": "q031",
        "question": "How many distinct evidence sources are cataloged in §2?",
        "modes": [
            _mode_with_predicates("cold", ["evidence_source"], rows=14),
            _mode_with_predicates("entity", ["source_id"], rows=12),
        ],
    }

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=["cold", "entity"]),
        mode_labels=["cold", "entity"],
        structural_choice="cold",
    )

    assert override == (
        "entity",
        "evidence-source count question needs source-id catalog surface rather than generic evidence-source rows",
    )


def test_memo_establish_guard_prefers_memo_reliability_scope_surface() -> None:
    row = {
        "id": "q024",
        "question": "What does Dr. Hsiao's memo establish about the autoclave's state?",
        "modes": [
            _mode_with_predicates("cold", ["evidence_source", "source_reliability_for"], rows=5),
            _mode_with_predicates("entity", ["memo_content", "source_reliability_not_for"], rows=3),
        ],
    }

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=["cold", "entity"]),
        mode_labels=["cold", "entity"],
        structural_choice="cold",
    )

    assert override == (
        "entity",
        "memo-establish question needs memo-content plus reliability-scope surface rather than broad investigative context",
    )


def test_negative_reliability_guard_prefers_reliability_scope() -> None:
    row = {
        "id": "q022",
        "question": "What does Okafor's testimony NOT reliably establish?",
        "modes": [
            _mode_with_predicates("source_record_facts", ["activity_unresolved"], rows=3),
            _mode_with_predicates("source_record", ["source_reliability_not_for"], rows=1),
        ],
    }

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=["source_record_facts", "source_record"]),
        mode_labels=["source_record_facts", "source_record"],
        structural_choice="source_record_facts",
    )

    assert override == (
        "source_record",
        "negative-reliability question needs source-reliability scope rather than unresolved-activity status alone",
    )


def test_communications_officer_guard_prefers_notice_role_surface() -> None:
    row = {
        "id": "q009",
        "question": "Who is named as the Communications Officer who drafted BWN-2026-04-28-A, RUN-2026-04-28-B, and LFT-2026-05-04?",
        "modes": [
            _mode_with_predicates("source_record", ["notice_id", "person_name", "person_role"], rows=4),
            _mode_with_predicates("memory_ledger_combo", ["notice_issued", "person_role"], rows=16),
        ],
    }

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=["source_record", "memory_ledger_combo"]),
        mode_labels=["source_record", "memory_ledger_combo"],
        structural_choice="memory_ledger_combo",
    )

    assert override == (
        "memory_ledger_combo",
        "communications-officer drafting question needs notice-issued plus person-role surface rather than name lookup alone",
    )


def test_sampler_offline_interval_guard_prefers_explicit_interval_surface() -> None:
    row = {
        "id": "q022",
        "question": "How many distinct sampler-offline intervals occurred at Station S-3 during the event?",
        "modes": [
            _mode_with_predicates("source_record", ["state_start", "state_end"], rows=8, relaxed=True),
            _mode_with_predicates("parallel", ["sampler_offline_interval"], rows=1, relaxed=True),
        ],
    }

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=["source_record", "parallel"]),
        mode_labels=["source_record", "parallel"],
        structural_choice="source_record",
    )

    assert override == (
        "parallel",
        "sampler-offline interval count needs explicit interval surface rather than state-start/end fragments",
    )


def test_chronological_event_row_count_guard_prefers_event_id_surface() -> None:
    row = {
        "id": "q025",
        "question": "How many event rows are listed in the chronological event log in §2?",
        "modes": [
            _mode_with_predicates("source_record_facts", [], rows=0),
            _mode_with_predicates("cold", ["event_id"], rows=13),
        ],
    }

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=["source_record_facts", "cold"]),
        mode_labels=["source_record_facts", "cold"],
        structural_choice="source_record_facts",
    )

    assert override == (
        "cold",
        "chronological-event-row count needs event-id enumeration rather than source-record-facts gap",
    )


def test_packet_close_open_item_count_guard_prefers_open_item_surface() -> None:
    row = {
        "id": "q026",
        "question": "How many open items are listed at packet close in §7?",
        "modes": [
            _mode_with_predicates("parallel", ["deadline_rule", "notice_id"], rows=3),
            _mode_with_predicates("cold", ["open_item_id", "open_item_status"], rows=3),
        ],
    }

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=["parallel", "cold"]),
        mode_labels=["parallel", "cold"],
        structural_choice="parallel",
    )

    assert override == (
        "cold",
        "packet-close open-item count needs explicit open-item surface rather than deadline/notice volume",
    )


def test_application_disposition_guard_prefers_status_surface() -> None:
    row = {
        "id": "q019",
        "question": "What is the disposition of App-2026-021?",
        "modes": [
            _mode_with_predicates("source_record_facts", [], rows=0),
            _mode_with_predicates("entity", ["determination_status", "rule_violated"], rows=2),
        ],
    }

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=["source_record_facts", "entity"]),
        mode_labels=["source_record_facts", "entity"],
        structural_choice="source_record_facts",
    )

    assert override == (
        "entity",
        "application-disposition question needs status/determination surface rather than source-record-facts gap",
    )


def test_roster_entry_count_guard_prefers_entry_preserving_surface() -> None:
    row = {
        "id": "q011",
        "question": "How many student entries appear in roster v1.0?",
        "modes": [
            _mode_with_predicates("entity", ["student_in_homeroom"], rows=8),
            _mode_with_predicates("memory_ledger_combo", ["student_in_homeroom"], rows=20),
            _mode_with_predicates("cold", ["student_in_homeroom"], rows=1, relaxed=True),
        ],
    }

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=["entity", "memory_ledger_combo", "cold"]),
        mode_labels=["entity", "memory_ledger_combo", "cold"],
        structural_choice="entity",
    )

    assert override == (
        "cold",
        "roster-entry count question needs entry-preserving roster surface rather than distinct-student membership volume",
    )


def test_authoritative_homeroom_guard_prefers_membership_surface() -> None:
    row = {
        "id": "q024",
        "question": "What is the registrar's authoritative homeroom for STU-1063?",
        "modes": [
            _mode_with_predicates("source_record_facts", ["correction_action"], rows=2),
            _mode_with_predicates("entity", ["homeroom_reassigned", "student_in_homeroom"], rows=1),
        ],
    }

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=["source_record_facts", "entity"]),
        mode_labels=["source_record_facts", "entity"],
        structural_choice="source_record_facts",
    )

    assert override == (
        "entity",
        "authoritative-homeroom question needs current roster membership surface rather than correction-action text alone",
    )


def test_authoritative_homeroom_guard_prefers_alias_table_surface() -> None:
    row = {
        "id": "q024",
        "question": "What is the registrar's authoritative homeroom for STU-1063?",
        "modes": [
            _mode_with_predicates("old_v2", ["student_in_homeroom", "homeroom_reassigned"], rows=39),
            _mode_with_predicates(
                "alias_full",
                ["homeroom_member_alias_support", "roster_table_member_alias_support"],
                rows=3,
            ),
        ],
    }

    labels = ["old_v2", "alias_full"]
    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=labels),
        mode_labels=labels,
        structural_choice="old_v2",
    )

    assert override == (
        "alias_full",
        "authoritative-homeroom question needs current member alias/table surface before correction-history rows",
    )


def test_authoritative_homeroom_guard_skips_source_record_facts_v2_volume() -> None:
    row = {
        "id": "q024",
        "question": "What is the registrar's authoritative homeroom for STU-1063?",
        "modes": [
            _mode_with_predicates("source_record_facts_v2", ["correction_action", "source_record_row"], rows=70, relaxed=True),
            _mode_with_predicates("entity", ["homeroom_reassigned", "student_in_homeroom"], rows=1),
        ],
    }

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=["source_record_facts_v2", "entity"]),
        mode_labels=["source_record_facts_v2", "entity"],
        structural_choice="source_record_facts_v2",
    )

    assert override == (
        "entity",
        "authoritative-homeroom question needs current roster membership surface rather than correction-action text alone",
    )


def test_distinct_student_registrar_count_prefers_count_support() -> None:
    row = {
        "id": "q012",
        "question": "How many distinct students are on the trip per the registrar in v1.0?",
        "modes": [
            _mode_with_predicates("alias_full", ["roster_table_member_label"], rows=39),
            _mode_with_predicates("count_full", ["roster_table_count_support"], rows=1),
        ],
    }

    labels = ["alias_full", "count_full"]
    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=labels),
        mode_labels=labels,
        structural_choice="alias_full",
    )

    assert override == (
        "count_full",
        "distinct-student registrar count needs roster-table count support rather than member-label enumeration",
    )


def test_student_identifier_guard_prefers_canonical_member_surface() -> None:
    row = {
        "id": "q008",
        "question": "What is the student identifier for Halpern?",
        "modes": [
            _mode_with_predicates("alias_full", ["roster_table_member_label"], rows=1),
            _mode_with_predicates(
                "count_full",
                ["roster_table_member_label", "roster_table_member", "roster_table_member_alias_support"],
                rows=1,
            ),
        ],
    }

    labels = ["alias_full", "count_full"]
    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=labels),
        mode_labels=labels,
        structural_choice="alias_full",
    )

    assert override == (
        "count_full",
        "student-identifier question needs label-to-canonical-member surface rather than printed-label surface alone",
    )


def test_roster_bus_assignment_correction_prefers_change_surface() -> None:
    row = {
        "id": "q028",
        "question": "Was the bus assignment of student Garner changed by any correction notice, and if so which?",
        "modes": [
            _mode_with_predicates("alias_full", ["roster_table_member", "roster_table_member_label"], rows=4),
            _mode_with_predicates("narrow_guidance", ["bus_assignee", "change_type"], rows=1),
        ],
    }

    labels = ["alias_full", "narrow_guidance"]
    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=labels),
        mode_labels=labels,
        structural_choice="alias_full",
    )

    assert override == (
        "narrow_guidance",
        "bus-assignment correction question needs bus-assignment plus change-type surface rather than roster table identity rows",
    )


def test_roster_ratio_compliance_prefers_compliance_status_surface() -> None:
    row = {
        "id": "q033",
        "question": "Under §3.2, was roster v1.0 compliant with the chaperone-to-student ratio?",
        "modes": [
            _mode_with_predicates("narrow_guidance", ["roster_table_version", "roster_table_member", "role"], rows=39),
            _mode_with_predicates("count_full", ["compliance_status"], rows=1),
        ],
    }

    labels = ["narrow_guidance", "count_full"]
    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=labels),
        mode_labels=labels,
        structural_choice="narrow_guidance",
    )

    assert override == (
        "count_full",
        "ratio-compliance question needs compliance_status surface rather than roster-table version volume",
    )


def test_roster_adult_total_prefers_role_surface_over_chaperone_count() -> None:
    row = {
        "id": "q018",
        "question": "How many adults total are accompanying the trip in v1.3?",
        "modes": [
            _mode_with_predicates("focused_homeroom", ["chaperone_added", "roster_state_support"], rows=6),
            _mode_with_predicates("narrow_guidance", ["role"], rows=5),
            _mode_with_predicates("alias_full", ["counting_chaperones"], rows=1),
        ],
    }

    labels = ["focused_homeroom", "narrow_guidance", "alias_full"]
    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=labels),
        mode_labels=labels,
        structural_choice="focused_homeroom",
    )

    assert override == (
        "narrow_guidance",
        "adult-total roster question needs adult role surface rather than qualifying-chaperone count alone",
    )


def test_correction_notice_replacement_guard_prefers_change_type_surface() -> None:
    row = {
        "id": "q026",
        "question": "Which student withdrew in Correction Notice 02, and which student replaced them?",
        "modes": [
            _mode_with_predicates("source_record_facts", ["correction_action"], rows=2),
            _mode_with_predicates("cold", ["change_type"], rows=1, relaxed=True),
        ],
    }

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=["source_record_facts", "cold"]),
        mode_labels=["source_record_facts", "cold"],
        structural_choice="source_record_facts",
    )

    assert override == (
        "cold",
        "correction-notice replacement question needs change-type surface rather than unparsed correction-action text",
    )


def test_application_count_guard_prefers_canonical_status_surface() -> None:
    row = {
        "id": "q027",
        "question": "How many applications are approved?",
        "modes": [
            _mode_with_predicates("source_record", ["determination_status"], rows=3),
            _mode_with_predicates("cold", ["application_status"], rows=2),
        ],
    }

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=["source_record", "cold"]),
        mode_labels=["source_record", "cold"],
        structural_choice="source_record",
    )

    assert override == (
        "cold",
        "application-count question needs canonical application-status surface rather than source-record duplicate rows",
    )


def test_date_alone_rule_guard_prefers_threshold_exception_surface() -> None:
    row = {
        "id": "q015",
        "question": "Does App-2026-019 satisfy §2.1 by Borden County incorporation date alone?",
        "modes": [
            _mode_with_predicates("parallel", ["applicant_attribute", "eligibility_determination"], rows=90),
            _mode_with_predicates("cold", ["threshold_met", "exception_applies", "rule_definition"], rows=3),
        ],
    }

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=["parallel", "cold"]),
        mode_labels=["parallel", "cold"],
        structural_choice="parallel",
    )

    assert override == (
        "cold",
        "date-alone rule question needs threshold plus exception surface rather than broad applicant-date volume",
    )


def test_projection_supersession_guard_prefers_trigger_surface() -> None:
    row = {
        "id": "q032",
        "question": "What event caused the projection in OPS-PROJ-04-29 to be superseded, and on what date and time did that event occur?",
        "modes": [
            _mode_with_predicates("parallel", ["projection_comparison"], rows=27),
            _mode_with_predicates("source_record", ["event_trigger_rule", "event_timestamp_corrected"], rows=2),
        ],
    }

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=["parallel", "source_record"]),
        mode_labels=["parallel", "source_record"],
        structural_choice="parallel",
    )

    assert override == (
        "source_record",
        "projection-supersession question needs trigger/actual event surface rather than projection-comparison volume",
    )


def test_trip_date_guard_prefers_roster_state_surface() -> None:
    row = {
        "id": "q002",
        "question": "On what date is the trip scheduled?",
        "modes": [
            _mode_with_predicates("source_record", ["roster_version"], rows=4),
            _mode_with_predicates("memory_ledger_combo", ["roster_state"], rows=1),
        ],
    }

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=["source_record", "memory_ledger_combo"]),
        mode_labels=["source_record", "memory_ledger_combo"],
        structural_choice="source_record",
    )

    assert override == (
        "memory_ledger_combo",
        "trip-date question needs roster-state schedule surface rather than roster-version/source-record volume",
    )


def test_rule_threshold_guard_prefers_threshold_surface() -> None:
    row = {
        "id": "q010",
        "question": "What is the outstanding tax-liability threshold under section 2.5?",
        "modes": [
            _mode_with_predicates("parallel", ["applicant_attribute", "eligibility_determination"], rows=7),
            _mode_with_predicates("source_record", ["rule_threshold"], rows=1),
        ],
    }

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=["parallel", "source_record"]),
        mode_labels=["parallel", "source_record"],
        structural_choice="parallel",
    )

    assert override == (
        "source_record",
        "threshold question needs rule-threshold surface rather than applicant-attribute volume",
    )


def test_barcode_supersession_guard_prefers_scan_correction_surface() -> None:
    row = {
        "id": "q007",
        "question": "Which barcode scan superseded the 2026-04-04 scan of the revolver, and on what date?",
        "modes": [
            _mode_with_predicates("cold", ["current_barcode"], rows=11),
            _mode_with_predicates("parallel", ["scan_record"], rows=4),
        ],
    }

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=["cold", "parallel"]),
        mode_labels=["cold", "parallel"],
        structural_choice="cold",
    )

    assert override == (
        "parallel",
        "barcode-supersession question needs scan/correction surface rather than broad current-barcode volume",
    )


def test_hybrid_selector_calls_model_for_identity_name_completeness_trap() -> None:
    row = {
        "id": "q004d",
        "question": "Who is Fair Warden Osric Thane?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "person_name",
                            "was_relaxed_fallback": False,
                        },
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "registered_as",
                            "was_relaxed_fallback": False,
                        },
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "authority_rows",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 8,
                            "predicate": "ruled_by",
                            "was_relaxed_fallback": False,
                        },
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "role_of",
                            "was_relaxed_fallback": False,
                        },
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }
    fallback_calls = 0

    def fallback_selector(**_kwargs):
        nonlocal fallback_calls
        fallback_calls += 1
        return {"selected_mode": "baseline", "selection_confidence": 0.7}

    scored = structural_mode_scores(row=row, mode_labels=["baseline", "authority_rows"])
    assert structural_identity_completeness_trap_reason(row=row, scored=scored)

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "authority_rows"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=fallback_selector,
    )

    assert fallback_calls == 1
    assert selected["selected_mode"] == "baseline"
    assert "explicit name support" in selected["structural_uncertainty_reasons"][0]


def test_hybrid_selector_calls_model_for_rationale_contrast_trap() -> None:
    row = {
        "id": "q004e",
        "question": "What is the difference between the permitted repair and the modification?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "rule_applies_to",
                            "was_relaxed_fallback": False,
                        },
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "disqualified_from",
                            "was_relaxed_fallback": False,
                        },
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "status_rows",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 8,
                            "predicate": "ruled_by",
                            "was_relaxed_fallback": False,
                        },
                        {
                            "status": "success",
                            "num_rows": 2,
                            "predicate": "results_in",
                            "was_relaxed_fallback": False,
                        },
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }
    fallback_calls = 0

    def fallback_selector(**_kwargs):
        nonlocal fallback_calls
        fallback_calls += 1
        return {"selected_mode": "baseline", "selection_confidence": 0.7}

    scored = structural_mode_scores(row=row, mode_labels=["baseline", "status_rows"])
    assert structural_rationale_contrast_trap_reason(row=row, scored=scored)

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "status_rows"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=fallback_selector,
    )

    assert fallback_calls == 1
    assert selected["selected_mode"] == "baseline"
    assert "explicit rationale support" in selected["structural_uncertainty_reasons"][0]


def test_hybrid_selector_keeps_baseline_for_broad_identity_action_override() -> None:
    row = {
        "id": "q004f",
        "question": "Who is Fair Warden Osric Thane?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "person_name",
                            "was_relaxed_fallback": False,
                        },
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "registered_as",
                            "was_relaxed_fallback": False,
                        },
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "permission_rationale",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 8,
                            "predicate": "event_actor",
                            "was_relaxed_fallback": False,
                        },
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "person_role",
                            "was_relaxed_fallback": False,
                        },
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    fallback_calls = 0

    def fallback_selector(**_kwargs):
        nonlocal fallback_calls
        fallback_calls += 1
        return {"selected_mode": "permission_rationale"}

    scored = structural_mode_scores(row=row, mode_labels=["baseline", "permission_rationale"])
    assert structural_baseline_answer_surface_guard_reason(
        row=row,
        scored=scored,
        mode_labels=["baseline", "permission_rationale"],
        structural_choice="permission_rationale",
    )

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "permission_rationale"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=fallback_selector,
    )

    assert fallback_calls == 0
    assert selected["selected_mode"] == "baseline"
    assert selected["hybrid_decision"] == "structural_baseline_answer_surface_guard"
    assert "broad action-heavy" in selected["baseline_guard_reason"]


def test_hybrid_selector_keeps_baseline_for_explicit_awarded_support() -> None:
    row = {
        "id": "q004g",
        "question": "Who won second place?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "awarded",
                            "was_relaxed_fallback": False,
                        }
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "permission_rationale",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 9,
                            "predicate": "person_name",
                            "was_relaxed_fallback": False,
                        },
                        {
                            "status": "success",
                            "num_rows": 9,
                            "predicate": "device_state",
                            "was_relaxed_fallback": True,
                        },
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    fallback_calls = 0

    def fallback_selector(**_kwargs):
        nonlocal fallback_calls
        fallback_calls += 1
        return {"selected_mode": "permission_rationale"}

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "permission_rationale"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=fallback_selector,
    )

    assert fallback_calls == 0
    assert selected["selected_mode"] == "baseline"
    assert "awarded support" in selected["baseline_guard_reason"]


def test_hybrid_selector_keeps_direct_status_rule_support() -> None:
    row = {
        "id": "q004h",
        "question": "What is the exhibition status of the Moth Lantern at closing?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 2,
                            "predicate": "disqualified_from",
                            "was_relaxed_fallback": False,
                        },
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "rule_applies_to",
                            "was_relaxed_fallback": False,
                        },
                        {
                            "status": "success",
                            "num_rows": 9,
                            "predicate": "device_state",
                            "was_relaxed_fallback": True,
                        },
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "permission_rationale",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "device_state",
                            "was_relaxed_fallback": True,
                        },
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "ruling_basis",
                            "was_relaxed_fallback": True,
                        },
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    fallback_calls = 0

    def fallback_selector(**_kwargs):
        nonlocal fallback_calls
        fallback_calls += 1
        return {"selected_mode": "permission_rationale"}

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "permission_rationale"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=fallback_selector,
    )

    assert fallback_calls == 0
    assert selected["selected_mode"] == "baseline"
    assert "status/rule support" in selected["baseline_guard_reason"]


def test_hybrid_selector_keeps_baseline_for_application_status_relaxed_candidate() -> None:
    row = {
        "id": "q004i",
        "question": "What is the status of Application E?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "application_status",
                            "was_relaxed_fallback": False,
                        }
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "operational_record",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "panel_decision",
                            "was_relaxed_fallback": False,
                        },
                        {
                            "status": "success",
                            "num_rows": 24,
                            "predicate": "decision_reasoning",
                            "was_relaxed_fallback": True,
                        },
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    fallback_calls = 0

    def fallback_selector(**_kwargs):
        nonlocal fallback_calls
        fallback_calls += 1
        return {"selected_mode": "operational_record"}

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "operational_record"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=fallback_selector,
    )

    assert fallback_calls == 0
    assert selected["selected_mode"] == "baseline"
    assert "application/status support" in selected["baseline_guard_reason"]


def test_hybrid_selector_keeps_baseline_for_counterfactual_rule_status_support() -> None:
    row = {
        "id": "q004j",
        "question": "If Lot 005 fails with a 35% germination rate, what would happen?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 2,
                            "predicate": "deaccession_threshold",
                            "was_relaxed_fallback": False,
                        },
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "species",
                            "was_relaxed_fallback": False,
                        },
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "operational_record",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 46,
                            "predicate": "policy_condition_threshold",
                            "was_relaxed_fallback": True,
                        },
                        {
                            "status": "success",
                            "num_rows": 6,
                            "predicate": "lot_status",
                            "was_relaxed_fallback": True,
                        },
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    fallback_calls = 0

    def fallback_selector(**_kwargs):
        nonlocal fallback_calls
        fallback_calls += 1
        return {"selected_mode": "operational_record"}

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "operational_record"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=fallback_selector,
    )

    assert fallback_calls == 0
    assert selected["selected_mode"] == "baseline"
    assert "counterfactual or hold/readiness question" in selected["baseline_guard_reason"]


def test_hybrid_selector_keeps_baseline_for_hold_readiness_status_support() -> None:
    row = {
        "id": "q004k",
        "question": "Should the system hold the bid date pending clarification?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 6,
                            "predicate": "event_status",
                            "was_relaxed_fallback": False,
                        },
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "pending_action",
                            "was_relaxed_fallback": False,
                        },
                        {
                            "status": "success",
                            "num_rows": 20,
                            "predicate": "event_occurred",
                            "was_relaxed_fallback": True,
                        },
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "operational_record",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 6,
                            "predicate": "event_corrects",
                            "was_relaxed_fallback": False,
                        },
                        {
                            "status": "success",
                            "num_rows": 15,
                            "predicate": "event_defers",
                            "was_relaxed_fallback": True,
                        },
                        {
                            "status": "success",
                            "num_rows": 6,
                            "predicate": "bid_amount",
                            "was_relaxed_fallback": True,
                        },
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    fallback_calls = 0

    def fallback_selector(**_kwargs):
        nonlocal fallback_calls
        fallback_calls += 1
        return {"selected_mode": "operational_record"}

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "operational_record"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=fallback_selector,
    )

    assert fallback_calls == 0
    assert selected["selected_mode"] == "baseline"
    assert "counterfactual or hold/readiness question" in selected["baseline_guard_reason"]


def test_hybrid_selector_prefers_request_surface_for_filing_timeliness() -> None:
    row = {
        "id": "q004l",
        "question": "Was the MEP inspection request filed on time after reinstatement?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 2,
                            "predicate": "inspection_completed_on",
                            "was_relaxed_fallback": False,
                        },
                        {
                            "status": "success",
                            "num_rows": 2,
                            "predicate": "business_days_between",
                            "was_relaxed_fallback": False,
                        },
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "deadline_requirement",
                            "was_relaxed_fallback": False,
                        },
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "operational_record",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 2,
                            "predicate": "permit_reinstated",
                            "was_relaxed_fallback": False,
                        },
                        {
                            "status": "success",
                            "num_rows": 2,
                            "predicate": "inspection_requested",
                            "was_relaxed_fallback": False,
                        },
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "rule_threshold_met",
                            "was_relaxed_fallback": False,
                        },
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    fallback_calls = 0

    def fallback_selector(**_kwargs):
        nonlocal fallback_calls
        fallback_calls += 1
        return {"selected_mode": "baseline"}

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "operational_record"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=fallback_selector,
    )

    assert fallback_calls == 0
    assert selected["selected_mode"] == "operational_record"
    assert "request/reinstatement threshold evidence" in selected["specialized_guard_reason"]


def test_hybrid_selector_prefers_process_surface_for_commit_readiness() -> None:
    row = {
        "id": "q004m",
        "question": "After Turn 16 but before Turn 23, should the system commit the lab exhaust fan recertification status?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "certification_status",
                            "was_relaxed_fallback": False,
                        },
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "event_occurred",
                            "was_relaxed_fallback": False,
                        },
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "operational_record",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "requires_investigation",
                            "was_relaxed_fallback": False,
                        },
                        {
                            "status": "success",
                            "num_rows": 4,
                            "predicate": "pending_action",
                            "was_relaxed_fallback": True,
                        },
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    fallback_calls = 0

    def fallback_selector(**_kwargs):
        nonlocal fallback_calls
        fallback_calls += 1
        return {"selected_mode": "baseline"}

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "operational_record"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=fallback_selector,
    )

    assert fallback_calls == 0
    assert selected["selected_mode"] == "operational_record"
    assert "unresolved process evidence" in selected["specialized_guard_reason"]


def test_hybrid_selector_keeps_rationale_note_for_cause_question() -> None:
    row = {
        "id": "q004n",
        "question": "What caused the MEP inspection delay?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "inspector_note",
                            "was_relaxed_fallback": True,
                        }
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "operational_record",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 12,
                            "predicate": "record_corrected",
                            "was_relaxed_fallback": False,
                        },
                        {
                            "status": "success",
                            "num_rows": 6,
                            "predicate": "inspection_requested",
                            "was_relaxed_fallback": False,
                        },
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    fallback_calls = 0

    def fallback_selector(**_kwargs):
        nonlocal fallback_calls
        fallback_calls += 1
        return {"selected_mode": "operational_record"}

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "operational_record"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=fallback_selector,
    )

    assert fallback_calls == 0
    assert selected["selected_mode"] == "baseline"
    assert "rationale-note support" in selected["specialized_guard_reason"]


def test_hybrid_selector_prefers_explicit_priority_surface() -> None:
    row = {
        "id": "q004o",
        "question": "Which applications have community impact priority?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 3,
                            "predicate": "has_community_impact",
                            "was_relaxed_fallback": False,
                        }
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "operational_record",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 3,
                            "predicate": "community_impact_priority",
                            "was_relaxed_fallback": False,
                        }
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    fallback_calls = 0

    def fallback_selector(**_kwargs):
        nonlocal fallback_calls
        fallback_calls += 1
        return {"selected_mode": "baseline"}

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "operational_record"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=fallback_selector,
    )

    assert fallback_calls == 0
    assert selected["selected_mode"] == "operational_record"
    assert "explicit priority predicate" in selected["specialized_guard_reason"]


def test_hybrid_selector_prefers_explicit_decision_surface() -> None:
    row = {
        "id": "q004p",
        "question": "Was the public-access question for Application D decided?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "application_status",
                            "was_relaxed_fallback": False,
                        },
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "pending_requirement",
                            "was_relaxed_fallback": True,
                        },
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "operational_record",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "panel_decision",
                            "was_relaxed_fallback": True,
                        },
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "decision_reasoning",
                            "was_relaxed_fallback": False,
                        },
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    fallback_calls = 0

    def fallback_selector(**_kwargs):
        nonlocal fallback_calls
        fallback_calls += 1
        return {"selected_mode": "baseline"}

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "operational_record"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=fallback_selector,
    )

    assert fallback_calls == 0
    assert selected["selected_mode"] == "operational_record"
    assert "explicit decision surface" in selected["specialized_guard_reason"]


def test_hybrid_selector_prefers_actual_split_surface_for_split_rationale() -> None:
    row = {
        "id": "q004q",
        "question": "Why was FB-2026-006 split to Vault 4?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "requires_cryogenic",
                            "was_relaxed_fallback": False,
                        },
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "vault_assignment_rule",
                            "was_relaxed_fallback": False,
                        },
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "operational_record",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "lot_vault_split",
                            "was_relaxed_fallback": False,
                        },
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "lot_germination_rate",
                            "was_relaxed_fallback": True,
                        },
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "lot_condition_after_test",
                            "was_relaxed_fallback": False,
                        },
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    fallback_calls = 0

    def fallback_selector(**_kwargs):
        nonlocal fallback_calls
        fallback_calls += 1
        return {"selected_mode": "baseline"}

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "operational_record"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=fallback_selector,
    )

    assert fallback_calls == 0
    assert selected["selected_mode"] == "operational_record"
    assert "actual split/lot-condition surface" in selected["specialized_guard_reason"]


def test_hybrid_selector_prefers_source_note_for_split_rationale_when_available() -> None:
    row = {
        "id": "q004t",
        "question": "Why was FB-2026-006 split to Vault 4?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 1, "predicate": "vault_assignment_rule"},
                        {"status": "success", "num_rows": 1, "predicate": "vault_type"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "operational_record",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 1, "predicate": "lot_vault_split"},
                        {"status": "success", "num_rows": 1, "predicate": "lot_germination_rate"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "rationale_contrast",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 1, "predicate": "note_content"},
                        {"status": "success", "num_rows": 1, "predicate": "note_subject"},
                        {"status": "success", "num_rows": 1, "predicate": "test_germination_rate"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "operational_record", "rationale_contrast"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "baseline"},
    )

    assert selected["selected_mode"] == "rationale_contrast"
    assert "source-note rationale plus viability context" in selected["specialized_guard_reason"]


def test_hybrid_selector_prefers_direct_collector_surface_for_collector_identity() -> None:
    row = {
        "id": "q004x",
        "question": "Who collected FB-2026-003?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 1, "predicate": "collector"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "rationale_contrast",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 8, "predicate": "stored_in_vault"},
                        {"status": "success", "num_rows": 5, "predicate": "test_status"},
                        {"status": "success", "num_rows": 2, "predicate": "note_content"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "rationale_contrast"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "rationale_contrast"},
    )

    assert selected["selected_mode"] == "baseline"
    assert "direct collector predicate surface" in selected["specialized_guard_reason"]


def test_hybrid_selector_prefers_source_note_for_viability_concern_contrast() -> None:
    row = {
        "id": "q004u",
        "question": "Is the Vault 4 split a viability concern?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 8, "predicate": "stored_in_vault"},
                        {"status": "success", "num_rows": 4, "predicate": "vault_type"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "rationale_contrast",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 1, "predicate": "note_content"},
                        {"status": "success", "num_rows": 1, "predicate": "note_subject"},
                        {"status": "success", "num_rows": 1, "predicate": "test_resulting_condition"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "rationale_contrast"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "baseline"},
    )

    assert selected["selected_mode"] == "rationale_contrast"
    assert "source-note contrast plus viability context" in selected["specialized_guard_reason"]


def test_hybrid_selector_prefers_pending_status_for_not_yet_tested_question() -> None:
    row = {
        "id": "q004v",
        "question": "Which accessions have not yet been viability tested?",
        "modes": [
            {
                "mode": "operational_record",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 8, "predicate": "lot_id"},
                        {"status": "success", "num_rows": 3, "predicate": "\\+"},
                        {"status": "success", "num_rows": 1, "predicate": "lot_deaccessioned"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "rationale_contrast",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 2, "predicate": "test_status"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["operational_record", "rationale_contrast"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "operational_record"},
    )

    assert selected["selected_mode"] == "rationale_contrast"
    assert "pending test-status surface" in selected["specialized_guard_reason"]


def test_hybrid_selector_prefers_compact_deaccession_status_for_yet_question() -> None:
    row = {
        "id": "q004v2",
        "question": "Has the bur oak lot been deaccessioned yet?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 8, "predicate": "lot_id"},
                        {"status": "success", "num_rows": 4, "predicate": "lot_condition_update"},
                        {"status": "success", "num_rows": 3, "predicate": "lot_deaccessioned"},
                        {
                            "status": "success",
                            "num_rows": 11,
                            "predicate": "lot_viability_test_result",
                            "was_relaxed_fallback": True,
                        },
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "object_state_custody",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "lot_deaccessioned",
                            "was_relaxed_fallback": False,
                        },
                        {
                            "status": "success",
                            "num_rows": 9,
                            "predicate": "lot_id",
                            "was_relaxed_fallback": False,
                        },
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "object_state_custody"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "baseline"},
    )

    assert selected["selected_mode"] == "object_state_custody"
    assert "scheduled/not-formally-completed status surface" in selected["specialized_guard_reason"]


def test_hybrid_selector_prefers_final_state_for_current_operational_status() -> None:
    row = {
        "id": "q004z",
        "question": "What is the current operational status of Segment 4?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 3, "predicate": "investigation_status"},
                        {"status": "success", "num_rows": 1, "predicate": "finding_not_made"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "operational_record",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 1, "predicate": "has_state"},
                        {"status": "success", "num_rows": 1, "predicate": "is_final_state"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "rationale_contrast",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 4, "predicate": "event_occurred"},
                        {"status": "success", "num_rows": 2, "predicate": "administrative_action"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "operational_record", "rationale_contrast"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "rationale_contrast"},
    )

    assert selected["selected_mode"] == "operational_record"
    assert "explicit final-state surface" in selected["specialized_guard_reason"]


def test_hybrid_selector_prefers_current_expiration_for_adjusted_reinstatement_expiration() -> None:
    row = {
        "id": "q004z2",
        "question": "What is the adjusted permit expiration after reinstatement?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 1, "predicate": "permit_expires_on"},
                        {"status": "success", "num_rows": 1, "predicate": "permit_status_at"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "operational_record",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 1, "predicate": "permit_expiration"},
                        {
                            "status": "success",
                            "num_rows": 5,
                            "predicate": "permit_expiration",
                            "was_relaxed_fallback": True,
                        },
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "temporal_status",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 2,
                            "predicate": "permit_current_expiration",
                            "was_relaxed_fallback": False,
                        }
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "operational_record", "temporal_status"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "operational_record"},
    )

    assert selected["selected_mode"] == "temporal_status"
    assert "explicit current-expiration surface" in selected["specialized_guard_reason"]


def test_hybrid_selector_prefers_entitlement_effect_for_correction_entitlement_question() -> None:
    row = {
        "id": "q004z3",
        "question": "Does Correction 3 change the section 5.5 extension entitlement?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 1, "predicate": "deadline_requirement"},
                        {"status": "success", "num_rows": 1, "predicate": "extension_approved_on"},
                        {"status": "success", "num_rows": 1, "predicate": "extension_duration_days"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "temporal_status",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 1, "predicate": "corrected_value"},
                        {"status": "success", "num_rows": 1, "predicate": "inspector_admission"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "temporal_status"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "temporal_status"},
    )

    assert selected["selected_mode"] == "baseline"
    assert "entitlement rule plus extension effect surface" in selected["specialized_guard_reason"]


def test_hybrid_selector_prefers_witness_report_surface_for_evidentiary_status() -> None:
    row = {
        "id": "q005a",
        "question": "What is the evidentiary status of the unnamed source report about the contractor vehicle?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 1, "predicate": "claim_epistemic_status"},
                        {"status": "success", "num_rows": 1, "predicate": "claim_source_type"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "rationale_contrast",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 1, "predicate": "witness_statement"},
                        {"status": "success", "num_rows": 1, "predicate": "allegation_tip"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "rationale_contrast"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "baseline"},
    )

    assert selected["selected_mode"] == "rationale_contrast"
    assert "explicit witness/report surface" in selected["specialized_guard_reason"]


def test_hybrid_selector_prefers_event_action_history_for_board_concern_decision() -> None:
    row = {
        "id": "q005b",
        "question": "What did the board decide about the ventilation concern in Turn 06?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 1, "predicate": "event_status"},
                        {"status": "success", "num_rows": 1, "predicate": "pending_action"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "operational_record",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 1, "predicate": "event_defers"},
                        {"status": "success", "num_rows": 1, "predicate": "pending_action"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "rationale_contrast",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 1, "predicate": "event_occurred"},
                        {"status": "success", "num_rows": 1, "predicate": "action_taken"},
                        {"status": "success", "num_rows": 1, "predicate": "concern_raised"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "operational_record", "rationale_contrast"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "operational_record"},
    )

    assert selected["selected_mode"] == "rationale_contrast"
    assert "event/action concern history" in selected["specialized_guard_reason"]


def test_hybrid_selector_commit_readiness_not_blocked_by_status_baseline_guard() -> None:
    row = {
        "id": "q005c",
        "question": "After Turn 16 but before Turn 23, should the system commit the lab exhaust fan recertification status?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 1, "predicate": "certification_status"},
                        {"status": "success", "num_rows": 1, "predicate": "event_occurred"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "operational_record",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 6, "predicate": "requires_investigation"},
                        {"status": "success", "num_rows": 7, "predicate": "pending_action"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "operational_record"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "baseline"},
    )

    assert selected["selected_mode"] == "operational_record"
    assert selected.get("baseline_guard_reason", "") == ""
    assert "unresolved process evidence" in selected["specialized_guard_reason"]


def test_hybrid_selector_keeps_public_event_extension_purpose_surface() -> None:
    row = {
        "id": "q_public_extension",
        "question": "Can public events be held on October 20?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 3, "predicate": "extension_granted"},
                        {"status": "success", "num_rows": 3, "predicate": "status_at"},
                        {"status": "success", "num_rows": 2, "predicate": "valid_to"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "candidate",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 18, "predicate": "permit_extension"},
                        {"status": "success", "num_rows": 18, "predicate": "permit_validity"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "candidate"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "candidate"},
    )

    assert selected["selected_mode"] == "baseline"
    assert "public-use extension" in selected["specialized_guard_reason"]


def test_hybrid_selector_prefers_unrenewed_expiry_endpoint_surface() -> None:
    row = {
        "id": "q_unrenewed_expiry",
        "question": "When does the Temporary Food Service License expire if not renewed?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 2, "predicate": "permit_name"},
                        {"status": "success", "num_rows": 2, "predicate": "valid_to"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "candidate",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 11, "predicate": "permit_type"},
                        {"status": "success", "num_rows": 11, "predicate": "permit_validity"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "candidate"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "candidate"},
    )

    assert selected["selected_mode"] == "baseline"
    assert "unrenewed-expiry" in selected["specialized_guard_reason"]


def test_hybrid_selector_prefers_violation_record_for_suspension_trigger() -> None:
    row = {
        "id": "q_suspension_trigger",
        "question": "What triggered the first sound permit suspension?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 12, "predicate": "suspension_period"},
                        {"status": "success", "num_rows": 12, "predicate": "violation_occurred"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "candidate",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 2, "predicate": "permit_suspension"},
                        {"status": "success", "num_rows": 2, "predicate": "violation_record"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "candidate"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "baseline"},
    )

    assert selected["selected_mode"] == "candidate"
    assert "violation-record" in selected["specialized_guard_reason"]


def test_hybrid_selector_prefers_quarantine_scope_for_split_lot_count() -> None:
    row = {
        "id": "q_split_lot_count",
        "question": "How many Lot 5C plants were never quarantined?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 7, "predicate": "lot_status"},
                        {"status": "success", "num_rows": 7, "predicate": "mistaken_inclusion"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "candidate",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 3, "predicate": "lot"},
                        {"status": "success", "num_rows": 3, "predicate": "lot_status"},
                        {"status": "success", "num_rows": 3, "predicate": "quarantine_scope"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "candidate"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "baseline"},
    )

    assert selected["selected_mode"] == "candidate"
    assert "split-lot never-quarantined" in selected["specialized_guard_reason"]


def test_hybrid_selector_prefers_destruction_supervisor_role_surface() -> None:
    row = {
        "id": "q_destruction_supervisor",
        "question": "Who supervised the destruction of Lot 3A and Lot 5A?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 8, "predicate": "destruction_completed"},
                        {"status": "success", "num_rows": 8, "predicate": "destruction_order"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "candidate",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 2, "predicate": "destruction_completed"},
                        {"status": "success", "num_rows": 2, "predicate": "person_role"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "candidate"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "baseline"},
    )

    assert selected["selected_mode"] == "candidate"
    assert "destruction-supervisor" in selected["specialized_guard_reason"]


def test_hybrid_selector_prefers_provisional_control_with_pending_context() -> None:
    row = {
        "id": "q_provisional_control",
        "question": "Who holds provisional control of the orchard?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 1, "predicate": "provisional_control"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "candidate",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 1, "predicate": "provisional_control"},
                        {"status": "success", "num_rows": 2, "predicate": "estate_asset_included"},
                        {"status": "success", "num_rows": 2, "predicate": "will_provision"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "candidate"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "baseline"},
    )

    assert selected["selected_mode"] == "candidate"
    assert "provisional-control" in selected["specialized_guard_reason"]


def test_hybrid_selector_prefers_court_inheritance_surface_for_post_death_legal_owner() -> None:
    row = {
        "id": "q_legal_owner",
        "question": "Who legally owns the King Pear?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 2, "predicate": "court_ruling"},
                        {"status": "success", "num_rows": 4, "predicate": "will_transfer"},
                        {"status": "success", "num_rows": 6, "predicate": "part_of"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "candidate",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 1, "predicate": "legal_owner"},
                        {"status": "success", "num_rows": 2, "predicate": "estate_asset_included"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "candidate"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "candidate"},
    )

    assert selected["selected_mode"] == "baseline"
    assert "post-death legal-ownership" in selected["specialized_guard_reason"]


def test_hybrid_selector_prefers_physical_possessor_for_current_maintenance() -> None:
    row = {
        "id": "q_current_possession",
        "question": "Who currently possesses the Greengage (maintains it)?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 3, "predicate": "gift_claim"},
                        {"status": "success", "num_rows": 3, "predicate": "court_ruling"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "candidate",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 1, "predicate": "physical_possessor"},
                        {"status": "success", "num_rows": 1, "predicate": "gift_intent_declared"},
                        {"status": "success", "num_rows": 1, "predicate": "disputed_claim"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "candidate"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "baseline"},
    )

    assert selected["selected_mode"] == "candidate"
    assert "current possession/maintenance" in selected["specialized_guard_reason"]


def test_hybrid_selector_keeps_solicitor_advice_with_adverse_possession_caveat() -> None:
    row = {
        "id": "q_solicitor_advice",
        "question": "What was Rhodri's solicitor's advice about Pye's harvest rights?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 1, "predicate": "solicitor_advice"},
                        {"status": "success", "num_rows": 1, "predicate": "adverse_possession_risk"},
                        {"status": "success", "num_rows": 1, "predicate": "potential_claim"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "candidate",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 2, "predicate": "legal_advice"},
                        {"status": "success", "num_rows": 2, "predicate": "harvest_right_holder"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "candidate"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "candidate"},
    )

    assert selected["selected_mode"] == "baseline"
    assert "solicitor-advice" in selected["specialized_guard_reason"]


def test_hybrid_selector_keeps_recovery_identity_on_testimony_surface() -> None:
    row = {
        "id": "q_recovery_identity",
        "question": "Who recovered the bell?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 1, "predicate": "testimony_by"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "candidate",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 3, "predicate": "physical_custody"},
                        {"status": "success", "num_rows": 3, "predicate": "within_zone"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "candidate"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "candidate"},
    )

    assert selected["selected_mode"] == "baseline"
    assert "recovery-identity" in selected["specialized_guard_reason"]


def test_hybrid_selector_keeps_source_belief_on_testimony_surface() -> None:
    row = {
        "id": "q_source_belief",
        "question": "What vessel does Strand believe the bell is from?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 2, "predicate": "testimony_by"},
                        {"status": "success", "num_rows": 2, "predicate": "claim_asserted_by"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "candidate",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 6, "predicate": "identification_status"},
                        {"status": "success", "num_rows": 6, "predicate": "candidate_origin"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "candidate"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "candidate"},
    )

    assert selected["selected_mode"] == "baseline"
    assert "source-belief" in selected["specialized_guard_reason"]


def test_hybrid_selector_prefers_candidate_vessel_list_surface() -> None:
    row = {
        "id": "q_candidate_vessels",
        "question": "Name the three vessels.",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 5, "predicate": "inscription_fragment"},
                        {"status": "success", "num_rows": 5, "predicate": "testimony_by"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "candidate",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 3, "predicate": "candidate_origin"},
                        {"status": "success", "num_rows": 3, "predicate": "vessel_loss_date"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "candidate"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "baseline"},
    )

    assert selected["selected_mode"] == "candidate"
    assert "candidate-vessel list" in selected["specialized_guard_reason"]


def test_hybrid_selector_prefers_direct_insurance_link_surface() -> None:
    row = {
        "id": "q_insured_by",
        "question": "Which of the three was insured by Meridian?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 1, "predicate": "insured_by"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "candidate",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 4, "predicate": "ownership_contingent_on"},
                        {"status": "success", "num_rows": 4, "predicate": "candidate_origin"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "candidate"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "candidate"},
    )

    assert selected["selected_mode"] == "baseline"
    assert "insurance-link" in selected["specialized_guard_reason"]


def test_hybrid_selector_prefers_banner_change_creation_surface() -> None:
    row = {
        "id": "q_banner_change",
        "question": "Why did Kester Mace change from Owl to Raven?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 6, "predicate": "filed_protest"},
                        {"status": "success", "num_rows": 6, "predicate": "score_correction"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "candidate",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 2, "predicate": "banner_created"},
                        {"status": "success", "num_rows": 2, "predicate": "banner_holder"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "candidate"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "baseline"},
    )

    assert selected["selected_mode"] == "candidate"
    assert "banner-change rationale" in selected["specialized_guard_reason"]


def test_hybrid_selector_prefers_final_attendance_for_student_count() -> None:
    row = {
        "id": "q_student_count",
        "question": "How many students were on the return coach?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 20, "predicate": "group_membership"},
                        {"status": "success", "num_rows": 3, "predicate": "attendance_status"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "candidate",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 1, "predicate": "attendance_final"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "candidate"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "baseline"},
    )

    assert selected["selected_mode"] == "candidate"
    assert "student-count" in selected["specialized_guard_reason"]


def test_hybrid_selector_prefers_group_formation_for_temporary_team_roster() -> None:
    row = {
        "id": "q_shore_team",
        "question": "Which students formed Shore Team on Day 3?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 30, "predicate": "group_membership"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "candidate",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 2, "predicate": "group_formation"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "candidate"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "baseline"},
    )

    assert selected["selected_mode"] == "candidate"
    assert "temporary-team roster" in selected["specialized_guard_reason"]


def test_hybrid_selector_prefers_hazard_observation_for_no_touch_question() -> None:
    row = {
        "id": "q_no_touch",
        "question": "Did any students touch the sealed container?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 30, "predicate": "group_membership"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "candidate",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 1, "predicate": "hazard_status"},
                        {"status": "success", "num_rows": 1, "predicate": "incident_occurred"},
                        {"status": "success", "num_rows": 1, "predicate": "chaperone_observation"},
                        {"status": "success", "num_rows": 1, "predicate": "witness_report"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "candidate"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "baseline"},
    )

    assert selected["selected_mode"] == "candidate"
    assert "no-touch hazard" in selected["specialized_guard_reason"]


def test_hybrid_selector_keeps_alias_plus_group_for_same_name_distinction() -> None:
    row = {
        "id": "q_alias_difference",
        "question": "What is the difference between Arden and Arden B.?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 2, "predicate": "person_alias_of"},
                        {"status": "success", "num_rows": 2, "predicate": "group_membership"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "candidate",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 2, "predicate": "identity_alias"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "candidate"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "candidate"},
    )

    assert selected["selected_mode"] == "baseline"
    assert "same-name distinction" in selected["specialized_guard_reason"]


def test_hybrid_selector_prefers_interval_membership_for_group_designation_suspension() -> None:
    row = {
        "id": "q008",
        "question": "Were group designations maintained during the Day 1 afternoon beach survey?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 35, "predicate": "event_occurs"},
                        {"status": "success", "num_rows": 45, "predicate": "group_membership", "was_relaxed_fallback": True},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "interval",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 1, "predicate": "event_occurs"},
                        {"status": "success", "num_rows": 38, "predicate": "group_membership", "was_relaxed_fallback": True},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "interval"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "baseline"},
    )

    assert selected["selected_mode"] == "interval"
    assert "group-designation" in selected["specialized_guard_reason"]


def test_hybrid_selector_keeps_baseline_for_yellow_to_blue_reassignment_list() -> None:
    row = {
        "id": "q013",
        "question": "Which Yellow Group students joined Blue Group on Day 2?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 10, "predicate": "event_occurs"},
                        {"status": "success", "num_rows": 16, "predicate": "group_membership"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "interval",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 20, "predicate": "group_membership"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "interval"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "interval"},
    )

    assert selected["selected_mode"] == "baseline"
    assert "yellow-to-blue" in selected["specialized_guard_reason"]


def test_hybrid_selector_prefers_found_object_event_surface_for_day_three_beach_find() -> None:
    row = {
        "id": "q034",
        "question": "What was found on the beach on Day 3?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 35, "predicate": "event_occurs"},
                        {"status": "success", "num_rows": 20, "predicate": "group_membership"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "interval",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 6, "predicate": "event_occurs"},
                        {"status": "success", "num_rows": 2, "predicate": "incident_claim"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "interval"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "baseline"},
    )

    assert selected["selected_mode"] == "interval"
    assert "day-3 found-object" in selected["specialized_guard_reason"]


def test_hybrid_selector_prefers_recorded_value_for_conservator_date_detail() -> None:
    row = {
        "id": "q_conservator_date",
        "question": "What does the conservator's report say about the chart's actual date?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 3, "predicate": "discrepancy_type"},
                        {"status": "success", "num_rows": 3, "predicate": "correct_value"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "candidate",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 2, "predicate": "recorded_value"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "candidate"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "baseline"},
    )

    assert selected["selected_mode"] == "candidate"
    assert "conservator-date" in selected["specialized_guard_reason"]


def test_hybrid_selector_keeps_governance_surface_for_display_authority() -> None:
    row = {
        "id": "q_display_authority",
        "question": "Who has the authority to decide what the Room 9 placard says?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 1, "predicate": "governance_decision"},
                        {"status": "success", "num_rows": 1, "predicate": "source_authority"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "candidate",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 4, "predicate": "display_text"},
                        {"status": "success", "num_rows": 4, "predicate": "board_decision"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "candidate"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "candidate"},
    )

    assert selected["selected_mode"] == "baseline"
    assert "display-authority" in selected["specialized_guard_reason"]


def test_hybrid_selector_keeps_handoff_surface_for_intake_actor() -> None:
    row = {
        "id": "q_intake_actor",
        "question": "Who brought in the Hartley marine chronometer?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 2, "predicate": "ledger_entry"},
                        {"status": "success", "num_rows": 1, "predicate": "item_location"},
                        {"status": "success", "num_rows": 1, "predicate": "story_event"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "candidate",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 4, "predicate": "ledger_entry"},
                        {"status": "success", "num_rows": 4, "predicate": "entry_has_hand"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "candidate"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "candidate"},
    )

    assert selected["selected_mode"] == "baseline"
    assert "intake-actor" in selected["specialized_guard_reason"]


def test_hybrid_selector_keeps_financial_value_surface_for_missing_book_claim() -> None:
    row = {
        "id": "q012",
        "question": "What is the insured value of the missing book?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 3, "predicate": "financial_value"},
                        {"status": "success", "num_rows": 3, "predicate": "incident_outcome"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "candidate",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 7, "predicate": "claim_status"},
                        {"status": "success", "num_rows": 4, "predicate": "incident_description"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "candidate"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "candidate"},
    )

    assert selected["selected_mode"] == "baseline"
    assert "claim-value" in selected["specialized_guard_reason"]


def test_hybrid_selector_keeps_inventory_count_surface_over_title_names() -> None:
    row = {
        "id": "q014",
        "question": "How many titles were found in the physical count?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 4, "predicate": "incident_outcome"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "candidate",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 9, "predicate": "novel_title"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "candidate"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "candidate"},
    )

    assert selected["selected_mode"] == "baseline"
    assert "physical inventory count" in selected["specialized_guard_reason"]


def test_hybrid_selector_keeps_discrepancy_explanation_surface_over_fiction_events() -> None:
    row = {
        "id": "q017",
        "question": "What explanation does Odell offer for the discrepancy?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 3, "predicate": "factual_discrepancy"},
                        {"status": "success", "num_rows": 3, "predicate": "incident_outcome"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "candidate",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 8, "predicate": "fictional_event_description"},
                        {"status": "success", "num_rows": 7, "predicate": "incident_description"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "candidate"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "candidate"},
    )

    assert selected["selected_mode"] == "baseline"
    assert "discrepancy-explanation" in selected["specialized_guard_reason"]


def test_hybrid_selector_prefers_surveyor_certification_for_lapse_year() -> None:
    row = {
        "id": "q005",
        "question": "What year did James Hargreaves's surveyor certification lapse?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 2, "predicate": "person_role"},
                        {"status": "success", "num_rows": 2, "predicate": "survey_result"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "candidate",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 2, "predicate": "surveyor_certification"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "candidate"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "baseline"},
    )

    assert selected["selected_mode"] == "candidate"
    assert "surveyor-certification" in selected["specialized_guard_reason"]


def test_hybrid_selector_keeps_receipt_surface_for_maintenance_evidence() -> None:
    row = {
        "id": "q010",
        "question": "What evidence did Nora present to support the Gowan family's maintenance of the well?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 2, "predicate": "evidence_source"},
                        {"status": "success", "num_rows": 1, "predicate": "evidence_status"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "candidate",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 5, "predicate": "witness_statement"},
                        {"status": "success", "num_rows": 4, "predicate": "hearsay_basis"},
                        {"status": "success", "num_rows": 3, "predicate": "finding_record"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "candidate"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "candidate"},
    )

    assert selected["selected_mode"] == "baseline"
    assert "maintenance-evidence" in selected["specialized_guard_reason"]


def test_hybrid_selector_keeps_plot_outcome_for_fictional_coin_order() -> None:
    row = {
        "id": "q035",
        "question": "Who ordered Farmer Wynn to pay twelve silver coins?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 3, "predicate": "plot_outcome"},
                        {"status": "success", "num_rows": 2, "predicate": "fictional_character"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "candidate",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 8, "predicate": "plot_event"},
                        {"status": "success", "num_rows": 2, "predicate": "fictional_character"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "candidate"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "candidate"},
    )

    assert selected["selected_mode"] == "baseline"
    assert "fictional-order" in selected["specialized_guard_reason"]


def test_hybrid_selector_keeps_marker_shift_surface_for_boundary_discrepancy_cause() -> None:
    row = {
        "id": "q040",
        "question": "What caused the discrepancy between the Hargreaves and Voss boundary measurements?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 4, "predicate": "measurement_value"},
                        {"status": "success", "num_rows": 4, "predicate": "object_location"},
                        {"status": "success", "num_rows": 4, "predicate": "finding_basis"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "candidate",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 5, "predicate": "survey_result"},
                        {"status": "success", "num_rows": 4, "predicate": "spatial_relation_to_boundary"},
                        {"status": "success", "num_rows": 4, "predicate": "finding_record"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "candidate"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "candidate"},
    )

    assert selected["selected_mode"] == "baseline"
    assert "boundary-discrepancy" in selected["specialized_guard_reason"]


def test_hybrid_selector_prefers_policy_threshold_for_failed_viability_hypothetical() -> None:
    row = {
        "id": "q004w",
        "question": "If FB-2026-005 fails viability testing with a 35% germination rate, what would happen?",
        "modes": [
            {
                "mode": "rationale_contrast",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 1, "predicate": "rule_threshold"},
                        {"status": "success", "num_rows": 1, "predicate": "rule_action"},
                        {"status": "success", "num_rows": 1, "predicate": "note_content"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "operational_record",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 1, "predicate": "policy_condition_threshold"},
                        {"status": "success", "num_rows": 1, "predicate": "policy_minimum_storage"},
                        {"status": "success", "num_rows": 1, "predicate": "lot_status"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["rationale_contrast", "operational_record"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "rationale_contrast"},
    )

    assert selected["selected_mode"] == "operational_record"
    assert "threshold/action policy surface" in selected["specialized_guard_reason"]


def test_hybrid_selector_keeps_direct_threshold_storage_for_failed_viability_hypothetical() -> None:
    row = {
        "id": "q004y",
        "question": "If FB-2026-005 fails viability testing with a 35% germination rate, what would happen?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 1, "predicate": "deaccession_threshold"},
                        {"status": "success", "num_rows": 1, "predicate": "minimum_storage_requirement"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "operational_record",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 1, "predicate": "policy_condition_threshold"},
                        {"status": "success", "num_rows": 1, "predicate": "policy_minimum_storage"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "operational_record"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "operational_record"},
    )

    assert selected["selected_mode"] == "baseline"
    assert "direct baseline threshold/storage support" in selected["specialized_guard_reason"]


def test_hybrid_selector_prefers_applicant_type_for_current_constitution() -> None:
    row = {
        "id": "q004r",
        "question": "Can the Heronvale Poetry Circle apply as currently constituted?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "applicant",
                            "was_relaxed_fallback": False,
                        },
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "director_interpretation",
                            "was_relaxed_fallback": False,
                        },
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "operational_record",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "applicant_type",
                            "was_relaxed_fallback": False,
                        },
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "director_interpretation",
                            "was_relaxed_fallback": False,
                        },
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    fallback_calls = 0

    def fallback_selector(**_kwargs):
        nonlocal fallback_calls
        fallback_calls += 1
        return {"selected_mode": "baseline"}

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "operational_record"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=fallback_selector,
    )

    assert fallback_calls == 0
    assert selected["selected_mode"] == "operational_record"
    assert "applicant-type plus controlling interpretation" in selected["specialized_guard_reason"]


def test_hybrid_selector_keeps_rule_proof_surface_for_resubmission_resolution() -> None:
    row = {
        "id": "q004s",
        "question": "If the Poetry Circle resubmits with a named Heronvale resident as applicant, would the eligibility objection be resolved?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 2,
                            "predicate": "director_interpretation",
                            "was_relaxed_fallback": True,
                        },
                        {
                            "status": "success",
                            "num_rows": 3,
                            "predicate": "has_residency_proof",
                            "was_relaxed_fallback": True,
                        },
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "rule_condition",
                            "was_relaxed_fallback": True,
                        },
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "operational_record",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "applicant_type",
                            "was_relaxed_fallback": False,
                        },
                        {
                            "status": "success",
                            "num_rows": 4,
                            "predicate": "residency_status",
                            "was_relaxed_fallback": True,
                        },
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    fallback_calls = 0

    def fallback_selector(**_kwargs):
        nonlocal fallback_calls
        fallback_calls += 1
        return {"selected_mode": "operational_record"}

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "operational_record"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=fallback_selector,
    )

    assert fallback_calls == 0
    assert selected["selected_mode"] == "baseline"
    assert "proof/rule resolution surface" in selected["specialized_guard_reason"]


def test_hybrid_selector_prefers_exact_order_series_identifier_surface() -> None:
    row = {
        "id": "q_or_order_series",
        "question": "What is the order series number for this incident?",
        "modes": [
            _mode_with_predicates("cold", ["incident_anchor", "order_supersedes"], rows=3),
            _mode_with_predicates("source_record", ["source_section"], rows=11),
            _mode_with_predicates("archival_row_ledger_v1", ["document_identifier"], rows=3),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "source_record"},
    )

    assert selected["selected_mode"] == "archival_row_ledger_v1"
    assert "order-series identifier" in selected["specialized_guard_reason"]


def test_hybrid_selector_prefers_packet_time_measurement_surface() -> None:
    row = {
        "id": "q_or_acreage",
        "question": "What was the estimated acreage at packet time?",
        "modes": [
            _mode_with_predicates("cold", ["incident_anchor", "map_correction"], rows=5, relaxed=True),
            _mode_with_predicates("source_record", ["measurement_value"], rows=1),
            _mode_with_predicates("archival_row_ledger_v1", ["row_value"], rows=6),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "archival_row_ledger_v1"},
    )

    assert selected["selected_mode"] == "source_record"
    assert "packet-time measurement" in selected["specialized_guard_reason"]


def test_hybrid_selector_prefers_focused_semantic_surface_over_archival_volume() -> None:
    row = {
        "id": "q_or_average",
        "question": "As of packet time, what is Okafor-Vance's current corrected average score?",
        "modes": [
            _mode_with_predicates("cold", ["application_average", "score_correction"], rows=1),
            _mode_with_predicates("source_record", ["measurement_value", "source_records"], rows=1),
            _mode_with_predicates("archival_row_ledger_v1", ["row_value", "row_actor"], rows=20),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "archival_row_ledger_v1"},
    )

    assert selected["selected_mode"] == "cold"
    assert "focused semantic surface" in selected["specialized_guard_reason"]


def test_hybrid_selector_prefers_log_entry_for_timestamped_source_question() -> None:
    row = {
        "id": "q_or_log_source",
        "question": "Which source recorded the wind shift confirmation message at 03:42?",
        "modes": [
            _mode_with_predicates("cold", ["radio_log_entry"], rows=13, relaxed=True),
            _mode_with_predicates("source_record", ["source_records", "source_document_author"], rows=13),
            _mode_with_predicates("archival_row_ledger_v1", ["row_source_name", "source_section_label"], rows=5, relaxed=True),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "archival_row_ledger_v1"},
    )

    assert selected["selected_mode"] == "cold"
    assert "timestamped message-source" in selected["specialized_guard_reason"]


def test_hybrid_selector_prefers_position_source_claim_surface() -> None:
    row = {
        "id": "q_or_position_source",
        "question": "Which source recorded the wreck's Position A?",
        "modes": [
            _mode_with_predicates("cold", ["survey_position", "documented_in"], rows=17),
            _mode_with_predicates("source_record", ["statement_claim", "source_document_author"], rows=9),
            _mode_with_predicates("archival_row_ledger_v1", ["record_row", "source_section"], rows=22),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "archival_row_ledger_v1"},
    )

    assert selected["selected_mode"] == "source_record"
    assert "position-source" in selected["specialized_guard_reason"]


def test_hybrid_selector_prefers_project_pi_role_surface_over_archival_volume() -> None:
    row = {
        "id": "q_or_project_pi",
        "question": "Who is the project PI on the Lower Sammish River PFAS Monitoring Study?",
        "modes": [
            _mode_with_predicates("cold", ["person_role"], rows=1),
            _mode_with_predicates("source_record", ["assignment_interval", "source_records"], rows=2),
            _mode_with_predicates("archival_row_ledger_v1", ["document_identifier", "row_actor", "row_value"], rows=60),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "archival_row_ledger_v1"},
    )

    assert selected["selected_mode"] == "source_record"
    assert "project-PI identity" in selected["specialized_guard_reason"]


def test_hybrid_selector_prefers_panel_list_member_for_panel_chair() -> None:
    row = {
        "id": "q_or_panel_chair",
        "question": "Who is the panel chair?",
        "modes": [
            _mode_with_predicates("cold", ["person_role"], rows=1),
            _mode_with_predicates("source_record", ["list_member"], rows=1),
            _mode_with_predicates("archival_row_ledger_v1", ["row_value"], rows=5),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "cold"},
    )

    assert selected["selected_mode"] == "source_record"
    assert "panel-chair identity" in selected["specialized_guard_reason"]


def test_hybrid_selector_prefers_combined_role_participant_surface() -> None:
    row = {
        "id": "q_or_combined_role",
        "question": "Who is Penobscot Marine Salvage's president and the multibeam sonar operator?",
        "modes": [
            _mode_with_predicates("cold", ["person_role"], rows=1),
            _mode_with_predicates("source_record", ["log_event", "source_document_author", "source_records"], rows=12),
            _mode_with_predicates("archival_row_ledger_v1", ["row_actor", "row_participant"], rows=2),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "cold"},
    )

    assert selected["selected_mode"] == "source_record"
    assert "combined role-identity" in selected["specialized_guard_reason"]


def test_hybrid_selector_prefers_system_log_for_interval_behavior_and_cause() -> None:
    row = {
        "id": "q_or_interval_behavior",
        "question": "What was freezer F-3's temperature behavior between May 4 19:48 and May 5 06:32, and what was the cause?",
        "modes": [
            _mode_with_predicates("cold", ["uncertainty_status"], rows=6, relaxed=True),
            _mode_with_predicates("source_record", ["system_log_event", "event_attribute", "elapsed_minutes"], rows=40),
            _mode_with_predicates("archival_row_ledger_v1", ["row_time", "row_event", "row_value"], rows=25),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "archival_row_ledger_v1"},
    )

    assert selected["selected_mode"] == "source_record"
    assert "interval behavior-plus-cause" in selected["specialized_guard_reason"]


def test_hybrid_selector_prefers_status_at_for_review_completion() -> None:
    row = {
        "id": "q_or_review_complete",
        "question": "As of packet time, has the contamination review been completed?",
        "modes": [
            _mode_with_predicates("cold", ["uncertainty_status"], rows=6),
            _mode_with_predicates("source_record", ["status_at"], rows=2),
            _mode_with_predicates("archival_row_ledger_v1", ["row_event"], rows=25),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "cold"},
    )

    assert selected["selected_mode"] == "source_record"
    assert "review-completion" in selected["specialized_guard_reason"]


def test_hybrid_selector_prefers_archival_inventory_for_active_lot_count() -> None:
    row = {
        "id": "q_or_cap_lots",
        "question": "How many cap lots were in active use in the lab during April 25 - May 1, 2026?",
        "modes": [
            _mode_with_predicates("cold", ["analyte_result", "sample_id", "uncertainty_status"], rows=10),
            _mode_with_predicates("source_record", ["negative_record", "unresolved_issue", "status_at"], rows=13),
            _mode_with_predicates("archival_row_ledger_v1", ["row_records", "row_time", "row_value"], rows=30),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "cold"},
    )

    assert selected["selected_mode"] == "archival_row_ledger_v1"
    assert "active-lot count" in selected["specialized_guard_reason"]


def test_activation_prompt_mentions_requirement_detail_completeness() -> None:
    prompt = selector_system_prompt("activation")

    assert "requirement questions" in prompt
    assert "count-only or status-only row is often partial" in prompt
    assert "spacing, interval, threshold" in prompt
    assert "who-is identity questions" in prompt
    assert "difference/contrast" in prompt
    assert "capability-failure questions" in prompt


def test_hybrid_selector_falls_back_to_structural_when_model_fails() -> None:
    row = {
        "id": "q005",
        "modes": [
            {
                "mode": "plain",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "answer_row",
                            "was_relaxed_fallback": False,
                        }
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "evidence",
                "query_evidence": {
                    "executed_results": [],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    def fallback_selector(**_kwargs):
        raise RuntimeError("bad json")

    selected = hybrid_selector(
        row=row,
        mode_labels=["plain", "evidence"],
        margin=1.5,
        min_score=3.0,
        fallback_selector=fallback_selector,
    )

    assert selected["selected_mode"] == "plain"
    assert selected["selection_source"] == "hybrid_structural_after_llm_error"
    assert "bad json" in selected["hybrid_llm_error"]


def test_score_selection_labels_llm_source_when_selector_has_no_source() -> None:
    row = {
        "id": "q006",
        "question": "Question?",
        "modes": [
            {"mode": "plain", "verdict": "miss"},
            {"mode": "rule", "verdict": "exact"},
        ],
    }

    scored = score_selection(
        row=row,
        selection={"selected_mode": "rule", "selection_confidence": 0.8},
        error="",
    )

    assert scored["selection_source"] == "llm"
    assert scored["selected_is_best"] is True


def test_score_selection_preserves_disabled_guard_reasons() -> None:
    row = {
        "id": "q006b",
        "question": "Question?",
        "modes": [
            {"mode": "plain", "verdict": "miss"},
            {"mode": "rule", "verdict": "exact"},
        ],
    }

    scored = score_selection(
        row=row,
        selection={
            "selected_mode": "rule",
            "selection_source": "hybrid_llm",
            "disabled_guard_reasons": ["raw-timestamp guard disabled for replay"],
        },
        error="",
    )

    assert scored["disabled_guard_reasons"] == ["raw-timestamp guard disabled for replay"]


def test_merge_qa_records_overlays_later_row_metadata() -> None:
    base = {
        "rows": [
            {
                "id": "q001",
                "utterance": "Question?",
                "reference_judge": {"verdict": "miss"},
                "query_results": [{"result": {"num_rows": 0}}],
            }
        ]
    }
    failure = {
        "rows": [
            {
                "id": "q001",
                "reference_judge": {"verdict": "exact"},
                "failure_surface": {"surface": "not_applicable"},
            }
        ]
    }

    merged = merge_qa_records([base, failure])

    assert len(merged["rows"]) == 1
    assert merged["rows"][0]["utterance"] == "Question?"
    assert merged["rows"][0]["reference_judge"]["verdict"] == "exact"
    assert merged["rows"][0]["failure_surface"]["surface"] == "not_applicable"


def test_load_group_accepts_plus_merged_artifacts(tmp_path) -> None:
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    candidate = tmp_path / "candidate.json"
    first.write_text(
        json.dumps({"rows": [{"id": "q001", "reference_judge": {"verdict": "miss"}}]}),
        encoding="utf-8",
    )
    second.write_text(
        json.dumps({"rows": [{"id": "q001", "reference_judge": {"verdict": "exact"}}]}),
        encoding="utf-8",
    )
    candidate.write_text(json.dumps({"rows": [{"id": "q001"}]}), encoding="utf-8")

    group = load_group(f"demo:baseline={first}+{second},candidate={candidate}")

    assert group["labels"] == ["baseline", "candidate"]
    assert len(group["artifacts"][0]["paths"]) == 2
    assert group["artifacts"][0]["record"]["rows"][0]["reference_judge"]["verdict"] == "exact"


def test_guarded_activation_uses_activation_with_self_check(monkeypatch, tmp_path) -> None:
    baseline = tmp_path / "baseline.json"
    candidate = tmp_path / "candidate.json"
    out_json = tmp_path / "selector.json"
    out_md = tmp_path / "selector.md"
    row = {
        "id": "q001",
        "utterance": "Question?",
        "reference_judge": {"verdict": "partial"},
        "queries": ["fact(X)."],
        "query_results": [
            {"query": "fact(X).", "result": {"status": "success", "num_rows": 1, "rows": ["x"], "predicate": "fact"}}
        ],
        "self_check": {"notes": ["bounded note"]},
    }
    baseline.write_text(json.dumps({"rows": [row]}), encoding="utf-8")
    candidate_row = dict(row)
    candidate_row["reference_judge"] = {"verdict": "exact"}
    candidate.write_text(json.dumps({"rows": [candidate_row]}), encoding="utf-8")

    def fake_call_selector(**kwargs):
        assert kwargs["selection_policy"] == "activation"
        assert "self_check" in kwargs["row"]["modes"][0]["query_evidence"]
        return {"selected_mode": "candidate", "selection_confidence": 0.8}

    monkeypatch.setattr(select_qa_mode_without_oracle, "call_selector", fake_call_selector)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "select_qa_mode_without_oracle.py",
            "--selection-policy",
            "guarded_activation",
            "--group",
            f"demo:baseline={baseline},candidate={candidate}",
            "--out-json",
            str(out_json),
            "--out-md",
            str(out_md),
        ],
    )

    assert select_qa_mode_without_oracle.main() == 0
    report = json.loads(out_json.read_text(encoding="utf-8"))

    assert report["selection_policy"] == "guarded_activation"
    assert report["hybrid_llm_policy"] == "activation"
    assert report["hybrid_margin"] == 1.0
    assert report["hybrid_min_score"] == 4.0
    assert report["include_self_check"] is True
    assert report["summary"]["selected_exact"] == 1


def test_activation_selector_prompt_prioritizes_answer_bearing_support() -> None:
    from scripts.select_qa_mode_without_oracle import selector_system_prompt

    prompt = selector_system_prompt("activation")

    assert "answer-bearing support bundle" in prompt
    assert "do not reward directness by itself" in prompt
    assert "conflicting status" in prompt


def test_competition_substitute_scorer_guard_keeps_compact_role_surface() -> None:
    row = {
        "id": "q016",
        "question": "Who served as substitute scorer for the final?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 1, "predicate": "serves_as", "was_relaxed_fallback": False}
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "admin",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "score_certified_by",
                            "was_relaxed_fallback": False,
                        },
                        {"status": "success", "num_rows": 3, "predicate": "match_result", "was_relaxed_fallback": True},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    labels = ["baseline", "admin"]
    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=labels),
        mode_labels=labels,
        structural_choice="admin",
    )

    assert override == (
        "baseline",
        "substitute-scorer identity question needs compact service-role surface rather than certification/result volume",
    )


def test_attendance_count_guard_prefers_explicit_session_count_surface() -> None:
    row = {
        "id": "q010",
        "question": "How many students attended the Day 1 afternoon session?",
        "modes": [
            {
                "mode": "interval",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 30,
                            "predicate": "group_member",
                            "was_relaxed_fallback": True,
                        }
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "station_registry",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "session_attendance_count",
                            "was_relaxed_fallback": False,
                        }
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    labels = ["interval", "station_registry"]
    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=labels),
        mode_labels=labels,
        structural_choice="interval",
    )

    assert override == (
        "station_registry",
        "attendance-count question needs explicit session_attendance_count surface rather than interval roster volume",
    )


def test_attendance_count_guard_does_not_capture_total_trip_count() -> None:
    row = {
        "id": "q001",
        "question": "How many students went on the field trip?",
        "modes": [
            {
                "mode": "roster",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 1, "predicate": "attendance_final"}
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "station_registry",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 1, "predicate": "session_attendance_count"}
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    labels = ["roster", "station_registry"]
    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=labels),
        mode_labels=labels,
        structural_choice="station_registry",
    )

    assert override == (
        "roster",
        "student-count question needs scoped final-attendance surface rather than broad roster volume",
    )


def test_station_supervisor_guard_prefers_explicit_station_surface() -> None:
    row = {
        "id": "q016",
        "question": "Who supervised Station B at the tide pools?",
        "modes": [
            {
                "mode": "interval",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "supervision_assignment",
                            "was_relaxed_fallback": False,
                        }
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "station_registry",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "station_supervisor",
                            "was_relaxed_fallback": False,
                        }
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    labels = ["interval", "station_registry"]
    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=labels),
        mode_labels=labels,
        structural_choice="interval",
    )

    assert override == (
        "station_registry",
        "station-supervisor question needs explicit station_supervisor surface rather than standing group-supervision rows",
    )


def test_station_arrival_time_guard_prefers_event_timestamp_surface() -> None:
    row = {
        "id": "q024",
        "question": "What time did Ms. Okafor arrive at Station B?",
        "modes": [
            {
                "mode": "roster",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 10, "predicate": "person_id"},
                        {"status": "success", "num_rows": 8, "predicate": "location_id"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "interval",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 1, "predicate": "event_occurs"}
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    labels = ["roster", "interval"]
    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=labels),
        mode_labels=labels,
        structural_choice="roster",
    )

    assert override == (
        "interval",
        "station-arrival-time question needs event/timestamp surface rather than roster identity rows",
    )


def test_temporary_role_guard_prefers_roster_state_role_hints() -> None:
    row = {
        "id": "q033",
        "question": "What role was Lotte assigned on Day 3?",
        "modes": [
            {
                "mode": "station_role",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 2, "predicate": "group_member"}
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "station_helper",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 2, "predicate": "group_member"},
                        {"status": "success", "num_rows": 85, "predicate": "roster_state_support"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    labels = ["station_role", "station_helper"]
    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=labels),
        mode_labels=labels,
        structural_choice="station_role",
    )

    assert override == (
        "station_helper",
        "temporary-role question needs roster-state role-hint support rather than bare group membership",
    )


def test_completion_report_guard_prefers_summary_issue_surfaces() -> None:
    row = {
        "id": "q039",
        "question": "List all incidents noted in Ms. Strand's trip completion report.",
        "modes": [
            {
                "mode": "station_registry",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 1, "predicate": "incident_report"}
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "station_role",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 3, "predicate": "trip_outcome"},
                        {"status": "success", "num_rows": 8, "predicate": "unresolved_issue"},
                        {"status": "success", "num_rows": 2, "predicate": "medical_event"},
                        {"status": "success", "num_rows": 2, "predicate": "hazard_identified"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    labels = ["station_registry", "station_role"]
    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=labels),
        mode_labels=labels,
        structural_choice="station_registry",
    )

    assert override == (
        "station_role",
        "completion-report incident list needs trip-outcome plus issue/medical/hazard surfaces",
    )


def test_competition_corrected_rank_guard_prefers_rank_correction_surface() -> None:
    row = {
        "id": "q029",
        "question": "What is the corrected rank order of the top four?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 6, "predicate": "qualifying_total", "was_relaxed_fallback": False}
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "admin",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 6, "predicate": "qualifying_rank", "was_relaxed_fallback": True},
                        {"status": "success", "num_rows": 2, "predicate": "score_correction", "was_relaxed_fallback": True},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    labels = ["baseline", "admin"]
    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=labels),
        mode_labels=labels,
        structural_choice="baseline",
    )

    assert override == (
        "admin",
        "corrected-rank-order question needs qualifying-rank plus score-correction surface rather than raw total volume",
    )


def test_competition_hold_call_guard_prefers_timing_condition_surface() -> None:
    row = {
        "id": "q022",
        "question": "Why didn't Bryce Emmet call a hold during the wind gust?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 1, "predicate": "event_condition", "was_relaxed_fallback": False},
                        {"status": "success", "num_rows": 1, "predicate": "serves_as", "was_relaxed_fallback": False},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "admin",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 1, "predicate": "witness_statement", "was_relaxed_fallback": False},
                        {"status": "success", "num_rows": 1, "predicate": "incident", "was_relaxed_fallback": False},
                        {"status": "success", "num_rows": 1, "predicate": "marshal_ruling", "was_relaxed_fallback": False},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    labels = ["baseline", "admin"]
    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=labels),
        mode_labels=labels,
        structural_choice="admin",
    )

    assert override == (
        "baseline",
        "hold-call rationale question needs event-condition timing surface rather than broad witness/incident volume",
    )


def test_call_selector_retries_invalid_json(monkeypatch) -> None:
    calls = 0

    def fake_completion(**_kwargs):
        nonlocal calls
        calls += 1
        if calls == 1:
            return '{"schema_version": "qa_mode_selector_v1", "selected_mode": '
        return json.dumps(
            {
                "schema_version": "qa_mode_selector_v1",
                "selected_mode": "baseline",
                "selection_confidence": 0.8,
                "evidence_quality_by_mode": [
                    {"mode": "baseline", "quality": "strong", "reason": "direct evidence"}
                ],
                "rationale": "baseline has the answer-bearing row",
                "risks": [],
            }
        )

    monkeypatch.setattr(select_qa_mode_without_oracle, "_selector_completion_content", fake_completion)

    selected = call_selector(
        base_url="http://127.0.0.1:1234/v1",
        model="test",
        timeout=1,
        temperature=0.0,
        top_p=1.0,
        max_tokens=100,
        row={"id": "q001", "question": "Q?", "modes": []},
        mode_labels=["baseline"],
        selection_policy="activation",
    )

    assert calls == 2
    assert selected["selected_mode"] == "baseline"


def test_protected_selector_keeps_structural_for_compact_candidate() -> None:
    row = {
        "id": "q007",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 1, "predicate": "answer", "was_relaxed_fallback": False}
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "evidence",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 1, "predicate": "answer", "was_relaxed_fallback": False},
                        {"status": "success", "num_rows": 1, "predicate": "detail", "was_relaxed_fallback": True},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }
    fallback_calls = 0

    def fallback_selector(**_kwargs):
        nonlocal fallback_calls
        fallback_calls += 1
        return {"selected_mode": "baseline"}

    selected = protected_selector(row=row, mode_labels=["baseline", "evidence"], fallback_selector=fallback_selector)

    assert fallback_calls == 0
    assert selected["selected_mode"] == "evidence"
    assert selected["selection_source"] == "protected_structural"


def test_protected_selector_calls_activation_for_high_volume_candidate() -> None:
    row = {
        "id": "q009",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 2, "predicate": "answer", "was_relaxed_fallback": False}
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "evidence",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 14, "predicate": "answer", "was_relaxed_fallback": False},
                        {"status": "success", "num_rows": 14, "predicate": "detail", "was_relaxed_fallback": True},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }
    fallback_calls = 0

    def fallback_selector(**_kwargs):
        nonlocal fallback_calls
        fallback_calls += 1
        return {"selected_mode": "baseline", "selection_confidence": 0.8}

    selected = protected_selector(row=row, mode_labels=["baseline", "evidence"], fallback_selector=fallback_selector)

    assert fallback_calls == 1
    assert selected["selected_mode"] == "baseline"
    assert selected["selection_source"] == "protected_llm"
