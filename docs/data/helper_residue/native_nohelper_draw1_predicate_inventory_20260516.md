# Compile Predicate Inventory

- Compile artifacts scanned: `56`
- Parsed artifacts: `56`
- Candidate predicate mentions: `1230`
- Unique candidate predicates: `1086`
- Admitted predicate mentions: `62371`
- Unique admitted predicates: `982`
- Candidate predicates not admitted anywhere: `124`
- Admitted predicates not listed as candidates anywhere: `20`

## Top Admitted Predicates

| Predicate | Clause mentions | Fixtures |
| --- | ---: | ---: |
| `source_record_numeric_token/2` | 8400 | 55 |
| `source_record_row/5` | 5739 | 56 |
| `source_record_kind/2` | 5739 | 56 |
| `source_record_line/2` | 5739 | 56 |
| `source_record_section/2` | 5739 | 56 |
| `source_record_text_key/2` | 5739 | 56 |
| `source_record_label/2` | 5676 | 56 |
| `source_record_text_atom/2` | 5673 | 56 |
| `source_record_cell/3` | 1906 | 20 |
| `source_record_cell_text_key/3` | 1906 | 20 |
| `source_record_cell_header/3` | 1649 | 20 |
| `source_record_field/3` | 1649 | 20 |
| `student_in_version/3` | 121 | 1 |
| `person_role/3` | 105 | 13 |
| `person_id/2` | 95 | 2 |
| `initial_group_assignment/3` | 83 | 1 |
| `roster_table_member/4` | 77 | 1 |
| `roster_table_member_label/5` | 77 | 1 |
| `event/5` | 60 | 1 |
| `person/1` | 59 | 4 |
| `rule_text/2` | 57 | 5 |
| `event_id/1` | 56 | 3 |
| `score_entry/5` | 53 | 1 |
| `rule_id/1` | 53 | 5 |
| `roster_member/4` | 52 | 1 |
| `statement_by/3` | 44 | 2 |
| `held_role/3` | 44 | 1 |
| `recorded_in/4` | 44 | 1 |
| `rule_condition/3` | 41 | 4 |
| `party_role/3` | 41 | 4 |
| `correction_applied/3` | 40 | 3 |
| `event_location/2` | 40 | 3 |
| `roster_table_member_alias/2` | 40 | 1 |
| `assigned_to_room/2` | 40 | 1 |
| `state_changed/3` | 39 | 1 |
| `assertion_source/3` | 37 | 4 |
| `event_type/2` | 36 | 3 |
| `docket_entry/4` | 35 | 1 |
| `applicant_attribute/3` | 35 | 1 |
| `student_id/1` | 35 | 1 |

## Top Candidate Predicates

| Predicate | Mentions | Fixtures |
| --- | ---: | ---: |
| `person_role/3` | 14 | 14 |
| `document_type/2` | 7 | 7 |
| `recorded_in/3` | 6 | 6 |
| `person_role/2` | 5 | 5 |
| `item_attribute/3` | 5 | 5 |
| `rule_id/1` | 5 | 5 |
| `rule_text/2` | 5 | 5 |
| `rule_condition/3` | 4 | 4 |
| `event_occurred/3` | 4 | 4 |
| `correction_applied/3` | 4 | 4 |
| `compiled_by/2` | 4 | 4 |
| `event_location/2` | 4 | 4 |
| `person/1` | 4 | 4 |
| `party_role/3` | 4 | 4 |
| `source_supports/4` | 4 | 4 |
| `fact_source/3` | 4 | 4 |
| `assertion_source/3` | 4 | 4 |
| `application_id/1` | 3 | 3 |
| `correction_id/1` | 3 | 3 |
| `event_type/2` | 3 | 3 |
| `source_recorded/4` | 3 | 3 |
| `location/1` | 3 | 3 |
| `unresolved_question/2` | 3 | 3 |
| `compiled_by/3` | 3 | 3 |
| `entity_type/2` | 3 | 3 |
| `organization/1` | 3 | 3 |
| `asset_attribute/3` | 3 | 3 |
| `event_id/1` | 3 | 3 |
| `event_occurred/4` | 3 | 3 |
| `supersedes/2` | 2 | 2 |
| `source_recorded/3` | 2 | 2 |
| `event_date/3` | 2 | 2 |
| `permit_status/3` | 2 | 2 |
| `correction_applied/4` | 2 | 2 |
| `applicant_name/2` | 2 | 2 |
| `applicant_type/2` | 2 | 2 |
| `requested_amount/2` | 2 | 2 |
| `vote_result/3` | 2 | 2 |
| `claim_source/3` | 2 | 2 |
| `person_id/2` | 2 | 2 |

## Fixtures

