# Iron Harbor Water Crisis Progress Journal

## 2026-04-29 - Dataset Integration

- Integrated source story, QA battery, reference KB, and strategy notes from `tmp/The Iron Harbor Water Crisis`.
- Normalized text files to ASCII for fixture stability while retaining source-provided answers and translations.
- Added starter failure buckets and an ontology registry derived from the reference KB.

## TODO

- Run the reference KB through the deterministic Prolog layer and record baseline QA coverage.
- Run source-only story ingestion and compare admitted predicates against `ontology_registry.json`.
- Add progress rows after each benchmark attempt; do not rewrite historical rows.
