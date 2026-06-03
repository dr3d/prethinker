% forbidden_facts.pl — fda_warning_letter_observation_transfer_001
% Cheat PATTERNS, live /5 detail shape: (Violation, detail_kind, detail_value, role, Src).

% record_review_subject used for facility/control OBSERVATION evidence:
fda_violation_detail(_, record_review_subject, environmental_monitoring_failure, _, _).

% observation_subject used for INVESTIGATION-FAILURE subjects:
fda_violation_detail(_, observation_subject, mammalian_hair_contamination, _, _).
fda_violation_detail(_, observation_subject, media_fill_termination, _, _).

% record_review_subject paired with corrective_action_evaluation (wrong role):
fda_violation_detail(_, record_review_subject, mammalian_hair_contamination, corrective_action_evaluation, _).

% affected_lot / affected_product for a generic subject with no real lot/product id:
fda_violation_detail(_, affected_lot, mammalian_hair_contamination, _, _).
fda_violation_detail(_, affected_product, environmental_monitoring_failure, _, _).

% Prose-shaped detail value:
fda_violation_detail(_, _, 'firm released batches with mammalian hair after culling units', _, _).

% Warning-letter / MARCS number used as the facility identifier:
fda_facility_identity(_, catalent_indiana_llc, bloomington_indiana, marcs_718189, _).
