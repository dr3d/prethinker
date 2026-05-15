# Compile Surface Stability Audit

- Compiles: `5`
- Fixtures: `1`
- Stable fixtures: `0`
- Unstable fixtures: `1`
- Unstable direct facts: `342`
- Predicate drift rows: `38`
- Surface drift rows: `4`

## `probate_storage_access_register`

- Draws: `5`
- Stable: `False`
- Common / union direct facts: `0 / 342`
- Unstable direct facts: `342`

| Predicate | Counts | Delta |
| --- | --- | ---: |
| `access_authority_source` | `[9, 0, 0, 0, 0]` | 9 |
| `access_authorized_to` | `[0, 0, 8, 0, 8]` | 8 |
| `access_source` | `[0, 0, 8, 0, 8]` | 8 |
| `assertion_made_by` | `[3, 0, 0, 0, 0]` | 3 |
| `assertion_recorded` | `[7, 0, 0, 0, 0]` | 7 |
| `asset_description` | `[11, 0, 0, 0, 0]` | 11 |
| `asset_id` | `[13, 0, 0, 0, 0]` | 13 |
| `authorized_party` | `[14, 0, 0, 0, 0]` | 14 |
| `claim_asserted_by` | `[0, 0, 3, 0, 3]` | 3 |
| `claim_evidence` | `[0, 0, 5, 0, 5]` | 5 |
| `correspondence_excerpt` | `[0, 0, 3, 0, 3]` | 3 |
| `court_order` | `[0, 0, 5, 5, 5]` | 5 |
| `custody_location` | `[0, 0, 8, 0, 8]` | 8 |
| `dispute_claimant` | `[2, 0, 0, 0, 0]` | 2 |
| `dispute_ground` | `[4, 0, 0, 0, 0]` | 4 |
| `dispute_status` | `[3, 0, 0, 0, 0]` | 3 |
| `dispute_subject` | `[3, 0, 0, 0, 0]` | 3 |
| `event_occurred` | `[0, 0, 20, 0, 18]` | 20 |
| `event_occurred_after` | `[1, 0, 0, 0, 0]` | 1 |
| `event_occurred_before` | `[18, 0, 0, 0, 0]` | 18 |
| `external_reference` | `[8, 0, 0, 0, 0]` | 8 |
| `has_physical_custodian` | `[0, 5, 0, 0, 0]` | 5 |
| `is_contested_by` | `[0, 1, 0, 0, 0]` | 1 |
| `issued_order` | `[0, 2, 0, 0, 0]` | 2 |
| `item_description` | `[0, 0, 11, 11, 10]` | 11 |
| `item_external_id` | `[0, 0, 8, 8, 7]` | 8 |
| `item_id` | `[0, 0, 11, 0, 10]` | 11 |
| `no_access_authority` | `[3, 0, 0, 0, 0]` | 3 |
| `order_date` | `[5, 0, 0, 0, 0]` | 5 |
| `order_effect` | `[5, 2, 0, 0, 0]` | 5 |
| `order_id` | `[5, 0, 0, 0, 0]` | 5 |
| `party_counsel` | `[2, 0, 0, 0, 0]` | 2 |
| `party_role` | `[15, 0, 16, 8, 15]` | 16 |
| `person_role` | `[0, 1, 0, 0, 0]` | 1 |
| `physical_custodian` | `[11, 0, 10, 11, 16]` | 16 |
| `title_contested_by` | `[10, 0, 1, 7, 7]` | 10 |
| `title_recorded_as` | `[10, 1, 0, 11, 0]` | 11 |
| `title_status` | `[0, 0, 10, 0, 10]` | 10 |

| Surface | Counts | Delta |
| --- | --- | ---: |
| `identity_role_surface` | `[15, 1, 18, 8, 17]` | 17 |
| `object_record_surface` | `[21, 1, 8, 11, 8]` | 20 |
| `status_phase_surface` | `[7, 0, 11, 0, 11]` | 11 |
| `task_scope_surface` | `[11, 0, 0, 0, 0]` | 11 |

### Missing From `compile_surface_invariant_focused_probate_20260514`

