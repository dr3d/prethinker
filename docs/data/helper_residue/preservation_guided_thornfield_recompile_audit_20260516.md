# Compile Surface Invariant Audit

- Schema: `compile_surface_invariant_audit_v1`
- Compiles: `1`
- Status counts: `{'ledger_only': 2, 'partial': 8, 'pass': 2}`

## Fixture Summary

| Run | Fixture | Direct facts | Source-record facts | Pass | Partial | Candidate-only | Ledger-only | Fail | N/A |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `preservation_guided_thornfield_recompile_20260516` | `thornfield_variance` | 52 | 1704 | 2 | 8 | 0 | 2 | 0 | 0 |

## Missing Or Weak Families

### `preservation_guided_thornfield_recompile_20260516` / `thornfield_variance`

- `source_addressability_surface`: `partial`; missing `['title_or_heading']`
- `source_authority_surface`: `partial`; missing `['source_actor_or_date']`
- `answer_detail_surface`: `partial`; missing `['availability_or_scope', 'detail_or_explanation']`
- `rule_policy_surface`: `partial`; missing `['policy_or_rule_id']`
- `object_device_surface`: `ledger_only`; missing `['object_or_item_id', 'vendor_or_model']`
- `temporal_event_surface`: `ledger_only`; missing `['timestamp_or_date']`
- `event_backbone_unit_surface`: `partial`; missing `['subject_or_object', 'temporal_anchor']`
- `measure_count_surface`: `partial`; missing `['duration_or_hours', 'measurement_value']`
- `financial_baseline_surface`: `partial`; missing `['baseline_value', 'resulting_value', 'scenario_or_actuality']`
- `custody_control_surface`: `partial`; missing `['ownership_or_title']`
- `financial_baseline_derivation_contract`: `partial`; missing keys `['adjustment_value', 'baseline_or_previous_value', 'resulting_value', 'scenario_or_basis']`
