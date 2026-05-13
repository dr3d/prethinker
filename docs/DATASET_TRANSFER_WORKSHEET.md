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
  - `factual`: `10`
  - `inference`: `9`
  - `categorical`: `3`
  - `comparative`: `2`
  - `synthesis`: `1`
- Regressed rows by new proposition type:
  - `factual`: `4`
  - `inference`: `3`
  - `comparative`: `1`
  - `synthesis`: `1`
- Non-exact proposition-type shift:
  - `inference`: `19 -> 12`
  - `factual`: `14 -> 11`
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
  - `29 passed`

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
  - `29 passed`

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

### DT-011 - SQuAD-10 Open-Ended Transfer Check

Before:

- DT-010 confirmed that semantic-bridge pressure can appear without
  multiple-choice answer labels, but the probe was synthetic.
- The next useful measurement was a small real open-ended external dataset slice
  using the same source-record default path.

Prediction:

- If Prethinker handles ordinary open-ended extractive QA cleanly, a small
  SQuAD slice should score higher than the RACE MCQ slice because most questions
  ask for directly stated spans.
- Remaining misses should shift away from RACE-style answer-option semantics
  and toward source-fidelity, acronym/label mapping, authority joins, and
  numeric/category rendering.

Intervention:

- Sampled `10` SQuAD validation passages with deterministic even spread.
- Staged the sampled passages through the existing incoming-fixture adapter.
- Ran six-lane OpenRouter compile/QA with source-record ledger facts enabled.
- Regenerated the transfer-coordinate summary with the tightened proposition
  and coordinate taxonomy.

After:

- Sampling/staging:
  - `10` fixtures sampled.
  - `10` staged.
  - `0` staging failures.
- Compile:
  - `10 / 10` parsed.
  - `92` candidate predicates.
  - `385` admitted facts.
  - `2` skipped facts.
- QA:
  - `71` questions.
  - `62 exact / 1 partial / 8 miss`.
  - Exact rate `0.8732`.
  - Runtime load errors `0`.
  - Write proposal rows `0`.
  - Helper rows `20`, pressure label `bounded_helper_surface`.
- Non-exact proposition types:
  - `factual`: `6`
  - `inference`: `1`
  - `comparative`: `1`
  - `categorical`: `1`
- Non-exact coordinates:
  - `direct_compile_surface_gap`: `4`
  - `answer_surface_mapping`: `2`
  - `background_role_or_audience_fact`: `1`
  - `false_or_exception_option_selection`: `1`
  - `implicit_attitude_or_consequence`: `1`

Artifacts:

- Sampled fixtures:
  `tmp\mrc_transfer_samples_squad10_20260513`
- Staged fixtures:
  `tmp\mrc_transfer_staged_squad10_20260513`
- Compile:
  `tmp\mrc_transfer_compile_squad10_source_records_20260513`
- QA:
  `tmp\mrc_transfer_qa_squad10_source_records_20260513`
- Coordinate summary:
  `tmp\mrc_transfer_qa_squad10_source_records_20260513\transfer_coordinate_summary.md`

Verification:

- `python scripts\sample_mrc_transfer_fixtures.py --source-format squad --dataset squad --no-config --split validation --limit 10 --sample-strategy even --out-root tmp\mrc_transfer_samples_squad10_20260513`
- `python scripts\stage_incoming_fixtures.py --root tmp\mrc_transfer_samples_squad10_20260513 --out-root tmp\mrc_transfer_staged_squad10_20260513`
- `python scripts\run_domain_bootstrap_file_batch.py --dataset-root tmp\mrc_transfer_staged_squad10_20260513 --out-root tmp\mrc_transfer_compile_squad10_source_records_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 900 --compile-source --compile-flat-plus-plan-passes --focused-pass-ops-schema --source-record-ledger --source-record-ledger-facts`
- `python scripts\run_domain_bootstrap_qa_batch.py --dataset-root tmp\mrc_transfer_staged_squad10_20260513 --compile-root tmp\mrc_transfer_compile_squad10_source_records_20260513 --out-root tmp\mrc_transfer_qa_squad10_source_records_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 420 --no-cache`
- `python scripts\summarize_mrc_transfer_qa.py --qa-root tmp\mrc_transfer_qa_squad10_source_records_20260513`

Manual audit:

- The SQuAD slice is much more extractive than RACE:
  `87.32%` exact versus the corrected RACE source-record replay at `83.05%`.
- The residue is not dominated by semantic-bridge inference.
  - Acronym expansion and template placeholder retrieval are source-surface
    mapping problems.
  - Counterfactual Roman numeral naming is external rule/format mapping.
  - Season versus event-date asks for better answer-surface selection.
  - Authority of a classification asks for a join between content relation and
    source/authority relation.
  - One partial row asks for an inferred submission recipient.

Lesson:

- Open-ended QA is not automatically harder than MCQ. The structural variable is
  still proposition type and answer-surface shape.
- SQuAD supports the current direction: direct extractive QA is mostly inside
  the set with source-record facts enabled; remaining pressure is specific and
  classifiable.
- The semantic-bridge pressure remains real, but SQuAD-10 shows it is not the
  dominant open-ended external residue in an extractive dataset.

Next pressure:

- Do not repair from SQuAD-10 yet.
- The next high-value focused probe is answer-surface mapping:
  season versus event date, acronym expansion, placeholder/template values, and
  numeric-to-label category rendering.
- Keep semantic-bridge inference in the queue, but do not let it crowd out
  source-surface and answer-rendering repairs that recur across external data.

### DT-012 - Answer-Surface Mapping Probe

Before:

- SQuAD-10 residue suggested answer-surface pressure:
  acronym expansion, season versus event date, template placeholders,
  numeric-to-label category rendering, authority joins, and submission recipient
  binding.
- The risk was overgeneralizing from SQuAD rows before isolating which of those
  surfaces were actually outside the set.

Prediction:

- If answer-surface mapping is broadly missing, a focused probe should miss
  abbreviation expansion, season/date selection, placeholder retrieval,
  numeric-to-label rendering, and identifier selection.
- If those pass, the remaining boundary is narrower: role/authority/recipient
  binding across nearby event and metadata surfaces.

Intervention:

- Added
  `experiments\boundary_probes\dataset_transfer_stage1\answer_surface_mapping_ladder`.
- The probe contains `8` open-ended questions over compact registry notes.
- Ran OpenRouter compile/QA with source-record ledger facts enabled.

After:

- Compile:
  - Parsed OK.
  - `16` candidate predicates.
  - `51` admitted facts.
  - `0` skipped facts.
- QA:
  - `8` questions.
  - `6 exact / 0 partial / 2 miss`.
  - Exact rate `0.75`.
  - Runtime load errors `0`.
  - Write proposal rows `0`.
  - Helper rows `0`.
- Passing surfaces:
  - Abbreviation expansion.
  - Season versus event-date selection.
  - Template placeholder retrieval.
  - Numeric-to-label scale rendering.
  - Program-year versus reception-date selection.
  - Filing identifier versus inspection code selection.
- Misses:
  - Classification agent: compile attributed the classification to the recorder
    rather than preserving the classifier as the authority.
  - Submission recipient: query/join failed to bind the submitted object to the
    recipient instead of nearby action performers.

Artifacts:

- Probe fixture:
  `experiments\boundary_probes\dataset_transfer_stage1\answer_surface_mapping_ladder`
- Compile:
  `tmp\boundary_probe_dataset_compile_answer_surface_source_records_20260513`
- QA:
  `tmp\boundary_probe_dataset_qa_answer_surface_source_records_20260513`
- Coordinate summary:
  `tmp\boundary_probe_dataset_qa_answer_surface_source_records_20260513\transfer_coordinate_summary.md`

Verification:

- `python scripts\run_domain_bootstrap_file_batch.py --dataset-root experiments\boundary_probes\dataset_transfer_stage1 --fixture answer_surface_mapping_ladder --out-root tmp\boundary_probe_dataset_compile_answer_surface_source_records_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 1 --timeout 900 --compile-source --compile-flat-plus-plan-passes --focused-pass-ops-schema --source-record-ledger --source-record-ledger-facts`
- `python scripts\run_domain_bootstrap_qa_batch.py --dataset-root experiments\boundary_probes\dataset_transfer_stage1 --fixture answer_surface_mapping_ladder --compile-root tmp\boundary_probe_dataset_compile_answer_surface_source_records_20260513 --out-root tmp\boundary_probe_dataset_qa_answer_surface_source_records_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 1 --timeout 420 --no-cache`
- `python scripts\summarize_mrc_transfer_qa.py --qa-root tmp\boundary_probe_dataset_qa_answer_surface_source_records_20260513`

Lesson:

- Most of the apparent answer-surface class is already inside the set when
  isolated.
- The live boundary is not generic answer rendering. It is role binding:
  distinguish the actor who classifies from the registrar who records, and the
  recipient of a submission from adjacent actors in the event sequence.
- This aligns with older authority-envelope work but in external-dataset form:
  the question asks for a role in a relation, and nearby source surfaces contain
  plausible but wrong roles.

Next pressure:

- Build or sample a role-binding/recipient-binding probe before making a repair.
- Candidate repair, if proven across unlike probes: reward evidence rows that
  bind relation, object, and requested role in the same surface; penalize nearby
  recorder/announcer/performer rows when the question asks classifier,
  recipient, approver, witness, or owner.
- Keep abbreviation, placeholder, season/date, scale-label, and identifier
  surfaces off the repair queue for now because the focused probe passed them.

### DT-013 - Role-Binding Probe

Before:

- DT-012 narrowed answer-surface pressure to role binding:
  classifier versus recorder, recipient versus performer, and adjacent authority
  roles.
- The question was whether that pressure recurs when isolated across several
  relation roles, or whether the previous misses were one-off compile variance.

Prediction:

- If role binding is inside the set, the probe should answer each `who`
  question by selecting the actor, recipient, owner, witness, approver, author,
  or assignee bound to the asked relation.
- If it fails, failures should cluster where the compile stores the action or
  object but drops the role-bearing participant.

Intervention:

- Added
  `experiments\boundary_probes\dataset_transfer_stage1\role_binding_ladder`.
- The probe contains `9` open-ended role-binding questions with isolated oracle
  answers.
- Ran OpenRouter compile/QA with source-record ledger facts enabled.

After:

- Compile:
  - Parsed OK.
  - `21` candidate predicates.
  - `46` admitted facts.
  - `0` skipped facts.
- QA:
  - `9` questions.
  - `5 exact / 0 partial / 4 miss`.
  - Exact rate `0.5556`.
  - Runtime load errors `0`.
  - Write proposal rows `0`.
  - Helper rows `0`.
- Passing roles:
  - Approver.
  - Witness.
  - Owner.
  - Author.
  - Recipient/custodian for delivered packet.
- Missed roles:
  - Classifier of a classification.
  - Recorder of a classification.
  - Recipient of a submission.
  - Assignee of an assigned task.

Artifacts:

- Probe fixture:
  `experiments\boundary_probes\dataset_transfer_stage1\role_binding_ladder`
- Compile:
  `tmp\boundary_probe_dataset_compile_role_binding_source_records_20260513`
