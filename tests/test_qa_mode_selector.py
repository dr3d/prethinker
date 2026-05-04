import json

from scripts import select_qa_mode_without_oracle
from scripts.select_qa_mode_without_oracle import (
    call_selector,
    hybrid_selector,
    protected_selector,
    score_selection,
    structural_selector,
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
