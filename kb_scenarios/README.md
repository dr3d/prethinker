# KB Scenarios

This directory is a small compatibility archive of early JSON scenario fixtures.
Current research work should prefer the newer source-local benchmark packs under
`datasets/`, focused probes under `experiments/`, and the domain
bootstrap/story-world harnesses.

Last updated: 2026-04-30

## Status

The old rung ladder has been retired from the working tree. Git history remains
the archive for those parser-era ladder files. Keeping them locally made the
repo look like it still had an English-first test ladder, which no longer
matches the current architecture.

The remaining JSON fixtures are compatibility pressure material for the
router/Semantic IR/mapper pipeline. Older JSON fixtures that were not reachable
from current sweeps have been removed from the working tree; Git history remains
their archive. Do not add new fixtures here unless a compatibility harness
explicitly needs this historical JSON scenario shape.

## Preferred Homes For New Work

- `datasets/story_worlds/`: source-local stories, gold KBs, QA batteries, and
  frontier journals.
- `datasets/profile_bootstrap/`: seed corpora and profile-bootstrap
  experiments.
- `experiments/boundary_probes/`: focused unlike probes for transfer-safe
  boundary work.
- `tmp/`: generated run output, local pressure packs, and scratch artifacts.

## Historical JSON Shape

Each scenario JSON usually contains:

- `name`: scenario label.
- `utterances`: list of natural-language turns.
- `validations`: deterministic Prolog checks run after the turns.

That shape is historical. The current architecture treats language
understanding as LLM-authored semantic workspace construction, with Python
limited to orchestration, schema/contract enforcement, mapping, runtime
execution, and scoring.
