# Compile Surface Invariant Audit

- Schema: `compile_surface_invariant_audit_v1`
- Compiles: `1`
- Status counts: `{'ledger_only': 2, 'partial': 6, 'pass': 2}`

## Fixture Summary

| Run | Fixture | Direct facts | Source-record facts | Pass | Partial | Candidate-only | Ledger-only | Fail | N/A |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `event_backbone_sable_recompile_20260516` | `sable_creek_budget` | 66 | 1592 | 2 | 6 | 0 | 2 | 0 | 0 |

## Missing Or Weak Families

### `event_backbone_sable_recompile_20260516` / `sable_creek_budget`

- `identity_role_surface`: `partial`; missing `['clinical_or_safety_role', 'registrar_or_recorder']`
- `source_addressability_surface`: `ledger_only`; missing `['negative_inference_coordinate', 'section_coordinate', 'title_or_heading']`
- `source_authority_surface`: `partial`; missing `['source_actor_or_date']`
- `answer_detail_surface`: `ledger_only`; missing `['commitment_or_future_action', 'detail_or_explanation', 'negative_or_exclusion_detail']`
- `temporal_event_surface`: `partial`; missing `['timestamp_or_date']`
- `event_backbone_unit_surface`: `partial`; missing `['temporal_anchor']`
- `measure_count_surface`: `partial`; missing `['count_or_total', 'ratio_or_formula']`
- `custody_control_surface`: `partial`; missing `['ownership_or_title']`
