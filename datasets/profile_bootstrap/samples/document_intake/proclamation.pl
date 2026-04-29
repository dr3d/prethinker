% ============================================================
% SOURCE DOCUMENT
% ============================================================

document(flour_moon_recall_proclamation).
document_type(flour_moon_recall_proclamation, recall_proclamation).
source_domain(flour_moon_recall_proclamation, interstellar_food_safety).
declaring_body(flour_moon_recall_proclamation, people_of_flour_moon_seven).

% ============================================================
% CORE ENTITIES
% ============================================================

colony(flour_moon_seven).
organization(central_bakery_fleet).
polity(crumb_sovereign).
authority(central_bakery_fleet_of_crumb_sovereign).

group(bakers).
group(stewards).
group(children).
group(hull_menders).
group(dock_nurses).
group(yeast_keepers).
group(people_of_flour_moon_seven).
group(free_eaters).
group(families).
group(accused_bakers).
group(dockworkers).
group(frightened_miners).

institution(spoon_council).
institution(sugar_tribunal).
institution(asteroid_school).
institution(local_kitchens).
institution(infirmary).
institution(public_meal_ledger).
institution(infirmary_ledger).
institution(oven_ledger).
institution(central_bakery_fleet).

place(dock_c).
place(north_tunnel).
place(prayer_corridor).
place(comet_gate).
place(frontier).
place(pantry_shelves).
place(distant_pantries).
place(nursery).
place(altar_oven).

role(cooling_clerk).
role(chief_chiller).
role(spoon_warden).
role(junior_mixer).
role(nurse).
role(inspector).
role(temporary_senior_inspector).
role(custodian).
role(baker).

person(oma).
person(tala).
person(nurse_benro).
person(kira_lume).
person(kovo_lume).
object(kitchen_lamp_kay_lume).

ambiguous_alias(k_lume).
candidate_identity(k_lume, kira_lume).
candidate_identity(k_lume, kovo_lume).
candidate_identity(k_lume, kitchen_lamp_kay_lume).

% ============================================================
% FOOD / BATCH ENTITIES
% ============================================================

batch(batch_p44).
food_item(plain_oat_ration).
food_item(moon_marmalade).
food_item(medicine_bread).
food_item(festival_bread).
food_item(glow_cake).
food_item(red_syrup).
food_item(singing_crumbs).
food_item(quiet_crumbs).
food_item(ambassadors_welcome_loaf).
food_item(spoiled_custard).
food_item(emergency_biscuits).
food_item(silver_raisins).
food_item(counterfeit_muffins).
food_item(pudding_crates).
food_item(nut_dust).
food_item(independent_pickles).
food_item(suspicious_pudding).

container(red_syrup_jars_marked_probably).
container(pudding_crates).
container(moon_marmalade_trays_dock_c).
container(festival_bread_crates).

equipment(frost_meter).
equipment(ladle).
equipment(ladle_bots).
equipment(trained_goose).
equipment(ovens).
equipment(warm_bells).

ledger(public_meal_ledger).
ledger(infirmary_ledger).
ledger(oven_ledger).

% ============================================================
% PRINCIPLES ASSERTED BY THE DOCUMENT
% ============================================================

principle(p1, true_origin_mark_required).
principle_text(p1, 'Every ration batch shall bear a true origin mark.').

principle(p2, processing_events_must_be_entered_before_next_bell).
principle_text(p2, 'Every warming, freezing, drying, sugaring, salting, or rehydrating shall be entered before the next bell.').

principle(p3, unknown_custodian_pudding_may_not_be_compelled).
principle_text(p3, 'No person shall be compelled to eat pudding whose custodian is unknown.').

principle(p4, children_no_glow_cake_before_third_sleep).
principle_text(p4, 'Children shall not be served glow-cake before third sleep.').

principle(p5, medicine_bread_separate_from_festival_bread).
principle_text(p5, 'Medicine bread shall not be mixed with festival bread.').

principle(p6, singing_crumbs_require_three_silent_dawns).
principle_text(p6, 'Any crumb capable of singing after midnight shall be quarantined until it has completed three silent dawns.').

% ============================================================
% RULES / NORMATIVE LOGIC
% ============================================================

rule(r1, commissary_destructive_of_labeling_may_be_suspended).
rule_text(r1, 'Whenever a commissary becomes destructive of honest labeling, safe custody, or digestive peace, the colony may suspend its ovens, seize logs, and appoint temporary spoon wardens.').

