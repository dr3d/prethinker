# Prethink Gateway MVP

This note documents the isolated scaffold in `ui_gateway/`.

## Purpose

Provide a lightweight product embodiment of Prethinker as a front-door gateway plus chat UI without touching the existing training lane.

## Current Shape

- browser UI served from `ui_gateway/static`
- local stdlib HTTP server in `ui_gateway/gateway/server.py`
- `POST /api/prethink` returns a phaseful envelope:
  - `ingest`
  - `clarify`
  - `commit`
  - `answer`
- config persisted in `ui_gateway/state/gateway_config.json`
- runtime path now uses strict compiler routing plus deterministic core tool execution

## Default Binding Choices

- compiler model: `qwen35-semparse:9b`
- compiler mode: `strict`
- compiler backend: `ollama`
- compiler base URL: `http://127.0.0.1:11434`

## Intended MITM Upgrade Path

1. Replace `RuntimeHooks.front_door()` with real `pre_think` calls.
2. Replace `RuntimeHooks.stage_commit()` with deterministic runtime tools.
3. Replace `RuntimeHooks.answer()` with the served-LLM call after commit gates pass.
4. Add durable session state and authenticated multi-user handling.
5. Add provenance so every answer shows which facts, rules, or clarification steps were used.

Status:

- Step 1 complete.
- Step 2 complete (`assert_fact`, `assert_rule`, `retract_fact`, `query_rows`).
- Step 3 pending (served-LLM call is still represented in envelope text only).
- Step 4 pending.
- Step 5 partially present via phase payloads; full provenance cards pending.

## Deliberate Limits

- No remote MCP transport yet (local gateway only)
- No served-LLM callout yet after deterministic pass
- No auth, persistence, or streaming yet
