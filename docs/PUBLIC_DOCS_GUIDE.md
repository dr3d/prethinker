# Public Docs Guide

Last updated: 2026-05-04

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

1. [docs/CURRENT_RESEARCH_HEADLINE.md](https://github.com/dr3d/prethinker/blob/main/docs/CURRENT_RESEARCH_HEADLINE.md)
2. [docs/MULTI_PASS_SEMANTIC_COMPILER.md](https://github.com/dr3d/prethinker/blob/main/docs/MULTI_PASS_SEMANTIC_COMPILER.md)
3. [PROJECT_STATE.md](https://github.com/dr3d/prethinker/blob/main/PROJECT_STATE.md)
4. [docs/ACTIVE_RESEARCH_LANES.md](https://github.com/dr3d/prethinker/blob/main/docs/ACTIVE_RESEARCH_LANES.md)
5. [docs/CURRENT_HARNESS_INSTRUMENT.md](https://github.com/dr3d/prethinker/blob/main/docs/CURRENT_HARNESS_INSTRUMENT.md)
6. [docs/README.md](https://github.com/dr3d/prethinker/blob/main/docs/README.md)
7. [docs/EXPLAINER.md](https://github.com/dr3d/prethinker/blob/main/docs/EXPLAINER.md)
8. [docs/GENERALIZATION_BASELINE_MATRIX.md](https://github.com/dr3d/prethinker/blob/main/docs/GENERALIZATION_BASELINE_MATRIX.md)
9. [docs/CURRENT_UTTERANCE_PIPELINE.md](https://github.com/dr3d/prethinker/blob/main/docs/CURRENT_UTTERANCE_PIPELINE.md)
10. [docs/SEMANTIC_IR_MAPPER_SPEC.md](https://github.com/dr3d/prethinker/blob/main/docs/SEMANTIC_IR_MAPPER_SPEC.md)
11. [docs/CLARIFICATION_EAGERNESS_STRATEGY.md](https://github.com/dr3d/prethinker/blob/main/docs/CLARIFICATION_EAGERNESS_STRATEGY.md)
12. [docs/FRONTIER_FIXTURE_STRATEGY.md](https://github.com/dr3d/prethinker/blob/main/docs/FRONTIER_FIXTURE_STRATEGY.md)
13. [README.md](https://github.com/dr3d/prethinker/blob/main/README.md)

## Current Research Center

The current headline is **semantic parallax**: one compile is one viewpoint.
Prethinker is moving toward multi-pass semantic compilation, where separate
backbone, support/source, temporal/status, and rule lenses propose constrained
views; the mapper admits each view independently; deterministic union
accumulates only admitted clauses.

The durable architectural pivot is:

```text
utterance + context
  -> semantic_router_v1 context/profile plan
  -> semantic_ir_v1 workspace
  -> deterministic mapper/admission diagnostics
  -> KB mutation, query, clarification, quarantine, or rejection
```

The current frontier extends that pivot to multi-pass compilation and rule
promotion. Story-like, procedural, enterprise-guidance, and charter-rule
sources can be viewed through separate backbone, support/source,
temporal/status, and rule lenses. The model proposes each view; the mapper
admits or skips each fragment; deterministic union accumulates only admitted
clauses.

The best current documents for that work are:

- [docs/ACTIVE_RESEARCH_LANES.md](https://github.com/dr3d/prethinker/blob/main/docs/ACTIVE_RESEARCH_LANES.md)
- [docs/CURRENT_HARNESS_INSTRUMENT.md](https://github.com/dr3d/prethinker/blob/main/docs/CURRENT_HARNESS_INSTRUMENT.md)
- [docs/CURRENT_UTTERANCE_PIPELINE.md](https://github.com/dr3d/prethinker/blob/main/docs/CURRENT_UTTERANCE_PIPELINE.md)
- [docs/CONTEXT_CONTROL_ARCHITECTURE_BRIEF.md](https://github.com/dr3d/prethinker/blob/main/docs/CONTEXT_CONTROL_ARCHITECTURE_BRIEF.md)
- [docs/CLARIFICATION_EAGERNESS_STRATEGY.md](https://github.com/dr3d/prethinker/blob/main/docs/CLARIFICATION_EAGERNESS_STRATEGY.md)
- [docs/FRONTIER_FIXTURE_STRATEGY.md](https://github.com/dr3d/prethinker/blob/main/docs/FRONTIER_FIXTURE_STRATEGY.md)
- [docs/SEMANTIC_IR_RESEARCH_DIRECTION_REPORT.md](https://github.com/dr3d/prethinker/blob/main/docs/SEMANTIC_IR_RESEARCH_DIRECTION_REPORT.md)
- [docs/SEMANTIC_IR_MAPPER_SPEC.md](https://github.com/dr3d/prethinker/blob/main/docs/SEMANTIC_IR_MAPPER_SPEC.md)
- [docs/TEMPORAL_GRAPH_V1.md](https://github.com/dr3d/prethinker/blob/main/docs/TEMPORAL_GRAPH_V1.md)
- [docs/DOMAIN_PROFILE_CATALOG.md](https://github.com/dr3d/prethinker/blob/main/docs/DOMAIN_PROFILE_CATALOG.md)
- [docs/COURTLISTENER_DOMAIN.md](https://github.com/dr3d/prethinker/blob/main/docs/COURTLISTENER_DOMAIN.md)
- [docs/SEC_CONTRACTS_DOMAIN.md](https://github.com/dr3d/prethinker/blob/main/docs/SEC_CONTRACTS_DOMAIN.md)
- [docs/SEMANTIC_ROUTER_EXPERIMENT.md](https://github.com/dr3d/prethinker/blob/main/docs/SEMANTIC_ROUTER_EXPERIMENT.md)
- [docs/ROUTER_TRAINING_SEED_AUDIT.md](https://github.com/dr3d/prethinker/blob/main/docs/ROUTER_TRAINING_SEED_AUDIT.md)
- [docs/DOMAIN_BOOTSTRAPPING_META_MODE.md](https://github.com/dr3d/prethinker/blob/main/docs/DOMAIN_BOOTSTRAPPING_META_MODE.md)
- [docs/MULTI_PASS_SEMANTIC_COMPILER.md](https://github.com/dr3d/prethinker/blob/main/docs/MULTI_PASS_SEMANTIC_COMPILER.md)
- [docs/MULTILINGUAL_SEMANTIC_IR_PROBE.md](https://github.com/dr3d/prethinker/blob/main/docs/MULTILINGUAL_SEMANTIC_IR_PROBE.md)
- [docs/NO_LANGUAGE_HANDLING_IN_PYTHON_AUDIT.md](https://github.com/dr3d/prethinker/blob/main/docs/NO_LANGUAGE_HANDLING_IN_PYTHON_AUDIT.md)
- [docs/FRONTIER_DATASET_SURVEY.md](https://github.com/dr3d/prethinker/blob/main/docs/FRONTIER_DATASET_SURVEY.md)
- [docs/prompts/SEMANTIC_IR_V1.md](https://github.com/dr3d/prethinker/blob/main/docs/prompts/SEMANTIC_IR_V1.md)

Current query/QA instruments:

- [docs/POST_INGESTION_QA_SURFACES.md](https://github.com/dr3d/prethinker/blob/main/docs/POST_INGESTION_QA_SURFACES.md)
- [docs/QUERY_SURFACE_MODE_COMPARISON.md](https://github.com/dr3d/prethinker/blob/main/docs/QUERY_SURFACE_MODE_COMPARISON.md)
- [docs/KB_INTERROGATOR.md](https://github.com/dr3d/prethinker/blob/main/docs/KB_INTERROGATOR.md)

Secondary design and pattern notes:

- [docs/PRETHINKER.md](https://github.com/dr3d/prethinker/blob/main/docs/PRETHINKER.md)
- [ROADMAP.md](https://github.com/dr3d/prethinker/blob/main/ROADMAP.md)
- [docs/CHAOS_PROVER_PATTERN_NOTES.md](https://github.com/dr3d/prethinker/blob/main/docs/CHAOS_PROVER_PATTERN_NOTES.md)

The newest open-domain work is the hint-free profile/bootstrap path: raw text
goes to an LLM-authored `intake_plan_v1` and `profile_bootstrap_v1` proposal,
then ordinary Semantic IR and deterministic admission test whether the proposed
predicate surface is usable. Human-authored expected Prolog files are
calibration tools, not product-time hints.

The newest rule-ingestion work started in Glass Tide and now transfers across
Sable Creek and Avalon. Broad compiles preserve charter/policy rules as source
records, while separate semantic lenses can admit executable clauses, acquire
body facts, union promotion-ready rule surfaces, and expose fanout, dormancy,
unsupported body goals, and helper-substrate gaps before any rule is promoted as
durable product behavior.

The newest query-surface work is row-level activation. Safe accumulated
rule/evidence surfaces can rescue rows that need them, but global activation can
perturb rows that were already good. Perfect-selector reports are diagnostic
upper bounds, not runtime policies.

The newest fixture-methodology work is the frontier fixture strategy: new
benchmarks should target specific architectural weaknesses, declare their
evidence lane before scoring, aim for a useful cold baseline difficulty band,
and trigger cross-fixture replay after general harness changes.

Clarification eagerness is now a named strategy surface, not just a UI behavior:
Prethinker should ask during ingestion when identity, temporal anchors,
correction targets, rule scope, or claim/fact boundaries block safe admission,
and should ask during query when the KB cannot answer without choosing a scope
for the user.

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

## Public Link And HTML Policy

GitHub Pages serves the public hub from `docs/index.html`. Public links to
Markdown should use GitHub `blob/main/...` URLs so readers see rendered Markdown
instead of raw or missing Pages output. Public links to HTML should use the
Pages domain.

Runtime/template HTML that belongs to the application stays with its owning
code, such as `ui_gateway/static/index.html` and
`scripts/templates/dialog-session-page.template.html`. Those files are not
public docs pages.

## Current Evidence Snapshot

Latest local verification:

- Frontier fixture progress is summarized in [docs/FRONTIER_PROGRESS_REPORT.md](https://github.com/dr3d/prethinker/blob/main/docs/FRONTIER_PROGRESS_REPORT.md), with raw journals linked for Iron Harbor, Blackthorn, Kestrel, Anaplan Polaris, Glass Tide, and Clarification Eagerness Trap.
- Multi-pass semantic compilation is now a named frontier: independent semantic lenses propose backbone, support/source, temporal/status, and rule fragments; the mapper admits each lens independently; deterministic union accumulates only admitted clauses.
- Clarification eagerness now has a dedicated first fixture at `datasets/clarification_eagerness/clarification_eagerness_trap/`: `20` ingestion CE cases, `20` query CE cases, and `10` baseline QA probes. CET-013 reran the source-context lane after the latest rule-admission work and held `40/40` correct, `0` over-eager, `0` under-eager, `0` unsafe candidates, `0` context-write violations, and `10/10` blocked-slot coverage. The remaining CE nuance is safe-partial richness, not ask/no-ask posture.
- Lean full pytest suite: `599 passed, 2 subtests passed`.
- Lava v5 latest 60-attempt rerun: `60/60` parsed JSON, `60/60` domain selector, `60/60` admission-safe, `45/60` semantic-clean, `41/60` full expectation score, `0` fuzzy edge kinds, and `0/60` temp-0 variance groups.
- `active_profile=auto` now uses `semantic_router_v1` as the first-pass context/profile planner. The old Python catalog selector is no longer in the active runtime or research harnesses.
- `semantic_ir_v1` now includes optional `temporal_graph_v1` proposal diagnostics: event nodes, time anchors, intervals, and temporal edges are visible in traces, but they cannot write durable KB facts unless matching `candidate_operations` pass admission.
- The new temporal kernel can answer `after/2`, transitive `precedes/2`, `follows/2`, and coarse `concurrent/2` queries from admitted temporal facts. This is deterministic Prolog reasoning over admitted clauses, not model-side temporal answering.
- Temporal anchor replacement now goes through stored-logic admission: changing `event_on/2`, `interval_start/2`, or `interval_end/2` for the same record requires an explicit retract/correction plan.
- Low-risk correction projection now ignores unsafe-implication residue that duplicates the stale fact being safely retracted, so explicit temporal corrections can remain `commit` when the safe retract/assert pair is complete.
- Multilingual router probe: `router_ok=10/10`, `compiler_parsed_ok=10/10` on raw Spanish, French, German, Portuguese, Italian, Japanese, and code-switched turns.
- Current profile packages supply router/compiler context, predicate contracts, and declarative validators for medical, legal/CourtListener, SEC/contracts, probate, and story-world lanes. The mapper still owns actual admission.
- Predicate-contract role enforcement blocks obvious argument-shape mismatches, profile validators block domain-specific unsafe admissions declaratively, temporal gates block inverted interval pairs, and duplicate-collapse prevents repeated candidate-operation floods from becoming repeated KB writes.
- Clause support records connect admitted facts/rules/retracts/queries back to their Semantic IR operation index, predicate, source, and rationale codes; this is a first dependency breadcrumb, not full truth maintenance yet.
- Epistemic Worlds v1 diagnostics preserve projection-blocked and supported-but-skipped candidates as scoped wrapper clauses such as `world_operation/4` and `world_arg/4`, so traces can remember rejected/quarantined/skipped content without asserting it as global truth.
- CourtListener legal-source lane: `legal_courtlistener@v0`, `adapters/courtlistener/`, synthetic legal seed fixtures, and ignored live smoke data for claim/finding, citation-not-endorsement, docket-not-holding, role-scope, provenance, and identity-boundary tests.
- SEC/contracts lane: `sec_contracts@v0`, `adapters/sec_edgar/`, and synthetic contract fixtures for obligation-not-fact, condition-not-event, temporal triggers, party scope, and breach-boundary tests.
- Semantic IR runtime edge pack: `20/20` decision labels, `0.976` avg score.
- Semantic IR weak-edge pack: `10/10` decision labels, `1.000` avg score.
- Cold generalization baseline: ten source-only fixtures currently total `245 exact / 81 partial / 144 miss` across `470` QA items, making transfer and overfit visible instead of assumed.
- Rule-lens transfer evidence: Sable Creek produced a body-supported public-hearing rule from admitted fact rows, and Avalon retained helper-composed matching-fund rules while the mapper skipped unsupported raw Prolog constructs.
- Policy/reimbursement cross-turn demo: English policy installed executable rules, derived query answers without writing derived `violation/2` facts, then corrected state and changed the answer.
- Anaplan Polaris enterprise-guidance fixture: multi-support safe-surface accumulation reached `42 exact / 1 partial / 0 miss` on a 43-question post-ingestion QA battery, with `0` runtime load errors and `0` QA write proposals.
- Profile bootstrap closed-loop smoke: a model-proposed starter profile ran generated starter cases through the normal Semantic IR mapper with `8/8` valid workspaces and `7/8` expected-boundary hits.
- Raw Proclamation hint-free profile-review experiment: useful early run produced `30` candidate predicates, `93` admitted source-compile operations, `4/4` successful planned passes, and first-20 post-ingestion QA at `10 exact / 5 partial / 4 miss / 1 not judged`. Newer source-record/reporter/condition pressure produced a stronger style-aligned compile shape (`18` predicates, `4` repeated structures, `497` admitted operations), and structural query-placeholder/QA planning improvements lifted that first-20 QA pass to `19 exact / 1 miss`. A follow-up status-aware hint-free recompile invented `grievance_status/2` with `source_bound_accusation` and reached `18 exact / 2 miss`, showing both progress on epistemic status and the remaining predicate-surface/query-planning tension.

The important qualitative result is that the current system has moved from
Python-side language rescue toward model-owned context planning plus
deterministic admission. The remaining hard problems are model-owned
segmentation, reusable predicate-contract coverage, durable temporal fact
representation and graph-derived QA, rule admission, broader profile validator
coverage, and mapper policy for partial/unsafe operations.
