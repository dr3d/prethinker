# Compile Surface Audit Comparison

- Schema: `compile_surface_audit_comparison_v1`
- Min direct-fact ratio: `0.85`
- Summary: `{'fixture_count': 1, 'gate_status_counts': {'regression': 1}, 'direct_fact_regression_count': 1, 'family_regression_count': 2, 'contract_regression_count': 0, 'predicate_loss_count': 15}`

| Fixture | Gate | Direct facts | Ratio | Family regressions | Contract regressions | Lost predicates |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `thornfield_variance` | `regression` | 122 -> 52 | 0.4262 | 2 | 0 | 15 |

## Regressions

### `thornfield_variance`
- Direct fact count regressed: `122` -> `52`.
- Family `object_device_surface`: `partial` -> `ledger_only`.
- Family `rule_policy_surface`: `pass` -> `partial`.
- Lost predicates: `appeal_filed`, `board_composition_rule`, `business_use_claim`, `easement_location`, `hearing_attendance`, `lot_line_survey`, `notice_requirement`, `objection_filed`, `permit_application`, `record_status`, `setback_requirement`, `structure_attribute`, `testimony_statement`, `variance_finding`, `variance_standard`.
