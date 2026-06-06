# Domain Pack Variance Status

Generated from retained domain-lens bundle manifests and typed summary reports.
This report does not read source prose, QA questions, judge output, or oracle answers.

## Summary

- Status: `pass`
- Groups: `9`
- Roots: `16`
- Warnings: `0`

## Groups

| Group | Fixture | Roots | Support Band | Forbidden Total | Unexpected Band | Status |
| --- | --- | ---: | --- | ---: | --- | --- |
| `sec_seed_qwen_moe_same_condition` | `sec_form_8k_skeleton_v1` | 1 | `13/13` | 0 | `5` | `pass` |
| `sec_t003_qwen_moe_repaired_schema` | `sec_form_8k_skeleton_transfer_003` | 5 | `11-13/13` | 0 | `0-2` | `pass` |
| `sec_t003_dense_compile_substitution_controls` | `sec_form_8k_skeleton_transfer_003` | 2 | `10/12` | 0 | `3-6` | `pass` |
| `osha_transfer001_qwen_moe_same_condition` | `osha_incident_transfer_001` | 2 | `15/15` | 0 | `3` | `pass` |
| `osha_seed_qwen_moe_same_condition` | `osha_incident_domain_v1` | 1 | `21/21` | 0 | `0` | `pass` |
| `fda_transfer002_qwen_moe_same_condition_negative` | `fda_warning_letter_domain_transfer_002` | 1 | `11/29` | 0 | `33` | `pass` |
| `sec_t001_current_mainline_retest_negative` | `sec_form_8k_skeleton_transfer_001` | 1 | `5/13` | 0 | `15` | `pass` |
| `sec_t002_current_mainline_retest` | `sec_form_8k_skeleton_transfer_002` | 1 | `11/12` | 0 | `2` | `pass` |
| `ntsb_transfer001_qwen_moe_same_condition` | `ntsb_investigation_transfer_surface_001` | 2 | `22/25` | 0 | `16` | `pass` |

## SEC seed local Qwen MoE same-condition retest

- Group: `sec_seed_qwen_moe_same_condition`
- Fixture: `sec_form_8k_skeleton_v1`
- Read: Use as the current standing SEC seed cell: the fresh current-mainline retest preserves 13/13 support with clean governance, while singleton item-treatment rows remain precision noise rather than promoted support.
- Support band: `13/13`
- Supported forbidden total: `0`
- Unexpected band: `5`
- Status: `pass`

| Root | Role | Score | Per-Run Exact | Forbidden | Unexpected | Gates | Model / Settings | Reconcile |
| --- | --- | --- | --- | ---: | ---: | --- | --- | --- |
| `current_mainline_r1` | same-local-Qwen SEC seed current-pack variance rerun | `13/13` | `39/39` | 0 | 5 | atom `0`; lens `0`; value `pass` | `lmstudio` `qwen/qwen3.6-35b-a3b`; temp `0.0`; top_p `1.0`; ctx `65536`; matcher `constant_slot` | `15` value-mode facts |

Roots:
- `current_mainline_r1`: `C:\prethinker_tmp_archive\sec_seed_current_pack_rerun_20260605\sec-seed-current-pack-r1-20260605`

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
| `stability_r1` | pre-registered stability rerun before later omission guard | `12/13` | `36/39` | 0 | 2 | atom `0`; lens `0`; value `pass` | `lmstudio` `qwen/qwen3.6-35b-a3b`; temp `0.0`; top_p `1.0`; ctx `65536`; matcher `constant_slot` | `13` value-mode facts |
| `item_treatment_filing_id_r2` | item-treatment filing-id seam check | `11/13` | `35/39` | 0 | 0 | atom `0`; lens `0`; value `pass` | `lmstudio` `qwen/qwen3.6-35b-a3b`; temp `0.0`; top_p `1.0`; ctx `65536`; matcher `constant_slot` | `11` value-mode facts |
| `axis_clean_refresh_r1` | same-local-Qwen refresh | `13/13` | `37/39` | 0 | 1 | atom `0`; lens `0`; value `pass` | `lmstudio` `qwen/qwen3.6-35b-a3b`; temp `0.0`; top_p `1.0`; ctx `65536`; matcher `constant_slot` | `13` value-mode facts |
| `qwen_mainline_rerun_r1` | same-day Qwen MoE mainline rerun | `13/13` | `36/39` | 0 | 0 | atom `0`; lens `0`; value `pass` | `lmstudio` `qwen/qwen3.6-35b-a3b`; temp `0.0`; top_p `1.0`; ctx `65536`; matcher `constant_slot` | `13` value-mode facts |
| `fenced_boundary_r8` | same-local-Qwen fenced boundary rerun; 12/13 support, 0 supported forbidden, 0 unexpected | `12/13` | `36/39` | 0 | 0 | atom `0`; lens `0`; value `pass` | `lmstudio` `qwen/qwen3.6-35b-a3b`; temp `0.0`; top_p `1.0`; ctx `65536`; matcher `constant_slot` | `12` value-mode facts |

