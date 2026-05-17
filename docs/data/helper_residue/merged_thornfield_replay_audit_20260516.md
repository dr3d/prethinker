# Compile Surface Invariant Audit

- Schema: `compile_surface_invariant_audit_v1`
- Compiles: `1`
- Status counts: `{'partial': 2, 'pass': 10}`

## Fixture Summary

| Run | Fixture | Direct facts | Source-record facts | Pass | Partial | Candidate-only | Ledger-only | Fail | N/A |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `merged_thornfield_replay_20260516` | `thornfield_variance` | 223 | 1704 | 10 | 2 | 0 | 0 | 0 | 0 |

## Missing Or Weak Families

### `merged_thornfield_replay_20260516` / `thornfield_variance`

- `source_addressability_surface`: `partial`; missing `['basis_coordinate', 'title_or_heading']`
- `answer_detail_surface`: `partial`; missing `['detail_or_explanation']`
- `financial_baseline_derivation_contract`: `partial`; missing keys `['adjustment_value', 'resulting_value']`
- `participant_statement_status_contract`: `missing_status_companion`; missing keys `['testimony_statement[1]', 'testimony_statement[2]', 'testimony_statement[3]', 'testimony_statement[4]', 'testimony_statement[5]', 'testimony_statement[6]', 'testimony_statement[7]']`
