% expected_facts.pl
% Fixture: fda_warning_letter_insanitary_001
% Source: PQ Pharmacy, LLC - 715795 - 10/10/2025 (CDER/OCQC, 503B), see source.md
% Live FDA registry shapes. Dates v_YYYY_MM_DD; citations cfr_ atoms.
% fda_violation_detail/5: (Violation, detail_kind, detail_value, role_or_purpose, Src).
%
% fda_insanitary_condition/5 =
%   (Condition, Letter, condition_N, condition_category, Src), mirroring fda_violation.
%   Captures the numbered 501(a)(2)(A) "Adulterated Drug Products / insanitary
%   conditions" observations, kept distinct from 501(a)(2)(B) CGMP violation details.

% --- wrapper / identity / parties ---
fda_warning_letter(Letter, cder, pq_pharmacy_llc, v_2025_10_10, SrcLetter).
% 503B letter shows no FEI -> identifier_value is not_stated (see omission).
fda_facility_identity(Facility, pq_pharmacy_llc, brooksville_fl, not_stated, SrcFacility).
fda_correspondence_party(Ltr, PartyRcpt, recipient, hale_n_dimetry, SrcRcpt).
fda_correspondence_party(Ltr, PartySig, signatory, f_gail_bormel, SrcSig).
fda_correspondence_party(Ltr, PartyContact, contact, compounding_inspections_office, SrcContact).

% --- chronology ---
fda_inspection_event(Inspection, FacilityRef, v_2025_03_25, v_2025_04_04, fda, SrcInsp).
fda_form483_response(Response, InspectionRef, v_2025_04_07, SrcResp).

% --- numbered insanitary observations (501(a)(2)(A)) ---
fda_insanitary_condition(Cond1, LetterRefI1, condition_1, sterility_assurance, SrcI1).
fda_insanitary_condition(Cond2, LetterRefI2, condition_2, airflow_control, SrcI2).
fda_insanitary_condition(Cond3, LetterRefI3, condition_3, airflow_control, SrcI3).

% --- CGMP violations (501(a)(2)(B)); letter numbering preserved ---
fda_cgmp_violation_item(Bundle1, LetterBundle1, violation_1, cfr_21_211_100_a, SrcBundle1).
fda_cgmp_violation_item(Bundle2, LetterBundle2, violation_2, cfr_21_211_113_b, SrcBundle2).
fda_cgmp_violation_item(Bundle3, LetterBundle3, violation_3, cfr_21_211_42_c_10_iv, SrcBundle3).
fda_cgmp_violation_item(Bundle4, LetterBundle4, violation_4, cfr_21_211_192, SrcBundle4).
fda_violation(Viol1, LetterRef1, violation_1, process_validation, SrcViol1).
fda_violation(Viol2, LetterRef2, violation_2, contamination_control, SrcViol2).
fda_violation(Viol3, LetterRef3, violation_3, facility_equipment_control, SrcViol3).
fda_violation(Viol4, LetterRef4, violation_4, investigation_failure, SrcViol4).

% --- citations ---
fda_violation_citation(ViolRef1, cfr_21_211_100_a, cgmps_requirement, SrcCite1).
fda_violation_citation(ViolRef2, cfr_21_211_113_b, cgmps_requirement, SrcCite2).
fda_violation_citation(ViolRef3, cfr_21_211_42_c_10_iv, cgmps_requirement, SrcCite3).
fda_violation_citation(ViolRef4, cfr_21_211_192, cgmps_requirement, SrcCite4).

% --- violation 2 details (211.113(b): observation + procedure_scope) ---
fda_violation_detail(V2a, observation_subject, poor_aseptic_technique, violation_scope, SrcD1).
fda_violation_detail(V2b, procedure_scope, aseptic_process_validation, violation_scope, SrcD2).

% --- violation 3 details (211.42(c)(10)(iv) EM system: observation) ---
fda_violation_detail(V3a, observation_subject, environmental_monitoring_system_inadequate, violation_scope, SrcD3).

% --- violation 4 details (211.192 investigation failure: record_review + critique + real lot) ---
fda_violation_detail(V4a, record_review_subject, particulate_contamination_investigation, violation_scope, SrcD4).
fda_violation_detail(V4b, response_status, investigation_scope_not_expanded, corrective_action_evaluation, SrcD5).
fda_violation_detail(V4c, affected_lot, pmb032025nfg, violation_scope, SrcD6).

% --- adulteration / consultant / response / conclusion ---
fda_adulteration_basis(LetterRefB, adulteration_cgmp, fdca_501_a_2_b, drug_products, SrcBasis).
fda_consultant_recommendation(LetterRefCn, qualified_third_party_consultant, system_assessment, SrcConsult).
fda_response_requirement(LetterRefR, written_response, fifteen_working_days, electronic_submission, corrective_actions_and_documentation, SrcReq).
fda_conclusion_scope(LetterRefC1, cited_violations_not_exhaustive, not_all_inclusive, SrcConcl1).

% --- omission accountability (negative control: no FEI shown) ---
domain_omission(FacilityRefO, 'fda_facility_identity/5', none_found, no_fei_shown_in_letter, SrcOmit).
