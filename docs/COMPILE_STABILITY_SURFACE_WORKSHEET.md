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
