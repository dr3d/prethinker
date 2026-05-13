# Guard Generalization Worksheet

Last updated: 2026-05-12 UTC / 2026-05-11 local run window

This is the CTO compression archive for turning selector guards into reusable
architecture without letting fixture vocabulary become substrate. The active
post-compression workbench is now `docs/BOUNDARY_HUNT_WORKSHEET.md`; return to
this file only when a boundary hunt reveals a new transferable guard
replacement or when updating the compression history.

Date convention: progress-entry `Date:` fields use UTC day. Some artifact
directories use the local run-day suffix when work crosses midnight UTC; that
is expected and should not be read as stale history by itself.

## Progress Journal

Trajectory format:

```text
before -> intervention -> after -> next pressure
```

Every entry should make the direction of travel visible. A result is not just a
score; it is evidence about whether the architecture is moving from guard scars
toward reusable substrate, selector scoring, helper contracts, or retirement.

### GG-001 - Count/Measure Scoring And Helper-Pressure Audit

Date: 2026-05-12

Scope: cross-harness guard/helper generalization.

Trajectory:

```text
13 high-priority helper-pressure guards
  -> count/measure scoring plus helper-pressure audit surfaces
  -> six-fixture QA10 at 54 / 4 / 2 and measured helper pressure
  -> duplicate helper delivery and source-record assignment transfer/pruning
```

Changed surfaces:

- `scripts/select_qa_mode_without_oracle.py` now has a reusable
  count/measure-focused scoring principle for compact rows that bind the
  requested measure, population, scope, time/status, and operands.
- `scripts/run_domain_bootstrap_qa_batch.py` can summarize existing QA runs and
  reports helper pressure in batch summaries.
- `scripts/audit_helper_usage.py` now reports answer-normalized helper pressure,
  candidate pruning targets by helper/support kind, and both delivered and
  unique helper-row breadth.

Measured result:

```text
OpenRouter six-fixture QA10:
  exact / partial / miss: 54 / 4 / 2
  runtime load errors: 0
  write proposals: 0

Helper usage audit over the same artifacts:
  delivered support-row occurrences: 8847
  unique helper rows: 229
  helper rows per exact answer: 163.833
  candidate-helper share: 0.5289
  pressure label: high_candidate_helper_pressure

Top candidate pruning target:
  helper: roster_state_support
  support kind: source_record_student_group_assignment
  delivered candidate rows: 4040
  unique candidate rows: 108
```

Artifacts:

- `tmp/openrouter_helper_pressure_qa10_20260511/qa_batch_summary.json`
- `tmp/openrouter_helper_pressure_qa10_20260511/qa_batch_summary.md`
- `tmp/helper_usage_pressure_20260512.json`
- `tmp/helper_usage_pressure_20260512.md`

Verification:

```powershell
python -m pytest tests/test_audit_helper_usage.py tests/test_audit_helper_classes.py -q
python -m pytest tests/test_domain_bootstrap_qa_batch.py tests/test_public_doc_link_domains.py -q
python -m pytest -q
```

Latest full verification: `996 passed, 2 subtests passed`.

Lesson:

Helper pressure has two different meanings. Delivered row volume can be harness
packaging pressure when identical helper tables are repeated across result
slots. Unique candidate-helper breadth is the real substrate transfer/pruning
pressure. The next guard-generalization work should first reduce duplicate
delivery, then decide whether source-record assignment rows deserve a generic
ledger or should remain candidate-labeled until sibling transfer proves them.

### GG-002 - Canonical Helper Delivery Audit

Date: 2026-05-12

Scope: cross-harness helper-pressure measurement.

Trajectory:

```text
audit walked both canonical query results and provenance copies
  -> count only canonical query_results, falling back to evidence-plan results when needed
  -> delivered helper pressure drops from 8847 to 5525 rows while unique breadth stays 229
  -> remaining pressure is repeated canonical helper tables plus candidate-row transfer
```

Changed surface:

- `scripts/audit_helper_usage.py` now treats top-level `query_results` as the
  canonical delivered evidence surface. It no longer double-counts the same
  support table stored under `evidence_bundle_plan_query_results` for
  provenance.
- `tests/test_audit_helper_usage.py` now has a regression test proving that a
  helper table duplicated across those two fields counts once.

Measured result:

```text
Before canonicalization:
  delivered support-row occurrences: 8847
  helper rows per exact answer: 163.833
  top source-record assignment target: 4040 delivered / 108 unique

After canonicalization:
  delivered support-row occurrences: 5525
  helper rows per exact answer: 102.315
  top source-record assignment target: 2535 delivered / 108 unique
  unique helper rows: 229
```

Verification:

```powershell
python -m pytest tests/test_audit_helper_usage.py tests/test_audit_helper_classes.py -q
```

Lesson:

The first duplicate-delivery problem was measurement-side provenance replay,
not helper architecture. The remaining delivered/unique gap is still real: the
same canonical helper tables appear repeatedly across question result slots.
That is now the next packaging/routing target, separate from whether the `108`
unique source-record assignment rows can transfer as generic substrate.

### GG-003 - OpenRouter QA20 Pressure Refresh

Date: 2026-05-12

Scope: six-lane hosted QA pressure over the existing OpenRouter compile set.

Trajectory:

```text
QA10 gave a fast first pressure map at 54 / 4 / 2
  -> six OpenRouter lanes reran the same fixture set to 20 questions each
  -> QA20 scored 112 / 3 / 5 with 0 runtime load errors and 0 write proposals
  -> next work is source-addressability/date-surface repair plus helper-table packaging
```

Measured result:

```text
OpenRouter six-fixture QA20:
  questions: 120
  exact / partial / miss: 112 / 3 / 5
  exact rate: 0.9333
  runtime load errors: 0
  write proposal rows: 0

Fixture scores:
  dream_library_index: 20 / 0 / 0
  festival_permit_maze: 18 / 2 / 0
  greenhouse_quarantine: 18 / 1 / 1
  hospital_shift_exception_log: 17 / 0 / 3
  sable_creek_budget: 20 / 0 / 0
  school_activity_roster_reconciliation: 19 / 0 / 1

Canonical helper pressure:
  delivered support-row occurrences: 10086
  unique helper rows: 236
  helper rows per exact answer: 90.054
  candidate-helper share: 0.5291
  top source-record assignment target: 4641 delivered / 108 unique
```

Artifacts:

- `tmp/openrouter_helper_pressure_qa20_20260511/qa_batch_summary.json`
- `tmp/openrouter_helper_pressure_qa20_20260511/qa_batch_summary.md`
- `tmp/helper_usage_pressure_qa20_20260512.json`
- `tmp/helper_usage_pressure_qa20_20260512.md`

Lesson:

The hosted lane is productive when kept warm: six parallel fixtures finished in
about nine minutes and preserved the governance boundary. The new misses are
not permission for fixture-specific guards. They cluster around reusable gaps:
source document/addressability rows, explicit date/deadline derivation, and
statement/source provenance. The helper-pressure story also sharpened: unique
candidate assignment breadth stayed at `108`, while delivered rows grew with
more questions. That points to packaging/routing pressure, not new parser
vocabulary.

### GG-004 - Conjunctive Evidence Bundle Queries

Date: 2026-05-12

Scope: source-addressability query execution over already-admitted facts.

Trajectory:

```text
hospital source-document questions missed because conjunctive source-record
queries were misread as impossible arities such as source_record_row/8
  -> evidence-bundle executor now validates every predicate in a conjunction
  -> hospital q010 and q013 flip from miss to exact on OpenRouter replay
  -> q009 remains a narrower source-token/query-surface gap
```

Changed surfaces:

- `scripts/run_domain_bootstrap_qa.py` now parses evidence-bundle query
  templates as either a single predicate or a top-level conjunction. It checks
  every predicate/arity in the conjunction against the compiled inventory
  before execution.
- `tests/test_domain_bootstrap_qa.py` now covers a conjunctive
  `source_record_row` + `source_record_text_atom` + `source_record_numeric_token`
  support query.

Measured result:

```text
Hospital OpenRouter first-13 replay:
  before: q009 miss, q010 miss, q013 miss in the QA20 artifact
  after:  q009 miss, q010 exact, q013 exact
  slice score: 12 / 0 / 1
  runtime load errors: 0
  write proposal rows: 0
```

Artifacts:

- `tmp/openrouter_conjunctive_evidence_replay_20260511/qa_batch_summary.json`
- `tmp/openrouter_conjunctive_evidence_replay_20260511/qa_batch_summary.md`

Lesson:

This is not a hospital-specific fix. The reusable principle is that evidence
bundles may need conjunctive joins across admitted source-record rows, text
atoms, numeric tokens, and semantic event predicates. The authority boundary is
unchanged: every predicate in the conjunction must already exist in the
compiled inventory, and no durable fact is written. The remaining q009 miss
points to a separate generic issue: source token normalization and source-name
addressability for event log rows.

### GG-005 - Source-Record Numeric Token Query Repair

Date: 2026-05-12

Scope: deterministic source-record ledger query normalization.

Trajectory:

```text
hospital q009 still missed after conjunction support because the evidence
bundle queried source_record_numeric_token(Line, '14_02_51')
while the deterministic ledger stores source numeric tokens as v_14_02_51
  -> query execution now repairs unprefixed source_record_numeric_token constants
  -> hospital first-13 OpenRouter replay reaches 13 / 0 / 0
  -> next pressure moves back to the broader QA20 date/deadline and helper-packaging gaps
```

Changed surfaces:

- `scripts/run_domain_bootstrap_qa.py` now repairs only
  `source_record_numeric_token/2` constants from quoted/unprefixed forms such
  as `'14_02_51'` to deterministic ledger atoms such as `v_14_02_51`.
- `tests/test_domain_bootstrap_qa.py` covers the repair inside a conjunctive
  source-record query.

Measured result:

```text
Hospital OpenRouter first-13 replay:
  after GG-004: 12 / 0 / 1
  after GG-005: 13 / 0 / 0
  q009: miss -> exact
  runtime load errors: 0
  write proposal rows: 0
```

Artifacts:

- `tmp/openrouter_numeric_token_replay_20260511/qa_batch_summary.json`
- `tmp/openrouter_numeric_token_replay_20260511/qa_batch_summary.md`

Lesson:

This is a ledger-contract repair, not a fixture-language patch. The model can
reasonably ask for a source numeric token as the visible time value; the
deterministic ledger stores the canonical token with a `v_` prefix. Query
execution may bridge that exact representation mismatch for
`source_record_numeric_token/2`, while leaving other predicates and arbitrary
constants alone.

### GG-006 - Source-Addressability QA20 Transfer Check

Date: 2026-05-12

Scope: six-lane hosted QA20 replay after conjunctive evidence-bundle and
source numeric-token repairs.

Trajectory:

```text
QA20 before source-addressability repairs scored 112 / 3 / 5
  -> rerun the same six hosted fixture lanes after GG-004 and GG-005
  -> QA20 scores 113 / 0 / 7 with 0 runtime load errors and 0 write proposals
  -> remaining work is query-planning/answer-surface stability, not source executor safety
```

Measured result:

```text
OpenRouter source-addressability QA20:
  questions: 120
  exact / partial / miss: 113 / 0 / 7
  exact rate: 0.9417
  runtime load errors: 0
  write proposal rows: 0

Notable flips relative to the prior QA20 artifact:
  festival q003: partial -> exact
  festival q006: partial -> exact
  greenhouse q009: partial -> exact
  hospital q009: miss -> exact
  hospital q010: miss -> exact
  school activity q018: miss -> exact

New or shifted misses:
  greenhouse q007, greenhouse q018
  hospital q013
  sable q017
  school activity q009, q012, q020

Canonical helper pressure:
  delivered support-row occurrences: 7804
  unique helper rows: 236
  helper rows per exact answer: 69.062
  candidate-helper share: 0.5254
  top source-record assignment target: 3563 delivered / 108 unique
```

Artifacts:

- `tmp/openrouter_source_addressability_qa20_20260511/qa_batch_summary.json`
- `tmp/openrouter_source_addressability_qa20_20260511/qa_batch_summary.md`
- `tmp/helper_usage_pressure_source_addressability_qa20_20260512.json`
- `tmp/helper_usage_pressure_source_addressability_qa20_20260512.md`

Lesson:

The source-addressability executor repairs transfer, but hosted QA20 remains a
stochastic query-planning pressure instrument. The durable gain is not "this
fixture score only went up"; it is that source-record conjunctions and numeric
ledger-token constants no longer fail structurally, with no runtime errors and
no writes. The next bounded substrate work should stabilize answer-surface
selection for repeated count/date/source questions rather than add local
guards for the shifted misses.

### GG-007 - Identifier Display Judgment Contract

Date: 2026-05-12

Scope: normalized identifier answer-surface judging.

Trajectory:

```text
school activity q012 shifted to miss because cn_2026_04_15 was not accepted as
the display identifier CN-2026-04-15
  -> QA judge policy now treats identical alphanumeric identifier token
     sequences as equivalent across case, hyphen, and underscore display forms
  -> school first-12 OpenRouter replay reaches 12 / 0 / 0
  -> next pressure is role/alias equivalence and duration surfaces, not
     identifier punctuation
```

Changed surfaces:

- `scripts/run_domain_bootstrap_qa.py` QA judge policy now includes an
  identifier-display rule for normalized atoms such as `cn_2026_04_15`,
  `ar_2026_027`, `rc_2026_04_20_v`, and `sc_2026_04_22`.
- `tests/test_domain_bootstrap_qa.py` asserts that this policy remains present
  in the judge contract.

Measured result:

```text
School activity first-12 OpenRouter replay:
  q012: miss -> exact
  slice score: 12 / 0 / 0
  runtime load errors: 0
  write proposal rows: 0
```

Artifacts:

- `tmp/openrouter_identifier_display_replay_20260511/qa_batch_summary.json`
- `tmp/openrouter_identifier_display_replay_20260511/qa_batch_summary.md`

Lesson:

This is a judging contract repair, not a new selector guard. The KB stores
canonical normalized atoms; references and users often render the same
identifier with uppercase letters and hyphens. When the alphanumeric token
sequence is identical, punctuation and case alone should not turn a supported
answer into a miss.

### GG-008 - Fresh Hosted Pressure And Compact Interval Duration

Date: 2026-05-12

Scope: hosted QA cadence, query-only interval duration derivation, and helper
pressure measurement hygiene.

Trajectory:

```text
school activity q020 shifted to a duration miss/partial because the compile
surface exposed a compact same-day interval atom, not separate start/end facts
  -> query execution can now derive a query-only duration companion from a
     compact interval already bound by a prior successful query
  -> fresh six-lane OpenRouter QA20, with cache disabled, moves the school
     first-20 slice to 20 / 0 / 0
  -> next pressure is reducing helper delivery volume and keeping local
     packet/support-kind names out of permanent architecture
```

Changed surfaces:

- `scripts/run_domain_bootstrap_qa.py` now recognizes compact same-day interval
  atoms such as `2026_05_02_11_00_12_30` when an elapsed-time query fails after
  a prior query already bound the interval variable. It emits a query-only
  `compact_interval_duration_support` row; it does not add durable facts or
  fixture-specific predicates.
- `scripts/run_domain_bootstrap_qa_batch.py` now exposes `--no-cache`, passing
  it through to the QA runner so hosted pressure runs can intentionally bypass
  warmed per-question cache rows.
- `tests/test_domain_bootstrap_qa.py` covers compact interval duration support.
- `tests/test_domain_bootstrap_qa_batch.py` covers the fresh-run `--no-cache`
  pass-through.

Measured result:

```text
Six-fixture OpenRouter QA20 fresh run:
  cache: disabled, 0 hits / 120 misses
  score: 110 / 4 / 6
  school activity first-20: 20 / 0 / 0
  runtime load errors: 0
  write proposal rows: 0
  elapsed wall clock: about 9m35s
```

Fresh helper-pressure audit:

```text
helper rows: 7256
helper rows per exact: 65.964
candidate-helper share: 0.5132
top candidate target:
  roster_state_support/source_record_student_group_assignment
  3241 delivered rows, 108 unique rows
```

Artifacts:

- `tmp/openrouter_fresh_helper_pressure_qa20_20260511/qa_batch_summary.json`
- `tmp/openrouter_fresh_helper_pressure_qa20_20260511/qa_batch_summary.md`
- `tmp/helper_usage_pressure_fresh_qa20_20260512.json`
- `tmp/helper_usage_pressure_fresh_qa20_20260512.md`

Lesson:

Compact interval duration is a general query-repair rule: when an existing
answer surface binds a same-day interval atom, elapsed-time questions should be
able to derive the duration without demanding a fixture-specific helper. The
fresh helper audit is the opposite lesson: local support-kind names such as
`school_packet_*` are still candidate pressure, not architecture.

### GG-009 - Helper Delivery Dedupe And Adult Role Surface

Date: 2026-05-12

Scope: helper packaging pressure and adult role/status support.

Trajectory:

```text
school first-20 helper pressure stayed high because primary and evidence-bundle
phases could deliver overlapping helper companion rows for the same question
  -> helper-labeled companion rows are now deduped across the combined query
     result package for a question
  -> school q1-q7 fresh hosted replay stays 7 / 0 / 0 while helper rows drop
     from 4040 to 1480 on the same slice
  -> next pressure is full first-20 replay and support-kind transfer review,
     not adding local packet nouns to architecture
```

Changed surfaces:

- `scripts/run_domain_bootstrap_qa.py` now applies query-plan/package-level
  dedupe to helper-labeled companion rows. This preserves the first delivered
  support row and drops repeated copies across primary and evidence-bundle
  phases.
- `roster_state_support` now exposes admitted person-level adult ratio status
  and lodging status from generic predicates such as `ratio_count_status/2` and
  `lodging_assignment/3`.
- Compact `temporary_assignment/4` rows can reuse the generic temporary-event
  source-link companion after splitting their compact same-day interval atom.

Measured result:

```text
School activity q1-q7 OpenRouter replay, cache disabled:
  before combined helper dedupe: 7 / 0 / 0, 4040 helper rows
  after combined helper dedupe:  7 / 0 / 0, 1480 helper rows
  runtime load errors: 0
  write proposal rows: 0
```

Artifacts:

- `tmp/openrouter_helper_dedupe_school_q7_20260511/qa_batch_summary.json`
- `tmp/openrouter_helper_dedupe_school_q7_replay2_20260511/qa_batch_summary.json`

Lesson:

This is packaging architecture, not fixture learning. The rule is about
duplicate helper-row delivery inside a question result package. The adult
role/lodging addition is also general: if admitted predicates expose
person-level ratio and lodging status, the helper surface should carry those
rows directly rather than forcing the judge to infer them from broad role notes.

### GG-010 - Dedupe Transfer Replay And Identifier Metadata Contract

Date: 2026-05-12

Scope: full hosted QA20 replay after helper package dedupe, and clean metadata
identifier judging.

Trajectory:

```text
fresh six-fixture QA20 after helper dedupe reduced helper pressure but exposed
one school miss where clean identifier metadata was treated as indirect
  -> QA judge contract now treats clean identifier/license metadata rows as
     answer-bearing when their Value or DisplayValue matches the asked code
  -> school q1-q15 fresh hosted replay reaches 15 / 0 / 0
  -> next pressure is remaining non-school compile/query gaps, plus full
     school first-20 replay after the metadata contract
```

Measured result:

```text
Six-fixture OpenRouter QA20 fresh run after helper dedupe:
  score: 107 / 6 / 7
  cache: disabled, 0 hits / 120 misses
  helper rows: 3419, down from 7256 on the comparable pre-dedupe fresh run
  helper rows per exact: 31.953, down from 65.964
  runtime load errors: 0
  write proposal rows: 0

School q1-q15 metadata replay:
  score: 15 / 0 / 0
  q015 driver-license identifier: miss -> exact
  runtime load errors: 0
  write proposal rows: 0
```

Artifacts:

- `tmp/openrouter_helper_dedupe_fresh_qa20_20260511/qa_batch_summary.json`
- `tmp/openrouter_helper_dedupe_fresh_qa20_20260511/qa_batch_summary.md`
- `tmp/helper_usage_pressure_dedupe_fresh_qa20_20260512.json`
- `tmp/helper_usage_pressure_dedupe_fresh_qa20_20260512.md`
- `tmp/openrouter_identifier_metadata_school_q15_20260511/qa_batch_summary.json`

Lesson:

The dedupe rule transferred as packaging pressure reduction, not answer
architecture: it removes repeated helper rows without changing durable KB
state. The metadata repair is a judge contract principle: clean identifier
metadata rows are valid answer surfaces for identifier/code/license questions
when a narrower predicate is absent or unavailable.

### GG-011 - Source-Record Note Surfaces

Date: 2026-05-12

Scope: source-record event notes and local packet support-kind cleanup.

Trajectory:

```text
school q1-q20 after identifier metadata replay exposed retention, observer,
and discovery-note support as present but unstable or locally named
  -> retention support became generic document_retention_location
  -> observer support became source_record_observer_permission_scope and is
     prioritized for the asked adult
  -> normalized discovery notes like *_discovered_YYYY_MM_DD_by_actor surface
     as source_record_discovery_note rows
  -> school q1-q18 fresh hosted replay reaches 18 / 0 / 0; q1-q20 is 19 / 1 / 0,
     with remaining pressure on making candidate observer-permission rows more
     answer-bearing without pretending they are clean transferred substrate
```

Measured result:

```text
School q1-q4 document-retention replay:
  score: 4 / 0 / 0

School q1-q7 observer-permission replay:
  score: 7 / 0 / 0

School q1-q18 source-note replay:
  score: 18 / 0 / 0

School q1-q20 source-note replay:
  score: 19 / 1 / 0
  remaining partial: observer permission row is present, but still candidate-helper
  runtime load errors: 0
  write proposal rows: 0
```

Artifacts:

- `tmp/openrouter_document_retention_school_q4_20260511/qa_batch_summary.json`
- `tmp/openrouter_observer_permission_school_q7_20260511/qa_batch_summary.json`
- `tmp/openrouter_discovery_note_school_q18_20260511/qa_batch_summary.json`
- `tmp/openrouter_source_note_school_q20_20260511/qa_batch_summary.json`

Lesson:

This slice is exactly where fixture vocabulary tries to sneak in. The useful
architecture is not `school_packet_retention_location`; it is document
retention location. It is not a rule about A. Diaz; it is source-record observer
permission scope. It is not a S-022/P. Rivera patch; it is a normalized
source-record discovery-note surface that binds event, date, and actor.

### GG-012 - Structured Observer Permission Scope

Date: 2026-05-12

Scope: answer-bearing source-record permission rows without promoting fixture
entities.

Trajectory:

```text
school q007 still wobbled because observer permission support was present but
looked like a candidate prose note rather than structured evidence
  -> source_record_observer_permission_scope now binds observer, related
     person, relationship, permission action, group, time window, and limit
     as fields parsed from normalized source-record text
  -> school q1-q20 fresh hosted replay returns 20 / 0 / 0
  -> next pressure is transfer review for whether this
     support kind should remain candidate-labeled or graduate after sibling proof
```

Measured result:

```text
School q1-q7 structured observer replay:
  score: 7 / 0 / 0
  helper rows: 1387
  runtime load errors: 0
  write proposal rows: 0

School q1-q20 structured observer replay:
  score: 20 / 0 / 0
  helper rows: 3469
  runtime load errors: 0
  write proposal rows: 0
```

Artifacts:

- `tmp/openrouter_observer_structured_school_q7_20260511/qa_batch_summary.json`
- `tmp/openrouter_observer_structured_school_q20_20260511/qa_batch_summary.json`

Lesson:

The general move is to convert source-record note prose into explicit scoped
fields when the normalized ledger already encodes those fields. The support
kind is still candidate-labeled because transfer is not proven, but it is no
longer just a local display string.

### GG-013 - Structured Source-Note Transfer Replay

Date: 2026-05-12

Scope: six-fixture hosted transfer check after structured source-note support.

Trajectory:

```text
source-note repairs made school q1-q20 clean, but needed unlike-fixture transfer
pressure before being treated as architecture
  -> rerun all six hosted QA20 lanes with cache disabled
  -> overall score improves from 107 / 6 / 7 after helper dedupe to 114 / 2 / 4
     while helper rows stay compressed near 3.47k
  -> next pressure shifts away from school and toward greenhouse temporal
     movement/count support plus hospital source-name addressability
```

Measured result:

```text
Six-fixture structured source-note QA20 replay:
  score: 114 / 2 / 4
  cache: disabled, 0 hits / 120 misses
  helper rows: 3470
  helper rows per exact: 30.439
  runtime load errors: 0
  write proposal rows: 0

Clean first-20 fixtures:
  dream_library_index: 20 / 0 / 0
  sable_creek_budget: 20 / 0 / 0
  school_activity_roster_reconciliation: 20 / 0 / 0
```

Remaining pressure:

```text
festival_permit_maze: q003/q004 partial, permit extension purpose/date linkage
greenhouse_quarantine: q1-q20 clean after temporal source notes plus sample-result source rows
hospital_shift_exception_log: q009 miss, source-record name/addressability
```

Artifacts:

- `tmp/openrouter_structured_source_note_fresh_qa20_20260511/qa_batch_summary.json`
- `tmp/openrouter_structured_source_note_fresh_qa20_20260511/qa_batch_summary.md`
- `tmp/helper_usage_pressure_structured_source_note_qa20_20260512.json`
- `tmp/helper_usage_pressure_structured_source_note_qa20_20260512.md`

Lesson:

This is the first clean transfer checkpoint for the source-note slice: the
school rescue did not destabilize sibling fixtures and the six-lane score moved
up materially. Do not keep polishing the solved school lane now; the next
architecture pressure is temporal movement support and source-name
addressability on unlike fixtures.

### GG-014 - Temporal Source-Note Movement Support

Date: 2026-05-12

Scope: greenhouse temporal movement and no-overlap source rows.

Trajectory:

```text
greenhouse q014/q017 missed even though normalized source rows contained the
movement, return, reporter, and no-overlap facts
  -> add candidate-labeled source_record_temporal_event_note and
     source_record_temporal_relation_note rows from normalized source-record
     text shapes
  -> q014 and q017 move to exact on fresh hosted OpenRouter replay
  -> q018 stays miss and is correctly classified as compile_surface_gap because
     the admitted KB contradicts the source answer with lab_result(..., positive, 5)
```

Measured result:

```text
Greenhouse targeted hosted replay q014/q017/q018:
  score: 2 / 0 / 1
  exact: q014, q017
  miss: q018
  failure surface: q018 compile_surface_gap
  cache: disabled, 0 hits / 3 misses
  helper rows: 6 candidate-helper rows
  runtime load errors: 0
  write proposal rows: 0
  elapsed wall clock: 56 seconds

Greenhouse broader hosted replay q1-q20:
  score: 17 / 1 / 2
  exact temporal repairs: q014, q017
  remaining partial: q003 initial-scope selection
  remaining misses: q007/q018 sample positive-count compile fidelity
  cache: disabled, 0 hits / 20 misses
  helper rows: 38 candidate-helper rows
  runtime load errors: 0
  write proposal rows: 0
  elapsed wall clock: 327 seconds
```

Artifacts:

- `tmp/openrouter_temporal_notes_greenhouse_target_20260511/domain_bootstrap_qa_20260512T040044126868Z_qa_qwen-qwen3-6-35b-a3b.json`
- `tmp/openrouter_temporal_notes_greenhouse_target_20260511/domain_bootstrap_qa_20260512T040044126868Z_qa_qwen-qwen3-6-35b-a3b.md`
- `tmp/openrouter_temporal_notes_greenhouse_q20_20260511/qa_batch_summary.json`
- `tmp/openrouter_temporal_notes_greenhouse_q20_20260511/qa_batch_summary.md`

Lesson:

This is source-addressability architecture, not greenhouse learning. The
replacement principle is: when a normalized source row explicitly binds a
subject, temporal action, location, return relation, reporter, or no-overlap
status, expose those fields as candidate support so query plans can use the
source row without memorizing fixture nouns. Do not use this to repair sample
counts; q007 and q018 are compile-fidelity scars until the source compile
preserves the original count-bearing lines. q003 is a separate initial-scope
selection pressure and should not be patched with greenhouse-specific status
vocabulary.

### GG-015 - Sample Result Source-Row Fidelity

Date: 2026-05-12

Scope: count-of-total sample result prose and lab-result answer surfaces.

Trajectory:

```text
greenhouse q007/q018 remained wrong after temporal source notes because sample
positive counts were either collapsed into a misleading semantic lab_result row
or missing from source_record rows entirely
  -> teach the deterministic source-record ledger to retain standalone
     "N of M samples..." prose as addressable source text
  -> expose source_record_sample_result_note candidate rows from normalized
     source text when it explicitly binds count, total, subject, unit, and
     result polarity
  -> fresh greenhouse compile now preserves the q018 source row and q007/q018
     targeted replay is exact; broader greenhouse q1-q20 is 20 / 0 / 0
```

Measured result:

```text
Existing compile q007 control:
  score: 0 / 1 / 0
  lesson: correct source-row support appeared, but contradictory semantic
          lab_result(..., positive, 6) kept the judge at partial
  elapsed wall clock: 21 seconds

Fresh hosted compile:
  compile admitted: 117
  deterministic source row added: src_line_0055
  semantic lab_result/4 reshaped to positive_count / total_samples for Lot 3A
  elapsed wall clock: 284 seconds

Fresh compile targeted q007/q018:
  score: 2 / 0 / 0
  helper rows: 8 candidate-helper rows
  elapsed wall clock: 24 seconds

Fresh compile greenhouse q1-q20:
  score: 20 / 0 / 0
  cache: disabled, 0 hits / 20 misses
  helper rows: 76 candidate-helper rows
  runtime load errors: 0
  write proposal rows: 0
  elapsed wall clock: 341 seconds
```

Artifacts:

- `tmp/openrouter_sample_result_compile_greenhouse_20260511/domain_bootstrap_file_20260512T041636252618Z_source_qwen-qwen3-6-35b-a3b.json`
- `tmp/openrouter_sample_result_fresh_compile_greenhouse_target_20260511/domain_bootstrap_qa_20260512T041732576608Z_qa_qwen-qwen3-6-35b-a3b.json`
- `tmp/openrouter_sample_result_fresh_compile_greenhouse_q20_20260511/domain_bootstrap_qa_20260512T042337007313Z_qa_qwen-qwen3-6-35b-a3b.md`

Lesson:

This is not a lab-result guard. The reusable principle is that source-record
addressability must preserve standalone count-of-total result prose, and QA may
surface those rows as candidate support only when the normalized source text
itself binds count, total, subject, unit, and result polarity. A contradictory
semantic predicate should remain visible as compile-fidelity pressure; the
source row gives the judge a recoverable evidence surface without teaching the
harness fixture-specific lab vocabulary.

### GG-016 - Matching Token Source-Section Support

Date: 2026-05-12

Scope: source-name addressability for time-stamped source rows.

Trajectory:

```text
hospital q009 missed in the structured-source-note replay because the primary
query retrieved the event at a timestamp but did not surface the source section
that contained the matching source row
  -> add source_record_matching_token_source rows when a
     time-like query constant matches source_record_numeric_token rows
  -> q009 moves to exact on fresh hosted replay without encoding the source
    name, room, actor, or fixture vocabulary
  -> GG-077 later promoted this narrow bound-token source-addressability
     surface from candidate-helper to clean-helper while leaving prose-derived
     source notes candidate-labeled
  -> broader hospital q1-q20 is 18 / 0 / 2; remaining misses are statement
     event linkage and Addendum authority hierarchy, not q009 source-name
     addressability
```

Measured result:

```text
Hospital targeted hosted replay q009:
  score: 1 / 0 / 0
  helper rows: 4 candidate-helper rows
  cache: disabled, 0 hits / 1 miss
  runtime load errors: 0
  write proposal rows: 0
  elapsed wall clock: 24 seconds

Hospital broader hosted replay q1-q20:
  score: 18 / 0 / 2
  remaining misses: q013 statement-event linkage, q018 addendum authority
  helper rows: 9 candidate-helper rows
  cache: disabled, 0 hits / 20 misses
  runtime load errors: 0
  write proposal rows: 0
  elapsed wall clock: 484 seconds
```

Artifacts:

- `tmp/openrouter_matching_token_source_hospital_q009_20260511/domain_bootstrap_qa_20260512T042817856118Z_qa_qwen-qwen3-6-35b-a3b.json`
- `tmp/openrouter_matching_token_source_hospital_q20_20260511/domain_bootstrap_qa_20260512T043635140191Z_qa_qwen-qwen3-6-35b-a3b.json`

Lesson:

This is a source-addressability repair, not a hospital-source rule. The
general principle is: when a query binds a time-like source token and the
source ledger contains rows with the same normalized numeric token, expose the
matching row's section/source label as candidate evidence. This lets a provenance
question recover the source name while leaving deeper authority and statement
linkage to compile-surface work.

### GG-017 - Timestamp Authority And Supersession Source Notes

Date: 2026-05-12

Scope: source-stated authority hierarchy for timestamp conflicts.

Trajectory:

```text
hospital q018 still missed after source-name addressability because the query
could retrieve event/log rows but not the source-stated authority relation
between an earlier device summary time and the preferred server record time
  -> add candidate-labeled timestamp-authority source notes from normalized
     source text, carrying preferred timestamp/source, superseded
     timestamp/source, and authority status
  -> targeted hosted q018 moves to exact with one candidate-helper row and no
     fixture nouns, row IDs, people, room names, or question IDs encoded in the
     helper
  -> broader hospital q1-q20 improves from 18 / 0 / 2 to 19 / 0 / 1; next
     pressure is q013 statement-event linkage plus unlike-fixture replay for
     authority/supersession notes before any graduation from candidate
```

Changed surface:

- `scripts/run_domain_bootstrap_qa.py` now emits
  `source_record_timestamp_authority_note` rows when source text states an
  authoritative timestamp/time and an earlier recorded or superseded time.
- The extraction guards against date-like tokens such as `march_12_2026`
  being misread as event times.
- `system_log_event` and `timestamp_correction` query plans may receive this
  candidate helper when the source ledger already contains the authority text.

Measured result:

```text
Hospital targeted hosted replay q018:
  score: 1 / 0 / 0
  helper rows: 1 candidate-helper row
  cache: disabled, 0 hits / 1 miss
  runtime load errors: 0
  write proposal rows: 0
  elapsed wall clock: 21 seconds

Hospital broader hosted replay q1-q20:
  score: 19 / 0 / 1
  remaining miss: q013 statement-event linkage
  helper rows: 26 candidate-helper rows
  cache: disabled, 0 hits / 20 misses
  runtime load errors: 0
  write proposal rows: 0
  elapsed wall clock: 364 seconds

Local verification:
  focused domain bootstrap QA: 97 passed
  full suite: 976 passed, 2 subtests passed
```

Artifacts:

- `tmp/openrouter_timestamp_authority_hospital_q018_20260511/domain_bootstrap_qa_20260512T051123981155Z_qa_qwen-qwen3-6-35b-a3b.json`
- `tmp/openrouter_timestamp_authority_hospital_q20_20260511/domain_bootstrap_qa_20260512T051750647093Z_qa_qwen-qwen3-6-35b-a3b.json`

Lesson:

This is an authority/supersession repair, not an addendum-specific fix. The
reusable principle is that when source text explicitly states which timestamp
or source is authoritative over an earlier recorded value, that relation is an
evidence surface in its own right. It should remain candidate-labeled until the
same shape transfers to unlike timestamp, version, or correction conflicts.

### GG-018 - Statement Filing Source Notes

Date: 2026-05-12

Scope: source-addressable statement filing metadata.

Trajectory:

```text
hospital q013 still missed after timestamp-authority repair because the
statement predicate named speakers/content while the source-record label held
the statement filing time as separate packet metadata
  -> add candidate-labeled statement-filing notes from source-record statement
     labels, linking speaker, filed time, role, statement id, and admitted
     statement content when staff_statement/3 is present
  -> targeted hosted q013 moves to exact; broader hospital q1-q20 moves from
     19 / 0 / 1 to 20 / 0 / 0
  -> next pressure is unlike-fixture replay for statement filing/source rows
     before graduating the candidate helper, plus helper-volume pruning
```

Changed surface:

- `scripts/run_domain_bootstrap_qa.py` now emits
  `source_record_statement_filing_note` rows for normalized source labels such
  as `person_role_statement_filed_time`.
- The note remains candidate-labeled and is triggered by `staff_statement`
  query plans.
- The row links source-record filing metadata to admitted statement predicates
  by speaker when available; it does not infer the truth of the statement.

Measured result:

```text
Hospital targeted hosted replay q013:
  score: 1 / 0 / 0
  helper rows: 4 candidate-helper rows
  cache: disabled, 0 hits / 1 miss
  runtime load errors: 0
  write proposal rows: 0
  elapsed wall clock: 22 seconds

Hospital broader hosted replay q1-q20:
  score: 20 / 0 / 0
  helper rows: 69 candidate-helper rows
  cache: disabled, 0 hits / 20 misses
  runtime load errors: 0
  write proposal rows: 0
  elapsed wall clock: 319 seconds

Local verification:
  focused domain bootstrap QA: 98 passed
  full suite: 977 passed, 2 subtests passed
```

Artifacts:

- `tmp/openrouter_statement_filing_hospital_q013_20260511/domain_bootstrap_qa_20260512T052208648046Z_qa_qwen-qwen3-6-35b-a3b.json`
- `tmp/openrouter_statement_filing_hospital_q20_20260511/domain_bootstrap_qa_20260512T052739738321Z_qa_qwen-qwen3-6-35b-a3b.json`

Lesson:

This is filing/source metadata, not statement truth. The reusable principle is
that source packets often encode provenance facts about statements in adjacent
labels rather than in the statement predicate itself. Surfacing speaker and
filed-time metadata can answer provenance questions, but the helper must remain
candidate-labeled until it transfers to unlike statement/source packets and
does not become a shortcut for believing statement contents.

### GG-019 - Long Source Row Preservation

Date: 2026-05-12

Scope: source-record ledger fidelity for long statement/source rows.

Trajectory:

```text
hospital q013 could be made exact with statement-filing metadata, but the
underlying compiled source row had truncated the answer-bearing tail of the
long statement before the Room 502 / 14:37 clause
  -> increase deterministic source-record row preservation from 360 to 1200
     characters and add a regression for long statement tail clauses
  -> fresh hospital compile preserves the full statement source atom and q013
     becomes exact with zero helper rows
  -> broader fresh q1-q20 drops to 16 / 0 / 4, exposing compile-surface drift
     in role routing, order identifier, telemetry source, and order
     supersession rows
```

Changed surface:

- `src/source_record_ledger.py` now preserves longer source rows by default so
  deterministic source-record context does not cut off late clauses in long
  statements or notes.
- `tests/test_source_record_ledger.py` now protects the long-statement tail
  case directly.
- High-pressure candidate helper delivery was pruned so broad
  `source_record_*` scans do not receive timestamp-authority, matching-token,
  or statement-filing helpers unless a bound source row/token actually matches.

Measured result:

```text
Fresh hospital compile with longer source ledger:
  admitted facts: 123
  skipped facts: 4
  source_record_text_atom(src_line_0093, ...) now preserves Room 502 and 14:37

Hospital targeted hosted replay q013 on fresh compile:
  score: 1 / 0 / 0
  helper rows: 0
  cache: disabled, 0 hits / 1 miss
  runtime load errors: 0
  write proposal rows: 0
  elapsed wall clock: 15 seconds

Hospital broader hosted replay q1-q20 on fresh compile:
  score: 16 / 0 / 4
  helper rows: 36 candidate-helper rows
  misses: q005 role routing, q008 order identifier display/source, q011
    telemetry source attribution, q017 order supersession/co-signature
  runtime load errors: 0
  write proposal rows: 0
  elapsed wall clock: 358 seconds

Local verification:
  source-ledger/domain/source-doc focused slice: 114 passed
  full suite: 980 passed, 2 subtests passed
```

Artifacts:

- `tmp/openrouter_long_source_ledger_hospital_compile_20260511/domain_bootstrap_file_20260512T054803885845Z_source_qwen-qwen3-6-35b-a3b.json`
- `tmp/openrouter_long_source_ledger_hospital_q013_20260511/domain_bootstrap_qa_20260512T054840359151Z_qa_qwen-qwen3-6-35b-a3b.json`
- `tmp/openrouter_long_source_ledger_hospital_q20_20260511/domain_bootstrap_qa_20260512T055451516174Z_qa_qwen-qwen3-6-35b-a3b.json`

Lesson:

This is source-fidelity architecture, not a q013 workaround. Candidate helpers
can rescue a missing source row, but a better substrate preserves the source
row so the compiler can admit direct statement content. The broader q20 drop
is the important warning: fixing ledger fidelity can change the compile shape,
so the next work should stabilize fresh-compile predicate coverage rather than
reinflate helpers to mask drift.

### GG-020 - Fresh Compile Source-Addressability Drift

Date: 2026-05-12

Scope: source-record packet notes for fresh-compile drift after long source
ledger preservation.

Trajectory:

```text
fresh long-ledger hospital q1-q20 replay exposed q005/q008/q011/q017 misses
after q013 moved to direct source-fidelity success
  -> add general source-record notes for role-routing, order identifiers,
     order authority/co-signature, telemetry source-token matches, and
     clock-event metadata, while tightening high-pressure note delivery so
     broad predicate scans do not flood helper rows
  -> targeted hosted replays for q005/q008/q011/q017/q004 are exact, and fresh
     q1-q20 improves from 16 / 0 / 4 to 19 / 0 / 1
  -> the remaining q20 miss is unstable across reruns, with q003 now exposing
     lot/event temporal join pressure and helper volume still high
```

Changed surface:

- `scripts/run_domain_bootstrap_qa.py` now exposes source-record notes for
  packet routing, order identifier display, order authority/co-signature,
  time-bound event metadata, and matching source sections for telemetry/event
  source questions.
- High-pressure source-record note delivery is now predicate-scoped and
  token-bound; broad role scans with no bound constants do not receive the
  packet-note helpers.
- `tests/test_domain_bootstrap_qa.py` covers the new source-note surfaces and
  the no-flood behavior for broad source-record role queries.

Measured result:

```text
Fresh long-ledger hospital q1-q20 before drift repair:
  score: 16 / 0 / 4
  helper rows: 36 candidate-helper rows
  misses: q005, q008, q011, q017

Targeted hosted drift replays after source-note repair:
  q005: 1 / 0 / 0, helper rows: 1
  q008: 1 / 0 / 0, helper rows: 10-11 across reruns
  q011: 1 / 0 / 0, helper rows: 12
  q017: 1 / 0 / 0, helper rows: 5
  q004: 1 / 0 / 0, helper rows: 1

Fresh hospital q1-q20 after drift repair:
  best score: 19 / 0 / 1
  latest miss: q003 lot-number event join
  helper rows: 135 candidate-helper rows
  runtime load errors: 0
  write proposal rows: 0

Local verification:
  focused domain/source-ledger slice: 114 passed
  full suite: 980 passed, 2 subtests passed
```

Artifacts:

- `tmp/openrouter_fresh_drift_q005_20260511/domain_bootstrap_qa_20260512T061514178888Z_qa_qwen-qwen3-6-35b-a3b.json`
- `tmp/openrouter_fresh_drift_q008_20260511/domain_bootstrap_qa_20260512T061513406009Z_qa_qwen-qwen3-6-35b-a3b.json`
- `tmp/openrouter_fresh_drift_q011_20260511/domain_bootstrap_qa_20260512T061511608413Z_qa_qwen-qwen3-6-35b-a3b.json`
- `tmp/openrouter_fresh_drift_q017_20260511/domain_bootstrap_qa_20260512T061517251100Z_qa_qwen-qwen3-6-35b-a3b.json`
- `tmp/openrouter_fresh_drift_q004_20260511/domain_bootstrap_qa_20260512T062434982401Z_qa_qwen-qwen3-6-35b-a3b.json`
- `tmp/openrouter_fresh_drift_recovered3_hospital_q20_20260511/domain_bootstrap_qa_20260512T063658981300Z_qa_qwen-qwen3-6-35b-a3b.json`

Lesson:

This is source-addressability substrate, not a hospital fixture patch. The
general principle is that packet labels, source-section labels, identifier
display forms, and event/source timestamps are addressable metadata when they
bind the queried role, item, time, authority, or source in the same source
atom. The q20 replay is deliberately not declared stable: the remaining moving
miss and helper volume mean the next work should target the general item/event
join and pruning problem before retiring any guard.

### GG-021 - Item/Event Identifier Source Notes

Date: 2026-05-12

Scope: general item identifier plus event-time source-note binding.

Trajectory:

```text
fresh hospital q1-q20 had recovered to 19 / 0 / 1, with the remaining moving
miss landing on q003: an item identifier asked through a time-bound event join
  -> add candidate source-record item/event identifier notes that bind an item
     identifier, display identifier, event action, and event time from one
     source atom; then scope those notes to compatible system-event queries
  -> hosted q003 is exact, and fresh no-cache hospital q1-q20 reaches
     20 / 0 / 0 after pruning
  -> helper pressure remains high at 163 candidate-helper rows for the first
     20, so the next pressure is row precision, not answer coverage
```

Changed surface:

- `scripts/run_domain_bootstrap_qa.py` now emits
  `source_record_item_event_identifier_note` rows when one source atom binds an
  item/code-like identifier to an action and event time.
- Source-record packet metadata scoping now treats the item/event note as a
  high-pressure candidate and only delivers it for `system_event` queries when
  the query tokens match the note's event time or identifier.
- `tests/test_domain_bootstrap_qa.py` protects the generic display and timing
  contract using neutral item/event vocabulary.

Measured result:

```text
Hospital targeted hosted q003 before item/event note:
  score: miss in the prior 19 / 0 / 1 q1-q20 replay
  failure surface: hybrid_join_gap

Hospital targeted hosted q003 after item/event note:
  score: 1 / 0 / 0
  helper rows: 17 candidate-helper rows after scoping
  cache: disabled, 0 hits / 1 miss
  runtime load errors: 0
  write proposal rows: 0
  elapsed wall clock: 15 seconds

Hospital fresh no-cache q1-q20 after item/event note:
  score: 20 / 0 / 0
  helper rows: 179 candidate-helper rows before item-event scoping
  helper rows: 163 candidate-helper rows after item-event scoping
  cache: disabled, 0 hits / 20 misses
  runtime load errors: 0
  write proposal rows: 0
  elapsed wall clock: 287 seconds after pruning

Local verification:
  focused domain/source-ledger slice: 114 passed
  full suite: 980 passed, 2 subtests passed
```

Artifacts:

- `tmp/openrouter_item_event_q003_20260512/domain_bootstrap_qa_20260512T064233883752Z_qa_qwen-qwen3-6-35b-a3b.json`
- `tmp/openrouter_item_event_hospital_q20_20260512/domain_bootstrap_qa_20260512T064816541890Z_qa_qwen-qwen3-6-35b-a3b.json`
- `tmp/openrouter_item_event_pruned_q003_20260512/domain_bootstrap_qa_20260512T064941004921Z_qa_qwen-qwen3-6-35b-a3b.json`
- `tmp/openrouter_item_event_pruned_hospital_q20_20260512/domain_bootstrap_qa_20260512T065444151293Z_qa_qwen-qwen3-6-35b-a3b.json`

Lesson:

This is an item/event binding repair, not a lot-number or hospital repair. The
transfer claim is deliberately narrow: when a single source row binds an
identifier-like item code, an event/action word, and an event time, the row can
act as candidate evidence for a time-bound event question. The helper family
earns continued pressure but not graduation; the 163-row q1-q20 helper load
means the next architecture bet should improve candidate precision before any
guard retirement.

### GG-022 - Packet Metadata Precision Scoping

Date: 2026-05-12

Scope: source-record packet metadata helper pressure after first-20 coverage
was recovered.

Trajectory:

```text
fresh hospital q1-q20 was exact after item/event notes, but still delivered
163 candidate-helper packet rows across 20 answers
  -> make explicit-wanted predicate metadata strict: lab-result queries get
     source-token/sample/temporal support only when those rows match, and
     system-event queries get token-bound event/source metadata without the
     generic eight-row context tail
  -> targeted hosted probes keep q003/q006/q007/q015 exact while q003 drops
     from 17 to 9 helper rows, q006 drops to 0, and q007 recovers with one
     source-token helper after an intentional over-prune test
  -> fresh no-cache q1-q20 stays 20 / 0 / 0 and helper rows drop
     163 -> 107
```

Changed surface:

- `scripts/run_domain_bootstrap_qa.py` now treats `system_event` metadata as
  strict token-bound support instead of adding a generic high-pressure context
  tail after relevant rows are found.
- `lab_result` metadata now admits matching source-token support, sample-result
  notes, and temporal notes, but does not fall back to the whole packet when no
  relevant support rows match.
- The q007 over-prune replay is kept as a scar in the journal: removing all
  lab-result packet support caused a miss, so the reusable rule is precision,
  not blanket deletion.

Measured result:

```text
Targeted hosted probes after strict packet scoping:
  q003: 1 / 0 / 0, helper rows: 9
  q006: 1 / 0 / 0, helper rows: 0
  q007: 1 / 0 / 0, helper rows: 1
  q015: 1 / 0 / 0, helper rows: 7

Hospital fresh no-cache q1-q20:
  score: 20 / 0 / 0
  helper rows: 107 candidate-helper rows
  previous comparable helper rows: 163
  cache: disabled, 0 hits / 20 misses
  runtime load errors: 0
  write proposal rows: 0
  elapsed wall clock: 323 seconds

Local verification:
  focused domain/source-ledger slice: 114 passed
  full suite: 980 passed, 2 subtests passed
```

Artifacts:

- `tmp/openrouter_packet_precision_q003_20260512/domain_bootstrap_qa_20260512T065943499480Z_qa_qwen-qwen3-6-35b-a3b.json`
- `tmp/openrouter_packet_precision_q006_20260512/domain_bootstrap_qa_20260512T065925617699Z_qa_qwen-qwen3-6-35b-a3b.json`
- `tmp/openrouter_packet_precision2_q007_20260512/domain_bootstrap_qa_20260512T070352019032Z_qa_qwen-qwen3-6-35b-a3b.json`
- `tmp/openrouter_packet_precision_q015_20260512/domain_bootstrap_qa_20260512T065949248039Z_qa_qwen-qwen3-6-35b-a3b.json`
- `tmp/openrouter_packet_precision_hospital_q20_20260512/domain_bootstrap_qa_20260512T070931008677Z_qa_qwen-qwen3-6-35b-a3b.json`

Lesson:

This is helper-pressure architecture, not answer chasing. The general rule is
that an explicit predicate-to-support contract should either deliver rows that
match that contract or deliver nothing; it should not use the whole source
packet as a consolation prize. The q007 scar matters because it prevents the
opposite mistake: some questions genuinely need a compact source-token helper,
so the winning rule is token-bound support, not deletion of metadata support.

### GG-023 - Placeholder-Aware Source Scan Scoping

Date: 2026-05-12

Scope: source-record metadata helper pressure from broad source scans and
evidence-bundle side queries.

Trajectory:

```text
fresh hospital q1-q20 held 20 / 0 / 0 after packet precision, but still
delivered 107 candidate-helper packet rows
  -> extend the generic lowercase-placeholder vocabulary to source-record slot
     labels such as line/text/textatom/section/source_row, and block packet
     metadata for predicates with no declared source-metadata contract
  -> first aggregate replay compressed helper rows to 52 but over-pruned q018,
     proving that timestamp-authority notes are legitimate for broad source
     label/section provenance scans
  -> allow only timestamp-authority notes through unbound source label/section
     scans; fresh no-cache q1-q20 recovers to 20 / 0 / 0 with 66 helper rows
```

Changed surface:

- `GENERIC_QUERY_PLACEHOLDERS` now includes source-record slot labels such as
  `line`, `lineid`, `text`, `textatom`, `section`, and `source_row`, so broad
  placeholder scans are repaired to variables instead of treated as constants.
- `policy_requirement` is explicitly a no-packet-metadata predicate; policy
  rows should not receive source-record packet metadata unless a specific
  policy-source support family is defined.
- Broad `source_record_label` and `source_record_section` scans may receive
  `source_record_timestamp_authority_note` rows, because provenance/version
  questions ask exactly through those surfaces; broad `source_record_text_atom`
  scans still do not receive high-pressure packet notes.
- `tests/test_domain_bootstrap_qa.py` now asserts that retired school packet
  content lives in `roster_state_support` and no longer expects a companion
  packet metadata table for `policy_requirement`.

Measured result:

```text
Hospital targeted hosted probes:
  q005 after policy no-packet: 1 / 0 / 0, helper rows: 1
  q016 after policy no-packet: 1 / 0 / 0, helper rows: 9
  q018 after source-label timestamp-authority exception: 1 / 0 / 0,
    helper rows: 5

Hospital fresh no-cache q1-q20:
  intermediate over-prune: 19 / 0 / 1, helper rows: 52
  recovered score: 20 / 0 / 0
  recovered helper rows: 66 candidate-helper rows
  previous comparable helper rows: 107
  cache: disabled, 0 hits / 20 misses
  runtime load errors: 0
  write proposal rows: 0
  elapsed wall clock: 382 seconds

Local verification:
  focused domain/source-ledger slice: 114 passed
  full suite: 980 passed, 2 subtests passed
```

Artifacts:

- `tmp/openrouter_policy_no_packet_q005_20260512/domain_bootstrap_qa_20260512T071339465872Z_qa_qwen-qwen3-6-35b-a3b.json`
- `tmp/openrouter_policy_no_packet_q016_20260512/domain_bootstrap_qa_20260512T071334669140Z_qa_qwen-qwen3-6-35b-a3b.json`
- `tmp/openrouter_placeholder_scoped_hospital_q20_20260512/domain_bootstrap_qa_20260512T072741608450Z_qa_qwen-qwen3-6-35b-a3b.json`
- `tmp/openrouter_placeholder_scoped_q018_20260512/domain_bootstrap_qa_20260512T072948791580Z_qa_qwen-qwen3-6-35b-a3b.json`
- `tmp/openrouter_placeholder_scoped_recovered_hospital_q20_20260512/domain_bootstrap_qa_20260512T073629177996Z_qa_qwen-qwen3-6-35b-a3b.json`

Lesson:

This is source-scan hygiene, not a hospital repair. Lowercase words like
`line`, `text`, and `section` are usually query slot labels, not evidence
constants, and they must not unlock high-pressure metadata. The q018 over-prune
is the important boundary: provenance/version questions can legitimately ask
through source labels and sections, so timestamp-authority notes need a narrow
path there while the rest of the packet remains suppressed.

### GG-024 - Source-Note Transfer Boundary

Date: 2026-05-12

Scope: unlike-fixture transfer check for placeholder-aware source-note scoping
and sample-result source fidelity.

Trajectory:

```text
hospital first-20 was exact with packet helper rows compressed to 66, but the
source-note precision rule still needed unlike-fixture pressure
  -> replay existing school and greenhouse compiles with fresh no-cache hosted
     QA, then fresh-compile greenhouse after the old compile exposed missing
     sample-result source rows
  -> school first-20 stays 20 / 0 / 0; old greenhouse compile remains
     17 / 2 / 1 with sample-count conflicts; fresh greenhouse compile preserves
     the missing Lot 5A sample-result row and targeted q007/q018 are exact
  -> next pressure is not a greenhouse-specific guard; it is source-ledger
     fidelity plus sample-result transfer across unlike sampled/result packets
```

Changed surface:

- No new fixture-specific helper was added. The work validated that
  placeholder-aware packet scoping can transfer to a school source-record
  packet without breaking first-20 coverage.
- Fresh greenhouse compilation with the current `source_record_ledger`
  preservation includes the previously missing `3 of 5` sample-result source
  row, which lets existing `source_record_sample_result_note` support recover
  the sample-count questions.
- The old greenhouse compile is retained as a scar: its deterministic source
  record layer skipped the Lot 5A sample-result sentence, so selector/helper
  tuning alone should not be asked to repair that stale compile.

Measured result:

```text
School transfer replay on existing compile:
  score: 20 / 0 / 0
  source_record_packet_metadata_support rows: 422
  total helper rows: 3054
  runtime load errors: 0
  write proposal rows: 0
  elapsed wall clock: 323 seconds

Greenhouse transfer replay on old compile:
  score: 17 / 2 / 1
  source_record_packet_metadata_support rows: 57
  non-exact: q003 initial-greenhouse temporal join, q007/q018 sample-count
    conflicts caused by stale/missing source rows
  runtime load errors: 0
  write proposal rows: 0
  elapsed wall clock: 386 seconds

Fresh greenhouse compile with current source ledger:
  admitted semantic facts: 16
  skipped facts: 0
  source_record_text_atom(src_line_0055, v_3_of_5_samples_from_lot_5a...)
    is preserved

Fresh greenhouse targeted q007/q018 replay:
  score: 2 / 0 / 0
  helper rows: 8 candidate-helper rows, 2 clean-helper rows
  runtime load errors: 0
  write proposal rows: 0
  elapsed wall clock: 67 seconds

Local verification:
  full suite: 980 passed, 2 subtests passed
```

Artifacts:

- `tmp/openrouter_placeholder_transfer_school_q20_20260512/domain_bootstrap_qa_20260512T074811098845Z_qa_qwen-qwen3-6-35b-a3b.json`
- `tmp/openrouter_placeholder_transfer_greenhouse_q20_20260512/domain_bootstrap_qa_20260512T074914375062Z_qa_qwen-qwen3-6-35b-a3b.json`
- `tmp/openrouter_placeholder_transfer_greenhouse_fresh_compile_20260512/domain_bootstrap_file_20260512T075531401227Z_source_qwen-qwen3-6-35b-a3b.json`
- `tmp/openrouter_placeholder_transfer_greenhouse_fresh_q007_q018_20260512/domain_bootstrap_qa_20260512T075713348997Z_qa_qwen-qwen3-6-35b-a3b.json`

Lesson:

This is transfer evidence and a source-fidelity boundary, not a new greenhouse
rule. When structured result rows collapse an `X of Y` sample statement into a
single misleading count, the source-record sample-result note is the right
candidate substrate, but only if the deterministic ledger preserved the source
sentence. The old compile proves helper work cannot compensate for missing
source rows; the fresh compile proves the existing general sample-result note
can transfer when the ledger is faithful.

### GG-025 - Roster Delivery Precision Boundary

Date: 2026-05-12

Scope: school transfer helper-pressure compression after placeholder-aware
source-note transfer.

Trajectory:

```text
school transfer held 20 / 0 / 0 but delivered 3054 helper rows, including
2623 roster_state_support rows and broad assignment tails on questions that
were not asking for roster membership
  -> change roster_state_support delivery from rank-then-tail to
     predicate-contract scoping, add observed-scan -> scheduled transport
     support, and make absence-of-lodging status answer-ready
  -> local suite is 982 passed, 2 subtests passed; targeted hosted q019 and
     q007 replays are exact; a transitional full hosted school q20 recovers
     20 / 0 / 0, and the latest person-bound q007 replay compresses the role
     surface to 4 roster rows
  -> person-bound full q20 holds 20 / 0 / 0 with helper rows compressed to
     1732 and q007 carried by exactly four roster-state rows
  -> next pressure is birth-row/unlike-row replay for guard retirement; this
     move is replay evidence, not automatic retirement permission
```

Changed surface:

- `_prioritize_roster_state_rows()` now scopes delivered rows by predicate
  contract instead of sorting every roster helper to the front and returning a
  broad tail.
- Membership predicates keep membership, supervision, and group-count support.
  Policy predicates keep packet-content support. Observed attendance scans now
  carry scheduled transport departure and scanner-clock audit support so scan
  events do not masquerade as the only time surface.
- Adult lodging absence is rendered as an answer-ready status row while
  remaining derived from the generic absence of `lodging_assignment/3`, not from
  a person-specific rule.
- Person-bound adult role queries now require the row's person to match the
  requested person before wildcard role slots can promote supporting rows. This
  prevents `adult_role(Person, Role)` from turning unrelated roster/membership
  rows into answer context.

Measured result:

```text
Before school transfer:
  score: 20 / 0 / 0
  helper rows: 3054
  roster_state_support rows: 2623
  source_record_packet_metadata_support rows: 422

After roster predicate-contract scoping, first full q20:
  score: 19 / 1 / 0
  helper rows: 1818
  roster_state_support rows: 1466
  source_record_packet_metadata_support rows: 352
  remaining partial: q019 observed scan vs scheduled departure
  elapsed wall clock: 484 seconds

Targeted q019 repair:
  score: 1 / 0 / 0
  helper rows: 212
  elapsed wall clock: 44.5 seconds

After answer-ready lodging absence, second full q20:
  score: 19 / 1 / 0
  helper rows: 1887
  roster_state_support rows: 1468
  source_record_packet_metadata_support rows: 418
  remaining partial: q007 role/status hybrid join despite rows being present
  elapsed wall clock: 543.6 seconds

Targeted q007 repair:
  score: 1 / 0 / 0
  helper rows: 212
  elapsed wall clock: 28 seconds

Full q20 after q007/q019 repairs, before final person-bound role narrowing:
  score: 20 / 0 / 0
  helper rows: 2097
  roster_state_support rows: 1648
  source_record_packet_metadata_support rows: 448
  runtime load errors: 0
  write proposal rows: 0
  elapsed wall clock: 379.3 seconds

Full q20 after role-slot tightening, before final person-bound narrowing:
  score: 20 / 0 / 0
  helper rows: 1846
  roster_state_support rows: 1366
  source_record_packet_metadata_support rows: 480
  runtime load errors: 0
  write proposal rows: 0
  elapsed wall clock: 408.7 seconds

Latest person-bound q007 replay:
  score: 1 / 0 / 0
  helper rows: 36
  roster_state_support rows: 4
  source_record_packet_metadata_support rows: 32
  runtime load errors: 0
  write proposal rows: 0
  elapsed wall clock: 27.8 seconds

Person-bound full q20:
  score: 20 / 0 / 0
  helper rows: 1732
  roster_state_support rows: 1283
  source_record_packet_metadata_support rows: 449
  runtime load errors: 0
  write proposal rows: 0
  elapsed wall clock: 415.2 seconds

Person-bound full q20 q007 detail:
  q007 score: exact
  primary roster_state_support rows: 4
  evidence-bundle roster_state_support rows: 4
  rows: adult_role, adult_ratio_count_status, adult_lodging_status,
    source_record_observer_permission_scope

Local verification:
  full suite: 982 passed, 2 subtests passed
```

Artifacts:

- `tmp/openrouter_roster_precision_school_q20_20260512/domain_bootstrap_qa_20260512T081216272670Z_qa_qwen-qwen3-6-35b-a3b.json`
- `tmp/openrouter_roster_precision_school_q019_20260512/domain_bootstrap_qa_20260512T081620103917Z_qa_qwen-qwen3-6-35b-a3b.json`
- `tmp/openrouter_roster_precision_school_q20_retry_20260512/domain_bootstrap_qa_20260512T082546952058Z_qa_qwen-qwen3-6-35b-a3b.json`
- `tmp/openrouter_roster_precision_school_q007_20260512/domain_bootstrap_qa_20260512T082747724843Z_qa_qwen-qwen3-6-35b-a3b.json`
- `tmp/openrouter_roster_precision_school_q20_after_q007_q019_20260512/domain_bootstrap_qa_20260512T083748763180Z_qa_qwen-qwen3-6-35b-a3b.json`
- `tmp/openrouter_roster_precision_school_q20_role_scoped_20260512/domain_bootstrap_qa_20260512T084250069457Z_qa_qwen-qwen3-6-35b-a3b.json`
- `tmp/openrouter_roster_precision_school_q007_person_scoped_20260512/domain_bootstrap_qa_20260512T083935142673Z_qa_qwen-qwen3-6-35b-a3b.json`
- `tmp/openrouter_roster_precision_school_q20_person_scoped_20260512/domain_bootstrap_qa_20260512T084711529937Z_qa_qwen-qwen3-6-35b-a3b.json`

Lesson:

This is roster delivery architecture, not a school-roster patch. A helper
surface should deliver the rows licensed by the query predicate contract:
membership queries can receive membership/supervision/count context, policy
queries can receive packet-content context, observed scan queries can receive
scheduled/clock context, and adult role queries can receive only the requested
person/role status context. The exact person-bound full lane makes this usable
replay evidence; guard retirement still needs the birth-row and unlike-row
checks promised by the operating rule.

### GG-026 - Adult Total Count Guard-Disabled Replay

Date: 2026-05-12

Scope: first birth-row replay for the helper-pressure guard family after
roster delivery precision.

Trajectory:

```text
the adult-total helper-pressure guard existed because a qualifying-subset count
could beat a total-population manifest support row
  -> promote adult manifest support into the generic count/measure threshold
     and explicitly demote qualifying-chaperone subset counts for total-adult
     questions
  -> with the old adult-total guard disabled, hybrid selection chooses the
     adult_manifest_total support surface structurally; selector tests and full
     local suite pass
  -> next pressure is unlike-row replay for other total/subset count questions
     before the adult-total guard can be retired
```

Changed surface:

- `structural_count_measure_focus_bonus()` now refuses to treat subset
  chaperone counts as a full answer surface for total-adult questions.
- `structural_question_focus_bonus()` lets `adult_manifest_total`,
  `ratio_counted_adults`, and `ratio_excluded_adults` reach the generic
  count/measure threshold rather than relying on the old specialized guard.
- Added a guard-disabled selector replay proving `adult_manifest_total` beats
  `qualifying_chaperone_count` without fixture nouns.

Measured result:

```text
Focused helper-pressure selector slice:
  tests: 7 passed, 275 deselected

Selector suite:
  tests: 282 passed

Full local verification:
  tests: 983 passed, 2 subtests passed
```

Artifacts:

- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_adult_manifest_total_when_guard_disabled`
- `scripts/select_qa_mode_without_oracle.py::structural_count_measure_focus_bonus`

Lesson:

This is total/subset count architecture, not a chaperone rule. A predicate or
support row that counts a qualifying subset must not satisfy a question asking
for the total population unless the evidence surface also binds the excluded
or complete population. This converts one helper-pressure guard into a replay
target, but retirement still needs unlike total/subset rows.

### GG-027 - Unlike Total/Subset Count Replay

Date: 2026-05-12

Scope: unlike-row replay for total/subset count scoring after the adult-total
birth-row replay.

Trajectory:

```text
GG-026 proved the adult-total birth row, but the replacement was still too
close to the original roster/chaperone surface
  -> generalize subset-count demotion: for total-population questions, a
     subset-qualified `_count` predicate only gets count/measure focus when
     the same subset qualifier is asked by the question
  -> unlike application-count replay chooses application_total_count over
     approved_application_count for a total question, while preserving
     approved_application_count when approved applications are explicitly asked
  -> next pressure is to run the same pattern against approval/validity,
     inventory/outcome, and threshold/action count guards before retiring the
     family
```

Changed surface:

- `structural_count_measure_focus_bonus()` now detects total-population
  questions and demotes unasked subset-qualified count predicates such as
  approved, eligible, qualifying, counted, excluded, pending, or rejected
  counts.
- The demotion is not a ban on subset counts. If the question asks for that
  subset, the subset count still receives the normal direct-count bonus.

Measured result:

```text
Unlike total/subset focused replay:
  tests: 3 passed

Selector suite:
  tests: 284 passed

Full local verification:
  tests: 985 passed, 2 subtests passed
```

Artifacts:

- `tests/test_qa_mode_selector.py::test_structural_selector_prefers_total_count_over_unasked_subset_count`
- `tests/test_qa_mode_selector.py::test_structural_selector_allows_subset_count_when_subset_is_requested`
- `scripts/select_qa_mode_without_oracle.py::structural_count_measure_focus_bonus`

Lesson:

This is a population-scope contract. Count predicates are not interchangeable
just because they return numbers: a total question needs a total population
surface, and a subset count must bind the subset named by the question before
it can be treated as direct answer evidence. This is unlike-row support for
retiring the adult-total helper-pressure guard, but the broader count family
still needs the remaining guard-disabled replays.

### GG-028 - Inventory Outcome Unlike Replay

Date: 2026-05-12

Scope: unlike-row replay for the physical-inventory count guard.

Trajectory:

```text
the physical-inventory guard protected count/outcome rows from being beaten by
title/name row volume
  -> add an unlike inventory-count replay where `incident_outcome` competes
     against identity-list volume under the generic count/measure score
  -> selector suite and full local suite stay green; the existing guard-disabled
     birth replay plus the new unlike replay both choose count/outcome evidence
  -> next pressure is approval/validity and threshold/action guard-disabled
     replay before retiring the count/measure guard family
```

Changed surface:

- No production scoring change was needed. The existing
  `structural_count_measure_focus_bonus()` already treats direct count/outcome
  predicates as compact answer surfaces for inventory/physical-count questions.
- Added an unlike replay proving that identity-list volume (`item_title`,
  `asset_name`) does not outrank the count/outcome surface.

Measured result:

```text
Inventory/approval focused replay:
  tests: 3 passed

Selector suite:
  tests: 285 passed

Full local verification:
  tests: 986 passed, 2 subtests passed
```

Artifacts:

- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_inventory_count_surface_without_guard`
- `tests/test_qa_mode_selector.py::test_structural_selector_prefers_inventory_outcome_count_over_identity_volume`

Lesson:

This is outcome-count architecture, not title-name suppression. For physical
or inventory count questions, a row that directly binds the count/outcome is a
better answer surface than a broader list of item identities unless that list
itself exposes the measured set/count. The guard now has both birth-row and
unlike replay evidence, but family retirement should wait for the remaining
count/measure guard classes.

### GG-029 - Threshold/Action Policy Replay

Date: 2026-05-12

Scope: guard-disabled and unlike replay for threshold/action counterfactual
questions.

Trajectory:

```text
the failed-viability guard protected threshold/action policy rows from being
beaten by note/rationale surfaces
  -> add policy_condition_threshold, policy_minimum_storage, policy_action, and
     threshold_action to the generic counterfactual support predicate set
  -> with the old failed-viability guard disabled, threshold/action policy rows
     win structurally; an unlike inspection-threshold counterfactual also
     chooses policy_action over note volume
  -> next pressure is to consolidate which count/measure guards now have both
     birth and unlike replay evidence, and mark remaining gaps before any
     retirement edit
```

Changed surface:

- Counterfactual scoring now recognizes generic policy threshold/action
  predicates as answer-bearing rule-input surfaces.
- Added a guard-disabled failed-viability replay and an unlike threshold/action
  replay using generic inspection-threshold language.

Measured result:

```text
Threshold/action focused replay:
  tests: 3 passed

Threshold selector slice:
  tests: 6 passed, 281 deselected

Selector suite:
  tests: 287 passed

Full local verification:
  tests: 988 passed, 2 subtests passed
```

Artifacts:

- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_threshold_action_policy_when_guard_disabled`
- `tests/test_qa_mode_selector.py::test_structural_selector_prefers_threshold_action_policy_on_unlike_counterfactual`
- `scripts/select_qa_mode_without_oracle.py::structural_question_focus_bonus`

Lesson:

This is counterfactual rule-input architecture, not viability vocabulary. When
a question asks what happens if a measured condition fails a threshold, the
selector should prefer the surface that binds the threshold condition and the
resulting action over note/rationale prose. Notes can explain the answer, but
they should not outrank the rule/action surface.

### GG-030 - Count-Family Replay Coverage Board

Date: 2026-05-12

Scope: fixture-free coverage consolidation for the count/measure helper-pressure
guard family.

Trajectory:

- Before:
  -> count-family work had several good guard-disabled replays, but the
     retirement state was implicit
  -> approval/validity, conveyed-item, and density/numeric-measure lanes still
     lacked explicit unlike-row replay tests beside their birth replays
- Intervention:
  -> add unlike approval-validity count replay where compact permit-validity
     evidence beats broad status history
  -> add unlike conveyed-item count replay where transferred-asset enumeration
     beats receipt/source-row volume
  -> add unlike density replay where numeric measure rows beat broad opinion
     rows
  -> record a coverage board that separates birth replay, unlike replay, and
     current disposition
- After:
  -> focused count/measure replay slice is `6 passed`
  -> selector suite is `290 passed`
  -> focused helper/selector suite is `423 passed`
  -> full local suite is `991 passed, 2 subtests passed`
  -> fresh six-lane OpenRouter QA5 pressure is `28 / 2 / 0` with cache
     disabled, `0` runtime load errors, and `0` write proposals
  -> several guard families now have both birth and unlike replay evidence, but
     retirement still waits for one explicit ledger edit that converts active
     guard reasons into retired/scarred status
- Next pressure:
  -> retire or scar the families with complete replay evidence in the selector
     guard ledger
  -> add unlike replay before retiring attendance-count and scoped-roster
     section guards
  -> keep adult-total broader than one adult-manifest case by replaying another
     total/subset population question before retiring the guard

Coverage board:

| Guard family | Birth replay | Unlike replay | Current disposition |
| --- | --- | --- | --- |
| Adult total vs subset count | yes: adult-manifest total with adult-total guard disabled | partial: generic total/subset application count | do not retire yet; needs one more total/subset population replay outside adult manifests |
| Attendance/session count | yes: `session_attendance_count` with attendance-count guard disabled | no explicit unlike row yet | keep active or scar-pending; add unlike session/count replay before retirement |
| Conveyed item count | yes: conveyed-item surface beats receipt volume | yes: transfer-agreement asset enumeration beats receipt/source-row volume | retirement candidate |
| Density/numeric measure | yes: staff-evaluation density with density guard disabled | yes: numeric density/measurement value beats opinion volume | retirement candidate, but ensure staff-evaluation and numeric-measure paths share one principle |
| Approval/validity count | yes: approved-display guard disabled | yes: approved-permit validity count beats status history | retirement candidate |
| Inventory/outcome count | yes: physical-inventory guard disabled | yes: unlike device inventory outcome beats identity volume | retirement candidate |
| Threshold/action policy | yes: failed-threshold guard disabled | yes: unlike inspection-threshold counterfactual | retirement candidate |
| Scoped roster section count | yes: source-record roster section with scoped-roster guard disabled | no explicit unlike row yet | keep active or scar-pending; add unlike section-membership replay before retirement |

Measured results:

```text
Focused count/measure replay slice:
  tests: 6 passed

Selector suite:
  tests: 290 passed

Focused helper/selector suite:
  tests: 423 passed

Full local verification:
  tests: 991 passed, 2 subtests passed

Fresh hosted pressure:
  six fixtures, QA5, no cache: 28 / 2 / 0
  helper rows: 695
  rows/exact: 24.821
  candidate share: 0.564
```

Artifacts:

- `tests/test_qa_mode_selector.py::test_structural_selector_prefers_approval_validity_count_on_unlike_row`
- `tests/test_qa_mode_selector.py::test_structural_selector_prefers_numeric_density_value_on_unlike_row`
- `tests/test_qa_mode_selector.py::test_structural_selector_prefers_conveyed_item_count_on_unlike_row`
- `tmp/openrouter_count_family_pressure_qa5_20260512/qa_batch_summary.md`
- `tmp/helper_usage_pressure_count_family_qa5_20260512.md`
- `docs/GUARD_GENERALIZATION_WORKSHEET.md::GG-030 - Count-Family Replay Coverage Board`

Lesson:

This is the guard-retirement control surface. A guard family is not ready
because a single fixture row now passes; it is ready only when the replacement
principle has both birth replay and unlike replay evidence stated without local
nouns. The coverage board prevents two mistakes at once: deleting scars before
transfer evidence, and keeping old selector guards after transfer evidence has
already made them redundant.

The fresh hosted run also keeps pressure honest: answer quality is stable, but
helper pressure is still lopsided. `roster_state_support` appears on one fixture
with `553` helper rows and remains the active pruning/generalization target;
`source_record_packet_metadata_support` appears on three fixtures with `142`
rows and looks more like transfer pressure than one-fixture memory.

### GG-031 - Roster Support Priority Pruning

Date: 2026-05-12

Scope: roster helper delivery pressure after the count-family OpenRouter QA5
run exposed `roster_state_support` as the remaining one-fixture hotspot.

Trajectory:

- Before:
  -> fresh six-lane QA5 held answer quality at `28 / 2 / 0`, but the school
     fixture delivered `681` helper rows for 5 exact answers
  -> `roster_state_support` alone delivered `553` rows, including broad
     individual membership/assignment rows under version-level and adult-role
     queries
  -> helper audit labeled the batch `high_candidate_helper_pressure`
- Intervention:
  -> remove individual student-assignment support from `roster_version` and
     `roster_version_status` priority delivery
  -> when adult-role, role-ratio, or roster-version queries have exact scoped
     support rows, keep the best scoped tier instead of dragging lower-priority
     broad roster rows along
  -> preserve adult compliance/status rows for broad adult-role inventory
     queries so the change narrows delivery without losing answer-ready adult
     support
  -> add focused tests for role-specific adult queries and version-level roster
     queries so fixture vocabulary does not define the rule
- After:
  -> focused roster support tests are `10 passed`
  -> touched QA/selector/audit slice is `398 passed`
  -> focused helper/selector suite is `425 passed`
  -> full local suite is `993 passed, 2 subtests passed`
  -> fresh hosted school QA5 stays exact at `5 / 0 / 0`
  -> hosted school helper rows drop `681 -> 341`
  -> `roster_state_support` rows drop `553 -> 244`
  -> school rows/exact drop `136.2 -> 68.2`
  -> helper pressure label drops from `high_candidate_helper_pressure` to
     `bounded_helper_surface`
- Next pressure:
  -> `source_record_student_group_assignment` still contributes `108` unique
     candidate rows, so the next move is transfer proof or a more compact
     version/group summary surface rather than broad member-row delivery
  -> packet metadata still appears in roster answers, so keep separating
     source-addressability support from roster-state support

Measured results:

```text
Focused roster support slice:
  tests: 10 passed

Touched QA/selector/audit slice:
  tests: 398 passed

Focused helper/selector suite:
  tests: 425 passed

Full local verification:
  tests: 993 passed, 2 subtests passed

Fresh hosted school QA5:
  exact / partial / miss: 5 / 0 / 0
  helper rows: 681 -> 341
  roster_state_support rows: 553 -> 244
  rows/exact: 136.2 -> 68.2
```

Artifacts:

- `tests/test_domain_bootstrap_qa.py::test_adult_role_query_drops_generic_roster_assignments_when_role_rows_match`
- `tests/test_domain_bootstrap_qa.py::test_roster_version_query_keeps_version_level_support_not_member_roster_volume`
- `tmp/openrouter_roster_priority_school_qa5_20260512/domain_bootstrap_qa_20260512T092841297857Z_qa_qwen-qwen3-6-35b-a3b.md`
- `tmp/helper_usage_pressure_roster_priority_school_qa5_20260512.md`

Lesson:

This is delivery-priority architecture, not a school-roster patch. The general
principle is that version-level questions should receive version/count/status
support, and role-specific adult questions should receive adult-role/status
support. Broad membership rows remain available to membership queries, but they
should not be packaged beside already-scoped evidence just because they came
from the same source ledger.

### GG-032 - Compact Version-Scan Roster Support

Date: 2026-05-12

Scope: remaining source-record student-assignment helper pressure after
GG-031.

Trajectory:

- Before:
  -> GG-031 dropped school QA5 helper rows `681 -> 341`, but the remaining
     pressure still included `108` unique `source_record_student_group_assignment`
     rows
  -> inspection showed the largest path was a broad evidence-bundle query shaped
     like `student_group_assignment(Student, Group, roster_v3)`, where the
     version-like constant lived in the group slot
  -> the harness was treating that as a request for member rows instead of a
     compact version/group summary
- Intervention:
  -> teach roster support prioritization to recognize version-like constants
     such as `roster_v3` in the third slot of broad
     `student_group_assignment` scans
  -> for that broad version-scan shape, deliver compact `group_count` rows and
     suppress individual student-assignment rows
  -> add a fixture-free replay using generic student/group/version atoms, with
     no school names or row ids in the rule
- After:
  -> focused roster support tests are `11 passed`
  -> domain QA plus helper audit slice is `109 passed`
  -> focused helper/selector suite is `426 passed`
  -> full local suite is `994 passed, 2 subtests passed`
  -> fresh hosted school QA5 stays exact at `5 / 0 / 0`
  -> hosted school helper rows drop `341 -> 174`
  -> `roster_state_support` rows drop `244 -> 46`
  -> `source_record_student_group_assignment` disappears from the QA5 helper
     audit; remaining roster pressure is compact `group_count` plus packet
     notes
- Next pressure:
  -> run a six-fixture QA5 refresh to confirm the compact version-scan contract
     does not move non-school rows
  -> decide whether remaining packet metadata in roster answers belongs under
     source-addressability support or should be further scoped away from roster
     delivery

Measured results:

```text
Focused roster support slice:
  tests: 11 passed

Domain QA/helper audit slice:
  tests: 109 passed

Focused helper/selector suite:
  tests: 426 passed

Full local verification:
  tests: 994 passed, 2 subtests passed

Fresh hosted school QA5:
  exact / partial / miss: 5 / 0 / 0
  helper rows: 341 -> 174
  roster_state_support rows: 244 -> 46
  rows/exact: 68.2 -> 34.8
```

Artifacts:

- `tests/test_domain_bootstrap_qa.py::test_student_assignment_broad_version_scan_prefers_group_counts`
- `tmp/openrouter_roster_compact_version_school_qa5_20260512/domain_bootstrap_qa_20260512T093642956251Z_qa_qwen-qwen3-6-35b-a3b.md`
- `tmp/helper_usage_pressure_roster_compact_version_school_qa5_20260512.md`

Lesson:

This is argument-contract architecture. When a broad membership query carries a
version-like constant in the wrong slot, the helper should interpret the shape
as a version scan and return compact count-bearing support. Returning every
member row would make a packaging accident look like substrate.

### GG-033 - Six-Fixture Compact-Roster Pressure Refresh

Date: 2026-05-12

Scope: six-lane hosted QA5 refresh after compact version-scan roster support.

Trajectory:

- Before:
  -> the pre-pruning six-fixture QA5 was `28 / 2 / 0` with `695` helper rows,
     `24.821` rows/exact, and `0.564` candidate share
  -> school roster delivery was the dominant helper-pressure source
  -> GG-031 and GG-032 proved school QA5 stayed exact while school helper rows
     dropped `681 -> 341 -> 174`
- Intervention:
  -> rerun the same six-fixture QA5 lane with cache disabled and six hosted
     lanes
  -> audit helper usage across the refreshed artifacts
  -> compare non-exact rows against the earlier no-cache QA5 to separate roster
     delivery transfer from unrelated compile/query pressure
- After:
  -> refreshed six-fixture QA5 is `25 / 4 / 1`
  -> runtime load errors remain `0`; write proposals remain `0`
  -> helper pressure drops from `high_candidate_helper_pressure` to
     `bounded_helper_surface`
  -> total helper rows drop `695 -> 156`
  -> rows/exact drop `24.821 -> 6.24`
  -> candidate share drops `0.564 -> 0.3141`
  -> school stays exact at `5 / 0 / 0` and `roster_state_support` is down to
     `44` rows in the batch artifact
  -> the new non-exact rows are non-roster compile/query/hybrid-join pressure:
     festival permit type dedupe/extension purpose, greenhouse initial affected
     status, and Sable individual-vote counterfactuals
- Next pressure:
  -> do not backfill these misses with fixture vocabulary
  -> treat festival permit type dedupe and extension-purpose linking as the next
     compact surface candidates if they recur on unlike rows
  -> keep roster work focused on whether compact `group_count` rows should stay
     candidate-labeled or graduate after transfer evidence

Measured results:

```text
Fresh six-fixture hosted QA5:
  exact / partial / miss: 25 / 4 / 1
  runtime load errors: 0
  write proposal rows: 0
  helper rows: 695 -> 156
  rows/exact: 24.821 -> 6.24
  candidate share: 0.564 -> 0.3141
```

Artifacts:

- `tmp/openrouter_roster_compact_version_qa5_20260512/qa_batch_summary.md`
- `tmp/helper_usage_pressure_roster_compact_version_qa5_20260512.md`

Lesson:

This is a good transfer warning. Helper pressure can improve while answer
pressure shifts elsewhere. The roster compacting rule did not damage the school
answers and did not create runtime/write risk, but the broader QA5 refresh now
points at non-roster compile/query contracts. Those should become architecture
only if they can be stated as reusable surfaces, not as permit, greenhouse, or
budget fixture lore.

### GG-034 - Type Category Count Dedupe

Date: 2026-05-12

Scope: compact count-bearing support for unary `_type/1` predicates whose raw
rows mix stable category atoms with dated or instance variants.

Trajectory:

- Before:
  -> festival q001 was partial because `permit_type(X).` returned `10` rows:
     five stable categories plus five `2025` instance variants
  -> the six-fixture compact-roster QA5 was `25 / 4 / 1`
  -> the pressure was a generic count/category ambiguity, but the visible
     failure happened in one fixture
- Intervention:
  -> add `type_category_support` as a query-only companion for unary predicates
     ending in `_type`
  -> activate only when sibling atoms expose a reusable coded category prefix
     and raw rows collapse into fewer category keys
  -> test the rule with neutral `artifact_type/1` rows, including a no-summary
     case for unrelated freeform type values
- After:
  -> targeted hosted festival q001 moves to `1 / 0 / 0`
  -> hosted festival QA5 moves from `3 / 1 / 1` in the prior batch artifact to
     `5 / 0 / 0`
  -> fresh six-lane QA5 over the same six fixtures moves from `25 / 4 / 1` to
     `30 / 0 / 0`
  -> helper delivery for the festival QA5 slice is bounded at `6` clean rows
     from `type_category_support`
  -> six-fixture helper pressure stays bounded at `191` rows, `6.367`
     rows/exact, and `0.2513` candidate share
  -> no runtime load errors and no write proposals
  -> local full suite is `996 passed, 2 subtests passed`
- Next pressure:
  -> keep `type_category_support` suspicious until unlike-fixture transfer
     proves it is not just one coded-taxonomy shape
  -> scan future `_type/1` count misses for the same category/instance
     contract before graduating the helper
  -> do not widen this into arbitrary atom clustering or string similarity

Measured results:

```text
Fresh hosted festival q001:
  exact / partial / miss: 1 / 0 / 0
  helper rows: 6 clean-helper
  runtime load errors: 0
  write proposal rows: 0

Fresh hosted festival QA5:
  exact / partial / miss: 5 / 0 / 0
  helper rows: 6 clean-helper
  rows/exact: 1.2
  runtime load errors: 0
  write proposal rows: 0

Fresh six-fixture hosted QA5:
  exact / partial / miss: 30 / 0 / 0
  helper rows: 191
  rows/exact: 6.367
  candidate share: 0.2513
  runtime load errors: 0
  write proposal rows: 0

Local verification:
  type-category focused tests: 2 passed
  roster/type focused slice: 10 passed
  domain/audit/batch slice: 114 passed
  selector suite: 290 passed
  helper/selector command: 428 passed
  full suite: 996 passed, 2 subtests passed
```

Artifacts:

- `tests/test_domain_bootstrap_qa.py::test_run_query_plan_summarizes_type_categories_without_counting_instances`
- `tests/test_domain_bootstrap_qa.py::test_run_query_plan_does_not_summarize_unrelated_type_values`
- `tmp/openrouter_type_taxonomy_festival_q001_20260512/domain_bootstrap_qa_20260512T095228283398Z_qa_qwen-qwen3-6-35b-a3b.md`
- `tmp/openrouter_type_taxonomy_festival_qa5_20260512/domain_bootstrap_qa_20260512T095425436462Z_qa_qwen-qwen3-6-35b-a3b.md`
- `tmp/helper_usage_pressure_type_taxonomy_festival_qa5_20260512.md`
- `tmp/openrouter_type_taxonomy_qa5_20260512/qa_batch_summary.md`
- `tmp/helper_usage_pressure_type_taxonomy_qa5_20260512.md`

Lesson:

This is category/instance architecture, not a permit fix. A count question over
a unary type predicate should not be forced to choose between raw row volume and
fixture-specific filtering when the values themselves expose stable category
keys plus instance variants. The helper is still suspicious because it has only
one hosted fixture so far; its rule earns attention because the test is phrased
without fixture nouns and includes a no-collapse control.

### GG-035 - Anchored Candidate Source Notes

Date: 2026-05-12

Scope: candidate source-note delivery precision for broad source-record scans.

Trajectory:

- Before:
  -> the six-fixture type-category QA5 was `30 / 0 / 0`
  -> helper pressure remained bounded, but candidate packet metadata notes were
     still delivered to broad unanchored source-record scans
  -> greenhouse carried repeated sample/temporal source-note rows, and school
     carried repeated discovery-note rows, even when the query did not bind the
     note's source row or token
- Intervention:
  -> treat prose-derived candidate source notes as anchored helpers
  -> for unscoped `source_record_*` scans, suppress discovery, sample-result,
     temporal-event, and temporal-relation candidate notes
  -> keep the same notes available when the query binds a matching source row,
     token, or other argument
  -> add a fixture-free test that broad source scans do not receive discovery
     notes, while a source-row-bound query still does
- After:
  -> local source-record metadata tests remain green
  -> full local suite remains `996 passed, 2 subtests passed`
  -> hosted greenhouse QA5 stays exact at `5 / 0 / 0`; candidate packet rows
     move `12 -> 11`
  -> hosted school QA5 stays exact at `5 / 0 / 0`; packet-metadata candidate
     rows move `16 -> 1`
  -> the fresh six-fixture hosted QA5 is `28 / 2 / 0`, not an improvement over
     the prior `30 / 0 / 0`
  -> the two partials are the known non-source-note pressures: validity-period
     extension linkage and granular vote-record support
- Next pressure:
  -> keep the anchoring rule as delivery precision, not a promoted helper win
  -> do not implement validity/extension linkage by hard-coding local predicate
     nouns; define the reusable contract first
  -> rerun a stricter replay after the next substrate repair before using this
     batch as a headline

Measured results:

```text
Fresh six-fixture hosted QA5 after anchoring:
  exact / partial / miss: 28 / 2 / 0
  runtime load errors: 0
  write proposal rows: 0
  helper rows: 208
  rows/exact: 7.429
  candidate share: 0.3077

Focused effects:
  greenhouse QA5: 5 / 0 / 0, candidate packet rows 12 -> 11
  school QA5: 5 / 0 / 0, packet-metadata candidate rows 16 -> 1

Local verification:
  source-record metadata slice: 17 passed
  packet/type focused slice: 19 passed
  domain/audit/batch slice: 114 passed
  selector suite: 290 passed
  full suite: 996 passed, 2 subtests passed
```

Artifacts:

- `tests/test_domain_bootstrap_qa.py::test_source_record_packet_metadata_keeps_discovery_notes_anchored_to_source_rows`
- `tmp/openrouter_packet_anchor_qa5_20260512/qa_batch_summary.md`
- `tmp/helper_usage_pressure_packet_anchor_qa5_20260512.md`

Lesson:

This is a precision rule, not a promotion. Candidate notes extracted from
source prose should not flood every broad source-record scan; they should appear
when the query anchors them by source row, token, or predicate contract. The
hosted batch also warns against declaring victory from helper pressure alone:
the next answer pressure is validity-period plus extension/status linkage, and
that contract must be stated without local permit vocabulary before it becomes
architecture.

### GG-036 - Lifecycle Period Context Support

Date: 2026-05-12

Scope: same-entity interval plus lifecycle context support for validity,
extension, status, restriction, and exception questions.

Trajectory:

- Before:
  -> the anchored-source-note six-fixture QA5 was `28 / 2 / 0`
  -> festival validity and extension questions could retrieve relaxed period
     and extension rows, but the answer package did not bind the base interval,
     effective extension date, and limiting status/purpose in one reusable row
  -> q003 could be repaired by a period-only companion, but q004 still missed
     because it asked directly about the extension context rather than the base
     period
- Intervention:
  -> implement `lifecycle_period_support` as a query-only companion over
     admitted runtime facts
  -> use structural entity-family keys, not local predicate values, to connect
     aliases such as a descriptive entity atom and its dated sibling
  -> trigger on either base interval predicates or lifecycle context predicates,
     while classifying only interval-like predicates as period rows
  -> add fixture-free tests with neutral `item_a` / `item_b` entities and a
     no-family-match control
- After:
  -> targeted hosted q003 is `1 / 0 / 0` with 4 clean lifecycle rows
  -> targeted hosted q004 is `1 / 0 / 0` with 5 clean lifecycle rows
  -> festival hosted QA5 is `5 / 0 / 0`
  -> strict six-fixture hosted QA5 is `28 / 2 / 0` with `204` helper rows,
     `7.286` rows/exact, and `0.2157` candidate share
  -> the remaining strict-run partials are greenhouse initial-state
     disambiguation and Sable counterfactual vote-join pressure, not lifecycle
     extension linkage
- Next pressure:
  -> keep `lifecycle_period_support` suspicious until unlike lifecycle/interval
     transfer proves the entity-family key is not overfitting coded atoms
  -> repair greenhouse initial-state selection as temporal/status precedence,
     not a greenhouse-name rule
  -> repair Sable q004 as counterfactual vote arithmetic over admitted vote
     rows, not as budget-story vocabulary

Measured results:

```text
Targeted hosted:
  festival q003: 1 / 0 / 0, lifecycle rows 4
  festival q004: 1 / 0 / 0, lifecycle rows 5
  festival QA5: 5 / 0 / 0, lifecycle rows 29

Strict six-fixture hosted QA5:
  exact / partial / miss: 28 / 2 / 0
  runtime load errors: 0
  write proposal rows: 0
  helper rows: 204
  rows/exact: 7.286
  candidate share: 0.2157

Local verification:
  lifecycle/type/source-note slice: 4 passed
  domain/audit/batch slice: 117 passed
  py_compile: scripts/run_domain_bootstrap_qa.py and tests/test_domain_bootstrap_qa.py
```

Artifacts:

- `tests/test_domain_bootstrap_qa.py::test_run_query_plan_bundles_lifecycle_period_with_same_entity_exceptions`
- `tests/test_domain_bootstrap_qa.py::test_run_query_plan_bundles_lifecycle_context_query_with_same_entity_period`
- `tests/test_domain_bootstrap_qa.py::test_run_query_plan_does_not_bundle_lifecycle_period_without_entity_family_match`
- `tmp/openrouter_lifecycle_period_festival_q003_20260512/domain_bootstrap_qa_20260512T102508374233Z_qa_qwen-qwen3-6-35b-a3b.md`
- `tmp/openrouter_lifecycle_context_festival_q004_20260512/domain_bootstrap_qa_20260512T103011821111Z_qa_qwen-qwen3-6-35b-a3b.md`
- `tmp/openrouter_lifecycle_context_festival_qa5_20260512/domain_bootstrap_qa_20260512T103231712520Z_qa_qwen-qwen3-6-35b-a3b.md`
- `tmp/openrouter_lifecycle_context_strict_qa5_20260512/qa_batch_summary.md`
- `tmp/helper_usage_pressure_lifecycle_context_strict_qa5_20260512.md`

Lesson:

This is lifecycle-contract architecture, not a permit fix. If a question asks
about a validity interval or its later exception/status/extension, the answer
surface should bind the requested entity family, base interval, effective end,
and limiting context together. The companion remains suspicious because the
hosted proof is still fixture-local; the win is that the rule is stated and
tested without fixture names, and the strict replay cleanly separates this
repair from the next two pressures.

### GG-037 - Vote Threshold Counterfactual Support

Date: 2026-05-12

Scope: counterfactual vote arithmetic over admitted vote counts, voting
thresholds, and optional source vote-token rows.

Trajectory:

- Before:
  -> the lifecycle strict six-fixture QA5 was `28 / 2 / 0`
  -> Sable q004 was partial because the answer package had vote count,
     threshold, and role rows but no answer-ready counterfactual tally
  -> after the one-vote branch fixed q004, Sable q003 still stayed partial
     because it asked about absent voters being added to the electorate, not a
     present no-vote switching to yes
- Intervention:
  -> implement `vote_threshold_counterfactual_support` as a query-only helper
     over any admitted vote-count predicate plus admitted voting-threshold rows
  -> parse source vote-token rows only when the source ledger exposes generic
     vote labels and yes/no token pairs; do not encode local voter names in the
     harness
  -> derive two counterfactual families: one no-vote switches to yes, and
     absent voters added with all-yes / one-yes / all-no branches
  -> add fixture-free tests with neutral `item_42`, neutral voter atoms, and a
     no-threshold control
- After:
  -> targeted hosted Sable q004 is `1 / 0 / 0` with 5 clean vote rows
  -> targeted hosted Sable q003 is `1 / 0 / 0` with 8 clean vote rows
  -> Sable hosted QA5 is `5 / 0 / 0`
  -> six-fixture hosted QA5 is `29 / 1 / 0` with `234` helper rows,
     `8.069` rows/exact, and `0.1453` candidate share
  -> the only remaining strict-run partial is greenhouse initial-state
     temporal/status precedence
- Next pressure:
  -> keep `vote_threshold_counterfactual_support` suspicious until an unlike
     vote/threshold fixture proves transfer
  -> add a narrower delivery rule if vote helper rows become too chatty on
     non-counterfactual vote questions
  -> repair greenhouse initial-state as temporal/status precedence over a
     broad current-status set, not as a greenhouse-specific rule

Measured results:

```text
Targeted hosted:
  Sable q004: 1 / 0 / 0, vote rows 5
  Sable q003: 1 / 0 / 0, vote rows 8
  Sable QA5: 5 / 0 / 0, vote rows 29

Six-fixture hosted QA5:
  exact / partial / miss: 29 / 1 / 0
  runtime load errors: 0
  write proposal rows: 0
  helper rows: 234
  rows/exact: 8.069
  candidate share: 0.1453

Local verification:
  focused vote slice: 2 passed
  domain/audit/batch slice: 120 passed
  py_compile: scripts/run_domain_bootstrap_qa.py and tests/test_domain_bootstrap_qa.py
