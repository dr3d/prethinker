# Prethinker

This is the stable design overview for the project.

If you want the current project snapshot, read [PROJECT_STATE.md](https://github.com/dr3d/prethinker/blob/main/PROJECT_STATE.md).

If you want the product story in plainer language, read [docs/EXPLAINER.md](https://github.com/dr3d/prethinker/blob/main/docs/EXPLAINER.md).

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

`language -> router/context plan -> semantic workspace -> deterministic gate -> KB mutation/query -> evidence`

In practice that means:

1. A user utterance arrives.
2. The router/context layer selects relevant profile context, predicate
   contracts, recent-turn context, and compact KB seed material.
3. The active research path emits a `semantic_ir_v1` workspace rather than
   forcing immediate Prolog.
4. Deterministic validation, mapping, normalization, and admission diagnostics
   decide whether any candidate operation is admissible.
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

## Domain Fit

Prethinker should be judged against domains where governed mutation is actually compatible with the language people use.

The key constraint is simple:

- precise state requires sufficiently precise language

When language stays highly implicit, the system has only three options:

- clarify
- abstain
- guess

Because Prethinker is designed as a governed compiler, it should usually prefer the first two over the third.

That means:

- semi-formal and formal conversational domains are the best fit
- casual conversational English is a weaker fit unless confirmation pressure is higher
- some perceived brittleness is the expected cost of refusing silent bad writes

In other words, the project should become broader by architecture and domain tuning, not by pretending ambiguous chat is already precise enough for durable KB mutation.

## Current Semantic Workspace Path

The current design has one main interpretation path:

### Prethinker

- schema-bound
- mutation-aware
- clarification-capable
- the only role allowed to authorize KB writes
- backed by a stronger local `qwen/qwen3.6-35b-a3b` Semantic IR pass
- supplied with recent context, selected domain profile context, predicate
  contracts, and a compact KB seed

That lets the main workspace do more of the discourse and truth-maintenance
setup before deterministic admission, without adding a second mainline model
role.

## Current Reality

As of April 29, 2026:

- the canonical interactive entryway is `process_utterance()` in [src/mcp_server.py](https://github.com/dr3d/prethinker/blob/main/src/mcp_server.py)
- the console in [ui_gateway/](https://github.com/dr3d/prethinker/tree/main/ui_gateway) is the main manual test cockpit
- the prompt-book UI and ledger telemetry are the primary live demonstration surface
- `semantic_ir_v1` is the active architecture pivot for model understanding before deterministic admission
- `semantic_router_v1` is the active context/profile planner when `active_profile=auto`
- [src/semantic_ir.py](https://github.com/dr3d/prethinker/blob/main/src/semantic_ir.py) owns mapper projection policy and admission diagnostics
- `medical@v0`, `legal_courtlistener@v0`, and `sec_contracts@v0` are the main starter domain lanes
- UMLS Semantic Network assets are built locally for type/relation explanation
- `intake_plan_v1` and `profile_bootstrap_v1` are the current hint-free raw-document/profile discovery path

That means the repo already supports the governed compiler shape directly.

The old clarification-liaison experiment is retired; it is no longer part of the
active gateway surface. The bigger current research question is whether richer
semantic workspaces can reduce English-specific Python rescue logic while
preserving the same authority boundary. Current improvements should come from
model workspaces, context/profile contracts, KB context, or structural mapper
checks, not Python phrase patches.

## Why The Repo Looks The Way It Does

The codebase has three different kinds of artifacts because they serve different jobs:

- runtime code
  - `kb_pipeline.py`
  - `src/mcp_server.py`
  - `ui_gateway/`
- local evidence and run artifacts, which should stay ignored
  - `tmp/`
  - `kb_runs/`
  - `kb_store/`
  - generated reports when explicitly rendered
- design notes
  - `PROJECT_STATE.md`
  - `docs/EXPLAINER.md`
  - `docs/SEMANTIC_IR_MAPPER_SPEC.md`
  - `docs/DOMAIN_PROFILE_CATALOG.md`
  - `docs/PROJECT_HORIZON.md`

The point is not just to build a parser.

It is to build a parser whose progress can be inspected without self-deception.

## Design Rule

Prethinker should become broader by architecture, not looser by authority.

That means:

- more coverage through better context handling and better ontology steering
- not through quieter trust boundaries

If the project succeeds, it will not be because the model became magically trustworthy.

It will be because the system became better at converting language into inspectable, governed state.
