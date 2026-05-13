# Dataset Transfer Worksheet

Last updated: 2026-05-13

This worksheet tracks external-dataset transfer work. It is separate from
`BOUNDARY_HUNT_WORKSHEET.md` because the hunt worksheet is now the architecture
case archive; this file is the intake and transfer-pressure board.

## Doctrine

- External datasets are measurement pressure, not permission to tune on their
  surface vocabulary.
- Sample into `tmp/` by default. Do not bulk-store upstream datasets in the
  repo.
- Preserve answer isolation: source and questions can compile; oracle answers
  are scoring-only.
- A transfer failure becomes architecture only after it is described without
  dataset names, row ids, answer strings, local people, or local organizations.
- Prefer small, focused samples that isolate one pressure over large runs that
  only produce unlabeled residue.

## Intake Tooling

`scripts/sample_mrc_transfer_fixtures.py` samples RACE- and SQuAD-style machine reading
comprehension records into Prethinker incoming fixture shape:

```powershell
python scripts/sample_mrc_transfer_fixtures.py --dataset ehovy/race --config high --split validation --limit 5
```

Use `--sample-strategy even` for deterministic spread samples across a split.
For open-ended extractive QA, use SQuAD-style rows:

```powershell
python scripts/sample_mrc_transfer_fixtures.py --source-format squad --dataset squad --no-config --split validation --limit 5 --sample-strategy even
```

Output defaults to `tmp/mrc_transfer_samples`. Each sampled passage has:

- `source.md` with passage text and source metadata;
- `qa.md` with questions and multiple-choice options only;
- `oracle.jsonl` with the answer key for after-the-fact scoring;
- `fixture_notes.md` with transfer/doctrine reminders.

The repo also has a local `datasets/` directory, so the sampler explicitly
guards against importing that namespace when it needs HuggingFace's
`load_dataset`.

## Candidate Lanes

| Lane | Purpose | First Sample |
| --- | --- | --- |
| RACE | Within-English school-style comprehension transfer; closest known match to current fixture shape. | 50-100 passages after a 5-passage smoke test. |
| CUAD | Legal contract transfer; tests domain shift and section/authority assumptions. | 10-20 documents once a CUAD adapter exists. |
| DROP | Arithmetic and discrete-operation stress; likely to pressure recent aggregation/counterfactual repairs. | Small sample after RACE smoke. |
| MultiWikiQA / Belebele | Non-English surface-risk pressure. | 5-10 samples per language after adapter shape is settled. |

## Progress Journal

### DT-001 - RACE-Style Intake Sampler

Before:

- Prethinker had a staging path for incoming fixtures, but no small,
  repeatable way to sample standard external MRC datasets into that shape.
- The natural HuggingFace import path was ambiguous because the repo has a
  local `datasets/` directory.

Prediction:

- A narrow adapter can create clean transfer fixtures without adding new
  architecture or committing upstream dataset content.
- The first adapter should preserve the existing `qa.md + oracle.jsonl`
  isolation contract so later transfer runs use the same staging discipline as
  hand-authored fixtures.

Intervention:

- Added `scripts/sample_mrc_transfer_fixtures.py`.
- Added unit coverage for answer-key isolation and compatibility with
  `stage_incoming_fixtures.py`.

After:

- RACE-style records can be sampled from HuggingFace or local JSONL into
  `tmp/mrc_transfer_samples`.
- The generated fixtures can be staged by the existing intake script.
- A one-passage live RACE smoke sample from HuggingFace staged cleanly.

Artifacts:

- `scripts/sample_mrc_transfer_fixtures.py`
- `tests/test_sample_mrc_transfer_fixtures.py`
- Smoke sample:
  `tmp\mrc_transfer_samples_race_smoke\race_high_validation_00000_high5060_txt`

Verification:

- `python -m pytest tests/test_sample_mrc_transfer_fixtures.py tests/test_stage_incoming_fixtures.py -q`
  -> `7 passed`.
- `python scripts\sample_mrc_transfer_fixtures.py --dataset ehovy/race --config high --split validation --limit 1 --out-root tmp\mrc_transfer_samples_race_smoke`
  -> wrote `1` fixture.
- `python scripts\stage_incoming_fixtures.py --root tmp\mrc_transfer_samples_race_smoke --out-root tmp\mrc_transfer_staged_race_smoke`
  -> `1` staged, `0` failed.

Lesson:

- Transfer intake is its own boundary surface. The adapter should translate
  external dataset format into fixture shape, but must not translate dataset
  vocabulary into compiler or selector logic.

Next pressure:

- Run a 5-passage RACE sample as the first external transfer compile/QA
  candidate, then classify misses as transfer coordinates rather than tuning
  instructions.

### DT-002 - RACE Five-Passage Transfer Smoke

Before:

- The lab had strong internal and focused-probe evidence, but no fresh
  external MRC measurement in the current fixture shape.
- OpenRouter was expected to be the faster hosted lane, but prior wide runs
  showed provider throttling above six lanes.

Prediction:

- A tiny unseen RACE sample should expose whether the current architecture
  transfers to school-style comprehension prose without adding helpers or
  fixture vocabulary.
- Because RACE asks title/theme/false-option questions, some misses should be
  answer-surface or resolution gaps rather than ordinary selector failures.

Intervention:

- Sampled five RACE high-school validation passages into
  `tmp\mrc_transfer_samples_race5`.
- Staged them into `tmp\mrc_transfer_staged_race5`.
- Tried OpenRouter at five lanes and then one lane; both runs failed with
  provider `503`, so those were recorded as transport, not architecture.
- Ran local compile and QA using the same staged fixtures.

After:

- Staging: `5` fixtures staged, `0` failed.
- Compile: `5` fixtures compiled, `0` runner errors.
- QA: `15` questions, `7 exact / 2 partial / 6 miss`, exact rate `0.4667`.
- Runtime load errors: `0`.
- Write proposal rows: `0`.
- Helper rows: `0`.

Artifacts:

- Samples: `tmp\mrc_transfer_samples_race5`
- Staged fixtures: `tmp\mrc_transfer_staged_race5`
- Failed OpenRouter compile attempts:
  `tmp\mrc_transfer_compile_race5_20260513`,
  `tmp\mrc_transfer_compile_race5_retry1_20260513`
- Local compile: `tmp\mrc_transfer_compile_race5_local_20260513`
- Local QA: `tmp\mrc_transfer_qa_race5_local_20260513`

Verification:

- `python scripts\stage_incoming_fixtures.py --root tmp\mrc_transfer_samples_race5 --out-root tmp\mrc_transfer_staged_race5`
  -> `5` staged, `0` failed.
- `python scripts\run_domain_bootstrap_file_batch.py ... --summarize-existing`
  -> all `5` local compile artifacts parsed.
- `python scripts\run_domain_bootstrap_qa_batch.py ... --lanes 2`
  -> `15` questions, `7 / 2 / 6`.

Boundary coordinates:

- Formula application over an extracted rule: the source compiled a general
  numeric rule and one stated instance, but the QA layer did not resolve a new
  instance of that rule.
- Title/theme generation: the KB held supporting facts for a passage theme,
  but no surface mapped those facts to a title-like answer.
- False-option selection: the KB contained evidence refuting an option, but the
  QA layer treated the reference answer as content to support rather than the
  selected false statement.
- Comparative timeline resolution: one side of a comparison was compiled while
  the other side was missing or not queryable.
- Background/role fact absence: answer-bearing educational or audience role
  distinctions were not emitted as queryable coordinates.
- Implicit consequence/attitude: source evidence supported a stance, but not
  the answer's psychological consequence phrasing.

Lesson:

- RACE is a good unlike fixture family because it pressures more than factual
  lookup. It reveals a boundary between symbolic fact extraction and
  exam-style answer selection: title synthesis, option negation, rule
  application, and implicit audience/theme inference. Those are transfer
  coordinates, not permissions to tune on RACE wording.

Next pressure:

- Build a tiny focused probe for one transfer coordinate at a time, starting
  with false-option selection or rule-application over an extracted formula.
- Keep title/theme generation separate; it may be a deliberate out-of-scope
  answer-rendering class rather than a compiler repair.

### DT-003 - RACE-50 Transfer Measurement

Before:

- DT-002 showed `7 / 2 / 6` over only `15` RACE questions. That was enough to
  reveal new MRC-shaped boundary classes, but too small for repair decisions.
- OpenRouter had failed on the compile phase with provider `503`, so local
  compile remained the reliable source-reading lane.

Prediction:

- A 50-passage spread sample should stabilize whether the small RACE pack's
  boundary classes recur.
- The exact rate should move because 15 questions is a very wide confidence
  interval.
- Repairs should remain paused until recurrence is visible.

Intervention:

- Added deterministic spread sampling to
  `scripts/sample_mrc_transfer_fixtures.py`.
- Generated `25` middle-school and `25` high-school RACE validation passages
  with `--sample-strategy even`.
- Staged all `50` fixtures.
- Compiled locally at two lanes.
- Retried OpenRouter for QA. A two-fixture smoke passed, then full QA ran at
  six lanes.
- Added `scripts/summarize_mrc_transfer_qa.py` to make coordinate summaries
  repeatable.

After:

- Staging: `50` fixtures staged, `0` failed.
- Compile: `50` fixtures compiled, `0` runner errors.
- QA: `177` questions, `97 exact / 8 partial / 68 miss / 4 not judged`.
- Exact rate: `0.548`.
- Runtime load errors: `0`.
- Write proposal rows: `2`.
- Helper rows: `0`.

Artifacts:

- Samples: `tmp\mrc_transfer_samples_race50_20260513`
- Staged fixtures: `tmp\mrc_transfer_staged_race50_20260513`
- Local compile: `tmp\mrc_transfer_compile_race50_local_20260513`
- OpenRouter QA smoke: `tmp\mrc_transfer_qa_race50_or_smoke_20260513`
- OpenRouter QA: `tmp\mrc_transfer_qa_race50_or_20260513`
- Coordinate summary:
  `tmp\mrc_transfer_qa_race50_or_20260513\transfer_coordinate_summary.md`

Verification:

- `python -m pytest tests/test_sample_mrc_transfer_fixtures.py tests/test_stage_incoming_fixtures.py -q`
  -> `8 passed`.
- `python scripts\stage_incoming_fixtures.py --root tmp\mrc_transfer_samples_race50_20260513 --out-root tmp\mrc_transfer_staged_race50_20260513`
  -> `50` staged, `0` failed.
