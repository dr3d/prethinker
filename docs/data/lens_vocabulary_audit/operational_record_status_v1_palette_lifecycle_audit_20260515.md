# Operational Lifecycle Palette Audit

- Schema: `operational_lifecycle_palette_audit_v1`
- Compiles: `6`
- Class counts: `{'alias_split': 6, 'supersession_target_collapse': 2, 'phase_classification_missing': 7, 'ambiguous_repeated_verb': 1}`
- Fixtures with findings: `4`

## Fixture Summary

| Fixture | Alias Split | Ambiguous Verb | Supersession Collapse | Phase Missing |
| --- | ---: | ---: | ---: | ---: |
| `clinic_intake_corrections` | 1 | 0 | 2 | 2 |
| `grant_review_queue` | 3 | 0 | 0 | 2 |
| `library_preservation_queue` | 0 | 0 | 0 | 0 |
| `permit_renewal_docket` | 0 | 1 | 0 | 2 |
| `warehouse_repair_log` | 0 | 0 | 0 | 0 |
| `water_sample_docket` | 2 | 0 | 0 | 1 |

## Findings

### `clinic_intake_corrections`

- `alias_split`: `code`='ci44', `variants`=['ci_44', 'evt_ci44_approved', 'evt_ci44_closed', 'evt_ci44_corrected', 'evt_ci44_denied', 'evt_ci44_received', 'evt_ci44_reopened', 'evt_ci44_routed']
  - identity code `ci44` appears as ci_44, evt_ci44_approved, evt_ci44_closed, evt_ci44_corrected, evt_ci44_denied, evt_ci44_received, evt_ci44_reopened, evt_ci44_routed
- `supersession_target_collapse`: `fact`='record_superseded_by(denied, pending_nurse_review).', `source_target_codes`=['ms9']
  - on_2026_02_05_the_front_desk_corrected_the_referral_by_adding_mobility_score_ms_9_the_denied_scheduling_status_was_superseded_by_pending_nurse_review
- `supersession_target_collapse`: `fact`='record_superseded_by(denied_scheduling, pending_nurse_review).', `source_target_codes`=['ms9']
  - on_2026_02_05_the_front_desk_corrected_the_referral_by_adding_mobility_score_ms_9_the_denied_scheduling_status_was_superseded_by_pending_nurse_review
- `phase_classification_missing`: `phase`='initial'
  - on_2026_02_02_intake_aide_mara_chen_received_referral_r_44_from_the_front_desk_and_filed_ci_44_with_status_pending_triage
- `phase_classification_missing`: `phase`='current'
  - on_2026_02_09_coordinator_lina_fox_closed_ci_44_as_scheduled_for_standard_afternoon_therapy_the_current_status_is_scheduled

### `grant_review_queue`

- `alias_split`: `code`='gq5', `variants`=['queue_gq5', 'record_gq5']
  - identity code `gq5` appears as queue_gq5, record_gq5
- `alias_split`: `code`='l5', `variants`=['letter_l5', 'record_l5']
  - identity code `l5` appears as letter_l5, record_l5
- `alias_split`: `code`='p5', `variants`=['proposal_p5', 'proposal_p_5', 'record_p5']
  - identity code `p5` appears as proposal_p5, proposal_p_5, record_p5
- `phase_classification_missing`: `phase`='initial'
  - on_2026_05_02_grants_clerk_ilya_ren_received_proposal_p_5_and_filed_it_with_status_pending_eligibility_check
- `phase_classification_missing`: `phase`='current'
  - on_2026_05_10_director_mei_holt_closed_gq_5_as_approved_for_the_tool_shed_without_the_solar_panel_line_the_current_status_is_approved_with_revised_budget

### `permit_renewal_docket`

- `ambiguous_repeated_verb`: `verb`='received', `predicate_surfaces`=[]
  - on_2026_01_04_clerk_erin_moss_received_application_a_18_and_filed_it_as_pr_18_the_initial_status_was_pending_completeness_review
  - on_2026_01_18_payment_was_received_and_the_permit_was_reopened_for_final_issuance
- `phase_classification_missing`: `phase`='initial'
  - on_2026_01_04_clerk_erin_moss_received_application_a_18_and_filed_it_as_pr_18_the_initial_status_was_pending_completeness_review
- `phase_classification_missing`: `phase`='current'
  - on_2026_01_20_supervisor_vale_closed_pr_18_as_approved_for_weekday_operation_only_the_current_status_of_pr_18_is_approved_weekday_renewal

### `water_sample_docket`

- `alias_split`: `code`='b12', `variants`=['sample_b12', 'sample_b_12']
  - identity code `b12` appears as sample_b12, sample_b_12
- `alias_split`: `code`='ws12', `variants`=['docket_ws12', 'docket_ws_12', 'ws_12']
  - identity code `ws12` appears as docket_ws12, docket_ws_12, ws_12
- `phase_classification_missing`: `phase`='initial'
  - on_2026_04_10_field_collector_niko_shah_received_sample_b_12_and_filed_docket_ws_12_with_status_pending_lab_receipt
