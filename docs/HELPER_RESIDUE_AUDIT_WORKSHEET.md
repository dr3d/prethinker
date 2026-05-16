# Helper Residue Audit Worksheet

Last updated: 2026-05-16

This worksheet tracks the helper-delivery cleanup lane after the first
instrument stamp. It is separate from guard compression and boundary hunting:
the question here is how many query-time helper companion rows must be delivered
to the answer/judge context once the compiled KB already exists.

Operating rule:

- Do not delete or weaken compiled facts to make helper volume look smaller.
- Do not encode fixture nouns, question IDs, answer strings, local people,
  local organizations, or row IDs into helper ranking.
- Treat helper rows as retired query-time compatibility surfaces. The current
  instrument default is no helper companion delivery; positive budgets are
  forensic opt-ins for old-run diagnosis.

CLI modes:

- Default/current instrument: `--helper-companion-row-limit 0`
- Bounded forensic delivery: `--helper-companion-row-limit N` for positive `N`
- Unbounded forensic delivery: `--helper-companion-row-limit -1`

When the limit is `0`, helper companion assembly is skipped upstream. This is
not merely a post-query row filter.

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
- At that stage, defaulted QA and batch QA to
  `--helper-companion-row-limit 3`.
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

## HR-005 - Full Native Ranked-Cap Replay

Date: 2026-05-14

Before:

- Native unbounded stamp: `2163` questions, `1824 / 92 / 247`, exact `84.33%`.
- Helper rows: `7281`, rows/exact `3.992`, rows/question `3.366`.
- The top-five pressure replay showed ranked cap-3 could delete about `93%` of
  helper rows in the worst fixtures without a miss increase.

Prediction:

- A full native replay under the ranked budget should reduce helper delivery by
  an order-of-magnitude-ish amount. Some exact-rate movement is expected because
  the QA judge and hosted provider draw are stochastic, but a large collapse
  would mean the budget is too aggressive.

Intervention:

- Ran all `56` native fixtures from the frozen draw-1 compile artifacts with:
  - `--helper-companion-row-limit 3`
  - OpenRouter `qwen/qwen3.6-35b-a3b`
  - `6` hosted lanes
  - fresh QA calls (`--no-cache`)

After:

| Slice | Fixtures | Questions | Exact | Partial | Miss | Exact rate | Helper rows | Rows/exact | Rows/question |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Unbounded native stamp | 56 | 2163 | 1824 | 92 | 247 | 84.33% | 7281 | 3.992 | 3.366 |
| Ranked cap-3 native replay | 56 | 2163 | 1804 | 99 | 260 | 83.40% | 976 | 0.541 | 0.451 |

Delta:

- Helper rows: `7281 -> 976`, a reduction of `6305` rows (`86.6%`).
- Exact answers: `1824 -> 1804`, down `20` exact rows (`-0.93` percentage
  points).
- Partial answers: `92 -> 99`, up `7`.
- Misses: `247 -> 260`, up `13`.
- Runtime load errors: `0`.
- Write proposal rows: `0`.

Remaining helper sources:

| Helper source | Rows |
| --- | ---: |
| `source_record_packet_metadata_support` | 374 |
| `grant_award_support` | 100 |
| `industrial_sensor_support` | 85 |
| `archive_authority_custody_support` | 77 |
| `source_record_table_body_count_support` | 66 |
| `roster_state_support` | 65 |
| `clinic_recall_support` | 61 |
| `lifecycle_period_support` | 33 |
| `story_choice_contrast_support` | 28 |
| `status_timeline_summary_support` | 25 |

Heaviest remaining fixture surfaces:

| Fixture | Helper rows | Exact | Partial | Miss |
| --- | ---: | ---: | ---: | ---: |
| `greenhouse_quarantine` | 101 | 32 | 2 | 6 |
| `industrial_sensor_clock_correction` | 98 | 35 | 2 | 3 |
| `grant_exception_cap_matrix` | 94 | 32 | 1 | 7 |
| `authority_possession_custody_packet` | 89 | 30 | 3 | 7 |
| `probate_storage_access_register` | 88 | 34 | 2 | 4 |
| `count_composition_roster` | 76 | 33 | 1 | 6 |
| `rule_activation_exception_matrix` | 75 | 37 | 1 | 2 |
| `clinic_device_recall_field_packet` | 63 | 34 | 0 | 6 |
| `school_activity_roster_reconciliation` | 52 | 31 | 2 | 7 |

