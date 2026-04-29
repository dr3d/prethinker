# Public Docs Guide

Last updated: 2026-04-29

This page is the map for public readers. Git history keeps the older research
trail; these docs should describe the project as it sits now.

![Prethinker semantic IR workspace](assets/prethinker-semantic-ir-workspace.png)

## Main Invention

Prethinker is a governed semantic-intake layer for turning natural-language
claims into auditable symbolic state.

Use the project terms this way:

- **Prethinker**: the overall system and strict authority boundary.
- **Semantic IR**: the model-produced workspace where meaning is represented
  before truth is admitted.
- **Mapper**: deterministic code that admits, skips, clarifies, quarantines, or
  rejects candidate operations.
- **Prolog KB**: the durable symbolic state after admission.
- **Console**: the live cockpit for watching the process.
- **Medical/UMLS**: the current bounded domain lane, not a general clinical
  reasoning claim.

## Current Front Door

Read these first:

1. [PROJECT_STATE.md](https://github.com/dr3d/prethinker/blob/main/PROJECT_STATE.md)
2. [README.md](https://github.com/dr3d/prethinker/blob/main/README.md)
3. [AGENT-README.md](https://github.com/dr3d/prethinker/blob/main/AGENT-README.md)
4. [docs/PRETHINK_GATEWAY_MVP.md](https://github.com/dr3d/prethinker/blob/main/docs/PRETHINK_GATEWAY_MVP.md)
5. [ui_gateway/README.md](https://github.com/dr3d/prethinker/blob/main/ui_gateway/README.md)
6. [docs/PROJECT_HORIZON.md](https://github.com/dr3d/prethinker/blob/main/docs/PROJECT_HORIZON.md)
7. [docs/CURRENT_UTTERANCE_PIPELINE.md](https://github.com/dr3d/prethinker/blob/main/docs/CURRENT_UTTERANCE_PIPELINE.md)
8. [docs/CONTEXT_CONTROL_ARCHITECTURE_BRIEF.md](https://github.com/dr3d/prethinker/blob/main/docs/CONTEXT_CONTROL_ARCHITECTURE_BRIEF.md)

## Current Research Center

The active architectural pivot is:

```text
utterance + context
  -> semantic_router_v1 context/profile plan
  -> semantic_ir_v1 workspace
  -> deterministic mapper/admission diagnostics
  -> KB mutation, query, clarification, quarantine, or rejection
```

The newest console work extends that pivot to long narrative ingestion. Story-like
utterances can be split into focused Semantic IR segments, processed through the
same runtime path, and then shown as one deduped ledger turn. This is meant to
exercise model semantic understanding while keeping admission deterministic and
auditable.

The best current documents for that work are:

- [docs/CURRENT_UTTERANCE_PIPELINE.md](https://github.com/dr3d/prethinker/blob/main/docs/CURRENT_UTTERANCE_PIPELINE.md)
- [docs/CONTEXT_CONTROL_ARCHITECTURE_BRIEF.md](https://github.com/dr3d/prethinker/blob/main/docs/CONTEXT_CONTROL_ARCHITECTURE_BRIEF.md)
- [docs/SEMANTIC_IR_RESEARCH_DIRECTION_REPORT.md](https://github.com/dr3d/prethinker/blob/main/docs/SEMANTIC_IR_RESEARCH_DIRECTION_REPORT.md)
- [docs/SEMANTIC_IR_MAPPER_SPEC.md](https://github.com/dr3d/prethinker/blob/main/docs/SEMANTIC_IR_MAPPER_SPEC.md)
- [docs/DOMAIN_PROFILE_CATALOG.md](https://github.com/dr3d/prethinker/blob/main/docs/DOMAIN_PROFILE_CATALOG.md)
- [docs/COURTLISTENER_DOMAIN.md](https://github.com/dr3d/prethinker/blob/main/docs/COURTLISTENER_DOMAIN.md)
- [docs/SEC_CONTRACTS_DOMAIN.md](https://github.com/dr3d/prethinker/blob/main/docs/SEC_CONTRACTS_DOMAIN.md)
- [docs/SEMANTIC_ROUTER_EXPERIMENT.md](https://github.com/dr3d/prethinker/blob/main/docs/SEMANTIC_ROUTER_EXPERIMENT.md)
- [docs/ROUTER_TRAINING_SEED_AUDIT.md](https://github.com/dr3d/prethinker/blob/main/docs/ROUTER_TRAINING_SEED_AUDIT.md)
- [docs/DOMAIN_BOOTSTRAPPING_META_MODE.md](https://github.com/dr3d/prethinker/blob/main/docs/DOMAIN_BOOTSTRAPPING_META_MODE.md)
- [docs/MULTILINGUAL_SEMANTIC_IR_PROBE.md](https://github.com/dr3d/prethinker/blob/main/docs/MULTILINGUAL_SEMANTIC_IR_PROBE.md)
- [docs/NO_LANGUAGE_HANDLING_IN_PYTHON_AUDIT.md](https://github.com/dr3d/prethinker/blob/main/docs/NO_LANGUAGE_HANDLING_IN_PYTHON_AUDIT.md)
- [docs/FRONTIER_DATASET_SURVEY.md](https://github.com/dr3d/prethinker/blob/main/docs/FRONTIER_DATASET_SURVEY.md)
- [docs/prompts/SEMANTIC_IR_V1.md](https://github.com/dr3d/prethinker/blob/main/docs/prompts/SEMANTIC_IR_V1.md)

The newest open-domain work is the hint-free profile/bootstrap path: raw text
goes to an LLM-authored `intake_plan_v1` and `profile_bootstrap_v1` proposal,
then ordinary Semantic IR and deterministic admission test whether the proposed
predicate surface is usable. Human-authored expected Prolog files are
calibration tools, not product-time hints.

## Current Domain Lanes

The active domain work is a three-lane starter set. These lanes provide profile
context, predicate contracts, and admission pressure; none of them grants the
model direct write authority.

- [docs/MEDICAL_PROFILE.md](https://github.com/dr3d/prethinker/blob/main/docs/MEDICAL_PROFILE.md)
- [docs/UMLS_MVP.md](https://github.com/dr3d/prethinker/blob/main/docs/UMLS_MVP.md)
- [docs/COURTLISTENER_DOMAIN.md](https://github.com/dr3d/prethinker/blob/main/docs/COURTLISTENER_DOMAIN.md)
- [docs/SEC_CONTRACTS_DOMAIN.md](https://github.com/dr3d/prethinker/blob/main/docs/SEC_CONTRACTS_DOMAIN.md)
- [docs/DOMAIN_PROFILE_CATALOG.md](https://github.com/dr3d/prethinker/blob/main/docs/DOMAIN_PROFILE_CATALOG.md)

Medical/UMLS remains bounded medical memory and normalization, not broad
diagnosis. CourtListener is legal-source intake, not legal advice or outcome
prediction. SEC/contracts is obligation and filing intake, not investment or
contract advice.

Older ontology-prospector notes are now Git-history context. The current
surface is profile packages, UMLS bridge assets, predicate contracts, and the
domain profile catalog.

## Demo Surface

- [docs/CONSOLE_TRYBOOK.md](https://github.com/dr3d/prethinker/blob/main/docs/CONSOLE_TRYBOOK.md)
- [docs/DEMO_PLAYBOOK.md](https://github.com/dr3d/prethinker/blob/main/docs/DEMO_PLAYBOOK.md)
- [docs/POLICY_REIMBURSEMENT_DEMO.md](https://github.com/dr3d/prethinker/blob/main/docs/POLICY_REIMBURSEMENT_DEMO.md)
- [docs/EXPLAINER.md](https://github.com/dr3d/prethinker/blob/main/docs/EXPLAINER.md)

## Historical Or Legacy Context

Old generated HTML run reports, ladder/rung pages, dated prompt snapshots,
pre-mid-April media/results, legacy parser-lane notes, and stale report
manifests were retired from the forward-facing tree. Git history preserves them.
The older English-parser lane is useful history, but it should not be mistaken
for the preferred future architecture centered on router-owned context
engineering, Semantic IR workspaces, and deterministic admission.

## Current Evidence Snapshot

Latest local verification:

- Full pytest suite after compiler-strategy and QA-context updates: `396 passed`.
- Lava v5 latest 60-attempt rerun: `60/60` parsed JSON, `60/60` domain selector, `60/60` admission-safe, `45/60` semantic-clean, `41/60` full expectation score, `0` fuzzy edge kinds, and `0/60` temp-0 variance groups.
- `active_profile=auto` now uses `semantic_router_v1` as the first-pass context/profile planner. The old Python catalog selector is no longer in the active runtime or research harnesses.
- Multilingual router probe: `router_ok=10/10`, `compiler_parsed_ok=10/10` on raw Spanish, French, German, Portuguese, Italian, Japanese, and code-switched turns.
- Current profile packages supply router/compiler context, predicate contracts, and declarative validators for medical, legal/CourtListener, SEC/contracts, probate, and story-world lanes. The mapper still owns actual admission.
- Predicate-contract role enforcement blocks obvious argument-shape mismatches, profile validators block domain-specific unsafe admissions declaratively, temporal gates block inverted interval pairs, and duplicate-collapse prevents repeated candidate-operation floods from becoming repeated KB writes.
- Clause support records connect admitted facts/rules/retracts/queries back to their Semantic IR operation index, predicate, source, and rationale codes; this is a first dependency breadcrumb, not full truth maintenance yet.
- Epistemic Worlds v1 diagnostics preserve projection-blocked and supported-but-skipped candidates as scoped wrapper clauses such as `world_operation/4` and `world_arg/4`, so traces can remember rejected/quarantined/skipped content without asserting it as global truth.
- CourtListener legal-source lane: `legal_courtlistener@v0`, `adapters/courtlistener/`, synthetic legal seed fixtures, and ignored live smoke data for claim/finding, citation-not-endorsement, docket-not-holding, role-scope, provenance, and identity-boundary tests.
- SEC/contracts lane: `sec_contracts@v0`, `adapters/sec_edgar/`, and synthetic contract fixtures for obligation-not-fact, condition-not-event, temporal triggers, party scope, and breach-boundary tests.
- Semantic IR runtime edge pack: `20/20` decision labels, `0.976` avg score.
- Semantic IR weak-edge pack: `10/10` decision labels, `1.000` avg score.
- Goldilocks full-story segmented smoke: `56` deduped mutations across `50` segments, with placeholder and vague-predicate bad writes removed after adding a generic story-world predicate palette.
- Policy/reimbursement cross-turn demo: English policy installed executable rules, derived query answers without writing derived `violation/2` facts, then corrected state and changed the answer.
- Profile bootstrap closed-loop smoke: a model-proposed starter profile ran generated starter cases through the normal Semantic IR mapper with `8/8` valid workspaces and `7/8` expected-boundary hits.
- Raw Proclamation hint-free profile-review experiment: useful run produced `30` candidate predicates, `93` admitted source-compile operations, `4/4` successful planned passes, and first-20 post-ingestion QA at `10 exact / 5 partial / 4 miss / 1 not judged`. Newer source-record/reporter/condition pressure produced a stronger product-like compile shape (`18` predicates, `4` repeated structures, `497` admitted operations), and structural query-placeholder normalization lifted the first-20 QA pass to `12 exact / 2 partial / 6 miss`.

The important qualitative result is that the current system has moved from
Python-side language rescue toward model-owned context planning plus
deterministic admission. The remaining hard problems are model-owned
segmentation, reusable predicate-contract coverage, temporal fact
representation, rule admission, broader profile validator coverage, and mapper
policy for partial/unsafe operations.
