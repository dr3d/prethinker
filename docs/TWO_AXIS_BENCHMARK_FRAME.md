# Two-Axis Benchmark Frame

Last updated: 2026-05-09

Status: strategic research direction, not a settled methodology.

Read with:

- [Two-Axis Probe Discipline](https://github.com/dr3d/prethinker/blob/main/docs/TWO_AXIS_PROBE_DISCIPLINE.md)
- [Edge Governance Positioning](https://github.com/dr3d/prethinker/blob/main/docs/EDGE_GOVERNANCE_POSITIONING.md)

## Short Version

The first frontier-model benchmark pilot weakened the simple story that
"Prethinker dominates frontier LLMs on hard documents." Frontier direct scores
were high on the pilot set, especially for `anthropic/claude-opus-4.7` and
`openai/gpt-5.5`.

That does not weaken the project. It clarifies the measurement problem.

Prethinker should be evaluated along two different axes:

1. **What gets through the door**: compile-time fidelity.
2. **What stays in the room**: retention durability under context pressure.

The first pilot measured single-document direct answer quality. That is only
**Axis-1-adjacent**: one document, one question, no competing source state, and
all attention available for the target. True Axis 1 asks whether an architecture
preserves the document's structural commitments during reading. That may
surface as answer accuracy, but it may also surface as consistency under
perturbation, provenance accuracy, source attribution, refusal calibration, and
preservation of distinctions that are not immediately queried.

The current Prethinker precision-batch OpenRouter result is:

- cold compile: `148/240`
- current best no-oracle selector: `204/240`
- available row-gated ceiling: `221/240`

The ceiling is diagnostic only. The operating number is the selector result.

The next benchmark horizon is not just "can Prethinker beat frontier models on
single-document direct QA?" It is:

```text
Which architecture preserves meaning at ingest,
and which architecture retains meaning under load?
```

The phrase worth keeping is **meaning-depth resolution**:

```text
how finely a system can distinguish structurally different meanings from each other
```

A system that separates `claim` from `finding` but collapses `withdrawn claim`,
`disputed claim`, and `unadopted claim` has lower meaning-depth resolution than
a system that preserves all four states.

## Axis 1: What Gets Through The Door

Axis 1 measures meaning that survives the act of reading.

This is the axis Prethinker has been measuring through the fixture program:

- source envelopes
- epistemic state
- authority distinctions
- supersession chains
- composition vs cardinality
- rule activation with exceptions
- exact identifier preservation
- source-record addressability

When a frontier LLM reads a document, it can answer many questions fluently
without preserving the document's governing structure as durable state. A
witness claim can become a fact. A draft can become policy. A correction can
replace its target while erasing the original speech act.

Prethinker's architectural commitment is different:

```text
language proposes
admission governs
state records
queries inspect
verdicts measure
```

Axis 1 asks whether the right structure enters governed state in the first
place.

Single-document direct QA is not the full Axis 1 measurement. It is the
single-document answer surface under optimal attention conditions. Frontier
models are expected to be strong there. A fuller Axis 1 test asks whether the
same structural commitment survives paraphrased questions, paired contrast
questions, source-attribution probes, and perturbations that should not change
the answer.

## Axis 2: What Stays In The Room

Axis 2 measures meaning that persists under load.

This is not what the fixture program has measured so far. It asks what systems
lose when context fills up, documents interfere, target position changes, or
many questions are asked after intervening material.

Known long-context pressures include:

- content lost in the middle
- recency bias
- cross-document interference
- context degradation before the nominal context limit
- meta-recall failure, where a model loses track of which documents it has

Prethinker should have a structural advantage here because compiled documents
are not retained as tokens in the prompt. They are admitted into state files and
queried later.

That claim still needs measurement. The careful version is:

**Prethinker should not exhibit token-context decay after compilation; the
empirical work is to verify any second-order effects from large KB collections,
multi-KB runtime loading, selector behavior, and helper computation.**

For Axis 2, the unit of experimental design changes. The fixture remains a
building block, but the primary object is the **assembly recipe**:

```text
target fixture
  + filler fixtures
  + ordering
  + position
  + filler length
  + question sequence
  + optional meta-recall prompt
```

A single fixture can participate in many Axis 2 experiments depending on how it
is assembled with other material. Existing fixtures become more valuable, not
less: they are ingredients for controlled interference recipes.

## The Hypothesis Map

```text
                         Gets in properly
                               ^
                               |
                         Prethinker
                               |
Doesn't stay <-----------------+-----------------> Stays persistently
                               |
                        Frontier LLMs
                               |
                               v
                         Gets flattened
```

This diagram is a hypothesis map, not a victory lap.

The useful question is not where a system sits forever. The useful question is
which axis each architecture can improve, and by what mechanism.

## Candidate Experiments

These are future experiments, not a committed methodology.

1. **Single-document baseline**: run each fixture alone through frontier direct
   QA and Prethinker.
2. **Stuffed-context regression**: place one target fixture inside a larger
   prompt containing several other fixtures and ask the same target questions.
3. **Position sensitivity**: place the same target fixture first, middle, and
   last.
4. **Long-context dilution**: add irrelevant but realistic filler at controlled
   lengths.
5. **Cross-document interference**: combine documents with similar identifiers,
   overlapping roles, or similar authority structures.
6. **Meta-recall**: ask the model to name or summarize the source documents it
   has before target QA begins.
7. **Per-category decay**: stratify errors by identifiers, counts,
   authority/role mappings, temporal intervals, source attribution, unresolved
   status, and rule activation.

Change exactly one thing at a time where possible: prompt context assembly. Use
the same model, same questions, same oracle, same scorer, same judge model, same
scoring categories, and same retry policy. Otherwise the comparison cannot
isolate context pressure.

## Assembly Recipe Artifacts

An Axis 2 result should always store the recipe that produced it:

- target fixture
- filler fixture list
- order and target position
- total prompt token estimate
- source section boundaries
- question sequence
- whether a meta-recall prompt was asked
- model id and run settings
- scorer/judge id
- standalone baseline artifact
- stuffed-context artifact

Without the recipe, an Axis 2 result is not reproducible. With the recipe, each
context assembly becomes a reusable experimental object.

## What We Do Not Know Yet

The existing Prethinker vocabulary may or may not transfer to Axis 2.

Possibilities:

- Existing lens/guard categories predict long-context decay well.
- They partly predict it, but position and token-form effects dominate.
- They do not predict it, and Axis 2 needs its own taxonomy.
- A new mixed vocabulary emerges: identifier fragility, first-mention effects,
  table-structure fragility, source-attribution decay, and cross-document
  interference.

Any of these outcomes is useful. The data should decide.

## Coordination Boundary

The benchmark lane owns frontier direct experiments and publication-grade
benchmark artifacts.

The architecture lane owns Prethinker compile, selector, helper, lens, guard,
and deterministic pre-compile ledger work.

The two lanes should exchange findings, not silently merge claims.

Useful shared artifacts:

- frontier rows that beat Prethinker
- Prethinker rows that beat frontier models
- rows where both fail
- category-specific weakness maps
- leakage notes and fixture-quality flags
- assembly recipes for Axis 2 probes

Do not compare Prethinker's diagnostic ceiling against a frontier model's
operating score as if both were runtime claims.

## Bottom Line

The two-axis frame absorbs the frontier benchmark surprise and points toward a
stronger research program.

But it is not yet methodology.

The next step is the minimal Axis 2 probe described in
[Two-Axis Probe Discipline](https://github.com/dr3d/prethinker/blob/main/docs/TWO_AXIS_PROBE_DISCIPLINE.md):
one target fixture, standalone vs stuffed context, same questions, and
per-category degradation analysis.

If the probe shows structured decay, build the Axis 2 program. If it surprises
us, update the frame before building around it.
