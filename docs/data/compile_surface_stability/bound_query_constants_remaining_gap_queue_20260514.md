# Bound Query Constants Remaining Gap Queue

- Schema: `compile_surface_stability_gap_queue_v1`
- Source run: `tmp/bound_query_constants_probate_qa_limit0_oracle_20260514/probate_storage_access_register/domain_bootstrap_qa_20260515T032939442860Z_qa_qwen-qwen3-6-35b-a3b.json`
- Questions: `40`
- Non-exact rows: `14`
- Helper rows: `0`

## Queue Summary

| Queue | Rows | Meaning |
| --- | ---: | --- |
| `compile_coverage` | 7 | The direct compile does not expose the requested distinction cleanly enough. |
| `query_choice` | 4 | The needed surface exists, but the planner asks the wrong slot or over-binds a value. |
| `hybrid_or_mixed` | 3 | The answer needs both better query choice and possibly denser direct compile coverage. |

## Rows

| ID | Verdict | Current surface | Queue | Why |
| --- | --- | --- | --- | --- |
| `q005` | `miss` | `compile_surface_gap` | `compile_coverage` | Query finds the organization role, not the registrar identity; the direct compile lacks the role-holder distinction. |
| `q007` | `partial` | `judge_uncertain` | `hybrid_or_mixed` | The planner broadens placeholder queries and reaches related assertion/custody rows, but the section basis is not cleanly bound. |
| `q009` | `partial` | `compile_surface_gap` | `compile_coverage` | Loan amendment effect and unchanged lender are not emitted as direct answer-bearing facts. |
| `q010` | `miss` | `compile_surface_gap` | `hybrid_or_mixed` | The order identity exists nearby, but section/source addressability for the order is not queryable enough. |
| `q015` | `miss` | `compile_surface_gap` | `compile_coverage` | Motion number filed by actor/date is not exposed as a direct event. |
| `q023` | `miss` | `compile_surface_gap` | `query_choice` | Order dates/effects exist, but the planner calls elapsed-days with unbound endpoint variables instead of binding the due/hearing dates first. |
| `q026` | `miss` | `query_surface_gap` | `hybrid_or_mixed` | Status wording over-binds, and one expected item appears absent from the direct status surface. |
| `q028` | `partial` | `query_surface_gap` | `query_choice` | Location wording over-binds; relaxed query returns the relevant location family but too broadly. |
| `q030` | `miss` | `compile_surface_gap` | `compile_coverage` | The claimant exists, but asserted gift date is not directly bound to the assertion. |
| `q031` | `miss` | `query_surface_gap` | `query_choice` | The planner answers who received access instead of who authorized it; authority/source predicates need to be queried. |
| `q032` | `miss` | `compile_surface_gap` | `compile_coverage` | No-authority category for the item is not directly emitted. |
| `q036` | `miss` | `compile_surface_gap` | `compile_coverage` | Referenced-but-not-reproduced document status is not directly queryable. |
| `q039` | `partial` | `hybrid_join_gap` | `query_choice` | Source authority exists in access/source rows, but the planner queries a generic asset placeholder and does not bind the specific agreement family. |
| `q040` | `miss` | `compile_surface_gap` | `compile_coverage` | Section-level authoritative sources for dispute findings are not emitted as a direct source-authority surface. |

## Lesson

The remaining zero-helper gap is not one substance. Native helpers should not
come back to cover it wholesale. Compile-coverage rows belong in invariant
guidance and focused compile probes. Query-choice rows belong in planner tests
and query repair, especially over-bound constants, wrong authority slot, and
unbound temporal endpoints.
