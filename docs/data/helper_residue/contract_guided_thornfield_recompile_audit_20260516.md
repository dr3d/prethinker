# Compile Surface Invariant Audit

- Schema: `compile_surface_invariant_audit_v1`
- Compiles: `1`
- Status counts: `{'partial': 9, 'pass': 3}`

## Fixture Summary

| Run | Fixture | Direct facts | Source-record facts | Pass | Partial | Candidate-only | Ledger-only | Fail | N/A |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `contract_guided_thornfield_recompile_20260516` | `thornfield_variance` | 59 | 1704 | 3 | 9 | 0 | 0 | 0 | 0 |

## Missing Or Weak Families

### `contract_guided_thornfield_recompile_20260516` / `thornfield_variance`

- `source_addressability_surface`: `partial`; missing `['title_or_heading']`
- `source_authority_surface`: `partial`; missing `['source_document_or_correspondence']`
- `answer_detail_surface`: `partial`; missing `['availability_or_scope']`
- `participant_statement_surface`: `partial`; missing `['speaker_or_actor', 'speech_act_or_record_type']`
- `object_device_surface`: `partial`; missing `['vendor_or_model']`
- `event_backbone_unit_surface`: `partial`; missing `['participant_or_system']`
- `measure_count_surface`: `partial`; missing `['count_or_total', 'measurement_value']`
- `financial_baseline_surface`: `partial`; missing `['baseline_value']`
- `custody_control_surface`: `partial`; missing `['ownership_or_title']`
- `financial_baseline_derivation_contract`: `partial`; missing keys `['adjustment_value', 'baseline_or_previous_value', 'resulting_value', 'scenario_or_basis']`
- `participant_statement_status_contract`: `missing_structural_surface`; missing keys `[]`
