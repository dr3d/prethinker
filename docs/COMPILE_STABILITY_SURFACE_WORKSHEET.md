# Compile Stability Surface Worksheet

Last updated: 2026-05-15

This worksheet tracks the cross-cutting question that emerged from CSS,
transition/lens work, and assignment-scope probes:

> When a source exposes parallel answer-bearing surfaces, does one compile draw
> preserve all of them, or does the surface palette move across draws?

This is not a lens-specific problem. A lens audit asks whether a vocabulary term
or slot contract transfers. Compile stability asks whether the compiler
preserves sibling surfaces consistently enough for no-helper QA to depend on a
single draw.

Guardrails:

- Do not encode fixture names, source row IDs, question IDs, answer strings, or
  local story vocabulary as architecture.
- Treat multi-draw consensus as measurement until there is a deterministic
  admission contract.
- Distinguish predicate dialect drift from true surface absence.
- Prefer declarative compile-surface invariants over query helpers when the
  source clearly exposes the missing surface.

## CS-001 - Assignment Scope Stability Audit

Date: 2026-05-15

Question:

Does the assignment-scope miss represent a lens/query gap, or a single-draw
compile-stability problem?

Before:

The assignment-scope probe cycle scored:

- initial no-helper QA: `14 / 0 / 1`
- redraw of the single miss fixture: `5 / 0 / 0`

The redraw emitted both assignment rows, while the first draw emitted only one.
That suggested compile variance, but the evidence needed its own audit view.

Prediction:

If this is compile-stability pressure, comparing the two draws should show
predicate and surface drift beyond the one missed answer row. If it is merely a
single missing fact, the drift should be narrow.

Intervention:

Added `scripts/audit_compile_surface_stability.py`.

The audit compares multiple compile draws of the same fixture and reports:

- direct fact union/common counts;
- predicate count drift;
- coarse surface count drift;
- union facts missing from each draw.

This is post-hoc measurement only. It does not merge facts, alter compile
guidance, or repair QA.

After:

Equipment-service two-draw audit:

- compiles=`2`
- fixtures=`1`
- stable fixtures=`0`
- unstable direct facts=`41`
- predicate drift rows=`17`
- surface drift rows=`6`

Largest relevant surface drifts:

- `assignment_binding_surface`: `[3, 7]`
- `task_scope_surface`: `[5, 8]`
- `object_record_surface`: `[4, 8]`
- `identity_role_surface`: `[6, 9]`

The first draw missed direct rows that the redraw acquired:

- both assignee-task rows;
- both task-completion rows;
- richer task descriptions;
- record/status/condition rows.

Artifacts:

- `scripts/audit_compile_surface_stability.py`
- `tests/test_compile_surface_stability.py`
- `docs/data/compile_surface_stability/assignment_scope_equipment_stability_audit_20260515.md`
- `docs/data/compile_surface_stability/assignment_scope_equipment_stability_audit_20260515.json`

Verification:

- `python -m py_compile scripts\audit_compile_surface_stability.py`
- `python -m pytest tests\test_compile_surface_stability.py -q` -> `1 passed`

Lesson:

The assignment-scope miss was a symptom of a larger compile-palette movement.
The two draws are not simply one fact apart; they speak different predicate
dialects and preserve different sibling surfaces. This connects directly to the
earlier CSS source-authority problem: direct surfaces can be present in one draw
and absent or renamed in another.

The immediate architecture target is therefore not an assignment helper. It is
a compile-stability primitive:

> For repeated parallel events, each event should preserve the same core slots:
> subject/object, actor, role when explicit, task/scope/action, and temporal
> anchor when explicit.

Next pressure:

Run the same stability audit on one source-authority multi-draw pair and one
operational lifecycle pair. If the same surface drift appears across those
contexts, promote this from assignment-scope finding to a general
compile-stability contract.

## CS-002 - Cross-Context Stability Confirmation

Date: 2026-05-15

Question:

Does compile-surface instability recur outside assignment scope?

Before:

CS-001 showed large drift on a two-draw assignment fixture. The user connected
that pressure to older source-authority CSS work and operational lifecycle
work. The claim needed evidence across those contexts.

Prediction:

