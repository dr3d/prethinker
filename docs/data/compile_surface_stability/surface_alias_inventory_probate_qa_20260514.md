# Surface Alias Inventory Probate QA Summary

- Schema: `compile_surface_stability_qa_summary_v1`
- Experiment: `surface_alias_inventory_probate_qa_limit0_oracle`
- Questions: `40`
- Reference judge: exact=`24` partial=`3` miss=`13`
- Helper rows: `0`
- Runtime load errors: `0`
- Write proposal rows: `0`
- Failure surfaces: `{"query_surface_gap":5,"not_applicable":24,"compile_surface_gap":11}`
- Artifact: `tmp/compile_surface_alias_inventory_probate_qa_limit0_oracle_20260514/probate_storage_access_register/domain_bootstrap_qa_20260515T031422082550Z_qa_qwen-qwen3-6-35b-a3b.json`

## Non-Exact Rows

| ID | Verdict | Surface | Reference answer |
| --- | --- | --- | --- |
| `q001` | `miss` | `query_surface_gap` | Berwick County Probate Court |
| `q005` | `miss` | `compile_surface_gap` | Beatrice Caulfield (B. Caulfield) |
| `q007` | `miss` | `query_surface_gap` | Section D.3 (Reeder-held items), corroborated by H.1 (Reeder's 2026-01-12 correspondence) |
| `q009` | `partial` | `compile_surface_gap` | It extended the loan period to 2027-09-30; it did not change the named lender |
| `q015` | `miss` | `compile_surface_gap` | P-26-347-M-3 |
| `q018` | `miss` | `compile_surface_gap` | 2025-11-04 |
| `q022` | `miss` | `compile_surface_gap` | 2024-10-04 |
| `q023` | `miss` | `compile_surface_gap` | 14 days (2026-06-03 to 2026-06-17) |
| `q026` | `miss` | `query_surface_gap` | 6 (EX-004, EX-005, EX-006, EX-007, EX-008, EX-011) |
| `q028` | `miss` | `query_surface_gap` | 4 (EX-004, EX-005, EX-010, EX-012) |
| `q030` | `partial` | `compile_surface_gap` | Daniel Holloway, asserting an in-person gift on 2024-11-19 |
| `q032` | `miss` | `compile_surface_gap` | Reading-room patron access (governed by museum policy MRP-04, not subject to executor revocation) |
| `q036` | `miss` | `compile_surface_gap` | No - Section G lists the will (dated 2018-07-22) as referenced but not reproduced |
| `q038` | `miss` | `compile_surface_gap` | No - Section F states that reproduction does not constitute a finding of fact and that the assertion has not been ruled upon |
| `q039` | `partial` | `query_surface_gap` | Section H.3, the museum registrar's (B. Caulfield) correspondence dated 2026-04-02, and the loan agreements themselves (referenced but not reproduced) |
| `q040` | `miss` | `compile_surface_gap` | The forensic handwriting analyst's report (when filed) and the Court's ultimate rulings, per Section F |

## Lesson

The alias inventory did not improve no-helper QA on this focused compile. It
gave the planner a generic surface-family map, but successful queries could
still hide answer-bearing constants in the query term itself rather than in
returned rows. That is answer-evidence visibility debt, not helper debt.
