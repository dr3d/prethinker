# Compiled KB Artifact Package

Last updated: 2026-05-25

## The Core Doctrine

After Prethinker compiles a natural-language source, ordinary Q&A should answer
from the compiled artifact package, not by rereading the original source prose.

If query-time answering needs the original utterance or document, the compiler
did not preserve enough meaning yet. That is a compile-surface gap or an
artifact-design gap, not the intended product path.

The source may still be kept for provenance, auditing, or recompilation, but it
is not the answer substrate.

## Product Shape

The durable compile product is best understood as a Prolog knowledge package
plus structured metadata:

```text
compiled_source/
  world.pl          admitted source state
  epistemic.pl      source commitment, claims, corrections, uncertainty
  ledgers.pl        deterministic source addressability and exact fields
  query_policy.json direct-surface policy and selector settings
  manifest.json     compiler/run/schema/lens metadata
  diagnostics.json  skipped/blocked/zombie/coverage notes, not truth
```

This may physically be one Prolog program at first, but the conceptual
separation matters.

The public `prethinker` package now writes this bundle shape during
`Engine.compile_document()`. In the current alpha API, `world.pl` admits source
identity and source-record coordinates, `ledgers.pl` admits deterministic source
addressability, and `diagnostics.json` explicitly marks rich semantic admission
as not yet run. That is a contract step, not a claim that the full research
compiler has been promoted into the package.

## World KB

`world.pl` contains admitted facts and rules about the compiled world:

- entities;
- relationships;
- events;
- statuses;
- quantities;
- dates and deadlines;
- corrections and current values;
- executable rules whose bodies were admitted and verified.

This is the ordinary answer substrate.

## Epistemic KB

`epistemic.pl` contains admitted facts about how the world is known:

- source claim versus established fact;
- witness statement versus authority finding;
- confirmed, denied, pending, unresolved, superseded, corrected;
- hypothetical or counterfactual status;
- contradiction or conflict;
- not-established rows when the source explicitly records absence,
  non-finding, or unresolved status.

The key principle:

```text
Uncertainty must be compiled too.
```

If uncertainty exists only as a model feeling, self-check note, or skipped
diagnostic, it is not durable answer state. If later Q&A should use that
uncertainty, the compiler must admit it as structured epistemic state.

## Ledgers And Query Policy

`ledgers.pl` contains deterministic source-addressability rather than
source-specific semantic inference:

- line numbers, headings, and section labels;
- table rows, table cells, and printed field names;
- exact identifiers, numeric tokens, dates, and timestamps;
- blockquote metadata such as `From`, `To`, `Date`, and `Re`;
- exact text atoms and stable source keys.

Ledgers do not assert source truth. They preserve the printed structure that
lets compile and QA recover the exact source coordinate without asking the model
to remember or paraphrase it.

`query_policy.json` records how Q&A was allowed to answer. The current default
is direct-surface QA: admitted predicates, deterministic ledgers, direct compile
surfaces, selectors, and guards are in-bounds. Retired compatibility adapters
belong only to explicit historical replay.

Direct-surface QA is not model-free. A model may still propose query operations,
evidence plans, reference-answer judgments, or failure classifications. The
policy boundary is that deterministic code controls which compiled surfaces may
be queried, which operations can execute, and whether the row stayed inside the
governed path. See
[QA Instrument](https://github.com/dr3d/prethinker/blob/main/docs/QA_INSTRUMENT.md).

## Manifest

`manifest.json` records reproducibility and instrument state:

- source hash;
- compiler version;
- schema versions;
- model/backend;
- pass/lens roster;
- predicate roster;
- admitted/skipped counts;
- compile health;
- semantic struggle assessment;
- artifact paths.

This is not truth, but it is essential for replay, comparison, and trust.

## Diagnostics

`diagnostics.json` contains research and debugging residue:

- skipped candidates;
- blocked writes;
- unsafe operations;
- projection diagnostics;
- selector traces;
- coverage notes;
- zombie/struggle evidence;
- failure-classification summaries.

Diagnostics are not the answer substrate. They may tell Codex or a human where
the instrument struggled, and they may motivate a new compile pass, but they do
not become answer truth unless recompiled into admitted `world.pl` or
`epistemic.pl` rows.

## Query-Time Behavior

At query time, Prethinker can ask for clarification without the original source
when the question itself is ambiguous relative to the compiled KB:

- multiple plausible entities;
- multiple deadlines or statuses;
- unresolved source conflicts;
- claim versus finding ambiguity;
- insufficient referent binding.

Good query-time responses include:

- answer from admitted world facts;
- answer with epistemic qualification from admitted epistemic facts;
- ask a focused clarification;
- say `not established in the compiled KB`;
- say `the KB records a claim, but no admitted finding`.

Bad query-time behavior:

- reread raw source prose as hidden RAG;
- invent a missing fact from plausible context;
- treat diagnostics as truth;
- ask a vague clarification when the real issue is a missing compiled fact.

## Certainty

Prethinker can eventually expose certainty, but the primary form should be
symbolic before numeric:

- `established`;
- `strongly_supported`;
- `source_claim_only`;
- `conflicted`;
- `pending`;
- `not_established`;
- `ambiguous_reference`;
- `requires_clarification`.

A numeric certainty score can be derived later from support class, source
count, contradiction status, rule path, and provenance type. It should not be a
free-floating LLM percentage.

## Design Summary

Prethinker compiles natural language into durable symbolic state. The useful
"spaghetti" around Prolog becomes organized scaffolding:

- world state;
- epistemic state;
- deterministic ledgers and query policy;
- reproducibility manifest;
- non-truth diagnostics.

The source text is the input. The compiled package is the product.
