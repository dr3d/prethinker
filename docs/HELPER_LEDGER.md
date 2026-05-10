# Helper Ledger

Last updated: 2026-05-10

This ledger tracks query helpers as first-class epistemic surface. It combines
two views:

- **fixtures per helper** from `scripts/audit_helper_usage.py`
- **row-level helper class** from `scripts/audit_helper_classes.py`

The usage row counts below come from historical QA artifacts under
`tmp/transfer_fixtures_20260510` and `tmp/openrouter_precision_20260509`. Treat
them as pressure signals, not unique facts: a helper row can appear many times
across QA files.

## Ledger

| Helper | Fixtures | Implemented | Current Class | Class Audit Rows | Current Read | Next Action |
| --- | ---: | --- | --- | --- | --- | --- |
| `archive_authority_custody_support` | 2 | yes | split, audit ongoing | transfer: 0 clean / 4 candidate; precision: 1 clean / 11 candidate | Generic object-custody/access/recalled-right joins are clean; older Pellico/Stille/Halberd source-cell and text recognizers remain candidate. | Genericize or retire family-specific count/source-cell recognizers before treating authority saturation as clean-helper evidence. |
| `clear_sample_clock_pause_support` | 1 | yes | clean-helper | precision: 1 clean / 0 candidate | Joins admitted clear-sample segments, sampler-offline intervals, and rule exceptions. | Seek transfer fixture evidence; no cleanup needed in current code. |
| `clinic_recall_support` | 1 | yes | split, audit ongoing | transfer cold: 23 clean / 2 candidate; refreshed clinic: 29 clean / 0 candidate | Device/serial field rows plus generic manufacturer-liaison, verification-procedure, explicit clinic abbreviations, cabinet/seal range, failure-rate atoms, visit-date ranges, key-retainer identity, and medical-director authority are clean when the needed source-record rows exist. The old transfer artifact leaves key-retainer and authority rows candidate because it lacks blockquoted sender/role text atoms; a refreshed compile after the blockquote ledger repair makes the helper fully clean. | Use refreshed source-record ledgers before claiming clean clinic high-water; stale artifacts should keep sender-dependent rows candidate-labeled. |
| `grant_award_support` | 1 | yes | clean-helper on transfer batch | transfer: 16 clean / 0 candidate | Award, cap, eligibility, field-recusal, appeal-window, committee-recusal vote-count, score-correction operational status, and appeal-pending status rows are clean over admitted predicates plus generic source-record atoms/sections. | Seek sibling transfer proof before treating the helper as broadly promoted; no current fixture constants remain in emitted rows. |
| `industrial_sensor_support` | 1 | yes | split, audit ongoing | transfer: 40 clean / 2 candidate; refreshed industrial: 33 clean / 0 candidate | Event/timestamp/count, computed duration, vendor/model, batch-id, ticket, packet-id, data-loss status, lab-sample status/return, system clock authority, and field-derived rows are mostly clean after recent cleanup. The old transfer artifact leaves only the root-cause packet-scope and operator-origin rows candidate because it does not preserve the necessary refusal/provenance prose. A refreshed compile after the source-ledger anchor repair preserves those lines and makes the helper output fully clean for that artifact. Two stated-duration recognizers were retired as duplicate/overclaiming scar rows. | Treat stale root-cause/operator rows as source-acquisition artifacts; use refreshed source-record ledgers before claiming clean industrial high-water. |
| `probate_storage_support` | 1 | no | orphaned artifact helper | not applicable | Historical QA artifacts contain this helper, but no current companion implementation is registered in the repo. | Do not report old probate rows as active architecture; rebuild generically only if probate pressure returns. |
| `roster_state_support` | 1 | yes | split, audit ongoing | transfer: 63 clean / 117 candidate | Admitted-predicate joins are clean; source-record roster parsing over `v1/v2/v3`, `group_a/group_b/group_c`, and `s_###` shapes is candidate. | Generalize roster parser or prove transfer on sibling roster fixtures before promotion. |
| `source_record_clock_sync_support` | 1 | yes | clean-helper | precision: 2 clean / 0 candidate | Deterministically extracts last-successful clock-sync dates from admitted source-record text/numeric rows. | Seek transfer fixture evidence; no cleanup needed in current code. |
| `source_record_packet_metadata_support` | 3 | yes | split, audit ongoing | transfer: 67 clean / 11 candidate | Generic identifiers and packet metadata are clean; packet-family physical retention/pending/role-scope notes remain candidate. | Keep generic identifiers; rewrite or quarantine embedded packet-family facts. |

## Current Pressure

- Helpers observed in usage audit: 9
- Suspicious low-transfer helpers, used on two or fewer fixtures: 8
- Orphaned artifact helpers: 1 (`probate_storage_support`)
- Helpers with row-level class audit coverage: 7

The high-pressure candidate surface is now primarily `roster_state_support`.
`clinic_recall_support` and `industrial_sensor_support` are mostly blocked only
by stale source-record artifacts; `grant_award_support` is clean on the current
transfer batch pending sibling proof.
The next cleanup work should reduce candidate rows inside those helpers rather
than create new lenses.

## Promotion Rule

A helper is promoted only when it adds a general operation and survives fresh
transfer without fixture-shaped constants. Candidate helpers may rescue rows,
but their rows must be reported as `candidate-helper` until rewritten,
transfer-proven, or retired.
