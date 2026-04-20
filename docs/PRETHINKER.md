# Prethinker

This is the stable design overview for the project.

If you want live metrics, read [docs/PROGRESS.md](/D:/_PROJECTS/prethinker/docs/PROGRESS.md).

If you want the product story in plainer language, read [docs/EXPLAINER.md](/D:/_PROJECTS/prethinker/docs/EXPLAINER.md).

## One-Sentence Definition

Prethinker is a governed intent compiler that sits between natural language and durable symbolic state.

## The Core Bet

The project is built on one architectural bet:

- neural models are useful for interpretation
- deterministic systems should retain authority over state

That means:

- the model may propose
- the runtime may decide

Prethinker is valuable only if that trust boundary stays legible.

## The System Shape

At a high level:

`language -> compiler proposal -> deterministic gate -> KB mutation/query -> evidence`

In practice that means:

1. A user utterance arrives.
2. The compiler classifies it as a write, query, retract, rule, or `other`.
3. A parser proposal is emitted in a strict machine-readable schema.
4. Deterministic validation and normalization decide whether it is admissible.
5. The runtime either:
   - commits a mutation
   - answers a query
   - requests clarification
   - rejects the operation
6. The run is logged with prompt/model provenance and can be graded later.

## What Prethinker Is

Prethinker is:

- a governed adapter for language-to-logic interaction
- a persistent symbolic memory layer
- a front-door compiler for controlled KB mutation
- a research and evaluation harness for improving that compiler honestly

## What Prethinker Is Not

Prethinker is not:

- a general chatbot
- a freeform reasoning engine with silent state authority
- a passive transcript logger
- a production-ready universal parser for every domain and language style

## Why "Governed" Matters

The project is designed to resist a very specific failure mode:

language that sounds right while writing the wrong thing.

The whole stack exists to narrow that gap.

That is why the system leans on:

- schema discipline
- optional registry/type constraints
- clarification policy
- deterministic runtime apply/query
- artifact-backed evaluation

## Product Direction

The product direction is a UI or adapter layer that can sit in front of a user's chatbot of choice.

In that shape:

- the chatbot remains the fluent conversational surface
- Prethinker listens to the interaction stream
- eligible turns become facts, rules, retracts, and queries
- the KB becomes durable, inspectable memory

So the best metaphor is:

- not "memory plugin"
- not "another chatbot"
- but "governed stenographer and compiler"

It records selectively.
It formalizes carefully.
It refuses when needed.

## The Two-Rail Future

The design now distinguishes two roles:

### Prethinker

The strict compiler.

- schema-bound
- mutation-aware
- clarification-capable
- the only role allowed to authorize KB writes

### Freethinker

The bounded clarification liaison.

- context-aware
- non-authoritative
- consulted only when Prethinker hesitates
- may suggest a clarification answer or a better clarification question
- may not write to the KB directly

This split is about permissions, not necessarily different model families.

Both roles can be backed by the same underlying `qwen3.5:9b` weights with different prompts and policies.

## Current Reality

As of April 20, 2026:

- the canonical interactive entryway is `process_utterance()` in [src/mcp_server.py](/D:/_PROJECTS/prethinker/src/mcp_server.py)
- the console in [ui_gateway/](/D:/_PROJECTS/prethinker/ui_gateway) is the main manual test cockpit
- the safety gate is green at `142 passed`
- strict Blocksworld remains the last verified stable proof lane
- frozen `process_utterance()` frontier packs now anchor the hardest interactive families
- correction is down to `2/12` remaining failures
- temporal is now `8/12` pass, `4/12` warn, and `0/12` fail on the frozen pack
- Freethinker is still defaulted to `off`

That means the repo already supports the governed compiler shape directly.

The clarification-liaison shape is partially scaffolded and intentionally not yet allowed to change baseline behavior.

## Why The Repo Looks The Way It Does

The codebase has three different kinds of artifacts because they serve different jobs:

- runtime code
  - `kb_pipeline.py`
  - `src/mcp_server.py`
  - `ui_gateway/`
- evidence and reports
  - `kb_runs/`
  - `docs/reports/`
  - `docs/PROGRESS.md`
- design notes
  - `docs/EXPLAINER.md`
  - `docs/FREETHINKER_DESIGN.md`
  - `docs/ONTOLOGY_STEERING.md`
  - `docs/ORCHESTRATION.md`

The point is not just to build a parser.

It is to build a parser whose progress can be inspected without self-deception.

## Design Rule

Prethinker should become broader by architecture, not looser by authority.

That means:

- more coverage through better context handling and better ontology steering
- not through quieter trust boundaries

If the project succeeds, it will not be because the model became magically trustworthy.

It will be because the system became better at converting language into inspectable, governed state.
