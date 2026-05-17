# QA Run Comparison

- Schema: `qa_run_comparison_v1`
- Summary: `{'fixture_count': 6, 'promotable_count': 5, 'regression_count': 1, 'aggregate_promotion_status': 'promotable', 'aggregate_delta': {'exact': 16, 'partial': -3, 'miss': -13}}`
- Aggregate: `{'baseline': {'exact': 166, 'partial': 22, 'miss': 52}, 'candidate': {'exact': 182, 'partial': 19, 'miss': 39}, 'delta': {'exact': 16, 'partial': -3, 'miss': -13}, 'promotion_status': 'promotable'}`

| Fixture | Status | Exact | Partial | Miss | Delta |
| --- | --- | ---: | ---: | ---: | --- |
| `dulse_ledger` | `promotable` | 28 -> 37 | 7 -> 3 | 5 -> 0 | `{'exact': 9, 'partial': -4, 'miss': -5}` |
| `industrial_sensor_clock_correction` | `regression` | 31 -> 29 | 0 -> 4 | 9 -> 7 | `{'exact': -2, 'partial': 4, 'miss': -2}` |
| `ridgeline_fire` | `promotable` | 23 -> 24 | 7 -> 6 | 10 -> 10 | `{'exact': 1, 'partial': -1, 'miss': 0}` |
| `sable_creek_budget` | `promotable` | 31 -> 33 | 3 -> 2 | 6 -> 5 | `{'exact': 2, 'partial': -1, 'miss': -1}` |
| `school_activity_roster_reconciliation` | `promotable` | 29 -> 29 | 1 -> 2 | 10 -> 9 | `{'exact': 0, 'partial': 1, 'miss': -1}` |
| `thornfield_variance` | `promotable` | 24 -> 30 | 4 -> 2 | 12 -> 8 | `{'exact': 6, 'partial': -2, 'miss': -4}` |
