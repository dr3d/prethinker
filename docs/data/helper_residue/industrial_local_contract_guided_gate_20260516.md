# Compile Surface Audit Comparison

- Schema: `compile_surface_audit_comparison_v1`
- Min direct-fact ratio: `0.85`
- Max lost predicates: `0`
- Summary: `{'fixture_count': 1, 'gate_status_counts': {'regression': 1}, 'direct_fact_regression_count': 1, 'family_regression_count': 2, 'contract_regression_count': 0, 'predicate_loss_count': 19, 'predicate_loss_regression_count': 1}`

| Fixture | Gate | Direct facts | Ratio | Family regressions | Contract regressions | Lost predicates |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `industrial_sensor_clock_correction` | `regression` | 121 -> 96 | 0.7934 | 2 | 0 | 19 |

## Regressions

### `industrial_sensor_clock_correction`
- Direct fact count regressed: `121` -> `96`.
- Predicate preservation failed: `19` lost predicates.
- Family `custody_control_surface`: `partial` -> `ledger_only`.
- Family `source_authority_surface`: `pass` -> `partial`.
- Lost predicates: `active_production_time_excludes`, `cause_status`, `drift_direction`, `event_corrected_timestamp`, `event_id`, `event_raw_timestamp`, `event_system`, `hold_interval`, `last_sync_time`, `missing_evidence`, `person_role`, `procedure_requirement`, `sensor_calibration_date`, `sensor_id`, `sensor_next_calibration_due`, `system_id`, `system_name`, `system_resolution`, `system_time_source`.
