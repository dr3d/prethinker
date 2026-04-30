/* ============================================================
   THE THREE OTTERS AND THE CLOCKWORK PIE
   Complete Prolog Knowledge Base
   ============================================================ */

:- discontiguous entity/1.
:- discontiguous kind/2.
:- discontiguous character/1.
:- discontiguous object/1.
:- discontiguous place/1.
:- discontiguous food/1.
:- discontiguous event/5.
:- discontiguous story_time/2.
:- discontiguous causes/2.
:- discontiguous caused_by/2.
:- discontiguous judged/4.
:- discontiguous said/3.


/* ============================================================
   CORE CHARACTERS
   ============================================================ */

entity(little_slip_otter).
entity(middle_sized_otter).
entity(great_long_otter).
entity(tilly_tumbletop).
entity(tillys_aunt).

character(little_slip_otter).
character(middle_sized_otter).
character(great_long_otter).
character(tilly_tumbletop).
character(tillys_aunt).

kind(little_slip_otter, otter).
kind(middle_sized_otter, otter).
kind(great_long_otter, otter).
kind(tilly_tumbletop, human_child).
kind(tillys_aunt, human_adult).

otter(little_slip_otter).
otter(middle_sized_otter).
otter(great_long_otter).

human(tilly_tumbletop).
human(tillys_aunt).

name(little_slip_otter, "Little Slip of an Otter").
name(middle_sized_otter, "Middle-sized Otter").
name(great_long_otter, "Great Long Otter").
name(tilly_tumbletop, "Tilly Tumbletop").
name(tillys_aunt, "Tilly's aunt").

size(little_slip_otter, little).
size(middle_sized_otter, middle).
size(great_long_otter, great).

voice_size(little_slip_otter, squeaky_little_voice).
voice_size(middle_sized_otter, middle_sized_voice).
voice_size(great_long_otter, great_long_voice).

trait(little_slip_otter, tidy_as_otters_go).
trait(middle_sized_otter, tidy_as_otters_go).
trait(great_long_otter, tidy_as_otters_go).

trait(little_slip_otter, hospitable).
trait(middle_sized_otter, hospitable).
trait(great_long_otter, hospitable).

trait(tilly_tumbletop, curious).
trait(tilly_tumbletop, unpolished).
trait(tilly_tumbletop, rubbed_about_at_the_edges).
trait(tilly_tumbletop, distractible).
trait(tilly_tumbletop, mischievous).
trait(tilly_tumbletop, capable_of_apology).

household(three_otter_household).
household_member(three_otter_household, little_slip_otter).
household_member(three_otter_household, middle_sized_otter).
household_member(three_otter_household, great_long_otter).


/* ============================================================
   PLACES
   ============================================================ */

entity(willow_root_house).
entity(willow_tree).
entity(bright_running_river).
entity(wood).
entity(kitchen).
entity(windowsill).
entity(round_window).
entity(chimney_hole).
entity(front_door).
entity(pantry).
entity(rain_barrel).
entity(floor).
entity(table).
entity(mat).
entity(stool).
entity(riverbank).
entity(puddle).

place(willow_root_house).
place(willow_tree).
place(bright_running_river).
place(wood).
place(kitchen).
place(windowsill).
place(round_window).
place(chimney_hole).
place(front_door).
place(pantry).
place(rain_barrel).
place(floor).
place(table).
place(mat).
place(stool).
place(riverbank).
place(puddle).

kind(willow_root_house, house).
kind(willow_tree, tree).
kind(bright_running_river, river).
kind(wood, forest).
kind(kitchen, room).
kind(windowsill, part_of_house).
kind(round_window, window).
kind(chimney_hole, opening).
kind(front_door, door).
kind(pantry, room).
kind(rain_barrel, container).
kind(floor, house_surface).
kind(table, furniture).
kind(mat, floor_covering).
kind(stool, furniture).
kind(riverbank, outdoor_place).
kind(puddle, water_on_floor).

located_in(willow_root_house, wood).
under(willow_root_house, willow_tree).
near(willow_root_house, bright_running_river).
part_of(kitchen, willow_root_house).
part_of(windowsill, willow_root_house).
part_of(round_window, willow_root_house).
part_of(chimney_hole, willow_root_house).
part_of(front_door, willow_root_house).
part_of(pantry, willow_root_house).
part_of(floor, willow_root_house).

lives_at(little_slip_otter, willow_root_house).
lives_at(middle_sized_otter, willow_root_house).
lives_at(great_long_otter, willow_root_house).

description(willow_root_house, snug).
description(bright_running_river, bright).
description(bright_running_river, running).


/* ============================================================
   HOUSEHOLD OBJECTS
   ============================================================ */

entity(little_mug).
entity(middle_mug).
entity(great_mug).

entity(little_boots).
entity(middle_boots).
entity(great_boots).

entity(little_boat).
entity(middle_boat).
entity(great_boat).

entity(little_knife).
entity(middle_knife).
entity(great_knife).

object(little_mug).
object(middle_mug).
object(great_mug).
object(little_boots).
object(middle_boots).
object(great_boots).
object(little_boat).
object(middle_boat).
object(great_boat).
object(little_knife).
object(middle_knife).
object(great_knife).

kind(little_mug, mug).
kind(middle_mug, mug).
kind(great_mug, mug).

kind(little_boots, boots).
kind(middle_boots, boots).
kind(great_boots, boots).

kind(little_boat, boat).
kind(middle_boat, boat).
kind(great_boat, boat).

kind(little_knife, knife).
kind(middle_knife, knife).
kind(great_knife, knife).

size(little_mug, little).
size(middle_mug, middle).
size(great_mug, great).

size(little_boots, little).
size(middle_boots, middle).
size(great_boots, great).

size(little_boat, little).
size(middle_boat, middle).
size(great_boat, great).

size(little_knife, little).
size(middle_knife, middle).
size(great_knife, great).

