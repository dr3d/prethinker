# Prethinker Semantic Parser Workbench

This project is a local workbench for building a high-accuracy semantic parser (Qwen 3.5 9B first) that converts natural language into Prolog-ready logic and applies it into named, persistent knowledge bases.

Last updated: 2026-04-09

## Honest Snapshot (For NSAI Readers)

Prethinker is a neuro-symbolic parsing workbench, not a finished parser product.

- Problem focus: map free-form language into executable symbolic operations (`assert_fact`, `assert_rule`, `query`, `retract`) and apply them deterministically to persistent KBs.
- Core approach: hybrid pipeline where the model proposes structure, then deterministic runtime logic refines, validates, and applies through MCP runtime tools.
- What is solid today: architecture, provenance, prompt/version lineage, scenario ladder, and observability (`kb_runs` + HTML docs/report views).
- What is not proven yet: broad generalization on hard inputs (transitivity, quantifiers, negation policy, pronoun ambiguity, unseen vocabulary).
- Current evidence level: early; passing smoke-to-mid ladder checks, but still small sample counts.

This is an open research effort and learning artifact, not a startup pitch.
If you're evaluating it as a research workbench, it's useful now. If you're evaluating it as production-grade semantic parsing, it's still early.

## Goals

- Build a robust semantic parser for `assert_fact`, `assert_rule`, `query`, `retract`, and `other`.
- Keep ontology/KB evolution persistent across runs.
- Start seed-light (or seedless) and grow ontology from observed utterances.
- Validate all ingestion via deterministic MCP runtime tools.
- Progress from simple scenarios to acid-test scenarios.

## Current State

- Qwen 3.5 9B prompt + Modelfile exists for local Ollama use.
- End-to-end runtime pipeline exists in `kb_pipeline.py`.
- Two-step parse mode is enabled by default:
  1. route classification
  2. split extraction (logic-only pass, then deterministic schema refinement)
- Named KB namespaces are retained under `kb_store/<kb-name>/`.
- `empty_kb()` is only used for brand-new ontology namespaces (unless forced).
- Scenario validation harness and progressive ladder are in place.
- Run provenance now captures prompt snapshot/version hash + model settings per run.
- Docs index now generates searchable run/prompt manifests for longitudinal tuning.
- Latest verified tune runs:
  - `kb_runs/stage_01_people_ladder_tune_r1.json` (passed `2/2`)
  - `kb_runs/stage_02_people_ladder_tune_r1.json` (passed `1/1`)

## Current Best Settings (Qwen 3.5 9B)

- Active prompt pack (source of truth):
  - `modelfiles/semantic_parser_system_prompt.md`
- Modelfile:
  - `modelfiles/qwen35-9b-semantic-parser.Modelfile`
- Latest validated prompt snapshot:
  - `modelfiles/history/prompts/sp-ad589d272fbb.md`
- Hub-published prompt snapshot:
  - `docs/prompts/sp-ad589d272fbb.md`

## Model Adaptation Stance (Prompt-First, LoRA Later)

- Current priority is system-prompt and runtime-policy quality, measured via scenario evidence.
- Planned training stack is Unsloth-style LoRA fine-tuning once prompt/runtime behavior stabilizes.
- LoRA outputs will be sanity-checked against the same benchmark ladder used for prompt iterations.
- GGUF packaging is treated as deployment format work after behavior is validated (not as a substitute for evaluation).

## High-Level Architecture

1. Input utterance(s) from scenario JSON.
2. Route decision (`assert_fact|assert_rule|query|retract|other`).
3. Parse pipeline:
   - logic-only extraction
   - deterministic refinement to full schema
   - repair/fallback when needed
4. Deterministic apply via MCP server runtime methods:
   - `assert_fact`
   - `assert_rule`
   - `retract_fact`
   - `query_rows`
5. Validation pass (`query_rows` checks against expected status/rows).
6. Persist corpus/profile and emit run report.

## Repository Layout

