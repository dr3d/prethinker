% forbidden_facts.pl — fda_warning_letter_insanitary_001 (PQ Pharmacy)
% Cheat PATTERNS, live /5 detail shape: (Violation, detail_kind, detail_value, role, Src).

% record_review_subject used for facility/control OBSERVATION evidence:
fda_violation_detail(_, record_review_subject, environmental_monitoring_system_inadequate, _, _).
fda_violation_detail(_, record_review_subject, poor_aseptic_technique, _, _).

% observation_subject used for the INVESTIGATION-FAILURE subject:
fda_violation_detail(_, observation_subject, particulate_contamination_investigation, _, _).

% record_review_subject paired with corrective_action_evaluation (wrong role):
fda_violation_detail(_, record_review_subject, particulate_contamination_investigation, corrective_action_evaluation, _).

% affected_lot / affected_product for a generic subject with no real lot/product id
% (contrast: the real lot pmb032025nfg IS a legitimate expected affected_lot row):
fda_violation_detail(_, affected_lot, particulate_contamination_investigation, _, _).
fda_violation_detail(_, affected_product, environmental_monitoring_system_inadequate, _, _).

% Prose-shaped detail value:
fda_violation_detail(_, _, 'failed to expand investigations into other products using the same bulk lots', _, _).

% Warning-letter number used as the facility identifier:
fda_facility_identity(_, pq_pharmacy_llc, brooksville_fl, wl_715795, _).

% CGMP citation shifted onto the wrong numbered bundle:
fda_cgmp_violation_item(_, _, violation_1, cfr_21_211_113_b, _).
fda_cgmp_violation_item(_, _, violation_3, cfr_21_211_113_b, _).
