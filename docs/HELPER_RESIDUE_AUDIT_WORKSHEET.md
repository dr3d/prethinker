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

## HR-012 - Default-Path No-Helper Native Smoke

Date: 2026-05-16

Before:

- HR-011 changed the runtime default, but the first proof was unit-level: direct
  `run_query_plan` calls and batch command construction.
- The next risk was operational drift: a real batch QA run might still deliver
  helper rows through evidence-bundle execution, source-text repair, or cached
  artifacts.

Prediction:

- A replay using the batch wrapper defaults, with no helper flag passed at the
  batch level, should still execute child QA jobs with
  `--helper-companion-row-limit 0`.
- Helper rows should remain exactly `0` across primary query, evidence-bundle,
  and source-text repair paths.
- Any misses should classify as compile/query surface work, not helper pressure.

Intervention:

- Replayed the established three-fixture native pressure smoke against the
  invariant-guided compile root:
  - `count_composition_roster`
  - `industrial_sensor_clock_correction`
  - `probate_storage_access_register`
- Ran `8` questions per fixture, local model, `3` lanes, QA cache disabled.
- Did not pass `--helper-companion-row-limit` to the batch command; the wrapper
  default supplied the child-level `0` helper setting.

After:

| Fixture | Questions | Exact | Partial | Miss | Helper rows | Failure surfaces |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `count_composition_roster` | 8 | 8 | 0 | 0 | 0 | `not_applicable=8` |
| `industrial_sensor_clock_correction` | 8 | 7 | 0 | 1 | 0 | `hybrid_join_gap=1`, `not_applicable=7` |
| `probate_storage_access_register` | 8 | 4 | 0 | 4 | 0 | `compile_surface_gap=3`, `hybrid_join_gap=1`, `not_applicable=4` |
| Total | 24 | 19 | 0 | 5 | 0 | `compile_surface_gap=3`, `hybrid_join_gap=2`, `not_applicable=19` |

Artifacts:

- `docs/data/helper_residue/default_retired_smoke_20260516.json`
- `docs/data/helper_residue/default_retired_smoke_20260516.md`
- `tmp/helper_default_retired_smoke_20260516`

Verification:

- Dry-run confirmed the batch wrapper generated child commands containing
  `--helper-companion-row-limit 0` while the batch command itself relied on the
  default.
- Real QA completed with:
  - runtime load errors=`0`
  - write proposal rows=`0`
  - helper rows=`0`
  - cache hits=`0`
- Wall-clock runtime was about `10.5` minutes for `24` questions on `3` local
  lanes.

Lesson:

- Helper retirement holds through the real batch path. The feared helper bulk is
  no longer a default runtime surface.
- The remaining native pressure is now properly exposed: roster is inside the
  no-helper set; sensor needs a bounded line/value join; probate still has
  source-fidelity and section/addressability compile gaps plus one line-bound
  numeric/title join.
- This is the architecture moving in the right direction. The next repair layer
  should strengthen direct compile surfaces and query joins; it should not
  restore helper companion delivery.

Next pressure:

- Build a small compile/query surface diagnostic for the five non-exact rows:
  classify whether each needs direct role/section preservation, grouped source
  addressability, or a deterministic line-bound join.
- Use unlike probes before changing guidance so probate-specific section names
  do not become architecture.

## HR-013 - Line-Bound Join Candidate Rejected

Date: 2026-05-16

Before:

- HR-012 left `5` non-exact rows in the default no-helper smoke:
  - `3` probate compile-surface gaps,
  - `1` probate hybrid-join gap,
  - `1` sensor hybrid-join gap.
- The apparently reusable repair candidate was a line-bound source-record join:
  after a query identifies a source row for an entity, a later broad
  `source_record_numeric_token/2` query should be joined back to the same row
  and expose sibling fields from that row.

Prediction:

- If the candidate is a safe generic repair, it should improve the item
  title/year miss while preserving the other `19` exact rows and keeping helper
  rows at `0`.
- If it adds too much row surface or catches only a local query shape, the
  smoke should show score regression or surface drift. In that case the repair
  should be rejected rather than promoted.

Intervention:

- Temporarily added a row-context join candidate in `run_query_plan`:
  source row lookup plus same-row `source_record_field/3` and
  `source_record_numeric_token/2`.
- Added a focused unlike unit test proving the primitive can work on a small
  two-row source table.
- Replayed the same default-path no-helper smoke:
  `3` native pressure fixtures, `24` questions, `3` lanes, no cache, helper
  default untouched.

After:

| Run | Questions | Exact | Partial | Miss | Helper rows |
| --- | ---: | ---: | ---: | ---: | ---: |
| HR-012 default no-helper | 24 | 19 | 0 | 5 | 0 |
| Join candidate replay | 24 | 18 | 1 | 5 | 0 |

Per-fixture movement:

| Fixture | HR-012 | Join candidate | Movement |
| --- | ---: | ---: | --- |
| `count_composition_roster` | `8 / 0 / 0` | `7 / 0 / 1` | regression |
| `industrial_sensor_clock_correction` | `7 / 0 / 1` | `6 / 0 / 2` | regression |
| `probate_storage_access_register` | `4 / 0 / 4` | `5 / 1 / 2` | local improvement |

Artifacts:

- `docs/data/helper_residue/default_retired_smoke_join_repair_20260516.json`
- `docs/data/helper_residue/default_retired_smoke_join_repair_20260516.md`
- `tmp/helper_default_retired_smoke_join_repair_20260516`

Verification:

- Focused unit tests for the candidate passed before replay.
- Replay completed with runtime load errors=`0`, write proposal rows=`0`,
  helper rows=`0`.
- The candidate code was removed after the replay; it is not current
  architecture.

Lesson:

- The primitive is real but too blunt as a default query repair. It can expose
  useful same-row evidence, but adding broad row-context material changes the
  evidence surface enough to destabilize unrelated exact rows.
- The decision point is clear: do not promote broad line-bound joins from this
  evidence. The next layer must be more selective, probably at query planning
  or profile-palette level, and it must be tested on unlike fixtures before
  returning to probate density.
- The helper-retirement claim still holds. Both runs reported exactly `0`
  helper rows. The remaining work is query/surface precision, not helper
  restoration.

Next pressure:

- Build a diagnostic, not a repair, for the five non-exact coordinates:
  - direct role/person surface missing,
  - section/addressability missing,
  - source-row field/value join needed,
  - unsupported/prose-like query operation,
  - over-specific source-record constants.
- Use that diagnostic to choose between query-planner guidance, deterministic
  normalization, or a focused unlike probe. Do not reintroduce helper companion
  delivery.

## HR-014 - No-Helper Miss Coordinate Diagnostic

Date: 2026-05-16

Before:

- HR-012 established the default no-helper smoke at `19 / 0 / 5` with
  helper rows=`0`.
- HR-013 rejected the broad line-bound join candidate: it improved one local
  area but regressed unrelated exact rows, moving the smoke to `18 / 1 / 5`.
- The open decision was whether the remaining five native coordinates point
  back toward helpers, toward a generic row join, or toward a narrower
  source-surface/query-planning layer.

Prediction:

- If helper retirement is structurally sound, the remaining misses should
  classify as direct compile-surface/source-addressability gaps or selective
  query-planning gaps, not as missing helper companion delivery.
- If the broad join candidate was merely under-scoped, multiple coordinates
  should require the same row-context repair.

Intervention:

- Inspected the five non-exact rows from
  `docs/data/helper_residue/default_retired_smoke_20260516.json`.
- Compared the planned queries and failure-surface rationales against the
  compile/source-record evidence where needed.
- Wrote a coordinate diagnostic instead of changing code.

After:

| Coordinate | Existing surface | Diagnostic class | Recommended next layer |
| --- | --- | --- | --- |
| sensor vendor/model | `hybrid_join_gap` | unsupported text membership; entity-labeled source text not planned | query planner or profile palette |
| registrar role | `compile_surface_gap` | direct role surface missing; wrong source row anchor | compile-surface invariant |
| chronology section | `compile_surface_gap` | section addressability missing; late section not indexed | source-section preservation invariant |
| possession basis section | `compile_surface_gap` | explanatory basis section missing; multi-source basis missing | source-basis provenance surface |
| item title/year | `hybrid_join_gap` | predicate semantics collision; row-bound field/numeric need | selective query planner guidance |

Totals:

- compile-surface or source-preservation pressure=`3`
- query-planner or profile-palette pressure=`2`
- helper restoration pressure=`0`
- broad row-context join pressure=`0` as a default repair, because HR-013
  already rejected that promotion path

Artifacts:

- `docs/data/helper_residue/no_helper_miss_coordinate_diagnostic_20260516.json`
- `docs/data/helper_residue/no_helper_miss_coordinate_diagnostic_20260516.md`

Verification:

- No code changes in this entry.
- The diagnostic uses the same baseline run as HR-012 and the rejected replay
  evidence from HR-013.

Lesson:

- The no-helper native pressure is not a helper problem. It is mostly
  source-addressability: answer-bearing sections, role-bearing source rows, and
  basis/corroboration rows need to survive compile as queryable coordinates.
- The two hybrid rows are not permission for a broad row join. One needs
  entity-labeled source text planning; the other needs a semantic distinction
  between object titles and legal/ownership title predicates plus a selective
  row-bound field/numeric plan.
- The next repair should be probe-first: build unlike documents that contain
  source sections, correspondence roles, basis/corroboration, and
  entity-labeled vendor/model or object-title rows without using this fixture's
  vocabulary.

Next pressure:

- Build a focused source-addressability probe suite with unlike documents:
  - section heading preservation,
  - person-role rows from correspondence/signature/source lines,
  - state plus basis/corroborating source separation,
  - entity-labeled source text carrying attributes such as vendor/model or
    object title/year.
- Use the probe to decide whether the repair belongs in compile-surface
  invariants, profile palette selection, or query planning. Do not run the full
  native corpus again until this layer is sharper.

## HR-015 - Unlike Source-Addressability Probe Is Inside

Date: 2026-05-16

Before:

- HR-014 classified the five no-helper smoke misses:
  - `3` source-preservation/addressability coordinates,
  - `2` query-planner/profile-palette coordinates,
  - `0` helper-restoration coordinates.
- The unresolved question was whether the source-addressability shapes are
  generally hard without helpers, or whether the modern compile can handle them
  on clean unlike documents and only slips under native density.

Prediction:

- If the architecture already has the primitive, fresh unlike fixtures should
  answer section, role, basis/corroboration, vendor/model, and object-title/year
  questions with helper rows=`0`.
- If helper retirement removed needed substrate, the same shapes should miss
  even on clean unlike documents.

Intervention:

- Added two unlike probe fixtures under
  `experiments/boundary_probes/helper_residue_stage1`:
  - `municipal_lab_source_addressability`
  - `river_terminal_source_addressability`
- Each fixture contains:
  - equipment vendor/model rows,
  - object title/year rows,
  - a signed role-bearing source line,
  - a basis section,
  - a chronology section,
  - a corroborating source note.
- Compiled both fixtures on OpenRouter with source-record ledger facts enabled.
- Ran QA with the default no-helper path; no helper row limit flag was passed to
  override the new default.

After:

| Fixture | Questions | Exact | Partial | Miss | Helper rows |
| --- | ---: | ---: | ---: | ---: | ---: |
| `municipal_lab_source_addressability` | 6 | 6 | 0 | 0 | 0 |
| `river_terminal_source_addressability` | 6 | 6 | 0 | 0 | 0 |
| Total | 12 | 12 | 0 | 0 | 0 |

Compile notes:

- `municipal_lab_source_addressability`: parsed ok, `73` admitted rows,
  rough compile score `0.833`.
- `river_terminal_source_addressability`: parsed ok, `60` admitted rows,
  rough compile score `0.778`.

Artifacts:

- `experiments/boundary_probes/helper_residue_stage1/municipal_lab_source_addressability`
- `experiments/boundary_probes/helper_residue_stage1/river_terminal_source_addressability`
- `docs/data/helper_residue/source_addressability_probe_qa_20260516.json`
- `docs/data/helper_residue/source_addressability_probe_qa_20260516.md`
- `tmp/helper_residue_source_addressability_compile_20260516`
- `tmp/helper_residue_source_addressability_qa_20260516`

Verification:

- Compile completed for both probe fixtures with return code `0`.
- QA completed with:
  - runtime load errors=`0`,
  - write proposal rows=`0`,
  - helper rows=`0`,
  - cache hits=`0`.
- The QA score was `12 / 0 / 0`.

Lesson:

- Clean unlike source-addressability is inside the current no-helper set. The
  system can answer source-section, role-bearing notice, basis/corroboration,
  vendor/model, and object title/year questions without helper companions.
- The native misses are therefore not evidence that helper rows should return.
  They point at density and stability: under larger native packets the compile
  sometimes fails to preserve all answer-bearing source coordinates, and the
  planner sometimes chooses a nearby but semantically wrong predicate.
- This narrows the next architecture target. The useful work is not a broad
  helper or row-join repair; it is a density replay: make native-like dense
  packets preserve the same source coordinates that clean unlike packets already
  preserve.

Next pressure:

- Build a dense unlike variant of this probe, not a native-fixture patch:
  multiple source sections, repeated roles, more than one basis/corroboration
  pair, and nearby legal/ownership title language beside object-title language.
- If the dense unlike variant fails, repair at compile-surface preservation or
  query-planner selection level and replay both clean probes plus the native
  no-helper smoke.
- If the dense unlike variant still passes, return to the native miss
  coordinates as corpus-specific density and inspect compile variance before
  changing architecture.

## HR-016 - Dense Unlike Source-Addressability Still Holds

Date: 2026-05-16

Before:

- HR-015 proved clean unlike source-addressability at `12 / 0 / 0`, helper
  rows=`0`.
- That result showed the primitive is available in the current architecture,
  but it did not prove the primitive survives density:
  - repeated nearby roles,
  - decoy timeline sections,
  - multiple basis/corroboration pairs,
  - legal-title language near object-title language,
  - equipment service rows near vendor/model rows.

Prediction:

- If source-addressability only works in clean toy packets, the dense unlike
  fixture should reproduce the native failure shape.
- If the native pressure is more likely stale compile draw or native-corpus
  density rather than missing architecture, the dense unlike fixture should
  still score exact with helper rows=`0`.

Intervention:

- Added `dense_source_addressability_collision` under
  `experiments/boundary_probes/helper_residue_stage1`.
- The fixture contains `12` questions covering vendor/model, object title/year,
  repeated role-bearing notices, chronology-vs-budget section selection,
  two basis sections, two corroborating source notes, and legal-title vs
  possession-basis distinction.
- Compiled on OpenRouter with source-record ledger facts enabled.
- Ran QA with the default no-helper path.

After:

| Fixture | Questions | Exact | Partial | Miss | Helper rows |
| --- | ---: | ---: | ---: | ---: | ---: |
| `dense_source_addressability_collision` | 12 | 12 | 0 | 0 | 0 |

Compile notes:

- Parsed ok.
- Admitted rows=`141`.
- Skipped rows=`1`.
- Rough compile score=`0.889`.
- Profile audit warned on `person_role_at/3` repeated-structure role mismatch,
  but the behavioral QA did not fail.

Artifacts:

- `experiments/boundary_probes/helper_residue_stage1/dense_source_addressability_collision`
- `docs/data/helper_residue/dense_source_addressability_probe_qa_20260516.json`
- `docs/data/helper_residue/dense_source_addressability_probe_qa_20260516.md`
- `tmp/helper_residue_dense_source_addressability_compile_20260516`
- `tmp/helper_residue_dense_source_addressability_qa_20260516`

Verification:

- Compile return code=`0`.
- QA completed with:
  - runtime load errors=`0`,
  - write proposal rows=`0`,
  - helper rows=`0`,
  - cache hits=`0`.
- Dense unlike QA score was `12 / 0 / 0`.

Lesson:

- Source-addressability is not merely inside on clean probes; it also holds
  under a moderate density probe with decoy sections and semantic collisions.
- This strengthens the helper-retirement claim. The current architecture can
  carry source-section, role-bearing source line, basis/corroboration,
  vendor/model, and object-title/year questions without helper companion rows.
- The remaining native failures should now be treated as one of:
  - stale compile draw from the earlier compile root,
  - native-corpus density beyond the probe,
  - planner selection against a specific native predicate palette.
  None of those are evidence for restoring helper delivery.

Next pressure:

- Recompile the two native pressure fixtures with the current instrument:
  `industrial_sensor_clock_correction` and `probate_storage_access_register`.
- Run the same first-8 no-helper QA slice against the fresh compile root.
- If the fresh native draw clears or improves the misses, journal them as stale
  compile/variance evidence. If the same misses persist, inspect those compile
  surfaces directly and repair only the smallest transferable planner or
  preservation rule.

## HR-017 - Native Pressure Slice Repaired Without Helper Return

Date: 2026-05-16

Before:

- HR-016 showed clean and dense unlike source-addressability probes inside the
  no-helper set:
  - clean unlike probes=`24 / 0 / 0` total across three probe fixtures,
  - helper rows=`0`.
- The open risk was native density. The same first-8 native pressure slice had
  previously scored:
  - HR-012 old compile root: `11 / 0 / 5` across the two pressure fixtures,
  - fresh recompile before repair: `11 / 0 / 5`, but with different misses.

Prediction:

- If the helper-retirement path is right, the remaining pressure should respond
  to small source-surface/query-normalization repairs while helper rows stay at
  `0`.
- If the old helpers were still structurally needed, no-helper replay should
  stay flat or require broad companion delivery to improve.

Intervention:

Accepted:

- Added a no-helper `source_record_field` to same-row
  `source_record_text_atom` fallback for unsplit source/header lines.
- Strengthened compile guidance for source-role/source-basis preservation:
  source/header/signature/correspondence roles and basis/corroboration source
  coordinates should be direct candidate surfaces when compatible predicates
  exist.
- Promoted the existing item-description title/year normalizer into the
  no-helper query path as `core-local` support, without `HelperClass`, so it
  does not count as helper companion delivery.

Rejected:

- Tried a stronger role-subject compile nudge that said person-plus-role lines
  must bind the person as role holder. It made probate compile denser and
  regressed QA, so the added wording was removed.

After:

| Run | Scope | Exact | Partial | Miss | Helper rows | Decision |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Fresh native recompile | two fixtures, first 8 | 11 | 0 | 5 | 0 | baseline |
| Source-text fallback | same compile root | 12 | 1 | 3 | 0 | accepted |
| Source-role/source-basis compile contract | fresh compile | 14 | 0 | 2 | 0 | accepted |
| No-helper item-detail core projection | same compile root | 15 | 0 | 1 | 0 | accepted |
| Strong role-subject nudge | probate only | 5 | 0 | 3 | 0 | rejected |

Best accepted native pressure result:

| Fixture | Questions | Exact | Partial | Miss | Helper rows |
| --- | ---: | ---: | ---: | ---: | ---: |
| `industrial_sensor_clock_correction` | 8 | 8 | 0 | 0 | 0 |
| `probate_storage_access_register` | 8 | 7 | 0 | 1 | 0 |
| Total | 16 | 15 | 0 | 1 | 0 |

Artifacts:

- `docs/data/helper_residue/native_pressure_recompile_qa_20260516.json`
- `docs/data/helper_residue/native_pressure_recompile_qa_20260516.md`
- `docs/data/helper_residue/native_pressure_text_fallback_qa_20260516.json`
- `docs/data/helper_residue/native_pressure_text_fallback_qa_20260516.md`
- `docs/data/helper_residue/native_pressure_source_role_contract_qa_20260516.json`
- `docs/data/helper_residue/native_pressure_source_role_contract_qa_20260516.md`
- `docs/data/helper_residue/native_pressure_item_detail_qa_20260516.json`
- `docs/data/helper_residue/native_pressure_item_detail_qa_20260516.md`
- `docs/data/helper_residue/native_pressure_role_subject_qa_20260516.json`
- `docs/data/helper_residue/native_pressure_role_subject_qa_20260516.md`
- `tmp/helper_residue_native_pressure_recompile_20260516`
- `tmp/helper_residue_native_pressure_recompile_qa_20260516`
- `tmp/helper_residue_native_pressure_text_fallback_qa_20260516`
- `tmp/helper_residue_native_pressure_source_role_contract_compile_20260516`
- `tmp/helper_residue_native_pressure_source_role_contract_qa_20260516`
- `tmp/helper_residue_native_pressure_item_detail_qa_20260516`
- `tmp/helper_residue_native_pressure_role_subject_compile_20260516`
- `tmp/helper_residue_native_pressure_role_subject_qa_20260516`

Verification:

- `python -m py_compile scripts\run_domain_bootstrap_file.py scripts\run_domain_bootstrap_qa.py`
- `python -m pytest tests\test_domain_bootstrap_qa.py -q`
  - `174 passed`
- Behavioral replay completed with:
  - runtime load errors=`0`,
  - write proposal rows=`0`,
  - helper rows=`0`.

Lesson:

- Helper retirement survived the pressure test. The native pressure slice moved
  from `11 / 0 / 5` to `15 / 0 / 1` without restoring helper companion rows.
- The successful repairs are structural:
  - exact source-line text fallback for unsplit source metadata,
  - direct source-role/source-basis compile contracts,
  - item-description title/year normalization as core query support.
- The rejected role-subject nudge is important evidence. More insistent compile
  prose can make a dense native fixture worse by changing the predicate palette.
  The last residual should not be attacked with broader wording.
- The remaining miss is a source-text role extraction case: the answer is
  visible in source-record text, but the compile still does not expose a stable
  person-role row for that source line. That is a narrow role-line extraction
  issue, not a helper-delivery issue.

Next pressure:

- Stop broad helper-residue repair here. The accepted result is a strong
  decision point: `15 / 0 / 1`, helper rows=`0`.
- For the final registrar/source-role residual, design a separate narrow
  role-line extraction audit with unlike source lines before changing compile
  guidance again. Do not use the native role noun as architecture.
- Once that is done, replay the three fixture smoke and then consider a larger
  native no-helper scan.

## HR-018 - Generic Role-Line Projection Rejected

Date: 2026-05-16

Before:

- HR-017 left one residual in the accepted no-helper native pressure slice:
  `15 / 0 / 1`, helper rows=`0`.
- The residual looked tempting: source text contained a person plus role, but
  the compile did not expose a structured person-role row.
- Existing legacy helper code already contains registrar-shaped packet metadata
  recognition. The audit goal was to avoid promoting that fixture-shaped logic.

Prediction:

- A generic deterministic role-line projection might recover person-plus-role
  source text without restoring helper companions if it:
  - emits no `HelperClass`,
  - handles unlike role lines,
  - avoids table headers, organization names, and negated/non-person phrases,
  - improves the native pressure slice without disturbing existing exact rows.

Intervention:

- Temporarily added a no-helper `source_record_role_line_support` projection
  over normalized `source_record_text_atom/2` rows.
- Tested it on unlike source-line shapes such as records liaison, terminal
  registrar, and embedded person-plus-role text.
