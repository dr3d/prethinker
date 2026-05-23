# ntsb_aviation_001

Rough NTSB aviation pilot fixture promoted from the May 23, 2026 incoming tmp package.

- `source.md` is the source document for compilation.
- `source_original.pdf` is the public NTSB PDF retained for provenance.
- `story.md` is a source-compatible alias for story-world harnesses.
- `qa.md` contains questions only.
- `qa_battery.json` contains `25` structured QA rows with reference answers for after-the-fact scoring.
- `qa_questions.jsonl` contains structured question rows without reference answers.
- `oracle.jsonl` contains reference answers for after-the-fact scoring.
- `metadata.json` and `provenance.md` preserve source and intake context.
- `fixture_notes.md`, `progress_journal.md`, and `progress_metrics.jsonl` record the shakedown status.

Do not feed `oracle.jsonl`, `qa_battery.json`, or other answer-bearing files into source compilation.
