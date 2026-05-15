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