owned_by(little_mug, little_slip_otter).
owned_by(middle_mug, middle_sized_otter).
owned_by(great_mug, great_long_otter).

owned_by(little_boots, little_slip_otter).
owned_by(middle_boots, middle_sized_otter).
owned_by(great_boots, great_long_otter).

owned_by(little_boat, little_slip_otter).
owned_by(middle_boat, middle_sized_otter).
owned_by(great_boat, great_long_otter).

owned_by(little_knife, little_slip_otter).
owned_by(middle_knife, middle_sized_otter).
owned_by(great_knife, great_long_otter).

designed_for(little_mug, little_slip_otter).
designed_for(middle_mug, middle_sized_otter).
designed_for(great_mug, great_long_otter).

designed_for(little_boots, little_slip_otter).
designed_for(middle_boots, middle_sized_otter).
designed_for(great_boots, great_long_otter).

designed_for(little_boat, little_slip_otter).
designed_for(middle_boat, middle_sized_otter).
designed_for(great_boat, great_long_otter).

initial_location(little_mug, willow_root_house).
initial_location(middle_mug, willow_root_house).
initial_location(great_mug, willow_root_house).

initial_location(little_boots, willow_root_house).
initial_location(middle_boots, willow_root_house).
initial_location(great_boots, willow_root_house).

initial_location(little_boat, rain_barrel).
initial_location(middle_boat, rain_barrel).
initial_location(great_boat, rain_barrel).

initial_location(little_knife, kitchen).
initial_location(middle_knife, kitchen).
initial_location(great_knife, kitchen).


/* ============================================================
   PIE, INGREDIENTS, AND FOOD
   ============================================================ */

entity(clockwork_pie).
entity(ordinary_pie).
entity(great_pie_slice).
entity(middle_pie_slice).
entity(little_pie_slice).

entity(apples).
entity(moon_sugar).
entity(brass_wheel_1).
entity(brass_wheel_2).
entity(brass_wheel_3).
entity(brass_wheel_4).
entity(brass_wheel_5).
entity(brass_wheel_6).
entity(pie_key).
entity(raisins).

food(clockwork_pie).
food(ordinary_pie).
food(great_pie_slice).
food(middle_pie_slice).
food(little_pie_slice).
food(apples).
food(moon_sugar).
food(raisins).

object(brass_wheel_1).
object(brass_wheel_2).
object(brass_wheel_3).
object(brass_wheel_4).
object(brass_wheel_5).
object(brass_wheel_6).
object(pie_key).

kind(clockwork_pie, pie).
kind(ordinary_pie, pie).
kind(great_pie_slice, pie_slice).
kind(middle_pie_slice, pie_slice).
kind(little_pie_slice, pie_slice).

kind(apples, ingredient).
kind(moon_sugar, ingredient).
kind(raisins, ingredient).

kind(brass_wheel_1, brass_wheel).
kind(brass_wheel_2, brass_wheel).
kind(brass_wheel_3, brass_wheel).
kind(brass_wheel_4, brass_wheel).
kind(brass_wheel_5, brass_wheel).
kind(brass_wheel_6, brass_wheel).
kind(pie_key, key).

ingredient_of(apples, clockwork_pie).
ingredient_of(moon_sugar, clockwork_pie).
ingredient_of(brass_wheel_1, clockwork_pie).
ingredient_of(brass_wheel_2, clockwork_pie).
ingredient_of(brass_wheel_3, clockwork_pie).
ingredient_of(brass_wheel_4, clockwork_pie).
ingredient_of(brass_wheel_5, clockwork_pie).
ingredient_of(brass_wheel_6, clockwork_pie).

contains_before_eating(little_pie_slice, brass_wheel_1).
contains_before_eating(little_pie_slice, brass_wheel_2).
contains_before_eating(little_pie_slice, brass_wheel_3).
contains_before_eating(little_pie_slice, brass_wheel_4).
contains_before_eating(little_pie_slice, brass_wheel_5).
contains_before_eating(little_pie_slice, brass_wheel_6).

portion_of(great_pie_slice, clockwork_pie).
portion_of(middle_pie_slice, clockwork_pie).
portion_of(little_pie_slice, clockwork_pie).

size(great_pie_slice, great).
size(middle_pie_slice, middle).
size(little_pie_slice, little).

property(clockwork_pie, ticking).
property(clockwork_pie, clockwork).
property(clockwork_pie, magical_or_whimsical).
property(clockwork_pie, breakfast_food).
property(clockwork_pie, half_birthday_food).

owned_by(clockwork_pie, three_otter_household).
owned_by(ordinary_pie, three_otter_household).

occasion(little_slip_otter_half_birthday).
honoree(little_slip_otter_half_birthday, little_slip_otter).
served_for(clockwork_pie, little_slip_otter_half_birthday).

initial_location(clockwork_pie, kitchen).
location_after_event(clockwork_pie, e004, windowsill).


/* ============================================================
   ERRAND ITEMS
   ============================================================ */

entity(blue_thread).
entity(pepper).
entity(mint_sprig_little).
entity(mint_sprig_middle).
entity(mint_sprig_great).
entity(sugared_minnows).
entity(jar_of_sugared_minnows).
entity(one_sugared_minnow).

object(blue_thread).
object(pepper).
object(mint_sprig_little).
object(mint_sprig_middle).
object(mint_sprig_great).
object(jar_of_sugared_minnows).
object(one_sugared_minnow).

food(sugared_minnows).
food(one_sugared_minnow).

kind(blue_thread, thread).
kind(pepper, spice).
kind(mint_sprig_little, mint_sprig).
kind(mint_sprig_middle, mint_sprig).
kind(mint_sprig_great, mint_sprig).
kind(sugared_minnows, sweets).
kind(jar_of_sugared_minnows, jar).
kind(one_sugared_minnow, sugared_minnow).

size(mint_sprig_little, little).
size(mint_sprig_middle, middle).
size(mint_sprig_great, great).

