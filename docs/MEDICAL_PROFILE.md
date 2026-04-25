# Medical Profile (`medical@v0`)

Date: 2026-04-25

`medical@v0` is the first formal bounded medical ontology package for Prethinker.

It is **not** a general clinical reasoning stack.

It is a profile for:

- normalized medical memory
- clarification-aware structured capture
- compact reusable predicates
- explicit type/argument discipline

## Profile Assets

- profile manifest: [modelfiles/profile.medical.v0.json](../modelfiles/profile.medical.v0.json)
- predicate registry: [modelfiles/predicate_registry.medical.json](../modelfiles/predicate_registry.medical.json)
- prompt supplement: [modelfiles/medical_compiler_prompt_supplement.md](../modelfiles/medical_compiler_prompt_supplement.md)
- type schema example: [modelfiles/type_schema.medical.example.json](../modelfiles/type_schema.medical.example.json)
- ontology prospector prompt: [modelfiles/medical_ontology_prospector_prompt.md](../modelfiles/medical_ontology_prospector_prompt.md)
- manifest-driven suite runner: [scripts/run_medical_profile_suite.py](../scripts/run_medical_profile_suite.py)
- local UMLS bridge generator: [scripts/build_umls_mvp_slice.py](../scripts/build_umls_mvp_slice.py)
- local UMLS Semantic Network builder: [scripts/build_umls_semantic_network_kb.py](../scripts/build_umls_semantic_network_kb.py)

## Canonical Predicate Palette

`medical@v0` currently formalizes these nine predicates:

- `taking/2`
- `has_condition/2`
- `has_symptom/2`
- `has_allergy/2`
- `underwent_lab_test/2`
- `lab_result_high/2`
- `lab_result_rising/2`
- `lab_result_abnormal/2`
- `pregnant/1`

## Current Rollup

Latest manifest-driven suite result:

- sharp-memory: `12/12` pass, `0` warn, `0` fail
- clinical checks: `7/7` pass, `0` warn, `0` fail
- UMLS bridge admission preflight: `9/9` pass, `0` fail
- prompt probe: `79/79` vs baseline `58/79`
- clarification probe: `38/38` vs baseline `21/38`

This set is not arbitrary.

It is reinforced by:

- the bounded UMLS MVP probes and bridge admission preflight
- the medical prompt probe
- the clarification-aware medical probe
- the local `qwen3.5:27b` ontology prospector run

See:

- [docs/UMLS_MVP.md](UMLS_MVP.md)
- [docs/ONTOLOGY_PROSPECTOR.md](ONTOLOGY_PROSPECTOR.md)
- [PROJECT_STATE.md](../PROJECT_STATE.md)

## Why The Palette Stays Small

The medical lane gets weaker if every drug, lab phrase, or diagnosis wording becomes its own predicate.

So `medical@v0` is designed around:

- stable predicates
- normalized concept arguments
- clarification when the meaning is too vague

Example:

- good:
  - `taking(lena, warfarin).`
- bad:
  - `taking_warfarin(lena).`

## Runtime Posture

Recommended posture for this profile:

- `compiler_mode=strict`
- `strict_registry=true`
- `strict_types=false`
- higher clarification eagerness
- `freethinker_resolution_policy=advisory_only`

Why `strict_types=false` by default:

The current type schema path still expects concrete entity atoms.

That makes the included type schema best understood as a **seed example** for argument discipline and evaluation, not as a universal strict-type gate for arbitrary patient names.

The bounded UMLS slice now emits a local `umls_bridge_facts.pl` file with normalized alias atoms and medical-profile semantic groups such as `medication`, `condition`, `symptom_or_finding`, `allergy`, `lab_or_procedure`, and `physiologic_state`.

Those bridge facts are intended for routing, validation, and clarification pressure. They are not intended to expand the nine-predicate palette.

The Semantic Network KB builder is now scaffolded for `SRDEF`, `SRSTR`, and optional `SRSTRE1`/`SRSTRE2` files. It should remain a local type/relation spine until the medical lane has tests that justify consuming more of it at runtime.

## Example Command

For batch experiments, the current stack can already use the profile assets explicitly:

```powershell
python kb_pipeline.py `
  --backend ollama `
  --base-url http://127.0.0.1:11434 `
  --model qwen3.5:9b `
  --scenario kb_scenarios/stage_02_rule_ingest.json `
  --kb-name medical_profile_demo `
  --predicate-registry modelfiles/predicate_registry.medical.json `
  --strict-registry `
  --type-schema modelfiles/type_schema.medical.example.json `
  --prompt-file modelfiles/semantic_parser_system_prompt.md
```

In the canonical MCP/gateway path, `active_profile=medical@v0` now loads the profile assets and UMLS bridge automatically. Batch experiments can still pass assets explicitly when they need controlled comparisons.

The profile can now also be exercised as one manifest-driven package with:

```powershell
python scripts/run_medical_profile_suite.py --model qwen3.5:9b
```

That suite rolls up:

- sharp-memory probe
- clinical checks probe
- medical prompt probe
- clarification-aware medical probe

Before model-backed runs, the bridge admission layer can be checked quickly with:

```powershell
python scripts/run_umls_bridge_admission_probe.py
```

That probe is deterministic and validates alias hits, vague medical surface forms, and predicate/type compatibility before spending time on local model runs.

## What Is Still Missing

`medical@v0` is a real profile package, but the stack is not yet fully profile-native.

Still missing:

- first-class `registry-profile` selection across every batch runner and legacy entrypoint
- automatic profile asset loading outside the canonical MCP/gateway path
- versioned overlay support
- cleaner type handling for arbitrary new patient names

So `medical@v0` is best understood as:

- a formal bounded ontology package
- plus live MCP/gateway runtime assets
- not yet a one-flag switch across every historical runner

## Bottom Line

This profile is the first concrete proof that Prethinker can narrow into a domain without turning into a giant universal ontology.

It is exactly the kind of packaged, bounded use case the repo has been moving toward.
