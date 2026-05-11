# Helper Ledger

Last updated: 2026-05-11

This ledger tracks query helpers as first-class epistemic surface. It combines
two views:

- **fixtures per helper** from `scripts/audit_helper_usage.py`
- **row-level helper class** from `scripts/audit_helper_classes.py`

Read with:

- `docs/ARTIFACT_UNIT_AND_HELPER_CLASSIFICATION.md`
- `docs/EDGE_GOVERNANCE_POSITIONING.md`

The usage row counts below come from historical QA artifacts under
`tmp/transfer_fixtures_20260510` and `tmp/openrouter_precision_20260509`. Treat
them as pressure signals, not unique facts: a helper row can appear many times
across QA files.

## Summary Ledger

The compact table is the comparison surface. Longer evidence and caveats live
in the detail sections below.

| Helper | Fixtures | Implemented | Current Status | Audit Since | Last Changed | Next Action |
| --- | ---: | --- | --- | --- | --- | --- |
| `source_record_table_body_count_support` | 3 | yes | transfer-proven clean-helper for explicit body-count intents | 2026-05-10 | 2026-05-10 | Keep narrow; require explicit table/list/log body-count wording. |
| `item_description_detail_support` | 2 | yes | transfer-shown clean-helper over admitted description predicates | 2026-05-10 | 2026-05-11 | Keep promoted narrowly; do not infer missing descriptions from source text. |
| `source_record_packet_metadata_support` | 4 | yes | clean structural/addressability helper; content-note branches retired | 2026-05-10 | 2026-05-11 | Keep generic metadata/addressability rows only; move domain prose to domain helpers or leave retired. |
| `roster_state_support` | 2 | yes | split, audit ongoing; school packet notes migrated candidate-labeled | 2026-05-10 | 2026-05-11 | Prefer deterministic roster-table ledgers where available; keep section/prose membership and school packet prose candidate-labeled. |
| `archive_authority_custody_support` | 2 | yes | split, retirement candidate for probate paths | 2026-05-10 | 2026-05-10 | Quarantine old authority/probate paths; prefer packet metadata for probate standing/source/addressability. |
| `industrial_sensor_support` | 1 | yes | clean on refreshed artifact, transfer pending | 2026-05-10 | 2026-05-10 | Seek sibling proof before promotion. |
| `clinic_recall_support` | 1 | yes | split, audit ongoing | 2026-05-10 | 2026-05-10 | Genericize or retire remaining candidate rows before clean saturation claims. |
| `grant_award_support` | 2 | yes | split; clean alias bridge transfer-shown, appeal/procedure rows still candidate | 2026-05-10 | 2026-05-11 | Keep predicate aliases; quarantine source-prose appeal/procedure recognizers until genericized or retired. |
| `clear_sample_clock_pause_support` | 1 | yes | clean-helper, one-fixture | 2026-05-10 | 2026-05-10 | Seek transfer evidence; no cleanup needed now. |
| `source_record_clock_sync_support` | 1 | yes | clean-helper, one-fixture | 2026-05-10 | 2026-05-10 | Seek transfer evidence; no cleanup needed now. |
| `roster_table_count_support` | 1 | yes | clean deterministic roster-table companion, one-fixture | 2026-05-10 | 2026-05-10 | Keep as companion to `roster_table_member/4`; seek sibling tables. |
| `roster_table_member_alias_support` | 1 | yes | clean deterministic printed-label companion, one-fixture | 2026-05-10 | 2026-05-10 | Keep as companion to roster table ledger; seek sibling tables. |
| `homeroom_member_alias_support` | 1 | yes | clean narrow alias companion, one-fixture | 2026-05-10 | 2026-05-10 | Keep narrow; avoid promotion beyond homeroom/table membership. |
| `probate_storage_support` | 1 | no | orphaned artifact helper | 2026-05-10 | 2026-05-10 | Do not report as active architecture. |

## Helper Details

### Transfer-Proven Or Transfer-Shown Clean Helpers

`source_record_table_body_count_support`: transfer-proven clean-helper for
explicit table/list/log body-count intents. Audit views: probate residual probe
`5 clean / 0 candidate`; probate full replay `10 clean / 0 candidate`; sibling
artifact audit found clinic `1` row, industrial `5`, school `8`, grant `7`;
routed sibling QA reached `8 / 0 / 0` with clean helper rows and intentional
non-routing on semantic school/grant counts. It counts field-bearing
`source_record_row(..., table_row, ...)` body rows while excluding header rows.
Keep it narrow; do not make it a general count helper.

`item_description_detail_support`: transfer-shown clean-helper over admitted
description predicates. Audit views: probate residual probe `25 clean / 0
candidate`; probate full replay `62 clean / 0 candidate`; identifier focused
probe `33 clean / 0 candidate`; identifier source-record-facts probe after the
`evidence_item/2` bridge `48 clean / 0 candidate` with `4 / 0 / 0`. It derives
display titles and trailing years from admitted `item_description/2` or
equivalent `evidence_item/2` rows. It must not infer descriptions directly from
source text.

