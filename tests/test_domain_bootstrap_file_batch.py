from scripts.run_domain_bootstrap_file_batch import (
    _extract_compile_summary,
    _quality_gate_result,
    _render_md,
    _summarize,
)


def test_compile_batch_summary_extracts_quality_gate_signals() -> None:
    summary = _extract_compile_summary(
        {
            "parsed_ok": True,
            "parsed": {"candidate_predicates": [{"signature": "record_status/2"}]},
            "source_compile": {"admitted_count": 9, "skipped_count": 1},
            "score": {
                "rough_score": 0.861,
                "risk_count": 3,
                "repeated_structure_count": 1,
                "repeated_structure_id_only_record_refs": ["record_id/1"],
                "repeated_structure_role_mismatch_refs": ["record_status/2"],
                "frontier_unknown_positive_predicate_count": 0,
                "frontier_unknown_positive_predicate_refs": [],
                "generic_predicate_count": 0,
            },
        }
    )

    assert summary["rough_score"] == 0.861
    assert summary["risk_count"] == 3
    assert summary["repeated_structure_id_only_record_refs"] == ["record_id/1"]
    assert summary["frontier_unknown_positive_predicate_count"] == 0


def test_compile_quality_gate_passes_accepted_draw_shape() -> None:
    result = {
        "fixture": "fixture_a",
        "returncode": 0,
        "compile_json": "compile.json",
        "summary": {
            "parsed_ok": True,
            "rough_score": 0.833,
            "risk_count": 5,
            "candidate_predicates": 18,
            "compile_admitted": 86,
            "compile_skipped": 52,
        },
    }

    gate = _quality_gate_result(result, min_rough_score=0.775, max_risk_count=5)

    assert gate["passed"] is True
    assert gate["decision"] == "pass"
    assert gate["compile_skipped_share"] == 0.3768


def test_compile_quality_gate_holds_high_risk_draw() -> None:
    result = {
        "fixture": "fixture_b",
        "returncode": 0,
        "compile_json": "compile.json",
        "summary": {
            "parsed_ok": True,
            "rough_score": 0.778,
            "risk_count": 6,
            "candidate_predicates": 30,
            "compile_admitted": 176,
            "compile_skipped": 23,
        },
    }

    gate = _quality_gate_result(result, min_rough_score=0.775, max_risk_count=5)

    assert gate["passed"] is False
    assert gate["decision"] == "hold"
    assert gate["reasons"] == ["risk_count>5"]


def test_compile_batch_quality_gate_renders_markdown() -> None:
    summary = _summarize(
        [
            {
                "fixture": "fixture_a",
                "returncode": 0,
                "compile_json": "a.json",
                "summary": {
                    "parsed_ok": True,
                    "rough_score": 0.9,
                    "risk_count": 2,
                    "candidate_predicates": 10,
                    "compile_admitted": 20,
                    "compile_skipped": 0,
                },
            },
            {
                "fixture": "fixture_b",
                "returncode": 0,
                "compile_json": "b.json",
                "summary": {
                    "parsed_ok": True,
                    "rough_score": 0.7,
                    "risk_count": 2,
                    "candidate_predicates": 10,
                    "compile_admitted": 20,
                    "compile_skipped": 0,
                },
            },
        ],
        lanes=2,
        base_timeout=900,
        effective_timeout=1800,
        quality_gate=True,
        quality_min_rough_score=0.775,
        quality_max_risk_count=5,
    )

    assert summary["quality_gate"]["passed"] is False
    assert summary["quality_gate"]["hold_count"] == 1
    markdown = _render_md(summary)
    assert "## Compile Quality Gate" in markdown
    assert "rough_score<0.775" in markdown
