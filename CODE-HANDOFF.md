# CODE-HANDOFF

Date: 2026-04-17
Author: Codex (GPT-5)
Repository: `D:\_PROJECTS\prethinker`

## 1) Mission Snapshot

Prethinker is a deterministic-first semantic parser workbench.
The system compiles natural language into logic operations and applies them through a governed runtime.

Core contract:
- Neural model proposes parse/intent.
- Deterministic policy/runtime decides what mutates KB state.
- Every run is scored and auditable.

Current strategic split:
- Structured/closed-world lanes (strong): Blocksworld + controlled packs.
- Wild narrative ingestion lanes (improving, harder frontier): Glitch, Ledger, HN-derived material.

## 2) Non-Negotiable Operating Rules

These were repeatedly emphasized and should be treated as hard requirements:

1. Raw-input rule
- Do not pre-chew/hand-correct source text before ingestion.
- Feed raw text directly to Prethinker.
- Codex can grade results after the run, but must not "help" by injecting answers upstream.

2. Honest attribution rule
- Never pretend Prethinker extracted something that Codex inferred offline.
- Reports must distinguish extracted facts vs evaluator inference.

3. Human-facing artifact rule
- For story tests, produce human-readable artifacts (HTML preferred) that show:
  - Source blob handed to Prethinker
  - Generated `kb.pl`
  - Interrogation questions + deterministic answers
  - CE clarification dialogs (if any)
  - Final score summary

4. Regression-first rule
- New experiments should not silently degrade stable lanes.
- Keep baseline gate green before claiming frontier wins.

## 3) Current System Architecture

High level path:
1. Ingest utterance(s)
2. Route + parse
3. Clarification (if needed)
4. Deterministic apply/query
5. Validation + telemetry + report

Primary runtime file:
- `kb_pipeline.py`

Primary wrappers:
- `scripts/run_story_raw.py`
- `scripts/run_story_stress_cycle.py`
- `scripts/run_story_progressive_gulp.py`
- `scripts/run_story_pack_suite.py`
- `scripts/kb_interrogator.py`
- `scripts/run_blocksworld_lane.py`
- `scripts/run_safety_gate.py`

## 4) Runtime Controls You Must Know

Reference doc:
- `docs/RUNTIME_SETTINGS_CHEATSHEET.md`

Most important toggles:
- Model/backend:
  - `--backend`, `--base-url`, `--model`, `--prompt-file`, `--context-length`
- Deterministic constraints:
  - `--predicate-registry`, `--strict-registry`, `--type-schema`, `--strict-types`
- Clarification engine:
  - `--clarification-eagerness`
  - `--clarification-eagerness-mode` (`static|adaptive`)
  - `--max-clarification-rounds`
  - `--clarification-answer-*` family
- Temporal sequencing:
  - `--temporal-dual-write`
  - `--temporal-predicate` (default `at_step`)

Key policy notes:
- Sidecar CE exists to resolve ambiguity with bounded recent context; it does not replace deterministic admission controls.
- Same-family parser+clarifier (`qwen3.5:9b`) is current preferred default for consistency and VRAM stability.

## 5) Important Predicate Registry Status

- `modelfiles/predicate_registry.blocksworld.json` is populated and useful for strict Blocksworld lanes.
- `modelfiles/predicate_registry.json` is currently:
  - `{"canonical_predicates": []}`
- Consequence:
  - "strict" runs that use `predicate_registry.json` are effectively unconstrained right now.

Do not over-claim strictness on narrative lanes until this registry is populated.

## 6) Test Lanes In Use

### Lane A: Safety Gate (fast preflight)

Script:
- `scripts/run_safety_gate.py`

What it does:
- `py_compile` on core modules
- full `pytest -q`

Current observed result in this cycle:
- `78 passed`

Command:
```powershell
python scripts/run_safety_gate.py
```

### Lane B: Blocksworld Symbolic + Ingestion Lane

Script:
- `scripts/run_blocksworld_lane.py`

What it does:
- Pulls Planetarium + Sys2Bench domain
- Solves via grounded BFS symbolic harness
- Optionally runs Prethinker ingestion pilot on sampled cases
- Emits JSON + MD summary

Recent upgrade in this commit:
- Added `--max-zero-hit`
- Added `gates.zero_hit` summary block
- Returns non-zero exit if zero-hit threshold violated

Zero-hit gate semantics:
- "zero-hit" = init-hit ratio == 0 and goal-hit ratio == 0 for a pilot case

