# Compile Surface Stability Audit

- Compiles: `18`
- Fixtures: `6`
- Stable fixtures: `0`
- Unstable fixtures: `6`
- Unstable direct facts: `679`
- Predicate drift rows: `183`
- Surface drift rows: `35`

## `clinic_intake_corrections`

- Draws: `3`
- Stable: `False`
- Common / union direct facts: `0 / 125`
- Unstable direct facts: `125`

| Predicate | Counts | Delta |
| --- | --- | ---: |
| `acted_as` | `[0, 4, 0]` | 4 |
| `actor_performed` | `[6, 0, 0]` | 6 |
| `actor_role` | `[0, 0, 12]` | 12 |
| `actor_role_at` | `[4, 0, 0]` | 4 |
| `approved` | `[0, 1, 0]` | 1 |
| `attribute_missing` | `[1, 0, 0]` | 1 |
| `case_closed` | `[1, 0, 0]` | 1 |
| `case_id` | `[0, 1, 0]` | 1 |
| `case_reopened` | `[1, 0, 0]` | 1 |
| `case_status` | `[2, 0, 0]` | 2 |
| `closed` | `[0, 2, 0]` | 2 |
| `current_status` | `[1, 1, 0]` | 1 |
| `denied` | `[0, 1, 0]` | 1 |
| `has_attribute` | `[0, 1, 0]` | 1 |
| `has_attribute_value` | `[0, 0, 1]` | 1 |
| `lacks_attribute` | `[0, 1, 0]` | 1 |
| `occurred_on` | `[0, 18, 0]` | 18 |
| `person_id` | `[0, 3, 0]` | 3 |
| `record_correction` | `[0, 0, 2]` | 2 |
| `record_lifecycle_event` | `[0, 0, 27]` | 27 |
| `record_status_phase` | `[0, 0, 8]` | 8 |
| `record_superseded_by` | `[0, 0, 2]` | 2 |
| `record_withdrawal` | `[0, 0, 1]` | 1 |
| `recorded_by` | `[0, 5, 0]` | 5 |
| `recorded_in` | `[0, 0, 2]` | 2 |
| `referral_corrected` | `[1, 0, 0]` | 1 |
| `referral_id` | `[0, 1, 0]` | 1 |
| `reopened` | `[0, 2, 0]` | 2 |
| `request_withdrawn` | `[1, 0, 0]` | 1 |
| `role_id` | `[0, 3, 0]` | 3 |
| `status_transition` | `[1, 5, 0]` | 5 |
| `status_transition_reason` | `[1, 0, 0]` | 1 |
| `withdrew_request` | `[0, 2, 0]` | 2 |

| Surface | Counts | Delta |
| --- | --- | ---: |
| `completion_transition_surface` | `[3, 9, 6]` | 6 |
| `identity_role_surface` | `[10, 6, 12]` | 6 |
| `object_record_surface` | `[1, 7, 42]` | 41 |
| `status_phase_surface` | `[6, 15, 15]` | 9 |
| `task_scope_surface` | `[2, 10, 5]` | 8 |

| Draw | Contract | Status | Source signals | Direct surfaces | Complete | Partial |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| `lens_vocab_operational_record_status_actor_content_compile_20260515` | `parallel_assignment_event_preservation` | `not_applicable` | 0 | 0 |  |  |
| `lens_vocab_operational_record_status_actor_content_compile_20260515` | `source_authority_pair_preservation` | `not_applicable` | 0 | 0 | 0 | 0 |
| `lens_vocab_operational_record_status_compile_20260515` | `parallel_assignment_event_preservation` | `not_applicable` | 0 | 0 |  |  |
| `lens_vocab_operational_record_status_compile_20260515` | `source_authority_pair_preservation` | `not_applicable` | 0 | 0 | 0 | 0 |
| `lens_vocab_operational_record_status_palette_compile_20260515` | `parallel_assignment_event_preservation` | `not_applicable` | 0 | 0 |  |  |
| `lens_vocab_operational_record_status_palette_compile_20260515` | `source_authority_pair_preservation` | `not_applicable` | 0 | 0 | 0 | 0 |

### Missing From `lens_vocab_operational_record_status_actor_content_compile_20260515`

- Missing union facts: `105`
- `acted_as(eben_ross, nurse).`
- `acted_as(eben_ross, triage_nurse).`
- `acted_as(lina_fox, coordinator).`
- `acted_as(mara_chen, intake_aide).`
- `actor_role(eben_ross, evt_004, triage_nurse).`
- `actor_role(eben_ross, evt_013, nurse).`
- `actor_role(eben_ross, evt_20260203_01, triage_nurse).`
- `actor_role(eben_ross, evt_20260206_01, nurse).`
- `actor_role(eben_ross, evt_ci44_approved, nurse).`
- `actor_role(eben_ross, evt_ci44_routed, triage_nurse).`
- `actor_role(lina_fox, evt_018, coordinator).`
- `actor_role(lina_fox, evt_20260209_01, coordinator).`
- `actor_role(lina_fox, evt_ci44_closed, coordinator).`
- `actor_role(mara_chen, evt_001, intake_aide).`
- `actor_role(mara_chen, evt_20260202_01, intake_aide).`
- `actor_role(mara_chen, evt_ci44_received, intake_aide).`
- `approved(ci_44, standard_scheduling).`
- `case_id(ci_44).`
- `closed(ci_44, scheduled).`
- `closed(ci_44, scheduled_for_standard_afternoon_therapy).`
- `denied(ci_44, immediate_scheduling_because_the_referral_lacked_a_mobility_score).`
- `has_attribute(r_44, mobility_score, ms_9).`
- `has_attribute_value(r_44, mobility_score, ms_9).`
- `lacks_attribute(r_44, mobility_score).`
- `occurred_on(event_0202, 2026_02_02, mara_chen_received_referral_r_44_and_filed_ci_44_with_status_pending_triage).`

### Missing From `lens_vocab_operational_record_status_compile_20260515`

