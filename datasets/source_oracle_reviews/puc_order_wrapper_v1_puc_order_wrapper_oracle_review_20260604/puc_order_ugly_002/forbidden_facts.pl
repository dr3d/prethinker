% forbidden_facts.pl — puc_order_ugly_002
% Boundary patterns a source-faithful compiler must not emit.

% Full caption sentence smuggled into the OrderKind slot.
puc_order(cpuc_alj_445, cpuc, h_22_07_010, resolution_alj_445_resolving_request_for_hearing_h_22_07_010_on_administrative_enforcement_order, v_2023_10_16, approves_settlement, src_caption).

% Settlement-finding sentence forced into the DecisionStatus slot.
puc_order(cpuc_alj_445, cpuc, h_22_07_010, resolution, v_2023_10_16, the_amounts_are_fair_just_and_reasonable, src_caption).

% Inferred legal status the source does not state for THIS resolution (it grants, not denies).
puc_order(cpuc_alj_445, cpuc, h_22_07_010, resolution, v_2023_10_16, denies_request, src_caption).

% Conflated identifier: M-4846 is a cited authority (Enforcement Policy), not this order's docket.
puc_order(cpuc_alj_445, cpuc, m_4846, resolution, v_2023_10_16, approves_settlement, src_caption).

% Swapped order id / docket id.
puc_order(h_22_07_010, cpuc, cpuc_alj_445, resolution, v_2023_10_16, approves_settlement, src_caption).

% Wrong issued date: 10/12/2023 is the conference/adoption date; Date of Issuance is 10/16/2023.
puc_order(cpuc_alj_445, cpuc, h_22_07_010, resolution, v_2023_10_12, approves_settlement, src_caption).

% Ordering paragraph forced into a wrapper slot.
puc_order(cpuc_alj_445, cpuc, h_22_07_010, resolution, v_2023_10_16, pge_shall_pay_500000_fine_to_the_general_fund, src_order).

% Commissioner vote roster forced into the source/scope slot.
puc_order(cpuc_alj_445, cpuc, h_22_07_010, resolution, v_2023_10_16, approves_settlement, alice_reynolds_president_genevieve_shiroma_john_reynolds_karen_douglas).