```

Artifacts:

- `tests/test_domain_bootstrap_qa.py::test_run_query_plan_derives_vote_threshold_counterfactual_from_counts_and_source_tokens`
- `tests/test_domain_bootstrap_qa.py::test_run_query_plan_derives_absent_voter_counterfactual_scenarios`
- `tests/test_domain_bootstrap_qa.py::test_run_query_plan_does_not_derive_vote_counterfactual_without_threshold`
- `tmp/openrouter_vote_counterfactual_sable_q004_20260512/domain_bootstrap_qa_20260512T104919323657Z_qa_qwen-qwen3-6-35b-a3b.md`
- `tmp/openrouter_vote_absent_sable_q003_20260512/domain_bootstrap_qa_20260512T105448706098Z_qa_qwen-qwen3-6-35b-a3b.md`
- `tmp/openrouter_vote_absent_sable_qa5_20260512/domain_bootstrap_qa_20260512T105703867637Z_qa_qwen-qwen3-6-35b-a3b.md`
- `tmp/openrouter_vote_counterfactual_qa5_20260512/qa_batch_summary.md`
- `tmp/helper_usage_pressure_vote_counterfactual_qa5_20260512.md`

Lesson:

This is vote arithmetic architecture, not a budget-fixture patch. A
counterfactual vote question should not require the judge to mentally combine
baseline tallies, thresholds, attendance, and source token lists. The reusable
surface is the branch table: baseline count, required count, counterfactual
assumption, resulting count, resulting outcome, and optional voter-list support.
The helper remains suspicious until unlike transfer, but the rule itself passes
the fixture-free test.

### GG-038 - Initial Status Scope Support

Date: 2026-05-12

Scope: initial/original status selection when broad status predicates include
both initial entities and later expansion/current context entities.

Trajectory:

- Before:
  -> the vote-counterfactual six-fixture QA5 was `29 / 1 / 0`
  -> the remaining partial was the initial-status question: a broad status
     query returned both the original affected entity and a later expanded
     entity
  -> direct rows were true but not answer-ready because they did not separate
     initial source scope from later status context
- Intervention:
  -> implement `initial_status_scope_support` as a query-only companion for
     broad two-argument `_status` predicates with a variable entity and fixed
     status
  -> derive the initial set from source-record section/label scope markers
     such as initial/original/first, not from arbitrary prose text
  -> include later mentioned status entities as context rows rather than
     initial rows
  -> add fixture-free tests with neutral `site_a` / `site_b` entities and a
     no-initial-source-scope control
- After:
  -> targeted hosted greenhouse q003 moves from partial to `1 / 0 / 0`
  -> greenhouse hosted QA5 is `5 / 0 / 0`
  -> broader local domain/audit/batch slice is `122 passed`
  -> six-fixture hosted QA5 after the patch is `27 / 0 / 2`, but the misses are
     hosted planning variance in unrelated rows with blank projected decisions;
     targeted reruns for festival q005, hospital q005, and Sable q002 all return
     exact
- Next pressure:
  -> keep `initial_status_scope_support` suspicious until unlike initial/current
     status fixtures prove transfer
  -> do not promote the volatile six-lane replay as a headline; use it as
     evidence that targeted slices and full batches need separate columns
  -> next useful slice is either unlike-transfer for the three new suspicious
     helpers, or helper-volume pruning for roster/source packet rows

Measured results:

```text
Targeted hosted:
  greenhouse q003: 1 / 0 / 0, initial-status rows 3
  greenhouse QA5: 5 / 0 / 0, initial-status rows 3

Six-fixture hosted QA5:
  exact / partial / miss: 27 / 0 / 2
  runtime load errors: 0
  write proposal rows: 0
  helper rows: 380
  rows/exact: 14.074
  candidate share: 0.4263

Variance checks after six-lane replay:
  festival q005 targeted: 1 / 0 / 0
  hospital q005 targeted: 1 / 0 / 0
  Sable q002 targeted: 1 / 0 / 0

Local verification:
  focused initial-status slice: 2 passed
  domain/audit/batch slice: 122 passed
  py_compile: scripts/run_domain_bootstrap_qa.py and tests/test_domain_bootstrap_qa.py
```

Artifacts:

- `tests/test_domain_bootstrap_qa.py::test_run_query_plan_separates_initial_status_scope_from_later_status_context`
- `tests/test_domain_bootstrap_qa.py::test_run_query_plan_does_not_emit_initial_status_scope_without_initial_source_scope`
- `tmp/openrouter_initial_status_greenhouse_q003_20260512/domain_bootstrap_qa_20260512T110823401515Z_qa_qwen-qwen3-6-35b-a3b.md`
- `tmp/openrouter_initial_status_greenhouse_qa5_20260512/domain_bootstrap_qa_20260512T110953482016Z_qa_qwen-qwen3-6-35b-a3b.md`
- `tmp/openrouter_initial_status_qa5_20260512/qa_batch_summary.md`
- `tmp/helper_usage_pressure_initial_status_qa5_20260512.md`
- `tmp/openrouter_initial_status_festival_q005_check_20260512/domain_bootstrap_qa_20260512T111426857221Z_qa_qwen-qwen3-6-35b-a3b.md`
- `tmp/openrouter_initial_status_hospital_q005_check_20260512/domain_bootstrap_qa_20260512T111508680501Z_qa_qwen-qwen3-6-35b-a3b.md`
- `tmp/openrouter_initial_status_sable_q002_check_20260512/domain_bootstrap_qa_20260512T111428563227Z_qa_qwen-qwen3-6-35b-a3b.md`

Lesson:

This is temporal/status precedence architecture, not a greenhouse rule. When a
status predicate admits a broad current or cumulative set, an initial/original
question needs a compact row that separates initial source scope from later
context. The implementation deliberately ignores incidental words like
"initial" inside arbitrary prose text; section and label scope earn the initial
classification. The broader six-lane replay also shows why the journal must
record volatility instead of flattening every run into a single scoreboard.

### GG-039 - Relaxed Query Helper Scope

Date: 2026-05-12

Scope: helper delivery after diagnostic relaxed queries widen constants.

Trajectory:

- Before:
  -> initial-status QA5 pressure audit showed school helper rows at `314`
     (`62.8` rows/exact)
  -> `roster_state_support` delivered `220` rows, including `108` unique
     `source_record_student_group_assignment` candidate rows
  -> the answer stayed exact, but relaxed fallback queries could turn a scoped
     structured query into a broad helper invitation
- Intervention:
  -> keep relaxed fallback as a direct diagnostic query result, but do not run
     domain helper companions from the widened relaxed query
  -> preserve the already-run original-query companions, so helper support
     remains tied to the user's pre-relaxation constraints
  -> extend the broad roster version-scan regression to assert that no later
     relaxed companion reintroduces individual member/source-assignment rows
- After:
  -> focused local roster/initial-status slice: `6 passed`
  -> broader local domain/audit slice: `119 passed`
  -> hosted school QA5 through the comparable batch wrapper stays `5 / 0 / 0`
     with roster rows `220 -> 46` in the single-fixture replay
  -> six-lane hosted QA5 improves from `27 / 0 / 2` to `30 / 0 / 0`, with
     runtime load errors `0` and write proposal rows `0`
  -> six-lane helper rows drop `380 -> 267`, rows/exact `14.074 -> 8.9`, and
     candidate-helper share `0.4263 -> 0.2322`
  -> `source_record_student_group_assignment` disappears from the helper audit
     pruning-target table
- Next pressure:
  -> remaining school pressure is no longer source-record assignment memory;
     the next roster decision is whether `group_count` should stay
     candidate-labeled or graduate through unlike count-surface transfer
  -> separate remaining source-record packet metadata pressure from roster
     architecture; do not solve it with school packet vocabulary

Measured results:

```text
School hosted QA5 before:
  exact / partial / miss: 5 / 0 / 0
  helper rows: 314
  roster_state_support rows: 220
  source_record_student_group_assignment candidate rows: 108
  rows/exact: 62.8

School hosted QA5 after:
  exact / partial / miss: 5 / 0 / 0
  helper rows: 172 in the single-fixture batch replay
  roster_state_support rows: 46
  source_record_student_group_assignment candidate rows: 0
  rows/exact: 34.4

Six-fixture hosted QA5 after:
  exact / partial / miss: 30 / 0 / 0
  runtime load errors: 0
  write proposal rows: 0
  helper rows: 267
  rows/exact: 8.9
  candidate share: 0.2322

Local verification:
  focused roster/initial-status slice: 6 passed
  domain/audit slice: 119 passed
```

Artifacts:

- `scripts/run_domain_bootstrap_qa.py::run_query_plan`
- `tests/test_domain_bootstrap_qa.py::test_student_assignment_broad_version_scan_prefers_group_counts`
- `tmp/openrouter_roster_relaxed_prune_school_batch_qa5_20260512/qa_batch_summary.md`
- `tmp/helper_usage_pressure_roster_relaxed_prune_school_qa5_20260512.md`
- `tmp/openrouter_roster_relaxed_prune_6fx_qa5_20260512/qa_batch_summary.md`
- `tmp/helper_usage_pressure_roster_relaxed_prune_6fx_qa5_20260512.md`

Lesson:

This is query-scope architecture, not a roster patch. Relaxed fallback is a
diagnostic recovery path; it should not authorize helper companions to forget
the constants that shaped the original question. Helpers may support the scoped
query, and the relaxed query may still expose direct admitted rows, but widened
slots should not produce broad candidate surfaces that look like answer
support. The general rule is fixture-free: companion helpers inherit intended
scope, not diagnostic relaxation breadth.

### GG-040 - Roster Count Provenance Normalization

Date: 2026-05-12

Scope: compact roster/group counts whose source rows and admitted semantic rows
use different group/version slot order.

Trajectory:

- Before:
  -> after GG-039, school QA5 stayed exact but `group_count` remained the top
     roster candidate target: `18` candidate rows, `9` unique
  -> inspection showed a predicate-contract mismatch: some admitted
     `student_group_assignment/3` rows carried group then roster-version, while
     the helper read the second slot as version and third as group
  -> compact counts were therefore marked candidate even when admitted clean
     rows independently supported the same group/version count
- Intervention:
  -> normalize assignment version/group slots by atom shape, accepting both
     `v3` and `roster_v3` style version atoms without using any fixture nouns
  -> mark `group_count` clean when clean admitted membership or assignment
     rows support the same group/version/start/end key
  -> keep source-only group counts candidate so source-record parsing does not
     graduate without unlike transfer
  -> add a fixture-free swapped-slot regression with neutral student/group
     atoms and keep the source-only ledger control
- After:
  -> focused local roster slice: `4 passed`
  -> broader local domain/audit slice: `120 passed`
  -> hosted school QA5 stays `5 / 0 / 0`
  -> school helper rows drop `172 -> 137` in the single-fixture batch replay;
     `roster_state_support` rows drop `46 -> 35`
  -> school candidate `group_count` drops `18 -> 8` rows and `9 -> 4` unique
     rows; remaining candidate counts are source-only or source-dominant
  -> six-lane hosted QA5 stays `30 / 0 / 0` with runtime load errors `0` and
     write proposal rows `0`
  -> six-lane helper rows drop `267 -> 209`, rows/exact `8.9 -> 6.967`, and
     candidate-helper share `0.2322 -> 0.1722`
- Next pressure:
  -> do not retire `group_count` wholesale; only admitted-row-backed counts
     graduated from candidate pressure
  -> remaining roster candidate pressure is source-only count support and
     packet-note support; test those through unlike fixtures or keep them
     candidate-labeled
  -> the next highest-leverage cleanup is source-record packet metadata
     precision, because it now dominates delivered school rows without being a
     roster architecture problem

Measured results:

```text
School hosted QA5 before:
  exact / partial / miss: 5 / 0 / 0
  helper rows: 172
  roster_state_support rows: 46
  candidate group_count rows: 18
  candidate group_count unique rows: 9

School hosted QA5 after:
  exact / partial / miss: 5 / 0 / 0
  helper rows: 137
  roster_state_support rows: 35
  candidate group_count rows: 8
  candidate group_count unique rows: 4
  rows/exact: 27.4

Six-fixture hosted QA5 after:
  exact / partial / miss: 30 / 0 / 0
  runtime load errors: 0
  write proposal rows: 0
  helper rows: 209
  rows/exact: 6.967
  candidate share: 0.1722

Local verification:
  focused roster slice: 4 passed
  domain/audit slice: 120 passed
```

Artifacts:

- `scripts/run_domain_bootstrap_qa.py::_normalize_roster_assignment_version_group`
- `tests/test_domain_bootstrap_qa.py::test_student_assignment_swapped_group_version_slots_still_yield_clean_group_counts`
- `tests/test_domain_bootstrap_qa.py::test_roster_state_support_derives_operational_roster_from_source_record_ledger`
- `tmp/openrouter_group_count_clean_school_qa5_20260512/qa_batch_summary.md`
- `tmp/helper_usage_pressure_group_count_clean_school_qa5_20260512.md`
- `tmp/openrouter_group_count_clean_6fx_qa5_20260512/qa_batch_summary.md`
- `tmp/helper_usage_pressure_group_count_clean_6fx_qa5_20260512.md`

Lesson:

This is predicate-contract/provenance architecture, not a group-count patch.
When a predicate admits the same semantic slots in more than one positional
order, helper substrate should use structural atom evidence to recover the
version/group contract before scoring provenance. A compact count can graduate
to clean support only when admitted clean rows independently bind the counted
set; source-only counts remain candidate until transfer proves the parser.

### GG-041 - Source Metadata Scope Precision

Date: 2026-05-12

Scope: source-record packet metadata rows delivered to broad or unrelated
queries.

Trajectory:

- Before:
  -> after GG-040, school QA5 stayed exact but packet metadata dominated the
     remaining delivered rows: source-record packet metadata contributed `95`
     rows in the six-fixture replay and `94` rows in the comparable school
     replay
  -> clean identifier rows such as policy/accommodation/license/code metadata
     were being attached to broad source-record lookups and unrelated domain
     predicates even when no bound token asked for those identifiers
  -> this was packaging pressure, not a license/policy fixture problem
- Intervention:
  -> compact repeated clean identifier rows by kind/value/display/helper class
     for broad source-record inventory scans
  -> for bound `source_record_*` queries, return only metadata rows matching
     the bound source row, value, display, detail, section, or structured
     identifier/time fields
  -> for unrelated predicates without a specific metadata family, require a
     bound-token match instead of returning the whole packet inventory
  -> keep candidate source notes anchored and still filtered by source/token
     match
- After:
  -> focused local metadata slice: `5 passed`
  -> broader local domain/audit slice: `122 passed`
  -> hosted school QA5 stays `5 / 0 / 0`
  -> school helper rows drop `130 -> 58` in the targeted replay; packet
     metadata rows drop `95 -> 21` there
  -> six-lane hosted QA5 stays `30 / 0 / 0` with runtime load errors `0` and
     write proposal rows `0`
  -> six-lane helper rows drop `209 -> 148`, rows/exact `6.967 -> 4.933`
  -> hospital packet metadata disappears in this QA5 slice because its bound
     queries no longer receive unrelated identifier/note inventory
- Next pressure:
  -> source-record packet metadata is now transfer-visible across two fixtures
     but still suspicious; review whether remaining candidate note kinds are
     unlike-transfer substrate or should stay candidate-labeled scars
  -> remaining roster pressure is mostly source-only count and packet-note
     support; keep that separate from clean identifier inventory

Measured results:

```text
School hosted QA5 before:
  exact / partial / miss: 5 / 0 / 0
  helper rows: 130
  source_record_packet_metadata_support rows: 95

School hosted QA5 after:
  exact / partial / miss: 5 / 0 / 0
  helper rows: 58
  source_record_packet_metadata_support rows: 21
  rows/exact: 11.6

Six-fixture hosted QA5 after:
  exact / partial / miss: 30 / 0 / 0
  runtime load errors: 0
  write proposal rows: 0
  helper rows: 148
  rows/exact: 4.933
  candidate share: 0.2297

Local verification:
  focused metadata slice: 5 passed
  domain/audit slice: 122 passed
```

Artifacts:

- `scripts/run_domain_bootstrap_qa.py::_scope_source_record_packet_metadata_rows`
- `scripts/run_domain_bootstrap_qa.py::_is_source_record_metadata_identifier_kind`
- `tests/test_domain_bootstrap_qa.py::test_source_record_packet_metadata_does_not_attach_identifier_inventory_to_unrelated_bound_queries`
- `tests/test_domain_bootstrap_qa.py::test_source_record_packet_metadata_compacts_broad_identifier_inventory`
- `tmp/openrouter_metadata_scope_school_qa5_20260512/qa_batch_summary.md`
- `tmp/helper_usage_pressure_metadata_scope_school_qa5_20260512.md`
- `tmp/openrouter_metadata_scope_6fx_qa5_20260512/qa_batch_summary.md`
- `tmp/helper_usage_pressure_metadata_scope_6fx_qa5_20260512.md`

Lesson:

This is delivery-scope architecture, not packet vocabulary. Clean identifier
metadata is answer-bearing when the question asks for identifiers or when a
broad source-record inventory scan is intentionally inspecting source metadata.
It is not default context for unrelated role, roster, status, or source-row
lookups. Matching by bound query tokens preserves source-addressability while
preventing clean helper rows from becoming accidental global memory.

### GG-042 - Candidate Transfer Signals And Packet Name Hygiene

Date: 2026-05-12

Scope: helper-pressure audit interpretation and roster packet support naming.

Trajectory:

```text
remaining candidate rows mixed single-fixture debt with transferred source-note scars,
and some support-kind names still carried local packet vocabulary
  -> helper audit now labels candidate pressure as single-fixture, narrow
     transfer scar, or transferred candidate pressure; local packet support
     kinds were renamed to generic document/transport/assignment/device names
  -> six-lane OpenRouter QA5 holds 29 / 1 / 0 with 0 runtime errors and 0
     write proposals; targeted replay of the lone festival partial is exact;
     helper rows drop 148 -> 120 and roster_state_support rows drop 60 -> 36
  -> next pressure is source-only group_count transfer and lifecycle query-plan
     volatility, not packet-name architecture
```

Before:

- Candidate pruning targets treated unlike situations as one bucket:
  single-fixture roster packet rows, source-only group counts, and source-note
  recognizer scars were all just "candidate-helper".
- The live support-kind board still exposed names with local packet vocabulary,
  even though those rows were deliberately still candidate-labeled.

Intervention:

- Added `transfer_signal` to `scripts/audit_helper_usage.py` candidate pruning
  targets:
  - `single_fixture_pressure`
  - `narrow_transfer_scar`
  - `transferred_candidate_pressure`
- Renamed local packet support kinds in `roster_state_support` to generic
  support names:
  - `document_policy_title`
  - `pending_document_item`
  - `adult_lodging_location`
  - `scheduled_transport_departure`
  - `temporary_assignment_source_record`
  - `device_clock_audit_status`
- Renamed the generator from source-record school packet support to operational
  packet support so new contexts do not inherit a fixture-shaped concept.

After:

```text
Six-fixture hosted QA5:
  exact / partial / miss: 29 / 1 / 0
  targeted q004 replay for the partial: 1 / 0 / 0
  runtime load errors: 0
  write proposal rows: 0
  helper rows: 120
  rows/exact: 4.138
  candidate share: 0.3000

Audit:
  source_record_packet_metadata_support fixture count: 3
  source-note rows: narrow_transfer_scar
  roster packet rows: single_fixture_pressure
  no school_packet_* support kinds remain in implementation or active tests

Local verification:
  tests/test_domain_bootstrap_qa.py: 118 passed
  tests/test_audit_helper_usage.py: 4 passed
  py_compile for run_domain_bootstrap_qa.py and audit_helper_usage.py: passed
```

Artifacts:

- `scripts/audit_helper_usage.py::candidate_transfer_signal`
- `scripts/run_domain_bootstrap_qa.py::_source_record_operational_packet_support`
- `tests/test_audit_helper_usage.py`
- `tests/test_domain_bootstrap_qa.py::test_roster_state_support_holds_operational_packet_content_notes_after_metadata_retirement`
- `tmp/openrouter_operational_packet_names_6fx_qa5_20260512/qa_batch_summary.md`
- `tmp/helper_usage_pressure_operational_packet_names_6fx_qa5_20260512.md`
- `tmp/openrouter_operational_packet_names_festival_q004_replay_20260512/`

Lesson:

Candidate-helper is not one substance. A candidate row seen only in one fixture
is architecture debt; a candidate row that transfers but remains prose-derived
is a scar awaiting proof; a broad transferred candidate row is substrate
pressure. The audit should name those states without letting any document's
local vocabulary become the name of the state. Renaming support kinds is not a
score hack; it is hygiene for future contexts.

### GG-043 - Retire Local Packet Recognizer, Keep Generic Retention Surface

Date: 2026-05-12

Scope: remove fixture-shaped roster packet recognizers while preserving a
fixture-free document-retention surface.

Trajectory:

```text
local operational packet recognizer had generic support-kind names but still
matched story-specific packet phrases
  -> remove the recognizer and stale roster triggers for source labels,
     attendance scans, and bus assignments; add only a generic
     retained-document physical-location parser
  -> targeted school q004 recovers exact, school QA5 stays exact, and
     six-fixture QA5 returns to 30 / 0 / 0 with helper rows 116
  -> next pressure is source-only group_count and document_retention_location
     transfer, not local packet reconstruction
```

Before:

- After GG-042, active support-kind names were generic, but the generator still
  matched local packet phrases for policy title, pending attendance scans,
  adult lodging, transport departure, observer permission, temporary assignment
  source, scanner-clock audit status, and retention location.
- Fully deleting that recognizer initially exposed the real retained-document
  need: school q004 missed and broad roster assignment rows reappeared.

Intervention:

- Removed `_source_record_operational_packet_support()` and its observer-scope
  helper entirely.
- Added `_source_record_document_retention_support()` as a generic parser for
  normalized rows shaped like:

```text
retained_in_the_<document>_location_<location>
... cabinet_<n>_drawer_<m>
```

- Removed stale roster-state triggers for predicates whose only roster support
  came from the retired local packet recognizer.
- Added local regression coverage so the old packet support kinds do not
  re-enter as active roster-state rows.

After:

```text
Targeted school q004:
  exact / partial / miss: 1 / 0 / 0

Focused school QA5:
  exact / partial / miss: 5 / 0 / 0
  helper rows: 71
  roster_state_support rows: 49

Six-fixture hosted QA5:
  exact / partial / miss: 30 / 0 / 0
  runtime load errors: 0
  write proposal rows: 0
  helper rows: 116
  rows/exact: 3.867
  candidate share: 0.2155

Final helper audit:
  roster_state_support rows: 25
  source_record_student_group_assignment candidate rows: 0
  document_retention_location candidate rows: 3 (1 unique)
```

Artifacts:

- `scripts/run_domain_bootstrap_qa.py::_source_record_document_retention_support`
- `tests/test_domain_bootstrap_qa.py::test_roster_state_support_does_not_promote_local_packet_content_notes`
- `tmp/openrouter_document_retention_generic_school_q004_20260512/`
- `tmp/openrouter_generic_retention_school_qa5_pruned_20260512/`
- `tmp/openrouter_generic_retention_pruned_6fx_qa5_20260512/qa_batch_summary.md`
- `tmp/helper_usage_pressure_generic_retention_pruned_6fx_qa5_20260512.md`

Lesson:

Generic names are necessary but not sufficient. A helper that recognizes local
packet prose is still local architecture even if its `SupportKind` looks clean.
The acceptable replacement is the smallest fixture-free shape that explains the
answer: retained document plus physical storage location. Everything else from
that packet remains in history until it earns transfer.

### GG-044 - First Guard Retirement From Count/Measure Replay

Date: 2026-05-12

Scope: retire one high-priority helper-pressure selector guard after birth and
unlike replay proved the generic count/measure principle.

Trajectory:

```text
deed item-count guard still matched the local phrase "supplementary deed" even
though generic conveyed-item scoring already covered the answer shape
  -> delete the phrase-specific selector guard, add a scar-ledger entry, and
     add a regression that the tempting phrase no longer triggers an override
  -> selector ledger compresses to 174 active guards, 12 helper-pressure
     guards, and 17 scars; selector/ledger suite passes 298 tests
  -> next pressure is the remaining count/measure guards with incomplete replay,
     especially attendance/session, adult-total, density, and scoped roster
```

Before:

- The high-priority helper-pressure board still counted `13` active guards.
- The conveyed-item guard was an active branch inside
  `structural_specialized_answer_surface_override()`, and it matched local
  question prose rather than a reusable evidence predicate contract.
- Birth and unlike tests already showed the generic count/measure scoring could
  select `conveyed_item` / `item_conveyed` enumeration rows over broad receipt
  or source-record volume.

Intervention:

- Removed the active local phrase guard:

```text
supplementary deed + how many distinct items -> conveys predicate override
```

- Recorded the retired reason as a scar in
  `scripts/summarize_selector_guard_families.py`.
- Added `test_deed_item_count_phrase_no_longer_has_selector_guard()` so the
  exact local phrase cannot quietly return as selector architecture.
- Regenerated selector guard rollups and ledger docs from the current code.

After:

```text
Selector ledger:
  active guards: 175 -> 174
  high-priority helper-pressure guards: 13 -> 12
  scar guards: 16 -> 17
  semantic families: 7
  unclassified reasons: 0

Local verification:
  conveyed-item focused tests + guard-family tests: 10 passed
  selector + guard-family suite: 298 passed
  public doc link domains: 1 passed

OpenRouter six-fixture QA5, cache disabled:
  exact / partial / miss: 30 / 0 / 0
  runtime load errors: 0
  write proposal rows: 0
  helper rows: 103
  rows/exact: 3.433
  candidate share: 0.2621

Helper audit:
  helpers observed: 6
  suspicious low-transfer helpers: 5
  orphaned artifact helpers: 0
  top single-fixture candidate pressures: group_count, document_retention_location
```

Artifacts:

- `scripts/select_qa_mode_without_oracle.py::structural_specialized_answer_surface_override`
- `scripts/summarize_selector_guard_families.py::RETIRED_SCAR_GUARDS`
- `tests/test_qa_mode_selector.py::test_deed_item_count_phrase_no_longer_has_selector_guard`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_conveyed_item_count_without_fixture_guard`
- `tests/test_qa_mode_selector.py::test_structural_selector_prefers_conveyed_item_count_on_unlike_row`
- `docs/SELECTOR_GUARD_FAMILY_ROLLUP.md`
- `docs/SELECTOR_GUARD_LEDGER.md`
- `tmp/openrouter_deed_guard_retire_6fx_qa5_20260512/qa_batch_summary.md`
- `tmp/helper_usage_pressure_deed_guard_retire_6fx_qa5_20260512.md`

Lesson:

A generic scoring principle only earns a retirement when it can carry both the
birth pressure and an unlike row without preserving the local phrase that first
made the guard useful. This retirement is small, but it is the right kind of
compression: the selector no longer knows about the document's local wording,
and the scar ledger keeps the cautionary history visible.

### GG-045 - Approval Count Guard Retirement

Date: 2026-05-12

Scope: retire a second high-priority helper-pressure guard from the same
count/measure scoring substrate.

Trajectory:

```text
approved-display count guard still matched fireworks/display wording even
though approval-validity scoring already covered the requested count surface
  -> remove the display-specific selector branch, scar the reason, and add a
     regression that the old fireworks wording no longer triggers an override
  -> selector ledger compresses to 173 active guards, 11 helper-pressure
     guards, and 18 scars; selector/ledger suite passes 299 tests
  -> next pressure is to retire only the remaining count/measure guards whose
     replacement has both birth and unlike replay, not just a local disabled run
```

Before:

- After GG-044, `approved-display count question needs approval/validity
  surface rather than broad current-status rows` was still an active
  `candidate_guard:helper_pressure` row.
- The live selector branch matched `fireworks`, `how many`, and `approved`.
  That made the fixture topic part of selector behavior.
- Existing replay already showed approval/validity count surfaces beating broad
  status rows on a birth-style display row and an unlike approved-permit row.

Intervention:

- Removed the active `fireworks` / `approved` selector branch from
  `structural_specialized_answer_surface_override()`.
- Added a scar-ledger entry for the retired guard with birth row `q020`.
- Removed the guard-disable crutch from
  `test_hybrid_selector_prefers_approval_validity_count_without_guard()`.
- Added `test_approved_fireworks_count_phrase_no_longer_has_selector_guard()`
  to keep the local phrase out of live selector architecture.

After:

```text
Selector ledger:
  active guards: 174 -> 173
  high-priority helper-pressure guards: 12 -> 11
  scar guards: 17 -> 18
  semantic families: 7
  unclassified reasons: 0

Local verification:
  approval focused tests + guard-family tests: 10 passed
  selector + guard-family suite: 299 passed

OpenRouter targeted birth row:
  festival q020 exact / partial / miss: 1 / 0 / 0
  runtime load errors: 0
  write proposal rows: 0

OpenRouter six-fixture QA5, cache disabled:
  exact / partial / miss: 23 / 0 / 4
  runtime load errors: 0
  write proposal rows: 0
  note: q001-q005 volatility is unrelated to the retired approval guard's q020
```

Artifacts:

- `scripts/select_qa_mode_without_oracle.py::structural_specialized_answer_surface_override`
- `scripts/summarize_selector_guard_families.py::RETIRED_SCAR_GUARDS`
- `tests/test_qa_mode_selector.py::test_approved_fireworks_count_phrase_no_longer_has_selector_guard`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_approval_validity_count_without_guard`
- `tests/test_qa_mode_selector.py::test_structural_selector_prefers_approval_validity_count_on_unlike_row`
- `docs/SELECTOR_GUARD_FAMILY_ROLLUP.md`
- `docs/SELECTOR_GUARD_LEDGER.md`
- `tmp/openrouter_approval_guard_retire_festival_q020_oracle_20260512/`
- `tmp/openrouter_approval_guard_retire_6fx_qa5_20260512/qa_batch_summary.md`
- `tmp/helper_usage_pressure_approval_guard_retire_6fx_qa5_20260512.md`

Lesson:

The count/measure principle is now doing repeatable retirement work, not just
adding scoring coverage. The important part is negative: the selector no longer
knows that this count happened to be about fireworks. It only knows that a
count question should prefer a compact approval/validity surface over broad
current-status history when that surface binds the measured approved set.

### GG-046 - Physical Inventory Count Guard Retirement

Date: 2026-05-12

Scope: retire a third count/measure helper-pressure guard after direct outcome
scoring proved it could replace title-volume protection.

Trajectory:

```text
physical inventory count guard still matched titles + physical count wording
even though incident/count outcome scoring already selected the measured surface
  -> remove the title-specific selector branch, scar the reason, and add a
     regression that the old physical-count wording no longer triggers override
  -> selector ledger compresses to 172 active guards, 10 helper-pressure
     guards, and 19 scars; selector/ledger suite passes 300 tests
  -> next pressure is density/numeric evaluation or threshold/action policy,
     where both birth and unlike replay already exist
```

Before:

- After GG-045, `physical inventory count question needs incident/count outcome
  surface rather than title-name rows` remained active.
- The guard protected the right surface, but it did so by matching the local
  title/physical-count wording.
- Existing replay showed `incident_outcome` / count-outcome predicates beating
  broad title or identity rows on the birth row and an unlike inventory row.

Intervention:

- Removed the active title/physical-count selector branch.
- Added a scar-ledger entry for the retired guard with birth row `q014`.
- Updated inventory replay tests so they no longer depend on disabled-guard
  bookkeeping.
- Added `test_physical_inventory_count_phrase_no_longer_has_selector_guard()`.

After:

```text
Selector ledger:
  active guards: 173 -> 172
  high-priority helper-pressure guards: 11 -> 10
  scar guards: 18 -> 19
  semantic families: 7
  unclassified reasons: 0

Local verification:
  inventory focused tests + guard-family tests: 11 passed
  selector + guard-family suite: 300 passed

OpenRouter targeted birth row:
  dream q014 exact / partial / miss: 1 / 0 / 0
  runtime load errors: 0
  write proposal rows: 0
```

Artifacts:

- `scripts/select_qa_mode_without_oracle.py::structural_specialized_answer_surface_override`
- `scripts/summarize_selector_guard_families.py::RETIRED_SCAR_GUARDS`
- `tests/test_qa_mode_selector.py::test_physical_inventory_count_phrase_no_longer_has_selector_guard`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_inventory_count_surface_over_title_names_without_guard`
- `tests/test_qa_mode_selector.py::test_structural_selector_prefers_inventory_outcome_count_over_identity_volume`
- `docs/SELECTOR_GUARD_FAMILY_ROLLUP.md`
- `docs/SELECTOR_GUARD_LEDGER.md`
- `tmp/openrouter_inventory_guard_retire_dream_q014_20260512/`

Lesson:

This is the same compression pattern as GG-044 and GG-045: the selector should
not know the answer was expressed as titles in a physical count. The reusable
principle is that a count question prefers a direct incident/count outcome over
broad identity enumeration unless the identity rows are themselves the measured
set.

### GG-047 - Density Measure Guard Retirement

Date: 2026-05-12

Scope: retire a density-specific baseline guard by folding direct
staff-evaluation rows into the generic measure-surface scoring contract.

Trajectory:

```text
density-calculation guard still kept a baseline staff_evaluation row over
source-opinion rows through a density-specific baseline guard
  -> treat direct staff_evaluation as a compact measure surface inside
     count/measure questions, delete the density guard, and scar the reason
  -> selector ledger compresses to 171 active guards, 9 helper-pressure guards,
     and 20 scars; selector/ledger suite passes 301 tests
  -> next pressure is threshold/action policy or remaining count-family rows
     that still lack unlike replay
```

Before:

- The density guard was less fixture-named than the previous retirements, but
  it still lived as a special baseline-protection branch.
- Unlike replay already proved `density_value` / `measurement_value` rows beat
  broad opinion volume.
