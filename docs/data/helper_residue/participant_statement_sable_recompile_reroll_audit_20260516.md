# Compile Surface Invariant Audit

- Schema: `compile_surface_invariant_audit_v1`
- Compiles: `1`
- Status counts: `{'partial': 5, 'pass': 7}`

## Fixture Summary

| Run | Fixture | Direct facts | Source-record facts | Pass | Partial | Candidate-only | Ledger-only | Fail | N/A |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `participant_statement_sable_recompile_reroll_20260516` | `sable_creek_budget` | 82 | 1542 | 7 | 5 | 0 | 0 | 0 | 0 |

## Missing Or Weak Families

### `participant_statement_sable_recompile_reroll_20260516` / `sable_creek_budget`

- `identity_role_surface`: `partial`; missing `['custodian_or_holder', 'registrar_or_recorder']`
- `source_addressability_surface`: `partial`; missing `['title_or_heading']`
- `answer_detail_surface`: `partial`; missing `['commitment_or_future_action', 'detail_or_explanation']`
- `event_backbone_unit_surface`: `partial`; missing `['outcome_or_state']`
- `custody_control_surface`: `partial`; missing `['custody_or_possession']`
- `participant_statement_status_contract`: `partial`; missing keys `['public_comment[2]', 'public_comment[3]', 'public_comment[4]', 'public_comment[5]']`