- `python scripts\run_domain_bootstrap_qa_batch.py ... --lanes 6 --base-url https://openrouter.ai/api/v1`
  -> `177` questions, `97 / 8 / 68`, `0` runtime load errors.
- `python scripts\summarize_mrc_transfer_qa.py --qa-root tmp\mrc_transfer_qa_race50_or_20260513`
  -> coordinate summary written.

Provisional transfer-coordinate counts:

- `direct_compile_surface_gap`: `23`
- `implicit_attitude_or_consequence`: `18`
- `background_role_or_audience_fact`: `14`
- `false_or_exception_option_selection`: `10`
- `title_theme_or_summary_answer`: `5`
- `comparative_or_temporal_resolution`: `4`
- `hybrid_join_resolution`: `2`
- `answer_surface_mapping`: `1`
- `formula_or_rule_application`: `1`
- `query_surface_resolution`: `1`
- `unclassified_transfer_coordinate`: `1`

Lesson:

- RACE-50 confirms that the small RACE sample was directionally right but
  score-noisy: exact rate rose from `0.4667` to `0.548`.
- The dominant new pressure is not helper volume; helper rows stayed at `0`.
  The boundary is mostly compile-surface resolution plus MRC-native answer
  behavior: attitude/consequence inference, role/audience facts,
  false/exception-option selection, and title/theme mapping.
- The `2` write-proposal rows are a safety signal. QA remained non-authoritative,
  but external MRC prompts can still tempt the answerer to propose missing facts.

Next pressure:

- Do not repair from this measurement alone.
- Manually audit a stratified sample from the top recurring coordinate classes,
  especially `direct_compile_surface_gap`,
  `implicit_attitude_or_consequence`, and
  `false_or_exception_option_selection`.
- Treat `title_theme_or_summary_answer` as likely answer-rendering/out-of-scope
  until it proves otherwise.

### DT-004 - RACE Option-Inline Audit and SQuAD Pivot

Before:

- DT-003 treated RACE as external transfer evidence, but manual audit began by
  reading the staged `qa.md` files rather than only the aggregate JSON.
- The top-three stratified audit was supposed to inspect recurring boundary
  classes before any repair.

Audit finding:

- The original RACE sampler wrote answer choices as indented lines under each
  question.
- `stage_incoming_fixtures.py` intentionally preserves only numbered question
  lines for markdown QA, so staged RACE questions lost their option choices.
- The `177`-question DT-003 run therefore measured open-ended questions, not
  the intended multiple-choice interface.

Intervention:

- Changed the RACE sampler to inline the option set into the numbered question
  line while still leaving the answer key isolated in `oracle.jsonl`.
- Re-ran RACE-50 QA using the same source compiles and corrected staged QA.
- Added SQuAD-style extractive-QA intake support to the sampler, because open
  ended QA is closer to Prethinker's target than multiple-choice exam
  selection.

After:

- Corrected RACE-50 with options inline:
  `177` questions, `133 exact / 4 partial / 40 miss`, exact rate `0.7514`.
- Runtime load errors: `0`.
- Write proposal rows: `0`.
- Helper rows: `0`.
- SQuAD smoke sample staged cleanly: `2` fixtures, `0` failed.

Artifacts:

- Corrected RACE samples:
  `tmp\mrc_transfer_samples_race50_options_20260513`
- Corrected staged RACE:
  `tmp\mrc_transfer_staged_race50_options_20260513`
- Corrected RACE QA:
  `tmp\mrc_transfer_qa_race50_options_or_20260513`
- Corrected coordinate summary:
  `tmp\mrc_transfer_qa_race50_options_or_20260513\transfer_coordinate_summary.md`
- SQuAD smoke:
  `tmp\mrc_transfer_samples_squad_smoke_20260513`,
  `tmp\mrc_transfer_staged_squad_smoke_20260513`

Verification:

- `python -m pytest tests/test_sample_mrc_transfer_fixtures.py tests/test_summarize_mrc_transfer_qa.py tests/test_stage_incoming_fixtures.py -q`
  -> `13 passed`.
- `python scripts\summarize_mrc_transfer_qa.py --qa-root tmp\mrc_transfer_qa_race50_options_or_20260513`
  -> `133 / 4 / 40 / 0`.

Lesson:

- The first manual audit did exactly what it should: it caught a measurement
  interface bug before any repair work started. RACE remains useful as a
  multiple-choice stressor, but the option interface itself is a benchmark
  shape. Prethinker's cleaner transfer target is open-ended extractive QA.

Next pressure:

- Do not repair against RACE option-selection yet.
- Run a SQuAD-50 extractive QA measurement next, using the same source compile
  and QA machinery, then audit its top recurring classes.

### DT-005 - Proposition-Type Reclassification

Before:

- Corrected RACE-50 with inline options improved from `97 / 8 / 68 / 4`
  to `133 / 4 / 40 / 0` over the same `177` questions.
- The result showed that selection among known choices is mostly compatible
  with the existing KB-evaluation machinery.
- The remaining `44` not-exact rows should not be classified by RACE-specific
  exam categories or by open-ended-versus-multiple-choice format.

Prediction:

- QA format is an interface. Proposition type is the substrate pressure.
- The cross-dataset categories should be defined before classification, or
  the audit will drift toward corpus-specific labels.

