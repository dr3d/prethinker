# Lens Vocabulary Transfer Audit

- Schema: `lens_vocabulary_transfer_audit_v1`
- Lens: `temporal_status`
- Compiles: `6`
- Status counts: `{'not_applicable': 31, 'shallow_structural': 5, 'structural': 12}`

## Term Summary

| Term | Structural | Shallow | Source-only | N/A |
| --- | ---: | ---: | ---: | ---: |
| `deadline` | 2 | 0 | 0 | 4 |
| `duration` | 0 | 0 | 0 | 6 |
| `effective_date` | 4 | 0 | 0 | 2 |
| `expiration` | 0 | 0 | 0 | 6 |
| `interval` | 0 | 0 | 0 | 6 |
| `status_at` | 2 | 3 | 0 | 1 |
| `temporal_supersession` | 3 | 2 | 0 | 1 |
| `timestamp` | 1 | 0 | 0 | 5 |

## Fixture Summary

| Run | Fixture | Direct facts | Source-record facts | Structural | Shallow | Source-only | N/A |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `transition_delta_contract_compile_20260515` | `document_field_delta` | 15 | 65 | 1 | 1 | 0 | 6 |
| `transition_delta_contract_compile_20260515` | `role_membership_transition` | 29 | 58 | 2 | 2 | 0 | 4 |
| `transition_delta_contract_compile_20260515` | `status_value_transition` | 13 | 56 | 2 | 1 | 0 | 5 |
| `transition_delta_contract_td002_compile_20260515` | `document_section_delta` | 9 | 70 | 2 | 1 | 0 | 5 |
| `transition_delta_contract_td002_compile_20260515` | `status_reason_delta` | 17 | 63 | 3 | 0 | 0 | 5 |
| `transition_delta_contract_td004_compile_20260515` | `policy_threshold_revision` | 11 | 81 | 2 | 0 | 0 | 6 |

## Shallow Or Source-Only Terms

- `document_field_delta` shallow: `status_at`
- `role_membership_transition` shallow: `status_at`, `temporal_supersession`
- `status_value_transition` shallow: `temporal_supersession`
- `document_section_delta` shallow: `status_at`