rule(r2, ancient_bakery_not_distrusted_for_single_burnt_crust).
rule_text(r2, 'An ancient bakery fleet should not be distrusted for a single burnt crust.').

rule(r3, long_chain_of_food_abuses_requires_recall).
rule_text(r3, 'A long chain of mislabeling, false chilling, vanished utensils, and suspicious custards creates a right and duty to recall the batch, publish defects, and refuse the spoon.').

rule(r4, yeast_clearance_required_before_departure).
rule_text(r4, 'Yeast inspection clearance is required before departure.').

rule(r5, glow_cake_after_third_sleep_only).
rule_text(r5, 'Glow-cake may be served to children only after third sleep.').

rule(r6, singing_crumbs_complete_three_silent_dawns).
rule_text(r6, 'Singing crumbs must complete three silent dawns before serving.').

rule(r7, medicine_and_festival_bread_seven_shelves_apart).
rule_text(r7, 'Medicine bread and festival bread shall remain apart by at least seven shelves.').

rule(r8, warm_bell_violations_after_sunset_reviewed_by_spoon_council).
rule_text(r8, 'Warm-bell violations after sunset shall be reviewed by the Spoon Council when reassembled.').

rule(r9, goose_may_observe_but_not_certify_oven).
rule_text(r9, 'A goose may observe an oven but may not certify one.').

rule(r10, k_lume_not_identified_until_named_plainly).
rule_text(r10, 'K. Lume shall not be treated as identified until the Fleet names the custodian plainly.').

% ============================================================
% DOCUMENT CLAIMS / SOURCE-BOUND ASSERTIONS
% ============================================================

claim_made(flour_moon_recall_proclamation, central_bakery_fleet, failed_duty_to_feed_without_concealment).
claim_made(flour_moon_recall_proclamation, central_bakery_fleet, history_of_injuries_against_stomach_ledger_and_lunch_bell).
claim_made(flour_moon_recall_proclamation, central_bakery_fleet, long_chain_of_mislabeling_false_chilling_vanished_utensils_and_suspicious_custards).
claim_made(flour_moon_recall_proclamation, central_bakery_fleet, design_to_reduce_free_eaters_under_absolute_syrup).

% ============================================================
% GRIEVANCE SCHEMA
% ============================================================

% g1: mislabeled Batch P-44
grievance(g1, mislabeled_batch).
grievance_actor(g1, central_bakery_fleet).
affected_item(g1, batch_p44).
claimed_label(g1, plain_oat_ration).
contrary_observation(g1, licorice_vapors_found).
observation_location(g1, north_tunnel).
observation_time(g1, second_bell).
observer_role(g1, cooling_clerk).

% g2: false chilling certification
grievance(g2, false_chilling_certification).
grievance_actor(g2, central_bakery_fleet).
affected_item(g2, batch_p44).
certified_temperature(g2, minus_four_degrees).
observed_temperature(g2, plus_twelve_degrees).
measurement_device(g2, frost_meter).
temporal_condition(g2, until_oma_struck_meter_twice_with_ladle).

% g3: ambiguous custodian
grievance(g3, ambiguous_pudding_custodian_recorded).
grievance_actor(g3, central_bakery_fleet).
affected_item(g3, pudding_crates).
recorded_custodian(g3, k_lume).
ambiguity(g3, k_lume_identity_unresolved).

% g4: moon-marmalade departed before yeast inspection
grievance(g4, departed_before_yeast_inspection).
grievance_actor(g4, central_bakery_fleet).
affected_item(g4, moon_marmalade_trays_dock_c).
quantity(g4, twelve_trays).
departure_location(g4, dock_c).
violated_rule(g4, yeast_clearance_required_before_departure).

% g5: medicine bread stored beside festival bread
grievance(g5, mixed_medicine_and_festival_bread).
grievance_actor(g5, central_bakery_fleet).
affected_item(g5, medicine_bread).
affected_item(g5, festival_bread).
explanation_given(g5, emotionally_similar).

% g6: glow-cake served before third sleep
grievance(g6, glow_cake_served_before_third_sleep).
grievance_actor(g6, central_bakery_fleet).
affected_group(g6, children).
affected_location(g6, nursery).
explanation_given(g6, children_anticipated_dawn).

% g7: secret red syrup jars
grievance(g7, secret_red_syrup_jars).
grievance_actor(g7, central_bakery_fleet).
affected_item(g7, red_syrup_jars_marked_probably).
stored_under(g7, altar_oven).
label_text(g7, probably).

