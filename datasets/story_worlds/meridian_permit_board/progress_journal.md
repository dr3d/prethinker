# Meridian Permit Board Progress Journal

Fixture id: `meridian_permit_board`

This journal records durable research findings for the Meridian incoming
fixture. Generated run artifacts may live under `tmp/`; the lessons and artifact
references belong here.

## MPB-000 - Fixture Admission

Date: 2026-05-04

Evidence lane: `fixture_admission`

Source admitted from: `tmp/incoming_staged/meridian_permit_board`

Files admitted:

- `source.md` / `story.md`
- `fixture_notes.md`
- `qa.md`
- `qa_questions.jsonl`
- `oracle.jsonl`
- `qa_authored_with_answers.jsonl`

Benchmark discipline:

- `source.md`/`story.md` is the only cold compile source.
- `oracle.jsonl`, `qa_authored_with_answers.jsonl`, `qa.md`, and
  `fixture_notes.md` are scoring/review assets, not compile context.
- No Python source-prose interpretation is allowed.

## MPB-001 - Scoped-Evidence Incoming Smoke

Date: 2026-05-04

Evidence lane: `cold_unseen`

Mode: scoped compile repair plus evidence-bundle context filtering.

Artifacts:

- Scoped-evidence scorecard:
  `tmp/incoming_smoke_summaries_scoped_evidence/scorecard.md`
- Meridian scoped-evidence QA:
  `tmp/incoming_cold_qa/meridian_permit_board_scoped_use_repair_evidence_first10/domain_bootstrap_qa_20260504T144613150328Z_qa_qwen-qwen3-6-35b-a3b.json`

Result:

- Compile: `169` admitted operations, `4` skips.
- Compile health: `healthy`.
- QA first-10: `9 exact / 1 partial / 0 miss`.
- Remaining non-exact: q006 river-centerline distance, classified
  `hybrid_join_gap`.
- Safety: `0` write-proposal rows.

Lesson:

Scoped compile plus evidence filtering removed misses but left a query/join
surface gap around spatial distance.

## MPB-002 - Spatial-Distance Compile Variant

Date: 2026-05-04

Evidence lane: `diagnostic_replay`

Mode: shifted spatial-distance compile variant.

Artifacts:

- Compile:
  `tmp/incoming_cold_runs/meridian_permit_board_spatial_distance_repair/domain_bootstrap_file_20260504T145736526896Z_source_qwen-qwen3-6-35b-a3b.json`
- QA:
  `tmp/incoming_cold_qa/meridian_permit_board_spatial_distance_repair_first10/domain_bootstrap_qa_20260504T150834385210Z_qa_qwen-qwen3-6-35b-a3b.json`
- Overlay plan:
  `tmp/incoming_smoke_summaries_official_companion_overlay/compile_variant_overlay_plan.md`

Result:

- Variant first-10: `9 exact / 1 partial / 0 miss`.
- Rescued row: q006.
- Exact-protection row: q007 stays better on baseline/scoped-evidence.

Lesson:

Meridian is a row-variant selector fixture: the spatial-distance compile is
needed for q006, but baseline/scoped evidence must protect q007.

## MPB-003 - Variant Selector Calibration

Date: 2026-05-04

Evidence lane: `selector_calibration`

Artifacts:

- Variant selector training plan:
  `tmp/incoming_smoke_summaries_official_companion_overlay/variant_selector_training_plan.md`
- Volume-gate selector comparison:
  `tmp/incoming_variant_selector_runs/incoming-variant-volume-gate-v2.md`

Result:

- Meridian activation target: q006.
- Meridian exact-protection target: q007.
- Guarded activation plus volume gate selected `2/2` best Meridian rows.

Lesson:

Structural row count was overconfident on both Meridian calibration rows until
the selector learned to treat relaxed/broad row-volume dominance as uncertainty.

## MPB-004 - Requirement-Detail Selector Replay

Date: 2026-05-04

Evidence lane: `selector_calibration`

Artifact:

- `tmp/incoming_variant_selector_runs/meridian_guarded_activation_requirement_detail.json`

Result:

- Meridian held `2/2` best choices under the requirement-detail selector replay.

Lesson:

The requirement-detail guard did not perturb the Meridian row-volume fix.

## MPB-005 - Full First-10 Variant Selector Replay

Date: 2026-05-04

Evidence lane: `selector_calibration`

Artifact:

- `tmp/incoming_variant_selector_runs/meridian_guarded_activation_requirement_detail_first10.json`

Result:

- Meridian first-10 selected `10/10` best choices.
- QA verdict through selected modes: `10 exact / 0 partial / 0 miss`.
- Selector errors: `0`.

Lesson:

The row-gated selector can safely combine scoped-evidence and spatial-distance
compile views across the whole first-10 slice.

## MPB-006 - Promoted Story-World Full-40 Run

Date: 2026-05-04

Evidence lane: `cold_unseen_full40`

Mode: promoted story-world cold compile plus evidence-bundle QA, followed by
failure-surface classification for non-exact rows.

Artifacts:

- Scorecard: `tmp/story_world_full40_classified_scorecards/scorecard.md`
- Repair targets: `tmp/story_world_full40_classified_scorecards/compile_repair_targets.md`

Result:

- Compile: `126` admitted operations, `5` skips.
- Compile health: `healthy`.
- QA full-40 after classification merge: `27 exact / 8 partial / 5 miss`.
- Failure surfaces: `8` compile-surface gaps and `5` helper/query-join gaps.
- Safety: `0` write-proposal rows.

Lesson:

Meridian now separates into two repair lanes: source-surface coverage for
materials, existing use, codification, and rule consequences; and helper/query
composition for spatial/coverage computations and final rule-compliance joins.
