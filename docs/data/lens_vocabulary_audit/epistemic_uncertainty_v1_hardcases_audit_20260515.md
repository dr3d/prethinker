# Lens Vocabulary Transfer Audit

- Schema: `lens_vocabulary_transfer_audit_v1`
- Lens: `epistemic_uncertainty`
- Compiles: `3`
- Status counts: `{'not_applicable': 14, 'shallow_structural': 7, 'source_only': 3, 'structural': 12}`

## Term Summary

| Term | Structural | Shallow | Source-only | N/A |
| --- | ---: | ---: | ---: | ---: |
| `confirmed` | 1 | 1 | 0 | 1 |
| `corrected` | 2 | 0 | 0 | 1 |
| `disputed` | 0 | 1 | 0 | 2 |
| `inferred` | 0 | 0 | 0 | 3 |
| `pending` | 0 | 1 | 0 | 2 |
| `provisional` | 1 | 1 | 0 | 1 |
| `resolved_negative` | 2 | 0 | 0 | 1 |
| `retracted` | 0 | 1 | 0 | 2 |
| `superseded` | 2 | 0 | 1 | 0 |
| `unknown` | 2 | 0 | 0 | 1 |
| `unstated` | 1 | 1 | 1 | 0 |
| `unsupported` | 1 | 1 | 1 | 0 |

## Fixture Summary

| Run | Fixture | Direct facts | Source-record facts | Structural | Shallow | Source-only | N/A |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `lens_vocab_epistemic_uncertainty_hardcases_compile_20260515` | `community_claim_support` | 39 | 137 | 4 | 4 | 1 | 3 |
| `lens_vocab_epistemic_uncertainty_hardcases_compile_20260515` | `inventory_absence_resolution` | 32 | 127 | 5 | 0 | 0 | 7 |
| `lens_vocab_epistemic_uncertainty_hardcases_compile_20260515` | `locker_metadata_gap` | 39 | 125 | 3 | 3 | 2 | 4 |

## Shallow Or Source-Only Terms

- `community_claim_support` shallow: `confirmed`, `provisional`, `retracted`, `unstated`
- `community_claim_support` source-only: `unsupported`
- `locker_metadata_gap` shallow: `disputed`, `pending`, `unsupported`
- `locker_metadata_gap` source-only: `superseded`, `unstated`
