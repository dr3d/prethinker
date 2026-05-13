# Prethinker

![Semantic Lenses Plain Guide](docs/assets/semantic-lenses-plain-guide.png)

**A governed write layer between natural language and a deterministic knowledge base.**

Prethinker is a governed semantic-intake layer for turning natural-language claims into auditable symbolic state.

The core bet is simple: **the model may propose, but deterministic code decides what becomes truth**. A capable LLM builds a rich semantic workspace from messy language; the mapper admits only candidate operations that survive schema, predicate-contract, provenance, and consistency checks; the Prolog KB remains the durable state layer.

This is not "English to Prolog by vibes." It is a research workbench for controlled memory admission: how much semantic understanding can a strong model contribute while a deterministic runtime prevents unsafe writes, ambiguity collapse, and claim/fact confusion?

Current center: artifact-first semantic parallax over compiled KB packages. Prethinker compiles source material into governed `world.pl` / `epistemic.pl` state, then tests row-level QA encounters through a pegboard of measured lenses, selectors, guards, and helpers. The live `ui_gateway` console still demonstrates the same authority boundary, but the active research work is now the harness learning which semantic surface to trust for each question without giving the model write authority or answer keys.

```text
compiled KB = durable state
row = measured encounter with that state
selector = chooses the best encounter surface
guard = prevents a tempting wrong surface
verdict = records what happened
```

Longer horizon:

```text
known state = filled cells
degrees of freedom = constrained blanks
propagation = visible recomputation, not hidden belief
```

![Prethinker semantic IR workspace](docs/assets/prethinker-semantic-ir-workspace.png)

## Read First

