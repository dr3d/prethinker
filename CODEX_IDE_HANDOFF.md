# Codex IDE Handoff

Last updated: 2026-04-13  
Live repo state can drift quickly. Verify before work:
- `git rev-parse --short HEAD`
- `git status --short`

## What This Project Is

Prethinker is a governed write layer between natural language and deterministic KB mutation.

Pipeline shape:

`English -> IR (intent/logic JSON) -> Prolog runtime apply/query -> validated KB state`

## Load These First In Codex IDE

1. `README.md`
2. `AGENT-README.md`
3. `SESSIONS.md`
4. `EXPLAINER.md`
5. `docs/index.html`

## Highest-Signal Current Artifacts

- Docs hub: `docs/index.html`
- Run explorer: `docs/run-reports-hub.html`
- Time-Loop Carnival demo scenario: `kb_scenarios/demo_05_time_loop_carnival.json`
- Time-Loop Carnival run: `kb_runs/demo_05_time_loop_carnival.json`
- Time-Loop Carnival HTML report: `docs/reports/demo_05_time_loop_carnival.html`
- Control-plane ablation (with progress): `docs/reports/progress_memory_contamination_ablation_with_progress_20260412.html`
- Control-plane ablation (no progress): `docs/reports/progress_memory_contamination_ablation_no_progress_20260412.html`

## Current Priorities

1. Keep improving language-width robustness without regressing deterministic write safety.
2. Expand high-value demos (state mutation, retraction, branching, query after churn).
3. Keep docs hub visitor-first while preserving maintainer-depth links.

## Fast Commands

Run a scenario:

```bash
python kb_pipeline.py --backend ollama --base-url http://127.0.0.1:11434 --model qwen35-semparse:9b --runtime core --prompt-file modelfiles/semantic_parser_system_prompt.md --scenario kb_scenarios/demo_05_time_loop_carnival.json --kb-name demo_05_time_loop_carnival --out kb_runs/demo_05_time_loop_carnival.json
```

Render run HTML:

```bash
python scripts/render_kb_run_html.py --input kb_runs/demo_05_time_loop_carnival.json --output docs/reports/demo_05_time_loop_carnival.html --theme standard
```

Refresh docs manifests/hub:

```bash
python scripts/build_hub_index.py
```

## Operating Notes

- Primary parser model target remains `qwen35-semparse:9b`.
- This repo is intentionally independent from `../prolog-reasoning` runtime dependencies.
- `kb_store/demo_*/` is ignored to avoid local demo clutter in git.
