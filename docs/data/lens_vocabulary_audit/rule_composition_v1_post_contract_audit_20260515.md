# Lens Vocabulary Transfer Audit

- Schema: `lens_vocabulary_transfer_audit_v1`
- Lens: `rule_composition`
- Compiles: `3`
- Status counts: `{'not_applicable': 4, 'shallow_structural': 14, 'source_only': 1, 'structural': 11}`

## Term Summary

| Term | Structural | Shallow | Source-only | N/A |
| --- | ---: | ---: | ---: | ---: |
| `activation_condition` | 0 | 3 | 0 | 0 |
| `base_rule` | 2 | 1 | 0 | 0 |
| `eligibility_condition` | 0 | 3 | 0 | 0 |
| `exception` | 2 | 1 | 0 | 0 |
| `expiration` | 2 | 0 | 0 | 1 |
| `fallback_rule` | 3 | 0 | 0 | 0 |
| `override` | 0 | 3 | 0 | 0 |
| `precedence` | 0 | 3 | 0 | 0 |
| `threshold` | 1 | 0 | 1 | 1 |
| `vote_requirement` | 1 | 0 | 0 | 2 |

## Fixture Summary

| Run | Fixture | Direct facts | Source-record facts | Structural | Shallow | Source-only | N/A |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `lens_vocab_rule_composition_post_contract_compile_20260515` | `garden_plot_governance` | 30 | 120 | 3 | 5 | 1 | 1 |
| `lens_vocab_rule_composition_post_contract_compile_20260515` | `library_room_booking` | 21 | 108 | 4 | 5 | 0 | 1 |
| `lens_vocab_rule_composition_post_contract_compile_20260515` | `makerspace_tool_access` | 19 | 100 | 4 | 4 | 0 | 2 |

## Shallow Or Source-Only Terms

- `garden_plot_governance` shallow: `base_rule`, `activation_condition`, `eligibility_condition`, `override`, `precedence`
- `garden_plot_governance` source-only: `threshold`
- `library_room_booking` shallow: `exception`, `activation_condition`, `eligibility_condition`, `override`, `precedence`
- `makerspace_tool_access` shallow: `activation_condition`, `eligibility_condition`, `override`, `precedence`
