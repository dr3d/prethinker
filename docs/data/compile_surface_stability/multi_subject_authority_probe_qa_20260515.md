# Multi-Subject Authority Probe QA

- Schema: `compile_surface_stability_qa_summary_v1`
- Experiment: `multi_subject_authority_probe`
- Question IDs: `q001,q002,q003,q004,q005,q006,q007,q008`
- Questions: `8`
- Reference judge: exact=`8` partial=`0` miss=`0`
- Helper rows: `0`
- Runtime load errors: `0`
- Write proposal rows: `0`
- Failure surfaces: `{"not_applicable":8}`
- Compile artifact: `tmp/multi_subject_authority_compile_20260515/multi_subject_authority_pair/domain_bootstrap_file_20260515T095815102314Z_source_qwen-qwen3-6-35b-a3b.json`
- QA artifact: `tmp/multi_subject_authority_metadata_qa_20260515/multi_subject_authority_pair/domain_bootstrap_qa_20260515T100211329038Z_qa_qwen-qwen3-6-35b-a3b.json`

## Rows

| ID | Verdict | Surface | Reading |
| --- | --- | --- | --- |
| `q001` | `exact` | `not_applicable` | Multi-cabinet authority list recovered. |
| `q002` | `exact` | `not_applicable` | Source authority for one governed cabinet recovered. |
| `q003` | `exact` | `not_applicable` | Access type for another governed cabinet recovered. |
| `q004` | `exact` | `not_applicable` | Nearby older authority boundary recovered. |
| `q005` | `exact` | `not_applicable` | Multi-package release list recovered. |
| `q006` | `exact` | `not_applicable` | Source authority plus issuer/date recovered after instrument metadata query hint. |
| `q007` | `exact` | `not_applicable` | Nearby non-transfer hold note recovered. |
| `q008` | `exact` | `not_applicable` | Explicit negative authority boundary recovered. |

## Lesson

A fresh unlike multi-subject authority probe passed `8/0/0` with zero helpers.
The current instrument can compile one authority governing multiple subjects
into direct rows when the source is simple. The remaining probate authority
miss is density/resolution, not a missing axis.
