# Process Utterance Frontier Baselines

- date: `2026-04-20`
- path under test: [src/mcp_server.py](</D:/_PROJECTS/prethinker/src/mcp_server.py>) `process_utterance()`
- compiler mode: `strict`
- compiler model: `qwen3.5:9b`
- freethinker policy: `off`

These are the first frozen replay baselines derived from the forge-distilled frontier packs. They are meant to be the official starting line for the hardest current `process_utterance()` families, not another floating tmp artifact.

## Correction Baseline

- pack: [process_utterance_correction_pack_v1.json](</D:/_PROJECTS/prethinker/docs/data/frontier_packs/process_utterance_correction_pack_v1.json>)
- frozen replay: [process_utterance_correction_pack_v1_baseline.json](</D:/_PROJECTS/prethinker/docs/data/frontier_packs/process_utterance_correction_pack_v1_baseline.json>)
- cases: `12`
- verdicts: `9 fail`, `3 warn`
- statuses: `9 clarification_required`, `3 error`
- deltas versus original forge source cases: `3 improved`, `9 unchanged`

Practical read:

- `correction` is still red.
- The small improvement is real but limited: a few cases moved from hard `error` into `clarification_required`.
- That is better behavior, but it is not yet a green or even yellow correction lane.

## Temporal Baseline

- pack: [process_utterance_temporal_pack_v1.json](</D:/_PROJECTS/prethinker/docs/data/frontier_packs/process_utterance_temporal_pack_v1.json>)
- frozen replay: [process_utterance_temporal_pack_v1_baseline.json](</D:/_PROJECTS/prethinker/docs/data/frontier_packs/process_utterance_temporal_pack_v1_baseline.json>)
- cases: `12`
- verdicts: `6 fail`, `6 warn`
- statuses: `6 error`, `6 success`
- deltas versus original forge source cases: `12 unchanged`

Practical read:

- `temporal_state` is a stable number-two frontier behind correction.
- The important thing here is reproducibility: the pack cleanly preserves the current temporal boundary.
- The red cases remain true red cases, and the yellow cases remain yellow for the same reasons:
  - same-step contradiction
  - dropped or weakened second leg of a sequence
  - over-clarification on straightforward temporal narration

## Why These Matter

These frozen baselines let us prove improvement in the hardest areas without turning every forge miss into a one-off patch.

The rule from here should be:

- rerun the relevant frontier pack
- compare against these frozen baselines
- only count a change as progress if it improves the family without breaking the stable scaffold
