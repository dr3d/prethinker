# source_notes.md — fda_warning_letter_insanitary_001 (PQ Pharmacy, LLC)

Oracle notes only. Not consumed by compile. Every non-obvious expected row is
justified from `source.md`.

## Source

- PQ Pharmacy, LLC - 715795 - 10/10/2025, CDER (Office of Compounding Quality and
  Compliance). Registered 503B outsourcing facility, Brooksville, FL. Real public-domain
  FDA document, distinct company from all existing fixtures.
- CAUTION for fixture selection: PQ Pharmacy compounds GLP-1 products (a "Semaglutide 5mg
  vials" lot appears in the disposition table). If the GLP-1 compounder previously set aside
  must be avoided by product class (not just by company identity), swap this fixture; the
  letter's CGMP/insanitary content is about aseptic processing generally, not GLP-1-specific.

## Registry carrier: fda_insanitary_condition/5

Written as `(Condition, Letter, condition_N, condition_category, Src)`, mirroring
`fda_violation(Violation, Letter, violation_N, category, Src)`. The numbered 501(a)(2)(A)
"Adulterated Drug Products" observations are modeled here, kept separate from 501(a)(2)(B)
CGMP `fda_violation_detail` rows. The condition values are closed registry categories, not
fixture-specific observation phrases.

## Wrapper / identity / parties

- issuing office `cder` (Office of Compounding Quality and Compliance is within CDER).
- Location is modeled as `brooksville_fl`, following the FDA facility-location reducer that
  removes ZIP/country suffixes from typed location atoms.
- No FEI shown anywhere; identifier_value is `not_stated`, also recorded as
  `domain_omission(Facility, 'fda_facility_identity/5', none_found, no_fei_shown_in_letter, Src)`.
- recipient `hale_n_dimetry` (President); signatory `f_gail_bormel`; contact
  `compounding_inspections_office` (replies to compoundinginspections@fda.hhs.gov, no named person).

## Chronology

- inspection v_2025_03_25..v_2025_04_04: "From March 25, 2025, to April 4, 2025."
- 483 response v_2025_04_07: "your facility's response, dated April 7, 2025."

## Numbered insanitary observations (501(a)(2)(A))

- condition_1 `sterility_assurance`: "An operator rested their arms on the work surface of the
  hood during aseptic production."
- condition_2 `airflow_control`: "the movement of 'first air' in the ISO 5 area was disrupted
  by operator manipulations."
- condition_3 `airflow_control`: "failed to perform adequate smoke studies under dynamic
  conditions to demonstrate unidirectional airflow."

## CGMP violations and the observation/record_review distinction

The letter numbers four CGMP violations (211.100(a), 211.113(b), 211.42(c)(10)(iv), 211.192).
For size, 211.100(a) (violation_1) is not modeled; the kept rows preserve the letter's
numbering (violation_2/3/4).

- Violation 2 (211.113(b)) -> `contamination_control`:
  - `poor_aseptic_technique` (observation_subject): observed aseptic-practice failures cited as
    contamination-control evidence (the insanitary practices feed this violation).
  - `aseptic_process_validation` (procedure_scope): "validation of all aseptic and sterilization processes."
- Violation 3 (211.42(c)(10)(iv)) -> `facility_equipment_control`:
  - `environmental_monitoring_system_inadequate` (observation_subject): "failed to establish an
    adequate system for monitoring environmental conditions." Cited as a control failure.
- Violation 4 (211.192) -> `investigation_failure`:
  - `particulate_contamination_investigation` (record_review_subject): the deficient investigations
    into particulate contamination (DEV2024072 bulk bag, DEV2024075 syringes) are the SUBJECT of
    the investigation failure.
  - `investigation_scope_not_expanded` (response_status, role `corrective_action_evaluation`):
    the corrective-action critique that CLEARLY belongs to the 211.192 violation - "you failed to
    expand your investigations into other products using the same lots ... the deviation report
    does not include a list of the specific lots assessed."
  - `pmb032025nfg` (affected_lot): a REAL lot id stated in the disposition table
    (Lot PMB032025NFG, produced 3/26/2025). This is the legitimate affected_lot case; the
    forbidden file pins affected_lot used for a generic subject lacking a real lot id.

## Other rows

- `fda_adulteration_basis(..., adulteration_cgmp, fdca_501_a_2_b, drug_products, ...)`.
- `fda_consultant_recommendation(..., qualified_third_party_consultant, system_assessment, ...)`.
- response requirement: "Within fifteen (15) working days"; modeled as `electronic_submission`
  for `corrective_actions_and_documentation`.
- conclusion scope: "not intended to be an all-inclusive statement." The separate legal-action
  warning is not modeled because the live FDA registry does not admit an enforcement-warning
  conclusion carrier.

## Forbidden swaps

Observation-vs-record-review swaps on this letter's real subjects: EM-system and aseptic-technique
(observation) must not be tagged record_review; the particulate investigation (record_review) must
not be tagged observation; wrong-role and generic affected_lot cheats; prose value; WL number as
identifier. The microbial-recovery swap case is carried by fixture 002 (US Specialty Formulations).
