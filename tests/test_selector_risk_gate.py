from scripts.plan_selector_risk_gate import build_report, render_markdown


def _selector_run(label: str, policy: str, rows: list[dict]) -> dict:
    return {
        "label": label,
        "path": f"{label}.json",
        "selection_policy": policy,
        "summary": {},
        "rows": rows,
    }


def _row(row_id: str, selected_verdict: str, *, selected_mode: str = "baseline", best_verdict: str = "exact") -> dict:
    return {
        "id": row_id,
        "question": f"Question {row_id}?",
        "selected_mode": selected_mode,
        "selected_verdict": selected_verdict,
        "best_verdict": best_verdict,
        "best_labels": [selected_mode],
    }


def _transfer(candidate_policy: str, *, candidate_exact: int, candidate_miss: int, alt_exact: int, alt_miss: int) -> dict:
    return {
        "label": "transfer",
        "policy_summaries": [
            {
                "selection_policy": candidate_policy,
                "selected_exact": candidate_exact,
                "selected_miss": candidate_miss,
            },
            {
                "selection_policy": "baseline_policy",
                "selected_exact": alt_exact,
                "selected_miss": alt_miss,
            },
        ],
    }


def test_risk_gate_marks_supported_candidate_rescue_safe() -> None:
    report = build_report(
        baseline=_selector_run("baseline", "baseline_policy", [_row("q001", "partial")]),
        candidate=_selector_run("candidate", "guarded_activation", [_row("q001", "exact", selected_mode="candidate")]),
        transfer_reports=[
            _transfer("guarded_activation", candidate_exact=10, candidate_miss=0, alt_exact=9, alt_miss=1)
        ],
    )

    assert report["summary"]["candidate_transfer_status"] == "supported"
    assert report["summary"]["safe_activation_target_count"] == 1
    assert report["rows"][0]["category"] == "safe_activation_target"


def test_risk_gate_keeps_weak_transfer_rescue_as_calibration() -> None:
    report = build_report(
        baseline=_selector_run("baseline", "baseline_policy", [_row("q001", "partial")]),
        candidate=_selector_run("candidate", "guarded_activation", [_row("q001", "exact", selected_mode="candidate")]),
        transfer_reports=[
            _transfer("guarded_activation", candidate_exact=8, candidate_miss=3, alt_exact=9, alt_miss=1)
        ],
    )

    assert report["summary"]["candidate_transfer_status"] == "weak"
    assert report["summary"]["safe_activation_target_count"] == 0
    assert report["summary"]["calibration_activation_target_count"] == 1
    assert report["summary"]["global_recommendation"] == "do_not_promote_candidate_policy"


def test_risk_gate_protects_baseline_exact_regression() -> None:
    report = build_report(
        baseline=_selector_run("baseline", "baseline_policy", [_row("q001", "exact")]),
        candidate=_selector_run("candidate", "guarded_activation", [_row("q001", "partial", selected_mode="candidate")]),
        transfer_reports=[
            _transfer("guarded_activation", candidate_exact=10, candidate_miss=0, alt_exact=9, alt_miss=1)
        ],
    )

    assert report["summary"]["protect_baseline_target_count"] == 1
    assert report["summary"]["baseline_exact_regression_count"] == 1
    assert report["rows"][0]["category"] == "protect_baseline_target"


def test_risk_gate_marks_rows_without_exact_mode_for_compile_repair() -> None:
    report = build_report(
        baseline=_selector_run("baseline", "baseline_policy", [_row("q001", "partial", best_verdict="partial")]),
        candidate=_selector_run("candidate", "guarded_activation", [_row("q001", "partial", best_verdict="partial")]),
        transfer_reports=[
            _transfer("guarded_activation", candidate_exact=10, candidate_miss=0, alt_exact=9, alt_miss=1)
        ],
    )
    markdown = render_markdown(report)

    assert report["summary"]["needs_compile_repair_count"] == 1
    assert report["rows"][0]["category"] == "needs_compile_repair"
    assert "Selector Risk-Gate Plan" in markdown
    assert "does not read source prose" in markdown

