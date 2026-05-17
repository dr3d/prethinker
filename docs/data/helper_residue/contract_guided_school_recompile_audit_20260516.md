# Compile Surface Invariant Audit

- Schema: `compile_surface_invariant_audit_v1`
- Compiles: `1`
- Status counts: `{'partial': 10, 'pass': 2}`

## Fixture Summary

| Run | Fixture | Direct facts | Source-record facts | Pass | Partial | Candidate-only | Ledger-only | Fail | N/A |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `contract_guided_school_recompile_20260516` | `school_activity_roster_reconciliation` | 219 | 2217 | 2 | 10 | 0 | 0 | 0 | 0 |

## Missing Or Weak Families

### `contract_guided_school_recompile_20260516` / `school_activity_roster_reconciliation`

- `identity_role_surface`: `partial`; missing `['registrar_or_recorder', 'supervisor_or_authority']`
- `source_addressability_surface`: `partial`; missing `['title_or_heading']`
- `source_authority_surface`: `partial`; missing `['source_actor_or_date']`
- `answer_detail_surface`: `partial`; missing `['availability_or_scope', 'detail_or_explanation']`
- `participant_statement_surface`: `partial`; missing `['speech_act_or_record_type']`
- `object_device_surface`: `partial`; missing `['device_or_system']`
- `temporal_event_surface`: `partial`; missing `['timestamp_or_date']`
- `event_backbone_unit_surface`: `partial`; missing `['participant_or_system', 'subject_or_object', 'temporal_anchor']`
- `measure_count_surface`: `partial`; missing `['duration_or_hours', 'threshold_or_limit']`
- `financial_baseline_surface`: `partial`; missing `['baseline_value', 'resulting_value']`
- `participant_statement_status_contract`: `missing_structural_surface`; missing keys `[]`
