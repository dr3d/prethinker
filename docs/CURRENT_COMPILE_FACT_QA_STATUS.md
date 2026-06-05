# Current Compile-Fact QA Status

Generated from the current compile-fact QA manifest run and manifest source/settings audit.
This page does not read source prose, call an LLM, or judge messy human questions.

## Summary

- Status: `pass`
- Cells: `8` across `4` families
- Support>=2: `125 / 141` expected typed facts
- Per-run exact: `348 / 423` deterministic fact rows
- Unexpected same-signature facts support>=2: `0`
- Forbidden fact emissions support>=1 / support>=2: `0 / 0`
- Prose-dependent exact rows: `0`
- Unregistered exact typed plans: `0`
- Source/provenance warnings: `0`

## By Family

| Family | Cells | Support>=2 | Per-run exact | Unexpected>=2 | Forbidden | Prose-dependent | Unregistered plans |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `fda_warning_letter` | 1 | 21 / 29 | 61 / 87 | 0 | 0 / 0 | 0 | 0 |
| `ntsb_investigation` | 1 | 22 / 25 | 60 / 75 | 0 | 0 / 0 | 0 | 0 |
| `osha_incident` | 2 | 36 / 36 | 93 / 108 | 0 | 0 / 0 | 0 | 0 |
| `sec_form_8k` | 4 | 46 / 51 | 134 / 153 | 0 | 0 / 0 | 0 | 0 |

## Cells

| Cell | Fixture | Support>=2 | Per-run exact | Unexpected>=2 | Forbidden | Replay gates | Source metadata |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| `sec_form_8k_skeleton_seed` | `sec_form_8k_skeleton_v1` | 13 / 13 | 39 / 39 | 0 | 0 / 0 | redaction `pass` / prose `0`; typed-plan `pass` / unregistered `0`; artifact atom pass/pass; value pass/pass | `lmstudio` `qwen/qwen3.6-35b-a3b`; temp `0.0`; top_p `1.0`; ctx `65536`; matcher `constant_slot`; lens compiles `12`; manifest `present` |
| `sec_form_8k_skeleton_transfer_001` | `sec_form_8k_skeleton_transfer_001` | 11 / 13 | 28 / 39 | 0 | 0 / 0 | redaction `pass` / prose `0`; typed-plan `pass` / unregistered `0`; artifact atom pass/pass; value pass/pass | `lmstudio` `qwen/qwen3.6-35b-a3b`; temp `0.0`; top_p `1.0`; ctx `65536`; matcher `constant_slot`; lens compiles `12`; manifest `present` |
| `sec_form_8k_skeleton_transfer_002` | `sec_form_8k_skeleton_transfer_002` | 11 / 12 | 32 / 36 | 0 | 0 / 0 | redaction `pass` / prose `0`; typed-plan `pass` / unregistered `0`; artifact atom pass/pass; value pass/pass | `lmstudio` `qwen/qwen3.6-35b-a3b`; temp `0.0`; top_p `1.0`; ctx `65536`; matcher `constant_slot`; lens compiles `12`; manifest `present` |
| `sec_form_8k_skeleton_transfer_003` | `sec_form_8k_skeleton_transfer_003` | 11 / 13 | 35 / 39 | 0 | 0 / 0 | redaction `pass` / prose `0`; typed-plan `pass` / unregistered `0`; artifact atom pass/pass; value pass/pass | `lmstudio` `qwen/qwen3.6-35b-a3b`; temp `0.0`; top_p `1.0`; ctx `65536`; matcher `constant_slot`; lens compiles `12`; manifest `present` |
| `ntsb_transfer_surface_001` | `ntsb_investigation_transfer_surface_001` | 22 / 25 | 60 / 75 | 0 | 0 / 0 | redaction `pass` / prose `0`; typed-plan `pass` / unregistered `0`; artifact atom pass/pass; value pass/pass | `lmstudio` `qwen/qwen3.6-35b-a3b`; temp `0.0`; top_p `1.0`; ctx `65536`; matcher `constant_slot`; lens compiles `18`; manifest `present` |
| `fda_warning_letter_transfer_002_current_pack` | `fda_warning_letter_domain_transfer_002` | 21 / 29 | 61 / 87 | 0 | 0 / 0 | redaction `pass` / prose `0`; typed-plan `pass` / unregistered `0`; artifact atom pass/pass; value pass/pass | `lmstudio` `qwen/qwen3.6-35b-a3b`; temp `0.0`; top_p `1.0`; ctx `65536`; matcher `constant_slot`; lens compiles `30`; manifest `present` |
| `osha_incident_seed` | `osha_incident_domain_v1` | 21 / 21 | 57 / 63 | 0 | 0 / 0 | redaction `pass` / prose `0`; typed-plan `pass` / unregistered `0`; artifact atom pass/pass; value pass/pass | `lmstudio` `qwen/qwen3.6-35b-a3b`; temp `0.0`; top_p `1.0`; ctx `65536`; matcher `constant_slot`; lens compiles `12`; manifest `present` |
| `osha_incident_transfer_001` | `osha_incident_transfer_001` | 15 / 15 | 36 / 45 | 0 | 0 / 0 | redaction `pass` / prose `0`; typed-plan `pass` / unregistered `0`; artifact atom pass/pass; value pass/pass | `lmstudio` `qwen/qwen3.6-35b-a3b`; temp `0.0`; top_p `1.0`; ctx `65536`; matcher `constant_slot`; lens compiles `12`; manifest `present` |

## Cell Notes

| Cell | Note |
| --- | --- |
| `sec_form_8k_skeleton_seed` | SEC Form 8-K skeleton seed micro, rerun after exhibit/item treatment axis contract clarification. |
| `sec_form_8k_skeleton_transfer_001` | SEC Form 8-K skeleton transfer 001, current repaired breadth bundle against the axis-clean oracle. |
| `sec_form_8k_skeleton_transfer_002` | SEC Form 8-K skeleton transfer 002, current repaired breadth bundle against the axis-clean oracle. |
| `sec_form_8k_skeleton_transfer_003` | SEC Form 8-K/A skeleton transfer 003, current axis-clean item/exhibit/treatment repair rerun. |
| `ntsb_transfer_surface_001` | NTSB first unlike transfer, rerun with scoped injury-count partition contract. |
| `fda_warning_letter_transfer_002_current_pack` | FDA warning-letter transfer 002 current-pack boundary bundle, rerun after explicit adulteration-basis contract tightening. |
| `osha_incident_seed` | OSHA accident/inspection seed skeleton/table probe, rerun with current related-activity blank-flag contract. |
| `osha_incident_transfer_001` | OSHA accident/inspection first unlike skeleton/table transfer, with blank Safety/Health related-activity flags constrained to not_stated. |

