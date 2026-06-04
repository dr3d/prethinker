% candidate_expected_facts.pl
% Review: fda_response_documentation_gap_oracle_review_20260603
% Predicate: fda_response_documentation_gap(GapId, ViolationId, CgmpCitation, GapKind, Source).
% Fixture: fda_warning_letter_domain_transfer_002
% Source: Rechon Life Science AB - 701040 - 04/30/2025 (CDER), see source.md
%
% Convention:
% - Capitalized arguments are floating GapId / source-coordinate variables.
% - Lowercase arguments are governed compact atoms.
% - ViolationId atoms (violation_1..violation_4) and CGMP citation atoms are
%   taken only from the fixture's existing numbered-item map, used here solely
%   to identify already-declared IDs and citations (allowed by the work order).
%
% RESULT: NO EXPECTED FACTS.
%
% Justification (full detail in adjudication_notes.md):
% The predicate fires only when the source says, in substance, that a firm
% RESPONSE or corrective-action position lacked supporting documentation,
% protocols, records, or validation evidence for a specific numbered CGMP item.
% On this fixture every response critique is the bare phrase "Your response is
% inadequate" (items 1, 2, 3) or is absent entirely (item 4). At no point does
% FDA state that the firm failed to PROVIDE documentation, protocols, records,
% or validation evidence in its response.
%
% - Item 1 (cfr_21_211_113_b): response inadequate because the *provided* revised
%   procedure still permits the bad practice -> substantive inadequacy of a
%   submitted document, not a missing-documentation gap. do_not_emit.
% - Item 2 (cfr_21_211_192): a failure-to-investigate critique -> belongs to
%   fda_response_investigation_gap/5, not this carrier. do_not_emit.
% - Item 3 (cfr_21_211_42_c_10_v): response critique is only "inadequate"; the
%   "failed to validate" language is the underlying operational violation, not a
%   stated response documentation/validation gap. Ambiguous -> abstain.
% - Item 4 (cfr_21_211_58): no response critique at all; citation is also outside
%   this predicate's allowed value domain. do_not_emit.
%
% Per the work order this carrier is allowed to miss borderline substance and is
% not allowed to encode a prose guess, so the correct expected set here is empty.
