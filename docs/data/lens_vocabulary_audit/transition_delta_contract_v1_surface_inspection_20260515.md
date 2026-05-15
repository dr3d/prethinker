# Transition/Delta Contract Surface Inspection

Generated: 2026-05-15

This is a manual compile-surface inspection over
`tmp/transition_delta_contract_compile_20260515`. It is not a repair.

## Summary

- Compile fixtures: `3`
- Parsed OK: `3`
- QA: `22 / 0 / 0`
- Helper rows: `0`

## Role Membership Transition

Direct transition rows are present:

- `membership_transition(trans_u12_1, trail_crew, ren_ido, left).`
- `membership_transition(trans_u12_1, trail_crew, mika_sol, joined).`
- `role_transition(trans_u12_1, supply_coordinator, ren_ido, mika_sol, replaced).`
- `transition_context(trans_u12_1, after_winter_roster_closed).`
- `transition_effective_date(...)` rows in the retry pass.
- `no_change(crew_lead, unchanged).`

Interpretation:

Role and membership transition are already inside the compile surface on this
focused unlike probe. The emitted rows bind group, member, join/leave state,
role, predecessor, successor, and context well enough for no-helper QA.

## Status Value Transition

Direct transition rows are present:

- `status_transition(w_6, pending_inspection, approved_for_release, 2026_12_12t13_40, sn_3).`
- `transition_actor(w_6, jae_lin).`
- `attribute_value(w_6, approval_reason, awaiting_sensor_check, pre_transition).`
- `attribute_value(w_6, approval_reason, sensor_check_passed, post_transition).`
- unchanged fields are present as current/post-transition attribute values.
- `work_order_not_cancelled(w_6).`

Interpretation:

Status transition is already inside the compile surface. The status old value,
new value, transition time, actor, and source note are bound in one row, with
adjacent attribute rows for reason and unchanged fields.

## Document Field Delta

The compile emits predecessor/current and old/new field values:

- `replaced_role(f_9, d_4).`
- `transition_status(f_9, current).`
- `transition_status(d_4, prior).`
- `field_value(d_4, missing_item, site_photo).`
- `field_value(f_9, missing_item, owner_signature).`
- `field_unchanged(parcel_number, transition_d_4_to_f_9).`
- `field_unchanged(contact_phone_number, transition_d_4_to_f_9).`
- `field_value(d_4, contact_phone_number, unstated).`
- `field_value(f_9, contact_phone_number, unstated).`

Interpretation:

Document field delta is answerable, but not fully contract-bound. The source
surface preserves predecessor, successor, current/prior status, old field
value, new field value, unchanged fields, and still-unstated fields. It does
not emit a direct row that binds the changed field to old value, new value,
predecessor, successor, and transition scope.

## Lesson

The emerging transition/delta primitive is real, but uneven:

- role/membership transitions: interior on focused unlike probe;
- status transitions: interior on focused unlike probe;
- document field deltas: answerable but still assembled from adjacent rows.

The next repair, if needed, should be a generic field-delta contract, not an
epistemic or entity/role vocabulary patch:

```text
field_delta(transition, subject_or_field, old_holder, old_value, new_holder, new_value, scope)
```

Exact predicate shape should be designed only after replaying at least one more
document-field and one more status/reason delta to avoid overfitting this first
packet example.
