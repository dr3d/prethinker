% forbidden_facts.pl
% Fixture: fda_warning_letter_domain_transfer_003
%
% Cheat PATTERNS. The transfer cell is not clean if the compiler emits anything
% unifying with one of these, even while supporting all expected facts.
% Detail patterns use the live registry's /5 shape. Prose-shaped catchers use
% short synthetic fragments, not source excerpts.

% Wrong facility identifier: cross-fixture FEI leakage (this is transfer_001's FEI).
fda_facility_identity(_, liebel_flarsheim_company_llc, _, fei_3002806978, _).

% MARCS-CMS / warning-letter number used as the FEI.
fda_facility_identity(_, liebel_flarsheim_company_llc, _, fei_711508, _).

% Warning-letter reference number used as the FEI.
fda_facility_identity(_, liebel_flarsheim_company_llc, _, wl_320_26_06, _).

% Prose-shaped violation detail value instead of a compact governed atom.
fda_violation_detail(_, _, 'failed to investigate microbial excursions and OOS endotoxin results', _, _).

% Wrong signatory role: Godwin is the signatory, not the recipient.
fda_correspondence_party(_, _, recipient, francis_godwin, _).

% Wrong contact role: Hammer is the response contact, not the signatory.
fda_correspondence_party(_, _, signatory, bryce_hammer, _).

% Overbroad violation detail (whole-facility scope instead of the specific area).
fda_violation_detail(_, process_area, entire_facility, _, _).

% Wrong detail kind for violation 2: environmental-monitoring excursion is
% observed facility/control evidence here, not an investigation/review subject.
fda_violation_detail(_, record_review_subject, environmental_monitoring_excursion, violation_scope, _).

% Wrong role: the cited OOS subject belongs to violation_scope, not
% corrective_action_evaluation.
fda_violation_detail(_, record_review_subject, oos_endotoxin_result, corrective_action_evaluation, _).

% Wrong role: FDA's CAPA critique belongs to corrective_action_evaluation, not
% violation_scope.
fda_violation_detail(_, corrective_action, inadequate_root_cause_remediation, violation_scope, _).
