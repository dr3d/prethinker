% Artifact 2 - Gold Prolog KB
% Fixture: The Glass Tide Charter of Lumenfall Harbor
% Notes:
% - This KB intentionally separates facts, claims, observations, certified logs, and executable rules.
% - It is designed as a gold target for Prethinker, not as the only possible representation.
% - Rules are source-stated unless marked as utility/derived helper rules.

:- discontiguous person/1.
:- discontiguous place/1.
:- discontiguous role/2.
:- discontiguous cargo/1.
:- discontiguous vessel/1.
:- discontiguous observed/1.
:- discontiguous certified_log/1.
:- discontiguous claim/3.

% ------------------------------------------------------------------
% Time helpers
% ------------------------------------------------------------------

time_min(t1000, 600).
time_min(t1200, 720).
time_min(t1700, 1020).
time_min(t1730, 1050).
time_min(t1740, 1060).
time_min(t1745, 1065).
time_min(t1800, 1080).
time_min(t1805, 1085).
time_min(t1815, 1095).
time_min(t1820, 1100).
time_min(t1825, 1105).
time_min(t1830, 1110).
time_min(t1850, 1130).
time_min(t1905, 1145).
time_min(t1910, 1150).
time_min(t1930, 1170).
time_min(t2005, 1205).
time_min(t2015, 1215).
time_min(t2040, 1240).
time_min(t2100, 1260).
time_min(t2110, 1270).
time_min(t2125, 1285).
time_min(t2200, 1320).
time_min(t2230, 1350).
time_min(t2359, 1439).
time_min(t1200_next_day, 2160).

at_or_after(T, S) :- time_min(T, TM), time_min(S, SM), TM >= SM.
at_or_before(T, E) :- time_min(T, TM), time_min(E, EM), TM =< EM.
between_inclusive(T, S, E) :- at_or_after(T, S), at_or_before(T, E).
at_least_hours_apart(T1, T2, Hours) :-
    time_min(T1, M1),
    time_min(T2, M2),
    Delta is M2 - M1,
    Required is Hours * 60,
    Delta >= Required.

% ------------------------------------------------------------------
% People, roles, places
% ------------------------------------------------------------------

person(mara_vale).
person(juno_vale).
person(ilya_sen).
person(sera_voss).
person(tomas_reed).
person(karel_nim).
person(nell_quill).
person(dr_pella_morn).
person(basil_crow).
person(captain_orra_pike).
person(captain_veda_lark).
person(dax_orr).
person(mira_gale).

role(mara_vale, harbor_warden).
role(juno_vale, chief_tide_engineer).
role(ilya_sen, archivist).
role(sera_voss, treasurer).
role(tomas_reed, lighthouse_keeper).
role(karel_nim, deputy_warden).
role(nell_quill, apprentice_courier).
role(dr_pella_morn, physician).
role(basil_crow, merchant).
role(captain_orra_pike, captain).
role(captain_veda_lark, captain).

sibling(mara_vale, juno_vale).
sibling(juno_vale, mara_vale).

place(lumenfall_harbor).
place(archive_vault).
place(beacon_tower).
place(glass_market).
place(quarantine_pier).
place(west_sluice).
place(east_gate).
place(moon_foundry).
place(temple_of_loam).
place(harbor_hospital).
place(offshore_waiting_ring).

council_voting_officer(mara_vale).
council_voting_officer(juno_vale).
council_voting_officer(ilya_sen).
council_voting_officer(sera_voss).
council_voting_officer(tomas_reed).

absent(karel_nim, azure17).

% ------------------------------------------------------------------
% Charter windows and alarms
% ------------------------------------------------------------------

glass_tide_window(azure17, t1800, t2200).
during_glass_tide(T) :- glass_tide_window(azure17, S, E), between_inclusive(T, S, E).

observed(owl_faces_sea_at_dawn(azure17)).
observed(barometer_below(azure17, 27)).
storm_alarm_raised(t1730).
storm_alarm_ends(t2359).
storm_alarm_active_at(T) :- between_inclusive(T, t1730, t2359).

% ------------------------------------------------------------------
% Engine readings and harbor closure
% ------------------------------------------------------------------