- Birth replay needed the same principle to cover `staff_evaluation` without
  saying "density calculation" in a guard.

Intervention:

- Added direct `staff_evaluation` to `structural_count_measure_focus_bonus()`
  as a measure predicate, scoped by the existing count/measure question gate.
- Removed the density-specific baseline guard.
- Added a scar-ledger entry for the retired reason.
- Removed the disabled-guard dependency from the density birth replay.
- Added `test_density_calculation_phrase_no_longer_has_baseline_guard()`.

After:

```text
Selector ledger:
  active guards: 172 -> 171
  high-priority helper-pressure guards: 10 -> 9
  scar guards: 19 -> 20
  semantic families: 7
  unclassified reasons: 0

Local verification:
  density focused tests + guard-family tests: 10 passed
  selector + guard-family suite: 301 passed

Hosted note:
  attempted fresh OpenRouter compile for draft_within_draft timed out locally
  after about 7 minutes with no compile artifact; no hosted birth-row claim is
  made for this retirement yet
```

Artifacts:

- `scripts/select_qa_mode_without_oracle.py::structural_count_measure_focus_bonus`
- `scripts/select_qa_mode_without_oracle.py::structural_baseline_answer_surface_guard_reason`
- `scripts/summarize_selector_guard_families.py::RETIRED_SCAR_GUARDS`
- `tests/test_qa_mode_selector.py::test_density_calculation_phrase_no_longer_has_baseline_guard`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_density_staff_evaluation_surface_over_broad_claims`
- `tests/test_qa_mode_selector.py::test_structural_selector_prefers_numeric_density_value_on_unlike_row`
- `docs/SELECTOR_GUARD_FAMILY_ROLLUP.md`
- `docs/SELECTOR_GUARD_LEDGER.md`

Lesson:

Not every retireable guard is visibly contaminated by a fixture noun. Some are
architecture debt because they protect one answer shape in a bespoke branch
instead of letting a reusable scoring contract own the behavior. The safe
replacement here is not "Dr. Holm density"; it is direct measure evidence.

### GG-048 - Threshold/Action Policy Guard Retirement

Date: 2026-05-12

Scope: retire the failed-viability threshold/action guard after generic
counterfactual scoring covered the birth and unlike replay shapes.

Trajectory:

```text
failed-viability guard still matched germination/viability wording to choose a
threshold/action policy surface over note rows
  -> remove the viability-specific selector branch, scar the reason, and let
     generic counterfactual scoring prefer policy threshold/action predicates
  -> selector ledger compresses to 170 active guards, 8 helper-pressure guards,
     and 21 scars; selector/ledger suite passes 302 tests
  -> next pressure is no longer complete-replay count/measure retirement; it is
     adding unlike replay for attendance/session, scoped roster, and adult-total
```

Before:

- After GG-047, the threshold/action policy guard remained active even though
  it had both a birth replay and an unlike threshold-action replay.
- The live selector branch matched `fails viability testing` and `germination
  rate`, making seedbank scenario wording part of active selector behavior.
- Generic counterfactual scoring already rewarded direct
  `policy_condition_threshold`, `policy_minimum_storage`, `policy_action`, and
  `threshold_action` support.

Intervention:

- Removed the active viability-specific selector branch from
  `structural_specialized_answer_surface_override()`.
- Added a scar-ledger entry for the retired reason with birth row `q025`.
- Renamed the birth replay to
  `test_hybrid_selector_prefers_threshold_action_policy_without_guard()`.
- Added
  `test_failed_viability_threshold_action_phrase_no_longer_has_selector_guard()`.
- Updated the older policy-threshold test so it expects structural selection
  without `specialized_guard_reason`.

After:

```text
Selector ledger:
  active guards: 171 -> 170
  high-priority helper-pressure guards: 9 -> 8
  scar guards: 20 -> 21
  semantic families: 7
  unclassified reasons: 0

Local verification:
  threshold/action focused tests + guard-family tests: 10 passed
  selector + guard-family suite: 302 passed

Hosted note:
  no Fenmore compile artifact is present under tmp; no hosted birth-row claim is
  made for this retirement yet
```

Artifacts:

- `scripts/select_qa_mode_without_oracle.py::structural_specialized_answer_surface_override`
- `scripts/select_qa_mode_without_oracle.py::structural_question_focus_bonus`
- `scripts/summarize_selector_guard_families.py::RETIRED_SCAR_GUARDS`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_threshold_action_policy_without_guard`
- `tests/test_qa_mode_selector.py::test_structural_selector_prefers_threshold_action_policy_on_unlike_counterfactual`
- `tests/test_qa_mode_selector.py::test_failed_viability_threshold_action_phrase_no_longer_has_selector_guard`
- `docs/SELECTOR_GUARD_FAMILY_ROLLUP.md`
- `docs/SELECTOR_GUARD_LEDGER.md`

Lesson:

Counterfactual policy questions need rule-input surfaces, not story-specific
event words. The reusable architecture is threshold condition plus required
action; viability and germination are just one instance of that shape.

### GG-049 - Attendance Session Count Guard Retirement

Date: 2026-05-12

Scope: add unlike replay for attendance/session counts, then retire the active
attendance-count selector guard into scar history.

Trajectory:

```text
attendance-count guard still matched attended/attendance/session wording to
prefer session_attendance_count over broad interval roster rows
  -> add an unlike briefing-row replay, remove the attendance-specific selector
     branch, and let generic count/measure scoring carry session_attendance_count
  -> selector ledger compresses to 169 active guards, 7 helper-pressure guards,
     and 22 scars; selector/ledger suite passes 303 tests
  -> next pressure is scoped roster or adult-total, but only after unlike replay
     makes the population/scope distinction explicit
```

Before:

- The coverage board marked attendance/session as birth-only: explicit
  `session_attendance_count` beat interval roster volume, but there was no
  unlike session/count replay.
- The live selector branch still matched attendance/session wording and returned
  a specialized guard reason.

Intervention:

- Added an unlike row:

```text
How many people checked into the morning safety briefing?
participant roster volume -> direct session_attendance_count
```

- Removed the active attendance/session selector branch.
- Added a scar-ledger entry for the retired reason.
- Updated the birth replay so it no longer uses guard-disable scaffolding.
- Added `test_attendance_count_phrase_no_longer_has_selector_guard()`.

After:

```text
Selector ledger:
  active guards: 170 -> 169
  high-priority helper-pressure guards: 8 -> 7
  scar guards: 21 -> 22
  semantic families: 7
  unclassified reasons: 0

Local verification:
  attendance focused tests + guard-family tests: 10 passed
  selector + guard-family suite: 303 passed
```

Artifacts:

- `scripts/select_qa_mode_without_oracle.py::structural_specialized_answer_surface_override`
- `scripts/select_qa_mode_without_oracle.py::structural_count_measure_focus_bonus`
- `scripts/summarize_selector_guard_families.py::RETIRED_SCAR_GUARDS`
- `tests/test_qa_mode_selector.py::test_attendance_count_phrase_no_longer_has_selector_guard`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_explicit_session_count_without_guard`
- `tests/test_qa_mode_selector.py::test_structural_selector_prefers_session_count_on_unlike_briefing_row`
- `docs/SELECTOR_GUARD_FAMILY_ROLLUP.md`
- `docs/SELECTOR_GUARD_LEDGER.md`

Lesson:

The reusable surface is not "field-trip attendance"; it is a direct count for a
bounded session/event. Broad roster or interval membership remains weak count
evidence unless it exposes the measured session population directly.

### GG-050 - Scoped Roster Section Guard Retirement

Date: 2026-05-12

Scope: add unlike replay for scoped roster/section counts and retire the
source-record roster section guard.

Trajectory:

```text
scoped roster-count guard still matched roster/excluding wording to prefer
assignment_interval + source_section over badge/log volume
  -> add unlike training-roster replay, remove the scoped-roster selector
     branch, and let generic count/measure section scoring carry the behavior
  -> selector ledger compresses to 168 active guards, 6 helper-pressure guards,
     and 23 scars; selector/ledger suite passes 305 tests
  -> next pressure is adult-total versus subset count, where total/subset
     population semantics need one more unlike replay before retirement
```

Before:

- Scoped roster count had a birth replay with the guard disabled, but the
  coverage board still lacked unlike section-membership replay.
- The active selector branch matched roster/excluding wording and returned a
  specialized guard reason for `assignment_interval + source_section`.

Intervention:

- Added an unlike row:

```text
How many trainees are listed in the roster section, excluding sign-in-only entries?
activity/sign-in volume -> assignment_interval + source_section
```

- Removed the active scoped-roster selector branch.
- Added a scar-ledger entry for the retired reason.
- Removed guard-disable scaffolding from the birth replay.
- Added `test_scoped_roster_count_phrase_no_longer_has_selector_guard()`.

After:

```text
Selector ledger:
  active guards: 169 -> 168
  high-priority helper-pressure guards: 7 -> 6
  scar guards: 22 -> 23
  semantic families: 7
  unclassified reasons: 0

Local verification:
  scoped-roster focused tests + guard-family tests: 10 passed
  selector + guard-family suite: 305 passed
```

Artifacts:

- `scripts/select_qa_mode_without_oracle.py::structural_specialized_answer_surface_override`
- `scripts/select_qa_mode_without_oracle.py::structural_count_measure_focus_bonus`
- `scripts/summarize_selector_guard_families.py::RETIRED_SCAR_GUARDS`
- `tests/test_qa_mode_selector.py::test_scoped_roster_count_phrase_no_longer_has_selector_guard`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_scoped_roster_section_surface_without_guard`
- `tests/test_qa_mode_selector.py::test_structural_selector_prefers_section_membership_count_on_unlike_training_roster`
- `docs/SELECTOR_GUARD_FAMILY_ROLLUP.md`
- `docs/SELECTOR_GUARD_LEDGER.md`

Lesson:

The reusable rule is section-scoped population evidence, not a school roster
memory. Activity logs prove participation; they do not define the scoped
population unless they expose the membership/count contract directly.

### GG-051 - Adult Total/Subcount Guard Retirement

Date: 2026-05-12

Scope: retire the adult-total roster guard after total/subset population
semantics were covered by generic count/measure scoring.

Trajectory:

```text
adult-total guard still matched adults total/accompanying wording to prefer
adult_manifest_total over qualifying-chaperone subset counts
  -> remove the adult-specific selector branch, scar the reason, and keep the
     total/subset replay tests as the architectural proof
  -> selector ledger compresses to 167 active guards, 5 helper-pressure guards,
     and 24 scars; selector/ledger suite passes 306 tests
  -> next pressure shifts out of count-family cleanup and into rule/scope guards
     that need transfer evidence before retirement
```

Before:

- Adult-total was the last active count-family helper-pressure guard with local
  birth replay and total/subset transfer tests.
- The active selector branch matched adult trip wording and looked for
  `adult_manifest_total` / `ratio_counted_adults` support kinds.
- Generic count/measure scoring already demoted unasked subset counts when the
  question asks for a total population.

Intervention:

- Removed the active adult-total selector branch.
- Added a scar-ledger entry for the retired reason.
- Removed guard-disable scaffolding from the adult-manifest birth replay.
- Added `test_adult_total_roster_phrase_no_longer_has_selector_guard()`.
- Kept the unlike total/subset application tests as the transfer evidence.

After:

```text
Selector ledger:
  active guards: 168 -> 167
  high-priority helper-pressure guards: 6 -> 5
  scar guards: 23 -> 24
  semantic families: 7
  unclassified reasons: 0

Local verification:
  adult-total focused tests + guard-family tests: 11 passed
  selector + guard-family suite: 306 passed
```

Artifacts:

- `scripts/select_qa_mode_without_oracle.py::structural_specialized_answer_surface_override`
- `scripts/select_qa_mode_without_oracle.py::structural_count_measure_focus_bonus`
- `scripts/summarize_selector_guard_families.py::RETIRED_SCAR_GUARDS`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_adult_manifest_total_without_guard`
- `tests/test_qa_mode_selector.py::test_adult_total_roster_phrase_no_longer_has_selector_guard`
- `tests/test_qa_mode_selector.py::test_structural_selector_prefers_total_count_over_unasked_subset_count`
- `tests/test_qa_mode_selector.py::test_structural_selector_allows_subset_count_when_subset_is_requested`
- `docs/SELECTOR_GUARD_FAMILY_ROLLUP.md`
- `docs/SELECTOR_GUARD_LEDGER.md`

Lesson:

This is total-population architecture, not an adult/chaperone shortcut. When a
question asks for the total population, subset-count surfaces are weak unless
the subset is explicitly requested.

### GG-052 - Scoped Status Count Guard Retirement

Date: 2026-05-12

Scope: retire the split-lot never-quarantined guard by generalizing to negative
scoped-status counts, while preventing overgeneralization to movement counts.

Trajectory:

```text
split-lot guard still matched plants/lot/never-quarantined wording to prefer
quarantine_scope over broad lot-status history
  -> add a generic negative/exclusion scoped-status count bonus, add an unlike
     restriction-scope replay, and retire the split-lot selector branch
  -> initial broad scope bonus overgeneralized to placed-under-quarantine
     movement counts; focused replay caught it and narrowed the bonus
  -> selector ledger compresses to 166 active guards, 4 helper-pressure guards,
     and 25 scars; selector/ledger suite passes 308 tests
```

Before:

- The split-lot guard was active because broad `lot_status` history could beat
  a scoped answer surface for "never quarantined" counts.
- Existing birth replay showed quarantine scope could win with the guard
  disabled, but there was no unlike scoped-status replay outside quarantine.

Intervention:

- Added a count/measure bonus for direct scoped-status predicates only when the
  question asks a negative or exclusion count (`never`, `without`, `excluding`,
  and related wording).
- Added an unlike restriction-scope row:

```text
How many Unit 4 devices were never restricted?
status history -> restriction_scope
```

- Removed the active split-lot selector branch and the older
  `plants`/`lot`/`never quarantined` focus-bonus branch.
- Added a scar-ledger entry for the retired reason.
- Added `test_split_lot_never_quarantined_phrase_no_longer_has_selector_guard()`.

After:

```text
Selector ledger:
  active guards: 167 -> 166
  high-priority helper-pressure guards: 5 -> 4
  scar guards: 24 -> 25
  semantic families: 7
  unclassified reasons: 0

Local verification:
  scoped-status focused tests + guard-family tests: 12 passed
  regression for placed-under-quarantine movement count: passed
  selector + guard-family suite: 308 passed
  public doc-link check: 1 passed

Hosted verification:
  OpenRouter six-lane no-cache QA5: 30 / 0 / 0
  runtime load errors: 0
  write proposal rows: 0
  helper pressure: 108 rows, 3.6 rows/exact, bounded_helper_surface
```

Artifacts:

- `scripts/select_qa_mode_without_oracle.py::structural_count_measure_focus_bonus`
- `scripts/select_qa_mode_without_oracle.py::structural_specialized_answer_surface_override`
- `scripts/summarize_selector_guard_families.py::RETIRED_SCAR_GUARDS`
- `tests/test_qa_mode_selector.py::test_split_lot_never_quarantined_phrase_no_longer_has_selector_guard`
- `tests/test_qa_mode_selector.py::test_structural_selector_prefers_scoped_status_count_on_unlike_restriction_row`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_mistaken_movement_quarantine_count_without_guard`
- `docs/SELECTOR_GUARD_FAMILY_ROLLUP.md`
- `docs/SELECTOR_GUARD_LEDGER.md`
- `tmp/openrouter_scoped_status_retirement_qa5_openrouter_20260512/summary.md`

Lesson:

Scoped-status evidence is only the right abstraction for negative/exclusion
membership counts. It must not swallow event or movement counts just because a
scope predicate is present. The regression that failed during this slice is the
useful science: it marked the boundary between set membership and event action.

### GG-053 - Post-Change Membership Count Guard Retirement

Date: 2026-05-12

Scope: retire the post-reassignment group-count guard by generalizing to
post-change membership-count evidence.

Trajectory:

```text
post-reassignment guard still matched local group/student/reassignment wording
to prefer membership rows over role-task volume
  -> add a generic count/measure scoring rule for post-change membership/event
     evidence, add birth and unlike roster replays, and retire the local branch
  -> selector ledger compresses to 165 active guards, 3 helper-pressure guards,
     and 26 scars; selector/ledger suite passes 311 tests
  -> remaining helper-pressure is now entirely rule-activation/status arithmetic
```

Before:

- The guard branch matched local wording for a specific school group count.
- Prior roster work had already made `group_count` and assignment support more
  compact, but this selector branch still treated one fixture phrase as policy.

Intervention:

- Added generic post-change membership-count scoring:

```text
count question + after/following/post/reassignment/change wording
  + direct membership/event/count evidence
  -> prefer that surface over broad role/task rows
```

- Removed the active post-reassignment selector branch.
- Added a no-guard birth replay for the school-style row.
- Added an unlike replay:

```text
How many trainees were in Cohort B following the afternoon reassignment?
role_tasks -> membership_change
```

After:

```text
Selector ledger:
  active guards: 166 -> 165
  high-priority helper-pressure guards: 4 -> 3
  scar guards: 25 -> 26
  semantic families: 7
  unclassified reasons: 0

Local verification:
  post-change focused tests: 4 passed
  selector + guard-family suite: 311 passed
  public doc-link check: 1 passed

Hosted verification:
  OpenRouter six-lane no-cache QA5: 30 / 0 / 0
  runtime load errors: 0
  write proposal rows: 0
  helper pressure: 107 rows, 3.567 rows/exact, bounded_helper_surface
```

Artifacts:

- `scripts/select_qa_mode_without_oracle.py::structural_count_measure_focus_bonus`
- `scripts/select_qa_mode_without_oracle.py::structural_specialized_answer_surface_override`
- `scripts/summarize_selector_guard_families.py::RETIRED_SCAR_GUARDS`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_post_change_membership_count_without_guard`
- `tests/test_qa_mode_selector.py::test_post_reassignment_group_count_phrase_no_longer_has_selector_guard`
- `tests/test_qa_mode_selector.py::test_structural_selector_prefers_post_change_membership_count_on_unlike_roster`
- `docs/SELECTOR_GUARD_FAMILY_ROLLUP.md`
- `docs/SELECTOR_GUARD_LEDGER.md`
- `tmp/openrouter_post_change_membership_qa5_openrouter_20260512/summary.md`

Lesson:

The architecture is not "Green Group" or even "school roster." It is a
post-change population-count contract: when a count question is scoped by a
change event, prefer evidence that binds membership and the change context over
rows that merely describe roles or tasks near the same story interval.

### GG-054 - Counterfactual Arithmetic Inputs Guard Retirement

Date: 2026-05-12

Scope: retire the reserve-status sibling guards by generalizing them into the
counterfactual arithmetic-input scoring contract.

Trajectory:

```text
two reserve-status guards still matched local hypothetical reserve wording to
keep reserve balance, minimum policy, and authorized spending inputs over
derived status rows
  -> add those predicates to the generic counterfactual support set, add
     birth/no-guard and unlike counterfactual-status replay, and retire both
     reserve-status branches
  -> selector ledger compresses to 163 active guards, 1 helper-pressure guard,
     and 28 scars; selector/ledger suite passes 314 tests
  -> only the amendment-recall authority guard remains in the high-priority
     helper-pressure lane
```

Before:

- Two active guards protected the same substrate principle with different
  wording: derived rule status is weaker than the explicit arithmetic inputs
  needed to answer a counterfactual status question.
- The branch matched `reserve status` text and a local predicate trio instead
  of using the existing counterfactual scoring substrate.

Intervention:

- Added `reserve_balance`, `minimum_reserve_policy`, and
  `expenditure_authorized` to the generic counterfactual support predicate set.
- Removed both active reserve-status selector branches.
- Added birth/no-guard replay for the reserve-status question shape.
- Added unlike replay:

```text
If the facility upgrade were authorized, what would happen to the compliance status?
derived_status -> arithmetic_inputs
```

After:

```text
Selector ledger:
  active guards: 165 -> 163
  high-priority helper-pressure guards: 3 -> 1
  scar guards: 26 -> 28
  semantic families: 7
  unclassified reasons: 0

Local verification:
  reserve/counterfactual focused tests: 5 passed
  selector + guard-family suite: 314 passed
  public doc-link check: 1 passed

Hosted verification:
  OpenRouter six-lane no-cache QA5: 30 / 0 / 0
  runtime load errors: 0
  write proposal rows: 0
  helper pressure: 119 rows, 3.967 rows/exact, bounded_helper_surface
```

Artifacts:

- `scripts/select_qa_mode_without_oracle.py::structural_question_focus_bonus`
- `scripts/select_qa_mode_without_oracle.py::structural_specialized_answer_surface_override`
- `scripts/summarize_selector_guard_families.py::RETIRED_SCAR_GUARDS`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_keeps_reserve_arithmetic_inputs_without_guard`
- `tests/test_qa_mode_selector.py::test_reserve_status_phrase_no_longer_has_selector_guard`
- `tests/test_qa_mode_selector.py::test_structural_selector_prefers_arithmetic_inputs_on_unlike_counterfactual_status`
- `docs/SELECTOR_GUARD_FAMILY_ROLLUP.md`
- `docs/SELECTOR_GUARD_LEDGER.md`
- `tmp/openrouter_reserve_arithmetic_qa5_openrouter_20260512/summary.md`

Lesson:

This is counterfactual arithmetic architecture, not reserve vocabulary. When a
question asks what would happen under a hypothetical, derived status rows are
often a lossy answer surface unless they expose the operands. The reusable
principle is to prefer the rule inputs needed to recompute the outcome.

### GG-055 - Authority/Action Guard Retirement

Date: 2026-05-12

Scope: retire the final high-priority helper-pressure guard by generalizing
amendment recall into authority/action scoring.

Trajectory:

```text
amendment-recall guard still matched recall plus local amendment wording to
prefer rule/threshold/action context over legal-opinion rows
  -> add generic authority/action scoring for governing-rule plus action-context
     surfaces, add birth/no-guard and unlike reversal replay, and retire the
     local amendment-recall branch
  -> selector ledger compresses to 162 active guards, 0 helper-pressure guards,
     and 29 scars; selector/ledger suite passes 317 tests
  -> the high-priority helper-pressure lane is closed
```

Before:

- The final high-priority helper-pressure guard used local recall/amendment
  wording as the selector trigger.
- The architecture principle was broader: legal-opinion or threshold-only rows
  are weaker than evidence binding governing rule, threshold, action, and
  context.

Intervention:

- Added generic authority/action scoring:

```text
authority/action/reversal question
  + governing rule or threshold evidence
  + action/reversal/context evidence
  - legal_opinion-only surface
  -> prefer the authority/action surface
```

- Removed the active amendment-recall selector branch.
- Added birth/no-guard replay for recall authority.
- Added unlike replay:

```text
What is required to reverse the access decision after emergency action?
legal_opinion -> action_authority
```

After:

```text
Selector ledger:
  active guards: 163 -> 162
  high-priority helper-pressure guards: 1 -> 0
  scar guards: 28 -> 29
  semantic families: 7
  unclassified reasons: 0

Local verification:
  authority/action focused tests: 5 passed
  selector + guard-family suite: 317 passed
  public doc-link check: 1 passed

Hosted verification:
  OpenRouter six-lane no-cache QA5: 30 / 0 / 0
  runtime load errors: 0
  write proposal rows: 0
  helper pressure: 126 rows, 4.2 rows/exact, bounded_helper_surface
```

Artifacts:

- `scripts/select_qa_mode_without_oracle.py::structural_question_focus_bonus`
- `scripts/select_qa_mode_without_oracle.py::structural_specialized_answer_surface_override`
- `scripts/summarize_selector_guard_families.py::RETIRED_SCAR_GUARDS`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_recall_authority_surface_without_guard`
- `tests/test_qa_mode_selector.py::test_amendment_recall_phrase_no_longer_has_selector_guard`
- `tests/test_qa_mode_selector.py::test_structural_selector_prefers_authority_action_surface_on_unlike_reversal`
- `docs/SELECTOR_GUARD_FAMILY_ROLLUP.md`
- `docs/SELECTOR_GUARD_LEDGER.md`
- `tmp/openrouter_authority_action_qa5_openrouter_20260512/summary.md`

Lesson:

Authority/action architecture is not amendment recall. It is the rule that a
question about who can act, what can be reversed, or what is required should
prefer evidence binding the governing rule or threshold to the action context.
Legal-opinion rows can summarize a conclusion, but they are not the substrate
when the rule-action contract is available.

### GG-056 - Calculated Deadline Guard Pair Retirement

Date: 2026-05-12

Scope: retire two high-priority singleton guards by generalizing them into a
calculated-deadline scoring contract.

Trajectory:

```text
deadline-filing and board-review guards still matched local deadline wording to
prefer calculated deadline rows over loose deadline values
  -> add generic deadline scoring that requires a calculated deadline plus a
     trigger event and rule/elapsed-day evidence, add birth/no-guard and unlike
     review-period replay, and retire both local branches
  -> selector ledger compresses to 160 active guards and 31 scars; selector/
     ledger suite passes 320 tests
  -> high-priority singleton debt compresses from 6 to 4 remaining guards
```

Before:

- Two active guards protected the same principle with local text triggers:
  filing timeliness and board review period.
- Loose deadline values could outrank the surface that actually binds trigger,
  rule, elapsed interval, and calculated result.

Intervention:

- Added generic calculated-deadline scoring:

```text
deadline/timeliness/review-period question
  + deadline_calculated
  + trigger event
  + rule text, deadline rule, requirement, threshold, or elapsed-days evidence
  -> prefer calculated deadline surface
```

- Removed both active deadline selector branches.
- Added no-guard replay for filing timeliness and board-review wording.
- Added unlike replay:

```text
When does the equipment review period end after the notice was issued?
loose_deadline -> calculated_deadline
```

After:

```text
Selector ledger:
  active guards: 162 -> 160
  high-priority candidate guards: 6 -> 4
  scar guards: 29 -> 31
  semantic families: 7
  unclassified reasons: 0

Local verification:
  calculated-deadline focused tests: 5 passed
  selector + guard-family suite: 320 passed
  public doc-link check: 1 passed

Hosted verification:
  OpenRouter six-lane no-cache QA5: 30 / 0 / 0
  runtime load errors: 0
  write proposal rows: 0
  helper pressure: 133 rows, 4.433 rows/exact, bounded_helper_surface
```

Artifacts:

- `scripts/select_qa_mode_without_oracle.py::structural_question_focus_bonus`
- `scripts/select_qa_mode_without_oracle.py::structural_specialized_answer_surface_override`
- `scripts/summarize_selector_guard_families.py::RETIRED_SCAR_GUARDS`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_calculated_deadline_filing_without_guard`
- `tests/test_qa_mode_selector.py::test_board_review_deadline_phrase_no_longer_has_selector_guard`
- `tests/test_qa_mode_selector.py::test_structural_selector_prefers_calculated_deadline_on_unlike_review_period`
- `docs/SELECTOR_GUARD_FAMILY_ROLLUP.md`
- `docs/SELECTOR_GUARD_LEDGER.md`
- `tmp/openrouter_calculated_deadline_qa5_openrouter_20260512/summary.md`

Lesson:

Calculated-deadline architecture is not filing or board-review vocabulary. A
deadline answer is reusable when it binds the triggering event, the governing
rule or elapsed interval, and the computed deadline in one surface. A loose
deadline value is weaker because it can detach the answer from the clock that
made it true.

### GG-057 - Appeal Event/Deadline Guard Pair Retirement

Date: 2026-05-12

Scope: retire the appeal-status and appeal-tolling singleton guards by
generalizing them into an appeal event/context scoring contract.

Trajectory:

```text
appeal-status and appeal-tolling guards still matched appeal/status/tolling
wording to prefer event-plus-context rows over bare docket or tolling labels
  -> add generic appeal event/context scoring, add birth/no-guard and unlike
     appeal-status replay, and retire both local branches
  -> selector ledger compresses to 158 active guards and 33 scars; selector/
     ledger suite passes 323 tests
  -> high-priority singleton debt compresses from 4 to 2 remaining guards
```

Before:

- Two active guards protected the same shape with separate prose triggers:
  appeal docket status and appeal tolling effect.
- Bare docket-status or tolling-label rows could look structurally sufficient
  even when the answer needed the appeal filing/event plus deadline, rule,
  no-decision, pending-decision, or clock context.

Intervention:

- Added generic appeal event/context scoring:

```text
appeal status/tolling/clock/deadline question
  + appeal filing or event evidence
  + deadline, rule, no-decision, pending-decision, or clock context
  -> prefer appeal event/context surface
```

- Removed both active appeal selector branches.
- Added no-guard replay for appeal docket-status and tolling wording.
- Added unlike replay:

```text
Is the permit appeal still pending after the review deadline?
docket_status -> appeal_deadline_context
```

After:

```text
Selector ledger:
  active guards: 160 -> 158
  high-priority candidate guards: 4 -> 2
  scar guards: 31 -> 33
  semantic families: 7
  unclassified reasons: 0

Local verification:
  selector + guard-family suite: 323 passed
  public doc-link check: 1 passed

Hosted verification:
  OpenRouter six-lane no-cache QA5: 30 / 0 / 0
  runtime load errors: 0
  write proposal rows: 0
  helper pressure: 170 rows, 5.667 rows/exact, bounded_helper_surface
```

Artifacts:

- `scripts/select_qa_mode_without_oracle.py::structural_question_focus_bonus`
- `scripts/select_qa_mode_without_oracle.py::structural_specialized_answer_surface_override`
- `scripts/summarize_selector_guard_families.py::RETIRED_SCAR_GUARDS`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_appeal_deadline_status_without_guard`
- `tests/test_qa_mode_selector.py::test_appeal_tolling_phrase_no_longer_has_selector_guard`
- `tests/test_qa_mode_selector.py::test_structural_selector_prefers_appeal_event_deadline_on_unlike_review_status`
- `docs/SELECTOR_GUARD_FAMILY_ROLLUP.md`
- `docs/SELECTOR_GUARD_LEDGER.md`
- `tmp/openrouter_appeal_deadline_qa5_openrouter_20260512/summary.md`

Lesson:

Appeal architecture is not docket-status or tolling vocabulary. It is the
surface contract that an appeal answer should bind the appeal event to the
rule, deadline, no-decision, pending-decision, or clock context that makes the
status true. A bare status label is weaker because it can name the docket
without carrying the reason the answer follows.

### GG-058 - Final High-Priority Singleton Guard Retirement

Date: 2026-05-12

Scope: retire the last two high-priority singleton guards by generalizing
duration and membership-transition evidence binding.

Trajectory:

```text
second-violation duration and yellow-to-blue reassignment guards still matched
local wording to protect event+interval and transition+membership surfaces
  -> add generic duration event/interval scoring and membership-transition
     scoring, add no-guard and unlike replay for both, and retire both branches
  -> selector ledger compresses to 156 active guards and 35 scars; selector/
     ledger suite passes 327 tests
  -> high-priority singleton debt compresses from 2 to 0 remaining guards
```

Before:

- The duration guard protected the reusable shape "event record plus resulting
  interval" but named a local violation story.
- The reassignment guard protected the reusable shape "transition event plus
  membership evidence" but named local group colors.
- The first-slice ledger view disappeared when the high-priority queue emptied,
  hiding the fact that the board was closed rather than missing.

Intervention:

- Added generic duration scoring:

```text
duration/how-long question
  + event, infraction, incident, or violation record
  + resulting active/restriction/suspension interval
  -> prefer event-bound duration surface
```

- Added generic membership-transition scoring:

```text
membership/assignment/roster transition question
  + transition, reassignment, or swap event
  + membership or assignment evidence
  -> prefer transition-bound membership surface
```

- Removed both active selector branches.
- Kept count questions out of the transition rule so post-change count scoring
  remains the owner of count-bearing reassignment questions.
- Made the ledger render "First Retirement Slices" even when the current
  high-priority queue is empty.

After:

```text
Selector ledger:
  active guards: 158 -> 156
  high-priority singleton guards: 2 -> 0
  scar guards: 33 -> 35
  semantic families: 7
  unclassified reasons: 0

Local verification:
  selector + guard-family suite: 327 passed
  public doc-link check: 1 passed

Hosted verification:
  OpenRouter six-lane no-cache QA5: 29 / 0 / 1
  runtime load errors: 0
  write proposal rows: 0
  helper pressure: 149 rows, 5.138 rows/exact, bounded_helper_surface
  miss: school q001 had an empty query list for packet compiler
