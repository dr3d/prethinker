# Layered Multi-Subject Authority Probe QA

- Schema: `compile_surface_stability_qa_summary_v1`
- Experiment: `layered_multi_subject_authority_probe`
- Question IDs: `q001,q002,q003,q004,q005,q006,q007,q008`
- Questions: `8`
- Reference judge: exact=`8` partial=`0` miss=`0`
- Helper rows: `0`
- Runtime load errors: `0`
- Write proposal rows: `0`
- Failure surfaces: `{"not_applicable":8}`
- Compile artifact: `tmp/layered_multi_subject_authority_compile_20260515/layered_multi_subject_authority_pair/domain_bootstrap_file_20260515T100530546051Z_source_qwen-qwen3-6-35b-a3b.json`
- QA artifact: `tmp/layered_multi_subject_authority_source_text_qa_20260515/layered_multi_subject_authority_pair/domain_bootstrap_qa_20260515T100922813139Z_qa_qwen-qwen3-6-35b-a3b.json`

## Rows

| ID | Verdict | Surface | Reading |
| --- | --- | --- | --- |
| `q001` | `exact` | `not_applicable` | Multi-file access list recovered. |
| `q002` | `exact` | `not_applicable` | Exact source-column wording recovered through source-record text. |
| `q003` | `exact` | `not_applicable` | Correspondence-to-authority reference recovered. |
| `q004` | `exact` | `not_applicable` | Non-authority preparation note boundary recovered. |
| `q005` | `exact` | `not_applicable` | Multi-specimen release list recovered. |
| `q006` | `exact` | `not_applicable` | Decision-packet authority for one governed specimen recovered. |
| `q007` | `exact` | `not_applicable` | Follow-up note author/source metadata recovered. |
| `q008` | `exact` | `not_applicable` | Older non-authority notice boundary recovered. |

## Lesson

Layered multi-subject authority with correspondence and decision-packet
references passed `8/0/0` with zero helpers after a narrow source-column text
query hint. Explicit layered source authority is interior. Remaining misses
should focus on denser or less explicit source statements.
