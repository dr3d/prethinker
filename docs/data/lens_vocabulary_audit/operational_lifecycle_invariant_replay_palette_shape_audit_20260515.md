# Operational Lifecycle Palette Audit

- Schema: `operational_lifecycle_palette_audit_v1`
- Compiles: `6`
- Class counts: `{'supersession_target_collapse': 1, 'phase_classification_missing': 6, 'alias_split': 3, 'shallow_lifecycle_palette': 3, 'ambiguous_repeated_verb': 1}`
- Fixtures with findings: `5`

## Fixture Summary

| Fixture | Alias Split | Ambiguous Verb | Supersession Collapse | Phase Missing | Shallow Palette |
| --- | ---: | ---: | ---: | ---: | ---: |
| `clinic_intake_corrections` | 0 | 0 | 1 | 2 | 0 |
| `grant_review_queue` | 1 | 0 | 0 | 2 | 1 |
| `library_preservation_queue` | 0 | 0 | 0 | 0 | 0 |
| `permit_renewal_docket` | 0 | 0 | 0 | 1 | 0 |
| `warehouse_repair_log` | 2 | 0 | 0 | 0 | 1 |
| `water_sample_docket` | 0 | 1 | 0 | 1 | 1 |

## Findings

### `clinic_intake_corrections`

- `supersession_target_collapse`: `fact`='status_superseded(denied_scheduling, pending_nurse_review).', `source_target_codes`=['ms9']
  - on_2026_02_05_the_front_desk_corrected_the_referral_by_adding_mobility_score_ms_9_the_denied_scheduling_status_was_superseded_by_pending_nurse_review
- `phase_classification_missing`: `phase`='initial'
  - on_2026_02_02_intake_aide_mara_chen_received_referral_r_44_from_the_front_desk_and_filed_ci_44_with_status_pending_triage
- `phase_classification_missing`: `phase`='current'
  - on_2026_02_09_coordinator_lina_fox_closed_ci_44_as_scheduled_for_standard_afternoon_therapy_the_current_status_is_scheduled

### `grant_review_queue`

- `alias_split`: `code`='l5', `variants`=['artifact_letter_l5', 'l_5']
  - identity code `l5` appears as artifact_letter_l5, l_5
- `phase_classification_missing`: `phase`='initial'
  - on_2026_05_02_grants_clerk_ilya_ren_received_proposal_p_5_and_filed_it_with_status_pending_eligibility_check
- `phase_classification_missing`: `phase`='current'
  - on_2026_05_10_director_mei_holt_closed_gq_5_as_approved_for_the_tool_shed_without_the_solar_panel_line_the_current_status_is_approved_with_revised_budget
- `shallow_lifecycle_palette`: `source_signal_count`=4, `candidate_count`=14, `nearby_signatures`=['status/1', 'proposal_status/2', 'queue_status/2', 'status_changed_on/2', 'assigned_to/2']
  - on_2026_05_02_grants_clerk_ilya_ren_received_proposal_p_5_and_filed_it_with_status_pending_eligibility_check
  - on_2026_05_05_eligibility_staff_denied_eligibility_approval_for_lack_of_the_match_letter

### `permit_renewal_docket`

- `phase_classification_missing`: `phase`='initial'
  - on_2026_01_04_clerk_erin_moss_received_application_a_18_and_filed_it_as_pr_18_the_initial_status_was_pending_completeness_review

### `warehouse_repair_log`

- `alias_split`: `code`='wr62', `variants`=['evt_wr62_approved', 'evt_wr62_assigned', 'evt_wr62_closed', 'evt_wr62_denied', 'evt_wr62_pending', 'evt_wr62_tested', 'evt_wr62_withdrawn', 'wr_62']
  - identity code `wr62` appears as evt_wr62_approved, evt_wr62_assigned, evt_wr62_closed, evt_wr62_denied, evt_wr62_pending, evt_wr62_tested, evt_wr62_withdrawn, wr_62
- `alias_split`: `code`='wr63', `variants`=['evt_wr63_superseded', 'wr_63']
  - identity code `wr63` appears as evt_wr63_superseded, wr_63
- `shallow_lifecycle_palette`: `source_signal_count`=5, `candidate_count`=12, `nearby_signatures`=['ticket_status/2', 'event_date/3', 'asset_status/2', 'diagnosis_corrected/2']
  - on_2026_03_01_shift_lead_tomas_iver_received_the_malfunction_report_and_logged_wr_62_as_pending_inspection
  - on_2026_03_03_rhea_denied_the_request_to_replace_the_scanner_because_the_power_module_had_not_been_tested

### `water_sample_docket`

- `ambiguous_repeated_verb`: `verb`='received', `predicate_surfaces`=[]
  - on_2026_04_10_field_collector_niko_shah_received_sample_b_12_and_filed_docket_ws_12_with_status_pending_lab_receipt
  - on_2026_04_11_lab_desk_ada_voss_logged_b_12_as_received_and_assigned_it_to_nitrate_testing
- `phase_classification_missing`: `phase`='initial'
  - on_2026_04_10_field_collector_niko_shah_received_sample_b_12_and_filed_docket_ws_12_with_status_pending_lab_receipt
- `shallow_lifecycle_palette`: `source_signal_count`=6, `candidate_count`=10, `nearby_signatures`=['event_date/2', 'docket_status/2', 'test_result/2']
  - on_2026_04_10_field_collector_niko_shah_received_sample_b_12_and_filed_docket_ws_12_with_status_pending_lab_receipt
  - on_2026_04_12_the_first_test_was_denied_as_valid_because_the_vial_seal_was_loose
