from scripts.select_compile_candidate import select_candidate


def _comparison(
    *,
    path: str,
    run: str,
    gate: str,
    ratio: float,
    family_regressions: int,
    contract_regressions: int,
    lost_predicates: int,
) -> dict:
    return {
        "_comparison_path": path,
        "comparisons": [
            {
                "fixture": "fixture_a",
                "candidate_run": run,
                "gate_status": gate,
                "direct_fact_ratio": ratio,
                "family_regressions": [{}] * family_regressions,
                "contract_regressions": [{}] * contract_regressions,
                "lost_predicates": ["p"] * lost_predicates,
            }
        ],
    }


def test_select_compile_candidate_prefers_qa_eligible() -> None:
    payload = select_candidate(
        [
            _comparison(
                path="candidate_a.json",
                run="candidate_a",
                gate="regression",
                ratio=0.99,
                family_regressions=0,
                contract_regressions=0,
                lost_predicates=1,
            ),
            _comparison(
                path="candidate_b.json",
                run="candidate_b",
                gate="pass",
                ratio=0.90,
                family_regressions=0,
                contract_regressions=0,
                lost_predicates=3,
            ),
        ]
    )

    assert payload["selected"]["candidate_run"] == "candidate_b"
    assert payload["selected"]["qa_eligible"] is True


def test_select_compile_candidate_ranks_regressions_by_damage() -> None:
    payload = select_candidate(
        [
            _comparison(
                path="candidate_a.json",
                run="candidate_a",
                gate="regression",
                ratio=0.50,
                family_regressions=2,
                contract_regressions=1,
                lost_predicates=10,
            ),
            _comparison(
                path="candidate_b.json",
                run="candidate_b",
                gate="regression",
                ratio=0.82,
                family_regressions=0,
                contract_regressions=0,
                lost_predicates=5,
            ),
        ]
    )

    assert payload["selected"]["candidate_run"] == "candidate_b"
    assert payload["selected"]["qa_eligible"] is False
