from scripts.select_profile_registry_for_prestamp import select_registry


def test_selector_rejects_empty_registry() -> None:
    report = select_registry(
        {"fixture": "fixture_a", "predicates": []},
        {"compiles": [], "summary": {}},
    )

    assert report["decision"] == "hold"
    assert "empty_registry" in report["reasons"]


def test_selector_rejects_broad_only_registry() -> None:
    report = select_registry(
        {"fixture": "fixture_a", "predicates": [{"signature": "source_detail/4"}]},
        {
            "compiles": [{"prior_missing_signatures": [], "prior_zero_yield_signatures": []}],
            "summary": {"all_prior_delivered_compile_count": 1},
        },
    )

    assert report["decision"] == "hold"
    assert "broad_only_registry" in report["reasons"]


def test_selector_rejects_zero_yield_history() -> None:
    report = select_registry(
        {"fixture": "fixture_a", "predicates": [{"signature": "lab_result/4"}]},
        {
            "compiles": [{"prior_missing_signatures": [], "prior_zero_yield_signatures": ["lab_result/4"]}],
            "summary": {"all_prior_delivered_compile_count": 1},
        },
    )

    assert report["decision"] == "hold"
    assert "zero_yield_compile_share>0" in report["reasons"]


def test_selector_accepts_delivered_nonbroad_registry() -> None:
    report = select_registry(
        {"fixture": "fixture_a", "predicates": [{"signature": "lab_result/4"}]},
        {
            "compiles": [
                {"prior_missing_signatures": [], "prior_zero_yield_signatures": []},
                {"prior_missing_signatures": ["lab_result/4"], "prior_zero_yield_signatures": []},
            ],
            "summary": {"all_prior_delivered_compile_count": 1},
        },
    )

    assert report["decision"] == "pass"
    assert report["all_prior_delivered_share"] == 0.5
