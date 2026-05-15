# Lens Vocabulary Transfer Audit

- Schema: `lens_vocabulary_transfer_audit_v1`
- Lens: `operational_record_status`
- Compiles: `6`
- Status counts: `{'not_applicable': 8, 'shallow_structural': 41, 'source_only': 14, 'structural': 15}`

## Term Summary

| Term | Structural | Shallow | Source-only | N/A |
| --- | ---: | ---: | ---: | ---: |
| `approved` | 2 | 4 | 0 | 0 |
| `assigned` | 1 | 4 | 1 | 0 |
| `closed` | 0 | 6 | 0 | 0 |
| `corrected` | 2 | 3 | 1 | 0 |
| `current_status` | 2 | 1 | 3 | 0 |
| `denied` | 1 | 4 | 0 | 1 |
| `filed` | 0 | 3 | 3 | 0 |
| `pending` | 1 | 4 | 1 | 0 |
| `received` | 0 | 4 | 2 | 0 |
| `reopened` | 0 | 3 | 0 | 3 |
| `status_transition` | 1 | 1 | 2 | 2 |
| `superseded` | 4 | 2 | 0 | 0 |
| `withdrawn` | 1 | 2 | 1 | 2 |

## Fixture Summary

| Run | Fixture | Direct facts | Source-record facts | Structural | Shallow | Source-only | N/A |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `lens_vocab_operational_record_status_compile_20260515` | `clinic_intake_corrections` | 51 | 84 | 2 | 10 | 0 | 1 |
| `lens_vocab_operational_record_status_compile_20260515` | `grant_review_queue` | 43 | 84 | 1 | 9 | 1 | 2 |
| `lens_vocab_operational_record_status_compile_20260515` | `library_preservation_queue` | 42 | 81 | 6 | 4 | 2 | 1 |
| `lens_vocab_operational_record_status_compile_20260515` | `permit_renewal_docket` | 49 | 85 | 1 | 10 | 1 | 1 |
| `lens_vocab_operational_record_status_compile_20260515` | `warehouse_repair_log` | 13 | 85 | 4 | 4 | 4 | 1 |
| `lens_vocab_operational_record_status_compile_20260515` | `water_sample_docket` | 66 | 82 | 1 | 4 | 6 | 2 |

## Shallow Or Source-Only Terms

- `clinic_intake_corrections` shallow: `received`, `filed`, `assigned`, `approved`, `denied`, `corrected`, `superseded`, `reopened`, `closed`, `status_transition`
- `grant_review_queue` shallow: `received`, `filed`, `assigned`, `approved`, `denied`, `corrected`, `reopened`, `closed`, `current_status`
- `grant_review_queue` source-only: `pending`
- `library_preservation_queue` shallow: `received`, `assigned`, `pending`, `closed`
- `library_preservation_queue` source-only: `filed`, `status_transition`
- `permit_renewal_docket` shallow: `received`, `filed`, `assigned`, `approved`, `withdrawn`, `pending`, `corrected`, `superseded`, `reopened`, `closed`
- `permit_renewal_docket` source-only: `current_status`
- `warehouse_repair_log` shallow: `denied`, `withdrawn`, `pending`, `closed`
- `warehouse_repair_log` source-only: `received`, `filed`, `current_status`, `status_transition`
- `water_sample_docket` shallow: `approved`, `denied`, `pending`, `closed`
- `water_sample_docket` source-only: `received`, `filed`, `assigned`, `withdrawn`, `corrected`, `current_status`
