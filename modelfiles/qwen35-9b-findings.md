# Qwen 3.5 9B Semantic Parser Findings

Date: 2026-04-09
Last updated: 2026-04-09 (post-provenance wiring)
Scope: LM Studio `/api/v1/chat` + semantic parser prompt in this folder.

## What Worked Reliably

- Clear fact assertions:
  - `Socrates is a man.`
- Clear rule patterns:
  - `If someone is a manager then they can approve budgets.`
  - `Whenever a patient has fever and cough, they may have flu.`
- Clear query patterns:
  - `Who is John's parent?`

For these, 9B consistently produced valid JSON with expected key shape.

## Failure Slice (Current)

- Pronoun-heavy and meta-instruction turns can consume output budget in reasoning and omit the final `message` block.
- Observed examples:
  - `John likes it.` (sometimes message missing; sometimes recoverable from reasoning JSON fragment)
  - `Actually, retract that: John is not Bob's parent.` (frequent reasoning-only, no final JSON)
  - `Translate this to French: the build passed.` (frequent reasoning-only, no final JSON)

## Practical Implications

- 9B is strong for direct semantic parsing lanes.
- 9B is less reliable on ambiguous correction/meta-command lanes unless wrapped by deterministic guardrails.

## Recommended 9B Runtime Pattern

1. Keep 9B as main parser for fact/rule/query turns.
2. Add deterministic pre-router for high-risk patterns:
   - explicit `retract` / correction cues
   - translation or non-logic meta instructions
   - unresolved pronoun-heavy statements
3. If model output is missing/invalid JSON:
   - apply deterministic fallback JSON (`intent=other` or route-specific fallback)
   - never pass malformed JSON downstream.

## Transferable Lessons (for future models)

- Prompt strictness alone is not enough for all slices.
- Deterministic fallback is load-bearing for safety and uptime.
- Evaluate per-slice, not only overall success rate.

## Backend Parity Check (LM Studio vs Ollama)

As of 2026-04-09, both backends pass the same 5-case edge battery with the tuned 2-pass harness:

- `John likes it.`
- `Actually, retract that: John is not Bob's parent.`
- `Translate this to French: the build passed.`
- `Who is John's parent?`
- `If someone is a manager then they can approve budgets.`

Observed backend behavior differences:

- LM Studio:
  - often returns `output[]` with `type=reasoning` and `type=message`
  - sometimes message is missing on hard turns
- Ollama:
  - can return empty `message.content` with long `message.thinking`
  - reliable after extracting JSON fallback from `message.thinking`

Operational guidance:

- Keep JSON extraction fallback enabled for both backends.
- Keep route-locked 2-pass prompt + strict validator enabled.
- Treat fallback extraction as expected runtime behavior, not an exception.

## Current Tuning Baseline

New provenance-aware baseline runs (Ollama `qwen3.5:9b`) are passing:

- `kb_runs/stage_01_people_ladder_tune_r1.json` -> `2/2` validations passed
- `kb_runs/stage_02_people_ladder_tune_r1.json` -> `1/1` validations passed

Both runs share prompt snapshot:

- `prompt_id`: `sp-ad589d272fbb`
- snapshot: `modelfiles/history/prompts/sp-ad589d272fbb.md`

## Tracking Guidance (Now Enforced)

Every new run should be compared by:

- `prompt_provenance.prompt_id`
- `overall_status`
- `validation_passed / validation_total`
- turn-level parser/apply failures

Use `docs/index.html` filters (scenario + prompt id) to monitor regression before advancing to harder rungs.