intended_for(mint_sprig_little, little_slip_otter).
intended_for(mint_sprig_middle, middle_sized_otter).
intended_for(mint_sprig_great, great_long_otter).

sent_by(tillys_aunt, tilly_tumbletop, errand_1).
errand_item(errand_1, blue_thread).
errand_item(errand_1, pepper).

forgotten_by_during_story(tilly_tumbletop, blue_thread).
hazy_notion_by_during_story(tilly_tumbletop, pepper).


/* ============================================================
   NORMS AND MANNERS
   ============================================================ */

norm(ask_before_entering_private_house).
norm(do_not_eat_food_without_permission).
norm(do_not_use_others_property_without_permission).
norm(repair_damage_you_caused).
norm(apologize_after_wrongdoing).

good_manners(wait_outside).
good_manners(ask_for_help_when_lost).
good_manners(wait_to_be_invited_inside).
good_manners(wait_to_be_offered_food).

bad_manners(peep_through_house_openings).
bad_manners(enter_without_permission).
bad_manners(eat_without_permission).
bad_manners(use_property_without_permission).
bad_manners(deny_responsibility_when_mostly_responsible).

permission(tilly_tumbletop, fetch, blue_thread).
permission(tilly_tumbletop, fetch, pepper).

% No explicit permissions were granted to Tilly for these.
no_permission(tilly_tumbletop, enter, willow_root_house).
no_permission(tilly_tumbletop, eat, clockwork_pie).
no_permission(tilly_tumbletop, use, little_boots).
no_permission(tilly_tumbletop, use, middle_boots).
no_permission(tilly_tumbletop, use, great_boots).
no_permission(tilly_tumbletop, use, little_boat).
no_permission(tilly_tumbletop, use, middle_boat).
no_permission(tilly_tumbletop, use, great_boat).


/* ============================================================
   STORY EVENTS
   event(EventId, Actor, Action, Object, Location).
   story_time(EventId, Integer).
   ============================================================ */

event(e001, three_otter_household, live_together, willow_root_house, wood).
story_time(e001, 1).

event(e002, three_otter_household, bake, clockwork_pie, kitchen).
story_time(e002, 2).

event(e003, clockwork_pie, come_out_of_oven, fiercely_ticking, kitchen).
story_time(e003, 3).

event(e004, great_long_otter, warn, whisker_tickling_risk, kitchen).
story_time(e004, 4).

said(e004, great_long_otter, "Dear me! If we eat it now it will tickle our whiskers off.").

event(e005, three_otter_household, put, clockwork_pie, windowsill).
story_time(e005, 5).

event(e006, three_otter_household, leave_house, gather_mint, riverbank).
story_time(e006, 6).

event(e007, tillys_aunt, send_on_errand, tilly_tumbletop, outside).
story_time(e007, 7).

event(e008, tilly_tumbletop, poke_sticks_into, puddles, outside).
story_time(e008, 8).

event(e009, tilly_tumbletop, count, beetles, outside).
story_time(e009, 9).

event(e010, tilly_tumbletop, follow, goose_shaped_cloud, outside).
story_time(e010, 10).

event(e011, tilly_tumbletop, forget, blue_thread, outside).
story_time(e011, 11).

event(e012, tilly_tumbletop, have_hazy_notion_of, pepper, outside).
story_time(e012, 12).

event(e013, tilly_tumbletop, see, willow_root_house, wood).
story_time(e013, 13).

event(e014, tilly_tumbletop, look_in, round_window, willow_root_house).
story_time(e014, 14).

event(e015, tilly_tumbletop, peep_through, chimney_hole, willow_root_house).
story_time(e015, 15).

event(e016, tilly_tumbletop, tap, front_door, willow_root_house).
story_time(e016, 16).

event(e017, nobody, answer, tap, willow_root_house).
story_time(e017, 17).

event(e018, tilly_tumbletop, lift_latch, front_door, willow_root_house).
story_time(e018, 18).

event(e019, tilly_tumbletop, enter, willow_root_house, front_door).
story_time(e019, 19).

event(e020, tilly_tumbletop, see, clockwork_pie, windowsill).
story_time(e020, 20).

event(e021, tilly_tumbletop, speak_about, clockwork_pie, kitchen).
story_time(e021, 21).

said(e021, tilly_tumbletop, "Oh! A pie that ticks! That must be a pie in a hurry.").

event(e022, tilly_tumbletop, cut_with, great_knife, clockwork_pie).
story_time(e022, 22).

event(e023, tilly_tumbletop, create_slice, great_pie_slice, kitchen).
story_time(e023, 23).

event(e024, great_pie_slice, tick_tock_fast, fork_chasing, plate).
story_time(e024, 24).

event(e025, tilly_tumbletop, reject, great_pie_slice, kitchen).
story_time(e025, 25).

said(e025, tilly_tumbletop, "This pie is too quick.").

event(e026, tilly_tumbletop, cut_with, middle_knife, clockwork_pie).
story_time(e026, 26).

event(e027, tilly_tumbletop, create_slice, middle_pie_slice, kitchen).
story_time(e027, 27).

event(e028, middle_pie_slice, tick_tock_slowly, raisins_delayed, plate).
story_time(e028, 28).

event(e029, tilly_tumbletop, fall_asleep_waiting_for, raisins, kitchen).
story_time(e029, 29).

event(e030, tilly_tumbletop, reject, middle_pie_slice, kitchen).
story_time(e030, 30).

said(e030, tilly_tumbletop, "This pie is too slow.").

event(e031, tilly_tumbletop, cut_with, little_knife, clockwork_pie).
story_time(e031, 31).

event(e032, tilly_tumbletop, create_slice, little_pie_slice, kitchen).
story_time(e032, 32).

event(e033, little_pie_slice, tick_tock_merrily, comfortable_rhythm, plate).
story_time(e033, 33).

event(e034, tilly_tumbletop, judge, little_pie_slice, kitchen).
story_time(e034, 34).

