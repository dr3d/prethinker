# Selector Guard Family Rollup

This report keeps the selector guard surface from turning into a pile of
fixture-shaped knobs. Individual guards are allowed while they are being
measured, but they should collapse into a small number of semantic families
before they become daily-driver harness doctrine.

Generated from `scripts/select_qa_mode_without_oracle.py`.

Companion audit ledger: [SELECTOR_GUARD_LEDGER.md](https://github.com/dr3d/prethinker/blob/main/docs/SELECTOR_GUARD_LEDGER.md).

## Summary

- guard return sites: `257`
- unique guard reasons: `257`
- classified families: `7`
- unclassified reasons: `0`
- duplicate guard reasons: `0`

## Growth Health

- status: `warn`
- family budget: `7 / 8`
- largest family: `operational_record_status` with `57` guards (`0.222` share)
- unique reason ratio: `1.0`
- guards per family: `36.71`
- unique reasons per family: `36.71`

Raw guard instances may grow during fixture farming, but semantic compression depends on low family count, zero unclassified reasons, no single family becoming a dumping ground, and no parameterized family hiding a large private enumeration table.

Warnings:

- enumeration pressure is high; parameterizing families may hide guard sprawl unless instances retire or transfer

## Family Counts

| Family | Count | Purpose |
| --- | ---: | --- |
| `entity_role_authority` | 42 | Separate identity, role definition, acting authority, collector, contract authority, and guardianship rows from broad action or title-only evidence. |
| `operational_record_status` | 57 | Protect current status, request timing, commit readiness, decision, priority, concern, constitution, and resubmission rows from nearby but less answer-bearing record/event surfaces. |
| `rationale_evidence_contrast` | 42 | Route why/cause, witness/report, source-note, split rationale, viability contrast, and pending test questions to explicit rationale or evidentiary support instead of adjacent status rows. |
| `regulatory_access_scope` | 8 | Route all/any scope, termination denial, affected-lot exclusion, and reclassification-deadline questions to access surfaces that carry the right set, threshold, target, or temporal boundary. |
| `rule_activation_surface` | 30 | Route promoted rule, eligibility, recall, recusal, window, rejection, and reserve questions to the evidence surface that contains both the governing condition and the instance facts needed to apply it. |
| `state_custody_ownership` | 27 | Separate current object state, custody transfer, possession, ownership, legal title, and award/result surfaces from generic event, property, or person rows. |
| `threshold_policy_arithmetic` | 51 | Prefer direct threshold, quantity, storage, policy-action, and arithmetic inputs when a broader policy or derived-status surface is tempting but incomplete. |

## Guard Reasons

### `entity_role_authority`

- `identity question has baseline name/role support and candidate is broad action-heavy` (scripts/select_qa_mode_without_oracle.py:865)
- `badge-id question with unresolved holder needs identity-status badge surface rather than nearest source-record usage` (scripts/select_qa_mode_without_oracle.py:1016)
- `same-item question needs current item identity/description surface rather than withdrawn-label evidence alone` (scripts/select_qa_mode_without_oracle.py:1045)
- `publication-authority question needs publication holder plus active restriction surface rather than broad access-authority volume` (scripts/select_qa_mode_without_oracle.py:1087)
- `arbitrator-unresolved-question row needs dispute-scope/topic surface rather than broad dispute-status volume` (scripts/select_qa_mode_without_oracle.py:1120)
- `student-identifier question needs label-to-canonical-member surface rather than printed-label surface alone` (scripts/select_qa_mode_without_oracle.py:1317)
- `authoritative-homeroom question needs current member alias/table surface before correction-history rows` (scripts/select_qa_mode_without_oracle.py:1342)
- `authoritative-homeroom question needs focused current roster helper rows` (scripts/select_qa_mode_without_oracle.py:1352)
- `authoritative-homeroom question needs current roster membership surface rather than correction-action text alone` (scripts/select_qa_mode_without_oracle.py:1357)
- `bus-assignment correction question needs bus-assignment plus change-type surface rather than roster table identity rows` (scripts/select_qa_mode_without_oracle.py:1366)
- `adult-total roster question needs adult role surface rather than qualifying-chaperone count alone` (scripts/select_qa_mode_without_oracle.py:1400)
- `ratio-exclusion identity question needs role-exclusion policy surface rather than adult-role count volume` (scripts/select_qa_mode_without_oracle.py:1416)
- `ratio-exclusion identity question needs role plus policy surface rather than adult-role count volume` (scripts/select_qa_mode_without_oracle.py:1423)
- `applicant identity question needs source-author/actor surface rather than generic event role rows` (scripts/select_qa_mode_without_oracle.py:1568)
- `school-principal identity question needs source-record authority surface rather than roster row volume` (scripts/select_qa_mode_without_oracle.py:1577)
- `adult-roster count question needs count-value surface rather than broad role membership rows` (scripts/select_qa_mode_without_oracle.py:1586)
- `panel-chair identity question needs panel list-member surface rather than generic person-role rows` (scripts/select_qa_mode_without_oracle.py:1604)
- `authority/source identity question needs the surface carrying the named note actor` (scripts/select_qa_mode_without_oracle.py:1613)
- `authority/source identity question needs the surface carrying the named judicial actor` (scripts/select_qa_mode_without_oracle.py:1622)
- `authority/source identity question needs issue-status authority surface rather than ownership claim rows` (scripts/select_qa_mode_without_oracle.py:1631)
- `project-PI identity question needs direct role/assignment surface rather than archival row volume` (scripts/select_qa_mode_without_oracle.py:1803)
- `combined role-identity question needs source/participant surface rather than single-role evidence` (scripts/select_qa_mode_without_oracle.py:1812)
- `school role/driver identity question needs direct role predicate rather than row-value volume` (scripts/select_qa_mode_without_oracle.py:1822)
- `parent-sample identifier question needs source or row sample-ID surface rather than ambiguous sample-id hierarchy` (scripts/select_qa_mode_without_oracle.py:1831)
- `student-location supervision question needs statement plus event-attribute surface rather than role roster volume` (scripts/select_qa_mode_without_oracle.py:1912)
- `credential question needs explicit credential-status surface rather than access-log volume` (scripts/select_qa_mode_without_oracle.py:2054)
- `collector identity question needs direct collector predicate surface rather than broad status/note evidence` (scripts/select_qa_mode_without_oracle.py:2141)
- `station-supervisor question needs explicit station_supervisor surface rather than standing group-supervision rows` (scripts/select_qa_mode_without_oracle.py:2287)
- `festival-director identity question needs direct person-role surface rather than meeting/ruling volume` (scripts/select_qa_mode_without_oracle.py:2325)
- `superlative identity question needs explicit age/identity surface rather than broad role membership rows` (scripts/select_qa_mode_without_oracle.py:2336)
- `official identity question needs role-authority definition surface rather than action volume or title-only rows` (scripts/select_qa_mode_without_oracle.py:2349)
- `reinstatement question needs focused role-history surface rather than broad current-role or rule evidence` (scripts/select_qa_mode_without_oracle.py:2387)
- `contract-validity question needs explicit acting-authority surface rather than generic rule evidence` (scripts/select_qa_mode_without_oracle.py:2426)
- `contract-validity question needs authority-source surface rather than unrelated ownership or entity rows` (scripts/select_qa_mode_without_oracle.py:2433)
- `guardianship-validity question needs residence/resumption condition surface rather than bare guardianship status` (scripts/select_qa_mode_without_oracle.py:2584)
- `destruction-supervisor question needs person role plus destruction event surface` (scripts/select_qa_mode_without_oracle.py:2812)
- `recovery-identity question needs direct testimony/recovery surface rather than custody or zone rows` (scripts/select_qa_mode_without_oracle.py:2865)
- `substitute-scorer identity question needs compact service-role surface rather than certification/result volume` (scripts/select_qa_mode_without_oracle.py:2932)
- `same-name distinction question needs alias plus group-membership surface rather than identity table alone` (scripts/select_qa_mode_without_oracle.py:3042)
- `surveyor-certification lapse question needs direct certification-status surface rather than survey-result role rows` (scripts/select_qa_mode_without_oracle.py:3069)
- `intake-actor question needs explicit item-received-from provenance surface` (scripts/select_qa_mode_without_oracle.py:3203)
- `intake-actor question needs handoff/location event surface rather than ledger-entry rows alone` (scripts/select_qa_mode_without_oracle.py:3212)

### `operational_record_status`

- `status question has direct baseline status/rule support` (scripts/select_qa_mode_without_oracle.py:883)
- `status question has direct baseline application/status support and candidate is broad or relaxed-heavy` (scripts/select_qa_mode_without_oracle.py:897)
- `counterfactual or hold/readiness question has direct baseline rule/status support and candidate is broad or relaxed-heavy` (scripts/select_qa_mode_without_oracle.py:917)
- `response-content question needs compact filed-response surface rather than broad procedural expansion` (scripts/select_qa_mode_without_oracle.py:929)
- `contract-rescission status question needs request/outcome surface rather than approval vote surface alone` (scripts/select_qa_mode_without_oracle.py:943)
- `raw-timestamp question needs explicit raw_timestamp surface rather than corrected/event-correlation volume` (scripts/select_qa_mode_without_oracle.py:973)
- `snapshot-state question needs sampler state-plus-cause surface when the snapshot row asks why that state held` (scripts/select_qa_mode_without_oracle.py:982)
- `snapshot-state question needs sampler status surface rather than broad event-description volume` (scripts/select_qa_mode_without_oracle.py:989)
- `snapshot-state question needs explicit sampler_state surface rather than broad event-description or status volume` (scripts/select_qa_mode_without_oracle.py:996)
- `clear-sample clock snapshot question needs segment-plus-elapsed-time helper surface rather than snapshot text alone` (scripts/select_qa_mode_without_oracle.py:1005)
- `corrected-timestamp question needs explicit corrected-timestamp surface rather than rule-description context` (scripts/select_qa_mode_without_oracle.py:1025)
- `corrected-duration question needs paired raw/corrected badge-event surface rather than corrected timestamp volume alone` (scripts/select_qa_mode_without_oracle.py:1034)
- `expected-order question needs explicit expected-order surface rather than open-exception volume` (scripts/select_qa_mode_without_oracle.py:1176)
- `communications-officer drafting question needs notice-issued plus person-role surface rather than name lookup alone` (scripts/select_qa_mode_without_oracle.py:1230)
- `sampler-offline interval count needs explicit interval surface rather than state-start/end fragments` (scripts/select_qa_mode_without_oracle.py:1239)
- `sampler-offline interval count needs sampler-state transition surface rather than event-log volume` (scripts/select_qa_mode_without_oracle.py:1246)
- `packet-close audit-exception count needs semantic open-exception surface rather than expanded source-row evidence` (scripts/select_qa_mode_without_oracle.py:1275)
- `homeroom-reassignment correction question needs homeroom_reassigned surface rather than generic change-type rows` (scripts/select_qa_mode_without_oracle.py:1375)
- `homeroom-reassignment count question needs roster helper membership/count surface` (scripts/select_qa_mode_without_oracle.py:1384)
- `pending-rather-than-approved question needs determination reason and pending-verification surface over raw source rows` (scripts/select_qa_mode_without_oracle.py:1489)
- `trip-date question needs roster-state schedule surface rather than roster-version/source-record volume` (scripts/select_qa_mode_without_oracle.py:1516)
- `order-series identifier question needs exact document-identifier surface rather than section/event volume` (scripts/select_qa_mode_without_oracle.py:1550)
- `erratum report-of-record question needs archival document/version surface rather than generic document-status rows` (scripts/select_qa_mode_without_oracle.py:1840)
- `review-completion question needs explicit status-at surface rather than broad uncertainty labels` (scripts/select_qa_mode_without_oracle.py:1858)
- `date-event anchor enumeration needs incident-anchor surface rather than source-section volume` (scripts/select_qa_mode_without_oracle.py:1966)
- `governing-board vote-status question needs explicit pending-determination surface rather than unrelated negative records` (scripts/select_qa_mode_without_oracle.py:1975)
- `timekeeping clock-out question needs timekeeping or assignment interval surface rather than badge-exit event rows` (scripts/select_qa_mode_without_oracle.py:2027)
- `medication lot-number question needs source-record event attributes rather than self-check paraphrase or row-volume evidence` (scripts/select_qa_mode_without_oracle.py:2036)
- `unresolved policy-deviation question needs review/open-issue status surface rather than archival event volume` (scripts/select_qa_mode_without_oracle.py:2073)
- `court-determination question needs packet/source status surface rather than broad unresolved labels` (scripts/select_qa_mode_without_oracle.py:2093)
- `resolved-status question needs direct unresolved/disputed-status surface rather than archival evidence volume` (scripts/select_qa_mode_without_oracle.py:2123)
- `planning-application request question needs application-summary plus unit-mix surface rather than claim/status volume` (scripts/select_qa_mode_without_oracle.py:2150)
- `prior-proposal disposition question needs proposal-version/procedural-status surface rather than current-application volume` (scripts/select_qa_mode_without_oracle.py:2170)
- `contract-rescission status question keeps request/outcome surface over approval vote surface alone` (scripts/select_qa_mode_without_oracle.py:2199)
- `appeal-status question needs appeal event plus no-decision/deadline surface rather than bare docket status` (scripts/select_qa_mode_without_oracle.py:2256)
- `temporary-availability question needs attendance plus authority-transfer surface` (scripts/select_qa_mode_without_oracle.py:2267)
- `station-arrival-time question needs event/timestamp surface rather than roster identity rows` (scripts/select_qa_mode_without_oracle.py:2296)
- `temporary-role question needs roster-state role-hint support rather than bare group membership` (scripts/select_qa_mode_without_oracle.py:2305)
- `completion-report incident list needs trip-outcome plus issue/medical/hazard surfaces` (scripts/select_qa_mode_without_oracle.py:2316)
- `current operational status question needs explicit final-state surface rather than adjacent event/action evidence` (scripts/select_qa_mode_without_oracle.py:2593)
- `public-use extension question needs extension purpose/status surface rather than broad permit lifecycle volume` (scripts/select_qa_mode_without_oracle.py:2602)
- `unrestricted-active count question needs baseline status, restriction, suspension, and violation surfaces` (scripts/select_qa_mode_without_oracle.py:2738)
- `student-count question needs scoped final-attendance surface rather than broad roster volume` (scripts/select_qa_mode_without_oracle.py:2957)
- `group-designation suspension question needs event plus interval-membership surface rather than broad fallback rows` (scripts/select_qa_mode_without_oracle.py:2968)
- `temporary-supervisor absence question needs location-change plus supervision/medical-event surface` (scripts/select_qa_mode_without_oracle.py:2977)
- `post-reassignment group-count question needs stable membership/count surface over role-task volume` (scripts/select_qa_mode_without_oracle.py:2991)
- `temporary-team roster question needs scoped group-formation surface rather than standing roster volume` (scripts/select_qa_mode_without_oracle.py:3011)
- `no-touch hazard question needs incident/hazard observation surface rather than broad attendance roster` (scripts/select_qa_mode_without_oracle.py:3033)
- `adjusted-expiration question needs explicit current-expiration surface rather than extension-label or original-date evidence` (scripts/select_qa_mode_without_oracle.py:3231)
- `request filing timeliness question needs request/reinstatement threshold evidence rather than completion-window evidence` (scripts/select_qa_mode_without_oracle.py:3272)
- `commit-readiness question needs unresolved process evidence rather than a bare status value` (scripts/select_qa_mode_without_oracle.py:3286)
- `priority question needs explicit priority predicate surface rather than an underlying condition predicate` (scripts/select_qa_mode_without_oracle.py:3320)
- `decision-status question needs explicit decision surface rather than adjacent application/status evidence` (scripts/select_qa_mode_without_oracle.py:3333)
- `board-concern decision question needs event/action concern history rather than bare pending status` (scripts/select_qa_mode_without_oracle.py:3342)
- `deaccession-yet question needs explicit scheduled/not-formally-completed status surface rather than broad lot-history volume` (scripts/select_qa_mode_without_oracle.py:3368)
- `current-constitution eligibility question needs applicant-type plus controlling interpretation surface` (scripts/select_qa_mode_without_oracle.py:3431)
- `resubmission eligibility question needs proof/rule resolution surface rather than current applicant status surface` (scripts/select_qa_mode_without_oracle.py:3452)

### `rationale_evidence_contrast`

- `memo-establish question needs memo-content plus reliability-scope surface rather than broad investigative context` (scripts/select_qa_mode_without_oracle.py:1187)
- `phone-ping granularity question needs device-ping granularity surface rather than evidence-source summary` (scripts/select_qa_mode_without_oracle.py:1196)
- `evidence-source count question needs source-id catalog surface rather than generic evidence-source rows` (scripts/select_qa_mode_without_oracle.py:1205)
- `evidence-source count question needs source-id catalog surface rather than unresolved-fact volume` (scripts/select_qa_mode_without_oracle.py:1212)
- `negative-reliability question needs source-reliability scope rather than unresolved-activity status alone` (scripts/select_qa_mode_without_oracle.py:1221)
- `memo-resolution question needs claim plus unresolved-issue surface rather than permit/status fragments` (scripts/select_qa_mode_without_oracle.py:1785)
- `interval behavior-plus-cause question needs system-log event attributes rather than row-value volume` (scripts/select_qa_mode_without_oracle.py:1849)
- `position-source question needs statement/source-author surface rather than generic row-source labels` (scripts/select_qa_mode_without_oracle.py:1991)
- `timestamped message-source question needs direct log-entry surface rather than row-source fallback` (scripts/select_qa_mode_without_oracle.py:2000)
- `printed source-provenance question needs archival row/source labels rather than generic packet identifiers` (scripts/select_qa_mode_without_oracle.py:2016)
- `reply-memo theory question needs archival memo row value rather than generic source-document presence` (scripts/select_qa_mode_without_oracle.py:2102)
- `false-conflict consistency question needs paired intake/photo interpretation surface rather than row ledger fragments` (scripts/select_qa_mode_without_oracle.py:2132)
- `failed-vendor rationale question needs itemized vendor-deficiency surface` (scripts/select_qa_mode_without_oracle.py:2679)
- `failed-vendor rationale question needs inspection, vendor-status, and violation-detail surfaces together` (scripts/select_qa_mode_without_oracle.py:2686)
- `display-outcome question needs inspection/outcome plus permit-status surface` (scripts/select_qa_mode_without_oracle.py:2715)
- `display-outcome question needs date-specific permit validity plus incident/inspection surface` (scripts/select_qa_mode_without_oracle.py:2722)
- `second-violation duration question needs violation-record plus suspension-period surfaces together` (scripts/select_qa_mode_without_oracle.py:2731)
- `status-elevation rationale question needs lab/location/status context rather than bare status-change reason` (scripts/select_qa_mode_without_oracle.py:2803)
- `source-belief question needs claimant testimony surface rather than identification-status summary` (scripts/select_qa_mode_without_oracle.py:2878)
- `alternative-inscription question needs candidate-origin plus inscription/attribute surface` (scripts/select_qa_mode_without_oracle.py:2889)
- `missing-evidence question needs claimant testimony plus explicit absence/claim surfaces` (scripts/select_qa_mode_without_oracle.py:2916)
- `banner-change rationale question needs banner succession/creation surface rather than protest or score rows` (scripts/select_qa_mode_without_oracle.py:2925)
- `hold-call rationale question needs event-condition timing surface rather than broad witness/incident volume` (scripts/select_qa_mode_without_oracle.py:2939)
- `yellow-to-blue reassignment question keeps baseline transition surface over partial interval membership rows` (scripts/select_qa_mode_without_oracle.py:2984)
- `source-specific witness question needs Brigid report/claim surface rather than unresolved-discrepancy summary` (scripts/select_qa_mode_without_oracle.py:3002)
- `day-3 found-object question needs focused event/found-object surface rather than broad hazard summary` (scripts/select_qa_mode_without_oracle.py:3022)
- `conservator-date question needs source-recorded value surface rather than generic discrepancy rows` (scripts/select_qa_mode_without_oracle.py:3051)
- `display-authority question needs controlling governance/source-authority surface rather than display text rows` (scripts/select_qa_mode_without_oracle.py:3060)
- `source-claim question needs witness-statement surface rather than finding/provenance summary rows` (scripts/select_qa_mode_without_oracle.py:3087)
- `permission-request question needs direct witness-statement surface rather than evidence-date volume` (scripts/select_qa_mode_without_oracle.py:3096)
- `survey-commission question needs explicit report-commission provenance surface` (scripts/select_qa_mode_without_oracle.py:3105)
- `maintenance-evidence question needs receipt/evidence-source surface rather than witness/hearsay rows` (scripts/select_qa_mode_without_oracle.py:3121)
- `fictional-order question needs plot-outcome surface rather than plot-event summary rows` (scripts/select_qa_mode_without_oracle.py:3133)
- `boundary-discrepancy cause question needs measurement/marker-shift surface rather than survey-summary rows` (scripts/select_qa_mode_without_oracle.py:3147)
- `discrepancy-explanation question needs factual-discrepancy/incident-outcome surface rather than fictional event rows` (scripts/select_qa_mode_without_oracle.py:3185)
- `correction-authorship question needs handwriting/expert-attribution surface rather than correction-status volume` (scripts/select_qa_mode_without_oracle.py:3221)
- `evidentiary-status report question needs explicit witness/report surface rather than generic claim-status surface` (scripts/select_qa_mode_without_oracle.py:3253)
- `cause question has explicit baseline rationale-note support and candidate is broad record/event surface` (scripts/select_qa_mode_without_oracle.py:3307)
- `not-yet-tested question needs explicit pending test-status surface rather than broad negation over all lots` (scripts/select_qa_mode_without_oracle.py:3351)
- `split rationale question needs explicit source-note rationale plus viability context` (scripts/select_qa_mode_without_oracle.py:3379)
- `split rationale question needs actual split/lot-condition surface rather than generic vault assignment surface` (scripts/select_qa_mode_without_oracle.py:3393)
- `viability-concern question needs explicit source-note contrast plus viability context` (scripts/select_qa_mode_without_oracle.py:3404)

### `regulatory_access_scope`

- `personal-letter reading-access question needs semantic access authority plus publication-restriction boundary, not raw source rows alone` (scripts/select_qa_mode_without_oracle.py:1100)
- `universal-scope question needs broad set-enumeration surface rather than narrower report-detail joins` (scripts/select_qa_mode_without_oracle.py:2443)
- `termination-denial question needs rationale plus quantity-threshold support rather than status text alone` (scripts/select_qa_mode_without_oracle.py:2452)
- `lot-affected question needs explicit target-lot exclusion/check surface rather than broad affected-lot listing` (scripts/select_qa_mode_without_oracle.py:2461)
- `counterfactual reclassification deadline question needs classification-bound deadline surface` (scripts/select_qa_mode_without_oracle.py:2472)
- `placed-under-quarantine count needs mistaken-movement surface rather than broad quarantine-scope volume` (scripts/select_qa_mode_without_oracle.py:2757)
- `split-lot never-quarantined count needs quarantine-scope surface rather than broad lot status history` (scripts/select_qa_mode_without_oracle.py:2769)
- `initial-affected greenhouse question needs greenhouse-status plus exclusion/location surface` (scripts/select_qa_mode_without_oracle.py:2785)

### `rule_activation_surface`

- `rescission-request eligibility question needs request/validity surface rather than generic vote-rule volume` (scripts/select_qa_mode_without_oracle.py:935)
- `rule-effect question needs supersession plus status/event surface rather than adjacent rule text` (scripts/select_qa_mode_without_oracle.py:1640)
- `rule-effect question needs direct bylaw-rule surface rather than partial requirement rows` (scripts/select_qa_mode_without_oracle.py:1649)
- `rule-effect question needs archival rule text rather than partial requirement rows` (scripts/select_qa_mode_without_oracle.py:1656)
- `rule-effect question needs explicit transfer requirement surface rather than ownership/status rows` (scripts/select_qa_mode_without_oracle.py:1665)
- `rule-effect question needs archival memo row value rather than ownership/status rows` (scripts/select_qa_mode_without_oracle.py:1672)
- `override-rule requirement question needs explicit source-record rule requirement surface rather than archival row values` (scripts/select_qa_mode_without_oracle.py:2045)
- `revised-plan monitoring question needs plan/rejection rule surface rather than observation-status rows` (scripts/select_qa_mode_without_oracle.py:2234)
- `appeal-tolling question needs rule text plus appeal/deadline surface rather than isolated tolling labels` (scripts/select_qa_mode_without_oracle.py:2245)
- `deferment-rationale question needs interpreted decision support rather than rule text alone` (scripts/select_qa_mode_without_oracle.py:2481)
- `component-problem question needs project-category plus rule-condition surface` (scripts/select_qa_mode_without_oracle.py:2490)
- `counterfactual-recusal outcome question needs both procedure path and eligibility surface` (scripts/select_qa_mode_without_oracle.py:2505)
- `recusal-rationale question needs recusal rule surface rather than eligibility determination surface` (scripts/select_qa_mode_without_oracle.py:2514)
- `post-recusal vote question needs recusal/vote/rule surface without misleading quorum-status volume` (scripts/select_qa_mode_without_oracle.py:2523)
- `window-merit question needs explicit rule-condition plus prior-history surface` (scripts/select_qa_mode_without_oracle.py:2532)
- `window-merit question needs prior-history plus interpretation surface` (scripts/select_qa_mode_without_oracle.py:2541)
- `amendment-recall question needs recall-authority surface rather than threshold-only legal-opinion rows` (scripts/select_qa_mode_without_oracle.py:2552)
- `rejection-cause question needs correction/clarification surface rather than derived status alone` (scripts/select_qa_mode_without_oracle.py:2561)
- `hypothetical reserve-status question keeps baseline arithmetic inputs over derived rule status` (scripts/select_qa_mode_without_oracle.py:2568)
- `hypothetical reserve-status question needs baseline arithmetic inputs rather than derived rule status` (scripts/select_qa_mode_without_oracle.py:2575)
- `valid-period extension question needs original validity plus extension-validity surface` (scripts/select_qa_mode_without_oracle.py:2611)
- `unrenewed-expiry question needs validity plus deadline/requirement surface` (scripts/select_qa_mode_without_oracle.py:2620)
- `unrenewed-expiry question needs original validity endpoint surface rather than renewed lifecycle rows` (scripts/select_qa_mode_without_oracle.py:2627)
- `appeal-hearing question needs filed-appeal/hearing-scheduled surface rather than broad status rows` (scripts/select_qa_mode_without_oracle.py:2636)
- `suspension-trigger question needs explicit violation-record plus permit-suspension surface` (scripts/select_qa_mode_without_oracle.py:2645)
- `suspension-trigger question needs violation event plus suspension surface, not suspension interval volume alone` (scripts/select_qa_mode_without_oracle.py:2654)
- `failed-reinspection count question needs compact aggregate inspection-result surface rather than lifecycle status volume` (scripts/select_qa_mode_without_oracle.py:2670)
- `permitted-hours question needs explicit operational-hours rule surface` (scripts/select_qa_mode_without_oracle.py:2695)
- `approved-display count question needs approval/validity surface rather than broad current-status rows` (scripts/select_qa_mode_without_oracle.py:2706)
- `permit-action list question needs suspension, restriction, status, and deadline surfaces together` (scripts/select_qa_mode_without_oracle.py:2747)

### `state_custody_ownership`

- `award/result question has baseline awarded support and candidate lacks awarded rows` (scripts/select_qa_mode_without_oracle.py:874)
- `near-duplicate bin-code question needs collision-risk plus bin-location surface rather than generic current-label rows` (scripts/select_qa_mode_without_oracle.py:1054)
- `physical-custody item-count question needs grouped custody count helper rather than raw custodian row count` (scripts/select_qa_mode_without_oracle.py:1074)
- `governing-2024-custody-document question needs exact amendment source-row text with custody/notice clauses` (scripts/select_qa_mode_without_oracle.py:1111)
- `location-plus-publication-pause question needs custody plus publication restriction surface` (scripts/select_qa_mode_without_oracle.py:1131)
- `MOU-scope expansion question needs agreement-clause plus access/addition surface rather than static right-scope volume` (scripts/select_qa_mode_without_oracle.py:1140)
- `photograph-album interval question needs exact access-log custody surface rather than broad access-event volume` (scripts/select_qa_mode_without_oracle.py:1149)
- `photograph-album interval question needs access/recall custody surface rather than broad conservation-scope volume` (scripts/select_qa_mode_without_oracle.py:1158)
- `custody-release question needs custody/status surface rather than scan-record volume` (scripts/select_qa_mode_without_oracle.py:1167)
- `barcode-supersession question needs scan/correction surface rather than broad current-barcode volume` (scripts/select_qa_mode_without_oracle.py:1541)
- `tree-amendment measurement question needs archival row-value surface preserving species/DBH/source basis` (scripts/select_qa_mode_without_oracle.py:1740)
- `dated physical-location question needs archival row location plus row-time support rather than synthesized cold self-check` (scripts/select_qa_mode_without_oracle.py:2082)
- `current object-component question needs direct current-state/component surface rather than transition history volume` (scripts/select_qa_mode_without_oracle.py:2358)
- `why-have question needs custody-transfer surface rather than adjacent action or object-property rows` (scripts/select_qa_mode_without_oracle.py:2367)
- `award placement question needs explicit award-result surface rather than nearby device/person rows` (scripts/select_qa_mode_without_oracle.py:2376)
- `carry question needs direct possession surface rather than broad title or event evidence` (scripts/select_qa_mode_without_oracle.py:2397)
- `possession-versus-ownership question needs inherit/own/possess distinction surface rather than broad event/rule evidence` (scripts/select_qa_mode_without_oracle.py:2408)
- `legal-title contest question needs claim/default/transfer surface rather than static ownership rows` (scripts/select_qa_mode_without_oracle.py:2417)
- `provisional-control question needs holder plus pending estate/claim context rather than bare holder row` (scripts/select_qa_mode_without_oracle.py:2823)
- `post-death legal-ownership question needs court/inheritance status surface rather than stale legal-owner interval` (scripts/select_qa_mode_without_oracle.py:2834)
- `current possession/maintenance question needs physical-possessor plus gift/dispute surface` (scripts/select_qa_mode_without_oracle.py:2845)
- `solicitor-advice question needs advice plus adverse-possession caveat surface` (scripts/select_qa_mode_without_oracle.py:2856)
- `insurance-link question needs direct insured-by surface rather than contingent ownership claim rows` (scripts/select_qa_mode_without_oracle.py:2907)
- `disputed-strip feature question needs object-location surface rather than broad finding/survey rows` (scripts/select_qa_mode_without_oracle.py:3078)
- `physical inventory count question needs incident/count outcome surface rather than title-name rows` (scripts/select_qa_mode_without_oracle.py:3173)
- `client-ledger pickup question needs asset-state/location surface rather than broad item provenance rows` (scripts/select_qa_mode_without_oracle.py:3194)
- `correction-entitlement question needs entitlement rule plus extension effect surface rather than correction/admission rows alone` (scripts/select_qa_mode_without_oracle.py:3244)

### `threshold_policy_arithmetic`

- `density-calculation question needs numeric staff-evaluation surface rather than qualitative source-opinion surface` (scripts/select_qa_mode_without_oracle.py:922)
- `active-held count question needs current-label/status plus withdrawn-label filter surface` (scripts/select_qa_mode_without_oracle.py:1065)
- `packet-close open-item count needs explicit open-item surface rather than deadline/notice volume` (scripts/select_qa_mode_without_oracle.py:1264)
- `application-disposition question needs status/determination surface rather than source-record-facts gap` (scripts/select_qa_mode_without_oracle.py:1284)
- `roster-entry count question needs entry-preserving roster surface rather than distinct-student membership volume` (scripts/select_qa_mode_without_oracle.py:1297)
- `distinct-student registrar count needs roster-table count support rather than member-label enumeration` (scripts/select_qa_mode_without_oracle.py:1306)
- `distinct-student count-change question needs roster-version count summary rather than itemized membership volume` (scripts/select_qa_mode_without_oracle.py:1328)
- `adult-total roster question needs adult manifest support rather than qualifying-chaperone count alone` (scripts/select_qa_mode_without_oracle.py:1393)
- `adult-total roster question needs chaperone change surface rather than qualifying-chaperone count alone` (scripts/select_qa_mode_without_oracle.py:1407)
- `ratio-compliance question needs compliance_status surface rather than roster-table version volume` (scripts/select_qa_mode_without_oracle.py:1433)
- `correction-notice replacement question needs change-type surface rather than unparsed correction-action text` (scripts/select_qa_mode_without_oracle.py:1442)
- `application-count question needs canonical application-status surface rather than source-record duplicate rows` (scripts/select_qa_mode_without_oracle.py:1456)
- `cap-application question needs rule/determination surface over expanded source-record rows` (scripts/select_qa_mode_without_oracle.py:1467)
- `counterfactual no-cap amount question needs arithmetic/grant amount surface rather than broad memory-ledger context` (scripts/select_qa_mode_without_oracle.py:1478)
- `date-alone rule question needs threshold plus exception surface rather than broad applicant-date volume` (scripts/select_qa_mode_without_oracle.py:1498)
- `projection-supersession question needs trigger/actual event surface rather than projection-comparison volume` (scripts/select_qa_mode_without_oracle.py:1507)
- `threshold question needs rule-threshold surface rather than applicant-attribute volume` (scripts/select_qa_mode_without_oracle.py:1525)
- `threshold question needs rule threshold/condition surface rather than applicant-attribute volume` (scripts/select_qa_mode_without_oracle.py:1532)
- `application-number identifier question needs exact document-identifier surface rather than score/event volume` (scripts/select_qa_mode_without_oracle.py:1559)
- `headcount-scan reconciliation question needs paired count/scan evidence rather than generic source-record claims` (scripts/select_qa_mode_without_oracle.py:1595)
- `focused semantic surface beats archival row-volume for status/score/authority questions` (scripts/select_qa_mode_without_oracle.py:1731)
- `operative-permit question needs permit issuance/amendment surface rather than source-document status alone` (scripts/select_qa_mode_without_oracle.py:1749)
- `tree-list/count question needs amendment count/list surface rather than stale protection-status rows` (scripts/select_qa_mode_without_oracle.py:1758)
- `remedy-imposition question needs unresolved-issue surface rather than remedy-label presence` (scripts/select_qa_mode_without_oracle.py:1767)
- `hearing-held question needs event/open-issue surface rather than scheduled-date presence` (scripts/select_qa_mode_without_oracle.py:1776)
- `packet-time measurement question needs direct measurement-value surface rather than row-value volume` (scripts/select_qa_mode_without_oracle.py:1794)
- `active-lot count question needs archival inventory row enumeration rather than contaminant/status volume` (scripts/select_qa_mode_without_oracle.py:1867)
- `document-identification question needs document-exhibit surface rather than event/source-type rows` (scripts/select_qa_mode_without_oracle.py:1876)
- `exhibit-identification question needs exhibit/source-document surface rather than witness/person rows` (scripts/select_qa_mode_without_oracle.py:1885)
- `roster-of-record membership question needs assigned/person roster surface rather than supersession metadata` (scripts/select_qa_mode_without_oracle.py:1894)
- `withdrawn-draft governance question needs source-status/supersession surface rather than document-id presence` (scripts/select_qa_mode_without_oracle.py:1903)
- `headcount elapsed-time question needs elapsed-minutes surface rather than headcount rows alone` (scripts/select_qa_mode_without_oracle.py:1921)
- `parent-letter determination question needs review-scheduled/letter surface rather than source-document volume` (scripts/select_qa_mode_without_oracle.py:1930)
- `witness-scan reconciliation question needs direct scan/location surface rather than broad source-record claims` (scripts/select_qa_mode_without_oracle.py:1939)
- `newsletter-versus-roster authority question needs supersession/roster evidence rather than stale assignment rows` (scripts/select_qa_mode_without_oracle.py:1948)
- `current-versus-withdrawn claim question needs statement-claim plus supersession/status surface` (scripts/select_qa_mode_without_oracle.py:1957)
- `scoped roster-count question needs source-record roster section surface rather than badge/log volume` (scripts/select_qa_mode_without_oracle.py:2063)
- `deed item-count question needs conveyed-item surface rather than broad receipt row volume` (scripts/select_qa_mode_without_oracle.py:2111)
- `zoning-designation question needs parcel-zoning surface rather than general zoning-definition volume` (scripts/select_qa_mode_without_oracle.py:2159)
- `build-out timeline question needs site-measure plus draft-condition surface rather than permit-expiry status alone` (scripts/select_qa_mode_without_oracle.py:2179)
- `dimensional-standards question needs staff-finding plus site-measure surface rather than consolidated compliance status alone` (scripts/select_qa_mode_without_oracle.py:2190)
- `deadline-filing timeliness question needs filed-event plus calculated-deadline surface` (scripts/select_qa_mode_without_oracle.py:2212)
- `board-review-period question needs calculated-deadline surface rather than loose deadline values` (scripts/select_qa_mode_without_oracle.py:2223)
- `attendance-count question needs explicit session_attendance_count surface rather than interval roster volume` (scripts/select_qa_mode_without_oracle.py:2278)
- `lot plant-count question needs direct lot/count surface rather than status or destruction history` (scripts/select_qa_mode_without_oracle.py:2776)
- `lot-3b lab-result question needs lab-result plus lot-status context, not generic lab-result volume` (scripts/select_qa_mode_without_oracle.py:2794)
- `candidate-vessel list question needs candidate-origin plus vessel-loss detail surface` (scripts/select_qa_mode_without_oracle.py:2898)
- `corrected-rank-order question needs qualifying-rank plus score-correction surface rather than raw total volume` (scripts/select_qa_mode_without_oracle.py:2948)
- `claim-value question needs financial-value/incident-outcome surface rather than claim/status fiction rows` (scripts/select_qa_mode_without_oracle.py:3162)
- `hypothetical failed-viability question keeps direct baseline threshold/storage support over broader policy-note surfaces` (scripts/select_qa_mode_without_oracle.py:3411)
- `hypothetical failed-viability question needs threshold/action policy surface rather than note surface` (scripts/select_qa_mode_without_oracle.py:3420)

## Promotion Discipline

- Add a guard freely when it protects a measured row-level failure.
- Do not call a guard a new lens until it transfers or clearly belongs to a family.
- If a family grows past a readable size, split by semantic reason, not by fixture.
- Do not hide guard growth inside parameter bags. A family generator must report its enumerated surfaces, transfer evidence, and retirement candidates.
- Prefer retiring guards when compile/query/helper improvements make the originating failure pass without selector intervention.
- If a guard remains unclassified, either retire it, rename it, or add a family with a purpose.