- Missing union facts: `74`
- `actor_performed(eben_ross, approved_scheduling, ci_44, 2026_02_06).`
- `actor_performed(eben_ross, approved_standard_scheduling, ci_44, 2026_02_06).`
- `actor_performed(eben_ross, routed_to_review, ci_44, 2026_02_03).`
- `actor_performed(front_desk, corrected_referral, r_44, 2026_02_05).`
- `actor_performed(mara_chen, filed_case, ci_44, 2026_02_02).`
- `actor_performed(mara_chen, received_referral, r_44, 2026_02_02).`
- `actor_role(eben_ross, evt_004, triage_nurse).`
- `actor_role(eben_ross, evt_013, nurse).`
- `actor_role(eben_ross, evt_20260203_01, triage_nurse).`
- `actor_role(eben_ross, evt_20260206_01, nurse).`
- `actor_role(eben_ross, evt_ci44_approved, nurse).`
- `actor_role(eben_ross, evt_ci44_routed, triage_nurse).`
- `actor_role(lina_fox, evt_018, coordinator).`
- `actor_role(lina_fox, evt_20260209_01, coordinator).`
- `actor_role(lina_fox, evt_ci44_closed, coordinator).`
- `actor_role(mara_chen, evt_001, intake_aide).`
- `actor_role(mara_chen, evt_20260202_01, intake_aide).`
- `actor_role(mara_chen, evt_ci44_received, intake_aide).`
- `actor_role_at(eben_ross, nurse, 2026_02_06).`
- `actor_role_at(eben_ross, triage_nurse, 2026_02_03).`
- `actor_role_at(lina_fox, coordinator, 2026_02_09).`
- `actor_role_at(mara_chen, intake_aide, 2026_02_02).`
- `attribute_missing(r_44, mobility_score, 2026_02_04).`
- `case_closed(ci_44, scheduled_for_standard_afternoon_therapy, 2026_02_09).`
- `case_reopened(ci_44, 2026_02_08).`

### Missing From `lens_vocab_operational_record_status_palette_compile_20260515`

- Missing union facts: `70`
- `acted_as(eben_ross, nurse).`
- `acted_as(eben_ross, triage_nurse).`
- `acted_as(lina_fox, coordinator).`
- `acted_as(mara_chen, intake_aide).`
- `actor_performed(eben_ross, approved_scheduling, ci_44, 2026_02_06).`
- `actor_performed(eben_ross, approved_standard_scheduling, ci_44, 2026_02_06).`
- `actor_performed(eben_ross, routed_to_review, ci_44, 2026_02_03).`
- `actor_performed(front_desk, corrected_referral, r_44, 2026_02_05).`
- `actor_performed(mara_chen, filed_case, ci_44, 2026_02_02).`
- `actor_performed(mara_chen, received_referral, r_44, 2026_02_02).`
- `actor_role_at(eben_ross, nurse, 2026_02_06).`
- `actor_role_at(eben_ross, triage_nurse, 2026_02_03).`
- `actor_role_at(lina_fox, coordinator, 2026_02_09).`
- `actor_role_at(mara_chen, intake_aide, 2026_02_02).`
- `approved(ci_44, standard_scheduling).`
- `attribute_missing(r_44, mobility_score, 2026_02_04).`
- `case_closed(ci_44, scheduled_for_standard_afternoon_therapy, 2026_02_09).`
- `case_id(ci_44).`
- `case_reopened(ci_44, 2026_02_08).`
- `case_status(ci_44, denied, 2026_02_04).`
- `case_status(ci_44, pending_triage, 2026_02_02).`
- `closed(ci_44, scheduled).`
- `closed(ci_44, scheduled_for_standard_afternoon_therapy).`
- `current_status(ci_44, scheduled).`
- `denied(ci_44, immediate_scheduling_because_the_referral_lacked_a_mobility_score).`

## `grant_review_queue`

- Draws: `3`
- Stable: `False`
- Common / union direct facts: `0 / 123`
- Unstable direct facts: `123`

| Predicate | Counts | Delta |
| --- | --- | ---: |
| `acted_as` | `[8, 0, 0]` | 8 |
| `assigned_to` | `[2, 0, 0]` | 2 |
| `closed` | `[3, 0, 0]` | 3 |
| `content_modified` | `[2, 0, 0]` | 2 |
| `document` | `[1, 0, 0]` | 1 |
| `document_reference` | `[0, 3, 0]` | 3 |
| `entity_attribute` | `[0, 2, 0]` | 2 |
| `entity_type` | `[0, 6, 0]` | 6 |
| `event` | `[0, 19, 0]` | 19 |
| `event_cause` | `[0, 5, 0]` | 5 |
| `line_item` | `[2, 0, 0]` | 2 |
| `person` | `[3, 0, 0]` | 3 |
| `person_role` | `[0, 6, 3]` | 6 |
| `proposal` | `[1, 0, 0]` | 1 |
| `queue` | `[1, 0, 0]` | 1 |
| `record_content_modification` | `[0, 0, 2]` | 2 |
| `record_id` | `[0, 0, 5]` | 5 |
| `record_lifecycle_event` | `[0, 0, 9]` | 9 |
| `record_status_phase` | `[0, 0, 4]` | 4 |
| `record_superseded_by` | `[0, 0, 1]` | 1 |
| `reopened` | `[2, 0, 0]` | 2 |
| `status_at` | `[15, 0, 0]` | 15 |
| `status_change_event` | `[12, 0, 0]` | 12 |
| `status_superseded` | `[0, 2, 0]` | 2 |
| `supersedes` | `[2, 0, 0]` | 2 |
| `withdrawn` | `[2, 0, 0]` | 2 |

| Surface | Counts | Delta |
| --- | --- | ---: |
| `assignment_binding_surface` | `[9, 3, 1]` | 8 |
| `completion_transition_surface` | `[5, 2, 1]` | 4 |
| `identity_role_surface` | `[6, 25, 11]` | 19 |
| `object_record_surface` | `[0, 5, 21]` | 21 |
| `status_phase_surface` | `[31, 5, 5]` | 26 |
| `task_scope_surface` | `[10, 7, 2]` | 8 |

| Draw | Contract | Status | Source signals | Direct surfaces | Complete | Partial |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| `lens_vocab_operational_record_status_actor_content_compile_20260515` | `parallel_assignment_event_preservation` | `not_applicable` | 1 | 2 |  |  |
| `lens_vocab_operational_record_status_actor_content_compile_20260515` | `source_authority_pair_preservation` | `not_applicable` | 0 | 0 | 0 | 0 |
| `lens_vocab_operational_record_status_compile_20260515` | `parallel_assignment_event_preservation` | `not_applicable` | 1 | 0 |  |  |
| `lens_vocab_operational_record_status_compile_20260515` | `source_authority_pair_preservation` | `not_applicable` | 0 | 0 | 0 | 0 |
| `lens_vocab_operational_record_status_palette_compile_20260515` | `parallel_assignment_event_preservation` | `not_applicable` | 1 | 0 |  |  |
| `lens_vocab_operational_record_status_palette_compile_20260515` | `source_authority_pair_preservation` | `not_applicable` | 0 | 0 | 0 | 0 |

### Missing From `lens_vocab_operational_record_status_actor_content_compile_20260515`

