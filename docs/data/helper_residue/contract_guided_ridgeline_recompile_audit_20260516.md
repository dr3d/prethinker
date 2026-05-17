# Compile Surface Invariant Audit

- Schema: `compile_surface_invariant_audit_v1`
- Compiles: `1`
- Status counts: `{'not_applicable': 2, 'partial': 7, 'pass': 3}`

## Fixture Summary

| Run | Fixture | Direct facts | Source-record facts | Pass | Partial | Candidate-only | Ledger-only | Fail | N/A |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `contract_guided_ridgeline_recompile_20260516` | `ridgeline_fire` | 45 | 1605 | 3 | 7 | 0 | 0 | 0 | 2 |

## Missing Or Weak Families

### `contract_guided_ridgeline_recompile_20260516` / `ridgeline_fire`

- `identity_role_surface`: `partial`; missing `['registrar_or_recorder', 'supervisor_or_authority']`
- `source_addressability_surface`: `partial`; missing `['chronology_coordinate', 'section_coordinate', 'title_or_heading']`
- `source_authority_surface`: `partial`; missing `['authority_or_evidence_role']`
- `participant_statement_surface`: `partial`; missing `['content_or_position', 'context_or_source_event', 'speaker_or_actor']`
- `rule_policy_surface`: `partial`; missing `['policy_or_rule_id', 'ratio_or_requirement']`
- `measure_count_surface`: `partial`; missing `['count_or_total', 'threshold_or_limit']`
- `financial_baseline_surface`: `partial`; missing `['constraint_or_threshold']`
- `participant_statement_status_contract`: `partial`; missing keys `['witness_claim[1]']`
