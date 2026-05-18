# Active Research Lanes

Last updated: 2026-05-17

This page is the compact public map of current work. It is not a rolling
session journal. Older lane notes, fixture-specific repair slices, retired
compatibility experiments, and generated reports live in Git history or the
local cold archive.

## Operating Rule

Prethinker's active research asks whether source documents can be compiled into
durable symbolic state, then queried cheaply and safely from the compiled
package.

Current default:

```text
source document
  -> compile into admitted predicates, epistemic state, deterministic ledgers,
     manifests, diagnostics
  -> answer from direct KB surfaces and deterministic ledgers
  -> repair only with fixture-free, replay-tested architecture
```

Do not promote a repair because it helps one fixture, row, answer string, or
dataset label. Promote only when the principle survives unlike probes.

## Live Lanes

| Priority | Lane | Question | Current Surface |
| --- | --- | --- | --- |
| 1 | Compile-surface stability | Can recurring answer-bearing distinctions be emitted as direct admitted surfaces instead of query-time compatibility bridges? | `docs/CURRENT_HARNESS_INSTRUMENT.md`, `docs/COMPILED_KB_ARTIFACT_PACKAGE.md` |
| 2 | Instrument stamp | What does the current direct-surface instrument score across internal and external corpora when measured as a frozen system? | `docs/CURRENT_HARNESS_INSTRUMENT.md`; current scorecards under `tmp` during active runs |
| 3 | Lens vocabulary audit | Do lens terms fire on unlike documents because they are structural, or because they still carry corpus-shaped trigger conditions? | `docs/SEMANTIC_LENS_ROSTER.md`, targeted tests |
| 4 | Transition and scope contracts | Can state transitions, assignment scope, and preservation contracts be normalized deterministically without hiding meaning in ad hoc predicates? | `src/transition_delta_normalizer.py`, focused tests |
| 5 | Dataset transfer | How far does the instrument transfer across RACE, SQuAD, contract, privacy-policy, and other external QA corpora without dataset-specific tuning? | summarized in `docs/CURRENT_HARNESS_INSTRUMENT.md` and current scorecards |
| 6 | Language transfer | Which parts of the harness assume English surface forms, date formats, role verbs, or section conventions? | `docs/BOUNDARY_PROBE_RESEARCH_METHOD.md`, focused language probes |
| 7 | Public face hygiene | Does the repo front door describe the living project without surfacing obsolete plans, generated artifact strata, or misleading history? | `README.md`, `docs/index.html`, `docs/PUBLIC_DOCS_GUIDE.md` |

## Current Architecture Pressure

The direct-surface path is the live instrument: admitted predicates,
deterministic ledgers, predicate contracts, selectors, guards, and query policy.
Retired compatibility adapters are not part of the forward repair path.

The highest-value current pressure is therefore:

- preserve concrete source coordinates as deterministic ledgers;
- compile recurring roles, statuses, quantities, transitions, authority
  envelopes, and source-record distinctions as direct admitted predicates;
- detect when a compile used vague `detail/event` wrappers where concrete
  backbone rows should exist;
- use unlike probes before naming any new surface architecture;
- keep fixture nouns, row IDs, answer strings, and dataset labels out of the
  harness.

## Resource Policy

POWER and OpenRouter are both measurement lanes. Prefer the route that gets
clean evidence fastest:

- use local single-lane runs when LM Studio/POWER is stable and avoids provider
  variance;
- use OpenRouter for parallel cold compiles, external transfer measurements,
  and independent draws;
- default hosted pressure to six lanes or fewer unless provider throughput
  evidence says otherwise;
- tag OpenRouter calls by experiment family, phase, and fixture/corpus so cost
  and speed can be inspected later.

Provider failures are transport evidence, not architecture evidence.

## Freeze Readiness

The project is near, but not permanently in, instrument-freeze mode. Freeze only
when the current repair cycle has stopped changing architecture and the next
question is measurement rather than repair. The 2026-05-17 fixed-compile
native direct-surface restamp measured the internal corpus at 1934/64/162 over
2163 judged rows, exact rate 89.41%, with zero compatibility rows.

Before a full stamp:

1. Commit pending code and current-doc changes.
2. Confirm compatibility adapter delivery is off by default.
3. Run focused direct-surface smoke checks.
4. Decide the exact corpus list and draw count.
5. Journal anomalies as variance during the stamp; do not repair mid-stamp.

## What Stays Off The Front Door

Do not resurface retired lab-automation, publishing, public-benchmarking,
generated report explorer, old compatibility-residue, or dated run-log strata
in public entry points. Git history keeps that material. The current repo
should remain a sharp map of the instrument as it exists now.
