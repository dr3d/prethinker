# Deterministic English->Logic Compilation: Progress Note

Date: 2026-04-17

## Update: 2026-04-19 (Temporal Interrogator Recovery)

We completed a focused interrogator-side recovery pass aimed at the sharpest remaining honest weakness: temporal exam quality.

- Safety gate is now green at `120 passed`.
- The main code change is in `scripts/kb_interrogator.py`:
  - guarded repair for brittle shared-step temporal queries
  - temporal-first fallback generation used only for temporal-floor rescue, not for general exam fill
- New regression coverage was added in `tests/test_kb_interrogator_temporal.py`.

Measured live improvements:

- Glitch control lane improved materially on the same live line-temporal profile:
  - exam pass `8/14 -> 11/14`
  - temporal exam `0/5 -> 3/5`
  - final score `0.8194 -> 0.8914`
  - pipeline remained `1/1`
- Mid strict `full` no longer has a hollow temporal floor:
  - exam held at `17/20`
  - temporal exam `0/0 (floor unmet) -> 8/8`
  - final score `0.843 -> 0.9262`
  - pipeline remained `passed`
- Upper-mid strict `full` was used as a control rerun after the refinement:
  - exam remained `16/20`
  - temporal exam remained `12/16`
  - final score remained `0.9039`
  - no regression observed

Interpretation:

- This is a real honesty-and-evaluation improvement, not a fake parser gain.
- The pipeline/KB stayed stable; the interrogator got better at asking answerable temporal questions against the actual event/state encoding.
- The most important outcome is that the temporal caveat documented in the April 17 frontier sweep is now much narrower.

References:

- `tmp/glitch_frontier_recovery_temporal3_20260419.summary.json`
- `tmp/mid_full_temporal_repair2_20260419.summary.json`
- `tmp/upper_mid_full_temporal_repair2_20260419.summary.json`
- `docs/reports/TEMPORAL_INTERROGATOR_RECOVERY_2026-04-19.md`

## Update: 2026-04-17 (Longform Full-Mode Recovery + Frontier Sweep)

We completed a longform recovery pass aimed at the weakest honest lane: strict `full` story ingestion on the narrative packs.

- Safety gate is now green at `105 passed`.
- Blocksworld guarded lane remains stable:
  - symbolic harness solve/replay: `20/20`
  - prethinker pilot pass: `8/8`
  - avg init predicate hit: `0.458334`
  - avg goal predicate hit: `0.458334`
  - zero-hit cases: `0`
- Mid strict now clears `pipeline_pass=3/3` and, most importantly, `full` mode recovered from `0/20` exam to `17/20`.
  - current best: `0.9284`
  - `full`: coverage `0.850`, precision `0.850`, exam `17/20`, temporal exam floor still unmet
  - `paragraph`: coverage `0.850`, precision `0.920`, exam `17/20`, temporal exam `4/4`
  - `line`: coverage `0.850`, precision `0.920`, exam `17/20`, temporal exam `4/4`
- Upper-mid strict remains strong and also clears `pipeline_pass=3/3`.
  - current best: `0.956`
  - `full`: coverage `0.850`, precision `0.920`, exam `16/20`, temporal exam `12/16`
  - `paragraph`: coverage `0.920`, precision `0.880`, exam `20/20`, temporal exam `12/12`
  - `line`: coverage `0.920`, precision `0.880`, exam `20/20`, temporal exam `12/12`
- Glitch control stayed structurally clean after the `at_step/2` namespace fix:
  - pipeline `1/1`
  - coverage `0.850`
  - precision `0.920`
  - exam `8/14`
  - temporal exam still `0/5`

Interpretation:

- The biggest win is real: `full` long-story ingestion is no longer the obvious weak link on the mid pack.
- The stable lane stayed intact while we made that change.
- Temporal question quality is still the main honest weakness on the Glitch control lane and the remaining caveat on mid `full`.

References:

- `docs/reports/FRONTIER_SWEEP_2026-04-17.md`
- `tmp/mid_pack_general_strict_temporal_recovery_fullfix2_20260417.summary.json`
- `tmp/upper_mid_pack_general_strict_temporal_regressioncheck2_20260417.summary.json`
- `tmp/glitch_frontier_recovery_temporal2_20260417.summary.json`
- `tmp/blocksworld_lane_regressioncheck_20260417.summary.json`

## Update: 2026-04-17 (Exam Hardening + Narrative Breakout)

We completed another strict recovery pass after hardening the interrogator against malformed exam queries and promoting a few remaining recurring story predicates.

- Safety gate is now green at `92 passed`.
- Blocksworld improved again under the guarded lane:
  - symbolic harness solve/replay: `20/20`
  - prethinker pilot pass: `8/8`
  - avg init predicate hit: `0.75`
  - avg goal predicate hit: `0.666667`
  - zero-hit cases: `0`
  - avg-hit gates `0.45 / 0.45` both passed
- Mid strict latest rerun recovered from the bad exam artifact and now lands at:
  - latest rerun best: `0.359033`
  - latest rerun pipeline: `1/3`
  - paragraph lane: coverage `0.850`, precision `0.920`, exam `0.800`, temporal exam `0.667`
  - historical best remains `0.3812`, so the lane is still real recovery work rather than a fresh promotion win
