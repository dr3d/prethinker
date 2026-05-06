# Selector Guard Family Rollup

This report keeps the selector guard surface from turning into a pile of
fixture-shaped knobs. Individual guards are allowed while they are being
measured, but they should collapse into a small number of semantic families
before they become daily-driver harness doctrine.

Generated from `scripts/select_qa_mode_without_oracle.py`.

## Summary

- guard return sites: `53`
- unique guard reasons: `52`
- classified families: `7`
- unclassified reasons: `0`

## Family Counts

| Family | Count | Purpose |
| --- | ---: | --- |
| `entity_role_authority` | 8 | Separate identity, role definition, acting authority, collector, contract authority, and guardianship rows from broad action or title-only evidence. |
| `operational_record_status` | 13 | Protect current status, request timing, commit readiness, decision, priority, concern, constitution, and resubmission rows from nearby but less answer-bearing record/event surfaces. |
| `rationale_evidence_contrast` | 6 | Route why/cause, witness/report, source-note, split rationale, viability contrast, and pending test questions to explicit rationale or evidentiary support instead of adjacent status rows. |
| `regulatory_access_scope` | 5 | Route all/any scope, termination denial, affected-lot exclusion, and reclassification-deadline questions to access surfaces that carry the right set, threshold, target, or temporal boundary. |
| `rule_activation_surface` | 11 | Route promoted rule, eligibility, recall, recusal, window, rejection, and reserve questions to the evidence surface that contains both the governing condition and the instance facts needed to apply it. |
| `state_custody_ownership` | 8 | Separate current object state, custody transfer, possession, ownership, legal title, and award/result surfaces from generic event, property, or person rows. |
| `threshold_policy_arithmetic` | 2 | Prefer direct threshold, quantity, storage, policy-action, and arithmetic inputs when a broader policy or derived-status surface is tempting but incomplete. |

## Guard Reasons

### `entity_role_authority`

- `identity question has baseline name/role support and candidate is broad action-heavy` (scripts/select_qa_mode_without_oracle.py:734)
- `collector identity question needs direct collector predicate surface rather than broad status/note evidence` (scripts/select_qa_mode_without_oracle.py:814)
- `superlative identity question needs explicit age/identity surface rather than broad role membership rows` (scripts/select_qa_mode_without_oracle.py:825)
- `official identity question needs role-authority definition surface rather than action volume or title-only rows` (scripts/select_qa_mode_without_oracle.py:838)
- `reinstatement question needs focused role-history surface rather than broad current-role or rule evidence` (scripts/select_qa_mode_without_oracle.py:876)
- `contract-validity question needs explicit acting-authority surface rather than generic rule evidence` (scripts/select_qa_mode_without_oracle.py:915)
- `contract-validity question needs authority-source surface rather than unrelated ownership or entity rows` (scripts/select_qa_mode_without_oracle.py:922)
- `guardianship-validity question needs residence/resumption condition surface rather than bare guardianship status` (scripts/select_qa_mode_without_oracle.py:1080)

### `operational_record_status`

- `status question has direct baseline status/rule support` (scripts/select_qa_mode_without_oracle.py:752)
- `status question has direct baseline application/status support and candidate is broad or relaxed-heavy` (scripts/select_qa_mode_without_oracle.py:766)
- `counterfactual or hold/readiness question has direct baseline rule/status support and candidate is broad or relaxed-heavy` (scripts/select_qa_mode_without_oracle.py:786)
- `current operational status question needs explicit final-state surface rather than adjacent event/action evidence` (scripts/select_qa_mode_without_oracle.py:1089)
- `adjusted-expiration question needs explicit current-expiration surface rather than extension-label or original-date evidence` (scripts/select_qa_mode_without_oracle.py:1099)
- `request filing timeliness question needs request/reinstatement threshold evidence rather than completion-window evidence` (scripts/select_qa_mode_without_oracle.py:1140)
- `commit-readiness question needs unresolved process evidence rather than a bare status value` (scripts/select_qa_mode_without_oracle.py:1154)
- `priority question needs explicit priority predicate surface rather than an underlying condition predicate` (scripts/select_qa_mode_without_oracle.py:1188)
- `decision-status question needs explicit decision surface rather than adjacent application/status evidence` (scripts/select_qa_mode_without_oracle.py:1201)
- `board-concern decision question needs event/action concern history rather than bare pending status` (scripts/select_qa_mode_without_oracle.py:1210)
- `deaccession-yet question needs explicit scheduled/not-formally-completed status surface rather than broad lot-history volume` (scripts/select_qa_mode_without_oracle.py:1236)
- `current-constitution eligibility question needs applicant-type plus controlling interpretation surface` (scripts/select_qa_mode_without_oracle.py:1299)
- `resubmission eligibility question needs proof/rule resolution surface rather than current applicant status surface` (scripts/select_qa_mode_without_oracle.py:1320)

### `rationale_evidence_contrast`

