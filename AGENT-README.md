# AGENT README (Onboarding for Coding Agents)

Last updated: 2026-04-23

## Mission

This repo is a semantic parsing workbench focused on one thing:

- convert natural language to Prolog elements with high reliability
- apply extracted logic deterministically into retained named KBs
- measure improvement over repeated rung/acid test runs

Primary model focus right now: `qwen3.5:9b`.

## Current Truth Snapshot

- Read `docs/PROGRESS.md` first for the current status headline.
- Safety gate is green (`142 passed`) on the latest verified batch.
- Strict Blocksworld remains the last verified stable proof lane (`20/20` solve/replay, `8/8` pilot, zero-hit `0`).
- Frozen `process_utterance()` frontier packs now exist for the hardest interactive families.
- Correction frontier is currently `10/12` pass with `2/12` failures left.
- Temporal frontier is currently `8/12` pass, `4/12` warn, `0/12` fail.
- The general registry is populated, so strict narrative runs are now actually constrained.
- The strict mid and upper-mid narrative packs are currently pipeline-green at `3/3`.
- The temporal interrogator recovery narrowed the earlier mid `full` caveat; Glitch temporal remains the clearest active frontier weakness.
- Deprecated rolling handoff files were retired; durable orientation now lives in `README.md`, `docs/`, and `SESSIONS.md`.
- The console is the canonical interactive front door.
- The console UI is also the clearest current manual product surface.
- `Freethinker` is a design-track clarification sidecar with live config/trace scaffolding, but policy remains `off` by default.
- The public docs spine is now the main orientation path; use `SESSIONS.md` as archive, not as the primary handoff.

## Product Vision

The long-term product shape is:

- a UI or adapter layer in front of a user's chatbot of choice
- `Prethinker` watching the interaction stream
- eligible turns compiled into Prolog facts, rules, queries, and retracts
- deterministic symbolic memory retained outside the chatbot's hidden context window

Best short description:

- `Prethinker` is a governed stenographer and compiler.
- `Freethinker` is a bounded clarification liaison.

## Workspace Assumption

- Run commands from repository root (current folder), not from hard-coded absolute paths.
- Historical run artifacts may contain absolute local paths from the machine that generated them.
- If the folder is renamed, rerender hub artifacts so displayed paths and manifests stay current.

## Explain It To A Human (Short Version)

"This system treats the LLM like a parser, not a reasoner. The model proposes logic (`facts`, `rules`, `queries`, `retracts`), the runtime validates and applies it via deterministic Prolog tools, and every run is tracked with exact prompt/version provenance so we can tune and compare objectively over time."

## First Files To Read

1. `README.md`
2. `docs/PRETHINKER.md`
3. `docs/EXPLAINER.md`
4. `docs/PRETHINK_GATEWAY_MVP.md`
5. `docs/FREETHINKER_DESIGN.md`
6. `docs/ONTOLOGY_STEERING.md`
7. `docs/PROGRESS.md`
8. `docs/FOCUS_EXECUTION_PLAN.md`
9. `docs/PROCESS_UTTERANCE_FRONTIER_PACKS.md`
10. `docs/reports/PROCESS_UTTERANCE_PIPELINE_BATCH_2026-04-20.md`
11. `kb_pipeline.py`
12. `src/mcp_server.py`
13. `modelfiles/semantic_parser_system_prompt.md`
14. `kb_scenarios/README.md`
15. `scripts/render_kb_run_html.py`
16. `scripts/build_hub_index.py`
17. `engine/constraint_propagation.py`
18. `engine/propagation_runner.py`

## Fast Resume (Single-Page Handoff)

- Primary target model: `qwen3.5:9b` (Ollama).
- Editable prompt source: `modelfiles/semantic_parser_system_prompt.md`.
- Current baseline loop:
1. Run `python scripts/run_safety_gate.py`.
2. Re-read `docs/PROGRESS.md` and the latest post-registry reports before claiming improvement.
3. Treat strict Blocksworld as the stable lane and the narrative packs as the frontier that must stay honestly reported.
- Current product-shape loop:
1. Treat `src/mcp_server.py` `process_utterance()` as the canonical interactive entryway.
2. Treat `ui_gateway/` as the manual test cockpit for that entryway.
3. Treat `Freethinker` as optional and currently non-authoritative.
- The old higher narrative strict scores (`0.6452`, `0.8718`) are historical/provisional only.
- The current verified interactive frontier batch is `docs/reports/PROCESS_UTTERANCE_PIPELINE_BATCH_2026-04-20.md`.
- The current verified frontier-pack contract is `docs/PROCESS_UTTERANCE_FRONTIER_PACKS.md`.
- The current verified temporal interrogator recovery is `docs/reports/TEMPORAL_INTERROGATOR_RECOVERY_2026-04-19.md`.
- Provenance fields must remain present in runs:
  - `run_id`
  - `prompt_provenance`
  - `system_prompt_text`

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
5. deterministic local core KB apply (default runtime)
6. deterministic validation queries
7. retained corpus/profile persistence
8. run report with prompt/model provenance

