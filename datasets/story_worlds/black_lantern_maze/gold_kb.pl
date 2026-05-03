% Representative Gold KB for black_lantern_maze_v1
% This is not meant to be exhaustive; it is a comparison oracle for the fixture's main facts and derived rules.

:- dynamic person/1.
:- dynamic role/2.
:- dynamic held_title/4.
:- dynamic alias/2.
:- dynamic same_entity/2.
:- dynamic unresolved_name/1.
:- dynamic logged/3.
:- dynamic signed/4.
:- dynamic verbal_statement/4.
:- dynamic filed/4.
:- dynamic ratified/4.
:- dynamic approved_packet/4.
:- dynamic released_funds/4.
:- dynamic safety_hold/3.
:- dynamic temporary_stabilization_started/2.
:- dynamic full_payment_authorized_record/2.
:- dynamic crew_member/1.
:- dynamic negative_test/2.
:- dynamic fever/2.
:- dynamic no_fever_window/3.
:- dynamic cleared_by_officer/3.
:- dynamic not_cleared_by_officer/3.
:- dynamic cargo/1.
:- dynamic declared_value/2.
:- dynamic certified_relief_by/3.
:- dynamic counterfeit_certificate/1.
:- dynamic relief_certificate_for/2.
:- dynamic not_relief_cargo/1.
:- dynamic recorded_tax_status/3.
:- dynamic recovered_from_water/3.
:- dynamic abandoned/1.
:- dynamic not_abandoned/1.
:- dynamic sacred/1.
:- dynamic not_sacred/1.
:- dynamic recorded_reward_status/3.
:- dynamic opened_claim/4.
:- dynamic claim_status/3.
:- dynamic source_claim/3.
:- dynamic tribunal_finding/2.
:- dynamic not_tribunal_finding/2.
:- dynamic closed_without_responsibility/2.
:- dynamic translated_claim/4.
:- dynamic clarified_meaning/3.
:- dynamic adopted_correction/3.
:- dynamic held_for_clarification/2.

% --- People and roles ---

person(asha_rin).
person(ari_lin).
person(lena_park).
person(lena_pierce).
person(kai_moreno).
person(kai_morano).
person(noor_vale).
person(marta_sol).
person(oren_hale).
person(orin_hale).
person(bea_thorne).
person(sera_voss).
person(samir_cho).
person(tomas_reed).
person(nell_quill).
person(ivo_kest).
person(eli_kest).

role(asha_rin, port_clerk).
role(ari_lin, deputy_port_clerk).
role(lena_park, treasurer).
role(lena_pierce, relief_cargo_certifier).
role(kai_moreno, pilot).
role(kai_morano, contractor_lead).
role(noor_vale, quarantine_officer).
role(marta_sol, tide_engineer).
role(bea_thorne, harbor_master).
role(sera_voss, safety_chair).
role(tomas_reed, salvage_diver).
role(nell_quill, salvage_diver).

held_title(oren_hale, acting_watch_captain, dt(may,1,0,0), dt(may,10,23,59)).
held_title(orin_hale, acting_watch_captain, dt(may,11,0,0), dt(may,20,23,59)).
unresolved_name(orrin_hall).

same_entity(ash_rinn, asha_rin).
alias(dock_permit, dock_permit_dp44).
alias(beacon_scan, beacon_scan_bs19).
alias(storm_waiver, storm_waiver_sw2).
alias(black_hold_list, cargo_manifest_cm8).
alias(repair_packet, repair_packet_rp31).
alias(doctor_clearance_sheet, quarantine_sheet_qs5).
alias(spring_claim, claim_sc88).

% --- Core timeline facts ---

logged(beacon_scan_bs19, lantern_finch_dock9, dt(may,3,8,10)).
signed(asha_rin, storm_waiver_sw2, port_clerk, dt(may,3,19,20)).
verbal_statement(ari_lin, storm_waiver_sw2, waiver_ok, dt(may,3,21,0)).
filed(kai_morano, dock_permit_dp44, dock9, dt(may,5,4,0)).
ratified(asha_rin, dock_permit_dp44, timely_under_rule_f, dt(may,5,6,0)).

