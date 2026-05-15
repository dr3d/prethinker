# Query Transition Predicate Palette Diff

Date: 2026-05-15

Scope:

- Old interval miss: temporal-status permit probe.
- Fresh interval exact: access-badge interval probe.
- Old initial-status miss: operational water-sample docket probe.
- Fresh initial-status exact: repair-ticket intake probe.

## Interval-Scoped Status

Old miss emitted separate facts:

- `permit_status(Entity, valid)`
- `permit_status(Entity, expired)`
- `permit_scope(Entity, Scope)`
- `effective_from(Entity, Start)`
- `valid_until(Entity, End)`
- `status_changed_at(Entity, ChangeTime)`

The query plan retrieved status and boundaries but did not retrieve the scope
row. The reference answer required status plus scope during the active interval.

Fresh exact emitted separate facts too:

- `access_level(Entity, supervised)`
- `grants_access_to(Entity, Location)`
- `valid_from(Entity, Start)`
- `valid_until(Entity, End)`
- `status_changed_to(Entity, inactive)`

The QA row was exact because the judge accepted the returned core status
`supervised` as support for the status question. It did not prove that the
query layer reliably binds status plus scope in one answer.

Interpretation:

Simple interval status is inside the set. Interval status plus scope remains an
open resolution edge. The next probe should ask explicitly for status and scope
so a core-status-only answer cannot pass by judge generosity.

## Initial Status

Old miss embedded the initial status inside a filed event sentence. The compile
emitted filing and final/current status rows, but no direct initial-status row:

- `recorded_event(Event, Date, Actor, filed, Record)`
- `docket_status(Record, completed_below_threshold)`
- source text containing the initial status phrase

Fresh exact used explicit initial-status wording. The compile emitted a direct
answer-bearing row:

- `initial_status(Entity, Status)`
- plus filing, assignment, status-change, and closure rows.

Interpretation:

Initial status is inside the set when the source states it as an explicit
initial-status proposition. The unresolved edge is the denser filing phrase:
"filed X with status Y." That should become a focused hard probe before any
compile guidance changes.

## Layer Read

These two comparisons say the same thing in different clothes:

- The axes exist.
- Simple forms are interior.
- Dense event/status/scope forms remain boundary.

Next pressure:

Build two hard probes:

- status plus scope during an interval, where both pieces are required;
- filed/intake event with status value embedded in the event phrase, without
  saying "initial status was".

Run compile and no-helper QA. Only repair if the hard probes reproduce the old
miss shape.
