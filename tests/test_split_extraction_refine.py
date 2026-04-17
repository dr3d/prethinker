from kb_pipeline import (
    _apply_predicate_name_sanity_guard,
    _apply_registry_fact_salvage_guard,
    _heuristic_route,
    _looks_blocksworld_state_description,
    _refine_logic_only_payload,
)


def test_refine_logic_only_payload_expands_multi_fact_logic_string():
    core = {
        "intent": "assert_fact",
        "logic_string": "on(a, b). clear(a). handempty.",
        "confidence": {"overall": 0.9, "intent": 0.95, "logic": 0.9},
        "ambiguities": [],
        "needs_clarification": False,
    }
    refined = _refine_logic_only_payload(core, "assert_fact", utterance="A is on B and A is clear and hand is empty.")
    assert isinstance(refined, dict)
    assert refined["intent"] == "assert_fact"
    assert refined["facts"] == ["on(a, b).", "clear(a).", "handempty."]
    assert refined["logic_string"] == "on(a, b).\nclear(a).\nhandempty."


def test_refine_logic_only_payload_keeps_single_fact():
    core = {
        "intent": "assert_fact",
        "logic_string": "holding(a).",
        "confidence": {"overall": 0.9, "intent": 0.95, "logic": 0.9},
        "ambiguities": [],
        "needs_clarification": False,
    }
    refined = _refine_logic_only_payload(core, "assert_fact", utterance="The arm is holding A.")
    assert isinstance(refined, dict)
    assert refined["facts"] == ["holding(a)."]
    assert refined["logic_string"] == "holding(a)."


def test_registry_fact_salvage_guard_drops_unknown_wrappers():
    parsed = {
        "intent": "assert_fact",
        "logic_string": "clear(b1).\ngoal(holding(b1)).",
        "facts": ["clear(b1).", "goal(holding(b1))."],
        "components": {"atoms": ["b1"], "variables": [], "predicates": ["clear", "goal"]},
        "ambiguities": [],
    }
    out, events = _apply_registry_fact_salvage_guard(
        parsed,
        allowed_signatures={"clear/1", "holding/1"},
        strict_registry=True,
    )
    assert out["facts"] == ["clear(b1)."]
    assert out["logic_string"] == "clear(b1)."
    assert events


def test_registry_fact_salvage_guard_requires_kept_subset():
    parsed = {
        "intent": "assert_fact",
        "logic_string": "goal(holding(b1)).\nstate(b1).",
        "facts": ["goal(holding(b1)).", "state(b1)."],
        "components": {"atoms": ["b1"], "variables": [], "predicates": ["goal", "state"]},
        "ambiguities": [],
    }
    out, events = _apply_registry_fact_salvage_guard(
        parsed,
        allowed_signatures={"clear/1", "holding/1"},
        strict_registry=True,
    )
    assert out == parsed
    assert events == []


def test_predicate_name_sanity_guard_rewrites_is_a_phrase_to_unary_fact():
    parsed = {
        "intent": "assert_fact",
        "logic_string": "go_live_is_a_task(go_live).",
        "facts": ["go_live_is_a_task(go_live)."],
        "rules": [],
        "queries": [],
        "components": {"atoms": ["go_live"], "variables": [], "predicates": ["go_live_is_a_task"]},
        "ambiguities": [],
        "rationale": "",
    }
    out, events = _apply_predicate_name_sanity_guard(
        parsed,
        allowed_signatures={"task/1"},
        strict_registry=True,
    )
    assert out["facts"] == ["task(go_live)."]
    assert out["logic_string"] == "task(go_live)."
    assert out["components"]["predicates"] == ["task"]
    assert events


def test_looks_blocksworld_state_description_positive():
    text = (
        "You have 3 blocks. Your arm is empty. b2 is on b1. "
        "b1 is on the table. b2 is clear. Your goal is to have the following."
    )
    assert _looks_blocksworld_state_description(text)


def test_looks_blocksworld_state_description_negative():
    text = "Please summarize this article about distributed systems."
    assert not _looks_blocksworld_state_description(text)


def test_heuristic_route_keeps_longform_story_blob_on_fact_path():
    text = (
        "The Observatory Residency at Pineglass Ridge\n\n"
        "In January 2022, Pineglass Ridge Field Station stood above Lake Orin and served a small residency program. "
        "Celeste Rowan used an office in Birch Lodge and shared the rear suite with her daughter Pia Rowan on weekends. "
        "Arun Dev lived in the apartment inside North Dome, Lena Ortiz served in the Map Vault, and Theo Marsh lived in South Cabin with his spouse Mara and their son Eli.\n\n"
        "Two governance documents shaped later events. The observatory covenant said that if the curator was absent for more than thirty consecutive days, the deputy curator automatically became acting curator until the board voted otherwise. "
        "The drone could remain assigned to the mapping program only if its annual certification was filed by September 30. "
        "If certification lapsed, title to Kestrel reverted immediately to the station.\n\n"
        "In September 2024, Selene Park spent thirty-three days in Harbor City after Noor Aziz underwent surgery and needed support. "
        "On day thirty-one of Selene's absence, the covenant made Noor Aziz acting curator. "
        "When Selene returned, she accepted the approvals as valid, and by February 2025 the board determined that Kestrel belonged to Pineglass Ridge Field Station."
    )
    assert _heuristic_route(text) == "assert_fact"
    flat_text = " ".join([text.replace("\n\n", " ")] * 2)
    assert _heuristic_route(flat_text) == "assert_fact"


def test_heuristic_route_keeps_explicit_rule_on_rule_path():
    text = (
        "If the curator is absent for more than thirty consecutive days, "
        "the deputy curator becomes acting curator until the board votes otherwise."
    )
    assert _heuristic_route(text) == "assert_rule"
