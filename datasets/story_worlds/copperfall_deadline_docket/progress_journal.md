# Copperfall Deadline Docket Progress Journal

Fixture id: `copperfall_deadline_docket`

This journal records durable research findings for the Copperfall incoming
fixture. Generated run artifacts may live under `tmp/`; the lessons and artifact
references belong here.

## CFD-000 - Fixture Admission

Date: 2026-05-04

Evidence lane: `fixture_admission`

Source admitted from: `tmp/incoming_staged/copperfall_deadline_docket`

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

## CFD-001 - Incoming First-10 Smoke

Date: 2026-05-04

Evidence lane: `cold_unseen`

Mode: incoming standard first-10 smoke. Copperfall needed compact profile retry,
then compiled and QAed cleanly.

Artifacts:

- Scorecard: `tmp/incoming_smoke_summaries/scorecard.md`
- Scoped-evidence scorecard: `tmp/incoming_smoke_summaries_scoped_evidence/scorecard.md`

Result:

- Compile: `95` admitted operations, `12` skips.
- Compile health: `warning`.
- Profile fallback: `compact_profile_retry`.
- QA first-10: `10 exact / 0 partial / 0 miss`.
- Safety: `0` write-proposal rows.
- Semantic progress: low risk, `continue`.

Lesson:

Copperfall is a clean temporal-status/deadline smoke after compact profile retry.
It should stay in the incoming calibration set as a regression guard for profile
fallback recovery and deadline-status source coverage.

## CFD-002 - Promoted Story-World Full-40 Run

Date: 2026-05-04

Evidence lane: `cold_unseen_full40`

Mode: promoted story-world cold compile plus evidence-bundle QA, followed by
failure-surface classification for non-exact rows.

Artifacts:

- Scorecard: `tmp/story_world_full40_classified_scorecards/scorecard.md`
- Repair targets: `tmp/story_world_full40_classified_scorecards/compile_repair_targets.md`

Result:

- Compile: `129` admitted operations, `4` skips.
- Compile health: `warning`.
- Semantic progress: medium risk, `continue_only_with_named_expected_contribution`.
- QA full-40 after classification merge: `38 exact / 1 partial / 1 miss`.
- Failure surfaces: `1` compile-surface gap, `1` helper/query-join gap.
- Safety: `0` write-proposal rows.

Lesson:

Copperfall remains a strong temporal-status fixture beyond the first ten rows.
The remaining repairs are narrow: original-answer deadline source coverage and
Orion reply-deadline helper/query composition.

## CFD-003 - Rationale/Contrast Older Transfer Diagnostic

Date: 2026-05-05

Evidence lane: `rationale_contrast_transfer`

Mode: focused rationale/contrast source-note compile over the older promoted
fixture, followed by targeted QA on judge, status-at-date, correction, trial
effect, and clerk-note rows.

Artifacts:

- Compile:
  `tmp/story_world_rationale_contrast_variant_older/copperfall_deadline_docket/domain_bootstrap_file_20260505T121214309995Z_source_qwen-qwen3-6-35b-a3b.json`
- Targeted QA:
  `tmp/story_world_rationale_contrast_qa_older_targeted/copperfall_deadline_docket/domain_bootstrap_qa_20260505T122103307691Z_qa_qwen-qwen3-6-35b-a3b.json`

Result:

```text
target rows:          11
targeted QA:          7 exact / 2 partial / 2 miss
failure surfaces:     2 compile-surface gaps, 2 hybrid-join gaps
write proposals:      0
runtime load errors:  0
compile shape:        96 admitted / 0 skipped, rough profile score 0.750
```

Lesson:

The lens transfers to correction/status notes, including the stay effective-date
correction and clerk-note surface. The misses cluster later in the temporal
ledger, so the next Copperfall work is not more rationale prose; it is stronger
date/status continuation and helper/query composition for deadline effects.
