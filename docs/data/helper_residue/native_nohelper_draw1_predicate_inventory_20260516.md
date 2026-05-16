# Compile Predicate Inventory

- Compile artifacts scanned: `56`
- Parsed artifacts: `56`
- Candidate predicate mentions: `1230`
- Unique candidate predicates: `1086`
- Admitted predicate mentions: `62371`
- Unique admitted predicates: `982`
- Candidate predicates not admitted anywhere: `124`
- Admitted predicates not listed as candidates anywhere: `20`

## Predicate Buckets

These buckets are a first-pass layer map, not a promotion decision.

### Admitted

| Bucket | Clause mentions | Unique predicates | Fixtures | Top predicates |
| --- | ---: | ---: | ---: | --- |
| `deterministic_ledger` | 55584 | 14 | 56 | `source_record_numeric_token/2` (8400), `source_record_row/5` (5739), `source_record_kind/2` (5739), `source_record_line/2` (5739), `source_record_section/2` (5739), `source_record_text_key/2` (5739) |
| `semantic_compile_surface` | 6247 | 953 | 56 | `person_role/3` (105), `person_id/2` (95), `event/5` (60), `person/1` (59), `rule_text/2` (57), `event_id/1` (56) |
| `legacy_compatibility_alias` | 540 | 15 | 4 | `student_in_version/3` (121), `initial_group_assignment/3` (83), `roster_table_member/4` (77), `roster_table_member_label/5` (77), `roster_member/4` (52), `roster_table_member_alias/2` (40) |

### Candidates

| Bucket | Mentions | Unique predicates | Fixtures | Top predicates |
| --- | ---: | ---: | ---: | --- |
| `semantic_compile_surface` | 1221 | 1077 | 56 | `person_role/3` (14), `document_type/2` (7), `recorded_in/3` (6), `person_role/2` (5), `item_attribute/3` (5), `rule_id/1` (5) |
| `legacy_compatibility_alias` | 9 | 9 | 4 | `student_in_version/3` (1), `student_withdrawn/2` (1), `student_added/2` (1), `homeroom_reassigned/3` (1), `initial_group_assignment/3` (1), `student_id/1` (1) |

## Alias Family Coverage

- Non-ledger unique predicates: `968`
- Non-ledger predicates with at least one generic alias family: `434`

