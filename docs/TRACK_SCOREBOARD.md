# Track Scoreboard

Last updated: 2026-04-20

## Read This First

This file is a partitioned scoreboard, not the repo headline.
Use `docs/PROGRESS.md` for the current source of truth.

Current status after the latest verified frontier-pack and gate reruns:

| Lane | Status | Evidence |
|---|---|---|
| Safety gate | green | `142 passed` |
| Blocksworld strict guarded | green | last verified stable lane: `20/20` solve/replay, `8/8` pilot, zero-hit `0`, avg init `0.458334`, avg goal `0.458334` |
| `process_utterance()` correction pack | improved | `10/12` pass, `2/12` fail |
| `process_utterance()` temporal pack | improved | `8/12` pass, `4/12` warn, `0/12` fail |
| Narrative strict (mid, last verified Apr 19) | recovered | `pipeline_pass=3/3`, best `0.9284`; temporal interrogator recovery restored a real `full` temporal floor |
| Narrative strict (upper-mid, last verified Apr 19) | strong | `pipeline_pass=3/3`, best `0.956`; paragraph and line both reached `20/20` |

References:

- `docs/PROGRESS.md`
- `docs/reports/PROCESS_UTTERANCE_PIPELINE_BATCH_2026-04-20.md`
- `docs/PROCESS_UTTERANCE_FRONTIER_PACKS.md`
- `docs/reports/FRONTIER_SWEEP_2026-04-17.md`
- `docs/reports/TEMPORAL_INTERROGATOR_RECOVERY_2026-04-19.md`

## Historical Width Tracks (2026-04-13 Snapshot, Ollama, qwen35-semparse:9b, runtime=core)

| Track | Passed / Total | Pass Rate | Target | Meets Target |
|---|---:|---:|---:|---|
| frontier_language_width_v4 | 12 / 12 | 100.0% | 67% | True |
| frontier_language_width_v5 | 15 / 15 | 100.0% | 67% | True |
| frontier_language_width_v6 | 16 / 16 | 100.0% | 67% | True |
| frontier_clarification_probe_v1 | 3 / 3 | 100.0% | 100% | True |
| frontier_confirmation_probe_v1 | 2 / 2 | 100.0% | 100% | True |

Raw summary JSON:

- `docs/data/tracks/frontier_language_width_v4_latest.json`
- `docs/data/tracks/frontier_language_width_v5_latest.json`
- `docs/data/tracks/frontier_language_width_v6_latest.json`
- `docs/data/tracks/frontier_clarification_probe_v1_latest.json`
- `docs/data/tracks/frontier_confirmation_probe_v1_latest.json`

## Same-Model Served-LLM Sweep (Historical Baseline)

Model setup:

- Parser: `qwen35-semparse:9b`
- Served-LLM clarification model: `qwen35-semparse:9b`
- Backend: Ollama

| Track | Passed / Total | Pass Rate | Target | Meets Target |
|---|---:|---:|---:|---|
| gate_ladder_frontier | 7 / 8 | 87.5% | 100% | False |
| examples_all | 2 / 7 | 28.6% | 80% | False |
| book_acid_goldilocks | 0 / 2 | 0.0% | 50% | False |

Historical JSON:

- `docs/data/tracks/gate_ladder_frontier_same_model_latest.json`
- `docs/data/tracks/examples_all_same_model_latest.json`
- `docs/data/tracks/book_acid_goldilocks_same_model_latest.json`

## Excursion Ceiling Sweep (2026-04-13 Historical GO Run, Bare `qwen3.5:9b`)

Model/setup:

- Parser: `qwen3.5:9b`
- Prompt source: runtime `modelfiles/semantic_parser_system_prompt.md`
- Backend: Ollama
- Runtime: `core`

| Track | Passed / Total | Pass Rate | Target | Meets Target |
|---|---:|---:|---:|---|
| excursion_cooperative_v1_full | 2 / 6 | 33.3% | 83% | False |
| excursion_wild_v1_full | 3 / 6 | 50.0% | 67% | False |
| excursion_frontier_v2_full | 5 / 12 | 41.7% | 75% | False |
| excursion_failure_promotions_v1 | 3 / 3 | 100.0% | 100% | True |

Run summary JSON (tmp artifacts):

- `tmp/runs/tracks/track_excursion_cooperative_v1_full_summary_20260413_204213.json`
- `tmp/runs/tracks/track_excursion_wild_v1_full_summary_20260413_204213.json`
- `tmp/runs/tracks/track_excursion_frontier_v2_full_summary_20260413_203539.json`
- `tmp/runs/tracks/track_excursion_failure_promotions_v1_summary_20260413_204119.json` (initial baseline)
- `tmp/runs/tracks/track_excursion_failure_promotions_v1_summary_20260413_211029.json` (after pre-normalization + targeted repair pass)
- `tmp/runs/tracks/track_excursion_failure_promotions_v1_summary_20260413_211353.json` (verified with new `run_track.py` default model)
