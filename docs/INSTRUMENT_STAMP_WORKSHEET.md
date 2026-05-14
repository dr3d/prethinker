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
| PrivacyQA-30 | `tmp\mrc_transfer_staged_privacyqa30_20260513` | 30 | 30 | Pending |
| MAUD-10 | `tmp\mrc_transfer_staged_maud10_20260513` | 10 | 40 | Pending |
| CUAD-10 | `tmp\mrc_transfer_staged_cuad10_20260513` | 10 | 40 | Pending; treat as rough corpus evidence |

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
