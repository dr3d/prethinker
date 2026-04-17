# Deterministic English->Logic Compilation: Progress Note

Date: 2026-04-16

## Update: 2026-04-17 (Blocksworld Lane)

We completed a focused parser upgrade on the strict Blocksworld lane to improve single-turn multi-fact extraction while preserving deterministic safety.

- What changed
  - split-extraction prompt guidance now permits multiple independent `assert_fact` clauses in one utterance.
  - logic-only refine path now expands a multi-clause `logic_string` into canonical fact batches.
  - strict-registry salvage guard now drops only out-of-registry facts from mixed batches and keeps valid facts commit-capable.

- Net result on strict pilot lanes
  - `12-case strict`: pass `12/12 -> 12/12`; avg init hit `0.4375 -> 0.5139`; avg goal hit `0.5000 -> 0.5139`.
  - `40-case strict`: pass `40/40 -> 40/40`; avg init hit `0.3688 -> 0.6271`; avg goal hit `0.3250 -> 0.5833`.
  - zero-hit subset on `40-case strict`: `4 -> 0`.

- Interpretation
  - this is a real extraction-quality lift without sacrificing strict-registry stability.
  - remaining ceiling is concentrated in a small recurring zero-hit subset (4 case IDs), so next work should be targeted diagnostics instead of broad prompt churn.

Reference: `docs/reports/BLOCKSWORLD_MULTI_FACT_UPGRADE_2026-04-17.md`

## Update: 2026-04-17 (Gated Baseline + Pack Corrections)

We added an explicit zero-hit regression gate to the Blocksworld lane runner and validated both pass/fail behavior.

- What changed
  - `scripts/run_blocksworld_lane.py` now accepts `--max-zero-hit`.
  - run summary JSON/MD now records gate status under `gates.zero_hit` (`enabled`, `threshold`, `observed`, `passed`, `reason`).
  - runner exits non-zero when `zero_hit_case_count` exceeds threshold.

- Gate verification
  - pass-path smoke: `max-zero-hit=0`, observed `0`, gate `passed`.
  - forced fail-path smoke (invalid model): observed `1`, gate `failed`, process exit `10`.

- New reproducible gated baseline (strict Blocksworld, MF3 prompt)
  - run A: `tmp/blocksworld_lane_strict_mf3_gate_20260417.summary.json`
  - run B: `tmp/blocksworld_lane_strict_mf3_gate_r2_20260417.summary.json`
  - both runs identical on key metrics:
    - symbolic harness solve/replay: `20/20` (`solve_rate=1.0`)
    - prethinker pilot pass: `8/8`
    - avg init predicate hit: `0.458334`
    - avg goal predicate hit: `0.458334`
    - zero-hit cases: `0` (gate pass at threshold `0`)

- Mid/upper-mid narrative pack correction (configuration sanity)
  - we discovered an invalid comparison run where narrative packs were executed with the Blocksworld predicate registry; that run is now treated as config-mismatch diagnostic, not quality signal.
  - corrected reruns used general registry path + strict flag:
    - `tmp/mid_pack_general_strict_temporal_20260417.summary.json`
      - `run_count=3`, `pipeline_pass=3`, `best_final_score=0.6452`
    - `tmp/upper_mid_pack_general_strict_temporal_20260417.summary.json`
      - `run_count=3`, `pipeline_pass=3`, `best_final_score=0.8718`
  - important caveat: current `modelfiles/predicate_registry.json` contains an empty canonical set (`entries=0`), so "strict" here is effectively unconstrained until registry population is completed.

References:
- `docs/reports/BLOCKSWORLD_LANE_STRICT_MF3_GATE_2026-04-17.md`
- `docs/reports/BLOCKSWORLD_LANE_STRICT_MF3_GATE_R2_2026-04-17.md`
- `docs/reports/MID_PACK_GENERAL_STRICT_TEMPORAL_2026-04-17.md`
- `docs/reports/UPPER_MID_PACK_GENERAL_STRICT_TEMPORAL_2026-04-17.md`

## Challenge Glossary (External Readers)

To make the scorecard readable outside the core team, here is what the shorthand names mean:

- `Ledger` / `The Ledger at Calder's Reach`
  - A deliberately dense long-form narrative with many entities, aliases, role changes, ownership transfers, and rule-triggered state changes over time. It is our current hardest public stress case for raw English ingestion.
- `Glitch` / `The Glitch in the Airlock`
  - A medium-complexity narrative stress test (sci-fi adaptation of a structured fairy-tale pattern) used as a control story for stability and regression checks.
- `ledger_reach_boss`
  - A focused stress-cycle label for the hardest active Ledger lane. This is the "boss-level" gate run we use to verify that severe narrative ingestion still passes.
- `full | paragraph | line` split modes
  - Packaging modes for raw story ingestion: `full` (entire story as one input), `paragraph` (paragraph chunks), `line` (line-by-line chunks).
- `temporal dual-write`
  - Runtime mode that writes both plain facts and step-indexed timeline facts (e.g., `fact(...)` and `at_step(T, fact(...))`) to preserve event order.
- `heuristic_fallback` (fact audit status)
  - A transparent fallback used when the primary fact-audit model output cannot be parsed as valid JSON; coverage/precision are then estimated from exam performance and load-error signals.
- `Agent54`
  - Our delegated GPT-5.4 subagent used for sidecar analysis and parallel research/pack generation tasks.

## Current Scorecard (Latest)

Primary fronts and where we stand after the latest boss cycle:

