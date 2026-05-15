# Compile Surface Invariant Audit

- Schema: `compile_surface_invariant_audit_v1`
- Compiles: `1`
- Status counts: `{'partial': 3, 'pass': 5}`

## Fixture Summary

| Run | Fixture | Direct facts | Source-record facts | Pass | Partial | Candidate-only | Ledger-only | Fail | N/A |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `source_authority_density_probate_compile_local_20260515` | `probate_storage_access_register` | 127 | 2380 | 5 | 3 | 0 | 0 | 0 | 0 |

## Missing Or Weak Families

### `source_authority_density_probate_compile_local_20260515` / `probate_storage_access_register`

- `source_addressability_surface`: `partial`; missing `['basis_coordinate', 'chronology_coordinate', 'negative_inference_coordinate']`
- `rule_policy_surface`: `partial`; missing `['exception_or_exclusion']`
- `measure_count_surface`: `partial`; missing `['measurement_value']`
