# Guarded Answer-Detail Large Native Slice Rollup

| Scope | Fixtures | Questions | Exact | Partial | Miss | Exact rate | Helper rows | compile_surface_gap | hybrid_join_gap | query_surface_gap |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Baseline native stamp | 7 | 280 | 192 | 27 | 61 | 68.57% | 0 | 72 | 8 | 7 |
| Guarded detail invariant pass7 | 7 | 280 | 219 | 21 | 40 | 78.21% | 0 | 47 | 8 | 5 |

## Compile Gate

| Fixture | Decision | Reasons | Rough | Risk |
| --- | --- | --- | ---: | ---: |
| `dulse_ledger` | `pass` | n/a | 0.778 | 4 |
| `industrial_sensor_clock_correction` | `hold` | detail_wrapper_drift:location_backbone_missing_with_wrapper:event_description, detail_wrapper_drift:quantity_backbone_missing_with_wrapper:event_description | 0.778 | 5 |
| `larkspur_clockwork_fair` | `pass` | n/a | 0.995 | 5 |
| `ridgeline_fire` | `pass` | n/a | 0.778 | 5 |
| `sable_creek_budget` | `pass` | n/a | 0.889 | 5 |
| `school_activity_roster_reconciliation` | `pass` | n/a | 0.889 | 5 |
| `thornfield_variance` | `pass` | n/a | 1.0 | 5 |
| `tournament_borrowed_names` | `pass` | n/a | 1.0 | 4 |

## Per Fixture

| Fixture | Baseline exact/partial/miss | Guarded exact/partial/miss | Baseline surfaces | Guarded surfaces |
| --- | --- | --- | --- | --- |
| `ridgeline_fire` | 24/4/12 | 29/3/8 | `{'compile_surface_gap': 15, 'hybrid_join_gap': 1, 'not_applicable': 24}` | `{'compile_surface_gap': 9, 'not_applicable': 29, 'query_surface_gap': 2}` |
| `thornfield_variance` | 26/3/11 | 29/2/9 | `{'compile_surface_gap': 13, 'judge_uncertain': 1, 'not_applicable': 26}` | `{'compile_surface_gap': 9, 'hybrid_join_gap': 2, 'not_applicable': 29}` |
| `dulse_ledger` | 27/7/6 | 33/7/0 | `{'compile_surface_gap': 6, 'hybrid_join_gap': 4, 'not_applicable': 27, 'query_surface_gap': 3}` | `{'compile_surface_gap': 4, 'hybrid_join_gap': 1, 'not_applicable': 33, 'query_surface_gap': 2}` |
| `sable_creek_budget` | 27/5/8 | 33/3/4 | `{'compile_surface_gap': 12, 'hybrid_join_gap': 1, 'not_applicable': 27}` | `{'compile_surface_gap': 7, 'not_applicable': 33}` |
| `school_activity_roster_reconciliation` | 28/1/11 | 27/1/12 | `{'compile_surface_gap': 10, 'hybrid_join_gap': 1, 'not_applicable': 28, 'query_surface_gap': 1}` | `{'compile_surface_gap': 9, 'hybrid_join_gap': 2, 'judge_uncertain': 1, 'not_applicable': 27, 'query_surface_gap': 1}` |
| `tournament_borrowed_names` | 30/2/8 | 34/2/4 | `{'compile_surface_gap': 8, 'hybrid_join_gap': 1, 'not_applicable': 30, 'query_surface_gap': 1}` | `{'compile_surface_gap': 4, 'hybrid_join_gap': 2, 'not_applicable': 34}` |
| `larkspur_clockwork_fair` | 30/5/5 | 34/3/3 | `{'compile_surface_gap': 8, 'not_applicable': 30, 'query_surface_gap': 2}` | `{'compile_surface_gap': 5, 'hybrid_join_gap': 1, 'not_applicable': 34}` |