- `kb_pipeline.py`: main orchestration script.
- `scripts/render_kb_run_html.py`: converts `kb_runs/*.json` into themed transcript HTML.
- `scripts/render_dialog_json_html.py`: shared transcript renderer (ported in-repo).
- `modelfiles/`: model and prompt assets.
  - `qwen35-9b-semantic-parser.Modelfile`
  - `semantic_parser_system_prompt.md` (human-editable prompt pack)
  - `qwen35-9b-findings.md`
  - `test-lmstudio-semparse.ps1`
- `kb_scenarios/`: scenario inputs + validation contracts.
- `kb_store/`: persistent named KB namespaces and ontology metadata.
- `kb_runs/`: JSON run reports.
- `docs/`: generated reports, ladder pages, KB snapshots, and prompt lineage manifests.
- `ROADMAP.md`: near-term execution plan and acceptance criteria.

## Requirements

- Python 3.10+
- Access to local model server:
  - Ollama (`http://127.0.0.1:11434`) or
  - LM Studio (`http://127.0.0.1:1234`)
- If LM Studio auth is enabled, set one of:
  - `LM_API_TOKEN` (LM Studio native), or
  - `LMSTUDIO_API_KEY` / `PRETHINKER_API_KEY`
- No sibling repo is required for default runs (`--runtime none`, parse-only apply path).
- Optional only: `--runtime mcp` can integrate with a Prolog MCP runtime when explicitly configured.

## Quick Start

### 1) Run a basic scenario (Ollama)

```bash
python kb_pipeline.py --backend ollama --base-url http://127.0.0.1:11434 --model qwen3.5:9b --scenario kb_scenarios/kb_positive.json --kb-name people_core --out kb_runs/kb_positive_ollama_people_core.json
```

### 2) Run retract scenario on same named KB

```bash
python kb_pipeline.py --backend ollama --base-url http://127.0.0.1:11434 --model qwen3.5:9b --scenario kb_scenarios/kb_with_retract.json --kb-name people_core --out kb_runs/kb_with_retract_ollama_people_core.json
```

### 3) Run progressive ladder

```bash
python kb_pipeline.py --backend ollama --base-url http://127.0.0.1:11434 --model qwen3.5:9b --scenario kb_scenarios/stage_01_facts_only.json --kb-name people_ladder --out kb_runs/stage_01_people_ladder.json
python kb_pipeline.py --backend ollama --base-url http://127.0.0.1:11434 --model qwen3.5:9b --scenario kb_scenarios/stage_02_rule_ingest.json --kb-name people_ladder --out kb_runs/stage_02_people_ladder.json
python kb_pipeline.py --backend ollama --base-url http://127.0.0.1:11434 --model qwen3.5:9b --scenario kb_scenarios/stage_03_transitive_chain.json --kb-name people_ladder --out kb_runs/stage_03_people_ladder.json
```

### 4) Tune prompt without code edits

Edit:

- `modelfiles/semantic_parser_system_prompt.md`

Then run with:

```bash
python kb_pipeline.py --backend ollama --base-url http://127.0.0.1:11434 --model qwen3.5:9b --prompt-file modelfiles/semantic_parser_system_prompt.md --scenario kb_scenarios/stage_02_rule_ingest.json --kb-name people_ladder --out kb_runs/stage_02_people_ladder_prompt_tuned.json
```

Each run now stores:

- `prompt_provenance.prompt_id` (`sp-...` hash id)
- `prompt_provenance.snapshot_path` (immutable prompt copy)
- `system_prompt_text` (full prompt used for that run)
- `model_settings` (context, timeout, split/two-pass flags, strict flags)

### 4b) Optional registry/type enforcement for extraction

```bash
python kb_pipeline.py --backend ollama --base-url http://127.0.0.1:11434 --model qwen3.5:9b --scenario kb_scenarios/stage_02_rule_ingest.json --kb-name people_ladder --predicate-registry modelfiles/predicate_registry.json --strict-registry --type-schema modelfiles/type_schema.example.json --strict-types --out kb_runs/stage_02_people_ladder_strict.json
```

Starter files:

- `modelfiles/predicate_registry.json`
- `modelfiles/type_schema.example.json`

### 5) Render test runs as themed HTML transcripts

```bash
# single run -> single html
python scripts/render_kb_run_html.py --input kb_runs/stage_02_people_ladder_v4_split.json --output kb_runs/stage_02_people_ladder_v4_split.html --theme telegram --keep-dialog-json

# whole folder -> html mirror tree
python scripts/render_kb_run_html.py --input kb_runs --output kb_runs/html --recursive --theme standard
```

