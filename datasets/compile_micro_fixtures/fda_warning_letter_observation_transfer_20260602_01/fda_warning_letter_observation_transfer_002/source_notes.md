# source_notes.md — fda_warning_letter_observation_transfer_002

Oracle notes only. Not consumed by compile. Every non-obvious expected row is
justified from `source.md`.

## Source

- Annovex Pharma, Inc. - 698115 - 03/05/2025, CDER (Office of Compounding Quality and
  Compliance). Registered 503B outsourcing facility, Lorton, VA. Real public-domain FDA
  document, distinct company from all other fixtures.
- Format note: this 503B letter lists the numbered CGMP violations compactly and presents
  the supporting evidence in the "Adulterated Drug Products" (insanitary) and "Corrective
  Actions" sections. Each detail row below is mapped to the numbered CGMP violation it
  evidences and is quoted from those sections.
- Schema note: the numbered examples under "Adulterated Drug Products" are also expected as
  `fda_insanitary_condition/5` rows, because they are source-stated 501(a)(2)(A) insanitary
  observations distinct from the later CGMP violation list. This is not a substitute for the
  CGMP violation rows.

## Wrapper / identity / parties

- issuing office `cder`: "Issuing Office: Center for Drug Evaluation and Research (CDER)."
- No FEI shown: identifier_value is the atom `not_stated` (live registry requires not_stated,
  not an unbound variable). The absence is also recorded as
  `domain_omission(Facility, 'fda_facility_identity/5', none_found, no_fei_shown_in_letter, Src)`.
  The compiler must not invent an FEI; the forbidden file pins the WL number used as an identifier.
- recipient `annovex_pharma_inc` under the correspondence-party contract's firm/entity
  preference; `adedayo_akinbi` is a source-stated responsible official. signatory
  `f_gail_bormel`; response contact `compoundinginspections_fda_hhs_gov` because the
  letter directs replies to compoundinginspections@fda.hhs.gov with no named individual.

## Chronology

- inspection `2024-08-26`..`2024-09-06`: "From August 26, 2024, to September 6, 2024, FDA
  investigators inspected your facility."
- 483 response `2024-09-25`: first of the firm's responses ("dated September 25, 2024,
  October 24, 2024, November 27, 2024, and December 27, 2024"); earliest used.

## Violations and the observation/record_review distinction

- Insanitary-condition observations:
  - `condition_1, media_fill_control`: source-stated numbered observation about media fills not
    being performed under the most challenging/stressful conditions and positive growth in filled
    units.
  - `condition_2, airflow_control`: source-stated numbered observation about inadequate dynamic
    smoke studies to demonstrate unidirectional airflow in the ISO 5 area.

- Violation 1 (211.113(b)) -> `contamination_control`, facility/control + validation:
  - `aseptic_process_validation` (procedure_scope): "media fills were not performed under the
    most challenging or stressful conditions" and "you did not incubate all units ... no
    evidence ... your aseptic processing operation is validated." A validation-scope deficiency.
  - `unidirectional_airflow_deficiency` (observation_subject): "failed to perform adequate
    smoke studies under dynamic conditions to demonstrate unidirectional airflow within the
    ISO 5 area ... may not provide adequate protection against the risk of contamination."
    Cited as observed evidence that the environmental/aseptic control is deficient -> observation.

- Violation 2 (211.192) -> `investigation_failure`, record_review:
  - `media_fill_positive_growth` (record_review_subject): "despite positive growth being
    identified in 10% of filled units during your January 2024 media fill. Your firm failed to
    investigate the positive growth." The positive growth is the SUBJECT of the investigation
    failure. This is the row that must NOT be tagged observation_subject.
  - `contamination_discarded_not_investigated` with role `corrective_action_evaluation`: FDA's
    critique - "Any contaminated unit should be considered objectionable and investigated" and
    "you ... discarded all units that showed signs of microbial contamination." Evaluates the
    firm's handling/CAPA, hence the role.

- Violation 3 (211.42(c)(10)(iv)) -> `facility_equipment_control`, facility/control:
  - `environmental_monitoring_system_inadequate` (observation_subject): "failed to establish an
    adequate system for monitoring environmental conditions in aseptic processing areas." The EM
    system inadequacy is cited as a control failure -> observation.

- Violation 4 (211.68(b)) -> `data_integrity`:
  - `computer_access_controls` (procedure_scope): "failed to exercise appropriate controls over
    computer or related systems to assure that only authorized personnel institute changes."

The contrast: airflow deficiency (V1) and EM-system inadequacy (V3) are `observation_subject`;
media-fill positive growth (V2) is `record_review_subject`. Forbidden facts pin the swaps and
the wrong-role and affected_lot/affected_product cheats.

## Other rows

- `fda_adulteration_basis(..., '21 USC 351(a)(2)(B)', cgmp_nonconformance, ...)`.
- `fda_consultant_recommendation(..., qualified_third_party_consultant, system_assessment, ...)`: "A third party
  consultant with relevant sterile drug manufacturing expertise should assist you."
- response requirements: "Within fifteen (15) working days"; reply to
  compoundinginspections@fda.hhs.gov referencing WL # 698115.
- conclusion scope: "not intended to be an all-inclusive statement"; firm responsibility;
  "legal action ... seizure and injunction."

## Uncertainty about atom choice

- Category tokens `facility_equipment_control` (V3, 211.42(c)(10)(iv)) and `data_integrity`
  (V4, 211.68(b)) are best-guesses; confirm against the registry (alternatives:
  `facility_equipment_design`, `computer_controls`). `contamination_control` (V1) and
  `investigation_failure` (V2) match prior fixtures.
- inspection `type` token `drug_cgmp` used for a 503B inspection for consistency; substitute a
  503B-specific token if the registry distinguishes.
- The cross-fixture detail-kind/role tokens (`observation_subject`, `record_review_subject`,
  `procedure_scope`, `corrective_action`, `violation_scope`, `corrective_action_evaluation`)
  are fixed by the worksheet; the value atoms are compact best-guesses to confirm.

## Live registry shapes applied

- `fda_violation_detail/5` (no detail id). CAPA/response critiques use detail_kind `response_status`
  (with role `corrective_action_evaluation`), since `corrective_action` is not an allowed detail_kind.
- `fda_correspondence_party(Letter, Party, contact, name, Src)` — role `contact`, not response_contact.
- `fda_violation(Violation, Letter, violation_N, category, Src)` — number then category.
- `fda_violation_citation(Violation, cfr_atom, cgmps_requirement, Src)` — `cfr_` citation atoms with the live citation role.
- `v_`-atom dates throughout; `not_stated` for the absent FEI; `domain_omission` carries the
  registered signature string `'fda_facility_identity/5'`.
