# School Trip Bus Roster Split Progress Journal

Fixture id: `school_trip_bus_roster_split`

This journal records durable research findings for this promoted incoming fixture.
Generated run artifacts may live under `tmp/`; lessons and artifact references belong here.

## STBR-000 - Fixture Admission

Date: 2026-05-04

Evidence lane: `fixture_admission`

Source admitted from: `tmp\incoming\claude_md_split_raw\school_trip_bus_roster_split`

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


## STBR-001 - Claude 8 Cold Baseline

Date: 2026-05-08

Evidence lane: `cold_unseen_full40`

Artifacts:

- Compile: `tmp\claude_8_baseline_20260508\cold_compile\school_trip_bus_roster_split\domain_bootstrap_file_20260508T170131076971Z_source_qwen-qwen3-6-35b-a3b.json`
- QA: `tmp\claude_8_baseline_20260508\qa_full40\school_trip_bus_roster_split\domain_bootstrap_qa_20260508T181637062034Z_qa_qwen-qwen3-6-35b-a3b.json`

Results:

- Full-40 cold score: `14 exact / 7 partial / 19 miss`.
- Runtime load errors: `0`.
- Write proposal rows: `0`.

Meaning lesson:

This fixture entered the Claude 8 dense operational-record batch. The cold run
measures the instrument before any fixture-specific source-record repair. The
batch-level result exposed a compile coverage gap rather than a governance
breach: the model often understood the document type but failed to preserve the
source rows, exact identifiers, and archival addresses needed for scoring.

## STBR-002 - Source-Record V2 Diagnostic Repair

Date: 2026-05-08

Evidence lane: `source_record_registry_scaffold`

Registry scaffold:

- `tmp\claude_8_baseline_20260508\registries\document_packet_source_record_registry_v2.json`

Artifacts:

- QA: `tmp\claude_8_baseline_20260508\repair_qa\source_record_v2_all\school_trip_bus_roster_split\domain_bootstrap_qa_20260508T212712992365Z_qa_qwen-qwen3-6-35b-a3b.json`
- Batch rollup: `tmp\claude_8_baseline_20260508\source_record_v2_80pct_rollup.md`

Results:

- Chosen diagnostic score: `34 exact / 3 partial / 3 miss`.
- Exact lift over cold: `+20`.
- Miss reduction over cold: `16`.
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

## STBR-003 - Archival Row Ledger V1 Promotion Candidate

Date: 2026-05-08/09

Evidence lane: `archival_row_ledger_v1_probe`

Artifacts:

- Compile: `tmp\claude_8_baseline_20260508\repair_compile\school_trip_bus_roster_split_archival_row_ledger_v1\domain_bootstrap_file_20260509T015007536578Z_source_qwen-qwen3-6-35b-a3b.json`
- Union: `tmp\claude_8_baseline_20260508\repair_union\school_trip_bus_roster_split_archival_row_ledger_v1\domain_bootstrap_file_20260509T015050844756Z_school-trip-bus-roster-split-archival-row-ledger-v1_qwen-qwen3-6-35b-a3b.json`
- QA: `tmp\claude_8_baseline_20260508\repair_qa\school_trip_bus_roster_split_archival_row_ledger_v1\domain_bootstrap_qa_20260509T022319032847Z_qa_qwen-qwen3-6-35b-a3b.json`
- Batch rollup: `tmp\claude_8_baseline_20260508\archival_row_ledger_v1_85pct_rollup.md`

Results:

- Whole archival score: `36 exact / 1 partial / 3 miss`.
- Exact lift over source-record V2: `+2`.
- Runtime load errors: `0`.
- Write proposal rows: `0`.

Meaning lesson:

School confirms that roster and scan-log fixtures need archival addressability.
The lens helped where the question asks for the row-level identity of students,
groups, counts, or scan evidence rather than only the narrative trip outcome.
