% expected_facts.pl
% Fixture: fda_warning_letter_observation_transfer_002
% Source: Annovex Pharma, Inc. - 698115 - 03/05/2025 (CDER/OCQC, 503B), see source.md
% Live FDA registry shapes (see fixture 001 header for conventions).

% --- wrapper / identity / parties ---
fda_warning_letter(Letter, cder, annovex_pharma_inc, v_2025_03_05, SrcLetter).
% No FEI shown in this 503B letter: identifier_value is the atom not_stated.
fda_facility_identity(Facility, annovex_pharma_inc, lorton_va, not_stated, SrcFacility).
fda_correspondence_party(Ltr, PartyRcpt, recipient, annovex_pharma_inc, SrcRcpt).
fda_correspondence_party(Ltr, PartySig, signatory, f_gail_bormel, SrcSig).
fda_correspondence_party(Ltr, PartyContact, contact, compoundinginspections_fda_hhs_gov, SrcContact).

% --- chronology ---
fda_inspection_event(Inspection, FacilityRef, v_2024_08_26, v_2024_09_06, fda, SrcInsp).
fda_form483_response(Response, InspectionRef, v_2024_09_25, SrcResp).

% --- violations (number then category) ---
fda_violation(Viol1, LetterRef1, violation_1, contamination_control, SrcViol1).
fda_violation(Viol2, LetterRef2, violation_2, investigation_failure, SrcViol2).
fda_violation(Viol3, LetterRef3, violation_3, facility_equipment_control, SrcViol3).
fda_violation(Viol4, LetterRef4, violation_4, data_integrity, SrcViol4).

% --- 501(a)(2)(A) insanitary-condition observations (separate from CGMP violations) ---
fda_insanitary_condition(Cond1, LetterRefIC1, condition_1, media_fill_control, SrcIC1).
fda_insanitary_condition(Cond2, LetterRefIC2, condition_2, airflow_control, SrcIC2).

% --- citations ---
fda_cgmp_violation_item(Bundle1, LetterBundle1, violation_1, cfr_21_211_113_b, SrcBundle1).
fda_cgmp_violation_item(Bundle2, LetterBundle2, violation_2, cfr_21_211_192, SrcBundle2).
fda_cgmp_violation_item(Bundle3, LetterBundle3, violation_3, cfr_21_211_42_c_10_iv, SrcBundle3).
fda_cgmp_violation_item(Bundle4, LetterBundle4, violation_4, cfr_21_211_68_b, SrcBundle4).
fda_violation_citation(ViolRef1, cfr_21_211_113_b, cgmps_requirement, SrcCite1).
fda_violation_citation(ViolRef2, cfr_21_211_192, cgmps_requirement, SrcCite2).
fda_violation_citation(ViolRef3, cfr_21_211_42_c_10_iv, cgmps_requirement, SrcCite3).
fda_violation_citation(ViolRef4, cfr_21_211_68_b, cgmps_requirement, SrcCite4).

% --- violation 1 details (211.113(b) -> observation_subject + procedure_scope) ---
fda_violation_detail(V1a, procedure_scope, aseptic_process_validation, violation_scope, SrcD1).
fda_violation_detail(V1b, observation_subject, unidirectional_airflow_deficiency, violation_scope, SrcD2).
fda_violation_detail_slot(V1SlotA, procedure_scope, violation_scope, SrcDSlot1).
fda_violation_detail_slot(V1SlotB, observation_subject, violation_scope, SrcDSlot2).
fda_response_assessment(Assessment1, violation_1, documentation_not_provided, corrective_action_evaluation, SrcAssessment1).

% --- violation 2 details (211.192 -> record_review_subject) ---
fda_violation_detail(V2a, record_review_subject, media_fill_positive_growth, violation_scope, SrcD3).
fda_violation_detail(V2b, response_status, contamination_discarded_not_investigated, corrective_action_evaluation, SrcD4).
fda_violation_detail_slot(V2SlotA, record_review_subject, violation_scope, SrcDSlot3).
fda_violation_detail_slot(V2SlotB, response_status, corrective_action_evaluation, SrcDSlot4).
fda_response_assessment(Assessment2, violation_2, not_investigated, corrective_action_evaluation, SrcAssessment2).

% --- violation 3 details (211.42(c)(10)(iv) -> observation_subject) ---
fda_violation_detail(V3a, observation_subject, environmental_monitoring_system_inadequate, violation_scope, SrcD5).
fda_violation_detail_slot(V3SlotA, observation_subject, violation_scope, SrcDSlot5).

% --- violation 4 details (211.68(b) data integrity) ---
fda_violation_detail(V4a, procedure_scope, computer_access_controls, violation_scope, SrcD6).
fda_violation_detail_slot(V4SlotA, procedure_scope, violation_scope, SrcDSlot6).

% --- adulteration / consultant / response / conclusion ---
fda_adulteration_basis(LetterRefB, adulteration_cgmp, fdca_501_a_2_b, drug_products, SrcBasis).
fda_consultant_recommendation(LetterRefCn, qualified_third_party_consultant, system_assessment, SrcConsult).
fda_response_requirement(LetterRefR, written_response, fifteen_working_days, electronic_submission, corrective_actions_and_documentation, SrcReq).
fda_conclusion_scope(LetterRefC1, cited_violations_not_exhaustive, not_all_inclusive, SrcConcl1).

% --- omission accountability (negative control: no FEI shown) ---
domain_omission(FacilityRefO, 'fda_facility_identity/5', none_found, no_fei_shown_in_letter, SrcOmit).
