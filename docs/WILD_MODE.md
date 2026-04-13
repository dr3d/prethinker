# Out In The Wild: Frontier Excursion Mode

Last updated: 2026-04-13

## What This Mode Is

`Out in the Wild` mode is our realism lane.
Instead of only synthetic ladder stories, we ingest real public discourse (Hacker News, Reddit, and cooperative formal-policy transcripts), convert it into bounded turnsets, and test whether Prethinker can still compile facts, rules, corrections, and queries into deterministic KB updates.

This is the anti-overfitting lane: we test language as it is actually spoken, not only as we wish it were spoken.

## Why We Are Doing It

The ladder can look clean while real language remains messy.
Wild mode exists to answer one hard question:

Can the Governed Intent Compiler still hold structure when language gets noisy, adversarial, and context-heavy?

## Current Process (When You Say `GO`)

1. Harvest source threads/transcripts into a source bank.
2. Build bounded turnsets (manageable size, meaningful semantic density).
3. Run full excursion tracks on bare `qwen3.5:9b` (prompt supplied at runtime).
4. Grade by validation results and turn-level telemetry.
5. Promote repeated failure patterns into new `rung_*` scenarios.
6. Re-run to confirm the new rung closes a real blind spot.

## What We Learned So Far

From `track_excursion_frontier_v2_full` run `2026-04-13T20:41:10Z`:

- overall: `5/12` passed (`41.67%`)
- cooperative lane and wild lane both expose real failure structure, but with different failure shapes
- most misses are not random; they cluster into repeatable linguistic patterns we can target

From latest HN midground harvest (`stories/excursions/hn_midground_v2`):

- we now have six fresh real-thread snapshot packs + generated turnsets
- smoke check on `hn_docker_spain_block_turnset_v1` committed `4/4` turns (readiness `C`) and gives a stable starting harness for deeper runs

System prompt execution sanity:

- recent excursion runs show `system_prompt_sources.double_source_active=false` in run metadata
- this indicates no runtime double-system-prompt collision in those runs

## What Counts As Progress

Progress is not just a higher pass rate.
Progress means:

- fewer repeated failure classes
- clearer mapping from each failure class to a new rung and fix
- higher retention of intended relations under noisy discourse
- consistent KB state under correction/retraction pressure

## Linked Artifacts

- excursion source pack: `stories/excursions/HN_MIDGROUND_PACK_V2.md`
- session log entry: `SESSIONS.md` (Session 32)
- failure isolation note: `docs/WILD_FAILURE_ISOLATION.md`
