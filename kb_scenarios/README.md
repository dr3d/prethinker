# KB Scenarios

These scenario files are consumed by `kb_pipeline.py`.

Last updated: 2026-04-09

## Contract

Each scenario JSON contains:

- `name`: label
- `utterances`: list of natural-language turns to parse and apply
  - each item can be either:
    - string: `"Alex is parent of Sam."`
    - object: `{"utterance":"Alex is parent of Sam.","clarification_answers":["I mean Alex is Sam's father."],"confirmation_answers":["yes"],"max_clarification_rounds":2,"require_final_confirmation":true}`
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
