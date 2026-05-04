from scripts.select_qa_mode_without_oracle import structural_selector


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