```

Artifacts:

- `scripts/select_qa_mode_without_oracle.py::structural_question_focus_bonus`
- `scripts/select_qa_mode_without_oracle.py::structural_specialized_answer_surface_override`
- `scripts/summarize_selector_guard_families.py::RETIRED_SCAR_GUARDS`
- `scripts/summarize_selector_guard_families.py::render_guard_ledger_markdown`
- `tests/test_qa_mode_selector.py::test_second_violation_duration_phrase_no_longer_has_selector_guard`
- `tests/test_qa_mode_selector.py::test_structural_selector_prefers_event_record_duration_on_unlike_interval_row`
- `tests/test_qa_mode_selector.py::test_yellow_to_blue_phrase_no_longer_has_selector_guard`
- `tests/test_qa_mode_selector.py::test_structural_selector_prefers_membership_transition_on_unlike_roster_row`
- `docs/SELECTOR_GUARD_FAMILY_ROLLUP.md`
- `docs/SELECTOR_GUARD_LEDGER.md`
- `tmp/openrouter_final_singleton_qa5_openrouter_20260512/summary.md`

Lesson:

A final singleton guard can close only when its replacement can be named
without the fixture's nouns. Duration questions need an event record tied to
the interval whose length is being asked for. Membership-transition questions
need the transition event tied to the membership surface. The hosted miss is a
separate query-planning pressure: an empty compiler query list, not evidence
that the retired guards were doing architecture.

### GG-059 - Hosted Transport Retry Resilience

Date: 2026-05-12

Scope: repair the final-singleton hosted miss without changing query semantics
or rehydrating a guard.

Trajectory:

```text
final-singleton QA5 showed one school q001 miss with empty queries
  -> inspect row and find OpenRouter provider HTTP 503 during Semantic IR query
     generation, add transient retry handling to hosted structured calls, and
     replay q001 plus six-fixture QA5
  -> q001 emits document_metadata(... compiled_by, X) and judges exact; fresh
     six-lane QA5 returns 30 / 0 / 0 with 117 helper rows
  -> next pressure moves away from guard retirement toward medium-priority
     families and hosted query-plan variance
```

Before:

- School q001 in the final-singleton hosted run was classified as a
  `query_surface_gap`, but the row carried an `HTTP 503` provider overload from
  OpenRouter and no emitted queries.
- The compiled KB already contained direct support:
  `document_metadata(..., compiled_by, d_auerbach)` plus the source-record
  compiled line.

Intervention:

- Added transient retry handling for OpenAI-compatible structured calls in:
  - `src/semantic_ir.py` for Semantic IR query generation;
  - `scripts/run_domain_bootstrap_qa.py` for evidence-plan, judge, and failure
    classifier calls.
- Retry is limited to transient hosted/provider failures such as 408, 429,
  500, 502, 503, and 504 when the base URL is OpenRouter.
- Added a unit test that simulates a 503 and verifies the call retries before
  failing the row.

After:

```text
Local verification:
  QA runner + batch tests: 122 passed
  selector + guard-family + doc-link checks: 328 passed

Targeted hosted verification:
  school q001 OpenRouter no-cache replay: 1 / 0 / 0
  emitted query: document_metadata(chms_rso_2026_t07, compiled_by, X).

Hosted verification:
  OpenRouter six-lane no-cache QA5: 30 / 0 / 0
  runtime load errors: 0
  write proposal rows: 0
  helper pressure: 117 rows, 3.9 rows/exact, bounded_helper_surface
```

Artifacts:

- `src/semantic_ir.py::_urlopen_json_with_transient_retries`
- `scripts/run_domain_bootstrap_qa.py::_urlopen_json_with_transient_retries`
- `tests/test_domain_bootstrap_qa.py::test_openrouter_transient_http_errors_retry_before_row_failure`
- `tmp/openrouter_q001_retry_probe_20260512_oracle/`
- `tmp/openrouter_transport_retry_qa5_openrouter_20260512/summary.md`

Lesson:

Hosted variance is not architecture debt unless it changes what the system
believes. A provider overload should not become a false query-surface lesson,
and it should not invite a fixture-specific query patch. The right repair is
transport resilience around already-governed structured calls, with the row
still answered only from the compiled KB.

### GG-060 - Direct Identity Role Surface Scoring

Date: 2026-05-12

Scope: medium-priority `entity_role_authority` guard compression.

Trajectory:

```text
six medium identity guards still depended on literal question phrases such as
collector/director/driver/scorer/official/superlative identity
  -> replace phrase guards with generic direct identity-role focus scoring that
     rewards compact role, collector, service-role, driver, age, and
     name+authority predicate binding
  -> active guards compress 156 -> 150 and scar guards rise 35 -> 41 while
     local verification and six-lane hosted QA5 stay exact
  -> next pressure is the remaining entity-role family: source-record authority,
     roster/current-member authority, station supervision, and actor/provenance
     handoff guards
```

Before:

- `entity_role_authority` still had medium-priority single-phrase guards for
  collector identity, event/director identity, official role authority,
  role/driver identity, compact service-role identity, and superlative
  age/identity.
- The tempting bad move was to keep adding phrases. The fixture-free target was
  narrower: identity questions should prefer compact rows that bind the asked
  person/role/authority/age predicate directly, without promoting every nearby
  `person_role` row.

Intervention:

- Added a generic identity focus slice in
  `scripts/select_qa_mode_without_oracle.py::structural_question_focus_bonus`.
- The rule rewards:
  - direct collector / driver / service-role predicates;
  - compact title-bearing `person_role` rows for direct role identity
    questions;
  - direct `person_name`/`name` plus authority predicates for official identity;
  - direct age/identity predicates for youngest/oldest identity questions.
- The rule deliberately does not reward bare `person_role` for applicant or
  panel-chair questions, and it does not reward bare action authority rows
  without a bound identity name.
- Removed six literal identity branches from
  `structural_specialized_answer_surface_override` and moved their reasons to
  scar history.

After:

```text
Selector ledger:
  active guards: 156 -> 150
  medium-priority entity_role_authority guards: 29 -> 23
  scar guards: 35 -> 41
  semantic families: 7
  unclassified reasons: 0

Local verification:
  focused selector suite: 326 passed
  guard-family + public doc-link checks: 8 passed
  broader local QA/selector/doc-link suite: 456 passed

Hosted verification:
  OpenRouter six-lane no-cache QA5: 30 / 0 / 0
  runtime load errors: 0
  write proposal rows: 0
  helper pressure: 106 rows, 3.533 rows/exact, bounded_helper_surface
```

Artifacts:

- `scripts/select_qa_mode_without_oracle.py::structural_question_focus_bonus`
- `scripts/select_qa_mode_without_oracle.py::structural_specialized_answer_surface_override`
- `scripts/summarize_selector_guard_families.py::RETIRED_SCAR_GUARDS`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_direct_collector_identity_without_guard`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_direct_role_identity_without_guard`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_role_authority_identity_without_guard`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_direct_driver_identity_without_guard`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_compact_service_role_identity_without_guard`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_superlative_age_identity_without_guard`
- `docs/SELECTOR_GUARD_FAMILY_ROLLUP.md`
- `docs/SELECTOR_GUARD_LEDGER.md`
- `tmp/openrouter_identity_role_qa5_openrouter_20260512/summary.md`

Lesson:

This is entity-role architecture, not a bundle of identity phrase patches. The
replacement principle is: for identity questions, reward compact answer
surfaces that bind the asked identity, role, authority, service function, or
age measure in the same evidence row; do not reward broad action, meeting,
status, roster, or title-only rows merely because they contain a person-shaped
predicate. The failed first draft of this slice was useful: it showed that
generic names are still too broad unless the rule preserves source/list
authority cases such as applicant and panel-chair identity.

### GG-061 - Actor Event And Provenance Surface Scoring

Date: 2026-05-12

Scope: next medium/low `entity_role_authority` actor-provenance compression.

Trajectory:

```text
six remaining entity-role guards still selected actor/event or actor/provenance
surfaces by local question phrase
  -> extend the generic focus scorer to prefer direct station-supervisor,
     role+event supervision, testimony actor, certification-status, and
     received-from/handoff provenance surfaces
  -> active guards compress 150 -> 144; scar guards rise 41 -> 47; local and
     hosted six-lane QA5 remain exact
  -> next pressure is the harder entity-role residue: source-record authority,
     current roster authority, same-name distinction, and contract/guardianship
     authority surfaces
```

Before:

- The selector still carried literal actor/provenance branches for station
  supervisor, destruction supervisor, recovery identity, surveyor certification
  lapse, and two intake-actor handoff/provenance cases.
- These were smaller than the previous direct-identity slice, but still risky:
  a guard named after a fixture action can quietly make local row vocabulary
  look like architecture.

Intervention:

- Added generic actor/provenance scoring in
  `scripts/select_qa_mode_without_oracle.py::structural_question_focus_bonus`.
- The scoring principle rewards surfaces that bind:
  - direct station-supervisor predicates for who-supervised station questions;
  - a person/role predicate together with the supervised event surface;
  - direct testimony actor rows over adjacent custody/location rows;
  - direct certification-status rows for lapse/expiration questions;
  - direct received-from or ledger+location+event handoff rows for intake
    actor questions.
- Removed six literal branches from
  `structural_specialized_answer_surface_override` and preserved them as scars.

After:

```text
Selector ledger:
  active guards: 150 -> 144
  entity_role_authority active guards: 23 -> 17
  scar guards: 41 -> 47
  semantic families: 7
  unclassified reasons: 0

Local verification:
  focused selector suite: 328 passed
  broader local QA/selector/doc-link suite: 458 passed

Hosted verification:
  OpenRouter six-lane no-cache QA5: 30 / 0 / 0
  runtime load errors: 0
  write proposal rows: 0
  helper pressure: 91 rows, 3.033 rows/exact, bounded_helper_surface
```

Artifacts:

- `scripts/select_qa_mode_without_oracle.py::structural_question_focus_bonus`
- `scripts/select_qa_mode_without_oracle.py::structural_specialized_answer_surface_override`
- `scripts/summarize_selector_guard_families.py::RETIRED_SCAR_GUARDS`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_destruction_supervisor_role_surface`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_keeps_recovery_identity_on_testimony_surface`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_keeps_handoff_surface_for_intake_actor`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_item_received_from_for_intake_actor`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_surveyor_certification_for_lapse_year`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_station_supervisor_without_guard`
- `docs/SELECTOR_GUARD_FAMILY_ROLLUP.md`
- `docs/SELECTOR_GUARD_LEDGER.md`
- `tmp/openrouter_actor_provenance_qa5_openrouter_20260512/summary.md`

Lesson:

Actor identity is not only `person_role`. The transferable principle is that a
who/actor question should prefer a compact surface that binds the actor to the
event, testimony, certification status, station role, or intake provenance the
question asks about. The rule remains deliberately smaller than "prefer any
actor row": broad custody, zone, ledger, standing supervision, or survey-result
rows still lose unless they carry the asked actor binding.

### GG-062 - Current Authority And Roster Surface Scoring

Date: 2026-05-12

Scope: current authority, dispute scope, and authoritative roster compression.

Trajectory:

```text
six entity-role guards still protected current authority or roster/correction
surfaces with local question phrases
  -> add generic current-authority, roster-alias/current-membership, dispute
     scope, publication authority, and correction-assignment scoring
  -> active guards compress 144 -> 138; entity-role active guards compress
     17 -> 11; six-lane hosted QA5 stays exact
  -> next pressure is the remaining hard residue: contract/guardianship
     authority, school-principal/source-record authority, same-name distinction,
     same-item identity, badge status, reinstatement, and supervision statement
     surfaces
```

Before:

- Active guards still selected publication holder plus restriction, unresolved
  dispute scope, authoritative roster membership, compact alias/table roster
  rows, roster helper rows, and correction assignment plus change type by
  literal branch.
- The high-risk pattern was letting current authority and roster correction
  questions depend on a private list of local phrases instead of a reusable
  answer-surface contract.

Intervention:

- Added a generic current-authority scoring slice in
  `scripts/select_qa_mode_without_oracle.py::structural_question_focus_bonus`.
- The rule rewards publication authority only when holder/authority is bound
  with an active restriction/resolution surface, dispute scope/topic for
  unresolved authority questions, compact roster alias/table rows over broad
  roster history, current roster membership over correction-action rows, and
  assignment plus change-type rows for correction-assignment questions.
- Removed six literal selector branches and moved them to scar history.

After:

```text
Selector ledger:
  active guards: 144 -> 138
  entity_role_authority active guards: 17 -> 11
  scar guards: 47 -> 53
  semantic families: 7
  unclassified reasons: 0

Local verification:
  focused selector suite: 328 passed
  broader local QA/selector/doc-link suite: 458 passed

Hosted verification:
  OpenRouter six-lane no-cache QA5: 30 / 0 / 0
  runtime load errors: 0
  write proposal rows: 0
  helper pressure: 109 rows, 3.633 rows/exact, bounded_helper_surface
```

Artifacts:

- `scripts/select_qa_mode_without_oracle.py::structural_question_focus_bonus`
- `scripts/select_qa_mode_without_oracle.py::structural_specialized_answer_surface_override`
- `scripts/summarize_selector_guard_families.py::RETIRED_SCAR_GUARDS`
- `tests/test_qa_mode_selector.py::test_publication_authority_guard_prefers_publication_restriction_surface`
- `tests/test_qa_mode_selector.py::test_arbitrator_unresolved_question_guard_prefers_dispute_scope_surface`
- `tests/test_qa_mode_selector.py::test_authoritative_homeroom_guard_prefers_membership_surface`
- `tests/test_qa_mode_selector.py::test_authoritative_homeroom_guard_prefers_alias_table_surface`
- `tests/test_qa_mode_selector.py::test_authoritative_homeroom_guard_skips_source_record_facts_v2_volume`
- `tests/test_qa_mode_selector.py::test_bus_assignment_correction_guard_prefers_change_surface`
- `docs/SELECTOR_GUARD_FAMILY_ROLLUP.md`
- `docs/SELECTOR_GUARD_LEDGER.md`
- `tmp/openrouter_authority_current_surface_qa5_openrouter_20260512/summary.md`

Lesson:

Current authority questions need the surface that binds the authority claim to
its current restriction, scope, roster state, or correction operation. Broad
status, source-record-facts scaffolds, correction-action rows, or large roster
history are not enough. The compact alias/table preference is the load-bearing
piece: current identity and roster authority must beat row volume without
encoding local student IDs, local groups, or row IDs.

### GG-063 - Entity Role Residue Compression

Date: 2026-05-12

Scope: final phrase-shaped `entity_role_authority` residue.

Trajectory:

```text
ten entity-role guards remained as local surface protections after the
identity, actor/provenance, and current-authority passes
  -> add narrow scoring for badge identity status, current item identity,
     alias disambiguation, layer authority, source-authority identity,
     statement-event supervision, role-history reinstatement, contract
     authority, and guardianship validity conditions
  -> active guards compress 138 -> 128; entity-role active guards compress
     11 -> 1; six-lane hosted QA5 stays exact
  -> leave the remaining baseline identity trap active until it can be proven
     as a generic cross-family baseline-vs-broad-action rule rather than a
     scarred selector phrase
```

Before:

- `entity_role_authority` still carried phrase branches for badge unresolved
  identity, same-item identity, source-record principal authority,
  statement-bound supervision, reinstatement role history, contract authority,
  guardianship validity, layer authority, and same-name disambiguation.
- These were not all the same problem, but they shared one generality test:
  the winning surface had to bind the asked identity/status/authority relation
  directly, not merely mention a nearby person, source, role, or status row.

Intervention:

- Extended `structural_question_focus_bonus()` with narrow contracts for:
  - badge identity status plus badge/access event;
  - current item description plus current label;
  - alias plus group-membership disambiguation;
  - archival layer row-value authority;
  - source author/claim authority for institutional role identity;
  - statement claim plus event attribute for supervision questions;
  - compact role-history `holds_role` for reinstatement;
  - contract validity authority source / acting role holder / rule condition;
  - guardianship validity as residence plus governing condition.
- Removed ten literal branches from
  `structural_specialized_answer_surface_override` and moved them to scar
  history.
- Left `identity question has baseline name/role support and candidate is broad
  action-heavy` active. That guard is not phrase-shaped; it is a baseline
  protection principle that needs its own cross-family audit.

After:

```text
Selector ledger:
  active guards: 138 -> 128
  entity_role_authority active guards: 11 -> 1
  scar guards: 53 -> 63
  semantic families: 7
  unclassified reasons: 0

Local verification:
  focused selector suite: 333 passed
  broader local QA/selector/doc-link suite: 463 passed

Hosted verification:
  OpenRouter six-lane no-cache QA5: 30 / 0 / 0
  runtime load errors: 0
  write proposal rows: 0
  helper pressure: 94 rows, 3.133 rows/exact, bounded_helper_surface
```

Artifacts:

- `scripts/select_qa_mode_without_oracle.py::structural_question_focus_bonus`
- `scripts/select_qa_mode_without_oracle.py::structural_specialized_answer_surface_override`
- `scripts/summarize_selector_guard_families.py::RETIRED_SCAR_GUARDS`
- `tests/test_qa_mode_selector.py::test_badge_id_guard_prefers_unresolved_identity_badge_surface`
- `tests/test_qa_mode_selector.py::test_same_item_guard_prefers_current_identity_description_surface`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_keeps_alias_plus_group_for_same_name_distinction`
- `tests/test_qa_mode_selector.py::test_road_jurisdiction_authority_prefers_archival_layer_value_surface`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_source_authority_for_principal_identity_without_guard`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_statement_event_supervision_without_guard`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_reinstatement_role_history_without_guard`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_contract_authority_without_guard`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_guardianship_residence_condition_without_guard`
- `docs/SELECTOR_GUARD_FAMILY_ROLLUP.md`
- `docs/SELECTOR_GUARD_LEDGER.md`
- `tmp/openrouter_entity_role_residue_qa5_openrouter_20260512/summary.md`

Lesson:

The entity-role family compressed only because each retired branch was replaced
by a fixture-free binding contract. A direct `person_role` is not enough; the
surface must bind the actor or identity to the status, event, authority,
disambiguator, rule, or current object relation the question asks about. The
remaining active entity-role guard is intentionally different: it protects
baseline explicit name/role support from broad action-heavy candidates, so it
should be audited as a general baseline protection rule, not swept into the
scar pile just to make the family count hit zero.

### GG-064 - Operational Current Status Surface Scoring

Date: 2026-05-12

Scope: explicit current/final/status-at surfaces in `operational_record_status`.

Trajectory:

```text
operational_record_status was the largest active guard family after
entity-role compression, with status/current/final branches still phrased as
selector exceptions
  -> move snapshot status, review completion, pending determination, current
     final state, decision status, priority, adjusted expiration, and
     deaccession-yet preferences into fixture-free focus scoring
  -> active guards compress 128 -> 118; operational_record_status active
     guards compress 36 -> 26; scars rise 63 -> 73; six-lane hosted QA5 stays
     exact
  -> leave broader request/eligibility/rescission/concern guards active until
     they can prove a shared request-state or process-resolution substrate
```

Before:

- `operational_record_status` still carried literal selector branches for
  snapshot sampler status/state, review completion status-at, board pending
  determination, current final state, decision status, priority, adjusted
  expiration, and deaccession-yet status.
- These branches were not allowed to retire merely because the names were
  cleaned up. The replacement had to say why compact status/current/final rows
  beat broad record, event, lifecycle, or relaxed-heavy rows.

Intervention:

- Extended `structural_question_focus_bonus()` with compact status scoring:
  snapshot state questions prefer direct sampler status, with state-plus-cause
  outranking status when the question demands causal state; review completion
  prefers direct `status_at`; vote/status questions prefer direct pending
  determination; current operational status prefers final state bound to
  current state; decision, priority, adjusted expiration, and deaccession-yet
  questions prefer compact direct status predicates.
- Removed the corresponding specialized guard reasons from active selector
  control flow and moved them to scar history.
- Updated targeted tests so the selected mode remains the same while
  `specialized_guard_reason` stays empty.

After:

```text
Selector ledger:
  active guards: 128 -> 118
  operational_record_status active guards: 36 -> 26
  scar guards: 63 -> 73
  semantic families: 7
  unclassified reasons: 0

Local verification:
  focused selector suite: 337 passed
  broader local QA/selector/doc-link suite: 467 passed

Hosted verification:
  OpenRouter six-lane no-cache QA5: 30 / 0 / 0
  runtime load errors: 0
  write proposal rows: 0
  helper pressure: 104 rows, 3.467 rows/exact, bounded_helper_surface
```

Artifacts:

- `scripts/select_qa_mode_without_oracle.py::structural_question_focus_bonus`
- `scripts/select_qa_mode_without_oracle.py::structural_specialized_answer_surface_override`
- `scripts/summarize_selector_guard_families.py::RETIRED_SCAR_GUARDS`
- `tests/test_qa_mode_selector.py::test_snapshot_state_guard_prefers_sampler_status_surface`
- `tests/test_qa_mode_selector.py::test_snapshot_state_guard_prefers_state_plus_cause_when_available`
- `tests/test_qa_mode_selector.py::test_snapshot_state_guard_falls_back_to_sampler_state_surface`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_compact_deaccession_status_for_yet_question`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_final_state_for_current_operational_status`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_explicit_priority_surface`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_explicit_decision_surface`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_current_expiration_for_adjusted_reinstatement_expiration`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_status_at_for_review_completion`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_pending_determination_without_guard`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_explicit_decision_status_without_guard`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_current_expiration_without_guard`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_explicit_priority_without_guard`
- `docs/SELECTOR_GUARD_FAMILY_ROLLUP.md`
- `docs/SELECTOR_GUARD_LEDGER.md`
- `tmp/openrouter_operational_status_qa5_openrouter_20260512/summary.md`

Lesson:

Status/current/final questions need compact surfaces that bind the requested
state, decision, completion, priority, expiration, or "not yet" condition
directly. Broad lifecycle rows, adjacent event/action histories, relaxed
fallback rows, or lot/status inventories can mention the right topic while
still failing the asked status relation. This is operational-state
architecture, not a sampler, board, permit, or lot-specific rescue.

### GG-065 - Operational Process Resolution Scoring

Date: 2026-05-12

Scope: process-resolution residue inside `operational_record_status`.

Trajectory:

```text
after current/status/final compression, 26 operational guards remained and
four still protected process-resolution surfaces with phrase branches
  -> move commit readiness, board concern decision, current-constitution
     eligibility, and resubmission proof/rule resolution into reusable focus
     scoring
  -> active guards compress 118 -> 114; operational_record_status active
     guards compress 26 -> 22; scars rise 73 -> 77; six-lane hosted QA5 stays
     exact
  -> leave baseline-protection, request/outcome, source-status, and roster
     status guards active until they prove a wider substrate contract
```

Before:

- Commit-readiness, board-concern decision, current-constitution eligibility,
  and resubmission resolution still lived as literal specialized selector
  branches.
- These were not about the local entities in the questions. They were about
  whether the selected surface binds an unresolved process, decision/action
  history, controlling interpretation, or proof/rule resolution to the asked
  operational state.

Intervention:

- Extended `structural_question_focus_bonus()` with process-resolution scoring:
  pending/investigation/deferral evidence for commit questions;
  event/action/concern binding for board decision questions; applicant-type
  plus controlling interpretation for current-constitution questions; and
  proof/rule/applicant resolution support for resubmission questions.
- Removed four specialized guard branches and preserved their reasons as scar
  entries.
- Updated targeted tests to require the same selected surfaces without
  `specialized_guard_reason`.

After:

```text
Selector ledger:
  active guards: 118 -> 114
  operational_record_status active guards: 26 -> 22
  scar guards: 73 -> 77
  semantic families: 7
  unclassified reasons: 0

Local verification:
  focused selector suite: 337 passed
  broader local QA/selector/doc-link suite: 467 passed

Hosted verification:
  OpenRouter six-lane no-cache QA5: 30 / 0 / 0
  runtime load errors: 0
  write proposal rows: 0
  helper pressure: 120 rows, 4.0 rows/exact, bounded_helper_surface
```

Artifacts:

- `scripts/select_qa_mode_without_oracle.py::structural_question_focus_bonus`
- `scripts/select_qa_mode_without_oracle.py::structural_specialized_answer_surface_override`
- `scripts/summarize_selector_guard_families.py::RETIRED_SCAR_GUARDS`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_process_surface_for_commit_readiness`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_commit_readiness_not_blocked_by_status_baseline_guard`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_event_action_history_for_board_concern_decision`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_applicant_type_for_current_constitution`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_keeps_rule_proof_surface_for_resubmission_resolution`
- `docs/SELECTOR_GUARD_FAMILY_ROLLUP.md`
- `docs/SELECTOR_GUARD_LEDGER.md`
- `tmp/openrouter_operational_process_resolution_qa5_openrouter_20260512/summary.md`

Lesson:

Process-resolution questions should reward rows that bind the asked process
state to the evidence that resolves it: investigation/pending action,
event/action concern history, applicant type plus controlling interpretation,
or proof/rule resolution. A bare status row can be true but incomplete, and a
current applicant/status row can be adjacent but not resolving. This is a
process-resolution contract, not a local permitting or lab-status patch.

### GG-066 - Rationale Evidence-Source Binding

Date: 2026-05-12

Scope: first `rationale_evidence_contrast` slice.

Trajectory:

```text
rationale_evidence_contrast became the largest active family with 34 guards
after operational-status compression
  -> move memo reliability scope, phone-ping granularity, negative reliability,
     and evidentiary witness/report status into evidence-source binding scoring
  -> active guards compress 114 -> 110; rationale_evidence_contrast active
     guards compress 34 -> 30; scars rise 77 -> 81; six-lane hosted QA5 stays
     exact
  -> continue rationale compression by separating witness/provenance,
     cause/rationale, and source-note contrast instead of mixing them together
```

Before:

- The first rationale/evidence guards were phrase branches for memo
  establishment, phone-ping granularity, negative reliability, and
  evidentiary report status.
- The shared pressure was not the named memo, phone, testimony, or report. It
  was whether the chosen evidence surface binds the source/evidence object to
  the interpretive scope requested by the question.

Intervention:

- Extended `structural_question_focus_bonus()` with evidence-source binding:
  memo content plus reliability scope; device or phone ping plus location
  granularity; direct source-reliability scope for negative reliability
  questions; and witness/report plus allegation/document context for
  evidentiary-status questions.
- Removed four specialized guard branches and preserved them as scar history.
- Updated targeted tests so the same modes win without
  `specialized_guard_reason`.

After:

```text
Selector ledger:
  active guards: 114 -> 110
  rationale_evidence_contrast active guards: 34 -> 30
  scar guards: 77 -> 81
  semantic families: 7
  unclassified reasons: 0

Local verification:
  focused selector suite: 337 passed
  broader local QA/selector/doc-link suite: 467 passed

Hosted verification:
  OpenRouter six-lane no-cache QA5: 30 / 0 / 0
  runtime load errors: 0
  write proposal rows: 0
  helper pressure: 93 rows, 3.1 rows/exact, bounded_helper_surface
```

Artifacts:

- `scripts/select_qa_mode_without_oracle.py::structural_question_focus_bonus`
- `scripts/select_qa_mode_without_oracle.py::structural_specialized_answer_surface_override`
- `scripts/summarize_selector_guard_families.py::RETIRED_SCAR_GUARDS`
- `tests/test_qa_mode_selector.py::test_memo_establish_guard_prefers_memo_reliability_scope_surface`
- `tests/test_qa_mode_selector.py::test_phone_ping_granularity_guard_prefers_device_ping_surface`
- `tests/test_qa_mode_selector.py::test_negative_reliability_guard_prefers_reliability_scope`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_witness_report_surface_for_evidentiary_status`
- `docs/SELECTOR_GUARD_FAMILY_ROLLUP.md`
- `docs/SELECTOR_GUARD_LEDGER.md`
- `tmp/openrouter_rationale_evidence_source_binding_qa5_openrouter_20260512/summary.md`

Lesson:

Evidence-source questions need rows that bind the evidence object to the asked
scope: what a memo establishes, what a ping row can spatially resolve, what a
source does or does not reliably establish, or what kind of report supports an
evidentiary status. Broad investigative context, generic evidence-source rows,
unresolved activity labels, and claim-status rows can be nearby while still
missing the evidence/source relation the answer depends on.

### GG-067 - Rationale Witness Provenance Scoring

Date: 2026-05-12

Scope: witness/provenance residue inside `rationale_evidence_contrast`.

Trajectory:

```text
after evidence-source binding, rationale_evidence_contrast still carried 30
active guards, many of them witness/provenance phrase branches
  -> move source belief, source-specific witness, source claim, permission
     request, survey commission, maintenance evidence, and correction
     authorship into generic witness/provenance scoring
  -> active guards compress 110 -> 103; rationale_evidence_contrast active
     guards compress 30 -> 23; scars rise 81 -> 88; six-lane hosted QA5 stays
     exact
  -> continue with cause/rationale and source-note contrast, not with
     witness/provenance local names
```

Before:

- Seven rationale guards still encoded local phrasing around belief, witness
  reports, source claims, permission requests, commissioned reports,
  maintenance evidence, and correction authorship.
- The shared issue was provenance binding: which row directly carries the
  claimant, witness, commissioned-by, evidence-source, or authorship relation
  the question asks for.

Intervention:

- Extended `structural_question_focus_bonus()` with witness/provenance scoring:
  testimony/claim surfaces beat identification summaries for belief questions;
  witness report plus incident claim beats unresolved summaries for
  source-specific questions; direct witness statements beat broad finding/date
  rows for claims and permission; report-commission and handwriting/expert
  attribution get direct credit; and evidence-source/status rows are protected
  from hearsay/finding volume.
- Removed seven specialized guard branches and preserved their reasons as scar
  entries.
- Added fixture-free transfer tests for claim provenance, permission request,
  witness report, report commission, and authorship attribution.

After:

```text
Selector ledger:
  active guards: 110 -> 103
  rationale_evidence_contrast active guards: 30 -> 23
  scar guards: 81 -> 88
  semantic families: 7
  unclassified reasons: 0

Local verification:
  focused selector suite: 342 passed
  broader local QA/selector/doc-link suite: 472 passed

Hosted verification:
  OpenRouter six-lane no-cache QA5: 30 / 0 / 0
  runtime load errors: 0
  write proposal rows: 0
  helper pressure: 105 rows, 3.5 rows/exact, bounded_helper_surface
```

Artifacts:

- `scripts/select_qa_mode_without_oracle.py::structural_question_focus_bonus`
- `scripts/select_qa_mode_without_oracle.py::structural_specialized_answer_surface_override`
- `scripts/summarize_selector_guard_families.py::RETIRED_SCAR_GUARDS`
- `tests/test_qa_mode_selector.py::test_specialized_guard_keeps_source_belief_on_testimony_surface`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_keeps_source_belief_on_testimony_surface`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_source_specific_witness_claim_without_guard`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_witness_statement_for_source_claim_without_guard`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_witness_statement_for_permission_request_without_guard`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_report_commission_provenance_without_guard`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_keeps_receipt_surface_for_maintenance_evidence`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_handwriting_attribution_without_guard`
- `docs/SELECTOR_GUARD_FAMILY_ROLLUP.md`
- `docs/SELECTOR_GUARD_LEDGER.md`
- `tmp/openrouter_rationale_witness_provenance_qa5_openrouter_20260512/summary.md`

Lesson:

Witness/provenance questions are not about remembered names. They ask which
surface binds an assertion to its source: testimony, claim, witness report,
commissioning relation, receipt/evidence source, or authorship attribution.
Broad finding summaries, identification status rows, unresolved discrepancy
rows, evidence dates, and correction status can be adjacent but not
provenance-bearing.

### GG-068 - Rationale Cause Outcome Scoring

Date: 2026-05-12

Scope: cause/outcome residue inside `rationale_evidence_contrast`.

Trajectory:

```text
after witness/provenance compression, rationale_evidence_contrast carried 23
active guards and several were still outcome/cause phrase branches
  -> move failure deficiency, violation/status failure, display outcome, and
     status-elevation context into generic cause/outcome scoring
  -> active guards compress 103 -> 98; rationale_evidence_contrast active
     guards compress 23 -> 18; scars rise 88 -> 93; six-lane hosted QA5 stays
     exact
  -> rationale_evidence_contrast is no longer the largest family; remaining
     work should split source-note contrast from narrative/fictional outcome
     residue
```

Before:

- Five cause/outcome guards still handled local phrases for failure, display
  outcome, and status elevation.
- The shared principle was not vendor/display/lot vocabulary. It was whether
  the evidence surface binds the asked outcome to the condition that explains
  it: deficiency, violation status, inspection/incident outcome, or
  lab/location/status context.

Intervention:

- Extended `structural_question_focus_bonus()` with cause/outcome scoring for
  deficiency plus inspection/status, violation plus inspection/status,
  inspection or incident outcome plus permit status/validity, and
  lab/location/status context for elevation questions.
- Removed five specialized guard branches and preserved their reasons as scar
  entries.
- Added fixture-free transfer tests for deficiency, violation/status failure,
  display outcome, and incident/validity outcome surfaces; updated the
  status-elevation test to assert guard-free selection.

After:

```text
Selector ledger:
  active guards: 103 -> 98
  rationale_evidence_contrast active guards: 23 -> 18
  scar guards: 88 -> 93
  semantic families: 7
  unclassified reasons: 0

Local verification:
  focused selector suite: 346 passed
  broader local QA/selector/doc-link suite: 476 passed

Hosted verification:
  OpenRouter six-lane no-cache QA5: 30 / 0 / 0
  runtime load errors: 0
  write proposal rows: 0
  helper pressure: 113 rows, 3.767 rows/exact, bounded_helper_surface
```

