# Prethinker Explainer

This is the public explainer for what Prethinker is, what it does well today, and where it still fails.

## Failure Modes We Kept Hitting (And Why They Matter)

The core discovery is this: most parser failures do not look like ignorance. They look like **near-correctness**.

The model often sounds right while still writing the wrong thing.

### 1. Argument direction illusions
English form is a poor predictor of Prolog argument order.

- "A is B's parent"
- "A has B as a parent"
- "A is parented by B"

These are close in wording and different in logic direction. Easy declaratives can pass while these fail.

### 2. Compound turns are a different problem, not just longer turns
"Assert this, retract that, then query lineage" can be semantically understood but serialized as one malformed logic blob.

Multi-clause language must be unpacked explicitly.

### 3. Natural-language retracts are under-specified
Humans do not say `retract(parent(x,y))`.
They say "undo that branch," "keep this edge," "swap the middle one."

Without a correction normalization layer, the system retracts the wrong thing or misses the retract.

### 4. Exclusion language is a silent killer
"not", "stays", "keep", "except" often indicate preserved structure, not removal.

A naive repair can wipe the branch that should have been protected.

### 5. Clarification can help or hurt
The question is not "ask more" vs "ask less."

Clarification helps when referents/write targets are unresolved.
Clarification hurts when the parse is already deterministic.

Good policy is selective friction.

### 6. Failures move as the system improves
Early failures were routing and schema shape.
Later failures are timing, branch preservation, correction semantics, and long-turn consistency.

That shift is progress, but still hard.

## How Prethinker Gets High Accuracy

Prethinker is a **governed intent compiler**: language can propose actions, but proposals do not get commit authority by default.

### Proposal is not authority
Natural language can suggest writes, queries, and repairs.
Durable state mutation is allowed only after policy and deterministic checks.

### Two memories, two jobs

1. **Sharp memory** (deterministic KB)
- retained named Prolog corpora
- exact queryability
- provenance-backed state
- only authoritative memory

2. **Mushy memory** (served LLM context)
- useful for phrasing, pronouns, and candidate clarifications
- probabilistic and advisory
- never a source of truth by itself

### Interception point (control plane)
Every turn is intercepted before write execution.

The compiler classifies intent, normalizes structure, decides commit/stage/escalate/reject, and only then permits runtime apply.

### Clarification is intentionally asymmetric

- **User clarification**: authoritative for intended meaning.
- **Served-LLM clarification**: advisory helper only.

A served model can suggest a likely interpretation. It cannot independently manufacture certainty for uncertain writes.

### Why the clarification voice sounds robotic
This is intentional safety design.

When requesting write authority, the system should sound instrument-like, not socially persuasive. A narrow, mechanical tone reduces the chance that fluency hides uncertainty.

## How We Tune It

We tune with a ladder that has two dimensions.

### Height: logical difficulty
facts -> rules -> chains -> retractions -> branch repair -> exclusion language -> story revisions -> clarification pressure.

### Width: language noise at fixed logic target
clean phrasing -> passive/inversion -> pronouns -> typos -> hedging -> missing punctuation -> mixed ingest/query turns.

Most systems look strong on height and weak on width. We track both.

### One concrete case shape
A typical case is:

1. establish world facts in plain English
2. ask baseline queries (expected true state)
3. apply state churn (add, retract, correct, exclude)
4. ask post-mutation queries
5. verify both new truth and preserved branches

That pattern catches "sounds-right, writes-wrong" behavior quickly.

### Why instrumentation matters
Run campaigns are expensive in wall-clock and review time. The main bottleneck is not launching runs; it is interpreting failures correctly.

That is why this repo emphasizes:

- prompt/version lineage
- run manifests and scoreboards
- reproducible scenario packs
- explicit failure retention, not only success screenshots

## What This Does Not Claim

Prethinker does not claim universal semantic parsing.

It claims something narrower and more useful today:

- deterministic memory discipline
- explicit trust boundaries
- auditable language-to-logic mutation
- transparent failure reporting as the system improves

## Why This Is Interesting

If English can be compiled into deterministic state under governance, you can narrate a world, mutate it over time, and query consequences without giving raw commit authority to a probabilistic model.

That is the product direction: not "chat that sounds smart," but **stateful reasoning you can inspect**.

![Prethinker control plane: natural-language input flows through interception, normalization, clarification/confirmation gates, then deterministic KB mutation](assets/prethinker-control-plane-infographic-v2.png)
