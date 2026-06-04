osha_inspection(Inspection, report_0111400, Establishment, boston_south_area_office, v_2024_12_20, closed, SrcInspection).
osha_establishment(Establishment, revoli_construction_co_inc, south_yarmouth_ma, naics_237110, SrcEstablishment).
domain_omission(Inspection, 'osha_accident/7', none_found, accident_summary_not_stated, SrcAccidentOmission).

osha_violation_count(Inspection, initial, serious, 1, SrcInitialSerious).
osha_violation_count(Inspection, initial, other, 1, SrcInitialOther).
osha_violation_count(Inspection, initial, total, 2, SrcInitialTotal).
osha_violation_count(Inspection, current, other, 1, SrcCurrentOther).
osha_violation_count(Inspection, current, total, 1, SrcCurrentTotal).

osha_penalty_amount(Inspection, initial, serious, usd_11585, SrcInitialSeriousPenalty).
osha_penalty_amount(Inspection, initial, other, usd_1655, SrcInitialOtherPenalty).
osha_penalty_amount(Inspection, initial, total, usd_13240, SrcInitialTotalPenalty).
osha_penalty_amount(Inspection, current, serious, usd_0, SrcCurrentSeriousPenalty).
osha_penalty_amount(Inspection, current, other, usd_6950, SrcCurrentOtherPenalty).
osha_penalty_amount(Inspection, current, total, usd_6950, SrcCurrentTotalPenalty).

osha_violation_item(Inspection, Citation1, item_1, other, standard_19260020_b02, v_2025_02_04, usd_6950, SrcViolation1).
osha_violation_item(Inspection, Citation2, item_2, serious, standard_19260403_b01, v_2025_02_04, usd_0, SrcViolation2).
osha_violation_item(Inspection, Citation3, item_3, other, standard_19040040_a, v_2025_02_04, usd_0, SrcViolation3).

osha_violation_status(Citation1, v_2025_02_26, not_stated, formal_settlement, SrcStatus1).
osha_violation_status(Citation2, v_2025_02_26, not_stated, formal_settlement, SrcStatus2).
osha_violation_status(Citation3, v_2025_02_26, not_stated, formal_settlement, SrcStatus3).

osha_related_activity(Inspection, referral, activity_2243934, yes, not_stated).
