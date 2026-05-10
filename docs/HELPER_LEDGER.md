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
| `archive_authority_custody_support` | 2 | yes | split, audit ongoing | transfer: 0 clean / 4 candidate; precision: 1 clean / 11 candidate; probate live QA: 96 candidate / 0 clean | Generic object-custody/access/recalled-right joins can be clean on the precision authority artifact, but the probate transfer artifact currently emits candidate-only helper rows and regresses the cold score (`29 / 3 / 8` live helper replay versus `34 / 1 / 5` cold). | Genericize or retire family-specific count/source-cell recognizers before treating authority/probate saturation as clean-helper evidence. |
| `clear_sample_clock_pause_support` | 1 | yes | clean-helper | precision: 1 clean / 0 candidate | Joins admitted clear-sample segments, sampler-offline intervals, and rule exceptions. | Seek transfer fixture evidence; no cleanup needed in current code. |
| `clinic_recall_support` | 1 | yes | split, audit ongoing | transfer cold: 23 clean / 2 candidate; refreshed class audit: 29 clean / 0 candidate; fresh QA artifact: 2000 clean / 240 candidate / 0 unlabeled | Device/serial field rows plus generic manufacturer-liaison, verification-procedure, explicit clinic abbreviations, cabinet/seal range, failure-rate atoms, visit-date ranges, key-retainer identity, and medical-director authority are mostly clean when the needed source-record rows exist. A fresh no-cache QA replay over the refreshed artifact reduced unlabeled output but still emitted 240 candidate rows and scored `35 / 0 / 4` with one unjudged row; row-gating with the prior `40 / 0 / 0` high-water stays exact. | Keep the prior clinic high-water as candidate-helper score; genericize or retire the remaining candidate emissions before claiming clean-helper saturation. |
| `grant_award_support` | 1 | yes | clean-helper on transfer batch | transfer: 16 clean / 0 candidate | Award, cap, eligibility, field-recusal, appeal-window, committee-recusal vote-count, score-correction operational status, and appeal-pending status rows are clean over admitted predicates plus generic source-record atoms/sections. | Seek sibling transfer proof before treating the helper as broadly promoted; no current fixture constants remain in emitted rows. |
| `industrial_sensor_support` | 1 | yes | clean on refreshed artifact, transfer pending | transfer: 40 clean / 2 candidate; refreshed class audit: 33 clean / 0 candidate; fresh QA artifact: 2805 clean / 0 candidate / 0 unlabeled | Event/timestamp/count, computed duration, vendor/model, batch-id, ticket, packet-id, data-loss status, lab-sample status/return, system clock authority, and field-derived rows are clean after source-ledger anchor repair. A fresh no-cache QA replay over the refreshed artifact emitted clean labels end to end but scored only `28 / 2 / 9` with one unjudged row due query-generation churn; row-gating that run with the prior `39 / 1 / 0` high-water reaches `40 / 0 / 0`. | Treat industrial as clean-labeled on its refreshed source artifact but still one-fixture by usage count; seek sibling proof before promotion. |
| `probate_storage_support` | 1 | no | orphaned artifact helper | not applicable | Historical QA artifacts contain this helper and a `36 / 0 / 4` replay, but no current companion implementation is registered in the repo. A current live replay without the orphan scores `29 / 3 / 8`; a row gate across cold, orphan, and current surfaces reaches `40 / 0 / 0` only as historical diagnostic evidence. | Do not report old probate rows as active architecture; rebuild generically only if probate storage/access pressure remains important. |
| `roster_state_support` | 2 | yes | split, audit ongoing | transfer class audit: 63 clean / 117 candidate; usage audit: 8306 clean / 15660 candidate across completed QA artifacts | Admitted-predicate joins are clean. Source-record adult/compliance rows are clean narrow parses. Source-record student membership rows remain candidate: they transfer across two roster notations, but still derive membership from source-record text atoms and section context. A first deterministic `roster_table_member/4` ledger now captures explicit table rows with both grouping and member columns, moving that narrow surface out of helper inference. Group counts inherit clean/candidate status from their member rows. | Compare clean ledger wins against older helper wins, then add selector/query guidance only where the deterministic surface is missed. Context-derived bus/group membership remains candidate. |
| `source_record_clock_sync_support` | 1 | yes | clean-helper | precision: 2 clean / 0 candidate; q011 hygiene replay: 3 clean / 0 candidate | Deterministically extracts last-successful clock-sync dates from admitted source-record text/numeric rows. Rows now emit `SupportKind=last_successful_ntp_sync`, and the companion triggers for corrected/raw timestamp queries as well as clock-sync predicates. | Seek transfer fixture evidence; no cleanup needed in current code. |
| `source_record_packet_metadata_support` | 3 | yes | split, audit ongoing | transfer: 67 clean / 11 candidate; cleanup audit: 17 identifier kinds / 10 content-note kinds | Generic identifiers and packet metadata are clean. The remaining candidate rows are not identifier metadata; they are content notes such as appeal funding source, appeal pending status, observer permission scope, pending packet item, role definitions, and transport departure. | Keep generic identifiers; quarantine embedded content notes until moved to domain helpers or retired as duplicates. |

