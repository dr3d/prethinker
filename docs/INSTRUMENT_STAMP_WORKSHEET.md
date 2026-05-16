# Instrument Stamp Worksheet

Purpose: characterize the frozen Prethinker instrument across the corpora we
already staged, using repeated fresh compile-plus-QA draws. This is measurement,
not repair.

Instrument under evaluation:

- Tag: `instrument-2026-05-14-dt053`
- Executable state: same code as current `main`; later commits are journal-only
  unless noted otherwise.
- Operating rule: no architecture, helper, selector, compile, prompt, or judge
  repairs during a stamp run. Failures become measurement evidence.

Stamp Protocol:

- Run at least `N=3` fresh compile-plus-QA draws per corpus when budget and
  transport allow.
- Report mean, range, and peak exact rate.
- Track runtime load errors, write proposal rows, helper pressure, and transport
  retries.
- Keep OpenRouter to `6` lanes or fewer; prefer `4` compile lanes when provider
  throttling appears.
- Retry transport-failed compile fixtures narrowly; do not change code or
  prompts during retries.
- Treat ugly or noisy datasets as evidence about transfer conditions, not as
  permission to tune toward them.

Corpus Inventory:

| Corpus | Staged root | Fixtures | Questions | Stamp status |
| --- | --- | ---: | ---: | --- |
| SQuAD-30 | `tmp\mrc_transfer_staged_squad30_20260513` | 30 | 171 | Complete, `N=3` |
| RACE-50 | `tmp\mrc_transfer_staged_race50_options_20260513` | 50 | 177 | Complete, `N=3`, corrected MCQ option-visible root |
| PrivacyQA-30 | `tmp\mrc_transfer_staged_privacyqa30_20260513` | 30 | 30 | Complete, `N=3` |
| MAUD-10 | `tmp\mrc_transfer_staged_maud10_20260513` | 10 | 40 | Complete, `N=3` |
| CUAD-10 | `tmp\mrc_transfer_staged_cuad10_20260513` | 10 | 40 | Complete, `N=3`; rough corpus evidence |
| Story-world corpus | `datasets\story_worlds` | 56 | 2163 draw-1 scored | Provisional native stamp, `N=1` |

## Stamp Rollup

Date: 2026-05-14

This rollup characterizes the frozen instrument after three fresh compile-plus-QA
draws per completed corpus. It is a measurement table, not a repair queue.

| Corpus | Questions per draw | Mean exact | Range | Peak | Dominant observed pressure |
| --- | ---: | ---: | --- | ---: | --- |
| SQuAD-30 | 171 | 92.20% | 91.23%-92.98% | 92.98% | direct factual QA with light compile variance |
| RACE-50, option-visible | 177 | 84.56% | 83.05%-86.44% | 86.44% | inference/background facts over MCQ propositions |
| PrivacyQA-30 | 30 | 82.22% | 80.00%-83.33% | 83.33% | factual policy compile/query resolution |
| MAUD-10 | 40 | 45.00% | 45.00%-45.00% | 45.00% | categorical clause and exception semantics |
| CUAD-10 | 40 | 92.50% | 90.00%-95.00% | 95.00% | mostly factual contract compile/query resolution |
| Story-world corpus | 2163 | 84.33% | provisional `N=1` | 84.33% | native-corpus compile-surface gaps and helper volume |

Rollup observations:

- The frozen instrument is not merely fitting the original fixture corpus:
  SQuAD and CUAD both stamp in the low-90s under fresh compiles.
- Corrected RACE and PrivacyQA form a low/mid-80s transfer band where the
  pressure is mostly proposition shape and resolution, not transport.
- MAUD is the sharp boundary outlier. Its low score does not generalize to all
  contract text because CUAD lands high; the pressure is categorical
  clause-role and exception semantics.
- OpenRouter transport was manageable at `6` lanes or fewer. RACE compile needed
  narrow retries; PrivacyQA, MAUD, and CUAD compiled cleanly at `3` lanes.
- The stamp has enough spread to support post-stamp work, but the code should
  remain frozen for this measurement series.
- The current native story-world corpus is much larger than the earlier
  41-fixture memory: `56` runnable source-plus-QA fixtures were present at stamp
  time.

## IS-001 - SQuAD-30 Stamp Imported From Dataset Transfer

Date: 2026-05-14

Before:

- SQuAD-30 was the first corpus stamped while closing the Dataset Transfer
  worksheet.
- The QA-only stabilization anchor was `161 / 2 / 8` over `171`, exact
  `94.15%`, but it reused an older compile and therefore was not the fresh
  compile-plus-QA stamp number.

Intervention:

- Ran three fresh compile-plus-QA draws under the frozen instrument.
- Logged provider retries as transport, not architecture.