- Missing union facts: `67`
- `document_reference(event_evt_20260506, entity_l_5, sponsor_letter).`
- `document_reference(evt_20260506_01, doc_l5, sponsor_letter).`
- `document_reference(evt_20260506_correction, doc_l5, sponsor_letter).`
- `entity_attribute(entity_p5, approved_without_solar_panel, true).`
- `entity_attribute(entity_p_5, final_status, approved_without_solar_panel).`
- `entity_type(entity_gq_5, grant_queue).`
- `entity_type(entity_l_5, document).`
- `entity_type(entity_p_5, proposal).`
- `entity_type(gq_5, queue).`
- `entity_type(l_5, document).`
- `entity_type(p_5, proposal).`
- `event(event_evt_20260502, 2026_05_02, person_ilya_ren, received_and_filed).`
- `event(event_evt_20260504, 2026_05_04, person_sana_cole, assigned_to_budget_review).`
- `event(event_evt_20260505, 2026_05_05, person_eligibility_staff, denied_eligibility).`
- `event(event_evt_20260506, 2026_05_06, person_applicant, corrected_file).`
- `event(event_evt_20260507, 2026_05_07, person_eligibility_staff, reinstated_approval).`
- `event(event_evt_20260508, 2026_05_08, person_applicant, withdrew_solar_panel_item).`
- `event(event_evt_20260509, 2026_05_09, person_budget_reviewer, reopened_proposal).`
- `event(event_evt_20260510, 2026_05_10, person_mei_holt, closed_approved).`
- `event(evt_20260502_01, 2026_05_02, person_ilya_ren, received_and_filed).`
- `event(evt_20260504_01, 2026_05_04, person_sana_cole, assigned_to_budget_review).`
- `event(evt_20260504_assign, 2026_05_04, person_sana_cole, assigned_to_budget_review).`
- `event(evt_20260505_01, 2026_05_05, person_eligibility_staff, denied_eligibility).`
- `event(evt_20260505_denial, 2026_05_05, person_eligibility_staff, denied_eligibility_approval).`
- `event(evt_20260506_01, 2026_05_06, person_sponsor, corrected_file).`

### Missing From `lens_vocab_operational_record_status_compile_20260515`

- Missing union facts: `80`
- `acted_as(eligibility_staff, eligibility_staff, evt_003).`
- `acted_as(eligibility_staff, eligibility_staff, evt_004).`
- `acted_as(ilya_ren, grants_clerk, evt_001).`
- `acted_as(mei_holt, director, evt_006).`
- `acted_as(person_ilya_ren, grants_clerk, evt_received_20260502).`
- `acted_as(person_mei_holt, director, evt_closed_20260510).`
- `acted_as(person_sana_cole, reviewer, evt_assigned_20260504).`
- `acted_as(sana_cole, reviewer, evt_002).`
- `assigned_to(evt_002, p_5, budget_review).`
- `assigned_to(evt_assigned_20260504, proposal_p5, budget_review).`
- `closed(evt_006, gq_5).`
- `closed(evt_close_20260510, gq_5).`
- `closed(evt_closed_20260510, queue_gq5).`
- `content_modified(evt_corrected_20260506, lineitem_solar_panel, match_evidence_present).`
- `content_modified(evt_withdrawal_20260508, solar_panel_line_item, withdrawn).`
- `document(document_l5).`
- `line_item(lineitem_solar_panel).`
- `line_item(solar_panel_line_item).`
- `person(person_ilya_ren).`
- `person(person_mei_holt).`
- `person(person_sana_cole).`
- `person_role(person_ilya_ren, clerk).`
- `person_role(person_mei_holt, director).`
- `person_role(person_sana_cole, reviewer).`
- `proposal(proposal_p5).`

### Missing From `lens_vocab_operational_record_status_palette_compile_20260515`

- Missing union facts: `99`
- `acted_as(eligibility_staff, eligibility_staff, evt_003).`
- `acted_as(eligibility_staff, eligibility_staff, evt_004).`
- `acted_as(ilya_ren, grants_clerk, evt_001).`
- `acted_as(mei_holt, director, evt_006).`
- `acted_as(person_ilya_ren, grants_clerk, evt_received_20260502).`
- `acted_as(person_mei_holt, director, evt_closed_20260510).`
- `acted_as(person_sana_cole, reviewer, evt_assigned_20260504).`
- `acted_as(sana_cole, reviewer, evt_002).`
- `assigned_to(evt_002, p_5, budget_review).`
- `assigned_to(evt_assigned_20260504, proposal_p5, budget_review).`
- `closed(evt_006, gq_5).`
- `closed(evt_close_20260510, gq_5).`
- `closed(evt_closed_20260510, queue_gq5).`
- `content_modified(evt_corrected_20260506, lineitem_solar_panel, match_evidence_present).`
- `content_modified(evt_withdrawal_20260508, solar_panel_line_item, withdrawn).`
- `document(document_l5).`
- `document_reference(event_evt_20260506, entity_l_5, sponsor_letter).`
- `document_reference(evt_20260506_01, doc_l5, sponsor_letter).`
- `document_reference(evt_20260506_correction, doc_l5, sponsor_letter).`
- `entity_attribute(entity_p5, approved_without_solar_panel, true).`
- `entity_attribute(entity_p_5, final_status, approved_without_solar_panel).`
- `entity_type(entity_gq_5, grant_queue).`
- `entity_type(entity_l_5, document).`
- `entity_type(entity_p_5, proposal).`
- `entity_type(gq_5, queue).`

## `library_preservation_queue`

- Draws: `3`
- Stable: `False`
- Common / union direct facts: `0 / 131`
- Unstable direct facts: `131`

| Predicate | Counts | Delta |
| --- | --- | ---: |
| `actor_id` | `[0, 2, 0]` | 2 |
| `actor_role` | `[0, 2, 0]` | 2 |
| `asset_condition_at` | `[0, 2, 0]` | 2 |
| `asset_id` | `[0, 1, 0]` | 1 |
| `assigned_role` | `[2, 0, 0]` | 2 |
| `condition_corrected` | `[0, 1, 0]` | 1 |
| `corrected_value` | `[2, 0, 0]` | 2 |
| `current_handling_restriction` | `[0, 1, 0]` | 1 |
| `decision_constraint` | `[5, 0, 0]` | 5 |
| `decision_made` | `[5, 0, 0]` | 5 |
| `decision_reason` | `[2, 0, 0]` | 2 |
| `entity_id` | `[4, 0, 8]` | 8 |
| `entity_type` | `[0, 0, 3]` | 3 |
| `event_actor` | `[3, 0, 0]` | 3 |
| `event_date` | `[15, 8, 0]` | 15 |
| `event_occurred` | `[0, 12, 0]` | 12 |
| `event_type` | `[13, 0, 0]` | 13 |
| `original_value` | `[2, 0, 0]` | 2 |
| `plan_approved_for` | `[0, 2, 0]` | 2 |
| `plan_denied` | `[0, 2, 0]` | 2 |
| `plan_entity` | `[0, 0, 4]` | 4 |
| `plan_superseded_by` | `[0, 2, 0]` | 2 |
| `plan_withdrawn` | `[0, 2, 0]` | 2 |
| `queue_contains` | `[0, 1, 0]` | 1 |
| `queue_id` | `[0, 1, 0]` | 1 |
| `queue_linked_to_case` | `[1, 0, 0]` | 1 |
| `queue_status_at` | `[0, 3, 0]` | 3 |
| `queue_status_changed` | `[3, 0, 0]` | 3 |
| `record_assigned_to` | `[0, 0, 1]` | 1 |
| `record_correction` | `[0, 0, 1]` | 1 |
| `record_decision` | `[0, 0, 3]` | 3 |
| `record_lifecycle_event` | `[0, 0, 1]` | 1 |
| `record_received` | `[0, 0, 1]` | 1 |
| `record_status_phase` | `[0, 0, 3]` | 3 |
| `record_superseded_by` | `[0, 0, 2]` | 2 |
| `recorded_in` | `[4, 0, 0]` | 4 |
| `request_withdrawn` | `[2, 0, 0]` | 2 |
| `superseded_by` | `[1, 0, 0]` | 1 |