- First replay showed false positives from organization/header text.
- Tightened the recognizer to exclude organization suffixes, table-header
  tokens, and negated/non-person phrases.
- Replayed the accepted native compile root after both attempts.

After:

| Run | Scope | Exact | Partial | Miss | Helper rows | Decision |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| HR-017 accepted state | two fixtures, first 8 | 15 | 0 | 1 | 0 | keep |
| Loose role-line projection | same compile root | 14 | 1 | 1 | 0 | reject |
| Tight role-line projection | same compile root | 13 | 0 | 3 | 0 | reject |

Artifacts:

- `docs/data/helper_residue/native_pressure_role_line_core_qa_20260516.json`
- `docs/data/helper_residue/native_pressure_role_line_core_qa_20260516.md`
- `docs/data/helper_residue/native_pressure_role_line_tight_qa_20260516.json`
- `docs/data/helper_residue/native_pressure_role_line_tight_qa_20260516.md`
- `tmp/helper_residue_native_pressure_role_line_core_qa_20260516`
- `tmp/helper_residue_native_pressure_role_line_tight_qa_20260516`

Verification:

- The role-line code and unit test were removed after rejection.
- Current focused tests are back to:
  - `python -m py_compile scripts\run_domain_bootstrap_qa.py`
  - `python -m pytest tests\test_domain_bootstrap_qa.py -q`
  - `174 passed`

Lesson:

- Deterministic role-line parsing is a real primitive, but this implementation
  is not stable enough for default architecture. Even after false-positive
  tightening, it reduced the native pressure score.
- The failure mode is exactly the guardrail: normalized source text can make
  organization labels, table headers, negated phrases, and person-role lines
  look structurally similar. A regex/token recognizer can become fixture-era
  helper logic in cleaner clothes.
- The accepted architecture remains HR-017: source-line fallback,
  source-role/source-basis compile contracts, and item-title/year core
  projection. The final role residual should be addressed by better compile
  preservation or a more principled role-line audit layer, not by promoting this
  recognizer.

Next pressure:

- Keep the accepted `15 / 0 / 1` no-helper state as the current decision point.
- Do not chase the last native residual inside helper residue. Move to a
  separate role-line/source-role audit only if it can define stronger admission
  criteria than adjacent token parsing.
- The next high-value check is a slightly broader no-helper native smoke using
  the accepted state, not more local role-line tinkering.

## HR-019 - Core Support Surfaces Are Not Helper Rows

Date: 2026-05-16

Before:

- HR-018 rejected role-line projection and kept the HR-017 accepted state:
  source-line fallback, source-role/source-basis compile contracts, and
  deterministic item title/year projection.
- A broader accepted-state replay across three native fixtures was needed to
  see whether no-helper delivery held outside the two-fixture pressure slice.
- The old delivery metric treated any predicate ending in `_support` as helper
  pressure, even when the row was emitted as `core-local` and had no
  `HelperClass`.

Prediction:

- If the helper-retirement line is real, a core-local deterministic projection
  should remain visible under a zero-helper budget without counting as helper
  delivery.
- If that distinction is only bookkeeping, replay will either restore helper
  rows or fail to recover the item-detail row.

Intervention:

- Replayed the accepted compile root on three native fixtures:
  `count_composition_roster`, `industrial_sensor_clock_correction`, and
  `probate_storage_access_register`.
- Tightened helper-result detection so `core-local` rows without `HelperClass`
  are not treated as helper companions merely because the predicate name ends
  in `_support`.
- Applied the same detector to helper summary accounting.
- Did not reintroduce legacy native helper adapters.

After:

| Run | Scope | Exact | Partial | Miss | Helper rows | Note |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Accepted-state replay, pre-metric fix | three fixtures, first 8 | 19 | 1 | 4 | 0 | item-detail surface generated but support suffix accounting was too blunt |
| Core-support delivery replay | same compile root | 21 | 0 | 3 | 0 | core-local support survives; legacy helper rows remain absent |

Remaining non-exacts:

| Fixture | Question shape | Surface | Interpretation |
| --- | --- | --- | --- |
| `industrial_sensor_clock_correction` | vendor/model for a sensor | compile-surface gap | commercial detail predicates were not preserved in this draw |
| `probate_storage_access_register` | person named as registrar | compile-surface gap | source-stated person-role row is absent |
| `probate_storage_access_register` | section basis for possession | compile-surface gap | statement-to-section link for the possession basis is absent |

Artifacts:

- `docs/data/helper_residue/three_fixture_accepted_qa_20260516.json`
- `docs/data/helper_residue/three_fixture_accepted_qa_20260516.md`
- `docs/data/helper_residue/three_fixture_core_support_delivery2_qa_20260516.json`
- `docs/data/helper_residue/three_fixture_core_support_delivery2_qa_20260516.md`
- `tmp/helper_residue_three_fixture_accepted_compile_20260516`
- `tmp/helper_residue_three_fixture_accepted_qa_20260516`
- `tmp/helper_residue_three_fixture_core_support_delivery2_qa_20260516`

Verification:

- Focused unit suite:
  - `python -m pytest tests\test_domain_bootstrap_qa.py -q`
  - `174 passed`
- The final replay reports:
  - `21 / 0 / 3`
  - helper rows=`0`
  - runtime load errors=`0`
  - write proposal rows=`0`

Lesson:

- Helper retirement requires two separate invariants:
  - legacy query-only companions must stay out of the delivery path;
  - deterministic core-local projections must not be erased or counted as
    helper pressure because their predicate names use support-like vocabulary.
- The 7,000-plus helper-row problem is not solved by making every support
  surface disappear. Some support surfaces are now architecture: compact,
  deterministic, fixture-free, and unlabeled by `HelperClass`.
- The remaining no-helper native misses are compile-preservation misses. They
  ask for better direct surfaces, not the return of helper companions.

Next pressure:

- Keep helper companions retired by default.
- Treat `core-local` support surfaces as part of the deterministic QA layer,
  not helper residue.
- Move the next work to compile-surface preservation for recurring source
  addressability gaps: commercial item attributes, person-role source lines,
  and statement-to-section provenance links.

## HR-020 - Equipment Specification Loss Belongs In Profile Review

Date: 2026-05-16

Before:

- HR-019 left three no-helper misses:
  - equipment vendor/model not preserved as direct predicates;
  - person-role source line absent;
  - statement-to-section provenance link absent.
- The compile guidance already said to preserve vendor/model-like surfaces, but
  the sensor profile did not provide an attribute slot, so the compiler could
  only keep the values in source-record text.

Prediction:

- If the pressure is profile-surface loss, broad compile guidance alone will
  not reliably recover vendor/model rows.
- A profile-review audit rule should flag equipment/device/instrument
  specification fields when the proposed profile only exposes id/status/scope
  rows.

Intervention:

- Added profile-bootstrap guidance for equipment/device/instrument/product/
  asset specifications: source-stated descriptive, identifying, versioning,
  capacity, location, qualification, or scope attributes are query-bearing.
- First equipment-pressure recompile after bootstrap guidance did not produce
  direct vendor/model predicates. The profile still centered device id plus
  certification rows.
- Added a profile-review rule for equipment-specification loss. The review then
  flagged the missing capability and retry guidance added domain-owned
  vendor/model predicates and related device-specification slots.
- Recompiled the equipment-pressure fixture and ran first-8 no-helper QA.

After:

| Run | Scope | Exact | Partial | Miss | Helper rows | Movement |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| HR-019 accepted-state sensor slice | first 8 | 7 | 0 | 1 | 0 | vendor/model absent |
| Bootstrap-only equipment guidance | compile inspection | n/a | n/a | n/a | n/a | profile still omitted vendor/model |
| Review-hardened equipment guidance | first 8 | 6 | 0 | 2 | 0 | vendor/model fixed; operator attribution exposed |

