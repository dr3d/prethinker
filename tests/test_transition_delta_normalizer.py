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


def test_normalizes_operational_status_phase_and_assignment_rows() -> None:
    observations = normalize_transition_delta_facts(
        [
            "record_status_phase(case_7, pending_review, 2026_02_01).",
            "record_status_phase(case_7, closed, 2026_02_09).",
            "record_status_phase(case_8, 2026_03_01, pending_intake).",
            "record_assigned_to(case_7, reviewer_a, 2026_02_02).",
        ]
    )

    assert {
        "kind": "status_phase_observation",
        "subject": "case_7",
        "status": "pending_review",
        "date": "2026_02_01",
        "source_predicate": "record_status_phase",
    } in observations
    assert {
        "kind": "status_phase_observation",
        "subject": "case_8",
        "status": "pending_intake",
        "date": "2026_03_01",
        "source_predicate": "record_status_phase",
    } in observations
    assert {
        "kind": "assignment_observation",
        "subject": "case_7",
        "assignee": "reviewer_a",
        "date": "2026_02_02",
        "source_predicate": "record_assigned_to",
    } in observations
    assert {
        "kind": "timeline_value_transition",
        "subject": "case_7",
        "field": "record_status_phase",
        "old_value": "pending_review",
        "new_value": "closed",
        "old_date": "2026_02_01",
        "new_date": "2026_02_09",
        "source_predicate": "record_status_phase",
    } in observations


def test_normalizes_source_record_table_order_transitions() -> None:
    observations = normalize_transition_delta_facts(
        [
            "source_record_section(row_a, original_policy).",
            "source_record_field(row_a, zone, zone_7).",
            "source_record_field(row_a, order, mandatory_evacuation).",
            "source_record_section(row_b, revised_policy).",
            "source_record_field(row_b, zone, zone_7).",
            "source_record_field(row_b, new_order, downgraded_to_evacuation_warning).",
            "source_record_section(row_c, revised_policy).",
            "source_record_field(row_c, zone, zone_8).",
            "source_record_field(row_c, new_order, evacuation_warning).",
        ]
    )

    assert {
        "kind": "source_record_value_transition",
        "subject": "zone_7",
        "field": "order",
        "old_value": "mandatory_evacuation",
        "new_value": "evacuation_warning",
        "predecessor": "row_a",
        "successor": "row_b",
        "predecessor_section": "original_policy",
        "successor_section": "revised_policy",
        "source_predicate": "source_record_field",
    } in observations
    assert {
        "kind": "source_record_subject_added",
        "subject": "zone_8",
        "field": "order",
        "new_value": "evacuation_warning",
        "successor": "row_c",
        "successor_section": "revised_policy",
        "source_predicate": "source_record_field",
    } in observations


def test_normalizes_generic_supersession_and_status_timeline() -> None:
    observations = normalize_transition_delta_facts(
        [
            "amendment_supersedes(amended_doc, original_doc).",
            "record_superseded_by(old_status, new_status).",
            "tree_protection_status(tree_19, eligible_for_removal, 2026_04_02, original_permit).",
            "tree_protection_status(tree_19, protected, 2026_04_25, amendment).",
        ]
    )

    assert {
        "kind": "supersession",
        "successor": "amended_doc",
        "predecessor": "original_doc",
        "source_predicate": "amendment_supersedes",
    } in observations
    assert {
        "kind": "supersession",
        "successor": "new_status",
        "predecessor": "old_status",
        "source_predicate": "record_superseded_by",
    } in observations
    assert {
        "kind": "timeline_value_transition",
        "subject": "tree_19",
        "field": "tree_protection_status",
        "old_value": "eligible_for_removal",
        "new_value": "protected",
        "old_date": "2026_04_02",
        "new_date": "2026_04_25",
        "source_predicate": "tree_protection_status",
    } in observations


