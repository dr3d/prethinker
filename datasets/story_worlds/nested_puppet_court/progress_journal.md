# Nested Puppet Court Progress Journal

Fixture id: `nested_puppet_court`

This journal records durable research findings for this promoted incoming fixture.
Generated run artifacts may live under `tmp/`; lessons and artifact references belong here.

## NPC-000 - Fixture Admission

Date: 2026-05-04

Evidence lane: `fixture_admission`

Source admitted from: `tmp/incoming/nested_puppet_court.zip`

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

## NPC-001 - First Full-40 Cold Baseline

Date: 2026-05-07

Evidence lane: `cold_unseen`

Score: `35 exact / 0 partial / 5 miss`

Artifacts:

- Compile: `tmp/incoming_10_cold_runs_20260507/nested_puppet_court`
- QA: `tmp/incoming_10_cold_qa_20260507/nested_puppet_court`

Boundary: `0` write proposals and `0` runtime load errors. This is a strong cold transfer fixture for quoted-world containment.

## NPC-002 - Profile Review Retry Probe

Date: 2026-05-07

Evidence lane: `candidate_profile_review_retry`

Score: `32 exact / 1 partial / 7 miss`

Artifacts:

- Compile: `tmp/incoming_10_repair_nested_profile_review_v1`
- QA: `tmp/incoming_10_repair_nested_profile_review_v1_qa_full`

Lesson: the profile-review retry added useful detail predicates such as `surveyor_certification/2` and recovered some small answer-bearing facts, but it weakened the puppet/narrative and measurement surfaces enough to regress the full fixture. This candidate is not promoted as a whole-compile replacement.

## NPC-003 - Row-Gated Detail Recovery

Date: 2026-05-07

Evidence lane: `row_gated_candidate_selection`

Score: `38 exact / 0 partial / 2 miss`

Artifacts:

- Selector: `tmp/incoming_10_candidate_mode_selectors/nested_guarded_selector_v2.json`
- Selector report: `tmp/incoming_10_candidate_mode_selectors/nested_guarded_selector_v2.md`

Lesson: small evidentiary detail predicates are valuable when a question asks directly for certification lapse, survey reliance, or residence/parcel occupancy. They must stay row-gated because the older baseline remains stronger for receipt evidence, fictional plot outcomes, canopy measurement, fence legal status, and marker-shift discrepancy causes.

## NPC-004 - Hearing Evidence Provenance Registry Candidate

Date: 2026-05-07

Evidence lane: `candidate_compile_mode` plus `candidate_mode_selector`

Harness/context change: expanded the source-authority strategy with report,
survey, exhibit, photograph, receipt, and expert-statement provenance guidance.
Free-form hearing-evidence candidates recovered Rowan's photograph dates but
still failed to create a commissioned-by surface for the Voss survey. A tiny
temporary provenance registry then supplied explicit evidence/report predicate
vocabulary without supplying any facts.

Registry scaffold:
`tmp/nested_hearing_evidence_registry_v1.json`

Candidate compile:
`tmp/incoming_10_repair_nested_hearing_evidence_registry_v1/domain_bootstrap_file_20260507T232534335667Z_source_qwen-qwen3-6-35b-a3b.json`

Compile result: `46` admitted facts, `4` skipped facts/rules, `0` runtime load
errors. New useful surfaces included `evidence_presented_by/4`,
`evidence_date/3`, `report_prepared_by/4`, `report_commissioned_by/4`,
`survey_result/5`, and `testimony_given/4`.

Targeted weak-row replay:
`tmp/incoming_10_repair_nested_hearing_evidence_registry_v1_qa_targeted/domain_bootstrap_qa_20260507T232604826221Z_qa_qwen-qwen3-6-35b-a3b.json`

Targeted result: `2 exact / 0 partial / 0 miss` over q019 and q039. The
candidate recovered the photograph years (`2016` and `2019`) and Officer
Drury's commission of the Voss survey.

Full candidate replay:
`tmp/incoming_10_repair_nested_hearing_evidence_registry_v1_qa_full/domain_bootstrap_qa_20260507T233530660410Z_qa_qwen-qwen3-6-35b-a3b.json`

Candidate score: `27 exact / 1 partial / 12 miss`. This is a surgical evidence
provenance mode, not a replacement compile.

Three-mode selector replay:
`tmp/incoming_10_candidate_mode_selectors/nested_hearing_registry_guarded_selector_v2.md`

Result: `40 exact / 0 partial / 0 miss`, matching the perfect available upper
bound across baseline, profile-review candidate, and provenance-registry modes.
The selector chose the best available mode on all `40/40` rows with `0`
selector errors.

Guard additions: disputed-strip feature rows prefer object-location surfaces
over broad finding/survey volume; source-claim and permission-request rows
prefer witness-statement surfaces over provenance summaries; survey-commission
rows prefer explicit report-commission provenance.

Lesson: evidence provenance is its own lane. For hearings, audits, and
source-authority records, the compiler needs explicit vocabulary for who
presented, prepared, dated, admitted, relied on, or commissioned an evidence
item. That scaffold should remain candidate-gated until it proves transferable,
because it is narrow and regresses broad narrative/legal questions when used as
a whole-compile replacement.
