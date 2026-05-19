from scripts.run_domain_bootstrap_file_batch import (
    _detail_wrapper_drift_flags,
    _extract_compile_summary,
    _profile_delivery_flags,
    _quality_gate_result,
    _quality_retry_context_lines,
    _render_md,
    _summarize,
)


def test_compile_batch_summary_extracts_quality_gate_signals() -> None:
    summary = _extract_compile_summary(
        {
            "parsed_ok": True,
            "parsed": {"candidate_predicates": [{"signature": "record_status/2"}]},
            "source_compile": {"admitted_count": 9, "skipped_count": 1},
            "score": {
                "rough_score": 0.861,
                "risk_count": 3,
                "repeated_structure_count": 1,
                "repeated_structure_id_only_record_refs": ["record_id/1"],
                "repeated_structure_role_mismatch_refs": ["record_status/2"],
                "frontier_unknown_positive_predicate_count": 0,
                "frontier_unknown_positive_predicate_refs": [],
                "generic_predicate_count": 0,
            },
        }
    )

    assert summary["rough_score"] == 0.861
    assert summary["risk_count"] == 3
    assert summary["repeated_structure_id_only_record_refs"] == ["record_id/1"]
    assert summary["frontier_unknown_positive_predicate_count"] == 0
    assert summary["detail_wrapper_drift_flags"] == []


def test_compile_batch_summary_flags_detail_wrapper_without_backbone() -> None:
    summary = _extract_compile_summary(
        {
            "parsed_ok": True,
            "parsed": {"candidate_predicates": [{"signature": "context/2"}]},
            "source_compile": {
                "facts": [
                    "source_record_field(src_line_001, record_id, rec_07).",
                    "source_record_field(src_line_001, departure_time, v_06_30).",
                    "context(rec_07, departure_context).",
                ],
            },
            "score": {"rough_score": 0.9, "risk_count": 2},
        }
    )

    assert any(flag.startswith("identity_backbone_missing_with_wrapper:") for flag in summary["detail_wrapper_drift_flags"])
    assert any(flag.startswith("date_time_backbone_missing_with_wrapper:") for flag in summary["detail_wrapper_drift_flags"])


def test_compile_batch_summary_flags_ledger_only_surface_contract() -> None:
    summary = _extract_compile_summary(
        {
            "parsed_ok": True,
            "parsed": {"candidate_predicates": [{"signature": "status_at/2"}]},
            "source_compile": {
                "facts": [
                    "source_record_text_atom(src_line_1, on_2026_05_01_record_a_was_received_with_status_pending).",
                    "source_record_text_atom(src_line_2, on_2026_05_02_record_a_was_closed_as_approved).",
                    "status_at(record_a, pending).",
                ],
            },
            "score": {"rough_score": 0.9, "risk_count": 2},
        }
    )

    assert summary["compile_surface_contract_flags"] == [
        "operational_lifecycle_preservation:ledger_only:source=2:direct=0"
    ]


def test_compile_batch_summary_extracts_profile_delivery_flags() -> None:
    payload = {
        "parsed_ok": True,
        "parsed": {"candidate_predicates": [{"signature": "status_state_at/4"}]},
        "source_compile": {
            "admitted_count": 9,
            "skipped_count": 1,
            "profile_delivery": {
                "findings": [
                    {
                        "class": "status_state_carrier_offered_but_undelivered",
                        "source_signal_count": 2,
                        "offered_carriers": ["status_state_at/4"],
                    }
                ]
            },
        },
        "score": {"rough_score": 0.9, "risk_count": 2},
    }

    assert _profile_delivery_flags(payload) == [
        "status_state_carrier_offered_but_undelivered:source=2:offered=status_state_at/4"
    ]
    summary = _extract_compile_summary(payload)
    assert summary["profile_delivery_flags"] == [
        "status_state_carrier_offered_but_undelivered:source=2:offered=status_state_at/4"
    ]


