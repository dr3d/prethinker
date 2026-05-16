# Guarded Answer-Detail Compile Surface Slice Rollup

| Scope | Fixtures | Questions | Exact | Partial | Miss | Exact rate | Helper rows | compile_surface_gap | hybrid_join_gap | query_surface_gap |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Baseline native stamp | 3 | 120 | 96 | 5 | 19 | 80.00% | 0 | 16 | 5 | 3 |
| Guarded detail invariant | 3 | 120 | 99 | 6 | 15 | 82.50% | 0 | 11 | 9 | 1 |

## Per Fixture

| Fixture | Baseline exact/partial/miss | Guarded exact/partial/miss | Baseline surfaces | Guarded surfaces |
| --- | --- | --- | --- | --- |
| `amended_lease_register` | 35/1/4 | 35/1/4 | `{'compile_surface_gap': 5, 'not_applicable': 35}` | `{'compile_surface_gap': 4, 'hybrid_join_gap': 1, 'not_applicable': 35}` |
| `arts_grant_panel_reconsideration` | 33/3/4 | 34/3/3 | `{'compile_surface_gap': 1, 'hybrid_join_gap': 4, 'not_applicable': 33, 'query_surface_gap': 2}` | `{'compile_surface_gap': 1, 'hybrid_join_gap': 5, 'not_applicable': 34}` |
| `school_activity_roster_reconciliation` | 28/1/11 | 30/2/8 | `{'compile_surface_gap': 10, 'hybrid_join_gap': 1, 'not_applicable': 28, 'query_surface_gap': 1}` | `{'compile_surface_gap': 6, 'hybrid_join_gap': 3, 'not_applicable': 30, 'query_surface_gap': 1}` |