Artifacts:

- `scripts/select_qa_mode_without_oracle.py::structural_question_focus_bonus`
- `scripts/select_qa_mode_without_oracle.py::structural_specialized_answer_surface_override`
- `scripts/summarize_selector_guard_families.py::RETIRED_SCAR_GUARDS`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_status_elevation_context_surface`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_vendor_deficiency_without_guard`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_violation_status_failure_surface_without_guard`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_display_outcome_surface_without_guard`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_incident_validity_outcome_surface_without_guard`
- `docs/SELECTOR_GUARD_FAMILY_ROLLUP.md`
- `docs/SELECTOR_GUARD_LEDGER.md`
- `tmp/openrouter_rationale_cause_outcome_qa5_openrouter_20260512/summary.md`

Lesson:

Cause/outcome questions need evidence that binds the requested result to the
condition that explains it. A status row, event row, or broad permit/history
surface can be true and still miss the answer if it does not carry the
deficiency, violation, inspection/incident, or contextual status relation. The
replacement is a cause/outcome binding rule, not a vendor, display, or lot
exception.

### GG-069 - Rationale Source-Note Contrast Scoring

Date: 2026-05-12

Scope: source-note, memo, split/viability, and pending-test residue inside
`rationale_evidence_contrast`.

Trajectory:

```text
after cause/outcome compression, rationale_evidence_contrast carried 18 active
guards, with seven still protecting source-note, memo-row, pending-test, and
split/viability surfaces
  -> move claim-plus-unresolved-issue, archival memo row-value,
     rationale-note, pending test-status, and split/viability context into
     fixture-free structural scoring
  -> active guards compress 98 -> 91; rationale_evidence_contrast active
     guards compress 18 -> 11; scars rise 93 -> 100; six-lane hosted QA5 stays
     exact
  -> remaining rationale residue is now mostly narrative/outcome,
     authority/source-control, and evidence-contrast surface selection
```

Before:

- Seven rationale guards were still phrase branches for memo resolution, reply
  memo theory, baseline rationale notes, pending viability testing, and
  split/viability contrast.
- The transferable rule was not memo or vault vocabulary. It was whether the
  selected surface carried the asked explanatory relation: claim plus open
  issue, answer-bearing archival row value, rationale note, pending status, or
  split/condition context.

Intervention:

- Extended `structural_question_focus_bonus()` with source-note contrast
  scoring for claim/unresolved issue surfaces, archival memo row values,
  compact pending `test_status`, rationale-note predicates, and split/viability
  condition bindings.
- Removed seven specialized guard branches and preserved their reasons as scar
  entries.
- Added transfer tests for memo-resolution and reply-memo row-value selection;
  updated source-note, split/viability, pending-status, and rationale-note tests
  to assert guard-free selection.

After:

```text
Selector ledger:
  active guards: 98 -> 91
  rationale_evidence_contrast active guards: 18 -> 11
  scar guards: 93 -> 100
  semantic families: 7
  unclassified reasons: 0

Local verification:
  focused selector suite: 348 passed
  broader local QA/selector/doc-link suite: 478 passed

Hosted verification:
  OpenRouter six-lane no-cache QA5: 30 / 0 / 0
  runtime load errors: 0
  write proposal rows: 0
  helper pressure: 146 rows, 4.867 rows/exact, bounded_helper_surface
```

Artifacts:

- `scripts/select_qa_mode_without_oracle.py::structural_question_focus_bonus`
- `scripts/select_qa_mode_without_oracle.py::structural_specialized_answer_surface_override`
- `scripts/summarize_selector_guard_families.py::RETIRED_SCAR_GUARDS`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_memo_resolution_claim_issue_surface_without_guard`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_reply_memo_row_value_without_guard`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_keeps_rationale_note_for_cause_question`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_actual_split_surface_for_split_rationale`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_source_note_for_split_rationale_when_available`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_source_note_for_viability_concern_contrast`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_pending_status_for_not_yet_tested_question`
- `docs/SELECTOR_GUARD_FAMILY_ROLLUP.md`
- `docs/SELECTOR_GUARD_LEDGER.md`
- `tmp/openrouter_rationale_source_note_contrast_qa5_openrouter_20260512/summary.md`

Lesson:

Source-note contrast is architecture only when the note or row value binds the
question's explanatory contract. A generic note, status row, or source-document
presence is still too loose; the winning surface must bind the claim and open
issue, the asked memo row value, the pending status, or the split condition
that explains the answer. The scar boundary is clean: local packet phrases are
history, while source-note binding remains substrate.

### GG-070 - Rationale Outcome Authority Closure

Date: 2026-05-12

Scope: final active `rationale_evidence_contrast` residue.

Trajectory:

```text
after source-note contrast compression, rationale_evidence_contrast still carried
11 active guards, mostly narrative/outcome, controlling-source, and
paired-interpretation phrase branches
  -> move paired intake/photo interpretation, candidate-origin attributes,
     missing-evidence claim/absence, succession/creation, event-condition
     timing, found-object event, recorded value, source authority, plot outcome,
     marker-shift, and factual-discrepancy/outcome into controlling-fact scoring
  -> active guards compress 91 -> 80; rationale_evidence_contrast active
     guards compress 11 -> 0; scars rise 100 -> 111; active semantic families
     compress 7 -> 6
  -> the rationale guard family is fully retired from active selector behavior
```

Before:

- Eleven rationale guards remained as local phrase branches around narrative
  outcomes, apparent conflicts, direct recorded values, source authority, and
  event-condition timing.
- The shared substrate was not story vocabulary. It was a controlling-fact
  contract: the evidence surface must bind the asked contrast, authority,
  outcome, or explanation to the fact that decides it.

Intervention:

- Extended `structural_question_focus_bonus()` with controlling-fact scoring
  for paired interpretation, candidate origin plus attribute, claim/absence,
  succession/creation, event condition, found-object event, recorded value,
  controlling authority, plot outcome, measurement/location/finding basis, and
  factual discrepancy/outcome surfaces.
- Removed the final eleven `rationale_evidence_contrast` guard branches and
  preserved their reasons as scar entries.
- Added or updated transfer tests so each retired guard now asserts guard-free
  structural selection.

After:

```text
Selector ledger:
  active guards: 91 -> 80
  rationale_evidence_contrast active guards: 11 -> 0
  scar guards: 100 -> 111
  semantic families: 7 -> 6
  unclassified reasons: 0

Local verification:
  focused selector suite: 350 passed
  broader local QA/selector/doc-link suite: 480 passed

Hosted verification:
  OpenRouter six-lane no-cache QA5: 30 / 0 / 0
  runtime load errors: 0
  write proposal rows: 0
  helper pressure: 122 rows, 4.067 rows/exact, bounded_helper_surface
```

Artifacts:

- `scripts/select_qa_mode_without_oracle.py::structural_question_focus_bonus`
- `scripts/select_qa_mode_without_oracle.py::structural_specialized_answer_surface_override`
- `scripts/summarize_selector_guard_families.py::RETIRED_SCAR_GUARDS`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_intake_photo_consistency_surface_without_guard`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_alternative_inscription_union_surface_without_guard`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_missing_evidence_claim_absence_surface_without_guard`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_banner_change_creation_surface`
- `tests/test_qa_mode_selector.py::test_competition_hold_call_guard_prefers_timing_condition_surface`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_found_object_event_surface_for_day_three_beach_find`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_recorded_value_for_conservator_date_detail`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_keeps_governance_surface_for_display_authority`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_keeps_plot_outcome_for_fictional_coin_order`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_keeps_marker_shift_surface_for_boundary_discrepancy_cause`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_keeps_discrepancy_explanation_surface_over_fiction_events`
- `docs/SELECTOR_GUARD_FAMILY_ROLLUP.md`
- `docs/SELECTOR_GUARD_LEDGER.md`
- `tmp/openrouter_rationale_outcome_authority_qa5_openrouter_20260512/summary.md`

Lesson:

The rationale family did not retire because every story case became the same.
It retired because every remaining guard pointed at the same structural move:
select the surface that binds the asked contrast, authority, or outcome to its
controlling fact. Names, story objects, and local events stay out of the
harness; the reusable architecture is the binding contract.

### GG-071 - Operational Direct Surface Compression

Date: 2026-05-12

Scope: direct answer-surface residue inside `operational_record_status`.

Trajectory:

```text
after rationale closure, operational_record_status was the largest active family
with 22 guards, many still routing direct operational answer surfaces by phrase
  -> move expected-order, notice/role drafting, reassignment, roster schedule,
     archival version, incident anchors, public-event extension status,
     attendance/authority transfer, roster role hints, completion-report issue
     bundles, temporary supervisor absence, group formation, and hazard
     observation into direct operational-surface scoring
  -> active guards compress 80 -> 67; operational_record_status active guards
     compress 22 -> 9; scars rise 111 -> 124; six-lane hosted QA5 stays exact
  -> operational is no longer the largest active family; remaining operational
     work is baseline-protection and request/status residue
```

Before:

- Thirteen operational guards still encoded direct answer surfaces as phrase
  branches.
- The shared principle was not school, report, permit, or roster vocabulary. It
  was directness: the surface that carries the scheduled date, issued notice,
  explicit reassignment, version row, incident anchor, extension status,
  attendance transfer, role hint, issue bundle, group formation, or hazard
  observation should beat broad roster/status/source volume.

Intervention:

- Extended `structural_question_focus_bonus()` with direct operational-surface
  scoring for the listed predicate contracts.
- Narrowed the identity-name uncertainty trap so a drafting question can trust
  `notice_issued + person_role` even when another mode contains a raw name.
- Removed thirteen specialized operational guard branches and preserved their
  reasons as scar entries.
- Added or updated transfer tests so each retired guard asserts guard-free
  structural selection.

After:

```text
Selector ledger:
  active guards: 80 -> 67
  operational_record_status active guards: 22 -> 9
  scar guards: 111 -> 124
  semantic families: 6
  unclassified reasons: 0

Local verification:
  focused selector suite: 354 passed
  broader local QA/selector/doc-link suite: 484 passed

Hosted verification:
  OpenRouter six-lane no-cache QA5: 30 / 0 / 0
  runtime load errors: 0
  write proposal rows: 0
  helper pressure: 125 rows, 4.167 rows/exact, bounded_helper_surface
```

Artifacts:

- `scripts/select_qa_mode_without_oracle.py::structural_question_focus_bonus`
- `scripts/select_qa_mode_without_oracle.py::structural_identity_completeness_trap_reason`
- `scripts/select_qa_mode_without_oracle.py::structural_specialized_answer_surface_override`
- `scripts/summarize_selector_guard_families.py::RETIRED_SCAR_GUARDS`
- `tests/test_qa_mode_selector.py::test_expected_order_guard_prefers_expected_order_surface`
- `tests/test_qa_mode_selector.py::test_communications_officer_guard_prefers_notice_role_surface`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_homeroom_reassignment_surface_without_guard`
- `tests/test_qa_mode_selector.py::test_trip_date_guard_prefers_roster_state_surface`
- `tests/test_qa_mode_selector.py::test_erratum_report_of_record_keeps_archival_identifier_surface`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_incident_anchor_surface_without_guard`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_keeps_public_event_extension_purpose_surface`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_temporary_availability_authority_surface_without_guard`
- `tests/test_qa_mode_selector.py::test_temporary_role_guard_prefers_roster_state_role_hints`
- `tests/test_qa_mode_selector.py::test_completion_report_guard_prefers_summary_issue_surfaces`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_temporary_supervisor_absence_surface_without_guard`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_group_formation_for_temporary_team_roster`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_hazard_observation_for_no_touch_question`
- `docs/SELECTOR_GUARD_FAMILY_ROLLUP.md`
- `docs/SELECTOR_GUARD_LEDGER.md`
- `tmp/openrouter_operational_direct_surface_qa5_openrouter_20260512/summary.md`

Lesson:

Operational directness is not a fixture phrase. It is a predicate contract:
when the question asks for an operational fact, prefer the surface that binds
the fact directly over broad source, roster, status, or event volume. The one
trap adjustment is also structural: explicit action-plus-role evidence can
outweigh raw name evidence when the question asks who performed that action.

### GG-072 - State/Custody Direct Surface Compression

Date: 2026-05-12

Scope: direct answer-surface residue inside `state_custody_ownership`.

Trajectory:

```text
after operational direct-surface compression, state/custody had 24 active
guards and was tied with threshold/policy pressure as the largest family
  -> move direct collision/location, custody/status, scan/correction,
     time-bound physical location, current component state, custody-transfer
     rationale, award/result, possession, insured-by, object-location,
     asset-state/location, and entitlement-effect branches into reusable
     direct state/custody-surface scoring
  -> active guards compress 67 -> 55; state_custody_ownership active guards
     compress 24 -> 7; scars rise 124 -> 136; six-lane hosted QA5 stays exact
     and helper rows drop 125 -> 88
  -> the remaining state/custody guards are harder composites: legal title,
     possession-versus-ownership, custody-document authority, publication
     restrictions, MOU scope, tree-amendment row fidelity, and one baseline
     award/result protector
```

Before:

- Twelve state/custody guards still routed direct surfaces by local question
  phrases.
- The replacement principle was not a local archive, object, award, or ledger
  noun. It was direct state binding: the surface that binds current state,
  possession, custody transfer, insured-by, location, or correction effect
  should beat broad title, provenance, event, scan, or claim volume.

Intervention:

- Extended `structural_question_focus_bonus()` with direct state/custody
  scoring for answer-bearing predicate contracts.
- Removed twelve specialized branches and preserved their reasons as scar
  entries.
- Added a generic transfer replay test using fixture-free object/state/
  possession/location wording, then converted older birth-row tests to assert
  guard-free structural selection.

After:

```text
Selector ledger:
  active guards: 67 -> 55
  state_custody_ownership active guards: 24 -> 7
  scar guards: 124 -> 136
  semantic families: 6
  unclassified reasons: 0

Local verification:
  focused selector suite: 355 passed
  broader local QA/selector/doc-link suite: 485 passed

Hosted verification:
  OpenRouter six-lane no-cache QA5: 30 / 0 / 0
  runtime load errors: 0
  write proposal rows: 0
  helper pressure: 88 rows, 2.933 rows/exact, bounded_helper_surface
```

Artifacts:

- `scripts/select_qa_mode_without_oracle.py::structural_question_focus_bonus`
- `scripts/select_qa_mode_without_oracle.py::structural_specialized_answer_surface_override`
- `scripts/summarize_selector_guard_families.py::RETIRED_SCAR_GUARDS`
- `tests/test_qa_mode_selector.py::test_near_duplicate_bin_code_guard_prefers_collision_location_surface`
- `tests/test_qa_mode_selector.py::test_custody_release_guard_prefers_status_surface_over_scan_volume`
- `tests/test_qa_mode_selector.py::test_barcode_supersession_guard_prefers_scan_correction_surface`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_direct_state_custody_surfaces_without_guards`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_direct_insurance_link_surface`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_entitlement_effect_for_correction_entitlement_question`
- `docs/SELECTOR_GUARD_FAMILY_ROLLUP.md`
- `docs/SELECTOR_GUARD_LEDGER.md`
- `tmp/openrouter_state_direct_surface_qa5_openrouter_20260512/summary.md`

Lesson:

Direct state is architecture only when it is phrased as a predicate contract.
The same scoring rule can handle custody release, current component state,
physical location, possession, insured-by links, and asset pickup because each
case asks for a current or time-bound state surface. The guards left behind are
not obvious cleanup targets; they combine authority, ownership distinctions,
publication restrictions, document provenance, or archival row fidelity and
may become stable edge-case guards rather than retirements.

### GG-073 - Policy Input Surface Compression

Date: 2026-05-12

Scope: direct policy, measurement, status, and arithmetic input residue inside
`threshold_policy_arithmetic`.

Trajectory:

```text
after state/custody compression, threshold_policy_arithmetic was the largest
active family with 19 guards
  -> move compliance status, change type, projection trigger, permit issuance,
     unresolved issue, hearing event, measurement value, roster-of-record,
     source-status/supersession, parent-letter review, scan/location,
     parcel zoning, site/draft-condition, staff finding/site measure, lab
     result/status, candidate-origin detail, rank/correction, and financial
     value branches into direct policy/input-surface scoring
  -> active guards compress 55 -> 36; threshold_policy_arithmetic active guards
     compress 19 -> 0; scars rise 136 -> 155; six-lane hosted QA5 stays exact
  -> after compression, the old rule family became too broad by share, so the
     rollup was split into rule_decision_procedure and rule_lifecycle_timing
     while preserving a tiny rule_activation_surface residue
```

Before:

- Nineteen threshold/policy guards still encoded direct policy inputs as
  specialized branches.
- The common replacement was a direct input contract: choose the surface that
  binds the requested compliance/status/change/measurement/rule input or
  arithmetic operand, rather than broad document, status, roster, claim, or
  source-record volume.

Intervention:

- Extended `structural_question_focus_bonus()` with direct policy/input
  scoring for the retired predicate contracts.
- Removed all active `threshold_policy_arithmetic` guard branches and preserved
  their reasons as scar entries.
- Added fixture-free replay coverage for direct policy inputs, including
  permit issuance, remedy/open issue, hearing event, roster-of-record,
  source-status governance, letter review, zoning, build-out, dimensional
  standards, and lab-result status.
- Split rule-family classification so the remaining guards no longer hide
  inside one oversized `rule_activation_surface` bucket.

After:

```text
Selector ledger:
  active guards: 55 -> 36
  threshold_policy_arithmetic active guards: 19 -> 0
  scar guards: 136 -> 155
  semantic families: 7
  unclassified reasons: 0
  largest family share: 0.25

Local verification:
  focused selector suite: 356 passed
  broader local QA/selector/doc-link suite: 486 passed

Hosted verification:
  OpenRouter six-lane no-cache QA5: 30 / 0 / 0
  runtime load errors: 0
  write proposal rows: 0
  helper pressure: 180 rows, 6.0 rows/exact, bounded_helper_surface
```

Artifacts:

- `scripts/select_qa_mode_without_oracle.py::structural_question_focus_bonus`
- `scripts/select_qa_mode_without_oracle.py::structural_specialized_answer_surface_override`
- `scripts/summarize_selector_guard_families.py::RETIRED_SCAR_GUARDS`
- `scripts/summarize_selector_guard_families.py::FAMILIES`
- `tests/test_qa_mode_selector.py::test_roster_ratio_compliance_prefers_compliance_status_surface`
- `tests/test_qa_mode_selector.py::test_correction_notice_replacement_guard_prefers_change_type_surface`
- `tests/test_qa_mode_selector.py::test_projection_supersession_guard_prefers_trigger_surface`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_direct_policy_input_surfaces_without_guards`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_candidate_vessel_list_surface`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_keeps_financial_value_surface_for_missing_book_claim`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_packet_time_measurement_surface`
- `tests/test_qa_mode_selector.py::test_competition_corrected_rank_guard_prefers_rank_correction_surface`
- `docs/SELECTOR_GUARD_FAMILY_ROLLUP.md`
- `docs/SELECTOR_GUARD_LEDGER.md`
- `tmp/openrouter_policy_input_surface_qa5_openrouter_20260512/summary.md`

Lesson:

Threshold and policy guards were mostly not threshold architecture anymore.
They were direct input selectors: compliance status, change type, permit
issuance, measurement value, zoning, rank correction, financial value, and
source-status facts. Once those predicate contracts were named, the family
collapsed. The important extra move was after the collapse: family health is
part of architecture, so the remaining rule guards were split by semantic
pressure instead of letting one broad bucket absorb the whole ledger.

### GG-074 - Operational Residue Closure

Date: 2026-05-12

Scope: final compact process/status residue inside `operational_record_status`.

Trajectory:

```text
after policy-input compression, operational_record_status was the largest
active family with 9 guards
  -> move baseline status/rule, application status, filed-response content,
     contract request/outcome, court/source status, unresolved/disputed status,
     planning request summary, and prior-proposal disposition branches into
     compact process/status surface scoring
  -> active guards compress 36 -> 27; operational_record_status active guards
     compress 9 -> 0; scars rise 155 -> 164; six-lane hosted QA5 stays exact
  -> helper pressure rises to 343 rows because the school roster fixture again
     delivered broad roster support; treat that as delivery pressure, not as
     selector guard regression
```

Before:

- Nine operational guards remained after earlier direct-surface compression.
- They were no longer local process architecture. Each could be stated as:
  choose the compact row bundle that binds the requested status, response
  content, request outcome, source/document status, unresolved/disputed state,
  application summary, or proposal disposition.

Intervention:

- Extended `structural_question_focus_bonus()` with compact process/status
  scoring for those predicate contracts.
- Removed the final operational-status guard branches and preserved their
  reasons as scar entries.
- Narrowed the operational uncertainty trap so a focused status surface is not
  forced back to the LLM merely because a competing operational mode contains
  record-state predicates.
- Added fixture-free selector replay for response content, contract rescission,
  court determination, resolved status, planning request, and prior proposal
  surfaces.

After:

```text
Selector ledger:
  active guards: 36 -> 27
  operational_record_status active guards: 9 -> 0
  scar guards: 155 -> 164
  semantic families: 6
  unclassified reasons: 0
  largest family share: 0.333

Local verification:
  focused selector suite: 357 passed
  broader local QA/selector/doc-link suite: 487 passed

Hosted verification:
  OpenRouter six-lane no-cache QA5: 30 / 0 / 0
  runtime load errors: 0
  write proposal rows: 0
  helper pressure: 343 rows, 11.433 rows/exact, bounded_helper_surface
```

Artifacts:

- `scripts/select_qa_mode_without_oracle.py::structural_question_focus_bonus`
- `scripts/select_qa_mode_without_oracle.py::structural_operational_record_status_trap_reason`
- `scripts/select_qa_mode_without_oracle.py::structural_baseline_answer_surface_guard_reason`
- `scripts/select_qa_mode_without_oracle.py::structural_specialized_answer_surface_override`
- `scripts/summarize_selector_guard_families.py::RETIRED_SCAR_GUARDS`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_keeps_baseline_for_application_status_relaxed_candidate`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_compact_operational_status_surfaces_without_guards`
- `docs/SELECTOR_GUARD_FAMILY_ROLLUP.md`
- `docs/SELECTOR_GUARD_LEDGER.md`
- `tmp/openrouter_operational_residue_qa5_openrouter_20260512/summary.md`

Lesson:

Operational status was not one substance. The earlier passes retired direct
state and process-resolution branches; this pass closed the final residue by
recognizing compact answer surfaces that bind process state to the requested
question act. The closure also shows why helper pressure and guard pressure
must stay separate: the selector family disappeared cleanly, but school roster
delivery still needs its own pruning discipline.

### GG-075 - Rule Binding Residue Compression

Date: 2026-05-12

Scope: rule-decision, rule-lifecycle, and rule-activation residue.

Trajectory:

```text
after operational residue closure, active rule families carried 15 guards:
9 rule_decision_procedure, 5 rule_lifecycle_timing, and 1 rule_activation_surface
  -> move request-validity/vote, revised-plan rule events, interpreted
     decision support, component category/condition, recusal/vote/rule,
     window history/interpretation, rejection correction, permit validity
     intervals, appeal hearing, suspension trigger, and operational-hours
     branches into rule/event binding scoring
  -> active guards compress 27 -> 13; rule_lifecycle_timing and
     rule_activation_surface active guards compress to 0; rule_decision_procedure
     compresses 9 -> 1; scars rise 164 -> 178
  -> the remaining rule-decision guard is an archival row-value fallback, not a
     general rule-binding principle
```

Before:

- Rule-family guards still mixed reusable rule/event binding with a few source
  fidelity fallbacks.
- The reusable replacement was: choose surfaces that bind the governing rule,
  decision condition, triggering event, lifecycle endpoint, or interpretation
  to the concrete question act.

Intervention:

- Extended `structural_question_focus_bonus()` with rule/event binding scoring.
- Removed fourteen rule-decision, rule-lifecycle, and rule-activation branches
  and preserved their reasons as scars.
- Added fixture-free replay coverage for rescission validity, revised-plan
  rejection, deferment, component condition, recusal vote/rule, window merit,
  rejection correction, appeal hearing, and permitted hours.
- Converted older validity-period, unrenewed-expiry, and suspension-trigger
  tests from guard assertions to guard-free structural assertions.

After:

```text
Selector ledger:
  active guards: 27 -> 13
  rule_decision_procedure active guards: 9 -> 1
  rule_lifecycle_timing active guards: 5 -> 0
  rule_activation_surface active guards: 1 -> 0
  scar guards: 164 -> 178
  semantic families: 4
  unclassified reasons: 0

Local verification:
  broader local QA/selector/doc-link suite: 488 passed

Hosted verification:
  OpenRouter six-lane no-cache QA5: 30 / 0 / 0
  runtime load errors: 0
  write proposal rows: 0
  helper pressure: 103 rows, 3.433 rows/exact, bounded_helper_surface
```

Artifacts:

- `scripts/select_qa_mode_without_oracle.py::structural_question_focus_bonus`
- `scripts/select_qa_mode_without_oracle.py::structural_baseline_answer_surface_guard_reason`
- `scripts/select_qa_mode_without_oracle.py::structural_specialized_answer_surface_override`
- `scripts/summarize_selector_guard_families.py::RETIRED_SCAR_GUARDS`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_rule_binding_surfaces_without_guards`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_routes_valid_period_to_union_validity_surface_without_guard`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_unrenewed_expiry_endpoint_surface`
- `tests/test_qa_mode_selector.py::test_hybrid_selector_prefers_violation_record_for_suspension_trigger`
- `docs/SELECTOR_GUARD_FAMILY_ROLLUP.md`
- `docs/SELECTOR_GUARD_LEDGER.md`
- `tmp/openrouter_rule_binding_residue_qa5_openrouter_20260512/summary.md`

Lesson:

Rule binding is architecture when it is phrased as a relation between a
governing rule, the triggering event or lifecycle endpoint, and the question's
decision act. It is not architecture when it merely says which local memo row
won once. That is why the archival rule-effect row-value guard remains active:
it may be a stable source-fidelity singleton rather than something the selector
should generalize away.

### GG-076 - State/Access Residue Terminal Compression

Date: 2026-05-12

Scope: state/custody/ownership, regulatory access/scope, and baseline
award-result residue.

Trajectory:

```text
Before:
  active guards: 13
  state_custody_ownership active guards: 7
  regulatory_access_scope active guards: 4
  entity_role_authority active guards: 1
  rule_decision_procedure active guards: 1
  scar guards: 178

Intervention:
  Remove 8 guard branches whose reusable principle can be stated without
  fixture names:
    - award/result rows beat adjacent name/state rows for award questions
    - access authority must bind to active policy/publication restrictions
    - current custody/location must bind to publication restriction state
    - agreement scope expansion must bind governing clause plus access/addition
    - ownership questions reward possession/ownership/inheritance/transfer
      distinction surfaces
    - legal-title contests reward claim/default/transfer surfaces over static
      owner rows
    - universal-scope questions reward set-enumeration rows that bind
      acknowledgement and deadline status
    - affected-target questions reward rows binding the target entity to
      correction or unit-count checks

After:
  active guards: 13 -> 5
  state_custody_ownership active guards: 7 -> 2
  regulatory_access_scope active guards: 4 -> 1
  entity_role_authority active guards: 1 -> 1
  rule_decision_procedure active guards: 1 -> 1
  scar guards: 178 -> 186
  semantic families: 4
  unclassified reasons: 0

Local verification:
  focused selector suite: 359 passed
  broader local QA/selector/doc-link suite: 489 passed

Hosted verification:
  OpenRouter six-lane no-cache QA5: 30 / 0 / 0
  helper rows: 120
  rows per exact answer: 4.0
  candidate-helper share: 0.1917
  runtime load errors: 0
  write proposal rows: 0
```

Lesson:

This slice is the first credible terminal boundary for guard compression. The
retired guards shared reusable relation structure: authority plus restriction,
custody plus publication state, agreement clause plus scope expansion, title
claim plus transfer/default context, or target membership plus exclusion/check
evidence. Those are architecture.

The 5 remaining guards are different. Three protect exact source-row fidelity
or archival row-value fallback, one protects baseline identity arbitration
against broad action-heavy candidates, and one still contains greenhouse-shaped
initial-status/exclusion vocabulary. Further compression should not be automatic.
Each remaining guard must either find unlike transfer evidence or stay as a
stable singleton/scar candidate. At this point the guard-compression phase is
entering terminal audit, not another bulk-retirement lane.

Next pressure:

- Decide whether the remaining `initial-affected greenhouse` guard can be
  rephrased as fixture-free initial-status/exclusion scoring. If it cannot,
  leave it active until unlike transfer appears.
- Treat the `governing-2024-custody-document`, `tree-amendment measurement`,
  and `rule-effect archival memo row value` guards as source-fidelity
  singletons unless better source-addressability substrate appears.
- Treat the remaining identity baseline guard as an arbitration-protection rule,
  not a helper/selector architecture growth target.

### GG-077 - Bound-Token Source Addressability Cleanup

Date: 2026-05-12

Scope: source-fidelity and helper classification after guard-compression
terminal audit.

Trajectory:

```text
Before:
  source_record_packet_metadata_support mixed two different surfaces:
    - clean generic identifier metadata
    - candidate prose-derived source notes
  source_record_matching_token_source was still labeled candidate-helper even
  though it only joined a bound query token to admitted source_record_* rows.

Prediction:
  A bound query token matched to source_record_numeric_token/2 and
  source_record_section/2 is source-addressability, not fixture learning. It can
  be labeled clean-helper if broad source-record scans still do not emit the
  high-pressure prose note rows.

Intervention:
  Reclassify source_record_matching_token_source as clean-helper and add an
  explicit SourceAddressability=bound_query_token field. Keep discovery,
  temporal, sample-result, timestamp-authority, filing, routing, clock, order,
  and item-event prose recognizers candidate-helper.

After:
  packet metadata helper contract now distinguishes:
    - clean identifiers
    - clean bound-token source-addressability
    - candidate prose-derived notes

Local verification:
  focused domain QA helper suite: 119 passed
  helper/domain/doc-link suite: 130 passed

Hosted verification:
  OpenRouter six-lane no-cache QA5: 30 / 0 / 0
  helper rows: 113
  rows per exact answer: 3.767
  candidate-helper share: 0.1858
  runtime load errors: 0
  write proposal rows: 0
```

Boundary update:

`interior_extended`. The operation is fixture-free: it does not inspect answer
words, story nouns, row ids, or local source prose. It only preserves the source
section for a query constant already present in admitted source-record numeric
tokens. This is source-fidelity architecture.

Next pressure:

Do not promote the remaining packet prose recognizers. The next helper cleanup
should either:

- reduce delivered roster/source-record helper rows without changing the
  candidate/clean boundary; or
- move another source-addressability operation from candidate to clean only if
  the rule can be stated over admitted source_record rows and query bindings.

### GG-078 - Wide OpenRouter Corpus Measurement

Date: 2026-05-12

Scope: broad hosted measurement after the guard-compression terminal boundary
and bound-token source-addressability cleanup.

Trajectory:

```text
Before:
  Six-fixture QA5 pressure was enough for fast guard/scar replay, but it did not
  measure how the tuned instrument behaved across the wider source-backed
  fixture corpus. The risk was over-reading local six-fixture exactness as
  corpus stability.

Prediction:
  A wider hosted run should be measurement only. It may expose provider
  throughput limits, source-fidelity pressure, helper-volume pressure, and
  query-planning gaps, but it must not license fixture, row, question, or answer
  vocabulary in the harness.

Intervention:
  Run a 12-lane OpenRouter compile over 56 source-backed fixtures, then run QA40
  over the 32 successfully compiled artifacts. Preserve all failures as
  transport/provider evidence rather than silently treating them as architecture
  failures. Cap future hosted default width back to six lanes after provider
  throttling appears.

After:
  Compile:
    fixtures attempted: 56
    parsed OK: 32
    compile artifacts: 32
    failed/no compile artifact: 24
    dominant provider/runtime pressure: OpenRouter/provider 429 and one
      incomplete read at 12 lanes

  QA over successful compiles:
    fixtures: 32 / 32 complete
    questions: 1218
    exact / partial / miss: 1008 / 76 / 134
    exact rate: 0.8276
    runtime load errors: 0
    write proposal rows: 0
    helper rows: 2877
    rows per exact answer: 2.854
    candidate-helper share: 0.1585
    pressure label: high_clean_helper_volume

Artifacts:
  compile summary:
    tmp/openrouter_wide_corpus_compile_20260512/compile_batch_summary.md
  QA summary:
    tmp/openrouter_wide_corpus_qa40_20260512/qa_batch_summary.md
