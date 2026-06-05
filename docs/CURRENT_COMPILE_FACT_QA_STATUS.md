# Current Compile-Fact QA Status

Generated from the current compile-fact QA manifest run and manifest source/settings audit.
This page does not read source prose, call an LLM, or judge messy human questions.

## Summary

- Status: `pass`
- Cells: `8` across `4` families
- Support>=2: `123 / 139` expected typed facts
- Per-run exact: `343 / 417` deterministic fact rows
- Unexpected same-signature facts support>=2: `4`
- Prose-dependent exact rows: `0`
- Unregistered exact typed plans: `0`
- Source/provenance warnings: `0`

## By Family

| Family | Cells | Support>=2 | Per-run exact | Unexpected>=2 | Prose-dependent | Unregistered plans |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `fda_warning_letter` | 1 | 20 / 27 | 59 / 81 | 3 | 0 | 0 |
| `ntsb_investigation` | 1 | 22 / 25 | 60 / 75 | 0 | 0 | 0 |
| `osha_incident` | 2 | 36 / 36 | 93 / 108 | 0 | 0 | 0 |
| `sec_form_8k` | 4 | 45 / 51 | 131 / 153 | 1 | 0 | 0 |

## Cells

| Cell | Fixture | Support>=2 | Per-run exact | Unexpected>=2 | Replay gates | Source metadata |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `sec_form_8k_skeleton_seed` | `sec_form_8k_skeleton_v1` | 12 / 13 | 36 / 39 | 1 | redaction `pass` / prose `0`; typed-plan `pass` / unregistered `0`; artifact atom pass/pass; value pass/pass | `lmstudio` `qwen/qwen3.6-35b-a3b`; temp `0.0`; top_p `1.0`; ctx `65536`; matcher `constant_slot`; lens compiles `12`; manifest `present` |
| `sec_form_8k_skeleton_transfer_001` | `sec_form_8k_skeleton_transfer_001` | 11 / 13 | 28 / 39 | 0 | redaction `pass` / prose `0`; typed-plan `pass` / unregistered `0`; artifact atom pass/pass; value pass/pass | `lmstudio` `qwen/qwen3.6-35b-a3b`; temp `0.0`; top_p `1.0`; ctx `65536`; matcher `constant_slot`; lens compiles `12`; manifest `present` |
| `sec_form_8k_skeleton_transfer_002` | `sec_form_8k_skeleton_transfer_002` | 11 / 12 | 32 / 36 | 0 | redaction `pass` / prose `0`; typed-plan `pass` / unregistered `0`; artifact atom pass/pass; value pass/pass | `lmstudio` `qwen/qwen3.6-35b-a3b`; temp `0.0`; top_p `1.0`; ctx `65536`; matcher `constant_slot`; lens compiles `12`; manifest `present` |
| `sec_form_8k_skeleton_transfer_003` | `sec_form_8k_skeleton_transfer_003` | 11 / 13 | 35 / 39 | 0 | redaction `pass` / prose `0`; typed-plan `pass` / unregistered `0`; artifact atom pass/pass; value pass/pass | `lmstudio` `qwen/qwen3.6-35b-a3b`; temp `0.0`; top_p `1.0`; ctx `65536`; matcher `constant_slot`; lens compiles `12`; manifest `present` |
| `ntsb_transfer_surface_001` | `ntsb_investigation_transfer_surface_001` | 22 / 25 | 60 / 75 | 0 | redaction `pass` / prose `0`; typed-plan `pass` / unregistered `0`; artifact atom pass/pass; value pass/pass | `lmstudio` `qwen/qwen3.6-35b-a3b`; temp `0.0`; top_p `1.0`; ctx `65536`; matcher `constant_slot`; lens compiles `18`; manifest `present` |
| `fda_warning_letter_transfer_002_current_pack` | `fda_warning_letter_domain_transfer_002` | 20 / 27 | 59 / 81 | 3 | redaction `pass` / prose `0`; typed-plan `pass` / unregistered `0`; artifact atom pass/pass; value pass/pass | `lmstudio` `qwen/qwen3.6-35b-a3b`; temp `0.0`; top_p `1.0`; ctx `65536`; matcher `constant_slot`; lens compiles `30`; manifest `present` |
| `osha_incident_seed` | `osha_incident_domain_v1` | 21 / 21 | 57 / 63 | 0 | redaction `pass` / prose `0`; typed-plan `pass` / unregistered `0`; artifact atom pass/pass; value pass/pass | `lmstudio` `qwen/qwen3.6-35b-a3b`; temp `0.0`; top_p `1.0`; ctx `65536`; matcher `constant_slot`; lens compiles `12`; manifest `present` |
| `osha_incident_transfer_001` | `osha_incident_transfer_001` | 15 / 15 | 36 / 45 | 0 | redaction `pass` / prose `0`; typed-plan `pass` / unregistered `0`; artifact atom pass/pass; value pass/pass | `lmstudio` `qwen/qwen3.6-35b-a3b`; temp `0.0`; top_p `1.0`; ctx `65536`; matcher `constant_slot`; lens compiles `12`; manifest `present` |

## Unexpected Same-Signature Support>=2

These rows are precision-pressure diagnostics only. They are not
promoted expected facts unless an independent source-only oracle
adds them to the fixture.

| Cell | Fixture | Support | Fact |
| --- | --- | ---: | --- |
| `sec_form_8k_skeleton_seed` | `sec_form_8k_skeleton_v1` | 3 | `sec_exhibit(sec_8k_material_event_001, exhibit_10_1, agreement, incorporated_by_reference, exhibit_table_row_10_1).` |
| `fda_warning_letter_transfer_002_current_pack` | `fda_warning_letter_domain_transfer_002` | 2 | `fda_adulteration_basis(fda_warning_letter_320_25_68, adulteration_insanitary_conditions, fdca_501_a_2_a, drug_products, direct).` |
| `fda_warning_letter_transfer_002_current_pack` | `fda_warning_letter_domain_transfer_002` | 2 | `fda_violation_detail(violation_2, record_review_subject, out_of_specification_assay, violation_scope, direct).` |
| `fda_warning_letter_transfer_002_current_pack` | `fda_warning_letter_domain_transfer_002` | 2 | `fda_violation_detail(violation_4, observation_subject, peeling_paint_ceiling, violation_scope, direct).` |

## Cell Notes

| Cell | Note |
| --- | --- |
| `sec_form_8k_skeleton_seed` | SEC Form 8-K skeleton seed micro, current repaired breadth bundle against the axis-clean oracle. |
| `sec_form_8k_skeleton_transfer_001` | SEC Form 8-K skeleton transfer 001, current repaired breadth bundle against the axis-clean oracle. |
| `sec_form_8k_skeleton_transfer_002` | SEC Form 8-K skeleton transfer 002, current repaired breadth bundle against the axis-clean oracle. |
| `sec_form_8k_skeleton_transfer_003` | SEC Form 8-K/A skeleton transfer 003, current axis-clean item/exhibit/treatment repair rerun. |
| `ntsb_transfer_surface_001` | NTSB first unlike transfer, rerun with scoped injury-count partition contract. |
| `fda_warning_letter_transfer_002_current_pack` | FDA warning-letter transfer 002 current-pack boundary bundle. |
| `osha_incident_seed` | OSHA accident/inspection seed skeleton/table probe, rerun with current related-activity blank-flag contract. |
| `osha_incident_transfer_001` | OSHA accident/inspection first unlike skeleton/table transfer, with blank Safety/Health related-activity flags constrained to not_stated. |

