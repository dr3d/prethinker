# Active Research Lanes

Last updated: 2026-06-01

This page is the compact public map of current work. It is not a rolling
session journal. Older lane notes, fixture-specific repair slices, retired
compatibility experiments, and generated reports live in Git history or the
local cold archive.

## Operating Rule

Prethinker's active research asks whether source documents can be compiled into
durable symbolic state, then queried cheaply and safely from the compiled
package.

Current default:

```text
source document
  -> compile into admitted predicates, epistemic state, deterministic ledgers,
     manifests, diagnostics
  -> answer from direct KB surfaces and deterministic ledgers
  -> repair only with fixture-free, replay-tested architecture
```

Do not promote a repair because it helps one fixture, row, answer string, or
dataset label. Promote only when the principle survives unlike probes.

## Live Lanes

| Priority | Lane | Question | Current Surface |
| --- | --- | --- | --- |
| 1 | Domain tier strategy | Can one closed document-type schema produce verified Tier 1 answers while the general compiler remains a lower-trust fallback? | `docs/DOMAIN_TIER_STRATEGY.md` |
| 2 | Per-answer-class hard-clean table | Which answer classes survive the hard-clean gate, and which substantive classes need domain predicates? | `docs/DOMAIN_TIER_WORKSHEET.md`, archive artifacts |
| 3 | Answer-judge governance | Does the evaluator reject empty evidence, wrong-reference evidence, prose-dependent evidence, and oracle leakage? | `scripts/audit_reference_judge_null_controls.py`, `scripts/audit_redaction_replay.py`, `scripts/audit_typed_plan_replay.py` |
| 4 | Atom-shape and carrier governance | Can compiled atoms stay compact, typed, and contract-governed instead of hiding prose in names or slots? | `scripts/audit_kb_atom_inventory.py`, carrier registry |
| 5 | Domain schema wedge selection | Which single regulatory document type has the strongest mix of value, repeated anatomy, and existing carrier coverage? | `docs/DOMAIN_TIER_STRATEGY.md`, per-class table |
| 6 | Overlay discipline | Can ACH and future lenses read compiled evidence without mutating KB truth, QA verdicts, or compile metrics? | `docs/OVERLAY_ARCHITECTURE.md`, `docs/ACH_OVERLAY_PROBE.md` |
| 7 | Provider/runtime discipline | Which model/provider/settings conditions are comparable enough for claims? | `docs/PROVIDER_RUNTIME_DISCIPLINE_NOTE.md` |
| 8 | Public face hygiene | Does the repo front door describe the living project without surfacing obsolete claims or generated artifact strata? | `README.md`, `docs/PUBLIC_DOCS_GUIDE.md` |

## Current Architecture Pressure

The direct-surface path is the live instrument: admitted predicates,
deterministic ledgers, predicate contracts, selectors, guards, and query policy.
Retired compatibility adapters are not part of the forward repair path.

The highest-value current pressure is therefore:

- preserve concrete source coordinates as deterministic ledgers;
- compile recurring roles, statuses, quantities, transitions, authority
  envelopes, and source-record distinctions as direct admitted predicates;
- detect when a compile used vague `detail/event` wrappers where concrete
  backbone rows should exist;
- use unlike probes before naming any new surface architecture;
- keep fixture nouns, row IDs, answer strings, and dataset labels out of the
  harness.

## Resource Policy

POWER and OpenRouter are both measurement lanes. Prefer the route that gets
clean evidence fastest:

- use local single-lane runs when LM Studio/POWER is stable and avoids provider
  variance;
- use OpenRouter for parallel cold compiles, external transfer measurements,
  and independent draws;
- default hosted pressure to six lanes or fewer unless provider throughput
  evidence says otherwise;
- tag OpenRouter calls by experiment family, phase, and fixture/corpus so cost
  and speed can be inspected later.

Provider failures are transport evidence, not architecture evidence.

## Reset Readiness

The project is in a sign-clean reset, not a release freeze. Earlier high product
scores remain useful history, but they are not current claim-bearing numbers
because they depended on source-record prose paths, open predicate drift, or
judge-facing surface tokens.

Current claim-bearing measurement is the hard-road floor on the current
8-fixture English batch:

```text
Product exact:                  88 / 200 = 44.0%
Typed-plan exact:               84 / 200 = 42.0%
Redaction-survived exact:       81 / 200 = 40.5%
Atom-shape-clean product exact: 84 / 200 = 42.0%
Hard-clean floor:               73 / 200 = 36.5%
```

This is a research floor, not a product claim. It says the general typed layer
is alive but not yet viable as the whole product. The next product-shaped move
is a closed domain schema measured by the same hard-clean gate.

Before the next product-facing claim:

1. Produce the per-answer-class hard-clean table.
2. Select one domain/document wedge.
3. Define the closed carrier schema and Tier 1 assignment rule.
4. Run answer-judge null controls and oracle-isolation checks.
5. Measure domain-schema answers with hard-clean gates before considering any
   RAG fallback.

## What Stays Off The Front Door

Do not resurface retired lab-automation, publishing, public-benchmarking,
generated report explorer, old compatibility-residue, or dated run-log strata
in public entry points. Git history keeps that material. The current repo
should remain a sharp map of the instrument as it exists now.
