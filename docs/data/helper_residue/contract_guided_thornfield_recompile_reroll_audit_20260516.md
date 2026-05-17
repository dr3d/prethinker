# Compile Surface Invariant Audit

- Schema: `compile_surface_invariant_audit_v1`
- Compiles: `1`
- Status counts: `{'partial': 6, 'pass': 6}`

## Fixture Summary

| Run | Fixture | Direct facts | Source-record facts | Pass | Partial | Candidate-only | Ledger-only | Fail | N/A |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `contract_guided_thornfield_recompile_reroll_20260516` | `thornfield_variance` | 101 | 1704 | 6 | 6 | 0 | 0 | 0 | 0 |

## Missing Or Weak Families

### `contract_guided_thornfield_recompile_reroll_20260516` / `thornfield_variance`

- `source_addressability_surface`: `partial`; missing `['basis_coordinate', 'title_or_heading']`
- `answer_detail_surface`: `partial`; missing `['detail_or_explanation']`
- `participant_statement_surface`: `partial`; missing `['speech_act_or_record_type']`
- `object_device_surface`: `partial`; missing `['object_or_item_id']`
- `financial_baseline_surface`: `partial`; missing `['adjustment_value']`
- `custody_control_surface`: `partial`; missing `['access_or_location']`
- `financial_baseline_derivation_contract`: `partial`; missing keys `['adjustment_value', 'resulting_value']`
- `participant_statement_status_contract`: `missing_structural_surface`; missing keys `[]`