After:

| Draw | Exact | Partial | Miss | Exact rate | Helper rows | Transport |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `draw1` | 158 | 2 | 11 | 92.40% | 0 | 3 compile fixtures retried after upstream 429s |
| `draw2` | 159 | 5 | 7 | 92.98% | 0 | 1 compile fixture retried after upstream 429 |
| `draw3` | 156 | 2 | 13 | 91.23% | 3 | no compile transport retry |

Stamp summary:

- Mean exact rate: `92.20%`.
- Range: `91.23%` to `92.98%`.
- Peak: `92.98%`.
- Runtime load errors: `0` in all QA draws.
- Write proposal rows: `0` in all QA draws.
- Helper pressure: absent or bounded.

Artifacts:

- `tmp\instrument_stamp_20260514_squad30_draw1_compile`
- `tmp\instrument_stamp_20260514_squad30_draw1_qa`
- `tmp\instrument_stamp_20260514_squad30_draw2_compile`
- `tmp\instrument_stamp_20260514_squad30_draw2_qa`
- `tmp\instrument_stamp_20260514_squad30_draw3_compile`
- `tmp\instrument_stamp_20260514_squad30_draw3_qa`

Lesson:

- The frozen instrument is a low-90s fresh compile-plus-QA system on SQuAD-30.
- The proper stamped claim is the variance band, not the previous QA-only peak.
- Helper pressure is not the limiting factor on this corpus.

Next pressure:

- Stamp RACE-50 against the corrected option-visible staging root with the same
  no-repair discipline.

## IS-002 - RACE-50 Option-Visibility Measurement Check

Date: 2026-05-14

Before:

- RACE-50 is a multiple-choice corpus. Its questions need the visible choice
  set to be a fair selection-among-known-options task.
- The first stamp attempt used `tmp\mrc_transfer_staged_race50_20260513`.

Prediction:

- If the QA runner saw only the question stems, RACE would be measured as an
  unfair open-ended fill-in task and the score would be depressed.
- The measurement should be restarted from the corrected option-visible root,
  not repaired architecturally.

Intervention:

- Checked the staged RACE files and QA runner.
- Confirmed `scripts\run_domain_bootstrap_qa_batch.py` reads each fixture's
  `qa.md`.
- Confirmed the uncorrected staged root kept options only in `qa_source.md`,
  while `qa.md` contained stems only.
- Confirmed the corrected root
  `tmp\mrc_transfer_staged_race50_options_20260513` has options inline in
  `qa.md` and keeps the answer key isolated in `oracle.jsonl`.

After:

- Invalidated the first uncorrected RACE stamp attempt as measurement hygiene:
  - `draw1`: `120 exact / 5 partial / 51 miss`, exact `67.80%`.
  - `draw2`: `121 exact / 9 partial / 46 miss`, exact `68.36%`.
  - `draw3` compile stopped at `49/50` after one upstream 429 and should not
    be carried into QA.
- These artifacts remain useful as evidence that the option surface matters,
  but they are not stamp evidence for RACE.

Artifacts:

- Invalid uncorrected RACE attempt:
  `tmp\instrument_stamp_20260514_race50_draw1_compile`,
  `tmp\instrument_stamp_20260514_race50_draw1_qa`,
  `tmp\instrument_stamp_20260514_race50_draw2_compile`,
  `tmp\instrument_stamp_20260514_race50_draw2_qa`,
  `tmp\instrument_stamp_20260514_race50_draw3_compile`
- Corrected RACE root:
  `tmp\mrc_transfer_staged_race50_options_20260513`

Verification:

- `qa.md` in the corrected root includes inline option labels and option text.
- `oracle.jsonl` remains the only answer-bearing file used for reference
  scoring.

Lesson:

- Stamp runs must audit the task interface as well as the model result. For
  multiple-choice corpora, hiding the options changes the proposition being
  measured.
- This is not an architecture failure and not permission to tune toward RACE;
  it is a measurement setup correction.

Next pressure:

- Restart RACE-50 `N=3` from the corrected option-visible root.

## IS-003 - RACE-50 Corrected Stamp

Date: 2026-05-14

Before:

- The corrected RACE root exposes multiple-choice options in `qa.md` while
  keeping reference answers isolated.
- Earlier RACE transfer work reported `147 / 5 / 25` over `177` after
  source-record replay, but that was not a fresh repeated stamp.

Prediction:

- Corrected RACE should land above the invalid option-hidden score and near the
  previous corrected transfer band.
- Remaining misses should be proposition-resolution evidence, not an interface
  artifact.

Intervention:

- Ran three corrected RACE fresh compile-plus-QA draws.
- Retried compile transport failures narrowly, at one lane, then regenerated
  the existing compile summaries.