tideheart_pressure(t1740, 84).
tideheart_coolant(t1740, 7).
tideheart_pressure(t2230, 61).
tideheart_coolant(t2230, 18).

instrument_record(tideheart_pressure(t1740, 84)).
instrument_record(tideheart_coolant(t1740, 7)).
instrument_record(tideheart_pressure(t2230, 61)).
instrument_record(tideheart_coolant(t2230, 18)).

engine_critical_at(T) :-
    tideheart_pressure(T, P),
    tideheart_coolant(T, C),
    P > 80,
    C < 10.

harbor_closed_between(t1740, t2230).
harbor_closed_at(T) :- between_inclusive(T, t1740, t2230).
harbor_reopened_at(t2230).

% ------------------------------------------------------------------
% Vessels and cargo
% ------------------------------------------------------------------

vessel(sunless_heron).
vessel(amber_finch).

captain_of(captain_orra_pike, sunless_heron).
captain_of(captain_veda_lark, amber_finch).

vessel_arrival(sunless_heron, t1820).
certified_arrival_time(sunless_heron, t1820).
docked_at(sunless_heron, west_sluice, t1825).
emergency_signal(sunless_heron, t1820).

uncertified_arrival_note(amber_finch, t1850).
certified_arrival_time(amber_finch, t1910).
vessel_arrival(amber_finch, t1910).
waited_at(amber_finch, offshore_waiting_ring).
entered_after_reopening(amber_finch).

cargo(glass_eels).
cargo(seed_crystals).
cargo(sapphire_figs).
cargo(lamp_rice).
cargo(blue_salt_crate_c17).
cargo(saint_loam_bell).

carried_by(glass_eels, sunless_heron).
carried_by(seed_crystals, amber_finch).
brought_by(sapphire_figs, basil_crow).
received_by(lamp_rice, harbor_hospital).

cargo_type(glass_eels, living_cargo).
cargo_value(glass_eels, 300).
cargo_owner(glass_eels, captain_orra_pike).

cargo_value(seed_crystals, 80).
cargo_owner(seed_crystals, captain_veda_lark).

cargo_value(sapphire_figs, 130).
cargo_owner(sapphire_figs, basil_crow).
ordinary_merchant_cargo(sapphire_figs).

cargo_value(lamp_rice, 240).
relief_cargo(lamp_rice).

abandoned(blue_salt_crate_c17).
not_sacred(blue_salt_crate_c17).
sacred(saint_loam_bell).

transferred_to(glass_eels, quarantine_pier, t1850).

claim(captain_orra_pike, signed_clearance(sunless_heron), t1821).
observed(no_signed_clearance_found(sunless_heron)).

% ------------------------------------------------------------------
% Evidence boundary and correction rules
% ------------------------------------------------------------------

supports_finding(P) :- observed(P).
supports_finding(P) :- instrument_record(P).
supports_finding(P) :- certified_log(P).

claim_only(P) :- claim(_, P, _), \+ supports_finding(P).

certified_log(arrival_time(amber_finch, t1910)).
weaker_note(arrival_time(amber_finch, t1850)).

effective_arrival_time(V, T) :- certified_arrival_time(V, T).
effective_arrival_time(V, T) :-
    uncertified_arrival_note(V, T),
    \+ certified_arrival_time(V, _).

certified_log_controls_over_uncertified_note(Event) :-
    certified_log(Event),
    weaker_note(Event).

% ------------------------------------------------------------------
% Living-cargo quarantine and harbor closure rules
% ------------------------------------------------------------------

living_cargo(Cargo) :- cargo_type(Cargo, living_cargo).
vessel_carries_living_cargo(Vessel) :- carried_by(Cargo, Vessel), living_cargo(Cargo).

signed_clearance(Vessel) :-
    clearance_signed_by(Vessel, mara_vale),
    clearance_signed_by(Vessel, dr_pella_morn).

requires_quarantine_pier(Vessel) :-
    vessel_carries_living_cargo(Vessel),
    \+ signed_clearance(Vessel).

temporary_west_sluice_dock_authorized(Vessel, Time) :-
    vessel_arrival(Vessel, ArrivalTime),
    harbor_closed_at(ArrivalTime),
    emergency_signal(Vessel, ArrivalTime),
    Time = t1825.

