# Lens Vocabulary Transfer Audit

- Schema: `lens_vocabulary_transfer_audit_v1`
- Lens: `rule_composition`
- Compiles: `3`
- Status counts: `{'not_applicable': 4, 'shallow_structural': 9, 'source_only': 5, 'structural': 12}`

## Term Summary

| Term | Structural | Shallow | Source-only | N/A |
| --- | ---: | ---: | ---: | ---: |
| `activation_condition` | 0 | 0 | 3 | 0 |
| `base_rule` | 2 | 1 | 0 | 0 |
| `eligibility_condition` | 1 | 2 | 0 | 0 |
| `exception` | 2 | 1 | 0 | 0 |
| `expiration` | 2 | 0 | 0 | 1 |
| `fallback_rule` | 2 | 1 | 0 | 0 |
| `override` | 1 | 1 | 1 | 0 |
| `precedence` | 1 | 2 | 0 | 0 |
| `threshold` | 1 | 0 | 1 | 1 |
| `vote_requirement` | 0 | 1 | 0 | 2 |

## Fixture Summary

| Run | Fixture | Direct facts | Source-record facts | Structural | Shallow | Source-only | N/A |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `lens_vocab_rule_composition_compile_20260515` | `garden_plot_governance` | 19 | 120 | 1 | 5 | 3 | 1 |
| `lens_vocab_rule_composition_compile_20260515` | `library_room_booking` | 15 | 108 | 8 | 0 | 1 | 1 |
| `lens_vocab_rule_composition_compile_20260515` | `makerspace_tool_access` | 16 | 100 | 3 | 4 | 1 | 2 |

## Shallow Or Source-Only Terms

- `garden_plot_governance` shallow: `base_rule`, `exception`, `eligibility_condition`, `precedence`, `vote_requirement`
- `garden_plot_governance` source-only: `threshold`, `activation_condition`, `override`
- `library_room_booking` source-only: `activation_condition`
- `makerspace_tool_access` shallow: `eligibility_condition`, `override`, `precedence`, `fallback_rule`
- `makerspace_tool_access` source-only: `activation_condition`
