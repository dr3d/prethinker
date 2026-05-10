# Estate Archive Access Dispute Progress Journal

Fixture id: `estate_archive_access_dispute`

This journal records durable research findings for this promoted incoming fixture.
Generated run artifacts may live under `tmp/`; lessons and artifact references belong here.

## EAAD-000 - Fixture Admission

Date: 2026-05-04

Evidence lane: `fixture_admission`

Source admitted from: `tmp\incoming\claude_md_split_raw\estate_archive_access_dispute`

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


## EAAD-001 - Claude 8 Cold Baseline

Date: 2026-05-08

Evidence lane: `cold_unseen_full40`

Artifacts:

- Compile: `tmp\claude_8_baseline_20260508\cold_compile\estate_archive_access_dispute\domain_bootstrap_file_20260508T170354663039Z_source_qwen-qwen3-6-35b-a3b.json`
- QA: `tmp\claude_8_baseline_20260508\qa_full40\estate_archive_access_dispute\domain_bootstrap_qa_20260508T172854094163Z_qa_qwen-qwen3-6-35b-a3b.json`

Results:

- Full-40 cold score: `21 exact / 9 partial / 10 miss`.
- Runtime load errors: `0`.
- Write proposal rows: `0`.

Meaning lesson:

This fixture entered the Claude 8 dense operational-record batch. The cold run
measures the instrument before any fixture-specific source-record repair. The
batch-level result exposed a compile coverage gap rather than a governance
breach: the model often understood the document type but failed to preserve the
source rows, exact identifiers, and archival addresses needed for scoring.

## EAAD-002 - Source-Record V2 Diagnostic Repair

Date: 2026-05-08

Evidence lane: `source_record_registry_scaffold`

Registry scaffold:

- `tmp\claude_8_baseline_20260508\registries\document_packet_source_record_registry_v2.json`

Artifacts:

- QA: `tmp\claude_8_baseline_20260508\repair_qa\estate_source_record_v2_all_candidates\domain_bootstrap_qa_20260508T222936109453Z_qa_qwen-qwen3-6-35b-a3b.json`
- Batch rollup: `tmp\claude_8_baseline_20260508\source_record_v2_80pct_rollup.md`

Results:

- Chosen diagnostic score: `29 exact / 5 partial / 6 miss`.
- Exact lift over cold: `+8`.
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

## EAAD-003 - Archival Row Ledger V1 Promotion Candidate

Date: 2026-05-08/09

Evidence lane: `archival_row_ledger_v1_probe`

Artifacts:

- Compile: `tmp\claude_8_baseline_20260508\repair_compile\estate_archive_access_dispute_archival_row_ledger_v1\domain_bootstrap_file_20260509T001558911286Z_source_qwen-qwen3-6-35b-a3b.json`
- Union: `tmp\claude_8_baseline_20260508\repair_union\estate_archive_access_dispute_archival_row_ledger_v1\domain_bootstrap_file_20260509T001634313682Z_estate-archive-access-dispute-archival-row-ledger-v1_qwen-qwen3-6-35b-a3b.json`
- QA: `tmp\claude_8_baseline_20260508\repair_qa\estate_archive_access_dispute_archival_row_ledger_v1\domain_bootstrap_qa_20260509T010444006315Z_qa_qwen-qwen3-6-35b-a3b.json`
- Batch rollup: `tmp\claude_8_baseline_20260508\archival_row_ledger_v1_85pct_rollup.md`

Results:

- Whole archival score: `36 exact / 3 partial / 1 miss`.
- Exact lift over source-record V2: `+7`.
- Runtime load errors: `0`.
- Write proposal rows: `0`.

Meaning lesson:

Estate is the strongest archival-row proof in the batch. Exhibit labels,
catalog IDs, receipt IDs, docket IDs, and manuscript identifiers are not
decoration; they are the address system through which the legal facts are
retrieved. The lens should stay as a measured candidate for archive-like
documents.

## EAAD-004 - Authority/Custody Helper Transfer Probe

Date: 2026-05-10

Evidence lane: `authority_custody_helper_transfer`

Artifacts:

- Baseline targeted QA: `tmp/helper_transfer_20260510/estate_source_record_v2_targeted/domain_bootstrap_qa_20260510T082822828819Z_qa_qwen-qwen3-6-35b-a3b.json`
- Helper targeted QA: `tmp/helper_transfer_20260510/estate_source_record_v2_object_custody_helper/domain_bootstrap_qa_20260510T083159022467Z_qa_qwen-qwen3-6-35b-a3b.json`
- Transfer note: `tmp/helper_transfer_20260510/authority_custody_helper_transfer_proof_20260510.md`

Results:

- Before helper transfer: `2 exact / 2 partial / 5 miss` on nine targeted rows.
- After helper transfer: `2 exact / 3 partial / 4 miss` on the same rows.
- `archive_authority_custody_support/5` fired on `object_custody_status/5`
  surfaces that were previously invisible to the helper.

Lesson:

The archive authority/custody helper transfers, but only to the boundary of
admitted state. Estate's source-record V2 compile already contained custody and
title rows as `object_custody_status/5`; exposing them through the helper moved
`q040` from miss to partial and improved support on several custody/title rows.
The remaining misses ask for procedural deferment, exact shelf/vault location,
probate authority, or pending-reply facts that were not admitted. Helper
propagation is useful here, but it cannot substitute for missing source surface.
