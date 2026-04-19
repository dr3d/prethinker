# Prethinker Orchestration (Codex + Agent54)

Last updated: 2026-04-13

## Purpose

This document defines exactly how we move up the ladder autonomously when you say `GO`:

- harder logic (height)
- worse/noisier language (width)
- deterministic verification
- repeat until a clear stop condition

This is the operating contract for current and future Codex agents.

## Core Intent

We are building a `Governed Intent Compiler` (GIC), not a chatbot.

- LLM proposes parse candidates.
- Deterministic runtime decides and applies.
- Progress is measured by rung/track evidence, not impression.

## Roles

### You (Director)

- Set strategic direction, pace, and stop/go decisions.
- Issue `GO` to start an autonomous frontier campaign.
- Issue `STOP` to halt.

### Codex Main Agent (Orchestrator + Curator)

- Runs sweeps, triages failures, integrates results.
- Maintains gate quality by pruning redundant low-signal retests.
- Preserves evidence quality and artifact consistency.

### Agent54 (Sub-Agent, model `gpt-5.4`)

- Generates new difficult story rungs.
- Focuses on creativity and adversarial language design.
- Produces deterministic scenario JSONs with validations.

## Model/Prompt Lane Policy

### Tuning lane (default)

- Model: `qwen3.5:9b` (bare)
- Prompt: runtime `--prompt-file modelfiles/semantic_parser_system_prompt.md`

### Frozen/baked lane (checkpoint only)

- Model: `qwen35-semparse:9b`
- Prompt source: baked SYSTEM only
- Runtime prompt file must be blank (or disabled)

### Non-negotiable rule

One system-prompt source per run. Never double-source.

`kb_pipeline.py` enforces this with:

- `--sp-conflict-policy error` (default)

## What `GO` Means

When you say `GO`, Codex should:

1. start the autonomous frontier cycle
2. keep GPU utilization high with real runs
3. add pressure at the frontier via Agent54
4. keep gate lanes clean and informative
5. stop only on explicit stop conditions

No additional prompting should be required.

## Autonomous Frontier Cycle

### Step 1: Lock run lane

- Confirm model/prompt lane and SP-source policy.
- Use temp KB roots for campaign hygiene: `--kb-root tmp/kb_store`.

### Step 2: Baseline sweep

- Run the active frontier tracks.
- Record failing slices and their failure types:
  - parse failure
  - apply/validation failure
  - clarification/escalation loop
  - semantic preservation/retraction miss

### Step 3: Frontier expansion by Agent54

- Spawn Agent54 (`gpt-5.4`) to add 1-3 new rungs near current failure edge.
- New rungs must include:
  - realistic difficult narrative language
  - at least one clarification-heavy turn object
  - deterministic validations
  - post-mutation query checks

### Step 4: Stabilize without diluting challenge

- Codex may do minimal bridge edits if runs fail for non-semantic parser-hostile wording.
- Do not remove the core challenge.

### Step 5: Re-run and compare

- Re-run only impacted tracks first.
- Promote when runs are clean:
  - `overall_status=passed`
  - zero parser/apply failures
  - validations pass

### Step 6: Gate curation

- Remove or demote redundant low-signal retest rungs from strict gate packs.
- Keep at least one anchor rung per behavior class.

### Step 7: Publish artifacts

- Persist run JSON and summary artifacts.
- Update track manifests/docs where needed.
- Log what changed and why.

## Height + Width Rung Design Standard

Each new rung should stress at least one of:

- retroactive correction/rebinding
- counterfactual vs actual separation
- preservation language (`keep`, `not`, `except`, `still`)
- multi-clause mutation + query-after-mutation
- pronoun/coref ambiguity with targeted clarification
- noisy/elliptic phrasing without losing deterministic truth

## Gate Prune Policy

Prune from strict retest lanes when all are true:

1. no novel failure signal for at least 3 consecutive sweeps
2. behavior is covered by a newer harder rung
3. runtime cost is high relative to signal

Never prune an entire behavior class.

## Stop Conditions

Campaign stops when any one triggers:

1. You say `STOP`.
2. Safety/contract violation:
   - double SP source active
   - severe regression in strict gate lanes
3. Plateau:
   - no net frontier gain across 2 consecutive full cycles
4. Time budget reached (default long-run window can be hours when requested).
5. Infrastructure instability prevents meaningful signal.

## GPU Long-Run Mode

When you want the GPU spinning for hours:

- run track/rung campaigns continuously
- use temp KB root to avoid clutter
- keep summaries per cycle
- prioritize frontier lanes before broad regressions

Example command pattern:

```bash
python scripts/run_track.py --track frontier_language_width_v7_addons --backend ollama --base-url http://127.0.0.1:11434 --model qwen3.5:9b --prompt-file modelfiles/semantic_parser_system_prompt.md --kb-root tmp/kb_store --fail-on-under
```

## Artifact Contract (Must Stay Stable)

Every cycle should produce:

- per-scenario run JSON
- per-track summary JSON
- reproducible command settings in artifacts
- clear pass/fail counts and failure-class notes

This preserves longitudinal comparability.

## Handoff Rules for Future Codex

If a new Codex resumes:

1. read this file, `AGENT-README.md`, `kb_scenarios/README.md`, and `tracks.json`
2. enforce single-SP-source policy
3. treat Agent54 as rung author (`gpt-5.4`)
4. keep curator role separate from author role
5. maintain artifact consistency and stop conditions

## Quick `GO` Checklist

When user says `GO`, execute:

1. confirm lane: bare `qwen3.5:9b` + runtime prompt file
2. run frontier baseline track(s)
3. spawn Agent54 for 1-3 new rungs
4. integrate + minimally stabilize
5. rerun impacted tracks
6. prune one redundant low-signal rung if justified
7. report results and whether stop condition hit