living_cargo_quarantine_compliant(Vessel) :-
    carried_by(Cargo, Vessel),
    living_cargo(Cargo),
    transferred_to(Cargo, quarantine_pier, _).

must_wait_offshore(Vessel) :-
    vessel_arrival(Vessel, Time),
    harbor_closed_at(Time),
    \+ emergency_signal(Vessel, Time).

may_dock_at_west_sluice(Vessel) :-
    vessel_arrival(Vessel, Time),
    harbor_closed_at(Time),
    emergency_signal(Vessel, Time).

% ------------------------------------------------------------------
% Archive access
% ------------------------------------------------------------------

apprentice(nell_quill).
possessed_key(nell_quill, blue_key, t1745).
entered(nell_quill, archive_vault, t1745).
red_seal_used(ilya_sen, nell_quill, blue_key, t1805).

key_revoked_at(Person, Key, T) :-
    red_seal_used(_, Person, Key, SealTime),
    at_or_after(T, SealTime),
    at_or_before(T, t1200_next_day).

has_valid_key(Person, Key, T) :-
    possessed_key(Person, Key, _),
    \+ key_revoked_at(Person, Key, T).

entry_authorized(Person, archive_vault, T) :-
    escorted_by(Person, Escort, T),
    role(Escort, archivist).

entry_authorized(Person, archive_vault, T) :-
    apprentice(Person),
    has_valid_key(Person, blue_key, T),
    \+ storm_alarm_active_at(T).

unauthorized_entry(Person, archive_vault, T) :-
    entered(Person, archive_vault, T),
    \+ entry_authorized(Person, archive_vault, T).

errand(nell_quill, deliver_sealed_chart, archive_vault).
errand_not_authorization(Person, archive_vault) :- errand(Person, _, archive_vault).

% ------------------------------------------------------------------
% Council voting
% ------------------------------------------------------------------

proposal(copper_rails).
budget_matter(copper_rails).
supported(copper_rails, mara_vale).
supported(copper_rails, juno_vale).
supported(copper_rails, ilya_sen).
supported(copper_rails, tomas_reed).
support_count(copper_rails, 4).
treasurer_veto(copper_rails, sera_voss).

proposal_passes(Proposal) :-
    support_count(Proposal, Count),
    Count >= 3,
    \+ (budget_matter(Proposal), treasurer_veto(Proposal, _), \+ emergency_override(Proposal)).

proposal_fails(Proposal) :-
    support_count(Proposal, Count),
    Count >= 3,
    budget_matter(Proposal),
    treasurer_veto(Proposal, _),
    \+ emergency_override(Proposal).

% ------------------------------------------------------------------
% Tax rules
% ------------------------------------------------------------------

owes_harbor_tax(Owner, Cargo) :-
    cargo_owner(Cargo, Owner),
    cargo_value(Cargo, Value),
    Value > 100,
    \+ relief_cargo(Cargo).

tax_exempt(Cargo, relief_cargo) :- relief_cargo(Cargo).
tax_exempt(Cargo, low_value) :- cargo_value(Cargo, Value), Value =< 100.

% ------------------------------------------------------------------
% Repairs and acting authority
% ------------------------------------------------------------------

repair_order(order71, t1830).
repair_interval(order71, t1830, t1905).
signed_by(order71, mara_vale).
signed_by(order71, juno_vale).

repair_order(order72, t2015).
signed_by(order72, ilya_sen).

incapacitated_at(mara_vale, T) :- at_or_after(T, t1930).

acting_warden_for(ilya_sen, permits, T) :-
    incapacitated_at(mara_vale, T),
    absent(karel_nim, azure17),
    role(ilya_sen, archivist).

can_issue_permit(Person, T) :-
    role(Person, harbor_warden),
    \+ incapacitated_at(Person, T).
can_issue_permit(Person, T) :- acting_warden_for(Person, permits, T).

permit_issued(ilya_sen, amber_finch, docking_after_reopen, t2005).
valid_permit(amber_finch, docking_after_reopen) :-
    permit_issued(Person, amber_finch, docking_after_reopen, T),
    can_issue_permit(Person, T).

