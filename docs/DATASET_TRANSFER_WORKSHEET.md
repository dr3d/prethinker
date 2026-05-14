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

### DT-021 - Transfer Intake Alignment Audit

Before:

- PrivacyQA-30's raw non-exacts were automatically labeled
  `compile_surface_gap`.
- Manual audit showed those four rows were better explained as noisy
  question/reference/source alignment: the source snippets did not clearly
  answer the asked proposition.
- Without a first-class intake label, benchmark noise would keep masquerading
  as architecture boundary.

Prediction:

- A lightweight fixture-free audit can catch the obvious alignment failures
  before coordinate summaries are interpreted.
- The audit must be conservative. It should separate `likely_reference_mismatch`
  from softer `review` rows, because lexical overlap is not a semantic judge.

Intervention:

- Added `scripts/audit_mrc_transfer_intake.py`.
- The audit reads incoming or staged MRC fixtures and compares:
  - non-generic question terms;
  - source/reference evidence terms;
  - whether the reference answer is literal in the source.
- Added conservative statuses:
  - `ok`;
  - `review`;
  - `likely_reference_mismatch`.
- Added `--intake-audit` support to
  `scripts/summarize_mrc_transfer_qa.py`.
- When a non-exact row is marked `likely_reference_mismatch`, the transfer
  coordinate summary now reports:
  - surface: `intake_quality_gap`;
  - coordinate: `dataset_answer_alignment_noise`.

After:

- PrivacyQA-30 intake audit:
  - Rows: `30`.
  - `ok`: `7`.
  - `review`: `19`.
  - `likely_reference_mismatch`: `4`.
- The four likely mismatches are the same four non-exact rows from PrivacyQA-30.
- PrivacyQA-30 coordinate summary with intake overlay:
  - Raw score remains `26 exact / 1 partial / 3 miss`.
  - Non-exact coordinate distribution becomes:
    - `dataset_answer_alignment_noise`: `4`.
  - Failure surface distribution becomes:
    - `intake_quality_gap`: `4`.
- PrivacyQA-10 intake audit:
  - Rows: `10`.
  - `likely_reference_mismatch`: `0`.

Artifacts:

- Audit script:
  `scripts\audit_mrc_transfer_intake.py`
- Tests:
  `tests\test_audit_mrc_transfer_intake.py`
- PrivacyQA-30 intake audit:
  `tmp\mrc_transfer_samples_privacyqa30_20260513\transfer_intake_audit_v3.md`
- PrivacyQA-30 coordinate summary with intake overlay:
  `tmp\mrc_transfer_qa_privacyqa30_source_records_20260513\transfer_coordinate_summary_with_intake.md`

Verification:

- `python -m pytest tests\test_audit_mrc_transfer_intake.py tests\test_summarize_mrc_transfer_qa.py -q`
  - `27 passed`
- `python scripts\summarize_mrc_transfer_qa.py --qa-root tmp\mrc_transfer_qa_privacyqa30_source_records_20260513 --intake-audit tmp\mrc_transfer_samples_privacyqa30_20260513\transfer_intake_audit_v3.json --out-json tmp\mrc_transfer_qa_privacyqa30_source_records_20260513\transfer_coordinate_summary_with_intake.json --out-md tmp\mrc_transfer_qa_privacyqa30_source_records_20260513\transfer_coordinate_summary_with_intake.md`

Lesson:

- Boundary hunting needs an intake-quality layer. Otherwise noisy external
  datasets produce false architecture coordinates.
- This is not a privacy-policy repair. The audit asks a reusable question:
  do the question's content terms appear in the provided evidence/reference
  surface strongly enough that a downstream miss should be interpreted as
  architecture?
- The audit is intentionally not a judge. `review` means "do not over-read this
  row"; only `likely_reference_mismatch` changes coordinate interpretation.

Next pressure:

- Use the intake overlay for future external dataset transfer summaries.
- Before adding new transfer datasets, run the intake audit on sampled fixtures
  and prefer rows with no `likely_reference_mismatch`.
- Next data move should be a cleaner document-grounded corpus, because PrivacyQA
  has now taught the methodology more about intake noise than about remaining
  Prethinker architecture gaps.

### DT-022 - Cross-Dataset Intake Lens

Before:

- DT-021 added the transfer-intake audit after PrivacyQA revealed that external
  rows can look like compile gaps while actually being question/reference/source
  alignment noise.
- The next decision was whether to continue PrivacyQA, return to SQuAD, or look
  for a new corpus.

Prediction:

- Cleaner open-ended extraction datasets should show low
  `likely_reference_mismatch`.
- Datasets whose task is option selection, legal taxonomy classification, or
  noisy snippet alignment should show more `review` or mismatch pressure.

Intervention:

- Ran the new intake audit across existing transfer sample roots.
- Re-rendered coordinate summaries with intake overlays for SQuAD, CUAD, MAUD,
  and PrivacyQA where QA artifacts were available.

After:

- SQuAD-10:
  - Intake: `65 ok / 6 review / 0 likely_reference_mismatch` over `71`.
  - QA: `62 exact / 1 partial / 8 miss`, exact `87.32%`.
  - Coordinates remain real architecture coordinates; no intake overlay changed
    them.
- CUAD-10:
  - Intake: `29 ok / 11 review / 0 likely_reference_mismatch` over `40`.
  - QA: `28 exact / 2 partial / 10 miss`, exact `70.0%`.
  - CUAD is ugly but still mostly answer-aligned enough to interpret.
- MAUD-10:
  - Intake: `5 ok / 35 review / 0 likely_reference_mismatch` over `40`.
  - QA: `17 exact / 1 partial / 22 miss`, exact `42.5%`.
  - The audit agrees with DT-017: MAUD is mostly taxonomy/rubric pressure, not
    clean extraction pressure.
- RACE-50 options:
  - Intake: `0 ok / 158 review / 19 likely_reference_mismatch` over `177`.
  - This lexical intake audit is not a good fit for option-selection surfaces;
    MCQ should be audited by option/proposition type, not reference literalness.
- PrivacyQA-30:
  - Intake: `7 ok / 19 review / 4 likely_reference_mismatch` over `30`.
  - Intake overlay moves the four non-exacts to
    `dataset_answer_alignment_noise`.

Artifacts:

- SQuAD intake:
  `tmp\mrc_transfer_samples_squad10_20260513\transfer_intake_audit.md`
- SQuAD coordinate summary with intake:
  `tmp\mrc_transfer_qa_squad10_source_records_20260513\transfer_coordinate_summary_with_intake.md`
- CUAD intake:
  `tmp\mrc_transfer_samples_cuad10_20260513\transfer_intake_audit.md`
- MAUD intake:
  `tmp\mrc_transfer_samples_maud10_20260513\transfer_intake_audit.md`

Verification:

- Intake audit ran successfully on SQuAD, RACE, CUAD, MAUD, and PrivacyQA sample
  roots.
- Coordinate summaries with intake overlays rendered for SQuAD, CUAD, MAUD, and
  PrivacyQA.

Lesson:

- The next clean measurement surface is SQuAD, not PrivacyQA. PrivacyQA is
  useful but noisy; SQuAD gives open-ended, source-grounded extraction with no
  likely reference/source mismatches in the current sample.
- The intake audit should be interpreted by dataset format. It is strong for
  open-ended extraction, useful for legal extraction, and not sufficient for MCQ
  option-selection tasks.

Next pressure:

- Widen SQuAD with the intake audit in the loop.
- Use the resulting non-exact coordinates as cleaner boundary evidence than
  PrivacyQA's noisy residue.

### DT-023 - SQuAD-30 Clean Transfer Measurement

Before:

- DT-022 selected SQuAD as the cleanest next measurement surface because
  PrivacyQA taught the transfer loop about intake noise, while SQuAD-10 had no
  likely reference/source mismatches.
- SQuAD-10 measured `62 exact / 1 partial / 8 miss` over `71`, exact `87.32%`.

Prediction:

- A wider SQuAD slice should stabilize the open-ended extraction score.
- Because the intake audit should remain clean, SQuAD non-exacts should be
  treated as architecture coordinates rather than dataset-alignment noise.

Intervention:

- Sampled `30` SQuAD validation passages with deterministic even spread.
- Staged them into transfer fixtures.
- Ran the transfer-intake audit before QA.
- Compiled all fixtures through OpenRouter at `6` lanes with source-record
  ledger facts enabled.
- Ran QA through OpenRouter at `6` lanes and summarized coordinates with the
  intake overlay.

After:

- Intake audit:
  - Rows: `171`.
  - `ok`: `163`.
  - `review`: `8`.
  - `likely_reference_mismatch`: `0`.
  - OK rate: `95.32%`.
- Compile:
  - Parsed: `30 / 30`.
  - Transport failures: `0`.
- QA:
  - Questions: `171`.
  - Exact / partial / miss: `134 / 5 / 32`.
  - Exact rate: `78.36%`.
  - Runtime load errors: `0`.
  - Write proposals: `0`.
  - Helper pressure: `bounded_helper_surface`, `1` row, `0.007` rows/exact.
- Non-exact proposition types:
  - `factual`: `33`.
  - `inference`: `2`.
  - `categorical`: `1`.
  - `synthesis`: `1`.
- Transfer coordinates:
  - `direct_compile_surface_gap`: `26`.
  - `query_surface_resolution`: `3`.
  - `answer_surface_mapping`: `2`.
  - `background_role_or_audience_fact`: `2`.
  - `false_or_exception_option_selection`: `1`.
  - `implicit_attitude_or_consequence`: `1`.
  - `judge_transport_uncertain`: `1`.
  - `title_theme_or_summary_answer`: `1`.

Artifacts:

- Samples:
  `tmp\mrc_transfer_samples_squad30_20260513`
- Staged fixtures:
  `tmp\mrc_transfer_staged_squad30_20260513`
- Compile artifacts:
  `tmp\mrc_transfer_compile_squad30_source_records_20260513`
- QA artifacts:
  `tmp\mrc_transfer_qa_squad30_source_records_20260513`
- Intake audit:
  `tmp\mrc_transfer_samples_squad30_20260513\transfer_intake_audit.md`
- Coordinate summary with intake:
  `tmp\mrc_transfer_qa_squad30_source_records_20260513\transfer_coordinate_summary_with_intake.md`

Verification:

- `python scripts\audit_mrc_transfer_intake.py --root tmp\mrc_transfer_samples_squad30_20260513 --out-json tmp\mrc_transfer_samples_squad30_20260513\transfer_intake_audit.json --out-md tmp\mrc_transfer_samples_squad30_20260513\transfer_intake_audit.md`
- `python scripts\run_domain_bootstrap_file_batch.py --dataset-root tmp\mrc_transfer_staged_squad30_20260513 --out-root tmp\mrc_transfer_compile_squad30_source_records_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 900 --compile-source --compile-flat-plus-plan-passes --focused-pass-ops-schema --source-record-ledger --source-record-ledger-facts`
- `python scripts\run_domain_bootstrap_qa_batch.py --dataset-root tmp\mrc_transfer_staged_squad30_20260513 --compile-root tmp\mrc_transfer_compile_squad30_source_records_20260513 --out-root tmp\mrc_transfer_qa_squad30_source_records_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 420 --no-cache`
- `python scripts\summarize_mrc_transfer_qa.py --qa-root tmp\mrc_transfer_qa_squad30_source_records_20260513 --intake-audit tmp\mrc_transfer_samples_squad30_20260513\transfer_intake_audit.json --out-json tmp\mrc_transfer_qa_squad30_source_records_20260513\transfer_coordinate_summary_with_intake.json --out-md tmp\mrc_transfer_qa_squad30_source_records_20260513\transfer_coordinate_summary_with_intake.md`

Lesson:

- SQuAD-30 is not an intake-quality problem. The row alignment is clean enough
  that the non-exacts should be treated as real boundary evidence.
- The dominant gap is value-bearing compile resolution: dense descriptive
  passages can produce predicates that name a property without binding the
  answer value. That is different from helper delivery pressure and different
  from PrivacyQA-style reference noise.
- The lower SQuAD-30 score does not contradict SQuAD-10. It reveals cluster
  sensitivity: a single dense event-description passage can contain many
  questions over the same under-resolved coordinate.

Next pressure:

- Audit the `direct_compile_surface_gap` cluster by shape, not by passage topic.
- Build a small unlike probe for value-bearing event attributes: event-to-date,
  event-to-location, event-to-participant, event-to-outcome, and acronym/name
  expansion. The probe must avoid SQuAD topic vocabulary while testing whether
  compile can bind extracted values instead of emitting unary marker facts.

### DT-024 - Event Attribute Value Probe Pair

Before:

- SQuAD-30 produced `26` `direct_compile_surface_gap` non-exacts.
- The largest cluster came from value-bearing event questions where the compile
  recognized properties such as date, location, participant, outcome, season,
  alternate label, or acronym context, but did not expose the answer value as a
  queryable coordinate.

Prediction:

- If value-bearing event attributes are a missing generic axis, an unlike probe
  should fail even when topic vocabulary is replaced.
- If the axis is already inside the set, focused probes should pass and the
  SQuAD cluster should be treated as a denser resolution problem or a
  run-specific compile variant.

Intervention:

- Added a sectioned unlike probe for event-to-value attributes:
  `experiments\boundary_probes\dataset_transfer_stage2\event_attribute_value_ladder`.
- Added a denser paragraph-shaped variant with adjacent participants, score,
  event date, venue, city, cycle, archival label, acronym expansion, and final
  appointments:
  `experiments\boundary_probes\dataset_transfer_stage2\dense_event_attribute_value_ladder`.
- Compiled and ran QA for both probes through OpenRouter at the normal `6`-lane
  ceiling.

After:

- Sectioned event-value probe:
  - Compile parsed: `true`.
  - Admitted / skipped: `28 / 0`.
  - QA: `10 exact / 0 partial / 0 miss`.
  - Helper rows: `0`.
- Dense event-value probe:
  - Compile parsed: `true`.
  - Admitted / skipped: `36 / 2`.
  - QA: `12 exact / 0 partial / 0 miss`.
  - Helper rows: `0`.

Artifacts:

- Sectioned compile:
  `tmp\boundary_probe_compile_event_attribute_value_20260513`
- Sectioned QA:
  `tmp\boundary_probe_qa_event_attribute_value_20260513`
- Dense compile:
  `tmp\boundary_probe_compile_dense_event_attribute_value_20260513`
- Dense QA:
  `tmp\boundary_probe_qa_dense_event_attribute_value_20260513`

Verification:

- `python scripts\run_domain_bootstrap_file_batch.py --dataset-root experiments\boundary_probes\dataset_transfer_stage2 --fixture event_attribute_value_ladder --out-root tmp\boundary_probe_compile_event_attribute_value_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 900 --compile-source --compile-flat-plus-plan-passes --focused-pass-ops-schema --source-record-ledger --source-record-ledger-facts`
- `python scripts\run_domain_bootstrap_qa_batch.py --dataset-root experiments\boundary_probes\dataset_transfer_stage2 --fixture event_attribute_value_ladder --compile-root tmp\boundary_probe_compile_event_attribute_value_20260513 --out-root tmp\boundary_probe_qa_event_attribute_value_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 420 --no-cache`
- `python scripts\run_domain_bootstrap_file_batch.py --dataset-root experiments\boundary_probes\dataset_transfer_stage2 --fixture dense_event_attribute_value_ladder --out-root tmp\boundary_probe_compile_dense_event_attribute_value_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 900 --compile-source --compile-flat-plus-plan-passes --focused-pass-ops-schema --source-record-ledger --source-record-ledger-facts`
- `python scripts\run_domain_bootstrap_qa_batch.py --dataset-root experiments\boundary_probes\dataset_transfer_stage2 --fixture dense_event_attribute_value_ladder --compile-root tmp\boundary_probe_compile_dense_event_attribute_value_20260513 --out-root tmp\boundary_probe_qa_dense_event_attribute_value_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 420 --no-cache`

