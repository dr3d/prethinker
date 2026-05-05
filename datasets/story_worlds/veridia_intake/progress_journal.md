# Veridia Intake Progress Journal

Fixture id: `veridia_intake`

This journal records durable research findings for this promoted incoming fixture.
Generated run artifacts may live under `tmp/`; lessons and artifact references belong here.

## VI-000 - Fixture Admission

Date: 2026-05-04

Evidence lane: `fixture_admission`

Source admitted from archived intake batch: `C:\prethinker_tmp_archive\incoming_zip_batch_20260504_171258\incoming_unzipped_20260504_171258\veridia_intake`

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

## VI-001 - Promoted Cold Baseline

Date: 2026-05-04

Evidence lane: `cold_unseen_baseline`

Mode: promoted story-world cold compile over the turnstream source plus
evidence-bundle QA over all `23` questions, followed by failure-surface
classification for the non-exact rows.

Artifacts:

- Compile: `tmp/story_world_cold_runs/veridia_intake/`
- First QA: `tmp/story_world_cold_qa/veridia_intake/`
- Failure classification: `tmp/story_world_failure_classification_zip/veridia_intake/`
- Batch scorecard: `tmp/story_world_zip_baseline_summaries/scorecard.md`
- Repair targets: `tmp/story_world_zip_baseline_summaries/compile_repair_targets.md`

Result:

```text
compile:            66 admitted / 5 skipped
compile health:     healthy
semantic progress:  low / continue
first QA:           15 exact / 5 partial / 3 miss
classified rollup:  15 exact / 5 partial / 3 miss
failure surfaces:   3 compile_surface_gap, 4 hybrid_join_gap, 1 answer_surface_gap
write proposals:    0
runtime errors:     0
```

Lesson:

Veridia is the useful stenographer-adjacent fixture in this batch: a compact
turnstream with corrections, pending uncertainty, and budget authority. The
compile is healthy, but most remaining failures are hybrid/join rather than
pure source acquisition, so this should feed the stenographer and correction
state lanes after the batch is safely admitted.

## VI-002 - Operational Record Status Lens Trial

Date: 2026-05-05

Evidence lane: `operational_record_status_lens`

Artifacts:

- Compile: `tmp/story_world_operational_record_variant/veridia_intake/`
- QA: `tmp/story_world_operational_record_variant_qa/veridia_intake/`
- Scorecard: `tmp/story_world_operational_record_variant_summaries/scorecard.md`
- Row gate: `tmp/story_world_operational_record_variant_summaries/row_gated_scorecard_plan.md`
- Selector: `tmp/story_world_operational_record_selector/veridia_intake-guarded_activation_operational_guard_selector.md`

Result:

```text
variant compile:      45 admitted / 27 skipped
variant QA:           15 exact / 4 partial / 4 miss
row-gated target:     accept q007, q013, q014, q019, q022; reject q001, q009, q015, q018, q020
guarded selector:     16 exact / 6 partial / 1 miss
selected best rows:   21 / 23
```

Lesson:

Veridia confirms the stenographer-adjacent problem: operational rows can expose
pending/reversal/unresolved surfaces, but they can also conflict with
commit/hold judgment. The selector guard improves the row-level result, yet the
remaining frontier is explicit commit-readiness versus unresolved-process
status.

## VI-003 - Baseline Readiness Selector Guard

Date: 2026-05-05

Evidence lane: `selector_baseline_readiness_guard`

Artifacts:

- Selector: `tmp/story_world_operational_record_selector_v3/veridia_intake-guarded_activation_baseline_readiness_guard_selector.md`
- Batch scorecard: `tmp/story_world_operational_record_selector_v3/scorecard.md`

Result:

```text
previous guarded selector: 16 exact / 6 partial / 1 miss; selected-best 21 / 23
readiness-guard selector: 17 exact / 5 partial / 1 miss; selected-best 22 / 23
delta:                    +1 exact / -1 partial / 0 miss
```

Lesson:

The hold-pending row now stays with baseline when baseline is the structural top
and carries direct event-status/pending-action support. The unresolved row is
commit-readiness: Prethinker still needs a sharper distinction between "there
is a certified status" and "the process should commit it now."
