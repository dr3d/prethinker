% candidate_expected_facts.pl
% Review: fda_response_assessment_item_oracle_review_20260604
% Predicate: fda_response_assessment_item(AssessmentId, ViolationId, CgmpCitation, AssessmentKind, AssessmentScope, SourceOrScope).
% Fixture: fda_warning_letter_domain_transfer_002 (Rechon)

% violation_1 (211.113(b)): "Your response is inadequate. Your revised procedure still allows for (b)(4) adjustments with sanitized, gloved fingertips."
fda_response_assessment_item(assessment_1, violation_1, cfr_21_211_113_b, response_inadequate, corrective_action_evaluation, src_item_1).

% violation_2 (211.192): EM/OOS investigations inadequate; "Your CAPAs ... were not robust"; "Your response is inadequate."
fda_response_assessment_item(assessment_2, violation_2, cfr_21_211_192, response_inadequate, corrective_action_evaluation, src_item_2).

% violation_3 (211.42(c)(10)(v)): decontamination not validated; sticky residue; "Your response is inadequate."
fda_response_assessment_item(assessment_3, violation_3, cfr_21_211_42_c_10_v, response_inadequate, corrective_action_evaluation, src_item_3).
