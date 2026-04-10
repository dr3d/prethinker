# Prethinker Explainer

Prethinker is a neuro-symbolic training workbench with one clear mission: shape a language model into a specialized semantic parser that does one job extremely well. That job is to take natural language, break it into formal logic, and hand that logic to a deterministic Prolog runtime for storage, inference, and retrieval.

It is not built as a general chatbot. It is built as a logic compiler.

At the front of the system, an LLM reads an utterance and tries to map it into one of a small set of intent types:

- `assert_fact`
- `assert_rule`
- `query`
- `retract`
- `other`

Then it extracts structured logical content:

- predicates
- atoms/constants
- variables
- facts
- rules
- queries

The key design principle is this: the LLM proposes, the deterministic runtime decides.

## Pipeline Internals

The pipeline in `kb_pipeline.py` runs as a disciplined sequence:

1. Route classification  
The system first decides what kind of operation the utterance represents.

2. Extraction pass  
The model produces logic-focused output (not free-form prose), then a refinement step normalizes this into strict JSON schema and Prolog-ready clauses.

3. Validation and repair  
The output is validated for schema correctness, Prolog shape, route consistency, and optional registry/type constraints. If malformed, the system can run a repair prompt.

4. Clarification gating (CE policy)  
Each parsed turn carries uncertainty signals (`uncertainty_score`, ambiguity markers, clarification flags).  
A Clarification Eagerness (CE) factor acts like an “annoyance dial”:
- high CE = ask clarification sooner
- low CE = proceed unless uncertainty is very high

This gate determines whether to apply to KB immediately or request clarification first.

5. Deterministic apply  
Accepted clauses are applied to the local Prolog core runtime (`assert_fact`, `assert_rule`, `retract_fact`, `query_rows`) against named persistent KB namespaces.

6. Validation checks  
Scenario contracts run deterministic queries and compare expected results.

7. Provenance and reporting  
Every run stores prompt hash/snapshot, model settings, turn traces, validation outcomes, and drift signals for reproducible iteration.

## Ladder Strategy

The ladder is the training discipline.  
Instead of random prompt tweaks, Prethinker climbs progressive rungs:

- Stage 1: atomic facts
- Stage 2: rule ingestion
- Stage 3: transitive/chain reasoning
- then acid tests for harder failure modes (temporal overrides, long context lineage, ambiguity pressure, etc.)

The workflow is cyclical and empirical:

- tune system prompt
- run rung(s)
- inspect failures
- retune
- rerun from lower rungs upward
- repeat until higher rungs stabilize
- then attack acid tests
- loop again

So prompt evolution is treated like code evolution: versioned, measured, and regression-tested.

## Clarification Eagerness (CE)

CE is one of the most important control knobs in the system.  
It governs how aggressively the pipeline asks clarification before writing to KB.

High CE is useful when:

- bootstrapping a new KB with unknown vocabulary
- preventing early ontology pollution
- prioritizing precision over ingestion speed

Lower CE is useful when:

- ingesting high-volume cleaner text
- accepting more automatic forward progress

In short, CE is the ingestion gate between ambiguity and memory mutation.

## Dual-Model Clarification Q&A

A major internal upgrade is clarification automation with model role separation.  
When clarification is needed, Prethinker can call a second, smarter model dedicated to Q&A responses (for example `gpt-oss:20b`) while the primary parser remains the semparse model (`qwen35-semparse:9b`).

This allows:

- parser model = extraction specialist
- Q&A model = clarification responder

This is especially useful during early KB bootstrapping, where vocabulary and relations are underdefined. High CE can force early disambiguation, helping establish a clean ontology foundation instead of ingesting fuzzy facts.

The system now also stops wasteful clarification loops:

- non-informative answers (like `unknown`) trigger immediate defer
- repeated same Q/A pairs stop early

So ambiguity is surfaced as a first-class unresolved state, not silently forced into bad KB writes.

## Why This Is Interesting

Prethinker is an iterative LLM specialization lab:

- it continuously engineers a model toward deterministic logic extraction
- it uses Prolog as the memory and inference substrate
- it climbs a formal ladder of increasingly difficult tests
- it keeps retuning until the parser survives acid-grade semantic stress

That makes it an unusual bridge between neural language understanding and symbolic correctness: the model interprets meaning, but the runtime guards truth.
