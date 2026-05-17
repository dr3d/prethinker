# Compile Surface Audit Comparison

- Schema: `compile_surface_audit_comparison_v1`
- Min direct-fact ratio: `0.85`
- Summary: `{'fixture_count': 1, 'gate_status_counts': {'regression': 1}, 'direct_fact_regression_count': 1, 'family_regression_count': 5, 'contract_regression_count': 1, 'predicate_loss_count': 20}`

| Fixture | Gate | Direct facts | Ratio | Family regressions | Contract regressions | Lost predicates |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `sable_creek_budget` | `regression` | 118 -> 32 | 0.2712 | 5 | 1 | 20 |

## Regressions

### `sable_creek_budget`
- Direct fact count regressed: `118` -> `32`.
- Family `answer_detail_surface`: `pass` -> `partial`.
- Family `custody_control_surface`: `partial` -> `ledger_only`.
- Family `financial_baseline_surface`: `pass` -> `partial`.
- Family `measure_count_surface`: `pass` -> `partial`.
- Family `source_authority_surface`: `pass` -> `partial`.
- Contract `financial_baseline_derivation_contract`: `pass` -> `partial`.
- Lost predicates: `balance_derived_from`, `certification_issued`, `charter_rule`, `conflict_of_interest_disclosed`, `council_ratified`, `emergency_declared`, `emergency_expenditure_authorized`, `event_happened`, `fund_balance`, `legal_opinion`, `opinion_is_binding`, `person_relationship`, `person_role`, `public_comment_made`, `record_correction`, `rule_exception`, `rule_threshold`, `staff_estimate`, `vote_cast`, `vote_result`.