- QA:
  `tmp\boundary_probe_dataset_qa_role_binding_source_records_20260513`
- Coordinate summary:
  `tmp\boundary_probe_dataset_qa_role_binding_source_records_20260513\transfer_coordinate_summary.md`

Verification:

- `python scripts\run_domain_bootstrap_file_batch.py --dataset-root experiments\boundary_probes\dataset_transfer_stage1 --fixture role_binding_ladder --out-root tmp\boundary_probe_dataset_compile_role_binding_source_records_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 1 --timeout 900 --compile-source --compile-flat-plus-plan-passes --focused-pass-ops-schema --source-record-ledger --source-record-ledger-facts`
- `python scripts\run_domain_bootstrap_qa_batch.py --dataset-root experiments\boundary_probes\dataset_transfer_stage1 --fixture role_binding_ladder --compile-root tmp\boundary_probe_dataset_compile_role_binding_source_records_20260513 --out-root tmp\boundary_probe_dataset_qa_role_binding_source_records_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 1 --timeout 420 --no-cache`
- `python scripts\summarize_mrc_transfer_qa.py --qa-root tmp\boundary_probe_dataset_qa_role_binding_source_records_20260513`

Lesson:

- Role binding is a real external-transfer coordinate.
- The failure pattern is compile-surface, not answer rendering: the compile
  often preserves that an object was classified, recorded, submitted, or
  assigned, but drops the role-bearing participant or compresses assignee into
  assigner.
- The passing rows are equally useful: approver, witness, owner, author, and
  delivered-packet recipient are already recoverable when the relation keeps the
  participant bound.

Next pressure:

- Candidate generic compile repair: when a source sentence contains an action
  with actor, object, and role-bearing participant, preserve all of them in the
  same relation surface or in explicitly joinable companion predicates.
- Target verbs are not fixture vocabulary; they are role-frame families:
  classify/record, submit/receive, assign/request, approve/recommend,
  witness/report, own/maintain, write/publish.
- Re-run the role-binding probe and a small SQuAD residue slice after any repair.

### DT-014 - Role-Frame Compile Guidance Repair

Before:

- DT-013 showed role binding was a real coordinate:
  role probe `5 / 0 / 4`, with misses on classifier, recorder, submission
  recipient, and task assignee.
- SQuAD-10 also carried role/recipient residue, especially submission recipient
  and consideration/classification authority.

Prediction:

- A generic compile-guidance repair should improve role frames where the source
  clearly states actor, object, and role-bearing participant.
- It should not add helpers, write proposals, or fixture-shaped predicates.
- The likely hardest residue is authority/source language such as "considers"
  because it can be represented as content relation without the considering
  agent.

Intervention:

- Added a generic role-frame preservation rule to source compile guidance and
  focused pass guidance:
  preserve actor, object, and role-bearing participant for
  classify/record, submit/receive, assign/request, approve/recommend,
  witness/report, own/maintain, and write/publish frames when the profile offers
  compatible predicates or detail surfaces.
- Recompiled and replayed the role-binding probe.
- Recompiled and replayed the two SQuAD fixtures containing role/recipient
  residue.

After:

- Role-binding probe:
  - Before repair: `9` questions, `5 exact / 0 partial / 4 miss`.
  - After repair: `9` questions, `7 exact / 0 partial / 2 miss`.
  - Runtime load errors `0`; write proposal rows `0`; helper rows `0`.
  - Improved rows: submission recipient and task assignee.
  - Remaining misses: classifier and recorder for a classification.
- SQuAD role-residue slice:
  - Before repair on the same two fixtures: `10` questions,
    `6 exact / 1 partial / 3 miss`.
  - After repair: `10` questions, `9 exact / 0 partial / 1 miss`.
  - Runtime load errors `0`; write proposal rows `0`; helper rows `0`.
  - Improved rows: connected area, submission recipient, and template
    placeholder.
  - Remaining miss: the authority that considers a metropolitan area separate.

Artifacts:

- Code:
  `scripts\run_domain_bootstrap_file.py`
- Role probe repair compile:
  `tmp\boundary_probe_dataset_compile_role_binding_frame_repair_20260513`
- Role probe repair QA:
  `tmp\boundary_probe_dataset_qa_role_binding_frame_repair_20260513`
- SQuAD repair compile:
  `tmp\mrc_transfer_compile_squad_role_binding_frame_repair_20260513`
- SQuAD repair QA:
  `tmp\mrc_transfer_qa_squad_role_binding_frame_repair_20260513`

Verification:

- `python scripts\run_domain_bootstrap_file_batch.py --dataset-root experiments\boundary_probes\dataset_transfer_stage1 --fixture role_binding_ladder --out-root tmp\boundary_probe_dataset_compile_role_binding_frame_repair_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 1 --timeout 900 --compile-source --compile-flat-plus-plan-passes --focused-pass-ops-schema --source-record-ledger --source-record-ledger-facts`
- `python scripts\run_domain_bootstrap_qa_batch.py --dataset-root experiments\boundary_probes\dataset_transfer_stage1 --fixture role_binding_ladder --compile-root tmp\boundary_probe_dataset_compile_role_binding_frame_repair_20260513 --out-root tmp\boundary_probe_dataset_qa_role_binding_frame_repair_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 1 --timeout 420 --no-cache`
- `python scripts\run_domain_bootstrap_file_batch.py --dataset-root tmp\mrc_transfer_staged_squad10_20260513 --fixture squad_default_validation_00002_southern_california --fixture squad_default_validation_00008_scottish_parliament --out-root tmp\mrc_transfer_compile_squad_role_binding_frame_repair_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 2 --timeout 900 --compile-source --compile-flat-plus-plan-passes --focused-pass-ops-schema --source-record-ledger --source-record-ledger-facts`
- `python scripts\run_domain_bootstrap_qa_batch.py --dataset-root tmp\mrc_transfer_staged_squad10_20260513 --fixture squad_default_validation_00002_southern_california --fixture squad_default_validation_00008_scottish_parliament --compile-root tmp\mrc_transfer_compile_squad_role_binding_frame_repair_20260513 --out-root tmp\mrc_transfer_qa_squad_role_binding_frame_repair_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 2 --timeout 420 --no-cache`

