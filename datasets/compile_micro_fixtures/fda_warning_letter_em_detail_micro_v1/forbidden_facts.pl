% Wrong role: investigation subjects are violation-scope details, not CAPA
% critique rows.
fda_violation_detail(_, record_review_subject, environmental_monitoring_excursion, corrective_action_evaluation, _).
fda_violation_detail(_, record_review_subject, oos_endotoxin_result, corrective_action_evaluation, _).

% Wrong detail kind: environmental-monitoring and OOS investigation subjects
% should not be encoded as affected product/lot details.
fda_violation_detail(_, affected_product, environmental_monitoring_excursion, _, _).
fda_violation_detail(_, affected_lot, environmental_monitoring_excursion, _, _).
fda_violation_detail(_, affected_product, oos_endotoxin_result, _, _).
fda_violation_detail(_, affected_lot, oos_endotoxin_result, _, _).

% Prose-shaped detail values.
fda_violation_detail(_, _, 'failed to thoroughly investigate environmental monitoring excursion results', _, _).
