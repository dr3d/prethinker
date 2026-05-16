# Compile Surface Invariant Audit

- Schema: `compile_surface_invariant_audit_v1`
- Compiles: `8`
- Status counts: `{'candidate_only': 1, 'ledger_only': 8, 'not_applicable': 4, 'partial': 44, 'pass': 15}`

## Fixture Summary

| Run | Fixture | Direct facts | Source-record facts | Pass | Partial | Candidate-only | Ledger-only | Fail | N/A |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `compile_surface_detail_guarded_large_slice_20260516_compile` | `dulse_ledger` | 82 | 1049 | 3 | 4 | 0 | 2 | 0 | 0 |
| `compile_surface_detail_guarded_large_slice_20260516_compile` | `industrial_sensor_clock_correction` | 60 | 2394 | 2 | 7 | 0 | 0 | 0 | 0 |
| `compile_surface_detail_guarded_large_slice_20260516_compile` | `larkspur_clockwork_fair` | 106 | 334 | 2 | 5 | 1 | 0 | 0 | 1 |
| `compile_surface_detail_guarded_large_slice_20260516_compile` | `ridgeline_fire` | 228 | 1605 | 2 | 5 | 0 | 0 | 0 | 2 |
| `compile_surface_detail_guarded_large_slice_20260516_compile` | `sable_creek_budget` | 80 | 1542 | 2 | 6 | 0 | 1 | 0 | 0 |
| `compile_surface_detail_guarded_large_slice_20260516_compile` | `school_activity_roster_reconciliation` | 98 | 2217 | 0 | 7 | 0 | 2 | 0 | 0 |
| `compile_surface_detail_guarded_large_slice_20260516_compile` | `thornfield_variance` | 126 | 1704 | 2 | 6 | 0 | 1 | 0 | 0 |
| `compile_surface_detail_guarded_large_slice_20260516_compile` | `tournament_borrowed_names` | 87 | 1087 | 2 | 4 | 0 | 2 | 0 | 1 |

## Missing Or Weak Families

### `compile_surface_detail_guarded_large_slice_20260516_compile` / `dulse_ledger`

- `source_addressability_surface`: `partial`; missing `['basis_coordinate', 'section_coordinate', 'title_or_heading']`
- `source_authority_surface`: `ledger_only`; missing `['source_actor_or_date', 'source_document_or_correspondence']`
- `object_device_surface`: `ledger_only`; missing `['vendor_or_model']`
- `temporal_event_surface`: `partial`; missing `['timestamp_or_date']`
- `measure_count_surface`: `partial`; missing `['measurement_value']`
- `custody_control_surface`: `partial`; missing `['ownership_or_title']`

### `compile_surface_detail_guarded_large_slice_20260516_compile` / `industrial_sensor_clock_correction`

- `identity_role_surface`: `partial`; missing `['registrar_or_recorder']`
- `source_addressability_surface`: `partial`; missing `['chronology_coordinate', 'section_coordinate', 'title_or_heading']`
- `source_authority_surface`: `partial`; missing `['governed_subject_or_item']`
- `answer_detail_surface`: `partial`; missing `['availability_or_scope', 'commitment_or_future_action']`
- `object_device_surface`: `partial`; missing `['vendor_or_model']`
- `measure_count_surface`: `partial`; missing `['count_or_total', 'ratio_or_formula']`
- `custody_control_surface`: `partial`; missing `['access_or_location', 'recall_or_return']`

### `compile_surface_detail_guarded_large_slice_20260516_compile` / `larkspur_clockwork_fair`

- `identity_role_surface`: `partial`; missing `['registrar_or_recorder']`
- `source_addressability_surface`: `partial`; missing `['section_coordinate', 'title_or_heading']`
- `source_authority_surface`: `candidate_only`; missing `['source_document_or_correspondence']`
- `answer_detail_surface`: `partial`; missing `['detail_or_explanation']`
- `rule_policy_surface`: `partial`; missing `['policy_or_rule_id']`
- `measure_count_surface`: `partial`; missing `['duration_or_hours']`

