% candidate_forbidden_facts.pl
% Review: fda_response_assessment_item_oracle_review_20260604
% Fixture: fda_warning_letter_domain_transfer_003 (Liebel-Flarsheim)
% Use _ for irrelevant slots.

% violation_2 carries a genuine "Your response is inadequate" (cleanroom reconstruction
% timelines unacceptable), BUT its citation is 211.42(c) / 211.63 (bare), which are NOT in
% the closed CgmpCitation domain. The assessment is therefore unrepresentable by this carrier.
% Do not fabricate an in-domain citation for v2:
fda_response_assessment_item(_, violation_2, cfr_21_211_42_c_10_v, _, _, _).
fda_response_assessment_item(_, violation_2, cfr_21_211_42_c_10_iv, _, _, _).
fda_response_assessment_item(_, violation_2, cfr_21_211_63, _, _, _).

% Consultant recommendation (211.34) is not a numbered-CGMP-item response assessment
% and is outside the closed CgmpCitation domain.
fda_response_assessment_item(_, _, cfr_21_211_34, _, _, _).

% Recasting the underlying 211.192 violation as the response assessment.
fda_response_assessment_item(_, violation_1, cfr_21_211_192, not_investigated, _, _).

% Source quote / prose in a slot.
fda_response_assessment_item(_, _, _, _, _, 'Your response is inadequate.').

% Facility/FEI/WL identifiers used as ViolationId.
fda_response_assessment_item(_, fei_1028892, _, _, _, _).
fda_response_assessment_item(_, fda_warning_letter_320_26_06, _, _, _, _).
