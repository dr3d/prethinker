# Domain Profile Catalog

Last updated: 2026-06-05

Domain profiles are now treated as governed predicate-pack registries for
bounded document families. They define the closed typed language a compile lens
may use, the value domains those carriers admit, and the validation gates that
decide whether a result is claim-bearing.

## Boundary

Profiles may supply or constrain:

- a closed predicate registry;
- lens-scoped offered signatures;
- carrier argument contracts and value domains;
- omission-accountability requirements;
- bounded typed reducers and integrity guards;
- representative seed and unlike-transfer micro-fixtures.

Profiles may not supply:

- durable truth;
- answer keys;
- hidden source interpretation by Python;
- permission to bypass mapper admission;
- product claims that a domain is solved;
- open-ended predicate invention during claim-bearing runs.

The LLM may propose facts inside the offered registry language. Deterministic
gates still own admission, replay, redaction survival, atom-shape checks,
lens-scope checks, registered-signature checks, and value-domain enforcement.

## Current Shape

```text
document family
  -> closed domain registry
  -> lens-scoped compile pass
  -> typed compile facts
  -> deterministic reducers and integrity guards
  -> N>=3/support>=2 transfer measurement
  -> claim, abstention boundary, or reject
```

For current research claims, the important selector is not broad
`active_profile=auto`; it is an explicit domain registry plus an explicit
profile-registry lens. The offered predicate set must be a function of the
domain and the lens:

```text
offered_predicates = f(domain_registry, lens)
```

Use `scripts/validate_domain_predicate_schema.py` to check that every offered
signature is registered, every predicate is offered by at least one lens, and
multi-lens registries do not accidentally hand the entire domain vocabulary to
one lens.

## Active Registry Families

The current governed profile registries live under `datasets/domain_profiles`:

- `fda_warning_letter_v1`
- `ntsb_investigation_v1`
- `sec_form_8k_v1`
- `osha_incident_v1`
- `state_ag_settlement_v1`
- `puc_order_v1`
- `procurement_gao_decision_v1`

These are research profiles, not product claims. The active result is narrow:
closed, lens-scoped predicate domains can stabilize some recurring
official-document anatomy under strict gates; open-ended substance remains an
abstention or lower-tier boundary unless a compact layer reproduces on unlike
documents.

## Unknown Domains

Unknown-domain work now belongs under the governed domain-predicate process:

- use retrieval or representative samples to propose a predicate palette;
- treat the palette as review material, not facts;
- close the palette into a registry and lens set;
- validate slot contracts, value domains, and unlike-document transfer;
- promote only terms that survive N>=3/support>=2, redaction/typed replay where
  QA exists, atom-shape, registered-signature, lens-scope, and value-domain
  gates.

See [Domain Predicate Schema Process](https://github.com/dr3d/prethinker/blob/main/docs/DOMAIN_PREDICATE_SCHEMA_PROCESS.md)
for the current version of this direction.

## Safety Rules

- A selected registry can offer language, not truth.
- A lens can narrow the offered predicate set, not expand beyond the registry.
- A profile validator can reject bad candidate rows, not invent good rows.
- Predicate and value-domain changes must be measured on unlike documents,
  not accepted because they rescue one row.
- Domain examples belong in tests or cold archive unless they state a reusable
  architecture lesson.
