# Project State

Last updated: 2026-05-19

## One-Sentence Shape

Prethinker compiles source documents into queryable symbolic knowledge bases,
then uses LLMs as planners over admitted state while deterministic gates decide
what can become durable truth.

## Current Center

- Runtime entrypoint: `src/mcp_server.py`, especially `process_utterance()`.
- Daily harness entrypoint: `scripts/run_kb_pipeline_clean_harness.py`, backed
  by `src/kb_pipeline_clean`.
- Current instrument brief: `docs/CURRENT_HARNESS_INSTRUMENT.md`.
- Public research headline: `docs/CURRENT_RESEARCH_HEADLINE.md`.
- Operating doctrine for high-context agents: `docs/CTO_ARCHITECTURE_BRIEF.md`.
- Public documentation map: `docs/PUBLIC_DOCS_GUIDE.md` and `docs/README.md`.
- Active architecture map: `docs/SEMANTIC_INSTRUMENT.md`.
- Active work map: `docs/ACTIVE_RESEARCH_LANES.md`.

Retired product/research lanes such as lab automation, public benchmarking,
publishing workflows, and guard-compression worksheets are no longer active
repo surfaces. Git history is the archive.

## Current Instrument State

The latest native direct-surface fixed-compile QA restamp is:

```text
2163 judged rows
1934 exact / 64 partial / 162 miss
89.41% exact
0 compatibility rows
0 runtime load errors
0 write proposal rows
```

The current full-suite verification after repo cleanup is:

```text
1449 passed, 2 subtests passed
```

These numbers are a measurement anchor, not a permanent claim. New repairs
should be judged by transfer-safe probes and then by a fresh stamp when the
instrument is otherwise stable.

## Current Architecture

```text
source document
  -> semantic compile passes
  -> deterministic mapper admission
  -> Prolog KB artifact package
  -> query planning over admitted state
  -> selector/guard choice among evidence surfaces
  -> judged answer row
```

The important boundary is source meaning versus durable truth:

- LLMs may propose predicates, rows, rules, query plans, and evidence bundles.
- Deterministic mappers admit only palette-valid, arity-valid, contract-valid
  operations.
- QA should answer from admitted KB state, deterministic ledgers, and runtime
  virtual predicates, not by re-reading source prose.
- Query-only diagnostics cannot authorize writes.
- Compatibility adapters are retired by default and should not appear in normal
  stamp runs.

## Active Research Pressure

The current center is not guard compression. It is pre-stamp hardening:

- Preserve direct compile surfaces so answer-bearing distinctions are emitted
  as queryable coordinates.
- Detect and reduce compile variance without tuning to fixture language.
- Keep source-fidelity surfaces clean: authority, status, temporal interval,
  provenance, lifecycle, assignment, rule, and epistemic distinctions should
  survive as typed rows.
- Audit recent vocabulary and invariants for fixture-language leakage.
- Keep public docs and agent-facing docs aligned with the current architecture.

The main stop condition before a full stamp is: no obvious transferable cleanup
remains except measuring the frozen instrument.

## Guardrails

- Do not let fixture nouns, QA answer strings, row ids, local people,
  organizations, or story-specific phrasing become architecture.
- Prefer unlike-document probes before promoting a new invariant.
- Treat a cold dataset result as measurement, not permission to tune to that
  dataset.
- Keep old work out of the public face unless it is still an active reference.
- If old context is needed, use git history or `C:\prethinker_tmp_archive`.

## Operating Notes

- OpenRouter is available for hosted lanes; default hosted concurrency should
  stay around six lanes unless provider behavior changes.
- POWER is the local workstation with the RTX 5090. It is useful but can be
  slower than hosted lanes for long compile batches.
- Use OpenAI-compatible structured output where possible.
- Keep run titles granular enough to distinguish compile versus QA and corpus
  or fixture group.

## Verification Commands

Common local checks:

```powershell
$env:PYTHONPATH='.'; pytest -q
python -m py_compile scripts\run_domain_bootstrap_file.py scripts\run_domain_bootstrap_qa.py
```

Before a public/docs cleanup commit, also run a stale-link grep over README,
agent docs, public docs, and active scripts for retired document names.

## Next Decision

Continue cleanup only while it removes stale public surfaces, fixture-shaped
vocabulary, or active prompt/config drift. Once those are quiet, the next real
move is a frozen native-corpus stamp.
