# Answer Detail Surface Transfer

Boundary class: `answer_detail_surface`

This probe tests whether answer-bearing details are preserved as additive
queryable surfaces on fresh unlike documents.

The fixture-free geometry is:

- the source states a concrete backbone row such as subject, status, date,
  count, location, amount, or role;
- the same source also states an answer-bearing detail such as rationale,
  exception, pending item, separate arrangement, outside-scope boundary, or
  promised future action;
- questions ask for both the backbone and the detail;
- a broad event, status, or note row is not sufficient if it replaces the
  concrete backbone rows;
- no helper should reconstruct missing details from prose after compile.

No repair should name this probe, its identifiers, or its domains.
