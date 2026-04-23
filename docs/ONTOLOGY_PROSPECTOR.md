# Ontology Prospector

Date: 2026-04-23

This note describes the **local-only ontology prospector** for the bounded medical lane.

The prospector is not part of the live `Prethinker` runtime.

It is an offline tool for using a larger local model to scan a bounded medical corpus and propose a compact canonical predicate palette.

## Why This Exists

The bounded medical lane is now specific enough that hand-authoring every predicate decision would be slow and brittle.

But letting the live runtime invent predicates from open medical language would be worse.

So the right split is:

- `Prethinker` stays strict at runtime
- the ontology prospector runs offline
- a larger local model scans medical language
- humans review what gets promoted into `medical@v0`

This makes the model an **ontology prospector**, not the authority.

## What It Produces

The prospector looks for:

- recurring relation shapes
- reusable argument slots
- places where the existing medical palette is already enough
- places where the model is trying to invent lexical junk like `taking_warfarin/1`

It writes local reports under `tmp/...`, not into the public KB.

## Tracked Inputs

- prompt: [modelfiles/medical_ontology_prospector_prompt.md](../modelfiles/medical_ontology_prospector_prompt.md)
- corpus: [docs/data/medical_ontology_prospector_corpus.json](data/medical_ontology_prospector_corpus.json)
- runner: [scripts/run_medical_ontology_prospector.py](../scripts/run_medical_ontology_prospector.py)

The corpus intentionally includes:

- direct medical statements
- vague shorthand
- clarified follow-ups
- pronoun-led cases that became sharp only after clarification

## Recommended Local Run

Run this locally against your larger Qwen model.

Example:

```powershell
python scripts/run_medical_ontology_prospector.py `
  --model qwen3:27b `
  --context-length 32768 `
  --timeout 240 `
  --temperature 0.2 `
  --think-enabled
```

If your local 27B tag is different, replace `qwen3:27b` with your actual Ollama model tag.

## Output

Default output directory:

- `tmp/licensed/umls/2025AB/prethinker_mvp/ontology_prospector_latest/`

Main artifacts:

- `summary.json`
- `summary.md`

The summary highlights:

- candidate predicates
- support counts across cases
- rejected lexicalized patterns
- convergence metrics

## What “Good” Looks Like

We want to see:

- a small number of recurring predicates
- strong reinforcement of predicates like `taking/2`, `has_condition/2`, `has_symptom/2`
- low single-case predicate sprawl
- explicit rejection of medication-specific or phrase-shaped predicates

## What “Bad” Looks Like

We should worry if the prospector keeps proposing:

- one predicate per medication
- one predicate per lab phrase
- mostly single-case predicates
- no stable convergence on argument structure

That would mean the lane is not ready for a formal package yet.

## Promotion Rule

Nothing from the prospector should become runtime ontology automatically.

Promotion should still be:

1. local prospecting
2. review
3. registry/profile change
4. prompt/profile update
5. measured probe rerun

That keeps the medical lane sharp without letting ontology drift silently in production.
