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


def test_hybrid_selector_routes_valid_period_to_union_validity_surface_without_guard() -> None:
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
    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=["baseline", "union"]),
        mode_labels=["baseline", "union"],
        structural_choice="baseline",
    )

    assert override is None

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "union"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "union"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected.get("specialized_guard_reason", "") == ""
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 8.0


def test_focus_scoring_routes_reinspection_count_to_compact_aggregate_surface() -> None:
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
                "mode": "compact_inspection",
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
    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "compact_inspection", "lifecycle"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda *, row, mode_labels: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "compact_inspection"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert "specialized_guard_reason" not in selected


def test_hybrid_selector_prefers_unrestricted_active_count_baseline_without_guard() -> None:
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
    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "union"],
        margin=1.0,
        min_score=4.0,
        guard_disable_regex=compile_guard_disable_regex("unrestricted-active count"),
        fallback_selector=lambda *, row, mode_labels: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "baseline"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert "specialized_guard_reason" not in selected


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

    assert override is None

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "union"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "baseline"
    assert selected.get("specialized_guard_reason", "") == ""


def test_hybrid_selector_prefers_alternative_inscription_union_surface_without_guard() -> None:
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
    selected = hybrid_selector(
        row=row,
        mode_labels=["candidate", "union"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "candidate"},
    )

    assert selected["selected_mode"] == "union"
    assert selected.get("specialized_guard_reason", "") == ""