| Fixture | Candidates | Unique candidates | Admitted mentions | Unique admitted | Skipped | Rough score |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `amended_lease_register` | 21 | 21 | 424 | 25 | 27 | 0.833 |
| `arts_grant_panel_reconsideration` | 17 | 17 | 1340 | 29 | 7 | 0.778 |
| `ashgrove_permit` | 19 | 19 | 983 | 27 | 0 | 0.722 |
| `authority_possession_custody_packet` | 21 | 21 | 1441 | 32 | 50 | 0.889 |
| `avalon_grant_committee` | 43 | 43 | 1864 | 46 | 2 | 0.778 |
| `black_lantern_maze` | 20 | 20 | 1668 | 23 | 13 | 0.994 |
| `building_access_reliability_packet` | 29 | 29 | 2175 | 40 | 4 | 0.778 |
| `census_reconciliation` | 16 | 16 | 684 | 28 | 5 | 1.0 |
| `clinic_device_recall_field_packet` | 15 | 15 | 2229 | 26 | 20 | 0.889 |
| `clockmakers_three_ledgers` | 26 | 26 | 587 | 29 | 23 | 0.889 |
| `contradictory_evidence_packet` | 20 | 20 | 1380 | 31 | 33 | 0.833 |
| `copperfall_deadline_docket` | 25 | 25 | 732 | 31 | 0 | 0.889 |
| `count_composition_roster` | 23 | 23 | 1922 | 41 | 12 | 0.889 |
| `deadline_cascade_docket` | 20 | 20 | 512 | 26 | 9 | 0.889 |
| `draft_within_draft` | 27 | 27 | 550 | 37 | 11 | 0.889 |
| `dream_library_index` | 27 | 27 | 424 | 35 | 11 | 0.778 |
| `dulse_ledger` | 29 | 29 | 1115 | 27 | 0 | 0.889 |
| `estate_archive_access_dispute` | 27 | 27 | 910 | 35 | 2 | 0.778 |
| `fenmore_seedbank` | 29 | 29 | 1148 | 26 | 20 | 0.778 |
| `festival_permit_maze` | 17 | 17 | 573 | 25 | 0 | 0.833 |
| `grant_exception_cap_matrix` | 23 | 23 | 2433 | 35 | 2 | 1.0 |
| `greenhouse_quarantine` | 10 | 10 | 731 | 20 | 21 | 0.778 |
| `greywell_pipeline` | 16 | 16 | 865 | 24 | 12 | 1.0 |
| `harbor_collision_reports` | 27 | 27 | 521 | 34 | 12 | 1.0 |
| `harrowgate_witness_file` | 15 | 15 | 422 | 22 | 4 | 1.0 |
| `heronvale_arts` | 16 | 16 | 1203 | 24 | 0 | 0.889 |
| `hospital_shift_exception_log` | 25 | 25 | 873 | 26 | 71 | 0.778 |
| `identifier_ledger_torture` | 25 | 25 | 1618 | 34 | 1 | 1.0 |
| `industrial_sensor_clock_correction` | 28 | 28 | 2504 | 36 | 3 | 0.889 |
| `lantern_school_field_trip` | 14 | 14 | 486 | 17 | 9 | 0.881 |
| `larkspur_clockwork_fair` | 23 | 23 | 443 | 24 | 73 | 0.879 |
| `ledger_at_calders_reach` | 31 | 31 | 681 | 34 | 57 | 0.778 |
| `maritime_salvage_sensor_packet` | 22 | 22 | 1058 | 29 | 12 | 0.884 |
| `meridian_permit_board` | 31 | 31 | 767 | 38 | 6 | 0.778 |
| `municipal_tree_permit_amendment` | 13 | 13 | 1181 | 25 | 6 | 1.0 |
| `museum_mislabelled_rooms` | 12 | 12 | 489 | 18 | 16 | 0.833 |
| `nested_puppet_court` | 27 | 27 | 377 | 34 | 4 | 0.889 |
| `northbridge_authority_packet` | 14 | 14 | 603 | 24 | 5 | 0.778 |
| `orchard_inheritance_game` | 31 | 31 | 329 | 26 | 1 | 0.885 |
| `oxalis_recall` | 25 | 25 | 1564 | 31 | 2 | 0.722 |
| `probate_storage_access_register` | 17 | 17 | 2556 | 28 | 29 | 0.833 |
| `ridgeline_fire` | 26 | 26 | 1847 | 33 | 96 | 0.778 |
| `rotating_chair_authority` | 13 | 13 | 530 | 21 | 8 | 0.722 |
| `rule_activation_exception_matrix` | 25 | 25 | 1789 | 39 | 5 | 0.722 |
| `sable_creek_budget` | 21 | 21 | 1560 | 19 | 4 | 0.778 |
| `salvage_bell_dispute` | 23 | 23 | 406 | 29 | 18 | 1.0 |
| `school_activity_roster_reconciliation` | 22 | 22 | 2407 | 28 | 9 | 0.778 |
| `school_trip_bus_roster_split` | 20 | 20 | 1277 | 26 | 26 | 0.994 |
| `temporal_state_ledger` | 27 | 27 | 1606 | 34 | 16 | 0.778 |
| `thornfield_variance` | 20 | 20 | 1826 | 29 | 2 | 0.889 |
| `three_moles_moon_marmalade_machine` | 14 | 14 | 742 | 20 | 0 | 0.694 |
| `tournament_borrowed_names` | 15 | 15 | 1157 | 25 | 11 | 0.889 |
| `university_lab_sample_chain` | 16 | 16 | 937 | 22 | 39 | 0.889 |
| `veridia9_supply_chain_patent_dispute` | 19 | 19 | 370 | 29 | 9 | 0.772 |
| `veridia_intake` | 26 | 26 | 520 | 34 | 5 | 1.0 |
| `wildfire_evacuation_revision_order` | 27 | 27 | 1032 | 38 | 1 | 0.889 |
