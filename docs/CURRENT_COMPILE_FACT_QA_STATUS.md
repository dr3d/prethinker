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
- Unsupported expected facts support<2: `16`
- Unsupported split support 0 / support 1: `10 / 6`

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

## Unsupported Expected Facts

These rows are the current coverage boundary: expected typed facts
with exact support below the claim threshold of 2. They are
diagnostic planning data, not permission to repair rows one by one.
Residue kinds are derived from deterministic matcher details on
non-exact runs only; they do not change support scores.

### By Carrier

| Family | Carrier | Unsupported | Support 0 | Support 1 | Zero Yield | Zero-Yield Pattern | Same-Sig Drift | No Primary | Other | Drift Slots | Cells |
| --- | --- | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: | --- | --- |
| `fda_warning_letter` | `fda_violation_detail/5` | 5 | 5 | 0 | 0 |  | 2 | 3 | 0 | `detail_value` x2 | `fda_warning_letter_transfer_002_current_pack` |
| `fda_warning_letter` | `fda_correspondence_party/5` | 2 | 2 | 0 | 0 |  | 0 | 2 | 0 |  | `fda_warning_letter_transfer_002_current_pack` |
| `fda_warning_letter` | `fda_violation/5` | 1 | 1 | 0 | 0 |  | 0 | 1 | 0 |  | `fda_warning_letter_transfer_002_current_pack` |
| `ntsb_investigation` | `ntsb_finding/5` | 2 | 0 | 2 | 2 | `unstable_zero_yield` x2 | 0 | 0 | 0 |  | `ntsb_transfer_surface_001` |
| `ntsb_investigation` | `ntsb_timeline_event/6` | 1 | 0 | 1 | 0 |  | 1 | 0 | 0 | `sequence_role` x1 | `ntsb_transfer_surface_001` |
| `sec_form_8k` | `sec_registrant_identifier/5` | 3 | 1 | 2 | 0 |  | 3 | 0 | 0 | `identifier_value` x3, `identifier_kind` x2 | `sec_form_8k_skeleton_transfer_001`, `sec_form_8k_skeleton_transfer_002`, `sec_form_8k_skeleton_transfer_003` |
| `sec_form_8k` | `sec_filing/6` | 1 | 1 | 0 | 1 | `persistent_zero_yield` x1 | 0 | 0 | 0 |  | `sec_form_8k_skeleton_transfer_001` |
| `sec_form_8k` | `sec_filing_item_treatment/4` | 1 | 0 | 1 | 1 | `unstable_zero_yield` x1 | 0 | 0 | 0 |  | `sec_form_8k_skeleton_transfer_003` |

### Rows

