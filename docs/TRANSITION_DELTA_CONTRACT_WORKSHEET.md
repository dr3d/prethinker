# Transition/Delta Contract Worksheet

This worksheet starts only because two independent lens-audit passes exposed the
same residue:

- LV-017: a document supersession question blurred the old/new missing-item
  binding after a replacement.
- LV-018: entity/role QA was perfect, but membership and role-transition terms
  remained shallow/source-only because direct transition rows were not emitted.

Doctrine:

- Do not encode fixture names, question IDs, answer strings, or local story
  vocabulary.
- Treat transition/delta as a candidate contract until unlike probes show
  transfer.
- A valid contract should bind field, old value, new value, subject, transition
  event, and scope/effective time when the source provides them.
- It must also distinguish unchanged fields from changed fields and negative
  status from absent evidence.

## TD-001 - Initial Unlike Transition/Delta Probe

Date: 2026-05-15

Question:

Does the current compiler already emit enough direct surface for generic
transition and field-delta questions, or are before/after values mostly
answerable only through nearby facts and source text?

Before:

The current lens-audit work shows strong answerability with zero helper rows,
but two residues point to the same missing contract:

- document supersession can expose predecessor/successor and field values
  without cleanly binding the changed field from old value to new value;
- entity/role compiles can expose current/previous role facts and cessation
  without a direct replacement or membership-transition row.

Prediction:

If the current surface is enough, three focused unlike probes should answer
transition questions cleanly and the compile should show direct rows such as
`changed_from_to`, `field_changed`, `status_transition`,
`role_transition`, or equivalent structural predicates. If not, QA may still
score well, but the facts will be assembled from adjacent role/status/source
rows rather than a reusable transition contract.

Intervention:

Added three unlike probes:

- `role_membership_transition`: join, leave, role replacement, before/after
  contact, unchanged role.
- `document_field_delta`: replacement packet, changed missing item, unchanged
  field, still-unstated field.
- `status_value_transition`: status change, reason change, unchanged technician
  and location, explicit negative cancellation.

After:

Compile:

- fixtures=`3`
- parsed OK=`3`
- candidate predicates=`23`
- admitted/skipped=`78 / 1`
- rough scores=`0.889`

No-helper QA:

- questions=`22`
- exact/partial/miss=`22 / 0 / 0`
- helper rows=`0`

Surface inspection:

- role/membership transition emitted direct `membership_transition/4`,
  `role_transition/5`, `transition_context/2`, and related effective-date rows.
- status transition emitted direct `status_transition/5`, `transition_actor/2`,
  and pre/post `attribute_value/4` rows.
- document field delta emitted predecessor/current rows and old/new
  `field_value/3` rows, plus `field_unchanged/2`, but did not emit a direct
  field-delta row binding changed field, old value, new value, predecessor,
  successor, and scope.

Artifacts:

- `experiments/transition_delta_contract_v1/`
- `docs/data/lens_vocabulary_audit/transition_delta_contract_v1_compile_summary_20260515.md`
- `docs/data/lens_vocabulary_audit/transition_delta_contract_v1_compile_summary_20260515.json`
- `docs/data/lens_vocabulary_audit/transition_delta_contract_v1_qa_summary_20260515.md`
- `docs/data/lens_vocabulary_audit/transition_delta_contract_v1_qa_summary_20260515.json`
- `docs/data/lens_vocabulary_audit/transition_delta_contract_v1_surface_inspection_20260515.md`

Verification:

- `python -m pytest tests -q` -> `1239 passed, 2 subtests passed`

Lesson:

Transition/delta is not just epistemic vocabulary in disguise. It appears as a
cross-lens contract family:

- role/membership transitions are already structurally emitted on a focused
  unlike probe;
- status transitions are already structurally emitted on a focused unlike
  probe;
- document field deltas are answerable, but still assembled from adjacent
  predecessor/current and field-value rows.

This matches the warning from LV-017: object-bound unstated fields can overlap
with supersession, but the repair target is the changed-field binding, not a
broader epistemic recognizer.

Next pressure:

Do not write broad compile guidance yet. Add one more compact document-field
delta and one status/reason delta, then decide whether a generic field-delta
contract has enough transfer evidence to become a compile-surface invariant.
