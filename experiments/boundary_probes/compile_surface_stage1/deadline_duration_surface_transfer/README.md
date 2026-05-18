# Deadline Duration Surface Transfer

Boundary detail class: `deadline_or_duration_arithmetic`

This probe tests whether elapsed-time, deadline, and timeliness surfaces become
direct queryable coordinates on unlike documents without relying on compatibility
adapters or source-prose rereading.

The fixture-free geometry is:

- a source states a start event and an end/submission/event time;
- a rule or policy states a permitted duration or deadline window;
- questions ask whether the event was timely, how long a violation lasted, or
  how much time elapsed between two anchors;
- direct compile surfaces should expose event timestamps, deadline thresholds,
  and computed/derivable elapsed durations clearly enough for QA;
- no repair may name this probe, its identifiers, or its domains.

## 2026-05-18 replay

Compile artifact:
`tmp/deadline_duration_surface_transfer_compile_20260518/domain_bootstrap_file_20260518T231822441747Z_source_qwen-qwen3-6-35b-a3b.json`

Initial QA replay: `8/0/2`. The misses were not absent timestamp
coordinates. The KB contained the relevant timestamp rows, but query planning
either called `elapsed_minutes/3` with unbound all-row variables or chose a
neighboring event predicate while missing the equivalent source-bound row.

Repairs tested:

- strengthen elapsed-time query strategy to bind start and end timestamps before
  calling runtime arithmetic;
- let source-identifier fallback rows enter the temporal join context;
- when a source-id fallback swaps to a neighboring predicate with the same arity
  and source slot, preserve the original variables so downstream joins can bind
  the requested timestamp.

Post-repair QA replay:
`10/0/0`, failure surfaces `{'not_applicable': 10}`, compatibility rows `0`,
runtime load errors `0`, write proposals `0`.

Lesson: this deadline/duration boundary is an interior coordinate with query
planning and join-context blur. The generic repair is to preserve admitted
timestamp rows and source-bound fallback rows as first-class join support, not
to create domain-specific duration helpers.
