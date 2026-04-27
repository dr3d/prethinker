from __future__ import annotations

from pathlib import Path

from src.policy_reimbursement_demo import (
    PolicyDemoState,
    apply_mapped_to_policy_runtime,
    build_policy_kb_context_pack,
    query_policy_runtime,
    summarize_policy_demo_rows,
    write_policy_demo_html,
)
from src.semantic_ir import semantic_ir_to_legacy_parse


def _mapped(*, facts=None, rules=None, retracts=None, queries=None) -> dict:
    return {
        "admission_diagnostics": {
            "clauses": {
                "facts": facts or [],
                "rules": rules or [],
                "retracts": retracts or [],
                "queries": queries or [],
            }
        }
    }


def test_policy_runtime_derives_violations_without_committing_derived_facts() -> None:
    state = PolicyDemoState()
    apply_mapped_to_policy_runtime(
        _mapped(
            rules=[
                "self_approval(R) :- requested_by(R, P), approved_by(R, P).",
                "manager_conflict_approval(R) :- requested_by(R, Requester), approved_by(R, Approver), manages(Approver, Requester).",
                "violation(R, reimbursement_policy) :- self_approval(R).",
                "violation(R, reimbursement_policy) :- manager_conflict_approval(R).",
            ]
        ),
        state,
    )
    apply_mapped_to_policy_runtime(
        _mapped(
            facts=[
                "requested_by(r1, maya).",
                "approved_by(r1, maya).",
                "requested_by(r2, theo).",
                "approved_by(r2, lena).",
                "manages(lena, theo).",
                "requested_by(r3, priya).",
                "approved_by(r3, sam).",
            ]
        ),
        state,
    )

    result = query_policy_runtime(state, "violation(R, reimbursement_policy).")

    assert result["r_values"] == ["r1", "r2"]
    assert "violation(r1, reimbursement_policy)." not in state.facts
    assert "self_approval(r1)." not in state.facts


def test_policy_runtime_explicit_correction_updates_query_answer() -> None:
    state = PolicyDemoState()
    apply_mapped_to_policy_runtime(
        _mapped(
            rules=[
                "manager_conflict_approval(R) :- requested_by(R, Requester), approved_by(R, Approver), manages(Approver, Requester).",
                "violation(R, reimbursement_policy) :- manager_conflict_approval(R).",
            ],
            facts=[
                "requested_by(r2, theo).",
                "approved_by(r2, lena).",
                "manages(lena, theo).",
            ],
        ),
        state,
    )
    assert query_policy_runtime(state, "violation(R, reimbursement_policy).")["r_values"] == ["r2"]

    apply_mapped_to_policy_runtime(
        _mapped(retracts=["approved_by(r2, lena)."], facts=["approved_by(r2, omar)."]),
        state,
    )

    assert query_policy_runtime(state, "violation(R, reimbursement_policy).")["r_values"] == []
    assert "approved_by(r2, lena)." not in state.facts
    assert "approved_by(r2, omar)." in state.facts


def test_policy_kb_context_pack_exposes_relevant_committed_clauses() -> None:
    state = PolicyDemoState()
    apply_mapped_to_policy_runtime(_mapped(facts=["approved_by(r2, lena).", "requested_by(r2, theo)."]), state)

    pack = build_policy_kb_context_pack(state, utterance="Correction: R2 was approved by Omar.", turn_id="correction")

    assert pack["version"] == "semantic_ir_context_pack_v1"
    assert "approved_by(r2, lena)." in pack["relevant_clauses"]
    assert "approved_by(r2, lena)." in pack["current_state_candidates"]
    assert "r2" in pack["entity_candidates"]


def test_policy_demo_summary_and_html_are_compact(tmp_path: Path) -> None:
    rows = [
        {
            "parsed_ok": True,
            "runtime_apply": {"apply_errors": [], "asserted_facts": ["requested_by(r1, maya)."]},
            "expected_match": True,
            "derived_violation_write_leak": False,
            "runtime_query": {"r_values": ["r1"]},
            "parsed": {"schema_version": "semantic_ir_v1"},
            "admission_diagnostics": {"clauses": {"facts": ["requested_by(r1, maya)."]}},
        }
    ]
    summary = summarize_policy_demo_rows(rows)
    path = tmp_path / "report.html"

    write_policy_demo_html({"summary": summary, "rows": rows}, path)

    assert summary["rough_score"] == 1.0
    text = path.read_text(encoding="utf-8")
    assert "<details" in text
    assert "max-height: 520px" in text


def test_mapper_does_not_demote_variable_like_rule_stub_to_fact() -> None:
    ir = {
        "schema_version": "semantic_ir_v1",
        "decision": "commit",
        "turn_type": "rule_update",
        "entities": [],
        "referents": [],
        "assertions": [],
        "unsafe_implications": [],
        "candidate_operations": [
            {
                "operation": "rule",
                "predicate": "violation",
                "args": ["R", "reimbursement_policy"],
                "polarity": "positive",
                "source": "direct",
                "safety": "safe",
            }
        ],
        "truth_maintenance": {
            "support_links": [],
            "conflicts": [],
            "retraction_plan": [],
            "derived_consequences": [],
        },
        "clarification_questions": [],
        "self_check": {"bad_commit_risk": "low", "missing_slots": [], "notes": []},
    }

    mapped, warnings = semantic_ir_to_legacy_parse(
        ir,
        allowed_predicates=["violation/2"],
        predicate_contracts=[{"signature": "violation/2", "args": ["event_or_record", "policy"]}],
    )

    assert mapped["facts"] == []
    assert mapped["rules"] == []
    assert warnings == ["skipped rule operation with variable-like args but no executable clause"]


def test_mapper_preserves_single_letter_query_variables() -> None:
    ir = {
        "schema_version": "semantic_ir_v1",
        "decision": "answer",
        "turn_type": "query",
        "entities": [],
        "referents": [],
        "assertions": [],
        "unsafe_implications": [],
        "candidate_operations": [
            {
                "operation": "query",
                "predicate": "violation",
                "args": ["R", "reimbursement_policy"],
                "polarity": "positive",
                "source": "direct",
                "safety": "safe",
            }
        ],
        "truth_maintenance": {
            "support_links": [],
            "conflicts": [],
            "retraction_plan": [],
            "derived_consequences": [],
        },
        "clarification_questions": [],
        "self_check": {"bad_commit_risk": "low", "missing_slots": [], "notes": []},
    }

    mapped, _ = semantic_ir_to_legacy_parse(
        ir,
        allowed_predicates=["violation/2"],
        predicate_contracts=[{"signature": "violation/2", "args": ["event_or_record", "policy"]}],
    )

    assert mapped["queries"] == ["violation(R, reimbursement_policy)."]
