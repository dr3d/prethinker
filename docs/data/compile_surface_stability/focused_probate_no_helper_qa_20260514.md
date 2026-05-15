# Focused Probate No-Helper QA Summary

- Schema: `compile_surface_stability_qa_summary_v1`
- Questions: `40`
- Reference judge: exact=`26` partial=`4` miss=`10`
- Helper rows: `0`
- Runtime load errors: `0`
- Write proposal rows: `0`
- Failure surfaces: `{"compile_surface_gap":9,"hybrid_join_gap":2,"not_applicable":26,"query_surface_gap":3}`

## Non-Exact Rows

| ID | Verdict | Surface | Reference answer |
| --- | --- | --- | --- |
| `q005` | `miss` | `compile_surface_gap` | Beatrice Caulfield (B. Caulfield) |
| `q007` | `partial` | `compile_surface_gap` | Section D.3 (Reeder-held items), corroborated by H.1 (Reeder's 2026-01-12 correspondence) |
| `q009` | `miss` | `compile_surface_gap` | It extended the loan period to 2027-09-30; it did not change the named lender |
| `q015` | `miss` | `compile_surface_gap` | P-26-347-M-3 |
| `q018` | `miss` | `compile_surface_gap` | 2025-11-04 |
| `q023` | `miss` | `hybrid_join_gap` | 14 days (2026-06-03 to 2026-06-17) |
| `q024` | `partial` | `hybrid_join_gap` | 12 |
| `q026` | `partial` | `compile_surface_gap` | 6 (EX-004, EX-005, EX-006, EX-007, EX-008, EX-011) |
| `q028` | `miss` | `query_surface_gap` | 4 (EX-004, EX-005, EX-010, EX-012) |
| `q031` | `miss` | `query_surface_gap` | The Berwick County Probate Court, by Court Order P-26-347-D dated 2026-02-14 |
| `q032` | `miss` | `query_surface_gap` | Reading-room patron access (governed by museum policy MRP-04, not subject to executor revocation) |
| `q038` | `miss` | `compile_surface_gap` | No â€” Section F states that reproduction does not constitute a finding of fact and that the assertion has not been ruled upon |
| `q039` | `partial` | `compile_surface_gap` | Section H.3, the museum registrar's (B. Caulfield) correspondence dated 2026-04-02, and the loan agreements themselves (referenced but not reproduced) |
| `q040` | `miss` | `compile_surface_gap` | The forensic handwriting analyst's report (when filed) and the Court's ultimate rulings, per Section F |
