# Prethinker

Prethinker is a governed semantic-intake layer for turning natural-language claims into auditable symbolic state.

More concretely, it is a local research workbench for governed Prolog knowledge-base updates. The LLM proposes structured semantic workspaces; deterministic code validates, maps, and applies only the parts that survive policy, schema, and consistency checks.

Current center: a live `ui_gateway` console backed by `src/mcp_server.py`, the `semantic_ir_v1` runtime path with `qwen3.6:35b-a3b`, the bounded `medical@v0` profile, and local UMLS Semantic Network assets.

![Prethinker semantic IR workspace](docs/assets/prethinker-semantic-ir-workspace.png)

## Current State

Read [PROJECT_STATE.md](https://github.com/dr3d/prethinker/blob/main/PROJECT_STATE.md) first. It is the compact, current orientation document for the repo.

The short version:

- `process_utterance()` is the canonical runtime entrypoint.
- The UI is a manual demonstration cockpit, not a marketing page.
- `semantic_ir_v1` is the active architecture pivot: stronger model semantics before deterministic admission.
- `medical@v0` is the main bounded domain profile.
- UMLS is used as a bounded normalization and semantic-type bridge, not as a giant preloaded clinical encyclopedia.
- The Prolog KB is the committed truth layer; model output remains provisional until the runtime admits it.
- Historical reports, old prompt snapshots, and run logs were pruned from the forward-facing tree because Git already preserves them.

## Useful Entry Points

- [PROJECT_STATE.md](https://github.com/dr3d/prethinker/blob/main/PROJECT_STATE.md) - current architecture, demo status, and next frontiers.
- [AGENT-README.md](https://github.com/dr3d/prethinker/blob/main/AGENT-README.md) - fast onboarding for coding agents.
- [docs/PRETHINK_GATEWAY_MVP.md](https://github.com/dr3d/prethinker/blob/main/docs/PRETHINK_GATEWAY_MVP.md) - live gateway shape.
- [docs/PUBLIC_DOCS_GUIDE.md](https://github.com/dr3d/prethinker/blob/main/docs/PUBLIC_DOCS_GUIDE.md) - current public-doc reading map.
- [docs/SEMANTIC_IR_RESEARCH_DIRECTION_REPORT.md](https://github.com/dr3d/prethinker/blob/main/docs/SEMANTIC_IR_RESEARCH_DIRECTION_REPORT.md) - why the project pivoted from parser rescue to semantic workspace.
- [docs/SEMANTIC_IR_MAPPER_SPEC.md](https://github.com/dr3d/prethinker/blob/main/docs/SEMANTIC_IR_MAPPER_SPEC.md) - deterministic mapper/admission contract.
- [docs/UMLS_MVP.md](https://github.com/dr3d/prethinker/blob/main/docs/UMLS_MVP.md) - UMLS bridge and Semantic Network work.
- [docs/MEDICAL_PROFILE.md](https://github.com/dr3d/prethinker/blob/main/docs/MEDICAL_PROFILE.md) - bounded medical profile.
- [docs/FREETHINKER_DESIGN.md](https://github.com/dr3d/prethinker/blob/main/docs/FREETHINKER_DESIGN.md) - optional clarification sidecar.
- [docs/CONSOLE_TRYBOOK.md](https://github.com/dr3d/prethinker/blob/main/docs/CONSOLE_TRYBOOK.md) - prompts for manual demos.
- [ui_gateway/README.md](https://github.com/dr3d/prethinker/blob/main/ui_gateway/README.md) - UI gateway notes.

## Run It

```powershell
python -m pytest -q
python ui_gateway/main.py
```

Open `http://127.0.0.1:8765` for the live console.

## Reproducibility Notes

The public repo currently tracks `29` pytest files under [tests/](https://github.com/dr3d/prethinker/tree/main/tests). The latest local verification before this update was:

```powershell
python -m pytest -q
# 248 passed
```

The UMLS Semantic Network and Metathesaurus-derived runtime assets are intentionally not committed because they depend on licensed source data. The public repo includes the builders, tests, docs, and profile code; outside reproduction of the UMLS lane requires obtaining the licensed UMLS files separately.

## Repository Hygiene

Large licensed or generated assets live under ignored local paths, especially `tmp/licensed/umls/2025AB/`. The repo should keep source code, compact docs, profiles, tests, and small durable fixtures. Do not commit full UMLS archives, extracted Metathesaurus tables, run dumps, caches, coverage HTML, or throwaway reports.
