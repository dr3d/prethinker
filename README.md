# Prethinker

![Semantic Lenses Plain Guide](docs/assets/semantic-lenses-plain-guide.png)

**Status: research phase closeout, June 2026.**

Prethinker is a research instrument for testing whether an LLM can propose
typed facts from messy official documents while deterministic governance decides
what is allowed to become claim-bearing state.

This repo is not presenting a product, a general legal AI system, or a broad
question-answering benchmark. It is the culminating record of one research
phase: what survived after contaminated high-score measurements were reset and
the system was forced to prove typed derivation under strict gates.

## The Current Result

The narrow result is:

```text
Closed, lens-scoped predicate packs can stabilize recurring
official-document skeleton anatomy under strict governance.
```

The equally important boundary is:

```text
Open-ended substance, causal findings, dense interpretation, legal
proposition support, and unstable role semantics remain abstention or
future-research boundaries unless a compact domain layer reproduces on
unlike documents.
```

That is smaller than the earlier hoped-for 90%+ general QA story. It is also
more real. Earlier 80.5%, 92.33%, 95%, 98.5%, and 99%-looking numbers are
historical contamination evidence, not current accuracy claims. Some were
inflated by source/display prose routing, question-shape routing, model-prior
completion, or judge-facing answer tokens.

## Read First

1. [From Contaminated Scores to Governed Document Compilation](https://github.com/dr3d/prethinker/blob/main/docs/PUBLIC_TECHNICAL_NOTE_GOVERNED_DOCUMENT_COMPILATION.md) - the main closeout note.
2. [Closed Domain Predicate Packs Technical Note](https://github.com/dr3d/prethinker/blob/main/docs/CLOSED_DOMAIN_PREDICATE_PACKS_TECHNICAL_NOTE.md) - the phase result, gates, evidence, and non-claims.
3. [Project State](https://github.com/dr3d/prethinker/blob/main/PROJECT_STATE.md) - compact current orientation.
4. [Domain Pack Research Evidence](https://github.com/dr3d/prethinker/blob/main/docs/DOMAIN_PACK_RESEARCH_EVIDENCE.md) - retained artifact ledger and family-by-family evidence.
5. [Public Docs Guide](https://github.com/dr3d/prethinker/blob/main/docs/PUBLIC_DOCS_GUIDE.md) - short map of the docs that still describe the living result.

Generated status pages remain in `docs/` because the governance suite uses
them, but they are supporting evidence rather than a new work queue.

## What Was Learned

- AI-assisted measurement can optimize toward the visible score and move prose
  back into the instrument unless anti-contamination gates bite in the loop.
- Closed predicate domains improve stability for repeated official-document
  skeleton anatomy such as wrappers, identifiers, dates, citations, counts, and
  table-like slots.
- Strict governance travels better than recall. A model can stay inside the
  closed language while still missing expected typed facts.
- The hard boundary is substance: causal findings, legal proposition support,
  dense explanatory detail, and some role semantics did not become clean
  claim-bearing capabilities in this phase.
- `false_verified=0` is the correct north-star metric for legal-authority
  plumbing, but generic citation/quote/pin checking is an underlay, not a
  solved legal-domain pack.

## Claim-Bearing Gates

A domain-pack result is claim-bearing only when the named run satisfies the
relevant gates:

- closed profile registry;
- lens-scoped offered signatures;
- N>=3 same-condition compiles;
- support>=2 for supported expected facts;
- 0 supported forbidden facts;
- registered signatures only;
- atom-shape pass;
- lens-scope pass;
- carrier value-domain pass where applicable;
- no source-record prose matching;
- no query-text routing;
- no fixture vocabulary;
- no prose-shaped atoms in the winning path.

Targeted replays are mechanism evidence, not transfer claims. Composed
historical runs are diagnostic unless a fresh same-condition bundle reproduces
them.

## Evidence Snapshot

- **SEC Form 8-K skeletons:** useful skeleton-pack evidence, but no longer a
  pristine or model-independent anchor. Current standing cells are boundary-aware
  and lower than the old favorable runs.
- **FDA warning letters:** the richest case study. Skeleton and recurring
  regulatory anatomy transfer better than wrapper role semantics,
  context-dependent categories, response/detail value flesh, and other
  substance lanes.
- **NTSB investigations:** corroborates the same skeleton-vs-substance boundary:
  wrappers, chronology, vehicles, and conditions are easier than findings or
  probable-cause substance.
- **OSHA accident/inspection records:** a clean skeleton probe in retained
  fixtures, useful as corroboration rather than a broad OSHA product claim.

See [Domain Pack Research Evidence](https://github.com/dr3d/prethinker/blob/main/docs/DOMAIN_PACK_RESEARCH_EVIDENCE.md)
and [Current Compile-Fact QA Status](https://github.com/dr3d/prethinker/blob/main/docs/CURRENT_COMPILE_FACT_QA_STATUS.md)
for the detailed retained cells and caveats.

## What This Does Not Claim

- 90%+ general Prethinker QA accuracy is not a claim.
- Arbitrary-domain document understanding.
- Legal proposition-support verification.
- Product readiness.
- Self-serve schema induction.
- Model-independent compile recall.
- That LLM-judged exact-rate is claim-bearing without null controls.
- Old 80.5%, 92.33%, 95%, 98.5%, or 99%-looking numbers are not current
  accuracy figures.

## Repository Shape

- `src/` and `prethinker/` contain the research runtime, validators, overlays,
  and public package facade.
- `datasets/domain_profiles/` contains closed predicate profile registries.
- `datasets/compile_micro_fixtures/` contains compact typed micro-fixtures.
- `datasets/domain_pack_measurements/` contains retained compile-fact manifest
  inputs.
- `docs/` contains the closeout notes, generated status pages, and public docs
  index.
- `tmp/` is scratch space and should not be treated as a stable source of truth.
- `C:\prethinker_tmp_archive` holds local historical artifacts outside Git.

## Verification

Useful current checks:

```powershell
python scripts\run_current_research_governance.py --out-root tmp\current_research_governance
python scripts\audit_historical_score_claims.py
python scripts\audit_research_artifact_paths.py
python scripts\validate_domain_predicate_schema.py --root datasets\domain_profiles
python -m pytest -q
```

The governance runner regenerates and checks the status pages that remain in
`docs/`. Those generated pages are evidence artifacts, not instructions to keep
expanding the research indefinitely.

## About The Author

Prethinker is built by Scott Evernden (`dr3d`), a retired software engineer who
has worked in and around symbolic AI since 1980. The project is partly a return
to older logic-programming instincts through modern local LLMs: inference
engines can be sharp, but knowledge acquisition and truth admission are where
systems often fail.
