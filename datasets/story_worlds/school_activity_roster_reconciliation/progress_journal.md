# School Activity Roster Reconciliation Progress Journal

Fixture id: `school_activity_roster_reconciliation`

This journal records durable research findings for this promoted incoming fixture.
Generated run artifacts may live under `tmp/`; lessons and artifact references belong here.

## SARR-000 - Fixture Admission

Date: 2026-05-10

Evidence lane: `fixture_admission`

Source admitted from: `tmp\prethinker_transfer_fixtures_unpacked\fixtures\school_activity_roster_reconciliation`

Files admitted:

- `source.md` / `story.md`
- `fixture_notes.md`
- `qa.md`
- `qa_questions.jsonl`
- `oracle.jsonl`
- `qa_battery.json`

Benchmark discipline:

- `source.md`/`story.md` is the only cold compile source.
- `oracle.jsonl`, `qa_battery.json`, `qa.md`, and `fixture_notes.md` are scoring/review assets, not compile context.
- No Python source-prose interpretation is allowed.

## SARR-001 - OpenRouter Cold Acquisition Baseline

Date: 2026-05-10

Evidence lane: `openrouter_cold_acquisition_baseline`

Artifacts:

- Compile: `tmp/transfer_fixtures_20260510/cold_acquisition_compile_lanes6/school_activity_roster_reconciliation/domain_bootstrap_file_20260510T093253491068Z_source_qwen-qwen3-6-35b-a3b.json`
- QA: `tmp/transfer_fixtures_20260510/cold_acquisition_qa_lanes6/school_activity_roster_reconciliation/domain_bootstrap_qa_20260510T094547518412Z_qa_qwen-qwen3-6-35b-a3b.json`

Result: `21 exact / 3 partial / 16 miss` over `40`.

Compile admitted/skipped: `150 / 8`.

Lesson: this is the clear hard edge in the transfer batch. The compile admitted
many rows, so the low cold score is not a thin-source failure. The pressure is
roster versioning, count versus composition, role-scope exclusion, and temporary
assignment intervals. This is the first repair target for roster-state helper
transfer and constraint-style composition.

## SARR-002 - Roster-State Candidate-Helper Replay

Date: 2026-05-10

Evidence lane: `candidate_helper_replay`

Helper class: `candidate-helper` under
`docs/ARTIFACT_UNIT_AND_HELPER_CLASSIFICATION.md`.

Artifacts:

- Baseline compile reused: `tmp/transfer_fixtures_20260510/cold_acquisition_compile_lanes6/school_activity_roster_reconciliation/domain_bootstrap_file_20260510T093253491068Z_source_qwen-qwen3-6-35b-a3b.json`
- Full helper replay QA: `tmp/transfer_fixtures_20260510/school_roster_helper_full_replay_20260510/domain_bootstrap_qa_20260510T101631950299Z_qa_qwen-qwen3-6-35b-a3b.json`

Result: `28 exact / 2 partial / 10 miss` over `40`.

Lift from cold baseline: `+7 exact`, with no new compile and no new lens.

What changed:

- The roster-state companion now joins admitted `adult_role/2` rows with
  `role_counts_towards_ratio/2`, surfacing counted-adult membership for ratio
  questions.
- The companion now derives roster membership/count support from admitted
  deterministic source-record ledger rows when roster lists are present as
  normalized line atoms rather than LLM-admitted `student_group_assignment/3`
  rows.
- The source-record roster derivation resets at roster-version and section
  boundaries so superseded v2 group listings do not leak into v3 counts.

Rows rescued include v3 group counts, v3 Group B composition, ratio-counted
adults, driver ratio exclusion, medical coverage identity, and Section 9
referenced-but-not-reproduced sources.

Remaining hard edge: source-address and source-specific lookup rows. The
replay still misses section-number rendering (`Section 1.4` / `Section 6.1`),
physical retention location, driver license exact lookup, scanner-device exact
lookup, parent-observer permission interval, and pending return-scan status.
The next repair target is therefore not another roster lens; it is structural
source-address rendering and small source-record companions for policy/device/
location rows.