## Current Pressure

Latest usage audit:
`tmp/helper_usage_audit_20260510/helper_usage_audit_latest.md`

- QA JSON artifacts scanned: 473
- Helpers observed in usage audit: 9
- Suspicious low-transfer helpers, used on two or fewer fixtures: 8
- Orphaned artifact helpers: 1 (`probate_storage_support`)
- Helpers with row-level class audit coverage: 7

Fixtures per helper is the sharper pressure view right now. Only
`source_record_packet_metadata_support` appears on more than two fixtures in
completed QA artifacts. `roster_state_support` and
`archive_authority_custody_support` appear on two fixtures; every other helper
is still one-fixture by usage count. That does not make them wrong, but it means
their scores must remain labeled as narrow, candidate, or awaiting sibling proof
until the spread changes.
The probate replay makes this concrete: historical `probate_storage_support`
rows improve score but are orphaned, while current live
`archive_authority_custody_support` rows are candidate-only and currently weaker
than cold. Helper spread alone is not promotion evidence; the helper must be
current, labeled, and non-regressive or row-routed safely.

Helpers per fixture is also useful. The heaviest helper-dependent fixtures are
`school_activity_roster_reconciliation`,
`industrial_sensor_clock_correction`, `grant_exception_cap_matrix`, and
`probate_storage_access_register`, each with two helper surfaces. The remaining
observed fixtures use one helper surface. There is not yet evidence of fixtures
requiring a sprawling helper stack; the mess risk is concentrated in
low-transfer helper breadth, not helpers-per-fixture explosion.

Most historical QA artifacts still lack row-level `HelperClass` labels, so the
usage audit now reports those rows as `unlabeled` rather than silently omitting
them. Treat unlabeled helper rows as audit debt. A fresh industrial replay adds
`2805` clean `industrial_sensor_support` rows and `1450` clean
`source_record_packet_metadata_support` rows to completed QA output, but older
industrial artifacts still dominate the usage count as unlabeled. A fresh clinic
replay adds `2000` clean and `240` candidate `clinic_recall_support` rows to
completed QA output, reducing but not eliminating clinic label debt. Current
usage artifacts still show large unlabeled surfaces for `grant_award_support`
and `archive_authority_custody_support`; their separate class-audit reports
remain the authority for clean/candidate split until fresh QA artifacts carry
class labels end to end.

