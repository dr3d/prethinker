# Fenmore Seedbank Progress Journal

Fixture id: `fenmore_seedbank`

This journal records durable research findings for this promoted incoming fixture.
Generated run artifacts may live under `tmp/`; lessons and artifact references belong here.

## FS-000 - Fixture Admission

Date: 2026-05-04

Evidence lane: `fixture_admission`

Source admitted from archived intake batch: `C:\prethinker_tmp_archive\incoming_zip_batch_20260504_171258\incoming_unzipped_20260504_171258\fenmore_seedbank`

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

## FS-001 - Promoted Cold Baseline

Date: 2026-05-04

Evidence lane: `cold_unseen_baseline`

Mode: promoted story-world cold compile plus evidence-bundle QA over all `25`
questions, followed by failure-surface classification for the non-exact rows.

Artifacts:

- Compile: `tmp/story_world_cold_runs/fenmore_seedbank/`
- First QA: `tmp/story_world_cold_qa/fenmore_seedbank/`
- Failure classification: `tmp/story_world_failure_classification_zip/fenmore_seedbank/`
- Batch scorecard: `tmp/story_world_zip_baseline_summaries/scorecard.md`
- Repair targets: `tmp/story_world_zip_baseline_summaries/compile_repair_targets.md`

Result:

```text
compile:            195 admitted / 4 skipped
compile health:     warning
semantic progress:  low / continue
first QA:           20 exact / 1 partial / 4 miss
classified rollup:  20 exact / 2 partial / 3 miss
failure surfaces:   5 compile_surface_gap
write proposals:    0
runtime errors:     0
```

Lesson:

Fenmore compiles a rich ledger surface and keeps the mapper quiet: no runtime
errors and no write proposals. The remaining failures are classified as
compile-surface gaps, so the next useful work is scoped acquisition of missing
accession/viability/storage details rather than selector prompting.

## FS-002 - Operational Record Status Lens Trial

Date: 2026-05-05

Evidence lane: `operational_record_status_lens`

Artifacts:

- Compile: `tmp/story_world_operational_record_variant/fenmore_seedbank/`
- QA: `tmp/story_world_operational_record_variant_qa/fenmore_seedbank/`
- Scorecard: `tmp/story_world_operational_record_variant_summaries/scorecard.md`
- Row gate: `tmp/story_world_operational_record_variant_summaries/row_gated_scorecard_plan.md`
- Selector: `tmp/story_world_operational_record_selector/fenmore_seedbank-guarded_activation_operational_guard_selector.md`

Result:

```text
variant compile:      171 admitted / 5 skipped
variant QA:           18 exact / 5 partial / 2 miss
row-gated target:     accept q015, q017, q019; reject q009, q012, q013, q025
guarded selector:     21 exact / 2 partial / 2 miss
selected best rows:   23 / 25
```

Lesson:

The lens helps threshold/status rows but weakens transfer/authorization and
hypothetical consequence rows. For conservation ledgers, operational-record
surface must not replace the richer baseline ledger unless a row-level selector
has evidence that the question asks for status, thresholds, or split rationale.

## FS-003 - Baseline Readiness Selector Guard

Date: 2026-05-05

Evidence lane: `selector_baseline_readiness_guard`

Artifacts:

- Selector: `tmp/story_world_operational_record_selector_v3/fenmore_seedbank-guarded_activation_baseline_readiness_guard_selector.md`
- Batch scorecard: `tmp/story_world_operational_record_selector_v3/scorecard.md`

Result:

```text
previous guarded selector: 21 exact / 2 partial / 2 miss; selected-best 23 / 25
readiness-guard selector: 22 exact / 1 partial / 2 miss; selected-best 24 / 25
delta:                    +1 exact / -1 partial / 0 miss
```

Lesson:

The guard correctly protects a hypothetical consequence row where baseline has
direct rule/status support and the operational candidate is broad fallback
surface. The remaining missed-best row is split rationale: the operational lens
has the better partial answer, but the selector still prefers baseline.
