# Compile Surface Audit Comparison

- Schema: `compile_surface_audit_comparison_v1`
- Min direct-fact ratio: `0.85`
- Max lost predicates: `0`
- Summary: `{'fixture_count': 1, 'gate_status_counts': {'regression': 1}, 'direct_fact_regression_count': 0, 'family_regression_count': 0, 'contract_regression_count': 0, 'predicate_loss_count': 9, 'predicate_loss_regression_count': 1}`

| Fixture | Gate | Direct facts | Ratio | Family regressions | Contract regressions | Lost predicates |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `school_activity_roster_reconciliation` | `regression` | 190 -> 219 | 1.1526 | 0 | 0 | 9 |

## Regressions

### `school_activity_roster_reconciliation`
- Predicate preservation failed: `9` lost predicates.
- Lost predicates: `accommodation_detail`, `adult_role`, `bus_chaperone`, `corrected_value`, `exempt_from_ratio`, `fact_authorization`, `medical_condition`, `policy_rule`, `seat_row_assignment`.