Artifacts:

- `tmp\helper_residue_full_native_cap3_ranked_or_qa`
- `tmp\helper_residue_full_native_cap3_ranked_or_qa\qa_batch_summary.json`
- `tmp\helper_residue_full_native_cap3_ranked_or_qa\qa_batch_summary.md`

Verification:

- Completed `56 / 56` fixtures and `2163 / 2163` questions.
- No active Python worker remained after completion.
- Batch summary reports `0` runtime load errors and `0` write proposal rows.

Lesson:

- The feared `7281` helper rows were mostly query-time delivery residue. The
  ranked budget removes `6305` delivered helper rows without deleting compiled
  facts or helper generators.
- The remaining `976` rows are now a tractable audit surface. They are not
  random: they concentrate in `source_record_packet_metadata_support` and a
  handful of historically helper-heavy fixtures.
- The next deletion should not lower the global row cap blindly. It should
  attack the remaining source-specific delivery shapes, especially packet
  metadata, by asking whether repeated rows can be summarized, scoped, or routed
  only when the question actually asks for source/addressability evidence.

Next pressure:

- Audit `source_record_packet_metadata_support` under the ranked budget. It is
  still `374 / 976` rows, so one helper source now accounts for `38.3%` of the
  remaining delivery surface.
- Compare exact-to-miss deltas between unbounded and ranked-cap native replays
  before tightening below cap `3`.

## HR-006 - Remaining Packet Metadata Shape

Date: 2026-05-14

Before:

- Full native ranked-cap replay left `976` helper rows.
- `source_record_packet_metadata_support` was the largest remaining source at
  `374` rows.

Prediction:

- If packet metadata still hides a broad flood, it should appear as many rows
  per question or many unrelated support kinds. If the global budget is already
  doing its job, it should appear as a small number of repeated source-support
  rows across source/addressability questions.

Intervention:

- Audited `source_record_packet_metadata_support` rows in
  `tmp\helper_residue_full_native_cap3_ranked_or_qa` by fixture, support kind,
  delivered rows, unique rows, and per-question row count.

After:

- Delivered packet metadata rows: `374`.
- Unique packet metadata rows: `137`.
- Questions receiving packet metadata: `158`.
- Average rows per packet-metadata question: `2.37`.

Per-question packet row count:

| Rows delivered | Questions |
| ---: | ---: |
| 1 | 37 |
| 2 | 26 |
| 3 | 95 |

Largest support kinds:

| Support kind | Rows |
| --- | ---: |
| `source_record_matching_token_source` | 51 |
| `source_record_custody_location` | 40 |
| `source_record_temporal_relation_note` | 31 |
| `source_record_temporal_event_note` | 29 |
| `source_record_sample_result_note` | 23 |
| `source_record_order_section` | 23 |
| `unreproduced_reference` | 22 |
| `source_record_item_event_identifier_note` | 21 |
| `source_record_statement_filing_note` | 16 |
| `motion_status` | 14 |

Fixture concentration:

| Fixture | Packet rows | Dominant support shape |
| --- | ---: | --- |
| `greenhouse_quarantine` | 83 | temporal and sample-result source notes |
| `probate_storage_access_register` | 88 | custody/location, motion status, assertion standing |
| `rule_activation_exception_matrix` | 42 | matching-token source |
| `hospital_shift_exception_log` | 38 | statement filing and timestamp authority |
| `school_activity_roster_reconciliation` | 31 | accommodation/policy identifiers |
| `grant_exception_cap_matrix` | 26 | unreproduced references and memo identifiers |

Verification:

- The global cap is active: packet metadata appears at no more than three rows
  per question.
- The remaining rows concentrate in source-addressability, temporal note,
  custody/location, and order/status support. That is a real source-fidelity
  surface, not an unbounded helper dump.

Lesson:

- The next packet-metadata reduction is not a global cap problem. The cap has
  already made delivery small per question.
