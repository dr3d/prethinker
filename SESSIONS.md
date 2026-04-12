# SESSIONS (Assembly Log and Migration Guide)

Last updated: 2026-04-12

## Purpose

This file documents how the current `prethinker` workbench was assembled, what changed, what worked, what failed, and how to pull this work back into `prolog-reasoning` with minimal friction.

Use this as the handoff doc for future agents and for repo-to-repo migration.

## Folder Rename Note

- The repo folder name can change without code changes because commands are relative to repo root.
- Existing `kb_runs/*.json`, `docs/*.html`, and prompt snapshot metadata may still show older absolute paths from when those artifacts were generated.
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
- built initial `/docs/index.html`

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

- `/docs/index.html` moved from flat listing to run explorer UI
- added search + filters:
  - status, scenario, model, prompt id
- added prompt evolution table with aggregate metrics
- added machine-readable manifests:
  - `docs/data/runs_manifest.json`
  - `docs/data/prompt_versions.json`
- prompt snapshots published to `docs/prompts/*.md`

## Session 9: Baseline Provenance-Aware Smoke Runs

Executed with Ollama `qwen3.5:9b`:

- `kb_runs/stage_01_people_ladder_tune_r1.json` (passed `2/2`)
- `kb_runs/stage_02_people_ladder_tune_r1.json` (passed `1/1`)

Shared prompt version:

- `prompt_id`: `sp-ad589d272fbb`
- source snapshot: `modelfiles/history/prompts/sp-ad589d272fbb.md`
- hub snapshot copy: `docs/prompts/sp-ad589d272fbb.md`

## Session 10: Documentation Consolidation

Outcome:

- updated core docs to current behavior
- created onboarding and migration docs:
  - `AGENT-README.md`
  - this `SESSIONS.md`
  - `NEXT-CODEX.md` (later consolidated into `AGENT-README.md`)

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
   - `docs/index.html`
   - `docs/data/runs_manifest.json`
   - `docs/data/prompt_versions.json`
6. Smoke pair passes with one prompt id:
   - stage 01 facts
   - stage 02 rule ingest

## Suggested First Port Commands

```bash
# run smoke pair in destination repo
python kb_pipeline.py --backend ollama --base-url http://127.0.0.1:11434 --model qwen3.5:9b --scenario kb_scenarios/stage_01_facts_only.json --kb-name people_ladder_tune --out kb_runs/stage_01_people_ladder_tune_r1.json
python kb_pipeline.py --backend ollama --base-url http://127.0.0.1:11434 --model qwen3.5:9b --scenario kb_scenarios/stage_02_rule_ingest.json --kb-name people_ladder_tune --out kb_runs/stage_02_people_ladder_tune_r1.json

# render + hub
python scripts/render_kb_run_html.py --input kb_runs --output docs/reports --theme standard --docs-hub-link ../index.html --repo-link ./README.md
python scripts/build_hub_index.py --reports-dir docs/reports --runs-dir kb_runs --kb-pages-dir docs/kb --ladder-index docs/rungs/index.html --output docs/index.html --title "Prethinker Report Hub"
```

## Artifacts To Trust During Future Tuning

Human-facing:

- `docs/index.html`
- `docs/reports/*.html`

Machine-facing:

- `docs/data/runs_manifest.json`
- `docs/data/prompt_versions.json`
- `kb_runs/*.json`

Provenance ground truth:

- `modelfiles/history/prompts/sp-*.md`

## Post-Rename Refresh Steps

Run these from repo root after renaming the folder:

```bash
python scripts/render_kb_run_html.py --input kb_runs --output docs/reports --recursive --theme standard --docs-hub-link ../index.html --repo-link ./README.md
python scripts/render_kb_store_html.py --kb-root kb_store --output-dir docs/kb --title-prefix "KB Snapshot"
python scripts/render_test_ladder_html.py --scenarios-dir kb_scenarios --runs-dir kb_runs --output-dir docs/rungs --title "Prolog Extraction Test Ladder"
python scripts/build_hub_index.py --reports-dir docs/reports --runs-dir kb_runs --kb-pages-dir docs/kb --ladder-index docs/rungs/index.html --output docs/index.html --title "Prethinker Report Hub"
``` 

## Closeout Note

This repo now has enough structure to run repeated prompt-tuning campaigns without losing history.
When merged back into `prolog-reasoning`, preserve the provenance contract and hub manifests first; they are the highest-leverage pieces for sustained iteration quality.

## Session 11: Standalone Runtime, Backend Validation, and Repo Cleanup

Date: 2026-04-10 UTC

Outcome:

- made `kb_pipeline.py` standalone by default (`--runtime none`) with optional MCP mode only when requested
- added parse-only runtime path and skip-validation behavior for parse-only mode
- removed hard dependency on sibling `prolog-reasoning` for default runs
- validated both backends on current code:
  - Ollama (`qwen3.5:9b`) passed smoke run
  - LM Studio (`qwen/qwen3.5-9b`) passed smoke run after auth + fallback hardening
- added LM Studio token fallback support via `LM_API_TOKEN`
- added possessive fallback parse (`my <relation> is <entity>`) to reduce non-JSON extractor failures
- added one-command rebake script:
  - `scripts/rebake_semparse.ps1`
- established `tmp/` workspace usage to keep root clean:
  - moved root `.tmp*` artifacts into `tmp/`
  - updated ignore rules for `tmp/`
- consolidated handoff docs to avoid redundancy:
  - `NEXT-CODEX.md` renamed/removed from root workflow
  - `AGENT-README.md` now carries fast-resume + onboarding role

Verification notes:

- Python parse checks passed (`kb_pipeline.py`, `scripts/build_hub_index.py`, `scripts/render_dialog_json_html.py`)
- Hub index build verified with temp output target under `tmp/docs/`
- Runtime checks written to:
  - `tmp/.tmp_check_ollama.json`
  - `tmp/.tmp_check_lmstudio.json`

## Session 12: Autonomous Prompt Tuning Loop (Safe-Mode, Full Ladder + Acid)

Date: 2026-04-10 UTC

Outcome:

- resumed autonomous tuning in unattended-safe mode:
  - no approval-gated steps
  - scratch artifacts routed to `tmp/`
  - isolated KB writes via `--kb-root tmp/kb_store`
- resolved local write-permission blockers by redirecting prompt snapshots/corpus output to temp-safe paths:
  - `--prompt-history-dir tmp/prompt_history`
  - `--kb-root tmp/kb_store`
- tuned `modelfiles/semantic_parser_system_prompt.md` to harden schema-safe query/retract output in stress probes

Prompt changes added:

- interrogative routing guard:
  - non-English interrogatives default to `query` unless explicit write intent
- yes/no query shape guard:
  - never emit bare atom query goals
  - require explicit args/variables for query predicates
- retract shape guard:
  - enforce `retract(<fact_like_term_with_args>).`
  - explicitly reject bare retract targets
- added micro-patterns:
  - ambiguous undo/retract behavior with clarification
  - yes/no status query with clarification fallback

Validation campaign:

- baseline and iterative sweeps were run with:
  - parser model: `qwen3.5:9b` (Ollama, temp 0, ctx 8192)
  - clarification answer model: `gpt-oss:20b` (Ollama, ctx 16384)
  - runtime: `core`
  - prompt file injection enabled
- final full sweep (`resume5`) passed all targeted scenarios:
  - `stage_00_foreign_unseen_probe`
  - `stage_00_multilingual_probe`
  - `stage_01_facts_only`
  - `stage_02_rule_ingest`
  - `stage_03_transitive_chain`
  - `acid_03_temporal_override`
  - `acid_04_alias_pressure`
  - `acid_05_long_context_lineage`

Evidence artifacts:

- summary:
  - `tmp/runs/resume5_summary_20260410_102508.json`
- per-scenario reports:
  - `tmp/runs/*_resume5_20260410_102508.json`
- passing prompt provenance id in these runs:
  - `sp-e0a66d9a2fbe`

## Session 13: Public Source-of-Truth Publish + CE Improvement Sweep

Date: 2026-04-10 UTC

Outcome:

- promoted latest `resume5` run set into published artifacts:
  - `kb_runs/*_resume5_latest.json`
  - `docs/data/runs/*_resume5_latest.json`
  - `docs/reports/*_resume5_latest.html`
- regenerated hub/manifests:
  - `docs/index.html`
  - `docs/progress_cards.html`
  - `docs/data/runs_manifest.json`
  - `docs/data/prompt_versions.json`
- updated README evidence and prompt snapshot references to match published truth

Published stats after refresh:

- total runs: `32`
- passed: `28`
- failed: `4`
- pass rate: `87.5%`

Fresh higher-target run (no-stuck check):

- executed clarification-eagerness sweep over full 8-scenario pack:
  - CE `0.55`, `0.65`, `0.75`, `0.85`
- all settings passed `8/8` scenarios
- improvement signal:
  - total clarification rounds dropped from `4` (CE `0.65+`) to `2` (CE `0.55`)

Evidence:

- CE sweep summary:
  - `tmp/ce_sweep/ce_sweep_20260410_110945.json`