Operational taxonomy:

- `factual`: answer is a directly stated event, entity, attribute, value,
  location, or relation; no comparison, category choice, synthesis, or
  unstated mental/causal inference is required.
- `comparative`: answer requires ordering, contrast, arithmetic, duration,
  count, date, threshold, before/after, more/less, first/last, or another
  relation among two or more extracted facts.
- `categorical`: answer selects or maps an extracted fact to a type, role,
  class, label, meaning, audience, object kind, or option category.
- `synthesis`: answer condenses multiple facts into a title, theme, main
  idea, passage purpose, summary, rhetorical point, or best overall
  description.
- `inference`: answer depends on an unstated consequence, attitude,
  motivation, belief, intent, cause, implication, or reader conclusion
  licensed by evidence.

Intervention:

- Added proposition-type criteria and classifier output to
  `scripts/summarize_mrc_transfer_qa.py`.
- Preserved the older transfer-coordinate labels as a secondary view, because
  those still help locate compile/query/surface failure modes.
- Added focused unit tests for the five proposition types and boundary cases
  that should not over-fire: temporal anchors, generic `most`, intended
  audience, and emotional-state blanks.
- Regenerated the corrected RACE-50 coordinate summary.

After:

- Corrected RACE-50 remains `133 exact / 4 partial / 40 miss / 0 not judged`.
- Proposition-type split across the `44` not-exact rows:
  - `inference`: `22`
  - `factual`: `11`
  - `comparative`: `6`
  - `categorical`: `3`
  - `synthesis`: `2`
- Failure surfaces remain mostly compile-side:
  - `compile_surface_gap`: `38`
  - `hybrid_join_gap`: `4`
  - `query_surface_gap`: `2`

Manual stratified audit:

- `inference` is the dominant pressure. It includes emotional state,
  author/narrator opinion, causal explanation, purpose, knowledge state, and
  implied consequence. Some of these may be legitimate future compile surfaces,
  but a repair from RACE alone would risk teaching exam-inference style rather
  than source-fidelity.
- `factual` misses are not option-selection problems. They are mostly direct
  answer-bearing distinctions that the compile did not make queryable, such
  as a procedural action, a residence attribute, a publication/source genre,
  or a specific event-state. This is the cleanest candidate family for later
  transfer probes.
- `comparative` misses are compact and familiar: duration from a rule, family
  count, distance, time, commute count, and missing-money arithmetic. These
  look closest to the boundary-hunt arithmetic/join work, but RACE evidence is
  not yet enough to unify them with existing temporal/business arithmetic.
- `categorical` is small but useful: phrase meaning, intended audience, and
  person role. These are exactly the kind of trigger surfaces that need
  fixture-free audit before any helper grows.
- `synthesis` remains likely out of scope for core compile repair unless the
  source has an explicit title/theme/purpose surface. It should stay separate
  from fact extraction.

Artifacts:

- Corrected RACE QA:
  `tmp\mrc_transfer_qa_race50_options_or_20260513`
- Proposition summary:
  `tmp\mrc_transfer_qa_race50_options_or_20260513\transfer_coordinate_summary.md`
- JSON summary:
  `tmp\mrc_transfer_qa_race50_options_or_20260513\transfer_coordinate_summary.json`

Verification:

- `python -m pytest tests/test_summarize_mrc_transfer_qa.py tests/test_sample_mrc_transfer_fixtures.py tests/test_stage_incoming_fixtures.py -q`
  -> `24 passed`.
- `python scripts\summarize_mrc_transfer_qa.py --qa-root tmp\mrc_transfer_qa_race50_options_or_20260513`
  -> `133 / 4 / 40 / 0`.

Lesson:

- The RACE wrinkle was not multiple choice itself. With options visible,
  candidate selection mostly works. The remaining boundary is proposition
  type: inference, factual compile resolution, comparative joins, categorical
  mapping, and synthesis.
- This keeps the doctrine clean: do not repair because an option was missed;
  repair only when a proposition type recurs across unlike sources and can be
  expressed without dataset vocabulary.

Next pressure:

- Hold SQuAD until this taxonomy is used as a comparison lens.
- If continuing RACE, probe factual compile-resolution misses first, because
  they are closest to Prethinker's target and least likely to import exam
  inference.
- Keep inference and synthesis as scar categories unless unlike open-ended
  data shows source-faithful extraction surfaces, not just reader reasoning.

### DT-006 - Factual Compile-Resolution Probe

Before:

- DT-005 identified `11` factual not-exact rows in corrected RACE-50.
- These were the safest next pressure because they looked closest to
  Prethinker's target: direct answer-bearing facts missing from queryable
  compile surfaces.
- The hypothesis was that simple unlike factual surfaces might already be
  interior, while the RACE misses are denser surface-resolution cases.

Prediction:

- A small open-ended fixture with no multiple-choice interface should pass if
  the factual misses are mostly RACE density.
- If it fails, direct factual compile resolution still has a live boundary.
- Source-record ledger facts should help only if the issue is source-fidelity
  addressability, not fixture vocabulary.

Intervention:

- Added
  `experiments\boundary_probes\dataset_transfer_stage1\factual_compile_resolution_ladder`.