- Upper-mid strict produced a real breakout:
  - current best: `0.967`
  - strict full-mode run: coverage `0.850`, precision `1.000`, exam `1.000`, temporal exam `1.000`
  - paragraph/line reruns each reached `0.385` with `20/20` exam and `8/8` temporal, but the pack still remains `pipeline_pass=1/3` because one governance paragraph still rejects

Interpretation:

- The interrogator scores are more trustworthy now because malformed rule-shaped exam queries and bad boolean row checks are no longer accepted as-is.
- Stable proof is still concentrated in safety gate + Blocksworld.
- Upper-mid now has a credible strict full-mode success, but we should not call the pack fully green until paragraph/line also clear.
- Mid is still blocked by a smaller parser/ontology tail, not by broad system instability.

References:

- `docs/reports/BLOCKSWORLD_LANE_GUARDED_2026-04-17.md`
- `docs/reports/NARRATIVE_PACKS_RECOVERY_2026-04-17.md`
- `docs/reports/MID_PACK_GENERAL_STRICT_TEMPORAL_RECOVERY4_2026-04-17.md`
- `docs/reports/UPPER_MID_PACK_GENERAL_STRICT_TEMPORAL_RECOVERY5_2026-04-17.md`

## Update: 2026-04-17 (Guardrail + Recovery Batch)

We completed the guardrail batch, reran the live Ollama spine, and now have a cleaner current public state than the earlier post-registry correction alone.

- Safety gate is now green at `88 passed`.
- Blocksworld stayed stable under stricter guarded evaluation:
  - symbolic harness solve/replay: `20/20`
  - prethinker pilot pass: `8/8`
  - avg init predicate hit: `0.458334`
  - avg goal predicate hit: `0.458334`
  - zero-hit cases: `0`
  - avg-hit gates `0.45 / 0.45` both passed
- Narrative strict packs improved from the first honest post-registry baseline, but still remain below full promotion bar:
  - mid pack: `0.3237` -> `0.3812`, `pipeline_pass=1/3`
  - upper-mid pack: `0.257644` -> `0.3922`, `pipeline_pass=1/3`

Interpretation:

- The repo is more trustworthy than it was before the registry population, and more capable than it was at the first strict rerun.
- Stable proof is still concentrated in safety gate + Blocksworld.
- Narrative recovery is real, but current strict narrative results should still be presented as "improving frontier work," not as a green solved lane.

References:

- `docs/reports/BLOCKSWORLD_LANE_GUARDED_2026-04-17.md`
- `docs/reports/NARRATIVE_PACKS_RECOVERY_2026-04-17.md`
- `docs/reports/MID_PACK_GENERAL_STRICT_TEMPORAL_RECOVERY2_2026-04-17.md`
- `docs/reports/UPPER_MID_PACK_GENERAL_STRICT_TEMPORAL_RECOVERY3_2026-04-17.md`

## Update: 2026-04-17 (Post-Registry Live Verification)

We completed the first live Ollama rerun after populating `modelfiles/predicate_registry.json`, which means the general strict lane is now actually strict.

- Blocksworld sanity check stayed stable
  - symbolic harness solve/replay: `20/20`
  - prethinker pilot pass: `8/8`
  - avg init predicate hit: `0.458334`
  - avg goal predicate hit: `0.458334`
  - zero-hit cases: `0`
- Narrative pack scores were corrected downward once strict admission became real
  - mid pack: provisional `0.6452` -> post-registry `0.3237`
  - upper-mid pack: provisional `0.8718` -> post-registry `0.257644`
  - both packs now show `pipeline_pass=1/3` under the strict temporal rerun

Interpretation:

- the old pack numbers were inflated by an effectively empty general registry.
- the new numbers are the first honest strict baseline for these two packs.
- the immediate problem is no longer "does strict mode exist?" but "how do we recover narrative recall without fake strictness?"

References:

- `docs/reports/BLOCKSWORLD_LANE_POST_REGISTRY_2026-04-17.md`
- `docs/reports/MID_PACK_GENERAL_STRICT_TEMPORAL_2026-04-17.md`
- `docs/reports/UPPER_MID_PACK_GENERAL_STRICT_TEMPORAL_2026-04-17.md`
- `docs/reports/NARRATIVE_PACKS_POST_REGISTRY_2026-04-17.md`

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

## Historical Note: 2026-04-17 (Pre-Population Pack Correction Attempt, Superseded)

This section is kept as an audit trail.
The narrative scores in it are no longer the current strict baseline because they were recorded before `modelfiles/predicate_registry.json` was populated.
Use the post-registry live verification at the top of this document as the current truth.

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

- Mid/upper-mid narrative pack correction (configuration sanity, now superseded)
  - we discovered an invalid comparison run where narrative packs were executed with the Blocksworld predicate registry; that run is now treated as config-mismatch diagnostic, not quality signal.
  - the provisional reruns below used the general registry path + strict flag before registry population was completed:
    - `tmp/mid_pack_general_strict_temporal_20260417.summary.json`
      - provisional `run_count=3`, `pipeline_pass=3`, `best_final_score=0.6452`
    - `tmp/upper_mid_pack_general_strict_temporal_20260417.summary.json`
      - provisional `run_count=3`, `pipeline_pass=3`, `best_final_score=0.8718`
  - these values must not be used as current strict-lane headline numbers.
  - they were replaced by the post-registry live reruns above:
    - mid pack: `0.3237`, `pipeline_pass=1/3`
    - upper-mid pack: `0.257644`, `pipeline_pass=1/3`

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

