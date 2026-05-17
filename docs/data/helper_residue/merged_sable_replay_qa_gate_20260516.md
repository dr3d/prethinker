# QA Run Comparison

- Schema: `qa_run_comparison_v1`
- Summary: `{'fixture_count': 1, 'promotable_count': 0, 'regression_count': 1}`

| Fixture | Status | Exact | Partial | Miss | Delta |
| --- | --- | ---: | ---: | ---: | --- |
| `sable_creek_budget` | `regression` | 34 -> 33 | 2 -> 3 | 3 -> 4 | `{'exact': -1, 'partial': 1, 'miss': 1}` |
