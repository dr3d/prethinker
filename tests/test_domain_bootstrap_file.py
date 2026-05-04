from scripts.run_domain_bootstrap_file import (
    PROFILE_SIGNATURE_ROSTER_JSON_SCHEMA,
    SOURCE_ENTITY_LEDGER_SCHEMA,
    SOURCE_PASS_OPS_JSON_SCHEMA,
    _compile_health_summary,
    _compile_source_with_plan_passes,
    _flat_plus_surface_contribution,
    _invalid_profile_retry_context,
    _pass_surface_contribution,
    _profile_from_signature_roster,
    _source_pass_ops_to_semantic_ir,
)
import scripts.run_domain_bootstrap_file as domain_bootstrap_file


def test_source_entity_ledger_schema_has_coverage_targets() -> None:
    assert "coverage_targets" in SOURCE_ENTITY_LEDGER_SCHEMA["required"]
    target_schema = SOURCE_ENTITY_LEDGER_SCHEMA["properties"]["coverage_targets"]["items"]
    assert target_schema["required"] == [
        "target_id",
        "lens",
        "anchor_atoms",
        "coverage_goal",
        "risk_note",
    ]
    assert "event_spine" in target_schema["properties"]["lens"]["enum"]
    assert "final_state" in target_schema["properties"]["lens"]["enum"]
    assert "causality" in target_schema["properties"]["lens"]["enum"]


def test_source_pass_ops_schema_is_operations_only() -> None:
    assert SOURCE_PASS_OPS_JSON_SCHEMA["required"] == [
        "schema_version",
        "pass_id",
        "decision",
        "candidate_operations",
        "self_check",
    ]
    assert "entities" not in SOURCE_PASS_OPS_JSON_SCHEMA["properties"]
    assert "propositions" not in SOURCE_PASS_OPS_JSON_SCHEMA["properties"]
    assert SOURCE_PASS_OPS_JSON_SCHEMA["properties"]["candidate_operations"]["maxItems"] == 64


def test_profile_signature_roster_schema_omits_arg_roles() -> None:
    item_schema = PROFILE_SIGNATURE_ROSTER_JSON_SCHEMA["properties"]["candidate_signatures"]["items"]

    assert "candidate_signatures" in PROFILE_SIGNATURE_ROSTER_JSON_SCHEMA["required"]
    assert "args" not in item_schema["properties"]
    assert item_schema["properties"]["signature"]["pattern"] == "^[a-z][a-z0-9_]*/[1-5]$"


def test_source_pass_ops_wraps_for_normal_mapper() -> None:
    ir = _source_pass_ops_to_semantic_ir(
        {
            "schema_version": "source_pass_ops_v1",
            "pass_id": "pass_1",
            "decision": "commit",
            "candidate_operations": [
                {
                    "operation": "assert",
                    "proposition_id": "",
                    "predicate": "person_role",
                    "args": ["elena_voss", "respondent"],
                    "polarity": "positive",
                    "source": "direct",
                    "safety": "safe",
                }
            ],
            "self_check": {"bad_commit_risk": "low", "missing_slots": [], "notes": ["compact pass"]},
        }
    )

    assert ir["schema_version"] == "semantic_ir_v1"
    assert ir["entities"] == []
    assert ir["propositions"] == []
    assert ir["candidate_operations"][0]["predicate"] == "person_role"
    assert ir["truth_maintenance"]["support_links"] == []
    assert ir["self_check"]["notes"] == ["compact pass"]


def test_pass_surface_contribution_counts_unique_rows_in_order() -> None:
    rows = _pass_surface_contribution(
        [
            {
                "pass_id": "p1",
                "facts": ["a(1).", "b(2)."],
                "rules": ["r(X) :- a(X)."],
                "queries": [],
                "admitted_count": 3,
                "skipped_count": 0,
            },
            {
                "pass_id": "p2",
                "facts": ["b(2).", "c(3)."],
                "rules": ["r(X) :- a(X)."],
                "queries": ["c(X)."],
                "admitted_count": 4,
                "skipped_count": 1,
            },
        ]
    )

    assert rows[0]["unique_contribution_count"] == 3
    assert rows[0]["duplicate_count"] == 0
    assert rows[1]["unique_contribution_count"] == 2
    assert rows[1]["duplicate_count"] == 2
    assert rows[1]["unique_contribution_ratio"] == 0.5
    assert rows[1]["health_flags"] == ["thin_surface"]


