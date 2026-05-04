# Copperfall Deadline Docket

Temporal status-ledger fixture for deadline arithmetic, tolling, corrections,
party stipulations versus court orders, and point-in-time case status.

## Files

- `source.md`: source fixture to compile.
- `story.md`: source-compatible alias for story-world harnesses.
- `fixture_notes.md`: authored challenge notes and expected failure modes.
- `qa.md`: 40-question QA battery, questions only.
- `qa_battery_40.json`: harness-ready structured QA records with reference
  answers for after-the-fact scoring.
- `qa_questions.jsonl`: structured question rows without reference answers.
- `oracle.jsonl`: reference answers for after-the-fact scoring only.
- `qa_authored_with_answers.jsonl`: original incoming authoring format.
- `progress_journal.md`: running research record.
- `progress_metrics.jsonl`: append-only metrics rows.

## Evidence-Lane Discipline

Cold compiles must use `source.md`/`story.md` only. `oracle.jsonl`,
`qa_authored_with_answers.jsonl`, `qa.md`, and `fixture_notes.md` are scoring,
review, and challenge assets, not source-compilation context.
