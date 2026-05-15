# Transition/Delta Normalization Audit

- Files: `3`
- Observations: `12`
- Kind counts: `{'absence_persistence': 1, 'field_added': 1, 'field_removed': 1, 'field_unchanged': 2, 'status_transition': 1, 'supersession': 2, 'value_transition': 4}`

## `domain_bootstrap_file_20260515T184701634315Z_source_qwen-qwen3-6-35b-a3b.json`

- Observations: `5`
- Kind counts: `{'absence_persistence': 1, 'field_unchanged': 2, 'supersession': 1, 'value_transition': 1}`

- `supersession`: `successor=rf_5, predecessor=of_2, source_predicate=form_replaced, source=rn_14`
- `field_unchanged`: `field=applicant_name, value=mina_rao, source=rn_14, source_predicate=field_unchanged`
- `field_unchanged`: `field=fee_amount, value=40_credits, source=rn_14, source_predicate=field_unchanged`
- `value_transition`: `field=inspection_checklist_section, old_value=section_3, new_value=section_5, predecessor=of_2, successor=rf_5, source_predicate=field_value_snapshot`
- `absence_persistence`: `field=emergency_contact, objects=['of_2', 'rf_5'], source_predicate=field_absent`

## `domain_bootstrap_file_20260515T184702809677Z_source_qwen-qwen3-6-35b-a3b.json`

- Observations: `1`
- Kind counts: `{'status_transition': 1}`

- `status_transition`: `subject=t_17, old_value=on_hold, new_value=ready_for_scheduling, event=cl_22, source_predicate=transition_occurred, timestamp=14_20, reason=address_proof_received`

## `domain_bootstrap_file_20260515T185956769930Z_source_qwen-qwen3-6-35b-a3b.json`

- Observations: `6`
- Kind counts: `{'field_added': 1, 'field_removed': 1, 'supersession': 1, 'value_transition': 3}`

- `supersession`: `successor=memo_r_19, predecessor=bulletin_c_14, source_predicate=supersedes`
- `value_transition`: `subject=memo_r_19, field=standard_parcel_weight_limit, old_value=18_kg, new_value=22_kg, source_predicate=policy_field_changed`
- `field_removed`: `field=cold_pack_supervisor_note_requirement, predecessor=bulletin_c_14, successor=memo_r_19, source_predicate=policy_field_removed`
- `field_added`: `field=oversized_label_photo_check_requirement, subject=memo_r_19, source_predicate=policy_field_added, new_value=required`
- `value_transition`: `subject=memo_r_19, field=cold_pack_supervisor_note_requirement, old_value=required, new_value=removed, source_predicate=policy_field_changed`
- `value_transition`: `subject=memo_r_19, field=oversized_label_photo_check_requirement, old_value=not_required, new_value=required, source_predicate=policy_field_changed`
