# AGENT README (Onboarding for Coding Agents)

Last updated: 2026-04-09

## Mission

This repo is a semantic parsing workbench focused on one thing:

- convert natural language to Prolog elements with high reliability
- apply extracted logic deterministically into retained named KBs
- measure improvement over repeated rung/acid test runs

Primary model focus right now: `qwen3.5:9b`.

## Workspace Assumption

- Run commands from repository root (current folder), not from hard-coded absolute paths.
- Historical run artifacts may contain absolute local paths from the machine that generated them.
- If the folder is renamed, rerender hub artifacts so displayed paths and manifests stay current.

## Explain It To A Human (Short Version)

"This system treats the LLM like a parser, not a reasoner. The model proposes logic (`facts`, `rules`, `queries`, `retracts`), the runtime validates and applies it via deterministic Prolog tools, and every run is tracked with exact prompt/version provenance so we can tune and compare objectively over time."

## First Files To Read

1. `README.md`
2. `Semantic Parsing.md`
3. `kb_pipeline.py`
4. `modelfiles/semantic_parser_system_prompt.md`
5. `kb_scenarios/README.md`
6. `scripts/render_kb_run_html.py`
7. `scripts/build_hub_index.py`
8. `NEXT-CODEX.md` (fast session resume packet)

## Core Invariants

- Keep focus on Prolog element extraction quality:
  - terms/constants, variables, predicates, facts, rules, queries
- Named ontology KBs are retained:
  - `empty_kb()` only for brand-new ontology namespaces (unless explicitly forced)
- Do not rely on large pre-seeded ontology encyclopedias for parser quality.
- Prompt tuning must be measured with scenarios, not judged by one-off impressions.
- Every meaningful run should be provenance-traceable.

## Runtime Architecture (Current)

`kb_pipeline.py`:

1. route selection (heuristic + optional model classifier)
2. split extraction (logic-only pass, deterministic refinement)
3. schema/prolog validation and optional repair prompt
4. optional registry/type checks
5. deterministic MCP KB apply
6. deterministic validation queries
7. retained corpus/profile persistence
8. run report with prompt/model provenance

## Provenance Contract (Required For Tuning)

Each run JSON should include:

- `run_id`
- `run_started_utc`, `run_finished_utc`
- `model_settings`
- `prompt_provenance` (`prompt_id`, `prompt_sha256`, `snapshot_path`)
- `system_prompt_text`

Prompt snapshots live in:

- `modelfiles/history/prompts/`

Hub publishing mirrors snapshots to:

- `docs/prompts/`

## Standard Tuning Loop

1. Edit prompt:
- `modelfiles/semantic_parser_system_prompt.md`

2. Run smoke pair (always):
- `kb_scenarios/stage_01_facts_only.json`
- `kb_scenarios/stage_02_rule_ingest.json`

3. Render and index:
- `scripts/render_kb_run_html.py`
- `scripts/build_hub_index.py`

4. Compare in hub:
- filter by scenario + `prompt_id`
- check status, validation rate, and turn-level parser/apply behavior

5. Only then move up to:
- `stage_03_transitive_chain.json`
- acid scenarios

## Command Quickstart

```bash
# 0) from repo root
cd <repo-root>

# 1) check Ollama
powershell -Command "Invoke-RestMethod -Method Get -Uri http://127.0.0.1:11434/api/tags"

# 2) smoke run A
python kb_pipeline.py --backend ollama --base-url http://127.0.0.1:11434 --model qwen3.5:9b --scenario kb_scenarios/stage_01_facts_only.json --kb-name people_ladder_tune --out kb_runs/stage_01_people_ladder_tune_rN.json

# 3) smoke run B
python kb_pipeline.py --backend ollama --base-url http://127.0.0.1:11434 --model qwen3.5:9b --scenario kb_scenarios/stage_02_rule_ingest.json --kb-name people_ladder_tune --out kb_runs/stage_02_people_ladder_tune_rN.json

# 4) render reports
python scripts/render_kb_run_html.py --input kb_runs --output docs/reports --theme standard --docs-hub-link ../index.html --repo-link ./README.md

# 5) rebuild hub + manifests
python scripts/build_hub_index.py --reports-dir docs/reports --runs-dir kb_runs --kb-pages-dir docs/kb --ladder-index docs/rungs/index.html --output docs/index.html --title "Prethinker Report Hub"
```

## Where To Inspect Results

- run JSONs: `kb_runs/*.json`
- run transcripts: `docs/reports/*.html`
- docs index: `docs/index.html`
- run manifest: `docs/data/runs_manifest.json`
- prompt manifest: `docs/data/prompt_versions.json`

## Known Legacy vs Current

Current:

- runs with `prompt_provenance.prompt_id` like `sp-...`
- reports with `run_context` + annotation cards
- hub with filters/search and prompt evolution table

Legacy:

- older runs may show `legacy-unknown` or `legacy-file-only` prompt IDs
- older runs may be missing `run_id` and full provenance fields

## Common Pitfalls

- Running render and hub build in parallel can produce stale/partial indexes.
- Passing rung validation does not imply parser correctness on harder slices.
- A run can have `overall_status=failed` despite validation rows passing if parse/apply failures occurred in turns.
- Acid scenarios can expose alias and normalization drift that basic rungs miss.

## Human-Facing Status Template

When reporting progress, include:

1. prompt id tested
2. scenarios run
3. pass/fail and validation totals
4. notable parser behavior changes
5. explicit next rung or rollback decision

## Porting Note

If this work is moved back into `prolog-reasoning`, use `SESSIONS.md` as the migration playbook and checklist.

## Post-Rename Refresh

After a folder rename, refresh rendered docs so embedded paths are coherent:

```bash
python scripts/render_kb_run_html.py --input kb_runs --output docs/reports --recursive --theme standard --docs-hub-link ../index.html --repo-link ./README.md
python scripts/render_kb_store_html.py --kb-root kb_store --output-dir docs/kb --title-prefix "KB Snapshot"
python scripts/render_test_ladder_html.py --scenarios-dir kb_scenarios --runs-dir kb_runs --output-dir docs/rungs --title "Prolog Extraction Test Ladder"
python scripts/build_hub_index.py --reports-dir docs/reports --runs-dir kb_runs --kb-pages-dir docs/kb --ladder-index docs/rungs/index.html --output docs/index.html --title "Prethinker Report Hub"
```


