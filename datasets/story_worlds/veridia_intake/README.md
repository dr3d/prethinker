# veridia_intake

Promoted incoming challenge fixture.

- `source.md` is the source document for compilation.
- `story.md` is a source-compatible alias for story-world harnesses.
- `qa.md` contains questions only.
- `qa_battery.json` contains `23` structured QA rows with reference answers for after-the-fact scoring.
- `qa_questions.jsonl` contains structured question rows without reference answers.
- `oracle.jsonl` contains reference answers for after-the-fact scoring.
- `qa_authored_with_answers.jsonl` or `oracle_authored.jsonl` preserves the original incoming answer-bearing authoring format when present.
- `progress_journal.md` records durable research findings.
- `progress_metrics.jsonl` records append-only run metrics.

Do not feed `oracle.jsonl`, `qa_battery.json`, `qa_authored_with_answers.jsonl`, or `oracle_authored.jsonl` into source compilation.
