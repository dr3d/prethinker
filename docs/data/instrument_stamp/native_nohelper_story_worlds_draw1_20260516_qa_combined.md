# Native No-Helper Story Worlds Draw 1 QA Combined

Generated: 2026-05-16T16:46:51.3003013Z

Mode: source-fixture QA over compile-gated native fixtures with helpers genuinely off (`--helper-companion-row-limit 0`, no cache, no legacy native helper adapters).

- Fixtures: `41`
- Questions: `1578`
- Exact / partial / miss: `1312 / 85 / 181`
- Exact rate: `0.8314`
- Helper rows: `0`
- Runtime load errors: `0`
- Write proposal rows: `0`

## Failure Surfaces

| Surface | Count |
| --- | ---: |
| `not_applicable` | 1312 |
| `compile_surface_gap` | 181 |
| `hybrid_join_gap` | 52 |
| `query_surface_gap` | 29 |
| `answer_surface_gap` | 2 |
| `judge_uncertain` | 2 |

## Lowest Exact-Rate Fixtures

| Fixture | Exact | Partial | Miss | Questions | Exact rate | Helper rows |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `ridgeline_fire` | 24 | 4 | 12 | 40 | 60% | 0 |
| `thornfield_variance` | 26 | 3 | 11 | 40 | 65% | 0 |
| `dulse_ledger` | 27 | 7 | 6 | 40 | 67.5% | 0 |
| `sable_creek_budget` | 27 | 5 | 8 | 40 | 67.5% | 0 |
| `school_activity_roster_reconciliation` | 28 | 1 | 11 | 40 | 70% | 0 |
| `avalon_grant_committee` | 29 | 4 | 7 | 40 | 72.5% | 0 |
| `larkspur_clockwork_fair` | 30 | 5 | 5 | 40 | 75% | 0 |
| `tournament_borrowed_names` | 30 | 2 | 8 | 40 | 75% | 0 |
| `heronvale_arts` | 19 | 2 | 4 | 25 | 76% | 0 |
| `fenmore_seedbank` | 19 | 1 | 5 | 25 | 76% | 0 |
| `school_trip_bus_roster_split` | 31 | 2 | 7 | 40 | 77.5% | 0 |
| `temporal_state_ledger` | 31 | 3 | 6 | 40 | 77.5% | 0 |

## Fixtures

| Fixture | Exact | Partial | Miss | Questions | Exact rate | Helper rows |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `amended_lease_register` | 35 | 1 | 4 | 40 | 87.5% | 0 |
| `arts_grant_panel_reconsideration` | 33 | 3 | 4 | 40 | 82.5% | 0 |
| `avalon_grant_committee` | 29 | 4 | 7 | 40 | 72.5% | 0 |
| `black_lantern_maze` | 34 | 3 | 3 | 40 | 85% | 0 |
| `census_reconciliation` | 32 | 1 | 7 | 40 | 80% | 0 |
| `clinic_device_recall_field_packet` | 37 | 1 | 2 | 40 | 92.5% | 0 |
| `contradictory_evidence_packet` | 36 | 2 | 2 | 40 | 90% | 0 |
| `copperfall_deadline_docket` | 32 | 3 | 5 | 40 | 80% | 0 |
| `count_composition_roster` | 37 | 1 | 2 | 40 | 92.5% | 0 |
| `deadline_cascade_docket` | 38 | 0 | 2 | 40 | 95% | 0 |
| `draft_within_draft` | 35 | 0 | 5 | 40 | 87.5% | 0 |
| `dream_library_index` | 36 | 0 | 4 | 40 | 90% | 0 |
| `dulse_ledger` | 27 | 7 | 6 | 40 | 67.5% | 0 |
| `estate_archive_access_dispute` | 33 | 3 | 4 | 40 | 82.5% | 0 |
| `fenmore_seedbank` | 19 | 1 | 5 | 25 | 76% | 0 |
| `festival_permit_maze` | 35 | 2 | 3 | 40 | 87.5% | 0 |
| `grant_exception_cap_matrix` | 35 | 0 | 5 | 40 | 87.5% | 0 |
| `greenhouse_quarantine` | 32 | 3 | 5 | 40 | 80% | 0 |
| `greywell_pipeline` | 23 | 1 | 1 | 25 | 92% | 0 |
| `harbor_collision_reports` | 38 | 2 | 0 | 40 | 95% | 0 |
| `harrowgate_witness_file` | 38 | 2 | 0 | 40 | 95% | 0 |
| `heronvale_arts` | 19 | 2 | 4 | 25 | 76% | 0 |
| `industrial_sensor_clock_correction` | 31 | 1 | 8 | 40 | 77.5% | 0 |
| `lantern_school_field_trip` | 34 | 2 | 4 | 40 | 85% | 0 |
| `larkspur_clockwork_fair` | 30 | 5 | 5 | 40 | 75% | 0 |
| `ledger_at_calders_reach` | 33 | 0 | 7 | 40 | 82.5% | 0 |
| `meridian_permit_board` | 38 | 1 | 1 | 40 | 95% | 0 |
| `municipal_tree_permit_amendment` | 37 | 2 | 1 | 40 | 92.5% | 0 |
| `museum_mislabelled_rooms` | 35 | 2 | 3 | 40 | 87.5% | 0 |
| `northbridge_authority_packet` | 38 | 2 | 0 | 40 | 95% | 0 |
| `orchard_inheritance_game` | 34 | 2 | 4 | 40 | 85% | 0 |
| `ridgeline_fire` | 24 | 4 | 12 | 40 | 60% | 0 |
| `sable_creek_budget` | 27 | 5 | 8 | 40 | 67.5% | 0 |
| `salvage_bell_dispute` | 38 | 0 | 2 | 40 | 95% | 0 |
| `school_activity_roster_reconciliation` | 28 | 1 | 11 | 40 | 70% | 0 |
| `school_trip_bus_roster_split` | 31 | 2 | 7 | 40 | 77.5% | 0 |
| `temporal_state_ledger` | 31 | 3 | 6 | 40 | 77.5% | 0 |
| `thornfield_variance` | 26 | 3 | 11 | 40 | 65% | 0 |
| `tournament_borrowed_names` | 30 | 2 | 8 | 40 | 75% | 0 |
| `university_lab_sample_chain` | 32 | 5 | 3 | 40 | 80% | 0 |
| `veridia_intake` | 22 | 1 | 0 | 23 | 95.65% | 0 |
