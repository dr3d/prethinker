% candidate_forbidden_facts.pl
% Review: fda_response_documentation_gap_oracle_review_20260603
% Predicate: fda_response_documentation_gap(GapId, ViolationId, CgmpCitation, GapKind, Source).
% Fixture: fda_warning_letter_domain_transfer_002
%
% Source-faithfulness boundaries the carrier must not cross on this fixture.
% Use _ for slots irrelevant to a given boundary. Rationale in adjudication_notes.md.

% --- 1. Response-inadequate-only mislabeled as a documentation gap ---
% Item 1's only response critique is "Your response is inadequate. Your revised
% procedure still allows..." -> substantive inadequacy of a *provided* document,
% not a statement that documentation was not provided.
fda_response_documentation_gap(_, violation_1, cfr_21_211_113_b, _, _).

% --- 2. Investigation-gap critique mislabeled as a documentation gap ---
% Item 2 (211.192) is a failure-to-investigate critique (CAPAs not robust, OOS
% investigations lacked scientific rationale). It belongs to
% fda_response_investigation_gap/5, not this carrier.
fda_response_documentation_gap(_, violation_2, cfr_21_211_192, _, _).

% --- 3. Underlying-violation language promoted into a response documentation gap ---
% Item 3's response critique is only "Your response is inadequate." The "failed to
% validate" wording is the underlying operational violation, not a stated response
% documentation/validation gap. Emitting here would encode a prose guess.
fda_response_documentation_gap(_, violation_3, cfr_21_211_42_c_10_v, _, _).

% --- 4. Documentation gap fabricated for an item with no response critique ---
% Item 4 has no "Your response is inadequate" sentence and no response critique at
% all; attaching any documentation gap is unsupported.
fda_response_documentation_gap(_, violation_4, _, _, _).

% --- 5. Documentation gap attached to the wrong citation ---
% Item 1's typed citation is cfr_21_211_113_b; pairing item 1 with another item's
% citation is a wrong-citation attachment.
fda_response_documentation_gap(_, violation_1, cfr_21_211_192, _, _).

% --- 6. Citation outside this predicate's allowed value domain ---
% cfr_21_211_58 is item 4's real citation but is NOT in the allowed CgmpCitation
% domain for fda_response_documentation_gap/5.
fda_response_documentation_gap(_, _, cfr_21_211_58, _, _).

% --- 7. Facility identifier used as a violation ID ---
fda_response_documentation_gap(_, fei_3002806978, _, _, _).

% --- 8. Recipient / firm name used as a violation ID ---
fda_response_documentation_gap(_, rechon_life_science_ab, _, _, _).

% --- 9. Warning-letter / reference identifier used as a violation ID ---
% Reference #: 320-25-68 / Warning Letter 320-25-68.
fda_response_documentation_gap(_, wl_320_25_68, _, _, _).

% --- 10. Document/SOP title placed in the closed gap_kind slot ---
% gap_kind is closed to {supporting_documentation, protocol_or_record,
% validation_evidence}.
fda_response_documentation_gap(_, _, _, sop_0870_3_0, _).

% --- 11. Investigation-gap kind placed in the gap_kind slot ---
% Conflates investigation gap with documentation gap; not an allowed gap_kind.
fda_response_documentation_gap(_, _, _, investigation_failure, _).

% --- 12. Organism name smuggled into the source/scope slot ---
fda_response_documentation_gap(_, _, _, _, moraxella_osloensis).

% --- 13. Whole source phrase smuggled into the source/scope slot ---
fda_response_documentation_gap(_, _, _, _, 'Your response is inadequate.').
