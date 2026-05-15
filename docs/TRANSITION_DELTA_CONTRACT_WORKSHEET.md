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

## TD-004 - Policy Threshold Revision Replay

Date: 2026-05-15

Question:

Does an unlike policy-threshold revision expose a missing transition/delta
compile surface, or does the modern compiler already emit direct old/new,
added/removed, and supersession rows without helper support?

Before:

TD-001 through TD-003 covered role/membership transitions, status transitions,
document field snapshots, absence persistence, and generic query placeholder
repair. The remaining uncertainty was whether explicit policy/rule revisions
would need a new normalized transition-delta invariant.

Prediction:

If transition/delta is genuinely inside the current compile surface, a compact
policy revision should emit direct rows for supersession, old/new threshold,
removed requirement, added check, and stable context. If it is not inside, QA
should fall back to source text or miss threshold/removal/addition questions.

Intervention:

Added `policy_threshold_revision`, an unlike probe with:

- a memo superseding a bulletin;
- a numeric threshold raised from one value to another;
- one removed requirement;
- one added check;
- unchanged approving body and intake desk.

Ran compile and no-helper QA with OpenRouter at six lanes.

After:

Compile:

- fixtures=`1`
- parsed OK=`1`
- candidate predicates=`9`
- admitted/skipped=`20 / 0`
- rough score=`0.833`

No-helper QA:

- questions=`9`
- exact/partial/miss=`9 / 0 / 0`
- helper rows=`0`
- write proposals=`0`

Surface inspection:

- direct `supersedes/2`;
- direct `policy_field_changed/4` for the threshold old/new value;
- direct `policy_field_removed/3`;
- direct `policy_field_added/3`;
- direct old/new state rows for the removed and added requirements;
- stable context rows for approving body and intake desk.

Artifacts:

- `experiments/transition_delta_contract_v1/policy_threshold_revision/`
- `docs/data/lens_vocabulary_audit/transition_delta_contract_v1_td004_compile_summary_20260515.md`
- `docs/data/lens_vocabulary_audit/transition_delta_contract_v1_td004_compile_summary_20260515.json`
- `docs/data/lens_vocabulary_audit/transition_delta_contract_v1_td004_qa_summary_20260515.md`
- `docs/data/lens_vocabulary_audit/transition_delta_contract_v1_td004_qa_summary_20260515.json`
- `docs/data/lens_vocabulary_audit/transition_delta_contract_v1_td004_surface_inspection_20260515.md`

Verification:

- `python scripts\run_domain_bootstrap_file_batch.py ... --fixture policy_threshold_revision ...` ->
  parsed OK, admitted/skipped=`20 / 0`
- `python scripts\run_domain_bootstrap_qa_batch.py ... --fixture policy_threshold_revision ...` ->
  `9 / 0 / 0`, helpers=`0`
- `python -m pytest tests -q` -> `1241 passed, 2 subtests passed`

Lesson:

Transition/delta is looking less like a missing compile surface and more like a
normalization family. Explicitly stated revisions already compile into
answer-bearing surfaces across role, status, document, and policy threshold
shapes.

The remaining architectural question is not "can the compiler see deltas?" It
is "do we want a deterministic normalization layer that maps equivalent
old/new, added/removed, superseded, and unchanged surfaces into one audit
grammar after compile?" That should be treated as a layer decision, not a
fixture repair.

Next pressure:

Pause broad transition/delta repair. Either design a small deterministic
normalization sketch for transition/delta rows, or return to the lens audit
queue and apply the same evidence to the next unsettled vocabulary. Do not add
compile guidance unless a future unlike replay shows a true absent coordinate.

## TD-005 - Audit-Only Transition Normalizer Prototype

Date: 2026-05-15

Question:

Can the already-emitted transition/delta surfaces be projected into a canonical
audit vocabulary deterministically, without changing compile prompts, QA
selection, or helper delivery?

Before:

TD-004 shifted the pressure from compile-surface absence to normalization. The
compiler produced answer-bearing rows, but equivalent transition ideas appeared
under several shapes:

- `form_replaced/3`
- `field_value_snapshot/4`
- `field_absent/2`
- `transition_occurred/4`
- `policy_field_changed/4`
- `policy_field_added/3`
- `policy_field_removed/3`
- `supersedes/2`

Prediction:

If a deterministic normalization layer is the right next layer, a small
audit-only pass should recover canonical observations across the unlike probes:
supersession, value transition, status transition, field add/remove,
unchanged field, and absence persistence.

Intervention:

Added an audit-only normalizer:

- `src/transition_delta_normalizer.py`
- `scripts/audit_transition_delta_normalization.py`
- `tests/test_transition_delta_normalizer.py`

The normalizer reads admitted compile facts and emits observation dictionaries.
It does not write facts back into the runtime and does not affect compile or QA.

After:

Ran the normalizer over the TD-002 and TD-004 compile JSON files:

- compile files=`3`
- canonical observations=`12`
- kind counts:
  - `absence_persistence`: `1`
  - `field_added`: `1`
  - `field_removed`: `1`
  - `field_unchanged`: `2`
  - `status_transition`: `1`
  - `supersession`: `2`
  - `value_transition`: `4`

The first pass initially missed the status/reason probe, which exposed a
recognizer-vocabulary gap rather than an architecture failure. Adding
`transition_occurred/4` with optional `transition_timestamp/2` and
`transition_reason/2` attachment brought the status probe into the canonical
audit.

Artifacts:

- `docs/data/lens_vocabulary_audit/transition_delta_contract_v1_normalization_audit_20260515.md`
- `docs/data/lens_vocabulary_audit/transition_delta_contract_v1_normalization_audit_20260515.json`

Verification:

- `python -m pytest tests\test_transition_delta_normalizer.py -q` -> `4 passed`
- `python -m pytest tests -q` -> `1245 passed, 2 subtests passed`
- `python scripts\audit_transition_delta_normalization.py ...` ->
  observations=`12`

Lesson:

The deterministic normalization layer is now a concrete candidate, not just an
idea. It should begin as audit/reporting infrastructure because that preserves
the scientific separation:

- compile emits source-grounded surfaces;
- QA answers from admitted surfaces;
- normalization observes equivalent transition/delta structure after the fact.

The recognizer vocabulary should be expected to grow under probe pressure, but
only by accepting reusable predicate contracts. The status transition miss in
the first normalizer pass is the right failure mode: it expanded the recognizer
with a general contract rather than pushing status language into the epistemic
lens or adding another helper.

Next pressure:

Keep the normalizer audit-only for another cycle. Apply it to future transition
probes and one internal fixture compile before integrating it into any selector
or QA pathway. The key question is coverage of reusable predicate contracts,
not answer-score improvement yet.

## TD-006 - Internal Fixture Normalizer Replay

Date: 2026-05-15

Question:

What happens when the audit-only transition/delta normalizer is applied to an
internal fixture with real revision/correction structure, while QA remains
zero-helper and unchanged?

Before:

TD-005 proved the normalizer on focused transition probes. The open question
was whether the same audit vocabulary would see transition structure inside an
internal story-world fixture, where historical helper pressure and source
ledger fallback are much higher.

Prediction:

If modern internal compiles emit direct domain transition facts, the normalizer
should recover observations from admitted predicates such as supersession,
status transition, or field-delta rows. If the transition evidence mostly lives
in source-record ledger rows, the first pass should undercount until a
source-record table recognizer is added.

Intervention:

Compiled `datasets/story_worlds/wildfire_evacuation_revision_order` with the
current instrument and ran zero-helper QA over all 40 questions. Then ran the
audit-only normalizer over the compile output.

Initial normalizer result:

- observations=`0`

Inspection showed the compile admitted sparse domain facts and many
source-record table rows. The source-record ledger contained the visible
transition evidence:

- original order table rows with `order`;
- revised order table rows with `new_order`;
- shared row key `zone`;
- sections distinguishing original and revised order documents.

Added a generic audit recognizer for repeated source-record table snapshots:

- key fields: `zone`, `record`, `document`, `item`, `subject`;
- value pairs: `order/new_order`, `status/new_status`, `state/new_state`,
  `value/new_value`;
- generic transition modifiers such as `downgraded_to_`, `upgraded_to_`, and
  `_unchanged` are normalized away.

After:

No-helper QA:

- questions=`40`
- exact/partial/miss=`33 / 2 / 5`
- helper rows=`0`
- write proposals=`0`
- failure surfaces: `query_surface_gap=4`, `hybrid_join_gap=2`,
  `answer_surface_gap=1`

Normalizer:

- compile files=`1`
- observations=`5`
- kind counts:
  - `source_record_value_transition`: `4`
  - `source_record_subject_added`: `1`

