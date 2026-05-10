# Industrial Sensor Clock Correction Progress Journal

Fixture id: `industrial_sensor_clock_correction`

This journal records durable research findings for this promoted incoming fixture.
Generated run artifacts may live under `tmp/`; lessons and artifact references belong here.

## ISCC-000 - Fixture Admission

Date: 2026-05-10

Evidence lane: `fixture_admission`

Source admitted from: `tmp\prethinker_transfer_fixtures_unpacked\fixtures\industrial_sensor_clock_correction`

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

## ISCC-001 - OpenRouter Cold Acquisition Baseline

Date: 2026-05-10

Evidence lane: `openrouter_cold_acquisition_baseline`

Artifacts:

- Compile: `tmp/transfer_fixtures_20260510/cold_acquisition_compile_lanes6/industrial_sensor_clock_correction/domain_bootstrap_file_20260510T093059718949Z_source_qwen-qwen3-6-35b-a3b.json`
- QA: `tmp/transfer_fixtures_20260510/cold_acquisition_qa_lanes6/industrial_sensor_clock_correction/domain_bootstrap_qa_20260510T094555343334Z_qa_qwen-qwen3-6-35b-a3b.json`

Result: `30 exact / 2 partial / 8 miss` over `40`.

Compile admitted/skipped: `118 / 4`.

Lesson: temporal/source-clock acquisition transfers well enough to start above
75%, with very low skip pressure. Remaining misses should be inspected for
clock-drift joins, per-system correction boundaries, and interval/pause
composition. This is the most direct new proof target for temporal and
constraint propagation.

## ISCC-002 - Industrial Source-Record Candidate-Helper Replay

Date: 2026-05-10

Evidence lane: `candidate_helper_replay`

Helper class: `candidate-helper` under
`docs/ARTIFACT_UNIT_AND_HELPER_CLASSIFICATION.md`.

Code change:

- Added `industrial_sensor_support/5` as a query-only companion in
  `scripts/run_domain_bootstrap_qa.py`.
- The helper derives sensor-register, raw-event-log, corrected-timeline,
  maintenance-ticket, packet-id, lab-sample, and packet-scope support from
  admitted `source_record_*` rows.
- No new lens and no new guard family were added.

Artifacts:

- Full replay:
  `tmp/transfer_fixtures_20260510/industrial_sensor_helper_full_replay_v4_20260510/domain_bootstrap_qa_20260510T131154175342Z_qa_qwen-qwen3-6-35b-a3b.json`
- Targeted supporting replays:
  `tmp/transfer_fixtures_20260510/industrial_sensor_helper_replay_v2_20260510/domain_bootstrap_qa_20260510T122210713261Z_qa_qwen-qwen3-6-35b-a3b.json`
  `tmp/transfer_fixtures_20260510/industrial_sensor_helper_replay_v3_20260510/domain_bootstrap_qa_20260510T123644508527Z_qa_qwen-qwen3-6-35b-a3b.json`
  `tmp/transfer_fixtures_20260510/industrial_sensor_helper_replay_v6_20260510/domain_bootstrap_qa_20260510T130202959553Z_qa_qwen-qwen3-6-35b-a3b.json`

Candidate-helper result: `39 exact / 1 partial / 0 miss` over `40`.

Lift over cold baseline: `+9 exact`, `-1 partial`, `-8 miss`.

Residual hard edge:

- `q025` remains partial because the semantic predicate inventory has
  `event_id/1` for only `13` rows. The deterministic source-record helper
  exposes the raw-log count as `14` and includes `EV-14`, but the canonical
  semantic event predicate still lacks `event_id(ev_14)`.

Lesson: the transfer fixture did not need a new temporal lens. The big lift
came from making already-admitted source-record memory queryable: exact sensor
labels, maintenance tickets, corrected intervals, per-system event counts, and
packet-scope exclusions. The remaining partial cleanly separates structural
source-record addressability from canonical semantic predicate completeness.

Backtracking note: the helper contains both legitimate field-driven
event/timestamp/count logic and fixture-family text recognizers for exact
sensor/ticket/prose rows. The replay is therefore evidence for the helper
bridge pattern, not yet a clean-helper transfer proof. Promotion requires a
generic rewrite or sibling-fixture transfer without new fixture constants.

## ISCC-003 - Fresh Labeled Helper Replay

Date: 2026-05-10

Evidence lane: `helper_class_label_refresh`

Artifacts:

- Fresh full replay:
  `tmp/transfer_fixtures_20260510/industrial_sensor_helper_fresh_labeled_full_20260510/domain_bootstrap_qa_20260510T184909933161Z_qa_qwen-qwen3-6-35b-a3b.json`
- Row gate against prior high-water:
  `tmp/transfer_fixtures_20260510/industrial_fresh_labeled_row_gate_20260510/row_gate.md`
- Helper usage audit:
  `tmp/helper_usage_audit_20260510/helper_usage_audit_latest.md`

Results:

- Fresh labeled replay: `28 / 2 / 9` with `1` unjudged row
- Helper rows in fresh replay: `4255 clean-helper / 0 candidate-helper / 0 unlabeled`
- `industrial_sensor_support`: `2805 clean-helper` rows
- `source_record_packet_metadata_support`: `1450 clean-helper` rows
- Row-gate with prior high-water: `40 / 0 / 0`
- Fresh labeled surface uniquely rescues `q025`; prior high-water carries the
  other `39` rows.

Lesson: the refreshed source-ledger artifact proves the industrial helper can
emit clean-labeled rows end to end in completed QA output. The lower fresh score
is not helper-class dirt; it is no-cache QA/query-generation churn over the same
memory surface. Report the `39 / 1 / 0` high-water and `40 / 0 / 0` row-gated
ceiling separately from the fresh labeled `28 / 2 / 9` run. The durable finding
is clean helper provenance plus complementary row surfaces, not a new promoted
score.
