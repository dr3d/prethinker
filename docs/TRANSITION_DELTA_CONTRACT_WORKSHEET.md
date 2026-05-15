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

## TD-002 - Field Delta Replay And Query-Surface Split

Date: 2026-05-15

Question:

Does a second document-field delta and a second status/reason delta confirm a
compile-surface field-delta gap, or split the pressure into another layer?

Before:

TD-001 showed:

- role/membership transitions: direct transition rows and perfect QA;
- status transitions: direct transition rows and perfect QA;
- document field delta: answerable through predecessor/current and old/new
  field rows, but without a single field-delta contract row.

The next question was whether document field delta was a compile-surface gap or
just a less-normalized but still queryable surface.

Prediction:

If document field delta is missing as a compile surface, a second document
probe should fail or require source text for changed/unchanged/absent fields.
If the facts are present but the planner struggles, misses should point to
query construction rather than absent predicates.

Intervention:

Added two focused unlike probes:

- `document_section_delta`: old form replaced by revised form, checklist
  section changes, applicant and fee unchanged, emergency contact absent from
  both forms.
- `status_reason_delta`: ticket status and reason change, reviewer/category
  unchanged, explicit not-rejected state, payment receipt unstated.

Ran compile and no-helper QA with OpenRouter at six lanes.

After:

Compile:

- fixtures=`2`
- parsed OK=`2`
- candidate predicates=`16`
- admitted/skipped=`43 / 0`
- rough scores=`0.889`

No-helper QA:

- questions=`17`
- exact/partial/miss=`16 / 0 / 1`
- helper rows=`0`

Surface inspection:

- `document_section_delta` emitted replacement, active form, before/after
  section snapshots, unchanged fields, and two direct `field_absent/2` rows.
- `status_reason_delta` emitted status transition, transition time, post-change
  reason, unchanged reviewer/category, unstated payment receipt, and
  not-rejected state.
- The one miss was "Which field remained absent from both forms?" The facts
  were present, but the generated query used lowercase `form` as a constant:
  `field_absent(form, emergency_contact).`

Artifacts:

- `experiments/transition_delta_contract_v1/document_section_delta/`
- `experiments/transition_delta_contract_v1/status_reason_delta/`
- `docs/data/lens_vocabulary_audit/transition_delta_contract_v1_td002_compile_summary_20260515.md`
- `docs/data/lens_vocabulary_audit/transition_delta_contract_v1_td002_compile_summary_20260515.json`
- `docs/data/lens_vocabulary_audit/transition_delta_contract_v1_td002_qa_summary_20260515.md`
- `docs/data/lens_vocabulary_audit/transition_delta_contract_v1_td002_qa_summary_20260515.json`
- `docs/data/lens_vocabulary_audit/transition_delta_contract_v1_td002_surface_inspection_20260515.md`

Verification:

- `python -m pytest tests\test_domain_bootstrap_qa.py -q` -> `170 passed`
- focused replay after the query repair:
  `document_section_delta` -> `8 / 0 / 0`, helper rows=`0`
- `python -m pytest tests -q` -> `1241 passed, 2 subtests passed`

Lesson:

The pressure split again. Field-delta compile surface is not absent: old/new
snapshots, unchanged fields, and absent fields are all emitted. The miss is
query-surface handling for quantifier-like language over record versions:
"both forms", "all versions", "remained absent", "stayed unstated".

This means the next repair should not be a compile guidance patch yet. A
generic field-delta contract may still be useful for normalization, but the
first observed failure after replay is a planner variable-binding error over an
existing predicate family.

The epistemic overlap also becomes clearer: "remained absent/unstated" can
look epistemic, but here it is a transition query over two source objects. The
epistemic recognizer should not absorb it.

Next pressure:

Do a tiny query-surface unit repair for lowercase generic placeholders in
generated Prolog queries when the source question asks over "both/all"
documents, records, versions, forms, packets, or statuses. Keep it predicate-
agnostic and test it on a generic `field_absent(Form, Field)` shape.

## TD-003 - Generic Object/Field Placeholder Repair

Date: 2026-05-15

Question:

Can the TD-002 miss be repaired as a generic query-surface slot-binding issue
without adding helper rows, compile guidance, or fixture-specific vocabulary?

Before:

TD-002 found one miss on an otherwise clean no-helper document-section delta
probe. The compiler had emitted the answer-bearing facts:

- `field_absent(of_2, emergency_contact).`
- `field_absent(rf_5, emergency_contact).`

The failed query treated the generic document object label as an atom:
`field_absent(form, emergency_contact).`

Prediction:

If this is a generic placeholder problem, extending the existing placeholder
repair vocabulary with document-object and field-slot labels should be enough.
The repair should convert lowercase generic slot labels into variables while
leaving concrete values such as `emergency_contact` bound.

Intervention:

Extended the existing query placeholder repair to recognize generic
document/version object labels and field-slot labels:

- `field`
- `form`
- `document`
- `packet`
- `version`

Added unit coverage for:

- `field_absent(form, emergency_contact).` ->
  `field_absent(Form, emergency_contact).`
- `field_absent(document, field).` ->
  `field_absent(Document, Field).`

No predicate-specific logic was added.

After:

Focused QA replay on the document-section delta probe:

- questions=`8`
- exact/partial/miss=`8 / 0 / 0`
- helper rows=`0`
- write proposals=`0`

Artifacts:

- `docs/data/lens_vocabulary_audit/transition_delta_contract_v1_td003_qa_summary_20260515.md`
- `docs/data/lens_vocabulary_audit/transition_delta_contract_v1_td003_qa_summary_20260515.json`

Verification:

- `python -m pytest tests\test_domain_bootstrap_qa.py -q` -> `170 passed`
- `python -m pytest tests -q` -> `1241 passed, 2 subtests passed`
- `python scripts\run_domain_bootstrap_qa_batch.py ... --fixture document_section_delta ...` ->
  `8 / 0 / 0`, helpers=`0`

Lesson:

This repair belongs to the query-surface layer, not the transition/delta
compile layer and not the epistemic lens. "Both forms" and "all versions"
often create generic placeholders in the query plan; those placeholders should
bind over source objects instead of becoming constants.

The repair remains fixture-free because it names structural slot kinds rather
than local source names, row IDs, answer strings, or fixture labels.

Next pressure:

Return to transition/delta contract design only after more replay shows a
recurring absence of direct old/new/supersession rows. The current observed gap
was query binding over existing surfaces, so the next architectural pass should
continue auditing transition/delta surfaces before promoting a new compile
invariant.
