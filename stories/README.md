# Story Packs

Each story file should map to one canonical answer KB in `goldens/kb/`.

Suggested naming:

- story file: `stories/<story_id>.md`
- scenario: `kb_scenarios/<story_id>.json`
- probe Q&A: `goldens/probes/<story_id>.json`
- golden KB: `goldens/kb/<story_id>.pl`

Workflow:

1. Build or choose the intended world model (facts/rules) first.
2. Write narrative text that expresses that world.
3. Craft probe Q&A to force coverage of all intended clauses.
4. Run rigorous ingestion and freeze canonical golden KB.
5. Use fast golden compare for routine prompt/model regressions.
