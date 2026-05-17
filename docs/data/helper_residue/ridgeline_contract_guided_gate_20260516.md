# Compile Surface Audit Comparison

- Schema: `compile_surface_audit_comparison_v1`
- Min direct-fact ratio: `0.85`
- Max lost predicates: `0`
- Summary: `{'fixture_count': 1, 'gate_status_counts': {'regression': 1}, 'direct_fact_regression_count': 1, 'family_regression_count': 6, 'contract_regression_count': 1, 'predicate_loss_count': 22, 'predicate_loss_regression_count': 1}`

| Fixture | Gate | Direct facts | Ratio | Family regressions | Contract regressions | Lost predicates |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `ridgeline_fire` | `regression` | 242 -> 45 | 0.186 | 6 | 1 | 22 |

## Regressions

### `ridgeline_fire`
- Direct fact count regressed: `242` -> `45`.
- Predicate preservation failed: `22` lost predicates.
- Family `financial_baseline_surface`: `pass` -> `partial`.
- Family `identity_role_surface`: `pass` -> `partial`.
- Family `measure_count_surface`: `pass` -> `partial`.
- Family `participant_statement_surface`: `pass` -> `partial`.
- Family `rule_policy_surface`: `pass` -> `partial`.
- Family `source_authority_surface`: `pass` -> `partial`.
- Contract `participant_statement_status_contract`: `pass` -> `partial`.
- Lost predicates: `authority_exclusion`, `compliance_status`, `corrected_event_id`, `corrected_value`, `correction_id`, `event_actor`, `event_id`, `event_joint_authorization`, `event_location`, `event_timestamp`, `event_type`, `fact_source`, `original_value`, `rule_authority`, `rule_condition`, `rule_deadline_minutes`, `rule_id`, `rule_prohibition`, `rule_text`, `statement_language`, `statement_original`, `statement_translation`.