def test_compile_batch_summary_allows_detail_wrapper_with_backbone() -> None:
    summary = _extract_compile_summary(
        {
            "parsed_ok": True,
            "parsed": {"candidate_predicates": [{"signature": "context/2"}]},
            "source_compile": {
                "facts": [
                    "source_record_field(src_line_001, record_id, rec_07).",
                    "source_record_field(src_line_001, departure_time, v_06_30).",
                    "record_id(rec_07).",
                    "departure_time(rec_07, v_06_30).",
                    "context(rec_07, departure_context).",
                ],
            },
            "score": {"rough_score": 0.9, "risk_count": 2},
        }
    )

    assert summary["detail_wrapper_drift_flags"] == []


def test_compile_batch_summary_treats_date_atoms_as_date_time_backbone() -> None:
    summary = _extract_compile_summary(
        {
            "parsed_ok": True,
            "parsed": {"candidate_predicates": [{"signature": "source_detail/4"}]},
            "source_compile": {
                "facts": [
                    "source_record_field(src_line_001, hearing_date, v_2026_04_24).",
                    "hearing_event(hearing_1, 2026_04_24, held).",
                    "source_detail(hearing_1, note, held_as_scheduled, src_line_001).",
                ],
            },
            "score": {"rough_score": 0.9, "risk_count": 2},
        }
    )

    assert "date_time_backbone_missing_with_wrapper:source_detail" not in summary["detail_wrapper_drift_flags"]


def test_detail_wrapper_drift_counts_contested_state_values() -> None:
    payload = {
        "parsed": {"candidate_predicates": [{"signature": "source_detail/4"}]},
        "source_compile": {
            "facts": [
                "source_record_field(src_line_1, title_status, contested_by_party).",
                "register_entry(item_a, external_a, object_a, holder_a, owner_a, contested_by_party).",
                "source_detail(item_a, title_status, contested_by_party, src_line_1).",
            ]
        },
    }

    assert _detail_wrapper_drift_flags(payload) == []


def test_compile_quality_gate_passes_accepted_draw_shape() -> None:
    result = {
        "fixture": "fixture_a",
        "returncode": 0,
        "compile_json": "compile.json",
        "summary": {
            "parsed_ok": True,
            "rough_score": 0.833,
            "risk_count": 5,
            "candidate_predicates": 18,
            "compile_admitted": 86,
            "compile_skipped": 52,
        },
    }

    gate = _quality_gate_result(result, min_rough_score=0.775, max_risk_count=5)

    assert gate["passed"] is True
    assert gate["decision"] == "pass"
    assert gate["compile_skipped_share"] == 0.3768


def test_compile_quality_gate_holds_high_risk_draw() -> None:
    result = {
        "fixture": "fixture_b",
        "returncode": 0,
        "compile_json": "compile.json",
        "summary": {
            "parsed_ok": True,
            "rough_score": 0.778,
            "risk_count": 6,
            "candidate_predicates": 30,
            "compile_admitted": 176,
            "compile_skipped": 23,
        },
    }

    gate = _quality_gate_result(result, min_rough_score=0.775, max_risk_count=5)

    assert gate["passed"] is False
    assert gate["decision"] == "hold"
    assert gate["reasons"] == ["risk_count>5"]


def test_compile_quality_gate_holds_detail_wrapper_drift() -> None:
    result = {
        "fixture": "fixture_detail",
        "returncode": 0,
        "compile_json": "compile.json",
        "summary": {
            "parsed_ok": True,
            "rough_score": 0.9,
            "risk_count": 2,
            "candidate_predicates": 12,
            "compile_admitted": 30,
            "compile_skipped": 0,
            "detail_wrapper_drift_flags": ["identity_backbone_missing_with_wrapper:context"],
        },
    }

    gate = _quality_gate_result(result, min_rough_score=0.775, max_risk_count=5)

    assert gate["passed"] is False
    assert gate["decision"] == "hold"
    assert gate["reasons"] == ["detail_wrapper_drift:identity_backbone_missing_with_wrapper:context"]


