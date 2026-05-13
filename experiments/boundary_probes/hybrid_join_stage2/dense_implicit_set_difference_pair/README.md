# Dense Implicit Set Difference Pair

Boundary class: `dense_implicit_set_difference`

This probe extends the simple implicit-difference probe by adding overlapping
populations and multiple exclusion sources. It tests whether the query/evidence
surface can bind the requested review to the correct population and exclusion
notice without an explicit `set_minus` fact or printed final answer.

The fixture-free geometry is:

- two or more populations share some member tokens;
- two or more exclusion notices remove different subsets;
- each review binds one population to one exclusion source;
- questions ask for remaining members and counts for a named review;
- final lists and counts are not printed.

No repair should name this probe, its identifiers, or its domains.
