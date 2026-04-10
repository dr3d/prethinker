# Goldilocks Semparse Roundtrip Report

Date: 2026-04-10

## Objective

Run a realistic narrative parse experiment:

1. Semparse a Goldilocks story into a Prolog KB.
2. Attempt story reconstruction from the generated KB.
3. Record concrete behavior (including failures) for future tuning.

## Input Artifacts

- Story text: `stories/goldilocks_roundtrip.md`
- Scenario: `kb_scenarios/story_goldilocks_roundtrip.json`

## Run Configuration

Command executed:

```bash
python kb_pipeline.py --scenario kb_scenarios/story_goldilocks_roundtrip.json --backend ollama --base-url http://127.0.0.1:11434 --model qwen3.5:9b --context-length 8192 --runtime core --kb-root tmp/kb_store_roundtrip --prompt-file modelfiles/semantic_parser_system_prompt.md --prompt-history-dir tmp/prompt_history --clarification-eagerness 0.55 --max-clarification-rounds 3 --clarification-answer-model gpt-oss:20b --clarification-answer-backend ollama --clarification-answer-base-url http://127.0.0.1:11434 --clarification-answer-context-length 16384 --write-corpus-on-fail --out tmp/goldilocks_roundtrip_run.json
```

Run metadata:

- Run ID: `run-20260410T160231Z-story_goldilocks_roundtr-qwen3_5_9b-2684`
- Prompt ID: `sp-e0a66d9a2fbe`
- Start UTC: `2026-04-10T16:02:31+00:00`
- End UTC: `2026-04-10T16:17:06+00:00`

## Topline Results

- Turns total: `50`
- Overall status: `failed`
- Parser failures: `7`
- Apply failures: `7`
- Clarification requests: `7`
- Clarification rounds total: `36`
- Synthetic clarification answers used: `36`
- Validation checks: `0/0` (scenario had no deterministic validations)

KB was still persisted due `--write-corpus-on-fail`:

- KB path: `tmp/kb_store_roundtrip/story_goldilocks_roundtrip/kb.pl`
- Clauses written: `29`
- Predicate signatures: `16`

## Failure Ledger

Captured to:

- `tmp/goldilocks_failure_ledger.json`

Problematic turns recorded: `14`

Representative issues:

- Turn 4: multi-fact output in a single `assert_fact` turn
  - utterance: "The house belonged to Papa Bear, Mama Bear, and Baby Bear."
  - logic: `belongs_to(house, papa_bear). belongs_to(house, mama_bear). belongs_to(house, baby_bear).`
  - error: `assert_fact requires logic_string == facts[0]`

- Turn 28: malformed zero-arity style fact
  - utterance: "Mama Bear had a medium bed."
  - logic: `mama_bear_in_medium_bed.`
  - error: `facts[0] is not valid Prolog fact/goal`

- Turns 45-46: unsupported argument shape for `saw/` facts
  - utterances about someone lying in bed
  - logic emitted as 3-argument relation with nested terms
  - error: `facts[0] is not valid Prolog fact/goal`

- Several turns deferred by clarification loop conditions:
  - `Clarification loop detected from answer model`
  - `Maximum clarification rounds reached`
  - `Clarification answer model returned non-informative answer`

## Generated KB Snapshot (Observed)

The KB preserved part of the story world, but with semantic drift and predicate mismatch.

Examples present:

- `goldilocks(little_girl).`
- `goldilocks_found(small_house, forest).`
- `tasted(goldilocks, porridge_of_papa_bear).`
- `too_hot(papa_bear_porridge).`
- `too_hard(papa_bear_chair, goldilocks).`
- `fits_goldilocks(baby_bear_bed, goldilocks).`
- `saw(baby_bear, goldilocks).`

Examples of drift/noise:

- `chairs_in_house(baby_bear, baby_bear).`
- `goldilocks_found(goldilocks, papa_bear_porridge).`
- `has_porridge(goldilocks, mama_bear_chair).`

## Reconstruction Attempt

Reconstruction file generated from KB clauses:

- `tmp/goldilocks_reconstructed_story.md`

Method:

- Deterministic template mapping from predicate clauses to English lines.
- No hand correction applied.

Outcome:

- Partial narrative is recoverable.
- Event ordering and role binding quality degrade quickly where predicate drift occurred.
- Reconstruction is useful as an observational artifact, not as a faithful retelling.

## What This Run Is Useful For

- Baseline stress sample for long narrative ingestion.
- Concrete evidence of where current parser/policy fails on dense story input.
- Candidate source for future golden-build process (after rigorous probe Q&A and normalization).

## Output Artifacts

- Run JSON: `tmp/goldilocks_roundtrip_run.json`
- Persisted KB: `tmp/kb_store_roundtrip/story_goldilocks_roundtrip/kb.pl`
- Failure ledger: `tmp/goldilocks_failure_ledger.json`
- Reconstructed story: `tmp/goldilocks_reconstructed_story.md`