event(e035, tilly_tumbletop, eat_all, little_pie_slice, kitchen).
story_time(e035, 35).

event(e036, tilly_tumbletop, swallow, brass_wheels, kitchen).
story_time(e036, 36).

event(e037, tilly_tumbletop, feel, stomach_buzzing, kitchen).
story_time(e037, 37).

event(e038, tilly_tumbletop, see, three_pairs_of_boots, willow_root_house).
story_time(e038, 38).

event(e039, tilly_tumbletop, put_on, great_boots, willow_root_house).
story_time(e039, 39).

event(e040, great_boots, walk_in_different_directions, tillys_legs, willow_root_house).
story_time(e040, 40).

event(e041, tilly_tumbletop, reject, great_boots, willow_root_house).
story_time(e041, 41).

said(e041, tilly_tumbletop, "These boots are too wandering.").

event(e042, tilly_tumbletop, put_on, middle_boots, willow_root_house).
story_time(e042, 42).

event(e043, middle_boots, require_clear_errand_statement, tilly_tumbletop, willow_root_house).
story_time(e043, 43).

event(e044, tilly_tumbletop, fail_to_state_errand_clearly, errand_1, willow_root_house).
story_time(e044, 44).

event(e045, tilly_tumbletop, reject, middle_boots, willow_root_house).
story_time(e045, 45).

said(e045, tilly_tumbletop, "These boots are too particular.").

event(e046, tilly_tumbletop, put_on, little_boots, willow_root_house).
story_time(e046, 46).

event(e047, tilly_tumbletop, judge, little_boots, willow_root_house).
story_time(e047, 47).

event(e048, little_boots, begin_to_dance, tilly_tumbletop, willow_root_house).
story_time(e048, 48).

event(e049, tilly_tumbletop, dance_after_boots, little_boots, willow_root_house).
story_time(e049, 49).

event(e050, tilly_tumbletop, dance_round, table, willow_root_house).
story_time(e050, 50).

event(e051, tilly_tumbletop, dance_over, mat, willow_root_house).
story_time(e051, 51).

event(e052, tilly_tumbletop, dance_under, stool, willow_root_house).
story_time(e052, 52).

event(e053, tilly_tumbletop, dance_into, pantry, willow_root_house).
story_time(e053, 53).

event(e054, tilly_tumbletop, knock_down, jar_of_sugared_minnows, pantry).
story_time(e054, 54).

event(e055, tilly_tumbletop, deny_full_fault, jar_incident, pantry).
story_time(e055, 55).

said(e055, tilly_tumbletop, "That was not my fault.").

event(e056, tilly_tumbletop, decide_to_row, boat, willow_root_house).
story_time(e056, 56).

event(e057, tilly_tumbletop, climb_into, great_boat, rain_barrel).
story_time(e057, 57).

event(e058, great_boat, rock_grandly, rain_barrel_water, rain_barrel).
story_time(e058, 58).

event(e059, great_boat, splash_water_into, tillys_ears, rain_barrel).
story_time(e059, 59).

event(e060, tilly_tumbletop, reject, great_boat, rain_barrel).
story_time(e060, 60).

said(e060, tilly_tumbletop, "This boat is too billowy.").

event(e061, tilly_tumbletop, climb_into, middle_boat, rain_barrel).
story_time(e061, 61).

event(e062, tilly_tumbletop, read_rules_inside, middle_boat, rain_barrel).
story_time(e062, 62).

event(e063, middle_boat, display_rule, rule_7, rain_barrel).
story_time(e063, 63).

rule_text(rule_7, "No rowing until all previous rules have been obeyed.").

event(e064, tilly_tumbletop, reject, middle_boat, rain_barrel).
story_time(e064, 64).

said(e064, tilly_tumbletop, "This boat is too bossy.").

event(e065, tilly_tumbletop, climb_into, little_boat, rain_barrel).
story_time(e065, 65).

event(e066, tilly_tumbletop, judge, little_boat, rain_barrel).
story_time(e066, 66).

event(e067, tilly_tumbletop, row_round_and_round, rain_barrel, little_boat).
story_time(e067, 67).

event(e068, tilly_tumbletop, pretend_to_be, queen_of_a_lake, little_boat).
story_time(e068, 68).

event(e069, little_boat, prove_not_made_for, queens, rain_barrel).
story_time(e069, 69).

event(e070, tilly_tumbletop, be_heavier_than, otter, little_boat).
story_time(e070, 70).

event(e071, tilly_tumbletop, be_heavier_after_eating, little_pie_slice, little_boat).
story_time(e071, 71).

event(e072, little_boat, sink_lower_and_lower, rain_barrel, rain_barrel).
story_time(e072, 72).

event(e073, rain_barrel, glug, loudly, willow_root_house).
story_time(e073, 73).

event(e074, plug, pop_out_of, rain_barrel, willow_root_house).
story_time(e074, 74).

event(e075, water, rush_across, floor, willow_root_house).
story_time(e075, 75).

event(e076, little_boat, spin_three_times, rain_barrel, willow_root_house).
story_time(e076, 76).

event(e077, little_boat, turn_over, rain_barrel, willow_root_house).
story_time(e077, 77).

event(e078, tilly_tumbletop, sit_in, puddle, floor).
story_time(e078, 78).

event(e079, one_sugared_minnow, stick_to, tillys_sleeve, floor).
story_time(e079, 79).

event(e080, three_otter_household, return_home_with, mint_sprigs, willow_root_house).
story_time(e080, 80).

event(e081, great_long_otter, open, front_door, willow_root_house).
story_time(e081, 81).

event(e082, great_long_otter, sniff, air, willow_root_house).
story_time(e082, 82).

event(e083, great_long_otter, discover, great_pie_slice_cut, kitchen).
story_time(e083, 83).

said(e083, great_long_otter, "Somebody has been cutting my clockwork pie!").

event(e084, middle_sized_otter, discover, middle_pie_slice_cut, kitchen).
story_time(e084, 84).

