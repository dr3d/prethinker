# Greywell Pipeline Progress Journal

Fixture id: `greywell_pipeline`

This journal records durable research findings for this promoted incoming fixture.
Generated run artifacts may live under `tmp/`; lessons and artifact references belong here.

## GP-000 - Fixture Admission

Date: 2026-05-04

Evidence lane: `fixture_admission`

Source admitted from archived intake batch: `C:\prethinker_tmp_archive\incoming_zip_batch_20260504_171258\incoming_unzipped_20260504_171258\greywell_pipeline`

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

## GP-001 - Promoted Cold Baseline

Date: 2026-05-04

Evidence lane: `cold_unseen_baseline`

Mode: promoted story-world cold compile plus evidence-bundle QA over all `25`
questions, followed by failure-surface classification for the non-exact rows.

Artifacts:

- Compile: `tmp/story_world_cold_runs/greywell_pipeline/`
- First QA: `tmp/story_world_cold_qa/greywell_pipeline/`
- Failure classification: `tmp/story_world_failure_classification_zip/greywell_pipeline/`
- Batch scorecard: `tmp/story_world_zip_baseline_summaries/scorecard.md`
- Repair targets: `tmp/story_world_zip_baseline_summaries/compile_repair_targets.md`

Result:

```text
compile:            163 admitted / 8 skipped
compile health:     healthy
semantic progress:  low / continue
first QA:           22 exact / 1 partial / 2 miss
classified rollup:  22 exact / 2 partial / 1 miss
failure surfaces:   1 compile_surface_gap, 1 hybrid_join_gap, 1 answer_surface_gap
write proposals:    0
runtime errors:     0
```

Lesson:

Greywell is the strongest cold baseline in this zip batch. Its residual errors
are split across compile, join, and answer surfaces, which makes it a good
anti-overfit check: a repair that only expands source acquisition may not move
all remaining rows.

## GP-002 - Operational Record Status Lens Trial

Date: 2026-05-05

Evidence lane: `operational_record_status_lens`

Artifacts:

- Compile: `tmp/story_world_operational_record_variant/greywell_pipeline/`
- QA: `tmp/story_world_operational_record_variant_qa_full/greywell_pipeline/`
- Scorecard: `tmp/story_world_operational_record_variant_summaries/scorecard.md`
- Row gate: `tmp/story_world_operational_record_variant_summaries/row_gated_scorecard_plan.md`
- Selector: `tmp/story_world_operational_record_selector/greywell_pipeline-guarded_activation_operational_guard_selector.md`

Result:

```text
variant compile:      83 admitted / 21 skipped
variant QA:           23 exact / 1 partial / 1 miss
row-gated target:     accept q003, q012; reject q023; q025 unchanged
guarded selector:     24 exact / 1 partial / 0 miss
selected best rows:   25 / 25
```

Lesson:

This is the cleanest transfer win for the operational/status selector guard.
The compile health is poor, so the lens should not become global, but the
selector can safely harvest the operational rows that answer who isolated the
segment and current operational status while protecting the baseline
recommendations row.

## GP-003 - Baseline Readiness Selector Guard

Date: 2026-05-05

Evidence lane: `selector_baseline_readiness_guard`

Artifacts:

- Selector: `tmp/story_world_operational_record_selector_v3/greywell_pipeline-guarded_activation_baseline_readiness_guard_selector.md`
- Batch scorecard: `tmp/story_world_operational_record_selector_v3/scorecard.md`

Result:

```text
previous guarded selector: 24 exact / 1 partial / 0 miss; selected-best 25 / 25
readiness-guard selector: 24 exact / 1 partial / 0 miss; selected-best 25 / 25
delta:                    0 exact / 0 partial / 0 miss
```

Lesson:

Greywell stays the anti-overfit check: it was already at its per-row selector
upper bound, and the new baseline-readiness guard does not perturb it.
