# Prethinker Explainer

## What This Project Is

Prethinker is a neuro-symbolic workbench for one narrow mission:
turn natural language into deterministic Prolog-operable state.

It is not a chatbot framework.  
It is a semantic parser lab and runtime pipeline.

The parser model's job is to classify intent and propose logic:

- `assert_fact`
- `assert_rule`
- `query`
- `retract`
- `other`

The runtime's job is to validate, apply, and verify those proposals against persistent KB state.

Core principle:

**The LLM proposes. The runtime decides.**

---

## Why Neuro-Symbolic

LLMs are flexible but probabilistic.  
Symbolic runtimes are rigid but auditable.

Prethinker combines both:

- Neural side for language perception and structure extraction
- Symbolic side for deterministic memory mutation and inference

That makes failures inspectable:

- what was parsed
- why it was accepted or rejected
- what changed in KB state
- what validations passed or failed

---

## Pipeline Internals

The main flow lives in `kb_pipeline.py`.

![Pre-thinker Control Plane](docs/assets/prethinker-control-plane-infographic-v2.png)

How to read the diagram:

- User utterances are intercepted by **Pre-thinker first**.
- **Sharp Memory** (deterministic Prolog KB) is the source of truth.
- The served **LLM** and its context are useful but probabilistic.
- Clarification can be sourced from:
  - user Q/A
  - served-LLM Q/A (KB-grounded context)
- For write intents (`assert_fact`, `assert_rule`, `retract`), final user yes/no confirmation gates KB mutation.

1. Route + parse
- Two-pass mode is default:
  - pass 1: classify intent
  - pass 2: extract logic-focused structure
- Deterministic refinement normalizes to schema and clause shape.

2. Validation + repair
- Schema checks
- Prolog shape checks
- route/logic consistency checks
- optional predicate registry + type schema checks
- repair prompt path when malformed

3. Uncertainty + clarification gate
- Every turn carries uncertainty fields (`uncertainty_score`, label, flags).
- Clarification Eagerness (CE) is the ingestion gate:
  - high CE = ask earlier
  - low CE = commit earlier
- CE is effectively a controlled "annoyance dial" for precision vs throughput.

4. Clarification Q&A loop (optional)
- Parser model can hand off clarification answers to a second model.
- Typical split:
  - parser: `qwen35-semparse:9b`
  - clarification responder: `gpt-oss:20b`
- Loop guardrails are in place:
  - stop on repetitive Q/A loops
  - stop on non-informative answers
  - defer unsafe writes instead of forcing bad facts

5. Deterministic apply
- Local vendored Prolog core runtime (`engine/core.py`) handles:
  - fact assertion
  - rule assertion
  - retraction
  - query evaluation
- No sibling repository is required for default operation.

6. Scenario validation
- Deterministic query contracts confirm whether the resulting KB behaves as expected.

7. Provenance + observability
- Every run records:
  - prompt hash and snapshot
  - model/runtime settings
  - turn traces and decision states
  - validation outcomes
  - ontology drift signals

---

## Decision States

Each turn is mapped into operational states:

- `commit`
- `stage_provisionally`
- `ask_clarification`
- `escalate`
- `reject`

This gives a clean workflow layer over raw parser/apply statuses.

---

## Ladder Strategy

Prethinker uses progressive rungs, then acid pressure:

- `stage_01_facts_only`
- `stage_02_rule_ingest`
- `stage_03_transitive_chain`
- acid scenarios (`acid_03`, `acid_04`, `acid_05`, and beyond)

The key improvement is avoiding wasted reruns:

- `scripts/run_ladder.py` supports `--start-rung` and `--end-rung`
- it skips already-passed fresh runs when scenario + prompt + settings match
- it allows targeted reruns instead of replaying the full ladder every cycle

So ladder runs now optimize wallclock while preserving rigor.

---

## Acid Philosophy: Never Let 100% Become Static

A fixed benchmark eventually overfits.

Prethinker treats acid as a moving frontier:

- keep a tiny smoke baseline for sanity
- expand hard rungs over time
- maintain holdout-style scenarios
- keep introducing unseen wording and ontology pressure

Goal:
avoid "stuck at 100%" on stale tests and keep measuring real generalization.

---

## Golden KB Workflow

For faster regression checks:

1. Run a rigorous parse + probe pass
2. Freeze the accepted result as a golden KB artifact
3. Compare future runs directly against that expected KB

This reduces repeated interactive probing during routine tuning loops while preserving deterministic evaluation.

---

## Ontological Tracking and Domain Bounding

The system tracks ontology profiles and diffs per KB namespace.

This helps:

- keep namespaces semantically coherent
- detect drift and unexpected predicate expansion
- require explicit intent before major domain shifts
- constrain parser behavior to the active ontology, not "all possible topics"

In practice, ontological tracking narrows the search space and reduces semantic sprawl.

---

## Runtime Hygiene and Artifact Policy

Persistent knowledge lives in `kb_store/`.

Ephemeral/scratch outputs are routed to `tmp/` (including transient KB namespaces like `sm_*`).

This keeps the repository view clean while retaining full run evidence.

---

## Honest Maturity Snapshot

What is strong now:

- architecture and separation of concerns
- deterministic runtime integration
- clarification gating mechanics
- provenance and reportability
- progressive benchmark discipline

What is still open:

- broader generalization under harder semantics
- continued acid expansion (ambiguity, contradiction, temporal revision, long narrative, unseen domains)
- evidence depth over larger sample volumes

Prethinker is best understood as a serious research workbench, not a finished product.

---

## Autonomous Project Mode

Current workflow is run autonomously by Codex orchestration:

- rung execution
- selective reruns
- prompt iteration support
- report generation
- artifact hygiene

Human guidance sets goals and constraints; Codex runs the operational loop.
