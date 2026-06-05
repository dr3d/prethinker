# Domain Predicate Proposal Validation

This report validates proposal shape only. A passing proposal is not a
promoted domain-pack claim until its transfer plan succeeds under the
claim-bearing gates.

- Proposals: `4`
- Blocking errors: `0`
- Warnings: `2`
- Status: `pass`

| Proposal | Signature | Status | Pending Work | Candidate Reviews | Source Oracles | Errors | Warnings |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `fda_warning_letter_response_assessment_item_v1` | `fda_response_assessment_item/6` | `candidate` | `` | `fda_warning_letter_domain_transfer_001:source_only_candidate_review_complete; fda_warning_letter_domain_transfer_002:source_only_candidate_review_complete; fda_warning_letter_domain_transfer_003:source_only_candidate_review_complete` | `` | `[]` | `[]` |
| `fda_warning_letter_response_documentation_gap_v1` | `fda_response_documentation_gap/5` | `rejected` | `` | `fda_warning_letter_domain_transfer_002:blocked_forbidden` | `` | `[]` | `[]` |
| `procurement_gao_decision_wrapper_v1` | `gao_bid_protest_decision/7` | `draft` | `` | `` | `procurement_gao_decision_wrapper_v1_procurement_gao_decision_wrapper_oracle_review_20260605:source_oracle_complete` | `[]` | `['candidate_signature_not_yet_registered']` |
| `puc_order_wrapper_v1` | `puc_order/7` | `draft` | `` | `` | `puc_order_wrapper_v1_puc_order_wrapper_oracle_review_20260604:source_oracle_complete` | `[]` | `['candidate_signature_not_yet_registered']` |