- Further reduction should be source-specific: summarize repeated
  source-addressability support only when it is semantically equivalent, and do
  not collapse temporal/custody/order distinctions that are answer-bearing.

Next pressure:

- Do not lower cap `3` globally yet. First inspect exact-to-miss examples where
  the ranked cap lost a previously exact answer, and separate true helper-loss
  failures from ordinary hosted/judge variance.

## HR-007 - Unlike Helper Transfer Probe

Date: 2026-05-14

Before:

- External transfer corpora used `0-3` helper rows per draw, while the native
  ranked-cap replay still used `976`.
- The unresolved question was whether native helpers are domain-correct
  structural helpers or fixture/palette-shaped recognizers.

Prediction:

- If helpers are domain-correct, novel documents with the same structural
  families should trigger the same helper families:
  - a non-school roster should trigger roster support,
  - a non-probate custody register should trigger custody support,
  - a non-factory sensor sheet should trigger sensor support.
- If helpers are fixture/palette-shaped, the novel documents should compile and
  answer through new direct predicates while the old helper families stay
  silent.

Intervention:

- Built three unlike probe fixtures under
  `tmp\helper_transfer_probe_20260514`:
  - `novel_club_roster`: volunteer squad rotation with changes and supervisors.
  - `novel_specimen_custody`: botanical specimen custody/access register.
  - `novel_freezer_sensor`: freezer sensor clock correction and threshold
    breach sheet.
- Compiled them with source-record ledger facts and the same current compiler
  machinery.
- Ran QA with unbounded helper delivery
  (`--helper-companion-row-limit -1`) so any helper trigger would be visible.

After:

| Probe | Questions | Exact | Partial | Miss | Helper rows |
| --- | ---: | ---: | ---: | ---: | ---: |
| `novel_club_roster` | 8 | 8 | 0 | 0 | 0 |
| `novel_specimen_custody` | 8 | 8 | 0 | 0 | 0 |
| `novel_freezer_sensor` | 8 | 8 | 0 | 0 | 0 |

Compiled predicate surfaces:

- Roster probe emitted direct predicates such as `volunteer_in_squad`,
  `roster_change_event`, `change_detail`, `supervisor_assignment`,
  `squad_minimum_size`.
- Custody probe emitted direct predicates such as `physical_holder`,
  `legal_owner`, `custody_status`, `access_event`, `authorized_by`,
  `recall_issued`.
- Sensor probe emitted direct predicates such as `sensor_clock_drift`,
  `correction_rule`, `event_corrected_timestamp`, `event_reading`,
  `event_status`, `breach_threshold`.

Helper trigger readout:

- `roster_state_support` did not fire because its trigger/row vocabulary expects
  older palette names such as `student_group_assignment`, `group_member`,
  `adult_role`, `supervision_assignment`, or related roster-table rows. The
  novel compile used `volunteer_in_squad` and `supervisor_assignment`.
- `archive_authority_custody_support` did not fire because its trigger/row
  vocabulary expects names such as `physical_custodian`,
  `physical_custody`, `access_log_entry`, or `access_authorized_by`. The novel
  compile used `physical_holder`, `legal_owner`, `access_event`, and
  `authorized_by`.
- `industrial_sensor_support` did not fire on the novel sensor sheet despite
  source-record predicates being queried. Its body contains an explicit
  fixture-era token gate for old sensor/event atoms before it will produce
  support rows.

Artifacts:

- `tmp\helper_transfer_probe_20260514`
- `tmp\helper_transfer_probe_compile_20260514`
- `tmp\helper_transfer_probe_qa_unbounded_20260514`

Verification:

- Compile completed for all `3 / 3` probes.
- QA completed `24 / 24` questions with `24 / 0 / 0`.
- Unbounded helper delivery reported `0` helper rows, so the absence of helper
  rows is not caused by the cap.

Lesson:

- The asymmetry is real. These helper families are not general domain
  recognizers over arbitrary roster/custody/sensor documents. They are largely
  adapters for older native palette names and, in at least one case, explicit
  fixture-era token gates.
