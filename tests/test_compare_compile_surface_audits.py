from scripts.compare_compile_surface_audits import compare_audits


def _audit_report(
    *,
    fixture: str = "fixture_a",
    direct_count: int,
    family_status: str,
    contract_status: str,
    predicates: list[str],
) -> dict:
    return {
        "reports": [
            {
                "fixture": fixture,
                "run": "run",
                "direct_fact_count": direct_count,
                "direct_predicates": predicates,
                "families": [{"family": "event_backbone_unit_surface", "status": family_status}],
                "relation_contracts": [{"contract": "participant_statement_status_contract", "status": contract_status}],
            }
        ]
    }


def test_compare_compile_surface_audits_flags_regressions() -> None:
    baseline = _audit_report(
        direct_count=100,
        family_status="pass",
        contract_status="pass",
        predicates=["event_happened", "vote_cast", "public_comment"],
    )
    candidate = _audit_report(
        direct_count=70,
        family_status="partial",
        contract_status="missing_status_companion",
        predicates=["public_comment"],
    )

    payload = compare_audits(baseline, candidate, min_direct_fact_ratio=0.85)

    row = payload["comparisons"][0]
    assert row["gate_status"] == "regression"
    assert row["direct_fact_regression"] is True
    assert row["family_regressions"] == [
        {
            "family": "event_backbone_unit_surface",
            "baseline_status": "pass",
            "candidate_status": "partial",
        }
    ]
    assert row["contract_regressions"] == [
        {
            "contract": "participant_statement_status_contract",
            "baseline_status": "pass",
            "candidate_status": "missing_status_companion",
        }
    ]
    assert row["lost_predicates"] == ["event_happened", "vote_cast"]


def test_compare_compile_surface_audits_passes_non_regression() -> None:
    baseline = _audit_report(
        direct_count=100,
        family_status="partial",
        contract_status="missing_status_companion",
        predicates=["event_happened"],
    )
    candidate = _audit_report(
        direct_count=95,
        family_status="pass",
        contract_status="pass",
        predicates=["event_happened", "participant_statement"],
    )

    payload = compare_audits(baseline, candidate, min_direct_fact_ratio=0.85)

    row = payload["comparisons"][0]
    assert row["gate_status"] == "pass"
    assert row["direct_fact_regression"] is False
    assert row["family_regressions"] == []
    assert row["contract_regressions"] == []