After:

| Draw | Exact | Partial | Miss | Exact rate | Helper rows | Transport |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `draw1` | 153 | 1 | 23 | 86.44% | 0 | 1 compile fixture retried after upstream 429 |
| `draw2` | 149 | 2 | 26 | 84.18% | 0 | 4 compile fixtures retried after upstream 429s |
| `draw3` | 147 | 3 | 27 | 83.05% | 1 | 3 compile fixtures retried after upstream 429s |

Stamp summary:

- Mean exact rate: `84.56%`.
- Range: `83.05%` to `86.44%`.
- Peak: `86.44%`.
- Runtime load errors: `0` in all QA draws.
- Write proposal rows: `0` in all QA draws.
- Helper pressure: absent or bounded.
- Aggregate non-exact rows across the three draws: `82` (`76` miss, `6`
  partial).

Aggregate proposition types across non-exact rows:

- `factual`: `37`
- `inference`: `31`
- `comparative`: `7`
- `synthesis`: `4`
- `categorical`: `3`

Aggregate transfer coordinates across non-exact rows:

- `implicit_attitude_or_consequence`: `26`
- `background_role_or_audience_fact`: `16`
- `direct_compile_surface_gap`: `16`
- `comparative_or_temporal_resolution`: `7`
- `query_surface_resolution`: `6`
- `false_or_exception_option_selection`: `4`
- `formula_or_rule_application`: `3`
- `title_theme_or_summary_answer`: `2`
- `hybrid_join_resolution`: `2`

Aggregate failure surfaces:

- `compile_surface_gap`: `53`
- `hybrid_join_gap`: `17`
- `query_surface_gap`: `11`
- `answer_surface_gap`: `1`

Artifacts:

- `tmp\instrument_stamp_20260514_race50_options_draw1_compile`
- `tmp\instrument_stamp_20260514_race50_options_draw1_qa`
- `tmp\instrument_stamp_20260514_race50_options_draw1_qa\transfer_coordinate_summary_with_intake.md`
- `tmp\instrument_stamp_20260514_race50_options_draw2_compile`
- `tmp\instrument_stamp_20260514_race50_options_draw2_qa`
- `tmp\instrument_stamp_20260514_race50_options_draw2_qa\transfer_coordinate_summary_with_intake.md`
- `tmp\instrument_stamp_20260514_race50_options_draw3_compile`
- `tmp\instrument_stamp_20260514_race50_options_draw3_qa`
- `tmp\instrument_stamp_20260514_race50_options_draw3_qa\transfer_coordinate_summary_with_intake.md`

Verification:

- All three QA summaries report `177` questions, `0` runtime load errors, and
  `0` write proposal rows.
- The corrected RACE `qa.md` files include answer choices; the invalid
  option-hidden runs are excluded from the stamp.

Lesson:

- Option visibility is a measurement precondition for MCQ transfer, not a model
  repair. Once visible, RACE rises from the invalid high-60s band to the
  mid-80s band under the frozen instrument.
- The remaining RACE boundary is not mainly multiple-choice mechanics. It is
  dominated by proposition-resolution pressure: implicit consequences and
  attitude, background role/audience facts, and direct compile-surface gaps.
- OpenRouter compile transport remains noisy even below six lanes; narrow
  one-fixture retries keep provider throttling from becoming architecture
  evidence.

Next pressure:

- Stamp the next unlike corpus, starting with PrivacyQA-30, using the same
  no-repair protocol.

## IS-004 - PrivacyQA-30 Stamp

Date: 2026-05-14

Before:

- PrivacyQA-30 is policy/legal prose with one open-ended policy question per
  fixture.
- Earlier transfer discussion predicted three interpretable bands: around
  `70%` would confirm a harder legal-domain extraction ceiling, around `85%`
  would suggest CUAD-specific drag, and around `50%` would imply CUAD was
  generous.

Prediction:

- PrivacyQA should be less distorted than CUAD by contract-specific annotation
  roughness, but still unlike SQuAD/RACE because policy snippets emphasize
  permissions, data uses, disclosure conditions, and exceptions.
- If the legal-policy boundary is real, non-exacts should concentrate in
  direct queryable-surface gaps rather than school-style synthesis.

Intervention:

- Ran three fresh compile-plus-QA draws under the frozen instrument.
- Used `3` OpenRouter compile lanes and `6` QA lanes.
- No transport retries were needed in any compile draw.

After:

| Draw | Exact | Partial | Miss | Exact rate | Helper rows | Transport |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `draw1` | 24 | 3 | 3 | 80.00% | 1 | none |
| `draw2` | 25 | 2 | 3 | 83.33% | 1 | none |
| `draw3` | 25 | 2 | 3 | 83.33% | 0 | none |

