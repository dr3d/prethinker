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

## FS-004 - Complete Selector Guard

Date: 2026-05-05

Evidence lane: `selector_complete_guard`

Artifacts:

- Selector: `tmp/story_world_operational_record_selector_v7/fenmore_seedbank-guarded_activation_complete_selector.md`
- Batch scorecard: `tmp/story_world_operational_record_selector_v7/scorecard.md`

Result:

```text
previous surface-specificity selector: 22 exact / 1 partial / 2 miss; selected-best 24 / 25
complete selector:                     22 exact / 2 partial / 1 miss; selected-best 25 / 25
delta:                                 0 exact / +1 partial / -1 miss
```

Lesson:

The split-rationale row now selects the best available mode. A why/split/vault
question needs the actual split and lot-condition surface rather than only a
generic vault-assignment rule. The remaining miss is an upper-bound limitation:
neither baseline nor operational-record mode contains the conservation rationale
needed for an exact answer.

## FS-005 - Rationale/Contrast Row-Level Lens

Date: 2026-05-05

Evidence lane: `rationale_contrast_source_note_lens`

Artifacts:

- Compile: `tmp/story_world_fenmore_rationale_contrast_variant/domain_bootstrap_file_20260505T041446371503Z_source_qwen-qwen3-6-35b-a3b.md`
- Full QA: `tmp/story_world_fenmore_rationale_contrast_qa_full/domain_bootstrap_qa_20260505T042253297606Z_qa_qwen-qwen3-6-35b-a3b.md`
- Selector: `tmp/story_world_fenmore_rationale_contrast_selector/fenmore_seedbank-guarded_activation_rationale_selector_v4.md`

Result:

```text
rationale/contrast compile alone: 17 exact / 1 partial / 7 miss
selector over baseline + operational + rationale: 24 exact / 1 partial / 0 miss
selected-best rows: 25 / 25
perfect selector upper bound: 24 exact / 1 partial / 0 miss
```

Lesson:

The remaining Vault 4 miss was a source-note rationale gap, not a selector
choice gap. A narrow rationale/contrast lens admitted the curator note surface
needed to distinguish conservation backup from viability concern, but the same
compile is much weaker globally. The harness gain is row-level: explicit source
notes are valuable when the question asks for rationale or contrast, while
collector identity and failed-viability hypotheticals must be protected by
direct collector and threshold/storage policy surfaces.

## FS-006 - Object/State/Custody Surface Boundary and Deaccession Guard

Date: 2026-05-05

Evidence lane: `object_state_custody_surface`

Mode: scoped source-surface compile with the same reason-named object/state/
custody acquisition contract used in transfer testing. The compile asked for
current state, condition, location, custody/ownership, storage placement,
transition events, viability or condition rationale, final status, and
chain-of-events rows. It did not use answer keys, oracle rows, failure labels,
or gold KB material during compile.

Artifacts:

- Compile:
  `tmp/object_state_custody_runs/fenmore_seedbank/domain_bootstrap_file_20260505T231906010069Z_source_qwen-qwen3-6-35b-a3b.json`
- Targeted QA:
  `tmp/object_state_custody_judged_qa/fenmore_seedbank/domain_bootstrap_qa_20260505T232432633642Z_qa_qwen-qwen3-6-35b-a3b.json`
- Targeted failure classification:
  `tmp/object_state_custody_failures/fenmore_seedbank/domain_bootstrap_qa_20260505T232432633642Z_qa_qwen-qwen3-6-35b-a3b_failure_surface_20260505T232545640824Z.json`
- Full QA:
  `tmp/object_state_custody_fullqa/fenmore_seedbank/domain_bootstrap_qa_20260505T233422942262Z_qa_qwen-qwen3-6-35b-a3b.json`
- Surface roster comparison:
  `tmp/object_state_custody_comparisons/fenmore_surface_roster_comparison.md`
- Selector after guard:
  `tmp/object_state_custody_selector/fenmore_surface_roster_guarded_activation_deaccession_guard.md`

Result:

```text
compile shape:                 48 admitted / 6 skipped, rough score 0.889
targeted QA:                   1 exact / 2 partial / 2 miss
targeted failure surfaces:      3 compile-surface gaps, 1 query-surface gap
full QA candidate:              12 exact / 3 partial / 10 miss
baseline comparison:            20 exact / 1 partial / 4 miss
candidate rescues:              q019, q024
candidate baseline regressions: 10 exact rows
four-surface upper bound:       25 exact / 0 partial / 0 miss
guarded selector before guard:  24 exact / 1 partial / 0 miss
guarded selector after guard:   25 exact / 0 partial / 0 miss
selector errors:                0
```

Lesson:

This broad object/state/custody acquisition shape is rejected as a global
Fenmore compile. It is too lossy on collector, transfer, and policy rows.
However, it contributed the missing deaccession-yet status surface for `q024`.
The new reason-named selector guard is
`deaccession-yet question needs explicit scheduled/not-formally-completed status surface rather than broad lot-history volume`.
With that guard, the selector reaches the full frozen-artifact upper bound
(`25 / 0 / 0`) across baseline, operational, rationale, and object/state
artifacts. The instrument lesson is pegboard, not bigger bag: conservation
rationale, operational threshold/status, and deaccession-yet status are
separate hooks.