Lesson:

- The repair is real but partial. It improves recipient and assignee binding and
  transfers to SQuAD, without helper growth or fixture vocabulary.
- The remaining authority/classifier residue is narrower than the original
  role-binding class. It needs source/authority-agent preservation for
  classification or consideration statements, not a broad role repair.
- This is the dataset-transfer phase doing the same discipline as guard
  compression: classify pressure, isolate it, repair generically, replay on an
  unlike slice, and keep the residue named.

Next pressure:

- Add a focused authority-agent probe before changing code again:
  classify/consider/record/source-attribution statements where the asked answer
  is the authority performing or asserting the relation.
- Re-run a broader SQuAD-10 or RACE factual/source-record slice only after the
  authority-agent residue is clarified.
- Watch for regressions: the role-frame guidance is prompt-level substrate and
  should be kept only if broader transfer holds.

### DT-015 - CUAD-10 Cross-Domain Legal Transfer

Before:

- RACE-50 and SQuAD-10 showed strong within-broad-English transfer with
  source-record facts enabled:
  - RACE-50 source-record replay: `147 / 5 / 25` over `177`, exact `83.05%`.
  - SQuAD-10 source-record run: `62 / 1 / 8` over `71`, exact `87.32%`.
- Both corpora are still academic/general English. The methodology needed a
  structurally unlike domain before claiming cross-domain transfer.

Prediction:

- CUAD legal contracts should lower exact rate if the architecture is
  genre-shaped around school/Wikipedia prose.
- A useful result is not only the score; it is whether the residue is familiar
  query/compile resolution or a new legal-only boundary class.
- No repair should be made from a `10`-contract smoke alone.

Intervention:

- Added a CUAD intake adapter to `scripts\sample_mrc_transfer_fixtures.py`.
- The adapter downloads `CUAD_v1.json` from HuggingFace, samples contract-level
  records, and writes bounded answer-neighborhood excerpts rather than whole
  contracts.
- It keeps references isolated in `oracle.jsonl` and rewrites only the question
  surface into open-ended extractive wording.
- Tightened `scripts\summarize_mrc_transfer_qa.py` for cross-domain use:
  - Latest QA artifact per fixture is summarized, so reruns do not double-count.
  - Direct contract field/date extraction is factual, not comparative.
  - Document-name extraction is not title/theme synthesis.
  - Provider/classifier transport errors are separated from false-option
    coordinates.

After:

- Sample/stage:
  - `10` CUAD fixtures.
  - `40` questions.
  - Source excerpts range from about `2.2k` to `11.5k` chars.
- Compile:
  - `10 / 10` parsed.
  - Candidate predicates `122`.
  - Compile admitted/skipped `486 / 30`.
  - Two initial OpenRouter provider-schema failures were retried at one lane and
    cleared.
- QA:
  - `28 exact / 2 partial / 10 miss` over `40`.
  - Exact rate `70.0%`.
  - Runtime load errors `0`.
  - Write proposal rows `0`.
  - Helper rows `0`.
- Residue:
  - Proposition types: all `12` non-exact judged rows are `factual`.
  - Transfer coordinates:
    - `query_surface_resolution`: `6`.
    - `direct_compile_surface_gap`: `3`.
    - `judge_transport_uncertain`: `2`.
    - `comparative_or_temporal_resolution`: `1`.
  - Main real boundary: query surfaces fail to retrieve already-compiled legal
    field/date/document facts.
  - Secondary boundary: compile sometimes does not emit direct legal field
    surfaces for parties or agreement date even though source rows preserve the
    text.

Artifacts:

- Sampled fixtures:
  `tmp\mrc_transfer_samples_cuad10_20260513`
- Staged fixtures:
  `tmp\mrc_transfer_staged_cuad10_20260513`
- Compile:
  `tmp\mrc_transfer_compile_cuad10_source_records_20260513`
- QA:
  `tmp\mrc_transfer_qa_cuad10_source_records_20260513`
- Coordinate summary:
  `tmp\mrc_transfer_qa_cuad10_source_records_20260513\transfer_coordinate_summary.md`

Verification:

