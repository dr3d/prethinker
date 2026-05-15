# Transition/Delta Contract TD-004 Surface Inspection

Generated: 2026-05-15

This inspection covers `policy_threshold_revision`.

## Summary

- Compile fixtures: `1`
- Parsed OK: `1`
- QA: `9 / 0 / 0`
- Helper rows: `0`

## Direct Rows

- `revision_notice_id(rn_31, source_md).`
- `revision_date(2027_01_06, source_md).`
- `supersedes(memo_r_19, bulletin_c_14).`
- `approving_body(operations_review).`
- `intake_desk(counter_2).`
- `policy_field_changed(standard_parcel_weight_limit, 18_kg, 22_kg, memo_r_19).`
- `policy_attribute_threshold(standard_parcel_weight_limit, 22_kg, memo_r_19).`
- `policy_field_removed(cold_pack_supervisor_note_requirement, bulletin_c_14, memo_r_19).`
- `policy_field_added(oversized_label_photo_check_requirement, memo_r_19, required).`
- `policy_field_changed(cold_pack_supervisor_note_requirement, required, removed, memo_r_19).`
- `policy_field_changed(oversized_label_photo_check_requirement, not_required, required, memo_r_19).`

## Reading

The replay strengthens the case that transition/delta is already mostly inside
the modern compile surface when the source states the transition explicitly.
This probe produced:

- a direct supersession relation;
- an old/new value row for a numeric threshold;
- separate added/removed rows;
- old/new value rows for add/remove as state transitions;
- stable context rows for unchanged authority/location.

The one imperfection is normalization, not answerability: unchanged authority
and location were emitted as stable context rows rather than `field_unchanged`
or equivalent delta rows. That is acceptable for current QA, but a future
normalization layer may want a cross-domain way to represent stable context
inside a revision.

## Lesson

Do not promote a broad transition/delta compile invariant from this replay.
Across TD-001 through TD-004, role transitions, status transitions,
document-field snapshots, absence persistence, and policy threshold revisions
all answer cleanly with zero helpers. The visible residue is normalization
shape, not missing extraction.
