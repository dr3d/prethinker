# Query Grounding Status

Generated from retained atom-library query artifacts, typed-plan replay, and redaction replay.
This report does not read source prose, source-record rows, or QA oracle prose.

## Summary

- Status: `pass`
- Cells: `3`
- Query rows: `75`
- Product exact: `75 / 75`
- Typed-plan exact: `75 / 75`
- Redaction-survived exact: `75 / 75`
- Prose-dependent exact rows: `0`
- Unregistered exact typed plans: `0`
- Blocked source-record plan rows: `0`
- Runtime load error rows: `0`
- Errors / warnings: `0 / 0`

## Cells

| Cell | Packet | Rows | Product | Typed replay | Redaction | Prose dep | Unregistered | Model / Settings |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `sec_atom_library_query_qwen_moe_r2` | `sec_form_8k_atom_library_query_v1` | 25 | 25/25 | 25/25 | 25/25 | 0 | 0 | `local_lmstudio` `qwen/qwen3.6-35b-a3b`; quant `Q4_K_M`; temp `0.0`; top_p `0.82`; ctx `32768`; loaded `65536` |
| `current_domain_atom_library_query_qwen_moe_r5` | `current_domain_atom_library_query_v1` | 25 | 25/25 | 25/25 | 25/25 | 0 | 0 | `local_lmstudio` `qwen/qwen3.6-35b-a3b`; quant `Q4_K_M`; temp `0.0`; top_p `0.82`; ctx `32768`; loaded `65536` |
| `current_domain_atom_library_query_qwen_moe_r6` | `current_domain_atom_library_query_v1` | 25 | 25/25 | 25/25 | 25/25 | 0 | 0 | `local_lmstudio` `qwen/qwen3.6-35b-a3b`; quant `Q4_K_M`; temp `0.0`; top_p `0.82`; ctx `32768`; loaded `65536` |
