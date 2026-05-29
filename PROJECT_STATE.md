# Project State

Last updated: 2026-05-28

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

That compile-gate line is the historical overloaded pass/hold headline from
the native stamp. Current tooling also reports reason tiers. A 2026-05-28
rescore of the saved May 22 native compile artifacts reads `2 pass / 54 hold`
under the old headline, with `11` blocking-tier holds, `53` diagnostic-tier
holds, and `0` advisory holds. Treat the old pass/hold as a continuity metric;
future release claims should state whether blocking, diagnostic, and advisory
tiers are clean.

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
fresh ugly public 2026-05-28 R1:
  197 / 3 / 0 over 200 rows, 98.5% exact
  compile gate old pass/hold 2 / 6; blocking / diagnostic / advisory holds 4 / 6 / 0
fresh ugly public 2026-05-28 R2 targeted query-template replay:
  affected two-fixture slice moved 47 / 3 / 0 -> 50 / 0 / 0
  changed rows 3, improved 3, regressed 0, compatibility/runtime/write 0/0/0
fresh ugly public 2026-05-28 R2 full QA replay:
  198 / 2 / 0 over 200 rows, 99.0% exact
  changed rows 3, improved 2, regressed 1, regression guard failed
  compatibility/runtime/write 0/0/0
fresh ugly public 2026-05-28 R3 targeted variance probe:
  labor+SEC slice 49 / 1 / 0 over 50 rows
  changed rows 1, improved 1, regressed 0, regression guard passed
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

The May 28 fresh ugly line is a single fresh R1 compile+QA run over newly
landed public English official-document fixtures. Treat it as the strongest
current fresh-transfer thermometer. Its QA hygiene is clean, but its compile
gate is not release-clean.

The R2 targeted replay is mechanism evidence. The full R2 replay improved the
aggregate but was not a clean promotion because one previously exact row became
partial. The R3 targeted variance probe indicates that labor-board regression
was transient judge/classifier variance, while the SEC role-tenure row remains
an unresolved support gap with a provider-variance component.

Fresh fixture intake has a current cut-and-paste specification at
`docs/NEXT_FRESH_FIXTURE_REQUESTS_20260528.md`. The priority package is
now measured as above; the second package is `fresh_ach_stress_public_20260528_04`.

Durable real-world fixture inputs live under `datasets/real_world_transfer/`.
They are transfer evidence, not part of the native `datasets/story_worlds`
baseline.

The sealed unseen authored fixture inputs live at
`datasets/sealed_unseen/20260521`. They are useful transfer evidence, but they
should remain distinct from externally sourced real-world documents.

The current full-suite verification is:

```text
2009 passed, 2 subtests passed
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
- Treat fresh ugly 2026-05-28 R2 as the current product thermometer, with the
  row-churn caveat visible, and Batch 03 as a regression guard.
- Work remaining fresh ugly residue as generic role-tenure/source-display
  support, provider-variance, compile-gate, source-record, and
  authority-normalization mechanisms.
- Keep the May 22 native restamp as the current internal non-regression anchor
  until a new full native stamp is worth the cost.
- Use the tiered compile gate for new compile stamps: blocking reasons are
  release blockers, diagnostic reasons are instrument signals, and advisory
  reasons are low-risk notes. Preserve the old pass/hold headline for
  continuity, but do not collapse every diagnostic hold into release failure.
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

- OpenRouter is the default measured lane for stamps, transfer batches, and
  provider-variance investigations. Default hosted concurrency should stay
  around six lanes unless provider behavior changes.
- Local LM Studio on POWER remains useful for package/API development,
  one-row smoke tests, and small affected-set probes. It is not currently the
  default lane for broad compiles, QA batches, or release claims.
- Local LM Studio localhost should stay at or below four inference lanes for
  QA-scale work when used at all.
- POWER is the local workstation with the RTX 5090. Current Q8 LM Studio probes
  showed low GPU utilization, CPU-heavy prefill, and slower broad compile/QA
  economics than hosted lanes.
- Model-path metadata matters: provider/backend, quantization, loaded context,
  routing, and prompt packing are measurement conditions. See
  `docs/PROVIDER_RUNTIME_DISCIPLINE_NOTE.md`.
- Fresh package validation profiles live in
  `scripts/validate_fresh_ugly_batch.py`: use `--package-profile extended` for
  the next fresh ugly public package and `--package-profile ach` for the ACH
  stress package.
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

The public claim should be preserved with caveats intact. The three May 28 R1
partials produced one generic, query-only normalization repair. A full R2 replay
now reads `198 / 2 / 0` over `200` rows (`99.0%` exact), but because the
regression guard failed it should be described as improved measurement with
row-churn caveat, not as a clean promotion. Native QA remains `92.33%`.

Next energy:

1. inspect the remaining SEC role-tenure/source-display support row without
   teaching fixture words to the instrument;
2. decide whether future OpenRouter measurement should pin provider/quantization
   for stamp claims or explicitly report hosted-path variance bands;
3. keep inspecting compile-gate holds separately from QA exactness, especially
   blocking-tier holds that QA can still answer around;
4. validate and run `fresh_ach_stress_public_20260528_04` when the ACH lane
   needs a heldout sensitivity read;
5. use the tiered compile gate in future compile stamps and report old
   pass/hold separately from blocking/diagnostic/advisory tiers;
6. keep native restamp preparation warm, but do not spend it until the next
   change set is stable;
7. keep fixture language, row IDs, answer strings, and local source names out
   of active prompts, code, and public doctrine.
