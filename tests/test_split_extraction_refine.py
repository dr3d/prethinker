from kb_pipeline import (
    _apply_assert_fact_shape_sync_guard,
    _apply_narrative_fact_normalization_guard,
    _apply_narrative_rule_normalization_guard,
    _apply_predicate_name_sanity_guard,
    _apply_registry_fact_salvage_guard,
    _apply_temporal_predicate_namespace_guard,
    _build_longform_recovery_chunks,
    _build_temporal_fact_clause,
    _heuristic_route,
    _looks_blocksworld_state_description,
    _maybe_recover_longform_assert_fact_payload,
    _refine_logic_only_payload,
    _should_attempt_longform_assert_fact_recovery,
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


def test_assert_fact_shape_sync_guard_aligns_logic_and_clears_placeholder_clarification():
    parsed = {
        "intent": "assert_fact",
        "logic_string": "clear(a).\nteached_two_public_weekend_seminas(celeste_rowan, volunteer).",
        "facts": ["clear(a).", "taught_two_public_weekend_seminas(celeste_rowan, volunteer)."],
        "components": {"atoms": ["a"], "variables": [], "predicates": ["clear"]},
        "ambiguities": [],
        "needs_clarification": True,
        "uncertainty_score": 0.72,
        "uncertainty_label": "high",
        "clarification_question": "Can you clarify this point before I apply it: None?",
        "clarification_reason": "None",
    }
    out, events = _apply_assert_fact_shape_sync_guard(parsed)
    assert out["facts"] == ["clear(a).", "taught_two_public_weekend_seminas(celeste_rowan, volunteer)."]
    assert out["logic_string"] == "clear(a).\ntaught_two_public_weekend_seminas(celeste_rowan, volunteer)."
    assert out["components"]["predicates"] == ["clear", "taught_two_public_weekend_seminas"]
    assert out["needs_clarification"] is False
    assert out["clarification_question"] == ""
    assert out["clarification_reason"] == ""
    assert {event["kind"] for event in events} == {
        "assert_fact_shape_sync_guard",
        "placeholder_clarification_downgrade_guard",
    }


def test_temporal_predicate_namespace_guard_rewrites_non_temporal_at_step_pair():
    parsed = {
        "intent": "assert_fact",
        "logic_string": "at_step(jax, mudroom).",
        "facts": ["at_step(jax, mudroom)."],
        "components": {"atoms": ["jax", "mudroom"], "variables": [], "predicates": ["at_step"]},
        "ambiguities": [],
        "needs_clarification": False,
        "uncertainty_score": 0.2,
        "uncertainty_label": "low",
        "clarification_question": "",
        "clarification_reason": "",
        "rationale": "",
    }
    out, events = _apply_temporal_predicate_namespace_guard(
        parsed,
        allowed_signatures={"at/2", "at_step/2"},
        strict_registry=True,
        temporal_predicate="at_step",
    )
    assert out["facts"] == ["at(jax, mudroom)."]
    assert out["logic_string"] == "at(jax, mudroom)."
    assert out["components"]["predicates"] == ["at"]
    assert out["needs_clarification"] is False
    assert any(event["reason"] == "non_temporal_reserved_predicate_rewritten" for event in events)


def test_temporal_predicate_namespace_guard_blocks_unrewritable_reserved_predicate_misuse():
    parsed = {
        "intent": "assert_fact",
        "logic_string": "at_step(jax, mudroom).",
        "facts": ["at_step(jax, mudroom)."],
        "components": {"atoms": ["jax", "mudroom"], "variables": [], "predicates": ["at_step"]},
        "ambiguities": [],
        "needs_clarification": False,
        "uncertainty_score": 0.2,
        "uncertainty_label": "low",
        "clarification_question": "",
        "clarification_reason": "",
        "rationale": "",
    }
    out, events = _apply_temporal_predicate_namespace_guard(
        parsed,
        allowed_signatures={"at_step/2"},
        strict_registry=True,
        temporal_predicate="at_step",
    )
    assert out["facts"] == []
    assert out["logic_string"] == ""
    assert out["needs_clarification"] is True
    assert "canonical predicate" in out["clarification_question"].lower()
    assert any(event["reason"] == "reserved_temporal_predicate_blocked" for event in events)


def test_build_temporal_fact_clause_skips_reserved_temporal_predicate_facts():
    assert _build_temporal_fact_clause(
        "at_step(jax, mudroom).",
        turn_index=11,
        temporal_predicate="at_step",
    ) is None
    assert _build_temporal_fact_clause(
        "at_step(11, at(jax, mudroom)).",
        turn_index=12,
        temporal_predicate="at_step",
    ) is None


def test_build_longform_recovery_chunks_prefers_rich_paragraphs():
    utterance = (
        "Title Only\n\n"
        "In January 2021, Nora Lin directed the commons and lived above Market Hall.\n\n"
        "Mateo Ruiz supervised the grounds and lived in Cedar House with Hana Bell.\n\n"
        "In July 2024, Priya Das was elected permanent director of Westhaven Commons."
    )
    chunks = _build_longform_recovery_chunks(utterance)
    assert len(chunks) == 3
    assert all("Title Only" not in chunk for chunk in chunks)


def test_should_attempt_longform_assert_fact_recovery_requires_sparse_longform_payload():
    utterance = (
        "The Greenhouse at Westhaven Commons\n\n"
        + (
            "In January 2021, Nora Lin directed the commons, lived above Market Hall, "
            "and kept the project calendar near the canal office. "
        )
        * 12
        + "\n\n"
        + (
            "Mateo Ruiz supervised the grounds, lived in Cedar House, and coordinated repairs "
            "with Hana Bell after each storm week. "
        )
        * 10
        + "\n\n"
        + (
            "In July 2024, Priya Das was elected permanent director of Westhaven Commons "
            "after the annual meeting and took over the director ledger. "
        )
        * 8
    )
    sparse = {
        "intent": "assert_fact",
        "logic_string": "at(westhaven_commons, canal).",
        "facts": ["at(westhaven_commons, canal)."],
    }
    rich = {
        "intent": "assert_fact",
        "logic_string": "\n".join(f"fact_{idx}(x)." for idx in range(8)),
        "facts": [f"fact_{idx}(x)." for idx in range(8)],
    }
    assert _should_attempt_longform_assert_fact_recovery(sparse, utterance) is True
    assert _should_attempt_longform_assert_fact_recovery(rich, utterance) is False


def test_maybe_recover_longform_assert_fact_payload_harvests_paragraph_facts(monkeypatch):
    utterance = (
        "The Greenhouse at Westhaven Commons\n\n"
        + (
            "In January 2021, Nora Lin directed the commons, lived above Market Hall, "
            "and kept the project calendar near the canal office. "
        )
        * 8
        + "\n\n"
        + (
            "Mateo Ruiz supervised the grounds, lived in Cedar House with Hana Bell, "
            "and tracked repair work after each storm week. "
        )
        * 8
        + "\n\n"
        + (
            "In July 2024, Priya Das was elected permanent director of Westhaven Commons "
            "after the annual meeting and took over the director ledger. "
        )
        * 7
    )
    parsed = {
        "intent": "assert_fact",
        "logic_string": "at(westhaven_commons, canal).",
        "facts": ["at(westhaven_commons, canal)."],
        "components": {"atoms": ["westhaven_commons", "canal"], "variables": [], "predicates": ["at"]},
        "ambiguities": [],
        "needs_clarification": False,
        "uncertainty_score": 0.12,
        "uncertainty_label": "low",
        "clarification_question": "",
        "clarification_reason": "",
        "rationale": "initial",
    }
    recovered_payloads = iter(
        [
            {
                "intent": "assert_fact",
                "logic_string": "director(nora_lin).\nlives_in(nora_lin, market_hall_apartment).",
                "confidence": {"overall": 0.9, "intent": 0.95, "logic": 0.9},
                "ambiguities": [],
                "needs_clarification": False,
                "uncertainty_score": 0.1,
                "uncertainty_label": "low",
                "clarification_question": "",
                "clarification_reason": "",
                "rationale": "chunk 1",
            },
            {
                "intent": "assert_fact",
                "logic_string": "grounds_supervisor(mateo_ruiz).\nlives_in(mateo_ruiz, cedar_house).",
                "confidence": {"overall": 0.9, "intent": 0.95, "logic": 0.9},
                "ambiguities": [],
                "needs_clarification": False,
                "uncertainty_score": 0.1,
                "uncertainty_label": "low",
                "clarification_question": "",
                "clarification_reason": "",
                "rationale": "chunk 2",
            },
            {
                "intent": "assert_fact",
                "logic_string": "director(priya_das).",
                "confidence": {"overall": 0.9, "intent": 0.95, "logic": 0.9},
                "ambiguities": [],
                "needs_clarification": False,
                "uncertainty_score": 0.1,
                "uncertainty_label": "low",
                "clarification_question": "",
                "clarification_reason": "",
                "rationale": "chunk 3",
            },
        ]
    )

    def fake_call_model_prompt(**kwargs):
        return {"raw": kwargs.get("prompt_text", "")}

    def fake_parse_model_json(resp, required_keys=None):
        return next(recovered_payloads), "{}"

    monkeypatch.setattr("kb_pipeline._call_model_prompt", fake_call_model_prompt)
    monkeypatch.setattr("kb_pipeline._parse_model_json", fake_parse_model_json)

    out, events = _maybe_recover_longform_assert_fact_payload(
        parsed,
        utterance=utterance,
        backend="ollama",
        base_url="http://127.0.0.1:11434",
        model="qwen3.5:9b",
        context_length=8192,
        timeout_seconds=30,
        api_key="",
        known_predicates=[],
        prompt_guide="",
    )
    assert out["facts"] == [
        "at(westhaven_commons, canal).",
        "director(nora_lin).",
        "lives_in(nora_lin, market_hall_apartment).",
        "grounds_supervisor(mateo_ruiz).",
        "lives_in(mateo_ruiz, cedar_house).",
        "director(priya_das).",
    ]
    assert "Longform fact recovery" in out["rationale"]
    assert events
    assert events[0]["kind"] == "longform_assert_fact_recovery"
    assert events[0]["recovered_fact_count"] == 5


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


def test_narrative_fact_normalization_guard_rewrites_story_specific_fact_names():
    parsed = {
        "intent": "assert_fact",
        "logic_string": (
            "at_board_meeting(june_2024, elected_permanent_director(lena_ortiz, pineglass_ridge)).\n"
            "repaired(washed_out_bridge).\n"
            "allowed_temporary_relocation(ranger_covenant, four_months).\n"
            "ordered_move(station, theo_marsh)."
        ),
        "facts": [
            "at_board_meeting(june_2024, elected_permanent_director(lena_ortiz, pineglass_ridge)).",
            "repaired(washed_out_bridge).",
            "allowed_temporary_relocation(ranger_covenant, four_months).",
            "ordered_move(station, theo_marsh).",
        ],
        "components": {"atoms": [], "variables": [], "predicates": []},
        "ambiguities": [],
        "needs_clarification": False,
    }
    out, events = _apply_narrative_fact_normalization_guard(
        parsed,
        utterance=(
            "At the board meeting in June 2024, Lena Ortiz was elected permanent director of Pineglass Ridge. "
            "That same summer the washed-out bridge was repaired, the ranger covenant allowed temporary relocation "
            "under four months, and the station ordered the move."
        ),
        allowed_signatures={"allowed/3", "director/1", "directed/2", "elected/4", "repaired/1"},
        strict_registry=True,
    )
    assert out["facts"] == [
        "elected(lena_ortiz, director, pineglass_ridge, june_2024).",
        "director(lena_ortiz).",
        "repaired(washed_out_bridge).",
        "allowed(ranger_covenant, temporary_relocation, four_months).",
        "directed(station, theo_marsh).",
    ]
    assert events


def test_narrative_fact_normalization_guard_rewrites_malformed_at_step_fact_to_at3():
    parsed = {
        "intent": "assert_fact",
        "logic_string": "at_step(glasshouse_a, public_micro_grant, september_2021).",
        "facts": ["at_step(glasshouse_a, public_micro_grant, september_2021)."],
        "components": {"atoms": [], "variables": [], "predicates": []},
        "ambiguities": [],
        "needs_clarification": False,
    }
    out, events = _apply_narrative_fact_normalization_guard(
        parsed,
        utterance="In September 2021, the trust accepted a public micro-grant for Glasshouse A.",
        allowed_signatures={"at/3"},
        strict_registry=True,
    )
    assert out["facts"] == ["at(glasshouse_a, public_micro_grant, september_2021)."]
    assert events


def test_narrative_fact_normalization_guard_extracts_summary_roles_and_resolves_mapping_clarification():
    parsed = {
        "intent": "assert_fact",
        "logic_string": "curator(selene).",
        "facts": ["curator(selene)."],
        "components": {"atoms": ["selene"], "variables": [], "predicates": ["curator"]},
        "ambiguities": ["The predicate 'operations_chief' is not in the allowed list."],
        "needs_clarification": True,
        "uncertainty_score": 0.81,
        "uncertainty_label": "high",
        "clarification_question": (
            "Which allowed predicates should map 'rights_dispute_settled', 'trail_fund_paid_for', "
            "'operations_chief', and 'taught'?"
        ),
        "clarification_reason": "Predicate mapping unclear.",
    }
    out, events = _apply_narrative_fact_normalization_guard(
        parsed,
        utterance=(
            "A rights dispute was finally settled in February 2025. "
            "The board determined that drone Kestrel belonged to Pineglass Ridge Field Station. "
            "It also determined that Northstep Imaging and Northstep Visuals should be treated as the same contractor record. "
            "By then, Lena remained director, Selene remained curator, Noor remained deputy curator, "
            "Theo remained trail ranger, Malcolm remained operations chief, and Celeste Rowan taught "
            "two public weekend seminars as a volunteer rather than as an officer."
        ),
        allowed_signatures={
            "closed/2",
            "curator/1",
            "deputy_curator/1",
            "director/1",
            "operations_chief/1",
            "owns/2",
            "related_to/2",
            "trail_ranger/1",
            "volunteer/1",
        },
        strict_registry=True,
    )
    assert out["facts"] == [
        "curator(selene).",
        "director(lena).",
        "deputy_curator(noor).",
        "trail_ranger(theo).",
        "operations_chief(malcolm).",
        "volunteer(celeste_rowan).",
        "closed(rights_dispute, february_2025).",
        "owns(pineglass_ridge_field_station, kestrel).",
        "related_to(northstep_imaging, northstep_visuals).",
    ]
    assert out["needs_clarification"] is False
    assert out["clarification_question"] == ""
    assert out["clarification_reason"] == ""
    assert out["uncertainty_label"] == "low"
    assert events


def test_narrative_fact_normalization_guard_clears_placeholder_clarification_when_summary_facts_exist():
    parsed = {
        "intent": "assert_fact",
        "logic_string": "director(lena).",
        "facts": ["director(lena)."],
        "components": {"atoms": ["lena"], "variables": [], "predicates": ["director"]},
        "ambiguities": [],
        "needs_clarification": True,
        "uncertainty_score": 0.81,
        "uncertainty_label": "high",
        "clarification_question": "Can you clarify this point before I apply it: None?",
        "clarification_reason": "None",
    }
    out, events = _apply_narrative_fact_normalization_guard(
        parsed,
        utterance=(
            "A rights dispute was finally settled in February 2025. "
            "The board determined that drone Kestrel belonged to Pineglass Ridge Field Station. "
            "By then, Lena remained director, Selene remained curator, Noor remained deputy curator."
        ),
        allowed_signatures={"closed/2", "curator/1", "deputy_curator/1", "director/1", "owns/2"},
        strict_registry=True,
    )
    assert out["needs_clarification"] is False
    assert out["clarification_question"] == ""
    assert out["clarification_reason"] == ""
    assert events


def test_narrative_fact_normalization_guard_uses_logic_string_fallback_for_summary_cleanup():
    parsed = {
        "intent": "assert_fact",
        "logic_string": (
            "rights_dispute_settled(feb_2025).\n"
            "drone_ownership(kestrel, pineglass_ridge_field_station).\n"
            "drone_ownership(kestrel, jonah_kade, false).\n"
            "drone_ownership(kestrel, mapping_program, false).\n"
            "northstep_imaging_same_contractor_record(northstep_visuals).\n"
            "trail_fund_paid_for(rebuilt_footbridge).\n"
            "director(lena).\n"
            "curator(selene).\n"
            "deputy_curator(noor).\n"
            "trail_ranger(theo).\n"
            "operations_chief(malcolm).\n"
            "teached_two_public_weekend_seminas(celeste_rowan, volunteer)."
        ),
        "components": {"atoms": [], "variables": [], "predicates": []},
        "ambiguities": [],
        "needs_clarification": True,
        "uncertainty_score": 0.81,
        "uncertainty_label": "high",
        "clarification_question": "Can you clarify this point before I apply it: None?",
        "clarification_reason": "None",
    }
    out, events = _apply_narrative_fact_normalization_guard(
        parsed,
        utterance=(
            "A rights dispute was finally settled in February 2025. "
            "The board determined that drone Kestrel belonged to Pineglass Ridge Field Station, "
            "not to Jonah Kade or the mapping program. "
            "It also determined that Northstep Imaging and Northstep Visuals should be treated "
            "as the same contractor record. "
            "The trail fund paid for the rebuilt footbridge. "
            "By then, Lena remained director, Selene remained curator, Noor remained deputy curator, "
            "Theo remained trail ranger, Malcolm remained operations chief, and Celeste Rowan taught "
            "two public weekend seminars as a volunteer rather than as an officer."
        ),
        allowed_signatures={
            "closed/2",
            "curator/1",
            "deputy_curator/1",
            "director/1",
            "operations_chief/1",
            "owns/2",
            "related_to/2",
            "trail_ranger/1",
            "volunteer/1",
        },
        strict_registry=True,
    )
    assert "closed(rights_dispute, february_2025)." in out["facts"]
    assert "owns(pineglass_ridge_field_station, kestrel)." in out["facts"]
    assert "related_to(northstep_imaging, northstep_visuals)." in out["facts"]
    assert "volunteer(celeste_rowan)." in out["facts"]
    assert out["needs_clarification"] is False
    assert out["clarification_question"] == ""
    assert out["clarification_reason"] == ""
    assert events


def test_narrative_fact_normalization_guard_extracts_grant_support_facts_for_salvage():
    parsed = {
        "intent": "assert_fact",
        "logic_string": (
            "accepted_grant(trust, public_micro_grant, glasshouse_a, september_2021).\n"
            "required_classes(public_micro_grant, 2, free, public, month)."
        ),
        "facts": [
            "accepted_grant(trust, public_micro_grant, glasshouse_a, september_2021).",
            "required_classes(public_micro_grant, 2, free, public, month).",
        ],
        "components": {"atoms": [], "variables": [], "predicates": []},
        "ambiguities": [],
        "needs_clarification": False,
    }
    normalized, events = _apply_narrative_fact_normalization_guard(
        parsed,
        utterance=(
            "In September 2021, the trust accepted a public micro-grant for Glasshouse A. "
            "Willa Quade and Hana Bell ended up teaching most of those classes. "
            "Elias Shore kept the attendance sheets because the grant required proof that "
            "the classes were open to any resident."
        ),
        allowed_signatures={"allowed/3", "documented_with/2", "gave/3", "milestone/3"},
        strict_registry=True,
    )
    salvaged, _ = _apply_registry_fact_salvage_guard(
        normalized,
        allowed_signatures={"allowed/3", "documented_with/2", "gave/3", "milestone/3"},
        strict_registry=True,
    )
    assert salvaged["facts"] == [
        "milestone(public_micro_grant, glasshouse_a, september_2021).",
        "documented_with(public_micro_grant, attendance_sheets).",
        "allowed(public_micro_grant, classes, any_resident).",
        "gave(willa_quade, public_classes, public_micro_grant).",
        "gave(hana_bell, public_classes, public_micro_grant).",
    ]
    assert events


def test_narrative_rule_normalization_guard_rewrites_westhaven_charter_and_clears_clarification():
    parsed = {
        "intent": "assert_rule",
        "logic_string": (
            "acting_manager(X) :- absent(X, Days), Days > 21, greenhouse_manager(X).\n"
            "anual_operating_surplus(Surplus) > 80000 -> transfer_roof_reserve(0.15 * Surplus), "
            "pay_staff_stipends(false)."
        ),
        "facts": [],
        "rules": [
            "acting_manager(X) :- absent(X, Days), Days > 21, greenhouse_manager(X).",
            "anual_operating_surplus(Surplus) > 80000 -> transfer_roof_reserve(0.15 * Surplus), pay_staff_stipends(false).",
        ],
        "queries": [],
        "components": {"atoms": [], "variables": [], "predicates": []},
        "ambiguities": [
            "Predicate 'transfer_roof_reserve' and 'pay_staff_stipends' not found in allowed list."
        ],
        "needs_clarification": True,
        "uncertainty_score": 0.9,
        "uncertainty_label": "high",
        "clarification_question": "What are the canonical predicate names for 'transfer into roof reserve' and 'pay staff stipends'?",
        "clarification_reason": "Required predicates not found.",
    }
    out, events = _apply_narrative_rule_normalization_guard(
        parsed,
        utterance=(
            "The Westhaven Trust charter had two clauses that seemed dull until they mattered. "
            "First, if the greenhouse manager was absent for more than twenty-one consecutive days, "
            "the assistant manager automatically became acting manager until the board voted otherwise. "
            "Second, if annual operating surplus exceeded eighty thousand crowns, then fifteen percent had to be "
            "transferred into the roof reserve before any staff stipends were paid. "
            "The lease said the cart could stay with the tenant only if maintenance logs were filed every quarter. "
            "If two quarterly logs were missed, title to the cart reverted to the trust even if the tenant still physically used it."
        ),
        allowed_signatures={
            "acting_manager/1",
            "absent/2",
            "annual_operating_surplus/1",
            "lease_valid/2",
            "maintenance_logs_filed_quarterly/2",
            "missed_log/3",
            "roof_reserve_transfer/1",
            "title_reverts_to_trust/2",
        },
        strict_registry=True,
    )
    assert out["rules"] == [
        "acting_manager(X) :- absent(X, Days), Days > 21.",
        "roof_reserve_transfer(15_percent) :- annual_operating_surplus(Surplus), Surplus > 80000.",
        "lease_valid(lot_12, cart) :- maintenance_logs_filed_quarterly(lot_12, cart).",
        "title_reverts_to_trust(lot_12, cart) :- missed_log(lot_12, cart, 2).",
    ]
    assert out["needs_clarification"] is False
    assert out["clarification_question"] == ""
    assert out["clarification_reason"] == ""
    assert out["uncertainty_label"] == "low"
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
