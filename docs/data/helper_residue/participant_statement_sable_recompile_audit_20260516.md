# Compile Surface Invariant Audit

- Schema: `compile_surface_invariant_audit_v1`
- Compiles: `1`
- Status counts: `{'ledger_only': 1, 'partial': 8, 'pass': 3}`

## Fixture Summary

| Run | Fixture | Direct facts | Source-record facts | Pass | Partial | Candidate-only | Ledger-only | Fail | N/A |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `participant_statement_sable_recompile_20260516` | `sable_creek_budget` | 32 | 1542 | 3 | 8 | 0 | 1 | 0 | 0 |

## Missing Or Weak Families

### `participant_statement_sable_recompile_20260516` / `sable_creek_budget`

- `identity_role_surface`: `partial`; missing `['custodian_or_holder', 'registrar_or_recorder', 'supervisor_or_authority']`
- `source_addressability_surface`: `partial`; missing `['section_coordinate', 'title_or_heading']`
- `source_authority_surface`: `partial`; missing `['authority_or_evidence_role', 'governed_subject_or_item', 'source_actor_or_date']`
- `answer_detail_surface`: `partial`; missing `['commitment_or_future_action']`
- `temporal_event_surface`: `partial`; missing `['correction_or_supersession', 'timestamp_or_date']`
- `event_backbone_unit_surface`: `partial`; missing `['event_identity', 'subject_or_object', 'temporal_anchor']`
- `measure_count_surface`: `partial`; missing `['count_or_total', 'ratio_or_formula']`
- `financial_baseline_surface`: `partial`; missing `['adjustment_value']`
- `custody_control_surface`: `ledger_only`; missing `['custody_or_possession', 'ownership_or_title', 'recall_or_return']`
- `financial_baseline_derivation_contract`: `partial`; missing keys `['adjustment_value']`
- `participant_statement_status_contract`: `missing_status_companion`; missing keys `['reserve_balance_at[1]', 'fiscal_certification[2]', 'reserve_balance_at[3]', 'public_comment[4]', 'public_comment[5]', 'public_comment[6]', 'public_comment[7]', 'fiscal_certification[8]', 'legal_advice[9]']`