| Family | Predicates covered | Examples |
| --- | ---: | --- |
| `access_authorization_surface` | 37 | `access_agreement/3`, `access_authority/2`, `access_event/5`, `access_event_authorization/2`, `accession_collector/2`, `accession_date/2`, `accession_id/1`, `accession_initial_condition/2` |
| `assignment_allocation_surface` | 10 | `assigned_to_bus/3`, `assigned_to_group/2`, `assigned_to_room/2`, `bus_assignment/3`, `funding_allocation/3`, `homeroom_reassigned/3`, `initial_group_assignment/3`, `liability_assignment/3` |
| `attribute_value_surface` | 14 | `applicant_attribute/3`, `asset_attribute/3`, `cycle_parameter/2`, `has_property/2`, `item_attribute/3`, `item_attribute_source/3`, `project_attribute/3`, `project_parameter/4` |
| `chronology_event_surface` | 44 | `absence_of_event/3`, `access_event/5`, `access_event_authorization/2`, `adverse_event/3`, `annexation_event/4`, `collision_event/1`, `corrected_event_id/2`, `correction_event/4` |
| `count_requirement_surface` | 15 | `approval_threshold/2`, `base_unit_count/3`, `clarification_required/2`, `distinct_student_count/2`, `excluded_from_count/2`, `fte_count/2`, `funding_threshold/2`, `headcount_confirmed_by/2` |
| `custody_location_surface` | 23 | `asset_location/2`, `chain_of_custody/2`, `custody_of/3`, `custody_state_at_date/3`, `custody_status/2`, `custody_status/3`, `custody_transfer/4`, `easement_location/4` |
| `external_identifier_surface` | 4 | `exhibit_reference/2`, `item_external_id/3`, `pending_external_action/3`, `policy_reference/2` |
| `identity_role_surface` | 25 | `action_by_role/4`, `adult_role/2`, `case_party/3`, `case_role/3`, `docket_party_role/4`, `entity_role/2`, `entity_role/3`, `entity_role_in_context/4` |
| `item_identifier_surface` | 121 | `accession_id/1`, `alternative_candidate/3`, `amendment_description/2`, `amendment_id/1`, `applicant_id/1`, `application_id/1`, `application_id/2`, `asset_attribute/3` |
| `order_effect_surface` | 17 | `amendment_effective_date/2`, `funding_order_rule/2`, `issued_order/4`, `order_date/2`, `order_id/1`, `order_issued_at/2`, `order_issued_by/2`, `order_outcome/2` |
| `record_provenance_surface` | 70 | `appeal_filed/3`, `appeal_filed/4`, `assertion_source/3`, `assertion_source/4`, `claim_source/3`, `conflicting_sources/2`, `correction_record/4`, `correction_source/3` |
| `score_measurement_surface` | 10 | `composite_score/3`, `measured_value/5`, `measurement_accuracy/3`, `measurement_recorded/4`, `recorded_score/4`, `reviewer_score/4`, `score_correction/5`, `score_entry/5` |
| `source_assertion_surface` | 39 | `adverse_possession_claim/2`, `application_claim/4`, `asserted_boundary_position/3`, `asserted_by/2`, `assertion_source/3`, `assertion_source/4`, `asserts_anchor_ball_status/3`, `asserts_claim/4` |
| `state_transition_surface` | 77 | `accession_status/2`, `advisory_statement/2`, `appeal_status/2`, `application_status/2`, `application_status_at/3`, `arbitration_status/2`, `asserts_anchor_ball_status/3`, `asset_status/3` |
| `title_status_surface` | 58 | `accession_status/2`, `appeal_status/2`, `application_status/2`, `application_status_at/3`, `arbitration_status/2`, `asserts_anchor_ball_status/3`, `asset_status/3`, `award_status/2` |
| `versioned_membership_surface` | 12 | `adult_in_version/3`, `compliance_version/1`, `document_version/2`, `gis_layer_version/1`, `policy_version_valid/3`, `report_version/3`, `roster_table_version/2`, `roster_version/1` |

## Admitted Semantic Risk Ranking