Resolved coordinate:

- The equipment-pressure row now has direct domain-owned vendor/model facts.
  Exact predicate names and emitted atoms are recorded in the run artifact, but
  they are not promoted here as reusable architecture vocabulary.
- The judge marked the vendor/model question exact.

New/remaining coordinates:

- Section-addressability query still overuses unsupported string/search
  predicates for human section-title lookup.
- A role-bearing operational source line now fails when the compile has event
  rows from the role-bearing source context but does not preserve the named
  person as a direct person-role/source row.

Artifacts:

- `docs/data/helper_residue/equipment_attribute_review_qa_20260516.json`
- `docs/data/helper_residue/equipment_attribute_review_qa_20260516.md`
- `tmp/helper_residue_equipment_attribute_compile_20260516`
- `tmp/helper_residue_equipment_attribute_review_compile_20260516`
- `tmp/helper_residue_equipment_attribute_review_qa_20260516`

Verification:

- Focused suite:
  - `python -m py_compile src\profile_bootstrap.py scripts\run_domain_bootstrap_file.py`
  - `python -m pytest tests\test_domain_bootstrap_qa.py tests\test_story_world_dataset.py -q`
  - `246 passed`

Lesson:

- Compile-surface preservation starts earlier than the compile. If the profile
  omits a reusable attribute slot, later guidance can correctly request a
  surface that the compiler has no clean vocabulary to emit.
- This is not a sensor-specific repair. The structural rule is:
  source-stated specifications on devices, equipment, products, inventory
  items, or assets need a queryable attribute surface before QA has to parse
  normalized prose.
- The score did not improve globally on the sensor first-8 slice because the
  fresh compile exposed an adjacent operator-attribution gap. That is not a
  reason to restore helpers; it is the next compile-preservation coordinate.

Next pressure:

- Apply the same review/audit shape to source-stated person-plus-role lines
  without enumerating the observed role vocabulary.
- Require the profile/review layer to notice when a source names a person plus
  role but the profile lacks a direct person-role/source slot.

## HR-021 - Source-Role Review Without Fixture Vocabulary

Date: 2026-05-16

Before:

- HR-020 showed that profile-review hardening can recover a missing
  compile-surface slot when the source states a reusable structural attribute.
- The next residual class was source-stated person-plus-role lines: named
  people tied to source, attendance, authorship, compilation, review, or other
  role-bearing contexts.
- This class is dangerous because examples can easily borrow current fixture
  vocabulary and turn the audit rule into a recognizer for recent rows.

Prediction:

- A fixture-free source-role review rule should cause profile retry to add a
  person-role/source-role slot when the source states a named person with a
  role and context.
- If the wording smuggles current fixture nouns, the rule should be rewritten
  before any result is treated as architecture.

Intervention:

- Added a profile-bootstrap/review rule for role-bearing source lines:
  signatures, headers, attendance notes, correspondence blocks,
  source-authored notes, office/title labels, and similar person-plus-role
  lines.
- Removed current-corpus-flavored role examples from the guidance after a
  leakage check. The instrument wording now names the contract, not the local
  fixture role.
- Verified the patched instrument text with a repository search for current
  names and row vocabulary.
- Recompiled the sensor pressure fixture with the cleaned guidance and ran
  first-8 no-helper QA.

After:

| Run | Scope | Exact | Partial | Miss | Helper rows | Note |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| HR-020 review-hardened equipment run | sensor first 8 | 6 | 0 | 2 | 0 | vendor/model fixed; person-role absent |
| HR-021 cleaned source-role run | sensor first 8 | 7 | 0 | 1 | 0 | vendor/model and person-role exact |

Resolved coordinates:

- Equipment specification remained exact through direct vendor/model rows.
- Source-stated person-role context became queryable through a direct
  role/context row.

Remaining coordinate:

- Section-title/addressability is now a query-surface gap: the KB has the
  relevant section atoms, but the query plan still reaches for unsupported
  string predicates and does not isolate the section-display coordinate.

Artifacts:

- `docs/data/helper_residue/source_role_review_sensor_clean_qa_20260516.json`
- `docs/data/helper_residue/source_role_review_sensor_clean_qa_20260516.md`
- `tmp/helper_residue_source_role_review_sensor_compile_20260516`
- `tmp/helper_residue_source_role_review_sensor_clean_compile_20260516`
- `tmp/helper_residue_source_role_review_sensor_clean_qa_20260516`

Verification:

- Focused suite:
  - `python -m py_compile src\profile_bootstrap.py scripts\run_domain_bootstrap_file.py`
  - `python -m pytest tests\test_domain_bootstrap_qa.py tests\test_story_world_dataset.py -q`
  - `246 passed`

Lesson:

- Source-role preservation is real, but it must be stated as a slot contract:
  named person, role, and governed source/context. The instrument should not
  name the recent fixture role that exposed the gap.
- The profile-review layer is becoming the right place for this class of work:
  it catches missing vocabulary before compile has to choose between hiding a
  person-role line in source text or inventing a brittle local predicate.
- The remaining sensor miss is no longer helper residue or profile-slot loss.
  It is section-display/query-surface resolution.

Next pressure:

- Run the cleaned source-role rule on the custody/provenance fixture that still
  has a person-role residual, then decide whether the rule transfers or needs
  a stricter source-role slot contract.
- After that, address section-display/source-addressability as a query-surface
  problem rather than a helper problem.

## HR-022 - Source-Role Transfer Check Points To Provenance Links

Date: 2026-05-16

Before:

- HR-021 repaired the sensor source-role coordinate under cleaned,
  fixture-free source-role guidance.
- The transfer question was whether the same contract would help a second
  native fixture with source-stated role language, without adding local role
  nouns to the instrument.

Prediction:

- If source-role review is structural, the second fixture should either expose
  a direct role row or give the query planner enough source-record evidence to
  answer without helper rows.
- If it is not structural, the role question will remain a compile-surface gap
  and the next step should be a stricter role-slot contract, not a local parser.

Intervention:

- Recompiled the custody/provenance fixture with the cleaned source-role
  profile-review guidance.
- Ran first-8 no-helper QA against the fresh compile.

After:

| Run | Scope | Exact | Partial | Miss | Helper rows | Note |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| HR-019 accepted-state probate slice | first 8 | 6 | 0 | 2 | 0 | role and provenance residuals |
| HR-022 source-role transfer check | first 8 | 7 | 0 | 1 | 0 | role row exact; provenance residual remains |

Resolved coordinate:

- The source-stated person-role question was judged exact with no helper rows.
  The support came through source-record evidence and broad role rows rather
  than a narrow local helper.

Remaining coordinate:

- The possession-basis question still needs a direct statement-to-section
  provenance link. The semantic assertion and physical custody rows exist, but
  the section/source coordinate that states the basis is not bound to the
  assertion row.

Artifacts:

- `docs/data/helper_residue/source_role_review_probate_qa_20260516.json`
- `docs/data/helper_residue/source_role_review_probate_qa_20260516.md`
- `tmp/helper_residue_source_role_review_probate_compile_20260516`
- `tmp/helper_residue_source_role_review_probate_qa_20260516`

Verification:

- QA summary:
  - `7 / 0 / 1`
  - helper rows=`0`
  - runtime load errors=`0`
  - write proposal rows=`0`

Lesson:

- The source-role rule transfers enough to keep it, but the second fixture did
  not prove that every role-bearing source line now emits the ideal direct
  person-role/source slot. The important result is narrower: no helper return
  was needed for the role question.
- The surviving residual is a different class: source provenance binding for a
  semantic assertion. This should not be repaired by a person-role recognizer.

Next pressure:

- Harden profile/bootstrap review for statement-to-section provenance:
  when a source states a semantic assertion, custody/access/status fact, basis,
  rationale, or evidence item in a named section/source coordinate, the profile
  needs a way to bind the semantic assertion to that source coordinate.
