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

## MPB-007 - Rationale/Contrast Older Transfer Diagnostic

Date: 2026-05-05

Evidence lane: `rationale_contrast_transfer`

Mode: focused rationale/contrast source-note compile over the older promoted
fixture, followed by a tiny targeted QA probe on report authorship and
counterfactual objection rows.

Artifacts:

- Compile:
  `tmp/story_world_rationale_contrast_variant_older/meridian_permit_board/domain_bootstrap_file_20260505T121132429657Z_source_qwen-qwen3-6-35b-a3b.json`
- Targeted QA:
  `tmp/story_world_rationale_contrast_qa_older_targeted/meridian_permit_board/domain_bootstrap_qa_20260505T121446323770Z_qa_qwen-qwen3-6-35b-a3b.json`

Result:

```text
target rows:          2
targeted QA:          2 exact / 0 partial / 0 miss
failure surfaces:     none
write proposals:      0
runtime load errors:  0
compile shape:        79 admitted / 1 skipped, rough profile score 1.000
```

Lesson:

The probe is clean but too small to claim broad transfer. Keep Meridian in the
larger helper/query and source-surface lanes; this run mainly says the
rationale/contrast lens did not disturb the report-authorship and
counterfactual-objection rows it was asked to cover.

## MPB-008 - Rule Interpretation/Application Full-40 Lift

Date: 2026-05-05

Evidence lane: `rule_interpretation_application_surface`

Mode: scoped source-surface compile over the same source with guidance to
preserve source-stated rule text, controlling interpretations, applicant or
property being tested, activation conditions, eligibility/applicability
results, exceptions, corrections, and consequences. This run did not use answer
keys, oracle rows, failure labels, or gold KB material during compile.

Artifacts:

- Compile:
  `tmp/rule_interpretation_application_runs/meridian_permit_board/domain_bootstrap_file_20260505T203403256220Z_source_qwen-qwen3-6-35b-a3b.json`
- Targeted QA:
  `tmp/rule_interpretation_application_qa/meridian_permit_board/domain_bootstrap_qa_20260505T203759072306Z_qa_qwen-qwen3-6-35b-a3b.json`
- Full QA:
  `tmp/rule_interpretation_application_fullqa/meridian_permit_board/domain_bootstrap_qa_20260505T205339596169Z_qa_qwen-qwen3-6-35b-a3b.json`
- Failure classification:
  `tmp/rule_interpretation_application_failures/meridian_permit_board/domain_bootstrap_qa_20260505T205339596169Z_qa_qwen-qwen3-6-35b-a3b_failure_surface_20260505T205410875691Z.json`
- Comparison:
  `tmp/rule_interpretation_application_comparisons/meridian_rule_interp_comparison.md`

Result:

```text
compile shape:        80 admitted / 12 skipped, rough profile score 0.889
targeted repair rows: 4 exact / 0 partial / 0 miss
full QA candidate:    39 exact / 1 partial / 0 miss
baseline comparison:  26 exact / 10 partial / 4 miss
rescued rows:         14
baseline regressions: 0
failure surfaces:     1 compile-surface gap
write proposals:      0
runtime errors:       0
```

Lesson:

This is the strongest current source-surface acquisition result on Meridian.
The scoped rule-interpretation/application surface rescues materials,
shared-parking approval, REO classification, codified-law status, and several
rule-consequence/compliance rows without losing a baseline exact row. The
remaining partial is `q007`, where Lot 12's existing use still lacks a direct
lot-to-building/person linkage. Treat this as a strong Meridian-local compile
candidate and a transfer candidate for unlike rule/application fixtures, not
yet as a global default.
