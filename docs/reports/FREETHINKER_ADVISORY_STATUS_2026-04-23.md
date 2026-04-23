# Freethinker Advisory Status

Date: 2026-04-23

## Summary

Freethinker is now live in the canonical console path as a bounded second-model clarification sidecar.

This is not a broad authority expansion. The main design rule still holds:

- `Prethinker` decides whether a turn may commit
- `Freethinker` only helps when `Prethinker` has already reported ambiguity

## What Is Live Now

- `process_utterance()` can now call a separate Freethinker model path when clarification is required
- Freethinker has its own:
  - model
  - backend
  - base URL
  - context length
  - timeout
  - temperature
  - think on/off flag
  - prompt file
- the console config panel now exposes those settings
- the console has a one-click `Enable Freethinker Advisory` preset
- debug mode now shows:
  - Freethinker prompt/context
  - Freethinker JSON decision

## Current Policy Behavior

- `off`
  - current baseline behavior
  - no watcher attempt
- `advisory_only`
  - Freethinker may improve or replace the clarification question
  - Freethinker may suggest a grounded answer, but the user still gets asked
- `grounded_reference`
  - Freethinker may auto-resolve only when confidence and grounding are strong enough
  - the resolved answer is still fed back through the normal Prethinker parse/apply path
- `conservative_contextual`
  - same bounded mechanism, but with a looser resolution threshold than `grounded_reference`

## Current Safety Boundary

Freethinker still does **not**:

- write directly to the KB
- bypass Prethinker
- replace the deterministic runtime
- invent missing user intent

It remains a liaison, not an authority.

## Why This Matters

The strongest justification for Freethinker is still pronoun-heavy and context-carrying language:

- `he`
- `she`
- `they`
- short follow-up turns
- clarification wording that should be more human than the raw compiler question

That is where Prethinker’s necessary brittleness is most visible, and where a bounded watcher has the best chance to help without weakening commit discipline.

## Verification

Focused checks covering the live Freethinker path are green:

- `python -m pytest tests/test_mcp_server.py tests/test_gateway_config.py -q`
  - `50 passed`
- `node --check ui_gateway/static/app.js`
- `python -m py_compile src/mcp_server.py ui_gateway/gateway/config.py ui_gateway/gateway/runtime_hooks.py kb_pipeline.py`

## Honest Current Read

This is the correct first live shape:

- real second-model path
- advisory-first rollout
- visible trace
- default policy still `off`

What is **not** proven yet is whether Freethinker materially reduces clarification pain across a real pronoun frontier pack. That is the next evidence step.
