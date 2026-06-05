# Candidate Oracle Review Audit

This report validates retained candidate-review package structure only.
It does not read source prose, inspect model outputs, or decide facts.
It verifies review folder identity and repo-relative source-file references without opening those sources.
Expected facts are hard-gated for compact atom shape and registered carrier value domains.
Forbidden facts are negative sentinels; off-domain or prose-shaped sentinel values are warnings, not support.

- Reviews: `9`
- Blocking errors: `0`
- Warnings: `17`
- Status: `pass`

| Review | Fixture | Predicate | Expected | Forbidden | Blind | Read Forbidden Inputs | Errors | Warnings |
| --- | --- | --- | ---: | ---: | --- | --- | --- | --- |
| `fda_response_assessment_item_oracle_review_20260604_fda_warning_letter_domain_transfer_001` | `fda_warning_letter_domain_transfer_001` | `fda_response_assessment_item/6` | 0 | 9 | `True` | `False` | `[]` | `['missing_README.md', 'candidate_forbidden_facts.pl:line_15:forbidden_value_domain:cgmps_citation:value_not_allowed:cfr_21_211_22_d', 'candidate_forbidden_facts.pl:line_16:forbidden_value_domain:cgmps_citation:value_not_allowed:cfr_21_211_28_a', 'candidate_forbidden_facts.pl:line_17:forbidden_value_domain:cgmps_citation:value_not_allowed:cfr_21_211_42_c_10_vi', 'candidate_forbidden_facts.pl:line_18:forbidden_value_domain:cgmps_citation:value_not_allowed:cfr_21_211_188', 'candidate_forbidden_facts.pl:line_21:forbidden_atom_shape:quoted_atom_contains_whitespace:arg6']` |
| `fda_response_assessment_item_oracle_review_20260604_fda_warning_letter_domain_transfer_002` | `fda_warning_letter_domain_transfer_002` | `fda_response_assessment_item/6` | 3 | 8 | `True` | `False` | `[]` | `['missing_README.md', 'candidate_forbidden_facts.pl:line_8:forbidden_value_domain:cgmps_citation:value_not_allowed:cfr_21_211_58', 'candidate_forbidden_facts.pl:line_20:forbidden_atom_shape:quoted_atom_contains_whitespace:arg6']` |
| `fda_response_assessment_item_oracle_review_20260604_fda_warning_letter_domain_transfer_003` | `fda_warning_letter_domain_transfer_003` | `fda_response_assessment_item/6` | 1 | 8 | `True` | `False` | `[]` | `['missing_README.md', 'candidate_forbidden_facts.pl:line_12:forbidden_value_domain:cgmps_citation:value_not_allowed:cfr_21_211_63', 'candidate_forbidden_facts.pl:line_16:forbidden_value_domain:cgmps_citation:value_not_allowed:cfr_21_211_34', 'candidate_forbidden_facts.pl:line_22:forbidden_atom_shape:quoted_atom_contains_whitespace:arg6']` |
| `fda_response_documentation_gap_oracle_review_20260603` | `fda_warning_letter_domain_transfer_002` | `fda_response_documentation_gap/5` | 0 | 13 | `True` | `False` | `[]` | `['candidate_forbidden_facts.pl:line_40:forbidden_value_domain:cgmps_citation:value_not_allowed:cfr_21_211_58', 'candidate_forbidden_facts.pl:line_55:forbidden_value_domain:gap_kind:value_not_allowed:sop_0870_3_0', 'candidate_forbidden_facts.pl:line_59:forbidden_value_domain:gap_kind:value_not_allowed:investigation_failure', 'candidate_forbidden_facts.pl:line_65:forbidden_atom_shape:quoted_atom_contains_whitespace:arg5']` |
| `fda_t002_adulteration_basis_focused_review_20260605` | `fda_warning_letter_domain_transfer_002` | `fda_adulteration_basis/5` | 0 | 1 | `True` | `False` | `[]` | `[]` |
| `fda_t002_oos_assay_detail_focused_review_20260605` | `fda_warning_letter_domain_transfer_002` | `fda_violation_detail/5` | 1 | 0 | `True` | `False` | `[]` | `[]` |
| `fda_t002_peeling_paint_detail_focused_review_20260605` | `fda_warning_letter_domain_transfer_002` | `fda_violation_detail/5` | 1 | 0 | `True` | `False` | `[]` | `[]` |
| `osha_fta_total_penalty_blind_review_20260605` | `osha_incident_domain_v1` | `osha_penalty_amount/5` | 1 | 0 | `True` | `False` | `[]` | `[]` |
| `sec_exhibit_treatment_blind_review_20260605` | `sec_form_8k_skeleton_v1` | `sec_exhibit/5` | 0 | 1 | `True` | `False` | `[]` | `[]` |
