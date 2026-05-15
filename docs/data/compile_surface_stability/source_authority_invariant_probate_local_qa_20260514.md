# Source Authority Invariant Local Probate QA Summary

- Schema: `compile_surface_stability_qa_summary_v1`
- Experiment: `source_authority_invariant_probate_local_qa_limit0_oracle`
- Questions: `40`
- Reference judge: exact=`21` partial=`4` miss=`15`
- Helper rows: `0`
- Runtime load errors: `0`
- Write proposal rows: `0`
- Failure surfaces: `{"compile_surface_gap":10,"not_applicable":21,"query_surface_gap":9}`
- Compile artifact: `tmp/source_authority_invariant_probate_compile_local_20260514/probate_storage_access_register/domain_bootstrap_file_20260515T040742270464Z_source_qwen-qwen3-6-35b-a3b.json`
- QA artifact: `tmp/source_authority_invariant_probate_local_qa_limit0_oracle_20260514/probate_storage_access_register/domain_bootstrap_qa_20260515T041919315179Z_qa_qwen-qwen3-6-35b-a3b.json`

## Result

The local recompile emitted useful authority/source surfaces, including
`access_source/3`, `access_authorized_to/3`, `court_order/4`,
`claim_asserted_by/3`, and `claim_evidence/3`. The compile itself was healthy
enough to test:

- admitted=`175`
- skipped=`8`
- invariant audit: pass=`4`, partial=`3`, candidate_only=`0`, ledger_only=`0`

The QA replay did not hold:

- exact=`21`
- partial=`4`
- miss=`15`
- helper rows=`0`

## Lesson

This is not a reason to restore native helpers. It is evidence that source
authority and section addressability must be treated as a compile-plus-query
contract. The compiler can emit better authority rows while the QA planner
still misses them if the predicate palette shifts from `authorized_party` /
`access_authority_source` to `access_authorized_to` / `access_source`.

## Next

Do not adopt this local compile as the new baseline. Keep the stricter
token-subset no-helper run (`28/1/11`) as the current best zero-helper reading.
The next repair should make query planning more predicate-contract aware for
authority/source palettes before another compile replay.
