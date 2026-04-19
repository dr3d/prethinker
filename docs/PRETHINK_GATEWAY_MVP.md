# Prethinker Console

This note documents the `Prethinker Console` front door in `ui_gateway/`.

## Purpose

Provide a lightweight product embodiment of Prethinker as a front-door console plus chat UI while still exercising the shared interactive GIC entry path.

## Current Shape

- browser UI served from `ui_gateway/static`
- local stdlib HTTP server in `ui_gateway/gateway/server.py`
- `POST /api/prethink` returns a phaseful envelope:
  - `ingest`
  - `clarify`
  - `commit`
  - `answer`
- config persisted in `ui_gateway/state/gateway_config.json`
- runtime path now uses the canonical `process_utterance()` server entryway plus deterministic core tool execution
- strict bouncer invariants now enforced when `strict_mode=true`

## Default Binding Choices

- compiler model: `qwen35-semparse:9b`
- compiler mode: `strict`
- compiler backend: `ollama`
- compiler base URL: `http://127.0.0.1:11434`
- served handoff mode in strict mode: `never`

## MITM Status

- `RuntimeHooks.front_door()` uses real `pre_think`.
- deterministic tool path is live (`assert_fact`, `assert_rule`, `retract_fact`, `query_rows`).
- served-LLM handoff exists but is intentionally disabled in strict mode.
- session trace export is available at `GET /api/session/state?session_id=...`.
- batch runner is available: `scripts/run_gateway_turnset.py`.

## Deliberate Limits

- No auth, persistence, or streaming yet
- No multi-user isolation guarantees yet (single local process MVP)