- The better architecture is not to make these helpers fire everywhere. The
  better architecture is to preserve the direct compiled surfaces that already
  answered the novel probes, then retire or quarantine native helper adapters as
  legacy scaffolding once equivalent direct predicates exist.
- The native corpus is harder partly because it carries old palette history. The
  external/unlike probes show that new material can compile into cleaner direct
  predicates and avoid helper delivery entirely.

Next pressure:

- Treat remaining native helper rows as legacy adapter debt unless a helper
  proves transfer on unlike documents without trigger-name or token-shape
  leakage.
- For each high-volume helper, either:
  - replace it with direct compile-surface guidance that emits answer-bearing
    predicates, or
  - keep it quarantined as a forensic/native compatibility adapter, not as
    current architecture.

## HR-008 - Quarantine Legacy Native Helper Adapters

Date: 2026-05-14

Before:

- The unlike helper transfer probe showed that modern compiles can answer
  roster, custody, and sensor structures through direct predicates with `0`
  helper rows.
- The native corpus still delivered high-volume helper rows because old helper
  families bridged from older palette names and fixture-era source shapes.
- The risk was architectural confusion: helper delivery could look like current
  substrate when it was really legacy compatibility scaffolding.

Prediction:

- If the native helper families are mostly legacy adapters, they can be disabled
  by default without changing the generic helper substrate.
- A useful quarantine must cover every query execution path, including evidence
  bundle repairs, not only the primary query list.
- Compile guidance should move in the opposite direction: make direct predicates
  more explicit so new compiles do not need query-time helper bridges.

Intervention:

- Added an opt-in CLI flag:
  `--include-legacy-native-helper-adapters`.
- Default QA and batch QA now run with legacy native adapters disabled.
- Marked opt-in legacy adapter results with
  `adapter_status=legacy_native_compatibility_adapter`,
  `default_delivery=disabled`, and a replacement direction that prefers direct
  compile surfaces.
- Quarantined the old native adapter families behind that opt-in gate:
  roster/table counts, school-style alias rows, packet metadata, grant/sensor
  adapters, clinic recall support, clock-sync support, custody support, clear
  sample clock pause support, and roster-state support.
- Strengthened compile guidance for:
  - roster-like documents: direct membership, assignment, supervisor,
    version/status, change-event, count, and minimum/ratio-rule rows,
  - custody/access/control registers: physical holder, legal owner, custody
    status, location, access event, authorizing source, recall/return clause,
    and recall-issued state,
  - sensor/clock/threshold sheets: sensor id, raw timestamp, corrected
    timestamp, correction rule, reading value, threshold, event status,
    inspection window, and breach classification.

After:

- A first no-legacy top-five smoke exposed a leak: evidence-bundle query repair
  still called `run_query_plan()` through its default legacy-compatible path and
  delivered old helper rows.
- Fixed the propagation so `include_legacy_native_helpers=False` flows through:
  - primary QA query execution,
  - evidence-bundle plan execution,
  - source-text containment repair.
- A second smoke with unbounded helper delivery and evidence bundles on produced
  `0` helper rows across `24` high-pressure native smoke questions:

| Fixture | Questions | Exact | Partial | Miss | Helper rows |
| --- | ---: | ---: | ---: | ---: | ---: |
| `count_composition_roster` | 8 | 7 | 1 | 0 | 0 |
| `industrial_sensor_clock_correction` | 8 | 6 | 0 | 2 | 0 |
| `probate_storage_access_register` | 8 | 8 | 0 | 0 | 0 |
| Total | 24 | 21 | 1 | 2 | 0 |

Artifacts:

- `tmp\helper_legacy_disabled_top5_unbounded_or_20260514`
  - failed gate smoke; retained as evidence that evidence-bundle repair was a
    helper leak path.
- `tmp\helper_legacy_disabled_smoke_unbounded_or_20260514`
  - fixed gate smoke; `0` helper rows with legacy adapters disabled and helper
    delivery unbounded.

Verification:

- `python -m py_compile scripts\run_domain_bootstrap_qa.py scripts\run_domain_bootstrap_qa_batch.py scripts\run_domain_bootstrap_file.py`
- `python -m pytest tests\test_domain_bootstrap_qa.py tests\test_domain_bootstrap_qa_batch.py -q`
- Result: `165 passed`.
- Added regression coverage for:
  - default batch commands not including the legacy adapter flag,
  - explicit opt-in preserving the legacy flag,
  - direct `run_query_plan(... include_legacy_native_helpers=False)` suppressing
    legacy helpers,
  - the subtle case where a generic companion fires first and must not reopen
    `roster_state_support`.

Lesson:

- Quarantine is not just a CLI option. It is a whole execution-path invariant.
  Helper adapters must stay disabled through primary queries, repaired evidence
  queries, and secondary filter probes.
- Generic helper names are not enough. Any helper whose trigger depends on old
  native palette names or fixture-era tokens belongs behind the compatibility
  gate until it proves unlike transfer.
- The replacement direction is compile-side, not helper-side: emit the
  answer-bearing surfaces directly, then let query-time helpers shrink toward
  true generic substrate.

Next pressure:

- Recompile a small native slice under the strengthened direct-surface guidance
  and compare old-vs-new predicate palettes before spending hours on a full
  native no-legacy replay.
- Keep legacy adapters available for forensic replay, but treat any request to
  turn them on as a compatibility decision rather than current architecture.

## HR-009 - Direct-Surface Recompile Smoke

Date: 2026-05-14

Before:

- HR-008 proved the legacy gate can reduce helper delivery to `0` on a
  high-pressure native smoke using the frozen stamp compile.
- That test did not prove that fresh native compiles would now emit all helper
  replacement surfaces. It only proved the helper adapter gate was closed.

Prediction:

- If the direct-surface guidance is sufficient, a fresh compile of the roster,
  custody, and sensor pressure fixtures should preserve or improve QA while
  still delivering `0` helper rows.
- If the guidance is directionally right but incomplete, helper rows should stay
  at `0` while misses shift into compile/query surface gaps that name the next
  compile-side surfaces to preserve.

Intervention:

- Recompiled three high-pressure native fixtures under the strengthened
  direct-surface guidance:
  - `count_composition_roster`,
  - `industrial_sensor_clock_correction`,
  - `probate_storage_access_register`.
- Ran the same `8`-question no-legacy, unbounded-helper QA smoke against the
  fresh compile artifacts.

After:

Compile summary:

| Fixture | Predicates | Admitted | Skipped | Rough |
| --- | ---: | ---: | ---: | ---: |
| `count_composition_roster` | 16 | 28 | 0 | 0.833 |
| `industrial_sensor_clock_correction` | 21 | 0 | 0 | 1.0 |
| `probate_storage_access_register` | 14 | 16 | 0 | 0.778 |

QA summary:

| Fixture | Questions | Exact | Partial | Miss | Helper rows |
| --- | ---: | ---: | ---: | ---: | ---: |
| `count_composition_roster` | 8 | 8 | 0 | 0 | 0 |
| `industrial_sensor_clock_correction` | 8 | 5 | 0 | 3 | 0 |
| `probate_storage_access_register` | 8 | 6 | 0 | 2 | 0 |
| Total | 24 | 19 | 0 | 5 | 0 |

Compared with the frozen-compile no-legacy smoke:

| Compile | Exact | Partial | Miss | Helper rows |
| --- | ---: | ---: | ---: | ---: |
| Frozen stamp compile | 21 | 1 | 2 | 0 |
| Fresh direct-surface compile | 19 | 0 | 5 | 0 |

Miss shape:

- Roster improved from `7 / 1 / 0` to `8 / 0 / 0`; direct roster surfaces are
  moving in the right direction.
- Sensor lost answers for vendor/model, section addressability, and operator
  attendance. That is not helper pressure; it is source-fidelity/surface
  retention pressure.
- Custody lost answers for registrar identity and chronology-section
  addressability. Again, the gap moved to compile surface breadth, not helper
  delivery.

Artifacts:

- `tmp\helper_direct_surface_recompile_20260514`
- `tmp\helper_direct_surface_recompile_qa_smoke_20260514`

Verification:

- Recompile completed for all `3 / 3` fixtures.
- QA completed `24 / 24` questions.
- Helper pressure stayed at `no_helper_rows` with `0` rows while helper delivery
  was unbounded.