- The probe asks for direct factual surfaces: publication form, small-office
  attribute, demonstration method, travel pause, post-spill action, listed
  contaminants, Monday home presence, and counted-group arrival.
- Ran OpenRouter compile/QA once with the usual compile shape.
- Re-ran the same probe with generic `source_record_ledger` and
  `source_record_ledger_facts` enabled.

After:

- Baseline compile/QA:
  - Compile: parsed, `31` admitted facts, `16` candidate predicates.
  - QA: `4 exact / 0 partial / 4 miss`.
  - Misses: publication form, office size, Monday home presence, counted-group
    arrival.
- Source-record compile/QA:
  - Compile: parsed, `56` admitted facts, `13` candidate predicates.
  - QA: `7 exact / 0 partial / 1 miss`.
  - No helpers, no write proposals, no runtime load errors.

Artifacts:

- Probe fixture:
  `experiments\boundary_probes\dataset_transfer_stage1\factual_compile_resolution_ladder`
- Baseline compile:
  `tmp\boundary_probe_dataset_compile_stage1_factual_20260513`
- Baseline QA:
  `tmp\boundary_probe_dataset_qa_stage1_factual_20260513`
- Source-record compile:
  `tmp\boundary_probe_dataset_compile_stage2_factual_source_records_20260513`
- Source-record QA:
  `tmp\boundary_probe_dataset_qa_stage2_factual_source_records_20260513`

Verification:

- Baseline OpenRouter QA: `8` questions, `4 / 0 / 4`, `0` write proposals,
  helper rows `0`.
- Source-record OpenRouter QA: `8` questions, `7 / 0 / 1`, `0` write
  proposals, helper rows `0`.
- The generic fixture intake validator flags this probe because it expects
  `40`-row story-world fixtures; that check is not applicable to the small
  boundary-probe folder pattern.

Manual audit:

- The first compile admitted the action and list surfaces but dropped source
  identity, the simple adjective attribute, the Monday presence roster, and the
  counted-group arrival surface.
- Source-record facts recovered three of those four misses without any helper
  growth or fixture-specific predicate names. This supports the source-fidelity
  direction: direct factual transfer pressure often needs addressable source
  surfaces, not new answer logic.
- The remaining miss is not a pure compile absence. The compile contains
  `count(trainees_late, 10)` and `arrived_by(trainees_late, ferry_delay)`, but
  QA planned `performed_action(trainees_late, X, Y)`. That is a query-surface
  mismatch around event/state verbs, not a reason to add a trainee-specific
  helper.

Lesson:

- Factual transfer pressure split into two layers:
  source-fidelity addressability and query predicate selection.
- Source-record ledger facts are a general substrate, not a RACE repair, and
  they make unlike factual surfaces much more recoverable.
- The residual boundary is whether a question like "what did the counted group
  do" can use admitted state/event predicates such as arrival rows without
  requiring the compiler to duplicate every state as a performed action.

Next pressure:

- Replay a small slice of RACE factual misses with source-record ledger facts
  before changing code.
- Separately audit query planning for event/state answer predicates, using the
  residual counted-group arrival miss as a coordinate, not as vocabulary to
  encode.

### DT-007 - RACE Factual Source-Record Replay

Before:

- DT-006 showed that source-record ledger facts moved an unlike factual probe
  from `4 / 0 / 4` to `7 / 0 / 1`.
- That was useful but synthetic. The question was whether the same generic
  source-fidelity substrate transfers back to real corrected RACE factual
  misses.

Prediction:

- If source-record facts are the right repair shape, the factual not-exact
  coordinates should improve without helper rows, write proposals, or
  RACE-specific logic.
- If the improvement only appears on the synthetic probe, the factual misses
  remain unresolved density or dataset-specific pressure.

Intervention:

- Selected the `10` fixtures containing the `11` corrected RACE-50 factual
  not-exact rows.
- Recompiled those fixtures on OpenRouter at six lanes with
  `source_record_ledger` and `source_record_ledger_facts` enabled.
- Re-ran QA on the full `40` questions in that slice.
- Compared only the `11` previously non-exact factual coordinates for the
  transfer claim.

After:

- Slice QA with source records: `40` questions,
  `32 exact / 1 partial / 7 miss`, exact rate `0.8`.
- Runtime load errors: `0`.
- Write proposal rows: `0`.
- Helper rows: `0`.
- Targeted factual coordinates:
  - `11 / 11` improved.
  - `10` are now exact.
  - `1` moved from miss to partial.
  - `0` stayed flat or regressed.

Artifacts:

- Source-record compile replay:
  `tmp\mrc_transfer_compile_race_factual_source_records_20260513`
- Source-record QA replay:
  `tmp\mrc_transfer_qa_race_factual_source_records_20260513`
- Proposition summary:
  `tmp\mrc_transfer_qa_race_factual_source_records_20260513\transfer_coordinate_summary.md`

Targeted coordinate movement:

- Other-kids post-incident action: `miss -> exact`.
- Competitor demonstration method: `miss -> exact`.
- Ocean pollutant list: `partial -> exact`.
- Iceberg temporary stop: `miss -> partial`.
- Residence attribute/location: `miss -> exact`.
- Monday at-home state: `miss -> exact`.
- Promised destination: `miss -> exact`.
- Near-school commute group: `partial -> exact`.
- Ten-student late-arrival group: `miss -> exact`.
- 3D-game player action: `miss -> exact`.
- Passage publication genre: `miss -> exact`.

