from scripts.select_qa_mode_without_oracle import hybrid_selector, structural_selector


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
    assert selected["structural_uncertainty_reasons"]


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
