% forbidden_facts.pl — fda_warning_letter_insanitary_002 (US Specialty Formulations)
% Cheat PATTERNS, live /5 detail shape. Includes the microbial-recovery
% observation-vs-record-review swap.

% record_review_subject used for facility/control OBSERVATION evidence:
fda_violation_detail(_, record_review_subject, environmental_monitoring_system_inadequate, _, _).

% observation_subject used for the INVESTIGATION-FAILURE / microbial-recovery subject:
fda_violation_detail(_, observation_subject, microbial_recovery_iso5, _, _).

% record_review_subject paired with corrective_action_evaluation (wrong role):
fda_violation_detail(_, record_review_subject, microbial_recovery_iso5, corrective_action_evaluation, _).

% affected_lot / affected_product for the generic microbial-recovery subject (no real lot id stated):
fda_violation_detail(_, affected_lot, microbial_recovery_iso5, _, _).
fda_violation_detail(_, affected_product, microbial_recovery_iso5, _, _).

% Prose-shaped detail value:
fda_violation_detail(_, _, 'did not evaluate products after microbial contamination recovered in ISO 5', _, _).

% Warning-letter number used as the facility identifier instead of the real FEI (3010680515):
fda_facility_identity(_, us_specialty_formulations_llc, allentown_pa, wl_659142, _).
