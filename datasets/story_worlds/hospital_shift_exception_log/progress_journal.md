# Hospital Shift Exception Log Progress Journal

Fixture id: `hospital_shift_exception_log`

This journal records durable research findings for this promoted incoming fixture.
Generated run artifacts may live under `tmp/`; lessons and artifact references belong here.

## HSEL-000 - Fixture Admission

Date: 2026-05-04

Evidence lane: `fixture_admission`

Source admitted from: `tmp\incoming\claude_md_split_raw\hospital_shift_exception_log`

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

## HSEL-001 - Claude 8 Cold Baseline

Date: 2026-05-08

Evidence lane: `cold_unseen_full40`

Artifacts:

- Compile: `tmp\claude_8_baseline_20260508\cold_compile\hospital_shift_exception_log\domain_bootstrap_file_20260508T164822507636Z_source_qwen-qwen3-6-35b-a3b.json`
- QA: `tmp\claude_8_baseline_20260508\qa_full40\hospital_shift_exception_log\domain_bootstrap_qa_20260508T174930520244Z_qa_qwen-qwen3-6-35b-a3b.json`

Results:

- Full-40 cold score: `13 exact / 3 partial / 24 miss`.
- Runtime load errors: `0`.
- Write proposal rows: `0`.

Meaning lesson:

This fixture entered the Claude 8 dense operational-record batch. The cold run
measures the instrument before any fixture-specific source-record repair. The
batch-level result exposed a compile coverage gap rather than a governance
breach: the model often understood the document type but failed to preserve the
source rows, exact identifiers, and archival addresses needed for scoring.

## HSEL-002 - Source-Record V2 Diagnostic Repair

Date: 2026-05-08

Evidence lane: `source_record_registry_scaffold`

Registry scaffold:

- `tmp\claude_8_baseline_20260508\registries\document_packet_source_record_registry_v2.json`

Artifacts:

- QA: `tmp\claude_8_baseline_20260508\repair_qa\hospital_source_record_v2_all_candidates\domain_bootstrap_qa_20260508T221325266199Z_qa_qwen-qwen3-6-35b-a3b.json`
- Batch rollup: `tmp\claude_8_baseline_20260508\source_record_v2_80pct_rollup.md`

Results:

- Chosen diagnostic score: `32 exact / 0 partial / 8 miss`.
- Exact lift over cold: `+19`.
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

## HSEL-003 - Archival Row Ledger V1 Selector Proof

Date: 2026-05-08/09

Evidence lane: `archival_row_ledger_v1_guarded_selector`

Artifacts:

- Compile: `tmp\claude_8_baseline_20260508\repair_compile\hospital_shift_exception_log_archival_row_ledger_v1\domain_bootstrap_file_20260509T000820320072Z_source_qwen-qwen3-6-35b-a3b.json`
- Union: `tmp\claude_8_baseline_20260508\repair_union\hospital_shift_exception_log_archival_row_ledger_v1\domain_bootstrap_file_20260509T001634084319Z_hospital-shift-exception-log-archival-row-ledger-v1_qwen-qwen3-6-35b-a3b.json`
- QA: `tmp\claude_8_baseline_20260508\repair_qa\hospital_shift_exception_log_archival_row_ledger_v1\domain_bootstrap_qa_20260509T003423048273Z_qa_qwen-qwen3-6-35b-a3b.json`
- Selector: `tmp\claude_8_baseline_20260508\selector_archival_row_ledger_v1\hospital_shift_exception_log_guarded_activation_source_provenance_guard.json`
- Lexical selector: `tmp\claude_8_baseline_20260508\selector_archival_identifier_ledger_v1\hospital_shift_exception_log_guarded_activation_three_way_timekeeping_guard_v2.json`
- Batch rollup: `tmp\claude_8_baseline_20260508\archival_row_ledger_v1_85pct_rollup.md`

Results:

- Selected score: `36 exact / 0 partial / 4 miss`.
- Exact lift over source-record V2: `+4`.
- Runtime load errors: `0`.
- Write proposal rows: `0`.

Meaning lesson:

Hospital proved the row-ledger distinction most sharply. Source-record V2 knew
that a packet recorded the event, but the archival row-ledger preserved the
printed source labels (`Pyxis MedStation 4000`, `Philips IntelliVue MX800`,
`ORD-882341`) that the benchmark asks for. A new selector guard was added:
printed source-provenance questions should prefer archival row/source labels
over generic packet identifiers.

The follow-up `archival_identifier_ledger_v1` probe confirmed the lexical-layer
diagnosis. Deterministic extraction of exact identifier-like spans improved
compile coverage and supplied one additional row rescue, but it also introduced
a badge-exit/timekeeping confusion. The successful selector therefore uses the
lexical lane as a candidate, not as a default, with a guard that keeps
timekeeping clock-out questions on timekeeping/assignment evidence rather than
physical badge-exit rows.
