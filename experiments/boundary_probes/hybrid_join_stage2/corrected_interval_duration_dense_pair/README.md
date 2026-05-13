# Corrected Interval Duration Dense Pair

Boundary class: `temporal_arithmetic_corrected_interval`

This probe increases density around corrected endpoint duration. It tests
whether the query layer can bind the correct start and end events before doing
elapsed-time arithmetic when several sibling endpoints and raw endpoint decoys
are present.

The fixture-free geometry is:

- several events belong to the same record;
- raw and corrected timestamps are both available;
- more than one corrected interval can be formed;
- the question names the interval role, not just the record;
- the answer requires selecting the matching corrected endpoint pair and then
  computing elapsed time.

No repair should name this fixture, its identifiers, or its domains.
