# Operational Lifecycle Palette Audit

- Schema: `operational_lifecycle_palette_audit_v1`
- Compiles: `6`
- Class counts: `{'alias_split': 9, 'phase_classification_missing': 7, 'supersession_target_collapse': 3, 'ambiguous_repeated_verb': 1}`
- Fixtures with findings: `5`

## Fixture Summary

| Fixture | Alias Split | Ambiguous Verb | Supersession Collapse | Phase Missing | Shallow Palette |
| --- | ---: | ---: | ---: | ---: | ---: |
| `clinic_intake_corrections` | 3 | 0 | 0 | 2 | 0 |
| `grant_review_queue` | 3 | 0 | 1 | 2 | 0 |
| `library_preservation_queue` | 0 | 0 | 0 | 0 | 0 |
| `permit_renewal_docket` | 0 | 0 | 2 | 2 | 0 |
| `warehouse_repair_log` | 3 | 0 | 0 | 0 | 0 |
| `water_sample_docket` | 0 | 1 | 0 | 1 | 0 |

## Findings

### `clinic_intake_corrections`

- `alias_split`: `code`='ci44', `variants`=['case_ci_44', 'ci_44']
  - identity code `ci44` appears as case_ci_44, ci_44
- `alias_split`: `code`='ms9', `variants`=['artifact_ms_9', 'ms_9']
  - identity code `ms9` appears as artifact_ms_9, ms_9
- `alias_split`: `code`='r44', `variants`=['artifact_r_44', 'r_44']
  - identity code `r44` appears as artifact_r_44, r_44
- `phase_classification_missing`: `phase`='initial'
  - on_2026_02_02_intake_aide_mara_chen_received_referral_r_44_from_the_front_desk_and_filed_ci_44_with_status_pending_triage
- `phase_classification_missing`: `phase`='current'
  - on_2026_02_09_coordinator_lina_fox_closed_ci_44_as_scheduled_for_standard_afternoon_therapy_the_current_status_is_scheduled

### `grant_review_queue`

- `alias_split`: `code`='gq5', `variants`=['gq_5', 'queue_gq_5']
  - identity code `gq5` appears as gq_5, queue_gq_5
- `alias_split`: `code`='l5', `variants`=['document_l_5', 'l_5']
  - identity code `l5` appears as document_l_5, l_5
- `alias_split`: `code`='p5', `variants`=['p_5', 'proposal_p_5']
  - identity code `p5` appears as p_5, proposal_p_5
- `supersession_target_collapse`: `fact`='supersedes(reinstated_eligibility, denied_eligibility).', `source_target_codes`=[]
  - on_2026_05_07_eligibility_approval_was_reinstated_and_the_earlier_denial_was_superseded
- `phase_classification_missing`: `phase`='initial'
  - on_2026_05_02_grants_clerk_ilya_ren_received_proposal_p_5_and_filed_it_with_status_pending_eligibility_check
- `phase_classification_missing`: `phase`='current'
  - on_2026_05_10_director_mei_holt_closed_gq_5_as_approved_for_the_tool_shed_without_the_solar_panel_line_the_current_status_is_approved_with_revised_budget

### `permit_renewal_docket`

- `supersession_target_collapse`: `fact`='status_superseded_by(pr_18, approved, pending_payment_status).', `source_target_codes`=['h2', 'pr18']
  - on_2026_01_12_payment_failed_the_approval_was_superseded_by_hold_notice_h_2_and_pr_18_returned_to_pending_payment_status
- `supersession_target_collapse`: `fact`='status_superseded_by(pr_18, approved, hold).', `source_target_codes`=['h2', 'pr18']
  - on_2026_01_12_payment_failed_the_approval_was_superseded_by_hold_notice_h_2_and_pr_18_returned_to_pending_payment_status
- `phase_classification_missing`: `phase`='initial'
  - on_2026_01_04_clerk_erin_moss_received_application_a_18_and_filed_it_as_pr_18_the_initial_status_was_pending_completeness_review
- `phase_classification_missing`: `phase`='current'
  - on_2026_01_20_supervisor_vale_closed_pr_18_as_approved_for_weekday_operation_only_the_current_status_of_pr_18_is_approved_weekday_renewal

### `warehouse_repair_log`

- `alias_split`: `code`='s6', `variants`=['asset_scanner_s6', 's_6']
  - identity code `s6` appears as asset_scanner_s6, s_6
- `alias_split`: `code`='wr62', `variants`=['evt_receive_wr62', 'ticket_wr_62', 'wr_62']
  - identity code `wr62` appears as evt_receive_wr62, ticket_wr_62, wr_62
- `alias_split`: `code`='wr63', `variants`=['ticket_wr_63', 'wr_63']
  - identity code `wr63` appears as ticket_wr_63, wr_63

### `water_sample_docket`

- `ambiguous_repeated_verb`: `verb`='received', `predicate_surfaces`=[]
  - on_2026_04_10_field_collector_niko_shah_received_sample_b_12_and_filed_docket_ws_12_with_status_pending_lab_receipt
  - on_2026_04_11_lab_desk_ada_voss_logged_b_12_as_received_and_assigned_it_to_nitrate_testing
- `phase_classification_missing`: `phase`='initial'
  - on_2026_04_10_field_collector_niko_shah_received_sample_b_12_and_filed_docket_ws_12_with_status_pending_lab_receipt
