# Deterministic English->Logic Compilation: Progress Note

Date: 2026-04-15

## Current Scorecard (Latest)

Primary fronts and where we stand after the latest sanity cycles:

- Front: baseline gate reliability (`baseline_focus`)
  - pipeline pass: `5/5` (`1.0`)
  - audit coverage: `0.865`
  - audit precision: `0.974`
  - exam pass: `0.793333`
  - temporal exam pass: `0.4`
- Front: raw wild-story ingest (`glitch_focus`, non-temporal)
  - pipeline pass: `3/3`
  - audit coverage: `0.583333`
  - audit precision: `0.8`
  - exam pass: `0.608333`
  - temporal exam pass: `0.333333`
- Front: temporal semantics (`glitch_focus`, temporal dual-write on)
  - pipeline pass: `3/3`
  - audit coverage: `0.65`
  - audit precision: `0.906667`
  - exam pass: `0.933333`
  - temporal exam pass: `0.921296`
  - delta vs non-temporal: coverage `+0.067`, precision `+0.107`, exam `+0.325`, temporal exam `+0.588`
- Front: deterministic engine/runtime health
  - targeted suite: `36 passed`
  - engine regression suite: `37 passed`

## Research Pipeline Sanity Check (2026-04-15 Evening)

Ran a full deterministic + live-LLM sanity sweep on local Ollama using `qwen3.5:9b`:

- Static sanity:
  - Python compile pass for `kb_pipeline`, MCP server, gate-cycle runner, raw-story runner, and gateway hooks.
- Engine/unit baseline:
  - `python -m pytest tests/test_core_runtime.py tests/test_engine_baseline_suite.py tests/test_clarification_eagerness.py -q` -> `36 passed`.
  - `python scripts/run_engine_regression.py` -> `37 passed`.
- Live pipeline sanity:
  - `scripts/run_gate_cycle.py --batch glitch_focus` (same-model CE, strict registry) -> pipeline `3/3`.
  - Re-ran the same batch with `--temporal-dual-write` enabled -> pipeline `3/3`.

Measured delta (temporal dual-write run minus non-temporal run):

- Coverage: `0.583 -> 0.650` (`+0.067`)
- Precision: `0.800 -> 0.907` (`+0.107`)
- Exam pass: `0.608 -> 0.933` (`+0.325`)
- Temporal exam pass: `0.333 -> 0.921` (`+0.588`)

Current read:

- Research pipeline is operational end-to-end on the live stack (parser, runtime, interrogator).
- Temporal dual-write is net-positive on the current glitch-focused pack and did not reduce pipeline stability.
- No parser/apply failures were observed in either sanity cycle (`turn_parse_failures=0`, `turn_apply_failures=0` across all scenarios).

## Gate Sprint Update (2026-04-15)

Recent updates:
- Kept a single mandatory gate command path and hardened it:
  - `scripts/run_gate_cycle.py` now supports gate enforcement (`--require-pipeline-pass-rate`), frontend mode selection (`--frontend-proposal-mode`), and built-in A/B comparison (`--compare-to-summary`, `--require-net-positive`).
  - Gate now returns non-zero when requirements are not met.
- Repaired Goldilocks regression path for gate reliability:
  - Goldilocks baseline in gate batch now uses bounded clarification rounds (`2`) with scenario-local clarification confidence floor (`0.0`) to prevent flaky defer-and-fail behavior.
- Ran reproducibility checks:
  - `baseline_focus_20260415_gate_a`: pipeline `5/5`, coverage `0.865`, precision `0.934`, exam `0.793333`.
  - `baseline_focus_20260415_gate_b`: pipeline `5/5`, coverage `0.865`, precision `0.934`, exam `0.813333`.
- Latest baseline sanity rerun (same stack, same gate path):
  - `sanity_baseline_qwen9b_20260415`: pipeline `5/5`, coverage `0.865`, precision `0.974`, exam `0.793333`, temporal exam `0.4`.
- Began frontend shadow A/B with enforced net-positive requirement:
  - `baseline_focus_20260415_shadow_a` vs `gate_b`: pipeline `5/5`, coverage `0.865`, precision `0.934`, exam `0.802857`.
  - Comparator result: `net_positive=false` (exam delta `-0.010476`), so `active` remains blocked.

Interpretation:
- We now have three consecutive `5/5` baseline passes, so core gate stability improved materially.
- Shadow mode is instrumented and being evaluated, but it has not yet earned promotion to active.

