# Native Restamp Worksheet

This worksheet tracks the 2026-05-22 native-corpus restamp. It is a lab note,
not project history state.

## 2026-05-22 Preflight

Baseline comparison target:

- QA summary: `C:\prethinker_tmp_archive\tmp_unload_20260521_2106\native_corpus_full_qa_stamp_20260520_openrouter6_summary.json`
- Compile summary: `C:\prethinker_tmp_archive\tmp_unload_20260521_2106\native_corpus_full_compile_stamp_20260520_summary.json`
- Corpus: same 56 `datasets/story_worlds` fixture names as the 2026-05-20 native stamp.
- Dataset git drift check: `git diff --name-only -- datasets/story_worlds datasets/clarification_eagerness datasets/enterprise_guidance` returned no paths.
- Current 56-fixture hash manifest: `C:\prethinker_tmp_archive\tmp_hot_artifacts_unload_20260522\native_corpus_stamp_20260522_fixture_manifest.json`

Comparability note:

- The current preflight confirms same fixture names and no dataset drift in git.
- No prior per-file hash manifest was found, so the strict claim is not
  "proven byte-identical to the prior stamp"; it is "same 56 named fixtures,
  current canonical dataset files unmodified by git."

Provider/model conditions:

- Provider path: OpenRouter-compatible API via `PRETHINKER_BASE_URL`.
- Model: `qwen/qwen3.6-35b-a3b`.
- Prior native compile lanes: `6`.
- Prior native QA lanes: `6`.

Baseline QA:

- Rows: `2163`
- Exact / partial / miss: `1971 / 64 / 127`
- Exact rate: `91.12%`
- Compatibility rows: `0`
- Runtime load errors: `0`
- Write proposal rows: `0`

Baseline failure-surface distribution:

- compile-surface gap: `116`
- hybrid-join gap: `47`
- query-surface gap: `20`
- answer-surface gap: `5`
- judge-uncertain: `4`

Baseline compile gate:

- Parsed fixtures: `56 / 56`
- Candidate predicates: `1380`
- Compile admitted / skipped: `8198 / 991`
- Effective admitted / skipped: `8198 / 863`
- Diagnostic rejected flat-pass skips: `128`
- Quality gate: `26 pass / 30 hold`

Success bands, fixed before running:

- Clean: exact rate at or above `91.12%`, compatibility rows `0`, and no
  materially worse failure-surface distribution.
- Neutral: `90.6%` to `91.5%` exact with similar failure-surface shape and
  compatibility rows `0`.
- Concerning: below `90.6%`, compatibility rows not `0`, compile failures, or
  a meaningfully different failure-surface distribution even if the headline
  score is similar.

Post-stamp protocol:

- Clean: publish the native + external transfer evidence as a current claim.
- Neutral: publish with an explicit note that native is roughly neutral while
  transfer improved.
- Concerning: do not publish; investigate named drift and restamp after repair.

Stamp discipline:

- Do not repair mid-stamp.
- If a fixture compile fails outright, record it as a failed fixture and keep
  moving.
- Real-world fixtures currently in `tmp` stay transfer evidence and are not
  mixed into the native corpus.

## 2026-05-22 Compile Stamp

Command shape:

- Script: `scripts\run_domain_bootstrap_file_batch.py`
- Dataset root: `datasets\story_worlds`
- Output root: `C:\prethinker_tmp_archive\tmp_hot_artifacts_unload_20260522\native_corpus_full_compile_stamp_20260522_current`
- Summary JSON: `C:\prethinker_tmp_archive\tmp_hot_artifacts_unload_20260522\native_corpus_full_compile_stamp_20260522_current_summary.json`
- Summary MD: `C:\prethinker_tmp_archive\tmp_hot_artifacts_unload_20260522\native_corpus_full_compile_stamp_20260522_current_summary.md`
- Provider/model: OpenRouter, `qwen/qwen3.6-35b-a3b`
- Lanes: `6`
- Base timeout: `1200`
- Effective worker timeout: `7200`
- Flags: `--compile-source`, `--compile-flat-plus-plan-passes`,
  `--focused-pass-ops-schema`, `--source-record-ledger`,
  `--source-record-ledger-facts`, `--quality-gate`,
  `--quality-retry-on-hold`, `--quality-retry-max-attempts 2`

Outcome:

- Process result: completed without stderr and without fixture process failures.
- Fixtures: `56`
- Parsed OK: `56 / 56`
- Candidate predicates: `1383`
- Compile admitted / skipped: `7814 / 1106`
- Effective admitted / skipped: `7814 / 1106`
- Diagnostic rejected flat-pass skips: `0`
- Quality gate: `9 pass / 47 hold`

Comparison to 2026-05-20 compile baseline:

- Candidate predicates: `1380 -> 1383`
- Compile admitted / skipped: `8198 / 991 -> 7814 / 1106`
- Effective admitted / skipped: `8198 / 863 -> 7814 / 1106`
- Diagnostic rejected flat-pass skips: `128 -> 0`
- Quality gate: `26 pass / 30 hold -> 9 pass / 47 hold`