Baseline command (gated):
```powershell
python scripts/run_blocksworld_lane.py \
  --sample-size 20 \
  --max-objects 4 \
  --planner-depth 12 \
  --run-prethinker \
  --prethinker-cases 8 \
  --backend ollama --base-url http://127.0.0.1:11434 \
  --model qwen3.5:9b \
  --prompt-file modelfiles/semantic_parser_system_prompt.md \
  --context-length 8192 \
  --prethinker-split-mode full \
  --predicate-registry modelfiles/predicate_registry.blocksworld.json \
  --strict-registry \
  --max-zero-hit 0 \
  --summary-json tmp/blocksworld_lane_strict_mf3_gate_20260417.summary.json \
  --summary-md docs/reports/BLOCKSWORLD_LANE_STRICT_MF3_GATE_2026-04-17.md
```

Repro run (same config, fresh output) was also executed and matched.

### Lane C: Raw Story Stress Matrix

Script:
- `scripts/run_story_stress_cycle.py`

Purpose:
- Compare split packaging (`full|paragraph|line`) and temporal mode (`off|on`)
- Generate stress summary and optional HTML report

Command template:
```powershell
python scripts/run_story_stress_cycle.py \
  --story-file <path-to-raw-story.txt> \
  --label <label> \
  --modes full,paragraph,line \
  --temporal off,on \
  --backend ollama --base-url http://127.0.0.1:11434 \
  --model qwen3.5:9b \
  --prompt-file modelfiles/semantic_parser_system_prompt.md \
  --context-length 8192 \
  --exam-style detective --exam-question-count 20 --exam-min-temporal-questions 4
```

### Lane D: Progressive Gulp (dense narratives)

Script:
- `scripts/run_story_progressive_gulp.py`

Purpose:
- Ingest story in increasing percentages into cumulative KB
- Evaluate each stage + carry-forward checks
- Useful for very dense stories (Ledger-class)

Key features:
- Gate profiles: `english_strict` vs `multilingual_experimental`
- Optional stage recovery on failure/quality
- Critical checks from story pack exam battery

Command template:
```powershell
python scripts/run_story_progressive_gulp.py \
  --story-file <story.txt> \
  --label <label> \
  --percentages 25,50,75,100 \
  --split-mode paragraph \
  --auto-fallback-split \
  --backend ollama --base-url http://127.0.0.1:11434 \
  --model qwen3.5:9b \
  --prompt-file modelfiles/semantic_parser_system_prompt.md \
  --context-length 8192 \
  --temporal-dual-write \
  --exam-style detective --exam-question-count 20 --exam-min-temporal-questions 4
```

### Lane E: Story Pack Suite Runner

Script:
- `scripts/run_story_pack_suite.py`

Purpose:
- Story-pack automation for mid / upper-mid style packs
- Runs stress + progressive for each pack
- Consolidates suite summary

Example:
```powershell
python scripts/run_story_pack_suite.py \
  --packs tmp/story_pack_mid.md,tmp/story_pack_upper_mid.md \
  --backend ollama --base-url http://127.0.0.1:11434 \
  --model qwen3.5:9b \
  --prompt-file modelfiles/semantic_parser_system_prompt.md \
  --context-length 8192 \
  --exam-style detective --exam-question-count 20 --exam-min-temporal-questions 4
```

### Lane F: KB Interrogator

Script:
- `scripts/kb_interrogator.py`

Purpose:
- Grade extracted KB with fact audit + deterministic reasoning exam
- Output JSON and markdown

Reference:
- `docs/KB_INTERROGATOR.md`

### Lane G: Wild/HN Excursion

Reference doc:
- `docs/WILD_MODE.md`

Principle:
- Real-world language pressure lane
- Use harvested discourse, bounded packets, promote failure patterns into new regression scenarios

## 7) Named Story Challenges (Shorthand)

- Goldilocks
  - Roundtrip benchmark story used to measure extraction + reconstruction quality.
- Glitch (`The Glitch in the Airlock`)
  - Mid-complexity sci-fi narrative stress test.
- Ledger (`The Ledger at Calder's Reach`)
  - High-density long narrative with aliases, legal rules, ownership and temporal state transitions.
- `ledger_reach_boss`
  - Hardest focused stress label for ledger profile.

## 8) Artifact Conventions

Runtime outputs:
- `tmp/` for JSON summaries, intermediate reports, generated scenarios
- `docs/reports/` for curated human-facing markdown/html summaries

KB state:
- `kb_store/<kb_name>/kb.pl` and related state files

Important distinction:
- `tmp/*` is operational and ephemeral
- `docs/reports/*` should be curated before push

## 9) What Changed In This Commit Set

