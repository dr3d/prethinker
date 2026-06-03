% forbidden_facts.pl — fda_warning_letter_observation_transfer_002
% Cheat PATTERNS, live /5 detail shape.

% record_review_subject used for facility/control OBSERVATION evidence:
fda_violation_detail(_, record_review_subject, unidirectional_airflow_deficiency, _, _).
fda_violation_detail(_, record_review_subject, environmental_monitoring_system_inadequate, _, _).

% observation_subject used for an INVESTIGATION-FAILURE subject:
fda_violation_detail(_, observation_subject, media_fill_positive_growth, _, _).

% record_review_subject paired with corrective_action_evaluation (wrong role):
fda_violation_detail(_, record_review_subject, media_fill_positive_growth, corrective_action_evaluation, _).

% affected_lot / affected_product for a generic microbial subject with no real id:
fda_violation_detail(_, affected_lot, media_fill_positive_growth, _, _).
fda_violation_detail(_, affected_product, media_fill_positive_growth, _, _).

% Prose-shaped detail value:
fda_violation_detail(_, _, 'distributed sterile products despite positive growth in media fill', _, _).

% Warning-letter number used as the facility identifier:
fda_facility_identity(_, annovex_pharma_inc, lorton_va, wl_698115, _).
