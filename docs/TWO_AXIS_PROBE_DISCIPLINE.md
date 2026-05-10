# Two-Axis Probe Discipline

Last updated: 2026-05-09

Status: caution note for
[Two-Axis Benchmark Frame](https://github.com/dr3d/prethinker/blob/main/docs/TWO_AXIS_BENCHMARK_FRAME.md).

Related positioning:
[Edge Governance Positioning](https://github.com/dr3d/prethinker/blob/main/docs/EDGE_GOVERNANCE_POSITIONING.md).

## Why This Note Exists

The two-axis frame is a strong research direction:

- **Axis 1: what gets through the door**: compile-time fidelity.
- **Axis 2: what stays in the room**: retention durability under load.

But Axis 2 has not been measured yet.

The first frontier pilot measured single-document direct answer quality, which
is only **Axis-1-adjacent**. It did not fully measure compile-time fidelity,
because a model can answer a single-document question correctly without
preserving the document's structural commitments as durable, reusable state.

That means the frame is not methodology. It is a candidate direction that needs
a cheap probe before anyone builds a large harness, authors new fixtures, or
writes a publication around it.

## Do Not Collapse The Axes

Do not collapse the axes into "single-document vs multi-document." Both axes can
be tested in single-document and multi-document conditions.

The axes are:

- whether structural commitments survive reading
- whether those commitments remain recoverable under load

Axis 1 has a known structure:

```text
source document -> compile -> mapper admission -> query -> verdict
```

Axis 2 is different. It asks how meaning decays under context pressure:

- multiple documents in one context
- target document buried among distractors
- fixture order effects
- long irrelevant filler
- source attribution under interference
- repeated questions after intervening content

There is no current Prethinker harness for this. There is also no guarantee that
Prethinker's Axis 1 vocabulary is the right vocabulary for Axis 2 decay.

## What Is Uncertain

### Existing Lenses May Not Predict Decay

Lenses describe reading strategies for compilation. Frontier LLMs do not read
through those lenses. Their failures may be governed more by attention,
position, token form, and interference than by our lens categories.

### Guard Families May Not Transfer

The seven guard families describe Prethinker selector failures. LLMs may fail
along different lines:

- first mention vs later reference
- table facts vs prose facts
- exact strings vs semantic summaries
- facts near document boundaries vs facts in the middle
- source-local facts vs cross-document facts

If that happens, Axis 2 needs its own taxonomy.

### Existing Fixtures May Be Raw Material

A good Axis 1 fixture is a single hostile document.

A good Axis 2 experiment may be a combination of documents:

- similar identifiers across fixtures
- similar names with different roles
- authority structures that interfere
- source documents placed in different positions
- irrelevant filler inserted at controlled lengths

The unit of design may be the **context assembly**, not the fixture. Name this
object explicitly: an **assembly recipe**.

## Minimal Probe

Run one cheap experiment first.

Recommended target: `contradictory_evidence_packet`, because it has rich source
addressability, conflict, timestamp, lookup, and unresolved-status rows.

### Run A: Standalone

Ask the frontier model the fixture's 40 questions with only that fixture in
context.

Record:

- exact / partial / miss
- per-category score
- row-level failures

### Run B: Stuffed Context

Place the same fixture inside a context containing several other fixtures. Ask
the same 40 questions.

Control what we can:

- same model
- same scorer
- same questions
- same oracle
- same judge model and scoring rubric
- same retry policy
- same answer prompt format
- target fixture position recorded
- filler fixtures recorded

Change exactly one thing: context assembly. Do not build a separate scoring
world for Axis 2. Reuse the direct runner and common judge so any score delta is
attributable to context pressure rather than changed instrumentation.

### Optional Run C: Meta-Recall

Before the target questions, ask:

```text
What source documents do you have access to in this prompt? Briefly name or
describe each one.
```

Score this separately from target QA. It checks whether the model can still
identify the assembled context before it tries to answer document-specific
questions.

### Compare

Measure:

- aggregate score delta
- per-category score delta
- which rows flipped
- whether errors are structured or noisy
- whether failures are source-attribution, identifier, temporal, count, or
  epistemic-state failures
- whether meta-recall failed before substantive QA failed
- whether failures correlate with target position, source boundaries, or filler
  similarity

Store the exact assembly recipe with the result:

- target fixture
- filler fixtures
- order and target position
- approximate token count
- question sequence
- meta-recall prompt, if used
- standalone baseline artifact
- stuffed-context artifact

## Possible Outcomes

### Outcome 1: Structured Category Decay

Some categories degrade more than others.

This supports the Axis 2 program. Build the fuller harness and begin measuring a
decay hierarchy.

### Outcome 2: Uniform Decay

Scores drop, but categories drop together.

The phenomenon exists, but our categories may not be the right ones. Try
position, document length, and token-form stratification before authoring new
fixtures.

### Outcome 3: No Meaningful Decay

The tested model handles the context size well under these conditions.

That is useful too. It means Axis 2 may require larger contexts, more hostile
interference, different models, or a different framing.

### Outcome 4: New Vocabulary Emerges

The failure pattern does not match Prethinker lenses or guard families.

Examples:

- exact strings decay fastest
- table facts decay differently than prose facts
- first-mentioned facts survive better than middle facts
- document-source attribution fails before factual recall fails

This is probably the most interesting outcome, but it means the methodology
must be revised before scaling.

## What Not To Do Yet

Do not yet:

- build a full Axis 2 harness
- author a large Axis 2 fixture batch
- publish the two-axis frame as settled methodology
- assume Prethinker lens categories predict LLM decay
- assume frontier models will fail in the way we expect
- turn single-document direct QA into the full Axis 1 claim
- compare stuffed-context results without storing the recipe

The cost asymmetry is large. A probe costs an afternoon and some OpenRouter
credit. A premature methodology costs weeks and credibility.

## Recommended Next Step

Run the one-fixture stuffed-context probe.

Suggested first target:

- `contradictory_evidence_packet`

Suggested filler pool:

- one identifier-heavy fixture
- one rule-heavy fixture
- one count/composition fixture
- one narrative/state fixture

Output:

- standalone score
- stuffed score
- per-category delta
- flipped-row table
- assembly recipe JSON/Markdown
- optional meta-recall result
- short interpretation note

Then decide whether the larger two-axis program deserves engineering time.

## Bottom Line

The two-axis frame is a good direction. It may become a real benchmark
methodology.

But first: probe.

```text
direction first
discipline next
data third
methodology fourth
publication fifth
```