- [Current research headline](https://github.com/dr3d/prethinker/blob/main/docs/CURRENT_RESEARCH_HEADLINE.md) - the latest compact lab note.
- [CTO architecture brief](https://github.com/dr3d/prethinker/blob/main/docs/CTO_ARCHITECTURE_BRIEF.md) - the current operating doctrine for new high-context collaborators.
- [Semantic instrument](https://github.com/dr3d/prethinker/blob/main/docs/SEMANTIC_INSTRUMENT.md) - the public guide to artifact-first orchestration, lens facets, selector guards, and uncertainty vocabulary.
- [Boundary hunt worksheet](https://github.com/dr3d/prethinker/blob/main/docs/BOUNDARY_HUNT_WORKSHEET.md) - the live workbench for wide-corpus boundary coordinates, probe backlog, and helper/source cleanup.
- [Dataset transfer worksheet](https://github.com/dr3d/prethinker/blob/main/docs/DATASET_TRANSFER_WORKSHEET.md) - external MRC/domain-transfer intake, first RACE smoke results, and transfer-pressure backlog.
- [The Twelve Lenses](https://github.com/dr3d/prethinker/blob/main/docs/TWELVE_LENSES_EXPLAINED.md) - plain-language explanation of the reader/control lenses and how they differ.
- [Multi-pass semantic compiler](https://github.com/dr3d/prethinker/blob/main/docs/MULTI_PASS_SEMANTIC_COMPILER.md) - semantic parallax, safe-surface accumulation, and rule-lens work.
- [Project state](https://github.com/dr3d/prethinker/blob/main/PROJECT_STATE.md) - compact status snapshot for the repo as it sits now.
- [Active research lanes](https://github.com/dr3d/prethinker/blob/main/docs/ACTIVE_RESEARCH_LANES.md) - how current GPU/research cycles are prioritized.
- [Current harness instrument](https://github.com/dr3d/prethinker/blob/main/docs/CURRENT_HARNESS_INSTRUMENT.md) - scorecards, selectors, risk gates, and repair queues.
- [Public docs guide](https://github.com/dr3d/prethinker/blob/main/docs/PUBLIC_DOCS_GUIDE.md) - reading order for deeper technical material.
- [Docs and evidence hub](https://dr3d.github.io/prethinker/) - public docs, current research map, and curated evidence.
- [Full design explainer](https://github.com/dr3d/prethinker/blob/main/docs/EXPLAINER.md) - the short conceptual tour.

## Current Research Headline

The active frontier is **row-gated semantic parallax**. One compile is one
viewpoint, and one broader prompt is rarely the answer. Prethinker now treats
each lens, registry scaffold, query helper, and selector policy as a measured
candidate surface over frozen artifacts.

Rows are not where truth lives. Truth lives in the compiled KB. A row is the
scored encounter where a question tests whether that state is present,
retrievable, and safe to answer from. The selector is the steering wheel; guards
are the rumble strips that stop tempting but wrong surfaces from winning.

The newest hard problem is no longer "can we add another lens?" It is where
the current semantic interior gets blurry on unlike source shapes. Guard
compression is archived; boundary hunt is active. The current work separates
compile-surface gaps from helper, selector, query, and answer-surface gaps, then
extends the system only with generic repairs that survive replay on unlike rows.

For the freshest orientation, read the
[current headline](https://github.com/dr3d/prethinker/blob/main/docs/CURRENT_RESEARCH_HEADLINE.md)
and then the
[boundary hunt worksheet](https://github.com/dr3d/prethinker/blob/main/docs/BOUNDARY_HUNT_WORKSHEET.md).
External transfer samples and RACE/CUAD-style dataset work are tracked in the
[dataset transfer worksheet](https://github.com/dr3d/prethinker/blob/main/docs/DATASET_TRANSFER_WORKSHEET.md).

## Current State

Read [PROJECT_STATE.md](https://github.com/dr3d/prethinker/blob/main/PROJECT_STATE.md) first. It is the compact, current orientation document for the repo.

The short version:

- `process_utterance()` is the canonical live runtime entrypoint.
- The UI is a manual demonstration cockpit, not a marketing page.
- Source-document research is artifact-first: compile once, freeze the KB package, then run row-level QA, selector, helper, and repair experiments against that package.
- `semantic_ir_v1` remains the live architecture pivot: stronger model semantics before deterministic admission.
- The console defaults to the current LM Studio `qwen/qwen3.6-35b-a3b` Semantic IR lane for manual research runs.
- `medical@v0` is the main bounded domain profile.
- UMLS is used as a bounded normalization and semantic-type bridge, not as a giant preloaded clinical encyclopedia.
- The active Semantic IR path passes `medical@v0` predicate contracts and compact UMLS concept context into the model input before deterministic admission.
- A thin profile roster now exposes skill-like domain packages such as `medical@v0`, `story_world@v0`, and `probate@v0`; only explicitly selected thick context affects the current Semantic IR pass.
- `active_profile=auto` now uses `semantic_router_v1` to select a cataloged profile per turn and load that profile's thick context/contracts into the Semantic IR call without granting write authority.
- `scripts/run_profile_bootstrap.py`, `scripts/run_domain_bootstrap_file.py`, and `scripts/run_profile_bootstrap_loop.py` are the current meta-profile experiments: the model proposes entity types, predicates, contracts, risks, intake passes, and starter cases for unfamiliar material; review loops and ordinary mapper admission decide whether the proposed surface is useful.
- `scripts/run_mixed_domain_agility.py` randomizes Goldilocks, Glitch, Ledger, Silverton, Harbor, CourtListener, SEC/contracts, and medical turns through `active_profile=auto` as a cross-domain agility pressure gauge.
- `legal_courtlistener@v0` and `adapters/courtlistener/` are the legal-source profile/adapter lane for claim/finding, citation, docket, role-scope, provenance, and identity-boundary experiments.
- `sec_contracts@v0` and `adapters/sec_edgar/` are the third large starter domain, aimed at obligations, conditions, temporal triggers, party roles, and filing/exhibit provenance.
- Epistemic Worlds v1 preserves projection-blocked and supported-but-skipped candidate writes as scoped diagnostics, without asserting them as global truth.
- The Prolog KB is the committed truth layer; model output remains provisional until the runtime admits it.
- Long story-like utterances can now be segmented into focused Semantic IR passes so narrative ingestion stays inspectable instead of relying on one summary-shaped model response.
- Historical reports, old prompt snapshots, and run logs were pruned from the forward-facing tree because Git already preserves them.
- Selector guard pressure is tracked as a design signal: the current guard surface has many explicit return sites, but they still collapse into `7` semantic families with `0` unclassified reasons. The next discipline is merge and retire before parameterizing.

## Useful Entry Points

- [docs/EXPLAINER.md](https://github.com/dr3d/prethinker/blob/main/docs/EXPLAINER.md) - what Prethinker is and why the authority boundary matters.
- [Docs hub](https://dr3d.github.io/prethinker/) - GitHub Pages index for public docs and evidence.
- [PROJECT_STATE.md](https://github.com/dr3d/prethinker/blob/main/PROJECT_STATE.md) - current architecture, demo status, and next frontiers.
- [docs/CURRENT_HARNESS_INSTRUMENT.md](https://github.com/dr3d/prethinker/blob/main/docs/CURRENT_HARNESS_INSTRUMENT.md) - current harness/instrument machinery for scorecards, selector comparison, and repair queues.
- [docs/CURRENT_RESEARCH_HEADLINE.md](https://github.com/dr3d/prethinker/blob/main/docs/CURRENT_RESEARCH_HEADLINE.md) - current research headline and newest public framing.
- [docs/BOUNDARY_HUNT_WORKSHEET.md](https://github.com/dr3d/prethinker/blob/main/docs/BOUNDARY_HUNT_WORKSHEET.md) - live CTO workbench for boundary coordinates and transferable repairs.
- [docs/DATASET_TRANSFER_WORKSHEET.md](https://github.com/dr3d/prethinker/blob/main/docs/DATASET_TRANSFER_WORKSHEET.md) - external dataset intake and transfer smoke evidence.
- [docs/SEMANTIC_INSTRUMENT.md](https://github.com/dr3d/prethinker/blob/main/docs/SEMANTIC_INSTRUMENT.md) - public instrument spec for lenses, guards, uncertainty states, and calibration evidence.
- [docs/TWELVE_LENSES_EXPLAINED.md](https://github.com/dr3d/prethinker/blob/main/docs/TWELVE_LENSES_EXPLAINED.md) - plain-language explanation of the twelve reader/control lenses.
- [docs/MULTI_PASS_SEMANTIC_COMPILER.md](https://github.com/dr3d/prethinker/blob/main/docs/MULTI_PASS_SEMANTIC_COMPILER.md) - semantic parallax and safe-surface accumulation.
- [docs/CLARIFICATION_EAGERNESS_STRATEGY.md](https://github.com/dr3d/prethinker/blob/main/docs/CLARIFICATION_EAGERNESS_STRATEGY.md) - ingestion/query clarification policy and the CE Trap fixture.
- [AGENT-README.md](https://github.com/dr3d/prethinker/blob/main/AGENT-README.md) - fast onboarding for coding agents.
- [docs/CURRENT_UTTERANCE_PIPELINE.md](https://github.com/dr3d/prethinker/blob/main/docs/CURRENT_UTTERANCE_PIPELINE.md) - current domain-aware, recent-context, KB-seeded utterance path.
- [docs/PUBLIC_DOCS_GUIDE.md](https://github.com/dr3d/prethinker/blob/main/docs/PUBLIC_DOCS_GUIDE.md) - current public-doc reading map.
- [docs/SEMANTIC_IR_MAPPER_SPEC.md](https://github.com/dr3d/prethinker/blob/main/docs/SEMANTIC_IR_MAPPER_SPEC.md) - deterministic mapper/admission contract.
- [docs/DOMAIN_PROFILE_CATALOG.md](https://github.com/dr3d/prethinker/blob/main/docs/DOMAIN_PROFILE_CATALOG.md) - profile/skill-style context packages for domain-aware Semantic IR.
- [docs/DOMAIN_BOOTSTRAPPING_META_MODE.md](https://github.com/dr3d/prethinker/blob/main/docs/DOMAIN_BOOTSTRAPPING_META_MODE.md) - hint-free predicate/profile discovery from representative text or raw documents.
- [docs/COURTLISTENER_DOMAIN.md](https://github.com/dr3d/prethinker/blob/main/docs/COURTLISTENER_DOMAIN.md) - CourtListener legal-source domain notes and first smoke findings.
- [docs/SEC_CONTRACTS_DOMAIN.md](https://github.com/dr3d/prethinker/blob/main/docs/SEC_CONTRACTS_DOMAIN.md) - SEC/contracts domain notes and first smoke findings.
- [docs/UMLS_MVP.md](https://github.com/dr3d/prethinker/blob/main/docs/UMLS_MVP.md) - UMLS bridge and Semantic Network work.
- [docs/MEDICAL_PROFILE.md](https://github.com/dr3d/prethinker/blob/main/docs/MEDICAL_PROFILE.md) - bounded medical profile.
- [ui_gateway/README.md](https://github.com/dr3d/prethinker/blob/main/ui_gateway/README.md) - UI gateway notes.

## Run It

```powershell
python -m pytest -q
python ui_gateway/main.py
```

Open `http://127.0.0.1:8765` for the live console.

## Reproducibility Notes

The latest full local verification after the retired-lane cleanup is:

```powershell
python -m pytest
# 996 passed, 2 subtests passed
```

Current focused local verification for the newest helper/guard work:

```powershell
python -m pytest tests\test_domain_bootstrap_file.py tests\test_domain_bootstrap_qa.py tests\test_qa_mode_selector.py tests\test_selector_guard_families.py -q
# 428 passed
```

Current high-signal evidence:

- Semantic IR edge runtime A/B: `20/20` decision labels, `0.976` average score, `0` non-mapper parse rescues.
- Weak-edge pass: `10/10` decision labels, `1.000` average score.
- Multilingual router probe: `10/10` router choices and `10/10` compiler JSON on raw Spanish, French, German, Portuguese, Italian, Japanese, and code-switched turns.
- Profile-owned predicate aliases now canonicalize candidate-operation predicate surfaces before palette admission, with an audit trail such as `dad_of/2 -> parent/2`; this is registry/context authority, not Python prose parsing.
- Policy/reimbursement cross-turn demo: English policy installed executable rules, derived query answers without writing derived `violation/2` facts, then corrected state and changed the answer.
- Anaplan Polaris enterprise-guidance fixture: multi-support safe-surface accumulation reached `42 exact / 1 partial / 0 miss` on a 43-question post-ingestion QA battery, with `0` runtime load errors and `0` QA write proposals.
- Sable Creek Budget rule replay: a narrow rule lens plus admitted-fact signature support produced the first fresh-fixture promotion-ready public-hearing rule without gold KBs, answer keys, or Python prose interpretation.
- Avalon Grant Committee rule replay: mapper-side rule gates skip raw Prolog negation/disjunction/comparison constructs, while helper-composed matching-fund rules remain promotion-ready; post-gate rule union reached `27 exact / 10 partial / 3 miss`.
- Clarification Eagerness source-context regression check: `40/40` correct, `0` unsafe candidates, `0` context-write violations, and `10/10` blocked-slot coverage after the rule-admission changes.
- Cold generalization evidence: the 2026-05-07 sealed 10-fixture story batch has a row-gated high-water of `361 exact / 16 partial / 23 miss` across `400` QA rows (`90.25%`), with zero QA write proposals in the contributing runs.
- Incoming-6 full-40 evidence: six new 2026-05-08 fixtures moved from a cold baseline of `186 / 16 / 38` to a diagnostic row-gated high-water of `240 / 0 / 0` over `240` rows. This proves reachable surfaces, not one global compiler; the new row shapes remain selector-scoped until unlike transfer checks prove them.
- Selector guard family rollup: `5` active guard return sites, `5` unique reasons, `4` semantic families, `0` unclassified reasons. The companion ledger preserves the retired/scar history.
- Temporal kernel slice: admitted `before/2` facts now support deterministic `after/2`, transitive `precedes/2`, and `follows/2` queries through Prolog rules; `temporal_graph_v1` remains proposal-only unless matching candidate operations pass admission.
- Temporal correction guard: replacement `event_on/2`, `interval_start/2`, and `interval_end/2` anchors are blocked unless the model emits an explicit retract/correction plan.
- Historical Lava stress packs remain under `docs/data/frontier_packs/` as calibration evidence, but they are no longer treated as the active research frontier.

The UMLS Semantic Network and Metathesaurus-derived runtime assets are intentionally not committed because they depend on licensed source data. The public repo includes the builders, tests, docs, and profile code; outside reproduction of the UMLS lane requires obtaining the licensed UMLS files separately.

## Repository Hygiene

Large licensed or generated assets live under ignored local paths, especially `tmp/licensed/umls/2025AB/`. The repo should keep source code, compact docs, profiles, tests, and small durable fixtures. Do not commit full UMLS archives, extracted Metathesaurus tables, run dumps, caches, coverage HTML, or throwaway reports.

## About The Author

Prethinker is built by Scott Evernden (`dr3d`), a retired software engineer who has been working in and around the symbolic AI tradition since 1980.

Scott first encountered Prolog at Digital Equipment Corporation in 1980 and became DEC's internal evangelist for the language. A friend he turned onto Prolog, Peter Gabel, later founded Arity Corporation, one of the canonical commercial Prolog implementations of the PC era. Scott ported SB-Prolog to the Amiga in 1986, working at the level of the Warren Abstract Machine, and lived through the expert-systems winter as a working symbolic programmer.

His earlier career includes computer graphics work at MIT's Architecture Machine Group under Nicholas Negroponte, Fortran libraries for one of the earliest commercial color inkjet plotters at Applicon, graphics terminal software at DEC, and foundational architecture work as employee #6 at Applix, later acquired by Cognos and then IBM. He later worked at Network Integrity / LiveVault, acquired by Iron Mountain, and briefly came out of retirement in 2019 as a Principal AI Engineer at Cantina Consulting in Boston.

Prethinker is partly a return to older logic-programming instincts through the lens of modern local LLMs. The lesson behind the project is that inference engines can be sharp; knowledge acquisition and truth admission are where systems often fail. This project asks whether a strong neural model can help acquire meaning while durable truth stays behind an explicit symbolic gate.
