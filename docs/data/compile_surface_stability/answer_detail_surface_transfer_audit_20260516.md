# Compile Surface Invariant Audit

- Schema: `compile_surface_invariant_audit_v1`
- Compiles: `1`
- Status counts: `{'ledger_only': 1, 'not_applicable': 2, 'partial': 4, 'pass': 2}`

## Fixture Summary

| Run | Fixture | Direct facts | Source-record facts | Pass | Partial | Candidate-only | Ledger-only | Fail | N/A |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `tmp` | `answer_detail_surface_transfer_compile_20260516` | 34 | 190 | 2 | 4 | 0 | 1 | 0 | 2 |

## Missing Or Weak Families

### `tmp` / `answer_detail_surface_transfer_compile_20260516`

- `identity_role_surface`: `partial`; missing `['supervisor_or_authority']`
- `source_addressability_surface`: `partial`; missing `['section_coordinate', 'title_or_heading']`
- `answer_detail_surface`: `partial`; missing `['commitment_or_future_action']`
- `rule_policy_surface`: `partial`; missing `['policy_or_rule_id']`
- `measure_count_surface`: `ledger_only`; missing `['count_or_total']`
