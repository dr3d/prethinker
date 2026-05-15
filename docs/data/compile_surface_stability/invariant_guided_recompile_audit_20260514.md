# Compile Surface Invariant Audit

- Schema: `compile_surface_invariant_audit_v1`
- Compiles: `3`
- Status counts: `{'candidate_only': 2, 'ledger_only': 2, 'not_applicable': 1, 'partial': 13, 'pass': 3}`

## Fixture Summary

| Run | Fixture | Direct facts | Source-record facts | Pass | Partial | Candidate-only | Ledger-only | Fail | N/A |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `compile_surface_invariant_recompile_20260514` | `count_composition_roster` | 297 | 1499 | 2 | 4 | 0 | 0 | 0 | 1 |
| `compile_surface_invariant_recompile_20260514` | `industrial_sensor_clock_correction` | 38 | 2383 | 1 | 5 | 0 | 1 | 0 | 0 |
| `compile_surface_invariant_recompile_20260514` | `probate_storage_access_register` | 12 | 2380 | 0 | 4 | 2 | 1 | 0 | 0 |

## Missing Or Weak Families

### `compile_surface_invariant_recompile_20260514` / `count_composition_roster`

- `identity_role_surface`: `partial`; missing `['registrar_or_recorder']`
- `source_addressability_surface`: `partial`; missing `['section_coordinate', 'title_or_heading']`
- `temporal_event_surface`: `partial`; missing `['timestamp_or_date']`
- `measure_count_surface`: `partial`; missing `['measurement_value']`

### `compile_surface_invariant_recompile_20260514` / `industrial_sensor_clock_correction`

- `identity_role_surface`: `partial`; missing `['custodian_or_holder', 'registrar_or_recorder', 'supervisor_or_authority']`
- `source_addressability_surface`: `partial`; missing `['chronology_coordinate', 'section_coordinate', 'title_or_heading']`
- `object_device_surface`: `partial`; missing `['vendor_or_model']`
- `temporal_event_surface`: `partial`; missing `['interval_or_window']`
- `measure_count_surface`: `partial`; missing `['count_or_total', 'duration_or_hours']`
- `custody_control_surface`: `ledger_only`; missing `['access_or_location', 'custody_or_possession', 'recall_or_return']`

### `compile_surface_invariant_recompile_20260514` / `probate_storage_access_register`

- `identity_role_surface`: `partial`; missing `['legal_or_claim_role', 'supervisor_or_authority']`
- `source_addressability_surface`: `partial`; missing `['basis_coordinate', 'chronology_coordinate', 'negative_inference_coordinate', 'section_coordinate']`
- `rule_policy_surface`: `ledger_only`; missing `['exception_or_exclusion', 'policy_or_rule_id']`
- `object_device_surface`: `candidate_only`; missing `['object_or_item_id']`
- `temporal_event_surface`: `candidate_only`; missing `['event_or_action', 'interval_or_window', 'timestamp_or_date']`
- `measure_count_surface`: `partial`; missing `['measurement_value']`
- `custody_control_surface`: `partial`; missing `['custody_or_possession', 'recall_or_return']`
