# Lens Vocabulary Transfer Audit

- Schema: `lens_vocabulary_transfer_audit_v1`
- Lens: `operational_record_status`
- Compiles: `6`
- Status counts: `{'not_applicable': 7, 'shallow_structural': 29, 'source_only': 10, 'structural': 32}`

## Term Summary

| Term | Structural | Shallow | Source-only | N/A |
| --- | ---: | ---: | ---: | ---: |
| `approved` | 2 | 4 | 0 | 0 |
| `assigned` | 4 | 2 | 0 | 0 |
| `closed` | 2 | 4 | 0 | 0 |
| `corrected` | 3 | 1 | 2 | 0 |
| `current_status` | 5 | 0 | 1 | 0 |
| `denied` | 3 | 2 | 0 | 1 |
| `filed` | 1 | 3 | 2 | 0 |
| `pending` | 2 | 4 | 0 | 0 |
| `received` | 1 | 4 | 1 | 0 |
| `reopened` | 1 | 2 | 0 | 3 |
| `status_transition` | 1 | 0 | 2 | 3 |
| `superseded` | 4 | 0 | 2 | 0 |
| `withdrawn` | 3 | 3 | 0 | 0 |

## Fixture Summary

| Run | Fixture | Direct facts | Source-record facts | Structural | Shallow | Source-only | N/A |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `lens_vocab_operational_record_status_actor_content_compile_20260515` | `clinic_intake_corrections` | 20 | 84 | 6 | 6 | 1 | 0 |
| `lens_vocab_operational_record_status_actor_content_compile_20260515` | `grant_review_queue` | 56 | 98 | 9 | 2 | 1 | 1 |
| `lens_vocab_operational_record_status_actor_content_compile_20260515` | `library_preservation_queue` | 64 | 81 | 2 | 7 | 3 | 1 |
| `lens_vocab_operational_record_status_actor_content_compile_20260515` | `permit_renewal_docket` | 37 | 88 | 2 | 8 | 1 | 2 |
| `lens_vocab_operational_record_status_actor_content_compile_20260515` | `warehouse_repair_log` | 39 | 85 | 7 | 3 | 2 | 1 |
| `lens_vocab_operational_record_status_actor_content_compile_20260515` | `water_sample_docket` | 26 | 82 | 6 | 3 | 2 | 2 |

## Shallow Or Source-Only Terms

- `clinic_intake_corrections` shallow: `received`, `filed`, `assigned`, `approved`, `denied`, `reopened`
- `clinic_intake_corrections` source-only: `superseded`
- `grant_review_queue` shallow: `received`, `closed`
- `grant_review_queue` source-only: `filed`
- `library_preservation_queue` shallow: `received`, `approved`, `denied`, `withdrawn`, `pending`, `corrected`, `closed`
- `library_preservation_queue` source-only: `filed`, `current_status`, `status_transition`
- `permit_renewal_docket` shallow: `received`, `filed`, `assigned`, `approved`, `withdrawn`, `pending`, `reopened`, `closed`
- `permit_renewal_docket` source-only: `corrected`
- `warehouse_repair_log` shallow: `filed`, `approved`, `pending`
- `warehouse_repair_log` source-only: `received`, `status_transition`
- `water_sample_docket` shallow: `withdrawn`, `pending`, `closed`
- `water_sample_docket` source-only: `corrected`, `superseded`
