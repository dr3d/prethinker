# Token Subset Relaxed Probate QA Summary

- Schema: `compile_surface_stability_qa_summary_v1`
- Experiment: `token_subset_relaxed_probate_qa_limit0_oracle`
- Questions: `40`
- Reference judge: exact=`28` partial=`1` miss=`11`
- Helper rows: `0`
- Runtime load errors: `0`
- Write proposal rows: `0`
- Failure surfaces: `{"compile_surface_gap":7,"hybrid_join_gap":1,"not_applicable":28,"query_surface_gap":4}`
- Artifact: `tmp/token_subset_relaxed_probate_qa_limit0_oracle_20260514/probate_storage_access_register/domain_bootstrap_qa_20260515T034333814953Z_qa_qwen-qwen3-6-35b-a3b.json`

## Movement From Bound-Constant Replay

| Row | Previous | Token-subset replay |
| --- | --- | --- |
| `q007` | `partial / judge_uncertain` | `exact / not_applicable` |
| `q010` | `miss / compile_surface_gap` | `exact / not_applicable` |
| `q028` | `partial / query_surface_gap` | `miss / query_surface_gap` |
| `q032` | `miss / compile_surface_gap` | `miss / query_surface_gap` |
| `q036` | `miss / compile_surface_gap` | `exact / not_applicable` |
| `q038` | `exact / not_applicable` | `miss / compile_surface_gap` |
| `q039` | `partial / hybrid_join_gap` | `miss / hybrid_join_gap` |

## Lesson

Strict token-subset filtering is worth keeping: it improved the focused
no-helper score to `28/1/11` with `0` helper rows and reduced compile-surface
gaps from `9` to `7`. A broader distinctive-token-overlap variant was tested
afterward, but replay fell to `26/2/12`; that broadening was reverted. The
architecture keeps the narrower repair and treats the remaining misses as
compile-coverage or query-choice debt.
