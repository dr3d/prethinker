# Lens Vocabulary Transfer Audit

- Schema: `lens_vocabulary_transfer_audit_v1`
- Lens: `temporal_status`
- Compiles: `3`
- Status counts: `{'not_applicable': 11, 'shallow_structural': 1, 'structural': 12}`

## Term Summary

| Term | Structural | Shallow | Source-only | N/A |
| --- | ---: | ---: | ---: | ---: |
| `deadline` | 2 | 0 | 0 | 1 |
| `duration` | 3 | 0 | 0 | 0 |
| `effective_date` | 1 | 0 | 0 | 2 |
| `expiration` | 1 | 0 | 0 | 2 |
| `interval` | 3 | 0 | 0 | 0 |
| `status_at` | 2 | 1 | 0 | 0 |
| `temporal_supersession` | 0 | 0 | 0 | 3 |
| `timestamp` | 0 | 0 | 0 | 3 |

## Fixture Summary

| Run | Fixture | Direct facts | Source-record facts | Structural | Shallow | Source-only | N/A |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `lens_vocab_temporal_status_compile_20260515` | `machine_uptime_log` | 10 | 69 | 3 | 0 | 0 | 5 |
| `lens_vocab_temporal_status_compile_20260515` | `permit_expiry_notice` | 15 | 66 | 5 | 1 | 0 | 2 |
| `lens_vocab_temporal_status_compile_20260515` | `rental_window_notice` | 11 | 68 | 4 | 0 | 0 | 4 |

## Shallow Or Source-Only Terms

- `permit_expiry_notice` shallow: `status_at`
