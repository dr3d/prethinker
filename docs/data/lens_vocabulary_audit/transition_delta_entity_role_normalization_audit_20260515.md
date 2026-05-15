# Transition/Delta Normalization Audit

- Files: `3`
- Observations: `6`
- Kind counts: `{'role_holder_transition': 1, 'role_lifecycle_state': 5}`

## `domain_bootstrap_file_20260515T183223581741Z_source_qwen-qwen3-6-35b-a3b.json`

- Observations: `0`
- Kind counts: `{}`


## `domain_bootstrap_file_20260515T183207348135Z_source_qwen-qwen3-6-35b-a3b.json`

- Observations: `1`
- Kind counts: `{'role_lifecycle_state': 1}`

- `role_lifecycle_state`: `subject=dima_kaur, role=temporary_workshop_guardian, scope=saturday_workshop, state=current, source_predicate=holds_role`

## `domain_bootstrap_file_20260515T183234091558Z_source_qwen-qwen3-6-35b-a3b.json`

- Observations: `5`
- Kind counts: `{'role_holder_transition': 1, 'role_lifecycle_state': 4}`

- `role_lifecycle_state`: `subject=lio_vale, role=rotation_steward, scope=repair_circle, state=current, source_predicate=holds_role`
- `role_lifecycle_state`: `subject=nessa_cho, role=rotation_steward, scope=repair_circle, state=ended, source_predicate=held_role|role_cessation`
- `role_holder_transition`: `predecessor=nessa_cho, successor=lio_vale, role=rotation_steward, scope=repair_circle, source_predicate=holds_role|held_role|role_cessation`
- `role_lifecycle_state`: `subject=nessa_cho, role=volunteer, scope=clinic, state=current, source_predicate=holds_role`
- `role_lifecycle_state`: `subject=nessa_cho, role=volunteer, scope=saturday_clinics, state=current, source_predicate=holds_role`
