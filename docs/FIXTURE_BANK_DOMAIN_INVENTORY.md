# Fixture Bank Domain Inventory

Generated from retained real-world fixture metadata and closed profile selection paths.
This report does not read source prose, QA questions, oracle answers, or judge outputs.

Use this as a domain-selection map, not as evidence that a domain pack transfers.

## Summary

- Fixtures with metadata: `88`
- Metadata families: `52`
- Closed profiles: `8`
- Fixtures selected by at least one closed profile: `17`
- Fixtures not selected by a closed profile: `71`
- Unprofiled and profile-unrelated families with at least two fixtures: `4`
- QA-bearing unprofiled/profile-unrelated multi-fixture families: `1`
- Declared non-English fixtures: `0`
- Fixtures with no declared language: `60`
- LLM-authored or rewritten fixtures: `0`
- Metadata parse errors: `0`
- Status: `pass`

## Family Inventory

| Family | Fixtures | Questions | Languages | Exact-selected profiles | Related profiles | Status | Sample fixture IDs |
| --- | ---: | ---: | --- | --- | --- | --- | --- |
| `fda` | 5 | 125 | `en` | - | `fda_warning_letter_v1` | `profile_family_related` | `fda_ugly_001`, `fda_ugly_002`, `fda_ugly_003`, `fda_warning_ugly_006`, `fda_warning_ugly_007` |
| `fda_warning` | 5 | 0 | - | - | `fda_warning_letter_v1` | `profile_family_related` | `fda_warning_ugly_001`, `fda_warning_ugly_002`, `fda_warning_ugly_003`, `fda_warning_ugly_004`, `fda_warning_ugly_005` |
| `osha` | 5 | 125 | `en` | `osha_incident_v1` | `osha_incident_v1` | `selected_by_closed_profile` | `osha_ugly_001`, `osha_ugly_002`, `osha_ugly_003`, `osha_incident_ugly_006`, `osha_incident_ugly_007` |
| `osha_incident` | 5 | 0 | - | `osha_incident_v1` | `osha_incident_v1` | `selected_by_closed_profile` | `osha_incident_ugly_001`, `osha_incident_ugly_002`, `osha_incident_ugly_003`, `osha_incident_ugly_004`, `osha_incident_ugly_005` |
| `sec` | 5 | 125 | `en` | `sec_form_8k_v1` | `sec_form_8k_v1` | `selected_by_closed_profile` | `sec_ugly_001`, `sec_ugly_002`, `sec_ugly_003`, `sec_material_event_ugly_006`, `sec_material_event_ugly_007` |
| `sec_material_event` | 5 | 0 | - | `sec_form_8k_v1` | `sec_form_8k_v1` | `selected_by_closed_profile` | `sec_material_event_ugly_001`, `sec_material_event_ugly_002`, `sec_material_event_ugly_003`, `sec_material_event_ugly_004`, `sec_material_event_ugly_005` |
| `enforcement_single_document_hook_001` | 2 | 0 | `en` | - | - | `candidate_unprofiled` | `enforcement_single_document_hook_001`, `enforcement_single_document_hook_001` |
| `legal_controls_medium_001` | 2 | 0 | `en` | - | `legal_authority_verification_v1` | `profile_family_related` | `legal_controls_medium_001`, `legal_controls_medium_001` |
| `ntsb` | 2 | 50 | - | - | `ntsb_investigation_v1` | `profile_family_related` | `ntsb_ugly_001`, `ntsb_ugly_002` |
| `ntsb_aviation` | 2 | 0 | - | - | `ntsb_investigation_v1` | `profile_family_related` | `ntsb_aviation_ugly_001`, `ntsb_aviation_ugly_002` |
| `ntsb_marine` | 2 | 0 | - | - | `ntsb_investigation_v1` | `profile_family_related` | `ntsb_marine_ugly_001`, `ntsb_marine_ugly_002` |
| `ntsb_pivotal_physical_001` | 2 | 0 | `en` | - | `ntsb_investigation_v1` | `profile_family_related` | `ntsb_pivotal_physical_001`, `ntsb_pivotal_physical_001` |
| `procurement` | 2 | 50 | `en` | `procurement_gao_decision_v1` | `procurement_gao_decision_v1` | `selected_by_closed_profile` | `procurement_contract_ugly_002`, `procurement_contract_ugly_003` |
| `public_order_low_001` | 2 | 0 | `en` | - | - | `candidate_unprofiled` | `public_order_low_001`, `public_order_low_001` |
| `puc` | 2 | 50 | `en` | `puc_order_v1` | `puc_order_v1` | `selected_by_closed_profile` | `puc_order_ugly_002`, `puc_order_ugly_003` |
| `regulatory_quality_medium_001` | 2 | 0 | `en` | - | - | `candidate_unprofiled` | `regulatory_quality_medium_001`, `regulatory_quality_medium_001` |
| `sec_scope_low_001` | 2 | 0 | `en` | - | `sec_form_8k_v1` | `profile_family_related` | `sec_scope_low_001`, `sec_scope_low_001` |
| `unknown` | 2 | 50 | - | - | - | `candidate_unprofiled` | `ja_corporate_001`, `ja_regulator_001` |
| `agencia_espa_ola_de_protecci_n_de_datos_resoluci_n_sancionadora` | 1 | 25 | - | - | - | `singleton_unprofiled` | `es_regulator_001` |
| `bolet_n_oficial_del_estado_boe_anuncio_de_licitaci_n_de_poder_adjudicador` | 1 | 25 | - | - | - | `singleton_unprofiled` | `es_public_procurement_001` |
| `bundeskartellamt_pressemitteilung_zu_kartellbeh_rdlichem_bussgeldverfahren` | 1 | 25 | - | - | - | `singleton_unprofiled` | `de_regulator_001` |
| `cnil_commission_nationale_de_l_informatique_et_des_libert_s` | 1 | 25 | - | - | - | `singleton_unprofiled` | `fr_regulator_001` |
| `conseil_d_tat_d_cision_juridictionnelle_cassation_sous_section_r_unie` | 1 | 25 | - | - | - | `singleton_unprofiled` | `fr_eu_official_001` |
| `court` | 1 | 25 | `en` | - | - | `singleton_unprofiled` | `court_order_ugly_002` |
| `court_federal_ndok` | 1 | 25 | - | - | - | `singleton_unprofiled` | `court_ugly_001` |
| `court_order` | 1 | 25 | `en` | - | - | `singleton_unprofiled` | `court_order_ugly_003` |
| `cpsc` | 1 | 25 | - | - | - | `singleton_unprofiled` | `other_ugly_003` |
| `dod_dow_contracts` | 1 | 25 | - | - | - | `singleton_unprofiled` | `procurement_ugly_001` |
| `epa` | 1 | 25 | - | - | - | `singleton_unprofiled` | `other_ugly_001` |
| `fda_warning_letter_cder_office_of_manufacturing_quality` | 1 | 15 | - | - | `fda_warning_letter_v1` | `profile_family_related` | `fda_warning_letter_001` |
| `fda_warning_or_recall_001` | 1 | 0 | - | - | `fda_warning_letter_v1` | `profile_family_related` | `fda_warning_or_recall_001` |
| `ftc` | 1 | 25 | - | - | - | `singleton_unprofiled` | `other_ugly_002` |
| `labor` | 1 | 25 | `en` | - | - | `singleton_unprofiled` | `labor_board_ugly_002` |
| `labor_board` | 1 | 25 | `en` | - | - | `singleton_unprofiled` | `labor_board_ugly_003` |
| `michigan_psc` | 1 | 25 | - | - | - | `singleton_unprofiled` | `puc_ugly_001` |
| `nhtsa` | 1 | 25 | - | - | - | `singleton_unprofiled` | `nhtsa_ugly_001` |
| `nlrb` | 1 | 25 | - | - | - | `singleton_unprofiled` | `nlrb_ugly_001` |
| `ntsb_001` | 1 | 0 | - | - | `ntsb_investigation_v1` | `profile_family_related` | `ntsb_001` |
| `ntsb_002` | 1 | 0 | - | - | `ntsb_investigation_v1` | `profile_family_related` | `ntsb_002` |
| `ntsb_aviation_001` | 1 | 0 | - | `ntsb_investigation_v1` | `ntsb_investigation_v1` | `selected_by_closed_profile` | `ntsb_aviation_001` |
| `ntsb_aviation_investigation_001` | 1 | 0 | - | - | `ntsb_investigation_v1` | `profile_family_related` | `ntsb_aviation_investigation_001` |
| `ntsb_aviation_investigation_final_report_carol` | 1 | 15 | - | - | `ntsb_investigation_v1` | `profile_family_related` | `ntsb_engine_power_001` |
| `ntsb_marine_investigation_001` | 1 | 0 | - | - | `ntsb_investigation_v1` | `profile_family_related` | `ntsb_marine_investigation_001` |
| `ntsb_surface` | 1 | 0 | - | - | `ntsb_investigation_v1` | `profile_family_related` | `ntsb_surface_ugly_001` |
| `osha_incident_or_enforcement_001` | 1 | 0 | - | - | `osha_incident_v1` | `profile_family_related` | `osha_incident_or_enforcement_001` |
| `porsche_se_ad_hoc_mitteilung_gem_ss_art_17_mar` | 1 | 25 | - | - | - | `singleton_unprofiled` | `de_corporate_001` |
| `sec_8k_material_event_001` | 1 | 0 | - | `sec_form_8k_v1` | `sec_form_8k_v1` | `selected_by_closed_profile` | `sec_8k_material_event_001` |
| `sec_edgar_form_8_k_item_4_02_non_reliance_on_previously_issued_financial_statements` | 1 | 15 | - | - | `sec_form_8k_v1` | `profile_family_related` | `sec_restatement_001` |
| `sec_order_instituting_cease_and_desist_proceedings_administrative_proceeding` | 1 | 15 | - | - | `sec_form_8k_v1` | `profile_family_related` | `legal_order_chronology_001` |
| `state_ag` | 1 | 25 | `en` | `state_ag_settlement_v1` | `state_ag_settlement_v1` | `selected_by_closed_profile` | `state_ag_settlement_ugly_002` |
| `state_ag_ny` | 1 | 25 | - | `state_ag_settlement_v1` | `state_ag_settlement_v1` | `selected_by_closed_profile` | `state_ag_ugly_001` |
| `state_ag_settlement` | 1 | 25 | `en` | `state_ag_settlement_v1` | `state_ag_settlement_v1` | `selected_by_closed_profile` | `state_ag_settlement_ugly_003` |

