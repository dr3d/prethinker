% forbidden_facts.pl — procurement_contract_ugly_003 (Enviremedial Services, B-423552.3)

% Conflates the PRIOR decision's partial-sustain (B-423552/.2, Aug 28 2025) with this one,
% which DENIES the protest.
gao_bid_protest_decision(gao_b_423552_3, gao, b_423552_3, rfp_w912hp25r1000, v_2026_03_24, sustained_in_part, src_header).
% Whole protest was not dismissed; only one ground was dismissed as untimely. Overall: denied.
gao_bid_protest_decision(gao_b_423552_3, gao, b_423552_3, rfp_w912hp25r1000, v_2026_03_24, dismissed, src_header).
% GAO stated "The protest is denied," not "denied in part" - do not infer a partial phrasing.
gao_bid_protest_decision(gao_b_423552_3, gao, b_423552_3, rfp_w912hp25r1000, v_2026_03_24, denied_in_part, src_header).

% Conflated docket: the prior protest filings B-423552 and B-423552.2 are distinct from this B-423552.3.
gao_bid_protest_decision(gao_b_423552_3, gao, b_423552, rfp_w912hp25r1000, v_2026_03_24, denied, src_header).
gao_bid_protest_decision(gao_b_423552_3, gao, b_423552_2, rfp_w912hp25r1000, v_2026_03_24, denied, src_header).

% Wrong date: Aug 28, 2025 is the prior decision; this decision is dated March 24, 2026.
gao_bid_protest_decision(gao_b_423552_3, gao, b_423552_3, rfp_w912hp25r1000, v_2025_08_28, denied, src_header).

% CPAR-merits detail forced into the ProcurementId slot.
gao_bid_protest_decision(gao_b_423552_3, gao, b_423552_3, three_marginal_cpar_ratings_on_a_six_month_interim_evaluation, v_2026_03_24, denied, src_header).

% Tradeoff finding sentence forced into the DecisionStatus slot.
gao_bid_protest_decision(gao_b_423552_3, gao, b_423552_3, rfp_w912hp25r1000, v_2026_03_24, brymak_lower_priced_proposal_represented_best_value, src_header).
