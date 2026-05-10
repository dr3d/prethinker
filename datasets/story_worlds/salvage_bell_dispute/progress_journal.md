# Salvage Bell Dispute Progress Journal

Fixture id: `salvage_bell_dispute`

This journal records durable research findings for this promoted incoming fixture.
Generated run artifacts may live under `tmp/`; lessons and artifact references belong here.

## SBD-000 - Fixture Admission

Date: 2026-05-04

Evidence lane: `fixture_admission`

Source admitted from: `tmp/incoming/salvage_bell_dispute.zip`

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

## SBD-001 - First Full-40 Cold Baseline

Date: 2026-05-07

Evidence lane: `cold_unseen`

Score: `27 exact / 7 partial / 6 miss`

Artifacts:

- Compile: `tmp/incoming_10_cold_runs_20260507/salvage_bell_dispute`
- QA: `tmp/incoming_10_cold_qa_20260507/salvage_bell_dispute`

Boundary: `0` write proposals and `0` runtime load errors. This is a mid-pack cold transfer fixture.

## SBD-002 - Maritime Report Detail Candidate

Date: 2026-05-07

Evidence lane: `candidate_compile_mode`

Candidate context: `maritime salvage adjudication insurance claim heritage
protected zone shipping register metallurgical report`, activating the
maritime/insurance dispute compiler context.

Targeted non-exact replay: `4 exact / 3 partial / 6 miss` across the `13`
baseline non-exact rows. The candidate improved recovery location, vessel-list
surface, metallurgical report conclusion, foundry suggestion, and report date
range, but regressed Strand's missing-evidence row.

Full guardrail replay: `25 exact / 7 partial / 8 miss` across all `40` rows,
down from baseline `27 / 7 / 6`. The candidate is not a global default.

Artifacts:

- Candidate compile: `tmp/incoming_10_repair_salvage_maritime_report_v1`
- Targeted QA: `tmp/incoming_10_repair_salvage_maritime_report_v1_qa_nonexact`
- Full guardrail QA: `tmp/incoming_10_repair_salvage_maritime_report_v1_qa_full`

Decision: useful report/detail candidate mode only. It captures independent
metallurgical-report and candidate-vessel surfaces, but thins claimant
testimony, direct insurance links, and missing-evidence support.

## SBD-003 - Maritime Detail Row-Gated Selector

Date: 2026-05-07

Evidence lane: `candidate_mode_selector`

Selector replay:
`tmp/incoming_10_candidate_mode_selectors/salvage_guarded_selector_v2.md`

Result: `31 exact / 4 partial / 5 miss`, matching the perfect available upper
bound from baseline plus maritime-report candidate modes. The selector chose
the best available mode on all `40/40` rows with `0` selector errors.

Guard lessons:

- Recovery-identity questions need direct testimony/recovery surface, not
  custody or zone rows.
- Source-belief questions need claimant testimony, not identification-status
  summary.
- Candidate-vessel list questions need candidate-origin plus vessel-loss detail
  surface.
- Insurance-link questions need direct `insured_by`/`insurer_of` support, not
  contingent ownership-claim rows.

Decision update: maritime report detail is a row-gated lane. The remaining
misses press on count/boundary/final-hearing and specific vessel attribute
surfaces.

## SBD-004 - Baseline/Maritime Union Selector Lane

Date: 2026-05-07

Evidence lane: `deterministic_compile_union` plus `candidate_mode_selector`

Union compile:
`tmp/incoming_10_repair_salvage_union_v1/domain_bootstrap_file_20260507T193922747557Z_salvage-baseline-plus-maritime_qwen-qwen3-6-35b-a3b.json`

Policy: no source prose was read and no new facts were inferred. The union
deduplicated mapper-admitted clauses from the cold baseline and maritime-report
candidate compiles.

Full union replay:
`tmp/incoming_10_repair_salvage_union_v1_qa_full/domain_bootstrap_qa_20260507T195025413955Z_qa_qwen-qwen3-6-35b-a3b.json`

Union alone scored `33 exact / 3 partial / 4 miss`, exceeding both individual
compile modes. The union recovered alternative-inscription coverage, Dr. Hale's
analysis deadline, and Strand's missing-evidence row, while still leaving
vessel-count, zone-boundary, final-hearing, and some vessel-attribute rows
unsolved.

Three-mode selector replay:
`tmp/incoming_10_candidate_mode_selectors/salvage_union_guarded_selector_v3.md`

Result: `34 exact / 2 partial / 4 miss`, matching the perfect available upper
bound across baseline, maritime candidate, and union modes. The selector chose
the best available mode on all `40/40` rows with `0` selector errors.

Guard additions: source-belief protection now avoids candidate-origin leakage
when the question asks what Strand believed; alternative-inscription questions
prefer candidate-origin plus inscription-fragment support; missing-evidence
questions prefer the combined claimant-testimony and explicit absence/claim
surface.

Lesson: union can be more than a rescue lane when the two compiles carry
different but compatible slices of the same testimony/report boundary. The
guard risk is equally visible: combined candidate-origin volume can drown out
source-owned belief unless the selector protects whose claim is being asked
about.
