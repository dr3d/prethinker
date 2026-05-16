# Compile Surface Invariant Audit

- Schema: `compile_surface_invariant_audit_v1`
- Compiles: `3`
- Status counts: `{'ledger_only': 4, 'not_applicable': 2, 'partial': 14, 'pass': 7}`

## Fixture Summary

| Run | Fixture | Direct facts | Source-record facts | Pass | Partial | Candidate-only | Ledger-only | Fail | N/A |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `compile_surface_detail_guarded_arts_20260516_compile` | `arts_grant_panel_reconsideration` | 48 | 1180 | 1 | 6 | 0 | 2 | 0 | 0 |
| `compile_surface_detail_guarded_slice_20260516_compile` | `amended_lease_register` | 111 | 333 | 5 | 2 | 0 | 0 | 0 | 2 |
| `compile_surface_detail_guarded_slice_20260516_compile` | `school_activity_roster_reconciliation` | 166 | 2217 | 1 | 6 | 0 | 2 | 0 | 0 |

## Missing Or Weak Families

### `compile_surface_detail_guarded_arts_20260516_compile` / `arts_grant_panel_reconsideration`

- `identity_role_surface`: `partial`; missing `['custodian_or_holder', 'registrar_or_recorder', 'supervisor_or_authority']`
- `source_addressability_surface`: `partial`; missing `['section_coordinate', 'title_or_heading']`
- `source_authority_surface`: `partial`; missing `['authority_or_evidence_role']`
- `answer_detail_surface`: `partial`; missing `['availability_or_scope']`
- `object_device_surface`: `ledger_only`; missing `['device_or_system']`
- `temporal_event_surface`: `partial`; missing `['interval_or_window']`
- `measure_count_surface`: `partial`; missing `['count_or_total', 'measurement_value', 'ratio_or_formula']`
- `custody_control_surface`: `ledger_only`; missing `['custody_or_possession']`

### `compile_surface_detail_guarded_slice_20260516_compile` / `amended_lease_register`

- `source_addressability_surface`: `partial`; missing `['section_coordinate', 'title_or_heading']`
- `temporal_event_surface`: `partial`; missing `['event_or_action']`

### `compile_surface_detail_guarded_slice_20260516_compile` / `school_activity_roster_reconciliation`

- `identity_role_surface`: `partial`; missing `['supervisor_or_authority']`
- `source_addressability_surface`: `partial`; missing `['section_coordinate', 'title_or_heading']`
- `source_authority_surface`: `partial`; missing `['authority_or_evidence_role', 'source_actor_or_date']`
- `answer_detail_surface`: `partial`; missing `['availability_or_scope', 'commitment_or_future_action', 'detail_or_explanation']`
- `object_device_surface`: `ledger_only`; missing `['device_or_system', 'object_or_item_id']`
- `temporal_event_surface`: `partial`; missing `['timestamp_or_date']`
- `measure_count_surface`: `partial`; missing `['duration_or_hours', 'threshold_or_limit']`
- `custody_control_surface`: `ledger_only`; missing `['access_or_location', 'recall_or_return']`