- `python -m pytest tests\test_summarize_mrc_transfer_qa.py tests\test_sample_mrc_transfer_fixtures.py -q`
- `python scripts\sample_mrc_transfer_fixtures.py --source-format cuad --dataset theatticusproject/cuad --no-config --split train --limit 10 --sample-strategy even --max-questions-per-record 4 --cuad-answer-window 1400 --cuad-max-answer-chars 800 --out-root tmp\mrc_transfer_samples_cuad10_20260513`
- `python scripts\stage_incoming_fixtures.py --root tmp\mrc_transfer_samples_cuad10_20260513 --out-root tmp\mrc_transfer_staged_cuad10_20260513`
- `python scripts\run_domain_bootstrap_file_batch.py --dataset-root tmp\mrc_transfer_staged_cuad10_20260513 --out-root tmp\mrc_transfer_compile_cuad10_source_records_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 900 --compile-source --compile-flat-plus-plan-passes --focused-pass-ops-schema --source-record-ledger --source-record-ledger-facts`
- `python scripts\run_domain_bootstrap_file_batch.py --dataset-root tmp\mrc_transfer_staged_cuad10_20260513 --fixture cuad_default_train_00008__collaboration_agreement --fixture cuad_default_train_00009_10_endorsement_agreement --out-root tmp\mrc_transfer_compile_cuad10_source_records_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 1 --timeout 900 --compile-source --compile-flat-plus-plan-passes --focused-pass-ops-schema --source-record-ledger --source-record-ledger-facts`
- `python scripts\run_domain_bootstrap_qa_batch.py --dataset-root tmp\mrc_transfer_staged_cuad10_20260513 --compile-root tmp\mrc_transfer_compile_cuad10_source_records_20260513 --out-root tmp\mrc_transfer_qa_cuad10_source_records_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 420 --no-cache`
- `python scripts\run_domain_bootstrap_qa_batch.py --dataset-root tmp\mrc_transfer_staged_cuad10_20260513 --fixture cuad_default_train_00007_ontent_license_agreement --fixture cuad_default_train_00008__collaboration_agreement --fixture cuad_default_train_00009_10_endorsement_agreement --compile-root tmp\mrc_transfer_compile_cuad10_source_records_20260513 --out-root tmp\mrc_transfer_qa_cuad10_source_records_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 1 --timeout 420 --no-cache`
- `python scripts\run_domain_bootstrap_file_batch.py --dataset-root tmp\mrc_transfer_staged_cuad10_20260513 --out-root tmp\mrc_transfer_compile_cuad10_source_records_20260513 --summarize-existing`
- `python scripts\run_domain_bootstrap_qa_batch.py --dataset-root tmp\mrc_transfer_staged_cuad10_20260513 --compile-root tmp\mrc_transfer_compile_cuad10_source_records_20260513 --out-root tmp\mrc_transfer_qa_cuad10_source_records_20260513 --summarize-existing`
- `python scripts\summarize_mrc_transfer_qa.py --qa-root tmp\mrc_transfer_qa_cuad10_source_records_20260513`

Lesson:

- CUAD-10 is a real cross-domain drop from RACE/SQuAD, but not a collapse.
  The architecture can answer most bounded legal extraction questions cold.
- The boundary is not synthesis or inference; the first CUAD slice is almost
  entirely factual field/date extraction.
- The dominant pressure is legal-source queryability: facts often exist in
  source-record rows or explicit legal predicates, but the query plan does not
  reliably retrieve the field/date/document surface.
- This is not permission for CUAD-specific contract helpers. The transferable
  shape is "field-like source facts and effective-date/document-date/party
  surfaces need stable query access."

Next pressure:

- Manual audit the `6` query-surface rows before any repair.
- If they share one fixture-free predicate family, build a focused legal-field
  extraction probe with document name, parties, agreement date, and effective
  date across unlike contract prose.
- Keep CUAD at measurement/probe status until a generic source-field query
  principle is proven outside these `10` contracts.

### DT-016 - CUAD Query-Surface Residue Audit

Before:

- DT-015 left `6` `query_surface_resolution` rows after the CUAD-10 run.
- These rows mattered more than the raw `70.0%` score because they determine
  whether the legal-domain gap is compile extraction or query addressability.

Prediction:

- If the rows share a fixture-free shape, the next work should be a focused
  legal-field query probe.
- If they are unrelated, CUAD-10 should remain only a measurement point and not
  drive repair.

Intervention:

- Read the six `query_surface_resolution` rows from the CUAD coordinate summary.
- Audited only question type, reference shape, and failure rationale; no fixture
  names, row IDs, or answer strings were promoted into architecture.

After:

- The six rows share one broad shape:
  field-like source facts are compiled, but the query plan does not retrieve
  the answer-bearing surface.
- Subshapes:
  - Document-name/title fields: `2` rows. Facts exist as `contract_title` or
    source-record title atoms, but query emission is empty or over-bound.
  - Contract date fields: `3` rows. Facts exist as `agreement_effective_date` or
    `effective_date`, but query emission is empty.
  - Party fields: `1` row. Party-name facts and source-record party definition
    text exist, but query emission is empty.
- The residue is not a legal-domain missing-axis result. It is a query
  addressability result over field-like source facts.

Artifacts:

- CUAD summary:
  `tmp\mrc_transfer_qa_cuad10_source_records_20260513\transfer_coordinate_summary.md`

Verification:

- Manual audit from
  `tmp\mrc_transfer_qa_cuad10_source_records_20260513\transfer_coordinate_summary.json`

Lesson:

- CUAD's first useful boundary class is "field-like source fact queryability."
  That is more general than contracts: any document with title/date/party-like
  header fields can expose the same gap.
- The repair target should not be CUAD categories. It should be a generic query
  principle: when a question asks for a named source field or field-like
  attribute, prefer direct field predicates and source-record text atoms whose
  labels or atoms bind the requested field surface.

Next pressure:

- Build a small focused probe with unlike prose styles:
  - formal contract header,
  - policy memo header,
  - invoice/order header,
  - meeting notice header.
- Ask only field-like extraction questions for document name, parties/actors,
  agreement/event date, and effective/start date.
- If the same query-surface miss reproduces, repair the query planner at the
  generic source-field level and replay CUAD-10 plus SQuAD/RACE smoke.

### DT-017 - MAUD-10 Legal Taxonomy Transfer

Before:

- CUAD-10 landed at `28 / 2 / 10` over `40`, exact `70.0%`.
- CUAD was useful but ugly: annotation-prompt questions, long clause spans, and
  OCR-ish legal text made it unclear whether the measured boundary was legal
  transfer or dataset shape.