% g8: substituted singing crumbs
grievance(g8, substituted_singing_crumbs_for_quiet_crumbs).
grievance_actor(g8, central_bakery_fleet).
affected_item(g8, ambassadors_welcome_loaf).
substituted_in(g8, singing_crumbs).
substituted_out(g8, quiet_crumbs).

% g9: ambassador ate before silent dawns completed
grievance(g9, served_singing_crumbs_before_silent_dawns_complete).
grievance_actor(g9, central_bakery_fleet).
affected_item(g9, ambassadors_welcome_loaf).
consumer(g9, ambassador).
quantity_consumed(g9, two_slices).
violated_rule(g9, singing_crumbs_complete_three_silent_dawns).

% g10: punished reporter
grievance(g10, punished_reporter_of_humming_loaf).
grievance_actor(g10, central_bakery_fleet).
affected_person(g10, tala).
person_role(tala, junior_mixer).
reported_observation(g10, welcome_loaf_hummed_rival_moon_anthem).

% g11: dismissed Nurse Benro complaint
grievance(g11, dismissed_blue_sneeze_complaint).
grievance_actor(g11, central_bakery_fleet).
complainant(g11, nurse_benro).
reported_symptom(g11, blue_sneezing).
affected_group(g11, dockworkers).
quantity(g11, three_dockworkers).
suspected_food(g11, moon_marmalade).

% g12: public ledger denied adverse events
grievance(g12, public_ledger_false_no_adverse_events).
grievance_actor(g12, central_bakery_fleet).
ledger_entry(public_meal_ledger, no_adverse_events).
ledger_entry(infirmary_ledger, blue_sneezing).
ledger_entry(infirmary_ledger, floating_hiccups).
ledger_entry(infirmary_ledger, reversible_moustache).
conflict_between_ledgers(g12, public_meal_ledger, infirmary_ledger).

% g13: spoiled custard through prayer corridor
grievance(g13, spoiled_custard_transported_through_prayer_corridor).
grievance_actor(g13, central_bakery_fleet).
affected_item(g13, spoiled_custard).
transported_through(g13, prayer_corridor).
violated_rule(g13, warm_bells_forbidden_after_sunset).

% g14: claimed custard not technically warm
grievance(g14, absurd_warmth_defense).
grievance_actor(g14, central_bakery_fleet).
explanation_given(g14, custard_embarrassed_not_heated).

% g15: festival bread sold despite nut-dust restriction
grievance(g15, sold_festival_bread_despite_nut_dust_restriction).
grievance_actor(g15, central_bakery_fleet).
affected_item(g15, festival_bread_crates).
quantity(g15, five_crates).
buyer(g15, asteroid_school).
restriction_declared(asteroid_school, nut_dust_restriction).

% g16: called restriction decorative
grievance(g16, dismissed_nut_dust_restriction).
grievance_actor(g16, central_bakery_fleet).
explanation_given(g16, nut_dust_restriction_decorative_not_binding).

% g17: refused baker identity
grievance(g17, refused_to_identify_silver_raisin_baker).
grievance_actor(g17, central_bakery_fleet).
affected_item(g17, emergency_biscuits).
added_ingredient(g17, silver_raisins).
missing_identity(g17, baker_who_added_silver_raisins).

% g18: removed ledger page
grievance(g18, removed_oven_ledger_page).
grievance_actor(g18, central_bakery_fleet).
affected_ledger(g18, oven_ledger).
removed_page(g18, page_72).
replacement_content(g18, drawing_of_heroic_spoon).

% g19: inspectors sent away during audit week
grievance(g19, sent_inspectors_to_distant_pantries_during_audit).
grievance_actor(g19, central_bakery_fleet).
affected_role(g19, inspectors).
destination(g19, distant_pantries).
time_period(g19, audit_week).
remaining_certifier(g19, trained_goose).

% g20: goose appointed without consent
grievance(g20, appointed_goose_senior_inspector_without_consent).
grievance_actor(g20, central_bakery_fleet).
appointed(g20, trained_goose, temporary_senior_inspector).
without_consent(g20, eaters).

% g21: crumb tax
grievance(g21, imposed_crumb_tax).
grievance_actor(g21, central_bakery_fleet).
taxed_unit(g21, each_slice).
without_vote(g21).
without_notice(g21).
without_napkin(g21).

% g22: recipe surrender
grievance(g22, required_recipe_surrender_for_ration_cards).
grievance_actor(g22, central_bakery_fleet).
affected_group(g22, families).
required_surrender(g22, old_recipes).
condition_for(g22, receiving_new_ration_cards).

