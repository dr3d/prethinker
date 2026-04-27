from __future__ import annotations

from scripts.run_profile_bootstrap_loop import summarize_loop


def test_profile_bootstrap_loop_summary_scores_core_counts() -> None:
    rows = [
        {
            "parsed_ok": True,
            "out_of_palette_skip_count": 0,
            "must_not_write_violations": [],
            "expected_positive_refs": ["approved_by/2"],
            "expected_ref_hits": ["approved_by/2"],
            "admitted_count": 1,
        },
        {
            "parsed_ok": True,
            "out_of_palette_skip_count": 1,
            "must_not_write_violations": ["waiver(obligation,lender)"],
            "expected_positive_refs": ["obligation/3"],
            "expected_ref_hits": [],
            "admitted_count": 1,
        },
    ]

    summary = summarize_loop(rows, bootstrap_score={"rough_score": 1.0})

    assert summary == {
        "cases": 2,
        "parsed_ok": 2,
        "zero_out_of_palette_skip_cases": 1,
        "zero_must_not_violation_cases": 1,
        "expected_ref_hit_cases": 1,
        "admitted_total": 2,
        "rough_score": 0.625,
        "bootstrap_rough_score": 1.0,
    }
