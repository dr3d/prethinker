from scripts.run_support_acquisition_pass import _support_acquisition_profile


def body_fact_signatures() -> set[str]:
    profile = _support_acquisition_profile({}, lens="body_fact")
    return {
        str(item.get("signature", ""))
        for item in profile.get("candidate_predicates", [])
        if isinstance(item, dict)
    }


def test_body_fact_lens_exposes_required_condition_predicate() -> None:
    assert "required_condition/2" in body_fact_signatures()