| Predicate | Risk | Mentions | Fixtures | Alias families | Flagged tokens | Reason |
| --- | --- | ---: | ---: | --- | --- | --- |
| `assigned_to_bus/3` | `domain_or_fixture_shaped_singleton` | 23 | 1 | `assignment_allocation_surface` | `bus` | domain-shaped vocabulary with little transfer evidence |
| `adult_in_version/3` | `domain_or_fixture_shaped_singleton` | 13 | 1 | `versioned_membership_surface` | `adult` | domain-shaped vocabulary with little transfer evidence |
| `bus_chaperone/2` | `domain_or_fixture_shaped_singleton` | 4 | 1 |  | `bus`, `chaperone` | domain-shaped vocabulary with little transfer evidence |
| `distinct_student_count/2` | `domain_or_fixture_shaped_singleton` | 4 | 1 | `count_requirement_surface` | `student` | domain-shaped vocabulary with little transfer evidence |
| `patient_use_exception/5` | `domain_or_fixture_shaped_singleton` | 4 | 1 |  | `patient` | domain-shaped vocabulary with little transfer evidence |
| `qualifying_chaperone_count/2` | `domain_or_fixture_shaped_singleton` | 4 | 1 | `count_requirement_surface` | `chaperone` | domain-shaped vocabulary with little transfer evidence |
| `roster_version/1` | `domain_or_fixture_shaped_singleton` | 4 | 1 | `versioned_membership_surface` | `roster` | domain-shaped vocabulary with little transfer evidence |
| `roster_version_date/2` | `domain_or_fixture_shaped_singleton` | 4 | 1 | `versioned_membership_surface` | `roster` | domain-shaped vocabulary with little transfer evidence |
| `sensor_id/1` | `domain_or_fixture_shaped_singleton` | 4 | 1 | `item_identifier_surface` | `sensor` | domain-shaped vocabulary with little transfer evidence |
| `roster_version/3` | `domain_or_fixture_shaped_singleton` | 3 | 1 | `versioned_membership_surface` | `roster` | domain-shaped vocabulary with little transfer evidence |
| `sensor_calibration_date/2` | `domain_or_fixture_shaped_singleton` | 3 | 1 |  | `sensor` | domain-shaped vocabulary with little transfer evidence |
| `sensor_certified_scope/2` | `domain_or_fixture_shaped_singleton` | 3 | 1 |  | `sensor` | domain-shaped vocabulary with little transfer evidence |
| `adult_added/2` | `domain_or_fixture_shaped_singleton` | 2 | 1 |  | `adult` | domain-shaped vocabulary with little transfer evidence |
| `bus_id/1` | `domain_or_fixture_shaped_singleton` | 2 | 1 | `item_identifier_surface` | `bus` | domain-shaped vocabulary with little transfer evidence |
| `final_grant_amount/2` | `domain_or_fixture_shaped_singleton` | 2 | 1 |  | `grant` | domain-shaped vocabulary with little transfer evidence |
| `grant_amount/2` | `domain_or_fixture_shaped_singleton` | 2 | 1 |  | `grant` | domain-shaped vocabulary with little transfer evidence |
| `grant_disbursement_date/2` | `domain_or_fixture_shaped_singleton` | 2 | 1 |  | `grant` | domain-shaped vocabulary with little transfer evidence |
| `grant_fiscal_year/2` | `domain_or_fixture_shaped_singleton` | 2 | 1 |  | `grant` | domain-shaped vocabulary with little transfer evidence |
| `grant_return_amount/2` | `domain_or_fixture_shaped_singleton` | 2 | 1 |  | `grant` | domain-shaped vocabulary with little transfer evidence |
| `grant_return_status/2` | `domain_or_fixture_shaped_singleton` | 2 | 1 | `state_transition_surface`, `title_status_surface` | `grant` | domain-shaped vocabulary with little transfer evidence |
| `prior_grant_id/1` | `domain_or_fixture_shaped_singleton` | 2 | 1 | `item_identifier_surface` | `grant` | domain-shaped vocabulary with little transfer evidence |
| `sensor_next_calibration_due/2` | `domain_or_fixture_shaped_singleton` | 2 | 1 |  | `sensor` | domain-shaped vocabulary with little transfer evidence |
| `sensor_not_certified_for/2` | `domain_or_fixture_shaped_singleton` | 2 | 1 |  | `sensor` | domain-shaped vocabulary with little transfer evidence |
| `adult_withdrawn/2` | `domain_or_fixture_shaped_singleton` | 1 | 1 |  | `adult` | domain-shaped vocabulary with little transfer evidence |
| `bus_assignment/3` | `domain_or_fixture_shaped_singleton` | 1 | 1 | `assignment_allocation_surface` | `bus` | domain-shaped vocabulary with little transfer evidence |
| `chaperone_substitution/3` | `domain_or_fixture_shaped_singleton` | 1 | 1 |  | `chaperone` | domain-shaped vocabulary with little transfer evidence |
| `patient_event/4` | `domain_or_fixture_shaped_singleton` | 1 | 1 | `chronology_event_surface` | `patient` | domain-shaped vocabulary with little transfer evidence |
| `standby_chaperone/2` | `domain_or_fixture_shaped_singleton` | 1 | 1 |  | `chaperone` | domain-shaped vocabulary with little transfer evidence |
| `student_in_version/3` | `legacy_compatibility_alias` | 121 | 1 | `versioned_membership_surface` | `student` | compatibility alias; keep out of new guidance unless explicitly scoped |
| `initial_group_assignment/3` | `legacy_compatibility_alias` | 83 | 1 | `assignment_allocation_surface` |  | compatibility alias; keep out of new guidance unless explicitly scoped |
| `roster_table_member/4` | `legacy_compatibility_alias` | 77 | 1 |  | `roster` | compatibility alias; keep out of new guidance unless explicitly scoped |
| `roster_table_member_label/5` | `legacy_compatibility_alias` | 77 | 1 |  | `roster` | compatibility alias; keep out of new guidance unless explicitly scoped |
| `roster_member/4` | `legacy_compatibility_alias` | 52 | 1 |  | `roster` | compatibility alias; keep out of new guidance unless explicitly scoped |
| `roster_table_member_alias/2` | `legacy_compatibility_alias` | 40 | 1 |  | `roster` | compatibility alias; keep out of new guidance unless explicitly scoped |
| `student_id/1` | `legacy_compatibility_alias` | 35 | 1 | `item_identifier_surface` | `student` | compatibility alias; keep out of new guidance unless explicitly scoped |
| `roster_table_member_header/2` | `legacy_compatibility_alias` | 12 | 1 |  | `roster` | compatibility alias; keep out of new guidance unless explicitly scoped |
| `roster_table_scope/2` | `legacy_compatibility_alias` | 12 | 1 |  | `roster` | compatibility alias; keep out of new guidance unless explicitly scoped |
| `roster_table_version/2` | `legacy_compatibility_alias` | 12 | 1 | `versioned_membership_surface` | `roster` | compatibility alias; keep out of new guidance unless explicitly scoped |
| `adult_role/2` | `legacy_compatibility_alias` | 8 | 1 | `identity_role_surface` | `adult` | compatibility alias; keep out of new guidance unless explicitly scoped |
| `homeroom_reassigned/3` | `legacy_compatibility_alias` | 3 | 1 | `assignment_allocation_surface` | `homeroom` | compatibility alias; keep out of new guidance unless explicitly scoped |
| `student_added/2` | `legacy_compatibility_alias` | 3 | 1 |  | `student` | compatibility alias; keep out of new guidance unless explicitly scoped |
| `student_withdrawn/2` | `legacy_compatibility_alias` | 3 | 1 |  | `student` | compatibility alias; keep out of new guidance unless explicitly scoped |
| `student_swap/4` | `legacy_compatibility_alias` | 2 | 1 |  | `student` | compatibility alias; keep out of new guidance unless explicitly scoped |
| `event/5` | `high_volume_single_fixture_surface` | 60 | 1 | `chronology_event_surface` |  | large local surface; check whether this is structure or corpus residue |
| `score_entry/5` | `high_volume_single_fixture_surface` | 53 | 1 | `score_measurement_surface` |  | large local surface; check whether this is structure or corpus residue |
| `held_role/3` | `high_volume_single_fixture_surface` | 44 | 1 | `identity_role_surface` |  | large local surface; check whether this is structure or corpus residue |
| `recorded_in/4` | `high_volume_single_fixture_surface` | 44 | 1 | `record_provenance_surface` |  | large local surface; check whether this is structure or corpus residue |
| `assigned_to_room/2` | `high_volume_single_fixture_surface` | 40 | 1 | `assignment_allocation_surface` |  | large local surface; check whether this is structure or corpus residue |
| `state_changed/3` | `high_volume_single_fixture_surface` | 39 | 1 | `state_transition_surface` |  | large local surface; check whether this is structure or corpus residue |
| `applicant_attribute/3` | `high_volume_single_fixture_surface` | 35 | 1 | `attribute_value_surface` |  | large local surface; check whether this is structure or corpus residue |
| `docket_entry/4` | `high_volume_single_fixture_surface` | 35 | 1 | `record_provenance_surface` |  | large local surface; check whether this is structure or corpus residue |
| `seat_row_assignment/3` | `high_volume_single_fixture_surface` | 35 | 1 | `assignment_allocation_surface` |  | large local surface; check whether this is structure or corpus residue |
| `object/1` | `high_volume_single_fixture_surface` | 33 | 1 | `item_identifier_surface` |  | large local surface; check whether this is structure or corpus residue |
| `said/3` | `high_volume_single_fixture_surface` | 33 | 1 | `item_identifier_surface` |  | large local surface; check whether this is structure or corpus residue |
| `administrative_action/5` | `high_volume_single_fixture_surface` | 32 | 1 |  |  | large local surface; check whether this is structure or corpus residue |
| `correction_source_record/3` | `high_volume_single_fixture_surface` | 32 | 1 | `record_provenance_surface` |  | large local surface; check whether this is structure or corpus residue |
| `item_attribute_source/3` | `high_volume_single_fixture_surface` | 30 | 1 | `attribute_value_surface`, `item_identifier_surface`, `record_provenance_surface` |  | large local surface; check whether this is structure or corpus residue |
| `owns/3` | `high_volume_single_fixture_surface` | 30 | 1 |  |  | large local surface; check whether this is structure or corpus residue |
| `project_parameter/4` | `high_volume_single_fixture_surface` | 30 | 1 | `attribute_value_surface` |  | large local surface; check whether this is structure or corpus residue |
| `entity_role_in_context/4` | `high_volume_single_fixture_surface` | 28 | 1 | `identity_role_surface` |  | large local surface; check whether this is structure or corpus residue |
| `consistent_with/3` | `high_volume_single_fixture_surface` | 26 | 1 |  |  | large local surface; check whether this is structure or corpus residue |
| `has_physical_custody/3` | `high_volume_single_fixture_surface` | 24 | 1 | `custody_location_surface` |  | large local surface; check whether this is structure or corpus residue |
| `item_internal_id/2` | `high_volume_single_fixture_surface` | 24 | 1 | `item_identifier_surface` |  | large local surface; check whether this is structure or corpus residue |
| `item_title_recorded/3` | `high_volume_single_fixture_surface` | 24 | 1 | `item_identifier_surface`, `record_provenance_surface`, `title_status_surface` |  | large local surface; check whether this is structure or corpus residue |
| `owned_by/2` | `high_volume_single_fixture_surface` | 24 | 1 |  |  | large local surface; check whether this is structure or corpus residue |
| `assigned_to_group/2` | `high_volume_single_fixture_surface` | 23 | 1 | `assignment_allocation_surface` |  | large local surface; check whether this is structure or corpus residue |
| `log_turn/2` | `high_volume_single_fixture_surface` | 23 | 1 |  |  | large local surface; check whether this is structure or corpus residue |
| `date_event_anchor/3` | `high_volume_single_fixture_surface` | 22 | 1 | `chronology_event_surface` |  | large local surface; check whether this is structure or corpus residue |
| `docket_event/4` | `high_volume_single_fixture_surface` | 22 | 1 | `chronology_event_surface`, `record_provenance_surface` |  | large local surface; check whether this is structure or corpus residue |
| `event/1` | `high_volume_single_fixture_surface` | 22 | 1 | `chronology_event_surface` |  | large local surface; check whether this is structure or corpus residue |
| `involved_actor/2` | `high_volume_single_fixture_surface` | 22 | 1 |  |  | large local surface; check whether this is structure or corpus residue |
| `structure_attribute/4` | `high_volume_single_fixture_surface` | 22 | 1 | `attribute_value_surface` |  | large local surface; check whether this is structure or corpus residue |
| `event_actor/2` | `high_volume_single_fixture_surface` | 21 | 1 | `chronology_event_surface` |  | large local surface; check whether this is structure or corpus residue |
| `event_actor_role/4` | `high_volume_single_fixture_surface` | 21 | 1 | `chronology_event_surface`, `identity_role_surface` |  | large local surface; check whether this is structure or corpus residue |
| `project_attribute/3` | `high_volume_single_fixture_surface` | 21 | 1 | `attribute_value_surface` |  | large local surface; check whether this is structure or corpus residue |
| `ambiguous_utterance/2` | `high_volume_single_fixture_surface` | 20 | 1 |  |  | large local surface; check whether this is structure or corpus residue |
| `conservation_engagement/4` | `high_volume_single_fixture_surface` | 20 | 1 |  |  | large local surface; check whether this is structure or corpus residue |
| `eligibility_finding/3` | `high_volume_single_fixture_surface` | 20 | 1 |  |  | large local surface; check whether this is structure or corpus residue |
| `rule_consequence/3` | `high_volume_single_fixture_surface` | 20 | 1 |  |  | large local surface; check whether this is structure or corpus residue |
| `person_role/3` | `broad_structural_candidate` | 105 | 13 | `identity_role_surface` |  | broad fixture spread; likely structural, still subject to slot-contract audit |

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
