% expected_facts.pl — state_ag_settlement_aod_transfer_002
% NY OAG Assurance of Discontinuance, In re Equinox Group, LLC / SoulCycle (Assurance No. 24-099).
% Source = OAG FINDINGS only (relief/monetary/release/reporting/signature provisions are NOT in
% the extract per provenance), so obligation/monetary/signature lanes are intentionally empty.
% Registered signatures only; compact atoms; coordinates in source_or_scope.

% --- instrument wrapper (caption) ---
% effective_date is not_stated: the FINDINGS extract states no execution/effective date for the AOD.
state_ag_instrument(aod_24_099, assurance_of_discontinuance, new_york_attorney_general, equinox_group_llc, assurance_24_099, not_stated, caption).

% --- parties: regulator + four named respondents (caption) ---
state_ag_party(aod_24_099, new_york_attorney_general, regulator, new_york_attorney_general, caption).
state_ag_party(aod_24_099, equinox_group_llc, respondent, equinox_group_llc, caption).
state_ag_party(aod_24_099, equinox_holdings_inc, respondent, equinox_holdings_inc, caption).
state_ag_party(aod_24_099, equinox_media_llc, respondent, equinox_media_llc, caption).
state_ag_party(aod_24_099, soulcycle_llc, respondent, soulcycle_llc, caption).

% --- investigation-authority citations (opening paragraph naming the authority for the investigation) ---
state_ag_authority_citation(aod_24_099, executive_law_63_12, investigation_authority, caption).
state_ag_authority_citation(aod_24_099, gbl_349, investigation_authority, caption).
state_ag_authority_citation(aod_24_099, gbl_350, investigation_authority, caption).
state_ag_authority_citation(aod_24_099, gbl_527_a, investigation_authority, caption).
state_ag_authority_citation(aod_24_099, rosca_15_usc_8403_3, investigation_authority, caption).

% --- compact dated events (exact-date events only) ---
state_ag_event(aod_24_099, event_1, conduct_period_start, v_2021_02_09, equinox, findings_para_16).
state_ag_event(aod_24_099, event_2, enrollment_disclosure_revision, v_2023_07_15, soulcycle, findings_para_59_67).
state_ag_event(aod_24_099, event_3, online_cancellation_established, v_2024_07_28, equinox, findings_para_47_54).

% --- cancellation contact channels tied to the correct brand/respondent ---
state_ag_contact_channel(aod_24_099, equinox_holdings_inc, cancellations_equinox_com, cancellation_channel, email, cancellations_equinox_com, findings_para_32).
state_ag_contact_channel(aod_24_099, soulcycle_llc, yoursoulmatters_soul_cycle_com, cancellation_channel, email, yoursoulmatters_soul_cycle_com, findings_para_58).
state_ag_contact_channel(aod_24_099, equinox_media_llc, hello_equinoxplus_com, cancellation_channel, email, hello_equinoxplus_com, findings_para_77_80).
state_ag_contact_channel(aod_24_099, equinox_media_llc, hello_equinoxmedia_com, cancellation_channel, email, hello_equinoxmedia_com, findings_para_77_80).
