# Lens Vocabulary Transfer Audit

- Schema: `lens_vocabulary_transfer_audit_v1`
- Lens: `epistemic_uncertainty`
- Compiles: `3`
- Status counts: `{'not_applicable': 8, 'shallow_structural': 3, 'source_only': 3, 'structural': 22}`

## Term Summary

| Term | Structural | Shallow | Source-only | N/A |
| --- | ---: | ---: | ---: | ---: |
| `confirmed` | 2 | 0 | 0 | 1 |
| `corrected` | 1 | 0 | 1 | 1 |
| `disputed` | 1 | 0 | 0 | 2 |
| `inferred` | 3 | 0 | 0 | 0 |
| `pending` | 2 | 0 | 1 | 0 |
| `provisional` | 2 | 0 | 0 | 1 |
| `resolved_negative` | 0 | 2 | 0 | 1 |
| `retracted` | 3 | 0 | 0 | 0 |
| `superseded` | 3 | 0 | 0 | 0 |
| `unknown` | 2 | 0 | 0 | 1 |
| `unstated` | 1 | 0 | 1 | 1 |
| `unsupported` | 2 | 1 | 0 | 0 |

## Fixture Summary

| Run | Fixture | Direct facts | Source-record facts | Structural | Shallow | Source-only | N/A |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `lens_vocab_epistemic_uncertainty_compile_20260515` | `field_trial_notes` | 36 | 118 | 9 | 0 | 0 | 3 |
| `lens_vocab_epistemic_uncertainty_compile_20260515` | `route_change_notice` | 41 | 100 | 8 | 2 | 0 | 2 |
| `lens_vocab_epistemic_uncertainty_compile_20260515` | `tool_checkout_review` | 28 | 111 | 5 | 1 | 3 | 3 |

## Shallow Or Source-Only Terms

- `route_change_notice` shallow: `resolved_negative`, `unsupported`
- `tool_checkout_review` shallow: `resolved_negative`
- `tool_checkout_review` source-only: `corrected`, `pending`, `unstated`