said(e084, middle_sized_otter, "And somebody has been cutting my clockwork pie!").

event(e085, little_slip_otter, discover, little_pie_slice_eaten, kitchen).
story_time(e085, 85).

said(e085, little_slip_otter, "And somebody has eaten my little slice all up!").

event(e086, great_long_otter, look_at, great_boots, willow_root_house).
story_time(e086, 86).

event(e087, great_long_otter, infer_use_of, great_boots, willow_root_house).
story_time(e087, 87).

said(e087, great_long_otter, "Somebody has been walking in my boots!").

event(e088, middle_sized_otter, infer_argument_with, middle_boots, willow_root_house).
story_time(e088, 88).

said(e088, middle_sized_otter, "And somebody has been arguing with my boots!").

event(e089, little_slip_otter, discover, little_boots_danced_holes, willow_root_house).
story_time(e089, 89).

said(e089, little_slip_otter, "And somebody has danced holes in mine!").

event(e090, three_otter_household, see, rain_barrel, willow_root_house).
story_time(e090, 90).

event(e091, great_long_otter, infer_rowing_in, great_boat, rain_barrel).
story_time(e091, 91).

said(e091, great_long_otter, "Somebody has been rowing in my boat!").

event(e092, middle_sized_otter, infer_rules_ignored_in, middle_boat, rain_barrel).
story_time(e092, 92).

said(e092, middle_sized_otter, "And somebody has been ignoring the rules in my boat!").

event(e093, little_slip_otter, discover, little_boat_sunk, rain_barrel).
story_time(e093, 93).

said(e093, little_slip_otter, "And somebody has sunk my boat all the way to the bottom!").

event(e094, tilly_tumbletop, sneeze, pantry, pantry).
story_time(e094, 94).

event(e095, three_otter_household, look_in, pantry, pantry).
story_time(e095, 95).

event(e096, three_otter_household, find, tilly_tumbletop, pantry).
story_time(e096, 96).

event(e097, three_otter_household, observe, tilly_dripping_wet, pantry).
story_time(e097, 97).

event(e098, three_otter_household, observe, crumbs_in_tillys_hair, pantry).
story_time(e098, 98).

event(e099, three_otter_household, observe, sugared_minnows_in_tillys_pockets, pantry).
story_time(e099, 99).

event(e100, three_otter_household, observe, tillys_stomach_tick_tocking, pantry).
story_time(e100, 100).

event(e101, nobody, speak, silence, pantry).
story_time(e101, 101).

event(e102, great_long_otter, speak_about, stomach_tick_tocking, pantry).
story_time(e102, 102).

said(e102, great_long_otter, "That is not a healthy sound for a child.").

event(e103, middle_sized_otter, speak_about, stomach_tick_tocking, pantry).
story_time(e103, 103).

said(e103, middle_sized_otter, "Nor a lawful one.").

event(e104, little_slip_otter, speak_about, swallowed_wheels, pantry).
story_time(e104, 104).

said(e104, little_slip_otter, "She has got my half-birthday wheels inside her.").

event(e105, tilly_tumbletop, cry_leakily, apology_beginning, pantry).
story_time(e105, 105).

event(e106, tilly_tumbletop, apologize, three_otter_household, pantry).
story_time(e106, 106).

said(e106, tilly_tumbletop, "I am sorry.").

event(e107, tilly_tumbletop, explain, errand_and_pie, pantry).
story_time(e107, 107).

said(e107, tilly_tumbletop, "I was sent for blue thread and pepper, and I found a ticking pie instead.").

event(e108, great_long_otter, state_moral_observation, trouble_beginning, pantry).
story_time(e108, 108).

said(e108, great_long_otter, "That is how trouble often begins.").

event(e109, middle_sized_otter, give, towel, pantry).
story_time(e109, 109).

event(e110, little_slip_otter, give, sharp_look, pantry).
story_time(e110, 110).

event(e111, three_otter_household, stand_on, tilly_tumbletop, stool).
story_time(e111, 111).

event(e112, three_otter_household, wind_with, pie_key, stool).
story_time(e112, 112).

event(e113, brass_wheel_1, click_out_of, tilly_tumbletop, stool).
story_time(e113, 113).

event(e114, brass_wheel_2, click_out_of, tilly_tumbletop, stool).
story_time(e114, 114).

event(e115, brass_wheel_3, click_out_of, tilly_tumbletop, stool).
story_time(e115, 115).

event(e116, brass_wheel_4, click_out_of, tilly_tumbletop, stool).
story_time(e116, 116).

event(e117, brass_wheel_5, click_out_of, tilly_tumbletop, stool).
story_time(e117, 117).

event(e118, brass_wheel_6, click_out_of, tilly_tumbletop, stool).
story_time(e118, 118).

event(e119, recovered_wheels, be_clean, none_the_worse, stool).
story_time(e119, 119).

event(e120, one_recovered_wheel, have, tooth_mark, stool).
story_time(e120, 120).

event(e121, tilly_tumbletop, help_mop, floor, willow_root_house).
story_time(e121, 121).

event(e122, tilly_tumbletop, help_mend, little_boat, willow_root_house).
story_time(e122, 122).

event(e123, tilly_tumbletop, help_polish, boots, willow_root_house).
story_time(e123, 123).

event(e124, three_otter_household, give, ordinary_pie_slice, willow_root_house).
story_time(e124, 124).

event(e125, tilly_tumbletop, eat, ordinary_pie_slice, willow_root_house).
story_time(e125, 125).

event(e126, tilly_tumbletop, leave_for_home, homeward_path, willow_root_house).
story_time(e126, 126).

event(e127, tilly_tumbletop, carry, blue_thread, homeward_path).
story_time(e127, 127).

event(e128, tilly_tumbletop, carry, pepper, homeward_path).
story_time(e128, 128).

event(e129, tilly_tumbletop, carry, mint_sprig, homeward_path).
story_time(e129, 129).

