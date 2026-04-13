# Track Scoreboard

Last updated: 2026-04-12

## Frontier Width Tracks (Ollama, qwen35-semparse:9b, runtime=core)

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
