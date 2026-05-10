# Anti-Leakage Manifest — Grant Exception Cap Matrix

## Per-question classification

| QID  | Class                  | Notes                                                            |
| ---- | ---------------------- | ---------------------------------------------------------------- |
| q001 | direct_lookup          | Header field.                                                    |
| q002 | direct_lookup          | Header field.                                                    |
| q003 | source_address         | Section 10.                                                      |
| q004 | source_address         | Section 5.1.                                                     |
| q005 | direct_lookup          | Section 1 cycle parameters.                                      |
| q006 | direct_lookup          | Section 1 cycle parameters.                                      |
| q007 | source_address         | Section 9.                                                       |
| q008 | direct_lookup          | Section 1 / Section 5.                                           |
| q009 | direct_lookup          | Section 11 references BWCF-CP-2025.                              |
| q010 | source_address         | Section 7.                                                       |
| q011 | identifier_exact       | Header.                                                          |
| q012 | identifier_exact       | Section 5.1.                                                     |
| q013 | identifier_exact       | Section 6.                                                       |
| q014 | identifier_exact       | Section 6.                                                       |
| q015 | identifier_exact       | Section 9.1.                                                     |
| q016 | identifier_exact       | Section 11 references BWCF-CP-2025.                              |
| q017 | direct_lookup          | Section 1 cycle window.                                          |
| q018 | direct_lookup          | Section 1 cycle window.                                          |
| q019 | direct_lookup          | Section 5.1.                                                     |
| q020 | direct_lookup          | Section 9.1 ("14-day appeal window").                            |
| q021 | direct_lookup          | Section 9.1.                                                     |
| q022 | direct_lookup          | Section 9.1.                                                     |
| q023 | direct_lookup          | Section 1 + Section 4 (7 applications).                          |
| q024 | derived_count          | Count of "Yes" rows in Section 4 Eligible column (6).            |
| q025 | derived_count          | Count of "Awarded" rows in Section 10 (5).                       |
| q026 | composition            | Section 7 + Section 4 rural %; A-02 and A-06 qualify.            |
| q027 | derived_count          | Section 7 final column ("Capped?" Yes count = 2).                |
| q028 | derived_count          | Section 9.2 explicitly states $107,000 and shows the sum.        |
| q029 | authority_boundary     | Section 6 explicit statement.                                    |
| q030 | status                 | Section 4 + Section 10 + Section 5 (not scored).                 |
| q031 | unresolved             | Section 9.1 + Section 10.                                        |
| q032 | authority_boundary     | Section 6 recusal table.                                         |
| q033 | composition            | Section 6 explicit statement (7-1=6).                            |
| q034 | unresolved             | Section 9.1 explicit "neither awarded nor finally declined."     |
| q035 | negative_existential   | Section 9.2 explicit "drawn against Fall 2026 carryover."        |
| q036 | authority_boundary     | Section 8 explicit statement.                                    |
| q037 | negative_existential   | Section 11 references but does not reproduce.                    |
| q038 | supersession           | Section 5.1 explicit "operational as of 2026-04-22."             |
| q039 | direct_lookup          | Section 11.                                                      |
| q040 | direct_lookup          | Section 11.                                                      |

## Leakage disclosure

The following intentional leakage exists in the packet. It is disclosed
because the spec requires disclosure rather than concealment.

1. **Section 4 includes an "Eligible?" column with explicit Yes/No
   values.** This makes q024 a count of Yes-rows rather than an
   inference from rule application. The leak is intentional: real
   eligibility tables produce explicit findings. A stricter variant
   would force the helper to apply ER-1, ER-2, ER-3, EX-A from the
   per-application data alone.

2. **Section 7 includes a "Final award" column with explicit dollar
   values for awarded applications.** This pre-resolves the
   bonus-then-cap arithmetic for q027 and q028. The leak is
   intentional and matches real grant computation tables. A stricter
   variant would provide only the requested amount, the rural %, and
   the cap parameters and require the helper to compute each row.

3. **Section 9.2 explicitly states the total awarded amount as
   $107,000** and shows the sum in arithmetic form. This makes q028 a
   direct lookup. A stricter variant would force the helper to
   sum the Section 10 award column.

4. **Section 5.1 explicitly states the corrected composite for A-02
   is 8.4 and is operational.** This pre-resolves q038 without
   requiring a supersession derivation.

5. **Section 8 explicitly states the recusal of J. Vasquez did not
   determine the outcome.** This pre-resolves q036 without requiring
   a derivation about what "recusal" entails. The leak is intentional
   because the test is whether the helper uses such a statement when
   present, not whether it can produce one in its absence.

6. **Section 6 explicitly states "a recusal does not automatically
   decide the named item in any direction."** This pre-resolves q029
   (which is a paraphrase of the same sentence). Again, intentional:
   real procedure documents say this.

## What is not leaked

- The ordering of bonus and cap is not stated in a single sentence;
  the helper must read Section 7's computation as
  "requested × 1.10, then capped" rather than
  "requested capped, then × 1.10."
- The composition of EX-B recipients (A-02, A-06) is not given as a
  list anywhere; it must be derived from the Rural % column and the
  EX-B rule.
- The status of A-07 as "neither awarded nor finally declined" is
  stated but the implication for downstream operations (A-07 is
  excluded from awarded counts but not from the application count) is
  not enumerated.
- The committee size of 7 is stated; the resulting voting body for
  a multi-recusal item is the helper's job to derive ("7 minus
  recusals filed for this specific item").
- A-04's borderline-vote requirement is stated only once, as the
  trigger for the Section 8 vote. The helper has to recognize that
  exactly-at-threshold composites trigger this rule from a single
  inline statement.
