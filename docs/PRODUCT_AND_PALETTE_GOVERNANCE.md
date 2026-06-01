# Product And Palette Governance

Last updated: 2026-05-28

> Status: historical pre-reset governance note. Use
> [Domain Tier Strategy](https://github.com/dr3d/prethinker/blob/main/docs/DOMAIN_TIER_STRATEGY.md)
> and
> [Active Research Lanes](https://github.com/dr3d/prethinker/blob/main/docs/ACTIVE_RESEARCH_LANES.md)
> for current public claim
> posture.

Prethinker has two related governance problems that should be kept together:

- Product state must distinguish durable corpus facts from live session
  assertions.
- Canonical KB vocabulary must be earned through palette contracts, not through
  one-off LLM predicate invention.

The shared rule is simple: preserve observations generously, admit architecture
conservatively.

## Product Shape To Keep

Prethinker has two product modes that should share governance without pretending
to be the same workflow.

### Corpus Mode

Corpus mode compiles bounded source material into durable, inspectable KB
artifacts:

```text
documents
  -> source-address ledgers
  -> intake/profile/bootstrap passes
  -> semantic compile candidates
  -> deterministic admission
  -> compiled KB package
  -> many cheap queries
```

This is the right mode for policies, contracts, archives, case files, research
papers, project histories, and other document sets that will be queried
repeatedly. Corpus mode should preserve separate layers for source-derived
truth, deterministic source records, compiler-admitted facts, query results, and
later user annotations.

### Session Mode

Session mode handles live interaction against a KB:

```text
utterance
  -> semantic workspace
  -> deterministic admission
  -> KB mutation, query, clarification, quarantine, or rejection
```

The hard problem in a young session is predicate choice. A single utterance
usually does not contain enough evidence to choose a stable ontology. Session
ingestion should therefore preserve candidate projections without immediately
promoting them all to durable truth.

The session rule is:

```text
ingest broadly
commit conservatively
resolve lazily
promote only under pressure
```

Resolution pressure can come from a query, a contradiction, repeated turns that
reveal a stable pattern, an explicit user clarification, or a corpus/profile
substrate that already owns the relevant palette.

### Product Bridge

The richest product shape is:

```text
Corpus Mode builds the world.
Session Mode lives inside it.
```

A user can compile a document set first, then interact with the compiled state.
The session can query, annotate, correct, or extend the corpus-derived KB while
preserving the difference between:

- document-stated facts;
- user assertions;
- candidate projections;
- admitted corrections;
- rejected or quarantined proposals;
- query results.

This is what keeps Prethinker from becoming ordinary chat memory. The product
value is governed, inspectable state with delayed ontology commitment.

## Palette Governance To Keep

The current compile path has historically given the LLM too much freedom to
propose predicate names and row shapes. That freedom is useful for discovery,
but dangerous when invented vocabulary becomes query substrate.

The architecture needs a membrane between local observation and canonical KB
state.

The proposed next layer is retrieval-constrained palette grounding:

```text
source span + lens + source type
  -> retrieve top-k compatible palette schemas
  -> constrained selection and slot filling
  -> canonical row or structured residue
```

This is not a vocabulary rewrite. The global palette remains unchanged. The
change is that deterministic retrieval and schema checks bound what the model is
allowed to emit as canonical state.

Canonical rows must satisfy the active palette contract:

- predicate is in the retrieved schema set;
- arity matches the predicate contract;
- required/core slots are present;
- row passes deterministic validation.

Novel observations should go to residue instead of canonical state. Residue
preserves discovery without granting queryable architecture status.

## Why The Two Ideas Belong Together

Corpus mode and session mode both face the same risk: early language can become
architecture too quickly.

In corpus mode, the risk appears as stochastic compile draws inventing or
choosing unstable predicates. In session mode, the risk appears as the first
phrasing of a user utterance hardening into durable ontology.

The same governance answer applies to both:

- keep source text, utterances, and candidate observations;
- admit only validated canonical rows;
- defer unresolved projections until pressure appears;
- make palette expansion explicit and auditable;
- never let local names, row ids, question language, or fixture vocabulary
  become reusable architecture.

## First Experiment To Keep

The retrieval-constrained idea should start audit-only. It should not change
compiler behavior until it earns its place.

Recommended first experiment:

- choose a small native slice with known source-record or palette instability;
- focus on one or two settled surfaces, such as source authority and
  operational record/profile surfaces;
- run top-k retrieval audits at `k=5`, `k=10`, and `k=20`;
- compare retrieved schemas against existing emitted rows and QA failures;
- measure missed schemas, overbroad candidate sets, useful suppressed rows, and
  answer-bearing rows that would have become residue;
- only then try constrained emission.

Success criteria:

- invented predicate count drops sharply;
- wrong-arity rows disappear mechanically;
- QA holds or improves;
- direct backbone rows remain present;
- residue is inspectable rather than a junk drawer;
- repeated compile draws show a more stable predicate palette;
- retrieval has a low missed-schema rate.

### First Audit Result

An initial coordinate-level proxy audit was run on 2026-05-18 against six
unstable native direct-surface fixtures from the then-current stamp-candidate
run. Scope: 49 boundary rows, 948 candidate registry signatures, `k=5/10/20`,
no compiler behavior change.

With the whole global registry, `k=20` was weak:

- exact schema recalled: 18 / 49;
- family recalled but exact schema missed: 11 / 49;
- missed schema: 18 / 49;
- no non-source predicate hint: 2 / 49.

That first result looked poor because the retrieval space was wrong. When the
same audit was scoped to the active fixture/profile candidate palette, `k=20`
recalled the exact hinted schema for 46 / 49 rows without source-gap context.
Adding source-gap evidence recalled 45 / 49 rows. The immediate lesson is that
profile-local palette scoping matters more than simply enlarging top-k or
searching the global registry.

Hard category filtering is not ready. A follow-up audit that restricted
fixture-local retrieval to coarse inferred target categories reduced candidate
spread but also dropped exact recall to 31 / 49 without source-gap context and
36 / 49 with source-gap context at `k=20`. The current category classifier is
too coarse to act as an admission membrane. Category/lens context should remain
a ranking feature until registry metadata and span attachment improve.

The coordinate-level proxy is useful enough to expose the pressure, but not
strong enough to govern canonical row admission by itself. It measures whether
the right schema is recoverable from existing candidate palettes; it does not
yet prove that span-level constrained decoding would preserve QA.

The next experiment should add one of these before constrained emission:

- source-span to candidate-row attachment, so retrieval sees the local source
  evidence instead of only question/rationale text;
- richer registry metadata for sibling predicates, slot criticality, and
  family membership;
- multi-draw palette consensus to stabilize vocabulary before fact admission.

### Mixed-Protocol Stability Finding

A follow-up audit used already-available repeated compile artifacts from the
native direct-surface, surface-promotion, and delivery-diagnostic runs. Because
those roots mix protocol states, the result is not a formal variance band. It
does, however, expose the next governance surface.

Across 165 compile artifacts and 56 fixtures, only 5 fixtures were palette
stable. The audit found 2746 unstable candidate signatures, 159 predicate-arity
drift rows, 2383 signature-delivery drift rows, and 618 candidate zero-yield
signatures.

That finding changes the retrieval-constrained roadmap. The first audit showed
that fixture/profile-local retrieval can usually find the right schema. The
mixed stability audit shows that retrieval alone is not enough: the instrument
also needs to know whether a schema is consistently offered, whether its arity
is stable, and whether offered schemas produce admitted rows.

The next clean experiment should therefore be a same-protocol N=3 audit on a
small fixture set: one known unstable fixture, one recently improved fixture,
and one stable control. The target metric is palette and delivery stability,
not QA score. If the same-protocol audit reproduces the mixed finding, then
multi-draw palette priors or targeted retry become the right response path. If
it does not, the mixed finding remains historical protocol-change evidence.

That same-protocol slice was then run against three already-compiled repeated
draw probes. It reproduced the pressure: 0 of 3 fixtures were palette-stable,
with 121 unstable candidate signatures, 3 predicate-arity drift rows, 118
signature-delivery drift rows, and 18 candidate zero-yield signatures. This is
still a small diagnostic slice, not a corpus stamp, but it is enough to promote
palette/delivery stability from suspicion to active architecture work.

## 2026-05-25 Status

Palette and delivery stability remain live governance concerns, but they are no
longer the release-blocking proof question by themselves. The 2026-05-22 native
restamp reached `1997 exact / 46 partial / 120 miss` over `2163` rows
(`92.33%` exact), while the four-fixture real-world spotcheck reached `160 / 0 /
0` with `4 / 4` compile gates clean. Fresh ugly public 2026-05-28 R1 reached
`197 / 3 / 0` over `200` rows (`98.5%` exact), while Batch 03 latest guarded
slices remain regression evidence at `291 / 6 / 3` over `300` rows (`97.0%`
exact) as a slice-combined current view. That says the current instrument can
generalize despite known palette variance, with the explicit caveat that May 28
still had compile-gate holds and Batch 03 is no longer untouched after mechanism
repair.

The unresolved pressure is more specific: the native compile gate shifted from
`26 / 30` pass/hold in the prior baseline to `9 / 47` under the old overloaded
gate, current tooling now separates blocking/diagnostic/advisory gate reasons,
and query-surface gaps rose from `20` to `29`. Palette governance should now
support that diagnosis: which unstable candidate signatures affect
answer-bearing surfaces, which are only diagnostic noise, and which deserve
profile-local retrieval, multi-draw priors, or direct compile-surface promotion.

The response path should stay audit-first:

- use profile-local retrieval as a candidate-prior, not an admission gate;
- measure whether the retrieved prior reduces palette churn across fresh draws;
- use targeted retry only when a high-value schema is known from the profile
  but missing or zero-yield in the current draw;
- reserve multi-draw consensus for rows that survive schema and slot checks;
- route unstable or novel schemas to residue instead of canonical state.

The first registry-mode calibration on the same three probes supports a soft
prior rather than a hard freeze. Intersection was too thin, union was too broad,
and a majority threshold gave the most plausible vocabulary scaffold:

| Probe type | Intersection | Majority threshold | Union |
| --- | ---: | ---: | ---: |
| sensor/time correction | 2 | 9 | 61 |
| authority/variance | 2 | 10 | 40 |
| narrative machine | 5 | 11 | 29 |

The architectural lesson is not "admit majority rows." The lesson is that
repeated candidate signatures can provide a vocabulary prior for a future draw.
The prior should bias or retry schema selection while still requiring source
support, slot validity, and direct-row delivery before anything becomes
canonical state.

A first causal replay with a majority prior supports the narrow version of that
claim. On a fresh sensor/time compile, all 9 majority-prior signatures were
offered and delivered, and 6 non-prior signatures were still allowed through
normal compiler discovery. The prior behaved like a soft scaffold rather than a
hard cage. QA scored only 30/3/7 over 40 questions, below stronger recent runs
on the same fixture, so the replay does not justify a broad prior rollout. It
does justify the next measurement layer: every palette-prior replay should
report prior-offered, prior-delivered, prior-zero-yield, and non-prior-delivered
signatures separately from QA.

The replay's not-exact rows then ran through the retrieval audit. At `k=10`,
the active 15-signature candidate palette recalled hinted schemas for 9 of 10
boundary rows. That means the candidate palette is often near enough to the
answer even when QA fails. The missing product layer is not only "retrieve the
right vocabulary"; it is "attach source spans to candidate rows, deliver the
answer-bearing rows, and compose the query over them." Retrieval is a membrane,
not the whole wall.

## Design Notes To Preserve

The palette registry will need richer metadata than predicate name and arity:

- family/frame membership;
- profiles or microtheories where the predicate is valid;
- source types;
- slot names and criticality;
- expected argument types;
- sibling and parent predicates;
- positive and negative retrieval cues;
- examples used only as retrieval metadata, not as fixture-shaped doctrine.

Slot criticality should distinguish:

- core slots: absence changes meaning or makes admission unsafe;
- supporting slots: useful for QA, provenance, or disambiguation;
- decorative/context slots: useful detail but not an admission requirement.

Multi-draw consensus remains a later stabilizer, not a replacement for the
single-draw governance layer:

```text
N constrained draws
  -> compare selected schemas and filled slots
  -> admit stable rows
  -> route unstable rows to review, retry, or residue
```

## Guardrail

The goal is not to make the LLM less expressive. The goal is to keep expression
behind an admission membrane. The LLM may still notice novel distinctions, but
canonical KB vocabulary should be earned through registry membership, slot
contracts, transfer evidence, and measurable stability.