def test_compile_quality_gate_holds_surface_contract_flag() -> None:
    result = {
        "fixture": "fixture_contract",
        "returncode": 0,
        "compile_json": "compile.json",
        "summary": {
            "parsed_ok": True,
            "rough_score": 0.9,
            "risk_count": 2,
            "candidate_predicates": 12,
            "compile_admitted": 30,
            "compile_skipped": 0,
            "compile_surface_contract_flags": [
                "operational_lifecycle_preservation:ledger_only:source=2:direct=0"
            ],
        },
    }

    gate = _quality_gate_result(result, min_rough_score=0.775, max_risk_count=5)

    assert gate["passed"] is False
    assert gate["decision"] == "hold"
    assert gate["reasons"] == [
        "compile_surface_contract:operational_lifecycle_preservation:ledger_only:source=2:direct=0"
    ]


def test_compile_quality_gate_holds_profile_delivery_flag() -> None:
    result = {
        "fixture": "fixture_profile_delivery",
        "returncode": 0,
        "compile_json": "compile.json",
        "summary": {
            "parsed_ok": True,
            "rough_score": 0.9,
            "risk_count": 2,
            "candidate_predicates": 12,
            "compile_admitted": 30,
            "compile_skipped": 0,
            "profile_delivery_flags": [
                "status_state_carrier_offered_but_undelivered:source=2:offered=status_state_at/4"
            ],
        },
    }

    gate = _quality_gate_result(result, min_rough_score=0.775, max_risk_count=5)

    assert gate["passed"] is False
    assert gate["decision"] == "hold"
    assert gate["reasons"] == [
        "profile_delivery:status_state_carrier_offered_but_undelivered:source=2:offered=status_state_at/4"
    ]


def test_quality_retry_context_lines_are_generic_for_wrapper_and_lifecycle_holds() -> None:
    lines = _quality_retry_context_lines(
        {
            "reasons": [
                "detail_wrapper_drift:location_backbone_missing_with_wrapper:source_detail",
                "compile_surface_contract:operational_lifecycle_preservation:ledger_only:source=2:direct=0",
                "compile_surface_contract:source_authority_pair_preservation:ledger_only:source=1:direct=0",
                "profile_delivery:status_state_carrier_offered_but_undelivered:source=2:offered=status_state_at/4",
            ]
        }
    )

    assert any("missing location backbone surface" in line for line in lines)
    assert any("complete direct lifecycle units" in line for line in lines)
    assert any("direct source-authority surface" in line for line in lines)
    assert any("direct status/state carrier" in line for line in lines)
    joined = "\n".join(lines).casefold()
    assert "fixture" not in joined
    assert "source_detail, event, context, note, or summary row is additive only" in joined
    assert "rule description, note, docket text, or source_record row is additive only" in joined


def test_compile_batch_quality_gate_renders_markdown() -> None:
    summary = _summarize(
        [
            {
                "fixture": "fixture_a",
                "returncode": 0,
                "compile_json": "a.json",
                "summary": {
                    "parsed_ok": True,
                    "rough_score": 0.9,
                    "risk_count": 2,
                    "candidate_predicates": 10,
                    "compile_admitted": 20,
                    "compile_skipped": 0,
                },
            },
            {
                "fixture": "fixture_b",
                "returncode": 0,
                "compile_json": "b.json",
                "summary": {
                    "parsed_ok": True,
                    "rough_score": 0.7,
                    "risk_count": 2,
                    "candidate_predicates": 10,
                    "compile_admitted": 20,
                    "compile_skipped": 0,
                },
            },
        ],
        lanes=2,
        base_timeout=900,
        effective_timeout=1800,
        quality_gate=True,
        quality_min_rough_score=0.775,
        quality_max_risk_count=5,
    )

    assert summary["quality_gate"]["passed"] is False
    assert summary["quality_gate"]["hold_count"] == 1
    markdown = _render_md(summary)
    assert "## Compile Quality Gate" in markdown
    assert "rough_score<0.775" in markdown
