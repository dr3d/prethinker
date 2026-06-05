# Pending External Work Order Audit

This report validates proposal-declared and standalone tmp work-order zip structure plus entry-name and template-content leak policy only.
It blocks pending packets that include filled oracle files, judged-QA manifests, model outputs, compile/run artifacts, or literal fact examples inside oracle templates.
It may read packet-control/template files, but it does not read source prose or decide expected/forbidden facts.

- Proposals scanned: `4`
- Pending work orders: `4`
- Standalone tmp work orders: `4`
- Blocking errors: `0`
- Warnings: `1`
- Status: `pass`

| Source | Proposal | Kind | Path | Fixtures | Entries | Errors | Warnings |
| --- | --- | --- | --- | --- | ---: | --- | --- |
| `tmp_zip` | `osha_fta_total_penalty_blind_review_work_order_20260605` | `standalone_external_work_order` | `tmp/osha_fta_total_penalty_blind_review_work_order_20260605.zip` | `.` | 7 | `[]` | `['candidate_fact_focus_review_not_full_blind:candidate_fact.pl']` |
| `tmp_zip` | `sec_exhibit_treatment_blind_review_work_order_20260605` | `standalone_external_work_order` | `tmp/sec_exhibit_treatment_blind_review_work_order_20260605.zip` | `.` | 6 | `[]` | `[]` |
| `tmp_zip` | `state_ag_t003_transfer_micro_work_order_20260604` | `standalone_external_work_order` | `tmp/state_ag_t003_transfer_micro_work_order_20260604.zip` | `.` | 8 | `[]` | `[]` |
| `tmp_zip` | `state_ag_transfer_micro_work_order_20260604` | `standalone_external_work_order` | `tmp/state_ag_transfer_micro_work_order_20260604.zip` | `.` | 8 | `[]` | `[]` |
