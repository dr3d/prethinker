# Compile Surface Invariant Audit

- Schema: `compile_surface_invariant_audit_v1`
- Compiles: `9`
- Status counts: `{'candidate_only': 12, 'ledger_only': 7, 'not_applicable': 3, 'partial': 27, 'pass': 14}`

## Fixture Summary

| Run | Fixture | Direct facts | Source-record facts | Pass | Partial | Candidate-only | Ledger-only | Fail | N/A |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `helper_direct_surface_recompile_20260514` | `count_composition_roster` | 258 | 1498 | 2 | 4 | 0 | 0 | 0 | 1 |
| `helper_direct_surface_recompile_20260514` | `industrial_sensor_clock_correction` | 0 | 2383 | 0 | 0 | 6 | 1 | 0 | 0 |
| `helper_direct_surface_recompile_20260514` | `probate_storage_access_register` | 16 | 2380 | 0 | 3 | 1 | 3 | 0 | 0 |
| `helper_source_fidelity_recompile_20260514` | `count_composition_roster` | 272 | 1498 | 2 | 4 | 0 | 0 | 0 | 1 |
| `helper_source_fidelity_recompile_20260514` | `industrial_sensor_clock_correction` | 52 | 2383 | 2 | 5 | 0 | 0 | 0 | 0 |
| `helper_source_fidelity_recompile_20260514` | `probate_storage_access_register` | 0 | 2380 | 0 | 0 | 5 | 2 | 0 | 0 |
| `instrument_stamp_20260514_story_worlds_draw1_compile` | `count_composition_roster` | 302 | 1498 | 2 | 4 | 0 | 0 | 0 | 1 |
| `instrument_stamp_20260514_story_worlds_draw1_compile` | `industrial_sensor_clock_correction` | 146 | 2383 | 2 | 4 | 0 | 1 | 0 | 0 |
| `instrument_stamp_20260514_story_worlds_draw1_compile` | `probate_storage_access_register` | 114 | 2380 | 4 | 3 | 0 | 0 | 0 | 0 |

## Missing Or Weak Families

### `helper_direct_surface_recompile_20260514` / `count_composition_roster`

- `identity_role_surface`: `partial`; missing `['registrar_or_recorder']`
- `source_addressability_surface`: `partial`; missing `['section_coordinate', 'title_or_heading']`
- `temporal_event_surface`: `partial`; missing `['event_or_action']`
- `measure_count_surface`: `partial`; missing `['measurement_value']`

### `helper_direct_surface_recompile_20260514` / `industrial_sensor_clock_correction`

- `identity_role_surface`: `candidate_only`; missing `['custodian_or_holder', 'operator_or_attendant', 'registrar_or_recorder', 'supervisor_or_authority']`
- `source_addressability_surface`: `candidate_only`; missing `['chronology_coordinate', 'negative_inference_coordinate', 'section_coordinate', 'title_or_heading']`
- `rule_policy_surface`: `candidate_only`; missing `['exception_or_exclusion', 'policy_or_rule_id']`
- `object_device_surface`: `candidate_only`; missing `['device_or_system', 'object_or_item_id', 'vendor_or_model']`
- `temporal_event_surface`: `candidate_only`; missing `['correction_or_supersession', 'event_or_action', 'interval_or_window', 'timestamp_or_date']`
- `measure_count_surface`: `candidate_only`; missing `['count_or_total', 'duration_or_hours', 'measurement_value', 'ratio_or_formula']`
- `custody_control_surface`: `ledger_only`; missing `['access_or_location', 'custody_or_possession', 'recall_or_return']`

### `helper_direct_surface_recompile_20260514` / `probate_storage_access_register`

