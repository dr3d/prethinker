# Selector Guard Audit Discipline

Prethinker is not going to hide selector complexity inside parameterized guard
families just to make the guard count look smaller. That would make the system
less inspectable while preserving the same underlying sprawl.

The current discipline is:

```text
keep guards explicit
classify them by family
track their audit status
merge exact duplicates
retire scars when upstream surfaces improve
```

## Why Not Parameterize Now

The seven guard families are useful semantic categories. They are not yet stable
enough to become seven large private rule engines.

A parameterized family can hide:

- a large enum table;
- fixture-shaped keyword lists;
- thresholds tuned to one model lane;
- branches no one can tie back to a birth row;
- guards that should have retired when a better compile surface landed.

Explicit guards are uglier, but they are auditable. Each one can be pointed at a
source line, replayed against the row that created it, and either promoted,
merged, or deleted.

## Audit Statuses

`transfer_guard`: replay evidence shows the guard helps more than one fixture or
domain without known regression.

`candidate_guard`: the default state. The guard fixed a measured row-level
failure, but transfer evidence is still pending.

`merge_candidate`: the guard has an exact or near duplicate. Inspect branch
conditions and replay the birth rows before merging.

`scar_guard`: the guard names a local accident, or it has been made unnecessary
by a stronger compile lens, deterministic pinboard, helper predicate, or query
surface.

## Retirement Conditions

Every guard should eventually answer this question:

```text
What upstream improvement would make this guard unnecessary?
```

Common answers:

- deterministic identifier/source pinboards preserve exact labels;
- helpers answer arithmetic, counts, intervals, or propagation directly;
- compile lenses admit explicit status, role, ownership, or authority surfaces;
- structural selector scoring learns to penalize broad row-volume traps;
- query planners retrieve the correct surface without selector intervention.

If a guard has no plausible retirement condition, it may be genuine permanent
selector doctrine. That should be rare and earned.

## Retirement Buckets

The audit ledger now assigns each guard a retirement bucket and priority. This
is not a deletion verdict; it is a replay queue.

- `helper_or_constraint_substrate`: arithmetic, count, interval, timestamp,
  deadline, clock-state, or threshold guards that should be retested after
  helper/constraint work lands.
- `pinboard_or_source_addressability`: identifier, source-id, printed label, or
  provenance guards that should be retested after deterministic source
  pinboards improve.
- `compile_surface`: status, role, authority, custody, ownership, possession, or
  current-state guards that should retire only when the compile admits the
  direct surface consistently.
- `selector_scoring_or_surface_penalty`: row-volume and broad-surface guards
  that may retire if structural scoring learns to penalize tempting but noisy
  candidate modes.
- `manual_audit`: guards whose retirement condition is not yet obvious from the
  reason string alone.

High-priority retirement slices are the guards most likely to be affected by
current helper, constraint, and pinboard work. They are the first guards to
replay without after a substrate improvement, not the first guards to delete.

## Health Signal

The healthy long-term shape is not a permanently growing guard list.

```text
lens count grows slowly
family count holds near 7-8
guard count peaks
merge pressure removes duplicates
retirement pressure removes scars
```

If the guard count keeps growing linearly with fixture rows, the architecture is
collecting scars. If it peaks and starts shrinking while scores hold or improve,
the instrument is learning upstream instead of memorizing downstream.

See [SELECTOR_GUARD_FAMILY_ROLLUP.md](https://github.com/dr3d/prethinker/blob/main/docs/SELECTOR_GUARD_FAMILY_ROLLUP.md)
for family pressure and
[SELECTOR_GUARD_LEDGER.md](https://github.com/dr3d/prethinker/blob/main/docs/SELECTOR_GUARD_LEDGER.md)
for the current audit scaffold.
