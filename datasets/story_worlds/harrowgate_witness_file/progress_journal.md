# Harrowgate Witness File Progress Journal

Fixture id: `harrowgate_witness_file`

This journal records durable research findings for the Harrowgate incoming
fixture. Generated run artifacts may live under `tmp/`; the lessons and artifact
references belong here.

## HWF-000 - Fixture Admission

Date: 2026-05-04

Evidence lane: `fixture_admission`

Source admitted from: `tmp/incoming_staged/harrowgate_witness_file`

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

## HWF-001 - Incoming First-10 Smoke

Date: 2026-05-04

Evidence lane: `cold_unseen`

Mode: incoming standard first-10 smoke.

Artifacts:

- Scorecard: `tmp/incoming_smoke_summaries/scorecard.md`
- Scoped-evidence scorecard: `tmp/incoming_smoke_summaries_scoped_evidence/scorecard.md`

Result:

- Compile: `135` admitted operations, `0` skips.
- Compile health: `warning`.
- QA first-10: `10 exact / 0 partial / 0 miss`.
- Safety: `0` write-proposal rows.
- Semantic progress: low risk, `continue`.

Lesson:

Harrowgate is a clean claim-versus-truth smoke. It should stay as a regression
guard for preserving testimony, official non-substantiation, and source
attribution without collapsing disputed claims into durable facts.
