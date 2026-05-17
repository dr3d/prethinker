# Compile Surface Audit Comparison

- Schema: `compile_surface_audit_comparison_v1`
- Min direct-fact ratio: `0.85`
- Max lost predicates: `0`
- Summary: `{'fixture_count': 1, 'gate_status_counts': {'regression': 1}, 'direct_fact_regression_count': 0, 'family_regression_count': 0, 'contract_regression_count': 1, 'predicate_loss_count': 0, 'predicate_loss_regression_count': 0}`

| Fixture | Gate | Direct facts | Ratio | Family regressions | Contract regressions | Lost predicates |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `ridgeline_fire` | `regression` | 242 -> 287 | 1.186 | 0 | 1 | 0 |

## Regressions

### `ridgeline_fire`
- Contract `participant_statement_status_contract`: `pass` -> `partial`.