### `compile_surface_detail_guarded_large_slice_20260516_compile` / `ridgeline_fire`

- `identity_role_surface`: `partial`; missing `['registrar_or_recorder']`
- `source_addressability_surface`: `partial`; missing `['chronology_coordinate', 'title_or_heading']`
- `answer_detail_surface`: `partial`; missing `['availability_or_scope']`
- `temporal_event_surface`: `partial`; missing `['correction_or_supersession', 'timestamp_or_date']`
- `measure_count_surface`: `partial`; missing `['count_or_total']`

### `compile_surface_detail_guarded_large_slice_20260516_compile` / `sable_creek_budget`

- `identity_role_surface`: `partial`; missing `['clinical_or_safety_role', 'custodian_or_holder', 'registrar_or_recorder']`
- `source_addressability_surface`: `partial`; missing `['title_or_heading']`
- `answer_detail_surface`: `partial`; missing `['commitment_or_future_action', 'detail_or_explanation']`
- `object_device_surface`: `ledger_only`; missing `['object_or_item_id']`
- `temporal_event_surface`: `partial`; missing `['timestamp_or_date']`
- `measure_count_surface`: `partial`; missing `['count_or_total', 'ratio_or_formula']`
- `custody_control_surface`: `partial`; missing `['custody_or_possession', 'ownership_or_title']`

### `compile_surface_detail_guarded_large_slice_20260516_compile` / `school_activity_roster_reconciliation`

- `identity_role_surface`: `partial`; missing `['supervisor_or_authority']`
- `source_addressability_surface`: `ledger_only`; missing `['negative_inference_coordinate', 'section_coordinate', 'title_or_heading']`
- `source_authority_surface`: `partial`; missing `['authority_or_evidence_role', 'source_actor_or_date']`
- `answer_detail_surface`: `ledger_only`; missing `['availability_or_scope', 'commitment_or_future_action', 'detail_or_explanation', 'negative_or_exclusion_detail']`
- `rule_policy_surface`: `partial`; missing `['exception_or_exclusion']`
- `object_device_surface`: `partial`; missing `['device_or_system']`
- `temporal_event_surface`: `partial`; missing `['event_or_action', 'interval_or_window', 'timestamp_or_date']`
- `measure_count_surface`: `partial`; missing `['count_or_total', 'duration_or_hours', 'threshold_or_limit']`
- `custody_control_surface`: `partial`; missing `['access_or_location']`

### `compile_surface_detail_guarded_large_slice_20260516_compile` / `thornfield_variance`

- `source_addressability_surface`: `partial`; missing `['title_or_heading']`
- `source_authority_surface`: `partial`; missing `['source_document_or_correspondence']`
- `answer_detail_surface`: `partial`; missing `['availability_or_scope']`
- `rule_policy_surface`: `partial`; missing `['policy_or_rule_id']`
- `temporal_event_surface`: `ledger_only`; missing `['timestamp_or_date']`
- `measure_count_surface`: `partial`; missing `['duration_or_hours', 'measurement_value']`
- `custody_control_surface`: `partial`; missing `['access_or_location']`

### `compile_surface_detail_guarded_large_slice_20260516_compile` / `tournament_borrowed_names`

- `identity_role_surface`: `partial`; missing `['clinical_or_safety_role', 'custodian_or_holder']`
- `source_addressability_surface`: `partial`; missing `['section_coordinate', 'title_or_heading']`
- `source_authority_surface`: `ledger_only`; missing `['source_document_or_correspondence']`
- `temporal_event_surface`: `partial`; missing `['interval_or_window']`
- `measure_count_surface`: `partial`; missing `['count_or_total', 'threshold_or_limit']`
- `custody_control_surface`: `ledger_only`; missing `['custody_or_possession']`
