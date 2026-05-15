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
