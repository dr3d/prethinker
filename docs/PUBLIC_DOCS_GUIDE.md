# Public Docs Guide

Last updated: 2026-04-27

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
- **Freethinker**: shelved optional clarification-sidecar experiment; not the
  current mainline path.
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

## Current Research Center

The active architectural pivot is:

```text
utterance + context
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
- [docs/SEMANTIC_IR_RESEARCH_DIRECTION_REPORT.md](https://github.com/dr3d/prethinker/blob/main/docs/SEMANTIC_IR_RESEARCH_DIRECTION_REPORT.md)
- [docs/SEMANTIC_IR_MAPPER_SPEC.md](https://github.com/dr3d/prethinker/blob/main/docs/SEMANTIC_IR_MAPPER_SPEC.md)
- [docs/DOMAIN_PROFILE_CATALOG.md](https://github.com/dr3d/prethinker/blob/main/docs/DOMAIN_PROFILE_CATALOG.md)
- [docs/COURTLISTENER_DOMAIN.md](https://github.com/dr3d/prethinker/blob/main/docs/COURTLISTENER_DOMAIN.md)
- [docs/SEC_CONTRACTS_DOMAIN.md](https://github.com/dr3d/prethinker/blob/main/docs/SEC_CONTRACTS_DOMAIN.md)
- [docs/GUARDRAIL_DEPENDENCY_AB.md](https://github.com/dr3d/prethinker/blob/main/docs/GUARDRAIL_DEPENDENCY_AB.md)
- [docs/PYTHON_GUARDRAIL_AUDIT.md](https://github.com/dr3d/prethinker/blob/main/docs/PYTHON_GUARDRAIL_AUDIT.md)
- [docs/prompts/SEMANTIC_IR_V1.md](https://github.com/dr3d/prethinker/blob/main/docs/prompts/SEMANTIC_IR_V1.md)

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

Ontology notes:

- [docs/ONTOLOGY_PROSPECTOR.md](https://github.com/dr3d/prethinker/blob/main/docs/ONTOLOGY_PROSPECTOR.md)
- [docs/ONTOLOGY_STEERING.md](https://github.com/dr3d/prethinker/blob/main/docs/ONTOLOGY_STEERING.md)

## Demo Surface

- [docs/CONSOLE_TRYBOOK.md](https://github.com/dr3d/prethinker/blob/main/docs/CONSOLE_TRYBOOK.md)
- [docs/DEMO_PLAYBOOK.md](https://github.com/dr3d/prethinker/blob/main/docs/DEMO_PLAYBOOK.md)
- [docs/EXPLAINER.md](https://github.com/dr3d/prethinker/blob/main/docs/EXPLAINER.md)

## Historical Or Legacy Context

These docs are still useful, but should be read as context for how the project
got here, not as the current center of gravity:

- [docs/GIC_ENGLISH_INPUT_PIPELINE.md](https://github.com/dr3d/prethinker/blob/main/docs/GIC_ENGLISH_INPUT_PIPELINE.md)
Old generated HTML run reports, ladder/rung pages, dated prompt snapshots,
legacy parser-lane notes, and stale report manifests were retired from the
forward-facing tree. Git history preserves them. The older 9B English-parser
lane is useful history, but it should not be mistaken for the preferred future
architecture.

## Current Evidence Snapshot

Latest local verification before this refresh:

- Full pytest suite: `318 passed`
- Profile-aware Semantic IR/UMLS handoff: `medical@v0` now supplies predicate contracts plus compact UMLS bridge context to the model input before deterministic admission
- Domain-profile catalog foundation: thin roster plus mock `story_world@v0` and `probate@v0` thick-context packages for future skill-like profile selection
- Auto profile-selection smoke: deterministic selector can steer one synthetic conversation through `medical@v0`, `legal_courtlistener@v0`, `sec_contracts@v0`, then back to `medical@v0`, loading matching thick context and predicate contracts per turn
- Mixed-domain agility smoke: `scripts/run_mixed_domain_agility.py` shuffled Goldilocks, Glitch, Ledger, CourtListener, SEC/contracts, and medical cases; first LM Studio smoke reached `12/12` expected profile selections and `12/12` valid Semantic IR
- Mixed-domain tightening pass: same seed reduced bad admitted placeholder/loose-trait clauses from `4` to `0` by adding generic placeholder admission guards and sharper story-world predicates
- Mixed-domain hard seed `99`: selector accuracy improved from `18/24` to `24/24`; real LM Studio pass stayed `24/24` valid Semantic IR
- Mixed-domain wider seed `2718`: selector-only improved from `36/40` to `40/40`; real LM Studio pass reached `40/40` expected profile selections and `40/40` valid Semantic IR
- Current profile packages use declarative `selection_keywords` plus profile-owned predicate contracts for legal source documents, relative dates, probate guardianship/conditional gifts, and SEC/contract-style clearance state; the mapper still owns actual admission
- Predicate-contract role enforcement now blocks obvious argument-shape mismatches, such as an `interval_start/2` operation whose first argument is a date instead of an interval id; the latest seed `2718` LM Studio run preserved `40/40` profile selections and `40/40` valid Semantic IR with that stricter gate enabled
- Profile-owned admission validators now live in the legal and SEC profile contracts, so allegation-shaped findings, citation-shaped holdings, obligation-shaped breach events, and unevidenced condition satisfaction can be blocked declaratively rather than by hidden mapper code
- Minimal temporal sanity checking now blocks inverted interval pairs where `interval_start/2` is later than `interval_end/2`
- Latest seed `2718` LM Studio pass with these validators stayed at `40/40` expected profile selections and `40/40` valid Semantic IR; the legal validator blocked one allegation-shaped `finding/4` while keeping the safe `claim_made/4`
- Clause support records now connect admitted facts/rules/retracts/queries back to their Semantic IR operation index, predicate, source, and rationale codes; this is a first dependency breadcrumb, not full truth maintenance yet
- Mapper duplicate-collapse now prevents repeated candidate-operation floods from becoming repeated KB writes
- CourtListener legal-source lane: `legal_courtlistener@v0`, `adapters/courtlistener/`, a synthetic legal seed fixture, and ignored live CourtListener smoke data for claim/finding, citation, docket, role-scope, provenance, and identity-boundary tests
- SEC/contracts scaffold: `sec_contracts@v0`, `adapters/sec_edgar/`, and a synthetic contract seed fixture for obligation, condition, temporal-trigger, party-scope, and breach-boundary tests
- Focused Semantic IR console/story-ingestion verification: `55 passed`
- Focused profile-contract verification: `6 passed`
- Focused domain-profile package verification: `2 passed`
- Focused CourtListener/domain-profile verification: `8 passed`
- Focused SEC/domain-profile verification: `9 passed`
- Semantic IR runtime edge pack: `20/20` decision labels, `0.976` avg score
- Semantic IR weak-edge pack: `10/10` decision labels, `1.000` avg score
- Goldilocks full-story segmented smoke: `56` deduped mutations across `50`
  segments, with placeholder and vague-predicate bad writes removed after adding
  a generic story-world predicate palette
- Silverton probate pack: intentionally hard frontier pack, currently weak
- Silverton noisy temporal pack: intentionally harder noisy/multilingual pack,
  useful as a pressure gauge rather than a demo headline
- Cross-turn frontier proposal: `docs/data/frontier_packs/semantic_ir_cross_turn_frontier_pack_v1.json`, held out for future runner integration
- Lava sweep harness: `scripts/run_semantic_ir_lava_sweep.py` balances old and new scenario sources, generates typo/bad-grammar/context-switch variants, repeats temperature-0 signatures for variance checks, applies admitted writes to a private stream KB, and records admitted queries without executing them by default so recursive query evaluation cannot stall broad Semantic IR sweeps

The important qualitative result is that semantic IR has reduced dependence on
non-mapper Python rescue code in tested packs. The remaining hard problems are
reusable predicate-contract coverage, temporal fact representation, rule
admission, broader profile validator coverage, and the mapper policy for
partial/unsafe operations.
