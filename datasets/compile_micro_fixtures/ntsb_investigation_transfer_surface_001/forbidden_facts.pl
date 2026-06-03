ntsb_report(Report, highway_investigation_report, final, 2025_09_16, SrcReport).
ntsb_occurrence_time(Occurrence, 2041_cdt, central_daylight_time, about_time, SrcAccidentTime).
ntsb_occurrence(Occurrence, Report, OccurrenceKind, v_2023_09_29, us_highway_40_between_mile_markers_21_and_22_teutopolis_effingham_county_illinois, SrcOccurrence).

ntsb_vehicle(Vehicle, Occurrence, combination_vehicle, truck_tractor_cargo_tank_combination_vehicle_carrying_anhydrous_ammonia, Identifier, SrcVehicle).
ntsb_vehicle(Vehicle, Occurrence, accident_vehicle, truck_tractor_cargo_tank, 2005_international_9900ix_1978_mississippi_tank_mc331, SrcVehicle).
ntsb_vehicle(Vehicle, Occurrence, passing_vehicle, minivan, 2013_toyota_sienna, SrcVehicle).
ntsb_condition(Occurrence, weather, dry_clear_and_nighttime_rural_unlit_undivided_highway_with_one_westbound_and_one_eastbound_travel_lane_55_mph_speed_limit, weather, SrcWeather).
ntsb_condition(Occurrence, hazmat_material, division_2_2_non_flammable_nonpoisonous_compressed_gas_with_inhalation_hazard_marking_and_international_division_2_3_gas_poisonous_by_inhalation, cargo, SrcCargo).

ntsb_injury_count(Occurrence, bystander, five, eight, three, SrcBystanderInjuries).
ntsb_injury_count(Occurrence, first_responder, zero, zero, one, SrcResponderInjuries).
ntsb_injury_count(Occurrence, not_stated, 0, 0, 1, SrcDuplicateResponderInjuries).

ntsb_safety_action(ActionRoad, Occurrence, idot, roadway_improvement, planned_2024_2029, SrcRoadAction).

ntsb_finding(Occurrence, Finding, not_stated, not_stated, SrcFinding).
domain_omission(Occurrence, 'ntsb_finding/5', none_found, probable_cause_or_finding_not_stated, SrcFindingOmission).
ntsb_finding(Occurrence, Finding, probable_cause, unsafe_passing_maneuver_by_a_teen_driver_that_caused_the_combination_vehicle_driver_to_initiate_an_evasive_action_that_resulted_in_loss_of_vehicle_control_and_rollover, SrcFinding).
