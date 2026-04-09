# NEXT CODEX HANDOFF

Updated: 2026-04-09 UTC

## What This Is

This is the short resume packet for the next Codex session after folder rename.
Treat this file as the fastest path back into productive tuning.

## Current Baseline

- Primary target model: `qwen3.5:9b` (Ollama).
- Current best provenance-tracked prompt: `sp-ad589d272fbb`.
- Prompt source: `modelfiles/semantic_parser_system_prompt.md`.
- Prompt snapshot: `modelfiles/history/prompts/sp-ad589d272fbb.md`.

Best verified runs for that prompt:

- `kb_runs/stage_01_people_ladder_tune_r1.json` (passed 2/2)
- `kb_runs/stage_02_people_ladder_tune_r1.json` (passed 1/1)

## First Commands After Rename

Run from repo root:

```bash
python scripts/render_kb_run_html.py --input kb_runs --output docs/reports --recursive --theme standard --docs-hub-link ../index.html --repo-link ./README.md
python scripts/render_kb_store_html.py --kb-root kb_store --output-dir docs/kb --title-prefix "KB Snapshot"
python scripts/render_test_ladder_html.py --scenarios-dir kb_scenarios --runs-dir kb_runs --output-dir docs/rungs --title "Prolog Extraction Test Ladder"
python scripts/build_hub_index.py --reports-dir docs/reports --runs-dir kb_runs --kb-pages-dir docs/kb --ladder-index docs/rungs/index.html --output docs/index.html --title "Prethinker Report Hub"
```

Then open:

- `docs/index.html`
- `docs/data/prompt_versions.json`
- `docs/data/runs_manifest.json`

## Immediate Next Tuning Loop

1. Keep `modelfiles/semantic_parser_system_prompt.md` as the single editable prompt source.
2. Run smoke pair first on every prompt change:
   - `kb_scenarios/stage_01_facts_only.json`
   - `kb_scenarios/stage_02_rule_ingest.json`
3. Only move to acid rungs after smoke pair remains stable.
4. Preserve provenance fields in every run (`prompt_provenance`, `run_id`, `system_prompt_text`).

## Open Technical Focus

- Parser accuracy on strict Prolog element extraction (facts, rules, queries, retracts).
- Gradual ladder ascent before broader ontology alignment layers.
- Keep named KB retention semantics unchanged (`empty_kb()` only for brand-new namespaces by default).

## Notes For Next Codex

- Use relative paths in commands and docs.
- Old run artifacts may carry historical absolute paths from prior folder names; rerendering updates displayed references.
- `AGENT-README.md` and `SESSIONS.md` are current and should be treated as canonical onboarding + migration context.
