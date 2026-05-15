# Operational Lifecycle Palette Audit

- Schema: `operational_lifecycle_palette_audit_v1`
- Compiles: `6`
- Class counts: `{'phase_classification_missing': 6, 'alias_split': 4, 'ambiguous_repeated_verb': 2, 'supersession_target_collapse': 1}`
- Fixtures with findings: `4`

## Fixture Summary

| Fixture | Alias Split | Ambiguous Verb | Supersession Collapse | Phase Missing |
| --- | ---: | ---: | ---: | ---: |
| `clinic_intake_corrections` | 0 | 0 | 0 | 1 |
| `grant_review_queue` | 2 | 0 | 0 | 2 |
| `library_preservation_queue` | 0 | 0 | 0 | 0 |
| `permit_renewal_docket` | 1 | 1 | 1 | 2 |
| `warehouse_repair_log` | 0 | 0 | 0 | 0 |
| `water_sample_docket` | 1 | 1 | 0 | 1 |

## Findings

### `clinic_intake_corrections`

- `phase_classification_missing`: `phase`='initial'
  - on_2026_02_02_intake_aide_mara_chen_received_referral_r_44_from_the_front_desk_and_filed_ci_44_with_status_pending_triage

### `grant_review_queue`

- `alias_split`: `code`='gq5', `variants`=['gq_5', 'queue_gq5']
  - identity code `gq5` appears as gq_5, queue_gq5
- `alias_split`: `code`='p5', `variants`=['p_5', 'proposal_p5']
  - identity code `p5` appears as p_5, proposal_p5
- `phase_classification_missing`: `phase`='initial'
  - on_2026_05_02_grants_clerk_ilya_ren_received_proposal_p_5_and_filed_it_with_status_pending_eligibility_check
- `phase_classification_missing`: `phase`='current'
  - on_2026_05_10_director_mei_holt_closed_gq_5_as_approved_for_the_tool_shed_without_the_solar_panel_line_the_current_status_is_approved_with_revised_budget

### `permit_renewal_docket`

- `alias_split`: `code`='pr18', `variants`=['applicant_pr18', 'pr_18']
  - identity code `pr18` appears as applicant_pr18, pr_18
- `ambiguous_repeated_verb`: `verb`='received', `predicate_surfaces`=['action_performed']
  - on_2026_01_04_clerk_erin_moss_received_application_a_18_and_filed_it_as_pr_18_the_initial_status_was_pending_completeness_review
  - on_2026_01_18_payment_was_received_and_the_permit_was_reopened_for_final_issuance
- `supersession_target_collapse`: `fact`='status_superseded_by(approved_subject_to_payment, pending_payment).', `source_target_codes`=['h2', 'pr18']
  - on_2026_01_12_payment_failed_the_approval_was_superseded_by_hold_notice_h_2_and_pr_18_returned_to_pending_payment_status
- `phase_classification_missing`: `phase`='initial'
  - on_2026_01_04_clerk_erin_moss_received_application_a_18_and_filed_it_as_pr_18_the_initial_status_was_pending_completeness_review
- `phase_classification_missing`: `phase`='current'
  - on_2026_01_20_supervisor_vale_closed_pr_18_as_approved_for_weekday_operation_only_the_current_status_of_pr_18_is_approved_weekday_renewal

### `water_sample_docket`

- `alias_split`: `code`='b12', `variants`=['b_12', 'sample_b12']
  - identity code `b12` appears as b_12, sample_b12
- `ambiguous_repeated_verb`: `verb`='received', `predicate_surfaces`=['sample_received']
  - on_2026_04_10_field_collector_niko_shah_received_sample_b_12_and_filed_docket_ws_12_with_status_pending_lab_receipt
  - on_2026_04_11_lab_desk_ada_voss_logged_b_12_as_received_and_assigned_it_to_nitrate_testing
- `phase_classification_missing`: `phase`='initial'
  - on_2026_04_10_field_collector_niko_shah_received_sample_b_12_and_filed_docket_ws_12_with_status_pending_lab_receipt