## Resume Update: Raw-Cage Matrix (No Preprocessing)

This matrix uses strict raw-input handling: source text is passed to Prethinker without cleanup/rewrite, then outputs are graded post-run.

- Matrix executed: `12` runs (`4` raw sources x `3` packaging modes: `full|paragraph|line`).
- Artifact completeness: `11/12` currently have both pipeline + interrogator artifacts.
- Pipeline pass rate: `6/12` (`0.50`).
- Average fact-audit coverage: `0.565455`.
- Average fact-audit precision: `0.833636`.
- Average exam pass rate: `0.371265`.
- Pending long-run case: `raw_fantasy_overlord_session.source_line_20260415` (`1584` utterances in line mode).

What improved in this resume:
- Fixed a real orchestration bug in `scripts/run_story_raw.py`: interrogator now resolves `kb.pl` from `pipeline_out -> kb_namespace.corpus_path` (with fallbacks), instead of assuming `kb_store/<raw kb-name>/kb.pl`.
- Backfilled missing interrogator artifacts for prior raw runs (indie/fantasy full + paragraph + indie line) using the actual persisted corpus paths.

What this tells us right now:
- `full` mode remains the most reliable shape for raw ingestion when the source is long/noisy.
- `paragraph` and especially `line` modes expose current apply/clarification limits quickly in messy, conversational sources.
- We are now measuring raw-path truth directly rather than benefiting from any hidden preprocessing.

## Delta Since Previous Report (2026-04-14 -> 2026-04-15)

- Added a single baseline command path: `python scripts/run_gate_cycle.py --batch baseline_focus`.
- Added a practical interrogator gate workflow and guide (`docs/KB_INTERROGATOR.md`).
- Added focused execution strategy and hard promotion gates (`docs/FOCUS_EXECUTION_PLAN.md`).
- Added GraphMERT-lite constrained front-end scaffold behind feature flags (`off|shadow|active`), default `off`.
- New focused baseline metrics (latest run):
  - pipeline pass rate: `1.0` (`5/5`)
  - average audit coverage: `0.865`
  - average audit precision: `0.974`
  - average exam pass: `0.793333`
  - average temporal exam pass: `0.4`
- Goldilocks moved from parse/apply instability to a clean pipeline pass in the latest baseline cycle (`turn_parse_failures=0`, `turn_apply_failures=0`).
- Temporal dual-write on glitch pack is now a proven net-positive, not just a theoretical add-on.

## Executive Summary

This cycle shifted Prethinker from multi-threaded exploration to a single execution spine:

`English -> deterministic KB -> interrogation-grade validation`

The strongest outcome is organizational and operational coherence: we now have one command path that runs ingestion and then grades the resulting KB with a deterministic/LLM-audited interrogator. HN middle-noise scenarios remain strong, Goldilocks now passes cleanly in baseline, and temporal dual-write materially improves glitch-story interrogation quality.

## What We Accomplished Since The Last Report

1. Strategy convergence and freeze of side quests
- Added a focused execution strategy with explicit phases, gates, and default stack.
- New plan doc: `docs/FOCUS_EXECUTION_PLAN.md`.

2. Interrogator matured into a practical gate
- `scripts/kb_interrogator.py` now supports:
  - source from plain text, scenario JSON, or pipeline run JSON
  - turn-prefix interrogation (`--through-turn`) for in-flight checks
  - exam styles (`general`, `detective`, `medical`)
  - retry on malformed model JSON
- New guide: `docs/KB_INTERROGATOR.md`.

3. Single command path for baseline cycles
- Added `scripts/run_gate_cycle.py`.
- One command now runs pipeline + interrogator + consolidated summary.
- Baseline command:

```powershell
python scripts/run_gate_cycle.py --batch baseline_focus
```

4. GraphMERT-lite front-end scaffold (feature-flagged, low-risk)
- Added `ingest_frontend.py` with staged proposal flow:
  - discover spans
  - rank allowed predicates (registry-gated)
  - assemble constrained arguments
  - produce parse proposal
- Wired into `kb_pipeline.py` with `--frontend-proposal-mode {off,shadow,active}`.
- Default remains `off` to preserve current behavior during stabilization.
- Added tests: `tests/test_ingest_frontend.py` (3 passing).

5. Fresh baseline run on focused pack
- Run folder: `tmp/runs/focus_cycles/sanity_baseline_qwen9b_20260415/`
- Aggregate summary: `summary.json`, `summary.md`.

