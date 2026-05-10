# Anti-Leakage Manifest — School Activity Roster Reconciliation

## Per-question classification

| QID  | Class                  | Notes                                                            |
| ---- | ---------------------- | ---------------------------------------------------------------- |
| q001 | direct_lookup          | Header field.                                                    |
| q002 | source_address         | Section 1.4 contains v3.                                         |
| q003 | direct_lookup          | Section 4 cites SCO-CH-3.                                        |
| q004 | direct_lookup          | Section 9.                                                       |
| q005 | direct_lookup          | Section 2.1 names lead chaperone.                                |
| q006 | source_address         | Section 6.1.                                                     |
| q007 | direct_lookup          | Section 4 table + paragraph.                                     |
| q008 | direct_lookup          | Header field.                                                    |
| q009 | direct_lookup          | Section 3 adult lodging.                                         |
| q010 | direct_lookup          | Section 4 cites CHPS-OF-12.                                      |
| q011 | identifier_exact       | Header.                                                          |
| q012 | identifier_exact       | Section 1.4.                                                     |
| q013 | identifier_exact       | Section 5.                                                       |
| q014 | identifier_exact       | Section 7.                                                       |
| q015 | identifier_exact       | Section 2.1.                                                     |
| q016 | identifier_exact       | Section 7.                                                       |
| q017 | direct_lookup          | Section 1 version table.                                         |
| q018 | direct_lookup          | Section 1.2 errata note.                                         |
| q019 | direct_lookup          | Section 2.1 / Section 2.2.                                       |
| q020 | derived_time           | Tournament Day Schedule cross-referenced with Section 6.1.       |
| q021 | direct_lookup          | Section 4 final paragraph (range explicitly given).              |
| q022 | direct_lookup          | Section 1.2.                                                     |
| q023 | derived_count          | v3 Group A list in Section 1.4.                                  |
| q024 | derived_count          | v3 Group C list in Section 1.4.                                  |
| q025 | direct_lookup          | Section 1.4 header text states 35.                               |
| q026 | composition            | v3 Group B list in Section 1.4.                                  |
| q027 | derived_count          | Section 4 adults table; 8 rows.                                  |
| q028 | derived_count          | Section 4 adults table; count "Yes" in last column.              |
| q029 | authority_boundary     | Section 1 + Section 9.                                           |
| q030 | authority_boundary     | Section 4 SCO-CH-3 role definitions.                             |
| q031 | authority_boundary     | Section 4 driver role definition.                                |
| q032 | custody_boundary       | Section 7 final paragraph; medical events escalate to N. Park.   |
| q033 | unresolved             | Section 8 explicitly pending.                                    |
| q034 | negative_existential   | Section 8 explicitly excluded from packet.                       |
| q035 | negative_existential   | Section 1.3 explicitly states v2.1 not issued.                   |
| q036 | composition            | Section 1.4 corrects the duplicate listing.                      |
| q037 | negative_existential   | Section 1.2 + Section 9 explicit reference, not reproduced.      |
| q038 | source_reliability     | Section 5 explicit "not been audited."                           |
| q039 | supersession           | Section 9 explicit supersession rule.                            |
| q040 | direct_lookup          | Section 9.                                                       |

## Leakage disclosure

The following intentional leakage exists in the packet. It is disclosed
because the spec requires disclosure rather than concealment.

1. **Section 1.4 explicitly states "Total students: 35"** in the v3
   header. This directly answers q025 in narrative form. The leak is
   intentional: real correction notices state the corrected total.
   A stricter variant could remove the header total and require the
   helper to count the v3 group lists.

2. **Section 1.2 errata note explicitly says "S-022 appears in both
   Group B and Group C"** and explicitly says v2 sums to 36 not 35.
   This pre-resolves the "v2 inconsistency" recognition that a stricter
   variant would force the helper to derive. The leak is intentional:
   real packets disclose errata. A stricter variant would have the
   inconsistency only in the data, not in the prose.

3. **Section 4 adults table includes a "Counts toward ratio?" column**
   with explicit Yes/No values. This makes q028 a count of Yes-rows
   rather than an inference from role definitions. The leak is
   intentional and matches how policy compliance tables are produced
   in real activity packets.

4. **Section 1.4 explicitly enumerates the v3 changes from v2** as a
   bullet list ("S-022 corrected to Group B only; S-019 reassigned
   from Group B to Group C"). This pre-resolves q036 without requiring
   a delta computation between the v2 and v3 lists.

5. **Section 9 explicit supersession statement** ("where v1 or v2 lists
   a student in a group that v3 has changed, v3 is operational"). This
   makes q039 a direct lookup rather than a supersession-doctrine
   inference. The leak is intentional: real activity packets do
   include this statement, and the test is whether the helper uses it.

## What is not leaked

- The v3 group list sizes (12, 10, 13) are not stated as a composition
  triple anywhere; they must be derived from the bullet lists.
- The number of chaperones counting toward ratio (4) is not stated
  numerically anywhere — it must be derived from the table by counting
  "Yes" rows.
- The fact that S-024 rides Bus 2 outbound and Bus 1 return-only is
  given in two separate places (Section 2.2 seat row table for
  outbound; Section 2.3 reassignment paragraph). The temporal scope
  must be respected; "S-024 is on Bus 1" without scope is incorrect.
- The fact that S-007's Group C presenter-aide assignment applies only
  during 11:00–12:30 is given in Section 6.1; "S-007 is in Group C"
  without temporal scope is incorrect.
- The medical withdrawal of S-018 is referenced; the underlying medical
  reason is not reproduced and should not be inferred.
- The v2 inconsistency is described as an errata; the correct count for
  v2 (had S-022 been listed once) is not stated. The packet does not
  retrospectively fix v2; it issues v3 instead.
