# Lens Vocabulary Transfer Audit

- Schema: `lens_vocabulary_transfer_audit_v1`
- Lens: `operational_record_status`
- Compiles: `6`
- Status counts: `{'not_applicable': 8, 'shallow_structural': 48, 'source_only': 13, 'structural': 9}`

## Term Summary

| Term | Structural | Shallow | Source-only | N/A |
| --- | ---: | ---: | ---: | ---: |
| `approved` | 0 | 6 | 0 | 0 |
| `assigned` | 1 | 5 | 0 | 0 |
| `closed` | 0 | 6 | 0 | 0 |
| `corrected` | 0 | 5 | 1 | 0 |
| `current_status` | 0 | 1 | 5 | 0 |
| `denied` | 0 | 5 | 0 | 1 |
| `filed` | 0 | 2 | 4 | 0 |
| `pending` | 0 | 6 | 0 | 0 |
| `received` | 1 | 4 | 1 | 0 |
| `reopened` | 0 | 3 | 0 | 3 |
| `status_transition` | 0 | 1 | 2 | 3 |
| `superseded` | 6 | 0 | 0 | 0 |
| `withdrawn` | 1 | 4 | 0 | 1 |

## Fixture Summary

| Run | Fixture | Direct facts | Source-record facts | Structural | Shallow | Source-only | N/A |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `lens_vocab_operational_record_status_palette_compile_20260515` | `clinic_intake_corrections` | 55 | 84 | 1 | 9 | 2 | 1 |
| `lens_vocab_operational_record_status_palette_compile_20260515` | `grant_review_queue` | 24 | 84 | 1 | 10 | 1 | 1 |
| `lens_vocab_operational_record_status_palette_compile_20260515` | `library_preservation_queue` | 27 | 81 | 3 | 5 | 4 | 1 |
| `lens_vocab_operational_record_status_palette_compile_20260515` | `permit_renewal_docket` | 29 | 85 | 1 | 9 | 1 | 2 |
| `lens_vocab_operational_record_status_palette_compile_20260515` | `warehouse_repair_log` | 16 | 85 | 2 | 6 | 4 | 1 |
| `lens_vocab_operational_record_status_palette_compile_20260515` | `water_sample_docket` | 35 | 82 | 1 | 9 | 1 | 2 |

## Shallow Or Source-Only Terms

- `clinic_intake_corrections` shallow: `received`, `assigned`, `approved`, `denied`, `withdrawn`, `pending`, `corrected`, `reopened`, `closed`
- `clinic_intake_corrections` source-only: `filed`, `current_status`
- `grant_review_queue` shallow: `received`, `filed`, `assigned`, `approved`, `denied`, `withdrawn`, `pending`, `corrected`, `reopened`, `closed`
- `grant_review_queue` source-only: `current_status`
- `library_preservation_queue` shallow: `approved`, `denied`, `withdrawn`, `pending`, `closed`
- `library_preservation_queue` source-only: `filed`, `corrected`, `current_status`, `status_transition`
- `permit_renewal_docket` shallow: `received`, `assigned`, `approved`, `pending`, `corrected`, `reopened`, `closed`, `current_status`, `status_transition`
- `permit_renewal_docket` source-only: `filed`
- `warehouse_repair_log` shallow: `assigned`, `approved`, `denied`, `pending`, `corrected`, `closed`
- `warehouse_repair_log` source-only: `received`, `filed`, `current_status`, `status_transition`
- `water_sample_docket` shallow: `received`, `filed`, `assigned`, `approved`, `denied`, `withdrawn`, `pending`, `corrected`, `closed`
- `water_sample_docket` source-only: `current_status`
