# Freethinker Design

This note captures the near-term design for adding a clarification sidecar to Prethinker without uncaging the main Governed Intent Compiler.

## Summary

Prethinker should remain the strict compiler and the only component allowed to commit KB mutations.

Freethinker should be a separate, quieter helper model that:

- watches conversation and accepted KB state evolve
- receives a bounded context pack
- intervenes only when Prethinker reports ambiguity or requests clarification
- proposes either:
  - a grounded clarification resolution
  - a better user-facing clarification question
  - abstention

Freethinker is a liaison, not an authority.

Current implementation status:

- the canonical console path now has a live bounded Freethinker model call
- default resolution policy is still `off`
- `advisory_only` is the first intended active rollout mode
- Freethinker has separate model/runtime settings, including temperature and think on/off
- advisory mode already improves some generic pronoun clarification holds into named confirmation questions when recent context yields exactly one grounded candidate
- Freethinker still does not write directly to the KB or bypass Prethinker

## Why This Exists

Today the canonical console path is mostly stateless at parse time:

- current utterance
- shared parser prompt
- pass-specific wrapper
- minimal pending clarification carry-forward

This works, but it underuses local discourse context and pushes too much burden onto:

- direct user clarification
- Python-side heuristics
- special-case normalization logic

The repo already contains a related idea in the batch harness: an internal clarification-answer helper that can use KB context, recent turns, and progress memory. That machinery supports autonomous frontier work, but it is not the normal console clarification path.

Freethinker generalizes that idea into a product-shaped sidecar.

## Why Not Just One Bigger-Context Parser?

We explicitly tested the simpler alternative: same `qwen3.5:9b`, more context, richer sidecar fed directly into the strict parser role.

Result:

- the single-path stronger-context parser did not materially improve clarification handling
- the split-role prototype did help on a uniquely grounded reference case
- the split-role prototype also overreached on a truly ambiguous case

So the design takeaway is not "Freethinker should auto-resolve everything."

It is:

- a separate clarification role is probably useful
- it should earn trust in narrow stages
- it should not begin life as a broad write-unblocking agent

Reference:

- [docs/reports/FREETHINKER_ARCHITECTURE_PROBE_2026-04-19.md](/D:/_PROJECTS/prethinker/docs/reports/FREETHINKER_ARCHITECTURE_PROBE_2026-04-19.md)

## Current State

### Canonical Console Path

The console currently routes through `process_utterance()` in [src/mcp_server.py](/D:/_PROJECTS/prethinker/src/mcp_server.py:1845).

Relevant behavior:

- `pre_think()` computes the front-door packet and determines whether clarification is required
- if clarification is required, `process_utterance()` returns that hold to the UI immediately
- if the user supplies a clarification answer, that answer is appended into the effective extraction prompt

Current clarification hold insertion point:

- [src/mcp_server.py](/D:/_PROJECTS/prethinker/src/mcp_server.py:1934)

Current parse carry-forward behavior:

- [src/mcp_server.py](/D:/_PROJECTS/prethinker/src/mcp_server.py:672)

### Existing Sidecar-Like Machinery

The batch harness already has a helper-model clarification path in [kb_pipeline.py](/D:/_PROJECTS/prethinker/kb_pipeline.py:11369).

It builds a bounded context pack from:

- deterministic KB clauses
- recent accepted turns
- progress memory
- prior clarification transcript

Key pieces:

- context pack: [kb_pipeline.py](/D:/_PROJECTS/prethinker/kb_pipeline.py:2400)
- clarification helper prompt: [kb_pipeline.py](/D:/_PROJECTS/prethinker/kb_pipeline.py:2554)
- synthetic/helper answer generation: [kb_pipeline.py](/D:/_PROJECTS/prethinker/kb_pipeline.py:2631)

This is the best existing foundation for Freethinker.

## Core Principles

1. Prethinker remains the source of truth for compilation and commit.
2. Freethinker never writes to the KB directly.
3. Freethinker may resolve reference, but not invent intent.
4. User clarification is still required when ambiguity is meaning-bearing rather than referential.
5. The sidecar must be bounded and auditable.

