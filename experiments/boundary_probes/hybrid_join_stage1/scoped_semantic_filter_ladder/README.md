# Scoped Semantic Filter Ladder Probe

Boundary class: `hybrid_join_gap`, subclass `status_timeline_join`, evidence
class `scoped_semantic_filter_count`.

Prediction: the compiler should expose status rows plus the scope/criterion that
distinguishes which rows count for a scoped semantic count. A failure here means
the next live-set extension is not generic status counting; it is status count
aggregation constrained by a source-stated criterion.

Forbidden fix: no selector, helper, or mapper logic may reference this probe's
packet id, case ids, question ids, local section labels, or answer strings.
