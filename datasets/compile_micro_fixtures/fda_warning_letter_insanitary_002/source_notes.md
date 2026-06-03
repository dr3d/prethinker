# source_notes.md — fda_warning_letter_insanitary_002 (US Specialty Formulations, LLC)

Oracle notes only. Not consumed by compile. Every non-obvious expected row is
justified from `source.md`.

## Source

- US Specialty Formulations, LLC - 659142 - 07/26/2023, issued by ORA's Division of
  Pharmaceutical Quality Operations I. Registered 503B outsourcing facility, Allentown, PA.
  Real public-domain FDA document, distinct company from all existing fixtures. Non-GLP-1.
- The firm initiated voluntary recalls (May 24, 2022) for lack of sterility assurance; noted
  in source.md as context (not separately modeled - no carrier for recalls).

## Registry carrier: fda_insanitary_condition/5

`(Condition, Letter, condition_N, condition_category, Src)`, mirroring `fda_violation`.
Models the numbered 501(a)(2)(A) insanitary observations, separate from 501(a)(2)(B) CGMP
`fda_violation_detail` rows. The condition values are closed registry categories, not
fixture-specific observation phrases.

## Wrapper / identity / parties

- issuing office `ora_pqo_i`: the Issuing Office is "Division of Pharmaceutical Quality
  Operations I" (Office of Regulatory Affairs) - NOT CDER/OMQ. Token is a best-guess; confirm.
- Location is modeled as `allentown_pa`, following the FDA facility-location reducer that
  removes ZIP/country suffixes from typed location atoms.
- FEI is STATED: "include FEI: 3010680515" -> identifier_value `fei_3010680515`. This fixture
  deliberately contrasts fixture 001 (no FEI -> not_stated + omission); here the identifier is
  present, so no domain_omission is emitted.
- recipient `kyle_y_flanigan` (CEO); signatory `lisa_harlan` (Program Division Director); contact
  `liatte_closs` (CAPT, Compliance Officer).

## Chronology

- inspection v_2022_03_21..v_2022_04_26: "From March 21 to April 26, 2022."
- 483 response v_2022_05_17: "your facility's response, dated May 17, 2022."

## Numbered insanitary observations (501(a)(2)(A))

Letter numbers six; three are modeled (numbering preserved):
- condition_1 `sterility_assurance`: "used non-sterile wipes within the ISO 5 aseptic processing
  area."
- condition_3 `airflow_control`: "failed to perform adequate smoke studies under dynamic
  conditions to demonstrate unidirectional airflow."
- condition_6 `microbial_contamination`: "did not perform adequate product evaluation and take
  appropriate corrective action after microbial contamination was recovered within the ISO 5
  aseptic processing area." (Observations 2, 4, 5 omitted for size.)

## CGMP violations and the observation/record_review distinction

Letter numbers eleven CGMP violations; four modeled (numbering preserved: 2, 3, 7, 8).

- Violation 2 (211.113(b)) -> `contamination_control`:
  - `aseptic_process_validation` (procedure_scope): "validation of all aseptic and sterilization processes."
- Violation 3 (211.42(c)(10)(v)) -> `contamination_control`:
  - `cleaning_disinfection_validation` (procedure_scope): "failed to establish an adequate system
    for cleaning and disinfecting the room and equipment to produce aseptic conditions."
- Violation 7 (211.42(c)(10)(iv)) -> `facility_equipment_control`:
  - `environmental_monitoring_system_inadequate` (observation_subject): "failed to establish an
    adequate system for monitoring environmental conditions." Cited as a facility/control failure.
- Violation 8 (211.192) -> `investigation_failure`:
  - `microbial_recovery_iso5` (record_review_subject): the ISO 5 microbial recovery that the firm
    failed to investigate/evaluate is the SUBJECT of the investigation failure. The SAME microbial
    recovery is also recorded as insanitary observation_6; here it is the 211.192 review subject.
    This is the row that must NOT be tagged observation_subject (forbidden file pins the swap).
  - `investigation_followup_incomplete` (response_status, role `corrective_action_evaluation`):
    the corrective-action critique tied to the 211.192 violation - re the white-fibers-in-vials
    investigation, "details regarding the investigation ... were not provided ... no preventative
    actions were provided."

## Forbidden swaps (microbial-recovery case)

- `observation_subject, microbial_recovery_iso5` - the microbial recovery is the 211.192 review
  subject, not facility-observation evidence (the requested microbial-recovery swap).
- `record_review_subject, environmental_monitoring_system_inadequate` - EM-system inadequacy is the
  observation; not a review subject.
- `record_review_subject, microbial_recovery_iso5, corrective_action_evaluation` - wrong role.
- `affected_lot/affected_product, microbial_recovery_iso5` - no real lot id is stated for the
  microbial recovery, so these are cheats (contrast fixture 001, which has a real lot).
- prose-shaped value; WL number used as identifier instead of the real FEI.

## Other rows

- `fda_adulteration_basis(..., adulteration_cgmp, fdca_501_a_2_b, drug_products, ...)`.
- `fda_consultant_recommendation(..., qualified_third_party_consultant, system_assessment, ...)`.
- response requirement: "Within fifteen (15) working days"; modeled as `electronic_submission`
  for `corrective_actions_and_documentation`.
- conclusion scope: "not intended to be an all-inclusive statement." The separate legal-action
  warning is not modeled because the live FDA registry does not admit an enforcement-warning
  conclusion carrier.

## Uncertainty about atom choice

- Category tokens `contamination_control` (211.42(c)(10)(v)) and `facility_equipment_control`
  (211.42(c)(10)(iv)); issuing-office token `ora_pqo_i`.
- `contamination_control` (211.113(b)) and `investigation_failure` (211.192) match prior fixtures.
- The fda_insanitary_condition/5 slot order now follows the live registry.