| Cell | Fixture | Carrier | Support | Residue | Drift Slots | Verdicts | Expected Fact | Non-Exact Emissions |
| --- | --- | --- | ---: | --- | --- | --- | --- | --- |
| `sec_form_8k_skeleton_transfer_001` | `sec_form_8k_skeleton_transfer_001` | `sec_filing/6` | 0 | `persistent_zero_yield` (0/4; candidates 0) |  | run1: miss, run2: miss, run3: miss | `sec_filing(Filing, form_8_k, current_report, v_2025_12_23, not_stated, SrcFiling).` | `` |
| `sec_form_8k_skeleton_transfer_001` | `sec_form_8k_skeleton_transfer_001` | `sec_registrant_identifier/5` | 0 | `same_signature_drift` (1/3; candidates 4) | `identifier_kind`, `identifier_value` | run1: miss, run2: partial, run3: partial | `sec_registrant_identifier(Filing, servicenow_inc, telephone, phone_408_501_8550, SrcPhone).` | `sec_registrant_identifier(filing_sec_8k_servicenow_20251223, servicenow_inc, commission_file_number, file_001_35580, sec_material_event_ugly_003).` |
| `sec_form_8k_skeleton_transfer_002` | `sec_form_8k_skeleton_transfer_002` | `sec_registrant_identifier/5` | 1 | `same_signature_drift` (2/3; candidates 5) | `identifier_value` | run1: exact, run2: partial, run3: partial | `sec_registrant_identifier(Filing, driven_brands_holdings_inc, commission_file_number, file_139898, SrcFileNumberCover).` | `sec_registrant_identifier(filing_sec_8k_001, driven_brands_holdings_inc, commission_file_number, file_001_39898, sec_material_event_ugly_007).; sec_registrant_identifier(filing_sec_8k_20260225, driven_brands_holdings_inc, commission_file_number, file_001_39898, sec_material_event_ugly_007).` |
| `sec_form_8k_skeleton_transfer_003` | `sec_form_8k_skeleton_transfer_003` | `sec_filing_item_treatment/4` | 1 | `unstable_zero_yield` (0/2; candidates 0) |  | run1: exact, run2: miss, run3: miss | `sec_filing_item_treatment(Filing, item_2_02, furnished, SrcItem202).` | `` |
| `sec_form_8k_skeleton_transfer_003` | `sec_form_8k_skeleton_transfer_003` | `sec_registrant_identifier/5` | 1 | `same_signature_drift` (1/3; candidates 4) | `identifier_kind`, `identifier_value` | run1: partial, run2: exact, run3: partial | `sec_registrant_identifier(Filing, blackstone_inc, telephone, phone_212_583_5000, SrcPhone).` | `sec_registrant_identifier(filing_sec_8ka_blackstone_20251023, blackstone_inc, commission_file_number, file_001_33551, sec_material_event_ugly_004).; sec_registrant_identifier(sec_filing_8ka_blackstone_20251023, blackstone_inc, commission_file_number, file_001_33551, sec_8ka_blackstone_20251023_amend1).` |
| `ntsb_transfer_surface_001` | `ntsb_investigation_transfer_surface_001` | `ntsb_finding/5` | 1 | `unstable_zero_yield` (0/1; candidates 0) |  | run1: exact, run2: miss, run3: miss | `ntsb_finding(Occurrence, CauseFinding, probable_cause, FindingValue, SrcCause).` | `` |
| `ntsb_transfer_surface_001` | `ntsb_investigation_transfer_surface_001` | `ntsb_finding/5` | 1 | `unstable_zero_yield` (0/1; candidates 0) |  | run1: exact, run2: miss, run3: miss | `ntsb_finding(Occurrence, FactorFinding, contributing_factor, FindingValue, SrcFactor).` | `` |
| `ntsb_transfer_surface_001` | `ntsb_investigation_transfer_surface_001` | `ntsb_timeline_event/6` | 1 | `same_signature_drift` (2/3; candidates 8) | `sequence_role` | run1: miss, run2: partial, run3: exact | `ntsb_timeline_event(Occurrence, Event911, distress_call, t_2023_09_29_2043_cdt, start, Src911).` | `ntsb_timeline_event(occ_hir2506, ev_dispatch, distress_call, t_2023_09_29_2043_cdt, intermediate, ntsb_surface_ugly_001).` |
| `fda_warning_letter_transfer_002_current_pack` | `fda_warning_letter_domain_transfer_002` | `fda_correspondence_party/5` | 0 | `same_signature_no_primary` (0/2; candidates 2) |  | run1: miss, run2: miss, run3: miss | `fda_correspondence_party(Letter, Recipient, recipient, rechon_life_science_ab, SrcRecipient).` | `` |
| `fda_warning_letter_transfer_002_current_pack` | `fda_warning_letter_domain_transfer_002` | `fda_correspondence_party/5` | 0 | `same_signature_no_primary` (0/2; candidates 2) |  | run1: miss, run2: miss, run3: miss | `fda_correspondence_party(Letter, ResponsibleOfficial, responsible_official, roland_holmqvist, SrcResponsibleOfficial).` | `` |
| `fda_warning_letter_transfer_002_current_pack` | `fda_warning_letter_domain_transfer_002` | `fda_violation/5` | 0 | `same_signature_no_primary` (0/2; candidates 3) |  | run1: miss, run2: miss, run3: miss | `fda_violation(Viol3, Letter, violation_3, aseptic_processing, SrcViol3).` | `` |
| `fda_warning_letter_transfer_002_current_pack` | `fda_warning_letter_domain_transfer_002` | `fda_violation_detail/5` | 0 | `same_signature_no_primary` (0/2; candidates 7) |  | run1: miss, run2: miss, run3: miss | `fda_violation_detail(Viol1, response_status, inadequate, ResponseRole1, SrcDetail2).` | `` |
| `fda_warning_letter_transfer_002_current_pack` | `fda_warning_letter_domain_transfer_002` | `fda_violation_detail/5` | 0 | `same_signature_no_primary` (0/2; candidates 7) |  | run1: miss, run2: miss, run3: miss | `fda_violation_detail(Viol2, response_status, inadequate, ResponseRole2, SrcDetail4).` | `` |
| `fda_warning_letter_transfer_002_current_pack` | `fda_warning_letter_domain_transfer_002` | `fda_violation_detail/5` | 0 | `same_signature_drift` (2/3; candidates 7) | `detail_value` | run1: partial, run2: partial, run3: partial | `fda_violation_detail(Viol3, procedure_scope, decontamination_effectiveness_validation, violation_scope, SrcDetail5).` | `fda_violation_detail(violation_1, procedure_scope, sop_0870_3_0, violation_scope, direct).` |
| `fda_warning_letter_transfer_002_current_pack` | `fda_warning_letter_domain_transfer_002` | `fda_violation_detail/5` | 0 | `same_signature_no_primary` (0/3; candidates 7) |  | run1: miss, run2: miss, run3: miss | `fda_violation_detail(Viol4, process_area, iso_7, violation_scope, SrcDetail6).` | `` |
| `fda_warning_letter_transfer_002_current_pack` | `fda_warning_letter_domain_transfer_002` | `fda_violation_detail/5` | 0 | `same_signature_drift` (4/5; candidates 7) | `detail_value` | run1: partial, run2: partial, run3: partial | `fda_violation_detail(violation_4, observation_subject, peeling_paint_ceiling, violation_scope, direct).` | `fda_violation_detail(violation_4, observation_subject, peeling_paint_and_rust, violation_scope, direct).; fda_violation_detail(violation_4, observation_subject, peeling_paint_bubbled_paint_rust, violation_scope, direct).; fda_violation_detail(violation_4, observation_subject, peeling_paint_on_ceiling, violation_scope, direct).` |

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

