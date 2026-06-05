% candidate_forbidden_facts.pl
% Review: fda_response_assessment_item_oracle_review_20260604
% Fixture: fda_warning_letter_domain_transfer_001
% Use _ for irrelevant slots.

% General letter-level CAPA concern recast as a per-item response assessment.
% The "not yet demonstrated adequate correction" sentence is not attached to any numbered item.
fda_response_assessment_item(_, violation_2, cfr_21_211_113_b, corrective_action_inadequate, corrective_action_evaluation, _).
fda_response_assessment_item(_, violation_5, cfr_21_211_42_c_10_v, corrective_action_inadequate, corrective_action_evaluation, _).

% Third-party-consultant RECOMMENDATION recast as an assessment of the firm's response.
fda_response_assessment_item(_, _, _, corrective_action_inadequate, response_review, _).

% Out-of-domain citations for items whose CFR is not in the closed CgmpCitation domain.
fda_response_assessment_item(_, violation_1, cfr_21_211_22_d, _, _, _).
fda_response_assessment_item(_, violation_3, cfr_21_211_28_a, _, _, _).
fda_response_assessment_item(_, violation_4, cfr_21_211_42_c_10_vi, _, _, _).
fda_response_assessment_item(_, violation_6, cfr_21_211_188, _, _, _).

% Prose / firm explanation smuggled into a slot.
fda_response_assessment_item(_, _, _, _, _, 'FDA remains concerned that your firm has not yet demonstrated adequate correction.').

% Facility/WL identifier used as ViolationId.
fda_response_assessment_item(_, wl_717972, _, _, _, _).
