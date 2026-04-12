# Track Scoreboard (Same-Model Served-LLM Sweep)

Date: 2026-04-12

Model setup:
- Parser: qwen35-semparse:9b
- Served-LLM clarification model: qwen35-semparse:9b
- Backend: Ollama

| Track | Passed / Total | Pass Rate | Target | Meets Target |
|---|---:|---:|---:|---|
| gate_ladder_frontier | 7 / 8 | 87.5% | 100% | False |
| examples_all | 2 / 7 | 28.6% | 80% | False |
| ook_acid_goldilocks | 0 / 2 | 0.0% | 50% | False |

Raw summary JSON:
- docs/data/tracks/gate_ladder_frontier_same_model_latest.json
- docs/data/tracks/examples_all_same_model_latest.json
- docs/data/tracks/book_acid_goldilocks_same_model_latest.json

Notes:
- This sweep intentionally forces both parse and clarification roles onto the same model to simplify VRAM behavior and isolate orchestration effects.
- Core gate performance remains high but below strict target due to one frontier miss (ung_230).
- Examples and book-acid tracks are currently below target and should be treated as active hardening backlog, not publish-quality claims.
