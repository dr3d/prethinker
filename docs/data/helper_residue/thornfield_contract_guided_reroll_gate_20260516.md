# Compile Surface Audit Comparison

- Schema: `compile_surface_audit_comparison_v1`
- Min direct-fact ratio: `0.85`
- Summary: `{'fixture_count': 1, 'gate_status_counts': {'regression': 1}, 'direct_fact_regression_count': 1, 'family_regression_count': 0, 'contract_regression_count': 0, 'predicate_loss_count': 15}`

| Fixture | Gate | Direct facts | Ratio | Family regressions | Contract regressions | Lost predicates |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `thornfield_variance` | `regression` | 122 -> 101 | 0.8279 | 0 | 0 | 15 |

## Regressions

### `thornfield_variance`
- Direct fact count regressed: `122` -> `101`.
- Lost predicates: `board_composition_rule`, `business_use_claim`, `easement_location`, `hearing_attendance`, `lot_line_survey`, `notice_requirement`, `objection_filed`, `permit_application`, `property_dimension`, `record_status`, `setback_requirement`, `structure_attribute`, `testimony_statement`, `variance_finding`, `variance_standard`.