event(e130, tilly_tumbletop, promise, never_enter_without_being_asked, homeward_path).
story_time(e130, 130).

event(e131, tilly_tumbletop, remember_moral_as, tick_tock_warning, future).
story_time(e131, 131).


/* ============================================================
   JUDGMENTS: TOO MUCH / TOO LITTLE / JUST RIGHT
   ============================================================ */

judged(tilly_tumbletop, great_pie_slice, ticking_speed, too_quick).
judged(tilly_tumbletop, middle_pie_slice, ticking_speed, too_slow).
judged(tilly_tumbletop, little_pie_slice, ticking_speed, just_right).

judged(tilly_tumbletop, great_boots, walking_behavior, too_wandering).
judged(tilly_tumbletop, middle_boots, obedience_requirement, too_particular).
judged(tilly_tumbletop, little_boots, mischief_level, just_mischievous_enough).

judged(tilly_tumbletop, great_boat, water_motion, too_billowy).
judged(tilly_tumbletop, middle_boat, rule_level, too_bossy).
judged(tilly_tumbletop, little_boat, rowing_fit, just_right).

accepted_choice(tilly_tumbletop, little_pie_slice).
accepted_choice(tilly_tumbletop, little_boots).
accepted_choice(tilly_tumbletop, little_boat).

rejected_choice(tilly_tumbletop, great_pie_slice).
rejected_choice(tilly_tumbletop, middle_pie_slice).
rejected_choice(tilly_tumbletop, great_boots).
rejected_choice(tilly_tumbletop, middle_boots).
rejected_choice(tilly_tumbletop, great_boat).
rejected_choice(tilly_tumbletop, middle_boat).


/* ============================================================
   STATE CHANGES AND CONSEQUENCES
   ============================================================ */

caused_by(e035, tilly_tumbletop).
causes(e035, eaten(little_pie_slice)).
causes(e035, swallowed(tilly_tumbletop, brass_wheel_1)).
causes(e035, swallowed(tilly_tumbletop, brass_wheel_2)).
causes(e035, swallowed(tilly_tumbletop, brass_wheel_3)).
causes(e035, swallowed(tilly_tumbletop, brass_wheel_4)).
causes(e035, swallowed(tilly_tumbletop, brass_wheel_5)).
causes(e035, swallowed(tilly_tumbletop, brass_wheel_6)).

caused_by(e037, little_pie_slice).
causes(e037, stomach_condition(tilly_tumbletop, buzzing)).
causes(e037, stomach_condition(tilly_tumbletop, ticking)).

caused_by(e040, great_boots).
causes(e040, loss_of_control(tilly_tumbletop, legs)).

caused_by(e043, middle_boots).
causes(e043, demand_for_clear_errand_statement(tilly_tumbletop)).

caused_by(e048, little_boots).
causes(e048, dancing(tilly_tumbletop)).

caused_by(e054, tilly_tumbletop).
causes(e054, knocked_down(jar_of_sugared_minnows)).
causes(e054, scattered(sugared_minnows)).
causes(e054, pantry_mess).

caused_by(e075, rain_barrel).
causes(e075, flooded(floor)).
causes(e075, water_across_floor).

caused_by(e077, little_boat).
causes(e077, overturned(little_boat)).

caused_by(e078, little_boat).
causes(e078, wet(tilly_tumbletop)).
causes(e078, sitting_in(tilly_tumbletop, puddle)).

caused_by(e089, little_boots).
causes(e089, damaged(little_boots)).
causes(e089, holes_in(little_boots)).

caused_by(e093, tilly_tumbletop).
causes(e093, sunk(little_boat)).

caused_by(e112, three_otter_household).
causes(e112, recovered(brass_wheel_1)).
causes(e112, recovered(brass_wheel_2)).
causes(e112, recovered(brass_wheel_3)).
causes(e112, recovered(brass_wheel_4)).
causes(e112, recovered(brass_wheel_5)).
causes(e112, recovered(brass_wheel_6)).
causes(e112, stomach_condition_removed(tilly_tumbletop, ticking)).

caused_by(e121, tilly_tumbletop).
causes(e121, cleaned(floor)).
causes(e121, repaired_consequence(flooded(floor))).

caused_by(e122, tilly_tumbletop).
causes(e122, mended(little_boat)).
causes(e122, repaired_consequence(sunk(little_boat))).

caused_by(e123, tilly_tumbletop).
causes(e123, polished(little_boots)).
causes(e123, polished(middle_boots)).
causes(e123, polished(great_boots)).
causes(e123, repaired_consequence(used_without_permission(tilly_tumbletop, little_boots))).

final_state(cleaned(floor)).
final_state(mended(little_boat)).
final_state(polished(little_boots)).
final_state(polished(middle_boots)).
final_state(polished(great_boots)).
final_state(recovered(brass_wheel_1)).
final_state(recovered(brass_wheel_2)).
final_state(recovered(brass_wheel_3)).
final_state(recovered(brass_wheel_4)).
final_state(recovered(brass_wheel_5)).
final_state(recovered(brass_wheel_6)).
final_state(tilly_has_promised_never_to_enter_without_being_asked).
final_state(tilly_has_moral_memory_tick_tock).

condition_after_story(tilly_tumbletop, no_longer_ticking).
condition_after_story(tilly_tumbletop, morally_warned).
condition_after_story(tilly_tumbletop, apologetic).

condition_after_story(little_boat, mended).
condition_after_story(floor, mopped).
condition_after_story(little_boots, polished).
condition_after_story(middle_boots, polished).
condition_after_story(great_boots, polished).


/* ============================================================
   WRONGDOING AND RESPONSIBILITY
   ============================================================ */

