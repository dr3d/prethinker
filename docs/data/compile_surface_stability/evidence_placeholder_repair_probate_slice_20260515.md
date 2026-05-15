# Evidence Placeholder Repair Probate Slice

- Schema: `compile_surface_stability_qa_summary_v1`
- Experiment: `evidence_placeholder_repair_probate_slice`
- Question IDs: `q031,q039,q040`
- Questions: `3`
- Reference judge: exact=`1` partial=`0` miss=`2`
- Helper rows: `0`
- Runtime load errors: `0`
- Write proposal rows: `0`
- Failure surfaces: `{"compile_surface_gap":2,"not_applicable":1}`
- Artifact: `tmp/evidence_placeholder_repair_probate_qa_slice_20260515/probate_storage_access_register/domain_bootstrap_qa_20260515T095415702826Z_qa_qwen-qwen3-6-35b-a3b.json`

## Rows

| ID | Verdict | Surface | Reading |
| --- | --- | --- | --- |
| `q031` | `miss` | `compile_surface_gap` | The planner queried both governed items, but the compile still emitted access/source rows only for one item. |
| `q039` | `exact` | `not_applicable` | Source-record evidence plus access/source rows were enough to recover the registrar correspondence and referenced agreements. |
| `q040` | `miss` | `compile_surface_gap` | Placeholder repair exposed claim evidence; the compile still lacks a direct authoritative-source-for-finding surface. |

## Lesson

Evidence/source slot placeholders are generic query variables, not constants.
Repairing `evidencetype` and `evidencesource` style slots restored one row to
exact without adding helpers. The remaining misses are compile-surface gaps:
multi-subject authority coverage and authoritative-source-for-finding surfaces.
