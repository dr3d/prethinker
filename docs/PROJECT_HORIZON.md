# Prethinker Project Horizon

Last updated: 2026-05-06

Prethinker's current aim is governed semantic intake into auditable symbolic
state.

That means the project is not trying to make a chatbot sound smarter. It is
trying to make selected pieces of language safe enough to become inspectable
state outside a model's private context window.

The current architecture is:

```text
utterance + context
  -> semantic_ir_v1 workspace
  -> deterministic mapper/admission
  -> Prolog KB mutation, query, clarification, quarantine, or rejection
```

The model proposes meaning. The runtime owns admission.

The current POWER/NITRO lab is the research rig, not the product boundary. A
future hosted lane must prove model-transfer evidence before it replaces the
local 35B workhorse.

For the detailed technical contract, see:

- [Semantic IR Mapper Spec](https://github.com/dr3d/prethinker/blob/main/docs/SEMANTIC_IR_MAPPER_SPEC.md)
- [Semantic IR Research Direction](https://github.com/dr3d/prethinker/blob/main/docs/SEMANTIC_IR_RESEARCH_DIRECTION_REPORT.md)
- [Domain Profile Catalog](https://github.com/dr3d/prethinker/blob/main/docs/DOMAIN_PROFILE_CATALOG.md)
- [Public Docs Guide](https://github.com/dr3d/prethinker/blob/main/docs/PUBLIC_DOCS_GUIDE.md)
- [Portability And Model Transfer](https://github.com/dr3d/prethinker/blob/main/docs/PORTABILITY_AND_MODEL_TRANSFER.md)

## What Exists Today

Today, Prethinker is a local research workbench and demonstration cockpit for:

- turning natural-language turns into Semantic IR proposals;
- admitting only safe candidate operations into symbolic state;
- preserving a ledger of what was admitted, skipped, clarified, quarantined, or
  rejected;
- using profile-owned predicate contracts for bounded domains such as medical,
  legal-source, SEC/contracts, story-world, and probate-style experiments;
- treating the Prolog KB as committed state, not as model opinion.

The strongest current claim is narrow:

Prethinker can make language-to-state mutation more explicit, testable, and
auditable than a normal freeform chat transcript.

The measured trajectory is broader than a toy demo. The instrument has been
calibrated against `25` hostile benchmarks across `14` domain types. The
current surgical fixture batch covers `9` fixtures and `303` questions, with
`284` exact answers (`94%`), only `3` misses, `7` zero-miss fixtures, Fenmore
and Greywell both perfect, and zero unauthorized writes across the checked
corpus. The evidence trail lives in
[Semantic Instrument](https://github.com/dr3d/prethinker/blob/main/docs/SEMANTIC_INSTRUMENT.md)
and the active progress journals.

## What Does Not Exist Yet

The horizon is broader than today's implementation.

Prethinker does not yet claim to be:

- a general legal, medical, or business-reasoning system;
- a complete temporal reasoner;
- a general theorem prover over natural language;
- a universal ontology builder;
- an autonomous planning agent;
- a production solver orchestrator.

Those are capability horizons, not current product claims.

## The Capability Horizon

If the current direction keeps working, the same governed intake pattern could
eventually support richer symbolic material:

- **Facts**: explicit state such as `owns(oskar, lease)` or
  `taking(mara, warfarin)`.
- **Rules**: scoped implications such as eligibility, inheritance, compliance,
  routing, or exception logic.
- **Constraints**: things that must not both be true, argument-type contracts,
  source-priority rules, and current-state exclusivity.
- **Worlds**: separate hypothetical, disputed, story, legal, or document-scoped
  states that should not collapse into one flat truth layer.
- **Objectives**: explicit goals or tasks that can be represented without
  silently becoming facts.
- **Solver handoff**: a future path where admitted symbolic state could be sent
  to a solver, planner, verifier, or query engine, with the handoff itself
  logged and bounded.
- **Truth and dependency boundaries**: evidence chains that distinguish direct
  observation, user claim, document text, model inference, contradiction,
  retraction, and derived consequence.

The important part is not any one solver or representation.

The important part is the boundary:

```text
language proposes
admission governs
state records
solvers may consume
dependencies stay visible
```

The first implementation step toward this boundary now exists inside
`semantic_ir_v1`: a `truth_maintenance` proposal block where the model may name
support links, conflicts, retraction plans, and derived consequences. That block
is not an execution surface. It is how the larger model can use more of its
semantic intelligence while deterministic admission still decides what becomes
state.

In practice, that means the model can say "this proposed correction depends on
turn 12, conflicts with the current holder row, and would imply retracting the
older status." The mapper can then inspect that dependency shape, admit the safe
pieces, quarantine the unsafe pieces, and preserve the diagnostic structure
without letting the diagnostic itself become truth.

## Why This Horizon Matters

Most model systems blur together:

- what was said;
- what was inferred;
- what was assumed;
- what was later corrected;
- what is currently safe to act on.

Prethinker's horizon is to keep those layers separate enough that downstream
systems can ask better questions:

- Is this a fact, a claim, a rule, a hypothesis, or a query?
- Which document or turn supports it?
- Was it directly observed or inferred?
- Did a later correction retract it?
- Which constraints block it from becoming durable state?
- Which solver, if any, is allowed to use it?

That is the project direction: not bigger hidden belief, but better governed
state.

## Public Chat-Site Guidepost

A plausible product horizon is a public chat-shaped site where visitors can
kick Prethinker directly. The surface can look simple: one bucket where a user
can paste a document, dump a family story, type ordinary facts, ask questions,
or correct something they said earlier.

The product should not depend on giving Prethinker a charming assistant
persona. The wow should come from instrument behavior:

- it notices whether a turn is adding world state, asking a question,
  correcting prior state, or exposing ambiguity;
- it answers from admitted symbolic memory rather than smoothing everything
  into a fluent guess;
- it distinguishes known, inferred, ambiguous, contradicted, superseded, and
  missing evidence;
- it asks sharp clarifying questions when a pronoun, identity, time boundary, or
  conflict matters;
- it can say "I can infer this, but here is the assumption" instead of hiding
  the assumption.

For casual use, a visitor might type:

```text
My mom is Ann, my dad is Ian, my brother is Blake, and his sons are Will and
Pierce. They live in Morro Bay, California.
```

The product behavior to earn is not only answering "Who are my nephews?" It is
also noticing that "they" has an interpretation boundary, answering with that
boundary visible, and later handling "Pierce moved to Oregon last year" as a
time-aware update rather than a flat overwrite.

For document use, the same surface should let a visitor paste large messy text,
watch Prethinker compile an inspectable world/package, then interrogate it. The
answer panel should make evidence, uncertainty, conflicts, and missing support
visible enough that the user feels the difference between a governed instrument
and an ordinary chatbot.

This guidepost is aspirational. A public v1 would need the current harness
wrapped around a strong structured-output model lane, likely through a hosted
provider such as OpenRouter only after context, JSON-schema behavior, latency,
cost, and transfer scores match the local POWER 35B lane closely enough. NITRO's
small-model sidecar lane may draft QA or summarize artifacts, but it is not hot
enough to serve as the Prethinker instrument.

## Near-Term Research Pressure

The next hard problems are already visible in the frontier packs and current
docs:

- cross-turn identity drift;
- claims versus observed facts;
- rule/query/fact mixtures;
- temporal corrections and interval boundaries;
- conflicting current-state updates;
- domain type ambiguity;
- noisy or multilingual phrasing;
- profile-owned validators that avoid English-specific Python patches.

Those pressures map directly to the concrete work plan in
[Cross-Fixture Repair Slices](https://github.com/dr3d/prethinker/blob/main/docs/CROSS_FIXTURE_REPAIR_SLICES.md),
where recurring failures are grouped into multi-fixture repair slices rather
than chased as one-off local accidents.

Those are not distractions from the main project. They are the path to making
the authority boundary real.

## Bottom Line

Prethinker is currently a governed Semantic IR intake layer backed by
deterministic admission into auditable symbolic state.

The horizon is a broader governed symbolic interface where facts, rules,
constraints, worlds, objectives, and solver handoffs can coexist without losing
truth boundaries or dependency trails.

That horizon is aspirational. The current work is the intake and admission
layer that would make it credible.
