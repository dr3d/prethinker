# KB Scenarios

These scenario files are consumed by `kb_pipeline.py`.

Last updated: 2026-04-09

## Contract

Each scenario JSON contains:

- `name`: label
- `utterances`: list of natural-language turns to parse and apply
  - each item can be either:
    - string: `"Alex is parent of Sam."`
    - object: `{"utterance":"Alex is parent of Sam.","clarification_answers":["I mean Alex is Sam's father."],"max_clarification_rounds":2}`
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

Recommended for ladder/tuning loops:

- Use a dedicated namespace such as `people_ladder_tune`.
- Keep output run names monotonic (`..._r1`, `..._r2`, ...).
- Re-run lower rungs after prompt edits before moving to acid tests.

## Progressive Ladder

Use these to ramp parser complexity before acid tests:

- `stage_01_facts_only.json`
- `stage_02_rule_ingest.json`
- `stage_03_transitive_chain.json`

## Acid Ladder (Run Hard -> Easier)

Use this order to stress long-context drift, alias pressure, and correction stability:

1. `acid_08_contradiction_reconciliation.json`
2. `acid_07_relation_drift_pressure.json`
3. `acid_06_compound_unpacking.json`
4. `acid_05_long_context_lineage.json`
5. `acid_04_alias_pressure.json`
6. `acid_03_temporal_override.json`
7. `stage_03_transitive_chain.json`
8. `stage_02_rule_ingest.json`
9. `stage_01_facts_only.json`

## Suggested Smoke Pair

Use these first after any prompt edit:

1. `stage_01_facts_only.json`
2. `stage_02_rule_ingest.json`
