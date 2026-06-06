# Overlay Architecture

Date: 2026-05-28

Prethinker's core instrument compiles documents into governed evidence and
state. Overlays are separate analytical lenses that read that substrate and
produce reviewable reports. They do not mutate the compiled KB.

```text
source documents
  -> compiled evidence/state package
  -> governed QA and trace surfaces
  -> optional overlays
       -> ACH matrix
       -> timeline
       -> contradiction map
       -> obligation tracker
       -> coverage report
```

## Boundary

Overlays may:

- read compiled typed evidence, source coordinates, claims, dates, quantities,
  statuses, authorities, and diagnostics;
- ask an LLM to propose report-only judgments under an explicit schema;
- run deterministic scoring, ranking, grouping, or visualization over those
  proposed judgments;
- emit JSON, Markdown, UI reports, and audit bundles.

Overlays may not:

- write durable KB facts;
- alter compile artifacts;
- mutate QA verdicts;
- create compatibility shortcuts for core queries;
- parse source-record/display prose as the evidence route;
- use fixture labels, answer strings, row ids, or source nouns as hidden
  architecture;
- turn an overlay ranking into truth without an explicit governed admission
  process.

The core rule is:

```text
overlays read evidence and emit reports;
they do not silently change the world model
```

## Current Overlays

ACH is the first serious overlay pattern.

Current shape:

```text
ACH payload
  -> hypotheses + evidence rows
  -> LLM proposes evidence x hypothesis judgments
  -> deterministic scorer ranks by least disconfirmation
  -> report names matrix completeness, warnings, sensitivity, support
```

The ACH proposer is allowed to propose judgments, dependency rows, omission
effects, and optional evidence-role diagnostics. The deterministic scorer makes
the ranking and sensitivity report. Neither path writes KB facts or changes QA
metrics.

Current read:

- ACH is research-plausible as a deterministic overlay, but not a solved
  competing-hypotheses claim;
- the existing real-document probes mostly collapse to one survivor and zero
  sensitivity rows, so they are arithmetic sanity checks rather than validation
  of pivotal-evidence intelligence;
- low-sensitivity controls have behaved in recent stress work, and
  high-sensitivity pivotal evidence is promising on the current stress sets;
- medium sensitivity has a deterministic family-level mechanism, but that
  success is still same-batch rescore evidence and needs a fresh heldout before
  it becomes a claim-bearing result;
- evidence-role diagnostics are useful but remain optional because they can
  compete with dependency capture.

The timeline overlay is the second, deliberately cheaper pattern check.

Current shape:

```text
timeline payload
  -> explicit event rows with source coordinates and dates
  -> deterministic chronology ordering
  -> report names undated events, invalid dates, same-date groups, and gaps
```

The first timeline probe is intentionally model-free. It validates that a
second overlay can follow the same boundary: explicit evidence rows in,
deterministic report out, no KB mutation and no QA score movement.

Current read:

- useful as a low-cost research lens for official documents with deadlines,
  notices, effective dates, response windows, and status changes;
- not yet integrated with compiled date/event predicates;
- no claim yet that Prethinker automatically builds timeline payloads.

## Why This Pattern Matters

The overlay pattern lets Prethinker test specialized review surfaces without
stuffing every reasoning mode into the compiler. The compiler's job is
preservation and admission. Overlays can then make specialized review modes
legible to people who already work with evidence matrices, timelines, coverage
gaps, contradictions, obligations, and source confidence.

This keeps any future-facing story broad while keeping the instrument narrow:

```text
compile messy official documents into auditable evidence;
apply explicit review lenses without corrupting the evidence layer
```

## Candidate Overlays

ACH / evidence matrix:

- compare competing hypotheses;
- rank by least disconfirmation;
- expose sensitivity and pivotal evidence limits.

Timeline:

- order events, deadlines, notice dates, effective dates, and status changes;
- identify gaps, conflicts, and ambiguous temporal joins.

Contradiction map:

- group claims that cannot all be true;
- separate source conflict from query/rendering failure;
- preserve provenance for each side.

Obligation tracker:

- list duties, exceptions, deadlines, responsible parties, and required
  responses;
- distinguish source-stated duties from inferred consequences.

Coverage report:

- show which question families are well supported by compiled evidence;
- separate compile absence from query/join failure;
- name low-confidence or missing source surfaces.

## Promotion Discipline

An overlay earns product status only when:

1. its input contract is explicit and source-grounded;
2. its LLM role, if any, is proposal-only;
3. deterministic code performs the report-critical scoring or accounting;
4. artifacts expose warnings, missing cells, and uncertainty;
5. results transfer to unlike fresh documents;
6. failures are labeled as overlay failures, not hidden as QA misses or compile
   wins.

If an overlay discovers a fact that should become durable KB state, that is a
separate design decision. The path must go through governed admission, not a
backchannel from the overlay report.