Stamp summary:

- Mean exact rate: `82.22%`.
- Range: `80.00%` to `83.33%`.
- Peak: `83.33%`.
- Runtime load errors: `0` in all QA draws.
- Write proposal rows: `0` in all QA draws.
- Helper pressure: absent or bounded.
- Aggregate non-exact rows across the three draws: `16` (`9` miss, `7`
  partial).

Aggregate proposition types across non-exact rows:

- `factual`: `11`
- `categorical`: `3`
- `inference`: `2`

Aggregate transfer coordinates across non-exact rows:

- `direct_compile_surface_gap`: `11`
- `query_surface_resolution`: `2`
- `background_role_or_audience_fact`: `1`
- `implicit_attitude_or_consequence`: `1`
- `hybrid_join_resolution`: `1`

Aggregate failure surfaces:

- `compile_surface_gap`: `12`
- `query_surface_gap`: `3`
- `hybrid_join_gap`: `1`

Artifacts:

- `tmp\instrument_stamp_20260514_privacyqa30_draw1_compile`
- `tmp\instrument_stamp_20260514_privacyqa30_draw1_qa`
- `tmp\instrument_stamp_20260514_privacyqa30_draw1_qa\transfer_coordinate_summary_with_intake.md`
- `tmp\instrument_stamp_20260514_privacyqa30_draw2_compile`
- `tmp\instrument_stamp_20260514_privacyqa30_draw2_qa`
- `tmp\instrument_stamp_20260514_privacyqa30_draw2_qa\transfer_coordinate_summary_with_intake.md`
- `tmp\instrument_stamp_20260514_privacyqa30_draw3_compile`
- `tmp\instrument_stamp_20260514_privacyqa30_draw3_qa`
- `tmp\instrument_stamp_20260514_privacyqa30_draw3_qa\transfer_coordinate_summary_with_intake.md`

Verification:

- All three compile draws parsed `30/30` fixtures without transport retries.
- All three QA summaries report `30` questions, `0` runtime load errors, and
  `0` write proposal rows.

Lesson:

- PrivacyQA lands in the low-80s band, close to corrected RACE and below
  SQuAD. That supports a real cross-domain pressure, but not a collapse.
- The boundary shape differs from RACE: policy non-exacts are mostly factual
  direct compile-surface gaps, not synthesis or multiple-choice option
  mechanics.
- This is clean stamp evidence because transport was quiet; the variance band
  is likely instrument/corpus behavior rather than provider noise.

Next pressure:

- Stamp MAUD-10 next. It is smaller but more contract-shaped than PrivacyQA,
  so it should clarify whether the legal-domain pressure is policy-generic or
  contract-specific.

## IS-005 - MAUD-10 Stamp

Date: 2026-05-14

Before:

- MAUD-10 is merger-agreement QA with four questions per contract fixture.
- PrivacyQA landed in the low-80s, so MAUD tests whether legal-domain transfer
  pressure is broad policy/legal prose or narrower contract-clause resolution.

Prediction:

- MAUD should be harder than PrivacyQA because the questions target categorical
  legal-clause distinctions, exceptions, definitions, and conditions over dense
  agreement text.
- If the boundary is contract-specific, non-exacts should concentrate in
  categorical compile/query surfaces rather than open-ended inference or
  synthesis.

Intervention:

- Ran three fresh compile-plus-QA draws under the frozen instrument.
- Used `3` OpenRouter compile lanes and `6` QA lanes.
- No transport retries were needed in any compile draw.

After:

| Draw | Exact | Partial | Miss | Exact rate | Helper rows | Transport |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `draw1` | 18 | 5 | 17 | 45.00% | 0 | none |
| `draw2` | 18 | 0 | 22 | 45.00% | 0 | none |
| `draw3` | 18 | 3 | 19 | 45.00% | 0 | none |

Stamp summary:

- Mean exact rate: `45.00%`.
- Range: `45.00%` to `45.00%`.
- Peak: `45.00%`.
- Runtime load errors: `0` in all QA draws.
- Write proposal rows: `0` in all QA draws.
- Helper pressure: absent.
- Aggregate non-exact rows across the three draws: `66` (`58` miss, `8`
  partial).

Aggregate proposition types across non-exact rows:

- `categorical`: `66`

Aggregate transfer coordinates across non-exact rows:

- `false_or_exception_option_selection`: `22`
- `direct_compile_surface_gap`: `20`
- `background_role_or_audience_fact`: `14`
- `query_surface_resolution`: `6`
- `answer_surface_mapping`: `2`
- `judge_transport_uncertain`: `1`
- `hybrid_join_resolution`: `1`

Aggregate failure surfaces:

- `compile_surface_gap`: `49`
- `query_surface_gap`: `8`
- `answer_surface_gap`: `5`
- `hybrid_join_gap`: `3`
- `judge_uncertain`: `1`

Artifacts:

- `tmp\instrument_stamp_20260514_maud10_draw1_compile`
- `tmp\instrument_stamp_20260514_maud10_draw1_qa`
- `tmp\instrument_stamp_20260514_maud10_draw1_qa\transfer_coordinate_summary_with_intake.md`
- `tmp\instrument_stamp_20260514_maud10_draw2_compile`
- `tmp\instrument_stamp_20260514_maud10_draw2_qa`
- `tmp\instrument_stamp_20260514_maud10_draw2_qa\transfer_coordinate_summary_with_intake.md`
- `tmp\instrument_stamp_20260514_maud10_draw3_compile`
- `tmp\instrument_stamp_20260514_maud10_draw3_qa`
- `tmp\instrument_stamp_20260514_maud10_draw3_qa\transfer_coordinate_summary_with_intake.md`

Verification:

- All three compile draws parsed `10/10` fixtures without transport retries.
- All three QA summaries report `40` questions, `0` runtime load errors, and
  `0` write proposal rows.

Lesson:

- MAUD is the first stamped corpus with a clear low-transfer ceiling: exactly
  `45.00%` exact across all three fresh draws.
- The legal-domain pressure is not uniform. Privacy policies were low-80s;
  merger agreements are much harder under the frozen instrument.
- The boundary is contract-categorical: false/exception option selection,
  clause role/background facts, and direct compile-surface gaps dominate. That
  is not a cue to patch toward MAUD during the stamp; it is evidence for the
  next post-stamp repair agenda.

Next pressure:

- Stamp CUAD-10 as rougher contract evidence, then compare CUAD against MAUD
  before deciding whether contract transfer needs a dedicated post-stamp
  worksheet.

## IS-006 - CUAD-10 Stamp

Date: 2026-05-14

Before:

- MAUD-10 landed at a stable `45.00%`, raising the question of whether the
  contract transfer gap was broad legal-domain weakness or a narrower
  clause-category boundary.
- CUAD-10 is rougher as a staged corpus, but it gives a second contract-shaped
  measurement using a different question style.

Prediction:

- If contract text itself is the problem, CUAD should land near MAUD.
- If MAUD exposed a narrower categorical/exception-clause boundary, CUAD should
  land higher and its non-exacts should be mostly factual compile/query
  resolution.

Intervention:

- Ran three fresh compile-plus-QA draws under the frozen instrument.
- Used `3` OpenRouter compile lanes and `6` QA lanes.
- No transport retries were needed in any compile draw.

After:

| Draw | Exact | Partial | Miss | Exact rate | Helper rows | Transport |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `draw1` | 37 | 2 | 1 | 92.50% | 0 | none |
| `draw2` | 36 | 2 | 2 | 90.00% | 0 | none |
| `draw3` | 38 | 1 | 1 | 95.00% | 0 | none |

Stamp summary:

- Mean exact rate: `92.50%`.
- Range: `90.00%` to `95.00%`.
- Peak: `95.00%`.
- Runtime load errors: `0` in all QA draws.
- Write proposal rows: `0` in all QA draws.
- Helper pressure: absent.
- Aggregate non-exact rows across the three draws: `9` (`4` miss, `5`
  partial).

Aggregate proposition types across non-exact rows:

- `factual`: `8`
- `inference`: `1`

Aggregate transfer coordinates across non-exact rows:

- `direct_compile_surface_gap`: `5`
- `background_role_or_audience_fact`: `1`
- `comparative_or_temporal_resolution`: `1`
- `implicit_attitude_or_consequence`: `1`
- `query_surface_resolution`: `1`

Aggregate failure surfaces:

- `compile_surface_gap`: `7`
- `query_surface_gap`: `2`

Artifacts:

- `tmp\instrument_stamp_20260514_cuad10_draw1_compile`
- `tmp\instrument_stamp_20260514_cuad10_draw1_qa`
- `tmp\instrument_stamp_20260514_cuad10_draw1_qa\transfer_coordinate_summary_with_intake.md`
- `tmp\instrument_stamp_20260514_cuad10_draw2_compile`
- `tmp\instrument_stamp_20260514_cuad10_draw2_qa`
- `tmp\instrument_stamp_20260514_cuad10_draw2_qa\transfer_coordinate_summary_with_intake.md`
- `tmp\instrument_stamp_20260514_cuad10_draw3_compile`
- `tmp\instrument_stamp_20260514_cuad10_draw3_qa`
- `tmp\instrument_stamp_20260514_cuad10_draw3_qa\transfer_coordinate_summary_with_intake.md`

