# Arithmetic Aggregation Unstated Pair

Boundary class: `arithmetic_aggregation_join`

This probe tests ordinary aggregation where the source prints the component
rows and the calculation instruction, but does not print the final aggregate.

The fixture-free geometry is:

- component values are stated as separate rows;
- inclusion/exclusion status is stated;
- the source names the aggregation view;
- the final sum or average must be assembled from the pieces;
- no final aggregate value is printed in the source.

Business-day and wall-clock arithmetic are intentionally absent. This probe is
only about numeric sum/average aggregation over admitted component rows.

No repair should name this fixture, its identifiers, or its domains.
