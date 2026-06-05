% expected_facts.pl
% Fixture: fda_warning_letter_domain_transfer_002
% Source: Rechon Life Science AB - 701040 - 04/30/2025 (CDER), see source.md
%
% Convention:
% - Capitalized arguments are floating IDs or source-coordinate variables.
% - Lowercase arguments are governed compact atoms.
% - Facts use only registered fda_warning_letter_v1 carriers.

% --- wrapper and facility ---
fda_warning_letter(Letter, cder, rechon_life_science_ab, v_2025_04_30, SrcLetter).
fda_facility_identity(Facility, rechon_life_science_ab, FacilityLocation, fei_3002806978, SrcFacility).

% --- correspondence parties ---
fda_correspondence_party(Letter, Recipient, recipient, rechon_life_science_ab, SrcRecipient).
fda_correspondence_party(Letter, ResponsibleOfficial, responsible_official, roland_holmqvist, SrcResponsibleOfficial).
fda_correspondence_party(Letter, Signatory, signatory, francis_godwin, SrcSignatory).
fda_correspondence_party(Letter, Contact, contact, erika_v_butler, SrcContact).

% --- chronology ---
fda_inspection_event(Inspection, Facility, v_2024_08_26, v_2024_09_06, fda, SrcInspection).
fda_form483_response(Response483, Inspection, v_2024_09_27, SrcResponse483).

% --- numbered CGMP violations ---
fda_violation(Viol1, Letter, violation_1, contamination_control, SrcViol1).
fda_violation(Viol2, Letter, violation_2, investigation_failure, SrcViol2).
fda_violation(Viol3, Letter, violation_3, aseptic_processing, SrcViol3).
fda_violation(Viol4, Letter, violation_4, facility_equipment_control, SrcViol4).

% --- CFR citations ---
fda_violation_citation(Viol1, cfr_21_211_113_b, cgmps_requirement, SrcCite1).
fda_violation_citation(Viol2, cfr_21_211_192, cgmps_requirement, SrcCite2).
fda_violation_citation(Viol3, cfr_21_211_42_c_10_v, cgmps_requirement, SrcCite3).
fda_violation_citation(Viol4, cfr_21_211_58, cgmps_requirement, SrcCite4).

% --- atomic violation details ---
fda_violation_detail(Viol1, procedure_scope, sop_0870_3_0, violation_scope, SrcDetail1).
fda_violation_detail(Viol1, response_status, inadequate, ResponseRole1, SrcDetail2).
fda_violation_detail(Viol2, record_review_subject, environmental_monitoring_excursion, violation_scope, SrcDetail3).
fda_violation_detail(Viol2, response_status, inadequate, ResponseRole2, SrcDetail4).
fda_violation_detail(violation_2, record_review_subject, out_of_specification_assay, violation_scope, direct).
fda_violation_detail(Viol3, procedure_scope, decontamination_effectiveness_validation, violation_scope, SrcDetail5).
fda_violation_detail(Viol4, process_area, iso_7, violation_scope, SrcDetail6).
fda_violation_detail(violation_4, observation_subject, peeling_paint_ceiling, violation_scope, direct).

% --- adulteration basis ---
fda_adulteration_basis(Letter, adulteration_cgmp, fdca_501_a_2_b, drug_products, SrcBasis).

% --- response requirements ---
fda_response_requirement(Letter, written_response, fifteen_working_days, electronic_submission, corrective_actions_and_documentation, SrcReq1).

% --- conclusion scope ---
fda_conclusion_scope(Letter, cited_violations_not_exhaustive, not_all_inclusive, SrcConcl1).
fda_conclusion_scope(Letter, recurrence_prevention, responsibility_to_correct, SrcConcl2).

% --- omission accountability ---
domain_omission(Letter, 'fda_regulatory_meeting/4', none_found, future_eligibility_only_no_meeting_held, SrcOmit1).