## Session 14: Golden KB Benchmark System (Story -> Answer KB)

Date: 2026-04-10 UTC

Outcome:

- added first-class golden KB tooling:
  - `scripts/golden_kb.py`
  - subcommands:
    - `freeze` (freeze canonical golden KB from rigorous run report)
    - `compare` (golden vs candidate KB diff)
    - `benchmark` (scenario ingest + direct golden compare)
    - `benchmark-manifest` (batch benchmark over manifest entries)
- added golden/story scaffolding:
  - `goldens/README.md`
  - `goldens/manifest.json`
  - `goldens/kb/`
  - `goldens/probes/`
  - `stories/README.md`
- seeded first example pack:
  - `stories/stage_01_facts_only.md`
  - `goldens/probes/stage_01_facts_only.json`
  - `goldens/kb/stage_01_facts_only_golden.pl`
  - manifest entry for `stage_01_facts_only`

Design note:

- benchmark defaults now favor deterministic story->KB isolation:
  - `clarification_eagerness=0.0`
  - `max_clarification_rounds=0`
  - `force_empty_kb=true`

Verification:

- ran manifest benchmark:
  - `python scripts/golden_kb.py benchmark-manifest --manifest goldens/manifest.json --out-summary tmp/golden_manifest_summary_stage01.json`
  - result: `stage_01_facts_only` run passed and `kb_match=true`

## Session 15: Decision-State Layer (Commit/Stage/Clarify/Escalate/Reject)

Date: 2026-04-10 UTC

Outcome:

- added a normalized turn-level decision-state mapping in `kb_pipeline.py`:
  - `commit`
  - `stage_provisionally`
  - `ask_clarification`
  - `escalate`
  - `reject`
- mapping is observational only (no apply-policy behavior changes)
- run reports now include:
  - per-turn `decision_state`
  - aggregate `decision_state_counts`
- console summary now prints decision-state totals after each run

Notes:

- this creates a clean bridge from raw statuses (`success/skipped/no_results/clarification_requested/validation_error/constraint_error`) to the higher-level workflow states discussed in planning
- enables future threshold tuning and escalation policy work without re-labelling historical run output

## Session 16: Goldilocks Story Roundtrip + Repo Demo Page

Date: 2026-04-10 UTC

Outcome:

- ran long-form story ingestion experiment using Goldilocks narrative text
- generated and preserved a failed-but-informative run corpus for analysis
- produced a deterministic reconstruction from generated KB clauses
- published a repo-visible demo page showing:
  - input story
  - expandable generated `kb.pl`
  - reconstructed story from KB-only memory

Artifacts:

- story inputs:
  - `stories/goldilocks_roundtrip.md`
  - `stories/goldilocks_and_the_three_bears.txt`
- scenario:
  - `kb_scenarios/story_goldilocks_roundtrip.json`
- report + diagnostics:
  - `GOLDILOCKS_ROUNDTRIP_REPORT.md`
  - `tmp/goldilocks_roundtrip_run.json`
  - `tmp/goldilocks_failure_ledger.json`
  - `tmp/goldilocks_reconstructed_story.md`
- docs-published roundtrip view:
  - `docs/goldilocks-roundtrip.html`
  - `docs/data/roundtrip/goldilocks_roundtrip_input_story.md`
  - `docs/data/roundtrip/goldilocks_roundtrip_generated_kb.pl`
  - `docs/data/roundtrip/goldilocks_roundtrip_reconstructed_story.md`

Notes:

- README now includes a top-level “Story Roundtrip Demo” callout with the user-requested wording:
  - “Watch the pre-thinker consume a story, then recite from captured facts and logical memory.”

## Session 17: Story/CE Frontier Expansion To rung_360

Date: 2026-04-12 UTC

Outcome:

- promoted new ladder frontier evidence from autonomous cycles into canonical run history:
  - `rung_270_story_lineage_fragmented_ingest`
  - `rung_280_story_revision_temporal_shift`
  - `rung_290_story_multi_branch_pronoun_pressure`
  - `rung_300_story_nested_corrections`
  - `rung_310_story_cross_clause_pronoun_weave`
  - `rung_320_story_temporal_exception_rebinding`
  - `rung_330_story_booklet_cross_scene_rebind`
  - `rung_340_ce_story_pronoun_transfer`
  - `rung_350_ce_story_multi_round_revision`
  - `rung_360_ce_story_branch_merge_noise`
- regenerated ladder pages and index:
  - `docs/rungs/index.html`
  - `docs/rungs/*.html` (74 scenario pages)
- refreshed run reports for newly promoted scenarios:
  - `docs/reports/*rung_270*` through `*rung_360*`