Lesson:

- This is the first strong transfer result for the dataset-transfer work:
  source-record facts improved every factual not-exact coordinate sampled from
  corrected RACE-50.
- The repair shape stays generic. It does not know RACE, option letters,
  fixture names, question ids, answer strings, or local story vocabulary. It
  improves source-fidelity addressability.
- The remaining non-exacts in the slice are no longer primarily factual
  compile-resolution misses; they include inference, synthesis, hybrid joins,
  and answer-surface issues. That supports the proposition-type framing.

Next pressure:

- Do not add a RACE-specific repair.
- Treat source-record ledger facts as a candidate default for dataset-transfer
  measurement, then replay a broader corrected RACE slice before claiming a
  general exact-rate lift.
- Keep the next architectural audit on query/answer surfaces that consume
  source-record facts cleanly, so source rows do not become a noisy substitute
  for actual compiled logic.

### DT-008 - Full RACE-50 Source-Record Replay

Before:

- DT-007 showed a targeted `10`-fixture factual slice improved when compiled
  with source-record ledger facts.
- That result was promising but could still be slice-shaped. The next question
  was whether source-record facts improve the full corrected RACE-50 transfer
  measurement without helper growth, write proposals, or dataset-specific
  predicates.
- The proposition-type taxonomy needed an explicit operational contract before
  using it for cross-dataset comparison.

Prediction:

- If source-record facts are general source-fidelity substrate, the full run
  should lift exact rate and reduce factual/direct compile-surface misses while
  preserving zero helper pressure.
- Some regressions are expected because the compile is LLM-produced and the
  source-record surface can change query planning; improvements must therefore
  be judged by aggregate movement and proposition type, not a single row.
- Inference and synthesis should remain boundary pressure rather than immediate
  repair targets.

Intervention:

- Recompiled the full corrected RACE-50 fixture set on OpenRouter at six lanes
  with `source_record_ledger` and `source_record_ledger_facts` enabled.
- Re-ran QA on the resulting compile artifacts.
- Updated `scripts\summarize_mrc_transfer_qa.py` so every MRC transfer summary
  carries explicit proposition-type criteria and precedence-ordered operational
  rules:
  synthesis, comparative, categorical, inference, factual.
- Regenerated transfer-coordinate summaries for both the corrected baseline and
  the source-record replay.

After:

- Baseline corrected RACE-50 QA:
  - `177` questions.
  - `133 exact / 4 partial / 40 miss`.
  - Exact rate `0.7514`.
  - Helper rows `0`; write proposal rows `0`; runtime load errors `0`.
- Full source-record RACE-50 QA:
  - `177` questions.
  - `147 exact / 5 partial / 25 miss`.
  - Exact rate `0.8305`.
  - Helper rows `0`; write proposal rows `0`; runtime load errors `0`.
- Full source-record compile:
  - `50 / 50` parsed.
  - `560` candidate predicates.
  - `2581` admitted facts.
  - `171` skipped facts.

Movement:

- Row-level movement across `177` questions:
  - `143` unchanged.
  - `25` improved.
  - `9` regressed.
- Improved rows by original proposition type:
  - `inference`: `12`
  - `factual`: `7`
  - `categorical`: `3`
  - `comparative`: `2`
  - `synthesis`: `1`
- Regressed rows by new proposition type:
  - `inference`: `4`
  - `factual`: `3`
  - `comparative`: `1`
  - `synthesis`: `1`
- Non-exact proposition-type shift:
  - `inference`: `22 -> 14`
  - `factual`: `11 -> 9`
  - `comparative`: `6 -> 5`
  - `categorical`: `3 -> 0`
  - `synthesis`: `2 -> 2`
- Non-exact coordinate shift:
  - `implicit_attitude_or_consequence`: `16 -> 9`
  - `direct_compile_surface_gap`: `14 -> 7`
  - `background_role_or_audience_fact`: `8 -> 5`
  - `comparative_or_temporal_resolution`: `2 -> 2`
  - `false_or_exception_option_selection`: `1 -> 3`
  - `hybrid_join_resolution`: `0 -> 1`
  - `formula_or_rule_application`: `1 -> 1`
  - `title_theme_or_summary_answer`: `1 -> 1`
  - `query_surface_resolution`: `1 -> 1`

Artifacts:

- Baseline corrected QA:
  `tmp\mrc_transfer_qa_race50_options_or_20260513`
- Baseline corrected coordinate summary:
  `tmp\mrc_transfer_qa_race50_options_or_20260513\transfer_coordinate_summary.md`
- Source-record compile:
  `tmp\mrc_transfer_compile_race50_source_records_20260513`
- Source-record QA:
  `tmp\mrc_transfer_qa_race50_source_records_20260513`
- Source-record coordinate summary:
  `tmp\mrc_transfer_qa_race50_source_records_20260513\transfer_coordinate_summary.md`

Verification:

- `python scripts\summarize_mrc_transfer_qa.py --qa-root tmp\mrc_transfer_qa_race50_options_or_20260513`
- `python scripts\summarize_mrc_transfer_qa.py --qa-root tmp\mrc_transfer_qa_race50_source_records_20260513`
- `python -m pytest tests\test_summarize_mrc_transfer_qa.py tests\test_sample_mrc_transfer_fixtures.py tests\test_stage_incoming_fixtures.py -q`
  - `25 passed`

