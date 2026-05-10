# Next Phase Engineering Plan

Last updated: 2026-05-08

Prethinker has crossed the first architectural proof line: governed semantic
proposal, deterministic admission, compiled artifacts, row-gated selectors, and
zero unauthorized QA writes are working across the research corpus and the
fresh cold-injected story-world batch.

The next phase is not "add more cleverness." It is to raise the ceiling without
letting the harness explode.

## North Star

The product should feel magical because memory is sharp:

- it notices facts, corrections, ambiguity, provenance, conflict, and missing
  support;
- it exposes what it knows and why;
- it refuses to turn vague language into hidden authority;
- it answers from admitted state rather than model mood.

The engineering discipline is the same as the lens discipline:

```text
language proposes
admission governs
state records
constraints bind
helpers compute
selectors route
families compress
```

The deeper substrate goal is to make the compiled world behave more like a
governed spreadsheet than a bag of facts. Filled cells are admitted state.
Blank cells are not just absence; they are degrees of freedom with types,
constraints, dependencies, and sometimes clarifying questions attached.
Propagation should recompute direct consequences, blocked consequences,
remaining unknowns, and impossible states without laundering model guesses into
durable truth.

## Current Frontier

The 2026-05-07 sealed story-world batch established the live generalization
frontier:

```text
cold baseline: 276 exact / 44 partial / 80 miss over 400
row-gated high-water: 361 exact / 16 partial / 23 miss over 400
exact rate: 90.25%
QA write proposals: 0 in contributing runs
```

The remaining misses are not mostly asking for another broad prompt. They point
to reusable substrates:

- temporal arithmetic and interval/status computation;
- quantity and simple arithmetic over admitted facts;
- group, roster, station, and temporary-role membership at time;
- object custody, provenance, and source-artifact roles;
- row-level activation that selects the right admitted surface without global
  perturbation.

The later 2026-05-08 incoming-six administrative/story batch has now been
exhausted diagnostically:

```text
cold baseline: 186 exact / 16 partial / 38 miss over 240
row-gated high-water: 240 exact / 0 partial / 0 miss over 240
```

That `240 / 0 / 0` result is a proof of reachable surfaces, not a production
claim that one global compiler solves the batch. It was reached by existing
selector work plus narrow residual repair artifacts. The durable pressure now
moves from "can this batch be solved?" to "which row shapes transfer cold?"

New row-shape candidates from that exhaustion pass:

- source lists that include non-human evidence sources such as CCTV;
- `last_confirmed_at` separated from unresolved current status;
- unresolved authority-question answer surfaces with reason, pending counsel,
  and no-determination boundaries;
- rejected-version planning surfaces separated from current applications;
- procedural `event_on_date` anchors for docket-style dates.

## Work Lanes

| Lane | Goal | First Useful Artifact |
| --- | --- | --- |
| Guard abstraction | Stop raw guard count from becoming harness sprawl. Treat guards as family instances with health metrics. | `docs/SELECTOR_GUARD_FAMILY_ROLLUP.md` reports family budget, largest-family share, and unclassified count. |
| Temporal helpers | Move deadline, interval, status-at-time, and business/calendar-day questions from lens guessing into deterministic helper substrates. | A helper pack that improves at least two unlike fixtures without selected-row regression. |
| Arithmetic helpers | Compute counts, totals, differences, thresholds, and rank/order facts from admitted values. | Quantity helper probes on cold-batch misses plus older Oxalis/Meridian-style arithmetic rows. |
| Constraint propagation | Represent known cells, constrained blanks, derived cells, and dependency trails so updates recompute what follows and what remains open. Ordered numeric/date-time domain narrowing is now present in `engine.constraint_propagation`; the next proof should feed it from admitted fixture rows rather than hand-authored specs. | One narrow fixture slice where a correction changes a derived answer while the derived answer remains query-only and support-traced. |
| Roster state | Represent temporary group membership, chaperone/supervisor roles, station assignments, reassignment intervals, and operational-version roster counts. | `school_activity_roster_reconciliation` moved from `21 / 3 / 16` to `40 / 0 / 0` through roster-state helpers, source-section rendering, wrapped-line ledger refresh, and packet metadata support; no new semantic lens or new LLM compile was needed. |
| Row-shape transfer | Prove the incoming-six residual row shapes are not prompt-shaped patches. | Unlike fixtures that cold-test source lists, last-confirmed-at, unresolved authority questions, rejected-version state, and date-event anchors. |
| Provenance transfer | Prove the new evidence/ledger provenance lenses are not one-story inventions. | A second cold or wild fixture where source-artifact provenance rows improve under row gating. |
| NITRO sidecar | Use Ministral for structured draft packets only where validators can reject bad output. | Validated source digest or QA-draft packet, kept out of compile evidence until POWER/35B consumes it. |