Lesson:

- Value-bearing event attributes are not a missing generic axis. Both the
  sectioned and dense unlike probes are fully inside the set.
- The SQuAD event cluster should not trigger a repair by itself. Its miss shape
  now needs a replay and density audit: repeated subject aliases, acronym
  expansion, title/label handling, and event-outcome relations may be causing a
  bad compile variant even though the generic machinery can express the
  coordinate.
- This is the boundary-hunt discipline working: measurement created a candidate
  coordinate, the unlike probes tested the generic axis, and the result moved
  the pressure from missing-axis repair to cluster replay.

Next pressure:

- Recompile and replay only the clustered SQuAD event fixture to check run
  variance before designing any repair.
- If replay still emits unary/property-marker facts for answer-bearing event
  attributes, classify the cluster by density mechanism rather than by source
  topic.

### DT-025 - SQuAD Event Cluster Replay

Before:

- SQuAD-30's largest apparent boundary was one event-description fixture with
  `6 exact / 1 partial / 23 miss`.
- DT-024 showed that generic value-bearing event attributes pass in both
  sectioned and dense unlike probes, so a repair from the original cluster
  would have risked chasing a bad compile draw.

Prediction:

- If the cluster represents a stable architecture gap, a replay should continue
  to miss most value-bearing event questions.
- If the cluster is compile-run variance, replay should recover the ordinary
  event values and shrink the residue to a much smaller set.

Intervention:

- Recompiled only the clustered SQuAD event fixture through OpenRouter at `6`
  lanes with the same source-record ledger settings.
- Replayed QA for the same `30` questions against the new compile.
- Summarized the replay with the existing SQuAD intake audit overlay.

After:

- Replay compile:
  - Parsed: `true`.
  - Admitted / skipped: `29 / 0`.
  - The replay compile exposed value-bearing predicates such as `event_date/2`,
    `event_location/2`, `venue_name/2`, `winner/2`, `score/2`,
    `conference_of/2`, `anniversary_theme/2`, `naming_override/2`, and
    `season_of/2`.
- Replay QA:
  - Questions: `30`.
  - Exact / partial / miss: `27 / 0 / 3`.
  - Exact rate: `90.0%`.
  - Helper rows: `0`.
- If this replay replaces the original bad cluster inside SQuAD-30, the adjusted
  slice becomes approximately:
  - `155 exact / 4 partial / 12 miss` over `171`.
  - Exact rate: `90.64%`.
- Stable replay residue:
  - Acronym expansion for inline parenthetical conference names: `2`.
  - Hypothetical/suspended alternate label: `1`.

Artifacts:

- Replay compile:
  `tmp\mrc_transfer_compile_squad30_event_cluster_replay_20260513`
- Replay QA:
  `tmp\mrc_transfer_qa_squad30_event_cluster_replay_20260513`
- Replay coordinate summary:
  `tmp\mrc_transfer_qa_squad30_event_cluster_replay_20260513\transfer_coordinate_summary_with_intake.md`

Verification:

- `python scripts\run_domain_bootstrap_file_batch.py --dataset-root tmp\mrc_transfer_staged_squad30_20260513 --fixture squad_default_validation_00000_super_bowl_50 --out-root tmp\mrc_transfer_compile_squad30_event_cluster_replay_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 900 --compile-source --compile-flat-plus-plan-passes --focused-pass-ops-schema --source-record-ledger --source-record-ledger-facts`
- `python scripts\run_domain_bootstrap_qa_batch.py --dataset-root tmp\mrc_transfer_staged_squad30_20260513 --fixture squad_default_validation_00000_super_bowl_50 --compile-root tmp\mrc_transfer_compile_squad30_event_cluster_replay_20260513 --out-root tmp\mrc_transfer_qa_squad30_event_cluster_replay_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 420 --no-cache`
- `python scripts\summarize_mrc_transfer_qa.py --qa-root tmp\mrc_transfer_qa_squad30_event_cluster_replay_20260513 --intake-audit tmp\mrc_transfer_samples_squad30_20260513\transfer_intake_audit.json --out-json tmp\mrc_transfer_qa_squad30_event_cluster_replay_20260513\transfer_coordinate_summary_with_intake.json --out-md tmp\mrc_transfer_qa_squad30_event_cluster_replay_20260513\transfer_coordinate_summary_with_intake.md`

Lesson:

- The original SQuAD-30 score was materially distorted by one unstable compile
  draw. The architecture can express the event-value coordinates; replay moved
  the cluster from `20%` exact to `90%` exact.
- Boundary measurements over hosted LLM compiles need replay discipline for
  large one-fixture clusters. A cluster is not architecture until it survives a
  second compile.
- The stable residue is sharper than the original boundary: inline parenthetical
  acronym expansion and hypothetical/suspended alternate labels.

Next pressure:

- Add an unlike probe for inline acronym expansion and hypothetical alternate
  labels, because those are the stable residues after replay.
- Do not repair from the original `23`-miss cluster.

### DT-026 - Inline Parenthetical Alias Repair

Before:

- DT-025 reduced the SQuAD event cluster to one stable alternate-label miss and
  two acronym-expansion misses.
- The focused inline-alias probe separated these shapes:
  - Explicit `stands for` alias: inside.
  - Hypothetical/ordinary alternate label: inside.
  - Parenthetical full-name abbreviation such as `Full Name (ABC)`: outside.

Prediction:

- A fixture-free repair should not name any dataset acronym or event.
- The reusable substrate should expose source-local parenthetical aliases as
  deterministic source-record surfaces, then let ordinary QA planning query
  those surfaces.

Intervention:

- Added deterministic source-record alias facts for narrow
  `Full Name (ABC)` patterns:
  - `source_record_parenthetical_alias(Row, Abbreviation, Expansion)`.
  - `source_record_alias(Row, Abbreviation, Expansion)`.
  - `source_record_alias(Row, Expansion, Abbreviation)`.
- The trigger is intentionally constrained:
  - parenthetical token must be short uppercase alphanumeric punctuation;
  - preceding phrase must contain at least two capitalized words;
  - abbreviation letters must match the capitalized-word initials;
  - leading connectors/articles before the expansion are dropped;
  - lowercase parentheticals such as role notes are ignored.
- Added tests covering direct parenthetical aliases, a phrase preceded by
  connector words, and a lowercase non-alias parenthetical.

After:

- Focused inline-alias probe before repair:
  - QA: `4 exact / 0 partial / 4 miss`.
- Focused inline-alias probe after repair:
  - QA: `8 exact / 0 partial / 0 miss`.
  - Helper rows: `0`.
- SQuAD event-cluster replay before repair:
  - QA: `27 exact / 0 partial / 3 miss`.
- SQuAD event-cluster replay after repair:
  - QA: `29 exact / 0 partial / 1 miss`.
  - Helper rows: `0`.
- If this repaired replay replaces the original unstable cluster inside
  SQuAD-30, the adjusted slice becomes:
  - `157 exact / 4 partial / 10 miss` over `171`.
  - Exact rate: `91.81%`.
- Remaining SQuAD event-cluster residue:
  - one general-name question asking for the name of the championship game,
    where the compiled KB has the instance-specific event but not a class/name
    relation for the game family.

Artifacts:

- Source-record repair:
  `src\source_record_ledger.py`
- Test coverage:
  `tests\test_source_record_ledger.py`
- Inline-alias probe:
  `experiments\boundary_probes\dataset_transfer_stage2\inline_alias_label_ladder`
- Pre-repair inline-alias QA:
  `tmp\boundary_probe_qa_inline_alias_label_20260513`
- Post-repair inline-alias QA:
  `tmp\boundary_probe_qa_inline_alias_label_repair_20260513`
- Post-repair SQuAD event-cluster replay:
  `tmp\mrc_transfer_qa_squad30_event_cluster_alias_repair_20260513`

Verification:

- `python -m pytest tests\test_source_record_ledger.py tests\test_domain_bootstrap_file.py tests\test_domain_bootstrap_qa.py tests\test_summarize_mrc_transfer_qa.py -q`
  - `211 passed`
- `python scripts\run_domain_bootstrap_file_batch.py --dataset-root experiments\boundary_probes\dataset_transfer_stage2 --fixture inline_alias_label_ladder --out-root tmp\boundary_probe_compile_inline_alias_label_repair_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 900 --compile-source --compile-flat-plus-plan-passes --focused-pass-ops-schema --source-record-ledger --source-record-ledger-facts`
- `python scripts\run_domain_bootstrap_qa_batch.py --dataset-root experiments\boundary_probes\dataset_transfer_stage2 --fixture inline_alias_label_ladder --compile-root tmp\boundary_probe_compile_inline_alias_label_repair_20260513 --out-root tmp\boundary_probe_qa_inline_alias_label_repair_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 420 --no-cache`
- `python scripts\run_domain_bootstrap_file_batch.py --dataset-root tmp\mrc_transfer_staged_squad30_20260513 --fixture squad_default_validation_00000_super_bowl_50 --out-root tmp\mrc_transfer_compile_squad30_event_cluster_alias_repair_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 900 --compile-source --compile-flat-plus-plan-passes --focused-pass-ops-schema --source-record-ledger --source-record-ledger-facts`
- `python scripts\run_domain_bootstrap_qa_batch.py --dataset-root tmp\mrc_transfer_staged_squad30_20260513 --fixture squad_default_validation_00000_super_bowl_50 --compile-root tmp\mrc_transfer_compile_squad30_event_cluster_alias_repair_20260513 --out-root tmp\mrc_transfer_qa_squad30_event_cluster_alias_repair_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 420 --no-cache`

Lesson:

- This is a real boundary extension, not fixture learning. The repair names a
  source-shape: uppercase parenthetical abbreviations whose letters match the
  immediately preceding capitalized phrase.
- Trigger discipline matters. The repair does not depend on English words such
  as `stands for`; it uses punctuation, capitalization, and initial alignment.
  It also refuses lowercase parenthetical notes.
- The repair belongs in source-record scaffolding rather than a dataset adapter:
  many external corpora use `Full Name (ABC)` in ordinary prose, and later QA
  can query the source-local alias without inventing global synonym truth.

Next pressure:

- Decide whether the remaining SQuAD-30 residue is worth a focused probe now
  or whether to widen SQuAD with replay-on-cluster discipline first.
- The remaining SQuAD event-cluster miss is a class/name relation, not an alias
  relation; do not fold it into this repair.

### DT-027 - Full SQuAD-30 Alias-Repair Remeasurement

Before:

- DT-026 proved the parenthetical-alias repair on an unlike probe and on the
  unstable SQuAD event cluster replay.
- The best SQuAD-30 number after DT-026 was still a hand-adjusted estimate:
  replace the original unstable event cluster with its repaired replay and the
  slice becomes `157 exact / 4 partial / 10 miss` over `171`.
- That estimate was useful but not a clean corpus measurement. The corpus
  needed a fresh full compile and QA pass with the alias substrate enabled.

Prediction:

- The alias repair should hold without helper growth.
- A full fresh hosted compile should land near the adjusted `90%` band, but not
  necessarily equal the hand-substituted score because hosted compile variance
  can move small fixtures and one-fixture clusters.
- Remaining residue should be treated as coordinates, not as permission for
  fixture-specific tuning.

Intervention:

- Recompiled all `30` staged SQuAD fixtures through OpenRouter at the normal
  `6`-lane ceiling with source-record ledger facts enabled.
- Ran full QA against that compile with no cache.
- Re-rendered the transfer coordinate summary with the intake audit overlay.

After:

- Full SQuAD-30 alias-repair run:
  - Questions: `171`.
  - Exact / partial / miss: `155 / 4 / 12`.
  - Exact rate: `90.64%`.
  - Runtime load errors: `0`.
  - Write proposals: `0`.
  - Helper rows: `0`.
  - Helper pressure: `no_helper_rows`.
- Proposition-type residue:
  - `factual`: `13`.
  - `inference`: `2`.
  - `comparative`: `1`.
- Coordinate residue:
  - `direct_compile_surface_gap`: `7`.
  - `false_or_exception_option_selection`: `3`.
  - `implicit_attitude_or_consequence`: `2`.
  - `background_role_or_audience_fact`: `1`.
  - `comparative_or_temporal_resolution`: `1`.
  - `hybrid_join_resolution`: `1`.
  - `query_surface_resolution`: `1`.
- Failure surfaces:
  - `compile_surface_gap`: `12`.
  - `hybrid_join_gap`: `2`.
  - `answer_surface_gap`: `1`.
  - `query_surface_gap`: `1`.
- The full run is slightly below the DT-026 hand-adjusted estimate because the
  fresh compile moved other small fixtures. That is measurement noise to manage,
  not a contradiction of the alias repair.

Artifacts:

- Full alias-repair compile:
  `tmp\mrc_transfer_compile_squad30_alias_repair_full_20260513`
- Full alias-repair QA:
  `tmp\mrc_transfer_qa_squad30_alias_repair_full_20260513`
- Coordinate summary:
  `tmp\mrc_transfer_qa_squad30_alias_repair_full_20260513\transfer_coordinate_summary_with_intake.md`
- Coordinate summary JSON:
  `tmp\mrc_transfer_qa_squad30_alias_repair_full_20260513\transfer_coordinate_summary_with_intake.json`

Verification:

- `python scripts\run_domain_bootstrap_file_batch.py --dataset-root tmp\mrc_transfer_staged_squad30_20260513 --out-root tmp\mrc_transfer_compile_squad30_alias_repair_full_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 900 --compile-source --compile-flat-plus-plan-passes --focused-pass-ops-schema --source-record-ledger --source-record-ledger-facts`
- `python scripts\run_domain_bootstrap_qa_batch.py --dataset-root tmp\mrc_transfer_staged_squad30_20260513 --compile-root tmp\mrc_transfer_compile_squad30_alias_repair_full_20260513 --out-root tmp\mrc_transfer_qa_squad30_alias_repair_full_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 420 --no-cache`
- `python scripts\summarize_mrc_transfer_qa.py --qa-root tmp\mrc_transfer_qa_squad30_alias_repair_full_20260513 --intake-audit tmp\mrc_transfer_samples_squad30_20260513\transfer_intake_audit.json --out-json tmp\mrc_transfer_qa_squad30_alias_repair_full_20260513\transfer_coordinate_summary_with_intake.json --out-md tmp\mrc_transfer_qa_squad30_alias_repair_full_20260513\transfer_coordinate_summary_with_intake.md`

Lesson:

- SQuAD transfer is now a high-band measurement surface. The clean rerun lands
  at `90.64%` exact with zero helper rows, which supports the claim that
  source-record alias scaffolding extended the boundary without creating a new
  helper dependency.
