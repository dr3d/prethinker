% expected_facts.pl
% Fixture: fda_warning_letter_domain_transfer_003
% Source: Liebel-Flarsheim Company LLC - 711508 - 10/17/2025 (CDER), see source.md
%
% Carrier-shape conventions (see source_notes.md for the full statement and a
% fallback if the live registry differs):
%   - Entity IDs, foreign-key ID references, and source-coordinate slots are
%     Prolog VARIABLES; content/value slots are compact non-prose ATOMS.
%   - fda_violation_detail uses the live registry's /5 shape:
%       fda_violation_detail(Violation, DetailKind, Value, Role, Src).
% Only existing fda_warning_letter_v1 carriers are used. No new predicates.
% Shared governed VALUE/ROLE atoms (environmental_monitoring_excursion,
% procedure_scope, violation_scope, corrective_action_evaluation) are reused
% deliberately so the two transfer_002 residue families line up for measurement;
% no transfer_001/002 prose or content is reused.

% --- letter wrapper ---
fda_warning_letter(Letter, cder, liebel_flarsheim_company_llc, v_2025_10_17, SrcLetter).

% --- facility identity ---
fda_facility_identity(Facility, liebel_flarsheim_company_llc, raleigh_nc, fei_1028892, SrcFacility).

% --- correspondence parties (recipient, signatory, response contact) ---
fda_correspondence_party(LetterRefP1, PartyRcpt, recipient, liebel_flarsheim_company_llc, SrcPartyRcpt).
fda_correspondence_party(LetterRefP2, PartySig, signatory, francis_godwin, SrcPartySig).
fda_correspondence_party(LetterRefP3, PartyContact, contact, bryce_hammer, SrcPartyContact).

% --- inspection event ---
fda_inspection_event(Inspection, FacilityRef, v_2025_03_25, v_2025_04_08, fda, SrcInspection).

% --- Form FDA 483 response ---
fda_form483_response(Response, InspectionRef, v_2025_04_25, SrcResponse).

% --- numbered violations ---
fda_violation(Viol1, LetterRef1, violation_1, investigation_failure, SrcViol1).
fda_violation(Viol2, LetterRef2, violation_2, facility_equipment_control, SrcViol2).

% --- CFR citations (compact references) ---
fda_violation_citation(ViolRef1, cfr_21_211_192, cgmps_requirement, SrcCite1).
fda_violation_citation(ViolRef2a, cfr_21_211_42_c, cgmps_requirement, SrcCite2).
fda_violation_citation(ViolRef2b, cfr_21_211_63, cgmps_requirement, SrcCite3).

% --- violation 1 details (211.192 investigation failure) ---
fda_violation_detail(ViolRefD1, record_review_subject, in_process_bioburden_excursion, violation_scope, SrcDet1).
fda_violation_detail(ViolRefD2, record_review_subject, oos_endotoxin_result, violation_scope, SrcDet2).
fda_violation_detail(ViolRefD3, procedure_scope, terminal_sterilization_process_validation, violation_scope, SrcDet3).
fda_violation_detail(ViolRefD5, response_status, inadequate, corrective_action_evaluation, SrcDet5).

% --- violation 2 details (211.42(c)/211.63 facility & equipment) ---
fda_violation_detail(ViolRefD6, process_area, iso_5_filling_line, violation_scope, SrcDet6).
fda_violation_detail(ViolRefD7, observation_subject, environmental_monitoring_excursion, violation_scope, SrcDet7).
fda_violation_detail(ViolRefD9, response_status, inadequate, corrective_action_evaluation, SrcDet9).

% --- adulteration basis ---
fda_adulteration_basis(LetterRefB, adulteration_cgmp, fdca_501_a_2_b, drug_products, SrcBasis).

% --- response requirements (decomposed) ---
fda_response_requirement(LetterRefR1, written_response, fifteen_working_days, electronic_submission, corrective_actions_and_documentation, SrcReq1).

% --- consultant recommendation (present in this letter) ---
fda_consultant_recommendation(LetterRefCn, qualified_cgmp_consultant, consultant_engagement, SrcConsult).
fda_violation_citation(LetterRefCn2, cfr_21_211_34, consultant_qualification, SrcConsultCite).

% --- conclusion scope ---
fda_conclusion_scope(LetterRefC1, cited_violations_not_exhaustive, not_all_inclusive, SrcConcl1).
fda_conclusion_scope(LetterRefC2, recurrence_prevention, responsibility_to_correct, SrcConcl2).

% --- omission accountability (negative control) ---
% Source states only future GDUFA eligibility for a Post-Warning Letter Meeting,
% never that a meeting occurred.
domain_omission(LetterRefO1, 'fda_regulatory_meeting/4', none_found, future_eligibility_only_no_meeting_held, SrcOmit1).
