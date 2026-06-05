% forbidden_facts.pl
% Fixture: fda_warning_letter_domain_transfer_002

% Paragraph-shaped violation category instead of a governed compact atom.
fda_violation(_, _, _, paragraph_shaped_microbiological_contamination_failure, _).

% Full response instructions collapsed into one slot.
fda_response_requirement(_, written_response, _, _, full_response_instruction_blob, _).

% Rule text used as a citation value instead of a compact CFR atom.
fda_violation_citation(_, full_rule_text_for_microbiological_contamination_control, _, _).

% Source excerpt or narrative summary smuggled into a detail value.
fda_violation_detail(_, procedure_scope, operator_touched_surface_with_gloved_hand, _, _).

% Inferred signatory not present in the source.
fda_correspondence_party(_, _, signatory, jane_doe, _).

% Inferred prior warning letter; source states a prior inspection finding, not a prior warning letter.
fda_prior_warning_letter(_, rechon_life_science_ab, _, _, _).

% Inferred regulatory meeting asserted as held; source states future eligibility only.
fda_regulatory_meeting(_, _, post_warning_letter_meeting_held, _).

% Source states FDCA 501(a)(2)(B) CGMP adulteration only, not 501(a)(2)(A) insanitary adulteration.
fda_adulteration_basis(_, adulteration_insanitary_conditions, fdca_501_a_2_a, _, _).
