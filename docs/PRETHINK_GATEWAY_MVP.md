# Prethinker Console

This note documents the current UI/front-door shape for Prethinker.

It is both:

- a practical manual test cockpit for the real interactive GIC path
- the early product embodiment of Prethinker as a governed adapter in front of conversational AI

## What The Console Is For

The console is where a human should be able to:

- type ordinary language
- see what Prethinker thinks the turn means
- see whether it committed, queried, or blocked
- inspect the symbolic ledger when desired

It is not meant to be a fake demo shell with its own parallel semantics.

The design goal is:

- same core interactive entry path
- friendlier UI
- optional debug visibility

## Canonical Entry Path

The console should be understood as a presentation layer over the canonical interactive entryway:

- [src/mcp_server.py](https://github.com/dr3d/prethinker/blob/main/src/mcp_server.py) `process_utterance()`

That means the console is supposed to be a truthful way to test Prethinker itself, not "something close enough."

## Product Direction

The larger product vision is that this UI, or a future descendant of it, can become the adapter layer in front of a user's chatbot of choice.

In that shape:

- the chatbot remains the fluent conversational surface
- Prethinker watches the interaction stream
- durable facts, rules, and queries are compiled into symbolic memory
- the user gets an inspectable ledger instead of hidden state drift

So the console is not just a developer toy.

It is the first place where the product behavior becomes legible.

## Current Shape

- browser UI served from `ui_gateway/static`
- local stdlib HTTP server in `ui_gateway/gateway/server.py`
- `POST /api/prethink` returns a phaseful envelope:
  - `ingest`
  - `workspace`
  - `admission`
  - `clarify`
  - `commit`
  - `answer`
- config persisted in `ui_gateway/state/gateway_config.json`
- runtime path uses the canonical `process_utterance()` server entryway plus deterministic core tool execution
- the live dials surface can now expose bounded runtime profiles such as `medical@v0`, not just raw model/backend settings
- the console now has a profile-aware prompt-book rail for repeatable demos that pair a setup move, an utterance, and the expected reasoning behavior to watch
- the semantic IR path can be enabled to show richer model workspace proposals before deterministic mapper/admission policy decides what survives
- long story-like utterances can be processed as multiple focused Semantic IR segments, then shown as one deduped console turn with segment-level trace data
- long or mixed utterances can split at query boundaries so a question does not share one semantic workspace with surrounding write facts

## Newbie-Friendly Surface

The console should feel usable to tire-kickers before they know anything about the runtime internals.

Current UI direction:

- plain-language onboarding copy
- empty-state example prompts
- clear turn outcome cards
- pending-clarification banner
- friendly default view with internals hidden

## Debug Mode

The console now also supports a debug-oriented experience.

By default, internals stay mostly hidden.

When `Debug details` is enabled, the user can inspect:

- compiler trace summary
- semantic workspace proposal
- model input compact view
- structured JSON
- segmented story records when applicable
- raw/normalized/admitted path
- ambiguity rows
- phase cards
- mutation details

This is important because the same UI needs to serve two audiences:

- newcomers evaluating the product shape
- us, when we need to see whether success came from the raw model, wrapper discipline, or runtime rescue logic

## Default Binding Choices

- semantic IR research/default console model: `qwen/qwen3.6-35b-a3b` via LM Studio/OpenAI-compatible structured output
- compiler mode: `semantic_ir_v1`
- semantic IR backend: `lmstudio`
- semantic IR base URL: `http://127.0.0.1:1234`
- served handoff mode in strict mode: `never`
- retired clarification experiment: removed from the mainline; current clarification pressure should come through router/compiler context and mapper projection

## Long Narrative Ingestion

The console now has a special path for long story-like utterances. Instead of
asking the model for one giant summary-shaped workspace, the gateway splits the
text into line/sentence segments and sends each segment through the canonical
runtime path.

This is deliberately a harness/framework choice, not a story-specific parser:

- each segment still uses `semantic_ir_v1`;
- each segment still goes through mapper admission and deterministic tools;
- placeholder actors such as `unknown_agent` are blocked from durable writes;
- admitted operations are deduped before the UI displays the final ledger.

The first useful smoke target is the repo's Goldilocks roundtrip story. The
latest local run produced `56` deduped mutations across `50` segments in about
`180s`, with the earlier bad artifacts (`unknown_agent`, voice-as-`carries`,
nonsensical `inside(...)` writes, stray body-part facts) removed.

## Query Boundary Segmentation

Queries are also natural segmentation points. In a mixed utterance such as:

```text
Mara owns the lease. Oskar manages the unit. Who owns the lease?
Also remember that Theo signed the addendum.
```

the gateway now prefers focused segments:

```text
Mara owns the lease.
Oskar manages the unit.
Who owns the lease?
Also remember that Theo signed the addendum.
```

This keeps asserted facts, query targets, and later write instructions from
collapsing into one overlarge workspace. The rule is structural and domain
neutral: split where the turn mode changes, then let each segment go through
normal Semantic IR admission.

## Retired Clarification Experiment

The experimental clarification helper has been removed from the active UI,
gateway config, and server trace surface. Old comparisons remain available in
git history, but normal console work now uses the primary Semantic IR pass with
recent context, profile context, predicate contracts, and KB seed context.

## Deliberate Limits

This is still an MVP.

What it does not claim yet:

- auth
- durable multi-user persistence
- production streaming UX
- a fully polished handoff into arbitrary external chatbots
- broad field robustness across every language style

## Why This Matters

The console is where the project stops being only a backend experiment.

If the UI can show:

- what was understood
- what was committed
- what was blocked
- what clarification is needed

in a way that feels honest rather than magical, then Prethinker starts to become a real product surface instead of only a tuning harness.
