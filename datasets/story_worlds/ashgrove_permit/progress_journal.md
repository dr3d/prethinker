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

## AP-002 - Operational Record Status Lens Trial

Date: 2026-05-05

Evidence lane: `operational_record_status_lens`

Mode: `operational_record_status_strategy_v1` compile context plus full QA and
baseline-vs-candidate selector comparison.

Artifacts:

- Compile: `tmp/story_world_operational_record_variant/ashgrove_permit/`
- QA: `tmp/story_world_operational_record_variant_qa/ashgrove_permit/`
- Scorecard: `tmp/story_world_operational_record_variant_summaries/scorecard.md`
- Row gate: `tmp/story_world_operational_record_variant_summaries/row_gated_scorecard_plan.md`
- Selector: `tmp/story_world_operational_record_selector/ashgrove_permit-guarded_activation_operational_guard_selector.md`

Result:

```text
variant compile:      129 admitted / 0 skipped
variant QA:           21 exact / 4 partial / 0 miss
row-gated target:     accept q006, q015, q016, q017; reject q018, q022
guarded selector:     21 exact / 3 partial / 1 miss
selected best rows:   23 / 25
```

Lesson:

The operational lens removes the permit-status misses but introduces
answer-surface partials on rationale/counterfactual rows. It is a row-level
candidate, not a global compile default. The selector uncertainty guard helps
by sending operational/status rows to activation when a competing mode has
specialized record-state evidence.

## AP-003 - Baseline Readiness Selector Guard

Date: 2026-05-05

Evidence lane: `selector_baseline_readiness_guard`

Mode: selector-only replay over frozen baseline and operational-record QA
artifacts. No source recompilation or new QA generation.

Artifacts:

- Selector: `tmp/story_world_operational_record_selector_v3/ashgrove_permit-guarded_activation_baseline_readiness_guard_selector.md`
- Batch scorecard: `tmp/story_world_operational_record_selector_v3/scorecard.md`

Result:

```text
previous guarded selector: 21 exact / 3 partial / 1 miss; selected-best 23 / 25
readiness-guard selector: 21 exact / 3 partial / 1 miss; selected-best 23 / 25
delta:                    0 exact / 0 partial / 0 miss
```

Lesson:

Ashgrove remains the permit-deadline selector pressure case. The new baseline
readiness guard does not move its score; the remaining misses are a deadline
filing-vs-completion confusion and a cause/rationale row where structural
volume still overvalues the operational lens.

## AP-004 - Question-Act Selector Guard

Date: 2026-05-05

Evidence lane: `selector_question_act_guard`

Artifacts:

- Selector: `tmp/story_world_operational_record_selector_v4/ashgrove_permit-guarded_activation_question_act_guard_selector.md`
- Batch scorecard: `tmp/story_world_operational_record_selector_v4/scorecard.md`

Result:

```text
previous readiness selector: 21 exact / 3 partial / 1 miss; selected-best 23 / 25
question-act selector:       22 exact / 3 partial / 0 miss; selected-best 24 / 25
delta:                       +1 exact / 0 partial / -1 miss
```

Lesson:

The request-filing guard fixes the AP-003 tender row: a question asking whether
an inspection request was filed on time after reinstatement needs request,
reinstatement, and threshold evidence, not completion-window evidence. The
remaining selector miss is cause/rationale: structural row volume still prefers
the operational lens even when baseline has the explicit inspector-note cause.
