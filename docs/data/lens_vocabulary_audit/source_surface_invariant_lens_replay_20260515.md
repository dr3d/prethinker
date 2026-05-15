# Compile Surface Invariant Audit

- Schema: `compile_surface_invariant_audit_v1`
- Compiles: `9`
- Status counts: `{'ledger_only': 19, 'not_applicable': 18, 'partial': 11, 'pass': 24}`

## Fixture Summary

| Run | Fixture | Direct facts | Source-record facts | Pass | Partial | Candidate-only | Ledger-only | Fail | N/A |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `lens_vocab_operational_record_status_palette_compile_20260515` | `clinic_intake_corrections` | 55 | 84 | 2 | 1 | 0 | 2 | 0 | 3 |
| `lens_vocab_operational_record_status_palette_compile_20260515` | `grant_review_queue` | 24 | 84 | 3 | 1 | 0 | 2 | 0 | 2 |
| `lens_vocab_operational_record_status_palette_compile_20260515` | `library_preservation_queue` | 27 | 81 | 2 | 1 | 0 | 2 | 0 | 3 |
| `lens_vocab_operational_record_status_palette_compile_20260515` | `permit_renewal_docket` | 29 | 85 | 3 | 2 | 0 | 1 | 0 | 2 |
| `lens_vocab_operational_record_status_palette_compile_20260515` | `warehouse_repair_log` | 16 | 85 | 2 | 1 | 0 | 2 | 0 | 3 |
| `lens_vocab_operational_record_status_palette_compile_20260515` | `water_sample_docket` | 35 | 82 | 4 | 1 | 0 | 2 | 0 | 1 |
| `lens_vocab_temporal_status_compile_20260515` | `machine_uptime_log` | 10 | 69 | 2 | 0 | 0 | 5 | 0 | 1 |
| `lens_vocab_temporal_status_compile_20260515` | `permit_expiry_notice` | 15 | 66 | 2 | 1 | 0 | 3 | 0 | 2 |
| `lens_vocab_temporal_status_compile_20260515` | `rental_window_notice` | 11 | 68 | 4 | 3 | 0 | 0 | 0 | 1 |

## Missing Or Weak Families

### `lens_vocab_operational_record_status_palette_compile_20260515` / `clinic_intake_corrections`

- `source_addressability_surface`: `ledger_only`; missing `['section_coordinate', 'title_or_heading']`
- `rule_policy_surface`: `ledger_only`; missing `['policy_or_rule_id']`
- `temporal_event_surface`: `partial`; missing `['interval_or_window']`

### `lens_vocab_operational_record_status_palette_compile_20260515` / `grant_review_queue`

- `source_addressability_surface`: `ledger_only`; missing `['section_coordinate', 'title_or_heading']`
- `source_authority_surface`: `partial`; missing `['authority_or_evidence_role']`
- `rule_policy_surface`: `ledger_only`; missing `['policy_or_rule_id']`

### `lens_vocab_operational_record_status_palette_compile_20260515` / `library_preservation_queue`

- `source_addressability_surface`: `ledger_only`; missing `['section_coordinate', 'title_or_heading']`
- `source_authority_surface`: `partial`; missing `['source_document_or_correspondence']`
- `rule_policy_surface`: `ledger_only`; missing `['policy_or_rule_id']`

### `lens_vocab_operational_record_status_palette_compile_20260515` / `permit_renewal_docket`

- `source_addressability_surface`: `partial`; missing `['title_or_heading']`
- `source_authority_surface`: `partial`; missing `['source_document_or_correspondence']`
- `rule_policy_surface`: `ledger_only`; missing `['policy_or_rule_id']`

### `lens_vocab_operational_record_status_palette_compile_20260515` / `warehouse_repair_log`

- `source_addressability_surface`: `ledger_only`; missing `['negative_inference_coordinate', 'section_coordinate', 'title_or_heading']`
- `source_authority_surface`: `partial`; missing `['source_document_or_correspondence']`
- `rule_policy_surface`: `ledger_only`; missing `['exception_or_exclusion', 'policy_or_rule_id']`

### `lens_vocab_operational_record_status_palette_compile_20260515` / `water_sample_docket`

- `source_addressability_surface`: `ledger_only`; missing `['section_coordinate', 'title_or_heading']`
- `source_authority_surface`: `partial`; missing `['source_document_or_correspondence']`
- `rule_policy_surface`: `ledger_only`; missing `['policy_or_rule_id']`

### `lens_vocab_temporal_status_compile_20260515` / `machine_uptime_log`

- `identity_role_surface`: `ledger_only`; missing `['operator_or_attendant', 'registrar_or_recorder']`
- `source_addressability_surface`: `ledger_only`; missing `['section_coordinate', 'title_or_heading']`
- `source_authority_surface`: `ledger_only`; missing `['governed_subject_or_item', 'source_document_or_correspondence']`
- `rule_policy_surface`: `ledger_only`; missing `['policy_or_rule_id']`
- `object_device_surface`: `ledger_only`; missing `['device_or_system']`

### `lens_vocab_temporal_status_compile_20260515` / `permit_expiry_notice`

- `identity_role_surface`: `ledger_only`; missing `['operator_or_attendant']`
- `source_addressability_surface`: `ledger_only`; missing `['section_coordinate', 'title_or_heading']`
- `source_authority_surface`: `partial`; missing `['source_document_or_correspondence']`
- `rule_policy_surface`: `ledger_only`; missing `['policy_or_rule_id']`

### `lens_vocab_temporal_status_compile_20260515` / `rental_window_notice`

- `source_addressability_surface`: `partial`; missing `['section_coordinate', 'title_or_heading']`
- `source_authority_surface`: `partial`; missing `['source_document_or_correspondence']`
- `rule_policy_surface`: `partial`; missing `['policy_or_rule_id']`