- Then replay the two remaining provenance/addressability rows before any
  native corpus rerun.

## HR-023 - Fixture-Language Audit Separates New Guidance From Legacy Adapters

Date: 2026-05-16

Before:

- HR-021 and HR-022 added or exercised profile-review guidance for equipment
  attributes and source-stated roles.
- The active risk was whether those repairs had quietly promoted native fixture
  language into the current instrument.

Prediction:

- If the new guidance is clean, fixture/story nouns should be absent from the
  profile bootstrap/review wording.
- If leakage exists, it should show up either as local nouns in the new profile
  guidance or as older query-time recognizers that are still reachable through
  normal QA execution.

Intervention:

- Searched `src` and `scripts` for recent native pressure terms, role nouns,
  local identifiers, and answer-bearing story strings.
- Inspected the query-companion dispatch path to verify whether legacy native
  adapters are enabled by default.

After:

- The recent profile guidance in `src/profile_bootstrap.py` does not contain
  the local fixture names, local people, question IDs, section IDs, or answer
  strings that exposed the current gaps.
- Legacy query-helper adapters in `scripts/run_domain_bootstrap_qa.py` still
  contain fixture-shaped recognizers and display strings for old native corpus
  compatibility.
- Those legacy adapters are default-off:
  - `--helper-companion-row-limit` defaults to `0`, disabling helper companion
    assembly,
  - `--include-legacy-native-helper-adapters` is opt-in,
  - legacy adapter outputs are marked with
    `adapter_status=legacy_native_compatibility_adapter` and
    `default_delivery=disabled`.
- The source-record ledger had one lexical trigger with terms too close to
  current native pressure examples. It was rewritten in this pass to preserve
  source-fidelity lines by structural criteria: reproduced/reference status,
  finding/ruling status, source support/corroboration, basis language, and
  source-action patterns ending in `by`.

Artifacts:

- Code inspection:
  - `src/profile_bootstrap.py`
  - `scripts/run_domain_bootstrap_qa.py`
  - `src/source_record_ledger.py`

Verification:

- The fixture-shaped query helpers are not active under the current default QA
  path.
- The fixture-shaped strings still exist in quarantined legacy adapter code, so
  the answer to the audit question is not "none"; it is "quarantined legacy
  code remains, current repairs did not add new fixture vocabulary, and the
  source-ledger trigger was cleaned."

Lesson:

- Fixture language can leak through three different surfaces:
  profile/review guidance, query-time adapters, and source-ledger trigger
  lexicons. The first surface looks clean in this cycle. The second is
  quarantined but still present. The third was converted from example terms to
  structural source-fidelity language.
- Default-off is acceptable for forensic compatibility, but it is not the same
  as architecture cleanliness. Anything still in live code must be either
  structural, deleted, or explicitly outside the stamped instrument.

Next pressure:

- Keep legacy native adapters out of normal QA and decide whether to move them
  into history rather than carrying them in the live script.
- Only then continue toward the native no-helper smoke and corpus rerun.

## HR-024 - Recent-Addition Leakage Audit Catches Enumeration Drift

Date: 2026-05-16

Before:

- HR-023 separated current profile guidance from quarantined legacy adapters.
- A follow-up review questioned HR-020 specifically: sensor-specific predicate
  names, the equipment attribute enumeration, and the role enumeration in the
  next-pressure text could still make fixture pressure look like architecture.

Prediction:

- If the leak was only in historical artifacts, the current diff should be
  clean and no instrument edits should be needed.
- If recent additions drifted toward fixture vocabulary, added-line audit over
  the last few commits should find the concrete terms.

Intervention:

- Audited added lines from the recent no-helper/helper-residue commits and the
  current working tree.
- Rewrote live profile guidance from enumerated equipment attributes to
  structural categories: descriptive, identifying, versioning, capacity,
  location, qualification, and scope attributes.
- Removed sensor-specific predicate examples from profile guidance.
- Rewrote compile guidance that named a specific record-author role and
  vendor/model values into structural record-author and source-stated
  specification language.
- Rewrote HR-020 so exact emitted predicate names remain in run artifacts, not
  in the worksheet's architecture claim.

After:

- Current live guidance has no recent sensor-specific predicate names, local
  identifiers, answer strings, question IDs, or the record-author role noun
  that exposed the pressure.
- HR-020 now describes the repair as a reusable equipment/specification
  attribute contract rather than as a sensor predicate success.
- Older worksheet entries still mention old coordinates because they are
  historical observations, not active guidance.

Artifacts:

- `src/profile_bootstrap.py`
- `scripts/run_domain_bootstrap_file.py`
- `src/source_record_ledger.py`
- `docs/HELPER_RESIDUE_AUDIT_WORKSHEET.md`

Verification:

- Added-line audit against the current working tree found no hits for the
  recent risky phrases in live guidance.
- Focused suite:
  - `python -m py_compile src\profile_bootstrap.py src\source_record_ledger.py scripts\run_domain_bootstrap_file.py scripts\run_domain_bootstrap_qa.py`
  - `python -m pytest tests\test_source_record_ledger.py tests\test_domain_bootstrap_file.py tests\test_domain_bootstrap_qa.py tests\test_story_world_dataset.py -q`
  - `300 passed`

Lesson:

- Generic-looking enumerations can still be corpus-shaped. The safer pattern is
  to name the slot class and admission contract, then let domain-owned
  predicates instantiate it.
- Run artifacts may preserve exact predicate names and emitted atoms. The
  instrument and methodology worksheet should promote only the transfer-level
  contract.

Next pressure:

- Commit this cleanup before more probe work, so the no-helper/native rerun
  starts from a clean instrument surface.
- Continue toward statement-to-section provenance only if the repair can be
  phrased as a source-coordinate slot contract, not as a local source parser.

## HR-025 - Source-Coordinate Slots Need Query Normalization, Not Helpers

Date: 2026-05-16

Before:

- HR-022 left the accepted probate no-helper slice at `7 / 0 / 1`, helper
  rows `0`.
- The remaining residual was source-coordinate provenance: the KB could answer
  the semantic custody/status question, but the source coordinate that stated
  the basis was not reliably bound to the answer surface.
- HR-024 cleaned the current instrument surface before further probe work.

Prediction:

- A generic source-coordinate profile contract should let the compiler preserve
  the semantic assertion, source coordinate, and support role without reviving
  helper rows.
- If the repair is truly structural, the final recovery should come from
  populated source-coordinate predicates or from deterministic query
  normalization over existing source-record surfaces, not from a fixture parser.

Intervention:

- Added profile guidance and profile-review guidance for source-coordinate
  provenance:
  - preserve the governed semantic assertion,
  - preserve the source row/section/note/document coordinate,
  - preserve the support role/status,
  - avoid invented claim ids that cannot be populated from source-stated slots.
- Ran two OpenRouter compile/QA probes on the probate source-coordinate slice:
  - a broad profile contract run,
  - a tightened source-coordinate slot run.
- Added generic QA-planner guidance for source-coordinate questions:
  - discover source rows with variables before binding a section or label,
  - use source-record text/field rows for source-stated role lines when direct
    role predicates are absent or organization-level only.
- Extended deterministic placeholder normalization so lowercase `title` is
  treated as a slot variable, matching the existing placeholder treatment for
  `label`, `content`, `value`, `status`, and related slot words.
- Ran the transfer-safety check suggested by review: when `title` or
  `description` is a legitimate source value, the runtime must preserve a
  successful literal query and only normalize placeholder-like lowercase values
  after the original query misses.
- Added deterministic source-coordinate hint queries for questions that ask for
  a source coordinate or source-stated capacity, and extended the existing
  item-description detail projection to accept descriptive `item_id/2` surfaces
  without helper rows.

