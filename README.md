# Prethinker

![Semantic Lenses Plain Guide](docs/assets/semantic-lenses-plain-guide.png)

**A governed write layer between natural language and a deterministic knowledge base.**

Prethinker is a multi-lens semantic compile and governed QA system for turning
natural-language claims into auditable symbolic state.

The core bet is simple: **the model may propose, but deterministic code decides what becomes truth**. A capable LLM builds rich semantic workspaces and query plans from messy language; deterministic gates admit only operations that survive schema, predicate-contract, provenance, and consistency checks; the Prolog KB and audit summaries remain the durable state and measurement layers.

This is not "English to Prolog by vibes." It is a research workbench for controlled memory admission: how much semantic understanding can a strong model contribute while a deterministic runtime prevents unsafe writes, ambiguity collapse, and claim/fact confusion?

Current center: artifact-first semantic parallax over compiled KB packages. Prethinker compiles source material into governed `world.pl` / `epistemic.pl` state, then tests row-level QA encounters through measured lenses, deterministic source ledgers, direct compile surfaces, selectors, and guards. The live `ui_gateway` console still demonstrates the same authority boundary, but the active research work is now the harness learning which admitted surface to trust for each question without giving the model write authority or answer keys.

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
- [Domain tier strategy](https://github.com/dr3d/prethinker/blob/main/docs/DOMAIN_TIER_STRATEGY.md) - the current post-reset strategy: closed domain schemas, hard-clean gates, and visible trust tiers.
- [Active research lanes](https://github.com/dr3d/prethinker/blob/main/docs/ACTIVE_RESEARCH_LANES.md) - compact map of current work without worksheet sediment.
- [Public docs guide](https://github.com/dr3d/prethinker/blob/main/docs/PUBLIC_DOCS_GUIDE.md) - reading order for the docs that still describe the living project.
- [Compiled KB artifact package](https://github.com/dr3d/prethinker/blob/main/docs/COMPILED_KB_ARTIFACT_PACKAGE.md) - what a compiled document product contains and what Q&A may use.
- [QA instrument](https://github.com/dr3d/prethinker/blob/main/docs/QA_INSTRUMENT.md) - how governed QA uses LLM planning and judging inside deterministic constraints.
- [Overlay architecture](https://github.com/dr3d/prethinker/blob/main/docs/OVERLAY_ARCHITECTURE.md) - how ACH and future overlays read evidence without mutating KB truth.
- [Boundary probe method](https://github.com/dr3d/prethinker/blob/main/docs/BOUNDARY_PROBE_RESEARCH_METHOD.md) - how focused fixtures are designed without fixture-vocabulary leakage.
- [Project state](https://github.com/dr3d/prethinker/blob/main/PROJECT_STATE.md) - compact status snapshot for the repo as it sits now.

Historical scorecards and older public notes remain in Git history or are
marked in-place as pre-reset context. They are not current claim-bearing docs.

## Current Research Headline

Prethinker is in a **sign-clean reset**. Earlier high scores were useful
research signals, but they are no longer public claims because audits showed
that some answer delivery depended on prose/source-record routing,
question-shape routing, or judge-facing surface tokens.

The current claim-bearing floor is deliberately harsher:

```text
Current 8-fixture English batch, model-redacted hard-road floor

Product exact:                  88 / 200 = 44.0%
Typed-plan exact:               84 / 200 = 42.0%
Redaction-survived exact:       81 / 200 = 40.5%
Atom-shape-clean product exact: 84 / 200 = 42.0%
Hard-clean floor:               73 / 200 = 36.5%
```

That number is not the product ambition. It is the honest research floor for
the open general compiler after the old shortcuts are no longer allowed to
score. The current product-shaped direction is a closed domain schema: one
document family, a governed predicate pack, explicit omission/accountability,
typed-plan replay, redaction survival, atom-shape cleanliness, and visible
trust tiers.

The practical next target is not another broad public proclamation. It is a
domain pack that can show Tier 1 verified answers on a bounded document type,
with lower-trust general typed and RAG/retrieval fallbacks labeled instead of
blended into the score.

## Current State

Read [PROJECT_STATE.md](https://github.com/dr3d/prethinker/blob/main/PROJECT_STATE.md) first. It is the compact, current orientation document for the repo.

The short version:

- `process_utterance()` is the canonical live runtime entrypoint.
- The UI is a manual demonstration cockpit, not a marketing page.
- Source-document research is artifact-first: compile once, freeze the KB package, then run row-level QA, selector, direct-surface, and repair experiments against that package.
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
- Selector guard pressure is tracked as a design signal: the current guard surface has `5` active return sites that collapse into `4` semantic families with `0` unclassified reasons. The next discipline is merge and retire before parameterizing.

## Useful Entry Points

- [docs/DOMAIN_TIER_STRATEGY.md](https://github.com/dr3d/prethinker/blob/main/docs/DOMAIN_TIER_STRATEGY.md) - current post-reset strategy and trust-tier boundary.
- [docs/ACTIVE_RESEARCH_LANES.md](https://github.com/dr3d/prethinker/blob/main/docs/ACTIVE_RESEARCH_LANES.md) - current work map and reset readiness.
- [docs/DOMAIN_TIER_WORKSHEET.md](https://github.com/dr3d/prethinker/blob/main/docs/DOMAIN_TIER_WORKSHEET.md) - live lab notes for the domain-schema climb.
- [docs/PUBLIC_DOCS_GUIDE.md](https://github.com/dr3d/prethinker/blob/main/docs/PUBLIC_DOCS_GUIDE.md) - maintained public-doc reading map.
- [docs/BOUNDARY_PROBE_RESEARCH_METHOD.md](https://github.com/dr3d/prethinker/blob/main/docs/BOUNDARY_PROBE_RESEARCH_METHOD.md) - boundary-coordinate and transfer-safe fixture method.
- [docs/COMPILED_KB_ARTIFACT_PACKAGE.md](https://github.com/dr3d/prethinker/blob/main/docs/COMPILED_KB_ARTIFACT_PACKAGE.md) - current compiled-document product contract.
- [docs/QA_INSTRUMENT.md](https://github.com/dr3d/prethinker/blob/main/docs/QA_INSTRUMENT.md) - governed QA pipeline and failure-surface interpretation.
- [docs/OVERLAY_ARCHITECTURE.md](https://github.com/dr3d/prethinker/blob/main/docs/OVERLAY_ARCHITECTURE.md) - how ACH and future overlays read compiled evidence without mutating the KB.
- [AGENT-README.md](https://github.com/dr3d/prethinker/blob/main/AGENT-README.md) - fast onboarding for coding agents.
- [docs/SEMANTIC_IR_MAPPER_SPEC.md](https://github.com/dr3d/prethinker/blob/main/docs/SEMANTIC_IR_MAPPER_SPEC.md) - deterministic mapper/admission contract.
- [docs/DOMAIN_PROFILE_CATALOG.md](https://github.com/dr3d/prethinker/blob/main/docs/DOMAIN_PROFILE_CATALOG.md) - profile/skill-style context packages for domain-aware Semantic IR.
- [ui_gateway/README.md](https://github.com/dr3d/prethinker/blob/main/ui_gateway/README.md) - UI gateway notes.

## Run It

```powershell
python -m pytest -q
python ui_gateway/main.py
```

Open `http://127.0.0.1:8765` for the live console.

## Reproducibility Notes

The current full-suite verification headline is kept in
[PROJECT_STATE.md](https://github.com/dr3d/prethinker/blob/main/PROJECT_STATE.md).

Focused local verification for the newest compile-surface and source-record
work:

```powershell
python -m pytest -q
# 2009 passed, 2 subtests passed

python scripts\audit_active_instrument_leakage.py
# forbidden hits: 0
# warning hits: 0
```

Current high-signal evidence:

- Current 8-fixture English hard-road floor: product exact `88 / 200`
  (`44.0%`), typed-plan exact `84 / 200` (`42.0%`), redaction-survived
  exact `81 / 200` (`40.5%`), atom-shape-clean product exact `84 / 200`
  (`42.0%`), hard-clean floor `73 / 200` (`36.5%`).
- FDA warning-letter domain micro-fixture: the first domain-pack wedge is live
  under `datasets/compile_micro_fixtures/fda_warning_letter_domain_v1/`, with
  value-domain, atom-shape, omission/accountability, and carrier-contract gates
  being tested before any public product claim.
- Answer-judge governance now has null controls, redaction replay, and
  typed-plan replay so judge exact rate is not allowed to become the thesis
  metric by itself.
- Historical high-score runs remain in Git history and marked docs as
  calibration context. They are not current claim-bearing numbers after the
  sign-clean reset.

The UMLS Semantic Network and Metathesaurus-derived runtime assets are intentionally not committed because they depend on licensed source data. The public repo includes the builders, tests, docs, and profile code; outside reproduction of the UMLS lane requires obtaining the licensed UMLS files separately.

## Repository Hygiene

Large licensed or generated assets live under ignored local paths, especially `tmp/licensed/umls/2025AB/`. The repo should keep source code, compact docs, profiles, tests, and small durable fixtures. Do not commit full UMLS archives, extracted Metathesaurus tables, run dumps, caches, coverage HTML, or throwaway reports.

## About The Author

Prethinker is built by Scott Evernden (`dr3d`), a retired software engineer who has been working in and around the symbolic AI tradition since 1980.

Scott first encountered Prolog at Digital Equipment Corporation in 1980 and became DEC's internal evangelist for the language. A friend he turned onto Prolog, Peter Gabel, later founded Arity Corporation, one of the canonical commercial Prolog implementations of the PC era. Scott ported SB-Prolog to the Amiga in 1986, working at the level of the Warren Abstract Machine, and lived through the expert-systems winter as a working symbolic programmer.

His earlier career includes computer graphics work at MIT's Architecture Machine Group under Nicholas Negroponte, Fortran libraries for one of the earliest commercial color inkjet plotters at Applicon, graphics terminal software at DEC, and foundational architecture work as employee #6 at Applix, later acquired by Cognos and then IBM. He later worked at Network Integrity / LiveVault, acquired by Iron Mountain, and briefly came out of retirement in 2019 as a Principal AI Engineer at Cantina Consulting in Boston.

Prethinker is partly a return to older logic-programming instincts through the lens of modern local LLMs. The lesson behind the project is that inference engines can be sharp; knowledge acquisition and truth admission are where systems often fail. This project asks whether a strong neural model can help acquire meaning while durable truth stays behind an explicit symbolic gate.
