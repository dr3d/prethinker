# Operational Lifecycle Palette Audit

- Schema: `operational_lifecycle_palette_audit_v1`
- Compiles: `2`
- Class counts: `{'alias_split': 3, 'shallow_lifecycle_palette': 2, 'phase_classification_missing': 1}`
- Fixtures with findings: `2`

## Fixture Summary

| Fixture | Alias Split | Ambiguous Verb | Supersession Collapse | Phase Missing | Shallow Palette |
| --- | ---: | ---: | ---: | ---: | ---: |
| `warehouse_repair_log` | 3 | 0 | 0 | 0 | 1 |
| `water_sample_docket` | 0 | 0 | 0 | 1 | 1 |

## Findings

### `warehouse_repair_log`

- `alias_split`: `code`='s6', `variants`=['asset_s6', 'asset_scanner_s6', 's_6']
  - identity code `s6` appears as asset_s6, asset_scanner_s6, s_6
- `alias_split`: `code`='wr62', `variants`=['ticket_wr62', 'wr_62']
  - identity code `wr62` appears as ticket_wr62, wr_62
- `alias_split`: `code`='wr63', `variants`=['supersedes_wr_63', 'ticket_wr63', 'wr_63']
  - identity code `wr63` appears as supersedes_wr_63, ticket_wr63, wr_63
- `shallow_lifecycle_palette`: `source_signal_count`=5, `candidate_count`=16, `nearby_signatures`=['ticket_status/2', 'ticket_assigned_to/2', 'event_date/3', 'diagnosis_corrected/2', 'asset_status/2']
  - on_2026_03_01_shift_lead_tomas_iver_received_the_malfunction_report_and_logged_wr_62_as_pending_inspection
  - on_2026_03_03_rhea_denied_the_request_to_replace_the_scanner_because_the_power_module_had_not_been_tested

### `water_sample_docket`

- `phase_classification_missing`: `phase`='initial'
  - on_2026_04_10_field_collector_niko_shah_received_sample_b_12_and_filed_docket_ws_12_with_status_pending_lab_receipt
- `shallow_lifecycle_palette`: `source_signal_count`=6, `candidate_count`=16, `nearby_signatures`=['assigned_to/2', 'docket_status/2', 'event_on_date/3', 'test_result/3', 'advisory_status/2', 'superseded_by/2', 'final_status/2']
  - on_2026_04_10_field_collector_niko_shah_received_sample_b_12_and_filed_docket_ws_12_with_status_pending_lab_receipt
  - on_2026_04_12_the_first_test_was_denied_as_valid_because_the_vial_seal_was_loose
