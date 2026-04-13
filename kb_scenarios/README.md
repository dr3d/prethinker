# KB Scenarios

These scenario files are consumed by `kb_pipeline.py`.

Last updated: 2026-04-12

## Contract

Each scenario JSON contains:

- `name`: label
- `utterances`: list of natural-language turns to parse and apply
  - each item can be either:
    - string: `"Alex is parent of Sam."`
    - object: `{"utterance":"Alex is parent of Sam.","clarification_answers":["I mean Alex is Sam's father."],"confirmation_answers":["yes"],"max_clarification_rounds":2,"require_final_confirmation":true}`
    - object can also include Progress Memory directives:
      - `progress.set_active_focus`: list of active focus strings
      - `progress.add_goals`: list of goal strings
      - `progress.add_open_questions`: list of unresolved question strings
      - `progress.resolve_goals`: list of goal ids/text to resolve
      - `progress.resolve_questions`: list of question ids/text to resolve
      - `progress.add_notes`: list of notes for progress context
- `validations`: list of deterministic checks run after all turns

Validation entry fields:

- `id`: optional label
- `query`: Prolog query string
- `expect_status`: `success` or `no_results` (default `success`)
- `min_rows`: optional minimum expected row count
- `max_rows`: optional maximum expected row count
- `contains_row`: optional exact row object requirement

## Important Runtime Behavior

`kb_pipeline.py` uses named retained KB namespaces:

- New ontology KB namespace: `empty_kb()` is applied once for clean start.
- Existing namespace: retained corpus is preloaded; no automatic empty/reset.
- Clarification policy is configurable at runtime:
  - `--clarification-eagerness` in `[0,1]` (higher asks clarification sooner)
  - `--max-clarification-rounds` controls multi-round Q&A depth per utterance
  - `--require-final-confirmation` requires explicit yes/no before write intents are applied (`assert_fact`, `assert_rule`, `retract`)

Recommended for ladder/tuning loops:

- Use a dedicated namespace such as `people_ladder_tune`.
- Keep output run names monotonic (`..._r1`, `..._r2`, ...).
- Re-run lower rungs after prompt edits before moving to acid tests.

## Progressive Ladder

Use these to ramp parser complexity before acid tests:

- `stage_01_facts_only.json`
- `stage_02_rule_ingest.json`
- `stage_03_transitive_chain.json`

## Naming Note

- Existing `acid_*` scenario names are retained as historical record.
- New hard-rung scenarios should use `rung_<nn>_<slug>.json` going forward.

## Frontier Rung Orchestration (Working Contract)

Rung work is split into two explicit functions:

- `Agent54` adds new frontier rungs to push logical height and language width.
- Gate curation removes low-signal retest rungs that waste runtime below the active frontier.

Authoring/curation flow:

1. Add rung file:
- create `kb_scenarios/rung_<nn>_<slug>.json` with deterministic validations.

2. Register rung in track manifest:
- add it to the intended frontier track in `kb_scenarios/tracks.json`.

3. Prove signal:
- run focused track checks and confirm the rung catches or protects a real behavior slice.

4. Prune gate debt:
- if an older rung is repeatedly redundant and covered by a harder successor, remove it from strict gate retests.
- keep at least one anchor rung per failure class.

Default prune thresholds:

- no novel failures across >=3 consecutive sweeps, and
- superseded by a harder/newer rung on the same semantic target.

## Rung Width (Language Robustness)

Rungs now grow in two dimensions:

- Height: harder logic/composition.
- Width: more linguistic variation for the same target KB result.

When adding new `rung_*` scenarios, include language-robustness pressure where possible:

- paraphrase/restatement
- inversion/passive voice
- synonym/lexical drift
- hedged language ("maybe", "I think", "probably")
- punctuation/typo/noisy phrasing
- pronoun/ellipsis ambiguity

Design rule:

- clean and noisy variants should map to the same intended KB outcome (or the same clarification/escalation expectation when ambiguity is intentionally unresolved).

## Acid Ladder (Run Hard -> Easier)

Use this order to stress long-context drift, alias pressure, and correction stability:

1. `acid_16_rule_stack_retarget.json`
2. `acid_15_dual_track_repair.json`
3. `acid_14_unary_conjunction_retract_effect.json`
4. `acid_13_branch_preservation_after_repair.json`
5. `acid_12_compound_repair_with_query.json`
6. `acid_11_batched_fact_rule_retract_mix.json`
7. `acid_10_compound_retract_unpacking.json`
8. `acid_09_compound_rule_unpacking.json`
9. `acid_08_contradiction_reconciliation.json`
10. `acid_07_relation_drift_pressure.json`
11. `acid_06_compound_unpacking.json`
12. `acid_05_long_context_lineage.json`
13. `acid_04_alias_pressure.json`
14. `acid_03_temporal_override.json`
15. `stage_03_transitive_chain.json`
16. `stage_02_rule_ingest.json`
17. `stage_01_facts_only.json`

