from src.transition_delta_normalizer import normalize_transition_delta_facts, summarize_observations


def test_normalizes_policy_revision_transition_shapes() -> None:
    observations = normalize_transition_delta_facts(
        [
            "supersedes(memo_r_19, bulletin_c_14).",
            "policy_field_changed(standard_parcel_weight_limit, 18_kg, 22_kg, memo_r_19).",
            "policy_field_removed(cold_pack_supervisor_note_requirement, bulletin_c_14, memo_r_19).",
            "policy_field_added(oversized_label_photo_check_requirement, memo_r_19, required).",
        ]
    )

    assert {
        "kind": "supersession",
        "successor": "memo_r_19",
        "predecessor": "bulletin_c_14",
        "source_predicate": "supersedes",
    } in observations
    assert {
        "kind": "value_transition",
        "subject": "memo_r_19",
        "field": "standard_parcel_weight_limit",
        "old_value": "18_kg",
        "new_value": "22_kg",
        "source_predicate": "policy_field_changed",
    } in observations
    assert any(item["kind"] == "field_removed" for item in observations)
    assert any(item["kind"] == "field_added" for item in observations)


def test_normalizes_document_snapshot_and_absence_shapes() -> None:
    observations = normalize_transition_delta_facts(
        [
            "form_replaced(of_2, rf_5, rn_14).",
            "field_value_snapshot(of_2, inspection_checklist_section, section_3, before).",
            "field_value_snapshot(rf_5, inspection_checklist_section, section_5, after).",
            "field_absent(of_2, emergency_contact).",
            "field_absent(rf_5, emergency_contact).",
            "field_unchanged(40_credits, fee_amount, rn_14).",
        ]
    )

    assert {
        "kind": "supersession",
        "successor": "rf_5",
        "predecessor": "of_2",
        "source_predicate": "form_replaced",
        "source": "rn_14",
    } in observations
    assert {
        "kind": "value_transition",
        "field": "inspection_checklist_section",
        "old_value": "section_3",
        "new_value": "section_5",
        "predecessor": "of_2",
        "successor": "rf_5",
        "source_predicate": "field_value_snapshot",
    } in observations
    assert {
        "kind": "absence_persistence",
        "field": "emergency_contact",
        "objects": ["of_2", "rf_5"],
        "source_predicate": "field_absent",
    } in observations
    assert any(item["kind"] == "field_unchanged" for item in observations)


def test_normalizes_status_transition_with_reason_and_timestamp() -> None:
    observations = normalize_transition_delta_facts(
        [
            "transition_occurred(t_17, on_hold, ready_for_scheduling, cl_22).",
            "transition_timestamp(cl_22, 14_20).",
            "transition_reason(t_17, address_proof_received).",
        ]
    )

    assert {
        "kind": "status_transition",
        "subject": "t_17",
        "old_value": "on_hold",
        "new_value": "ready_for_scheduling",
        "event": "cl_22",
        "source_predicate": "transition_occurred",
        "timestamp": "14_20",
        "reason": "address_proof_received",
    } in observations


def test_summarizes_observations_by_kind() -> None:
    summary = summarize_observations(
        [
            {"kind": "supersession"},
            {"kind": "value_transition"},
            {"kind": "value_transition"},
        ]
    )

    assert summary == {
        "observation_count": 3,
        "kind_counts": {"supersession": 1, "value_transition": 2},
    }
