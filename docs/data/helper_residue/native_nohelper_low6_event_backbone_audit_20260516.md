# Compile Surface Invariant Audit

- Schema: `compile_surface_invariant_audit_v1`
- Compiles: `6`
- Status counts: `{'candidate_only': 3, 'ledger_only': 5, 'not_applicable': 2, 'partial': 35, 'pass': 15}`

## Fixture Summary

| Run | Fixture | Direct facts | Source-record facts | Pass | Partial | Candidate-only | Ledger-only | Fail | N/A |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `native_nohelper_story_worlds_draw1_20260516_compile` | `dulse_ledger` | 66 | 1049 | 2 | 6 | 0 | 2 | 0 | 0 |
| `native_nohelper_story_worlds_draw1_20260516_compile` | `industrial_sensor_clock_correction` | 121 | 2383 | 4 | 6 | 0 | 0 | 0 | 0 |
| `native_nohelper_story_worlds_draw1_20260516_compile` | `ridgeline_fire` | 242 | 1605 | 6 | 2 | 0 | 0 | 0 | 2 |
| `native_nohelper_story_worlds_draw1_20260516_compile` | `sable_creek_budget` | 18 | 1542 | 0 | 6 | 2 | 2 | 0 | 0 |
| `native_nohelper_story_worlds_draw1_20260516_compile` | `school_activity_roster_reconciliation` | 190 | 2217 | 1 | 8 | 1 | 0 | 0 | 0 |
| `native_nohelper_story_worlds_draw1_20260516_compile` | `thornfield_variance` | 122 | 1704 | 2 | 7 | 0 | 1 | 0 | 0 |

## Missing Or Weak Families

### `native_nohelper_story_worlds_draw1_20260516_compile` / `dulse_ledger`

- `identity_role_surface`: `partial`; missing `['registrar_or_recorder']`
- `source_addressability_surface`: `partial`; missing `['basis_coordinate', 'section_coordinate', 'title_or_heading']`
- `source_authority_surface`: `ledger_only`; missing `['source_actor_or_date', 'source_document_or_correspondence']`
- `object_device_surface`: `ledger_only`; missing `['vendor_or_model']`
- `temporal_event_surface`: `partial`; missing `['correction_or_supersession', 'timestamp_or_date']`
- `event_backbone_unit_surface`: `partial`; missing `['temporal_anchor']`
- `measure_count_surface`: `partial`; missing `['measurement_value']`
- `custody_control_surface`: `partial`; missing `['ownership_or_title']`

### `native_nohelper_story_worlds_draw1_20260516_compile` / `industrial_sensor_clock_correction`

- `identity_role_surface`: `partial`; missing `['registrar_or_recorder']`
- `source_addressability_surface`: `partial`; missing `['chronology_coordinate', 'section_coordinate', 'title_or_heading']`
- `object_device_surface`: `partial`; missing `['vendor_or_model']`
- `event_backbone_unit_surface`: `partial`; missing `['subject_or_object']`
- `measure_count_surface`: `partial`; missing `['count_or_total']`
- `custody_control_surface`: `partial`; missing `['access_or_location', 'recall_or_return']`

### `native_nohelper_story_worlds_draw1_20260516_compile` / `ridgeline_fire`

- `source_addressability_surface`: `partial`; missing `['title_or_heading']`
- `answer_detail_surface`: `partial`; missing `['detail_or_explanation']`

### `native_nohelper_story_worlds_draw1_20260516_compile` / `sable_creek_budget`

- `identity_role_surface`: `partial`; missing `['registrar_or_recorder', 'supervisor_or_authority']`
- `source_addressability_surface`: `candidate_only`; missing `['negative_inference_coordinate', 'section_coordinate', 'title_or_heading']`
- `source_authority_surface`: `partial`; missing `['authority_or_evidence_role', 'source_actor_or_date', 'source_document_or_correspondence']`
- `answer_detail_surface`: `ledger_only`; missing `['commitment_or_future_action', 'detail_or_explanation', 'negative_or_exclusion_detail']`
- `rule_policy_surface`: `candidate_only`; missing `['exception_or_exclusion', 'policy_or_rule_id', 'ratio_or_requirement']`
- `object_device_surface`: `ledger_only`; missing `['object_or_item_id']`
- `temporal_event_surface`: `partial`; missing `['correction_or_supersession', 'timestamp_or_date']`
- `event_backbone_unit_surface`: `partial`; missing `['event_identity', 'subject_or_object', 'temporal_anchor']`
- `measure_count_surface`: `partial`; missing `['count_or_total', 'ratio_or_formula', 'threshold_or_limit']`
- `custody_control_surface`: `partial`; missing `['ownership_or_title', 'recall_or_return']`

### `native_nohelper_story_worlds_draw1_20260516_compile` / `school_activity_roster_reconciliation`

- `identity_role_surface`: `partial`; missing `['registrar_or_recorder', 'supervisor_or_authority']`
- `source_addressability_surface`: `partial`; missing `['section_coordinate', 'title_or_heading']`
- `source_authority_surface`: `partial`; missing `['authority_or_evidence_role']`
- `answer_detail_surface`: `partial`; missing `['availability_or_scope', 'commitment_or_future_action']`
- `object_device_surface`: `partial`; missing `['device_or_system']`
- `temporal_event_surface`: `partial`; missing `['event_or_action', 'interval_or_window', 'timestamp_or_date']`
- `event_backbone_unit_surface`: `candidate_only`; missing `['event_identity', 'outcome_or_state', 'participant_or_system', 'subject_or_object', 'temporal_anchor']`
- `measure_count_surface`: `partial`; missing `['count_or_total', 'duration_or_hours', 'threshold_or_limit']`
- `custody_control_surface`: `partial`; missing `['recall_or_return']`

### `native_nohelper_story_worlds_draw1_20260516_compile` / `thornfield_variance`

- `source_addressability_surface`: `partial`; missing `['basis_coordinate', 'section_coordinate', 'title_or_heading']`
- `source_authority_surface`: `partial`; missing `['source_actor_or_date', 'source_document_or_correspondence']`
- `answer_detail_surface`: `partial`; missing `['availability_or_scope', 'detail_or_explanation']`
- `object_device_surface`: `partial`; missing `['vendor_or_model']`
- `temporal_event_surface`: `ledger_only`; missing `['timestamp_or_date']`
- `event_backbone_unit_surface`: `partial`; missing `['participant_or_system', 'temporal_anchor']`
- `measure_count_surface`: `partial`; missing `['duration_or_hours']`
- `custody_control_surface`: `partial`; missing `['ownership_or_title']`