Lesson:

- The helper-quarantine direction is correct: the system can run these native
  pressure questions with no helper rows at all.
- The next risk is not helper absence. It is compile sparsity. Fresh direct
  compiles must preserve source-fidelity surfaces such as vendor/model identity,
  operator/attendee roles, registrar identity, and section/chronology
  addressability while still avoiding old helper adapters.
- Roster is the first high-pressure native family to show the desired shape:
  direct compile surfaces plus no helper rows plus improved QA.

Next pressure:

- Strengthen compile guidance for source-addressability and role/identity
  fidelity in operational and custody registers:
  - preserve vendor/model/manufacturer and procedure identifiers,
  - preserve attended-by/operator-at-console/observer role rows,
  - preserve registrar/compiler/custodian identity rows,
  - preserve named section titles and chronology/location sections as queryable
    source coordinates.
- Then rerun the same three-fixture direct-surface smoke before considering a
  broader no-legacy native replay.

## HR-010 - Source-Fidelity Guidance Smoke

Date: 2026-05-14

Before:

- HR-009 showed that zero-helper direct compiles were possible but could become
  too sparse.
- The losses were source-fidelity/addressability losses: vendor/model identity,
  operator/attendant roles, registrar identity, and named section coordinates.

Prediction:

- Strengthening source-fidelity guidance should improve sensor and custody
  misses without reintroducing helper rows.
- If the compile remains stochastic, a small improvement in one family may be
  offset by sparsity in another; that would argue for repeated compile draws or
  stronger invariant checks before a broad replay.

Intervention:

- Added generic source-fidelity guidance:
  - operational records must preserve vendor, manufacturer, model number,
    procedure/manual identifiers, operators, console attendants, observers,
    reviewers, and named section/title coordinates,
  - custody/property registers must preserve registrar, compiler, recorder,
    custodian, counsel, claimant, object/register identifiers, named chronology
    sections, location sections, and other section/title coordinates.
- Recompiled the same three-fixture native smoke slice.
- Reran the same no-legacy, unbounded-helper QA smoke.

After:

Compile summary:

| Fixture | Predicates | Admitted | Skipped | Rough |
| --- | ---: | ---: | ---: | ---: |
| `count_composition_roster` | 14 | 42 | 0 | 1.0 |
| `industrial_sensor_clock_correction` | 15 | 52 | 2 | 1.0 |
| `probate_storage_access_register` | 26 | 0 | 0 | 0.778 |

QA summary:

| Fixture | Questions | Exact | Partial | Miss | Helper rows |
| --- | ---: | ---: | ---: | ---: | ---: |
| `count_composition_roster` | 8 | 5 | 1 | 2 | 0 |
| `industrial_sensor_clock_correction` | 8 | 7 | 0 | 1 | 0 |
| `probate_storage_access_register` | 8 | 7 | 1 | 0 | 0 |
| Total | 24 | 19 | 2 | 3 | 0 |

Compared with HR-009:

| Compile | Exact | Partial | Miss | Helper rows |
| --- | ---: | ---: | ---: | ---: |
| HR-009 direct-surface recompile | 19 | 0 | 5 | 0 |
| HR-010 source-fidelity recompile | 19 | 2 | 3 | 0 |

Observed movement:

- Sensor improved from `5 / 0 / 3` to `7 / 0 / 1`. Vendor/model and
  operator-attendance gaps were repaired; one section-addressability miss
  remained.
- Custody improved from `6 / 0 / 2` to `7 / 1 / 0`. Registrar/chronology
  losses became recoverable or partially recoverable; one section-basis answer
  remained partial.
- Roster regressed from `8 / 0 / 0` to `5 / 1 / 2`. The misses were registered
  nurse identity, policy-section identity, and the exact ratio expression. This
  looks like compile sparsity/variance, not helper pressure.

Artifacts:

- `tmp\helper_source_fidelity_recompile_20260514`
- `tmp\helper_source_fidelity_recompile_qa_smoke_20260514`

Verification:

- Recompile completed for all `3 / 3` fixtures.
- QA completed `24 / 24` questions.
- Helper rows stayed at `0` with helper delivery unbounded.