- MAUD looked like a cleaner legal alternative because it ships CSV rows with
  `text`, `question`, `answer`, `label`, and contract identifiers.

Prediction:

- If CUAD's drop was mostly dataset ugliness, MAUD-10 should recover toward the
  RACE/SQuAD range.
- If legal-domain transfer requires external legal taxonomy labels, MAUD should
  expose a different boundary: category/label mapping rather than extractive QA.

Intervention:

- Added MAUD support to `scripts\sample_mrc_transfer_fixtures.py`.
- The adapter downloads MAUD CSV splits from HuggingFace, groups rows by
  contract, writes bounded merger-agreement excerpts, and keeps MAUD labels and
  reference answers isolated in `oracle.jsonl`.
- Added small external-text cleanup at intake for common source encoding
  artifacts.
- Sampled `10` MAUD dev contracts, `4` rows each.
- OpenRouter was temporarily unusable for Qwen (`429` plus provider schema
  errors), so compile/QA ran through local LM Studio on the 5090.

After:

- Sample/stage:
  - `10` MAUD fixtures.
  - `40` questions.
  - Source excerpts range from about `10k` to `18k` chars.
- Compile:
  - `10 / 10` parsed.
  - Candidate predicates `115`.
  - Compile admitted/skipped `785 / 90`.
  - One local HTTP `500` cleared on single-fixture retry.
- QA:
  - `17 exact / 1 partial / 22 miss` over `40`.
  - Exact rate `42.5%`.
  - Runtime load errors `0`.
  - Write proposal rows `0`.
  - Helper rows `0`.
- Residue:
  - Proposition types: `23` non-exact rows classified as `categorical`.
  - Transfer coordinates:
    - `false_or_exception_option_selection`: `8`.
    - `direct_compile_surface_gap`: `7`.
    - `background_role_or_audience_fact`: `3`.
    - `hybrid_join_resolution`: `2`.
    - `query_surface_resolution`: `2`.
    - `implicit_attitude_or_consequence`: `1`.
  - Failure surfaces:
    - `compile_surface_gap`: `16`.
    - `hybrid_join_gap`: `5`.
    - `query_surface_gap`: `2`.
- Literalness audit:
  - MAUD dev `main` answered rows: `3471`.
  - Rows where the reference answer appears literally in the excerpt: `515`
    (`14.8%`).
  - Many MAUD answers are external legal taxonomy labels such as consideration
    type, representation-and-warranty category sets, carveout/dropdown labels,
    or yes/no legal judgments.

Artifacts:

- Sampled fixtures:
  `tmp\mrc_transfer_samples_maud10_20260513`
- Staged fixtures:
  `tmp\mrc_transfer_staged_maud10_20260513`
- Compile:
  `tmp\mrc_transfer_compile_maud10_source_records_20260513`
- QA:
  `tmp\mrc_transfer_qa_maud10_source_records_20260513`
- Coordinate summary:
  `tmp\mrc_transfer_qa_maud10_source_records_20260513\transfer_coordinate_summary.md`

Verification:

- `python -m pytest tests\test_sample_mrc_transfer_fixtures.py tests\test_summarize_mrc_transfer_qa.py -q`
- `python scripts\sample_mrc_transfer_fixtures.py --source-format maud --dataset theatticusproject/maud --no-config --split dev --limit 10 --sample-strategy even --max-questions-per-record 4 --maud-max-text-chars 5000 --maud-max-answer-chars 400 --maud-data-type main --out-root tmp\mrc_transfer_samples_maud10_20260513`
- `python scripts\stage_incoming_fixtures.py --root tmp\mrc_transfer_samples_maud10_20260513 --out-root tmp\mrc_transfer_staged_maud10_20260513`
- `python scripts\run_domain_bootstrap_file_batch.py --dataset-root tmp\mrc_transfer_staged_maud10_20260513 --out-root tmp\mrc_transfer_compile_maud10_source_records_20260513 --model qwen/qwen3.6-35b-a3b --base-url http://localhost:1234/v1 --lanes 2 --timeout 1200 --compile-source --compile-flat-plus-plan-passes --focused-pass-ops-schema --source-record-ledger --source-record-ledger-facts`
- `python scripts\run_domain_bootstrap_file_batch.py --dataset-root tmp\mrc_transfer_staged_maud10_20260513 --fixture maud_default_dev_00001_contract_15 --out-root tmp\mrc_transfer_compile_maud10_source_records_20260513 --model qwen/qwen3.6-35b-a3b --base-url http://localhost:1234/v1 --lanes 1 --timeout 1200 --compile-source --compile-flat-plus-plan-passes --focused-pass-ops-schema --source-record-ledger --source-record-ledger-facts`
- `python scripts\run_domain_bootstrap_file_batch.py --dataset-root tmp\mrc_transfer_staged_maud10_20260513 --out-root tmp\mrc_transfer_compile_maud10_source_records_20260513 --summarize-existing`
- `python scripts\run_domain_bootstrap_qa_batch.py --dataset-root tmp\mrc_transfer_staged_maud10_20260513 --compile-root tmp\mrc_transfer_compile_maud10_source_records_20260513 --out-root tmp\mrc_transfer_qa_maud10_source_records_20260513 --model qwen/qwen3.6-35b-a3b --base-url http://localhost:1234/v1 --lanes 2 --timeout 600 --no-cache`
- `python scripts\summarize_mrc_transfer_qa.py --qa-root tmp\mrc_transfer_qa_maud10_source_records_20260513`

Lesson:

- MAUD is cleaner as a dataset package but not cleaner as a Prethinker transfer
  target. It is mostly legal taxonomy classification, not open-ended document
  QA or extractive answer recovery.
