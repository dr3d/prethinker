# Compile Surface Invariant Audit

- Schema: `compile_surface_invariant_audit_v1`
- Compiles: `1`
- Status counts: `{'not_applicable': 3, 'partial': 3, 'pass': 2}`

## Fixture Summary

| Run | Fixture | Direct facts | Source-record facts | Pass | Partial | Candidate-only | Ledger-only | Fail | N/A |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `multi_subject_authority_compile_20260515` | `multi_subject_authority_pair` | 28 | 125 | 2 | 3 | 0 | 0 | 0 | 3 |

## Missing Or Weak Families

### `multi_subject_authority_compile_20260515` / `multi_subject_authority_pair`

- `source_addressability_surface`: `partial`; missing `['section_coordinate', 'title_or_heading']`
- `source_authority_surface`: `partial`; missing `['source_document_or_correspondence']`
- `rule_policy_surface`: `partial`; missing `['policy_or_rule_id']`
