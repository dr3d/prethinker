% forbidden_facts.pl — puc_order_ugly_003
% Boundary patterns a source-faithful compiler must not emit.

% Settlement-finding sentence forced into the DecisionStatus slot.
puc_order(utah_psc_24_035_04_omd, utah_psc, docket_24_035_04, order_memorializing_decision, v_2025_06_24, just_and_reasonable_in_result_and_in_the_public_interest, src_caption).

% Conflated disposition: this order MEMORIALIZES a prior approval; it does not itself newly approve.
puc_order(utah_psc_24_035_04_omd, utah_psc, docket_24_035_04, order_memorializing_decision, v_2025_06_24, approves_settlement, src_caption).

% Full caption sentence smuggled into the OrderKind slot.
puc_order(utah_psc_24_035_04_omd, utah_psc, docket_24_035_04, order_memorializing_decision_application_of_rocky_mountain_power_for_authority_to_increase_its_retail_electric_utility_service_rates, v_2025_06_24, memorializes_decision, src_caption).

% Conflated identifier: DW#340357 is a document-control number, not the docket (24-035-04).
puc_order(utah_psc_24_035_04_omd, utah_psc, dw_340357, order_memorializing_decision, v_2025_06_24, memorializes_decision, src_caption).

% Wrong issued date: April 25, 2025 is the prior lengthy order that omitted the language;
% this Order Memorializing Decision issued June 24, 2025.
puc_order(utah_psc_24_035_04_omd, utah_psc, docket_24_035_04, order_memorializing_decision, v_2025_04_25, memorializes_decision, src_caption).

% Inferred finality / wrong closed kind: the document is an Order Memorializing Decision,
% not a "final order" (the final order was the April 25, 2025 order).
puc_order(utah_psc_24_035_04_omd, utah_psc, docket_24_035_04, final_order, v_2025_06_24, memorializes_decision, src_caption).

% Certificate-of-service distribution roster forced into the source/scope slot.
puc_order(utah_psc_24_035_04_omd, utah_psc, docket_24_035_04, order_memorializing_decision, v_2025_06_24, memorializes_decision, pacificorp_mayer_brown_mcdowell_rackner_western_resource_advocates_utah_clean_energy).
