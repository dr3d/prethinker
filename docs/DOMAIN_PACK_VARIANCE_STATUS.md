# Domain Pack Variance Status

Generated from retained domain-lens bundle manifests and typed summary reports.
This report does not read source prose, QA questions, judge output, or oracle answers.

## Summary

- Status: `pass`
- Groups: `4`
- Roots: `9`
- Warnings: `5`

Warnings:
- `stability_r1:value_domain_report_not_recorded`
- `item_treatment_filing_id_r2:value_domain_report_not_recorded`
- `gemma4_q4_r1:value_domain_report_not_recorded`
- `qwen27b_q4_r1:value_domain_report_not_recorded`
- `related_activity_blank_flag_r1:value_domain_report_not_recorded`

## Groups

| Group | Fixture | Roots | Support Band | Forbidden Total | Unexpected Band | Status |
| --- | --- | ---: | --- | ---: | --- | --- |
| `sec_t003_qwen_moe_repaired_schema` | `sec_form_8k_skeleton_transfer_003` | 4 | `11-13/13` | 0 | `0-2` | `pass` |
| `sec_t003_dense_compile_substitution_controls` | `sec_form_8k_skeleton_transfer_003` | 2 | `10/12` | 0 | `3-6` | `pass` |
| `osha_transfer001_qwen_moe_same_condition` | `osha_incident_transfer_001` | 2 | `15/15` | 0 | `3` | `pass` |
| `sec_t001_current_mainline_retest_negative` | `sec_form_8k_skeleton_transfer_001` | 1 | `5/13` | 0 | `15` | `pass` |

## SEC transfer_003 repaired-schema local Qwen MoE band

- Group: `sec_t003_qwen_moe_repaired_schema`
- Fixture: `sec_form_8k_skeleton_transfer_003`
- Read: Use as an 11-13/13 same-condition band. Do not promote a favorable 13/13 draw as a fixed score.
- Support band: `11-13/13`
- Supported forbidden total: `0`
- Unexpected band: `0-2`
- Status: `pass`

| Root | Role | Score | Per-Run Exact | Forbidden | Unexpected | Gates | Model / Settings | Reconcile |
| --- | --- | --- | --- | ---: | ---: | --- | --- | --- |
| `stability_r1` | pre-registered stability rerun before later omission guard | `12/13` | `36/39` | 0 | 2 | atom `0`; lens `0`; value `not_recorded` | `lmstudio` `qwen/qwen3.6-35b-a3b`; temp `0.0`; top_p `1.0`; ctx `65536`; matcher `constant_slot` | `not_recorded` |
| `item_treatment_filing_id_r2` | item-treatment filing-id seam check | `11/13` | `35/39` | 0 | 0 | atom `0`; lens `0`; value `not_recorded` | `lmstudio` `qwen/qwen3.6-35b-a3b`; temp `0.0`; top_p `1.0`; ctx `65536`; matcher `constant_slot` | `not_recorded` |
| `axis_clean_refresh_r1` | same-local-Qwen refresh | `13/13` | `37/39` | 0 | 1 | atom `0`; lens `0`; value `pass` | `lmstudio` `qwen/qwen3.6-35b-a3b`; temp `0.0`; top_p `1.0`; ctx `65536`; matcher `constant_slot` | `not_recorded` |
| `qwen_mainline_rerun_r1` | same-day Qwen MoE mainline rerun | `13/13` | `36/39` | 0 | 0 | atom `0`; lens `0`; value `pass` | `lmstudio` `qwen/qwen3.6-35b-a3b`; temp `0.0`; top_p `1.0`; ctx `65536`; matcher `constant_slot` | `13` value-mode facts |

Roots:
- `stability_r1`: `C:\prethinker_tmp_archive\sec_stability_20260604\sec-t003-axis-stability-r1`
- `item_treatment_filing_id_r2`: `C:\prethinker_tmp_archive\sec_item_treatment_filing_id_20260604\sec8k-t003-item-treatment-filing-id-r2-20260604`
- `axis_clean_refresh_r1`: `C:\prethinker_tmp_archive\sec_t003_refresh_20260605\sec8k-t003-axis-clean-refresh-r1-20260605`
- `qwen_mainline_rerun_r1`: `C:\prethinker_tmp_archive\sec_t003_qwen_mainline_rerun_20260605\sec8k-t003-qwen-mainline-rerun-r1-20260605`

## SEC transfer_003 dense compile-substitution controls

- Group: `sec_t003_dense_compile_substitution_controls`
- Fixture: `sec_form_8k_skeleton_transfer_003`
- Read: Use as model-path robustness evidence: closed-language governance held, but recall did not reproduce the Qwen MoE favorable cell.
- Support band: `10/12`
- Supported forbidden total: `0`
- Unexpected band: `3-6`
- Status: `pass`

