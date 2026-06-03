ntsb_report(Report, aviation_accident, preliminary, v_2025_11_07, SrcReport).
ntsb_occurrence(Occurrence, Report, aviation_accident, v_2025_11_05, louisville_kentucky, SrcOccurrence).
ntsb_occurrence_time(Occurrence, t_2025_11_05_1713_30_est, eastern_standard_time, about_time, SrcAccidentTime).

ntsb_vehicle(Aircraft, Occurrence, aircraft, boeing_md_11f, n259up, SrcAircraft).
ntsb_party(Occurrence, Operator, operator, ups_airlines, SrcOperator).

ntsb_injury_count(Occurrence, crew, 0, 0, 0, SrcCrewInjuries).
ntsb_injury_count(Occurrence, passenger, 0, 0, 0, SrcPassengerInjuries).

ntsb_condition(Occurrence, visibility, miles_10, weather, SrcVisibility).
ntsb_condition(Occurrence, wind, degrees_310_knots_4, weather, SrcWind).
ntsb_condition(Occurrence, recorder_state, cvr_not_recovered, recorder, SrcCvr).
ntsb_condition(Occurrence, recorder_state, fdr_recovered, recorder, SrcFdr).

ntsb_safety_action(Action, Occurrence, Actor, emergency_directive, v_2025_11_14, SrcAd).

domain_omission(Occurrence, 'ntsb_finding/5', none_found, probable_cause_or_finding_not_stated, SrcFindingOmission).