## Proposed Roles

### Prethinker

- strict semantic compiler
- schema-bound
- deterministic gate before mutation
- may ask for clarification
- may commit accepted KB mutations

### Freethinker

- context-aware observer
- broader short-term working memory
- consulted only when Prethinker hesitates
- may propose:
  - `resolve_from_context`
  - `ask_user_this`
  - `abstain`
- never commits

## Minimal Slipstream Integration

The cleanest insertion point is in `process_utterance()` after `pre_think()` has already decided that clarification is required but before that hold is surfaced to the UI.

Current flow:

1. `pre_think()`
2. if clarification required -> return `clarification_required`
3. else parse + apply

Proposed flow:

1. `pre_think()`
2. if clarification required:
   - build Freethinker context pack
   - ask Freethinker for one bounded attempt
   - if Freethinker returns `resolve_from_context` and policy allows it:
     - feed that answer back through the existing clarification path
     - re-enter parse/compile using Prethinker
   - if Freethinker returns `ask_user_this`:
     - surface that refined question to the UI
   - if Freethinker returns `abstain`:
     - surface the original clarification hold
3. parse + apply remains unchanged

This keeps the live console path stable while adding one bounded step.

## Context Pack

Freethinker should not receive the full raw transcript by default. It should receive a compact sidecar.

Suggested `freethinker_context_v1`:

- `current_utterance`
- `prethink_id`
- `compiler_intent`
- `compiler_uncertainty_score`
- `clarification_question`
- `clarification_reason`
- `current_parse_signals`
- `pending_clarification_transcript`
- `recent_accepted_turns`
- `recent_committed_logic`
- `active_entities`
- `small_kb_snapshot`
- `source_of_truth_note`

Suggested size limits:

- recent turns: last `2-4`
- committed logic preview: last `3-6`
- KB clause budget: `20-40`
- char budget: `2k-4k`

## Resolution Policy Dial

This should be configurable separately from `clarification_eagerness`.

Suggested setting:

- `freethinker_resolution_policy`

Suggested values:

- `off`
  - no sidecar attempt
- `advisory_only`
  - Freethinker may rewrite the question but may not resolve automatically
- `grounded_reference`
  - only resolve uniquely grounded referents and carry-forward subjects
- `conservative_contextual`
  - allow safe local discourse continuation when the intent is unchanged

Current rollout recommendation:

- implementation default: `off`
- first live UI experiment: `advisory_only`
- only after evidence: narrow `grounded_reference`
- autonomous batch lanes should remain on their existing helper-model path until Freethinker earns a cleaner role

## What Freethinker May Resolve

Allowed in principle:

- obvious pronoun/reference carry-over
- active subject continuation from immediately prior accepted turn
- pending clarification continuation
- simple definite-description continuation when uniquely grounded

Not allowed:

- choosing between two plausible entities
- inventing a missing fact
- deciding predicate direction when unresolved
- deciding negation vs retraction
- deciding event vs state flattening
- making time/causality assumptions

Short constitutional form:

- Freethinker may resolve reference.
- Freethinker may not resolve intent.

## Prompt Contract

Freethinker should have its own system prompt, separate from the parser prompt.
This is a requirement, not an optional refinement.

Freethinker should not reuse the main semantic parser prompt pack, because the jobs are different:

- Prethinker is trying to emit one strict schema-valid compiler object.
- Freethinker is trying to understand bounded context, resolve local discourse, and either help or abstain.

Reusing the parser SP would encourage the wrong behavior:

- over-optimization for schema emission
- premature Prolog mapping
- brittle uncertainty behavior tuned for commit safety rather than contextual help
- unnecessary pressure to behave like a second compiler

Freethinker's SP should optimize for:

- grounded discourse tracking
- conservative ambiguity resolution
- abstention when evidence is weak
- short machine-readable answers

Freethinker should explicitly be told:

- you are not the KB authority
- you do not commit mutations
- you do not reinterpret user intent freely
- you may resolve reference when grounding is strong
- you must prefer abstention over speculation

