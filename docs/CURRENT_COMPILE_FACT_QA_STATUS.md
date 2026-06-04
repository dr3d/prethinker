# Current Compile-Fact QA Status

Generated from the current compile-fact QA manifest run and manifest source/settings audit.
This page does not read source prose, call an LLM, or judge messy human questions.

## Summary

- Status: `pass`
- Cells: `8` across `4` families
- Support>=2: `118 / 137` expected typed facts
- Per-run exact: `336 / 411` deterministic fact rows
- Prose-dependent exact rows: `0`
- Unregistered exact typed plans: `0`
- Source/provenance warnings: `2`

## By Family

| Family | Cells | Support>=2 | Per-run exact | Prose-dependent | Unregistered plans |
| --- | ---: | ---: | ---: | ---: | ---: |
| `fda_warning_letter` | 1 | 20 / 27 | 59 / 81 | 0 | 0 |
| `ntsb_investigation` | 1 | 18 / 25 | 53 / 75 | 0 | 0 |
| `osha_incident` | 2 | 30 / 35 | 80 / 105 | 0 | 0 |
| `sec_form_8k` | 4 | 50 / 50 | 144 / 150 | 0 | 0 |

## Cells

| Cell | Fixture | Support>=2 | Per-run exact | Replay gates | Source metadata |
| --- | --- | ---: | ---: | --- | --- |
| `sec_form_8k_skeleton_seed` | `sec_form_8k_skeleton_v1` | 13 / 13 | 38 / 39 | redaction `pass` / prose `0`; typed-plan `pass` / unregistered `0` | `lmstudio` `qwen/qwen3.6-35b-a3b`; temp `0.0`; top_p `1.0`; ctx `65536`; matcher `constant_slot`; manifest `missing_recovered_from_compile_json` |
| `sec_form_8k_skeleton_transfer_001` | `sec_form_8k_skeleton_transfer_001` | 13 / 13 | 38 / 39 | redaction `pass` / prose `0`; typed-plan `pass` / unregistered `0` | `lmstudio` `qwen/qwen3.6-35b-a3b`; temp `0.0`; top_p `1.0`; ctx `65536`; matcher `constant_slot`; manifest `missing_recovered_from_compile_json` |
| `sec_form_8k_skeleton_transfer_002` | `sec_form_8k_skeleton_transfer_002` | 12 / 12 | 33 / 36 | redaction `pass` / prose `0`; typed-plan `pass` / unregistered `0` | `lmstudio` `qwen/qwen3.6-35b-a3b`; temp `0.0`; top_p `1.0`; ctx `65536`; matcher `constant_slot`; manifest `present` |
| `sec_form_8k_skeleton_transfer_003` | `sec_form_8k_skeleton_transfer_003` | 12 / 12 | 35 / 36 | redaction `pass` / prose `0`; typed-plan `pass` / unregistered `0` | `lmstudio` `qwen/qwen3.6-35b-a3b`; temp `0.0`; top_p `1.0`; ctx `65536`; matcher `constant_slot`; manifest `present` |
| `ntsb_transfer_surface_001` | `ntsb_investigation_transfer_surface_001` | 18 / 25 | 53 / 75 | redaction `pass` / prose `0`; typed-plan `pass` / unregistered `0` | `lmstudio` `qwen/qwen3.6-35b-a3b`; temp `0.0`; top_p `1.0`; ctx `65536`; matcher `constant_slot`; manifest `present` |
| `fda_warning_letter_transfer_002_current_pack` | `fda_warning_letter_domain_transfer_002` | 20 / 27 | 59 / 81 | redaction `pass` / prose `0`; typed-plan `pass` / unregistered `0` | `lmstudio` `qwen/qwen3.6-35b-a3b`; temp `0.0`; top_p `1.0`; ctx `65536`; matcher `constant_slot`; manifest `present` |
| `osha_incident_seed` | `osha_incident_domain_v1` | 18 / 20 | 53 / 60 | redaction `pass` / prose `0`; typed-plan `pass` / unregistered `0` | `lmstudio` `qwen/qwen3.6-35b-a3b`; temp `0.0`; top_p `1.0`; ctx `65536`; matcher `unification`; manifest `present` |
| `osha_incident_transfer_001` | `osha_incident_transfer_001` | 12 / 15 | 27 / 45 | redaction `pass` / prose `0`; typed-plan `pass` / unregistered `0` | `lmstudio` `qwen/qwen3.6-35b-a3b`; temp `0.0`; top_p `1.0`; ctx `65536`; matcher `constant_slot`; manifest `present` |

## Source Warnings

- `sec_form_8k_skeleton_seed:missing_bundle_manifest_recovered_from_compile_json`
- `sec_form_8k_skeleton_transfer_001:missing_bundle_manifest_recovered_from_compile_json`