- Front: severe narrative ingest (`Ledger`, raw input, `paragraph + temporal`)
  - pipeline pass: `1/1`
  - parser failures: `0`
  - apply failures: `0`
  - clarification requests: `0`
  - audit coverage: `0.800` (`heuristic_fallback`)
  - audit precision: `0.800` (`heuristic_fallback`)
  - exam pass: `16/20` (`0.800`)
- Front: severe narrative stress gate (`ledger_reach_boss`)
  - run matrix: `paragraph x temporal(on)`
  - pipeline pass: `1/1`
  - avg coverage: `0.800`
  - avg precision: `0.800`
  - avg exam pass: `0.800`
  - avg temporal exam pass: `0.000` (exam emitted no temporal questions in this run)
- Front: control regression check (`Glitch`, raw input, `line + temporal`)
  - pipeline pass: `passed`
  - parser failures: `0`
  - apply failures: `0`
  - clarification requests: `0`
  - clauses written: `16`
  - audit coverage: `0.850`
  - audit precision: `0.920`
  - exam pass: `14/20` (`0.700`)
  - temporal exam pass: `11/17` (`0.647`)
- Front: runtime/engine confidence
  - no new runtime regressions observed in this cycle
  - full engine suite was not rerun in this specific pass (last green remains from prior cycle)

## Key Wins Achieved

1. Ledger lane moved from unstable to stable in the hardest current profile.
- Previous hard-story matrix on 2026-04-15 showed `2/6` pipeline pass across `full|paragraph|line x temporal(off|on)`.
- Current focused lane now passes cleanly with `parse=0`, `apply=0`, and no clarification deadlock.

2. Clarification deadlocks were reduced in permissive-mode ingest.
- Added guards so non-strict runs do not block on "canonical predicate naming" meta-questions.
- Added unsafe-mapping downgrade so clearly wrong schema substitutions are staged as non-mutating instead of being forced into bad facts.

3. Narrative routing and pre-normalization became more robust.
- Hardened rule-cue detection so incidental narrative `if` phrasing is less likely to force `assert_rule` misrouting.
- Improved `while` handling in pre-normalization so subordinate clauses are less likely to be malformed.

4. Fact-audit reporting is now resilient when model JSON parse fails.
- `scripts/kb_interrogator.py` now emits `heuristic_fallback` audit instead of hard-zeroing coverage/precision to `0.0/0.0`.
- This keeps reports usable and honest about failure mode.

5. New reusable challenge packs were created via Agent54.
- `tmp/story_pack_mid.md` (moderate density, 46 Q/A)
- `tmp/story_pack_upper_mid.md` (upper-mid density, 52 Q/A)

## Technical Changes Shipped In This Cycle

- `kb_pipeline.py`
  - route-cue hardening for rule detection
  - clarification normalization/policy hardening
  - predicate-naming clarification guard
  - unsafe predicate-mapping downgrade guard
  - fact-batch salvage improvements
  - safer `while` narrative rewrite behavior
- `scripts/kb_interrogator.py`
  - fact-audit fallback mode (`heuristic_fallback`) when primary audit JSON is unparseable

## Latest Artifacts (2026-04-16)

- Ledger focused pass
  - `tmp/raw_ledger_reach_paragraph_temporal_routefix5_20260416.pipeline.json`
  - `tmp/raw_ledger_reach_paragraph_temporal_routefix5_20260416.interrogator.v2.json`
  - `tmp/raw_ledger_reach_paragraph_temporal_routefix5_20260416.interrogator.v2.md`
- Ledger boss stress summary
  - `tmp/ledger_reach_boss_stress_20260416_001539.summary.json`
  - `tmp/ledger_reach_boss_stress_20260416_001539.summary.md`
  - `docs/reports/ledger_reach_boss-stress-20260416_001539.html`
  - `docs/reports/ledger_reach_boss-stress-latest.html`
- Glitch control pass
  - `tmp/raw_glitch_line_temporal_routefix_20260416.pipeline.json`
  - `tmp/raw_glitch_line_temporal_routefix_20260416.interrogator.json`
  - `tmp/raw_glitch_line_temporal_routefix_20260416.interrogator.md`
- New challenge packs
  - `tmp/story_pack_mid.md`
  - `tmp/story_pack_upper_mid.md`

## Honest Read: What Improved vs What Is Still Hard

Improved materially:
- Severe-story ingest stability in the targeted Ledger lane.
- Clarification behavior in permissive mode.
- Report robustness (no more forced `0/0` audit collapse on parse-error).

Still hard:
- Temporal exam generation is inconsistent for dense stories (some runs produce `0` temporal questions despite temporal dual-write).
- Fact-audit fallback is a stopgap, not a replacement for fully reliable primary audit parsing.
- Semantic quality still needs lift in dense narratives (`16/20` exam pass is good progress, not ceiling).

## Immediate Next Steps

1. Reproducibility gate: run two more `ledger_reach_boss` cycles and require stable pass with no parse/apply failures.
2. Temporal exam hardening: enforce a minimum temporal-question floor in interrogator generation for temporal-dual-write runs.
3. Use new packs as progression ladder:
- mid pack as default regression
- upper-mid pack as next promotion gate before returning to max-density stories.
4. Keep raw-input rule strict: no pre-processing of incoming story material before Prethinker ingest.

## Executive Summary

This cycle produced a real reliability gain, not cosmetic movement. The hardest active narrative lane (Ledger paragraph+temporal) now passes deterministically with zero parser/apply failures, and Glitch control remains strong. The current bottleneck has shifted from pipeline stability to deeper semantic scoring and temporal-question coverage consistency, which is the right next frontier.

