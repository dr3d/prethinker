# KB Scenarios

This directory is a small compatibility archive of early JSON scenario fixtures.
Current research work should prefer the newer source-local benchmark packs under
`datasets/`, `docs/data/frontier_packs/`, and the domain bootstrap/story-world
harnesses.

Last updated: 2026-04-30

## Status

The old rung ladder has been retired from the working tree. Git history remains
the archive for those parser-era ladder files. Keeping them locally made the
repo look like it still had an English-first test ladder, which no longer
matches the current architecture.

The remaining non-rung files are retained only because a few smoke/lava paths
can still mine them as generic pressure material through the current
router/Semantic IR/mapper pipeline. Do not add new fixtures here unless a
legacy harness explicitly needs JSON scenario shape.

## Preferred Homes For New Work

- `datasets/story_worlds/`: source-local stories, gold KBs, QA batteries, and
  frontier journals.
- `datasets/domain_bootstrap/`: seed corpora and profile-bootstrap experiments.
- `docs/data/frontier_packs/`: mixed-domain Lava packs and router/admission
  pressure cases.
- `docs/data/policy_demo/`: product-like policy/rule demos.

## Historical JSON Shape

Each scenario JSON usually contains:

- `name`: scenario label.
- `utterances`: list of natural-language turns.
- `validations`: deterministic Prolog checks run after the turns.

That shape is historical. The current architecture treats language
understanding as LLM-authored semantic workspace construction, with Python
limited to orchestration, schema/contract enforcement, mapping, runtime
execution, and scoring.
