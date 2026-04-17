# Ontology Steering and Registry Strategy

This note captures the intended shape of ontology control in Prethinker.

It separates:

- what the repo does today
- what a delivered system should do
- what should and should not change automatically in the field

## Current Repo Reality

Today, Prethinker uses static predicate registries loaded from JSON files such as:

- `modelfiles/predicate_registry.json`
- `modelfiles/predicate_registry.blocksworld.json`

The runtime:

- loads the active registry at startup
- builds a set of allowed predicate signatures (`name/arity`)
- optionally injects those signatures into the parser prompt
- optionally enforces strict admission with `--strict-registry`
- optionally rewrites registered aliases onto canonical predicate names

This means the registry already serves two roles:

1. Ontological steering at generation time
2. Ontological admission control at validation time

The current implementation is intentionally static during a run. The active registry does not self-mutate while ingesting user material.

## What "Single Prethinker" Should Mean

Prethinker should be one engine with shared runtime semantics, not one giant flat ontology that pretends every domain is equally well modeled.

The right long-term shape is:

- one parsing/runtime core
- one shared KB discipline
- multiple ontology profiles

Examples of ontology profiles:

- `general`
- `blocksworld`
- `legal`
- `medical`
- `operations`

The active profile should determine:

- which predicate registry is in force
- which type schema is in force
- how strict admission should be
- how aggressively clarification should be requested

## Why Not One Huge Universal Registry

A single monolithic registry is the wrong target because it causes:

- prompt bloat
- more semantic overlap between predicates
- easier accidental admission of low-quality parses
- weaker domain boundaries
- more configuration mistakes when evaluating results

Prethinker should support wide topical coverage through profile selection, not through one endlessly growing universal predicate list.

## Delivered-System Shape

A delivered system should likely ship with layered ontology assets:

1. Formal shipped registries
- versioned
- tested
- curated
- stable for a release

2. Domain-specific registries
- legal, medical, logistics, narrative, etc.
- narrower than a universal registry
- paired with optional type schemas and validation settings

3. Field overlays
- local or customer-specific additions
- aliases for local language
- deployment-specific naming adjustments
- enabled explicitly, not silently merged into canonical product files

4. Promotion pipeline
- field-learned candidates reviewed by humans
- promoted into formal registries only after evidence and testing
- shipped back in a later formal version

## Live Augmentation Policy

Registries may grow over time, but strict registries should not silently rewrite themselves in production.

Healthy live behavior is:

- unknown predicate encountered
- system logs it as a candidate
- candidate is classified as one of:
  - alias suggestion
  - local overlay addition
  - upstream promotion candidate
- human review decides whether it becomes:
  - an alias to an existing canonical predicate
  - an overlay-only predicate
  - a formal predicate in a future shipped registry

Unhealthy live behavior is:

- strict mode admits unknown predicates automatically
- canonical registries mutate in place during normal traffic
- evaluation baselines change invisibly between runs

That would make "strict" unstable and damage reproducibility.

## Formal Registry vs Field Overlay

These should be treated differently.

Formal registry:

- part of the release
- stable across runs for that release
- used for benchmark claims
- covered by regression tests

Field overlay:

- specific to one deployment, customer, or site
- may include local aliases or truly local predicates
- should be separately versioned and clearly identified in run artifacts
- should not be confused with the formal product ontology

## Promotion Path Back to Formal Versions

Field augmentation is useful only if there is a clean path back upstream.

The intended loop is:

1. Observe unknown or awkwardly mapped predicates in real traffic.
2. Record them with provenance and frequency.
3. Review whether they are:
- parser mistakes
- aliases of existing canonical predicates
- real new predicates
4. Add them to:
- alias maps
- field overlay registries
- or the next formal registry release
5. Re-run benchmark packs before promotion.

This keeps the system adaptable without sacrificing honest strictness.

## Practical Release Model

The clean production shape is something like:

- `general@v1`
- `legal@v1`
- `medical@v1`
- `customer_overlay@v1`

Run artifacts should record which combination was active.

For example:

- registry profile: `medical`
- formal registry version: `medical@v3`
- overlay version: `hospital_a@v2`

That makes field behavior auditable and benchmark claims reproducible.

## What This Repo Already Supports

The current repo already supports important pieces of this design:

- registry-based predicate steering
- strict registry enforcement
- alias handling in registry files
- optional type-schema enforcement
- domain-specific registry files
- cross-domain registry guardrails in suite runners

## What Is Still Missing

The repo does not yet fully implement the production architecture described above.

Not yet formalized:

- first-class `registry-profile` selection across the whole stack
- versioned overlay loading and reporting
- a dedicated `pending_promotions` workflow
- human-review tooling for registry promotion
- clean separation between formal ontology packages and field overlay packages

## Design Rule

Prethinker should be broad by architecture, not vague by ontology.

That means:

- one engine
- many profiles
- explicit steering
- explicit validation
- explicit promotion

Wide-domain handling is a strength only if the ontology boundary remains legible.
