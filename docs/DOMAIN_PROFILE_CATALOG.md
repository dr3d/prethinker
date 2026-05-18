# Domain Profile Catalog

Last updated: 2026-05-18

Domain profiles are optional context and validation packages for Semantic IR.
They help the model choose useful predicates and help the mapper enforce
argument contracts without turning the generic mapper into domain-specific
Python.

## Boundary

Profiles may supply:

- a short roster description;
- selected profile context;
- predicate palettes and argument-role contracts;
- declarative validators;
- normalization hints and bounded alias context;
- domain-specific clarification pressure.

Profiles may not supply:

- durable truth;
- answer keys;
- hidden source interpretation by Python;
- permission to bypass mapper admission;
- product claims that a domain is solved.

The router may choose profile context. The mapper still owns admission.

## Current Shape

```text
utterance or document
  -> router/profile/context plan
  -> selected profile package
  -> semantic_ir_v1 workspace
  -> deterministic mapper and profile validators
  -> KB mutation, query, clarification, quarantine, or rejection
```

`active_profile=auto` is the measured control-plane path: the model sees a thin
profile roster, chooses relevant context, and the compiler receives only the
selected package. The trace should show which profile was visible, which was
selected, what context was loaded, and how admission responded.

## Example Profile Families

The repository has used profile packages for bounded research pressure such as:

- medical memory and UMLS-style type grounding;
- legal source/provenance and claim-versus-finding separation;
- contract and filing obligations;
- probate and estate records;
- story-world/narrative fixtures.

Treat these as profile-pattern evidence, not as public domain-product claims.
The active product question is whether profile contracts improve governed
compilation while keeping the admission boundary inspectable.

## Unknown Domains

Unknown-domain work now belongs under product and palette governance:

- use retrieval or representative samples to propose a predicate palette;
- treat the palette as review material, not facts;
- validate slot contracts and unlike-document transfer;
- promote only terms that survive replay without fixture vocabulary.

See [Product And Palette Governance](https://github.com/dr3d/prethinker/blob/main/docs/PRODUCT_AND_PALETTE_GOVERNANCE.md)
for the current version of this direction.

## Safety Rules

- A selected profile can add context, not authority.
- A profile validator can reject bad candidate rows, not invent good rows.
- Multiple plausible profiles should yield `mixed` or `clarify` unless their
  safe writes can be separated cleanly.
- Domain examples belong in tests or cold archive unless they state a reusable
  architecture lesson.