### Split Helpers Under Active Audit

`source_record_packet_metadata_support`: broadest helper by fixture spread.
Generic identifiers, source-reference list rows, filing-location metadata,
official-prose standing notes, role-holder headings, custody-location fields,
non-reproduced references, authoritative-source statements, asserted-event
dates, unruled-motion status, loan-amendment effects, court-order access joins,
court-order source-section rows, and non-revocable access-policy rows are clean
when mechanically derived from admitted predicates or source-record
atoms/sections/fields/numeric tokens. A 2026-05-11 retirement pass removed the
older candidate content-note rows for grant appeal/procedure prose and school
roster/travel prose. Fresh cold-transfer helper audit now shows
`source_record_packet_metadata_support` at `116 clean / 0 candidate / 0
unlabeled` across the six transfer fixtures.

`roster_state_support`: admitted-predicate joins are clean. Source-record
adult/compliance rows are clean narrow parses. Source-record student membership
rows remain candidate: they transfer across two roster notations, but still
derive membership from source-record text atoms and section context. The
deterministic `roster_table_member/4` ledger moves explicit table rows with both
grouping and member columns out of helper inference. Section/prose-derived
roster membership remains candidate-helper until a stronger ledger design
exists. After packet-metadata cleanup, three school packet prose rows migrated
here as candidate-helper rows: `school_packet_policy_title`,
`school_packet_retention_location`, and `school_packet_pending_item`. Targeted
school replay recovered `q003`, `q004`, and `q033` while packet metadata stayed
clean-only. A second 2026-05-11 migration added candidate rows for adult lodging,
bus departure, observer permission scope, temporary-assignment source notes, and
scanner clock-audit status. Targeted replay recovered `q009`, `q019`, `q021`,
and `q038`; `q006` remains an event-to-source linkage problem because
`temporary_event_assignment/4` lacks explicit section/note provenance.

`archive_authority_custody_support`: generic object-custody/access/recalled
right joins can be clean on the precision authority artifact, but the probate
transfer artifact emitted candidate-only helper rows and regressed cold (`29 /
3 / 8` live helper replay versus `34 / 1 / 5` cold). The active probate repair
path moved away from this helper and into clean `source_record_packet_metadata`
rows. Treat old probate/authority branches as retirement candidates unless new
fixtures prove they still add distinct clean capability.

`clinic_recall_support`: device/serial field rows plus generic
manufacturer-liaison, verification-procedure, explicit clinic abbreviations,
cabinet/seal range, failure-rate atoms, visit-date ranges, key-retainer
identity, and medical-director authority are mostly clean when the needed
source-record rows exist. Fresh QA still emitted candidate rows, so prior
clinic saturation is candidate-helper evidence until those emissions are
genericized, retired, or transfer-proven.

`grant_award_support`: award, cap, eligibility, field-recusal, appeal-window,
committee-recusal vote-count, score-correction operational status, and
appeal-pending status rows are mostly clean over admitted predicates plus
generic source-record atoms/sections. A scar cleanup removed hard-coded `a_07`
and `2026-05-22` assumptions; a later cleanup removed an `a_05` eligibility
detail branch. The helper now includes a clean admitted-predicate alias bridge
for older grant/rule vocabularies such as `final_grant_amount/3`,
`grant_calculation/4`, `grant_amount/2`, `application_status/2`,
`final_status/2`, `determination_status/2`, `eligibility_determination/3`, and
`bonus_qualification/3`. That bridge gives sibling evidence on
`rule_activation_exception_matrix` without fixture constants. Source-prose
appeal/procedure recognizers remain candidate-helper rows.

### Clean But Still One-Fixture

`industrial_sensor_support`: clean-labeled on refreshed industrial artifacts,
with field-driven event/timestamp/count, computed duration, vendor/model,
batch-id, ticket, packet-id, data-loss status, lab-sample status/return, system
clock authority, and field-derived rows. It still needs sibling proof before
promotion because fixture fanout is one.

`clear_sample_clock_pause_support`: joins admitted clear-sample segments,
sampler-offline intervals, and rule exceptions. It is currently clean but only
shown on `temporal_state_ledger`.

`source_record_clock_sync_support`: deterministically extracts
last-successful clock-sync dates from admitted source-record text/numeric rows.
It is clean but currently one-fixture.

`roster_table_count_support`, `roster_table_member_alias_support`, and
`homeroom_member_alias_support`: clean narrow companions around explicit roster
table ledgers and printed labels. Their legitimacy comes from their narrow
contract, not broad fixture spread yet.

### Orphaned Or Retired

`probate_storage_support`: historical QA artifacts contain this helper and a
`36 / 0 / 4` replay, but no current companion implementation is registered in
the repo. Do not report old probate rows as active architecture; rebuild
generically only if probate storage/access pressure remains important.

