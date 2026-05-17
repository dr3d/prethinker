# Compile Surface Audit Comparison

- Schema: `compile_surface_audit_comparison_v1`
- Min direct-fact ratio: `0.85`
- Summary: `{'fixture_count': 1, 'gate_status_counts': {'regression': 1}, 'direct_fact_regression_count': 1, 'family_regression_count': 1, 'contract_regression_count': 0, 'predicate_loss_count': 17}`

| Fixture | Gate | Direct facts | Ratio | Family regressions | Contract regressions | Lost predicates |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `sable_creek_budget` | `regression` | 118 -> 82 | 0.6949 | 1 | 0 | 17 |

## Regressions

### `sable_creek_budget`
- Direct fact count regressed: `118` -> `82`.
- Family `answer_detail_surface`: `pass` -> `partial`.
- Lost predicates: `balance_derived_from`, `certification_issued`, `conflict_of_interest_disclosed`, `council_ratified`, `emergency_declared`, `emergency_expenditure_authorized`, `event_happened`, `fund_balance`, `legal_opinion`, `opinion_is_binding`, `person_relationship`, `public_comment_made`, `rule_exception`, `rule_threshold`, `staff_estimate`, `vote_cast`, `vote_result`.