## SARR-003 - Source-Address Rendering Helper Replay

Date: 2026-05-10

Evidence lane: `clean_helper_plus_candidate_helper_replay`

Helper class: mixed. `source_record_section_display` is clean-helper substrate;
the roster-state companion remains candidate-helper pending helper audit.

Artifacts:

- Baseline compile reused: `tmp/transfer_fixtures_20260510/cold_acquisition_compile_lanes6/school_activity_roster_reconciliation/domain_bootstrap_file_20260510T093253491068Z_source_qwen-qwen3-6-35b-a3b.json`
- Full section-address replay QA: `tmp/transfer_fixtures_20260510/school_source_address_full_replay_20260510/domain_bootstrap_qa_20260510T102601735615Z_qa_qwen-qwen3-6-35b-a3b.json`

Result: `30 exact / 1 partial / 9 miss` over `40`.

Lift from cold baseline: `+9 exact`, with no new compile and no new lens.

What changed:

- A query-only source-record section companion renders admitted normalized
  section atoms such as `v_1_4_roster_v3_2026_04_15` and
  `v_6_1_temporary_in_day_assignment` as human section labels (`Section 1.4`,
  `Section 6.1`).
- This converted the two source-address rows from miss/partial to exact while
  preserving the same compile artifact.

Remaining hard edge after the replay:

- small source-record lookup companions for policy identifiers and role
  definitions (`SCO-CH-3`, chaperone authority text);
- physical location rows (`Activities Office filing cabinet 3, drawer 2`,
  `Marwick Hall room 206`);
- exact device/license identifiers embedded in headings or prose
  (`DEV-SCAN-07`, `CDL-MA-44291`);
- parent-observer permission interval and pending return-scan status.

This confirms the transfer fixture's original weakness was not a new roster
semantic lens. The next useful work is cold acquisition/source-address
companions for official packet metadata and embedded identifiers.

## SARR-004 - Packet Metadata Candidate-Helper And Wrapped-Line Ledger Refresh

Date: 2026-05-10

Evidence lane: `deterministic_ledger_refresh_plus_candidate_helper_replay`

Helper class: `candidate-helper`. The wrapped-line source-record ledger refresh
is deterministic acquisition work, but the packet metadata companion still
contains fixture-family literals and is not yet a clean-helper surface.

Artifacts:

- Refreshed compile artifact: `tmp/transfer_fixtures_20260510/school_source_record_refreshed_compile_20260510/domain_bootstrap_file_school_source_record_refreshed_20260510.json`
- Final full replay QA: `tmp/transfer_fixtures_20260510/school_final_full_replay_20260510/domain_bootstrap_qa_20260510T105505215114Z_qa_qwen-qwen3-6-35b-a3b.json`

Candidate-helper result: `40 exact / 0 partial / 0 miss` over `40`.

Lift from cold baseline: `+19 exact`, `-3 partial`, `-16 miss`.

What changed:

- The deterministic source-record ledger now preserves wrapped official prose
  lines that follow anchored/labeled records. This admitted previously missing
  addressability for adult lodging (`N. Park 206`) and audit-binder retention
  (`Activities Office filing cabinet 3, drawer 2`).
- The refreshed compile artifact preserved the original semantic compile rows
  and replaced only deterministic `source_record_*` facts from the improved
  ledger. No new LLM semantic compile was required.
- A query-only packet metadata companion surfaces exact display values and
  high-value source-record details from admitted source-record atoms:
  `CHMS-RSO-2026-T07`, `SCO-CH-3`, `DEV-SCAN-07`, `CDL-MA-44291`,
  observer permission scope, transport departure, pending return scans, and
  physical retention location.
- Domain companions now allow multiple source-record/helper companions to
  appear together, so source-address rows do not suppress roster-state rows.

Architectural lesson: this fixture was initially the weakest fresh transfer
fixture (`21 / 3 / 16`) and looked like a roster/composition frontier. The
candidate-helper replay shows the largest remaining pressure was deterministic
source addressability and queryability over already available packet structure.
This is a cold-acquisition/helper-substrate win, not lens growth, but the
helper-assisted saturation should not be reported as clean-helper architecture
until the packet metadata and roster helpers are audited, generalized, or
transfer-proven without fixture-shaped constants.

