from scripts.run_domain_bootstrap_qa import (
    _current_state_source_text_hint_queries,
    _event_description_hint_queries,
    _source_text_question_needles,
    _source_coordinate_hint_queries,
    _source_attribution_hint_queries,
)


def test_source_attribution_hint_uses_inventory_only() -> None:
    kb_inventory = {
        "signatures": [
            "source_attributed_claim/4",
            "source_authority/3",
            "source_record_text_atom/2",
            "unrelated_fact/2",
        ]
    }

    assert _source_attribution_hint_queries(
        utterance="Why was the status corrected and who was responsible?",
        kb_inventory=kb_inventory,
    ) == [
        "source_attributed_claim(SourceOrSpeaker, Subject, ClaimOrFinding, Scope).",
        "source_authority(SubjectOrScope, Authority, Action).",
        "source_record_text_atom(SourceRow, TextAtom).",
    ]


def test_source_attribution_hint_stays_quiet_without_trigger_language() -> None:
    assert (
        _source_attribution_hint_queries(
            utterance="What is the current value?",
            kb_inventory={"signatures": ["source_attributed_claim/4"]},
        )
        == []
    )


def test_source_attribution_hint_handles_modal_use_questions() -> None:
    assert _source_attribution_hint_queries(
        utterance="Can the registered group use any shared space currently?",
        kb_inventory={"signatures": ["source_attributed_claim/4", "source_record_text_atom/2"]},
    ) == [
        "source_attributed_claim(SourceOrSpeaker, Subject, ClaimOrFinding, Scope).",
        "source_record_text_atom(SourceRow, TextAtom).",
    ]


def test_event_description_hint_targets_generic_event_signatures() -> None:
    kb_inventory = {
        "signatures": [
            "source_record_text_atom/2",
            "status_event/5",
            "measurement_event/4",
            "static_fact/3",
        ]
    }

    assert _event_description_hint_queries(
        utterance="Why was the effective date corrected?",
        kb_inventory=kb_inventory,
    ) == [
        "status_event(X, Y, Z, A, B).",
        "measurement_event(X, Y, Z, A).",
    ]


def test_event_description_hint_requires_event_question() -> None:
    assert (
        _event_description_hint_queries(
            utterance="Which item is active?",
            kb_inventory={"signatures": ["status_event/5"]},
        )
        == []
    )


def test_current_state_source_text_hint_is_bounded_to_current_value_questions() -> None:
    kb_inventory = {"signatures": ["source_record_text_atom/2"]}

    assert _current_state_source_text_hint_queries(
        utterance="What is the current monthly rent for the tenant?",
        kb_inventory=kb_inventory,
    ) == ["source_record_text_atom(SourceRow, TextAtom)."]

    assert (
        _current_state_source_text_hint_queries(
            utterance="What happened during the first amendment?",
            kb_inventory=kb_inventory,
        )
        == []
    )


def test_source_coordinate_hint_recognizes_according_to_and_per() -> None:
    kb_inventory = {
        "signatures": [
            "source_record_section/2",
            "source_record_label/2",
            "source_record_line/2",
            "source_record_field/3",
            "source_record_text_atom/2",
        ]
    }

    assert _source_coordinate_hint_queries(
        utterance="According to the chronology, what date was the event?",
        kb_inventory=kb_inventory,
    ) == [
        "source_record_section(SourceRow, Section).",
        "source_record_label(SourceRow, Label).",
        "source_record_line(SourceRow, Line).",
        "source_record_field(SourceRow, Field, Value).",
        "source_record_text_atom(SourceRow, TextAtom).",
    ]

    assert _source_coordinate_hint_queries(
        utterance="Per the signed order, what activity may continue?",
        kb_inventory=kb_inventory,
    )[-1] == "source_record_text_atom(SourceRow, TextAtom)."

    assert _source_coordinate_hint_queries(
        utterance="What is the packet ID associated with this source within the packet?",
        kb_inventory=kb_inventory,
    )[3] == "source_record_field(SourceRow, Field, Value)."


def test_source_text_needles_preserve_legal_title_phrase() -> None:
    needles = _source_text_question_needles(
        "Per the memo, what is required for the insurance settlement to transfer title to the wreck?"
    )

    assert needles[0] == "transfer_title"