| Surface | Counts | Delta |
| --- | --- | ---: |
| `assignment_binding_surface` | `[4, 2, 1]` | 3 |
| `completion_transition_surface` | `[4, 2, 2]` | 2 |
| `identity_role_surface` | `[7, 4, 0]` | 7 |
| `object_record_surface` | `[4, 0, 13]` | 13 |
| `status_phase_surface` | `[5, 4, 4]` | 1 |
| `task_scope_surface` | `[3, 3, 1]` | 2 |

| Draw | Contract | Status | Source signals | Direct surfaces | Complete | Partial |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| `lens_vocab_operational_record_status_actor_content_compile_20260515` | `parallel_assignment_event_preservation` | `not_applicable` | 1 | 0 |  |  |
| `lens_vocab_operational_record_status_actor_content_compile_20260515` | `source_authority_pair_preservation` | `not_applicable` | 0 | 0 | 0 | 0 |
| `lens_vocab_operational_record_status_compile_20260515` | `parallel_assignment_event_preservation` | `not_applicable` | 1 | 0 |  |  |
| `lens_vocab_operational_record_status_compile_20260515` | `source_authority_pair_preservation` | `not_applicable` | 0 | 0 | 0 | 0 |
| `lens_vocab_operational_record_status_palette_compile_20260515` | `parallel_assignment_event_preservation` | `not_applicable` | 1 | 1 |  |  |
| `lens_vocab_operational_record_status_palette_compile_20260515` | `source_authority_pair_preservation` | `not_applicable` | 0 | 0 | 0 | 0 |

### Missing From `lens_vocab_operational_record_status_actor_content_compile_20260515`

- Missing union facts: `67`
- `actor_id(nora_pike).`
- `actor_id(ravi_sen).`
- `actor_role(nora_pike, archivist).`
- `actor_role(ravi_sen, conservator).`
- `asset_condition_at(m_31, brittle_hinge_strip, 2026_06_03).`
- `asset_condition_at(m_31, repaired_hinge_strip, 2026_06_04).`
- `asset_id(m_31).`
- `condition_corrected(m_31, brittle_hinge_strip, repaired_hinge_strip).`
- `current_handling_restriction(lq_31, display_approved_with_handling_restricted).`
- `entity_id(lq_31, preservation_queue).`
- `entity_id(lq_31, preservation_queue_lq_31).`
- `entity_id(m_31, map_case).`
- `entity_id(m_31, map_case_m_31).`
- `entity_id(nora_pike, archivist).`
- `entity_id(nora_pike, nora_pike).`
- `entity_id(ravi_sen, conservator).`
- `entity_id(ravi_sen, ravi_sen).`
- `entity_type(lq_31, record).`
- `entity_type(m_31, physical_object).`
- `entity_type(m_31, physicalobject).`
- `event_date(evt_20260601_receipt, 2026_06_01).`
- `event_date(evt_20260602_assign, 2026_06_02).`
- `event_date(evt_20260603_denial, 2026_06_03).`
- `event_date(evt_20260604_correction, 2026_06_04).`
- `event_date(evt_20260605_approval, 2026_06_05).`

### Missing From `lens_vocab_operational_record_status_compile_20260515`

- Missing union facts: `89`
- `assigned_role(actor_ravi_sen, condition_review, evt_assign_ravi_20260602).`
- `assigned_role(ravi_sen, condition_review, evt_002).`
- `corrected_value(evt_004, repaired_hinge_strip).`
- `corrected_value(evt_corr_20260604, repaired_hinge_strip).`
- `decision_constraint(evt_005, low_light_case).`
- `decision_constraint(evt_008, display_approved_with_handling_restricted).`
- `decision_constraint(evt_20260608_close, handling_restricted).`
- `decision_constraint(evt_20260608_close, low_light_display_only).`
- `decision_constraint(evt_disp_20260605, low_light_case).`
- `decision_made(display, approved, evt_005).`
- `decision_made(lq_31, approved, evt_20260608_close).`
- `decision_made(public_display, denied, evt_003).`
- `decision_made(request_public_display, approved, evt_disp_20260605).`
- `decision_made(request_public_display, denied, evt_denial_display_20260603).`
- `decision_reason(evt_003, hinge_strip_was_brittle).`
- `decision_reason(evt_denial_display_20260603, brittle_hinge_strip).`
- `entity_id(actor, nora_pike).`
- `entity_id(actor, ravi_sen).`
- `entity_id(case, m_31).`
- `entity_id(lq_31, preservation_queue).`
- `entity_id(lq_31, preservation_queue_lq_31).`
- `entity_id(m_31, map_case).`
- `entity_id(m_31, map_case_m_31).`
- `entity_id(nora_pike, archivist).`
- `entity_id(nora_pike, nora_pike).`

### Missing From `lens_vocab_operational_record_status_palette_compile_20260515`

