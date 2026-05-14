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
