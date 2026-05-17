# QA Run Comparison

- Schema: `qa_run_comparison_v1`
- Summary: `{'fixture_count': 1, 'promotable_count': 0, 'regression_count': 1}`

| Fixture | Status | Exact | Partial | Miss | Delta |
| --- | --- | ---: | ---: | ---: | --- |
| `school_activity_roster_reconciliation` | `regression` | 29 -> 26 | 1 -> 1 | 10 -> 13 | `{'exact': -3, 'partial': 0, 'miss': 3}` |
