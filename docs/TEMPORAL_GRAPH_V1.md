# Temporal Graph V1

Last updated: 2026-04-29

## Purpose

`temporal_graph_v1` is an optional proposal block inside `semantic_ir_v1`.
It gives the model a place to represent time as structure before any durable
fact is admitted.

The idea is borrowed from the useful part of temporal-graph reasoning work:

```text
text
  -> structured temporal representation
  -> reasoning over structure
```

Prethinker adds its usual authority boundary:

```text
utterance
  -> semantic_router_v1 context plan
  -> semantic_ir_v1 + optional temporal_graph_v1 proposal
  -> deterministic mapper
  -> admitted KB facts/rules/queries/retracts only from candidate_operations
```

The temporal graph is not truth. It is a diagnostic/proposal workspace.

## Shape

The block is deliberately graph-like:

```json
{
  "schema_version": "temporal_graph_v1",
  "events": [
    {
      "id": "ev1",
      "label": "approval happened",
      "participants": ["iris", "reimbursement_17"],
      "source_status": "direct_assertion",
      "support_ref": "current_utterance"
    }
  ],
  "time_anchors": [
    {
      "id": "t1",
      "value": "2026-02-10",
      "precision": "day",
      "source_status": "direct_assertion",
      "support_ref": "current_utterance"
    }
  ],
  "intervals": [
    {
      "id": "i1",
      "start": "t1",
      "end": "t2",
      "source_status": "claim",
      "support_ref": "witness_statement"
    }
  ],
  "edges": [
    {
      "relation": "before",
      "a": "ev1",
      "b": "ev2",
      "source_status": "direct_assertion",
      "support_ref": "current_utterance"
    }
  ]
}
```

The current edge vocabulary is intentionally small:

```text
before | after | during | overlaps | starts | ends | same_time | supersedes | unknown
```

## Admission Boundary

`temporal_graph_v1` never writes to the KB by itself.

Durable temporal facts still need matching `candidate_operations`, such as:

```json
{
  "operation": "assert",
  "predicate": "event_on",
  "args": ["approval_event", "2026_02_10"],
  "polarity": "positive",
  "source": "direct",
  "safety": "safe"
}
```

The mapper may then admit:

```prolog
event_on(approval_event, 2026_02_10).
```

If the model emits only the temporal graph and no candidate operation, the trace
will show the graph as proposal-only diagnostics, and no durable temporal fact
will be written.

## Why This Helps

Temporal language is where direct fact extraction gets brittle:

- relative dates;
- before/after dependencies;
- effective dates;
- stale date corrections;
- overlapping intervals;
- claim-vs-observation conflicts;
- rules that depend on timing.

The graph gives the model a focused workspace for those structures without
forcing every temporal idea to become an immediate Prolog clause.

That is the design pattern Prethinker keeps returning to:

```text
model does richer understanding
deterministic mapper controls truth
```

## Current Status

Implemented:

- schema support for optional `temporal_graph_v1`;
- prompt/context guidance asking for temporal graph proposals when time/order
  structure matters;
- admission diagnostics that surface event, time-anchor, interval, and edge
  counts plus bounded sample rows;
- tests proving that temporal graphs have no durable KB effect without admitted
  candidate operations.

Next:

- add graph-derived temporal QA probes;
- use graph proposals to improve temporal predicate profile design;
- decide which temporal predicates deserve durable profile contracts;
- expand trace/UI views so humans can inspect temporal graph proposals beside
  candidate operations and mapper decisions.
