# Compile Surface Invariant Audit

- Schema: `compile_surface_invariant_audit_v1`
- Compiles: `1`
- Status counts: `{'not_applicable': 2, 'partial': 1, 'pass': 9}`

## Fixture Summary

| Run | Fixture | Direct facts | Source-record facts | Pass | Partial | Candidate-only | Ledger-only | Fail | N/A |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `merged_ridgeline_replay_20260516` | `ridgeline_fire` | 287 | 1605 | 9 | 1 | 0 | 0 | 0 | 2 |

## Missing Or Weak Families

### `merged_ridgeline_replay_20260516` / `ridgeline_fire`

- `source_addressability_surface`: `partial`; missing `['title_or_heading']`
- `participant_statement_status_contract`: `partial`; missing keys `['witness_claim[2]']`
