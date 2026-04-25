# Prethinker

Prethinker is a local research workbench for turning natural-language turns into governed Prolog knowledge-base updates. The LLM proposes structured deltas; the runtime validates, routes, and applies only the parts that survive policy, schema, and consistency checks.

Current center: a live `ui_gateway` console backed by `src/mcp_server.py`, with the bounded `medical@v0` profile and local UMLS Semantic Network assets as the most active research direction.

## Current State

Read [PROJECT_STATE.md](https://github.com/dr3d/prethinker/blob/main/PROJECT_STATE.md) first. It is the compact, current orientation document for the repo.

The short version:

- `process_utterance()` is the canonical runtime entrypoint.
- The UI is a manual demonstration cockpit, not a marketing page.
- `medical@v0` is the main frontier profile.
- UMLS is used as a bounded normalization and semantic-type bridge, not as a giant preloaded clinical encyclopedia.
- The Prolog KB is the committed truth layer; model output remains provisional until the runtime admits it.
- Historical reports, old prompt snapshots, and run logs were pruned from the forward-facing tree because Git already preserves them.

## Useful Entry Points

- [PROJECT_STATE.md](https://github.com/dr3d/prethinker/blob/main/PROJECT_STATE.md) - current architecture, demo status, and next frontiers.
- [AGENT-README.md](https://github.com/dr3d/prethinker/blob/main/AGENT-README.md) - fast onboarding for coding agents.
- [docs/PRETHINK_GATEWAY_MVP.md](https://github.com/dr3d/prethinker/blob/main/docs/PRETHINK_GATEWAY_MVP.md) - live gateway shape.
- [docs/UMLS_MVP.md](https://github.com/dr3d/prethinker/blob/main/docs/UMLS_MVP.md) - UMLS bridge and Semantic Network work.
- [docs/MEDICAL_PROFILE.md](https://github.com/dr3d/prethinker/blob/main/docs/MEDICAL_PROFILE.md) - bounded medical profile.
- [docs/FREETHINKER_DESIGN.md](https://github.com/dr3d/prethinker/blob/main/docs/FREETHINKER_DESIGN.md) - optional clarification sidecar.
- [docs/CONSOLE_TRYBOOK.md](https://github.com/dr3d/prethinker/blob/main/docs/CONSOLE_TRYBOOK.md) - prompts for manual demos.
- [ui_gateway/README.md](https://github.com/dr3d/prethinker/blob/main/ui_gateway/README.md) - UI gateway notes.

## Run It

```powershell
python -m pytest -q
python -m uvicorn ui_gateway.gateway.server:app --host 127.0.0.1 --port 8765
```

Open `http://127.0.0.1:8765` for the live console.

## Repository Hygiene

Large licensed or generated assets live under ignored local paths, especially `tmp/licensed/umls/2025AB/`. The repo should keep source code, compact docs, profiles, tests, and small durable fixtures. Do not commit full UMLS archives, extracted Metathesaurus tables, run dumps, caches, coverage HTML, or throwaway reports.
