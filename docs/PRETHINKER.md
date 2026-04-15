# PRETHINKER

Date: 2026-04-15
Author: CTO Report (Codex)

## Executive Summary

PRETHINKER is a governed intent compiler for language-to-logic execution.

It does one thing with discipline:

1. read natural language,
2. propose symbolic operations,
3. validate and gate those operations deterministically,
4. mutate/query a persistent Prolog-style knowledge base,
5. grade the result with an interrogation layer.

The key strategic choice is this:

- neural model for interpretation,
- deterministic runtime for authority.

That split is why this can work in sensitive domains where auditability matters.

## What PRETHINKER Is

PRETHINKER is not a chatbot. It is a compiler-like system for turning language into controlled knowledge operations.

Core operation intents:

- `assert_fact`
- `assert_rule`
- `retract`
- `query`
- `other`

Core outcome:

- durable, interrogable symbolic state instead of hidden conversational drift.

## Why We Built It

General LLM answers are often fluent but ungrounded. PRETHINKER exists to prevent "plausible but wrong" from becoming system state.

Design goals:

- determinism at commit time,
- explicit ambiguity handling,
- reproducible evidence for every run,
- progressive hardening via regression packs and wild-language stress.

## How PRETHINKER Was Made

PRETHINKER was built in phases, each phase reducing uncertainty in a different part of the stack.

Phase 1: deterministic engine baseline

- established core term/unification/resolution behavior,
- validated runtime mutation and query correctness,
- added stable unit/regression harnesses.

Phase 2: intent parsing and guarded mutation

- added two-pass parse and route decisions,
- added strict predicate registry and optional type-schema checks,
- blocked invalid or unsafe writes before runtime apply.

Phase 3: clarification orchestration

- added bounded clarification rounds,
- added confidence and uncertainty controls,
- added explicit confirmation paths for higher-risk commits.

Phase 4: evidence and grading

- added run manifests and report generation,
- added KB interrogator to score coverage, precision, and exam performance,
- made quality measurable per scenario, not anecdotal.

Phase 5: wild ingestion and temporal semantics

- shifted from synthetic-only ladder pressure toward raw internet-style text,
- added temporal dual-write (`fact(...)` plus `at_step(T, fact(...))`) for narrative state tracking,
- verified temporal indexing improves interrogation outcomes on story-like workloads.

## How It Works

Operational spine:

`raw text -> parser proposal -> deterministic gate -> runtime apply/query -> interrogator grading`

Detailed path:

1. Ingest

- Input enters as raw text with no hidden "smart cleanup".
- Parser proposes operation intent + logic string candidates.

2. Gate

- Validates clause shape and intent schema.
- Applies registry/type constraints when configured.
- Applies ambiguity and clarification policy.
- Can stage, defer, or commit.

3. Runtime

- Deterministic core applies accepted facts/rules/retractions.
- Queries run against current KB state.
- Writes are durable in named KB namespaces.

4. Evidence

- Every run emits machine-readable artifacts and human-readable reports.
- Interrogator grades extraction quality against source text.

5. Feedback loop

- Repeated failure patterns become scenarios/rungs.
- Scenarios become regression gates.
- System improves by closing measured gaps.

## Current State (As Of 2026-04-15)

Latest measured scorecard:

- Baseline gate reliability (`baseline_focus`)
  - pipeline pass: `5/5`
  - audit coverage: `0.865`
  - audit precision: `0.974`
  - exam pass: `0.793333`
  - temporal exam pass: `0.4`
- Wild story ingest (`glitch_focus`, non-temporal)
  - pipeline pass: `3/3`
  - audit coverage: `0.583333`
  - audit precision: `0.8`
  - exam pass: `0.608333`
  - temporal exam pass: `0.333333`
