# Ashgrove Permit Progress Journal

Fixture id: `ashgrove_permit`

This journal records durable research findings for this promoted incoming fixture.
Generated run artifacts may live under `tmp/`; lessons and artifact references belong here.

## AP-000 - Fixture Admission

Date: 2026-05-04

Evidence lane: `fixture_admission`

Source admitted from archived intake batch: `C:\prethinker_tmp_archive\incoming_zip_batch_20260504_171258\incoming_unzipped_20260504_171258\ashgrove_permit`

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

## AP-001 - Promoted Cold Baseline

Date: 2026-05-04

Evidence lane: `cold_unseen_baseline`

Mode: promoted story-world cold compile plus evidence-bundle QA over all `25`
questions, followed by failure-surface classification for the non-exact rows.

Artifacts:

- Compile: `tmp/story_world_cold_runs/ashgrove_permit/`
- First QA: `tmp/story_world_cold_qa/ashgrove_permit/`
- Failure classification: `tmp/story_world_failure_classification_zip/ashgrove_permit/`
- Batch scorecard: `tmp/story_world_zip_baseline_summaries/scorecard.md`
- Repair targets: `tmp/story_world_zip_baseline_summaries/compile_repair_targets.md`

Result:

```text
compile:            77 admitted / 1 skipped
compile health:     poor
semantic progress:  low / continue
first QA:           19 exact / 2 partial / 4 miss
classified rollup:  21 exact / 0 partial / 4 miss
failure surfaces:   2 compile_surface_gap, 2 hybrid_join_gap
write proposals:    0
runtime errors:     0
```

Lesson:

Ashgrove is a compact permit/deadline fixture with visible scoring volatility:
two rows that were non-exact in the first QA pass judged exact during the
classification rerun. Treat the classified rollup as the repair ledger, but
keep the first-pass score as the cold-contact score. The remaining durable
pressure is deadline/status arithmetic and helper join behavior, not unsafe
writes.