- Missing union facts: `180`
- `access_authorized_to(ex_001, caroline_sutter, physical).`
- `access_authorized_to(ex_001, northpoint_regional_museum, physical).`
- `access_authorized_to(ex_002, caroline_sutter, physical).`
- `access_authorized_to(ex_003, caroline_sutter, physical).`
- `access_authorized_to(ex_003, northpoint_regional_museum, physical).`
- `access_authorized_to(ex_004, caroline_sutter, physical).`
- `access_authorized_to(ex_004, lillian_park, observation_only).`
- `access_authorized_to(ex_005, caroline_sutter, physical).`
- `access_source(ex_001, caroline_sutter, loan_agreement_nrm_ll_2019_08_standing).`
- `access_source(ex_001, northpoint_regional_museum, loan_agreement_nrm_ll_2019_08_standing).`
- `access_source(ex_002, caroline_sutter, estate_authority_standing).`
- `access_source(ex_003, caroline_sutter, loan_agreement_nrm_ll_2020_02_standing).`
- `access_source(ex_003, northpoint_regional_museum, loan_agreement_nrm_ll_2020_02_standing).`
- `access_source(ex_004, caroline_sutter, court_order_p_26_347_d_2026_02_14).`
- `access_source(ex_004, lillian_park, court_order_p_26_347_d_2026_02_14).`
- `access_source(ex_005, caroline_sutter, estate_authority_standing).`
- `claim_asserted_by(codicil_claim_1, eliza_yamamoto_holloway, valid_holographic_codicil_bequeathing_all_notebooks_and_digital_archives).`
- `claim_asserted_by(gift_claim_1, daniel_holloway, ex_003_was_a_private_gift_given_in_person_on_2024_11_19).`
- `claim_asserted_by(reeder_claim_1, vance_reeder, ex_006_ex_007_ex_008_transferred_for_safekeeping_in_late_2024).`
- `claim_asserted_by(reeder_safekeeping_claim_1, vance_reeder, ex_006_ex_007_ex_008_transferred_for_safekeeping_in_late_2024).`
- `claim_evidence(codicil_claim_1, forensic_report, handwriting_analysis_ordered_2026_03_19_p_26_347_c_report_due_2026_06_03).`
- `claim_evidence(codicil_claim_1, forensic_report, ordered_2026_03_19_p_26_347_c_report_due_2026_06_03).`
- `claim_evidence(codicil_claim_1, handwritten_note, nb_2002_f_dated_2024_09_12).`
- `claim_evidence(codicil_claim_1, handwritten_note, nb_2002_f_ex_006_dated_2024_09_12_signed_m_holloway_witnessed_v_reeder).`
- `claim_evidence(gift_claim_1, motion, motion_2026_03_04_for_declaratory_ruling).`

### Missing From `compile_surface_invariant_recompile_20260514`

- Missing union facts: `330`
- `access_authority_source(ex_001, loan_agreement_nrm_ll_2019_08_standing).`
- `access_authority_source(ex_002, estate_authority_standing).`
- `access_authority_source(ex_003, loan_agreement_nrm_ll_2020_02_standing).`
- `access_authority_source(ex_004, court_order_p_26_347_d_2026_02_14).`
- `access_authority_source(ex_005, estate_authority_standing).`
- `access_authority_source(ex_009, museum_policy_mrp_04_estate_authority).`
- `access_authority_source(ex_010, court_order_p_26_347_d_2026_02_14).`
- `access_authority_source(ex_011, estate_authority_standing).`
- `access_authority_source(ex_012, estate_authority_standing).`
- `access_authorized_to(ex_001, caroline_sutter, physical).`
- `access_authorized_to(ex_001, northpoint_regional_museum, physical).`
- `access_authorized_to(ex_002, caroline_sutter, physical).`
- `access_authorized_to(ex_003, caroline_sutter, physical).`
- `access_authorized_to(ex_003, northpoint_regional_museum, physical).`
- `access_authorized_to(ex_004, caroline_sutter, physical).`
- `access_authorized_to(ex_004, lillian_park, observation_only).`
- `access_authorized_to(ex_005, caroline_sutter, physical).`
- `access_source(ex_001, caroline_sutter, loan_agreement_nrm_ll_2019_08_standing).`
- `access_source(ex_001, northpoint_regional_museum, loan_agreement_nrm_ll_2019_08_standing).`
- `access_source(ex_002, caroline_sutter, estate_authority_standing).`
- `access_source(ex_003, caroline_sutter, loan_agreement_nrm_ll_2020_02_standing).`
- `access_source(ex_003, northpoint_regional_museum, loan_agreement_nrm_ll_2020_02_standing).`
- `access_source(ex_004, caroline_sutter, court_order_p_26_347_d_2026_02_14).`
- `access_source(ex_004, lillian_park, court_order_p_26_347_d_2026_02_14).`
- `access_source(ex_005, caroline_sutter, estate_authority_standing).`

