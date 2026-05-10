# Greenhouse Quarantine Progress Journal

Fixture id: `greenhouse_quarantine`

This journal records durable research findings for this promoted incoming fixture.
Generated run artifacts may live under `tmp/`; lessons and artifact references belong here.

## GQ-000 - Fixture Admission

Date: 2026-05-04

Evidence lane: `fixture_admission`

Source admitted from: `tmp/incoming/greenhouse_quarantine.zip`

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

## GQ-001 - First Full-40 Cold Baseline

Date: 2026-05-07

Evidence lane: `cold_unseen`

Score: `20 exact / 9 partial / 11 miss`

Artifacts:

- Compile: `tmp/incoming_10_cold_runs_20260507/greenhouse_quarantine`
- QA: `tmp/incoming_10_cold_qa_20260507/greenhouse_quarantine`

Boundary: `0` write proposals and `0` runtime load errors. This is an immediate repair frontier fixture.

## GQ-002 - Quarantine/Lot Status Candidate

Date: 2026-05-07

Evidence lane: `candidate_compile_mode`

Candidate context: `operational_record_status_strategy_v1` with
quarantine/lot-status emphasis.

Targeted non-exact replay: `14 exact / 4 partial / 2 miss` across the `20`
baseline non-exact rows. The candidate improved `15` rows, including disease
identity, plant counts, sample positive/negative counts, GH-5 movement interval,
Lot 5C no-overlap rationale, mistaken movement actor, subset quarantine counts,
current status split, status-at-date rows, and destruction supervisor/witness
distinction. It regressed one targeted partial row about Lot 5B lab-result
counting.

Full guardrail replay: `31 exact / 6 partial / 3 miss` across all `40` rows,
up from the baseline `20 / 9 / 11`. It improved `15` rows and regressed `4`
rows, mostly around Lot 5B elevation/lab-result and final no-further-action
details.

Artifacts:

- Candidate compile: `tmp/incoming_10_repair_greenhouse_context_v1`
- Targeted QA: `tmp/incoming_10_repair_greenhouse_context_v1_qa_nonexact`
- Full guardrail QA: `tmp/incoming_10_repair_greenhouse_context_v1_qa_full`
- Query-only status helper probe:
  `tmp/incoming_10_repair_greenhouse_status_interval_v1_qa`

Decision: strong candidate mode and likely row-gated selector input, not yet a
blind global default. The transferable lesson is explicit lot/subset/status
transition acquisition plus query-only interval support for sparse
`*_status(Entity, Status, Date)` anchors.

Selector follow-up:

- Structural selector:
  `tmp/incoming_10_candidate_mode_selectors/greenhouse_structural_selector.md`
  selected `27 exact / 5 partial / 8 miss` against a perfect available upper
  bound of `34 / 5 / 1`.
- Guarded activation selector:
  `tmp/incoming_10_candidate_mode_selectors/greenhouse_guarded_selector.md`
  selected `30 exact / 7 partial / 3 miss`, with `35/40` selected-best rows.

Decision update: guarded selection preserves most of the candidate gain while
protecting the worst candidate regressions. Remaining missed-best rows point to
sample-count completeness and split-lot count guards, especially Lot 3A sample
count, Lot 3B lab result, Lot 5C unmoved count, and final supervision/no-action
details.

## GQ-004 - Lot Count And Destruction Selector Guards

Date: 2026-05-07

Evidence lane: `candidate_mode_selector`

Guard additions: direct lot plant-count surface, split-lot never-quarantined
scope, status-elevation rationale, and destruction supervisor role/event
surface.

Full selector replay:
`tmp/incoming_10_candidate_mode_selectors/greenhouse_guarded_selector_v2.md`

Result: `33 exact / 6 partial / 1 miss`, with `39/40` rows choosing the best
available mode and `0` selector errors. The perfect available upper bound is
`34 exact / 5 partial / 1 miss`.

Lesson: the new guards recover the high-value candidate rows while avoiding the
known candidate regressions on status elevation, final no-action, and Lot 5B
lab-result counting. The remaining missed-best row is `q011`, a Lot 3B lab
result question where a simple "prefer richer lab_result evidence" rule would
also select the wrong mode for `q023` (Lot 5B lab result). Do not add a generic
lab-result selector guard from this evidence alone; the distinction still needs
a real semantic lens or a safer evidence-quality feature.

## GQ-005 - Baseline/Lot-Status Union Selector Lane

Date: 2026-05-07

Evidence lane: `deterministic_compile_union` plus `candidate_mode_selector`

Union compile:
`tmp/incoming_10_repair_greenhouse_union_v1/domain_bootstrap_file_20260507T195736517071Z_greenhouse-baseline-plus-lot-status_qwen-qwen3-6-35b-a3b.json`

Policy: no source prose was read and no new facts were inferred. The union
deduplicated mapper-admitted clauses from the cold baseline and quarantine/lot
status candidate compiles.

Full union replay:
`tmp/incoming_10_repair_greenhouse_union_v1_qa_full/domain_bootstrap_qa_20260507T200805359558Z_qa_qwen-qwen3-6-35b-a3b.json`

Union alone scored `32 exact / 5 partial / 3 miss`, so it is not a global
default. It did recover the initially affected greenhouse row and the Lot 3B
lab result, but regressed several Lot 5C count/status rows.

Three-mode selector replay:
`tmp/incoming_10_candidate_mode_selectors/greenhouse_union_guarded_selector_v2.md`

Result: `35 exact / 4 partial / 1 miss`, matching the perfect available upper
bound across baseline, lot-status candidate, and union modes. The selector
chose the best available mode on all `40/40` rows with `0` selector errors.

Guard additions: initially affected greenhouse needs greenhouse-status plus
exclusion/location surface; Lot 3B lab-result needs lab-result plus lot-status
context; Lot 5C placed-under-quarantine count needs mistaken-movement surface;
Lot 5C never-quarantined count must avoid the broader status-change union
surface.

Lesson: the earlier warning was right: a generic lab-result guard is unsafe.
The useful distinction is not "more lab_result rows" but a specific
question-surface bundle: Lot 3B lab-result joins to surrounding lot-status
context, while Lot 5C count questions depend on mistaken movement and
quarantine-scope boundaries.
