% candidate_expected_facts.pl
% Review: fda_response_assessment_item_oracle_review_20260604
% Predicate: fda_response_assessment_item(AssessmentId, ViolationId, CgmpCitation, AssessmentKind, AssessmentScope, SourceOrScope).
% Fixture: fda_warning_letter_domain_transfer_001
%
% RESULT: NO EXPECTED FACTS.
% The source contains no firm-response/corrective-action assessment attached to a
% numbered CGMP item. Section D states only a general, letter-level CAPA concern
% ("FDA remains concerned that your firm has not yet demonstrated that adequate
% correction has been properly implemented") and a third-party-consultant
% recommendation. Neither attaches to a violation_N with a matching in-domain
% CGMP citation, so per the contract this carrier abstains.
