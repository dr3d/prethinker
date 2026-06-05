% Forbidden facts for state_ag_settlement_aod_v1.
% Each pattern represents an obvious governance failure that must NOT appear.

% full caption packed into the wrapper instead of compact instrument atoms
state_ag_instrument(Aod, assurance_of_discontinuance, 'attorney general of the state of new york bureau of consumer frauds and protection in the matter of investigation by letitia james', equifax_information_services_llc, aod_24_102, v_2025_01_02, SrcInstrument).

% full address blob packed into party identity
state_ag_party(Aod, equifax_information_services_llc, respondent, 'equifax information services llc 1550 peachtree street nw atlanta georgia 30309', SrcEquifax).

% liability/admission inference smuggled into party role
state_ag_party(Aod, equifax_information_services_llc, admitted_wrongdoing, equifax_information_services_llc, SrcEquifax).

% full legal text packed into citation instead of compact citation atom
state_ag_authority_citation(Aod, 'general business law sections 349 and 350 prohibition of deceptive conduct and false advertising full text', investigation_authority, SrcAuthority).

% causal narrative packed into chronology event kind
state_ag_event(Aod, oms_code_change, 'code change caused consumers to be denied credit or offered less favorable terms', v_2022_03_17, oms_issue, SrcEvent).

% full obligation sentence instead of compact obligation kind
state_ag_obligation(Aod, equifax_information_services_llc, obligation_9, 'review and as appropriate update its change control policies and procedures to address the development testing and implementation of technology changes', ongoing, not_stated, SrcObligation).

% bare number amount instead of compact typed amount
state_ag_monetary_payment(Aod, equifax_information_services_llc, state_of_new_york, 725000, restitution_and_penalties, within_30_days_after_assurance_date, SrcPayment).

% full notice paragraph packed into contact channel value
state_ag_contact_channel(Aod, nyag, glenna_goldis, regulator_contact, email, 'office of the new york state attorney general 28 liberty street new york ny 10005 glenna goldis ag email and phone', SrcContact).

% full signature block packed into signatory title
state_ag_signature(Aod, nyag, glenna_goldis, 'assistant attorney general consumer frauds and protection bureau 646 856 3697 glenna goldis ag ny gov', v_2025_01_02, SrcSignature).