After:

| Run | Questions | Exact | Partial | Miss | Helper rows | Result |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| HR-022 accepted probate slice | 8 | 7 | 0 | 1 | 0 | baseline |
| Broad source-coordinate profile | 8 | 5 | 0 | 3 | 0 | rejected |
| Tight source-coordinate profile | 8 | 6 | 0 | 2 | 0 | partial |
| Tight profile + source-coordinate QA guidance | 8 | 6 | 1 | 1 | 0 | partial |
| Tight profile + deterministic title normalization | 8 | 8 | 0 | 0 | 0 | provisional; failed literal-value safety check |
| Literal-safe placeholder normalization | 8 | 6 | 0 | 2 | 0 | rejected; protected literals but lost local recovery |
| Literal-safe normalization + source-coordinate hints | 8 | 6 | 1 | 1 | 0 | partial |
| Literal-safe normalization + source hints + `item_id/2` detail projection | 8 | 7 | 0 | 1 | 0 | accepted safe state |

- The broad profile contract over-produced/under-bound and regressed the slice.
- The tightened slot guidance recovered the basis/source-coordinate row but
  still depended on query behavior.
- The `8 / 0 / 0` run was not accepted as architecture after transfer review:
  preemptive normalization of common words such as `title` could broaden a
  query where the word was a legitimate data value.
- The accepted safe state is `7 / 0 / 1`, helper rows `0`: the title/year and
  source-section residuals are repaired without helpers, while the remaining
  source-stated capacity row is honestly classified as a compile-surface gap
  until the compiler emits a direct role-bearing predicate.

Artifacts:

- `src/profile_bootstrap.py`
- `scripts/run_domain_bootstrap_qa.py`
- `tests/test_profile_bootstrap.py`
- `tests/test_domain_bootstrap_qa.py`
- `docs/data/helper_residue/source_coordinate_profile_compile_20260516.json`
- `docs/data/helper_residue/source_coordinate_profile_compile_20260516.md`
- `docs/data/helper_residue/source_coordinate_profile_qa_20260516.json`
- `docs/data/helper_residue/source_coordinate_profile_qa_20260516.md`
- `docs/data/helper_residue/source_coordinate_profile_slot_compile_20260516.json`
- `docs/data/helper_residue/source_coordinate_profile_slot_compile_20260516.md`
- `docs/data/helper_residue/source_coordinate_profile_slot_qa_20260516.json`
- `docs/data/helper_residue/source_coordinate_profile_slot_qa_20260516.md`
- `docs/data/helper_residue/source_coordinate_profile_slot_qaguidance_qa_20260516.json`
- `docs/data/helper_residue/source_coordinate_profile_slot_qaguidance_qa_20260516.md`
- `docs/data/helper_residue/source_coordinate_profile_slot_qaguidance2_qa_20260516.json`
- `docs/data/helper_residue/source_coordinate_profile_slot_qaguidance2_qa_20260516.md`
- `docs/data/helper_residue/source_coordinate_profile_slot_qanorm_qa_20260516.json`
- `docs/data/helper_residue/source_coordinate_profile_slot_qanorm_qa_20260516.md`
- `docs/data/helper_residue/source_coordinate_profile_slot_safeplaceholder_qa_20260516.json`
- `docs/data/helper_residue/source_coordinate_profile_slot_safeplaceholder_qa_20260516.md`
- `docs/data/helper_residue/source_coordinate_profile_slot_sourcehints_qa_20260516.json`
- `docs/data/helper_residue/source_coordinate_profile_slot_sourcehints_qa_20260516.md`
- `docs/data/helper_residue/source_coordinate_profile_slot_itemid_sourcehints_qa_20260516.json`
- `docs/data/helper_residue/source_coordinate_profile_slot_itemid_sourcehints_qa_20260516.md`
- `tmp/helper_residue_source_coordinate_profile_compile_20260516`
- `tmp/helper_residue_source_coordinate_profile_qa_20260516`
- `tmp/helper_residue_source_coordinate_profile_slot_compile_20260516`
- `tmp/helper_residue_source_coordinate_profile_slot_qa_20260516`
- `tmp/helper_residue_source_coordinate_profile_slot_qaguidance_qa_20260516`
- `tmp/helper_residue_source_coordinate_profile_slot_qaguidance2_qa_20260516`
- `tmp/helper_residue_source_coordinate_profile_slot_qanorm_qa_20260516`
- `tmp/helper_residue_source_coordinate_profile_slot_safeplaceholder_qa_20260516`
- `tmp/helper_residue_source_coordinate_profile_slot_sourcehints_qa_20260516`
- `tmp/helper_residue_source_coordinate_profile_slot_itemid_sourcehints_qa_20260516`

Verification:

- `python -m py_compile scripts\run_domain_bootstrap_qa.py src\profile_bootstrap.py`
- `python -m pytest tests\test_domain_bootstrap_qa.py tests\test_profile_bootstrap.py -q`
  - `197 passed`
- `python -m pytest tests -q`
  - `1281 passed, 2 subtests passed`

Lesson:

- Profile contracts can identify a missing source-coordinate capability, but a
  proposed predicate is not architecture until the compile populates it and the
  query layer can retrieve it without over-bound constants.
- Common English slot words require a literal-value safety rule: first execute
  the original query, and only promote the word to a variable after the original
  query misses.
- The transfer-level repair is not a local parser. It is a source-coordinate
  slot contract, deterministic source-coordinate discovery, and safe
  placeholder normalization over structural slot words.
- Helper retirement is still holding: the accepted safe slice reached `7 / 0 /
  1` with helper rows `0`, and the remaining residual is a real compile-surface
  role-bearing capacity gap rather than a reason to revive native helpers.

Next pressure:

- Run the accepted safe no-helper path on the paired pressure slice again, then
  move toward a broader native corpus no-helper rerun only after confirming this
  source-coordinate repair does not regress the sensor/equipment side.
- Keep watching deterministic placeholder expansion: add only structural slot
  words that recur across domains, not local answer vocabulary.

## HR-026 - Three-Fixture Safe Query Replay Holds Helper Retirement

Date: 2026-05-16

Before:

- HR-025 accepted the safer source-coordinate/query-normalization state after
  rejecting the preemptive `title` normalization shortcut.
- The open risk was regression on the paired no-helper pressure slice: source
  coordinate repairs could help one fixture while adding query noise or losing
  resolution elsewhere.

Prediction:

- If the new query layer is structural, a three-fixture replay should preserve
  zero helper rows and recover source-coordinate/title pressure without
  lowering count/roster or equipment QA.
- If the new source-coordinate hints are too broad, the replay should show
  answer drift or judge uncertainty from excessive source-record rows.

Intervention:

- Replayed the accepted three-fixture compile root with:
  - helper companion row limit at default `0`,
  - legacy native helper adapters disabled,
  - literal-safe placeholder normalization,
  - deterministic source-coordinate hint queries,
  - core-local item-detail projection over descriptive `item_id/2` rows.

After:

| Fixture | Questions | Exact | Partial | Miss | Helper rows | Failure surface |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| count/roster pressure | 8 | 8 | 0 | 0 | 0 | n/a |
| equipment/source-fidelity pressure | 8 | 7 | 0 | 1 | 0 | `compile_surface_gap=1` |
| custody/source-coordinate pressure | 8 | 8 | 0 | 0 | 0 | n/a |
| Total | 24 | 23 | 0 | 1 | 0 | `compile_surface_gap=1` |

- The source-coordinate/title repair transferred across the replay without
  helper delivery.
- The remaining miss is the same structural equipment-specification compile gap:
  the source states a device specification, but the accepted compile root does
  not expose a direct specification attribute row.

Artifacts:

- `docs/data/helper_residue/three_fixture_safequery_qa_20260516.json`
- `docs/data/helper_residue/three_fixture_safequery_qa_20260516.md`
- `tmp/helper_residue_three_fixture_safequery_qa_20260516`

Verification:

- Batch QA:
  - `python scripts\run_domain_bootstrap_qa_batch.py --dataset-root datasets\story_worlds --compile-root tmp\helper_residue_three_fixture_accepted_compile_20260516 --out-root tmp\helper_residue_three_fixture_safequery_qa_20260516 --fixture count_composition_roster --fixture industrial_sensor_clock_correction --fixture probate_storage_access_register --limit 8 --model qwen/qwen3.6-35b-a3b --base-url https://openrouter.ai/api/v1 --lanes 3 --timeout 420 --no-cache --out-json docs\data\helper_residue\three_fixture_safequery_qa_20260516.json --out-md docs\data\helper_residue\three_fixture_safequery_qa_20260516.md`
  - `23 / 0 / 1`, helper rows `0`, runtime load errors `0`, write proposals `0`.

Lesson:

- The helper-retirement path is no longer "remove helpers and hope." It now has
  three replacement layers:
  - compile/profile contracts for source roles, specifications, and source
    coordinates,
  - deterministic query normalization with literal-value safety,
  - small core-local projections for structural item detail surfaces.
- The remaining work is compile-surface preservation, not helper resurrection:
  when the source states an attribute but the compile keeps it only inside a
  text atom, no amount of helper-budget tuning should be treated as the
  architectural fix.

Next pressure:

- Recompile the equipment/source-fidelity pressure under the current profile and
  compile-surface invariants, then rerun the three-fixture smoke. If the single
  residual clears without helper rows, move to a broader native no-helper
  corpus rerun.

## HR-027 - Fresh Equipment Recompile Rejected As Compile-Variance Evidence

Date: 2026-05-16

Before:

- HR-026 left the three-fixture no-helper replay at `23 / 0 / 1`, helper rows
  `0`.
- The only residual was an equipment/source-fidelity compile gap in the accepted
  compile root: a source-stated specification remained in source text rather
  than a direct specification/attribute surface.

Prediction:

- If the current profile and compile-surface invariants are sufficient, a fresh
  equipment recompile should preserve the specification as a direct attribute
  surface and recover the residual without helper rows.
- If compile stability is the real pressure, a fresh draw may move sideways or
  regress even though the query/runtime layer is cleaner.

Intervention:

- Recompiled the equipment/source-fidelity fixture under current profile review,
  source-record ledger facts, flat+plan passes, and focused pass schema.
- Ran the first eight QA rows with helper companions disabled by default.

After:

| Run | Questions | Exact | Partial | Miss | Helper rows | Result |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| HR-026 accepted compile root | 8 | 7 | 0 | 1 | 0 | keep |
| Fresh current recompile | 8 | 4 | 0 | 4 | 0 | reject |

- The fresh compile profile scored `0.778`, with repeated id-only record
  pressure and four QA misses.
- This draw is not a candidate for the no-helper native baseline.
- The failure supports the compile-stability finding: once helpers are off, the
  bottleneck is whether a single compile draw preserves all expected direct
  surfaces, not whether the query layer can compensate.

Artifacts:

- `docs/data/helper_residue/equipment_current_compile_20260516.json`
- `docs/data/helper_residue/equipment_current_compile_20260516.md`
- `docs/data/helper_residue/equipment_current_qa_20260516.json`
- `docs/data/helper_residue/equipment_current_qa_20260516.md`
- `tmp/helper_residue_equipment_current_compile_20260516`
- `tmp/helper_residue_equipment_current_qa_20260516`

Verification:

- Compile summary: candidate predicates `30`, admitted clauses `176`, skipped
  clauses `23`, rough score `0.778`.
- QA summary: `4 / 0 / 4`, helper rows `0`, runtime load errors `0`, write
  proposals `0`.

Lesson:

- A bad single draw should not be repaired midstream with fixture-specific
  parsing. It should be rejected as compile-variance evidence.
- The helper-retirement replacement stack is doing its job when it refuses to
  hide a poor compile behind compatibility adapters.

Next pressure:

- Commit the safe query/runtime and journal work.
- Treat the remaining path to native no-helper restamp as a compile-stability
  problem: either use a known-good accepted compile root for immediate smoke, or
  design a small compile-quality gate/consensus pass before broader native
  corpus measurement.

## HR-028 - Compile Quality Gate For Native No-Helper Stamp Prep

Date: 2026-05-16

Before:

- HR-027 showed that a fresh compile draw can regress badly even when helpers
  stay off and the query layer is cleaner.
- The next broader native no-helper stamp needs a stop/go point between compile
  and QA, otherwise a weak compile draw can waste QA spend and confuse the
  empirical baseline.

Prediction:

- A lightweight, fixture-free compile gate can separate accepted/rejected draw
  shapes using profile/compile health signals already emitted by the compiler:
  parsed OK, rough score, risk count, admitted rows, skipped-share reporting,
  and explicit hold reasons.
- The gate should pass the accepted three-fixture compile root while holding the
  rejected equipment draw from HR-027.

Intervention:

- Added `--quality-gate` to `scripts/run_domain_bootstrap_file_batch.py`.
- Added `--quality-gate-fail-on-hold` so stamp automation can stop before QA
  when any fixture is held.
- Extended compile summaries to preserve audit signals:
  - repeated structure count,
  - id-only record refs,
  - role-mismatch refs,
  - frontier unknown positive predicate refs,
  - generic predicate count.
- Gate defaults:
  - minimum rough score `0.775`,
  - maximum risk count `5`,
  - parsed OK required,
  - admitted rows required.

After:

| Compile root | Gate result | Passed | Held | Hold reason |
| --- | --- | ---: | ---: | --- |
| accepted three-fixture root | pass | 3 | 0 | n/a |
| rejected equipment draw | hold | 0 | 1 | `risk_count>5` |

- `--quality-gate-fail-on-hold` returns `0` for the accepted root and `2` for
  the rejected draw.
- The gate is intentionally a stamp-readiness gate, not a correctness oracle:
  a passing compile still needs no-helper QA; a held compile should be reviewed
  or redrawn rather than patched with helper adapters.

Artifacts:

- `scripts/run_domain_bootstrap_file_batch.py`
- `tests/test_domain_bootstrap_file_batch.py`
- `docs/data/helper_residue/compile_quality_gate_three_fixture_20260516.json`
- `docs/data/helper_residue/compile_quality_gate_three_fixture_20260516.md`
- `docs/data/helper_residue/compile_quality_gate_equipment_rejected_20260516.json`
- `docs/data/helper_residue/compile_quality_gate_equipment_rejected_20260516.md`

Verification:

- `python -m py_compile scripts\run_domain_bootstrap_file_batch.py`
- `python -m pytest tests\test_domain_bootstrap_file_batch.py tests\test_domain_bootstrap_qa_batch.py -q`
  - `8 passed`
- Accepted root gate:
  - `python scripts\run_domain_bootstrap_file_batch.py ... --summarize-existing --quality-gate --quality-gate-fail-on-hold`
  - exit `0`
- Rejected draw gate:
  - `python scripts\run_domain_bootstrap_file_batch.py ... --summarize-existing --quality-gate --quality-gate-fail-on-hold`
  - exit `2`

Lesson:

- Native no-helper stamping needs a two-stage protocol:
  1. compile and gate the draw;
  2. only then run no-helper QA.
- This keeps the stamp from mixing architectural movement with compile-variance
  wobble. A held draw is evidence, not a repair target.

Next pressure:

- Review this gate, then launch the broader native no-helper stamp with:
  - compile batch using `--quality-gate --quality-gate-fail-on-hold`,
  - no-helper QA batch only for passing compile roots,
  - no helper companion rows,
  - no legacy native adapters,
  - no mid-stamp repairs.
