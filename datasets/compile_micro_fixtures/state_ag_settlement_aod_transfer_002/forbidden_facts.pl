% forbidden_facts.pl — state_ag_settlement_aod_transfer_002
% Negative controls using the same registered signatures. Each must NOT be emitted.

% [instrument lane / independence] AOD effective date is NOT stated in the FINDINGS extract;
% v_2025_05_19 appears only in packet metadata, not in source.md. Must not be authored as the date.
state_ag_instrument(aod_24_099, assurance_of_discontinuance, new_york_attorney_general, equinox_group_llc, assurance_24_099, v_2025_05_19, caption).

% [wrong/added party] Blink Fitness is a subsidiary mentioned in background (para 15); it is NOT a
% named Respondent in the caption.
state_ag_party(aod_24_099, blink_fitness, respondent, blink_fitness, findings_para_15).

% [wrong party-role] SoulCycle LLC is a Respondent, not the regulator.
state_ag_party(aod_24_099, soulcycle_llc, regulator, soulcycle_llc, caption).

% [prose-shaped party] full caption roster collapsed into one party_name blob.
state_ag_party(aod_24_099, respondents, respondent, equinox_group_equinox_holdings_equinox_media_and_soulcycle_collectively_respondents, caption).

% [wrong authority-role/attachment] GBL 624(2) (the three-day cancellation right, a material term in
% paras 22/58) is not part of the stated investigation-authority list.
state_ag_authority_citation(aod_24_099, gbl_624_2, investigation_authority, caption).

% [prose-shaped authority] statutory definition text smuggled into the citation slot.
state_ag_authority_citation(aod_24_099, clear_and_conspicuous_means_in_larger_type_than_the_surrounding_text, governing_law, findings_para_4).

% [wrong contact-channel attachment] cancellations@equinox.com is the Equinox channel, not SoulCycle's.
state_ag_contact_channel(aod_24_099, soulcycle_llc, cancellations_equinox_com, cancellation_channel, email, cancellations_equinox_com, findings_para_32).

% [wrong contact-channel attachment] yoursoulmatters@soul-cycle.com is SoulCycle's, not Equinox's.
state_ag_contact_channel(aod_24_099, equinox_holdings_inc, yoursoulmatters_soul_cycle_com, cancellation_channel, email, yoursoulmatters_soul_cycle_com, findings_para_58).

% [prose-shaped contact] narrative sentence forced into the channel_value slot.
state_ag_contact_channel(aod_24_099, equinox_holdings_inc, equinox_cancellation, cancellation_channel, email, members_could_cancel_by_certified_mail_at_the_front_desk_or_by_emailing_cancellations, findings_para_32).

% [open-ended finding recast as obligation] a FINDING about material terms is not a prospective-relief
% obligation; the relief provisions are not in this extract.
state_ag_obligation(aod_24_099, equinox_holdings_inc, obligation_22, disclosure_obligation, ongoing, not_stated, findings_para_22).

% [finding mis-typed as settlement payment] $300 is the Equinox initiation fee charged to consumers
% (material term, para 22), NOT a settlement/penalty payment; no monetary settlement is in this extract.
state_ag_monetary_payment(aod_24_099, equinox_group_llc, new_york_attorney_general, usd_300, penalty, not_stated, findings_para_22).

% [narrative as event] "save the member" is narrative conduct (para 38), not a dated instrument event.
state_ag_event(aod_24_099, event_save, save_the_member_instruction, not_stated, equinox, findings_para_38).
