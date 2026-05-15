# Lens Vocabulary Transfer Audit

- Schema: `lens_vocabulary_transfer_audit_v1`
- Lens: `authority_custody`
- Compiles: `3`
- Status counts: `{'shallow_structural': 11, 'source_only': 1, 'structural': 18}`

## Term Summary

| Term | Structural | Shallow | Source-only | N/A |
| --- | ---: | ---: | ---: | ---: |
| `access_control` | 3 | 0 | 0 | 0 |
| `board_vote` | 2 | 1 | 0 | 0 |
| `controlling_finding` | 1 | 2 | 0 | 0 |
| `court_order` | 1 | 2 | 0 | 0 |
| `custody_holder` | 3 | 0 | 0 | 0 |
| `draft_recommendation` | 1 | 2 | 0 | 0 |
| `governing_rule` | 2 | 1 | 0 | 0 |
| `noncontrolling_source` | 1 | 1 | 1 | 0 |
| `official_record` | 2 | 1 | 0 | 0 |
| `staff_note` | 2 | 1 | 0 | 0 |

## Fixture Summary

| Run | Fixture | Direct facts | Source-record facts | Structural | Shallow | Source-only | N/A |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `lens_vocab_authority_custody_compile_20260515` | `clinic_device_custody` | 40 | 102 | 3 | 6 | 1 | 0 |
| `lens_vocab_authority_custody_compile_20260515` | `housing_archive_access` | 91 | 111 | 5 | 5 | 0 | 0 |
| `lens_vocab_authority_custody_compile_20260515` | `lab_sample_chain` | 72 | 103 | 10 | 0 | 0 | 0 |

## Shallow Or Source-Only Terms

- `clinic_device_custody` shallow: `court_order`, `board_vote`, `official_record`, `staff_note`, `draft_recommendation`, `controlling_finding`
- `clinic_device_custody` source-only: `noncontrolling_source`
- `housing_archive_access` shallow: `court_order`, `governing_rule`, `draft_recommendation`, `controlling_finding`, `noncontrolling_source`
