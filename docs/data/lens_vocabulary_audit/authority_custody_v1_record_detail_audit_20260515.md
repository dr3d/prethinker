# Lens Vocabulary Transfer Audit

- Schema: `lens_vocabulary_transfer_audit_v1`
- Lens: `authority_custody`
- Compiles: `3`
- Status counts: `{'shallow_structural': 13, 'source_only': 1, 'structural': 16}`

## Term Summary

| Term | Structural | Shallow | Source-only | N/A |
| --- | ---: | ---: | ---: | ---: |
| `access_control` | 2 | 1 | 0 | 0 |
| `board_vote` | 2 | 1 | 0 | 0 |
| `controlling_finding` | 2 | 1 | 0 | 0 |
| `court_order` | 1 | 2 | 0 | 0 |
| `custody_holder` | 3 | 0 | 0 | 0 |
| `draft_recommendation` | 1 | 2 | 0 | 0 |
| `governing_rule` | 3 | 0 | 0 | 0 |
| `noncontrolling_source` | 0 | 2 | 1 | 0 |
| `official_record` | 0 | 3 | 0 | 0 |
| `staff_note` | 2 | 1 | 0 | 0 |

## Fixture Summary

| Run | Fixture | Direct facts | Source-record facts | Structural | Shallow | Source-only | N/A |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `lens_vocab_authority_custody_record_detail_compile_20260515` | `clinic_device_custody` | 60 | 102 | 5 | 5 | 0 | 0 |
| `lens_vocab_authority_custody_record_detail_compile_20260515` | `housing_archive_access` | 72 | 106 | 5 | 5 | 0 | 0 |
| `lens_vocab_authority_custody_record_detail_compile_20260515` | `lab_sample_chain` | 124 | 109 | 6 | 3 | 1 | 0 |

## Shallow Or Source-Only Terms

- `clinic_device_custody` shallow: `court_order`, `official_record`, `draft_recommendation`, `noncontrolling_source`, `access_control`
- `housing_archive_access` shallow: `official_record`, `staff_note`, `draft_recommendation`, `controlling_finding`, `noncontrolling_source`
- `lab_sample_chain` shallow: `court_order`, `board_vote`, `official_record`
- `lab_sample_chain` source-only: `noncontrolling_source`