Separate local propagation layer (not yet pipeline-wired):

- `engine/constraint_propagation.py` (known-state + DoF propagation)
- `engine/propagation_schema.py` (state/rule/constraint types)
- `engine/propagation_runner.py` (JSON problem runner)

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

## Frontier Orchestration Contract (Agent54 + Gate Curator)

Use a two-role operating model to keep the ladder moving without bloating must-run retests.

Role A: `Agent54` (Rung Author)
- Add frontier rungs at the edge of current failures (height and/or width).
- Ensure each new rung has deterministic validations and clear expected outcomes.
- Register new rungs in `kb_scenarios/tracks.json` in the intended frontier lane.
- Deliver one short "what this rung tests" note with each added rung.

Role B: Gate Curator (Retest Pruner)
- Remove low-signal rungs from strict gate retest packs when they are repeatedly redundant.
- Keep at least one anchor rung per failure class (do not prune entire behavior classes).
- Prefer promoting harder successor rungs and demoting older easy duplicates to non-gating tracks.
- Maintain a lean gate set that maximizes new-signal-per-minute.

Prune criteria (default)
- No novel failures across at least 3 consecutive frontier sweeps.
- Behavior is covered by a newer/harder rung with the same semantic target.
- Runtime cost is materially high relative to diagnostic value.

LM Studio vs Ollama operating pattern:

- LM Studio: use stock model + `--prompt-file` for fast prompt iteration.
- Ollama: periodically rebake `qwen35-semparse:9b` from latest prompt via `scripts/rebake_semparse.ps1`.
- Always confirm rebaked tag with `ollama show qwen35-semparse:9b` before reporting baked-prompt results.
- Clarification Q&A can use a separate model via:
  `--clarification-answer-model`, `--clarification-answer-backend`, and `--clarification-answer-context-length`.

## Command Quickstart

```bash
# 0) from repo root
cd <repo-root>

# quick engine regression sanity check
python scripts/run_engine_regression.py

# 1) check Ollama
powershell -Command "Invoke-RestMethod -Method Get -Uri http://127.0.0.1:11434/api/tags"

# 2) smoke run A
python kb_pipeline.py --backend ollama --base-url http://127.0.0.1:11434 --model qwen3.5:9b --scenario kb_scenarios/stage_01_facts_only.json --kb-name people_ladder_tune --out kb_runs/stage_01_people_ladder_tune_rN.json

# 3) smoke run B
python kb_pipeline.py --backend ollama --base-url http://127.0.0.1:11434 --model qwen3.5:9b --scenario kb_scenarios/stage_02_rule_ingest.json --kb-name people_ladder_tune --out kb_runs/stage_02_people_ladder_tune_rN.json

# 4) render reports
python scripts/render_kb_run_html.py --input kb_runs --output docs/reports --theme standard --docs-hub-link ../index.html --repo-link ./README.md

# 5) rebuild run explorer + manifests
# (this writes docs/run-reports-hub.html; docs/index.html remains the curated landing page)
python scripts/build_hub_index.py --reports-dir docs/reports --runs-dir kb_runs --kb-pages-dir docs/kb --ladder-index docs/rungs/index.html --output docs/run-reports-hub.html --title "Prethinker Report Hub"

# 6) run propagation example
python -m engine.propagation_runner --problem-json kb_scenarios/propagation_problem.example.json
```

## Where To Inspect Results

- run JSONs: `kb_runs/*.json`
- run transcripts: `docs/reports/*.html`
- docs landing page: `docs/index.html`
- docs run explorer: `docs/run-reports-hub.html`
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

If this work is moved into another repo, use `SESSIONS.md` as the migration playbook and checklist.

## Post-Rename Refresh

After a folder rename, refresh rendered docs so embedded paths are coherent:

```bash
python scripts/render_kb_run_html.py --input kb_runs --output docs/reports --recursive --theme standard --docs-hub-link ../index.html --repo-link ./README.md
python scripts/render_kb_store_html.py --kb-root kb_store --output-dir docs/kb --title-prefix "KB Snapshot"
python scripts/render_test_ladder_html.py --scenarios-dir kb_scenarios --runs-dir kb_runs --output-dir docs/rungs --title "Prolog Extraction Test Ladder"
python scripts/build_hub_index.py --reports-dir docs/reports --runs-dir kb_runs --kb-pages-dir docs/kb --ladder-index docs/rungs/index.html --output docs/run-reports-hub.html --title "Prethinker Report Hub"
```


