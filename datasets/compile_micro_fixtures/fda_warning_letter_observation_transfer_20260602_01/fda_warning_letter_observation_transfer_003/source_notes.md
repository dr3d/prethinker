# source_notes.md — fda_warning_letter_observation_transfer_003

Oracle notes only. Not consumed by compile. Every non-obvious expected row is
justified from `source.md`.

## Source

- OSRX, Inc. - 701889 - 04/23/2025, CDER (Office of Compounding Quality and Compliance).
  Registered 503B outsourcing facility, Missoula, MT, compounding sterile ophthalmic
  solutions. Real public-domain FDA document, distinct company from all other fixtures.
- Format note: the numbered CGMP violations are listed compactly; the supporting evidence is
  in the "Adulterated Drug Products" (insanitary) and "Corrective Actions" sections. Each
  detail row is mapped to the numbered violation it evidences and is grounded in those sections.
- Schema note: the numbered examples under "Adulterated Drug Products" are also expected as
  `fda_insanitary_condition/5` rows, because they are source-stated 501(a)(2)(A) insanitary
  observations distinct from the later CGMP violation list. This is not a substitute for the
  CGMP violation rows.

## Why this is the cleanest contrast in the batch

The same class of evidence - microbial recovery in the ISO 5 area - appears in two roles:
- as an OBSERVED facility/control failure under the EM-system violation (V3), and
- as the SUBJECT of a failure-to-investigate under 211.192 (V2).
Distinct value atoms are used (`iso5_aseptic_area_microbial_contamination` for the observation,
`iso5_viable_air_microbial_recovery` for the uninvestigated review subject) so the forbidden
swaps are real cheats that cannot unify with an expected row.

## Wrapper / identity / parties

- issuing office `cder`: "Issuing Office: Center for Drug Evaluation and Research (CDER)."
- No FEI shown: identifier_value is the atom `not_stated` (live registry requires not_stated,
  not an unbound variable). Also recorded as
  `domain_omission(Facility, 'fda_facility_identity/5', none_found, no_fei_shown_in_letter, Src)`;
  the WL number used as an identifier is pinned in forbidden facts.
- recipient `osrx_inc`: the recipient block names "OSRX, Inc."; "Dear Ms. Frost" is salutation
  context, not the expected organization-recipient row. signatory `f_gail_bormel`; response
  contact `compoundinginspections_fda_hhs_gov` because replies are directed to
  compoundinginspections@fda.hhs.gov, with no named person.

## Chronology

- inspection `2024-10-16`..`2024-10-25`: "From October 16, 2024, to October 25, 2024, an FDA
  investigator inspected your facility."
- 483 response `2024-11-15`: "receipt of your facility's response, dated November 15, 2024."
  (The original 483 issued Oct 25, 2024 and an amended 483 issued Nov 4, 2024; the firm response
  date is used for fda_form483_response.)

## Violations and the observation/record_review distinction

- Insanitary-condition observations:
  - `condition_1, airflow_control`: source-stated numbered observation about inadequate dynamic
    smoke studies to demonstrate unidirectional airflow within the ISO 5 classified critical area.
  - `condition_2, microbial_contamination`: source-stated numbered observation about microbial
    contamination recovered within the ISO 5 aseptic processing area.

- Violation 1 (211.113(b)) -> `contamination_control`, facility/control + validation:
  - `aseptic_process_validation` (procedure_scope): "failure to simulate the worst-case
    scenarios ... during Aseptic Simulation Process (APS)" and "failure to incubate all integral
    media fill units."
  - `smoke_study_airflow_validation` (procedure_scope): "failed to perform adequate smoke studies
    under dynamic conditions to demonstrate unidirectional airflow within the ISO 5 ... area."

- Violation 2 (211.192) -> `investigation_failure`, record_review:
  - `iso5_viable_air_microbial_recovery` (record_review_subject): "your investigations did not
    include environmental trending reports ... when microorganisms were recovered inside the ISO 5
    BSC from active viable air sampling plates." The recovery is the SUBJECT of the investigation
    failure. Must NOT be tagged observation_subject.
  - `microbial_recovery_not_investigated` with role `corrective_action_evaluation`: FDA's critique
    that "your response failed to ensure a thorough investigation is performed for any microbial
    recovery in the ISO 5 environment." Evaluates the firm's response, hence the role.

- Violation 3 (211.42(c)(10)(iv)) -> `facility_equipment_control`, facility/control:
  - `iso5_aseptic_area_microbial_contamination` (observation_subject): "microbial contamination
    was recovered within the ISO 5 aseptic processing area." Cited as observed evidence that the
    environmental-monitoring/control system failed. Must NOT be tagged record_review_subject.
  - `viable_air_action_limit_inadequate` (observation_subject): "you failed to implement an
    interim corrective action to address the reclassification of the action limit ... for the ISO 5
    classified areas." Observed control inadequacy.

- Violation 4 (211.110(a)) -> `process_validation`:
  - `in_process_control_validation` (procedure_scope): "failed to establish and follow adequate
    control procedures to monitor the output and to validate the performance of those manufacturing
    processes that may be responsible for causing variability."

## Other rows

- `fda_adulteration_basis(..., '21 USC 351(a)(2)(B)', cgmp_nonconformance, ...)`.
- `fda_consultant_recommendation(..., qualified_third_party_consultant, system_assessment, ...)`: "A third party consultant
  with relevant sterile drug manufacturing expertise should assist you."
- response requirements: "Within fifteen (15) working days"; correspondence referencing WL # 701889
  to compoundinginspections@fda.hhs.gov.
- conclusion scope: "not intended to be an all-inclusive statement"; firm responsibility;
  "legal action ... seizure and injunction."

## Uncertainty about atom choice

- Category tokens `facility_equipment_control` (V3, 211.42(c)(10)(iv)) and `process_validation`
  (V4, 211.110(a)) are best-guesses; confirm against the registry. `contamination_control` (V1)
  and `investigation_failure` (V2) match prior fixtures.
- inspection `type` token `drug_cgmp` used for the 503B inspection for consistency.
- The cross-fixture detail-kind/role tokens are fixed by the worksheet; the value atoms are
  compact best-guesses to confirm against the registry value domains.

## Live registry shapes applied

- `fda_violation_detail/5` (no detail id). CAPA/response critiques use detail_kind `response_status`
  (with role `corrective_action_evaluation`), since `corrective_action` is not an allowed detail_kind.
- `fda_correspondence_party(Letter, Party, contact, name, Src)` — role `contact`, not response_contact.
- `fda_violation(Violation, Letter, violation_N, category, Src)` — number then category.
- `fda_violation_citation(Violation, cfr_atom, cgmps_requirement, Src)` — `cfr_` citation atoms with the live citation role.
- `v_`-atom dates throughout; `not_stated` for the absent FEI; `domain_omission` carries the
  registered signature string `'fda_facility_identity/5'`.
