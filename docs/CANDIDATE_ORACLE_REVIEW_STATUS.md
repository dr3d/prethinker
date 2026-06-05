# Candidate Oracle Review Audit

This report validates retained candidate-review package structure only.
It does not read source prose, inspect model outputs, or decide facts.
It verifies review folder identity and repo-relative source-file references without opening those sources.
Expected facts are hard-gated for compact atom shape and registered carrier value domains.
Forbidden facts are negative sentinels; off-domain or prose-shaped sentinel values are warnings, not support.

- Reviews: `1`
- Blocking errors: `0`
- Warnings: `4`
- Status: `pass`

| Review | Fixture | Predicate | Expected | Forbidden | Blind | Read Forbidden Inputs | Errors | Warnings |
| --- | --- | --- | ---: | ---: | --- | --- | --- | --- |
| `fda_response_documentation_gap_oracle_review_20260603` | `fda_warning_letter_domain_transfer_002` | `fda_response_documentation_gap/5` | 0 | 13 | `True` | `False` | `[]` | `['candidate_forbidden_facts.pl:line_40:forbidden_value_domain:cgmps_citation:value_not_allowed:cfr_21_211_58', 'candidate_forbidden_facts.pl:line_55:forbidden_value_domain:gap_kind:value_not_allowed:sop_0870_3_0', 'candidate_forbidden_facts.pl:line_59:forbidden_value_domain:gap_kind:value_not_allowed:investigation_failure', 'candidate_forbidden_facts.pl:line_65:forbidden_atom_shape:quoted_atom_contains_whitespace:arg5']` |
