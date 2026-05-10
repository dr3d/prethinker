# hospital_shift_exception_log Fixture Notes

## Author Delivery Note

This fixture was delivered as one markdown artifact containing all five files
with `===== FILENAME: x =====` separators:

- `source.md`
- `qa.md`
- `oracle.jsonl`
- `strategy.md`
- `anti_leakage_manifest.md`

The author noted that the full eight-fixture request was too large for one
high-quality response, so fixtures were delivered one at a time.

## Set-Level Design Notes

- Oracle answers should stay tight.
- Where an answer is unresolved, the oracle should name the pending evidence
  rather than merely saying "unknown."
- Numeric facts in `source.md` should resolve to exactly one canonical reading
  once supersession and clock-skew are accounted for.
- QA traps should probe whether a parser collapses superseded values into
  current state.

## Fixture-Specific Notes

- Fixture 1, `hospital_shift_exception_log`, was described by the author as
  complete: source around 1,950 words, 40 oracle rows, and every question
  having a single defensible answer rooted in the document.
- Q30 was changed from an original Pyxis-event count question to "how many
  badge events to Room 504" because the Pyxis count had genuine ambiguity:
  whether the 14:03:34 override-note row should count as a separate event from
  the 14:02:51 withdrawal it annotates. The badge count is intentionally
  unambiguous at 7.
- Q19's "no assigned RN" answer is intentionally a negative-existential answer.
  It should test whether Prethinker can emit the absence cleanly instead of
  hallucinating a fallback name.
- The two-timestamp test is intentional: the source mentions 14:02:21 as the
  superseded value in Addendum A and 14:02:51 as the authoritative Pyxis event
  timestamp. Badge-log corroboration at 14:02:30 is nearby but not the
  authoritative cabinet-event timestamp.
- The author offered an optional future thickening of the supersession test: add
  a third timestamp via a subsequent erratum that briefly reverts and then
  re-corrects, to test correction-chain tracking rather than last-write-wins.
