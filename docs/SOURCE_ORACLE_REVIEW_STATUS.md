# Source Oracle Review Audit

This report validates retained source-only expected/forbidden oracle packages.
It does not read source prose, inspect model outputs, or decide facts.
Expected facts are hard-gated for compact atom shape and registered carrier value domains.
Forbidden facts are negative sentinels; off-domain or prose-shaped sentinel values are warnings, not support.

- Reviews: `2`
- Outputs: `4`
- Blocking errors: `0`
- Warnings: `5`
- Status: `pass`

| Review | Proposal | Predicate | Status | Fixture | Expected | Forbidden | Errors | Warnings |
| --- | --- | --- | --- | --- | ---: | ---: | --- | --- |
| `procurement_gao_decision_wrapper_v1_procurement_gao_decision_wrapper_oracle_review_20260605` | `procurement_gao_decision_wrapper_v1` | `gao_bid_protest_decision/7` | `complete` | `procurement_contract_ugly_002` | 1 | 8 | `[]` | `['forbidden_facts.pl:line_12:forbidden_atom_shape:atom_value_prose_shaped:arg4']` |
| `procurement_gao_decision_wrapper_v1_procurement_gao_decision_wrapper_oracle_review_20260605` | `procurement_gao_decision_wrapper_v1` | `gao_bid_protest_decision/7` | `complete` | `procurement_contract_ugly_003` | 1 | 8 | `[]` | `[]` |
| `puc_order_wrapper_v1_puc_order_wrapper_oracle_review_20260604` | `puc_order_wrapper_v1` | `puc_order/7` | `complete` | `puc_order_ugly_002` | 1 | 8 | `[]` | `['forbidden_facts.pl:line_5:forbidden_atom_shape:atom_value_prose_shaped:arg4']` |
| `puc_order_wrapper_v1_puc_order_wrapper_oracle_review_20260604` | `puc_order_wrapper_v1` | `puc_order/7` | `complete` | `puc_order_ugly_003` | 1 | 7 | `[]` | `['forbidden_facts.pl:line_5:forbidden_atom_shape:atom_value_prose_shaped:arg6', 'forbidden_facts.pl:line_11:forbidden_atom_shape:atom_value_prose_shaped:arg4', 'forbidden_facts.pl:line_11:forbidden_atom_shape:atom_value_prose_shaped:arg4']` |
