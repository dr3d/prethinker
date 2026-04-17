from kb_pipeline import (
    _apply_registry_fact_salvage_guard,
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


def test_looks_blocksworld_state_description_positive():
    text = (
        "You have 3 blocks. Your arm is empty. b2 is on b1. "
        "b1 is on the table. b2 is clear. Your goal is to have the following."
    )
    assert _looks_blocksworld_state_description(text)


def test_looks_blocksworld_state_description_negative():
    text = "Please summarize this article about distributed systems."
    assert not _looks_blocksworld_state_description(text)