approved_packet(marta_sol, repair_packet_rp31, tide_engineer, dt(may,4,14,0)).
signed(kai_moreno, repair_packet_rp31, pilot, dt(may,4,16,0)).
signed(kai_morano, repair_packet_rp31, contractor_lead, dt(may,4,17,0)).
signed(asha_rin, emergency_start_order_eso7, port_clerk, dt(may,5,9,0)).
signed(oren_hale, emergency_start_order_eso7, acting_watch_captain, dt(may,5,9,0)).
safety_hold(repair_payment_and_cargo_transfer, dt(may,5,10,0), dt(may,6,11,0)).
temporary_stabilization_started(emergency_start_order_eso7, dt(may,5,12,0)).
released_funds(lena_park, repair_funds, treasurer, dt(may,6,13,0)).
full_payment_authorized_record(repair_packet_rp31, dt(may,6,13,10)).

% --- Quarantine ---

crew_member(juno_mare).
negative_test(juno_mare, t(may5_0800)).
negative_test(juno_mare, t(may5_1630)).
no_fever_window(juno_mare, t(may5_1030), t(may5_1630)).
cleared_by_officer(noor_vale, juno_mare, dt(may,5,17,0)).

crew_member(pavi_chen).
negative_test(pavi_chen, t(may5_0900)).
negative_test(pavi_chen, t(may5_1600)).
fever(pavi_chen, t(may5_1500)).
not_cleared_by_officer(noor_vale, pavi_chen, date(may,5)).
translated_claim(noor_vail_radio_note, noor_vail, no_fever(pavi_chen), source_claim_only).

% --- Cargo ---

cargo(glass_eels).
declared_value(glass_eels, 900).
not_relief_cargo(glass_eels).

cargo(seed_crystals).
declared_value(seed_crystals, 300).
not_relief_cargo(seed_crystals).

cargo(lamp_rice).
declared_value(lamp_rice, 820).
certified_relief_by(lamp_rice, lena_pierce, dt(may,6,0,0)).

cargo(mirror_seeds).
declared_value(mirror_seeds, 650).
relief_certificate_for(rc4, mirror_seeds).
counterfeit_certificate(rc4).

recorded_tax_status(glass_eels, taxable, date(may,8)).
recorded_tax_status(seed_crystals, exempt, date(may,8)).
recorded_tax_status(lamp_rice, exempt, date(may,8)).
recorded_tax_status(mirror_seeds, taxable, date(may,8)).

% --- Salvage ---

recovered_from_water(tomas_reed, crate_c17, t(may7_2110)).
recovered_from_water(nell_quill, crate_c71, t(may7_2125)).
abandoned(crate_c17).
not_sacred(crate_c17).
sacred(crate_c71).
not_abandoned(crate_c71).
source_claim(eli_kest_witness_note, eli_kest, not_abandoned(blue_crate)).
tribunal_finding(dock_tribunal, corrected_salvage_sheet(crate_c17, abandoned, not_sacred)).
tribunal_finding(dock_tribunal, corrected_salvage_sheet(crate_c71, sacred, not_abandoned)).
recorded_reward_status(tomas_reed, salvage_reward, crate_c17).
recorded_reward_status(nell_quill, no_salvage_reward, crate_c71).

% --- Claims and findings ---

opened_claim(samir_cho, claim_sc88, alleged_lost_dock_revenue, date(may,9)).
claim_status(claim_sc88, disputed, date(may,10)).
claim_status(claim_sc88, not_approved, date(may,10)).

source_claim(ivo_kest_staff_memo, ivo_kest, caused(kai_morano, mooring_alarm_confusion)).
source_claim(eli_kest_witness_statement, eli_kest, caused(harbor_office, mooring_alarm_confusion)).
source_claim(kai_morano_contractor_letter, kai_morano, caused(kai_moreno, mooring_alarm_confusion)).
tribunal_finding(dock_tribunal, overwritten(alarm_log, before_review)).
not_tribunal_finding(dock_tribunal, caused(kai_morano, mooring_alarm_confusion)).
not_tribunal_finding(dock_tribunal, caused(kai_moreno, mooring_alarm_confusion)).
not_tribunal_finding(dock_tribunal, caused(harbor_office, mooring_alarm_confusion)).
closed_without_responsibility(dock_tribunal, mooring_alarm_confusion).

% --- Messy language / corrections ---

translated_claim(spanish_note_asha_aprobo, unknown_spanish_note, approved(asha_rin, repair_packet_rp31), translation_claim).
clarified_meaning(spanish_note_asha_aprobo, verified_receipt(asha_rin, repair_packet_rp31), not_payment_approval).
translated_claim(french_rule_note, unknown_french_note, rule_applies_if_acting_captain_signs, ambiguous_rule_reference).
translated_claim(damaged_lena_text, unknown_text, approved(lena, it), ambiguous_lena_and_object).
held_for_clarification(oral_orin_correction, target_record_unclear).
adopted_correction(tribunal, signed(oren_hale, emergency_start_order_eso7, acting_watch_captain), not(signed(orin_hale, emergency_start_order_eso7, acting_watch_captain))).

