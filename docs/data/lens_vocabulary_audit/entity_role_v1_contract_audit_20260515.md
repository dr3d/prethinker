# Lens Vocabulary Transfer Audit

- Schema: `lens_vocabulary_transfer_audit_v1`
- Lens: `entity_role`
- Compiles: `3`
- Status counts: `{'not_applicable': 7, 'shallow_structural': 2, 'source_only': 2, 'structural': 16}`

## Term Summary

| Term | Structural | Shallow | Source-only | N/A |
| --- | ---: | ---: | ---: | ---: |
| `alias` | 2 | 0 | 0 | 1 |
| `custody` | 3 | 0 | 0 | 0 |
| `family_relationship` | 1 | 0 | 0 | 2 |
| `identity_equivalence` | 1 | 0 | 0 | 2 |
| `membership` | 0 | 2 | 1 | 0 |
| `ownership` | 3 | 0 | 0 | 0 |
| `responsibility` | 3 | 0 | 0 | 0 |
| `role_holder` | 3 | 0 | 0 | 0 |
| `role_transition` | 0 | 0 | 1 | 2 |

## Fixture Summary

| Run | Fixture | Direct facts | Source-record facts | Structural | Shallow | Source-only | N/A |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `lens_vocab_entity_role_compile_20260515` | `badge_role_alias` | 18 | 83 | 6 | 0 | 1 | 2 |
| `lens_vocab_entity_role_compile_20260515` | `family_guardian_custody` | 24 | 79 | 6 | 1 | 0 | 2 |
| `lens_vocab_entity_role_compile_20260515` | `membership_transition_ownership` | 23 | 82 | 4 | 1 | 1 | 3 |

## Shallow Or Source-Only Terms

- `badge_role_alias` source-only: `membership`
- `family_guardian_custody` shallow: `membership`
- `membership_transition_ownership` shallow: `membership`
- `membership_transition_ownership` source-only: `role_transition`