- Hosted compile variance is now a first-class measurement fact. The original
  SQuAD-30 event cluster was a bad draw; the repaired event replay was stronger;
  the full fresh rerun introduced smaller movement elsewhere. Large local drops
  should be replayed before any repair is designed.
- The remaining residue is heterogeneous. It includes direct missing compile
  coordinates, negative/exception answer surfaces, event-sequence joins,
  temporal later-state resolution, query plans missing an available fact, and a
  small amount of dataset/reference ambiguity.
- The next repair should come from a repeated unlike probe, not from a single
  SQuAD row or a dataset-specific phrase.

Next pressure:

- Build a residue board that separates:
  - stable transferable architecture candidates;
  - replay-needed compile variance;
  - likely dataset/reference ambiguity.
- The leading candidate for the next focused probe is negative or exception
  answer-surface handling, but the `false_or_exception_option_selection` bucket
  is mixed and must be audited before any repair.

### DT-028 - SQuAD-30 Residue Board

Before:

- DT-027 reduced the SQuAD-30 transfer surface to `16` non-exact rows.
- The largest named bucket, `direct_compile_surface_gap`, was still too broad
  to act on. The second bucket, `false_or_exception_option_selection`, mixed
  real negative-answer behavior with alternate-label and possible
  dataset/reference ambiguity.

Prediction:

- A manual board should separate repair candidates from noisy measurement
  residue.
- The next focused probe should target a recurring proposition shape, not a
  source topic or answer string.

Intervention:

- Read the full SQuAD-30 alias-repair coordinate summary and grouped each
  non-exact by actionability.

After:

- Stable transferable architecture candidates:
  - Negative or exception answer surfaces: explicit no-control evidence,
    exceptions to an ordinary rule, and possibly false-option/refuting evidence.
  - Query-surface resolution when the needed fact exists in the KB but the query
    plan retrieves an adjacent predicate.
  - Event-sequence ordinal joins where the answer requires binding the first,
    last, next, or later event in a sequence to an actor or value.
  - Later-state temporal comparison where an entity has one role during an
    earlier context and a different role later.
- Replay-needed compile variance:
  - City/location hierarchy under an event venue.
  - Spouse-property date joins.
  - Reform or process start-date facts.
  - Property-list completeness.
  - Institutional target lists.
  - Role facts that are present in source text but omitted from structured
    compile.
- Likely dataset/reference ambiguity or weak single-row evidence:
  - A metric-system question whose reference answer names a non-metric unit.
  - A class/name relation that may be answerable by source text but should not
    be treated as alias repair.
  - Single inference rows that require social or rhetorical bridging rather than
    directly stated extraction.

Artifacts:

- SQuAD-30 alias-repair coordinate summary:
  `tmp\mrc_transfer_qa_squad30_alias_repair_full_20260513\transfer_coordinate_summary_with_intake.md`

Verification:

- Manual pass over all `16` non-exact rows from the DT-027 summary.

Lesson:

- The next useful pressure is not another broad SQuAD score. SQuAD is now high
  enough that the residue needs small unlike probes.
- Negative or exception answer surfaces are the cleanest immediate probe target
  because they recur across external rows and are not specific to any source
  topic. The probe must distinguish explicit negative evidence from
  counterfactual labels and bad references.
- Query-surface misses are also important, but the current evidence is nearly a
  duplicated row. It should wait until a focused negative/exception probe tells
  us whether explicit negation is already inside the set.

Next pressure:

- Add an unlike negative/exception answer-surface probe with no SQuAD vocabulary.
- Run compile and QA first. Do not repair unless the focused probe exposes a
  stable generic miss.

### DT-029 - Negative and Exception Surface Repair

Before:

- DT-028 selected negative/exception answer surfaces as the next focused probe.
- The SQuAD residue included explicit no-control evidence and other exception
  or false-answer surfaces, but the bucket was mixed with alternate labels and
  likely reference ambiguity.

Prediction:

- If explicit negative surfaces are already inside the set, an unlike probe
  should pass without repair.
- If the probe fails, the repair should be phrased at the source-fidelity level:
  preserve explicit prohibitions, lack of authority, no-control/no-veto,
  exemptions, and outside-scope statements as queryable source facts when the
  profile offers a compatible predicate.

Intervention:

- Added a new unlike probe:
  `experiments\boundary_probes\dataset_transfer_stage2\negative_exception_answer_surface_ladder`.
- The probe tests:
  - explicit no-control answer;
  - lack of veto;
  - outside-scope exclusion;
  - exemption from a general rule;
  - manual rather than automatic routing;
  - allowed approval role;
  - explicitly barred approval role;
  - positive neighboring workflow role.
- First run:
  - Compile parsed: `true`.
  - Admitted / skipped: `19 / 11`.
  - QA: `6 exact / 0 partial / 2 miss`.
  - The profile proposed negative predicates, but compile omitted the negative
    facts.
- Added source-pass compile guidance:
  - explicit negative surfaces should be preserved as positive assertions on
    compatible prohibition/forbidden/exempt/outside-scope/lacks-authority
    predicates;
  - do not encode them as general negative-polarity facts;
  - do not preserve only the adjacent positive permission.
- Second run:
  - Compile parsed: `true`.
  - Admitted / skipped: `23 / 7`.
  - QA: `6 exact / 1 partial / 1 miss`.
  - The not-allowed approval role repaired, but the no-veto row still missed
    because the profile exposed only a positive `has_veto/2` predicate and a
    note that negation mattered.
- Added profile-bootstrap and profile-review guidance:
  - explicit negative surfaces need their own queryable predicate when the
    source treats them as facts;
  - do not rely on a positive predicate such as `has_veto/2` plus an admission
    note that negation is significant.
- Final run:
  - Compile parsed: `true`.
  - Admitted / skipped: `62 / 5`.
  - QA: `8 exact / 0 partial / 0 miss`.
  - Helper rows: `0`.

Artifacts:

- Probe:
  `experiments\boundary_probes\dataset_transfer_stage2\negative_exception_answer_surface_ladder`
- Initial compile:
  `tmp\boundary_probe_compile_negative_exception_answer_surface_20260513`
- Initial QA:
  `tmp\boundary_probe_qa_negative_exception_answer_surface_20260513`
- Compile-guidance replay:
  `tmp\boundary_probe_compile_negative_exception_answer_surface_repair_20260513`
- Compile-guidance QA:
  `tmp\boundary_probe_qa_negative_exception_answer_surface_repair_20260513`
- Profile-guidance replay:
  `tmp\boundary_probe_compile_negative_exception_answer_surface_profile_repair_20260513`
- Profile-guidance QA:
  `tmp\boundary_probe_qa_negative_exception_answer_surface_profile_repair_20260513`

Verification:

- `python -m pytest tests\test_profile_bootstrap.py::ProfileBootstrapTests::test_bootstrap_guidance_preserves_source_records_reporters_and_conditions tests\test_domain_bootstrap_file.py::test_source_pass_ops_guidance_preserves_explicit_negative_surfaces -q`
  - `2 passed`
- `python scripts\run_domain_bootstrap_file_batch.py --dataset-root experiments\boundary_probes\dataset_transfer_stage2 --fixture negative_exception_answer_surface_ladder --out-root tmp\boundary_probe_compile_negative_exception_answer_surface_profile_repair_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 900 --compile-source --compile-flat-plus-plan-passes --focused-pass-ops-schema --source-record-ledger --source-record-ledger-facts`
- `python scripts\run_domain_bootstrap_qa_batch.py --dataset-root experiments\boundary_probes\dataset_transfer_stage2 --fixture negative_exception_answer_surface_ladder --compile-root tmp\boundary_probe_compile_negative_exception_answer_surface_profile_repair_20260513 --out-root tmp\boundary_probe_qa_negative_exception_answer_surface_profile_repair_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 420 --no-cache`

Lesson:

- Negative surfaces are two-stage architecture. The profile must expose a
  predicate that can carry the negative relation, and the source-pass compiler
  must admit the explicitly stated negative relation as a positive fact on that
  predicate.
- The old failure was not that the harness needed source-specific words. It was
  that profile design sometimes represented `no veto` as `has_veto/2` plus a
  note. That is not queryable under the current safe-negation policy.
- The repair remains fixture-free: it names structural source surfaces, not
  specific offices, documents, answer strings, or dataset rows.
- The final compile admitted many more facts (`62`) than the first run (`19`).
  That is acceptable for this tiny probe, but broader replay should watch for
  profile-guidance over-breadth before declaring this repaired across SQuAD.

Next pressure:

- Run focused tests around profile/source-pass guidance.
- Replay the SQuAD-30 residue row with explicit no-control evidence and, if
  cheap, the full SQuAD-30 alias-repair corpus to measure transfer. Treat a
  broader score change as measurement evidence, not permission for new
  fixture-specific tuning.

### DT-030 - Negative Surface SQuAD Residue Replay

Before:

- DT-029 repaired the unlike negative/exception probe to `8 exact / 0 partial /
  0 miss`.
- The repair changed profile design and source-pass compile guidance, so the
  next question was whether it transferred to the SQuAD residue row that
  triggered the pressure.

Prediction:

- If the repair is genuinely structural, the SQuAD fixture containing explicit
  no-control evidence should replay cleanly without helper growth.
- If it only solved the focused probe, the no-control row should remain an
  answer-surface or compile-surface miss.

Intervention:

- Recompiled only the SQuAD fixture containing the explicit no-control question
  through OpenRouter at `6` lanes.
- Replayed QA for that fixture with no cache.

After:

- SQuAD negative-surface fixture replay:
  - Compile parsed: `true`.
  - Admitted / skipped: `20 / 0`.
  - QA: `5 exact / 0 partial / 0 miss`.
  - Helper rows: `0`.
  - Runtime load errors: `0`.
  - Write proposals: `0`.

Artifacts:

- Replay compile:
  `tmp\mrc_transfer_compile_squad30_negative_surface_replay_20260513`
- Replay QA:
  `tmp\mrc_transfer_qa_squad30_negative_surface_replay_20260513`

Verification:

- `python -m pytest tests\test_profile_bootstrap.py tests\test_domain_bootstrap_file.py::test_source_pass_ops_guidance_preserves_explicit_negative_surfaces -q`
  - `16 passed`
- `python scripts\run_domain_bootstrap_file_batch.py --dataset-root tmp\mrc_transfer_staged_squad30_20260513 --fixture squad_default_validation_00007_sky_united_kingdom --out-root tmp\mrc_transfer_compile_squad30_negative_surface_replay_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 900 --compile-source --compile-flat-plus-plan-passes --focused-pass-ops-schema --source-record-ledger --source-record-ledger-facts`
- `python scripts\run_domain_bootstrap_qa_batch.py --dataset-root tmp\mrc_transfer_staged_squad30_20260513 --fixture squad_default_validation_00007_sky_united_kingdom --compile-root tmp\mrc_transfer_compile_squad30_negative_surface_replay_20260513 --out-root tmp\mrc_transfer_qa_squad30_negative_surface_replay_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 420 --no-cache`

Lesson:

- The negative-surface repair transferred to the external row that motivated
  the probe. That strengthens DT-029 from focused-probe success to at least one
  unlike external replay success.
- This does not prove all negative/exception external rows are solved. It proves
  that explicit no-control evidence should no longer be treated as a SQuAD-only
  residue.
- The next broad run should be interpreted carefully because full hosted
  compiles still move. The repair is real; the exact corpus score may still
  vary by compile draw.

Next pressure:

- Run a cheap full test suite slice, then commit this boundary step.
- After commit, run a full SQuAD-30 remeasure if OpenRouter is healthy and use
  the result as measurement, not as a new repair mandate.

### DT-031 - Full SQuAD-30 Negative-Surface Remeasurement

Before:

- DT-030 proved the negative-surface repair on the targeted SQuAD residue
  fixture: `5 exact / 0 partial / 0 miss`.
- The previous full SQuAD-30 anchor after alias repair was `155 exact / 4
  partial / 12 miss` over `171`, exact `90.64%`.

Prediction:

- The explicit no-control residue should stay solved in a full run.
- The full score might not move monotonically because hosted compiles can
  change other fixture surfaces even when the targeted repair transfers.

Intervention:

- Recompiled the full SQuAD-30 staged set through OpenRouter at `6` lanes with
  alias and negative-surface repairs active.
- Ran full QA with no cache.
- Rendered the standard coordinate summary with the intake audit overlay.

After:

- Full SQuAD-30 negative-surface run:
  - Questions: `171`.
  - Exact / partial / miss: `152 / 2 / 17`.
  - Exact rate: `88.89%`.
  - Runtime load errors: `0`.
  - Write proposals: `0`.
  - Helper rows: `0`.
  - Helper pressure: `no_helper_rows`.
- Compared to the previous full alias-repair anchor:
  - `11` previous non-exacts resolved, including the explicit no-control row,
    several prior compile gaps, one event-sequence row, and one likely bad
    reference row.
  - `5` non-exacts persisted across both full runs.
  - `14` new or returned non-exacts appeared, concentrated in direct compile
    gaps plus a few query and hybrid joins.
- Current residue:
  - Proposition types: `18 factual`, `1 categorical`.
  - Coordinates:
    - `direct_compile_surface_gap`: `14`.
    - `query_surface_resolution`: `2`.
    - `comparative_or_temporal_resolution`: `1`.
    - `false_or_exception_option_selection`: `1`.
    - `hybrid_join_resolution`: `1`.
  - Failure surfaces:
    - `compile_surface_gap`: `15`.
    - `query_surface_gap`: `2`.
    - `answer_surface_gap`: `1`.
    - `hybrid_join_gap`: `1`.

Artifacts:

- Full compile:
  `tmp\mrc_transfer_compile_squad30_negative_surface_full_20260513`
- Full QA:
  `tmp\mrc_transfer_qa_squad30_negative_surface_full_20260513`
- Coordinate summary:
  `tmp\mrc_transfer_qa_squad30_negative_surface_full_20260513\transfer_coordinate_summary_with_intake.md`

Verification:

- `python scripts\run_domain_bootstrap_file_batch.py --dataset-root tmp\mrc_transfer_staged_squad30_20260513 --out-root tmp\mrc_transfer_compile_squad30_negative_surface_full_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 900 --compile-source --compile-flat-plus-plan-passes --focused-pass-ops-schema --source-record-ledger --source-record-ledger-facts`
- `python scripts\run_domain_bootstrap_qa_batch.py --dataset-root tmp\mrc_transfer_staged_squad30_20260513 --compile-root tmp\mrc_transfer_compile_squad30_negative_surface_full_20260513 --out-root tmp\mrc_transfer_qa_squad30_negative_surface_full_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 420 --no-cache`
- `python scripts\summarize_mrc_transfer_qa.py --qa-root tmp\mrc_transfer_qa_squad30_negative_surface_full_20260513 --intake-audit tmp\mrc_transfer_samples_squad30_20260513\transfer_intake_audit.json --out-json tmp\mrc_transfer_qa_squad30_negative_surface_full_20260513\transfer_coordinate_summary_with_intake.json --out-md tmp\mrc_transfer_qa_squad30_negative_surface_full_20260513\transfer_coordinate_summary_with_intake.md`

Lesson:

- The targeted repair transferred, but the full corpus score dipped because the
  hosted compile drew different surfaces elsewhere. This confirms the current
  operating rule: full-corpus remeasurement is necessary, but broad score
  movement alone is not a repair mandate.
- SQuAD-30 remains a high-band transfer surface with no helper rows. The more
  important signal is now stability by coordinate: the no-control row is
  solved; the persistent pressure is query-surface resolution and a small set of
  repeated direct compile gaps.
- The apparent compile-gap count is partly a classifier artifact. Some rows
  explicitly have the needed fact in the KB but are still summarized as compile
  gaps because the query plan used an adjacent predicate. These should be
  audited under query-surface resolution before any compile repair.

Next pressure:

- Do not repair from the full run's new one-off compile gaps yet.
- Build an unlike query-surface probe for cases where the KB contains the
  answer-bearing fact but the query plan retrieves an adjacent predicate.
- Use the duplicate `in addition to` residue as pressure shape only; the probe
  must use unlike vocabulary and no SQuAD entities.

### DT-032 - Adjacent Relation Query-Surface Probe

Date: 2026-05-13

Before:

- DT-031 showed that some apparent compile gaps were really query-surface
  misses: the compiled KB contained an answer-bearing fact, but the query plan
  retrieved only a neighboring baseline relation.
- The pressure shape was complementary phrasing: a question asks for what was
  present in addition to, besides, along with, apart from, or not only but also
  a named baseline relation.

Prediction:

- If the boundary is query-surface resolution, an unlike probe should compile
  the answer facts but miss when QA stops at the baseline relation.
- A useful repair should not name a dataset, source row, answer string, or local
  entity. It should retrieve sibling predicates over the same grounded subject
  when complementary wording asks for the extra relation.

Intervention:

- Added `adjacent_relation_query_surface_ladder`, a small unlike probe for
  complementary relation retrieval.
- Initial OpenRouter QA on the existing compile scored `4 / 0 / 4` with zero
  helper rows. Three misses had the answer-bearing facts already compiled, but
  QA queried only baseline relations such as possession, return, or assignment.
- Added a generic query-planning rule and deterministic query hint:
  complementary questions now add sibling-predicate probes over the same
  grounded subject from the compiled KB inventory.
- Added judge guidance that predicate names are answer-bearing relation
  surfaces and that complementary possession/carry wording may be answered by
  an abstract sibling predicate rather than the baseline possession predicate.

After:

- Replayed the probe after the query hint and judge policy:
  - Questions: `8`.
  - Exact / partial / miss: `7 / 0 / 1`.
  - Runtime load errors: `0`.
  - Write proposals: `0`.
  - Helper rows: `0`.
- The repaired rows used already-admitted facts such as:
  - `has_influence_on(Subject, Complement)`;
  - `has_knowledge_of(Subject, Complement)`;
  - `has_experience_with(Subject, Complement)`.
- The one remaining miss is not the same query-surface class. It is a
  compile-surface omission: the source says an actor joined a target group
  after a prior event, but the compile preserved the prior event as the join
  target and did not preserve the target group as a queryable coordinate.

Artifacts:

- Probe:
  `experiments\boundary_probes\dataset_transfer_stage2\adjacent_relation_query_surface_ladder`
- Initial QA:
  `tmp\boundary_probe_qa_adjacent_relation_query_surface_20260513`
- Prompt-only replay:
  `tmp\boundary_probe_qa_adjacent_relation_query_surface_repair_20260513`
- Query-hint replay:
  `tmp\boundary_probe_qa_adjacent_relation_query_surface_hint_repair_20260513`
- Final relation-judge replay:
  `tmp\boundary_probe_qa_adjacent_relation_query_surface_relation_judge_20260513`

Verification:

- `python -m pytest tests\test_domain_bootstrap_qa.py::test_post_ingestion_qa_strategy_prefers_compiled_kb_surface tests\test_domain_bootstrap_qa.py::test_complementary_relation_hints_query_sibling_subject_surfaces tests\test_domain_bootstrap_qa.py::test_reference_judge_policy_treats_normalized_purpose_atoms_as_answer_bearing -q`
- `python scripts\run_domain_bootstrap_qa_batch.py --dataset-root experiments\boundary_probes\dataset_transfer_stage2 --fixture adjacent_relation_query_surface_ladder --compile-root tmp\boundary_probe_compile_adjacent_relation_query_surface_20260513 --out-root tmp\boundary_probe_qa_adjacent_relation_query_surface_relation_judge_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 420 --no-cache`

Lesson:

- Complementary phrasing is a real query-surface boundary: the answer may live
  on a sibling predicate, while the named baseline relation is only context.
- The repair is fixture-free because it uses only the question's structural
  complement marker, the planner's grounded subject, and the compiled predicate
  inventory. No dataset vocabulary or answer string enters the architecture.
- Predicate names are part of the answer surface. A row such as
  `has_knowledge_of(Entity, Value)` can support "knowledge of Value" even if
  the value atom does not repeat the relation words.

Next pressure:

- Audit the remaining join-target compile omission as a separate coordinate:
  source phrasing that binds a target group and a prior event in the same verb
  phrase must preserve the target relation and the temporal qualifier
  separately.
- Before repair, build a tiny unlike probe for target-versus-anchor joins:
  joined/assigned/appointed/attached to target after/before anchor.

### DT-033 - Target-Anchor Relation Probe

Date: 2026-05-13

Before:

- DT-032 left one compile-surface miss: source phrasing bound a relation target
  and a temporal anchor in the same clause, but the compile preserved the anchor
  as if it were the target.
- The open question was whether target-versus-anchor separation was a missing
  axis or only a denser boundary variant.

Prediction:

- If the axis is missing, a clean unlike probe should fail on target questions:
  joined/appointed/attached/enrolled/moved-to targets would collapse into
  after/before/following/during anchors.
- If the simple axis is inside, target and anchor questions should both answer
  exactly, and the wide-corpus miss should be treated as a density case.

Intervention:

- Added `target_anchor_relation_ladder`, a focused unlike probe that pairs each
  target question with its temporal/causal anchor question.
- Ran OpenRouter compile and QA at `6` lanes with source-record ledger facts
  enabled.

After:

- Target-anchor probe:
  - Questions: `10`.
  - Exact / partial / miss: `10 / 0 / 0`.
  - Runtime load errors: `0`.
  - Write proposals: `0`.
  - Helper rows: `0`.
- The compile did preserve target and anchor separately in the simple case.

Artifacts:

- Probe:
  `experiments\boundary_probes\dataset_transfer_stage2\target_anchor_relation_ladder`
- Compile:
  `tmp\boundary_probe_compile_target_anchor_relation_20260513`
- QA:
  `tmp\boundary_probe_qa_target_anchor_relation_20260513`

Verification:

- `python scripts\run_domain_bootstrap_file_batch.py --dataset-root experiments\boundary_probes\dataset_transfer_stage2 --fixture target_anchor_relation_ladder --out-root tmp\boundary_probe_compile_target_anchor_relation_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 900 --compile-source --compile-flat-plus-plan-passes --focused-pass-ops-schema --source-record-ledger --source-record-ledger-facts`
- `python scripts\run_domain_bootstrap_qa_batch.py --dataset-root experiments\boundary_probes\dataset_transfer_stage2 --fixture target_anchor_relation_ladder --compile-root tmp\boundary_probe_compile_target_anchor_relation_20260513 --out-root tmp\boundary_probe_qa_target_anchor_relation_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 420 --no-cache`

Lesson:

- Target-versus-anchor separation is not absent. The clean coordinate is
  interior.
- The remaining wide-corpus miss is likely a resolution-density problem:
  denser syntax, multiple candidate targets, ambiguous attachment, or a
  relation label that the compile over-normalizes.
- Do not add a repair from this probe. The evidence says to probe density
  variants before changing compile guidance.

Next pressure:

- Build a denser target-anchor probe with multiple possible targets and anchors:
  nested clauses, pronoun/role aliases, target lists, and target-vs-event
  ambiguity. The repair, if any, must still preserve target relation and anchor
  relation as separate coordinates without naming corpus vocabulary.

### DT-034 - Dense Target-Anchor Repair

Date: 2026-05-13

Before:

- DT-033 showed that the clean target-anchor coordinate was interior.
- The remaining question was density: contrastive targets, prior and later
  anchors, object attachment near actor assignment, and action-event anchor
  labels in the same source region.

Prediction:

- If the clean pass was hiding density blur, a denser unlike probe should expose
  several distinct failures rather than one missing axis.
- Useful repairs should preserve source-fidelity surfaces without teaching the
  harness any probe vocabulary.

Intervention:

- Added `target_anchor_density_ladder`, a focused density probe.
- Initial compile/QA result:
  - Questions: `12`.
  - Exact / partial / miss: `8 / 1 / 3`.
  - Helper rows: `0`.
- Classified four non-exact rows:
  - exact anchor modifier collapse: a shorter anchor atom lost a source-stated
    modifier needed by a later query;
  - object-vs-actor attachment collapse: an object attached to a place was
    crowded out by the actor's assignment to a unit;
  - anchor-to-later-event join gap: later-event question needed the exact
    anchor label to join to ordering rows;
  - trigger/anchor query gap: QA asked for temporal-before when the direct
    trigger/anchor row already carried the answer.
- Added generic compile guidance for target-anchor preservation and
  object-vs-actor attachment separation.
- Added generic QA guidance and a deterministic hint for direct
  anchor/trigger predicates such as `event_anchor(Anchor, ActionEvent)` and
  `triggered_by(ActionEvent, Anchor)`.

After:

- Recompiled the density probe after compile guidance:
  - QA result: `11 / 0 / 1`.
  - The modifier and object/actor attachment gaps moved inside.
- Replayed QA after anchor/trigger query hints:
  - QA result: `12 / 0 / 0`.
  - Runtime load errors: `0`.
  - Write proposals: `0`.
  - Helper rows: `0`.

Artifacts:

- Probe:
  `experiments\boundary_probes\dataset_transfer_stage2\target_anchor_density_ladder`
- Initial compile:
  `tmp\boundary_probe_compile_target_anchor_density_20260513`
- Initial QA:
  `tmp\boundary_probe_qa_target_anchor_density_20260513`
- Repaired compile:
  `tmp\boundary_probe_compile_target_anchor_density_repair_20260513`
- Compile-repair QA:
  `tmp\boundary_probe_qa_target_anchor_density_repair_20260513`
- Final anchor-query QA:
  `tmp\boundary_probe_qa_target_anchor_density_anchor_repair_20260513`

Verification:

- `python -m pytest tests\test_domain_bootstrap_file.py::test_source_pass_ops_guidance_preserves_explicit_negative_surfaces tests\test_domain_bootstrap_qa.py::test_anchor_relation_hints_query_direct_trigger_surfaces tests\test_domain_bootstrap_qa.py::test_reference_judge_policy_treats_normalized_purpose_atoms_as_answer_bearing -q`
- `python scripts\run_domain_bootstrap_file_batch.py --dataset-root experiments\boundary_probes\dataset_transfer_stage2 --fixture target_anchor_density_ladder --out-root tmp\boundary_probe_compile_target_anchor_density_repair_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 900 --compile-source --compile-flat-plus-plan-passes --focused-pass-ops-schema --source-record-ledger --source-record-ledger-facts`
- `python scripts\run_domain_bootstrap_qa_batch.py --dataset-root experiments\boundary_probes\dataset_transfer_stage2 --fixture target_anchor_density_ladder --compile-root tmp\boundary_probe_compile_target_anchor_density_repair_20260513 --out-root tmp\boundary_probe_qa_target_anchor_density_anchor_repair_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 420 --no-cache`

Lesson:

- Target-anchor was not a missing axis; it was a resolution-density boundary.
  The live set extended when compile preserved exact anchor labels and kept
  object attachment separate from actor assignment.
- Trigger/anchor rows are answer surfaces, not mere provenance. When a question
  asks what came before or anchored an action, the direct anchor row can answer
  before any broader temporal ordering query is needed.
- The repair stayed clean: no probe nouns, no answer strings, no helper rows,
  and no dataset-specific predicates.

Next pressure:

- Replay the SQuAD-30 residue rows that motivated this coordinate before a full
  corpus rerun. The expected movement is narrow: target-anchor or
  complementary-query rows should improve, while unrelated direct compile gaps
  remain measurement coordinates.

### DT-035 - SQuAD Complementary-Query Replay

Date: 2026-05-13

Before:

- DT-031's full SQuAD-30 run had two duplicate non-exact rows asking what a
  returning group had "in addition to" a named baseline attribute.
- DT-032 repaired the unlike complementary-query probe, but replay on the
  motivating SQuAD coordinate was still needed before claiming transfer.

Prediction:

- The targeted SQuAD fixture should move without helpers if the repair is
  genuinely about complementary query shape rather than the probe packet.
- A clean result should not imply the whole SQuAD residue is solved; unrelated
  direct compile gaps remain separate coordinates.

Intervention:

- Recompiled only the motivating SQuAD fixture with current compile guidance.
- Ran QA through OpenRouter at `6` lanes with no cache.

After:

- Targeted SQuAD replay:
  - Fixture: `squad_default_validation_00026_islamism`.
  - Questions: `6`.
  - Exact / partial / miss: `6 / 0 / 0`.
  - Runtime load errors: `0`.
  - Write proposals: `0`.
  - Helper rows: `0`.
- The duplicate complementary-query residue moved inside on replay.

Artifacts:

- Compile:
  `tmp\mrc_transfer_compile_squad30_dt034_islamism_replay_20260513`
- QA:
  `tmp\mrc_transfer_qa_squad30_dt034_islamism_replay_20260513`

Verification:

- `python scripts\run_domain_bootstrap_file_batch.py --dataset-root tmp\mrc_transfer_staged_squad30_20260513 --fixture squad_default_validation_00026_islamism --out-root tmp\mrc_transfer_compile_squad30_dt034_islamism_replay_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 900 --compile-source --compile-flat-plus-plan-passes --focused-pass-ops-schema --source-record-ledger --source-record-ledger-facts`
- `python scripts\run_domain_bootstrap_qa_batch.py --dataset-root tmp\mrc_transfer_staged_squad30_20260513 --fixture squad_default_validation_00026_islamism --compile-root tmp\mrc_transfer_compile_squad30_dt034_islamism_replay_20260513 --out-root tmp\mrc_transfer_qa_squad30_dt034_islamism_replay_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 420 --no-cache`

Lesson:

- The complementary-query repair transferred back to the motivating SQuAD
  coordinate. The unlike probe was not an isolated toy success.
- The result is narrow evidence, not permission to overclaim: the remaining
  SQuAD residue still includes direct compile gaps and a temporal-distance
  hybrid join that need their own probes.

Next pressure:

- Mine the remaining stable SQuAD residues by coordinate. The most valuable
  next probe is the temporal-distance hybrid row: a source prints a relative
  distance ("three years before") but compile/query surfaces preserve only
  publication year and before relation, not the numeric distance or comparable
  endpoint.

### DT-036 - Printed Temporal-Distance Surface

Date: 2026-05-13

Before:

- DT-035 identified the next stable SQuAD residue: a source printed a relative
  distance, but the compiled profile exposed only publication year plus a
  boolean before-death relation.