def test_hybrid_selector_prefers_intake_photo_consistency_surface_without_guard() -> None:
    row = {
        "id": "q_false_conflict",
        "question": "Is the intake receipt consistent with the photo?",
        "modes": [
            _mode_with_predicates("ledger_fragments", ["ledger_entry", "row_value"], rows=8),
            _mode_with_predicates("paired_interpretation", ["records_intake", "shows_location", "asserts"], rows=2),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["ledger_fragments", "paired_interpretation"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "paired_interpretation"
    assert selected.get("specialized_guard_reason", "") == ""


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


def test_raw_timestamp_focus_prefers_raw_timestamp_surface() -> None:
    row = {
        "id": "q007",
        "question": "What is the raw (uncorrected) timestamp of BAS-002?",
        "modes": [
            _mode_with_predicates("cold", ["recorded_access_event", "clock_drift_applied"], rows=6),
            _mode_with_predicates("entity", ["raw_timestamp"], rows=2),
        ],
    }

    selected = structural_selector(row=row, mode_labels=["cold", "entity"])

    assert selected["selected_mode"] == "entity"
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 9.0


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

    assert selected["selected_mode"] == "entity"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert "specialized_guard_reason" not in selected
    assert "disabled_guard_reasons" not in selected


def test_raw_timestamp_focus_selects_raw_timestamp_surface_with_guard_disabled() -> None:
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
        margin=1,
        min_score=4,
        fallback_selector=lambda *, row, mode_labels: (_ for _ in ()).throw(AssertionError("fallback called")),
        guard_disable_regex=compile_guard_disable_regex("raw-timestamp question"),
    )

    assert selected["selected_mode"] == "entity"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert "disabled_guard_reasons" not in selected


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
    assert "specialized_guard_reason" not in selected
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

    assert override is None

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "parallel", "entity"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "parallel"
    assert selected["selection_source"] == "hybrid_structural"


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

    assert override is None

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "parallel", "entity"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "entity"
    assert selected["selection_source"] == "hybrid_structural"


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

    assert override is None

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "entity"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "entity"
    assert selected["selection_source"] == "hybrid_structural"


def test_clear_sample_clock_snapshot_focus_prefers_pause_helper_surface() -> None:
    row = {
        "id": "q029",
        "question": "What was the state of the clear-sample clock at 2026-05-01 10:00 according to the snapshot table, and how many hours had been counted?",
        "modes": [
            _mode_with_predicates("entity", ["event_description", "event_timestamp", "sampler_state"], rows=64, relaxed=True),
            {
                "mode": "pause_helper",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "clear_sample_clock_pause_support",
                            "was_relaxed_fallback": True,
                            "sample_rows": [
                                {
                                    "SupportKind": "clear_sample_clock_pause",
                                    "ClockState": "paused",
                                    "CountedHours": "18",
                                }
                            ],
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
        mode_labels=["entity", "pause_helper"],
        margin=1,
        min_score=4,
        fallback_selector=lambda *, row, mode_labels: (_ for _ in ()).throw(AssertionError("fallback called")),
        guard_disable_regex=compile_guard_disable_regex("clear-sample clock snapshot question"),
    )

    assert selected["selected_mode"] == "pause_helper"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert "disabled_guard_reasons" not in selected


def test_lift_notification_clock_begin_focus_prefers_trigger_timestamp_surface() -> None:
    row = {
        "id": "q014",
        "question": "At what date and time did the §6.3 48-hour lift-notification clock begin?",
        "modes": [
            _mode_with_predicates("memory_ledger_combo", ["deadline_origin", "event_occurred"], rows=1),
            _mode_with_predicates(
                "parallel",
                ["deadline_trigger", "event_as_logged", "deadline_original", "deadline_adjusted"],
                rows=2,
            ),
            _mode_with_predicates("pause_helper", ["deadline_trigger", "event_as_logged", "deadline_rule"], rows=2),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["memory_ledger_combo", "parallel", "pause_helper"],
        margin=1,
        min_score=4,
        fallback_selector=lambda *, row, mode_labels: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "parallel"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


def test_temporal_full_replay_blocker_focuses_use_answer_bearing_surfaces() -> None:
    scenarios = [
        (
            "q007",
            "Who is recorded as the compiler of this packet?",
            [
                _mode_with_predicates("memory_ledger_combo", ["person_role"], rows=4),
                _mode_with_predicates("parallel", ["document_compiler", "person_role"], rows=1),
            ],
            "parallel",
        ),
        (
            "q010",
            "On what date did the metrology technician perform the review of the S-3 sampler-controller clock drift?",
            [
                _mode_with_predicates("parallel", ["event_as_logged", "person_role"], rows=14),
                _mode_with_predicates(
                    "source_record_facts_v2",
                    ["source_record_text_atom", "event_timestamp", "person_role"],
                    rows=2,
                ),
            ],
            "source_record_facts_v2",
        ),
        (
            "q017",
            "What was the total active duration of BWN-2026-04-28-A from issuance to lift?",
            [
                _mode_with_predicates("cold", ["event_description", "event_id"], rows=14),
                _mode_with_predicates("pause_helper", ["notice_issued", "notice_lifted"], rows=4, relaxed=True),
            ],
            "pause_helper",
        ),
        (
            "q018",
            "What was the total active duration of RUN-2026-04-28-B from issuance to lift?",
            [
                _mode_with_predicates("cold", ["event_description", "event_id"], rows=28),
                _mode_with_predicates("pause_helper", ["notice_issued", "notice_lifted"], rows=9, relaxed=True),
            ],
            "pause_helper",
        ),
        (
            "q019",
            "What was the duration of the first sampler-offline interval (E-04 corrected to E-05)?",
            [
                _mode_with_predicates("cold", ["event_corrected_from", "event_description"], rows=3),
                _mode_with_predicates(
                    "pause_helper",
                    ["clear_sample_clock_pause_support", "sampler_offline_interval"],
                    rows=25,
                    relaxed=True,
                ),
            ],
            "pause_helper",
        ),
        (
            "q036",
            "What is the status, as of packet close, of the engineering review report on the cause of the 2026-04-28 contamination, and by what date is it expected?",
            [
                _mode_with_predicates("parallel", ["event_description", "projection_content"], rows=28),
                _mode_with_predicates("entity", ["open_item_description", "open_item_expected_date"], rows=2),
            ],
            "entity",
        ),
        (
            "q040",
            "If the §6.3 weekend-shift rule had not been applied, by how many hours would the Authority have missed the §6.3 deadline given that the Lift Notice was issued at 2026-05-04 12:00?",
            [
                _mode_with_predicates("source_record", ["event_timestamp_as_logged", "notice_issued_at"], rows=14),
                _mode_with_predicates(
                    "parallel",
                    ["deadline_adjusted", "deadline_original", "notice_issued"],
                    rows=3,
                ),
            ],
            "parallel",
        ),
    ]

    for qid, question, modes, expected in scenarios:
        selected = hybrid_selector(
            row={"id": qid, "question": question, "modes": modes},
            mode_labels=[mode["mode"] for mode in modes],
            margin=1,
            min_score=4,
            fallback_selector=lambda *, row, mode_labels: (_ for _ in ()).throw(AssertionError("fallback called")),
        )

        assert selected["selected_mode"] == expected
        assert selected["selection_source"] == "hybrid_structural"
        assert selected["hybrid_decision"] == "structural_confident"


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

    assert override is None

    selected = hybrid_selector(
        row=row,
        mode_labels=["source_record", "cold"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "cold"
    assert selected["selection_source"] == "hybrid_structural"


def test_corrected_timestamp_focus_prefers_corrected_timestamp_surface() -> None:
    row = {
        "id": "q011",
        "question": "What is the corrected timestamp of event E-04 under §6.5?",
        "modes": [
            _mode_with_predicates("cold", ["event_corrected_from", "rule_description"], rows=1),
            _mode_with_predicates("entity", ["event_corrected_timestamp", "event_description"], rows=1),
        ],
    }

    selected = structural_selector(row=row, mode_labels=["cold", "entity"])

    assert selected["selected_mode"] == "entity"
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 6.0


def test_corrected_timestamp_focus_selects_explicit_timestamp_with_guard_disabled() -> None:
    row = {
        "id": "q011",
        "question": "What is the corrected timestamp of event E-04 under rule 6.5?",
        "modes": [
            _mode_with_predicates("cold", ["event_corrected_from", "rule_description"], rows=8, relaxed=True),
            _mode_with_predicates("entity", ["event_corrected_timestamp", "event_description"], rows=1, relaxed=True),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "entity"],
        margin=1,
        min_score=4,
        fallback_selector=lambda *, row, mode_labels: (_ for _ in ()).throw(AssertionError("fallback called")),
        guard_disable_regex=compile_guard_disable_regex("corrected-timestamp question"),
    )

    assert selected["selected_mode"] == "entity"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert "disabled_guard_reasons" not in selected


def test_corrected_duration_focus_prefers_paired_badge_timestamps() -> None:
    row = {
        "id": "q015",
        "question": "How long, on the corrected timeline, was the badge holder inside Lab 4-C?",
        "modes": [
            _mode_with_predicates("source_record", ["corrected_timestamp"], rows=18),
            _mode_with_predicates("parallel", ["badge_used", "raw_timestamp", "corrected_timestamp"], rows=1, relaxed=True),
        ],
    }

    selected = structural_selector(row=row, mode_labels=["source_record", "parallel"])

    assert selected["selected_mode"] == "parallel"
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 8.0


def test_corrected_duration_focus_selects_paired_timestamp_surface_with_guard_disabled() -> None:
    row = {
        "id": "q015",
        "question": "How long, on the corrected timeline, was the badge holder inside Lab 4-C?",
        "modes": [
            _mode_with_predicates("source_record", ["corrected_timestamp"], rows=18),
            _mode_with_predicates("parallel", ["badge_used", "raw_timestamp", "corrected_timestamp"], rows=1, relaxed=True),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["source_record", "parallel"],
        margin=1,
        min_score=4,
        fallback_selector=lambda *, row, mode_labels: (_ for _ in ()).throw(AssertionError("fallback called")),
        guard_disable_regex=compile_guard_disable_regex("corrected-duration question"),
    )

    assert selected["selected_mode"] == "parallel"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert "disabled_guard_reasons" not in selected


def test_timekeeping_clock_out_focus_selects_assignment_interval_with_guard_disabled() -> None:
    row = {
        "id": "q004",
        "question": "At what time did Devon Ramos clock out of the timekeeping system?",
        "modes": [
            _mode_with_predicates("cold", ["badge_access"], rows=1),
            _mode_with_predicates("source_record", ["assignment_interval"], rows=1),
            _mode_with_predicates("archival_row_ledger_v1", ["row_event", "source_record_row"], rows=12),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1,
        min_score=4,
        fallback_selector=lambda *, row, mode_labels: (_ for _ in ()).throw(AssertionError("fallback called")),
        guard_disable_regex=compile_guard_disable_regex("timekeeping clock-out question"),
    )

    assert selected["selected_mode"] == "source_record"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert "disabled_guard_reasons" not in selected


def test_version_choice_focus_prefers_correction_rows_over_source_volume() -> None:
    row = {
        "id": "q018",
        "question": "Which version of the Pyxis nightly summary should the timeline use, the nightly summary or the central pharmacy server record?",
        "modes": [
            _mode_with_predicates("cold", ["system_log_entry", "correction_applied"], rows=2),
            _mode_with_predicates("source_record", ["controlling_source", "source_document_type"], rows=9),
            _mode_with_predicates("archival_row_ledger_v1", ["row_value", "source_section"], rows=51, relaxed=True),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1,
        min_score=4,
        fallback_selector=lambda *, row, mode_labels: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "cold"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


def test_assigned_role_focus_prefers_assignment_interval_over_archival_rows() -> None:
    row = {
        "id": "q021",
        "question": "As of 15:00, who was the assigned floor RN for Room 504?",
        "modes": [
            _mode_with_predicates("cold", ["badge_access", "system_log_entry", "statement_made"], rows=25),
            _mode_with_predicates("source_record", ["assignment_interval"], rows=12, relaxed=True),
            _mode_with_predicates("archival_row_ledger_v1", ["row_location", "row_time", "row_value"], rows=26),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1,
        min_score=4,
        fallback_selector=lambda *, row, mode_labels: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "source_record"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


def test_lab_value_focus_prefers_archival_row_value_over_event_volume() -> None:
    row = {
        "id": "q006",
        "question": "What was the patient's morning potassium value?",
        "modes": [
            _mode_with_predicates("cold", ["clinical_order", "system_log_entry"], rows=12, relaxed=True),
            _mode_with_predicates("source_record", ["event_attribute", "log_event"], rows=29),
            _mode_with_predicates("archival_row_ledger_v1", ["row_value"], rows=51, relaxed=True),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1,
        min_score=4,
        fallback_selector=lambda *, row, mode_labels: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "archival_row_ledger_v1"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


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

    assert override is None

    selected = hybrid_selector(
        row=row,
        mode_labels=["source_record_facts", "source_record"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "source_record"
    assert selected["selection_source"] == "hybrid_structural"


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

    assert override is None

    selected = hybrid_selector(
        row=row,
        mode_labels=["source_record_facts", "entity"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "entity"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected.get("specialized_guard_reason", "") == ""


def test_active_held_count_prefers_current_label_status_filter_surface() -> None:
    row = {
        "id": "q040",
        "question": "Counting only currently active labels and excluding any item that has already been released from custody, how many items remain physically held in the evidence room?",
        "modes": [
            _mode_with_predicates("cold", ["current_exhibit_label", "item_status", "item_location"], rows=9),
            _mode_with_predicates("source_record", ["has_current_label", "custody_status", "located_at"], rows=12),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "source_record"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected.get("specialized_guard_reason", "") == ""


def test_hybrid_selector_prefers_current_label_status_filter_without_guard() -> None:
    row = {
        "id": "q040",
        "question": "Counting only currently active labels and excluding any item that has already been released from custody, how many items remain physically held in the evidence room?",
        "modes": [
            _mode_with_predicates("cold", ["current_exhibit_label", "item_status", "item_location"], rows=9),
            _mode_with_predicates("parallel", ["item_status", "current_location", "withdrawn_label"], rows=12),
            _mode_with_predicates("entity", ["status_of", "located_at"], rows=12),
            _mode_with_predicates("source_record", ["custody_status", "has_current_label", "located_at"], rows=12),
            _mode_with_predicates(
                "source_record_facts_v2",
                ["has_current_label", "custody_status", "located_at"],
                rows=12,
            ),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "parallel", "entity", "source_record", "source_record_facts_v2"],
        margin=1.0,
        min_score=4.0,
        guard_disable_regex=compile_guard_disable_regex("active-held count question"),
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] in {"source_record", "source_record_facts_v2"}
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


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

    assert override is None

    selected = hybrid_selector(
        row=row,
        mode_labels=["parallel", "source_record_facts_v2", "source_record"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "source_record"
    assert selected["selection_source"] == "hybrid_structural"


def test_hybrid_selector_prefers_reading_access_restriction_surface_without_guard() -> None:
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

    assert override is None

    selected = hybrid_selector(
        row=row,
        mode_labels=["source_record_facts_v2", "source_record", "memory_ledger_combo"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "memory_ledger_combo"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected.get("specialized_guard_reason", "") == ""


def test_physical_custody_item_count_guard_is_retired() -> None:
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

    assert override is None


def test_hybrid_selector_prefers_physical_custody_count_helper_without_guard() -> None:
    row = {
        "id": "q022",
        "question": "How many items remain in Pellico's physical custody as of 2026-04-30?",
        "modes": [
            _mode_with_predicates("parallel", ["physical_custodian"], rows=3),
            {
                "mode": "authority_helper",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 7,
                            "predicate": "physical_custody",
                            "was_relaxed_fallback": False,
                        },
                        {
                            "status": "success",
                            "num_rows": 5,
                            "predicate": "archive_authority_custody_support",
                            "was_relaxed_fallback": False,
                            "sample_rows": [{"SupportKind": "physical_custody_count"}],
                        },
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            _mode_with_predicates("source_record_facts_v2", ["physical_custody"], rows=7),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["parallel", "authority_helper", "source_record_facts_v2"],
        margin=1.0,
        min_score=4.0,
        guard_disable_regex=compile_guard_disable_regex("physical-custody item-count question"),
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "authority_helper"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


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

    assert override is None

    selected = hybrid_selector(
        row=row,
        mode_labels=["source_record", "entity"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "entity"
    assert selected["selection_source"] == "hybrid_structural"


def test_hybrid_selector_prefers_custody_restriction_surface_without_guard() -> None:
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

    assert override is None

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "source_record"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected.get("specialized_guard_reason", "") == ""


def test_hybrid_selector_prefers_agreement_addition_surface_without_guard() -> None:
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

    assert override is None

    selected = hybrid_selector(
        row=row,
        mode_labels=["source_record", "parallel"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "parallel"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected.get("specialized_guard_reason", "") == ""


def test_hybrid_selector_prefers_state_access_relation_surfaces_without_guards() -> None:
    cases = [
        (
            {
                "id": "q_universal_scope",
                "question": "Did all distributors acknowledge the notice before the deadline?",
                "modes": [
                    _mode_with_predicates("report_details", ["report_submitted", "acknowledgment_received"], rows=3),
                    _mode_with_predicates(
                        "set_enumeration",
                        ["acknowledgment_received", "deadline_met", "deadline_exceeded"],
                        rows=7,
                    ),
                ],
            },
            ["report_details", "set_enumeration"],
            "set_enumeration",
        ),
        (
            {
                "id": "q_target_affected",
                "question": "Is Lot 7200-2024-G affected by the recall?",
                "modes": [
                    _mode_with_predicates("broad_affected_listing", ["lot_affected"], rows=20, relaxed=True),
                    _mode_with_predicates("target_check", ["lot_affected", "correction_applied", "unit_count"], rows=2),
                ],
            },
            ["broad_affected_listing", "target_check"],
            "target_check",
        ),
        (
            {
                "id": "q_possession_ownership",
                "question": "Who carries the object after inheriting ownership?",
                "modes": [
                    _mode_with_predicates("broad_event_rule", ["event_actor", "rule_text"], rows=8),
                    _mode_with_predicates("ownership_distinction", ["inherits", "owns", "possesses"], rows=3),
                ],
            },
            ["broad_event_rule", "ownership_distinction"],
            "ownership_distinction",
        ),
        (
            {
                "id": "q_legal_title",
                "question": "Which claimant has the stronger title?",
                "modes": [
                    _mode_with_predicates("static_owner_rows", ["legal_owner"], rows=4),
                    _mode_with_predicates("claim_transfer_rows", ["claimed_by", "transferred_ownership"], rows=3),
                ],
            },
            ["static_owner_rows", "claim_transfer_rows"],
            "claim_transfer_rows",
        ),
    ]

    for row, labels, expected in cases:
        selected = hybrid_selector(
            row=row,
            mode_labels=labels,
            margin=1.0,
            min_score=4.0,
            fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
        )

        assert selected["selected_mode"] == expected
        assert selected["selection_source"] == "hybrid_structural"
        assert selected.get("specialized_guard_reason", "") == ""


def test_photograph_album_interval_guard_is_retired() -> None:
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

    assert override is None


def test_hybrid_selector_prefers_photograph_album_interval_surface_without_guard() -> None:
    row = {
        "id": "q036",
        "question": "During what interval was the photograph album physically at Pellico's premises despite being on the conservation intake list at Stille?",
        "modes": [
            _mode_with_predicates("parallel", ["access_event", "physical_custodian", "recall_event"], rows=5),
            _mode_with_predicates("entity", ["access_log_entry", "physical_custodian", "recall_event"], rows=3),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["parallel", "entity"],
        margin=1.0,
        min_score=4.0,
        guard_disable_regex=compile_guard_disable_regex("photograph-album interval question"),
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "entity"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


def test_hybrid_selector_prefers_publication_right_surface_for_grant_question() -> None:
    row = {
        "id": "q027",
        "question": "Does Stille have any right to grant publication of items in its custody?",
        "modes": [
            _mode_with_predicates("source_record_facts", ["board_policy", "conservation_intake", "parties"], rows=16),
            _mode_with_predicates("source_record", ["publication_authority", "reserved_right"], rows=2),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["source_record_facts", "source_record"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "source_record"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


def test_hybrid_selector_prefers_direct_legal_title_interval_surface() -> None:
    row = {
        "id": "q029",
        "question": "Since when has the Pellico Society held legal title to Notebook A?",
        "modes": [
            _mode_with_predicates("source_record_facts", ["legal_document", "parties", "document_type"], rows=16),
            _mode_with_predicates(
                "memory_ledger_combo",
                ["custody_transfer", "instrument_date", "instrument_party", "legal_title_holder"],
                rows=10,
            ),
            _mode_with_predicates("cold", ["legal_title_holder", "physical_custodian"], rows=2),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["source_record_facts", "memory_ledger_combo", "cold"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "cold"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


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

    assert override is None

    selected = hybrid_selector(
        row=row,
        mode_labels=["source_record_facts", "memory_ledger_combo", "source_record"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] in {"memory_ledger_combo", "source_record"}
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected.get("specialized_guard_reason", "") == ""


def test_expected_order_guard_prefers_expected_order_surface() -> None:
    row = {
        "id": "q039",
        "question": "When is Judge Anwar's order on EX-C-01 expected?",
        "modes": [
            _mode_with_predicates("source_record", ["has_open_exception"], rows=5),
            _mode_with_predicates("parallel", ["expected_order_date"], rows=1),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["source_record", "parallel"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "source_record"},
    )

    assert selected["selected_mode"] == "parallel"
    assert selected.get("specialized_guard_reason", "") == ""


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

    assert override is None

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "entity"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "entity"
    assert selected.get("specialized_guard_reason", "") == ""


def retired_evidence_source_count_unresolved_guard_prefers_source_catalog_surface() -> None:
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
        "evidence-source count question needs source-id catalog surface rather than unresolved-fact volume",
    )


def retired_evidence_source_count_unresolved_guard_prefers_source_id_over_generic_source_rows() -> None:
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
        "evidence-source count question needs source-id catalog surface rather than unresolved-fact volume",
    )


def test_evidence_source_count_focus_prefers_source_id_without_guard() -> None:
    row = {
        "id": "q031",
        "question": "How many distinct evidence sources are cataloged in Â§2?",
        "modes": [
            _mode_with_predicates("cold", ["evidence_source"], rows=14),
            _mode_with_predicates("entity", ["source_id"], rows=12),
            _mode_with_predicates("source_record_facts", ["activity_unresolved", "person"], rows=13),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "entity", "source_record_facts"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
        guard_disable_regex=compile_guard_disable_regex("evidence-source count question needs source-id catalog surface"),
    )

    assert selected["selected_mode"] == "entity"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


def test_reported_lost_badge_question_prefers_source_record_content_surface() -> None:
    row = {
        "id": "q040",
        "question": "Has Aldridge reported badge BDG-44217 as lost or stolen?",
        "modes": [
            _mode_with_predicates("entity", ["email_content", "memo_content", "unresolved_question"], rows=10),
            _mode_with_predicates("source_record", ["evidence_content", "source_record"], rows=16),
            _mode_with_predicates("source_record_facts", ["allegation_of", "denial_of"], rows=2),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["entity", "source_record", "source_record_facts"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "source_record"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


def test_testimony_reliability_question_prefers_testimony_scope_surface() -> None:
    row = {
        "id": "q021",
        "question": "What does Okafor's testimony reliably establish?",
        "modes": [
            _mode_with_predicates(
                "entity",
                ["witness_statement", "testimony_scope", "source_reliability_for", "source_reliability_not_for"],
                rows=2,
            ),
            _mode_with_predicates("source_record_facts", ["role_of", "allegation_of", "activity_unresolved"], rows=3),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["entity", "source_record_facts"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "entity"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


def test_evidence_source_count_focus_prefers_section_catalog_source_record_facts_v2() -> None:
    row = {
        "id": "q031",
        "question": "How many distinct evidence sources are cataloged in §2?",
        "modes": [
            _mode_with_predicates("source_record_facts", ["activity_unresolved", "person"], rows=13),
            _mode_with_predicates("entity", ["source_id"], rows=12),
            _mode_with_predicates(
                "source_record_facts_v2",
                ["evidence_source", "source_record_section", "source_record_label", "source_record_text_atom"],
                rows=11,
            ),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["source_record_facts", "entity", "source_record_facts_v2"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
        guard_disable_regex=compile_guard_disable_regex("evidence-source count question needs source-id catalog surface"),
    )

    assert selected["selected_mode"] == "source_record_facts_v2"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


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

    assert override is None

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "entity"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "entity"
    assert selected.get("specialized_guard_reason", "") == ""


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

    assert override is None

    selected = hybrid_selector(
        row=row,
        mode_labels=["source_record_facts", "source_record"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "source_record"
    assert selected.get("specialized_guard_reason", "") == ""


def test_communications_officer_guard_prefers_notice_role_surface() -> None:
    row = {
        "id": "q009",
        "question": "Who is named as the Communications Officer who drafted BWN-2026-04-28-A, RUN-2026-04-28-B, and LFT-2026-05-04?",
        "modes": [
            _mode_with_predicates("source_record", ["notice_id", "person_name", "person_role"], rows=4),
            _mode_with_predicates("memory_ledger_combo", ["notice_issued", "person_role"], rows=16),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["source_record", "memory_ledger_combo"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "source_record"},
    )

    assert selected["selected_mode"] == "memory_ledger_combo"
    assert selected.get("specialized_guard_reason", "") == ""


def test_structural_selector_prefers_interval_count_surface_over_event_volume() -> None:
    row = {
        "id": "q022",
        "question": "How many distinct sampler-offline intervals occurred at Station S-3 during the event?",
        "modes": [
            _mode_with_predicates(
                "cold",
                ["event_id", "event_description", "rule_description"],
                rows=8,
            ),
            _mode_with_predicates("parallel", ["sampler_offline_interval"], rows=4, relaxed=True),
        ],
    }

    selected = structural_selector(row=row, mode_labels=["cold", "parallel"])

    assert selected["selected_mode"] == "parallel"
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 7.5


def test_hybrid_selector_trusts_focused_interval_count_surface_without_model_call() -> None:
    row = {
        "id": "q022",
        "question": "How many distinct sampler-offline intervals occurred at Station S-3 during the event?",
        "modes": [
            _mode_with_predicates(
                "cold",
                ["event_id", "event_description", "rule_description"],
                rows=8,
            ),
            _mode_with_predicates("parallel", ["sampler_offline_interval"], rows=4, relaxed=True),
        ],
    }
    fallback_calls = 0

    def fallback_selector(**_kwargs):
        nonlocal fallback_calls
        fallback_calls += 1
        return {"selected_mode": "cold"}

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "parallel"],
        margin=1.0,
        min_score=3.0,
        fallback_selector=fallback_selector,
        guard_disable_regex=compile_guard_disable_regex("sampler-offline interval count"),
    )

    assert fallback_calls == 0
    assert selected["selected_mode"] == "parallel"
    assert selected["hybrid_decision"] == "structural_confident"


def test_structural_selector_prefers_state_transition_count_surface_over_event_volume() -> None:
    row = {
        "id": "q022",
        "question": "How many distinct sampler-offline intervals occurred at Station S-3 during the event?",
        "modes": [
            _mode_with_predicates(
                "cold",
                ["event_id", "event_description", "rule_description"],
                rows=8,
            ),
            {
                "mode": "entity",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 2,
                            "predicate": "sampler_state",
                            "was_relaxed_fallback": False,
                        },
                        {
                            "status": "success",
                            "num_rows": 2,
                            "predicate": "sampler_state_cause",
                            "was_relaxed_fallback": False,
                        },
                        {
                            "status": "success",
                            "num_rows": 8,
                            "predicate": "sampler_state",
                            "was_relaxed_fallback": True,
                        },
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = structural_selector(row=row, mode_labels=["cold", "entity"])

    assert selected["selected_mode"] == "entity"
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 1.5


def test_structural_selector_prefers_roster_table_count_support_for_registrar_count() -> None:
    row = {
        "id": "q012",
        "question": "How many distinct students are on the trip per the registrar in v1.0?",
        "modes": [
            _mode_with_predicates("alias_full", ["roster_table_member"], rows=39),
            _mode_with_predicates(
                "count_full",
                ["roster_table_count_support", "roster_table_member"],
                rows=40,
                relaxed=True,
            ),
        ],
    }

    selected = structural_selector(row=row, mode_labels=["alias_full", "count_full"])

    assert selected["selected_mode"] == "count_full"
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 4.0


def test_hybrid_selector_trusts_roster_table_count_support_when_guard_disabled() -> None:
    row = {
        "id": "q012",
        "question": "How many distinct students are on the trip per the registrar in v1.0?",
        "modes": [
            _mode_with_predicates("alias_full", ["roster_table_member"], rows=39),
            _mode_with_predicates(
                "count_full",
                ["roster_table_count_support", "roster_table_member"],
                rows=40,
                relaxed=True,
            ),
        ],
    }
    fallback_calls = 0

    def fallback_selector(**_kwargs):
        nonlocal fallback_calls
        fallback_calls += 1
        return {"selected_mode": "alias_full"}

    selected = hybrid_selector(
        row=row,
        mode_labels=["alias_full", "count_full"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=fallback_selector,
        guard_disable_regex=compile_guard_disable_regex("distinct-student registrar count"),
    )

    assert fallback_calls == 0
    assert selected["selected_mode"] == "count_full"
    assert selected["hybrid_decision"] == "structural_confident"


def test_structural_selector_prefers_roster_entry_preserving_surface() -> None:
    row = {
        "id": "q011",
        "question": "How many student entries appear in roster v1.0?",
        "modes": [
            _mode_with_predicates("entity", ["student_in_homeroom"], rows=8),
            _mode_with_predicates("cold", ["student_in_homeroom"], rows=125, relaxed=True),
        ],
    }

    selected = structural_selector(row=row, mode_labels=["entity", "cold"])

    assert selected["selected_mode"] == "cold"
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 7.0


def test_hybrid_selector_prefers_scoped_roster_section_surface_without_guard() -> None:
    row = {
        "id": "q013",
        "question": "How many people are in the original roster section, excluding activity-log-only rows?",
        "modes": [
            _mode_with_predicates("activity_log", ["badge_log"], rows=45),
            _mode_with_predicates("source_record_facts", ["assignment_interval", "source_section"], rows=2),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["activity_log", "source_record_facts"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "source_record_facts"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 5.0
    assert selected.get("specialized_guard_reason", "") == ""


def test_scoped_roster_count_phrase_no_longer_has_selector_guard() -> None:
    row = {
        "id": "q_scoped_roster_count_retired_guard",
        "question": "How many people are in the original roster section, excluding activity-log-only rows?",
        "modes": [
            _mode_with_predicates("activity_log", ["badge_log"], rows=45),
            _mode_with_predicates("source_record_facts", ["assignment_interval", "source_section"], rows=2),
        ],
    }
    labels = ["activity_log", "source_record_facts"]
    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=labels),
        mode_labels=labels,
        structural_choice="activity_log",
    )

    assert override is None


def test_structural_selector_prefers_section_membership_count_on_unlike_training_roster() -> None:
    row = {
        "id": "q_scoped_section_count_unlike",
        "question": "How many trainees are listed in the roster section, excluding sign-in-only entries?",
        "modes": [
            _mode_with_predicates("activity_log", ["badge_log", "check_in_event"], rows=52, relaxed=True),
            _mode_with_predicates("source_record_facts", ["assignment_interval", "source_section"], rows=3),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["activity_log", "source_record_facts"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "source_record_facts"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 5.0


def test_structural_selector_prefers_homeroom_reassignment_count_support() -> None:
    row = {
        "id": "q027",
        "question": "Did the total student count on the manifest change when Marrero's homeroom was reassigned?",
        "modes": [
            _mode_with_predicates("count_full", ["roster_table_count_support", "roster_table_member"], rows=40),
            {
                "mode": "adult_compliance",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 50,
                            "predicate": "roster_state_support",
                            "sample_rows": [{"SupportKind": "source_record_student_group_assignment"}],
                            "was_relaxed_fallback": False,
                        },
                        {
                            "status": "success",
                            "num_rows": 50,
                            "predicate": "student_in_homeroom",
                            "was_relaxed_fallback": True,
                        },
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = structural_selector(row=row, mode_labels=["count_full", "adult_compliance"])

    assert selected["selected_mode"] == "adult_compliance"
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 2.5


def test_hybrid_selector_prefers_post_change_membership_count_without_guard() -> None:
    row = {
        "id": "q_post_reassignment_count",
        "question": "How many students were in Green Group after the Day 2 reassignment?",
        "modes": [
            _mode_with_predicates("role_tasks", ["person_role", "task_assignment"], rows=31),
            _mode_with_predicates("membership_change", ["event_occurs", "group_membership"], rows=13),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["role_tasks", "membership_change"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda *, row, mode_labels: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "membership_change"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert not selected.get("specialized_guard_reason")
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 5.0


def test_post_reassignment_group_count_phrase_no_longer_has_selector_guard() -> None:
    row = {
        "id": "q_post_reassignment_guard_retired",
        "question": "How many students were in Green Group after the Day 2 reassignment?",
        "modes": [
            _mode_with_predicates("role_tasks", ["person_role", "task_assignment"], rows=31),
            _mode_with_predicates("membership_change", ["event_occurs", "group_membership"], rows=13),
        ],
    }
    labels = ["role_tasks", "membership_change"]
    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=labels),
        mode_labels=labels,
        structural_choice="role_tasks",
    )

    assert override is None


def test_structural_selector_prefers_post_change_membership_count_on_unlike_roster() -> None:
    row = {
        "id": "q_post_change_membership_count_unlike",
        "question": "How many trainees were in Cohort B following the afternoon reassignment?",
        "modes": [
            _mode_with_predicates("role_tasks", ["person_role", "task_assignment"], rows=26),
            _mode_with_predicates("membership_change", ["event_occurs", "member_of_group"], rows=6),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["role_tasks", "membership_change"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda *, row, mode_labels: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "membership_change"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 5.0


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


def test_structural_selector_prefers_packet_close_open_item_surface() -> None:
    row = {
        "id": "q026",
        "question": "How many open items are listed at packet close in §7?",
        "modes": [
            _mode_with_predicates("parallel", ["deadline_rule", "notice_id"], rows=15),
            _mode_with_predicates("cold", ["open_item_id", "open_item_status"], rows=3),
        ],
    }

    selected = structural_selector(row=row, mode_labels=["parallel", "cold"])

    assert selected["selected_mode"] == "cold"
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 6.0


def test_hybrid_selector_prefers_open_item_surface_without_guard() -> None:
    row = {
        "id": "q026",
        "question": "How many open items are listed at packet close?",
        "modes": [
            _mode_with_predicates("temporal_helper_fix", ["deadline_rule", "notice_id"], rows=15),
            _mode_with_predicates("source_record", ["open_item_id", "open_item_status"], rows=3),
        ],
    }
    fallback_calls = 0

    def fallback_selector(**_kwargs):
        nonlocal fallback_calls
        fallback_calls += 1
        return {"selected_mode": "temporal_helper_fix"}

    selected = hybrid_selector(
        row=row,
        mode_labels=["temporal_helper_fix", "source_record"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=fallback_selector,
    )

    assert fallback_calls == 0
    assert selected["selected_mode"] == "source_record"
    assert selected["hybrid_decision"] == "structural_confident"


def test_hybrid_selector_prefers_open_audit_exception_surface_without_guard() -> None:
    row = {
        "id": "q019",
        "question": "How many audit exceptions are open at packet close?",
        "modes": [
            _mode_with_predicates("parallel", ["audit_exception", "exception_status"], rows=6),
            _mode_with_predicates(
                "source_record",
                ["has_open_exception", "exception_status", "exception_nature"],
                rows=6,
            ),
        ],
    }
    fallback_calls = 0

    def fallback_selector(**_kwargs):
        nonlocal fallback_calls
        fallback_calls += 1
        return {"selected_mode": "parallel"}

    selected = hybrid_selector(
        row=row,
        mode_labels=["parallel", "source_record"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=fallback_selector,
    )

    assert fallback_calls == 0
    assert selected["selected_mode"] == "source_record"
    assert selected["hybrid_decision"] == "structural_confident"


def test_hybrid_selector_prefers_roster_version_count_summary_without_guard() -> None:
    row = {
        "id": "q019",
        "question": "Did the total distinct-student count change between roster v1.0 and v1.3?",
        "modes": [
            _mode_with_predicates("entity", ["student_in_homeroom"], rows=46),
            _mode_with_predicates("source_record", ["distinct_student_count"], rows=10, relaxed=True),
        ],
    }
    fallback_calls = 0

    def fallback_selector(**_kwargs):
        nonlocal fallback_calls
        fallback_calls += 1
        return {"selected_mode": "entity"}

    selected = hybrid_selector(
        row=row,
        mode_labels=["entity", "source_record"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=fallback_selector,
    )

    assert fallback_calls == 0
    assert selected["selected_mode"] == "source_record"
    assert selected["hybrid_decision"] == "structural_confident"


def test_structural_selector_prefers_voided_slip_source_record_facts_v2_surface() -> None:
    row = {
        "id": "q029",
        "question": "Which slip was voided during the window because no item had been received against it, and on what date?",
        "modes": [
            _mode_with_predicates("cold", ["item_status", "exception_open"], rows=9),
            _mode_with_predicates(
                "source_record_facts_v2",
                ["audit_window", "custody_status", "linked_to_slip", "source_record_text_atom"],
                rows=12,
            ),
            _mode_with_predicates("entity", ["voided_label", "effective_date_of"], rows=5),
        ],
    }

    selected = structural_selector(row=row, mode_labels=["cold", "source_record_facts_v2", "entity"])

    assert selected["selected_mode"] == "source_record_facts_v2"
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 4.0


def test_hybrid_selector_prefers_replacement_slip_direct_surface() -> None:
    row = {
        "id": "q030",
        "question": "Which slip replaced the voided slip, and for which item?",
        "modes": [
            _mode_with_predicates("source_record_facts", ["slip_number", "item_type"], rows=4),
            _mode_with_predicates("entity", ["has_label", "superseded_by", "voided_label"], rows=13),
            _mode_with_predicates("source_record", ["has_current_slip", "item_description", "voided_value"], rows=12),
        ],
    }
    fallback_calls = 0

    def fallback_selector(**_kwargs):
        nonlocal fallback_calls
        fallback_calls += 1
        return {"selected_mode": "source_record_facts"}

    selected = hybrid_selector(
        row=row,
        mode_labels=["source_record_facts", "entity", "source_record"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=fallback_selector,
    )

    assert fallback_calls == 0
    assert selected["selected_mode"] == "entity"
    assert selected["hybrid_decision"] == "structural_confident"


def test_structural_selector_prefers_active_label_count_surface() -> None:
    row = {
        "id": "q017",
        "question": "How many active labels remain in the master inventory after the withdrawals during the window are applied?",
        "modes": [
            _mode_with_predicates("parallel", ["current_exhibit_label", "withdrawn_label"], rows=15),
            _mode_with_predicates("source_record_facts", ["active_label_count", "current_label", "withdrawn_label"], rows=1),
        ],
    }

    selected = structural_selector(row=row, mode_labels=["parallel", "source_record_facts"])

    assert selected["selected_mode"] == "source_record_facts"
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 7.0


def test_application_disposition_focus_prefers_status_surface_without_guard() -> None:
    row = {
        "id": "q019",
        "question": "What is the disposition of App-2026-021?",
        "modes": [
            _mode_with_predicates("source_record_facts", [], rows=0),
            _mode_with_predicates("entity", ["determination_status", "rule_violated"], rows=2),
        ],
    }

    selected = structural_selector(row=row, mode_labels=["source_record_facts", "entity"])

    assert selected["selected_mode"] == "entity"
    assert selected.get("specialized_guard_reason", "") == ""


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

    assert override is None

    selected = hybrid_selector(
        row=row,
        mode_labels=["source_record_facts", "entity"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "entity"
    assert selected["selection_source"] == "hybrid_structural"


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

    assert override is None

    selected = hybrid_selector(
        row=row,
        mode_labels=labels,
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "alias_full"
    assert selected["selection_source"] == "hybrid_structural"


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

    assert override is None

    selected = hybrid_selector(
        row=row,
        mode_labels=["source_record_facts_v2", "entity"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "entity"
    assert selected["selection_source"] == "hybrid_structural"


def test_student_identifier_focus_prefers_canonical_member_surface_without_guard() -> None:
    row = {
        "id": "q008",
        "question": "What is the student identifier for Halpern?",
        "modes": [
            _mode_with_predicates("alias_full", ["roster_table_member_label"], rows=1),
            _mode_with_predicates(
                "count_full",
                ["roster_table_member_label", "roster_table_member", "roster_table_member_alias_support"],
                rows=2,
            ),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["alias_full", "count_full"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
        guard_disable_regex=compile_guard_disable_regex("student-identifier question"),
    )

    assert selected["selected_mode"] == "count_full"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


def test_student_identifier_focus_prefers_alias_table_surface_without_guard() -> None:
    row = {
        "id": "q009",
        "question": "What is the student identifier for Yates?",
        "modes": [
            {
                "mode": "focused_homeroom",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 39,
                            "predicate": "student_in_homeroom",
                            "was_relaxed_fallback": False,
                        },
                        {
                            "status": "success",
                            "num_rows": 129,
                            "predicate": "roster_state_support",
                            "was_relaxed_fallback": True,
                        },
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "alias_full",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 40,
                            "predicate": "roster_table_member_alias",
                            "was_relaxed_fallback": True,
                        },
                        {
                            "status": "success",
                            "num_rows": 77,
                            "predicate": "roster_table_member_label",
                            "was_relaxed_fallback": True,
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
        mode_labels=["focused_homeroom", "alias_full"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
        guard_disable_regex=compile_guard_disable_regex("student-identifier question"),
    )

    assert selected["selected_mode"] == "alias_full"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


def test_parent_sample_identifier_focus_prefers_source_or_row_value_without_guard() -> None:
    row = {
        "id": "q002",
        "question": "What is the parent sample identifier for the water sample collected at site SR-7?",
        "modes": [
            _mode_with_predicates("cold", ["sample_id"], rows=2),
            _mode_with_predicates("source_record", ["source_records"], rows=39),
            _mode_with_predicates("archival_row_ledger_v1", ["row_value"], rows=79),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
        guard_disable_regex=compile_guard_disable_regex("parent-sample identifier question"),
    )

    assert selected["selected_mode"] in {"source_record", "archival_row_ledger_v1"}
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


def test_erratum_report_of_record_keeps_archival_identifier_surface() -> None:
    row = {
        "id": "q017",
        "question": "Which report version is the report of record after an erratum?",
        "modes": [
            _mode_with_predicates("cold", ["report_version", "result_supersedes"], rows=3, relaxed=True),
            _mode_with_predicates("source_record", ["source_document_status"], rows=2),
            _mode_with_predicates("archival_row_ledger_v1", ["document_identifier", "row_value"], rows=98, relaxed=True),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "archival_row_ledger_v1"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected.get("specialized_guard_reason", "") == ""


def test_chain_of_custody_personnel_count_keeps_archival_row_surface() -> None:
    row = {
        "id": "q032",
        "question": "How many distinct named personnel are recorded in the chain-of-custody log for sample LS-PFAS-2026-0428-SR7-A?",
        "modes": [
            _mode_with_predicates("cold", ["person_role", "sample_id"], rows=6, relaxed=True),
            _mode_with_predicates(
                "source_record",
                ["assignment_interval", "source_document_author", "source_records"],
                rows=18,
                relaxed=True,
            ),
            _mode_with_predicates("archival_row_ledger_v1", ["row_actor", "row_subject", "row_participant"], rows=8),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "archival_row_ledger_v1"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert "specialized_guard_reason" not in selected


def test_packet_time_aliquot_location_prefers_archival_row_surface() -> None:
    row = {
        "id": "q020",
        "question": "As of packet time, where is aliquot B located?",
        "modes": [
            _mode_with_predicates("cold", ["sample_id", "uncertainty_status"], rows=2),
            _mode_with_predicates("source_record", ["status_at", "unresolved_issue"], rows=13, relaxed=True),
            _mode_with_predicates("archival_row_ledger_v1", ["row_event", "row_subject", "row_time", "row_value"], rows=28),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "archival_row_ledger_v1"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


def test_manual_freezer_check_prefers_archival_time_value_actor_surface() -> None:
    row = {
        "id": "q021",
        "question": "As of May 4 at 11:30, what was freezer F-3's temperature according to the manual check, and who performed it?",
        "modes": [
            _mode_with_predicates("cold", ["analyte_result", "person_role", "uncertainty_status"], rows=8, relaxed=True),
            _mode_with_predicates("source_record", ["event_attribute", "status_at"], rows=47),
            _mode_with_predicates(
                "archival_row_ledger_v1",
                ["record_row", "row_actor", "row_time", "row_value"],
                rows=38,
                relaxed=True,
            ),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "archival_row_ledger_v1"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


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

    assert override is None

    selected = hybrid_selector(
        row=row,
        mode_labels=labels,
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "narrow_guidance"
    assert selected["selection_source"] == "hybrid_structural"


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

    assert override is None

    selected = hybrid_selector(
        row=row,
        mode_labels=labels,
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "count_full"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected.get("specialized_guard_reason", "") == ""


def test_roster_ratio_compliance_skips_relaxed_compliance_status_surface() -> None:
    row = {
        "id": "q033",
        "question": "Under Â§3.2, was roster v1.0 compliant with the chaperone-to-student ratio?",
        "modes": [
            {
                "mode": "parallel",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "roster_version",
                            "was_relaxed_fallback": False,
                        },
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "compliance_status",
                            "was_relaxed_fallback": True,
                        },
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            _mode_with_predicates("entity", ["compliance_status"], rows=1),
        ],
    }

    labels = ["parallel", "entity"]
    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=labels),
        mode_labels=labels,
        structural_choice="parallel",
    )

    assert override is None

    selected = hybrid_selector(
        row=row,
        mode_labels=labels,
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "entity"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected.get("specialized_guard_reason", "") == ""


def test_structural_selector_prefers_chaperone_roster_adult_count_value() -> None:
    row = {
        "id": "q028",
        "question": "Per the chaperone roster of record on the day of the trip, how many adults were on the trip?",
        "modes": [
            _mode_with_predicates("cold", ["person_role", "assigned_to"], rows=22, relaxed=True),
            _mode_with_predicates("source_record", ["count_value"], rows=1),
        ],
    }

    selected = structural_selector(row=row, mode_labels=["cold", "source_record"])

    assert selected["selected_mode"] == "source_record"
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 9.0


def test_hybrid_selector_trusts_chaperone_roster_adult_count_value_when_membership_guard_applies() -> None:
    row = {
        "id": "q028",
        "question": "Per the chaperone roster of record on the day of the trip, how many adults were on the trip?",
        "modes": [
            _mode_with_predicates("cold", ["person_role", "assigned_to"], rows=22, relaxed=True),
            _mode_with_predicates("source_record", ["count_value"], rows=1),
        ],
    }
    fallback_calls = 0

    def fallback_selector(**_kwargs):
        nonlocal fallback_calls
        fallback_calls += 1
        return {"selected_mode": "cold"}

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=fallback_selector,
    )

    assert fallback_calls == 0
    assert selected["selected_mode"] == "source_record"
    assert selected["hybrid_decision"] == "structural_confident"


def test_structural_selector_prefers_adult_total_roster_state_count_support() -> None:
    row = {
        "id": "q018",
        "question": "How many adults total are accompanying the trip in v1.3?",
        "modes": [
            _mode_with_predicates("focused_homeroom", ["chaperone_added", "roster_state_support"], rows=6),
            {
                "mode": "adult_compliance",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 6,
                            "predicate": "roster_state_support",
                            "sample_rows": [{"SupportKind": "compliance_status"}],
                            "was_relaxed_fallback": False,
                        }
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = structural_selector(row=row, mode_labels=["focused_homeroom", "adult_compliance"])

    assert selected["selected_mode"] == "adult_compliance"
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 2.5


def test_hybrid_selector_prefers_adult_manifest_total_without_guard() -> None:
    row = {
        "id": "q_adult_total_general",
        "question": "How many adults total are accompanying the trip?",
        "modes": [
            _mode_with_predicates("qualifying_chaperones", ["qualifying_chaperone_count"], rows=1),
            {
                "mode": "adult_manifest",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "roster_state_support",
                            "sample_rows": [{"SupportKind": "adult_manifest_total"}],
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
        mode_labels=["qualifying_chaperones", "adult_manifest"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "adult_manifest"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 4.0


def test_adult_total_roster_phrase_no_longer_has_selector_guard() -> None:
    row = {
        "id": "q_adult_total_retired_guard",
        "question": "How many adults total are accompanying the trip?",
        "modes": [
            _mode_with_predicates("qualifying_chaperones", ["qualifying_chaperone_count"], rows=1),
            {
                "mode": "adult_manifest",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "roster_state_support",
                            "sample_rows": [{"SupportKind": "adult_manifest_total"}],
                            "was_relaxed_fallback": False,
                        }
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }
    labels = ["qualifying_chaperones", "adult_manifest"]
    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=labels),
        mode_labels=labels,
        structural_choice="qualifying_chaperones",
    )

    assert override is None


def test_structural_selector_prefers_total_count_over_unasked_subset_count() -> None:
    row = {
        "id": "q_total_subset_general",
        "question": "How many total applications were submitted?",
        "modes": [
            _mode_with_predicates("approved_subset", ["approved_application_count"], rows=1),
            _mode_with_predicates("all_applications", ["application_total_count"], rows=1),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["approved_subset", "all_applications"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "all_applications"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 6.0


def test_structural_selector_allows_subset_count_when_subset_is_requested() -> None:
    row = {
        "id": "q_requested_subset_general",
        "question": "How many approved applications total were submitted?",
        "modes": [
            _mode_with_predicates("approved_subset", ["approved_application_count"], rows=1),
            _mode_with_predicates("all_applications", ["application_total_count"], rows=1),
        ],
    }

    selected = structural_selector(row=row, mode_labels=["approved_subset", "all_applications"])

    assert selected["selected_mode"] == "approved_subset"
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 6.0


def test_structural_selector_prefers_ratio_exclusion_role_policy_surface() -> None:
    row = {
        "id": "q031",
        "question": "Which person on the trip roster is excluded from the §3.2 chaperone-to-student ratio under §3.4?",
        "modes": [
            _mode_with_predicates("alias_full", ["adult_role", "roster_state_support"], rows=30, relaxed=True),
            _mode_with_predicates("narrow_guidance", ["role", "policy_section"], rows=5),
        ],
    }

    selected = structural_selector(row=row, mode_labels=["alias_full", "narrow_guidance"])

    assert selected["selected_mode"] == "narrow_guidance"
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 4.0


def test_structural_selector_prefers_ratio_exclusion_role_exclusion_policy_surface() -> None:
    row = {
        "id": "q031",
        "question": "Which person on the trip roster is excluded from the §3.2 chaperone-to-student ratio under §3.4?",
        "modes": [
            _mode_with_predicates("alias_full", ["adult_role", "roster_state_support"], rows=30, relaxed=True),
            _mode_with_predicates("old_v2", ["role_exclusion", "policy_section"], rows=1),
        ],
    }

    selected = structural_selector(row=row, mode_labels=["alias_full", "old_v2"])

    assert selected["selected_mode"] == "old_v2"
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 6.0


def retired_roster_adult_total_prefers_role_surface_over_chaperone_count() -> None:
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

    assert override is None

    selected = hybrid_selector(
        row=row,
        mode_labels=["source_record_facts", "cold"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "cold"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected.get("specialized_guard_reason", "") == ""


def test_application_count_prefers_canonical_status_surface() -> None:
    row = {
        "id": "q027",
        "question": "How many applications are approved?",
        "modes": [
            _mode_with_predicates("source_record", ["determination_status"], rows=3),
            _mode_with_predicates("cold", ["application_status"], rows=2),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["source_record", "cold"],
        margin=1.0,
        min_score=4.0,
        guard_disable_regex=compile_guard_disable_regex("application-count question"),
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "cold"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected.get("specialized_guard_reason", "") == ""


def test_tree_amendment_count_prefers_direct_count_value_without_guard() -> None:
    row = {
        "id": "q031",
        "question": "Under the amendment, how many trees are approved for removal?",
        "modes": [
            _mode_with_predicates(
                "cold",
                ["determination_pending", "permit_issued", "permit_issued_amendment", "tree_protected_status"],
                rows=6,
            ),
            _mode_with_predicates("source_record", ["count_value"], rows=2),
            _mode_with_predicates("archival_row_ledger_v1", ["row_value"], rows=2),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        guard_disable_regex=compile_guard_disable_regex("tree-list/count question"),
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "source_record"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected.get("specialized_guard_reason", "") == ""


def test_tree_amendment_id_list_prefers_direct_count_surface_without_guard() -> None:
    row = {
        "id": "q032",
        "question": "List all protected tree IDs after the amendment.",
        "modes": [
            _mode_with_predicates(
                "cold",
                ["permit_issued_amendment", "tree_protected_status", "tree_reclassified"],
                rows=3,
            ),
            _mode_with_predicates("source_record", ["count_value"], rows=2),
            _mode_with_predicates("archival_row_ledger_v1", ["row_value"], rows=32, relaxed=True),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        guard_disable_regex=compile_guard_disable_regex("tree-list/count question"),
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "source_record"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected.get("specialized_guard_reason", "") == ""


def test_headcount_scan_reconciliation_prefers_direct_paired_evidence_without_guard() -> None:
    row = {
        "id": "q040",
        "question": (
            "The Bus 2 driver's manual count at 2:35 PM was 40, indicating one student short. "
            "The wristband scan log places Lila Marchetti at Mill Station entry at 2:35 PM. "
            "How are these two records reconciled?"
        ),
        "modes": [
            _mode_with_predicates(
                "cold",
                ["wristband_scan", "headcount_recorded", "count_discrepancy", "incident_location"],
                rows=1,
            ),
            _mode_with_predicates(
                "source_record",
                ["count_value", "statement_claim", "event_attribute"],
                rows=18,
                relaxed=True,
            ),
            _mode_with_predicates(
                "archival_row_ledger_v1",
                ["row_value", "row_subject", "row_event", "row_time"],
                rows=41,
            ),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        guard_disable_regex=compile_guard_disable_regex("headcount-scan reconciliation question"),
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "cold"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected.get("specialized_guard_reason", "") == ""


def test_medication_lot_number_prefers_source_record_event_attributes_without_guard() -> None:
    row = {
        "id": "q003",
        "question": "What is the lot number of the heparin bag hung at 13:44?",
        "modes": [
            _mode_with_predicates("cold", ["system_log_entry"], rows=12, relaxed=True),
            _mode_with_predicates("source_record", ["log_event", "event_attribute"], rows=29, relaxed=True),
            _mode_with_predicates("archival_row_ledger_v1", ["row_time", "row_value"], rows=71, relaxed=True),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        guard_disable_regex=compile_guard_disable_regex("medication lot-number question"),
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "source_record"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected.get("specialized_guard_reason", "") == ""


def test_alarm_acknowledger_prefers_source_record_statement_and_event_attribute() -> None:
    row = {
        "id": "q023",
        "question": "At 14:42, who acknowledged the alarm at the central station per the telemetry log?",
        "modes": [
            _mode_with_predicates("cold", ["alarm_event"], rows=1),
            _mode_with_predicates("source_record", ["statement_claim", "event_attribute"], rows=2),
            _mode_with_predicates("archival_row_ledger_v1", ["row_value", "row_actor"], rows=33),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "source_record"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


def test_credential_question_prefers_direct_credential_status_without_guard() -> None:
    row = {
        "id": "q029",
        "question": "Was Tilling credentialed to work the cardiac step-down telemetry unit?",
        "modes": [
            _mode_with_predicates("cold", ["badge_access", "system_log_entry", "policy_requirement"], rows=12),
            _mode_with_predicates("source_record", ["credential_status"], rows=1),
            _mode_with_predicates(
                "archival_row_ledger_v1",
                ["row_actor", "row_value", "row_location", "row_event"],
                rows=51,
            ),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        guard_disable_regex=compile_guard_disable_regex("credential question"),
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "source_record"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected.get("specialized_guard_reason", "") == ""


def test_policy_deviation_question_prefers_open_issue_status_without_guard() -> None:
    row = {
        "id": "q036",
        "question": (
            "Has it been determined whether Tilling's 14:42 alarm acknowledgment without "
            "bedside response constitutes a policy deviation?"
        ),
        "modes": [
            _mode_with_predicates("cold", ["alarm_event", "open_question", "review_status"], rows=3),
            _mode_with_predicates(
                "source_record",
                ["unresolved_issue", "statement_claim", "negative_record", "rule_requirement"],
                rows=49,
            ),
            _mode_with_predicates(
                "archival_row_ledger_v1",
                ["row_value", "row_actor", "row_time", "row_event"],
                rows=20,
            ),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        guard_disable_regex=compile_guard_disable_regex("unresolved policy-deviation question"),
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "source_record"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected.get("specialized_guard_reason", "") == ""


def test_override_rule_requirement_prefers_source_record_rule_surface_without_guard() -> None:
    row = {
        "id": "q026",
        "question": (
            "Per Pyxis Override Rule R-OV-2, what must occur within 60 seconds of an "
            "override withdrawal of a high-alert anticoagulant?"
        ),
        "modes": [
            _mode_with_predicates("cold", ["policy_requirement"], rows=4, relaxed=True),
            _mode_with_predicates("source_record", ["rule_requirement", "event_attribute"], rows=13, relaxed=True),
            _mode_with_predicates("archival_row_ledger_v1", ["row_value"], rows=4),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        guard_disable_regex=compile_guard_disable_regex("override-rule requirement question"),
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "source_record"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected.get("specialized_guard_reason", "") == ""


def test_project_pi_identity_prefers_assignment_surface_without_guard() -> None:
    row = {
        "id": "q001",
        "question": "Who is the project PI on the Lower Sammish River PFAS Monitoring Study?",
        "modes": [
            _mode_with_predicates("cold", ["person_role"], rows=1),
            _mode_with_predicates("source_record", ["assignment_interval", "source_records"], rows=39),
            _mode_with_predicates("archival_row_ledger_v1", ["document_identifier", "row_actor", "row_value"], rows=103),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        guard_disable_regex=compile_guard_disable_regex("project-PI identity question"),
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "source_record"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected.get("specialized_guard_reason", "") == ""


def test_applicant_identity_prefers_source_author_without_guard() -> None:
    row = {
        "id": "q002",
        "question": "Who is the applicant?",
        "modes": [
            _mode_with_predicates("cold", ["event_occurred", "person_role"], rows=2),
            _mode_with_predicates("source_record", ["source_document_author"], rows=20),
            _mode_with_predicates("archival_row_ledger_v1", ["row_actor"], rows=17),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        guard_disable_regex=compile_guard_disable_regex("applicant identity question"),
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "source_record"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected.get("specialized_guard_reason", "") == ""


def test_original_permit_number_prefers_identifier_surface() -> None:
    row = {
        "id": "q004",
        "question": "What is the original permit number?",
        "modes": [
            _mode_with_predicates("cold", ["permit_issued"], rows=1, relaxed=True),
            _mode_with_predicates("source_record", ["supersession"], rows=2, relaxed=True),
            _mode_with_predicates("archival_row_ledger_v1", ["document_identifier"], rows=7, relaxed=True),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "archival_row_ledger_v1"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


def test_authority_source_identity_prefers_issue_status_authority_without_guard() -> None:
    row = {
        "id": "q029",
        "question": "As of packet time, who currently holds authority to determine ownership status of the wreck?",
        "modes": [
            _mode_with_predicates(
                "cold",
                ["court_order", "ownership_of_record", "asserts_ownership", "asserts_subrogation"],
                rows=5,
            ),
            _mode_with_predicates(
                "source_record",
                ["unresolved_issue", "status_at", "source_document_author"],
                rows=3,
            ),
            _mode_with_predicates("archival_row_ledger_v1", ["row_value"], rows=3),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        guard_disable_regex=compile_guard_disable_regex("authority/source identity question needs issue-status"),
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "source_record"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected.get("specialized_guard_reason", "") == ""


def test_named_judicial_actor_prefers_direct_person_role_without_guard() -> None:
    row = {
        "id": "q005",
        "question": "Who is the assigned Federal Magistrate Judge?",
        "modes": [
            _mode_with_predicates("cold", ["person_role"], rows=1),
            _mode_with_predicates("source_record", ["source_document_author", "unresolved_issue"], rows=3),
            _mode_with_predicates("archival_row_ledger_v1", ["row_actor", "row_event", "row_value"], rows=118),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        guard_disable_regex=compile_guard_disable_regex("authority/source identity question needs the surface carrying the named judicial actor"),
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "cold"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected.get("specialized_guard_reason", "") == ""


def test_named_note_actor_prefers_archival_bench_note_row_value_without_guard() -> None:
    row = {
        "id": "q010",
        "question": "According to whose bench notes is Aragon's Artistic Merit score 38?",
        "modes": [
            _mode_with_predicates("cold", ["score_correction", "person_role"], rows=7, relaxed=True),
            _mode_with_predicates("source_record", ["measurement_value", "source_document_author"], rows=6, relaxed=True),
            _mode_with_predicates("archival_row_ledger_v1", ["row_value"], rows=91),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        guard_disable_regex=compile_guard_disable_regex("authority/source identity question needs the surface carrying the named note actor"),
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "archival_row_ledger_v1"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected.get("specialized_guard_reason", "") == ""


def test_position_source_prefers_statement_author_surface_without_guard() -> None:
    row = {
        "id": "q009",
        "question": "Which source recorded the wreck's Position A?",
        "modes": [
            _mode_with_predicates("cold", ["survey_position", "documented_in"], rows=18),
            _mode_with_predicates("source_record", ["statement_claim", "source_document_author"], rows=17),
            _mode_with_predicates("archival_row_ledger_v1", ["row_value", "record_row", "source_section"], rows=41, relaxed=True),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        guard_disable_regex=compile_guard_disable_regex("position-source question needs statement/source-author surface"),
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "source_record"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected.get("specialized_guard_reason", "") == ""


def test_current_withdrawn_claim_prefers_statement_supersession_status_without_guard() -> None:
    row = {
        "id": "q017",
        "question": "What is the salvor's current operative claim, and what was the withdrawn earlier position?",
        "modes": [
            _mode_with_predicates("cold", ["claims_salvage", "event_withdrawn"], rows=5),
            {
                "mode": "source_record",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "statement_claim",
                            "was_relaxed_fallback": False,
                        },
                        {
                            "status": "success",
                            "num_rows": 32,
                            "predicate": "status_at",
                            "was_relaxed_fallback": True,
                        },
                        {
                            "status": "success",
                            "num_rows": 4,
                            "predicate": "supersession",
                            "was_relaxed_fallback": True,
                        },
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            _mode_with_predicates("archival_row_ledger_v1", ["row_value"], rows=103, relaxed=True),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        guard_disable_regex=compile_guard_disable_regex("current-versus-withdrawn claim question"),
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "source_record"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected.get("specialized_guard_reason", "") == ""


def test_position_b_source_prefers_archival_location_source_surface() -> None:
    row = {
        "id": "q010",
        "question": "Which source recorded the wreck's Position B?",
        "modes": [
            _mode_with_predicates("cold", ["survey_position", "documented_in"], rows=18),
            _mode_with_predicates("source_record", ["measurement_value", "source_document_author"], rows=10, relaxed=True),
            {
                "mode": "archival_row_ledger_v1",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 2,
                            "predicate": "row_location",
                            "was_relaxed_fallback": False,
                        },
                        {
                            "status": "success",
                            "num_rows": 22,
                            "predicate": "record_row",
                            "was_relaxed_fallback": True,
                        },
                        {
                            "status": "success",
                            "num_rows": 4,
                            "predicate": "source_section_label",
                            "was_relaxed_fallback": True,
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
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "archival_row_ledger_v1"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


def test_magistrate_salvage_award_prefers_source_record_memo_surface() -> None:
    row = {
        "id": "q024",
        "question": "As of April 28, 2026, what determination did the Magistrate Judge issue regarding the salvage award?",
        "modes": [
            _mode_with_predicates("cold", ["court_order", "person_role"], rows=3),
            _mode_with_predicates(
                "source_record",
                ["source_document_author", "source_document_date", "source_records"],
                rows=15,
            ),
            _mode_with_predicates("archival_row_ledger_v1", ["row_value"], rows=103, relaxed=True),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "source_record"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


def test_date_event_anchors_prefers_log_event_surface_over_incomplete_direct_events() -> None:
    row = {
        "id": "q033",
        "question": "List the date-event anchors that occurred on April 5, April 6, and April 7, 2026.",
        "modes": [
            _mode_with_predicates("cold", ["event_occurred"], rows=18),
            _mode_with_predicates("source_record", ["log_event"], rows=28, relaxed=True),
            _mode_with_predicates("archival_row_ledger_v1", ["row_time"], rows=8, relaxed=True),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "source_record"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


def test_hybrid_selector_prefers_incident_anchor_surface_without_guard() -> None:
    row = {
        "id": "q_date_event_anchor_direct",
        "question": "List the date-event anchors for the incident sequence.",
        "modes": [
            _mode_with_predicates("source_sections", ["source_record_section"], rows=9),
            _mode_with_predicates("incident_anchor", ["incident_anchor"], rows=3),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["source_sections", "incident_anchor"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "incident_anchor"
    assert selected.get("specialized_guard_reason", "") == ""


def test_hybrid_selector_prefers_denial_reason_rule_context() -> None:
    row = {
        "id": "q025",
        "question": "Why is App-2026-042 (Kintaro Sushi) denied?",
        "modes": [
            _mode_with_predicates(
                "source_record_facts_v2",
                ["determination_status", "denial_ground", "rule_threshold", "applicant_attribute"],
                rows=4,
            ),
            _mode_with_predicates(
                "source_record",
                ["determination_status", "determination_reason", "rule_description", "rule_threshold", "rule_exception"],
                rows=8,
            ),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["source_record_facts_v2", "source_record"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "source_record"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


def test_hybrid_selector_prefers_unresolved_status_bundle() -> None:
    row = {
        "id": "q035",
        "question": "What specifically is unresolved about App-2026-019?",
        "modes": [
            _mode_with_predicates(
                "source_record_facts_v2",
                ["verification_pending", "verification_deadline", "external_record_requested"],
                rows=3,
            ),
            _mode_with_predicates(
                "parallel",
                ["final_status", "eligibility_determination", "pending_verification", "applicant_attribute"],
                rows=4,
            ),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["source_record_facts_v2", "parallel"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "parallel"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


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

    assert override is None

    selected = hybrid_selector(
        row=row,
        mode_labels=["parallel", "cold"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )
    assert selected["selected_mode"] == "cold"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected.get("specialized_guard_reason", "") == ""


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

    assert override is None

    selected = hybrid_selector(
        row=row,
        mode_labels=["parallel", "source_record"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "source_record"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected.get("specialized_guard_reason", "") == ""


def test_trip_date_guard_prefers_roster_state_surface() -> None:
    row = {
        "id": "q002",
        "question": "On what date is the trip scheduled?",
        "modes": [
            _mode_with_predicates("source_record", ["roster_version"], rows=4),
            _mode_with_predicates("memory_ledger_combo", ["roster_state"], rows=1),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["source_record", "memory_ledger_combo"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "source_record"},
    )

    assert selected["selected_mode"] == "memory_ledger_combo"
    assert selected.get("specialized_guard_reason", "") == ""


def test_hybrid_selector_prefers_homeroom_reassignment_surface_without_guard() -> None:
    row = {
        "id": "q_homeroom_reassigned",
        "question": "Which student was reassigned by the homeroom correction notice?",
        "modes": [
            _mode_with_predicates("change_text", ["change_type", "correction_action"], rows=8),
            _mode_with_predicates("reassignment", ["homeroom_reassigned"], rows=1),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["change_text", "reassignment"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "reassignment"
    assert selected.get("specialized_guard_reason", "") == ""


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

    assert override is None

    selected = hybrid_selector(
        row=row,
        mode_labels=["parallel", "source_record"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )
    assert selected["selected_mode"] == "source_record"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected.get("specialized_guard_reason", "") == ""


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

    assert override is None

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "parallel"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "parallel"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected.get("specialized_guard_reason", "") == ""


def test_hybrid_selector_prefers_direct_state_custody_surfaces_without_guards() -> None:
    cases = [
        (
            "where_as_of",
            "As of the incident date, where was the artifact physically located?",
            _mode_with_predicates("broad", ["location_claim", "source_note"], rows=12),
            _mode_with_predicates("focused", ["row_location", "row_time"], rows=1),
        ),
        (
            "current_component",
            "What thread is currently in the instrument?",
            _mode_with_predicates("broad", ["transition_event", "maintenance_note"], rows=12),
            _mode_with_predicates("focused", ["current_state", "contained_thread"], rows=1),
        ),
        (
            "why_have",
            "Why does the archive have the item?",
            _mode_with_predicates("broad", ["object_property", "action_note"], rows=12),
            _mode_with_predicates("focused", ["custody_transfer", "custody_reason"], rows=1),
        ),
        (
            "carry",
            "Who carried the object during the inspection?",
            _mode_with_predicates("broad", ["legal_title_holder", "event_occurs"], rows=12),
            _mode_with_predicates("focused", ["possesses"], rows=1),
        ),
        (
            "spatial_location",
            "Which two features were on the disputed strip?",
            _mode_with_predicates("broad", ["finding_record", "survey_record"], rows=12),
            _mode_with_predicates("focused", ["object_location", "spatial_relation_to_boundary"], rows=1),
        ),
        (
            "asset_pickup",
            "Which asset in the client ledger was picked up?",
            _mode_with_predicates("broad", ["item_provenance", "ledger_entry"], rows=12),
            _mode_with_predicates("focused", ["asset_location_at", "current_asset_state"], rows=1),
        ),
    ]

    for row_id, question, broad_mode, focused_mode in cases:
        row = {
            "id": row_id,
            "question": question,
            "modes": [broad_mode, focused_mode],
        }

        selected = hybrid_selector(
            row=row,
            mode_labels=["broad", "focused"],
            margin=1.0,
            min_score=4.0,
            fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
        )

        assert selected["selected_mode"] == "focused", row_id
        assert selected["selection_source"] == "hybrid_structural", row_id
        assert selected["hybrid_decision"] == "structural_confident", row_id
        assert selected.get("specialized_guard_reason", "") == "", row_id


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
    assert selected.get("baseline_guard_reason", "") == ""
    assert selected.get("specialized_guard_reason", "") == ""


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
    assert selected.get("baseline_guard_reason", "") == ""
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 8.0


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
    assert selected.get("baseline_guard_reason", "") == ""
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 8.0


def test_hybrid_selector_prefers_compact_operational_status_surfaces_without_guards() -> None:
    cases = [
        (
            "response_content",
            "What did the filed response include?",
            [
                _mode_with_predicates("compact_response", ["event_actor", "event_type", "rule_condition"], rows=1),
                _mode_with_predicates("broad_procedure", ["event_filed", "event_issued"], rows=15),
            ],
            ["compact_response", "broad_procedure"],
            "compact_response",
            "response-content question",
        ),
        (
            "contract_rescission",
            "Was the contract rescinded after the request?",
            [
                _mode_with_predicates(
                    "request_outcome",
                    ["validity_question_raised", "notification_sent", "event_outcome", "contract_value"],
                    rows=1,
                ),
                _mode_with_predicates("vote_volume", ["meeting_item", "vote_result"], rows=8),
            ],
            ["request_outcome", "vote_volume"],
            "request_outcome",
            "contract-rescission status",
        ),
        (
            "court_status",
            "Has the court issued a determination on the disputed questions?",
            [
                _mode_with_predicates("broad_unresolved", ["unresolved_issue"], rows=40, relaxed=True),
                _mode_with_predicates("source_status", ["source_document_status", "negative_record"], rows=2),
                _mode_with_predicates("archival_status", ["record_row", "row_value"], rows=3),
            ],
            ["broad_unresolved", "source_status", "archival_status"],
            {"source_status", "archival_status"},
            "court-determination question",
        ),
        (
            "resolved_status",
            "Has the completed inter vivos gift question been resolved or determined?",
            [
                _mode_with_predicates("broad_rows", ["row_value"], rows=40),
                _mode_with_predicates("status_surface", ["disputed_ownership", "is_unresolved"], rows=2),
            ],
            ["broad_rows", "status_surface"],
            "status_surface",
            "resolved-status question",
        ),
        (
            "planning_request",
            "What is the applicant requesting and what is the request type?",
            [
                _mode_with_predicates("claim_volume", ["claim_status"], rows=20),
                _mode_with_predicates("request_summary", ["application_summary", "project_unit_mix"], rows=2),
            ],
            ["claim_volume", "request_summary"],
            "request_summary",
            "planning-application request",
        ),
        (
            "prior_proposal",
            "Was the 18-unit proposal denied or rejected?",
            [
                _mode_with_predicates("current_status", ["application_status"], rows=20),
                _mode_with_predicates("proposal_record", ["proposal_version", "staff_finding"], rows=2),
            ],
            ["current_status", "proposal_record"],
            "proposal_record",
            "prior-proposal disposition",
        ),
    ]

    for row_id, question, modes, labels, expected_mode, disabled_guard in cases:
        selected = hybrid_selector(
            row={"id": row_id, "question": question, "modes": modes},
            mode_labels=labels,
            margin=1.0,
            min_score=4.0,
            guard_disable_regex=compile_guard_disable_regex(disabled_guard),
            fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
        )

        if isinstance(expected_mode, set):
            assert selected["selected_mode"] in expected_mode
        else:
            assert selected["selected_mode"] == expected_mode
        assert selected["selection_source"] == "hybrid_structural"
        assert selected["hybrid_decision"] == "structural_confident"
        assert selected.get("baseline_guard_reason", "") == ""
        assert selected.get("specialized_guard_reason", "") == ""


def test_hybrid_selector_prefers_rule_binding_surfaces_without_guards() -> None:
    cases = [
        (
            "rescission",
            "Could the board request rescission if two members voted against it?",
            _mode_with_predicates("rule_volume", ["governance_rule", "meeting_item"], rows=8),
            _mode_with_predicates("request_validity", ["validity_question_raised", "notification_sent", "vote_cast"], rows=1),
            "request_validity",
            "rescission-request",
        ),
        (
            "revised_plan",
            "Why was the revised plan monitoring frequency rejected?",
            _mode_with_predicates("status_volume", ["observation_status"], rows=15),
            _mode_with_predicates("rule_event", ["event_reason", "rule_text", "event_issued"], rows=1),
            "rule_event",
            "revised-plan",
        ),
        (
            "deferment",
            "Why was the application deferred?",
            _mode_with_predicates("rule_text", ["rule_text"], rows=15),
            _mode_with_predicates(
                "interpreted_decision",
                ["vote_result", "recusal_member", "eligibility_determination", "interpretation_text"],
                rows=1,
            ),
            "interpreted_decision",
            "deferment-rationale",
        ),
        (
            "component_problem",
            "Which component problem triggers the rule?",
            _mode_with_predicates("category_rule", ["project_category", "rule_condition"], rows=1),
            _mode_with_predicates("component_volume", ["component_status"], rows=15),
            "category_rule",
            "component-problem",
        ),
        (
            "recusal",
            "Why did the member recuse?",
            _mode_with_predicates("eligibility", ["eligibility_determination"], rows=15),
            _mode_with_predicates("recusal_rule", ["recusal_member", "vote_result", "rule_text"], rows=1),
            "recusal_rule",
            "recusal-rationale",
        ),
        (
            "post_recusal",
            "Why couldn't the recused member vote?",
            _mode_with_predicates("quorum", ["quorum_status", "vote_result"], rows=15),
            _mode_with_predicates("recusal_vote", ["recusal_member", "vote_result", "rule_text"], rows=1),
            "recusal_vote",
            "post-recusal",
        ),
        (
            "window_merit_condition",
            "Does the 3-year window argument have merit?",
            _mode_with_predicates("applicant_volume", ["applicant_id", "prior_grant_history"], rows=15),
            _mode_with_predicates("history_rule", ["prior_grant_history", "interpretation_text", "rule_condition"], rows=1),
            "history_rule",
            "window-merit",
        ),
        (
            "window_merit_interpretation",
            "Does the three-year window argument have merit?",
            _mode_with_predicates("applicant_volume", ["applicant_id", "prior_grant_history"], rows=15),
            _mode_with_predicates(
                "history_interpretation",
                ["prior_grant_history", "interpretation_text", "rule_interpreted"],
                rows=1,
            ),
            "history_interpretation",
            "window-merit",
        ),
        (
            "rejection_cause",
            "Was the application rejected on the merits because of absences?",
            _mode_with_predicates("derived_status", ["derived_status"], rows=15),
            _mode_with_predicates("record_correction", ["correction_to_record", "clarification_of_record"], rows=1),
            "record_correction",
            "rejection-cause",
        ),
        (
            "appeal_hearing",
            "Has the appeal hearing been heard?",
            _mode_with_predicates("appeal_status", ["appeal_status"], rows=15),
            _mode_with_predicates("hearing_event", ["appeal_filed", "appeal_hearing_scheduled"], rows=1),
            "hearing_event",
            "appeal-hearing",
        ),
        (
            "permitted_hours",
            "What are the permitted sound hours for amplified sound?",
            _mode_with_predicates("permit_status", ["permit_status"], rows=15),
            _mode_with_predicates("hours_rule", ["operational_hours"], rows=1),
            "hours_rule",
            "permitted-hours",
        ),
    ]

    for row_id, question, broad_mode, focused_mode, expected_mode, disabled_guard in cases:
        selected = hybrid_selector(
            row={"id": row_id, "question": question, "modes": [broad_mode, focused_mode]},
            mode_labels=[broad_mode["mode"], focused_mode["mode"]],
            margin=1.0,
            min_score=4.0,
            guard_disable_regex=compile_guard_disable_regex(disabled_guard),
            fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
        )

        assert selected["selected_mode"] == expected_mode, row_id
        assert selected["selection_source"] == "hybrid_structural", row_id
        assert selected["hybrid_decision"] == "structural_confident", row_id
        assert selected.get("baseline_guard_reason", "") == "", row_id
        assert selected.get("specialized_guard_reason", "") == "", row_id


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
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected.get("baseline_guard_reason", "") == ""
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 6.0


def test_hybrid_selector_keeps_reserve_arithmetic_inputs_without_guard() -> None:
    row = {
        "id": "q_reserve_counterfactual",
        "question": "If the amendment had passed and the emergency spending occurred, what would the reserve status be?",
        "modes": [
            _mode_with_predicates(
                "derived_status",
                ["derived_status", "rule_status", "status_at"],
                rows=12,
            ),
            _mode_with_predicates(
                "arithmetic_inputs",
                ["reserve_balance", "minimum_reserve_policy", "expenditure_authorized"],
                rows=3,
            ),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["derived_status", "arithmetic_inputs"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda *, row, mode_labels: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "arithmetic_inputs"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert not selected.get("specialized_guard_reason")
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 6.0


def test_reserve_status_phrase_no_longer_has_selector_guard() -> None:
    row = {
        "id": "q_reserve_counterfactual_guard_retired",
        "question": "If the amendment had passed and the emergency spending occurred, what would the reserve status be?",
        "modes": [
            _mode_with_predicates(
                "derived_status",
                ["derived_status", "rule_status", "status_at"],
                rows=12,
            ),
            _mode_with_predicates(
                "arithmetic_inputs",
                ["reserve_balance", "minimum_reserve_policy", "expenditure_authorized"],
                rows=3,
            ),
        ],
    }
    labels = ["derived_status", "arithmetic_inputs"]

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=labels),
        mode_labels=labels,
        structural_choice="derived_status",
    )

    assert override is None


def test_structural_selector_prefers_arithmetic_inputs_on_unlike_counterfactual_status() -> None:
    row = {
        "id": "q_unlike_counterfactual_arithmetic_inputs",
        "question": "If the facility upgrade were authorized, what would happen to the compliance status?",
        "modes": [
            _mode_with_predicates("derived_status", ["derived_status", "status_at"], rows=15),
            _mode_with_predicates(
                "arithmetic_inputs",
                ["reserve_balance", "minimum_reserve_policy", "expenditure_authorized"],
                rows=4,
            ),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["derived_status", "arithmetic_inputs"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda *, row, mode_labels: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "arithmetic_inputs"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 6.0


def test_hybrid_selector_prefers_recall_authority_surface_without_guard() -> None:
    row = {
        "id": "q_recall_authority",
        "question": "Could the Council recall BA-2026-08 after the emergency to restore the reserve?",
        "modes": [
            _mode_with_predicates("legal_opinion", ["charter_rule", "voting_threshold", "legal_opinion"], rows=9),
            _mode_with_predicates(
                "recall_authority",
                ["charter_rule", "voting_threshold", "reserve_balance", "emergency_declared"],
                rows=4,
            ),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["legal_opinion", "recall_authority"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda *, row, mode_labels: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "recall_authority"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert not selected.get("specialized_guard_reason")
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 6.5


def test_amendment_recall_phrase_no_longer_has_selector_guard() -> None:
    row = {
        "id": "q_recall_authority_guard_retired",
        "question": "Could the Council recall BA-2026-08 after the emergency to restore the reserve?",
        "modes": [
            _mode_with_predicates("legal_opinion", ["charter_rule", "voting_threshold", "legal_opinion"], rows=9),
            _mode_with_predicates(
                "recall_authority",
                ["charter_rule", "voting_threshold", "reserve_balance", "emergency_declared"],
                rows=4,
            ),
        ],
    }
    labels = ["legal_opinion", "recall_authority"]

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=labels),
        mode_labels=labels,
        structural_choice="legal_opinion",
    )

    assert override is None


def test_structural_selector_prefers_authority_action_surface_on_unlike_reversal() -> None:
    row = {
        "id": "q_unlike_authority_action",
        "question": "What is required to reverse the access decision after emergency action?",
        "modes": [
            _mode_with_predicates("legal_opinion", ["policy_rule", "rule_threshold", "legal_opinion"], rows=11),
            _mode_with_predicates(
                "action_authority",
                ["policy_rule", "rule_threshold", "event_reverses", "governance_decision"],
                rows=3,
            ),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["legal_opinion", "action_authority"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda *, row, mode_labels: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "action_authority"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 6.5


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
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected.get("baseline_guard_reason", "") == ""
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 6.0


def test_hybrid_selector_prefers_request_surface_for_filing_timeliness_without_guard() -> None:
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
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert "specialized_guard_reason" not in selected

    disabled_selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "operational_record"],
        margin=1.0,
        min_score=4.0,
        guard_disable_regex=compile_guard_disable_regex("request filing timeliness question"),
        fallback_selector=fallback_selector,
    )

    assert fallback_calls == 0
    assert disabled_selected["selected_mode"] == "operational_record"
    assert disabled_selected["hybrid_decision"] == "structural_confident"
    assert "specialized_guard_reason" not in disabled_selected
    assert "disabled_guard_reasons" not in disabled_selected


def test_hybrid_selector_prefers_calculated_deadline_filing_without_guard() -> None:
    row = {
        "id": "q_calculated_deadline_filing",
        "question": "Was the appeal filed before the original deadline?",
        "modes": [
            _mode_with_predicates("loose_deadline", ["deadline_value", "event_status"], rows=8),
            _mode_with_predicates("calculated_deadline", ["event_filed", "deadline_calculated", "rule_text"], rows=3),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["loose_deadline", "calculated_deadline"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda *, row, mode_labels: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "calculated_deadline"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert not selected.get("specialized_guard_reason")
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 6.0


def test_board_review_deadline_phrase_no_longer_has_selector_guard() -> None:
    row = {
        "id": "q_board_review_deadline_guard_retired",
        "question": "When does the board review period end?",
        "modes": [
            _mode_with_predicates("loose_deadline", ["deadline_value"], rows=6),
            _mode_with_predicates("calculated_deadline", ["event_filed", "deadline_calculated", "rule_text"], rows=2),
        ],
    }
    labels = ["loose_deadline", "calculated_deadline"]

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=labels),
        mode_labels=labels,
        structural_choice="loose_deadline",
    )

    assert override is None


def test_structural_selector_prefers_calculated_deadline_on_unlike_review_period() -> None:
    row = {
        "id": "q_unlike_calculated_deadline",
        "question": "When does the equipment review period end after the notice was issued?",
        "modes": [
            _mode_with_predicates("loose_deadline", ["deadline_value"], rows=9),
            _mode_with_predicates("calculated_deadline", ["event_issued", "deadline_calculated", "elapsed_days"], rows=3),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["loose_deadline", "calculated_deadline"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda *, row, mode_labels: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "calculated_deadline"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 6.0


def test_hybrid_selector_prefers_appeal_deadline_status_without_guard() -> None:
    row = {
        "id": "q_appeal_status_deadline",
        "question": "What is the docket status of the appeal if no decision was issued by the deadline?",
        "modes": [
            _mode_with_predicates("bare_docket_status", ["docket_status", "appeal_status"], rows=12),
            _mode_with_predicates("appeal_deadline_context", ["event_filed", "deadline_calculated", "no_decision"], rows=3),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["bare_docket_status", "appeal_deadline_context"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda *, row, mode_labels: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "appeal_deadline_context"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert not selected.get("specialized_guard_reason")
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 6.25


def test_appeal_tolling_phrase_no_longer_has_selector_guard() -> None:
    row = {
        "id": "q_appeal_tolling_guard_retired",
        "question": "What tolling effect did the appeal have on the penalty clock?",
        "modes": [
            _mode_with_predicates("isolated_tolling_label", ["tolling_label"], rows=6),
            _mode_with_predicates("appeal_rule_context", ["event_filed", "deadline_calculated", "rule_text"], rows=3),
        ],
    }
    labels = ["isolated_tolling_label", "appeal_rule_context"]

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=labels),
        mode_labels=labels,
        structural_choice="isolated_tolling_label",
    )

    assert override is None


def test_structural_selector_prefers_appeal_event_deadline_on_unlike_review_status() -> None:
    row = {
        "id": "q_unlike_appeal_event_deadline",
        "question": "Is the permit appeal still pending after the review deadline?",
        "modes": [
            _mode_with_predicates("docket_status", ["appeal_status", "docket_status"], rows=10),
            _mode_with_predicates("appeal_deadline_context", ["appeal_filed", "deadline_calculated", "decision_pending"], rows=2),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["docket_status", "appeal_deadline_context"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda *, row, mode_labels: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "appeal_deadline_context"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 6.25


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
    assert selected.get("specialized_guard_reason", "") == ""


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
    assert selected.get("specialized_guard_reason", "") == ""


def test_hybrid_selector_prefers_memo_resolution_claim_issue_surface_without_guard() -> None:
    row = {
        "id": "q004n2",
        "question": "Does the resolution substantially turn on an unresolved memo claim?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 4, "predicate": "permit_status"},
                        {"status": "success", "num_rows": 3, "predicate": "document_status"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "rationale_contrast",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 1, "predicate": "statement_claim"},
                        {"status": "success", "num_rows": 1, "predicate": "unresolved_issue"},
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
    assert selected.get("specialized_guard_reason", "") == ""


def test_hybrid_selector_prefers_reply_memo_row_value_without_guard() -> None:
    row = {
        "id": "q004n3",
        "question": "What theory did the reply memo use to contest the finding?",
        "modes": [
            {
                "mode": "baseline",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 6, "predicate": "source_document_status"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "archival_row",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 1, "predicate": "row_value"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "archival_row"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "baseline"},
    )

    assert selected["selected_mode"] == "archival_row"
    assert selected.get("specialized_guard_reason", "") == ""


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
    assert selected.get("specialized_guard_reason", "") == ""


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
    assert selected.get("specialized_guard_reason", "") == ""


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
    assert selected.get("specialized_guard_reason", "") == ""


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
    assert selected.get("specialized_guard_reason", "") == ""


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
    assert selected.get("specialized_guard_reason", "") == ""


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
    assert selected.get("specialized_guard_reason", "") == ""


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
    assert selected.get("specialized_guard_reason", "") == ""


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
    assert selected.get("specialized_guard_reason", "") == ""


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
    assert selected.get("specialized_guard_reason", "") == ""


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
    assert selected.get("specialized_guard_reason", "") == ""


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
    assert selected.get("specialized_guard_reason", "") == ""


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
    assert selected.get("specialized_guard_reason", "") == ""


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
    assert selected.get("specialized_guard_reason", "") == ""


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
    assert selected.get("specialized_guard_reason", "") == ""


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
    assert selected.get("specialized_guard_reason", "") == ""


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
    assert selected.get("specialized_guard_reason", "") == ""
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 8.0


def test_hybrid_selector_prefers_unrenewed_expiry_deadline_surface_with_guard_disabled() -> None:
    row = {
        "id": "q_unrenewed_expiry_deadline",
        "question": "When does the Temporary Food Service License expire if not renewed?",
        "modes": [
            _mode_with_predicates("lifecycle", ["permit_name", "valid_to", "permit_extension"], rows=18, relaxed=True),
            _mode_with_predicates(
                "validity_deadline",
                ["deadline_requirement", "permit_status", "permit_validity"],
                rows=4,
                relaxed=True,
            ),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["lifecycle", "validity_deadline"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda *, row, mode_labels: (_ for _ in ()).throw(AssertionError("fallback called")),
        guard_disable_regex=compile_guard_disable_regex("unrenewed-expiry question needs validity plus deadline"),
    )

    assert selected["selected_mode"] == "validity_deadline"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert "specialized_guard_reason" not in selected
    assert "disabled_guard_reasons" not in selected


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
    assert selected.get("specialized_guard_reason", "") == ""
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 5.0


def test_hybrid_selector_prefers_violation_event_suspension_surface_with_guard_disabled() -> None:
    row = {
        "id": "q_suspension_trigger_event",
        "question": "What triggered the first sound permit suspension?",
        "modes": [
            _mode_with_predicates(
                "interval",
                ["permit_name", "instance_of", "suspension_period", "violation_occurred"],
                rows=12,
            ),
            _mode_with_predicates(
                "violation_event",
                ["permit_name", "instance_of", "suspension_period", "violation_record", "violation_occurred"],
                rows=4,
                relaxed=True,
            ),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["interval", "violation_event"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda *, row, mode_labels: (_ for _ in ()).throw(AssertionError("fallback called")),
        guard_disable_regex=compile_guard_disable_regex("suspension-trigger question needs violation event"),
    )

    assert selected["selected_mode"] == "violation_event"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert "specialized_guard_reason" not in selected


def test_second_violation_duration_phrase_no_longer_has_selector_guard() -> None:
    row = {
        "id": "q_second_violation_duration_guard_retired",
        "question": "How long was the suspension period after the second sound violation?",
        "modes": [
            _mode_with_predicates("interval_only", ["suspension_period"], rows=8),
            _mode_with_predicates(
                "event_interval",
                ["permit_suspension", "suspension_period", "violation_record"],
                rows=3,
            ),
        ],
    }
    labels = ["interval_only", "event_interval"]

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=labels),
        mode_labels=labels,
        structural_choice="interval_only",
    )

    assert override is None


def test_structural_selector_prefers_event_record_duration_on_unlike_interval_row() -> None:
    row = {
        "id": "q_unlike_event_duration",
        "question": "How long was the access restriction period after the badge infraction?",
        "modes": [
            _mode_with_predicates("interval_only", ["restriction_period"], rows=10),
            _mode_with_predicates(
                "event_interval",
                ["infraction_record", "restriction_period", "active_interval"],
                rows=2,
            ),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["interval_only", "event_interval"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda *, row, mode_labels: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "event_interval"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 7.25


def test_hybrid_selector_prefers_complete_permit_action_list_with_guard_disabled() -> None:
    row = {
        "id": "q_permit_action_list",
        "question": "List every permit that has been suspended, restricted, or is pending action as of October 16.",
        "modes": [
            _mode_with_predicates("status_rows", ["instance_of", "permit_name", "permit_status"], rows=20),
            _mode_with_predicates(
                "action_surface",
                ["automatic_suspension", "deadline_requirement", "permit_restriction", "permit_status"],
                rows=11,
                relaxed=True,
            ),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["status_rows", "action_surface"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda *, row, mode_labels: (_ for _ in ()).throw(AssertionError("fallback called")),
        guard_disable_regex=compile_guard_disable_regex("permit-action list"),
    )

    assert selected["selected_mode"] == "action_surface"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert "specialized_guard_reason" not in selected
    assert "disabled_guard_reasons" not in selected


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
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected.get("specialized_guard_reason", "") == ""


def test_hybrid_selector_prefers_mistaken_movement_quarantine_count_without_guard() -> None:
    row = {
        "id": "q_quarantine_count",
        "question": "How many Lot 5C plants were placed under quarantine?",
        "modes": [
            {
                "mode": "quarantine_scope",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 4, "predicate": "lot"},
                        {"status": "success", "num_rows": 5, "predicate": "lot_status"},
                        {"status": "success", "num_rows": 4, "predicate": "quarantine_scope"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "mistaken_movement",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 1, "predicate": "lot"},
                        {"status": "success", "num_rows": 1, "predicate": "lot_status"},
                        {"status": "success", "num_rows": 1, "predicate": "mistaken_movement"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["quarantine_scope", "mistaken_movement"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda *, row, mode_labels: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "mistaken_movement"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert not selected.get("specialized_guard_reason")


def test_hybrid_selector_prefers_quarantine_scope_for_never_quarantined_count_without_guard() -> None:
    row = {
        "id": "q_never_quarantined_count",
        "question": "How many Lot 5C plants were never quarantined?",
        "modes": [
            _mode_with_predicates("lot_status", ["lot_status", "lot_location", "lab_result"], rows=7),
            _mode_with_predicates("quarantine_scope", ["lot", "lot_status", "quarantine_scope"], rows=3),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["lot_status", "quarantine_scope"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda *, row, mode_labels: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "quarantine_scope"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 5.0


def test_split_lot_never_quarantined_phrase_no_longer_has_selector_guard() -> None:
    row = {
        "id": "q_split_lot_retired_guard",
        "question": "How many Lot 5C plants were never quarantined?",
        "modes": [
            _mode_with_predicates("lot_status", ["lot_status", "lot_location", "lab_result"], rows=7),
            _mode_with_predicates("quarantine_scope", ["lot", "lot_status", "quarantine_scope"], rows=3),
        ],
    }
    labels = ["lot_status", "quarantine_scope"]
    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=labels),
        mode_labels=labels,
        structural_choice="lot_status",
    )

    assert override is None


def test_structural_selector_prefers_scoped_status_count_on_unlike_restriction_row() -> None:
    row = {
        "id": "q_scoped_status_count_unlike",
        "question": "How many Unit 4 devices were never restricted?",
        "modes": [
            _mode_with_predicates("status_history", ["device_status", "status_history"], rows=19),
            _mode_with_predicates("restriction_scope", ["device_status", "restriction_scope"], rows=4),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["status_history", "restriction_scope"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda *, row, mode_labels: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "restriction_scope"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 5.0


def test_hybrid_selector_prefers_lot5c_status_summary_surface() -> None:
    row = {
        "id": "q_lot5c_current_status",
        "question": "What is the current status of all 15 Lot 5C plants?",
        "modes": [
            _mode_with_predicates("lot_status", ["lot_status", "lot_location", "lab_result"], rows=7),
            _mode_with_predicates(
                "mistaken_movement",
                ["lot", "lot_status", "mistaken_movement", "status_change_reason"],
                rows=3,
            ),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["lot_status", "mistaken_movement"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda *, row, mode_labels: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "mistaken_movement"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


def test_hybrid_selector_prefers_status_elevation_context_surface() -> None:
    row = {
        "id": "q_status_elevation",
        "question": "Why was Lot 5B elevated from precautionary hold to suspect?",
        "modes": [
            _mode_with_predicates("status_reason", ["lot", "lot_status", "status_change_reason"], rows=1),
            _mode_with_predicates("status_context", ["greenhouse_status", "lab_result", "lot_location", "lot_status"], rows=6),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["status_reason", "status_context"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda *, row, mode_labels: (_ for _ in ()).throw(AssertionError("fallback called")),
        guard_disable_regex=compile_guard_disable_regex("status-elevation rationale"),
    )

    assert selected["selected_mode"] == "status_context"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert "disabled_guard_reasons" not in selected


def test_hybrid_selector_prefers_vendor_deficiency_without_guard() -> None:
    row = {
        "id": "q_failed_vendor_rationale",
        "question": "Why did the service vendor fail the compliance check?",
        "modes": [
            _mode_with_predicates("status_summary", ["vendor_status", "inspection_result"], rows=8),
            _mode_with_predicates("deficiency_detail", ["vendor_deficiency", "inspection_result", "permit_status"], rows=1),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["status_summary", "deficiency_detail"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "deficiency_detail"
    assert selected.get("specialized_guard_reason", "") == ""


def test_hybrid_selector_prefers_violation_status_failure_surface_without_guard() -> None:
    row = {
        "id": "q_failed_vendor_violation",
        "question": "Why did the vendor fail inspection?",
        "modes": [
            _mode_with_predicates("broad_status", ["vendor_status"], rows=10),
            _mode_with_predicates("violation_surface", ["inspection_result", "vendor_status", "violation_record"], rows=2),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["broad_status", "violation_surface"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "violation_surface"
    assert selected.get("specialized_guard_reason", "") == ""


def test_hybrid_selector_prefers_display_outcome_surface_without_guard() -> None:
    row = {
        "id": "q_display_outcome",
        "question": "What happened during the public display?",
        "modes": [
            _mode_with_predicates("permit_summary", ["permit_status"], rows=8),
            _mode_with_predicates("inspection_outcome", ["inspection_conducted", "inspection_result", "permit_status"], rows=2),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["permit_summary", "inspection_outcome"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "inspection_outcome"
    assert selected.get("specialized_guard_reason", "") == ""


def test_hybrid_selector_prefers_incident_validity_outcome_surface_without_guard() -> None:
    row = {
        "id": "q_incident_outcome",
        "question": "What was the display outcome after the reported incident?",
        "modes": [
            _mode_with_predicates("permit_summary", ["permit_validity"], rows=8),
            _mode_with_predicates("incident_outcome", ["permit_validity", "incident_reported", "inspection_result"], rows=2),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["permit_summary", "incident_outcome"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "incident_outcome"
    assert selected.get("specialized_guard_reason", "") == ""


def test_hybrid_selector_prefers_termination_rationale_threshold_with_guard_disabled() -> None:
    row = {
        "id": "q_termination_denial",
        "question": "[OX-020] Why was the first termination request denied?",
        "modes": [
            _mode_with_predicates(
                "termination_response",
                ["clarification_of", "termination_request", "termination_response", "unit_status_change"],
                rows=4,
            ),
            _mode_with_predicates(
                "termination_rationale",
                ["termination_status", "clarification_provided", "unit_count"],
                rows=3,
                relaxed=True,
            ),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["termination_response", "termination_rationale"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda *, row, mode_labels: (_ for _ in ()).throw(AssertionError("fallback called")),
        guard_disable_regex=compile_guard_disable_regex("termination-denial question"),
    )

    assert selected["selected_mode"] == "termination_rationale"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert "specialized_guard_reason" not in selected
    assert "disabled_guard_reasons" not in selected


def test_hybrid_selector_prefers_classification_bound_counterfactual_deadline_with_guard_disabled() -> None:
    row = {
        "id": "q_counterfactual_reclassification_deadline",
        "question": (
            "[OX-039] If the recall had not been reclassified from Class II to Class I, "
            "what would the distributor notification deadline have been?"
        ),
        "modes": [
            _mode_with_predicates("notification_deadline", ["notification_deadline"], rows=1),
            _mode_with_predicates(
                "classification_deadline",
                ["classification_change", "deadline_requirement", "recall_classification"],
                rows=3,
                relaxed=True,
            ),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["notification_deadline", "classification_deadline"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda *, row, mode_labels: (_ for _ in ()).throw(AssertionError("fallback called")),
        guard_disable_regex=compile_guard_disable_regex("counterfactual reclassification deadline"),
    )

    assert selected["selected_mode"] == "classification_deadline"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert "specialized_guard_reason" not in selected
    assert "disabled_guard_reasons" not in selected


def test_hybrid_selector_prefers_procedure_and_eligibility_for_counterfactual_recusal() -> None:
    row = {
        "id": "q_counterfactual_recusal",
        "question": (
            "[AG-040] If Bianchi had not been a board member of SCLT and had not recused, "
            "and if all 5 committee members had been present, what would have been different "
            "about the SCLT decision?"
        ),
        "modes": [
            _mode_with_predicates(
                "broad_context",
                ["quorum_status", "rule_text", "vote_outcome", "ineligible_due_to"],
                rows=37,
                relaxed=True,
            ),
            _mode_with_predicates(
                "procedure_eligibility",
                [
                    "application_status",
                    "committee_member",
                    "eligibility_determination",
                    "member_recused",
                    "quorum_met",
                    "rule_text",
                    "vote_result",
                ],
                rows=32,
                relaxed=True,
            ),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["broad_context", "procedure_eligibility"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda *, row, mode_labels: (_ for _ in ()).throw(AssertionError("fallback called")),
        guard_disable_regex=compile_guard_disable_regex("counterfactual-recusal outcome"),
    )

    assert selected["selected_mode"] == "procedure_eligibility"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert "specialized_guard_reason" not in selected
    assert "disabled_guard_reasons" not in selected


def test_hybrid_selector_prefers_rule3_ineligibility_surface_for_avalon() -> None:
    row = {
        "id": "q_rule3_ineligible",
        "question": "[AG-005] Is Achebe also ineligible under Rule 3 (for-profit entity)?",
        "modes": [
            _mode_with_predicates("raw_context", ["org_type", "project_component", "grant_denied", "rule_text"], rows=8),
            _mode_with_predicates("determination", ["applicant_type", "eligibility_determination", "rule_text"], rows=3),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["raw_context", "determination"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda *, row, mode_labels: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "determination"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


def test_hybrid_selector_prefers_conditional_approval_deadline_surface_for_avalon() -> None:
    row = {
        "id": "q_conditional_deadline",
        "question": "[AG-019] What is the deadline for Petrov to satisfy her conditional approval?",
        "modes": [
            _mode_with_predicates("interpretation", ["applicant_name", "rule_text", "director_interpretation"], rows=10),
            _mode_with_predicates("deadline", ["conditional_approval", "condition_deadline"], rows=2),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["interpretation", "deadline"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda *, row, mode_labels: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "deadline"
    assert selected["selection_source"] == "hybrid_structural"


def test_hybrid_selector_prefers_direct_prior_grant_window_surface_for_avalon() -> None:
    row = {
        "id": "q_three_year_window",
        "question": "[AG-014] Does SCLT's FY2023 3-year-window argument have merit?",
        "modes": [
            _mode_with_predicates(
                "broad_window",
                ["eligibility_determination", "prior_grant_history", "interpretation_text", "rule_text"],
                rows=16,
                relaxed=True,
            ),
            _mode_with_predicates("direct_window", ["prior_grant", "rule_text", "director_interpretation"], rows=3),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["broad_window", "direct_window"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda *, row, mode_labels: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "direct_window"
    assert selected["selection_source"] == "hybrid_structural"


def test_hybrid_selector_prefers_application_status_counts_for_avalon() -> None:
    received = {
        "id": "q_application_received_count",
        "question": "[AG-027] How many applications were received in the 2026 cycle?",
        "modes": [
            _mode_with_predicates("status_count", ["application_status", "applicant_id"], rows=9),
            _mode_with_predicates("vote_count", ["applicant_id", "vote_outcome"], rows=8),
        ],
    }
    denied = {
        "id": "q_application_denied_count",
        "question": "[AG-028] How many applications were denied?",
        "modes": [
            _mode_with_predicates("status_count", ["application_status"], rows=4),
            _mode_with_predicates("vote_count", ["vote_outcome"], rows=3),
        ],
    }

    for row in [received, denied]:
        selected = hybrid_selector(
            row=row,
            mode_labels=["status_count", "vote_count"],
            margin=1.0,
            min_score=4.0,
            fallback_selector=lambda *, row, mode_labels: (_ for _ in ()).throw(AssertionError("fallback called")),
        )
        assert selected["selected_mode"] == "status_count"
        assert selected["selection_source"] == "hybrid_structural"


def test_hybrid_selector_prefers_recall_scope_change_timeline_surface() -> None:
    row = {
        "id": "q_recall_scope_change",
        "question": "[OX-028] How did the recall scope change over time?",
        "modes": [
            _mode_with_predicates(
                "recall_classification",
                ["classification_change", "lot_affected", "recall_classification", "unit_count"],
                rows=13,
            ),
            _mode_with_predicates(
                "timeline",
                ["clock_reset", "event_occurred", "lot_affected", "recall_classified_as", "unit_count"],
                rows=1,
            ),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["recall_classification", "timeline"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda *, row, mode_labels: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "timeline"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


def test_hybrid_selector_prefers_specific_lot_affectedness_correction_surface() -> None:
    row = {
        "id": "q_lot_affected",
        "question": "[OX-037] Is Lot 7200-2024-G affected by the recall?",
        "modes": [
            _mode_with_predicates(
                "recall_classification",
                ["correction_of", "recall_classification", "recall_reclassification", "unit_count"],
                rows=6,
                relaxed=True,
            ),
            _mode_with_predicates("lot_correction", ["corrected_value", "lot_affected"], rows=2, relaxed=True),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["recall_classification", "lot_correction"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda *, row, mode_labels: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "lot_correction"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


def test_hybrid_selector_prefers_compact_failed_reinspection_count_with_guard_disabled() -> None:
    row = {
        "id": "q_failed_reinspection",
        "question": "How many vendors failed the October 15 reinspection?",
        "modes": [
            _mode_with_predicates("lifecycle_status", ["inspection_record", "vendor_status"], rows=6),
            _mode_with_predicates("compact_inspection", ["inspection_result"], rows=2),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["lifecycle_status", "compact_inspection"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda *, row, mode_labels: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "compact_inspection"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert "specialized_guard_reason" not in selected
    assert "disabled_guard_reasons" not in selected


def test_hybrid_selector_prefers_alcohol_restriction_rationale_surface() -> None:
    row = {
        "id": "q_alcohol_restriction",
        "question": "Why were alcohol service hours restricted?",
        "modes": [
            _mode_with_predicates("lifecycle_status", ["permit_restriction", "permit_status"], rows=4),
            _mode_with_predicates(
                "rationale",
                ["meeting_summary", "permit_restriction", "permit_type", "permit_validity", "source_claim", "violation_record"],
                rows=1,
            ),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["lifecycle_status", "rationale"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda *, row, mode_labels: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "rationale"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


def test_hybrid_selector_prefers_unrestricted_active_count_status_surface() -> None:
    row = {
        "id": "q_unrestricted_active_count",
        "question": "As of October 16, how many of the five permit types are fully active without restrictions?",
        "modes": [
            _mode_with_predicates(
                "broad_rows",
                ["instance_of", "permit_name", "permit_restriction", "permit_validity", "restriction_applied"],
                rows=26,
            ),
            _mode_with_predicates(
                "status_restriction",
                ["permit_status", "permit_restriction", "permit_type", "permit_validity"],
                rows=4,
            ),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["broad_rows", "status_restriction"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda *, row, mode_labels: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "status_restriction"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


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
    assert selected.get("specialized_guard_reason", "") == ""


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
        guard_disable_regex=compile_guard_disable_regex("provisional-control question"),
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "candidate"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


def test_hybrid_selector_prefers_court_inheritance_surface_for_post_death_legal_owner_structurally() -> None:
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
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "baseline"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


def test_hybrid_selector_prefers_court_inheritance_surface_without_ownership_guard() -> None:
    row = {
        "id": "q031",
        "question": "Who legally owns the King Pear?",
        "modes": [
            _mode_with_predicates("stale_owner", ["legal_owner", "estate_asset_included"], rows=25, relaxed=True),
            {
                "mode": "court_inheritance",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 1, "predicate": "court_ruling"},
                        {"status": "success", "num_rows": 1, "predicate": "part_of"},
                        {"status": "success", "num_rows": 1, "predicate": "will_transfer"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["stale_owner", "court_inheritance"],
        margin=1.0,
        min_score=4.0,
        guard_disable_regex=compile_guard_disable_regex("post-death legal-ownership question"),
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "court_inheritance"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


def test_hybrid_selector_prefers_bronwen_will_provision_tree_surface() -> None:
    row = {
        "id": "q004",
        "question": "Which trees did Bronwen inherit?",
        "modes": [
            _mode_with_predicates("court_inheritance", ["inheritance", "will_transfer"], rows=5, relaxed=True),
            {
                "mode": "will_provision_tree_list",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "will_provision",
                            "was_relaxed_fallback": False,
                        },
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "legal_owner",
                            "was_relaxed_fallback": False,
                        },
                        {
                            "status": "success",
                            "num_rows": 12,
                            "predicate": "estate_asset_included",
                            "was_relaxed_fallback": True,
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
        mode_labels=["court_inheritance", "will_provision_tree_list"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "will_provision_tree_list"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


def test_hybrid_selector_prefers_uncontested_estate_status_for_ffion_inheritance() -> None:
    row = {
        "id": "q027",
        "question": "List the trees that are uncontested parts of Ffion's inheritance.",
        "modes": [
            _mode_with_predicates(
                "court_compound_atom",
                ["court_ruling", "part_of", "will_transfer", "claim_disputed", "will_challenge"],
                rows=3,
                relaxed=True,
            ),
            _mode_with_predicates(
                "estate_status_rows",
                ["court_finding", "estate_asset_included", "disputed_claim", "will_provision", "legal_owner"],
                rows=3,
                relaxed=True,
            ),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["court_compound_atom", "estate_status_rows"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "estate_status_rows"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


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
        guard_disable_regex=compile_guard_disable_regex("current possession/maintenance question"),
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "candidate"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


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
                        {"status": "success", "num_rows": 1, "predicate": "harvest_right_granted"},
                        {"status": "success", "num_rows": 1, "predicate": "verbal_agreement"},
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
        guard_disable_regex=compile_guard_disable_regex("solicitor-advice question"),
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "baseline"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


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
    assert selected.get("specialized_guard_reason", "") == ""


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
    assert selected.get("specialized_guard_reason", "") == ""


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
    assert selected.get("specialized_guard_reason", "") == ""


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
    assert selected.get("specialized_guard_reason", "") == ""


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
    assert selected.get("specialized_guard_reason", "") == ""


def test_hybrid_selector_prefers_missing_evidence_claim_absence_surface_without_guard() -> None:
    row = {
        "id": "q_missing_evidence",
        "question": "What evidence did the claimant not produce?",
        "modes": [
            _mode_with_predicates("status_summary", ["claim_status", "finding_record"], rows=8),
            _mode_with_predicates("claim_absence", ["acknowledged_by", "claim_asserted_by", "asserts_claim"], rows=2),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["status_summary", "claim_absence"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "claim_absence"
    assert selected.get("specialized_guard_reason", "") == ""


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
    assert selected["selection_source"] == "hybrid_structural"
    assert "specialized_guard_reason" not in selected


def test_final_attendance_focus_selects_student_count_with_guard_disabled() -> None:
    row = {
        "id": "q_student_count",
        "question": "How many students were on the return coach?",
        "modes": [
            _mode_with_predicates("broad_roster", ["group_membership", "attendance_status"], rows=20, relaxed=True),
            _mode_with_predicates("scoped_final_attendance", ["attendance_final"], rows=1),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["broad_roster", "scoped_final_attendance"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
        guard_disable_regex=compile_guard_disable_regex("student-count question needs scoped final-attendance"),
    )

    assert selected["selected_mode"] == "scoped_final_attendance"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 9.0


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
    assert selected.get("specialized_guard_reason", "") == ""


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
    assert selected.get("specialized_guard_reason", "") == ""


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
    assert selected.get("specialized_guard_reason", "") == ""


def test_hybrid_selector_prefers_interval_membership_for_group_designation_focus() -> None:
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
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 6.0


def test_group_designation_focus_selects_interval_surface_with_guard_disabled() -> None:
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
        guard_disable_regex=compile_guard_disable_regex("group-designation suspension question"),
        fallback_selector=lambda **_kwargs: {"selected_mode": "baseline"},
    )

    assert selected["selected_mode"] == "interval"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 6.0


def test_compact_query_evidence_includes_bundle_results_as_direct_support() -> None:
    evidence = select_qa_mode_without_oracle.compact_query_evidence(
        {
            "query_results": [
                {
                    "derived_from_queries": ["event_occurs(Overbound, Person, Action, Time)."],
                    "query": "event_occurs(Relaxed, Person, Action, Time).",
                    "result": {
                        "status": "success",
                        "predicate": "event_occurs",
                        "num_rows": 12,
                        "variables": ["Relaxed", "Person", "Action", "Time"],
                        "rows": [{"Action": "departed_early"}],
                    },
                }
            ],
            "evidence_bundle_plan_query_results": [
                {
                    "derived_from_queries": [
                        "event_occurs(EvtJostad, person_jostad, departed_for_emergency, 2025_10_08t12_00)."
                    ],
                    "query": "event_occurs(EvtJostad, person_jostad, departed_for_emergency, 2025_10_08t12_00).",
                    "result": {
                        "status": "success",
                        "predicate": "event_occurs",
                        "num_rows": 1,
                        "variables": ["EvtJostad"],
                        "rows": [{"EvtJostad": "evt_jostad_departure_1200"}],
                    },
                }
            ],
        },
        sample_row_limit=3,
        include_self_check=False,
    )

    relaxed, bundle = evidence["executed_results"]

    assert relaxed["was_relaxed_fallback"] is True
    assert bundle["from_evidence_bundle_plan"] is True
    assert bundle["was_relaxed_fallback"] is False


def test_jostad_departure_reason_focus_prefers_explicit_emergency_event_surface() -> None:
    row = {
        "id": "q012",
        "question": "Why did Mr. Jostad leave on Day 2?",
        "modes": [
            {
                "mode": "early_broad_membership",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "event_occurs",
                            "sample_rows": [{"Action_Jostad": "departed_early"}],
                        },
                        {"status": "success", "num_rows": 1, "predicate": "attendance_status"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "interval_membership",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "event_occurs",
                            "sample_rows": [{"Action": "departed_for_emergency"}],
                        },
                        {"status": "success", "num_rows": 1, "predicate": "attendance_status"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["early_broad_membership", "interval_membership"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "early_broad_membership"},
    )

    assert selected["selected_mode"] == "interval_membership"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 7.0


def test_cosmo_original_group_focus_prefers_direct_membership_surface() -> None:
    row = {
        "id": "q004",
        "question": "Which group was Cosmo originally assigned to?",
        "modes": [
            {
                "mode": "formal_group_formation",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 6, "predicate": "group_id"},
                        {"status": "success", "num_rows": 2, "predicate": "group_formation"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "direct_membership",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 2,
                            "predicate": "group_membership",
                            "sample_rows": [{"Group": "group_red", "Person": "person_cosmo"}],
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
        mode_labels=["formal_group_formation", "direct_membership"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "formal_group_formation"},
    )

    assert selected["selected_mode"] == "direct_membership"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 7.0


def test_freya_witness_focus_prefers_starfish_claim_surface() -> None:
    row = {
        "id": "q017",
        "question": "According to Freya, what was Elio reaching for when he slipped?",
        "modes": [
            {
                "mode": "unresolved_discrepancy",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 1, "predicate": "unresolved_issue"},
                        {"status": "success", "num_rows": 1, "predicate": "discrepancy_in"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "freya_claim",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 1,
                            "predicate": "incident_claim",
                            "sample_rows": [
                                {
                                    "Person": "person_freya",
                                    "ClaimText": "elio_was_reaching_for_a_starfish_when_he_slipped",
                                }
                            ],
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
        mode_labels=["unresolved_discrepancy", "freya_claim"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "unresolved_discrepancy"},
    )

    assert selected["selected_mode"] == "freya_claim"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 8.0


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
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert "specialized_guard_reason" not in selected
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 7.0


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
    assert selected.get("specialized_guard_reason", "") == ""


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
    assert selected.get("specialized_guard_reason", "") == ""


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
    assert selected.get("specialized_guard_reason", "") == ""


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
    assert selected.get("specialized_guard_reason", "") == ""


def test_hybrid_selector_prefers_item_received_from_for_intake_actor() -> None:
    row = {
        "id": "q_intake_actor_received_from",
        "question": "Who brought in the clockwork notebook?",
        "modes": [
            _mode_with_predicates("ledger_volume", ["ledger_entry", "entry_has_hand"], rows=8),
            _mode_with_predicates("received_from", ["item_received_from"], rows=1),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["ledger_volume", "received_from"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "received_from"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected.get("specialized_guard_reason", "") == ""


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
    assert selected.get("specialized_guard_reason", "") == ""


def test_hybrid_selector_prefers_inventory_count_surface_over_title_names_without_guard() -> None:
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
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert "specialized_guard_reason" not in selected


def test_hybrid_selector_prefers_inventory_count_surface_without_guard() -> None:
    row = {
        "id": "q_inventory_count_general",
        "question": "How many titles were found in the physical count?",
        "modes": [
            _mode_with_predicates("count_outcome", ["incident_outcome"], rows=4),
            _mode_with_predicates("title_names", ["novel_title"], rows=9),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["count_outcome", "title_names"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "count_outcome"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


def test_structural_selector_prefers_inventory_outcome_count_over_identity_volume() -> None:
    row = {
        "id": "q_inventory_outcome_unlike",
        "question": "How many devices were missing in the inventory count?",
        "modes": [
            _mode_with_predicates("count_outcome", ["incident_outcome"], rows=2),
            _mode_with_predicates("identity_volume", ["item_title", "asset_name"], rows=14),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["count_outcome", "identity_volume"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "count_outcome"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 6.0


def test_physical_inventory_count_phrase_no_longer_has_selector_guard() -> None:
    row = {
        "id": "q_inventory_count_retired_guard",
        "question": "How many titles were found in the physical count?",
        "modes": [
            _mode_with_predicates("count_outcome", ["incident_outcome"], rows=4),
            _mode_with_predicates("title_names", ["novel_title"], rows=9),
        ],
    }
    scored = structural_mode_scores(row=row, mode_labels=["count_outcome", "title_names"])

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=scored,
        mode_labels=["count_outcome", "title_names"],
        structural_choice="title_names",
    )

    assert override is None


def test_hybrid_selector_prefers_approval_validity_count_without_guard() -> None:
    row = {
        "id": "q_approval_validity_count_general",
        "question": "How many approved displays remain valid?",
        "modes": [
            _mode_with_predicates("status_history", ["current_status", "status_at"], rows=18),
            _mode_with_predicates("approval_validity", ["permit_instance", "permit_type", "permit_validity"], rows=2),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["status_history", "approval_validity"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "approval_validity"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


def test_structural_selector_prefers_approval_validity_count_on_unlike_row() -> None:
    row = {
        "id": "q_approval_validity_count_unlike",
        "question": "How many approved permits remain valid after inspection?",
        "modes": [
            _mode_with_predicates("status_history", ["current_status", "status_at"], rows=25),
            _mode_with_predicates("approval_validity", ["permit_instance", "permit_type", "permit_validity"], rows=2),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["status_history", "approval_validity"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "approval_validity"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 5.5


def test_approved_fireworks_count_phrase_no_longer_has_selector_guard() -> None:
    row = {
        "id": "q_approval_validity_count_retired_guard",
        "question": "How many fireworks displays are approved?",
        "modes": [
            _mode_with_predicates("status_history", ["current_status", "status_at"], rows=18),
            _mode_with_predicates("approval_validity", ["permit_instance", "permit_type", "permit_validity"], rows=2),
        ],
    }
    scored = structural_mode_scores(row=row, mode_labels=["status_history", "approval_validity"])

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=scored,
        mode_labels=["status_history", "approval_validity"],
        structural_choice="status_history",
    )

    assert override is None


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
    assert selected.get("specialized_guard_reason", "") == ""


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
    assert selected.get("specialized_guard_reason", "") == ""


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
    assert selected.get("specialized_guard_reason", "") == ""


def test_hybrid_selector_prefers_witness_statement_for_source_claim_without_guard() -> None:
    row = {
        "id": "q_source_claim_provenance",
        "question": "What did the source claim about the 2003 boundary event?",
        "modes": [
            _mode_with_predicates("finding_summary", ["finding_record", "provenance_summary"], rows=8),
            _mode_with_predicates("witness_source", ["witness_statement"], rows=1),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["finding_summary", "witness_source"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "witness_source"
    assert selected.get("specialized_guard_reason", "") == ""


def test_hybrid_selector_prefers_source_specific_witness_claim_without_guard() -> None:
    row = {
        "id": "q_source_specific_witness",
        "question": "According to the witness, what was the worker reaching for?",
        "modes": [
            _mode_with_predicates("unresolved_summary", ["unresolved_issue", "discrepancy_in"], rows=6),
            _mode_with_predicates("witness_claim", ["witness_report", "incident_claim"], rows=1),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["unresolved_summary", "witness_claim"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "witness_claim"
    assert selected.get("specialized_guard_reason", "") == ""


def test_hybrid_selector_prefers_witness_statement_for_permission_request_without_guard() -> None:
    row = {
        "id": "q_permission_request_provenance",
        "question": "Who requested permission for the archive access?",
        "modes": [
            _mode_with_predicates("date_evidence", ["evidence_date", "document_date"], rows=9),
            _mode_with_predicates("witness_source", ["witness_statement"], rows=1),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["date_evidence", "witness_source"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "witness_source"
    assert selected.get("specialized_guard_reason", "") == ""


def test_hybrid_selector_prefers_report_commission_provenance_without_guard() -> None:
    row = {
        "id": "q_report_commission_provenance",
        "question": "Who commissioned the engineering survey report?",
        "modes": [
            _mode_with_predicates("report_summary", ["survey_report", "report_status"], rows=7),
            _mode_with_predicates("commission_source", ["report_commissioned_by"], rows=1),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["report_summary", "commission_source"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "commission_source"
    assert selected.get("specialized_guard_reason", "") == ""


def test_hybrid_selector_prefers_handwriting_attribution_without_guard() -> None:
    row = {
        "id": "q_correction_authorship",
        "question": "Which expert confirmed who wrote the correction?",
        "modes": [
            _mode_with_predicates("correction_status", ["correction_status"], rows=6),
            _mode_with_predicates("authorship", ["handwriting_attribution", "expert_opinion"], rows=1),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["correction_status", "authorship"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "authorship"
    assert selected.get("specialized_guard_reason", "") == ""


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
    assert selected.get("specialized_guard_reason", "") == ""


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
    assert selected.get("specialized_guard_reason", "") == ""


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
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected.get("specialized_guard_reason", "") == ""


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
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected.get("specialized_guard_reason", "") == ""
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 8.0


def test_hybrid_selector_keeps_failed_viability_threshold_storage_when_guards_disabled() -> None:
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
                        {
                            "status": "success",
                            "num_rows": 8,
                            "predicate": "lot_id",
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
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
        guard_disable_regex=compile_guard_disable_regex("hypothetical failed-viability|counterfactual or hold/readiness"),
    )

    assert selected["selected_mode"] == "baseline"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected.get("disabled_guard_reasons", []) == []
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 8.0


def test_hybrid_selector_prefers_threshold_action_policy_without_guard() -> None:
    row = {
        "id": "q_threshold_action_birth",
        "question": "If FB-2026-005 fails viability testing with a 35% germination rate, what would happen?",
        "modes": [
            _mode_with_predicates("note_surface", ["note_content", "note_subject"], rows=4),
            _mode_with_predicates("policy_action", ["policy_condition_threshold", "policy_minimum_storage", "policy_action"], rows=3),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["note_surface", "policy_action"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "policy_action"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 6.0


def test_structural_selector_prefers_threshold_action_policy_on_unlike_counterfactual() -> None:
    row = {
        "id": "q_threshold_action_unlike",
        "question": "If the inspection score falls below the policy threshold, what action is required?",
        "modes": [
            _mode_with_predicates("note_surface", ["note_content", "note_subject"], rows=6),
            _mode_with_predicates("policy_action", ["policy_condition_threshold", "policy_action"], rows=2),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["note_surface", "policy_action"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "policy_action"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 6.0


def test_failed_viability_threshold_action_phrase_no_longer_has_selector_guard() -> None:
    row = {
        "id": "q_threshold_action_retired_guard",
        "question": "If FB-2026-005 fails viability testing with a 35% germination rate, what would happen?",
        "modes": [
            _mode_with_predicates("note_surface", ["note_content", "note_subject"], rows=4),
            _mode_with_predicates("policy_action", ["policy_condition_threshold", "policy_minimum_storage", "policy_action"], rows=3),
        ],
    }
    scored = structural_mode_scores(row=row, mode_labels=["note_surface", "policy_action"])

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=scored,
        mode_labels=["note_surface", "policy_action"],
        structural_choice="note_surface",
    )

    assert override is None


def test_hybrid_selector_prefers_density_staff_evaluation_surface_over_broad_claims() -> None:
    row = {
        "id": "q011",
        "question": "What density does Dr. Holm calculate?",
        "modes": [
            {
                "mode": "staff_eval",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 1, "predicate": "staff_evaluation"},
                        {
                            "status": "success",
                            "num_rows": 12,
                            "predicate": "staff_evaluation",
                            "was_relaxed_fallback": True,
                        },
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            {
                "mode": "old_staff_eval_of",
                "query_evidence": {
                    "executed_results": [
                        {"status": "success", "num_rows": 5, "predicate": "claim_made_by"},
                        {"status": "success", "num_rows": 5, "predicate": "staff_evaluation_of"},
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["staff_eval", "old_staff_eval_of"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "staff_eval"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 6.0


def test_structural_selector_prefers_numeric_density_value_on_unlike_row() -> None:
    row = {
        "id": "q_density_measure_unlike",
        "question": "What density did the inspection sheet calculate?",
        "modes": [
            _mode_with_predicates("source_opinions", ["claim_made_by", "source_opinion"], rows=12),
            _mode_with_predicates("numeric_evaluation", ["density_value", "measurement_value"], rows=1),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["source_opinions", "numeric_evaluation"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "numeric_evaluation"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 6.0


def test_density_calculation_phrase_no_longer_has_baseline_guard() -> None:
    row = {
        "id": "q_density_retired_guard",
        "question": "What density does Dr. Holm calculate?",
        "modes": [
            _mode_with_predicates("staff_eval", ["staff_evaluation"], rows=1),
            _mode_with_predicates("source_opinions", ["claim_made_by", "source_opinion"], rows=12),
        ],
    }
    scored = structural_mode_scores(row=row, mode_labels=["staff_eval", "source_opinions"])

    reason = structural_baseline_answer_surface_guard_reason(
        row=row,
        scored=scored,
        mode_labels=["staff_eval", "source_opinions"],
        structural_choice="source_opinions",
    )

    assert reason == ""


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
    assert selected.get("specialized_guard_reason", "") == ""


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
    assert selected.get("specialized_guard_reason", "") == ""


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
    assert selected["selection_source"] == "hybrid_structural"
    assert "specialized_guard_reason" not in selected


def test_order_series_identifier_focus_prefers_document_identifier_without_guard() -> None:
    row = {
        "id": "q002",
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
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
        guard_disable_regex=compile_guard_disable_regex("order-series identifier question"),
    )

    assert selected["selected_mode"] == "archival_row_ledger_v1"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


def test_application_number_identifier_focus_prefers_document_identifier_without_guard() -> None:
    row = {
        "id": "q001",
        "question": "What is the application number for Rosalind Okafor-Vance?",
        "modes": [
            _mode_with_predicates("cold", ["score"], rows=48, relaxed=True),
            _mode_with_predicates("source_record", ["source_records"], rows=5),
            _mode_with_predicates("archival_row_ledger_v1", ["document_identifier", "row_actor"], rows=3),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
        guard_disable_regex=compile_guard_disable_regex("application-number identifier question"),
    )

    assert selected["selected_mode"] == "archival_row_ledger_v1"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


def test_wildfire_gis_layer_time_question_prefers_layer_assignment_surface() -> None:
    row = {
        "id": "q020",
        "question": "As of 04:30 PDT on April 15, what evacuation order applied to the Manton Knolls subdivision according to the GIS layer published at that time?",
        "modes": [
            _mode_with_predicates("cold", ["incident_anchor", "layer_supersedes", "parcel_zone_assignment"], rows=19, relaxed=True),
            _mode_with_predicates("source_record", ["source_records", "supersession"], rows=15),
            _mode_with_predicates("archival_row_ledger_v1", ["row_subject", "row_value"], rows=95, relaxed=True),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "cold"
    assert selected["selection_source"] == "hybrid_structural"


def test_road_jurisdiction_authority_prefers_archival_layer_value_surface() -> None:
    row = {
        "id": "q026",
        "question": "Per the road-jurisdiction layer, who has authority over Forest Road 32N17?",
        "modes": [
            _mode_with_predicates("cold", ["road_jurisdiction"], rows=1),
            _mode_with_predicates("source_record", ["controlling_source", "unresolved_issue"], rows=1),
            _mode_with_predicates("archival_row_ledger_v1", ["row_value"], rows=2),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "archival_row_ledger_v1"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected.get("specialized_guard_reason", "") == ""


def test_fiscal_balance_source_prefers_archival_source_row_surface() -> None:
    row = {
        "id": "q012",
        "question": "Which source records the cycle's current fiscal balance?",
        "modes": [
            _mode_with_predicates("cold", ["fiscal_ledger"], rows=6, relaxed=True),
            _mode_with_predicates("source_record", ["count_value", "source_records"], rows=5),
            _mode_with_predicates("archival_row_ledger_v1", ["document_identifier", "row_value", "source_section"], rows=1),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "archival_row_ledger_v1"
    assert selected["selection_source"] == "hybrid_structural"


def test_resulting_average_question_prefers_measured_recomputation_surface() -> None:
    row = {
        "id": "q032",
        "question": "If Tovar's score is dropped from the corrected score sheet, what is the resulting average for Okafor-Vance?",
        "modes": [
            _mode_with_predicates("cold", ["application_average", "score"], rows=8),
            _mode_with_predicates("source_record", ["measurement_value"], rows=10, relaxed=True),
            _mode_with_predicates("archival_row_ledger_v1", ["record_row", "row_participant", "row_value"], rows=11),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "source_record"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected.get("specialized_guard_reason", "") == ""


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
    assert selected.get("specialized_guard_reason", "") == ""


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
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected.get("specialized_guard_reason", "") == ""


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
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "cold"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


def test_hybrid_selector_prefers_log_entry_for_timestamped_source_question_without_guard() -> None:
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
        guard_disable_regex=compile_guard_disable_regex("timestamped message-source question"),
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "cold"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


def test_printed_source_provenance_uses_archival_surface_without_guard() -> None:
    row = {
        "id": "q009",
        "question": "Which source records the 14:02:51 cabinet withdrawal?",
        "modes": [
            _mode_with_predicates("cold", ["event_description"], rows=2),
            _mode_with_predicates("source_record", ["source_document"], rows=2),
            _mode_with_predicates(
                "archival_row_ledger_v1",
                ["record_row", "row_source_name", "source_section_label"],
                rows=2,
            ),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "archival_row_ledger_v1"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert "specialized_guard_reason" not in selected


def test_authoritative_timestamp_question_prefers_correction_surface_over_row_volume() -> None:
    row = {
        "id": "q040",
        "question": "Two timestamps were reported for the cabinet event near 14:02. What are they, which is authoritative, and why?",
        "modes": [
            _mode_with_predicates("archival_row_ledger_v1", ["row_actor", "row_event", "row_time"], rows=69),
            _mode_with_predicates("cold", ["correction_applied", "system_log_entry"], rows=14),
            _mode_with_predicates("source_record", ["controlling_source", "supersession"], rows=2),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["archival_row_ledger_v1", "cold", "source_record"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "cold"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


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
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected.get("specialized_guard_reason", "") == ""


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
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected.get("specialized_guard_reason", "") == ""


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
        guard_disable_regex=compile_guard_disable_regex("panel-chair identity question"),
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "source_record"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected.get("specialized_guard_reason", "") == ""
    assert "disabled_guard_reasons" not in selected


def test_hybrid_selector_prefers_document_exhibit_for_document_identification() -> None:
    row = {
        "id": "q_or_document_identification",
        "question": "What document is Okafor-Vance's reconsideration request?",
        "modes": [
            {
                "mode": "cold",
                "query_evidence": {
                    "executed_results": [
                        {
                            "status": "success",
                            "num_rows": 4,
                            "predicate": "document_exhibit",
                            "was_relaxed_fallback": True,
                        },
                        {
                            "status": "success",
                            "num_rows": 14,
                            "predicate": "event_occurred",
                            "was_relaxed_fallback": False,
                        },
                    ],
                    "warnings": [],
                    "parse_error": "",
                },
            },
            _mode_with_predicates("source_record", ["log_event", "source_document_type"], rows=14),
            _mode_with_predicates("archival_row_ledger_v1", ["row_actor", "record_row", "source_document"], rows=32),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        guard_disable_regex=compile_guard_disable_regex("document-identification question"),
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "cold"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected.get("specialized_guard_reason", "") == ""
    assert "disabled_guard_reasons" not in selected


def test_hybrid_selector_prefers_supersession_status_for_counsel_note_effect() -> None:
    row = {
        "id": "q_or_rule_effect_supersession",
        "question": (
            "Did the §IV.B.3 counsel note supersede the panel's original determination "
            "that Okafor-Vance's application was not fundable?"
        ),
        "modes": [
            _mode_with_predicates(
                "cold",
                ["event_occurred", "bylaw_rule", "score_correction", "application_average"],
                rows=5,
            ),
            _mode_with_predicates("source_record", ["supersession", "status_at", "log_event"], rows=3),
            _mode_with_predicates("archival_row_ledger_v1", ["row_value"], rows=4),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        guard_disable_regex=compile_guard_disable_regex("rule-effect question needs supersession plus status/event"),
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "source_record"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected.get("specialized_guard_reason", "") == ""
    assert "disabled_guard_reasons" not in selected


def test_hybrid_selector_accepts_archival_rule_text_for_scrivener_question_without_bylaw_guard() -> None:
    row = {
        "id": "q_or_rule_effect_bylaw",
        "question": "Per bylaws §IV.B.3, may a scrivener's error in score transcription be corrected in-cycle?",
        "modes": [
            _mode_with_predicates("cold", ["bylaw_rule"], rows=2),
            _mode_with_predicates("source_record", ["bylaw_rule"], rows=24, relaxed=True),
            _mode_with_predicates("archival_row_ledger_v1", ["row_records", "row_value"], rows=3),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        guard_disable_regex=compile_guard_disable_regex("rule-effect question needs direct bylaw-rule"),
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "archival_row_ledger_v1"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected.get("specialized_guard_reason", "") == ""
    assert "disabled_guard_reasons" not in selected


def test_hybrid_selector_prefers_measurement_value_for_resulting_average_without_guard() -> None:
    row = {
        "id": "q_or_resulting_average",
        "question": "If Tovar's score is dropped from the corrected score sheet, what is the resulting average for Okafor-Vance?",
        "modes": [
            _mode_with_predicates("cold", ["score", "application_average"], rows=8),
            _mode_with_predicates("source_record", ["measurement_value"], rows=10, relaxed=True),
            _mode_with_predicates("archival_row_ledger_v1", ["row_value", "record_row", "row_participant"], rows=11),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        guard_disable_regex=compile_guard_disable_regex("resulting-average question"),
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "source_record"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected.get("specialized_guard_reason", "") == ""
    assert "disabled_guard_reasons" not in selected


def test_hybrid_selector_prefers_rule_threshold_for_tax_liability_threshold_without_guard() -> None:
    row = {
        "id": "q_or_tax_threshold",
        "question": "What is the outstanding tax-liability threshold under §2.5?",
        "modes": [
            _mode_with_predicates("parallel", ["applicant_attribute", "eligibility_determination", "pending_verification"], rows=7),
            _mode_with_predicates("cold", ["rule_definition"], rows=2),
            _mode_with_predicates("entity", ["rule_condition", "rule_section"], rows=1),
            _mode_with_predicates("source_record", ["rule_threshold", "rule_description", "rule_id"], rows=1),
            _mode_with_predicates("source_record_facts_v2", ["rule_threshold"], rows=1),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["parallel", "cold", "entity", "source_record", "source_record_facts_v2"],
        margin=1.0,
        min_score=4.0,
        guard_disable_regex=compile_guard_disable_regex("threshold question needs rule-threshold surface"),
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] in {"cold", "entity", "source_record", "source_record_facts_v2"}
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected.get("specialized_guard_reason", "") == ""
    assert "disabled_guard_reasons" not in selected


def test_hybrid_selector_prefers_threshold_exception_surface_for_date_alone_rule_without_guard() -> None:
    row = {
        "id": "q_or_date_alone",
        "question": "Does App-2026-019 satisfy section 2.1 by Borden County incorporation date alone?",
        "modes": [
            _mode_with_predicates("cold", ["threshold_met", "exception_applies", "rule_definition"], rows=4),
            _mode_with_predicates(
                "parallel",
                ["eligibility_determination", "applicant_attribute", "exception_condition"],
                rows=12,
            ),
            _mode_with_predicates(
                "source_record_facts_v2",
                ["rule_threshold", "rule_exception", "applicant_attribute"],
                rows=4,
                relaxed=True,
            ),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "parallel", "source_record_facts_v2"],
        margin=1.0,
        min_score=4.0,
        guard_disable_regex=compile_guard_disable_regex("date-alone rule question"),
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "cold"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected.get("specialized_guard_reason", "") == ""
    assert "disabled_guard_reasons" not in selected


def test_hybrid_selector_prefers_grant_recomputation_surface_for_no_cap_amount_without_guard() -> None:
    row = {
        "id": "q_or_no_cap_amount",
        "question": "What grant amount would App-2026-014 have received if the section 3.4 cap had not applied?",
        "modes": [
            _mode_with_predicates("source_record_facts_v2", ["grant_amount", "rule_bonus", "rule_cap"], rows=7),
            _mode_with_predicates(
                "memory_ledger_combo",
                ["grant_amount", "determination_reason", "applicant_attribute"],
                rows=8,
            ),
            _mode_with_predicates(
                "entity",
                ["grant_amount", "bonus_percentage", "rule_condition", "exception_applied"],
                rows=4,
                relaxed=True,
            ),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["source_record_facts_v2", "memory_ledger_combo", "entity"],
        margin=1.0,
        min_score=4.0,
        guard_disable_regex=compile_guard_disable_regex("counterfactual no-cap amount question"),
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "entity"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected.get("specialized_guard_reason", "") == ""


def test_hybrid_selector_prefers_cap_rule_determination_surface_without_guard() -> None:
    row = {
        "id": "q_or_cap_application",
        "question": "Does the section 3.4 cap apply to App-2026-014's combined bonus, and if so, what is the effective bonus rate?",
        "modes": [
            _mode_with_predicates("source_record_facts_v2", ["bonus_applied", "grant_amount", "rule_cap"], rows=6),
            _mode_with_predicates(
                "source_record",
                ["rule_threshold", "rule_description", "grant_bonus", "determination_status"],
                rows=4,
            ),
            _mode_with_predicates(
                "entity",
                ["rule_condition", "bonus_percentage", "determination_status"],
                rows=3,
                relaxed=True,
            ),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["source_record_facts_v2", "source_record", "entity"],
        margin=1.0,
        min_score=4.0,
        guard_disable_regex=compile_guard_disable_regex("cap-application question"),
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "source_record"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected.get("specialized_guard_reason", "") == ""


def test_hybrid_selector_prefers_pending_reason_surface_without_guard() -> None:
    row = {
        "id": "q_or_pending_reason",
        "question": "Why is App-2026-019 currently pending rather than approved?",
        "modes": [
            _mode_with_predicates(
                "source_record_facts_v2",
                ["determination_status", "verification_pending", "verification_deadline", "rule_threshold"],
                rows=4,
            ),
            _mode_with_predicates(
                "source_record",
                ["determination_reason", "determination_status", "pending_verification", "verification_source"],
                rows=4,
            ),
            _mode_with_predicates(
                "parallel",
                ["final_status", "eligibility_determination", "pending_verification", "applicant_attribute"],
                rows=11,
            ),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["source_record_facts_v2", "source_record", "parallel"],
        margin=1.0,
        min_score=4.0,
        guard_disable_regex=compile_guard_disable_regex("pending-rather-than-approved question"),
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "source_record"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected.get("specialized_guard_reason", "") == ""


def test_hybrid_selector_prefers_application_disposition_status_surface_without_guard() -> None:
    row = {
        "id": "q_or_application_disposition",
        "question": "What is the disposition of App-2026-021?",
        "modes": [
            _mode_with_predicates("source_record_facts_v2", ["determination_status", "denial_ground"], rows=5),
            _mode_with_predicates("entity", ["determination_status", "rule_violated"], rows=2),
            _mode_with_predicates("source_record", ["determination_reason", "determination_status"], rows=2),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["source_record_facts_v2", "entity", "source_record"],
        margin=1.0,
        min_score=4.0,
        guard_disable_regex=compile_guard_disable_regex("application-disposition question"),
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "entity"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected.get("specialized_guard_reason", "") == ""


def test_hybrid_selector_prefers_original_average_surface() -> None:
    row = {
        "id": "q_original_average",
        "question": "What was Okafor-Vance's original average score before the correction?",
        "modes": [
            _mode_with_predicates("cold", ["application_average"], rows=1),
            _mode_with_predicates("source_record", ["measurement_value"], rows=1),
            _mode_with_predicates("archival_row_ledger_v1", ["row_actor", "row_value"], rows=3),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] in {"cold", "source_record"}
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


def test_hybrid_selector_prefers_docket_held_status_surface() -> None:
    row = {
        "id": "q_docket_held",
        "question": "Has the reconsideration docket been held?",
        "modes": [
            _mode_with_predicates("cold", ["event_occurred"], rows=14, relaxed=True),
            _mode_with_predicates("source_record", ["source_document_status"], rows=1),
            _mode_with_predicates("archival_row_ledger_v1", ["row_actor", "row_time", "row_value"], rows=4),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] in {"cold", "source_record"}
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


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
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected.get("specialized_guard_reason", "") == ""
    assert "disabled_guard_reasons" not in selected


def test_hybrid_selector_prefers_exhibit_label_surface_without_guard() -> None:
    row = {
        "id": "q_or_exhibit",
        "question": "Which exhibit is the Magistrate Judge's April 28 memo?",
        "modes": [
            _mode_with_predicates("cold", ["documented_in"], rows=17, relaxed=True),
            _mode_with_predicates(
                "source_record",
                ["source_document_author", "source_document_date", "source_document_type"],
                rows=3,
            ),
            _mode_with_predicates("archival_row_ledger_v1", ["exhibit_label", "row_actor", "row_time"], rows=19),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        guard_disable_regex=compile_guard_disable_regex("exhibit-identification question"),
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] in {"source_record", "archival_row_ledger_v1"}
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


def test_hybrid_selector_prefers_transfer_requirement_without_guard() -> None:
    row = {
        "id": "q_or_transfer_requirement",
        "question": "Per Magistrate Judge Kovacs's memo, what is required for the insurance settlement to transfer title to the wreck?",
        "modes": [
            _mode_with_predicates(
                "cold",
                ["court_order", "insurer_policy", "ownership_of_record", "registry_status"],
                rows=1,
            ),
            _mode_with_predicates("source_record", ["rule_requirement"], rows=4),
            _mode_with_predicates("archival_row_ledger_v1", ["row_value"], rows=103, relaxed=True),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        guard_disable_regex=compile_guard_disable_regex("rule-effect question"),
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "source_record"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


def test_hybrid_selector_prefers_owner_of_record_without_generic_row_volume_guard() -> None:
    row = {
        "id": "q_owner_record",
        "question": "Who is the owner of record of F/V Mara Velasco?",
        "modes": [
            _mode_with_predicates("cold", ["ownership_of_record"], rows=1),
            _mode_with_predicates("source_record", ["source_records"], rows=13, relaxed=True),
            _mode_with_predicates("archival_row_ledger_v1", ["row_value"], rows=7),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        guard_disable_regex=compile_guard_disable_regex("focused semantic surface beats archival row-volume"),
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "cold"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


def test_hybrid_selector_prefers_registry_change_status_without_generic_row_volume_guard() -> None:
    row = {
        "id": "q_registry_change",
        "question": "Per the registry, has the documented owner of F/V Mara Velasco changed since the casualty?",
        "modes": [
            _mode_with_predicates("cold", ["ownership_of_record", "registry_status"], rows=2),
            _mode_with_predicates("source_record", ["status_at", "source_records"], rows=2),
            _mode_with_predicates("archival_row_ledger_v1", ["row_records", "row_value"], rows=10),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        guard_disable_regex=compile_guard_disable_regex("focused semantic surface beats archival row-volume"),
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] in {"cold", "source_record"}
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


def test_hybrid_selector_prefers_position_adjudication_status_without_generic_row_volume_guard() -> None:
    row = {
        "id": "q_position_adjudication",
        "question": "Position A and Position B differ by approximately 220 meters. The packet records two interpretations. Has either interpretation been adjudicated?",
        "modes": [
            _mode_with_predicates("cold", ["court_order", "insurer_policy", "survey_position"], rows=5),
            _mode_with_predicates("source_record", ["status_at", "unresolved_issue"], rows=39),
            _mode_with_predicates("archival_row_ledger_v1", ["row_value"], rows=208),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        guard_disable_regex=compile_guard_disable_regex("focused semantic surface beats archival row-volume"),
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "source_record"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


def test_hybrid_selector_prefers_authoritative_correction_without_generic_row_volume_guard() -> None:
    row = {
        "id": "q_authoritative_correction",
        "question": "The April 5 sonar survey originally listed depth as \"84 feet\" but the erratum corrected it to 84 meters. Which value is currently authoritative, and how was the correction made?",
        "modes": [
            _mode_with_predicates("cold", ["report_version", "survey_depth"], rows=8),
            _mode_with_predicates("source_record", ["measurement_value", "status_at", "supersession"], rows=2),
            _mode_with_predicates("archival_row_ledger_v1", ["row_value"], rows=24),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        guard_disable_regex=compile_guard_disable_regex("focused semantic surface beats archival row-volume"),
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] in {"source_record", "archival_row_ledger_v1"}
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


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
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected.get("specialized_guard_reason", "") == ""


def test_hybrid_selector_prefers_system_log_for_interval_behavior_without_guard() -> None:
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
        guard_disable_regex=compile_guard_disable_regex("interval behavior-plus-cause question"),
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "source_record"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


def test_hybrid_selector_prefers_elapsed_minutes_for_headcount_without_guard() -> None:
    row = {
        "id": "q_school_headcount_elapsed",
        "question": "What was the elapsed time between Bus 2's first short headcount at 2:35 PM and the final confirmed headcount?",
        "modes": [
            _mode_with_predicates("cold", ["headcount_recorded"], rows=8, relaxed=True),
            _mode_with_predicates("source_record", ["system_log_event", "event_attribute", "elapsed_minutes"], rows=3),
            _mode_with_predicates("archival_row_ledger_v1", ["row_time", "row_event", "row_value"], rows=18),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        guard_disable_regex=compile_guard_disable_regex("headcount elapsed-time question"),
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "source_record"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


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
    assert selected.get("specialized_guard_reason", "") == ""


def test_hybrid_selector_prefers_pending_determination_without_guard() -> None:
    row = {
        "id": "q_status_pending_determination",
        "question": "How did the board vote and what is the pending status?",
        "modes": [
            _mode_with_predicates("negative_records", ["negative_record"], rows=12),
            _mode_with_predicates("vote_status", ["pending_determination"], rows=1),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["negative_records", "vote_status"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "vote_status"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected.get("specialized_guard_reason", "") == ""


def test_hybrid_selector_prefers_explicit_decision_status_without_guard() -> None:
    row = {
        "id": "q_status_decision",
        "question": "What decision did the panel reach?",
        "modes": [
            _mode_with_predicates("adjacent_status", ["application_status", "event_occurred"], rows=10),
            _mode_with_predicates("decision_surface", ["panel_decision", "decision_reasoning"], rows=1),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["adjacent_status", "decision_surface"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "decision_surface"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected.get("specialized_guard_reason", "") == ""


def test_hybrid_selector_prefers_current_expiration_without_guard() -> None:
    row = {
        "id": "q_status_adjusted_expiration",
        "question": "What is the adjusted expiration after reinstatement?",
        "modes": [
            _mode_with_predicates("extension_label", ["extension_granted", "valid_to"], rows=8),
            _mode_with_predicates("current_expiration", ["permit_current_expiration"], rows=1),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["extension_label", "current_expiration"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "current_expiration"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected.get("specialized_guard_reason", "") == ""


def test_hybrid_selector_prefers_explicit_priority_without_guard() -> None:
    row = {
        "id": "q_status_priority",
        "question": "What priority was assigned to the review item?",
        "modes": [
            _mode_with_predicates("condition_surface", ["underlying_condition"], rows=8),
            _mode_with_predicates("priority_surface", ["review_priority"], rows=1),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["condition_surface", "priority_surface"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "priority_surface"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected.get("specialized_guard_reason", "") == ""


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
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected.get("specialized_guard_reason", "") == ""


def test_hybrid_selector_prefers_archival_inventory_for_active_lot_count_without_guard() -> None:
    row = {
        "id": "q_or_cap_lots",
        "question": "How many cap lots were in active use in the lab during April 25 - May 1, 2026?",
        "modes": [
            _mode_with_predicates(
                "cold",
                ["analyte_result", "sample_id", "uncertainty_status", "potential_contaminant_source"],
                rows=10,
            ),
            _mode_with_predicates("source_record", ["negative_record", "unresolved_issue", "status_at"], rows=27),
            _mode_with_predicates("archival_row_ledger_v1", ["row_records", "row_time", "row_value"], rows=89),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["cold", "source_record", "archival_row_ledger_v1"],
        margin=1.0,
        min_score=4.0,
        guard_disable_regex=compile_guard_disable_regex("active-lot count question"),
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "archival_row_ledger_v1"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


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


def test_competition_substitute_scorer_phrase_no_longer_has_selector_guard() -> None:
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

    assert override is None


def test_hybrid_selector_prefers_compact_service_role_identity_without_guard() -> None:
    row = {
        "id": "q_role_service_identity",
        "question": "Who served as substitute scorer for the final?",
        "modes": [
            _mode_with_predicates("service_role", ["serves_as"], rows=1),
            _mode_with_predicates("broad_results", ["score_certified_by", "match_result"], rows=12),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["service_role", "broad_results"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "service_role"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected.get("specialized_guard_reason", "") == ""


def test_hybrid_selector_prefers_direct_collector_identity_without_guard() -> None:
    row = {
        "id": "q_role_collector_identity",
        "question": "Who collected the intake specimen?",
        "modes": [
            _mode_with_predicates("status_notes", ["status_note", "record_status"], rows=18),
            _mode_with_predicates("collector_surface", ["collector"], rows=1),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["status_notes", "collector_surface"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "collector_surface"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected.get("specialized_guard_reason", "") == ""


def test_hybrid_selector_prefers_direct_role_identity_without_guard() -> None:
    row = {
        "id": "q_role_director_identity",
        "question": "Who is the event director?",
        "modes": [
            _mode_with_predicates("meeting_rows", ["meeting_attendance", "ruling_made_by"], rows=10),
            _mode_with_predicates("role_surface", ["person_role"], rows=1),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["meeting_rows", "role_surface"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "role_surface"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected.get("specialized_guard_reason", "") == ""


def test_hybrid_selector_prefers_role_authority_identity_without_guard() -> None:
    row = {
        "id": "q_role_authority_identity",
        "question": "Who is the official authorized to approve the request?",
        "modes": [
            _mode_with_predicates("action_volume", ["official_action"], rows=14),
            _mode_with_predicates("authority_surface", ["person_name", "role_authority"], rows=1),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["action_volume", "authority_surface"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "authority_surface"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected.get("specialized_guard_reason", "") == ""


def test_hybrid_selector_prefers_direct_driver_identity_without_guard() -> None:
    row = {
        "id": "q_role_driver_identity",
        "question": "Who drove the transport van?",
        "modes": [
            _mode_with_predicates("row_values", ["row_value"], rows=20),
            _mode_with_predicates("driver_surface", ["driver_of"], rows=1),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["row_values", "driver_surface"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "driver_surface"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected.get("specialized_guard_reason", "") == ""


def test_hybrid_selector_prefers_superlative_age_identity_without_guard() -> None:
    row = {
        "id": "q_role_superlative_identity",
        "question": "Who is the youngest registered member?",
        "modes": [
            _mode_with_predicates("membership_rows", ["group_member"], rows=24),
            _mode_with_predicates("age_surface", ["person_age", "person_identity"], rows=1),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["membership_rows", "age_surface"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "age_surface"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected.get("specialized_guard_reason", "") == ""


def test_hybrid_selector_prefers_source_authority_for_principal_identity_without_guard() -> None:
    row = {
        "id": "q_role_principal_source_authority",
        "question": "Who is the school principal recorded by the statement of authority?",
        "modes": [
            _mode_with_predicates("roster_volume", ["person_role", "group_member"], rows=18),
            _mode_with_predicates("source_authority", ["source_document_author", "statement_claim"], rows=1),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["roster_volume", "source_authority"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "source_authority"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected.get("specialized_guard_reason", "") == ""


def test_hybrid_selector_prefers_statement_event_supervision_without_guard() -> None:
    row = {
        "id": "q_role_supervision_statement",
        "question": "Who supervised the student location according to the incident statement?",
        "modes": [
            _mode_with_predicates("role_roster", ["person_role", "group_member"], rows=20),
            _mode_with_predicates("statement_event", ["statement_claim", "event_attribute"], rows=2),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["role_roster", "statement_event"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "statement_event"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected.get("specialized_guard_reason", "") == ""


def test_hybrid_selector_prefers_reinstatement_role_history_without_guard() -> None:
    row = {
        "id": "q_role_reinstated",
        "question": "Who was reinstated after the review?",
        "modes": [
            _mode_with_predicates("current_role", ["person_role"], rows=12),
            _mode_with_predicates("role_history", ["holds_role"], rows=1),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["current_role", "role_history"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "role_history"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected.get("specialized_guard_reason", "") == ""


def test_hybrid_selector_prefers_contract_authority_without_guard() -> None:
    row = {
        "id": "q_role_contract_authority",
        "question": "Does the contract remain valid if the acting officer signed it?",
        "modes": [
            _mode_with_predicates("entity_rows", ["entity_name", "ownership_status"], rows=16),
            _mode_with_predicates("authority_surface", ["authority_source", "acting_role_holder"], rows=1),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["entity_rows", "authority_surface"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "authority_surface"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected.get("specialized_guard_reason", "") == ""


def test_hybrid_selector_prefers_guardianship_residence_condition_without_guard() -> None:
    row = {
        "id": "q_role_guardianship_condition",
        "question": "Is the guardianship valid after retroactive residence is considered?",
        "modes": [
            _mode_with_predicates("status_only", ["guardianship_status"], rows=9),
            _mode_with_predicates("residence_rule", ["resides_at", "rule_condition"], rows=1),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["status_only", "residence_rule"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "residence_rule"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected.get("specialized_guard_reason", "") == ""


def test_attendance_count_phrase_no_longer_has_selector_guard() -> None:
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

    assert override is None


def test_hybrid_selector_prefers_explicit_session_count_without_guard() -> None:
    row = {
        "id": "q_attendance_count_general",
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
            _mode_with_predicates("station_registry", ["session_attendance_count"], rows=1),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["interval", "station_registry"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda *, row, mode_labels: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "station_registry"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 6.0


def test_structural_selector_prefers_session_count_on_unlike_briefing_row() -> None:
    row = {
        "id": "q_attendance_count_unlike",
        "question": "How many people checked into the morning safety briefing?",
        "modes": [
            _mode_with_predicates("participant_roster", ["person_role", "group_member"], rows=34, relaxed=True),
            _mode_with_predicates("briefing_register", ["session_attendance_count"], rows=1),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["participant_roster", "briefing_register"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda *, row, mode_labels: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "briefing_register"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 6.0


def test_hybrid_selector_prefers_conveyed_item_count_without_fixture_guard() -> None:
    row = {
        "id": "q_conveyed_item_count_general",
        "question": "How many items did the deed convey?",
        "modes": [
            _mode_with_predicates("receipt_volume", ["receipt_row", "source_record_row"], rows=18, relaxed=True),
            _mode_with_predicates("conveyed_items", ["conveyed_item"], rows=3),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["receipt_volume", "conveyed_items"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda *, row, mode_labels: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "conveyed_items"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"


def test_structural_selector_prefers_conveyed_item_count_on_unlike_row() -> None:
    row = {
        "id": "q_conveyed_item_count_unlike",
        "question": "How many assets did the transfer agreement convey?",
        "modes": [
            _mode_with_predicates("receipt_volume", ["receipt_row", "source_record_row"], rows=21, relaxed=True),
            _mode_with_predicates("transferred_assets", ["conveyed_item", "item_conveyed"], rows=4),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["receipt_volume", "transferred_assets"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda *, row, mode_labels: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "transferred_assets"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 3.5


def test_deed_item_count_phrase_no_longer_has_selector_guard() -> None:
    row = {
        "id": "q_conveyed_item_count_retired_guard",
        "question": "How many distinct items did the supplementary deed convey?",
        "modes": [
            _mode_with_predicates("receipt_volume", ["receipt_row", "source_record_row"], rows=18, relaxed=True),
            _mode_with_predicates("conveyed_items", ["conveyed_item"], rows=3),
        ],
    }
    scored = structural_mode_scores(row=row, mode_labels=["receipt_volume", "conveyed_items"])

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=scored,
        mode_labels=["receipt_volume", "conveyed_items"],
        structural_choice="receipt_volume",
    )

    assert override is None


def test_final_attendance_student_count_guard_is_retired() -> None:
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

    assert override is None


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

    assert override is None


def test_hybrid_selector_prefers_station_supervisor_without_guard() -> None:
    row = {
        "id": "q_station_supervisor_unlike",
        "question": "Who supervised Station C during the evening inspection?",
        "modes": [
            _mode_with_predicates("standing_group", ["supervision_assignment"], rows=6),
            _mode_with_predicates("station_registry", ["station_supervisor"], rows=1),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["standing_group", "station_registry"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "station_registry"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected.get("specialized_guard_reason", "") == ""


def test_station_arrival_time_focus_prefers_event_timestamp_surface() -> None:
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

    selected = hybrid_selector(
        row=row,
        mode_labels=["roster", "interval"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda *, row, mode_labels: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "interval"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 8.0


def test_hybrid_selector_prefers_station_arrival_event_timestamp_with_guard_disabled() -> None:
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

    selected = hybrid_selector(
        row=row,
        mode_labels=["roster", "interval"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda *, row, mode_labels: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "interval"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert "specialized_guard_reason" not in selected


def test_hybrid_selector_prefers_group_swap_for_yellow_to_blue_with_guard_disabled() -> None:
    row = {
        "id": "q013",
        "question": "Which Yellow Group students joined Blue Group on Day 2?",
        "modes": [
            _mode_with_predicates("interval_membership", ["group_membership"], rows=38, relaxed=True),
            _mode_with_predicates(
                "roster_swap",
                ["group_member", "roster_state_support", "group_swap"],
                rows=6,
                relaxed=True,
            ),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["interval_membership", "roster_swap"],
        margin=1.0,
        min_score=4.0,
        guard_disable_regex=compile_guard_disable_regex("yellow-to-blue reassignment"),
        fallback_selector=lambda *, row, mode_labels: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "roster_swap"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert "specialized_guard_reason" not in selected


def test_yellow_to_blue_phrase_no_longer_has_selector_guard() -> None:
    row = {
        "id": "q_yellow_to_blue_guard_retired",
        "question": "Which Yellow Group students joined Blue Group on Day 2?",
        "modes": [
            _mode_with_predicates("interval_membership", ["group_membership"], rows=38),
            _mode_with_predicates("transition_membership", ["event_occurs", "group_membership"], rows=6),
        ],
    }
    labels = ["interval_membership", "transition_membership"]

    override = structural_specialized_answer_surface_override(
        row=row,
        scored=structural_mode_scores(row=row, mode_labels=labels),
        mode_labels=labels,
        structural_choice="interval_membership",
    )

    assert override is None


def test_structural_selector_prefers_membership_transition_on_unlike_roster_row() -> None:
    row = {
        "id": "q_unlike_membership_transition",
        "question": "Which training-team members were reassigned to the audit team after the roster update?",
        "modes": [
            _mode_with_predicates("interval_membership", ["group_membership"], rows=24),
            _mode_with_predicates(
                "transition_membership",
                ["assignment_change", "group_membership", "roster_state_support"],
                rows=4,
            ),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["interval_membership", "transition_membership"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda *, row, mode_labels: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "transition_membership"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected["evidence_quality_by_mode"][0]["focus_bonus"] == 7.0


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

    selected = hybrid_selector(
        row=row,
        mode_labels=["station_role", "station_helper"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "station_role"},
    )

    assert selected["selected_mode"] == "station_helper"
    assert selected.get("specialized_guard_reason", "") == ""


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

    selected = hybrid_selector(
        row=row,
        mode_labels=["station_registry", "station_role"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "station_registry"},
    )

    assert selected["selected_mode"] == "station_role"
    assert selected.get("specialized_guard_reason", "") == ""


def test_hybrid_selector_prefers_temporary_availability_authority_surface_without_guard() -> None:
    row = {
        "id": "q_temporary_availability",
        "question": "Was the chair available for the special meeting?",
        "modes": [
            _mode_with_predicates("role_list", ["board_member"], rows=9),
            _mode_with_predicates("attendance_authority", ["meeting_attendance", "authority_transfer"], rows=2),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["role_list", "attendance_authority"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "attendance_authority"
    assert selected.get("specialized_guard_reason", "") == ""


def test_hybrid_selector_prefers_temporary_supervisor_absence_surface_without_guard() -> None:
    row = {
        "id": "q_temporary_supervisor_absence",
        "question": "What was the supervisor absence status during the drill?",
        "modes": [
            _mode_with_predicates("role_roster", ["person_role"], rows=7),
            _mode_with_predicates("absence_event", ["location_change", "supervises", "medical_event"], rows=2),
        ],
    }

    selected = hybrid_selector(
        row=row,
        mode_labels=["role_roster", "absence_event"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "absence_event"
    assert selected.get("specialized_guard_reason", "") == ""


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

    assert override is None

    selected = hybrid_selector(
        row=row,
        mode_labels=labels,
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
    )

    assert selected["selected_mode"] == "admin"
    assert selected["selection_source"] == "hybrid_structural"
    assert selected["hybrid_decision"] == "structural_confident"
    assert selected.get("specialized_guard_reason", "") == ""


def test_hybrid_selector_prefers_direct_policy_input_surfaces_without_guards() -> None:
    cases = [
        (
            "permit_issued",
            "Was the permit operative on the event date?",
            _mode_with_predicates("broad", ["source_document_status"], rows=10),
            _mode_with_predicates("focused", ["permit_issued", "document_identifier"], rows=1),
        ),
        (
            "remedy_issue",
            "Was the replacement requirement imposed?",
            _mode_with_predicates("broad", ["remedy_label"], rows=10),
            _mode_with_predicates("focused", ["unresolved_issue"], rows=1),
        ),
        (
            "hearing_event",
            "Has the appeal hearing been held?",
            _mode_with_predicates("broad", ["scheduled_date"], rows=10),
            _mode_with_predicates("focused", ["log_event", "unresolved_issue"], rows=1),
        ),
        (
            "roster_record",
            "Who was on the roster of record?",
            _mode_with_predicates("broad", ["supersession", "source_document_status"], rows=10),
            _mode_with_predicates("focused", ["assigned_to", "person_role"], rows=1),
        ),
        (
            "governing_draft",
            "Does the draft plan govern the action?",
            _mode_with_predicates("broad", ["document_identifier"], rows=10),
            _mode_with_predicates("focused", ["source_document_status", "supersession"], rows=1),
        ),
        (
            "parent_letter",
            "Did the parent letter make a substantive determination?",
            _mode_with_predicates("broad", ["source_document"], rows=10),
            _mode_with_predicates("focused", ["parent_letter", "review_scheduled_for"], rows=1),
        ),
        (
            "zoning",
            "What zoning designation applies to the property?",
            _mode_with_predicates("broad", ["zoning_definition"], rows=10),
            _mode_with_predicates("focused", ["parcel_zoning"], rows=1),
        ),
        (
            "buildout",
            "What build-out timeline applies?",
            _mode_with_predicates("broad", ["permit_expiry_status"], rows=10),
            _mode_with_predicates("focused", ["site_measure", "draft_condition"], rows=1),
        ),
        (
            "dimensions",
            "Which dimensional standards apply?",
            _mode_with_predicates("broad", ["compliance_status"], rows=10),
            _mode_with_predicates("focused", ["staff_finding", "site_measure"], rows=1),
        ),
        (
            "lab_status",
            "What was the lab result for the lot?",
            _mode_with_predicates("broad", ["lab_result"], rows=10),
            _mode_with_predicates("focused", ["lab_result", "lot_status"], rows=1),
        ),
    ]

    for row_id, question, broad_mode, focused_mode in cases:
        row = {"id": row_id, "question": question, "modes": [broad_mode, focused_mode]}

        selected = hybrid_selector(
            row=row,
            mode_labels=["broad", "focused"],
            margin=1.0,
            min_score=4.0,
            fallback_selector=lambda **_kwargs: (_ for _ in ()).throw(AssertionError("fallback called")),
        )

        assert selected["selected_mode"] == "focused", row_id
        assert selected["selection_source"] == "hybrid_structural", row_id
        assert selected["hybrid_decision"] == "structural_confident", row_id
        assert selected.get("specialized_guard_reason", "") == "", row_id


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

    selected = hybrid_selector(
        row=row,
        mode_labels=["baseline", "admin"],
        margin=1.0,
        min_score=4.0,
        fallback_selector=lambda **_kwargs: {"selected_mode": "admin"},
    )

    assert selected["selected_mode"] == "baseline"
    assert selected.get("specialized_guard_reason", "") == ""


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
