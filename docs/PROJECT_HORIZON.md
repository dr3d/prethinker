# Prethinker Project Horizon

Last updated: 2026-04-27

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

For the detailed technical contract, see:

- [Semantic IR Mapper Spec](https://github.com/dr3d/prethinker/blob/main/docs/SEMANTIC_IR_MAPPER_SPEC.md)
- [Semantic IR Research Direction](https://github.com/dr3d/prethinker/blob/main/docs/SEMANTIC_IR_RESEARCH_DIRECTION_REPORT.md)
- [Domain Profile Catalog](https://github.com/dr3d/prethinker/blob/main/docs/DOMAIN_PROFILE_CATALOG.md)
- [Public Docs Guide](https://github.com/dr3d/prethinker/blob/main/docs/PUBLIC_DOCS_GUIDE.md)

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
