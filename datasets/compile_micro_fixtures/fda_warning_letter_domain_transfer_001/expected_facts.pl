% Expected facts for fda_warning_letter_domain_transfer_001
% Source: Apothecary Pharma, LLC warning letter, WL # 717972, 2025-12-01 (CDER).
% Convention: capitalized = ID / source-coordinate variables; lowercase = governed atoms.
% Semantic slots follow datasets/domain_profiles/fda_warning_letter_v1/ontology_registry.json.

% --- wrapper and facility ---
fda_warning_letter(Letter, cder, apothecary_pharma_llc, v_2025_12_01, SrcLetter).
fda_facility_identity(Facility, apothecary_pharma_llc, cary_nc, registered_outsourcing_facility, SrcFacility).

% --- correspondence parties ---
fda_correspondence_party(Letter, Recipient, recipient, apothecary_pharma_llc, SrcRecip).
fda_correspondence_party(Letter, Signatory, signatory, f_gail_bormel, SrcSig).

% --- chronology ---
fda_inspection_event(Inspection, Facility, v_2025_05_12, v_2025_05_15, fda, SrcInsp).
fda_form483_response(Resp483, Inspection, v_2025_06_09, SrcResp).

% --- adulteration bases ---
fda_adulteration_basis(Letter, adulteration_insanitary_conditions, fdca_501_a_2_a, drug_products, SrcBasisA).
fda_adulteration_basis(Letter, adulteration_cgmp, fdca_501_a_2_b, drug_products, SrcBasisB).

% --- numbered CGMP violations ---
fda_violation(Viol1, Letter, violation_1, quality_unit_failure, SrcViol1).
fda_violation(Viol2, Letter, violation_2, contamination_control, SrcViol2).
fda_violation(Viol3, Letter, violation_3, contamination_control, SrcViol3).
fda_violation(Viol4, Letter, violation_4, aseptic_processing, SrcViol4).
fda_violation(Viol5, Letter, violation_5, aseptic_processing, SrcViol5).
fda_violation(Viol6, Letter, violation_6, other_registered_category, SrcViol6).

% --- CFR citations ---
fda_violation_citation(Viol1, cfr_21_211_22_d, cgmps_requirement, SrcCite1).
fda_violation_citation(Viol2, cfr_21_211_113_b, cgmps_requirement, SrcCite2).
fda_violation_citation(Viol3, cfr_21_211_28_a, cgmps_requirement, SrcCite3).
fda_violation_citation(Viol4, cfr_21_211_42_c_10_vi, cgmps_requirement, SrcCite4).
fda_violation_citation(Viol5, cfr_21_211_42_c_10_v, cgmps_requirement, SrcCite5).
fda_violation_citation(Viol6, cfr_21_211_188, cgmps_requirement, SrcCite6).

% --- second-layer violation details ---
fda_violation_detail(Viol4, process_area, iso_5_aseptic_processing_area, sterile_drug_products, SrcDetail1).
fda_violation_detail(Viol2, affected_product, tirzepatide_injection_10_mg_ml, violation_scope, SrcDetail2).

% --- response and consultant ---
fda_response_requirement(Letter, written_response, fifteen_working_days, fda, corrective_actions_and_documentation, SrcReq).
fda_consultant_recommendation(Letter, qualified_third_party_consultant, system_assessment, SrcRec).

% --- conclusion scope language ---
fda_conclusion_scope(Letter, cited_violations_not_exhaustive, not_all_inclusive, SrcConcl1).
fda_conclusion_scope(Letter, recurrence_prevention, responsibility_to_correct, SrcConcl2).
