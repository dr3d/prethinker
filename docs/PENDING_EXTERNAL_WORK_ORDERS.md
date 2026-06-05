# Pending External Work Order Audit

This report validates proposal-declared and standalone tmp work-order zip structure only.
It does not read source prose or decide expected/forbidden facts.

- Proposals scanned: `4`
- Pending work orders: `8`
- Standalone tmp work orders: `6`
- Blocking errors: `0`
- Warnings: `0`
- Status: `pass`

| Source | Proposal | Kind | Path | Fixtures | Entries | Errors | Warnings |
| --- | --- | --- | --- | --- | ---: | --- | --- |
| `proposal` | `procurement_gao_decision_wrapper_v1` | `source_only_expected_forbidden_oracle` | `tmp/procurement_gao_decision_wrapper_oracle_work_order_20260605.zip` | `procurement_contract_ugly_002, procurement_contract_ugly_003` | 13 | `[]` | `[]` |
| `proposal` | `puc_order_wrapper_v1` | `source_only_expected_forbidden_oracle` | `tmp/puc_order_wrapper_oracle_work_order_20260604.zip` | `puc_order_ugly_002, puc_order_ugly_003` | 13 | `[]` | `[]` |
| `tmp_zip` | `fda_response_assessment_item_blind_review_work_order_20260604` | `standalone_external_work_order` | `tmp/fda_response_assessment_item_blind_review_work_order_20260604.zip` | `fixtures/fda_warning_letter_domain_transfer_001, fixtures/fda_warning_letter_domain_transfer_002, fixtures/fda_warning_letter_domain_transfer_003` | 16 | `[]` | `[]` |
| `tmp_zip` | `fda_t002_unexpected_blind_review_work_order_20260604` | `standalone_external_work_order` | `tmp/fda_t002_unexpected_blind_review_work_order_20260604.zip` | `.` | 6 | `[]` | `[]` |
| `tmp_zip` | `osha_fta_total_penalty_blind_review_work_order_20260605` | `standalone_external_work_order` | `tmp/osha_fta_total_penalty_blind_review_work_order_20260605.zip` | `.` | 7 | `[]` | `[]` |
| `tmp_zip` | `sec_exhibit_treatment_blind_review_work_order_20260605` | `standalone_external_work_order` | `tmp/sec_exhibit_treatment_blind_review_work_order_20260605.zip` | `.` | 5 | `[]` | `[]` |
| `tmp_zip` | `state_ag_t003_transfer_micro_work_order_20260604` | `standalone_external_work_order` | `tmp/state_ag_t003_transfer_micro_work_order_20260604.zip` | `.` | 8 | `[]` | `[]` |
| `tmp_zip` | `state_ag_transfer_micro_work_order_20260604` | `standalone_external_work_order` | `tmp/state_ag_transfer_micro_work_order_20260604.zip` | `.` | 8 | `[]` | `[]` |