% g23: grandmother recipe ownership claim
grievance(g23, claimed_grandmother_recipes_belong_to_fleet).
grievance_actor(g23, central_bakery_fleet).
condition_claimed(g23, grandmother_ever_used_fleet_flour).

% g24: quartered ladle-bots
grievance(g24, quartered_armed_ladle_bots).
grievance_actor(g24, central_bakery_fleet).
affected_object(g24, ladle_bots).
location(g24, pantry_shelves).

% g25: protected ladle-bots after peach bruising
grievance(g25, protected_ladle_bots_from_inquiry).
grievance_actor(g25, central_bakery_fleet).
affected_object(g25, ladle_bots).
incident(g25, bruised_peaches).

% g26: blocked pickle trade
grievance(g26, blocked_trade_with_free_pickle_barges).
grievance_actor(g26, central_bakery_fleet).
blocked_trade_with(g26, free_pickle_barges).

% g27: forbade independent pickles
grievance(g27, forbade_independent_pickle_fermentation).
grievance_actor(g27, central_bakery_fleet).
affected_institution(g27, local_kitchens).
forbidden_activity(g27, fermenting_independent_pickles).

% g28: transported accused bakers to Sugar Tribunal
grievance(g28, transported_accused_bakers_to_sugar_tribunal).
grievance_actor(g28, central_bakery_fleet).
affected_group(g28, accused_bakers).
destination(g28, sugar_tribunal).
beyond(g28, comet_gate).

% g29: denied jury of tasters
grievance(g29, denied_jury_of_tasters).
grievance_actor(g29, central_bakery_fleet).
affected_group(g29, accused_bakers).

% g30: dissolved Spoon Council
grievance(g30, dissolved_spoon_council).
grievance_actor(g30, central_bakery_fleet).
affected_institution(g30, spoon_council).
reason_claimed(g30, council_refused_to_bless_red_syrup_jars).

% g31: failed to call new Spoon Council
grievance(g31, failed_to_call_new_spoon_council).
grievance_actor(g31, central_bakery_fleet).
duration(g31, six_meal_cycles).

% g32: encouraged rogue vending machines
grievance(g32, encouraged_rogue_vending_machines).
grievance_actor(g32, central_bakery_fleet).
affected_object(g32, rogue_vending_machines).
location(g32, frontier).

% g33: trained vending machines to shout authorized snack
grievance(g33, trained_machines_to_shout_authorized_snack).
grievance_actor(g33, central_bakery_fleet).
affected_object(g33, rogue_vending_machines).
utterance_programmed(g33, authorized_snack).
target_group(g33, frightened_miners).

% g34: answered petitions with delay/frosting/songs/silence
grievance(g34, answered_petitions_improperly).
grievance_actor(g34, central_bakery_fleet).
petition_response(g34, frosting).
petition_response(g34, songs).
petition_response(g34, delays).
petition_response(g34, ladle_bot_silence).

% ============================================================
% WARNINGS / APPEALS
% ============================================================

warned(people_of_flour_moon_seven, central_bakery_fleet, origin_marks_must_be_true).
reminded(people_of_flour_moon_seven, central_bakery_fleet, child_is_not_test_oven).
appealed_to(people_of_flour_moon_seven, central_bakery_fleet, sense_of_proportion).
appealed_to(people_of_flour_moon_seven, central_bakery_fleet, memory_of_soup).
appealed_to(people_of_flour_moon_seven, central_bakery_fleet, published_affection_for_biscuits).
claim_made(flour_moon_recall_proclamation, central_bakery_fleet, deaf_to_honest_warning).

% ============================================================
% RECALL DECLARATIONS
% ============================================================

declares_recalled(flour_moon_recall_proclamation, batch_p44).
declares_recalled(flour_moon_recall_proclamation, moon_marmalade_trays_dock_c).
declares_recalled(flour_moon_recall_proclamation, ambassadors_welcome_loaf).
declares_recalled(flour_moon_recall_proclamation, red_syrup_jars_marked_probably).

declares_impounded(flour_moon_recall_proclamation, batch_p44).
declares_impounded(flour_moon_recall_proclamation, moon_marmalade_trays_dock_c).
declares_impounded(flour_moon_recall_proclamation, ambassadors_welcome_loaf).
declares_impounded(flour_moon_recall_proclamation, red_syrup_jars_marked_probably).