Verification:

- All three compile draws parsed `10/10` fixtures without transport retries.
- All three QA summaries report `40` questions, `0` runtime load errors, and
  `0` write proposal rows.

Lesson:

- CUAD does not confirm MAUD as a general contract ceiling. It lands in the
  SQuAD-like low-90s band despite being contract prose.
- The contrast points to question shape, not domain label: CUAD non-exacts are
  mostly factual compile/query resolution, while MAUD non-exacts were entirely
  categorical and heavily false/exception-option shaped.
- The post-stamp contract agenda should therefore target categorical
  clause-role and exception semantics, not generic "legal text" handling.

Next pressure:

- Produce the instrument-stamp rollup across all completed corpora, then decide
  whether focused probe ladders should be included in the same stamp or kept as
  post-stamp validation evidence.

## IS-007 - Story-World Corpus Native Draw 1

Date: 2026-05-14

Before:

- The external transfer corpora had been stamped, but the home corpus itself
  still needed a frozen-instrument reading.
- The older working memory of `41` fixtures was stale. The current promoted
  story-world corpus contains `56` runnable source-plus-QA fixtures.

Prediction:

- The native corpus should land near or above the earlier wide-corpus snapshot
  (`82.76%` exact over `1218` questions), but helper volume may remain high
  because the corpus includes the older high-pressure fixtures.
- Compile transport may need narrow retries, but runtime/load and write-proposal
  failures should remain absent if the instrument is stable.

Intervention:

- Ran one fresh compile-plus-QA draw under the frozen instrument across all
  current `datasets\story_worlds` fixtures.
- Used `3` OpenRouter compile lanes and `6` QA lanes.
- Retried one compile transport failure narrowly at `1` lane after an upstream
  `429`; no prompt or code changed.
- The QA parent exceeded the interactive shell timeout while children remained
  alive. All child jobs were allowed to finish, then the batch summary was
  generated from existing artifacts.

After:

| Draw | Fixtures | Questions | Exact | Partial | Miss | Exact rate | Helper rows | Transport |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `draw1` | 56 | 2163 | 1824 | 92 | 247 | 84.33% | 7281 | one compile 429 retry; QA parent shell timeout, children completed |

Stamp summary:

- Mean exact rate: provisional `84.33%` (`N=1`).
- Runtime load errors: `0`.
- Write proposal rows: `0`.
- Helper pressure: `high_clean_helper_volume`, rows/exact `3.992`,
  candidate-helper share `0.1834`.

Failure-surface counts:

- `compile_surface_gap`: `242`
- `hybrid_join_gap`: `54`
- `query_surface_gap`: `31`
- `answer_surface_gap`: `6`
- `judge_uncertain`: `6`

Helper-class counts:

- `clean-helper`: `5895`
- `candidate-helper`: `1335`
- `unlabeled`: `51`

Largest helper row sources:

- `roster_state_support`: `2502`
- `source_record_packet_metadata_support`: `1838`
- `industrial_sensor_support`: `1260`
- `clinic_recall_support`: `580`
- `grant_award_support`: `408`

Lowest exact-rate fixtures in draw 1:

- `thornfield_variance`: `24 / 40`, exact `60.00%`
- `sable_creek_budget`: `27 / 40`, exact `67.50%`
- `heronvale_arts`: `17 / 25`, exact `68.00%`
- `authority_possession_custody_packet`: `30 / 40`, exact `75.00%`
- `university_lab_sample_chain`: `30 / 40`, exact `75.00%`

Artifacts:

- `tmp\instrument_stamp_20260514_story_worlds_draw1_compile`
- `tmp\instrument_stamp_20260514_story_worlds_draw1_compile\compile_batch_summary.md`
- `tmp\instrument_stamp_20260514_story_worlds_draw1_qa`
- `tmp\instrument_stamp_20260514_story_worlds_draw1_qa\qa_batch_summary.md`

Verification:

- Compile parsed `56 / 56` fixtures after the narrow transport retry.
- QA completed `56 / 56` fixtures and `2163` questions.
- Runtime load errors and write proposals were both `0`.

Lesson:

- The native corpus reading is close to the corrected RACE transfer band and
  above the older wide-corpus snapshot, but it is not a clean low-helper state.
- The same broad boundary shape persists at corpus scale: compile-surface gaps
  dominate non-exacts, while helper volume remains a separate delivery/scope
  pressure.
- The home corpus should not be used as a repair target during the stamp. This
  draw is a baseline against which post-stamp work can be compared.

Next pressure:

- Decide whether the native corpus needs `N=3` despite its high runtime cost, or
  whether one full native draw plus `N=3` external transfer stamps is the right
  characterization package for the current paper-facing stamp.

