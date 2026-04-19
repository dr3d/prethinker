# Focus Execution Plan

Last updated: 2026-04-17

## Objective

Keep one truthful spine:

`English -> deterministic KB -> reliable interrogation`

No side quests unless they improve this path, and no headline claim unless it survives the current strict baselines.

## Current Reality

- `scripts/run_safety_gate.py` is green (`105 passed`).
- Strict Blocksworld is the current stable proof lane.
- `modelfiles/predicate_registry.json` is now populated, so the general strict lane is actually strict.
- The guarded Blocksworld lane is currently stable at `20/20`, `8/8`, zero-hit `0`, avg-hit `0.458334 / 0.458334`.
- The mid and upper-mid narrative packs are now pipeline-green at `3/3`.
- The main remaining caveat is not pipeline fragility; it is evaluation honesty around temporal coverage, especially on mid `full` and the Glitch control lane.

## Default Operating Stack

- Parser model: `qwen3.5:9b`
- Runtime: `core`
- Prompt source: `modelfiles/semantic_parser_system_prompt.md`
- Registry: strict (`--strict-registry`)
- Type schema: scenario-specific where available (Goldilocks profile for Goldilocks)
- Clarification: enabled with bounded rounds
- Frontend proposal: `off` during baseline stabilization

## Phases

1. Hold stable lanes
- Keep the safety gate green.
- Keep Blocksworld zero-hit at `0`.
- Do not trade stable-lane honesty for frontier optimism.

2. Recover narrative strict lane
- Compare against the latest honest recovery baselines (`0.9284` mid best, `0.956` upper-mid best) while keeping the post-registry correction as the audit floor.
- Improve temporal coverage and query honesty without loosening strict admission.
- Treat mid `full` temporal floor and Glitch temporal reasoning as the current sharpest open fixes.

3. Real-world pressure
- Resume broader HN/story pressure only after item 2 is stable.
- Promote repeated failure patterns into regression scenarios.

4. Medical lane (after UMLS approval)
- Start with a constrained UMLS subset.
- Add medical predicate/type profile.
- Run medical interrogation packs.

5. Frontend evolution
- Introduce constrained frontend proposals in `shadow` mode first.
- Promote to `active` only with consistent metric improvement.

## Promotion Targets

These are promotion targets, not the current achieved state across the full repo.

- Fact precision >= `0.90`
- Fact coverage >= `0.85`
- Exam pass rate >= `0.80`
- Temporal exam pass rate >= `0.70`
- Incorrect KB mutation rate <= `0.02`

## Current Honest Command Path

There is not yet a single truthful one-command status cycle for the whole project.
The practical current loop is:

```powershell
python scripts/run_safety_gate.py
```

```powershell
python scripts/run_blocksworld_lane.py --sample-size 20 --max-objects 4 --planner-depth 12 --run-prethinker --prethinker-cases 8 --backend ollama --base-url http://127.0.0.1:11434 --model qwen3.5:9b --prompt-file modelfiles/semantic_parser_system_prompt.md --context-length 8192 --prethinker-split-mode full --predicate-registry modelfiles/predicate_registry.blocksworld.json --strict-registry --max-zero-hit 0 --min-avg-init-hit 0.45 --min-avg-goal-hit 0.45 --summary-json tmp/blocksworld_lane_guarded_20260417.summary.json --summary-md docs/reports/BLOCKSWORLD_LANE_GUARDED_2026-04-17.md
```

```powershell
python scripts/run_story_stress_cycle.py --story-file tmp/story_inputs/<mid_or_upper_mid>.txt --label <pack_label> --modes full,paragraph,line --temporal on --backend ollama --base-url http://127.0.0.1:11434 --model qwen3.5:9b --prompt-file modelfiles/semantic_parser_system_prompt.md --context-length 8192 --predicate-registry modelfiles/predicate_registry.json --strict-registry --exam-style detective --exam-question-count 20 --exam-min-temporal-questions 4 --summary-json tmp/<pack_label>.summary.json --summary-md docs/reports/<PACK_REPORT>.md
```

`scripts/run_gate_cycle.py` is still useful as an experiment wrapper, but it should not be treated as the sole project headline until it matches the current evidence spine above.

## Shadow A/B Gate

Before any `frontend_proposal_mode=active` trial, run `shadow` against a known-good `off` baseline and require net-positive metrics:

```powershell
python scripts/run_gate_cycle.py --batch baseline_focus --frontend-proposal-mode shadow --compare-to-summary <baseline_summary.json> --require-net-positive --require-pipeline-pass-rate 1.0 --write-corpus-on-fail
```

Current policy:
- If net-positive check fails, `active` remains blocked.
- If net-positive check passes repeatedly, only then schedule controlled `active` trial.

## Weekly Rhythm

1. Run the safety gate.
2. Re-run Blocksworld strict and confirm no stable-lane regression.
3. Re-run the strict narrative packs and inspect why they are still failing.
4. Promote repeated misses into regression scenarios only after the strict reruns are honestly scored.

## UMLS Readiness (pending approval email)

Pre-stage now:
- UMLS import pipeline skeleton
- medical registry/type schema profile
- medical interrogation pack templates

Go-live when license arrives:
- ingest a small validated slice first
- compare against pre-UMLS baseline using same interrogation gates
