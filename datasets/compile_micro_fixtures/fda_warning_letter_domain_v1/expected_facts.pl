fda_warning_letter(Letter, office_of_pharmaceutical_quality_operations, marigold_sterile_products_inc, v_2025_05_14, SrcLetter).
fda_facility_identity(Facility, marigold_sterile_products_inc, camden_new_jersey, fei_3012345678, SrcFacility).
fda_correspondence_party(Letter, Recipient, recipient, marigold_sterile_products_inc, SrcRecipient).

fda_inspection_event(Inspection, Facility, v_2025_02_03, v_2025_02_07, fda, SrcInspection).
fda_form483_response(Response, Inspection, v_2025_02_21, SrcResponse).
fda_prior_warning_letter(PriorLetter, Recipient, v_2022_08_12, prior_letter, SrcPriorLetter).
fda_regulatory_meeting(Meeting, Recipient, v_2025_04_03, SrcMeeting).

fda_violation(Violation1, Letter, violation_1, quality_unit_failure, SrcViolation1).
fda_violation_citation(Violation1, cfr_21_211_192, cgmps_requirement, SrcViolation1Citation).
fda_violation_detail(Violation1, affected_lot, lot_a_104, product_release_record_review, SrcLotA104).
fda_violation_detail(Violation1, affected_lot, lot_a_105, product_release_record_review, SrcLotA105).
fda_violation_detail(Violation1, missing_record_type, batch_production_records, pre_release_quality_review, SrcRecords).

fda_violation(Violation2, Letter, violation_2, contamination_control, SrcViolation2).
fda_violation_citation(Violation2, cfr_21_211_113_b, cgmps_requirement, SrcViolation2Citation).
fda_violation_detail(Violation2, procedure_scope, microbiological_contamination_prevention, sterile_drug_products, SrcSterileProcedure).

fda_adulteration_basis(Letter, adulteration_cgmp, fdca_501_a_2_b, drug_products, SrcAdulteration).
fda_response_requirement(Letter, written_response, fifteen_working_days, fda, corrective_actions_and_documentation, SrcResponseRequirement).
fda_response_requirement(Letter, documentation_submission, fifteen_working_days, fda, supporting_documentation, SrcDocumentationRequirement).
fda_consultant_recommendation(Letter, qualified_cgmp_consultant, consultant_engagement, SrcConsultant).
fda_violation_citation(Letter, cfr_21_211_34, consultant_qualification, SrcConsultantCitation).
fda_conclusion_scope(Letter, cited_violations_not_exhaustive, not_all_inclusive, SrcScope).
fda_conclusion_scope(Letter, repeat_observation_context, prevent_recurrence, SrcRecurrence).

domain_omission(Letter, 'fda_correspondence_party/5', role_missing, signatory_not_stated, SrcSignatoryOmission).
