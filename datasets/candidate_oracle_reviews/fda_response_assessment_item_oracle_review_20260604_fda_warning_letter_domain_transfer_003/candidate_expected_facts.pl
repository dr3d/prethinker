% candidate_expected_facts.pl
% Review: fda_response_assessment_item_oracle_review_20260604
% Predicate: fda_response_assessment_item(AssessmentId, ViolationId, CgmpCitation, AssessmentKind, AssessmentScope, SourceOrScope).
% Fixture: fda_warning_letter_domain_transfer_003 (Liebel-Flarsheim)

% violation_1 (211.192): two "Your response is inadequate" statements (failed to adequately
% investigate excursions/OOS endotoxin; risk assessment minimizes patient impact). One
% response-assessment item; both statements are the same inadequacy verdict on the same item.
fda_response_assessment_item(assessment_1, violation_1, cfr_21_211_192, response_inadequate, corrective_action_evaluation, src_item_1).