entered_without_permission(tilly_tumbletop, willow_root_house, e019).
ate_without_permission(tilly_tumbletop, little_pie_slice, e035).
used_without_permission(tilly_tumbletop, great_knife, e022).
used_without_permission(tilly_tumbletop, middle_knife, e026).
used_without_permission(tilly_tumbletop, little_knife, e031).
used_without_permission(tilly_tumbletop, great_boots, e039).
used_without_permission(tilly_tumbletop, middle_boots, e042).
used_without_permission(tilly_tumbletop, little_boots, e046).
used_without_permission(tilly_tumbletop, great_boat, e057).
used_without_permission(tilly_tumbletop, middle_boat, e061).
used_without_permission(tilly_tumbletop, little_boat, e065).

violated_norm(tilly_tumbletop, ask_before_entering_private_house, e019).
violated_norm(tilly_tumbletop, do_not_eat_food_without_permission, e035).
violated_norm(tilly_tumbletop, do_not_use_others_property_without_permission, e039).
violated_norm(tilly_tumbletop, do_not_use_others_property_without_permission, e042).
violated_norm(tilly_tumbletop, do_not_use_others_property_without_permission, e046).
violated_norm(tilly_tumbletop, do_not_use_others_property_without_permission, e057).
violated_norm(tilly_tumbletop, do_not_use_others_property_without_permission, e061).
violated_norm(tilly_tumbletop, do_not_use_others_property_without_permission, e065).

mostly_responsible_for(tilly_tumbletop, jar_incident).
mostly_responsible_for(tilly_tumbletop, pantry_mess).
mostly_responsible_for(tilly_tumbletop, flooded_floor).
mostly_responsible_for(tilly_tumbletop, sunk_little_boat).
mostly_responsible_for(tilly_tumbletop, eaten_little_pie_slice).
mostly_responsible_for(tilly_tumbletop, swallowed_brass_wheels).

mitigating_factor(tilly_tumbletop, apologized).
mitigating_factor(tilly_tumbletop, helped_clean_floor).
mitigating_factor(tilly_tumbletop, helped_mend_boat).
mitigating_factor(tilly_tumbletop, helped_polish_boots).
mitigating_factor(tilly_tumbletop, promised_not_to_repeat_wrongdoing).

restitution(tilly_tumbletop, mopped_floor).
restitution(tilly_tumbletop, mended_little_boat).
restitution(tilly_tumbletop, polished_boots).

forgiven_enough_to_receive_food(tilly_tumbletop).
received_hospitality_after_apology(tilly_tumbletop, ordinary_pie_slice).


/* ============================================================
   EVIDENCE AND OTTER INFERENCES
   ============================================================ */

evidence(great_pie_slice_cut, great_pie_slice).
evidence(middle_pie_slice_cut, middle_pie_slice).
evidence(little_pie_slice_eaten, little_pie_slice).
evidence(little_boots_danced_holes, little_boots).
evidence(little_boat_sunk, little_boat).
evidence(floor_flooded, floor).
evidence(tilly_dripping_wet, tilly_tumbletop).
evidence(crumbs_in_tillys_hair, tilly_tumbletop).
evidence(sugared_minnows_in_tillys_pockets, tilly_tumbletop).
evidence(tillys_stomach_tick_tocking, tilly_tumbletop).

inferred_by(great_long_otter, someone_cut_pie, e083).
inferred_by(middle_sized_otter, someone_cut_pie, e084).
inferred_by(little_slip_otter, someone_ate_little_slice, e085).
inferred_by(great_long_otter, someone_walked_in_great_boots, e087).
inferred_by(middle_sized_otter, someone_argued_with_middle_boots, e088).
inferred_by(little_slip_otter, someone_danced_holes_in_little_boots, e089).
inferred_by(great_long_otter, someone_rowed_in_great_boat, e091).
inferred_by(middle_sized_otter, someone_ignored_middle_boat_rules, e092).
inferred_by(little_slip_otter, someone_sank_little_boat, e093).

found_in(tilly_tumbletop, pantry, e096).
found_condition(tilly_tumbletop, dripping_wet, e097).
found_condition(tilly_tumbletop, crumbs_in_hair, e098).
found_condition(tilly_tumbletop, sugared_minnows_in_pockets, e099).
found_condition(tilly_tumbletop, stomach_tick_tocking, e100).


/* ============================================================
   STORY THEMES AND MORAL
   ============================================================ */

theme(curiosity_without_manners_causes_trouble).
theme(repetition_and_comic_escalation).
theme(too_much_too_little_just_right_pattern).
theme(apology_and_restitution).
theme(hospitality_after_accountability).

moral("Mind your manners before the pie does it for you.").
memory_warning(tilly_tumbletop, tick_tock).
symbolizes(tick_tock_warning, conscience).
symbolizes(tick_tock_warning, memory_of_consequences).
symbolizes(clockwork_pie, magical_consequence_of_meddling).


/* ============================================================
   GENERAL RULES
   ============================================================ */

before(E1, E2) :-
    story_time(E1, T1),
    story_time(E2, T2),
    T1 < T2.

after(E2, E1) :-
    before(E1, E2).

same_household(A, B) :-
    household_member(H, A),
    household_member(H, B),
    A \= B.

belongs_to_household(Object, Household) :-
    owned_by(Object, Household).

belongs_to_household(Object, Household) :-
    owned_by(Object, Owner),
    household_member(Household, Owner).

otter_property(Object) :-
    owned_by(Object, Owner),
    otter(Owner).

otter_property(Object) :-
    owned_by(Object, three_otter_household).

just_right_for(Person, Thing) :-
    judged(Person, Thing, _, just_right).

just_right_for(Person, Thing) :-
    judged(Person, Thing, _, just_mischievous_enough).

too_extreme_for(Person, Thing) :-
    judged(Person, Thing, _, Verdict),
    Verdict \= just_right,
    Verdict \= just_mischievous_enough.

accepted_by(Person, Thing) :-
    accepted_choice(Person, Thing).

rejected_by(Person, Thing) :-
    rejected_choice(Person, Thing).

wrongful_entry(Person, Place) :-
    entered_without_permission(Person, Place, _).