## SARR-005 - Packet Metadata Candidate Retirement

Date: 2026-05-11

Evidence lane: `helper_audit_retirement`

Artifacts:

- candidate audit:
  `tmp/transfer_fixtures_20260510/source_record_packet_metadata_candidate_audit_20260511.md`
- post-retirement cold audit:
  `tmp/transfer_fixtures_20260510/packet_metadata_retirement_cold_audit_20260511.json`

Code change:

- retired school roster/travel content-note rows from
  `source_record_packet_metadata_support`

Result:

- `source_record_packet_metadata_support` on this fixture now emits `22 clean /
  0 candidate / 0 unlabeled` rows in the cold-transfer helper audit

Lesson:

The packet metadata helper remains useful for clean identifiers such as policy,
device, accommodation, correction-notice, driver-license, and packet IDs. It no
longer carries candidate prose rows for role definitions, observer permission
scope, pending return scans, lodging, audit-binder retention, or transport
departure. Those surfaces remain legitimate memory pressures, but they need
domain helpers, deterministic ledgers, or explicit candidate reporting outside
the broad packet-metadata helper.

## SARR-006 - School Packet Notes Domain Migration

Date: 2026-05-11

Evidence lane: `candidate_helper_boundary_repair`

Artifacts:

- QA delta readout:
  `tmp/transfer_fixtures_20260510/packet_metadata_retirement_qa_delta_20260511.md`
- targeted judged replay:
  `tmp/transfer_fixtures_20260510/school_packet_notes_migration_targeted_judged_20260511/`
- post-migration helper audit:
  `tmp/transfer_fixtures_20260510/school_packet_notes_migration_cold_audit_20260511.json`

Code change:

- migrated three answer-bearing school packet prose rows into
  `roster_state_support` as explicitly candidate-labeled rows:
  `school_packet_policy_title`, `school_packet_retention_location`, and
  `school_packet_pending_item`

Result:

- targeted replay on `q003`, `q004`, and `q033`: `3 exact / 0 partial / 0 miss`
- `source_record_packet_metadata_support` remains clean-only in helper audit:
  `116 clean / 0 candidate / 0 unlabeled` across the cold transfer batch

Lesson:

The retirement was correct: packet metadata should not carry these domain prose
answers. But the rows are still useful for the school packet. Keeping them in
`roster_state_support` with `candidate-helper` labels restores answerability
without blurring the broad source-addressability helper.

## SARR-007 - School Packet Notes Second Migration

Date: 2026-05-11

Evidence lane: `candidate_helper_boundary_repair`

Artifacts:

- targeted judged replay:
  `tmp/transfer_fixtures_20260510/school_packet_notes_second_migration_targeted_v2_judged_20260511/`
- helper audit:
  `tmp/transfer_fixtures_20260510/school_packet_notes_second_migration_cold_audit_20260511.json`
- readout:
  `tmp/transfer_fixtures_20260510/school_packet_notes_second_migration_delta_20260511.md`

Code change:

- added additional candidate-helper rows to `roster_state_support` for:
  N. Park lodging room, bus departure time, A. Diaz observer interval,
  S-007 temporary-assignment source note, and scanner clock-audit status

Result:

- targeted replay on `q006`, `q009`, `q019`, `q021`, `q038`:
  `4 exact / 0 partial / 1 miss`
- exact: `q009`, `q019`, `q021`, `q038`
- remaining miss: `q006`
- `source_record_packet_metadata_support` remains clean-only:
  `116 clean / 0 candidate / 0 unlabeled` across the cold transfer batch

Lesson:

The domain-helper migration is working and the packet metadata boundary remains
clean. The remaining `q006` miss is not another prose row; it is an explicit
event-to-source linkage gap. The system has
`temporary_event_assignment(s_007, bridge_engineering, 2026_05_02_11_00,
2026_05_02_12_30)` and a candidate source-note row, but not a governed predicate
that links the temporary event directly to Section 6.1 / `SCH-2026-05-02-A`.
