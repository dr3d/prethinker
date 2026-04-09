# SESSIONS (Assembly Log and Migration Guide)

Last updated: 2026-04-09

## Purpose

This file documents how the current `prethinker` workbench was assembled, what changed, what worked, what failed, and how to pull this work back into `prolog-reasoning` with minimal friction.

Use this as the handoff doc for future agents and for repo-to-repo migration.

## Folder Rename Note

- The repo folder name can change without code changes because commands are relative to repo root.
- Existing `kb_runs/*.json`, `hub/*.html`, and prompt snapshot metadata may still show older absolute paths from when those artifacts were generated.
- Treat those embedded paths as historical metadata, then rerender outputs after rename to refresh visible references.

## Scope Achieved

- Tunable Qwen 3.5 9B semantic parsing pipeline (`kb_pipeline.py`)
- Named KB retention semantics with seedless bootstrap behavior
- Progressive rung + acid scenario structure
- Human-readable run reporting (themed transcripts + annotation cards)
- Hub UX for large run sets (search/filter/grouping)
- Prompt/version lineage with per-run provenance and manifests

## Timeline of Major Sessions

## Session 1: Initial Workbench Foundation

Outcome:

- established `prethinker` as a focused semantic parser workbench around the Prethinker model
- kept architecture centered on "LLM suggests structure, deterministic runtime enforces truth"

Key files:

- `kb_pipeline.py`
- `modelfiles/semantic_parser_system_prompt.md`
- `modelfiles/qwen35-9b-semantic-parser.Modelfile`

## Session 2: KB Retention and Ontology Namespace Semantics

Outcome:

- named ontology KBs persisted under `kb_store/<kb-name>/`
- `empty_kb()` policy aligned to user preference:
  - only for brand-new ontology namespaces
  - existing namespaces preload retained corpus

Key behavior:

- seedless bootstrap file created for new namespaces
- retained corpus/profile/index written after successful runs (or when explicitly allowed on fail)

## Session 3: Parser Reliability Layers

Outcome:

- two-pass routing and split extraction paths were enabled
- logic-only extraction plus deterministic refinement implemented
- repair/fallback paths added for invalid/missing model JSON

Key flags:

- `--two-pass` / `--no-two-pass`
- `--split-extraction` / `--no-split-extraction`
- `--prompt-file`

## Session 4: Scenario Ladder and Stress Direction

Outcome:

- progressive rungs formalized:
  - stage 01 facts
  - stage 02 rule ingest
  - stage 03 transitive chain
- acid scenarios added for harder failure slices:
  - long context drift
  - alias pressure
  - temporal correction/retract behavior

Key files:

- `kb_scenarios/*.json`
- `kb_scenarios/README.md`

## Session 5: Human-Readable Rendering and Hub

Outcome:

- imported conversation renderer stack from `prolog-reasoning`
- built run report conversion into transcript pages
- built KB snapshot and rung renderers
- built initial `/hub/index.html`

Key files:

- `scripts/render_dialog_json_html.py`
- `scripts/render_kb_run_html.py`
- `scripts/render_kb_store_html.py`
- `scripts/render_test_ladder_html.py`
- `scripts/build_hub_index.py`

## Session 6: Report Annotation Enrichment

Outcome:

- post-run reports now annotate:
  - why route was selected
  - what KB action was taken
  - extracted elements
  - per-turn score components
  - validation score and row-level pass/fail cards

Implementation:

- annotation payloads emitted by `render_kb_run_html.py`
- annotation cards styled/rendered by `render_dialog_json_html.py`

## Session 7: Prompt Lineage and Reproducibility

Outcome:

- run-level provenance added in `kb_pipeline.py`:
  - `run_id`, timestamps, invocation, model settings
  - `prompt_provenance` (`prompt_id`, sha256, snapshot path, preview)
  - `system_prompt_text`
- immutable prompt snapshots created automatically:
  - `modelfiles/history/prompts/sp-*.md`

## Session 8: Hub Scale-Up for Longitudinal Tuning

Outcome:

- `/hub/index.html` moved from flat listing to run explorer UI
- added search + filters:
  - status, scenario, model, prompt id
- added prompt evolution table with aggregate metrics
- added machine-readable manifests:
  - `hub/data/runs_manifest.json`
  - `hub/data/prompt_versions.json`
- prompt snapshots published to `hub/prompts/*.md`

## Session 9: Baseline Provenance-Aware Smoke Runs

Executed with Ollama `qwen3.5:9b`:

- `kb_runs/stage_01_people_ladder_tune_r1.json` (passed `2/2`)
- `kb_runs/stage_02_people_ladder_tune_r1.json` (passed `1/1`)

Shared prompt version:

- `prompt_id`: `sp-ad589d272fbb`
- source snapshot: `modelfiles/history/prompts/sp-ad589d272fbb.md`
- hub snapshot copy: `hub/prompts/sp-ad589d272fbb.md`

## Session 10: Documentation Consolidation

Outcome:

- updated core docs to current behavior
- created onboarding and migration docs:
  - `AGENT-README.md`
  - this `SESSIONS.md`
  - `NEXT-CODEX.md` (short resume packet for next session)

## What We Learned

## Architecture Lessons

- prompt quality matters, but pipeline guardrails matter more.
- deterministic validation/runtime gates prevent many silent failures.
- extraction quality should be measured by scenario/rung slices, not one aggregate score.

## Model Behavior Lessons (Qwen 3.5 9B)

- strong on straightforward fact/rule/query lanes.
- weaker on pronoun-heavy correction/meta lanes without guardrails.
- fallback parsing and strict validation are necessary for stable operation.

## Knowledge Base Lessons

- persistence by named ontology is useful and should remain default.
- calling `empty_kb()` only for new ontologies aligns with corpus growth goals.
- retract correctness and alias normalization are frequent stress points.

## Evaluation Lessons

- easy rungs can pass while hidden parser drift remains.
- acid scenarios expose failures that simple validations do not.
- prompt lineage is mandatory to avoid repeating bad tuning approaches.

## Known Open Gaps

- stage 03 and harder acid runs can still be slow/fragile depending on model load.
- predicate registry/type enforcement exists but needs deeper production hardening.
- multilingual and enterprise-domain packs are not fully formalized yet.

## Migration Plan Back To `prolog-reasoning`

## Recommended Pull-In Order

1. Pipeline provenance features:
- `kb_pipeline.py`
  - prompt snapshot/versioning
  - run id/timestamp/model settings
  - run report provenance fields

2. Reporting and hub stack:
- `scripts/render_dialog_json_html.py`
- `scripts/render_kb_run_html.py`
- `scripts/build_hub_index.py`
- (optional) `scripts/render_kb_store_html.py`, `scripts/render_test_ladder_html.py`

3. Prompt/version assets:
- `modelfiles/semantic_parser_system_prompt.md`
- `modelfiles/history/prompts/`

4. Scenario packs and docs:
- `kb_scenarios/`
- updated README/doc sections

## Port Validation Checklist

After copying into `prolog-reasoning`, verify:

1. `kb_pipeline.py` still imports MCP server correctly in that repo context.
2. Prompt snapshots are written and reused (`sp-*` files).
3. Run JSON includes:
   - `run_id`
   - `prompt_provenance`
   - `system_prompt_text`
4. `render_kb_run_html.py` shows `run_context` and annotation cards.
5. `build_hub_index.py` generates:
   - `hub/index.html`
   - `hub/data/runs_manifest.json`
   - `hub/data/prompt_versions.json`
6. Smoke pair passes with one prompt id:
   - stage 01 facts
   - stage 02 rule ingest

## Suggested First Port Commands

```bash
# run smoke pair in destination repo
python kb_pipeline.py --backend ollama --base-url http://127.0.0.1:11434 --model qwen3.5:9b --scenario kb_scenarios/stage_01_facts_only.json --kb-name people_ladder_tune --out kb_runs/stage_01_people_ladder_tune_r1.json
python kb_pipeline.py --backend ollama --base-url http://127.0.0.1:11434 --model qwen3.5:9b --scenario kb_scenarios/stage_02_rule_ingest.json --kb-name people_ladder_tune --out kb_runs/stage_02_people_ladder_tune_r1.json

# render + hub
python scripts/render_kb_run_html.py --input kb_runs --output hub/reports --theme standard --docs-hub-link /hub --repo-link ./README.md
python scripts/build_hub_index.py --reports-dir hub/reports --runs-dir kb_runs --kb-pages-dir hub/kb --ladder-index hub/rungs/index.html --output hub/index.html --title "Prethinker Report Hub"
```

## Artifacts To Trust During Future Tuning

Human-facing:

- `hub/index.html`
- `hub/reports/*.html`

Machine-facing:

- `hub/data/runs_manifest.json`
- `hub/data/prompt_versions.json`
- `kb_runs/*.json`

Provenance ground truth:

- `modelfiles/history/prompts/sp-*.md`

## Post-Rename Refresh Steps

Run these from repo root after renaming the folder:

```bash
python scripts/render_kb_run_html.py --input kb_runs --output hub/reports --recursive --theme standard --docs-hub-link /hub --repo-link ./README.md
python scripts/render_kb_store_html.py --kb-root kb_store --output-dir hub/kb --title-prefix "KB Snapshot"
python scripts/render_test_ladder_html.py --scenarios-dir kb_scenarios --runs-dir kb_runs --output-dir hub/rungs --title "Prolog Extraction Test Ladder"
python scripts/build_hub_index.py --reports-dir hub/reports --runs-dir kb_runs --kb-pages-dir hub/kb --ladder-index hub/rungs/index.html --output hub/index.html --title "Prethinker Report Hub"
``` 

## Closeout Note

This repo now has enough structure to run repeated prompt-tuning campaigns without losing history.
When merged back into `prolog-reasoning`, preserve the provenance contract and hub manifests first; they are the highest-leverage pieces for sustained iteration quality.








