% Iron Harbor Water Crisis -- Reference Prolog KB
% This is what a correct Prethinker ingestion should approximately produce.
% Predicate names are suggestions; the profile bootstrapper may propose alternatives.

% === Roles ===
person_role(diane_cheng, chief_water_officer).
person_role(luis_ferreira, harbor_master).
person_role(k_lindstrom, facility_manager_eastgate).
person_role(r_vasquez, lab_technician).
person_role(m_okonkwo, lab_technician).
person_role(j_patel, dispatch_operator).

% === Zone classification ===
residential_zone(millbrook).
residential_zone(linden_terrace).
residential_zone(old_harbor).
non_residential_zone(foundry_row).
downstream_of(millbrook, eastgate).
downstream_of(linden_terrace, eastgate).
downstream_of(old_harbor, eastgate).

% === Facilities ===
facility(eastgate_treatment_facility, treatment).
facility(pier_7_chlorination_unit, emergency_bypass).
facility(intake_point_alpha, intake).

% === Standing policy rules ===
testing_interval(normal, 72).
testing_interval(contamination_advisory, 12).
contamination_threshold(coliform, 400).
clean_threshold(coliform, 50).
boil_water_notice_deadline_hours(1).
boil_water_notice_lift_deadline_hours(4).
foundry_row_notification_deadline_hours(2).
eastgate_offline_threshold_hours(6).
bypass_inspection_validity_days(30).
bypass_requires_joint(chief_water_officer, harbor_master).
consecutive_clean_readings_required(2).
clean_reading_interval_hours(12).

% === Coliform readings (corrected values) ===
coliform_reading(intake_point_alpha, 85, '2026-03-03T06:00', r_vasquez).
coliform_reading(intake_point_alpha, 180, '2026-03-03T14:00', r_vasquez).
coliform_reading(intake_point_alpha, 480, '2026-03-04T02:00', m_okonkwo).
coliform_reading(intake_point_alpha, 35, '2026-03-05T04:00', r_vasquez).
coliform_reading(intake_point_alpha, 28, '2026-03-05T16:00', r_vasquez).

% === Corrections (retracted values preserved as claims) ===
% claim: original_coliform_reading(intake_point_alpha, 120, '2026-03-03T14:00', r_vasquez).
% correction_authority: lab_notebook, r_vasquez
% claim: okonkwo_stated_arrival('2026-03-04T01:45').
% correction_authority: badge_log, showing 01:52
% claim: ferreira_initial_inspection_date('2026-01-28').
% correction_authority: written_inspection_log, showing 2026-02-01

% === Authoritative corrected facts ===
okonkwo_arrival(intake_point_alpha, '2026-03-04T01:52').
inspection(pier_7_chlorination_unit, luis_ferreira, '2026-02-01').

% === Contamination advisory ===
contamination_advisory(triggered, '2026-03-04T02:00').
contamination_advisory(lifted, '2026-03-06T09:00').

% === Notifications ===
notification(diane_cheng, contamination_advisory, '2026-03-04T02:15', phone, m_okonkwo).
notification(foundry_row, contamination_advisory, '2026-03-04T03:30', email, j_patel).

% === Facility status ===
facility_status(eastgate_treatment_facility, offline, '2026-03-04T08:00').
facility_status(eastgate_treatment_facility, online, '2026-03-05T16:30').

% === Bypass authorization ===
bypass_authorization(pier_7_chlorination_unit, luis_ferreira, '2026-03-04T15:30').
bypass_authorization(pier_7_chlorination_unit, diane_cheng, '2026-03-04T15:45').
bypass_activated(pier_7_chlorination_unit, '2026-03-04T16:00').

% === Boil-water notice ===
boil_water_notice(millbrook, '2026-03-04T14:45', diane_cheng).
boil_water_notice(linden_terrace, '2026-03-04T14:45', diane_cheng).
% NOTE: old_harbor is NOT in the boil-water notice -- this is a policy violation.
boil_water_notice_lifted('2026-03-05T20:30', diane_cheng).

% === Post-incident ===
review_meeting('2026-03-06T10:00', [diane_cheng, luis_ferreira, k_lindstrom, r_vasquez, m_okonkwo, j_patel]).

% === Temporal ordering (admitted before/2 for the temporal kernel) ===
before('2026-03-03T06:00', '2026-03-03T14:00').
before('2026-03-03T14:00', '2026-03-04T02:00').
before('2026-03-04T02:00', '2026-03-04T08:00').
before('2026-03-04T08:00', '2026-03-04T14:00').
before('2026-03-04T14:00', '2026-03-04T14:45').
before('2026-03-04T14:45', '2026-03-04T15:30').
before('2026-03-04T15:30', '2026-03-04T15:45').
before('2026-03-04T15:45', '2026-03-04T16:00').
before('2026-03-04T16:00', '2026-03-05T04:00').
before('2026-03-05T04:00', '2026-03-05T16:00').
before('2026-03-05T16:00', '2026-03-05T16:30').
before('2026-03-05T16:30', '2026-03-05T20:30').
before('2026-03-05T20:30', '2026-03-06T09:00').
before('2026-03-06T09:00', '2026-03-06T10:00').

% === Disclosure (NOT a finding -- scoped as claim) ===
% claim: disclosure(diane_cheng, aware_of_pump_deterioration_feb_20, '2026-03-06', statement_not_finding).

% === Derived rules (should be installed from policy, not written as facts) ===
% Rule: advisory triggered when reading > 400
% contamination_advisory_triggered :- coliform_reading(_, V, _, _), V > 400.
%
% Rule: boil-water notice required when Eastgate offline > 6 hours during advisory
% boil_water_required(Zone) :- residential_zone(Zone), downstream_of(Zone, eastgate),
%     facility_status(eastgate_treatment_facility, offline, _),
%     contamination_advisory(triggered, _).
%
% Rule: bypass authorization valid only if both officers sign AND inspection current
% bypass_valid(Facility) :-
%     bypass_authorization(Facility, Officer1, _),
%     bypass_authorization(Facility, Officer2, _),
%     Officer1 \= Officer2,
%     person_role(Officer1, chief_water_officer),
%     person_role(Officer2, harbor_master),
%     inspection(Facility, Officer2, InspDate),
%     days_since(InspDate, Days),
%     Days =< 30.
