# Anti-Leakage Manifest — Industrial Sensor Clock Correction

## Per-question classification

| QID  | Class                  | Notes                                                            |
| ---- | ---------------------- | ---------------------------------------------------------------- |
| q001 | direct_lookup          | Section 1 systems table.                                         |
| q002 | identifier_exact       | Header field.                                                    |
| q003 | direct_lookup          | Header field.                                                    |
| q004 | direct_lookup          | Section 9 sensor register excerpt.                               |
| q005 | source_address         | Section 4 is the corrected-timeline section.                     |
| q006 | source_address         | Section 8.2 enumerates inferences not available.                 |
| q007 | direct_lookup          | Section 6 names R. Kim.                                          |
| q008 | direct_lookup          | Section 5.3 names QHP-04.                                        |
| q009 | source_address         | Section 9 contains certified-scope excerpts.                     |
| q010 | direct_lookup          | Section 1 systems table.                                         |
| q011 | identifier_exact       | EV-08 row in Section 3.                                          |
| q012 | identifier_exact       | Section 2 final paragraph.                                       |
| q013 | identifier_exact       | Section 7 missing-evidence paragraph.                            |
| q014 | identifier_exact       | Section 5.1.                                                     |
| q015 | identifier_exact       | EV-03 row in Section 3.                                          |
| q016 | identifier_exact       | Section 11.                                                      |
| q017 | identifier_exact       | EV-13 row in Section 3.                                          |
| q018 | direct_lookup          | Section 2 drift table.                                           |
| q019 | direct_lookup          | Section 2 header.                                                |
| q020 | derived_time           | Corrected interval; explicitly stated in Section 4 prose.        |
| q021 | derived_time           | Line-stop duration; explicitly stated in Section 5.2 prose.      |
| q022 | derived_time           | Corrected wall-clock of EV-08; given in Section 4 table.         |
| q023 | direct_lookup          | Section 9 HUM-D-04 entry.                                        |
| q024 | derived_count          | Count from Section 1 table; trivial.                             |
| q025 | derived_count          | Count from Section 3 table; trivial.                             |
| q026 | derived_count          | Per-system count of SYS-A rows in Section 3.                     |
| q027 | composition            | Per-system breakdown across all 14 events in Section 3.          |
| q028 | derived_count          | Section 7 names two missing sources together.                    |
| q029 | authority_boundary     | Section 2 interpretation rules.                                  |
| q030 | direct_lookup          | Section 7 / Section 10 confirm data lost.                        |
| q031 | authority_boundary     | Section 5.3 names QHP-04.                                        |
| q032 | direct_lookup          | Section 7 / Section 10 status of LAB-2026-0422-S3.               |
| q033 | composition            | Section 6 closing sentence on EV-08 / EV-12 origination.         |
| q034 | unresolved             | Section 7 + Section 8.2 confirm.                                 |
| q035 | negative_existential   | Section 8.2 explicit "absence is not affirmative."               |
| q036 | source_reliability     | Section 7 + Section 9 HUM-D-04 entry.                            |
| q037 | unresolved             | Section 8.2 explicit "this packet does not assign root cause."   |
| q038 | source_reliability     | Section 9 QIS-OPT-12 entry.                                      |
| q039 | source_reliability     | Section 1 + Section 6 minute-resolution constraint.              |
| q040 | direct_lookup          | Section 11 explicitly describes the relationship.                |

## Leakage disclosure

The following intentional leakage exists in the packet. It is disclosed
because the spec requires disclosure rather than concealment.

1. **Section 4 closing prose explicitly states the corrected EV-08–EV-09
   interval (2m12s) and contrasts it with the raw value (5m17s).** This
   directly answers q020 in narrative form. The leak is intentional: the
   transfer pressure is whether the helper applies the correct rule
   automatically, not whether it can be told the answer. A future variant
   should suppress this paragraph and require the helper to derive the
   interval from the table alone.

2. **Section 5.2 explicitly states the line-stop duration as
   "17 hours 45 minutes 52 seconds."** This directly answers q021 in
   narrative form. Same rationale as item 1.

3. **Section 7 names the two missing pieces of evidence in a single
   paragraph** with explicit "either (i) ... or (ii) ..." structure. This
   simplifies q028, which then becomes a count of named items rather than a
   structural inference about what counts as missing evidence.

4. **Section 8.1 reproduces the corrected EV-08–EV-09 interval and the
   line-stop duration as bullet points.** This double-leaks the same numbers
   as items 1 and 2. The bullet form is included because real engineering
   packets do summarize at the end; a stricter variant would drop Section
   8.1 entirely.

5. **Section 11 names MPP-COMP-2026-0427 explicitly as the regulatory
   report** and explicitly describes the raw-vs-corrected timestamp
   division. This makes q040 a direct lookup rather than a provenance
   inference. The leak is intentional: provenance answers in real packets
   do appear in compilation notes, and the test is whether the helper can
   recognize and use that prose.

## What is not leaked

- The per-system breakdown of EV-row counts (q027) is not stated as a
  composition list anywhere in the packet; it must be derived from the
  Section 3 table by reading each row's `System` column.
- The 72-hour active-production-time clock value is not computed in the
  packet; the packet states the rule and the pause interval but does not
  state how much active production time has accrued. (No QA question asks
  for this; if added, it would require interval arithmetic.)
- The cause of EV-03 is not stated. The packet is explicit that it is
  unresolved.
- R. Kim's actions during 14:50–15:02 are not stated; the silence is
  flagged as silence, not as evidence.
- Sub-minute reasoning over SYS-D entries is explicitly forbidden by the
  resolution constraint, but the packet does not enumerate the consequent
  questions; the helper has to recognize the constraint scope.
