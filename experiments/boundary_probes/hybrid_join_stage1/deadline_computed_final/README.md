# Deadline Computed Final Probe

Boundary class: `hybrid_join_gap`.

Prediction: the compiler should expose the base date, tolling amount, granted
extension, and rejected decoys as generic date/status/authority coordinates. QA
should answer the final date by applying only approved adjustments. If the final
date fails while the inputs pass, the boundary is a derived temporal join rather
than missing extraction.

Forbidden fix: no selector, helper, or mapper logic may reference this probe's
permit id, officer name, event ids, question ids, or answer date.
