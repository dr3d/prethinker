# Domain Tier Strategy

Status: working strategy, June 1, 2026. This document reframes the next phase
of Prethinker work after the sign-clean reset. It is not a lab notebook; record
experiment results in worksheets.

## Position

The open general compiler remains valuable, but it is not the first sellable
shape. The current clean floor says the general layer is a research compiler and
fallback tier, not yet the product core.

Current 8-fixture English batch, measured from existing artifacts with
`audit_hard_road_floor.py` and model-redacted rejudge:

```text
Product exact:                  88 / 200 = 44.0%
Typed-plan exact:               84 / 200 = 42.0%
Redaction-survived exact:       81 / 200 = 40.5%
Atom-shape-clean product exact: 84 / 200 = 42.0%
Hard-clean floor:               73 / 200 = 36.5%
```

That number is not a failure of the whole idea. It is evidence that open
predicate invention is too unstable to be the product surface. The compiler can
find dates, identifiers, rosters, and some typed relations, but high-value
propositional content such as obligations, findings, dispositions, relief,
procedural consequences, and legal grounds still tends to fall into prose
carriers, prose-shaped atoms, or run-specific predicate families.

The next product-shaped path is a domain schema: pick one document type, define
the carrier language in advance, compile into that language, and let the
hard-clean gate decide which answers earn verified status.

This is a hypothesis, not a foregone conclusion. The bet is that content that is
irreducible across all documents becomes reducible inside one recurring document
type because the document type has stable propositional anatomy. The next
measurements may show no wedge is close enough. That would be a valid and
important answer, not a failed experiment to paper over.

## Tier Ladder

Prethinker should assign every answer a trust tier. The tier must be visible to
the user and must be computed by gates, not by product copy.

```text
Tier 1  Domain schema verified   hard-clean answer over closed domain predicates
Tier 2  General typed fallback   typed-plan replayable answer outside domain schema
Tier 3  Retrieved / RAG assist   source-retrieved best effort, verify before use
Tier 0  Abstain                  outside scope or unsupported
```

Default behavior for a domain product should be Tier 1 or Tier 0. Lower tiers
are opt-in fallbacks, not silent degradation. Tier 2 is still gated; it is not a
dumping ground for ungated best effort.

## Domain Schema

A domain schema is not a helper stack. It is a governed predicate pack for one
document type or tightly bounded document family.

The schema includes:

- closed carrier names;
- fixed argument roles;
- permitted value shapes;
- source-coordinate and provenance requirements;
- omission/accountability behavior;
- query plans that operate over emitted domain atoms;
- hard-clean promotion criteria.

The model's compile job becomes "map this source into this known carrier set,"
not "invent a useful ontology." That is a narrower and more reproducible task.

Within a domain, predicate offering should also be lens-scoped:

```text
offered_predicates = f(domain_registry, lens)
```

The wrapper lens, violation lens, response/obligation lens, and conclusion lens
should not all receive the same writable predicate set. A lens may focus
attention, but it should only emit its assigned subset of the domain registry.
This keeps semantic lenses useful without turning them into a new path for
uncontrolled ontology growth.

The main design test is whether domain predicates cover substance, not only
scaffolding. A schema that verifies identifiers and dates but leaves findings
and obligations in Tier 3 is not enough.

