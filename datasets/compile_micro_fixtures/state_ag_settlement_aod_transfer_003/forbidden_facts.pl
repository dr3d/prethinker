% forbidden_facts.pl — state_ag_settlement_aod_transfer_003
% Negative controls using the same registered signatures. Each must NOT be emitted.

% [prose instrument] full caption sentence smuggled into the instrument_number slot.
state_ag_instrument(aod_24_102, assurance_of_discontinuance, new_york_attorney_general, equifax_information_services_llc, in_the_matter_of_the_investigation_by_letitia_james_of_equifax_information_services_llc, v_2025_01_02, caption).

% [wrong party-role] Equifax is the Respondent, not the regulator.
state_ag_party(aod_24_102, equifax_information_services_llc, regulator, equifax_information_services_llc, caption).

% [wrong party-role] Prentice-Hall is Equifax's registered agent (para 3), not a Respondent.
state_ag_party(aod_24_102, prentice_hall_corporation_system_inc, respondent, prentice_hall_corporation_system_inc, findings_para_3).

% [prose party] narrative corporate descriptor forced into the party_name slot.
state_ag_party(aod_24_102, equifax_information_services_llc, respondent, for_profit_georgia_limited_liability_company_principal_place_of_business_atlanta_georgia, findings_para_2).

% [wrong authority-role] GBL 349-d is the payment authority (para 15), not an investigation authority.
state_ag_authority_citation(aod_24_102, gbl_349_d, investigation_authority, recitals).

% [prose authority] statute description smuggled into the citation slot.
state_ag_authority_citation(aod_24_102, reasonable_procedures_to_assure_maximum_possible_accuracy_in_consumer_reports, prospective_relief_authority, agreement_para_8).

% [wrong contact-channel attachment] Oldham/Equifax email is not the NYAG channel.
state_ag_contact_channel(aod_24_102, new_york_attorney_general, nick_oldham, regulator_contact, email, nicholas_oldham_equifax_com, communications_para_25).

% [prose contact] notice-method narrative forced into the channel_value slot.
state_ag_contact_channel(aod_24_102, equifax_information_services_llc, nick_oldham, respondent_contact, email, given_by_hand_delivery_express_courier_or_electronic_mail_at_a_designated_address, communications_para_25).

% [wrong payment/deadline] payment is due within thirty days (para 15), not sixty.
state_ag_monetary_payment(aod_24_102, equifax_information_services_llc, state_of_new_york, usd_725000, restitution_and_penalties, within_60_days, agreement_para_15).

% [prose monetary] discretionary-use sentence forced into the payment_kind slot.
state_ag_monetary_payment(aod_24_102, equifax_information_services_llc, state_of_new_york, usd_725000, to_be_used_as_restitution_and_penalties_in_the_sole_and_absolute_discretion_of_the_nyag, within_30_days, agreement_para_15).

% [signature-role confusion] Letitia James is named but did not sign; the block is signed "By: Azia"
% and "By: Goldis" for the NYAG. James is not a signatory.
state_ag_signature(aod_24_102, new_york_attorney_general, letitia_james, attorney_general, v_2025_01_02, signature_block).

% [open-ended finding refused] para 1's "may have caused some consumers to be denied credit" is a
% finding narrative, not a dated instrument event.
state_ag_event(aod_24_102, event_denied_credit, consumers_denied_credit, not_stated, oms_issue, findings_para_1).
