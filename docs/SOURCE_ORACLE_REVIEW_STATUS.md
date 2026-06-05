# Source Oracle Review Audit

This report validates retained source-only expected/forbidden oracle packages.
It does not read source prose, inspect model outputs, or decide facts.
Expected facts are hard-gated for compact atom shape and registered carrier value domains.
Forbidden facts are negative sentinels; off-domain or prose-shaped sentinel values are warnings, not support.

- Reviews: `2`
- Outputs: `4`
- Blocking errors: `0`
- Warnings: `12`
- Status: `pass`

| Review | Proposal | Predicate | Status | Fixture | Expected | Forbidden | Errors | Warnings |
| --- | --- | --- | --- | --- | ---: | ---: | --- | --- |
| `procurement_gao_decision_wrapper_v1_procurement_gao_decision_wrapper_oracle_review_20260605` | `procurement_gao_decision_wrapper_v1` | `gao_bid_protest_decision/7` | `complete` | `procurement_contract_ugly_002` | 1 | 8 | `[]` | `['forbidden_facts.pl:line_9:forbidden_value_domain:decision_status:value_not_allowed:agency_failed_to_document_consideration_of_an_apparent_oci', 'forbidden_facts.pl:line_12:forbidden_atom_shape:registered_carrier_prose_shaped_value:arg4']` |
| `procurement_gao_decision_wrapper_v1_procurement_gao_decision_wrapper_oracle_review_20260605` | `procurement_gao_decision_wrapper_v1` | `gao_bid_protest_decision/7` | `complete` | `procurement_contract_ugly_003` | 1 | 8 | `[]` | `['forbidden_facts.pl:line_22:forbidden_value_domain:decision_status:value_not_allowed:brymak_lower_priced_proposal_represented_best_value']` |
| `puc_order_wrapper_v1_puc_order_wrapper_oracle_review_20260604` | `puc_order_wrapper_v1` | `puc_order/7` | `complete` | `puc_order_ugly_002` | 1 | 8 | `[]` | `['forbidden_facts.pl:line_5:forbidden_atom_shape:registered_carrier_prose_shaped_value:arg4', 'forbidden_facts.pl:line_5:forbidden_value_domain:order_kind:value_not_allowed:resolution_alj_445_resolving_request_for_hearing_h_22_07_010_on_administrative_enforcement_order', 'forbidden_facts.pl:line_8:forbidden_value_domain:decision_status:value_not_allowed:the_amounts_are_fair_just_and_reasonable', 'forbidden_facts.pl:line_23:forbidden_value_domain:decision_status:value_not_allowed:pge_shall_pay_500000_fine_to_the_general_fund']` |
| `puc_order_wrapper_v1_puc_order_wrapper_oracle_review_20260604` | `puc_order_wrapper_v1` | `puc_order/7` | `complete` | `puc_order_ugly_003` | 1 | 7 | `[]` | `['forbidden_facts.pl:line_5:forbidden_atom_shape:registered_carrier_prose_shaped_value:arg6', 'forbidden_facts.pl:line_5:forbidden_value_domain:decision_status:value_not_allowed:just_and_reasonable_in_result_and_in_the_public_interest', 'forbidden_facts.pl:line_11:forbidden_atom_shape:registered_carrier_prose_shaped_value:arg4', 'forbidden_facts.pl:line_11:forbidden_atom_shape:registered_carrier_prose_shaped_value:arg4', 'forbidden_facts.pl:line_11:forbidden_value_domain:order_kind:value_not_allowed:order_memorializing_decision_application_of_rocky_mountain_power_for_authority_to_increase_its_retail_electric_utility_service_rates']` |
