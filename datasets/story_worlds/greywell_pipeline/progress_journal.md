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
