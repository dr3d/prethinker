# Helper Residue Audit Worksheet

Last updated: 2026-05-14

This worksheet tracks the helper-delivery cleanup lane after the first
instrument stamp. It is separate from guard compression and boundary hunting:
the question here is how many query-time helper companion rows must be delivered
to the answer/judge context once the compiled KB already exists.

Operating rule:

- Do not delete or weaken compiled facts to make helper volume look smaller.
- Do not encode fixture nouns, question IDs, answer strings, local people,
  local organizations, or row IDs into helper ranking.
- Treat helper rows as query-time delivery budget. If a helper is needed, keep
  the most question-relevant rows; if a forensic run is needed, use the
  unbounded mode.

CLI modes:

- Default: `--helper-companion-row-limit 3`
- Zero-helper ablation: `--helper-companion-row-limit 0`
- Unbounded forensic delivery: `--helper-companion-row-limit -1`

## HR-001 - Native Helper Pressure Anatomy

Date: 2026-05-14

Before:

- Native story-world stamp, draw 1: `56` fixtures, `2163` questions.
- QA result: `1824 / 92 / 247`, exact `84.33%`.
- Helper rows: `7281`, rows/exact `3.992`, candidate-helper share `0.1834`.
- Largest helper sources:
  - `roster_state_support`: `2502`
  - `source_record_packet_metadata_support`: `1838`
  - `industrial_sensor_support`: `1260`
  - `clinic_recall_support`: `580`
  - `grant_award_support`: `408`

Prediction:

- The residue is mostly delivery/scope pressure, not missing facts. External
  transfer corpora reached strong QA scores with near-zero helper rows, so the
  native corpus likely over-delivers historical helper surfaces.

Intervention:

- Isolate the five highest-pressure native fixtures:
  - `count_composition_roster`
  - `industrial_sensor_clock_correction`
  - `probate_storage_access_register`
  - `clinic_device_recall_field_packet`
  - `grant_exception_cap_matrix`

After:

| Slice | Questions | Exact | Partial | Miss | Helper rows | Exact rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Baseline top 5 | 200 | 170 | 4 | 26 | 5866 | 85.0% |

Artifacts:

- `tmp\instrument_stamp_20260514_story_worlds_draw1_qa\qa_batch_summary.json`

Verification:

- Baseline top-five numbers were derived from the locked native stamp artifact,
  not from a fresh repair run.

Lesson:

- The native helper problem is concentrated. Five fixtures account for most of
  the visible helper bulk, so the first cleanup target can be narrow without
  being parochial.

Next pressure:

- Run zero-helper and bounded-helper ablations on the same five fixtures.

## HR-002 - Zero-Helper Ablation

Date: 2026-05-14

Before:

- Baseline top five: `170 / 4 / 26`, `5866` helper rows.

Prediction:

- If helpers are pure residue, zero-helper delivery should preserve most of the
  exact rate. If some helpers still carry useful query-time structure, exactness
  should fall in specific fixtures.

Intervention:

- Ran the five pressure fixtures with `--helper-companion-row-limit 0`.

After:

| Slice | Questions | Exact | Partial | Miss | Helper rows | Exact rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Zero-helper top 5 | 199 | 149 | 7 | 43 | 0 | 74.87% |

Per-fixture shape:

| Fixture | Exact | Partial | Miss | Helper rows |
| --- | ---: | ---: | ---: | ---: |
| `count_composition_roster` | 28 | 2 | 10 | 0 |
| `industrial_sensor_clock_correction` | 32 | 3 | 5 | 0 |
| `probate_storage_access_register` | 33 | 0 | 6 | 0 |
| `clinic_device_recall_field_packet` | 34 | 1 | 5 | 0 |
| `grant_exception_cap_matrix` | 22 | 1 | 17 | 0 |

Artifacts:

- `tmp\helper_residue_ablation_20260514_top5_limit0_qa`

Verification:

- The drop is concentrated in fixtures whose helper rows expose useful count,
  addressability, or procedural support. One fixture improved, confirming that
  not all helper rows are beneficial.

Lesson:

- The target is not "delete all helpers." The target is "stop delivering large
  unrelated helper surfaces." Some query-time companions still buy performance.

Next pressure:

- Test a small helper delivery budget rather than an all-or-nothing deletion.

## HR-003 - Crude Cap Shows The Budget Shape And Its Failure Mode

Date: 2026-05-14

Before:

- Zero-helper confirmed some helper rows are useful.
- The first bounded delivery implementation kept the first `N` helper rows per
  question after dedupe.

