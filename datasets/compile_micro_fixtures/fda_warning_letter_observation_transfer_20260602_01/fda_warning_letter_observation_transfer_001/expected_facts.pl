% expected_facts.pl
% Fixture: fda_warning_letter_observation_transfer_001
% Source: Catalent Indiana, LLC - 718189 - 11/20/2025 (CDER/OMQ), see source.md
% Live FDA registry shapes. Dates are v_YYYY_MM_DD atoms; citations are cfr_ atoms.
% fda_violation_detail is /5: (Violation, detail_kind, detail_value, role_or_purpose, Src).
% detail_kind in {observation_subject, record_review_subject, procedure_scope,
%   response_status, process_area, affected_lot, affected_product, missing_record_type}.
% observation_subject = observed contamination/program-result evidence of facility/control
% failure; record_review_subject = subject of a 211.192 investigation/review failure.

% --- wrapper / identity / parties ---
fda_warning_letter(Letter, office_of_manufacturing_quality, catalent_indiana_llc, v_2025_11_20, SrcLetter).
fda_facility_identity(Facility, catalent_indiana_llc, bloomington_indiana, fei_3005949964, SrcFacility).
fda_correspondence_party(Ltr, PartyRcpt, recipient, catalent_indiana_llc, SrcRcpt).
fda_correspondence_party(Ltr, PartySig, signatory, francis_godwin, SrcSig).
fda_correspondence_party(Ltr, PartyContact, contact, carrie_a_hughes, SrcContact).

% --- chronology / meeting ---
fda_inspection_event(Inspection, FacilityRef, v_2025_06_23, v_2025_07_14, fda, SrcInsp).
fda_form483_response(Response, InspectionRef, v_2025_08_04, SrcResp).
fda_regulatory_meeting(Meeting, FacilityRefM, v_2025_09_26, SrcMeeting).

% --- violations (number then category) ---
fda_violation(Viol1, LetterRef1, violation_1, investigation_failure, SrcViol1).
fda_violation(Viol2, LetterRef2, violation_2, contamination_control, SrcViol2).

% --- citations ---
fda_cgmp_violation_item(Bundle1, LetterBundle1, violation_1, cfr_21_211_192, SrcBundle1).
fda_cgmp_violation_item(Bundle2, LetterBundle2, violation_2, cfr_21_211_113_b, SrcBundle2).
fda_violation_citation(ViolRef1, cfr_21_211_192, cgmps_requirement, SrcCite1).
fda_violation_citation(ViolRef2, cfr_21_211_113_b, cgmps_requirement, SrcCite2).

% --- violation 1 details (211.192 -> record_review_subject) ---
fda_violation_detail(V1a, record_review_subject, mammalian_hair_contamination, violation_scope, SrcD1).
fda_violation_detail(V1b, record_review_subject, media_fill_termination, violation_scope, SrcD2).
fda_violation_detail(V1c, response_status, premature_capa_sunset, corrective_action_evaluation, SrcD3).
fda_violation_detail_slot(V1SlotA, record_review_subject, violation_scope, SrcDSlot1).
fda_violation_detail_slot(V1SlotB, record_review_subject, violation_scope, SrcDSlot2).
fda_violation_detail_slot(V1SlotC, response_status, corrective_action_evaluation, SrcDSlot3).
fda_response_assessment(Assessment1, violation_1, response_inadequate, corrective_action_evaluation, SrcAssessment1).

% --- violation 2 details (211.113(b) -> observation_subject + procedure_scope) ---
fda_violation_detail(V2a, observation_subject, environmental_monitoring_failure, violation_scope, SrcD4).
fda_violation_detail(V2b, procedure_scope, decontamination_process_validation, violation_scope, SrcD5).
fda_violation_detail(V2c, response_status, response_inadequate, corrective_action_evaluation, SrcD6).
fda_violation_detail_slot(V2SlotA, observation_subject, violation_scope, SrcDSlot4).
fda_violation_detail_slot(V2SlotB, procedure_scope, violation_scope, SrcDSlot5).
fda_violation_detail_slot(V2SlotC, response_status, corrective_action_evaluation, SrcDSlot6).
fda_response_assessment(Assessment2, violation_2, response_inadequate, corrective_action_evaluation, SrcAssessment2).

% --- adulteration / response / conclusion ---
fda_adulteration_basis(LetterRefB, adulteration_cgmp, fdca_501_a_2_b, drug_products, SrcBasis).
fda_response_requirement(LetterRefR, written_response, fifteen_working_days, electronic_submission, corrective_actions_and_documentation, SrcReq).
fda_conclusion_scope(LetterRefC1, cited_violations_not_exhaustive, not_all_inclusive, SrcConcl1).