## QA-Bearing Unprofiled Multi-Fixture Families

These are the most relevant retained candidates for future closed-pack work.
They still need a named research reason, a compact seed scope, and independent
expected/forbidden oracles before they can support a claim.

| Family | Fixtures | Questions | Languages | Sample paths |
| --- | ---: | ---: | --- | --- |
| `unknown` | 2 | 50 | - | `datasets/real_world_transfer/fresh_non_english_wild_20260526_01/ja_corporate_001`, `datasets/real_world_transfer/fresh_non_english_wild_20260526_01/ja_regulator_001` |

## All Unprofiled Multi-Fixture Families

These are possible future closed-pack candidates. Families related to an existing profile are omitted here
unless they also need a deliberately separate pack. Candidates still need a named research reason,
a compact seed scope, and independent expected/forbidden oracles before they can support a claim.

| Family | Fixtures | Questions | Languages | Sample paths |
| --- | ---: | ---: | --- | --- |
| `enforcement_single_document_hook_001` | 2 | 0 | `en` | `datasets/real_world_transfer/fresh_ach_stress_public_20260528_02/enforcement_single_document_hook_001`, `datasets/real_world_transfer/fresh_ach_stress_public_20260528_03/enforcement_single_document_hook_001` |
| `public_order_low_001` | 2 | 0 | `en` | `datasets/real_world_transfer/fresh_ach_stress_public_20260528_02/public_order_low_001`, `datasets/real_world_transfer/fresh_ach_stress_public_20260528_03/public_order_low_001` |
| `regulatory_quality_medium_001` | 2 | 0 | `en` | `datasets/real_world_transfer/fresh_ach_stress_public_20260528_02/regulatory_quality_medium_001`, `datasets/real_world_transfer/fresh_ach_stress_public_20260528_03/regulatory_quality_medium_001` |
| `unknown` | 2 | 50 | - | `datasets/real_world_transfer/fresh_non_english_wild_20260526_01/ja_corporate_001`, `datasets/real_world_transfer/fresh_non_english_wild_20260526_01/ja_regulator_001` |

## Closed Profile Selection Coverage

| Profile | Selection paths in registry | Exact matched metadata fixtures |
| --- | ---: | ---: |
| `fda_warning_letter_v1` | 0 | 0 |
| `legal_authority_verification_v1` | 12 | 0 |
| `ntsb_investigation_v1` | 10 | 1 |
| `osha_incident_v1` | 5 | 5 |
| `procurement_gao_decision_v1` | 2 | 2 |
| `puc_order_v1` | 2 | 2 |
| `sec_form_8k_v1` | 4 | 4 |
| `state_ag_settlement_v1` | 3 | 3 |