- `identity_role_surface`: `partial`; missing `['supervisor_or_authority']`
- `source_addressability_surface`: `partial`; missing `['basis_coordinate', 'chronology_coordinate', 'negative_inference_coordinate', 'title_or_heading']`
- `rule_policy_surface`: `ledger_only`; missing `['exception_or_exclusion', 'policy_or_rule_id']`
- `object_device_surface`: `candidate_only`; missing `['object_or_item_id']`
- `temporal_event_surface`: `ledger_only`; missing `['event_or_action', 'interval_or_window', 'timestamp_or_date']`
- `measure_count_surface`: `ledger_only`; missing `['measurement_value', 'ratio_or_formula']`
- `custody_control_surface`: `partial`; missing `['access_or_location', 'ownership_or_title', 'recall_or_return']`

### `helper_source_fidelity_recompile_20260514` / `count_composition_roster`

- `identity_role_surface`: `partial`; missing `['registrar_or_recorder']`
- `source_addressability_surface`: `partial`; missing `['section_coordinate', 'title_or_heading']`
- `temporal_event_surface`: `partial`; missing `['interval_or_window', 'timestamp_or_date']`
- `measure_count_surface`: `partial`; missing `['duration_or_hours', 'measurement_value', 'threshold_or_limit']`

### `helper_source_fidelity_recompile_20260514` / `industrial_sensor_clock_correction`

- `identity_role_surface`: `partial`; missing `['registrar_or_recorder']`
- `source_addressability_surface`: `partial`; missing `['chronology_coordinate', 'section_coordinate', 'title_or_heading']`
- `temporal_event_surface`: `partial`; missing `['correction_or_supersession']`
- `measure_count_surface`: `partial`; missing `['count_or_total']`
- `custody_control_surface`: `partial`; missing `['access_or_location', 'recall_or_return']`

### `helper_source_fidelity_recompile_20260514` / `probate_storage_access_register`

- `identity_role_surface`: `candidate_only`; missing `['custodian_or_holder', 'legal_or_claim_role', 'registrar_or_recorder', 'supervisor_or_authority']`
- `source_addressability_surface`: `candidate_only`; missing `['basis_coordinate', 'chronology_coordinate', 'negative_inference_coordinate', 'section_coordinate', 'title_or_heading']`
- `rule_policy_surface`: `ledger_only`; missing `['exception_or_exclusion', 'policy_or_rule_id']`
- `object_device_surface`: `candidate_only`; missing `['object_or_item_id']`
- `temporal_event_surface`: `candidate_only`; missing `['event_or_action', 'interval_or_window', 'timestamp_or_date']`
- `measure_count_surface`: `ledger_only`; missing `['measurement_value', 'ratio_or_formula']`
- `custody_control_surface`: `candidate_only`; missing `['access_or_location', 'custody_or_possession', 'ownership_or_title', 'recall_or_return']`

### `instrument_stamp_20260514_story_worlds_draw1_compile` / `count_composition_roster`

- `identity_role_surface`: `partial`; missing `['registrar_or_recorder']`
- `source_addressability_surface`: `partial`; missing `['title_or_heading']`
- `temporal_event_surface`: `partial`; missing `['event_or_action']`
- `measure_count_surface`: `partial`; missing `['measurement_value']`

### `instrument_stamp_20260514_story_worlds_draw1_compile` / `industrial_sensor_clock_correction`

- `identity_role_surface`: `partial`; missing `['custodian_or_holder', 'registrar_or_recorder']`
- `source_addressability_surface`: `partial`; missing `['chronology_coordinate', 'section_coordinate', 'title_or_heading']`
- `object_device_surface`: `partial`; missing `['vendor_or_model']`
- `measure_count_surface`: `partial`; missing `['count_or_total']`
- `custody_control_surface`: `ledger_only`; missing `['access_or_location', 'custody_or_possession', 'recall_or_return']`

### `instrument_stamp_20260514_story_worlds_draw1_compile` / `probate_storage_access_register`

- `identity_role_surface`: `partial`; missing `['legal_or_claim_role']`
- `source_addressability_surface`: `partial`; missing `['basis_coordinate', 'chronology_coordinate']`
- `measure_count_surface`: `partial`; missing `['measurement_value']`