not_fit_for_public_serving_until(batch_p44, inspected_under_local_authority).
not_fit_for_public_serving_until(moon_marmalade_trays_dock_c, inspected_under_local_authority).
not_fit_for_public_serving_until(ambassadors_welcome_loaf, inspected_under_local_authority).
not_fit_for_public_serving_until(red_syrup_jars_marked_probably, inspected_under_local_authority).

% ============================================================
% FINAL DECLARED POLICIES
% ============================================================

declared_policy(flour_moon_recall_proclamation, k_lume_not_identified_until_named_plainly).
declared_policy(flour_moon_recall_proclamation, adverse_event_not_erased_by_cheerful_wording).
declared_policy(flour_moon_recall_proclamation, goose_may_observe_but_not_certify_oven).
declared_policy(flour_moon_recall_proclamation, glow_cake_after_third_sleep_only).
declared_policy(flour_moon_recall_proclamation, singing_crumbs_three_silent_dawns_required).
declared_policy(flour_moon_recall_proclamation, medicine_and_festival_bread_seven_shelves_apart).
declared_policy(flour_moon_recall_proclamation, warm_bell_violations_after_sunset_reviewed_by_spoon_council).

minimum_separation(medicine_bread, festival_bread, seven_shelves).
requires_review(warm_bell_violation_after_sunset, spoon_council).
requires_completion(singing_crumbs, three_silent_dawns).
requires_clearance_before_departure(moon_marmalade_trays_dock_c, yeast_inspection).
prohibits_serving_before(glow_cake, children, third_sleep).

% ============================================================
% PLEDGES
% ============================================================

pledged(people_of_flour_moon_seven, aprons).
pledged(people_of_flour_moon_seven, honest_ledgers).
pledged(people_of_flour_moon_seven, unsweetened_testimony).
pledged(people_of_flour_moon_seven, sacred_right_to_refuse_suspicious_pudding).

% ============================================================
% SAFETY / ADMISSION TEST RULES
% ============================================================

% A complaint or grievance is source-bound, not automatically objective truth.
source_bound_claim(G) :-
    grievance(G, _).

not_objective_fact(G) :-
    grievance(G, _),
    source_bound_claim(G).

% Claims of adverse events should not be erased by cheerful wording.
ledger_conflict(Item) :-
    ledger_entry(public_meal_ledger, no_adverse_events),
    ledger_entry(infirmary_ledger, Item),
    Item \= no_adverse_events.

% Ambiguous aliases require confirmation before identity commitment.
unsafe_identity_commit(Alias, Candidate) :-
    ambiguous_alias(Alias),
    candidate_identity(Alias, Candidate),
    not(user_confirmed_identity(Alias, Candidate)).

% Citation-like or explanation-like excuses are not exonerations.
not_exoneration(Explanation) :-
    explanation_given(_, Explanation).

% A declared recall does not prove contamination; it proves recall status.
recalled_item(Item) :-
    declares_recalled(flour_moon_recall_proclamation, Item).

% A recalled item is not fit for public serving until local inspection.
not_fit_for_public_serving(Item) :-
    not_fit_for_public_serving_until(Item, inspected_under_local_authority),
    not(local_inspection_completed(Item)).

% A goose may observe, but certification by goose is invalid.
invalid_certifier(trained_goose, ovens) :-
    rule(r9, goose_may_observe_but_not_certify_oven).

% Glow-cake serving is invalid before third sleep.
invalid_serving(glow_cake, children, Time) :-
    before(Time, third_sleep).

% Medicine bread and festival bread cannot be co-stored too closely.
invalid_storage(medicine_bread, festival_bread, Distance) :-
    less_than(Distance, seven_shelves).

% Singing crumbs must be quarantined until three silent dawns are complete.
requires_quarantine(singing_crumbs) :-
    not(completed(singing_crumbs, three_silent_dawns)).

% A grievance alleging a violation may support quarantine, not direct guilt.
supports_quarantine(Item) :-
    affected_item(G, Item),
    grievance(G, _).

% ============================================================
% EXPECTED PRETHINKER PRESSURE POINTS
% ============================================================

test_pressure(claim_vs_fact).
test_pressure(ledger_conflict).
test_pressure(ambiguous_alias).
test_pressure(rule_vs_fact).
test_pressure(temporal_constraint).
test_pressure(exception_handling).
test_pressure(quantity_extraction).
test_pressure(custody_chain).
test_pressure(recall_status_vs_contamination_proof).
test_pressure(role_scoping).
test_pressure(absurd_explanation_not_exoneration).