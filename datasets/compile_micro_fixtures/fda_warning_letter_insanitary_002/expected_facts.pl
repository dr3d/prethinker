% expected_facts.pl
% Fixture: fda_warning_letter_insanitary_002
% Source: US Specialty Formulations, LLC - 659142 - 07/26/2023 (ORA DPQO I, 503B), see source.md
% Live FDA registry shapes. fda_violation_detail/5; v_ dates; cfr_ citations.
% fda_insanitary_condition/5 = (Condition, Letter, condition_N, condition_category, Src).
% This fixture carries the microbial-recovery case for the observation-vs-record-review swap.

% --- wrapper / identity / parties ---
fda_warning_letter(Letter, ora_pqo_i, us_specialty_formulations_llc, v_2023_07_26, SrcLetter).
% FEI is stated in this letter -> a real identifier_value (contrast with the not_stated 503B letters).
fda_facility_identity(Facility, us_specialty_formulations_llc, allentown_pa, fei_3010680515, SrcFacility).
fda_correspondence_party(Ltr, PartyRcpt, recipient, kyle_y_flanigan, SrcRcpt).
fda_correspondence_party(Ltr, PartySig, signatory, lisa_harlan, SrcSig).
fda_correspondence_party(Ltr, PartyContact, contact, liatte_closs, SrcContact).

% --- chronology ---
fda_inspection_event(Inspection, FacilityRef, v_2022_03_21, v_2022_04_26, fda, SrcInsp).
fda_form483_response(Response, InspectionRef, v_2022_05_17, SrcResp).

% --- numbered insanitary observations (501(a)(2)(A)); letter numbering preserved ---
fda_insanitary_condition(Cond1, LetterRefI1, condition_1, sterility_assurance, SrcI1).
fda_insanitary_condition(Cond3, LetterRefI3, condition_3, airflow_control, SrcI3).
fda_insanitary_condition(Cond6, LetterRefI6, condition_6, microbial_contamination, SrcI6).

% --- CGMP violations (501(a)(2)(B)); letter numbering preserved (subset modeled) ---
fda_cgmp_violation_item(Bundle2, LetterBundle2, violation_2, cfr_21_211_113_b, SrcBundle2).
fda_cgmp_violation_item(Bundle3, LetterBundle3, violation_3, cfr_21_211_42_c_10_v, SrcBundle3).
fda_cgmp_violation_item(Bundle7, LetterBundle7, violation_7, cfr_21_211_42_c_10_iv, SrcBundle7).
fda_cgmp_violation_item(Bundle8, LetterBundle8, violation_8, cfr_21_211_192, SrcBundle8).
fda_violation(Viol2, LetterRef2, violation_2, contamination_control, SrcViol2).
fda_violation(Viol3, LetterRef3, violation_3, contamination_control, SrcViol3).
fda_violation(Viol7, LetterRef7, violation_7, facility_equipment_control, SrcViol7).
fda_violation(Viol8, LetterRef8, violation_8, investigation_failure, SrcViol8).

% --- citations ---
fda_violation_citation(ViolRef2, cfr_21_211_113_b, cgmps_requirement, SrcCite2).
fda_violation_citation(ViolRef3, cfr_21_211_42_c_10_v, cgmps_requirement, SrcCite3).
fda_violation_citation(ViolRef7, cfr_21_211_42_c_10_iv, cgmps_requirement, SrcCite7).
fda_violation_citation(ViolRef8, cfr_21_211_192, cgmps_requirement, SrcCite8).

% --- violation details ---
fda_violation_detail(V2a, procedure_scope, aseptic_process_validation, violation_scope, SrcD1).
fda_violation_detail(V3a, procedure_scope, cleaning_disinfection_validation, violation_scope, SrcD2).
fda_violation_detail(V7a, observation_subject, environmental_monitoring_system_inadequate, violation_scope, SrcD3).
% 211.192 investigation failure: microbial recovery is the review subject; plus a critique row.
fda_violation_detail(V8a, record_review_subject, microbial_recovery_iso5, violation_scope, SrcD4).
fda_violation_detail(V8b, response_status, investigation_followup_incomplete, corrective_action_evaluation, SrcD5).

% --- adulteration / consultant / response / conclusion ---
fda_adulteration_basis(LetterRefB, adulteration_cgmp, fdca_501_a_2_b, drug_products, SrcBasis).
fda_consultant_recommendation(LetterRefCn, qualified_third_party_consultant, system_assessment, SrcConsult).
fda_response_requirement(LetterRefR, written_response, fifteen_working_days, electronic_submission, corrective_actions_and_documentation, SrcReq).
fda_conclusion_scope(LetterRefC1, cited_violations_not_exhaustive, not_all_inclusive, SrcConcl1).