### Missing From `source_authority_density_probate_compile_local_20260515`

- Missing union facts: `215`
- `access_authority_source(ex_001, loan_agreement_nrm_ll_2019_08_standing).`
- `access_authority_source(ex_002, estate_authority_standing).`
- `access_authority_source(ex_003, loan_agreement_nrm_ll_2020_02_standing).`
- `access_authority_source(ex_004, court_order_p_26_347_d_2026_02_14).`
- `access_authority_source(ex_005, estate_authority_standing).`
- `access_authority_source(ex_009, museum_policy_mrp_04_estate_authority).`
- `access_authority_source(ex_010, court_order_p_26_347_d_2026_02_14).`
- `access_authority_source(ex_011, estate_authority_standing).`
- `access_authority_source(ex_012, estate_authority_standing).`
- `assertion_made_by(assert_codicil_eliza, eliza_yamamoto_holloway).`
- `assertion_made_by(assert_gift_ex003, daniel_holloway).`
- `assertion_made_by(assert_safekeeping, vance_reeder).`
- `assertion_recorded(assert_codicil_eliza, codicil_contention, section_f).`
- `assertion_recorded(assert_gift_ex003, private_gift_assertion_regarding_ex_003, section_f).`
- `assertion_recorded(assert_safekeeping, safekeeping_basis_for_possession_of_ex_006_ex_007_ex_008, section_f).`
- `assertion_recorded(compilation_note_g_content, register_reflects_status_as_of_2026_04_30_title_status_of_ex_004_ex_005_ex_006_ex_007_ex_008_ex_011_will_not_be_reduced_to_non_contested_before_2026_06_17, section_g).`
- `assertion_recorded(correspondence_h1_excerpt, decedent_transferred_ex_006_ex_007_ex_008_to_reeder_in_october_2024_for_safekeeping_reeder_asserts_no_claim_of_title_and_will_deliver_to_court_direction_reeder_will_not_access_items, section_h_1).`
- `assertion_recorded(correspondence_h2_excerpt, l_park_requests_observation_access_to_ex_004_and_ex_010_at_safestore_does_not_request_access_to_reeder_held_items, section_h_2).`
- `assertion_recorded(correspondence_h3_excerpt, museum_confirms_estate_is_lender_for_nrm_ll_2019_08_and_nrm_ll_2020_02_no_instruction_to_change_lender_for_ex_003_reading_room_access_policy_is_not_subject_to_change_by_lender, section_h_3).`
- `asset_description(ex_001, painting_three_apples_in_saucer_1987).`
- `asset_description(ex_002, painting_coastline_at_dusk_1991).`
- `asset_description(ex_003, bronze_caryatid_study_r_bess_1976).`
- `asset_description(ex_004, notebook_nb_1981_a_sketches).`
- `asset_description(ex_005, notebook_nb_1989_c_correspondence).`
- `asset_description(ex_006, notebook_nb_2002_f_working_notes).`

### Missing From `source_authority_invariant_probate_compile_20260514`