Roots:
- `stability_r1`: `C:\prethinker_tmp_archive\sec_stability_20260604\sec-t003-axis-stability-r1`
- `item_treatment_filing_id_r2`: `C:\prethinker_tmp_archive\sec_item_treatment_filing_id_20260604\sec8k-t003-item-treatment-filing-id-r2-20260604`
- `axis_clean_refresh_r1`: `C:\prethinker_tmp_archive\sec_t003_refresh_20260605\sec8k-t003-axis-clean-refresh-r1-20260605`
- `qwen_mainline_rerun_r1`: `C:\prethinker_tmp_archive\sec_t003_qwen_mainline_rerun_20260605\sec8k-t003-qwen-mainline-rerun-r1-20260605`
- `fenced_boundary_r8`: `C:\prethinker_tmp_archive\sec_t003_r8_20260605\sec-t003-r8`

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
| `gemma4_q4_r1` | Gemma 4 12B Q4_K_M compile substitution | `10/12` | `29/36` | 0 | 6 | atom `0`; lens `0`; value `pass` | `lmstudio` `google/gemma-4-12b`; temp `0.0`; top_p `1.0`; ctx `65536`; matcher `constant_slot` | `12` value-mode facts |
| `qwen27b_q4_r1` | Qwen 3.6 27B Q4_K_M dense same-family compile substitution | `10/12` | `30/36` | 0 | 3 | atom `0`; lens `0`; value `pass` | `lmstudio` `qwen/qwen3.6-27b`; temp `0.0`; top_p `1.0`; ctx `65536`; matcher `constant_slot` | `13` value-mode facts |

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
| `related_activity_blank_flag_r1` | standing transfer_001 current-pack root after blank related-activity flag contract | `15/15` | `36/45` | 0 | 3 | atom `0`; lens `0`; value `pass` | `lmstudio` `qwen/qwen3.6-35b-a3b`; temp `0.0`; top_p `1.0`; ctx `65536`; matcher `constant_slot` | `11` value-mode facts |
| `qwen_mainline_rerun_r1` | same-local-Qwen transfer_001 variance rerun | `15/15` | `36/45` | 0 | 3 | atom `0`; lens `0`; value `pass` | `lmstudio` `qwen/qwen3.6-35b-a3b`; temp `0.0`; top_p `1.0`; ctx `65536`; matcher `constant_slot` | `11` value-mode facts |

Roots:
- `related_activity_blank_flag_r1`: `C:\prethinker_tmp_archive\osha_related_activity_flag_contract_20260604\osha-transfer-001-related-activity-blank-flag-r1`
- `qwen_mainline_rerun_r1`: `C:\prethinker_tmp_archive\osha_transfer001_variance_probe_20260605\osha-transfer-001-variance-r1`

## OSHA seed local Qwen MoE same-condition retest

- Group: `osha_seed_qwen_moe_same_condition`
- Fixture: `osha_incident_domain_v1`
- Read: Use as the current standing OSHA seed cell: the fresh current-mainline retest preserves 21/21 support with clean governance, while run1 still shows accident-lane zero-yield jitter before support>=2 reconciliation.
- Support band: `21/21`
- Supported forbidden total: `0`
- Unexpected band: `0`
- Status: `pass`

| Root | Role | Score | Per-Run Exact | Forbidden | Unexpected | Gates | Model / Settings | Reconcile |
| --- | --- | --- | --- | ---: | ---: | --- | --- | --- |
| `current_mainline_r1` | same-local-Qwen OSHA seed current-pack variance rerun | `21/21` | `57/63` | 0 | 0 | atom `0`; lens `0`; value `pass` | `lmstudio` `qwen/qwen3.6-35b-a3b`; temp `0.0`; top_p `1.0`; ctx `65536`; matcher `constant_slot` | `15` value-mode facts |

Roots:
- `current_mainline_r1`: `C:\prethinker_tmp_archive\osha_seed_current_pack_rerun_20260605\osha-seed-current-pack-r1-20260605`

## FDA transfer_002 current-pack local Qwen MoE retest negative

- Group: `fda_transfer002_qwen_moe_same_condition_negative`
- Fixture: `fda_warning_letter_domain_transfer_002`
- Read: Use as a current-pack negative retest: governance stayed clean, but the same-condition N=3 rerun supported only 11/29 expected facts at support>=2. Do not retain earlier higher transfer_002 numbers as current-pack recall claims.
- Support band: `11/29`
- Supported forbidden total: `0`
- Unexpected band: `33`
- Status: `pass`

| Root | Role | Score | Per-Run Exact | Forbidden | Unexpected | Gates | Model / Settings | Reconcile |
| --- | --- | --- | --- | ---: | ---: | --- | --- | --- |
| `qwen_mainline_rerun_r1` | same-local-Qwen transfer_002 current-pack variance rerun | `11/29` | `33/87` | 0 | 33 | atom `0`; lens `0`; value `pass` | `lmstudio` `qwen/qwen3.6-35b-a3b`; temp `0.0`; top_p `1.0`; ctx `65536`; matcher `constant_slot` | `45` value-mode facts |