Suggested output schema:

- `action`: `resolve_from_context | ask_user_this | abstain`
- `proposed_answer`
- `proposed_question`
- `confidence`
- `grounding`
- `notes`

Where `grounding` is one of:

- `recent_turn`
- `pending_clarification`
- `kb_clause`
- `multi_source`
- `weak_inference`

If grounding would be `weak_inference`, the preferred action should usually be `abstain` or `ask_user_this`.

## Rollout Strategy

Freethinker should not obsolete the current frontier and regression regimen.

The safe rollout is:

1. `off`
   - current behavior
   - required control lane for A/B comparisons
2. `advisory_only`
   - UI-first
   - Freethinker may improve or replace the clarification wording
   - no automatic write unblocking
3. `grounded_reference`
   - only for very narrow, uniquely grounded referential carry-over
   - only after trace evidence shows it reduces user friction without raising bad commits

This preserves the current highway:

- safety gate
- Blocksworld guarded lane
- narrative frontier packs
- autonomous helper-model clarification in the batch harness

Nothing about Freethinker should silently change those baselines without an explicit experimental lane and a sidecar-off control.

## Safety Boundary

Freethinker should never be the thing that authorizes a write.

Safe pattern:

1. Freethinker proposes a clarification resolution.
2. Prethinker recompiles the current turn using that proposed clarification.
3. Prethinker still decides whether the result is admissible.

That means:

- no direct KB mutation from Freethinker
- no sidecar-only commit path
- no "helpful" write invention

## UI Behavior

The console should remain newbie-friendly.

Default UI behavior:

- if Freethinker resolves safely, the user simply sees a smoother turn with traceable provenance in debug mode
- if Freethinker rewrites the clarification, the user sees the refined question
- if Freethinker abstains, current behavior remains

Debug mode should expose:

- whether Freethinker was consulted
- action chosen
- confidence
- grounding source
- whether the final commit was:
  - direct Prethinker pass
  - Freethinker-assisted clarification
  - user-clarified

## Test Plan

### 1. No-Regression Control Pack

Goal: Freethinker must not alter clean direct parses.

Cases:

- explicit family relations
- clean location statements
- clean query turns
- simple multi-fact writes

Pass condition:

- no change in admitted parse or commit result compared with current console path

### 2. Ambiguity Recovery Pack

Goal: reduce needless user clarification for grounded local discourse.

Cases:

- pronoun carry-over
- repeated active subject
- short follow-up turns like `and he lives in Salem`
- definite descriptions grounded by the previous accepted turn

Pass condition:

- fewer user-facing clarification holds
- no rise in wrong commits

### 3. Safety Pack

Goal: ensure the sidecar does not turn speculation into mutation.

Cases:

- two plausible male referents
- two plausible parents
- unresolved negation vs retraction
- unresolved event vs state
- unresolved time reference

Pass condition:

- Freethinker abstains or rewrites the user question
- no automatic commit

### 4. Traceability Pack

Goal: every Freethinker intervention is visible and attributable.

Required trace fields:

- `freethinker_used`
- `freethinker_action`
- `freethinker_confidence`
- `freethinker_grounding`
- `freethinker_policy`
- `final_resolution_source`

## Recommended Implementation Order

### Phase 1

- doc and schema only
- add `freethinker_resolution_policy` config field
- add trace placeholders

### Phase 2

- implement `FreethinkerAdapter` in the console/runtime layer
- enable `advisory_only`
- no auto-resolution yet

### Phase 3

- enable `grounded_reference`
- allow one bounded auto-resolution attempt
- run ambiguity recovery pack

### Phase 4

- evaluate whether this should also replace or absorb parts of the current batch clarification helper path

## Recommendation

This should not be a large rewrite.

The cleanest way to slipstream it in is:

- doc first
- one new sidecar adapter
- one new policy dial
- one new trace block
- one insertion point in `process_utterance()`

That is enough to test whether Freethinker reduces brittle clarification without weakening Prethinker's authority.
