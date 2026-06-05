# FDA T002 OOS Assay Detail Focused Review

Source-only focused review returned on 2026-06-05 from the cleaned work-order
packet. The reviewer did not receive model outputs, prior oracle files, or
judged-QA manifests.

Decision: `expected_addition`.

Candidate:

```prolog
fda_violation_detail(violation_2, record_review_subject, out_of_specification_assay, violation_scope, direct).
```

Source-only rationale: violation 2 is the `211.192` failure-to-investigate
row, and the source explicitly names out-of-specification assay results as an
inadequately investigated subject. The closed FDA detail contract represents
that as a compact `record_review_subject` row.
