# Assignment Scope Probe Findings

Date: 2026-05-15

Scope:

- Three unlike assignment-scope probes.
- No-helper QA.
- One redraw for the only not-exact fixture.

## Initial Run

Compile:

- fixtures: `3`
- parsed OK: `3`
- candidate predicates: `25`
- admitted/skipped: `80 / 6`

QA:

- questions: `15`
- exact/partial/miss: `14 / 0 / 1`
- helper rows: `0`

The one miss was a second-assignment row in the equipment service probe. The
compile emitted the first assignment but did not bind the second assignee to
the second task. The source text and task vocabulary contained the missing
task, but there was no structured assignee-task row for that person.

## Redraw

A fresh compile draw for the same equipment fixture emitted task rows that
bound both assignees:

- `task_assigned_to(task_fuel, theo_aran, 2026_12_11t09_00)`
- `task_assigned_to(task_voltage, priya_noor, 2026_12_12)`

No-helper QA on the redraw:

- questions: `5`
- exact/partial/miss: `5 / 0 / 0`
- helper rows: `0`

## Interpretation

Assignment scope is not ready for an architecture repair from this evidence.
The axis is present: when the compile emits assignee-task rows, the query layer
answers cleanly without helper rows. The first miss is a compile stability
variant where one of two parallel assignments was dropped.

Next pressure:

Do not add assignment-scope helpers. If this pattern recurs, treat it as a
compile-surface stability question for repeated parallel assignments:
the invariant is "each assignment event should bind assignee, task/scope, and
time when the source exposes them." A repair would belong in compile-surface
invariants, not the query companion layer.