| Root | Role | Score | Per-Run Exact | Forbidden | Unexpected | Gates | Model / Settings | Reconcile |
| --- | --- | --- | --- | ---: | ---: | --- | --- | --- |
| `gemma4_q4_r1` | Gemma 4 12B Q4_K_M compile substitution | `10/12` | `29/36` | 0 | 6 | atom `0`; lens `0`; value `not_recorded` | `lmstudio` `google/gemma-4-12b`; temp `0.0`; top_p `1.0`; ctx `65536`; matcher `constant_slot` | `not_recorded` |
| `qwen27b_q4_r1` | Qwen 3.6 27B Q4_K_M dense same-family compile substitution | `10/12` | `30/36` | 0 | 3 | atom `0`; lens `0`; value `not_recorded` | `lmstudio` `qwen/qwen3.6-27b`; temp `0.0`; top_p `1.0`; ctx `65536`; matcher `constant_slot` | `not_recorded` |

Roots:
- `gemma4_q4_r1`: `C:\prethinker_tmp_archive\model_variance_prereg_20260604\sec_compile_substitution_20260604\compile_substitution_sec\sec8k-t003-gemma4-q4-temp0-r1`
- `qwen27b_q4_r1`: `C:\prethinker_tmp_archive\model_variance_prereg_20260604\sec_compile_substitution_20260604\qwen27b_compile_substitution_sec\sec8k-t003-qwen27b-q4-temp0-r1`

## OSHA transfer_001 local Qwen MoE same-condition band

- Group: `osha_transfer001_qwen_moe_same_condition`
- Fixture: `osha_incident_transfer_001`
- Read: Use as a 15/15 same-condition OSHA transfer band with visible per-run jitter; do not infer long-table or mixed-section transfer from this bounded cell.
- Support band: `15/15`
- Supported forbidden total: `0`
- Unexpected band: `3`
- Status: `pass`

| Root | Role | Score | Per-Run Exact | Forbidden | Unexpected | Gates | Model / Settings | Reconcile |
| --- | --- | --- | --- | ---: | ---: | --- | --- | --- |
| `related_activity_blank_flag_r1` | standing transfer_001 current-pack root after blank related-activity flag contract | `15/15` | `36/45` | 0 | 3 | atom `0`; lens `0`; value `not_recorded` | `lmstudio` `qwen/qwen3.6-35b-a3b`; temp `0.0`; top_p `1.0`; ctx `65536`; matcher `constant_slot` | `not_recorded` |
| `qwen_mainline_rerun_r1` | same-local-Qwen transfer_001 variance rerun | `15/15` | `36/45` | 0 | 3 | atom `0`; lens `0`; value `pass` | `lmstudio` `qwen/qwen3.6-35b-a3b`; temp `0.0`; top_p `1.0`; ctx `65536`; matcher `constant_slot` | `11` value-mode facts |

Roots:
- `related_activity_blank_flag_r1`: `C:\prethinker_tmp_archive\osha_related_activity_flag_contract_20260604\osha-transfer-001-related-activity-blank-flag-r1`
- `qwen_mainline_rerun_r1`: `C:\prethinker_tmp_archive\osha_transfer001_variance_probe_20260605\osha-transfer-001-variance-r1`

## SEC transfer_001 current-mainline full-bundle retest negative

- Group: `sec_t001_current_mainline_retest_negative`
- Fixture: `sec_form_8k_skeleton_transfer_001`
- Read: Use as a negative current-mainline retest: the wrapper date recovered, but registrant/exhibit axes destabilized and the older retained 11/13 root should not be treated as a stable current-pack score.
- Support band: `5/13`
- Supported forbidden total: `0`
- Unexpected band: `15`
- Status: `pass`

| Root | Role | Score | Per-Run Exact | Forbidden | Unexpected | Gates | Model / Settings | Reconcile |
| --- | --- | --- | --- | ---: | ---: | --- | --- | --- |
| `current_mainline_r1` | fresh current-mainline Qwen MoE full-bundle rerun after SEC registrant guidance | `5/13` | `18/39` | 0 | 15 | atom `0`; lens `0`; value `pass` | `lmstudio` `qwen/qwen3.6-35b-a3b`; temp `0.0`; top_p `1.0`; ctx `65536`; matcher `constant_slot` | `7` value-mode facts |

Roots:
- `current_mainline_r1`: `C:\prethinker_tmp_archive\sec_t001_current_pack_rerun_negative_20260605\sec-t001-current-pack-r1-20260605`
