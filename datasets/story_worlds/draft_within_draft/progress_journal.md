# Draft Within Draft Progress Journal

Fixture id: `draft_within_draft`

This journal records durable research findings for this promoted incoming fixture.
Generated run artifacts may live under `tmp/`; lessons and artifact references belong here.

## DWD-000 - Fixture Admission

Date: 2026-05-04

Evidence lane: `fixture_admission`

Source admitted from: `tmp\incoming_validation_20260508_new6\draft_within_draft`

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

## DWD-001 - Planning Summary And Authority-Boundary Registry Probe

Date: 2026-05-08

Evidence lane: `registry_scaffold_probe`

Cold first-10 smoke missed three front-matter/staff-report rows:

- q001: current request details
- q003: zoning designation full name/code
- q010: Route 14 distance and actual location

The first registry attempt supplied planning-application summary, parcel zoning,
unit mix, site measures, transit route location/distance, staff finding, draft
condition, and proposal-version predicates. It recovered the target rows but
lost a source-claim row. A second attempt added `applicant_claim/4`; a third
added `recommendation_status/4` for the explicit non-binding staff
recommendation boundary.

Artifacts:

- Registry: `tmp\planning_application_summary_registry_v1.json`
- v3 compile: `tmp\planning_summary_registry_probe_20260508\draft_within_draft_v3\domain_bootstrap_file_20260508T085133754168Z_source_qwen-qwen3-6-35b-a3b.json`
- v3 first-10 QA: `tmp\planning_summary_registry_probe_20260508\draft_within_draft_v3_qa_first10\domain_bootstrap_qa_20260508T085345844991Z_qa_qwen-qwen3-6-35b-a3b.json`
- v3 full-40 QA: `tmp\planning_summary_registry_probe_20260508\draft_within_draft_v3_qa_full40\domain_bootstrap_qa_20260508T090325443343Z_qa_qwen-qwen3-6-35b-a3b.json`
- v4 compile: `tmp\planning_summary_registry_probe_20260508\draft_within_draft_v4\domain_bootstrap_file_20260508T090657660778Z_source_qwen-qwen3-6-35b-a3b.json`
- v4 full-40 QA: `tmp\planning_summary_registry_probe_20260508\draft_within_draft_v4_qa_full40\domain_bootstrap_qa_20260508T092139222158Z_qa_qwen-qwen3-6-35b-a3b.json`

Results:

- v1 compile: `45` admitted / `14` skipped.
- v1 target q001/q003/q010: `3 exact / 0 partial / 0 miss`.
- v1 first-10: `9 exact / 0 partial / 1 miss`.
- v2 compile with `applicant_claim/4`: `69` admitted / `5` skipped.
- v2 first-10: `9 exact / 1 partial / 0 miss`.
- v3 compile with `recommendation_status/4`: `82` admitted / `1` skipped.
- v3 first-10: `10 exact / 0 partial / 0 miss`.
- v3 full-40: `25 exact / 3 partial / 12 miss`.
- v4 added traffic/environment/site-condition/opinion predicates: `49` admitted
  / `1` skipped.
- v4 first-10: `10 exact / 0 partial / 0 miss`.
- v4 full-40: `31 exact / 2 partial / 7 miss`.
- Writes/errors: `0` / `0`.

Meaning lesson:

Planning staff reports need a source/authority split that is more specific than
generic claim rows. The current application request, applicant claims, staff
findings, recommendation status, rejected prior proposal, draft conditions, and
final commission authority are separate semantic objects. When those slots are
available, the front-matter and early staff-authority questions become crisp.

Promotion status:

Candidate row-gated registry only. The full-40 score shows the scaffold is not a
complete planning-report compiler. v4 recovers traffic, environmental review,
and condition rows, but remaining misses still show incomplete acquisition for
density calculation, below-minimum lot ids, AR-2 minimum lot size, Saturday
construction hours, condition modification authority, Courtyard B recommendation
authority, April 15 comment-period closure, and applicant-opinion rollups.

## DWD-002 - Rejected-Version, Opinion, And Date-Event Residual Repair

Date: 2026-05-08

Evidence lane: `row_gated_residual_repair`

Artifacts:

- Row-shape compile: `tmp\draft_rowshape_compile_20260508\domain_bootstrap_file_20260508T143300637974Z_source_qwen-qwen3-6-35b-a3b.json`
- Row-shape QA q021/q022/q033/q040: `tmp\draft_rowshape_qa_20260508\domain_bootstrap_qa_20260508T143355647457Z_qa_qwen-qwen3-6-35b-a3b.json`
- April 15 compile: `tmp\draft_april15_compile_20260508\domain_bootstrap_file_20260508T143541489091Z_source_qwen-qwen3-6-35b-a3b.json`
- April 15 QA q033: `tmp\draft_april15_qa_20260508\domain_bootstrap_qa_20260508T143604324793Z_qa_qwen-qwen3-6-35b-a3b.json`

Result:

- Residual rows after row-gated selection: `4 exact / 0 partial / 0 miss`
- Writes/errors: `0` / `0`

Meaning lesson:

Planning documents need rejected-version surfaces separate from the current
application. The useful rows were below-minimum lots for the 18-unit version,
the AR-2 minimum lot size, and applicant-opinion/projection rows distinct from
staff findings. A second tiny repair showed that procedural dates need explicit
`event_on_date` anchors: "April 15" was not an approval or hearing date; it was
the MND public comment period closure.
