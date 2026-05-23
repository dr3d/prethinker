# Anti-Leakage Manifest — lease_amendment_status_register

- oracle.jsonl is scoring-only. It must not be visible to the model under test, to the extractor, or to any compile-time process. It exists solely to score answers produced from source.md.
- source.md is the only compile source. All extraction, ingestion, KB compilation, and clause assertion must be derived exclusively from source.md. No other file in this fixture folder is to be ingested as evidence.
- qa.md contains questions only. It contains no answers, no answer hints, no correct-answer markers, no implied solutions. It may be presented to the model under test in question form.
- fixture_notes.md is meta-commentary about what the fixture pressures. It must not be ingested as source.
- expected_failure_modes.md describes anticipated failure patterns. It must not be ingested as source.
- This manifest (anti_leakage_manifest.md) is meta-control documentation. It must not be ingested as source.