- Missing union facts: `104`
- `actor_id(nora_pike).`
- `actor_id(ravi_sen).`
- `actor_role(nora_pike, archivist).`
- `actor_role(ravi_sen, conservator).`
- `asset_condition_at(m_31, brittle_hinge_strip, 2026_06_03).`
- `asset_condition_at(m_31, repaired_hinge_strip, 2026_06_04).`
- `asset_id(m_31).`
- `assigned_role(actor_ravi_sen, condition_review, evt_assign_ravi_20260602).`
- `assigned_role(ravi_sen, condition_review, evt_002).`
- `condition_corrected(m_31, brittle_hinge_strip, repaired_hinge_strip).`
- `corrected_value(evt_004, repaired_hinge_strip).`
- `corrected_value(evt_corr_20260604, repaired_hinge_strip).`
- `current_handling_restriction(lq_31, display_approved_with_handling_restricted).`
- `decision_constraint(evt_005, low_light_case).`
- `decision_constraint(evt_008, display_approved_with_handling_restricted).`
- `decision_constraint(evt_20260608_close, handling_restricted).`
- `decision_constraint(evt_20260608_close, low_light_display_only).`
- `decision_constraint(evt_disp_20260605, low_light_case).`
- `decision_made(display, approved, evt_005).`
- `decision_made(lq_31, approved, evt_20260608_close).`
- `decision_made(public_display, denied, evt_003).`
- `decision_made(request_public_display, approved, evt_disp_20260605).`
- `decision_made(request_public_display, denied, evt_denial_display_20260603).`
- `decision_reason(evt_003, hinge_strip_was_brittle).`
- `decision_reason(evt_denial_display_20260603, brittle_hinge_strip).`

## `permit_renewal_docket`

- Draws: `3`
- Stable: `False`
- Common / union direct facts: `0 / 111`
- Unstable direct facts: `111`

| Predicate | Counts | Delta |
| --- | --- | ---: |
| `action_by` | `[0, 9, 0]` | 9 |
| `action_performed` | `[12, 0, 0]` | 12 |
| `actor_id` | `[4, 0, 0]` | 4 |
| `actor_role` | `[4, 0, 0]` | 4 |
| `application_id` | `[0, 0, 1]` | 1 |
| `assigned_to` | `[0, 1, 0]` | 1 |
| `certificate_id` | `[0, 0, 1]` | 1 |
| `closed_date` | `[0, 0, 1]` | 1 |
| `condition_applied` | `[0, 0, 2]` | 2 |
| `docket_final_status` | `[1, 0, 0]` | 1 |
| `docket_has_document` | `[3, 0, 0]` | 3 |
| `docket_id` | `[1, 0, 1]` | 1 |
| `docket_status` | `[0, 2, 0]` | 2 |
| `entity_type` | `[0, 9, 0]` | 9 |
| `event_occurred` | `[0, 10, 3]` | 10 |
| `flag_status` | `[0, 4, 0]` | 4 |
| `notice_id` | `[0, 0, 1]` | 1 |
| `partial_withdrawal` | `[0, 0, 2]` | 2 |
| `payment_failure` | `[0, 0, 1]` | 1 |
| `person_id` | `[0, 0, 3]` | 3 |
| `person_role` | `[0, 3, 3]` | 3 |
| `references` | `[0, 2, 0]` | 2 |
| `request_component_active` | `[1, 0, 0]` | 1 |
| `request_component_withdrawn` | `[1, 0, 0]` | 1 |
| `scope_limitation` | `[0, 0, 1]` | 1 |
| `status_changed_at` | `[9, 0, 0]` | 9 |
| `status_superseded_by` | `[1, 0, 0]` | 1 |
| `status_transition` | `[0, 5, 7]` | 7 |
| `submitted` | `[0, 2, 0]` | 2 |
| `superseded_by` | `[0, 0, 2]` | 2 |
| `supersedes` | `[0, 2, 0]` | 2 |

| Surface | Counts | Delta |
| --- | --- | ---: |
| `assignment_binding_surface` | `[2, 5, 2]` | 3 |
| `completion_transition_surface` | `[2, 6, 8]` | 6 |
| `identity_role_surface` | `[8, 3, 6]` | 5 |
| `object_record_surface` | `[8, 5, 1]` | 7 |
| `status_phase_surface` | `[13, 12, 8]` | 5 |
| `task_scope_surface` | `[3, 5, 2]` | 3 |

| Draw | Contract | Status | Source signals | Direct surfaces | Complete | Partial |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| `lens_vocab_operational_record_status_actor_content_compile_20260515` | `parallel_assignment_event_preservation` | `not_applicable` | 1 | 0 |  |  |
| `lens_vocab_operational_record_status_actor_content_compile_20260515` | `source_authority_pair_preservation` | `not_applicable` | 0 | 0 | 0 | 0 |
| `lens_vocab_operational_record_status_compile_20260515` | `parallel_assignment_event_preservation` | `not_applicable` | 1 | 1 |  |  |
| `lens_vocab_operational_record_status_compile_20260515` | `source_authority_pair_preservation` | `not_applicable` | 0 | 0 | 0 | 0 |
| `lens_vocab_operational_record_status_palette_compile_20260515` | `parallel_assignment_event_preservation` | `not_applicable` | 1 | 0 |  |  |
| `lens_vocab_operational_record_status_palette_compile_20260515` | `source_authority_pair_preservation` | `not_applicable` | 0 | 0 | 0 | 0 |

### Missing From `lens_vocab_operational_record_status_actor_content_compile_20260515`

- Missing union facts: `74`
- `action_by(evt_approval_20260110, permit_office).`
- `action_by(evt_assignment, noor_patel).`
- `action_by(evt_assignment_20260106, noor_patel).`
- `action_by(evt_closing, vale).`
- `action_by(evt_closing_20260120, vale).`
- `action_by(evt_correction_20260109, sanitation_desk).`
- `action_by(evt_filing, erin_moss).`
- `action_by(evt_filing_20260104, erin_moss).`
- `action_by(evt_withdrawal_20260115, applicant).`
- `application_id(a_18).`
- `assigned_to(pr_18, sanitation_desk).`
- `certificate_id(c_77).`
- `closed_date(2026_01_20).`
- `condition_applied(pr_18, subject_to_payment_of_the_late_fee).`
- `condition_applied(pr_18, weekday_operation_only).`
- `docket_status(pr_18, approved_weekday_renewal).`
- `docket_status(pr_18, pending_completeness_review).`
- `entity_type(a_18, application).`
- `entity_type(a_18, artifact).`
- `entity_type(c_77, artifact).`
- `entity_type(c_77, certificate).`
- `entity_type(h_2, artifact).`
- `entity_type(h_2, hold_notice).`
- `entity_type(permit_office, department).`
- `entity_type(pr_18, docket).`

### Missing From `lens_vocab_operational_record_status_compile_20260515`