## Current Pressure

Latest usage audit:
`tmp/transfer_fixtures_20260510/helper_fixture_fanout_audit_20260511.md`

- QA JSON artifacts scanned: 554
- Helpers observed in usage audit: 14
- Suspicious low-transfer helpers, used on two or fewer fixtures: 12
- Orphaned artifact helpers: 1 (`probate_storage_support`)
- Helpers with broad fixture fanout: 2

Fixtures per helper is the sharper pressure view right now.
`source_record_packet_metadata_support` and
`source_record_table_body_count_support` now appear on more than two fixtures in
completed QA artifacts, though the latter is deliberately narrow: explicit
table/list/log body-count questions only. `roster_state_support`,
`archive_authority_custody_support`, and `item_description_detail_support`
appear on two fixtures; `item_description_detail_support` is transfer-shown as
clean substrate only when an item-description predicate such as
`item_description/2` or `evidence_item/2` has already been admitted. Every other
helper is still one-fixture by usage count. That does not make them wrong, but
it means their scores must remain labeled as narrow, candidate, or awaiting
sibling proof until the spread changes.
The probate replay makes this concrete: historical `probate_storage_support`
rows improve score but are orphaned, while the older live
`archive_authority_custody_support` rows were candidate-only and weaker than
cold. A later clean repair used refreshed deterministic source-record ledger
facts plus `source_record_packet_metadata_support`; the hard-row probe reached
`9 / 0 / 0` with only clean-helper rows. A follow-up query-scoping repair moved
the six residual rows to `6 / 0 / 0` with `115` clean-helper rows and no
candidate rows. The full replay stayed at `34 / 2 / 4`, so the remaining
probate pressure is query-planner/selector routing over clean rows rather than
helper acquisition. A later residual bridge added clean
`item_description_detail_support`, `source_record_table_body_count_support`,
and access-policy/order joins; a focused five-row probe reached `4 / 0 / 1`
and the best full replay reached `37 / 0 / 3`, with no candidate-helper rows.
The residual hard row was a source-record acquisition/staleness gap: the stale
compile artifact skipped the Section F continuation lines that name the
authoritative finding sources. A no-LLM source-record refresh increased probate
source-record rows from `122` to `169`; q040 then passed, q010/q040 passed
together after adding clean order-section support, and probate now has a
clean-helper row-gated `40 / 0 / 0` high-water from the refreshed artifact.
Helper spread alone is not promotion evidence; the helper must be current,
labeled, and non-regressive or row-routed safely.

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

`source_record_packet_metadata_support` first had an explicit cleanup readout at
`tmp/transfer_fixtures_20260510/source_record_packet_metadata_cleanup_20260510/packet_metadata_cleanup.md`.
A follow-up audit at
`tmp/transfer_fixtures_20260510/source_record_packet_metadata_candidate_audit_20260511.md`
found candidate content-note rows concentrated in grant appeal/procedure prose
and school roster/travel prose. Those branches have now been retired from packet
metadata. The helper's active surface is exact identifier/addressability
metadata and generic document-standing/source-reference rows.

## Retirement Candidates

Retirement is an architectural outcome, not a failure. A helper or helper branch
should retire when better compile acquisition, deterministic ledgers, or cleaner
generic helpers cover the same answer surface.

Current candidates:

- `probate_storage_support`: already orphaned. Historical rows are archaeology,
  not active architecture.
- `archive_authority_custody_support` probate branches: active probate repair
  moved to clean source-record packet metadata and access/order joins. Keep only
  branches that still prove distinct clean authority/custody value on sibling
  fixtures.
- Candidate content-note branches inside `source_record_packet_metadata_support`:
  retired 2026-05-11 from the broad packet-metadata helper. If any retired row
  proves answer-bearing, reintroduce it through a domain helper or a separately
  named generic prose helper, not through packet metadata.
- Candidate appeal/procedure branches inside `grant_award_support`: next audit
  decides whether these rewrite into generic source-record section/reference
  substrate or stay quarantined as one-fixture candidate evidence.
- Source-record student-membership branches inside `roster_state_support`: retire
  explicit table membership paths as deterministic roster-table ledgers cover
  them; keep section/prose membership candidate-labeled until a stronger ledger
  exists.

## Promotion Rule

A helper is promoted only when it adds a general operation and survives fresh
transfer without fixture-shaped constants. Candidate helpers may rescue rows,
but their rows must be reported as `candidate-helper` until rewritten,
transfer-proven, or retired.

Promotion path:

```text
candidate scar
  -> generic rewrite or declared lens companion
  -> targeted replay on origin fixture
  -> full replay/no-regression on origin fixture
  -> sibling transfer replay
  -> promotion or retirement
```

Every promoted helper must keep a retirement condition. The healthy long-term
trajectory is not that helper count grows forever; it is that helper count and
candidate-helper rows become measurable, then some retire as deterministic
ledgers and compile acquisition improve.
