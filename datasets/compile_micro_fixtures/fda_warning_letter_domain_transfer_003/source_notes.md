# source_notes.md - fda_warning_letter_domain_transfer_003

Oracle notes only. Not consumed by compile.

## Source

- URL: https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/liebel-flarsheim-company-llc-711508-10172025
- Title: Liebel-Flarsheim Company LLC - 711508 - 10/17/2025
- Center: CDER, Office of Manufacturing Quality, Office of Compliance
- Company: Liebel-Flarsheim Company LLC, wholly owned subsidiary of Guerbet America LLC
- Real public-domain U.S. federal document. Different company, FEI, geography, and product line from transfer_001 and transfer_002.

## Why this letter was selected

The primary purpose is to give the two transfer_002 residue families a second unlike data point:

1. `observation_subject = environmental_monitoring_excursion` with role `violation_scope`.
2. `procedure_scope = *_validation`.

Liebel-Flarsheim is on-point for both. Violation 1 is an investigation-failure violation built on in-process bioburden excursions and OOS endotoxin invalidations, with clear response-inadequacy critiques. Violation 1 also raises terminal sterilization validation adequacy. Violation 2 carries environmental-monitoring-excursion evidence and facility/equipment-control pressure.

The letter also adds a real consultant recommendation and a response contact.

## Numbered-Violation Count Caveat

This letter has two numbered violations, below the "at least 3 if possible" preference. It was chosen anyway because residue-family fit is the stated primary purpose and the substructure exercises several FDA detail families cleanly.

## Carrier-Shape Assumptions

- `fda_violation_detail/5` follows the live registry order:
  `violation_id, detail_kind, detail_value, role_or_purpose, source_or_scope`.
- `fda_correspondence_party/5` follows the live registry order:
  `letter_id, party_id, party_role, party_name, source_or_scope`.
- Dates, citations, FEI values, violation numbers, and deadline values use the compact atom conventions from transfer_001/002, such as `v_2025_10_17`, `cfr_21_211_192`, `fei_1028892`, `violation_1`, and `fifteen_working_days`.
- Expected facts use only signatures registered in `datasets/domain_profiles/fda_warning_letter_v1/ontology_registry.json`.

## Violation Category Rationale

- Violation 1 uses `investigation_failure` because the source pressure is failure to thoroughly investigate bioburden excursions and OOS endotoxin results under 21 CFR 211.192.
- Violation 2 uses `facility_equipment_control` because the source describes cleanroom controls, HEPA/vent gaps, equipment rust, and facility/equipment maintenance under 21 CFR 211.42(c) and 21 CFR 211.63.

## Role-Ambiguity Design

Under Violation 1, the expected facts separate the cited deficiency from FDA's evaluation of the firm's response:

- `(record_review_subject, oos_endotoxin_result, violation_scope)` is the cited subject of the investigation-failure violation.
- `(response_status, inadequate, corrective_action_evaluation)` is FDA's evaluation of the firm's response.

Forbidden facts catch the tempting role swaps, including OOS subject tagged as `corrective_action_evaluation` and CAPA critique tagged as `violation_scope`.

## Residue-Family Second Data Points

- EM family: `fda_violation_detail(V2, observation_subject, environmental_monitoring_excursion, violation_scope, _)`, supported by the environmental monitoring program discussion under violation 2. This is not a `record_review_subject` row because violation 2 is framed as a facility/equipment-control violation, not an investigation or record-review failure.
- Validation family: `fda_violation_detail(V1, procedure_scope, terminal_sterilization_process_validation, violation_scope, _)`, supported by the terminal sterilization validation discussion under violation 1.

Both reuse governed value/kind/role atoms from transfer_002 so the gate can measure whether those families transfer rather than introducing fresh incomparable vocabulary.

## Facts Deliberately Not Represented

- The amended-letter note is not represented as `fda_prior_warning_letter/5`; it is an amendment of the same reference number, not a separate prior warning letter.
- No `fda_regulatory_meeting/4` is emitted. The GDUFA III footnote states only future eligibility for a Post-Warning Letter Meeting, so the absence is accounted as `domain_omission(.., 'fda_regulatory_meeting/4', none_found, future_eligibility_only_no_meeting_held, ..)`.
- Redacted `(b)(4)` details are not used as expected atoms.
- The rust/corrosion equipment defect is not an expected `fda_violation_detail/5` row because the current detail-kind value domain has no dedicated facility-defect slot. It remains source context for violation 2.

## Atom-Choice Notes

- `qualified_cgmp_consultant` and `consultant_engagement` are used for the consultant recommendation because the source invokes 21 CFR 211.34.
- A separate `fda_violation_citation/4` row captures `cfr_21_211_34` with role `consultant_qualification`.
- The response requirement is represented as one written-response obligation with an electronic-submission channel, rather than a separate reply-channel pseudo-obligation.
