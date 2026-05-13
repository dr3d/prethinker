# Corrected Interval Duration Pair

Boundary class: `temporal_arithmetic_corrected_interval`

This probe isolates duration questions where the answer is not a stored final
duration. The source gives raw endpoint times plus a correction rule, and the
question asks for the elapsed time on the corrected timeline.

The fixture-free geometry is:

- a start endpoint has a raw timestamp;
- an end endpoint has a raw timestamp;
- a correction rule converts the raw endpoints to authoritative endpoints;
- the question asks for the elapsed time between the corrected endpoints;
- decoy raw duration must not override corrected duration.

No repair should name this fixture, its identifiers, or its domains.
