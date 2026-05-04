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
