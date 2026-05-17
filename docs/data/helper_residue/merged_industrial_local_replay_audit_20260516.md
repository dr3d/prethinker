# Compile Surface Invariant Audit

- Schema: `compile_surface_invariant_audit_v1`
- Compiles: `1`
- Status counts: `{'partial': 8, 'pass': 4}`

## Fixture Summary

| Run | Fixture | Direct facts | Source-record facts | Pass | Partial | Candidate-only | Ledger-only | Fail | N/A |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `merged_industrial_local_replay_20260516` | `industrial_sensor_clock_correction` | 205 | 2383 | 4 | 8 | 0 | 0 | 0 | 0 |

## Missing Or Weak Families

### `merged_industrial_local_replay_20260516` / `industrial_sensor_clock_correction`

- `identity_role_surface`: `partial`; missing `['registrar_or_recorder']`
- `source_addressability_surface`: `partial`; missing `['section_coordinate', 'title_or_heading']`
- `participant_statement_surface`: `partial`; missing `['speech_act_or_record_type']`
- `object_device_surface`: `partial`; missing `['vendor_or_model']`
- `event_backbone_unit_surface`: `partial`; missing `['subject_or_object']`
- `measure_count_surface`: `partial`; missing `['count_or_total']`
- `financial_baseline_surface`: `partial`; missing `['resulting_value']`
- `custody_control_surface`: `partial`; missing `['access_or_location', 'recall_or_return']`
- `participant_statement_status_contract`: `missing_structural_surface`; missing keys `[]`
