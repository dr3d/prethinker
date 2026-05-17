# Compile Surface Invariant Audit

- Schema: `compile_surface_invariant_audit_v1`
- Compiles: `1`
- Status counts: `{'partial': 3, 'pass': 9}`

## Fixture Summary

| Run | Fixture | Direct facts | Source-record facts | Pass | Partial | Candidate-only | Ledger-only | Fail | N/A |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `merged_sable_replay_20260516` | `sable_creek_budget` | 199 | 1542 | 9 | 3 | 0 | 0 | 0 | 0 |

## Missing Or Weak Families

### `merged_sable_replay_20260516` / `sable_creek_budget`

- `identity_role_surface`: `partial`; missing `['custodian_or_holder', 'registrar_or_recorder']`
- `source_addressability_surface`: `partial`; missing `['title_or_heading']`
- `custody_control_surface`: `partial`; missing `['custody_or_possession']`
- `participant_statement_status_contract`: `partial`; missing keys `['public_comment_made[3]', 'public_comment_made[4]', 'public_comment_made[5]', 'public_comment_made[6]', 'staff_estimate[9]', 'public_comment[14]', 'public_comment[15]', 'public_comment[16]', 'public_comment[17]']`
