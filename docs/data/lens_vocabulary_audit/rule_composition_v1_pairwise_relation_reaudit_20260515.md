# Lens Vocabulary Transfer Audit

- Schema: `lens_vocabulary_transfer_audit_v1`
- Lens: `rule_composition`
- Compiles: `3`
- Status counts: `{'not_applicable': 4, 'shallow_structural': 9, 'source_only': 4, 'structural': 13}`

## Term Summary

| Term | Structural | Shallow | Source-only | N/A |
| --- | ---: | ---: | ---: | ---: |
| `activation_condition` | 0 | 1 | 2 | 0 |
| `base_rule` | 1 | 1 | 1 | 0 |
| `eligibility_condition` | 1 | 2 | 0 | 0 |
| `exception` | 3 | 0 | 0 | 0 |
| `expiration` | 2 | 0 | 0 | 1 |
| `fallback_rule` | 2 | 0 | 1 | 0 |
| `override` | 1 | 2 | 0 | 0 |
| `precedence` | 1 | 2 | 0 | 0 |
| `threshold` | 1 | 1 | 0 | 1 |
| `vote_requirement` | 1 | 0 | 0 | 2 |

## Fixture Summary

| Run | Fixture | Direct facts | Source-record facts | Structural | Shallow | Source-only | N/A |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `lens_vocab_rule_composition_guidance_replay_compile_20260515` | `garden_plot_governance` | 25 | 120 | 6 | 1 | 2 | 1 |
| `lens_vocab_rule_composition_guidance_replay_compile_20260515` | `library_room_booking` | 22 | 108 | 3 | 5 | 1 | 1 |
| `lens_vocab_rule_composition_guidance_replay_compile_20260515` | `makerspace_tool_access` | 12 | 100 | 4 | 3 | 1 | 2 |

## Shallow Or Source-Only Terms

- `garden_plot_governance` shallow: `base_rule`
- `garden_plot_governance` source-only: `activation_condition`, `fallback_rule`
- `library_room_booking` shallow: `threshold`, `activation_condition`, `eligibility_condition`, `override`, `precedence`
- `library_room_booking` source-only: `base_rule`
- `makerspace_tool_access` shallow: `eligibility_condition`, `override`, `precedence`
- `makerspace_tool_access` source-only: `activation_condition`