If this is a cross-cutting compile-stability primitive, source-authority and
operational lifecycle compiles should show the same pattern: direct facts and
predicate palettes move across draws or compile regimes, even when source
content is the same.

Intervention:

Ran `scripts/audit_compile_surface_stability.py` over:

- five probate/source-authority compile draws;
- three operational-record/status compile regimes for six fixtures.

After:

Source-authority/probate:

- compiles=`5`
- fixtures=`1`
- stable fixtures=`0`
- unstable direct facts=`342`
- predicate drift rows=`38`
- surface drift rows=`4`

Operational-record/status:

- compiles=`18`
- fixtures=`6`
- stable fixtures=`0`
- unstable direct facts=`679`
- predicate drift rows=`183`
- surface drift rows=`35`

Artifacts:

- `docs/data/compile_surface_stability/source_authority_probate_stability_audit_20260515.md`
- `docs/data/compile_surface_stability/source_authority_probate_stability_audit_20260515.json`
- `docs/data/compile_surface_stability/operational_record_status_stability_audit_20260515.md`
- `docs/data/compile_surface_stability/operational_record_status_stability_audit_20260515.json`

Verification:

- `python scripts\audit_compile_surface_stability.py ...` completed for both
  contexts.

Lesson:

The pressure is real and cross-cutting. It is larger than assignment scope,
larger than operational lifecycle, and larger than source authority. The
compiler can preserve different sibling surfaces across draws and under
different guidance regimes. This explains why a single draw can score cleanly
or miss a row without any query/helper change.

The audit also exposes a second measurement problem: exact direct-fact
intersection is often zero because predicate dialect changes. Surface-level
counts are more useful than exact fact equality, but still coarse. The next
useful primitive is a declarative preservation contract for repeated parallel
events and source-authority pairs, not another broad prompt paragraph.

Next pressure:

Draft the first compile-stability contract in fixture-free language:

- For repeated parallel events, preserve every event as a row binding event
  subject/object, actor when explicit, role when explicit, action/task/scope,
  and time/date when explicit.
- For source-authority pairs, preserve both the governed subject/action and the
  authority/source companion when explicit.

Then add an audit recognizer that can score those contracts directly instead of
using broad surface counts as a proxy.

## CS-003 - Consolidation Checkpoint

Date: 2026-05-15

Question:

What methodological refinements should be carried forward before the next
repair cycle?

Before:

The lens sweep, transition/delta work, helper retirement, and compile-surface
stability work were all producing useful artifacts, but the boundary between
them was easy to blur. A single not-exact row could look like a lens problem,
a query problem, a helper problem, or a compile problem depending on which
worksheet was open.

Refinement:

The current doctrine is now:

1. Lens vocabulary audit asks whether bounded structural terms and slot
   contracts transfer to unlike documents.
2. Query/transition repair is allowed only when the needed facts are already
   admitted and the gap is how to interpret or join them.
3. Compile-surface repair is allowed only when an unlike hard probe reproduces
   the missing answer-bearing surface.
4. Compile-stability audit is separate from compile-surface repair: it measures
   whether sibling surfaces are preserved consistently across draws or compile
   regimes.
5. Helper resurrection is disfavored unless a reusable surface proves that
   query-only support is the right layer.

After:

Verification pass:

- `python -m pytest tests\test_compile_surface_stability.py tests\test_compile_surface_invariants.py tests\test_lens_vocabulary_transfer.py tests\test_transition_delta_normalizer.py tests\test_query_transition_resolution_audit.py tests\test_operational_lifecycle_palette_audit.py tests\test_audit_helper_classes.py tests\test_audit_helper_usage.py tests\test_domain_bootstrap_file.py tests\test_domain_bootstrap_qa.py tests\test_domain_bootstrap_qa_batch.py -q`
- result: `283 passed`

Working-tree status before this journal entry was clean, so there were no
pending normalizer artifacts to commit.

Lesson:

The project now has a clearer layer stack:

- vocabulary/slot transfer;
- deterministic transition normalization;
- query interpretation over admitted rows;
- compile-surface acquisition;
- compile-surface stability across draws;
- helper compatibility quarantine.

