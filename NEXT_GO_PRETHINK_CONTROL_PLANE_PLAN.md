# NEXT GO: Pre-think Control Plane Plan

Last updated: 2026-04-11
Status: Active, rewritten to match current repo reality.

## Decision

Keep this plan. Do not jettison.

- `prethinker` remains the source of truth for parser + CE policy evolution.
- MCP interposition is still a separate next lane and is not complete yet.
- We keep parser training lane and control-plane lane separate so one does not destabilize the other.

## Reality Check: What Is Already Implemented

These are already present in this repo today:

1. Deterministic KB mutation via local core runtime (`runtime=core`).
2. Uncertainty + clarification policy with tunable clarification eagerness (CE).
3. Multi-round clarification loops (`--max-clarification-rounds`).
4. Optional separate clarification-answer model (for synthetic Q/A during runs), including confidence gating.
5. User confirmation gate for writes (yes/no required before mutation when confirmation is pending).
6. Strong run provenance capture (model, prompt, CE settings, clarification stats, outcomes).
7. Ladder/rung evaluation workflow and reporting.

## Not Implemented Yet (Core Gap)

These are the control-plane goals still pending:

1. Local MCP tool surface for true `/prethink` interposition:
   - `pre_think`
   - `set_pre_think_session`
   - `show_pre_think_state`
   - optional deterministic KB tools (`query_rows`, `assert_fact`, `assert_rule`, `retract_fact`)
2. Host-side slash mapping and fail-closed routing:
   - every turn must pass through pre-think before LLM response
3. Mode routing at interposition boundary:
   - `short_circuit`
   - `forward_with_facts`
   - `block_or_clarify`
4. Egress gating (optional but planned):
   - verify/guard outbound response before final display
5. Explicit source-aware CE broker logging:
   - source tags (`kb`, `llm`, `user`)
   - uncertainty transition trace
   - commit authority basis (`kb_proof|user_confirmed|both`)

## Trust Rule (Must Keep)

If pre-think starts uncertain, served-LLM input can reduce uncertainty but cannot by itself authorize commit certainty.

Write-path commit must be grounded by at least one:

1. deterministic KB disambiguation, or
2. explicit user confirmation.

## Planned Execution (Rebased)

## Phase 0: Contract Freeze

1. Freeze `pre_think` request/response schema in repo docs.
2. Freeze mode decision enum (`short_circuit|forward_with_facts|block_or_clarify`).
3. Freeze source-tag schema for clarification traces.

Acceptance:

- schemas are documented and versioned
- parser lane can continue unchanged while control-plane code is added

## Phase 1: Minimal MCP Interposition Surface

1. Add local MCP server module in this repo (no sibling repo imports).
2. Implement `pre_think`, `set_pre_think_session`, `show_pre_think_state`.
3. Wire to existing `kb_pipeline`/core runtime behavior.

Acceptance:

- tool list/call smoke tests pass
- no dependency on `../prolog-reasoning`

## Phase 2: Router + Fail-Closed Policy

1. Add ingress wrapper with `all_turns_require_prethink=true`.
2. Implement mode routing (`short_circuit|forward_with_facts|block_or_clarify`).
3. Add policy failure behavior (no bypass if pre-think fails).

Acceptance:

- every served turn includes pre-think trace
- deterministic short-circuit works for simple query class

## Phase 3: Source-Aware CE Broker

1. Add ambiguity-class routing:
   - ontology/predicate ambiguity -> `kb` first
   - language-shape ambiguity -> `llm` helper first
   - missing entity/truth value -> `user` first
2. Add source-tagged transcript and uncertainty transition logs.
3. Enforce commit-authority basis field on every write.

Acceptance:

- commit after uncertainty always shows non-LLM authority basis
- repeated clarification loops are detected and safely deferred

## Phase 4: Reporting + Regression Harness

1. Add control-plane scenarios separate from parser ladder scenarios.
2. Report parse quality and control-plane routing quality independently.
3. Publish concise online summary (recent wins + spot checks), keep full archives raw.

Acceptance:

- regressions in interposition behavior are measurable without conflating parser metrics

## Immediate Next Tasks

1. Add `docs/prethink_control_plane_contract.md` with the frozen schemas.
2. Scaffold local MCP server module and stub the three core tools.
3. Add minimal tool dispatch tests.
4. Add one end-to-end demo trace:
   - user turn -> `pre_think` -> selected mode -> final output path

## Done vs Pending Summary

- Keep file: Yes.
- Rewrite file: Done (this document).
- Jettison file: No.