wrongful_eating(Person, Food) :-
    ate_without_permission(Person, Food, _).

wrongful_use(Person, Object) :-
    used_without_permission(Person, Object, _).

wrongdoing(Person) :-
    violated_norm(Person, _, _).

damaged(Item) :-
    causes(_, damaged(Item)).

made_mess(Person, Mess) :-
    caused_by(Event, Person),
    causes(Event, Mess),
    Mess = pantry_mess.

made_mess(Person, flooded_floor) :-
    caused_by(Event, Person),
    causes(Event, sunk(little_boat)).

needs_repair(Item) :-
    causes(_, damaged(Item)).

needs_repair(Item) :-
    causes(_, sunk(Item)).

needs_cleaning(floor) :-
    causes(_, flooded(floor)).

repaired(Item) :-
    final_state(mended(Item)).

repaired(Item) :-
    final_state(cleaned(Item)).

repaired(Item) :-
    final_state(polished(Item)).

recovered_wheel(Wheel) :-
    kind(Wheel, brass_wheel),
    final_state(recovered(Wheel)).

swallowed_wheel(Person, Wheel) :-
    causes(_, swallowed(Person, Wheel)).

all_wheels_recovered :-
    recovered_wheel(brass_wheel_1),
    recovered_wheel(brass_wheel_2),
    recovered_wheel(brass_wheel_3),
    recovered_wheel(brass_wheel_4),
    recovered_wheel(brass_wheel_5),
    recovered_wheel(brass_wheel_6).

ate_clockwork_part(Person) :-
    swallowed_wheel(Person, Wheel),
    kind(Wheel, brass_wheel).

stomach_ticks(Person) :-
    causes(_, stomach_condition(Person, ticking)),
    \+ final_state(stomach_condition_removed(Person, ticking)).

stomach_ticked_during_story(Person) :-
    causes(_, stomach_condition(Person, ticking)).

has_moral_growth(Person) :-
    character(Person),
    apologized(Person),
    made_restitution(Person),
    promised_better_behavior(Person).

apologized(tilly_tumbletop) :-
    event(e106, tilly_tumbletop, apologize, three_otter_household, pantry).

made_restitution(tilly_tumbletop) :-
    restitution(tilly_tumbletop, mopped_floor),
    restitution(tilly_tumbletop, mended_little_boat),
    restitution(tilly_tumbletop, polished_boots).

promised_better_behavior(tilly_tumbletop) :-
    event(e130, tilly_tumbletop, promise, never_enter_without_being_asked, homeward_path).

forgivable(Person) :-
    apologized(Person),
    made_restitution(Person),
    promised_better_behavior(Person).

hospitable_response(three_otter_household, tilly_tumbletop) :-
    forgiven_enough_to_receive_food(tilly_tumbletop),
    received_hospitality_after_apology(tilly_tumbletop, ordinary_pie_slice).

comic_escalation_step(e035, eats_clockwork_pie).
comic_escalation_step(e048, boots_begin_dancing).
comic_escalation_step(e054, pantry_mess).
comic_escalation_step(e075, floor_flooded).
comic_escalation_step(e100, stomach_tick_tocking).
comic_escalation_step(e112, pie_key_remedy).

pattern_instance(too_much_too_little_just_right, pie_slices).
pattern_instance(too_much_too_little_just_right, boots).
pattern_instance(too_much_too_little_just_right, boats).

pattern_choice(pie_slices, great_pie_slice, too_quick).
pattern_choice(pie_slices, middle_pie_slice, too_slow).
pattern_choice(pie_slices, little_pie_slice, just_right).

pattern_choice(boots, great_boots, too_wandering).
pattern_choice(boots, middle_boots, too_particular).
pattern_choice(boots, little_boots, just_mischievous_enough).

pattern_choice(boats, great_boat, too_billowy).
pattern_choice(boats, middle_boat, too_bossy).
pattern_choice(boats, little_boat, just_right).


/* ============================================================
   USEFUL QUERY HELPERS
   ============================================================ */

who_lived_in_house(Character) :-
    lives_at(Character, willow_root_house).

what_did_tilly_eat(Food) :-
    event(_, tilly_tumbletop, eat_all, Food, _).

what_did_tilly_swallow(Wheel) :-
    swallowed_wheel(tilly_tumbletop, Wheel).

what_was_just_right(Item) :-
    just_right_for(tilly_tumbletop, Item).

what_was_rejected(Item) :-
    rejected_by(tilly_tumbletop, Item).

what_did_tilly_damage_or_mess_up(ItemOrMess) :-
    caused_by(Event, tilly_tumbletop),
    causes(Event, ItemOrMess).

where_was_tilly_found(Place) :-
    found_in(tilly_tumbletop, Place, _).

why_did_boat_sink(little_boat, reason(tilly_too_heavy_and_had_eaten_clockwork_pie)) :-
    event(e070, tilly_tumbletop, be_heavier_than, otter, little_boat),
    event(e071, tilly_tumbletop, be_heavier_after_eating, little_pie_slice, little_boat).

why_did_otters_leave_house(reason(clockwork_pie_too_tickly_or_hot_to_eat_immediately)) :-
    event(e004, great_long_otter, warn, whisker_tickling_risk, kitchen),
    event(e006, three_otter_household, leave_house, gather_mint, riverbank).

why_did_tilly_enter(reason(curiosity_and_lack_of_polished_manners)) :-
    trait(tilly_tumbletop, curious),
    trait(tilly_tumbletop, unpolished),
    event(e019, tilly_tumbletop, enter, willow_root_house, front_door).

how_was_problem_fixed(clockwork_wheels, wound_tilly_with_pie_key) :-
    event(e112, three_otter_household, wind_with, pie_key, stool),
    all_wheels_recovered.

story_resolution(apology_restitution_and_hospitality) :-
    apologized(tilly_tumbletop),
    made_restitution(tilly_tumbletop),
    hospitable_response(three_otter_household, tilly_tumbletop).