The next work should not collapse those layers. In particular, compile
stability is now its own research lane: the first repair target is a direct
contract audit for repeated parallel events and source-authority pairs, not a
prompt paragraph and not a helper.

Next pressure:

Add contract-level recognizers for the two compile-stability primitives:

- repeated parallel event preservation;
- source-authority pair preservation.

Then rerun the stability audit on the assignment, operational, and
source-authority evidence sets.

## CS-004 - Contract-Level Stability Recognizers

Date: 2026-05-15

Question:

Can the compile-stability audit score preservation contracts directly, instead
of relying only on broad predicate/surface drift counts?

Before:

CS-001 and CS-002 showed large drift, but exact fact and predicate drift are
too coarse. Equivalent predicate dialects can make stable surfaces look
unstable, while a single missing sibling event can be hidden inside a large
drift board.

Prediction:

A first contract recognizer should make the assignment-scope evidence legible:
the first draw should be partial, and the redraw should pass, because the
redraw preserved both parallel assignee-task events.

Intervention:

Extended `scripts/audit_compile_surface_stability.py` with two first-pass
contract recognizers:

- `parallel_assignment_event_preservation`
- `source_authority_pair_preservation`

These recognizers are audit-only. They compare source-record signals against
direct surfaces within each draw and do not merge facts, repair compiles, or
alter QA.

After:

Assignment equipment two-draw replay:

- first draw: `parallel_assignment_event_preservation=partial`
  - source signals=`2`
  - direct surfaces=`1`
- redraw: `parallel_assignment_event_preservation=pass`
  - source signals=`2`
  - direct surfaces=`2`

The broader stability summaries remain:

- assignment two-draw: unstable facts=`41`, predicate drift=`17`, surface
  drift=`6`
- source-authority/probate: unstable facts=`342`, predicate drift=`38`,
  surface drift=`4`
- operational-record/status: unstable facts=`679`, predicate drift=`183`,
  surface drift=`35`

Artifacts:

- `scripts/audit_compile_surface_stability.py`
- `tests/test_compile_surface_stability.py`
- regenerated stability reports in `docs/data/compile_surface_stability/`

Verification:

- `python -m py_compile scripts\audit_compile_surface_stability.py`
- `python -m pytest tests\test_compile_surface_stability.py -q` -> `1 passed`

Lesson:

Contract-level scoring is the right direction. It turns the vague statement
"compile drift happened" into a testable preservation claim: the source exposed
two assignment events, and the draw preserved one or two of them. This is much
closer to architecture than exact fact equality.

The source-authority recognizer is still a first-pass proxy and needs sharper
slot logic before it should drive repair decisions.

Next pressure:

Harden the source-authority pair recognizer so it scores governed subject,
recipient/action, and authority/source slots rather than broad source tokens.
Then use the recognizer to decide whether source-authority stability needs a
compile contract, a profile-palette constraint, or multi-draw consensus.

## CS-005 - Source-Authority Slot Contract Hardening

Date: 2026-05-15

Question:

Can the source-authority stability recognizer distinguish complete
governed-subject/recipient/source pairs from shallow source-authority rows?

Before:

CS-004 counted broad source-authority-ish rows. That was useful as a first
proxy, but too permissive: a lone `court_order(...)`, an authority/source row
without recipient, or mismatched access/source recipients could look like
direct preservation.

Prediction:

A hardened recognizer should:

- count a decomposed access authority pair only when `access_authorized_to` and
  `access_source` share governed subject and recipient;
- count packed access-authority rows only when source and authorized party are
  both present for the subject;
- count generic authority/source predicates only when they expose at least
  three slots;
- track complete and partial direct units separately.

Intervention:

Updated `scripts/audit_compile_surface_stability.py`:

- added `_source_authority_direct_units()`;
- made `source_authority_pair_preservation` count complete direct units rather
  than broad source-like rows;
- added `direct_complete_count` and `direct_partial_count` to contract reports;
- expanded markdown output to show complete and partial counts.

Added a unit test proving that:

- `access_authorized_to(item, reader_one, ...)` plus
  `access_source(item, reader_two, source)` is not complete;
- the same subject and same recipient is complete;
- `court_order(...)` alone does not satisfy the contract.

