# Anti-Leakage Manifest — probate_storage_access_register

## Per-question manifest classification

| QID  | Manifest class       | Notes                                                                  |
| ---- | -------------------- | ---------------------------------------------------------------------- |
| q001 | direct_lookup        | Header.                                                                |
| q002 | identifier_exact     | Header.                                                                |
| q003 | direct_lookup        | Section A and header.                                                  |
| q004 | direct_lookup        | Section A.                                                             |
| q005 | direct_lookup        | Section H.3 signature.                                                 |
| q006 | source_address       | Section heading.                                                       |
| q007 | source_address       | Section D.3 explicitly named.                                          |
| q008 | direct_lookup        | Section B row.                                                         |
| q009 | direct_lookup        | Section H.3 explicit.                                                  |
| q010 | source_address       | Section E.                                                             |
| q011 | identifier_exact     | Section B.                                                             |
| q012 | identifier_exact     | Section B and external-ID convention note.                             |
| q013 | identifier_exact     | Section E.                                                             |
| q014 | identifier_exact     | Section B reverse lookup.                                              |
| q015 | identifier_exact     | Section D.3.                                                           |
| q016 | identifier_exact     | Section B.                                                             |
| q017 | identifier_exact     | Section E.                                                             |
| q018 | derived_time         | Header / Section I.                                                    |
| q019 | derived_time         | Section E (P-26-347-A) / Section I.                                    |
| q020 | derived_time         | Section E (P-26-347-E) / Section I.                                    |
| q021 | derived_time         | Section E (P-26-347-C) / Section I.                                    |
| q022 | derived_time         | Section I footnote.                                                    |
| q023 | derived_time         | Subtraction over Section I dates.                                      |
| q024 | derived_count        | Count of Section B rows.                                               |
| q025 | derived_count        | Filter on custodian.                                                   |
| q026 | derived_count        | Filter on title status text.                                           |
| q027 | composition          | Filter and list.                                                       |
| q028 | derived_count        | Filter on custodian.                                                   |
| q029 | custody_boundary     | Section B.                                                             |
| q030 | authority_boundary   | Section D.2 + Section I.                                               |
| q031 | authority_boundary   | Section E + Section C.                                                 |
| q032 | authority_boundary   | Section C explicit limitation paragraph.                               |
| q033 | custody_boundary     | Section D.3 explicit.                                                  |
| q034 | unresolved           | Section D.1 + E (deferment).                                           |
| q035 | unresolved           | Section D.2 explicit.                                                  |
| q036 | negative_existential | Section G enumeration of not-reproduced sources.                       |
| q037 | negative_existential | Section D.3 explicit.                                                  |
| q038 | source_reliability   | Section F.                                                             |
| q039 | source_reliability   | Section H.3 attribution.                                               |
| q040 | source_reliability   | Section F.                                                             |

## Disclosed leakage (self-flagged)

1. **Section F is an explicit "what is recorded vs what is found"
   paragraph.** This makes q038 and q040 close to direct-lookup. This
   is intentional. The instrument is whether Prethinker uses the
   distinction Section F makes; the questions are calibration.
2. **Section G enumerates referenced-but-not-reproduced sources.** This
   makes q036 close to direct-lookup, but the answer is not a single
   token; it requires picking one item out of the listed five.
3. **Section D.3 explicitly states the executor has not directed
   delivery and that no party other than Reeder has access to EX-006,
   EX-007, EX-008.** This is the kind of explicit-negative line the
   spec warns about. q033, q037 are easier than they would be if a
   reader had to derive them from absence.
4. **Section I (chronology) duplicates dates and events that appear
   inline elsewhere.** This means temporal questions (q018-q022) can
   be answered from chronology alone, but it also means the chronology
   does not introduce dates the rest of the document doesn't have. The
   chronology is the convenient single-source for temporal questions.
5. **Section C's narrative paragraph explicitly states the executor has
   no authority over reading-room patron access at EX-009.** q032 is
   essentially a paraphrase of that paragraph.
6. **Section E narrative explicitly says P-26-347-E is a deferment, not
   a decision.** q034 is partially leaked by the explicit statement
   "The scheduling order (P-26-347-E) defers the codicil determination;
   it does not decide the codicil's validity."

## Not present (deliberate)

- No paragraph stating "items in V. Reeder's custody are EX-006,
  EX-007, EX-008" in summary form; this composition must be derived
  from Section B (q027).
- No paragraph stating "X items are at Northpoint Regional Museum"
  or "Y items at SafeStore Vault"; these are derived (q025, q028).
- No paragraph stating "the codicil is invalid" or "the gift claim is
  valid"; both are explicitly held in the recorded-but-not-found
  bucket.
- No "therefore..." paragraph linking custody to ownership.
- No worked count of contested items in summary form (q026 derives
  from Section B's title-status column).
- No worked interval between forensic report and rescheduled hearing
  (q023 derives from chronology).

## Leakage risk-level summary

- **Low risk** of bypass: q001-q005, q008, q011-q017.
- **Moderate risk** of bypass via explicit prose: q032 (paragraph in
  Section C), q034 (paragraph in Section E narrative), q037 (Section
  D.3 explicit), q038 (Section F explicit).
- **Useful if missed**: q026 (requires reading title-status field),
  q027 (composition), q029 vs q030 (custody vs ownership separation —
  the central instrument), q031 vs q032 (authority scope), q040
  (recognizes Section F's hierarchy of authoritative sources).

End of manifest.
