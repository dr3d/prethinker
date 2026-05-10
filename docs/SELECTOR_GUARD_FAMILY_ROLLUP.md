# Selector Guard Family Rollup

This report keeps the selector guard surface from turning into a pile of
fixture-shaped knobs. Individual guards are allowed while they are being
measured, but they should collapse into a small number of semantic families
before they become daily-driver harness doctrine.

Generated from `scripts/select_qa_mode_without_oracle.py`.

Companion audit ledger: [SELECTOR_GUARD_LEDGER.md](https://github.com/dr3d/prethinker/blob/main/docs/SELECTOR_GUARD_LEDGER.md).

## Summary

- guard return sites: `244`
- unique guard reasons: `244`
- classified families: `7`
- unclassified reasons: `0`
- duplicate guard reasons: `0`

## Growth Health

- status: `warn`
- family budget: `7 / 8`
- largest family: `operational_record_status` with `55` guards (`0.225` share)
- unique reason ratio: `1.0`
- guards per family: `34.86`
- unique reasons per family: `34.86`

Raw guard instances may grow during fixture farming, but semantic compression depends on low family count, zero unclassified reasons, no single family becoming a dumping ground, and no parameterized family hiding a large private enumeration table.

Warnings:

- enumeration pressure is high; parameterizing families may hide guard sprawl unless instances retire or transfer

## Family Counts

| Family | Count | Purpose |
| --- | ---: | --- |
| `entity_role_authority` | 35 | Separate identity, role definition, acting authority, collector, contract authority, and guardianship rows from broad action or title-only evidence. |
| `operational_record_status` | 55 | Protect current status, request timing, commit readiness, decision, priority, concern, constitution, and resubmission rows from nearby but less answer-bearing record/event surfaces. |
| `rationale_evidence_contrast` | 42 | Route why/cause, witness/report, source-note, split rationale, viability contrast, and pending test questions to explicit rationale or evidentiary support instead of adjacent status rows. |
| `regulatory_access_scope` | 8 | Route all/any scope, termination denial, affected-lot exclusion, and reclassification-deadline questions to access surfaces that carry the right set, threshold, target, or temporal boundary. |
| `rule_activation_surface` | 30 | Route promoted rule, eligibility, recall, recusal, window, rejection, and reserve questions to the evidence surface that contains both the governing condition and the instance facts needed to apply it. |
| `state_custody_ownership` | 27 | Separate current object state, custody transfer, possession, ownership, legal title, and award/result surfaces from generic event, property, or person rows. |
| `threshold_policy_arithmetic` | 47 | Prefer direct threshold, quantity, storage, policy-action, and arithmetic inputs when a broader policy or derived-status surface is tempting but incomplete. |

## Guard Reasons

### `entity_role_authority`

- `identity question has baseline name/role support and candidate is broad action-heavy` (scripts/select_qa_mode_without_oracle.py:810)
- `badge-id question with unresolved holder needs identity-status badge surface rather than nearest source-record usage` (scripts/select_qa_mode_without_oracle.py:961)
- `same-item question needs current item identity/description surface rather than withdrawn-label evidence alone` (scripts/select_qa_mode_without_oracle.py:990)
- `publication-authority question needs publication holder plus active restriction surface rather than broad access-authority volume` (scripts/select_qa_mode_without_oracle.py:1032)
- `arbitrator-unresolved-question row needs dispute-scope/topic surface rather than broad dispute-status volume` (scripts/select_qa_mode_without_oracle.py:1065)
- `authoritative-homeroom question needs current roster membership surface rather than correction-action text alone` (scripts/select_qa_mode_without_oracle.py:1264)
- `applicant identity question needs source-author/actor surface rather than generic event role rows` (scripts/select_qa_mode_without_oracle.py:1399)
- `school-principal identity question needs source-record authority surface rather than roster row volume` (scripts/select_qa_mode_without_oracle.py:1408)
- `adult-roster count question needs count-value surface rather than broad role membership rows` (scripts/select_qa_mode_without_oracle.py:1417)
- `panel-chair identity question needs panel list-member surface rather than generic person-role rows` (scripts/select_qa_mode_without_oracle.py:1435)
- `authority/source identity question needs the surface carrying the named note actor` (scripts/select_qa_mode_without_oracle.py:1444)
- `authority/source identity question needs the surface carrying the named judicial actor` (scripts/select_qa_mode_without_oracle.py:1453)
- `authority/source identity question needs issue-status authority surface rather than ownership claim rows` (scripts/select_qa_mode_without_oracle.py:1462)
- `project-PI identity question needs direct role/assignment surface rather than archival row volume` (scripts/select_qa_mode_without_oracle.py:1634)
- `combined role-identity question needs source/participant surface rather than single-role evidence` (scripts/select_qa_mode_without_oracle.py:1643)
- `school role/driver identity question needs direct role predicate rather than row-value volume` (scripts/select_qa_mode_without_oracle.py:1653)
- `parent-sample identifier question needs source or row sample-ID surface rather than ambiguous sample-id hierarchy` (scripts/select_qa_mode_without_oracle.py:1662)
- `student-location supervision question needs statement plus event-attribute surface rather than role roster volume` (scripts/select_qa_mode_without_oracle.py:1743)
- `credential question needs explicit credential-status surface rather than access-log volume` (scripts/select_qa_mode_without_oracle.py:1885)
- `collector identity question needs direct collector predicate surface rather than broad status/note evidence` (scripts/select_qa_mode_without_oracle.py:1972)
- `station-supervisor question needs explicit station_supervisor surface rather than standing group-supervision rows` (scripts/select_qa_mode_without_oracle.py:2118)
- `festival-director identity question needs direct person-role surface rather than meeting/ruling volume` (scripts/select_qa_mode_without_oracle.py:2156)
- `superlative identity question needs explicit age/identity surface rather than broad role membership rows` (scripts/select_qa_mode_without_oracle.py:2167)
- `official identity question needs role-authority definition surface rather than action volume or title-only rows` (scripts/select_qa_mode_without_oracle.py:2180)
- `reinstatement question needs focused role-history surface rather than broad current-role or rule evidence` (scripts/select_qa_mode_without_oracle.py:2218)
- `contract-validity question needs explicit acting-authority surface rather than generic rule evidence` (scripts/select_qa_mode_without_oracle.py:2257)
- `contract-validity question needs authority-source surface rather than unrelated ownership or entity rows` (scripts/select_qa_mode_without_oracle.py:2264)
- `guardianship-validity question needs residence/resumption condition surface rather than bare guardianship status` (scripts/select_qa_mode_without_oracle.py:2415)
- `destruction-supervisor question needs person role plus destruction event surface` (scripts/select_qa_mode_without_oracle.py:2643)
- `recovery-identity question needs direct testimony/recovery surface rather than custody or zone rows` (scripts/select_qa_mode_without_oracle.py:2696)
- `substitute-scorer identity question needs compact service-role surface rather than certification/result volume` (scripts/select_qa_mode_without_oracle.py:2763)
- `same-name distinction question needs alias plus group-membership surface rather than identity table alone` (scripts/select_qa_mode_without_oracle.py:2873)
- `surveyor-certification lapse question needs direct certification-status surface rather than survey-result role rows` (scripts/select_qa_mode_without_oracle.py:2900)
- `intake-actor question needs explicit item-received-from provenance surface` (scripts/select_qa_mode_without_oracle.py:3034)
- `intake-actor question needs handoff/location event surface rather than ledger-entry rows alone` (scripts/select_qa_mode_without_oracle.py:3043)

### `operational_record_status`

- `status question has direct baseline status/rule support` (scripts/select_qa_mode_without_oracle.py:828)
- `status question has direct baseline application/status support and candidate is broad or relaxed-heavy` (scripts/select_qa_mode_without_oracle.py:842)
- `counterfactual or hold/readiness question has direct baseline rule/status support and candidate is broad or relaxed-heavy` (scripts/select_qa_mode_without_oracle.py:862)
- `response-content question needs compact filed-response surface rather than broad procedural expansion` (scripts/select_qa_mode_without_oracle.py:874)
- `contract-rescission status question needs request/outcome surface rather than approval vote surface alone` (scripts/select_qa_mode_without_oracle.py:888)
- `raw-timestamp question needs explicit raw_timestamp surface rather than corrected/event-correlation volume` (scripts/select_qa_mode_without_oracle.py:918)
- `snapshot-state question needs sampler state-plus-cause surface when the snapshot row asks why that state held` (scripts/select_qa_mode_without_oracle.py:927)
- `snapshot-state question needs sampler status surface rather than broad event-description volume` (scripts/select_qa_mode_without_oracle.py:934)
- `snapshot-state question needs explicit sampler_state surface rather than broad event-description or status volume` (scripts/select_qa_mode_without_oracle.py:941)
- `clear-sample clock snapshot question needs segment-plus-elapsed-time helper surface rather than snapshot text alone` (scripts/select_qa_mode_without_oracle.py:950)
- `corrected-timestamp question needs explicit corrected-timestamp surface rather than rule-description context` (scripts/select_qa_mode_without_oracle.py:970)
- `corrected-duration question needs paired raw/corrected badge-event surface rather than corrected timestamp volume alone` (scripts/select_qa_mode_without_oracle.py:979)
- `expected-order question needs explicit expected-order surface rather than open-exception volume` (scripts/select_qa_mode_without_oracle.py:1121)
- `communications-officer drafting question needs notice-issued plus person-role surface rather than name lookup alone` (scripts/select_qa_mode_without_oracle.py:1175)
- `sampler-offline interval count needs explicit interval surface rather than state-start/end fragments` (scripts/select_qa_mode_without_oracle.py:1184)
- `sampler-offline interval count needs sampler-state transition surface rather than event-log volume` (scripts/select_qa_mode_without_oracle.py:1191)
- `packet-close audit-exception count needs semantic open-exception surface rather than expanded source-row evidence` (scripts/select_qa_mode_without_oracle.py:1220)
- `pending-rather-than-approved question needs determination reason and pending-verification surface over raw source rows` (scripts/select_qa_mode_without_oracle.py:1320)
- `trip-date question needs roster-state schedule surface rather than roster-version/source-record volume` (scripts/select_qa_mode_without_oracle.py:1347)
- `order-series identifier question needs exact document-identifier surface rather than section/event volume` (scripts/select_qa_mode_without_oracle.py:1381)
- `erratum report-of-record question needs archival document/version surface rather than generic document-status rows` (scripts/select_qa_mode_without_oracle.py:1671)
- `review-completion question needs explicit status-at surface rather than broad uncertainty labels` (scripts/select_qa_mode_without_oracle.py:1689)
- `date-event anchor enumeration needs incident-anchor surface rather than source-section volume` (scripts/select_qa_mode_without_oracle.py:1797)
- `governing-board vote-status question needs explicit pending-determination surface rather than unrelated negative records` (scripts/select_qa_mode_without_oracle.py:1806)
- `timekeeping clock-out question needs timekeeping or assignment interval surface rather than badge-exit event rows` (scripts/select_qa_mode_without_oracle.py:1858)
- `medication lot-number question needs source-record event attributes rather than self-check paraphrase or row-volume evidence` (scripts/select_qa_mode_without_oracle.py:1867)
- `unresolved policy-deviation question needs review/open-issue status surface rather than archival event volume` (scripts/select_qa_mode_without_oracle.py:1904)
- `court-determination question needs packet/source status surface rather than broad unresolved labels` (scripts/select_qa_mode_without_oracle.py:1924)
- `resolved-status question needs direct unresolved/disputed-status surface rather than archival evidence volume` (scripts/select_qa_mode_without_oracle.py:1954)
- `planning-application request question needs application-summary plus unit-mix surface rather than claim/status volume` (scripts/select_qa_mode_without_oracle.py:1981)
- `prior-proposal disposition question needs proposal-version/procedural-status surface rather than current-application volume` (scripts/select_qa_mode_without_oracle.py:2001)
- `contract-rescission status question keeps request/outcome surface over approval vote surface alone` (scripts/select_qa_mode_without_oracle.py:2030)
- `appeal-status question needs appeal event plus no-decision/deadline surface rather than bare docket status` (scripts/select_qa_mode_without_oracle.py:2087)
- `temporary-availability question needs attendance plus authority-transfer surface` (scripts/select_qa_mode_without_oracle.py:2098)
- `station-arrival-time question needs event/timestamp surface rather than roster identity rows` (scripts/select_qa_mode_without_oracle.py:2127)
- `temporary-role question needs roster-state role-hint support rather than bare group membership` (scripts/select_qa_mode_without_oracle.py:2136)
- `completion-report incident list needs trip-outcome plus issue/medical/hazard surfaces` (scripts/select_qa_mode_without_oracle.py:2147)
- `current operational status question needs explicit final-state surface rather than adjacent event/action evidence` (scripts/select_qa_mode_without_oracle.py:2424)
- `public-use extension question needs extension purpose/status surface rather than broad permit lifecycle volume` (scripts/select_qa_mode_without_oracle.py:2433)
- `unrestricted-active count question needs baseline status, restriction, suspension, and violation surfaces` (scripts/select_qa_mode_without_oracle.py:2569)
- `student-count question needs scoped final-attendance surface rather than broad roster volume` (scripts/select_qa_mode_without_oracle.py:2788)
- `group-designation suspension question needs event plus interval-membership surface rather than broad fallback rows` (scripts/select_qa_mode_without_oracle.py:2799)
- `temporary-supervisor absence question needs location-change plus supervision/medical-event surface` (scripts/select_qa_mode_without_oracle.py:2808)
- `post-reassignment group-count question needs stable membership/count surface over role-task volume` (scripts/select_qa_mode_without_oracle.py:2822)
- `temporary-team roster question needs scoped group-formation surface rather than standing roster volume` (scripts/select_qa_mode_without_oracle.py:2842)
- `no-touch hazard question needs incident/hazard observation surface rather than broad attendance roster` (scripts/select_qa_mode_without_oracle.py:2864)
- `adjusted-expiration question needs explicit current-expiration surface rather than extension-label or original-date evidence` (scripts/select_qa_mode_without_oracle.py:3062)
- `request filing timeliness question needs request/reinstatement threshold evidence rather than completion-window evidence` (scripts/select_qa_mode_without_oracle.py:3103)
- `commit-readiness question needs unresolved process evidence rather than a bare status value` (scripts/select_qa_mode_without_oracle.py:3117)
- `priority question needs explicit priority predicate surface rather than an underlying condition predicate` (scripts/select_qa_mode_without_oracle.py:3151)
- `decision-status question needs explicit decision surface rather than adjacent application/status evidence` (scripts/select_qa_mode_without_oracle.py:3164)
- `board-concern decision question needs event/action concern history rather than bare pending status` (scripts/select_qa_mode_without_oracle.py:3173)
- `deaccession-yet question needs explicit scheduled/not-formally-completed status surface rather than broad lot-history volume` (scripts/select_qa_mode_without_oracle.py:3199)
- `current-constitution eligibility question needs applicant-type plus controlling interpretation surface` (scripts/select_qa_mode_without_oracle.py:3262)
- `resubmission eligibility question needs proof/rule resolution surface rather than current applicant status surface` (scripts/select_qa_mode_without_oracle.py:3283)

### `rationale_evidence_contrast`

- `memo-establish question needs memo-content plus reliability-scope surface rather than broad investigative context` (scripts/select_qa_mode_without_oracle.py:1132)
- `phone-ping granularity question needs device-ping granularity surface rather than evidence-source summary` (scripts/select_qa_mode_without_oracle.py:1141)
- `evidence-source count question needs source-id catalog surface rather than generic evidence-source rows` (scripts/select_qa_mode_without_oracle.py:1150)
- `evidence-source count question needs source-id catalog surface rather than unresolved-fact volume` (scripts/select_qa_mode_without_oracle.py:1157)
- `negative-reliability question needs source-reliability scope rather than unresolved-activity status alone` (scripts/select_qa_mode_without_oracle.py:1166)
- `memo-resolution question needs claim plus unresolved-issue surface rather than permit/status fragments` (scripts/select_qa_mode_without_oracle.py:1616)
- `interval behavior-plus-cause question needs system-log event attributes rather than row-value volume` (scripts/select_qa_mode_without_oracle.py:1680)
- `position-source question needs statement/source-author surface rather than generic row-source labels` (scripts/select_qa_mode_without_oracle.py:1822)
- `timestamped message-source question needs direct log-entry surface rather than row-source fallback` (scripts/select_qa_mode_without_oracle.py:1831)
- `printed source-provenance question needs archival row/source labels rather than generic packet identifiers` (scripts/select_qa_mode_without_oracle.py:1847)
- `reply-memo theory question needs archival memo row value rather than generic source-document presence` (scripts/select_qa_mode_without_oracle.py:1933)
- `false-conflict consistency question needs paired intake/photo interpretation surface rather than row ledger fragments` (scripts/select_qa_mode_without_oracle.py:1963)
- `failed-vendor rationale question needs itemized vendor-deficiency surface` (scripts/select_qa_mode_without_oracle.py:2510)
- `failed-vendor rationale question needs inspection, vendor-status, and violation-detail surfaces together` (scripts/select_qa_mode_without_oracle.py:2517)
- `display-outcome question needs inspection/outcome plus permit-status surface` (scripts/select_qa_mode_without_oracle.py:2546)
- `display-outcome question needs date-specific permit validity plus incident/inspection surface` (scripts/select_qa_mode_without_oracle.py:2553)
- `second-violation duration question needs violation-record plus suspension-period surfaces together` (scripts/select_qa_mode_without_oracle.py:2562)
- `status-elevation rationale question needs lab/location/status context rather than bare status-change reason` (scripts/select_qa_mode_without_oracle.py:2634)
- `source-belief question needs claimant testimony surface rather than identification-status summary` (scripts/select_qa_mode_without_oracle.py:2709)
- `alternative-inscription question needs candidate-origin plus inscription/attribute surface` (scripts/select_qa_mode_without_oracle.py:2720)
- `missing-evidence question needs claimant testimony plus explicit absence/claim surfaces` (scripts/select_qa_mode_without_oracle.py:2747)
- `banner-change rationale question needs banner succession/creation surface rather than protest or score rows` (scripts/select_qa_mode_without_oracle.py:2756)
- `hold-call rationale question needs event-condition timing surface rather than broad witness/incident volume` (scripts/select_qa_mode_without_oracle.py:2770)
- `yellow-to-blue reassignment question keeps baseline transition surface over partial interval membership rows` (scripts/select_qa_mode_without_oracle.py:2815)
- `source-specific witness question needs Brigid report/claim surface rather than unresolved-discrepancy summary` (scripts/select_qa_mode_without_oracle.py:2833)
- `day-3 found-object question needs focused event/found-object surface rather than broad hazard summary` (scripts/select_qa_mode_without_oracle.py:2853)
- `conservator-date question needs source-recorded value surface rather than generic discrepancy rows` (scripts/select_qa_mode_without_oracle.py:2882)
- `display-authority question needs controlling governance/source-authority surface rather than display text rows` (scripts/select_qa_mode_without_oracle.py:2891)
- `source-claim question needs witness-statement surface rather than finding/provenance summary rows` (scripts/select_qa_mode_without_oracle.py:2918)
- `permission-request question needs direct witness-statement surface rather than evidence-date volume` (scripts/select_qa_mode_without_oracle.py:2927)
- `survey-commission question needs explicit report-commission provenance surface` (scripts/select_qa_mode_without_oracle.py:2936)
- `maintenance-evidence question needs receipt/evidence-source surface rather than witness/hearsay rows` (scripts/select_qa_mode_without_oracle.py:2952)
- `fictional-order question needs plot-outcome surface rather than plot-event summary rows` (scripts/select_qa_mode_without_oracle.py:2964)
- `boundary-discrepancy cause question needs measurement/marker-shift surface rather than survey-summary rows` (scripts/select_qa_mode_without_oracle.py:2978)
- `discrepancy-explanation question needs factual-discrepancy/incident-outcome surface rather than fictional event rows` (scripts/select_qa_mode_without_oracle.py:3016)
- `correction-authorship question needs handwriting/expert-attribution surface rather than correction-status volume` (scripts/select_qa_mode_without_oracle.py:3052)
- `evidentiary-status report question needs explicit witness/report surface rather than generic claim-status surface` (scripts/select_qa_mode_without_oracle.py:3084)
- `cause question has explicit baseline rationale-note support and candidate is broad record/event surface` (scripts/select_qa_mode_without_oracle.py:3138)
- `not-yet-tested question needs explicit pending test-status surface rather than broad negation over all lots` (scripts/select_qa_mode_without_oracle.py:3182)
- `split rationale question needs explicit source-note rationale plus viability context` (scripts/select_qa_mode_without_oracle.py:3210)
- `split rationale question needs actual split/lot-condition surface rather than generic vault assignment surface` (scripts/select_qa_mode_without_oracle.py:3224)
- `viability-concern question needs explicit source-note contrast plus viability context` (scripts/select_qa_mode_without_oracle.py:3235)

### `regulatory_access_scope`

- `personal-letter reading-access question needs semantic access authority plus publication-restriction boundary, not raw source rows alone` (scripts/select_qa_mode_without_oracle.py:1045)
- `universal-scope question needs broad set-enumeration surface rather than narrower report-detail joins` (scripts/select_qa_mode_without_oracle.py:2274)
- `termination-denial question needs rationale plus quantity-threshold support rather than status text alone` (scripts/select_qa_mode_without_oracle.py:2283)
- `lot-affected question needs explicit target-lot exclusion/check surface rather than broad affected-lot listing` (scripts/select_qa_mode_without_oracle.py:2292)
- `counterfactual reclassification deadline question needs classification-bound deadline surface` (scripts/select_qa_mode_without_oracle.py:2303)
- `placed-under-quarantine count needs mistaken-movement surface rather than broad quarantine-scope volume` (scripts/select_qa_mode_without_oracle.py:2588)
- `split-lot never-quarantined count needs quarantine-scope surface rather than broad lot status history` (scripts/select_qa_mode_without_oracle.py:2600)
- `initial-affected greenhouse question needs greenhouse-status plus exclusion/location surface` (scripts/select_qa_mode_without_oracle.py:2616)

### `rule_activation_surface`

- `rescission-request eligibility question needs request/validity surface rather than generic vote-rule volume` (scripts/select_qa_mode_without_oracle.py:880)
- `rule-effect question needs supersession plus status/event surface rather than adjacent rule text` (scripts/select_qa_mode_without_oracle.py:1471)
- `rule-effect question needs direct bylaw-rule surface rather than partial requirement rows` (scripts/select_qa_mode_without_oracle.py:1480)
- `rule-effect question needs archival rule text rather than partial requirement rows` (scripts/select_qa_mode_without_oracle.py:1487)
- `rule-effect question needs explicit transfer requirement surface rather than ownership/status rows` (scripts/select_qa_mode_without_oracle.py:1496)
- `rule-effect question needs archival memo row value rather than ownership/status rows` (scripts/select_qa_mode_without_oracle.py:1503)
- `override-rule requirement question needs explicit source-record rule requirement surface rather than archival row values` (scripts/select_qa_mode_without_oracle.py:1876)
- `revised-plan monitoring question needs plan/rejection rule surface rather than observation-status rows` (scripts/select_qa_mode_without_oracle.py:2065)
- `appeal-tolling question needs rule text plus appeal/deadline surface rather than isolated tolling labels` (scripts/select_qa_mode_without_oracle.py:2076)
- `deferment-rationale question needs interpreted decision support rather than rule text alone` (scripts/select_qa_mode_without_oracle.py:2312)
- `component-problem question needs project-category plus rule-condition surface` (scripts/select_qa_mode_without_oracle.py:2321)
- `counterfactual-recusal outcome question needs both procedure path and eligibility surface` (scripts/select_qa_mode_without_oracle.py:2336)
- `recusal-rationale question needs recusal rule surface rather than eligibility determination surface` (scripts/select_qa_mode_without_oracle.py:2345)
- `post-recusal vote question needs recusal/vote/rule surface without misleading quorum-status volume` (scripts/select_qa_mode_without_oracle.py:2354)
- `window-merit question needs explicit rule-condition plus prior-history surface` (scripts/select_qa_mode_without_oracle.py:2363)
- `window-merit question needs prior-history plus interpretation surface` (scripts/select_qa_mode_without_oracle.py:2372)
- `amendment-recall question needs recall-authority surface rather than threshold-only legal-opinion rows` (scripts/select_qa_mode_without_oracle.py:2383)
- `rejection-cause question needs correction/clarification surface rather than derived status alone` (scripts/select_qa_mode_without_oracle.py:2392)
- `hypothetical reserve-status question keeps baseline arithmetic inputs over derived rule status` (scripts/select_qa_mode_without_oracle.py:2399)
- `hypothetical reserve-status question needs baseline arithmetic inputs rather than derived rule status` (scripts/select_qa_mode_without_oracle.py:2406)
- `valid-period extension question needs original validity plus extension-validity surface` (scripts/select_qa_mode_without_oracle.py:2442)
- `unrenewed-expiry question needs validity plus deadline/requirement surface` (scripts/select_qa_mode_without_oracle.py:2451)
- `unrenewed-expiry question needs original validity endpoint surface rather than renewed lifecycle rows` (scripts/select_qa_mode_without_oracle.py:2458)
- `appeal-hearing question needs filed-appeal/hearing-scheduled surface rather than broad status rows` (scripts/select_qa_mode_without_oracle.py:2467)
- `suspension-trigger question needs explicit violation-record plus permit-suspension surface` (scripts/select_qa_mode_without_oracle.py:2476)
- `suspension-trigger question needs violation event plus suspension surface, not suspension interval volume alone` (scripts/select_qa_mode_without_oracle.py:2485)
- `failed-reinspection count question needs compact aggregate inspection-result surface rather than lifecycle status volume` (scripts/select_qa_mode_without_oracle.py:2501)
- `permitted-hours question needs explicit operational-hours rule surface` (scripts/select_qa_mode_without_oracle.py:2526)
- `approved-display count question needs approval/validity surface rather than broad current-status rows` (scripts/select_qa_mode_without_oracle.py:2537)
- `permit-action list question needs suspension, restriction, status, and deadline surfaces together` (scripts/select_qa_mode_without_oracle.py:2578)

### `state_custody_ownership`

- `award/result question has baseline awarded support and candidate lacks awarded rows` (scripts/select_qa_mode_without_oracle.py:819)
- `near-duplicate bin-code question needs collision-risk plus bin-location surface rather than generic current-label rows` (scripts/select_qa_mode_without_oracle.py:999)
- `physical-custody item-count question needs grouped custody count helper rather than raw custodian row count` (scripts/select_qa_mode_without_oracle.py:1019)
- `governing-2024-custody-document question needs exact amendment source-row text with custody/notice clauses` (scripts/select_qa_mode_without_oracle.py:1056)
- `location-plus-publication-pause question needs custody plus publication restriction surface` (scripts/select_qa_mode_without_oracle.py:1076)
- `MOU-scope expansion question needs agreement-clause plus access/addition surface rather than static right-scope volume` (scripts/select_qa_mode_without_oracle.py:1085)
- `photograph-album interval question needs exact access-log custody surface rather than broad access-event volume` (scripts/select_qa_mode_without_oracle.py:1094)
- `photograph-album interval question needs access/recall custody surface rather than broad conservation-scope volume` (scripts/select_qa_mode_without_oracle.py:1103)
- `custody-release question needs custody/status surface rather than scan-record volume` (scripts/select_qa_mode_without_oracle.py:1112)
- `barcode-supersession question needs scan/correction surface rather than broad current-barcode volume` (scripts/select_qa_mode_without_oracle.py:1372)
- `tree-amendment measurement question needs archival row-value surface preserving species/DBH/source basis` (scripts/select_qa_mode_without_oracle.py:1571)
- `dated physical-location question needs archival row location plus row-time support rather than synthesized cold self-check` (scripts/select_qa_mode_without_oracle.py:1913)
- `current object-component question needs direct current-state/component surface rather than transition history volume` (scripts/select_qa_mode_without_oracle.py:2189)
- `why-have question needs custody-transfer surface rather than adjacent action or object-property rows` (scripts/select_qa_mode_without_oracle.py:2198)
- `award placement question needs explicit award-result surface rather than nearby device/person rows` (scripts/select_qa_mode_without_oracle.py:2207)
- `carry question needs direct possession surface rather than broad title or event evidence` (scripts/select_qa_mode_without_oracle.py:2228)
- `possession-versus-ownership question needs inherit/own/possess distinction surface rather than broad event/rule evidence` (scripts/select_qa_mode_without_oracle.py:2239)
- `legal-title contest question needs claim/default/transfer surface rather than static ownership rows` (scripts/select_qa_mode_without_oracle.py:2248)
- `provisional-control question needs holder plus pending estate/claim context rather than bare holder row` (scripts/select_qa_mode_without_oracle.py:2654)
- `post-death legal-ownership question needs court/inheritance status surface rather than stale legal-owner interval` (scripts/select_qa_mode_without_oracle.py:2665)
- `current possession/maintenance question needs physical-possessor plus gift/dispute surface` (scripts/select_qa_mode_without_oracle.py:2676)
- `solicitor-advice question needs advice plus adverse-possession caveat surface` (scripts/select_qa_mode_without_oracle.py:2687)
- `insurance-link question needs direct insured-by surface rather than contingent ownership claim rows` (scripts/select_qa_mode_without_oracle.py:2738)
- `disputed-strip feature question needs object-location surface rather than broad finding/survey rows` (scripts/select_qa_mode_without_oracle.py:2909)
- `physical inventory count question needs incident/count outcome surface rather than title-name rows` (scripts/select_qa_mode_without_oracle.py:3004)
- `client-ledger pickup question needs asset-state/location surface rather than broad item provenance rows` (scripts/select_qa_mode_without_oracle.py:3025)
- `correction-entitlement question needs entitlement rule plus extension effect surface rather than correction/admission rows alone` (scripts/select_qa_mode_without_oracle.py:3075)

### `threshold_policy_arithmetic`

- `density-calculation question needs numeric staff-evaluation surface rather than qualitative source-opinion surface` (scripts/select_qa_mode_without_oracle.py:867)
- `active-held count question needs current-label/status plus withdrawn-label filter surface` (scripts/select_qa_mode_without_oracle.py:1010)
- `packet-close open-item count needs explicit open-item surface rather than deadline/notice volume` (scripts/select_qa_mode_without_oracle.py:1209)
- `application-disposition question needs status/determination surface rather than source-record-facts gap` (scripts/select_qa_mode_without_oracle.py:1229)
- `roster-entry count question needs entry-preserving roster surface rather than distinct-student membership volume` (scripts/select_qa_mode_without_oracle.py:1242)
- `distinct-student count-change question needs roster-version count summary rather than itemized membership volume` (scripts/select_qa_mode_without_oracle.py:1253)
- `correction-notice replacement question needs change-type surface rather than unparsed correction-action text` (scripts/select_qa_mode_without_oracle.py:1273)
- `application-count question needs canonical application-status surface rather than source-record duplicate rows` (scripts/select_qa_mode_without_oracle.py:1287)
- `cap-application question needs rule/determination surface over expanded source-record rows` (scripts/select_qa_mode_without_oracle.py:1298)
- `counterfactual no-cap amount question needs arithmetic/grant amount surface rather than broad memory-ledger context` (scripts/select_qa_mode_without_oracle.py:1309)
- `date-alone rule question needs threshold plus exception surface rather than broad applicant-date volume` (scripts/select_qa_mode_without_oracle.py:1329)
- `projection-supersession question needs trigger/actual event surface rather than projection-comparison volume` (scripts/select_qa_mode_without_oracle.py:1338)
- `threshold question needs rule-threshold surface rather than applicant-attribute volume` (scripts/select_qa_mode_without_oracle.py:1356)
- `threshold question needs rule threshold/condition surface rather than applicant-attribute volume` (scripts/select_qa_mode_without_oracle.py:1363)
- `application-number identifier question needs exact document-identifier surface rather than score/event volume` (scripts/select_qa_mode_without_oracle.py:1390)
- `headcount-scan reconciliation question needs paired count/scan evidence rather than generic source-record claims` (scripts/select_qa_mode_without_oracle.py:1426)
- `focused semantic surface beats archival row-volume for status/score/authority questions` (scripts/select_qa_mode_without_oracle.py:1562)
- `operative-permit question needs permit issuance/amendment surface rather than source-document status alone` (scripts/select_qa_mode_without_oracle.py:1580)
- `tree-list/count question needs amendment count/list surface rather than stale protection-status rows` (scripts/select_qa_mode_without_oracle.py:1589)
- `remedy-imposition question needs unresolved-issue surface rather than remedy-label presence` (scripts/select_qa_mode_without_oracle.py:1598)
- `hearing-held question needs event/open-issue surface rather than scheduled-date presence` (scripts/select_qa_mode_without_oracle.py:1607)
- `packet-time measurement question needs direct measurement-value surface rather than row-value volume` (scripts/select_qa_mode_without_oracle.py:1625)
- `active-lot count question needs archival inventory row enumeration rather than contaminant/status volume` (scripts/select_qa_mode_without_oracle.py:1698)
- `document-identification question needs document-exhibit surface rather than event/source-type rows` (scripts/select_qa_mode_without_oracle.py:1707)
- `exhibit-identification question needs exhibit/source-document surface rather than witness/person rows` (scripts/select_qa_mode_without_oracle.py:1716)
- `roster-of-record membership question needs assigned/person roster surface rather than supersession metadata` (scripts/select_qa_mode_without_oracle.py:1725)
- `withdrawn-draft governance question needs source-status/supersession surface rather than document-id presence` (scripts/select_qa_mode_without_oracle.py:1734)
- `headcount elapsed-time question needs elapsed-minutes surface rather than headcount rows alone` (scripts/select_qa_mode_without_oracle.py:1752)
- `parent-letter determination question needs review-scheduled/letter surface rather than source-document volume` (scripts/select_qa_mode_without_oracle.py:1761)
- `witness-scan reconciliation question needs direct scan/location surface rather than broad source-record claims` (scripts/select_qa_mode_without_oracle.py:1770)
- `newsletter-versus-roster authority question needs supersession/roster evidence rather than stale assignment rows` (scripts/select_qa_mode_without_oracle.py:1779)
- `current-versus-withdrawn claim question needs statement-claim plus supersession/status surface` (scripts/select_qa_mode_without_oracle.py:1788)
- `scoped roster-count question needs source-record roster section surface rather than badge/log volume` (scripts/select_qa_mode_without_oracle.py:1894)
- `deed item-count question needs conveyed-item surface rather than broad receipt row volume` (scripts/select_qa_mode_without_oracle.py:1942)
- `zoning-designation question needs parcel-zoning surface rather than general zoning-definition volume` (scripts/select_qa_mode_without_oracle.py:1990)
- `build-out timeline question needs site-measure plus draft-condition surface rather than permit-expiry status alone` (scripts/select_qa_mode_without_oracle.py:2010)
- `dimensional-standards question needs staff-finding plus site-measure surface rather than consolidated compliance status alone` (scripts/select_qa_mode_without_oracle.py:2021)
- `deadline-filing timeliness question needs filed-event plus calculated-deadline surface` (scripts/select_qa_mode_without_oracle.py:2043)
- `board-review-period question needs calculated-deadline surface rather than loose deadline values` (scripts/select_qa_mode_without_oracle.py:2054)
- `attendance-count question needs explicit session_attendance_count surface rather than interval roster volume` (scripts/select_qa_mode_without_oracle.py:2109)
- `lot plant-count question needs direct lot/count surface rather than status or destruction history` (scripts/select_qa_mode_without_oracle.py:2607)
- `lot-3b lab-result question needs lab-result plus lot-status context, not generic lab-result volume` (scripts/select_qa_mode_without_oracle.py:2625)
- `candidate-vessel list question needs candidate-origin plus vessel-loss detail surface` (scripts/select_qa_mode_without_oracle.py:2729)
- `corrected-rank-order question needs qualifying-rank plus score-correction surface rather than raw total volume` (scripts/select_qa_mode_without_oracle.py:2779)
- `claim-value question needs financial-value/incident-outcome surface rather than claim/status fiction rows` (scripts/select_qa_mode_without_oracle.py:2993)
- `hypothetical failed-viability question keeps direct baseline threshold/storage support over broader policy-note surfaces` (scripts/select_qa_mode_without_oracle.py:3242)
- `hypothetical failed-viability question needs threshold/action policy surface rather than note surface` (scripts/select_qa_mode_without_oracle.py:3251)

## Promotion Discipline

- Add a guard freely when it protects a measured row-level failure.
- Do not call a guard a new lens until it transfers or clearly belongs to a family.
- If a family grows past a readable size, split by semantic reason, not by fixture.
- Do not hide guard growth inside parameter bags. A family generator must report its enumerated surfaces, transfer evidence, and retirement candidates.
- Prefer retiring guards when compile/query/helper improvements make the originating failure pass without selector intervention.
- If a guard remains unclassified, either retire it, rename it, or add a family with a purpose.