After:

Probate/source-authority redraw under the hardened recognizer:

- `compile_surface_invariant_focused_probate_20260514`: partial,
  source signals=`11`, complete direct units=`9`
- `compile_surface_invariant_recompile_20260514`: ledger-only,
  source signals=`11`, complete direct units=`0`
- `source_authority_density_probate_compile_local_20260515`: partial,
  source signals=`11`, complete direct units=`8`
- `source_authority_invariant_probate_compile_20260514`: ledger-only,
  source signals=`11`, complete direct units=`0`
- `source_authority_invariant_probate_compile_local_20260514`: partial,
  source signals=`11`, complete direct units=`8`

No draw passes after slot hardening. This is a stronger and more honest result
than the earlier broad recognizer.

Artifacts:

- `scripts/audit_compile_surface_stability.py`
- `tests/test_compile_surface_stability.py`
- regenerated stability reports in `docs/data/compile_surface_stability/`

Verification:

- `python -m py_compile scripts\audit_compile_surface_stability.py`
- `python -m pytest tests\test_compile_surface_stability.py -q` -> `2 passed`

Lesson:

Source-authority stability is not solved by merely emitting authority-flavored
rows. The contract needs a governed subject, an actor/recipient/action surface,
and an authority/source companion that can be joined without guessing. Under
that stricter reading, the probate evidence is still partial at best.

Next pressure:

Do not repair from this recognizer alone. First make the source signal count
less approximate by extracting candidate governed-subject/recipient/source
mentions from source-record text or from source-ledger rows. Then decide
whether the repair belongs to compile guidance, profile-palette constraints, or
multi-draw consensus.

## CS-006 - Field-Bound Source Units And Operational Lifecycle Contract

Date: 2026-05-15

Question:

Can the stability audit move one step closer to pre-stamp measurement by making
source-authority source signals field-bound and adding an operational lifecycle
preservation contract?

Before:

CS-005 hardened the direct source-authority side, but the source side still
used authority-flavored text mentions. The operational/status report also had
only assignment and source-authority contracts, so its largest drift surface was
visible only as predicate/surface churn rather than as a preservation claim.

Prediction:

Two measurement-only refinements should improve the audit without changing the
instrument:

- source-authority source signals should prefer `source_record_field` rows that
  bind a subject/object, an access/party field, and an authority/source field on
  the same source record;
- operational lifecycle should count source text lines with lifecycle/status
  plus temporal/state markers and compare them to direct lifecycle/status facts
  with enough slots to bind event, subject/status, and time/state.

Intervention:

Updated `scripts/audit_compile_surface_stability.py`:

- added field-bound source units for `source_authority_pair_preservation`;
- kept text mention counts visible as provenance rather than primary source
  counts when structured source rows exist;
- added `operational_lifecycle_preservation`;
- expanded contract markdown columns so reports show source field units, source
  text mentions, direct surfaces, complete direct units, and partial direct
  units.

Added unit tests for:

- structured source-authority field units;
- operational lifecycle source text vs direct status/lifecycle surfaces.

After:

Source-authority/probate:

- structured source units=`12`;
- text mentions=`11`;
- best direct complete units remain `9` and `8`;
- two draws remain ledger-only at `0`;
- no source-authority draw passes under the stricter field-bound source count.

Operational/status:

- compiles=`18`, fixtures=`6`;
- preservation statuses: pass=`11`, partial=`5`, ledger-only=`2`;
- ledger-only cases: one grant-review draw and one water-sample palette draw;
- partial cases preserve some lifecycle surfaces but miss enough direct units to
  stay below the source signal count.

This turns the operational drift from a large undifferentiated predicate table
into a contract-level reading: most draws preserve the lifecycle surface, but
the same fixture family still has regime-specific collapses.

Artifacts:

- `scripts/audit_compile_surface_stability.py`
- `tests/test_compile_surface_stability.py`
- regenerated stability reports in `docs/data/compile_surface_stability/`

Verification:

- `python -m py_compile scripts\audit_compile_surface_stability.py`
- `python -m pytest tests\test_compile_surface_stability.py -q` -> `4 passed`

Lesson:

The preservation layer is becoming useful enough to gate a future stamp. It
does not repair compile variance; it names which source-exposed contract is
preserved, partial, ledger-only, or not applicable. That separation keeps the
future internal re-stamp from mixing architecture movement with measurement
language that is still settling.

Next pressure:

Run the audit-focused suite and commit this measurement layer. Then inspect the
two operational ledger-only rows and the five partial rows qualitatively before
any repair. If those failures are profile-palette omissions, repair belongs
there; if they are stochastic compile drops, they belong in multi-draw consensus
or stamp variance accounting.

## CS-007 - Operational Lifecycle Failure Shape

Date: 2026-05-15

Question:

Do the operational lifecycle partial and ledger-only rows point to a recognizer
bug, profile-palette omission, stochastic compile drop, or a need for helper
resurrection?

Before:

CS-006 added `operational_lifecycle_preservation` and found:

- pass=`11`
- partial=`5`
- ledger-only=`2`

The raw result was not enough to decide a repair layer.

Inspection:

The seven not-pass rows are:

| Fixture | Draw regime | Status | Source | Direct complete | Reading |
| --- | --- | --- | ---: | ---: | --- |
| `clinic_intake_corrections` | base status compile | partial | 6 | 5 | Mostly preserved; one source lifecycle line lacks a complete direct peer. |
| `grant_review_queue` | base status compile | ledger-only | 5 | 0 | Emits fragments such as supersession/closed/withdrawn without date-bound lifecycle/status units. |
| `library_preservation_queue` | actor/content compile | partial | 4 | 3 | Mostly preserved; one lifecycle line is not carried as a complete unit. |
| `warehouse_repair_log` | base status compile | partial | 6 | 3 | Uses domain-shaped predicates such as ticket/request rows; some are partial because date/state slots are absent. |
| `warehouse_repair_log` | palette compile | partial | 6 | 5 | Palette mostly works; one lifecycle line still lacks a complete direct unit. |
| `water_sample_docket` | base status compile | partial | 6 | 5 | Date/status surfaces exist, but one source lifecycle line is not preserved. |
| `water_sample_docket` | palette compile | ledger-only | 6 | 0 | Collapses to supersession/status fragments without complete lifecycle units. |

Interpretation:

This is not a helper problem. The source has lifecycle/status pressure and the
compiles usually see it. The problem is preservation shape:

- some regimes emit stable, complete lifecycle/status surfaces;
- some regimes emit nearby fragments without the slot set needed for queryable
  lifecycle resolution;
- some partial cases may also expose recognizer strictness around domain-shaped
  predicates, but the missing date/state slots are real enough that loosening
  the recognizer would blur the measurement.

Artifacts:

- `docs/data/compile_surface_stability/operational_record_status_stability_audit_20260515.md`
- `docs/data/compile_surface_stability/operational_record_status_stability_audit_20260515.json`

Verification:

- `python -m pytest tests\test_compile_surface_stability.py tests\test_compile_surface_invariants.py tests\test_lens_vocabulary_transfer.py tests\test_transition_delta_normalizer.py tests\test_query_transition_resolution_audit.py tests\test_operational_lifecycle_palette_audit.py tests\test_audit_helper_classes.py tests\test_audit_helper_usage.py tests\test_domain_bootstrap_file.py tests\test_domain_bootstrap_qa.py tests\test_domain_bootstrap_qa_batch.py -q` -> `286 passed`

Lesson:

The preservation contract is doing the right kind of work: it separates
source-visible lifecycle pressure from direct-surface preservation. The next
architecture move should not add helpers. It should either strengthen the
compile/profile requirement that operational records preserve complete
lifecycle units, or record these regime differences as stamp variance if the
instrument is otherwise frozen.

Next pressure:

Add one small compile/profile invariant, not a helper: when source text exposes
a repeated operational lifecycle with dates/statuses, at least one direct
surface family must preserve event or status units with subject, lifecycle
state/action, and temporal slot. Then rerun only the six operational probes
before considering any internal corpus stamp.

## CS-008 - Operational Parallel Lifecycle Invariant

Date: 2026-05-15

Question:

Can the operational lifecycle repair pressure be expressed as a small
compile/profile invariant rather than as a helper or fixture-specific patch?

