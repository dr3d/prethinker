# Semantic Parsing Spec (Current)

Last updated: 2026-04-09

## Purpose

This document defines the current semantic parsing behavior implemented in this repository.
It is the authoritative runtime spec for `kb_pipeline.py`.

## Target

Convert natural language utterances into Prolog-compatible structures for deterministic KB actions:

- `assert_fact`
- `assert_rule`
- `query`
- `retract`
- `other` (no KB mutation)

## Runtime Pipeline

1. Route selection
- heuristic route first
- optional model classifier override (`two_pass`)

2. Extraction
- default: split extraction enabled
- pass A: logic-only JSON
- pass B: deterministic refinement to full schema
- fallback: full-schema extractor prompt if pass A fails

3. Validation and repair
- schema + Prolog checks
- optional repair prompt if validation fails
- deterministic fallback parser per route when needed

4. Alignment and constraints
- optional predicate alias alignment from registry
- optional strict registry enforcement
- optional strict type checks

5. KB action dispatch
- deterministic MCP runtime tools (`assert_*`, `retract_*`, `query_rows`)

6. Validation queries
- scenario validations executed after all turns

7. Persistence
- retained corpus/profile written to named ontology namespace
- ontology drift + known matches computed

## Parse Output Shape

Required keys:

- `intent`
- `logic_string`
- `components` (`atoms`, `variables`, `predicates`)
- `facts`
- `rules`
- `queries`
- `confidence` (`overall`, `intent`, `logic`)
- `ambiguities`
- `needs_clarification`
- `rationale`

## Prompting Strategy

Primary prompt source:

- `modelfiles/semantic_parser_system_prompt.md`

Prompt is injected into classifier/extractor/repair prompts.
Temperature is deterministic (`0`) at runtime.

## Provenance and Reproducibility

Each run report now stores:

- `run_id`
- `run_started_utc`, `run_finished_utc`
- invocation argv/cwd
- `model_settings`
- `prompt_provenance`:
  - `prompt_id` (`sp-...`)
  - `prompt_sha256`
  - `snapshot_path`
  - preview and metadata
- `system_prompt_text` (full text used during run)

Prompt snapshots are immutable and saved under:

- `modelfiles/history/prompts/`

## Hub Artifacts

Hub now tracks both run and prompt evolution:

- `hub/index.html`
- `hub/data/runs_manifest.json`
- `hub/data/prompt_versions.json`
- `hub/prompts/*.md` (published prompt snapshots)

Run reports include annotation cards for:

- why turn was routed
- what KB action was applied
- extracted Prolog elements
- per-turn score and validation score

## Recommended Tuning Loop (Qwen 3.5 9B)

1. edit `modelfiles/semantic_parser_system_prompt.md`
2. run smoke pair:
   - `kb_scenarios/stage_01_facts_only.json`
   - `kb_scenarios/stage_02_rule_ingest.json`
3. compare same scenario across `prompt_id` in hub
4. only then advance to:
   - `stage_03_transitive_chain.json`
   - acid scenarios

## Notes

`Chatgpt Ideas.md` is treated as external research/archive material.
This file is the active implementation spec.