## Suggested Smoke Pair

Use these first after any prompt edit:

1. `stage_01_facts_only.json`
2. `stage_02_rule_ingest.json`

## Cross-Domain Expansion Rungs

These extend beyond family-only parsing into operational and simulation language:

1. `rung_240_ops_hospital_vendor_delay_core.json`
2. `rung_241_ops_hospital_cpm_natural_flow.json`
3. `rung_250_ops_indie_launch_uncertainty_routing.json`
4. `rung_251_ops_indie_warroom_natural_flow.json`
5. `rung_260_sim_fantasy_state_repair.json`
6. `rung_261_sim_fantasy_overlord_natural_flow.json`

## Progress-Memory Rungs

These scenarios exercise the feasibility-vs-progress lane and goal-directed clarification behavior:

1. `rung_370_progress_feasibility_alignment.json`
2. `rung_380_progress_irrelevant_fact_filter.json`
3. `rung_390_progress_goal_directed_clarification.json`

Additional benefit-targeted probes:

4. `rung_400_progress_relevance_repair.json`
5. `rung_410_progress_goal_context_steering.json`
6. `rung_420_progress_focus_shift_transition.json`

## Book-Acid Rungs

These push toward narrative/book ingestion and Q&A over long-form prose:

1. `rung_430_goldilocks_roundtrip_retry.json` (structured story retry + deterministic checks)
2. `rung_431_book_goldilocks_raw_chaptered_qa.json` (raw source text chunks + probe checks)

Authoring note for book-acid:

- Keep the long-form narrative pressure, but add a few short bridge utterances when raw chapter chunks would otherwise be skipped as "just narrative."
- Use scripted `clarification_answers` for answer-critical probes or pronoun-heavy turns when the challenge is book retention, not referent roulette.
- Prefer validations on answer-critical facts (`ate_all/2`, `broke/1`, `slept_in/2`, `saw/2`) over a single brittle paraphrase-specific predicate/state when multiple faithful encodings are plausible.

## Frontier Width V2 Rungs

These rungs push language-noise and midstream-repair pressure harder while preserving deterministic validation:

1. `rung_432_noise_pronoun_inversion_chain.json`
2. `rung_433_noisy_inverse_retarget_repair.json`
3. `rung_434_dual_pronoun_flip_guard.json`
4. `rung_435_frontier_checkpoint_compound_turns.json`
5. `rung_436_frontier_noise_typo_coref.json`
6. `rung_437_frontier_policy_override_flow.json`

## Frontier Width V3 Add-ons

Additional harder-width rungs layered on top of v2:

1. `rung_438_frontier_multibind_query_pressure.json`
2. `rung_439_frontier_plural_coref_exception_guard.json`
3. `rung_440_frontier_policy_revision_loop.json`

## Frontier Width V4 Add-ons

Further width pressure with higher-noise pronoun shifts and multi-step policy/asset revision loops:

1. `rung_441_frontier_pronoun_bucket_shuffle.json`
2. `rung_442_frontier_policy_multirevision_guard.json`
3. `rung_443_frontier_dual_item_handoff_coref.json`

## Frontier Width V5 Add-ons

Compressed language pressure add-ons:

1. `rung_444_frontier_unpunctuated_coref_sweep.json`
2. `rung_445_frontier_compound_write_query_braid.json`
3. `rung_446_frontier_policy_noisy_rebind_loop.json`

## Frontier Width V6 Add-on

Variable-binding answer pressure:

1. `rung_449_frontier_multibind_uncle_query.json`

## Frontier Width V7 Add-ons

Story-heavy frontier add-ons for retroactive identity correction and counterfactual-vs-actual separation:

1. `rung_450_frontier_story_retroactive_identity_swap.json`
2. `rung_451_frontier_story_counterfactual_retract_weave.json`

## Excursion Pilot V1

First in-the-wild pilot pair with graded language noise:

1. `rung_452_excursion_hn_docker_spain_block.json` (HN middle-noise incident thread)
2. `rung_453_excursion_reddit_security_deposit_appeal.json` (Reddit legal update timeline)

Seed source bank:

- `stories/excursions/SOURCE_BANK_V1.md`
- `stories/excursions/excursion_manifest_v1.json`

## Excursion Gradient Packs (v1)

Cooperative lane (`G1` -> `G2`):

1. `rung_454_excursion_coop_fed_policy_hold.json`
2. `rung_455_excursion_coop_fed_revision_guard.json`
3. `rung_456_excursion_coop_scotus_exception_logic.json`
4. `rung_462_excursion_coop_fed_labor_inflation_balance.json`
5. `rung_463_excursion_coop_fed_counterfactual_guard.json`
6. `rung_464_excursion_coop_scotus_parenthetical_exception.json`

HN middle-noise lane (`G3`):

1. `rung_452_excursion_hn_docker_spain_block.json`
2. `rung_457_excursion_hn_codex_claude_scope_split.json`
3. `rung_458_excursion_hn_agents_key_policy.json`
4. `rung_459_excursion_hn_scope_correction.json`

Reddit wild lane (`G4`):

1. `rung_453_excursion_reddit_security_deposit_appeal.json`
2. `rung_460_excursion_reddit_landlord_entry_timeline.json`
3. `rung_461_excursion_reddit_commercial_entry_dispute.json`

## Failure-Promotion Guards (From Excursion Failures)

These are synthetic guard rungs promoted from repeated failure patterns observed in wild excursions:

1. `rung_465_frontier_failure_multiclause_scope_drop_guard.json`
2. `rung_466_frontier_failure_exception_rule_partition.json`
3. `rung_467_frontier_failure_question_advice_dual_intent.json`

## Demo Pack Scenarios

These are presentation-oriented runnable demos (not core ladder gates):

1. `demo_01_meeting_commitment_extractor.json`
2. `demo_02_policy_stress_test_machine.json`
3. `demo_03_story_world_interrogator.json`
4. `demo_04_reimbursement_violation_check.json`

## Scenario Tracks

Track manifest:

- `kb_scenarios/tracks.json`

Run tracks:

```bash
# list tracks
python scripts/run_track.py --list-tracks

# strict gate battery
python scripts/run_track.py --track gate_ladder_frontier --fail-on-under

# examples + demos battery
python scripts/run_track.py --track examples_all

# book-acid Goldilocks sweep
python scripts/run_track.py --track book_acid_goldilocks

# frontier language-width stress sweep
python scripts/run_track.py --track frontier_language_width_v2

# extended frontier sweep (v3)
python scripts/run_track.py --track frontier_language_width_v3

# frontier width v4 sweep
python scripts/run_track.py --track frontier_language_width_v4

# frontier width v5 sweep
python scripts/run_track.py --track frontier_language_width_v5

# frontier width v6 sweep
python scripts/run_track.py --track frontier_language_width_v6

# frontier width v7 add-ons sweep
python scripts/run_track.py --track frontier_language_width_v7_addons

# in-the-wild excursion pilot pair
python scripts/run_track.py --track excursion_pilot_v1

# excursion cooperative lane (formal transcript style)
python scripts/run_track.py --track excursion_cooperative_v1

# excursion middle lane (HN)
python scripts/run_track.py --track excursion_middle_hn_v1

# excursion wild lane (Reddit legal narrative)
python scripts/run_track.py --track excursion_wild_reddit_v1

# full graded excursion frontier sweep
python scripts/run_track.py --track excursion_frontier_v1 --kb-root tmp/kb_store_excursion --fail-on-under

# scaled full cooperative pack (6)
python scripts/run_track.py --track excursion_cooperative_v1_full --kb-root tmp/kb_store_excursion --fail-on-under

# scaled full wild pack (6)
python scripts/run_track.py --track excursion_wild_v1_full --kb-root tmp/kb_store_excursion --fail-on-under

# scaled full excursion frontier (12 total)
python scripts/run_track.py --track excursion_frontier_v2_full --kb-root tmp/kb_store_excursion --fail-on-under

# promoted failure-class guard pack
python scripts/run_track.py --track excursion_failure_promotions_v1 --kb-root tmp/kb_store_excursion --fail-on-under

# CE probe on newest noisy rungs
python scripts/run_track.py --track frontier_clarification_probe_v1 --clarification-eagerness 0.85 --max-clarification-rounds 3

# final-confirmation gate probe
python scripts/run_track.py --track frontier_confirmation_probe_v1 --require-final-confirmation
```

Tip for unattended sweeps:

- add `--kb-root tmp/kb_store` to keep temporary run namespaces out of the canonical `kb_store/`.