- CUAD's surface is ugly, but its task is closer to source-grounded extraction.
  MAUD's surface is cleaner, but its answers often require mapping source text
  into an external legal annotation scheme that the source does not literally
  state.
- The `42.5%` exact rate should not be read as a worse legal-reading score than
  CUAD. It is evidence that Prethinker does not currently own MAUD's external
  legal taxonomy.
- This should not trigger fixture-specific MAUD repairs. A repair would require
  a generic architecture for task-provided label taxonomies or classification
  rubrics, not merger-agreement vocabulary.

Next pressure:

- Do not use raw MAUD as the main clean legal QA baseline.
- Either:
  - build a MAUD-literal subset where the answer appears in the excerpt, if the
    goal is legal extractive QA; or
  - treat MAUD as a separate taxonomy-classification probe, if the goal is
    label/rubric grounding.
- For a cleaner open-ended legal/document QA baseline, look next at PrivacyQA or
  another document-grounded QA set whose answers are naturally expressed in the
  source rather than annotation labels.

### DT-018 - PrivacyQA Pre-Registered Interpretation Frame

Before:

- CUAD-10 and MAUD-10 showed that "legal" is too broad as an evaluation label:
  - CUAD is ugly but closer to source-grounded extraction.
  - MAUD is packaged cleanly but mostly tests external legal taxonomy labels.
- PrivacyQA is the next candidate because privacy policies are legal-ish,
  document-grounded, and closer to user-facing questions than merger-agreement
  label rubrics.

Prediction:

- PrivacyQA should be interpreted only after measuring the literalness fraction.
- If literalness is below `30%`, treat the run mostly as classification,
  inference, or rubric pressure rather than extractive QA.
- If `query_surface_resolution` dominates, that strengthens the CUAD finding:
  legal-ish extraction pressure is about stable access to source-field/source-row
  facts.
- If `compile_surface_gap` dominates, PrivacyQA is exposing missing policy
  surfaces rather than query access.
- If inference-heavy rows dominate, privacy policy QA is closer to reader
  conclusion MRC than contract extraction, and "legal" is not the useful frame.
- Score bands are pre-committed:
  - Around `70%`: CUAD probably approximates current legal-ish extraction
    transfer.
  - Around `85%`: CUAD was mostly corpus ugliness; cleaner legal-ish QA is much
    closer to SQuAD/RACE.
  - Around `50%`: CUAD was generous; legal/policy transfer is materially harder.

Intervention:

- Locked this frame before sampling or scoring PrivacyQA.
- Probed OpenRouter with a tiny Qwen call; transport returned HTTP `200` via
  Parasail, so hosted runs can be tried again with normal token budgets.

After:

- No PrivacyQA measurement yet.
- OpenRouter appears available again, but previous provider 429/schema failures
  remain part of the operating context; use hosted lanes when productive and
  fall back locally if transport becomes the experiment.

Artifacts:

- OpenRouter probe: direct `/chat/completions` call against
  `qwen/qwen3.6-35b-a3b`.

Verification:

- Probe returned HTTP `200`.

Lesson:

- Pre-commitment matters here because the next result can land in several
  scientifically useful regimes. The interpretation should not be rewritten
  after seeing the score.

Next pressure:

- Inspect PrivacyQA schema and answer literalness before building any adapter.
- If the dataset is suitable, sample a small PrivacyQA-10 run and compare
  coordinate distribution against CUAD and MAUD.

### DT-019 - PrivacyQA-10 Source-Aligned Policy Probe

Before:

- DT-018 pre-committed the PrivacyQA interpretation bands before measurement:
  literalness first, then score and coordinate shape.
- The first blind even sample exposed a dataset-quality risk: some question /
  snippet pairs looked visibly misaligned. That is dataset noise, not a useful
  architecture boundary.

Prediction:

- If PrivacyQA is mostly source-grounded, it should score closer to SQuAD/RACE
  than CUAD/MAUD.
- If the score lands near `85%` or above with no dominant residue class, the
  CUAD result should be read as partly corpus ugliness rather than a general
  legal-ish extraction ceiling.
- If the score lands near `70%` with `query_surface_resolution` residue, CUAD's
  source-row access pressure transfers.

Intervention:

- Added PrivacyQA intake support to
  `scripts/sample_mrc_transfer_fixtures.py`.
- Added a reproducible `--privacyqa-record-ids` intake option so noisy rows can
  be excluded without teaching the compiler or selector anything about privacy
  policies. The ids are sampling metadata only.
- Measured dataset literalness before scoring:
  - Rows inspected: `194` across `7` policies.
  - Full answer literal in snippets: `69 / 194 = 35.6%`.
  - At least one answer line literal in snippets: `168 / 194 = 86.6%`.
- Built a source-aligned PrivacyQA-10 probe with ten single-question fixtures.
- Ran compile and QA through OpenRouter at `6` lanes using
  `qwen/qwen3.6-35b-a3b`.

After:

- Compile: `10 / 10` parsed.
- Compile totals: `66` candidate predicates, `287` admitted rows, `4` skipped
  rows.
- QA: `10 exact / 0 partial / 0 miss` over `10` questions.
- Exact rate: `100.0%`.
- Runtime load errors: `0`.
- Write proposals: `0`.
- Helper pressure: `0` helper rows; pressure label `no_helper_rows`.
- No non-exact coordinate distribution exists for this probe.

Artifacts:

- Samples:
  `tmp\mrc_transfer_samples_privacyqa10_20260513`
- Staged fixtures:
  `tmp\mrc_transfer_staged_privacyqa10_20260513`
- Compile:
  `tmp\mrc_transfer_compile_privacyqa10_source_records_20260513`
