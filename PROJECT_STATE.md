# Project State

Last updated: 2026-05-26

## One-Sentence Shape

Prethinker compiles source documents into queryable symbolic knowledge bases,
then uses LLMs as language/intent planners over admitted state while
deterministic gates decide what can become durable truth.

## Current Center

- Runtime entrypoint: `src/mcp_server.py`, especially `process_utterance()`.
- Daily harness entrypoint: `scripts/run_kb_pipeline_clean_harness.py`, backed
  by `src/kb_pipeline_clean`.
- Public package facade: `prethinker.Engine` `0.5.0`, whose
  `compile_document()` returns and persists the semantic compiled artifact
  bundle contract. Default `compile_mode="ledger"` stays fast and local; opt-in
  `compile_mode="semantic"` calls an OpenAI-compatible endpoint and admits only
  source-record-anchored semantic candidates into `world.pl` / `epistemic.pl`.
- Current instrument brief: `docs/SEMANTIC_INSTRUMENT.md`.
- Public research headline: `docs/CURRENT_RESEARCH_HEADLINE.md`.
- Operating doctrine for high-context agents: `docs/CTO_ARCHITECTURE_BRIEF.md`.
- Public documentation map: `docs/PUBLIC_DOCS_GUIDE.md` and `docs/README.md`.
- Active architecture map: `docs/SEMANTIC_INSTRUMENT.md`.
- Active work map: `docs/ACTIVE_RESEARCH_LANES.md`.

Retired product/research lanes such as lab automation, public benchmarking,
publishing workflows, and guard-compression worksheets are no longer active
repo surfaces. Git history is the archive.

## Current Instrument State

The latest full native-corpus compile and QA stamp is:

```text
2163 judged rows
1997 exact / 46 partial / 120 miss
92.33% exact
0 compatibility rows
0 runtime load errors
0 write proposal rows
```

The matching compile stamp is:

```text
56 / 56 fixtures parsed
1383 candidate predicates
7814 compile admitted / 1106 skipped
7814 effective admitted / 1106 effective skipped
0 diagnostic rejected flat-pass skips
compile quality gate: 9 passed / 47 held
```

The latest native QA failure distribution is:

```text
compile-surface gap: 96
hybrid-join gap: 39
query-surface gap: 29
answer-surface gap: 1
judge-uncertain: 1
```

Current transfer anchors:

```text
fresh ugly public Batch 03 latest guarded slices:
  75 / 0 / 0 SEC
  216 / 6 / 3 non-SEC
  slice-combined 291 / 6 / 3 over 300 rows, 97.0% exact
real-world external four-fixture spotcheck: 160 / 0 / 0, 4 / 4 compile gates clean
sealed unseen authored transfer: 152 / 1 / 6 over 160 rows, 95.0% exact
NTSB two-document pilot transfer: 50 / 0 / 0 over 50 rows, 100.0% exact
earlier cold transfer baseline: 177 / 10 / 53 over 240 rows, 73.75% exact
```

The Batch 03 line is a slice-combined current view, not one single fresh
300-row rerun. The SEC subset is now clean under current code; the non-SEC
guard predates the later one-row ratio-calculation targeted replay. Treat
Batch 03 as current transfer/regression evidence, not as a benchmark claim.

Durable real-world fixture inputs live under `datasets/real_world_transfer/`.
They are transfer evidence, not part of the native `datasets/story_worlds`
baseline.

The sealed unseen authored fixture inputs live at
`datasets/sealed_unseen/20260521`. They are useful transfer evidence, but they
should remain distinct from externally sourced real-world documents.

The current full-suite verification is:

```text
1807 passed, 2 subtests passed
```

These numbers are the current public measurement anchor, not a permanent
ceiling. New repairs should be judged by transfer-safe probes and then by a
fresh stamp when the instrument is otherwise stable.

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
- Query-side language understanding belongs in Semantic IR / structured
  `query_intents[]`, not in Python regex gates over raw user questions.
- QA should answer from admitted KB state, deterministic ledgers, and runtime
  virtual predicates, not by re-reading source prose.
- Query-only diagnostics cannot authorize writes.
- Compatibility adapters are retired by default and should not appear in normal
  stamp runs.

## Active Research Pressure

The current center is not guard compression. It is post-claim discipline:

- Preserve direct compile surfaces so answer-bearing distinctions remain
  queryable coordinates.
- Treat fresh ugly Batch 03 as a product thermometer and regression guard while
  asking new unseen documents to answer the generalization question.
- Work remaining Batch 03 blockers as generic source-record, query-surface,
  cross-document, and authority-normalization mechanisms.
- Keep the May 22 native restamp as the current internal non-regression anchor
  until a new full native stamp is worth the cost.
- Keep source-fidelity surfaces clean: authority, status, temporal interval,
  provenance, lifecycle, assignment, rule, and epistemic distinctions should
  survive as typed rows.
- Audit recent vocabulary and invariants for fixture-language leakage.
- Keep public docs and agent-facing docs aligned with the current architecture.

Current lab notes live in short, run-named worksheets when an active stamp or
repair lane needs them. Old worksheets are not front-door project state.

The stop condition before another full native stamp is: a change materially
touches compile behavior or query-surface policy and focused probes suggest it
should change corpus-level behavior. Do not burn a full stamp just to re-prove
the current public claim.

## Guardrails

- Do not let fixture nouns, QA answer strings, row ids, local people,
  organizations, or story-specific phrasing become architecture.
- Prefer unlike-document probes before promoting a new invariant.
- Treat a cold dataset result as measurement, not permission to tune to that
  dataset.
- Keep old work out of the public face unless it is still an active reference.
- If old context is needed, use git history or `C:\prethinker_tmp_archive`.

## Operating Notes

- Local LM Studio on POWER is the default target for product-adjacent API calls
  and ordinary development runs. Use `PRETHINKER_BASE_URL=http://127.0.0.1:1234`
  and `PRETHINKER_MODEL=qwen/qwen3.6-35b-a3b`.
- OpenRouter is available for explicit hosted lanes; default hosted concurrency
  should stay around six lanes unless provider behavior changes.
- Local LM Studio localhost should stay at or below four inference lanes for
  QA-scale work.
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

The public claim should be preserved with caveats intact. The next engineering
decision is whether the remaining Batch 03 residue points to new generic
mechanisms or to declared source/oracle limits. Treat that separately from
native QA accuracy: the native QA stamp remains `92.33%`, while fresh ugly
guarded slices currently sit at a slice-combined `291 / 6 / 3` over `300`
rows.

Next energy:

1. classify the remaining Batch 03 non-exacts into repairable mechanisms versus
   external-evidence limits;
2. run fresh ugly documents when a mechanism batch needs an unseen thermometer;
3. keep native restamp preparation warm, but do not spend it until the next
   change set is stable;
4. keep fixture language, row IDs, answer strings, and local source names out
   of active prompts, code, and public doctrine.
