# Deterministic English->Logic Compilation: Progress Note

Date: 2026-04-15

## Delta Since Previous Report (2026-04-14 -> 2026-04-15)

- Added a single baseline command path: `python scripts/run_gate_cycle.py --batch baseline_focus`.
- Added a practical interrogator gate workflow and guide (`docs/KB_INTERROGATOR.md`).
- Added focused execution strategy and hard promotion gates (`docs/FOCUS_EXECUTION_PLAN.md`).
- Added GraphMERT-lite constrained front-end scaffold behind feature flags (`off|shadow|active`), default `off`.
- New focused baseline metrics:
  - pipeline pass rate: `0.80` (`4/5`)
  - average audit coverage: `0.86875`
  - average audit precision: `0.9875`
  - average exam pass: `0.866667`
  - average temporal exam pass: `0.25`
- Core near-term blocker remains: Goldilocks roundtrip stability (`turn_parse_failures=4`, `turn_apply_failures=4` in this cycle).

## Executive Summary

This cycle shifted Prethinker from multi-threaded exploration to a single execution spine:

`English -> deterministic KB -> interrogation-grade validation`

The strongest outcome is organizational and operational coherence: we now have one command path that runs ingestion and then grades the resulting KB with a deterministic/LLM-audited interrogator. The baseline evidence is mixed but meaningful: Hacker News middle-noise scenarios are performing strongly, while Goldilocks still exposes unresolved narrative edge cases.

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
- Run folder: `tmp/runs/focus_cycles/baseline_focus_20260415/`
- Aggregate summary: `summary.json`, `summary.md`.

## Baseline Metrics (2026-04-15 Focus Cycle)

Batch: Goldilocks roundtrip + HN middle-noise mini-pack (4 scenarios)

- Pipeline pass rate: `0.80` (`4/5`)
- Interrogator successful reports: `4/5`
- Average fact coverage: `0.86875`
- Average fact precision: `0.9875`
- Average exam pass rate: `0.866667`
- Average temporal exam pass rate: `0.25`

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
  - pipeline failed (`turn_parse_failures=4`, `turn_apply_failures=4`)
  - no committed corpus artifact for interrogator in this run profile

## Honest Read: Successes And Challenges

Successes:
- We now have a repeatable, instrumented gate loop instead of ad-hoc testing.
- HN middle-noise ingestion is strong under strict registry with high precision.
- The interrogator is now usable for both full-ingest and turn-by-turn quality checks.
- We have a safe scaffold for GraphMERT-style constrained front-end work without destabilizing production flow.

Challenges:
- Goldilocks remains a hard narrative stressor with unresolved parse/apply failures in this cycle.
- Temporal reasoning quality is still weak in aggregate (`0.25` temporal exam pass), largely due lack of temporal-rich scenarios and uneven temporal assertions.
- Coverage is not yet at target across all frontier scenarios; some packs still show semantic drop under compression/noise.
- The front-end proposal stage is scaffolded but not yet validated in `shadow` mode against broad baseline packs.

## Directions Forward (What Comes Next)

Immediate (next 48-72 hours):
1. Keep the single command path as the mandatory baseline gate.
2. Repair Goldilocks regression path until baseline cycle reaches `5/5` pipeline pass.
3. Run a second focus cycle to verify reproducibility, not one-off luck.
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
- Focus run summary: `tmp/runs/focus_cycles/baseline_focus_20260415/summary.json`
- Focus run markdown: `tmp/runs/focus_cycles/baseline_focus_20260415/summary.md`
- Command wrapper: `scripts/run_gate_cycle.py`
- Front-end scaffold: `ingest_frontend.py`
- Interrogator implementation: `scripts/kb_interrogator.py`
