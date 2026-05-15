# Compile Surface Invariant Audit

- Schema: `compile_surface_invariant_audit_v1`
- Compiles: `1`
- Status counts: `{'partial': 2, 'pass': 5}`

## Fixture Summary

| Run | Fixture | Direct facts | Source-record facts | Pass | Partial | Candidate-only | Ledger-only | Fail | N/A |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `compile_surface_invariant_focused_probate_20260514` | `probate_storage_access_register` | 162 | 2388 | 5 | 2 | 0 | 0 | 0 | 0 |

## Missing Or Weak Families

### `compile_surface_invariant_focused_probate_20260514` / `probate_storage_access_register`

- `source_addressability_surface`: `partial`; missing `['chronology_coordinate']`
- `measure_count_surface`: `partial`; missing `['measurement_value']`
