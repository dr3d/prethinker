# Compile Surface Audit Comparison

- Schema: `compile_surface_audit_comparison_v1`
- Min direct-fact ratio: `0.85`
- Max lost predicates: `0`
- Summary: `{'fixture_count': 1, 'gate_status_counts': {'regression': 1}, 'direct_fact_regression_count': 0, 'family_regression_count': 0, 'contract_regression_count': 0, 'predicate_loss_count': 16, 'predicate_loss_regression_count': 1}`

| Fixture | Gate | Direct facts | Ratio | Family regressions | Contract regressions | Lost predicates |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `dulse_ledger` | `regression` | 66 -> 113 | 1.7121 | 0 | 0 | 16 |

## Regressions

### `dulse_ledger`
- Predicate preservation failed: `16` lost predicates.
- Lost predicates: `debt_created`, `debt_deadline`, `debt_settled`, `debt_violation`, `dispute_initiated`, `dispute_position`, `family`, `good`, `location`, `person`, `person_belongs_to`, `person_role`, `rule_penalty`, `shelter_event`, `shelter_marker`, `shelter_penalty`.
