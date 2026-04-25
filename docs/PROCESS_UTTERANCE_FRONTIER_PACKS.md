# Process Utterance Frontier Packs

These are the first durable replay targets distilled from the forge.

The forge is still where we discover new weirdness. The packs are where we pin the hardest current families so we can rerun them after a change and see whether things actually got better.

## Current Packs

- [process_utterance_correction_pack_v1.json](</D:/_PROJECTS/prethinker/docs/data/frontier_packs/process_utterance_correction_pack_v1.json>)
- [process_utterance_temporal_pack_v1.json](</D:/_PROJECTS/prethinker/docs/data/frontier_packs/process_utterance_temporal_pack_v1.json>)

## Frozen Baselines

- [process_utterance_correction_pack_v1_baseline.json](</D:/_PROJECTS/prethinker/docs/data/frontier_packs/process_utterance_correction_pack_v1_baseline.json>)
- [process_utterance_temporal_pack_v1_baseline.json](</D:/_PROJECTS/prethinker/docs/data/frontier_packs/process_utterance_temporal_pack_v1_baseline.json>)

Historical dated baseline reports were pruned from the forward-facing tree; rerun the pack runner to regenerate fresh local reports when needed.

## What They Are For

- `correction_pack`
  Distilled from forge correction failures. These are replayable write-revision cases with a simple prior setup turn so we can test whether correction handling is still red.

- `temporal_pack`
  Distilled from forge temporal failures and warns. These are the current `at_step(...)` / `later moved` / relative-time pressure cases that define the real sequencing frontier.

## Builder

- [build_process_utterance_frontier_packs.py](</D:/_PROJECTS/prethinker/scripts/build_process_utterance_frontier_packs.py>)

This script re-derives the tracked pack JSONs from the current forge interesting-case directories.

## Runner

- [run_process_utterance_frontier_pack.py](</D:/_PROJECTS/prethinker/scripts/run_process_utterance_frontier_pack.py>)

Suggested smoke command:

```powershell
python scripts/run_process_utterance_frontier_pack.py --pack docs/data/frontier_packs/process_utterance_temporal_pack_v1.json --limit 3
```

Full temporal replay:

```powershell
python scripts/run_process_utterance_frontier_pack.py --pack docs/data/frontier_packs/process_utterance_temporal_pack_v1.json
```

Full correction replay:

```powershell
python scripts/run_process_utterance_frontier_pack.py --pack docs/data/frontier_packs/process_utterance_correction_pack_v1.json
```

## Rule Of Use

These packs are not a license to patch every miss.

They exist so we can:

- prove improvement in the hardest current families
- notice regressions quickly
- keep the green/yellow/red map honest
