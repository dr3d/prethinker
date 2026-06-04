osha_inspection(Inspection, report_0112600, Establishment, springfield_area_office, v_2025_03_28, open, SrcInspection).
osha_establishment(Establishment, premier_fence_llc, west_springfield_ma, naics_238990, SrcEstablishment).

osha_accident(Accident, Inspection, accident_180500_015, v_2025_03_28, struck_by_vehicle, 3, SrcAccident).
osha_injured_employee(Accident, employee_1, 26, m, fatality, construction_laborers, SrcEmployee1).
osha_injured_employee(Accident, employee_2, 48, m, fatality, construction_laborers, SrcEmployee2).
osha_injured_employee(Accident, employee_3, 57, m, fatality, construction_laborers, SrcEmployee3).

osha_violation_count(Inspection, initial, serious, 2, SrcInitialSerious).
osha_violation_count(Inspection, current, serious, 2, SrcCurrentSerious).
osha_violation_count(Inspection, initial, total, 2, SrcInitialTotal).
osha_violation_count(Inspection, current, total, 2, SrcCurrentTotal).

osha_penalty_amount(Inspection, initial, serious, usd_23170, SrcInitialSeriousPenalty).
osha_penalty_amount(Inspection, current, serious, usd_23170, SrcCurrentSeriousPenalty).
osha_penalty_amount(Inspection, initial, total, usd_23170, SrcInitialTotalPenalty).
osha_penalty_amount(Inspection, current, total, usd_23170, SrcCurrentTotalPenalty).

osha_violation_item(Inspection, Citation1, item_1, serious, standard_19260200_g01, v_2025_09_17, usd_11585, SrcViolation1).
osha_violation_item(Inspection, Citation2, item_2, serious, standard_19260200_g02, v_2025_09_17, usd_11585, SrcViolation2).
osha_violation_status(Citation1, v_2025_10_06, v_2025_11_04, contested, SrcStatus1).
osha_violation_status(Citation2, v_2025_10_06, v_2025_11_04, contested, SrcStatus2).

osha_related_activity(Inspection, accident, activity_2277281, not_stated, not_stated).
osha_related_activity(Inspection, inspection, activity_1814197, yes, not_stated).
