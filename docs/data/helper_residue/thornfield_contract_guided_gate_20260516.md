# Compile Surface Audit Comparison

- Schema: `compile_surface_audit_comparison_v1`
- Min direct-fact ratio: `0.85`
- Summary: `{'fixture_count': 1, 'gate_status_counts': {'regression': 1}, 'direct_fact_regression_count': 1, 'family_regression_count': 0, 'contract_regression_count': 0, 'predicate_loss_count': 13}`

| Fixture | Gate | Direct facts | Ratio | Family regressions | Contract regressions | Lost predicates |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `thornfield_variance` | `regression` | 122 -> 59 | 0.4836 | 0 | 0 | 13 |

## Regressions

### `thornfield_variance`
- Direct fact count regressed: `122` -> `59`.
- Lost predicates: `appeal_filed`, `board_composition_rule`, `business_use_claim`, `hearing_attendance`, `lot_line_survey`, `notice_requirement`, `permit_application`, `record_status`, `setback_requirement`, `survey_measurement`, `testimony_statement`, `variance_finding`, `variance_standard`.