repair_authorized(Order) :-
    repair_order(Order, T),
    during_glass_tide(T),
    signed_by(Order, mara_vale),
    signed_by(Order, juno_vale).

repair_not_authorized(Order) :-
    repair_order(Order, T),
    during_glass_tide(T),
    \+ repair_authorized(Order).

archivist_cannot_substitute_for_engineer(Person) :- role(Person, archivist).

% ------------------------------------------------------------------
% Emergency priority and ovens
% ------------------------------------------------------------------

beacon_emergency_signal(t1825, hospital_burn_ward).
emergency_open_between(t1825, t2100).
emergency_open_at(T) :- between_inclusive(T, t1825, t2100).

overrides(beacon_emergency, market_deliveries) :- emergency_open_at(t1825).
overrides(beacon_emergency, charter_disputes) :- emergency_open_at(t1825).

allowed_storm_bake_target(harbor_hospital).
allowed_storm_bake_target(lighthouse).
allowed_storm_bake_target(quay_crews).

baked_for(glass_market_ovens, harbor_hospital, t2040).
requested_bake(glass_market_ovens, festival_cakes, t2100).
ordinary_market_food(festival_cakes).

baking_allowed(Target, T) :-
    storm_alarm_active_at(T),
    allowed_storm_bake_target(Target).

baking_not_allowed(Target, T) :-
    storm_alarm_active_at(T),
    \+ allowed_storm_bake_target(Target).

% ------------------------------------------------------------------
% Salvage rules
% ------------------------------------------------------------------

recovered_from_water(tomas_reed, blue_salt_crate_c17, t2110).
recovered_from_water(nell_quill, saint_loam_bell, t2125).

salvage_reward(Person, Cargo) :-
    recovered_from_water(Person, Cargo, _),
    abandoned(Cargo),
    \+ sacred(Cargo).

must_return_to_temple(Cargo) :-
    recovered_from_water(_, Cargo, _),
    sacred(Cargo).

no_salvage_reward(Person, Cargo) :-
    recovered_from_water(Person, Cargo, _),
    sacred(Cargo).

% ------------------------------------------------------------------
% Quarantine patient rules
% ------------------------------------------------------------------

quarantine_patient(dax_orr).
quarantine_patient(mira_gale).

no_fever(dax_orr, t1000).
negative_test(dax_orr, t1000).
negative_test(dax_orr, t1700).

no_fever(mira_gale, t1200).
negative_test(mira_gale, t1200).
negative_test(mira_gale, t1700).

cleared_from_quarantine(Patient) :-
    quarantine_patient(Patient),
    no_fever(Patient, FirstTime),
    negative_test(Patient, FirstTime),
    negative_test(Patient, SecondTime),
    at_least_hours_apart(FirstTime, SecondTime, 6).

not_cleared_from_quarantine(Patient) :-
    quarantine_patient(Patient),
    \+ cleared_from_quarantine(Patient).

% ------------------------------------------------------------------
% Derived summary predicates for common QA targets
% ------------------------------------------------------------------

harbor_was_closed_when(Vessel) :- vessel_arrival(Vessel, T), harbor_closed_at(T).

vessel_entry_status(Vessel, may_temporarily_dock_west_sluice) :- may_dock_at_west_sluice(Vessel).
vessel_entry_status(Vessel, must_wait_offshore) :- must_wait_offshore(Vessel).

cargo_tax_status(Cargo, owes_tax) :- cargo_owner(Cargo, Owner), owes_harbor_tax(Owner, Cargo).
cargo_tax_status(Cargo, exempt_relief) :- tax_exempt(Cargo, relief_cargo).
cargo_tax_status(Cargo, exempt_low_value) :- tax_exempt(Cargo, low_value).

archive_access_status(Person, Time, unauthorized) :- unauthorized_entry(Person, archive_vault, Time).
archive_key_status(Person, Time, revoked) :- key_revoked_at(Person, blue_key, Time).

repair_status(Order, authorized) :- repair_authorized(Order).
repair_status(Order, not_authorized) :- repair_not_authorized(Order).

patient_status(Patient, cleared) :- cleared_from_quarantine(Patient).
patient_status(Patient, not_cleared) :- not_cleared_from_quarantine(Patient).
