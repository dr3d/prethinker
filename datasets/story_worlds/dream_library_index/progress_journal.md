# Dream Library Index Progress Journal

Fixture id: `dream_library_index`

This journal records durable research findings for this promoted incoming fixture.
Generated run artifacts may live under `tmp/`; lessons and artifact references belong here.

## DLI-000 - Fixture Admission

Date: 2026-05-04

Evidence lane: `fixture_admission`

Source admitted from: `tmp/incoming/dream_library_index.zip`

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

## DLI-001 - First Full-40 Cold Baseline

Date: 2026-05-07

Evidence lane: `cold_unseen`

Score: `34 exact / 2 partial / 4 miss`

Artifacts:

- Compile: `tmp/incoming_10_cold_runs_20260507/dream_library_index`
- QA: `tmp/incoming_10_cold_qa_20260507/dream_library_index`

Boundary: `0` write proposals and `0` runtime load errors. This is a strong cold transfer fixture.

## DLI-002 - Fiction Reference Containment Probe

Date: 2026-05-07

Evidence lane: `candidate_context_probe`

Candidate context: `FICTION_REFERENCE_CONTAINMENT_CONTEXT_V1`

Score: `28 exact / 1 partial / 11 miss`

Artifacts:

- Compile: `tmp/incoming_10_repair_dream_fiction_containment_v1`
- QA: `tmp/incoming_10_repair_dream_fiction_containment_v1_qa_full`

Lesson: the fiction/reference containment context did recover one pipe-leak row, but it was globally worse than the cold baseline. It over-preferred fictional-event and title-name surfaces for ordinary incident/accounting questions. This is not a promoted lens on its own.

## DLI-003 - Row-Gated Candidate Selection

Date: 2026-05-07

Evidence lane: `row_gated_candidate_selection`

Score: `35 exact / 2 partial / 3 miss`

Artifacts:

- Selector: `tmp/incoming_10_candidate_mode_selectors/dream_guarded_selector_v2.json`
- Selector report: `tmp/incoming_10_candidate_mode_selectors/dream_guarded_selector_v2.md`

Lesson: the selector can keep the one useful fiction-containment improvement while protecting the baseline for insured value, physical inventory count, and Odell's discrepancy explanation. The durable lesson is selector-level: fiction/reference rows are useful when they resolve a story-layer leak, but they must not displace direct financial, count, or incident-discrepancy evidence.