## IS-008 - No-Helper Fresh External Draw 1

Date: 2026-05-15

Before:

- The first stamp established a frozen-instrument external reading, but several
  runs still permitted bounded helper delivery or reused earlier compile
  artifacts.
- The native corpus draw exposed high helper volume (`7281` helper rows), raising
  a stricter question: whether transfer performance survives when helpers are
  genuinely absent rather than merely quiet.
- The operating constraint was measurement only: do not repair anomalies inside
  the freeze window.

Prediction:

- SQuAD and PrivacyQA should mostly hold without helpers because recent external
  transfer runs already showed sparse helper use.
- RACE should remain lower than SQuAD because MCQ option semantics add
  categorical and inference pressure, but direct option selection should still
  work through existing KB evaluation.
- Contract corpora may show wider variance because MAUD and CUAD differ sharply
  in question shape and clause-role semantics.

Intervention:

- Ran one fresh compile-plus-QA draw for five external transfer corpora under
  tag `instrument-freeze-20260515-r1`.
- Forced helpers genuinely off in QA with `--helper-companion-row-limit 0`,
  `--no-cache`, and no legacy native helper adapter flag.
- Used OpenRouter for broad SQuAD, PrivacyQA, and RACE work, and POWER/local
  5090 for MAUD and CUAD once local capacity was available.
- Kept the run clean: no prompt edits, code edits, or repair attempts after the
  freeze tag while the stamp was running.

After:

| Corpus | Questions | Exact | Partial | Miss | Exact rate | Helper rows |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `PrivacyQA-30` | 30 | 27 | 0 | 3 | 90.00% | 0 |
| `MAUD-10` | 40 | 17 | 2 | 21 | 42.50% | 0 |
| `SQuAD-30` | 171 | 165 | 1 | 5 | 96.49% | 0 |
| `CUAD-10` | 40 | 30 | 6 | 4 | 75.00% | 0 |
| `RACE-50-options` | 177 | 151 | 1 | 25 | 85.31% | 0 |
| **Aggregate** | **458** | **390** | **10** | **58** | **85.15%** | **0** |

Stamp summary:

- Runtime load errors: `0`.
- Write proposal rows: `0`.
- Helper pressure label: `no_helper_rows` across every QA summary.
- Aggregate helper rows per exact: `0.0`.

Artifacts:

- `docs\data\instrument_stamp\nohelper_fresh_draw1_rollup_20260515.json`
- `docs\data\instrument_stamp\nohelper_fresh_draw1_rollup_20260515.md`
- `tmp\instrument_stamp_20260515_fresh_privacyqa30_draw1_compile_or`
- `tmp\instrument_stamp_20260515_fresh_privacyqa30_draw1_qa_or`
- `tmp\instrument_stamp_20260515_fresh_maud10_draw1_compile_power`
- `tmp\instrument_stamp_20260515_fresh_maud10_draw1_qa_power`
- `tmp\instrument_stamp_20260515_fresh_squad30_draw1_compile_or`
- `tmp\instrument_stamp_20260515_fresh_squad30_draw1_qa_or`
- `tmp\instrument_stamp_20260515_fresh_cuad10_draw1_compile_power`
- `tmp\instrument_stamp_20260515_fresh_cuad10_draw1_qa_power`
- `tmp\instrument_stamp_20260515_fresh_race50_draw1_compile_or`
- `tmp\instrument_stamp_20260515_fresh_race50_draw1_qa_or`

Verification:

- All five fresh compile batches completed their target fixture counts.
- All five QA batches completed their target question counts.
- Every QA summary reported `0` helper rows, `0` runtime load errors, and `0`
  write proposal rows.

Lesson:

- Helper retirement is plausible for the external transfer layer: SQuAD,
  PrivacyQA, and RACE remain respectable to strong with no helper rows at all.
- CUAD's lower fresh no-helper result shows that the earlier contract headline
  was compile/helper/draw sensitive. This is an observed stamp property, not a
  mid-freeze repair target.
- MAUD remains the sharpest external boundary: its low score is not caused by
  helper delivery, and should be treated as categorical/clause-role pressure.
- The current instrument can be stamped in a true zero-helper mode for external
  transfer, but the native corpus still needs a separate helper-retirement pass
  before its helper-heavy baseline can be compared fairly.

Next pressure:

- Produce a native-corpus no-helper measurement only after deciding whether to
  reuse the current compile artifacts or pay for a fresh compile draw.
- If the next phase resumes architecture work, focus on helper replacement by
  compile-surface invariants and direct predicate emission rather than restoring
  helper adapters.

## IS-009 - No-Helper Fresh External N=2 Variance

Date: 2026-05-15 / 2026-05-16

Before:

- The no-helper external stamp had one fresh draw across five transfer corpora:
  `390 / 10 / 58` over `458` questions, `85.15%` exact, helper rows `0`.
- That was a clean helper-retirement measurement, but still only one stochastic
  compile-plus-QA draw.
- The freeze discipline remained unchanged: measure variance under the frozen
  instrument, do not repair inside the stamp window.

Prediction:

- PrivacyQA and CUAD should be relatively stable if their boundary is mostly
  query-surface and contract-role difficulty rather than stochastic compile
  omission.
- SQuAD and RACE may move modestly because they have broader question variety
  and option/synthesis pressure.
- MAUD should be treated as the likely high-variance contract boundary because
  its first draw was already low and clause-role semantics are dense.

Intervention:

- Ran a second fresh external compile-plus-QA draw under tag
  `instrument-freeze-20260515-r1`.
- Kept helpers genuinely off with `--helper-companion-row-limit 0`, `--no-cache`,
  and no legacy native helper adapter flag.
- Used OpenRouter for PrivacyQA, SQuAD, and RACE at six hosted lanes total; used
  POWER/local for MAUD and CUAD.
- Made no prompt, code, helper, or repair changes during the draw.

After:

| Corpus | Draw 1 | Draw 2 | Mean | Range | Helper rows |
| --- | ---: | ---: | ---: | ---: | ---: |
| `PrivacyQA-30` | 90.00% (`27/30`) | 90.00% (`27/30`) | 90.00% | 0.00 pts | `0 / 0` |
| `MAUD-10` | 42.50% (`17/40`) | 35.00% (`14/40`) | 38.75% | 7.50 pts | `0 / 0` |
| `SQuAD-30` | 96.49% (`165/171`) | 94.15% (`161/171`) | 95.32% | 2.34 pts | `0 / 0` |
| `CUAD-10` | 75.00% (`30/40`) | 75.00% (`30/40`) | 75.00% | 0.00 pts | `0 / 0` |
| `RACE-50-options` | 85.31% (`151/177`) | 84.18% (`149/177`) | 84.75% | 1.13 pts | `0 / 0` |

Aggregate:

| Draw | Questions | Exact | Partial | Miss | Exact rate | Helper rows |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `draw1` | 458 | 390 | 10 | 58 | 85.15% | 0 |
| `draw2` | 458 | 381 | 13 | 64 | 83.19% | 0 |
| **N=2 pooled** | **916** | **771** | **23** | **122** | **84.17%** | **0** |

Artifacts:

- `docs\data\instrument_stamp\nohelper_external_n2_variance_rollup_20260515.json`
- `docs\data\instrument_stamp\nohelper_external_n2_variance_rollup_20260515.md`
- `tmp\instrument_stamp_20260515_fresh_privacyqa30_draw2_compile_or`
- `tmp\instrument_stamp_20260515_fresh_privacyqa30_draw2_qa_or`
- `tmp\instrument_stamp_20260515_fresh_maud10_draw2_compile_power`
- `tmp\instrument_stamp_20260515_fresh_maud10_draw2_qa_power`
- `tmp\instrument_stamp_20260515_fresh_squad30_draw2_compile_or`
- `tmp\instrument_stamp_20260515_fresh_squad30_draw2_qa_or`
- `tmp\instrument_stamp_20260515_fresh_cuad10_draw2_compile_power`
- `tmp\instrument_stamp_20260515_fresh_cuad10_draw2_qa_power`
- `tmp\instrument_stamp_20260515_fresh_race50_draw2_compile_or`
- `tmp\instrument_stamp_20260515_fresh_race50_draw2_qa_or`

Verification:

- All five draw-two QA summaries completed their expected question counts.
- Every draw-two QA summary reported helper rows `0`, runtime load errors `0`,
  and write proposal rows `0`.
- Draw-two worker processes had exited before the rollup was written.

Lesson:

- The external no-helper result is not a single lucky draw: pooled N=2 exact is
  `84.17%` across `916` questions with helper rows still exactly `0`.
- PrivacyQA and CUAD repeated exactly, so their current boundaries look stable
  under this two-draw sample.
- SQuAD and RACE remain high with modest spread; RACE's MCQ option surface does
  not appear to require helper restoration.
- MAUD is the clear high-variance, low-score legal-transfer boundary. That is a
  stamp finding, not a reason to repair during the freeze.

Next pressure:

- If the stamp needs publication-grade variance bands immediately, run N=3 next,
  with special attention to MAUD because it is the only corpus whose two-draw
  spread is large enough to alter the qualitative interpretation.
- If compute time is the constraint, defer universal N=3 and treat the current
  N=2 rollup as the external no-helper baseline while resuming post-freeze
  architecture work on helper-free native compile-surface invariants.
