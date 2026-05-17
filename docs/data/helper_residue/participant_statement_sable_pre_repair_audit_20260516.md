# Compile Surface Invariant Audit

- Schema: `compile_surface_invariant_audit_v1`
- Compiles: `1`
- Status counts: `{'partial': 5, 'pass': 7}`

## Fixture Summary

| Run | Fixture | Direct facts | Source-record facts | Pass | Partial | Candidate-only | Ledger-only | Fail | N/A |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `financial_baseline_sable_recompile_20260516` | `sable_creek_budget` | 118 | 1542 | 7 | 5 | 0 | 0 | 0 | 0 |

## Missing Or Weak Families

### `financial_baseline_sable_recompile_20260516` / `sable_creek_budget`

- `identity_role_surface`: `partial`; missing `['custodian_or_holder', 'registrar_or_recorder']`
- `source_addressability_surface`: `partial`; missing `['title_or_heading']`
- `temporal_event_surface`: `partial`; missing `['timestamp_or_date']`
- `event_backbone_unit_surface`: `partial`; missing `['temporal_anchor']`
- `custody_control_surface`: `partial`; missing `['custody_or_possession']`
- `participant_statement_status_contract`: `partial`; missing keys `['certification_issued[1]', 'certification_issued[2]', 'public_comment_made[3]', 'public_comment_made[4]', 'public_comment_made[5]', 'public_comment_made[6]', 'staff_estimate[9]', 'staff_estimate[12]']`
