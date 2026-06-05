# Oracle Authoring Notes — state_ag_settlement_aod_transfer_003

Instrument: NY OAG Assurance of Discontinuance, In re Equifax Information Services LLC — AOD 24-102.
Authored from `source.md` + `ontology_registry.json` only; blind to model outputs/run artifacts.
Unlike transfer_002, this source is the **full instrument** (recitals, findings 1-9, agreement 1-37,
monetary relief, communications, and the signature block), so all eight carrier lanes are populated.

## Expected facts (29) and source basis

### Instrument (1) — caption + para 37
- `aod_24_102`, `assurance_of_discontinuance`, `new_york_attorney_general`, respondent
  `equifax_information_services_llc`, number `assurance_24_102` ("AOD 24-102"). **effective_date
  v_2025_01_02** is stated: agreement para 37 ("The effective date of this Assurance shall be
  January 2, 2025") and the signature block ("Date: Jan. 2, 2025").

### Parties (4)
- regulator `new_york_attorney_general` (caption: Letitia James, AG of New York).
- respondent `equifax_information_services_llc` (caption).
- registered_agent `prentice_hall_corporation_system_inc` (para 3: "registered agent The
  Prentice-Hall Corporation System, Inc.").
- counsel `alston_bird_llp` (signature block / communications para 25: "Counsel for Equifax").

### Authority citations (7)
- Investigation authority (recitals): `executive_law_63_12`, `gbl_349`, `gbl_350`.
- `executive_law_63_15` as `assurance_authority` (para 1: "willing to accept the terms ... pursuant
  to New York Executive Law § 63(15)").
- `gbl_349_d` as `payment_authority` (para 15: "pursuant to GBL §§ 349-d").
- `public_officers_law_87` as `confidentiality_authority` (para 14: information "excepted from
  disclosure under Public Officers Law § 87").
- `gbl_380_j` as `prospective_relief_authority` (paras 6/8: NYFCRA accuracy compliance).
  (Section 63(12)/349/350 are cited once as investigation authority; their re-listing in para 5 as
  compliance statutes is not duplicated into a second role.)

### Events (4) — exact-date OMS chronology
- `code_change_introduced v_2022_03_17` (para 5); `equifax_investigation_initiated v_2022_03_22`
  (para 5); `oms_issue_partially_resolved v_2022_04_06` (para 6); `oms_issue_fully_resolved
  v_2022_04_08` (para 6).

### Obligations (5) — numbered prospective-relief paragraphs
- `obligation_9 change_control_review` (para 9); `obligation_11 training_program` (para 11);
  `obligation_13 incident_monitoring weekly` (para 13: "not less than once per week" -> frequency
  `weekly`); `obligation_14 cooperation` (para 14); `obligation_20 documentation_on_request`
  (para 20). due_or_effective_date is `not_stated` (no per-obligation deadline; the document-wide
  effective date is deliberately not copied into obligation slots, per the registry note).

### Monetary payment (1) — para 15
- payor `equifax_information_services_llc`, payee `state_of_new_york` ("check payable to the State
  of New York"), amount `usd_725000`, kind `restitution_and_penalties` ("to be used as restitution
  and penalties"), timing `within_30_days` ("within thirty (30) days after the date of this
  Assurance").

### Contact channels (3) — communications para 25, brand/role-correct
- `nicholas_oldham_equifax_com` -> `equifax_information_services_llc` (respondent_contact).
- `john_redding_alston_com` -> `alston_bird_llp` (counsel_contact).
- `glenna_goldis_ag_ny_gov` -> `new_york_attorney_general` (regulator_contact).

### Signatures (4) — signature block, Date Jan. 2, 2025
- `jane_azia` (bureau_chief) and `glenna_goldis` (assistant_attorney_general) for the NYAG;
  `nick_oldham` (chief_compliance_officer) for Equifax; `john_redding` (counsel) for Alston & Bird.

## Omitted / ambiguous areas (deliberately not authored)
- **Letitia James** is named at the head of the signature block, but the block is executed "By: Jane
  Azia" and "By: Glenna Goldis"; James did not personally sign, so no James signature is authored
  (James-as-signatory is a forbidden control).
- **Findings substance** (76,000 affected consumers; soft-inquiry count; "may have caused some
  consumers to be denied credit"; the no-admission clause in para 17) is narrative/finding content,
  not skeleton anatomy -> not authored (and two of these are forbidden controls).
- **Paragraphs 38-39** are referenced (e.g., "voided pursuant to paragraph 39") but their text is not
  rendered in `source.md`, so nothing is authored from them.
- **Phone numbers** in the communications/signature blocks are not authored (scope prioritizes email
  channels); only email channels are captured.
- **"Comply with the law" paragraphs 5-8** are largely statutory-compliance restatements; only the
  distinct operational obligations (9, 11, 13, 14, 20) are authored as obligation rows, and the
  relevant statutes are captured once in the authority lane.

## Forbidden controls (12) — what they test
prose caption blob in instrument_number; Equifax-as-regulator (wrong party-role); Prentice-Hall-as-
respondent (wrong party-role); narrative descriptor as party_name (prose party); GBL 349-d as
investigation authority (wrong authority-role); statute-description prose in a citation slot (prose
authority); Oldham/Equifax email tied to the NYAG (wrong contact attachment); notice-method narrative
in a channel_value slot (prose contact); within_60_days instead of within_30_days (wrong deadline);
discretionary-use sentence in the payment_kind slot (prose monetary); Letitia James as a signatory
(signature-role confusion); and a finding ("consumers_denied_credit") authored as a dated event
(open-ended finding refused).

All facts use only registered `state_ag_settlement_v1` signatures with correct arities; the forbidden
set is disjoint from expected; both files parse.