- The question was whether printed temporal distance was a missing axis or only
  a dense-profile capability gap.

Prediction:

- A clean unlike probe should be inside if the architecture already knows how
  to represent printed distances when the profile proposes an appropriate
  predicate.
- The motivating SQuAD row should remain outside until profile bootstrap is
  told not to collapse printed intervals into boolean before/after predicates.

Intervention:

- Added `printed_relative_distance_ladder`, a focused unlike probe for printed
  distances such as years before, months after, and days after.
- Initial probe result:
  - Questions: `10`.
  - Exact / partial / miss: `10 / 0 / 0`.
  - Helper rows: `0`.
- Replayed the motivating SQuAD fixture before profile repair:
  - Fixture: `squad_default_validation_00006_martin_luther`.
  - Exact / partial / miss: `4 / 0 / 1`.
  - The miss had `published_before_death/2` but no distance/proximity slot.
- Added profile-bootstrap and profile-review guidance: printed relative
  intervals are first-class query surfaces and should get a duration/proximity
  predicate rather than only a boolean before/after predicate.

After:

- Replayed the motivating SQuAD fixture after profile guidance:
  - Questions: `5`.
  - Exact / partial / miss: `5 / 0 / 0`.
  - Runtime load errors: `0`.
  - Write proposals: `0`.
  - Helper rows: `0`.

Artifacts:

- Probe:
  `experiments\boundary_probes\dataset_transfer_stage2\printed_relative_distance_ladder`
- Probe compile:
  `tmp\boundary_probe_compile_printed_relative_distance_20260513`
- Probe QA:
  `tmp\boundary_probe_qa_printed_relative_distance_20260513`
- SQuAD replay before profile repair:
  `tmp\mrc_transfer_qa_squad30_dt036_luther_replay_20260513`
- SQuAD replay after profile repair:
  `tmp\mrc_transfer_qa_squad30_dt036_luther_profile_repair_20260513`

Verification:

- `python -m pytest tests\test_profile_bootstrap.py::ProfileBootstrapTests::test_bootstrap_guidance_preserves_source_records_reporters_and_conditions -q`
- `python scripts\run_domain_bootstrap_file_batch.py --dataset-root experiments\boundary_probes\dataset_transfer_stage2 --fixture printed_relative_distance_ladder --out-root tmp\boundary_probe_compile_printed_relative_distance_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 900 --compile-source --compile-flat-plus-plan-passes --focused-pass-ops-schema --source-record-ledger --source-record-ledger-facts`
- `python scripts\run_domain_bootstrap_qa_batch.py --dataset-root experiments\boundary_probes\dataset_transfer_stage2 --fixture printed_relative_distance_ladder --compile-root tmp\boundary_probe_compile_printed_relative_distance_20260513 --out-root tmp\boundary_probe_qa_printed_relative_distance_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 420 --no-cache`
- `python scripts\run_domain_bootstrap_file_batch.py --dataset-root tmp\mrc_transfer_staged_squad30_20260513 --fixture squad_default_validation_00006_martin_luther --out-root tmp\mrc_transfer_compile_squad30_dt036_luther_profile_repair_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 900 --compile-source --compile-flat-plus-plan-passes --focused-pass-ops-schema --source-record-ledger --source-record-ledger-facts`
- `python scripts\run_domain_bootstrap_qa_batch.py --dataset-root tmp\mrc_transfer_staged_squad30_20260513 --fixture squad_default_validation_00006_martin_luther --compile-root tmp\mrc_transfer_compile_squad30_dt036_luther_profile_repair_20260513 --out-root tmp\mrc_transfer_qa_squad30_dt036_luther_profile_repair_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 420 --no-cache`

Lesson:

- Printed relative distance is not a missing runtime helper problem when the
  source explicitly states the distance. The architecture needs a profile slot
  that preserves the printed distance.
- Boolean temporal predicates such as `published_before_death/2` are too thin
  when the source says how near or how long before/after. Endpoint dates,
  ordering, and printed distance are separate query surfaces.
- The repair transferred back to the motivating SQuAD coordinate with no helper
  rows and no fixture vocabulary.

Next pressure:

- The remaining stable SQuAD residues are now mostly direct compile-surface
  gaps and query-surface resolution around named entities or title/display
  surfaces. Audit those before a full SQuAD-30 rerun.

### DT-037 - Full SQuAD-30 Transfer Remeasurement

Date: 2026-05-13

Before:

- DT-032 through DT-036 repaired targeted transfer coordinates with unlike
  probes and narrow motivating replays.
- The last comparable full SQuAD-30 run was still the DT-031-era measurement:
  `152 / 2 / 17` exact / partial / miss across `171` questions, or `88.89%`
  exact.
- A full rerun was needed because targeted replays can hide broad compile
  variance and can overstate transfer if they only move the motivating row.

Prediction:

- The full run should improve if the recent repairs are actually transferable:
  complementary relation questions, target-anchor questions, and printed
  temporal-distance questions should no longer dominate the residue.
- Remaining not-exact rows should mostly be direct compile-surface gaps, not
  fixture-shaped query-plan or helper-delivery failures.
- Any new repair should wait until the residue is audited as a coordinate
  family; the full run is measurement, not permission for patching.

Intervention:

- Recompiled all `30` staged SQuAD fixtures through OpenRouter at `6` lanes
  with source-record ledger facts enabled.
- Ran QA across the same `30` fixtures through OpenRouter at `6` lanes with
  cache disabled.
- Summarized the result with the transfer-coordinate intake audit.

After:

- Full SQuAD-30 rerun:
  - Questions: `171`.
  - Exact / partial / miss / not judged: `160 / 4 / 7 / 0`.
  - Exact rate: `93.57%`.
  - Non-exact rows: `11`.
  - Runtime load errors: `0`.
  - Write proposals: `0`.
  - Helper rows: `0`.
- Movement from previous full run:
  - Exact: `152 -> 160` (`+8`).
  - Non-exact: `19 -> 11` (`-8`).
  - Exact rate: `88.89% -> 93.57%`.
- Current residue by coordinate:
  - `direct_compile_surface_gap`: `9`.
  - `hybrid_join_resolution`: `1`.
  - `implicit_attitude_or_consequence`: `1`.
- Current residue by failure surface:
  - `compile_surface_gap`: `10`.
  - `hybrid_join_gap`: `1`.

Artifacts:

- Compile:
  `tmp\mrc_transfer_compile_squad30_dt036_full_20260513`
- QA:
  `tmp\mrc_transfer_qa_squad30_dt036_full_20260513`
- Coordinate summary:
  `tmp\mrc_transfer_qa_squad30_dt036_full_20260513\transfer_coordinate_summary_with_intake.md`

Verification:

- `python scripts\run_domain_bootstrap_file_batch.py --dataset-root tmp\mrc_transfer_staged_squad30_20260513 --out-root tmp\mrc_transfer_compile_squad30_dt036_full_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 900 --compile-source --compile-flat-plus-plan-passes --focused-pass-ops-schema --source-record-ledger --source-record-ledger-facts`
- `python scripts\run_domain_bootstrap_qa_batch.py --dataset-root tmp\mrc_transfer_staged_squad30_20260513 --compile-root tmp\mrc_transfer_compile_squad30_dt036_full_20260513 --out-root tmp\mrc_transfer_qa_squad30_dt036_full_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 420 --no-cache`
- `python scripts\summarize_mrc_transfer_qa.py --qa-root tmp\mrc_transfer_qa_squad30_dt036_full_20260513 --intake-audit tmp\mrc_transfer_samples_squad30_20260513\transfer_intake_audit.json --out-json tmp\mrc_transfer_qa_squad30_dt036_full_20260513\transfer_coordinate_summary_with_intake.json --out-md tmp\mrc_transfer_qa_squad30_dt036_full_20260513\transfer_coordinate_summary_with_intake.md`

Lesson:

- The recent targeted repairs transferred under full rerun pressure. The score
  moved materially without helper rows, write proposals, or transport errors.
- SQuAD is no longer primarily exposing the query-surface failures that started
  this dataset-transfer loop. The remaining boundary is mostly compile
  resolution: preserving direct answer-bearing distinctions, descriptors,
  category terms, and small causal joins as queryable surfaces.
- The residue is now small enough to audit manually before the next repair.
  Repairing from a single row would risk turning dataset vocabulary into
  architecture; repairing from a recurring coordinate family is the correct
  next move.

Next pressure:

- Manually stratify the `11` remaining non-exact rows. The first useful split
  is likely descriptor preservation, category/generalization preservation,
  fraction/remaining-share arithmetic, causal-chain join, and external-code
  inference. Only build a probe for a family that recurs or represents a
  transferable missing resolution shape.

### DT-038 - SQuAD Residue Stratification

Date: 2026-05-13

Before:

- DT-037 reduced the full SQuAD-30 residue to `11` non-exact rows.
- The coordinate summary labelled `9` rows as `direct_compile_surface_gap`, but
  that class was too broad to choose the next repair responsibly.

Prediction:

- If the remaining rows are mostly unrelated singletons, the correct move is
  more measurement rather than repair.
- If several rows share the same fixture-free resolution shape, the next probe
  should target that shape with unlike source prose and no dataset vocabulary.

Intervention:

- Manually stratified the `11` non-exact rows by the proposition surface the
  source needed to preserve, ignoring fixture names and question ids.

After:

- Residue classes:
  - Answer-bearing complement preservation: `4`.
    Source states a relation or definition with a compact answer complement,
    but compile preserves adjacent facts while dropping the exact complement.
    This includes descriptive complements, purpose/use complements, temporal
    start labels, and reactive-target complements.
  - Generic name, category, or component-list preservation: `3`.
    Source states a general name, class, or component set, but compile keeps a
    narrower instance, adjacent plan, or overly specific member.
  - External code/world mapping: `1`.
    The answer requires a conventional mapping not printed as an answer surface.
  - Scope or authority envelope: `1`.
    The answer depends on keeping a target/scope envelope distinct from nearby
    exception or justification prose.
  - Remaining-share arithmetic: `1`.
    The answer depends on complement-of-fraction or residual-share reasoning.
  - Causal-chain join: `1`.
    The answer depends on chaining cause/lead-to with an ended-state predicate.

Artifacts:

- Coordinate summary:
  `tmp\mrc_transfer_qa_squad30_dt036_full_20260513\transfer_coordinate_summary_with_intake.md`

Verification:

- `python - <<'PY' ...` manual stratification helper over
  `tmp\mrc_transfer_qa_squad30_dt036_full_20260513\transfer_coordinate_summary_with_intake.json`

Lesson:

- The next useful probe is not about a dataset format. It is about whether
  compile treats answer-bearing complements as first-class query surfaces.
- A complement may be an attribute, purpose, temporal label, reaction target,
  definition, component list, or category. The repair target must be the
  generic preservation rule, not any one subject area.
- The singleton rows should stay on the board. They are valuable coordinates,
  but they do not yet earn architecture.

Next pressure:

- Build a focused unlike probe for answer-bearing complement preservation. It
  should contain printed complements but no printed final-answer shortcuts:
  descriptive definition, use/purpose, temporal start label, reaction/affinity
  target, and component-list membership. Run it before changing compile logic.

### DT-039 - Answer-Bearing Complement Probe

Date: 2026-05-13

Before:

- DT-038 identified answer-bearing complement preservation as the largest
  recurring SQuAD residue family.
- The unknown was whether this was a missing axis or a density boundary: could
  compile preserve simple descriptive, purpose, temporal, relation-target,
  component-list, name, and category complements when the source stated them
  plainly?

Prediction:

- If the probe misses, a generic compile-surface repair is justified.
- If the probe is exact with no helpers, then the axis is interior and the
  SQuAD failures are denser variants rather than missing architecture.

Intervention:

- Added `answer_bearing_complement_ladder`, an unlike probe with eight compact
  complement questions and no SQuAD topics.
- Compiled and ran QA through OpenRouter at `6` lanes.

After:

- Probe result:
  - Questions: `8`.
  - Exact / partial / miss: `8 / 0 / 0`.
  - Runtime load errors: `0`.
  - Write proposals: `0`.
  - Helper rows: `0`.

Artifacts:

- Probe:
  `experiments\boundary_probes\dataset_transfer_stage2\answer_bearing_complement_ladder`
- Compile:
  `tmp\boundary_probe_compile_answer_bearing_complement_20260513`
- QA:
  `tmp\boundary_probe_qa_answer_bearing_complement_20260513`

Verification:

- `python scripts\run_domain_bootstrap_file_batch.py --dataset-root experiments\boundary_probes\dataset_transfer_stage2 --fixture answer_bearing_complement_ladder --out-root tmp\boundary_probe_compile_answer_bearing_complement_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 900 --compile-source --compile-flat-plus-plan-passes --focused-pass-ops-schema --source-record-ledger --source-record-ledger-facts`
- `python scripts\run_domain_bootstrap_qa_batch.py --dataset-root experiments\boundary_probes\dataset_transfer_stage2 --fixture answer_bearing_complement_ladder --compile-root tmp\boundary_probe_compile_answer_bearing_complement_20260513 --out-root tmp\boundary_probe_qa_answer_bearing_complement_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 420 --no-cache`

Lesson:

- Answer-bearing complements are not a missing axis in the simple case. The
  architecture can preserve and query descriptive, purpose, temporal,
  relation-target, list, name, and category complements without helper rows.
- The SQuAD residue is therefore a density question: adjacent facts,
  paraphrase, generic-vs-specific naming, and competing envelopes can still
  blur the complement surface.
- No compile repair is warranted from the simple probe. The next probe needs
  density, not a bigger generic instruction.

Next pressure:

- Build a dense complement probe with nearby distractor complements, generic
  and specific category variants, competing purpose clauses, and adjacent
  relation targets. If that probe fails, repair the density rule; if it passes,
  move to the next SQuAD residue family.

### DT-040 - Dense Complement Probe

Date: 2026-05-13

Before:

- DT-039 proved simple answer-bearing complements were inside the set.
- The remaining possibility was that density, not the axis itself, caused the
  SQuAD residue: nearby distractor complements, separate names, category
  variants, adjacent purposes, and exception clauses could blur the answer
  surface.

Prediction:

- A failure would justify a generic density repair for complement preservation.
- A clean result would retire this as the next repair target for now and push
  attention to other residue families.

Intervention:

- Added `dense_answer_bearing_complement_ladder`, an unlike probe with ten
  complement questions and nearby distractor facts.
- Compiled and ran QA through OpenRouter at `6` lanes.

After:

- Probe result:
  - Questions: `10`.
  - Exact / partial / miss: `10 / 0 / 0`.
  - Runtime load errors: `0`.
  - Write proposals: `0`.
  - Helper rows: `0`.
- Compile result:
  - Parsed OK.
  - Admitted clauses: `61`.
  - Skipped clauses: `5`.

Artifacts:

- Probe:
  `experiments\boundary_probes\dataset_transfer_stage2\dense_answer_bearing_complement_ladder`
- Compile:
  `tmp\boundary_probe_compile_dense_answer_bearing_complement_20260513`
- QA:
  `tmp\boundary_probe_qa_dense_answer_bearing_complement_20260513`

Verification:

- `python scripts\run_domain_bootstrap_file_batch.py --dataset-root experiments\boundary_probes\dataset_transfer_stage2 --fixture dense_answer_bearing_complement_ladder --out-root tmp\boundary_probe_compile_dense_answer_bearing_complement_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 900 --compile-source --compile-flat-plus-plan-passes --focused-pass-ops-schema --source-record-ledger --source-record-ledger-facts`
- `python scripts\run_domain_bootstrap_qa_batch.py --dataset-root experiments\boundary_probes\dataset_transfer_stage2 --fixture dense_answer_bearing_complement_ladder --compile-root tmp\boundary_probe_compile_dense_answer_bearing_complement_20260513 --out-root tmp\boundary_probe_qa_dense_answer_bearing_complement_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 420 --no-cache`

Lesson:

- Complement preservation is interior under both simple and moderate-density
  unlike probes. A generic repair here would be premature.
- The SQuAD rows that looked like complement-preservation failures are more
  likely narrower lexical/source-detail gaps: broad category recovery,
  paraphrased descriptor extraction, or source wording that was not represented
  with enough precision.
- The boundary-hunt discipline prevented overfitting: a tempting repair target
  failed to reproduce under unlike probes, so it stays on the board as
  measurement, not architecture.

Next pressure:

- Move to the next transferable residue family with higher machinery value:
  remaining-share arithmetic. Build a focused probe for complement-of-fraction
  and residual-share questions before changing any arithmetic or compile
  guidance.

### DT-041 - Remaining-Share Arithmetic Repair

Date: 2026-05-13

Before:

- DT-040 left remaining-share arithmetic as the next high-value residue family.
- The SQuAD motivating row was only one row, so it did not justify a repair by
  itself. A focused unlike probe was needed first.

Prediction:

- Recipient and printed-fraction residual questions should already be inside
  if compile preserves `receives_remainder` and explicit shares.
- Residual absolute amount questions may fail if the system retrieves total and
  allocated amount but does not derive `total - allocated` as a support row.

Intervention:

- Added `remaining_share_arithmetic_ladder`, a focused unlike probe for:
  - residual recipient lookup,
  - printed complementary fractions,
  - residual absolute amount from total minus allocated amount,
  - distractor exclusions outside the split.
- Initial probe result:
  - Questions: `7`.
  - Exact / partial / miss: `5 / 0 / 2`.
  - Failure surface: `hybrid_join_gap` for `2`.
  - Helper rows: `0`.
- The two misses both had all needed admitted rows:
  - total amount,
  - absolute allocated amount,
  - remainder recipient.
  The missing operation was exposing the residual amount as query support.
- Added `residual_absolute_amount_support`, a query-only clean helper that
  subtracts admitted absolute allocations from an admitted scenario total for
  an admitted remainder recipient.
- Tightened delivery after the first repair replay exposed helper volume:
  duplicate `recipient_*` rows are normalized before summing, and support rows
  are scoped to the scenario or remainder recipient present in the query.

After:

- Final scoped probe replay:
  - Questions: `7`.
  - Exact / partial / miss: `7 / 0 / 0`.
  - Runtime load errors: `0`.
  - Write proposals: `0`.
  - Helper rows: `3`.
  - Helper class: `clean-helper`.
- Broad QA tests:
  - `149 passed`.

Artifacts:

- Probe:
  `experiments\boundary_probes\dataset_transfer_stage2\remaining_share_arithmetic_ladder`
- Initial compile:
  `tmp\boundary_probe_compile_remaining_share_arithmetic_20260513`
- Initial QA:
  `tmp\boundary_probe_qa_remaining_share_arithmetic_20260513`
- Final QA:
  `tmp\boundary_probe_qa_remaining_share_arithmetic_residual_scoped_20260513`

Verification:

- `python scripts\run_domain_bootstrap_file_batch.py --dataset-root experiments\boundary_probes\dataset_transfer_stage2 --fixture remaining_share_arithmetic_ladder --out-root tmp\boundary_probe_compile_remaining_share_arithmetic_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 900 --compile-source --compile-flat-plus-plan-passes --focused-pass-ops-schema --source-record-ledger --source-record-ledger-facts`
- `python scripts\run_domain_bootstrap_qa_batch.py --dataset-root experiments\boundary_probes\dataset_transfer_stage2 --fixture remaining_share_arithmetic_ladder --compile-root tmp\boundary_probe_compile_remaining_share_arithmetic_20260513 --out-root tmp\boundary_probe_qa_remaining_share_arithmetic_residual_scoped_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 420 --no-cache`
- `python -m pytest tests\test_domain_bootstrap_qa.py -q`

Lesson:

- Remaining-share arithmetic splits into two different surfaces:
  recipient/fraction residuals can be answered from direct admitted rows, while
  absolute residual amounts need a derived support row.
- The helper is generic and source-faithful: it only derives from admitted
  totals, admitted absolute allocations, and admitted remainder recipients. It
  does not write durable facts and does not infer a remainder recipient.
- Helper delivery needs the same pressure discipline as compile surfaces. The
  first working version returned too many rows because duplicate `recipient_*`
  aliases inflated both arithmetic and delivery. Normalizing those aliases and
  scoping to query-bound scenario/recipient kept the repair small.

Next pressure:

- Replay the SQuAD Rhine residue to see whether this repair helps the
  motivating row. If it does not, keep the SQuAD row classified separately as
  fraction-channel/source-detail pressure rather than broad residual arithmetic.

### DT-042 - Rhine Residual Replay

Date: 2026-05-13

Before:

- DT-041 repaired absolute residual-share arithmetic on an unlike probe.
- The motivating SQuAD row asked for the channel corresponding to the other
  third of a river flow, which might or might not share the new helper's
  absolute-residual machinery.

Prediction:

- If the SQuAD row needed the new helper, replay should move with
  `residual_absolute_amount_support` or related helper evidence.
- If it moved without helpers, the row should be reclassified as a query/judge
  resolution replay rather than evidence for the new absolute-residual helper.

Intervention:

- Replayed the SQuAD Rhine fixture with current QA code against the existing
  DT-037 full SQuAD compile.

After:

- Targeted replay:
  - Fixture: `squad_default_validation_00025_rhine`.
  - Questions: `9`.
  - Exact / partial / miss: `9 / 0 / 0`.
  - Runtime load errors: `0`.
  - Write proposals: `0`.
  - Helper rows: `0`.
- The former non-exact row moved inside. The query result contained the answer
  channel directly via flow-through evidence and contextual fraction evidence.

Artifacts:

- QA:
  `tmp\mrc_transfer_qa_squad30_dt041_rhine_residual_replay_20260513`

Verification:

- `python scripts\run_domain_bootstrap_qa_batch.py --dataset-root tmp\mrc_transfer_staged_squad30_20260513 --fixture squad_default_validation_00025_rhine --compile-root tmp\mrc_transfer_compile_squad30_dt036_full_20260513 --out-root tmp\mrc_transfer_qa_squad30_dt041_rhine_residual_replay_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 420 --no-cache`

Lesson:

- The unlike residual-share repair is still valid, but the SQuAD Rhine row is
  not evidence that the helper transferred. It moved without helper rows.
- The useful claim is narrower and cleaner: absolute residual amount is now
  covered by a generic helper; fraction-channel recipient questions can already
  resolve through direct flow/fraction evidence when the query plan retrieves
  the right rows.
- This is another case where replay prevents over-attribution. A row can move
  inside after nearby work without being caused by that work.

Next pressure:

- Commit this slice, then choose between two remaining high-value residue
  families: causal-chain join and generic/category surface preservation. The
  causal-chain join is smaller but more machinery-like; category preservation
  has more rows but may be lexical/source-detail noise.

### DT-043 - Causal End-State Chain Repair

Date: 2026-05-13

Before:

- DT-042 left the SQuAD imperialism residue as the next machinery-like
  boundary: an upstream event led to an ending event, and the ending event ended
  a target state.
- The risk was overgeneralizing causality. Direct end-state questions should
  answer the immediate ending event; upstream-cause questions should answer the
  cause that produced the ending event.

Prediction:

- A focused unlike probe should mostly pass if direct and upstream-cause rows
  are queried correctly.
- Any failure should distinguish query delivery from judge policy. A judge-only
  policy cannot help if the upstream causal row is absent from query results.

Intervention:

- Added `causal_chain_end_state_ladder`, an unlike probe with direct ending,
  upstream cause, trigger, lead-to, and explicit non-cause questions.
- Initial probe result:
  - Questions: `10`.
  - Exact / partial / miss: `9 / 1 / 0`.
  - Failure surface: `hybrid_join_gap`.
  - Helper rows: `0`.
- The partial row had `ended(EndingEvent, State)` and a valid upstream
  `led_to(Cause, EndingEvent)` chain, but the chain was not consistently
  delivered to the judge.
- Added:
  - query-planning guidance for cause-of-ending questions,
  - judge policy for causal end-state chains,
  - `causal_end_state_support`, a query-only clean helper that joins admitted
    upstream causal rows to admitted end-state rows.
- Initial SQuAD replay exposed a generic morphology gap: the corpus used
  `leads_to/2` while the helper recognized `led_to/2`. Added `leads_to/2`
  support.

After:

- Final unlike probe replay:
  - Questions: `10`.
  - Exact / partial / miss: `10 / 0 / 0`.
  - Runtime load errors: `0`.
  - Write proposals: `0`.
  - Helper rows: `10`.
  - Helper class: `clean-helper`.
- SQuAD imperialism replay:
  - Fixture: `squad_default_validation_00027_imperialism`.
  - Questions: `4`.
  - Exact / partial / miss: `4 / 0 / 0`.
  - Helper rows: `1`.
  - Helper class: `clean-helper`.
- Broad QA tests:
  - `150 passed`.

Artifacts:

- Probe:
  `experiments\boundary_probes\dataset_transfer_stage2\causal_chain_end_state_ladder`
- Probe compile:
  `tmp\boundary_probe_compile_causal_chain_end_state_20260513`
- Final probe QA:
  `tmp\boundary_probe_qa_causal_chain_end_state_companion_repair_20260513`
- SQuAD replay:
  `tmp\mrc_transfer_qa_squad30_dt043_imperialism_causal_replay2_20260513`

Verification:

- `python scripts\run_domain_bootstrap_file_batch.py --dataset-root experiments\boundary_probes\dataset_transfer_stage2 --fixture causal_chain_end_state_ladder --out-root tmp\boundary_probe_compile_causal_chain_end_state_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 900 --compile-source --compile-flat-plus-plan-passes --focused-pass-ops-schema --source-record-ledger --source-record-ledger-facts`
- `python scripts\run_domain_bootstrap_qa_batch.py --dataset-root experiments\boundary_probes\dataset_transfer_stage2 --fixture causal_chain_end_state_ladder --compile-root tmp\boundary_probe_compile_causal_chain_end_state_20260513 --out-root tmp\boundary_probe_qa_causal_chain_end_state_companion_repair_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 420 --no-cache`
- `python scripts\run_domain_bootstrap_qa_batch.py --dataset-root tmp\mrc_transfer_staged_squad30_20260513 --fixture squad_default_validation_00027_imperialism --compile-root tmp\mrc_transfer_compile_squad30_dt036_full_20260513 --out-root tmp\mrc_transfer_qa_squad30_dt043_imperialism_causal_replay2_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 420 --no-cache`
- `python -m pytest tests\test_domain_bootstrap_qa.py -q`

Lesson:

- Causal end-state questions require preserving two answer surfaces: the direct
  ending event and the upstream cause of that ending event. Which one answers
  depends on the question wording.
- The repair is query-only and source-faithful. It does not invent causal
  chains; it only joins admitted `led_to`/`leads_to`, `caused_by`, `triggered`,
  or `triggered_by` rows to admitted end-state rows.
- Morphology matters at the architecture level. Supporting both `led_to` and
  `leads_to` is not fixture vocabulary; it is predicate-family normalization.

Next pressure:

- Remeasure the full SQuAD-30 slice after DT-041 and DT-043. Expected movement
  is small but real: the Rhine and imperialism rows should now be inside, while
  remaining rows should mostly be generic/category or lexical source-detail
  gaps.

### DT-044 - Full SQuAD-30 Post-Repair Remeasurement

Date: 2026-05-13

Before:

- DT-041 and DT-043 each passed focused unlike probes and targeted SQuAD
  replays.
- A full SQuAD-30 rerun was needed to check whether the repairs held under
  broader QA pressure and whether new variance appeared.

Prediction:

- Rhine should remain inside.
- Imperialism should improve if `causal_end_state_support` is accepted by the
  judge under full-run context.
- The overall score should be interpreted cautiously because QA judge variance
  can move isolated rows even with the same compile.

Intervention:

- Reran QA over the existing DT-037 SQuAD-30 compile with current QA code,
  OpenRouter at `6` lanes, and cache disabled.
- Summarized the run with the transfer-coordinate intake audit.

After:

- Full SQuAD-30 rerun:
  - Questions: `171`.
  - Exact / partial / miss / not judged: `156 / 5 / 10 / 0`.
  - Exact rate: `91.23%`.
  - Non-exact rows: `15`.
  - Runtime load errors: `0`.
  - Write proposals: `0`.
- Compared with DT-037 (`160 / 4 / 7`, `93.57%`):
  - Resolved from old residue: `3`.
  - New non-exacts: `7`.
  - Still non-exact: `8`.
- Important row movements:
  - Rhine residual row moved inside in both targeted and full replay.
  - Causal imperialism row moved in one targeted replay, but remained partial
    in the full rerun and in a follow-up targeted replay despite a clean
    `causal_end_state_support` row.
  - Several new non-exacts are judge/query variance or known noisy references,
    including an answer-surface row where the reference appears to repeat the
    question subject instead of the designer.

Artifacts:

- Full QA:
  `tmp\mrc_transfer_qa_squad30_dt043_full_20260513`
- Summary:
  `tmp\mrc_transfer_qa_squad30_dt043_full_20260513\transfer_coordinate_summary_with_intake.md`
- Causal helper-policy targeted replay:
  `tmp\mrc_transfer_qa_squad30_dt043_imperialism_causal_helper_policy_20260513`

Verification:

- `python scripts\run_domain_bootstrap_qa_batch.py --dataset-root tmp\mrc_transfer_staged_squad30_20260513 --compile-root tmp\mrc_transfer_compile_squad30_dt036_full_20260513 --out-root tmp\mrc_transfer_qa_squad30_dt043_full_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 420 --no-cache`
- `python scripts\summarize_mrc_transfer_qa.py --qa-root tmp\mrc_transfer_qa_squad30_dt043_full_20260513 --intake-audit tmp\mrc_transfer_samples_squad30_20260513\transfer_intake_audit.json --out-json tmp\mrc_transfer_qa_squad30_dt043_full_20260513\transfer_coordinate_summary_with_intake.json --out-md tmp\mrc_transfer_qa_squad30_dt043_full_20260513\transfer_coordinate_summary_with_intake.md`
- `python scripts\run_domain_bootstrap_qa_batch.py --dataset-root tmp\mrc_transfer_staged_squad30_20260513 --fixture squad_default_validation_00027_imperialism --compile-root tmp\mrc_transfer_compile_squad30_dt036_full_20260513 --out-root tmp\mrc_transfer_qa_squad30_dt043_imperialism_causal_helper_policy_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 420 --no-cache`

Lesson:

- Focused probe success is necessary but not sufficient. The full SQuAD rerun
  exposed judge/directness variance around the causal helper, even though the
  helper row was present and clean.
- The residual-share repair is stable enough for the current evidence: the
  Rhine row stayed inside without helper rows.
- Causal end-state support is architecturally useful, but the judge still has a
  directness bias for questions phrased as "what ended" when the reference
  names an upstream cause. Do not hard-code the SQuAD reference preference into
  architecture; keep this as causal/directness pressure.
- The current full score is a measurement, not a regression verdict. It should
  be tracked as a cold QA rerun with variance, while stable focused probes and
  targeted rows remain the stronger evidence for specific repairs.

Next pressure:

- Do not chase the full-run score row by row. Next useful work is to separate
  judge/reference noise from durable architecture pressure: answer-surface
  false-reference rows, directness bias in causal chains, and remaining
  category/generalization source-detail gaps.

### DT-045 - Short Negative Answer Judge Stabilization

Date: 2026-05-13

Before:

- DT-044 exposed a short negative reference row where the query results already
  contained explicit negative support, including a normalized negative value and
  a source text atom with the same negative claim.
- The judge returned `miss` while its own explanation said the evidence
  supported the reference. That made this look like answer-surface pressure, but
  the first question was whether the broader negative/exception axis was already
  inside.

Prediction:

- If the negative/exception surface is truly missing, the existing unlike probe
  should fail under current code.
- If the unlike probe holds, the SQuAD row is a narrow judge-stability defect:
  short negative references need a deterministic precheck when returned row
  values carry explicit negative surfaces.

Intervention:

- Replayed the existing unlike negative/exception answer-surface probe with
  current code.
- Added a deterministic precheck before the LLM judge for very short negative
  references (`no`, `not`, `none`, `false`, `negative`).
- The precheck only inspects returned row values, not query strings or fixture
  names, and only fires on generic normalized negative surfaces such as
  `no_*`, `does_not_*`, `did_not_*`, `not_*`, `without_*`, `lacks_*`, and
  `lack_of_*`.

After:

- Unlike negative/exception probe:
  - Questions: `8`.
  - Exact / partial / miss: `8 / 0 / 0`.
  - Helper rows: `0`.
  - Runtime load errors: `0`.
  - Write proposals: `0`.
- Targeted SQuAD replay:
  - Questions: `5`.
  - Exact / partial / miss: `5 / 0 / 0`.
  - Helper rows: `0`.
  - Runtime load errors: `0`.
  - Write proposals: `0`.
- Broad QA tests:
  - `151 passed`.

Artifacts:

- Unlike probe compile:
  `tmp\boundary_probe_compile_negative_exception_current_20260513`
- Unlike probe QA:
  `tmp\boundary_probe_qa_negative_exception_current_20260513`
- Targeted SQuAD replay:
  `tmp\mrc_transfer_qa_squad30_dt045_sky_negative_precheck_20260513`

Verification:

- `python scripts\run_domain_bootstrap_qa_batch.py --dataset-root tmp\mrc_transfer_staged_squad30_20260513 --fixture squad_default_validation_00007_sky_united_kingdom --compile-root tmp\mrc_transfer_compile_squad30_dt036_full_20260513 --out-root tmp\mrc_transfer_qa_squad30_dt045_sky_negative_precheck_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 420 --no-cache`
- `python scripts\summarize_mrc_transfer_qa.py --qa-root tmp\mrc_transfer_qa_squad30_dt045_sky_negative_precheck_20260513`
- `python -m pytest tests\test_domain_bootstrap_qa.py -q`

Lesson:

- Broad negative/exception answer-surface handling was already interior. The
  defect was a judge self-contradiction around short negative reference answers,
  not a compile, selector, or helper gap.
- This is a judge-stability repair, not a fixture repair. The trigger is
  value-scoped and shape-based; it does not depend on passage vocabulary,
  question ids, answer strings beyond the short negative reference class, or
  local entity names.

Next pressure:

- Continue separating stable architecture pressure from measurement noise. The
  strongest next candidates are false-reference rows, causal directness
  variance, and category/generalization gaps where the KB has supporting facts
  but the answer surface is too broad or too lexical to render cleanly.

### DT-046 - Source Text Filter Query Repair and OpenRouter Tagging

Date: 2026-05-13

Before:

- DT-044 left one clean `query_surface_resolution` row: the KB contained the
  answer-bearing source text atom, but an evidence-bundle query tried to filter
  it with unsupported `memberchk/2`.
- The failure was not that the source text was absent. It was that the
  control-plane query used a Prolog helper outside the compiled inventory.
- OpenRouter logs also showed `App = Unknown` for hosted pressure runs, making
  retrospective spend/runtime analysis harder than necessary.

Prediction:

- A generic source-text containment repair should move the `memberchk/2` row
  without admitting new facts or helpers.
- The repair should execute only for the narrow pattern
  `source_record_text_atom(Line, Text), memberchk('normalized_phrase', Text)`;
  everything else should still go through the normal predicate-inventory gate.
- Hosted runs should carry an `X-Title` header derived from the experiment
  output path unless the operator supplies an explicit title.

Intervention:

- Added a value-preserving evidence-bundle query repair:
  - detect the narrow source-text/member containment pattern,
  - execute the admitted `source_record_text_atom/2` predicate,
  - apply normalized containment outside Prolog,
  - mark the result as `source_text_contains_filter_repaired`.
- Added a fixture-free unit test using generic source text.
- Added OpenRouter `X-Title` support in the compile runner, QA runner, and
  shared Semantic IR request layer. The default title is
  `prethinker:<experiment>/<fixture>` from the output path, with
  `PRETHINKER_OPENROUTER_TITLE`, `OPENROUTER_APP_TITLE`, or
  `OPENROUTER_X_TITLE` as overrides.

After:

- Targeted geology replay:
  - Questions: `5`.
  - Exact / partial / miss: `4 / 0 / 1`.
  - Helper rows: `0`.
  - Runtime load errors: `0`.
  - Write proposals: `0`.
- The original `query_surface_resolution` row moved:
  - q004 now exact.
  - The returned row contains the answer-bearing source text, and the judge
    recognizes the reference from that source row.
- The remaining miss is a different compile-surface gap:
  - q001 asks for the purpose/use of an instrument.
  - The KB has instrument/property rows, but no symbolic surface linking those
    rows to the broader source-stated purpose.
- Broad QA tests:
  - `154 passed`.

Artifacts:

- Targeted SQuAD replay:
  `tmp\mrc_transfer_qa_squad30_dt046_geology_source_text_filter_20260513`
- Summary:
  `tmp\mrc_transfer_qa_squad30_dt046_geology_source_text_filter_20260513\transfer_coordinate_summary.md`

Verification:

- `python scripts\run_domain_bootstrap_qa_batch.py --dataset-root tmp\mrc_transfer_staged_squad30_20260513 --fixture squad_default_validation_00013_geology --compile-root tmp\mrc_transfer_compile_squad30_dt036_full_20260513 --out-root tmp\mrc_transfer_qa_squad30_dt046_geology_source_text_filter_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 420 --no-cache`
- `python scripts\summarize_mrc_transfer_qa.py --qa-root tmp\mrc_transfer_qa_squad30_dt046_geology_source_text_filter_20260513`
- `python -m pytest tests\test_domain_bootstrap_qa.py -q`

Lesson:

- Evidence-bundle plans are allowed to be query guidance, not a new Prolog
  language. When they emit an unsupported source-text filter, the architecture
  should translate only the containment operation onto admitted source-record
  rows rather than pretend `memberchk/2` is part of the compiled KB.
- This is a query repair, not a helper or fixture repair. It is source-faithful
  because it returns only existing source-record rows and adds no semantic
  conclusion.
- Operational tags matter now that dataset-transfer work uses hosted pressure
  heavily. `X-Title` gives the lab a cheap way to separate SQuAD, RACE, MAUD,
  PrivacyQA, and focused probe costs in OpenRouter logs.

Next pressure:

- The next machinery-shaped SQuAD gap is source-stated purpose/use: the source
  text names a task or purpose, while structured rows preserve adjacent
  instrument/property facts. Probe this as purpose-surface preservation before
  any repair, because it may overlap with broader component/category surface
  preservation.

### DT-047 - Purpose/Use Surface Probe

Date: 2026-05-14

Before:

- DT-046 moved the source-text query-filter row, leaving a different geology
  miss: the source stated a broader task/use near instrument/property rows, but
  the structured KB evidence available to QA emphasized the lower-level
  properties.
- This looked like a possible purpose/use surface gap, but the SQuAD row alone
  was too local to justify repair.

Prediction:

- If purpose/use extraction is missing generally, an unlike probe with multiple
  tools, uses, measurements, and negative-use boundaries should fail.
- If the probe passes, the SQuAD row is a dense-context variant rather than a
  missing axis. The right next step would be density characterization, not
  architecture change.

Intervention:

- Added `purpose_use_surface_ladder`, a new unlike probe with:
  - five tool/user/source-purpose pairs,
  - adjacent measurement/property rows,
  - explicit negative-use controls,
  - open-ended QA for both broader use and narrower measured attributes.
- Compiled and ran QA through OpenRouter using the new experiment title tagging.

After:

- Compile:
  - Parsed OK: `1`.
  - Candidate predicates: `7`.
  - Compile admitted / skipped: `80 / 0`.
  - Rough score: `0.833`.
- QA:
  - Questions: `10`.
  - Exact / partial / miss: `10 / 0 / 0`.
  - Helper rows: `0`.
  - Runtime load errors: `0`.
  - Write proposals: `0`.
- No repair was made.

Artifacts:

- Probe:
  `experiments\boundary_probes\dataset_transfer_stage2\purpose_use_surface_ladder`
- Compile:
  `tmp\boundary_probe_compile_purpose_use_surface_20260513`
- QA:
  `tmp\boundary_probe_qa_purpose_use_surface_20260513`
- Summary:
  `tmp\boundary_probe_qa_purpose_use_surface_20260513\transfer_coordinate_summary.md`

Verification:

- `python scripts\run_domain_bootstrap_file_batch.py --dataset-root experiments\boundary_probes\dataset_transfer_stage2 --fixture purpose_use_surface_ladder --out-root tmp\boundary_probe_compile_purpose_use_surface_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 1 --timeout 900 --compile-source --compile-flat-plus-plan-passes --focused-pass-ops-schema --source-record-ledger --source-record-ledger-facts`
- `python scripts\run_domain_bootstrap_qa_batch.py --dataset-root experiments\boundary_probes\dataset_transfer_stage2 --fixture purpose_use_surface_ladder --compile-root tmp\boundary_probe_compile_purpose_use_surface_20260513 --out-root tmp\boundary_probe_qa_purpose_use_surface_20260513 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 420 --no-cache`
- `python scripts\summarize_mrc_transfer_qa.py --qa-root tmp\boundary_probe_qa_purpose_use_surface_20260513`

Lesson:

- Simple source-stated purpose/use is interior. The compile can preserve a
  broader use surface separately from adjacent measurement/property surfaces and
  can also preserve explicit negative-use boundaries.
- The SQuAD geology miss should not be repaired as a broad purpose/use gap.
  Its pressure is denser: the broad task is expressed as the frame for a method
  paragraph, while the local structured rows bind the instrument to lower-level
  measured properties.
- This is the live-set pattern again: simple coordinate inside, dense variant
  still blurry.

Next pressure:

- Probe density around purpose surfaces rather than adding machinery: cases
  where a paragraph-level task frames several methods/instruments, and the
  question asks for the frame-level task through one method.

### DT-048 - Dense Purpose Frame Boundary

Date: 2026-05-14

Before:

- DT-047 showed that direct purpose/use surfaces are interior.
- The unresolved SQuAD pressure was denser: a paragraph-level task frames
  multiple methods or instruments, and the question asks what one method is
  used for. The method's local rows preserve measurements/actions, while the
  frame-level task may sit on the paragraph anchor or agent/domain row.

Prediction:

- A dense probe should fail if the architecture cannot connect method-level
  rows back to the agent/task frame.
- Failures should cluster on high-level task answers; direct measurement and
  negative-use controls should mostly hold.

Intervention:

- Added `dense_purpose_frame_ladder`, an unlike probe with:
  - four agent/task frames,
  - two methods per frame,
  - lower-level metrics/actions per method,
  - explicit negative-purpose controls,
  - QA that alternates frame-level purpose questions with direct metric and
    negative-control questions.
- Compiled and ran QA through OpenRouter.

After:

- Compile:
  - Parsed OK: `1`.
  - Candidate predicates: `9`.
  - Compile admitted / skipped: `104 / 0`.
  - Rough score: `0.88`.
- QA:
  - Questions: `10`.
  - Exact / partial / miss: `6 / 1 / 3`.
  - Failure surfaces: `answer_surface_gap=1`, `compile_surface_gap=3`.
  - Helper rows: `0`.
  - Runtime load errors: `0`.
  - Write proposals: `0`.
- The non-exact rows are exactly the frame-level purpose questions:
  - method used for diagnosing a frame-level problem,
  - method used for restoring a frame-level object,
  - method used for comparing frame-level samples,
  - method used for evaluating a frame-level technique.
- Direct metric questions and negative-use controls held.

Artifacts:

- Probe:
  `experiments\boundary_probes\dataset_transfer_stage2\dense_purpose_frame_ladder`
- Compile:
  `tmp\boundary_probe_compile_dense_purpose_frame_20260514`
- QA:
  `tmp\boundary_probe_qa_dense_purpose_frame_20260514`
- Summary:
  `tmp\boundary_probe_qa_dense_purpose_frame_20260514\transfer_coordinate_summary.md`

Verification:

- `python scripts\run_domain_bootstrap_file_batch.py --dataset-root experiments\boundary_probes\dataset_transfer_stage2 --fixture dense_purpose_frame_ladder --out-root tmp\boundary_probe_compile_dense_purpose_frame_20260514 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 1 --timeout 900 --compile-source --compile-flat-plus-plan-passes --focused-pass-ops-schema --source-record-ledger --source-record-ledger-facts`
- `python scripts\run_domain_bootstrap_qa_batch.py --dataset-root experiments\boundary_probes\dataset_transfer_stage2 --fixture dense_purpose_frame_ladder --compile-root tmp\boundary_probe_compile_dense_purpose_frame_20260514 --out-root tmp\boundary_probe_qa_dense_purpose_frame_20260514 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 420 --no-cache`
- `python scripts\summarize_mrc_transfer_qa.py --qa-root tmp\boundary_probe_qa_dense_purpose_frame_20260514`

Lesson:

- Purpose/use is not one coordinate. Direct purpose is interior; inherited
  frame purpose is boundary.
- The failure is not measurement extraction. Metrics and local method actions
  survive. The missing surface is the bridge from method to paragraph-level
  task through the agent/domain/source anchor.
- This is a good repair candidate only if phrased as a generic method-frame
  support surface: method plus agent plus frame/task/domain source row. It
  should not encode any of the probe's method names, domains, or reference
  answers.

Next pressure:

- Implement and replay a generic method-frame purpose support surface that joins
  admitted method-use rows to admitted agent/domain rows and source-record frame
  text. Then replay both dense probe and the original SQuAD geology fixture.

### DT-049 - Method-Frame Purpose Support Repair