Before:

CS-007 showed that the operational failures were mostly preservation-shape
failures. The source exposed repeated dated lifecycle/status lines, while some
draws preserved only fragments: supersession rows, closed/withdrawn labels, or
record ids without a complete subject/action-or-status/date unit.

Prediction:

The next instruction should be a compile-surface invariant, not a runtime
helper:

> Repeated lifecycle/status source lines require parallel preservation. For
> each stated dated lifecycle/status line, emit at least one complete direct
> unit that keeps subject, lifecycle state/action, and date/turn joinable.

That phrasing is fixture-free and applies to any permit, intake, docket, queue,
sample, ticket, accession, repair, or similar operational record source.

Intervention:

Updated `scripts/run_domain_bootstrap_file.py`:

- added an operational lifecycle preservation rule to
  `OPERATIONAL_RECORD_STATUS_CONTEXT_V1`;
- added a matching compile-surface invariant to
  `COMPILE_SURFACE_INVARIANT_CONTEXT_V1`;
- did not add helpers or new query-time repair logic.

Updated `tests/test_domain_bootstrap_file.py` so the invariant stays pinned in
both contexts.

After:

The architecture now has explicit language for the failure CS-007 exposed:
parallel source lifecycle lines should survive as parallel queryable direct
units, not as a bag of nearby status vocabulary.

Artifacts:

- `scripts/run_domain_bootstrap_file.py`
- `tests/test_domain_bootstrap_file.py`

Verification:

- `python -m pytest tests\test_domain_bootstrap_file.py tests\test_compile_surface_stability.py -q` -> `34 passed`

Lesson:

This is the kind of pre-stamp movement that should land before a baseline run:
it clarifies the instrument's contract without changing evaluation, adding
fixtures, or creating a helper bridge. A future stamp should include this
invariant because otherwise internal scores would mix real architecture state
with a known unexpressed preservation expectation.

Next pressure:

Rerun the six operational probes under the updated invariant when using OR or
local compile capacity is worthwhile. Compare only the preservation-contract
statuses first. If ledger-only/partial rows persist, classify them as remaining
compile variance or profile-palette limitations before broad internal
restamping.

## CS-009 - Operational Invariant Replay

Date: 2026-05-15

Question:

Does the new operational lifecycle invariant move the six unlike operational
probes into complete direct-surface preservation, or does it expose a sharper
pre-stamp pressure?

Before:

CS-008 added only compile/profile language. No helper, query repair, fixture
branch, or QA tuning was added. The expected result was not guaranteed uplift;
the expected result was a cleaner distinction between:

- complete lifecycle/status units;
- split rows where date and state survive but not as one queryable unit;
- true preservation gaps where the direct surface keeps nearby vocabulary but
  loses the slot set.

Prediction:

If the invariant is enough, the six-probe replay should move toward complete
direct units without increasing helper delivery. If not, the audit should name
which pressure remains without counting split fragments as success.

Intervention:

Ran a six-lane OpenRouter compile replay over the existing unlike operational
record/status probes using source-record ledger facts and the new invariant.
Then reran the compile-surface stability audit.

Also refined the audit recognizer to report `direct_split_count` for operational
lifecycle surfaces. A split surface is a date-only lifecycle/status row and a
state-only lifecycle/status row sharing the same subject. This is measurement
only: split rows remain non-passing because the direct compile did not preserve
subject, state/action, and date/turn in the same queryable unit.

After:

The replay compiled all six probes successfully.

| Probe | Contract status | Source signals | Complete | Partial | Split | Reading |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| `clinic_intake_corrections` | pass | 6 | 8 | 8 | 1 | Complete units exist; split rows are extra noise, not blocking. |
| `grant_review_queue` | ledger-only | 5 | 0 | 15 | 2 | Date and state partially survive as split surfaces; this is a normalization/preservation pressure, not a helper need. |
| `library_preservation_queue` | pass | 4 | 8 | 2 | 2 | Complete units exist despite nearby split fragments. |
| `permit_renewal_docket` | pass | 5 | 6 | 1 | 1 | Complete units exist. |
| `warehouse_repair_log` | ledger-only | 6 | 0 | 23 | 0 | Event dates and status fragments survive, but the audit finds no same-subject date/state join. |
| `water_sample_docket` | ledger-only | 6 | 0 | 15 | 0 | Event dates and result/status fragments survive, but not as dated lifecycle units. |