Staged source updates include:
- `kb_pipeline.py`
- `scripts/kb_interrogator.py`
- `scripts/run_story_stress_cycle.py`
- `scripts/run_blocksworld_lane.py` (new; includes zero-hit gate)
- `scripts/run_safety_gate.py` (new)
- `scripts/run_story_pack_suite.py` (new)
- `scripts/run_story_progressive_gulp.py` (new)
- `scripts/build_baseline_reset.py` (new)
- `tests/test_split_extraction_refine.py` (new)
- `tests/test_language_profile_routing.py` (new)
- `tests/test_progressive_gate_profiles.py` (new)
- `modelfiles/predicate_registry.blocksworld.json` (new)
- `docs/PROGRESS.md` (updated)
- curated reports under `docs/reports/` retained for this cycle

## 10) Latest Verified Metrics To Trust

From current cycle reports:

Blocksworld gated baseline (run A and run B, identical):
- symbolic solve/replay: `20/20`
- pilot pipeline pass: `8/8`
- avg init hit: `0.458334`
- avg goal hit: `0.458334`
- zero-hit: `0` (gate passed with threshold `0`)

Narrative pack corrected reruns:
- mid pack (corrected): `run_count=3`, `pipeline_pass=3`, best final `0.6452`
- upper-mid pack (corrected): `run_count=3`, `pipeline_pass=3`, best final `0.8718`
- caveat: these used an effectively empty general strict registry

## 11) Known Weaknesses / Footguns

1. Empty general registry footgun
- `modelfiles/predicate_registry.json` is empty.
- Any "strict narrative" claim using this file is misleading.

2. Config-mismatch footgun
- Running narrative packs with Blocksworld registry can create false-negative quality signals.
- Use domain-appropriate registry.

3. Clarification dead-end risk
- High eagerness + unresolved pronouns/speculative utterances can stall progress.
- Balance CE knobs before escalating model swaps.

4. Temporal exam coverage instability
- Some dense runs under temporal mode still emit too few temporal questions.

## 12) Process Pattern (Recommended Daily Loop)

1. Run safety gate.
2. Run gated Blocksworld baseline (`--max-zero-hit 0`).
3. Run target narrative lane (stress and/or progressive).
4. Run interrogator and collect fact audit + exam pass.
5. Promote repeated failures into explicit regression tests.
6. Re-run baseline to ensure no collateral regression.
7. Curate reports before commit.

## 13) Immediate Priorities For Next Agent

Priority 1
- Populate `modelfiles/predicate_registry.json` with meaningful general predicates.
- Re-run mid/upper-mid strict narrative lanes and replace provisional scores.

Priority 2
- Enforce temporal question floor for temporal runs in interrogator generation.

Priority 3
- Keep Blocksworld zero-hit gate mandatory in baseline cycle.

Priority 4
- Continue raw-input fidelity in all wild story ingestion tests.

## 14) First 60 Minutes Checklist (New Agent)

1. Confirm environment and model availability
```powershell
ollama list
python scripts/run_safety_gate.py
```

2. Reconfirm baseline
```powershell
python scripts/run_blocksworld_lane.py \
  --sample-size 20 --max-objects 4 --planner-depth 12 \
  --run-prethinker --prethinker-cases 8 \
  --backend ollama --base-url http://127.0.0.1:11434 \
  --model qwen3.5:9b \
  --prompt-file modelfiles/semantic_parser_system_prompt.md \
  --context-length 8192 \
  --prethinker-split-mode full \
  --predicate-registry modelfiles/predicate_registry.blocksworld.json \
  --strict-registry --max-zero-hit 0
```

3. Reconfirm narrative lane behavior
```powershell
python scripts/run_story_pack_suite.py \
  --packs tmp/story_pack_mid.md,tmp/story_pack_upper_mid.md \
  --backend ollama --base-url http://127.0.0.1:11434 \
  --model qwen3.5:9b \
  --prompt-file modelfiles/semantic_parser_system_prompt.md \
  --context-length 8192 \
  --exam-style detective --exam-question-count 20 --exam-min-temporal-questions 4
```

4. Start next improvement slice from Priority 1 above.

## 15) Collaboration / Orchestration Notes

- "Agent54" is the creative/scouting subagent role used to generate harder story packs and external research sweeps.
- Main agent role is gatekeeper/integrator:
  - remove low-signal retests
  - keep frontier pressure while preserving stable baselines
- Expected working mode:
  - "GO" means execute autonomous runs, gather artifacts, and report deltas with evidence.

---

If you are the next coding agent: start with Sections 12 and 14, then attack Section 13 Priority 1 immediately.