Initial read before QA:

- The compile run is operationally valid: all fixtures parsed and all processes
  returned `0`.
- The gate distribution shifted materially stricter/worse, mostly around
  source-claim, source-authority, vote-tally, quantity, and coexistence delivery
  flags. Treat this as concerning unless QA shows the held surfaces are mostly
  non-answer-bearing for the native questions.

## 2026-05-22 QA Stamp

Command shape:

- Script: `scripts\run_domain_bootstrap_qa_batch.py`
- Dataset root: `datasets\story_worlds`
- Compile root: `C:\prethinker_tmp_archive\tmp_hot_artifacts_unload_20260522\native_corpus_full_compile_stamp_20260522_current`
- Output root: `C:\prethinker_tmp_archive\tmp_hot_artifacts_unload_20260522\native_corpus_full_qa_stamp_20260522_openrouter6`
- Summary JSON: `C:\prethinker_tmp_archive\tmp_hot_artifacts_unload_20260522\native_corpus_full_qa_stamp_20260522_openrouter6_summary.json`
- Summary MD: `C:\prethinker_tmp_archive\tmp_hot_artifacts_unload_20260522\native_corpus_full_qa_stamp_20260522_openrouter6_summary.md`
- Provider/model: OpenRouter, `qwen/qwen3.6-35b-a3b`
- Lanes: `6`
- Base timeout: `420`
- Effective per-call timeout: `2520`
- Flags: `--no-cache`, reference-answer judging, failure-surface
  classification, evidence bundle plan/execute/context filter,
  compatibility adapter row limit `0`

Outcome:

- Process result: completed without stderr and without fixture process failures.
- Questions: `2163`
- Exact / partial / miss: `1997 / 46 / 120`
- Exact rate: `92.33%`
- Compatibility rows: `0`
- Runtime load errors: `0`
- Write proposal rows: `0`

Comparison to 2026-05-20 QA baseline:

- Exact / partial / miss: `1971 / 64 / 127 -> 1997 / 46 / 120`
- Exact rate: `91.12% -> 92.33%`
- Exact row delta: `+26`
- Partial row delta: `-18`
- Miss row delta: `-7`
- Compatibility rows: `0 -> 0`
- Runtime load errors: `0 -> 0`
- Write proposal rows: `0 -> 0`

Failure-surface distribution:

- Compile-surface gap: `116 -> 96`
- Hybrid-join gap: `47 -> 39`
- Query-surface gap: `20 -> 29`
- Answer-surface gap: `5 -> 1`
- Judge-uncertain: `4 -> 1`

Lowest current fixture scores:

- `thornfield_variance`: `30 / 3 / 7`, exact rate `75.0%`
- `ridgeline_fire`: `31 / 2 / 7`, exact rate `77.5%`
- `sable_creek_budget`: `31 / 6 / 3`, exact rate `77.5%`
- `black_lantern_maze`: `33 / 1 / 6`, exact rate `82.5%`
- `oxalis_recall`: `33 / 3 / 4`, exact rate `82.5%`

Largest fixture regressions vs 2026-05-20:

- `black_lantern_maze`: `40 / 0 / 0 -> 33 / 1 / 6`
- `fenmore_seedbank`: `24 / 0 / 1 -> 21 / 0 / 4`
- `identifier_ledger_torture`: `40 / 0 / 0 -> 36 / 2 / 2`
- `lantern_school_field_trip`: `40 / 0 / 0 -> 37 / 0 / 3`
- `tournament_borrowed_names`: `38 / 1 / 1 -> 35 / 1 / 4`

Largest fixture gains vs 2026-05-20:

- `dulse_ledger`: `28 / 5 / 7 -> 35 / 4 / 1`
- `veridia9_supply_chain_patent_dispute`: `32 / 4 / 4 -> 37 / 2 / 1`
- `wildfire_evacuation_revision_order`: `34 / 1 / 5 -> 38 / 1 / 1`
- `industrial_sensor_clock_correction`: `35 / 2 / 3 -> 39 / 0 / 1`
- `hospital_shift_exception_log`: `35 / 2 / 3 -> 39 / 0 / 1`

Stamp read:

- By the predeclared QA threshold, this is a clean native score: exact rate is
  above `91.12%`, compatibility rows are `0`, and failure distribution is not
  materially worse overall.
- The compile gate itself is not clean: `9 / 47` pass/hold is a large regression
  from `26 / 30`, even though held surfaces did not translate into worse native
  QA. Treat this as a gate calibration / compile-surface diagnostic blocker, not
  a native QA blocker.
- The sharpest current energy should go into the query-surface increase and the
  fixture regressions headed by `black_lantern_maze`, while using the gains in
  `dulse_ledger`, `veridia9_supply_chain_patent_dispute`, and
  `wildfire_evacuation_revision_order` as evidence that recent work did not
  merely overfit one lane.