Date: 2026-05-14

Before:

- DT-048 isolated a real dense-purpose boundary:
  - direct measurement rows held,
  - negative-use controls held,
  - frame-level purpose questions failed.
- The desired repair had to connect a method to its broader agent/task frame
  without naming any fixture method, domain, question, or answer.

Prediction:

- A query-only support surface that joins admitted method-use rows to admitted
  agent/frame rows should move the dense probe if the frame axis is present.
- The original SQuAD geology row may remain non-exact if its older compile
  lacks the same frame-axis predicates.

Intervention:

- Added `method_frame_purpose_support`, a clean query-only companion.
- Trigger shape:
  - admitted `agent_uses_method(Agent, Method)`,
  - admitted `agent_operates_in(Agent, FramePurpose)`,
  - source-record label/text rows that overlap the agent or frame-purpose
    tokens.
- Added a judge policy stating that this support row is answer-bearing for
  method-use questions when the method and agent bind the asked surface and the
  frame purpose/source text binds the broader source-stated task.
- Added a fixture-free unit test over generic operator/method/frame facts.

After:

- Dense purpose-frame replay:
  - Questions: `10`.
  - Exact / partial / miss: `10 / 0 / 0`.
  - Helper rows: `22`.
  - Helper class: `clean-helper`.
  - Runtime load errors: `0`.
  - Write proposals: `0`.
- SQuAD geology replay:
  - Questions: `5`.
  - Exact / partial / miss: `4 / 0 / 1`.
  - Helper rows: `0`.
  - Runtime load errors: `0`.
  - Write proposals: `0`.
- Direct compile inspection explains the blocked transfer:
  - SQuAD geology compile exposes `uses_instrument/2`, `analyzes_property/2`,
    and source-record text.
  - It does not expose `agent_uses_method/2` or `agent_operates_in/2`, so the
    generic companion has no admitted frame axis to join.
- Broad QA tests:
  - `155 passed`.

Artifacts:

- Dense replay:
  `tmp\boundary_probe_qa_dense_purpose_frame_repair_20260514`
- SQuAD replay:
  `tmp\mrc_transfer_qa_squad30_dt049_geology_method_frame_replay_20260514`
- SQuAD compile inspected:
  `tmp\mrc_transfer_compile_squad30_dt036_full_20260513\squad_default_validation_00013_geology`

Verification:

- `python scripts\run_domain_bootstrap_qa_batch.py --dataset-root experiments\boundary_probes\dataset_transfer_stage2 --fixture dense_purpose_frame_ladder --compile-root tmp\boundary_probe_compile_dense_purpose_frame_20260514 --out-root tmp\boundary_probe_qa_dense_purpose_frame_repair_20260514 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 420 --no-cache`
- `python scripts\run_domain_bootstrap_qa_batch.py --dataset-root tmp\mrc_transfer_staged_squad30_20260513 --fixture squad_default_validation_00013_geology --compile-root tmp\mrc_transfer_compile_squad30_dt036_full_20260513 --out-root tmp\mrc_transfer_qa_squad30_dt049_geology_method_frame_replay_20260514 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 420 --no-cache`
- `python -m pytest tests\test_domain_bootstrap_qa.py -q`

Lesson:

- Dense method-frame purpose can be repaired generically when the compile
  exposes a frame axis. This extends the interior for a real boundary found by
  DT-048.
- The SQuAD geology miss did not move because the compile surface is older and
  narrower: it preserved method/property and source text, not agent/frame
  linkage. That is valuable negative transfer evidence.
- The next repair should not special-case `uses_instrument` or any geology
  vocabulary. If we want this SQuAD row to move, the right target is a generic
  compile-surface rule for preserving task/frame purpose around method catalogs.

Next pressure:

- Decide whether to recompile a small SQuAD geology-like fixture with current
  source-record and frame-purpose expectations, or to build a generic compile
  probe for method catalogs where a paragraph-level task frames methods and
  measurements. Do not add QA helpers for the old compile surface alone.

### DT-050 - Geology Recompile Surface Tradeoff

Date: 2026-05-14

Before:

- DT-049 repaired dense method-frame purpose when the compile exposes
  `agent_uses_method` and `agent_operates_in`.
- The original SQuAD geology compile did not expose that frame axis. It exposed
  `uses_instrument`, `analyzes_property`, and source-record text instead.
- The open question was whether a fresh compile would preserve the missing
  purpose axis, or whether the compiler generally failed to capture it.

Prediction:

- If the fresh compile emits a purpose predicate for methods, then the old
  SQuAD miss is a compile-surface variance/staleness problem rather than a
  missing architecture capability.
- If the fresh QA still fails, the remaining issue is likely answer rendering or
  stable multi-surface preservation across alternative predicate palettes.

Intervention:

- Recompiled the original SQuAD geology fixture with the current compiler,
  source-record ledger, flat-plus-plan passes, and OpenRouter tagging.
- Ran QA against the fresh compile.
- Compared the new predicate surface against the old compile.

After:

- Fresh compile:
  - Parsed OK: `1`.
  - Candidate predicates: `9`.
  - Compile admitted / skipped: `31 / 0`.
  - Rough score: `0.889`.
- Fresh compile surface changed materially:
  - New high-level purpose rows include
    `primary_method(electron_microprobe, identifying_rocks_in_the_laboratory)`
    and `primary_method(electron_microprobe, rock_identification)`.
  - The old compile's `uses_instrument`/`analyzes_property` surface was replaced
    by a different palette including `primary_method` and
    `analyzes_component`.
- Fresh QA:
  - Questions: `5`.
  - Exact / partial / miss: `3 / 1 / 1`.
  - Helper rows: `0`.
  - Runtime load errors: `0`.
  - Write proposals: `0`.
- Movement:
  - The original purpose/use row moved inside.
  - A property/lens row became partial because only one property was linked to
    the lens-specific predicate.
  - The location row became an answer-surface miss because the retrieved
    purpose atom contained `..._in_the_laboratory`, but the final answer needed
    the location phrase itself.

Artifacts:

- Fresh compile:
  `tmp\mrc_transfer_compile_squad30_dt050_geology_recompile_20260514`
- Fresh QA:
  `tmp\mrc_transfer_qa_squad30_dt050_geology_recompile_20260514`
- Summary:
  `tmp\mrc_transfer_qa_squad30_dt050_geology_recompile_20260514\transfer_coordinate_summary.md`

Verification:

- `python scripts\run_domain_bootstrap_file_batch.py --dataset-root tmp\mrc_transfer_staged_squad30_20260513 --fixture squad_default_validation_00013_geology --out-root tmp\mrc_transfer_compile_squad30_dt050_geology_recompile_20260514 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 1 --timeout 900 --compile-source --compile-flat-plus-plan-passes --focused-pass-ops-schema --source-record-ledger --source-record-ledger-facts`
- `python scripts\run_domain_bootstrap_qa_batch.py --dataset-root tmp\mrc_transfer_staged_squad30_20260513 --fixture squad_default_validation_00013_geology --compile-root tmp\mrc_transfer_compile_squad30_dt050_geology_recompile_20260514 --out-root tmp\mrc_transfer_qa_squad30_dt050_geology_recompile_20260514 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 420 --no-cache`
- `python scripts\summarize_mrc_transfer_qa.py --qa-root tmp\mrc_transfer_qa_squad30_dt050_geology_recompile_20260514`

Lesson:

- The compiler can preserve method purpose when the pass plan asks for it. The
  old SQuAD miss was not proof that the axis was unavailable.
- But preserving one surface can trade off against another. The fresh compile
  gained purpose rows while losing or narrowing the older property/lens surface.
- This is the next major research shape: stable multi-surface preservation. The
  architecture should preserve frame purpose, method details, measurement
  properties, and location phrases together rather than rotating among them
  across compiles.

Next pressure:

- Build a generic method-catalog compile probe that demands simultaneous
  preservation of:
  - frame purpose,
  - method/property details,
  - instrument or condition details,
  - location/context phrase extraction.
- Treat success as multi-surface stability, not row-count expansion.

### DT-051 - Method Catalog Stability Probe

Date: 2026-05-14

Before:

- DT-050 showed a method-catalog surface tradeoff: a fresh compile could recover
  method purpose, but detail and location surfaces could shift.
- The next pressure was to test simultaneous preservation on an unlike,
  fixture-free method catalog before designing any repair.

Prediction:

- If purpose, method detail, condition, and context-location surfaces all
  survive together, the DT-050 SQuAD movement is mostly old-compile variance.
- If the probe misses, classify whether the miss is:
  - method-detail loss,
  - context/location loss,
  - frame-object loss,
  - source-record addressability loss.

Intervention:

- Added `method_catalog_surface_stability_ladder`, a 16-question focused probe
  over four unlike operational method paragraphs.
- Compiled it with the current source-record ledger and current OpenRouter
  request tagging.
- Ran QA on the compile.
- Briefly trialed a role-method source-frame helper after the two misses, then
  discarded it when inspection showed the needed source-record rows were absent
  rather than merely ignored.
- Repaired deterministic source-record ledger coverage so plain paragraph lines
  are addressable source rows, not only headings, tables, bullets, labels, and
  heuristic anchor lines.
- Added a query-only `method_actor_frame_source_support` companion plus a strict
  source-record reference-support policy for cases where the asked frame object
  is present in returned source-record text.
- Shortened OpenRouter titles to phase-plus-fixture labels:
  `compile:<fixture>` and `qa:<fixture>`.

After:

- Compile:
  - Parsed OK: `1`.
  - Candidate predicates: `9`.
  - Compile admitted / skipped: `90 / 6`.
  - Rough score: `0.833`.
  - Repeated-structure role mismatch refs included `method_condition/2`,
    `method_measures/2`, `method_not_performed_at/2`, and
    `method_performed_at/2`.
- First QA:
  - Questions: `16`.
  - Exact / partial / miss: `14 / 0 / 2`.
  - Failure surfaces: `compile_surface_gap: 2`.
  - Helper rows: `0`.
- Diagnostic helper replay:
  - Delivered `18` clean `role_method_frame_source_support` rows.
  - Still scored `14 / 0 / 2`.
  - Inspection showed the helper only had source-record text for the first and
    third paragraphs; the second and fourth paragraph frame text was not emitted
    as `source_record_text_atom`/`source_record_label`.
  - No helper code was retained.
- Ledger repair compile:
  - Parsed OK: `1`.
  - Candidate predicates: `8`.
  - Compile admitted / skipped: `101 / 0`.
  - Rough score: `0.833`.
  - Repeated-structure role mismatch refs: none.
- Ledger repair QA before source-record support:
  - Exact / partial / miss: `12 / 0 / 4`.
  - This got worse because the compile surface shifted to a cleaner
    method-catalog vocabulary while the QA/judge layer still over-valued method
    measures and under-valued returned source-record text.
- Final QA after source-record support:
  - Exact / partial / miss: `16 / 0 / 0`.
  - Failure surfaces: `not_applicable: 16`.
  - Helper rows: `50`, all clean `method_actor_frame_source_support`.
  - Runtime load errors: `0`.
  - Write proposals: `0`.

Boundary Classification:

- The two misses were not method-detail failures. The KB retrieved role,
  method, location, condition, and measurement rows.
- The missing coordinate was the frame object/objective:
  - what a role was comparing,
  - what a role was verifying.
- The deeper cause was source-record addressability incompleteness: deterministic
  source-record support was present for only two of four method-catalog
  paragraphs, so the QA layer could not recover the missing frame object from
  source text.
- After source-record ledger repair, a remaining condition miss showed a second
  boundary: helper frame support must prefer exact source text atoms over broad
  repeated paragraph labels when a method is explicitly bound.

Artifacts:

- Probe:
  `experiments\boundary_probes\dataset_transfer_stage2\method_catalog_surface_stability_ladder`
- Compile:
  `tmp\boundary_probe_compile_method_catalog_stability_20260514`
- First QA:
  `tmp\boundary_probe_qa_method_catalog_stability_20260514`
- Diagnostic replay:
  `tmp\boundary_probe_qa_method_catalog_stability_repair_20260514`
- Ledger repair compile:
  `tmp\boundary_probe_compile_method_catalog_stability_ledger_repair_20260514`
- Ledger repair QA:
  `tmp\boundary_probe_qa_method_catalog_stability_ledger_repair_20260514`
- Final QA:
  `tmp\boundary_probe_qa_method_catalog_stability_final2_20260514`

Verification:

- `python scripts\run_domain_bootstrap_file_batch.py --dataset-root experiments\boundary_probes\dataset_transfer_stage2 --fixture method_catalog_surface_stability_ladder --out-root tmp\boundary_probe_compile_method_catalog_stability_20260514 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 1 --timeout 900 --compile-source --compile-flat-plus-plan-passes --focused-pass-ops-schema --source-record-ledger --source-record-ledger-facts`
- `python scripts\run_domain_bootstrap_qa_batch.py --dataset-root experiments\boundary_probes\dataset_transfer_stage2 --fixture method_catalog_surface_stability_ladder --compile-root tmp\boundary_probe_compile_method_catalog_stability_20260514 --out-root tmp\boundary_probe_qa_method_catalog_stability_20260514 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 420 --no-cache`
- `python scripts\run_domain_bootstrap_qa_batch.py --dataset-root experiments\boundary_probes\dataset_transfer_stage2 --fixture method_catalog_surface_stability_ladder --compile-root tmp\boundary_probe_compile_method_catalog_stability_20260514 --out-root tmp\boundary_probe_qa_method_catalog_stability_repair_20260514 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 420 --no-cache`
- `python scripts\run_domain_bootstrap_file_batch.py --dataset-root experiments\boundary_probes\dataset_transfer_stage2 --fixture method_catalog_surface_stability_ladder --out-root tmp\boundary_probe_compile_method_catalog_stability_ledger_repair_20260514 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 1 --timeout 900 --compile-source --compile-flat-plus-plan-passes --focused-pass-ops-schema --source-record-ledger --source-record-ledger-facts`
- `python scripts\run_domain_bootstrap_qa_batch.py --dataset-root experiments\boundary_probes\dataset_transfer_stage2 --fixture method_catalog_surface_stability_ladder --compile-root tmp\boundary_probe_compile_method_catalog_stability_ledger_repair_20260514 --out-root tmp\boundary_probe_qa_method_catalog_stability_final2_20260514 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 6 --timeout 420 --no-cache`
- `python -m pytest tests\test_domain_bootstrap_qa.py tests\test_source_record_ledger.py -q`

Lesson:

- The method-catalog surface is inside the set when deterministic source
  addressability is complete and the QA layer treats returned source-record text
  as answer-bearing.
- The repair is generic: preserve plain prose source rows, expose role/method
  frame text as query-only support, and prefer exact source text over repeated
  labels when a method is bound. No fixture terms, row ids, answer strings, or
  local entities entered architecture.
- The failed intermediate helper was useful: it proved that helper policy cannot
  compensate for missing source-record coverage. Ledger completeness comes
  before helper confidence.

Next pressure:

- Re-run a small unlike replay set that uses source-record ledger facts to check
  for helper-volume regressions and accidental source-text over-crediting.
- Then return to the dataset-transfer map: classify whether remaining SQuAD/RACE
  misses are frame-object, condition-as-tool, synthesis, or true absent-axis
  cases.