def test_flat_plus_surface_contribution_treats_flat_pass_as_seen() -> None:
    rows = _flat_plus_surface_contribution(
        flat={"facts": ["a(1).", "b(2)."], "rules": [], "queries": [], "admitted_count": 2, "skipped_count": 0},
        focused={
            "passes": [
                {
                    "pass_id": "p1",
                    "facts": ["b(2).", "c(3)."],
                    "rules": [],
                    "queries": [],
                    "admitted_count": 2,
                    "skipped_count": 0,
                }
            ]
        },
    )

    assert rows[0]["pass_id"] == "flat_skeleton"
    assert rows[0]["unique_contribution_count"] == 2
    assert rows[1]["pass_id"] == "p1"
    assert rows[1]["unique_contribution_count"] == 1
    assert rows[1]["duplicate_count"] == 1
    assert "thin_surface" in rows[1]["health_flags"]


def test_pass_surface_contribution_flags_zero_and_skip_heavy_passes() -> None:
    rows = _pass_surface_contribution(
        [
            {"pass_id": "failed", "ok": False, "facts": [], "rules": [], "queries": []},
            {
                "pass_id": "skip_heavy",
                "ok": True,
                "facts": ["a(1)."],
                "rules": [],
                "queries": [],
                "admitted_count": 1,
                "skipped_count": 9,
            },
        ]
    )

    assert rows[0]["health_flags"] == ["pass_not_ok", "zero_yield"]
    assert "thin_surface" in rows[1]["health_flags"]
    assert "skip_heavy" in rows[1]["health_flags"]


def test_compile_health_summary_classifies_pass_surface() -> None:
    healthy = _compile_health_summary(
        [
            {
                "pass_id": "p1",
                "unique_contribution_count": 10,
                "duplicate_count": 1,
                "health_flags": [],
            }
        ]
    )
    warning = _compile_health_summary(
        [
            {
                "pass_id": "p1",
                "unique_contribution_count": 2,
                "duplicate_count": 0,
                "health_flags": ["thin_surface"],
            }
        ]
    )
    poor = _compile_health_summary(
        [
            {
                "pass_id": "p1",
                "unique_contribution_count": 0,
                "duplicate_count": 0,
                "health_flags": ["pass_not_ok", "zero_yield"],
            }
        ]
    )
    skip_warning = _compile_health_summary(
        [
            {
                "pass_id": "p1",
                "unique_contribution_count": 10,
                "duplicate_count": 1,
                "health_flags": [],
            },
            {
                "pass_id": "p2",
                "unique_contribution_count": 5,
                "duplicate_count": 2,
                "health_flags": ["skip_heavy"],
            },
        ]
    )

    assert healthy["verdict"] == "healthy"
    assert healthy["recommendation"] == "qa_run_reasonable"
    assert healthy["semantic_progress"]["zombie_risk"] == "low"
    assert warning["verdict"] == "warning"
    assert warning["recommendation"] == "run_qa_but_treat_thin_lens_results_as_diagnostic"
    assert warning["semantic_progress"]["recommended_action"] == "continue_only_with_named_expected_contribution"
    assert poor["verdict"] == "poor"
    assert poor["recommendation"] == "repair_compile_before_qa"
    assert poor["semantic_progress"]["recommended_action"] == "stop_and_report_struggle"
    assert poor["flag_counts"]["zero_yield"] == 1
    assert poor["unhealthy_passes"] == ["p1"]
    assert skip_warning["verdict"] == "warning"
    assert skip_warning["recommendation"] == "run_qa_but_treat_thin_lens_results_as_diagnostic"
    assert skip_warning["semantic_progress"]["zombie_risk"] == "medium"


