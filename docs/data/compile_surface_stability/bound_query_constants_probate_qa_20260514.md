# Bound Query Constants Probate QA Summary

- Schema: `compile_surface_stability_qa_summary_v1`
- Experiment: `bound_query_constants_probate_qa_limit0_oracle`
- Questions: `40`
- Reference judge: exact=`26` partial=`4` miss=`10`
- Helper rows: `0`
- Runtime load errors: `0`
- Write proposal rows: `0`
- Failure surfaces: `{"not_applicable":26,"compile_surface_gap":9,"judge_uncertain":1,"query_surface_gap":3,"hybrid_join_gap":1}`
- Artifact: `tmp/bound_query_constants_probate_qa_limit0_oracle_20260514/probate_storage_access_register/domain_bootstrap_qa_20260515T032939442860Z_qa_qwen-qwen3-6-35b-a3b.json`

## Non-Exact Rows

| ID | Verdict | Surface | Reference answer |
| --- | --- | --- | --- |
| `q005` | `miss` | `compile_surface_gap` | Beatrice Caulfield (B. Caulfield) |
| `q007` | `partial` | `judge_uncertain` | Section D.3 (Reeder-held items), corroborated by H.1 (Reeder's 2026-01-12 correspondence) |
| `q009` | `partial` | `compile_surface_gap` | It extended the loan period to 2027-09-30; it did not change the named lender |
| `q010` | `miss` | `compile_surface_gap` | Section E (Court Orders Affecting This Register) |
| `q015` | `miss` | `compile_surface_gap` | P-26-347-M-3 |
| `q023` | `miss` | `compile_surface_gap` | 14 days (2026-06-03 to 2026-06-17) |
| `q026` | `miss` | `query_surface_gap` | 6 (EX-004, EX-005, EX-006, EX-007, EX-008, EX-011) |
| `q028` | `partial` | `query_surface_gap` | 4 (EX-004, EX-005, EX-010, EX-012) |
| `q030` | `miss` | `compile_surface_gap` | Daniel Holloway, asserting an in-person gift on 2024-11-19 |
| `q031` | `miss` | `query_surface_gap` | The Berwick County Probate Court, by Court Order P-26-347-D dated 2026-02-14 |
| `q032` | `miss` | `compile_surface_gap` | Reading-room patron access (governed by museum policy MRP-04, not subject to executor revocation) |
| `q036` | `miss` | `compile_surface_gap` | No - Section G lists the will (dated 2018-07-22) as referenced but not reproduced |
| `q039` | `partial` | `hybrid_join_gap` | Section H.3, the museum registrar's (B. Caulfield) correspondence dated 2026-04-02, and the loan agreements themselves (referenced but not reproduced) |
| `q040` | `miss` | `compile_surface_gap` | The forensic handwriting analyst's report (when filed) and the Court's ultimate rulings, per Section F |

## Lesson

Making bound query constants visible repaired cases where the answer-bearing
value was confirmed by a successful query but absent from returned variable
rows. It restored the focused no-helper score to `26/4/10`, with `0` helper
rows, but did not improve beyond the earlier baseline. The next repair should
target query choice and direct compile coverage, not native helper delivery.
