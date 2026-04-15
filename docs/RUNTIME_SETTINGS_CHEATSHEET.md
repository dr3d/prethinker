# Prethinker Runtime Settings Cheat Sheet

Last updated: 2026-04-15

## Purpose

This is the operational cheat sheet for running Prethinker with predictable behavior.
It focuses on runtime controls, clarification engine (CE) behavior, sidecar usage, and temporal sequencing.

## Mental Model

Prethinker has two layers:

1. Compiler path (deterministic-first):
   - Parses utterances into structured intents.
   - Applies validated facts/rules/queries/retracts.
2. CE sidecar path (optional clarifier):
   - Answers clarification questions when ambiguity blocks safe writes.
   - Uses bounded recent-turn + KB context.
   - Improves short-horizon disambiguation without changing deterministic apply rules.

## Key Control Groups

### Core model/runtime

- `--backend`
- `--base-url`
- `--model`
- `--runtime`
- `--context-length`

### Deterministic constraints

- `--predicate-registry`
- `--strict-registry`
- `--type-schema`
- `--strict-types`

### Clarification engine (CE)

- `--clarification-eagerness`
- `--clarification-eagerness-mode` (`static` or `adaptive`)
- `--max-clarification-rounds`
- `--require-final-confirmation`

### CE adaptive backoff (when mode is `adaptive`)

- `--clarification-eagerness-new-kb-boost`
- `--clarification-eagerness-existing-kb-boost`
- `--clarification-eagerness-decay-turns`
- `--clarification-eagerness-decay-clauses`

### Sidecar clarification model

- `--clarification-answer-model`
- `--clarification-answer-backend`
- `--clarification-answer-base-url`
- `--clarification-answer-context-length`
- `--clarification-answer-history-turns`
- `--clarification-answer-kb-clause-limit`
- `--clarification-answer-kb-char-budget`
- `--clarification-answer-min-confidence`

### Served-LLM override for CE

- `--served-llm-model`
- `--served-llm-backend`
- `--served-llm-base-url`
- `--served-llm-context-length`

### Temporal sequencing

- `--temporal-dual-write`
- `--temporal-predicate` (default `at_step`)

### Progress memory policy

- `--progress-memory`
- `--progress-low-relevance-threshold`
- `--progress-high-risk-threshold`

## Default Safety Posture

- CE mode defaults to `static`.
- Temporal sequencing defaults to off unless `--temporal-dual-write` is passed.
- Registry/type strictness is opt-in and should be enabled for controlled domain runs.

## Recommended Presets

### Preset A: Safe static baseline (default operations)

Use for reproducible day-to-day runs and regression baselines.

```powershell
python kb_pipeline.py `
  --backend ollama --base-url http://127.0.0.1:11434 --model qwen3.5:9b `
  --runtime core `
  --scenario kb_scenarios/story_glitch_in_the_airlock_raw_line.json `
  --kb-name baseline_static_glitch `
  --prompt-file modelfiles/semantic_parser_system_prompt.md `
  --predicate-registry modelfiles/predicate_registry.json --strict-registry `
  --clarification-eagerness 0.20 `
  --clarification-eagerness-mode static `
  --max-clarification-rounds 2 `
  --clarification-answer-model qwen3.5:9b `
  --clarification-answer-backend ollama `
  --clarification-answer-base-url http://127.0.0.1:11434 `
  --clarification-answer-context-length 8192 `
  --clarification-answer-min-confidence 0.0 `
  --out tmp/runs/baseline_static_glitch.pipeline.json
```

### Preset B: Adaptive CE for new KB bootstrapping

Use when standing up a new ontology and you want CE to start strict, then relax.

```powershell
python kb_pipeline.py `
  --backend ollama --base-url http://127.0.0.1:11434 --model qwen3.5:9b `
  --runtime core `
  --scenario kb_scenarios/story_glitch_in_the_airlock_raw_line.json `
  --kb-name adaptive_bootstrap_glitch `
  --prompt-file modelfiles/semantic_parser_system_prompt.md `
  --predicate-registry modelfiles/predicate_registry.json --strict-registry `
  --clarification-eagerness 0.20 `
  --clarification-eagerness-mode adaptive `
  --clarification-eagerness-new-kb-boost 0.35 `
  --clarification-eagerness-existing-kb-boost 0.12 `
  --clarification-eagerness-decay-turns 24 `
  --clarification-eagerness-decay-clauses 120 `
  --max-clarification-rounds 2 `
  --clarification-answer-model qwen3.5:9b `
  --clarification-answer-backend ollama `
  --clarification-answer-base-url http://127.0.0.1:11434 `
  --clarification-answer-context-length 8192 `
  --clarification-answer-min-confidence 0.0 `
  --out tmp/runs/adaptive_bootstrap_glitch.pipeline.json
```

### Preset C: Story mode with temporal sequencing

Use for narrative/state-change stories where order matters.

```powershell
python kb_pipeline.py `
  --backend ollama --base-url http://127.0.0.1:11434 --model qwen3.5:9b `
  --runtime core `
  --scenario kb_scenarios/story_goldilocks_roundtrip.json `
  --kb-name story_temporal_goldilocks `
  --prompt-file modelfiles/semantic_parser_system_prompt.md `
  --predicate-registry modelfiles/predicate_registry.goldilocks.json --strict-registry `
  --type-schema modelfiles/type_schema.goldilocks.json --strict-types `
  --temporal-dual-write --temporal-predicate at_step `
  --clarification-eagerness 0.20 --clarification-eagerness-mode static `
  --max-clarification-rounds 2 `
  --clarification-answer-model qwen3.5:9b `
  --clarification-answer-backend ollama `
  --clarification-answer-base-url http://127.0.0.1:11434 `
  --clarification-answer-context-length 8192 `
  --clarification-answer-min-confidence 0.0 `
  --out tmp/runs/story_temporal_goldilocks.pipeline.json
```

### Preset D: Medical/static ontology ingestion

Use for mostly timeless domain facts. Keep temporal off unless ingesting case timelines.

```powershell
python kb_pipeline.py `
  --backend ollama --base-url http://127.0.0.1:11434 --model qwen3.5:9b `
  --runtime core `
  --scenario kb_scenarios/acid_01_medical_baseline.json `
  --kb-name medical_static `
  --prompt-file modelfiles/semantic_parser_system_prompt.md `
  --predicate-registry modelfiles/predicate_registry.json --strict-registry `
  --clarification-eagerness 0.18 `
  --clarification-eagerness-mode static `
  --max-clarification-rounds 2 `
  --clarification-answer-model qwen3.5:9b `
  --clarification-answer-backend ollama `
  --clarification-answer-base-url http://127.0.0.1:11434 `
  --clarification-answer-context-length 8192 `
  --clarification-answer-min-confidence 0.0 `
  --out tmp/runs/medical_static.pipeline.json
```

## One-Liner Focus Gate (Batch)

Static CE:

```powershell
python scripts/run_gate_cycle.py --batch glitch_focus --model qwen3.5:9b --clarification-eagerness-mode static
```

Adaptive CE + temporal:

```powershell
python scripts/run_gate_cycle.py --batch glitch_focus --model qwen3.5:9b --clarification-eagerness-mode adaptive --temporal-dual-write
```

## Diagnostics

Inspect all current runtime flags:

```powershell
python kb_pipeline.py --help
```

Inspect batch runner flags:

```powershell
python scripts/run_gate_cycle.py --help
```

Check model availability:

```powershell
ollama list
```

