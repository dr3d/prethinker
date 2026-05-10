# municipal_tree_permit_amendment Fixture Notes

## Author Delivery Note

Fixture 6, `municipal_tree_permit_amendment`, was described by the author as
complete: source around 2,000 words, 40 oracle rows, and the full five-file set
delivered.

## Fixture-Specific Notes

- Q20 and Q24 are the filed-versus-issued linchpin pair. The amendment was
  filed April 18, the felling happened April 21, and the amendment was issued
  April 25. The common LLM error is collapsing "filed" into "in force." If both
  rows fail together, that is likely the cause. If Q20 succeeds but Q24 fails,
  that suggests asymmetric handling of the same boundary.
- Q29 is the double-qualification trap. Tree #19 qualifies as protected under
  two independent clauses:
  - section 18-12(b)(ii): Sugar Maple at least 18 inches;
  - section 18-12(b)(i): any native species at least 24 inches.
  Naive parsers may grab the first matching clause and stop. The correct answer
  enumerates both.
- Q39 is the "preserve the unresolved factual question" test. The City
  Solicitor's memo identifies the factual question the determination turns on:
  actual knowledge. It explicitly does not resolve that question. The desired
  behavior is to surface the open factual question and stop, not decide whether
  the violation occurred.
- Q10 tests cross-exhibit corroboration. The April 21 felling has three
  corroborating sources: Kowalski email, Inspector Ruiz photos, and Tahir's
  stump exam. The oracle answer names all three. Getting one is partial; full
  credit requires composing across exhibits.

## Self-Flagged Leakage / Hardness Decision

The counts of 7 protected, 16 removable, and 23 subject-to-ordinance are stated
explicitly in source. Q15, Q31, and Q30 are therefore direct lookups rather than
derivations from the tree lists.

Possible future choice: strip the explicit counts to force derivation from the
lists. This is the same design fork as the arts grant worked-average issue:
test extraction of stated counts, or test composition/counting from records.

No source edit has been made yet.