def test_normalizes_attribute_timeline_from_identification_rows() -> None:
    observations = normalize_transition_delta_facts(
        [
            "tree_identified(tree_19, acer_platanoides, 22, surveyor_a, 2026_03_24).",
            "tree_identified(tree_19, acer_saccharum, 24_5, arborist_b, 2026_04_14).",
        ]
    )

    assert {
        "kind": "timeline_value_transition",
        "subject": "tree_19",
        "field": "species",
        "old_value": "acer_platanoides",
        "new_value": "acer_saccharum",
        "old_date": "2026_03_24",
        "new_date": "2026_04_14",
        "source_predicate": "tree_identified",
    } in observations
    assert {
        "kind": "timeline_value_transition",
        "subject": "tree_19",
        "field": "dbh",
        "old_value": "22",
        "new_value": "24_5",
        "old_date": "2026_03_24",
        "new_date": "2026_04_14",
        "source_predicate": "tree_identified",
    } in observations


def test_normalizes_related_document_value_transitions() -> None:
    observations = normalize_transition_delta_facts(
        [
            "amends(amended_notice, original_notice).",
            "draft_superseded_by(original_form, final_form).",
            "authorized_count(original_notice, food_stalls, 18).",
            "authorized_count(original_notice, craft_stalls, 6).",
            "closing_time(original_notice, 20_00).",
            "authorized_count(amended_notice, food_stalls, 16).",
            "authorized_count(amended_notice, craft_stalls, 6).",
            "closing_time(amended_notice, 19_30).",
            "form_status(original_form, pending).",
            "form_status(final_form, approved).",
        ]
    )

    assert {
        "kind": "related_document_value_transition",
        "relation": "amends",
        "predecessor": "original_notice",
        "successor": "amended_notice",
        "field": "food_stalls",
        "old_value": "18",
        "new_value": "16",
        "source_predicate": "authorized_count",
    } in observations
    assert {
        "kind": "related_document_value_unchanged",
        "relation": "amends",
        "predecessor": "original_notice",
        "successor": "amended_notice",
        "field": "craft_stalls",
        "old_value": "6",
        "new_value": "6",
        "source_predicate": "authorized_count",
    } in observations
    assert {
        "kind": "related_document_value_transition",
        "relation": "amends",
        "predecessor": "original_notice",
        "successor": "amended_notice",
        "field": "value",
        "old_value": "20_00",
        "new_value": "19_30",
        "source_predicate": "closing_time",
    } in observations
    assert {
        "kind": "related_document_value_transition",
        "relation": "draft_superseded_by",
        "predecessor": "original_form",
        "successor": "final_form",
        "field": "value",
        "old_value": "pending",
        "new_value": "approved",
        "source_predicate": "form_status",
    } in observations


def test_normalizes_role_lifecycle_and_unique_holder_transition() -> None:
    observations = normalize_transition_delta_facts(
        [
            "holds_role(new_holder, coordinator, lab_group).",
            "held_role(prior_holder, coordinator, lab_group).",
            "role_cessation(prior_holder, coordinator, lab_group).",
            "holds_role(side_observer, reviewer, lab_group).",
        ]
    )

    assert {
        "kind": "role_lifecycle_state",
        "subject": "new_holder",
        "role": "coordinator",
        "scope": "lab_group",
        "state": "current",
        "source_predicate": "holds_role",
    } in observations
    assert {
        "kind": "role_lifecycle_state",
        "subject": "prior_holder",
        "role": "coordinator",
        "scope": "lab_group",
        "state": "ended",
        "source_predicate": "held_role|role_cessation",
    } in observations
    assert {
        "kind": "role_holder_transition",
        "predecessor": "prior_holder",
        "successor": "new_holder",
        "role": "coordinator",
        "scope": "lab_group",
        "source_predicate": "holds_role|held_role|role_cessation",
    } in observations


def test_role_holder_transition_requires_unique_current_and_prior_ended_holder() -> None:
    observations = normalize_transition_delta_facts(
        [
            "holds_role(new_holder_a, coordinator, lab_group).",
            "holds_role(new_holder_b, coordinator, lab_group).",
            "held_role(prior_holder, coordinator, lab_group).",
            "role_cessation(prior_holder, coordinator, lab_group).",
        ]
    )

    assert not any(item["kind"] == "role_holder_transition" for item in observations)


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
