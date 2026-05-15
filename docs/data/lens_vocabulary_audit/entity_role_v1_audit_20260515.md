# Lens Vocabulary Transfer Audit

- Schema: `lens_vocabulary_transfer_audit_v1`
- Lens: `entity_role`
- Compiles: `3`
- Status counts: `{'not_applicable': 7, 'shallow_structural': 7, 'source_only': 4, 'structural': 9}`

## Term Summary

| Term | Structural | Shallow | Source-only | N/A |
| --- | ---: | ---: | ---: | ---: |
| `alias` | 2 | 0 | 0 | 1 |
| `custody` | 2 | 1 | 0 | 0 |
| `family_relationship` | 0 | 1 | 0 | 2 |
| `identity_equivalence` | 1 | 0 | 0 | 2 |
| `membership` | 0 | 2 | 1 | 0 |
| `ownership` | 0 | 1 | 2 | 0 |
| `responsibility` | 1 | 2 | 0 | 0 |
| `role_holder` | 3 | 0 | 0 | 0 |
| `role_transition` | 0 | 0 | 1 | 2 |

## Fixture Summary

| Run | Fixture | Direct facts | Source-record facts | Structural | Shallow | Source-only | N/A |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `lens_vocab_entity_role_compile_20260515` | `badge_role_alias` | 18 | 83 | 4 | 2 | 1 | 2 |
| `lens_vocab_entity_role_compile_20260515` | `family_guardian_custody` | 24 | 79 | 3 | 3 | 1 | 2 |
| `lens_vocab_entity_role_compile_20260515` | `membership_transition_ownership` | 23 | 82 | 2 | 2 | 2 | 3 |

## Shallow Or Source-Only Terms

- `badge_role_alias` shallow: `ownership`, `responsibility`
- `badge_role_alias` source-only: `membership`
- `family_guardian_custody` shallow: `membership`, `custody`, `family_relationship`
- `family_guardian_custody` source-only: `ownership`
- `membership_transition_ownership` shallow: `membership`, `responsibility`
- `membership_transition_ownership` source-only: `role_transition`, `ownership`
