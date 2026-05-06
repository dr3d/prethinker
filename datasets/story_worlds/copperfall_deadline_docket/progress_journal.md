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

## CFD-004 - Temporal Status/Deadline Transfer Rejection

Date: 2026-05-05

Evidence lane: `temporal_status_deadline_surface`

Mode: scoped temporal/status/deadline compile over the same source. The compile
asked for source-stated dates, event order, effective dates, original and
revised deadlines, filing dates, response/reply deadlines, stays, tolling or
non-tolling intervals, status-at-date facts, grace periods, and unresolved
temporal conditions. It did not use answer keys, oracle rows, failure labels,
or gold KB material during compile.

Artifacts:

- Compile:
  `tmp/temporal_status_deadline_runs/copperfall_deadline_docket/domain_bootstrap_file_20260506T005656146629Z_source_qwen-qwen3-6-35b-a3b.json`
- Targeted QA:
  `tmp/temporal_status_deadline_targeted_qa/copperfall_deadline_docket/domain_bootstrap_qa_20260506T005753214377Z_qa_qwen-qwen3-6-35b-a3b.json`
- Targeted failure classification:
  `tmp/temporal_status_deadline_failures/copperfall_deadline_docket/domain_bootstrap_qa_20260506T005753214377Z_qa_qwen-qwen3-6-35b-a3b_failure_surface_20260506T005837348308Z.json`
- Full QA:
  `tmp/temporal_status_deadline_fullqa/copperfall_deadline_docket/domain_bootstrap_qa_20260506T011040521274Z_qa_qwen-qwen3-6-35b-a3b.json`
- Full failure classification:
  `tmp/temporal_status_deadline_full_failures/copperfall_deadline_docket/domain_bootstrap_qa_20260506T011040521274Z_qa_qwen-qwen3-6-35b-a3b_failure_surface_20260506T011226035888Z.json`

Result:

```text
compile shape:                  100 admitted / 6 skipped, rough score 1.000
targeted temporal rows:          1 exact / 0 partial / 1 miss
targeted failure surfaces:       1 query-surface gap
full QA temporal candidate:      25 exact / 5 partial / 10 miss
journaled high-water comparison: 38 exact / 1 partial / 1 miss
full failure surfaces:           7 compile-surface gaps, 3 hybrid-join gaps, 5 query-surface gaps
write proposals:                 0
runtime errors:                  0
```

Lesson:

The temporal/status/deadline surface is rejected for Copperfall. It recovers
the original answer deadline (`q024`) but confuses Orion's later reply deadline
(`q034`) by querying the wrong 14-day deadline family. Full replay is much
worse than the existing high-water, so the next Copperfall move is not another
broad temporal compile. It needs deadline-family disambiguation in the query
planner or helper layer: original answer deadline, resumed answer deadline, and
later reply deadline must remain separate temporal families.

## CFD-005 - Deadline-Family Query Companion

Date: 2026-05-06

Evidence lane: `deadline_family_query_surface`

Mode: query-only companion retrieval over admitted `deadline_calculated/5`
rows. When a QA query touches one deadline calculation, the runtime now also
retrieves the sibling deadline table:
`deadline_calculated(Deadline, Type, StartDate, Duration, EndDate).` This is
query support over existing KB facts only. It does not read source prose, add
new facts, use answer keys for planning, or authorize writes.

Artifacts:

- Targeted q024/q034 replay:
  `tmp/deadline_family_companion_qa/copperfall_deadline_docket/domain_bootstrap_qa_20260506T012633272137Z_qa_qwen-qwen3-6-35b-a3b.json`
- Deadline-cluster replay:
  `tmp/deadline_family_companion_cluster_qa/copperfall_deadline_docket/domain_bootstrap_qa_20260506T012909203020Z_qa_qwen-qwen3-6-35b-a3b.json`
- Full QA replay:
  `tmp/deadline_family_companion_fullqa/copperfall_deadline_docket/domain_bootstrap_qa_20260506T013654291947Z_qa_qwen-qwen3-6-35b-a3b.json`
- Comparison:
  `tmp/deadline_family_companion_comparisons/copperfall_deadline_family_full.md`
- Failure classification:
  `tmp/deadline_family_companion_failures/copperfall_deadline_docket/domain_bootstrap_qa_20260506T013654291947Z_qa_qwen-qwen3-6-35b-a3b_failure_surface_20260506T013745775081Z.json`

Result:

```text
q024/q034 targeted replay:      2 exact / 0 partial / 0 miss
deadline cluster q024-q035:     11 exact / 1 partial / 0 miss
full QA before companion:       25 exact / 5 partial / 10 miss
full QA after companion:        30 exact / 5 partial / 5 miss
rescued rows:                   8
baseline-exact regressions:     0
failure surfaces after replay:  6 compile, 3 query, 1 hybrid
write proposals:                0
runtime errors:                 0
```

Lesson:

The compile already contained the correct reply-deadline row, but q034 queried
the neighboring answer-resumed deadline family. The query companion makes the
deadline family visible without hiding the original query mistake. This is a
good harness-level support pattern: when a predicate represents a family of
typed deadlines, retrieve the family table so the answer/judge surface can
distinguish `answer`, `response`, `reply`, `discovery`, and `dispositive`
deadlines. Copperfall is still below its older high-water, so the remaining
work is compile coverage plus narrower query joins, not another broad temporal
compile.

## CFD-006 - Status-at-Date Interval Support

Date: 2026-05-06

Evidence lane: `status_interval_query_surface`

Mode: query-only temporal support over admitted `case_status_at_date/3`
transition anchors. When a QA query asks for a concrete case/date status and
the exact date lookup misses, the harness now derives one transparent support
row from the latest prior admitted status anchor plus the next later anchor.
This is structural temporal interval support over compiled KB rows. It does
not read source prose, add durable facts, use answer keys for planning, or
authorize writes.

Artifacts:

- Status-band q011-q017 replay:
  `tmp/status_interval_support_qa/domain_bootstrap_qa_20260506T015302220204Z_qa_qwen-qwen3-6-35b-a3b.json`
- Full QA replay:
  `tmp/status_interval_support_fullqa/domain_bootstrap_qa_20260506T020047458491Z_qa_qwen-qwen3-6-35b-a3b.json`
- Comparison:
  `tmp/status_interval_support_comparisons/copperfall_status_interval.md`

Result:

```text
status band q011-q017:          5 exact / 1 partial / 1 miss
full QA before interval helper: 30 exact / 5 partial / 5 miss
full QA after interval helper:  35 exact / 4 partial / 1 miss
rescued rows:                   6
baseline-exact regressions:     0
failure surfaces after replay:  1 compile, 2 query, 2 hybrid
write proposals:                0
runtime errors:                 0
```

Lesson:

Sparse status anchors are not enough by themselves: questions usually ask for
interior dates. The new helper exposes the active interval implied by admitted
transition anchors and makes atom-surface drift visible through `ObservedCase`
and `CaseMatch` fields rather than hiding it. The remaining hard Copperfall
status rows are the stay overlay: `stayed` was not admitted as a status anchor,
so deriving it from docket/correction rows would be a future explicit
status-override surface, not a silent Python guess.
