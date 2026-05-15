# Transition/Delta Normalization Audit

- Files: `2`
- Observations: `9`
- Kind counts: `{'assignment_observation': 1, 'status_phase_observation': 3, 'supersession': 3, 'timeline_value_transition': 2}`

## `domain_bootstrap_file_20260515T174923134962Z_source_qwen-qwen3-6-35b-a3b.json`

- Observations: `6`
- Kind counts: `{'assignment_observation': 1, 'status_phase_observation': 3, 'timeline_value_transition': 2}`

- `status_phase_observation`: `subject=lq_31, status=pending_condition_review, date=2026_06_01, source_predicate=record_status_phase`
- `assignment_observation`: `subject=lq_31, assignee=ravi_sen, date=2026_06_02, source_predicate=record_assigned_to`
- `status_phase_observation`: `subject=lq_31, status=closed, date=2026_06_08, source_predicate=record_status_phase`
- `status_phase_observation`: `subject=lq_31, status=approved_for_low_light_display_only, date=2026_06_08, source_predicate=record_status_phase`
- `timeline_value_transition`: `subject=lq_31, field=record_status_phase, old_value=pending_condition_review, new_value=approved_for_low_light_display_only, old_date=2026_06_01, new_date=2026_06_08, source_predicate=record_status_phase`
- `timeline_value_transition`: `subject=lq_31, field=record_status_phase, old_value=approved_for_low_light_display_only, new_value=closed, old_date=2026_06_08, new_date=2026_06_08, source_predicate=record_status_phase`

## `domain_bootstrap_file_20260515T174942407460Z_source_qwen-qwen3-6-35b-a3b.json`

- Observations: `3`
- Kind counts: `{'supersession': 3}`

- `supersession`: `successor=entry_approved_result, predecessor=note_pending_lab_receipt, source_predicate=record_superseded_by`
- `supersession`: `successor=entry_approved, predecessor=note_pending, source_predicate=record_superseded_by`
- `supersession`: `successor=approved_result_entry, predecessor=pending_lab_receipt_note, source_predicate=record_superseded_by`
