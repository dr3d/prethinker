import json
import sys

from scripts import select_qa_mode_without_oracle
from scripts.select_qa_mode_without_oracle import (
    call_selector,
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
    structural_volume_trap_reason,
)


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