Recovered observations:

- `tc_7`: `mandatory_evacuation` -> `evacuation_warning`
- `tc_8`: `mandatory_evacuation` -> `mandatory_evacuation`
- `tc_9`: `evacuation_warning` -> `mandatory_evacuation`
- `tc_10`: `shelter_in_place_advisory` -> `evacuation_warning`
- `tc_11`: newly added with `evacuation_warning`

Artifacts:

- `docs/data/lens_vocabulary_audit/transition_delta_internal_wildfire_compile_summary_20260515.md`
- `docs/data/lens_vocabulary_audit/transition_delta_internal_wildfire_compile_summary_20260515.json`
- `docs/data/lens_vocabulary_audit/transition_delta_internal_wildfire_qa_nohelpers_summary_20260515.md`
- `docs/data/lens_vocabulary_audit/transition_delta_internal_wildfire_qa_nohelpers_summary_20260515.json`
- `docs/data/lens_vocabulary_audit/transition_delta_internal_wildfire_normalization_audit_20260515.md`
- `docs/data/lens_vocabulary_audit/transition_delta_internal_wildfire_normalization_audit_20260515.json`

Verification:

- `python scripts\run_domain_bootstrap_file_batch.py ... --fixture wildfire_evacuation_revision_order ...` ->
  parsed OK, admitted/skipped=`46 / 82`
- `python scripts\run_domain_bootstrap_qa_batch.py ... --helper-companion-row-limit 0 ...` ->
  `33 / 2 / 5`, helpers=`0`
- `python scripts\audit_transition_delta_normalization.py ...` ->
  observations=`5`
- `python -m pytest tests -q` -> `1246 passed, 2 subtests passed`

Lesson:

The internal fixture does not disprove the transition/delta layer. It shows
where the layer has to look. Focused probes produced domain predicates; the
internal fixture preserved transition structure mainly in deterministic source
ledger table rows. The normalizer can recover that structure without changing
QA or adding helpers.

This is the first concrete bridge from helper-heavy internal fixtures toward
audit-only deterministic normalization: do not ask helpers to carry this
transition structure if source-record table geometry already preserves it.

Next pressure:

Run this audit on 2-3 more helper-heavy internal fixtures before integrating
anything. The key measurement is whether source-record table normalization
recurs across unlike internal documents, or whether this replay is specific to
evacuation/order tables.

## TD-007 - Internal Permit Amendment Normalizer Replay

Date: 2026-05-15

Question:

Does a second internal fixture confirm the source-record table finding from
TD-006, or does a different internal document expose another reusable
transition/delta recognizer family?

Before:

TD-006 recovered evacuation order transitions from deterministic source-record
table geometry. The next question was whether that was an evacuation-table
special case. `municipal_tree_permit_amendment` has a different transition
shape: permit amendment, species/measurement reclassification, procedural
status changes, physical state changes, and current authoritative values.

Prediction:

If the normalizer is still too table-oriented, the permit amendment fixture
should undercount until it recognizes timeline-style domain predicates such as
status/state and identification rows.

Intervention:

Compiled `datasets/story_worlds/municipal_tree_permit_amendment`, ran
zero-helper QA over all 40 questions, then ran the audit-only normalizer.

Initial normalizer result:

- observations=`0`

Inspection showed the compile had strong domain predicates, including:

- `amendment_supersedes/2`
- `tree_identified/5`
- `tree_protection_status/4`
- `tree_physical_state/3`
- `procedural_status/3`

Added audit-only recognizers for:

- generic `*_supersedes/2` as supersession;
- generic `*_status` and `*_state` timelines with subject, value, date;
- identification-style attribute timelines for species and measurement values.

After:

No-helper QA:

- questions=`40`
- exact/partial/miss=`33 / 3 / 4`
- helper rows=`0`
- write proposals=`0`
- failure surfaces: `compile_surface_gap=3`, `hybrid_join_gap=4`

Normalizer:

- compile files=`1`
- observations=`27`
- kind counts:
  - `attribute_observation`: `20`
  - `supersession`: `1`
  - `timeline_value_transition`: `6`

Recovered transition structure included:

- amendment supersedes original permit;
- tree #19 species changed from one classification to another;
- tree #19 measurement changed from one DBH value to another;
- tree #19 protection status changed from eligible-for-removal to protected;
- tree #19 physical state changed from standing to felled to stump-present;
- amendment procedural status changed from filed to issued.

