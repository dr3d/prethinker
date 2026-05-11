# Selector Guard Family Rollup

This report keeps the selector guard surface from turning into a pile of
fixture-shaped knobs. Individual guards are allowed while they are being
measured, but they should collapse into a small number of semantic families
before they become daily-driver harness doctrine.

Generated from `scripts/select_qa_mode_without_oracle.py`.

Companion audit ledger: [SELECTOR_GUARD_LEDGER.md](https://github.com/dr3d/prethinker/blob/main/docs/SELECTOR_GUARD_LEDGER.md).

## Summary

- guard return sites: `175`
- unique guard reasons: `175`
- classified families: `7`
- unclassified reasons: `0`
- duplicate guard reasons: `0`

## Growth Health

- status: `pass`
- family budget: `7 / 8`
- largest family: `operational_record_status` with `38` guards (`0.217` share)
- unique reason ratio: `1.0`
- guards per family: `25.0`
- unique reasons per family: `25.0`

Raw guard instances may grow during fixture farming, but semantic compression depends on low family count, zero unclassified reasons, no single family becoming a dumping ground, and no parameterized family hiding a large private enumeration table.

## Family Counts

| Family | Count | Purpose |
| --- | ---: | --- |
| `entity_role_authority` | 29 | Separate identity, role definition, acting authority, collector, contract authority, and guardianship rows from broad action or title-only evidence. |
| `operational_record_status` | 38 | Protect current status, request timing, commit readiness, decision, priority, concern, constitution, and resubmission rows from nearby but less answer-bearing record/event surfaces. |
| `rationale_evidence_contrast` | 36 | Route why/cause, witness/report, source-note, split rationale, viability contrast, and pending test questions to explicit rationale or evidentiary support instead of adjacent status rows. |
| `regulatory_access_scope` | 5 | Route all/any scope, termination denial, affected-lot exclusion, and reclassification-deadline questions to access surfaces that carry the right set, threshold, target, or temporal boundary. |
| `rule_activation_surface` | 20 | Route promoted rule, eligibility, recall, recusal, window, rejection, and reserve questions to the evidence surface that contains both the governing condition and the instance facts needed to apply it. |
| `state_custody_ownership` | 20 | Separate current object state, custody transfer, possession, ownership, legal title, and award/result surfaces from generic event, property, or person rows. |
| `threshold_policy_arithmetic` | 27 | Prefer direct threshold, quantity, storage, policy-action, and arithmetic inputs when a broader policy or derived-status surface is tempting but incomplete. |

## Guard Reasons

### `entity_role_authority`

- `identity question has baseline name/role support and candidate is broad action-heavy` (scripts/select_qa_mode_without_oracle.py:885)
- `badge-id question with unresolved holder needs identity-status badge surface rather than nearest source-record usage` (scripts/select_qa_mode_without_oracle.py:999)
- `same-item question needs current item identity/description surface rather than withdrawn-label evidence alone` (scripts/select_qa_mode_without_oracle.py:1010)
- `publication-authority question needs publication holder plus active restriction surface rather than broad access-authority volume` (scripts/select_qa_mode_without_oracle.py:1032)
- `arbitrator-unresolved-question row needs dispute-scope/topic surface rather than broad dispute-status volume` (scripts/select_qa_mode_without_oracle.py:1065)
- `road-jurisdiction authority question needs archival layer value surface rather than broad source status` (scripts/select_qa_mode_without_oracle.py:1132)
- `authoritative-homeroom question needs current member alias/table surface before correction-history rows` (scripts/select_qa_mode_without_oracle.py:1173)
- `authoritative-homeroom question needs focused current roster helper rows` (scripts/select_qa_mode_without_oracle.py:1183)
- `authoritative-homeroom question needs current roster membership surface rather than correction-action text alone` (scripts/select_qa_mode_without_oracle.py:1188)
- `bus-assignment correction question needs bus-assignment plus change-type surface rather than roster table identity rows` (scripts/select_qa_mode_without_oracle.py:1197)
- `school-principal identity question needs source-record authority surface rather than roster row volume` (scripts/select_qa_mode_without_oracle.py:1269)
- `school role/driver identity question needs direct role predicate rather than row-value volume` (scripts/select_qa_mode_without_oracle.py:1346)
- `student-location supervision question needs statement plus event-attribute surface rather than role roster volume` (scripts/select_qa_mode_without_oracle.py:1391)
- `collector identity question needs direct collector predicate surface rather than broad status/note evidence` (scripts/select_qa_mode_without_oracle.py:1513)
- `station-supervisor question needs explicit station_supervisor surface rather than standing group-supervision rows` (scripts/select_qa_mode_without_oracle.py:1659)
- `festival-director identity question needs direct person-role surface rather than meeting/ruling volume` (scripts/select_qa_mode_without_oracle.py:1688)
- `superlative identity question needs explicit age/identity surface rather than broad role membership rows` (scripts/select_qa_mode_without_oracle.py:1699)
- `official identity question needs role-authority definition surface rather than action volume or title-only rows` (scripts/select_qa_mode_without_oracle.py:1712)
- `reinstatement question needs focused role-history surface rather than broad current-role or rule evidence` (scripts/select_qa_mode_without_oracle.py:1750)
- `contract-validity question needs explicit acting-authority surface rather than generic rule evidence` (scripts/select_qa_mode_without_oracle.py:1789)
- `contract-validity question needs authority-source surface rather than unrelated ownership or entity rows` (scripts/select_qa_mode_without_oracle.py:1796)
- `guardianship-validity question needs residence/resumption condition surface rather than bare guardianship status` (scripts/select_qa_mode_without_oracle.py:1912)
- `destruction-supervisor question needs person role plus destruction event surface` (scripts/select_qa_mode_without_oracle.py:2090)
- `recovery-identity question needs direct testimony/recovery surface rather than custody or zone rows` (scripts/select_qa_mode_without_oracle.py:2099)
- `substitute-scorer identity question needs compact service-role surface rather than certification/result volume` (scripts/select_qa_mode_without_oracle.py:2166)
- `same-name distinction question needs alias plus group-membership surface rather than identity table alone` (scripts/select_qa_mode_without_oracle.py:2256)
- `surveyor-certification lapse question needs direct certification-status surface rather than survey-result role rows` (scripts/select_qa_mode_without_oracle.py:2283)
- `intake-actor question needs explicit item-received-from provenance surface` (scripts/select_qa_mode_without_oracle.py:2417)
- `intake-actor question needs handoff/location event surface rather than ledger-entry rows alone` (scripts/select_qa_mode_without_oracle.py:2426)

### `operational_record_status`

- `status question has direct baseline status/rule support` (scripts/select_qa_mode_without_oracle.py:903)
- `status question has direct baseline application/status support and candidate is broad or relaxed-heavy` (scripts/select_qa_mode_without_oracle.py:917)
- `response-content question needs compact filed-response surface rather than broad procedural expansion` (scripts/select_qa_mode_without_oracle.py:929)
- `contract-rescission status question needs request/outcome surface rather than approval vote surface alone` (scripts/select_qa_mode_without_oracle.py:943)
- `snapshot-state question needs sampler state-plus-cause surface when the snapshot row asks why that state held` (scripts/select_qa_mode_without_oracle.py:974)
- `snapshot-state question needs sampler status surface rather than broad event-description volume` (scripts/select_qa_mode_without_oracle.py:981)
- `snapshot-state question needs explicit sampler_state surface rather than broad event-description or status volume` (scripts/select_qa_mode_without_oracle.py:988)
- `expected-order question needs explicit expected-order surface rather than open-exception volume` (scripts/select_qa_mode_without_oracle.py:1103)
- `communications-officer drafting question needs notice-issued plus person-role surface rather than name lookup alone` (scripts/select_qa_mode_without_oracle.py:1150)
- `homeroom-reassignment correction question needs homeroom_reassigned surface rather than generic change-type rows` (scripts/select_qa_mode_without_oracle.py:1206)
- `trip-date question needs roster-state schedule surface rather than roster-version/source-record volume` (scripts/select_qa_mode_without_oracle.py:1251)
- `erratum report-of-record question needs archival document/version surface rather than generic document-status rows` (scripts/select_qa_mode_without_oracle.py:1355)
- `review-completion question needs explicit status-at surface rather than broad uncertainty labels` (scripts/select_qa_mode_without_oracle.py:1364)
- `date-event anchor enumeration needs incident-anchor surface rather than source-section volume` (scripts/select_qa_mode_without_oracle.py:1427)
- `governing-board vote-status question needs explicit pending-determination surface rather than unrelated negative records` (scripts/select_qa_mode_without_oracle.py:1436)
- `court-determination question needs packet/source status surface rather than broad unresolved labels` (scripts/select_qa_mode_without_oracle.py:1465)
- `resolved-status question needs direct unresolved/disputed-status surface rather than archival evidence volume` (scripts/select_qa_mode_without_oracle.py:1495)
- `planning-application request question needs application-summary plus unit-mix surface rather than claim/status volume` (scripts/select_qa_mode_without_oracle.py:1522)
- `prior-proposal disposition question needs proposal-version/procedural-status surface rather than current-application volume` (scripts/select_qa_mode_without_oracle.py:1542)
- `contract-rescission status question keeps request/outcome surface over approval vote surface alone` (scripts/select_qa_mode_without_oracle.py:1571)
- `appeal-status question needs appeal event plus no-decision/deadline surface rather than bare docket status` (scripts/select_qa_mode_without_oracle.py:1628)
- `temporary-availability question needs attendance plus authority-transfer surface` (scripts/select_qa_mode_without_oracle.py:1639)
- `temporary-role question needs roster-state role-hint support rather than bare group membership` (scripts/select_qa_mode_without_oracle.py:1668)
- `completion-report incident list needs trip-outcome plus issue/medical/hazard surfaces` (scripts/select_qa_mode_without_oracle.py:1679)
- `current operational status question needs explicit final-state surface rather than adjacent event/action evidence` (scripts/select_qa_mode_without_oracle.py:1921)
- `public-use extension question needs extension purpose/status surface rather than broad permit lifecycle volume` (scripts/select_qa_mode_without_oracle.py:1930)
- `temporary-supervisor absence question needs location-change plus supervision/medical-event surface` (scripts/select_qa_mode_without_oracle.py:2191)
- `post-reassignment group-count question needs stable membership/count surface over role-task volume` (scripts/select_qa_mode_without_oracle.py:2205)
- `temporary-team roster question needs scoped group-formation surface rather than standing roster volume` (scripts/select_qa_mode_without_oracle.py:2225)
- `no-touch hazard question needs incident/hazard observation surface rather than broad attendance roster` (scripts/select_qa_mode_without_oracle.py:2247)
- `adjusted-expiration question needs explicit current-expiration surface rather than extension-label or original-date evidence` (scripts/select_qa_mode_without_oracle.py:2445)
- `commit-readiness question needs unresolved process evidence rather than a bare status value` (scripts/select_qa_mode_without_oracle.py:2481)
- `priority question needs explicit priority predicate surface rather than an underlying condition predicate` (scripts/select_qa_mode_without_oracle.py:2515)
- `decision-status question needs explicit decision surface rather than adjacent application/status evidence` (scripts/select_qa_mode_without_oracle.py:2528)
- `board-concern decision question needs event/action concern history rather than bare pending status` (scripts/select_qa_mode_without_oracle.py:2537)
- `deaccession-yet question needs explicit scheduled/not-formally-completed status surface rather than broad lot-history volume` (scripts/select_qa_mode_without_oracle.py:2563)
- `current-constitution eligibility question needs applicant-type plus controlling interpretation surface` (scripts/select_qa_mode_without_oracle.py:2622)
- `resubmission eligibility question needs proof/rule resolution surface rather than current applicant status surface` (scripts/select_qa_mode_without_oracle.py:2643)

### `rationale_evidence_contrast`

- `memo-establish question needs memo-content plus reliability-scope surface rather than broad investigative context` (scripts/select_qa_mode_without_oracle.py:1114)
- `phone-ping granularity question needs device-ping granularity surface rather than evidence-source summary` (scripts/select_qa_mode_without_oracle.py:1123)
- `negative-reliability question needs source-reliability scope rather than unresolved-activity status alone` (scripts/select_qa_mode_without_oracle.py:1141)
- `memo-resolution question needs claim plus unresolved-issue surface rather than permit/status fragments` (scripts/select_qa_mode_without_oracle.py:1327)
- `reply-memo theory question needs archival memo row value rather than generic source-document presence` (scripts/select_qa_mode_without_oracle.py:1474)
- `false-conflict consistency question needs paired intake/photo interpretation surface rather than row ledger fragments` (scripts/select_qa_mode_without_oracle.py:1504)
- `failed-vendor rationale question needs itemized vendor-deficiency surface` (scripts/select_qa_mode_without_oracle.py:1985)
- `failed-vendor rationale question needs inspection, vendor-status, and violation-detail surfaces together` (scripts/select_qa_mode_without_oracle.py:1992)
- `display-outcome question needs inspection/outcome plus permit-status surface` (scripts/select_qa_mode_without_oracle.py:2021)
- `display-outcome question needs date-specific permit validity plus incident/inspection surface` (scripts/select_qa_mode_without_oracle.py:2028)
- `second-violation duration question needs violation-record plus suspension-period surfaces together` (scripts/select_qa_mode_without_oracle.py:2037)
- `status-elevation rationale question needs lab/location/status context rather than bare status-change reason` (scripts/select_qa_mode_without_oracle.py:2081)
- `source-belief question needs claimant testimony surface rather than identification-status summary` (scripts/select_qa_mode_without_oracle.py:2112)
- `alternative-inscription question needs candidate-origin plus inscription/attribute surface` (scripts/select_qa_mode_without_oracle.py:2123)
- `missing-evidence question needs claimant testimony plus explicit absence/claim surfaces` (scripts/select_qa_mode_without_oracle.py:2150)
- `banner-change rationale question needs banner succession/creation surface rather than protest or score rows` (scripts/select_qa_mode_without_oracle.py:2159)
- `hold-call rationale question needs event-condition timing surface rather than broad witness/incident volume` (scripts/select_qa_mode_without_oracle.py:2173)
- `yellow-to-blue reassignment question keeps baseline transition surface over partial interval membership rows` (scripts/select_qa_mode_without_oracle.py:2198)
- `source-specific witness question needs Brigid report/claim surface rather than unresolved-discrepancy summary` (scripts/select_qa_mode_without_oracle.py:2216)
- `day-3 found-object question needs focused event/found-object surface rather than broad hazard summary` (scripts/select_qa_mode_without_oracle.py:2236)
- `conservator-date question needs source-recorded value surface rather than generic discrepancy rows` (scripts/select_qa_mode_without_oracle.py:2265)
- `display-authority question needs controlling governance/source-authority surface rather than display text rows` (scripts/select_qa_mode_without_oracle.py:2274)
- `source-claim question needs witness-statement surface rather than finding/provenance summary rows` (scripts/select_qa_mode_without_oracle.py:2301)
- `permission-request question needs direct witness-statement surface rather than evidence-date volume` (scripts/select_qa_mode_without_oracle.py:2310)
- `survey-commission question needs explicit report-commission provenance surface` (scripts/select_qa_mode_without_oracle.py:2319)
- `maintenance-evidence question needs receipt/evidence-source surface rather than witness/hearsay rows` (scripts/select_qa_mode_without_oracle.py:2335)
- `fictional-order question needs plot-outcome surface rather than plot-event summary rows` (scripts/select_qa_mode_without_oracle.py:2347)
- `boundary-discrepancy cause question needs measurement/marker-shift surface rather than survey-summary rows` (scripts/select_qa_mode_without_oracle.py:2361)
- `discrepancy-explanation question needs factual-discrepancy/incident-outcome surface rather than fictional event rows` (scripts/select_qa_mode_without_oracle.py:2399)
- `correction-authorship question needs handwriting/expert-attribution surface rather than correction-status volume` (scripts/select_qa_mode_without_oracle.py:2435)
- `evidentiary-status report question needs explicit witness/report surface rather than generic claim-status surface` (scripts/select_qa_mode_without_oracle.py:2467)
- `cause question has explicit baseline rationale-note support and candidate is broad record/event surface` (scripts/select_qa_mode_without_oracle.py:2502)
- `not-yet-tested question needs explicit pending test-status surface rather than broad negation over all lots` (scripts/select_qa_mode_without_oracle.py:2546)
- `split rationale question needs explicit source-note rationale plus viability context` (scripts/select_qa_mode_without_oracle.py:2574)
- `split rationale question needs actual split/lot-condition surface rather than generic vault assignment surface` (scripts/select_qa_mode_without_oracle.py:2588)
- `viability-concern question needs explicit source-note contrast plus viability context` (scripts/select_qa_mode_without_oracle.py:2599)

### `regulatory_access_scope`

- `personal-letter reading-access question needs semantic access authority plus publication-restriction boundary, not raw source rows alone` (scripts/select_qa_mode_without_oracle.py:1045)
- `universal-scope question needs broad set-enumeration surface rather than narrower report-detail joins` (scripts/select_qa_mode_without_oracle.py:1806)
- `lot-affected question needs explicit target-lot exclusion/check surface rather than broad affected-lot listing` (scripts/select_qa_mode_without_oracle.py:1815)
- `split-lot never-quarantined count needs quarantine-scope surface rather than broad lot status history` (scripts/select_qa_mode_without_oracle.py:2054)
- `initial-affected greenhouse question needs greenhouse-status plus exclusion/location surface` (scripts/select_qa_mode_without_oracle.py:2063)

### `rule_activation_surface`

- `rescission-request eligibility question needs request/validity surface rather than generic vote-rule volume` (scripts/select_qa_mode_without_oracle.py:935)
- `rule-effect question needs archival memo row value rather than ownership/status rows` (scripts/select_qa_mode_without_oracle.py:1282)
- `revised-plan monitoring question needs plan/rejection rule surface rather than observation-status rows` (scripts/select_qa_mode_without_oracle.py:1606)
- `appeal-tolling question needs rule text plus appeal/deadline surface rather than isolated tolling labels` (scripts/select_qa_mode_without_oracle.py:1617)
- `deferment-rationale question needs interpreted decision support rather than rule text alone` (scripts/select_qa_mode_without_oracle.py:1824)
- `component-problem question needs project-category plus rule-condition surface` (scripts/select_qa_mode_without_oracle.py:1833)
- `recusal-rationale question needs recusal rule surface rather than eligibility determination surface` (scripts/select_qa_mode_without_oracle.py:1842)
- `post-recusal vote question needs recusal/vote/rule surface without misleading quorum-status volume` (scripts/select_qa_mode_without_oracle.py:1851)
- `window-merit question needs explicit rule-condition plus prior-history surface` (scripts/select_qa_mode_without_oracle.py:1860)
- `window-merit question needs prior-history plus interpretation surface` (scripts/select_qa_mode_without_oracle.py:1869)
- `amendment-recall question needs recall-authority surface rather than threshold-only legal-opinion rows` (scripts/select_qa_mode_without_oracle.py:1880)
- `rejection-cause question needs correction/clarification surface rather than derived status alone` (scripts/select_qa_mode_without_oracle.py:1889)
- `hypothetical reserve-status question keeps baseline arithmetic inputs over derived rule status` (scripts/select_qa_mode_without_oracle.py:1896)
- `hypothetical reserve-status question needs baseline arithmetic inputs rather than derived rule status` (scripts/select_qa_mode_without_oracle.py:1903)
- `valid-period extension question needs original validity plus extension-validity surface` (scripts/select_qa_mode_without_oracle.py:1939)
- `unrenewed-expiry question needs original validity endpoint surface rather than renewed lifecycle rows` (scripts/select_qa_mode_without_oracle.py:1958)
- `appeal-hearing question needs filed-appeal/hearing-scheduled surface rather than broad status rows` (scripts/select_qa_mode_without_oracle.py:1967)
- `suspension-trigger question needs explicit violation-record plus permit-suspension surface` (scripts/select_qa_mode_without_oracle.py:1976)
- `permitted-hours question needs explicit operational-hours rule surface` (scripts/select_qa_mode_without_oracle.py:2001)
- `approved-display count question needs approval/validity surface rather than broad current-status rows` (scripts/select_qa_mode_without_oracle.py:2012)

### `state_custody_ownership`

- `award/result question has baseline awarded support and candidate lacks awarded rows` (scripts/select_qa_mode_without_oracle.py:894)
- `near-duplicate bin-code question needs collision-risk plus bin-location surface rather than generic current-label rows` (scripts/select_qa_mode_without_oracle.py:1019)
- `governing-2024-custody-document question needs exact amendment source-row text with custody/notice clauses` (scripts/select_qa_mode_without_oracle.py:1056)
- `location-plus-publication-pause question needs custody plus publication restriction surface` (scripts/select_qa_mode_without_oracle.py:1076)
- `MOU-scope expansion question needs agreement-clause plus access/addition surface rather than static right-scope volume` (scripts/select_qa_mode_without_oracle.py:1085)
- `custody-release question needs custody/status surface rather than scan-record volume` (scripts/select_qa_mode_without_oracle.py:1094)
- `barcode-supersession question needs scan/correction surface rather than broad current-barcode volume` (scripts/select_qa_mode_without_oracle.py:1260)
- `tree-amendment measurement question needs archival row-value surface preserving species/DBH/source basis` (scripts/select_qa_mode_without_oracle.py:1291)
- `dated physical-location question needs archival row location plus row-time support rather than synthesized cold self-check` (scripts/select_qa_mode_without_oracle.py:1454)
- `current object-component question needs direct current-state/component surface rather than transition history volume` (scripts/select_qa_mode_without_oracle.py:1721)
- `why-have question needs custody-transfer surface rather than adjacent action or object-property rows` (scripts/select_qa_mode_without_oracle.py:1730)
- `award placement question needs explicit award-result surface rather than nearby device/person rows` (scripts/select_qa_mode_without_oracle.py:1739)
- `carry question needs direct possession surface rather than broad title or event evidence` (scripts/select_qa_mode_without_oracle.py:1760)
- `possession-versus-ownership question needs inherit/own/possess distinction surface rather than broad event/rule evidence` (scripts/select_qa_mode_without_oracle.py:1771)
- `legal-title contest question needs claim/default/transfer surface rather than static ownership rows` (scripts/select_qa_mode_without_oracle.py:1780)
- `insurance-link question needs direct insured-by surface rather than contingent ownership claim rows` (scripts/select_qa_mode_without_oracle.py:2141)
- `disputed-strip feature question needs object-location surface rather than broad finding/survey rows` (scripts/select_qa_mode_without_oracle.py:2292)
- `physical inventory count question needs incident/count outcome surface rather than title-name rows` (scripts/select_qa_mode_without_oracle.py:2387)
- `client-ledger pickup question needs asset-state/location surface rather than broad item provenance rows` (scripts/select_qa_mode_without_oracle.py:2408)
- `correction-entitlement question needs entitlement rule plus extension effect surface rather than correction/admission rows alone` (scripts/select_qa_mode_without_oracle.py:2458)

### `threshold_policy_arithmetic`

- `density-calculation question needs numeric staff-evaluation surface rather than qualitative source-opinion surface` (scripts/select_qa_mode_without_oracle.py:922)
- `adult-total roster question needs adult manifest support rather than qualifying-chaperone count alone` (scripts/select_qa_mode_without_oracle.py:1215)
- `ratio-compliance question needs compliance_status surface rather than roster-table version volume` (scripts/select_qa_mode_without_oracle.py:1224)
- `correction-notice replacement question needs change-type surface rather than unparsed correction-action text` (scripts/select_qa_mode_without_oracle.py:1233)
- `projection-supersession question needs trigger/actual event surface rather than projection-comparison volume` (scripts/select_qa_mode_without_oracle.py:1242)
- `operative-permit question needs permit issuance/amendment surface rather than source-document status alone` (scripts/select_qa_mode_without_oracle.py:1300)
- `remedy-imposition question needs unresolved-issue surface rather than remedy-label presence` (scripts/select_qa_mode_without_oracle.py:1309)
- `hearing-held question needs event/open-issue surface rather than scheduled-date presence` (scripts/select_qa_mode_without_oracle.py:1318)
- `packet-time measurement question needs direct measurement-value surface rather than row-value volume` (scripts/select_qa_mode_without_oracle.py:1336)
- `roster-of-record membership question needs assigned/person roster surface rather than supersession metadata` (scripts/select_qa_mode_without_oracle.py:1373)
- `withdrawn-draft governance question needs source-status/supersession surface rather than document-id presence` (scripts/select_qa_mode_without_oracle.py:1382)
- `parent-letter determination question needs review-scheduled/letter surface rather than source-document volume` (scripts/select_qa_mode_without_oracle.py:1400)
- `witness-scan reconciliation question needs direct scan/location surface rather than broad source-record claims` (scripts/select_qa_mode_without_oracle.py:1409)
- `newsletter-versus-roster authority question needs supersession/roster evidence rather than stale assignment rows` (scripts/select_qa_mode_without_oracle.py:1418)
- `scoped roster-count question needs source-record roster section surface rather than badge/log volume` (scripts/select_qa_mode_without_oracle.py:1445)
- `deed item-count question needs conveyed-item surface rather than broad receipt row volume` (scripts/select_qa_mode_without_oracle.py:1483)
- `zoning-designation question needs parcel-zoning surface rather than general zoning-definition volume` (scripts/select_qa_mode_without_oracle.py:1531)
- `build-out timeline question needs site-measure plus draft-condition surface rather than permit-expiry status alone` (scripts/select_qa_mode_without_oracle.py:1551)
- `dimensional-standards question needs staff-finding plus site-measure surface rather than consolidated compliance status alone` (scripts/select_qa_mode_without_oracle.py:1562)
- `deadline-filing timeliness question needs filed-event plus calculated-deadline surface` (scripts/select_qa_mode_without_oracle.py:1584)
- `board-review-period question needs calculated-deadline surface rather than loose deadline values` (scripts/select_qa_mode_without_oracle.py:1595)
- `attendance-count question needs explicit session_attendance_count surface rather than interval roster volume` (scripts/select_qa_mode_without_oracle.py:1650)
- `lot-3b lab-result question needs lab-result plus lot-status context, not generic lab-result volume` (scripts/select_qa_mode_without_oracle.py:2072)
- `candidate-vessel list question needs candidate-origin plus vessel-loss detail surface` (scripts/select_qa_mode_without_oracle.py:2132)
- `corrected-rank-order question needs qualifying-rank plus score-correction surface rather than raw total volume` (scripts/select_qa_mode_without_oracle.py:2182)
- `claim-value question needs financial-value/incident-outcome surface rather than claim/status fiction rows` (scripts/select_qa_mode_without_oracle.py:2376)
- `hypothetical failed-viability question needs threshold/action policy surface rather than note surface` (scripts/select_qa_mode_without_oracle.py:2611)

## Promotion Discipline

- Add a guard freely when it protects a measured row-level failure.
- Do not call a guard a new lens until it transfers or clearly belongs to a family.
- If a family grows past a readable size, split by semantic reason, not by fixture.
- Do not hide guard growth inside parameter bags. A family generator must report its enumerated surfaces, transfer evidence, and retirement candidates.
- Prefer retiring guards when compile/query/helper improvements make the originating failure pass without selector intervention.
- If a guard remains unclassified, either retire it, rename it, or add a family with a purpose.