- Missing union facts: `62`
- `action_performed(applicant_pr18, applicant, submitted_certificate, 2026_01_09).`
- `action_performed(applicant_pr18, applicant, withdrew_weekend_hours, 2026_01_15).`
- `action_performed(erin_moss, clerk, received_and_filed, 2026_01_04).`
- `action_performed(erin_moss, clerk, received_application_and_filed, 2026_01_04).`
- `action_performed(noor_patel, reviewer, assigned_to_sanitation_desk, 2026_01_06).`
- `action_performed(permit_office, permit_office, approved_renewal, 2026_01_10).`
- `action_performed(permit_office, permit_office, hold_notice_issued, 2026_01_12).`
- `action_performed(permit_office, permit_office, payment_received_and_reopened, 2026_01_18).`
- `action_performed(system, system, payment_failed, 2026_01_12).`
- `action_performed(system, system, payment_received, 2026_01_18).`
- `action_performed(vale, supervisor, closed_as_approved_weekday, 2026_01_20).`
- `action_performed(vale, supervisor, closed_docket, 2026_01_20).`
- `actor_id(applicant_pr18).`
- `actor_id(erin_moss).`
- `actor_id(noor_patel).`
- `actor_id(vale).`
- `actor_role(applicant_pr18, applicant).`
- `actor_role(erin_moss, clerk).`
- `actor_role(noor_patel, reviewer).`
- `actor_role(vale, supervisor).`
- `application_id(a_18).`
- `certificate_id(c_77).`
- `closed_date(2026_01_20).`
- `condition_applied(pr_18, subject_to_payment_of_the_late_fee).`
- `condition_applied(pr_18, weekday_operation_only).`

### Missing From `lens_vocab_operational_record_status_palette_compile_20260515`

- Missing union facts: `82`
- `action_by(evt_approval_20260110, permit_office).`
- `action_by(evt_assignment, noor_patel).`
- `action_by(evt_assignment_20260106, noor_patel).`
- `action_by(evt_closing, vale).`
- `action_by(evt_closing_20260120, vale).`
- `action_by(evt_correction_20260109, sanitation_desk).`
- `action_by(evt_filing, erin_moss).`
- `action_by(evt_filing_20260104, erin_moss).`
- `action_by(evt_withdrawal_20260115, applicant).`
- `action_performed(applicant_pr18, applicant, submitted_certificate, 2026_01_09).`
- `action_performed(applicant_pr18, applicant, withdrew_weekend_hours, 2026_01_15).`
- `action_performed(erin_moss, clerk, received_and_filed, 2026_01_04).`
- `action_performed(erin_moss, clerk, received_application_and_filed, 2026_01_04).`
- `action_performed(noor_patel, reviewer, assigned_to_sanitation_desk, 2026_01_06).`
- `action_performed(permit_office, permit_office, approved_renewal, 2026_01_10).`
- `action_performed(permit_office, permit_office, hold_notice_issued, 2026_01_12).`
- `action_performed(permit_office, permit_office, payment_received_and_reopened, 2026_01_18).`
- `action_performed(system, system, payment_failed, 2026_01_12).`
- `action_performed(system, system, payment_received, 2026_01_18).`
- `action_performed(vale, supervisor, closed_as_approved_weekday, 2026_01_20).`
- `action_performed(vale, supervisor, closed_docket, 2026_01_20).`
- `actor_id(applicant_pr18).`
- `actor_id(erin_moss).`
- `actor_id(noor_patel).`
- `actor_id(vale).`

## `warehouse_repair_log`

- Draws: `3`
- Stable: `False`
- Common / union direct facts: `0 / 65`
- Unstable direct facts: `65`

| Predicate | Counts | Delta |
| --- | --- | ---: |
| `action_taken` | `[0, 0, 3]` | 3 |
| `actor_role` | `[0, 0, 4]` | 4 |
| `approval_granted` | `[0, 1, 0]` | 1 |
| `asset_status` | `[0, 1, 1]` | 1 |
| `assigned_to` | `[0, 0, 1]` | 1 |
| `component_of` | `[0, 0, 1]` | 1 |
| `diagnosed_as` | `[0, 0, 2]` | 2 |
| `diagnosis_corrected` | `[0, 1, 0]` | 1 |
| `diagnosis_corrected_by` | `[1, 0, 0]` | 1 |
| `entity_name` | `[6, 0, 0]` | 6 |
| `entity_type` | `[3, 0, 0]` | 3 |
| `equipment_current_status` | `[1, 0, 0]` | 1 |
| `person_assigned` | `[0, 1, 0]` | 1 |
| `person_role` | `[6, 3, 0]` | 6 |
| `recorded_in` | `[13, 0, 0]` | 13 |
| `request_denied_by` | `[2, 0, 0]` | 2 |
| `request_withdrawn` | `[0, 1, 1]` | 1 |
| `request_withdrawn_by` | `[1, 0, 0]` | 1 |
| `superseded_by` | `[0, 0, 1]` | 1 |
| `ticket_assigned_to` | `[1, 0, 0]` | 1 |
| `ticket_closed` | `[0, 1, 0]` | 1 |
| `ticket_closed_by` | `[2, 0, 0]` | 2 |
| `ticket_created` | `[0, 1, 0]` | 1 |
| `ticket_superseded_by` | `[1, 1, 0]` | 1 |

| Surface | Counts | Delta |
| --- | --- | ---: |
| `assignment_binding_surface` | `[3, 1, 1]` | 2 |
| `completion_transition_surface` | `[5, 1, 1]` | 4 |
| `identity_role_surface` | `[14, 4, 4]` | 10 |
| `object_record_surface` | `[23, 5, 2]` | 21 |
| `status_phase_surface` | `[10, 4, 3]` | 7 |
| `task_scope_surface` | `[2, 1, 1]` | 1 |

| Draw | Contract | Status | Source signals | Direct surfaces | Complete | Partial |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| `lens_vocab_operational_record_status_actor_content_compile_20260515` | `parallel_assignment_event_preservation` | `not_applicable` | 0 | 0 |  |  |
| `lens_vocab_operational_record_status_actor_content_compile_20260515` | `source_authority_pair_preservation` | `not_applicable` | 0 | 0 | 0 | 0 |
| `lens_vocab_operational_record_status_compile_20260515` | `parallel_assignment_event_preservation` | `not_applicable` | 0 | 0 |  |  |
| `lens_vocab_operational_record_status_compile_20260515` | `source_authority_pair_preservation` | `not_applicable` | 0 | 0 | 0 | 0 |
| `lens_vocab_operational_record_status_palette_compile_20260515` | `parallel_assignment_event_preservation` | `not_applicable` | 0 | 1 |  |  |
| `lens_vocab_operational_record_status_palette_compile_20260515` | `source_authority_pair_preservation` | `not_applicable` | 0 | 0 | 0 | 0 |

### Missing From `lens_vocab_operational_record_status_actor_content_compile_20260515`