Roots:
- `qwen_mainline_rerun_r1`: `C:\prethinker_tmp_archive\fda_t002_variance_probe_20260605\fda-t002-variance-r1-20260605`

## SEC transfer_001 current-mainline full-bundle retest negative

- Group: `sec_t001_current_mainline_retest_negative`
- Fixture: `sec_form_8k_skeleton_transfer_001`
- Read: Use as a pre-source-review negative current-mainline retest: the wrapper date recovered, but registrant/exhibit axes destabilized and the older retained 11/13 root should not be treated as a stable current-pack score. The imported source-only review and source-scope filing-id guard now tighten the current standing manifest cell to 3/13 with source-reviewed registrant alias blockers; do not use this 5/13 root as the current score.
- Support band: `5/13`
- Supported forbidden total: `0`
- Unexpected band: `15`
- Status: `pass`

| Root | Role | Score | Per-Run Exact | Forbidden | Unexpected | Gates | Model / Settings | Reconcile |
| --- | --- | --- | --- | ---: | ---: | --- | --- | --- |
| `current_mainline_r1` | fresh current-mainline Qwen MoE full-bundle rerun after SEC registrant guidance | `5/13` | `18/39` | 0 | 15 | atom `0`; lens `0`; value `pass` | `lmstudio` `qwen/qwen3.6-35b-a3b`; temp `0.0`; top_p `1.0`; ctx `65536`; matcher `constant_slot` | `7` value-mode facts |

Roots:
- `current_mainline_r1`: `C:\prethinker_tmp_archive\sec_t001_current_pack_rerun_negative_20260605\sec-t001-current-pack-r1-20260605`

## SEC transfer_002 current-mainline full-bundle retest

- Group: `sec_t002_current_mainline_retest`
- Fixture: `sec_form_8k_skeleton_transfer_002`
- Read: Use as pre-source-scope-guard variance evidence: the fresh current-mainline Qwen MoE retest preserved 11/12 support with clean governance, while duplicate commission-file value support remained the live boundary. The current standing manifest now scores this cell at 10/12 under the stricter source-scope filing-id guard.
- Support band: `11/12`
- Supported forbidden total: `0`
- Unexpected band: `2`
- Status: `pass`

| Root | Role | Score | Per-Run Exact | Forbidden | Unexpected | Gates | Model / Settings | Reconcile |
| --- | --- | --- | --- | ---: | ---: | --- | --- | --- |
| `current_mainline_r1` | fresh current-mainline Qwen MoE full-bundle rerun after SEC standing-cell demotions | `11/12` | `31/36` | 0 | 2 | atom `0`; lens `0`; value `pass` | `lmstudio` `qwen/qwen3.6-35b-a3b`; temp `0.0`; top_p `1.0`; ctx `65536`; matcher `constant_slot` | `11` value-mode facts |

Roots:
- `current_mainline_r1`: `C:\prethinker_tmp_archive\sec_t002_current_pack_rerun_20260605\sec-t002-current-pack-r1-20260605`

## NTSB transfer_001 local Qwen MoE same-condition band

- Group: `ntsb_transfer001_qwen_moe_same_condition`
- Fixture: `ntsb_investigation_transfer_surface_001`
- Read: Use as a 22/25 same-condition NTSB transfer band with clean governance and 0 supported forbidden rows; precision remains noisy because the fresh rerun produced 16 singleton unexpected same-signature facts.
- Support band: `22/25`
- Supported forbidden total: `0`
- Unexpected band: `16`
- Status: `pass`

| Root | Role | Score | Per-Run Exact | Forbidden | Unexpected | Gates | Model / Settings | Reconcile |
| --- | --- | --- | --- | ---: | ---: | --- | --- | --- |
| `scoped_injury_count_r1` | standing transfer_001 current scoped injury-count root | `22/25` | `60/75` | 0 | 16 | atom `0`; lens `0`; value `pass` | `lmstudio` `qwen/qwen3.6-35b-a3b`; temp `0.0`; top_p `1.0`; ctx `65536`; matcher `constant_slot` | `6` value-mode facts |
| `qwen_mainline_rerun_r1` | same-local-Qwen transfer_001 variance rerun | `22/25` | `60/75` | 0 | 16 | atom `0`; lens `0`; value `pass` | `lmstudio` `qwen/qwen3.6-35b-a3b`; temp `0.0`; top_p `1.0`; ctx `65536`; matcher `constant_slot` | `6` value-mode facts |

Roots:
- `scoped_injury_count_r1`: `C:\prethinker_tmp_archive\ntsb_casualty_partition_contract_20260604\ntsb-transfer-casualty-partition-r1`
- `qwen_mainline_rerun_r1`: `C:\prethinker_tmp_archive\ntsb_transfer001_variance_probe_20260605\ntsb-transfer-001-variance-r1-20260605`
