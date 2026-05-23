# Anti-Leakage Manifest — cpsc_recall_polaris_rzr200_2023

- `oracle.jsonl` is for scoring only. It must not be visible to the system under test during compile, indexing, retrieval, or query.
- `source.md` is the only compile source for this fixture.
- `qa.md` contains questions only. No answer text, hints, or category labels are embedded in `qa.md`.
- `fixture_notes.md` and `expected_failure_modes.md` are documentation for the fixture itself; they should not be exposed to the system under test as retrievable content.