- Missing union facts: `26`
- `action_taken(wr_62, approved_parts, parts_desk, 2026_03_05).`
- `action_taken(wr_62, corrected_diagnosis, power_test, 2026_03_04).`
- `action_taken(wr_62, denied_request, rhea_lin, 2026_03_03).`
- `actor_role(june_malik, supervisor).`
- `actor_role(parts_desk, parts_desk).`
- `actor_role(rhea_lin, technician).`
- `actor_role(tomas_iver, shift_lead).`
- `approval_granted(wr_62, parts_desk, 2026_03_05).`
- `asset_status(s_6, working).`
- `asset_status(s_6, working, 2026_03_08).`
- `assigned_to(wr_62, rhea_lin).`
- `component_of(s_6, loading_bay_scanner).`
- `diagnosed_as(s_6, cable_fault, 2026_03_04).`
- `diagnosed_as(s_6, scanner_failure, 2026_03_04).`
- `diagnosis_corrected(wr_62, scanner_failure, cable_fault).`
- `person_assigned(rhea_lin, wr_62, 2026_03_02).`
- `person_role(june_malik, supervisor, 2026_03_08).`
- `person_role(rhea_lin, technician, 2026_03_02).`
- `person_role(tomas_iver, shift_lead, 2026_03_01).`
- `request_withdrawn(wr_62, 2026_03_06).`
- `request_withdrawn(wr_62, scanner_replacement, 2026_03_06).`
- `superseded_by(wr_63, wr_62, 2026_03_07).`
- `ticket_closed(wr_62, 2026_03_08).`
- `ticket_created(wr_62, 2026_03_01).`
- `ticket_status(wr_62, denied, 2026_03_03).`

### Missing From `lens_vocab_operational_record_status_compile_20260515`

- Missing union facts: `52`
- `action_taken(wr_62, approved_parts, parts_desk, 2026_03_05).`
- `action_taken(wr_62, corrected_diagnosis, power_test, 2026_03_04).`
- `action_taken(wr_62, denied_request, rhea_lin, 2026_03_03).`
- `actor_role(june_malik, supervisor).`
- `actor_role(parts_desk, parts_desk).`
- `actor_role(rhea_lin, technician).`
- `actor_role(tomas_iver, shift_lead).`
- `asset_status(s_6, working, 2026_03_08).`
- `assigned_to(wr_62, rhea_lin).`
- `component_of(s_6, loading_bay_scanner).`
- `diagnosed_as(s_6, cable_fault, 2026_03_04).`
- `diagnosed_as(s_6, scanner_failure, 2026_03_04).`
- `diagnosis_corrected_by(wr_62, power_test, 2026_03_04).`
- `entity_name(june_malik, june_malik).`
- `entity_name(rhea_lin, rhea_lin).`
- `entity_name(s_6, s_6).`
- `entity_name(tomas_iver, tomas_iver).`
- `entity_name(wr_62, wr_62).`
- `entity_name(wr_63, wr_63).`
- `entity_type(s_6, equipment).`
- `entity_type(wr_62, ticket).`
- `entity_type(wr_63, ticket).`
- `equipment_current_status(s_6, working).`
- `person_role(june_malik, supervisor).`
- `person_role(person_june_malik, supervisor).`

### Missing From `lens_vocab_operational_record_status_palette_compile_20260515`

- Missing union facts: `49`
- `approval_granted(wr_62, parts_desk, 2026_03_05).`
- `asset_status(s_6, working).`
- `diagnosis_corrected(wr_62, scanner_failure, cable_fault).`
- `diagnosis_corrected_by(wr_62, power_test, 2026_03_04).`
- `entity_name(june_malik, june_malik).`
- `entity_name(rhea_lin, rhea_lin).`
- `entity_name(s_6, s_6).`
- `entity_name(tomas_iver, tomas_iver).`
- `entity_name(wr_62, wr_62).`
- `entity_name(wr_63, wr_63).`
- `entity_type(s_6, equipment).`
- `entity_type(wr_62, ticket).`
- `entity_type(wr_63, ticket).`
- `equipment_current_status(s_6, working).`
- `person_assigned(rhea_lin, wr_62, 2026_03_02).`
- `person_role(june_malik, supervisor).`
- `person_role(june_malik, supervisor, 2026_03_08).`
- `person_role(person_june_malik, supervisor).`
- `person_role(person_rhea_lin, technician).`
- `person_role(person_tomas_iver, shift_lead).`
- `person_role(rhea_lin, technician).`
- `person_role(rhea_lin, technician, 2026_03_02).`
- `person_role(tomas_iver, shift_lead).`
- `person_role(tomas_iver, shift_lead, 2026_03_01).`
- `recorded_in(source_md, rec_001, wr_62_logged_as_pending_inspection).`

## `water_sample_docket`

- Draws: `3`
- Stable: `False`
- Common / union direct facts: `0 / 124`
- Unstable direct facts: `124`

| Predicate | Counts | Delta |
| --- | --- | ---: |
| `acted_as` | `[0, 6, 0]` | 6 |
| `actor_id` | `[3, 0, 0]` | 3 |
| `actor_role_at` | `[4, 0, 0]` | 4 |
| `assigned_to` | `[0, 0, 2]` | 2 |
| `caused_by` | `[0, 6, 0]` | 6 |
| `closed` | `[0, 2, 0]` | 2 |
| `docket_action` | `[3, 0, 0]` | 3 |
| `docket_filed` | `[1, 0, 0]` | 1 |
| `docket_final_status` | `[1, 0, 0]` | 1 |
| `docket_id` | `[1, 1, 0]` | 1 |
| `docket_status` | `[0, 1, 3]` | 3 |
| `entry_supersedes` | `[1, 0, 0]` | 1 |
| `event_date` | `[0, 16, 0]` | 16 |
| `event_id` | `[0, 16, 0]` | 16 |
| `linked_to` | `[0, 1, 0]` | 1 |
| `person_id` | `[0, 2, 0]` | 2 |
| `person_role` | `[0, 0, 6]` | 6 |
| `record_superseded_by` | `[0, 0, 3]` | 3 |
| `recorded_event` | `[0, 0, 13]` | 13 |
| `sample_condition` | `[3, 2, 2]` | 1 |
| `sample_id` | `[2, 1, 0]` | 2 |
| `sample_received` | `[2, 0, 0]` | 2 |
| `status_at_date` | `[0, 5, 0]` | 5 |
| `superseded_by` | `[0, 1, 0]` | 1 |
| `test_approved` | `[1, 0, 0]` | 1 |
| `test_assigned` | `[2, 0, 0]` | 2 |
| `test_denied` | `[2, 0, 0]` | 2 |
| `test_result` | `[0, 4, 0]` | 4 |
| `test_result_value` | `[0, 0, 2]` | 2 |
| `test_validity` | `[0, 0, 4]` | 4 |
| `withdrew` | `[0, 2, 0]` | 2 |