The high-pressure candidate surface is still `roster_state_support`. The roster
source-record parser is not a one-fixture scar anymore: it finds `108` candidate
assignment rows on `school_activity_roster_reconciliation` and `78` on the
sibling `count_composition_roster`, and completed sibling QA replays now make
`roster_state_support` visible on two fixtures. Focused homeroom prioritization
improves the sibling source-record V2 artifact from `27 / 4 / 9` to
`29 / 2 / 9`; source-record adult/compliance rows plus a narrow IR fallback for
no-query compliance intents move it to `30 / 2 / 8`. An artifact-only row gate
across old V2, focused homeroom, and adult/compliance surfaces reaches
`36 / 3 / 1`. Guarded selector discrimination reaches `34 / 2 / 4`, so remaining
pressure is row routing over emitted helper rows, not helper acquisition.
The roster candidate-label audit at
`tmp/helper_usage_audit_20260510/roster_state_candidate_label_audit.md` keeps
student membership rows candidate. A first deterministic roster-table ledger
now emits `roster_table_member/4` only when the source table has explicit group
and member columns. On `count_composition_roster` it emits `89` member facts;
on `school_activity_roster_reconciliation` it emits `0` because the relevant
bus tables lack a group column. That is the desired boundary: explicit table
membership can become deterministic memory, while section/prose-derived roster
membership stays candidate-helper until a stronger ledger design exists.
A narrowed QA planning hint for homeroom membership/count questions lifted the
table-ledger replay from `28 / 3 / 9` to `30 / 3 / 7` by routing q015 and q016
to `roster_table_member/4`; the guarded selector remains higher at `34 / 2 / 4`.
The next pressure is row routing and answer-surface handling, not broader roster
parsing.
The ledger also now preserves printed member labels via
`roster_table_member_label/5` and `roster_table_member_alias/2`, so
`STU-1063 Vinokur` can remain linked to normalized `stu_1063` without counting
as a second student. That rescues q023, and a narrow homeroom/roster-table
alias support path can make q024 exact by surfacing the current `v1_3 -> 7_b`
assignment. Full replay remains below the guarded selector because other rows
still churn; the next pressure is selector/answer routing, not more roster
parsing.
A row gate across old V2, focused homeroom, adult/compliance, narrow
table-guidance, and alias surfaces reaches `39 / 1 / 0`, with only q012
remaining partial. That is strong evidence the answerable memory surface is
present and the active runtime gap is selector discrimination plus one residual
distinct-count/composition row.
The first guarded selector replay over those five surfaces lands at only
`31 / 3 / 6`, selecting the best available row on `32 / 40`. The added
table/alias surfaces therefore need row-gating or risk-gating: they are valuable
when the question is explicitly homeroom/table/printed-label shaped, but should
not globally displace broader source-record or adult/compliance surfaces.
The residual q012 count/composition row is now covered by
`roster_table_count_support`, which derives entry count, distinct normalized
member count, duplicate members, and group counts from `roster_table_member/4`.
With that count surface included, the row-gated ceiling reaches `40 / 0 / 0`.
The guarded selector initially stayed at `31 / 3 / 6`, with `31 / 40`
selected-best rows, proving the active problem was selector/runtime routing
across complementary surfaces, not missing compiled memory.

A selector risk-gate replay now reaches `40 / 0 / 0` and `40 / 40`
selected-best over the six-mode package. The gates are question-shape based:
distinct student counts prefer `roster_table_count_support`; authoritative
homeroom rows prefer current member alias/table support; correction-notice rows
prefer explicit change surfaces; adult-total rows avoid qualifying-chaperone
counts; ratio-compliance rows prefer `compliance_status` over roster table
volume. This keeps the table/alias/count helpers valuable without letting their
row volume displace broader surfaces on unrelated policy or lookup rows.

The next cleanup work should reduce candidate or unlabeled helper rows and seek
sibling proof for one-fixture helpers rather than create new lenses.

`source_record_packet_metadata_support` now has an explicit cleanup readout at
`tmp/transfer_fixtures_20260510/source_record_packet_metadata_cleanup_20260510/packet_metadata_cleanup.md`.
The decision is no code change yet: the helper's clean surface is exact
identifier/addressability metadata, while its candidate surface is embedded
content notes. Those candidate rows should remain quarantined rather than being
promoted as metadata. Future cleanup should either move useful content notes
into domain helpers or retire them if duplicate.

## Promotion Rule

A helper is promoted only when it adds a general operation and survives fresh
transfer without fixture-shaped constants. Candidate helpers may rescue rows,
but their rows must be reported as `candidate-helper` until rewritten,
transfer-proven, or retired.
