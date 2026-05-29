from scripts.run_domain_bootstrap_qa import (
    _current_state_source_text_hint_queries,
    _event_description_hint_queries,
    _source_text_question_needles,
    _source_text_question_token_hint_queries,
    _source_record_clock_duration_companion,
    _source_record_numeric_range_companion,
    _source_record_question_overlap_companion,
    _source_record_list_window_companion,
    _source_record_speaker_window_companion,
    _source_record_discrepancy_list_companion,
    _scope_discrepancy_completion_companion,
    _condition_finding_companion,
    _scope_discrepancy_hint_queries,
    _source_coordinate_hint_queries,
    _source_attribution_hint_queries,
    _vote_record_counterfactual_companion,
    _vote_record_disambiguation_companion,
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


def test_scope_discrepancy_hint_adds_unbound_inventory_query() -> None:
    assert _scope_discrepancy_hint_queries(
        utterance="List all unresolved discrepancies between the resolution and agreement.",
        kb_inventory={"signatures": ["scope_discrepancy/6", "source_record_text_atom/2"]},
    ) == [
        "scope_discrepancy(Issue, LeftValue, LeftRecord, RightValue, RightRecord, Basis).",
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


def test_source_text_needles_include_common_travel_event_inflections() -> None:
    needles = _source_text_question_needles(
        "How many minutes elapsed between departure from Seattle and the accident?"
    )

    assert "departed" in needles
    assert needles.index("accident") < 10


def test_source_text_needles_do_not_invent_regular_past_tense_garbage() -> None:
    needles = _source_text_question_needles(
        "Place these in chronological order: (a) issuance of citations; (b) worker fatality; "
        "(c) OSHA investigation; (d) the deadline to contest expires. Note any items the release "
        "does not place in time."
    )

    assert needles[:6] == ["issued", "citations", "fatality", "investigation", "deadline", "contest"]
    assert not {"issuanced", "fatalitied", "investigationed", "deadlined"} & set(needles)


def test_source_text_needles_bridge_salvage_to_recovery_language() -> None:
    needles = _source_text_question_needles(
        "What impact did salvage operations have on the physical evidence examination?"
    )

    assert "recovery" in needles
    assert "recovery_activities" in needles


def test_temporal_source_text_numeric_hints_cover_both_duration_anchors() -> None:
    queries = _source_text_question_token_hint_queries(
        utterance="How many minutes elapsed between departure from Seattle and the accident?",
        kb_inventory={"signatures": ["source_record_text_atom/2", "source_record_numeric_token/2"]},
    )

    assert (
        'source_record_text_atom(SourceRow, TextAtom), memberchk("departed", TextAtom), '
        "source_record_numeric_token(SourceRow, NumericToken)."
    ) in queries
    assert (
        'source_record_text_atom(SourceRow, TextAtom), memberchk("accident", TextAtom), '
        "source_record_numeric_token(SourceRow, NumericToken)."
    ) in queries


def test_source_record_clock_duration_companion_pairs_endpoint_clock_tokens() -> None:
    results = [
        {
            "query": 'source_record_text_atom(SourceRow, TextAtom), memberchk("departed", TextAtom), source_record_numeric_token(SourceRow, NumericToken).',
            "result": {
                "status": "success",
                "rows": [
                    {"SourceRow": "src_line_0001", "NumericToken": "v_1328"},
                ],
                "reasoning_basis": {"contains_needles": ["departed"]},
            },
        },
        {
            "query": 'source_record_text_atom(SourceRow, TextAtom), memberchk("accident", TextAtom), source_record_numeric_token(SourceRow, NumericToken).',
            "result": {
                "status": "success",
                "rows": [
                    {"SourceRow": "src_line_0002", "NumericToken": "v_1620"},
                ],
                "reasoning_basis": {"contains_needles": ["accident"]},
            },
        },
    ]

    companion = _source_record_clock_duration_companion(
        results=results,
        query='source_record_text_atom(SourceRow, TextAtom), memberchk("accident", TextAtom), source_record_numeric_token(SourceRow, NumericToken).',
    )

    assert companion is not None
    row = companion["result"]["rows"][0]
    assert row["DurationMinutes"] == "172"
    assert row["Duration"] == "2 hours 52 minutes"


def test_source_record_numeric_range_companion_extracts_range_support() -> None:
    results = [
        {
            "query": "source_record_text_atom(SourceRow, TextAtom).",
            "result": {
                "status": "success",
                "rows": [
                    {
                        "SourceRow": "src_line_0001",
                        "TextAtom": (
                            "captain_estimated_winds_were_about_85_100_mph_about_74_87_knots_"
                            "and_the_closest_location_reported_winds_gusting_up_to_48_62_knots_"
                            "22_27_miles_from_the_site"
                        ),
                    }
                ],
            },
        }
    ]

    companion = _source_record_numeric_range_companion(
        results,
        utterance="What were the respective wind speed ranges reported by the crew and station?",
    )

    assert companion is not None
    ranges = {row["Range"] for row in companion["result"]["rows"]}
    assert {"85-100 mph", "74-87 knots", "48-62 knots", "22-27 miles"} <= ranges


class _FakeRuntime:
    def __init__(self, rows_by_query: dict[str, list[dict[str, str]]]) -> None:
        self.rows_by_query = rows_by_query

    def query_rows(self, query: str) -> dict[str, object]:
        return {"status": "success", "rows": self.rows_by_query.get(query, [])}


def test_source_record_question_overlap_companion_ranks_relevant_source_rows() -> None:
    runtime = _FakeRuntime(
        {
            "source_record_text_atom(SourceRow, TextAtom).": [
                {
                    "SourceRow": "src_line_0001",
                    "TextAtom": "application_rec_2026_0093_jordan_vale_recused",
                },
                {
                    "SourceRow": "src_line_0002",
                    "TextAtom": "unrelated_score_sheet_total",
                },
            ],
            "source_record_row(SourceRow, Kind, Line, SectionAtom, Label).": [
                {
                    "SourceRow": "src_line_0001",
                    "Kind": "paragraph_line",
                    "Line": "49",
                    "SectionAtom": "other_relevant_applications",
                    "Label": "application_rec_2026_0093",
                },
                {
                    "SourceRow": "src_line_0002",
                    "Kind": "paragraph_line",
                    "Line": "50",
                    "SectionAtom": "score_sheet",
                    "Label": "score_sheet",
                },
            ],
        }
    )

    companion = _source_record_question_overlap_companion(
        runtime,
        utterance="Which application records Jordan Vale's recusal?",
    )

    assert companion is not None
    row = companion["result"]["rows"][0]
    assert row["SourceRow"] == "src_line_0001"
    assert row["SourceTextDisplay"] == "application rec 2026 0093 jordan vale recused"
    assert "jordan" in row["QuestionOverlap"]
    assert "recusal" in row["QuestionOverlap"] or "recused" in row["QuestionOverlap"]


def test_source_record_question_overlap_companion_includes_bounded_turn_sections() -> None:
    runtime = _FakeRuntime(
        {
            "source_record_text_atom(SourceRow, TextAtom).": [
                {"SourceRow": "src_line_0016", "TextAtom": "turn_16"},
                {
                    "SourceRow": "src_line_0017",
                    "TextAtom": "dr_osei_was_not_sure_about_the_lab_exhaust_fans",
                },
                {"SourceRow": "src_line_0023", "TextAtom": "turn_23"},
            ],
            "source_record_row(SourceRow, Kind, Line, SectionAtom, Label).": [
                {
                    "SourceRow": "src_line_0016",
                    "Kind": "heading",
                    "Line": "16",
                    "SectionAtom": "turn_16",
                    "Label": "turn_16",
                },
                {
                    "SourceRow": "src_line_0017",
                    "Kind": "paragraph_line",
                    "Line": "17",
                    "SectionAtom": "turn_16",
                    "Label": "dr_osei",
                },
                {
                    "SourceRow": "src_line_0023",
                    "Kind": "heading",
                    "Line": "23",
                    "SectionAtom": "turn_23",
                    "Label": "turn_23",
                },
            ],
        }
    )

    companion = _source_record_question_overlap_companion(
        runtime,
        utterance="After Turn 16 but before Turn 23, should the lab exhaust fan status be committed?",
    )

    assert companion is not None
    rows = companion["result"]["rows"]
    assert {row["SourceRow"] for row in rows} >= {"src_line_0016", "src_line_0017", "src_line_0023"}


def test_source_record_list_window_companion_follows_list_header_and_delta() -> None:
    runtime = _FakeRuntime(
        {
            "source_record_text_atom(SourceRow, TextAtom).": [
                {"SourceRow": "src_line_0010", "TextAtom": "listed_protected_items"},
                {"SourceRow": "src_line_0011", "TextAtom": "v_4_white_oak"},
                {"SourceRow": "src_line_0012", "TextAtom": "v_11_red_oak"},
                {"SourceRow": "src_line_0020", "TextAtom": "updated_protected_item_count_3_the_prior_2_plus_item_19"},
            ],
            "source_record_row(SourceRow, Kind, Line, SectionAtom, Label).": [
                {
                    "SourceRow": "src_line_0010",
                    "Kind": "paragraph_line",
                    "Line": "10",
                    "SectionAtom": "original_items",
                    "Label": "listed_protected_items",
                },
                {
                    "SourceRow": "src_line_0011",
                    "Kind": "table_row",
                    "Line": "11",
                    "SectionAtom": "original_items",
                    "Label": "v_4",
                },
                {
                    "SourceRow": "src_line_0012",
                    "Kind": "table_row",
                    "Line": "12",
                    "SectionAtom": "original_items",
                    "Label": "v_11",
                },
                {
                    "SourceRow": "src_line_0020",
                    "Kind": "anchored_line",
                    "Line": "20",
                    "SectionAtom": "amendment",
                    "Label": "updated_protected_item_count",
                },
            ],
        }
    )

    companion = _source_record_list_window_companion(
        runtime,
        utterance="List all protected item IDs after the amendment.",
    )

    assert companion is not None
    display_ids = {row["DisplayItemId"] for row in companion["result"]["rows"]}
    assert {"#4", "#11", "#19"} <= display_ids


def test_source_record_speaker_window_companion_returns_neighboring_rows() -> None:
    runtime = _FakeRuntime(
        {
            "source_record_text_atom(SourceRow, TextAtom).": [
                {"SourceRow": "src_line_0010", "TextAtom": "condition_b_minimum_size_discussion"},
                {"SourceRow": "src_line_0011", "TextAtom": "marchetti_an_architect_said_720_square_feet_is_needed"},
                {"SourceRow": "src_line_0012", "TextAtom": "avery_has_the_board_verified_this"},
                {"SourceRow": "src_line_0013", "TextAtom": "avery_no_documentation_from_the_architect_has_been_submitted"},
            ],
            "source_record_row(SourceRow, Kind, Line, SectionAtom, Label).": [
                {"SourceRow": "src_line_0010", "Kind": "paragraph_line", "Line": "10", "SectionAtom": "hearing", "Label": "condition_b"},
                {"SourceRow": "src_line_0011", "Kind": "paragraph_line", "Line": "11", "SectionAtom": "hearing", "Label": "marchetti"},
                {"SourceRow": "src_line_0012", "Kind": "paragraph_line", "Line": "12", "SectionAtom": "hearing", "Label": "avery"},
                {"SourceRow": "src_line_0013", "Kind": "paragraph_line", "Line": "13", "SectionAtom": "hearing", "Label": "avery"},
            ],
        }
    )

    companion = _source_record_speaker_window_companion(
        runtime,
        utterance="Why did Avery dissent on condition (b)?",
    )

    assert companion is not None
    text = " ".join(row["TextAtom"] for row in companion["result"]["rows"])
    assert "no_documentation_from_the_architect" in text


def test_source_record_discrepancy_list_companion_marks_one_sided_context() -> None:
    runtime = _FakeRuntime(
        {
            "source_record_text_atom(SourceRow, TextAtom).": [
                {
                    "SourceRow": "src_line_0010",
                    "TextAtom": "progress_reports_the_resolution_requires_monthly_reports_the_agreement_requires_quarterly_reports",
                },
                {
                    "SourceRow": "src_line_0011",
                    "TextAtom": "customer_notice_the_resolution_requires_72_hours_notice_not_addressed_in_the_agreement_and_entirely_within_town_discretion",
                },
            ],
            "source_record_row(SourceRow, Kind, Line, SectionAtom, Label).": [
                {"SourceRow": "src_line_0010", "Kind": "labeled_line", "Line": "10", "SectionAtom": "memo", "Label": "progress_reports"},
                {"SourceRow": "src_line_0011", "Kind": "labeled_line", "Line": "11", "SectionAtom": "memo", "Label": "customer_notice"},
            ],
        }
    )

    companion = _source_record_discrepancy_list_companion(
        runtime,
        utterance="List all unresolved discrepancies between the resolution and agreement.",
    )

    assert companion is not None
    statuses = {row["SourceRow"]: row["DiscrepancyStatus"] for row in companion["result"]["rows"]}
    assert statuses["src_line_0010"] == "candidate_discrepancy"
    assert statuses["src_line_0011"] == "one_sided_not_discrepancy"


def test_source_record_discrepancy_list_companion_uses_section_context_for_record_names() -> None:
    runtime = _FakeRuntime(
        {
            "source_record_text_atom(SourceRow, TextAtom).": [
                {
                    "SourceRow": "src_line_0010",
                    "TextAtom": "timeline_the_resolution_specifies_18_months_the_first_agreement_specifies_24_months",
                },
                {
                    "SourceRow": "src_line_0011",
                    "TextAtom": "scope_the_borrower_shall_complete_work_within_24_months_note_this_differs_from_the_resolution",
                },
            ],
            "source_record_row(SourceRow, Kind, Line, SectionAtom, Label).": [
                {
                    "SourceRow": "src_line_0010",
                    "Kind": "labeled_line",
                    "Line": "10",
                    "SectionAtom": "director_memo",
                    "Label": "timeline",
                },
                {
                    "SourceRow": "src_line_0011",
                    "Kind": "labeled_line",
                    "Line": "11",
                    "SectionAtom": "document_b_finance_agreement",
                    "Label": "timeline",
                },
            ],
        }
    )

    companion = _source_record_discrepancy_list_companion(
        runtime,
        utterance="List all unresolved discrepancies between the resolution and agreement.",
    )

    assert companion is not None
    rows = {row["SourceRow"]: row for row in companion["result"]["rows"]}
    assert rows["src_line_0010"]["DiscrepancyStatus"] == "candidate_discrepancy"
    assert rows["src_line_0011"]["DiscrepancyStatus"] == "candidate_discrepancy"


def test_condition_finding_companion_returns_condition_specific_findings() -> None:
    runtime = _FakeRuntime(
        {
            "board_finding(ActorOrHearing, Condition, Finding).": [
                {
                    "ActorOrHearing": "hearing_2026_04_24",
                    "Condition": "condition_b",
                    "Finding": "no_documentation_from_the_architect_has_been_submitted",
                },
                {
                    "ActorOrHearing": "hearing_2026_04_24",
                    "Condition": "condition_c",
                    "Finding": "neighborhood_character_met",
                },
            ],
            "source_attributed_claim(SourceOrSpeaker, Subject, ClaimOrFinding, Scope).": [
                {
                    "SourceOrSpeaker": "claim_avery_condition_b",
                    "Subject": "avery",
                    "ClaimOrFinding": "i_disagree_no_documentation_from_the_architect_has_been_submitted",
                    "Scope": "condition_b_discussion",
                }
            ],
        }
    )

    companion = _condition_finding_companion(
        runtime,
        utterance="Why did Avery dissent on condition (b)?",
    )

    assert companion is not None
    rows = companion["result"]["rows"]
    assert rows[0]["SupportKind"] == "condition_finding_source_claim"
    assert rows[0]["SpeakerAlignment"] == "speaker_matched"
    assert "no_documentation_from_the_architect" in " ".join(row["Finding"] for row in rows)


def test_scope_discrepancy_completion_companion_marks_source_only_gaps() -> None:
    runtime = _FakeRuntime(
        {
            "scope_discrepancy(Issue, LeftValue, LeftRecord, RightValue, RightRecord, Basis).": [
                {
                    "Issue": "pipe_length",
                    "LeftValue": "3200_feet",
                    "LeftRecord": "resolution",
                    "RightValue": "3400_feet",
                    "RightRecord": "agreement",
                    "Basis": "estimate_difference",
                }
            ],
            "source_record_text_atom(SourceRow, TextAtom).": [
                {
                    "SourceRow": "src_line_0010",
                    "TextAtom": "v_1_pipe_length_the_resolution_states_3200_feet_the_agreement_states_3400_feet",
                },
                {
                    "SourceRow": "src_line_0011",
                    "TextAtom": "v_4_progress_reports_the_resolution_requires_monthly_reports_the_agreement_requires_quarterly_reports",
                },
            ],
            "source_record_row(SourceRow, Kind, Line, SectionAtom, Label).": [
                {"SourceRow": "src_line_0010", "Kind": "labeled_line", "Line": "10", "SectionAtom": "memo", "Label": "v_1_pipe_length"},
                {"SourceRow": "src_line_0011", "Kind": "labeled_line", "Line": "11", "SectionAtom": "memo", "Label": "v_4_progress_reports"},
            ],
        }
    )

    companion = _scope_discrepancy_completion_companion(
        runtime,
        utterance="List all unresolved discrepancies between the resolution and agreement.",
    )

    assert companion is not None
    rows = {row["Issue"]: row for row in companion["result"]["rows"]}
    assert rows["pipe_length"]["CompletionStatus"] == "already_structured"
    assert rows["reporting_frequency"]["CompletionStatus"] == "source_record_completion"


def test_vote_record_counterfactual_companion_matches_motion_alias_and_counts_flip() -> None:
    results = [
        {
            "query": "vote_record(Motion, ForVotes, AgainstVotes, Denominator, ThresholdRequired).",
            "result": {
                "status": "success",
                "rows": [
                    {
                        "Motion": "vote_mot202607",
                        "ForVotes": "okafor",
                        "AgainstVotes": "yes",
                        "Denominator": "2026_04_01",
                        "ThresholdRequired": "failed",
                    },
                    {
                        "Motion": "vote_mot202607",
                        "ForVotes": "medina",
                        "AgainstVotes": "yes",
                        "Denominator": "2026_04_01",
                        "ThresholdRequired": "failed",
                    },
                    {
                        "Motion": "vote_mot202607",
                        "ForVotes": "river",
                        "AgainstVotes": "no",
                        "Denominator": "2026_04_01",
                        "ThresholdRequired": "failed",
                    },
                    {
                        "Motion": "vote_mot202607",
                        "ForVotes": "volkov",
                        "AgainstVotes": "no",
                        "Denominator": "2026_04_01",
                        "ThresholdRequired": "failed",
                    },
                    {
                        "Motion": "vote_mot202607",
                        "ForVotes": "singh",
                        "AgainstVotes": "yes",
                        "Denominator": "2026_04_01",
                        "ThresholdRequired": "failed",
                    },
                ],
            },
        },
        {
            "query": "source_record_text_atom(SourceRow, TextAtom).",
            "result": {
                "status": "success",
                "rows": [
                    {
                        "SourceRow": "src_line_0001",
                        "TextAtom": "town_council_may_amend_by_vote_of_at_least_4_of_7_members",
                    }
                ],
            },
        },
    ]

    companion = _vote_record_counterfactual_companion(
        results,
        utterance="If River had voted yes on MOT-2026-07, would it have passed?",
    )

    assert companion is not None
    row = companion["result"]["rows"][0]
    assert row["MatchedMotion"] == "vote_mot202607"
    assert row["OriginalVote"] == "no"
    assert row["HypotheticalYesCount"] == "4"
    assert row["Threshold"] == "4"
    assert row["WouldPass"] == "yes"
    assert row["HypotheticalYesActors"] == "medina,okafor,river,singh"


def test_vote_record_disambiguation_companion_prefers_exception_motion() -> None:
    results = [
        {
            "query": "vote_record(Motion, ForVotes, AgainstVotes, Denominator, ThresholdRequired).",
            "result": {
                "status": "success",
                "rows": [
                    {
                        "Motion": "motion_3a_case_r24_003",
                        "ForVotes": "4",
                        "AgainstVotes": "3",
                        "Denominator": "7",
                        "ThresholdRequired": "5",
                    },
                    {
                        "Motion": "motion_3b_case_r24_003",
                        "ForVotes": "7",
                        "AgainstVotes": "0",
                        "Denominator": "7",
                        "ThresholdRequired": "4",
                    },
                ],
            },
        }
    ]

    companion = _vote_record_disambiguation_companion(
        results,
        utterance="What was the vote tally on the exception motion for CASE-R24-003?",
    )

    assert companion is not None
    rows = companion["result"]["rows"]
    assert rows[0]["MatchedMotion"] == "motion_3a_case_r24_003"
    assert rows[0]["MotionKind"] == "exception_or_supermajority"
    assert rows[0]["ShortTally"] == "4-3-0"
    assert rows[0]["WouldCarry"] == "no"