Artifacts:

- `docs/data/lens_vocabulary_audit/transition_delta_internal_tree_compile_summary_20260515.md`
- `docs/data/lens_vocabulary_audit/transition_delta_internal_tree_compile_summary_20260515.json`
- `docs/data/lens_vocabulary_audit/transition_delta_internal_tree_qa_nohelpers_summary_20260515.md`
- `docs/data/lens_vocabulary_audit/transition_delta_internal_tree_qa_nohelpers_summary_20260515.json`
- `docs/data/lens_vocabulary_audit/transition_delta_internal_tree_normalization_audit_20260515.md`
- `docs/data/lens_vocabulary_audit/transition_delta_internal_tree_normalization_audit_20260515.json`

Verification:

- `python scripts\run_domain_bootstrap_file_batch.py ... --fixture municipal_tree_permit_amendment ...` ->
  parsed OK, admitted/skipped=`109 / 11`
- `python scripts\run_domain_bootstrap_qa_batch.py ... --helper-companion-row-limit 0 ...` ->
  `33 / 3 / 4`, helpers=`0`
- `python scripts\audit_transition_delta_normalization.py ...` ->
  observations=`27`
- `python -m pytest tests -q` -> `1248 passed, 2 subtests passed`

Lesson:

The second internal fixture confirms the general direction but changes the
recognizer family. Internal transition structure is not only table geometry;
it also appears as timeline-like domain predicates. That supports the
normalizer as a deterministic audit layer over multiple reusable contracts.

It also sharpens the helper-retirement path: if zero-helper QA is already
`33/40` on two internal fixtures and the normalizer recovers the transition
structure post-compile, helper pressure should be audited for remaining gaps
rather than assumed necessary.

Next pressure:

Start the foreign-language leakage probe before broadening the normalizer
again. The multilingual fixture should test whether trigger conditions,
source-record labels, date/number handling, placeholder repair, and QA planning
are secretly English-shaped.

## TD-008 - Entity/Role Transition Normalizer Replay

Date: 2026-05-15

Question:

Does the entity/role lens residue from LV-018 belong in the transition/delta
normalizer rather than in entity/role-specific compile guidance?

Before:

LV-018 reached perfect no-helper QA on three unlike entity/role probes, but the
vocabulary audit still showed residue:

- `membership`: shallow/source-only because join/leave language compiled as role
  and relative-time rows rather than direct membership-transition rows;
- `role_transition`: source-only because the compile emitted current/prior role
  facts and cessation, but not a single direct replacement row.

The existing transition/delta normalizer recovered document, status, table,
related-document, and timeline transitions. When run unchanged over the
entity/role compiles, it produced zero observations.

Prediction:

If the residue is structural, the admitted direct facts should already bind the
minimum slots for at least part of the transition: subject, role, scope, current
state, ended prior state, and a unique predecessor/successor relation. If the
normalizer has to read source prose or fixture labels to recover it, the repair
does not belong.

Intervention:

Added an audit-only entity/role transition recognizer to
`src/transition_delta_normalizer.py`:

- `holds_role(Person, Role, Scope)` emits a `role_lifecycle_state` with
  `state=current`;
- `held_role(Person, Role, Scope)` plus
  `role_cessation(Person, Role, Scope)` emits a `role_lifecycle_state` with
  `state=ended`;
- a `role_holder_transition` is emitted only when exactly one current holder and
  exactly one ended prior holder share the same role and scope.

The recognizer does not read source-record prose, fixture names, question
strings, or local entity vocabulary. It uses only admitted direct fact
predicates and slot equality.

After:

Entity/role transition normalization over the LV-018 compiles:

- files=`3`
- observations=`6`
- kind counts:
  - `role_lifecycle_state`: `5`
  - `role_holder_transition`: `1`

Recovered:

- current role lifecycle states for directly bound role holders;
- ended prior role lifecycle state where prior role and cessation shared slots;
- one unique role-holder transition binding predecessor, successor, role, and
  scope.

The badge/alias fixture still produced zero transition observations because it
uses `held_role/4` for standing/temporary role typing rather than a current/prior
cessation pattern. That is correct: standing-vs-temporary role classification is
not the same contract as role-holder replacement.

Artifacts:

- `src/transition_delta_normalizer.py`
- `tests/test_transition_delta_normalizer.py`
- `docs/data/lens_vocabulary_audit/transition_delta_entity_role_normalization_audit_20260515.md`
- `docs/data/lens_vocabulary_audit/transition_delta_entity_role_normalization_audit_20260515.json`

Verification:

- `python -m py_compile src\transition_delta_normalizer.py scripts\audit_transition_delta_normalization.py`
- `python -m pytest tests\test_transition_delta_normalizer.py -q` -> `10 passed`
- `python -m pytest tests\test_lens_vocabulary_transfer.py tests\test_transition_delta_normalizer.py -q` -> `52 passed`
- `python scripts\audit_transition_delta_normalization.py ...` ->
  observations=`6`

Lesson:

The entity/role residue was not a reason to broaden entity/role guidance. It was
another transfer point for the transition/delta layer. This is the new layer
becoming clearer: vocabulary families can remain strict, while a deterministic
normalizer recovers reusable before/after and lifecycle contracts from admitted
facts after compile.

The uniqueness gate matters. A role-holder transition is structural only when
the facts bind one current holder and one ended prior holder for the same role
and scope. Multiple current holders, missing cessation, or role typing without
replacement should stay lifecycle/classification evidence, not transition
evidence.

Next pressure:

Replay the transition/delta normalizer across the existing operational-status
and epistemic pending/supersession probe compiles as a cross-lens audit sweep.
Do not add more recognizers until the replay shows a repeated missing contract.

## TD-009 - Cross-Lens Supersession Direction Replay

Date: 2026-05-15

Question:

Do operational-status and epistemic lifecycle compiles expose repeated
transition/delta contracts that the normalizer still misses?

Before:

TD-008 added entity/role lifecycle recovery and named the next step as a
cross-lens replay. The candidate compiles were:

- six operational record/status palette probes;
- one epistemic pending/supersession lifecycle probe.

Initial replay with the TD-008 normalizer produced only one observation:

- `timeline_value_transition`: `1`

Inspection showed a repeated missing contract: the compiler often emits
`superseded_by(Old, New)` or `record_superseded_by(Old, New)`, while the
normalizer only recognized `supersedes(New, Old)` and `*_supersedes(New, Old)`.
That is a predicate-direction synonym, not a domain-specific phrase.

Prediction:

If the contract is generic, adding `superseded_by` directionality should recover
supersession observations across both operational and epistemic probes without
new helper rows, source prose parsing, or fixture vocabulary.

Intervention:

Extended the audit-only normalizer:

- `superseded_by(Predecessor, Successor)` emits a `supersession`;
- `*_superseded_by(Predecessor, Successor)` emits a `supersession`;
- related-document comparison uses the same predecessor/successor direction for
  value comparisons.

After:

Cross-lens replay:

- files=`7`
- observations=`12`
- kind counts:
  - `supersession`: `10`
  - `related_document_value_unchanged`: `1`
  - `timeline_value_transition`: `1`

Recovered:

- operational record supersessions from `record_superseded_by/2`;
- epistemic note/status supersessions from `superseded_by/2`;
- one related-document unchanged value across superseded lifecycle events;
- the already-visible ticket-status timeline transition.

Artifacts:

- `src/transition_delta_normalizer.py`
- `tests/test_transition_delta_normalizer.py`
- `docs/data/lens_vocabulary_audit/transition_delta_cross_lens_replay_20260515.md`
- `docs/data/lens_vocabulary_audit/transition_delta_cross_lens_replay_20260515.json`

Verification:

- `python -m py_compile src\transition_delta_normalizer.py scripts\audit_transition_delta_normalization.py`
- `python -m pytest tests\test_transition_delta_normalizer.py -q` -> `10 passed`
- `python -m pytest tests\test_lens_vocabulary_transfer.py tests\test_transition_delta_normalizer.py tests\test_domain_bootstrap_file.py -q` -> `82 passed`
- `python scripts\audit_transition_delta_normalization.py ...` ->
  observations=`12`

Lesson:

The new layer is not a bag of domain adapters. It is a deterministic contract
normalizer over admitted facts. `supersedes(New, Old)` and
`superseded_by(Old, New)` are the same structural relation expressed in opposite
predicate direction. Normalizing that relation lets multiple lens families share
the same downstream audit surface.