- Missing union facts: `281`
- `access_authority_source(ex_001, loan_agreement_nrm_ll_2019_08_standing).`
- `access_authority_source(ex_002, estate_authority_standing).`
- `access_authority_source(ex_003, loan_agreement_nrm_ll_2020_02_standing).`
- `access_authority_source(ex_004, court_order_p_26_347_d_2026_02_14).`
- `access_authority_source(ex_005, estate_authority_standing).`
- `access_authority_source(ex_009, museum_policy_mrp_04_estate_authority).`
- `access_authority_source(ex_010, court_order_p_26_347_d_2026_02_14).`
- `access_authority_source(ex_011, estate_authority_standing).`
- `access_authority_source(ex_012, estate_authority_standing).`
- `access_authorized_to(ex_001, caroline_sutter, physical).`
- `access_authorized_to(ex_001, northpoint_regional_museum, physical).`
- `access_authorized_to(ex_002, caroline_sutter, physical).`
- `access_authorized_to(ex_003, caroline_sutter, physical).`
- `access_authorized_to(ex_003, northpoint_regional_museum, physical).`
- `access_authorized_to(ex_004, caroline_sutter, physical).`
- `access_authorized_to(ex_004, lillian_park, observation_only).`
- `access_authorized_to(ex_005, caroline_sutter, physical).`
- `access_source(ex_001, caroline_sutter, loan_agreement_nrm_ll_2019_08_standing).`
- `access_source(ex_001, northpoint_regional_museum, loan_agreement_nrm_ll_2019_08_standing).`
- `access_source(ex_002, caroline_sutter, estate_authority_standing).`
- `access_source(ex_003, caroline_sutter, loan_agreement_nrm_ll_2020_02_standing).`
- `access_source(ex_003, northpoint_regional_museum, loan_agreement_nrm_ll_2020_02_standing).`
- `access_source(ex_004, caroline_sutter, court_order_p_26_347_d_2026_02_14).`
- `access_source(ex_004, lillian_park, court_order_p_26_347_d_2026_02_14).`
- `access_source(ex_005, caroline_sutter, estate_authority_standing).`

### Missing From `source_authority_invariant_probate_compile_local_20260514`

- Missing union facts: `209`
- `access_authority_source(ex_001, loan_agreement_nrm_ll_2019_08_standing).`
- `access_authority_source(ex_002, estate_authority_standing).`
- `access_authority_source(ex_003, loan_agreement_nrm_ll_2020_02_standing).`
- `access_authority_source(ex_004, court_order_p_26_347_d_2026_02_14).`
- `access_authority_source(ex_005, estate_authority_standing).`
- `access_authority_source(ex_009, museum_policy_mrp_04_estate_authority).`
- `access_authority_source(ex_010, court_order_p_26_347_d_2026_02_14).`
- `access_authority_source(ex_011, estate_authority_standing).`
- `access_authority_source(ex_012, estate_authority_standing).`
- `assertion_made_by(assert_codicil_eliza, eliza_yamamoto_holloway).`
- `assertion_made_by(assert_gift_ex003, daniel_holloway).`
- `assertion_made_by(assert_safekeeping, vance_reeder).`
- `assertion_recorded(assert_codicil_eliza, codicil_contention, section_f).`
- `assertion_recorded(assert_gift_ex003, private_gift_assertion_regarding_ex_003, section_f).`
- `assertion_recorded(assert_safekeeping, safekeeping_basis_for_possession_of_ex_006_ex_007_ex_008, section_f).`
- `assertion_recorded(compilation_note_g_content, register_reflects_status_as_of_2026_04_30_title_status_of_ex_004_ex_005_ex_006_ex_007_ex_008_ex_011_will_not_be_reduced_to_non_contested_before_2026_06_17, section_g).`
- `assertion_recorded(correspondence_h1_excerpt, decedent_transferred_ex_006_ex_007_ex_008_to_reeder_in_october_2024_for_safekeeping_reeder_asserts_no_claim_of_title_and_will_deliver_to_court_direction_reeder_will_not_access_items, section_h_1).`
- `assertion_recorded(correspondence_h2_excerpt, l_park_requests_observation_access_to_ex_004_and_ex_010_at_safestore_does_not_request_access_to_reeder_held_items, section_h_2).`
- `assertion_recorded(correspondence_h3_excerpt, museum_confirms_estate_is_lender_for_nrm_ll_2019_08_and_nrm_ll_2020_02_no_instruction_to_change_lender_for_ex_003_reading_room_access_policy_is_not_subject_to_change_by_lender, section_h_3).`
- `asset_description(ex_001, painting_three_apples_in_saucer_1987).`
- `asset_description(ex_002, painting_coastline_at_dusk_1991).`
- `asset_description(ex_003, bronze_caryatid_study_r_bess_1976).`
- `asset_description(ex_004, notebook_nb_1981_a_sketches).`
- `asset_description(ex_005, notebook_nb_1989_c_correspondence).`
- `asset_description(ex_006, notebook_nb_2002_f_working_notes).`
