# Compile Surface Invariant Audit

- Schema: `compile_surface_invariant_audit_v1`
- Compiles: `1`
- Status counts: `{'ledger_only': 2, 'partial': 2, 'pass': 3}`

## Fixture Summary

| Run | Fixture | Direct facts | Source-record facts | Pass | Partial | Candidate-only | Ledger-only | Fail | N/A |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `source_authority_invariant_probate_compile_20260514` | `probate_storage_access_register` | 61 | 2380 | 3 | 2 | 0 | 2 | 0 | 0 |

## Missing Or Weak Families

### `source_authority_invariant_probate_compile_20260514` / `probate_storage_access_register`

- `source_addressability_surface`: `partial`; missing `['basis_coordinate', 'chronology_coordinate', 'negative_inference_coordinate']`
- `rule_policy_surface`: `ledger_only`; missing `['exception_or_exclusion', 'policy_or_rule_id']`
- `temporal_event_surface`: `partial`; missing `['event_or_action', 'timestamp_or_date']`
- `measure_count_surface`: `ledger_only`; missing `['measurement_value', 'ratio_or_formula']`
