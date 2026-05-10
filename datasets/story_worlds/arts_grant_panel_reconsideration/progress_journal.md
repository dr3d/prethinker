# Arts Grant Panel Reconsideration Progress Journal

Fixture id: `arts_grant_panel_reconsideration`

This journal records durable research findings for this promoted incoming fixture.
Generated run artifacts may live under `tmp/`; lessons and artifact references belong here.

## AGPR-000 - Fixture Admission

Date: 2026-05-04

Evidence lane: `fixture_admission`

Source admitted from: `tmp\incoming\claude_md_split_raw\arts_grant_panel_reconsideration`

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


## AGPR-001 - Claude 8 Cold Baseline

Date: 2026-05-08

Evidence lane: `cold_unseen_full40`

Artifacts:

- Compile: `tmp\claude_8_baseline_20260508\cold_compile\arts_grant_panel_reconsideration\domain_bootstrap_file_20260508T165459005421Z_source_qwen-qwen3-6-35b-a3b.json`
- QA: `tmp\claude_8_baseline_20260508\qa_full40\arts_grant_panel_reconsideration\domain_bootstrap_qa_20260508T172752533916Z_qa_qwen-qwen3-6-35b-a3b.json`

Results:

- Full-40 cold score: `28 exact / 5 partial / 7 miss`.
- Runtime load errors: `0`.
- Write proposal rows: `0`.

Meaning lesson:

This fixture entered the Claude 8 dense operational-record batch. The cold run
measures the instrument before any fixture-specific source-record repair. The
batch-level result exposed a compile coverage gap rather than a governance
breach: the model often understood the document type but failed to preserve the
source rows, exact identifiers, and archival addresses needed for scoring.

## AGPR-002 - Source-Record V2 Diagnostic Repair

Date: 2026-05-08

Evidence lane: `source_record_registry_scaffold`

Registry scaffold:

- `tmp\claude_8_baseline_20260508\registries\document_packet_source_record_registry_v2.json`

Artifacts:

- QA: `tmp\claude_8_baseline_20260508\repair_qa\source_record_v2_all\arts_grant_panel_reconsideration\domain_bootstrap_qa_20260508T202923918950Z_qa_qwen-qwen3-6-35b-a3b.json`
- Batch rollup: `tmp\claude_8_baseline_20260508\source_record_v2_80pct_rollup.md`

Results:

- Chosen diagnostic score: `32 exact / 5 partial / 3 miss`.
- Exact lift over cold: `+4`.
- Miss reduction over cold: `4`.
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

## AGPR-003 - Archival Row Ledger V1 Rejection

Date: 2026-05-08/09

Evidence lane: `archival_row_ledger_v1_probe`

Artifacts:

- Compile: `tmp\claude_8_baseline_20260508\repair_compile\arts_grant_panel_reconsideration_archival_row_ledger_v1\domain_bootstrap_file_20260509T022728742393Z_source_qwen-qwen3-6-35b-a3b.json`
- Union: `tmp\claude_8_baseline_20260508\repair_union\arts_grant_panel_reconsideration_archival_row_ledger_v1\domain_bootstrap_file_20260509T022738475662Z_arts-grant-panel-reconsideration-archival-row-ledger-v1_qwen-qwen3-6-35b-a3b.json`
- QA: `tmp\claude_8_baseline_20260508\repair_qa\arts_grant_panel_reconsideration_archival_row_ledger_v1\domain_bootstrap_qa_20260509T024316066559Z_qa_qwen-qwen3-6-35b-a3b.json`
- Batch rollup: `tmp\claude_8_baseline_20260508\archival_row_ledger_v1_85pct_rollup.md`

Results:

- Whole archival score: `30 exact / 5 partial / 5 miss`.
- Source-record V2 remains selected: `32 exact / 5 partial / 3 miss`.
- Runtime load errors: `0`.
- Write proposal rows: `0`.

Meaning lesson:

Arts confirms that archival addressability is not a substitute for procedural
and decisional semantics. The hard rows are about whether a correction changes a
decision, not about locating the printed row that mentioned it.
