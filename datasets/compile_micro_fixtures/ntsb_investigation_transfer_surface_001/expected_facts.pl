ntsb_report(Report, highway_crash, final, v_2025_09_16, SrcReport).
ntsb_occurrence(Occurrence, Report, highway_crash, v_2023_09_29, Location, SrcOccurrence).
ntsb_occurrence_time(Occurrence, t_2023_09_29_2041_cdt, central_daylight_time, occurrence_time, SrcAccidentTime).

ntsb_vehicle(CombinationVehicle, Occurrence, accident_vehicle, combination_vehicle, not_stated, SrcCombinationVehicle).
ntsb_vehicle(Minivan, Occurrence, passing_vehicle, minivan, not_stated, SrcMinivan).

ntsb_party(Occurrence, Carrier, operator, prairieland_transport, SrcCarrier).

ntsb_injury_count(Occurrence, driver, 0, 1, 0, SrcDriverInjuries).
ntsb_injury_count(Occurrence, bystander, 5, 8, 3, SrcBystanderInjuries).
ntsb_injury_count(Occurrence, first_responder, 0, 0, 1, SrcResponderInjuries).

ntsb_condition(Occurrence, weather, dry_clear_nighttime, weather, SrcWeather).
ntsb_condition(Occurrence, roadway, rural_unlit_undivided_highway, roadway, SrcRoadway).
ntsb_condition(Occurrence, speed_limit, mph_55, roadway, SrcSpeedLimit).
ntsb_condition(Occurrence, hazmat_material, anhydrous_ammonia, cargo, SrcCargo).
ntsb_condition(Occurrence, hazmat_un_number, un1005, cargo, SrcUnNumber).

ntsb_timeline_event(Occurrence, Event911, distress_call, t_2023_09_29_2043_cdt, start, Src911).
ntsb_timeline_event(Occurrence, EventClosedOrder, road_closure_ordered, t_2023_09_29_2055_cdt, intermediate, SrcClosedOrder).
ntsb_timeline_event(Occurrence, EventClosedComplete, road_closure_completed, t_2023_09_29_2106_cdt, intermediate, SrcClosedComplete).
ntsb_timeline_event(Occurrence, EventMabas, mutual_aid_request, t_2023_09_29_2116_cdt, intermediate, SrcMabas).
ntsb_timeline_event(Occurrence, EventEntry, hazmat_entry, t_2023_09_29_2317_cdt, intermediate, SrcEntry).
ntsb_timeline_event(Occurrence, EventReopen, road_reopen, t_2023_09_30_2020_cdt, end, SrcReopen).

ntsb_safety_action(ActionReview, Occurrence, org_ruralmed, after_action_review, not_stated, SrcAfterAction).
ntsb_safety_action(ActionTraining, Occurrence, org_teutopolis_fire_dept, hazmat_training, not_stated, SrcTraining).
ntsb_safety_action(ActionRoad, Occurrence, org_idot, roadway_improvement, not_stated, SrcRoadAction).

ntsb_finding(Occurrence, CauseFinding, probable_cause, FindingValue, SrcCause).
ntsb_finding(Occurrence, FactorFinding, contributing_factor, FindingValue, SrcFactor).