def test_invalid_profile_retry_context_blocks_arg_role_runaway() -> None:
    context = _invalid_profile_retry_context(
        parse_error="json_error:bad comma",
        raw_content='"args":["plaintiff_id_ref_entity_type_1_2_3_4_5"]',
        max_predicates=12,
    )

    joined = "\n".join(context)
    assert "at most 12 unique predicate signatures" in joined
    assert "candidate_predicates[].args are short structural role labels only" in joined
    assert "argument-role runaway" in joined
    assert "entity_type_N counters" in joined


def test_profile_from_signature_roster_uses_generic_args() -> None:
    profile = _profile_from_signature_roster(
        {
            "schema_version": "profile_signature_roster_v1",
            "domain_guess": "legal_docket",
            "domain_scope": "Docket state and deadlines.",
            "confidence": 0.7,
            "source_summary": ["Compact profile."],
            "entity_types": [{"name": "case", "description": "Case record."}],
            "candidate_signatures": [
                {
                    "signature": "case_info/4",
                    "description": "Case metadata.",
                    "admission_notes": ["source-bound"],
                },
                {
                    "signature": "case_info/4",
                    "description": "duplicate",
                    "admission_notes": [],
                },
                {
                    "signature": "bad/9",
                    "description": "ignored",
                    "admission_notes": [],
                },
            ],
            "repeated_structures": [
                {
                    "name": "docket entries",
                    "record_predicate": "docket_event/4",
                    "property_predicates": ["event_date/2"],
                }
            ],
            "admission_risks": ["deadline/fact collapse"],
            "clarification_policy": [],
            "unsafe_transformations": [],
            "self_check": {"notes": ["fallback"]},
        }
    )

    assert profile is not None
    assert profile["schema_version"] == "profile_bootstrap_v1"
    assert profile["candidate_predicates"][0]["signature"] == "case_info/4"
    assert profile["candidate_predicates"][0]["args"] == ["arg_1", "arg_2", "arg_3", "arg_4"]
    assert len(profile["candidate_predicates"]) == 1
    assert profile["repeated_structures"][0]["record_predicate"] == "docket_event/4"
    assert "compact_signature_roster_fallback" in profile["self_check"]["notes"]


def test_compile_source_with_plan_passes_reports_health(monkeypatch) -> None:
    def fake_compile(**kwargs):
        pass_id = ""
        for row in kwargs.get("extra_context", []):
            if str(row).startswith("current_intake_pass_id:"):
                pass_id = str(row).split(":", 1)[1].strip()
        if pass_id == "p1":
            return {"ok": True, "facts": ["a(1)."], "rules": [], "queries": [], "admitted_count": 1, "skipped_count": 0}
        return {"ok": True, "facts": ["a(1).", "b(2)."], "rules": [], "queries": [], "admitted_count": 2, "skipped_count": 0}

    monkeypatch.setattr(domain_bootstrap_file, "_compile_source_with_draft_profile", fake_compile)
    args = type(
        "Args",
        (),
        {
            "max_plan_passes": 2,
            "focused_pass_operation_target": 48,
            "focused_pass_ops_schema": False,
            "domain_hint": "test",
        },
    )()

    result = _compile_source_with_plan_passes(
        source_text="source",
        parsed_profile={"candidate_predicates": []},
        intake_plan={
            "pass_plan": [
                {"pass_id": "p1", "purpose": "first", "focus": "one"},
                {"pass_id": "p2", "purpose": "second", "focus": "two"},
            ]
        },
        args=args,
    )

    assert result["ok"] is True
    assert result["facts"] == ["a(1).", "b(2)."]
    assert result["surface_contribution"][0]["unique_contribution_count"] == 1
    assert result["surface_contribution"][1]["duplicate_count"] == 1
    assert result["compile_health"]["verdict"] in {"healthy", "warning"}