```

Boundary update:

`measurement_extended`. The corpus run is not a guard-retirement event and not
a fixture-learning event. It establishes a broader measurement baseline for the
current instrument: strong hosted transfer across the 32 compiled fixtures,
clear evidence that 12 hosted lanes overdrive provider capacity, and continuing
helper-surface pressure that should be handled as source-fidelity/helper
cleanup rather than local vocabulary repair.

Lesson:

Hosted width is an instrument parameter, not a doctrine change. Twelve lanes
produced enough throttling to reduce practical throughput, while the completed
QA artifacts show the tuned instrument is stable enough for broader pressure.
Future OpenRouter pressure should default to six lanes unless the experiment is
explicitly about provider limits.

Next pressure:

- Retry the 24 compile-missing fixtures only if broad corpus coverage is needed,
  using six lanes or fewer and preserving the current failed rows as provider
  evidence.
- Mine the 32 QA artifacts for fixture-free helper/source-fidelity classes:
  high clean-helper volume, candidate-helper share, compile-surface gaps, and
  query-planning gaps.
- Do not tune against any fixture name, question id, row id, or local story
  phrase exposed by this wide run.

## Trajectory Board

| Pressure | Before | Intervention | After | Next Pressure |
| --- | --- | --- | --- | --- |
| Helper-pressure guards | `13` high-priority `candidate_guard:helper_pressure` entries with local guard reasons | Recast first slice as count/measure binding, post-change membership, counterfactual arithmetic, and authority/action substrate; retire every high-priority helper-pressure guard after unlike replay | Helper-pressure guards compress `13 -> 0`; scars rise `16 -> 29`; active guards compress `175 -> 162`; high-priority helper-pressure lane is closed | Move to singleton/single-question guard debt without letting fixture nouns enter substrate |
| Singleton high-priority guards | `6` high-priority singleton `candidate_guard` entries remained after helper-pressure closed | Retire calculated-deadline, appeal event/context, duration event/interval, and membership-transition guards with unlike replay | High-priority singleton guards compress `6 -> 0`; scars rise `29 -> 35`; active guards compress `162 -> 156` | Shift from high-priority singleton retirement to hosted query-planning gaps and medium-priority guard families |
| Medium entity-role authority guards | `29` active medium-priority `entity_role_authority` guards remained after singleton closure | Replace literal direct-identity, actor/provenance, current-authority, and final residue branches with fixture-free binding contracts | Active guards compress `156 -> 128`; `entity_role_authority` active guards compress `29 -> 1`; scars rise `35 -> 63`; latest six-lane QA5 is `30 / 0 / 0` with `94` helper rows | Audit the remaining baseline identity trap as a cross-family baseline-protection rule; then move to the next largest family |
| Medium operational status guards | `36` active `operational_record_status` guards remained after entity-role compression | Replace literal current/status/final branches with compact status-surface scoring for snapshot, review, pending determination, final state, decision, priority, expiration, and not-yet status rows | Active guards compress `128 -> 118`; `operational_record_status` active guards compress `36 -> 26`; scars rise `63 -> 73`; six-lane QA5 is `30 / 0 / 0` with `104` helper rows | Audit remaining process-resolution status guards without turning local request prose into substrate |
| Operational process-resolution guards | `26` active operational guards remained, including four process-resolution phrase branches | Replace commit-readiness, board concern, current-constitution, and resubmission branches with reusable process-resolution scoring | Active guards compress `118 -> 114`; `operational_record_status` active guards compress `26 -> 22`; scars rise `73 -> 77`; latest six-lane QA5 is `30 / 0 / 0` with `120` helper rows | Shift to remaining baseline-protection/request-status residue or the larger `rationale_evidence_contrast` family |
| Rationale evidence-source guards | `34` active `rationale_evidence_contrast` guards remained as the largest family | Replace memo reliability, phone granularity, negative reliability, and evidentiary report branches with reusable evidence-source binding scoring | Active guards compress `114 -> 110`; `rationale_evidence_contrast` active guards compress `34 -> 30`; scars rise `77 -> 81`; latest six-lane QA5 is `30 / 0 / 0` with `93` helper rows | Continue rationale compression by separating witness/provenance, cause/rationale, and source-note contrast subfamilies |
| Rationale witness/provenance guards | `30` active rationale guards remained after evidence-source binding, including seven witness/provenance phrase branches | Replace belief, witness-report, source-claim, permission, commission, evidence-source, and authorship branches with generic provenance scoring | Active guards compress `110 -> 103`; `rationale_evidence_contrast` active guards compress `30 -> 23`; scars rise `81 -> 88`; latest six-lane QA5 is `30 / 0 / 0` with `105` helper rows | Continue with cause/rationale and source-note contrast without local witness names |
| Rationale cause/outcome guards | `23` active rationale guards remained after provenance compression, including five failure/outcome/status-elevation phrase branches | Replace deficiency, violation/status, display outcome, and elevation context branches with cause/outcome scoring | Active guards compress `103 -> 98`; `rationale_evidence_contrast` active guards compress `23 -> 18`; scars rise `88 -> 93`; latest six-lane QA5 is `30 / 0 / 0` with `113` helper rows | Split remaining source-note contrast from narrative/fictional outcome residue |
| Rationale source-note contrast guards | `18` active rationale guards remained after cause/outcome compression, including memo, source-note, pending-test, and split/viability phrase branches | Replace claim/open-issue, archival memo row-value, rationale-note, pending-status, and split/viability context branches with source-note contrast scoring | Active guards compress `98 -> 91`; `rationale_evidence_contrast` active guards compress `18 -> 11`; scars rise `93 -> 100`; latest six-lane QA5 is `30 / 0 / 0` with `146` helper rows | Attack the remaining narrative/outcome and source-authority rationale residue; watch helper pressure because this retirement was not a row-compression win |
| Rationale outcome/authority closure | `11` active rationale guards remained after source-note compression | Replace paired interpretation, candidate-origin attributes, claim/absence, succession/creation, event-condition, found-object, recorded-value, source-authority, plot-outcome, marker-shift, and factual-outcome branches with controlling-fact scoring | Active guards compress `91 -> 80`; `rationale_evidence_contrast` active guards compress `11 -> 0`; scars rise `100 -> 111`; active semantic families compress `7 -> 6`; latest six-lane QA5 is `30 / 0 / 0` with `122` helper rows | Move to the largest remaining active family: operational status residue, while preserving the single entity-role baseline trap for later cross-family handling |
| Operational direct surfaces | `22` active operational guards remained after rationale closure, many routing direct answer surfaces by phrase | Replace expected-order, notice/role, reassignment, roster schedule, archival version, incident anchor, extension/status, attendance transfer, role hint, issue bundle, supervisor absence, group formation, and hazard observation branches with direct-surface scoring | Active guards compress `80 -> 67`; `operational_record_status` active guards compress `22 -> 9`; scars rise `111 -> 124`; latest six-lane QA5 is `30 / 0 / 0` with `125` helper rows | Move to custody/ownership or threshold/policy families now tied as largest; leave remaining operational baseline-protection residue for a smaller cleanup pass |
| State/custody direct surfaces | `24` active state/custody guards remained, including twelve direct state, possession, location, and correction-effect branches | Replace collision/location, custody/status, scan/correction, time-bound location, component state, custody-transfer, award/result, possession, insured-by, object-location, asset-state, and entitlement-effect branches with direct state/custody scoring | Active guards compress `67 -> 55`; `state_custody_ownership` active guards compress `24 -> 7`; scars rise `124 -> 136`; latest six-lane QA5 is `30 / 0 / 0` with `88` helper rows | Treat the seven remaining state/custody guards as harder composites; next broad target is `threshold_policy_arithmetic` with 19 active guards |
| Policy input surfaces | `19` active threshold/policy guards remained, mostly direct policy, status, measurement, and arithmetic input branches | Replace compliance, change-type, trigger, permit, remedy, hearing, measurement, roster, source-status, parent-letter, scan/location, zoning, site/finding, lab/status, origin/detail, rank/correction, and financial-value branches with direct policy/input scoring; split oversized rule family | Active guards compress `55 -> 36`; `threshold_policy_arithmetic` active guards compress `19 -> 0`; scars rise `136 -> 155`; latest six-lane QA5 is `30 / 0 / 0` with `180` helper rows; family health returns to pass | Remaining pressure is no longer one big threshold bucket: largest family is operational status with 9 guards; rule pressure is split into decision/procedure and lifecycle/timing |
| Operational residue closure | `9` active operational-status guards remained after direct-surface and policy-input compression | Replace baseline status/rule, application status, response content, contract request/outcome, court/source status, unresolved/disputed status, planning request, and prior-proposal branches with compact process/status surface scoring | Active guards compress `36 -> 27`; `operational_record_status` active guards compress `9 -> 0`; scars rise `155 -> 164`; latest six-lane QA5 is `30 / 0 / 0` with `343` helper rows | Move to remaining rule-decision/rule-lifecycle and state/custody composites; keep roster helper delivery pressure separate |
| Rule binding residue | `15` active rule-family guards remained across decision, lifecycle, and activation pressure | Replace request-validity, rule-event, interpreted decision, component condition, recusal/vote/rule, window history/interpretation, rejection correction, validity interval, appeal hearing, suspension trigger, and operational-hours branches with rule/event binding scoring | Active guards compress `27 -> 13`; `rule_lifecycle_timing` and `rule_activation_surface` active guards close; `rule_decision_procedure` leaves one archival fallback; scars rise `164 -> 178`; latest six-lane QA5 is `30 / 0 / 0` with `103` helper rows | Treat remaining rule-effect archival row-value guard as a source-fidelity singleton candidate; next pressure is state/custody composites or regulatory scope |
| State/access terminal residue | `13` active guards remained across state/custody, regulatory scope, identity, and archival rule-effect residue | Replace award/result, access-with-restriction, custody-with-publication-state, agreement-scope expansion, ownership distinction, legal-title contest, universal-scope, and affected-target branches with reusable relation scoring | Active guards compress `13 -> 5`; scars rise `178 -> 186`; latest six-lane QA5 is `30 / 0 / 0` with `120` helper rows | Stop bulk compression unless unlike transfer appears; remaining guards are source-fidelity, baseline-arbitration, or singleton initial-status residue |
| Bound-token source addressability | `source_record_matching_token_source` was candidate-labeled despite only joining bound query tokens to admitted source-record numeric tokens and sections | Reclassify the bound-token section surface as clean-helper and add explicit `SourceAddressability=bound_query_token`; leave prose-derived source notes candidate-labeled | six-lane QA5 remains `30 / 0 / 0`; helper rows `113`; candidate-helper share `0.1858`; local helper/domain/doc-link suite is `130 passed` | Keep promoting only source-addressability operations stated over admitted source rows and query bindings; do not promote prose recognizers without transfer |
| Compact answer surfaces | Broad roster/status/receipt/title/note rows could outrank compact count-bearing, rule-input, deadline, event-context, duration, or transition evidence | `structural_count_measure_focus_bonus()` rewards rows binding measure, population, scope, time/status, and operands; sibling scoring rewards threshold/action/arithmetic, calculated-deadline, appeal event/context, duration event/interval, and membership-transition surfaces | Conveyed-item, approval/display, inventory/title, density, threshold/action, attendance/session, scoped-roster, adult-total, scoped-status count, post-change membership-count, reserve arithmetic, authority/action, calculated-deadline, appeal event/context, duration, and transition guards retired; selector suite is `327 passed` | Hold further compact-surface retirement unless new unlike replay exposes a missing substrate principle |
| Type/category count surfaces | Unary `_type/1` rows could mix stable categories with dated or instance variants, inflating category counts | `type_category_support` collapses sibling atoms only when they expose a reusable coded category prefix and includes a no-collapse control | festival q001 moves exact; festival QA5 is `5 / 0 / 0`; fresh six-fixture QA5 is `30 / 0 / 0` with `191` helper rows | Prove transfer on unlike `_type/1` count misses before graduating; avoid arbitrary atom clustering |
| Lifecycle interval context | Validity, extension, and status facts could be retrieved separately without one answer-ready interval/context surface | `lifecycle_period_support` bundles same-entity-family period rows with admitted exception/status/extension context and triggers from either interval or context predicates | targeted festival q003/q004 are exact; festival QA5 is `5 / 0 / 0`; strict six-fixture QA5 is `28 / 2 / 0` with `204` helper rows | Prove unlike lifecycle transfer; then repair greenhouse initial-state and Sable vote arithmetic as separate substrate pressures |
| Vote threshold counterfactuals | Vote counts, thresholds, roles, and source vote tokens existed separately, leaving counterfactual outcome arithmetic to the judge | `vote_threshold_counterfactual_support` derives no-to-yes and absent-voter branch tables from admitted vote counts, voting thresholds, and optional source vote-token rows | targeted Sable q003/q004 are exact; Sable QA5 is `5 / 0 / 0`; six-fixture QA5 is `29 / 1 / 0` with `234` helper rows | Prove unlike vote/threshold transfer and repair greenhouse initial-state precedence |
| Initial status scope | Broad status predicates could return both original and later-expanded status entities for an initial/original question | `initial_status_scope_support` separates entities mentioned in initial source sections/labels from later status context | targeted greenhouse q003 is exact; greenhouse QA5 is `5 / 0 / 0`; six-fixture replay is volatile at `27 / 0 / 2` but targeted variance checks are exact | Prove unlike initial/current transfer; keep full-batch volatility separate from targeted repair evidence |
| Candidate source-note delivery | Prose-derived candidate notes could attach to broad unanchored source-record scans | Anchor discovery/sample/temporal candidate notes to source rows or query tokens for `source_record_*` scans | greenhouse and school targeted candidate packet rows drop while staying exact; lifecycle strict replay is `28 / 2 / 0` with remaining partials outside source-note delivery | Keep as delivery precision; separate source-note pressure from temporal/status precedence and counterfactual vote arithmetic |
| Helper pressure measurement | Raw helper rows were visible, but duplicate delivery and unique breadth were conflated | `audit_helper_usage.py` reports answer-normalized pressure, support-kind pruning targets, unique row breadth, and skips provenance-copy double counts | canonical delivered pressure is `5525` rows, collapsing to `229` unique helper rows; school QA5 rows/exact drops `136.2 -> 68.2 -> 34.8`; six-fixture QA5 helper rows drop `695 -> 156` | Judge remaining packet metadata pressure and keep non-roster answer drift separate from helper delivery wins |
| Helper package delivery | Primary and evidence-bundle phases could repeat the same helper rows inside one answer package | Deduplicate helper-labeled companion rows across combined query results | school q1-q7 fresh replay holds `7 / 0 / 0` while helper rows drop `4040 -> 1480`; six-fixture QA20 helper rows drop `7256 -> 3419` | Full school first-20 replay, then support-kind transfer review |
| Roster source-record assignment support | Candidate rows rescued answer coverage but risked hidden fixture memory | Support-kind target isolates `source_record_student_group_assignment` under `roster_state_support`; broad version scans now return compact group counts, relaxed fallback no longer spawns widened helper companions, and version/group slots normalize by atom shape | hosted school QA5 removes `source_record_student_group_assignment` from the helper audit while staying `5 / 0 / 0`; `roster_state_support` rows drop `220 -> 46 -> 35`; candidate `group_count` rows drop `18 -> 8`; six-fixture QA5 is `30 / 0 / 0` with total helpers `380 -> 267 -> 209` | Keep source-only `group_count` candidate-labeled until unlike transfer; keep packet metadata pressure separate from roster architecture |
| Source metadata delivery | Clean identifier metadata was answer-bearing but could attach to unrelated bound queries and broad packet lookups as repeated inventory rows | Compact repeated identifier inventory for broad source-record scans; require bound-token matches for bound source-record or unrelated predicates | school packet metadata rows drop `95 -> 21` in targeted QA5 and six-fixture helper rows drop `209 -> 148` while staying `30 / 0 / 0` | Transfer-review remaining candidate note kinds; keep clean identifier inventory scoped to identifier/source-metadata intent |
| Candidate transfer signals and packet names | Candidate-helper pressure mixed single-fixture rows with transferred scars, and local packet vocabulary appeared in support-kind names | Audit candidate pruning targets now carry transfer signals; operational packet support kinds use generic document/transport/assignment/device names | six-fixture QA5 is `29 / 1 / 0` with targeted partial replay exact; helper rows drop `148 -> 120`; no local packet support-kind names remain in implementation/tests | Review source-only `group_count` and lifecycle query-plan volatility as separate pressures |
| Local packet recognizer retirement | Generic support-kind names still hid local packet phrase recognizers | Retired the operational packet recognizer; kept only a generic retained-document physical-location parser; removed stale roster triggers | six-fixture QA5 is `30 / 0 / 0`; helper rows are `116`; `source_record_student_group_assignment` disappears again; school rows/exact is `9.2` | Prove or scar `document_retention_location` transfer; then return to source-only `group_count` |
| OpenRouter pressure cadence | Hosted lanes went idle after QA10, and cached runs could look active while doing no hosted calls | Six-lane QA20 refreshes, batch-level `--no-cache` for fresh hosted pressure, targeted hosted follow-ups, and transient retry handling for OpenRouter provider failures | cached QA20 reached `112 / 3 / 5`; fresh no-cache QA20 reached `110 / 4 / 6`; count-family QA5 no-cache reached `28 / 2 / 0`; compact-roster QA5 reached `25 / 4 / 1`; type-category six-fixture QA5 reached `30 / 0 / 0`; lifecycle-context strict QA5 reached `28 / 2 / 0`; vote-counterfactual QA5 reached `29 / 1 / 0`; initial-status QA5 target repair passed but full replay was volatile at `27 / 0 / 2`; relaxed-scope helper replay reached `30 / 0 / 0`; group-count provenance replay reached `30 / 0 / 0`; metadata-scope replay reached `30 / 0 / 0`; scoped-status retirement QA5 reached `30 / 0 / 0` with `108` helper rows; post-change membership QA5 reached `30 / 0 / 0` with `107` helper rows; reserve arithmetic QA5 reached `30 / 0 / 0` with `119` helper rows; authority/action QA5 reached `30 / 0 / 0` with `126` helper rows; calculated-deadline QA5 reached `30 / 0 / 0` with `133` helper rows; appeal event/context QA5 reached `30 / 0 / 0` with `170` helper rows; final-singleton QA5 reached `29 / 0 / 1` due to an OpenRouter 503; retry repair replay reached `30 / 0 / 0` with `117` helper rows; entity-role residue QA5 reached `30 / 0 / 0` with `94` helper rows; operational-status QA5 reached `30 / 0 / 0` with `104` helper rows; operational-process QA5 reached `30 / 0 / 0` with `120` helper rows; rationale evidence-source QA5 reached `30 / 0 / 0` with `93` helper rows; rationale witness-provenance QA5 reached `30 / 0 / 0` with `105` helper rows; rationale cause/outcome QA5 reached `30 / 0 / 0` with `113` helper rows; rationale source-note QA5 reached `30 / 0 / 0` with `146` helper rows; rationale outcome/authority QA5 reached `30 / 0 / 0` with `122` helper rows; operational direct-surface QA5 reached `30 / 0 / 0` with `125` helper rows; state/custody direct-surface QA5 reached `30 / 0 / 0` with `88` helper rows; policy input-surface QA5 reached `30 / 0 / 0` with `180` helper rows; operational-residue QA5 reached `30 / 0 / 0` with `343` helper rows; rule-binding residue QA5 reached `30 / 0 / 0` with `103` helper rows; all cited runs had `0` runtime errors and `0` write proposals | Keep six-lane slices warm; separate provider variance from query-planning and architecture evidence |
| Source-addressability execution | Evidence-bundle conjunctions were rejected as fake arities like `source_record_row/8` | Validate top-level conjunctive evidence-bundle queries and surface matching-token source sections, timestamp authority, statement filing notes, long source-row preservation, item/event identifier notes, strict packet scoping, placeholder-aware source scans, and transfer replays | Old hospital compile first-20 reached `20 / 0 / 0`; fresh long-ledger compile makes q013 exact with zero helpers; source-note repair plus item/event binding moves q1-q20 from `16 / 0 / 4` to `20 / 0 / 0`; packet precision drops helpers `163 -> 107 -> 66`; school transfer holds `20 / 0 / 0`; fresh greenhouse sample q007/q018 is `2 / 0 / 0` | Transfer-test remaining sample-result/source-note paths before graduating helper surfaces |
| Source numeric-token contract | Source numeric tokens were queried as visible constants but stored as `v_` ledger atoms | Repair unprefixed `source_record_numeric_token/2` constants during query execution | hospital q009 moved from miss to exact; first-13 replay is `13 / 0 / 0` | Keep as source-token normalization; avoid widening into arbitrary string search |
| Source-addressability transfer | QA20 pre-repair was `112 / 3 / 5` with source-row arity/token misses | Six-lane QA20 replay after source executor repairs | `113 / 0 / 7`; several source/date rows improved, some query plans shifted to misses | Stabilize query planning and answer-surface selection without local guard vocabulary |
| Identifier display judging | Normalized identifier atoms could be judged different from display IDs solely by punctuation/case | Add identifier-display equivalence to the QA judge contract | school q012 moved miss to exact; first-12 replay is `12 / 0 / 0` | Stabilize role/alias and duration answer surfaces |
| Identifier metadata judging | Clean metadata rows could be dismissed as indirect when a narrower identifier predicate was unavailable | Add identifier-metadata equivalence for clean `_identifier`/`_license_identifier` rows | school q015 recovers; q1-q15 fresh replay is `15 / 0 / 0` | Re-run school first-20 and keep metadata policy limited to clean identifier/code surfaces |
| Source-record note surfaces | Local packet support kinds carried answer-bearing retention, observer, and discovery notes | Rename/reshape into document retention, observer permission scope, and discovery-note surfaces | q1-q18 fresh replay is `18 / 0 / 0`; q1-q20 reaches `20 / 0 / 0` after structured observer fields | Transfer-review candidate source-note surfaces before graduating them |
| Structured observer permission | Observer support was a candidate display string with relationship/scope buried in prose | Parse normalized source text into observer, related person, relationship, group, action, time window, and limit fields | q1-q20 fresh replay is `20 / 0 / 0` with `3469` helper rows | Prove transfer before graduating from candidate-helper |
| Structured source-note transfer | School source-note fixes needed unlike-fixture pressure | Six-lane QA20 fresh replay after source-note changes | `114 / 2 / 4`, up from `107 / 6 / 7` after helper dedupe, with `0` runtime errors | Shift to greenhouse temporal movement/count and hospital source-name addressability |
| Temporal source-note movement | Greenhouse q014/q017 had answer-bearing movement/no-overlap rows only as raw source text | Parse normalized temporal source rows into candidate event/relation fields | Targeted fresh hosted replay q014/q017/q018 is `2 / 0 / 1`; broader greenhouse q1-q20 is `17 / 1 / 2` with q014/q017 exact | Fold into source-note transfer review with sample-result support; avoid graduating until unlike-fixture replay |
| Sample result source rows | Count-of-total sample prose could be skipped or contradicted by semantic lab_result rows | Preserve standalone sample-result prose in source_record ledger and expose candidate sample-result fields | Fresh greenhouse compile preserves missing Lot 5A sample prose; targeted q007/q018 is `2 / 0 / 0`; prior greenhouse q1-q20 high-water remains `20 / 0 / 0` | Transfer-test on unlike sampled/result fixtures and watch helper-row volume before graduating |
| Matching-token source sections | Time-bound provenance questions could retrieve event rows but miss the source document name | Match time-like query constants against source_record_numeric_token rows and expose the source section label | Hospital q009 targeted replay is exact; q1-q20 remains `18 / 0 / 2` for unrelated compile-surface gaps | Transfer-test on unlike timestamp/source-name rows and keep candidate-labeled until proven |
| Timestamp authority notes | Timestamp-conflict questions could retrieve event/log rows but miss which source/time the document says is authoritative | Parse source-stated authoritative timestamp/source and earlier or superseded timestamp/source into candidate helper rows | Hospital q018 targeted replay is `1 / 0 / 0`; helper pruning keeps q018 exact with one row; local full suite is `980 passed, 2 subtests passed` | Replay unlike version/correction conflicts before graduating; avoid broad source-record helper flooding |
| Statement filing notes | Statement predicates named content but source filing metadata lived in adjacent packet labels | Parse statement filing labels into speaker/filed-time/source notes and link to admitted `staff_statement/3` rows by speaker | Old compile q013 targeted replay is exact with 3 rows after pruning; fresh long-ledger compile q013 is exact with zero helper rows | Prefer source-fidelity/direct compile surfaces; keep filing helper candidate-labeled for packets where statement predicates remain thin |
| Long source row preservation | Long source-record rows could lose late answer-bearing clauses before compile or QA | Preserve 1200 chars per deterministic source row and test long statement tails | Fresh hospital q013 is `1 / 0 / 0` with zero helpers; fresh q1-q20 exposed `16 / 0 / 4` compile drift, then source-note repair recovered targeted misses | Keep as source-fidelity substrate; do not mask remaining q003/q20 drift with fixture-language helpers |
| Fresh compile source-note drift | Fresh long-ledger compile changed predicate shape enough to reopen role, order, telemetry-source, authority, and item/event questions | Add predicate-scoped packet/source metadata notes, item/event identifier notes, no-flood tests, and placeholder-aware broad-source scoping | Targeted q005/q008/q011/q017/q004/q003/q018 are exact; fresh q1-q20 is `20 / 0 / 0` with helper rows compressed `163 -> 107 -> 66` | Transfer-test item/event and timestamp-authority paths on unlike fixtures before guard retirement |
| Compact interval duration | Duration questions could miss when the KB bound `YYYY_MM_DD_HH_MM_HH_MM` as one interval atom | Query execution derives elapsed support from a prior compact interval binding | school q020 is exact; fresh school first-20 replay is `20 / 0 / 0` | Generalize only as interval arithmetic; avoid storing fixture-local schedule helpers |
| Adult role/status support | Adult-role rows exposed role labels but not person-level ratio/lodging status | `roster_state_support` carries admitted `ratio_count_status/2` and `lodging_assignment/3` status rows | q007 fresh replay recovers exact with explicit ratio/lodging support | Transfer this as role/status support, not a school-parent observer rule |
| Roster delivery precision | School transfer stayed exact but delivered 3054 helper rows, mostly broad roster tails | Scope `roster_state_support` by predicate contract, pair observed scans with scheduled/clock support, render lodging absence answer-ready, bind adult-role support to requested person/role, avoid broad assignment delivery for version-level or role-specific queries, and compact broad version scans to group counts | person-bound full q20 is `20 / 0 / 0` with 1732 helpers; q007 is exact with 4 roster rows; hosted school QA5 stays `5 / 0 / 0` while helper rows drop `681 -> 341 -> 174` | Refresh the six-fixture pressure run and then split remaining roster packet notes from source-addressability metadata |

## Operating Rule

Every guard must move toward one of three outcomes:

- **Generalize** into helper substrate, selector scoring, compile surface,
  predicate contract, or source-addressability ledger.
- **Scar** when it records a local accident that should remain visible but not
  active behavior.
- **Retire** only after replay proves the replacement holds on the birth row and
  unlike rows.

The key test:

```text
Would this guard still make sense if all fixture names, row IDs, local people,
and local organizations were removed?
```

## Current Pressure

Current selector ledger state:

- `5` active guards
- `0` high-priority `candidate_guard:helper_pressure`
- `186` scar guards
- `0` high-priority singleton `candidate_guard` entries
- `4` semantic families
- `0` unclassified reasons

Singleton or single-question guards are treated as **not-yet-architecture**
pressure. They are not automatically bad, but they must earn generality before
they shape helpers, selectors, or query planning.

## First Slice: Helper-Pressure Guards

This slice is now closed. The initial `13` high-priority helper-pressure guards
all moved into reusable substrate or scar history.

| Source Line | Family | Guard Reason | Likely Replacement |
| ---: | --- | --- | --- |
| _closed_ | _closed_ | no active high-priority helper-pressure guards remain | Next audit target is singleton/single-question guard debt. |

## First Architecture Bet

The strongest shared principle is count and measure binding:

```text
For count, total, density, threshold, and arithmetic questions, reward compact
surfaces that bind the requested measure, population, scope, time/status, and
numeric operands in the same evidence row or helper row. Penalize broad
membership, roster, status-history, receipt, badge, note, or title rows unless
they expose the measured set or explicit count.
```

This should be implemented as a reusable selector/scoring principle only if it
can be stated without local nouns and replayed across unlike rows.

Status: first implementation landed in
`scripts/select_qa_mode_without_oracle.py` as
`structural_count_measure_focus_bonus()`. Initial proof tests cover:

- explicit `session_attendance_count` beating interval roster volume; this
  guard has now retired into scar history after unlike session-count replay;
- `conveyed_item` enumeration beating broad receipt/source-record volume; this
  guard has now retired into scar history after unlike replay.
- `incident_outcome` count outcome beating title-name volume; this guard has
  now retired into scar history after unlike replay.
- approval/validity count surface beating broad current-status volume; this
  guard has now retired into scar history after unlike replay.
- section-bound assignment evidence beating broad activity-log volume for
  scoped roster/count questions; this guard has now retired into scar history
  after unlike section-membership replay.
- unlike approval/validity, conveyed-item, and density/numeric-measure rows
  beating broad status, receipt/source, and opinion volume. The density guard
  has now retired into scar history after `staff_evaluation` joined the generic
  measure-surface scoring contract.

This retired the adult-total, attendance/session, conveyed-item,
approval/display, inventory/title, density, threshold/action, scoped-roster,
scoped-status count, post-change membership-count, and reserve arithmetic
guards after replay. The count/membership/arithmetic slice is closed for now.
The high-priority helper-pressure lane is closed. Singleton and single-question
guard debt is now active; the high-priority singleton board is now closed after
calculated-deadline, appeal event/context, duration event/interval, and
membership-transition retirement.

## OpenRouter Review

OpenRouter review is active through `.env.local` and repo bootstrap. The first
batch review grouped the helper-pressure guards into these reusable pressure
classes:

- stable membership/count surface;
- quarantine-scope surface;
- authority/action surface;
- approval/validity surface;
- baseline arithmetic input surface;
- incident/count outcome surface;
- adult manifest support;
- explicit session attendance count;
- conveyed-item surface;
- numeric evaluation surface;
- threshold/action policy surface;
- source-record roster section surface.

Use these as review labels, not as magic family names. Each label still needs a
fixture-free implementation and replay.

Current OpenRouter pressure result: a six-fixture, 10-question first pass over
fresh hosted compiles scored `54 / 4 / 2` with `0` runtime load errors and `0`
write proposals. The strongest helper-pressure signal was not a new selector
guard: one roster/activity fixture produced `5525` helper rows (`2935`
candidate-helper, `2590` clean-helper) while scoring `10 / 0 / 0`. Treat that
as a coverage/pruning measurement target, not permission to encode fixture,
question, or answer vocabulary in the harness.

`scripts/audit_helper_usage.py` now reports answer-normalized helper pressure:
helper rows per judged exact answer, candidate-helper share, clean-helper share,
unique helper-row breadth, and a pressure label. On the same OpenRouter QA10
artifacts, the canonical usage audit reports `5525` delivered support-row
occurrences over `54` exact answers (`102.315` rows/exact) with
candidate-helper share `0.5312`, labeled `high_candidate_helper_pressure`.
Those delivered rows collapse to `229` unique helper rows, with `126` unique
candidate-helper rows and `103` unique clean-helper rows. The generality gate
has two parts: delivered helper volume is harness/packaging pressure, while
unique candidate-helper breadth is substrate transfer/pruning pressure.

The current pruning target is support-kind based, not fixture based:

| Helper | Candidate support kind | Delivered rows | Unique rows | Share of helper | Interpretation |
| --- | --- | ---: | ---: | ---: | --- |
| `roster_state_support` | `source_record_student_group_assignment` | `2535` | `108` | `0.5633` delivered / `0.5482` unique | Either this support kind transfers as a general source-record assignment surface, or it must be pruned/cleaned so it stops acting like hidden fixture memory. |
| `roster_state_support` | `group_count` | `215` | `9` | `0.0478` delivered / `0.0457` unique | Keep only if it behaves as a reusable count-bearing surface; otherwise fold into narrower count/measure scoring. |

Smaller operational packet support kinds are also candidate-helper rows, but
their row counts are secondary. They now use generic document/transport/
assignment/device names and should be reviewed as transfer candidates only if
their behavior transfers without preserving local packet vocabulary.

Next decision: first reduce duplicate delivery of identical helper tables inside
QA artifacts, then decide whether the `108` unique source-record assignment
rows deserve a generic source-record assignment ledger or remain
candidate-labeled until sibling transfer proves them.

## Singleton Guard Review

Singleton guards are reviewed after the helper-pressure slice, but they are part
of the same plan.

For each singleton:

1. Rewrite the reason as a fixture-free semantic mismatch.
2. Identify whether the replacement belongs to helper substrate, compile
   surface, selector scoring, predicate contracts, source-addressability, or
   scar history.
3. Block rewrites that depend on story names, local entities, row IDs, or
   question IDs.
4. Replay the birth row plus unlike rows before retiring behavior.

## Replay Standard

A guard can retire only when the replacement passes:

- the original row that created the guard;
- at least one unlike row in the same semantic family;
- a focused regression slice for the nearest known tempting wrong surface;
- the cheap selector/ledger tests.

Minimum local verification for worksheet edits:

```powershell
python -m pytest tests/test_selector_guard_families.py tests/test_qa_mode_selector.py -q
python -m pytest tests/test_public_doc_link_domains.py -q
```
