# Frontier Sweep - 2026-04-17

This note captures the latest local health check across the repo's main active frontiers after the longform full-story recovery pass and the reserved `at_step/2` hardening work.

## Overall Read

- Safety gate is green at `105 passed`.
- Stable Blocksworld lane is holding.
- Mid strict narrative pack is now pipeline-green across `full`, `paragraph`, and `line`, and `full` mode is materially better than it was before this batch.
- Upper-mid strict narrative pack remains strong across all three modes.
- Glitch control lane is structurally healthier after the reserved `at_step/2` fix: the old nested/non-temporal `at_step` misuse did not reappear in the new KB.
- One interrogator-side temporal experiment was tried and rejected in this cycle because it hurt the stronger narrative lanes; the current state below reflects the reverted, better-performing path.

## Stable Lane

### Blocksworld Guarded Lane

Source artifacts:
- `tmp/blocksworld_lane_regressioncheck_20260417.summary.json`
- `tmp/blocksworld_lane_regressioncheck_20260417.md`

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
- `tmp/mid_pack_general_strict_temporal_recovery_fullfix2_20260417.summary.json`

Aggregate:
- pipeline pass count: `3/3`
- avg coverage: `0.85`
- avg precision: `0.896667`
- avg exam pass rate: `0.85`
- avg temporal exam pass rate: `0.666667`
- best final score: `0.9284`

Per mode:
- `full`: coverage `0.85`, precision `0.85`, exam `17/20`, temporal `0.0`, final `0.843`
- `paragraph`: coverage `0.85`, precision `0.92`, exam `17/20`, temporal `1.0`, final `0.9284`
- `line`: coverage `0.85`, precision `0.92`, exam `17/20`, temporal `1.0`, final `0.9284`

Read: this is the biggest concrete gain of the batch. Mid `full` moved from a technically-passing but semantically weak `0/20` exam state to a useful `17/20`, while the split lanes stayed strong.

### Upper-Mid Strict Narrative Pack

Source artifact:
- `tmp/upper_mid_pack_general_strict_temporal_regressioncheck2_20260417.summary.json`

Aggregate:
- pipeline pass count: `3/3`
- avg coverage: `0.896667`
- avg precision: `0.893333`
- avg exam pass rate: `0.933333`
- avg temporal exam pass rate: `0.916667`
- best final score: `0.956`

Per mode:
- `full`: coverage `0.85`, precision `0.92`, exam `16/20`, temporal `0.75`, final `0.9039`
- `paragraph`: coverage `0.92`, precision `0.88`, exam `20/20`, temporal `1.0`, final `0.956`
- `line`: coverage `0.92`, precision `0.88`, exam `20/20`, temporal `1.0`, final `0.956`

Read: upper-mid remains healthy and did not lose pipeline stability while the runtime changed under it. The strongest signal is still in the split lanes.

## Glitch Control

Source artifacts:
- `tmp/glitch_frontier_recovery_temporal2_20260417.summary.json`
- `kb_store/raw_glitch_frontier_recovery_temporal2_20260417_line_temporal_20260417_185227/kb.pl`

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

Read: the structural `at_step/2` bug is fixed in this control lane, but temporal reasoning quality here is still weak and remains an open frontier.

## What This Means

- The repo is holding together across the main fronts.
- The stable lane remains stable under stricter gates.
- The most important concrete improvement in this batch is longform `full`-mode recovery on the mid pack.
- The most important honesty rule remains: do not treat `pipeline passed` as identical to `semantic success`, especially when temporal coverage falls short.

## Recommended Next Step

Refresh the outward-facing status docs to match this local sweep, especially the move to `105 passed`, the mid `full` recovery, and the current split-vs-full narrative distinctions.