## Complexity Budget

Raw guard instances may grow during farming. That is acceptable only while the
families compress them.

Healthy growth:

- family count stays small;
- unclassified guard reasons stay at zero;
- new guards name answer surfaces, not fixture anecdotes;
- repeated patterns become parameterized family instances;
- a new family appears only when an existing family cannot honestly explain the
  semantic reason.

Unhealthy growth:

- every fixture adds bespoke selector branches;
- family count grows linearly with fixture count;
- one family becomes a dumping ground;
- score gains depend on hidden Python knowledge of story facts;
- docs celebrate raw count instead of compression.

## Immediate Sequence

1. Add guard-family health metrics to the rollup so count growth is measured by
   compression, not by raw instance total.
2. Pick one remaining cold-batch miss cluster or one newly discovered row shape
   where transfer can be measured without answer-shaped prompting. The first
   roster bite is
   `roster_state_support`, which recovered Lotte's Day 3 role from admitted
   group atoms while correctly leaving unsupported station/chaperone rows as
   compile gaps. The next roster bite used aggregate roster registry context to
   recover Day 1 attendance count and Station A/B rosters. The Day 3 chaperone
   count then exposed a different admission lesson: day-level aggregate facts
   should use event/context roles, not interval roles, unless the source gives a
   clock range. The full Lantern row-gated selector now reaches
   `40 exact / 0 miss`, turning the next pressure point from Lantern repair to
   transfer. First transfer control is complete: Tournament, Greenhouse, and
   Festival all stayed at their available upper bounds after the Lantern
   selector repairs. That passes safety for the selector boundaries, but not
   positive lens transfer for the broad supervision-count registry. Fresh
   transfer proof now exists on
   `school_activity_roster_reconciliation`: a helper-only replay derived v3
   group membership and ratio-counted adults from admitted source-record and
   role rows, then a section-display companion rendered normalized source
   section atoms into human labels. Together they lifted the same cold compile
   artifact from `21 / 3 / 16` to `30 / 1 / 9`. A deterministic wrapped-line
   ledger refresh plus packet metadata companion then surfaced exact packet
   identifiers, policy identifiers, driver/license/device IDs, physical
   retention location, adult lodging, transport departure, and pending-scan
   status, bringing the fixture to `40 / 0 / 0`. This confirms the roster
   frontier was queryability over durable memory, not another LLM reading pass.
3. Build the smallest helper substrate or vocabulary scaffold that composes
   admitted KB rows only.
4. Replay against the target fixture and at least one unlike regression fixture.
5. Promote only if the helper/scaffold reduces misses or partials without increasing
   selected misses.

First incoming-6 helper proof: `deadline_cascade_docket` q006 showed a compact
query-only substrate win. Lowercase temporal slot labels such as
`originaldeadline` and `dayselapsed` are now repaired to variables before query
execution, and the repaired helper query is carried into temporal joins even if
the standalone helper cannot run without prior bindings. The focused q006 replay
is exact with `0` writes. This is the preferred shape for the helper lane:
small, deterministic, artifact-only, and promoted from a fresh-fixture failure.

Incoming-six exhaustion proof: the final residual repair pass produced a
row-gated `240 / 0 / 0` diagnostic path over the six 2026-05-08 fixtures. Proof
artifact:
`tmp/incoming_6_full40_qa_20260508/batch_exhaustion_proof_20260508.md`.

The magical version of Prethinker will not come from more decoration on the
pegboard. It will come from fewer, sharper semantic surfaces feeding real
state, real helpers, honest admission boundaries, and new fixtures that keep
the instrument honest.
