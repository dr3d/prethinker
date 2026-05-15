# Compile Surface Stability Audit

- Compiles: `2`
- Fixtures: `1`
- Stable fixtures: `0`
- Unstable fixtures: `1`
- Unstable direct facts: `41`
- Predicate drift rows: `17`
- Surface drift rows: `6`

## `equipment_service_queue`

- Draws: `2`
- Stable: `False`
- Common / union direct facts: `0 / 41`
- Unstable direct facts: `41`

| Predicate | Counts | Delta |
| --- | --- | ---: |
| `assigned_role` | `[0, 3]` | 3 |
| `equipment_assigned_to_record` | `[0, 1]` | 1 |
| `equipment_id` | `[1, 2]` | 1 |
| `equipment_service_record` | `[1, 0]` | 1 |
| `equipment_type` | `[0, 2]` | 2 |
| `person_name` | `[3, 6]` | 3 |
| `person_role` | `[3, 0]` | 3 |
| `record_created_by` | `[0, 1]` | 1 |
| `record_status` | `[0, 1]` | 1 |
| `service_record_status` | `[1, 0]` | 1 |
| `signoff_condition` | `[0, 1]` | 1 |
| `task_assigned` | `[1, 0]` | 1 |
| `task_assigned_to` | `[0, 2]` | 2 |
| `task_completed_by` | `[0, 2]` | 2 |
| `task_dependency` | `[2, 0]` | 2 |
| `task_description` | `[0, 4]` | 4 |
| `task_type` | `[2, 0]` | 2 |

| Surface | Counts | Delta |
| --- | --- | ---: |
| `assignment_binding_surface` | `[3, 7]` | 4 |
| `completion_transition_surface` | `[0, 2]` | 2 |
| `identity_role_surface` | `[6, 9]` | 3 |
| `object_record_surface` | `[4, 8]` | 4 |
| `status_phase_surface` | `[3, 4]` | 1 |
| `task_scope_surface` | `[5, 8]` | 3 |

| Draw | Contract | Status | Source signals | Direct surfaces |
| --- | --- | --- | ---: | ---: |
| `assignment_scope_v1_compile_20260515` | `parallel_assignment_event_preservation` | `partial` | 2 | 1 |
| `assignment_scope_v1_compile_20260515` | `source_authority_pair_preservation` | `not_applicable` | 0 | 0 |
| `assignment_scope_v1_equipment_redraw_compile_20260515` | `parallel_assignment_event_preservation` | `pass` | 2 | 2 |
| `assignment_scope_v1_equipment_redraw_compile_20260515` | `source_authority_pair_preservation` | `not_applicable` | 0 | 0 |

### Missing From `assignment_scope_v1_compile_20260515`

- Missing union facts: `26`
- `assigned_role(mara_lin, coordinator).`
- `assigned_role(priya_noor, electrician).`
- `assigned_role(theo_aran, mechanic).`
- `equipment_assigned_to_record(sr_44, g_44).`
- `equipment_id(equip_g44, g_44).`
- `equipment_id(g_44, g_44).`
- `equipment_type(equip_g44, portable_generator).`
- `equipment_type(g_44, portable_generator).`
- `person_name(mara_lin, mara_lin).`
- `person_name(person_mara_lin, mara_lin).`
- `person_name(person_priya_noor, priya_noor).`
- `person_name(person_theo_aran, theo_aran).`
- `person_name(priya_noor, priya_noor).`
- `person_name(theo_aran, theo_aran).`
- `record_created_by(sr_44, mara_lin, 2026_12_11t08_15).`
- `record_status(sr_44, pending_signoff).`
- `service_record_id(sr_44, sr_44).`
- `signoff_condition(sr_44, both_assignments_were_marked_complete).`
- `task_assigned_to(task_fuel, theo_aran, 2026_12_11t09_00).`
- `task_assigned_to(task_voltage, priya_noor, 2026_12_12).`
- `task_completed_by(task_fuel, theo_aran, 2026_12_13).`
- `task_completed_by(task_voltage, priya_noor, 2026_12_14).`
- `task_description(task_fuel, fuel_line_inspection).`
- `task_description(task_fuel_line_001, fuel_line_inspection).`
- `task_description(task_voltage, voltage_output_testing).`

### Missing From `assignment_scope_v1_equipment_redraw_compile_20260515`

- Missing union facts: `15`
- `equipment_id(g_44).`
- `equipment_service_record(g_44, sr_44).`
- `person_name(mara_lin).`
- `person_name(priya_noor).`
- `person_name(theo_aran).`
- `person_role(mara_lin, coordinator).`
- `person_role(priya_noor, electrician).`
- `person_role(theo_aran, mechanic).`
- `service_record_id(sr_44).`
- `service_record_status(sr_44, pending).`
- `task_assigned(theo_aran, fuel_line_inspection, 2026_12_11, 09_00).`
- `task_dependency(sr_44, both_assignments_complete).`
- `task_dependency(sr_44, pending_signoff_until_both_assignments_were_marked_complete).`
- `task_type(fuel_line_inspection, fuel_line_inspection).`
- `task_type(voltage_output_testing, voltage_output_testing).`
