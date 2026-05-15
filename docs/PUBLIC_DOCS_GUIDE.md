# Public Docs Guide

Last updated: 2026-05-11

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
- **Compiled KB package**: the durable artifact package, especially
  `world.pl`, `epistemic.pl`, helpers, manifest, and diagnostics.
- **Row**: one measured encounter between a question and the compiled state:
  question, reference answer, attempt, verdict, and supporting trace.
- **Selector**: the steering wheel that chooses the best available QA surface
  for a row.
- **Guard**: the check that blocks a tempting but wrong surface when it has
  volume, proximity, or relaxed evidence without the needed precision.
- **Pegboard**: the working roster of lenses, helpers, registries, and selector
  modes that can be tested row-by-row against frozen artifacts.
- **Console**: the live cockpit for watching the process.
- **Medical/UMLS**: a bounded domain lane, not a general clinical reasoning
  claim.

## Current Front Door

Read these first:

1. [docs/CURRENT_RESEARCH_HEADLINE.md](https://github.com/dr3d/prethinker/blob/main/docs/CURRENT_RESEARCH_HEADLINE.md)
2. [docs/CTO_ARCHITECTURE_BRIEF.md](https://github.com/dr3d/prethinker/blob/main/docs/CTO_ARCHITECTURE_BRIEF.md)
3. [docs/SEMANTIC_INSTRUMENT.md](https://github.com/dr3d/prethinker/blob/main/docs/SEMANTIC_INSTRUMENT.md)
4. [docs/TWELVE_LENSES_EXPLAINED.md](https://github.com/dr3d/prethinker/blob/main/docs/TWELVE_LENSES_EXPLAINED.md)
5. [docs/MULTI_PASS_SEMANTIC_COMPILER.md](https://github.com/dr3d/prethinker/blob/main/docs/MULTI_PASS_SEMANTIC_COMPILER.md)
6. [PROJECT_STATE.md](https://github.com/dr3d/prethinker/blob/main/PROJECT_STATE.md)
7. [docs/BOUNDARY_HUNT_WORKSHEET.md](https://github.com/dr3d/prethinker/blob/main/docs/BOUNDARY_HUNT_WORKSHEET.md)
8. [docs/HELPER_RESIDUE_AUDIT_WORKSHEET.md](https://github.com/dr3d/prethinker/blob/main/docs/HELPER_RESIDUE_AUDIT_WORKSHEET.md)
9. [docs/COMPILE_SURFACE_STABILITY_WORKSHEET.md](https://github.com/dr3d/prethinker/blob/main/docs/COMPILE_SURFACE_STABILITY_WORKSHEET.md)
10. [docs/ACTIVE_RESEARCH_LANES.md](https://github.com/dr3d/prethinker/blob/main/docs/ACTIVE_RESEARCH_LANES.md)
11. [docs/CURRENT_HARNESS_INSTRUMENT.md](https://github.com/dr3d/prethinker/blob/main/docs/CURRENT_HARNESS_INSTRUMENT.md)
12. [docs/SELECTOR_GUARD_FAMILY_ROLLUP.md](https://github.com/dr3d/prethinker/blob/main/docs/SELECTOR_GUARD_FAMILY_ROLLUP.md)
13. [docs/README.md](https://github.com/dr3d/prethinker/blob/main/docs/README.md)
14. [docs/EXPLAINER.md](https://github.com/dr3d/prethinker/blob/main/docs/EXPLAINER.md)
15. [docs/CURRENT_UTTERANCE_PIPELINE.md](https://github.com/dr3d/prethinker/blob/main/docs/CURRENT_UTTERANCE_PIPELINE.md)
16. [docs/SEMANTIC_IR_MAPPER_SPEC.md](https://github.com/dr3d/prethinker/blob/main/docs/SEMANTIC_IR_MAPPER_SPEC.md)
17. [docs/CLARIFICATION_EAGERNESS_STRATEGY.md](https://github.com/dr3d/prethinker/blob/main/docs/CLARIFICATION_EAGERNESS_STRATEGY.md)
18. [docs/BOUNDARY_PROBE_RESEARCH_METHOD.md](https://github.com/dr3d/prethinker/blob/main/docs/BOUNDARY_PROBE_RESEARCH_METHOD.md)
19. [README.md](https://github.com/dr3d/prethinker/blob/main/README.md)

## Current Research Center

The current headline is **row-gated semantic parallax**: one compile is one
viewpoint, and one row is one measured encounter with the compiled state.
Prethinker is no longer trying to win by making every compile broader. It is
learning which admitted surface should answer which question.

```text
compiled KB = durable state
row = measured encounter with that state
selector = chooses the best encounter surface
guard = prevents a tempting wrong surface
verdict = records what happened
```

The durable architectural pivot is:

```text
utterance + context
  -> semantic_router_v1 context/profile plan
  -> semantic_ir_v1 workspace
  -> deterministic mapper/admission diagnostics
  -> KB mutation, query, clarification, quarantine, or rejection
```

The current frontier extends that pivot to multi-pass compilation, rule
promotion, query helpers, and selector governance. Story-like, procedural,
enterprise-guidance, and charter-rule sources can be viewed through separate
backbone, support/source, temporal/status, rule, provenance, registry, and
helper surfaces. The model proposes each view; deterministic admission decides
what can enter the compiled artifact; selectors and guards decide which
encounter surface is safe for each row.

The best current documents for that work are:

- [docs/ACTIVE_RESEARCH_LANES.md](https://github.com/dr3d/prethinker/blob/main/docs/ACTIVE_RESEARCH_LANES.md)
- [docs/CTO_ARCHITECTURE_BRIEF.md](https://github.com/dr3d/prethinker/blob/main/docs/CTO_ARCHITECTURE_BRIEF.md)
- [docs/SEMANTIC_INSTRUMENT.md](https://github.com/dr3d/prethinker/blob/main/docs/SEMANTIC_INSTRUMENT.md)
- [docs/TWELVE_LENSES_EXPLAINED.md](https://github.com/dr3d/prethinker/blob/main/docs/TWELVE_LENSES_EXPLAINED.md)
- [docs/CURRENT_HARNESS_INSTRUMENT.md](https://github.com/dr3d/prethinker/blob/main/docs/CURRENT_HARNESS_INSTRUMENT.md)
- [docs/BOUNDARY_HUNT_WORKSHEET.md](https://github.com/dr3d/prethinker/blob/main/docs/BOUNDARY_HUNT_WORKSHEET.md)
- [docs/BOUNDARY_PROBE_RESEARCH_METHOD.md](https://github.com/dr3d/prethinker/blob/main/docs/BOUNDARY_PROBE_RESEARCH_METHOD.md)
- [docs/COMPILE_SURFACE_STABILITY_WORKSHEET.md](https://github.com/dr3d/prethinker/blob/main/docs/COMPILE_SURFACE_STABILITY_WORKSHEET.md)
- [docs/SELECTOR_GUARD_FAMILY_ROLLUP.md](https://github.com/dr3d/prethinker/blob/main/docs/SELECTOR_GUARD_FAMILY_ROLLUP.md)
- [docs/CURRENT_UTTERANCE_PIPELINE.md](https://github.com/dr3d/prethinker/blob/main/docs/CURRENT_UTTERANCE_PIPELINE.md)
- [docs/CLARIFICATION_EAGERNESS_STRATEGY.md](https://github.com/dr3d/prethinker/blob/main/docs/CLARIFICATION_EAGERNESS_STRATEGY.md)
- [docs/SEMANTIC_IR_MAPPER_SPEC.md](https://github.com/dr3d/prethinker/blob/main/docs/SEMANTIC_IR_MAPPER_SPEC.md)
- [docs/DOMAIN_PROFILE_CATALOG.md](https://github.com/dr3d/prethinker/blob/main/docs/DOMAIN_PROFILE_CATALOG.md)
- [docs/DOMAIN_BOOTSTRAPPING_META_MODE.md](https://github.com/dr3d/prethinker/blob/main/docs/DOMAIN_BOOTSTRAPPING_META_MODE.md)
- [docs/MULTI_PASS_SEMANTIC_COMPILER.md](https://github.com/dr3d/prethinker/blob/main/docs/MULTI_PASS_SEMANTIC_COMPILER.md)
- [docs/prompts/SEMANTIC_IR_V1.md](https://github.com/dr3d/prethinker/blob/main/docs/prompts/SEMANTIC_IR_V1.md)

Current query/QA instruments:

- [docs/CURRENT_HARNESS_INSTRUMENT.md](https://github.com/dr3d/prethinker/blob/main/docs/CURRENT_HARNESS_INSTRUMENT.md)

Secondary design notes:

- [docs/PRETHINKER.md](https://github.com/dr3d/prethinker/blob/main/docs/PRETHINKER.md)
- [ROADMAP.md](https://github.com/dr3d/prethinker/blob/main/ROADMAP.md)
- [docs/PROJECT_HORIZON.md](https://github.com/dr3d/prethinker/blob/main/docs/PROJECT_HORIZON.md)

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
rule/evidence/helper surfaces can rescue rows that need them, but global
activation can perturb rows that were already good. Perfect-selector reports
are diagnostic upper bounds, not runtime policies.

The newest boundary work starts from the completed guard-compression archive
and asks where the current system still blurs on unlike source shapes. The live
discipline is to classify boundary coordinates, design narrow probe fixtures,
and promote only repairs that can be described without fixture vocabulary and
replayed on unlike rows.

Clarification eagerness is now a named strategy surface, not just a UI behavior:
Prethinker should ask during ingestion when identity, temporal anchors,
correction targets, rule scope, or claim/fact boundaries block safe admission,
and should ask during query when the KB cannot answer without choosing a scope
for the user.

## Current Domain Lanes

The active domain-profile surface is documented through the profile catalog and
meta-bootstrap notes. Older per-domain smoke notes for medical/UMLS,
CourtListener, and SEC/contracts have been archived out of the front-door docs;
they remain recoverable through Git history and the local cold archive.

- [docs/DOMAIN_PROFILE_CATALOG.md](https://github.com/dr3d/prethinker/blob/main/docs/DOMAIN_PROFILE_CATALOG.md)
- [docs/DOMAIN_BOOTSTRAPPING_META_MODE.md](https://github.com/dr3d/prethinker/blob/main/docs/DOMAIN_BOOTSTRAPPING_META_MODE.md)

## Demo Surface

- [docs/EXPLAINER.md](https://github.com/dr3d/prethinker/blob/main/docs/EXPLAINER.md)
- [ui_gateway/README.md](https://github.com/dr3d/prethinker/blob/main/ui_gateway/README.md)

## Historical Or Legacy Context

Old generated HTML run reports, ladder/rung pages, dated prompt snapshots,
pre-mid-April media/results, legacy parser-lane notes, stale report manifests,
lab-automation plans, publishing plans, and public-benchmarking plans are retired from
the forward-facing tree. Git history preserves them. The older English-parser
lane is useful history, but it should not be mistaken for the preferred future
architecture centered on router-owned context engineering, Semantic IR
workspaces, and deterministic admission.

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

Latest local verification and current evidence live in
[PROJECT_STATE.md](https://github.com/dr3d/prethinker/blob/main/PROJECT_STATE.md)
and the focused docs linked above. Keep this page as a map, not a rolling
results ledger.

Important current signals:

- Multi-pass semantic compilation is the named frontier: independent semantic
  lenses propose backbone, support/source, temporal/status, and rule fragments;
  the mapper admits each lens independently; deterministic union accumulates
  only admitted clauses.
- Clarification eagerness has a dedicated fixture family for ask/no-ask,
  safe-partial preservation, blocked-slot coverage, unsafe candidates, and
  context-write hygiene.
- `active_profile=auto` uses `semantic_router_v1` as the first-pass
  context/profile planner. The old Python catalog selector is no longer in the
  active runtime or research harnesses.
- `semantic_ir_v1` includes optional `temporal_graph_v1` proposal diagnostics:
  event nodes, time anchors, intervals, and temporal edges are visible in
  traces, but they cannot write durable KB facts unless matching
  `candidate_operations` pass admission.
- Multilingual router/compiler probes remain the cleanest evidence for the
  no-Python-language-handling direction.
- Current profile packages supply router/compiler context, predicate contracts,
  and declarative validators for medical, legal/CourtListener, SEC/contracts,
  probate, and story-world lanes. The mapper still owns actual admission.

The remaining hard problems are model-owned segmentation, reusable
predicate-contract coverage, durable temporal fact representation and
graph-derived QA, rule admission, broader profile validator coverage, and mapper
policy for partial/unsafe operations.
