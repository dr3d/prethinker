# Lens Vocabulary Transfer Audit

- Schema: `lens_vocabulary_transfer_audit_v1`
- Lens: `authority_custody`
- Compiles: `6`
- Status counts: `{'shallow_structural': 29, 'structural': 31}`

## Term Summary

| Term | Structural | Shallow | Source-only | N/A |
| --- | ---: | ---: | ---: | ---: |
| `access_control` | 6 | 0 | 0 | 0 |
| `board_vote` | 4 | 2 | 0 | 0 |
| `controlling_finding` | 3 | 3 | 0 | 0 |
| `court_order` | 3 | 3 | 0 | 0 |
| `custody_holder` | 5 | 1 | 0 | 0 |
| `draft_recommendation` | 1 | 5 | 0 | 0 |
| `governing_rule` | 4 | 2 | 0 | 0 |
| `noncontrolling_source` | 0 | 6 | 0 | 0 |
| `official_record` | 2 | 4 | 0 | 0 |
| `staff_note` | 3 | 3 | 0 | 0 |

## Fixture Summary

| Run | Fixture | Direct facts | Source-record facts | Structural | Shallow | Source-only | N/A |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `lens_vocab_authority_custody_expanded_compile_20260515` | `clinic_device_custody` | 55 | 102 | 6 | 4 | 0 | 0 |
| `lens_vocab_authority_custody_expanded_compile_20260515` | `community_garden_gate_key` | 99 | 91 | 5 | 5 | 0 | 0 |
| `lens_vocab_authority_custody_expanded_compile_20260515` | `housing_archive_access` | 94 | 106 | 4 | 6 | 0 | 0 |
| `lens_vocab_authority_custody_expanded_compile_20260515` | `lab_sample_chain` | 88 | 103 | 5 | 5 | 0 | 0 |
| `lens_vocab_authority_custody_expanded_compile_20260515` | `makerspace_tool_lockout` | 81 | 94 | 7 | 3 | 0 | 0 |
| `lens_vocab_authority_custody_expanded_compile_20260515` | `transit_lost_property_release` | 54 | 92 | 4 | 6 | 0 | 0 |

## Shallow Or Source-Only Terms

- `clinic_device_custody` shallow: `court_order`, `draft_recommendation`, `noncontrolling_source`, `custody_holder`
- `community_garden_gate_key` shallow: `governing_rule`, `official_record`, `staff_note`, `draft_recommendation`, `noncontrolling_source`
- `housing_archive_access` shallow: `governing_rule`, `official_record`, `staff_note`, `draft_recommendation`, `controlling_finding`, `noncontrolling_source`
- `lab_sample_chain` shallow: `official_record`, `staff_note`, `draft_recommendation`, `controlling_finding`, `noncontrolling_source`
- `makerspace_tool_lockout` shallow: `court_order`, `board_vote`, `noncontrolling_source`
- `transit_lost_property_release` shallow: `court_order`, `board_vote`, `official_record`, `draft_recommendation`, `controlling_finding`, `noncontrolling_source`
