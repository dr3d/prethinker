# Status Count Aggregation Ladder Probe

Boundary class: `hybrid_join_gap`, subclass `status_timeline_join`, density
class `status_count_aggregation`.

Prediction: the compiler should expose item status transitions and decoys, while
QA should count the final status at close of record. A failure here means the
next live-set extension is status-conditioned set/count aggregation, not
point-in-time state resolution.

Forbidden fix: no selector, helper, or mapper logic may reference this probe's
docket id, issue ids, question ids, local status words, or answer strings.