- Wild story ingest (`glitch_focus`, temporal dual-write enabled)
  - pipeline pass: `3/3`
  - audit coverage: `0.65`
  - audit precision: `0.906667`
  - exam pass: `0.933333`
  - temporal exam pass: `0.921296`
  - deltas vs non-temporal:
    - coverage `+0.067`
    - precision `+0.107`
    - exam `+0.325`
    - temporal exam `+0.588`
- Deterministic health
  - targeted suite: `36 passed`
  - engine regression suite: `37 passed`

Interpretation:

- System stability is now strong in core gate runs.
- Temporal sequencing is a real quality multiplier on narrative material.
- We still need better non-temporal performance on fragmented noisy packaging.

## Why I Think We Can Be Successful

Reason 1: the architecture is correctly split

- LLM handles uncertain language.
- Deterministic runtime controls truth mutation.
- This prevents silent drift and keeps state auditable.

Reason 2: we measure what matters

- not just "did it run",
- but coverage, precision, exam pass, temporal reasoning, and mutation quality.

Reason 3: we have a functioning improvement loop

- failure discovery -> scenario formalization -> regression gate -> re-measure.

Reason 4: we are now testing in realistic language

- synthetic ladders remain for regression,
- wild/noisy corpora now pressure real ingestion behavior.

Reason 5: we have clear promotion thresholds

- precision target `>= 0.90`
- coverage target `>= 0.85`
- exam target `>= 0.80`
- temporal exam target `>= 0.70`
- incorrect mutation target `<= 0.02`

This is what "engineering a compiler" looks like, not prompt theater.

## How PRETHINKER Will Get Better

Near-term improvements already defined:

1. Keep one mandatory command path for baseline gates.
2. Keep temporal dual-write on narrative stress packs while collecting more A/B evidence.
3. Expand wild corpora and preserve raw-input discipline.
4. Bring constrained frontend proposal mode (`shadow`) to statistically net-positive before any active promotion.
5. Build stronger interrogator packs for contradiction, causality, and temporal consistency.

Mid-term improvements:

1. Add stronger ontology alignment controls for open-domain ingestion.
2. Improve pronoun and possession disambiguation under noisy syntax.
3. Add dynamic clarification behavior tuned by KB maturity and recent confidence history.
4. Prepare medical lane onboarding (UMLS-backed schema + targeted tests).

Long-term improvements:

1. Domain packs for legal/medical/operational logs.
2. Higher-fidelity temporal reasoning with robust persistence rules.
3. Better admission control for low-confidence novel predicates.
4. Continued reduction of false commits under adversarial language.

## Risk Register (Honest)

Risk: semantic overgeneralization

- Mitigation: stricter registry/type gating, stronger interrogator probes, and scenario promotion of failure modes.

Risk: narrative state collapse without time index

- Mitigation: temporal dual-write now operational and should remain default for story-like material.

Risk: good ingestion but weak retelling fidelity

- Mitigation: emphasize interrogator scoring and targeted query packs, not only pipeline pass.

Risk: overfitting to canonical stories

- Mitigation: wild corpus ingestion and formalized excursions as first-class test lanes.

Risk: docs drift from runtime reality

- Mitigation: tie documentation updates to run artifacts and scorecard refresh cadence.

## Recommended Operating Posture

- Treat PRETHINKER as a controlled compiler, not a free-form assistant.
- Favor measurable improvements over aesthetic prompt changes.
- Promote only on aggregate metrics, not one-off wins.
- Keep all claims backed by artifact paths and reproducible command lines.

## Bottom Line

PRETHINKER is now beyond concept stage.

It has:

- a coherent architecture,
- deterministic authority at commit time,
- reproducible quality gates,
- measurable gains from temporal semantics,
- and a credible path to higher-stakes domains.

Success is not guaranteed, but it is engineering-plausible and increasingly evidence-backed.

If we keep the current discipline, this project can deliver a practical, auditable language-to-logic system that is materially better than unconstrained LLM workflows for stateful reasoning tasks.
