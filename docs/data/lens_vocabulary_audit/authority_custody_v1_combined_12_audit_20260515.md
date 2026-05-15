# Lens Vocabulary Transfer Audit

- Schema: `lens_vocabulary_transfer_audit_v1`
- Lens: `authority_custody`
- Compiles: `12`
- Status counts: `{'not_applicable': 9, 'shallow_structural': 57, 'source_only': 1, 'structural': 53}`

## Term Summary

| Term | Structural | Shallow | Source-only | N/A |
| --- | ---: | ---: | ---: | ---: |
| `access_control` | 12 | 0 | 0 | 0 |
| `board_vote` | 5 | 5 | 0 | 2 |
| `controlling_finding` | 5 | 7 | 0 | 0 |
| `court_order` | 3 | 5 | 0 | 4 |
| `custody_holder` | 10 | 1 | 1 | 0 |
| `draft_recommendation` | 3 | 9 | 0 | 0 |
| `governing_rule` | 7 | 5 | 0 | 0 |
| `noncontrolling_source` | 1 | 10 | 0 | 1 |
| `official_record` | 2 | 10 | 0 | 0 |
| `staff_note` | 5 | 5 | 0 | 2 |

## Fixture Summary

| Run | Fixture | Direct facts | Source-record facts | Structural | Shallow | Source-only | N/A |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `lens_vocab_authority_custody_expanded_compile_20260515` | `clinic_device_custody` | 55 | 102 | 6 | 4 | 0 | 0 |
| `lens_vocab_authority_custody_expanded_compile_20260515` | `community_garden_gate_key` | 99 | 91 | 5 | 5 | 0 | 0 |
| `lens_vocab_authority_custody_expanded_compile_20260515` | `housing_archive_access` | 94 | 106 | 4 | 6 | 0 | 0 |
| `lens_vocab_authority_custody_expanded_compile_20260515` | `lab_sample_chain` | 88 | 103 | 5 | 5 | 0 | 0 |
| `lens_vocab_authority_custody_expanded_compile_20260515` | `makerspace_tool_lockout` | 81 | 94 | 7 | 3 | 0 | 0 |
| `lens_vocab_authority_custody_expanded_compile_20260515` | `transit_lost_property_release` | 54 | 92 | 4 | 6 | 0 | 0 |
| `lens_vocab_authority_custody_hardcases_compile_20260515` | `clinic_fridge_notice` | 51 | 83 | 2 | 7 | 0 | 1 |
| `lens_vocab_authority_custody_hardcases_compile_20260515` | `library_cart_policy_draft` | 38 | 74 | 5 | 3 | 0 | 2 |
| `lens_vocab_authority_custody_hardcases_compile_20260515` | `pool_lane_schedule_draft` | 50 | 76 | 5 | 3 | 0 | 2 |
| `lens_vocab_authority_custody_hardcases_compile_20260515` | `repair_room_signage` | 39 | 73 | 2 | 6 | 0 | 2 |
| `lens_vocab_authority_custody_hardcases_compile_20260515` | `studio_key_access_draft` | 62 | 82 | 4 | 4 | 1 | 1 |
| `lens_vocab_authority_custody_hardcases_compile_20260515` | `theater_prop_cage` | 37 | 82 | 4 | 5 | 0 | 1 |

## Shallow Or Source-Only Terms

- `clinic_device_custody` shallow: `court_order`, `draft_recommendation`, `noncontrolling_source`, `custody_holder`
- `community_garden_gate_key` shallow: `governing_rule`, `official_record`, `staff_note`, `draft_recommendation`, `noncontrolling_source`
- `housing_archive_access` shallow: `governing_rule`, `official_record`, `staff_note`, `draft_recommendation`, `controlling_finding`, `noncontrolling_source`
- `lab_sample_chain` shallow: `official_record`, `staff_note`, `draft_recommendation`, `controlling_finding`, `noncontrolling_source`
- `makerspace_tool_lockout` shallow: `court_order`, `board_vote`, `noncontrolling_source`
- `transit_lost_property_release` shallow: `court_order`, `board_vote`, `official_record`, `draft_recommendation`, `controlling_finding`, `noncontrolling_source`
- `clinic_fridge_notice` shallow: `court_order`, `governing_rule`, `official_record`, `staff_note`, `draft_recommendation`, `controlling_finding`, `noncontrolling_source`
- `library_cart_policy_draft` shallow: `court_order`, `official_record`, `controlling_finding`
- `pool_lane_schedule_draft` shallow: `governing_rule`, `official_record`, `draft_recommendation`
- `repair_room_signage` shallow: `governing_rule`, `board_vote`, `official_record`, `draft_recommendation`, `controlling_finding`, `noncontrolling_source`
- `studio_key_access_draft` shallow: `board_vote`, `official_record`, `controlling_finding`, `noncontrolling_source`
- `studio_key_access_draft` source-only: `custody_holder`
- `theater_prop_cage` shallow: `board_vote`, `official_record`, `staff_note`, `draft_recommendation`, `noncontrolling_source`
