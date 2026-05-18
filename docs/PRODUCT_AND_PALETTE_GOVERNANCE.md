# Product And Palette Governance

Last updated: 2026-05-18

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
unstable native no-helper fixtures from the latest stamp-candidate run. Scope:
49 boundary rows, 948 candidate registry signatures, `k=5/10/20`, no compiler
behavior change.

At `k=20`:

- exact schema recalled: 18 / 49;
- family recalled but exact schema missed: 11 / 49;
- missed schema: 18 / 49;
- no non-source predicate hint: 2 / 49.

Increasing from `k=10` to `k=20` did not improve exact recall. That means the
first retriever is limited by context and metadata, not just by candidate set
size. The coordinate-level proxy is useful enough to expose the pressure, but
not strong enough to govern canonical row admission.

The next experiment should add one of these before constrained emission:

- source-span to candidate-row attachment, so retrieval sees the local source
  evidence instead of only question/rationale text;
- richer registry metadata for sibling predicates, slot criticality, and
  family membership;
- multi-draw palette consensus to stabilize vocabulary before fact admission.

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