So the invariant did not close the operational lifecycle pressure. It made the
pressure more legible: one case is a split-surface candidate, while two cases
are still true preservation failures under the current direct predicate palette.

Artifacts:

- `docs/data/compile_surface_stability/operational_lifecycle_invariant_replay_compile_summary_20260515.md`
- `docs/data/compile_surface_stability/operational_lifecycle_invariant_replay_compile_summary_20260515.json`
- `docs/data/compile_surface_stability/operational_lifecycle_invariant_replay_stability_audit_20260515.md`
- `docs/data/compile_surface_stability/operational_lifecycle_invariant_replay_stability_audit_20260515.json`

Verification:

- `python -m pytest tests\test_compile_surface_stability.py -q` -> `5 passed`
- `python -m pytest tests\test_domain_bootstrap_file.py tests\test_compile_surface_stability.py -q` -> `35 passed`

Lesson:

This is exactly why the stamp should wait. A broad internal rescan right now
would mix a known preservation-contract issue with the baseline score. The
architecture has not learned fixture vocabulary, but it has exposed a real
compile-surface weakness: operational status timelines are sometimes preserved
as nearby fragments instead of durable, slot-complete direct rows.

Next pressure:

Do not add helpers. Split-surface cases may belong to a strict deterministic
normalizer if subject/date/state rows are joinable without guessing. The
warehouse and water cases need profile-palette or compile-invariant pressure
because the date slot is absent from the status/result surfaces. The next small
job should inspect candidate predicate palette selection for those two shapes
and decide whether a generic `record_lifecycle_event` / `record_status_phase`
surface should be required whenever source lifecycle lines are repeated.

## CS-010 - Two-Miss Palette Loophole Replay

Date: 2026-05-15

Question:

Were the two remaining operational misses caused by a prompt loophole where a
domain-specific status/result predicate was treated as equivalent to the
canonical lifecycle palette even though it dropped the temporal/event slot?

Before:

CS-009 showed two true preservation misses after the invariant replay. Both had
nearby date/event rows and nearby status/result rows, but no complete
subject/state-or-action/date unit.

Prediction:

If the loophole is mostly wording, then telling the compiler that a
domain-specific two-slot status/result predicate is not stricter when it drops
date/event/actor/governed-subject slots should push the two probes toward
canonical complete rows. If not, the issue belongs below prompt wording: profile
palette enforcement, candidate predicate admission, or deterministic
normalization over strictly joinable split surfaces.

Intervention:

Updated compile guidance only:

- the operational lifecycle palette construction rule now says a
  domain-specific status/result predicate is not stricter if it drops a stated
  date, event, actor, or governed-subject slot;
- the compile-surface invariant now rejects two-slot status/result predicates
  as satisfying repeated lifecycle/status lines when they omit the date/event
  join.

The audit recognizer was also refined to report split lifecycle evidence when a
generic temporal carrier such as `event_date` shares a subject with a state row.
This still does not pass the contract; it only separates split-but-joinable
evidence from true missing preservation.

After:

Ran a two-fixture OpenRouter replay for the two true misses.

| Probe | Candidate predicates | Contract status | Complete | Partial | Split | Reading |
| --- | ---: | --- | ---: | ---: | ---: | --- |
| `warehouse_repair_log` | 16 | ledger-only | 0 | 29 | 2 | Some date/state rows share subject, but the compiler still chose split domain predicates instead of complete lifecycle units. |
| `water_sample_docket` | 16 | ledger-only | 0 | 24 | 0 | The compiler kept event/result/status surfaces separated with no same-subject lifecycle unit. |

The wording improvement did not close the pressure. It increased nearby
fragments and made the shape clearer: warehouse has a possible deterministic
split-normalization path, while water remains a stronger palette/admission
failure.

Artifacts:

- `docs/data/compile_surface_stability/operational_lifecycle_two_miss_palette_replay_compile_summary_20260515.md`
- `docs/data/compile_surface_stability/operational_lifecycle_two_miss_palette_replay_compile_summary_20260515.json`
- `docs/data/compile_surface_stability/operational_lifecycle_two_miss_palette_replay_stability_audit_20260515.md`
- `docs/data/compile_surface_stability/operational_lifecycle_two_miss_palette_replay_stability_audit_20260515.json`

Verification:

- `python -m pytest tests\test_compile_surface_stability.py tests\test_domain_bootstrap_file.py -q` -> `36 passed`

Lesson:

This is no longer a helper-removal issue and no longer simple prompt polish.
The architecture needs a clearer layer boundary:

- deterministic normalization may compose split date/state rows only when the
  join is explicit and subject-preserving;
- compile/profile admission should require canonical lifecycle surfaces when
  the source states repeated dated statuses and the proposed domain predicates
  do not preserve the slot contract.

Next pressure:

Design the smallest profile/admission check that can mark a candidate predicate
palette as shallow when repeated lifecycle source lines are present but no
allowed predicate can carry subject, state/action, and date/event together. Do
not broaden QA helpers to patch this. The failure is upstream of query-time
support.

## CS-011 - Shallow Lifecycle Palette Diagnostic

Date: 2026-05-15

Question:

Can the operational lifecycle palette audit detect the upstream failure before
QA: repeated lifecycle/status source pressure with no candidate predicate able
to carry subject, status/result, and date together?

Before:

CS-010 showed the two-miss replay still produced ledger-only preservation
status. The compile outputs had nearby predicates, but their palette was
shallow: two-slot status/result predicates plus separate date/event predicates.
That shape is upstream of query support because the required direct row shape
was never offered as a candidate surface.

Prediction:

A useful diagnostic should:

- flag palettes that offer only split status/date surfaces;
- not flag palettes that have a legitimate complete status-at-date predicate;
- stay generic enough to apply to permits, queues, tickets, samples, dockets,
  applications, records, and similar operational logs without fixture terms.

Intervention:

Extended `scripts/audit_operational_lifecycle_palette.py` with a
`shallow_lifecycle_palette` finding. It fires when source-record text contains
repeated lifecycle/status pressure and the parsed candidate predicate palette
has no candidate with subject, status/result, and date/source slots, or one of
the canonical lifecycle predicates.

The diagnostic is admission-side measurement only. It does not repair facts and
does not loosen QA support.

After:

Six-probe invariant replay:

- `shallow_lifecycle_palette`: 3 findings.
- Flagged: grant queue, warehouse repair, water sample.
- Not flagged: clinic intake, library preservation, permit renewal.
- The permit case was an important calibration: `permit_status_at/3` with
  `permit_file`, `date`, and `status` is a valid complete candidate, so the
  audit no longer treats it as shallow.

Two-miss replay:

- `warehouse_repair_log`: shallow palette plus alias pressure.
- `water_sample_docket`: shallow palette plus initial phase missing.

Artifacts:

- `docs/data/lens_vocabulary_audit/operational_lifecycle_invariant_replay_palette_shape_audit_20260515.md`
- `docs/data/lens_vocabulary_audit/operational_lifecycle_invariant_replay_palette_shape_audit_20260515.json`
- `docs/data/lens_vocabulary_audit/operational_lifecycle_two_miss_palette_shape_audit_20260515.md`
- `docs/data/lens_vocabulary_audit/operational_lifecycle_two_miss_palette_shape_audit_20260515.json`

Verification:

- `python -m pytest tests\test_operational_lifecycle_palette_audit.py tests\test_compile_surface_stability.py -q` -> `15 passed`

Lesson:

The architecture now has a clearer pre-stamp gate: not merely "did the direct
compile preserve complete rows?" but "did the candidate palette even contain a
row shape capable of preserving them?" This is the new layer taking shape:
profile/admission stability before compile preservation, before deterministic
normalization, before QA.

Next pressure:

Use this diagnostic to decide the next repair surface. If the candidate palette
is shallow, strengthen profile/admission constraints. If the palette is complete
but emitted facts are split, deterministic normalization may be valid only when
the join is explicit. If both palette and facts are complete, any residual miss
belongs downstream in selector/query planning.
