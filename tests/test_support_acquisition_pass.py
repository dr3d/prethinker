from scripts.run_support_acquisition_pass import (
    _support_acquisition_profile,
    _support_guidance_context,
    _support_system_prompt,
)


def body_fact_signatures() -> set[str]:
    profile = _support_acquisition_profile({}, lens="body_fact")
    return {
        str(item.get("signature", ""))
        for item in profile.get("candidate_predicates", [])
        if isinstance(item, dict)
    }


def test_body_fact_lens_exposes_required_condition_predicate() -> None:
    assert "required_condition/2" in body_fact_signatures()


def test_body_fact_guidance_does_not_ban_allowed_supported_vote_rows() -> None:
    guidance = "\n".join(_support_guidance_context(lens="body_fact"))

    assert "support_reason/2" in guidance
    assert "supported/2" in guidance
    assert "Do not treat allowed vote predicates such as supported/2 as banned" in guidance
    assert "explicit instance rows" in guidance


def test_body_fact_system_prompt_mentions_body_facts_not_rationales() -> None:
    prompt = _support_system_prompt(lens="body_fact")

    assert "body facts" in prompt
    assert "rationale/effect/tradeoff" not in prompt
