# Operational Lifecycle Palette Audit

- Schema: `operational_lifecycle_palette_audit_v1`
- Compiles: `6`
- Class counts: `{'phase_classification_missing': 7, 'alias_split': 6, 'supersession_target_collapse': 1, 'shallow_lifecycle_palette': 1, 'ambiguous_repeated_verb': 1}`
- Fixtures with findings: `6`

## Fixture Summary

| Fixture | Alias Split | Ambiguous Verb | Supersession Collapse | Phase Missing | Shallow Palette |
| --- | ---: | ---: | ---: | ---: | ---: |
| `clinic_intake_corrections` | 0 | 0 | 0 | 2 | 0 |
| `grant_review_queue` | 3 | 0 | 1 | 2 | 1 |
| `library_preservation_queue` | 0 | 1 | 0 | 0 | 0 |
| `permit_renewal_docket` | 0 | 0 | 0 | 2 | 0 |
| `warehouse_repair_log` | 1 | 0 | 0 | 0 | 0 |
| `water_sample_docket` | 2 | 0 | 0 | 1 | 0 |

## Findings

### `clinic_intake_corrections`

- `phase_classification_missing`: `phase`='initial'
  - on_2026_02_02_intake_aide_mara_chen_received_referral_r_44_from_the_front_desk_and_filed_ci_44_with_status_pending_triage
- `phase_classification_missing`: `phase`='current'
  - on_2026_02_09_coordinator_lina_fox_closed_ci_44_as_scheduled_for_standard_afternoon_therapy_the_current_status_is_scheduled

### `grant_review_queue`

- `alias_split`: `code`='gq5', `variants`=['gq_5', 'queue_gq5', 'queue_gq_5']
  - identity code `gq5` appears as gq_5, queue_gq5, queue_gq_5
- `alias_split`: `code`='l5', `variants`=['artifact_l_5', 'l_5', 'letter_l5']
  - identity code `l5` appears as artifact_l_5, l_5, letter_l5
- `alias_split`: `code`='p5', `variants`=['artifact_p_5', 'p_5', 'proposal_p5', 'proposal_p_5']
  - identity code `p5` appears as artifact_p_5, p_5, proposal_p5, proposal_p_5
- `supersession_target_collapse`: `fact`='superseded_by(denied, reinstated).', `source_target_codes`=[]
  - on_2026_05_07_eligibility_approval_was_reinstated_and_the_earlier_denial_was_superseded
- `phase_classification_missing`: `phase`='initial'
  - on_2026_05_02_grants_clerk_ilya_ren_received_proposal_p_5_and_filed_it_with_status_pending_eligibility_check
- `phase_classification_missing`: `phase`='current'
  - on_2026_05_10_director_mei_holt_closed_gq_5_as_approved_for_the_tool_shed_without_the_solar_panel_line_the_current_status_is_approved_with_revised_budget
- `shallow_lifecycle_palette`: `source_signal_count`=4, `candidate_count`=13, `nearby_signatures`=['event_date/2', 'proposal_status/2', 'status_changed_on/2', 'superseded_by/2', 'queue_status/2', 'final_state/2']
  - on_2026_05_02_grants_clerk_ilya_ren_received_proposal_p_5_and_filed_it_with_status_pending_eligibility_check
  - on_2026_05_05_eligibility_staff_denied_eligibility_approval_for_lack_of_the_match_letter

### `library_preservation_queue`

- `ambiguous_repeated_verb`: `verb`='approved', `predicate_surfaces`=['final_status']
  - on_2026_06_06_a_prior_digitization_only_plan_was_superseded_by_the_approved_display_plan
  - on_2026_06_08_lq_31_was_closed_as_approved_for_low_light_display_only_the_current_preservation_status_is_display_approved_with_handling_restricted

### `permit_renewal_docket`

- `phase_classification_missing`: `phase`='initial'
  - on_2026_01_04_clerk_erin_moss_received_application_a_18_and_filed_it_as_pr_18_the_initial_status_was_pending_completeness_review
- `phase_classification_missing`: `phase`='current'
  - on_2026_01_20_supervisor_vale_closed_pr_18_as_approved_for_weekday_operation_only_the_current_status_of_pr_18_is_approved_weekday_renewal

### `warehouse_repair_log`

- `alias_split`: `code`='s6', `variants`=['s_6', 'scanner_s_6']
  - identity code `s6` appears as s_6, scanner_s_6

### `water_sample_docket`

- `alias_split`: `code`='b12', `variants`=['b_12', 'sample_b12', 'sample_b_12']
  - identity code `b12` appears as b_12, sample_b12, sample_b_12
- `alias_split`: `code`='ws12', `variants`=['docket_ws12', 'docket_ws_12', 'ws_12']
  - identity code `ws12` appears as docket_ws12, docket_ws_12, ws_12
- `phase_classification_missing`: `phase`='initial'
  - on_2026_04_10_field_collector_niko_shah_received_sample_b_12_and_filed_docket_ws_12_with_status_pending_lab_receipt
