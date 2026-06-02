fda_warning_letter(Letter, office_of_pharmaceutical_quality_operations, northbank_sterile_solutions_llc, v_2025_06_09, SrcLetter).
fda_facility_identity(Facility, northbank_sterile_solutions_llc, newark_delaware, fei_3022334455, SrcFacility).
fda_inspection_event(Inspection, Facility, v_2025_03_10, v_2025_03_14, fda, SrcInspection).
fda_form483_response(Response, Inspection, v_2025_03_28, SrcResponse).

fda_violation(Viol1, Letter, violation_1, investigation_failure, SrcViol1).
fda_violation_citation(Viol1, cfr_21_211_192, cgmps_requirement, SrcCite1).
fda_violation_detail(Viol1, record_review_subject, environmental_monitoring_excursion, violation_scope, SrcDetail1).
fda_violation_detail(Viol1, record_review_subject, oos_endotoxin_result, violation_scope, SrcDetail2).
fda_violation_detail(Viol1, procedure_scope, terminal_sterilization_cycle_execution, violation_scope, SrcDetail3).
fda_violation_detail(Viol1, response_status, inadequate, corrective_action_evaluation, SrcDetail4).

fda_violation(Viol2, Letter, violation_2, facility_equipment_control, SrcViol2).
fda_violation_citation(Viol2, cfr_21_211_42_c, cgmps_requirement, SrcCite2).
fda_violation_detail(Viol2, process_area, iso_7_staging_area, violation_scope, SrcDetail5).

fda_adulteration_basis(Letter, adulteration_cgmp, fdca_501_a_2_b, drug_products, SrcBasis).
