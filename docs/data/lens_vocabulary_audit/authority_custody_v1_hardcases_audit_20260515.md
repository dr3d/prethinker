# Lens Vocabulary Transfer Audit

- Schema: `lens_vocabulary_transfer_audit_v1`
- Lens: `authority_custody`
- Compiles: `6`
- Status counts: `{'not_applicable': 9, 'shallow_structural': 28, 'source_only': 1, 'structural': 22}`

## Term Summary

| Term | Structural | Shallow | Source-only | N/A |
| --- | ---: | ---: | ---: | ---: |
| `access_control` | 6 | 0 | 0 | 0 |
| `board_vote` | 1 | 3 | 0 | 2 |
| `controlling_finding` | 2 | 4 | 0 | 0 |
| `court_order` | 0 | 2 | 0 | 4 |
| `custody_holder` | 5 | 0 | 1 | 0 |
| `draft_recommendation` | 2 | 4 | 0 | 0 |
| `governing_rule` | 3 | 3 | 0 | 0 |
| `noncontrolling_source` | 1 | 4 | 0 | 1 |
| `official_record` | 0 | 6 | 0 | 0 |
| `staff_note` | 2 | 2 | 0 | 2 |

## Fixture Summary

| Run | Fixture | Direct facts | Source-record facts | Structural | Shallow | Source-only | N/A |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `lens_vocab_authority_custody_hardcases_compile_20260515` | `clinic_fridge_notice` | 51 | 83 | 2 | 7 | 0 | 1 |
| `lens_vocab_authority_custody_hardcases_compile_20260515` | `library_cart_policy_draft` | 38 | 74 | 5 | 3 | 0 | 2 |
| `lens_vocab_authority_custody_hardcases_compile_20260515` | `pool_lane_schedule_draft` | 50 | 76 | 5 | 3 | 0 | 2 |
| `lens_vocab_authority_custody_hardcases_compile_20260515` | `repair_room_signage` | 39 | 73 | 2 | 6 | 0 | 2 |
| `lens_vocab_authority_custody_hardcases_compile_20260515` | `studio_key_access_draft` | 62 | 82 | 4 | 4 | 1 | 1 |
| `lens_vocab_authority_custody_hardcases_compile_20260515` | `theater_prop_cage` | 37 | 82 | 4 | 5 | 0 | 1 |

## Shallow Or Source-Only Terms

- `clinic_fridge_notice` shallow: `court_order`, `governing_rule`, `official_record`, `staff_note`, `draft_recommendation`, `controlling_finding`, `noncontrolling_source`
- `library_cart_policy_draft` shallow: `court_order`, `official_record`, `controlling_finding`
- `pool_lane_schedule_draft` shallow: `governing_rule`, `official_record`, `draft_recommendation`
- `repair_room_signage` shallow: `governing_rule`, `board_vote`, `official_record`, `draft_recommendation`, `controlling_finding`, `noncontrolling_source`
- `studio_key_access_draft` shallow: `board_vote`, `official_record`, `controlling_finding`, `noncontrolling_source`
- `studio_key_access_draft` source-only: `custody_holder`
- `theater_prop_cage` shallow: `board_vote`, `official_record`, `staff_note`, `draft_recommendation`, `noncontrolling_source`
