% candidate_forbidden_facts.pl
% Review: fda_response_assessment_item_oracle_review_20260604
% Fixture: fda_warning_letter_domain_transfer_002 (Rechon)
% Use _ for irrelevant slots.

% violation_4 is 211.58, which is NOT in the closed CgmpCitation domain, and v4 carries
% no response critique (only an observed peeling-paint condition). No assessment may attach.
fda_response_assessment_item(_, violation_4, cfr_21_211_58, _, _, _).
fda_response_assessment_item(_, violation_4, _, _, _, _).

% Wrong citation attachment: v2 is 211.192, not 211.113(b).
fda_response_assessment_item(_, violation_2, cfr_21_211_113_b, _, _, _).

% Recasting the underlying 211.192 violation ("failed to investigate") as the response
% assessment. The source's assessment is "Your response is inadequate" (response_inadequate),
% not the violation's own not_investigated language.
fda_response_assessment_item(_, violation_2, cfr_21_211_192, not_investigated, _, _).

% Source quote / prose smuggled into a slot.
fda_response_assessment_item(_, _, _, _, _, 'Your response is inadequate.').

% Organism / document title in a slot.
fda_response_assessment_item(_, _, _, _, _, moraxella_osloensis).

% Facility/FEI/WL identifiers used as ViolationId.
fda_response_assessment_item(_, fei_3002806978, _, _, _, _).
fda_response_assessment_item(_, fda_warning_letter_320_25_68, _, _, _, _).