The replay also shows what not to do. Most operational lifecycle residue is not
fixed by adding more transition recognizers. Existing operational diagnostics
still show alias splits, phase-classification gaps, and supersession-target
collapse. Those are profile/identity/palette issues. The normalizer should
recover transitions that are already structurally present; it should not invent
missing lifecycle records from source prose.

Next pressure:

Audit the remaining lens families for structural residue, but split the response
by layer:

- if facts already bind before/after state, add a deterministic normalizer
  contract;
- if facts are shallow because identity aliases split, inspect profile palette or
  identity normalization;
- if facts are absent, create a focused unlike probe before any compile guidance.

## TD-010 - Operational Status Phase And Assignment Replay

Date: 2026-05-15

Question:

Do the remaining operational-record/status QA misses expose reusable
transition/delta contracts already present in admitted facts?

Before:

The operational-record/status palette run scored `46 / 0 / 2` with zero helper
rows over six unlike probes. The two not-exact rows were:

- an assignment question where `record_assigned_to(record, actor, date)` existed
  but the assignment purpose/scope was not a bound slot;
- an initial-status question where the source and profile expectation named the
  initial status, but no direct initial-status row was admitted.

The TD-009 normalizer replay over the two miss fixtures saw only supersession
contracts, so it was blind to admitted status-phase and assignment rows.

Prediction:

If operational status phase and assignment rows are structural, the normalizer
should recover them from direct facts only. It should not recover the missing
initial status from source-record text, because that would turn the normalizer
into a prose parser.

Intervention:

Added two audit-only recognizers:

- `record_status_phase(Subject, Status, Date)` and
  `*_status_phase(Subject, Status, Date)` emit `status_phase_observation` and
  feed timeline-transition recovery.
- The same recognizer also accepts the observed profile-palette variant
  `record_status_phase(Subject, Date, Status)` when the middle slot is a
  temporal anchor.
- `record_assigned_to(Subject, Assignee, Date)` and
  `*_assigned_to(Subject, Assignee, Date)` emit `assignment_observation`.

These contracts use predicate shape and temporal-slot detection only. They do
not read source prose, fixture names, question strings, or answer keys.

After:

Two-miss replay:

- files=`2`
- observations=`9`
- kind counts:
  - `assignment_observation`: `1`
  - `status_phase_observation`: `3`
  - `supersession`: `3`
  - `timeline_value_transition`: `2`

Full operational palette replay:

- files=`6`
- observations=`36`
- kind counts:
  - `status_phase_observation`: `15`
  - `timeline_value_transition`: `11`
  - `supersession`: `8`
  - `assignment_observation`: `1`
  - `related_document_value_unchanged`: `1`

Artifacts:

- `src/transition_delta_normalizer.py`
- `tests/test_transition_delta_normalizer.py`
- `docs/data/lens_vocabulary_audit/transition_delta_operational_two_miss_replay_20260515.md`
- `docs/data/lens_vocabulary_audit/transition_delta_operational_two_miss_replay_20260515.json`
- `docs/data/lens_vocabulary_audit/transition_delta_operational_palette_replay_20260515.md`
- `docs/data/lens_vocabulary_audit/transition_delta_operational_palette_replay_20260515.json`

Verification:

- `python -m py_compile src\transition_delta_normalizer.py scripts\audit_transition_delta_normalization.py`
- `python -m pytest tests\test_transition_delta_normalizer.py -q` -> `11 passed`
- `python -m pytest tests\test_lens_vocabulary_transfer.py tests\test_transition_delta_normalizer.py tests\test_domain_bootstrap_file.py -q` -> `85 passed`

Lesson:

Operational status uses a structural event spine, but the palette still wobbles
in slot order and granularity. `record_status_phase(subject, status, date)` and
`record_status_phase(subject, date, status)` are the same contract, so the
normalizer should absorb that deterministic variation. This is a clean
normalization win, not a fixture-specific repair.

The two original misses split cleanly by layer. The assignment miss has a
recoverable assignment row but no task/scope slot, so it is a query/projection
or profile-contract pressure. The initial-status miss has no admitted
initial-status fact; it remains compile-surface pressure. The normalizer must
not fill that gap by reading ledger prose.

Next pressure:

Do not broaden operational guidance from these two misses. If assignment-scope
questions recur, add a focused profile-palette probe for assignment purpose or
scope slots. If initial/current status omissions recur, treat them as compile
surface gaps and test with focused unlike probes before changing guidance.
