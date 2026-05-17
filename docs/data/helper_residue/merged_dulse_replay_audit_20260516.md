# Compile Surface Invariant Audit

- Schema: `compile_surface_invariant_audit_v1`
- Compiles: `1`
- Status counts: `{'ledger_only': 1, 'partial': 5, 'pass': 6}`

## Fixture Summary

| Run | Fixture | Direct facts | Source-record facts | Pass | Partial | Candidate-only | Ledger-only | Fail | N/A |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `merged_dulse_replay_20260516` | `dulse_ledger` | 173 | 1049 | 6 | 5 | 0 | 1 | 0 | 0 |

## Missing Or Weak Families

### `merged_dulse_replay_20260516` / `dulse_ledger`

- `source_addressability_surface`: `partial`; missing `['basis_coordinate', 'title_or_heading']`
- `source_authority_surface`: `partial`; missing `['source_document_or_correspondence']`
- `object_device_surface`: `ledger_only`; missing `['vendor_or_model']`
- `measure_count_surface`: `partial`; missing `['measurement_value']`
- `financial_baseline_surface`: `partial`; missing `['resulting_value']`
- `custody_control_surface`: `partial`; missing `['ownership_or_title']`
- `participant_statement_status_contract`: `partial`; missing keys `['clerk_observation[3]', 'clerk_observation[4]', 'clerk_observation[6]', 'clerk_observation[9]']`