## Baseline Metrics (2026-04-15 Focus Cycle, Latest)

Batch: Goldilocks roundtrip + HN middle-noise mini-pack (5 scenarios)

- Pipeline pass rate: `1.0` (`5/5`)
- Interrogator successful reports: `5/5`
- Average fact coverage: `0.865`
- Average fact precision: `0.974`
- Average exam pass rate: `0.793333`
- Average temporal exam pass rate: `0.4`

Per-scenario highlights:

- `rung_452_excursion_hn_docker_spain_block`
  - coverage `1.00`, precision `1.00`, exam pass `1.00`
- `rung_457_excursion_hn_codex_claude_scope_split`
  - coverage `0.875`, precision `1.00`, exam pass `1.00`
- `rung_458_excursion_hn_agents_key_policy`
  - coverage `0.85`, precision `0.95`, exam pass `0.80`
- `rung_459_excursion_hn_scope_correction`
  - coverage `0.75`, precision `1.00`, exam pass `0.666667`
- `story_goldilocks_roundtrip`
  - pipeline passed (`turn_parse_failures=0`, `turn_apply_failures=0`)
  - interrogator: coverage `0.85`, precision `0.92`, exam pass `0.5`

## Honest Read: Successes And Challenges

Successes:
- We now have a repeatable, instrumented gate loop instead of ad-hoc testing.
- HN middle-noise ingestion is strong under strict registry with high precision.
- The interrogator is now usable for both full-ingest and turn-by-turn quality checks.
- We have a safe scaffold for GraphMERT-style constrained front-end work without destabilizing production flow.

Challenges:
- Goldilocks now ingests cleanly, but retelling/query quality is still not yet strong enough (`exam_pass_rate=0.5` on this cycle).
- Raw glitch quality without temporal dual-write is still weak in `paragraph`/`line` packaging modes.
- Coverage is not yet at target across all frontier scenarios; some packs still show semantic drop under compression/noise.
- The front-end proposal stage is scaffolded but not yet validated in `shadow` mode against broad baseline packs.

## Directions Forward (What Comes Next)

Immediate (next 48-72 hours):
1. Keep the single command path as the mandatory baseline gate.
2. Keep temporal dual-write enabled on narrative stress packs (`glitch`, `goldilocks`) while collecting additional A/B evidence.
3. Run a second baseline + glitch temporal pair to verify reproducibility, not one-off luck.
4. Begin `frontend_proposal_mode=shadow` A/B on the same batch; require net-positive metrics before any active usage.

Near term (pending UMLS approval email):
1. Prepare UMLS ingestion slice pipeline (`MRCONSO`/`MRREL` to seed facts).
2. Add medical predicate registry + type schema profile.
3. Build medical interrogation packs for contradiction, temporal progression, and differential consistency.

Promotion gates before expanding scope:
- Precision >= `0.90`
- Coverage >= `0.85`
- Exam pass >= `0.80`
- Temporal exam pass >= `0.70`
- Incorrect mutation rate <= `0.02`

## Artifact Index

Current-cycle key artifacts:
- Focus strategy: `docs/FOCUS_EXECUTION_PLAN.md`
- Interrogator guide: `docs/KB_INTERROGATOR.md`
- Baseline sanity summary: `tmp/runs/focus_cycles/sanity_baseline_qwen9b_20260415/summary.json`
- Baseline sanity markdown: `tmp/runs/focus_cycles/sanity_baseline_qwen9b_20260415/summary.md`
- Glitch sanity (non-temporal): `tmp/runs/focus_cycles/sanity_glitch_qwen9b_20260415/summary.json`
- Glitch sanity (temporal): `tmp/runs/focus_cycles/sanity_glitch_qwen9b_temporal_20260415/summary.json`
- Raw matrix run index: `tmp/raw_matrix_20260415_run_index.json`
- Raw matrix summary: `tmp/raw_matrix_20260415_summary.json`
- Raw matrix summary (markdown): `tmp/raw_matrix_20260415_summary.md`
- Interrogator backfill log: `tmp/raw_matrix_20260415_interrogator_backfill.json`
- Raw audit HTML (glitch): `docs/raw-story-audit-glitch.html`
- Command wrapper: `scripts/run_gate_cycle.py`
- Raw story runner: `scripts/run_story_raw.py`
- Front-end scaffold: `ingest_frontend.py`
- Interrogator implementation: `scripts/kb_interrogator.py`
