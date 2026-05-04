# Proposed Architecture

## Current Observations

The active path has two large centers of gravity:

- `src/mcp_server.py` owns MCP tools, pre-think session state, token gates,
  clarification continuation, compiler calls, Semantic IR calls, context packs,
  parse traces, stored-logic conflict checks, and canonical `process_utterance`.
- `kb_pipeline.py` still owns deterministic `CorePrologRuntime`, parse-only
  runtime, prompt builders, JSON extraction, parse validation, fallback parses,
  many structural guard/rewrite functions, `_apply_to_kb`, progress memory, and
  the legacy scenario CLI.

The replacement should split those responsibilities without changing behavior.

## Modules

`contracts.py`

Defines shared dataclasses and protocols for runtime, compiler, gate, mapper,
normalizer, and apply boundaries. These are deliberately small so production
code can migrate gradually.

`runtime.py`

Owns deterministic runtime operations. The first implementation can wrap the
existing `CorePrologRuntime` and `ParseOnlyRuntime`; the final implementation
can move the code here and leave compatibility imports in `kb_pipeline.py`.

`gate_session.py`

Owns pre-think session state and authorization checks:

- writes require pre-think when session is enabled
- queries require pre-think when `all_turns_require_prethink` is enabled
- query calls with an active `prethink_id` honor clarification and loop guards
- writes require confirmation when configured
- clarification answers clear the pending query gate
- pending authorization stays alive for mixed segment turns

`compiler_client.py`

Owns compiler-facing ports:

- pre-think compile
- parse compile
- Semantic IR compile
- trace payloads

Initial migration can use `LegacyMCPCompilerFacade` around a live
`PrologMCPServer` instance.

`parse_normalization.py`

Owns ordered structural normalizers. The proposed categories are:

- `schema_field_normalizer`
- `relation_orientation_normalizer`
- `retraction_target_normalizer`
- `clarification_policy_normalizer`
- `subject_anchor_normalizer`
- `entity_type_normalizer`
- `story_world_observation_normalizer`
- `group_event_normalizer`
- `explicit_rule_normalizer`
- `query_shape_normalizer`
- `registry_schema_normalizer`
- `temporal_namespace_normalizer`
- `narrative_fact_normalizer`
- `narrative_rule_normalizer`
- `profile_parse_guard`

Names are general; legacy fixture names are tracked only in the migration
matrix so behavior can be ported without keeping old naming.

`semantic_mapper.py`

Owns the Semantic IR boundary. It may call the active mapper during migration,
but the boundary is explicit:

- model/router context is advisory
- allowed predicates and contracts are admission inputs
- mapper diagnostics decide `commit`, `query`, `mixed`, `clarify`,
  `quarantine`, or rejection projection into legacy parse

`apply_engine.py`

Owns deterministic apply sequencing:

- correction retracts before writes
- stored-logic conflict guard before fact assertion
- assert fact/rule batches
- retract target expansion
- query execution
- temporal dual-write and registry/type constraints for legacy scenario runs

`mcp_tools.py`

Owns the public tool surface and the orchestration seam for `process_utterance`.
`src/mcp_server.py` should eventually become mostly construction, transport,
serialization, and delegation.

`scenario_cli.py`

Keeps legacy scenario/batch functionality separate from runtime and MCP code.

## Trace Contract

The trace should keep these stable fields:

- `compiler_trace.prethink`
- `compiler_trace.parse`
- `compiler_trace.summary.overall`
- `compiler_trace.summary.prethink_source`
- `compiler_trace.summary.parse_rescues`
- parse `validation_errors`
- parse `rescues[*].name`, `applied`, `summary`
- Semantic IR trace under parse or compiler trace when enabled

Normalizers should emit event names that are stable and general. If a legacy
event name is required by tests, expose it through a compatibility alias in the
trace adapter, not as the new internal function name.

## Doctrine

The Python layer should remain structural:

- OK: rewrite `at_step(foo, bar).` to `at(foo, bar).` based on predicate shape,
  arity, registry policy, and term parsing.
- OK: reject `parent(alice, flu).` using a type schema.
- OK: map `semantic_ir_v1.candidate_operations` to clauses using allowed
  predicates and contracts.
- Not OK: infer the intended relation from arbitrary English inside a Python
  normalizer.

