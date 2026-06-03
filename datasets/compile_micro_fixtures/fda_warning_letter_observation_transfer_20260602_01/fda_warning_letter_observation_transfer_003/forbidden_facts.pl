% forbidden_facts.pl — fda_warning_letter_observation_transfer_003
% Cheat PATTERNS, live /5 detail shape. Distinct observation vs record_review
% value atoms make these genuine cheats that never unify with an expected row.

% record_review_subject used for facility/control OBSERVATION evidence:
fda_violation_detail(_, record_review_subject, iso5_aseptic_area_microbial_contamination, _, _).

% observation_subject used for the INVESTIGATION-FAILURE subject:
fda_violation_detail(_, observation_subject, iso5_viable_air_microbial_recovery, _, _).

% record_review_subject paired with corrective_action_evaluation (wrong role):
fda_violation_detail(_, record_review_subject, iso5_viable_air_microbial_recovery, corrective_action_evaluation, _).

% affected_lot / affected_product for a generic microbial subject with no real id:
fda_violation_detail(_, affected_lot, iso5_viable_air_microbial_recovery, _, _).
fda_violation_detail(_, affected_product, iso5_aseptic_area_microbial_contamination, _, _).

% Prose-shaped detail value:
fda_violation_detail(_, _, 'failed to investigate microbial recovery in the ISO 5 BSC', _, _).

% Warning-letter number used as the facility identifier:
fda_facility_identity(_, osrx_inc, missoula_mt, wl_701889, _).
