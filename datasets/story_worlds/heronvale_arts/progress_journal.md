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

## HA-002 - Operational Record Status Lens Trial

Date: 2026-05-05

Evidence lane: `operational_record_status_lens`

Artifacts:

- Compile: `tmp/story_world_operational_record_variant/heronvale_arts/`
- QA: `tmp/story_world_operational_record_variant_qa/heronvale_arts/`
- Scorecard: `tmp/story_world_operational_record_variant_summaries/scorecard.md`
- Row gate: `tmp/story_world_operational_record_variant_summaries/row_gated_scorecard_plan.md`
- Selector: `tmp/story_world_operational_record_selector/heronvale_arts-guarded_activation_operational_guard_selector.md`

Result:

```text
variant compile:      127 admitted / 24 skipped
variant QA:           19 exact / 6 partial / 0 miss
row-gated target:     accept q004, q009, q010, q011, q022; reject q006, q013, q015, q016, q017
guarded selector:     19 exact / 5 partial / 1 miss
selected best rows:   20 / 25
```

Lesson:

The lens finds application/correction/remedy rows but still confuses status and
hypothetical eligibility rows. Heronvale remains a hard selector calibration
fixture: row-gated upper bound is large, but no-oracle selection needs stronger
baseline protection for application-status and counterfactual rule rows.

## HA-003 - Baseline Readiness Selector Guard

Date: 2026-05-05

Evidence lane: `selector_baseline_readiness_guard`

Artifacts:

- Selector: `tmp/story_world_operational_record_selector_v3/heronvale_arts-guarded_activation_baseline_readiness_guard_selector.md`
- Batch scorecard: `tmp/story_world_operational_record_selector_v3/scorecard.md`

Result:

```text
previous guarded selector: 19 exact / 5 partial / 1 miss; selected-best 20 / 25
readiness-guard selector: 22 exact / 2 partial / 1 miss; selected-best 23 / 25
delta:                    +3 exact / -3 partial / 0 miss
```

Lesson:

This is the strongest transfer from the new guard. Naming the hazard as
baseline application/status and counterfactual rule support prevents the
selector from over-trusting broad operational-record evidence on eligibility
rows. The remaining misses are not the same hazard: they need entity mapping
and community-priority selection work.

## HA-004 - Surface Specificity Selector Guard

Date: 2026-05-05

Evidence lane: `selector_surface_specificity_guard`

Artifacts:

- Selector: `tmp/story_world_operational_record_selector_v5/heronvale_arts-guarded_activation_surface_specificity_selector.md`
- Batch scorecard: `tmp/story_world_operational_record_selector_v5/scorecard.md`

Result:

```text
previous question-act replay: 20 exact / 4 partial / 1 miss; selected-best 21 / 25
surface-specificity selector: 23 exact / 1 partial / 1 miss; selected-best 24 / 25
delta:                        +3 exact / -3 partial / 0 miss
```

Lesson:

Heronvale benefits from two new selector labels. Decision-status questions need
explicit decision surface rather than adjacent application/status evidence.
Priority questions need an explicit priority predicate rather than an
underlying condition predicate. The remaining miss is entity mapping for the
Poetry Circle as currently constituted.
