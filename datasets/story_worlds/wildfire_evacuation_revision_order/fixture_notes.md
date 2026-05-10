# wildfire_evacuation_revision_order Fixture Notes

## Author Delivery Note

Fixture 2, `wildfire_evacuation_revision_order`, was described by the author as
complete: source around 1,950 words, 40 oracle rows, and a deliberately thorny
supersession structure.

## Core Supersession Shape

The fixture has two interacting version chains:

- order chain: `DRAFT -> 014A -> 014B`;
- map/layer chain: `v1.0 -> v1.1 -> v1.1.1`.

The `v1.1` layer was published but wrong for one subdivision. This means the
fixture distinguishes:

- what the published layer said at a given time;
- what the corrected order/layer establishes after the correction.

## Fixture-Specific Notes

- Q20 versus Q21 is the linchpin pair. They concern the same parcels and nearly
  the same timeline, but require different valid answers depending on whether
  the question asks what the published layer said or what the corrected order
  says. This should catch parsers that collapse published-but-wrong state into
  corrected state, or vice versa.
- Q29 is a refusal trap. The Forest Supervisor email gives enough context that
  an LLM may confabulate a USFS process. The oracle answer is intentionally
  "not specified." Grade this strictly.
- Q40 is intentionally compound. It asks for three sub-states across two
  documents and probes whether Prethinker can return a temporal-interval answer
  rather than a single point answer.

## Self-Flagged Leakage Risk

The anti-leakage manifest notes one possible source-leakage concern: section 4
includes the count "46 parcels" in prose alongside the parcel range
`074-220-001 through 074-220-046`. That arguably makes Q31 a lookup rather than
a pure range-to-count derivation.

Possible future edit: replace "46 parcels" with "the parcels" in source prose
and force Q31 to derive the count from the range. Do not make this edit without
an explicit decision, because preserving the authored fixture exactly may be
preferred for baseline comparability.
