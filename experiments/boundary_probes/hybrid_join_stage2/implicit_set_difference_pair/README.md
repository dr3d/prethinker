# Implicit Set Difference Pair

Boundary class: `implicit_set_difference`

This probe tests whether the compile and QA layers can answer a remaining-set
question when the source prints the universe and the excluded subset, but does
not print a derived set-operation fact, view name, final list, or final count.

The fixture-free geometry is:

- a source lists a complete population;
- a separate source row or notice marks a subset for exclusion;
- the question asks for the unmarked or remaining population;
- no explicit `set_minus` view is supplied in the prose;
- final lists and counts must be assembled from component facts.

No repair should name this probe, its identifiers, or its domains.
