# Lens Vocabulary Transfer Audit

- Schema: `lens_vocabulary_transfer_audit_v1`
- Lens: `rule_composition`
- Compiles: `1`
- Status counts: `{'not_applicable': 3, 'shallow_structural': 2, 'structural': 5}`

## Term Summary

| Term | Structural | Shallow | Source-only | N/A |
| --- | ---: | ---: | ---: | ---: |
| `activation_condition` | 1 | 0 | 0 | 0 |
| `base_rule` | 1 | 0 | 0 | 0 |
| `eligibility_condition` | 0 | 0 | 0 | 1 |
| `exception` | 1 | 0 | 0 | 0 |
| `expiration` | 0 | 1 | 0 | 0 |
| `fallback_rule` | 1 | 0 | 0 | 0 |
| `override` | 1 | 0 | 0 | 0 |
| `precedence` | 0 | 1 | 0 | 0 |
| `threshold` | 0 | 0 | 0 | 1 |
| `vote_requirement` | 0 | 0 | 0 | 1 |

## Fixture Summary

| Run | Fixture | Direct facts | Source-record facts | Structural | Shallow | Source-only | N/A |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `lens_vocab_rule_composition_activation_anchor_compile_20260515` | `makerspace_tool_access` | 23 | 100 | 5 | 2 | 0 | 3 |

## Shallow Or Source-Only Terms

- `makerspace_tool_access` shallow: `precedence`, `expiration`
