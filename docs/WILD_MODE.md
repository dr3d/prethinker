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

## Live Random HN Harness (Structured, Not Ad-Hoc)

To move out of ad-hoc testing, use the live random harness:

- script: `scripts/run_hn_random_ingest.py`
- flow:
  - samples random HN stories from feed (`top/new/best`)
  - harvests bounded OP+comment packets (BFS depth + comment caps)
  - auto-builds turnsets and runnable scenarios
  - runs each through `kb_pipeline.py`
  - writes per-thread reports and aggregate summary

Recommended baseline profile:

- parser: `qwen3.5:9b`
- CE answer model: same family (`qwen3.5:9b`)
- CE settings: `clarification_eagerness=0.35`, `max_clarification_rounds=2`

Optional low-VRAM profile:

- CE sidecar: explicit smaller model (for example `qwen2.5:4b`) via `--ce-mode explicit --clarification-answer-model ...`

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

From CE envelope sweeps on `2026-04-13`:

- aggressive CE wall (`ce=0.90`, rounds `3`):
  - `excursion_frontier_v2_full`: `2/12` (`16.7%`)
  - `excursion_failure_promotions_v1`: `0/3` (`0.0%`)
  - failure mode: escalation/clarification pressure can suppress useful commits
- balanced CE (`ce=0.55`, rounds `2`):
  - `excursion_failure_promotions_v1`: `3/3` (`100%`)
  - tradeoff: safer commits, but low clarification-route exercise in those specific rungs
- typo/pronoun stress under higher CE (`ce=0.70`):
  - `frontier_language_width_v6`: `6/16` (`37.5%`)
  - confirms this lane still has severe brittleness on bare model under pressure

From MITM clarification-loop runs (`2026-04-13`):

- `rung460_ce85_mitm`: fallback sidecar resolved `4/4` pending clarification stalls (grade `A`)
- `hn_signal_v3_ce85_mitm`: unresolved pending clarifications remained (`2/15` turns pending, fallback resolved `0/4`, grade `D`)
- interpretation: the CE/Q&A route works, but can still dead-end on underspecified user-identity/predicate-canonicalization questions

From latest source harvest:

- new harder pack published: `HN_MIDGROUND_PACK_V3.md`
- six additional HN threads with deeper BFS sampling (`max_comments=140`, `max_depth=4`)
- ready-to-run turnsets expanded to OP + 14 comments (15-turn stress format)

From first live-random structured harness run (`2026-04-14T13:34:31Z`):

- run dir: `tmp/runs/hn_random_ingest/hn_random_top_20260414_133343`
- requested/selected: `2/2` random top-feed stories
- result: `2/2` pipeline runs completed with `0` parse failures and `0` apply failures
- note: commit density was low on one thread (`stage_provisionally` dominated), which is now measurable and can be promoted into targeted regression rungs

## What Counts As Progress

Progress is not just a higher pass rate.
Progress means:

- fewer repeated failure classes
- clearer mapping from each failure class to a new rung and fix
- higher retention of intended relations under noisy discourse
- consistent KB state under correction/retraction pressure

## Linked Artifacts

- excursion source pack: `stories/excursions/HN_MIDGROUND_PACK_V2.md`
- harder source pack: `stories/excursions/HN_MIDGROUND_PACK_V3.md`
- session log entry: `SESSIONS.md` (Session 33)
- failure isolation note: `docs/WILD_FAILURE_ISOLATION.md`