- `evidentiary-status report question needs explicit witness/report surface rather than generic claim-status surface` (scripts/select_qa_mode_without_oracle.py:1121)
- `cause question has explicit baseline rationale-note support and candidate is broad record/event surface` (scripts/select_qa_mode_without_oracle.py:1175)
- `not-yet-tested question needs explicit pending test-status surface rather than broad negation over all lots` (scripts/select_qa_mode_without_oracle.py:1219)
- `split rationale question needs explicit source-note rationale plus viability context` (scripts/select_qa_mode_without_oracle.py:1247)
- `split rationale question needs actual split/lot-condition surface rather than generic vault assignment surface` (scripts/select_qa_mode_without_oracle.py:1261)
- `viability-concern question needs explicit source-note contrast plus viability context` (scripts/select_qa_mode_without_oracle.py:1272)

### `regulatory_access_scope`

- `universal-scope question needs broad set-enumeration surface rather than narrower report-detail joins` (scripts/select_qa_mode_without_oracle.py:932)
- `termination-denial question needs rationale plus quantity-threshold support rather than status text alone` (scripts/select_qa_mode_without_oracle.py:941)
- `lot-affected question needs explicit target-lot exclusion/check surface rather than broad affected-lot listing` (scripts/select_qa_mode_without_oracle.py:950)
- `counterfactual reclassification deadline question needs classification-bound deadline surface` (scripts/select_qa_mode_without_oracle.py:959)
- `counterfactual reclassification deadline question needs classification-bound deadline surface` (scripts/select_qa_mode_without_oracle.py:968)

### `rule_activation_surface`

- `deferment-rationale question needs interpreted decision support rather than rule text alone` (scripts/select_qa_mode_without_oracle.py:977)
- `component-problem question needs project-category plus rule-condition surface` (scripts/select_qa_mode_without_oracle.py:986)
- `counterfactual-recusal outcome question needs both procedure path and eligibility surface` (scripts/select_qa_mode_without_oracle.py:1001)
- `recusal-rationale question needs recusal rule surface rather than eligibility determination surface` (scripts/select_qa_mode_without_oracle.py:1010)
- `post-recusal vote question needs recusal/vote/rule surface without misleading quorum-status volume` (scripts/select_qa_mode_without_oracle.py:1019)
- `window-merit question needs explicit rule-condition plus prior-history surface` (scripts/select_qa_mode_without_oracle.py:1028)
- `window-merit question needs prior-history plus interpretation surface` (scripts/select_qa_mode_without_oracle.py:1037)
- `amendment-recall question needs recall-authority surface rather than threshold-only legal-opinion rows` (scripts/select_qa_mode_without_oracle.py:1048)
- `rejection-cause question needs correction/clarification surface rather than derived status alone` (scripts/select_qa_mode_without_oracle.py:1057)
- `hypothetical reserve-status question keeps baseline arithmetic inputs over derived rule status` (scripts/select_qa_mode_without_oracle.py:1064)
- `hypothetical reserve-status question needs baseline arithmetic inputs rather than derived rule status` (scripts/select_qa_mode_without_oracle.py:1071)

### `state_custody_ownership`

- `award/result question has baseline awarded support and candidate lacks awarded rows` (scripts/select_qa_mode_without_oracle.py:743)
- `current object-component question needs direct current-state/component surface rather than transition history volume` (scripts/select_qa_mode_without_oracle.py:847)
- `why-have question needs custody-transfer surface rather than adjacent action or object-property rows` (scripts/select_qa_mode_without_oracle.py:856)
- `award placement question needs explicit award-result surface rather than nearby device/person rows` (scripts/select_qa_mode_without_oracle.py:865)
- `carry question needs direct possession surface rather than broad title or event evidence` (scripts/select_qa_mode_without_oracle.py:886)
- `possession-versus-ownership question needs inherit/own/possess distinction surface rather than broad event/rule evidence` (scripts/select_qa_mode_without_oracle.py:897)
- `legal-title contest question needs claim/default/transfer surface rather than static ownership rows` (scripts/select_qa_mode_without_oracle.py:906)
- `correction-entitlement question needs entitlement rule plus extension effect surface rather than correction/admission rows alone` (scripts/select_qa_mode_without_oracle.py:1112)

### `threshold_policy_arithmetic`

- `hypothetical failed-viability question keeps direct baseline threshold/storage support over broader policy-note surfaces` (scripts/select_qa_mode_without_oracle.py:1279)
- `hypothetical failed-viability question needs threshold/action policy surface rather than note surface` (scripts/select_qa_mode_without_oracle.py:1288)

## Promotion Discipline

- Add a guard freely when it protects a measured row-level failure.
- Do not call a guard a new lens until it transfers or clearly belongs to a family.
- If a family grows past a readable size, split by semantic reason, not by fixture.
- If a guard remains unclassified, either retire it, rename it, or add a family with a purpose.
