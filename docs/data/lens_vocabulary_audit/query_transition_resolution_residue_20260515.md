# Query/Transition Resolution Residue Audit

- Files: `4`
- Not-exact rows: `4`
- Classification counts: `{'assignment_scope_missing': 1, 'initial_status_not_admitted': 1, 'interval_scoped_status_flattened': 1, 'return_to_state_requires_intervening_end': 1}`
- Failure-surface counts: `{'compile_surface_gap': 2, 'hybrid_join_gap': 2}`

| Classification | Failure surface | Verdict | Query count | Utterance | Predicates |
| --- | --- | --- | ---: | --- | --- |
| `interval_scoped_status_flattened` | `compile_surface_gap` | `miss` | 4 | What status applied during the active interval? | `effective_from`, `permit_status`, `status_changed_at`, `valid_until` |
| `return_to_state_requires_intervening_end` | `hybrid_join_gap` | `miss` | 1 | When did PU-3 return to standby? | `state_start` |
| `assignment_scope_missing` | `hybrid_join_gap` | `miss` | 3 | Who was assigned to condition review? | `entity_id`, `record_assigned_to`, `record_status_phase` |
| `initial_status_not_admitted` | `compile_surface_gap` | `miss` | 6 | What was WS-12's initial status? | `docket_status`, `recorded_event`, `source_record_text_atom`, `source_record_text_atom(Line, Text) :- source_record_line(Line, 5)` |
