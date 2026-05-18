# Semantic Lens Roster

Last updated: 2026-05-18

This is the current public roster of meaning surfaces Prethinker measures.
Older fixture-by-fixture calibration notes were archived to
`C:\prethinker_tmp_archive\docs_markdown_sweep_20260518` and Git history. This
file should name the architecture, not the story nouns that helped discover it.

## Core Frame

```text
compiled KB = durable state
row = measured encounter with that state
selector = chooses the best encounter surface
guard = prevents a tempting wrong surface
verdict = records what happened
```

Truth lives in the compiled artifact. Rows measure whether that truth is
present, retrievable, and safe to answer from.

## Current Facets

| Facet | What It Measures | Transfer Test |
| --- | --- | --- |
| Source surface | Whether entities, facts, dates, quantities, rules, corrections, exceptions, and statuses were admitted. | The same predicate family appears on unlike documents without fixture names. |
| Operational record/status | Lifecycle, docket, permit, intake, correction, reversal, and status-transition structure. | Repeated dated lifecycle rows bind the object, phase, date, and state. |
| Rule composition | Thresholds, precedence, activation, exceptions, eligibility, overrides, votes, and expiration. | Rules bind their base rule, condition, effect, scope, and controlled outcome. |
| Temporal/status | Status-at-date, interval overlap, deadline arithmetic, effective/expired boundaries, supersession. | Temporal rows preserve point state and interval state without mixing deadline families. |
| Authority | Which source, actor, rule, vote, finding, or correction controls when accounts conflict. | Control is represented by issuer/body/source, content, date, scope, and authority rank. |
| Evidence provenance | Who prepared, presented, dated, admitted, relied on, commissioned, corrected, or located a source artifact. | Provenance rows bind actor, artifact/content, source context, and role. |
| Archival/source ledger | Exact printed source labels, row labels, table cells, exhibit ids, docket ids, field names, identifiers. | Deterministic ledgers preserve exact source coordinates without semantic overclaim. |
| Epistemic uncertainty | Unknown, unstated, pending, disputed, retracted, superseded, unsupported, inferred, resolved-negative, provisional. | The answer can distinguish absence, conflict, negation, and derivation from ordinary missing data. |
| Entity and role | Aliases, titles, identities, memberships, ownership, custody, responsibility, assignment scope. | Role rows bind entity, role, scope, time, and source rather than a bare label. |
| Query surface | Whether query planning asks for the right admitted predicates and deterministic ledgers. | The KB contains the answer but the query must choose the correct join. |
| Selector surface | Whether row-level selection chooses the right evidence mode. | Selector and guards improve rows without reading answers or source prose. |
| Answer surface | Whether the final answer should be direct, qualified, refused, or report insufficient support. | The answer shape follows admitted epistemic state, not model confidence. |
| Struggle detection | Whether additional passes are adding useful unique rows or only churn. | The run stops or changes strategy when contribution collapses. |

## Promotion Rule

A lens term earns a durable slot only when it passes all four checks:

1. It names a fixture-free semantic surface.
2. It has slot contracts strong enough to reject shallow rows.
3. It fires on unlike documents with the same structure.
4. It preserves or improves QA without weakening source fidelity.

Registry scaffolds and palette priors are allowed as research aids. They are
not architecture until they survive transfer and can be described without
fixture nouns, row ids, local people, local organizations, answer strings, or
dataset labels.

## Current Audit Pressure

Recent lens audits have focused on slot contracts rather than adding new lens
names. The recurring lesson is calibration by surface:

- provenance needs actor + artifact/content + source/context;
- rule composition needs relational partners, conditions, effects, and scope;
- authority often needs gradient/rank contracts and may validly remain sparse;
- operational record/status needs lifecycle identity, phase, transition target,
  date, and supersession target;
- epistemic uncertainty needs explicit negative, object-bound unstated, and
  change-event separation.

When a vocabulary term fails on unlike probes, the next step is not to add a
fixture-specific synonym. The next step is to decide whether the term needs a
stronger slot contract, belongs to another facet, or should remain a scar in
history.

## Companion Documents

- [Semantic Instrument](https://github.com/dr3d/prethinker/blob/main/docs/SEMANTIC_INSTRUMENT.md)
- [Selector Guard Family Rollup](https://github.com/dr3d/prethinker/blob/main/docs/SELECTOR_GUARD_FAMILY_ROLLUP.md)
- [Boundary Probe Research Method](https://github.com/dr3d/prethinker/blob/main/docs/BOUNDARY_PROBE_RESEARCH_METHOD.md)
- [Active Research Lanes](https://github.com/dr3d/prethinker/blob/main/docs/ACTIVE_RESEARCH_LANES.md)
