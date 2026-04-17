# Frontier Sweep - 2026-04-17

This note captures a broad local health check across the repo's main active frontiers after the latest parser/runtime hardening work.

## Overall Read

- Safety gate is green at `100 passed`.
- Stable Blocksworld lane is holding.
- Mid strict narrative pack is now pipeline-green across `full`, `paragraph`, and `line`, but only the split lanes look semantically convincing.
- Upper-mid strict narrative pack is in the best shape it has been locally: all three modes passed, with strong exam performance.
- Glitch control lane is structurally healthier after the reserved `at_step/2` fix: the old nested/non-temporal `at_step` misuse did not reappear in the new KB.

## Stable Lane

### Blocksworld Guarded Lane

Source artifacts:
- `tmp/blocksworld_lane_sweep_20260417.summary.json`
- `tmp/blocksworld_lane_sweep_20260417.md`

Observed:
- symbolic solve/replay: `20/20`
- pilot pipeline pass: `8/8`
- avg init predicate hit ratio: `0.458334`
- avg goal predicate hit ratio: `0.458334`
- zero-hit cases: `0`

Gate status:
- `max_zero_hit=0`: pass
- `min_avg_init_hit=0.45`: pass
- `min_avg_goal_hit=0.45`: pass

Read: the deterministic-first baseline is still on the highway.

## Narrative Frontier

### Mid Strict Narrative Pack

Source artifact:
- `tmp/mid_pack_general_strict_temporal_sweep_20260417.summary.json`

Aggregate:
- pipeline pass count: `3/3`
- avg coverage: `0.783333`
- avg precision: `0.896667`
- avg exam pass rate: `0.55`
- avg temporal exam pass rate: `0.583333`
- best final score: `0.9284`

Per mode:
- `full`: coverage `0.65`, precision `0.85`, exam `0/20`, temporal `0.0`, final `0.68`
- `paragraph`: coverage `0.85`, precision `0.92`, exam `17/20`, temporal `1.0`, final `0.9284`
- `line`: coverage `0.85`, precision `0.92`, exam `16/20`, temporal `0.75`, final `0.9039`

Read: this pack is no longer operationally fragile, but `full` mode still overstates health if read naively. The split lanes are the trustworthy signal.

### Upper-Mid Strict Narrative Pack

Source artifact:
- `tmp/upper_mid_pack_general_strict_temporal_sweep_20260417.summary.json`

Aggregate:
- pipeline pass count: `3/3`
- avg coverage: `0.896667`
- avg precision: `0.943333`
- avg exam pass rate: `0.933333`
- avg temporal exam pass rate: `0.933333`
- best final score: `0.967`

Per mode:
- `full`: coverage `0.85`, precision `1.0`, exam `20/20`, temporal `1.0`, final `0.967`
- `paragraph`: coverage `0.92`, precision `0.88`, exam `20/20`, temporal `1.0`, final `0.956`
- `line`: coverage `0.92`, precision `0.95`, exam `16/20`, temporal `0.8`, final `0.9294`

Read: upper-mid is the healthiest narrative frontier right now. This is a real improvement, not just a pipeline technicality.

## Glitch Control

Source artifacts:
- `tmp/glitch_frontier_sweep_20260417.summary.json`
- `kb_store/raw_glitch_frontier_sweep_20260417_line_temporal_20260417_181829/kb.pl`

Observed:
- pipeline pass count: `1/1`
- parse failures: `0`
- apply failures: `0`
- clarification requests: `0`
- coverage: `0.85`
- precision: `0.92`
- exam: `8/14`
- temporal exam pass rate: `0.0`
- final score: `0.8194`

Structural check:
- no `at_step(<number>, at_step(...))` nested clauses found
- no bare non-temporal `at_step(entity, location)` facts found
- malformed `at_step/2` usage that previously polluted this lane did not recur

Read: the structural `at_step/2` bug is fixed in this control lane, but temporal reasoning quality here is still weak.

## What This Means

- The repo is holding together across the main fronts.
- The stable lane remains stable under stricter gates.
- The narrative frontier is no longer drifting blindly; both major packs are operationally passable, and upper-mid is strong.
- The most important current honesty rule remains: do not treat `pipeline passed` as identical to `semantic success`, especially for `full` narrative mode.

## Recommended Next Step

Refresh the outward-facing status docs to match this local sweep, especially the move from `92 passed` to `100 passed` and the stronger current narrative picture.