The renderer supports three skins (`standard`, `telegram`, `imessage`) and each page includes light/dark appearance toggle, for 6 appearance combinations.

### 6) Build docs front page

```bash
# render all run JSONs into docs/reports
python scripts/render_kb_run_html.py --input kb_runs --output docs/reports --recursive --theme standard

# render persistent KB corpora into docs/kb pages
python scripts/render_kb_store_html.py --kb-root kb_store --output-dir docs/kb --title-prefix "KB Snapshot"

# render human-readable rung pages from ladder scenarios + latest runs
python scripts/render_test_ladder_html.py --scenarios-dir kb_scenarios --runs-dir kb_runs --output-dir docs/rungs --title "Prolog Extraction Test Ladder"

# build docs/index.html + run/prompt manifests
python scripts/build_hub_index.py --reports-dir docs/reports --runs-dir kb_runs --kb-pages-dir docs/kb --ladder-index docs/rungs/index.html --output docs/index.html --title "Prethinker Report Hub"
```

`docs/index.html` is intentionally light/dark only (not conversation skins).
It now includes run filtering/search and prompt-evolution tables.
Manifests are generated at:

- `docs/data/runs_manifest.json`
- `docs/data/prompt_versions.json`
- prompt snapshots mirrored to `docs/prompts/*.md`

## Key Runtime Semantics

- New ontology namespace:
  - creates seedless bootstrap file
  - calls `empty_kb()` once for clean start
- Existing namespace:
  - does not call `empty_kb()` by default
  - preloads retained corpus clauses into runtime
- Dedup behavior:
  - re-asserting existing fact/rule is skipped
  - retracting absent fact returns `no_results`

## Scenario Contract

Each scenario JSON contains:

- `name`
- `utterances`: list of NL turns
- `validations`: list of checks using `query_rows`

Validation supports:

- `expect_status`
- `min_rows` / `max_rows`
- `contains_row`

See `kb_scenarios/README.md` for details.

## What Was Implemented In This Iteration

- Seed-light named KB persistence and namespace organization.
- Ontology profile generation and drift detection per run.
- Gear-change signals in report output.
- Split extraction path (logic-only -> deterministic refinement).
- Prompt-file loading for maintainable system prompt tuning.
- Prompt snapshot/version lineage (`prompt_id`, sha, immutable snapshot files).
- Fallback handling improvements for parser failure slices.
- Progressive scenario ladder for controlled complexity ramp.
- Added `kb_run -> html` conversion flow with in-repo transcript renderer stack.
- Docs run explorer with filters + prompt evolution table + JSON manifests.

## Known Gaps

- Stage 3 transitive-chain scenario can be slow/time out depending on model/server load.
- Predicate alignment registry layer is drafted but not fully wired into runtime yet.
- Multilingual stress pack is documented in notes but not yet formalized in `kb_scenarios/`.

## Suggested Next Steps

1. Finalize and enable predicate-registry alignment (canonical names + aliases).
2. Add multilingual stress scenarios (EN/ES/FR/DE/ZH) with strict expected outputs.
3. Add candidate-voting mode (`N` parses + validator select) for harder utterances.
4. Add ontology-specific validation gates for pharma/finance/compliance domains.
5. Build acid-test suites for transitivity, quantifiers, negation policy, and pronoun ambiguity.

## Useful Files

- Prompt pack: `modelfiles/semantic_parser_system_prompt.md`
- Agent onboarding: `AGENT-README.md`
- Session/migration log: `SESSIONS.md`
- Next-session handoff: `AGENT-README.md`
- Execution roadmap: `ROADMAP.md`
- Pipeline: `kb_pipeline.py`
- KB run HTML renderer: `scripts/render_kb_run_html.py`
- Shared theme renderer: `scripts/render_dialog_json_html.py`
- Modelfile: `modelfiles/qwen35-9b-semantic-parser.Modelfile`
- Findings: `modelfiles/qwen35-9b-findings.md`
- Scenarios: `kb_scenarios/`
- Runs: `kb_runs/`





