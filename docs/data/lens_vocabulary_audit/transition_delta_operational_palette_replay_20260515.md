# Transition/Delta Normalization Audit

- Files: `6`
- Observations: `36`
- Kind counts: `{'assignment_observation': 1, 'related_document_value_unchanged': 1, 'status_phase_observation': 15, 'supersession': 8, 'timeline_value_transition': 11}`

## `domain_bootstrap_file_20260515T175020840734Z_source_qwen-qwen3-6-35b-a3b.json`

- Observations: `17`
- Kind counts: `{'status_phase_observation': 8, 'supersession': 2, 'timeline_value_transition': 7}`

- `status_phase_observation`: `subject=ci_44, status=pending_triage, date=2026_02_02, source_predicate=record_status_phase`
- `status_phase_observation`: `subject=ci_44, status=denied, date=2026_02_04, source_predicate=record_status_phase`
- `supersession`: `successor=pending_nurse_review, predecessor=denied, source_predicate=record_superseded_by`
- `status_phase_observation`: `subject=ci_44, status=pending_nurse_review, date=2026_02_05, source_predicate=record_status_phase`
- `status_phase_observation`: `subject=ci_44, status=scheduled, date=2026_02_09, source_predicate=record_status_phase`
- `status_phase_observation`: `subject=ci_44, status=orthopedic_review, date=2026_02_03, source_predicate=record_status_phase`
- `status_phase_observation`: `subject=ci_44, status=approved, date=2026_02_06, source_predicate=record_status_phase`
- `status_phase_observation`: `subject=ci_44, status=reopened, date=2026_02_08, source_predicate=record_status_phase`
- `status_phase_observation`: `subject=ci_44, status=closed, date=2026_02_09, source_predicate=record_status_phase`
- `supersession`: `successor=pending_nurse_review, predecessor=denied_scheduling, source_predicate=record_superseded_by`
- `timeline_value_transition`: `subject=ci_44, field=record_status_phase, old_value=pending_triage, new_value=orthopedic_review, old_date=2026_02_02, new_date=2026_02_03, source_predicate=record_status_phase`
- `timeline_value_transition`: `subject=ci_44, field=record_status_phase, old_value=orthopedic_review, new_value=denied, old_date=2026_02_03, new_date=2026_02_04, source_predicate=record_status_phase`
- `timeline_value_transition`: `subject=ci_44, field=record_status_phase, old_value=denied, new_value=pending_nurse_review, old_date=2026_02_04, new_date=2026_02_05, source_predicate=record_status_phase`
- `timeline_value_transition`: `subject=ci_44, field=record_status_phase, old_value=pending_nurse_review, new_value=approved, old_date=2026_02_05, new_date=2026_02_06, source_predicate=record_status_phase`
- `timeline_value_transition`: `subject=ci_44, field=record_status_phase, old_value=approved, new_value=reopened, old_date=2026_02_06, new_date=2026_02_08, source_predicate=record_status_phase`
- `timeline_value_transition`: `subject=ci_44, field=record_status_phase, old_value=reopened, new_value=closed, old_date=2026_02_08, new_date=2026_02_09, source_predicate=record_status_phase`
- `timeline_value_transition`: `subject=ci_44, field=record_status_phase, old_value=closed, new_value=scheduled, old_date=2026_02_09, new_date=2026_02_09, source_predicate=record_status_phase`

## `domain_bootstrap_file_20260515T174828801002Z_source_qwen-qwen3-6-35b-a3b.json`

- Observations: `7`
- Kind counts: `{'related_document_value_unchanged': 1, 'status_phase_observation': 4, 'supersession': 1, 'timeline_value_transition': 1}`

- `status_phase_observation`: `subject=record_gq5, status=pending_eligibility_check, date=2026_05_02, source_predicate=record_status_phase`
- `supersession`: `successor=evt_20260507_01, predecessor=evt_20260505_01, source_predicate=record_superseded_by`
- `status_phase_observation`: `subject=record_gq5, status=approved_with_revised_budget, date=2026_05_10, source_predicate=record_status_phase`
- `status_phase_observation`: `subject=record_p5, status=pending_eligibility_check, date=2026_05_02, source_predicate=record_status_phase`
- `status_phase_observation`: `subject=queue_gq5, status=approved_with_revised_budget, date=2026_05_10, source_predicate=record_status_phase`
- `timeline_value_transition`: `subject=record_gq5, field=record_status_phase, old_value=pending_eligibility_check, new_value=approved_with_revised_budget, old_date=2026_05_02, new_date=2026_05_10, source_predicate=record_status_phase`
- `related_document_value_unchanged`: `relation=record_superseded_by, predecessor=evt_20260505_01, successor=evt_20260507_01, field=record_p5, old_value=role_eligibility_staff, new_value=role_eligibility_staff, source_predicate=record_lifecycle_event`

## `domain_bootstrap_file_20260515T174923134962Z_source_qwen-qwen3-6-35b-a3b.json`

- Observations: `6`
- Kind counts: `{'assignment_observation': 1, 'status_phase_observation': 3, 'timeline_value_transition': 2}`

- `status_phase_observation`: `subject=lq_31, status=pending_condition_review, date=2026_06_01, source_predicate=record_status_phase`
- `assignment_observation`: `subject=lq_31, assignee=ravi_sen, date=2026_06_02, source_predicate=record_assigned_to`
- `status_phase_observation`: `subject=lq_31, status=closed, date=2026_06_08, source_predicate=record_status_phase`
- `status_phase_observation`: `subject=lq_31, status=approved_for_low_light_display_only, date=2026_06_08, source_predicate=record_status_phase`
- `timeline_value_transition`: `subject=lq_31, field=record_status_phase, old_value=pending_condition_review, new_value=approved_for_low_light_display_only, old_date=2026_06_01, new_date=2026_06_08, source_predicate=record_status_phase`
- `timeline_value_transition`: `subject=lq_31, field=record_status_phase, old_value=approved_for_low_light_display_only, new_value=closed, old_date=2026_06_08, new_date=2026_06_08, source_predicate=record_status_phase`

## `domain_bootstrap_file_20260515T174922376403Z_source_qwen-qwen3-6-35b-a3b.json`

- Observations: `2`
- Kind counts: `{'supersession': 2}`

- `supersession`: `successor=h_2, predecessor=2026_01_10_approval, source_predicate=superseded_by`
- `supersession`: `successor=hold_notice_h_2, predecessor=approved, source_predicate=superseded_by`

## `domain_bootstrap_file_20260515T174839078801Z_source_qwen-qwen3-6-35b-a3b.json`

- Observations: `1`
- Kind counts: `{'timeline_value_transition': 1}`

- `timeline_value_transition`: `subject=wr_62, field=ticket_status, old_value=pending_inspection, new_value=closed, old_date=2026_03_01, new_date=2026_03_08, source_predicate=ticket_status`

## `domain_bootstrap_file_20260515T174942407460Z_source_qwen-qwen3-6-35b-a3b.json`

- Observations: `3`
- Kind counts: `{'supersession': 3}`

- `supersession`: `successor=entry_approved_result, predecessor=note_pending_lab_receipt, source_predicate=record_superseded_by`
- `supersession`: `successor=entry_approved, predecessor=note_pending, source_predicate=record_superseded_by`
- `supersession`: `successor=approved_result_entry, predecessor=pending_lab_receipt_note, source_predicate=record_superseded_by`