The repeatable process for building and customizing a domain predicate pack is
documented in
[Domain Predicate Schema Process](https://github.com/dr3d/prethinker/blob/main/docs/DOMAIN_PREDICATE_SCHEMA_PROCESS.md).

## RAG Policy

RAG can coexist with the domain schema, but only as a tiered component.

Allowed uses:

- Source locator: retrieval can help select source regions for compile or user
  inspection, provided the locator influence is recorded and Tier 1 still
  depends only on governed typed facts that independently survive hard-clean
  replay.
- Fallback answer: retrieval can produce a Tier 3 "verify this" answer when the
  domain schema cannot support Tier 1.
- Analyst assist: retrieval can show surrounding source context for a verified
  answer without becoming the reason the answer is verified.

Disallowed uses:

- Hidden booster: retrieval cannot help an answer pass as Tier 1 unless the
  result also compiles into governed typed atoms and survives hard-clean replay.
- Blended output: a response cannot mix verified and retrieved support without
  labeling the tier of each claim.
- Prose laundering: source chunks cannot be stuffed into typed atom names or
  value slots to pass a derivation gate.

RAG is a coverage extender. The differentiator remains knowing which claims are
verified and which are merely retrieved.

## Answer Judging Governance

Answer judging was a previous cheat surface and remains a permanent governance
surface.

The reference judge may see a human reference answer because it is a scorer, not
a query path. But the judge cannot be the primary proof that a row is clean.
Tier assignment must require independent gates:

- product judge verdict;
- typed-plan replay over non-prose atoms;
- redaction replay or redacted rejudge;
- atom-shape cleanliness for returned claim-path evidence;
- oracle/reference isolation from compile and query planning;
- null controls against the judge.

The judge must not:

- write facts;
- alter the compiled KB;
- promote a row to Tier 1 by itself;
- accept empty evidence as exact;
- accept wrong-reference evidence as exact;
- treat source-record display text as verified typed derivation.

Current null-control harness:

```text
scripts/audit_reference_judge_null_controls.py
```

The harness samples product-exact rows and rejudges two adversarial variants:

- true reference with empty evidence;
- redacted typed evidence with a wrong reference answer from the same fixture.

Any exact verdict in either control blocks score confidence. Larger samples
should be run before any public or product claim.

## What Survives

The recent row-level work was not wasted, but it should be separated into keep,
partial-keep, and sunk categories.

Keep as domain-independent machinery:

- carrier contract registry;
- atom reducers and atom-shape audit;
- sign-clean audit;
- redaction replay and redacted rejudge;
- typed-plan replay;
- hard-road floor audit;
- provider/model metadata discipline;
- query grounding in emitted atom inventory;
- omission/accountability ledger concept.

Keep selectively as legal/regulatory substrate:

- document identifiers;
- document dates;
- party and role carriers;
- legal citation detail;
- monetary payment and relief carriers;
- obligation/procedural detail carriers;
- document action, outcome, and disposition carriers.

Treat as sunk or research-only:

- source-record helper stacks;
- row-specific repair tricks;
- free-text support surfaces;
- broad open-vocabulary predicate invention;
- mechanisms that only helped a known fixture and did not survive redaction,
  typed replay, unlike-document pressure, and N-cycle stability.

## Operating Loop

Immediate work should move from row-chasing to a stable measurement and design
loop.

1. Produce a per-answer-class hard-clean table from current artifacts.
2. Decide which answer classes are scaffolding and which are substantive.
3. Pick one wedge document type where substantive domain predicates are
   plausible.
4. Sketch the closed domain carrier set for that wedge.
5. Define Tier 1 assignment rules before running the domain compile.
6. Run compile and QA under the same hard-clean gates, and record a before/after
   hard-clean table for the domain pack.
7. Use omission/accountability to explain unsupported answer classes.
8. Only then consider Tier 3 retrieval for remaining coverage.

The first wedge should be selected by evidence, not taste. Candidate families:

- regulatory warning letters;
- settlements and consent orders;
- public utility or agency orders;
- securities material-event filings.

Selection criteria:

- repeated document anatomy;
- high-value questions are known;
- propositional content can be represented by closed carriers;
- enough existing carriers transfer without row-specific behavior;
- hard-clean table shows the general layer is close enough to make the wedge
  worth attempting.

Reject criteria are just as important:

- no substantive answer class has a plausible hard-clean path;
- domain predicates proliferate per row instead of covering repeated anatomy;
- N>=3 same-condition compiles cannot reproduce the same carrier coverage with
  support>=2 for promoted rows;
- gains move rows into prose-shaped names or slots;
- Tier 1 improvement requires hidden RAG or source-window support.

## Boundary Rules

- A domain predicate pack narrows the target; it is not a universal ontology.
- A carrier that works for one document type does not automatically graduate to
  another.
- Out-of-domain content abstains or drops tier; it is not forced into Tier 1.
- Gates apply to the returned claim path, not every unused atom in the KB.
- A product score and a thesis score are both printed; the thesis score is the
  claim-bearing number.
- No public claim is made from a metric the model can influence after seeing the
  answer.

## Next Decisions

The next concrete artifact is the per-answer-class hard-clean table. It should
answer:

- Which answer classes are already Tier-1-like?
- Which fail because compile lacks typed facts?
- Which fail because query planning misses available atoms?
- Which fail because the atom is prose-shaped?
- Which fail because the answer judge is too generous or too strict?
- Which document type has the best concentration of closeable substantive rows?

Only after that table should the first domain schema be designed.

Any domain-schema build must then answer its own before/after question:

```text
general hard-clean on wedge rows
domain-pack hard-clean on the same rows
domain-pack hard-clean on N>=3 same-condition compiles, promoting only rows
  that survive in at least 2 runs
domain-pack hard-clean on an unlike document of the same type
```

If those numbers do not improve reproducibly, the domain schema is not yet a
Tier 1 product lane.

Tier edge case: a domain-schema answer that passes typed replay and redaction
but fails atom-shape does not drop to Tier 2 as a trusted typed answer. It is not
claim-clean. It must abstain by default or be shown only as an explicitly
lower-tier review item, because the failure mode is prose hiding inside typed
language.