- QA:
  `tmp\mrc_transfer_qa_privacyqa10_source_records_20260513`
- Coordinate summary:
  `tmp\mrc_transfer_qa_privacyqa10_source_records_20260513\transfer_coordinate_summary.md`

Verification:

- `python -m pytest tests\test_sample_mrc_transfer_fixtures.py tests\test_summarize_mrc_transfer_qa.py tests\test_stage_incoming_fixtures.py -q`
  - `40 passed`
- `python scripts\summarize_mrc_transfer_qa.py --qa-root tmp\mrc_transfer_qa_privacyqa10_source_records_20260513`
  - `{"exact": 10, "exact_rate": 1.0, "miss": 0, "non_exact": 0, "not_judged": 0, "partial": 0, "question_count": 10}`

Lesson:

- PrivacyQA gives the clean legal-ish document-grounded result that CUAD and
  MAUD did not. On source-aligned policy snippets, current Prethinker handles
  the task as ordinary document QA.
- The legal/domain label was too coarse. Contract fields, merger-agreement
  taxonomies, and policy snippets have different transfer shapes.
- The result should not trigger policy-specific architecture. It is a
  measurement that the existing source-record path can answer clean
  privacy-policy questions when the evidence snippet actually bears the answer.
- The quality-filter step is part of dataset intake, not substrate. It prevents
  benchmark noise from masquerading as a boundary class.

Next pressure:

- Keep PrivacyQA as evidence that cleaner policy QA is inside the current set.
- Do not repair from PrivacyQA-10; there are no failures to explain.
- For the next transfer probe, choose either:
  - a larger PrivacyQA source-aligned sample to estimate stability; or
  - a different document-grounded legal/policy corpus to test whether the
    policy result transfers beyond this dataset.

### DT-020 - PrivacyQA-30 Stability Probe

Before:

- DT-019 landed at `10 / 10` exact on a curated source-aligned PrivacyQA probe.
- That was strong but too small. The next question was whether the result held
  across a wider policy sample, or whether the ten-row probe was lucky.

Prediction:

- A larger source-aligned sample should stay near the DT-018 high band if
  PrivacyQA is genuinely closer to source-grounded policy QA than CUAD/MAUD.
- Any non-exact rows must be manually audited before being called architecture
  gaps, because PrivacyQA already showed some question/snippet alignment noise.

Intervention:

- Counted available PrivacyQA rows under the current answer-length cap:
  - `170` rows with answers at or below `2500` chars.
  - `119` with query/evidence lexical overlap at least `0.2`.
  - `95` with overlap at least `0.33`.
  - `56` with overlap at least `0.5` across all splits; `43` in train.
- Built a deterministic `30`-fixture train sample from the overlap `>= 0.5`
  rows.
- Staged `30 / 30` fixtures.
- Ran compile on OpenRouter at `6` lanes, then retried `3` upstream `429`
  transport failures at `1` lane.
- Ran QA on OpenRouter at `6` lanes.

After:

- Compile after retry: `30 / 30` parsed.
- QA raw score: `26 exact / 1 partial / 3 miss` over `30`.
- Raw exact rate: `86.67%`.
- Runtime load errors: `0`.
- Write proposals: `0`.
- Helper pressure: `0` helper rows; pressure label `no_helper_rows`.
- Automated coordinate summary labeled the `4` non-exacts as
  `compile_surface_gap`.
- Manual audit changed the interpretation:
  - The non-exact rows are not clean compile-boundary evidence.
  - The reference snippets do not clearly answer the asked propositions in the
    location / marketing cases.
  - These are better treated as `dataset_answer_alignment_noise` until a cleaner
    source confirms the same shape.

Artifacts:

- Samples:
  `tmp\mrc_transfer_samples_privacyqa30_20260513`
- Staged fixtures:
  `tmp\mrc_transfer_staged_privacyqa30_20260513`
- Compile:
  `tmp\mrc_transfer_compile_privacyqa30_source_records_20260513`
- QA:
  `tmp\mrc_transfer_qa_privacyqa30_source_records_20260513`
- Coordinate summary:
  `tmp\mrc_transfer_qa_privacyqa30_source_records_20260513\transfer_coordinate_summary.md`

Verification:

- `python scripts\summarize_mrc_transfer_qa.py --qa-root tmp\mrc_transfer_qa_privacyqa30_source_records_20260513`
  - `{"exact": 26, "exact_rate": 0.8667, "miss": 3, "non_exact": 4, "not_judged": 0, "partial": 1, "question_count": 30}`
- OpenRouter provider behavior:
  - Initial compile at `6` lanes hit upstream `429` on `3` fixtures.
  - Narrow retry at `1` lane completed those `3` fixtures.
  - QA completed without provider failure.

Lesson:

- The DT-018 score-band prediction held: PrivacyQA-30 landed in the high band
  at `86.67%` raw exact, supporting the view that CUAD's lower score was partly
  corpus/interface ugliness rather than a global legal-ish extraction ceiling.
- The deeper lesson is intake quality. Lexical source-alignment reduces noise
  but does not prove the reference answer actually answers the question.
- No Prethinker repair should be made from these four non-exacts. The first
  repair target is the dataset-transfer intake audit: distinguish answer-bearing
  evidence from merely literal snippets.

Next pressure:

- Add a transfer-intake quality note or lightweight audit path that can flag
  `reference_does_not_answer_question` before compile/QA results are interpreted
  as architecture gaps.
- For domain transfer, prefer cleaner document-grounded datasets or manually
  audited slices over larger noisy PrivacyQA batches.
- Keep OpenRouter default at `6` lanes for normal batches; use `1`-lane retry
  for provider `429` residues.
