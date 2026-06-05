# Domain Predicate Proposal Validation

This report validates proposal shape only. A passing proposal is not a
promoted domain-pack claim until its transfer plan succeeds under the
claim-bearing gates.

- Proposals: `4`
- Blocking errors: `0`
- Warnings: `3`
- Status: `pass`

| Proposal | Signature | Status | Pending Work | Candidate Reviews | Source Oracles | Errors | Warnings |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `fda_warning_letter_response_assessment_item_v1` | `fda_response_assessment_item/6` | `candidate` | `source_only_candidate_oracle_review:tmp/fda_response_assessment_item_blind_review_work_order_20260604.zip` | `` | `` | `[]` | `['candidate_has_no_review_results']` |
| `fda_warning_letter_response_documentation_gap_v1` | `fda_response_documentation_gap/5` | `rejected` | `` | `fda_warning_letter_domain_transfer_002:blocked_forbidden` | `` | `[]` | `[]` |
| `procurement_gao_decision_wrapper_v1` | `gao_bid_protest_decision/7` | `draft` | `source_only_expected_forbidden_oracle:tmp/procurement_gao_decision_wrapper_oracle_work_order_20260605.zip` | `` | `` | `[]` | `['candidate_signature_not_yet_registered']` |
| `puc_order_wrapper_v1` | `puc_order/7` | `draft` | `source_only_expected_forbidden_oracle:tmp/puc_order_wrapper_oracle_work_order_20260604.zip` | `` | `` | `[]` | `['candidate_signature_not_yet_registered']` |
