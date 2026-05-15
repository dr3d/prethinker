# Authority Source Query Contract Slice

- Schema: `compile_surface_stability_qa_summary_v1`
- Experiment: `authority_source_query_contract_slice`
- Question IDs: `q010,q031,q039,q040`
- Questions: `4`
- Reference judge: exact=`1` partial=`1` miss=`2`
- Helper rows: `0`
- Runtime load errors: `0`
- Write proposal rows: `0`
- Failure surfaces: `{"compile_surface_gap":3,"not_applicable":1}`
- Artifact: `tmp/authority_source_query_contract_slice_20260514/probate_storage_access_register/domain_bootstrap_qa_20260515T042328262779Z_qa_qwen-qwen3-6-35b-a3b.json`

## Rows

| ID | Verdict | Surface | Reading |
| --- | --- | --- | --- |
| `q010` | `exact` | `not_applicable` | Court-order section question recovered. |
| `q031` | `miss` | `compile_surface_gap` | Planner queried `access_source/3`; compile had source for one requested item but not the paired item. |
| `q039` | `miss` | `compile_surface_gap` | Planner queried `access_source/3`, but source/correspondence authority rows were not dense enough to answer the registrar/loan-agreement source. |
| `q040` | `partial` | `compile_surface_gap` | Claim evidence rows exposed forensic-report support, but court-ultimate-ruling/source-authority distinction was still incomplete. |

## Lesson

The query contract moved the planner in the intended direction. The remaining
failures are no longer "the planner did not know to ask authority/source";
they are compile-coverage gaps in paired item authority and source/correspondence
authority density.
