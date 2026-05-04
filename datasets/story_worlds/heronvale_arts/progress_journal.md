# Heronvale Arts Progress Journal

Fixture id: `heronvale_arts`

This journal records durable research findings for this promoted incoming fixture.
Generated run artifacts may live under `tmp/`; lessons and artifact references belong here.

## HA-000 - Fixture Admission

Date: 2026-05-04

Evidence lane: `fixture_admission`

Source admitted from archived intake batch: `C:\prethinker_tmp_archive\incoming_zip_batch_20260504_171258\incoming_unzipped_20260504_171258\heronvale_arts`

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

## HA-001 - Promoted Cold Baseline

Date: 2026-05-04

Evidence lane: `cold_unseen_baseline`

Mode: promoted story-world cold compile plus evidence-bundle QA over all `25`
questions, followed by failure-surface classification for the non-exact rows.

Artifacts:

- Compile: `tmp/story_world_cold_runs/heronvale_arts/`
- First QA: `tmp/story_world_cold_qa/heronvale_arts/`
- Failure classification: `tmp/story_world_failure_classification_zip/heronvale_arts/`
- Batch scorecard: `tmp/story_world_zip_baseline_summaries/scorecard.md`
- Repair targets: `tmp/story_world_zip_baseline_summaries/compile_repair_targets.md`

Result:

```text
compile:            122 admitted / 23 skipped
compile health:     warning
semantic progress:  medium / continue_only_with_named_expected_contribution
first QA:           18 exact / 4 partial / 3 miss
classified rollup:  19 exact / 2 partial / 4 miss
failure surfaces:   5 compile_surface_gap, 1 hybrid_join_gap
write proposals:    0
runtime errors:     0
```

Lesson:

Heronvale is the batch's rule/eligibility pressure case. It compiled enough to
answer most rows, but the skip count and medium semantic-progress signal say
future passes need a named expected contribution. Most remaining classified
gaps are compile-surface acquisition, with one helper/join row.