Lesson:

- Source-record facts are now supported by both a synthetic unlike factual
  probe and a full RACE-50 replay. The effect is not small:
  `75.14% -> 83.05%` exact with no helper rows.
- The improvement is not limited to direct factual questions. Addressable
  source facts also helped inference and categorical rows because the answer
  layer could retrieve the evidence needed to evaluate options.
- This does not mean raw source rows should become the architecture's answer
  substitute. The regressions show that source-fidelity surfaces can perturb
  query planning and judgment. The clean direction is to make source records a
  measured dataset-transfer default while auditing the query/answer layer that
  consumes them.
- The taxonomy now has operational criteria before classification. Cross-dataset
  comparisons should report proposition type, not just MCQ versus open-ended
  format.

Next pressure:

- Manually audit the top remaining source-record non-exact classes:
  `implicit_attitude_or_consequence`, `comparative_or_temporal_resolution`, and
  `direct_compile_surface_gap`.
- Do not repair from RACE alone. A candidate repair needs the same proposition
  pressure to recur in unlike open-ended data or focused probes.
- Use source-record facts as the default for the next dataset-transfer
  measurement unless a run is specifically testing compile-only behavior.

### DT-009 - Source-Record Residue Manual Audit

Before:

- DT-008 left `30` non-exact rows after the full source-record replay.
- The initial top coordinate labels exposed a drift risk: ordinary
  `before`/`after` wording was being counted as comparative/temporal even when
  the proposition was emotion, purpose, or direct post-event action.
- After tightening the coordinate classifier, the top coordinate labels were:
  `implicit_attitude_or_consequence` (`9`),
  `direct_compile_surface_gap` (`7`), and
  `background_role_or_audience_fact` (`5`).
- Before any repair, those labels needed manual stratification so an automated
  coordinate name would not become architecture by accident.

Prediction:

- If a top coordinate class is coherent, it should describe one transferable
  repair pressure without relying on RACE passage vocabulary.
- If a class is mixed, the correct next move is better measurement or focused
  probes, not a broad helper/scoring change.

Intervention:

- Audited the source-record residue using the operational proposition taxonomy
  from DT-008.
- Treated the automated coordinate as a starting label only; proposition type
  and failure rationale decided whether the row belonged in a repair queue.
- Tightened `classify_transfer_coordinate()` so emotional, causal, and
  post-event action questions are not misclassified merely because their wording
  contains `before` or `after`.

After:

- `implicit_attitude_or_consequence` is coherent enough to track, but not yet
  safe to repair from RACE alone.
  - The source-record replay now has `9` such rows.
  - All `9` rows are inference propositions; `8` are compile-surface gaps and
    `1` is a hybrid-join gap around event-specific feeling.
  - The recurring shape is a semantic bridge from evidence to an unstated
    evaluative answer: attitude, purpose, trait, convenience, danger, or
    consequence.
  - This is the highest-value unlike-probe target, but also the highest leakage
    risk because MCQ answer labels can smuggle dataset-specific paraphrase
    mappings into the harness.
- `comparative_or_temporal_resolution` is now a much cleaner, smaller class.
  - It contains `2` true comparative join rows: route distance and missing-money
    arithmetic.
  - Keep it separate from emotional `before/after` wording and ordinary
    post-event action retrieval.
- `direct_compile_surface_gap` splits into at least three pressures.
  - It has `7` rows after the classifier tightening.
  - Source/publication genre metadata.
  - Generalized action or desire facts that were not compiled as direct
    predicates.
  - Synthesis/proverb/theme mapping.
  - Those should stay separate. A single "direct compile gap" repair would be
    too broad and likely to encode reading-comprehension test habits.
- `background_role_or_audience_fact` has `5` rows and is mixed.
  - It includes witness/knowledge binding, purpose-of-mention judgment, family
    counting, reuse advice, and teacher-cause explanation.
  - That label is not a repair target yet; it is a queue for finer coordinate
    splitting.

Artifacts:

- Source-record coordinate summary:
  `tmp\mrc_transfer_qa_race50_source_records_20260513\transfer_coordinate_summary.md`
- Manual audit source rows came from:
  `tmp\mrc_transfer_qa_race50_source_records_20260513\transfer_coordinate_summary.json`

Verification:

- Audited all rows in the initial top coordinate groups, then regenerated the
  summaries after tightening coordinate rules.
- Current top counts are:
  - `9` implicit-attitude rows.
  - `7` direct-compile rows.
  - `5` background-role/audience rows.
  - `2` comparative-or-temporal rows.
- No code repair was made from this audit.

Lesson:

- The proposition taxonomy did its job: it prevented the coordinate labels from
  becoming repair instructions.
- The remaining RACE residue is not primarily an MCQ interface problem. It is a
  proposition-pressure problem: semantic bridges, temporal/event joins, source
  metadata, and synthesis.
- The next defensible test is not "patch RACE." It is to create or sample unlike
  open-ended probes for the same proposition pressures and see which recur.

Next pressure:

- Build a small unlike open-ended probe for semantic-bridge inference:
  evidence states an action, reaction, risk, purpose, or trait; the question
  asks for the licensed consequence or attitude without multiple-choice labels.
