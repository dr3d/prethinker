# Set Dedupe Aggregation Pair

Boundary class: `set_dedupe_aggregation`

This probe tests component-set construction before counting or listing. The
source prints the member rows and exclusion/duplicate/amendment facts, but does
not print the final deduplicated set or final counts.

The fixture-free geometry is:

- a raw member list contains an alias or duplicate row;
- the source states which row duplicates another row;
- a subset is excluded by status or membership;
- an amendment adds one row to a previously named set;
- questions ask for unique counts, unaffected sets, or post-amendment sets;
- final sets and counts must be assembled from component facts.

No repair should name this fixture, its identifiers, or its domains.
