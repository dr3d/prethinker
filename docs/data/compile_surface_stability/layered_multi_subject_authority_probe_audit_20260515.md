# Compile Surface Invariant Audit

- Schema: `compile_surface_invariant_audit_v1`
- Compiles: `1`
- Status counts: `{'candidate_only': 2, 'not_applicable': 2, 'partial': 3, 'pass': 1}`

## Fixture Summary

| Run | Fixture | Direct facts | Source-record facts | Pass | Partial | Candidate-only | Ledger-only | Fail | N/A |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `layered_multi_subject_authority_compile_20260515` | `layered_multi_subject_authority_pair` | 21 | 161 | 1 | 3 | 2 | 0 | 0 | 2 |

## Missing Or Weak Families

### `layered_multi_subject_authority_compile_20260515` / `layered_multi_subject_authority_pair`

- `identity_role_surface`: `partial`; missing `['supervisor_or_authority']`
- `source_addressability_surface`: `candidate_only`; missing `['negative_inference_coordinate', 'section_coordinate', 'title_or_heading']`
- `source_authority_surface`: `partial`; missing `['authority_or_evidence_role']`
- `rule_policy_surface`: `candidate_only`; missing `['exception_or_exclusion', 'policy_or_rule_id']`
- `custody_control_surface`: `partial`; missing `['ownership_or_title']`
