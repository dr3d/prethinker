# sec_8k_material_event_001

Real-world transfer fixture for Prethinker.

- `source.md` is the source document for compilation.
- `source_original.*` is retained for provenance.
- `story.md` is a source-compatible alias.
- `qa.md` contains runner-compatible numbered questions only.
- `oracle.jsonl` contains reference answers for after-the-fact scoring.
- `qa_battery.json` contains structured QA rows with answers.
- `qa_questions.jsonl` contains structured question rows without answers.
- `metadata.json` and `provenance.md` preserve source context.
- `fixture_notes.md` and `anti_leakage_manifest.md` record fixture discipline.

Do not feed `oracle.jsonl`, `qa_battery.json`, or answer-bearing files into source compilation.
