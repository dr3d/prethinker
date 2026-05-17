# Compile Surface Invariant Audit

- Schema: `compile_surface_invariant_audit_v1`
- Compiles: `1`
- Status counts: `{'ledger_only': 1, 'partial': 8, 'pass': 3}`

## Fixture Summary

| Run | Fixture | Direct facts | Source-record facts | Pass | Partial | Candidate-only | Ledger-only | Fail | N/A |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `contract_guided_industrial_local_recompile_20260516` | `industrial_sensor_clock_correction` | 96 | 2383 | 3 | 8 | 0 | 1 | 0 | 0 |

## Missing Or Weak Families

### `contract_guided_industrial_local_recompile_20260516` / `industrial_sensor_clock_correction`

- `identity_role_surface`: `partial`; missing `['custodian_or_holder', 'registrar_or_recorder']`
- `source_addressability_surface`: `partial`; missing `['section_coordinate', 'title_or_heading']`
- `source_authority_surface`: `partial`; missing `['source_actor_or_date']`
- `participant_statement_surface`: `partial`; missing `['speech_act_or_record_type']`
- `object_device_surface`: `partial`; missing `['vendor_or_model']`
- `event_backbone_unit_surface`: `partial`; missing `['subject_or_object']`
- `measure_count_surface`: `partial`; missing `['count_or_total']`
- `financial_baseline_surface`: `partial`; missing `['resulting_value']`
- `custody_control_surface`: `ledger_only`; missing `['access_or_location', 'custody_or_possession', 'recall_or_return']`
- `participant_statement_status_contract`: `missing_structural_surface`; missing keys `[]`