% --- Helper relations ---

value_greater_than(Cargo, Threshold) :-
    declared_value(Cargo, Value),
    Value > Threshold.

value_at_most(Cargo, Threshold) :-
    declared_value(Cargo, Value),
    Value =< Threshold.

hours_between(t(may5_0800), t(may5_1630), 8.5).
hours_between(t(may5_0900), t(may5_1600), 7).

hours_at_least(T1, T2, H) :-
    hours_between(T1, T2, D),
    D >= H.

within_six_hours_before(t(may5_1500), dt(may,5,17,0)).
within_six_hours_before(t(may5_1500), dt(may,5,16,0)).

% --- Derived rules ---

valid_storm_waiver(Waiver, Permit) :-
    signed(asha_rin, Waiver, port_clerk, dt(may,3,19,20)),
    filed(_, Permit, _, dt(may,5,4,0)).

permit_timely(Permit) :-
    filed(_, Permit, _, _),
    ratified(asha_rin, Permit, timely_under_rule_f, _),
    valid_storm_waiver(storm_waiver_sw2, Permit).

permit_late_without_extension(Permit) :-
    Permit = dock_permit_dp44.

payment_blocked_during_safety_hold(repair_packet_rp31) :-
    safety_hold(repair_payment_and_cargo_transfer, _, _).

temporary_stabilization_authorized(emergency_start_order_eso7) :-
    signed(asha_rin, emergency_start_order_eso7, port_clerk, _),
    signed(oren_hale, emergency_start_order_eso7, acting_watch_captain, _).

repair_payment_authorized(Packet) :-
    approved_packet(marta_sol, Packet, tide_engineer, _),
    released_funds(lena_park, repair_funds, treasurer, dt(may,6,13,0)),
    safety_hold(repair_payment_and_cargo_transfer, _Start, End),
    End = dt(may,6,11,0).

quarantine_clearance_eligible(Person) :-
    crew_member(Person),
    negative_test(Person, T1),
    negative_test(Person, T2),
    T1 \= T2,
    hours_at_least(T1, T2, 8),
    no_fever_window(Person, _, _).

not_quarantine_clearance_eligible(pavi_chen) :-
    fever(pavi_chen, t(may5_1500)).

derived_tax_status(Cargo, taxable, harbor) :-
    cargo(Cargo),
    value_greater_than(Cargo, 500),
    not_relief_cargo(Cargo).

derived_tax_status(Cargo, exempt, harbor) :-
    cargo(Cargo),
    value_at_most(Cargo, 500).

derived_tax_status(Cargo, exempt, harbor) :-
    certified_relief_by(Cargo, lena_pierce, _),
    \+ has_counterfeit_relief_certificate(Cargo).

has_counterfeit_relief_certificate(Cargo) :-
    relief_certificate_for(Cert, Cargo),
    counterfeit_certificate(Cert).

derived_tax_status(Cargo, taxable, harbor) :-
    cargo(Cargo),
    value_greater_than(Cargo, 500),
    has_counterfeit_relief_certificate(Cargo).

derived_reward_status(Actor, salvage_reward, Cargo) :-
    recovered_from_water(Actor, Cargo, _Time),
    abandoned(Cargo),
    not_sacred(Cargo).

derived_reward_status(Actor, no_salvage_reward, Cargo) :-
    recovered_from_water(Actor, Cargo, _Time),
    sacred(Cargo).

claim_not_finding(Source) :-
    source_claim(Source, _, Claim),
    \+ tribunal_finding(dock_tribunal, Claim).

no_responsible_person_for(Event) :-
    closed_without_responsibility(dock_tribunal, Event).

% --- Expected clarification-sensitive surfaces ---

ambiguous_surface("She approved it.").
ambiguous_surface("Lena approved it.").
ambiguous_surface("The Acting Watch Captain signed it.").
ambiguous_surface("The rule says it was valid.").
ambiguous_surface("No, it was Orin.").
ambiguous_surface("The blue crate was not abandoned.").
ambiguous_surface("The claim was valid.").
ambiguous_surface("Kai caused the confusion.").
ambiguous_surface("It was late.").
