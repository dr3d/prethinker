# Status Timeline Ladder Probe

Boundary class: `hybrid_join_gap`, subclass `status_timeline_join`.

Prediction: the compiler should expose prior, current, corrected, superseded,
rejected, and scheduled states as generic status/time/authority coordinates. QA
should answer dates before, during, and after the corrected interval without
using the rejected recommendation or the superseded interval.

Forbidden fix: no selector, helper, or mapper logic may reference this probe's
credential id, notice ids, question ids, local status words, or answer strings.