Lesson:

- The no-helper objective is holding. The remaining work is not to revive
  native helpers; it is to make compile surfaces reliably broad enough.
- Source-fidelity guidance helped the classes it named, especially sensor and
  custody identity/addressability.
- Single compile draws are too noisy to declare a locked replacement. The next
  repair should be framed as compile-surface invariants, not more prose
  nudges: the compiler should preserve role identity, policy/rule identifiers,
  and named section coordinates whenever those are stated.

Next pressure:

- Add a lightweight compile-surface audit for no-helper native replay candidates:
  expected identity/addressability surfaces should be visible before QA is used
  as the only signal.
- Keep full native replay paused until the three-fixture smoke can repeatedly
  stay near or above the frozen no-legacy baseline without helper rows.

## HR-011 - Retire Helper Companion Delivery By Default

Date: 2026-05-16

Before:

- The original native stamp exposed `7281` delivered helper rows. The ranked
  cap reduced that to `976`, but that still left a large context surface that
  external transfer corpora did not need.
- The external N=3 stamp ran with helpers genuinely off and held at
  `1157 / 33 / 184` across `1374` questions, exact `84.21%`, helper rows `0`.
- Unlike helper probes showed that modern documents with roster, custody, and
  sensor structures answered through direct compiled predicates rather than old
  native helper triggers.

Prediction:

- The current instrument should default to zero helper companion delivery.
- If a run requests `--helper-companion-row-limit 0`, the harness should skip
  helper companion assembly entirely, not assemble helper rows and filter them
  away after spending query/context budget.
- Positive helper budgets should remain available only for forensic replay of
  old native compatibility behavior.

Intervention:

- Changed QA and batch QA defaults to `--helper-companion-row-limit 0`.
- Added a root `helper_companions_enabled` gate that disables helper companion
  assembly in:
  - primary query execution,
  - evidence-bundle plan execution,
  - source-text containment repair.
- Left direct KB queries, query repairs, relaxed fallback, and temporal/status
  joins available. The retirement target is helper companion delivery, not the
  core query machinery.
- Kept positive limits and `-1` as explicit forensic modes for compatibility
  audits.

After:

- Default batch commands now emit `--helper-companion-row-limit 0`.
- `run_query_plan(..., helper_companions_enabled=False)` preserves direct query
  results while proving generic helper companion functions are not called.
- Legacy native helper adapters remain opt-in behind
  `--include-legacy-native-helper-adapters`; helper companion delivery itself is
  now also off by default.

Artifacts:

- `scripts/run_domain_bootstrap_qa.py`
- `scripts/run_domain_bootstrap_qa_batch.py`
- `tests/test_domain_bootstrap_qa.py`
- `tests/test_domain_bootstrap_qa_batch.py`

Verification:

- `python -m py_compile scripts\run_domain_bootstrap_qa.py scripts\run_domain_bootstrap_qa_batch.py`
- `python -m pytest tests\test_domain_bootstrap_qa.py::test_run_query_plan_can_disable_helper_companion_assembly tests\test_domain_bootstrap_qa.py::test_run_query_plan_suppresses_legacy_native_helpers_when_disabled tests\test_domain_bootstrap_qa.py::test_helper_companion_row_limit_zero_suppresses_helper_results_only tests\test_domain_bootstrap_qa_batch.py -q`
  -> `7 passed`
- `python -m pytest tests\test_domain_bootstrap_qa.py tests\test_domain_bootstrap_qa_batch.py -q`
  -> `176 passed`

Lesson:

- The helper lane crossed from compression to retirement. `7281 -> 976` proved
  the bulk was delivery residue; the helper-free external stamp and unlike
  probes proved current architecture does not need helper companions as a
  default substrate.
- Retiring helpers is cleaner than carrying a low cap because it removes both
  context load and accidental architectural ambiguity. Any future helper row
  must be an explicit forensic or compatibility choice.

Next pressure:

- Re-run the focused QA/unit checks and then use native no-helper replays as
  compile-surface evidence. Misses should be routed to direct predicate
  preservation, source-fidelity invariants, or query planning, not back to
  native helper delivery.
