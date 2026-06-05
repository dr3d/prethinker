% expected_facts.pl — state_ag_settlement_aod_transfer_003
% NY OAG Assurance of Discontinuance, In re Equifax Information Services LLC (AOD 24-102).
% Full instrument (recitals, findings 1-9, agreement 1-37, monetary, communications, signatures).
% Registered state_ag_settlement_v1 signatures only; compact atoms; paragraph coordinates in scope.

% --- instrument wrapper ---
% effective_date v_2025_01_02 stated in agreement para 37 and the signature block ("Date: Jan. 2, 2025").
state_ag_instrument(aod_24_102, assurance_of_discontinuance, new_york_attorney_general, equifax_information_services_llc, assurance_24_102, v_2025_01_02, caption).

% --- parties ---
state_ag_party(aod_24_102, new_york_attorney_general, regulator, new_york_attorney_general, caption).
state_ag_party(aod_24_102, equifax_information_services_llc, respondent, equifax_information_services_llc, caption).
state_ag_party(aod_24_102, prentice_hall_corporation_system_inc, registered_agent, prentice_hall_corporation_system_inc, findings_para_3).
state_ag_party(aod_24_102, alston_bird_llp, counsel, alston_bird_llp, signature_block).

% --- authority citations ---
state_ag_authority_citation(aod_24_102, executive_law_63_12, investigation_authority, recitals).
state_ag_authority_citation(aod_24_102, gbl_349, investigation_authority, recitals).
state_ag_authority_citation(aod_24_102, gbl_350, investigation_authority, recitals).
state_ag_authority_citation(aod_24_102, executive_law_63_15, assurance_authority, agreement_para_1).
state_ag_authority_citation(aod_24_102, gbl_349_d, payment_authority, agreement_para_15).
state_ag_authority_citation(aod_24_102, public_officers_law_87, confidentiality_authority, agreement_para_14).
state_ag_authority_citation(aod_24_102, gbl_380_j, prospective_relief_authority, agreement_para_6).

% --- chronology (exact-date OMS events) ---
state_ag_event(aod_24_102, event_1, code_change_introduced, v_2022_03_17, oms_issue, findings_para_5).
state_ag_event(aod_24_102, event_2, equifax_investigation_initiated, v_2022_03_22, oms_issue, findings_para_5).
state_ag_event(aod_24_102, event_3, oms_issue_partially_resolved, v_2022_04_06, oms_issue, findings_para_6).
state_ag_event(aod_24_102, event_4, oms_issue_fully_resolved, v_2022_04_08, oms_issue, findings_para_6).

% --- prospective-relief obligations (numbered agreement paragraphs) ---
state_ag_obligation(aod_24_102, equifax_information_services_llc, obligation_9, change_control_review, ongoing, not_stated, agreement_para_9).
state_ag_obligation(aod_24_102, equifax_information_services_llc, obligation_11, training_program, ongoing, not_stated, agreement_para_11).
state_ag_obligation(aod_24_102, equifax_information_services_llc, obligation_13, incident_monitoring, weekly, not_stated, agreement_para_13).
state_ag_obligation(aod_24_102, equifax_information_services_llc, obligation_14, cooperation, ongoing, not_stated, agreement_para_14).
state_ag_obligation(aod_24_102, equifax_information_services_llc, obligation_20, documentation_on_request, on_request, not_stated, agreement_para_20).

% --- monetary payment ---
state_ag_monetary_payment(aod_24_102, equifax_information_services_llc, state_of_new_york, usd_725000, restitution_and_penalties, within_30_days, agreement_para_15).

% --- contact channels (Communications para 25), tied to the correct party/role ---
state_ag_contact_channel(aod_24_102, equifax_information_services_llc, nick_oldham, respondent_contact, email, nicholas_oldham_equifax_com, communications_para_25).
state_ag_contact_channel(aod_24_102, alston_bird_llp, john_redding, counsel_contact, email, john_redding_alston_com, communications_para_25).
state_ag_contact_channel(aod_24_102, new_york_attorney_general, glenna_goldis, regulator_contact, email, glenna_goldis_ag_ny_gov, communications_para_25).

% --- signatures (signature block, Date: Jan. 2, 2025) ---
state_ag_signature(aod_24_102, new_york_attorney_general, jane_azia, bureau_chief, v_2025_01_02, signature_block).
state_ag_signature(aod_24_102, new_york_attorney_general, glenna_goldis, assistant_attorney_general, v_2025_01_02, signature_block).
state_ag_signature(aod_24_102, equifax_information_services_llc, nick_oldham, chief_compliance_officer, v_2025_01_02, signature_block).
state_ag_signature(aod_24_102, alston_bird_llp, john_redding, counsel, v_2025_01_02, signature_block).