Prediction:

- A question-level cap of `3` should delete most helper bulk. If the first rows
  are not always the relevant rows, cap regressions should expose row-order
  leakage rather than fixture-specific failure.

Intervention:

- Ran five pressure fixtures with a crude `--helper-companion-row-limit 3`.
- Audited exact-to-miss regressions by comparing helper rows delivered in
  baseline versus cap.

After:

| Slice | Questions | Exact | Partial | Miss | Helper rows | Exact rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Crude cap-3 top 5 | 200 | 161 | 6 | 33 | 382 | 80.50% |

Observed failure shape:

- The cap deleted about `93.5%` of top-five helper rows.
- Several regressions were caused by preserving early but irrelevant support
  rows while dropping later rows with the asked measure, status, or procedure.

Artifacts:

- `tmp\helper_residue_ablation_20260514_top5_limit3_qa`
- `tmp\helper_residue_ablation_20260514_top3_limit3_or_qa`

Verification:

- Targeted regression audit found row-order failures, not a need for
  fixture-specific routing. Example shape: a procedural-duration question lost
  the procedural-duration helper because earlier count helpers consumed the
  budget.

Lesson:

- A helper budget must be a relevance budget, not a list-order budget. The
  general principle is transferable: rank helper companion rows by overlap with
  the current question/query surfaces before delivery.

Next pressure:

- Replace first-N delivery with a fixture-free query-relevance budget.

## HR-004 - Query-Relevance Helper Budget

Date: 2026-05-14

Before:

- Crude cap-3 proved a large deletion is possible but exposed row-order
  regressions.

Prediction:

- Ranking helper rows by generic lexical overlap with the question, generated
  queries, support kind, predicate, and row values should keep asked-for support
  without teaching the harness fixture vocabulary.

Intervention:

- Added `_limit_helper_query_results(...)` as a query-time helper delivery
  filter.
- Defaulted QA and batch QA to `--helper-companion-row-limit 3`.
- Added `--helper-companion-row-limit -1` for unbounded forensic delivery.
- Added unit tests covering relevance ranking and zero-helper suppression.

After:

| Slice | Questions | Exact | Partial | Miss | Helper rows | Exact rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Ranked cap-3 top 5 | 200 | 167 | 8 | 25 | 405 | 83.50% |

Compared with baseline:

| Slice | Exact | Partial | Miss | Helper rows |
| --- | ---: | ---: | ---: | ---: |
| Baseline top 5 | 170 | 4 | 26 | 5866 |
| Ranked cap-3 top 5 | 167 | 8 | 25 | 405 |

Targeted regression replay:

- Three previously damaged grant questions under crude cap replayed at `3 / 0 /
  0` with only `9` helper rows after the ranked budget landed.

Artifacts:

- `scripts\run_domain_bootstrap_qa.py`
- `scripts\run_domain_bootstrap_qa_batch.py`
- `tests\test_domain_bootstrap_qa.py`
- `tmp\helper_residue_ablation_20260514_top5_limit3_ranked_or_qa`
- `tmp\helper_residue_ablation_20260514_grant_limit3_ranked_or_qa`

Verification:

- `python -m py_compile scripts\run_domain_bootstrap_qa.py scripts\run_domain_bootstrap_qa_batch.py`
- `python -m pytest tests\test_domain_bootstrap_qa.py::test_helper_companion_row_limit_prefers_question_relevant_support_rows tests\test_domain_bootstrap_qa.py::test_helper_companion_row_limit_zero_suppresses_helper_results_only tests\test_domain_bootstrap_qa.py::test_run_query_plan_dedupes_repeated_helper_companion_rows tests\test_domain_bootstrap_qa_batch.py -q`
- OpenRouter ranked cap-3 top-five replay completed with `0` runtime errors
  and `0` write proposals.

Lesson:

- This is a delivery repair, not a fixture repair. The compiled KB and helper
  generators remain available, but ordinary QA now sees a small ranked
  companion budget. The instrument can still run unbounded when auditing helper
  substrate.
- The first large helper deletion is defensible: top-five helper rows dropped
  from `5866` to `405` (`93.1%` reduction) while exact answers stayed within
  the same practical band and misses did not increase.

Next pressure:

- Run a full native-corpus capped replay when runtime budget allows. The likely
  target is not zero helpers; it is low single-digit helper rows per question
  without losing the useful support rows.
- Audit the remaining high helper sources under the ranked budget before
  changing helper generators themselves.
