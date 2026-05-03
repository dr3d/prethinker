from scripts.run_domain_bootstrap_file import (
    SOURCE_PASS_OPS_JSON_SCHEMA,
    _compile_health_summary,
    _flat_plus_surface_contribution,
    _pass_surface_contribution,
    _source_pass_ops_to_semantic_ir,
)


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

    assert healthy["verdict"] == "healthy"
    assert healthy["recommendation"] == "qa_run_reasonable"
    assert warning["verdict"] == "warning"
    assert warning["recommendation"] == "run_qa_but_treat_thin_lens_results_as_diagnostic"
    assert poor["verdict"] == "poor"
    assert poor["recommendation"] == "repair_compile_before_qa"
    assert poor["flag_counts"]["zero_yield"] == 1
    assert poor["unhealthy_passes"] == ["p1"]
