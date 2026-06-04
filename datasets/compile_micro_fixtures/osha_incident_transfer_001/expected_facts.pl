osha_inspection(Inspection, report_0420600, Establishment, tampa_area_office, v_2020_01_13, closed, SrcInspection).
osha_establishment(Establishment, centimark_corporation, plant_city_fl, naics_238160, SrcEstablishment).

osha_accident(Accident, Inspection, accident_123160_015, v_2020_01_13, fall, 1, SrcAccident).
osha_injured_employee(Accident, employee_1, 51, m, fatality, roofers, SrcEmployee1).

osha_violation_count(Inspection, initial, serious, 1, SrcInitialSerious).
osha_violation_count(Inspection, current, serious, 1, SrcCurrentSerious).
osha_violation_count(Inspection, initial, total, 1, SrcInitialTotal).
osha_violation_count(Inspection, current, total, 1, SrcCurrentTotal).

osha_penalty_amount(Inspection, initial, serious, usd_13494, SrcInitialSeriousPenalty).
osha_penalty_amount(Inspection, current, serious, usd_6747, SrcCurrentSeriousPenalty).
osha_penalty_amount(Inspection, initial, total, usd_13494, SrcInitialTotalPenalty).
osha_penalty_amount(Inspection, current, total, usd_6747, SrcCurrentTotalPenalty).

osha_violation_item(Inspection, Citation1, item_1, serious, standard_19260760_a01, v_2020_06_25, usd_6747, SrcViolation1).
osha_violation_status(Citation1, not_stated, v_2020_07_08, informal_settlement, SrcStatus1).

osha_related_activity(Inspection, accident, activity_1533489, not_stated, not_stated).