Key result:

- frontier CE/story trio passed in refined check:
  - `rung_340`: `11/11`
  - `rung_350`: `11/11`
  - `rung_360`: `12/12`

## Session 18: Docs Publish Retention (Curated + Historical Split)

Date: 2026-04-12 UTC

Outcome:

- added curated publish utility:
  - `scripts/refresh_published_runs.py`
- established publish split:
  - full historical corpus stays in `kb_runs/`
  - curated docs source now generated into `kb_runs_published/`
  - docs JSON corpus (`docs/data/runs/`) rebuilt from curated set only
  - historical stats (`docs/data/historical_metrics.json`) computed from full corpus
- rebuilt docs surfaces with updated curation:
  - `docs/run-reports-hub.html`
  - `docs/progress_cards.html`
  - `docs/data/runs_manifest.json`
  - `docs/data/runs_curated.json`
  - `docs/data/scenario_progress.json`
  - `docs/data/historical_metrics.json`

Notes:

- this prevents docs/report sprawl while preserving full evidence and trendability.
- docs landing content and README were updated to explain the retention model.

## Session 19: Progress Memory v1 (Governance Layer + New Rungs)

Date: 2026-04-12 UTC

Outcome:

- implemented Progress Memory v1 in `kb_pipeline.py`:
  - per-ontology `progress.json` state (`active_focus`, `goals`, `open_questions`, `resolved_items`, `notes`)
  - scenario-level progress directives (`progress.set_active_focus`, `add_goals`, `add_open_questions`, `resolve_goals`, `resolve_questions`, `add_notes`)
  - progress-aware clarification policy inputs:
    - `progress_low_relevance_threshold`
    - `progress_high_risk_threshold`
  - progress context included in clarification answer prompt packs
- added dedicated progress-memory unit tests:
  - `tests/test_progress_memory.py`
- added progress-memory scenario packs:
  - `rung_370_progress_feasibility_alignment`
  - `rung_380_progress_irrelevant_fact_filter`
  - `rung_390_progress_goal_directed_clarification`
  - `rung_400_progress_relevance_repair`
  - `rung_410_progress_goal_context_steering`
  - `rung_420_progress_focus_shift_transition`

Verification:

- full test suite passed (`28/28`)
- all new progress rungs passed in core runtime checks

## Session 20: Progress Memory Value Proof (Contamination Ablation + Metrics)

Date: 2026-04-12 UTC

Outcome:

- added run-level governance metrics to `kb_pipeline.py` reports:
  - `off_focus_write_attempts`
  - `off_focus_write_intercepts`
  - `off_focus_write_commits`
  - `off_focus_write_block_rate`
  - `off_focus_write_contamination_rate`
  - `kb_contamination_delta`
- added per-turn tracking fields to support those aggregates:
  - `progress_low_relevance_seen`
  - `progress_high_risk_seen`
- ran same-scenario contamination ablation with fresh KB namespaces:
  - with progress memory:
    - off-focus writes intercepted
    - `block_rate=1.000`
    - off-focus query outcomes were `no_results`
  - without progress memory:
    - off-focus writes committed
    - off-focus query outcomes were `success`
  - parser confidence was unchanged between arms (`avg_conf=0.971`)

Interpretation:

- progress memory provides state-governance value (KB contamination control), not parser-confidence lift.
- this justifies keeping progress memory in high-integrity flows and optionally disabling it in bulk-ingest lanes.

## Session 21: Public-Facing Polish + Docs Hub Refresh

Date: 2026-04-12 UTC

Outcome:

- refreshed public docs surfaces to foreground current frontier work:
  - `docs/index.html` updated callouts for `rung_370 -> rung_420`
  - explicit links added for progress-memory contamination ablation runs
  - founder explainer card retained as top-level narrative entry point
- updated README quick-link framing and evidence summary wording so outside readers land on:
  - docs hub
  - run explorer
  - explainer article
  - sessions assembly log
- regenerated report hub/manifests after adding new progress-memory run artifacts:
  - `docs/run-reports-hub.html`
  - `docs/data/runs_manifest.json`
  - `docs/data/runs_curated.json`
  - `docs/data/scenario_progress.json`
  - `docs/data/prompt_versions.json`
  - `docs/data/historical_metrics.json`

Notes:

- this publish pass keeps the "curated public slice + full historical corpus" split intact:
  - `kb_runs/` remains canonical history
  - `kb_runs_published/` remains bounded docs source
- objective for this pass was presentation clarity, not benchmark inflation:
  evidence now emphasizes current frontier and governance deltas while preserving full lineage in raw runs.








