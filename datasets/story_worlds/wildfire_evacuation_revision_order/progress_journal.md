# Wildfire Evacuation Revision Order Progress Journal

Fixture id: `wildfire_evacuation_revision_order`

This journal records durable research findings for this promoted incoming fixture.
Generated run artifacts may live under `tmp/`; lessons and artifact references belong here.

## WERO-000 - Fixture Admission

Date: 2026-05-04

Evidence lane: `fixture_admission`

Source admitted from: `tmp\incoming\claude_md_split_raw\wildfire_evacuation_revision_order`

Files admitted:

- `source.md` / `story.md`
- `fixture_notes.md`
- `qa.md`
- `qa_questions.jsonl`
- `oracle.jsonl`
- `qa_battery.json`

Benchmark discipline:

- `source.md`/`story.md` is the only cold compile source.
- `oracle.jsonl`, `qa_battery.json`, `qa.md`, and `fixture_notes.md` are scoring/review assets, not compile context.
- No Python source-prose interpretation is allowed.

## WERO-001 - Claude 8 Cold Baseline

Date: 2026-05-08

Evidence lane: `cold_unseen_full40`

Artifacts:

- Compile: `tmp\claude_8_baseline_20260508\cold_compile\wildfire_evacuation_revision_order\domain_bootstrap_file_20260508T165052668795Z_source_qwen-qwen3-6-35b-a3b.json`
- QA: `tmp\claude_8_baseline_20260508\qa_full40\wildfire_evacuation_revision_order\domain_bootstrap_qa_20260508T183513079337Z_qa_qwen-qwen3-6-35b-a3b.json`

Results:

- Full-40 cold score: `19 exact / 4 partial / 17 miss`.
- Runtime load errors: `0`.
- Write proposal rows: `0`.

Meaning lesson:

This fixture entered the Claude 8 dense operational-record batch. The cold run
measures the instrument before any fixture-specific source-record repair. The
batch-level result exposed a compile coverage gap rather than a governance
breach: the model often understood the document type but failed to preserve the
source rows, exact identifiers, and archival addresses needed for scoring.

## WERO-002 - Source-Record V2 Diagnostic Repair

Date: 2026-05-08

Evidence lane: `source_record_registry_scaffold`

Registry scaffold:

- `tmp\claude_8_baseline_20260508\registries\document_packet_source_record_registry_v2.json`

Artifacts:

- QA: `tmp\claude_8_baseline_20260508\repair_qa\wildfire_source_record_v2_all_candidates\domain_bootstrap_qa_20260508T230941971627Z_qa_qwen-qwen3-6-35b-a3b.json`
- Batch rollup: `tmp\claude_8_baseline_20260508\source_record_v2_80pct_rollup.md`

Results:

- Chosen diagnostic score: `32 exact / 1 partial / 7 miss`.
- Exact lift over cold: `+13`.
- Miss reduction over cold: `10`.
- Runtime load errors: `0`.
- Write proposal rows: `0`.

Meaning lesson:

`document_packet_source_record_registry_v2` is a temporary scaffold, not a
promoted permanent lens. It showed that dense packets need source-record
vocabulary before they need cleverer answers: source documents, sections, logs,
status rows, count/list rows, supersession rows, and unresolved issues must be
admitted as queryable surfaces. Remaining non-exact rows mostly point toward an
archival row-ledger problem: exact printed labels, exhibit IDs, receipt IDs,
case numbers, system names, and table-row addresses are still too thin.

## WERO-003 - Archival Row Ledger V1 Complement Probe

Date: 2026-05-08/09

Evidence lane: `archival_row_ledger_v1_guarded_selector`

Artifacts:

- Compile: `tmp\claude_8_baseline_20260508\repair_compile\wildfire_evacuation_revision_order_archival_row_ledger_v1\domain_bootstrap_file_20260509T010857371972Z_source_qwen-qwen3-6-35b-a3b.json`
- Union: `tmp\claude_8_baseline_20260508\repair_union\wildfire_evacuation_revision_order_archival_row_ledger_v1\domain_bootstrap_file_20260509T010857546491Z_wildfire-evacuation-revision-order-archival-row-ledger-v1_qwen-qwen3-6-35b-a3b.json`
- QA: `tmp\claude_8_baseline_20260508\repair_qa\wildfire_evacuation_revision_order_archival_row_ledger_v1\domain_bootstrap_qa_20260509T012411833756Z_qa_qwen-qwen3-6-35b-a3b.json`
- Selector: `tmp\claude_8_baseline_20260508\selector_archival_row_ledger_v1\wildfire_evacuation_revision_order_guarded_activation.json`
- Batch rollup: `tmp\claude_8_baseline_20260508\archival_row_ledger_v1_85pct_rollup.md`

Results:

- Whole archival score: `31 exact / 4 partial / 5 miss`.
- Guarded selected score: `33 exact / 2 partial / 5 miss`.
- Exact lift over source-record V2 selected row routing: `+1`.
- Runtime load errors: `0`.
- Write proposal rows: `0`.

Meaning lesson:

Wildfire rejects blind archival promotion. The row-ledger surface can rescue a
few source-addressed rows, but the fixture's real pressure remains version-chain
and correction-scope semantics. This candidate should remain row-gated here.