- Keep route/distance joins as a separate probe. Do not mix them with
  wall-clock, business-day, or ordinary before/after event ordering until they
  prove they share machinery.
- Treat source/publication genre metadata as an intake/compiler metadata probe,
  not an inference repair.

### DT-010 - Open-Ended Semantic Bridge Probe

Before:

- RACE residue suggested semantic-bridge pressure, but multiple-choice labels
  could have been doing hidden work.
- DT-009 therefore called for an unlike open-ended probe where the source states
  actions, reactions, risks, purposes, and habits while the questions ask for
  the licensed attitude, purpose, trait, risk, or consequence.

Prediction:

- If the semantic-bridge boundary is real outside MCQ, the open-ended probe
  should miss or partially answer emotional-state, purpose, and consequence
  questions even with source-record facts enabled.
- Direct factual post-event action should be easier than semantic-bridge
  inference. If it misses, that is separate source-fidelity/action-detail
  pressure, not evidence that every inference row needs a semantic mapper.

Intervention:

- Added
  `experiments\boundary_probes\dataset_transfer_stage1\semantic_bridge_inference_ladder`.
- The probe contains `8` open-ended questions with isolated oracle answers and
  no multiple-choice answer labels.
- Ran OpenRouter compile/QA with source-record ledger facts enabled.
- Tightened the transfer-coordinate classifier after the probe exposed drift:
  `before`/`after` wording no longer makes a row comparative unless the row
  actually asks for order, distance, duration, arithmetic, or timeline assembly.

After:

- Compile:
  - Parsed OK.
  - `11` candidate predicates.
  - `205` admitted facts.
  - `19` skipped facts.
- QA:
  - `8` questions.
  - `3 exact / 2 partial / 3 miss`.
  - Exact rate `0.375`.
  - Runtime load errors `0`.
  - Write proposal rows `0`.
  - Helper rows `0`.
- Non-exact summary after classifier tightening:
  - Proposition types: `4` inference, `1` factual.
  - Coordinates: `4` implicit-attitude/consequence, `1` background-role/audience.
  - Failure surface: `5` compile-surface gaps.

Artifacts:

- Probe fixture:
  `experiments\boundary_probes\dataset_transfer_stage1\semantic_bridge_inference_ladder`
- Compile:
  `tmp\boundary_probe_dataset_compile_semantic_bridge_source_records_20260513`
- QA:
  `tmp\boundary_probe_dataset_qa_semantic_bridge_source_records_20260513`
- Coordinate summary:
  `tmp\boundary_probe_dataset_qa_semantic_bridge_source_records_20260513\transfer_coordinate_summary.md`

Verification:

- `python scripts\run_domain_bootstrap_file_batch.py --dataset-root experiments\boundary_probes\dataset_transfer_stage1 --fixture semantic_bridge_inference_ladder --out-root tmp\boundary_probe_dataset_compile_semantic_bridge_source_records_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 1 --timeout 900 --compile-source --compile-flat-plus-plan-passes --focused-pass-ops-schema --source-record-ledger --source-record-ledger-facts`
- `python scripts\run_domain_bootstrap_qa_batch.py --dataset-root experiments\boundary_probes\dataset_transfer_stage1 --fixture semantic_bridge_inference_ladder --compile-root tmp\boundary_probe_dataset_compile_semantic_bridge_source_records_20260513 --out-root tmp\boundary_probe_dataset_qa_semantic_bridge_source_records_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 1 --timeout 420 --no-cache`
- `python scripts\summarize_mrc_transfer_qa.py --qa-root tmp\boundary_probe_dataset_qa_semantic_bridge_source_records_20260513`
- `python -m pytest tests\test_summarize_mrc_transfer_qa.py tests\test_sample_mrc_transfer_fixtures.py tests\test_stage_incoming_fixtures.py -q`
  - `28 passed`

Manual audit:

- Exact rows:
  - Inventive/repair-minded trait.
  - Dangerous/unsafe path.
  - Portable-light consequence.
- Partial rows:
  - Clinic covers: physical context retrieved, purpose/user-experience bridge
    incomplete.
  - Children cleanup: action retrieved abstractly, but tool/object details were
    lost.
- Miss rows:
  - Relief after all-clear.
  - Nervousness before speaking.
  - Coat-check purpose before pickup.

Lesson:

- The semantic-bridge boundary transfers outside multiple-choice. MCQ labels
  are not the whole explanation.
- The architecture can already bridge some traits, risks, and consequences, but
  emotional-state and purpose-from-action surfaces remain thin.
- This should still not become a generic "map gestures to emotions" table from
  one probe. The safe next step is a second unlike open-ended probe or a small
  SQuAD slice classified by the same proposition taxonomy.
- The coordinate drift caught here validates the user's warning: taxonomy must
  have operational criteria before classification, and the instrument itself
  must be audited when a label starts collecting unlike things.

Next pressure:

- Either sample a small SQuAD open-ended slice and classify its non-exacts by
  proposition type, or build one more focused open-ended semantic-bridge probe
  with different surface conventions.
- Keep emotional-state bridge, purpose bridge, and action-detail source fidelity
  as separate pressures.
- Do not implement semantic-bridge repair until the same pressure recurs across
  unlike sources without answer-option vocabulary.