| Surface | Counts | Delta |
| --- | --- | ---: |
| `assignment_binding_surface` | `[2, 0, 2]` | 2 |
| `completion_transition_surface` | `[2, 4, 5]` | 3 |
| `identity_role_surface` | `[8, 2, 10]` | 8 |
| `object_record_surface` | `[15, 5, 26]` | 21 |
| `status_phase_surface` | `[3, 9, 9]` | 6 |
| `task_scope_surface` | `[5, 0, 2]` | 5 |

| Draw | Contract | Status | Source signals | Direct surfaces | Complete | Partial |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| `lens_vocab_operational_record_status_actor_content_compile_20260515` | `parallel_assignment_event_preservation` | `not_applicable` | 1 | 0 |  |  |
| `lens_vocab_operational_record_status_actor_content_compile_20260515` | `source_authority_pair_preservation` | `not_applicable` | 0 | 0 | 0 | 0 |
| `lens_vocab_operational_record_status_compile_20260515` | `parallel_assignment_event_preservation` | `not_applicable` | 1 | 0 |  |  |
| `lens_vocab_operational_record_status_compile_20260515` | `source_authority_pair_preservation` | `not_applicable` | 0 | 0 | 0 | 0 |
| `lens_vocab_operational_record_status_palette_compile_20260515` | `parallel_assignment_event_preservation` | `not_applicable` | 1 | 2 |  |  |
| `lens_vocab_operational_record_status_palette_compile_20260515` | `source_authority_pair_preservation` | `not_applicable` | 0 | 0 | 0 | 0 |

### Missing From `lens_vocab_operational_record_status_actor_content_compile_20260515`

- Missing union facts: `98`
- `acted_as(ada_voss, analyst, ev_closure).`
- `acted_as(ada_voss, analyst, evt_ws12_closure).`
- `acted_as(ada_voss, analyst, evt_ws12_withdrawal).`
- `acted_as(ada_voss, lab_desk, ev_receipt).`
- `acted_as(niko_shah, field_collector, ev_filing).`
- `acted_as(niko_shah, field_collector, evt_ws12_filing).`
- `assigned_to(sample_b12, nitrate_testing).`
- `assigned_to(sample_b_12, nitrate_testing).`
- `caused_by(ev_denial, ev_denial).`
- `caused_by(ev_withdrawal, ev_approval).`
- `caused_by(evt_ws12_approval, evt_ws12_correction).`
- `caused_by(evt_ws12_denial, evt_ws12_correction).`
- `caused_by(evt_ws12_supersession, evt_ws12_approval).`
- `caused_by(evt_ws12_withdrawal, evt_ws12_approval).`
- `closed(ws_12, ev_closure).`
- `closed(ws_12, evt_ws12_closure).`
- `docket_status(docket_ws12, completed_below_threshold).`
- `docket_status(docket_ws_12, completed_below_threshold).`
- `docket_status(ws_12, completed_below_threshold).`
- `event_date(ev_approval, 2026_04_14).`
- `event_date(ev_closure, 2026_04_17).`
- `event_date(ev_correction, 2026_04_13).`
- `event_date(ev_denial, 2026_04_12).`
- `event_date(ev_filing, 2026_04_10).`
- `event_date(ev_receipt, 2026_04_11).`

### Missing From `lens_vocab_operational_record_status_compile_20260515`

- Missing union facts: `58`
- `actor_id(actor_ada_voss).`
- `actor_id(ada_voss).`
- `actor_id(niko_shah).`
- `actor_role_at(actor_ada_voss, lab_desk, 2026_04_11, lab_processing).`
- `actor_role_at(ada_voss, analyst, 2026_04_17, ws_12).`
- `actor_role_at(ada_voss, lab_desk, 2026_04_11, ws_12).`
- `actor_role_at(niko_shah, field_collector, 2026_04_10, ws_12).`
- `assigned_to(sample_b12, nitrate_testing).`
- `assigned_to(sample_b_12, nitrate_testing).`
- `docket_action(ws_12, closed, 2026_04_17).`
- `docket_action(ws_12, emergency_advisory_withdrawn, 2026_04_15).`
- `docket_action(ws_12, withdrawn, 2026_04_15).`
- `docket_filed(niko_shah, ws_12, b_12, 2026_04_10).`
- `docket_final_status(ws_12, completed_below_threshold).`
- `docket_status(docket_ws12, completed_below_threshold).`
- `docket_status(docket_ws_12, completed_below_threshold).`
- `entry_supersedes(approved_result_entry, pending_lab_receipt_note).`
- `person_role(ada_voss, analyst, ws_12).`
- `person_role(ada_voss, lab_desk, ws_12).`
- `person_role(niko_shah, field_collector, ws_12).`
- `person_role(person_ada_voss, analyst, docket_ws_12).`
- `person_role(person_ada_voss, lab_desk, docket_ws_12).`
- `person_role(person_niko_shah, field_collector, docket_ws_12).`
- `record_superseded_by(note_pending, entry_approved).`
- `record_superseded_by(note_pending_lab_receipt, entry_approved_result).`

### Missing From `lens_vocab_operational_record_status_palette_compile_20260515`

- Missing union facts: `89`
- `acted_as(ada_voss, analyst, ev_closure).`
- `acted_as(ada_voss, analyst, evt_ws12_closure).`
- `acted_as(ada_voss, analyst, evt_ws12_withdrawal).`
- `acted_as(ada_voss, lab_desk, ev_receipt).`
- `acted_as(niko_shah, field_collector, ev_filing).`
- `acted_as(niko_shah, field_collector, evt_ws12_filing).`
- `actor_id(actor_ada_voss).`
- `actor_id(ada_voss).`
- `actor_id(niko_shah).`
- `actor_role_at(actor_ada_voss, lab_desk, 2026_04_11, lab_processing).`
- `actor_role_at(ada_voss, analyst, 2026_04_17, ws_12).`
- `actor_role_at(ada_voss, lab_desk, 2026_04_11, ws_12).`
- `actor_role_at(niko_shah, field_collector, 2026_04_10, ws_12).`
- `caused_by(ev_denial, ev_denial).`
- `caused_by(ev_withdrawal, ev_approval).`
- `caused_by(evt_ws12_approval, evt_ws12_correction).`
- `caused_by(evt_ws12_denial, evt_ws12_correction).`
- `caused_by(evt_ws12_supersession, evt_ws12_approval).`
- `caused_by(evt_ws12_withdrawal, evt_ws12_approval).`
- `closed(ws_12, ev_closure).`
- `closed(ws_12, evt_ws12_closure).`
- `docket_action(ws_12, closed, 2026_04_17).`
- `docket_action(ws_12, emergency_advisory_withdrawn, 2026_04_15).`
- `docket_action(ws_12, withdrawn, 2026_04_15).`
- `docket_filed(niko_shah, ws_12, b_12, 2026_04_10).`
